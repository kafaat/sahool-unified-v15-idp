"""
IoT Dashboard Module | وحدة لوحة تحكم إنترنت الأشياء

Provides real-time IoT dashboard data:
- Sensor readings visualization
- Threshold alerts
- Device management
- Integration with Jetson Orin edge devices
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class SensorType(StrEnum):
    SOIL_MOISTURE = "soil_moisture"
    SOIL_TEMPERATURE = "soil_temperature"
    SOIL_PH = "soil_ph"
    SOIL_EC = "soil_ec"
    AIR_TEMPERATURE = "air_temperature"
    AIR_HUMIDITY = "air_humidity"
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    RAINFALL = "rainfall"
    SOLAR_RADIATION = "solar_radiation"
    LEAF_WETNESS = "leaf_wetness"
    CO2 = "co2"
    WATER_FLOW = "water_flow"
    WATER_LEVEL = "water_level"
    NDVI_SENSOR = "ndvi_sensor"


class DeviceStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    LOW_BATTERY = "low_battery"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


SENSOR_TYPE_AR = {
    SensorType.SOIL_MOISTURE: "رطوبة التربة",
    SensorType.SOIL_TEMPERATURE: "حرارة التربة",
    SensorType.SOIL_PH: "حموضة التربة",
    SensorType.SOIL_EC: "توصيل التربة الكهربائي",
    SensorType.AIR_TEMPERATURE: "حرارة الهواء",
    SensorType.AIR_HUMIDITY: "رطوبة الهواء",
    SensorType.WIND_SPEED: "سرعة الرياح",
    SensorType.WIND_DIRECTION: "اتجاه الرياح",
    SensorType.RAINFALL: "هطول الأمطار",
    SensorType.SOLAR_RADIATION: "الإشعاع الشمسي",
    SensorType.LEAF_WETNESS: "رطوبة الأوراق",
    SensorType.CO2: "ثاني أكسيد الكربون",
    SensorType.WATER_FLOW: "تدفق المياه",
    SensorType.WATER_LEVEL: "مستوى المياه",
    SensorType.NDVI_SENSOR: "مستشعر NDVI",
}

DEVICE_STATUS_AR = {
    DeviceStatus.ONLINE: "متصل",
    DeviceStatus.OFFLINE: "غير متصل",
    DeviceStatus.LOW_BATTERY: "بطارية منخفضة",
    DeviceStatus.ERROR: "خطأ",
    DeviceStatus.MAINTENANCE: "صيانة",
}

# Sensor thresholds for agricultural alerts
SENSOR_THRESHOLDS = {
    SensorType.SOIL_MOISTURE: {"low": 20.0, "high": 80.0, "unit": "%", "unit_ar": "%"},
    SensorType.SOIL_TEMPERATURE: {"low": 5.0, "high": 40.0, "unit": "°C", "unit_ar": "°م"},
    SensorType.SOIL_PH: {"low": 5.5, "high": 8.5, "unit": "pH", "unit_ar": "pH"},
    SensorType.SOIL_EC: {"low": 0.5, "high": 4.0, "unit": "dS/m", "unit_ar": "ديسي سيمنز/م"},
    SensorType.AIR_TEMPERATURE: {"low": 0.0, "high": 45.0, "unit": "°C", "unit_ar": "°م"},
    SensorType.AIR_HUMIDITY: {"low": 20.0, "high": 90.0, "unit": "%", "unit_ar": "%"},
    SensorType.WIND_SPEED: {"low": 0.0, "high": 40.0, "unit": "km/h", "unit_ar": "كم/س"},
    SensorType.RAINFALL: {"low": 0.0, "high": 100.0, "unit": "mm", "unit_ar": "مم"},
}


@dataclass
class SensorReading:
    """A single sensor reading | قراءة مستشعر واحدة"""

    device_id: str = ""
    sensor_type: SensorType = SensorType.SOIL_MOISTURE
    sensor_type_ar: str = ""
    value: float = 0.0
    unit: str = ""
    unit_ar: str = ""
    timestamp: str = ""
    field_id: str = ""
    is_anomaly: bool = False


@dataclass
class IoTDevice:
    """An IoT device | جهاز إنترنت الأشياء"""

    device_id: str = ""
    device_name: str = ""
    device_name_ar: str = ""
    device_type: str = ""
    status: DeviceStatus = DeviceStatus.ONLINE
    status_ar: str = "متصل"
    battery_percent: float = 100.0
    field_id: str = ""
    sensors: list[SensorType] = field(default_factory=list)
    last_reading_at: str = ""
    firmware_version: str = ""


@dataclass
class ThresholdAlert:
    """A threshold alert | تنبيه عتبة"""

    alert_id: str = ""
    device_id: str = ""
    sensor_type: SensorType = SensorType.SOIL_MOISTURE
    sensor_type_ar: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    current_value: float = 0.0
    threshold: float = 0.0
    direction: str = "above"  # above or below
    message: str = ""
    message_ar: str = ""
    field_id: str = ""
    timestamp: str = ""


@dataclass
class IoTDashboardData:
    """IoT dashboard summary | ملخص لوحة تحكم IoT"""

    total_devices: int = 0
    online_devices: int = 0
    offline_devices: int = 0
    low_battery_devices: int = 0
    active_alerts: int = 0
    critical_alerts: int = 0
    latest_readings: list[SensorReading] = field(default_factory=list)
    alerts: list[ThresholdAlert] = field(default_factory=list)
    devices: list[IoTDevice] = field(default_factory=list)
    generated_at: str = ""
    message: str = ""
    message_ar: str = ""


class IoTDashboard:
    """IoT dashboard for real-time sensor monitoring.

    لوحة تحكم IoT لمراقبة المستشعرات في الوقت الفعلي.
    """

    def __init__(self):
        self._devices: dict[str, IoTDevice] = {}
        self._readings: list[SensorReading] = []

    def register_device(
        self,
        device_id: str,
        device_name: str,
        device_name_ar: str,
        device_type: str,
        field_id: str,
        sensors: list[SensorType],
    ) -> IoTDevice:
        """Register a new IoT device."""
        device = IoTDevice(
            device_id=device_id,
            device_name=device_name,
            device_name_ar=device_name_ar,
            device_type=device_type,
            status=DeviceStatus.ONLINE,
            status_ar=DEVICE_STATUS_AR[DeviceStatus.ONLINE],
            field_id=field_id,
            sensors=sensors,
        )
        self._devices[device_id] = device
        return device

    def add_reading(
        self,
        device_id: str,
        sensor_type: SensorType,
        value: float,
    ) -> SensorReading:
        """Add a sensor reading."""
        threshold = SENSOR_THRESHOLDS.get(sensor_type, {})
        is_anomaly = False
        if threshold:
            is_anomaly = value < threshold.get("low", float("-inf")) or value > threshold.get("high", float("inf"))

        reading = SensorReading(
            device_id=device_id,
            sensor_type=sensor_type,
            sensor_type_ar=SENSOR_TYPE_AR.get(sensor_type, ""),
            value=value,
            unit=threshold.get("unit", ""),
            unit_ar=threshold.get("unit_ar", ""),
            timestamp=datetime.now(UTC).isoformat(),
            is_anomaly=is_anomaly,
        )
        self._readings.append(reading)

        if device_id in self._devices:
            self._devices[device_id].last_reading_at = reading.timestamp

        return reading

    def check_thresholds(self) -> list[ThresholdAlert]:
        """Check all recent readings against thresholds."""
        alerts = []
        for reading in self._readings[-100:]:
            threshold = SENSOR_THRESHOLDS.get(reading.sensor_type, {})
            if not threshold:
                continue

            if reading.value < threshold.get("low", float("-inf")):
                alerts.append(
                    ThresholdAlert(
                        alert_id=f"ALT-{len(alerts) + 1:04d}",
                        device_id=reading.device_id,
                        sensor_type=reading.sensor_type,
                        sensor_type_ar=SENSOR_TYPE_AR.get(reading.sensor_type, ""),
                        severity=AlertSeverity.CRITICAL
                        if reading.sensor_type in (SensorType.SOIL_MOISTURE, SensorType.AIR_TEMPERATURE)
                        else AlertSeverity.WARNING,
                        current_value=reading.value,
                        threshold=threshold["low"],
                        direction="below",
                        message=f"{reading.sensor_type.value} below threshold: {reading.value} < {threshold['low']}",
                        message_ar=f"{SENSOR_TYPE_AR.get(reading.sensor_type, '')} أقل من الحد: {reading.value} < {threshold['low']}",
                        timestamp=reading.timestamp,
                    )
                )

            if reading.value > threshold.get("high", float("inf")):
                alerts.append(
                    ThresholdAlert(
                        alert_id=f"ALT-{len(alerts) + 1:04d}",
                        device_id=reading.device_id,
                        sensor_type=reading.sensor_type,
                        sensor_type_ar=SENSOR_TYPE_AR.get(reading.sensor_type, ""),
                        severity=AlertSeverity.CRITICAL,
                        current_value=reading.value,
                        threshold=threshold["high"],
                        direction="above",
                        message=f"{reading.sensor_type.value} above threshold: {reading.value} > {threshold['high']}",
                        message_ar=f"{SENSOR_TYPE_AR.get(reading.sensor_type, '')} أعلى من الحد: {reading.value} > {threshold['high']}",
                        timestamp=reading.timestamp,
                    )
                )

        return alerts

    def get_dashboard(self) -> IoTDashboardData:
        """Get complete dashboard data."""
        devices = list(self._devices.values())
        online = sum(1 for d in devices if d.status == DeviceStatus.ONLINE)
        offline = sum(1 for d in devices if d.status == DeviceStatus.OFFLINE)
        low_bat = sum(1 for d in devices if d.battery_percent < 20)

        alerts = self.check_thresholds()
        critical = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)

        return IoTDashboardData(
            total_devices=len(devices),
            online_devices=online,
            offline_devices=offline,
            low_battery_devices=low_bat,
            active_alerts=len(alerts),
            critical_alerts=critical,
            latest_readings=self._readings[-20:],
            alerts=alerts[:10],
            devices=devices,
            generated_at=datetime.now(UTC).isoformat(),
            message=f"IoT: {online}/{len(devices)} online, {len(alerts)} alerts",
            message_ar=f"IoT: {online}/{len(devices)} متصل، {len(alerts)} تنبيهات",
        )
