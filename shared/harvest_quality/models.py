"""
Harvest Quality Tracking Models
===============================
نماذج تتبع جودة المحصول

Data models for quality grades, tests, standards, and buyer requirements.
Supports grains (wheat, barley), dates, and vegetables.

نماذج البيانات لدرجات الجودة والاختبارات والمعايير ومتطلبات المشترين.
يدعم الحبوب (القمح والشعير) والتمور والخضروات.

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

# ─────────────────────────────────────────────────────────────────────────────
# Enums - التعدادات
# ─────────────────────────────────────────────────────────────────────────────


class CropCategory(StrEnum):
    """Crop category for quality standards | فئة المحصول لمعايير الجودة"""

    GRAIN = "grain"  # حبوب (wheat, barley, corn)
    DATE = "date"  # تمور
    VEGETABLE = "vegetable"  # خضروات
    FRUIT = "fruit"  # فواكه
    LEGUME = "legume"  # بقوليات


class QualityGrade(StrEnum):
    """Quality grade classification | تصنيف درجة الجودة"""

    PREMIUM = "premium"  # ممتاز - Highest quality
    GRADE_A = "grade_a"  # درجة أولى - High quality
    GRADE_B = "grade_b"  # درجة ثانية - Standard quality
    GRADE_C = "grade_c"  # درجة ثالثة - Below standard
    INDUSTRIAL = "industrial"  # صناعي - Processing grade
    REJECTED = "rejected"  # مرفوض - Does not meet standards


class GrainType(StrEnum):
    """Types of grains | أنواع الحبوب"""

    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    CORN = "corn"  # ذرة
    SORGHUM = "sorghum"  # ذرة رفيعة
    RICE = "rice"  # أرز
    MILLET = "millet"  # دخن


class DateVariety(StrEnum):
    """Date palm varieties | أصناف التمور"""

    SUKKARI = "sukkari"  # سكري
    KHALAS = "khalas"  # خلاص
    AJWA = "ajwa"  # عجوة
    MEDJOOL = "medjool"  # مجهول
    BARHI = "barhi"  # برحي
    DEGLET_NOOR = "deglet_noor"  # دقلة نور
    SAFAWI = "safawi"  # صفاوي
    SEGAI = "segai"  # صقعي
    KHUDRI = "khudri"  # خضري
    MABROOM = "mabroom"  # مبروم
    ZAHIDI = "zahidi"  # زاهدي
    OTHER = "other"  # أخرى


class DateStage(StrEnum):
    """Date ripening stages | مراحل نضج التمر"""

    KIMRI = "kimri"  # خلال - Unripe green
    KHALAL = "khalal"  # بسر - Full size, crisp
    RUTAB = "rutab"  # رطب - Soft, ripe
    TAMR = "tamr"  # تمر - Fully ripe, dried


class VegetableType(StrEnum):
    """Types of vegetables | أنواع الخضروات"""

    TOMATO = "tomato"  # طماطم
    CUCUMBER = "cucumber"  # خيار
    ONION = "onion"  # بصل
    POTATO = "potato"  # بطاطس
    CARROT = "carrot"  # جزر
    EGGPLANT = "eggplant"  # باذنجان
    PEPPER = "pepper"  # فلفل
    LETTUCE = "lettuce"  # خس
    ZUCCHINI = "zucchini"  # كوسة
    CABBAGE = "cabbage"  # ملفوف
    OTHER = "other"  # أخرى


class TestType(StrEnum):
    """Types of quality tests | أنواع اختبارات الجودة"""

    # Grain tests
    MOISTURE = "moisture"  # الرطوبة
    PROTEIN = "protein"  # البروتين
    TEST_WEIGHT = "test_weight"  # الوزن النوعي
    FOREIGN_MATTER = "foreign_matter"  # الشوائب
    DAMAGED_KERNELS = "damaged_kernels"  # الحبوب التالفة
    BROKEN_KERNELS = "broken_kernels"  # الحبوب المكسورة
    FALLING_NUMBER = "falling_number"  # رقم السقوط
    GLUTEN = "gluten"  # الجلوتين

    # Date tests
    SUGAR_CONTENT = "sugar_content"  # نسبة السكر
    TEXTURE = "texture"  # القوام
    SIZE = "size"  # الحجم
    COLOR = "color"  # اللون
    DEFECTS = "defects"  # العيوب
    SKIN_SEPARATION = "skin_separation"  # انفصال القشرة

    # Vegetable tests
    FIRMNESS = "firmness"  # الصلابة
    BRIX = "brix"  # درجة بريكس (السكر)
    PH_LEVEL = "ph_level"  # مستوى الحموضة
    UNIFORMITY = "uniformity"  # التجانس
    FRESHNESS = "freshness"  # النضارة
    PEST_DAMAGE = "pest_damage"  # أضرار الآفات
    DISEASE_PRESENCE = "disease_presence"  # وجود أمراض

    # General
    VISUAL_INSPECTION = "visual_inspection"  # الفحص البصري
    WEIGHT_CHECK = "weight_check"  # فحص الوزن


class TestStatus(StrEnum):
    """Test status | حالة الاختبار"""

    PENDING = "pending"  # قيد الانتظار
    IN_PROGRESS = "in_progress"  # جارٍ
    COMPLETED = "completed"  # مكتمل
    FAILED = "failed"  # فشل
    CANCELLED = "cancelled"  # ملغى


class TestResult(StrEnum):
    """Test result classification | تصنيف نتيجة الاختبار"""

    PASS = "pass"  # ناجح
    MARGINAL = "marginal"  # حدي
    FAIL = "fail"  # راسب
    NOT_APPLICABLE = "not_applicable"  # لا ينطبق


class BuyerType(StrEnum):
    """Buyer type classification | تصنيف نوع المشتري"""

    RETAIL = "retail"  # تجزئة
    WHOLESALE = "wholesale"  # جملة
    PROCESSOR = "processor"  # مصنع
    EXPORTER = "exporter"  # مصدر
    COOPERATIVE = "cooperative"  # تعاونية
    GOVERNMENT = "government"  # حكومي


class TrendDirection(StrEnum):
    """Quality trend direction | اتجاه الجودة"""

    IMPROVING = "improving"  # يتحسن
    STABLE = "stable"  # مستقر
    DECLINING = "declining"  # يتراجع
    FLUCTUATING = "fluctuating"  # متقلب


class Currency(StrEnum):
    """Supported currencies | العملات المدعومة"""

    SAR = "SAR"  # Saudi Riyal | ريال سعودي
    YER = "YER"  # Yemeni Rial | ريال يمني
    USD = "USD"  # US Dollar | دولار أمريكي


class PriceUnit(StrEnum):
    """Price measurement units | وحدات قياس السعر"""

    KG = "kg"  # Kilogram | كيلوجرام
    TON = "ton"  # Metric ton | طن
    QUINTAL = "quintal"  # 100 kg | قنطار
    BOX = "box"  # Box/crate | صندوق


# ─────────────────────────────────────────────────────────────────────────────
# Quality Standards - معايير الجودة
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class QualityParameter:
    """
    Single quality parameter with thresholds
    معيار جودة واحد مع الحدود
    """

    parameter_name: str
    parameter_name_ar: str
    unit: str
    unit_ar: str

    # Grade thresholds (premium, grade_a, grade_b, grade_c)
    premium_min: float | None = None
    premium_max: float | None = None
    grade_a_min: float | None = None
    grade_a_max: float | None = None
    grade_b_min: float | None = None
    grade_b_max: float | None = None
    grade_c_min: float | None = None
    grade_c_max: float | None = None

    # Industrial/rejection thresholds
    industrial_min: float | None = None
    industrial_max: float | None = None
    rejection_threshold: float | None = None

    # Is lower value better?
    lower_is_better: bool = False

    # Weight in overall grade calculation (0.0 - 1.0)
    weight: float = 1.0

    # Is this a mandatory test?
    mandatory: bool = True

    description: str = ""
    description_ar: str = ""

    def get_grade_for_value(self, value: float) -> QualityGrade:
        """Determine grade based on measured value"""
        # Check rejection first
        if self.rejection_threshold is not None:
            if (
                self.lower_is_better
                and value > self.rejection_threshold
                or not self.lower_is_better
                and value < self.rejection_threshold
            ):
                return QualityGrade.REJECTED

        # Check each grade level
        if self._in_range(value, self.premium_min, self.premium_max):
            return QualityGrade.PREMIUM
        elif self._in_range(value, self.grade_a_min, self.grade_a_max):
            return QualityGrade.GRADE_A
        elif self._in_range(value, self.grade_b_min, self.grade_b_max):
            return QualityGrade.GRADE_B
        elif self._in_range(value, self.grade_c_min, self.grade_c_max):
            return QualityGrade.GRADE_C
        elif self._in_range(value, self.industrial_min, self.industrial_max):
            return QualityGrade.INDUSTRIAL
        else:
            return QualityGrade.REJECTED

    def _in_range(self, value: float, min_val: float | None, max_val: float | None) -> bool:
        """Check if value is in range"""
        if min_val is None and max_val is None:
            return False
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "parameter_name_ar": self.parameter_name_ar,
            "unit": self.unit,
            "unit_ar": self.unit_ar,
            "premium_min": self.premium_min,
            "premium_max": self.premium_max,
            "grade_a_min": self.grade_a_min,
            "grade_a_max": self.grade_a_max,
            "grade_b_min": self.grade_b_min,
            "grade_b_max": self.grade_b_max,
            "grade_c_min": self.grade_c_min,
            "grade_c_max": self.grade_c_max,
            "industrial_min": self.industrial_min,
            "industrial_max": self.industrial_max,
            "rejection_threshold": self.rejection_threshold,
            "lower_is_better": self.lower_is_better,
            "weight": self.weight,
            "mandatory": self.mandatory,
            "description": self.description,
            "description_ar": self.description_ar,
        }


@dataclass
class QualityStandard:
    """
    Complete quality standard for a crop type
    معيار الجودة الكامل لنوع المحصول
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    name_ar: str = ""
    crop_category: CropCategory = CropCategory.GRAIN
    crop_type: str = ""  # Specific crop (wheat, sukkari, tomato)
    crop_type_ar: str = ""

    # Parameters for this standard
    parameters: list[QualityParameter] = field(default_factory=list)

    # Standard metadata
    version: str = "1.0"
    effective_date: date | None = None
    expiry_date: date | None = None
    is_active: bool = True

    # Regulatory information
    regulatory_body: str = ""
    regulatory_body_ar: str = ""
    standard_code: str = ""  # e.g., SASO 1234, GSO 5678

    # Regional applicability
    applicable_regions: list[str] = field(default_factory=list)

    # Certification requirements
    certification_required: bool = False
    certification_bodies: list[str] = field(default_factory=list)

    description: str = ""
    description_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_parameter(self, parameter_name: str) -> QualityParameter | None:
        """Get parameter by name"""
        for param in self.parameters:
            if param.parameter_name == parameter_name:
                return param
        return None

    def get_mandatory_parameters(self) -> list[QualityParameter]:
        """Get all mandatory parameters"""
        return [p for p in self.parameters if p.mandatory]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "crop_category": self.crop_category.value,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "parameters": [p.to_dict() for p in self.parameters],
            "version": self.version,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "is_active": self.is_active,
            "regulatory_body": self.regulatory_body,
            "regulatory_body_ar": self.regulatory_body_ar,
            "standard_code": self.standard_code,
            "applicable_regions": self.applicable_regions,
            "certification_required": self.certification_required,
            "certification_bodies": self.certification_bodies,
            "description": self.description,
            "description_ar": self.description_ar,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Quality Tests - اختبارات الجودة
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class QualityTestResult:
    """
    Single quality test measurement
    قياس اختبار جودة واحد
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_type: TestType = TestType.VISUAL_INSPECTION
    parameter_name: str = ""
    parameter_name_ar: str = ""

    # Measured values
    value: float = 0.0
    unit: str = ""
    unit_ar: str = ""

    # Grade for this specific test
    grade: QualityGrade = QualityGrade.GRADE_B
    result: TestResult = TestResult.PASS

    # Thresholds used
    threshold_min: float | None = None
    threshold_max: float | None = None

    # Equipment/method
    test_method: str = ""
    test_method_ar: str = ""
    equipment_id: str = ""
    equipment_name: str = ""

    # Performed by
    tester_id: str = ""
    tester_name: str = ""
    test_timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Notes
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "test_type": self.test_type.value,
            "parameter_name": self.parameter_name,
            "parameter_name_ar": self.parameter_name_ar,
            "value": self.value,
            "unit": self.unit,
            "unit_ar": self.unit_ar,
            "grade": self.grade.value,
            "result": self.result.value,
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max,
            "test_method": self.test_method,
            "test_method_ar": self.test_method_ar,
            "equipment_id": self.equipment_id,
            "equipment_name": self.equipment_name,
            "tester_id": self.tester_id,
            "tester_name": self.tester_name,
            "test_timestamp": self.test_timestamp.isoformat(),
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


@dataclass
class QualityTestRecord:
    """
    Complete quality test record for a batch
    سجل اختبار الجودة الكامل لدفعة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_record_number: str = ""

    # Identification
    tenant_id: str = ""
    farm_id: str = ""
    field_id: str = ""
    batch_id: str = ""
    batch_code: str = ""

    # Crop information
    crop_category: CropCategory = CropCategory.GRAIN
    crop_type: str = ""
    crop_type_ar: str = ""
    variety: str = ""
    variety_ar: str = ""

    # Harvest information
    harvest_date: date | None = None
    harvest_location: str = ""

    # Sample information
    sample_id: str = ""
    sample_size_kg: float = 0.0
    sample_collected_at: datetime | None = None
    sample_collector_id: str = ""
    sample_collector_name: str = ""

    # Test status
    status: TestStatus = TestStatus.PENDING

    # Standard used
    standard_id: str = ""
    standard_name: str = ""
    standard_code: str = ""

    # Individual test results
    test_results: list[QualityTestResult] = field(default_factory=list)

    # Overall grading
    overall_grade: QualityGrade = QualityGrade.GRADE_B
    grade_score: float = 0.0  # 0-100 composite score
    grade_confidence: float = 0.0  # 0-1 confidence in grade

    # Key metrics summary (for quick access)
    moisture_percent: float | None = None
    protein_percent: float | None = None
    sugar_brix: float | None = None
    foreign_matter_percent: float | None = None
    defect_percent: float | None = None

    # Certification
    certified: bool = False
    certified_by: str = ""
    certified_at: datetime | None = None
    certificate_number: str = ""

    # Attachments
    photos: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)

    # Location where test was performed
    test_facility_id: str = ""
    test_facility_name: str = ""
    test_facility_name_ar: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""

    notes: str = ""
    notes_ar: str = ""

    def get_test_result(self, test_type: TestType) -> QualityTestResult | None:
        """Get test result by type"""
        for result in self.test_results:
            if result.test_type == test_type:
                return result
        return None

    def is_complete(self) -> bool:
        """Check if all required tests are completed"""
        return self.status == TestStatus.COMPLETED

    def passed_all_tests(self) -> bool:
        """Check if all tests passed"""
        return all(r.result in [TestResult.PASS, TestResult.MARGINAL] for r in self.test_results)

    def get_failed_tests(self) -> list[QualityTestResult]:
        """Get list of failed tests"""
        return [r for r in self.test_results if r.result == TestResult.FAIL]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "test_record_number": self.test_record_number,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "batch_id": self.batch_id,
            "batch_code": self.batch_code,
            "crop_category": self.crop_category.value,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "variety": self.variety,
            "variety_ar": self.variety_ar,
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "harvest_location": self.harvest_location,
            "sample_id": self.sample_id,
            "sample_size_kg": self.sample_size_kg,
            "sample_collected_at": self.sample_collected_at.isoformat() if self.sample_collected_at else None,
            "sample_collector_id": self.sample_collector_id,
            "sample_collector_name": self.sample_collector_name,
            "status": self.status.value,
            "standard_id": self.standard_id,
            "standard_name": self.standard_name,
            "standard_code": self.standard_code,
            "test_results": [r.to_dict() for r in self.test_results],
            "overall_grade": self.overall_grade.value,
            "grade_score": self.grade_score,
            "grade_confidence": self.grade_confidence,
            "moisture_percent": self.moisture_percent,
            "protein_percent": self.protein_percent,
            "sugar_brix": self.sugar_brix,
            "foreign_matter_percent": self.foreign_matter_percent,
            "defect_percent": self.defect_percent,
            "certified": self.certified,
            "certified_by": self.certified_by,
            "certified_at": self.certified_at.isoformat() if self.certified_at else None,
            "certificate_number": self.certificate_number,
            "photos": self.photos,
            "documents": self.documents,
            "test_facility_id": self.test_facility_id,
            "test_facility_name": self.test_facility_name,
            "test_facility_name_ar": self.test_facility_name_ar,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
            "is_complete": self.is_complete(),
            "passed_all_tests": self.passed_all_tests(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# Buyer Requirements - متطلبات المشترين
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BuyerRequirement:
    """
    Buyer quality requirements
    متطلبات جودة المشتري
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Buyer information
    buyer_id: str = ""
    buyer_name: str = ""
    buyer_name_ar: str = ""
    buyer_type: BuyerType = BuyerType.WHOLESALE
    contact_email: str = ""
    contact_phone: str = ""

    # Crop requirements
    crop_category: CropCategory = CropCategory.GRAIN
    crop_type: str = ""
    crop_type_ar: str = ""
    acceptable_varieties: list[str] = field(default_factory=list)

    # Minimum quality grade accepted
    minimum_grade: QualityGrade = QualityGrade.GRADE_B

    # Specific parameter requirements
    max_moisture_percent: float | None = None
    min_protein_percent: float | None = None
    max_foreign_matter_percent: float | None = None
    min_sugar_brix: float | None = None
    max_defect_percent: float | None = None

    # Custom requirements
    custom_requirements: list[dict[str, Any]] = field(default_factory=list)
    # [{"parameter": "moisture", "operator": "<=", "value": 13.0}]

    # Quantity requirements
    min_quantity_kg: float | None = None
    max_quantity_kg: float | None = None
    preferred_quantity_kg: float | None = None

    # Pricing
    base_price_per_kg: Decimal = Decimal("0")
    currency: Currency = Currency.SAR
    price_premium_percent: float = 0.0  # For higher grades
    price_discount_percent: float = 0.0  # For lower grades

    # Delivery requirements
    delivery_region: str = ""
    delivery_region_ar: str = ""
    max_delivery_distance_km: float | None = None
    preferred_delivery_dates: list[date] = field(default_factory=list)

    # Packaging requirements
    packaging_type: str = ""
    packaging_type_ar: str = ""
    max_package_weight_kg: float | None = None

    # Certification requirements
    required_certifications: list[str] = field(default_factory=list)
    # e.g., ["globalgap", "organic", "halal"]

    # Validity
    valid_from: date | None = None
    valid_until: date | None = None
    is_active: bool = True

    # Priority
    priority: int = 0  # Higher = more important

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    notes: str = ""
    notes_ar: str = ""

    def is_valid(self) -> bool:
        """Check if requirement is currently valid"""
        if not self.is_active:
            return False
        today = date.today()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True

    def matches_grade(self, grade: QualityGrade) -> bool:
        """Check if grade meets minimum requirement"""
        grade_order = [
            QualityGrade.PREMIUM,
            QualityGrade.GRADE_A,
            QualityGrade.GRADE_B,
            QualityGrade.GRADE_C,
            QualityGrade.INDUSTRIAL,
            QualityGrade.REJECTED,
        ]
        return grade_order.index(grade) <= grade_order.index(self.minimum_grade)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "buyer_id": self.buyer_id,
            "buyer_name": self.buyer_name,
            "buyer_name_ar": self.buyer_name_ar,
            "buyer_type": self.buyer_type.value,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "crop_category": self.crop_category.value,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "acceptable_varieties": self.acceptable_varieties,
            "minimum_grade": self.minimum_grade.value,
            "max_moisture_percent": self.max_moisture_percent,
            "min_protein_percent": self.min_protein_percent,
            "max_foreign_matter_percent": self.max_foreign_matter_percent,
            "min_sugar_brix": self.min_sugar_brix,
            "max_defect_percent": self.max_defect_percent,
            "custom_requirements": self.custom_requirements,
            "min_quantity_kg": self.min_quantity_kg,
            "max_quantity_kg": self.max_quantity_kg,
            "preferred_quantity_kg": self.preferred_quantity_kg,
            "base_price_per_kg": str(self.base_price_per_kg),
            "currency": self.currency.value,
            "price_premium_percent": self.price_premium_percent,
            "price_discount_percent": self.price_discount_percent,
            "delivery_region": self.delivery_region,
            "delivery_region_ar": self.delivery_region_ar,
            "max_delivery_distance_km": self.max_delivery_distance_km,
            "preferred_delivery_dates": [d.isoformat() for d in self.preferred_delivery_dates],
            "packaging_type": self.packaging_type,
            "packaging_type_ar": self.packaging_type_ar,
            "max_package_weight_kg": self.max_package_weight_kg,
            "required_certifications": self.required_certifications,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "is_active": self.is_active,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "notes": self.notes,
            "notes_ar": self.notes_ar,
            "is_valid": self.is_valid(),
        }


@dataclass
class BuyerMatch:
    """
    Match result between harvest and buyer
    نتيجة المطابقة بين المحصول والمشتري
    """

    buyer_requirement_id: str
    buyer_id: str
    buyer_name: str
    buyer_name_ar: str
    buyer_type: BuyerType

    # Match quality
    match_score: float = 0.0  # 0-100
    is_eligible: bool = False

    # Price information
    offered_price_per_kg: Decimal = Decimal("0")
    price_adjustment_percent: float = 0.0
    estimated_total_value: Decimal = Decimal("0")
    currency: Currency = Currency.SAR

    # Requirements met
    grade_requirement_met: bool = False
    quantity_requirement_met: bool = False
    certification_requirement_met: bool = False
    parameter_requirements_met: list[dict[str, Any]] = field(default_factory=list)
    # [{"parameter": "moisture", "required": 13.0, "actual": 12.5, "met": True}]

    # Unmet requirements
    unmet_requirements: list[str] = field(default_factory=list)
    unmet_requirements_ar: list[str] = field(default_factory=list)

    # Contact information
    contact_email: str = ""
    contact_phone: str = ""

    # Recommendation
    recommendation: str = ""
    recommendation_ar: str = ""

    matched_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "buyer_requirement_id": self.buyer_requirement_id,
            "buyer_id": self.buyer_id,
            "buyer_name": self.buyer_name,
            "buyer_name_ar": self.buyer_name_ar,
            "buyer_type": self.buyer_type.value,
            "match_score": self.match_score,
            "is_eligible": self.is_eligible,
            "offered_price_per_kg": str(self.offered_price_per_kg),
            "price_adjustment_percent": self.price_adjustment_percent,
            "estimated_total_value": str(self.estimated_total_value),
            "currency": self.currency.value,
            "grade_requirement_met": self.grade_requirement_met,
            "quantity_requirement_met": self.quantity_requirement_met,
            "certification_requirement_met": self.certification_requirement_met,
            "parameter_requirements_met": self.parameter_requirements_met,
            "unmet_requirements": self.unmet_requirements,
            "unmet_requirements_ar": self.unmet_requirements_ar,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "recommendation": self.recommendation,
            "recommendation_ar": self.recommendation_ar,
            "matched_at": self.matched_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Quality Trends - اتجاهات الجودة
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class QualityTrendPoint:
    """Single point in quality trend | نقطة واحدة في اتجاه الجودة"""

    date: date
    grade: QualityGrade
    grade_score: float
    moisture_percent: float | None = None
    protein_percent: float | None = None
    sugar_brix: float | None = None
    defect_percent: float | None = None
    sample_count: int = 1


@dataclass
class QualityTrendAnalysis:
    """
    Quality trend analysis result
    نتيجة تحليل اتجاه الجودة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Scope
    tenant_id: str = ""
    farm_id: str = ""
    field_id: str = ""
    crop_type: str = ""
    crop_type_ar: str = ""

    # Analysis period
    period_start: date | None = None
    period_end: date | None = None

    # Trend data points
    data_points: list[QualityTrendPoint] = field(default_factory=list)

    # Overall trend
    trend_direction: TrendDirection = TrendDirection.STABLE
    trend_strength: float = 0.0  # 0-100

    # Summary statistics
    average_grade_score: float = 0.0
    grade_score_std_dev: float = 0.0
    best_grade_score: float = 0.0
    worst_grade_score: float = 0.0

    # Grade distribution
    grade_distribution: dict[str, int] = field(default_factory=dict)
    # {"premium": 5, "grade_a": 10, "grade_b": 15, ...}

    # Parameter trends
    moisture_trend: TrendDirection = TrendDirection.STABLE
    protein_trend: TrendDirection = TrendDirection.STABLE
    sugar_trend: TrendDirection = TrendDirection.STABLE

    # Average parameter values
    avg_moisture_percent: float | None = None
    avg_protein_percent: float | None = None
    avg_sugar_brix: float | None = None
    avg_defect_percent: float | None = None

    # Comparison with regional/seasonal averages
    vs_regional_average: float = 0.0  # Percentage above/below
    vs_seasonal_average: float = 0.0

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Analysis metadata
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    sample_count: int = 0
    confidence_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "data_points": [
                {
                    "date": p.date.isoformat(),
                    "grade": p.grade.value,
                    "grade_score": p.grade_score,
                    "moisture_percent": p.moisture_percent,
                    "protein_percent": p.protein_percent,
                    "sugar_brix": p.sugar_brix,
                    "defect_percent": p.defect_percent,
                    "sample_count": p.sample_count,
                }
                for p in self.data_points
            ],
            "trend_direction": self.trend_direction.value,
            "trend_strength": self.trend_strength,
            "average_grade_score": self.average_grade_score,
            "grade_score_std_dev": self.grade_score_std_dev,
            "best_grade_score": self.best_grade_score,
            "worst_grade_score": self.worst_grade_score,
            "grade_distribution": self.grade_distribution,
            "moisture_trend": self.moisture_trend.value,
            "protein_trend": self.protein_trend.value,
            "sugar_trend": self.sugar_trend.value,
            "avg_moisture_percent": self.avg_moisture_percent,
            "avg_protein_percent": self.avg_protein_percent,
            "avg_sugar_brix": self.avg_sugar_brix,
            "avg_defect_percent": self.avg_defect_percent,
            "vs_regional_average": self.vs_regional_average,
            "vs_seasonal_average": self.vs_seasonal_average,
            "recommendations": self.recommendations,
            "recommendations_ar": self.recommendations_ar,
            "analyzed_at": self.analyzed_at.isoformat(),
            "sample_count": self.sample_count,
            "confidence_score": self.confidence_score,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Pricing Models - نماذج التسعير
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class GradePriceMatrix:
    """
    Price matrix for different quality grades
    مصفوفة الأسعار لدرجات الجودة المختلفة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Crop information
    crop_category: CropCategory = CropCategory.GRAIN
    crop_type: str = ""
    crop_type_ar: str = ""
    variety: str = ""
    variety_ar: str = ""

    # Base pricing
    currency: Currency = Currency.SAR
    price_unit: PriceUnit = PriceUnit.KG
    base_price: Decimal = Decimal("0")  # Reference price for Grade B

    # Grade-based price adjustments (as percentage of base price)
    premium_multiplier: float = 1.30  # 130% of base
    grade_a_multiplier: float = 1.15  # 115% of base
    grade_b_multiplier: float = 1.00  # 100% of base
    grade_c_multiplier: float = 0.85  # 85% of base
    industrial_multiplier: float = 0.60  # 60% of base

    # Absolute prices (calculated or override)
    premium_price: Decimal | None = None
    grade_a_price: Decimal | None = None
    grade_b_price: Decimal | None = None
    grade_c_price: Decimal | None = None
    industrial_price: Decimal | None = None

    # Parameter-based adjustments
    moisture_adjustment_per_percent: Decimal = Decimal("0")  # Deduction per % above threshold
    protein_bonus_per_percent: Decimal = Decimal("0")  # Bonus per % above threshold
    foreign_matter_deduction_per_percent: Decimal = Decimal("0")

    # Market and season
    market_id: str = ""
    market_name: str = ""
    market_name_ar: str = ""
    season: str = ""  # winter, summer, etc.

    # Validity
    effective_date: date | None = None
    expiry_date: date | None = None
    is_active: bool = True

    # Source
    source: str = "market"  # market, contract, government
    source_id: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_price_for_grade(self, grade: QualityGrade) -> Decimal:
        """Get price for a specific grade"""
        if grade == QualityGrade.PREMIUM:
            return self.premium_price or self.base_price * Decimal(str(self.premium_multiplier))
        elif grade == QualityGrade.GRADE_A:
            return self.grade_a_price or self.base_price * Decimal(str(self.grade_a_multiplier))
        elif grade == QualityGrade.GRADE_B:
            return self.grade_b_price or self.base_price * Decimal(str(self.grade_b_multiplier))
        elif grade == QualityGrade.GRADE_C:
            return self.grade_c_price or self.base_price * Decimal(str(self.grade_c_multiplier))
        elif grade == QualityGrade.INDUSTRIAL:
            return self.industrial_price or self.base_price * Decimal(str(self.industrial_multiplier))
        else:
            return Decimal("0")  # Rejected

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "crop_category": self.crop_category.value,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "variety": self.variety,
            "variety_ar": self.variety_ar,
            "currency": self.currency.value,
            "price_unit": self.price_unit.value,
            "base_price": str(self.base_price),
            "premium_multiplier": self.premium_multiplier,
            "grade_a_multiplier": self.grade_a_multiplier,
            "grade_b_multiplier": self.grade_b_multiplier,
            "grade_c_multiplier": self.grade_c_multiplier,
            "industrial_multiplier": self.industrial_multiplier,
            "premium_price": str(self.get_price_for_grade(QualityGrade.PREMIUM)),
            "grade_a_price": str(self.get_price_for_grade(QualityGrade.GRADE_A)),
            "grade_b_price": str(self.get_price_for_grade(QualityGrade.GRADE_B)),
            "grade_c_price": str(self.get_price_for_grade(QualityGrade.GRADE_C)),
            "industrial_price": str(self.get_price_for_grade(QualityGrade.INDUSTRIAL)),
            "moisture_adjustment_per_percent": str(self.moisture_adjustment_per_percent),
            "protein_bonus_per_percent": str(self.protein_bonus_per_percent),
            "foreign_matter_deduction_per_percent": str(self.foreign_matter_deduction_per_percent),
            "market_id": self.market_id,
            "market_name": self.market_name,
            "market_name_ar": self.market_name_ar,
            "season": self.season,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "is_active": self.is_active,
            "source": self.source,
            "source_id": self.source_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class PriceCalculation:
    """
    Detailed price calculation for a batch
    حساب السعر التفصيلي لدفعة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Batch information
    batch_id: str = ""
    test_record_id: str = ""

    # Quality information
    overall_grade: QualityGrade = QualityGrade.GRADE_B
    grade_score: float = 0.0

    # Base pricing
    price_matrix_id: str = ""
    base_price_per_unit: Decimal = Decimal("0")
    grade_price_per_unit: Decimal = Decimal("0")
    currency: Currency = Currency.SAR
    price_unit: PriceUnit = PriceUnit.KG

    # Quantity
    quantity: float = 0.0
    quantity_unit: str = "kg"

    # Adjustments
    adjustments: list[dict[str, Any]] = field(default_factory=list)
    # [{"reason": "Moisture above threshold", "reason_ar": "...", "amount": -50.00}]
    total_adjustments: Decimal = Decimal("0")

    # Final calculation
    subtotal: Decimal = Decimal("0")  # grade_price * quantity
    final_price: Decimal = Decimal("0")  # subtotal + adjustments
    final_price_per_unit: Decimal = Decimal("0")

    # Comparison
    vs_base_price_percent: float = 0.0  # % above/below base
    vs_market_average_percent: float = 0.0

    # Calculation metadata
    calculated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    calculated_by: str = ""

    notes: str = ""
    notes_ar: str = ""

    def calculate(self) -> Decimal:
        """Calculate final price"""
        self.subtotal = self.grade_price_per_unit * Decimal(str(self.quantity))
        self.total_adjustments = sum(Decimal(str(adj.get("amount", 0))) for adj in self.adjustments)
        self.final_price = self.subtotal + self.total_adjustments
        if self.quantity > 0:
            self.final_price_per_unit = self.final_price / Decimal(str(self.quantity))
        return self.final_price

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "test_record_id": self.test_record_id,
            "overall_grade": self.overall_grade.value,
            "grade_score": self.grade_score,
            "price_matrix_id": self.price_matrix_id,
            "base_price_per_unit": str(self.base_price_per_unit),
            "grade_price_per_unit": str(self.grade_price_per_unit),
            "currency": self.currency.value,
            "price_unit": self.price_unit.value,
            "quantity": self.quantity,
            "quantity_unit": self.quantity_unit,
            "adjustments": self.adjustments,
            "total_adjustments": str(self.total_adjustments),
            "subtotal": str(self.subtotal),
            "final_price": str(self.final_price),
            "final_price_per_unit": str(self.final_price_per_unit),
            "vs_base_price_percent": self.vs_base_price_percent,
            "vs_market_average_percent": self.vs_market_average_percent,
            "calculated_at": self.calculated_at.isoformat(),
            "calculated_by": self.calculated_by,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# Error Handling - معالجة الأخطاء
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class QualityError:
    """Quality module error message | رسالة خطأ وحدة الجودة"""

    code: str
    message: str
    message_ar: str


class QualityErrors:
    """Quality error messages | رسائل أخطاء الجودة"""

    STANDARD_NOT_FOUND = QualityError(
        code="standard_not_found",
        message="Quality standard not found",
        message_ar="معيار الجودة غير موجود",
    )

    TEST_RECORD_NOT_FOUND = QualityError(
        code="test_record_not_found",
        message="Quality test record not found",
        message_ar="سجل اختبار الجودة غير موجود",
    )

    BUYER_REQUIREMENT_NOT_FOUND = QualityError(
        code="buyer_requirement_not_found",
        message="Buyer requirement not found",
        message_ar="متطلبات المشتري غير موجودة",
    )

    PRICE_MATRIX_NOT_FOUND = QualityError(
        code="price_matrix_not_found",
        message="Price matrix not found for this crop",
        message_ar="مصفوفة الأسعار غير موجودة لهذا المحصول",
    )

    INVALID_TEST_VALUE = QualityError(
        code="invalid_test_value",
        message="Invalid test value provided",
        message_ar="قيمة اختبار غير صالحة",
    )

    INCOMPLETE_TEST_DATA = QualityError(
        code="incomplete_test_data",
        message="Test data is incomplete. All mandatory tests are required",
        message_ar="بيانات الاختبار غير مكتملة. جميع الاختبارات الإلزامية مطلوبة",
    )

    GRADE_CALCULATION_FAILED = QualityError(
        code="grade_calculation_failed",
        message="Failed to calculate quality grade",
        message_ar="فشل في حساب درجة الجودة",
    )

    INSUFFICIENT_DATA_FOR_TREND = QualityError(
        code="insufficient_data_for_trend",
        message="Insufficient data for trend analysis",
        message_ar="بيانات غير كافية لتحليل الاتجاه",
    )

    NO_MATCHING_BUYERS = QualityError(
        code="no_matching_buyers",
        message="No buyers match the quality criteria",
        message_ar="لا يوجد مشترين يطابقون معايير الجودة",
    )


class QualityException(Exception):
    """Base exception for quality module | استثناء أساسي لوحدة الجودة"""

    def __init__(self, error: QualityError, details: str = ""):
        self.error = error
        self.details = details
        super().__init__(error.message)

    def to_dict(self, lang: str = "en") -> dict[str, Any]:
        message = self.error.message_ar if lang == "ar" else self.error.message
        return {
            "error": self.error.code,
            "message": message,
            "details": self.details,
        }
