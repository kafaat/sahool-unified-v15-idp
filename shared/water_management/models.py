"""
Water Management Models - نماذج إدارة المياه
=============================================

Data models for comprehensive water management including:
- Water sources (wells, tanks, canals)
- Water rights and allocations
- Water quality monitoring
- Irrigation records

Compliant with Saudi water regulations:
- Ministry of Environment, Water and Agriculture (MEWA) requirements
- National Water Company (NWC) standards
- Groundwater conservation regulations

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

# =============================================================================
# Enumerations - التعدادات
# =============================================================================


class WaterSourceType(StrEnum):
    """Type of water source - نوع مصدر المياه"""

    WELL = "well"  # بئر
    ARTESIAN_WELL = "artesian_well"  # بئر ارتوازي
    TANK = "tank"  # خزان
    RESERVOIR = "reservoir"  # خزان كبير
    CANAL = "canal"  # قناة
    CHANNEL = "channel"  # مجرى
    RIVER = "river"  # نهر
    TREATED_WASTEWATER = "treated_wastewater"  # مياه صرف معالجة
    DESALINATED = "desalinated"  # مياه محلاة
    RAINWATER = "rainwater"  # مياه أمطار
    SPRING = "spring"  # ينبوع


class WaterSourceStatus(StrEnum):
    """Operational status of water source - حالة تشغيل مصدر المياه"""

    ACTIVE = "active"  # يعمل
    INACTIVE = "inactive"  # متوقف
    MAINTENANCE = "maintenance"  # صيانة
    SEASONAL = "seasonal"  # موسمي
    DEPLETED = "depleted"  # نضب
    CONTAMINATED = "contaminated"  # ملوث
    PERMIT_EXPIRED = "permit_expired"  # انتهت الرخصة
    SUSPENDED = "suspended"  # معلق


class WaterQualityClass(StrEnum):
    """Water quality classification per Saudi standards - تصنيف جودة المياه"""

    CLASS_A = "A"  # صالحة للشرب - Potable
    CLASS_B = "B"  # صالحة للري غير المقيد - Unrestricted irrigation
    CLASS_C = "C"  # صالحة للري المقيد - Restricted irrigation
    CLASS_D = "D"  # صالحة للري المحدود - Limited irrigation
    UNFIT = "unfit"  # غير صالحة - Unfit for use


class WaterRightType(StrEnum):
    """Type of water allocation right - نوع حق تخصيص المياه"""

    TRADITIONAL = "traditional"  # حق تقليدي
    LICENSED = "licensed"  # مرخص
    PERMIT = "permit"  # تصريح
    EMERGENCY = "emergency"  # طوارئ
    TEMPORARY = "temporary"  # مؤقت
    TRANSFERRED = "transferred"  # منقول


class AllocationPeriod(StrEnum):
    """Period for water allocation - فترة تخصيص المياه"""

    DAILY = "daily"  # يومي
    WEEKLY = "weekly"  # أسبوعي
    MONTHLY = "monthly"  # شهري
    SEASONAL = "seasonal"  # موسمي
    ANNUAL = "annual"  # سنوي


class IrrigationMethod(StrEnum):
    """Irrigation method - طريقة الري"""

    DRIP = "drip"  # ري بالتنقيط
    SPRINKLER = "sprinkler"  # ري بالرش
    CENTER_PIVOT = "center_pivot"  # ري محوري
    FLOOD = "flood"  # ري غمر
    FURROW = "furrow"  # ري بالأخاديد
    SUBSURFACE = "subsurface"  # ري تحت سطحي
    MANUAL = "manual"  # ري يدوي


class AlertSeverity(StrEnum):
    """Alert severity level - مستوى خطورة التنبيه"""

    INFO = "info"  # معلومات
    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # عالي
    CRITICAL = "critical"  # حرج


class ComplianceStatus(StrEnum):
    """Regulatory compliance status - حالة الامتثال التنظيمي"""

    COMPLIANT = "compliant"  # ممتثل
    NON_COMPLIANT = "non_compliant"  # غير ممتثل
    PENDING_REVIEW = "pending_review"  # قيد المراجعة
    EXEMPTED = "exempted"  # معفى
    WARNING = "warning"  # تحذير


class MeterType(StrEnum):
    """Water meter type - نوع عداد المياه"""

    MECHANICAL = "mechanical"  # ميكانيكي
    ULTRASONIC = "ultrasonic"  # فوق صوتي
    ELECTROMAGNETIC = "electromagnetic"  # كهرومغناطيسي
    SMART = "smart"  # ذكي
    MANUAL_READING = "manual_reading"  # قراءة يدوية


# =============================================================================
# Water Source Models - نماذج مصادر المياه
# =============================================================================


@dataclass
class GeoLocation:
    """Geographic location - الموقع الجغرافي"""

    lat: float
    lng: float
    elevation_m: float | None = None
    accuracy_m: float | None = None


@dataclass
class WaterMeter:
    """
    Water meter device - عداد المياه

    Tracks water flow and consumption for regulatory compliance.
    """

    id: str
    source_id: str
    tenant_id: str

    # Device info
    name: str
    name_ar: str
    meter_type: MeterType
    model: str
    serial_number: str
    manufacturer: str

    # Readings
    current_reading_m3: float = 0.0
    last_reading_at: datetime | None = None
    last_reading_m3: float = 0.0

    # Calibration
    calibration_factor: float = 1.0
    last_calibrated_at: datetime | None = None
    calibration_due_at: datetime | None = None

    # Status
    is_active: bool = True
    is_certified: bool = True  # MEWA certification
    certification_expiry: date | None = None

    # Installation
    installed_at: datetime | None = None
    installed_by: str | None = None

    def calculate_consumption(self, previous_reading: float) -> float:
        """Calculate consumption since previous reading"""
        if self.current_reading_m3 < previous_reading:
            # Meter rollover
            return self.current_reading_m3 + (999999 - previous_reading)
        return (self.current_reading_m3 - previous_reading) * self.calibration_factor

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "meter_type": self.meter_type.value,
            "model": self.model,
            "serial_number": self.serial_number,
            "current_reading_m3": self.current_reading_m3,
            "last_reading_at": (self.last_reading_at.isoformat() if self.last_reading_at else None),
            "is_active": self.is_active,
            "is_certified": self.is_certified,
        }


@dataclass
class WaterSource:
    """
    Water source - مصدر المياه

    Represents any water source (well, tank, canal, etc.) used for irrigation.
    Compliant with MEWA well registration requirements.
    """

    id: str
    tenant_id: str
    farm_id: str

    # Basic info
    name: str
    name_ar: str
    source_type: WaterSourceType
    status: WaterSourceStatus = WaterSourceStatus.ACTIVE

    # Location
    location: GeoLocation | None = None
    governorate: str | None = None  # المحافظة
    region: str | None = None  # المنطقة

    # Capacity and levels
    max_capacity_m3: float | None = None  # السعة القصوى
    current_level_m3: float | None = None  # المستوى الحالي
    min_operational_level_m3: float | None = None  # الحد الأدنى للتشغيل
    static_water_level_m: float | None = None  # مستوى المياه الساكنة (for wells)
    dynamic_water_level_m: float | None = None  # مستوى المياه الديناميكي

    # Well-specific
    well_depth_m: float | None = None  # عمق البئر
    casing_diameter_mm: float | None = None  # قطر التبطين
    aquifer_name: str | None = None  # اسم طبقة المياه الجوفية
    aquifer_name_ar: str | None = None

    # Pump info
    pump_installed: bool = False
    pump_capacity_m3_hr: float | None = None  # سعة المضخة
    pump_power_kw: float | None = None
    pump_efficiency: float | None = None  # 0-1

    # Meters
    meter: WaterMeter | None = None
    has_meter: bool = False

    # Quality
    water_quality_class: WaterQualityClass = WaterQualityClass.CLASS_B
    last_quality_test_at: datetime | None = None
    salinity_ppm: float | None = None  # الملوحة
    ph_level: float | None = None

    # Licensing (MEWA requirements)
    license_number: str | None = None  # رقم الرخصة
    license_issued_at: date | None = None
    license_expiry_at: date | None = None
    licensed_extraction_m3_day: float | None = None  # الكمية المرخصة يومياً
    licensed_extraction_m3_year: float | None = None  # الكمية المرخصة سنوياً

    # Usage tracking
    total_extracted_m3_ytd: float = 0.0  # المستخرج هذا العام
    avg_daily_extraction_m3: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""
    notes_ar: str = ""

    @property
    def is_license_valid(self) -> bool:
        """Check if license is valid"""
        if not self.license_expiry_at:
            return False
        return self.license_expiry_at >= date.today()

    @property
    def extraction_remaining_m3_year(self) -> float | None:
        """Calculate remaining annual extraction allowance"""
        if self.licensed_extraction_m3_year is None:
            return None
        return max(0, self.licensed_extraction_m3_year - self.total_extracted_m3_ytd)

    @property
    def extraction_utilization_percent(self) -> float | None:
        """Calculate percentage of annual allocation used"""
        if not self.licensed_extraction_m3_year:
            return None
        return (self.total_extracted_m3_ytd / self.licensed_extraction_m3_year) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "source_type": self.source_type.value,
            "status": self.status.value,
            "location": (
                {
                    "lat": self.location.lat,
                    "lng": self.location.lng,
                    "elevation_m": self.location.elevation_m,
                }
                if self.location
                else None
            ),
            "capacity": {
                "max_capacity_m3": self.max_capacity_m3,
                "current_level_m3": self.current_level_m3,
                "min_operational_level_m3": self.min_operational_level_m3,
            },
            "well_info": {
                "depth_m": self.well_depth_m,
                "static_water_level_m": self.static_water_level_m,
                "dynamic_water_level_m": self.dynamic_water_level_m,
                "aquifer_name": self.aquifer_name,
                "aquifer_name_ar": self.aquifer_name_ar,
            }
            if self.source_type in (WaterSourceType.WELL, WaterSourceType.ARTESIAN_WELL)
            else None,
            "pump": {
                "installed": self.pump_installed,
                "capacity_m3_hr": self.pump_capacity_m3_hr,
                "power_kw": self.pump_power_kw,
                "efficiency": self.pump_efficiency,
            },
            "quality": {
                "class": self.water_quality_class.value,
                "last_test_at": (self.last_quality_test_at.isoformat() if self.last_quality_test_at else None),
                "salinity_ppm": self.salinity_ppm,
                "ph_level": self.ph_level,
            },
            "license": {
                "number": self.license_number,
                "expiry_at": (self.license_expiry_at.isoformat() if self.license_expiry_at else None),
                "licensed_extraction_m3_day": self.licensed_extraction_m3_day,
                "licensed_extraction_m3_year": self.licensed_extraction_m3_year,
                "is_valid": self.is_license_valid,
            },
            "usage": {
                "total_extracted_m3_ytd": self.total_extracted_m3_ytd,
                "avg_daily_extraction_m3": self.avg_daily_extraction_m3,
                "remaining_m3_year": self.extraction_remaining_m3_year,
                "utilization_percent": self.extraction_utilization_percent,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# =============================================================================
# Water Rights and Allocation Models - نماذج حقوق المياه والتخصيص
# =============================================================================


@dataclass
class WaterRight:
    """
    Water right / allocation permit - حق المياه / تصريح التخصيص

    Represents legal water allocation rights per Saudi regulations.
    """

    id: str
    tenant_id: str
    farm_id: str
    source_id: str | None = None

    # Right details
    right_type: WaterRightType = WaterRightType.LICENSED
    permit_number: str | None = None  # رقم التصريح
    issued_by: str | None = None  # الجهة المصدرة (MEWA, NWC)

    # Allocation amounts
    allocated_m3_day: float = 0.0  # الكمية المخصصة يومياً
    allocated_m3_month: float = 0.0
    allocated_m3_season: float = 0.0
    allocated_m3_year: float = 0.0

    # Validity
    valid_from: date | None = None
    valid_until: date | None = None
    is_renewable: bool = True

    # Usage
    used_m3_ytd: float = 0.0
    used_m3_current_period: float = 0.0
    allocation_period: AllocationPeriod = AllocationPeriod.ANNUAL

    # Conditions
    conditions_en: str = ""  # شروط الاستخدام
    conditions_ar: str = ""
    crop_restrictions: list[str] = field(default_factory=list)  # قيود المحاصيل
    area_restrictions_ha: float | None = None  # قيود المساحة

    # Transfer
    is_transferable: bool = False
    transferred_from_id: str | None = None
    transfer_date: date | None = None

    # Status
    status: ComplianceStatus = ComplianceStatus.COMPLIANT

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_valid(self) -> bool:
        """Check if water right is currently valid"""
        today = date.today()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True

    @property
    def remaining_allocation_m3(self) -> float:
        """Calculate remaining allocation for current period"""
        if self.allocation_period == AllocationPeriod.ANNUAL:
            return max(0, self.allocated_m3_year - self.used_m3_ytd)
        return max(0, self.allocated_m3_month - self.used_m3_current_period)

    @property
    def utilization_percent(self) -> float:
        """Calculate utilization percentage"""
        if self.allocation_period == AllocationPeriod.ANNUAL:
            if self.allocated_m3_year <= 0:
                return 0.0
            return (self.used_m3_ytd / self.allocated_m3_year) * 100
        if self.allocated_m3_month <= 0:
            return 0.0
        return (self.used_m3_current_period / self.allocated_m3_month) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "source_id": self.source_id,
            "right_type": self.right_type.value,
            "permit_number": self.permit_number,
            "issued_by": self.issued_by,
            "allocation": {
                "daily_m3": self.allocated_m3_day,
                "monthly_m3": self.allocated_m3_month,
                "seasonal_m3": self.allocated_m3_season,
                "annual_m3": self.allocated_m3_year,
                "period": self.allocation_period.value,
            },
            "validity": {
                "from": self.valid_from.isoformat() if self.valid_from else None,
                "until": self.valid_until.isoformat() if self.valid_until else None,
                "is_valid": self.is_valid,
                "is_renewable": self.is_renewable,
            },
            "usage": {
                "used_m3_ytd": self.used_m3_ytd,
                "used_m3_current_period": self.used_m3_current_period,
                "remaining_m3": self.remaining_allocation_m3,
                "utilization_percent": self.utilization_percent,
            },
            "conditions": {
                "en": self.conditions_en,
                "ar": self.conditions_ar,
                "crop_restrictions": self.crop_restrictions,
                "area_restrictions_ha": self.area_restrictions_ha,
            },
            "status": self.status.value,
        }


@dataclass
class WaterAllocation:
    """
    Water allocation record for a specific field/crop
    سجل تخصيص المياه لحقل/محصول معين
    """

    id: str
    tenant_id: str
    farm_id: str
    field_id: str
    water_right_id: str
    source_id: str | None = None

    # Crop info
    crop_type: str | None = None  # نوع المحصول
    crop_type_ar: str | None = None
    growing_season: str | None = None  # الموسم الزراعي
    area_ha: float = 0.0

    # Allocation
    allocated_m3: float = 0.0
    allocation_period: AllocationPeriod = AllocationPeriod.SEASONAL

    # Water requirement estimates
    estimated_requirement_m3: float = 0.0  # المتطلبات المائية المقدرة
    crop_coefficient_kc: float = 1.0  # معامل المحصول
    reference_et_mm_day: float | None = None  # التبخر-نتح المرجعي

    # Scheduling
    start_date: date | None = None
    end_date: date | None = None
    irrigation_method: IrrigationMethod = IrrigationMethod.DRIP

    # Priority
    priority: int = 5  # 1=highest, 10=lowest

    # Tracking
    consumed_m3: float = 0.0
    irrigation_count: int = 0
    last_irrigation_at: datetime | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def remaining_m3(self) -> float:
        """Calculate remaining allocation"""
        return max(0, self.allocated_m3 - self.consumed_m3)

    @property
    def utilization_percent(self) -> float:
        """Calculate utilization percentage"""
        if self.allocated_m3 <= 0:
            return 0.0
        return (self.consumed_m3 / self.allocated_m3) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "water_right_id": self.water_right_id,
            "source_id": self.source_id,
            "crop": {
                "type": self.crop_type,
                "type_ar": self.crop_type_ar,
                "season": self.growing_season,
                "area_ha": self.area_ha,
            },
            "allocation": {
                "allocated_m3": self.allocated_m3,
                "period": self.allocation_period.value,
                "consumed_m3": self.consumed_m3,
                "remaining_m3": self.remaining_m3,
                "utilization_percent": self.utilization_percent,
            },
            "water_requirement": {
                "estimated_m3": self.estimated_requirement_m3,
                "crop_coefficient_kc": self.crop_coefficient_kc,
                "reference_et_mm_day": self.reference_et_mm_day,
            },
            "irrigation": {
                "method": self.irrigation_method.value,
                "count": self.irrigation_count,
                "last_at": (self.last_irrigation_at.isoformat() if self.last_irrigation_at else None),
            },
            "priority": self.priority,
        }


# =============================================================================
# Water Quality Models - نماذج جودة المياه
# =============================================================================


@dataclass
class WaterQualityParameter:
    """Single water quality parameter - معامل جودة مياه واحد"""

    parameter: str  # e.g., "pH", "TDS", "EC"
    parameter_ar: str  # الاسم بالعربية
    value: float
    unit: str
    min_acceptable: float | None = None
    max_acceptable: float | None = None
    is_within_limits: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "parameter": self.parameter,
            "parameter_ar": self.parameter_ar,
            "value": self.value,
            "unit": self.unit,
            "min_acceptable": self.min_acceptable,
            "max_acceptable": self.max_acceptable,
            "is_within_limits": self.is_within_limits,
        }


@dataclass
class WaterQualityTest:
    """
    Water quality test result - نتيجة اختبار جودة المياه

    Follows Saudi standards for irrigation water quality.
    """

    id: str
    source_id: str
    tenant_id: str
    tested_at: datetime

    # Lab info
    lab_name: str | None = None
    lab_name_ar: str | None = None
    lab_certificate_no: str | None = None
    sample_id: str | None = None
    sampled_by: str | None = None

    # Classification
    quality_class: WaterQualityClass = WaterQualityClass.CLASS_B

    # Key parameters
    ph: float | None = None  # 6.5-8.5 acceptable
    electrical_conductivity_ds_m: float | None = None  # الموصلية الكهربائية
    tds_ppm: float | None = None  # المواد الصلبة الذائبة
    salinity_ppm: float | None = None  # الملوحة
    sar: float | None = None  # Sodium Adsorption Ratio - نسبة امتصاص الصوديوم
    hardness_ppm: float | None = None  # عسر الماء

    # Nutrients
    nitrate_ppm: float | None = None  # النترات
    phosphate_ppm: float | None = None  # الفوسفات
    potassium_ppm: float | None = None  # البوتاسيوم

    # Ions
    sodium_ppm: float | None = None  # الصوديوم
    calcium_ppm: float | None = None  # الكالسيوم
    magnesium_ppm: float | None = None  # المغنيسيوم
    chloride_ppm: float | None = None  # الكلوريد
    bicarbonate_ppm: float | None = None  # البيكربونات
    sulfate_ppm: float | None = None  # الكبريتات
    boron_ppm: float | None = None  # البورون

    # Microbial (for treated wastewater)
    total_coliform_cfu: float | None = None  # البكتيريا القولونية
    fecal_coliform_cfu: float | None = None
    e_coli_cfu: float | None = None

    # Heavy metals
    lead_ppm: float | None = None
    cadmium_ppm: float | None = None
    arsenic_ppm: float | None = None
    mercury_ppm: float | None = None

    # All parameters
    parameters: list[WaterQualityParameter] = field(default_factory=list)

    # Assessment
    suitable_for_irrigation: bool = True
    suitable_crops: list[str] = field(default_factory=list)
    unsuitable_crops: list[str] = field(default_factory=list)
    recommendations_en: str = ""
    recommendations_ar: str = ""

    # Metadata
    report_url: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def classify_water(self) -> WaterQualityClass:
        """
        Classify water quality based on Saudi standards.
        تصنيف جودة المياه وفق المعايير السعودية
        """
        # Classification based on EC and TDS
        if self.electrical_conductivity_ds_m is not None:
            ec = self.electrical_conductivity_ds_m
            if ec <= 0.7:
                return WaterQualityClass.CLASS_A
            elif ec <= 3.0:
                return WaterQualityClass.CLASS_B
            elif ec <= 6.0:
                return WaterQualityClass.CLASS_C
            elif ec <= 10.0:
                return WaterQualityClass.CLASS_D
            else:
                return WaterQualityClass.UNFIT

        if self.tds_ppm is not None:
            tds = self.tds_ppm
            if tds <= 450:
                return WaterQualityClass.CLASS_A
            elif tds <= 2000:
                return WaterQualityClass.CLASS_B
            elif tds <= 4000:
                return WaterQualityClass.CLASS_C
            elif tds <= 6000:
                return WaterQualityClass.CLASS_D
            else:
                return WaterQualityClass.UNFIT

        return WaterQualityClass.CLASS_B  # Default

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "tenant_id": self.tenant_id,
            "tested_at": self.tested_at.isoformat(),
            "lab": {
                "name": self.lab_name,
                "name_ar": self.lab_name_ar,
                "certificate_no": self.lab_certificate_no,
                "sample_id": self.sample_id,
            },
            "quality_class": self.quality_class.value,
            "key_parameters": {
                "ph": self.ph,
                "ec_ds_m": self.electrical_conductivity_ds_m,
                "tds_ppm": self.tds_ppm,
                "salinity_ppm": self.salinity_ppm,
                "sar": self.sar,
            },
            "nutrients": {
                "nitrate_ppm": self.nitrate_ppm,
                "phosphate_ppm": self.phosphate_ppm,
                "potassium_ppm": self.potassium_ppm,
            },
            "ions": {
                "sodium_ppm": self.sodium_ppm,
                "calcium_ppm": self.calcium_ppm,
                "magnesium_ppm": self.magnesium_ppm,
                "chloride_ppm": self.chloride_ppm,
            },
            "parameters": [p.to_dict() for p in self.parameters],
            "assessment": {
                "suitable_for_irrigation": self.suitable_for_irrigation,
                "suitable_crops": self.suitable_crops,
                "unsuitable_crops": self.unsuitable_crops,
                "recommendations_en": self.recommendations_en,
                "recommendations_ar": self.recommendations_ar,
            },
        }


# =============================================================================
# Water Consumption and Irrigation Records - سجلات استهلاك المياه والري
# =============================================================================


@dataclass
class WaterConsumptionRecord:
    """
    Water consumption record - سجل استهلاك المياه

    Records water usage for regulatory reporting and analysis.
    """

    id: str
    tenant_id: str
    farm_id: str
    source_id: str
    field_id: str | None = None
    allocation_id: str | None = None

    # Time period
    period_start: datetime | None = None
    period_end: datetime | None = None

    # Consumption
    volume_m3: float = 0.0
    meter_reading_start: float | None = None
    meter_reading_end: float | None = None

    # Irrigation details
    irrigation_method: IrrigationMethod | None = None
    duration_hours: float | None = None
    flow_rate_m3_hr: float | None = None

    # Purpose
    purpose: str = "irrigation"  # irrigation, livestock, processing, domestic
    purpose_ar: str = "ري"
    crop_type: str | None = None

    # Cost tracking
    cost_sar: Decimal | None = None  # التكلفة بالريال
    energy_kwh: float | None = None  # استهلاك الطاقة

    # Recording
    recorded_by: str | None = None
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_estimated: bool = False

    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "source_id": self.source_id,
            "field_id": self.field_id,
            "allocation_id": self.allocation_id,
            "period": {
                "start": (self.period_start.isoformat() if self.period_start else None),
                "end": self.period_end.isoformat() if self.period_end else None,
            },
            "consumption": {
                "volume_m3": self.volume_m3,
                "meter_reading_start": self.meter_reading_start,
                "meter_reading_end": self.meter_reading_end,
            },
            "irrigation": {
                "method": (self.irrigation_method.value if self.irrigation_method else None),
                "duration_hours": self.duration_hours,
                "flow_rate_m3_hr": self.flow_rate_m3_hr,
            },
            "purpose": self.purpose,
            "purpose_ar": self.purpose_ar,
            "crop_type": self.crop_type,
            "cost_sar": float(self.cost_sar) if self.cost_sar else None,
            "energy_kwh": self.energy_kwh,
            "recorded_at": self.recorded_at.isoformat(),
            "is_estimated": self.is_estimated,
        }


@dataclass
class IrrigationEvent:
    """
    Single irrigation event - حدث ري واحد

    Records detailed irrigation application for efficiency tracking.
    """

    id: str
    tenant_id: str
    farm_id: str
    field_id: str
    source_id: str
    allocation_id: str | None = None

    # Timing
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_minutes: int = 0

    # Water applied
    volume_m3: float = 0.0
    depth_mm: float = 0.0  # Water depth applied
    area_irrigated_ha: float = 0.0

    # Method
    irrigation_method: IrrigationMethod = IrrigationMethod.DRIP

    # Equipment
    equipment_id: str | None = None
    equipment_type: str | None = None  # pivot, pump, valve, etc.

    # Conditions
    soil_moisture_before: float | None = None  # % before irrigation
    soil_moisture_after: float | None = None  # % after irrigation
    target_soil_moisture: float | None = None

    # Weather at time of irrigation
    temperature_c: float | None = None
    humidity_percent: float | None = None
    wind_speed_ms: float | None = None
    et_mm: float | None = None  # Evapotranspiration

    # Efficiency
    uniformity_coefficient: float | None = None  # معامل التجانس
    application_efficiency: float | None = None  # كفاءة الإضافة

    # Decision basis
    trigger_type: str = "scheduled"  # scheduled, sensor, manual, advisory
    trigger_type_ar: str = "مجدول"
    advisory_id: str | None = None  # Link to irrigation advisory

    # Operator
    operator_id: str | None = None
    operator_name: str | None = None

    # Status
    status: str = "completed"  # scheduled, in_progress, completed, cancelled
    notes: str = ""
    notes_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "source_id": self.source_id,
            "timing": {
                "started_at": (self.started_at.isoformat() if self.started_at else None),
                "ended_at": self.ended_at.isoformat() if self.ended_at else None,
                "duration_minutes": self.duration_minutes,
            },
            "application": {
                "volume_m3": self.volume_m3,
                "depth_mm": self.depth_mm,
                "area_ha": self.area_irrigated_ha,
                "method": self.irrigation_method.value,
            },
            "soil_moisture": {
                "before": self.soil_moisture_before,
                "after": self.soil_moisture_after,
                "target": self.target_soil_moisture,
            },
            "weather": {
                "temperature_c": self.temperature_c,
                "humidity_percent": self.humidity_percent,
                "wind_speed_ms": self.wind_speed_ms,
                "et_mm": self.et_mm,
            },
            "efficiency": {
                "uniformity_coefficient": self.uniformity_coefficient,
                "application_efficiency": self.application_efficiency,
            },
            "trigger": {
                "type": self.trigger_type,
                "type_ar": self.trigger_type_ar,
                "advisory_id": self.advisory_id,
            },
            "status": self.status,
        }


# =============================================================================
# Alert Models - نماذج التنبيهات
# =============================================================================


@dataclass
class WaterAlert:
    """
    Water management alert - تنبيه إدارة المياه

    Alerts for various water-related conditions.
    """

    id: str
    tenant_id: str
    farm_id: str
    alert_type: str  # e.g., "low_level", "quality_issue", "quota_exceeded"

    # Optional identifiers
    source_id: str | None = None
    field_id: str | None = None

    # Alert details
    severity: AlertSeverity = AlertSeverity.MEDIUM

    # Messages
    title_en: str = ""
    title_ar: str = ""
    message_en: str = ""
    message_ar: str = ""

    # Context
    triggered_value: float | None = None
    threshold_value: float | None = None
    unit: str | None = None

    # Actions
    recommended_action_en: str = ""
    recommended_action_ar: str = ""

    # Status
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved: bool = False
    resolved_at: datetime | None = None
    resolution_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "source_id": self.source_id,
            "field_id": self.field_id,
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "title": {"en": self.title_en, "ar": self.title_ar},
            "message": {"en": self.message_en, "ar": self.message_ar},
            "context": {
                "triggered_value": self.triggered_value,
                "threshold_value": self.threshold_value,
                "unit": self.unit,
            },
            "recommended_action": {
                "en": self.recommended_action_en,
                "ar": self.recommended_action_ar,
            },
            "status": {
                "acknowledged": self.acknowledged,
                "acknowledged_by": self.acknowledged_by,
                "acknowledged_at": (self.acknowledged_at.isoformat() if self.acknowledged_at else None),
                "resolved": self.resolved,
                "resolved_at": (self.resolved_at.isoformat() if self.resolved_at else None),
            },
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Saudi Water Regulations Constants - ثوابت أنظمة المياه السعودية
# =============================================================================


@dataclass
class SaudiWaterStandards:
    """
    Saudi water quality and usage standards
    معايير جودة المياه والاستخدام السعودية
    """

    # EC thresholds (dS/m) for irrigation water classes
    EC_CLASS_A_MAX: float = 0.7
    EC_CLASS_B_MAX: float = 3.0
    EC_CLASS_C_MAX: float = 6.0
    EC_CLASS_D_MAX: float = 10.0

    # TDS thresholds (ppm)
    TDS_CLASS_A_MAX: float = 450
    TDS_CLASS_B_MAX: float = 2000
    TDS_CLASS_C_MAX: float = 4000
    TDS_CLASS_D_MAX: float = 6000

    # SAR limits for soil types
    SAR_CLAY_MAX: float = 6.0
    SAR_LOAM_MAX: float = 10.0
    SAR_SAND_MAX: float = 15.0

    # pH acceptable range
    PH_MIN: float = 6.5
    PH_MAX: float = 8.5

    # Boron limits (ppm) by crop sensitivity
    BORON_SENSITIVE_MAX: float = 0.5  # citrus, stone fruits
    BORON_MODERATE_MAX: float = 1.0  # most crops
    BORON_TOLERANT_MAX: float = 2.0  # date palm, cotton

    # Groundwater extraction limits (m3/ha/year) by region
    EXTRACTION_LIMIT_CENTRAL: float = 8000
    EXTRACTION_LIMIT_EASTERN: float = 10000
    EXTRACTION_LIMIT_WESTERN: float = 6000
    EXTRACTION_LIMIT_SOUTHERN: float = 7000
    EXTRACTION_LIMIT_NORTHERN: float = 7500

    # Water meter requirements
    METER_REQUIRED_WELL_DEPTH_M: float = 50  # Required for wells deeper than 50m
    METER_CALIBRATION_INTERVAL_MONTHS: int = 12

    # Reporting requirements
    CONSUMPTION_REPORT_FREQUENCY_DAYS: int = 90  # Quarterly
    QUALITY_TEST_FREQUENCY_MONTHS: int = 6  # Bi-annual

    @classmethod
    def get_extraction_limit(cls, region: str) -> float:
        """Get extraction limit for region"""
        limits = {
            "central": cls.EXTRACTION_LIMIT_CENTRAL,
            "الوسطى": cls.EXTRACTION_LIMIT_CENTRAL,
            "eastern": cls.EXTRACTION_LIMIT_EASTERN,
            "الشرقية": cls.EXTRACTION_LIMIT_EASTERN,
            "western": cls.EXTRACTION_LIMIT_WESTERN,
            "الغربية": cls.EXTRACTION_LIMIT_WESTERN,
            "southern": cls.EXTRACTION_LIMIT_SOUTHERN,
            "الجنوبية": cls.EXTRACTION_LIMIT_SOUTHERN,
            "northern": cls.EXTRACTION_LIMIT_NORTHERN,
            "الشمالية": cls.EXTRACTION_LIMIT_NORTHERN,
        }
        return limits.get(region.lower(), cls.EXTRACTION_LIMIT_CENTRAL)
