from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel

from app.db import get_db
from app.models.product import Product, ProductCategory

router = APIRouter()


class ProductListResponse(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    total_pages: int


class CategoryResponse(BaseModel):
    categories: list


@router.get("", response_model=ProductListResponse)
async def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    query = select(Product)

    if category:
        try:
            cat = ProductCategory(category)
            query = query.where(Product.category == cat)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}",
            )

    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%") | Product.model_number.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        items=[p.to_dict() for p in products],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
    )


@router.get("/categories", response_model=CategoryResponse)
async def get_categories(db: AsyncSession = Depends(get_db)):
    # Get count per category
    query = select(
        Product.category,
        func.count(Product.id).label("count"),
    ).group_by(Product.category)

    result = await db.execute(query)
    rows = result.all()

    category_info = {
        ProductCategory.SMARTPHONE: {"name": "스마트폰", "icon": "📱"},
        ProductCategory.TV: {"name": "TV", "icon": "📺"},
        ProductCategory.APPLIANCE: {"name": "가전", "icon": "🏠"},
        ProductCategory.WEARABLE: {"name": "웨어러블", "icon": "⌚"},
    }

    categories = []
    for row in rows:
        info = category_info.get(row.category, {"name": row.category.value, "icon": "📦"})
        categories.append({
            "id": row.category.value,
            "name": info["name"],
            "icon": info["icon"],
            "count": row.count,
        })

    # Add categories with 0 count
    existing_cats = {row.category for row in rows}
    for cat, info in category_info.items():
        if cat not in existing_cats:
            categories.append({
                "id": cat.value,
                "name": info["name"],
                "icon": info["icon"],
                "count": 0,
            })

    return CategoryResponse(categories=categories)


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product.to_dict()


@router.post("/recognize")
async def recognize_product(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # In production, this would:
    # 1. Upload image to S3
    # 2. Call Vision API (GPT-4V or Claude) to identify product
    # 3. Match with products in database

    # For now, return mock response
    return {
        "recognized": False,
        "message": "제품을 인식하지 못했습니다. 직접 선택해주세요.",
        "suggestions": [],
    }
