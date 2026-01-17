"""
SAHOOL Agricultural Monitoring Types
أنواع الرصد الزراعي

Based on Remote Sensing + AI Agricultural Monitoring Products:
1. Crop Distribution and Area Monitoring
2. Economic Crop Distribution Monitoring
3. Crop Growth Monitoring
4. Crop Maturity Monitoring
5. Seedling Status Monitoring
6. Crop Yield Estimation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# Common Types
# ═══════════════════════════════════════════════════════════════════════════


class DataSource(str, Enum):
    """Satellite data source"""

    SENTINEL_2 = "sentinel-2"
    LANDSAT_8 = "landsat-8"
    MODIS = "modis"
    GEE = "gee"
    COPERNICUS = "copernicus"
    MOCK = "mock"


class Resolution(str, Enum):
    """Spatial resolution categories"""

    HIGH = "high"  # 1-3m
    MEDIUM = "medium"  # 10-16m
    LOW = "low"  # 30m


@dataclass
class GeoCoordinates:
    """Geographic coordinates"""

    latitude: float
    longitude: float


@dataclass
class BoundingBox:
    """Geographic bounding box"""

    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


@dataclass
class MonitoringMetadata:
    """Common metadata for monitoring results"""

    data_source: DataSource
    resolution: Resolution
    resolution_meters: float
    acquisition_date: str
    cloud_cover_percent: float
    confidence_score: float  # 0-100
    processing_date: str


# ═══════════════════════════════════════════════════════════════════════════
# 1. Crop Distribution and Area Monitoring
# توزيع المحاصيل ورصد المساحة
# ═══════════════════════════════════════════════════════════════════════════


class MainCropType(str, Enum):
    """Main staple crop types"""

    WHEAT = "wheat"  # القمح
    CORN = "corn"  # الذرة
    RICE = "rice"  # الأرز
    SOYBEAN = "soybean"  # فول الصويا
    COTTON = "cotton"  # القطن
    SORGHUM = "sorghum"  # الذرة الرفيعة
    BARLEY = "barley"  # الشعير
    MILLET = "millet"  # الدخن


@dataclass
class CropDistribution:
    """Crop distribution data for a region"""

    id: str
    region_id: str
    region_name: str
    region_name_ar: str
    crop_type: MainCropType
    crop_name_ar: str
    crop_name_en: str
    area_hectares: float
    percentage_of_total: float
    bounding_box: BoundingBox
    centroid: GeoCoordinates
    metadata: MonitoringMetadata
    season_year: int
    season_type: str  # winter, summer, perennial


@dataclass
class CropAreaMonitoringResult:
    """Result of crop area monitoring"""

    success: bool
    region_id: str
    total_area_hectares: float
    crops: list[CropDistribution]
    accuracy_percent: float  # 85-95%
    update_frequency: str  # monthly, seasonal
    last_updated: str
    next_update_expected: str


# ═══════════════════════════════════════════════════════════════════════════
# 2. Economic Crop Distribution Monitoring
# توزيع المحاصيل الاقتصادية المميزة
# ═══════════════════════════════════════════════════════════════════════════


class EconomicCropType(str, Enum):
    """Economic/cash crop types"""

    TEA = "tea"  # الشاي
    OIL_TEA = "oil_tea"  # الشاي الزيتي
    SUGARCANE = "sugarcane"  # قصب السكر
    TOBACCO = "tobacco"  # التبغ
    COFFEE = "coffee"  # البن
    DATES = "dates"  # التمور
    GRAPES = "grapes"  # العنب
    MANGO = "mango"  # المانجو
    CITRUS = "citrus"  # الحمضيات
    OLIVES = "olives"  # الزيتون
    QAT = "qat"  # القات


@dataclass
class EconomicCropDistribution:
    """Economic crop distribution data"""

    id: str
    region_id: str
    region_name: str
    region_name_ar: str
    crop_type: EconomicCropType
    crop_name_ar: str
    crop_name_en: str
    area_hectares: float
    estimated_value: float  # USD
    value_currency: str
    quality_grade: str  # A, B, C
    bounding_box: BoundingBox
    centroid: GeoCoordinates
    metadata: MonitoringMetadata
    harvest_season: str


# ═══════════════════════════════════════════════════════════════════════════
# 3. Crop Growth Monitoring
# مراقبة نمو المحاصيل
# ═══════════════════════════════════════════════════════════════════════════


class GrowthLevel(int, Enum):
    """Growth level (1-5)"""

    VERY_POOR = 1
    POOR = 2
    NORMAL = 3
    GOOD = 4
    EXCELLENT = 5


class GrowthStatus(str, Enum):
    """Growth status categories"""

    VERY_POOR = "very_poor"  # سيئ جداً
    POOR = "poor"  # سيئ
    NORMAL = "normal"  # طبيعي
    GOOD = "good"  # جيد
    EXCELLENT = "excellent"  # ممتاز


@dataclass
class GrowthIndicators:
    """Vegetation and growth indicators"""

    ndvi: float  # Normalized Difference Vegetation Index
    evi: float  # Enhanced Vegetation Index
    lai: float  # Leaf Area Index
    chlorophyll_content: float
    water_stress_index: float


class RiskType(str, Enum):
    """Risk alert types"""

    DISEASE = "disease"
    PEST = "pest"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    WATER_STRESS = "water_stress"
    HEAT_STRESS = "heat_stress"


class RiskSeverity(str, Enum):
    """Risk severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskAlert:
    """Risk alert for crop monitoring"""

    id: str
    type: RiskType
    severity: RiskSeverity
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    affected_area_percent: float
    detected_at: str
    recommended_action: str
    recommended_action_ar: str


@dataclass
class CropGrowthStatus:
    """Crop growth monitoring status"""

    id: str
    field_id: str
    field_name: str
    field_name_ar: str
    crop_type: str
    growth_level: GrowthLevel
    growth_status: GrowthStatus
    growth_status_ar: str
    indicators: GrowthIndicators
    comparison_to_historical: float  # percentage +/-
    risk_alerts: list[RiskAlert]
    recommendations: list[str]
    recommendations_ar: list[str]
    metadata: MonitoringMetadata
    observation_date: str


# ═══════════════════════════════════════════════════════════════════════════
# 4. Crop Maturity Monitoring
# رصد نضج المحاصيل
# ═══════════════════════════════════════════════════════════════════════════


class MaturityStage(str, Enum):
    """Maturity stage categories"""

    VEGETATIVE = "vegetative"  # نمو خضري
    FLOWERING = "flowering"  # إزهار
    FRUIT_SET = "fruit_set"  # عقد الثمار
    DEVELOPMENT = "development"  # تطور
    MATURATION = "maturation"  # نضج
    HARVEST_READY = "harvest_ready"  # جاهز للحصاد


@dataclass
class MaturityIndex:
    """Maturity index data"""

    value: float  # 0-100
    stage: MaturityStage
    stage_ar: str
    days_to_optimal_harvest: int
    optimal_harvest_start: str
    optimal_harvest_end: str


@dataclass
class QualityFactors:
    """Quality prediction factors"""

    moisture_content: float
    sugar_content: float | None = None
    protein_content: float | None = None
    oil_content: float | None = None


@dataclass
class WeatherRisk:
    """Weather-related harvest risks"""

    rain_probability: float
    frost_risk: bool
    heat_wave_risk: bool


@dataclass
class CropMaturityStatus:
    """Crop maturity monitoring status"""

    id: str
    field_id: str
    field_name: str
    field_name_ar: str
    crop_type: str
    maturity_index: MaturityIndex
    quality_prediction: str  # A, B, C
    quality_factors: QualityFactors
    harvest_recommendation: str
    harvest_recommendation_ar: str
    weather_risk: WeatherRisk
    metadata: MonitoringMetadata
    observation_date: str


# ═══════════════════════════════════════════════════════════════════════════
# 5. Seedling Status Monitoring
# رصد حالة النباتات (الشتلات)
# ═══════════════════════════════════════════════════════════════════════════


class SeedlingLevel(int, Enum):
    """Seedling health level (1-4)"""

    WEAK = 1  # شتلات ضعيفة - تدخل فوري مطلوب
    MODERATE = 2  # شتلات متوسطة - مراقبة مستمرة
    GOOD = 3  # شتلات جيدة - صيانة عادية
    EXCELLENT = 4  # شتلات ممتازة - نمو مزدهر


class SeedlingStatus(str, Enum):
    """Seedling status categories"""

    WEAK = "weak"
    MODERATE = "moderate"
    GOOD = "good"
    EXCELLENT = "excellent"


class SoilMoistureStatus(str, Enum):
    """Soil moisture status"""

    CRITICAL = "critical"
    LOW = "low"
    OPTIMAL = "optimal"
    HIGH = "high"


class InterventionType(str, Enum):
    """Intervention types for seedlings"""

    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    PEST_CONTROL = "pest_control"
    REPLANTING = "replanting"


@dataclass
class EarlyRisk:
    """Early disease/pest risk detection"""

    detected: bool
    type: str | None = None
    severity: RiskSeverity | None = None
    affected_area_percent: float | None = None


@dataclass
class SeedlingCondition:
    """Seedling condition monitoring data"""

    id: str
    field_id: str
    field_name: str
    field_name_ar: str
    crop_type: str
    seedling_level: SeedlingLevel
    seedling_status: SeedlingStatus
    seedling_status_ar: str
    emergence_rate: float  # percentage of expected seedlings
    uniformity_score: float  # 0-100
    density_per_sqm: float
    soil_moisture_status: SoilMoistureStatus
    soil_moisture_status_ar: str
    early_disease_risk: EarlyRisk
    early_pest_risk: EarlyRisk
    intervention_required: bool
    intervention_type: InterventionType | None
    recommendations: list[str]
    recommendations_ar: list[str]
    metadata: MonitoringMetadata
    observation_date: str


# ═══════════════════════════════════════════════════════════════════════════
# 6. Crop Yield Estimation
# تقديرات إنتاج المحاصيل
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class YieldInputs:
    """Inputs for yield estimation model"""

    satellite_ndvi: list[float]
    weather_temp_min: list[float]
    weather_temp_max: list[float]
    precipitation_mm: float
    et0_mm: float | None
    soil_type: str
    soil_ph: float
    soil_organic_matter: float
    soil_nitrogen: float
    soil_phosphorus: float
    soil_potassium: float
    planted_area_ha: float
    crop_type: str
    planting_date: str
    irrigation_type: str  # rainfed, drip, sprinkler, flood


@dataclass
class YieldFactors:
    """Yield factor contributions (0-1 scale)"""

    vegetation_health: float
    biomass_accumulation: float
    thermal_time: float
    water_availability: float
    soil_quality: float


@dataclass
class ConfidenceInterval:
    """Confidence interval for yield estimate"""

    min: float
    max: float


@dataclass
class YieldEstimate:
    """Crop yield estimation result"""

    id: str
    field_id: str
    field_name: str
    field_name_ar: str
    crop_type: str
    crop_name_ar: str
    estimated_yield_tons: float
    confidence_interval: ConfidenceInterval
    yield_per_hectare: float
    comparison_to_average: float  # percentage +/-
    comparison_to_last_year: float | None
    yield_factors: YieldFactors
    risk_factors: list[str]
    risk_factors_ar: list[str]
    recommendations: list[str]
    recommendations_ar: list[str]
    metadata: MonitoringMetadata
    estimation_date: str
    expected_harvest_date: str


# ═══════════════════════════════════════════════════════════════════════════
# Integrated Monitoring Dashboard Types
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class FieldMonitoringSummary:
    """Summary of field monitoring status"""

    field_id: str
    field_name: str
    field_name_ar: str
    crop_type: str
    area_hectares: float
    current_growth_status: GrowthStatus
    current_growth_level: GrowthLevel
    maturity_percent: float
    seedling_status: SeedlingStatus | None
    estimated_yield_tons: float | None
    active_alerts: list[RiskAlert]
    last_updated: str
    overall_health_score: float  # 0-100


@dataclass
class CropBreakdown:
    """Crop breakdown for regional summary"""

    crop_type: str
    crop_name_ar: str
    area_hectares: float
    field_count: int
    average_growth_level: float


@dataclass
class AlertsSummary:
    """Summary of alerts by severity"""

    critical: int
    high: int
    medium: int
    low: int


@dataclass
class RegionMonitoringSummary:
    """Summary of region-wide monitoring"""

    region_id: str
    region_name: str
    region_name_ar: str
    total_fields: int
    total_area_hectares: float
    crop_breakdown: list[CropBreakdown]
    alerts_summary: AlertsSummary
    estimated_total_yield_tons: float
    last_updated: str


# ═══════════════════════════════════════════════════════════════════════════
# Vegetation Indices Types
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class VegetationIndices:
    """Standard vegetation indices"""

    ndvi: float  # Normalized Difference Vegetation Index
    evi: float  # Enhanced Vegetation Index
    savi: float  # Soil Adjusted Vegetation Index
    lai: float  # Leaf Area Index
    ndwi: float | None = None  # Normalized Difference Water Index
    ndmi: float | None = None  # Normalized Difference Moisture Index


@dataclass
class SpectralBands:
    """Satellite spectral band values"""

    red: float
    nir: float
    blue: float | None = None
    green: float | None = None
    swir1: float | None = None
    swir2: float | None = None


@dataclass
class SatelliteObservation:
    """Individual satellite observation"""

    id: str
    field_id: str
    observation_date: str
    data_source: DataSource
    cloud_cover_percent: float
    bands: SpectralBands
    indices: VegetationIndices
    quality_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_growth_status_ar(status: GrowthStatus) -> str:
    """Get Arabic translation of growth status"""
    translations = {
        GrowthStatus.VERY_POOR: "سيئ جداً",
        GrowthStatus.POOR: "سيئ",
        GrowthStatus.NORMAL: "طبيعي",
        GrowthStatus.GOOD: "جيد",
        GrowthStatus.EXCELLENT: "ممتاز",
    }
    return translations.get(status, status.value)


def get_seedling_status_ar(status: SeedlingStatus) -> str:
    """Get Arabic translation of seedling status"""
    translations = {
        SeedlingStatus.WEAK: "شتلات ضعيفة",
        SeedlingStatus.MODERATE: "شتلات متوسطة",
        SeedlingStatus.GOOD: "شتلات جيدة",
        SeedlingStatus.EXCELLENT: "شتلات ممتازة",
    }
    return translations.get(status, status.value)


def get_maturity_stage_ar(stage: MaturityStage) -> str:
    """Get Arabic translation of maturity stage"""
    translations = {
        MaturityStage.VEGETATIVE: "نمو خضري",
        MaturityStage.FLOWERING: "إزهار",
        MaturityStage.FRUIT_SET: "عقد الثمار",
        MaturityStage.DEVELOPMENT: "تطور",
        MaturityStage.MATURATION: "نضج",
        MaturityStage.HARVEST_READY: "جاهز للحصاد",
    }
    return translations.get(stage, stage.value)


def get_soil_moisture_status_ar(status: SoilMoistureStatus) -> str:
    """Get Arabic translation of soil moisture status"""
    translations = {
        SoilMoistureStatus.CRITICAL: "حرج",
        SoilMoistureStatus.LOW: "منخفض",
        SoilMoistureStatus.OPTIMAL: "مثالي",
        SoilMoistureStatus.HIGH: "مرتفع",
    }
    return translations.get(status, status.value)


def growth_level_to_status(level: GrowthLevel) -> GrowthStatus:
    """Convert growth level to status"""
    mapping = {
        GrowthLevel.VERY_POOR: GrowthStatus.VERY_POOR,
        GrowthLevel.POOR: GrowthStatus.POOR,
        GrowthLevel.NORMAL: GrowthStatus.NORMAL,
        GrowthLevel.GOOD: GrowthStatus.GOOD,
        GrowthLevel.EXCELLENT: GrowthStatus.EXCELLENT,
    }
    return mapping.get(level, GrowthStatus.NORMAL)


def ndvi_to_growth_level(ndvi: float) -> GrowthLevel:
    """Convert NDVI value to growth level"""
    if ndvi < 0.2:
        return GrowthLevel.VERY_POOR
    elif ndvi < 0.35:
        return GrowthLevel.POOR
    elif ndvi < 0.5:
        return GrowthLevel.NORMAL
    elif ndvi < 0.65:
        return GrowthLevel.GOOD
    else:
        return GrowthLevel.EXCELLENT
