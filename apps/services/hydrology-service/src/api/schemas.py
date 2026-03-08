"""
Pydantic Schemas for Hydrology Service
نماذج البيانات لخدمة الهيدرولوجيا

Defines request/response models for hydrology analysis endpoints.

Includes comprehensive validation for:
- Geographic coordinates and polygons
- Resolution and threshold values
- Field ID format
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# Validation constants
# ثوابت التحقق من الصحة
COORDINATE_PRECISION = 8  # Max decimal places for coordinates
MIN_RESOLUTION_M = 1.0  # Minimum resolution in meters
MAX_RESOLUTION_M = 1000.0  # Maximum resolution in meters
MIN_FLOW_THRESHOLD = 1
MAX_FLOW_THRESHOLD = 100000
MAX_RAINFALL_MM = 2000.0  # Maximum rainfall in mm


# ==============================================================================
# Enums
# ==============================================================================


class DrainageType(StrEnum):
    """Types of drainage patterns."""

    DENDRITIC = "dendritic"  # شجيري
    PARALLEL = "parallel"  # متوازي
    TRELLIS = "trellis"  # شبكي
    RECTANGULAR = "rectangular"  # مستطيل
    RADIAL = "radial"  # شعاعي
    CENTRIPETAL = "centripetal"  # مركزي
    DERANGED = "deranged"  # مشوش
    UNKNOWN = "unknown"  # غير معروف


class WetnessLevel(StrEnum):
    """Wetness classification levels."""

    VERY_DRY = "very_dry"  # جاف جداً
    DRY = "dry"  # جاف
    MODERATE = "moderate"  # معتدل
    WET = "wet"  # رطب
    VERY_WET = "very_wet"  # رطب جداً
    WATERLOGGED = "waterlogged"  # مشبع بالماء


class DepressionRisk(StrEnum):
    """Risk level for depressions."""

    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # مرتفع
    CRITICAL = "critical"  # حرج


class StreamOrder(int, Enum):
    """Strahler stream order classification."""

    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    HIGHER = 6


# ==============================================================================
# Base Models
# ==============================================================================


class GeoPoint(BaseModel):
    """Geographic point with coordinates."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude | خط العرض")
    lon: float = Field(..., ge=-180, le=180, description="Longitude | خط الطول")


class BoundingBox(BaseModel):
    """Bounding box for geographic area."""

    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)


class GeoPolygon(BaseModel):
    """Geographic polygon with coordinates."""

    coordinates: list[list[float]] = Field(..., min_length=3, description="List of [lon, lat] coordinate pairs")
    type: str = Field(default="Polygon")

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: list[list[float]]) -> list[list[float]]:
        """Validate polygon coordinates."""
        if len(v) < 3:
            raise ValueError(
                "Polygon must have at least 3 coordinate pairs | يجب أن يحتوي المضلع على 3 أزواج إحداثيات على الأقل"
            )

        for i, coord in enumerate(v):
            if not isinstance(coord, (list, tuple)) or len(coord) < 2:
                raise ValueError(
                    f"Coordinate at index {i} must be [lon, lat] array | "
                    f"الإحداثية في الفهرس {i} يجب أن تكون مصفوفة [خط الطول، خط العرض]"
                )

            try:
                lon, lat = float(coord[0]), float(coord[1])
            except (TypeError, ValueError) as e:
                raise ValueError(
                    f"Coordinate at index {i} contains non-numeric values | "
                    f"الإحداثية في الفهرس {i} تحتوي على قيم غير رقمية"
                ) from e

            # Validate coordinate ranges
            if not -180 <= lon <= 180:
                raise ValueError(
                    f"Longitude {lon} at index {i} must be between -180 and 180 | "
                    f"خط الطول {lon} في الفهرس {i} يجب أن يكون بين -180 و 180"
                )
            if not -90 <= lat <= 90:
                raise ValueError(
                    f"Latitude {lat} at index {i} must be between -90 and 90 | "
                    f"خط العرض {lat} في الفهرس {i} يجب أن يكون بين -90 و 90"
                )

        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate geometry type."""
        if v != "Polygon":
            raise ValueError(
                f"Geometry type must be 'Polygon', got '{v}' | نوع الهندسة يجب أن يكون 'Polygon'، تم الحصول على '{v}'"
            )
        return v


# ==============================================================================
# Request Models
# ==============================================================================


class HydrologyAnalysisRequest(BaseModel):
    """Request for full hydrology analysis.
    طلب تحليل هيدرولوجي كامل
    """

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    tenant_id: str = Field(..., min_length=1, max_length=64, description="Tenant identifier | معرف المستأجر")
    boundary: GeoPolygon | None = Field(None, description="Field boundary polygon | حدود الحقل")
    dem_source: str | None = Field(
        None,
        max_length=32,
        description="DEM data source (srtm, aster, local) | مصدر بيانات الارتفاع",
    )
    resolution_m: float = Field(
        default=30.0,
        ge=MIN_RESOLUTION_M,
        le=MAX_RESOLUTION_M,
        description="Analysis resolution in meters | دقة التحليل بالمتر",
    )
    include_rainfall: bool = Field(default=True, description="Include rainfall data from weather service")
    rainfall_period_days: int = Field(default=30, ge=1, le=365, description="Period for rainfall analysis in days")
    correlation_id: str | None = Field(None, max_length=64, description="Correlation ID for tracing")

    @field_validator("field_id", "tenant_id")
    @classmethod
    def validate_id_fields(cls, v: str) -> str:
        """Validate field and tenant ID format."""
        v = v.strip()
        if not v:
            raise ValueError("ID cannot be empty | المعرف لا يمكن أن يكون فارغاً")
        return v

    @field_validator("dem_source")
    @classmethod
    def validate_dem_source(cls, v: str | None) -> str | None:
        """Validate DEM source value."""
        if v is not None:
            v = v.strip().lower()
            valid_sources = {"srtm", "aster", "copernicus", "local", "custom"}
            if v and v not in valid_sources:
                raise ValueError(
                    f"Invalid DEM source '{v}'. Valid options: {', '.join(valid_sources)} | "
                    f"مصدر DEM غير صالح '{v}'. الخيارات الصالحة: {', '.join(valid_sources)}"
                )
        return v


class DrainageAnalysisRequest(BaseModel):
    """Request for drainage network analysis."""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    tenant_id: str | None = Field(None, max_length=64, description="Tenant identifier | معرف المستأجر")
    flow_threshold: int = Field(
        default=100,
        ge=MIN_FLOW_THRESHOLD,
        le=MAX_FLOW_THRESHOLD,
        description="Flow accumulation threshold for stream detection",
    )
    include_pattern: bool = Field(default=True, description="Include drainage pattern classification")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


class WetnessAnalysisRequest(BaseModel):
    """Request for wetness/waterlogging analysis."""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    tenant_id: str | None = Field(None, max_length=64, description="Tenant identifier | معرف المستأجر")
    include_prediction: bool = Field(default=True, description="Include waterlogging prediction")
    rainfall_mm: float | None = Field(
        None, ge=0, le=MAX_RAINFALL_MM, description="Expected rainfall in mm for prediction"
    )

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


class DepressionAnalysisRequest(BaseModel):
    """Request for depression identification."""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    tenant_id: str | None = Field(None, max_length=64, description="Tenant identifier | معرف المستأجر")
    min_depth_m: float = Field(default=0.1, ge=0.01, le=10.0, description="Minimum depression depth in meters")
    min_area_sqm: float = Field(
        default=10.0, ge=1.0, le=1000000.0, description="Minimum depression area in square meters"
    )

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


class StreamDetectionRequest(BaseModel):
    """Request for stream detection."""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    tenant_id: str | None = Field(None, max_length=64, description="Tenant identifier | معرف المستأجر")
    min_order: int = Field(default=1, ge=1, le=6, description="Minimum Strahler stream order to include")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


class BasinDelineationRequest(BaseModel):
    """Request for basin/watershed delineation."""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    tenant_id: str | None = Field(None, max_length=64, description="Tenant identifier | معرف المستأجر")
    pour_point: GeoPoint | None = Field(None, description="Custom pour point for watershed delineation")
    min_area_ha: float = Field(default=0.5, ge=0.1, le=10000.0, description="Minimum basin area in hectares")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


# ==============================================================================
# Response Models - Drainage
# ==============================================================================


class DrainageSegment(BaseModel):
    """A single drainage segment."""

    segment_id: str
    coordinates: list[list[float]] = Field(..., description="Line coordinates [[lon, lat], ...]")
    stream_order: int = Field(..., ge=1, description="Strahler stream order")
    length_m: float = Field(..., ge=0, description="Segment length in meters")
    upstream_area_ha: float = Field(..., ge=0, description="Upstream contributing area in hectares")
    slope_percent: float = Field(..., description="Average slope percentage")


class DrainageNetwork(BaseModel):
    """Complete drainage network analysis result."""

    field_id: str
    total_length_m: float = Field(..., description="Total drainage length")
    drainage_density: float = Field(..., description="Drainage density (m/ha) | كثافة التصريف")
    main_channel_length_m: float = Field(..., description="Main channel length")
    bifurcation_ratio: float = Field(..., description="Bifurcation ratio | نسبة التفرع")
    pattern: DrainageType = Field(..., description="Drainage pattern type")
    pattern_ar: str = Field(..., description="Pattern name in Arabic")
    segments: list[DrainageSegment]
    statistics: dict[str, Any] = Field(default_factory=dict, description="Additional statistics")


class DrainageNetworkResponse(BaseModel):
    """Response model for drainage network endpoint."""

    success: bool = True
    data: DrainageNetwork
    analyzed_at: datetime
    dem_source: str | None = None
    resolution_m: float


# ==============================================================================
# Response Models - Wetness
# ==============================================================================


class WetnessZone(BaseModel):
    """A zone with specific wetness characteristics."""

    zone_id: str
    level: WetnessLevel
    level_ar: str = Field(..., description="Wetness level in Arabic")
    area_ha: float = Field(..., ge=0, description="Zone area in hectares")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of field area")
    twi_mean: float = Field(..., description="Mean Topographic Wetness Index")
    twi_range: tuple[float, float] = Field(..., description="TWI range (min, max)")
    polygon: GeoPolygon | None = None
    recommendations_ar: list[str] = Field(default_factory=list, description="Recommendations in Arabic")
    recommendations_en: list[str] = Field(default_factory=list, description="Recommendations in English")


class WaterloggingPrediction(BaseModel):
    """Prediction for waterlogging risk."""

    rainfall_mm: float = Field(..., description="Rainfall amount used")
    risk_level: DepressionRisk
    risk_level_ar: str
    affected_area_ha: float
    affected_percentage: float
    time_to_drain_hours: float | None = Field(None, description="Estimated time to drain")
    mitigation_ar: list[str] = Field(default_factory=list)
    mitigation_en: list[str] = Field(default_factory=list)


class WetnessAnalysis(BaseModel):
    """Complete wetness analysis result."""

    field_id: str
    total_area_ha: float
    twi_mean: float = Field(..., description="Mean Topographic Wetness Index")
    twi_std: float = Field(..., description="TWI standard deviation")
    twi_min: float
    twi_max: float
    dominant_level: WetnessLevel
    dominant_level_ar: str
    zones: list[WetnessZone]
    waterlogging_prediction: WaterloggingPrediction | None = None
    irrigation_efficiency_score: float = Field(
        ..., ge=0, le=100, description="Irrigation efficiency based on wetness distribution"
    )


class WetnessAnalysisResponse(BaseModel):
    """Response model for wetness analysis endpoint."""

    success: bool = True
    data: WetnessAnalysis
    analyzed_at: datetime


# ==============================================================================
# Response Models - Depressions
# ==============================================================================


class Depression(BaseModel):
    """A single depression/sink identified in the terrain."""

    depression_id: str
    center: GeoPoint
    depth_m: float = Field(..., ge=0, description="Maximum depth in meters")
    area_sqm: float = Field(..., ge=0, description="Area in square meters")
    volume_m3: float = Field(..., ge=0, description="Volume in cubic meters")
    perimeter_m: float = Field(..., ge=0)
    risk_level: DepressionRisk
    risk_level_ar: str
    boundary: GeoPolygon | None = None
    drainage_recommendations_ar: list[str] = Field(default_factory=list)
    drainage_recommendations_en: list[str] = Field(default_factory=list)


class DepressionAnalysis(BaseModel):
    """Complete depression analysis result."""

    field_id: str
    total_depressions: int
    total_volume_m3: float
    total_area_sqm: float
    field_area_ha: float
    depressions_percentage: float = Field(..., description="Percentage of field with depressions")
    high_risk_count: int
    critical_count: int
    depressions: list[Depression]
    summary_ar: str
    summary_en: str


class DepressionAnalysisResponse(BaseModel):
    """Response model for depression analysis endpoint."""

    success: bool = True
    data: DepressionAnalysis
    analyzed_at: datetime


# ==============================================================================
# Response Models - Streams
# ==============================================================================


class Stream(BaseModel):
    """A detected stream segment."""

    stream_id: str
    order: int = Field(..., ge=1, description="Strahler order")
    coordinates: list[list[float]]
    length_m: float
    avg_slope_percent: float
    upstream_area_ha: float
    is_perennial: bool = Field(default=False, description="Whether stream is perennial")


class StreamNetwork(BaseModel):
    """Complete stream network analysis."""

    field_id: str
    total_streams: int
    total_length_m: float
    max_order: int = Field(..., description="Maximum Strahler order")
    streams_by_order: dict[int, int] = Field(..., description="Count of streams by order")
    main_stream_length_m: float
    streams: list[Stream]
    hydraulic_geometry: dict[str, float] = Field(default_factory=dict, description="Hydraulic geometry parameters")


class StreamNetworkResponse(BaseModel):
    """Response model for stream detection endpoint."""

    success: bool = True
    data: StreamNetwork
    analyzed_at: datetime


# ==============================================================================
# Response Models - Basins
# ==============================================================================


class SubBasin(BaseModel):
    """A sub-basin/catchment area."""

    basin_id: str
    area_ha: float
    perimeter_m: float
    centroid: GeoPoint
    pour_point: GeoPoint
    mean_elevation_m: float
    elevation_range_m: float
    mean_slope_percent: float
    time_of_concentration_min: float = Field(..., description="Time of concentration in minutes")
    boundary: GeoPolygon


class BasinDelineation(BaseModel):
    """Complete basin delineation result."""

    field_id: str
    total_basins: int
    total_area_ha: float
    main_basin_area_ha: float
    outlet_point: GeoPoint
    mean_elevation_m: float
    relief_m: float = Field(..., description="Total relief")
    elongation_ratio: float
    circularity_ratio: float
    basins: list[SubBasin]
    runoff_coefficient: float = Field(..., ge=0, le=1, description="Estimated runoff coefficient")


class BasinDelineationResponse(BaseModel):
    """Response model for basin delineation endpoint."""

    success: bool = True
    data: BasinDelineation
    analyzed_at: datetime


# ==============================================================================
# Response Models - Full Analysis
# ==============================================================================


class HydrologyAnalysisResult(BaseModel):
    """Complete hydrology analysis result."""

    field_id: str
    tenant_id: str
    analyzed_at: datetime
    dem_source: str
    resolution_m: float

    # Summary metrics
    field_area_ha: float
    mean_elevation_m: float
    elevation_range_m: float
    mean_slope_percent: float

    # Component results
    drainage: DrainageNetwork
    wetness: WetnessAnalysis
    depressions: DepressionAnalysis
    streams: StreamNetwork
    basins: BasinDelineation

    # Overall assessment
    flood_risk_level: DepressionRisk
    flood_risk_level_ar: str
    drainage_quality_score: float = Field(..., ge=0, le=100, description="Overall drainage quality score")

    # Recommendations
    recommendations_ar: list[str]
    recommendations_en: list[str]

    # Rainfall integration
    rainfall_data: dict[str, Any] | None = None


class HydrologyAnalysisResponse(BaseModel):
    """Response model for full hydrology analysis."""

    success: bool = True
    data: HydrologyAnalysisResult
    processing_time_ms: float


# ==============================================================================
# Arabic Labels Mapping
# ==============================================================================


WETNESS_LEVEL_AR = {
    WetnessLevel.VERY_DRY: "جاف جداً",
    WetnessLevel.DRY: "جاف",
    WetnessLevel.MODERATE: "معتدل",
    WetnessLevel.WET: "رطب",
    WetnessLevel.VERY_WET: "رطب جداً",
    WetnessLevel.WATERLOGGED: "مشبع بالماء",
}

DRAINAGE_TYPE_AR = {
    DrainageType.DENDRITIC: "شجيري",
    DrainageType.PARALLEL: "متوازي",
    DrainageType.TRELLIS: "شبكي",
    DrainageType.RECTANGULAR: "مستطيل",
    DrainageType.RADIAL: "شعاعي",
    DrainageType.CENTRIPETAL: "مركزي",
    DrainageType.DERANGED: "مشوش",
    DrainageType.UNKNOWN: "غير معروف",
}

DEPRESSION_RISK_AR = {
    DepressionRisk.LOW: "منخفض",
    DepressionRisk.MEDIUM: "متوسط",
    DepressionRisk.HIGH: "مرتفع",
    DepressionRisk.CRITICAL: "حرج",
}
