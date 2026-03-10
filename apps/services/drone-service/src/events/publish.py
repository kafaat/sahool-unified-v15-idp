"""
Event Publisher - SAHOOL Drone Service
ناشر الأحداث - خدمة الطائرات المسيرة

Provides EventEnvelope wrapper and DronePublisher class
following the advisory-service pattern.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

try:
    from nats.aio.client import Client as NATS
except ImportError:
    NATS = None  # type: ignore[assignment,misc]

from .types import get_subject, get_version

logger = structlog.get_logger()

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")


class EventEnvelope:
    """Standard event envelope wrapper matching platform convention."""

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
    ) -> EventEnvelope:
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


class DronePublisher:
    """Publisher for drone service events with lifecycle management."""

    def __init__(self, nats_url: str | None = None):
        self.nats_url = nats_url or NATS_URL
        self.nc: NATS | None = None

    async def connect(self) -> None:
        """Connect to NATS server."""
        import nats as nats_lib

        self.nc = await nats_lib.connect(self.nats_url)
        logger.info("drone_publisher_connected", url=self.nats_url)

    async def close(self) -> None:
        """Close NATS connection."""
        if self.nc:
            await self.nc.close()
            logger.info("drone_publisher_closed")

    async def publish(
        self,
        event_type: str,
        tenant_id: str,
        aggregate_id: str,
        payload: dict,
        correlation_id: str | None = None,
    ) -> str:
        """Publish an event with EventEnvelope wrapper.

        Returns the event_id.
        """
        if not self.nc:
            logger.warning("publish_skipped_no_connection", event_type=event_type)
            return ""

        envelope = EventEnvelope.create(
            event_type=event_type,
            version=get_version(event_type),
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        subject = get_subject(event_type)

        # Derive the action from the full subject (e.g., "registered" from "sahool.drone.registered")
        tenant_action = subject.rsplit(".", 1)[-1]

        try:
            data = json.dumps(envelope.to_dict()).encode()
            await self.nc.publish(subject, data)

            # Also publish tenant-scoped subject using action suffix
            tenant_subject = _get_tenant_subject(tenant_id, tenant_action)
            await self.nc.publish(tenant_subject, data)

            logger.info(
                "event_published",
                event_id=envelope.event_id,
                subject=subject,
                event_type=event_type,
                tenant_id=tenant_id,
            )
            return envelope.event_id
        except Exception as e:
            logger.warning("event_publish_failed", subject=subject, error=str(e))
            return ""

    async def publish_drone_registered(
        self,
        tenant_id: str,
        drone_id: str,
        model: str,
        correlation_id: str | None = None,
    ) -> str:
        from .types import DRONE_REGISTERED

        return await self.publish(
            DRONE_REGISTERED,
            tenant_id,
            drone_id,
            {"drone_id": drone_id, "model": model},
            correlation_id,
        )

    async def publish_flight_planned(
        self,
        tenant_id: str,
        plan_id: str,
        plan_type: str,
        field_id: str,
        correlation_id: str | None = None,
    ) -> str:
        from .types import FLIGHT_PLANNED

        return await self.publish(
            FLIGHT_PLANNED,
            tenant_id,
            plan_id,
            {"plan_id": plan_id, "plan_type": plan_type, "field_id": field_id},
            correlation_id,
        )

    async def publish_mission_event(
        self,
        event_type: str,
        tenant_id: str,
        mission_id: str,
        drone_id: str | None = None,
        correlation_id: str | None = None,
    ) -> str:
        payload: dict[str, Any] = {"mission_id": mission_id}
        if drone_id:
            payload["drone_id"] = drone_id
        return await self.publish(
            event_type,
            tenant_id,
            mission_id,
            payload,
            correlation_id,
        )

    async def publish_prescription_created(
        self,
        tenant_id: str,
        prescription_id: str,
        field_id: str,
        prescription_type: str = "ndvi",
        correlation_id: str | None = None,
    ) -> str:
        from .types import VRA_PRESCRIPTION_CREATED

        return await self.publish(
            VRA_PRESCRIPTION_CREATED,
            tenant_id,
            prescription_id,
            {"prescription_id": prescription_id, "field_id": field_id, "type": prescription_type},
            correlation_id,
        )


def _get_tenant_subject(tenant_id: str, event_type: str) -> str:
    """Build tenant-scoped NATS subject."""
    try:
        from shared.events.subjects import get_tenant_subject

        action = event_type.replace("_", ".")
        return get_tenant_subject(tenant_id, "drone", action)
    except ImportError:
        return f"sahool.tenant.{tenant_id}.drone.{event_type}"


# ─────────────────────────────────────────────────────────────────────────────
# Backward-compatible helper functions
# ─────────────────────────────────────────────────────────────────────────────


async def publish_event(
    nc,
    subject: str,
    payload: dict[str, Any],
    tenant_id: str | None = None,
) -> None:
    """Publish a NATS event (simple helper for backward compatibility)."""
    if not nc:
        return
    if tenant_id:
        payload["tenant_id"] = tenant_id
    try:
        await nc.publish(subject, json.dumps(payload).encode())
        logger.info("event_published", subject=subject, tenant_id=tenant_id)
    except Exception as e:
        logger.warning("event_publish_failed", subject=subject, error=str(e))


async def publish_drone_event(
    nc,
    event: str,
    tenant_id: str,
    **kwargs: Any,
) -> None:
    """Publish drone event (backward-compatible helper)."""
    payload = {"tenant_id": tenant_id, **kwargs}
    await publish_event(nc, event, payload, tenant_id)
    action = event.split(".")[-1]
    tenant_subject = _get_tenant_subject(tenant_id, action)
    await publish_event(nc, tenant_subject, payload)


async def subscribe_cross_service_events(nc, app_state) -> None:
    """Subscribe to events from related services for integration."""
    if not nc:
        return

    from .types import (
        VISION_DISEASE_DETECTED,
        VISION_PEST_DETECTED,
        VISION_WEED_DETECTED,
        WEATHER_ALERT,
    )

    async def on_vision_detection(msg):
        """Handle pest/disease/weed detection -> auto-create spot spray mission."""
        try:
            data = json.loads(msg.data.decode())
            logger.info(
                "vision_detection_received",
                subject=msg.subject,
                field_id=data.get("field_id"),
                detection_type=data.get("detection_type"),
            )
            if hasattr(app_state, "pending_detections"):
                app_state.pending_detections.append(data)
        except Exception as e:
            logger.warning("vision_event_handler_failed", error=str(e))

    async def on_weather_alert(msg):
        """Handle weather alerts -> ground drones if unsafe."""
        try:
            data = json.loads(msg.data.decode())
            logger.info("weather_alert_received", alert_type=data.get("alert_type"))
        except Exception as e:
            logger.warning("weather_event_handler_failed", error=str(e))

    try:
        await nc.subscribe(VISION_PEST_DETECTED, cb=on_vision_detection)
        await nc.subscribe(VISION_DISEASE_DETECTED, cb=on_vision_detection)
        await nc.subscribe(VISION_WEED_DETECTED, cb=on_vision_detection)
        await nc.subscribe(WEATHER_ALERT, cb=on_weather_alert)
        logger.info("cross_service_event_subscriptions_active")
    except Exception as e:
        logger.warning("cross_service_subscription_failed", error=str(e))
