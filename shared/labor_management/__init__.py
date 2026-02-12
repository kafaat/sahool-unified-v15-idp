"""
SAHOOL Labor Management Module - وحدة إدارة العمالة

Comprehensive labor management for agricultural operations including:
- Worker scheduling and assignment - جدولة وتعيين العمال
- Task tracking and completion - تتبع المهام وإكمالها
- Attendance and timesheet management - إدارة الحضور والجدول الزمني
- Worker skill tracking - تتبع مهارات العمال
- Safety compliance (PPE, REI zones) - الامتثال للسلامة

Features:
- Skill-based task matching - مطابقة المهام بناءً على المهارات
- REI (Re-Entry Interval) zone integration with pesticide_compliance module
- PPE requirement tracking - تتبع متطلبات معدات الحماية الشخصية
- Heat stress monitoring - مراقبة الإجهاد الحراري
- Bilingual Arabic/English support - دعم ثنائي اللغة عربي/إنجليزي

Usage Example:
    ```python
    from shared.labor_management import (
        Worker, Task, LaborScheduler, SafetyComplianceManager,
        TaskCategory, SchedulingStrategy, create_worker, create_task
    )

    # Create a worker
    worker = create_worker(
        tenant_id="farm_001",
        farm_id="FARM-001",
        first_name="Mohammed",
        last_name="Ahmed",
        first_name_ar="محمد",
        last_name_ar="أحمد",
        phone="+966501234567"
    )

    # Create a task
    task = create_task(
        tenant_id="farm_001",
        farm_id="FARM-001",
        title="Apply nitrogen fertilizer",
        title_ar="تطبيق سماد النيتروجين",
        category=TaskCategory.FERTILIZATION,
        field_id="FIELD-003"
    )

    # Schedule workers
    scheduler = LaborScheduler(workers=[worker], tasks=[task])
    result = scheduler.bulk_schedule(strategy=SchedulingStrategy.SKILL_PRIORITY)

    # Check safety compliance
    safety_manager = SafetyComplianceManager(workers=[worker])
    rei_check = safety_manager.check_rei_compliance(
        field_id="FIELD-003",
        task_category=TaskCategory.FERTILIZATION
    )
    ```

Version: 1.0.0
"""

# Models - Worker, Task, Schedule, Attendance
from .models import (
    AttendanceRecord,
    AttendanceStatus,
    # Data Classes
    BilingualText,
    EmergencyContact,
    LeaveRequest,
    LeaveType,
    PPEType,
    PreTaskSafetyCheck,
    REIZone,
    SafetyCertification,
    SafetyChecklistItem,
    SafetyViolation,
    SafetyViolationType,
    SkillCategory,
    SkillLevel,
    Task,
    TaskCategory,
    TaskPriority,
    TaskRequirement,
    TaskStatus,
    Timesheet,
    Worker,
    WorkerCertification,
    WorkerSchedule,
    WorkerSkill,
    # Enums
    WorkerStatus,
    WorkerType,
    WorkShift,
    create_rei_zone,
    create_task,
    create_worker,
    # Factory Functions
    generate_id,
)

# Safety - REI zones, PPE, compliance
from .safety import (
    GENERAL_SAFETY_CHECKLIST,
    PESTICIDE_SAFETY_CHECKLIST,
    REI_ENTRY_CHECKLIST,
    # Constants
    TASK_PPE_REQUIREMENTS,
    HeatRiskLevel,
    HeatStressAssessment,
    # Data Classes
    PPERequirementSet,
    REIComplianceResult,
    SafetyCheckResult,
    # Enums
    SafetyCheckStatus,
    # Main Class
    SafetyComplianceManager,
)

# Scheduler - Worker scheduling algorithms
from .scheduler import (
    # Main Class
    LaborScheduler,
    # Data Classes
    SchedulingConflict,
    SchedulingConflictType,
    SchedulingResult,
    # Enums
    SchedulingStrategy,
    TaskAssignment,
    WorkerAvailability,
    WorkerScore,
)

__all__ = [
    # ==================== Models ====================
    # Enums
    "WorkerStatus",
    "WorkerType",
    "TaskStatus",
    "TaskPriority",
    "TaskCategory",
    "SkillLevel",
    "SkillCategory",
    "AttendanceStatus",
    "LeaveType",
    "SafetyViolationType",
    "SafetyCertification",
    "PPEType",
    # Data Classes
    "BilingualText",
    "WorkerSkill",
    "WorkerCertification",
    "EmergencyContact",
    "Worker",
    "TaskRequirement",
    "Task",
    "WorkShift",
    "WorkerSchedule",
    "AttendanceRecord",
    "LeaveRequest",
    "Timesheet",
    "SafetyViolation",
    "REIZone",
    "SafetyChecklistItem",
    "PreTaskSafetyCheck",
    # Factory Functions
    "generate_id",
    "create_worker",
    "create_task",
    "create_rei_zone",
    # ==================== Scheduler ====================
    # Enums
    "SchedulingStrategy",
    "SchedulingConflictType",
    # Data Classes
    "SchedulingConflict",
    "WorkerAvailability",
    "TaskAssignment",
    "SchedulingResult",
    "WorkerScore",
    # Main Class
    "LaborScheduler",
    # ==================== Safety ====================
    # Enums
    "SafetyCheckStatus",
    "HeatRiskLevel",
    # Data Classes
    "PPERequirementSet",
    "SafetyCheckResult",
    "HeatStressAssessment",
    "REIComplianceResult",
    # Constants
    "TASK_PPE_REQUIREMENTS",
    "GENERAL_SAFETY_CHECKLIST",
    "PESTICIDE_SAFETY_CHECKLIST",
    "REI_ENTRY_CHECKLIST",
    # Main Class
    "SafetyComplianceManager",
]

__version__ = "1.0.0"
