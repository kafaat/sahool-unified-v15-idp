"""
Comprehensive IoT Gateway API Tests
Tests all FastAPI endpoints including health checks, sensor readings, device management
"""

import sys
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Mock NATS before importing main
sys.modules["nats"] = MagicMock()
sys.modules["nats.aio"] = MagicMock()
sys.modules["nats.aio.client"] = MagicMock()

# Mock shared middleware before importing main
sys.modules["shared.middleware"] = MagicMock()
sys.modules["shared.observability.middleware"] = MagicMock()
sys.modules["shared.errors_py"] = MagicMock()

from apps.services.iot_gateway.src.main import app
from apps.services.iot_gateway.src.registry import DeviceRegistry, DeviceStatus


@pytest.fixture
def test_client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_registry():
    """Create mock device registry"""
    registry = DeviceRegistry()
    # Register test devices
    registry.register(
        device_id="test_device_001",
        tenant_id="tenant_1",
        field_id="field_1",
        device_type="soil_sensor",
        name_ar="حساس تربة 1",
        name_en="Soil Sensor 1",
    )
    registry.register(
        device_id="test_device_002",
        tenant_id="tenant_1",
        field_id="field_1",
        device_type="weather_station",
        name_ar="محطة طقس 1",
        name_en="Weather Station 1",
    )
    return registry


@pytest.fixture
def mock_publisher():
    """Create mock IoT publisher"""
    publisher = MagicMock()
    publisher.publish_sensor_reading = AsyncMock(return_value="event_123")
    publisher.publish_device_registered = AsyncMock(return_value="event_456")
    publisher.publish_device_status = AsyncMock(return_value="event_789")
    publisher.publish_device_alert = AsyncMock(return_value="event_alert_1")
    publisher.get_stats = MagicMock(
        return_value={
            "readings_published": 10,
            "status_published": 5,
            "alerts_published": 2,
            "connected": True,
        }
    )
    return publisher


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_simple(self, test_client):
        """Test simple health check"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "iot-gateway"

    def test_healthz(self, test_client):
        """Test healthz endpoint"""
        response = test_client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "iot-gateway"


class TestSensorEndpoints:
    """Test sensor reading endpoints"""

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    @pytest.mark.asyncio
    async def test_post_sensor_reading_success(
        self, mock_pub, mock_reg, test_client, mock_registry, mock_publisher
    ):
        """Test successful sensor reading submission"""
        mock_reg.__bool__ = lambda x: True
        mock_reg.get = mock_registry.get
        mock_reg.update_status = mock_registry.update_status
        mock_pub.__bool__ = lambda x: True
        mock_pub.publish_sensor_reading = mock_publisher.publish_sensor_reading

        payload = {
            "device_id": "test_device_001",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "sensor_type": "soil_moisture",
            "value": 45.5,
            "unit": "%",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["device_id"] == "test_device_001"
        assert data["sensor_type"] == "soil_moisture"
        assert data["value"] == 45.5
        assert "event_id" in data

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    def test_post_sensor_reading_device_not_found(
        self, mock_pub, mock_reg, test_client, mock_publisher
    ):
        """Test sensor reading with unregistered device"""
        mock_reg.get = MagicMock(return_value=None)
        mock_pub.__bool__ = lambda x: True

        payload = {
            "device_id": "unknown_device",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "sensor_type": "soil_moisture",
            "value": 45.5,
            "unit": "%",
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"].lower()

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    def test_post_sensor_reading_invalid_value_range(
        self, mock_pub, mock_reg, test_client, mock_registry
    ):
        """Test sensor reading with value out of range"""
        mock_reg.get = mock_registry.get
        mock_pub.__bool__ = lambda x: True

        payload = {
            "device_id": "test_device_001",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "sensor_type": "soil_moisture",
            "value": 150.0,  # Out of range (max 100)
            "unit": "%",
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 422  # Validation error

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    @pytest.mark.asyncio
    async def test_post_sensor_reading_with_metadata(
        self, mock_pub, mock_reg, test_client, mock_registry, mock_publisher
    ):
        """Test sensor reading with metadata"""
        mock_reg.__bool__ = lambda x: True
        mock_reg.get = mock_registry.get
        mock_reg.update_status = mock_registry.update_status
        mock_pub.__bool__ = lambda x: True
        mock_pub.publish_sensor_reading = mock_publisher.publish_sensor_reading

        payload = {
            "device_id": "test_device_001",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "sensor_type": "soil_temperature",
            "value": 22.5,
            "unit": "°C",
            "metadata": {"battery": 85, "rssi": -65},
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @patch("apps.services.iot_gateway.src.main.publisher")
    def test_post_sensor_reading_publisher_unavailable(self, mock_pub, test_client):
        """Test sensor reading when publisher is unavailable"""
        mock_pub.__bool__ = lambda x: False

        payload = {
            "device_id": "test_device_001",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "sensor_type": "soil_moisture",
            "value": 45.5,
            "unit": "%",
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 503
        assert "not available" in response.json()["detail"].lower()

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    @pytest.mark.asyncio
    async def test_post_batch_readings_success(
        self, mock_pub, mock_reg, test_client, mock_registry, mock_publisher
    ):
        """Test successful batch reading submission"""
        mock_reg.__bool__ = lambda x: True
        mock_reg.get = mock_registry.get
        mock_reg.update_status = mock_registry.update_status
        mock_pub.__bool__ = lambda x: True
        mock_pub.publish_sensor_reading = mock_publisher.publish_sensor_reading

        payload = {
            "device_id": "test_device_002",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "readings": [
                {"type": "air_temperature", "value": 25.5, "unit": "°C"},
                {"type": "air_humidity", "value": 65.0, "unit": "%"},
                {"type": "wind_speed", "value": 12.3, "unit": "km/h"},
            ],
        }

        response = test_client.post("/sensor/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] >= 3
        assert len(data["event_ids"]) >= 3


class TestDeviceEndpoints:
    """Test device management endpoints"""

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    @pytest.mark.asyncio
    async def test_register_device_success(self, mock_pub, mock_reg, test_client, mock_publisher):
        """Test successful device registration"""
        new_registry = DeviceRegistry()
        mock_reg.register = new_registry.register
        mock_pub.__bool__ = lambda x: True
        mock_pub.publish_device_registered = mock_publisher.publish_device_registered

        payload = {
            "device_id": "new_device_001",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "device_type": "soil_sensor",
            "name_ar": "حساس جديد",
            "name_en": "New Sensor",
            "location": {"lat": 24.7136, "lng": 46.6753},
            "metadata": {"firmware": "v1.2.3"},
        }

        response = test_client.post("/device/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["device"]["device_id"] == "new_device_001"
        assert data["device"]["device_type"] == "soil_sensor"

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_get_device_success(self, mock_reg, test_client, mock_registry):
        """Test getting device information"""
        mock_reg.get = mock_registry.get

        response = test_client.get("/device/test_device_001")
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "test_device_001"
        assert data["tenant_id"] == "tenant_1"

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_get_device_not_found(self, mock_reg, test_client):
        """Test getting non-existent device"""
        mock_reg.get = MagicMock(return_value=None)

        response = test_client.get("/device/unknown_device")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_get_device_status(self, mock_reg, test_client, mock_registry):
        """Test getting device status"""
        mock_reg.get = mock_registry.get

        response = test_client.get("/device/test_device_001/status")
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "test_device_001"
        assert "status" in data
        assert "is_online" in data
        assert "last_seen" in data

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_list_all_devices(self, mock_reg, test_client, mock_registry):
        """Test listing all devices"""
        mock_reg.list_all = mock_registry.list_all

        response = test_client.get("/devices")
        assert response.status_code == 200
        data = response.json()
        assert "devices" in data
        assert "count" in data
        assert data["count"] == 2

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_list_devices_by_field(self, mock_reg, test_client, mock_registry):
        """Test listing devices by field"""
        mock_reg.get_by_field = mock_registry.get_by_field

        response = test_client.get("/devices?field_id=field_1")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert all(d["field_id"] == "field_1" for d in data["devices"])

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_list_devices_by_type(self, mock_reg, test_client, mock_registry):
        """Test listing devices by type"""
        mock_reg.get_by_type = mock_registry.get_by_type

        response = test_client.get("/devices?device_type=soil_sensor")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["devices"][0]["device_type"] == "soil_sensor"

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_delete_device_success(self, mock_reg, test_client, mock_registry):
        """Test successful device deletion"""
        mock_reg.delete = mock_registry.delete

        response = test_client.delete("/device/test_device_001")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["device_id"] == "test_device_001"

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_delete_device_not_found(self, mock_reg, test_client):
        """Test deleting non-existent device"""
        mock_reg.delete = MagicMock(return_value=False)

        response = test_client.delete("/device/unknown_device")
        assert response.status_code == 404


class TestFieldEndpoints:
    """Test field-related endpoints"""

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_get_field_devices(self, mock_reg, test_client, mock_registry):
        """Test getting all devices for a field"""
        mock_reg.get_by_field = mock_registry.get_by_field

        response = test_client.get("/field/field_1/devices")
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_1"
        assert data["count"] == 2
        assert len(data["devices"]) == 2

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_get_field_latest_readings(self, mock_reg, test_client, mock_registry):
        """Test getting latest readings from field devices"""
        # Update a device with a reading
        mock_registry.update_status(
            device_id="test_device_001",
            last_reading={"sensor_type": "soil_moisture", "value": 45.5, "unit": "%"},
        )
        mock_reg.get_by_field = mock_registry.get_by_field

        response = test_client.get("/field/field_1/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_1"
        assert "readings" in data
        assert "count" in data


class TestStatsEndpoint:
    """Test statistics endpoint"""

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    def test_get_stats(self, mock_pub, mock_reg, test_client, mock_registry, mock_publisher):
        """Test getting gateway statistics"""
        mock_reg.get_stats = mock_registry.get_stats
        mock_pub.get_stats = mock_publisher.get_stats
        mock_pub.__bool__ = lambda x: True
        mock_reg.__bool__ = lambda x: True

        response = test_client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "publisher" in data
        assert "registry" in data
        assert "mqtt" in data


class TestValidation:
    """Test request validation"""

    def test_sensor_reading_missing_required_fields(self, test_client):
        """Test sensor reading with missing required fields"""
        payload = {
            "device_id": "test_device_001",
            "sensor_type": "soil_moisture",
            # Missing tenant_id, field_id, value
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 422

    def test_sensor_reading_invalid_device_id(self, test_client):
        """Test sensor reading with empty device_id"""
        payload = {
            "device_id": "",  # Empty string
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "sensor_type": "soil_moisture",
            "value": 45.5,
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 422

    def test_device_register_missing_fields(self, test_client):
        """Test device registration with missing fields"""
        payload = {
            "device_id": "new_device",
            "tenant_id": "tenant_1",
            # Missing field_id, device_type, names
        }

        response = test_client.post("/device/register", json=payload)
        assert response.status_code == 422

    @patch("apps.services.iot_gateway.src.main.registry")
    def test_tenant_isolation_validation(self, mock_reg, test_client, mock_registry):
        """Test that devices cannot access other tenants' data"""
        # Create device in tenant_2
        mock_registry.register(
            device_id="isolated_device",
            tenant_id="tenant_2",
            field_id="field_2",
            device_type="soil_sensor",
            name_ar="حساس معزول",
            name_en="Isolated Sensor",
        )
        mock_reg.get = mock_registry.get

        # Try to submit reading for wrong tenant
        payload = {
            "device_id": "isolated_device",
            "tenant_id": "tenant_1",  # Wrong tenant
            "field_id": "field_2",
            "sensor_type": "soil_moisture",
            "value": 45.5,
        }

        response = test_client.post("/sensor/reading", json=payload)
        assert response.status_code == 403


class TestAsyncEndpoints:
    """Test async endpoint behavior"""

    @pytest.mark.asyncio
    async def test_async_health_check(self):
        """Test health check with async client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

    @patch("apps.services.iot_gateway.src.main.registry")
    @patch("apps.services.iot_gateway.src.main.publisher")
    @pytest.mark.asyncio
    async def test_async_sensor_reading(self, mock_pub, mock_reg, mock_registry, mock_publisher):
        """Test sensor reading submission with async client"""
        mock_reg.__bool__ = lambda x: True
        mock_reg.get = mock_registry.get
        mock_reg.update_status = mock_registry.update_status
        mock_pub.__bool__ = lambda x: True
        mock_pub.publish_sensor_reading = mock_publisher.publish_sensor_reading

        payload = {
            "device_id": "test_device_001",
            "tenant_id": "tenant_1",
            "field_id": "field_1",
            "sensor_type": "soil_moisture",
            "value": 45.5,
            "unit": "%",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/sensor/reading", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
