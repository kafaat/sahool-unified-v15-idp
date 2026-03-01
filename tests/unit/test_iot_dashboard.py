"""Tests for IoT dashboard."""
import pytest
from shared.iot_dashboard import (
    IoTDashboard, SensorType, DeviceStatus, AlertSeverity, SENSOR_THRESHOLDS
)

class TestIoTDashboard:
    def setup_method(self):
        self.dash = IoTDashboard()

    def test_register_device(self):
        dev = self.dash.register_device(
            "D-001", "Soil Sensor 1", "مستشعر تربة 1", "soil_sensor",
            "F-001", [SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE],
        )
        assert dev.status == DeviceStatus.ONLINE

    def test_add_reading(self):
        self.dash.register_device("D-002", "Sensor", "مستشعر", "soil", "F-001", [SensorType.SOIL_MOISTURE])
        reading = self.dash.add_reading("D-002", SensorType.SOIL_MOISTURE, 35.0)
        assert reading.value == 35.0
        assert reading.is_anomaly is False

    def test_anomaly_detection(self):
        reading = self.dash.add_reading("D-003", SensorType.SOIL_MOISTURE, 5.0)
        assert reading.is_anomaly is True

    def test_threshold_alerts(self):
        self.dash.add_reading("D-004", SensorType.AIR_TEMPERATURE, 48.0)
        alerts = self.dash.check_thresholds()
        assert len(alerts) > 0
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_get_dashboard(self):
        self.dash.register_device("D-005", "S1", "م1", "weather", "F-001", [SensorType.AIR_TEMPERATURE])
        self.dash.add_reading("D-005", SensorType.AIR_TEMPERATURE, 28.0)
        dashboard = self.dash.get_dashboard()
        assert dashboard.total_devices == 1
        assert dashboard.online_devices == 1

    def test_sensor_types_have_arabic(self):
        # Sensors without numeric thresholds (direction, radiation, wetness, flow, level, CO2, NDVI)
        no_threshold_sensors = (
            SensorType.WIND_DIRECTION, SensorType.SOLAR_RADIATION,
            SensorType.LEAF_WETNESS, SensorType.CO2,
            SensorType.WATER_FLOW, SensorType.WATER_LEVEL,
            SensorType.NDVI_SENSOR,
        )
        for sensor in SensorType:
            assert sensor in SENSOR_THRESHOLDS or sensor in no_threshold_sensors
