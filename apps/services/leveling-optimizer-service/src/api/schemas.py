"""
Pydantic schemas for Leveling Optimizer Service.

نماذج البيانات لخدمة تحسين التسوية

Includes comprehensive validation for:
- Elevation points and ranges
- Grade/slope percentages
- Field boundaries and coordinates
- Field ID format
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# Validation constants
# ثوابت التحقق من الصحة
ELEVATION_MIN_M = -100.0  # Minimum elevation for agricultural fields
ELEVATION_MAX_M = 3000.0  # Maximum elevation for agricultural fields
MAX_GRADE_PERCENT = 15.0  # Maximum allowed grade percentage
MIN_GRADE_PERCENT = -15.0  # Minimum allowed grade percentage
MAX_ELEVATION_POINTS = 100000  # Maximum number of elevation points


class EquipmentType(StrEnum):
    """Equipment types for leveling operations. | أنواع معدات التسوية"""

    BULLDOZER = "bulldozer"  # جرافة
    SCRAPER = "scraper"  # كاشطة
    GRADER = "grader"  # ممهدة
    LASER_LEVELER = "laser_leveler"  # مسوي ليزر
    EXCAVATOR = "excavator"  # حفارة
    DUMP_TRUCK = "dump_truck"  # شاحنة قلابة


class SoilType(StrEnum):
    """Soil types for leveling calculations. | أنواع التربة لحسابات التسوية"""

    SANDY = "sandy"  # رملية
    LOAMY = "loamy"  # طفالية
    CLAY = "clay"  # طينية
    SILTY = "silty"  # طميية
    ROCKY = "rocky"  # صخرية


class LevelingMethod(StrEnum):
    """Leveling methods. | طرق التسوية"""

    SINGLE_PLANE = "single_plane"  # مستوى واحد
    DUAL_PLANE = "dual_plane"  # مستويين
    CONTOUR = "contour"  # كنتوري
    BENCH = "bench"  # مصاطب


class LevelingPriority(StrEnum):
    """Leveling optimization priority. | أولوية تحسين التسوية"""

    MINIMIZE_COST = "minimize_cost"  # تقليل التكلفة
    MINIMIZE_EARTHWORK = "minimize_earthwork"  # تقليل الحفر والردم
    OPTIMAL_DRAINAGE = "optimal_drainage"  # تصريف مثالي
    IRRIGATION_EFFICIENCY = "irrigation_efficiency"  # كفاءة الري


# Request Models


class ElevationPoint(BaseModel):
    """Single elevation point. | نقطة ارتفاع واحدة"""

    x: float = Field(..., description="X coordinate (meters) | الإحداثي السيني (متر)")
    y: float = Field(..., description="Y coordinate (meters) | الإحداثي الصادي (متر)")
    elevation: float = Field(
        ...,
        ge=ELEVATION_MIN_M,
        le=ELEVATION_MAX_M,
        description="Elevation (meters) | الارتفاع (متر)",
    )
    point_id: str | None = Field(None, max_length=64, description="Point identifier | معرف النقطة")

    @field_validator("elevation")
    @classmethod
    def validate_elevation(cls, v: float) -> float:
        """Validate elevation is within reasonable bounds for agricultural fields."""
        if not ELEVATION_MIN_M <= v <= ELEVATION_MAX_M:
            raise ValueError(
                f"Elevation {v}m must be between {ELEVATION_MIN_M}m and {ELEVATION_MAX_M}m | "
                f"الارتفاع {v}م يجب أن يكون بين {ELEVATION_MIN_M}م و {ELEVATION_MAX_M}م"
            )
        return v

    @field_validator("point_id")
    @classmethod
    def validate_point_id(cls, v: str | None) -> str | None:
        """Validate point ID format if provided."""
        if v is not None:
            # Strip whitespace and validate length
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 64:
                raise ValueError("Point ID must be 64 characters or less | معرف النقطة يجب أن يكون 64 حرفاً أو أقل")
        return v


class FieldBoundary(BaseModel):
    """Field boundary polygon. | حدود الحقل"""

    coordinates: list[list[float]] = Field(
        ...,
        min_length=3,
        description="List of [x, y] coordinates forming boundary | قائمة إحداثيات الحدود",
    )

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: list[list[float]]) -> list[list[float]]:
        """Validate boundary coordinates."""
        if len(v) < 3:
            raise ValueError(
                "Boundary must have at least 3 coordinate pairs | يجب أن تحتوي الحدود على 3 أزواج إحداثيات على الأقل"
            )

        for i, coord in enumerate(v):
            if not isinstance(coord, (list, tuple)) or len(coord) < 2:
                raise ValueError(
                    f"Coordinate at index {i} must be [x, y] array | الإحداثية في الفهرس {i} يجب أن تكون مصفوفة [س، ص]"
                )
            try:
                float(coord[0])
                float(coord[1])
            except (TypeError, ValueError) as e:
                raise ValueError(
                    f"Coordinate at index {i} contains non-numeric values | "
                    f"الإحداثية في الفهرس {i} تحتوي على قيم غير رقمية"
                ) from e

        return v


class LevelingAnalysisRequest(BaseModel):
    """Request for field leveling analysis. | طلب تحليل تسوية الحقل"""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    elevation_points: list[ElevationPoint] = Field(
        ...,
        description="Survey elevation points | نقاط المسح الطبوغرافي",
        min_length=4,
        max_length=MAX_ELEVATION_POINTS,
    )
    boundary: FieldBoundary | None = Field(None, description="Field boundary polygon | حدود الحقل")
    soil_type: SoilType = Field(SoilType.LOAMY, description="Soil type | نوع التربة")
    target_grade_x: float | None = Field(
        None,
        ge=MIN_GRADE_PERCENT,
        le=MAX_GRADE_PERCENT,
        description="Target grade in X direction (%) | الميل المستهدف بالاتجاه السيني (%)",
    )
    target_grade_y: float | None = Field(
        None,
        ge=MIN_GRADE_PERCENT,
        le=MAX_GRADE_PERCENT,
        description="Target grade in Y direction (%) | الميل المستهدف بالاتجاه الصادي (%)",
    )
    method: LevelingMethod = Field(LevelingMethod.SINGLE_PLANE, description="Leveling method | طريقة التسوية")
    priority: LevelingPriority = Field(
        LevelingPriority.MINIMIZE_COST, description="Optimization priority | أولوية التحسين"
    )
    include_cost_estimate: bool = Field(True, description="Include cost estimate | تضمين تقدير التكلفة")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        if len(v) > 64:
            raise ValueError("Field ID must be 64 characters or less | معرف الحقل يجب أن يكون 64 حرفاً أو أقل")
        return v

    @field_validator("target_grade_x", "target_grade_y")
    @classmethod
    def validate_grade(cls, v: float | None) -> float | None:
        """Validate grade percentage is within reasonable bounds."""
        if v is not None and not MIN_GRADE_PERCENT <= v <= MAX_GRADE_PERCENT:
            raise ValueError(
                f"Grade {v}% must be between {MIN_GRADE_PERCENT}% and {MAX_GRADE_PERCENT}% | "
                f"الميل {v}% يجب أن يكون بين {MIN_GRADE_PERCENT}% و {MAX_GRADE_PERCENT}%"
            )
        return v

    @field_validator("elevation_points")
    @classmethod
    def validate_elevation_points_count(cls, v: list[ElevationPoint]) -> list[ElevationPoint]:
        """Validate elevation points count."""
        if len(v) < 4:
            raise ValueError(
                "At least 4 elevation points required for leveling analysis | "
                "مطلوب 4 نقاط ارتفاع على الأقل لتحليل التسوية"
            )
        if len(v) > MAX_ELEVATION_POINTS:
            raise ValueError(
                f"Maximum {MAX_ELEVATION_POINTS} elevation points allowed | "
                f"الحد الأقصى {MAX_ELEVATION_POINTS} نقطة ارتفاع مسموح بها"
            )
        return v


class SimulationRequest(BaseModel):
    """Request for leveling simulation. | طلب محاكاة التسوية"""

    field_id: str = Field(..., min_length=1, max_length=64, description="Field identifier | معرف الحقل")
    elevation_points: list[ElevationPoint] = Field(
        ...,
        description="Survey elevation points | نقاط المسح الطبوغرافي",
        min_length=4,
        max_length=MAX_ELEVATION_POINTS,
    )
    target_elevation: float | None = Field(
        None,
        ge=ELEVATION_MIN_M,
        le=ELEVATION_MAX_M,
        description="Target design elevation (meters) | الارتفاع التصميمي المستهدف (متر)",
    )
    target_grade_x: float = Field(
        0.2,
        ge=MIN_GRADE_PERCENT,
        le=MAX_GRADE_PERCENT,
        description="Target grade in X direction (%) | الميل المستهدف بالاتجاه السيني (%)",
    )
    target_grade_y: float = Field(
        0.1,
        ge=MIN_GRADE_PERCENT,
        le=MAX_GRADE_PERCENT,
        description="Target grade in Y direction (%) | الميل المستهدف بالاتجاه الصادي (%)",
    )
    soil_type: SoilType = Field(SoilType.LOAMY, description="Soil type | نوع التربة")
    method: LevelingMethod = Field(LevelingMethod.SINGLE_PLANE, description="Leveling method | طريقة التسوية")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, v: str) -> str:
        """Validate field ID format."""
        v = v.strip()
        if not v:
            raise ValueError("Field ID cannot be empty | معرف الحقل لا يمكن أن يكون فارغاً")
        return v

    @field_validator("target_grade_x", "target_grade_y")
    @classmethod
    def validate_grade(cls, v: float) -> float:
        """Validate grade percentage is within reasonable bounds."""
        if not MIN_GRADE_PERCENT <= v <= MAX_GRADE_PERCENT:
            raise ValueError(
                f"Grade {v}% must be between {MIN_GRADE_PERCENT}% and {MAX_GRADE_PERCENT}% | "
                f"الميل {v}% يجب أن يكون بين {MIN_GRADE_PERCENT}% و {MAX_GRADE_PERCENT}%"
            )
        return v

    @field_validator("target_elevation")
    @classmethod
    def validate_target_elevation(cls, v: float | None) -> float | None:
        """Validate target elevation is within reasonable bounds."""
        if v is not None and not ELEVATION_MIN_M <= v <= ELEVATION_MAX_M:
            raise ValueError(
                f"Target elevation {v}m must be between {ELEVATION_MIN_M}m and {ELEVATION_MAX_M}m | "
                f"الارتفاع المستهدف {v}م يجب أن يكون بين {ELEVATION_MIN_M}م و {ELEVATION_MAX_M}م"
            )
        return v


# Response Models


class CutFillVolume(BaseModel):
    """Cut and fill volume calculations. | حسابات أحجام القطع والردم"""

    cut_volume_m3: float = Field(..., description="Volume to cut (m³) | حجم القطع (م³)")
    fill_volume_m3: float = Field(..., description="Volume to fill (m³) | حجم الردم (م³)")
    net_volume_m3: float = Field(..., description="Net volume (cut - fill) (m³) | الحجم الصافي (القطع - الردم) (م³)")
    cut_area_m2: float = Field(..., description="Area requiring cut (m²) | مساحة القطع (م²)")
    fill_area_m2: float = Field(..., description="Area requiring fill (m²) | مساحة الردم (م²)")
    balance_ratio: float = Field(..., description="Cut/Fill balance ratio | نسبة توازن القطع/الردم")
    max_cut_depth_m: float = Field(..., description="Maximum cut depth (m) | أقصى عمق قطع (م)")
    max_fill_depth_m: float = Field(..., description="Maximum fill depth (m) | أقصى عمق ردم (م)")
    avg_cut_depth_m: float = Field(..., description="Average cut depth (m) | متوسط عمق القطع (م)")
    avg_fill_depth_m: float = Field(..., description="Average fill depth (m) | متوسط عمق الردم (م)")


class DesignPlane(BaseModel):
    """Design plane parameters. | معلمات مستوى التصميم"""

    centroid_elevation: float = Field(..., description="Elevation at centroid (m) | الارتفاع عند مركز الثقل (م)")
    grade_x_percent: float = Field(..., description="Grade in X direction (%) | الميل بالاتجاه السيني (%)")
    grade_y_percent: float = Field(..., description="Grade in Y direction (%) | الميل بالاتجاه الصادي (%)")
    plane_equation: str = Field(..., description="Plane equation: z = a*x + b*y + c | معادلة المستوى")
    coefficient_a: float = Field(..., description="Coefficient a (grade X)")
    coefficient_b: float = Field(..., description="Coefficient b (grade Y)")
    coefficient_c: float = Field(..., description="Coefficient c (elevation offset)")


class CostEstimate(BaseModel):
    """Detailed cost estimation in SAR. | تقدير التكلفة المفصل بالريال السعودي"""

    total_cost_sar: float = Field(..., description="Total estimated cost (SAR) | إجمالي التكلفة المقدرة (ريال)")
    earthwork_cost_sar: float = Field(..., description="Earthwork cost (SAR) | تكلفة الحفريات (ريال)")
    equipment_cost_sar: float = Field(..., description="Equipment rental cost (SAR) | تكلفة استئجار المعدات (ريال)")
    labor_cost_sar: float = Field(..., description="Labor cost (SAR) | تكلفة العمالة (ريال)")
    fuel_cost_sar: float = Field(..., description="Fuel cost (SAR) | تكلفة الوقود (ريال)")
    surveying_cost_sar: float = Field(..., description="Surveying cost (SAR) | تكلفة المسح (ريال)")
    contingency_sar: float = Field(..., description="Contingency (10%) (SAR) | احتياطي (10%) (ريال)")
    cost_per_m3_sar: float = Field(..., description="Cost per cubic meter (SAR/m³) | التكلفة للمتر المكعب (ريال/م³)")
    cost_per_hectare_sar: float = Field(..., description="Cost per hectare (SAR/ha) | التكلفة للهكتار (ريال/هـ)")
    estimated_duration_hours: float = Field(..., description="Estimated duration (hours) | المدة المقدرة (ساعات)")
    estimated_duration_days: float = Field(
        ..., description="Estimated duration (8-hour days) | المدة المقدرة (أيام عمل)"
    )

    # Bilingual summary
    summary_en: str = Field(..., description="Cost summary in English")
    summary_ar: str = Field(..., description="ملخص التكلفة بالعربية")


class EquipmentRecommendation(BaseModel):
    """Equipment recommendation for leveling. | توصية المعدات للتسوية"""

    equipment_type: EquipmentType = Field(..., description="Equipment type | نوع المعدات")
    equipment_name_en: str = Field(..., description="Equipment name (English)")
    equipment_name_ar: str = Field(..., description="اسم المعدات (عربي)")
    quantity: int = Field(..., description="Recommended quantity | الكمية الموصى بها")
    hours_required: float = Field(..., description="Hours required | الساعات المطلوبة")
    cost_per_hour_sar: float = Field(..., description="Cost per hour (SAR) | التكلفة بالساعة (ريال)")
    total_cost_sar: float = Field(..., description="Total cost (SAR) | إجمالي التكلفة (ريال)")
    productivity_m3_per_hour: float = Field(..., description="Productivity (m³/hour) | الإنتاجية (م³/ساعة)")
    recommended_for: str = Field(..., description="Recommended use case | الاستخدام الموصى به")
    priority: int = Field(..., description="Priority rank (1 = highest) | ترتيب الأولوية")


class LevelingPlan(BaseModel):
    """Comprehensive leveling plan. | خطة التسوية الشاملة"""

    plan_id: str = Field(..., description="Plan identifier | معرف الخطة")
    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp | وقت الإنشاء")

    # Design parameters
    design_plane: DesignPlane = Field(..., description="Design plane parameters | معلمات مستوى التصميم")
    method: LevelingMethod = Field(..., description="Leveling method | طريقة التسوية")

    # Volumes
    cut_fill: CutFillVolume = Field(..., description="Cut and fill volumes | أحجام القطع والردم")

    # Field statistics
    field_area_m2: float = Field(..., description="Field area (m²) | مساحة الحقل (م²)")
    field_area_hectares: float = Field(..., description="Field area (hectares) | مساحة الحقل (هكتار)")
    original_elevation_range: float = Field(..., description="Original elevation range (m) | نطاق الارتفاع الأصلي (م)")
    leveled_elevation_range: float = Field(
        ..., description="Leveled elevation range (m) | نطاق الارتفاع بعد التسوية (م)"
    )

    # Haul analysis
    avg_haul_distance_m: float = Field(..., description="Average haul distance (m) | متوسط مسافة النقل (م)")

    # Recommendations
    equipment_recommendations: list[EquipmentRecommendation] = Field(
        default_factory=list, description="Equipment recommendations | توصيات المعدات"
    )

    # Cost estimate
    cost_estimate: CostEstimate | None = Field(None, description="Cost estimate | تقدير التكلفة")

    # Bilingual summaries
    summary_en: str = Field(..., description="Plan summary in English")
    summary_ar: str = Field(..., description="ملخص الخطة بالعربية")
    recommendations_en: list[str] = Field(default_factory=list, description="Recommendations in English")
    recommendations_ar: list[str] = Field(default_factory=list, description="التوصيات بالعربية")


class LevelingAnalysisResponse(BaseModel):
    """Response from leveling analysis. | استجابة تحليل التسوية"""

    success: bool = Field(..., description="Analysis success | نجاح التحليل")
    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Analysis timestamp | وقت التحليل"
    )
    plan: LevelingPlan = Field(..., description="Leveling plan | خطة التسوية")
    message_en: str = Field(..., description="Status message (English)")
    message_ar: str = Field(..., description="رسالة الحالة (عربي)")


class SimulationResult(BaseModel):
    """Leveling simulation result. | نتيجة محاكاة التسوية"""

    field_id: str = Field(..., description="Field identifier | معرف الحقل")
    simulation_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Simulation timestamp | وقت المحاكاة"
    )

    # Original vs Simulated
    original_points: list[ElevationPoint] = Field(..., description="Original elevation points | نقاط الارتفاع الأصلية")
    simulated_points: list[ElevationPoint] = Field(
        ..., description="Simulated leveled points | نقاط المحاكاة بعد التسوية"
    )
    cut_points: list[ElevationPoint] = Field(..., description="Points requiring cut | نقاط تحتاج قطع")
    fill_points: list[ElevationPoint] = Field(..., description="Points requiring fill | نقاط تحتاج ردم")

    # Design plane
    design_plane: DesignPlane = Field(..., description="Applied design plane | مستوى التصميم المطبق")

    # Volumes
    cut_fill: CutFillVolume = Field(..., description="Cut and fill volumes | أحجام القطع والردم")

    # Statistics
    original_std_dev: float = Field(..., description="Original elevation std dev (m) | الانحراف المعياري الأصلي (م)")
    simulated_std_dev: float = Field(
        ..., description="Simulated elevation std dev (m) | الانحراف المعياري بعد المحاكاة (م)"
    )
    uniformity_improvement: float = Field(..., description="Uniformity improvement (%) | تحسن التجانس (%)")

    # Bilingual summary
    summary_en: str = Field(..., description="Simulation summary (English)")
    summary_ar: str = Field(..., description="ملخص المحاكاة (عربي)")


class HealthResponse(BaseModel):
    """Health check response. | استجابة فحص الصحة"""

    status: str = Field(..., description="Service status | حالة الخدمة")
    service: str = Field(..., description="Service name | اسم الخدمة")
    version: str = Field(..., description="Service version | إصدار الخدمة")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp | وقت الفحص")


class ReadinessResponse(BaseModel):
    """Readiness check response. | استجابة فحص الجاهزية"""

    status: str = Field(..., description="Readiness status | حالة الجاهزية")
    database: bool = Field(..., description="Database connected | الاتصال بقاعدة البيانات")
    nats: bool = Field(..., description="NATS connected | الاتصال بـ NATS")
    checks: dict[str, bool] = Field(default_factory=dict, description="Additional checks | فحوصات إضافية")


class ErrorResponse(BaseModel):
    """Error response model. | نموذج استجابة الخطأ"""

    error: str = Field(..., description="Error message | رسالة الخطأ")
    error_ar: str = Field(..., description="رسالة الخطأ (عربي)")
    detail: str | None = Field(None, description="Error details | تفاصيل الخطأ")
    request_id: str | None = Field(None, description="Request ID | معرف الطلب")
