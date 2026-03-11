"""
YOLO26 Vision Service - NATS Event Publisher
=============================================
ناشر أحداث NATS - خدمة الرؤية الحاسوبية YOLO26

Publishes vision detection events to NATS subjects defined in
shared.events.vision_events for consumption by downstream services
(alert-service, notification-service, advisory-service, etc.).

Subjects:
    sahool.vision.pest_detected      - Pest detection results
    sahool.vision.disease_detected   - Disease detection results
    sahool.vision.weed_detected      - Weed detection results
    sahool.vision.plant_count_completed - Plant counting results
    sahool.vision.critical.alert     - Critical pest alerts (RPW, locust)
    sahool.vision.analysis_started   - Analysis job started
    sahool.vision.analysis_completed - Analysis job completed
    sahool.vision.analysis_failed    - Analysis job failed
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)

# Critical pest class IDs that trigger critical alerts
CRITICAL_PEST_IDS = {
    0,  # Red Palm Weevil (سوسة النخيل الحمراء)
    11,  # Locust (الجراد)
}

# NATS subjects (matching shared.events.vision_events.VisionSubjects)
SUBJECT_PEST_DETECTED = "sahool.vision.pest_detected"
SUBJECT_DISEASE_DETECTED = "sahool.vision.disease_detected"
SUBJECT_WEED_DETECTED = "sahool.vision.weed_detected"
SUBJECT_PLANT_COUNT_COMPLETED = "sahool.vision.plant_count_completed"
SUBJECT_CRITICAL_ALERT = "sahool.vision.critical.alert"
SUBJECT_ANALYSIS_STARTED = "sahool.vision.analysis_started"
SUBJECT_ANALYSIS_COMPLETED = "sahool.vision.analysis_completed"
SUBJECT_ANALYSIS_FAILED = "sahool.vision.analysis_failed"


class VisionEventPublisher:
    """
    Publishes vision detection events to NATS.
    ناشر أحداث اكتشاف الرؤية عبر NATS

    Args:
        nc: NATS client connection (from app.state.nc)
        service_name: Source service identifier
    """

    def __init__(self, nc: Any, service_name: str = "yolo26-vision-service"):
        self._nc = nc
        self._service_name = service_name

    def _base_envelope(self, correlation_id: str | None = None) -> dict:
        """Create base event envelope with standard fields."""
        return {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "source_service": self._service_name,
            "correlation_id": correlation_id or str(uuid4()),
        }

    async def _publish(self, subject: str, payload: dict) -> None:
        """Publish a JSON payload to a NATS subject with error handling."""
        try:
            data = json.dumps(payload, default=str).encode()
            await self._nc.publish(subject, data)
            logger.info(
                "event_published",
                subject=subject,
                event_id=payload.get("event_id"),
            )
        except Exception as e:
            logger.error(
                "event_publish_failed",
                subject=subject,
                error=str(e),
            )

    # ─────────────────────────────────────────────────────────────────
    # Pest Detection Events
    # ─────────────────────────────────────────────────────────────────

    async def publish_pest_detected(
        self,
        *,
        request_id: UUID,
        detections: list[dict],
        processing_time_ms: float,
        model_variant: str,
        field_id: UUID | None = None,
        tenant_id: UUID | None = None,
        image_url: str | None = None,
        detection_source: str = "mobile",
    ) -> None:
        """
        Publish pest detection event after successful detection.
        نشر حدث اكتشاف الآفات بعد نجاح الكشف

        Also publishes critical alerts for Red Palm Weevil and Locust.
        """
        envelope = self._base_envelope(correlation_id=str(request_id))
        envelope.update(
            {
                "detection_id": str(uuid4()),
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "detection_count": len(detections),
                "model_variant": model_variant,
                "processing_time_ms": round(processing_time_ms, 2),
                "detection_source": detection_source,
                "image_url": image_url,
                "detections": [
                    {
                        "class_id": d.get("class_id"),
                        "class_name_en": d.get("class_name_en"),
                        "class_name_ar": d.get("class_name_ar"),
                        "confidence": d.get("confidence"),
                        "severity": d.get("severity"),
                        "bbox": d.get("bbox"),
                    }
                    for d in detections
                ],
            }
        )

        await self._publish(SUBJECT_PEST_DETECTED, envelope)

        # Check for critical pests and publish critical alert
        critical_detections = [d for d in detections if d.get("class_id") in CRITICAL_PEST_IDS]
        if critical_detections:
            await self._publish_critical_alert(
                alert_type="pest_outbreak",
                detections=critical_detections,
                field_id=field_id,
                tenant_id=tenant_id,
                correlation_id=str(request_id),
            )

    # ─────────────────────────────────────────────────────────────────
    # Disease Detection Events
    # ─────────────────────────────────────────────────────────────────

    async def publish_disease_detected(
        self,
        *,
        request_id: UUID,
        detections: list[dict],
        processing_time_ms: float,
        model_variant: str,
        health_score: float,
        field_id: UUID | None = None,
        tenant_id: UUID | None = None,
        image_url: str | None = None,
        detection_source: str = "mobile",
    ) -> None:
        """
        Publish disease detection event.
        نشر حدث اكتشاف الأمراض
        """
        envelope = self._base_envelope(correlation_id=str(request_id))
        envelope.update(
            {
                "detection_id": str(uuid4()),
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "detection_count": len(detections),
                "model_variant": model_variant,
                "processing_time_ms": round(processing_time_ms, 2),
                "health_score": round(health_score, 1),
                "detection_source": detection_source,
                "image_url": image_url,
                "detections": [
                    {
                        "class_id": d.get("class_id"),
                        "class_name_en": d.get("class_name_en"),
                        "class_name_ar": d.get("class_name_ar"),
                        "confidence": d.get("confidence"),
                        "severity": d.get("severity"),
                        "affected_area_percent": d.get("affected_area_percent"),
                        "spread_risk": d.get("spread_risk"),
                        "bbox": d.get("bbox"),
                    }
                    for d in detections
                ],
            }
        )

        await self._publish(SUBJECT_DISEASE_DETECTED, envelope)

        # Critical alert for severe disease outbreaks
        critical = [d for d in detections if d.get("severity") in ("critical", "high")]
        if len(critical) >= 3 or health_score < 30:
            await self._publish_critical_alert(
                alert_type="disease_outbreak",
                detections=critical or detections[:3],
                field_id=field_id,
                tenant_id=tenant_id,
                correlation_id=str(request_id),
            )

    # ─────────────────────────────────────────────────────────────────
    # Weed Detection Events
    # ─────────────────────────────────────────────────────────────────

    async def publish_weed_detected(
        self,
        *,
        request_id: UUID,
        detections: list[dict],
        processing_time_ms: float,
        model_variant: str,
        total_coverage_percent: float,
        field_id: UUID | None = None,
        tenant_id: UUID | None = None,
        image_url: str | None = None,
        detection_source: str = "drone",
    ) -> None:
        """
        Publish weed detection event.
        نشر حدث اكتشاف الأعشاب الضارة
        """
        envelope = self._base_envelope(correlation_id=str(request_id))
        envelope.update(
            {
                "detection_id": str(uuid4()),
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "detection_count": len(detections),
                "model_variant": model_variant,
                "processing_time_ms": round(processing_time_ms, 2),
                "total_coverage_percent": round(total_coverage_percent, 1),
                "detection_source": detection_source,
                "image_url": image_url,
                "species_distribution": {},
                "detections": [
                    {
                        "class_id": d.get("class_id"),
                        "class_name_en": d.get("class_name_en"),
                        "class_name_ar": d.get("class_name_ar"),
                        "confidence": d.get("confidence"),
                        "coverage_percent": d.get("coverage_percent"),
                        "bbox": d.get("bbox"),
                    }
                    for d in detections
                ],
            }
        )

        # Build species distribution
        for d in detections:
            name = d.get("class_name_en", "Unknown")
            envelope["species_distribution"][name] = envelope["species_distribution"].get(name, 0) + 1

        await self._publish(SUBJECT_WEED_DETECTED, envelope)

    # ─────────────────────────────────────────────────────────────────
    # Plant Count Events
    # ─────────────────────────────────────────────────────────────────

    async def publish_plant_count_completed(
        self,
        *,
        request_id: UUID,
        total_count: int,
        processing_time_ms: float,
        model_variant: str,
        density_per_sqm: float | None = None,
        field_id: UUID | None = None,
        tenant_id: UUID | None = None,
        crop_type: str | None = None,
        detection_source: str = "drone",
    ) -> None:
        """
        Publish plant counting completed event.
        نشر حدث اكتمال إحصاء النباتات
        """
        envelope = self._base_envelope(correlation_id=str(request_id))
        envelope.update(
            {
                "analysis_id": str(uuid4()),
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "total_plant_count": total_count,
                "plants_per_sqm": density_per_sqm,
                "model_variant": model_variant,
                "processing_time_ms": round(processing_time_ms, 2),
                "crop_type": crop_type,
                "detection_source": detection_source,
            }
        )

        await self._publish(SUBJECT_PLANT_COUNT_COMPLETED, envelope)

    # ─────────────────────────────────────────────────────────────────
    # Analysis Lifecycle Events
    # ─────────────────────────────────────────────────────────────────

    async def publish_analysis_started(
        self,
        *,
        analysis_type: str,
        request_id: UUID,
        field_id: UUID | None = None,
        tenant_id: UUID | None = None,
        model_variant: str = "m",
    ) -> None:
        """
        Publish analysis started event.
        نشر حدث بدء التحليل
        """
        envelope = self._base_envelope(correlation_id=str(request_id))
        envelope.update(
            {
                "analysis_id": str(request_id),
                "analysis_type": analysis_type,
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "model_id": f"yolo26-{model_variant}",
            }
        )

        await self._publish(SUBJECT_ANALYSIS_STARTED, envelope)

    async def publish_analysis_completed(
        self,
        *,
        analysis_type: str,
        request_id: UUID,
        total_detections: int,
        processing_time_ms: float,
        field_id: UUID | None = None,
        tenant_id: UUID | None = None,
    ) -> None:
        """
        Publish analysis completed event.
        نشر حدث اكتمال التحليل
        """
        envelope = self._base_envelope(correlation_id=str(request_id))
        envelope.update(
            {
                "analysis_id": str(request_id),
                "analysis_type": analysis_type,
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "status": "completed",
                "total_detections": total_detections,
                "processing_duration_ms": round(processing_time_ms, 2),
            }
        )

        await self._publish(SUBJECT_ANALYSIS_COMPLETED, envelope)

    async def publish_analysis_failed(
        self,
        *,
        analysis_type: str,
        request_id: UUID,
        error_code: str,
        error_message: str,
        field_id: UUID | None = None,
        tenant_id: UUID | None = None,
    ) -> None:
        """
        Publish analysis failed event.
        نشر حدث فشل التحليل
        """
        envelope = self._base_envelope(correlation_id=str(request_id))
        envelope.update(
            {
                "analysis_id": str(request_id),
                "analysis_type": analysis_type,
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "error_code": error_code,
                "error_message": error_message,
            }
        )

        await self._publish(SUBJECT_ANALYSIS_FAILED, envelope)

    # ─────────────────────────────────────────────────────────────────
    # Critical Alert (internal helper)
    # ─────────────────────────────────────────────────────────────────

    async def _publish_critical_alert(
        self,
        *,
        alert_type: str,
        detections: list[dict],
        field_id: UUID | None,
        tenant_id: UUID | None,
        correlation_id: str,
    ) -> None:
        """Publish critical alert for emergency pest/disease situations."""
        # Determine alert details based on type
        if alert_type == "pest_outbreak":
            title = "Critical Pest Alert"
            title_ar = "تنبيه آفات حرج"
            message = f"Critical pest detected: {len(detections)} detection(s) require immediate action"
            message_ar = f"تم اكتشاف آفة حرجة: {len(detections)} اكتشاف(ات) تتطلب إجراءً فوريًا"
            response_hours = 24
        else:
            title = "Disease Outbreak Alert"
            title_ar = "تنبيه تفشي مرض"
            message = f"Severe disease outbreak: {len(detections)} critical detection(s)"
            message_ar = f"تفشي مرض شديد: {len(detections)} اكتشاف(ات) حرجة"
            response_hours = 48

        envelope = self._base_envelope(correlation_id=correlation_id)
        envelope.update(
            {
                "alert_id": str(uuid4()),
                "alert_type": alert_type,
                "alert_title": title,
                "alert_title_ar": title_ar,
                "alert_message": message,
                "alert_message_ar": message_ar,
                "severity": "critical",
                "priority": 1,
                "field_id": str(field_id) if field_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "detection_count": len(detections),
                "response_deadline_hours": response_hours,
                "auto_notify_agronomist": True,
                "escalation_level": 1,
                "related_detections": [
                    {
                        "class_id": d.get("class_id"),
                        "class_name_en": d.get("class_name_en"),
                        "confidence": d.get("confidence"),
                    }
                    for d in detections
                ],
            }
        )

        await self._publish(SUBJECT_CRITICAL_ALERT, envelope)

        logger.warning(
            "critical_alert_published",
            alert_type=alert_type,
            detection_count=len(detections),
            field_id=str(field_id) if field_id else None,
        )
