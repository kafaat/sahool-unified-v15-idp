"""
SPRING Water Management Metrics
مقاييس إدارة المياه لبرنامج SPRING

Pydantic models for tracking water usage, efficiency, and quality metrics.
نماذج Pydantic لتتبع استخدام المياه والكفاءة ومقاييس الجودة.
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, validator

# ==================== Enumerations ====================


class WaterSourceType(str, Enum):
    """Water source type enumeration / تعداد أنواع مصادر المياه"""

    WELL = "WELL"  # بئر
    BOREHOLE = "BOREHOLE"  # حفرة
    RIVER = "RIVER"  # نهر
    CANAL = "CANAL"  # قناة
    RESERVOIR = "RESERVOIR"  # خزان
    MUNICIPAL = "MUNICIPAL"  # بلدية
    RAINWATER = "RAINWATER"  # مياه الأمطار
    RECYCLED = "RECYCLED"  # معاد تدويرها
    DESALINATED = "DESALINATED"  # محلاة


class IrrigationMethod(str, Enum):
    """Irrigation method enumeration / تعداد طرق الري"""

    DRIP = "DRIP"  # بالتنقيط
    SPRINKLER = "SPRINKLER"  # بالرش
    SURFACE = "SURFACE"  # سطحي
    SUBSURFACE = "SUBSURFACE"  # تحت السطح
    CENTER_PIVOT = "CENTER_PIVOT"  # محوري
    FLOOD = "FLOOD"  # غمر
    FURROW = "FURROW"  # خنادق


class WaterQualityStatus(str, Enum):
    """Water quality status / حالة جودة المياه"""

    EXCELLENT = "EXCELLENT"  # ممتاز
    GOOD = "GOOD"  # جيد
    ACCEPTABLE = "ACCEPTABLE"  # مقبول
    POOR = "POOR"  # ضعيف
    UNACCEPTABLE = "UNACCEPTABLE"  # غير مقبول


# ==================== Water Source Models ====================


class WaterSource(BaseModel):
    """
    Water source information
    معلومات مصدر المياه
    """

    source_id: str = Field(
        ..., description="Unique source identifier / معرف المصدر الفريد"
    )
    source_type: WaterSourceType = Field(
        ..., description="Type of water source / نوع مصدر المياه"
    )
    name_en: str = Field(
        ..., description="Source name in English / اسم المصدر بالإنجليزية"
    )
    name_ar: str = Field(..., description="Source name in Arabic / اسم المصدر بالعربية")
    location: str | None = Field(None, description="Source location / موقع المصدر")
    depth_meters: float | None = Field(
        None, description="Depth in meters (for wells) / العمق بالأمتار (للآبار)"
    )
    capacity_cubic_meters: float | None = Field(
        None, description="Capacity in cubic meters / السعة بالمتر المكعب"
    )
    legal_permit_number: str | None = Field(
        None, description="Water rights permit number / رقم تصريح حقوق المياه"
    )
    permit_expiry_date: date | None = Field(
        None, description="Permit expiry date / تاريخ انتهاء التصريح"
    )
    max_daily_extraction_m3: float | None = Field(
        None, description="Maximum daily extraction (m³) / الحد الأقصى للاستخراج اليومي"
    )
    is_active: bool = Field(True, description="Source is active / المصدر نشط")
    notes: str | None = Field(None, description="Additional notes / ملاحظات إضافية")

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "WELL-001",
                "source_type": "WELL",
                "name_en": "North Field Well",
                "name_ar": "بئر الحقل الشمالي",
                "location": "N15.5527 E48.5164",
                "depth_meters": 120.0,
                "capacity_cubic_meters": 50000.0,
                "legal_permit_number": "YE-WR-2024-1234",
                "permit_expiry_date": "2026-12-31",
                "max_daily_extraction_m3": 500.0,
                "is_active": True,
                "notes": "Primary irrigation source for northern fields",
            }
        }


class WaterQualityTest(BaseModel):
    """
    Water quality test results
    نتائج اختبار جودة المياه
    """

    test_id: str = Field(..., description="Test identifier / معرف الاختبار")
    source_id: str = Field(..., description="Water source ID / معرف مصدر المياه")
    test_date: date = Field(..., description="Test date / تاريخ الاختبار")
    laboratory: str | None = Field(None, description="Testing laboratory / المختبر")
    ph_level: float | None = Field(
        None, ge=0, le=14, description="pH level / مستوى الحموضة"
    )
    ec_ds_per_m: float | None = Field(
        None, description="Electrical conductivity (dS/m) / التوصيل الكهربائي"
    )
    tds_ppm: float | None = Field(
        None, description="Total dissolved solids (ppm) / المواد الصلبة الذائبة الكلية"
    )
    salinity_ppm: float | None = Field(None, description="Salinity (ppm) / الملوحة")
    nitrate_ppm: float | None = Field(
        None, description="Nitrate concentration (ppm) / تركيز النترات"
    )
    phosphate_ppm: float | None = Field(
        None, description="Phosphate concentration (ppm) / تركيز الفوسفات"
    )
    bacterial_count: int | None = Field(
        None, description="Bacterial count / عدد البكتيريا"
    )
    heavy_metals: dict[str, float] | None = Field(
        None, description="Heavy metals (ppm) / المعادن الثقيلة"
    )
    quality_status: WaterQualityStatus = Field(
        ..., description="Overall quality status / حالة الجودة الإجمالية"
    )
    meets_irrigation_standards: bool = Field(
        ..., description="Meets irrigation standards / تلبي معايير الري"
    )
    notes: str | None = Field(None, description="Test notes / ملاحظات الاختبار")

    class Config:
        json_schema_extra = {
            "example": {
                "test_id": "WQ-2024-001",
                "source_id": "WELL-001",
                "test_date": "2024-12-15",
                "laboratory": "Yemen Agricultural Laboratory",
                "ph_level": 7.2,
                "ec_ds_per_m": 1.5,
                "tds_ppm": 960,
                "salinity_ppm": 450,
                "nitrate_ppm": 8.5,
                "phosphate_ppm": 0.3,
                "bacterial_count": 10,
                "heavy_metals": {"lead": 0.001, "cadmium": 0.0005},
                "quality_status": "GOOD",
                "meets_irrigation_standards": True,
                "notes": "Water quality suitable for drip irrigation",
            }
        }


# ==================== Water Usage Models ====================


class WaterUsageMetric(BaseModel):
    """
    Water usage measurement
    قياس استخدام المياه
    """

    usage_id: str = Field(
        ..., description="Usage record identifier / معرف سجل الاستخدام"
    )
    source_id: str = Field(..., description="Water source ID / معرف مصدر المياه")
    field_id: str | None = Field(None, description="Field identifier / معرف الحقل")
    crop_type: str | None = Field(None, description="Crop type / نوع المحصول")
    measurement_date: date = Field(..., description="Measurement date / تاريخ القياس")
    volume_cubic_meters: float = Field(
        ..., gt=0, description="Water volume used (m³) / حجم المياه المستخدم"
    )
    crop_area_hectares: float | None = Field(
        None, gt=0, description="Irrigated area (ha) / المساحة المروية"
    )
    irrigation_method: IrrigationMethod | None = Field(
        None, description="Irrigation method / طريقة الري"
    )
    duration_hours: float | None = Field(
        None, gt=0, description="Irrigation duration (hours) / مدة الري"
    )
    flow_rate_m3_per_hour: float | None = Field(
        None, description="Flow rate (m³/h) / معدل التدفق"
    )

    @validator("flow_rate_m3_per_hour", always=True)
    def calculate_flow_rate(cls, v, values):
        """Calculate flow rate if not provided / حساب معدل التدفق إذا لم يتم توفيره"""
        if v is None and "volume_cubic_meters" in values and "duration_hours" in values:
            if values["duration_hours"] and values["duration_hours"] > 0:
                return values["volume_cubic_meters"] / values["duration_hours"]
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "usage_id": "WU-2024-12-001",
                "source_id": "WELL-001",
                "field_id": "FIELD-N1",
                "crop_type": "Tomatoes",
                "measurement_date": "2024-12-15",
                "volume_cubic_meters": 125.5,
                "crop_area_hectares": 2.5,
                "irrigation_method": "DRIP",
                "duration_hours": 6.0,
                "flow_rate_m3_per_hour": 20.92,
            }
        }


class IrrigationEfficiency(BaseModel):
    """
    Irrigation efficiency metrics
    مقاييس كفاءة الري
    """

    efficiency_id: str = Field(
        ..., description="Efficiency record ID / معرف سجل الكفاءة"
    )
    field_id: str = Field(..., description="Field identifier / معرف الحقل")
    measurement_period_start: date = Field(
        ..., description="Period start date / تاريخ بداية الفترة"
    )
    measurement_period_end: date = Field(
        ..., description="Period end date / تاريخ نهاية الفترة"
    )
    irrigation_method: IrrigationMethod = Field(
        ..., description="Irrigation method / طريقة الري"
    )
    water_applied_m3: float = Field(
        ..., gt=0, description="Total water applied (m³) / المياه المطبقة الكلية"
    )
    water_stored_in_root_zone_m3: float = Field(
        ..., gt=0, description="Water in root zone (m³) / المياه في منطقة الجذور"
    )
    application_efficiency_percent: float = Field(
        ..., ge=0, le=100, description="Application efficiency (%) / كفاءة التطبيق"
    )
    distribution_uniformity_percent: float | None = Field(
        None, ge=0, le=100, description="Distribution uniformity (%) / توحيد التوزيع"
    )
    water_use_efficiency_kg_per_m3: float | None = Field(
        None, description="Water use efficiency (kg/m³) / كفاءة استخدام المياه"
    )
    crop_yield_kg: float | None = Field(
        None, description="Crop yield (kg) / إنتاج المحصول"
    )
    irrigation_scheduling_method: str | None = Field(
        None, description="Scheduling method / طريقة الجدولة"
    )
    soil_moisture_monitoring: bool = Field(
        False, description="Uses soil moisture sensors / يستخدم أجهزة رطوبة التربة"
    )
    weather_based_scheduling: bool = Field(
        False, description="Weather-based scheduling / جدولة بناءً على الطقس"
    )
    notes: str | None = Field(None, description="Additional notes / ملاحظات إضافية")

    @validator("application_efficiency_percent", always=True)
    def calculate_efficiency(cls, v, values):
        """Calculate efficiency if not provided / حساب الكفاءة إذا لم يتم توفيرها"""
        if v is None or v == 0:
            if (
                "water_applied_m3" in values
                and "water_stored_in_root_zone_m3" in values
            ):
                if values["water_applied_m3"] > 0:
                    return (
                        values["water_stored_in_root_zone_m3"]
                        / values["water_applied_m3"]
                    ) * 100
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "efficiency_id": "IE-2024-Q4-001",
                "field_id": "FIELD-N1",
                "measurement_period_start": "2024-10-01",
                "measurement_period_end": "2024-12-31",
                "irrigation_method": "DRIP",
                "water_applied_m3": 5000,
                "water_stored_in_root_zone_m3": 4250,
                "application_efficiency_percent": 85.0,
                "distribution_uniformity_percent": 92.0,
                "water_use_efficiency_kg_per_m3": 8.5,
                "crop_yield_kg": 42500,
                "irrigation_scheduling_method": "Soil moisture sensors + weather data",
                "soil_moisture_monitoring": True,
                "weather_based_scheduling": True,
                "notes": "High efficiency due to drip irrigation and precision scheduling",
            }
        }


class RainfallHarvesting(BaseModel):
    """
    Rainwater harvesting record
    سجل حصاد مياه الأمطار
    """

    harvest_id: str = Field(..., description="Harvest record ID / معرف سجل الحصاد")
    collection_date: date = Field(..., description="Collection date / تاريخ التجميع")
    rainfall_mm: float = Field(
        ..., ge=0, description="Rainfall amount (mm) / كمية الأمطار"
    )
    collection_area_m2: float = Field(
        ..., gt=0, description="Collection area (m²) / منطقة التجميع"
    )
    collected_volume_m3: float = Field(
        ..., ge=0, description="Collected volume (m³) / الحجم المجمع"
    )
    storage_location: str = Field(..., description="Storage location / موقع التخزين")
    storage_capacity_m3: float = Field(
        ..., gt=0, description="Storage capacity (m³) / سعة التخزين"
    )
    current_storage_level_m3: float = Field(
        ..., ge=0, description="Current level (m³) / المستوى الحالي"
    )
    water_treatment_applied: bool = Field(
        False, description="Treatment applied / تم تطبيق المعالجة"
    )
    treatment_method: str | None = Field(
        None, description="Treatment method / طريقة المعالجة"
    )
    intended_use: str = Field(..., description="Intended use / الاستخدام المقصود")
    notes: str | None = Field(None, description="Additional notes / ملاحظات إضافية")

    @validator("collected_volume_m3", always=True)
    def estimate_collected_volume(cls, v, values):
        """Estimate collected volume if not provided / تقدير الحجم المجمع إذا لم يتم توفيره"""
        if v is None or v == 0:
            if "rainfall_mm" in values and "collection_area_m2" in values:
                # Simple calculation: rainfall (mm) × area (m²) × collection efficiency (0.8)
                return (
                    (values["rainfall_mm"] / 1000) * values["collection_area_m2"] * 0.8
                )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "harvest_id": "RH-2024-12-001",
                "collection_date": "2024-12-15",
                "rainfall_mm": 25.5,
                "collection_area_m2": 500,
                "collected_volume_m3": 10.2,
                "storage_location": "North Field Tank",
                "storage_capacity_m3": 100,
                "current_storage_level_m3": 65.3,
                "water_treatment_applied": True,
                "treatment_method": "Filtration + UV treatment",
                "intended_use": "Supplementary irrigation",
                "notes": "Good rainfall event, tank now at 65% capacity",
            }
        }


# ==================== Water Efficiency Scoring ====================


class WaterEfficiencyScore(BaseModel):
    """
    Overall water efficiency assessment
    تقييم كفاءة المياه الإجمالي
    """

    assessment_id: str = Field(..., description="Assessment ID / معرف التقييم")
    farm_id: str = Field(..., description="Farm identifier / معرف المزرعة")
    assessment_date: date = Field(..., description="Assessment date / تاريخ التقييم")
    assessment_period_start: date = Field(
        ..., description="Period start / بداية الفترة"
    )
    assessment_period_end: date = Field(..., description="Period end / نهاية الفترة")

    # Water sources
    total_water_sources: int = Field(
        ..., ge=0, description="Total water sources / مجموع مصادر المياه"
    )
    sources_with_legal_permits: int = Field(
        ..., ge=0, description="Sources with permits / المصادر بتصاريح"
    )

    # Water usage
    total_water_used_m3: float = Field(
        ..., ge=0, description="Total water used (m³) / المياه المستخدمة الكلية"
    )
    total_irrigated_area_ha: float = Field(
        ..., gt=0, description="Irrigated area (ha) / المساحة المروية"
    )
    water_use_per_hectare_m3: float = Field(
        ..., ge=0, description="Water per hectare (m³/ha) / المياه لكل هكتار"
    )

    # Efficiency metrics
    average_application_efficiency: float = Field(
        ..., ge=0, le=100, description="Avg efficiency (%) / الكفاءة المتوسطة"
    )
    drip_irrigation_percentage: float = Field(
        ..., ge=0, le=100, description="Drip irrigation (%) / نسبة الري بالتنقيط"
    )
    soil_moisture_monitoring_coverage: float = Field(
        ..., ge=0, le=100, description="Sensor coverage (%) / تغطية الأجهزة"
    )

    # Rainwater harvesting
    rainwater_harvested_m3: float = Field(
        0, ge=0, description="Rainwater harvested (m³) / مياه الأمطار المحصودة"
    )
    rainwater_percentage: float = Field(
        0, ge=0, le=100, description="Rainwater % / نسبة مياه الأمطار"
    )

    # Water quality
    water_quality_tests_conducted: int = Field(
        0, ge=0, description="Quality tests / اختبارات الجودة"
    )
    sources_meeting_standards: int = Field(
        0, ge=0, description="Sources meeting standards / المصادر المطابقة"
    )

    # Overall score
    overall_spring_score: float = Field(
        ..., ge=0, le=100, description="Overall SPRING score / درجة SPRING الإجمالية"
    )
    compliance_level: str = Field(..., description="Compliance level / مستوى الامتثال")

    recommendations_en: list[str] = Field(
        default_factory=list, description="Recommendations (EN) / التوصيات"
    )
    recommendations_ar: list[str] = Field(
        default_factory=list, description="Recommendations (AR) / التوصيات"
    )

    @validator("water_use_per_hectare_m3", always=True)
    def calculate_water_per_hectare(cls, v, values):
        """Calculate water use per hectare / حساب استخدام المياه لكل هكتار"""
        if v is None or v == 0:
            if "total_water_used_m3" in values and "total_irrigated_area_ha" in values:
                if values["total_irrigated_area_ha"] > 0:
                    return (
                        values["total_water_used_m3"]
                        / values["total_irrigated_area_ha"]
                    )
        return v

    @validator("rainwater_percentage", always=True)
    def calculate_rainwater_percentage(cls, v, values):
        """Calculate rainwater percentage / حساب نسبة مياه الأمطار"""
        if v is None or v == 0:
            if "rainwater_harvested_m3" in values and "total_water_used_m3" in values:
                if values["total_water_used_m3"] > 0:
                    return (
                        values["rainwater_harvested_m3"] / values["total_water_used_m3"]
                    ) * 100
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "SPRING-2024-Q4",
                "farm_id": "FARM-YE-001",
                "assessment_date": "2024-12-31",
                "assessment_period_start": "2024-10-01",
                "assessment_period_end": "2024-12-31",
                "total_water_sources": 3,
                "sources_with_legal_permits": 3,
                "total_water_used_m3": 15000,
                "total_irrigated_area_ha": 10.0,
                "water_use_per_hectare_m3": 1500,
                "average_application_efficiency": 82.0,
                "drip_irrigation_percentage": 85.0,
                "soil_moisture_monitoring_coverage": 75.0,
                "rainwater_harvested_m3": 500,
                "rainwater_percentage": 3.33,
                "water_quality_tests_conducted": 6,
                "sources_meeting_standards": 3,
                "overall_spring_score": 85.5,
                "compliance_level": "EXCELLENT",
                "recommendations_en": [
                    "Increase rainwater harvesting capacity",
                    "Install soil moisture sensors in remaining 25% of fields",
                    "Continue quarterly water quality testing",
                ],
                "recommendations_ar": [
                    "زيادة سعة حصاد مياه الأمطار",
                    "تركيب أجهزة استشعار رطوبة التربة في 25% المتبقية من الحقول",
                    "الاستمرار في اختبارات جودة المياه الفصلية",
                ],
            }
        }


# ==================== Helper Functions ====================


def calculate_water_balance(
    total_input_m3: float,
    crop_evapotranspiration_m3: float,
    runoff_m3: float = 0,
    deep_percolation_m3: float = 0,
) -> dict[str, float]:
    """
    Calculate water balance for a field
    حساب توازن المياه للحقل

    Args:
        total_input_m3: Total water input (irrigation + rainfall)
        crop_evapotranspiration_m3: Crop water consumption
        runoff_m3: Surface runoff
        deep_percolation_m3: Deep percolation losses

    Returns:
        Water balance components
    """
    total_output = crop_evapotranspiration_m3 + runoff_m3 + deep_percolation_m3
    storage_change = total_input_m3 - total_output

    efficiency = (
        (crop_evapotranspiration_m3 / total_input_m3 * 100) if total_input_m3 > 0 else 0
    )

    return {
        "total_input_m3": total_input_m3,
        "crop_evapotranspiration_m3": crop_evapotranspiration_m3,
        "runoff_m3": runoff_m3,
        "deep_percolation_m3": deep_percolation_m3,
        "total_output_m3": total_output,
        "storage_change_m3": storage_change,
        "beneficial_use_efficiency_percent": round(efficiency, 2),
    }


def classify_water_efficiency(efficiency_percent: float) -> tuple[str, str]:
    """
    Classify water efficiency level
    تصنيف مستوى كفاءة المياه

    Args:
        efficiency_percent: Efficiency percentage

    Returns:
        Tuple of (level_en, level_ar)
    """
    if efficiency_percent >= 85:
        return ("EXCELLENT", "ممتاز")
    elif efficiency_percent >= 75:
        return ("GOOD", "جيد")
    elif efficiency_percent >= 65:
        return ("ACCEPTABLE", "مقبول")
    elif efficiency_percent >= 50:
        return ("NEEDS_IMPROVEMENT", "يحتاج تحسين")
    else:
        return ("POOR", "ضعيف")
