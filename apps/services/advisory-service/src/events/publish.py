"""
Event Publisher - SAHOOL Agro Advisor
Publish events to NATS JetStream
"""

import json
import os
import uuid
from datetime import UTC, datetime

import structlog

try:
    from nats.aio.client import Client as NATS
except ImportError:
    NATS = None  # Optional: not available in test environments

from .types import get_subject, get_version

logger = structlog.get_logger(__name__)

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")


class EventEnvelope:
    """Standard event envelope wrapper"""

    def __init__(
        self,
        event_id: str,
        event_type: str,
        version: int,
        aggregate_id: str,
        tenant_id: str,
        correlation_id: str,
        timestamp: str,
        payload: dict,
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.version = version
        self.aggregate_id = aggregate_id
        self.tenant_id = tenant_id
        self.correlation_id = correlation_id
        self.timestamp = timestamp
        self.payload = payload

    @classmethod
    def create(
        cls,
        event_type: str,
        version: int,
        aggregate_id: str,
        tenant_id: str,
        correlation_id: str,
        payload: dict,
    ) -> "EventEnvelope":
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            version=version,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC).isoformat(),
            payload=payload,
        )

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "version": self.version,
            "aggregate_id": self.aggregate_id,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class AdvisorPublisher:
    """Publisher for Agro Advisor events"""

    def __init__(self, nats_url: str = None):
        self.nats_url = nats_url or NATS_URL
        self.nc = None
        self._connected = False
        self._nats_unavailable = False

    async def connect(self):
        """Connect to NATS server"""
        if self._connected:
            return

        if self._nats_unavailable:
            return

        if NATS is None:
            logger.warning("nats-py not installed, event publishing disabled")
            self._nats_unavailable = True
            return

        self.nc = NATS()
        try:
            await self.nc.connect(self.nats_url)
            self._connected = True
            logger.info("nats_connected", url=self.nats_url)
        except Exception as e:
            logger.error("nats_connection_failed", url=self.nats_url, error=str(e))
            raise

    async def close(self):
        """Close NATS connection"""
        if self.nc and self._connected:
            await self.nc.close()
            self._connected = False
            logger.info("nats_disconnected")

    async def publish(
        self,
        event_type: str,
        tenant_id: str,
        aggregate_id: str,
        payload: dict,
        correlation_id: str = None,
        subject: str = None,
    ) -> str:
        """
        Publish an event to NATS

        Args:
            event_type: Type of event (e.g., 'recommendation_issued')
            tenant_id: Tenant ID
            aggregate_id: Aggregate ID (usually field_id)
            payload: Event payload
            correlation_id: Optional correlation ID
            subject: Optional custom subject

        Returns:
            Event ID
        """
        if not self._connected:
            await self.connect()

        if self.nc is None:
            logger.debug("NATS unavailable, skipping event publish", event_type=event_type)
            return str(uuid.uuid4())

        version = get_version(event_type)
        # Use tenant-scoped subject for multi-tenant data isolation
        # استخدام موضوع مخصص للمستأجر لعزل بيانات المستأجرين
        target_subject = subject or get_subject(event_type, tenant_id)

        envelope = EventEnvelope.create(
            event_type=event_type,
            version=version,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        message = json.dumps(envelope.to_dict(), default=str).encode()
        try:
            await self.nc.publish(target_subject, message)
        except Exception as e:
            logger.error(
                "nats_publish_failed",
                subject=target_subject,
                event_type=event_type,
                event_id=envelope.event_id,
                error=str(e),
            )
            raise

        logger.info(
            "nats_event_published",
            subject=target_subject,
            event_type=event_type,
            event_id=envelope.event_id,
        )
        return envelope.event_id

    async def publish_recommendation(
        self,
        tenant_id: str,
        field_id: str,
        category: str,
        severity: str,
        title_ar: str,
        title_en: str,
        actions: list[str],
        confidence: float,
        correlation_id: str = None,
        details: dict = None,
    ) -> str:
        """Publish a recommendation event"""
        payload = {
            "field_id": field_id,
            "category": category,
            "severity": severity,
            "title_ar": title_ar,
            "title_en": title_en,
            "actions": actions,
            "confidence": confidence,
            "details": details or {},
        }

        return await self.publish(
            event_type="recommendation_issued",
            tenant_id=tenant_id,
            aggregate_id=field_id,
            payload=payload,
            correlation_id=correlation_id,
        )

    async def publish_fertilizer_plan(
        self,
        tenant_id: str,
        field_id: str,
        crop: str,
        stage: str,
        plan: list[dict],
        correlation_id: str = None,
        notes: list[str] = None,
    ) -> str:
        """Publish a fertilizer plan event"""
        payload = {
            "field_id": field_id,
            "crop": crop,
            "stage": stage,
            "plan": plan,
            "notes": notes or [],
        }

        return await self.publish(
            event_type="fertilizer_plan_issued",
            tenant_id=tenant_id,
            aggregate_id=field_id,
            payload=payload,
            correlation_id=correlation_id,
        )

    async def publish_nutrient_assessment(
        self,
        tenant_id: str,
        field_id: str,
        deficiency_id: str,
        nutrient: str,
        severity: str,
        title_ar: str,
        title_en: str,
        corrections: list[dict],
        confidence: float,
        correlation_id: str = None,
    ) -> str:
        """Publish a nutrient assessment event"""
        payload = {
            "field_id": field_id,
            "deficiency_id": deficiency_id,
            "nutrient": nutrient,
            "severity": severity,
            "title_ar": title_ar,
            "title_en": title_en,
            "corrections": corrections,
            "confidence": confidence,
        }

        return await self.publish(
            event_type="nutrient_assessment_issued",
            tenant_id=tenant_id,
            aggregate_id=field_id,
            payload=payload,
            correlation_id=correlation_id,
        )


# Singleton instance
_publisher: AdvisorPublisher | None = None


async def get_publisher() -> AdvisorPublisher:
    """Get or create publisher singleton"""
    global _publisher
    if _publisher is None:
        _publisher = AdvisorPublisher()
        try:
            await _publisher.connect()
        except Exception as e:
            logger.warning("Failed to connect to NATS: %s", e)
    return _publisher
