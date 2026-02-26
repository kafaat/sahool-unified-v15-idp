# Labor Management Module - وحدة إدارة العمالة

Workforce scheduling, safety compliance, and attendance tracking for agricultural operations on the SAHOOL platform. Provides skill-based task matching, Re-Entry Interval (REI) zone enforcement, PPE requirement management, heat stress assessment, and safety violation tracking with full Arabic/English bilingual support.

**Version**: 1.0.0 | **Python**: 3.11+

## File Structure

```
shared/labor_management/
├── __init__.py    # Public API and re-exports
├── models.py      # Worker, Task, WorkerSchedule, AttendanceRecord, REIZone, safety models
├── safety.py      # SafetyComplianceManager, heat stress, PPE verification, pre-task checks
└── scheduler.py   # LaborScheduler, skill-based matching, conflict detection
```

## Key Components

### Worker Model
Tracks personal details, skill set (`WorkerSkill` with `SkillCategory` and `SkillLevel`), certifications (`WorkerCertification`), availability schedule, emergency contacts, and accumulated leave requests. Factory function: `create_worker()`.

### Task Model
Includes bilingual title/description, `TaskCategory`, `TaskPriority`, field assignment, required skills and certifications, estimated hours, and PPE requirements. Factory function: `create_task()`.

### Task Categories (`TaskCategory`)
`IRRIGATION`, `FERTILIZATION`, `PESTICIDE_APPLICATION`, `HARVESTING`, `PRUNING`, `PLANTING`, `WEEDING`, `SOIL_PREPARATION`, `EQUIPMENT_MAINTENANCE`, `GREENHOUSE_WORK`, `SCOUTING`, `PACKING`, `QUALITY_CONTROL`, `LIVESTOCK`, `GENERAL_LABOR`

### Scheduling Strategies (`SchedulingStrategy`)

| Strategy | Description |
|----------|-------------|
| `SKILL_PRIORITY` | Assign the most skilled available worker first |
| `WORKLOAD_BALANCE` | Distribute tasks evenly across the workforce |
| `AVAILABILITY_FIRST` | Assign any available worker regardless of skill level |
| `COST_OPTIMIZED` | Minimize total labor cost |
| `SAFETY_PRIORITY` | Prioritize workers with the most relevant safety certifications |

### `SafetyComplianceManager`
- REI zone creation from pesticide applications and expiry tracking
- `check_rei_compliance()`: field entry check with earliest safe-entry time and early-entry PPE requirements
- `get_ppe_requirements()`: combines task-category defaults with active REI zone overrides
- `verify_worker_ppe()`: confirms a worker has all required PPE items
- `verify_worker_certifications()`: validates certification validity and warns on near-expiry
- `assess_heat_stress()`: calculates heat index, risk level, work/rest cycles, and water intake
- Pre-task safety checklists: general, pesticide-specific, and REI-entry checklists
- Safety violation recording and resolution workflow

### Standard PPE by Task (selected)

| Task | Required PPE |
|------|-------------|
| `PESTICIDE_APPLICATION` | Gloves, respirator, goggles, coverall, boots |
| `FERTILIZATION` | Gloves, goggles, boots |
| `HARVESTING` | Gloves, hat, boots |
| `EQUIPMENT_MAINTENANCE` | Gloves, goggles, ear protection, boots |

## Usage Examples

### Create Workers and Tasks

```python
from shared.labor_management import (
    create_worker, create_task, WorkerType, TaskCategory, TaskPriority,
    SkillCategory, SkillLevel, WorkerSkill,
)

worker = create_worker(
    tenant_id="farm_001",
    farm_id="FARM-001",
    first_name="Mohammed",
    last_name="Al-Harbi",
    first_name_ar="محمد",
    last_name_ar="الحربي",
    phone="+966501234567",
    worker_type=WorkerType.PERMANENT,
)
worker.skills.append(WorkerSkill(
    category=SkillCategory.PESTICIDE_APPLICATION,
    level=SkillLevel.EXPERT,
    years_experience=5,
))

task = create_task(
    tenant_id="farm_001",
    farm_id="FARM-001",
    title="Apply pre-emergent herbicide",
    title_ar="تطبيق مبيد الأعشاب قبل الإنبات",
    category=TaskCategory.PESTICIDE_APPLICATION,
    field_id="FIELD-003",
    priority=TaskPriority.HIGH,
    estimated_hours=3.0,
)
```

### Schedule Workers

```python
from shared.labor_management import LaborScheduler, SchedulingStrategy

scheduler = LaborScheduler(workers=[worker], tasks=[task])

# Assign one task
assignment = scheduler.schedule_task(task, strategy=SchedulingStrategy.SKILL_PRIORITY)
if assignment:
    print(f"Assigned to: {assignment.worker_id}, score: {assignment.score:.2f}")

# Bulk-schedule all pending tasks
result = scheduler.bulk_schedule(strategy=SchedulingStrategy.WORKLOAD_BALANCE)
print(f"Assigned: {result.assignments_made}, conflicts: {len(result.conflicts)}")
for conflict in result.conflicts:
    print(f"  Conflict: {conflict.conflict_type} - {conflict.message_en}")
```

### Safety Compliance Checks

```python
from shared.labor_management import (
    SafetyComplianceManager, TaskCategory, PPEType, SafetyCertification,
)
from datetime import datetime, timezone

safety = SafetyComplianceManager(workers=[worker])

# Register an REI zone after pesticide application
rei_zone = safety.create_rei_zone_from_pesticide_application(
    tenant_id="farm_001",
    farm_id="FARM-001",
    field_id="FIELD-003",
    pesticide_application_id="APP-789",
    pesticide_id="PEST-001",
    pesticide_name="Glyphosate 360",
    pesticide_name_ar="جليفوسات 360",
    application_time=datetime.now(timezone.utc),
    rei_hours=12,
    early_entry_allowed=True,
    early_entry_tasks=["scouting"],
    early_entry_ppe=[PPEType.GLOVES, PPEType.BOOTS],
)

# Check if a worker can enter FIELD-003 now
rei_result = safety.check_rei_compliance(
    field_id="FIELD-003",
    task_category=TaskCategory.SCOUTING,
)
print(f"Can enter: {rei_result.can_enter}")
print(f"Message  : {rei_result.message_en}")
print(f"Arabic   : {rei_result.message_ar}")

# Verify certifications
cert_result = safety.verify_worker_certifications(
    worker_id=worker.worker_id,
    required_certifications=[SafetyCertification.PESTICIDE_APPLICATOR],
)
print(f"Cert status: {cert_result.status}")

# Assess heat stress at current conditions
heat = safety.assess_heat_stress(
    farm_id="FARM-001",
    temperature_c=42.0,
    humidity_percent=35.0,
    wind_speed_kmh=8.0,
)
print(f"Risk level : {heat.risk_level}")
print(f"Work cycle : {heat.max_continuous_work_minutes} min work / "
      f"{heat.required_break_minutes} min rest")
print(f"Water      : {heat.water_intake_liters_per_hour} L/hr")
```

## Integration Notes

- Integrates with `shared.pesticide_compliance` for REI hour data when creating REI zones.
- `LaborScheduler` detects conflicts: `WORKER_UNAVAILABLE`, `SKILL_MISMATCH`, `CERTIFICATION_MISSING`, `CERTIFICATION_EXPIRED`, `REI_RESTRICTION`, `DOUBLE_BOOKING`, `ON_LEAVE`.
- Heat index calculation uses the NWS Steadman formula; wind cooling adjustment applied above 5 km/h.
- Bilingual messages throughout (`message_en` / `message_ar`) support Arabic-first farmer workflows.
- Connect attendance and timesheet records to payroll via `task-service` (port 8103).
