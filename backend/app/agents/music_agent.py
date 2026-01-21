"""
Music Generation Agent - Suno AI Integration

Generates background music for videos using AI.
"""

import httpx
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class MusicMood(Enum):
    UPBEAT = "upbeat"
    CALM = "calm"
    DRAMATIC = "dramatic"
    INSPIRING = "inspiring"
    TECH = "tech"
    LUXURY = "luxury"
    ENERGETIC = "energetic"
    MINIMALIST = "minimalist"
    CINEMATIC = "cinematic"


class MusicGenre(Enum):
    ELECTRONIC = "electronic"
    ORCHESTRAL = "orchestral"
    AMBIENT = "ambient"
    POP = "pop"
    CINEMATIC = "cinematic"
    CORPORATE = "corporate"


class MusicStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MusicGenerationResult:
    task_id: str
    status: MusicStatus
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    title: Optional[str] = None
    error: Optional[str] = None


# Preset prompts for Samsung product categories
SAMSUNG_MUSIC_PRESETS = {
    "smartphone": {
        "mood": MusicMood.TECH,
        "genre": MusicGenre.ELECTRONIC,
        "prompt": "Modern, sleek electronic music with subtle beats, perfect for tech product showcase, clean and premium feel",
    },
    "tv": {
        "mood": MusicMood.CINEMATIC,
        "genre": MusicGenre.ORCHESTRAL,
        "prompt": "Cinematic orchestral music with rich strings, dramatic yet elegant, perfect for premium TV advertisement",
    },
    "appliance": {
        "mood": MusicMood.CALM,
        "genre": MusicGenre.AMBIENT,
        "prompt": "Calm, sophisticated ambient music, modern home lifestyle feeling, clean and refreshing",
    },
    "wearable": {
        "mood": MusicMood.ENERGETIC,
        "genre": MusicGenre.ELECTRONIC,
        "prompt": "Energetic, motivational electronic music, fitness and health theme, uplifting beats",
    },
    "tablet": {
        "mood": MusicMood.INSPIRING,
        "genre": MusicGenre.CORPORATE,
        "prompt": "Inspiring corporate music, creative and productive mood, modern and professional",
    },
    "default": {
        "mood": MusicMood.UPBEAT,
        "genre": MusicGenre.ELECTRONIC,
        "prompt": "Modern, premium electronic music for Samsung brand, innovative and sophisticated feel",
    },
}


class SunoMusicAgent:
    """
    Agent for generating music using Suno AI.

    Note: Suno doesn't have an official public API yet.
    This implementation uses a third-party API wrapper or can be
    replaced with alternative services like Mubert or Beatoven.ai
    """

    # Using unofficial API endpoint (would need proper API in production)
    BASE_URL = "https://api.sunoai.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'SUNO_API_KEY', '')
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    async def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        make_instrumental: bool = True,
    ) -> MusicGenerationResult:
        """
        Generate music from a text prompt.

        Args:
            prompt: Description of the music to generate
            duration: Target duration in seconds
            make_instrumental: Generate without vocals

        Returns:
            MusicGenerationResult
        """
        try:
            response = await self.client.post(
                "/api/generate",
                json={
                    "prompt": prompt,
                    "duration": duration,
                    "make_instrumental": make_instrumental,
                    "wait_audio": False,
                },
            )
            response.raise_for_status()

            data = response.json()

            return MusicGenerationResult(
                task_id=data.get("id", ""),
                status=MusicStatus.PENDING,
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Suno API error: {e.response.text}")
            return MusicGenerationResult(
                task_id="",
                status=MusicStatus.FAILED,
                error=f"API error: {e.response.status_code}",
            )
        except Exception as e:
            logger.error(f"Music generation error: {str(e)}")
            return MusicGenerationResult(
                task_id="",
                status=MusicStatus.FAILED,
                error=str(e),
            )

    async def get_task_status(self, task_id: str) -> MusicGenerationResult:
        """Check the status of a music generation task."""
        try:
            response = await self.client.get(f"/api/get?ids={task_id}")
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                item = data[0]
                status_str = item.get("status", "pending")

                status_map = {
                    "pending": MusicStatus.PENDING,
                    "processing": MusicStatus.PROCESSING,
                    "complete": MusicStatus.COMPLETED,
                    "error": MusicStatus.FAILED,
                }

                result = MusicGenerationResult(
                    task_id=task_id,
                    status=status_map.get(status_str, MusicStatus.PENDING),
                    title=item.get("title"),
                )

                if result.status == MusicStatus.COMPLETED:
                    result.audio_url = item.get("audio_url")
                    result.duration = item.get("duration")

                return result

            return MusicGenerationResult(
                task_id=task_id,
                status=MusicStatus.FAILED,
                error="No data returned",
            )

        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return MusicGenerationResult(
                task_id=task_id,
                status=MusicStatus.FAILED,
                error=str(e),
            )

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 10,
        max_wait: int = 300,
    ) -> MusicGenerationResult:
        """Wait for music generation to complete."""
        elapsed = 0
        while elapsed < max_wait:
            result = await self.get_task_status(task_id)

            if result.status in [MusicStatus.COMPLETED, MusicStatus.FAILED]:
                return result

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        return MusicGenerationResult(
            task_id=task_id,
            status=MusicStatus.FAILED,
            error="Timeout waiting for music generation",
        )

    def get_preset_prompt(self, category: str = "default") -> Dict[str, Any]:
        """Get preset music configuration for a product category."""
        return SAMSUNG_MUSIC_PRESETS.get(category, SAMSUNG_MUSIC_PRESETS["default"])

    async def generate_for_category(
        self,
        category: str,
        duration: int = 30,
    ) -> MusicGenerationResult:
        """
        Generate music for a specific product category.

        Args:
            category: Product category (smartphone, tv, appliance, etc.)
            duration: Target duration in seconds

        Returns:
            MusicGenerationResult
        """
        preset = self.get_preset_prompt(category)
        return await self.generate_music(
            prompt=preset["prompt"],
            duration=duration,
            make_instrumental=True,
        )

    async def close(self):
        await self.client.aclose()


class MubertMusicAgent:
    """
    Alternative music agent using Mubert API.
    Has official API with commercial licensing.
    """

    BASE_URL = "https://api-b2b.mubert.com/v2"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'MUBERT_API_KEY', '')
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Content-Type": "application/json"},
            timeout=60.0,
        )

    async def generate_track(
        self,
        prompt: str,
        duration: int = 30,
        intensity: str = "medium",
    ) -> MusicGenerationResult:
        """
        Generate a music track.

        Args:
            prompt: Text prompt describing the music
            duration: Duration in seconds
            intensity: low, medium, high

        Returns:
            MusicGenerationResult
        """
        try:
            response = await self.client.post(
                "/TTMRecordTrack",
                json={
                    "method": "TTMRecordTrack",
                    "params": {
                        "pat": self.api_key,
                        "prompt": prompt,
                        "duration": duration,
                        "intensity": intensity,
                        "format": "mp3",
                    },
                },
            )
            response.raise_for_status()

            data = response.json()

            if data.get("status") == 1:
                return MusicGenerationResult(
                    task_id=data.get("data", {}).get("task_id", ""),
                    status=MusicStatus.PENDING,
                )

            return MusicGenerationResult(
                task_id="",
                status=MusicStatus.FAILED,
                error=data.get("error", {}).get("text", "Unknown error"),
            )

        except Exception as e:
            logger.error(f"Mubert error: {str(e)}")
            return MusicGenerationResult(
                task_id="",
                status=MusicStatus.FAILED,
                error=str(e),
            )

    async def get_track_status(self, task_id: str) -> MusicGenerationResult:
        """Check track generation status."""
        try:
            response = await self.client.post(
                "/TrackStatus",
                json={
                    "method": "TrackStatus",
                    "params": {
                        "pat": self.api_key,
                        "task_id": task_id,
                    },
                },
            )
            response.raise_for_status()

            data = response.json()
            task_data = data.get("data", {})

            if task_data.get("status") == "done":
                return MusicGenerationResult(
                    task_id=task_id,
                    status=MusicStatus.COMPLETED,
                    audio_url=task_data.get("download_link"),
                    duration=task_data.get("duration"),
                )
            elif task_data.get("status") == "error":
                return MusicGenerationResult(
                    task_id=task_id,
                    status=MusicStatus.FAILED,
                    error=task_data.get("error", "Generation failed"),
                )

            return MusicGenerationResult(
                task_id=task_id,
                status=MusicStatus.PROCESSING,
            )

        except Exception as e:
            logger.error(f"Mubert status error: {str(e)}")
            return MusicGenerationResult(
                task_id=task_id,
                status=MusicStatus.FAILED,
                error=str(e),
            )

    async def close(self):
        await self.client.aclose()


class StockMusicAgent:
    """
    Agent for using pre-licensed stock music.
    Fallback option when AI generation is not needed or available.
    """

    # Samsung-approved stock music library
    STOCK_TRACKS = {
        "tech_upbeat": {
            "url": "/assets/music/tech_upbeat.mp3",
            "duration": 60,
            "mood": MusicMood.TECH,
            "bpm": 120,
        },
        "cinematic_premium": {
            "url": "/assets/music/cinematic_premium.mp3",
            "duration": 90,
            "mood": MusicMood.DRAMATIC,
            "bpm": 80,
        },
        "ambient_modern": {
            "url": "/assets/music/ambient_modern.mp3",
            "duration": 120,
            "mood": MusicMood.CALM,
            "bpm": 90,
        },
        "energetic_fitness": {
            "url": "/assets/music/energetic_fitness.mp3",
            "duration": 60,
            "mood": MusicMood.ENERGETIC,
            "bpm": 140,
        },
        "inspiring_corporate": {
            "url": "/assets/music/inspiring_corporate.mp3",
            "duration": 90,
            "mood": MusicMood.INSPIRING,
            "bpm": 100,
        },
    }

    def get_track_for_mood(self, mood: MusicMood) -> Dict[str, Any]:
        """Get a stock track matching the mood."""
        for track_id, track in self.STOCK_TRACKS.items():
            if track["mood"] == mood:
                return {"id": track_id, **track}

        # Default track
        return {"id": "tech_upbeat", **self.STOCK_TRACKS["tech_upbeat"]}

    def get_track_for_category(self, category: str) -> Dict[str, Any]:
        """Get a stock track for product category."""
        category_moods = {
            "smartphone": MusicMood.TECH,
            "tv": MusicMood.DRAMATIC,
            "appliance": MusicMood.CALM,
            "wearable": MusicMood.ENERGETIC,
            "tablet": MusicMood.INSPIRING,
        }

        mood = category_moods.get(category, MusicMood.TECH)
        return self.get_track_for_mood(mood)


# Factory function
def get_music_agent(provider: str = "suno") -> SunoMusicAgent | MubertMusicAgent | StockMusicAgent:
    """Get the music generation agent for the specified provider."""
    if provider == "mubert":
        return MubertMusicAgent()
    elif provider == "stock":
        return StockMusicAgent()
    return SunoMusicAgent()
