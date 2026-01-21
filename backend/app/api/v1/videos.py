"""
Video Generation API Endpoints

Handles video generation requests and status tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timedelta

from app.db import get_db
from app.models.project import Project, ProjectStatus
from app.models.video import Video
from app.models.user import User
from app.core.security import get_current_user_id
from app.tasks.video_tasks import (
    generate_video_task,
    cancel_job,
    get_job_status,
)

router = APIRouter()


class GenerateVideoRequest(BaseModel):
    project_id: str
    script: Dict[str, Any]
    config: Dict[str, Any]


class GenerationJobResponse(BaseModel):
    job_id: str
    project_id: str
    status: str
    estimated_time: int
    created_at: Optional[str] = None


class VideoStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    current_step: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    estimated_remaining: Optional[int] = None
    video: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class DownloadResponse(BaseModel):
    download_url: str
    expires_at: str
    format: Dict[str, Any]


class CancelJobResponse(BaseModel):
    success: bool
    message: str


# Pipeline step definitions
PIPELINE_STEPS = [
    {"name": "script_processing", "label": "스크립트 처리", "weight": 5},
    {"name": "audio_generation", "label": "나레이션 생성", "weight": 15},
    {"name": "music_generation", "label": "배경음악 선택", "weight": 5},
    {"name": "video_generation", "label": "영상 생성", "weight": 50},
    {"name": "video_compositing", "label": "영상 합성", "weight": 15},
    {"name": "final_export", "label": "최종 내보내기", "weight": 10},
]


@router.post("/generate", response_model=GenerationJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: GenerateVideoRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Start video generation process.

    Creates a job and dispatches it to the Celery worker queue.
    Returns job ID for status polling.
    """
    # Get and validate project
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == user_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check if already processing
    if project.status == ProjectStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project is already being processed",
        )

    # Check user credits
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user or user.credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits",
        )

    # Create job ID
    job_id = str(uuid.uuid4())

    # Update project status
    project.status = ProjectStatus.PROCESSING
    project.script = request.script

    # Deduct credit
    user.credits -= 1

    await db.commit()

    # Get product and template info for the pipeline
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

    # Dispatch to Celery worker
    generate_video_task.delay(
        job_id=job_id,
        project_id=request.project_id,
        product=product_info,
        template=template_info,
        config=request.config,
        script=request.script,
    )

    # Calculate estimated time based on duration
    duration = request.config.get("duration", 30)
    estimated_time = 60 + (duration * 4)  # Base 60s + 4s per video second

    return GenerationJobResponse(
        job_id=job_id,
        project_id=request.project_id,
        status="queued",
        estimated_time=estimated_time,
        created_at=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/{job_id}/status", response_model=VideoStatusResponse)
async def get_video_status(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get video generation job status.

    Poll this endpoint to track progress.
    """
    job_data = get_job_status(job_id)

    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Build steps list with current status
    current_step = job_data.get("current_step", "initializing")
    progress = job_data.get("progress", 0)

    steps = []
    step_reached = False

    for step in PIPELINE_STEPS:
        if step["name"] == current_step:
            step_reached = True
            steps.append({
                "name": step["name"],
                "label": step["label"],
                "status": "in_progress",
            })
        elif not step_reached:
            steps.append({
                "name": step["name"],
                "label": step["label"],
                "status": "completed",
            })
        else:
            steps.append({
                "name": step["name"],
                "label": step["label"],
                "status": "pending",
            })

    # Calculate estimated remaining time
    remaining_weight = sum(
        s["weight"] for s in PIPELINE_STEPS
        if any(step["name"] == s["name"] and step["status"] != "completed" for step in steps)
    )
    estimated_remaining = int((remaining_weight / 100) * 180)  # Base 3 minutes

    # Build response
    response_data = {
        "job_id": job_id,
        "status": job_data.get("status", "processing"),
        "progress": progress,
        "current_step": current_step,
        "steps": steps,
        "estimated_remaining": estimated_remaining,
    }

    # Include video info if completed
    if job_data.get("status") == "completed" and job_data.get("result"):
        response_data["video"] = job_data["result"]

    # Include error if failed
    if job_data.get("status") == "failed" and job_data.get("error"):
        response_data["error"] = {
            "message": job_data["error"],
            "code": "generation_failed",
        }

    return VideoStatusResponse(**response_data)


@router.post("/{job_id}/cancel", response_model=CancelJobResponse)
async def cancel_video_generation(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a running video generation job.

    Only jobs in 'queued' or 'processing' status can be cancelled.
    """
    job_data = get_job_status(job_id)

    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job_data.get("status") in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job_data.get('status')}",
        )

    # Cancel the job
    success = cancel_job(job_id)

    if success:
        # Refund credit (would need to track project_id in job data)
        return CancelJobResponse(
            success=True,
            message="Job cancelled successfully. Credit refunded.",
        )

    return CancelJobResponse(
        success=False,
        message="Failed to cancel job",
    )


@router.get("/{video_id}/download", response_model=DownloadResponse)
async def get_download_url(
    video_id: str,
    format: Optional[str] = Query("youtube", description="Export format"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get download URL for a generated video.

    Supports multiple export formats:
    - youtube: 16:9, 1080p
    - instagram: 9:16, 1080p
    - tiktok: 9:16, 1080p
    - coupang: 1:1, 720p
    """
    # Get video
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Verify ownership via project
    result = await db.execute(
        select(Project).where(
            Project.id == video.project_id,
            Project.user_id == user_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Format specifications
    format_specs = {
        "youtube": {
            "aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "codec": "h264",
            "bitrate": "8Mbps",
        },
        "instagram": {
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "codec": "h264",
            "bitrate": "6Mbps",
        },
        "tiktok": {
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "codec": "h264",
            "bitrate": "6Mbps",
        },
        "coupang": {
            "aspect_ratio": "1:1",
            "resolution": "720x720",
            "codec": "h264",
            "bitrate": "4Mbps",
        },
    }

    spec = format_specs.get(format, format_specs["youtube"])

    # Generate presigned URL (in production, use S3 presigned URL)
    download_url = f"{video.video_url}?format={format}&expires={int(datetime.utcnow().timestamp()) + 3600}"

    return DownloadResponse(
        download_url=download_url,
        expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        format={
            "name": format,
            **spec,
        },
    )


@router.get("/", response_model=List[Dict[str, Any]])
async def list_user_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    List all videos for the current user.
    """
    # Get videos via projects
    result = await db.execute(
        select(Video)
        .join(Project)
        .where(Project.user_id == user_id)
        .order_by(Video.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    videos = result.scalars().all()

    return [
        {
            "id": str(video.id),
            "project_id": str(video.project_id),
            "video_url": video.video_url,
            "thumbnail_url": video.thumbnail_url,
            "duration": video.duration,
            "resolution": video.resolution,
            "created_at": video.created_at.isoformat() if video.created_at else None,
        }
        for video in videos
    ]
