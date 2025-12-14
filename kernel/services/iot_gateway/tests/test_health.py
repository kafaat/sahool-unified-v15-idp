"""
Health Check Tests - IoT Gateway
"""

import pytest

# Import will fail without NATS, so we mock
import sys
from unittest.mock import MagicMock

# Mock NATS before importing main
sys.modules["nats"] = MagicMock()
sys.modules["nats.aio"] = MagicMock()
sys.modules["nats.aio.client"] = MagicMock()

from kernel.services.iot_gateway.src.normalizer import (  # noqa: E402
    normalize,
)
from kernel.services.iot_gateway.src.registry import (  # noqa: E402
    DeviceRegistry,
    DeviceStatus,
)


class TestNormalizer:
    """Test sensor data normalizer"""

    def test_normalize_standard_payload(self):
        """Test normalization of standard payload"""
        payload = """
        {
            "device_id": "sensor_001",
            "field_id": "field_123",
            "type": "soil_moisture",
            "value": 45.5,
            "unit": "%"
        }
        """

        result = normalize(payload)

        assert result.device_id == "sensor_001"
        assert result.field_id == "field_123"
        assert result.sensor_type == "soil_moisture"
        assert result.value == 45.5
        assert result.unit == "%"

    def test_normalize_compact_payload(self):
        """Test normalization of compact payload"""
        payload = """
        {
            "d": "sensor_002",
            "f": "field_456",
            "t": "temperature",
            "v": 28.3
        }
        """

        result = normalize(payload)

        assert result.device_id == "sensor_002"
        assert result.field_id == "field_456"
        assert result.sensor_type == "air_temperature"
        assert result.value == 28.3

    def test_normalize_with_metadata(self):
        """Test normalization with battery and RSSI"""
        payload = """
        {
            "device_id": "sensor_003",
            "field_id": "field_789",
            "type": "soil_ec",
            "value": 2.5,
            "unit": "mS/cm",
            "battery": 85,
            "rssi": -65
        }
        """

        result = normalize(payload)

        assert result.metadata["battery"] == 85
        assert result.metadata["rssi"] == -65

    def test_normalize_sensor_type_alias(self):
        """Test sensor type alias mapping"""
        payload = """
        {
            "device_id": "sensor_004",
            "field_id": "field_001",
            "type": "sm",
            "value": 30
        }
        """

        result = normalize(payload)
        assert result.sensor_type == "soil_moisture"

    def test_normalize_missing_device_id_raises(self):
        """Test that missing device_id raises error"""
        payload = """{"field_id": "f1", "type": "temp", "value": 25}"""

        with pytest.raises(ValueError, match="device_id"):
            normalize(payload)

    def test_normalize_from_topic(self):
        """Test extraction from MQTT topic"""
        payload = """{"type": "soil_moisture", "value": 40}"""
        topic = "sahool/sensors/sensor_005/field_abc/soil_moisture"

        result = normalize(payload, topic)

        assert result.device_id == "sensor_005"
        assert result.field_id == "field_abc"


class TestRegistry:
    """Test device registry"""

    def test_register_device(self):
        """Test device registration"""
        registry = DeviceRegistry()

        device = registry.register(
            device_id="dev_001",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس تربة 1",
            name_en="Soil Sensor 1",
        )

        assert device.device_id == "dev_001"
        assert device.tenant_id == "tenant_1"
        assert device.field_id == "field_1"

    def test_get_device(self):
        """Test getting device by ID"""
        registry = DeviceRegistry()
        registry.register(
            device_id="dev_002",
            tenant_id="t1",
            field_id="f1",
            device_type="weather_station",
            name_ar="محطة طقس",
            name_en="Weather Station",
        )

        device = registry.get("dev_002")
        assert device is not None
        assert device.device_id == "dev_002"

        # Non-existent device
        assert registry.get("non_existent") is None

    def test_get_by_field(self):
        """Test getting devices by field"""
        registry = DeviceRegistry()

        registry.register("d1", "t1", "field_a", "soil_sensor", "ح1", "S1")
        registry.register("d2", "t1", "field_a", "weather_station", "ط1", "W1")
        registry.register("d3", "t1", "field_b", "soil_sensor", "ح2", "S2")

        field_a_devices = registry.get_by_field("field_a")
        assert len(field_a_devices) == 2

        field_b_devices = registry.get_by_field("field_b")
        assert len(field_b_devices) == 1

    def test_update_status(self):
        """Test updating device status"""
        registry = DeviceRegistry()
        registry.register("dev_003", "t1", "f1", "sensor", "حساس", "Sensor")

        registry.update_status(
            device_id="dev_003",
            status=DeviceStatus.ONLINE,
            battery_level=90,
            signal_strength=-55,
        )

        device = registry.get("dev_003")
        assert device.status == DeviceStatus.ONLINE.value
        assert device.battery_level == 90
        assert device.signal_strength == -55

    def test_low_battery_warning(self):
        """Test that low battery sets warning status"""
        registry = DeviceRegistry()
        registry.register("dev_004", "t1", "f1", "sensor", "حساس", "Sensor")

        registry.update_status(
            device_id="dev_004",
            battery_level=15,  # Low battery
        )

        device = registry.get("dev_004")
        assert device.status == DeviceStatus.WARNING.value

    def test_auto_register(self):
        """Test auto-registration on first reading"""
        registry = DeviceRegistry()

        device = registry.auto_register(
            device_id="auto_dev_001",
            tenant_id="t1",
            field_id="f1",
            sensor_type="soil_moisture",
        )

        assert device.device_id == "auto_dev_001"
        assert device.device_type == "soil_sensor"

    def test_get_stats(self):
        """Test registry statistics"""
        registry = DeviceRegistry()

        registry.register("d1", "t1", "f1", "soil_sensor", "ح1", "S1")
        registry.register("d2", "t1", "f1", "weather_station", "ط1", "W1")

        registry.update_status("d1", DeviceStatus.ONLINE)
        registry.update_status("d2", DeviceStatus.OFFLINE)

        stats = registry.get_stats()

        assert stats["total"] == 2
        assert stats["online"] == 1
        assert stats["offline"] == 1
        assert "soil_sensor" in stats["by_type"]
