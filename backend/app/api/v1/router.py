from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    products,
    templates,
    projects,
    videos,
    scripts,
    payments,
    voices,
    ab_tests,
    public_api,
    analytics,
    collaboration,
    storyboard,
)

api_router = APIRouter()

# Internal API routes (requires JWT authentication)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(voices.router, prefix="/voices", tags=["voices"])
api_router.include_router(ab_tests.router, prefix="/ab-tests", tags=["ab-tests"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["collaboration"])
api_router.include_router(storyboard.router, prefix="/storyboard", tags=["storyboard"])

# Public API routes (B2B - requires API key authentication)
api_router.include_router(public_api.router, prefix="/public", tags=["public-api"])
