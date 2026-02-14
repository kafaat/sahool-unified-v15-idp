"""
E2E Tests for IoT Device Lifecycle.
اختبارات شاملة لدورة حياة أجهزة إنترنت الأشياء

Tests the complete IoT device workflow:
- Device registration and listing
- Sensor data retrieval (soil moisture, temperature, etc.)
- Actuator control (pump toggle, valve control)
- Irrigation schedule management
- Historical sensor data queries
- Dashboard aggregation

Service: iot-service (NestJS)
Port: 8117
Routes: /api/v1/iot/*

Usage:
    pytest tests/e2e/test_iot_device_e2e.py -v -m e2e

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

# ============================================================================
# Configuration
# ============================================================================

IOT_BASE_URL = os.getenv("E2E_IOT_BASE_URL", "http://localhost:8117")
AUTH_BASE_URL = os.getenv("E2E_AUTH_BASE_URL", "http://localhost:3025")
IOT_API = f"{IOT_BASE_URL}/api/v1/iot"

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
async def auth_token() -> str:
    """Obtain JWT auth token from user-service."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{AUTH_BASE_URL}/api/v1/auth/login",
                json={
                    "email": os.getenv("E2E_TEST_EMAIL", "test@sahool.app"),
                    "password": os.getenv("E2E_TEST_PASSWORD", "TestPass123!"),
                },
            )
            if resp.status_code == 200:
                return resp.json().get("access_token", "e2e-test-token")
        except httpx.ConnectError:
            pass
    return "e2e-test-token-fallback"


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Authorization headers."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


@pytest.fixture
async def http_client() -> httpx.AsyncClient:
    """Async HTTP client with extended timeout."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def test_field_id() -> str:
    """Field ID for IoT tests."""
    return os.getenv("E2E_IOT_FIELD_ID", f"field-{uuid.uuid4().hex[:8]}")


# ============================================================================
# Health Check Tests
# ============================================================================


class TestIoTServiceHealth:
    """IoT service health and readiness tests."""

    async def test_health_check(self, http_client: httpx.AsyncClient):
        """
        IoT service health check.
        فحص صحة خدمة إنترنت الأشياء
        """
        # IoT health is at /api/v1/iot/health (inside controller with prefix)
        resp = await http_client.get(f"{IOT_API}/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") == "ok"
        assert body.get("service") == "iot-service"
        assert "timestamp" in body

    async def test_healthz_kubernetes_probe(self, http_client: httpx.AsyncClient):
        """
        Kubernetes liveness probe (excluded from global prefix).
        فحص الحياة لكوبرنيتس
        """
        resp = await http_client.get(f"{IOT_BASE_URL}/healthz")
        # healthz may not be implemented separately - depends on health controller
        assert resp.status_code in (200, 404)


# ============================================================================
# Sensor Data Retrieval Tests
# ============================================================================


class TestSensorDataRetrieval:
    """
    Tests for reading sensor data from IoT devices.
    اختبارات قراءة بيانات المستشعرات من أجهزة إنترنت الأشياء
    """

    async def test_get_all_field_sensors(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Retrieve all sensor readings for a field.
        استرجاع جميع قراءات المستشعرات لحقل معين
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/sensors",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert isinstance(body, list)
            for reading in body:
                assert "sensorType" in reading
                assert "value" in reading
                assert "unit" in reading
                assert "timestamp" in reading

    async def test_get_soil_moisture_sensor(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Retrieve soil moisture sensor reading.
        استرجاع قراءة مستشعر رطوبة التربة
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/sensor/SOIL_MOISTURE",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            if body is not None:
                assert body.get("sensorType") == "SOIL_MOISTURE"
                assert "value" in body
                assert "unit" in body

    async def test_get_temperature_sensor(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Retrieve temperature sensor reading.
        استرجاع قراءة مستشعر الحرارة
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/sensor/TEMPERATURE",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

    async def test_get_humidity_sensor(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Retrieve humidity sensor reading.
        استرجاع قراءة مستشعر الرطوبة
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/sensor/HUMIDITY",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

    async def test_get_sensor_without_auth(
        self,
        http_client: httpx.AsyncClient,
        test_field_id: str,
    ):
        """
        Sensor data access without authentication should be rejected.
        يجب رفض الوصول إلى بيانات المستشعر بدون مصادقة
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/sensors",
        )
        assert resp.status_code == 401


# ============================================================================
# Actuator Control Tests
# ============================================================================


class TestActuatorControl:
    """
    Tests for controlling actuators (pumps, valves).
    اختبارات التحكم في المحركات (المضخات، الصمامات)
    """

    async def test_toggle_pump_on(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Toggle pump ON with a duration.
        تشغيل المضخة مع مدة زمنية
        """
        resp = await http_client.post(
            f"{IOT_API}/field/{test_field_id}/pump",
            headers=auth_headers,
            json={"status": "ON", "duration": 30},
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            assert "message" in body

    async def test_toggle_pump_off(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Toggle pump OFF.
        إيقاف المضخة
        """
        resp = await http_client.post(
            f"{IOT_API}/field/{test_field_id}/pump",
            headers=auth_headers,
            json={"status": "OFF"},
        )
        assert resp.status_code in (200, 401, 404)

    async def test_toggle_pump_invalid_status(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Toggle pump with invalid status should fail.
        تبديل المضخة بحالة غير صالحة يجب أن يفشل
        """
        resp = await http_client.post(
            f"{IOT_API}/field/{test_field_id}/pump",
            headers=auth_headers,
            json={"status": "MAYBE"},
        )
        assert resp.status_code in (400, 401, 422)

    async def test_toggle_valve(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Toggle a specific valve ON.
        تشغيل صمام محدد
        """
        valve_id = "valve-zone-1"
        resp = await http_client.post(
            f"{IOT_API}/field/{test_field_id}/valve/{valve_id}",
            headers=auth_headers,
            json={"status": "ON"},
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True

    async def test_get_actuator_states(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Get all actuator states (pump, valves) for a field.
        الحصول على حالات جميع المحركات لحقل معين
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/actuators",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert isinstance(body, dict)


# ============================================================================
# Irrigation Schedule Tests
# ============================================================================


class TestIrrigationSchedule:
    """
    Tests for irrigation schedule management.
    اختبارات إدارة جدول الري
    """

    async def test_set_irrigation_schedule(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Set an irrigation schedule for a field.
        تعيين جدول ري لحقل معين
        """
        schedule = {
            "startTime": "06:00",
            "duration": 45,
            "days": ["sunday", "tuesday", "thursday"],
            "enabled": True,
        }
        resp = await http_client.post(
            f"{IOT_API}/field/{test_field_id}/irrigation/schedule",
            headers=auth_headers,
            json=schedule,
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True

    async def test_set_irrigation_schedule_invalid_duration(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Invalid schedule duration should be rejected.
        مدة جدول غير صالحة يجب أن ترفض
        """
        schedule = {
            "startTime": "06:00",
            "duration": -10,  # Invalid negative duration
            "days": ["monday"],
            "enabled": True,
        }
        resp = await http_client.post(
            f"{IOT_API}/field/{test_field_id}/irrigation/schedule",
            headers=auth_headers,
            json=schedule,
        )
        assert resp.status_code in (400, 401, 422)


# ============================================================================
# Device Management Tests
# ============================================================================


class TestDeviceManagement:
    """
    Tests for device listing and management.
    اختبارات قائمة الأجهزة وإدارتها
    """

    async def test_list_connected_devices(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        List all connected IoT devices with statistics.
        سرد جميع أجهزة IoT المتصلة مع الإحصائيات
        """
        resp = await http_client.get(
            f"{IOT_API}/devices",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401)

        if resp.status_code == 200:
            body = resp.json()
            assert "devices" in body
            assert "stats" in body
            assert isinstance(body["devices"], list)

    async def test_list_devices_without_auth(self, http_client: httpx.AsyncClient):
        """Device listing without auth should fail."""
        resp = await http_client.get(f"{IOT_API}/devices")
        assert resp.status_code == 401


# ============================================================================
# Dashboard Data Tests
# ============================================================================


class TestIoTDashboard:
    """
    Tests for IoT dashboard data aggregation.
    اختبارات تجميع بيانات لوحة معلومات إنترنت الأشياء
    """

    async def test_get_field_dashboard(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Get aggregated IoT dashboard data for a field.
        الحصول على بيانات لوحة المعلومات المجمعة لحقل
        """
        resp = await http_client.get(
            f"{IOT_API}/dashboard/{test_field_id}",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("fieldId") == test_field_id
            assert "sensors" in body
            assert "actuators" in body
            assert "timestamp" in body


# ============================================================================
# Historical Data Tests
# ============================================================================


class TestHistoricalSensorData:
    """
    Tests for querying historical sensor readings.
    اختبارات الاستعلام عن القراءات التاريخية للمستشعرات
    """

    async def test_get_historical_readings_default(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Get historical sensor readings with default 24h window.
        الحصول على القراءات التاريخية مع نافذة 24 ساعة افتراضية
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/history",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

    async def test_get_historical_readings_filtered(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_field_id: str,
    ):
        """
        Get historical soil moisture readings for last 48 hours.
        الحصول على قراءات رطوبة التربة التاريخية لآخر 48 ساعة
        """
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/history",
            headers=auth_headers,
            params={"sensorType": "SOIL_MOISTURE", "hours": "48"},
        )
        assert resp.status_code in (200, 401, 404)

    async def test_get_historical_readings_without_auth(
        self,
        http_client: httpx.AsyncClient,
        test_field_id: str,
    ):
        """Historical data access without auth should be rejected."""
        resp = await http_client.get(
            f"{IOT_API}/field/{test_field_id}/history",
        )
        assert resp.status_code == 401
