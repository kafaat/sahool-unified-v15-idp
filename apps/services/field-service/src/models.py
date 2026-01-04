"""
SAHOOL Field Service - Data Models
نماذج بيانات خدمة الحقول
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ============== Enums ==============


class FieldStatus(str, Enum):
    """حالة الحقل"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    PENDING = "pending"


class SoilType(str, Enum):
    """نوع التربة"""

    CLAY = "clay"
    SANDY = "sandy"
    LOAM = "loam"
    SANDY_LOAM = "sandy_loam"
    CLAY_LOAM = "clay_loam"
    SILT = "silt"
    ROCKY = "rocky"
    UNKNOWN = "unknown"


class IrrigationSource(str, Enum):
    """مصدر الري"""

    WELL = "well"
    CANAL = "canal"
    RAINWATER = "rainwater"
    RIVER = "river"
    SPRING = "spring"
    RESERVOIR = "reservoir"
    NONE = "none"


class CropSeasonStatus(str, Enum):
    """حالة موسم المحصول"""

    PLANNING = "planning"
    ACTIVE = "active"
    HARVESTED = "harvested"
    FAILED = "failed"


class ZonePurpose(str, Enum):
    """غرض المنطقة"""

    SOIL_DIFFERENCE = "soil_difference"
    WATER_ACCESS = "water_access"
    SLOPE = "slope"
    SHADE = "shade"
    EXPERIMENTAL = "experimental"
    OTHER = "other"


# ============== GeoJSON Models ==============


class GeoPoint(BaseModel):
    """نقطة جغرافية"""

    lat: float = Field(..., ge=-90, le=90, description="خط العرض")
    lng: float = Field(..., ge=-180, le=180, description="خط الطول")


class GeoPolygon(BaseModel):
    """مضلع جغرافي - GeoJSON Polygon"""

    type: str = Field(default="Polygon")
    coordinates: list[list[list[float]]] = Field(
        ..., description="إحداثيات المضلع [[lng, lat], ...]"
    )

    @field_validator("coordinates")
    @classmethod
    def validate_polygon(cls, v: list[list[list[float]]]) -> list[list[list[float]]]:
        """التحقق من صحة المضلع"""
        if not v or not v[0]:
            raise ValueError("يجب أن يحتوي المضلع على حلقة خارجية واحدة على الأقل")

        outer_ring = v[0]
        if len(outer_ring) < 4:
            raise ValueError(
                "يجب أن تحتوي الحلقة على 4 نقاط على الأقل (بما في ذلك نقطة الإغلاق)"
            )

        # التحقق من أن المضلع مغلق
        if outer_ring[0] != outer_ring[-1]:
            raise ValueError("يجب أن يكون المضلع مغلقاً (النقطة الأولى = الأخيرة)")

        return v


# ============== Location Models ==============


class FieldLocation(BaseModel):
    """موقع الحقل"""

    region: str = Field(..., description="المنطقة/المحافظة")
    region_ar: str | None = Field(None, description="اسم المنطقة بالعربية")
    district: str | None = Field(None, description="المديرية")
    village: str | None = Field(None, description="القرية")
    coordinates: GeoPoint | None = Field(None, description="مركز الحقل")


# ============== Field Request Models ==============


class FieldCreate(BaseModel):
    """إنشاء حقل جديد"""

    tenant_id: str = Field(..., description="معرف المستأجر")
    user_id: str = Field(..., description="معرف المزارع")
    name: str = Field(..., min_length=1, max_length=200, description="اسم الحقل")
    name_en: str | None = Field(
        None, max_length=200, description="الاسم بالإنجليزية"
    )

    location: FieldLocation = Field(..., description="موقع الحقل")
    boundary: GeoPolygon | None = Field(None, description="حدود الحقل")
    area_hectares: float = Field(..., gt=0, description="المساحة بالهكتار")

    soil_type: SoilType | None = Field(SoilType.UNKNOWN, description="نوع التربة")
    irrigation_source: IrrigationSource | None = Field(
        IrrigationSource.NONE, description="مصدر الري"
    )

    current_crop: str | None = Field(None, description="المحصول الحالي")
    metadata: dict[str, Any] | None = Field(None, description="بيانات إضافية")


class FieldUpdate(BaseModel):
    """تحديث بيانات الحقل"""

    name: str | None = Field(None, min_length=1, max_length=200)
    name_en: str | None = Field(None, max_length=200)
    location: FieldLocation | None = None
    area_hectares: float | None = Field(None, gt=0)
    soil_type: SoilType | None = None
    irrigation_source: IrrigationSource | None = None
    status: FieldStatus | None = None
    metadata: dict[str, Any] | None = None


class BoundaryUpdate(BaseModel):
    """تحديث حدود الحقل"""

    boundary: GeoPolygon = Field(..., description="الحدود الجديدة")
    recalculate_area: bool = Field(True, description="إعادة حساب المساحة")


# ============== Crop Season Models ==============


class CropSeasonCreate(BaseModel):
    """إنشاء موسم محصول"""

    crop_type: str = Field(..., description="نوع المحصول")
    variety: str | None = Field(None, description="الصنف")
    planting_date: str = Field(..., description="تاريخ الزراعة")
    expected_harvest: str | None = Field(None, description="التاريخ المتوقع للحصاد")
    seed_source: str | None = Field(None, description="مصدر البذور")
    notes: str | None = Field(None, description="ملاحظات")


class CropSeasonClose(BaseModel):
    """إنهاء موسم المحصول"""

    harvest_date: str = Field(..., description="تاريخ الحصاد")
    actual_yield_kg: float | None = Field(
        None, ge=0, description="الإنتاج الفعلي بالكيلوغرام"
    )
    quality_grade: str | None = Field(None, description="درجة الجودة")
    notes: str | None = Field(None, description="ملاحظات")


class CropSeasonResponse(BaseModel):
    """استجابة موسم المحصول"""

    id: str
    field_id: str
    crop_type: str
    variety: str | None
    planting_date: str
    expected_harvest: str | None
    harvest_date: str | None
    status: CropSeasonStatus
    expected_yield_kg: float | None
    actual_yield_kg: float | None
    seed_source: str | None
    created_at: str


# ============== Zone Models ==============


class ZoneCreate(BaseModel):
    """إنشاء منطقة داخل الحقل"""

    name: str = Field(..., min_length=1, max_length=100)
    name_ar: str | None = Field(None, max_length=100)
    boundary: GeoPolygon = Field(..., description="حدود المنطقة")
    purpose: ZonePurpose = Field(..., description="غرض التقسيم")
    notes: str | None = None


class ZoneResponse(BaseModel):
    """استجابة المنطقة"""

    id: str
    field_id: str
    name: str
    name_ar: str | None
    boundary: dict[str, Any]
    area_hectares: float
    purpose: str
    created_at: str


# ============== NDVI History ==============


class NDVIRecord(BaseModel):
    """سجل NDVI"""

    date: str
    mean: float = Field(..., ge=-1, le=1)
    min: float = Field(..., ge=-1, le=1)
    max: float = Field(..., ge=-1, le=1)
    std: float | None = Field(None, ge=0)
    cloud_cover_pct: float | None = Field(None, ge=0, le=100)
    source: str | None = None


class NDVITrend(BaseModel):
    """اتجاه NDVI"""

    direction: str  # increasing, decreasing, stable
    change_percent: float
    period_days: int
    start_value: float
    end_value: float


# ============== Field Response Models ==============


class FieldResponse(BaseModel):
    """استجابة الحقل الأساسية"""

    id: str
    tenant_id: str
    user_id: str
    name: str
    name_en: str | None
    status: FieldStatus
    location: dict[str, Any]
    area_hectares: float
    soil_type: str | None
    irrigation_source: str | None
    current_crop: str | None
    created_at: str
    updated_at: str


class FieldDetailResponse(FieldResponse):
    """استجابة تفصيلية للحقل"""

    boundary: dict[str, Any] | None
    zones_count: int = 0
    seasons_count: int = 0
    latest_ndvi: NDVIRecord | None = None
    ndvi_trend: NDVITrend | None = None


class FieldStatsResponse(BaseModel):
    """إحصائيات الحقل"""

    field_id: str
    area_hectares: float
    seasons_count: int
    crops_grown: list[str]
    average_yield_kg_ha: float | None
    best_season: dict[str, Any] | None
    ndvi_stats: dict[str, float] | None


# ============== User Stats ==============


class UserFieldsStats(BaseModel):
    """إحصائيات حقول المستخدم"""

    user_id: str
    tenant_id: str
    fields_count: int
    total_area_hectares: float
    active_fields: int
    active_seasons: int
    crops_summary: dict[str, int]


# ============== Boundary Operations ==============


class OverlapCheckRequest(BaseModel):
    """طلب فحص التداخل"""

    boundary: GeoPolygon
    exclude_field_id: str | None = None


class OverlapCheckResponse(BaseModel):
    """نتيجة فحص التداخل"""

    has_overlap: bool
    overlapping_fields: list[dict[str, Any]]
    overlap_area_hectares: float


class AreaCalculationResponse(BaseModel):
    """نتيجة حساب المساحة"""

    field_id: str
    calculated_area_hectares: float
    stored_area_hectares: float
    difference_percent: float
    centroid: GeoPoint


# ============== Pagination ==============


class PaginatedResponse(BaseModel):
    """استجابة مُرقّمة"""

    items: list[Any]
    total: int
    skip: int
    limit: int
    has_more: bool
