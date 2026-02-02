"""
SAHOOL Field Management Service - NATS Publisher
Publishes field-related events to NATS event bus

REFACTORED: Now uses shared EventPublisher for consistency across services
"""

import logging
from datetime import datetime, timezone, UTC
from typing import Any
from uuid import uuid4

# Use the shared EventPublisher from shared/events/
from shared.events.publisher import EventPublisher, PublisherConfig

logger = logging.getLogger(__name__)


class NatsPublisher:
    """
    NATS Event Publisher for Field Management Service

    This is an adapter that wraps the shared EventPublisher to provide
    backward-compatible API for the field-management-service.
    """

    def __init__(self, service_name: str = "field-management-service"):
        self._publisher: EventPublisher | None = None
        self._service_name = service_name
        self.connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS"""
        return self._publisher is not None and self._publisher.is_connected

    async def connect(self, nats_url: str) -> bool:
        """
        Connect to NATS server

        Args:
            nats_url: NATS server URL

        Returns:
            bool: Connection success status
        """
        try:
            config = PublisherConfig(
                servers=[nats_url],
                name=self._service_name,
            )
            self._publisher = EventPublisher(
                config=config,
                service_name=self._service_name,
            )
            success = await self._publisher.connect()
            self.connected = success
            if success:
                logger.info(f"✅ NATS connected: {nats_url}")
            return success
        except Exception as e:
            logger.error(f"❌ NATS connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from NATS server"""
        if self._publisher:
            try:
                await self._publisher.close()
                self.connected = False
                logger.info("NATS disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting from NATS: {e}")

    async def publish_event(
        self,
        subject: str,
        event_type: str,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Publish event to NATS

        Args:
            subject: NATS subject/topic
            event_type: Type of event
            payload: Event data
            metadata: Additional metadata

        Returns:
            bool: Publish success status
        """
        if not self.is_connected:
            logger.warning(f"NATS not connected, skipping event publish: {event_type}")
            return False

        try:
            # Ensure subject has sahool. prefix for security compliance
            if not subject.startswith("sahool."):
                subject = f"sahool.{subject}"

            event = {
                "eventId": str(uuid4()),
                "eventType": event_type,
                "timestamp": datetime.now(UTC).isoformat(),
                "version": "1.0",
                "sourceService": self._service_name,
                "payload": payload,
                "metadata": metadata or {},
            }

            success = await self._publisher.publish_json(subject, event)

            if success:
                logger.info(f"📤 Event published: {event_type} to {subject}")
            return success

        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            return False


# Global publisher instance
_publisher: NatsPublisher | None = None


def get_publisher() -> NatsPublisher | None:
    """Get global NATS publisher instance"""
    return _publisher


def set_publisher(publisher: NatsPublisher):
    """Set global NATS publisher instance"""
    global _publisher
    _publisher = publisher


# ============================================================================
# Field Event Publishers - Follow shared-events package patterns
# ============================================================================


async def publish_field_created(
    field_id: str,
    user_id: str,
    name: str,
    area: float,
    location: dict[str, Any],
    crop_type: str | None = None,
) -> bool:
    """
    Publish field created event

    Args:
        field_id: Field identifier
        user_id: User who created the field
        name: Field name
        area: Field area (hectares)
        location: Field location (GeoJSON polygon)
        crop_type: Type of crop (optional)

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.field.created",
        event_type="field.created",
        payload={
            "fieldId": field_id,
            "userId": user_id,
            "name": name,
            "area": area,
            "location": location,
            "cropType": crop_type,
        },
    )


async def publish_field_updated(
    field_id: str,
    user_id: str,
    changes: dict[str, Any],
) -> bool:
    """
    Publish field updated event

    Args:
        field_id: Field identifier
        user_id: User who updated the field
        changes: Dictionary of changed fields

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.field.updated",
        event_type="field.updated",
        payload={
            "fieldId": field_id,
            "userId": user_id,
            "changes": changes,
        },
    )


async def publish_field_deleted(
    field_id: str,
    user_id: str,
    deleted_at: str,
) -> bool:
    """
    Publish field deleted event

    Args:
        field_id: Field identifier
        user_id: User who deleted the field
        deleted_at: Deletion timestamp (ISO format)

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.field.deleted",
        event_type="field.deleted",
        payload={
            "fieldId": field_id,
            "userId": user_id,
            "deletedAt": deleted_at,
        },
    )


async def publish_profitability_analyzed(
    field_id: str,
    crop_season_id: str,
    crop_code: str,
    profit_margin: float,
    roi: float,
    break_even_yield: float,
    recommendations: list[str],
) -> bool:
    """
    Publish profitability analysis completed event

    Args:
        field_id: Field identifier
        crop_season_id: Crop season identifier
        crop_code: Crop code
        profit_margin: Calculated profit margin percentage
        roi: Return on investment percentage
        break_even_yield: Break-even yield in kg/ha
        recommendations: List of recommendations

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.field.profitability.analyzed",
        event_type="field.profitability.analyzed",
        payload={
            "fieldId": field_id,
            "cropSeasonId": crop_season_id,
            "cropCode": crop_code,
            "profitMargin": profit_margin,
            "roi": roi,
            "breakEvenYield": break_even_yield,
            "recommendations": recommendations,
            "analyzedAt": datetime.now(UTC).isoformat(),
        },
    )
