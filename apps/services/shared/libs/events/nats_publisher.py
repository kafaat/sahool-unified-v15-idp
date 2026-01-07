"""
SAHOOL NATS Publisher
Real-time event publishing to NATS for notification spine

Field-First Architecture:
- تحليل → NATS → notification-service → mobile
- Decoupling بين خدمات التحليل والإشعارات
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# NATS client - lazy import for optional dependency
_nats_client = None
_nats_available = False

try:
    import nats
    from nats.aio.client import Client as NATSClient

    _nats_available = True
except ImportError:
    logger.warning("NATS package not installed. NATS publishing disabled.")
    NATSClient = None


class NATSConfig(BaseModel):
    """NATS connection configuration"""

    servers: list[str] = Field(
        default_factory=lambda: [os.getenv("NATS_URL", "nats://localhost:4222")]
    )
    name: str = Field(default="sahool-publisher")
    reconnect_time_wait: int = Field(default=2)
    max_reconnect_attempts: int = Field(default=60)


class AnalysisEvent(BaseModel):
    """
    Event published when analysis is completed

    Used by analysis services to notify downstream consumers
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = Field(
        ..., description="e.g., 'ndvi.computed', 'irrigation.recommended'"
    )
    source_service: str = Field(
        ..., description="e.g., 'satellite-service', 'irrigation-smart'"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Target
    tenant_id: str | None = None
    field_id: str | None = None
    farmer_id: str | None = None

    # Payload
    data: dict[str, Any] = Field(default_factory=dict)

    # ActionTemplate (if applicable)
    action_template: dict[str, Any] | None = None

    # Notification hints
    notification_priority: str = Field(default="medium")
    notification_channels: list[str] = Field(default_factory=lambda: ["in_app"])

    def to_json(self) -> str:
        return json.dumps(
            {
                "event_id": self.event_id,
                "event_type": self.event_type,
                "source_service": self.source_service,
                "timestamp": self.timestamp.isoformat(),
                "tenant_id": self.tenant_id,
                "field_id": self.field_id,
                "farmer_id": self.farmer_id,
                "data": self.data,
                "action_template": self.action_template,
                "notification_priority": self.notification_priority,
                "notification_channels": self.notification_channels,
            }
        )


class NATSPublisher:
    """
    NATS Publisher for real-time event delivery

    Usage:
        publisher = NATSPublisher()
        await publisher.connect()
        await publisher.publish_analysis_event(event)
        await publisher.close()
    """

    def __init__(self, config: NATSConfig | None = None):
        self.config = config or NATSConfig()
        self._nc: NATSClient | None = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self._nc is not None

    async def connect(self) -> bool:
        """Connect to NATS server"""
        if not _nats_available:
            logger.warning("NATS not available. Publishing disabled.")
            return False

        try:
            self._nc = await nats.connect(
                servers=self.config.servers,
                name=self.config.name,
                reconnect_time_wait=self.config.reconnect_time_wait,
                max_reconnect_attempts=self.config.max_reconnect_attempts,
                error_cb=self._error_callback,
                disconnected_cb=self._disconnected_callback,
                reconnected_cb=self._reconnected_callback,
            )
            self._connected = True
            logger.info(f"✅ Connected to NATS: {self.config.servers}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            return False

    async def close(self):
        """Close NATS connection"""
        if self._nc:
            await self._nc.close()
            self._connected = False
            logger.info("🔌 NATS connection closed")

    async def _error_callback(self, e):
        logger.error(f"NATS error: {e}")

    async def _disconnected_callback(self):
        logger.warning("NATS disconnected")
        self._connected = False

    async def _reconnected_callback(self):
        logger.info("NATS reconnected")
        self._connected = True

    async def publish(self, subject: str, data: bytes) -> bool:
        """Publish raw data to a NATS subject"""
        if not self.is_connected:
            logger.warning(f"Not connected to NATS. Cannot publish to {subject}")
            return False

        try:
            await self._nc.publish(subject, data)
            logger.debug(f"📤 Published to {subject}: {len(data)} bytes")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to {subject}: {e}")
            return False

    async def publish_analysis_event(self, event: AnalysisEvent) -> bool:
        """
        Publish an analysis event to NATS

        Subject format: sahool.analysis.{event_type}
        """
        subject = f"sahool.analysis.{event.event_type.replace('.', '_')}"
        data = event.to_json().encode("utf-8")

        success = await self.publish(subject, data)

        if success:
            logger.info(
                f"📤 Analysis event published: {event.event_type} "
                f"field={event.field_id} priority={event.notification_priority}"
            )

        return success

    async def publish_action_event(
        self,
        action_type: str,
        field_id: str,
        action_template: dict,
        source_service: str,
        farmer_id: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        """
        Publish an action event (from ActionTemplate)

        Subject: sahool.actions.{action_type}
        """
        event = AnalysisEvent(
            event_type=f"action.{action_type}",
            source_service=source_service,
            field_id=field_id,
            farmer_id=farmer_id,
            tenant_id=tenant_id,
            action_template=action_template,
            notification_priority=action_template.get("urgency", "medium"),
            notification_channels=["push", "in_app"],
        )

        subject = f"sahool.actions.{action_type}"
        data = event.to_json().encode("utf-8")

        return await self.publish(subject, data)


# Singleton instance for convenience
_publisher_instance: NATSPublisher | None = None


async def get_publisher() -> NATSPublisher:
    """Get or create the singleton NATS publisher"""
    global _publisher_instance

    if _publisher_instance is None:
        _publisher_instance = NATSPublisher()
        await _publisher_instance.connect()

    return _publisher_instance


async def publish_analysis_completed(
    event_type: str,
    source_service: str,
    field_id: str,
    data: dict[str, Any],
    action_template: dict | None = None,
    priority: str = "medium",
    farmer_id: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """
    Convenience function to publish an analysis event

    Args:
        event_type: Event type (e.g., 'ndvi.computed', 'irrigation.recommended')
        source_service: Source service name
        field_id: Field ID
        data: Event data/payload
        action_template: Optional ActionTemplate dict
        priority: Notification priority (low, medium, high, critical)
        farmer_id: Optional farmer ID
        tenant_id: Optional tenant ID

    Returns:
        True if published successfully
    """
    publisher = await get_publisher()

    if not publisher.is_connected:
        logger.warning("NATS not connected. Falling back to sync mode.")
        return False

    event = AnalysisEvent(
        event_type=event_type,
        source_service=source_service,
        field_id=field_id,
        farmer_id=farmer_id,
        tenant_id=tenant_id,
        data=data,
        action_template=action_template,
        notification_priority=priority,
    )

    return await publisher.publish_analysis_event(event)


# Sync wrapper for non-async contexts
def publish_analysis_completed_sync(
    event_type: str,
    source_service: str,
    field_id: str,
    data: dict[str, Any],
    action_template: dict | None = None,
    priority: str = "medium",
    farmer_id: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """Sync wrapper for publish_analysis_completed"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Schedule as task if loop is already running
            asyncio.create_task(
                publish_analysis_completed(
                    event_type=event_type,
                    source_service=source_service,
                    field_id=field_id,
                    data=data,
                    action_template=action_template,
                    priority=priority,
                    farmer_id=farmer_id,
                    tenant_id=tenant_id,
                )
            )
            return True
        else:
            return loop.run_until_complete(
                publish_analysis_completed(
                    event_type=event_type,
                    source_service=source_service,
                    field_id=field_id,
                    data=data,
                    action_template=action_template,
                    priority=priority,
                    farmer_id=farmer_id,
                    tenant_id=tenant_id,
                )
            )
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        return False
