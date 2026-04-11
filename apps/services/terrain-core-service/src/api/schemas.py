"""
Pydantic schemas for Terrain Core Service
نماذج البيانات لخدمة تحليل التضاريس

Provides data models for:
- Terrain analysis requests/responses
- Slope, aspect, and flow analysis
- TWI (Topographic Wetness Index)
- Contour generation
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# =============================================================================
# Enums
# =============================================================================


class DEMSourceType(StrEnum):
    """DEM data source types | أنواع مصادر بيانات الارتفاعات"""

    COPERNICUS = "copernicus"  # Copernicus DEM GLO-30/GLO-90
    SRTM = "srtm"  # NASA SRTM
    ALOS_PALSAR = "alos_palsar"  # JAXA ALOS PALSAR
    LOCAL = "local"  # User-uploaded DEM


class SlopeUnit(StrEnum):
    """Slope measurement units | وحدات قياس الميل"""

    DEGREES = "degrees"  # درجات
    PERCENT = "percent"  # نسبة مئوية
    RADIANS = "radians"  # راديان


class AspectClassification(StrEnum):
    """Aspect cardinal directions | اتجاهات الجوانب الأصلية"""

    FLAT = "flat"  # مسطح
    NORTH = "north"  # شمال
    NORTHEAST = "northeast"  # شمال شرق
    EAST = "east"  # شرق
    SOUTHEAST = "southeast"  # جنوب شرق
    SOUTH = "south"  # جنوب
    SOUTHWEST = "southwest"  # جنوب غرب
    WEST = "west"  # غرب
    NORTHWEST = "northwest"  # شمال غرب


class FlowDirectionMethod(StrEnum):
    """Flow direction calculation methods | طرق حساب اتجاه التدفق"""

    D8 = "d8"  # Eight-direction pour point model
    DINF = "dinf"  # D-Infinity (Tarboton)
    MFD = "mfd"  # Multiple Flow Direction


class CurvatureType(StrEnum):
    """Curvature calculation types | أنواع حساب الانحناء"""

    PLAN = "plan"  # انحناء أفقي
    PROFILE = "profile"  # انحناء طولي
    TOTAL = "total"  # الانحناء الكلي


class TerrainCategory(StrEnum):
    """Terrain classification categories | تصنيفات التضاريس"""

    FLAT = "flat"  # مسطح (0-2%)
    GENTLE = "gentle"  # لطيف (2-5%)
    MODERATE = "moderate"  # معتدل (5-10%)
    STEEP = "steep"  # حاد (10-20%)
    VERY_STEEP = "very_steep"  # حاد جداً (>20%)


# =============================================================================
# Bilingual Field Model
# =============================================================================


class BilingualField(BaseModel):
    """Bilingual field with Arabic and English values | حقل ثنائي اللغة"""

    en: str = Field(..., description="English value | القيمة بالإنجليزية")
    ar: str = Field(..., description="Arabic value | القيمة بالعربية")


# =============================================================================
# Coordinate and Geometry Models
# =============================================================================


class Coordinate(BaseModel):
    """Geographic coordinate | إحداثية جغرافية"""

    longitude: float = Field(..., ge=-180, le=180, description="Longitude | خط الطول")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude | خط العرض")


class BoundingBox(BaseModel):
    """Geographic bounding box | المربع المحيط"""

    min_lon: float = Field(..., ge=-180, le=180, description="Minimum longitude")
    min_lat: float = Field(..., ge=-90, le=90, description="Minimum latitude")
    max_lon: float = Field(..., ge=-180, le=180, description="Maximum longitude")
    max_lat: float = Field(..., ge=-90, le=90, description="Maximum latitude")

    @field_validator("max_lon")
    @classmethod
    def validate_lon_range(cls, v: float, info) -> float:
        if "min_lon" in info.data and v <= info.data["min_lon"]:
            raise ValueError("max_lon must be greater than min_lon")
        return v

    @field_validator("max_lat")
    @classmethod
    def validate_lat_range(cls, v: float, info) -> float:
        if "min_lat" in info.data and v <= info.data["min_lat"]:
            raise ValueError("max_lat must be greater than min_lat")
        return v


class GeoJSONPoint(BaseModel):
    """GeoJSON Point geometry | هندسة نقطة GeoJSON"""

    type: Literal["Point"] = "Point"
    coordinates: list[float] = Field(..., description="Point coordinates [lon, lat] | إحداثيات النقطة")


class GeoJSONLineString(BaseModel):
    """GeoJSON LineString geometry | هندسة خط GeoJSON"""

    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]] = Field(..., description="LineString coordinates | إحداثيات الخط")


class GeoJSONMultiLineString(BaseModel):
    """GeoJSON MultiLineString geometry | هندسة خطوط متعددة GeoJSON"""

    type: Literal["MultiLineString"] = "MultiLineString"
    coordinates: list[list[list[float]]] = Field(
        ..., description="MultiLineString coordinates | إحداثيات الخطوط المتعددة"
    )


class GeoJSONPolygon(BaseModel):
    """GeoJSON Polygon geometry | هندسة مضلع GeoJSON"""

    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]] = Field(..., description="Polygon coordinates | إحداثيات المضلع")


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature | ميزة GeoJSON"""

    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONPoint | GeoJSONLineString | GeoJSONMultiLineString | GeoJSONPolygon = Field(
        ..., description="Feature geometry | هندسة الميزة"
    )
    properties: dict[str, Any] = Field(default_factory=dict, description="Feature properties | خصائص الميزة")
    id: str | int | None = Field(None, description="Feature ID | معرف الميزة")


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection | مجموعة ميزات GeoJSON"""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature] = Field(default_factory=list, description="Features list | قائمة الميزات")


class FieldGeometry(BaseModel):
    """Field boundary geometry | هندسة حدود الحقل"""

    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    geometry: GeoJSONPolygon = Field(..., description="Field boundary | حدود الحقل")
    crs: str = Field(default="EPSG:4326", description="Coordinate Reference System | نظام الإحداثيات")


# =============================================================================
# DEM Processing Models
# =============================================================================


class DEMMetadata(BaseModel):
    """DEM file metadata | بيانات ملف الارتفاعات الوصفية"""

    source: DEMSourceType = Field(..., description="DEM source | مصدر الارتفاعات")
    source_name: BilingualField = Field(..., description="Source name bilingual | اسم المصدر ثنائي اللغة")
    resolution_m: float = Field(..., gt=0, description="Resolution in meters | الدقة بالأمتار")
    crs: str = Field(..., description="Coordinate Reference System")
    bounds: BoundingBox = Field(..., description="Data bounds | حدود البيانات")
    acquisition_date: datetime | None = Field(None, description="Data acquisition date | تاريخ الحصول على البيانات")
    vertical_datum: str = Field(default="EGM96", description="Vertical datum | المرجع الرأسي")
    nodata_value: float = Field(default=-9999.0, description="NoData value | قيمة عدم وجود بيانات")


class DEMStatistics(BaseModel):
    """DEM statistical summary | ملخص إحصائي للارتفاعات"""

    min_elevation_m: float = Field(..., description="Minimum elevation | أدنى ارتفاع")
    max_elevation_m: float = Field(..., description="Maximum elevation | أقصى ارتفاع")
    mean_elevation_m: float = Field(..., description="Mean elevation | متوسط الارتفاع")
    std_elevation_m: float = Field(..., description="Standard deviation | الانحراف المعياري")
    elevation_range_m: float = Field(..., description="Elevation range | نطاق الارتفاع")
    total_pixels: int = Field(..., description="Total pixels | إجمالي البكسلات")
    valid_pixels: int = Field(..., description="Valid pixels | البكسلات الصالحة")


# =============================================================================
# Terrain Analysis Request Models
# =============================================================================


class TerrainAnalysisRequest(BaseModel):
    """Request for full terrain analysis | طلب تحليل التضاريس الكامل"""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    geometry: GeoJSONPolygon | None = Field(None, description="Field boundary (optional if field_id is provided)")
    dem_source: DEMSourceType = Field(
        default=DEMSourceType.COPERNICUS,
        description="DEM data source | مصدر بيانات الارتفاعات",
    )
    target_resolution_m: float | None = Field(
        default=None, gt=0, le=1000.0, description="Target resolution in meters | الدقة المستهدفة"
    )
    target_crs: str | None = Field(default=None, max_length=32, description="Target CRS | نظام الإحداثيات المستهدف")
    include_slope: bool = Field(default=True, description="Include slope analysis | تضمين تحليل الميل")
    include_aspect: bool = Field(default=True, description="Include aspect analysis | تضمين تحليل الجانب")
    include_flow_direction: bool = Field(default=True, description="Include flow direction | تضمين اتجاه التدفق")
    include_flow_accumulation: bool = Field(default=True, description="Include flow accumulation | تضمين تراكم التدفق")
    include_twi: bool = Field(default=True, description="Include TWI | تضمين مؤشر الرطوبة الطبوغرافية")
    include_curvature: bool = Field(default=True, description="Include curvature | تضمين الانحناء")
    include_contours: bool = Field(default=True, description="Include contour lines | تضمين خطوط الكنتور")
    contour_interval_m: float | None = Field(
        default=5.0, gt=0, le=100.0, description="Contour interval in meters | فترة خطوط الكنتور"
    )
    slope_unit: SlopeUnit = Field(default=SlopeUnit.DEGREES, description="Slope unit | وحدة الميل")
    flow_method: FlowDirectionMethod = Field(
        default=FlowDirectionMethod.D8, description="Flow direction method | طريقة اتجاه التدفق"
    )
    tenant_id: str | None = Field(None, max_length=64, description="Tenant identifier | معرف المستأجر")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v

    @field_validator("target_crs")
    @classmethod
    def validate_target_crs(cls, v: str | None) -> str | None:
        """Validate target CRS format."""
        if v is not None:
            v = v.strip().upper()
            # Basic EPSG validation
            import re

            if v and not re.match(r"^EPSG:\d+$", v):
                raise ValueError(
                    f"Invalid CRS format '{v}'. Expected format: EPSG:XXXX | "
                    f"تنسيق نظام الإحداثيات غير صالح '{v}'. التنسيق المتوقع: EPSG:XXXX"
                )
        return v


class SlopeAnalysisRequest(BaseModel):
    """Request for slope analysis only | طلب تحليل الميل فقط"""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    dem_source: DEMSourceType = Field(default=DEMSourceType.COPERNICUS)
    slope_unit: SlopeUnit = Field(default=SlopeUnit.DEGREES)
    classify: bool = Field(default=True, description="Classify slopes into categories | تصنيف الميول")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


class FlowAnalysisRequest(BaseModel):
    """Request for flow analysis | طلب تحليل التدفق"""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    dem_source: DEMSourceType = Field(default=DEMSourceType.COPERNICUS)
    method: FlowDirectionMethod = Field(default=FlowDirectionMethod.D8)
    accumulation_threshold: int = Field(
        default=100, ge=1, le=100000, description="Flow accumulation threshold | عتبة تراكم التدفق"
    )

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


class TWIRequest(BaseModel):
    """Request for Topographic Wetness Index | طلب مؤشر الرطوبة الطبوغرافية"""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    dem_source: DEMSourceType = Field(default=DEMSourceType.COPERNICUS)
    flow_method: FlowDirectionMethod = Field(default=FlowDirectionMethod.D8)

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v


class ContourRequest(BaseModel):
    """Request for contour generation | طلب إنشاء خطوط الكنتور"""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    dem_source: DEMSourceType = Field(default=DEMSourceType.COPERNICUS)
    interval_m: float = Field(
        default=5.0,
        gt=0,
        le=100.0,
        description="Contour interval in meters | فترة الكنتور بالأمتار",
    )
    min_elevation: float | None = Field(
        None,
        ge=-500.0,
        le=9000.0,
        description="Minimum elevation for contours | أدنى ارتفاع للكنتور",
    )
    max_elevation: float | None = Field(
        None,
        ge=-500.0,
        le=9000.0,
        description="Maximum elevation for contours | أقصى ارتفاع للكنتور",
    )
    simplify_tolerance: float | None = Field(
        default=1.0,
        ge=0.0,
        le=100.0,
        description="Line simplification tolerance | تسامح تبسيط الخط",
    )

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v

    @model_validator(mode="after")
    def validate_elevation_range(self) -> "ContourRequest":
        """Validate that min_elevation < max_elevation if both are provided."""
        if self.min_elevation is not None and self.max_elevation is not None:
            if self.min_elevation >= self.max_elevation:
                raise ValueError(
                    "min_elevation must be less than max_elevation | أدنى ارتفاع يجب أن يكون أقل من أقصى ارتفاع"
                )
        return self


# =============================================================================
# Terrain Analysis Response Models
# =============================================================================


class SlopeResult(BaseModel):
    """Slope analysis result | نتيجة تحليل الميل"""

    unit: SlopeUnit = Field(..., description="Slope unit | وحدة الميل")
    unit_name: BilingualField = Field(..., description="Unit name | اسم الوحدة")
    min_slope: float = Field(..., description="Minimum slope | أدنى ميل")
    max_slope: float = Field(..., description="Maximum slope | أقصى ميل")
    mean_slope: float = Field(..., description="Mean slope | متوسط الميل")
    std_slope: float = Field(..., description="Slope standard deviation | الانحراف المعياري للميل")
    classification: dict[str, float] | None = Field(
        None, description="Slope classification percentages | نسب تصنيف الميل"
    )
    raster_url: str | None = Field(None, description="URL to slope raster | رابط خريطة الميل")


class AspectResult(BaseModel):
    """Aspect analysis result | نتيجة تحليل الجانب"""

    dominant_direction: AspectClassification = Field(..., description="Dominant aspect direction | الاتجاه السائد")
    dominant_direction_name: BilingualField = Field(..., description="Dominant direction name | اسم الاتجاه السائد")
    distribution: dict[str, float] = Field(
        ..., description="Aspect distribution by direction | توزيع الجوانب حسب الاتجاه"
    )
    mean_aspect_degrees: float = Field(..., description="Mean aspect in degrees | متوسط الجانب بالدرجات")
    raster_url: str | None = Field(None, description="URL to aspect raster | رابط خريطة الجانب")


class FlowDirectionResult(BaseModel):
    """Flow direction analysis result | نتيجة تحليل اتجاه التدفق"""

    method: FlowDirectionMethod = Field(..., description="Method used | الطريقة المستخدمة")
    method_name: BilingualField = Field(..., description="Method name | اسم الطريقة")
    dominant_direction: str = Field(..., description="Dominant flow direction | اتجاه التدفق السائد")
    direction_distribution: dict[str, float] = Field(
        ..., description="Flow direction distribution | توزيع اتجاه التدفق"
    )
    raster_url: str | None = Field(None, description="URL to flow direction raster | رابط خريطة اتجاه التدفق")


class FlowAccumulationResult(BaseModel):
    """Flow accumulation analysis result | نتيجة تحليل تراكم التدفق"""

    max_accumulation: int = Field(..., description="Maximum flow accumulation | أقصى تراكم تدفق")
    mean_accumulation: float = Field(..., description="Mean flow accumulation | متوسط تراكم التدفق")
    drainage_density: float = Field(..., description="Drainage density | كثافة الصرف")
    channel_pixels: int = Field(..., description="Channel pixels (above threshold) | بكسلات القنوات")
    threshold_used: int = Field(..., description="Threshold used | العتبة المستخدمة")
    streams_geojson: GeoJSONFeatureCollection | None = Field(
        None, description="Stream network GeoJSON | شبكة المجاري بصيغة GeoJSON"
    )
    raster_url: str | None = Field(None, description="URL to flow accumulation raster | رابط خريطة تراكم التدفق")


class TWIResult(BaseModel):
    """Topographic Wetness Index result | نتيجة مؤشر الرطوبة الطبوغرافية"""

    name: BilingualField = Field(
        default_factory=lambda: BilingualField(en="Topographic Wetness Index", ar="مؤشر الرطوبة الطبوغرافية"),
        description="Index name | اسم المؤشر",
    )
    min_twi: float = Field(..., description="Minimum TWI | أدنى TWI")
    max_twi: float = Field(..., description="Maximum TWI | أقصى TWI")
    mean_twi: float = Field(..., description="Mean TWI | متوسط TWI")
    std_twi: float = Field(..., description="TWI standard deviation | الانحراف المعياري")
    high_moisture_area_pct: float = Field(..., description="High moisture area percentage | نسبة المنطقة عالية الرطوبة")
    interpretation: BilingualField = Field(..., description="TWI interpretation | تفسير المؤشر")
    raster_url: str | None = Field(None, description="URL to TWI raster | رابط خريطة TWI")


class CurvatureResult(BaseModel):
    """Curvature analysis result | نتيجة تحليل الانحناء"""

    curvature_type: CurvatureType = Field(..., description="Curvature type | نوع الانحناء")
    type_name: BilingualField = Field(..., description="Type name | اسم النوع")
    min_curvature: float = Field(..., description="Minimum curvature | أدنى انحناء")
    max_curvature: float = Field(..., description="Maximum curvature | أقصى انحناء")
    mean_curvature: float = Field(..., description="Mean curvature | متوسط الانحناء")
    convex_pct: float = Field(..., description="Convex area percentage | نسبة المنطقة المحدبة")
    concave_pct: float = Field(..., description="Concave area percentage | نسبة المنطقة المقعرة")
    flat_pct: float = Field(..., description="Flat area percentage | نسبة المنطقة المسطحة")
    raster_url: str | None = Field(None, description="URL to curvature raster | رابط خريطة الانحناء")


class ContourLine(BaseModel):
    """Single contour line | خط كنتور واحد"""

    elevation_m: float = Field(..., description="Elevation in meters | الارتفاع بالأمتار")
    length_m: float = Field(..., description="Length in meters | الطول بالأمتار")
    is_major: bool = Field(default=False, description="Is major contour | خط كنتور رئيسي")
    geometry: GeoJSONLineString | GeoJSONMultiLineString = Field(
        ..., description="LineString or MultiLineString GeoJSON geometry | هندسة الخط"
    )


class ContourResult(BaseModel):
    """Contour generation result | نتيجة إنشاء خطوط الكنتور"""

    interval_m: float = Field(..., description="Contour interval | فترة الكنتور")
    min_elevation_m: float = Field(..., description="Minimum elevation | أدنى ارتفاع")
    max_elevation_m: float = Field(..., description="Maximum elevation | أقصى ارتفاع")
    total_contours: int = Field(..., description="Total contour lines | إجمالي خطوط الكنتور")
    major_interval_m: float = Field(..., description="Major contour interval | فترة الكنتور الرئيسي")
    contours: list[ContourLine] = Field(default_factory=list, description="Contour lines | خطوط الكنتور")
    geojson_url: str | None = Field(None, description="URL to contours GeoJSON | رابط ملف GeoJSON")


class TerrainIrrigationRecommendation(BaseModel):
    """Irrigation recommendation based on terrain | توصية الري بناءً على التضاريس"""

    zone_id: str = Field(..., description="Zone identifier | معرف المنطقة")
    zone_name: BilingualField = Field(..., description="Zone name | اسم المنطقة")
    area_ha: float = Field(..., description="Area in hectares | المساحة بالهكتار")
    mean_slope_pct: float = Field(..., description="Mean slope percentage | متوسط نسبة الميل")
    mean_twi: float = Field(..., description="Mean TWI | متوسط TWI")
    irrigation_suitability: str = Field(..., description="Suitability category | فئة الملاءمة")
    suitability_name: BilingualField = Field(..., description="Suitability name | اسم الملاءمة")
    recommended_method: BilingualField = Field(..., description="Recommended irrigation method | طريقة الري الموصى بها")
    water_retention_capacity: str = Field(..., description="Water retention capacity | قدرة احتفاظ المياه")
    erosion_risk: str = Field(..., description="Erosion risk level | مستوى خطر التعرية")
    notes: BilingualField = Field(..., description="Additional notes | ملاحظات إضافية")


class TerrainAnalysisResponse(BaseModel):
    """Full terrain analysis response | استجابة تحليل التضاريس الكاملة"""

    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    analysis_id: str = Field(..., description="Analysis identifier | معرف التحليل")
    status: str = Field(..., description="Analysis status | حالة التحليل")
    analyzed_at: datetime = Field(..., description="Analysis timestamp | وقت التحليل")

    # DEM Information
    dem_metadata: DEMMetadata = Field(..., description="DEM metadata | بيانات الارتفاعات الوصفية")
    dem_statistics: DEMStatistics = Field(..., description="DEM statistics | إحصائيات الارتفاعات")

    # Terrain Indicators
    slope: SlopeResult | None = Field(None, description="Slope analysis | تحليل الميل")
    aspect: AspectResult | None = Field(None, description="Aspect analysis | تحليل الجانب")
    flow_direction: FlowDirectionResult | None = Field(None, description="Flow direction | اتجاه التدفق")
    flow_accumulation: FlowAccumulationResult | None = Field(None, description="Flow accumulation | تراكم التدفق")
    twi: TWIResult | None = Field(None, description="Topographic Wetness Index | مؤشر الرطوبة الطبوغرافية")
    plan_curvature: CurvatureResult | None = Field(None, description="Plan curvature | الانحناء الأفقي")
    profile_curvature: CurvatureResult | None = Field(None, description="Profile curvature | الانحناء الطولي")
    contours: ContourResult | None = Field(None, description="Contour lines | خطوط الكنتور")

    # Recommendations
    terrain_category: TerrainCategory = Field(..., description="Overall terrain category | تصنيف التضاريس العام")
    terrain_category_name: BilingualField = Field(..., description="Category name | اسم التصنيف")
    irrigation_recommendations: list[TerrainIrrigationRecommendation] = Field(
        default_factory=list,
        description="Irrigation recommendations | توصيات الري",
    )

    # Processing info
    processing_time_ms: int = Field(..., description="Processing time in milliseconds | وقت المعالجة بالمللي ثانية")
    warnings: list[str] = Field(default_factory=list, description="Processing warnings | تحذيرات المعالجة")


# =============================================================================
# Simple Response Models
# =============================================================================


class SlopeAnalysisResponse(BaseModel):
    """Simple slope analysis response | استجابة تحليل الميل البسيطة"""

    field_id: str
    analyzed_at: datetime
    dem_source: DEMSourceType
    slope: SlopeResult
    processing_time_ms: int


class FlowAnalysisResponse(BaseModel):
    """Flow analysis response | استجابة تحليل التدفق"""

    field_id: str
    analyzed_at: datetime
    dem_source: DEMSourceType
    flow_direction: FlowDirectionResult
    flow_accumulation: FlowAccumulationResult
    processing_time_ms: int


class TWIAnalysisResponse(BaseModel):
    """TWI analysis response | استجابة تحليل TWI"""

    field_id: str
    analyzed_at: datetime
    dem_source: DEMSourceType
    twi: TWIResult
    processing_time_ms: int


class ContourAnalysisResponse(BaseModel):
    """Contour analysis response | استجابة تحليل الكنتور"""

    field_id: str
    analyzed_at: datetime
    dem_source: DEMSourceType
    contours: ContourResult
    processing_time_ms: int


class AspectAnalysisResponse(BaseModel):
    """
    Aspect analysis response | استجابة تحليل الجانب

    Returns sun-facing direction (0-360 degrees, 0=North, clockwise)
    computed from the DEM for the field. Contract endpoint:
    GET /api/v1/terrain/aspect/{field_id}
    """

    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    analyzed_at: datetime = Field(..., description="Analysis timestamp | وقت التحليل")
    dem_source: DEMSourceType = Field(..., description="DEM source used | مصدر الارتفاعات")
    aspect: AspectResult = Field(..., description="Aspect analysis result | نتيجة تحليل الجانب")
    processing_time_ms: int = Field(..., description="Processing time (ms) | وقت المعالجة (ملي ثانية)")


# =============================================================================
# Error Response Models
# =============================================================================


class TerrainErrorDetail(BaseModel):
    """Terrain service error detail | تفاصيل خطأ خدمة التضاريس"""

    code: str = Field(..., description="Error code | رمز الخطأ")
    message: str = Field(..., description="Error message | رسالة الخطأ")
    message_ar: str = Field(..., description="Arabic error message | رسالة الخطأ بالعربية")
    field_id: str | None = Field(None, description="Related field ID | معرف الحقل المرتبط")
    details: dict[str, Any] | None = Field(None, description="Additional details | تفاصيل إضافية")


# =============================================================================
# DEM Source Response Models
# =============================================================================


class DEMSourceInfo(BaseModel):
    """DEM source information | معلومات مصدر الارتفاعات"""

    source: DEMSourceType = Field(..., description="Source type | نوع المصدر")
    name: str = Field(..., description="Source name | اسم المصدر")
    name_ar: str = Field(..., description="Arabic source name | اسم المصدر بالعربية")
    description: str = Field(..., description="Source description | وصف المصدر")
    description_ar: str = Field(..., description="Arabic description | الوصف بالعربية")
    resolution_m: float = Field(..., description="Resolution in meters | الدقة بالأمتار")
    coverage: str = Field(..., description="Geographic coverage | التغطية الجغرافية")
    is_available: bool = Field(default=True, description="Is source available | هل المصدر متاح")


class DEMSourcesResponse(BaseModel):
    """Response for listing DEM sources | استجابة قائمة مصادر الارتفاعات"""

    sources: list[DEMSourceInfo] = Field(..., description="Available DEM sources | مصادر الارتفاعات المتاحة")
    default: str = Field(..., description="Default source | المصدر الافتراضي")
    default_name: BilingualField = Field(..., description="Default source name | اسم المصدر الافتراضي")


class DEMDataBounds(BaseModel):
    """DEM data bounds | حدود بيانات الارتفاعات"""

    min_lon: float = Field(..., description="Minimum longitude | خط الطول الأدنى")
    min_lat: float = Field(..., description="Minimum latitude | خط العرض الأدنى")
    max_lon: float = Field(..., description="Maximum longitude | خط الطول الأقصى")
    max_lat: float = Field(..., description="Maximum latitude | خط العرض الأقصى")


class DEMDataRequest(BaseModel):
    """Request for DEM data | طلب بيانات الارتفاعات"""

    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    tenant_id: str | None = Field(None, description="Tenant identifier | معرف المستأجر")
    dem_source: DEMSourceType = Field(default=DEMSourceType.COPERNICUS, description="DEM source | مصدر الارتفاعات")
    resolution_m: float | None = Field(None, description="Target resolution in meters | الدقة المستهدفة بالمتر")


class DEMDataResponse(BaseModel):
    """Response containing DEM data for downstream services | استجابة بيانات الارتفاعات للخدمات المتصلة"""

    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    dem_source: DEMSourceType = Field(..., description="DEM source used | مصدر الارتفاعات المستخدم")
    bounds: DEMDataBounds = Field(..., description="Data bounds | حدود البيانات")
    resolution_m: float = Field(..., description="Resolution in meters | الدقة بالمتر")
    rows: int = Field(..., description="Number of rows | عدد الصفوف")
    cols: int = Field(..., description="Number of columns | عدد الأعمدة")
    crs: str = Field(..., description="Coordinate reference system | نظام الإحداثيات")
    nodata_value: float = Field(..., description="NoData value | قيمة عدم وجود بيانات")
    elevation_min: float = Field(..., description="Minimum elevation (m) | أدنى ارتفاع (م)")
    elevation_max: float = Field(..., description="Maximum elevation (m) | أقصى ارتفاع (م)")
    elevation_mean: float = Field(..., description="Mean elevation (m) | متوسط الارتفاع (م)")
    elevation_data: list[list[float]] | None = Field(
        None, description="Elevation data array (optional, for small fields) | مصفوفة الارتفاعات"
    )
    download_url: str | None = Field(None, description="URL to download full DEM data | رابط تنزيل البيانات الكاملة")
    analyzed_at: datetime = Field(..., description="Analysis timestamp | وقت التحليل")


# =============================================================================
# Erosion (RUSLE) Schemas — Phase 3
# =============================================================================


class SoilTextureEnum(StrEnum):
    """USDA soil texture classes used by the RUSLE K-factor lookup."""

    SAND = "sand"
    LOAMY_SAND = "loamy_sand"
    SANDY_LOAM = "sandy_loam"
    LOAM = "loam"
    SILT_LOAM = "silt_loam"
    CLAY_LOAM = "clay_loam"
    CLAY = "clay"


class ErosionRiskLevelEnum(StrEnum):
    """FAO Water Erosion Classification bands."""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class ErosionAssessmentRequest(BaseModel):
    """
    Inputs for a RUSLE (Revised Universal Soil Loss Equation) assessment.

    Every factor is an aggregated per-field value. For sub-field
    variability, call this endpoint once per zone and compose the
    results on the caller side.
    """

    field_id: str = Field(..., min_length=1, max_length=100, description="Field identifier")
    tenant_id: str = Field(..., min_length=1, max_length=100, description="Tenant identifier")

    # Topography — usually provided by the existing /terrain/slope endpoint
    slope_pct: float = Field(..., ge=0, le=200, description="Mean slope percentage (0-200)")
    slope_length_m: float | None = Field(
        None,
        ge=1,
        le=1000,
        description="Slope length in metres (default 22.13, the RUSLE reference)",
    )

    # Soil
    soil_texture: SoilTextureEnum = Field(..., description="USDA soil texture class — drives the K factor")

    # Climate
    annual_rainfall_mm: float = Field(..., ge=0, le=5000, description="Mean annual precipitation (mm)")
    rainy_days_per_year: int = Field(..., ge=0, le=365, description="Mean rainy days per year")

    # Land cover
    cover_type: str = Field(
        "bare_soil",
        max_length=64,
        description=(
            "Crop / cover class (bare_soil, fallow, wheat, barley, corn, date_palm, olive, citrus, grass, forest, ...)"
        ),
    )
    conservation_practice: str = Field(
        "none",
        max_length=64,
        description=("Support practice (none, contour_farming, strip_cropping, terraces, bench_terraces)"),
    )

    @field_validator("field_id", "tenant_id")
    @classmethod
    def _validate_identifier(cls, value: str) -> str:
        # Match the platform-wide pattern used on other endpoints to
        # harden against path-traversal and header injection.
        import re

        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
            raise ValueError("identifier must match [A-Za-z0-9_-]{1,100}")
        return value


class RUSLEFactorsResponse(BaseModel):
    """The 5 RUSLE factors that multiply to produce A = RKLSCP."""

    r_factor: float = Field(..., description="Rainfall-runoff erosivity (MJ·mm/ha·h·yr)")
    k_factor: float = Field(..., description="Soil erodibility (tonnes·ha·h/ha·MJ·mm)")
    ls_factor: float = Field(..., description="Slope length × steepness (dimensionless)")
    c_factor: float = Field(..., description="Cover-management (dimensionless, 0-1)")
    p_factor: float = Field(..., description="Support practice (dimensionless, 0-1)")


class ErosionAssessmentResponse(BaseModel):
    """
    Full RUSLE assessment output — the honest answer that replaces the
    Phase-1 ``erosion_risk: "low"`` stub in the irrigation recommendation
    helper.
    """

    field_id: str
    tenant_id: str
    soil_loss_t_ha_yr: float = Field(..., description="Annual soil loss A = RKLSCP (tonnes / hectare / year)")
    risk_level: ErosionRiskLevelEnum = Field(
        ..., description="FAO risk band (none / low / moderate / high / severe / catastrophic)"
    )
    risk_level_ar: str = Field(..., description="Arabic label for the risk band")
    factors: RUSLEFactorsResponse = Field(..., description="Per-factor breakdown")
    factor_contributions_pct: dict[str, float] = Field(
        default_factory=dict,
        description="Log-normalised per-factor contribution (%) — which factor drives the loss",
    )
    recommendations: list[str] = Field(default_factory=list, description="Mitigation actions (English)")
    recommendations_ar: list[str] = Field(default_factory=list, description="خطوات التخفيف (عربي)")
    assessed_at: datetime = Field(..., description="Assessment timestamp")


# =============================================================================
# Erosion (RWEQ wind + Combined) Schemas — Phase 3.1
# =============================================================================


class SurfaceRoughnessEnum(StrEnum):
    """
    Chepil surface roughness classes used by the RWEQ-lite K' factor.
    فئات خشونة السطح (شيبيل) المستخدمة في عامل K' لمعادلة RWEQ-lite.
    """

    SMOOTH = "smooth"
    MEDIUM = "medium"
    ROUGH = "rough"
    FURROWED = "furrowed"


class ResidueStateEnum(StrEnum):
    """
    Crop residue state after harvest — drives the RWEQ COG cover factor.
    حالة بقايا المحاصيل بعد الحصاد — تحدد عامل الغطاء COG في RWEQ.
    """

    BARE = "bare"
    FLAT = "flat"
    STANDING = "standing"


class DominantProcessEnum(StrEnum):
    """
    Which erosion process dominates a field's combined risk.
    العملية المسيطرة على الخطر المشترك لتعرية الحقل.
    """

    WATER = "water"
    WIND = "wind"
    BOTH = "both"
    NONE = "none"


def _validate_erosion_identifier(value: str) -> str:
    """Shared identifier regex validator for erosion request models."""
    import re

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise ValueError("identifier must match [A-Za-z0-9_-]{1,100}")
    return value


class WindErosionAssessmentRequest(BaseModel):
    """
    Inputs for a RWEQ-lite (Revised Wind Erosion Equation) assessment.

    مدخلات تقييم تعرية الرياح باستخدام معادلة RWEQ-lite.

    Use this for flat grain-producing plains (Tihama, Marib, Al-Jawf,
    Hadramawt) where slope is near-zero and wind is the dominant
    erosion driver. For sloped fields, pair with the water erosion
    endpoint — or call ``/erosion/combined`` for both at once.
    """

    field_id: str = Field(
        ..., min_length=1, max_length=100, description="Field identifier | معرف الحقل"
    )
    tenant_id: str = Field(
        ..., min_length=1, max_length=100, description="Tenant identifier | معرف المستأجر"
    )

    # Soil — either a USDA texture class OR a Yemen profile key.
    texture_key: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description=(
            "Soil texture key — USDA class (sand, loam, clay, ...) or Yemen "
            "profile (tihama_sandy_loam, highland_clay_loam, ...) | "
            "مفتاح قوام التربة (USDA أو ملف تعريف يمني)"
        ),
    )

    # Climate
    mean_wind_speed_ms: float = Field(
        ...,
        ge=0,
        le=50,
        description="Mean wind speed (m/s) — use peak-month mean for conservative planning | متوسط سرعة الرياح (م/ث)",
    )
    annual_rainfall_mm: float = Field(
        ...,
        ge=0,
        le=5000,
        description="Mean annual precipitation (mm) | متوسط الهطول السنوي (مم)",
    )
    annual_et0_mm: float = Field(
        ...,
        ge=100,
        le=5000,
        description="Annual reference evapotranspiration total (mm) | إجمالي التبخر النتح المرجعي السنوي (مم)",
    )

    # Surface / cover
    roughness: SurfaceRoughnessEnum = Field(
        SurfaceRoughnessEnum.MEDIUM,
        description="Chepil surface roughness class (drives K') | فئة خشونة السطح",
    )
    residue_state: ResidueStateEnum = Field(
        ResidueStateEnum.BARE,
        description="Crop residue state after harvest (drives COG) | حالة بقايا المحصول",
    )
    residue_cover_pct: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Flat/standing residue cover (%) | نسبة تغطية البقايا (٪)",
    )
    canopy_cover_pct: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Active canopy cover (%) | نسبة تغطية المظلة النباتية (٪)",
    )
    unsheltered_length_m: float = Field(
        100.0,
        ge=1,
        le=5000,
        description=(
            "Unsheltered field length along the prevailing wind direction (m) | "
            "طول الحقل غير المحمي باتجاه الرياح السائدة (م)"
        ),
    )

    @field_validator("field_id", "tenant_id")
    @classmethod
    def _validate_identifier(cls, value: str) -> str:
        return _validate_erosion_identifier(value)


class RWEQFactorsResponse(BaseModel):
    """
    The 5 RWEQ-lite factors that drive the wind soil loss estimate.
    العوامل الخمسة في معادلة RWEQ-lite التي تحدد تقدير فقد التربة بالرياح.
    """

    wind_factor: float = Field(
        ..., description="WF — aridity-weighted wind kinetic energy | عامل الرياح"
    )
    erodibility_factor: float = Field(
        ..., description="EF — soil erodibility from texture + OM | عامل قابلية التعرية"
    )
    soil_crust_factor: float = Field(
        ..., description="SCF — clay + OM surface crust protection | عامل قشرة التربة"
    )
    roughness_factor: float = Field(
        ..., description="K' — Chepil tillage / surface roughness | عامل الخشونة"
    )
    cover_factor: float = Field(
        ..., description="COG — residue + canopy ground cover | عامل الغطاء"
    )


class WindErosionAssessmentResponse(BaseModel):
    """
    Full RWEQ-lite assessment output for a single field.
    مخرجات تقييم RWEQ-lite الكامل لحقل واحد.
    """

    field_id: str
    tenant_id: str
    soil_loss_t_ha_yr: float = Field(
        ..., description="Annual wind soil loss (tonnes / hectare / year) | فقد التربة بالرياح سنوياً"
    )
    risk_level: ErosionRiskLevelEnum = Field(
        ...,
        description="FAO risk band (none / low / moderate / high / severe / catastrophic)",
    )
    risk_level_ar: str = Field(..., description="Arabic label for the risk band")
    factors: RWEQFactorsResponse = Field(..., description="Per-factor breakdown")
    factor_contributions_pct: dict[str, float] = Field(
        default_factory=dict,
        description="Log-normalised per-factor contribution (%) — which factor drives the loss",
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Wind-erosion mitigation actions (English)"
    )
    recommendations_ar: list[str] = Field(
        default_factory=list, description="خطوات التخفيف من تعرية الرياح (عربي)"
    )
    assessed_at: datetime = Field(..., description="Assessment timestamp")


class CombinedErosionAssessmentRequest(BaseModel):
    """
    Inputs for a combined water (RUSLE) + wind (RWEQ-lite) erosion
    assessment. Every field from :class:`ErosionAssessmentRequest` and
    :class:`WindErosionAssessmentRequest` is present here.

    مدخلات تقييم التعرية المشترك (تعرية المياه + تعرية الرياح).

    ``texture_key`` is optional: when omitted, the engine derives it
    from the RUSLE ``soil_texture`` USDA class. Pass an explicit key
    to use a Yemen-specific soil profile (e.g. ``tihama_sandy_loam``)
    that the USDA class doesn't represent.
    """

    field_id: str = Field(
        ..., min_length=1, max_length=100, description="Field identifier | معرف الحقل"
    )
    tenant_id: str = Field(
        ..., min_length=1, max_length=100, description="Tenant identifier | معرف المستأجر"
    )

    # --- Water erosion (RUSLE) inputs ---
    slope_pct: float = Field(
        ..., ge=0, le=200, description="Mean slope percentage (0-200) | متوسط نسبة الميل"
    )
    slope_length_m: float | None = Field(
        None,
        ge=1,
        le=1000,
        description="Slope length in metres (default 22.13, the RUSLE reference) | طول الميل (م)",
    )
    soil_texture: SoilTextureEnum = Field(
        ...,
        description="USDA soil texture class — drives the RUSLE K factor | فئة قوام التربة",
    )
    annual_rainfall_mm: float = Field(
        ..., ge=0, le=5000, description="Mean annual precipitation (mm) | الهطول السنوي"
    )
    rainy_days_per_year: int = Field(
        ..., ge=0, le=365, description="Mean rainy days per year | عدد الأيام الممطرة سنوياً"
    )
    cover_type: str = Field(
        "bare_soil",
        max_length=64,
        description="Crop / cover class (bare_soil, wheat, date_palm, ...) | نوع الغطاء النباتي",
    )
    conservation_practice: str = Field(
        "none",
        max_length=64,
        description="Support practice (none, contour_farming, bench_terraces, ...) | ممارسة الحفاظ",
    )

    # --- Wind erosion (RWEQ-lite) inputs ---
    texture_key: str | None = Field(
        None,
        max_length=64,
        description=(
            "Optional Yemen-specific texture key (e.g. tihama_sandy_loam). "
            "If omitted, derived from the RUSLE soil_texture. | "
            "مفتاح قوام تربة يمني اختياري، يُشتق من soil_texture إذا لم يُحدد"
        ),
    )
    mean_wind_speed_ms: float = Field(
        ...,
        ge=0,
        le=50,
        description="Mean wind speed (m/s) — use peak-month mean | متوسط سرعة الرياح",
    )
    annual_et0_mm: float = Field(
        ...,
        ge=100,
        le=5000,
        description="Annual reference evapotranspiration total (mm) | إجمالي التبخر النتح المرجعي",
    )
    roughness: SurfaceRoughnessEnum = Field(
        SurfaceRoughnessEnum.MEDIUM,
        description="Chepil surface roughness class | فئة خشونة السطح",
    )
    residue_state: ResidueStateEnum = Field(
        ResidueStateEnum.BARE,
        description="Crop residue state after harvest | حالة بقايا المحصول",
    )
    residue_cover_pct: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Flat/standing residue cover (%) | نسبة تغطية البقايا",
    )
    canopy_cover_pct: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Active canopy cover (%) | نسبة تغطية المظلة",
    )
    unsheltered_length_m: float = Field(
        100.0,
        ge=1,
        le=5000,
        description="Unsheltered field length along prevailing wind (m) | طول الحقل غير المحمي",
    )

    @field_validator("field_id", "tenant_id")
    @classmethod
    def _validate_identifier(cls, value: str) -> str:
        return _validate_erosion_identifier(value)


class CombinedErosionAssessmentResponse(BaseModel):
    """
    Unified water (RUSLE) + wind (RWEQ-lite) erosion assessment.

    مخرجات التقييم المشترك لتعرية التربة (مياه + رياح).

    The ``overall_risk_level`` is the *worst* of the two sub-results
    (the FAO band with the highest ordinal). ``dominant_process``
    surfaces which engine is driving that worst-case, so operators can
    prioritise actions accordingly. Both sub-results are preserved in
    the ``water`` and ``wind`` fields so callers that care about the
    per-process breakdown can introspect them.
    """

    field_id: str
    tenant_id: str
    overall_risk_level: ErosionRiskLevelEnum = Field(
        ..., description="Worst-of-two FAO risk band | أعلى مستوى خطر"
    )
    overall_risk_level_ar: str = Field(
        ..., description="Arabic label for the overall risk band"
    )
    dominant_process: DominantProcessEnum = Field(
        ..., description="Which erosion process dominates the risk | العملية المسيطرة"
    )
    water: ErosionAssessmentResponse = Field(
        ..., description="Full RUSLE (water) sub-result | نتيجة تعرية المياه"
    )
    wind: WindErosionAssessmentResponse = Field(
        ..., description="Full RWEQ-lite (wind) sub-result | نتيجة تعرية الرياح"
    )
    combined_recommendations: list[str] = Field(
        default_factory=list,
        description="Priority-ordered mitigation actions across both processes (English)",
    )
    combined_recommendations_ar: list[str] = Field(
        default_factory=list,
        description="خطوات التخفيف مرتبة حسب الأولوية لكلا العمليتين (عربي)",
    )
    assessed_at: datetime = Field(..., description="Assessment timestamp")


class YemenRegionErosionRequest(BaseModel):
    """
    Minimum-input combined erosion request for a Yemeni field, using
    a named agro-ecological region to fill in climate + soil defaults.

    طلب تقييم التعرية المشترك لحقل يمني بالحد الأدنى من المدخلات
    باستخدام منطقة زراعية مسماة لملء القيم المناخية والتربة تلقائياً.

    Known regions: ``tihama``, ``eastern_plateau``, ``hadhramaut``,
    ``southern_coast``, ``highlands``. Only field-specific variables
    (slope, cover, residue) need to be supplied — everything else is
    inferred from ``YEMEN_REGION_PRESETS`` in
    ``shared/terrain_erosion/combined.py``.
    """

    field_id: str = Field(
        ..., min_length=1, max_length=100, description="Field identifier | معرف الحقل"
    )
    tenant_id: str = Field(
        ..., min_length=1, max_length=100, description="Tenant identifier | معرف المستأجر"
    )
    region: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description=(
            "Yemen agro-ecological region key (tihama, eastern_plateau, "
            "hadhramaut, southern_coast, highlands) | المنطقة الزراعية اليمنية"
        ),
    )
    slope_pct: float = Field(
        1.0,
        ge=0,
        le=200,
        description="Mean slope percentage (0-200), default 1% for plains | نسبة الميل",
    )
    soil_texture: SoilTextureEnum | None = Field(
        None,
        description=(
            "Optional USDA soil texture override — when None, inferred from "
            "the regional Yemen profile | فئة قوام تربة اختيارية تُستنتج تلقائياً"
        ),
    )
    cover_type: str = Field(
        "bare_soil",
        max_length=64,
        description="Crop / cover class for the RUSLE C factor | نوع الغطاء النباتي",
    )
    conservation_practice: str = Field(
        "none",
        max_length=64,
        description="Support practice for the RUSLE P factor | ممارسة الحفاظ",
    )
    residue_state: ResidueStateEnum = Field(
        ResidueStateEnum.BARE,
        description="Crop residue state after harvest | حالة بقايا المحصول",
    )
    residue_cover_pct: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Flat/standing residue cover (%) | نسبة تغطية البقايا",
    )
    canopy_cover_pct: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Active canopy cover (%) | نسبة تغطية المظلة",
    )

    @field_validator("field_id", "tenant_id")
    @classmethod
    def _validate_identifier(cls, value: str) -> str:
        return _validate_erosion_identifier(value)
