"""
Analytics Service

Provides analytics data for user dashboard and admin dashboard.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import logging

from app.models.project import Project, ProjectStatus
from app.models.user import User

logger = logging.getLogger(__name__)


class TimeRange(Enum):
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    THIS_YEAR = "year"
    ALL_TIME = "all"


@dataclass
class VideoMetrics:
    total_videos: int
    completed_videos: int
    failed_videos: int
    in_progress_videos: int
    average_generation_time: float  # seconds
    total_duration: int  # total video duration in seconds


@dataclass
class UsageMetrics:
    total_api_calls: int
    videos_generated: int
    credits_used: int
    credits_remaining: int
    storage_used: float  # GB


@dataclass
class TrendData:
    date: str
    videos: int
    api_calls: int


class AnalyticsService:
    """Service for generating analytics data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_dashboard_metrics(
        self,
        user_id: str,
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
    ) -> Dict[str, Any]:
        """
        Get dashboard metrics for a specific user.

        Args:
            user_id: User ID
            time_range: Time range for metrics

        Returns:
            Dashboard metrics including videos, usage, trends
        """
        start_date = self._get_start_date(time_range)

        # Get video metrics
        video_metrics = await self._get_video_metrics(user_id, start_date)

        # Get usage metrics
        usage_metrics = await self._get_usage_metrics(user_id)

        # Get trend data
        trend_data = await self._get_trend_data(user_id, start_date)

        # Get top products
        top_products = await self._get_top_products(user_id, start_date)

        # Get top templates
        top_templates = await self._get_top_templates(user_id, start_date)

        return {
            "video_metrics": {
                "total": video_metrics.total_videos,
                "completed": video_metrics.completed_videos,
                "failed": video_metrics.failed_videos,
                "in_progress": video_metrics.in_progress_videos,
                "avg_generation_time": video_metrics.average_generation_time,
                "total_duration": video_metrics.total_duration,
            },
            "usage_metrics": {
                "api_calls": usage_metrics.total_api_calls,
                "videos_generated": usage_metrics.videos_generated,
                "credits_used": usage_metrics.credits_used,
                "credits_remaining": usage_metrics.credits_remaining,
                "storage_used_gb": usage_metrics.storage_used,
            },
            "trends": [
                {
                    "date": t.date,
                    "videos": t.videos,
                    "api_calls": t.api_calls,
                }
                for t in trend_data
            ],
            "top_products": top_products,
            "top_templates": top_templates,
            "time_range": time_range.value,
        }

    async def get_admin_dashboard_metrics(
        self,
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
    ) -> Dict[str, Any]:
        """
        Get admin dashboard metrics (all users).

        Args:
            time_range: Time range for metrics

        Returns:
            Admin dashboard metrics
        """
        start_date = self._get_start_date(time_range)

        # Total users
        total_users = await self._get_total_users()

        # Active users (created video in time range)
        active_users = await self._get_active_users(start_date)

        # New users in time range
        new_users = await self._get_new_users(start_date)

        # Total videos
        total_videos = await self._get_total_videos(start_date)

        # Revenue metrics (mock for now)
        revenue = self._get_revenue_metrics(start_date)

        # System health
        system_health = self._get_system_health()

        # Top users by usage
        top_users = await self._get_top_users(start_date)

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "new": new_users,
            },
            "videos": {
                "total": total_videos,
                "completed_rate": 0.95,
                "avg_generation_time": 120,
            },
            "revenue": revenue,
            "system_health": system_health,
            "top_users": top_users,
            "time_range": time_range.value,
        }

    async def _get_video_metrics(
        self, user_id: str, start_date: datetime
    ) -> VideoMetrics:
        """Get video metrics for a user."""
        query = select(Project).where(
            and_(
                Project.user_id == user_id,
                Project.created_at >= start_date,
            )
        )
        result = await self.db.execute(query)
        projects = result.scalars().all()

        total = len(projects)
        completed = sum(1 for p in projects if p.status == ProjectStatus.COMPLETED)
        failed = sum(1 for p in projects if p.status == ProjectStatus.FAILED)
        in_progress = sum(
            1 for p in projects if p.status in [ProjectStatus.PROCESSING, ProjectStatus.DRAFT]
        )

        # Calculate average generation time (mock)
        avg_time = 120.0  # 2 minutes average

        # Total video duration
        total_duration = sum(p.duration or 30 for p in projects if p.status == ProjectStatus.COMPLETED)

        return VideoMetrics(
            total_videos=total,
            completed_videos=completed,
            failed_videos=failed,
            in_progress_videos=in_progress,
            average_generation_time=avg_time,
            total_duration=total_duration,
        )

    async def _get_usage_metrics(self, user_id: str) -> UsageMetrics:
        """Get usage metrics for a user."""
        # Get user
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        credits_remaining = user.credits if user else 0

        # Count total projects
        result = await self.db.execute(
            select(func.count(Project.id)).where(Project.user_id == user_id)
        )
        total_projects = result.scalar() or 0

        return UsageMetrics(
            total_api_calls=total_projects * 5,  # Estimated API calls per project
            videos_generated=total_projects,
            credits_used=total_projects,
            credits_remaining=credits_remaining,
            storage_used=total_projects * 0.05,  # ~50MB per video
        )

    async def _get_trend_data(
        self, user_id: str, start_date: datetime
    ) -> List[TrendData]:
        """Get daily trend data."""
        trends = []
        current_date = start_date
        today = datetime.utcnow()

        while current_date <= today:
            # Count videos for this day
            next_date = current_date + timedelta(days=1)
            result = await self.db.execute(
                select(func.count(Project.id)).where(
                    and_(
                        Project.user_id == user_id,
                        Project.created_at >= current_date,
                        Project.created_at < next_date,
                    )
                )
            )
            video_count = result.scalar() or 0

            trends.append(
                TrendData(
                    date=current_date.strftime("%Y-%m-%d"),
                    videos=video_count,
                    api_calls=video_count * 5,
                )
            )
            current_date = next_date

        return trends

    async def _get_top_products(
        self, user_id: str, start_date: datetime, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top products used by user."""
        # In production, this would be a proper GROUP BY query
        # For now, return mock data
        return [
            {"product_id": "galaxy-s25-ultra", "name": "Galaxy S25 Ultra", "count": 15},
            {"product_id": "galaxy-z-fold6", "name": "Galaxy Z Fold 6", "count": 8},
            {"product_id": "galaxy-buds3-pro", "name": "Galaxy Buds 3 Pro", "count": 5},
            {"product_id": "galaxy-watch7", "name": "Galaxy Watch 7", "count": 3},
            {"product_id": "galaxy-ring", "name": "Galaxy Ring", "count": 2},
        ][:limit]

    async def _get_top_templates(
        self, user_id: str, start_date: datetime, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top templates used by user."""
        return [
            {"template_id": "unboxing", "name": "언박싱", "count": 12},
            {"template_id": "feature-highlight", "name": "기능 하이라이트", "count": 9},
            {"template_id": "comparison", "name": "비교 분석", "count": 6},
            {"template_id": "lifestyle", "name": "라이프스타일", "count": 4},
            {"template_id": "review", "name": "리뷰", "count": 2},
        ][:limit]

    async def _get_total_users(self) -> int:
        """Get total user count."""
        result = await self.db.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def _get_active_users(self, start_date: datetime) -> int:
        """Get active users count."""
        result = await self.db.execute(
            select(func.count(func.distinct(Project.user_id))).where(
                Project.created_at >= start_date
            )
        )
        return result.scalar() or 0

    async def _get_new_users(self, start_date: datetime) -> int:
        """Get new users count."""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= start_date)
        )
        return result.scalar() or 0

    async def _get_total_videos(self, start_date: datetime) -> int:
        """Get total videos count."""
        result = await self.db.execute(
            select(func.count(Project.id)).where(Project.created_at >= start_date)
        )
        return result.scalar() or 0

    def _get_revenue_metrics(self, start_date: datetime) -> Dict[str, Any]:
        """Get revenue metrics (mock data)."""
        return {
            "total": 15000000,  # 15M KRW
            "subscriptions": 12000000,
            "one_time": 3000000,
            "growth_rate": 0.15,  # 15% growth
        }

    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        return {
            "api_latency_ms": 145,
            "video_queue_size": 12,
            "error_rate": 0.02,
            "uptime": 0.999,
            "storage_used_tb": 2.5,
            "storage_limit_tb": 10,
        }

    async def _get_top_users(
        self, start_date: datetime, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top users by video count."""
        # In production, proper GROUP BY query
        return [
            {"user_id": "user_1", "email": "user1@example.com", "videos": 45, "plan": "pro"},
            {"user_id": "user_2", "email": "user2@example.com", "videos": 32, "plan": "enterprise"},
            {"user_id": "user_3", "email": "user3@example.com", "videos": 28, "plan": "pro"},
        ][:limit]

    def _get_start_date(self, time_range: TimeRange) -> datetime:
        """Calculate start date based on time range."""
        now = datetime.utcnow()

        if time_range == TimeRange.LAST_7_DAYS:
            return now - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            return now - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            return now - timedelta(days=90)
        elif time_range == TimeRange.THIS_YEAR:
            return datetime(now.year, 1, 1)
        else:
            return datetime(2020, 1, 1)  # All time


async def get_video_performance(
    db: AsyncSession,
    project_id: str,
) -> Dict[str, Any]:
    """
    Get performance metrics for a specific video.

    In production, this would integrate with YouTube Analytics,
    Meta Ads Manager, etc.
    """
    return {
        "project_id": project_id,
        "views": {
            "youtube": 15420,
            "instagram": 8930,
            "tiktok": 25600,
            "coupang": 3200,
        },
        "engagement": {
            "likes": 1250,
            "comments": 89,
            "shares": 234,
        },
        "conversion": {
            "clicks": 890,
            "ctr": 0.058,
            "conversions": 45,
            "conversion_rate": 0.051,
        },
        "demographics": {
            "age_groups": {
                "18-24": 0.35,
                "25-34": 0.42,
                "35-44": 0.15,
                "45+": 0.08,
            },
            "gender": {
                "male": 0.48,
                "female": 0.52,
            },
            "top_countries": [
                {"country": "KR", "percentage": 0.72},
                {"country": "US", "percentage": 0.12},
                {"country": "JP", "percentage": 0.08},
            ],
        },
        "updated_at": datetime.utcnow().isoformat(),
    }
