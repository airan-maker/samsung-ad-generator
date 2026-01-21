"""
Voice API Endpoints

Handles AI voice selection and preview for narration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.security import get_current_user_id
from app.agents.audio_agent import (
    SAMSUNG_VOICES,
    VoiceLanguage,
    get_all_voices_grouped,
    ElevenLabsAudioAgent,
)

router = APIRouter()


class VoiceResponse(BaseModel):
    id: str
    name: str
    language: str
    style: str
    preview_url: Optional[str]


class VoicesListResponse(BaseModel):
    voices: Dict[str, List[VoiceResponse]]


class GeneratePreviewRequest(BaseModel):
    voice_id: str
    text: str = "안녕하세요. 삼성 AI 광고 생성기입니다."


class GeneratePreviewResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    error: Optional[str] = None


@router.get("/", response_model=VoicesListResponse)
async def list_voices():
    """
    Get all available AI voices grouped by language.

    Returns voices for Korean, English, Chinese, and Japanese.
    """
    grouped = get_all_voices_grouped()

    # Convert to response format
    result = {}
    for lang, voices in grouped.items():
        result[lang] = [
            VoiceResponse(
                id=v["id"],
                name=v["name"],
                language=lang,
                style=v["style"],
                preview_url=v["preview_url"],
            )
            for v in voices
        ]

    return VoicesListResponse(voices=result)


@router.get("/{voice_id}")
async def get_voice(voice_id: str):
    """Get details for a specific voice."""
    voice = SAMSUNG_VOICES.get(voice_id)

    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice not found",
        )

    return {
        "id": voice_id,
        "name": voice.name,
        "language": voice.language.value,
        "style": voice.style.value,
        "preview_url": voice.preview_url,
    }


@router.post("/preview", response_model=GeneratePreviewResponse)
async def generate_voice_preview(
    request: GeneratePreviewRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Generate a voice preview with custom text.

    This is a Pro feature that allows users to hear how their
    script will sound with different voices.
    """
    voice = SAMSUNG_VOICES.get(request.voice_id)

    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice not found",
        )

    # Limit text length for preview
    text = request.text[:200]

    agent = ElevenLabsAudioAgent()
    try:
        result = await agent.generate_speech(
            text=text,
            voice_id=voice.voice_id,
        )

        if result.success:
            # In production, upload to S3 and return URL
            # For now, return base64 encoded audio
            import base64
            audio_base64 = base64.b64encode(result.audio_data).decode() if result.audio_data else None

            return GeneratePreviewResponse(
                success=True,
                audio_url=f"data:audio/mpeg;base64,{audio_base64}" if audio_base64 else None,
            )
        else:
            return GeneratePreviewResponse(
                success=False,
                error=result.error,
            )
    finally:
        await agent.close()


@router.get("/languages/")
async def list_languages():
    """Get all supported languages for narration."""
    return {
        "languages": [
            {"code": "ko", "name": "한국어", "native_name": "한국어"},
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "zh", "name": "Chinese", "native_name": "中文"},
            {"code": "ja", "name": "Japanese", "native_name": "日本語"},
        ]
    }
