"""
Celery Application Configuration

Configures Celery for async task processing.
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "saiad",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.video_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,

    # Result settings
    result_expires=3600,  # 1 hour
    result_extended=True,

    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,

    # Task routing
    task_routes={
        "app.tasks.video_tasks.generate_video_task": {"queue": "video"},
        "app.tasks.video_tasks.composite_video_task": {"queue": "video"},
        "app.tasks.video_tasks.export_video_task": {"queue": "video"},
    },

    # Rate limiting
    task_annotations={
        "app.tasks.video_tasks.generate_video_task": {
            "rate_limit": "10/m",  # 10 per minute (API rate limits)
        },
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-jobs": {
            "task": "app.tasks.video_tasks.cleanup_expired_jobs",
            "schedule": 3600.0,  # Every hour
        },
        "check-stalled-jobs": {
            "task": "app.tasks.video_tasks.check_stalled_jobs",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)


def get_celery_app() -> Celery:
    """Get the Celery app instance."""
    return celery_app
