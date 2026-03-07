"""
NATS event publishing for drone service - نشر أحداث NATS لخدمة الطائرات
Integrates with shared.events.subjects for standardized event subjects.
"""

from __future__ import annotations

import json
from typing import Any

import structlog

logger = structlog.get_logger()

# ─────────────────────────────────────────────────────────────────────────────
# Event subjects - موضوعات الأحداث
# ─────────────────────────────────────────────────────────────────────────────

# Drone lifecycle events
DRONE_REGISTERED = "sahool.drone.registered"
DRONE_UPDATED = "sahool.drone.updated"
DRONE_DEREGISTERED = "sahool.drone.deregistered"
DRONE_STATUS_CHANGED = "sahool.drone.status_changed"

# Flight planning events
FLIGHT_PLANNED = "sahool.drone.flight_planned"
FLIGHT_WEATHER_CHECKED = "sahool.drone.weather_checked"

# Mission lifecycle events
MISSION_CREATED = "sahool.drone.mission_created"
MISSION_STARTED = "sahool.drone.mission_started"
MISSION_PAUSED = "sahool.drone.mission_paused"
MISSION_RESUMED = "sahool.drone.mission_resumed"
MISSION_COMPLETED = "sahool.drone.mission_completed"
MISSION_ABORTED = "sahool.drone.mission_aborted"

# VRA events
VRA_PRESCRIPTION_CREATED = "sahool.drone.vra_prescription_created"
VRA_SPOT_SPRAY_CREATED = "sahool.drone.vra_spot_spray_created"

# Cross-service integration events (consumed)
VISION_PEST_DETECTED = "sahool.vision.pest_detected"
VISION_DISEASE_DETECTED = "sahool.vision.disease_detected"
VISION_WEED_DETECTED = "sahool.vision.weed_detected"
FIELD_UPDATED = "sahool.field.updated"
WEATHER_ALERT = "sahool.weather.alert"


def _get_tenant_subject(tenant_id: str, domain: str, action: str) -> str:
    """Build tenant-scoped NATS subject."""
    try:
        from shared.events.subjects import get_tenant_subject
        return get_tenant_subject(tenant_id, domain, action)
    except ImportError:
        return f"sahool.tenant.{tenant_id}.{domain}.{action}"


async def publish_event(
    nc, subject: str, payload: dict[str, Any], tenant_id: str | None = None
) -> None:
    """Publish a NATS event with optional tenant scoping."""
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
    nc, event: str, tenant_id: str, **kwargs: Any
) -> None:
    """Publish drone-scoped event with tenant isolation."""
    payload = {"tenant_id": tenant_id, **kwargs}
    await publish_event(nc, event, payload, tenant_id)

    # Also publish tenant-scoped subject for isolated streams
    action = event.split(".")[-1]
    tenant_subject = _get_tenant_subject(tenant_id, "drone", action)
    await publish_event(nc, tenant_subject, payload)


async def subscribe_cross_service_events(nc, app_state) -> None:
    """Subscribe to events from related services for integration."""
    if not nc:
        return

    async def on_vision_detection(msg):
        """Handle pest/disease/weed detection → auto-create spot spray mission."""
        try:
            data = json.loads(msg.data.decode())
            logger.info(
                "vision_detection_received",
                subject=msg.subject,
                field_id=data.get("field_id"),
                detection_type=data.get("detection_type"),
            )
            # Store for potential auto-spray mission creation
            if hasattr(app_state, "pending_detections"):
                app_state.pending_detections.append(data)
        except Exception as e:
            logger.warning("vision_event_handler_failed", error=str(e))

    async def on_weather_alert(msg):
        """Handle weather alerts → ground drones if unsafe."""
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
