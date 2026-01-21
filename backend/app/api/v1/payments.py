"""
Payment API Endpoints

Handles subscriptions, credit purchases, and payment webhooks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.db import get_db
from app.models.user import User, PlanType
from app.models.payment import Payment, PaymentStatus
from app.core.security import get_current_user_id
from app.services.payment_service import (
    TossPaymentsService,
    PLAN_CONFIG,
    CREDIT_PACKAGES,
    SubscriptionPlan,
    generate_order_id,
)

router = APIRouter()


# Request/Response Models
class PlanResponse(BaseModel):
    id: str
    name: str
    price: int
    credits: int
    features: List[str]
    max_duration: int
    max_resolution: str
    is_popular: bool = False


class PlansListResponse(BaseModel):
    plans: List[PlanResponse]


class CreditPackageResponse(BaseModel):
    credits: int
    price: int
    name: str
    discount: Optional[str] = None


class CreateCheckoutRequest(BaseModel):
    plan: str  # basic, pro, enterprise
    billing_cycle: str = "monthly"  # monthly, yearly


class CreateCheckoutResponse(BaseModel):
    order_id: str
    order_name: str
    amount: int
    client_key: str
    success_url: str
    fail_url: str


class ConfirmPaymentRequest(BaseModel):
    payment_key: str
    order_id: str
    amount: int


class ConfirmPaymentResponse(BaseModel):
    success: bool
    plan: Optional[str] = None
    credits: Optional[int] = None
    receipt_url: Optional[str] = None
    error: Optional[str] = None


class BuyCreditsRequest(BaseModel):
    package_index: int  # 0-3 for credit packages


class CancelSubscriptionRequest(BaseModel):
    reason: Optional[str] = None


class CancelResponse(BaseModel):
    message: str
    effective_date: str


class PaymentHistoryItem(BaseModel):
    id: str
    amount: int
    plan: Optional[str]
    credits: Optional[int]
    status: str
    created_at: str
    receipt_url: Optional[str]


class PaymentHistoryResponse(BaseModel):
    items: List[PaymentHistoryItem]
    total: int


# Endpoints
@router.get("/plans", response_model=PlansListResponse)
async def get_plans():
    """Get all available subscription plans."""
    plans = []

    for plan_enum, details in PLAN_CONFIG.items():
        plans.append(
            PlanResponse(
                id=plan_enum.value,
                name=details.name,
                price=details.price,
                credits=details.credits,
                features=details.features,
                max_duration=details.max_duration,
                max_resolution=details.max_resolution,
                is_popular=plan_enum == SubscriptionPlan.PRO,
            )
        )

    return PlansListResponse(plans=plans)


@router.get("/credit-packages", response_model=List[CreditPackageResponse])
async def get_credit_packages():
    """Get available credit packages for one-time purchase."""
    return [CreditPackageResponse(**pkg) for pkg in CREDIT_PACKAGES]


@router.post("/checkout", response_model=CreateCheckoutResponse)
async def create_checkout(
    request: CreateCheckoutRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a checkout session for subscription.

    Returns the necessary data for Toss Payments widget.
    """
    # Validate plan
    try:
        plan = SubscriptionPlan(request.plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan",
        )

    if plan == SubscriptionPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot checkout for free plan",
        )

    plan_details = PLAN_CONFIG[plan]

    # Calculate amount (yearly = 12 months * 0.8)
    if request.billing_cycle == "yearly":
        amount = int(plan_details.price * 12 * 0.8)
        order_name = f"SaiAD {plan_details.name} (연간)"
    else:
        amount = plan_details.price
        order_name = f"SaiAD {plan_details.name} (월간)"

    # Generate order ID
    order_id = generate_order_id("SUB")

    # Create pending payment record
    payment = Payment(
        id=uuid.uuid4(),
        user_id=user_id,
        amount=amount,
        plan=request.plan,
        payment_method="card",
        transaction_id=order_id,
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    await db.commit()

    from app.core.config import settings

    return CreateCheckoutResponse(
        order_id=order_id,
        order_name=order_name,
        amount=amount,
        client_key=settings.TOSS_CLIENT_KEY,
        success_url=f"https://saiad.io/payment/success?orderId={order_id}",
        fail_url=f"https://saiad.io/payment/fail?orderId={order_id}",
    )


@router.post("/checkout/credits", response_model=CreateCheckoutResponse)
async def create_credit_checkout(
    request: BuyCreditsRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a checkout session for credit purchase.
    """
    if request.package_index < 0 or request.package_index >= len(CREDIT_PACKAGES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid package index",
        )

    package = CREDIT_PACKAGES[request.package_index]
    order_id = generate_order_id("CRD")

    # Create pending payment record
    payment = Payment(
        id=uuid.uuid4(),
        user_id=user_id,
        amount=package["price"],
        plan=None,
        payment_method="card",
        transaction_id=order_id,
        status=PaymentStatus.PENDING,
        metadata={"credits": package["credits"]},
    )
    db.add(payment)
    await db.commit()

    from app.core.config import settings

    return CreateCheckoutResponse(
        order_id=order_id,
        order_name=package["name"],
        amount=package["price"],
        client_key=settings.TOSS_CLIENT_KEY,
        success_url=f"https://saiad.io/payment/success?orderId={order_id}&type=credits",
        fail_url=f"https://saiad.io/payment/fail?orderId={order_id}",
    )


@router.post("/confirm", response_model=ConfirmPaymentResponse)
async def confirm_payment(
    request: ConfirmPaymentRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm a payment after user completes checkout.

    This is called from the frontend after Toss redirect.
    """
    # Get payment record
    result = await db.execute(
        select(Payment).where(
            Payment.transaction_id == request.order_id,
            Payment.user_id == user_id,
        )
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already processed",
        )

    # Verify amount matches
    if payment.amount != request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount mismatch",
        )

    # Confirm with Toss
    payment_service = TossPaymentsService()
    try:
        result = await payment_service.confirm_payment(
            payment_key=request.payment_key,
            order_id=request.order_id,
            amount=request.amount,
        )
    finally:
        await payment_service.close()

    if not result.success:
        payment.status = PaymentStatus.FAILED
        await db.commit()
        return ConfirmPaymentResponse(
            success=False,
            error=result.error,
        )

    # Update payment record
    payment.status = PaymentStatus.COMPLETED
    payment.payment_key = request.payment_key

    # Get user and update plan/credits
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if user:
        if payment.plan:
            # Subscription payment - upgrade plan
            user.plan = PlanType(payment.plan)
            plan_details = PLAN_CONFIG[SubscriptionPlan(payment.plan)]
            user.credits = plan_details.credits
            credits_added = plan_details.credits
        else:
            # Credit purchase
            credits_to_add = payment.metadata.get("credits", 0) if payment.metadata else 0
            user.credits += credits_to_add
            credits_added = credits_to_add

    await db.commit()

    return ConfirmPaymentResponse(
        success=True,
        plan=payment.plan,
        credits=credits_added if 'credits_added' in dir() else None,
        receipt_url=result.receipt_url,
    )


@router.post("/cancel", response_model=CancelResponse)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel the current subscription.

    Subscription remains active until the end of the billing period.
    """
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

    # In production, this would:
    # 1. Cancel the recurring billing with Toss
    # 2. Set a cancellation date
    # 3. Schedule a job to downgrade at end of period

    # For now, mark for cancellation
    effective_date = datetime.utcnow() + timedelta(days=30)

    return CancelResponse(
        message="구독이 취소되었습니다. 현재 결제 기간이 끝날 때까지 모든 기능을 이용하실 수 있습니다.",
        effective_date=effective_date.isoformat() + "Z",
    )


@router.get("/history", response_model=PaymentHistoryResponse)
async def get_payment_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user's payment history."""
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .limit(50)
    )
    payments = result.scalars().all()

    items = []
    for p in payments:
        items.append(
            PaymentHistoryItem(
                id=str(p.id),
                amount=p.amount,
                plan=p.plan,
                credits=p.metadata.get("credits") if p.metadata else None,
                status=p.status.value,
                created_at=p.created_at.isoformat() if p.created_at else "",
                receipt_url=None,  # Would store receipt URL in payment record
            )
        )

    return PaymentHistoryResponse(
        items=items,
        total=len(items),
    )


@router.get("/current")
async def get_current_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user's current subscription details."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    plan = SubscriptionPlan(user.plan.value)
    plan_details = PLAN_CONFIG[plan]

    return {
        "plan": user.plan.value,
        "plan_name": plan_details.name,
        "credits": user.credits,
        "monthly_credits": plan_details.credits,
        "max_duration": plan_details.max_duration,
        "max_resolution": plan_details.max_resolution,
        "features": plan_details.features,
        "next_billing_date": None,  # Would track in user or subscription table
        "is_cancelled": False,
    }


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Toss Payments webhooks.

    Events: DONE, CANCELED, PARTIAL_CANCELED, ABORTED, EXPIRED
    """
    # Verify webhook signature (production requirement)
    # signature = request.headers.get("Toss-Signature")

    body = await request.json()
    event_type = body.get("eventType")
    data = body.get("data", {})

    payment_key = data.get("paymentKey")
    order_id = data.get("orderId")

    if not payment_key or not order_id:
        return {"status": "ignored"}

    # Find payment record
    result = await db.execute(
        select(Payment).where(Payment.transaction_id == order_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        return {"status": "payment_not_found"}

    # Handle event
    if event_type == "DONE":
        payment.status = PaymentStatus.COMPLETED
    elif event_type in ["CANCELED", "PARTIAL_CANCELED"]:
        payment.status = PaymentStatus.CANCELLED
    elif event_type in ["ABORTED", "EXPIRED"]:
        payment.status = PaymentStatus.FAILED

    await db.commit()

    return {"status": "ok"}
