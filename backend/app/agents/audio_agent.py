"""
Audio Generation Agent - ElevenLabs API Integration

Generates high-quality AI narration/voiceover for videos.
"""

import httpx
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging
import io

from app.core.config import settings

logger = logging.getLogger(__name__)


class VoiceLanguage(Enum):
    KOREAN = "ko"
    ENGLISH = "en"
    JAPANESE = "ja"
    CHINESE = "zh"


class VoiceStyle(Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ENERGETIC = "energetic"
    CALM = "calm"


@dataclass
class Voice:
    voice_id: str
    name: str
    language: VoiceLanguage
    style: VoiceStyle
    preview_url: Optional[str] = None


@dataclass
class AudioGenerationResult:
    success: bool
    audio_data: Optional[bytes] = None
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None


# Predefined voices for Samsung ads - organized by language
SAMSUNG_VOICES = {
    # Korean voices
    "ko_professional_male": Voice(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam
        name="전문가 남성",
        language=VoiceLanguage.KOREAN,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/ko_professional_male.mp3",
    ),
    "ko_professional_female": Voice(
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Rachel
        name="전문가 여성",
        language=VoiceLanguage.KOREAN,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/ko_professional_female.mp3",
    ),
    "ko_friendly_male": Voice(
        voice_id="VR6AewLTigWG4xSOukaG",  # Arnold
        name="친근한 남성",
        language=VoiceLanguage.KOREAN,
        style=VoiceStyle.FRIENDLY,
        preview_url="/audio/previews/ko_friendly_male.mp3",
    ),
    "ko_friendly_female": Voice(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Bella
        name="친근한 여성",
        language=VoiceLanguage.KOREAN,
        style=VoiceStyle.FRIENDLY,
        preview_url="/audio/previews/ko_friendly_female.mp3",
    ),
    "ko_energetic": Voice(
        voice_id="yoZ06aMxZJJ28mfd3POQ",  # Sam
        name="에너지틱",
        language=VoiceLanguage.KOREAN,
        style=VoiceStyle.ENERGETIC,
        preview_url="/audio/previews/ko_energetic.mp3",
    ),
    # English voices
    "en_professional_male": Voice(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam
        name="Professional Male",
        language=VoiceLanguage.ENGLISH,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/en_professional_male.mp3",
    ),
    "en_professional_female": Voice(
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Rachel
        name="Professional Female",
        language=VoiceLanguage.ENGLISH,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/en_professional_female.mp3",
    ),
    "en_friendly": Voice(
        voice_id="jBpfuIE2acCO8z3wKNLl",  # Emily
        name="Friendly",
        language=VoiceLanguage.ENGLISH,
        style=VoiceStyle.FRIENDLY,
        preview_url="/audio/previews/en_friendly.mp3",
    ),
    # Chinese voices
    "zh_professional_male": Voice(
        voice_id="g5CIjZEefAph4nQFvHAz",  # Chinese male
        name="专业男声",
        language=VoiceLanguage.CHINESE,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/zh_professional_male.mp3",
    ),
    "zh_professional_female": Voice(
        voice_id="Xb7hH8MSUJpSbSDYk0k2",  # Chinese female
        name="专业女声",
        language=VoiceLanguage.CHINESE,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/zh_professional_female.mp3",
    ),
    # Japanese voices
    "ja_professional_male": Voice(
        voice_id="GBv7mTt0atIp3Br8iCZE",  # Japanese male
        name="プロフェッショナル男性",
        language=VoiceLanguage.JAPANESE,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/ja_professional_male.mp3",
    ),
    "ja_professional_female": Voice(
        voice_id="XrExE9yKIg1WjnnlVkGX",  # Japanese female
        name="プロフェッショナル女性",
        language=VoiceLanguage.JAPANESE,
        style=VoiceStyle.PROFESSIONAL,
        preview_url="/audio/previews/ja_professional_female.mp3",
    ),
}


def get_voices_by_language(language: VoiceLanguage) -> List[Voice]:
    """Get all voices for a specific language."""
    return [
        voice for voice in SAMSUNG_VOICES.values()
        if voice.language == language
    ]


def get_all_voices_grouped() -> Dict[str, List[Dict[str, Any]]]:
    """Get all voices grouped by language for API response."""
    result = {}
    for lang in VoiceLanguage:
        result[lang.value] = [
            {
                "id": key,
                "name": voice.name,
                "style": voice.style.value,
                "preview_url": voice.preview_url,
            }
            for key, voice in SAMSUNG_VOICES.items()
            if voice.language == lang
        ]
    return result


class ElevenLabsAudioAgent:
    """Agent for generating voiceover using ElevenLabs API."""

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def generate_speech(
        self,
        text: str,
        voice_id: str = "pNInz6obpgDQGcFmaJgB",
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
    ) -> AudioGenerationResult:
        """
        Generate speech from text.

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: Model to use (eleven_multilingual_v2 for Korean)
            stability: Voice stability (0-1)
            similarity_boost: Voice clarity (0-1)
            style: Style exaggeration (0-1)
            use_speaker_boost: Enhance speaker similarity

        Returns:
            AudioGenerationResult with audio data
        """
        try:
            response = await self.client.post(
                f"/text-to-speech/{voice_id}",
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": similarity_boost,
                        "style": style,
                        "use_speaker_boost": use_speaker_boost,
                    },
                },
                headers={"Accept": "audio/mpeg"},
            )
            response.raise_for_status()

            return AudioGenerationResult(
                success=True,
                audio_data=response.content,
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error: {e.response.text}")
            return AudioGenerationResult(
                success=False,
                error=f"API error: {e.response.status_code}",
            )
        except Exception as e:
            logger.error(f"Audio generation error: {str(e)}")
            return AudioGenerationResult(
                success=False,
                error=str(e),
            )

    async def generate_speech_with_timestamps(
        self,
        text: str,
        voice_id: str = "pNInz6obpgDQGcFmaJgB",
        model_id: str = "eleven_multilingual_v2",
    ) -> Dict[str, Any]:
        """
        Generate speech with word-level timestamps for syncing.

        Returns audio data along with timing information.
        """
        try:
            response = await self.client.post(
                f"/text-to-speech/{voice_id}/with-timestamps",
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
            )
            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "audio_base64": data.get("audio_base64"),
                "alignment": data.get("alignment", {}),
                "normalized_alignment": data.get("normalized_alignment", {}),
            }

        except Exception as e:
            logger.error(f"Timestamped audio error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_voices(self) -> List[Dict[str, Any]]:
        """Get all available voices."""
        try:
            response = await self.client.get("/voices")
            response.raise_for_status()

            data = response.json()
            return data.get("voices", [])

        except Exception as e:
            logger.error(f"Get voices error: {str(e)}")
            return []

    async def get_user_info(self) -> Dict[str, Any]:
        """Get user subscription info and remaining characters."""
        try:
            response = await self.client.get("/user/subscription")
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Get user info error: {str(e)}")
            return {}

    def get_preset_voice(self, preset_key: str) -> Voice:
        """Get a preset voice by key."""
        return SAMSUNG_VOICES.get(preset_key, SAMSUNG_VOICES["ko_professional_female"])

    async def generate_for_script(
        self,
        script_segments: List[Dict[str, Any]],
        voice_preset: str = "ko_professional_female",
    ) -> List[AudioGenerationResult]:
        """
        Generate audio for multiple script segments.

        Args:
            script_segments: List of {text: str, start: float, end: float}
            voice_preset: Preset voice key

        Returns:
            List of AudioGenerationResult for each segment
        """
        voice = self.get_preset_voice(voice_preset)
        results = []

        for segment in script_segments:
            text = segment.get("text", "")
            if not text.strip():
                continue

            result = await self.generate_speech(
                text=text,
                voice_id=voice.voice_id,
            )
            results.append(result)

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)

        return results

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class OpenAITTSAgent:
    """
    Alternative TTS agent using OpenAI's TTS API.
    Good fallback option with consistent quality.
    """

    BASE_URL = "https://api.openai.com/v1"

    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def generate_speech(
        self,
        text: str,
        voice: str = "nova",
        model: str = "tts-1-hd",
        speed: float = 1.0,
    ) -> AudioGenerationResult:
        """
        Generate speech using OpenAI TTS.

        Args:
            text: Text to convert
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            model: tts-1 or tts-1-hd
            speed: Speech speed (0.25 to 4.0)

        Returns:
            AudioGenerationResult
        """
        try:
            response = await self.client.post(
                "/audio/speech",
                json={
                    "model": model,
                    "input": text,
                    "voice": voice,
                    "speed": speed,
                },
            )
            response.raise_for_status()

            return AudioGenerationResult(
                success=True,
                audio_data=response.content,
            )

        except Exception as e:
            logger.error(f"OpenAI TTS error: {str(e)}")
            return AudioGenerationResult(
                success=False,
                error=str(e),
            )

    async def close(self):
        await self.client.aclose()


# Factory function
def get_audio_agent(provider: str = "elevenlabs") -> ElevenLabsAudioAgent | OpenAITTSAgent:
    """Get the audio generation agent for the specified provider."""
    if provider == "openai":
        return OpenAITTSAgent()
    return ElevenLabsAudioAgent()
