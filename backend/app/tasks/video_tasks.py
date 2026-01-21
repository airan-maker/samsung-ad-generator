"""
Video Generation Celery Tasks

Async tasks for video generation pipeline.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from celery import shared_task
from celery.utils.log import get_task_logger
import redis

from app.tasks.celery_app import celery_app
from app.agents.pipeline import run_video_pipeline, PipelineProgress
from app.core.config import settings

logger = get_task_logger(__name__)

# Redis client for job status tracking
redis_client = redis.from_url(settings.REDIS_URL)


def get_job_key(job_id: str) -> str:
    """Get Redis key for job status."""
    return f"saiad:job:{job_id}"


def update_job_status(
    job_id: str,
    status: str,
    progress: int = 0,
    current_step: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
):
    """Update job status in Redis."""
    job_data = {
        "status": status,
        "progress": progress,
        "current_step": current_step,
        "updated_at": datetime.utcnow().isoformat(),
    }

    if result:
        job_data["result"] = result
    if error:
        job_data["error"] = error

    redis_client.setex(
        get_job_key(job_id),
        timedelta(hours=24),  # TTL: 24 hours
        json.dumps(job_data),
    )


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job status from Redis."""
    data = redis_client.get(get_job_key(job_id))
    if data:
        return json.loads(data)
    return None


@celery_app.task(bind=True, name="app.tasks.video_tasks.generate_video_task")
def generate_video_task(
    self,
    job_id: str,
    project_id: str,
    product: Dict[str, Any],
    template: Dict[str, Any],
    config: Dict[str, Any],
    script: Optional[Dict[str, Any]] = None,
):
    """
    Main video generation task.

    Args:
        job_id: Unique job identifier
        project_id: Project ID
        product: Product information
        template: Template configuration
        config: Generation settings
        script: Pre-generated script (optional)
    """
    logger.info(f"Starting video generation task: {job_id}")

    # Update initial status
    update_job_status(
        job_id,
        status="processing",
        progress=0,
        current_step="initializing",
    )

    def on_progress(progress: PipelineProgress):
        """Callback for pipeline progress updates."""
        update_job_status(
            job_id,
            status="processing",
            progress=progress.progress,
            current_step=progress.stage.value,
        )

    try:
        # Run the async pipeline in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                run_video_pipeline(
                    project_id=project_id,
                    product=product,
                    template=template,
                    config=config,
                    existing_script=script,
                    on_progress=on_progress,
                )
            )
        finally:
            loop.close()

        if result.success:
            update_job_status(
                job_id,
                status="completed",
                progress=100,
                current_step="completed",
                result={
                    "video_url": result.video_url,
                    "thumbnail_url": result.thumbnail_url,
                    "duration": result.duration,
                    "metadata": result.metadata,
                },
            )
            logger.info(f"Video generation completed: {job_id}")

            # Trigger post-processing
            post_process_video.delay(job_id, project_id, result.video_url)

            return {
                "success": True,
                "video_url": result.video_url,
            }

        else:
            update_job_status(
                job_id,
                status="failed",
                progress=0,
                error=result.error,
            )
            logger.error(f"Video generation failed: {job_id} - {result.error}")
            return {
                "success": False,
                "error": result.error,
            }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Video generation error: {job_id} - {error_msg}")

        update_job_status(
            job_id,
            status="failed",
            progress=0,
            error=error_msg,
        )

        # Retry on transient errors
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            raise self.retry(exc=e, countdown=60, max_retries=3)

        return {
            "success": False,
            "error": error_msg,
        }


@celery_app.task(name="app.tasks.video_tasks.post_process_video")
def post_process_video(
    job_id: str,
    project_id: str,
    video_url: str,
):
    """
    Post-process generated video.

    - Generate additional formats
    - Create preview thumbnail
    - Update project record in database
    """
    logger.info(f"Post-processing video: {job_id}")

    try:
        # Generate thumbnail
        generate_thumbnail.delay(job_id, video_url)

        # Generate additional export formats
        for format_name in ["instagram", "tiktok"]:
            export_video_format.delay(job_id, video_url, format_name)

        # Update project in database
        update_project_video.delay(project_id, job_id, video_url)

        logger.info(f"Post-processing initiated: {job_id}")

    except Exception as e:
        logger.error(f"Post-processing error: {job_id} - {str(e)}")


@celery_app.task(name="app.tasks.video_tasks.generate_thumbnail")
def generate_thumbnail(job_id: str, video_url: str) -> Optional[str]:
    """Generate thumbnail from video."""
    logger.info(f"Generating thumbnail: {job_id}")

    # In production, use FFmpeg to extract frame
    # For now, return placeholder
    thumbnail_url = video_url.replace(".mp4", "_thumb.jpg")

    # Store thumbnail URL
    job_data = get_job_status(job_id)
    if job_data and job_data.get("result"):
        job_data["result"]["thumbnail_url"] = thumbnail_url
        redis_client.setex(
            get_job_key(job_id),
            timedelta(hours=24),
            json.dumps(job_data),
        )

    return thumbnail_url


@celery_app.task(name="app.tasks.video_tasks.export_video_format")
def export_video_format(
    job_id: str,
    video_url: str,
    format_name: str,
) -> Optional[str]:
    """Export video to a specific format."""
    logger.info(f"Exporting video to {format_name}: {job_id}")

    format_specs = {
        "instagram": {"aspect": "9:16", "resolution": "1080x1920"},
        "tiktok": {"aspect": "9:16", "resolution": "1080x1920"},
        "youtube_short": {"aspect": "9:16", "resolution": "1080x1920"},
        "square": {"aspect": "1:1", "resolution": "1080x1080"},
    }

    spec = format_specs.get(format_name)
    if not spec:
        logger.warning(f"Unknown format: {format_name}")
        return None

    # In production, use FFmpeg to convert
    # For now, return placeholder
    export_url = video_url.replace(".mp4", f"_{format_name}.mp4")

    # Store export URL
    job_data = get_job_status(job_id)
    if job_data:
        exports = job_data.get("exports", {})
        exports[format_name] = export_url
        job_data["exports"] = exports
        redis_client.setex(
            get_job_key(job_id),
            timedelta(hours=24),
            json.dumps(job_data),
        )

    return export_url


@celery_app.task(name="app.tasks.video_tasks.update_project_video")
def update_project_video(
    project_id: str,
    job_id: str,
    video_url: str,
):
    """Update project with generated video."""
    logger.info(f"Updating project {project_id} with video")

    # This would update the database in production
    # Using sync database access or another async task

    # For now, just log
    logger.info(f"Project {project_id} updated with video: {video_url}")


@celery_app.task(name="app.tasks.video_tasks.cleanup_expired_jobs")
def cleanup_expired_jobs():
    """Clean up expired job data from Redis."""
    logger.info("Running cleanup for expired jobs")

    # Redis TTL handles expiration automatically
    # This task is for additional cleanup if needed

    pattern = "saiad:job:*"
    cursor = 0
    cleaned = 0

    while True:
        cursor, keys = redis_client.scan(cursor, match=pattern, count=100)

        for key in keys:
            job_data = redis_client.get(key)
            if job_data:
                data = json.loads(job_data)
                updated_at = data.get("updated_at")

                if updated_at:
                    updated = datetime.fromisoformat(updated_at)
                    if datetime.utcnow() - updated > timedelta(days=7):
                        redis_client.delete(key)
                        cleaned += 1

        if cursor == 0:
            break

    logger.info(f"Cleaned up {cleaned} expired jobs")
    return cleaned


@celery_app.task(name="app.tasks.video_tasks.check_stalled_jobs")
def check_stalled_jobs():
    """Check for stalled jobs and mark as failed."""
    logger.info("Checking for stalled jobs")

    pattern = "saiad:job:*"
    cursor = 0
    stalled = 0

    while True:
        cursor, keys = redis_client.scan(cursor, match=pattern, count=100)

        for key in keys:
            job_data = redis_client.get(key)
            if job_data:
                data = json.loads(job_data)

                if data.get("status") == "processing":
                    updated_at = data.get("updated_at")
                    if updated_at:
                        updated = datetime.fromisoformat(updated_at)
                        # Mark as stalled if no update for 30 minutes
                        if datetime.utcnow() - updated > timedelta(minutes=30):
                            data["status"] = "failed"
                            data["error"] = "Job timed out (stalled)"
                            data["updated_at"] = datetime.utcnow().isoformat()
                            redis_client.setex(
                                key,
                                timedelta(hours=24),
                                json.dumps(data),
                            )
                            stalled += 1

        if cursor == 0:
            break

    logger.info(f"Marked {stalled} stalled jobs as failed")
    return stalled


@celery_app.task(name="app.tasks.video_tasks.cancel_job")
def cancel_job(job_id: str) -> bool:
    """Cancel a running job."""
    logger.info(f"Cancelling job: {job_id}")

    job_data = get_job_status(job_id)
    if not job_data:
        return False

    if job_data.get("status") in ["completed", "failed", "cancelled"]:
        return False

    update_job_status(
        job_id,
        status="cancelled",
        progress=0,
        error="Job cancelled by user",
    )

    # In production, would also revoke Celery task
    # celery_app.control.revoke(task_id, terminate=True)

    return True
