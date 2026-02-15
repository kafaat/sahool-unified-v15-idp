"""
NATS Event Publisher for YOLO26 Vision Service.

Publishes detection events to NATS subjects for downstream processing
by advisory, notification, and alert services.

ناشر أحداث NATS لخدمة الرؤية الحاسوبية YOLO26.
ينشر أحداث الكشف إلى مواضيع NATS للمعالجة اللاحقة.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import structlog
from fastapi import Request

logger = structlog.get_logger(__name__)

# NATS subjects matching shared/events/subjects.py
VISION_SUBJECTS = {
    "pest_detected": "sahool.vision.pest_detected",
    "disease_detected": "sahool.vision.disease_detected",
    "weed_detected": "sahool.vision.weed_detected",
    "plant_count_completed": "sahool.vision.plant_count_completed",
    "critical_alert": "sahool.vision.critical_alert",
    "analysis_started": "sahool.vision.analysis_started",
    "analysis_completed": "sahool.vision.analysis_completed",
    "analysis_failed": "sahool.vision.analysis_failed",
}

# Critical pest species that trigger critical alerts
CRITICAL_PESTS = {
    "red_palm_weevil",
    "locust",
    "desert_locust",
    "fall_armyworm",
}


async def publish_event(
    request: Request,
    subject: str,
    payload: dict[str, Any],
) -> bool:
    """
    Publish an event to NATS if connected.

    Args:
        request: FastAPI request (to access app.state.nc)
        subject: NATS subject string
        payload: Event payload dict

    Returns:
        True if published successfully, False otherwise
    """
    nc = getattr(request.app.state, "nc", None)
    if nc is None or not getattr(request.app.state, "nats_connected", False):
        logger.debug("nats_not_connected_skipping_event", subject=subject)
        return False

    try:
        data = json.dumps(payload, default=str).encode()
        await nc.publish(subject, data)
        logger.info(
            "event_published",
            subject=subject,
            event_id=payload.get("event_id", "unknown"),
        )
        return True
    except Exception as e:
        logger.warning("event_publish_failed", subject=subject, error=str(e))
        return False


async def publish_pest_detection(
    request: Request,
    detections: list[dict[str, Any]],
    *,
    model_variant: str = "m",
    processing_time_ms: float = 0,
    field_id: str | None = None,
    tenant_id: str | None = None,
) -> None:
    """
    Publish pest detection events to NATS.

    Sends individual events per detection and a critical alert
    for high-priority pests (RPW, locust).
    """
    for det in detections:
        event_id = str(uuid4())
        class_name = det.get("class_name_en", "").lower().replace(" ", "_")

        # Determine severity from confidence
        confidence = det.get("confidence", 0)
        severity = _confidence_to_severity(confidence)

        payload = {
            "event_id": event_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "source_service": "yolo26-vision-service",
            "detection_type": "pest",
            "class_name_en": det.get("class_name_en", ""),
            "class_name_ar": det.get("class_name_ar", ""),
            "confidence": confidence,
            "severity": severity,
            "model_variant": model_variant,
            "processing_time_ms": processing_time_ms,
            "bbox": det.get("bbox"),
        }

        if field_id:
            payload["field_id"] = field_id
        if tenant_id:
            payload["tenant_id"] = tenant_id

        await publish_event(request, VISION_SUBJECTS["pest_detected"], payload)

        # Critical alert for high-priority pests
        if class_name in CRITICAL_PESTS or severity == "critical":
            alert_payload = {
                **payload,
                "alert_type": "critical_pest",
                "urgency_hours": 24 if class_name != "red_palm_weevil" else 6,
            }
            await publish_event(request, VISION_SUBJECTS["critical_alert"], alert_payload)


async def publish_disease_detection(
    request: Request,
    detections: list[dict[str, Any]],
    *,
    model_variant: str = "m",
    processing_time_ms: float = 0,
    field_id: str | None = None,
    tenant_id: str | None = None,
) -> None:
    """Publish disease detection events to NATS."""
    for det in detections:
        confidence = det.get("confidence", 0)
        payload = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "source_service": "yolo26-vision-service",
            "detection_type": "disease",
            "class_name_en": det.get("class_name_en", ""),
            "class_name_ar": det.get("class_name_ar", ""),
            "confidence": confidence,
            "severity": _confidence_to_severity(confidence),
            "model_variant": model_variant,
            "processing_time_ms": processing_time_ms,
            "bbox": det.get("bbox"),
            "affected_area_percentage": det.get("affected_area_percentage"),
        }

        if field_id:
            payload["field_id"] = field_id
        if tenant_id:
            payload["tenant_id"] = tenant_id

        await publish_event(request, VISION_SUBJECTS["disease_detected"], payload)


async def publish_weed_detection(
    request: Request,
    detections: list[dict[str, Any]],
    *,
    model_variant: str = "m",
    processing_time_ms: float = 0,
    field_id: str | None = None,
    tenant_id: str | None = None,
) -> None:
    """Publish weed detection events to NATS."""
    for det in detections:
        confidence = det.get("confidence", 0)
        payload = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "source_service": "yolo26-vision-service",
            "detection_type": "weed",
            "class_name_en": det.get("class_name_en", ""),
            "class_name_ar": det.get("class_name_ar", ""),
            "confidence": confidence,
            "severity": _confidence_to_severity(confidence),
            "model_variant": model_variant,
            "processing_time_ms": processing_time_ms,
            "bbox": det.get("bbox"),
            "coverage_percentage": det.get("coverage_percentage"),
        }

        if field_id:
            payload["field_id"] = field_id
        if tenant_id:
            payload["tenant_id"] = tenant_id

        await publish_event(request, VISION_SUBJECTS["weed_detected"], payload)


async def publish_analysis_event(
    request: Request,
    event_type: str,
    *,
    task: str = "",
    details: dict[str, Any] | None = None,
    field_id: str | None = None,
    tenant_id: str | None = None,
) -> None:
    """
    Publish analysis lifecycle events (started/completed/failed).

    Args:
        event_type: One of "analysis_started", "analysis_completed", "analysis_failed"
        task: Analysis task name (e.g., "plant_counting", "ripeness")
        details: Additional event details
    """
    subject = VISION_SUBJECTS.get(event_type)
    if not subject:
        logger.warning("unknown_event_type", event_type=event_type)
        return

    payload = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "yolo26-vision-service",
        "task": task,
        **(details or {}),
    }

    if field_id:
        payload["field_id"] = field_id
    if tenant_id:
        payload["tenant_id"] = tenant_id

    await publish_event(request, subject, payload)


def _confidence_to_severity(confidence: float) -> str:
    """Map confidence score to severity level."""
    if confidence >= 0.85:
        return "critical"
    elif confidence >= 0.7:
        return "high"
    elif confidence >= 0.5:
        return "medium"
    return "low"
