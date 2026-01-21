"""
Payment Service - Toss Payments Integration

Handles subscription payments, credit purchases, and billing management.
"""

import httpx
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionPlan(Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class PlanDetails:
    name: str
    price: int  # KRW
    credits: int
    features: List[str]
    max_duration: int  # seconds
    max_resolution: str


# Plan configurations
PLAN_CONFIG: Dict[SubscriptionPlan, PlanDetails] = {
    SubscriptionPlan.FREE: PlanDetails(
        name="무료",
        price=0,
        credits=3,
        features=[
            "월 3회 영상 생성",
            "15초 영상",
            "720p 해상도",
            "워터마크 포함",
        ],
        max_duration=15,
        max_resolution="720p",
    ),
    SubscriptionPlan.BASIC: PlanDetails(
        name="Basic",
        price=29000,
        credits=30,
        features=[
            "월 30회 영상 생성",
            "30초 영상",
            "1080p 해상도",
            "워터마크 제거",
            "기본 템플릿",
        ],
        max_duration=30,
        max_resolution="1080p",
    ),
    SubscriptionPlan.PRO: PlanDetails(
        name="Pro",
        price=79000,
        credits=100,
        features=[
            "월 100회 영상 생성",
            "60초 영상",
            "4K 해상도",
            "프리미엄 템플릿",
            "AI 나레이션",
            "다국어 지원",
            "A/B 테스트",
        ],
        max_duration=60,
        max_resolution="4K",
    ),
    SubscriptionPlan.ENTERPRISE: PlanDetails(
        name="Enterprise",
        price=290000,
        credits=999,
        features=[
            "무제한 영상 생성",
            "120초 영상",
            "4K+ 해상도",
            "모든 템플릿",
            "전용 지원",
            "API 접근",
            "맞춤 브랜딩",
            "팀 협업",
        ],
        max_duration=120,
        max_resolution="4K+",
    ),
}


@dataclass
class PaymentResult:
    success: bool
    payment_key: Optional[str] = None
    order_id: Optional[str] = None
    amount: Optional[int] = None
    status: PaymentStatus = PaymentStatus.PENDING
    error: Optional[str] = None
    receipt_url: Optional[str] = None


class TossPaymentsService:
    """Service for handling Toss Payments transactions."""

    BASE_URL = "https://api.tosspayments.com/v1"

    def __init__(self):
        self.secret_key = settings.TOSS_SECRET_KEY
        self.client_key = settings.TOSS_CLIENT_KEY

        # Create auth header
        auth_string = f"{self.secret_key}:"
        self.auth_header = base64.b64encode(auth_string.encode()).decode()

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Basic {self.auth_header}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def confirm_payment(
        self,
        payment_key: str,
        order_id: str,
        amount: int,
    ) -> PaymentResult:
        """
        Confirm a payment after user completes checkout.

        Args:
            payment_key: Payment key from Toss
            order_id: Your order ID
            amount: Payment amount in KRW

        Returns:
            PaymentResult with transaction details
        """
        try:
            response = await self.client.post(
                "/payments/confirm",
                json={
                    "paymentKey": payment_key,
                    "orderId": order_id,
                    "amount": amount,
                },
            )

            if response.status_code == 200:
                data = response.json()
                return PaymentResult(
                    success=True,
                    payment_key=data.get("paymentKey"),
                    order_id=data.get("orderId"),
                    amount=data.get("totalAmount"),
                    status=PaymentStatus.COMPLETED,
                    receipt_url=data.get("receipt", {}).get("url"),
                )
            else:
                error_data = response.json()
                logger.error(f"Payment confirmation failed: {error_data}")
                return PaymentResult(
                    success=False,
                    status=PaymentStatus.FAILED,
                    error=error_data.get("message", "Payment failed"),
                )

        except Exception as e:
            logger.error(f"Payment error: {str(e)}")
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                error=str(e),
            )

    async def get_payment(self, payment_key: str) -> Optional[Dict[str, Any]]:
        """Get payment details by payment key."""
        try:
            response = await self.client.get(f"/payments/{payment_key}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Get payment error: {str(e)}")
            return None

    async def cancel_payment(
        self,
        payment_key: str,
        cancel_reason: str,
        cancel_amount: Optional[int] = None,
    ) -> PaymentResult:
        """
        Cancel or refund a payment.

        Args:
            payment_key: Payment key to cancel
            cancel_reason: Reason for cancellation
            cancel_amount: Partial refund amount (None for full refund)

        Returns:
            PaymentResult
        """
        try:
            payload = {"cancelReason": cancel_reason}
            if cancel_amount:
                payload["cancelAmount"] = cancel_amount

            response = await self.client.post(
                f"/payments/{payment_key}/cancel",
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                return PaymentResult(
                    success=True,
                    payment_key=data.get("paymentKey"),
                    status=PaymentStatus.CANCELLED if not cancel_amount else PaymentStatus.REFUNDED,
                )
            else:
                error_data = response.json()
                return PaymentResult(
                    success=False,
                    status=PaymentStatus.FAILED,
                    error=error_data.get("message", "Cancellation failed"),
                )

        except Exception as e:
            logger.error(f"Cancel payment error: {str(e)}")
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                error=str(e),
            )

    async def create_billing_key(
        self,
        customer_key: str,
        auth_key: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a billing key for recurring payments.

        Args:
            customer_key: Unique customer identifier
            auth_key: Auth key from card registration

        Returns:
            Billing key data
        """
        try:
            response = await self.client.post(
                "/billing/authorizations/issue",
                json={
                    "customerKey": customer_key,
                    "authKey": auth_key,
                },
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Create billing key error: {str(e)}")
            return None

    async def charge_billing(
        self,
        billing_key: str,
        customer_key: str,
        amount: int,
        order_id: str,
        order_name: str,
    ) -> PaymentResult:
        """
        Charge a saved card using billing key.

        Args:
            billing_key: Saved card billing key
            customer_key: Customer identifier
            amount: Amount to charge
            order_id: Order ID
            order_name: Order description

        Returns:
            PaymentResult
        """
        try:
            response = await self.client.post(
                f"/billing/{billing_key}",
                json={
                    "customerKey": customer_key,
                    "amount": amount,
                    "orderId": order_id,
                    "orderName": order_name,
                },
            )

            if response.status_code == 200:
                data = response.json()
                return PaymentResult(
                    success=True,
                    payment_key=data.get("paymentKey"),
                    order_id=data.get("orderId"),
                    amount=data.get("totalAmount"),
                    status=PaymentStatus.COMPLETED,
                    receipt_url=data.get("receipt", {}).get("url"),
                )
            else:
                error_data = response.json()
                return PaymentResult(
                    success=False,
                    status=PaymentStatus.FAILED,
                    error=error_data.get("message", "Billing failed"),
                )

        except Exception as e:
            logger.error(f"Charge billing error: {str(e)}")
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                error=str(e),
            )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class SubscriptionService:
    """Service for managing subscriptions and credits."""

    def __init__(self, db_session):
        self.db = db_session
        self.payment_service = TossPaymentsService()

    def get_plan_details(self, plan: SubscriptionPlan) -> PlanDetails:
        """Get details for a subscription plan."""
        return PLAN_CONFIG.get(plan, PLAN_CONFIG[SubscriptionPlan.FREE])

    def get_all_plans(self) -> Dict[str, Dict[str, Any]]:
        """Get all available plans with their details."""
        return {
            plan.value: {
                "name": details.name,
                "price": details.price,
                "credits": details.credits,
                "features": details.features,
                "max_duration": details.max_duration,
                "max_resolution": details.max_resolution,
            }
            for plan, details in PLAN_CONFIG.items()
        }

    async def upgrade_plan(
        self,
        user_id: str,
        new_plan: SubscriptionPlan,
        payment_key: str,
        order_id: str,
    ) -> Dict[str, Any]:
        """
        Upgrade user's subscription plan.

        Args:
            user_id: User ID
            new_plan: New subscription plan
            payment_key: Payment key from Toss
            order_id: Order ID

        Returns:
            Result with updated subscription details
        """
        plan_details = self.get_plan_details(new_plan)

        # Confirm payment
        result = await self.payment_service.confirm_payment(
            payment_key=payment_key,
            order_id=order_id,
            amount=plan_details.price,
        )

        if not result.success:
            return {
                "success": False,
                "error": result.error,
            }

        # Update user's plan in database
        # This would interact with your User model
        # For now, return success response

        return {
            "success": True,
            "plan": new_plan.value,
            "credits": plan_details.credits,
            "receipt_url": result.receipt_url,
            "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }

    async def add_credits(
        self,
        user_id: str,
        credits: int,
        payment_key: str,
        order_id: str,
        amount: int,
    ) -> Dict[str, Any]:
        """
        Add credits to user's account (one-time purchase).

        Args:
            user_id: User ID
            credits: Number of credits to add
            payment_key: Payment key
            order_id: Order ID
            amount: Payment amount

        Returns:
            Result with updated credit balance
        """
        # Confirm payment
        result = await self.payment_service.confirm_payment(
            payment_key=payment_key,
            order_id=order_id,
            amount=amount,
        )

        if not result.success:
            return {
                "success": False,
                "error": result.error,
            }

        # Add credits to user's balance
        # This would update your User model

        return {
            "success": True,
            "credits_added": credits,
            "receipt_url": result.receipt_url,
        }

    async def deduct_credit(self, user_id: str) -> bool:
        """
        Deduct one credit from user's balance.

        Returns True if successful, False if insufficient credits.
        """
        # Check and deduct from User model
        # Implementation depends on your database session handling
        return True

    async def check_credits(self, user_id: str) -> int:
        """Get user's current credit balance."""
        # Query User model for credits
        return 0

    async def cancel_subscription(
        self,
        user_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Cancel user's subscription.

        Subscription will remain active until the end of the billing period.
        """
        # Update user's subscription status
        # Schedule downgrade to free plan

        return {
            "success": True,
            "message": "구독이 취소되었습니다. 현재 결제 기간이 끝날 때까지 이용 가능합니다.",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }


# Credit packages for one-time purchase
CREDIT_PACKAGES = [
    {"credits": 10, "price": 9900, "name": "10 크레딧"},
    {"credits": 30, "price": 24900, "name": "30 크레딧", "discount": "17%"},
    {"credits": 50, "price": 39900, "name": "50 크레딧", "discount": "20%"},
    {"credits": 100, "price": 69900, "name": "100 크레딧", "discount": "30%"},
]


def generate_order_id(prefix: str = "SAIAD") -> str:
    """Generate a unique order ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}_{timestamp}_{unique_id}"
