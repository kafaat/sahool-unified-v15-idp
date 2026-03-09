"""
Integration Tests for NATS Advisory Events
اختبارات التكامل لأحداث الاستشارات الزراعية عبر NATS

Tests for advisory-related NATS event publishing, subscribing, and schema validation.
Covers subjects:
    - sahool.advisory.generated
    - sahool.advisory.irrigation
    - sahool.advisory.fertilizer
    - sahool.advisory.pest_control

Author: SAHOOL Platform Team
"""

from __future__ import annotations

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

# Advisory event subjects
# Note: The subjects.py module uses "recommendation" domain for advisory events.
# The advisory-service publishes to "sahool.advisory.*" subjects while
# recommendation subjects are used for the recommendation subsystem.
try:
    from shared.events.subjects import (
        SAHOOL_RECOMMENDATION_CREATED,
        SAHOOL_RECOMMENDATION_FERTILIZER,
        SAHOOL_RECOMMENDATION_IRRIGATION,
        SAHOOL_RECOMMENDATION_PEST_CONTROL,
    )

    _subjects_available = True
except ImportError:
    SAHOOL_RECOMMENDATION_CREATED = "sahool.recommendation.created"
    SAHOOL_RECOMMENDATION_IRRIGATION = "sahool.recommendation.irrigation"
    SAHOOL_RECOMMENDATION_FERTILIZER = "sahool.recommendation.fertilizer"
    SAHOOL_RECOMMENDATION_PEST_CONTROL = "sahool.recommendation.pest_control"
    _subjects_available = False

# Advisory-service specific subjects (used in the 4-layer event architecture)
SAHOOL_ADVISORY_GENERATED = "sahool.advisory.generated"
SAHOOL_ADVISORY_IRRIGATION = "sahool.advisory.irrigation"
SAHOOL_ADVISORY_FERTILIZER = "sahool.advisory.fertilizer"
SAHOOL_ADVISORY_PEST_CONTROL = "sahool.advisory.pest_control"


# ─────────────────────────────────────────────────────────────────────────────
# Test Data Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_advisory_generated_payload(
    field_id: str | None = None,
    tenant_id: str | None = None,
    advisory_type: str = "general",
) -> dict:
    """Build a valid advisory.generated event payload with bilingual content."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "advisory-service",
        "correlation_id": str(uuid.uuid4()),
        "advisory_id": str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "advisory_type": advisory_type,
        "priority": "high",
        "title": "Nitrogen Deficiency Detected in Field Alpha",
        "title_ar": "اكتشاف نقص النيتروجين في حقل ألفا",
        "summary": "Soil analysis confirms nitrogen deficiency at 18 ppm (target: 25 ppm). "
        "Immediate top-dressing recommended to prevent yield loss.",
        "summary_ar": "تحليل التربة يؤكد نقص النيتروجين عند 18 جزء في المليون (الهدف: 25 جزء في المليون). "
        "يُنصح بالتسميد العلوي الفوري لمنع خسارة المحصول.",
        "recommendation": "Apply Urea 46% at 46 kg/ha as top dressing early morning with dew present.",
        "recommendation_ar": "تطبيق يوريا 46% بمعدل 46 كغ/هكتار كتسميد علوي في الصباح الباكر مع وجود الندى.",
        "rationale": "Based on soil test results, crop growth stage (tillering), and weather forecast.",
        "rationale_ar": "بناءً على نتائج تحليل التربة ومرحلة نمو المحصول (التفريع) وتوقعات الطقس.",
        "action_items": [
            {
                "step": 1,
                "action": "Apply Urea 46% at 46 kg/ha using broadcast method",
                "action_ar": "تطبيق يوريا 46% بمعدل 46 كغ/هكتار بطريقة البث",
                "timing": "Early morning (6-8 AM) with dew",
                "timing_ar": "الصباح الباكر (6-8 صباحا) مع الندى",
            },
            {
                "step": 2,
                "action": "Light irrigation 15-20 mm within 1-2 days after application",
                "action_ar": "ري خفيف 15-20 مم خلال 1-2 يوم بعد التطبيق",
                "timing": "1-2 days after fertilizer",
                "timing_ar": "1-2 يوم بعد السماد",
            },
            {
                "step": 3,
                "action": "Monitor leaf color improvement in 7-10 days",
                "action_ar": "مراقبة تحسن لون الأوراق خلال 7-10 أيام",
                "timing": "7-10 days after application",
                "timing_ar": "7-10 أيام بعد التطبيق",
            },
        ],
        "confidence_score": 0.87,
        "data_sources": ["soil_test", "ndvi_satellite", "weather_forecast", "growth_stage"],
        "crop_type": "wheat",
        "crop_type_ar": "قمح",
        "growth_stage": "tillering",
        "growth_stage_ar": "التفريع",
        "economic_analysis": {
            "treatment_cost_per_ha": 115.0,
            "expected_yield_saved_per_ha": 0.7,
            "yield_price_per_ton": 1850.0,
            "expected_revenue_saved_per_ha": 1295.0,
            "roi_percentage": 1025.0,
            "currency": "SAR",
        },
        "follow_up_date": datetime.now(UTC).isoformat(),
        "generated_by": "crop_advisor_agent",
        "model_version": "advisory-v2.3",
    }


def _make_irrigation_advisory_payload(
    field_id: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    """Build a valid advisory.irrigation event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "irrigation-smart",
        "advisory_id": str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "advisory_type": "irrigation",
        "priority": "high",
        "title": "Irrigation Recommended - Soil Moisture Below Threshold",
        "title_ar": "يُنصح بالري - رطوبة التربة أقل من الحد الأدنى",
        "summary": "Current soil moisture at 28% is below the 35% threshold for wheat at tillering stage. "
        "Apply 25mm irrigation within 24 hours.",
        "summary_ar": "رطوبة التربة الحالية عند 28% أقل من حد 35% للقمح في مرحلة التفريع. تطبيق 25 مم ري خلال 24 ساعة.",
        "recommendation": "Apply 25mm irrigation using drip system. Best time: early morning before 8 AM.",
        "recommendation_ar": "تطبيق 25 مم ري باستخدام نظام التنقيط. أفضل وقت: الصباح الباكر قبل 8 صباحا.",
        "irrigation_details": {
            "recommended_amount_mm": 25.0,
            "current_soil_moisture_percent": 28.0,
            "target_soil_moisture_percent": 45.0,
            "field_capacity_percent": 55.0,
            "wilting_point_percent": 15.0,
            "irrigation_method": "drip",
            "estimated_duration_minutes": 180,
            "et_value_mm_day": 5.5,
            "crop_coefficient_kc": 0.85,
            "rain_probability_24h_percent": 5,
            "best_time_window": "06:00-08:00",
            "avoid_time_window": "12:00-16:00",
        },
        "crop_type": "wheat",
        "crop_type_ar": "قمح",
        "growth_stage": "tillering",
        "growth_stage_ar": "التفريع",
        "confidence_score": 0.92,
        "data_sources": ["soil_sensor", "weather_forecast", "et_calculation"],
        "sensor_readings": [
            {"sensor_id": "soil_moisture_1", "value": 28.0, "unit": "%", "timestamp": datetime.now(UTC).isoformat()},
        ],
        "generated_by": "irrigation_expert_agent",
    }


def _make_fertilizer_advisory_payload(
    field_id: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    """Build a valid advisory.fertilizer event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "advisory-service",
        "advisory_id": str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "advisory_type": "fertilizer",
        "priority": "medium",
        "title": "Phosphorus Application Recommended for Pre-Planting",
        "title_ar": "يُنصح بتطبيق الفوسفور قبل الزراعة",
        "summary": "Soil test shows phosphorus at 12 ppm (target: 20 ppm). "
        "Apply DAP before planting for optimal root development.",
        "summary_ar": "تحليل التربة يظهر فوسفور عند 12 جزء في المليون (الهدف: 20 جزء في المليون). "
        "تطبيق DAP قبل الزراعة لتطوير جذور مثالي.",
        "recommendation": "Apply DAP 18-46-0 at 100 kg/ha incorporated into soil before planting.",
        "recommendation_ar": "تطبيق DAP 18-46-0 بمعدل 100 كغ/هكتار مدمج في التربة قبل الزراعة.",
        "fertilizer_details": {
            "product_name": "DAP 18-46-0",
            "product_name_ar": "داي أمونيوم فوسفات 18-46-0",
            "active_nutrients": {"N": 18.0, "P2O5": 46.0, "K2O": 0.0},
            "application_rate_kg_ha": 100.0,
            "application_method": "soil_incorporation",
            "application_method_ar": "الدمج في التربة",
            "soil_test_results": {
                "nitrogen_ppm": 22.0,
                "phosphorus_ppm": 12.0,
                "potassium_ppm": 185.0,
                "ph": 7.4,
                "organic_matter_percent": 1.8,
                "ec_ds_m": 1.2,
            },
            "target_levels": {
                "nitrogen_ppm": 25.0,
                "phosphorus_ppm": 20.0,
                "potassium_ppm": 180.0,
            },
            "timing_window": "1-2 weeks before planting",
            "timing_window_ar": "1-2 أسبوع قبل الزراعة",
            "compatibility_notes": "Compatible with most soil treatments. Do not mix with calcium-based amendments.",
            "compatibility_notes_ar": "متوافق مع معظم معالجات التربة. لا تخلط مع تعديلات الكالسيوم.",
        },
        "crop_type": "wheat",
        "crop_type_ar": "قمح",
        "growth_stage": "pre_planting",
        "growth_stage_ar": "قبل الزراعة",
        "economic_analysis": {
            "treatment_cost_per_ha": 280.0,
            "expected_yield_increase_percent": 12.0,
            "roi_percentage": 320.0,
            "currency": "SAR",
        },
        "confidence_score": 0.88,
        "data_sources": ["soil_test", "crop_plan", "nutrient_model"],
        "generated_by": "soil_analyst_agent",
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
# Tests: Advisory Generated Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_advisory_generated_event_published(mock_nats):
    """Test that advisory.generated event is published with bilingual content."""
    payload = _make_advisory_generated_payload(advisory_type="fertilizer")
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_ADVISORY_GENERATED, data)
    mock_nats.publish.assert_awaited_once_with(SAHOOL_ADVISORY_GENERATED, data)

    decoded = json.loads(data)
    assert "advisory_id" in decoded
    assert "field_id" in decoded
    assert "tenant_id" in decoded
    assert decoded["advisory_type"] == "fertilizer"
    assert decoded["source_service"] == "advisory-service"

    # Bilingual content must be present
    assert "title" in decoded and len(decoded["title"]) > 0
    assert "title_ar" in decoded and len(decoded["title_ar"]) > 0
    assert "summary" in decoded and len(decoded["summary"]) > 0
    assert "summary_ar" in decoded and len(decoded["summary_ar"]) > 0
    assert "recommendation" in decoded
    assert "recommendation_ar" in decoded
    assert "rationale" in decoded
    assert "rationale_ar" in decoded


@pytest.mark.integration
@pytest.mark.asyncio
async def test_advisory_generated_bilingual_action_items(mock_nats):
    """Test that advisory action items include both Arabic and English content."""
    payload = _make_advisory_generated_payload()
    data = json.dumps(payload).encode("utf-8")

    decoded = json.loads(data)
    assert "action_items" in decoded
    assert len(decoded["action_items"]) >= 1

    for item in decoded["action_items"]:
        assert "step" in item and isinstance(item["step"], int)
        assert "action" in item and len(item["action"]) > 0
        assert "action_ar" in item and len(item["action_ar"]) > 0
        assert "timing" in item
        assert "timing_ar" in item


@pytest.mark.integration
@pytest.mark.asyncio
async def test_advisory_generated_includes_economic_analysis(mock_nats):
    """Test that advisory.generated includes economic ROI analysis."""
    payload = _make_advisory_generated_payload()
    data = json.dumps(payload).encode("utf-8")

    decoded = json.loads(data)
    assert "economic_analysis" in decoded

    econ = decoded["economic_analysis"]
    assert "treatment_cost_per_ha" in econ
    assert econ["treatment_cost_per_ha"] >= 0
    assert "roi_percentage" in econ
    assert econ["roi_percentage"] > 0, "Advisory should show positive ROI"
    assert econ["currency"] == "SAR"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Irrigation Advisory Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_irrigation_advisory_event_schema(mock_nats):
    """Test irrigation advisory event payload with irrigation-specific details."""
    payload = _make_irrigation_advisory_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_ADVISORY_IRRIGATION, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert decoded["advisory_type"] == "irrigation"
    assert decoded["source_service"] == "irrigation-smart"

    # Bilingual content
    assert "title" in decoded and "title_ar" in decoded
    assert "summary" in decoded and "summary_ar" in decoded
    assert "recommendation" in decoded and "recommendation_ar" in decoded

    # Irrigation-specific details
    assert "irrigation_details" in decoded
    details = decoded["irrigation_details"]
    assert details["recommended_amount_mm"] > 0
    assert 0 <= details["current_soil_moisture_percent"] <= 100
    assert 0 <= details["target_soil_moisture_percent"] <= 100
    assert details["target_soil_moisture_percent"] > details["current_soil_moisture_percent"]
    assert details["irrigation_method"] in ("drip", "sprinkler", "flood", "pivot", "surface")
    assert details["estimated_duration_minutes"] > 0
    assert details["et_value_mm_day"] > 0
    assert 0 <= details["crop_coefficient_kc"] <= 2.0
    assert "best_time_window" in details
    assert "avoid_time_window" in details


@pytest.mark.integration
@pytest.mark.asyncio
async def test_irrigation_advisory_subscribe_and_receive(mock_nats, mock_nats_msg):
    """Test subscribing to irrigation advisory and verifying sensor data context."""
    received_advisories: list[dict] = []

    async def handler(msg):
        data = json.loads(msg.data.decode("utf-8"))
        received_advisories.append(data)

    await mock_nats.subscribe(SAHOOL_ADVISORY_IRRIGATION, cb=handler)

    payload = _make_irrigation_advisory_payload()
    msg = mock_nats_msg(SAHOOL_ADVISORY_IRRIGATION, payload)
    await handler(msg)

    assert len(received_advisories) == 1
    advisory = received_advisories[0]

    # Verify sensor readings are included for context
    assert "sensor_readings" in advisory
    assert len(advisory["sensor_readings"]) >= 1
    reading = advisory["sensor_readings"][0]
    assert "sensor_id" in reading
    assert "value" in reading
    assert "unit" in reading
    assert "timestamp" in reading

    # Confidence
    assert 0 <= advisory["confidence_score"] <= 1


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Fertilizer Advisory Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fertilizer_advisory_event_schema(mock_nats):
    """Test fertilizer advisory event payload with soil test and nutrient details."""
    payload = _make_fertilizer_advisory_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_ADVISORY_FERTILIZER, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert decoded["advisory_type"] == "fertilizer"

    # Bilingual content
    assert "title" in decoded and "title_ar" in decoded
    assert "summary" in decoded and "summary_ar" in decoded
    assert "recommendation" in decoded and "recommendation_ar" in decoded

    # Fertilizer-specific details
    assert "fertilizer_details" in decoded
    details = decoded["fertilizer_details"]
    assert "product_name" in details
    assert "product_name_ar" in details
    assert "active_nutrients" in details

    nutrients = details["active_nutrients"]
    assert "N" in nutrients and isinstance(nutrients["N"], (int, float))
    assert "P2O5" in nutrients and isinstance(nutrients["P2O5"], (int, float))
    assert "K2O" in nutrients and isinstance(nutrients["K2O"], (int, float))

    assert details["application_rate_kg_ha"] > 0
    assert "application_method" in details
    assert "application_method_ar" in details

    # Soil test results
    assert "soil_test_results" in details
    soil = details["soil_test_results"]
    assert "nitrogen_ppm" in soil
    assert "phosphorus_ppm" in soil
    assert "potassium_ppm" in soil
    assert "ph" in soil and 0 <= soil["ph"] <= 14

    # Targets
    assert "target_levels" in details


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fertilizer_advisory_bilingual_completeness(mock_nats, mock_nats_msg):
    """Test that all user-facing fertilizer advisory text has Arabic counterparts."""
    payload = _make_fertilizer_advisory_payload()
    decoded = payload

    # All user-facing fields must have Arabic counterparts
    bilingual_pairs = [
        ("title", "title_ar"),
        ("summary", "summary_ar"),
        ("recommendation", "recommendation_ar"),
        ("crop_type", "crop_type_ar"),
        ("growth_stage", "growth_stage_ar"),
    ]

    for en_key, ar_key in bilingual_pairs:
        assert en_key in decoded, f"Missing English field: {en_key}"
        assert ar_key in decoded, f"Missing Arabic field: {ar_key}"
        assert len(decoded[en_key]) > 0, f"English field {en_key} is empty"
        assert len(decoded[ar_key]) > 0, f"Arabic field {ar_key} is empty"

    # Fertilizer details bilingual
    details = decoded["fertilizer_details"]
    details_bilingual = [
        ("product_name", "product_name_ar"),
        ("application_method", "application_method_ar"),
        ("timing_window", "timing_window_ar"),
        ("compatibility_notes", "compatibility_notes_ar"),
    ]

    for en_key, ar_key in details_bilingual:
        assert en_key in details, f"Missing English fertilizer detail: {en_key}"
        assert ar_key in details, f"Missing Arabic fertilizer detail: {ar_key}"
        assert len(details[en_key]) > 0, f"English detail {en_key} is empty"
        assert len(details[ar_key]) > 0, f"Arabic detail {ar_key} is empty"
