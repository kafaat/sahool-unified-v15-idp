"""
Comprehensive Device Management Tests
Tests device registry, status tracking, lifecycle management
"""

from datetime import UTC, datetime, timedelta
from time import sleep

import pytest
from apps.services.iot_gateway.src.registry import (
    Device,
    DeviceRegistry,
    DeviceStatus,
    DeviceType,
    get_registry,
)


class TestDevice:
    """Test Device dataclass"""

    def test_create_device(self):
        """Test creating a device"""
        device = Device(
            device_id="dev_001",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس تربة",
            name_en="Soil Sensor",
        )

        assert device.device_id == "dev_001"
        assert device.tenant_id == "tenant_1"
        assert device.field_id == "field_1"
        assert device.device_type == "soil_sensor"
        assert device.name_ar == "حساس تربة"
        assert device.name_en == "Soil Sensor"
        assert device.status == DeviceStatus.UNKNOWN.value

    def test_device_to_dict(self):
        """Test converting device to dictionary"""
        device = Device(
            device_id="dev_001",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس تربة",
            name_en="Soil Sensor",
            battery_level=85.5,
            signal_strength=-65,
        )

        data = device.to_dict()
        assert isinstance(data, dict)
        assert data["device_id"] == "dev_001"
        assert data["battery_level"] == 85.5
        assert data["signal_strength"] == -65

    def test_device_is_online_with_recent_timestamp(self):
        """Test device is considered online with recent last_seen"""
        device = Device(
            device_id="dev_001",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس",
            name_en="Sensor",
            last_seen=datetime.now(UTC).isoformat(),
        )

        assert device.is_online(timeout_minutes=15) is True

    def test_device_is_offline_with_old_timestamp(self):
        """Test device is considered offline with old last_seen"""
        old_time = datetime.now(UTC) - timedelta(minutes=30)
        device = Device(
            device_id="dev_001",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس",
            name_en="Sensor",
            last_seen=old_time.isoformat(),
        )

        assert device.is_online(timeout_minutes=15) is False

    def test_device_is_offline_without_last_seen(self):
        """Test device is offline if last_seen is None"""
        device = Device(
            device_id="dev_001",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس",
            name_en="Sensor",
        )

        assert device.is_online() is False


class TestDeviceStatus:
    """Test DeviceStatus enum"""

    def test_device_status_values(self):
        """Test all device status enum values"""
        assert DeviceStatus.ONLINE.value == "online"
        assert DeviceStatus.OFFLINE.value == "offline"
        assert DeviceStatus.WARNING.value == "warning"
        assert DeviceStatus.ERROR.value == "error"
        assert DeviceStatus.UNKNOWN.value == "unknown"


class TestDeviceType:
    """Test DeviceType enum"""

    def test_device_type_values(self):
        """Test all device type enum values"""
        assert DeviceType.SOIL_SENSOR.value == "soil_sensor"
        assert DeviceType.WEATHER_STATION.value == "weather_station"
        assert DeviceType.WATER_SENSOR.value == "water_sensor"
        assert DeviceType.FLOW_METER.value == "flow_meter"
        assert DeviceType.VALVE_CONTROLLER.value == "valve_controller"
        assert DeviceType.GATEWAY.value == "gateway"
        assert DeviceType.CAMERA.value == "camera"
        assert DeviceType.UNKNOWN.value == "unknown"


class TestDeviceRegistration:
    """Test device registration operations"""

    def test_register_new_device(self):
        """Test registering a new device"""
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
        assert device.device_type == "soil_sensor"

    def test_register_device_with_optional_fields(self):
        """Test registering device with optional fields"""
        registry = DeviceRegistry()

        device = registry.register(
            device_id="dev_002",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="weather_station",
            name_ar="محطة طقس",
            name_en="Weather Station",
            location={"lat": 24.7136, "lng": 46.6753},
            firmware_version="v1.2.3",
            metadata={"manufacturer": "ACME Corp", "model": "WS-2000"},
        )

        assert device.location["lat"] == 24.7136
        assert device.firmware_version == "v1.2.3"
        assert device.metadata["manufacturer"] == "ACME Corp"

    def test_update_existing_device(self):
        """Test updating an existing device registration"""
        registry = DeviceRegistry()

        # Initial registration
        registry.register(
            device_id="dev_003",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس قديم",
            name_en="Old Sensor",
        )

        # Update registration
        updated_device = registry.register(
            device_id="dev_003",
            tenant_id="tenant_1",
            field_id="field_2",  # Changed field
            device_type="soil_sensor",
            name_ar="حساس جديد",  # Changed name
            name_en="New Sensor",  # Changed name
        )

        assert updated_device.field_id == "field_2"
        assert updated_device.name_ar == "حساس جديد"
        assert updated_device.name_en == "New Sensor"

    def test_register_multiple_devices(self):
        """Test registering multiple devices"""
        registry = DeviceRegistry()

        for i in range(5):
            registry.register(
                device_id=f"dev_{i:03d}",
                tenant_id="tenant_1",
                field_id="field_1",
                device_type="soil_sensor",
                name_ar=f"حساس {i}",
                name_en=f"Sensor {i}",
            )

        devices = registry.list_all()
        assert len(devices) == 5


class TestDeviceRetrieval:
    """Test device retrieval operations"""

    @pytest.fixture
    def populated_registry(self):
        """Create a registry with test devices"""
        registry = DeviceRegistry()

        # Tenant 1, Field 1
        registry.register(
            "dev_t1_f1_s1", "tenant_1", "field_1", "soil_sensor", "حساس 1", "Sensor 1"
        )
        registry.register(
            "dev_t1_f1_s2", "tenant_1", "field_1", "soil_sensor", "حساس 2", "Sensor 2"
        )
        registry.register(
            "dev_t1_f1_w1",
            "tenant_1",
            "field_1",
            "weather_station",
            "طقس 1",
            "Weather 1",
        )

        # Tenant 1, Field 2
        registry.register(
            "dev_t1_f2_s1", "tenant_1", "field_2", "soil_sensor", "حساس 3", "Sensor 3"
        )

        # Tenant 2, Field 3
        registry.register("dev_t2_f3_s1", "tenant_2", "field_3", "water_sensor", "ماء 1", "Water 1")

        return registry

    def test_get_device_by_id(self, populated_registry):
        """Test getting device by ID"""
        device = populated_registry.get("dev_t1_f1_s1")
        assert device is not None
        assert device.device_id == "dev_t1_f1_s1"
        assert device.tenant_id == "tenant_1"

    def test_get_nonexistent_device(self, populated_registry):
        """Test getting non-existent device returns None"""
        device = populated_registry.get("nonexistent_device")
        assert device is None

    def test_get_by_field(self, populated_registry):
        """Test getting devices by field"""
        devices = populated_registry.get_by_field("field_1")
        assert len(devices) == 3
        assert all(d.field_id == "field_1" for d in devices)

    def test_get_by_field_empty(self, populated_registry):
        """Test getting devices from empty field"""
        devices = populated_registry.get_by_field("empty_field")
        assert len(devices) == 0

    def test_get_by_tenant(self, populated_registry):
        """Test getting devices by tenant"""
        devices = populated_registry.get_by_tenant("tenant_1")
        assert len(devices) == 4
        assert all(d.tenant_id == "tenant_1" for d in devices)

    def test_get_by_type(self, populated_registry):
        """Test getting devices by type"""
        devices = populated_registry.get_by_type("soil_sensor")
        assert len(devices) == 3
        assert all(d.device_type == "soil_sensor" for d in devices)

    def test_list_all_devices(self, populated_registry):
        """Test listing all devices"""
        devices = populated_registry.list_all()
        assert len(devices) == 5


class TestDeviceStatusTracking:
    """Test device status tracking"""

    def test_update_device_status(self):
        """Test updating device status"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        device = registry.update_status(device_id="dev_001", status=DeviceStatus.ONLINE)

        assert device.status == DeviceStatus.ONLINE.value
        assert device.last_seen is not None

    def test_update_status_sets_last_seen(self):
        """Test that updating status sets last_seen timestamp"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        before = datetime.now(UTC)
        registry.update_status(device_id="dev_001")
        device = registry.get("dev_001")
        after = datetime.now(UTC)

        last_seen = datetime.fromisoformat(device.last_seen.replace("Z", "+00:00"))
        assert before <= last_seen <= after

    def test_update_status_with_last_reading(self):
        """Test updating status with last reading"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        reading = {"sensor_type": "soil_moisture", "value": 45.5, "unit": "%"}

        device = registry.update_status(device_id="dev_001", last_reading=reading)

        assert device.last_reading == reading

    def test_update_status_with_battery_level(self):
        """Test updating status with battery level"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        device = registry.update_status(device_id="dev_001", battery_level=85.5)

        assert device.battery_level == 85.5

    def test_update_status_with_signal_strength(self):
        """Test updating status with signal strength"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        device = registry.update_status(device_id="dev_001", signal_strength=-65)

        assert device.signal_strength == -65

    def test_update_status_low_battery_sets_warning(self):
        """Test that low battery sets warning status"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        device = registry.update_status(device_id="dev_001", battery_level=15)

        assert device.status == DeviceStatus.WARNING.value
        assert device.battery_level == 15

    def test_update_status_nonexistent_device(self):
        """Test updating status of non-existent device returns None"""
        registry = DeviceRegistry()

        result = registry.update_status(device_id="nonexistent")

        assert result is None


class TestOfflineDeviceDetection:
    """Test offline device detection"""

    def test_check_offline_devices_empty_registry(self):
        """Test checking offline devices in empty registry"""
        registry = DeviceRegistry()

        offline = registry.check_offline_devices()

        assert len(offline) == 0

    def test_check_offline_devices_no_offline(self):
        """Test checking when all devices are online"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")
        registry.update_status("dev_001", DeviceStatus.ONLINE)

        offline = registry.check_offline_devices()

        assert len(offline) == 0

    def test_check_offline_devices_detects_offline(self):
        """Test detecting offline devices"""
        registry = DeviceRegistry()

        # Register device and set old last_seen
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")
        old_time = datetime.now(UTC) - timedelta(minutes=30)
        device = registry.get("dev_001")
        device.last_seen = old_time.isoformat()
        device.status = DeviceStatus.ONLINE.value

        offline = registry.check_offline_devices()

        assert len(offline) == 1
        assert offline[0].device_id == "dev_001"
        assert offline[0].status == DeviceStatus.OFFLINE.value

    def test_check_offline_devices_skips_already_offline(self):
        """Test that already offline devices are skipped"""
        registry = DeviceRegistry()

        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")
        device = registry.get("dev_001")
        device.status = DeviceStatus.OFFLINE.value
        old_time = datetime.now(UTC) - timedelta(minutes=30)
        device.last_seen = old_time.isoformat()

        offline = registry.check_offline_devices()

        assert len(offline) == 0  # Already marked as offline

    def test_check_offline_devices_multiple(self):
        """Test detecting multiple offline devices"""
        registry = DeviceRegistry()

        # Register 3 devices
        for i in range(3):
            registry.register(
                f"dev_{i:03d}",
                "tenant_1",
                "field_1",
                "soil_sensor",
                f"حساس {i}",
                f"Sensor {i}",
            )

        # Make them all old
        old_time = datetime.now(UTC) - timedelta(minutes=30)
        for i in range(3):
            device = registry.get(f"dev_{i:03d}")
            device.last_seen = old_time.isoformat()
            device.status = DeviceStatus.ONLINE.value

        offline = registry.check_offline_devices()

        assert len(offline) == 3


class TestDeviceDeletion:
    """Test device deletion"""

    def test_delete_device_success(self):
        """Test successful device deletion"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        result = registry.delete("dev_001")

        assert result is True
        assert registry.get("dev_001") is None

    def test_delete_nonexistent_device(self):
        """Test deleting non-existent device"""
        registry = DeviceRegistry()

        result = registry.delete("nonexistent")

        assert result is False

    def test_delete_device_removes_from_all_queries(self):
        """Test that deleted device is removed from all queries"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")
        registry.register("dev_002", "tenant_1", "field_1", "weather_station", "طقس", "Weather")

        registry.delete("dev_001")

        assert len(registry.list_all()) == 1
        assert len(registry.get_by_field("field_1")) == 1
        assert len(registry.get_by_tenant("tenant_1")) == 1


class TestRegistryStatistics:
    """Test registry statistics"""

    def test_get_stats_empty_registry(self):
        """Test statistics for empty registry"""
        registry = DeviceRegistry()

        stats = registry.get_stats()

        assert stats["total"] == 0
        assert stats["online"] == 0
        assert stats["offline"] == 0
        assert stats["warning"] == 0
        assert stats["by_type"] == {}

    def test_get_stats_with_devices(self):
        """Test statistics with devices"""
        registry = DeviceRegistry()

        # Register 5 devices
        for i in range(3):
            registry.register(
                f"soil_{i}", "tenant_1", "field_1", "soil_sensor", f"حساس {i}", f"S{i}"
            )

        for i in range(2):
            registry.register(
                f"weather_{i}",
                "tenant_1",
                "field_1",
                "weather_station",
                f"طقس {i}",
                f"W{i}",
            )

        stats = registry.get_stats()

        assert stats["total"] == 5
        assert stats["by_type"]["soil_sensor"] == 3
        assert stats["by_type"]["weather_station"] == 2

    def test_get_stats_with_status_tracking(self):
        """Test statistics with status tracking"""
        registry = DeviceRegistry()

        # Register devices with different statuses
        registry.register("dev_online", "t1", "f1", "soil_sensor", "ح1", "S1")
        registry.update_status("dev_online", DeviceStatus.ONLINE)

        registry.register("dev_offline", "t1", "f1", "soil_sensor", "ح2", "S2")
        registry.update_status("dev_offline", DeviceStatus.OFFLINE)

        registry.register("dev_warning", "t1", "f1", "soil_sensor", "ح3", "S3")
        registry.update_status("dev_warning", battery_level=15)  # Sets warning

        stats = registry.get_stats()

        assert stats["total"] == 3
        assert stats["online"] == 1
        assert stats["offline"] == 1
        assert stats["warning"] == 1


class TestAutoRegistration:
    """Test auto-registration functionality"""

    def test_auto_register_new_device(self):
        """Test auto-registering a new device"""
        registry = DeviceRegistry()

        device = registry.auto_register(
            device_id="auto_dev_001",
            tenant_id="tenant_1",
            field_id="field_1",
            sensor_type="soil_moisture",
        )

        assert device.device_id == "auto_dev_001"
        assert device.device_type == "soil_sensor"  # Inferred from sensor type
        assert device.tenant_id == "tenant_1"
        assert device.field_id == "field_1"

    def test_auto_register_existing_device(self):
        """Test auto-registering an existing device returns existing device"""
        registry = DeviceRegistry()

        # Manual registration
        registry.register(
            "existing_dev",
            "tenant_1",
            "field_1",
            "soil_sensor",
            "حساس موجود",
            "Existing Sensor",
        )

        # Auto-registration should return existing device
        device = registry.auto_register(
            device_id="existing_dev",
            tenant_id="tenant_1",
            field_id="field_1",
            sensor_type="soil_moisture",
        )

        assert device.name_ar == "حساس موجود"  # Original name preserved

    def test_auto_register_infers_device_type_soil(self):
        """Test auto-registration infers soil sensor type"""
        registry = DeviceRegistry()

        for sensor_type in ["soil_moisture", "soil_temperature", "soil_ec", "soil_ph"]:
            device = registry.auto_register(
                device_id=f"dev_{sensor_type}",
                tenant_id="tenant_1",
                field_id="field_1",
                sensor_type=sensor_type,
            )
            assert device.device_type == "soil_sensor"

    def test_auto_register_infers_device_type_weather(self):
        """Test auto-registration infers weather station type"""
        registry = DeviceRegistry()

        for sensor_type in [
            "air_temperature",
            "air_humidity",
            "wind_speed",
            "rainfall",
        ]:
            device = registry.auto_register(
                device_id=f"dev_{sensor_type}",
                tenant_id="tenant_1",
                field_id="field_1",
                sensor_type=sensor_type,
            )
            assert device.device_type == "weather_station"

    def test_auto_register_infers_device_type_water(self):
        """Test auto-registration infers water sensor types"""
        registry = DeviceRegistry()

        device1 = registry.auto_register(
            device_id="water_level_dev",
            tenant_id="tenant_1",
            field_id="field_1",
            sensor_type="water_level",
        )
        assert device1.device_type == "water_sensor"

        device2 = registry.auto_register(
            device_id="water_flow_dev",
            tenant_id="tenant_1",
            field_id="field_1",
            sensor_type="water_flow",
        )
        assert device2.device_type == "flow_meter"

    def test_auto_register_unknown_sensor_type(self):
        """Test auto-registration with unknown sensor type"""
        registry = DeviceRegistry()

        device = registry.auto_register(
            device_id="unknown_dev",
            tenant_id="tenant_1",
            field_id="field_1",
            sensor_type="unknown_sensor_type",
        )

        assert device.device_type == "unknown"


class TestRegistrySingleton:
    """Test registry singleton pattern"""

    def test_get_registry_returns_singleton(self):
        """Test that get_registry returns the same instance"""
        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2

    def test_get_registry_persists_data(self):
        """Test that registry data persists across get_registry calls"""
        registry1 = get_registry()
        registry1.register("persistent_dev", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        registry2 = get_registry()
        device = registry2.get("persistent_dev")

        assert device is not None
        assert device.device_id == "persistent_dev"


class TestConcurrentOperations:
    """Test concurrent operations on registry"""

    def test_multiple_status_updates(self):
        """Test multiple status updates on same device"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        # Multiple status updates
        for i in range(5):
            registry.update_status(
                device_id="dev_001",
                status=DeviceStatus.ONLINE,
                battery_level=100 - i * 10,
            )

        device = registry.get("dev_001")
        assert device.battery_level == 60  # Last update

    def test_register_many_devices_rapidly(self):
        """Test registering many devices rapidly"""
        registry = DeviceRegistry()

        # Register 100 devices
        for i in range(100):
            registry.register(
                f"bulk_dev_{i:03d}",
                "tenant_1",
                "field_1",
                "soil_sensor",
                f"حساس {i}",
                f"Sensor {i}",
            )

        assert len(registry.list_all()) == 100

    def test_mixed_operations(self):
        """Test mixed registry operations"""
        registry = DeviceRegistry()

        # Register
        for i in range(10):
            registry.register(
                f"dev_{i}", "tenant_1", f"field_{i % 3}", "soil_sensor", f"ح{i}", f"S{i}"
            )

        # Update some
        for i in range(5):
            registry.update_status(f"dev_{i}", DeviceStatus.ONLINE)

        # Delete some
        for i in range(5, 8):
            registry.delete(f"dev_{i}")

        # Verify
        assert len(registry.list_all()) == 7
        devices = registry.get_by_field("field_0")
        assert len(devices) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_device_id(self):
        """Test behavior with empty device_id"""
        registry = DeviceRegistry()

        # Should still work (validation happens at API layer)
        device = registry.register("", "tenant_1", "field_1", "sensor", "ح", "S")
        assert device.device_id == ""

    def test_very_long_device_id(self):
        """Test behavior with very long device_id"""
        registry = DeviceRegistry()
        long_id = "dev_" + "x" * 1000

        device = registry.register(long_id, "tenant_1", "field_1", "sensor", "ح", "S")
        assert device.device_id == long_id

    def test_special_characters_in_ids(self):
        """Test device IDs with special characters"""
        registry = DeviceRegistry()

        special_ids = [
            "dev-001",
            "dev_001",
            "dev.001",
            "dev@001",
            "dev#001",
            "デバイス-001",
            "جهاز-001",
        ]

        for device_id in special_ids:
            device = registry.register(device_id, "tenant_1", "field_1", "sensor", "ح", "S")
            assert device.device_id == device_id

    def test_zero_battery_level(self):
        """Test device with zero battery level"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        device = registry.update_status(device_id="dev_001", battery_level=0)

        assert device.battery_level == 0
        assert device.status == DeviceStatus.WARNING.value

    def test_negative_signal_strength(self):
        """Test device with negative signal strength (RSSI)"""
        registry = DeviceRegistry()
        registry.register("dev_001", "tenant_1", "field_1", "soil_sensor", "حساس", "Sensor")

        device = registry.update_status(device_id="dev_001", signal_strength=-120)

        assert device.signal_strength == -120

    def test_unicode_in_names(self):
        """Test device with Unicode characters in names"""
        registry = DeviceRegistry()

        device = registry.register(
            "dev_001",
            "tenant_1",
            "field_1",
            "soil_sensor",
            "حساس رطوبة التربة المتقدم 🌱",
            "Advanced Soil Moisture Sensor 🌱",
        )

        assert "🌱" in device.name_ar
        assert "🌱" in device.name_en
