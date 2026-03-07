"""
NATS Event Publishers - ناشرو أحداث NATS
Based on: SAHOOL 4-Layer Event Architecture

This module publishes ground vision events to the NATS message bus
for consumption by other services.
"""

import json
import logging
from datetime import UTC, datetime, timezone
from typing import Optional

from pydantic import BaseModel

from ..models.anomaly import AnomalyAlert, AnomalyDetection
from ..models.detection import FieldOperationDetection
from ..models.timeline import CropTimelineAnalysis, CropTimelineEntry

logger = logging.getLogger(__name__)


class EventPayload(BaseModel):
    """Base event payload structure"""

    event_id: str
    event_type: str
    timestamp: str
    tenant_id: str
    data: dict


class GroundVisionPublisher:
    """
    Publish ground vision events to NATS.

    Event subjects follow the pattern:
    sahool.{tenant_id}.ground_vision.{event_type}
    """

    # Event subject patterns
    SUBJECT_FRAME_CAPTURED = "sahool.{tenant_id}.ground_vision.frame_captured"
    SUBJECT_OPERATION_DETECTED = "sahool.{tenant_id}.ground_vision.operation_detected"
    SUBJECT_GROWTH_STAGE_CHANGED = "sahool.{tenant_id}.ground_vision.growth_stage_changed"
    SUBJECT_ANOMALY_DETECTED = "sahool.{tenant_id}.ground_vision.anomaly_detected"
    SUBJECT_TIMELINE_UPDATED = "sahool.{tenant_id}.ground_vision.timeline_updated"
    SUBJECT_CAMERA_STATUS = "sahool.{tenant_id}.ground_vision.camera_status"

    def __init__(self, nc=None):
        """
        Initialize publisher.

        Args:
            nc: NATS connection (async)
        """
        self.nc = nc
        self._event_counter = 0

    def set_connection(self, nc):
        """Set NATS connection after initialization."""
        self.nc = nc

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        self._event_counter += 1
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        return f"gv_evt_{timestamp}_{self._event_counter}"

    async def publish_frame_captured(
        self,
        camera_id: str,
        frame_id: str,
        tenant_id: str,
        geo_bounds: list[dict] | None = None,
        metadata: dict | None = None,
    ):
        """
        Publish frame captured event.

        Args:
            camera_id: Camera that captured the frame
            frame_id: Unique frame identifier
            tenant_id: Tenant identifier
            geo_bounds: Geographic bounds of frame coverage
            metadata: Additional frame metadata
        """
        subject = self.SUBJECT_FRAME_CAPTURED.format(tenant_id=tenant_id)

        payload = EventPayload(
            event_id=self._generate_event_id(),
            event_type="frame_captured",
            timestamp=datetime.now(UTC).isoformat(),
            tenant_id=tenant_id,
            data={
                "camera_id": camera_id,
                "frame_id": frame_id,
                "geo_bounds": geo_bounds,
                "metadata": metadata or {},
            },
        )

        await self._publish(subject, payload)
        logger.debug(f"Published frame_captured event for {frame_id}")

    async def publish_operation_detected(
        self,
        detection: FieldOperationDetection,
    ):
        """
        Publish agricultural operation detected event.

        Args:
            detection: Field operation detection result
        """
        subject = self.SUBJECT_OPERATION_DETECTED.format(tenant_id=detection.tenant_id)

        payload = EventPayload(
            event_id=self._generate_event_id(),
            event_type="operation_detected",
            timestamp=datetime.now(UTC).isoformat(),
            tenant_id=detection.tenant_id,
            data={
                "detection_id": detection.detection_id,
                "field_id": detection.field_id,
                "camera_id": detection.camera_id,
                "operation_type": detection.operation_type.value,
                "operation_type_ar": detection.operation_type_ar,
                "confidence": detection.confidence,
                "confidence_level": detection.confidence_level.value,
                "equipment_type": detection.equipment_type.value if detection.equipment_type else None,
                "equipment_type_ar": detection.equipment_type_ar,
                "center_lat": detection.center_lat,
                "center_lon": detection.center_lon,
                "detected_at": detection.detected_at.isoformat(),
                "source_frame_id": detection.source_frame_id,
            },
        )

        await self._publish(subject, payload)
        logger.info(f"Published operation_detected: {detection.operation_type.value} in {detection.field_id}")

    async def publish_growth_stage_changed(
        self,
        field_id: str,
        tenant_id: str,
        crop_type: str,
        crop_type_ar: str,
        from_stage: str,
        from_stage_ar: str,
        to_stage: str,
        to_stage_ar: str,
        confidence: float,
        evidence_frames: list[str],
    ):
        """
        Publish growth stage transition event.

        Args:
            field_id: Field identifier
            tenant_id: Tenant identifier
            crop_type: Crop type (English)
            crop_type_ar: Crop type (Arabic)
            from_stage: Previous growth stage
            from_stage_ar: Previous stage (Arabic)
            to_stage: New growth stage
            to_stage_ar: New stage (Arabic)
            confidence: Confidence in transition
            evidence_frames: Frame IDs supporting the transition
        """
        subject = self.SUBJECT_GROWTH_STAGE_CHANGED.format(tenant_id=tenant_id)

        payload = EventPayload(
            event_id=self._generate_event_id(),
            event_type="growth_stage_changed",
            timestamp=datetime.now(UTC).isoformat(),
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "crop_type": crop_type,
                "crop_type_ar": crop_type_ar,
                "from_stage": from_stage,
                "from_stage_ar": from_stage_ar,
                "to_stage": to_stage,
                "to_stage_ar": to_stage_ar,
                "confidence": confidence,
                "evidence_frames": evidence_frames,
            },
        )

        await self._publish(subject, payload)
        logger.info(f"Published growth_stage_changed: {from_stage} -> {to_stage} for {field_id}")

    async def publish_anomaly_detected(
        self,
        anomaly: AnomalyDetection,
    ):
        """
        Publish anomaly detected event.

        Args:
            anomaly: Anomaly detection result
        """
        subject = self.SUBJECT_ANOMALY_DETECTED.format(tenant_id=anomaly.tenant_id)

        payload = EventPayload(
            event_id=self._generate_event_id(),
            event_type="anomaly_detected",
            timestamp=datetime.now(UTC).isoformat(),
            tenant_id=anomaly.tenant_id,
            data={
                "anomaly_id": anomaly.anomaly_id,
                "field_id": anomaly.field_id,
                "camera_id": anomaly.camera_id,
                "anomaly_type": anomaly.anomaly_type.value,
                "anomaly_type_ar": anomaly.anomaly_type_ar,
                "severity": anomaly.severity.value,
                "severity_ar": anomaly.severity_ar,
                "confidence": anomaly.confidence,
                "description": anomaly.description,
                "description_ar": anomaly.description_ar,
                "location": {
                    "lat": anomaly.location.lat,
                    "lon": anomaly.location.lon,
                    "affected_area_percent": anomaly.location.affected_area_percent,
                },
                "detected_at": anomaly.detected_at.isoformat(),
                "response_deadline_hours": anomaly.response_deadline_hours,
            },
        )

        await self._publish(subject, payload)
        logger.warning(
            f"Published anomaly_detected: {anomaly.anomaly_type.value} ({anomaly.severity.value}) in {anomaly.field_id}"
        )

    async def publish_timeline_updated(
        self,
        analysis: CropTimelineAnalysis,
    ):
        """
        Publish timeline analysis completed event.

        Args:
            analysis: Crop timeline analysis result
        """
        subject = self.SUBJECT_TIMELINE_UPDATED.format(tenant_id=analysis.tenant_id)

        payload = EventPayload(
            event_id=self._generate_event_id(),
            event_type="timeline_updated",
            timestamp=datetime.now(UTC).isoformat(),
            tenant_id=analysis.tenant_id,
            data={
                "analysis_id": analysis.analysis_id,
                "field_id": analysis.field_id,
                "crop_type": analysis.crop_type.value,
                "crop_type_ar": analysis.crop_type_ar,
                "current_stage": analysis.current_stage.value,
                "current_stage_ar": analysis.current_stage_ar,
                "stage_confidence": analysis.stage_confidence,
                "health_score": analysis.health_score,
                "operations_detected": analysis.operations_detected,
                "anomalies": analysis.anomalies,
                "recommendations": analysis.recommendations,
                "recommendations_ar": analysis.recommendations_ar,
                "analyzed_at": analysis.analyzed_at.isoformat(),
            },
        )

        await self._publish(subject, payload)
        logger.info(
            f"Published timeline_updated for {analysis.field_id}: "
            f"{analysis.crop_type.value} at {analysis.current_stage.value}"
        )

    async def publish_camera_status(
        self,
        camera_id: str,
        tenant_id: str,
        status: str,
        status_ar: str,
        details: dict | None = None,
    ):
        """
        Publish camera status change event.

        Args:
            camera_id: Camera identifier
            tenant_id: Tenant identifier
            status: Status (online, offline, error, maintenance)
            status_ar: Status in Arabic
            details: Additional status details
        """
        subject = self.SUBJECT_CAMERA_STATUS.format(tenant_id=tenant_id)

        payload = EventPayload(
            event_id=self._generate_event_id(),
            event_type="camera_status",
            timestamp=datetime.now(UTC).isoformat(),
            tenant_id=tenant_id,
            data={
                "camera_id": camera_id,
                "status": status,
                "status_ar": status_ar,
                "details": details or {},
            },
        )

        await self._publish(subject, payload)
        logger.info(f"Published camera_status: {camera_id} is {status}")

    async def _publish(self, subject: str, payload: EventPayload):
        """
        Publish event to NATS.

        Args:
            subject: NATS subject
            payload: Event payload
        """
        if self.nc is None:
            logger.warning(f"NATS not connected, skipping publish to {subject}")
            return

        try:
            data = payload.model_dump_json().encode()
            await self.nc.publish(subject, data)
        except Exception as e:
            logger.error(f"Failed to publish to {subject}: {e}")
            raise
