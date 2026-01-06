"""
نماذج الأحداث الحقلية - Field Events Models
Agricultural field events and anomalies
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """أنواع الأحداث - Event Types"""

    NDVI_DROP = "ndvi_drop"  # انخفاض مؤشر NDVI
    NDVI_ANOMALY = "ndvi_anomaly"  # شذوذ في NDVI
    WEATHER_ALERT = "weather_alert"  # تنبيه طقس
    SOIL_MOISTURE_LOW = "soil_moisture_low"  # رطوبة تربة منخفضة
    SOIL_MOISTURE_HIGH = "soil_moisture_high"  # رطوبة تربة عالية
    TEMPERATURE_EXTREME = "temperature_extreme"  # درجة حرارة متطرفة
    PEST_DETECTION = "pest_detection"  # كشف آفات
    DISEASE_DETECTION = "disease_detection"  # كشف أمراض
    IRRIGATION_NEEDED = "irrigation_needed"  # حاجة للري
    HARVEST_READY = "harvest_ready"  # جاهز للحصاد
    ASTRONOMICAL_EVENT = "astronomical_event"  # حدث فلكي (زراعة/حصاد)
    CUSTOM = "custom"  # حدث مخصص


class EventStatus(str, Enum):
    """حالات الحدث - Event Status"""

    ACTIVE = "active"  # نشط
    ACKNOWLEDGED = "acknowledged"  # تم الإقرار
    RESOLVED = "resolved"  # تم الحل
    IGNORED = "ignored"  # تم التجاهل


class EventSeverity(str, Enum):
    """درجات خطورة الحدث - Event Severity"""

    LOW = "low"  # منخفضة
    MEDIUM = "medium"  # متوسطة
    HIGH = "high"  # عالية
    CRITICAL = "critical"  # حرجة


# ═══════════════════════════════════════════════════════════════════════════════
# Base Event Models
# ═══════════════════════════════════════════════════════════════════════════════


class FieldEvent(BaseModel):
    """
    نموذج الحدث الحقلي الأساسي
    Base Field Event Model
    """

    event_id: str
    tenant_id: str
    field_id: str
    event_type: EventType
    severity: EventSeverity
    status: EventStatus = EventStatus.ACTIVE
    title: str
    title_ar: str | None = None
    description: str
    description_ar: str | None = None
    source_service: str  # e.g., "ndvi-engine", "weather-service", "iot-gateway"
    metadata: dict[str, Any] = Field(default_factory=dict)
    location: dict[str, float] | None = None  # {lat, lon}
    created_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    correlation_id: str | None = None  # للربط مع أحداث أخرى


class EventCreate(BaseModel):
    """
    إنشاء حدث جديد
    Create New Event
    """

    tenant_id: str
    field_id: str
    event_type: EventType
    severity: EventSeverity
    title: str
    title_ar: str | None = None
    description: str
    description_ar: str | None = None
    source_service: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    location: dict[str, float] | None = None
    correlation_id: str | None = None


class EventResponse(BaseModel):
    """
    استجابة الحدث
    Event Response
    """

    event_id: str
    tenant_id: str
    field_id: str
    event_type: EventType
    severity: EventSeverity
    status: EventStatus
    title: str
    title_ar: str | None = None
    description: str
    description_ar: str | None = None
    source_service: str
    metadata: dict[str, Any]
    location: dict[str, float] | None = None
    created_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    correlation_id: str | None = None
    triggered_rules: list[str] = Field(
        default_factory=list, description="معرفات القواعد التي تم تفعيلها"
    )
    created_tasks: list[str] = Field(
        default_factory=list, description="معرفات المهام التي تم إنشاؤها"
    )
    notifications_sent: int = Field(default=0, description="عدد الإشعارات المرسلة")


# ═══════════════════════════════════════════════════════════════════════════════
# Specific Event Types
# ═══════════════════════════════════════════════════════════════════════════════


class NDVIDropEvent(BaseModel):
    """
    حدث انخفاض NDVI
    NDVI Drop Event Data
    """

    current_ndvi: float = Field(..., ge=0.0, le=1.0)
    previous_ndvi: float = Field(..., ge=0.0, le=1.0)
    drop_percentage: float
    threshold: float
    analysis_date: datetime
    affected_area_hectares: float | None = None
    image_url: str | None = None
    satellite_source: str | None = None


class WeatherAlertEvent(BaseModel):
    """
    حدث تنبيه الطقس
    Weather Alert Event Data
    """

    alert_type: str  # e.g., "frost", "heatwave", "storm", "drought"
    alert_type_ar: str | None = None
    weather_condition: str
    temperature_celsius: float | None = None
    humidity_percent: float | None = None
    wind_speed_kmh: float | None = None
    precipitation_mm: float | None = None
    forecast_hours: int  # عدد ساعات التوقع
    recommendations: list[str] = Field(default_factory=list)
    recommendations_ar: list[str] = Field(default_factory=list)


class SoilMoistureEvent(BaseModel):
    """
    حدث رطوبة التربة
    Soil Moisture Event Data
    """

    current_moisture_percent: float = Field(..., ge=0.0, le=100.0)
    optimal_min: float
    optimal_max: float
    sensor_id: str | None = None
    depth_cm: int | None = None  # عمق القياس بالسنتيمتر
    measurement_time: datetime
    zone_id: str | None = None
    irrigation_recommendation: str | None = None
    irrigation_recommendation_ar: str | None = None


class AstronomicalEvent(BaseModel):
    """
    حدث فلكي زراعي
    Astronomical Agricultural Event
    """

    event_name: str
    event_name_ar: str
    event_date: datetime
    event_category: str  # "planting", "harvest", "maintenance"
    moon_phase: str | None = None
    moon_phase_ar: str | None = None
    recommended_crops: list[str] = Field(default_factory=list)
    recommended_crops_ar: list[str] = Field(default_factory=list)
    traditional_practice: str | None = None
    traditional_practice_ar: str | None = None
    scientific_rationale: str | None = None
    scientific_rationale_ar: str | None = None
