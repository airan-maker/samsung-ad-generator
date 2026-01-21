"""
Video Generation Pipeline Orchestrator

Coordinates all agents to produce a complete video advertisement.
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import uuid

from app.agents.script_agent import ScriptAgent
from app.agents.video_agent import RunwayVideoAgent, VideoStatus, get_video_agent
from app.agents.audio_agent import ElevenLabsAudioAgent, get_audio_agent
from app.agents.music_agent import SunoMusicAgent, MusicStatus, get_music_agent
from app.core.config import settings

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    INITIALIZED = "initialized"
    SCRIPT_GENERATION = "script_generation"
    AUDIO_GENERATION = "audio_generation"
    MUSIC_GENERATION = "music_generation"
    VIDEO_GENERATION = "video_generation"
    VIDEO_COMPOSITING = "video_compositing"
    FINAL_EXPORT = "final_export"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineProgress:
    stage: PipelineStage
    progress: int = 0  # 0-100
    message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class PipelineResult:
    success: bool
    pipeline_id: str
    project_id: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    stages: List[PipelineProgress] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoSegment:
    """Represents a segment of the final video."""
    index: int
    start_time: float
    end_time: float
    prompt: str
    narration: Optional[str] = None
    video_url: Optional[str] = None
    audio_data: Optional[bytes] = None


class VideoPipeline:
    """
    Orchestrates the complete video generation process.

    Pipeline stages:
    1. Script Generation - Generate/refine the ad script
    2. Audio Generation - Generate voiceover narration
    3. Music Generation - Generate background music
    4. Video Generation - Generate video segments
    5. Video Compositing - Combine video, audio, music
    6. Final Export - Encode and export final video
    """

    def __init__(
        self,
        project_id: str,
        on_progress: Optional[Callable[[PipelineProgress], None]] = None,
    ):
        self.pipeline_id = str(uuid.uuid4())
        self.project_id = project_id
        self.on_progress = on_progress

        # Initialize agents
        self.script_agent = ScriptAgent()
        self.video_agent = get_video_agent("runway")
        self.audio_agent = get_audio_agent("elevenlabs")
        self.music_agent = get_music_agent("stock")  # Start with stock music

        # Pipeline state
        self.current_stage = PipelineStage.INITIALIZED
        self.stages: List[PipelineProgress] = []
        self.segments: List[VideoSegment] = []

    def _update_progress(
        self,
        stage: PipelineStage,
        progress: int,
        message: str,
    ):
        """Update and broadcast progress."""
        stage_progress = PipelineProgress(
            stage=stage,
            progress=progress,
            message=message,
            started_at=datetime.utcnow() if progress == 0 else None,
            completed_at=datetime.utcnow() if progress == 100 else None,
        )

        # Update or add stage
        existing = next((s for s in self.stages if s.stage == stage), None)
        if existing:
            existing.progress = progress
            existing.message = message
            if progress == 100:
                existing.completed_at = datetime.utcnow()
        else:
            stage_progress.started_at = datetime.utcnow()
            self.stages.append(stage_progress)

        self.current_stage = stage

        if self.on_progress:
            self.on_progress(stage_progress)

        logger.info(f"Pipeline {self.pipeline_id}: {stage.value} - {progress}% - {message}")

    async def run(
        self,
        product: Dict[str, Any],
        template: Dict[str, Any],
        config: Dict[str, Any],
        existing_script: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        """
        Run the complete video generation pipeline.

        Args:
            product: Product information
            template: Template configuration
            config: Generation configuration (tone, duration, etc.)
            existing_script: Pre-generated script (optional)

        Returns:
            PipelineResult with video URL and metadata
        """
        try:
            # Stage 1: Script Generation
            script = await self._generate_script(
                product, template, config, existing_script
            )
            if not script:
                return self._create_error_result("Script generation failed")

            # Parse script into segments
            self._parse_script_segments(script, config)

            # Stage 2 & 3: Audio and Music Generation (parallel)
            audio_task = asyncio.create_task(
                self._generate_audio(self.segments, config)
            )
            music_task = asyncio.create_task(
                self._generate_music(product, config)
            )

            audio_results, music_result = await asyncio.gather(
                audio_task, music_task
            )

            # Stage 4: Video Generation
            video_results = await self._generate_videos(self.segments, config)

            # Stage 5: Video Compositing
            composite_url = await self._composite_video(
                video_results, audio_results, music_result, config
            )

            # Stage 6: Final Export
            final_result = await self._export_video(composite_url, config)

            self._update_progress(
                PipelineStage.COMPLETED, 100, "Video generation complete"
            )

            return PipelineResult(
                success=True,
                pipeline_id=self.pipeline_id,
                project_id=self.project_id,
                video_url=final_result.get("video_url"),
                thumbnail_url=final_result.get("thumbnail_url"),
                duration=final_result.get("duration"),
                stages=self.stages,
                metadata={
                    "script": script,
                    "segments": len(self.segments),
                    "format": config.get("format", "16:9"),
                },
            )

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            self._update_progress(
                PipelineStage.FAILED, 0, f"Pipeline failed: {str(e)}"
            )
            return self._create_error_result(str(e))

        finally:
            await self._cleanup()

    async def _generate_script(
        self,
        product: Dict[str, Any],
        template: Dict[str, Any],
        config: Dict[str, Any],
        existing_script: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generate or use existing script."""
        self._update_progress(
            PipelineStage.SCRIPT_GENERATION, 0, "Starting script generation"
        )

        if existing_script:
            self._update_progress(
                PipelineStage.SCRIPT_GENERATION, 100, "Using provided script"
            )
            return existing_script

        try:
            script = await self.script_agent.generate_script(
                product_info=product,
                template_type=template.get("style", "unboxing"),
                duration=config.get("duration", 30),
                tone=config.get("tone", "professional"),
                target_audience=config.get("target_audience"),
            )

            self._update_progress(
                PipelineStage.SCRIPT_GENERATION, 100, "Script generated"
            )

            return script

        except Exception as e:
            logger.error(f"Script generation error: {str(e)}")
            self._update_progress(
                PipelineStage.SCRIPT_GENERATION, 0, f"Failed: {str(e)}"
            )
            return None

    def _parse_script_segments(
        self,
        script: Dict[str, Any],
        config: Dict[str, Any],
    ):
        """Parse script into video segments."""
        scenes = script.get("scenes", [])
        total_duration = config.get("duration", 30)

        # Calculate segment durations
        num_scenes = len(scenes)
        base_duration = total_duration / max(num_scenes, 1)

        current_time = 0.0
        for i, scene in enumerate(scenes):
            duration = scene.get("duration", base_duration)
            self.segments.append(
                VideoSegment(
                    index=i,
                    start_time=current_time,
                    end_time=current_time + duration,
                    prompt=scene.get("visual_description", ""),
                    narration=scene.get("narration", ""),
                )
            )
            current_time += duration

    async def _generate_audio(
        self,
        segments: List[VideoSegment],
        config: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate voiceover for all segments."""
        self._update_progress(
            PipelineStage.AUDIO_GENERATION, 0, "Generating voiceover"
        )

        results = []
        voice_preset = config.get("voice_preset", "ko_professional_female")

        for i, segment in enumerate(segments):
            if not segment.narration:
                results.append({"success": True, "audio_data": None})
                continue

            progress = int((i / len(segments)) * 90)
            self._update_progress(
                PipelineStage.AUDIO_GENERATION,
                progress,
                f"Generating audio {i + 1}/{len(segments)}",
            )

            try:
                result = await self.audio_agent.generate_speech(
                    text=segment.narration,
                    voice_id=self.audio_agent.get_preset_voice(voice_preset).voice_id,
                )
                segment.audio_data = result.audio_data
                results.append({
                    "success": result.success,
                    "audio_data": result.audio_data,
                })
            except Exception as e:
                logger.error(f"Audio generation error for segment {i}: {str(e)}")
                results.append({"success": False, "error": str(e)})

            # Rate limiting
            await asyncio.sleep(0.5)

        self._update_progress(
            PipelineStage.AUDIO_GENERATION, 100, "Voiceover complete"
        )

        return results

    async def _generate_music(
        self,
        product: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate or select background music."""
        self._update_progress(
            PipelineStage.MUSIC_GENERATION, 0, "Selecting music"
        )

        category = product.get("category", "smartphone")

        # Use stock music for MVP (faster and more reliable)
        if isinstance(self.music_agent, type(get_music_agent("stock"))):
            track = self.music_agent.get_track_for_category(category)
            self._update_progress(
                PipelineStage.MUSIC_GENERATION, 100, f"Selected: {track['id']}"
            )
            return track

        # AI music generation
        try:
            result = await self.music_agent.generate_for_category(
                category=category,
                duration=config.get("duration", 30),
            )

            if result.status == MusicStatus.COMPLETED:
                self._update_progress(
                    PipelineStage.MUSIC_GENERATION, 100, "Music generated"
                )
                return {
                    "url": result.audio_url,
                    "duration": result.duration,
                }

            # Fallback to stock
            stock_agent = get_music_agent("stock")
            track = stock_agent.get_track_for_category(category)
            self._update_progress(
                PipelineStage.MUSIC_GENERATION, 100, f"Fallback to stock: {track['id']}"
            )
            return track

        except Exception as e:
            logger.error(f"Music generation error: {str(e)}")
            # Fallback to stock
            stock_agent = get_music_agent("stock")
            return stock_agent.get_track_for_category(category)

    async def _generate_videos(
        self,
        segments: List[VideoSegment],
        config: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate video for each segment."""
        self._update_progress(
            PipelineStage.VIDEO_GENERATION, 0, "Starting video generation"
        )

        results = []
        aspect_ratio = config.get("aspect_ratio", "16:9")

        # Generate videos (potentially in parallel with rate limiting)
        for i, segment in enumerate(segments):
            progress = int((i / len(segments)) * 90)
            self._update_progress(
                PipelineStage.VIDEO_GENERATION,
                progress,
                f"Generating video {i + 1}/{len(segments)}",
            )

            try:
                # Generate video for this segment
                result = await self.video_agent.generate_video(
                    prompt=segment.prompt,
                    duration=int(segment.end_time - segment.start_time),
                    ratio=aspect_ratio,
                )

                # Wait for completion
                if result.status != VideoStatus.FAILED:
                    result = await self.video_agent.wait_for_completion(
                        result.task_id,
                        poll_interval=5,
                        max_wait=300,
                    )

                segment.video_url = result.video_url
                results.append({
                    "success": result.status == VideoStatus.COMPLETED,
                    "video_url": result.video_url,
                    "error": result.error,
                })

            except Exception as e:
                logger.error(f"Video generation error for segment {i}: {str(e)}")
                results.append({"success": False, "error": str(e)})

        self._update_progress(
            PipelineStage.VIDEO_GENERATION, 100, "Videos generated"
        )

        return results

    async def _composite_video(
        self,
        video_results: List[Dict[str, Any]],
        audio_results: List[Dict[str, Any]],
        music_result: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Optional[str]:
        """
        Composite all video segments with audio and music.

        In production, this would use FFmpeg or a cloud video processing service.
        """
        self._update_progress(
            PipelineStage.VIDEO_COMPOSITING, 0, "Compositing video"
        )

        # Collect successful video URLs
        video_urls = [
            r["video_url"] for r in video_results
            if r.get("success") and r.get("video_url")
        ]

        if not video_urls:
            logger.error("No videos to composite")
            return None

        # In production, call video compositing service
        # For now, simulate the process
        self._update_progress(
            PipelineStage.VIDEO_COMPOSITING, 50, "Merging segments"
        )

        await asyncio.sleep(1)  # Simulate processing

        self._update_progress(
            PipelineStage.VIDEO_COMPOSITING, 80, "Adding audio tracks"
        )

        await asyncio.sleep(1)

        self._update_progress(
            PipelineStage.VIDEO_COMPOSITING, 100, "Composite complete"
        )

        # Return placeholder URL (would be actual URL in production)
        return f"https://cdn.saiad.io/videos/{self.pipeline_id}/composite.mp4"

    async def _export_video(
        self,
        composite_url: Optional[str],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Export final video in requested format."""
        self._update_progress(
            PipelineStage.FINAL_EXPORT, 0, "Exporting video"
        )

        if not composite_url:
            return {"video_url": None, "thumbnail_url": None, "duration": 0}

        # Export format settings
        export_format = config.get("export_format", "youtube")
        format_specs = {
            "youtube": {"resolution": "1080p", "codec": "h264", "bitrate": "8M"},
            "instagram": {"resolution": "1080p", "codec": "h264", "bitrate": "6M"},
            "tiktok": {"resolution": "1080p", "codec": "h264", "bitrate": "6M"},
        }

        spec = format_specs.get(export_format, format_specs["youtube"])

        self._update_progress(
            PipelineStage.FINAL_EXPORT, 50, f"Encoding {spec['resolution']}"
        )

        await asyncio.sleep(1)  # Simulate encoding

        self._update_progress(
            PipelineStage.FINAL_EXPORT, 90, "Generating thumbnail"
        )

        await asyncio.sleep(0.5)

        self._update_progress(
            PipelineStage.FINAL_EXPORT, 100, "Export complete"
        )

        return {
            "video_url": f"https://cdn.saiad.io/videos/{self.pipeline_id}/final_{export_format}.mp4",
            "thumbnail_url": f"https://cdn.saiad.io/videos/{self.pipeline_id}/thumbnail.jpg",
            "duration": config.get("duration", 30),
        }

    def _create_error_result(self, error: str) -> PipelineResult:
        """Create an error result."""
        return PipelineResult(
            success=False,
            pipeline_id=self.pipeline_id,
            project_id=self.project_id,
            stages=self.stages,
            error=error,
        )

    async def _cleanup(self):
        """Cleanup resources."""
        try:
            await self.video_agent.close()
            await self.audio_agent.close()
            if hasattr(self.music_agent, 'close'):
                await self.music_agent.close()
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")


# Convenience function for running pipeline
async def run_video_pipeline(
    project_id: str,
    product: Dict[str, Any],
    template: Dict[str, Any],
    config: Dict[str, Any],
    existing_script: Optional[Dict[str, Any]] = None,
    on_progress: Optional[Callable[[PipelineProgress], None]] = None,
) -> PipelineResult:
    """
    Run the video generation pipeline.

    This is the main entry point for video generation.
    """
    pipeline = VideoPipeline(project_id, on_progress)
    return await pipeline.run(product, template, config, existing_script)
