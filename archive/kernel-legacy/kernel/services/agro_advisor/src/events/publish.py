"""
Event Publisher - SAHOOL Agro Advisor
Publish events to NATS JetStream
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from nats.aio.client import Client as NATS

from .types import get_subject, get_version

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
            timestamp=datetime.now(timezone.utc).isoformat(),
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
        self.nc: Optional[NATS] = None
        self._connected = False

    async def connect(self):
        """Connect to NATS server"""
        if self._connected:
            return

        self.nc = NATS()
        try:
            await self.nc.connect(self.nats_url)
            self._connected = True
            print(f"📡 Connected to NATS: {self.nats_url}")
        except Exception as e:
            print(f"❌ Failed to connect to NATS: {e}")
            raise

    async def close(self):
        """Close NATS connection"""
        if self.nc and self._connected:
            await self.nc.close()
            self._connected = False
            print("📴 Disconnected from NATS")

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

        version = get_version(event_type)
        target_subject = subject or get_subject(event_type)

        envelope = EventEnvelope.create(
            event_type=event_type,
            version=version,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        message = json.dumps(envelope.to_dict(), default=str).encode()
        await self.nc.publish(target_subject, message)

        print(f"📤 Published {event_type} to {target_subject}: {envelope.event_id}")
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
_publisher: Optional[AdvisorPublisher] = None


async def get_publisher() -> AdvisorPublisher:
    """Get or create publisher singleton"""
    global _publisher
    if _publisher is None:
        _publisher = AdvisorPublisher()
        await _publisher.connect()
    return _publisher
