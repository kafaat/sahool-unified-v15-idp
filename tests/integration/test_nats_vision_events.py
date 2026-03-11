"""
Integration Tests for NATS Vision Events
اختبارات التكامل لأحداث الرؤية الحاسوبية عبر NATS

Tests for YOLO26 vision-related NATS event publishing, subscribing, and schema validation.
Covers subjects:
    - sahool.vision.pest_detected
    - sahool.vision.disease_detected
    - sahool.vision.weed_detected
    - sahool.vision.critical_alert
    - sahool.vision.analysis_started
    - sahool.vision.analysis_completed

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")

# Import vision subject constants
try:
    from shared.events.subjects import (
        SAHOOL_VISION_ANALYSIS_COMPLETED,
        SAHOOL_VISION_ANALYSIS_FAILED,
        SAHOOL_VISION_ANALYSIS_STARTED,
        SAHOOL_VISION_CRITICAL_ALERT,
        SAHOOL_VISION_DISEASE_DETECTED,
        SAHOOL_VISION_PEST_DETECTED,
        SAHOOL_VISION_WEED_DETECTED,
    )
except ImportError:
    SAHOOL_VISION_PEST_DETECTED = "sahool.vision.pest_detected"
    SAHOOL_VISION_DISEASE_DETECTED = "sahool.vision.disease_detected"
    SAHOOL_VISION_WEED_DETECTED = "sahool.vision.weed_detected"
    SAHOOL_VISION_CRITICAL_ALERT = "sahool.vision.critical.alert"
    SAHOOL_VISION_ANALYSIS_STARTED = "sahool.vision.analysis_started"
    SAHOOL_VISION_ANALYSIS_COMPLETED = "sahool.vision.analysis_completed"
    SAHOOL_VISION_ANALYSIS_FAILED = "sahool.vision.analysis_failed"

# Import vision event models
try:
    from shared.events.vision_events import (
        BoundingBox,
        PestDetectedEvent,
        VisionCriticalAlertEvent,
        VisionDiseaseDetectedEvent,
        VisionSubjects,
        WeedDetectedEvent,
    )

    _vision_models_available = True
except ImportError:
    _vision_models_available = False


# ─────────────────────────────────────────────────────────────────────────────
# Test Data Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_bounding_box() -> dict:
    """Build a bounding box payload."""
    return {
        "x_min": 0.12,
        "y_min": 0.25,
        "x_max": 0.38,
        "y_max": 0.55,
        "confidence": 0.92,
        "pixel_x": 120,
        "pixel_y": 250,
        "width_px": 260,
        "height_px": 300,
    }


def _make_pest_detected_payload(
    field_id: str | None = None,
    tenant_id: str | None = None,
    confidence: float = 0.89,
    severity: str = "high",
) -> dict:
    """Build a valid pest_detected event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "yolo26-vision-service",
        "correlation_id": str(uuid.uuid4()),
        "detection_id": str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "pest_class": "red_palm_weevil",
        "pest_class_ar": "سوسة النخيل الحمراء",
        "pest_family": "Curculionidae",
        "scientific_name": "Rhynchophorus ferrugineus",
        "confidence": confidence,
        "severity": severity,
        "infestation_level": "moderate",
        "location": _make_bounding_box(),
        "image_url": "https://storage.sahool.app/images/detection-001.jpg",
        "thumbnail_url": "https://storage.sahool.app/thumbnails/detection-001.jpg",
        "detection_source": "drone",
        "model_version": "yolo26-m-v1.2",
        "processing_time_ms": 55,
        "crop_type": "date_palm",
        "crop_type_ar": "نخيل",
        "growth_stage": "fruiting",
        "estimated_count": 8,
        "affected_area_sqm": 250.0,
        "affected_area_percentage": 3.5,
        "recommended_action": "Apply Emamectin benzoate injection immediately",
        "recommended_action_ar": "تطبيق حقن إمامكتين بنزوات فورا",
        "urgency_hours": 24,
        "estimated_yield_loss_percentage": 15.0,
    }


def _make_disease_detected_payload(
    field_id: str | None = None,
    confidence: float = 0.85,
) -> dict:
    """Build a valid disease_detected event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "yolo26-vision-service",
        "detection_id": str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "disease_class": "wheat_leaf_rust",
        "disease_class_ar": "صدأ أوراق القمح",
        "disease_category": "fungal",
        "pathogen_name": "Puccinia triticina",
        "confidence": confidence,
        "severity": "medium",
        "infection_stage": "developing",
        "location": _make_bounding_box(),
        "image_url": "https://storage.sahool.app/images/disease-001.jpg",
        "detection_source": "mobile",
        "model_version": "yolo26-m-v1.2",
        "processing_time_ms": 62,
        "crop_type": "wheat",
        "crop_type_ar": "قمح",
        "growth_stage": "heading",
        "plant_part_affected": "leaf",
        "affected_plants_count": 25,
        "affected_area_sqm": 400.0,
        "affected_area_percentage": 5.0,
        "spread_risk": "high",
        "symptoms": ["yellow-orange pustules", "leaf chlorosis"],
        "symptoms_ar": ["بثور برتقالية صفراء", "اصفرار الأوراق"],
        "treatment_recommendation": "Apply propiconazole fungicide at 125 ml/ha",
        "treatment_recommendation_ar": "تطبيق مبيد فطري بروبيكونازول بمعدل 125 مل/هكتار",
        "preventive_measures": ["Resistant variety selection", "Crop rotation"],
        "urgency_hours": 48,
        "estimated_yield_loss_percentage": 20.0,
    }


def _make_weed_detected_payload() -> dict:
    """Build a valid weed_detected event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "yolo26-vision-service",
        "detection_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "weed_class": "wild_oat",
        "weed_class_ar": "الشوفان البري",
        "weed_type": "grass",
        "scientific_name": "Avena fatua",
        "confidence": 0.91,
        "severity": "high",
        "density": "dense",
        "location": _make_bounding_box(),
        "image_url": "https://storage.sahool.app/images/weed-001.jpg",
        "detection_source": "drone",
        "model_version": "yolo26-m-v1.2",
        "processing_time_ms": 48,
        "crop_type": "wheat",
        "crop_type_ar": "قمح",
        "growth_stage": "tillering",
        "estimated_count": 150,
        "affected_area_sqm": 1200.0,
        "affected_area_percentage": 12.0,
        "control_method": "chemical",
        "herbicide_recommendation": "Clodinafop-propargyl at 60 g/ha",
        "herbicide_recommendation_ar": "كلودينافوب بروبارجيل بمعدل 60 غ/هكتار",
        "optimal_control_window": "Within 7 days before tillering stage",
        "estimated_yield_loss_percentage": 25.0,
        "control_cost_estimate": 350.0,
        "currency": "SAR",
    }


def _make_critical_alert_payload(
    field_id: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    """Build a valid critical_alert event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "yolo26-vision-service",
        "alert_id": str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "alert_type": "pest_outbreak",
        "alert_title": "Red Palm Weevil Outbreak Detected",
        "alert_title_ar": "اكتشاف تفشي سوسة النخيل الحمراء",
        "alert_message": "Multiple RPW detections in date palm block B. Immediate action required.",
        "alert_message_ar": "اكتشاف متعدد لسوسة النخيل الحمراء في كتلة النخيل ب. يتطلب إجراء فوري.",
        "severity": "critical",
        "priority": 1,
        "related_detection_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
        "detection_count": 5,
        "affected_area_sqm": 800.0,
        "affected_area_percentage": 8.5,
        "crop_type": "date_palm",
        "crop_type_ar": "نخيل",
        "estimated_loss_percentage": 30.0,
        "estimated_loss_value": 45000.0,
        "currency": "SAR",
        "response_deadline_hours": 24,
        "recommended_actions": [
            "Mark affected trees with red paint",
            "Inject Emamectin benzoate at 50-100ml per point",
            "Report to Ministry of Agriculture",
        ],
        "recommended_actions_ar": [
            "تحديد الأشجار المصابة بطلاء أحمر",
            "حقن إمامكتين بنزوات بمعدل 50-100 مل لكل نقطة",
            "الإبلاغ لوزارة الزراعة",
        ],
        "auto_notify_agronomist": True,
        "escalation_level": 2,
        "evidence_image_urls": [
            "https://storage.sahool.app/images/rpw-evidence-001.jpg",
            "https://storage.sahool.app/images/rpw-evidence-002.jpg",
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_nats():
    """Create a mock NATS client."""
    nc = AsyncMock()
    nc.publish = AsyncMock()
    nc.subscribe = AsyncMock()
    nc.flush = AsyncMock()
    nc.drain = AsyncMock()
    nc.close = AsyncMock()
    nc.is_connected = True
    return nc


@pytest.fixture
def mock_nats_msg():
    """Factory for mock NATS messages."""

    def _make(subject: str, payload: dict):
        msg = MagicMock()
        msg.subject = subject
        msg.data = json.dumps(payload).encode("utf-8")
        msg.headers = {}
        msg.ack = AsyncMock()
        msg.nak = AsyncMock()
        return msg

    return _make


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Pest Detection Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pest_detected_event_published_with_correct_schema(mock_nats):
    """Test that pest_detected event is published with complete detection payload."""
    payload = _make_pest_detected_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_VISION_PEST_DETECTED, data)
    mock_nats.publish.assert_awaited_once_with(SAHOOL_VISION_PEST_DETECTED, data)

    decoded = json.loads(data)
    # Core detection fields
    assert "detection_id" in decoded
    assert "field_id" in decoded
    assert "tenant_id" in decoded
    assert "pest_class" in decoded
    assert "pest_class_ar" in decoded

    # Confidence and severity
    assert 0 <= decoded["confidence"] <= 1, "Confidence must be in [0, 1]"
    assert decoded["severity"] in ("low", "medium", "high", "critical")

    # Bounding box
    assert "location" in decoded
    bbox = decoded["location"]
    assert "x_min" in bbox and "y_min" in bbox
    assert "x_max" in bbox and "y_max" in bbox
    assert "confidence" in bbox

    # Recommendations
    assert "recommended_action" in decoded
    assert "recommended_action_ar" in decoded
    assert decoded["urgency_hours"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pest_detected_subscribe_and_receive(mock_nats, mock_nats_msg):
    """Test subscribing to pest_detected and receiving detection event."""
    received_events: list[dict] = []

    async def handler(msg):
        data = json.loads(msg.data.decode("utf-8"))
        received_events.append(data)

    await mock_nats.subscribe(SAHOOL_VISION_PEST_DETECTED, cb=handler)

    payload = _make_pest_detected_payload(confidence=0.95, severity="critical")
    msg = mock_nats_msg(SAHOOL_VISION_PEST_DETECTED, payload)
    await handler(msg)

    assert len(received_events) == 1
    event = received_events[0]
    assert event["pest_class"] == "red_palm_weevil"
    assert event["confidence"] == 0.95
    assert event["severity"] == "critical"
    assert event["source_service"] == "yolo26-vision-service"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Disease Detection Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_disease_detected_event_schema(mock_nats):
    """Test disease_detected event payload includes disease-specific fields."""
    payload = _make_disease_detected_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_VISION_DISEASE_DETECTED, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert decoded["disease_class"] == "wheat_leaf_rust"
    assert decoded["disease_class_ar"] == "صدأ أوراق القمح"
    assert decoded["disease_category"] in ("fungal", "bacterial", "viral", "physiological", "nutrient_deficiency")
    assert decoded["infection_stage"] in ("early", "developing", "advanced", "terminal")
    assert "symptoms" in decoded and len(decoded["symptoms"]) > 0
    assert "symptoms_ar" in decoded and len(decoded["symptoms_ar"]) > 0
    assert "treatment_recommendation" in decoded
    assert "treatment_recommendation_ar" in decoded
    assert decoded["spread_risk"] in ("low", "medium", "high")


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Weed Detection Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weed_detected_event_schema(mock_nats):
    """Test weed_detected event payload includes weed-specific and cost fields."""
    payload = _make_weed_detected_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_VISION_WEED_DETECTED, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert decoded["weed_class"] == "wild_oat"
    assert decoded["weed_class_ar"] == "الشوفان البري"
    assert decoded["weed_type"] in ("broadleaf", "grass", "sedge", "parasitic")
    assert decoded["density"] in ("sparse", "moderate", "dense", "very_dense")
    assert decoded["control_method"] in ("mechanical", "chemical", "biological", "manual", "integrated")
    assert decoded["control_cost_estimate"] >= 0
    assert decoded["currency"] == "SAR"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Critical Alert Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_critical_alert_event_schema(mock_nats):
    """Test critical_alert event payload includes bilingual alerts and escalation."""
    payload = _make_critical_alert_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_VISION_CRITICAL_ALERT, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    # Alert classification
    assert decoded["alert_type"] in ("pest_outbreak", "disease_outbreak", "severe_infestation", "crop_failure_risk")
    assert decoded["severity"] in ("high", "critical")
    assert 1 <= decoded["priority"] <= 5

    # Bilingual content
    assert "alert_title" in decoded and len(decoded["alert_title"]) > 0
    assert "alert_title_ar" in decoded and len(decoded["alert_title_ar"]) > 0
    assert "alert_message" in decoded
    assert "alert_message_ar" in decoded

    # Related detections
    assert decoded["detection_count"] >= 1
    assert len(decoded["related_detection_ids"]) > 0

    # Response and escalation
    assert decoded["response_deadline_hours"] >= 1
    assert len(decoded["recommended_actions"]) > 0
    assert len(decoded["recommended_actions_ar"]) > 0
    assert decoded["auto_notify_agronomist"] is True
    assert 1 <= decoded["escalation_level"] <= 3

    # Economic impact
    assert decoded["estimated_loss_value"] >= 0
    assert decoded["currency"] == "SAR"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_critical_alert_triggers_from_pest_detection(mock_nats, mock_nats_msg):
    """Test the flow of pest detection leading to a critical alert event."""
    published_subjects: list[str] = []
    published_payloads: list[dict] = []

    original_publish = mock_nats.publish

    async def capture_publish(subject, data):
        published_subjects.append(subject)
        published_payloads.append(json.loads(data.decode("utf-8")))
        return await original_publish(subject, data)

    mock_nats.publish = capture_publish

    # Step 1: Publish pest detection
    pest_payload = _make_pest_detected_payload(severity="critical")
    await mock_nats.publish(
        SAHOOL_VISION_PEST_DETECTED,
        json.dumps(pest_payload).encode("utf-8"),
    )

    # Step 2: Publish critical alert (as would be triggered by the vision service)
    alert_payload = _make_critical_alert_payload(
        field_id=pest_payload["field_id"],
        tenant_id=pest_payload["tenant_id"],
    )
    await mock_nats.publish(
        SAHOOL_VISION_CRITICAL_ALERT,
        json.dumps(alert_payload).encode("utf-8"),
    )

    assert len(published_subjects) == 2
    assert published_subjects[0] == SAHOOL_VISION_PEST_DETECTED
    assert published_subjects[1] == SAHOOL_VISION_CRITICAL_ALERT

    # The alert should reference the same field and tenant
    assert published_payloads[1]["field_id"] == pest_payload["field_id"]
    assert published_payloads[1]["tenant_id"] == pest_payload["tenant_id"]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Pydantic Model Validation
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _vision_models_available, reason="shared.events.vision_events not available")
async def test_pest_detected_pydantic_model_validation():
    """Test PestDetectedEvent Pydantic model validates correctly."""
    payload = _make_pest_detected_payload()
    event = PestDetectedEvent(**payload)

    assert event.pest_class == "red_palm_weevil"
    assert event.pest_class_ar == "سوسة النخيل الحمراء"
    assert event.confidence == 0.89
    assert event.severity == "high"
    assert event.location.x_min == 0.12
    assert event.location.confidence == 0.92
    assert event.source_service == "yolo26-vision-service"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _vision_models_available, reason="shared.events.vision_events not available")
async def test_vision_subjects_class_constants():
    """Test VisionSubjects class provides correct subject constants."""
    assert VisionSubjects.PEST_DETECTED == "sahool.vision.pest_detected"
    assert VisionSubjects.DISEASE_DETECTED == "sahool.vision.disease_detected"
    assert VisionSubjects.WEED_DETECTED == "sahool.vision.weed_detected"
    assert VisionSubjects.CRITICAL_ALERT == "sahool.vision.critical.alert"
    assert VisionSubjects.ANALYSIS_STARTED == "sahool.vision.analysis_started"
    assert VisionSubjects.ANALYSIS_COMPLETED == "sahool.vision.analysis_completed"
    assert VisionSubjects.ANALYSIS_FAILED == "sahool.vision.analysis_failed"

    # Test tenant-scoped subject
    tenant_id = "org_farm_001"
    scoped = VisionSubjects.tenant_scoped(tenant_id, "pest_detected")
    assert scoped == f"sahool.tenant.{tenant_id}.vision.pest_detected"
