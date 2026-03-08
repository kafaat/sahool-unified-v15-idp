"""
Weather Alerts Data Models
==========================
نماذج بيانات تنبيهات الطقس

Data models for weather alerts, forecasts, spray windows, and agricultural
timing recommendations.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from enum import StrEnum
from typing import Any


class AlertSeverity(StrEnum):
    """Alert severity levels | مستويات خطورة التنبيهات"""

    CRITICAL = "critical"  # حرج - Immediate action required
    WARNING = "warning"  # تحذير - Action within 24-48h
    ADVISORY = "advisory"  # استشارة - Action within 1 week
    WATCH = "watch"  # مراقبة - Be aware
    INFORMATION = "information"  # معلومات - For awareness only


class AlertType(StrEnum):
    """Types of weather alerts | أنواع تنبيهات الطقس"""

    FROST = "frost"  # صقيع
    HEAT = "heat"  # موجة حر
    WIND = "wind"  # رياح قوية
    HAIL = "hail"  # برد
    RAIN = "rain"  # أمطار غزيرة
    DROUGHT = "drought"  # جفاف
    SANDSTORM = "sandstorm"  # عاصفة رملية
    HUMIDITY = "humidity"  # رطوبة مرتفعة
    INVERSION = "inversion"  # انقلاب حراري
    UV = "uv"  # أشعة فوق بنفسجية


class SprayCondition(StrEnum):
    """Spray window condition status | حالة نافذة الرش"""

    OPTIMAL = "optimal"  # مثالي - All conditions ideal
    ACCEPTABLE = "acceptable"  # مقبول - Conditions within range
    MARGINAL = "marginal"  # هامشي - Some conditions borderline
    UNSUITABLE = "unsuitable"  # غير مناسب - One or more conditions out of range
    DANGEROUS = "dangerous"  # خطر - Drift risk or phytotoxicity risk


class IrrigationRecommendation(StrEnum):
    """Irrigation recommendation types | أنواع توصيات الري"""

    IRRIGATE_NOW = "irrigate_now"  # ري فوري
    IRRIGATE_SOON = "irrigate_soon"  # ري قريب
    DELAY_IRRIGATION = "delay_irrigation"  # تأجيل الري
    REDUCE_AMOUNT = "reduce_amount"  # تقليل الكمية
    INCREASE_AMOUNT = "increase_amount"  # زيادة الكمية
    SKIP_IRRIGATION = "skip_irrigation"  # تخطي الري
    MONITOR = "monitor"  # مراقبة


class HarvestCondition(StrEnum):
    """Harvest timing condition | حالة توقيت الحصاد"""

    OPTIMAL = "optimal"  # مثالي
    GOOD = "good"  # جيد
    ACCEPTABLE = "acceptable"  # مقبول
    RISKY = "risky"  # محفوف بالمخاطر
    UNSUITABLE = "unsuitable"  # غير مناسب


class CropType(StrEnum):
    """Supported crop types | أنواع المحاصيل المدعومة"""

    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    DATE_PALM = "date_palm"  # نخيل
    TOMATO = "tomato"  # طماطم
    CUCUMBER = "cucumber"  # خيار
    ALFALFA = "alfalfa"  # برسيم
    CITRUS = "citrus"  # حمضيات
    GRAPE = "grape"  # عنب
    OLIVE = "olive"  # زيتون
    GENERAL = "general"  # عام


@dataclass
class WeatherForecast:
    """
    Weather forecast data structure
    بيانات توقعات الطقس
    """

    # Time information
    forecast_date: date
    forecast_time: time | None = None
    hour: int | None = None  # 0-23 for hourly forecasts

    # Temperature (Celsius)
    temperature: float = 0.0
    temperature_min: float = 0.0
    temperature_max: float = 0.0
    feels_like: float | None = None
    dew_point: float | None = None

    # Humidity (%)
    humidity: float = 0.0
    humidity_min: float | None = None
    humidity_max: float | None = None

    # Wind
    wind_speed: float = 0.0  # km/h
    wind_gust: float | None = None  # km/h
    wind_direction: str | None = None  # N, NE, E, etc.
    wind_direction_degrees: int | None = None

    # Precipitation
    precipitation_probability: float = 0.0  # %
    precipitation_amount: float = 0.0  # mm
    precipitation_type: str | None = None  # rain, snow, hail

    # Atmospheric conditions
    pressure: float | None = None  # hPa
    visibility: float | None = None  # km
    cloud_cover: float | None = None  # %
    uv_index: int | None = None

    # Special conditions
    is_inversion_likely: bool = False
    inversion_start_hour: int | None = None
    inversion_end_hour: int | None = None

    # Source
    source: str = "weather_service"
    confidence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "forecast_date": self.forecast_date.isoformat(),
            "forecast_time": self.forecast_time.isoformat() if self.forecast_time else None,
            "hour": self.hour,
            "temperature": self.temperature,
            "temperature_min": self.temperature_min,
            "temperature_max": self.temperature_max,
            "feels_like": self.feels_like,
            "dew_point": self.dew_point,
            "humidity": self.humidity,
            "humidity_min": self.humidity_min,
            "humidity_max": self.humidity_max,
            "wind_speed": self.wind_speed,
            "wind_gust": self.wind_gust,
            "wind_direction": self.wind_direction,
            "wind_direction_degrees": self.wind_direction_degrees,
            "precipitation_probability": self.precipitation_probability,
            "precipitation_amount": self.precipitation_amount,
            "precipitation_type": self.precipitation_type,
            "pressure": self.pressure,
            "visibility": self.visibility,
            "cloud_cover": self.cloud_cover,
            "uv_index": self.uv_index,
            "is_inversion_likely": self.is_inversion_likely,
            "inversion_start_hour": self.inversion_start_hour,
            "inversion_end_hour": self.inversion_end_hour,
            "source": self.source,
            "confidence": self.confidence,
        }


@dataclass
class WeatherAlert:
    """
    Weather alert with bilingual support
    تنبيه طقس مع دعم ثنائي اللغة
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: AlertType = AlertType.FROST
    severity: AlertSeverity = AlertSeverity.WARNING

    # Location
    field_id: str | None = None
    farm_id: str | None = None
    location_name: str = ""
    location_name_ar: str = ""
    latitude: float | None = None
    longitude: float | None = None

    # Time validity
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    # Alert content - English
    title: str = ""
    description: str = ""
    impact: str = ""
    recommended_actions: list[str] = field(default_factory=list)

    # Alert content - Arabic
    title_ar: str = ""
    description_ar: str = ""
    impact_ar: str = ""
    recommended_actions_ar: list[str] = field(default_factory=list)

    # Weather data that triggered the alert
    trigger_value: float | None = None
    threshold_value: float | None = None
    trigger_unit: str = ""

    # Affected crops
    affected_crops: list[str] = field(default_factory=list)
    crop_damage_risk: str = ""  # low, medium, high, severe
    crop_damage_risk_ar: str = ""

    # Economic impact estimate
    potential_loss_min: float | None = None
    potential_loss_max: float | None = None
    currency: str = "SAR"

    # Status
    is_active: bool = True
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None

    # Metadata
    source: str = "weather_alerts"
    confidence: float = 0.8
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "field_id": self.field_id,
            "farm_id": self.farm_id,
            "location_name": self.location_name,
            "location_name_ar": self.location_name_ar,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "issued_at": self.issued_at.isoformat(),
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "recommended_actions": self.recommended_actions,
            "title_ar": self.title_ar,
            "description_ar": self.description_ar,
            "impact_ar": self.impact_ar,
            "recommended_actions_ar": self.recommended_actions_ar,
            "trigger_value": self.trigger_value,
            "threshold_value": self.threshold_value,
            "trigger_unit": self.trigger_unit,
            "affected_crops": self.affected_crops,
            "crop_damage_risk": self.crop_damage_risk,
            "crop_damage_risk_ar": self.crop_damage_risk_ar,
            "potential_loss_min": self.potential_loss_min,
            "potential_loss_max": self.potential_loss_max,
            "currency": self.currency,
            "is_active": self.is_active,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "source": self.source,
            "confidence": self.confidence,
            "tags": self.tags,
        }

    def get_priority_icon(self) -> str:
        """Get priority icon for display"""
        icons = {
            AlertSeverity.CRITICAL: "[!!!]",
            AlertSeverity.WARNING: "[!!]",
            AlertSeverity.ADVISORY: "[!]",
            AlertSeverity.WATCH: "[.]",
            AlertSeverity.INFORMATION: "[i]",
        }
        return icons.get(self.severity, "[.]")


@dataclass
class SprayWindow:
    """
    Spray window recommendation
    نافذة رش موصى بها
    """

    # Time window
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_hours: float = 0.0

    # Condition assessment
    overall_condition: SprayCondition = SprayCondition.UNSUITABLE
    score: float = 0.0  # 0-100

    # Individual factors (0-100 each)
    temperature_score: float = 0.0
    humidity_score: float = 0.0
    wind_score: float = 0.0
    inversion_score: float = 0.0
    rain_score: float = 0.0

    # Weather values during window
    temperature_avg: float = 0.0
    temperature_min: float = 0.0
    temperature_max: float = 0.0
    humidity_avg: float = 0.0
    wind_speed_avg: float = 0.0
    wind_speed_max: float = 0.0

    # Risk assessment
    drift_risk: str = "low"  # low, medium, high
    drift_risk_ar: str = "منخفض"
    evaporation_risk: str = "low"
    evaporation_risk_ar: str = "منخفض"
    phytotoxicity_risk: str = "low"
    phytotoxicity_risk_ar: str = "منخفض"

    # Recommendations - English
    recommendation: str = ""
    cautions: list[str] = field(default_factory=list)
    adjustments: list[str] = field(default_factory=list)

    # Recommendations - Arabic
    recommendation_ar: str = ""
    cautions_ar: list[str] = field(default_factory=list)
    adjustments_ar: list[str] = field(default_factory=list)

    # Inversion details
    is_inversion_period: bool = False
    inversion_warning: str = ""
    inversion_warning_ar: str = ""

    # Product considerations
    suitable_for_systemic: bool = True
    suitable_for_contact: bool = True
    suitable_for_volatile: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_hours": self.duration_hours,
            "overall_condition": self.overall_condition.value,
            "score": self.score,
            "temperature_score": self.temperature_score,
            "humidity_score": self.humidity_score,
            "wind_score": self.wind_score,
            "inversion_score": self.inversion_score,
            "rain_score": self.rain_score,
            "temperature_avg": self.temperature_avg,
            "temperature_min": self.temperature_min,
            "temperature_max": self.temperature_max,
            "humidity_avg": self.humidity_avg,
            "wind_speed_avg": self.wind_speed_avg,
            "wind_speed_max": self.wind_speed_max,
            "drift_risk": self.drift_risk,
            "drift_risk_ar": self.drift_risk_ar,
            "evaporation_risk": self.evaporation_risk,
            "evaporation_risk_ar": self.evaporation_risk_ar,
            "phytotoxicity_risk": self.phytotoxicity_risk,
            "phytotoxicity_risk_ar": self.phytotoxicity_risk_ar,
            "recommendation": self.recommendation,
            "cautions": self.cautions,
            "adjustments": self.adjustments,
            "recommendation_ar": self.recommendation_ar,
            "cautions_ar": self.cautions_ar,
            "adjustments_ar": self.adjustments_ar,
            "is_inversion_period": self.is_inversion_period,
            "inversion_warning": self.inversion_warning,
            "inversion_warning_ar": self.inversion_warning_ar,
            "suitable_for_systemic": self.suitable_for_systemic,
            "suitable_for_contact": self.suitable_for_contact,
            "suitable_for_volatile": self.suitable_for_volatile,
        }


@dataclass
class IrrigationSchedule:
    """
    Irrigation scheduling based on weather forecast
    جدولة الري بناء على توقعات الطقس
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str = ""
    crop_type: CropType = CropType.GENERAL

    # Recommendation
    recommendation: IrrigationRecommendation = IrrigationRecommendation.MONITOR

    # Timing
    recommended_date: date | None = None
    recommended_time: time | None = None
    optimal_window_start: datetime | None = None
    optimal_window_end: datetime | None = None

    # Amount
    recommended_amount_mm: float = 0.0
    original_amount_mm: float = 0.0
    adjustment_factor: float = 1.0

    # Weather factors
    expected_rain_mm: float = 0.0
    expected_et_mm: float = 0.0
    soil_moisture_current: float | None = None
    soil_moisture_target: float | None = None

    # Reasoning - English
    reason: str = ""
    factors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Reasoning - Arabic
    reason_ar: str = ""
    factors_ar: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    # Cost-benefit
    water_saved_liters: float | None = None
    cost_saved: float | None = None
    currency: str = "SAR"

    # Confidence
    confidence: float = 0.8
    forecast_days_used: int = 3

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "crop_type": self.crop_type.value,
            "recommendation": self.recommendation.value,
            "recommended_date": self.recommended_date.isoformat() if self.recommended_date else None,
            "recommended_time": self.recommended_time.isoformat() if self.recommended_time else None,
            "optimal_window_start": self.optimal_window_start.isoformat() if self.optimal_window_start else None,
            "optimal_window_end": self.optimal_window_end.isoformat() if self.optimal_window_end else None,
            "recommended_amount_mm": self.recommended_amount_mm,
            "original_amount_mm": self.original_amount_mm,
            "adjustment_factor": self.adjustment_factor,
            "expected_rain_mm": self.expected_rain_mm,
            "expected_et_mm": self.expected_et_mm,
            "soil_moisture_current": self.soil_moisture_current,
            "soil_moisture_target": self.soil_moisture_target,
            "reason": self.reason,
            "factors": self.factors,
            "warnings": self.warnings,
            "reason_ar": self.reason_ar,
            "factors_ar": self.factors_ar,
            "warnings_ar": self.warnings_ar,
            "water_saved_liters": self.water_saved_liters,
            "cost_saved": self.cost_saved,
            "currency": self.currency,
            "confidence": self.confidence,
            "forecast_days_used": self.forecast_days_used,
        }


@dataclass
class HarvestWindow:
    """
    Harvest timing recommendation
    توصية توقيت الحصاد
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str = ""
    crop_type: CropType = CropType.GENERAL

    # Timing window
    window_start: datetime | None = None
    window_end: datetime | None = None
    optimal_date: date | None = None
    optimal_time: time | None = None

    # Condition
    overall_condition: HarvestCondition = HarvestCondition.ACCEPTABLE
    score: float = 0.0  # 0-100

    # Weather conditions during window
    expected_rain_probability: float = 0.0
    expected_humidity_avg: float = 0.0
    expected_temperature_avg: float = 0.0
    dry_hours_available: float = 0.0

    # Risk factors
    rain_risk: str = "low"
    rain_risk_ar: str = "منخفض"
    moisture_risk: str = "low"
    moisture_risk_ar: str = "منخفض"
    quality_risk: str = "low"
    quality_risk_ar: str = "منخفض"

    # Recommendations - English
    recommendation: str = ""
    considerations: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)

    # Recommendations - Arabic
    recommendation_ar: str = ""
    considerations_ar: list[str] = field(default_factory=list)
    alternatives_ar: list[str] = field(default_factory=list)

    # Quality factors
    expected_moisture_content: float | None = None
    target_moisture_content: float | None = None
    drying_needed: bool = False
    drying_hours_needed: float = 0.0

    # Economic impact
    quality_premium_expected: float | None = None
    penalty_risk: float | None = None
    currency: str = "SAR"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "crop_type": self.crop_type.value,
            "window_start": self.window_start.isoformat() if self.window_start else None,
            "window_end": self.window_end.isoformat() if self.window_end else None,
            "optimal_date": self.optimal_date.isoformat() if self.optimal_date else None,
            "optimal_time": self.optimal_time.isoformat() if self.optimal_time else None,
            "overall_condition": self.overall_condition.value,
            "score": self.score,
            "expected_rain_probability": self.expected_rain_probability,
            "expected_humidity_avg": self.expected_humidity_avg,
            "expected_temperature_avg": self.expected_temperature_avg,
            "dry_hours_available": self.dry_hours_available,
            "rain_risk": self.rain_risk,
            "rain_risk_ar": self.rain_risk_ar,
            "moisture_risk": self.moisture_risk,
            "moisture_risk_ar": self.moisture_risk_ar,
            "quality_risk": self.quality_risk,
            "quality_risk_ar": self.quality_risk_ar,
            "recommendation": self.recommendation,
            "considerations": self.considerations,
            "alternatives": self.alternatives,
            "recommendation_ar": self.recommendation_ar,
            "considerations_ar": self.considerations_ar,
            "alternatives_ar": self.alternatives_ar,
            "expected_moisture_content": self.expected_moisture_content,
            "target_moisture_content": self.target_moisture_content,
            "drying_needed": self.drying_needed,
            "drying_hours_needed": self.drying_hours_needed,
            "quality_premium_expected": self.quality_premium_expected,
            "penalty_risk": self.penalty_risk,
            "currency": self.currency,
        }


@dataclass
class AlertThresholds:
    """
    Configurable alert thresholds
    عتبات التنبيهات القابلة للتكوين
    """

    # Frost thresholds (Celsius)
    frost_critical: float = -2.0  # Severe frost damage
    frost_warning: float = 0.0  # Frost possible
    frost_advisory: float = 3.0  # Near-frost conditions

    # Heat thresholds (Celsius)
    heat_critical: float = 45.0  # Extreme heat
    heat_warning: float = 40.0  # Very high heat
    heat_advisory: float = 35.0  # High heat

    # Wind thresholds (km/h)
    wind_critical: float = 80.0  # Damaging winds
    wind_warning: float = 50.0  # Strong winds
    wind_advisory: float = 30.0  # Moderate winds
    wind_spray_max: float = 15.0  # Max for spraying

    # Rain thresholds (mm)
    rain_critical: float = 50.0  # Heavy rain
    rain_warning: float = 25.0  # Significant rain
    rain_spray_threshold: float = 0.5  # Rain expected = no spray

    # Humidity thresholds (%)
    humidity_high_warning: float = 90.0  # Disease risk
    humidity_low_warning: float = 20.0  # Stress risk
    humidity_spray_min: float = 40.0  # Min for effective spray
    humidity_spray_max: float = 85.0  # Max to avoid slow drying

    # Spray temperature range (Celsius)
    spray_temp_min: float = 10.0
    spray_temp_max: float = 30.0
    spray_temp_optimal_min: float = 15.0
    spray_temp_optimal_max: float = 25.0

    # Harvest thresholds
    harvest_rain_probability_max: float = 30.0  # Max rain chance for harvest
    harvest_humidity_max: float = 70.0  # Max humidity for grain harvest
    harvest_dry_hours_min: float = 4.0  # Min dry hours needed

    # UV thresholds
    uv_extreme: int = 11
    uv_very_high: int = 8
    uv_high: int = 6

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "frost_critical": self.frost_critical,
            "frost_warning": self.frost_warning,
            "frost_advisory": self.frost_advisory,
            "heat_critical": self.heat_critical,
            "heat_warning": self.heat_warning,
            "heat_advisory": self.heat_advisory,
            "wind_critical": self.wind_critical,
            "wind_warning": self.wind_warning,
            "wind_advisory": self.wind_advisory,
            "wind_spray_max": self.wind_spray_max,
            "rain_critical": self.rain_critical,
            "rain_warning": self.rain_warning,
            "rain_spray_threshold": self.rain_spray_threshold,
            "humidity_high_warning": self.humidity_high_warning,
            "humidity_low_warning": self.humidity_low_warning,
            "humidity_spray_min": self.humidity_spray_min,
            "humidity_spray_max": self.humidity_spray_max,
            "spray_temp_min": self.spray_temp_min,
            "spray_temp_max": self.spray_temp_max,
            "spray_temp_optimal_min": self.spray_temp_optimal_min,
            "spray_temp_optimal_max": self.spray_temp_optimal_max,
            "harvest_rain_probability_max": self.harvest_rain_probability_max,
            "harvest_humidity_max": self.harvest_humidity_max,
            "harvest_dry_hours_min": self.harvest_dry_hours_min,
            "uv_extreme": self.uv_extreme,
            "uv_very_high": self.uv_very_high,
            "uv_high": self.uv_high,
        }


# Crop-specific threshold adjustments
CROP_FROST_THRESHOLDS: dict[CropType, dict[str, float]] = {
    CropType.WHEAT: {"critical": -5.0, "warning": -2.0, "advisory": 2.0},
    CropType.BARLEY: {"critical": -6.0, "warning": -3.0, "advisory": 1.0},
    CropType.DATE_PALM: {"critical": -4.0, "warning": 0.0, "advisory": 5.0},
    CropType.TOMATO: {"critical": 0.0, "warning": 2.0, "advisory": 5.0},
    CropType.CUCUMBER: {"critical": 2.0, "warning": 5.0, "advisory": 8.0},
    CropType.CITRUS: {"critical": -3.0, "warning": 0.0, "advisory": 4.0},
    CropType.GRAPE: {"critical": -2.0, "warning": 0.0, "advisory": 3.0},
    CropType.OLIVE: {"critical": -7.0, "warning": -3.0, "advisory": 0.0},
    CropType.ALFALFA: {"critical": -8.0, "warning": -4.0, "advisory": 0.0},
    CropType.GENERAL: {"critical": -2.0, "warning": 0.0, "advisory": 3.0},
}


CROP_HEAT_THRESHOLDS: dict[CropType, dict[str, float]] = {
    CropType.WHEAT: {"critical": 38.0, "warning": 35.0, "advisory": 32.0},
    CropType.BARLEY: {"critical": 40.0, "warning": 36.0, "advisory": 33.0},
    CropType.DATE_PALM: {"critical": 50.0, "warning": 46.0, "advisory": 42.0},
    CropType.TOMATO: {"critical": 38.0, "warning": 35.0, "advisory": 32.0},
    CropType.CUCUMBER: {"critical": 35.0, "warning": 32.0, "advisory": 30.0},
    CropType.CITRUS: {"critical": 42.0, "warning": 38.0, "advisory": 35.0},
    CropType.GRAPE: {"critical": 40.0, "warning": 37.0, "advisory": 34.0},
    CropType.OLIVE: {"critical": 45.0, "warning": 40.0, "advisory": 37.0},
    CropType.ALFALFA: {"critical": 40.0, "warning": 36.0, "advisory": 33.0},
    CropType.GENERAL: {"critical": 45.0, "warning": 40.0, "advisory": 35.0},
}
