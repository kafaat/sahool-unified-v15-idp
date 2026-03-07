"""
Safety Compliance Module - وحدة سلامة الامتثال

Provides safety compliance tracking for agricultural workers including:
- Re-Entry Interval (REI) zone management
- Personal Protective Equipment (PPE) requirements
- Safety certifications validation
- Heat stress monitoring
- Pre-task safety checks
- Safety violation tracking and reporting

Integrates with shared.pesticide_compliance for REI data.

Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum

from .models import (
    PPEType,
    PreTaskSafetyCheck,
    REIZone,
    SafetyCertification,
    SafetyChecklistItem,
    SafetyViolation,
    SafetyViolationType,
    Task,
    TaskCategory,
    Worker,
    create_rei_zone,
    generate_id,
)


class SafetyCheckStatus(StrEnum):
    """Safety check status - حالة فحص السلامة"""

    PASSED = "passed"  # ناجح
    FAILED = "failed"  # فاشل
    WARNING = "warning"  # تحذير
    PENDING = "pending"  # قيد الانتظار


class HeatRiskLevel(StrEnum):
    """Heat stress risk level - مستوى خطر الإجهاد الحراري"""

    LOW = "low"  # منخفض
    MODERATE = "moderate"  # متوسط
    HIGH = "high"  # مرتفع
    EXTREME = "extreme"  # شديد


@dataclass
class PPERequirementSet:
    """PPE requirement set for a task/zone - مجموعة متطلبات الحماية للمهمة/المنطقة"""

    required_ppe: list[PPEType]
    task_category: TaskCategory | None = None
    rei_zone_id: str | None = None
    pesticide_id: str | None = None

    description_en: str = ""
    description_ar: str = ""

    # Detailed requirements
    gloves_type: str = "Chemical-resistant nitrile"
    gloves_type_ar: str = "نتريل مقاوم للمواد الكيميائية"
    respirator_type: str = "N95 or better"
    respirator_type_ar: str = "N95 أو أفضل"
    eye_protection_type: str = "Chemical splash goggles"
    eye_protection_type_ar: str = "نظارات واقية من الرذاذ الكيميائي"
    clothing_type: str = "Long sleeves and pants"
    clothing_type_ar: str = "أكمام وسراويل طويلة"
    footwear_type: str = "Rubber boots"
    footwear_type_ar: str = "أحذية مطاطية"


@dataclass
class SafetyCheckResult:
    """Result of a safety compliance check - نتيجة فحص الامتثال للسلامة"""

    check_id: str
    check_type: str
    status: SafetyCheckStatus

    message_en: str
    message_ar: str

    # Detailed results
    issues: list[str] = field(default_factory=list)
    issues_ar: list[str] = field(default_factory=list)
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Related entities
    worker_id: str | None = None
    task_id: str | None = None
    field_id: str | None = None
    zone_id: str | None = None

    # Metadata
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    checked_by: str | None = None


@dataclass
class HeatStressAssessment:
    """Heat stress risk assessment - تقييم خطر الإجهاد الحراري"""

    assessment_id: str
    farm_id: str

    # Weather conditions
    temperature_c: float
    humidity_percent: float
    heat_index_c: float
    wind_speed_kmh: float

    # Risk assessment
    risk_level: HeatRiskLevel

    # Work modifications
    max_continuous_work_minutes: int
    required_break_minutes: int
    water_intake_liters_per_hour: float

    # Messages
    message_en: str
    message_ar: str
    precautions_en: list[str] = field(default_factory=list)
    precautions_ar: list[str] = field(default_factory=list)

    # Assessment time
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_until: datetime = field(default_factory=lambda: datetime.now(UTC) + timedelta(hours=2))

    def is_valid(self) -> bool:
        """Check if assessment is still valid"""
        return datetime.now(UTC) < self.valid_until


@dataclass
class REIComplianceResult:
    """REI compliance check result - نتيجة فحص امتثال فترة إعادة الدخول"""

    field_id: str
    check_time: datetime

    is_compliant: bool
    can_enter: bool
    requires_ppe: bool

    # Active zones
    active_zones: list[REIZone] = field(default_factory=list)
    earliest_safe_entry: datetime | None = None

    # Required PPE for early entry (if allowed)
    early_entry_ppe: list[PPEType] = field(default_factory=list)
    allowed_early_entry_tasks: list[str] = field(default_factory=list)

    # Messages
    message_en: str = ""
    message_ar: str = ""
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)


# ==================== Standard PPE Sets by Task Category ====================

TASK_PPE_REQUIREMENTS: dict[TaskCategory, list[PPEType]] = {
    TaskCategory.PESTICIDE_APPLICATION: [
        PPEType.GLOVES,
        PPEType.RESPIRATOR,
        PPEType.GOGGLES,
        PPEType.COVERALL,
        PPEType.BOOTS,
    ],
    TaskCategory.FERTILIZATION: [PPEType.GLOVES, PPEType.GOGGLES, PPEType.BOOTS],
    TaskCategory.HARVESTING: [PPEType.GLOVES, PPEType.HAT, PPEType.BOOTS],
    TaskCategory.PRUNING: [PPEType.GLOVES, PPEType.GOGGLES, PPEType.HAT],
    TaskCategory.IRRIGATION: [PPEType.BOOTS, PPEType.HAT],
    TaskCategory.EQUIPMENT_MAINTENANCE: [
        PPEType.GLOVES,
        PPEType.GOGGLES,
        PPEType.EAR_PROTECTION,
        PPEType.BOOTS,
    ],
    TaskCategory.GREENHOUSE_WORK: [PPEType.GLOVES, PPEType.HAT],
    TaskCategory.SOIL_PREPARATION: [PPEType.GLOVES, PPEType.BOOTS, PPEType.HAT],
    TaskCategory.WEEDING: [PPEType.GLOVES, PPEType.HAT, PPEType.BOOTS],
    TaskCategory.SCOUTING: [PPEType.HAT, PPEType.BOOTS],
    TaskCategory.PLANTING: [PPEType.GLOVES, PPEType.HAT],
    TaskCategory.PACKING: [PPEType.GLOVES, PPEType.APRON],
    TaskCategory.QUALITY_CONTROL: [PPEType.GLOVES],
    TaskCategory.LIVESTOCK: [PPEType.GLOVES, PPEType.BOOTS, PPEType.COVERALL],
    TaskCategory.GENERAL_LABOR: [PPEType.GLOVES, PPEType.HAT],
}


# ==================== Standard Safety Checklists ====================

GENERAL_SAFETY_CHECKLIST: list[SafetyChecklistItem] = [
    SafetyChecklistItem(
        item_id="GEN001",
        description="Worker has been briefed on task hazards",
        description_ar="تم إطلاع العامل على مخاطر المهمة",
        category="briefing",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="GEN002",
        description="Emergency contact information is up to date",
        description_ar="معلومات الاتصال في حالات الطوارئ محدثة",
        category="emergency",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="GEN003",
        description="Worker knows location of first aid kit",
        description_ar="العامل يعرف موقع صندوق الإسعافات الأولية",
        category="emergency",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="GEN004",
        description="Worker is physically fit for the task",
        description_ar="العامل لائق بدنياً للمهمة",
        category="health",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="GEN005",
        description="Adequate water and shade available",
        description_ar="تتوفر مياه كافية وظل",
        category="heat",
        is_mandatory=True,
    ),
]

PESTICIDE_SAFETY_CHECKLIST: list[SafetyChecklistItem] = [
    SafetyChecklistItem(
        item_id="PEST001",
        description="Worker has valid pesticide applicator certification",
        description_ar="العامل لديه شهادة تطبيق مبيدات صالحة",
        category="certification",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="PEST002",
        description="Product label has been read and understood",
        description_ar="تم قراءة وفهم ملصق المنتج",
        category="preparation",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="PEST003",
        description="Required PPE is available and in good condition",
        description_ar="معدات الحماية المطلوبة متوفرة وبحالة جيدة",
        category="ppe",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="PEST004",
        description="Mixing area is clear of bystanders",
        description_ar="منطقة الخلط خالية من المارة",
        category="area",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="PEST005",
        description="Wind conditions are suitable for spraying",
        description_ar="ظروف الرياح مناسبة للرش",
        category="weather",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="PEST006",
        description="REI posting signs are ready",
        description_ar="لافتات فترة إعادة الدخول جاهزة",
        category="rei",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="PEST007",
        description="Decontamination facilities are available",
        description_ar="مرافق إزالة التلوث متوفرة",
        category="decontamination",
        is_mandatory=True,
    ),
]

REI_ENTRY_CHECKLIST: list[SafetyChecklistItem] = [
    SafetyChecklistItem(
        item_id="REI001",
        description="REI period has been verified as expired",
        description_ar="تم التحقق من انتهاء فترة إعادة الدخول",
        category="rei",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="REI002",
        description="Worker is wearing required PPE for early entry (if applicable)",
        description_ar="العامل يرتدي معدات الحماية المطلوبة للدخول المبكر (إن وجد)",
        category="ppe",
        is_mandatory=True,
    ),
    SafetyChecklistItem(
        item_id="REI003",
        description="Worker has been informed of recent pesticide applications",
        description_ar="تم إبلاغ العامل بتطبيقات المبيدات الأخيرة",
        category="information",
        is_mandatory=True,
    ),
]


class SafetyComplianceManager:
    """
    Safety compliance manager - مدير الامتثال للسلامة

    Manages safety compliance including REI zones, PPE requirements,
    certifications, and safety violations.
    """

    def __init__(
        self,
        workers: list[Worker] | None = None,
        rei_zones: list[REIZone] | None = None,
        violations: list[SafetyViolation] | None = None,
    ):
        self.workers: list[Worker] = workers or []
        self.rei_zones: list[REIZone] = rei_zones or []
        self.violations: list[SafetyViolation] = violations or []

        # Indexes
        self._workers_by_id: dict[str, Worker] = {}
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Rebuild internal indexes"""
        self._workers_by_id = {w.worker_id: w for w in self.workers}

    def add_worker(self, worker: Worker) -> None:
        """Add a worker"""
        self.workers.append(worker)
        self._workers_by_id[worker.worker_id] = worker

    def add_rei_zone(self, rei_zone: REIZone) -> None:
        """Add an REI zone"""
        self.rei_zones.append(rei_zone)

    def add_violation(self, violation: SafetyViolation) -> None:
        """Record a safety violation"""
        self.violations.append(violation)

    # ==================== REI Zone Management ====================

    def create_rei_zone_from_pesticide_application(
        self,
        tenant_id: str,
        farm_id: str,
        field_id: str,
        pesticide_application_id: str,
        pesticide_id: str,
        pesticide_name: str,
        pesticide_name_ar: str,
        application_time: datetime,
        rei_hours: int,
        area_hectares: float = 0.0,
        boundary_coordinates: list[tuple[float, float]] | None = None,
        early_entry_allowed: bool = False,
        early_entry_tasks: list[str] | None = None,
        early_entry_ppe: list[PPEType] | None = None,
    ) -> REIZone:
        """
        Create an REI zone from a pesticide application

        Integrates with pesticide_compliance module data.
        """
        zone = create_rei_zone(
            tenant_id=tenant_id,
            farm_id=farm_id,
            field_id=field_id,
            pesticide_application_id=pesticide_application_id,
            pesticide_id=pesticide_id,
            pesticide_name=pesticide_name,
            pesticide_name_ar=pesticide_name_ar,
            application_time=application_time,
            rei_hours=rei_hours,
            area_hectares=area_hectares,
            boundary_coordinates=boundary_coordinates or [],
            early_entry_allowed=early_entry_allowed,
            early_entry_tasks_allowed=early_entry_tasks or [],
            early_entry_ppe_required=early_entry_ppe or [],
        )

        self.add_rei_zone(zone)
        return zone

    def get_active_rei_zones(
        self,
        field_id: str | None = None,
        farm_id: str | None = None,
        check_time: datetime | None = None,
    ) -> list[REIZone]:
        """Get currently active REI zones"""
        check = check_time or datetime.now(UTC)
        active = []

        for zone in self.rei_zones:
            if not zone.is_currently_restricted(check):
                continue
            if field_id and zone.field_id != field_id:
                continue
            if farm_id and zone.farm_id != farm_id:
                continue
            active.append(zone)

        return active

    def check_rei_compliance(
        self,
        field_id: str,
        task_category: TaskCategory | None = None,
        check_time: datetime | None = None,
    ) -> REIComplianceResult:
        """
        Check REI compliance for field entry - فحص امتثال فترة إعادة الدخول

        Returns detailed compliance result with any active restrictions.
        """
        check = check_time or datetime.now(UTC)
        active_zones = self.get_active_rei_zones(field_id=field_id, check_time=check)

        if not active_zones:
            return REIComplianceResult(
                field_id=field_id,
                check_time=check,
                is_compliant=True,
                can_enter=True,
                requires_ppe=False,
                message_en="No active REI restrictions. Field is safe for entry.",
                message_ar="لا توجد قيود REI نشطة. الحقل آمن للدخول.",
            )

        # Analyze restrictions
        earliest_safe_entry = max(z.rei_expiry_time for z in active_zones)
        early_entry_ppe: list[PPEType] = []
        allowed_tasks: list[str] = []
        can_enter_early = False

        warnings_en = []
        warnings_ar = []

        for zone in active_zones:
            remaining = zone.get_remaining_hours(check)
            warnings_en.append(
                f"{zone.pesticide_name}: {remaining:.1f}h remaining until safe entry "
                f"(expires {zone.rei_expiry_time.strftime('%Y-%m-%d %H:%M')})"
            )
            warnings_ar.append(
                f"{zone.pesticide_name_ar}: {remaining:.1f} ساعة متبقية للدخول الآمن "
                f"(ينتهي {zone.rei_expiry_time.strftime('%Y-%m-%d %H:%M')})"
            )

            if zone.early_entry_allowed:
                can_enter_early = True
                early_entry_ppe.extend(zone.early_entry_ppe_required)
                allowed_tasks.extend(zone.early_entry_tasks_allowed)

        # Check if task is allowed for early entry
        can_enter = False
        requires_ppe = False

        if task_category and can_enter_early:
            if task_category.value in allowed_tasks:
                can_enter = True
                requires_ppe = True

        # Deduplicate PPE
        early_entry_ppe = list(set(early_entry_ppe))

        if can_enter:
            message_en = (
                f"Early entry allowed for {task_category.value if task_category else 'specified tasks'}. "
                f"Required PPE: {', '.join(p.value for p in early_entry_ppe)}"
            )
            message_ar = (
                f"يُسمح بالدخول المبكر لـ {task_category.value if task_category else 'المهام المحددة'}. "
                f"معدات الحماية المطلوبة: {', '.join(p.value for p in early_entry_ppe)}"
            )
        else:
            message_en = (
                f"Field entry restricted due to {len(active_zones)} active REI zone(s). "
                f"Safe entry after {earliest_safe_entry.strftime('%Y-%m-%d %H:%M')}."
            )
            message_ar = (
                f"الدخول للحقل مقيد بسبب {len(active_zones)} منطقة REI نشطة. "
                f"الدخول الآمن بعد {earliest_safe_entry.strftime('%Y-%m-%d %H:%M')}."
            )

        return REIComplianceResult(
            field_id=field_id,
            check_time=check,
            is_compliant=not active_zones,
            can_enter=can_enter,
            requires_ppe=requires_ppe,
            active_zones=active_zones,
            earliest_safe_entry=earliest_safe_entry,
            early_entry_ppe=early_entry_ppe,
            allowed_early_entry_tasks=list(set(allowed_tasks)),
            message_en=message_en,
            message_ar=message_ar,
            warnings_en=warnings_en,
            warnings_ar=warnings_ar,
        )

    def expire_rei_zones(self, check_time: datetime | None = None) -> list[REIZone]:
        """
        Mark expired REI zones as inactive

        Returns list of zones that were expired.
        """
        check = check_time or datetime.now(UTC)
        expired = []

        for zone in self.rei_zones:
            if zone.is_active and not zone.is_currently_restricted(check):
                zone.is_active = False
                zone.updated_at = check
                expired.append(zone)

        return expired

    # ==================== PPE Requirements ====================

    def get_ppe_requirements(
        self,
        task_category: TaskCategory,
        field_id: str | None = None,
        check_time: datetime | None = None,
    ) -> PPERequirementSet:
        """
        Get PPE requirements for a task/location - الحصول على متطلبات الحماية

        Considers both task requirements and any active REI zones.
        """
        # Start with base task requirements
        required_ppe = list(TASK_PPE_REQUIREMENTS.get(task_category, []))

        description_en = f"Standard PPE for {task_category.value}"
        description_ar = f"معدات الحماية القياسية لـ {task_category.value}"

        # Add REI zone requirements if applicable
        if field_id:
            rei_check = self.check_rei_compliance(
                field_id=field_id,
                task_category=task_category,
                check_time=check_time,
            )
            if rei_check.requires_ppe:
                required_ppe.extend(rei_check.early_entry_ppe)
                description_en += " + REI early entry PPE"
                description_ar += " + معدات الدخول المبكر REI"

        # Deduplicate
        required_ppe = list(set(required_ppe))

        return PPERequirementSet(
            required_ppe=required_ppe,
            task_category=task_category,
            description_en=description_en,
            description_ar=description_ar,
        )

    def verify_worker_ppe(
        self,
        worker_id: str,
        required_ppe: list[PPEType],
        actual_ppe: list[PPEType],
    ) -> SafetyCheckResult:
        """
        Verify worker has required PPE - التحقق من معدات حماية العامل
        """
        missing_ppe = [p for p in required_ppe if p not in actual_ppe]

        if not missing_ppe:
            return SafetyCheckResult(
                check_id=generate_id("CHK"),
                check_type="ppe_verification",
                status=SafetyCheckStatus.PASSED,
                worker_id=worker_id,
                message_en="All required PPE verified",
                message_ar="تم التحقق من جميع معدات الحماية المطلوبة",
            )

        # Create violation if PPE missing
        issues = [f"Missing {p.value}" for p in missing_ppe]
        issues_ar = [f"ينقص {p.value}" for p in missing_ppe]

        return SafetyCheckResult(
            check_id=generate_id("CHK"),
            check_type="ppe_verification",
            status=SafetyCheckStatus.FAILED,
            worker_id=worker_id,
            message_en=f"Missing required PPE: {', '.join(p.value for p in missing_ppe)}",
            message_ar=f"معدات الحماية المطلوبة ناقصة: {', '.join(p.value for p in missing_ppe)}",
            issues=issues,
            issues_ar=issues_ar,
            recommendations_en=["Provide worker with missing PPE before task begins"],
            recommendations_ar=["زود العامل بمعدات الحماية الناقصة قبل بدء المهمة"],
        )

    # ==================== Certification Validation ====================

    def verify_worker_certifications(
        self,
        worker_id: str,
        required_certifications: list[SafetyCertification],
        check_date: date | None = None,
    ) -> SafetyCheckResult:
        """
        Verify worker has valid required certifications

        Returns check result with any missing/expired certifications.
        """
        worker = self._workers_by_id.get(worker_id)
        if not worker:
            return SafetyCheckResult(
                check_id=generate_id("CHK"),
                check_type="certification_verification",
                status=SafetyCheckStatus.FAILED,
                worker_id=worker_id,
                message_en="Worker not found",
                message_ar="العامل غير موجود",
            )

        check_date = check_date or date.today()
        missing = []
        expired = []
        expiring_soon = []

        for cert_type in required_certifications:
            has_valid = False
            for cert in worker.certifications:
                if cert.certification_type == cert_type:
                    if cert.is_valid(check_date):
                        has_valid = True
                        # Check if expiring within 30 days
                        days_left = cert.days_until_expiry(check_date)
                        if days_left <= 30:
                            expiring_soon.append((cert_type, days_left))
                    else:
                        expired.append(cert_type)
                    break

            if not has_valid and cert_type not in expired:
                missing.append(cert_type)

        # Build result
        issues = []
        issues_ar = []
        recommendations_en = []
        recommendations_ar = []

        for cert_type in missing:
            issues.append(f"Missing certification: {cert_type.value}")
            issues_ar.append(f"شهادة مفقودة: {cert_type.value}")
            recommendations_en.append(f"Worker must obtain {cert_type.value} certification")
            recommendations_ar.append(f"يجب على العامل الحصول على شهادة {cert_type.value}")

        for cert_type in expired:
            issues.append(f"Expired certification: {cert_type.value}")
            issues_ar.append(f"شهادة منتهية: {cert_type.value}")
            recommendations_en.append(f"Worker must renew {cert_type.value} certification")
            recommendations_ar.append(f"يجب على العامل تجديد شهادة {cert_type.value}")

        warnings_en = []
        warnings_ar = []
        for cert_type, days_left in expiring_soon:
            warnings_en.append(f"{cert_type.value} certification expires in {days_left} days")
            warnings_ar.append(f"شهادة {cert_type.value} تنتهي في {days_left} يوم")

        if missing or expired:
            status = SafetyCheckStatus.FAILED
            message_en = f"Certification issues: {len(missing)} missing, {len(expired)} expired"
            message_ar = f"مشاكل الشهادات: {len(missing)} مفقودة، {len(expired)} منتهية"
        elif expiring_soon:
            status = SafetyCheckStatus.WARNING
            message_en = f"Certifications valid, but {len(expiring_soon)} expiring soon"
            message_ar = f"الشهادات صالحة، لكن {len(expiring_soon)} تنتهي قريباً"
        else:
            status = SafetyCheckStatus.PASSED
            message_en = "All required certifications are valid"
            message_ar = "جميع الشهادات المطلوبة صالحة"

        result = SafetyCheckResult(
            check_id=generate_id("CHK"),
            check_type="certification_verification",
            status=status,
            worker_id=worker_id,
            message_en=message_en,
            message_ar=message_ar,
            issues=issues,
            issues_ar=issues_ar,
            recommendations_en=recommendations_en + warnings_en,
            recommendations_ar=recommendations_ar + warnings_ar,
        )

        return result

    # ==================== Heat Stress Assessment ====================

    def assess_heat_stress(
        self,
        farm_id: str,
        temperature_c: float,
        humidity_percent: float,
        wind_speed_kmh: float = 0,
    ) -> HeatStressAssessment:
        """
        Assess heat stress risk for workers - تقييم خطر الإجهاد الحراري

        Based on temperature and humidity to calculate heat index
        and recommend work/rest cycles.
        """
        # Calculate heat index (simplified formula)
        # Full formula: https://www.weather.gov/media/epz/wxcalc/heatIndex.pdf
        if temperature_c < 27:
            heat_index_c = temperature_c
        else:
            c1 = -8.78469475556
            c2 = 1.61139411
            c3 = 2.33854883889
            c4 = -0.14611605
            c5 = -0.012308094
            c6 = -0.0164248277778
            c7 = 0.002211732
            c8 = 0.00072546
            c9 = -0.000003582

            T = temperature_c
            R = humidity_percent

            heat_index_c = (
                c1
                + c2 * T
                + c3 * R
                + c4 * T * R
                + c5 * T * T
                + c6 * R * R
                + c7 * T * T * R
                + c8 * T * R * R
                + c9 * T * T * R * R
            )

        # Adjust for wind (cooling effect)
        if wind_speed_kmh > 5:
            wind_adjustment = min(3, wind_speed_kmh * 0.1)
            heat_index_c -= wind_adjustment

        # Determine risk level
        if heat_index_c < 27:
            risk_level = HeatRiskLevel.LOW
            max_work_min = 60
            break_min = 10
            water_liters = 0.5
        elif heat_index_c < 32:
            risk_level = HeatRiskLevel.MODERATE
            max_work_min = 45
            break_min = 15
            water_liters = 0.75
        elif heat_index_c < 39:
            risk_level = HeatRiskLevel.HIGH
            max_work_min = 30
            break_min = 15
            water_liters = 1.0
        else:
            risk_level = HeatRiskLevel.EXTREME
            max_work_min = 15
            break_min = 30
            water_liters = 1.5

        # Generate precautions
        precautions_en = [
            "Ensure adequate water supply is available",
            "Take regular breaks in shaded areas",
            "Wear light, breathable clothing",
        ]
        precautions_ar = [
            "تأكد من توفر إمدادات مياه كافية",
            "خذ استراحات منتظمة في مناطق مظللة",
            "ارتدِ ملابس خفيفة وقابلة للتنفس",
        ]

        if risk_level in [HeatRiskLevel.HIGH, HeatRiskLevel.EXTREME]:
            precautions_en.extend(
                [
                    "Monitor workers for heat stress symptoms",
                    "Consider rescheduling heavy work to cooler hours",
                    "Have emergency cooling measures ready",
                ]
            )
            precautions_ar.extend(
                [
                    "راقب العمال بحثاً عن أعراض الإجهاد الحراري",
                    "فكر في إعادة جدولة العمل الشاق لساعات أبرد",
                    "جهّز تدابير تبريد الطوارئ",
                ]
            )

        if risk_level == HeatRiskLevel.EXTREME:
            message_en = (
                f"EXTREME HEAT RISK: Heat index {heat_index_c:.1f}C. "
                f"Limit outdoor work. Consider postponing non-essential tasks."
            )
            message_ar = (
                f"خطر حرارة شديد: مؤشر الحرارة {heat_index_c:.1f}م. "
                f"قلل العمل في الخارج. فكر في تأجيل المهام غير الضرورية."
            )
        else:
            message_en = (
                f"Heat risk level: {risk_level.value}. Heat index: {heat_index_c:.1f}C. "
                f"Work {max_work_min} min, rest {break_min} min. Drink {water_liters}L water/hour."
            )
            message_ar = (
                f"مستوى خطر الحرارة: {risk_level.value}. مؤشر الحرارة: {heat_index_c:.1f}م. "
                f"اعمل {max_work_min} دقيقة، استرح {break_min} دقيقة. اشرب {water_liters} لتر ماء/ساعة."
            )

        return HeatStressAssessment(
            assessment_id=generate_id("HEAT"),
            farm_id=farm_id,
            temperature_c=temperature_c,
            humidity_percent=humidity_percent,
            heat_index_c=round(heat_index_c, 1),
            wind_speed_kmh=wind_speed_kmh,
            risk_level=risk_level,
            max_continuous_work_minutes=max_work_min,
            required_break_minutes=break_min,
            water_intake_liters_per_hour=water_liters,
            message_en=message_en,
            message_ar=message_ar,
            precautions_en=precautions_en,
            precautions_ar=precautions_ar,
        )

    # ==================== Pre-Task Safety Check ====================

    def create_pre_task_safety_check(
        self,
        tenant_id: str,
        farm_id: str,
        task: Task,
        worker_id: str,
    ) -> PreTaskSafetyCheck:
        """
        Create a pre-task safety check for a worker - إنشاء فحص سلامة قبل المهمة
        """
        # Get appropriate checklist
        checklist = list(GENERAL_SAFETY_CHECKLIST)

        if task.category == TaskCategory.PESTICIDE_APPLICATION:
            checklist.extend(PESTICIDE_SAFETY_CHECKLIST)

        if task.field_id:
            rei_zones = self.get_active_rei_zones(field_id=task.field_id)
            if rei_zones:
                checklist.extend(REI_ENTRY_CHECKLIST)

        # Get required PPE
        ppe_req = self.get_ppe_requirements(
            task_category=task.category,
            field_id=task.field_id,
        )

        # Get required certifications
        required_certs = []
        if task.category == TaskCategory.PESTICIDE_APPLICATION:
            required_certs.append(SafetyCertification.PESTICIDE_APPLICATOR)
        if task.requirements and task.requirements.required_certifications:
            required_certs.extend(task.requirements.required_certifications)

        # Check REI zone
        rei_zone_id = None
        if task.field_id:
            rei_zones = self.get_active_rei_zones(field_id=task.field_id)
            if rei_zones:
                rei_zone_id = rei_zones[0].zone_id

        return PreTaskSafetyCheck(
            check_id=generate_id("PSC"),
            tenant_id=tenant_id,
            farm_id=farm_id,
            task_id=task.task_id,
            worker_id=worker_id,
            checklist_items=checklist,
            completed_items=[],
            ppe_verified=[],
            ppe_missing=ppe_req.required_ppe,
            rei_check_passed=not bool(rei_zone_id),
            rei_zone_id=rei_zone_id,
            certifications_verified=False,
            missing_certifications=list(set(required_certs)),
        )

    def complete_safety_check_item(
        self,
        check: PreTaskSafetyCheck,
        item_id: str,
    ) -> bool:
        """Mark a safety check item as completed"""
        if item_id not in [i.item_id for i in check.checklist_items]:
            return False
        if item_id not in check.completed_items:
            check.completed_items.append(item_id)
        return True

    def verify_ppe_item(
        self,
        check: PreTaskSafetyCheck,
        ppe_type: PPEType,
    ) -> bool:
        """Verify a PPE item is present"""
        if ppe_type in check.ppe_missing:
            check.ppe_missing.remove(ppe_type)
        if ppe_type not in check.ppe_verified:
            check.ppe_verified.append(ppe_type)
        return True

    def finalize_safety_check(
        self,
        check: PreTaskSafetyCheck,
        approver_id: str,
    ) -> SafetyCheckResult:
        """
        Finalize and approve a pre-task safety check - إنهاء والموافقة على فحص السلامة
        """
        issues = []
        issues_ar = []

        # Check if all mandatory items completed
        if not check.is_complete():
            incomplete = [i for i in check.checklist_items if i.is_mandatory and i.item_id not in check.completed_items]
            for item in incomplete:
                issues.append(f"Incomplete: {item.description}")
                issues_ar.append(f"غير مكتمل: {item.description_ar}")

        # Check PPE
        if check.ppe_missing:
            for ppe in check.ppe_missing:
                issues.append(f"Missing PPE: {ppe.value}")
                issues_ar.append(f"معدات حماية ناقصة: {ppe.value}")

        # Check REI
        if not check.rei_check_passed and not check.rei_violation_acknowledged:
            issues.append("REI restriction not cleared")
            issues_ar.append("قيد فترة إعادة الدخول غير مُزال")

        # Check certifications
        if check.missing_certifications:
            for cert in check.missing_certifications:
                issues.append(f"Missing certification: {cert.value}")
                issues_ar.append(f"شهادة مفقودة: {cert.value}")

        if issues:
            status = SafetyCheckStatus.FAILED
            message_en = f"Safety check failed with {len(issues)} issue(s)"
            message_ar = f"فشل فحص السلامة مع {len(issues)} مشكلة"
        else:
            status = SafetyCheckStatus.PASSED
            check.is_approved = True
            check.approved_by = approver_id
            check.approved_at = datetime.now(UTC)
            message_en = "Safety check passed. Worker cleared for task."
            message_ar = "نجح فحص السلامة. العامل مخول للمهمة."

        return SafetyCheckResult(
            check_id=check.check_id,
            check_type="pre_task_safety_check",
            status=status,
            worker_id=check.worker_id,
            task_id=check.task_id,
            message_en=message_en,
            message_ar=message_ar,
            issues=issues,
            issues_ar=issues_ar,
        )

    # ==================== Safety Violations ====================

    def record_violation(
        self,
        tenant_id: str,
        farm_id: str,
        violation_type: SafetyViolationType,
        severity: str = "warning",
        worker_id: str | None = None,
        field_id: str | None = None,
        task_id: str | None = None,
        description: str = "",
        description_ar: str = "",
        pesticide_id: str | None = None,
        pesticide_name: str | None = None,
        missing_ppe: list[PPEType] | None = None,
        reported_by: str | None = None,
    ) -> SafetyViolation:
        """
        Record a safety violation - تسجيل مخالفة سلامة
        """
        violation = SafetyViolation(
            violation_id=generate_id("VIO"),
            tenant_id=tenant_id,
            farm_id=farm_id,
            field_id=field_id,
            worker_id=worker_id,
            task_id=task_id,
            violation_type=violation_type,
            severity=severity,
            description=description,
            description_ar=description_ar,
            related_pesticide_id=pesticide_id,
            related_pesticide_name=pesticide_name,
            missing_ppe=missing_ppe or [],
            reported_by=reported_by,
        )

        self.add_violation(violation)
        return violation

    def get_violations(
        self,
        worker_id: str | None = None,
        farm_id: str | None = None,
        field_id: str | None = None,
        violation_type: SafetyViolationType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        unresolved_only: bool = False,
    ) -> list[SafetyViolation]:
        """
        Get safety violations with optional filters - الحصول على مخالفات السلامة
        """
        violations = self.violations

        if worker_id:
            violations = [v for v in violations if v.worker_id == worker_id]
        if farm_id:
            violations = [v for v in violations if v.farm_id == farm_id]
        if field_id:
            violations = [v for v in violations if v.field_id == field_id]
        if violation_type:
            violations = [v for v in violations if v.violation_type == violation_type]
        if start_date:
            violations = [v for v in violations if v.incident_time >= start_date]
        if end_date:
            violations = [v for v in violations if v.incident_time <= end_date]
        if unresolved_only:
            violations = [v for v in violations if not v.is_resolved]

        return violations

    def resolve_violation(
        self,
        violation_id: str,
        resolved_by: str,
        resolution_notes: str = "",
        resolution_notes_ar: str = "",
    ) -> SafetyViolation | None:
        """
        Mark a violation as resolved - تعليم المخالفة كمحلولة
        """
        for violation in self.violations:
            if violation.violation_id == violation_id:
                violation.is_resolved = True
                violation.resolved_by = resolved_by
                violation.resolved_at = datetime.now(UTC)
                violation.resolution_notes = resolution_notes
                violation.resolution_notes_ar = resolution_notes_ar
                violation.updated_at = datetime.now(UTC)
                return violation
        return None

    def get_safety_summary(
        self,
        farm_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:
        """
        Get safety summary statistics - الحصول على ملخص إحصائيات السلامة
        """
        violations = self.get_violations(
            farm_id=farm_id,
            start_date=start_date,
            end_date=end_date,
        )

        by_type = {}
        for v in violations:
            vtype = v.violation_type.value
            if vtype not in by_type:
                by_type[vtype] = 0
            by_type[vtype] += 1

        by_severity = {}
        for v in violations:
            if v.severity not in by_severity:
                by_severity[v.severity] = 0
            by_severity[v.severity] += 1

        unresolved = [v for v in violations if not v.is_resolved]
        resolved = [v for v in violations if v.is_resolved]

        active_rei_zones = self.get_active_rei_zones(farm_id=farm_id)

        return {
            "farm_id": farm_id,
            "period_start": start_date.isoformat() if start_date else None,
            "period_end": end_date.isoformat() if end_date else None,
            "total_violations": len(violations),
            "unresolved_violations": len(unresolved),
            "resolved_violations": len(resolved),
            "violations_by_type": by_type,
            "violations_by_severity": by_severity,
            "active_rei_zones": len(active_rei_zones),
            "summary_en": (
                f"Farm has {len(violations)} total violations ({len(unresolved)} unresolved). "
                f"{len(active_rei_zones)} active REI zone(s)."
            ),
            "summary_ar": (
                f"المزرعة لديها {len(violations)} مخالفة إجمالية ({len(unresolved)} غير محلولة). "
                f"{len(active_rei_zones)} منطقة REI نشطة."
            ),
        }
