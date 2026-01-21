from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List

from app.db import get_db
from app.models.user import User, PlanType
from app.models.payment import Payment, PaymentStatus
from app.core.security import get_current_user_id

router = APIRouter()


class SubscribeRequest(BaseModel):
    plan: str  # basic, pro
    payment_method: str  # card


class SubscribeResponse(BaseModel):
    payment_url: str
    order_id: str


class CancelResponse(BaseModel):
    message: str
    effective_date: str


class PaymentHistoryResponse(BaseModel):
    items: List[dict]
    total: int


@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(
    request: SubscribeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Validate plan
    valid_plans = ["basic", "pro"]
    if request.plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}",
        )

    # Get plan price
    plan_prices = {
        "basic": 19900,
        "pro": 49900,
    }
    amount = plan_prices[request.plan]

    # Create payment record
    import uuid

    order_id = f"order_{uuid.uuid4().hex[:12]}"
    payment = Payment(
        user_id=user_id,
        amount=amount,
        plan=request.plan,
        payment_method=request.payment_method,
        transaction_id=order_id,
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    await db.commit()

    # In production, create Toss Payments checkout session
    # For now, return mock URL
    payment_url = f"https://pay.tosspayments.com/checkout/{order_id}"

    return SubscribeResponse(
        payment_url=payment_url,
        order_id=order_id,
    )


@router.post("/cancel", response_model=CancelResponse)
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.plan == PlanType.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel",
        )

    # In production, cancel with payment provider
    # Update user plan (effective at end of billing period)
    from datetime import datetime, timedelta

    effective_date = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"

    return CancelResponse(
        message="구독이 취소되었습니다.",
        effective_date=effective_date,
    )


@router.get("/history", response_model=PaymentHistoryResponse)
async def get_payment_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()

    return PaymentHistoryResponse(
        items=[p.to_dict() for p in payments],
        total=len(payments),
    )
