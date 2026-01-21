from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create tables if not exist (for development)
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="SaiAd API",
    description="""
# Samsung AI Advertisement Generator API

AI-powered video advertisement generator for Samsung Electronics products.

## Overview

SaiAd provides a comprehensive API for:
- **Video Generation**: Create professional advertisement videos automatically
- **Template Selection**: Choose from 12+ optimized advertisement templates
- **AI Script Generation**: Generate compelling copy using Claude AI
- **Multi-format Export**: Export for YouTube, Instagram, TikTok, and Coupang

## Authentication

### Internal API (Web App)
Uses JWT Bearer tokens via `/api/v1/auth` endpoints.

### Public API (B2B)
Uses API key authentication via `X-API-Key` header.
Contact sales@saiad.io for API access.

## Rate Limits

| Plan | Requests/min | Videos/month |
|------|-------------|--------------|
| Free | 10 | 5 |
| Basic | 30 | 50 |
| Pro | 60 | 200 |
| Enterprise | Custom | Unlimited |

## Support

- Documentation: https://docs.saiad.io
- Email: support@saiad.io
- Status: https://status.saiad.io
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication endpoints for user login/registration",
        },
        {
            "name": "users",
            "description": "User profile and account management",
        },
        {
            "name": "products",
            "description": "Samsung product catalog browsing and search",
        },
        {
            "name": "templates",
            "description": "Advertisement video template selection",
        },
        {
            "name": "projects",
            "description": "Video project management",
        },
        {
            "name": "videos",
            "description": "Video generation and processing",
        },
        {
            "name": "scripts",
            "description": "AI-powered advertisement script generation",
        },
        {
            "name": "payments",
            "description": "Subscription and payment management (Toss Payments)",
        },
        {
            "name": "voices",
            "description": "AI voice selection for narration",
        },
        {
            "name": "ab-tests",
            "description": "A/B testing for multi-version video generation",
        },
        {
            "name": "public-api",
            "description": "B2B Public API for external integrations (API key required)",
        },
    ],
    contact={
        "name": "SaiAd Support",
        "email": "support@saiad.io",
        "url": "https://saiad.io",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://saiad.io/terms",
    },
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware (only in production)
if settings.ENVIRONMENT == "production":
    from app.core.security_middleware import setup_security_middleware
    setup_security_middleware(app)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "environment": settings.ENVIRONMENT}


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        },
    )
