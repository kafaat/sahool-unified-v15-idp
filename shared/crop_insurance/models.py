"""
Crop Insurance Data Models
==========================
نماذج بيانات التأمين الزراعي

Data models for insurance policies, claims, premiums, and risk assessment.
Supports both traditional indemnity-based insurance and parametric/index-based insurance.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any


class InsuranceType(StrEnum):
    """Types of crop insurance | أنواع التأمين الزراعي"""

    TRADITIONAL = "traditional"  # Traditional indemnity-based | تقليدي قائم على التعويض
    PARAMETRIC = "parametric"  # Index-based/parametric | معياري/قائم على المؤشر
    HYBRID = "hybrid"  # Combination of both | مزيج من الاثنين
    AREA_YIELD = "area_yield"  # Area-yield index | مؤشر إنتاجية المنطقة
    WEATHER_INDEX = "weather_index"  # Weather index insurance | تأمين مؤشر الطقس


class PolicyStatus(StrEnum):
    """Policy status | حالة البوليصة"""

    DRAFT = "draft"  # مسودة
    PENDING_APPROVAL = "pending_approval"  # بانتظار الموافقة
    ACTIVE = "active"  # نشطة
    SUSPENDED = "suspended"  # معلقة
    EXPIRED = "expired"  # منتهية الصلاحية
    CANCELLED = "cancelled"  # ملغاة
    CLAIMED = "claimed"  # تم المطالبة بها


class ClaimStatus(StrEnum):
    """Claim status | حالة المطالبة"""

    DRAFT = "draft"  # مسودة
    SUBMITTED = "submitted"  # مقدمة
    UNDER_REVIEW = "under_review"  # قيد المراجعة
    FIELD_INSPECTION = "field_inspection"  # معاينة ميدانية
    APPROVED = "approved"  # موافق عليها
    PARTIALLY_APPROVED = "partially_approved"  # موافق عليها جزئياً
    REJECTED = "rejected"  # مرفوضة
    PAID = "paid"  # مدفوعة
    APPEALED = "appealed"  # مستأنفة
    CLOSED = "closed"  # مغلقة


class ClaimType(StrEnum):
    """Type of insurance claim | نوع مطالبة التأمين"""

    CROP_LOSS = "crop_loss"  # فقدان المحصول
    YIELD_SHORTFALL = "yield_shortfall"  # نقص الإنتاجية
    WEATHER_EVENT = "weather_event"  # حدث طقسي
    PEST_DAMAGE = "pest_damage"  # ضرر الآفات
    DISEASE_DAMAGE = "disease_damage"  # ضرر الأمراض
    HAIL_DAMAGE = "hail_damage"  # ضرر البرد
    FLOOD_DAMAGE = "flood_damage"  # ضرر الفيضان
    DROUGHT_DAMAGE = "drought_damage"  # ضرر الجفاف
    FROST_DAMAGE = "frost_damage"  # ضرر الصقيع
    FIRE_DAMAGE = "fire_damage"  # ضرر الحريق
    EQUIPMENT_FAILURE = "equipment_failure"  # فشل المعدات
    PARAMETRIC_TRIGGER = "parametric_trigger"  # تحفيز معياري


class RiskLevel(StrEnum):
    """Risk level classification | تصنيف مستوى المخاطر"""

    VERY_LOW = "very_low"  # منخفض جداً
    LOW = "low"  # منخفض
    MODERATE = "moderate"  # متوسط
    HIGH = "high"  # عالي
    VERY_HIGH = "very_high"  # عالي جداً
    EXTREME = "extreme"  # شديد


class CoverageType(StrEnum):
    """Coverage type | نوع التغطية"""

    FULL = "full"  # كاملة
    PARTIAL = "partial"  # جزئية
    BASIC = "basic"  # أساسية
    COMPREHENSIVE = "comprehensive"  # شاملة
    PREMIUM = "premium"  # ممتازة
    CUSTOM = "custom"  # مخصصة


class PayoutTriggerType(StrEnum):
    """Payout trigger type for parametric insurance | نوع محفز الدفع للتأمين المعياري"""

    RAINFALL_DEFICIT = "rainfall_deficit"  # عجز في هطول الأمطار
    RAINFALL_EXCESS = "rainfall_excess"  # فائض في هطول الأمطار
    TEMPERATURE_HIGH = "temperature_high"  # درجة حرارة عالية
    TEMPERATURE_LOW = "temperature_low"  # درجة حرارة منخفضة
    DROUGHT_INDEX = "drought_index"  # مؤشر الجفاف
    NDVI_THRESHOLD = "ndvi_threshold"  # عتبة NDVI
    SOIL_MOISTURE = "soil_moisture"  # رطوبة التربة
    WIND_SPEED = "wind_speed"  # سرعة الرياح
    GROWING_DEGREE_DAYS = "growing_degree_days"  # أيام درجات النمو


class WeatherIndexType(StrEnum):
    """Weather index types | أنواع مؤشرات الطقس"""

    CUMULATIVE_RAINFALL = "cumulative_rainfall"  # هطول الأمطار التراكمي
    CONSECUTIVE_DRY_DAYS = "consecutive_dry_days"  # أيام الجفاف المتتالية
    HEAT_WAVE_DURATION = "heat_wave_duration"  # مدة موجة الحر
    FROST_DAYS = "frost_days"  # أيام الصقيع
    EVAPOTRANSPIRATION = "evapotranspiration"  # التبخر والنتح
    SOIL_MOISTURE_INDEX = "soil_moisture_index"  # مؤشر رطوبة التربة
    VEGETATION_HEALTH = "vegetation_health"  # صحة الغطاء النباتي


@dataclass
class BilingualText:
    """Bilingual text for Arabic and English | نص ثنائي اللغة للعربية والإنجليزية"""

    en: str
    ar: str

    def get(self, lang: str = "en") -> str:
        """Get text in specified language"""
        return self.ar if lang == "ar" else self.en

    def to_dict(self) -> dict[str, str]:
        return {"en": self.en, "ar": self.ar}


@dataclass
class InsuranceProvider:
    """Insurance provider details | تفاصيل مزود التأمين"""

    id: str
    name: str
    name_ar: str
    license_number: str
    contact_email: str
    contact_phone: str
    address: str | None = None
    address_ar: str | None = None
    website: str | None = None
    rating: float = 0.0  # 0-5 stars
    is_active: bool = True
    supported_regions: list[str] = field(default_factory=list)
    supported_crops: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "license_number": self.license_number,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "address": self.address,
            "address_ar": self.address_ar,
            "website": self.website,
            "rating": self.rating,
            "is_active": self.is_active,
            "supported_regions": self.supported_regions,
            "supported_crops": self.supported_crops,
            "metadata": self.metadata,
        }


@dataclass
class CoverageDetails:
    """Insurance coverage details | تفاصيل تغطية التأمين"""

    coverage_type: CoverageType
    sum_insured: Decimal  # المبلغ المؤمن عليه
    currency: str = "SAR"  # العملة
    deductible_percentage: float = 0.0  # نسبة التحمل
    deductible_amount: Decimal | None = None  # مبلغ التحمل
    max_payout: Decimal | None = None  # الحد الأقصى للدفع
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None

    # Coverage limits by peril
    drought_coverage: float = 1.0  # 0-1 percentage
    flood_coverage: float = 1.0
    hail_coverage: float = 1.0
    frost_coverage: float = 1.0
    pest_coverage: float = 0.8
    disease_coverage: float = 0.8

    # Additional options
    replanting_coverage: bool = False  # تغطية إعادة الزراعة
    input_cost_coverage: bool = False  # تغطية تكاليف المدخلات
    revenue_protection: bool = False  # حماية الإيرادات

    description: str = ""
    description_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "coverage_type": self.coverage_type.value,
            "sum_insured": str(self.sum_insured),
            "currency": self.currency,
            "deductible_percentage": self.deductible_percentage,
            "deductible_amount": str(self.deductible_amount) if self.deductible_amount else None,
            "max_payout": str(self.max_payout) if self.max_payout else None,
            "coverage_start_date": self.coverage_start_date.isoformat() if self.coverage_start_date else None,
            "coverage_end_date": self.coverage_end_date.isoformat() if self.coverage_end_date else None,
            "drought_coverage": self.drought_coverage,
            "flood_coverage": self.flood_coverage,
            "hail_coverage": self.hail_coverage,
            "frost_coverage": self.frost_coverage,
            "pest_coverage": self.pest_coverage,
            "disease_coverage": self.disease_coverage,
            "replanting_coverage": self.replanting_coverage,
            "input_cost_coverage": self.input_cost_coverage,
            "revenue_protection": self.revenue_protection,
            "description": self.description,
            "description_ar": self.description_ar,
        }


@dataclass
class WeatherIndex:
    """Weather index for parametric insurance | مؤشر الطقس للتأمين المعياري"""

    index_type: WeatherIndexType
    measurement_station_id: str
    measurement_period_start: date
    measurement_period_end: date

    # Threshold values
    trigger_threshold: float  # القيمة المحفزة
    exit_threshold: float | None = None  # قيمة الخروج (لحساب تناسبي)

    # Current values (updated periodically)
    current_value: float | None = None
    last_updated: datetime | None = None

    # Payout calculation
    payout_rate_per_unit: Decimal = Decimal("0")  # سعر الدفع لكل وحدة
    max_units: float = 100.0  # الحد الأقصى للوحدات
    unit_name: str = "mm"  # اسم الوحدة
    unit_name_ar: str = "مم"

    description: str = ""
    description_ar: str = ""

    def is_triggered(self) -> bool:
        """Check if the index trigger condition is met"""
        if self.current_value is None:
            return False

        if self.index_type in [
            WeatherIndexType.CUMULATIVE_RAINFALL,
            WeatherIndexType.SOIL_MOISTURE_INDEX,
            WeatherIndexType.VEGETATION_HEALTH,
        ]:
            # Below threshold triggers payout
            return self.current_value < self.trigger_threshold
        else:
            # Above threshold triggers payout
            return self.current_value > self.trigger_threshold

    def calculate_payout_units(self) -> float:
        """Calculate payout units based on index deviation"""
        if self.current_value is None or not self.is_triggered():
            return 0.0

        if self.exit_threshold is not None:
            # Proportional payout between trigger and exit
            deviation = abs(self.current_value - self.trigger_threshold)
            max_deviation = abs(self.exit_threshold - self.trigger_threshold)
            ratio = min(deviation / max_deviation, 1.0) if max_deviation > 0 else 1.0
            return ratio * self.max_units
        else:
            # Binary payout
            return self.max_units

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_type": self.index_type.value,
            "measurement_station_id": self.measurement_station_id,
            "measurement_period_start": self.measurement_period_start.isoformat(),
            "measurement_period_end": self.measurement_period_end.isoformat(),
            "trigger_threshold": self.trigger_threshold,
            "exit_threshold": self.exit_threshold,
            "current_value": self.current_value,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "payout_rate_per_unit": str(self.payout_rate_per_unit),
            "max_units": self.max_units,
            "unit_name": self.unit_name,
            "unit_name_ar": self.unit_name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "is_triggered": self.is_triggered(),
        }


@dataclass
class ParametricTrigger:
    """Parametric insurance trigger configuration | تكوين محفز التأمين المعياري"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: PayoutTriggerType = PayoutTriggerType.RAINFALL_DEFICIT
    name: str = ""
    name_ar: str = ""

    # Trigger conditions
    threshold_value: float = 0.0
    threshold_operator: str = "<"  # <, >, <=, >=, ==
    measurement_unit: str = "mm"
    measurement_unit_ar: str = "مم"

    # Time window
    evaluation_period_days: int = 30
    rolling_window: bool = False  # Use rolling window vs fixed dates

    # Payout structure
    payout_percentage: float = 100.0  # Percentage of sum insured
    payout_amount: Decimal | None = None  # Fixed amount (if applicable)
    graduated_payout: bool = False  # Use graduated payout scale

    # Graduated payout tiers (if graduated_payout is True)
    payout_tiers: list[dict[str, Any]] = field(default_factory=list)
    # Example: [{"threshold": 50, "payout_pct": 25}, {"threshold": 30, "payout_pct": 50}]

    # Data source
    data_source: str = "weather_service"
    data_source_id: str = ""

    # Auto-trigger settings
    auto_trigger_enabled: bool = True
    requires_verification: bool = False

    def evaluate_trigger(self, measured_value: float) -> tuple[bool, float]:
        """
        Evaluate if trigger condition is met and calculate payout percentage

        Returns:
            Tuple of (is_triggered, payout_percentage)
        """
        operators = {
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
            "==": lambda a, b: a == b,
        }

        is_triggered = operators.get(self.threshold_operator, lambda a, b: False)(measured_value, self.threshold_value)

        if not is_triggered:
            return False, 0.0

        if self.graduated_payout and self.payout_tiers:
            # Find applicable tier
            payout_pct = 0.0
            for tier in sorted(self.payout_tiers, key=lambda x: x.get("threshold", 0), reverse=True):
                tier_threshold = tier.get("threshold", 0)
                if self.threshold_operator in ["<", "<="]:
                    if measured_value <= tier_threshold:
                        payout_pct = tier.get("payout_pct", 0)
                else:
                    if measured_value >= tier_threshold:
                        payout_pct = tier.get("payout_pct", 0)
            return True, payout_pct
        else:
            return True, self.payout_percentage

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "trigger_type": self.trigger_type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "threshold_value": self.threshold_value,
            "threshold_operator": self.threshold_operator,
            "measurement_unit": self.measurement_unit,
            "measurement_unit_ar": self.measurement_unit_ar,
            "evaluation_period_days": self.evaluation_period_days,
            "rolling_window": self.rolling_window,
            "payout_percentage": self.payout_percentage,
            "payout_amount": str(self.payout_amount) if self.payout_amount else None,
            "graduated_payout": self.graduated_payout,
            "payout_tiers": self.payout_tiers,
            "data_source": self.data_source,
            "data_source_id": self.data_source_id,
            "auto_trigger_enabled": self.auto_trigger_enabled,
            "requires_verification": self.requires_verification,
        }


@dataclass
class PolicyPremium:
    """Insurance policy premium details | تفاصيل قسط التأمين"""

    base_premium: Decimal  # القسط الأساسي
    risk_loading: Decimal = Decimal("0")  # تحميل المخاطر
    admin_fee: Decimal = Decimal("0")  # الرسوم الإدارية
    tax_amount: Decimal = Decimal("0")  # مبلغ الضريبة
    discount_amount: Decimal = Decimal("0")  # مبلغ الخصم
    total_premium: Decimal = Decimal("0")  # القسط الإجمالي
    currency: str = "SAR"

    # Premium calculation details
    base_rate: float = 0.0  # النسبة الأساسية
    risk_multiplier: float = 1.0  # مضاعف المخاطر
    area_adjustment: float = 1.0  # تعديل المساحة
    crop_adjustment: float = 1.0  # تعديل المحصول
    history_adjustment: float = 1.0  # تعديل التاريخ (No claims bonus)

    # Payment
    payment_frequency: str = "annual"  # annual, semi_annual, quarterly, monthly
    installment_amount: Decimal | None = None
    due_date: date | None = None
    paid: bool = False
    payment_date: date | None = None

    # Subsidies (if applicable)
    government_subsidy: Decimal = Decimal("0")  # دعم حكومي
    subsidy_percentage: float = 0.0

    def calculate_total(self) -> Decimal:
        """Calculate total premium"""
        subtotal = self.base_premium + self.risk_loading + self.admin_fee
        after_discount = subtotal - self.discount_amount
        self.total_premium = after_discount + self.tax_amount - self.government_subsidy
        return self.total_premium

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_premium": str(self.base_premium),
            "risk_loading": str(self.risk_loading),
            "admin_fee": str(self.admin_fee),
            "tax_amount": str(self.tax_amount),
            "discount_amount": str(self.discount_amount),
            "total_premium": str(self.total_premium),
            "currency": self.currency,
            "base_rate": self.base_rate,
            "risk_multiplier": self.risk_multiplier,
            "area_adjustment": self.area_adjustment,
            "crop_adjustment": self.crop_adjustment,
            "history_adjustment": self.history_adjustment,
            "payment_frequency": self.payment_frequency,
            "installment_amount": str(self.installment_amount) if self.installment_amount else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid": self.paid,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "government_subsidy": str(self.government_subsidy),
            "subsidy_percentage": self.subsidy_percentage,
        }


@dataclass
class InsurancePolicy:
    """
    Insurance policy for crop coverage
    بوليصة التأمين لتغطية المحاصيل
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    policy_number: str = ""
    tenant_id: str = ""
    farmer_id: str = ""

    # Policy details
    insurance_type: InsuranceType = InsuranceType.TRADITIONAL
    status: PolicyStatus = PolicyStatus.DRAFT

    # Provider
    provider_id: str = ""
    provider_name: str = ""
    provider_name_ar: str = ""

    # Coverage
    coverage: CoverageDetails | None = None

    # Field and crop details
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str = ""
    field_area_hectares: float = 0.0
    crop_type: str = ""
    crop_type_ar: str = ""
    crop_variety: str = ""
    planting_date: date | None = None
    expected_harvest_date: date | None = None

    # Location
    latitude: float | None = None
    longitude: float | None = None
    region: str = ""
    region_ar: str = ""

    # Policy period
    effective_date: date | None = None
    expiry_date: date | None = None

    # Premium
    premium: PolicyPremium | None = None

    # Parametric insurance settings (if applicable)
    parametric_triggers: list[ParametricTrigger] = field(default_factory=list)
    weather_indices: list[WeatherIndex] = field(default_factory=list)

    # Expected yield
    expected_yield_per_hectare: float = 0.0  # الإنتاجية المتوقعة لكل هكتار
    guaranteed_yield_percentage: float = 70.0  # نسبة الإنتاجية المضمونة
    price_per_unit: Decimal = Decimal("0")  # سعر الوحدة
    yield_unit: str = "ton"  # وحدة الإنتاجية
    yield_unit_ar: str = "طن"

    # Risk assessment
    risk_level: RiskLevel = RiskLevel.MODERATE
    risk_score: float = 50.0  # 0-100

    # Claims history
    claims_count: int = 0
    total_claims_paid: Decimal = Decimal("0")

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    approved_by: str = ""
    approved_at: datetime | None = None

    # Terms and conditions
    terms_accepted: bool = False
    terms_accepted_at: datetime | None = None
    special_conditions: str = ""
    special_conditions_ar: str = ""

    # Documents
    documents: list[dict[str, str]] = field(default_factory=list)
    # [{"type": "field_map", "url": "...", "name": "..."}]

    def is_active(self) -> bool:
        """Check if policy is currently active"""
        if self.status != PolicyStatus.ACTIVE:
            return False
        today = date.today()
        if self.effective_date and self.expiry_date:
            return self.effective_date <= today <= self.expiry_date
        return False

    def days_until_expiry(self) -> int | None:
        """Calculate days until policy expiry"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days

    def calculate_guaranteed_value(self) -> Decimal:
        """Calculate guaranteed production value"""
        total_expected_yield = Decimal(str(self.expected_yield_per_hectare * self.field_area_hectares))
        guaranteed_yield = total_expected_yield * Decimal(str(self.guaranteed_yield_percentage / 100))
        return guaranteed_yield * self.price_per_unit

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "policy_number": self.policy_number,
            "tenant_id": self.tenant_id,
            "farmer_id": self.farmer_id,
            "insurance_type": self.insurance_type.value,
            "status": self.status.value,
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "provider_name_ar": self.provider_name_ar,
            "coverage": self.coverage.to_dict() if self.coverage else None,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "field_area_hectares": self.field_area_hectares,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "crop_variety": self.crop_variety,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "expected_harvest_date": self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "region": self.region,
            "region_ar": self.region_ar,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "premium": self.premium.to_dict() if self.premium else None,
            "parametric_triggers": [t.to_dict() for t in self.parametric_triggers],
            "weather_indices": [w.to_dict() for w in self.weather_indices],
            "expected_yield_per_hectare": self.expected_yield_per_hectare,
            "guaranteed_yield_percentage": self.guaranteed_yield_percentage,
            "price_per_unit": str(self.price_per_unit),
            "yield_unit": self.yield_unit,
            "yield_unit_ar": self.yield_unit_ar,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "claims_count": self.claims_count,
            "total_claims_paid": str(self.total_claims_paid),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "terms_accepted": self.terms_accepted,
            "terms_accepted_at": self.terms_accepted_at.isoformat() if self.terms_accepted_at else None,
            "special_conditions": self.special_conditions,
            "special_conditions_ar": self.special_conditions_ar,
            "documents": self.documents,
            "is_active": self.is_active(),
            "days_until_expiry": self.days_until_expiry(),
            "guaranteed_value": str(self.calculate_guaranteed_value()),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class ClaimEvidence:
    """Evidence for insurance claim | دليل لمطالبة التأمين"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str = ""  # photo, document, sensor_data, weather_data, inspection_report
    title: str = ""
    title_ar: str = ""
    description: str = ""
    description_ar: str = ""
    file_url: str | None = None
    file_type: str | None = None
    file_size_bytes: int | None = None

    # For sensor/weather data
    data_source: str = ""
    data_value: Any = None
    data_timestamp: datetime | None = None

    # For inspection reports
    inspector_id: str | None = None
    inspector_name: str | None = None
    inspection_date: date | None = None

    # Verification
    verified: bool = False
    verified_by: str | None = None
    verified_at: datetime | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "evidence_type": self.evidence_type,
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "file_url": self.file_url,
            "file_type": self.file_type,
            "file_size_bytes": self.file_size_bytes,
            "data_source": self.data_source,
            "data_value": self.data_value,
            "data_timestamp": self.data_timestamp.isoformat() if self.data_timestamp else None,
            "inspector_id": self.inspector_id,
            "inspector_name": self.inspector_name,
            "inspection_date": self.inspection_date.isoformat() if self.inspection_date else None,
            "verified": self.verified,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ClaimPayout:
    """Payout details for approved claim | تفاصيل الدفع للمطالبة الموافق عليها"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim_id: str = ""

    # Amounts
    approved_amount: Decimal = Decimal("0")  # المبلغ الموافق عليه
    deductible_amount: Decimal = Decimal("0")  # مبلغ التحمل
    net_payout: Decimal = Decimal("0")  # صافي المدفوعات
    currency: str = "SAR"

    # Calculation breakdown
    loss_percentage: float = 0.0  # نسبة الخسارة
    coverage_percentage: float = 0.0  # نسبة التغطية
    calculation_details: dict[str, Any] = field(default_factory=dict)

    # Payment
    payment_method: str = ""  # bank_transfer, check, mobile_money
    payment_reference: str = ""
    payment_date: date | None = None
    payment_status: str = "pending"  # pending, processing, completed, failed

    # Bank details (if bank transfer)
    bank_name: str = ""
    account_number: str = ""
    iban: str = ""

    # Approval
    approved_by: str = ""
    approved_at: datetime | None = None
    approval_notes: str = ""
    approval_notes_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def calculate_net_payout(self) -> Decimal:
        """Calculate net payout after deductible"""
        self.net_payout = max(self.approved_amount - self.deductible_amount, Decimal("0"))
        return self.net_payout

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "approved_amount": str(self.approved_amount),
            "deductible_amount": str(self.deductible_amount),
            "net_payout": str(self.net_payout),
            "currency": self.currency,
            "loss_percentage": self.loss_percentage,
            "coverage_percentage": self.coverage_percentage,
            "calculation_details": self.calculation_details,
            "payment_method": self.payment_method,
            "payment_reference": self.payment_reference,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_status": self.payment_status,
            "bank_name": self.bank_name,
            "account_number": self.account_number[-4:] if self.account_number else "",  # Masked
            "iban": self.iban[-4:] if self.iban else "",  # Masked
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approval_notes": self.approval_notes,
            "approval_notes_ar": self.approval_notes_ar,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class InsuranceClaim:
    """
    Insurance claim for crop loss or damage
    مطالبة التأمين لخسارة أو ضرر المحصول
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    claim_number: str = ""
    policy_id: str = ""
    policy_number: str = ""
    tenant_id: str = ""
    farmer_id: str = ""

    # Claim details
    claim_type: ClaimType = ClaimType.CROP_LOSS
    status: ClaimStatus = ClaimStatus.DRAFT

    # Description
    title: str = ""
    title_ar: str = ""
    description: str = ""
    description_ar: str = ""

    # Date information
    incident_date: date | None = None
    discovery_date: date | None = None
    reported_date: date = field(default_factory=date.today)

    # Field and crop details
    field_id: str = ""
    field_name: str = ""
    affected_area_hectares: float = 0.0
    total_field_area_hectares: float = 0.0
    crop_type: str = ""
    crop_stage: str = ""  # Growth stage at time of incident

    # Loss details
    estimated_loss_percentage: float = 0.0  # نسبة الخسارة المقدرة
    estimated_loss_amount: Decimal = Decimal("0")  # مبلغ الخسارة المقدر
    actual_yield: float | None = None  # الإنتاجية الفعلية (if known)
    expected_yield: float | None = None  # الإنتاجية المتوقعة

    # Cause of loss
    cause_of_loss: str = ""
    cause_of_loss_ar: str = ""
    weather_event_id: str | None = None  # Link to weather event if applicable
    pest_id: str | None = None  # Link to pest/disease if applicable

    # Parametric claim details (if applicable)
    is_parametric_claim: bool = False
    trigger_id: str | None = None
    index_value: float | None = None
    threshold_value: float | None = None

    # Evidence
    evidence: list[ClaimEvidence] = field(default_factory=list)

    # Assessment
    assessor_id: str | None = None
    assessor_name: str | None = None
    assessment_date: date | None = None
    assessment_notes: str = ""
    assessment_notes_ar: str = ""
    verified_loss_percentage: float | None = None

    # Payout
    payout: ClaimPayout | None = None

    # Status history
    status_history: list[dict[str, Any]] = field(default_factory=list)
    # [{"status": "submitted", "timestamp": "...", "by": "...", "notes": "..."}]

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    submitted_at: datetime | None = None
    resolved_at: datetime | None = None

    # Contact
    contact_phone: str = ""
    contact_email: str = ""
    preferred_language: str = "ar"

    def add_status_change(self, new_status: ClaimStatus, by: str, notes: str = "") -> None:
        """Record status change in history"""
        self.status_history.append(
            {
                "previous_status": self.status.value,
                "new_status": new_status.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "by": by,
                "notes": notes,
            }
        )
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def can_be_submitted(self) -> tuple[bool, str, str]:
        """Check if claim can be submitted"""
        if self.status != ClaimStatus.DRAFT:
            return False, "Claim is not in draft status", "المطالبة ليست في حالة مسودة"

        if not self.incident_date:
            return False, "Incident date is required", "تاريخ الحادثة مطلوب"

        if not self.description and not self.description_ar:
            return False, "Description is required", "الوصف مطلوب"

        if self.estimated_loss_percentage <= 0:
            return (
                False,
                "Loss percentage must be greater than 0",
                "يجب أن تكون نسبة الخسارة أكبر من 0",
            )

        if not self.evidence:
            return False, "At least one piece of evidence is required", "مطلوب دليل واحد على الأقل"

        return True, "OK", "موافق"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "claim_number": self.claim_number,
            "policy_id": self.policy_id,
            "policy_number": self.policy_number,
            "tenant_id": self.tenant_id,
            "farmer_id": self.farmer_id,
            "claim_type": self.claim_type.value,
            "status": self.status.value,
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "incident_date": self.incident_date.isoformat() if self.incident_date else None,
            "discovery_date": self.discovery_date.isoformat() if self.discovery_date else None,
            "reported_date": self.reported_date.isoformat(),
            "field_id": self.field_id,
            "field_name": self.field_name,
            "affected_area_hectares": self.affected_area_hectares,
            "total_field_area_hectares": self.total_field_area_hectares,
            "crop_type": self.crop_type,
            "crop_stage": self.crop_stage,
            "estimated_loss_percentage": self.estimated_loss_percentage,
            "estimated_loss_amount": str(self.estimated_loss_amount),
            "actual_yield": self.actual_yield,
            "expected_yield": self.expected_yield,
            "cause_of_loss": self.cause_of_loss,
            "cause_of_loss_ar": self.cause_of_loss_ar,
            "weather_event_id": self.weather_event_id,
            "pest_id": self.pest_id,
            "is_parametric_claim": self.is_parametric_claim,
            "trigger_id": self.trigger_id,
            "index_value": self.index_value,
            "threshold_value": self.threshold_value,
            "evidence": [e.to_dict() for e in self.evidence],
            "assessor_id": self.assessor_id,
            "assessor_name": self.assessor_name,
            "assessment_date": self.assessment_date.isoformat() if self.assessment_date else None,
            "assessment_notes": self.assessment_notes,
            "assessment_notes_ar": self.assessment_notes_ar,
            "verified_loss_percentage": self.verified_loss_percentage,
            "payout": self.payout.to_dict() if self.payout else None,
            "status_history": self.status_history,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "preferred_language": self.preferred_language,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class RiskFactor:
    """Individual risk factor for assessment | عامل مخاطر فردي للتقييم"""

    factor_type: str  # weather, soil, historical, location, crop
    name: str
    name_ar: str
    weight: float  # 0.0 to 1.0
    score: float  # 0-100
    impact: str  # positive, negative, neutral
    description: str = ""
    description_ar: str = ""
    data_source: str = ""
    confidence: float = 0.8

    def weighted_score(self) -> float:
        """Calculate weighted score"""
        return self.score * self.weight

    def to_dict(self) -> dict[str, Any]:
        return {
            "factor_type": self.factor_type,
            "name": self.name,
            "name_ar": self.name_ar,
            "weight": self.weight,
            "score": self.score,
            "impact": self.impact,
            "description": self.description,
            "description_ar": self.description_ar,
            "data_source": self.data_source,
            "confidence": self.confidence,
            "weighted_score": self.weighted_score(),
        }


@dataclass
class FieldRiskProfile:
    """Comprehensive risk profile for a field | ملف المخاطر الشامل للحقل"""

    field_id: str
    tenant_id: str

    # Overall assessment
    overall_risk_level: RiskLevel = RiskLevel.MODERATE
    overall_risk_score: float = 50.0  # 0-100
    risk_grade: str = "B"  # A, B, C, D, F

    # Individual factors
    factors: list[RiskFactor] = field(default_factory=list)

    # Category scores
    weather_risk_score: float = 50.0
    soil_risk_score: float = 50.0
    historical_risk_score: float = 50.0
    location_risk_score: float = 50.0
    crop_risk_score: float = 50.0

    # Historical data
    historical_yield_average: float | None = None
    historical_yield_variance: float | None = None
    previous_claims_count: int = 0
    previous_claims_total: Decimal = Decimal("0")

    # Weather statistics
    drought_probability: float = 0.0
    flood_probability: float = 0.0
    frost_probability: float = 0.0
    hail_probability: float = 0.0

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Premium impact
    suggested_premium_multiplier: float = 1.0
    suggested_deductible_percentage: float = 10.0

    # Assessment metadata
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    assessment_version: str = "1.0"
    data_sources: list[str] = field(default_factory=list)
    confidence_score: float = 0.8

    def calculate_overall_score(self) -> float:
        """Calculate overall risk score from factors"""
        if not self.factors:
            return 50.0

        total_weight = sum(f.weight for f in self.factors)
        if total_weight == 0:
            return 50.0

        weighted_sum = sum(f.weighted_score() for f in self.factors)
        self.overall_risk_score = weighted_sum / total_weight
        return self.overall_risk_score

    def determine_risk_level(self) -> RiskLevel:
        """Determine risk level from score"""
        score = self.overall_risk_score
        if score <= 20:
            self.overall_risk_level = RiskLevel.VERY_LOW
            self.risk_grade = "A"
        elif score <= 35:
            self.overall_risk_level = RiskLevel.LOW
            self.risk_grade = "A"
        elif score <= 50:
            self.overall_risk_level = RiskLevel.MODERATE
            self.risk_grade = "B"
        elif score <= 65:
            self.overall_risk_level = RiskLevel.HIGH
            self.risk_grade = "C"
        elif score <= 80:
            self.overall_risk_level = RiskLevel.VERY_HIGH
            self.risk_grade = "D"
        else:
            self.overall_risk_level = RiskLevel.EXTREME
            self.risk_grade = "F"
        return self.overall_risk_level

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "tenant_id": self.tenant_id,
            "overall_risk_level": self.overall_risk_level.value,
            "overall_risk_score": self.overall_risk_score,
            "risk_grade": self.risk_grade,
            "factors": [f.to_dict() for f in self.factors],
            "weather_risk_score": self.weather_risk_score,
            "soil_risk_score": self.soil_risk_score,
            "historical_risk_score": self.historical_risk_score,
            "location_risk_score": self.location_risk_score,
            "crop_risk_score": self.crop_risk_score,
            "historical_yield_average": self.historical_yield_average,
            "historical_yield_variance": self.historical_yield_variance,
            "previous_claims_count": self.previous_claims_count,
            "previous_claims_total": str(self.previous_claims_total),
            "drought_probability": self.drought_probability,
            "flood_probability": self.flood_probability,
            "frost_probability": self.frost_probability,
            "hail_probability": self.hail_probability,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
            "suggested_premium_multiplier": self.suggested_premium_multiplier,
            "suggested_deductible_percentage": self.suggested_deductible_percentage,
            "assessed_at": self.assessed_at.isoformat(),
            "assessment_version": self.assessment_version,
            "data_sources": self.data_sources,
            "confidence_score": self.confidence_score,
        }


@dataclass
class PremiumQuote:
    """Premium quote for insurance policy | عرض سعر قسط التأمين"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    quote_number: str = ""
    tenant_id: str = ""
    farmer_id: str = ""

    # Field details
    field_id: str = ""
    field_area_hectares: float = 0.0
    crop_type: str = ""

    # Coverage
    insurance_type: InsuranceType = InsuranceType.TRADITIONAL
    coverage_type: CoverageType = CoverageType.BASIC
    sum_insured: Decimal = Decimal("0")

    # Premium calculation
    base_rate: float = 0.0  # As percentage
    risk_adjusted_rate: float = 0.0
    calculated_premium: Decimal = Decimal("0")

    # Risk profile
    risk_profile: FieldRiskProfile | None = None

    # Validity
    quote_date: date = field(default_factory=date.today)
    valid_until: date | None = None

    # Provider quotes
    provider_quotes: list[dict[str, Any]] = field(default_factory=list)
    # [{"provider_id": "...", "premium": "...", "coverage": {...}}]

    # Status
    status: str = "pending"  # pending, accepted, expired, rejected
    accepted_provider_id: str | None = None
    policy_id: str | None = None  # If converted to policy

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "quote_number": self.quote_number,
            "tenant_id": self.tenant_id,
            "farmer_id": self.farmer_id,
            "field_id": self.field_id,
            "field_area_hectares": self.field_area_hectares,
            "crop_type": self.crop_type,
            "insurance_type": self.insurance_type.value,
            "coverage_type": self.coverage_type.value,
            "sum_insured": str(self.sum_insured),
            "base_rate": self.base_rate,
            "risk_adjusted_rate": self.risk_adjusted_rate,
            "calculated_premium": str(self.calculated_premium),
            "risk_profile": self.risk_profile.to_dict() if self.risk_profile else None,
            "quote_date": self.quote_date.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "provider_quotes": self.provider_quotes,
            "status": self.status,
            "accepted_provider_id": self.accepted_provider_id,
            "policy_id": self.policy_id,
            "created_at": self.created_at.isoformat(),
        }


# Error Messages
@dataclass
class InsuranceErrorMessage:
    """Insurance error messages in Arabic and English"""

    en: str
    ar: str
    code: str


class InsuranceErrors:
    """Insurance error messages"""

    POLICY_NOT_FOUND = InsuranceErrorMessage(
        en="Insurance policy not found",
        ar="بوليصة التأمين غير موجودة",
        code="policy_not_found",
    )

    POLICY_NOT_ACTIVE = InsuranceErrorMessage(
        en="Insurance policy is not active",
        ar="بوليصة التأمين غير نشطة",
        code="policy_not_active",
    )

    POLICY_EXPIRED = InsuranceErrorMessage(
        en="Insurance policy has expired",
        ar="انتهت صلاحية بوليصة التأمين",
        code="policy_expired",
    )

    CLAIM_NOT_FOUND = InsuranceErrorMessage(
        en="Insurance claim not found",
        ar="مطالبة التأمين غير موجودة",
        code="claim_not_found",
    )

    CLAIM_ALREADY_SUBMITTED = InsuranceErrorMessage(
        en="Claim has already been submitted",
        ar="تم تقديم المطالبة بالفعل",
        code="claim_already_submitted",
    )

    CLAIM_INVALID_STATUS = InsuranceErrorMessage(
        en="Claim is in invalid status for this operation",
        ar="المطالبة في حالة غير صالحة لهذه العملية",
        code="claim_invalid_status",
    )

    INSUFFICIENT_EVIDENCE = InsuranceErrorMessage(
        en="Insufficient evidence provided for claim",
        ar="دليل غير كافٍ مقدم للمطالبة",
        code="insufficient_evidence",
    )

    INCIDENT_DATE_INVALID = InsuranceErrorMessage(
        en="Incident date is outside policy coverage period",
        ar="تاريخ الحادثة خارج فترة تغطية البوليصة",
        code="incident_date_invalid",
    )

    PREMIUM_NOT_PAID = InsuranceErrorMessage(
        en="Premium payment is required before submitting claim",
        ar="يلزم دفع القسط قبل تقديم المطالبة",
        code="premium_not_paid",
    )

    PARAMETRIC_TRIGGER_NOT_MET = InsuranceErrorMessage(
        en="Parametric trigger conditions not met",
        ar="شروط المحفز المعياري غير مستوفاة",
        code="parametric_trigger_not_met",
    )

    RISK_ASSESSMENT_FAILED = InsuranceErrorMessage(
        en="Risk assessment could not be completed",
        ar="تعذر إكمال تقييم المخاطر",
        code="risk_assessment_failed",
    )

    FIELD_NOT_INSURABLE = InsuranceErrorMessage(
        en="Field does not meet insurance eligibility criteria",
        ar="الحقل لا يستوفي معايير أهلية التأمين",
        code="field_not_insurable",
    )


class InsuranceException(Exception):
    """Base insurance exception"""

    def __init__(self, error: InsuranceErrorMessage, status_code: int = 400, details: str = ""):
        self.error = error
        self.status_code = status_code
        self.details = details
        super().__init__(error.en)

    def to_dict(self, lang: str = "en") -> dict[str, Any]:
        """Convert to dictionary for API response"""
        message = self.error.ar if lang == "ar" else self.error.en
        return {
            "error": self.error.code,
            "message": message,
            "details": self.details,
            "status_code": self.status_code,
        }
