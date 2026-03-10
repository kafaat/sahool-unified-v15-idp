"""
Tests for IoT Dashboard | اختبارات لوحة تحكم إنترنت الأشياء

Tests cover sensor registration, readings, anomaly detection,
threshold alerts, and dashboard summary generation.
"""

from __future__ import annotations

import pytest

from shared.iot_dashboard import (
    DEVICE_STATUS_AR,
    SENSOR_THRESHOLDS,
    SENSOR_TYPE_AR,
    AlertSeverity,
    DeviceStatus,
    IoTDashboard,
    IoTDashboardData,
    IoTDevice,
    SensorReading,
    SensorType,
    ThresholdAlert,
)


class TestDeviceRegistration:
    """Tests for IoT device registration | اختبارات تسجيل الأجهزة"""

    def setup_method(self) -> None:
        self.dash = IoTDashboard()

    def test_register_device(self) -> None:
        """Register a device and verify its fields."""
        dev = self.dash.register_device(
            "D-001",
            "Soil Sensor 1",
            "مستشعر تربة 1",
            "soil_sensor",
            "F-001",
            [SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE],
        )
        assert isinstance(dev, IoTDevice)
        assert dev.device_id == "D-001"
        assert dev.device_name == "Soil Sensor 1"
        assert dev.device_name_ar == "مستشعر تربة 1"
        assert dev.status == DeviceStatus.ONLINE

    def test_device_status_arabic(self) -> None:
        """Registered device has Arabic status label | حالة الجهاز بالعربية"""
        dev = self.dash.register_device(
            "D-002",
            "Weather Station",
            "محطة طقس",
            "weather",
            "F-001",
            [SensorType.AIR_TEMPERATURE],
        )
        assert dev.status_ar == "متصل"

    def test_device_stored_internally(self) -> None:
        """Registered device is stored in internal dict."""
        self.dash.register_device(
            "D-003",
            "S3",
            "م3",
            "soil",
            "F-001",
            [SensorType.SOIL_PH],
        )
        assert "D-003" in self.dash._devices

    def test_device_sensors_list(self) -> None:
        """Device sensors list is correctly stored."""
        sensors = [SensorType.SOIL_MOISTURE, SensorType.SOIL_EC, SensorType.SOIL_PH]
        dev = self.dash.register_device("D-004", "Multi", "متعدد", "multi", "F-002", sensors)
        assert dev.sensors == sensors

    def test_multiple_devices_registered(self) -> None:
        """Register multiple devices."""
        self.dash.register_device("D-010", "A", "أ", "soil", "F-001", [SensorType.SOIL_MOISTURE])
        self.dash.register_device("D-011", "B", "ب", "weather", "F-001", [SensorType.AIR_TEMPERATURE])
        assert len(self.dash._devices) == 2


class TestSensorReadings:
    """Tests for adding sensor readings | اختبارات قراءات المستشعرات"""

    def setup_method(self) -> None:
        self.dash = IoTDashboard()
        self.dash.register_device(
            "D-100",
            "Sensor",
            "مستشعر",
            "soil",
            "F-001",
            [SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE],
        )

    def test_add_reading_normal(self) -> None:
        """Normal reading within thresholds is not anomaly."""
        reading = self.dash.add_reading("D-100", SensorType.SOIL_MOISTURE, 45.0)
        assert isinstance(reading, SensorReading)
        assert reading.value == 45.0
        assert reading.is_anomaly is False

    def test_reading_has_arabic_type(self) -> None:
        """Reading has Arabic sensor type label | نوع المستشعر بالعربية"""
        reading = self.dash.add_reading("D-100", SensorType.SOIL_MOISTURE, 50.0)
        assert reading.sensor_type_ar == "رطوبة التربة"

    def test_reading_has_unit(self) -> None:
        """Reading has appropriate unit and Arabic unit."""
        reading = self.dash.add_reading("D-100", SensorType.SOIL_MOISTURE, 30.0)
        assert reading.unit == "%"
        assert reading.unit_ar == "%"

    def test_reading_has_timestamp(self) -> None:
        """Reading has a timestamp."""
        reading = self.dash.add_reading("D-100", SensorType.SOIL_MOISTURE, 40.0)
        assert reading.timestamp != ""

    def test_reading_updates_device_last_reading(self) -> None:
        """Adding a reading updates the device's last_reading_at."""
        reading = self.dash.add_reading("D-100", SensorType.SOIL_MOISTURE, 35.0)
        dev = self.dash._devices["D-100"]
        assert dev.last_reading_at == reading.timestamp

    def test_reading_stored_in_list(self) -> None:
        """Readings are stored in internal list."""
        self.dash.add_reading("D-100", SensorType.SOIL_MOISTURE, 30.0)
        self.dash.add_reading("D-100", SensorType.SOIL_TEMPERATURE, 22.0)
        assert len(self.dash._readings) == 2


class TestAnomalyDetection:
    """Tests for anomaly detection in readings | اختبارات كشف الشذوذ"""

    def setup_method(self) -> None:
        self.dash = IoTDashboard()

    def test_below_threshold_is_anomaly(self) -> None:
        """Reading below low threshold is anomaly | قراءة أقل من الحد"""
        reading = self.dash.add_reading("D-200", SensorType.SOIL_MOISTURE, 5.0)
        assert reading.is_anomaly is True

    def test_above_threshold_is_anomaly(self) -> None:
        """Reading above high threshold is anomaly | قراءة أعلى من الحد"""
        reading = self.dash.add_reading("D-201", SensorType.SOIL_MOISTURE, 95.0)
        assert reading.is_anomaly is True

    def test_within_threshold_not_anomaly(self) -> None:
        """Reading within threshold is not anomaly."""
        reading = self.dash.add_reading("D-202", SensorType.AIR_TEMPERATURE, 25.0)
        assert reading.is_anomaly is False

    def test_extreme_temperature_anomaly(self) -> None:
        """Extreme temperature triggers anomaly."""
        reading = self.dash.add_reading("D-203", SensorType.AIR_TEMPERATURE, 48.0)
        assert reading.is_anomaly is True

    def test_sensor_without_threshold(self) -> None:
        """Sensor type without defined threshold is not anomaly."""
        reading = self.dash.add_reading("D-204", SensorType.WIND_DIRECTION, 180.0)
        assert reading.is_anomaly is False


class TestThresholdAlerts:
    """Tests for threshold alert generation | اختبارات تنبيهات العتبة"""

    def setup_method(self) -> None:
        self.dash = IoTDashboard()

    def test_high_temp_generates_critical_alert(self) -> None:
        """Temperature above threshold generates critical alert."""
        self.dash.add_reading("D-300", SensorType.AIR_TEMPERATURE, 48.0)
        alerts = self.dash.check_thresholds()
        assert len(alerts) > 0
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].direction == "above"

    def test_low_moisture_generates_critical_alert(self) -> None:
        """Low soil moisture generates critical alert."""
        self.dash.add_reading("D-301", SensorType.SOIL_MOISTURE, 10.0)
        alerts = self.dash.check_thresholds()
        assert len(alerts) > 0
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        assert len(critical_alerts) > 0

    def test_alert_has_bilingual_message(self) -> None:
        """Alert has both English and Arabic messages | تنبيه ثنائي اللغة"""
        self.dash.add_reading("D-302", SensorType.SOIL_MOISTURE, 5.0)
        alerts = self.dash.check_thresholds()
        assert len(alerts) > 0
        assert alerts[0].message != ""
        assert alerts[0].message_ar != ""

    def test_alert_has_sensor_type_arabic(self) -> None:
        """Alert has Arabic sensor type label."""
        self.dash.add_reading("D-303", SensorType.AIR_TEMPERATURE, 48.0)
        alerts = self.dash.check_thresholds()
        assert alerts[0].sensor_type_ar != ""

    def test_no_alerts_for_normal_readings(self) -> None:
        """Normal readings should not generate alerts."""
        self.dash.add_reading("D-304", SensorType.AIR_TEMPERATURE, 25.0)
        self.dash.add_reading("D-304", SensorType.SOIL_MOISTURE, 45.0)
        alerts = self.dash.check_thresholds()
        assert len(alerts) == 0

    def test_alert_id_format(self) -> None:
        """Alert IDs follow expected format."""
        self.dash.add_reading("D-305", SensorType.AIR_TEMPERATURE, 50.0)
        alerts = self.dash.check_thresholds()
        assert alerts[0].alert_id.startswith("ALT-")


class TestDashboardSummary:
    """Tests for dashboard summary generation | اختبارات ملخص لوحة التحكم"""

    def setup_method(self) -> None:
        self.dash = IoTDashboard()

    def test_empty_dashboard(self) -> None:
        """Empty dashboard returns zeros."""
        data = self.dash.get_dashboard()
        assert isinstance(data, IoTDashboardData)
        assert data.total_devices == 0
        assert data.online_devices == 0

    def test_dashboard_with_devices(self) -> None:
        """Dashboard counts devices correctly."""
        self.dash.register_device("D-400", "A", "أ", "soil", "F-001", [SensorType.SOIL_MOISTURE])
        self.dash.register_device("D-401", "B", "ب", "weather", "F-001", [SensorType.AIR_TEMPERATURE])
        data = self.dash.get_dashboard()
        assert data.total_devices == 2
        assert data.online_devices == 2

    def test_dashboard_with_readings(self) -> None:
        """Dashboard includes latest readings."""
        self.dash.register_device("D-410", "S1", "م1", "soil", "F-001", [SensorType.SOIL_MOISTURE])
        self.dash.add_reading("D-410", SensorType.SOIL_MOISTURE, 35.0)
        data = self.dash.get_dashboard()
        assert len(data.latest_readings) > 0

    def test_dashboard_alert_count(self) -> None:
        """Dashboard counts alerts correctly."""
        self.dash.add_reading("D-420", SensorType.AIR_TEMPERATURE, 50.0)
        data = self.dash.get_dashboard()
        assert data.active_alerts > 0
        assert data.critical_alerts > 0

    def test_dashboard_bilingual_message(self) -> None:
        """Dashboard has bilingual summary message | رسالة ملخص ثنائية اللغة"""
        self.dash.register_device("D-430", "S1", "م1", "soil", "F-001", [SensorType.SOIL_MOISTURE])
        data = self.dash.get_dashboard()
        assert data.message != ""
        assert data.message_ar != ""
        assert "متصل" in data.message_ar or "تنبيهات" in data.message_ar

    def test_dashboard_has_timestamp(self) -> None:
        """Dashboard has generated_at timestamp."""
        data = self.dash.get_dashboard()
        assert data.generated_at != ""


class TestSensorTranslations:
    """Tests for sensor type Arabic translations | اختبارات ترجمة أنواع المستشعرات"""

    def test_all_sensor_types_have_arabic(self) -> None:
        """Every SensorType has an Arabic label."""
        for sensor in SensorType:
            assert sensor in SENSOR_TYPE_AR, f"{sensor} missing Arabic translation"

    def test_all_device_statuses_have_arabic(self) -> None:
        """Every DeviceStatus has an Arabic label."""
        for status in DeviceStatus:
            assert status in DEVICE_STATUS_AR, f"{status} missing Arabic translation"

    def test_threshold_sensors_have_units(self) -> None:
        """Sensors with thresholds have both unit and unit_ar."""
        for sensor, threshold in SENSOR_THRESHOLDS.items():
            assert "unit" in threshold, f"{sensor} missing unit"
            assert "unit_ar" in threshold, f"{sensor} missing unit_ar"

    def test_sensors_without_thresholds(self) -> None:
        """Some sensors (direction, radiation, etc.) may not have thresholds."""
        no_threshold = {
            SensorType.WIND_DIRECTION,
            SensorType.SOLAR_RADIATION,
            SensorType.LEAF_WETNESS,
            SensorType.CO2,
            SensorType.WATER_FLOW,
            SensorType.WATER_LEVEL,
            SensorType.NDVI_SENSOR,
        }
        for sensor in SensorType:
            assert sensor in SENSOR_THRESHOLDS or sensor in no_threshold, (
                f"{sensor} not in thresholds or no_threshold set"
            )
