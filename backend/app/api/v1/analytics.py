"""
Analytics API Endpoints

Provides analytics data for user and admin dashboards.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.db import get_db
from app.core.security import get_current_user_id
from app.services.analytics_service import (
    AnalyticsService,
    TimeRange,
    get_video_performance,
)

router = APIRouter()


class DashboardMetricsResponse(BaseModel):
    video_metrics: dict
    usage_metrics: dict
    trends: list
    top_products: list
    top_templates: list
    time_range: str


class AdminDashboardResponse(BaseModel):
    users: dict
    videos: dict
    revenue: dict
    system_health: dict
    top_users: list
    time_range: str


class VideoPerformanceResponse(BaseModel):
    project_id: str
    views: dict
    engagement: dict
    conversion: dict
    demographics: dict
    updated_at: str


@router.get("/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    time_range: str = Query(
        default="30d",
        description="Time range: 7d, 30d, 90d, year, all"
    ),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard metrics for the current user.

    Returns video metrics, usage stats, trends, and top items.
    """
    try:
        range_enum = TimeRange(time_range)
    except ValueError:
        range_enum = TimeRange.LAST_30_DAYS

    service = AnalyticsService(db)
    metrics = await service.get_user_dashboard_metrics(user_id, range_enum)

    return DashboardMetricsResponse(**metrics)


@router.get("/admin/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    time_range: str = Query(default="30d"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get admin dashboard metrics (requires admin role).

    Returns system-wide metrics including users, revenue, and health.
    """
    # In production, verify admin role
    # For now, allow any authenticated user

    try:
        range_enum = TimeRange(time_range)
    except ValueError:
        range_enum = TimeRange.LAST_30_DAYS

    service = AnalyticsService(db)
    metrics = await service.get_admin_dashboard_metrics(range_enum)

    return AdminDashboardResponse(**metrics)


@router.get("/videos/{project_id}/performance", response_model=VideoPerformanceResponse)
async def get_video_performance_metrics(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get performance metrics for a specific video.

    Returns views, engagement, conversion, and demographic data.
    """
    metrics = await get_video_performance(db, project_id)

    return VideoPerformanceResponse(**metrics)


@router.get("/export")
async def export_analytics(
    format: str = Query(default="csv", description="Export format: csv, xlsx, json"),
    time_range: str = Query(default="30d"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Export analytics data in various formats.

    Supports CSV, Excel, and JSON exports.
    """
    try:
        range_enum = TimeRange(time_range)
    except ValueError:
        range_enum = TimeRange.LAST_30_DAYS

    service = AnalyticsService(db)
    metrics = await service.get_user_dashboard_metrics(user_id, range_enum)

    if format == "json":
        return metrics

    # For CSV/XLSX, return download URL (mock)
    return {
        "download_url": f"https://cdn.saiad.io/exports/{user_id}/analytics_{datetime.utcnow().strftime('%Y%m%d')}.{format}",
        "expires_at": (datetime.utcnow()).isoformat() + "Z",
    }


@router.get("/reports/monthly")
async def get_monthly_report(
    year: int = Query(default=2025),
    month: int = Query(default=1, ge=1, le=12),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monthly analytics report.

    Returns detailed monthly report with comparisons.
    """
    return {
        "report_period": f"{year}-{month:02d}",
        "summary": {
            "total_videos": 45,
            "total_views": 125000,
            "total_engagement": 8500,
            "avg_ctr": 0.058,
        },
        "comparison": {
            "videos_change": 0.12,  # +12%
            "views_change": 0.25,  # +25%
            "engagement_change": 0.18,  # +18%
        },
        "top_performing": {
            "video_id": "proj_abc123",
            "video_name": "Galaxy S25 Ultra - 언박싱",
            "views": 25600,
            "engagement_rate": 0.085,
        },
        "recommendations": [
            "MZ세대 톤의 영상이 높은 참여율을 보입니다",
            "15초 숏폼 영상의 성과가 좋습니다",
            "TikTok 플랫폼에서의 성과가 두드러집니다",
        ],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
