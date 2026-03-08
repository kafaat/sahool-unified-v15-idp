"""
Labor Management Models - نماذج إدارة العمالة

Data models for worker scheduling, task management, attendance tracking,
skill management, and safety compliance.

Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from enum import StrEnum
from uuid import uuid4

# ==================== Enums ====================


class WorkerStatus(StrEnum):
    """Worker employment status - حالة توظيف العامل"""

    ACTIVE = "active"  # نشط
    INACTIVE = "inactive"  # غير نشط
    ON_LEAVE = "on_leave"  # في إجازة
    TERMINATED = "terminated"  # منهي الخدمة
    SUSPENDED = "suspended"  # موقوف


class WorkerType(StrEnum):
    """Worker employment type - نوع التوظيف"""

    FULL_TIME = "full_time"  # دوام كامل
    PART_TIME = "part_time"  # دوام جزئي
    SEASONAL = "seasonal"  # موسمي
    CONTRACT = "contract"  # عقد
    DAILY = "daily"  # يومي


class TaskStatus(StrEnum):
    """Task status - حالة المهمة"""

    PENDING = "pending"  # قيد الانتظار
    ASSIGNED = "assigned"  # معينة
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    COMPLETED = "completed"  # مكتملة
    CANCELLED = "cancelled"  # ملغاة
    ON_HOLD = "on_hold"  # معلقة
    BLOCKED = "blocked"  # محظورة (e.g., due to REI)


class TaskPriority(StrEnum):
    """Task priority levels - مستويات أولوية المهمة"""

    CRITICAL = "critical"  # حرج
    HIGH = "high"  # عالي
    MEDIUM = "medium"  # متوسط
    LOW = "low"  # منخفض


class TaskCategory(StrEnum):
    """Task category types - أنواع فئات المهام"""

    PLANTING = "planting"  # زراعة
    IRRIGATION = "irrigation"  # ري
    FERTILIZATION = "fertilization"  # تسميد
    PESTICIDE_APPLICATION = "pesticide_application"  # تطبيق المبيدات
    HARVESTING = "harvesting"  # حصاد
    PRUNING = "pruning"  # تقليم
    WEEDING = "weeding"  # إزالة الأعشاب
    SOIL_PREPARATION = "soil_preparation"  # تحضير التربة
    EQUIPMENT_MAINTENANCE = "equipment_maintenance"  # صيانة المعدات
    SCOUTING = "scouting"  # مراقبة الحقل
    GREENHOUSE_WORK = "greenhouse_work"  # عمل البيوت المحمية
    LIVESTOCK = "livestock"  # الماشية
    GENERAL_LABOR = "general_labor"  # عمالة عامة
    QUALITY_CONTROL = "quality_control"  # مراقبة الجودة
    PACKING = "packing"  # تعبئة


class SkillLevel(StrEnum):
    """Skill proficiency level - مستوى إتقان المهارة"""

    NONE = "none"  # لا يوجد
    BEGINNER = "beginner"  # مبتدئ
    INTERMEDIATE = "intermediate"  # متوسط
    ADVANCED = "advanced"  # متقدم
    EXPERT = "expert"  # خبير


class SkillCategory(StrEnum):
    """Skill category - فئة المهارة"""

    EQUIPMENT_OPERATION = "equipment_operation"  # تشغيل المعدات
    PESTICIDE_HANDLING = "pesticide_handling"  # التعامل مع المبيدات
    IRRIGATION_SYSTEMS = "irrigation_systems"  # أنظمة الري
    CROP_MANAGEMENT = "crop_management"  # إدارة المحاصيل
    HARVESTING = "harvesting"  # الحصاد
    MACHINERY = "machinery"  # الآلات
    LIVESTOCK = "livestock"  # الماشية
    GREENHOUSE = "greenhouse"  # البيوت المحمية
    ORGANIC_FARMING = "organic_farming"  # الزراعة العضوية
    FIRST_AID = "first_aid"  # الإسعافات الأولية
    SAFETY = "safety"  # السلامة


class AttendanceStatus(StrEnum):
    """Attendance status - حالة الحضور"""

    PRESENT = "present"  # حاضر
    ABSENT = "absent"  # غائب
    LATE = "late"  # متأخر
    EARLY_LEAVE = "early_leave"  # مغادرة مبكرة
    HALF_DAY = "half_day"  # نصف يوم
    ON_LEAVE = "on_leave"  # في إجازة
    HOLIDAY = "holiday"  # عطلة


class LeaveType(StrEnum):
    """Leave type - نوع الإجازة"""

    ANNUAL = "annual"  # سنوية
    SICK = "sick"  # مرضية
    EMERGENCY = "emergency"  # طارئة
    MATERNITY = "maternity"  # أمومة
    PATERNITY = "paternity"  # أبوة
    UNPAID = "unpaid"  # بدون راتب
    PILGRIMAGE = "pilgrimage"  # حج
    COMPENSATORY = "compensatory"  # تعويضية


class SafetyViolationType(StrEnum):
    """Safety violation type - نوع مخالفة السلامة"""

    REI_VIOLATION = "rei_violation"  # انتهاك فترة إعادة الدخول
    PPE_MISSING = "ppe_missing"  # معدات الحماية مفقودة
    PPE_IMPROPER = "ppe_improper"  # معدات حماية غير مناسبة
    UNAUTHORIZED_ENTRY = "unauthorized_entry"  # دخول غير مصرح
    CERTIFICATION_EXPIRED = "certification_expired"  # شهادة منتهية
    UNSAFE_PRACTICE = "unsafe_practice"  # ممارسة غير آمنة
    HEAT_STRESS = "heat_stress"  # إجهاد حراري
    INJURY = "injury"  # إصابة


class SafetyCertification(StrEnum):
    """Safety certification types - أنواع شهادات السلامة"""

    PESTICIDE_APPLICATOR = "pesticide_applicator"  # رخصة تطبيق المبيدات
    EQUIPMENT_OPERATOR = "equipment_operator"  # رخصة تشغيل المعدات
    FORKLIFT_OPERATOR = "forklift_operator"  # رخصة الرافعة الشوكية
    FIRST_AID = "first_aid"  # شهادة الإسعافات الأولية
    FIRE_SAFETY = "fire_safety"  # شهادة السلامة من الحرائق
    CHEMICAL_HANDLING = "chemical_handling"  # شهادة التعامل مع المواد الكيميائية
    HEIGHT_WORK = "height_work"  # شهادة العمل على ارتفاعات


class PPEType(StrEnum):
    """Personal Protective Equipment types - أنواع معدات الحماية الشخصية"""

    GLOVES = "gloves"  # قفازات
    RESPIRATOR = "respirator"  # كمامة/جهاز تنفس
    GOGGLES = "goggles"  # نظارات واقية
    FACE_SHIELD = "face_shield"  # واقي الوجه
    COVERALL = "coverall"  # بدلة كاملة
    BOOTS = "boots"  # أحذية
    HAT = "hat"  # قبعة
    APRON = "apron"  # مريلة
    EAR_PROTECTION = "ear_protection"  # حماية الأذن


# ==================== Data Classes ====================


@dataclass
class BilingualText:
    """Bilingual text container - نص ثنائي اللغة"""

    en: str
    ar: str

    def get(self, lang: str = "en") -> str:
        """Get text in specified language"""
        return self.ar if lang == "ar" else self.en


@dataclass
class WorkerSkill:
    """Worker skill record - سجل مهارة العامل"""

    skill_id: str
    skill_name: str
    skill_name_ar: str
    category: SkillCategory
    level: SkillLevel

    # Certification details
    is_certified: bool = False
    certification_number: str | None = None
    certification_date: date | None = None
    certification_expiry: date | None = None
    certifying_authority: str | None = None

    # Verification
    verified_by: str | None = None
    verified_date: date | None = None

    notes: str = ""
    notes_ar: str = ""

    def is_certification_valid(self, check_date: date | None = None) -> bool:
        """Check if certification is still valid"""
        if not self.is_certified or not self.certification_expiry:
            return False
        check = check_date or date.today()
        return check <= self.certification_expiry

    def days_until_expiry(self, check_date: date | None = None) -> int | None:
        """Get days until certification expires"""
        if not self.certification_expiry:
            return None
        check = check_date or date.today()
        return (self.certification_expiry - check).days


@dataclass
class WorkerCertification:
    """Safety certification record - سجل شهادة السلامة"""

    certification_id: str
    certification_type: SafetyCertification
    name: str
    name_ar: str

    issue_date: date
    expiry_date: date
    issuing_authority: str
    issuing_authority_ar: str
    certificate_number: str

    # Verification
    is_verified: bool = True
    verified_by: str | None = None
    verified_date: date | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_valid(self, check_date: date | None = None) -> bool:
        """Check if certification is still valid"""
        check = check_date or date.today()
        return self.is_verified and check <= self.expiry_date

    def days_until_expiry(self, check_date: date | None = None) -> int:
        """Get days until certification expires"""
        check = check_date or date.today()
        return (self.expiry_date - check).days


@dataclass
class EmergencyContact:
    """Emergency contact information - معلومات الاتصال في حالات الطوارئ"""

    name: str
    relationship: str
    relationship_ar: str
    phone: str
    alternate_phone: str | None = None
    address: str | None = None


@dataclass
class Worker:
    """
    Farm worker profile - ملف العامل الزراعي

    Contains comprehensive worker information including personal details,
    employment info, skills, certifications, and safety records.
    """

    worker_id: str
    tenant_id: str
    farm_id: str

    # Personal info
    first_name: str
    last_name: str
    first_name_ar: str
    last_name_ar: str

    # Contact
    phone: str
    email: str | None = None
    address: str | None = None
    address_ar: str | None = None

    # Employment
    status: WorkerStatus = WorkerStatus.ACTIVE
    worker_type: WorkerType = WorkerType.FULL_TIME
    hire_date: date | None = None
    termination_date: date | None = None

    # Work details
    department: str = ""
    department_ar: str = ""
    position: str = ""
    position_ar: str = ""
    supervisor_id: str | None = None

    # Compensation
    hourly_rate: float | None = None
    daily_rate: float | None = None
    monthly_salary: float | None = None
    currency: str = "SAR"  # Saudi Riyal

    # Skills and certifications
    skills: list[WorkerSkill] = field(default_factory=list)
    certifications: list[WorkerCertification] = field(default_factory=list)

    # Safety
    emergency_contact: EmergencyContact | None = None
    blood_type: str | None = None
    medical_conditions: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)

    # ID documents
    national_id: str | None = None
    iqama_number: str | None = None  # Saudi residence permit
    passport_number: str | None = None

    # Languages
    languages: list[str] = field(default_factory=lambda: ["ar"])
    preferred_language: str = "ar"

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str = ""
    notes_ar: str = ""

    @property
    def full_name(self) -> str:
        """Get full name in English"""
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name_ar(self) -> str:
        """Get full name in Arabic"""
        return f"{self.first_name_ar} {self.last_name_ar}"

    def has_skill(self, skill_category: SkillCategory, min_level: SkillLevel = SkillLevel.BEGINNER) -> bool:
        """Check if worker has a skill at minimum level"""
        skill_order = [
            SkillLevel.NONE,
            SkillLevel.BEGINNER,
            SkillLevel.INTERMEDIATE,
            SkillLevel.ADVANCED,
            SkillLevel.EXPERT,
        ]
        min_index = skill_order.index(min_level)

        for skill in self.skills:
            if skill.category == skill_category:
                skill_index = skill_order.index(skill.level)
                if skill_index >= min_index:
                    return True
        return False

    def has_valid_certification(self, cert_type: SafetyCertification, check_date: date | None = None) -> bool:
        """Check if worker has valid certification of given type"""
        return any(cert.certification_type == cert_type and cert.is_valid(check_date) for cert in self.certifications)

    def get_expiring_certifications(self, days_ahead: int = 30) -> list[WorkerCertification]:
        """Get certifications expiring within given days"""
        check_date = date.today()
        expiring = []
        for cert in self.certifications:
            if cert.is_valid() and cert.days_until_expiry(check_date) <= days_ahead:
                expiring.append(cert)
        return expiring


@dataclass
class TaskRequirement:
    """Task skill and certification requirements - متطلبات المهمة"""

    required_skills: list[tuple[SkillCategory, SkillLevel]] = field(default_factory=list)
    required_certifications: list[SafetyCertification] = field(default_factory=list)
    required_ppe: list[PPEType] = field(default_factory=list)

    min_workers: int = 1
    max_workers: int = 10

    # Physical requirements
    requires_heavy_lifting: bool = False
    requires_height_work: bool = False
    requires_confined_space: bool = False

    notes: str = ""
    notes_ar: str = ""


@dataclass
class Task:
    """
    Agricultural task - المهمة الزراعية

    Represents a work task that can be assigned to workers.
    Includes safety requirements and integration with pesticide compliance.
    """

    task_id: str
    tenant_id: str
    farm_id: str
    field_id: str | None = None

    # Task details
    title: str = ""
    title_ar: str = ""
    description: str = ""
    description_ar: str = ""

    category: TaskCategory = TaskCategory.GENERAL_LABOR
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING

    # Scheduling
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None

    estimated_hours: float = 1.0
    actual_hours: float | None = None

    # Assignment
    assigned_workers: list[str] = field(default_factory=list)  # Worker IDs
    supervisor_id: str | None = None
    created_by: str | None = None

    # Requirements
    requirements: TaskRequirement | None = None

    # Location
    location_description: str = ""
    location_description_ar: str = ""
    gps_coordinates: tuple[float, float] | None = None

    # Pesticide/Safety integration
    related_pesticide_application_id: str | None = None
    rei_restricted: bool = False
    rei_expiry_time: datetime | None = None
    safety_notes: str = ""
    safety_notes_ar: str = ""

    # Equipment
    required_equipment: list[str] = field(default_factory=list)

    # Completion
    completion_notes: str = ""
    completion_notes_ar: str = ""
    quality_rating: int | None = None  # 1-5

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_blocked_by_rei(self, check_time: datetime | None = None) -> bool:
        """Check if task is blocked due to REI restriction"""
        if not self.rei_restricted or not self.rei_expiry_time:
            return False
        check = check_time or datetime.now(UTC)
        return check < self.rei_expiry_time

    def get_rei_remaining_hours(self, check_time: datetime | None = None) -> float | None:
        """Get remaining REI hours"""
        if not self.rei_restricted or not self.rei_expiry_time:
            return None
        check = check_time or datetime.now(UTC)
        if check >= self.rei_expiry_time:
            return 0.0
        return (self.rei_expiry_time - check).total_seconds() / 3600


@dataclass
class WorkShift:
    """Work shift definition - تعريف وردية العمل"""

    shift_id: str
    name: str
    name_ar: str

    start_time: time
    end_time: time

    break_duration_minutes: int = 60

    # Days active (0=Monday, 6=Sunday)
    active_days: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5])

    # Premium rates
    is_night_shift: bool = False
    overtime_multiplier: float = 1.5

    notes: str = ""
    notes_ar: str = ""

    def get_duration_hours(self) -> float:
        """Get shift duration in hours excluding breaks"""
        start = datetime.combine(date.today(), self.start_time)
        end = datetime.combine(date.today(), self.end_time)
        if end < start:  # Overnight shift
            end += timedelta(days=1)
        total_minutes = (end - start).total_seconds() / 60
        return (total_minutes - self.break_duration_minutes) / 60


@dataclass
class WorkerSchedule:
    """
    Worker schedule assignment - تعيين جدول العامل

    Assigns a worker to a shift on specific dates.
    """

    schedule_id: str
    tenant_id: str
    farm_id: str
    worker_id: str
    shift_id: str

    # Date range
    start_date: date
    end_date: date

    # Assigned tasks for this schedule
    task_ids: list[str] = field(default_factory=list)

    # Override times (if different from shift)
    custom_start_time: time | None = None
    custom_end_time: time | None = None

    # Status
    is_confirmed: bool = False
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None

    # Notes
    notes: str = ""
    notes_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AttendanceRecord:
    """
    Worker attendance record - سجل حضور العامل

    Tracks daily attendance including clock in/out times.
    """

    attendance_id: str
    tenant_id: str
    farm_id: str
    worker_id: str

    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT

    # Clock times
    clock_in: datetime | None = None
    clock_out: datetime | None = None

    # Breaks
    break_start: datetime | None = None
    break_end: datetime | None = None
    total_break_minutes: int = 0

    # Hours
    scheduled_hours: float = 8.0
    worked_hours: float | None = None
    overtime_hours: float = 0.0

    # Location (for mobile clock-in)
    clock_in_location: tuple[float, float] | None = None
    clock_out_location: tuple[float, float] | None = None

    # Verification
    verified_by: str | None = None
    verified_at: datetime | None = None

    # Notes
    notes: str = ""
    notes_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def calculate_worked_hours(self) -> float | None:
        """Calculate worked hours from clock times"""
        if not self.clock_in or not self.clock_out:
            return None
        delta = self.clock_out - self.clock_in
        total_minutes = delta.total_seconds() / 60
        worked_minutes = total_minutes - self.total_break_minutes
        return worked_minutes / 60


@dataclass
class LeaveRequest:
    """
    Leave request - طلب إجازة
    """

    leave_id: str
    tenant_id: str
    farm_id: str
    worker_id: str

    leave_type: LeaveType
    start_date: date
    end_date: date

    reason: str = ""
    reason_ar: str = ""

    # Approval
    status: str = "pending"  # pending, approved, rejected
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejection_reason: str = ""
    rejection_reason_ar: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_duration_days(self) -> int:
        """Get leave duration in days"""
        return (self.end_date - self.start_date).days + 1


@dataclass
class Timesheet:
    """
    Weekly timesheet summary - ملخص الجدول الزمني الأسبوعي
    """

    timesheet_id: str
    tenant_id: str
    farm_id: str
    worker_id: str

    # Period
    week_start: date
    week_end: date

    # Attendance records
    attendance_records: list[AttendanceRecord] = field(default_factory=list)

    # Summary
    total_scheduled_hours: float = 0.0
    total_worked_hours: float = 0.0
    total_overtime_hours: float = 0.0
    total_absent_days: int = 0
    total_late_count: int = 0

    # Approval
    status: str = "draft"  # draft, submitted, approved, rejected
    submitted_at: datetime | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None

    notes: str = ""
    notes_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SafetyViolation:
    """
    Safety violation record - سجل مخالفة السلامة
    """

    violation_id: str
    tenant_id: str
    farm_id: str
    violation_type: SafetyViolationType

    # Optional identifiers
    field_id: str | None = None
    worker_id: str | None = None
    task_id: str | None = None

    severity: str = "warning"  # warning, minor, major, critical

    # Details
    description: str = ""
    description_ar: str = ""

    # REI-specific (if applicable)
    related_pesticide_id: str | None = None
    related_pesticide_name: str | None = None
    rei_expiry_time: datetime | None = None

    # PPE-specific (if applicable)
    missing_ppe: list[PPEType] = field(default_factory=list)

    # Location and time
    incident_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    incident_location: str = ""
    incident_location_ar: str = ""
    gps_coordinates: tuple[float, float] | None = None

    # Response
    corrective_action: str = ""
    corrective_action_ar: str = ""
    action_taken_by: str | None = None
    action_taken_at: datetime | None = None

    # Resolution
    is_resolved: bool = False
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    resolution_notes: str = ""
    resolution_notes_ar: str = ""

    # Metadata
    reported_by: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class REIZone:
    """
    Re-Entry Interval restricted zone - منطقة مقيدة بفترة إعادة الدخول

    Tracks areas that are temporarily restricted due to pesticide application.
    """

    zone_id: str
    tenant_id: str
    farm_id: str
    field_id: str

    # Pesticide application details
    pesticide_application_id: str
    pesticide_id: str
    pesticide_name: str
    pesticide_name_ar: str

    # REI period
    application_time: datetime
    rei_hours: int
    rei_expiry_time: datetime

    # Zone details
    zone_name: str = ""
    zone_name_ar: str = ""
    zone_description: str = ""
    zone_description_ar: str = ""

    # Boundaries (GeoJSON-compatible)
    boundary_coordinates: list[tuple[float, float]] = field(default_factory=list)
    area_hectares: float = 0.0

    # Early entry requirements
    early_entry_allowed: bool = False
    early_entry_ppe_required: list[PPEType] = field(default_factory=list)
    early_entry_tasks_allowed: list[str] = field(default_factory=list)

    # Status
    is_active: bool = True

    # Messages
    warning_message_en: str = ""
    warning_message_ar: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_currently_restricted(self, check_time: datetime | None = None) -> bool:
        """Check if zone is currently restricted"""
        if not self.is_active:
            return False
        check = check_time or datetime.now(UTC)
        return check < self.rei_expiry_time

    def get_remaining_hours(self, check_time: datetime | None = None) -> float:
        """Get remaining REI hours"""
        check = check_time or datetime.now(UTC)
        if check >= self.rei_expiry_time:
            return 0.0
        return (self.rei_expiry_time - check).total_seconds() / 3600


@dataclass
class SafetyChecklistItem:
    """Safety checklist item - عنصر قائمة التحقق من السلامة"""

    item_id: str
    description: str
    description_ar: str
    category: str
    is_mandatory: bool = True

    def __hash__(self):
        return hash(self.item_id)


@dataclass
class PreTaskSafetyCheck:
    """
    Pre-task safety check - فحص السلامة قبل المهمة

    Safety checklist completed before starting a task.
    """

    check_id: str
    tenant_id: str
    farm_id: str
    task_id: str
    worker_id: str

    # Checklist items
    checklist_items: list[SafetyChecklistItem] = field(default_factory=list)
    completed_items: list[str] = field(default_factory=list)  # Item IDs

    # PPE verification
    ppe_verified: list[PPEType] = field(default_factory=list)
    ppe_missing: list[PPEType] = field(default_factory=list)

    # REI check
    rei_check_passed: bool = True
    rei_zone_id: str | None = None
    rei_violation_acknowledged: bool = False

    # Certification verification
    certifications_verified: bool = True
    missing_certifications: list[SafetyCertification] = field(default_factory=list)

    # Overall status
    is_approved: bool = False
    approved_by: str | None = None
    approved_at: datetime | None = None

    # Notes
    notes: str = ""
    notes_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_complete(self) -> bool:
        """Check if all mandatory items are completed"""
        mandatory_ids = {item.item_id for item in self.checklist_items if item.is_mandatory}
        completed_ids = set(self.completed_items)
        return mandatory_ids.issubset(completed_ids)


# ==================== Helper Functions ====================


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique = uuid4().hex[:12]
    return f"{prefix}_{unique}" if prefix else unique


def create_worker(
    tenant_id: str,
    farm_id: str,
    first_name: str,
    last_name: str,
    first_name_ar: str,
    last_name_ar: str,
    phone: str,
    **kwargs,
) -> Worker:
    """Factory function to create a new worker"""
    return Worker(
        worker_id=generate_id("WRK"),
        tenant_id=tenant_id,
        farm_id=farm_id,
        first_name=first_name,
        last_name=last_name,
        first_name_ar=first_name_ar,
        last_name_ar=last_name_ar,
        phone=phone,
        **kwargs,
    )


def create_task(tenant_id: str, farm_id: str, title: str, title_ar: str, category: TaskCategory, **kwargs) -> Task:
    """Factory function to create a new task"""
    return Task(
        task_id=generate_id("TSK"),
        tenant_id=tenant_id,
        farm_id=farm_id,
        title=title,
        title_ar=title_ar,
        category=category,
        **kwargs,
    )


def create_rei_zone(
    tenant_id: str,
    farm_id: str,
    field_id: str,
    pesticide_application_id: str,
    pesticide_id: str,
    pesticide_name: str,
    pesticide_name_ar: str,
    application_time: datetime,
    rei_hours: int,
    **kwargs,
) -> REIZone:
    """Factory function to create a new REI zone"""
    rei_expiry_time = application_time + timedelta(hours=rei_hours)

    return REIZone(
        zone_id=generate_id("REI"),
        tenant_id=tenant_id,
        farm_id=farm_id,
        field_id=field_id,
        pesticide_application_id=pesticide_application_id,
        pesticide_id=pesticide_id,
        pesticide_name=pesticide_name,
        pesticide_name_ar=pesticide_name_ar,
        application_time=application_time,
        rei_hours=rei_hours,
        rei_expiry_time=rei_expiry_time,
        warning_message_en=f"RESTRICTED AREA: Re-entry prohibited until {rei_expiry_time.strftime('%Y-%m-%d %H:%M')} "
        f"due to {pesticide_name} application ({rei_hours}h REI)",
        warning_message_ar=f"منطقة مقيدة: يحظر الدخول حتى {rei_expiry_time.strftime('%Y-%m-%d %H:%M')} "
        f"بسبب تطبيق {pesticide_name_ar} (فترة إعادة الدخول {rei_hours} ساعة)",
        **kwargs,
    )
