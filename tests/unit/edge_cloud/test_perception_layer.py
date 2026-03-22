"""
SAHOOL Edge-Cloud Perception Layer Tests
اختبارات طبقة الإدراك للحوسبة الحافة-السحابة

Tests for the perception layer including:
- Device registration (MQTT, Modbus, LoRa, CoAP)
- Sensor data collection
- Multi-protocol support
- Sampling frequency management

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from .conftest import (
    DataQuality,
    DeviceProtocol,
    DeviceStatus,
    SensorType,
)

# ==============================================================================
# Device Manager Class (Test Target Mock)
# ==============================================================================


class DeviceManager:
    """Device management for perception layer (mock implementation for testing)"""

    def __init__(self):
        self._devices: dict[str, dict[str, Any]] = {}
        self._protocol_handlers: dict[str, Any] = {}

    async def register_device(self, device_config: dict[str, Any]) -> dict[str, Any]:
        """Register a new device"""
        device_id = device_config.get("device_id", str(uuid.uuid4()))
        protocol = device_config.get("protocol")

        if not protocol:
            raise ValueError("Protocol must be specified")

        if protocol not in [p.value for p in DeviceProtocol]:
            raise ValueError(f"Unsupported protocol: {protocol}")

        self._devices[device_id] = {
            **device_config,
            "device_id": device_id,
            "registered_at": datetime.now(UTC).isoformat(),
            "status": DeviceStatus.ONLINE.value,
        }

        return {
            "success": True,
            "device_id": device_id,
            "protocol": protocol,
            "message": f"Device registered successfully with {protocol} protocol",
        }

    async def unregister_device(self, device_id: str) -> dict[str, Any]:
        """Unregister a device"""
        if device_id not in self._devices:
            raise ValueError(f"Device not found: {device_id}")

        del self._devices[device_id]
        return {"success": True, "device_id": device_id}

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        """Get device configuration"""
        return self._devices.get(device_id)

    def list_devices(self, protocol: str | None = None) -> list[dict[str, Any]]:
        """List all registered devices"""
        devices = list(self._devices.values())
        if protocol:
            devices = [d for d in devices if d.get("protocol") == protocol]
        return devices


class SensorDataCollector:
    """Sensor data collection (mock implementation for testing)"""

    def __init__(self, device_manager: DeviceManager):
        self._device_manager = device_manager
        self._readings: list[dict[str, Any]] = []

    async def collect(self, device_id: str) -> dict[str, Any]:
        """Collect sensor data from a device"""
        device = self._device_manager.get_device(device_id)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        sensors = device.get("sensors", [])
        readings = []

        for sensor in sensors:
            reading = {
                "reading_id": str(uuid.uuid4()),
                "device_id": device_id,
                "sensor_id": sensor["sensor_id"],
                "sensor_type": sensor["type"],
                "value": self._simulate_reading(sensor["type"]),
                "unit": sensor["unit"],
                "timestamp": datetime.now(UTC).isoformat(),
                "quality": DataQuality.GOOD.value,
            }
            readings.append(reading)
            self._readings.append(reading)

        return {
            "device_id": device_id,
            "readings_count": len(readings),
            "readings": readings,
            "collected_at": datetime.now(UTC).isoformat(),
        }

    async def collect_batch(self, device_ids: list[str]) -> dict[str, Any]:
        """Collect data from multiple devices"""
        results = []
        errors = []

        for device_id in device_ids:
            try:
                result = await self.collect(device_id)
                results.append(result)
            except Exception as e:
                errors.append({"device_id": device_id, "error": str(e)})

        return {
            "total_devices": len(device_ids),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }

    def _simulate_reading(self, sensor_type: str) -> float:
        """Simulate sensor reading value"""
        import random

        ranges = {
            SensorType.SOIL_MOISTURE.value: (20, 80),
            SensorType.TEMPERATURE.value: (15, 40),
            SensorType.HUMIDITY.value: (30, 90),
            SensorType.PH.value: (5.5, 8.5),
            SensorType.EC.value: (0.5, 4.0),
            SensorType.LIGHT.value: (0, 100000),
        }
        min_val, max_val = ranges.get(sensor_type, (0, 100))
        return round(random.uniform(min_val, max_val), 2)

    def get_sampling_frequency(self, device_id: str) -> int:
        """Get device sampling frequency in seconds"""
        device = self._device_manager.get_device(device_id)
        if not device:
            raise ValueError(f"Device not found: {device_id}")
        return device.get("sampling_frequency_seconds", 300)

    def set_sampling_frequency(self, device_id: str, frequency_seconds: int) -> bool:
        """Set device sampling frequency"""
        device = self._device_manager.get_device(device_id)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        if frequency_seconds < 10 or frequency_seconds > 3600:
            raise ValueError("Frequency must be between 10 and 3600 seconds")

        device["sampling_frequency_seconds"] = frequency_seconds
        return True


# ==============================================================================
# Test Classes
# ==============================================================================


class TestRegisterMqttDevice:
    """Tests for MQTT device registration"""

    @pytest.fixture
    def device_manager(self) -> DeviceManager:
        return DeviceManager()

    @pytest.mark.asyncio
    async def test_register_mqtt_device_success(
        self, device_manager: DeviceManager, sample_mqtt_device: dict[str, Any]
    ):
        """Test successful MQTT device registration"""
        result = await device_manager.register_device(sample_mqtt_device)

        assert result["success"] is True
        assert result["device_id"] == sample_mqtt_device["device_id"]
        assert result["protocol"] == DeviceProtocol.MQTT.value
        assert "mqtt" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_register_mqtt_device_with_connection_params(
        self, device_manager: DeviceManager, sample_mqtt_device: dict[str, Any]
    ):
        """Test MQTT device registration includes connection parameters"""
        await device_manager.register_device(sample_mqtt_device)
        device = device_manager.get_device(sample_mqtt_device["device_id"])

        assert device is not None
        assert "connection" in device
        assert "broker_url" in device["connection"]
        assert "topic_data" in device["connection"]
        assert "qos" in device["connection"]

    @pytest.mark.asyncio
    async def test_register_mqtt_device_with_tls(
        self, device_manager: DeviceManager, sample_mqtt_device: dict[str, Any]
    ):
        """Test MQTT device with TLS enabled"""
        await device_manager.register_device(sample_mqtt_device)
        device = device_manager.get_device(sample_mqtt_device["device_id"])

        assert device["connection"]["use_tls"] is True

    @pytest.mark.asyncio
    async def test_register_mqtt_device_sets_status_online(
        self, device_manager: DeviceManager, sample_mqtt_device: dict[str, Any]
    ):
        """Test newly registered device status is online"""
        await device_manager.register_device(sample_mqtt_device)
        device = device_manager.get_device(sample_mqtt_device["device_id"])

        assert device["status"] == DeviceStatus.ONLINE.value

    @pytest.mark.asyncio
    async def test_register_mqtt_device_with_sensors(
        self, device_manager: DeviceManager, sample_mqtt_device: dict[str, Any]
    ):
        """Test MQTT device registration with multiple sensors"""
        await device_manager.register_device(sample_mqtt_device)
        device = device_manager.get_device(sample_mqtt_device["device_id"])

        assert "sensors" in device
        assert len(device["sensors"]) == 2
        sensor_types = [s["type"] for s in device["sensors"]]
        assert SensorType.SOIL_MOISTURE.value in sensor_types
        assert SensorType.TEMPERATURE.value in sensor_types


class TestRegisterModbusDevice:
    """Tests for Modbus device registration"""

    @pytest.fixture
    def device_manager(self) -> DeviceManager:
        return DeviceManager()

    @pytest.mark.asyncio
    async def test_register_modbus_device_success(
        self, device_manager: DeviceManager, sample_modbus_device: dict[str, Any]
    ):
        """Test successful Modbus device registration"""
        result = await device_manager.register_device(sample_modbus_device)

        assert result["success"] is True
        assert result["protocol"] == DeviceProtocol.MODBUS.value

    @pytest.mark.asyncio
    async def test_register_modbus_device_with_registers(
        self, device_manager: DeviceManager, sample_modbus_device: dict[str, Any]
    ):
        """Test Modbus device registration includes register configuration"""
        await device_manager.register_device(sample_modbus_device)
        device = device_manager.get_device(sample_modbus_device["device_id"])

        assert "registers" in device
        assert len(device["registers"]) == 4

        # Check register structure
        temp_register = next((r for r in device["registers"] if r["name"] == "temperature"), None)
        assert temp_register is not None
        assert temp_register["address"] == 0
        assert temp_register["type"] == "holding"
        assert temp_register["scale_factor"] == 0.1

    @pytest.mark.asyncio
    async def test_register_modbus_rtu_connection(
        self, device_manager: DeviceManager, sample_modbus_device: dict[str, Any]
    ):
        """Test Modbus RTU connection parameters"""
        await device_manager.register_device(sample_modbus_device)
        device = device_manager.get_device(sample_modbus_device["device_id"])

        conn = device["connection"]
        assert conn["mode"] == "rtu"
        assert conn["baudrate"] == 9600
        assert conn["slave_address"] == 1

    @pytest.mark.asyncio
    async def test_register_modbus_device_with_multiple_sensors(
        self, device_manager: DeviceManager, sample_modbus_device: dict[str, Any]
    ):
        """Test Modbus device with weather station sensors"""
        await device_manager.register_device(sample_modbus_device)
        device = device_manager.get_device(sample_modbus_device["device_id"])

        assert len(device["sensors"]) == 4
        sensor_types = [s["type"] for s in device["sensors"]]
        assert SensorType.TEMPERATURE.value in sensor_types
        assert SensorType.HUMIDITY.value in sensor_types
        assert SensorType.WIND_SPEED.value in sensor_types
        assert SensorType.RAIN_GAUGE.value in sensor_types


class TestCollectSensorData:
    """Tests for sensor data collection"""

    @pytest.fixture
    def device_manager(self) -> DeviceManager:
        return DeviceManager()

    @pytest.fixture
    def collector(self, device_manager: DeviceManager) -> SensorDataCollector:
        return SensorDataCollector(device_manager)

    @pytest.mark.asyncio
    async def test_collect_sensor_data_success(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test successful sensor data collection"""
        await device_manager.register_device(sample_mqtt_device)
        result = await collector.collect(sample_mqtt_device["device_id"])

        assert result["device_id"] == sample_mqtt_device["device_id"]
        assert result["readings_count"] == 2  # Two sensors in mqtt device
        assert "readings" in result
        assert "collected_at" in result

    @pytest.mark.asyncio
    async def test_collect_sensor_data_reading_structure(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test collected reading has correct structure"""
        await device_manager.register_device(sample_mqtt_device)
        result = await collector.collect(sample_mqtt_device["device_id"])

        reading = result["readings"][0]
        assert "reading_id" in reading
        assert "device_id" in reading
        assert "sensor_id" in reading
        assert "sensor_type" in reading
        assert "value" in reading
        assert "unit" in reading
        assert "timestamp" in reading
        assert "quality" in reading

    @pytest.mark.asyncio
    async def test_collect_sensor_data_device_not_found(self, collector: SensorDataCollector):
        """Test collection fails for non-existent device"""
        with pytest.raises(ValueError, match="Device not found"):
            await collector.collect("non-existent-device-id")

    @pytest.mark.asyncio
    async def test_collect_sensor_data_values_in_range(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test collected values are within expected ranges"""
        await device_manager.register_device(sample_mqtt_device)
        result = await collector.collect(sample_mqtt_device["device_id"])

        for reading in result["readings"]:
            if reading["sensor_type"] == SensorType.SOIL_MOISTURE.value:
                assert 0 <= reading["value"] <= 100
            elif reading["sensor_type"] == SensorType.TEMPERATURE.value:
                assert -40 <= reading["value"] <= 60


class TestMultiProtocolSupport:
    """Tests for multi-protocol device support"""

    @pytest.fixture
    def device_manager(self) -> DeviceManager:
        return DeviceManager()

    @pytest.mark.asyncio
    async def test_register_multiple_protocols(
        self,
        device_manager: DeviceManager,
        sample_mqtt_device: dict[str, Any],
        sample_modbus_device: dict[str, Any],
        sample_lora_device: dict[str, Any],
    ):
        """Test registering devices with different protocols"""
        await device_manager.register_device(sample_mqtt_device)
        await device_manager.register_device(sample_modbus_device)
        await device_manager.register_device(sample_lora_device)

        devices = device_manager.list_devices()
        assert len(devices) == 3

        protocols = {d["protocol"] for d in devices}
        assert DeviceProtocol.MQTT.value in protocols
        assert DeviceProtocol.MODBUS.value in protocols
        assert DeviceProtocol.LORA.value in protocols

    @pytest.mark.asyncio
    async def test_filter_devices_by_protocol(
        self,
        device_manager: DeviceManager,
        sample_mqtt_device: dict[str, Any],
        sample_modbus_device: dict[str, Any],
    ):
        """Test filtering devices by protocol"""
        await device_manager.register_device(sample_mqtt_device)
        await device_manager.register_device(sample_modbus_device)

        mqtt_devices = device_manager.list_devices(protocol=DeviceProtocol.MQTT.value)
        assert len(mqtt_devices) == 1
        assert mqtt_devices[0]["protocol"] == DeviceProtocol.MQTT.value

        modbus_devices = device_manager.list_devices(protocol=DeviceProtocol.MODBUS.value)
        assert len(modbus_devices) == 1
        assert modbus_devices[0]["protocol"] == DeviceProtocol.MODBUS.value

    @pytest.mark.asyncio
    async def test_unsupported_protocol_rejected(self, device_manager: DeviceManager):
        """Test that unsupported protocols are rejected"""
        invalid_device = {
            "device_id": str(uuid.uuid4()),
            "protocol": "unsupported_protocol",
            "name_en": "Invalid Device",
        }

        with pytest.raises(ValueError, match="Unsupported protocol"):
            await device_manager.register_device(invalid_device)

    @pytest.mark.asyncio
    async def test_lora_device_specific_params(self, device_manager: DeviceManager, sample_lora_device: dict[str, Any]):
        """Test LoRa device has protocol-specific parameters"""
        await device_manager.register_device(sample_lora_device)
        device = device_manager.get_device(sample_lora_device["device_id"])

        conn = device["connection"]
        assert "dev_eui" in conn
        assert "app_eui" in conn
        assert "spreading_factor" in conn
        assert "frequency_mhz" in conn

    @pytest.mark.asyncio
    async def test_coap_protocol_support(self, device_manager: DeviceManager):
        """Test CoAP protocol device registration"""
        coap_device = {
            "device_id": str(uuid.uuid4()),
            "protocol": DeviceProtocol.COAP.value,
            "name_en": "CoAP Sensor",
            "connection": {
                "uri": "coap://sensor.local:5683",
                "resource": "/sensors/temperature",
            },
            "sensors": [
                {
                    "sensor_id": "coap_temp",
                    "type": SensorType.TEMPERATURE.value,
                    "unit": "C",
                }
            ],
        }

        result = await device_manager.register_device(coap_device)
        assert result["success"] is True
        assert result["protocol"] == DeviceProtocol.COAP.value


class TestSamplingFrequency:
    """Tests for sampling frequency management"""

    @pytest.fixture
    def device_manager(self) -> DeviceManager:
        return DeviceManager()

    @pytest.fixture
    def collector(self, device_manager: DeviceManager) -> SensorDataCollector:
        return SensorDataCollector(device_manager)

    @pytest.mark.asyncio
    async def test_get_default_sampling_frequency(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test getting default sampling frequency"""
        await device_manager.register_device(sample_mqtt_device)
        frequency = collector.get_sampling_frequency(sample_mqtt_device["device_id"])

        assert frequency == 300  # 5 minutes as defined in fixture

    @pytest.mark.asyncio
    async def test_set_sampling_frequency(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test setting new sampling frequency"""
        await device_manager.register_device(sample_mqtt_device)

        result = collector.set_sampling_frequency(sample_mqtt_device["device_id"], 60)
        assert result is True

        new_frequency = collector.get_sampling_frequency(sample_mqtt_device["device_id"])
        assert new_frequency == 60

    @pytest.mark.asyncio
    async def test_sampling_frequency_minimum_limit(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test sampling frequency minimum limit (10 seconds)"""
        await device_manager.register_device(sample_mqtt_device)

        with pytest.raises(ValueError, match="between 10 and 3600"):
            collector.set_sampling_frequency(sample_mqtt_device["device_id"], 5)

    @pytest.mark.asyncio
    async def test_sampling_frequency_maximum_limit(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test sampling frequency maximum limit (3600 seconds = 1 hour)"""
        await device_manager.register_device(sample_mqtt_device)

        with pytest.raises(ValueError, match="between 10 and 3600"):
            collector.set_sampling_frequency(sample_mqtt_device["device_id"], 7200)

    @pytest.mark.asyncio
    async def test_different_protocols_different_frequencies(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
        sample_modbus_device: dict[str, Any],
        sample_lora_device: dict[str, Any],
    ):
        """Test different protocols can have different sampling frequencies"""
        await device_manager.register_device(sample_mqtt_device)
        await device_manager.register_device(sample_modbus_device)
        await device_manager.register_device(sample_lora_device)

        mqtt_freq = collector.get_sampling_frequency(sample_mqtt_device["device_id"])
        modbus_freq = collector.get_sampling_frequency(sample_modbus_device["device_id"])
        lora_freq = collector.get_sampling_frequency(sample_lora_device["device_id"])

        # MQTT: 5 minutes, Modbus: 1 minute, LoRa: 15 minutes (battery saving)
        assert mqtt_freq == 300
        assert modbus_freq == 60
        assert lora_freq == 900

    @pytest.mark.asyncio
    async def test_batch_collection_multiple_devices(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
        sample_modbus_device: dict[str, Any],
    ):
        """Test batch collection from multiple devices"""
        await device_manager.register_device(sample_mqtt_device)
        await device_manager.register_device(sample_modbus_device)

        device_ids = [sample_mqtt_device["device_id"], sample_modbus_device["device_id"]]
        result = await collector.collect_batch(device_ids)

        assert result["total_devices"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_batch_collection_partial_failure(
        self,
        device_manager: DeviceManager,
        collector: SensorDataCollector,
        sample_mqtt_device: dict[str, Any],
    ):
        """Test batch collection with some devices failing"""
        await device_manager.register_device(sample_mqtt_device)

        device_ids = [sample_mqtt_device["device_id"], "non-existent-device"]
        result = await collector.collect_batch(device_ids)

        assert result["total_devices"] == 2
        assert result["successful"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
