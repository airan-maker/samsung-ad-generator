"""
A/B Testing API Endpoints

Handles multi-version video generation for A/B testing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

from app.db import get_db
from app.models.project import Project
from app.models.user import User, PlanType
from app.core.security import get_current_user_id
from app.services.ab_testing_service import (
    ABTestingService,
    get_available_tones,
)

router = APIRouter()


class CreateABTestRequest(BaseModel):
    project_id: str
    tones: Optional[List[str]] = None  # Default: all 3 tones


class ToneResponse(BaseModel):
    id: str
    name: str
    description: str


class ABTestVersionResponse(BaseModel):
    version_id: str
    tone: str
    name: str
    status: str
    script_title: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error: Optional[str] = None


class ABTestResponse(BaseModel):
    test_id: str
    project_id: str
    status: str
    versions: List[ABTestVersionResponse]
    total_versions: int
    completed_versions: int
    created_at: str
    completed_at: Optional[str] = None


class GenerateABTestResponse(BaseModel):
    test_id: str
    message: str
    versions_count: int


@router.get("/tones", response_model=List[ToneResponse])
async def list_tones():
    """
    Get available tones for A/B testing.

    Returns the 3 standard tones: Premium, Practical, MZ.
    """
    tones = get_available_tones()
    return [ToneResponse(**t) for t in tones]


@router.post("/create", response_model=GenerateABTestResponse)
async def create_ab_test(
    request: CreateABTestRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new A/B test for a project.

    This will generate multiple versions of the video with different tones.
    Requires Pro plan or higher.
    """
    # Check user plan
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # A/B testing requires Pro plan or higher
    if user.plan not in [PlanType.PRO, PlanType.ENTERPRISE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A/B testing requires Pro plan or higher",
        )

    # Get project
    project_result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == user_id,
        )
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Determine number of versions
    tones = request.tones or ["premium", "practical", "mz"]
    versions_count = len(tones)

    # Check if user has enough credits
    if user.credits < versions_count:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {versions_count}, have {user.credits}",
        )

    # Create A/B test
    service = ABTestingService()

    product_info = {
        "id": str(project.product_id),
        "name": project.product.name if project.product else "Unknown",
        "category": project.product.category.value if project.product else "smartphone",
    }

    template_info = {
        "id": str(project.template_id),
        "name": project.template.name if project.template else "Unknown",
        "style": project.template.style.value if project.template else "unboxing",
    }

    config = {
        "duration": project.duration or 30,
    }

    ab_test = await service.create_ab_test(
        project_id=request.project_id,
        product=product_info,
        template=template_info,
        config=config,
        tones=tones,
    )

    # Deduct credits
    user.credits -= versions_count
    await db.commit()

    # Start background task for video generation
    # In production, this would dispatch to Celery
    # generate_ab_test_videos.delay(ab_test.test_id, ...)

    return GenerateABTestResponse(
        test_id=ab_test.test_id,
        message=f"A/B test created with {versions_count} versions",
        versions_count=versions_count,
    )


@router.get("/{test_id}", response_model=ABTestResponse)
async def get_ab_test(
    test_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get A/B test status and results.

    Returns all versions with their current status.
    """
    # In production, fetch from database
    # For now, return mock data

    return ABTestResponse(
        test_id=test_id,
        project_id="proj_123",
        status="completed",
        versions=[
            ABTestVersionResponse(
                version_id="v1",
                tone="premium",
                name="프리미엄",
                status="completed",
                script_title="Galaxy S25 Ultra - 혁신의 정점",
                video_url="https://cdn.saiad.io/videos/v1/premium.mp4",
                thumbnail_url="https://cdn.saiad.io/videos/v1/premium_thumb.jpg",
            ),
            ABTestVersionResponse(
                version_id="v2",
                tone="practical",
                name="실용적",
                status="completed",
                script_title="Galaxy S25 Ultra - 당신의 일상을 바꾸다",
                video_url="https://cdn.saiad.io/videos/v2/practical.mp4",
                thumbnail_url="https://cdn.saiad.io/videos/v2/practical_thumb.jpg",
            ),
            ABTestVersionResponse(
                version_id="v3",
                tone="mz",
                name="MZ세대",
                status="completed",
                script_title="갤럭시 S25 울트라, 이거 실화?",
                video_url="https://cdn.saiad.io/videos/v3/mz.mp4",
                thumbnail_url="https://cdn.saiad.io/videos/v3/mz_thumb.jpg",
            ),
        ],
        total_versions=3,
        completed_versions=3,
        created_at="2025-01-21T10:00:00Z",
        completed_at="2025-01-21T10:15:00Z",
    )


@router.get("/{test_id}/compare")
async def compare_versions(
    test_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get side-by-side comparison data for A/B test versions.

    Returns detailed comparison including scripts and metrics.
    """
    # In production, fetch from database

    return {
        "test_id": test_id,
        "versions": [
            {
                "version_id": "v1",
                "tone": "premium",
                "name": "프리미엄",
                "script": {
                    "title": "Galaxy S25 Ultra - 혁신의 정점",
                    "scenes": [
                        {
                            "scene_number": 1,
                            "narration": "당신이 상상하던 그 미래, 이제 손안에 있습니다.",
                            "duration": 5,
                        },
                    ],
                },
                "video_url": "https://cdn.saiad.io/videos/v1/premium.mp4",
                "characteristics": ["고급스러운 톤", "제품 가치 강조", "감성적 어필"],
            },
            {
                "version_id": "v2",
                "tone": "practical",
                "name": "실용적",
                "script": {
                    "title": "Galaxy S25 Ultra - 당신의 일상을 바꾸다",
                    "scenes": [
                        {
                            "scene_number": 1,
                            "narration": "200MP 카메라로 놓치는 순간 없이 기록하세요.",
                            "duration": 5,
                        },
                    ],
                },
                "video_url": "https://cdn.saiad.io/videos/v2/practical.mp4",
                "characteristics": ["기능 중심", "실용적 혜택", "명확한 정보 전달"],
            },
            {
                "version_id": "v3",
                "tone": "mz",
                "name": "MZ세대",
                "script": {
                    "title": "갤럭시 S25 울트라, 이거 실화?",
                    "scenes": [
                        {
                            "scene_number": 1,
                            "narration": "역대급 카메라에 AI까지? 미쳤다 진짜.",
                            "duration": 5,
                        },
                    ],
                },
                "video_url": "https://cdn.saiad.io/videos/v3/mz.mp4",
                "characteristics": ["트렌디한 표현", "캐주얼한 톤", "젊은 타겟"],
            },
        ],
        "recommendation": {
            "best_for_brand": "premium",
            "best_for_conversion": "practical",
            "best_for_engagement": "mz",
        },
    }


@router.post("/{test_id}/select/{version_id}")
async def select_version(
    test_id: str,
    version_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Select a winning version from the A/B test.

    This makes the selected version the main video for the project.
    """
    # In production:
    # 1. Find the A/B test and version
    # 2. Update project with selected version's video
    # 3. Mark A/B test as finalized

    return {
        "success": True,
        "message": f"Version {version_id} selected as winner",
        "video_url": f"https://cdn.saiad.io/videos/{version_id}/final.mp4",
    }
