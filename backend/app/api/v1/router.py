from fastapi import APIRouter

from app.api.v1 import auth, products, templates, projects, videos, scripts, payments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
