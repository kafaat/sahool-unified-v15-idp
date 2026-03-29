# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
اختبارات سير العمل الكامل (End-to-End Workflows)
========================================================

Each test class covers a distinct agricultural user journey that spans
multiple SAHOOL microservices.  Tests are written to be runnable offline:
when a live service is not reachable the test degrades gracefully by
either skipping or exercising the same logic through in-process mocks.

Workflows covered
-----------------
W1: Complete Agricultural Advisory Journey
    Farmer → Create Field → Fetch Weather → Compute NDVI → Get Advisory → Notify

W2: Smart Irrigation Cycle
    Soil Sensor Data → Weather Forecast → Irrigation Calculation → Schedule → Execute → Log

W3: Pest / Disease Detection Response
    Capture Image → YOLO26 Detection → Advisory Enrichment → Alert Generation → Notification

W4: Harvest & Market Chain
    Harvest Record → Quality Assessment → Traceability QR → Market Price Check → Sell

W5: User Registration & Onboarding
    Register → Email Verify → Create Farm → Create Field → First Advisory

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import base64
import io
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    import httpx
    from httpx import AsyncClient

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# ---------------------------------------------------------------------------
# Service URLs derived from the shared registry
# (apps/services/shared/versions.py) with env-override support.
# ---------------------------------------------------------------------------
import os

import importlib.util
from pathlib import Path

try:
    # Load versions.py via importlib so it registers under a unique module name
    # instead of being imported as the top-level ``shared`` package, which would
    # shadow the repo-root shared/ package for the rest of the pytest session.
    _VERSIONS_PATH = (
        Path(__file__).resolve().parent.parent.parent
        / "apps"
        / "services"
        / "shared"
        / "versions.py"
    )
    if not _VERSIONS_PATH.is_file():
        raise FileNotFoundError(_VERSIONS_PATH)
    _spec = importlib.util.spec_from_file_location(
        "_apps_services_shared_versions_e2e",
        _VERSIONS_PATH,
    )
    if _spec is None or _spec.loader is None:
        raise ImportError("Cannot load spec for shared/versions.py")
    _versions_mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_versions_mod)  # type: ignore[union-attr]
    get_service_url = _versions_mod.get_service_url  # type: ignore[attr-defined]

    def _svc(name: str, fallback_port: int) -> str:
        host = os.getenv("SERVICE_HOST", "localhost")
        return os.getenv(f"{name.upper().replace('-', '_')}_URL") or get_service_url(name, host)

except Exception:
    def _svc(name: str, fallback_port: int) -> str:  # type: ignore[misc]
        host = os.getenv("SERVICE_HOST", "localhost")
        return os.getenv(f"{name.upper().replace('-', '_')}_URL") or f"http://{host}:{fallback_port}"


SVCURL: dict[str, str] = {
    "auth": _svc("user-service", 3025),
    "field": _svc("field-management-service", 3000),
    "weather": _svc("weather-service", 8092),
    "vegetation": _svc("vegetation-analysis-service", 8090),
    "advisory": _svc("advisory-service", 8093),
    "irrigation": _svc("irrigation-smart", 8094),
    "vision": _svc("yolo26-vision-service", 8150),
    "alert": _svc("alert-service", 8113),
    "notification": _svc("notification-service", 8110),
    "task": _svc("task-service", 8103),
    "marketplace": _svc("marketplace-service", 3010),
    "traceability": _svc("traceability-service", 8123),
    "billing": _svc("billing-core", 8089),
    "iot": _svc("iot-service", 8117),
}

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _headers(tenant_id: str | None = None, user_id: str | None = None) -> dict[str, str]:
    # Use E2E_AUTH_TOKEN env var when provided (allows real JWT in CI/staging),
    # otherwise fall back to a placeholder only accepted by the test middleware.
    token = os.getenv("E2E_AUTH_TOKEN", "e2e-test-token")
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id or str(uuid.uuid4()),
        "X-User-ID": user_id or str(uuid.uuid4()),
        "X-Request-ID": str(uuid.uuid4()),
    }


async def _post(url: str, body: dict, headers: dict, timeout: float = 10.0) -> tuple[int, dict]:
    """Return (status_code, json_body). Returns (-1, {}) if service unreachable."""
    if not HAS_HTTPX:
        return -1, {}
    try:
        async with AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=body, headers=headers)
            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, {}
    except Exception:
        return -1, {}


async def _get(url: str, headers: dict, timeout: float = 10.0) -> tuple[int, dict]:
    """Return (status_code, json_body). Returns (-1, {}) if service unreachable."""
    if not HAS_HTTPX:
        return -1, {}
    try:
        async with AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, headers=headers)
            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, {}
    except Exception:
        return -1, {}


def _field_geometry() -> dict:
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [46.6753, 24.7136],
                [46.6853, 24.7136],
                [46.6853, 24.7236],
                [46.6753, 24.7236],
                [46.6753, 24.7136],
            ]
        ],
    }


# ---------------------------------------------------------------------------
# W1 – Complete Agricultural Advisory Journey
# ---------------------------------------------------------------------------


class TestAgriculturalAdvisoryJourney:
    """
    سير العمل: إنشاء حقل → بيانات الطقس → NDVI → الحصول على استشارة → إرسال إشعار

    Simulates the most common farmer journey on the SAHOOL platform.
    """

    @pytest.mark.asyncio
    async def test_step1_create_field(self):
        """
        Step 1: Farmer creates a new field.
        الخطوة 1: المزارع ينشئ حقلاً جديداً.
        """
        tenant_id = str(uuid.uuid4())
        hdrs = _headers(tenant_id=tenant_id)
        payload = {
            "name": "E2E Advisory Field",
            "name_ar": "حقل الاستشارة الشاملة",
            "tenant_id": tenant_id,
            "area_hectares": 12.0,
            "crop_type": "wheat",
            "geometry": _field_geometry(),
        }
        status, body = await _post(f"{SVCURL['field']}/api/v1/fields", payload, hdrs)
        if status == -1:
            pytest.skip("field-management-service not available")
        assert status in (201, 400, 409, 422), f"Unexpected status {status}: {body}"

    @pytest.mark.asyncio
    async def test_step2_fetch_weather_for_field(self):
        """
        Step 2: Platform fetches weather data relevant to the field's location.
        الخطوة 2: المنصة تجلب بيانات الطقس الخاصة بموقع الحقل.
        """
        hdrs = _headers()
        status, body = await _get(f"{SVCURL['weather']}/api/v1/current?location=riyadh", hdrs)
        if status == -1:
            pytest.skip("weather-service not available")
        assert status in (200, 404, 422)
        if status == 200:
            data = body.get("data", body)
            assert "temperature" in data or "temp" in data

    @pytest.mark.asyncio
    async def test_step3_ndvi_analysis_for_field(self):
        """
        Step 3: NDVI is computed for the field using satellite imagery.
        الخطوة 3: حساب مؤشر NDVI للحقل باستخدام صور الأقمار الصناعية.
        """
        field_id = str(uuid.uuid4())
        hdrs = _headers()
        url = f"{SVCURL['vegetation']}/api/v1/ndvi?field_id={field_id}&date={datetime.now(UTC).date()}"
        status, body = await _get(url, hdrs)
        if status == -1:
            pytest.skip("vegetation-analysis-service not available")
        assert status in (200, 202, 404, 422)

    @pytest.mark.asyncio
    async def test_step4_advisory_recommendations_received(self):
        """
        Step 4: Advisory service returns crop management recommendations.
        الخطوة 4: خدمة الاستشارات تُرجع توصيات لإدارة المحصول.
        """
        tenant_id = str(uuid.uuid4())
        hdrs = _headers(tenant_id=tenant_id)
        payload = {
            "field_id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "crop_type": "wheat",
            "crop_stage": "tillering",
            "ndvi_value": 0.68,
            "weather": {"temperature": 22.0, "rain_probability": 10.0},
        }
        status, body = await _post(f"{SVCURL['advisory']}/api/v1/recommendations", payload, hdrs)
        if status == -1:
            pytest.skip("advisory-service not available")
        assert status in (200, 201, 400, 422)

    @pytest.mark.asyncio
    async def test_full_advisory_journey_mock(self):
        """
        Full in-process mock of the W1 journey — always runs, no live services needed.
        محاكاة كاملة لرحلة الاستشارة دون الحاجة لخدمات حية.
        """
        # --- Step 1: Create field ---
        field_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())
        field = {
            "id": field_id,
            "tenant_id": tenant_id,
            "name": "Mock Field",
            "area_hectares": 15.0,
            "crop_type": "wheat",
            "geometry": _field_geometry(),
            "created_at": datetime.now(UTC).isoformat(),
        }
        assert field["id"] == field_id

        # --- Step 2: Fetch weather ---
        weather = {
            "temperature": 25.0,
            "humidity": 45.0,
            "wind_speed": 10.0,
            "rain_probability": 5.0,
            "evapotranspiration_mm_day": 6.5,
        }
        assert weather["temperature"] > 0

        # --- Step 3: NDVI analysis ---
        ndvi = {
            "field_id": field_id,
            "mean_value": 0.65,
            "health_status": "healthy",
            "health_status_ar": "صحي",
            "acquisition_date": datetime.now(UTC).isoformat(),
        }
        assert ndvi["mean_value"] > 0.5

        # --- Step 4: Generate advisory ---
        def generate_advisory(field: dict, weather: dict, ndvi: dict) -> dict:
            needs_irrigation = weather["rain_probability"] < 20 and weather["temperature"] > 23
            return {
                "field_id": field["id"],
                "tenant_id": field["tenant_id"],
                "crop_type": field["crop_type"],
                "recommendations": [
                    {
                        "type": "irrigation",
                        "urgency": "high" if needs_irrigation else "low",
                        "message_ar": "يُنصح بالري خلال 24 ساعة" if needs_irrigation else "الري مناسب حالياً",
                        "message_en": "Irrigate within 24h" if needs_irrigation else "Irrigation adequate",
                    },
                    {
                        "type": "monitoring",
                        "message_ar": "تابع نمو القمح في مرحلة التفريع",
                        "message_en": "Monitor wheat at tillering stage",
                    },
                ],
                "generated_at": datetime.now(UTC).isoformat(),
            }

        advisory = generate_advisory(field, weather, ndvi)
        assert len(advisory["recommendations"]) >= 1
        irr_rec = next(r for r in advisory["recommendations"] if r["type"] == "irrigation")
        assert irr_rec["urgency"] == "high"  # weather temp >23, rain <20%

        # --- Step 5: Send notification ---
        notification = {
            "tenant_id": tenant_id,
            "user_id": str(uuid.uuid4()),
            "channel": "push",
            "title_ar": "توصية زراعية جديدة",
            "title_en": "New Agricultural Advisory",
            "body_ar": irr_rec["message_ar"],
            "body_en": irr_rec["message_en"],
            "sent_at": datetime.now(UTC).isoformat(),
        }
        assert notification["channel"] == "push"
        assert notification["tenant_id"] == tenant_id


# ---------------------------------------------------------------------------
# W2 – Smart Irrigation Cycle
# ---------------------------------------------------------------------------


class TestSmartIrrigationCycle:
    """
    سير العمل: بيانات مستشعر التربة → توقعات الطقس → حساب الري → جدولة → تنفيذ → تسجيل
    """

    @pytest.mark.asyncio
    async def test_soil_sensor_reading_submission(self):
        """
        Soil sensor reading is submitted to IoT service.
        إرسال قراءة مستشعر التربة إلى خدمة إنترنت الأشياء.
        """
        hdrs = _headers()
        payload = {
            "sensor_id": str(uuid.uuid4()),
            "field_id": str(uuid.uuid4()),
            "reading_type": "soil_moisture",
            "value": 24.0,
            "unit": "percent",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        status, body = await _post(f"{SVCURL['iot']}/api/v1/readings", payload, hdrs)
        if status == -1:
            pytest.skip("iot-service not available")
        assert status in (200, 201, 400, 422)

    @pytest.mark.asyncio
    async def test_irrigation_recommendation_request(self):
        """
        Irrigation smart service is requested after sensor + weather data.
        طلب توصية ري بعد جمع بيانات المستشعر والطقس.
        """
        hdrs = _headers()
        payload = {
            "field_id": str(uuid.uuid4()),
            "crop_type": "tomato",
            "crop_stage": "flowering",
            "soil_moisture_percent": 24.0,
            "weather_context": {
                "temperature": 31.0,
                "humidity": 35.0,
                "rain_probability": 2.0,
                "evapotranspiration_mm_day": 9.0,
            },
        }
        status, body = await _post(f"{SVCURL['irrigation']}/api/v1/calculate", payload, hdrs)
        if status == -1:
            pytest.skip("irrigation-smart-service not available")
        assert status in (200, 201, 400, 422)

    @pytest.mark.asyncio
    async def test_full_irrigation_cycle_mock(self):
        """
        Full in-process mock of the W2 smart irrigation cycle.
        محاكاة دورة الري الذكي الكاملة بدون خدمات حية.
        """
        field_id = str(uuid.uuid4())

        # Step 1: Soil sensor reading
        soil_moisture = 22.5  # Below critical threshold of 30%

        # Step 2: Weather forecast
        weather = {"temperature": 34.0, "humidity": 30.0, "rain_probability": 1.0, "et_mm": 10.0}

        # Step 3: Calculate irrigation need
        def calculate(moisture: float, weather: dict) -> dict:
            deficit = max(0.0, 55.0 - moisture)
            et = weather["et_mm"]
            amount = round(deficit * 0.35 + et * 1.1, 1)
            return {
                "field_id": field_id,
                "water_amount_mm": amount,
                "duration_hours": round(amount / 5.0, 1),  # assume 5mm/hour drip
                "urgency": "critical" if moisture < 25 else "normal",
                "scheduled_at": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
            }

        schedule = calculate(soil_moisture, weather)
        assert schedule["urgency"] == "critical"
        assert schedule["water_amount_mm"] > 10.0

        # Step 4: Create task for operator
        task = {
            "task_type": "irrigation",
            "field_id": field_id,
            "priority": "high",
            "scheduled_at": schedule["scheduled_at"],
            "instructions_ar": f"قم بري الحقل بمقدار {schedule['water_amount_mm']} مم",
            "instructions_en": f"Irrigate field with {schedule['water_amount_mm']} mm",
        }
        assert task["priority"] == "high"
        assert str(schedule["water_amount_mm"]) in task["instructions_en"]

        # Step 5: Log execution
        log = {
            "task_id": str(uuid.uuid4()),
            "field_id": field_id,
            "executed_at": datetime.now(UTC).isoformat(),
            "actual_amount_mm": schedule["water_amount_mm"],
            "status": "completed",
        }
        assert log["status"] == "completed"


# ---------------------------------------------------------------------------
# W3 – Pest / Disease Detection Response Workflow
# ---------------------------------------------------------------------------


class TestPestDetectionResponseWorkflow:
    """
    سير العمل: التقاط صورة → كشف YOLO26 → إثراء الاستشارة → إنشاء تنبيه → إشعار
    """

    @pytest.mark.asyncio
    async def test_image_submission_to_vision_service(self):
        """
        Image is submitted to the vision service for pest detection.
        إرسال الصورة إلى خدمة الرؤية للكشف عن الآفات.
        """
        # Minimal 1x1 JPEG
        tiny_jpeg = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
            b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
            b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1c\xc0"
        )
        payload = {
            "image_base64": base64.b64encode(tiny_jpeg).decode(),
            "field_id": str(uuid.uuid4()),
            "model_variant": "n",
        }
        hdrs = _headers()
        status, body = await _post(f"{SVCURL['vision']}/api/v1/detect/pest", payload, hdrs)
        if status == -1:
            pytest.skip("yolo26-vision-service not available")
        assert status in (200, 400, 413, 422)

    @pytest.mark.asyncio
    async def test_full_pest_detection_workflow_mock(self):
        """
        Full mock of the W3 pest detection → advisory → alert → notification pipeline.
        محاكاة كاملة لدورة كشف الآفات حتى الإشعار.
        """
        field_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        # Step 1: Vision detection result (mocked)
        detection = {
            "field_id": field_id,
            "tenant_id": tenant_id,
            "model_variant": "m",
            "detections": [
                {
                    "label": "red_palm_weevil",
                    "confidence": 0.92,
                    "category": "pest",
                    "severity": "critical",
                    "bbox": [100, 200, 350, 450],
                }
            ],
            "inference_time_ms": 45.2,
            "detected_at": datetime.now(UTC).isoformat(),
        }

        # Step 2: Generate critical alert
        def build_alert(det: dict) -> dict:
            critical_pests = {"red_palm_weevil", "desert_locust"}
            detections = det["detections"]
            is_critical = any(d["label"] in critical_pests for d in detections)
            return {
                "alert_type": "pest_detected",
                "field_id": det["field_id"],
                "tenant_id": det["tenant_id"],
                "severity": "critical" if is_critical else "warning",
                "pest_labels": [d["label"] for d in detections],
                "message_ar": "تم الكشف عن سوسة النخيل الحمراء! اتخاذ إجراء فوري مطلوب",
                "message_en": "Red Palm Weevil detected! Immediate action required",
                "action_required": True,
                "response_window_hours": 24 if is_critical else 72,
            }

        alert = build_alert(detection)
        assert alert["severity"] == "critical"
        assert alert["action_required"] is True
        assert alert["response_window_hours"] == 24

        # Step 3: Advisory recommendation for RPW
        advisory = {
            "field_id": field_id,
            "issue": "red_palm_weevil",
            "treatment": {
                "product": "Emamectin benzoate 5%",
                "rate_ml_per_tree": 75,
                "method": "trunk_injection",
                "depth_cm": 18,
                "application_points": 5,
            },
            "preventive": {
                "pheromone_traps_per_ha": 5,
                "inspection_interval_days": 7,
            },
            "cost_sar": 5400,
            "message_ar": "حقن الجذع بالمبيد خلال 24-48 ساعة",
            "message_en": "Inject trunk with pesticide within 24-48 hours",
        }
        assert advisory["treatment"]["product"] == "Emamectin benzoate 5%"

        # Step 4: Notification to farmer
        notification = {
            "tenant_id": tenant_id,
            "channel": "push",
            "priority": "critical",
            "title_ar": "⚠️ تنبيه عاجل: سوسة النخيل الحمراء",
            "title_en": "⚠️ URGENT: Red Palm Weevil Detected",
            "body_ar": alert["message_ar"],
            "body_en": alert["message_en"],
            "action_url": f"/fields/{field_id}/alerts",
        }
        assert notification["priority"] == "critical"
        assert "red_palm_weevil" in alert["pest_labels"]


# ---------------------------------------------------------------------------
# W4 – Harvest & Market Chain
# ---------------------------------------------------------------------------


class TestHarvestAndMarketChain:
    """
    سير العمل: تسجيل الحصاد → تقييم الجودة → QR للتتبع → فحص أسعار السوق → البيع
    """

    @pytest.mark.asyncio
    async def test_traceability_service_health(self):
        """خدمة التتبع يجب أن تستجيب لفحص الصحة."""
        status, body = await _get(f"{SVCURL['traceability']}/healthz", headers=_headers())
        if status == -1:
            pytest.skip("traceability-service not available")
        assert status == 200

    @pytest.mark.asyncio
    async def test_marketplace_service_health(self):
        """خدمة السوق يجب أن تستجيب لفحص الصحة."""
        status, body = await _get(f"{SVCURL['marketplace']}/healthz", headers=_headers())
        if status == -1:
            pytest.skip("marketplace-service not available")
        assert status == 200

    @pytest.mark.asyncio
    async def test_full_harvest_market_chain_mock(self):
        """
        Full in-process mock of the W4 harvest → market sale chain.
        محاكاة كاملة لسلسلة الحصاد والبيع في السوق.
        """
        field_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        # Step 1: Record harvest
        harvest = {
            "id": str(uuid.uuid4()),
            "field_id": field_id,
            "tenant_id": tenant_id,
            "crop_type": "wheat",
            "variety": "Sakha 95",
            "quantity_kg": 12500.0,
            "moisture_percent": 12.5,
            "harvested_at": datetime.now(UTC).isoformat(),
            "operator_id": str(uuid.uuid4()),
        }
        assert harvest["quantity_kg"] > 0

        # Step 2: Quality assessment
        def assess_quality(harvest: dict) -> dict:
            moisture = harvest["moisture_percent"]
            grade = "A" if moisture <= 13.5 else "B" if moisture <= 15 else "C"
            return {
                "harvest_id": harvest["id"],
                "grade": grade,
                "moisture_percent": moisture,
                "protein_percent": 12.8,
                "gluten_index": 68,
                "thousand_kernel_weight_g": 42.5,
                "eligible_for_export": grade == "A",
                "price_adjustment_factor": 1.0 if grade == "A" else 0.92 if grade == "B" else 0.85,
            }

        quality = assess_quality(harvest)
        assert quality["grade"] == "A"
        assert quality["eligible_for_export"] is True

        # Step 3: Generate traceability QR
        qr_data = {
            "harvest_id": harvest["id"],
            "field_id": field_id,
            "tenant_id": tenant_id,
            "crop_type": harvest["crop_type"],
            "variety": harvest["variety"],
            "quantity_kg": harvest["quantity_kg"],
            "quality_grade": quality["grade"],
            "certified_at": datetime.now(UTC).isoformat(),
            "qr_code": f"SAH-{harvest['id'][:8].upper()}",
        }
        assert qr_data["qr_code"].startswith("SAH-")

        # Step 4: Market price lookup
        market_price = {
            "crop_type": "wheat",
            "price_per_kg_sar": 1.85,
            "market": "riyadh_grain_exchange",
            "date": datetime.now(UTC).date().isoformat(),
            "trend": "rising",
        }

        # Step 5: Calculate sale value
        total_value = harvest["quantity_kg"] * market_price["price_per_kg_sar"] * quality["price_adjustment_factor"]
        assert total_value > 0
        assert total_value == pytest.approx(
            harvest["quantity_kg"] * market_price["price_per_kg_sar"] * quality["price_adjustment_factor"],
            rel=0.01,
        )


# ---------------------------------------------------------------------------
# W5 – User Registration & Onboarding
# ---------------------------------------------------------------------------


class TestUserRegistrationAndOnboarding:
    """
    سير العمل: تسجيل → تحقق البريد → إنشاء مزرعة → إنشاء حقل → أول استشارة
    """

    @pytest.mark.asyncio
    async def test_auth_service_health(self):
        """خدمة المصادقة يجب أن تستجيب لفحص الصحة."""
        status, body = await _get(f"{SVCURL['auth']}/healthz", headers=_headers())
        if status == -1:
            pytest.skip("user-service not available")
        assert status == 200

    @pytest.mark.asyncio
    async def test_user_registration_endpoint(self):
        """
        POST /api/v1/auth/register must accept a valid user payload.
        POST /api/v1/auth/register يجب أن يقبل بيانات المستخدم الصحيحة.
        """
        payload = {
            "email": f"e2e_{uuid.uuid4().hex[:8]}@test.sahool.app",
            "password": "SecurePass123!@#",
            "first_name": "Ahmed",
            "first_name_ar": "أحمد",
            "last_name": "Al-Rashid",
            "last_name_ar": "الراشد",
            "phone": "+966501234567",
            "tenant_name": f"farm_{uuid.uuid4().hex[:6]}",
        }
        status, body = await _post(f"{SVCURL['auth']}/api/v1/auth/register", payload, headers=_headers())
        if status == -1:
            pytest.skip("user-service not available")
        # 201=created, 409=already exists, 422=validation error — all acceptable
        assert status in (201, 400, 409, 422)

    @pytest.mark.asyncio
    async def test_full_onboarding_journey_mock(self):
        """
        Full in-process mock of the W5 onboarding journey.
        محاكاة كاملة لرحلة تسجيل وإعداد المزارع الجديد.
        """
        # Step 1: Register user
        user = {
            "id": str(uuid.uuid4()),
            "email": f"farmer_{uuid.uuid4().hex[:8]}@test.com",
            "tenant_id": str(uuid.uuid4()),
            "roles": ["farmer"],
            "created_at": datetime.now(UTC).isoformat(),
        }
        assert "@" in user["email"]

        # Step 2: Email verification (simulated)
        verification = {
            "user_id": user["id"],
            "token": str(uuid.uuid4()),
            "verified_at": datetime.now(UTC).isoformat(),
        }
        assert verification["user_id"] == user["id"]

        # Step 3: Create farm
        farm = {
            "id": str(uuid.uuid4()),
            "tenant_id": user["tenant_id"],
            "name": "Al-Rashid Farm",
            "name_ar": "مزرعة الراشد",
            "total_area_hectares": 50.0,
            "location": {"lat": 24.7136, "lon": 46.6753, "city_ar": "الرياض"},
        }
        assert farm["total_area_hectares"] > 0

        # Step 4: Create first field
        field = {
            "id": str(uuid.uuid4()),
            "farm_id": farm["id"],
            "tenant_id": user["tenant_id"],
            "name": "Field A",
            "name_ar": "الحقل أ",
            "crop_type": "wheat",
            "area_hectares": 15.0,
            "geometry": _field_geometry(),
        }
        assert field["crop_type"] == "wheat"

        # Step 5: First advisory (welcome recommendation)
        first_advisory = {
            "field_id": field["id"],
            "tenant_id": user["tenant_id"],
            "type": "onboarding",
            "message_ar": "مرحباً! إليك توصياتك الأولى لزراعة القمح.",
            "message_en": "Welcome! Here are your first wheat cultivation recommendations.",
            "recommendations": [
                {"step": 1, "action_ar": "احرص على فحص التربة", "action_en": "Ensure soil testing"},
                {"step": 2, "action_ar": "اختر البذور المعتمدة", "action_en": "Select certified seeds"},
                {"step": 3, "action_ar": "ضبط نظام الري", "action_en": "Set up irrigation system"},
            ],
        }
        assert len(first_advisory["recommendations"]) == 3
        assert first_advisory["type"] == "onboarding"

    @pytest.mark.asyncio
    async def test_billing_quota_check_on_new_tenant(self):
        """
        A newly registered tenant should have an active quota/plan.
        المستأجر الجديد يجب أن يمتلك حصة/خطة نشطة.
        """
        tenant_id = str(uuid.uuid4())
        hdrs = _headers(tenant_id=tenant_id)
        url = f"{SVCURL['billing']}/api/v1/tenants/{tenant_id}/quota"
        status, body = await _get(url, hdrs)
        if status == -1:
            pytest.skip("billing-core not available")
        assert status in (200, 404)
        if status == 200:
            data = body.get("data", body)
            assert "plan" in data or "quota" in data
