"""
ML Irrigation Prediction Models
================================
نماذج التنبؤ بالري باستخدام التعلم الآلي

Data models for ML-based irrigation prediction including:
- Input features (weather, soil, crop data)
- Prediction outputs (irrigation needs, timing)
- Anomaly detection results
- Historical pattern analysis

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class IrrigationUrgency(StrEnum):
    """Urgency level for irrigation | مستوى إلحاح الري"""

    CRITICAL = "critical"  # حرج - irrigate immediately
    HIGH = "high"  # عالي - irrigate within 6 hours
    MEDIUM = "medium"  # متوسط - irrigate within 24 hours
    LOW = "low"  # منخفض - can wait 48+ hours
    NONE = "none"  # لا حاجة - no irrigation needed


class CropStage(StrEnum):
    """Crop growth stages | مراحل نمو المحصول"""

    GERMINATION = "germination"  # الإنبات
    SEEDLING = "seedling"  # الشتلة
    VEGETATIVE = "vegetative"  # النمو الخضري
    TILLERING = "tillering"  # التفريع
    FLOWERING = "flowering"  # الإزهار
    GRAIN_FILL = "grain_fill"  # امتلاء الحبوب
    MATURITY = "maturity"  # النضج
    HARVEST = "harvest"  # الحصاد


class SoilType(StrEnum):
    """Soil types | أنواع التربة"""

    SANDY = "sandy"  # رملية
    LOAMY = "loamy"  # طفلية
    CLAY = "clay"  # طينية
    SANDY_LOAM = "sandy_loam"  # رملية طفلية
    CLAY_LOAM = "clay_loam"  # طينية طفلية
    SILT = "silt"  # طمية


class IrrigationType(StrEnum):
    """Irrigation system types | أنواع أنظمة الري"""

    DRIP = "drip"  # تنقيط
    SPRINKLER = "sprinkler"  # رش
    FLOOD = "flood"  # غمر
    CENTER_PIVOT = "center_pivot"  # محوري مركزي
    FURROW = "furrow"  # أخدود
    SUBSURFACE = "subsurface"  # تحت سطحي


class AnomalyType(StrEnum):
    """Types of irrigation system anomalies | أنواع شذوذ نظام الري"""

    LEAK = "leak"  # تسرب
    BLOCKAGE = "blockage"  # انسداد
    PRESSURE_DROP = "pressure_drop"  # انخفاض الضغط
    OVERCONSUMPTION = "overconsumption"  # استهلاك مفرط
    UNDERCONSUMPTION = "underconsumption"  # استهلاك ناقص
    SENSOR_MALFUNCTION = "sensor_malfunction"  # خلل في الحساس
    SCHEDULING_ERROR = "scheduling_error"  # خطأ في الجدولة
    PUMP_FAILURE = "pump_failure"  # عطل المضخة


class AnomalySeverity(StrEnum):
    """Severity of detected anomalies | شدة الشذوذ المكتشف"""

    CRITICAL = "critical"  # حرج
    HIGH = "high"  # عالي
    MEDIUM = "medium"  # متوسط
    LOW = "low"  # منخفض


class PredictionConfidence(StrEnum):
    """Confidence level of predictions | مستوى ثقة التنبؤات"""

    VERY_HIGH = "very_high"  # عالي جداً (>90%)
    HIGH = "high"  # عالي (75-90%)
    MEDIUM = "medium"  # متوسط (60-75%)
    LOW = "low"  # منخفض (40-60%)
    VERY_LOW = "very_low"  # منخفض جداً (<40%)


@dataclass
class WeatherFeatures:
    """
    Weather input features for irrigation prediction
    ميزات الطقس المدخلة للتنبؤ بالري
    """

    # Temperature
    temperature_current: float  # Current temperature (Celsius)
    temperature_max: float  # Forecasted max temperature
    temperature_min: float  # Forecasted min temperature

    # Humidity and precipitation
    humidity: float  # Relative humidity (%)
    precipitation_probability: float  # Rain probability (0-100%)
    precipitation_amount_mm: float  # Expected precipitation (mm)

    # Wind
    wind_speed: float  # Wind speed (km/h)
    wind_direction: float  # Wind direction (degrees)

    # Solar radiation
    solar_radiation: float  # Solar radiation (W/m2)
    cloud_cover: float  # Cloud cover (%)

    # Evapotranspiration
    et0: float  # Reference evapotranspiration (mm/day)

    # Forecast horizon
    forecast_hours: int = 24  # Hours ahead of forecast

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "temperature_current": self.temperature_current,
            "temperature_max": self.temperature_max,
            "temperature_min": self.temperature_min,
            "humidity": self.humidity,
            "precipitation_probability": self.precipitation_probability,
            "precipitation_amount_mm": self.precipitation_amount_mm,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "solar_radiation": self.solar_radiation,
            "cloud_cover": self.cloud_cover,
            "et0": self.et0,
            "forecast_hours": self.forecast_hours,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WeatherFeatures:
        """Create from dictionary"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now(UTC)

        return cls(
            temperature_current=data["temperature_current"],
            temperature_max=data["temperature_max"],
            temperature_min=data["temperature_min"],
            humidity=data["humidity"],
            precipitation_probability=data.get("precipitation_probability", 0.0),
            precipitation_amount_mm=data.get("precipitation_amount_mm", 0.0),
            wind_speed=data.get("wind_speed", 0.0),
            wind_direction=data.get("wind_direction", 0.0),
            solar_radiation=data.get("solar_radiation", 0.0),
            cloud_cover=data.get("cloud_cover", 0.0),
            et0=data.get("et0", 0.0),
            forecast_hours=data.get("forecast_hours", 24),
            timestamp=timestamp,
        )

    def to_feature_vector(self) -> list[float]:
        """Convert to numerical feature vector for ML models"""
        return [
            self.temperature_current,
            self.temperature_max,
            self.temperature_min,
            self.humidity,
            self.precipitation_probability,
            self.precipitation_amount_mm,
            self.wind_speed,
            self.solar_radiation,
            self.cloud_cover,
            self.et0,
        ]


@dataclass
class SoilFeatures:
    """
    Soil input features for irrigation prediction
    ميزات التربة المدخلة للتنبؤ بالري
    """

    # Moisture levels
    moisture_current: float  # Current soil moisture (%)
    moisture_field_capacity: float  # Field capacity (%)
    moisture_wilting_point: float  # Permanent wilting point (%)
    moisture_depth_cm: float  # Measurement depth (cm)

    # Soil properties
    soil_type: SoilType
    infiltration_rate: float  # Infiltration rate (mm/hour)
    water_holding_capacity: float  # Water holding capacity (mm/m)

    # Salinity
    ec: float  # Electrical conductivity (dS/m)
    ph: float  # Soil pH

    # Temperature
    soil_temperature: float  # Soil temperature (Celsius)

    # Additional sensors
    sensor_id: str | None = None
    sensor_depth_cm: float = 30.0

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def available_water(self) -> float:
        """Calculate available water content (%)"""
        return max(0, self.moisture_current - self.moisture_wilting_point)

    @property
    def moisture_deficit(self) -> float:
        """Calculate moisture deficit from field capacity (%)"""
        return max(0, self.moisture_field_capacity - self.moisture_current)

    @property
    def depletion_fraction(self) -> float:
        """Calculate soil moisture depletion fraction (0-1)"""
        total_available = self.moisture_field_capacity - self.moisture_wilting_point
        if total_available <= 0:
            return 0.0
        return self.moisture_deficit / total_available

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "moisture_current": self.moisture_current,
            "moisture_field_capacity": self.moisture_field_capacity,
            "moisture_wilting_point": self.moisture_wilting_point,
            "moisture_depth_cm": self.moisture_depth_cm,
            "soil_type": self.soil_type.value,
            "infiltration_rate": self.infiltration_rate,
            "water_holding_capacity": self.water_holding_capacity,
            "ec": self.ec,
            "ph": self.ph,
            "soil_temperature": self.soil_temperature,
            "sensor_id": self.sensor_id,
            "sensor_depth_cm": self.sensor_depth_cm,
            "available_water": self.available_water,
            "moisture_deficit": self.moisture_deficit,
            "depletion_fraction": self.depletion_fraction,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SoilFeatures:
        """Create from dictionary"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now(UTC)

        return cls(
            moisture_current=data["moisture_current"],
            moisture_field_capacity=data.get("moisture_field_capacity", 35.0),
            moisture_wilting_point=data.get("moisture_wilting_point", 15.0),
            moisture_depth_cm=data.get("moisture_depth_cm", 30.0),
            soil_type=SoilType(data.get("soil_type", "loamy")),
            infiltration_rate=data.get("infiltration_rate", 15.0),
            water_holding_capacity=data.get("water_holding_capacity", 150.0),
            ec=data.get("ec", 1.0),
            ph=data.get("ph", 7.0),
            soil_temperature=data.get("soil_temperature", 20.0),
            sensor_id=data.get("sensor_id"),
            sensor_depth_cm=data.get("sensor_depth_cm", 30.0),
            timestamp=timestamp,
        )

    def to_feature_vector(self) -> list[float]:
        """Convert to numerical feature vector for ML models"""
        soil_type_encoding = list(SoilType).index(self.soil_type) / len(SoilType)
        return [
            self.moisture_current,
            self.moisture_field_capacity,
            self.moisture_wilting_point,
            self.depletion_fraction,
            soil_type_encoding,
            self.infiltration_rate,
            self.water_holding_capacity,
            self.ec,
            self.ph,
            self.soil_temperature,
        ]


@dataclass
class CropFeatures:
    """
    Crop input features for irrigation prediction
    ميزات المحصول المدخلة للتنبؤ بالري
    """

    # Crop identification (required)
    crop_type: str  # Crop type (wheat, barley, tomato, etc.)
    crop_type_ar: str  # Arabic name

    # Growth stage (required)
    growth_stage: CropStage
    days_after_planting: int
    growth_stage_days: int  # Days in current stage

    # Crop coefficients (required)
    kc: float  # Crop coefficient
    root_depth_cm: float  # Root zone depth

    # Optional fields (with defaults)
    variety: str | None = None  # Crop variety

    # Crop health indicators
    ndvi: float | None = None  # Normalized difference vegetation index
    lai: float | None = None  # Leaf area index
    canopy_cover: float | None = None  # Canopy cover (%)

    # Water stress
    stress_index: float = 0.0  # Water stress index (0-1)

    # Yield target
    target_yield_tons_ha: float | None = None

    # Field info
    field_id: str | None = None
    area_ha: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "variety": self.variety,
            "growth_stage": self.growth_stage.value,
            "days_after_planting": self.days_after_planting,
            "growth_stage_days": self.growth_stage_days,
            "kc": self.kc,
            "root_depth_cm": self.root_depth_cm,
            "ndvi": self.ndvi,
            "lai": self.lai,
            "canopy_cover": self.canopy_cover,
            "stress_index": self.stress_index,
            "target_yield_tons_ha": self.target_yield_tons_ha,
            "field_id": self.field_id,
            "area_ha": self.area_ha,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CropFeatures:
        """Create from dictionary"""
        return cls(
            crop_type=data["crop_type"],
            crop_type_ar=data.get("crop_type_ar", data["crop_type"]),
            growth_stage=CropStage(data.get("growth_stage", "vegetative")),
            days_after_planting=data.get("days_after_planting", 0),
            growth_stage_days=data.get("growth_stage_days", 0),
            kc=data.get("kc", 1.0),
            root_depth_cm=data.get("root_depth_cm", 60.0),
            variety=data.get("variety"),
            ndvi=data.get("ndvi"),
            lai=data.get("lai"),
            canopy_cover=data.get("canopy_cover"),
            stress_index=data.get("stress_index", 0.0),
            target_yield_tons_ha=data.get("target_yield_tons_ha"),
            field_id=data.get("field_id"),
            area_ha=data.get("area_ha"),
        )

    def to_feature_vector(self) -> list[float]:
        """Convert to numerical feature vector for ML models"""
        stage_encoding = list(CropStage).index(self.growth_stage) / len(CropStage)
        return [
            stage_encoding,
            self.days_after_planting / 200.0,  # Normalize by typical max
            self.kc,
            self.root_depth_cm / 150.0,  # Normalize
            self.ndvi if self.ndvi else 0.5,
            self.lai if self.lai else 3.0,
            self.canopy_cover / 100.0 if self.canopy_cover else 0.5,
            self.stress_index,
        ]


@dataclass
class IrrigationFeatures:
    """
    Combined features for irrigation prediction
    الميزات المجمعة للتنبؤ بالري
    """

    # Component features
    weather: WeatherFeatures
    soil: SoilFeatures
    crop: CropFeatures

    # Irrigation system
    irrigation_type: IrrigationType
    system_efficiency: float  # Irrigation system efficiency (0-1)

    # Historical context
    last_irrigation_date: datetime | None = None
    last_irrigation_amount_mm: float | None = None

    # Request metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    field_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def days_since_irrigation(self) -> float | None:
        """Calculate days since last irrigation"""
        if self.last_irrigation_date:
            delta = self.timestamp - self.last_irrigation_date
            return delta.total_seconds() / 86400.0
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "weather": self.weather.to_dict(),
            "soil": self.soil.to_dict(),
            "crop": self.crop.to_dict(),
            "irrigation_type": self.irrigation_type.value,
            "system_efficiency": self.system_efficiency,
            "last_irrigation_date": self.last_irrigation_date.isoformat() if self.last_irrigation_date else None,
            "last_irrigation_amount_mm": self.last_irrigation_amount_mm,
            "days_since_irrigation": self.days_since_irrigation,
            "request_id": self.request_id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_feature_vector(self) -> list[float]:
        """Convert to numerical feature vector for ML models"""
        irrigation_type_encoding = list(IrrigationType).index(self.irrigation_type) / len(IrrigationType)
        days_since = self.days_since_irrigation if self.days_since_irrigation else 7.0

        return (
            self.weather.to_feature_vector()
            + self.soil.to_feature_vector()
            + self.crop.to_feature_vector()
            + [
                irrigation_type_encoding,
                self.system_efficiency,
                min(days_since / 14.0, 1.0),  # Normalize by 2 weeks
            ]
        )


@dataclass
class IrrigationPrediction:
    """
    Irrigation need prediction result
    نتيجة التنبؤ باحتياج الري
    """

    # Core prediction (required)
    irrigation_needed: bool
    recommended_amount_mm: float
    urgency: IrrigationUrgency
    confidence: float  # 0-1

    # Optional fields with defaults
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    recommended_amount_liters: float | None = None  # If area known

    # Timing
    optimal_time: datetime | None = None
    optimal_time_window_hours: int = 6

    # Confidence level
    confidence_level: PredictionConfidence = PredictionConfidence.MEDIUM

    # Bilingual recommendation
    recommendation: str = ""
    recommendation_ar: str = ""

    # Reasoning
    reasoning: str = ""
    reasoning_ar: str = ""

    # Contributing factors
    factors: list[dict[str, Any]] = field(default_factory=list)

    # Model info
    model_name: str = ""
    model_version: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "prediction_id": self.prediction_id,
            "request_id": self.request_id,
            "irrigation_needed": self.irrigation_needed,
            "recommended_amount_mm": self.recommended_amount_mm,
            "recommended_amount_liters": self.recommended_amount_liters,
            "urgency": self.urgency.value,
            "optimal_time": self.optimal_time.isoformat() if self.optimal_time else None,
            "optimal_time_window_hours": self.optimal_time_window_hours,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "recommendation": self.recommendation,
            "recommendation_ar": self.recommendation_ar,
            "reasoning": self.reasoning,
            "reasoning_ar": self.reasoning_ar,
            "factors": self.factors,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class WaterOptimizationResult:
    """
    Water usage optimization result
    نتيجة تحسين استخدام المياه
    """

    # Current vs optimized (required)
    current_usage_mm: float
    optimized_usage_mm: float
    savings_mm: float
    savings_percent: float

    # Optional fields with defaults
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str = ""

    # Volume calculations
    current_volume_m3: float | None = None
    optimized_volume_m3: float | None = None
    savings_volume_m3: float | None = None

    # Cost analysis
    water_cost_per_m3: float | None = None
    current_cost: float | None = None
    optimized_cost: float | None = None
    cost_savings: float | None = None

    # Schedule optimization
    optimized_schedule: list[dict[str, Any]] = field(default_factory=list)

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Confidence
    confidence: float = 0.8

    # Metadata
    analysis_period_days: int = 7
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "optimization_id": self.optimization_id,
            "field_id": self.field_id,
            "current_usage_mm": self.current_usage_mm,
            "optimized_usage_mm": self.optimized_usage_mm,
            "savings_mm": self.savings_mm,
            "savings_percent": self.savings_percent,
            "current_volume_m3": self.current_volume_m3,
            "optimized_volume_m3": self.optimized_volume_m3,
            "savings_volume_m3": self.savings_volume_m3,
            "water_cost_per_m3": self.water_cost_per_m3,
            "current_cost": self.current_cost,
            "optimized_cost": self.optimized_cost,
            "cost_savings": self.cost_savings,
            "optimized_schedule": self.optimized_schedule,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
            "confidence": self.confidence,
            "analysis_period_days": self.analysis_period_days,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class IrrigationAnomaly:
    """
    Detected irrigation system anomaly
    شذوذ مكتشف في نظام الري
    """

    # Anomaly details (required)
    anomaly_type: AnomalyType
    severity: AnomalySeverity

    # Detection info (required)
    detected_value: float
    expected_value: float
    deviation_percent: float

    # Description (required)
    description: str
    description_ar: str

    # Optional fields with defaults
    anomaly_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str = ""

    # Impact assessment
    impact_description: str = ""
    impact_description_ar: str = ""
    estimated_water_loss_m3: float | None = None
    estimated_cost_impact: float | None = None

    # Recommendations
    recommended_action: str = ""
    recommended_action_ar: str = ""

    # Detection metadata
    confidence: float = 0.8
    detection_method: str = ""

    # Timestamps
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    first_occurrence: datetime | None = None

    # Status
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "anomaly_id": self.anomaly_id,
            "field_id": self.field_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "detected_value": self.detected_value,
            "expected_value": self.expected_value,
            "deviation_percent": self.deviation_percent,
            "description": self.description,
            "description_ar": self.description_ar,
            "impact_description": self.impact_description,
            "impact_description_ar": self.impact_description_ar,
            "estimated_water_loss_m3": self.estimated_water_loss_m3,
            "estimated_cost_impact": self.estimated_cost_impact,
            "recommended_action": self.recommended_action,
            "recommended_action_ar": self.recommended_action_ar,
            "confidence": self.confidence,
            "detection_method": self.detection_method,
            "detected_at": self.detected_at.isoformat(),
            "first_occurrence": self.first_occurrence.isoformat() if self.first_occurrence else None,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class HistoricalPattern:
    """
    Historical irrigation pattern analysis
    تحليل أنماط الري التاريخية
    """

    # Time period (required)
    start_date: datetime
    end_date: datetime
    total_days: int

    # Irrigation statistics (required)
    total_irrigations: int
    total_water_mm: float
    average_amount_mm: float
    average_interval_days: float

    # Efficiency metrics (required)
    calculated_efficiency: float  # Actual vs theoretical need

    # Optional fields with defaults
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str = ""

    # Optional volume
    total_water_m3: float | None = None

    # Water productivity
    water_productivity: float | None = None  # Yield per unit water

    # Temporal patterns
    most_common_day: str | None = None  # Day of week
    most_common_hour: int | None = None  # Hour of day

    # Comparison to optimal
    deviation_from_optimal_percent: float = 0.0

    # Identified patterns
    patterns_identified: list[str] = field(default_factory=list)
    patterns_identified_ar: list[str] = field(default_factory=list)

    # Insights
    insights: list[str] = field(default_factory=list)
    insights_ar: list[str] = field(default_factory=list)

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "field_id": self.field_id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_days": self.total_days,
            "total_irrigations": self.total_irrigations,
            "total_water_mm": self.total_water_mm,
            "total_water_m3": self.total_water_m3,
            "average_amount_mm": self.average_amount_mm,
            "average_interval_days": self.average_interval_days,
            "calculated_efficiency": self.calculated_efficiency,
            "water_productivity": self.water_productivity,
            "most_common_day": self.most_common_day,
            "most_common_hour": self.most_common_hour,
            "deviation_from_optimal_percent": self.deviation_from_optimal_percent,
            "patterns_identified": self.patterns_identified,
            "patterns_identified_ar": self.patterns_identified_ar,
            "insights": self.insights,
            "insights_ar": self.insights_ar,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class IrrigationRecord:
    """
    Historical irrigation event record
    سجل حدث ري تاريخي
    """

    # Event details (required)
    irrigation_date: datetime
    amount_mm: float
    irrigation_type: IrrigationType

    # Optional fields with defaults
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str = ""
    amount_m3: float | None = None
    duration_minutes: int | None = None

    # Conditions at time of irrigation
    soil_moisture_before: float | None = None
    soil_moisture_after: float | None = None
    weather_temp: float | None = None
    weather_humidity: float | None = None

    # Effectiveness
    was_scheduled: bool = True
    followed_recommendation: bool | None = None
    effectiveness_rating: float | None = None  # 1-5

    # Notes
    notes: str | None = None
    notes_ar: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "record_id": self.record_id,
            "field_id": self.field_id,
            "irrigation_date": self.irrigation_date.isoformat(),
            "amount_mm": self.amount_mm,
            "amount_m3": self.amount_m3,
            "duration_minutes": self.duration_minutes,
            "irrigation_type": self.irrigation_type.value,
            "soil_moisture_before": self.soil_moisture_before,
            "soil_moisture_after": self.soil_moisture_after,
            "weather_temp": self.weather_temp,
            "weather_humidity": self.weather_humidity,
            "was_scheduled": self.was_scheduled,
            "followed_recommendation": self.followed_recommendation,
            "effectiveness_rating": self.effectiveness_rating,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IrrigationRecord:
        """Create from dictionary"""
        irrigation_date = data.get("irrigation_date")
        if isinstance(irrigation_date, str):
            irrigation_date = datetime.fromisoformat(irrigation_date)

        return cls(
            irrigation_date=irrigation_date,
            amount_mm=data["amount_mm"],
            irrigation_type=IrrigationType(data.get("irrigation_type", "drip")),
            record_id=data.get("record_id", str(uuid.uuid4())),
            field_id=data.get("field_id", ""),
            amount_m3=data.get("amount_m3"),
            duration_minutes=data.get("duration_minutes"),
            soil_moisture_before=data.get("soil_moisture_before"),
            soil_moisture_after=data.get("soil_moisture_after"),
            weather_temp=data.get("weather_temp"),
            weather_humidity=data.get("weather_humidity"),
            was_scheduled=data.get("was_scheduled", True),
            followed_recommendation=data.get("followed_recommendation"),
            effectiveness_rating=data.get("effectiveness_rating"),
            notes=data.get("notes"),
            notes_ar=data.get("notes_ar"),
        )
