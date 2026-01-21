"""
Celery Tasks Package

Async task processing for video generation pipeline.
"""

from app.tasks.celery_app import celery_app

__all__ = ["celery_app"]
