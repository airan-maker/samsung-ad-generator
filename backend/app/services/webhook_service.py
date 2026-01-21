"""
Webhook Notification Service

Sends webhook notifications for various events.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import hmac
import hashlib
import json
import logging
import httpx

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    # Video events
    VIDEO_GENERATION_STARTED = "video.generation.started"
    VIDEO_GENERATION_PROGRESS = "video.generation.progress"
    VIDEO_GENERATION_COMPLETED = "video.generation.completed"
    VIDEO_GENERATION_FAILED = "video.generation.failed"

    # Project events
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"

    # Export events
    EXPORT_COMPLETED = "export.completed"
    EXPORT_FAILED = "export.failed"

    # Payment events
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"

    # A/B Test events
    AB_TEST_COMPLETED = "ab_test.completed"

    # Social media events
    SOCIAL_POST_PUBLISHED = "social.post.published"
    SOCIAL_POST_FAILED = "social.post.failed"


@dataclass
class WebhookEndpoint:
    endpoint_id: str
    user_id: str
    url: str
    secret: str
    events: List[WebhookEvent]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered_at: Optional[datetime] = None
    failure_count: int = 0


@dataclass
class WebhookDelivery:
    delivery_id: str
    endpoint_id: str
    event: WebhookEvent
    payload: Dict[str, Any]
    status: str  # pending, success, failed
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    attempts: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None


class WebhookService:
    """
    Service for managing webhook endpoints and delivering notifications.
    """

    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 300, 900]  # 1 min, 5 min, 15 min

    def __init__(self):
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.deliveries: List[WebhookDelivery] = []
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def register_endpoint(
        self,
        user_id: str,
        url: str,
        events: List[WebhookEvent],
        secret: Optional[str] = None,
    ) -> WebhookEndpoint:
        """
        Register a new webhook endpoint.
        """
        import uuid

        endpoint_id = str(uuid.uuid4())

        # Generate secret if not provided
        if not secret:
            secret = hashlib.sha256(
                f"{endpoint_id}{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:32]

        endpoint = WebhookEndpoint(
            endpoint_id=endpoint_id,
            user_id=user_id,
            url=url,
            secret=secret,
            events=events,
        )

        self.endpoints[endpoint_id] = endpoint

        logger.info(f"Registered webhook endpoint {endpoint_id} for user {user_id}")
        return endpoint

    async def update_endpoint(
        self,
        endpoint_id: str,
        user_id: str,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[WebhookEndpoint]:
        """
        Update a webhook endpoint.
        """
        endpoint = self.endpoints.get(endpoint_id)

        if not endpoint or endpoint.user_id != user_id:
            return None

        if url is not None:
            endpoint.url = url
        if events is not None:
            endpoint.events = events
        if is_active is not None:
            endpoint.is_active = is_active

        return endpoint

    async def delete_endpoint(
        self,
        endpoint_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a webhook endpoint.
        """
        endpoint = self.endpoints.get(endpoint_id)

        if not endpoint or endpoint.user_id != user_id:
            return False

        del self.endpoints[endpoint_id]
        logger.info(f"Deleted webhook endpoint {endpoint_id}")
        return True

    def get_endpoints(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all webhook endpoints for a user.
        """
        return [
            {
                "endpoint_id": ep.endpoint_id,
                "url": ep.url,
                "events": [e.value for e in ep.events],
                "is_active": ep.is_active,
                "created_at": ep.created_at.isoformat(),
                "last_triggered_at": ep.last_triggered_at.isoformat() if ep.last_triggered_at else None,
                "failure_count": ep.failure_count,
            }
            for ep in self.endpoints.values()
            if ep.user_id == user_id
        ]

    async def trigger_event(
        self,
        user_id: str,
        event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> List[str]:
        """
        Trigger a webhook event for all matching endpoints.
        """
        delivery_ids = []

        # Find all endpoints subscribed to this event
        for endpoint in self.endpoints.values():
            if (
                endpoint.user_id == user_id
                and endpoint.is_active
                and event in endpoint.events
            ):
                delivery_id = await self._deliver_webhook(endpoint, event, payload)
                delivery_ids.append(delivery_id)

        return delivery_ids

    async def _deliver_webhook(
        self,
        endpoint: WebhookEndpoint,
        event: WebhookEvent,
        payload: Dict[str, Any],
    ) -> str:
        """
        Deliver a webhook to an endpoint.
        """
        import uuid

        delivery_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Build webhook payload
        webhook_payload = {
            "id": delivery_id,
            "event": event.value,
            "created_at": timestamp.isoformat() + "Z",
            "data": payload,
        }

        # Generate signature
        signature = self._generate_signature(endpoint.secret, webhook_payload)

        # Create delivery record
        delivery = WebhookDelivery(
            delivery_id=delivery_id,
            endpoint_id=endpoint.endpoint_id,
            event=event,
            payload=webhook_payload,
            status="pending",
        )
        self.deliveries.append(delivery)

        # Attempt delivery
        await self._attempt_delivery(delivery, endpoint, signature)

        return delivery_id

    async def _attempt_delivery(
        self,
        delivery: WebhookDelivery,
        endpoint: WebhookEndpoint,
        signature: str,
    ):
        """
        Attempt to deliver a webhook with retries.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Id": delivery.delivery_id,
            "X-Webhook-Event": delivery.event.value,
            "User-Agent": "SaiAd-Webhook/1.0",
        }

        for attempt in range(self.MAX_RETRIES):
            delivery.attempts = attempt + 1

            try:
                response = await self.http_client.post(
                    endpoint.url,
                    json=delivery.payload,
                    headers=headers,
                )

                delivery.response_code = response.status_code
                delivery.response_body = response.text[:1000]  # Limit response body

                if 200 <= response.status_code < 300:
                    delivery.status = "success"
                    delivery.delivered_at = datetime.utcnow()
                    endpoint.last_triggered_at = datetime.utcnow()
                    endpoint.failure_count = 0

                    logger.info(
                        f"Webhook delivered successfully: {delivery.delivery_id} "
                        f"to {endpoint.url}"
                    )
                    return
                else:
                    logger.warning(
                        f"Webhook delivery failed with status {response.status_code}: "
                        f"{delivery.delivery_id}"
                    )

            except Exception as e:
                logger.error(f"Webhook delivery error: {e}")
                delivery.response_body = str(e)

            # Wait before retry
            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(self.RETRY_DELAYS[attempt])

        # All retries failed
        delivery.status = "failed"
        endpoint.failure_count += 1

        # Disable endpoint after too many failures
        if endpoint.failure_count >= 10:
            endpoint.is_active = False
            logger.warning(
                f"Disabled webhook endpoint {endpoint.endpoint_id} "
                f"due to repeated failures"
            )

    def _generate_signature(
        self,
        secret: str,
        payload: Dict[str, Any],
    ) -> str:
        """
        Generate HMAC signature for webhook payload.
        """
        payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()
        return f"sha256={signature}"

    @staticmethod
    def verify_signature(
        secret: str,
        payload: str,
        signature: str,
    ) -> bool:
        """
        Verify a webhook signature.
        """
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        expected = f"sha256={expected_signature}"
        return hmac.compare_digest(signature, expected)

    def get_delivery_history(
        self,
        user_id: str,
        endpoint_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get webhook delivery history.
        """
        # Filter by user's endpoints
        user_endpoint_ids = {
            ep.endpoint_id for ep in self.endpoints.values()
            if ep.user_id == user_id
        }

        deliveries = [
            d for d in self.deliveries
            if d.endpoint_id in user_endpoint_ids
            and (endpoint_id is None or d.endpoint_id == endpoint_id)
        ]

        # Sort by created_at descending
        deliveries.sort(key=lambda d: d.created_at, reverse=True)

        return [
            {
                "delivery_id": d.delivery_id,
                "endpoint_id": d.endpoint_id,
                "event": d.event.value,
                "status": d.status,
                "response_code": d.response_code,
                "attempts": d.attempts,
                "created_at": d.created_at.isoformat(),
                "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
            }
            for d in deliveries[:limit]
        ]

    async def test_endpoint(
        self,
        endpoint_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Send a test webhook to an endpoint.
        """
        endpoint = self.endpoints.get(endpoint_id)

        if not endpoint or endpoint.user_id != user_id:
            return {"success": False, "error": "Endpoint not found"}

        test_payload = {
            "test": True,
            "message": "This is a test webhook from SaiAd",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        delivery_id = await self._deliver_webhook(
            endpoint,
            WebhookEvent.VIDEO_GENERATION_COMPLETED,
            test_payload,
        )

        # Get delivery result
        delivery = next(
            (d for d in self.deliveries if d.delivery_id == delivery_id),
            None,
        )

        if delivery:
            return {
                "success": delivery.status == "success",
                "delivery_id": delivery_id,
                "status": delivery.status,
                "response_code": delivery.response_code,
            }

        return {"success": False, "error": "Delivery not found"}


# Convenience functions for common events
async def notify_video_started(
    webhook_service: WebhookService,
    user_id: str,
    project_id: str,
    video_id: str,
):
    """Notify when video generation starts."""
    await webhook_service.trigger_event(
        user_id=user_id,
        event=WebhookEvent.VIDEO_GENERATION_STARTED,
        payload={
            "project_id": project_id,
            "video_id": video_id,
        },
    )


async def notify_video_progress(
    webhook_service: WebhookService,
    user_id: str,
    project_id: str,
    video_id: str,
    progress: int,
    current_step: str,
):
    """Notify video generation progress."""
    await webhook_service.trigger_event(
        user_id=user_id,
        event=WebhookEvent.VIDEO_GENERATION_PROGRESS,
        payload={
            "project_id": project_id,
            "video_id": video_id,
            "progress": progress,
            "current_step": current_step,
        },
    )


async def notify_video_completed(
    webhook_service: WebhookService,
    user_id: str,
    project_id: str,
    video_id: str,
    video_url: str,
    thumbnail_url: str,
):
    """Notify when video generation completes."""
    await webhook_service.trigger_event(
        user_id=user_id,
        event=WebhookEvent.VIDEO_GENERATION_COMPLETED,
        payload={
            "project_id": project_id,
            "video_id": video_id,
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
        },
    )


async def notify_video_failed(
    webhook_service: WebhookService,
    user_id: str,
    project_id: str,
    video_id: str,
    error: str,
):
    """Notify when video generation fails."""
    await webhook_service.trigger_event(
        user_id=user_id,
        event=WebhookEvent.VIDEO_GENERATION_FAILED,
        payload={
            "project_id": project_id,
            "video_id": video_id,
            "error": error,
        },
    )


# Global instance
webhook_service = WebhookService()
