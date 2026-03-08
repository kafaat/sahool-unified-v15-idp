"""
Crop Rotation Planning Models - نماذج تخطيط الدورة الزراعية

Data models for crop rotation planning, soil health tracking,
pest/disease management, and multi-year planning.

Supports common Middle East crops including:
- Wheat (قمح)
- Barley (شعير)
- Alfalfa (برسيم)
- Vegetables (خضروات)
- Date Palm (نخيل)
- Sorghum (ذرة رفيعة)
- Maize (ذرة)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

# =============================================================================
# Enums - التعدادات
# =============================================================================


class CropFamily(StrEnum):
    """Botanical crop families for rotation planning"""

    POACEAE = "poaceae"  # النجيليات (Grasses: wheat, barley, rice, maize)
    FABACEAE = "fabaceae"  # البقوليات (Legumes: alfalfa, clover, beans)
    SOLANACEAE = "solanaceae"  # الباذنجانيات (Nightshades: tomato, pepper, eggplant)
    CUCURBITACEAE = "cucurbitaceae"  # القرعيات (Cucurbits: melon, cucumber, squash)
    BRASSICACEAE = "brassicaceae"  # الصليبيات (Brassicas: cabbage, cauliflower)
    APIACEAE = "apiaceae"  # الخيميات (Umbellifers: carrot, celery)
    LILIACEAE = "liliaceae"  # الزنبقيات (Alliums: onion, garlic)
    CHENOPODIACEAE = "chenopodiaceae"  # الرمراميات (Goosefoots: spinach, beet)
    ARECACEAE = "arecaceae"  # النخيليات (Palms: date palm)
    MALVACEAE = "malvaceae"  # الخبازيات (Mallows: cotton, okra)
    OTHER = "other"  # أخرى


class CropType(StrEnum):
    """Common crop types in Middle East agriculture"""

    # Cereals - الحبوب
    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    RICE = "rice"  # أرز
    MAIZE = "maize"  # ذرة
    SORGHUM = "sorghum"  # ذرة رفيعة
    MILLET = "millet"  # دخن

    # Legumes - البقوليات
    ALFALFA = "alfalfa"  # برسيم
    CLOVER = "clover"  # برسيم حجازي
    FABA_BEAN = "faba_bean"  # فول
    CHICKPEA = "chickpea"  # حمص
    LENTIL = "lentil"  # عدس
    COWPEA = "cowpea"  # لوبيا

    # Vegetables - الخضروات
    TOMATO = "tomato"  # طماطم
    POTATO = "potato"  # بطاطس
    ONION = "onion"  # بصل
    GARLIC = "garlic"  # ثوم
    PEPPER = "pepper"  # فلفل
    EGGPLANT = "eggplant"  # باذنجان
    CUCUMBER = "cucumber"  # خيار
    MELON = "melon"  # بطيخ أصفر
    WATERMELON = "watermelon"  # بطيخ أحمر
    SQUASH = "squash"  # كوسة
    CARROT = "carrot"  # جزر
    CABBAGE = "cabbage"  # ملفوف
    LETTUCE = "lettuce"  # خس
    SPINACH = "spinach"  # سبانخ

    # Fruits - الفواكه
    DATE_PALM = "date_palm"  # نخيل
    CITRUS = "citrus"  # حمضيات
    GRAPE = "grape"  # عنب
    OLIVE = "olive"  # زيتون

    # Industrial - المحاصيل الصناعية
    COTTON = "cotton"  # قطن
    SUNFLOWER = "sunflower"  # عباد الشمس
    SESAME = "sesame"  # سمسم

    # Fodder - محاصيل العلف
    RHODES_GRASS = "rhodes_grass"  # حشيشة رودس
    SUDAN_GRASS = "sudan_grass"  # حشيشة السودان

    # Fallow/Cover - البور/الغطاء
    FALLOW = "fallow"  # أرض بور
    GREEN_MANURE = "green_manure"  # سماد أخضر


class Season(StrEnum):
    """Growing seasons in Middle East"""

    WINTER = "winter"  # شتوي (Oct-Apr)
    SUMMER = "summer"  # صيفي (Apr-Oct)
    SPRING = "spring"  # ربيعي
    FALL = "fall"  # خريفي
    YEAR_ROUND = "year_round"  # طوال العام
    PERENNIAL = "perennial"  # معمر


class RotationBenefit(StrEnum):
    """Benefits of crop rotation"""

    NITROGEN_FIXATION = "nitrogen_fixation"  # تثبيت النيتروجين
    PEST_BREAK = "pest_break"  # كسر دورة الآفات
    DISEASE_BREAK = "disease_break"  # كسر دورة الأمراض
    WEED_SUPPRESSION = "weed_suppression"  # مكافحة الأعشاب
    SOIL_STRUCTURE = "soil_structure"  # تحسين بنية التربة
    ORGANIC_MATTER = "organic_matter"  # زيادة المادة العضوية
    NUTRIENT_CYCLING = "nutrient_cycling"  # دورة المغذيات
    EROSION_CONTROL = "erosion_control"  # مكافحة التعرية
    WATER_EFFICIENCY = "water_efficiency"  # كفاءة استخدام المياه
    BIODIVERSITY = "biodiversity"  # التنوع الحيوي


class SoilHealthIndicator(StrEnum):
    """Soil health indicators"""

    ORGANIC_MATTER = "organic_matter"  # المادة العضوية
    NITROGEN = "nitrogen"  # النيتروجين
    PHOSPHORUS = "phosphorus"  # الفسفور
    POTASSIUM = "potassium"  # البوتاسيوم
    PH = "ph"  # درجة الحموضة
    EC = "ec"  # الموصلية الكهربائية
    SOIL_STRUCTURE = "soil_structure"  # بنية التربة
    MICROBIAL_ACTIVITY = "microbial_activity"  # النشاط الميكروبي
    WATER_RETENTION = "water_retention"  # احتباس الماء
    COMPACTION = "compaction"  # الانضغاط


class RecommendationPriority(StrEnum):
    """Priority level for recommendations"""

    CRITICAL = "critical"  # حرج
    HIGH = "high"  # عالي
    MEDIUM = "medium"  # متوسط
    LOW = "low"  # منخفض
    OPTIONAL = "optional"  # اختياري


class PlanStatus(StrEnum):
    """Status of rotation plan"""

    DRAFT = "draft"  # مسودة
    ACTIVE = "active"  # نشط
    COMPLETED = "completed"  # مكتمل
    CANCELLED = "cancelled"  # ملغي
    ARCHIVED = "archived"  # مؤرشف


# =============================================================================
# Crop Information - معلومات المحاصيل
# =============================================================================


@dataclass
class CropCharacteristics:
    """
    Agronomic characteristics of a crop
    الخصائص الزراعية للمحصول
    """

    crop_type: CropType
    crop_family: CropFamily

    # Names
    name_en: str
    name_ar: str

    # Growing requirements
    growing_season: Season

    # Optional fields with defaults
    scientific_name: str = ""
    growing_days_min: int = 90
    growing_days_max: int = 150
    optimal_temp_min_c: float = 15.0
    optimal_temp_max_c: float = 30.0

    # Water requirements (mm/season)
    water_requirement_mm: float = 400.0
    drought_tolerance: float = 0.5  # 0-1 scale

    # Soil preferences
    preferred_ph_min: float = 6.0
    preferred_ph_max: float = 7.5
    salt_tolerance: float = 0.5  # 0-1 scale (1 = highly tolerant)

    # Nutrient characteristics
    is_nitrogen_fixer: bool = False
    nitrogen_demand: float = 0.5  # 0-1 scale (relative)
    phosphorus_demand: float = 0.5
    potassium_demand: float = 0.5
    residue_nitrogen_kg_ha: float = 0.0  # N contribution to next crop

    # Root characteristics
    root_depth_cm: float = 60.0
    root_type: str = "fibrous"  # fibrous, taproot, shallow

    # Rotation considerations
    min_rotation_years: int = 1  # Years before replanting same family
    break_crop_for: list[str] = field(default_factory=list)  # Crops it helps

    # Common pests/diseases (for rotation planning)
    major_pests: list[str] = field(default_factory=list)
    major_diseases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "crop_type": self.crop_type.value,
            "crop_family": self.crop_family.value,
            "name_en": self.name_en,
            "name_ar": self.name_ar,
            "scientific_name": self.scientific_name,
            "growing_season": self.growing_season.value,
            "growing_days": {
                "min": self.growing_days_min,
                "max": self.growing_days_max,
            },
            "water_requirement_mm": self.water_requirement_mm,
            "is_nitrogen_fixer": self.is_nitrogen_fixer,
            "min_rotation_years": self.min_rotation_years,
        }


# =============================================================================
# Rotation Planning - تخطيط الدورة الزراعية
# =============================================================================


@dataclass
class RotationSlot:
    """
    Single slot in a rotation sequence
    خانة واحدة في تسلسل الدورة الزراعية
    """

    slot_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Crop assignment
    crop_type: CropType | None = None
    crop_variety: str | None = None

    # Timing
    season: Season = Season.WINTER
    year: int = 1  # Year in rotation cycle (1, 2, 3, ...)
    planned_planting_date: date | None = None
    planned_harvest_date: date | None = None

    # Area
    area_ha: float | None = None

    # Expected outcomes
    expected_yield_tons_ha: float | None = None
    expected_nitrogen_contribution_kg_ha: float = 0.0

    # Benefits provided
    rotation_benefits: list[RotationBenefit] = field(default_factory=list)

    # Status
    is_completed: bool = False
    actual_planting_date: date | None = None
    actual_harvest_date: date | None = None
    actual_yield_tons_ha: float | None = None

    # Notes
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "slot_id": self.slot_id,
            "crop_type": self.crop_type.value if self.crop_type else None,
            "crop_variety": self.crop_variety,
            "season": self.season.value,
            "year": self.year,
            "planned_planting_date": self.planned_planting_date.isoformat() if self.planned_planting_date else None,
            "planned_harvest_date": self.planned_harvest_date.isoformat() if self.planned_harvest_date else None,
            "area_ha": self.area_ha,
            "expected_yield_tons_ha": self.expected_yield_tons_ha,
            "expected_nitrogen_contribution_kg_ha": self.expected_nitrogen_contribution_kg_ha,
            "rotation_benefits": [b.value for b in self.rotation_benefits],
            "is_completed": self.is_completed,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


@dataclass
class RotationSequence:
    """
    Multi-year crop rotation sequence
    تسلسل الدورة الزراعية متعدد السنوات
    """

    sequence_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Identification
    name: str = ""
    name_ar: str = ""
    description: str = ""
    description_ar: str = ""

    # Duration
    cycle_years: int = 3  # Length of rotation cycle
    start_year: int = 2026

    # Slots
    slots: list[RotationSlot] = field(default_factory=list)

    # Target benefits
    target_benefits: list[RotationBenefit] = field(default_factory=list)

    # Agronomic context
    soil_type: str = "loamy"
    irrigation_type: str = "drip"
    climate_zone: str = "arid"

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""

    def get_slots_for_year(self, year: int) -> list[RotationSlot]:
        """Get all slots for a specific year"""
        return [s for s in self.slots if s.year == year]

    def get_crop_sequence(self) -> list[CropType | None]:
        """Get ordered list of crops in sequence"""
        sorted_slots = sorted(self.slots, key=lambda s: (s.year, s.season.value))
        return [s.crop_type for s in sorted_slots]

    def calculate_nitrogen_balance(self) -> float:
        """Calculate net nitrogen contribution of sequence"""
        return sum(s.expected_nitrogen_contribution_kg_ha for s in self.slots)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "sequence_id": self.sequence_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "cycle_years": self.cycle_years,
            "start_year": self.start_year,
            "slots": [s.to_dict() for s in self.slots],
            "target_benefits": [b.value for b in self.target_benefits],
            "soil_type": self.soil_type,
            "irrigation_type": self.irrigation_type,
            "nitrogen_balance_kg_ha": self.calculate_nitrogen_balance(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RotationPlan:
    """
    Complete rotation plan for a field
    خطة الدورة الزراعية الكاملة للحقل
    """

    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Identification
    tenant_id: str = ""
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str = ""

    # Plan details
    name: str = ""
    name_ar: str = ""
    description: str = ""
    description_ar: str = ""

    # Area
    total_area_ha: float = 0.0

    # Time frame
    start_date: date | None = None
    end_date: date | None = None
    planning_horizon_years: int = 5

    # Rotation sequence
    sequence: RotationSequence | None = None

    # Status
    status: PlanStatus = PlanStatus.DRAFT

    # Goals
    primary_goals: list[str] = field(default_factory=list)
    primary_goals_ar: list[str] = field(default_factory=list)

    # Constraints
    constraints: list[str] = field(default_factory=list)  # e.g., "no cotton", "water limited"
    constraints_ar: list[str] = field(default_factory=list)

    # Economic projections
    projected_total_revenue: float | None = None
    projected_total_cost: float | None = None
    projected_profit_per_ha: float | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    approved_by: str | None = None
    approved_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plan_id": self.plan_id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "total_area_ha": self.total_area_ha,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "planning_horizon_years": self.planning_horizon_years,
            "sequence": self.sequence.to_dict() if self.sequence else None,
            "status": self.status.value,
            "primary_goals": self.primary_goals,
            "primary_goals_ar": self.primary_goals_ar,
            "projected_profit_per_ha": self.projected_profit_per_ha,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Pest and Disease Management - إدارة الآفات والأمراض
# =============================================================================


@dataclass
class PestDiseaseRisk:
    """
    Pest or disease risk assessment for rotation planning
    تقييم مخاطر الآفات أو الأمراض لتخطيط الدورة
    """

    risk_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Identification
    name_en: str = ""
    name_ar: str = ""
    scientific_name: str = ""

    # Type
    is_pest: bool = True  # False if disease
    pest_type: str = ""  # insect, nematode, mite, etc.
    disease_type: str = ""  # fungal, bacterial, viral, etc.

    # Host crops
    host_crops: list[CropType] = field(default_factory=list)
    primary_host: CropType | None = None

    # Survival and lifecycle
    soil_persistence_years: int = 1  # Years pathogen survives in soil
    requires_host_crop: bool = True
    overwinters_in_residue: bool = False

    # Break crops (non-hosts that reduce pressure)
    break_crops: list[CropType] = field(default_factory=list)
    recommended_break_years: int = 2

    # Impact
    yield_loss_potential_percent: float = 0.0  # Maximum yield loss if untreated
    economic_impact_level: str = "medium"  # low, medium, high, severe

    # Risk factors
    risk_factors: list[str] = field(default_factory=list)
    risk_factors_ar: list[str] = field(default_factory=list)

    # Control recommendations
    cultural_controls: list[str] = field(default_factory=list)
    cultural_controls_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "risk_id": self.risk_id,
            "name_en": self.name_en,
            "name_ar": self.name_ar,
            "scientific_name": self.scientific_name,
            "is_pest": self.is_pest,
            "pest_type": self.pest_type,
            "disease_type": self.disease_type,
            "host_crops": [c.value for c in self.host_crops],
            "primary_host": self.primary_host.value if self.primary_host else None,
            "soil_persistence_years": self.soil_persistence_years,
            "break_crops": [c.value for c in self.break_crops],
            "recommended_break_years": self.recommended_break_years,
            "yield_loss_potential_percent": self.yield_loss_potential_percent,
        }


@dataclass
class PestBreakRecommendation:
    """
    Recommendation for pest/disease break through rotation
    توصية لكسر دورة الآفات/الأمراض من خلال الدورة الزراعية
    """

    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context
    field_id: str = ""
    current_crop: CropType | None = None
    pest_disease_risks: list[PestDiseaseRisk] = field(default_factory=list)

    # Recommendation
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    recommended_break_crops: list[CropType] = field(default_factory=list)
    minimum_break_years: int = 2

    # Reasoning
    reasoning_en: str = ""
    reasoning_ar: str = ""

    # Expected outcomes
    expected_risk_reduction_percent: float = 0.0
    expected_yield_improvement_percent: float = 0.0

    # Warnings
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "recommendation_id": self.recommendation_id,
            "field_id": self.field_id,
            "current_crop": self.current_crop.value if self.current_crop else None,
            "priority": self.priority.value,
            "recommended_break_crops": [c.value for c in self.recommended_break_crops],
            "minimum_break_years": self.minimum_break_years,
            "reasoning_en": self.reasoning_en,
            "reasoning_ar": self.reasoning_ar,
            "expected_risk_reduction_percent": self.expected_risk_reduction_percent,
            "expected_yield_improvement_percent": self.expected_yield_improvement_percent,
            "warnings_en": self.warnings_en,
            "warnings_ar": self.warnings_ar,
            "generated_at": self.generated_at.isoformat(),
        }


# =============================================================================
# Soil Health - صحة التربة
# =============================================================================


@dataclass
class SoilHealthMeasurement:
    """
    Single soil health measurement
    قياس واحد لصحة التربة
    """

    measurement_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Location
    field_id: str = ""
    sample_location: str = ""  # GPS or description
    sample_depth_cm: float = 30.0

    # Timestamp
    measurement_date: date = field(default_factory=date.today)

    # Physical properties
    organic_matter_percent: float | None = None
    bulk_density_g_cm3: float | None = None
    porosity_percent: float | None = None
    water_holding_capacity_mm_m: float | None = None
    infiltration_rate_mm_hr: float | None = None

    # Chemical properties
    ph: float | None = None
    ec_ds_m: float | None = None  # Electrical conductivity
    cec_meq_100g: float | None = None  # Cation exchange capacity

    # Nutrients (ppm or kg/ha)
    nitrogen_total_ppm: float | None = None
    nitrogen_available_kg_ha: float | None = None
    phosphorus_ppm: float | None = None
    potassium_ppm: float | None = None
    calcium_ppm: float | None = None
    magnesium_ppm: float | None = None
    sulfur_ppm: float | None = None

    # Micronutrients
    iron_ppm: float | None = None
    zinc_ppm: float | None = None
    manganese_ppm: float | None = None
    boron_ppm: float | None = None

    # Biological indicators
    microbial_biomass_mg_kg: float | None = None
    respiration_rate_mg_co2_kg_day: float | None = None
    earthworm_count_per_m2: int | None = None

    # Calculated scores (0-100)
    overall_health_score: float | None = None
    fertility_score: float | None = None
    structure_score: float | None = None
    biological_score: float | None = None

    # Lab info
    lab_name: str | None = None
    lab_reference: str | None = None

    # Notes
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "measurement_id": self.measurement_id,
            "field_id": self.field_id,
            "measurement_date": self.measurement_date.isoformat(),
            "sample_depth_cm": self.sample_depth_cm,
            "organic_matter_percent": self.organic_matter_percent,
            "ph": self.ph,
            "ec_ds_m": self.ec_ds_m,
            "nitrogen_available_kg_ha": self.nitrogen_available_kg_ha,
            "phosphorus_ppm": self.phosphorus_ppm,
            "potassium_ppm": self.potassium_ppm,
            "overall_health_score": self.overall_health_score,
            "fertility_score": self.fertility_score,
            "structure_score": self.structure_score,
            "biological_score": self.biological_score,
        }


@dataclass
class SoilHealthTrend:
    """
    Soil health trend over multiple measurements
    اتجاه صحة التربة عبر قياسات متعددة
    """

    trend_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context
    field_id: str = ""
    indicator: SoilHealthIndicator = SoilHealthIndicator.ORGANIC_MATTER

    # Time period
    start_date: date | None = None
    end_date: date | None = None
    measurement_count: int = 0

    # Values
    initial_value: float | None = None
    current_value: float | None = None
    target_value: float | None = None

    # Trend analysis
    trend_direction: str = "stable"  # improving, declining, stable
    change_percent: float = 0.0
    change_rate_per_year: float = 0.0

    # Statistical
    min_value: float | None = None
    max_value: float | None = None
    avg_value: float | None = None
    std_deviation: float | None = None

    # Assessment
    status: str = "adequate"  # deficient, low, adequate, optimal, excessive
    status_ar: str = "كافي"

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "trend_id": self.trend_id,
            "field_id": self.field_id,
            "indicator": self.indicator.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "measurement_count": self.measurement_count,
            "initial_value": self.initial_value,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "trend_direction": self.trend_direction,
            "change_percent": self.change_percent,
            "change_rate_per_year": self.change_rate_per_year,
            "status": self.status,
            "status_ar": self.status_ar,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
        }


@dataclass
class SoilHealthReport:
    """
    Comprehensive soil health report
    تقرير شامل عن صحة التربة
    """

    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context
    tenant_id: str = ""
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str = ""

    # Report date
    report_date: date = field(default_factory=date.today)
    reporting_period_years: int = 3

    # Latest measurement
    latest_measurement: SoilHealthMeasurement | None = None

    # Trends
    trends: list[SoilHealthTrend] = field(default_factory=list)

    # Overall assessment
    overall_score: float = 0.0  # 0-100
    overall_rating: str = "fair"  # poor, fair, good, excellent
    overall_rating_ar: str = "مقبول"

    # Category scores
    physical_health_score: float = 0.0
    chemical_health_score: float = 0.0
    biological_health_score: float = 0.0

    # Rotation impact analysis
    rotation_impact_assessment: str = ""
    rotation_impact_assessment_ar: str = ""

    # Key findings
    key_findings: list[str] = field(default_factory=list)
    key_findings_ar: list[str] = field(default_factory=list)

    # Improvement areas
    improvement_areas: list[str] = field(default_factory=list)
    improvement_areas_ar: list[str] = field(default_factory=list)

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    generated_by: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.report_id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "report_date": self.report_date.isoformat(),
            "reporting_period_years": self.reporting_period_years,
            "latest_measurement": self.latest_measurement.to_dict() if self.latest_measurement else None,
            "trends": [t.to_dict() for t in self.trends],
            "overall_score": self.overall_score,
            "overall_rating": self.overall_rating,
            "overall_rating_ar": self.overall_rating_ar,
            "physical_health_score": self.physical_health_score,
            "chemical_health_score": self.chemical_health_score,
            "biological_health_score": self.biological_health_score,
            "rotation_impact_assessment": self.rotation_impact_assessment,
            "rotation_impact_assessment_ar": self.rotation_impact_assessment_ar,
            "key_findings": self.key_findings,
            "key_findings_ar": self.key_findings_ar,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
            "generated_at": self.generated_at.isoformat(),
        }


# =============================================================================
# Nutrient Cycling - دورة المغذيات
# =============================================================================


@dataclass
class NutrientBalance:
    """
    Nutrient balance calculation for rotation
    حساب توازن المغذيات للدورة الزراعية
    """

    balance_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context
    field_id: str = ""
    rotation_plan_id: str = ""
    calculation_date: date = field(default_factory=date.today)

    # Nitrogen balance (kg/ha)
    nitrogen_inputs: float = 0.0  # Fertilizer, fixation, residues
    nitrogen_outputs: float = 0.0  # Crop removal, losses
    nitrogen_balance: float = 0.0
    nitrogen_fixation_contribution: float = 0.0  # From legumes

    # Phosphorus balance (kg/ha)
    phosphorus_inputs: float = 0.0
    phosphorus_outputs: float = 0.0
    phosphorus_balance: float = 0.0

    # Potassium balance (kg/ha)
    potassium_inputs: float = 0.0
    potassium_outputs: float = 0.0
    potassium_balance: float = 0.0

    # Organic matter contribution
    organic_matter_addition_t_ha: float = 0.0
    residue_return_t_ha: float = 0.0

    # Assessment
    is_sustainable: bool = True
    sustainability_score: float = 0.0  # 0-100

    # Recommendations
    fertilizer_savings_potential_kg_ha: float = 0.0
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "balance_id": self.balance_id,
            "field_id": self.field_id,
            "rotation_plan_id": self.rotation_plan_id,
            "calculation_date": self.calculation_date.isoformat(),
            "nitrogen": {
                "inputs": self.nitrogen_inputs,
                "outputs": self.nitrogen_outputs,
                "balance": self.nitrogen_balance,
                "fixation_contribution": self.nitrogen_fixation_contribution,
            },
            "phosphorus": {
                "inputs": self.phosphorus_inputs,
                "outputs": self.phosphorus_outputs,
                "balance": self.phosphorus_balance,
            },
            "potassium": {
                "inputs": self.potassium_inputs,
                "outputs": self.potassium_outputs,
                "balance": self.potassium_balance,
            },
            "organic_matter_addition_t_ha": self.organic_matter_addition_t_ha,
            "is_sustainable": self.is_sustainable,
            "sustainability_score": self.sustainability_score,
            "fertilizer_savings_potential_kg_ha": self.fertilizer_savings_potential_kg_ha,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
        }


# =============================================================================
# Rotation Recommendations - توصيات الدورة الزراعية
# =============================================================================


@dataclass
class RotationRecommendation:
    """
    AI-generated rotation recommendation
    توصية الدورة الزراعية المولدة بالذكاء الاصطناعي
    """

    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context
    tenant_id: str = ""
    field_id: str = ""
    previous_crops: list[CropType] = field(default_factory=list)  # Last 3-5 crops

    # Recommendation
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    recommended_crop: CropType | None = None
    recommended_crop_name_ar: str = ""
    recommended_variety: str | None = None

    # Alternative options
    alternative_crops: list[CropType] = field(default_factory=list)

    # Timing
    recommended_season: Season = Season.WINTER
    recommended_planting_window_start: date | None = None
    recommended_planting_window_end: date | None = None

    # Expected benefits
    expected_benefits: list[RotationBenefit] = field(default_factory=list)

    # Scores (0-100)
    overall_suitability_score: float = 0.0
    soil_health_score: float = 0.0
    pest_break_score: float = 0.0
    economic_score: float = 0.0
    water_efficiency_score: float = 0.0

    # Reasoning
    reasoning_en: str = ""
    reasoning_ar: str = ""

    # Detailed factors
    positive_factors: list[str] = field(default_factory=list)
    positive_factors_ar: list[str] = field(default_factory=list)
    negative_factors: list[str] = field(default_factory=list)
    negative_factors_ar: list[str] = field(default_factory=list)

    # Warnings and cautions
    warnings: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    # Economic projection
    projected_yield_tons_ha: float | None = None
    projected_revenue_per_ha: float | None = None
    projected_cost_per_ha: float | None = None
    projected_profit_per_ha: float | None = None

    # Confidence
    confidence: float = 0.8  # 0-1

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    model_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "recommendation_id": self.recommendation_id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "previous_crops": [c.value for c in self.previous_crops],
            "priority": self.priority.value,
            "recommended_crop": self.recommended_crop.value if self.recommended_crop else None,
            "recommended_crop_name_ar": self.recommended_crop_name_ar,
            "recommended_variety": self.recommended_variety,
            "alternative_crops": [c.value for c in self.alternative_crops],
            "recommended_season": self.recommended_season.value,
            "expected_benefits": [b.value for b in self.expected_benefits],
            "scores": {
                "overall_suitability": self.overall_suitability_score,
                "soil_health": self.soil_health_score,
                "pest_break": self.pest_break_score,
                "economic": self.economic_score,
                "water_efficiency": self.water_efficiency_score,
            },
            "reasoning_en": self.reasoning_en,
            "reasoning_ar": self.reasoning_ar,
            "positive_factors": self.positive_factors,
            "positive_factors_ar": self.positive_factors_ar,
            "negative_factors": self.negative_factors,
            "negative_factors_ar": self.negative_factors_ar,
            "warnings": self.warnings,
            "warnings_ar": self.warnings_ar,
            "projected_profit_per_ha": self.projected_profit_per_ha,
            "confidence": self.confidence,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class MultiYearPlan:
    """
    Multi-year rotation and planning analysis
    تحليل الدورة الزراعية والتخطيط متعدد السنوات
    """

    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context
    tenant_id: str = ""
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str = ""
    total_area_ha: float = 0.0

    # Time frame
    start_year: int = 2026
    end_year: int = 2030
    total_years: int = 5

    # Year-by-year plans
    yearly_recommendations: list[RotationRecommendation] = field(default_factory=list)

    # Cumulative projections
    total_projected_revenue: float = 0.0
    total_projected_cost: float = 0.0
    total_projected_profit: float = 0.0
    average_annual_profit_per_ha: float = 0.0

    # Soil health trajectory
    expected_organic_matter_change_percent: float = 0.0
    expected_soil_health_score_change: float = 0.0

    # Nutrient balance
    nutrient_balance: NutrientBalance | None = None

    # Risk assessment
    overall_risk_level: str = "medium"  # low, medium, high
    risk_factors: list[str] = field(default_factory=list)
    risk_factors_ar: list[str] = field(default_factory=list)
    risk_mitigation: list[str] = field(default_factory=list)
    risk_mitigation_ar: list[str] = field(default_factory=list)

    # Summary
    summary_en: str = ""
    summary_ar: str = ""

    # Key recommendations
    key_recommendations: list[str] = field(default_factory=list)
    key_recommendations_ar: list[str] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    generated_by: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plan_id": self.plan_id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "total_area_ha": self.total_area_ha,
            "time_frame": {
                "start_year": self.start_year,
                "end_year": self.end_year,
                "total_years": self.total_years,
            },
            "yearly_recommendations": [r.to_dict() for r in self.yearly_recommendations],
            "projections": {
                "total_revenue": self.total_projected_revenue,
                "total_cost": self.total_projected_cost,
                "total_profit": self.total_projected_profit,
                "average_annual_profit_per_ha": self.average_annual_profit_per_ha,
            },
            "soil_health": {
                "expected_organic_matter_change_percent": self.expected_organic_matter_change_percent,
                "expected_soil_health_score_change": self.expected_soil_health_score_change,
            },
            "nutrient_balance": self.nutrient_balance.to_dict() if self.nutrient_balance else None,
            "risk_assessment": {
                "overall_risk_level": self.overall_risk_level,
                "risk_factors": self.risk_factors,
                "risk_factors_ar": self.risk_factors_ar,
                "risk_mitigation": self.risk_mitigation,
                "risk_mitigation_ar": self.risk_mitigation_ar,
            },
            "summary_en": self.summary_en,
            "summary_ar": self.summary_ar,
            "key_recommendations": self.key_recommendations,
            "key_recommendations_ar": self.key_recommendations_ar,
            "generated_at": self.generated_at.isoformat(),
        }


# =============================================================================
# Field History - سجل الحقل
# =============================================================================


@dataclass
class CropHistoryRecord:
    """
    Historical record of a crop grown in a field
    سجل تاريخي لمحصول زُرع في حقل
    """

    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Context
    field_id: str = ""
    tenant_id: str = ""

    # Crop info
    crop_type: CropType = CropType.WHEAT
    crop_variety: str | None = None

    # Dates
    planting_date: date | None = None
    harvest_date: date | None = None
    season: Season = Season.WINTER
    year: int = 2025

    # Area
    area_ha: float = 0.0

    # Yields
    yield_tons_ha: float | None = None
    yield_quality: str | None = None  # Grade A, B, C, etc.

    # Inputs
    fertilizer_n_kg_ha: float = 0.0
    fertilizer_p_kg_ha: float = 0.0
    fertilizer_k_kg_ha: float = 0.0
    irrigation_mm: float = 0.0
    pesticide_applications: int = 0

    # Issues
    pest_issues: list[str] = field(default_factory=list)
    disease_issues: list[str] = field(default_factory=list)
    weather_issues: list[str] = field(default_factory=list)

    # Economics
    revenue_per_ha: float | None = None
    cost_per_ha: float | None = None
    profit_per_ha: float | None = None

    # Notes
    notes: str = ""
    notes_ar: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "record_id": self.record_id,
            "field_id": self.field_id,
            "crop_type": self.crop_type.value,
            "crop_variety": self.crop_variety,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "season": self.season.value,
            "year": self.year,
            "area_ha": self.area_ha,
            "yield_tons_ha": self.yield_tons_ha,
            "fertilizer": {
                "n_kg_ha": self.fertilizer_n_kg_ha,
                "p_kg_ha": self.fertilizer_p_kg_ha,
                "k_kg_ha": self.fertilizer_k_kg_ha,
            },
            "irrigation_mm": self.irrigation_mm,
            "pest_issues": self.pest_issues,
            "disease_issues": self.disease_issues,
            "profit_per_ha": self.profit_per_ha,
        }


@dataclass
class FieldRotationHistory:
    """
    Complete rotation history for a field
    سجل الدورة الزراعية الكامل للحقل
    """

    history_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Field info
    field_id: str = ""
    tenant_id: str = ""
    field_name: str = ""
    field_name_ar: str = ""

    # History records
    records: list[CropHistoryRecord] = field(default_factory=list)

    # Analysis
    total_crops_grown: int = 0
    years_of_data: int = 0
    most_common_crop: CropType | None = None
    average_yield_tons_ha: float = 0.0
    average_profit_per_ha: float = 0.0

    # Rotation patterns identified
    rotation_patterns: list[str] = field(default_factory=list)
    rotation_patterns_ar: list[str] = field(default_factory=list)

    # Issues patterns
    recurring_pests: list[str] = field(default_factory=list)
    recurring_diseases: list[str] = field(default_factory=list)

    # Soil health trend (from historical data)
    soil_health_trend: str = "stable"  # improving, declining, stable

    # Recommendations based on history
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    def get_last_n_crops(self, n: int = 5) -> list[CropType]:
        """Get the last N crops grown"""
        sorted_records = sorted(self.records, key=lambda r: (r.year, r.season.value), reverse=True)
        return [r.crop_type for r in sorted_records[:n]]

    def get_years_since_crop(self, crop_type: CropType) -> int | None:
        """Get years since a specific crop was grown"""
        for record in sorted(self.records, key=lambda r: r.year, reverse=True):
            if record.crop_type == crop_type:
                from datetime import date

                current_year = date.today().year
                return current_year - record.year
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "history_id": self.history_id,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "records": [r.to_dict() for r in self.records],
            "analysis": {
                "total_crops_grown": self.total_crops_grown,
                "years_of_data": self.years_of_data,
                "most_common_crop": self.most_common_crop.value if self.most_common_crop else None,
                "average_yield_tons_ha": self.average_yield_tons_ha,
                "average_profit_per_ha": self.average_profit_per_ha,
            },
            "rotation_patterns": self.rotation_patterns,
            "rotation_patterns_ar": self.rotation_patterns_ar,
            "recurring_pests": self.recurring_pests,
            "recurring_diseases": self.recurring_diseases,
            "soil_health_trend": self.soil_health_trend,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
        }
