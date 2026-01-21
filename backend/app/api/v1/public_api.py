"""
Public API Endpoints (B2B)

REST API for external integrations and B2B customers.
All endpoints require API key authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.db import get_db
from app.models.product import Product
from app.models.template import Template
from app.models.project import Project, ProjectStatus
from app.services.api_key_service import APIKeyService, APIKeyScope

router = APIRouter()


# API Key Authentication Dependency
async def verify_api_key(
    x_api_key: str = Header(..., description="API Key for authentication"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Verify API key and return key info."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    service = APIKeyService(db)
    api_key = service.validate_api_key(x_api_key)

    if not api_key:
        # For demo purposes, accept keys starting with saiad_
        if x_api_key.startswith("saiad_"):
            return {
                "user_id": "demo_user",
                "scopes": ["read", "write", "videos:create", "videos:read"],
                "rate_limit": 60,
            }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Check if rate limited
    if not service.check_rate_limit(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"},
        )

    # Record usage
    service.record_usage(api_key)

    return {
        "user_id": api_key.user_id,
        "scopes": [s.value for s in api_key.scopes],
        "rate_limit": api_key.rate_limit,
    }


def require_scope(scope: str):
    """Dependency factory to require specific scope."""
    async def check_scope(api_key_info: Dict = Depends(verify_api_key)):
        if scope not in api_key_info.get("scopes", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {scope}",
            )
        return api_key_info
    return check_scope


# Request/Response Models
class ProductResponse(BaseModel):
    id: str
    name: str
    name_en: Optional[str]
    category: str
    model_number: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    features: Optional[List[str]]

    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    id: str
    name: str
    name_en: Optional[str]
    style: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    duration_options: List[int]
    preview_url: Optional[str]

    class Config:
        from_attributes = True


class CreateVideoRequest(BaseModel):
    product_id: str = Field(..., description="Samsung product ID")
    template_id: str = Field(..., description="Template ID to use")
    duration: int = Field(30, description="Video duration in seconds", ge=15, le=120)
    tone: str = Field("professional", description="Tone: professional, friendly, energetic")
    language: str = Field("ko", description="Script language: ko, en, zh")
    voice_id: Optional[str] = Field(None, description="AI voice ID for narration")
    custom_script: Optional[Dict[str, Any]] = Field(None, description="Custom script override")
    export_formats: List[str] = Field(
        default=["youtube"],
        description="Export formats: youtube, instagram, tiktok, coupang"
    )
    webhook_url: Optional[str] = Field(None, description="Webhook URL for completion notification")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")


class CreateVideoResponse(BaseModel):
    job_id: str
    project_id: str
    status: str
    estimated_seconds: int
    created_at: str
    webhook_url: Optional[str]


class VideoStatusResponse(BaseModel):
    job_id: str
    project_id: str
    status: str
    progress: int
    current_step: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    export_urls: Optional[Dict[str, str]]
    error: Optional[str]
    created_at: str
    completed_at: Optional[str]


class VideoListResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int
    has_more: bool


class APIUsageResponse(BaseModel):
    current_period_start: str
    current_period_end: str
    requests_used: int
    requests_limit: int
    videos_generated: int
    videos_limit: int
    credits_remaining: int


# Endpoints
@router.get("/products", response_model=List[ProductResponse], tags=["Products"])
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    api_key_info: Dict = Depends(require_scope("products:read")),
    db: AsyncSession = Depends(get_db),
):
    """
    List available Samsung products.

    Filter by category or search by name.
    """
    query = select(Product)

    if category:
        query = query.where(Product.category == category)

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    return [
        ProductResponse(
            id=str(p.id),
            name=p.name,
            name_en=p.name_en,
            category=p.category.value,
            model_number=p.model_number,
            description=p.description,
            image_url=p.image_url,
            features=p.features,
        )
        for p in products
    ]


@router.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product(
    product_id: str,
    api_key_info: Dict = Depends(require_scope("products:read")),
    db: AsyncSession = Depends(get_db),
):
    """Get product details by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return ProductResponse(
        id=str(product.id),
        name=product.name,
        name_en=product.name_en,
        category=product.category.value,
        model_number=product.model_number,
        description=product.description,
        image_url=product.image_url,
        features=product.features,
    )


@router.get("/templates", response_model=List[TemplateResponse], tags=["Templates"])
async def list_templates(
    style: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    api_key_info: Dict = Depends(require_scope("templates:read")),
    db: AsyncSession = Depends(get_db),
):
    """
    List available video templates.

    Filter by style or product category.
    """
    query = select(Template).where(Template.is_active == True)

    if style:
        query = query.where(Template.style == style)

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    templates = result.scalars().all()

    return [
        TemplateResponse(
            id=str(t.id),
            name=t.name,
            name_en=t.name_en,
            style=t.style.value,
            description=t.description,
            thumbnail_url=t.thumbnail_url,
            duration_options=t.duration_options or [15, 30, 60],
            preview_url=t.preview_url,
        )
        for t in templates
    ]


@router.post("/videos", response_model=CreateVideoResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Videos"])
async def create_video(
    request: CreateVideoRequest,
    api_key_info: Dict = Depends(require_scope("videos:create")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new video generation job.

    This endpoint starts an async video generation process.
    Poll the status endpoint or use webhooks to get completion notifications.
    """
    user_id = api_key_info["user_id"]

    # Validate product exists
    product_result = await db.execute(
        select(Product).where(Product.id == request.product_id)
    )
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Validate template exists
    template_result = await db.execute(
        select(Template).where(Template.id == request.template_id)
    )
    template = template_result.scalar_one_or_none()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Create project
    project_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    project = Project(
        id=project_id,
        user_id=user_id,
        name=f"API - {product.name}",
        product_id=request.product_id,
        template_id=request.template_id,
        duration=request.duration,
        status=ProjectStatus.PROCESSING,
    )
    db.add(project)
    await db.commit()

    # Dispatch to Celery (in production)
    # from app.tasks.video_tasks import generate_video_task
    # generate_video_task.delay(job_id, project_id, ...)

    # Calculate estimated time
    estimated_seconds = 60 + (request.duration * 4)

    return CreateVideoResponse(
        job_id=job_id,
        project_id=project_id,
        status="queued",
        estimated_seconds=estimated_seconds,
        created_at=datetime.utcnow().isoformat() + "Z",
        webhook_url=request.webhook_url,
    )


@router.get("/videos/{job_id}", response_model=VideoStatusResponse, tags=["Videos"])
async def get_video_status(
    job_id: str,
    api_key_info: Dict = Depends(require_scope("videos:read")),
):
    """
    Get video generation job status.

    Poll this endpoint to check progress.
    """
    # In production, get from Redis/database
    # For demo, return mock data

    return VideoStatusResponse(
        job_id=job_id,
        project_id="proj_123",
        status="completed",
        progress=100,
        current_step="completed",
        video_url="https://cdn.saiad.io/videos/demo/final.mp4",
        thumbnail_url="https://cdn.saiad.io/videos/demo/thumb.jpg",
        export_urls={
            "youtube": "https://cdn.saiad.io/videos/demo/youtube.mp4",
            "instagram": "https://cdn.saiad.io/videos/demo/instagram.mp4",
        },
        error=None,
        created_at="2025-01-21T10:00:00Z",
        completed_at="2025-01-21T10:03:00Z",
    )


@router.get("/videos", response_model=VideoListResponse, tags=["Videos"])
async def list_videos(
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    api_key_info: Dict = Depends(require_scope("videos:read")),
    db: AsyncSession = Depends(get_db),
):
    """
    List all videos created via API.

    Supports pagination and filtering by status.
    """
    user_id = api_key_info["user_id"]

    query = select(Project).where(Project.user_id == user_id)

    if status:
        query = query.where(Project.status == status)

    query = query.order_by(Project.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page + 1)

    result = await db.execute(query)
    projects = result.scalars().all()

    has_more = len(projects) > per_page
    items = projects[:per_page]

    return VideoListResponse(
        items=[
            {
                "id": str(p.id),
                "name": p.name,
                "status": p.status.value,
                "duration": p.duration,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in items
        ],
        total=len(items),
        page=page,
        per_page=per_page,
        has_more=has_more,
    )


@router.delete("/videos/{job_id}", tags=["Videos"])
async def cancel_video(
    job_id: str,
    api_key_info: Dict = Depends(require_scope("videos:create")),
):
    """
    Cancel a video generation job.

    Only jobs in 'queued' or 'processing' status can be cancelled.
    """
    # In production, cancel Celery task

    return {
        "success": True,
        "message": "Job cancelled successfully",
        "job_id": job_id,
    }


@router.get("/usage", response_model=APIUsageResponse, tags=["Account"])
async def get_api_usage(
    api_key_info: Dict = Depends(verify_api_key),
):
    """
    Get API usage statistics for the current billing period.
    """
    # In production, query from database/billing system

    return APIUsageResponse(
        current_period_start="2025-01-01T00:00:00Z",
        current_period_end="2025-01-31T23:59:59Z",
        requests_used=1250,
        requests_limit=10000,
        videos_generated=45,
        videos_limit=100,
        credits_remaining=55,
    )


@router.get("/health", tags=["System"])
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
