from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel

from app.db import get_db
from app.models.template import Template, TemplateStyle
from app.models.product import ProductCategory

router = APIRouter()


class TemplateListResponse(BaseModel):
    items: list
    total: int


@router.get("", response_model=TemplateListResponse)
async def get_templates(
    category: Optional[str] = Query(None),
    style: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Template)

    if category:
        try:
            cat = ProductCategory(category)
            query = query.where(Template.category == cat)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}",
            )

    if style:
        try:
            st = TemplateStyle(style)
            query = query.where(Template.style == st)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid style: {style}",
            )

    result = await db.execute(query)
    templates = result.scalars().all()

    return TemplateListResponse(
        items=[t.to_dict() for t in templates],
        total=len(templates),
    )


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Add scenes info if available in config
    template_dict = template.to_dict()
    if template.config and "scenes" in template.config:
        template_dict["scenes"] = template.config["scenes"]

    return template_dict
