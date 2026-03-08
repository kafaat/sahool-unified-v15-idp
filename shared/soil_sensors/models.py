"""
Soil Sensors Models - نماذج مجسات التربة
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class SensorType(StrEnum):
    """Type of soil sensor"""

    MOISTURE = "moisture"  # رطوبة التربة
    TEMPERATURE = "temperature"  # حرارة التربة
    EC = "electrical_conductivity"  # الموصلية الكهربائية
    PH = "ph"  # درجة الحموضة
    NPK = "npk"  # النيتروجين والفسفور والبوتاسيوم
    SALINITY = "salinity"  # الملوحة
    WATER_LEVEL = "water_level"  # مستوى المياه
    MULTI = "multi"  # متعدد القياسات


class SensorProtocol(StrEnum):
    """Communication protocol"""

    MQTT = "mqtt"
    LORAWAN = "lorawan"
    HTTP = "http"
    ZIGBEE = "zigbee"
    NBIOT = "nb-iot"
    CELLULAR = "cellular"


class SensorStatus(StrEnum):
    """Sensor operational status"""

    ACTIVE = "active"  # يعمل
    OFFLINE = "offline"  # غير متصل
    LOW_BATTERY = "low_battery"  # بطارية منخفضة
    MAINTENANCE = "maintenance"  # صيانة
    ERROR = "error"  # خطأ
    CALIBRATING = "calibrating"  # معايرة


class AlertSeverity(StrEnum):
    """Alert severity level"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SensorReading:
    """
    Single sensor reading - قراءة مجس واحدة
    """

    sensor_id: str
    timestamp: datetime
    reading_type: SensorType

    # Value
    value: float
    unit: str  # %, °C, mS/cm, pH, ppm, etc.

    # Quality
    quality: float = 1.0  # 0-1 quality score
    is_valid: bool = True

    # Location (if GPS-enabled)
    lat: float | None = None
    lng: float | None = None
    depth_cm: float | None = None  # Sensor depth

    # Raw data
    raw_value: float | None = None
    raw_unit: str | None = None

    # Metadata
    battery_percent: float | None = None
    signal_strength: int | None = None  # RSSI


@dataclass
class SoilSensor:
    """
    Soil sensor device - جهاز مجس التربة
    """

    id: str
    tenant_id: str
    field_id: str

    # Device info
    name: str
    name_ar: str
    sensor_type: SensorType
    protocol: SensorProtocol
    model: str  # Device model (e.g., "CropX-100", "Sensoterra-Probe")
    manufacturer: str

    # Location
    lat: float
    lng: float
    depth_cm: float = 30  # Installation depth

    # Status
    status: SensorStatus = SensorStatus.ACTIVE
    battery_percent: float | None = None
    last_reading_at: datetime | None = None
    last_seen_at: datetime | None = None

    # Configuration
    reading_interval_min: int = 60  # Reading frequency
    transmission_interval_min: int = 60  # Data transmission frequency

    # Thresholds for alerts
    min_threshold: float | None = None
    max_threshold: float | None = None
    critical_min: float | None = None
    critical_max: float | None = None

    # Calibration
    calibration: SensorCalibration | None = None
    last_calibrated_at: datetime | None = None

    # Network
    device_eui: str | None = None  # For LoRaWAN
    mqtt_topic: str | None = None  # For MQTT
    api_endpoint: str | None = None  # For HTTP

    # Metadata
    installed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "sensor_type": self.sensor_type.value,
            "protocol": self.protocol.value,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "location": {"lat": self.lat, "lng": self.lng, "depth_cm": self.depth_cm},
            "status": self.status.value,
            "battery_percent": self.battery_percent,
            "last_reading_at": self.last_reading_at.isoformat() if self.last_reading_at else None,
            "thresholds": {
                "min": self.min_threshold,
                "max": self.max_threshold,
                "critical_min": self.critical_min,
                "critical_max": self.critical_max,
            },
            "is_active": self.is_active,
        }


@dataclass
class SensorCalibration:
    """
    Sensor calibration data - بيانات معايرة المجس
    """

    sensor_id: str
    calibrated_at: datetime
    calibrated_by: str

    # Calibration points
    dry_value: float  # Reading in dry soil
    wet_value: float  # Reading in saturated soil
    known_dry_percent: float = 0.0  # Actual moisture %
    known_wet_percent: float = 100.0  # Actual moisture %

    # Correction factors
    offset: float = 0.0
    scale: float = 1.0

    # Soil type specific
    soil_type: str | None = None  # sandy, clay, loam
    soil_type_ar: str | None = None

    # Validity
    valid_until: datetime | None = None
    notes: str = ""

    def apply_calibration(self, raw_value: float) -> float:
        """Apply calibration to raw value"""
        # Linear interpolation between dry and wet points
        if self.wet_value == self.dry_value:
            return raw_value

        normalized = (raw_value - self.dry_value) / (self.wet_value - self.dry_value)
        calibrated = self.known_dry_percent + normalized * (self.known_wet_percent - self.known_dry_percent)

        # Apply offset and scale
        calibrated = (calibrated * self.scale) + self.offset

        # Clamp to valid range
        return max(0.0, min(100.0, calibrated))


@dataclass
class SensorAlert:
    """
    Sensor alert - تنبيه المجس
    """

    alert_id: str
    sensor_id: str
    field_id: str
    tenant_id: str
    timestamp: datetime

    # Alert type
    alert_type: str  # threshold_exceeded, sensor_offline, low_battery, etc.
    severity: AlertSeverity

    # Reading that triggered alert
    reading_value: float | None = None
    reading_unit: str | None = None
    threshold_value: float | None = None

    # Messages
    title_en: str = ""
    title_ar: str = ""
    message_en: str = ""
    message_ar: str = ""

    # Status
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved: bool = False
    resolved_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for NATS publishing"""
        return {
            "alert_id": self.alert_id,
            "sensor_id": self.sensor_id,
            "field_id": self.field_id,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp.isoformat(),
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "reading_value": self.reading_value,
            "reading_unit": self.reading_unit,
            "threshold_value": self.threshold_value,
            "title_en": self.title_en,
            "title_ar": self.title_ar,
            "message_en": self.message_en,
            "message_ar": self.message_ar,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
        }


@dataclass
class FieldMoistureMap:
    """
    Field moisture map from sensor interpolation
    خريطة رطوبة الحقل من استيفاء المجسات
    """

    field_id: str
    timestamp: datetime

    # Grid data
    grid_resolution_m: float = 10  # Meters per grid cell
    min_lat: float = 0.0
    max_lat: float = 0.0
    min_lng: float = 0.0
    max_lng: float = 0.0

    # Moisture values (2D grid)
    moisture_grid: list[list[float]] = field(default_factory=list)

    # Statistics
    avg_moisture: float = 0.0
    min_moisture: float = 0.0
    max_moisture: float = 0.0
    std_moisture: float = 0.0

    # Sensor coverage
    sensor_count: int = 0
    interpolation_method: str = "idw"  # inverse distance weighting

    # Recommendations
    dry_zones: list[dict] = field(default_factory=list)  # Areas needing water
    wet_zones: list[dict] = field(default_factory=list)  # Waterlogged areas


@dataclass
class SensorAggregation:
    """
    Aggregated sensor readings over time period
    قراءات المجس المجمعة خلال فترة زمنية
    """

    sensor_id: str
    field_id: str
    period_start: datetime
    period_end: datetime
    reading_type: SensorType

    # Aggregated values
    count: int = 0
    avg_value: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    std_value: float = 0.0

    # Trend
    trend: str = "stable"  # increasing, decreasing, stable
    trend_rate: float = 0.0  # Units per hour

    # Quality
    valid_readings: int = 0
    invalid_readings: int = 0
