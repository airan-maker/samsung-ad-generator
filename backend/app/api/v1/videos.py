from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import uuid

from app.db import get_db
from app.models.project import Project, ProjectStatus
from app.models.video import Video
from app.core.security import get_current_user_id

router = APIRouter()


class GenerateVideoRequest(BaseModel):
    project_id: str
    script: dict
    config: dict


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
    steps: Optional[list] = None
    estimated_remaining: Optional[int] = None
    video: Optional[dict] = None
    error: Optional[dict] = None


class DownloadResponse(BaseModel):
    download_url: str
    expires_at: str
    format: dict


# In-memory job storage (use Redis in production)
_jobs = {}


@router.post("/generate", response_model=GenerationJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: GenerateVideoRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
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

    # Check user credits
    # In production, verify user has enough credits

    # Update project status
    project.status = ProjectStatus.PROCESSING
    project.script = request.script
    await db.commit()

    # Create job
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "project_id": request.project_id,
        "status": "queued",
        "progress": 0,
        "config": request.config,
    }

    # In production, dispatch to Celery worker
    # from app.tasks.video_tasks import generate_video_task
    # generate_video_task.delay(job_id, request.project_id, request.script, request.config)

    return GenerationJobResponse(
        job_id=job_id,
        project_id=request.project_id,
        status="queued",
        estimated_time=180,  # 3 minutes
    )


@router.get("/{job_id}/status", response_model=VideoStatusResponse)
async def get_video_status(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
):
    job = _jobs.get(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # In production, get status from Celery/Redis
    # For demo, return mock progress
    return VideoStatusResponse(
        job_id=job_id,
        status=job.get("status", "queued"),
        progress=job.get("progress", 0),
        current_step=job.get("current_step"),
        steps=[
            {"name": "script_processing", "status": "completed"},
            {"name": "image_processing", "status": "completed"},
            {"name": "video_generation", "status": "in_progress"},
            {"name": "video_compositing", "status": "pending"},
            {"name": "audio_mixing", "status": "pending"},
        ],
        estimated_remaining=120,
    )


@router.get("/{video_id}/download", response_model=DownloadResponse)
async def get_download_url(
    video_id: str,
    format: Optional[str] = Query("youtube"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
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

    # Generate signed URL (in production, use S3 presigned URL)
    format_specs = {
        "youtube": {"aspect_ratio": "16:9", "resolution": "1080p"},
        "instagram": {"aspect_ratio": "9:16", "resolution": "1080p"},
        "tiktok": {"aspect_ratio": "9:16", "resolution": "1080p"},
        "coupang": {"aspect_ratio": "1:1", "resolution": "720p"},
    }

    spec = format_specs.get(format, format_specs["youtube"])

    from datetime import datetime, timedelta

    return DownloadResponse(
        download_url=f"{video.video_url}?format={format}",
        expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        format={
            "name": format,
            **spec,
        },
    )
