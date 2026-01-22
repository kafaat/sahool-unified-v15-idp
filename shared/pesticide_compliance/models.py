"""
Pesticide Compliance Models - نماذج بيانات سلامة المبيدات
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ComplianceStatus(str, Enum):
    """Compliance check status"""
    COMPLIANT = "compliant"  # آمن
    WARNING = "warning"  # تحذير
    VIOLATION = "violation"  # مخالفة
    CRITICAL = "critical"  # حرج


class PesticideCategory(str, Enum):
    """Pesticide category types"""
    INSECTICIDE = "insecticide"  # مبيد حشري
    FUNGICIDE = "fungicide"  # مبيد فطري
    HERBICIDE = "herbicide"  # مبيد أعشاب
    ACARICIDE = "acaricide"  # مبيد عناكب
    NEMATICIDE = "nematicide"  # مبيد نيماتودا
    RODENTICIDE = "rodenticide"  # مبيد قوارض
    MOLLUSCICIDE = "molluscicide"  # مبيد رخويات
    GROWTH_REGULATOR = "growth_regulator"  # منظم نمو
    ADJUVANT = "adjuvant"  # مادة مساعدة


class ToxicityClass(str, Enum):
    """WHO toxicity classification"""
    IA = "Ia"  # شديد الخطورة
    IB = "Ib"  # خطير جداً
    II = "II"  # خطير متوسط
    III = "III"  # خطير قليلاً
    U = "U"  # غير محتمل أن يشكل خطراً حاداً


class PPELevel(str, Enum):
    """Personal Protective Equipment levels"""
    MINIMAL = "minimal"  # الحد الأدنى
    STANDARD = "standard"  # قياسي
    ENHANCED = "enhanced"  # معزز
    MAXIMUM = "maximum"  # أقصى حماية


class MixCompatibility(str, Enum):
    """Tank mix compatibility status"""
    COMPATIBLE = "compatible"  # متوافق
    CAUTION = "caution"  # يحتاج حذر
    INCOMPATIBLE = "incompatible"  # غير متوافق
    UNKNOWN = "unknown"  # غير معروف


@dataclass
class PPERequirement:
    """Personal Protective Equipment requirements - متطلبات الحماية الشخصية"""
    level: PPELevel
    gloves: str  # نوع القفازات
    gloves_ar: str
    respirator: str  # نوع الكمامة
    respirator_ar: str
    eye_protection: str  # حماية العين
    eye_protection_ar: str
    clothing: str  # الملابس
    clothing_ar: str
    footwear: str  # الأحذية
    footwear_ar: str
    additional: list[str] = field(default_factory=list)
    additional_ar: list[str] = field(default_factory=list)


@dataclass
class Pesticide:
    """Pesticide product information - معلومات منتج المبيد"""
    id: str
    trade_name: str
    trade_name_ar: str
    active_ingredient: str
    active_ingredient_ar: str
    category: PesticideCategory
    toxicity_class: ToxicityClass

    # Safety intervals
    phi_days: int  # Pre-Harvest Interval (days) - فترة ما قبل الحصاد (أيام)
    rei_hours: int  # Re-Entry Interval (hours) - فترة إعادة الدخول (ساعات)

    # Application parameters
    max_applications_per_season: int  # أقصى عدد تطبيقات في الموسم
    min_days_between_applications: int  # الحد الأدنى للأيام بين التطبيقات

    # Target crops
    registered_crops: list[str]  # المحاصيل المسجلة

    # PPE requirements
    ppe_requirements: PPERequirement

    # Registration
    registration_number: str  # رقم التسجيل
    registration_country: str = "SA"  # بلد التسجيل
    is_organic_approved: bool = False  # معتمد للزراعة العضوية
    is_restricted: bool = False  # مقيد الاستخدام

    # Additional info
    formulation: str = ""  # صيغة المستحضر
    manufacturer: str = ""  # الشركة المصنعة
    notes: str = ""
    notes_ar: str = ""


@dataclass
class PesticideApplication:
    """Record of pesticide application - سجل تطبيق المبيد"""
    application_id: str
    tenant_id: str
    field_id: str
    pesticide_id: str

    # Application details
    application_date: datetime
    application_rate: float  # معدل التطبيق (لتر/هكتار أو كجم/هكتار)
    application_rate_unit: str  # L/ha, kg/ha, etc.
    area_treated_ha: float  # المساحة المعالجة

    # Target
    target_pest: str  # الآفة المستهدفة
    target_pest_ar: str
    crop: str
    growth_stage: str

    # Weather conditions at application
    temperature_c: float | None = None
    humidity_percent: float | None = None
    wind_speed_kmh: float | None = None
    wind_direction: str | None = None

    # Applicator info
    applicator_id: str | None = None
    applicator_name: str | None = None
    application_method: str = "sprayer"  # sprayer, drone, aerial, etc.

    # Tank mix
    tank_mix_products: list[str] = field(default_factory=list)

    # Compliance
    phi_expiry_date: datetime | None = None
    rei_expiry_time: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""


@dataclass
class PHIViolation:
    """Pre-Harvest Interval violation - انتهاك فترة ما قبل الحصاد"""
    field_id: str
    pesticide_id: str
    pesticide_name: str
    pesticide_name_ar: str
    application_date: datetime
    phi_days: int
    earliest_harvest_date: datetime
    planned_harvest_date: datetime
    days_remaining: int

    status: ComplianceStatus

    message_en: str
    message_ar: str

    # Recommendations
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)


@dataclass
class REIViolation:
    """Re-Entry Interval violation - انتهاك فترة إعادة الدخول"""
    field_id: str
    pesticide_id: str
    pesticide_name: str
    pesticide_name_ar: str
    application_date: datetime
    rei_hours: int
    safe_entry_time: datetime

    status: ComplianceStatus

    message_en: str
    message_ar: str

    # PPE for early entry
    early_entry_ppe: PPERequirement | None = None


@dataclass
class TankMixCompatibility:
    """Tank mix compatibility check result - نتيجة فحص توافق الخلط"""
    product_a_id: str
    product_a_name: str
    product_b_id: str
    product_b_name: str

    compatibility: MixCompatibility

    message_en: str
    message_ar: str

    # Warnings
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)

    # If compatible, mixing order
    mixing_order: list[str] = field(default_factory=list)


@dataclass
class SprayDriftRisk:
    """Spray drift risk assessment - تقييم مخاطر انجراف الرش"""
    field_id: str
    assessment_time: datetime

    # Weather conditions
    wind_speed_kmh: float
    wind_direction: str
    temperature_c: float
    humidity_percent: float
    delta_t: float  # Temperature - Wet bulb temperature

    # Risk assessment
    risk_level: str  # low, medium, high, extreme
    risk_level_ar: str

    # Buffer zones
    recommended_buffer_m: int  # المنطقة العازلة الموصى بها (متر)

    # Recommendations
    can_spray: bool
    message_en: str
    message_ar: str

    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)


@dataclass
class ComplianceCheck:
    """Overall compliance check result - نتيجة فحص الامتثال الشاملة"""
    field_id: str
    check_date: datetime

    # Status
    overall_status: ComplianceStatus

    # Individual checks
    phi_status: ComplianceStatus
    rei_status: ComplianceStatus
    tank_mix_status: ComplianceStatus
    drift_risk_status: ComplianceStatus

    # Violations
    phi_violations: list[PHIViolation] = field(default_factory=list)
    rei_violations: list[REIViolation] = field(default_factory=list)
    tank_mix_issues: list[TankMixCompatibility] = field(default_factory=list)
    drift_assessment: SprayDriftRisk | None = None

    # Summary
    summary_en: str = ""
    summary_ar: str = ""

    # Recommendations
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)
