"""
Soil Testing Models - نماذج تحليل التربة

Comprehensive data models for soil test recording, lab integration,
and result management for SAHOOL agricultural platform.

Supports:
- Macronutrients (NPK)
- Secondary nutrients (Ca, Mg, S)
- Micronutrients (Fe, Zn, Mn, Cu, B, Mo)
- Soil properties (pH, EC, organic matter, CEC)
- Soil texture and classification
- Local Middle East soil types

Author: SAHOOL Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any


class NutrientStatus(StrEnum):
    """Nutrient level interpretation status - حالة تفسير مستوى العنصر"""

    VERY_DEFICIENT = "very_deficient"  # نقص شديد جداً
    DEFICIENT = "deficient"  # نقص
    LOW = "low"  # منخفض
    ADEQUATE = "adequate"  # كافي
    OPTIMAL = "optimal"  # مثالي
    HIGH = "high"  # مرتفع
    EXCESSIVE = "excessive"  # زائد
    TOXIC = "toxic"  # سام


class SoilTextureClass(StrEnum):
    """USDA Soil texture classification - تصنيف قوام التربة"""

    SAND = "sand"  # رمل
    LOAMY_SAND = "loamy_sand"  # رمل طميي
    SANDY_LOAM = "sandy_loam"  # طمي رملي
    LOAM = "loam"  # طمي
    SILT_LOAM = "silt_loam"  # طمي طيني
    SILT = "silt"  # طين
    SANDY_CLAY_LOAM = "sandy_clay_loam"  # طمي صلصالي رملي
    CLAY_LOAM = "clay_loam"  # طمي صلصالي
    SILTY_CLAY_LOAM = "silty_clay_loam"  # طمي صلصالي طيني
    SANDY_CLAY = "sandy_clay"  # صلصال رملي
    SILTY_CLAY = "silty_clay"  # صلصال طيني
    CLAY = "clay"  # صلصال


class SoilType(StrEnum):
    """Local soil types common in Middle East - أنواع التربة المحلية"""

    ALLUVIAL = "alluvial"  # طمي فيضي
    CALCAREOUS = "calcareous"  # كلسي
    SALINE = "saline"  # ملحي
    SODIC = "sodic"  # صودي
    GYPSIFEROUS = "gypsiferous"  # جبسي
    SANDY_DESERT = "sandy_desert"  # صحراوي رملي
    LOESS = "loess"  # لوس
    RED_MEDITERRANEAN = "red_mediterranean"  # أحمر متوسطي
    VERTISOL = "vertisol"  # فرتيسول (أراضي سوداء)
    ARIDISOL = "aridisol"  # أراضي جافة


class SampleType(StrEnum):
    """Type of soil sample - نوع عينة التربة"""

    COMPOSITE = "composite"  # مركبة
    SINGLE = "single"  # مفردة
    GRID = "grid"  # شبكية
    ZONE = "zone"  # منطقية
    DEPTH_PROFILE = "depth_profile"  # قطاع عمقي


class LabStatus(StrEnum):
    """Lab analysis status - حالة التحليل المعملي"""

    PENDING = "pending"  # قيد الانتظار
    IN_PROGRESS = "in_progress"  # جاري التحليل
    COMPLETED = "completed"  # مكتمل
    FAILED = "failed"  # فشل
    PARTIAL = "partial"  # جزئي


class ExtractionMethod(StrEnum):
    """Nutrient extraction methods - طرق استخلاص العناصر"""

    MEHLICH_3 = "mehlich_3"  # ميليك-3
    OLSEN = "olsen"  # أولسن (للتربة القلوية)
    BRAY_1 = "bray_1"  # براي-1
    AMMONIUM_ACETATE = "ammonium_acetate"  # أسيتات الأمونيوم
    DTPA = "dtpa"  # DTPA للعناصر الصغرى
    HOT_WATER = "hot_water"  # ماء ساخن (للبورون)
    SATURATED_PASTE = "saturated_paste"  # عجينة مشبعة


@dataclass
class SampleLocation:
    """GPS location and depth of soil sample - موقع وعمق عينة التربة"""

    latitude: float
    longitude: float
    depth_cm_start: int = 0
    depth_cm_end: int = 30
    elevation_m: float | None = None
    zone_name: str = ""
    zone_name_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "depth_cm": f"{self.depth_cm_start}-{self.depth_cm_end}",
            "elevation_m": self.elevation_m,
            "zone": self.zone_name,
            "zone_ar": self.zone_name_ar,
        }


@dataclass
class LabInfo:
    """Laboratory information - معلومات المختبر"""

    lab_id: str
    lab_name: str
    lab_name_ar: str
    accreditation: str = ""  # ISO 17025, etc.
    contact_email: str = ""
    contact_phone: str = ""
    address: str = ""
    address_ar: str = ""
    turnaround_days: int = 7

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "lab_id": self.lab_id,
            "lab_name": self.lab_name,
            "lab_name_ar": self.lab_name_ar,
            "accreditation": self.accreditation,
            "turnaround_days": self.turnaround_days,
        }


@dataclass
class MacronutrientResults:
    """
    Macronutrient test results - نتائج العناصر الكبرى
    Values in ppm (mg/kg) unless otherwise noted
    """

    # Primary macronutrients
    nitrogen_total_percent: float = 0.0  # نيتروجين كلي %
    nitrogen_nitrate_ppm: float = 0.0  # نترات النيتروجين
    nitrogen_ammonium_ppm: float = 0.0  # أمونيوم النيتروجين
    phosphorus_ppm: float = 0.0  # فسفور
    potassium_ppm: float = 0.0  # بوتاسيوم

    # Secondary macronutrients
    calcium_ppm: float = 0.0  # كالسيوم
    magnesium_ppm: float = 0.0  # مغنيسيوم
    sulfur_ppm: float = 0.0  # كبريت

    # Extraction methods used
    p_extraction_method: ExtractionMethod = ExtractionMethod.OLSEN
    k_extraction_method: ExtractionMethod = ExtractionMethod.AMMONIUM_ACETATE

    @property
    def available_nitrogen_ppm(self) -> float:
        """Total available nitrogen (nitrate + ammonium)"""
        return self.nitrogen_nitrate_ppm + self.nitrogen_ammonium_ppm

    @property
    def ca_mg_ratio(self) -> float:
        """Calcium to Magnesium ratio (optimal: 3-5)"""
        if self.magnesium_ppm > 0:
            return self.calcium_ppm / self.magnesium_ppm
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "N_total_percent": self.nitrogen_total_percent,
            "N_NO3_ppm": self.nitrogen_nitrate_ppm,
            "N_NH4_ppm": self.nitrogen_ammonium_ppm,
            "N_available_ppm": self.available_nitrogen_ppm,
            "P_ppm": self.phosphorus_ppm,
            "K_ppm": self.potassium_ppm,
            "Ca_ppm": self.calcium_ppm,
            "Mg_ppm": self.magnesium_ppm,
            "S_ppm": self.sulfur_ppm,
            "Ca_Mg_ratio": round(self.ca_mg_ratio, 2),
        }


@dataclass
class MicronutrientResults:
    """
    Micronutrient test results - نتائج العناصر الصغرى
    Values in ppm (mg/kg)
    """

    iron_ppm: float = 0.0  # حديد Fe
    zinc_ppm: float = 0.0  # زنك Zn
    manganese_ppm: float = 0.0  # منجنيز Mn
    copper_ppm: float = 0.0  # نحاس Cu
    boron_ppm: float = 0.0  # بورون B
    molybdenum_ppm: float = 0.0  # موليبدنوم Mo
    chloride_ppm: float = 0.0  # كلوريد Cl
    sodium_ppm: float = 0.0  # صوديوم Na (often tested with micros)

    # Extraction method
    extraction_method: ExtractionMethod = ExtractionMethod.DTPA

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "Fe_ppm": self.iron_ppm,
            "Zn_ppm": self.zinc_ppm,
            "Mn_ppm": self.manganese_ppm,
            "Cu_ppm": self.copper_ppm,
            "B_ppm": self.boron_ppm,
            "Mo_ppm": self.molybdenum_ppm,
            "Cl_ppm": self.chloride_ppm,
            "Na_ppm": self.sodium_ppm,
        }


@dataclass
class SoilProperties:
    """
    Physical and chemical soil properties - خواص التربة الفيزيائية والكيميائية
    """

    # Acidity/Alkalinity
    ph: float = 7.0  # درجة الحموضة
    ph_buffer: float | None = None  # pH buffer for lime requirement

    # Salinity
    ec_ds_m: float = 0.0  # التوصيل الكهربائي dS/m
    sar: float = 0.0  # نسبة امتصاص الصوديوم (Sodium Adsorption Ratio)
    esp: float = 0.0  # نسبة الصوديوم المتبادل %

    # Organic matter
    organic_matter_percent: float = 0.0  # المادة العضوية %
    organic_carbon_percent: float = 0.0  # الكربون العضوي %

    # Cation Exchange
    cec_meq_100g: float = 0.0  # السعة التبادلية الكاتيونية
    base_saturation_percent: float = 0.0  # نسبة تشبع القواعد %

    # Calcium carbonate
    caco3_percent: float = 0.0  # كربونات الكالسيوم %
    active_lime_percent: float = 0.0  # الجير النشط %

    # Gypsum
    gypsum_percent: float = 0.0  # الجبس %

    # Moisture
    field_capacity_percent: float = 0.0  # السعة الحقلية %
    wilting_point_percent: float = 0.0  # نقطة الذبول %
    available_water_percent: float = 0.0  # الماء المتاح %

    @property
    def organic_carbon_from_om(self) -> float:
        """Calculate organic carbon from organic matter (OM / 1.724)"""
        return self.organic_matter_percent / 1.724

    @property
    def is_saline(self) -> bool:
        """Check if soil is saline (EC > 4 dS/m)"""
        return self.ec_ds_m > 4.0

    @property
    def is_sodic(self) -> bool:
        """Check if soil is sodic (ESP > 15% or SAR > 13)"""
        return self.esp > 15 or self.sar > 13

    @property
    def is_calcareous(self) -> bool:
        """Check if soil is calcareous (CaCO3 > 15%)"""
        return self.caco3_percent > 15

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pH": self.ph,
            "pH_buffer": self.ph_buffer,
            "EC_dS_m": self.ec_ds_m,
            "SAR": self.sar,
            "ESP_percent": self.esp,
            "OM_percent": self.organic_matter_percent,
            "OC_percent": self.organic_carbon_percent,
            "CEC_meq_100g": self.cec_meq_100g,
            "base_saturation_percent": self.base_saturation_percent,
            "CaCO3_percent": self.caco3_percent,
            "active_lime_percent": self.active_lime_percent,
            "gypsum_percent": self.gypsum_percent,
            "is_saline": self.is_saline,
            "is_sodic": self.is_sodic,
            "is_calcareous": self.is_calcareous,
        }


@dataclass
class SoilTexture:
    """Soil texture analysis - تحليل قوام التربة"""

    sand_percent: float = 0.0  # رمل %
    silt_percent: float = 0.0  # طمي %
    clay_percent: float = 0.0  # صلصال %

    # Calculated/determined texture class
    texture_class: SoilTextureClass = SoilTextureClass.LOAM
    texture_class_ar: str = ""

    # Coarse fragments
    gravel_percent: float = 0.0  # حصى %
    stones_percent: float = 0.0  # حجارة %

    @property
    def fine_earth_percent(self) -> float:
        """Percentage of fine earth (< 2mm)"""
        return 100 - self.gravel_percent - self.stones_percent

    def validate_percentages(self) -> bool:
        """Validate that sand + silt + clay = 100%"""
        total = self.sand_percent + self.silt_percent + self.clay_percent
        return 99.0 <= total <= 101.0  # Allow small rounding errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "sand_percent": self.sand_percent,
            "silt_percent": self.silt_percent,
            "clay_percent": self.clay_percent,
            "texture_class": self.texture_class.value,
            "texture_class_ar": self.texture_class_ar,
            "gravel_percent": self.gravel_percent,
            "stones_percent": self.stones_percent,
        }


@dataclass
class HeavyMetals:
    """Heavy metal content - محتوى المعادن الثقيلة"""

    lead_ppm: float = 0.0  # رصاص Pb
    cadmium_ppm: float = 0.0  # كادميوم Cd
    chromium_ppm: float = 0.0  # كروم Cr
    nickel_ppm: float = 0.0  # نيكل Ni
    arsenic_ppm: float = 0.0  # زرنيخ As
    mercury_ppm: float = 0.0  # زئبق Hg

    def exceeds_limits(self, crop_type: str = "general") -> list[str]:
        """Check if any heavy metal exceeds regulatory limits"""
        # FAO/WHO limits for agricultural soils (mg/kg)
        limits = {
            "lead_ppm": 100,
            "cadmium_ppm": 3,
            "chromium_ppm": 100,
            "nickel_ppm": 50,
            "arsenic_ppm": 20,
            "mercury_ppm": 1,
        }
        exceeded = []
        for metal, limit in limits.items():
            if getattr(self, metal, 0) > limit:
                exceeded.append(metal.replace("_ppm", "").capitalize())
        return exceeded

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "Pb_ppm": self.lead_ppm,
            "Cd_ppm": self.cadmium_ppm,
            "Cr_ppm": self.chromium_ppm,
            "Ni_ppm": self.nickel_ppm,
            "As_ppm": self.arsenic_ppm,
            "Hg_ppm": self.mercury_ppm,
            "exceeds_limits": self.exceeds_limits(),
        }


@dataclass
class SoilTestResult:
    """
    Complete soil test result record - سجل نتيجة تحليل التربة الكامل

    This is the main data model for a complete soil test including
    all nutrient analyses, soil properties, and metadata.
    """

    # Identification
    id: str
    tenant_id: str
    field_id: str
    sample_id: str

    # Timing
    sample_date: datetime
    analysis_date: datetime | None = None
    report_date: datetime | None = None

    # Sample details
    sample_type: SampleType = SampleType.COMPOSITE
    sample_location: SampleLocation | None = None
    number_of_subsamples: int = 1
    sampler_name: str = ""

    # Lab information
    lab_info: LabInfo | None = None
    lab_status: LabStatus = LabStatus.PENDING
    lab_reference_number: str = ""

    # Results
    macronutrients: MacronutrientResults | None = None
    micronutrients: MicronutrientResults | None = None
    soil_properties: SoilProperties | None = None
    texture: SoilTexture | None = None
    heavy_metals: HeavyMetals | None = None

    # Classification
    soil_type: SoilType | None = None
    soil_type_ar: str = ""

    # Quality indicators
    quality_score: float = 0.0  # 0-100
    data_completeness_percent: float = 0.0

    # Cost
    analysis_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""
    notes_ar: str = ""

    # Attachments
    report_url: str = ""
    raw_data_url: str = ""

    def calculate_completeness(self) -> float:
        """Calculate data completeness percentage"""
        total_fields = 0
        filled_fields = 0

        # Check macronutrients
        if self.macronutrients:
            total_fields += 8
            if self.macronutrients.nitrogen_total_percent > 0:
                filled_fields += 1
            if self.macronutrients.nitrogen_nitrate_ppm > 0:
                filled_fields += 1
            if self.macronutrients.phosphorus_ppm > 0:
                filled_fields += 1
            if self.macronutrients.potassium_ppm > 0:
                filled_fields += 1
            if self.macronutrients.calcium_ppm > 0:
                filled_fields += 1
            if self.macronutrients.magnesium_ppm > 0:
                filled_fields += 1
            if self.macronutrients.sulfur_ppm > 0:
                filled_fields += 1
            if self.macronutrients.nitrogen_ammonium_ppm > 0:
                filled_fields += 1

        # Check micronutrients
        if self.micronutrients:
            total_fields += 6
            if self.micronutrients.iron_ppm > 0:
                filled_fields += 1
            if self.micronutrients.zinc_ppm > 0:
                filled_fields += 1
            if self.micronutrients.manganese_ppm > 0:
                filled_fields += 1
            if self.micronutrients.copper_ppm > 0:
                filled_fields += 1
            if self.micronutrients.boron_ppm > 0:
                filled_fields += 1
            if self.micronutrients.molybdenum_ppm > 0:
                filled_fields += 1

        # Check soil properties
        if self.soil_properties:
            total_fields += 5
            if self.soil_properties.ph > 0:
                filled_fields += 1
            if self.soil_properties.ec_ds_m >= 0:
                filled_fields += 1
            if self.soil_properties.organic_matter_percent > 0:
                filled_fields += 1
            if self.soil_properties.cec_meq_100g > 0:
                filled_fields += 1
            if self.soil_properties.caco3_percent >= 0:
                filled_fields += 1

        # Check texture
        if self.texture:
            total_fields += 3
            if self.texture.sand_percent > 0:
                filled_fields += 1
            if self.texture.silt_percent > 0:
                filled_fields += 1
            if self.texture.clay_percent > 0:
                filled_fields += 1

        if total_fields == 0:
            return 0.0

        return (filled_fields / total_fields) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "sample_id": self.sample_id,
            "sample_date": self.sample_date.isoformat(),
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "sample_type": self.sample_type.value,
            "sample_location": self.sample_location.to_dict() if self.sample_location else None,
            "lab_info": self.lab_info.to_dict() if self.lab_info else None,
            "lab_status": self.lab_status.value,
            "macronutrients": self.macronutrients.to_dict() if self.macronutrients else None,
            "micronutrients": self.micronutrients.to_dict() if self.micronutrients else None,
            "soil_properties": self.soil_properties.to_dict() if self.soil_properties else None,
            "texture": self.texture.to_dict() if self.texture else None,
            "heavy_metals": self.heavy_metals.to_dict() if self.heavy_metals else None,
            "soil_type": self.soil_type.value if self.soil_type else None,
            "soil_type_ar": self.soil_type_ar,
            "quality_score": self.quality_score,
            "data_completeness_percent": self.calculate_completeness(),
            "analysis_cost": float(self.analysis_cost),
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class NutrientInterpretation:
    """
    Interpretation of a single nutrient level - تفسير مستوى عنصر غذائي

    Used to communicate the meaning of a soil test value to farmers.
    """

    nutrient_code: str  # N, P, K, Fe, etc.
    nutrient_name: str
    nutrient_name_ar: str

    # Value and units
    value: float
    unit: str  # ppm, %, meq/100g
    unit_ar: str

    # Interpretation
    status: NutrientStatus
    status_description: str
    status_description_ar: str

    # Thresholds used
    deficient_threshold: float
    low_threshold: float
    adequate_threshold: float
    high_threshold: float
    excessive_threshold: float

    # Action guidance
    action_needed: bool
    action_priority: int  # 1=urgent, 5=monitoring
    action_description: str = ""
    action_description_ar: str = ""

    # Impact
    crop_impact: str = ""
    crop_impact_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "nutrient_code": self.nutrient_code,
            "nutrient_name": self.nutrient_name,
            "nutrient_name_ar": self.nutrient_name_ar,
            "value": self.value,
            "unit": self.unit,
            "status": self.status.value,
            "status_description": self.status_description,
            "status_description_ar": self.status_description_ar,
            "action_needed": self.action_needed,
            "action_priority": self.action_priority,
            "action_description": self.action_description,
            "action_description_ar": self.action_description_ar,
        }


@dataclass
class InterpretationReport:
    """
    Complete interpretation report for a soil test - تقرير تفسير كامل لتحليل التربة
    """

    # Reference
    soil_test_id: str
    field_id: str
    interpretation_date: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Nutrient interpretations
    interpretations: list[NutrientInterpretation] = field(default_factory=list)

    # Overall assessment
    overall_fertility_score: float = 0.0  # 0-100
    overall_fertility_grade: str = ""  # A, B, C, D, F
    overall_fertility_grade_ar: str = ""

    # Key issues identified
    deficiencies: list[str] = field(default_factory=list)
    deficiencies_ar: list[str] = field(default_factory=list)
    excesses: list[str] = field(default_factory=list)
    excesses_ar: list[str] = field(default_factory=list)

    # Soil health indicators
    ph_status: str = ""
    ph_status_ar: str = ""
    salinity_status: str = ""
    salinity_status_ar: str = ""
    organic_matter_status: str = ""
    organic_matter_status_ar: str = ""

    # Summary
    summary_en: str = ""
    summary_ar: str = ""

    # Recommendations preview
    immediate_actions: list[str] = field(default_factory=list)
    immediate_actions_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "soil_test_id": self.soil_test_id,
            "field_id": self.field_id,
            "interpretation_date": self.interpretation_date.isoformat(),
            "interpretations": [i.to_dict() for i in self.interpretations],
            "overall_fertility_score": self.overall_fertility_score,
            "overall_fertility_grade": self.overall_fertility_grade,
            "deficiencies": self.deficiencies,
            "deficiencies_ar": self.deficiencies_ar,
            "excesses": self.excesses,
            "excesses_ar": self.excesses_ar,
            "summary_en": self.summary_en,
            "summary_ar": self.summary_ar,
            "immediate_actions": self.immediate_actions,
            "immediate_actions_ar": self.immediate_actions_ar,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class AmendmentRecommendation:
    """
    Single soil amendment recommendation - توصية تعديل تربة واحدة
    """

    # Amendment identification
    amendment_id: str
    amendment_type: str  # fertilizer, lime, gypsum, organic, etc.
    amendment_type_ar: str

    # Product details
    product_name: str
    product_name_ar: str
    product_formula: str = ""  # Chemical formula if applicable

    # Application details
    application_rate_kg_ha: float = 0.0
    application_rate_per_tree: float | None = None  # For orchards
    application_method: str = ""
    application_method_ar: str = ""

    # Timing
    application_timing: str = ""
    application_timing_ar: str = ""
    optimal_season: str = ""
    optimal_season_ar: str = ""

    # Target
    target_nutrient: str = ""
    target_improvement: str = ""
    target_improvement_ar: str = ""

    # Nutrients supplied (for fertilizers)
    nutrients_supplied: dict[str, float] = field(default_factory=dict)

    # Cost
    estimated_cost_per_ha: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Priority and confidence
    priority: int = 1  # 1=highest, 5=lowest
    confidence: float = 0.8  # 0-1

    # Warnings
    warnings: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    # Reasoning
    reason_en: str = ""
    reason_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "amendment_id": self.amendment_id,
            "amendment_type": self.amendment_type,
            "amendment_type_ar": self.amendment_type_ar,
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "application_rate_kg_ha": self.application_rate_kg_ha,
            "application_method": self.application_method,
            "application_method_ar": self.application_method_ar,
            "application_timing": self.application_timing,
            "application_timing_ar": self.application_timing_ar,
            "target_nutrient": self.target_nutrient,
            "nutrients_supplied": self.nutrients_supplied,
            "estimated_cost_per_ha": float(self.estimated_cost_per_ha),
            "priority": self.priority,
            "confidence": self.confidence,
            "warnings": self.warnings,
            "warnings_ar": self.warnings_ar,
            "reason_en": self.reason_en,
            "reason_ar": self.reason_ar,
        }


@dataclass
class AmendmentPlan:
    """
    Complete amendment plan based on soil test - خطة تعديل التربة الكاملة
    """

    # Reference
    plan_id: str
    soil_test_id: str
    field_id: str
    tenant_id: str

    # Context
    crop: str = ""
    crop_ar: str = ""
    target_yield_tons_ha: float = 0.0
    field_area_ha: float = 0.0

    # Plan details
    plan_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_until: datetime | None = None

    # Recommendations
    recommendations: list[AmendmentRecommendation] = field(default_factory=list)

    # Totals
    total_estimated_cost: Decimal = Decimal("0.00")
    total_n_kg_ha: float = 0.0
    total_p_kg_ha: float = 0.0
    total_k_kg_ha: float = 0.0
    currency: str = "SAR"

    # Implementation timeline
    phases: list[dict] = field(default_factory=list)

    # Expected outcomes
    expected_yield_improvement_percent: float = 0.0
    expected_roi: float = 0.0

    # Summary
    summary_en: str = ""
    summary_ar: str = ""

    # Metadata
    created_by: str = ""
    approved_by: str = ""
    approved_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plan_id": self.plan_id,
            "soil_test_id": self.soil_test_id,
            "field_id": self.field_id,
            "crop": self.crop,
            "crop_ar": self.crop_ar,
            "target_yield_tons_ha": self.target_yield_tons_ha,
            "field_area_ha": self.field_area_ha,
            "plan_date": self.plan_date.isoformat(),
            "recommendations": [r.to_dict() for r in self.recommendations],
            "total_estimated_cost": float(self.total_estimated_cost),
            "total_nutrients_kg_ha": {
                "N": self.total_n_kg_ha,
                "P2O5": self.total_p_kg_ha,
                "K2O": self.total_k_kg_ha,
            },
            "expected_yield_improvement_percent": self.expected_yield_improvement_percent,
            "expected_roi": self.expected_roi,
            "summary_en": self.summary_en,
            "summary_ar": self.summary_ar,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class TrendDataPoint:
    """Single data point for trend analysis - نقطة بيانات واحدة لتحليل الاتجاهات"""

    date: datetime
    value: float
    soil_test_id: str
    notes: str = ""


@dataclass
class NutrientTrend:
    """
    Trend analysis for a single nutrient - تحليل اتجاه لعنصر غذائي واحد
    """

    nutrient_code: str
    nutrient_name: str
    nutrient_name_ar: str
    unit: str

    # Data points
    data_points: list[TrendDataPoint] = field(default_factory=list)

    # Statistics
    min_value: float = 0.0
    max_value: float = 0.0
    mean_value: float = 0.0
    std_deviation: float = 0.0

    # Trend analysis
    trend_direction: str = ""  # increasing, decreasing, stable
    trend_direction_ar: str = ""
    trend_slope: float = 0.0  # Change per year
    trend_r_squared: float = 0.0  # Correlation coefficient

    # Status over time
    status_history: list[dict] = field(default_factory=list)

    # Interpretation
    interpretation_en: str = ""
    interpretation_ar: str = ""

    # Recommendations based on trend
    trend_based_action: str = ""
    trend_based_action_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "nutrient_code": self.nutrient_code,
            "nutrient_name": self.nutrient_name,
            "nutrient_name_ar": self.nutrient_name_ar,
            "unit": self.unit,
            "data_points": [{"date": dp.date.isoformat(), "value": dp.value} for dp in self.data_points],
            "statistics": {
                "min": self.min_value,
                "max": self.max_value,
                "mean": self.mean_value,
                "std_dev": self.std_deviation,
            },
            "trend": {
                "direction": self.trend_direction,
                "direction_ar": self.trend_direction_ar,
                "slope_per_year": self.trend_slope,
                "r_squared": self.trend_r_squared,
            },
            "interpretation_en": self.interpretation_en,
            "interpretation_ar": self.interpretation_ar,
        }


@dataclass
class TrendReport:
    """
    Complete trend analysis report - تقرير تحليل الاتجاهات الكامل
    """

    # Identification
    field_id: str
    tenant_id: str
    report_date: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Analysis period
    period_start: datetime | None = None
    period_end: datetime | None = None
    number_of_tests: int = 0

    # Nutrient trends
    nutrient_trends: list[NutrientTrend] = field(default_factory=list)

    # Soil property trends
    ph_trend: NutrientTrend | None = None
    ec_trend: NutrientTrend | None = None
    om_trend: NutrientTrend | None = None

    # Key findings
    improving_nutrients: list[str] = field(default_factory=list)
    improving_nutrients_ar: list[str] = field(default_factory=list)
    declining_nutrients: list[str] = field(default_factory=list)
    declining_nutrients_ar: list[str] = field(default_factory=list)
    stable_nutrients: list[str] = field(default_factory=list)
    stable_nutrients_ar: list[str] = field(default_factory=list)

    # Overall soil health trend
    overall_trend: str = ""  # improving, stable, declining
    overall_trend_ar: str = ""
    soil_health_score_history: list[dict] = field(default_factory=list)

    # Recommendations
    management_recommendations: list[str] = field(default_factory=list)
    management_recommendations_ar: list[str] = field(default_factory=list)

    # Summary
    summary_en: str = ""
    summary_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field_id": self.field_id,
            "report_date": self.report_date.isoformat(),
            "period": {
                "start": self.period_start.isoformat() if self.period_start else None,
                "end": self.period_end.isoformat() if self.period_end else None,
                "number_of_tests": self.number_of_tests,
            },
            "nutrient_trends": [t.to_dict() for t in self.nutrient_trends],
            "soil_property_trends": {
                "pH": self.ph_trend.to_dict() if self.ph_trend else None,
                "EC": self.ec_trend.to_dict() if self.ec_trend else None,
                "OM": self.om_trend.to_dict() if self.om_trend else None,
            },
            "findings": {
                "improving": self.improving_nutrients,
                "declining": self.declining_nutrients,
                "stable": self.stable_nutrients,
            },
            "overall_trend": self.overall_trend,
            "overall_trend_ar": self.overall_trend_ar,
            "recommendations": self.management_recommendations,
            "recommendations_ar": self.management_recommendations_ar,
            "summary_en": self.summary_en,
            "summary_ar": self.summary_ar,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
