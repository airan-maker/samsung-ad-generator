"""
Video Generation Agent - Runway API Integration

Supports Runway Gen-4 for high-quality video generation from text prompts.
"""

import httpx
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoModel(Enum):
    GEN4 = "gen4"
    GEN4_TURBO = "gen4_turbo"


class VideoStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VideoGenerationResult:
    task_id: str
    status: VideoStatus
    video_url: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    progress: int = 0


class RunwayVideoAgent:
    """Agent for generating videos using Runway API."""

    BASE_URL = "https://api.runwayml.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.RUNWAY_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Runway-Version": "2024-11-06",
            },
            timeout=60.0,
        )

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        model: VideoModel = VideoModel.GEN4,
        ratio: str = "16:9",
        seed: Optional[int] = None,
        image_url: Optional[str] = None,
    ) -> VideoGenerationResult:
        """
        Generate a video from a text prompt.

        Args:
            prompt: Text description of the video to generate
            duration: Video duration in seconds (5 or 10)
            model: Runway model to use
            ratio: Aspect ratio (16:9, 9:16, 1:1)
            seed: Random seed for reproducibility
            image_url: Optional reference image URL

        Returns:
            VideoGenerationResult with task_id for polling
        """
        try:
            payload = {
                "promptText": prompt,
                "model": model.value,
                "duration": duration,
                "ratio": ratio,
            }

            if seed:
                payload["seed"] = seed

            if image_url:
                payload["promptImage"] = image_url

            response = await self.client.post(
                "/image_to_video",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()

            return VideoGenerationResult(
                task_id=data.get("id"),
                status=VideoStatus.PENDING,
                progress=0,
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Runway API error: {e.response.text}")
            return VideoGenerationResult(
                task_id="",
                status=VideoStatus.FAILED,
                error=f"API error: {e.response.status_code}",
            )
        except Exception as e:
            logger.error(f"Video generation error: {str(e)}")
            return VideoGenerationResult(
                task_id="",
                status=VideoStatus.FAILED,
                error=str(e),
            )

    async def get_task_status(self, task_id: str) -> VideoGenerationResult:
        """
        Check the status of a video generation task.

        Args:
            task_id: The task ID from generate_video

        Returns:
            VideoGenerationResult with current status
        """
        try:
            response = await self.client.get(f"/tasks/{task_id}")
            response.raise_for_status()

            data = response.json()
            status_str = data.get("status", "PENDING")

            status_map = {
                "PENDING": VideoStatus.PENDING,
                "RUNNING": VideoStatus.PROCESSING,
                "SUCCEEDED": VideoStatus.COMPLETED,
                "FAILED": VideoStatus.FAILED,
            }

            result = VideoGenerationResult(
                task_id=task_id,
                status=status_map.get(status_str, VideoStatus.PENDING),
                progress=data.get("progress", 0),
            )

            if result.status == VideoStatus.COMPLETED:
                result.video_url = data.get("output", [None])[0]
                result.duration = data.get("duration")
            elif result.status == VideoStatus.FAILED:
                result.error = data.get("failure", "Unknown error")

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Runway status check error: {e.response.text}")
            return VideoGenerationResult(
                task_id=task_id,
                status=VideoStatus.FAILED,
                error=f"Status check failed: {e.response.status_code}",
            )
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return VideoGenerationResult(
                task_id=task_id,
                status=VideoStatus.FAILED,
                error=str(e),
            )

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 5,
        max_wait: int = 300,
    ) -> VideoGenerationResult:
        """
        Wait for a video generation task to complete.

        Args:
            task_id: The task ID to wait for
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait

        Returns:
            Final VideoGenerationResult
        """
        elapsed = 0
        while elapsed < max_wait:
            result = await self.get_task_status(task_id)

            if result.status in [VideoStatus.COMPLETED, VideoStatus.FAILED]:
                return result

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        return VideoGenerationResult(
            task_id=task_id,
            status=VideoStatus.FAILED,
            error="Timeout waiting for video generation",
        )

    async def generate_and_wait(
        self,
        prompt: str,
        duration: int = 5,
        model: VideoModel = VideoModel.GEN4,
        **kwargs,
    ) -> VideoGenerationResult:
        """
        Generate a video and wait for completion.

        Convenience method that combines generate_video and wait_for_completion.
        """
        result = await self.generate_video(prompt, duration, model, **kwargs)

        if result.status == VideoStatus.FAILED:
            return result

        return await self.wait_for_completion(result.task_id)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class ReplicateVideoAgent:
    """
    Fallback agent using Replicate API for Stable Video Diffusion.
    More cost-effective for high volume.
    """

    BASE_URL = "https://api.replicate.com/v1"
    SVD_MODEL = "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.REPLICATE_API_KEY if hasattr(settings, 'REPLICATE_API_KEY') else ""
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def generate_video(
        self,
        image_url: str,
        motion_bucket_id: int = 127,
        fps: int = 24,
        cond_aug: float = 0.02,
    ) -> VideoGenerationResult:
        """
        Generate video from an image using Stable Video Diffusion.

        Args:
            image_url: URL of the source image
            motion_bucket_id: Amount of motion (0-255)
            fps: Frames per second
            cond_aug: Conditioning augmentation

        Returns:
            VideoGenerationResult
        """
        try:
            response = await self.client.post(
                "/predictions",
                json={
                    "version": self.SVD_MODEL.split(":")[-1],
                    "input": {
                        "input_image": image_url,
                        "motion_bucket_id": motion_bucket_id,
                        "fps": fps,
                        "cond_aug": cond_aug,
                    },
                },
            )
            response.raise_for_status()

            data = response.json()

            return VideoGenerationResult(
                task_id=data.get("id"),
                status=VideoStatus.PENDING,
            )

        except Exception as e:
            logger.error(f"Replicate error: {str(e)}")
            return VideoGenerationResult(
                task_id="",
                status=VideoStatus.FAILED,
                error=str(e),
            )

    async def get_task_status(self, task_id: str) -> VideoGenerationResult:
        """Check prediction status."""
        try:
            response = await self.client.get(f"/predictions/{task_id}")
            response.raise_for_status()

            data = response.json()
            status_str = data.get("status", "starting")

            status_map = {
                "starting": VideoStatus.PENDING,
                "processing": VideoStatus.PROCESSING,
                "succeeded": VideoStatus.COMPLETED,
                "failed": VideoStatus.FAILED,
                "canceled": VideoStatus.FAILED,
            }

            result = VideoGenerationResult(
                task_id=task_id,
                status=status_map.get(status_str, VideoStatus.PENDING),
            )

            if result.status == VideoStatus.COMPLETED:
                output = data.get("output")
                if isinstance(output, list) and output:
                    result.video_url = output[0]
                elif isinstance(output, str):
                    result.video_url = output
            elif result.status == VideoStatus.FAILED:
                result.error = data.get("error", "Unknown error")

            return result

        except Exception as e:
            logger.error(f"Replicate status error: {str(e)}")
            return VideoGenerationResult(
                task_id=task_id,
                status=VideoStatus.FAILED,
                error=str(e),
            )

    async def close(self):
        await self.client.aclose()


# Factory function to get the appropriate video agent
def get_video_agent(provider: str = "runway") -> RunwayVideoAgent | ReplicateVideoAgent:
    """Get the video generation agent for the specified provider."""
    if provider == "replicate":
        return ReplicateVideoAgent()
    return RunwayVideoAgent()
