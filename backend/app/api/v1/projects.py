from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel

from app.db import get_db
from app.models.project import Project, ProjectStatus
from app.core.security import get_current_user_id

router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str
    product_id: Optional[str] = None
    custom_product_image: Optional[str] = None
    custom_product_name: Optional[str] = None
    template_id: str
    config: dict


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    config: Optional[dict] = None


class ProjectListResponse(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    total_pages: int


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Validate that either product_id or custom_product_image is provided
    if not request.product_id and not request.custom_product_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either product_id or custom_product_image must be provided",
        )

    project = Project(
        user_id=user_id,
        name=request.name,
        product_id=request.product_id,
        template_id=request.template_id,
        custom_product_image=request.custom_product_image,
        custom_product_name=request.custom_product_name,
        config=request.config,
        status=ProjectStatus.DRAFT,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Load relationships
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.product), selectinload(Project.template))
        .where(Project.id == project.id)
    )
    project = result.scalar_one()

    return project.to_dict()


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(Project).where(Project.user_id == user_id)

    if status_filter:
        try:
            st = ProjectStatus(status_filter)
            query = query.where(Project.status == st)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}",
            )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate and order
    query = (
        query.options(selectinload(Project.product), selectinload(Project.template))
        .order_by(Project.updated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    result = await db.execute(query)
    projects = result.scalars().all()

    return ProjectListResponse(
        items=[
            {
                "id": str(p.id),
                "name": p.name,
                "product_name": p.product.name if p.product else p.custom_product_name,
                "template_name": p.template.name if p.template else None,
                "status": p.status.value,
                "thumbnail": p.product.thumbnail if p.product else p.custom_product_image,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in projects
        ],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 0,
    )


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.product),
            selectinload(Project.template),
            selectinload(Project.videos),
        )
        .where(Project.id == project_id, Project.user_id == user_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project.to_dict()


@router.patch("/{project_id}")
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if request.name is not None:
        project.name = request.name

    if request.config is not None:
        project.config = {**(project.config or {}), **request.config}

    await db.commit()
    await db.refresh(project)

    return project.to_dict()


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    await db.delete(project)
    await db.commit()
