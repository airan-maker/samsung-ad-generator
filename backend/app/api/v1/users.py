from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.db import get_db
from app.models.user import User
from app.core.security import get_current_user_id

router = APIRouter()


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    profile_image: Optional[str]
    plan: str
    credits: int
    created_at: Optional[str]


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        profile_image=user.profile_image,
        plan=user.plan.value,
        credits=user.credits,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    request: UpdateUserRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if request.name is not None:
        user.name = request.name

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        profile_image=user.profile_image,
        plan=user.plan.value,
        credits=user.credits,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


@router.get("/me/credits")
async def get_user_credits(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's credit balance."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Calculate monthly credits based on plan
    plan_credits = {
        "free": 3,
        "basic": 30,
        "pro": 100,
        "enterprise": 999,
    }

    return {
        "credits": user.credits,
        "plan": user.plan.value,
        "monthly_limit": plan_credits.get(user.plan.value, 3),
    }
