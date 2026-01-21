from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List

from app.db import get_db
from app.models.project import Project
from app.core.security import get_current_user_id
from app.agents.script_agent import ScriptAgent

router = APIRouter()


class GenerateScriptRequest(BaseModel):
    project_id: str
    tone: str  # premium, practical, mz
    language: str  # ko, en, zh
    custom_keywords: Optional[List[str]] = None


class RegenerateScriptRequest(BaseModel):
    project_id: str
    field: str  # headline, subline, narration, cta
    current_value: str
    instruction: Optional[str] = None


class ScriptResponse(BaseModel):
    headline: str
    subline: str
    narration: str
    cta: str
    scenes: Optional[list] = None
    alternatives: Optional[dict] = None


class RegenerateResponse(BaseModel):
    field: str
    value: str
    alternatives: List[str]


@router.post("/generate", response_model=ScriptResponse)
async def generate_script(
    request: GenerateScriptRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Get project
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == user_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get product info
    product_name = None
    product_features = []
    product_specs = {}

    if project.product:
        product_name = project.product.name
        product_features = project.product.features or []
        product_specs = project.product.specs or {}
    elif project.custom_product_name:
        product_name = project.custom_product_name

    if not product_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product information not available",
        )

    # Get template info
    template_style = None
    if project.template:
        template_style = project.template.style.value

    # Generate script using AI agent
    agent = ScriptAgent()
    script = await agent.generate(
        product_name=product_name,
        product_features=product_features,
        product_specs=product_specs,
        template_style=template_style,
        tone=request.tone,
        language=request.language,
        duration=project.config.get("duration", 30) if project.config else 30,
        custom_keywords=request.custom_keywords,
    )

    # Save script to project
    project.script = script
    await db.commit()

    return ScriptResponse(**script)


@router.post("/regenerate", response_model=RegenerateResponse)
async def regenerate_script(
    request: RegenerateScriptRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Get project
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == user_id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not project.script:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No script generated yet",
        )

    # Validate field
    valid_fields = ["headline", "subline", "narration", "cta"]
    if request.field not in valid_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field. Must be one of: {', '.join(valid_fields)}",
        )

    # Regenerate specific field using AI agent
    agent = ScriptAgent()
    result = await agent.regenerate_field(
        field=request.field,
        current_value=request.current_value,
        instruction=request.instruction,
        context={
            "product_name": project.product.name if project.product else project.custom_product_name,
            "existing_script": project.script,
        },
    )

    # Update script
    project.script[request.field] = result["value"]
    await db.commit()

    return RegenerateResponse(**result)
