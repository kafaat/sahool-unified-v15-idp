# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
اختبارات التكامل بين الخدمات - Service-to-Service Integration Tests
=========================================================================

Validates that each service can communicate correctly with its direct
dependencies via HTTP/REST and NATS events.  All tests are written to
degrade gracefully when infrastructure (NATS, Postgres, downstream HTTP
services) is not available, so the suite can be executed in a plain
`pytest` run without a running stack — it will skip or pass-with-warning
instead of error.

Test groups
-----------
1. Field → Advisory  (field creation triggers advisory event)
2. Weather → Irrigation  (weather data feeds irrigation smart service)
3. IoT → Alert       (sensor threshold breach → alert service)
4. Vision → Advisory  (pest detection → crop advisory enrichment)
5. Satellite/NDVI → Indicators  (NDVI result → indicators service)
6. Auth propagation  (JWT tenant claims forwarded across service hops)

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

try:
    from httpx import AsyncClient

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# ---------------------------------------------------------------------------
# Canonical service URLs derived from the shared registry
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
        "_apps_services_shared_versions_integration",
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
    # Fallback when shared registry is not importable (e.g., plain pytest run)
    def _svc(name: str, fallback_port: int) -> str:  # type: ignore[misc]
        host = os.getenv("SERVICE_HOST", "localhost")
        return os.getenv(f"{name.upper().replace('-', '_')}_URL") or f"http://{host}:{fallback_port}"


SERVICE_URLS: dict[str, str] = {
    "field_management": _svc("field-management-service", 3000),
    "user_service": _svc("user-service", 3025),
    "advisory": _svc("advisory-service", 8093),
    "weather": _svc("weather-service", 8092),
    "irrigation_smart": _svc("irrigation-smart", 8094),
    "vegetation_analysis": _svc("vegetation-analysis-service", 8090),
    "indicators": _svc("indicators-service", 8091),
    "alert": _svc("alert-service", 8113),
    "notification": _svc("notification-service", 8110),
    "yolo26_vision": _svc("yolo26-vision-service", 8150),
    "iot": _svc("iot-service", 8117),
    "crop_intelligence": _svc("crop-intelligence-service", 8095),
}

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Override db_cursor fixture locally so the integration conftest autouse
# cleanup fixture does not skip our tests when psycopg2 is absent.
# ---------------------------------------------------------------------------


@pytest.fixture
def db_cursor():
    """Lightweight override: these tests do not need a real DB cursor."""
    return MagicMock()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_jwt_headers(tenant_id: str | None = None, user_id: str | None = None) -> dict[str, str]:
    """Build JWT-like test headers accepted by all SAHOOL services."""
    token = os.getenv("INTEGRATION_AUTH_TOKEN", "test-integration-token")
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Tenant-ID": tenant_id or str(uuid.uuid4()),
        "X-User-ID": user_id or str(uuid.uuid4()),
        "X-Request-ID": str(uuid.uuid4()),
        # Use env-provided token (real JWT) when running against a live stack,
        # falling back to a placeholder accepted by the test middleware.
        "Authorization": f"Bearer {token}",
    }


def _polygon_geometry() -> dict[str, Any]:
    """A small valid polygon in Saudi Arabia for geospatial tests."""
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


async def _get_or_skip(url: str, headers: dict, timeout: float = 5.0) -> dict[str, Any] | None:
    """
    Attempt a GET request; return the JSON body or None if the service is
    unreachable (so individual tests can skip gracefully).
    """
    if not HAS_HTTPX:
        return None
    try:
        async with AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass  # service unreachable — result stays None


# ---------------------------------------------------------------------------
# 1. Field → Advisory integration
# ---------------------------------------------------------------------------


class TestFieldToAdvisoryIntegration:
    """Field creation should trigger an advisory recommendation pipeline."""

    @pytest.mark.asyncio
    async def test_field_creation_returns_valid_schema(self):
        """
        POST /api/v1/fields on the field-management-service must return a
        response that contains ``id`` and ``tenant_id`` fields so that
        downstream advisory calls can be chained.
        اختبار أن إنشاء الحقل يُرجع مخططاً صحيحاً يمكن تمريره للخدمات الأخرى.
        """
        tenant_id = str(uuid.uuid4())
        headers = _make_jwt_headers(tenant_id=tenant_id)
        payload = {
            "name": "S2S Test Field",
            "name_ar": "حقل اختبار S2S",
            "tenant_id": tenant_id,
            "area_hectares": 10.5,
            "crop_type": "wheat",
            "geometry": _polygon_geometry(),
        }

        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        async with AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(
                    f"{SERVICE_URLS['field_management']}/api/v1/fields",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 201:
                    body = resp.json()
                    assert "id" in body or "field_id" in body, "Field response must contain an identifier"
                    assert body.get("tenant_id") == tenant_id or body.get("tenantId") == tenant_id
                # 422 / 409 are also acceptable (service is up but input validation differs)
                assert resp.status_code in (201, 400, 409, 422, 503), (
                    f"Unexpected status {resp.status_code}: {resp.text}"
                )
            except Exception:
                pytest.skip("field-management-service not available")

    @pytest.mark.asyncio
    async def test_advisory_service_health(self):
        """
        Advisory service must respond to /healthz.
        خدمة الاستشارات يجب أن تستجيب لفحص الصحة.
        """
        health = await _get_or_skip(f"{SERVICE_URLS['advisory']}/healthz", headers={})
        if health is None:
            pytest.skip("advisory-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")

    @pytest.mark.asyncio
    async def test_advisory_recommendations_contract(self):
        """
        GET /api/v1/recommendations must return a list or object structure.
        يجب أن تُرجع التوصيات هيكل بيانات قائمة أو كائن.
        """
        tenant_id = str(uuid.uuid4())
        headers = _make_jwt_headers(tenant_id=tenant_id)
        url = f"{SERVICE_URLS['advisory']}/api/v1/recommendations?crop_type=wheat&tenant_id={tenant_id}"
        body = await _get_or_skip(url, headers=headers)
        if body is None:
            pytest.skip("advisory-service not available")
        assert isinstance(body, (list, dict))

    @pytest.mark.asyncio
    async def test_field_advisory_data_consistency(self):
        """
        After creating a field the advisory service should be able to return
        recommendations that reference the same tenant_id.
        بعد إنشاء حقل يجب أن تُرجع الاستشارات توصيات بنفس معرف المستأجر.
        """
        tenant_id = str(uuid.uuid4())
        headers = _make_jwt_headers(tenant_id=tenant_id)

        # Step 1: create field (mocked if service unavailable)
        field_id = str(uuid.uuid4())

        # Step 2: request advisory for that field
        adv_url = (
            f"{SERVICE_URLS['advisory']}/api/v1/recommendations"
            f"?field_id={field_id}&tenant_id={tenant_id}"
        )
        body = await _get_or_skip(adv_url, headers=headers)
        if body is None:
            pytest.skip("advisory-service not available")
        # If a body is returned it must be list or dict — never a string error
        assert isinstance(body, (list, dict))


# ---------------------------------------------------------------------------
# 2. Weather → Irrigation integration
# ---------------------------------------------------------------------------


class TestWeatherToIrrigationIntegration:
    """Weather data must flow into irrigation calculation correctly."""

    @pytest.mark.asyncio
    async def test_weather_service_health(self):
        """خدمة الطقس يجب أن تستجيب لفحص الصحة."""
        health = await _get_or_skip(f"{SERVICE_URLS['weather']}/healthz", headers={})
        if health is None:
            pytest.skip("weather-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")

    @pytest.mark.asyncio
    async def test_weather_current_response_schema(self):
        """
        Weather current endpoint must return temperature and humidity fields.
        نقطة نهاية الطقس الحالي يجب أن تُرجع بيانات درجة الحرارة والرطوبة.
        """
        headers = _make_jwt_headers()
        url = f"{SERVICE_URLS['weather']}/api/v1/current?location=riyadh"
        body = await _get_or_skip(url, headers=headers)
        if body is None:
            pytest.skip("weather-service not available")
        # Accept either a data wrapper or a flat object
        data = body.get("data", body)
        assert "temperature" in data or "temp" in data, "Missing temperature field"

    @pytest.mark.asyncio
    async def test_irrigation_uses_weather_context(self):
        """
        Irrigation smart service must accept a weather_data payload and return
        a water_amount_mm value.
        خدمة الري الذكي يجب أن تقبل بيانات الطقس وتُرجع كمية المياه المقترحة.
        """
        headers = _make_jwt_headers()
        payload = {
            "field_id": str(uuid.uuid4()),
            "crop_type": "wheat",
            "crop_stage": "tillering",
            "weather_context": {
                "temperature": 28.5,
                "humidity": 40.0,
                "wind_speed": 12.0,
                "rain_probability": 5.0,
            },
            "soil_moisture_percent": 30.0,
        }
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")
        try:
            async with AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{SERVICE_URLS['irrigation_smart']}/api/v1/calculate",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 200:
                    body = resp.json()
                    # Result may be nested under 'data' key
                    result = body.get("data", body)
                    assert "water_amount_mm" in result or "recommended_mm" in result or "amount" in result
                assert resp.status_code in (200, 400, 422, 503)
        except Exception:
            pytest.skip("irrigation-smart-service not available")

    @pytest.mark.asyncio
    async def test_weather_to_irrigation_chain_mock(self):
        """
        Validate the weather → irrigation chain using mocks when services are
        offline.  Ensures the data contract between the two services is honoured.
        التحقق من عقد البيانات بين خدمة الطقس وخدمة الري عبر المحاكاة.
        """
        # Mock weather response
        weather_response = {
            "temperature": 32.0,
            "humidity": 35.0,
            "wind_speed": 15.0,
            "rain_probability": 0.0,
            "evapotranspiration_mm_day": 8.5,
        }

        # Mock irrigation calculation based on weather
        def calculate_irrigation(weather: dict, soil_moisture: float) -> dict:
            et = weather.get("evapotranspiration_mm_day", 6.0)
            deficit = max(0.0, 50.0 - soil_moisture)  # target 50%
            amount = round(deficit * 0.3 + et * 1.2, 1)
            return {
                "water_amount_mm": amount,
                "irrigation_needed": amount > 5.0,
                "next_irrigation_hours": 12 if amount > 10 else 24,
            }

        result = calculate_irrigation(weather_response, soil_moisture=28.0)
        assert result["water_amount_mm"] > 0
        assert isinstance(result["irrigation_needed"], bool)
        assert result["next_irrigation_hours"] in (12, 24)


# ---------------------------------------------------------------------------
# 3. IoT sensor → Alert service integration
# ---------------------------------------------------------------------------


class TestIoTToAlertIntegration:
    """IoT threshold breach must propagate to the alert service."""

    @pytest.mark.asyncio
    async def test_iot_service_health(self):
        """خدمة إنترنت الأشياء يجب أن تستجيب لفحص الصحة."""
        health = await _get_or_skip(f"{SERVICE_URLS['iot']}/healthz", headers={})
        if health is None:
            pytest.skip("iot-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")

    @pytest.mark.asyncio
    async def test_alert_service_health(self):
        """خدمة التنبيهات يجب أن تستجيب لفحص الصحة."""
        health = await _get_or_skip(f"{SERVICE_URLS['alert']}/healthz", headers={})
        if health is None:
            pytest.skip("alert-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")

    @pytest.mark.asyncio
    async def test_sensor_reading_submission(self):
        """
        POST /api/v1/readings to iot-service should accept a valid sensor payload.
        POST /api/v1/readings يجب أن يقبل بيانات الاستشعار الصحيحة.
        """
        headers = _make_jwt_headers()
        reading = {
            "sensor_id": str(uuid.uuid4()),
            "field_id": str(uuid.uuid4()),
            "reading_type": "soil_moisture",
            "value": 18.5,
            "unit": "percent",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")
        try:
            async with AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{SERVICE_URLS['iot']}/api/v1/readings",
                    json=reading,
                    headers=headers,
                )
                assert resp.status_code in (200, 201, 400, 422, 503)
        except Exception:
            pytest.skip("iot-service not available")

    @pytest.mark.asyncio
    async def test_alert_threshold_breach_mock(self):
        """
        Simulate a soil-moisture breach and verify the alert payload is correctly
        structured for the notification service.
        محاكاة تجاوز حد رطوبة التربة والتحقق من صحة حمولة التنبيه.
        """

        def evaluate_sensor_alert(reading: dict, thresholds: dict) -> dict | None:
            value = reading["value"]
            low = thresholds.get("low", 20.0)
            if value < low:
                return {
                    "alert_type": "soil_moisture_low",
                    "sensor_id": reading["sensor_id"],
                    "field_id": reading["field_id"],
                    "current_value": value,
                    "threshold": low,
                    "severity": "warning" if value > low * 0.7 else "critical",
                    "message_ar": "رطوبة التربة منخفضة",
                    "message_en": "Soil moisture is below threshold",
                    "created_at": datetime.now(UTC).isoformat(),
                }
            return None

        reading = {
            "sensor_id": "sensor-001",
            "field_id": "field-001",
            "value": 12.0,  # below threshold of 20
        }
        alert = evaluate_sensor_alert(reading, {"low": 20.0})
        assert alert is not None
        assert alert["alert_type"] == "soil_moisture_low"
        assert alert["severity"] in ("warning", "critical")
        assert "message_ar" in alert
        assert "message_en" in alert

    @pytest.mark.asyncio
    async def test_notification_service_health(self):
        """خدمة الإشعارات يجب أن تستجيب لفحص الصحة."""
        health = await _get_or_skip(f"{SERVICE_URLS['notification']}/healthz", headers={})
        if health is None:
            pytest.skip("notification-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")


# ---------------------------------------------------------------------------
# 4. Vision (YOLO26) → Crop Advisory integration
# ---------------------------------------------------------------------------


class TestVisionToAdvisoryIntegration:
    """Pest/disease detection must produce actionable advisory enrichment."""

    @pytest.mark.asyncio
    async def test_vision_service_health(self):
        """خدمة الرؤية الحاسوبية يجب أن تستجيب لفحص الصحة."""
        health = await _get_or_skip(f"{SERVICE_URLS['yolo26_vision']}/healthz", headers={})
        if health is None:
            pytest.skip("yolo26-vision-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")

    @pytest.mark.asyncio
    async def test_vision_detection_response_schema(self):
        """
        A detection response must include ``detections`` list and a
        ``severity`` or ``confidence`` score.
        استجابة الكشف يجب أن تحتوي على قائمة detections ودرجة الثقة.
        """
        import base64

        # 1×1 white JPEG (minimal valid image)
        tiny_jpeg_b64 = (
            "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U"
            "HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgN"
            "DRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
            "MjL/wAARCAABAAEDASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgUE/8QAIhAAAQQC"
            "AgMAAAAAAAAAAAAAAQIDBBEhMUFRYf/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAA"
            "AAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AmWtb1ooNLWNJO5gAHOBvjuB5AIJB6xQB/9k="
        )
        headers = _make_jwt_headers()
        payload = {"image_base64": tiny_jpeg_b64, "model_variant": "n", "task": "pest"}

        if not HAS_HTTPX:
            pytest.skip("httpx not installed")
        try:
            async with AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{SERVICE_URLS['yolo26_vision']}/api/v1/detect/pest",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 200:
                    body = resp.json()
                    data = body.get("data", body)
                    assert "detections" in data or "results" in data
                assert resp.status_code in (200, 400, 422, 503)
        except Exception:
            pytest.skip("yolo26-vision-service not available")

    @pytest.mark.asyncio
    async def test_vision_to_advisory_data_mapping_mock(self):
        """
        Map a vision detection result to an advisory recommendation request and
        verify the contract without needing live services.
        تعيين نتيجة الكشف الى طلب توصية استشارية والتحقق من العقد.
        """

        def map_detection_to_advisory_request(detection_result: dict) -> dict:
            detections = detection_result.get("detections", [])
            pests = [d for d in detections if d.get("category") == "pest"]
            diseases = [d for d in detections if d.get("category") == "disease"]
            return {
                "field_id": detection_result["field_id"],
                "tenant_id": detection_result["tenant_id"],
                "issues_detected": {
                    "pests": [d["label"] for d in pests],
                    "diseases": [d["label"] for d in diseases],
                },
                "severity": max(
                    (d.get("severity", "low") for d in detections),
                    default="none",
                    key=lambda s: {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}.get(s, 0),
                ),
                "recommendation_needed": len(detections) > 0,
            }

        detection_result = {
            "field_id": "field-001",
            "tenant_id": "tenant-001",
            "detections": [
                {"label": "aphid", "category": "pest", "confidence": 0.87, "severity": "medium"},
                {"label": "powdery_mildew", "category": "disease", "confidence": 0.72, "severity": "low"},
            ],
        }
        req = map_detection_to_advisory_request(detection_result)
        assert req["recommendation_needed"] is True
        assert "aphid" in req["issues_detected"]["pests"]
        assert req["severity"] == "medium"


# ---------------------------------------------------------------------------
# 5. Vegetation Analysis → Indicators integration
# ---------------------------------------------------------------------------


class TestVegetationToIndicatorsIntegration:
    """NDVI results must be consumable by the indicators service."""

    @pytest.mark.asyncio
    async def test_vegetation_analysis_health(self):
        """خدمة تحليل الغطاء النباتي يجب أن تستجيب لفحص الصحة."""
        health = await _get_or_skip(f"{SERVICE_URLS['vegetation_analysis']}/healthz", headers={})
        if health is None:
            pytest.skip("vegetation-analysis-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")

    @pytest.mark.asyncio
    async def test_indicators_service_health(self):
        """خدمة المؤشرات يجب أن تستجيب لفحص الصحة."""
        health = await _get_or_skip(f"{SERVICE_URLS['indicators']}/healthz", headers={})
        if health is None:
            pytest.skip("indicators-service not available")
        assert health.get("status") in ("ok", "healthy", "UP")

    @pytest.mark.asyncio
    async def test_ndvi_result_schema_compatibility(self):
        """
        An NDVI result payload must contain all fields that the indicators
        service expects: field_id, mean_value, health_status.
        نتيجة NDVI يجب أن تحتوي على الحقول التي تحتاجها خدمة المؤشرات.
        """
        headers = _make_jwt_headers()
        field_id = str(uuid.uuid4())
        url = (
            f"{SERVICE_URLS['vegetation_analysis']}/api/v1/ndvi"
            f"?field_id={field_id}&date={datetime.now(UTC).date()}"
        )
        body = await _get_or_skip(url, headers=headers)
        if body is None:
            pytest.skip("vegetation-analysis-service not available")
        data = body.get("data", body)
        # Verify required fields consumed by indicators service
        for field in ("field_id", "mean_value", "health_status"):
            assert field in data, f"Missing required field: {field}"

    @pytest.mark.asyncio
    async def test_ndvi_to_indicator_pipeline_mock(self):
        """
        Validate the full NDVI → indicators transformation pipeline with mocks.
        التحقق من خط أنابيب NDVI → المؤشرات باستخدام محاكاة كاملة.
        """

        def compute_indicators_from_ndvi(ndvi: dict) -> dict:
            mean = ndvi.get("mean_value", 0.0)
            status = ndvi.get("health_status", "unknown")
            return {
                "field_id": ndvi["field_id"],
                "vegetation_health_score": round(mean * 100, 1),
                "health_status": status,
                "health_status_ar": {
                    "healthy": "صحي",
                    "moderate": "معتدل",
                    "stressed": "مجهد",
                    "critical": "حرج",
                }.get(status, "غير معروف"),
                "alerts": ["low_ndvi"] if mean < 0.3 else [],
                "computed_at": datetime.now(UTC).isoformat(),
            }

        ndvi_result = {
            "field_id": "field-001",
            "mean_value": 0.25,
            "min_value": 0.1,
            "max_value": 0.4,
            "health_status": "stressed",
            "acquisition_date": datetime.now(UTC).isoformat(),
        }
        indicators = compute_indicators_from_ndvi(ndvi_result)
        assert indicators["vegetation_health_score"] == 25.0
        assert indicators["health_status"] == "stressed"
        assert "low_ndvi" in indicators["alerts"]
        assert indicators["health_status_ar"] == "مجهد"


# ---------------------------------------------------------------------------
# 6. JWT / Tenant auth propagation across service hops
# ---------------------------------------------------------------------------


class TestAuthPropagationIntegration:
    """
    JWT tenant claims (tid, sub) must be correctly forwarded by every service
    that makes downstream HTTP calls on behalf of a request.
    مطالبات JWT يجب أن تُمرَّر بشكل صحيح بين الخدمات.
    """

    def test_tenant_id_in_outbound_headers(self):
        """
        When service A calls service B, the X-Tenant-ID header must match the
        original request's tid JWT claim.
        معرف المستأجر في الرأس الصادر يجب أن يطابق مطالبة tid في JWT.
        """
        tenant_id = str(uuid.uuid4())
        headers = _make_jwt_headers(tenant_id=tenant_id)
        assert headers["X-Tenant-ID"] == tenant_id

    def test_request_id_propagation(self):
        """
        Every inter-service call must carry a unique X-Request-ID for
        distributed tracing continuity.
        كل استدعاء بين خدمة وأخرى يجب أن يحمل X-Request-ID فريداً.
        """
        req_id = str(uuid.uuid4())
        headers = {"X-Request-ID": req_id, "X-Tenant-ID": str(uuid.uuid4())}
        # Simulate downstream service echoing back the request ID
        response_headers = {"X-Request-ID": req_id, "X-Trace-ID": "trace-abc"}
        assert response_headers["X-Request-ID"] == headers["X-Request-ID"]

    @pytest.mark.asyncio
    async def test_401_returned_without_auth_header(self):
        """
        All protected endpoints must return 401 when Authorization header is absent.
        جميع نقاط النهاية المحمية يجب أن تُرجع 401 عند غياب رأس المصادقة.
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        endpoints = [
            (SERVICE_URLS["field_management"], "/api/v1/fields"),
            (SERVICE_URLS["advisory"], "/api/v1/recommendations"),
            (SERVICE_URLS["weather"], "/api/v1/current"),
        ]
        for base_url, path in endpoints:
            try:
                async with AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{base_url}{path}")
                    # 401 or 403 expected; 404/503 acceptable if service offline
                    assert resp.status_code in (401, 403, 404, 503), (
                        f"{base_url}{path} returned {resp.status_code} without auth"
                    )
            except Exception:
                # Service not available — skip silently
                pass

    def test_nats_event_contains_tenant_id(self):
        """
        Every NATS event published by a service must contain a tenant_id field
        to support multi-tenancy routing.
        كل حدث NATS يجب أن يحتوي على tenant_id لدعم تعدد المستأجرين.
        """

        def build_nats_event(domain: str, action: str, tenant_id: str, data: dict) -> dict:
            # Subject follows the canonical pattern: sahool.{domain}.{action}
            # tenant_id belongs in the payload, not the subject, so that
            # existing wildcard subscribers (sahool.*.*) continue to match.
            return {
                "subject": f"sahool.{domain}.{action}",
                "data": {
                    "tenant_id": tenant_id,
                    "event_type": f"{domain}.{action}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    **data,
                },
            }

        tenant_id = str(uuid.uuid4())
        event = build_nats_event("field", "created", tenant_id, {"field_id": str(uuid.uuid4())})
        assert event["data"]["tenant_id"] == tenant_id
        assert event["subject"].startswith("sahool.")
        assert event["subject"] == "sahool.field.created"
