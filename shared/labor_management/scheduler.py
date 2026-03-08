"""
Worker Scheduling Algorithms - خوارزميات جدولة العمال

Provides intelligent worker scheduling with:
- Skill-based task matching
- Availability-aware scheduling
- REI zone conflict detection
- Workload balancing
- Shift optimization

Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from enum import StrEnum

from .models import (
    LeaveRequest,
    PPEType,
    REIZone,
    SafetyCertification,
    SkillCategory,
    SkillLevel,
    Task,
    TaskCategory,
    TaskPriority,
    TaskStatus,
    Worker,
    WorkerSchedule,
    WorkerStatus,
    WorkShift,
)


class SchedulingStrategy(StrEnum):
    """Scheduling strategy options - خيارات استراتيجية الجدولة"""

    SKILL_PRIORITY = "skill_priority"  # أولوية المهارات - Assign most skilled workers first
    WORKLOAD_BALANCE = "workload_balance"  # توازن العبء - Distribute work evenly
    AVAILABILITY_FIRST = "availability_first"  # الإتاحة أولاً - Assign available workers
    COST_OPTIMIZED = "cost_optimized"  # تحسين التكلفة - Minimize labor cost
    SAFETY_PRIORITY = "safety_priority"  # أولوية السلامة - Prioritize safety certifications


class SchedulingConflictType(StrEnum):
    """Types of scheduling conflicts - أنواع تعارضات الجدولة"""

    WORKER_UNAVAILABLE = "worker_unavailable"  # العامل غير متاح
    SKILL_MISMATCH = "skill_mismatch"  # عدم تطابق المهارات
    CERTIFICATION_MISSING = "certification_missing"  # الشهادة مفقودة
    CERTIFICATION_EXPIRED = "certification_expired"  # الشهادة منتهية
    REI_RESTRICTION = "rei_restriction"  # قيود فترة إعادة الدخول
    OVERTIME_LIMIT = "overtime_limit"  # حد العمل الإضافي
    DOUBLE_BOOKING = "double_booking"  # حجز مزدوج
    ON_LEAVE = "on_leave"  # في إجازة
    MAX_WORKERS_REACHED = "max_workers_reached"  # الحد الأقصى للعمال


@dataclass
class SchedulingConflict:
    """Scheduling conflict details - تفاصيل تعارض الجدولة"""

    conflict_type: SchedulingConflictType
    worker_id: str | None = None
    task_id: str | None = None

    message_en: str = ""
    message_ar: str = ""

    # Additional details
    details: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.conflict_type.value}: {self.message_en}"


@dataclass
class WorkerAvailability:
    """Worker availability status - حالة إتاحة العامل"""

    worker_id: str
    worker_name: str
    worker_name_ar: str

    is_available: bool
    availability_date: date

    # Schedule details
    shift_id: str | None = None
    shift_start: time | None = None
    shift_end: time | None = None

    # Hours
    scheduled_hours: float = 0.0
    remaining_hours: float = 8.0
    overtime_hours: float = 0.0

    # Conflicts
    conflicts: list[SchedulingConflict] = field(default_factory=list)

    # Current assignments
    assigned_task_ids: list[str] = field(default_factory=list)


@dataclass
class TaskAssignment:
    """Task assignment result - نتيجة تعيين المهمة"""

    task_id: str
    worker_ids: list[str]

    assigned_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    assigned_by: str | None = None

    # Schedule
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None

    # Status
    is_successful: bool = True
    partial_assignment: bool = False

    # Conflicts/Warnings
    conflicts: list[SchedulingConflict] = field(default_factory=list)
    warnings_en: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)


@dataclass
class SchedulingResult:
    """Overall scheduling result - نتيجة الجدولة الشاملة"""

    # Assignments
    assignments: list[TaskAssignment] = field(default_factory=list)

    # Summary
    total_tasks: int = 0
    tasks_assigned: int = 0
    tasks_partially_assigned: int = 0
    tasks_unassigned: int = 0

    # Workers
    workers_assigned: int = 0
    total_worker_hours: float = 0.0

    # Issues
    conflicts: list[SchedulingConflict] = field(default_factory=list)

    # Messages
    summary_en: str = ""
    summary_ar: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class WorkerScore:
    """Scoring result for worker-task matching - نتيجة تسجيل تطابق العامل والمهمة"""

    worker_id: str
    task_id: str
    total_score: float = 0.0

    # Score components
    skill_score: float = 0.0
    availability_score: float = 0.0
    certification_score: float = 0.0
    workload_score: float = 0.0
    cost_score: float = 0.0

    # Eligibility
    is_eligible: bool = True
    ineligibility_reasons: list[str] = field(default_factory=list)


class LaborScheduler:
    """
    Labor scheduling engine - محرك جدولة العمالة

    Provides intelligent worker scheduling with skill matching,
    availability checking, and safety compliance.
    """

    def __init__(
        self,
        workers: list[Worker] | None = None,
        tasks: list[Task] | None = None,
        shifts: list[WorkShift] | None = None,
        schedules: list[WorkerSchedule] | None = None,
        leave_requests: list[LeaveRequest] | None = None,
        rei_zones: list[REIZone] | None = None,
    ):
        self.workers: list[Worker] = workers or []
        self.tasks: list[Task] = tasks or []
        self.shifts: list[WorkShift] = shifts or []
        self.schedules: list[WorkerSchedule] = schedules or []
        self.leave_requests: list[LeaveRequest] = leave_requests or []
        self.rei_zones: list[REIZone] = rei_zones or []

        # Indexes for quick lookup
        self._workers_by_id: dict[str, Worker] = {}
        self._tasks_by_id: dict[str, Task] = {}
        self._shifts_by_id: dict[str, WorkShift] = {}
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Rebuild internal indexes"""
        self._workers_by_id = {w.worker_id: w for w in self.workers}
        self._tasks_by_id = {t.task_id: t for t in self.tasks}
        self._shifts_by_id = {s.shift_id: s for s in self.shifts}

    def add_worker(self, worker: Worker) -> None:
        """Add a worker to the scheduler"""
        self.workers.append(worker)
        self._workers_by_id[worker.worker_id] = worker

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler"""
        self.tasks.append(task)
        self._tasks_by_id[task.task_id] = task

    def add_rei_zone(self, rei_zone: REIZone) -> None:
        """Add an REI zone restriction"""
        self.rei_zones.append(rei_zone)

    def get_worker(self, worker_id: str) -> Worker | None:
        """Get worker by ID"""
        return self._workers_by_id.get(worker_id)

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID"""
        return self._tasks_by_id.get(task_id)

    # ==================== Availability Checking ====================

    def check_worker_availability(
        self,
        worker_id: str,
        check_date: date,
        check_time: datetime | None = None,
    ) -> WorkerAvailability:
        """
        Check worker availability for a specific date - تحقق من إتاحة العامل

        Args:
            worker_id: Worker ID to check
            check_date: Date to check availability
            check_time: Optional time for REI zone checks

        Returns:
            WorkerAvailability with status and any conflicts
        """
        worker = self._workers_by_id.get(worker_id)
        if not worker:
            return WorkerAvailability(
                worker_id=worker_id,
                worker_name="Unknown",
                worker_name_ar="غير معروف",
                is_available=False,
                availability_date=check_date,
                conflicts=[
                    SchedulingConflict(
                        conflict_type=SchedulingConflictType.WORKER_UNAVAILABLE,
                        worker_id=worker_id,
                        message_en="Worker not found",
                        message_ar="العامل غير موجود",
                    )
                ],
            )

        conflicts = []

        # Check worker status
        if worker.status != WorkerStatus.ACTIVE:
            conflicts.append(
                SchedulingConflict(
                    conflict_type=SchedulingConflictType.WORKER_UNAVAILABLE,
                    worker_id=worker_id,
                    message_en=f"Worker status is {worker.status.value}",
                    message_ar=f"حالة العامل {worker.status.value}",
                )
            )

        # Check leave requests
        for leave in self.leave_requests:
            if (
                leave.worker_id == worker_id
                and leave.status == "approved"
                and leave.start_date <= check_date <= leave.end_date
            ):
                conflicts.append(
                    SchedulingConflict(
                        conflict_type=SchedulingConflictType.ON_LEAVE,
                        worker_id=worker_id,
                        message_en=f"Worker on {leave.leave_type.value} leave",
                        message_ar=f"العامل في إجازة {leave.leave_type.value}",
                        details={"leave_type": leave.leave_type.value},
                    )
                )

        # Get scheduled hours for the day
        scheduled_hours = 0.0
        assigned_tasks = []
        shift_id = None
        shift_start = None
        shift_end = None

        for schedule in self.schedules:
            if schedule.worker_id == worker_id and schedule.start_date <= check_date <= schedule.end_date:
                shift_id = schedule.shift_id
                shift = self._shifts_by_id.get(shift_id)
                if shift:
                    scheduled_hours = shift.get_duration_hours()
                    shift_start = schedule.custom_start_time or shift.start_time
                    shift_end = schedule.custom_end_time or shift.end_time
                assigned_tasks.extend(schedule.task_ids)

        # Calculate remaining hours
        task_hours = sum(self._tasks_by_id[tid].estimated_hours for tid in assigned_tasks if tid in self._tasks_by_id)
        remaining_hours = max(0, scheduled_hours - task_hours)

        is_available = len(conflicts) == 0 and (
            scheduled_hours > 0 or worker.worker_type.value in ["daily", "seasonal"]
        )

        return WorkerAvailability(
            worker_id=worker_id,
            worker_name=worker.full_name,
            worker_name_ar=worker.full_name_ar,
            is_available=is_available,
            availability_date=check_date,
            shift_id=shift_id,
            shift_start=shift_start,
            shift_end=shift_end,
            scheduled_hours=scheduled_hours,
            remaining_hours=remaining_hours,
            conflicts=conflicts,
            assigned_task_ids=assigned_tasks,
        )

    def get_available_workers(
        self,
        check_date: date,
        farm_id: str | None = None,
        required_skills: list[tuple[SkillCategory, SkillLevel]] | None = None,
        required_certifications: list[SafetyCertification] | None = None,
    ) -> list[WorkerAvailability]:
        """
        Get all available workers for a date - الحصول على جميع العمال المتاحين

        Args:
            check_date: Date to check
            farm_id: Optional farm filter
            required_skills: Optional skill requirements
            required_certifications: Optional certification requirements

        Returns:
            List of WorkerAvailability for available workers
        """
        available = []

        for worker in self.workers:
            # Farm filter
            if farm_id and worker.farm_id != farm_id:
                continue

            availability = self.check_worker_availability(worker.worker_id, check_date)

            # Skill filter
            if required_skills:
                for skill_cat, min_level in required_skills:
                    if not worker.has_skill(skill_cat, min_level):
                        availability.is_available = False
                        availability.conflicts.append(
                            SchedulingConflict(
                                conflict_type=SchedulingConflictType.SKILL_MISMATCH,
                                worker_id=worker.worker_id,
                                message_en=f"Missing required skill: {skill_cat.value}",
                                message_ar=f"مهارة مطلوبة مفقودة: {skill_cat.value}",
                            )
                        )

            # Certification filter
            if required_certifications:
                for cert_type in required_certifications:
                    if not worker.has_valid_certification(cert_type, check_date):
                        availability.is_available = False
                        availability.conflicts.append(
                            SchedulingConflict(
                                conflict_type=SchedulingConflictType.CERTIFICATION_MISSING,
                                worker_id=worker.worker_id,
                                message_en=f"Missing certification: {cert_type.value}",
                                message_ar=f"شهادة مفقودة: {cert_type.value}",
                            )
                        )

            if availability.is_available:
                available.append(availability)

        return available

    # ==================== REI Zone Checking ====================

    def check_rei_restrictions(
        self,
        field_id: str,
        check_time: datetime | None = None,
    ) -> list[REIZone]:
        """
        Check REI restrictions for a field - تحقق من قيود فترة إعادة الدخول

        Returns list of active REI zones for the field
        """
        check = check_time or datetime.now(UTC)
        active_zones = []

        for zone in self.rei_zones:
            if zone.field_id == field_id and zone.is_currently_restricted(check):
                active_zones.append(zone)

        return active_zones

    def can_enter_field(
        self,
        worker_id: str,
        field_id: str,
        task_category: TaskCategory,
        check_time: datetime | None = None,
    ) -> tuple[bool, list[SchedulingConflict], list[PPEType]]:
        """
        Check if worker can enter a field considering REI zones

        Returns:
            Tuple of (can_enter, conflicts, required_ppe)
        """
        check = check_time or datetime.now(UTC)
        conflicts = []
        required_ppe: list[PPEType] = []

        worker = self._workers_by_id.get(worker_id)
        if not worker:
            return (
                False,
                [
                    SchedulingConflict(
                        conflict_type=SchedulingConflictType.WORKER_UNAVAILABLE,
                        message_en="Worker not found",
                        message_ar="العامل غير موجود",
                    )
                ],
                [],
            )

        active_zones = self.check_rei_restrictions(field_id, check)

        for zone in active_zones:
            # Check if early entry is allowed for this task
            if zone.early_entry_allowed and task_category.value in zone.early_entry_tasks_allowed:
                # Early entry allowed with PPE
                required_ppe.extend(zone.early_entry_ppe_required)
            else:
                # Entry not allowed
                remaining_hours = zone.get_remaining_hours(check)
                conflicts.append(
                    SchedulingConflict(
                        conflict_type=SchedulingConflictType.REI_RESTRICTION,
                        worker_id=worker_id,
                        message_en=f"REI restriction active for {zone.pesticide_name}. "
                        f"Entry allowed after {zone.rei_expiry_time.strftime('%Y-%m-%d %H:%M')} "
                        f"({remaining_hours:.1f}h remaining)",
                        message_ar=f"قيد فترة إعادة الدخول نشط لـ {zone.pesticide_name_ar}. "
                        f"يُسمح بالدخول بعد {zone.rei_expiry_time.strftime('%Y-%m-%d %H:%M')} "
                        f"(متبقي {remaining_hours:.1f} ساعة)",
                        details={
                            "zone_id": zone.zone_id,
                            "pesticide_id": zone.pesticide_id,
                            "rei_expiry": zone.rei_expiry_time.isoformat(),
                            "remaining_hours": remaining_hours,
                        },
                    )
                )

        can_enter = len(conflicts) == 0
        return can_enter, conflicts, list(set(required_ppe))

    # ==================== Worker Scoring ====================

    def score_worker_for_task(
        self,
        worker: Worker,
        task: Task,
        check_date: date,
        strategy: SchedulingStrategy = SchedulingStrategy.SKILL_PRIORITY,
    ) -> WorkerScore:
        """
        Score a worker for a task based on various criteria

        Higher score = better match
        """
        score = WorkerScore(
            worker_id=worker.worker_id,
            task_id=task.task_id,
        )

        # Check basic eligibility
        availability = self.check_worker_availability(worker.worker_id, check_date)
        if not availability.is_available:
            score.is_eligible = False
            score.ineligibility_reasons.extend([c.message_en for c in availability.conflicts])
            return score

        # Check REI restrictions if task has a field
        if task.field_id:
            can_enter, rei_conflicts, _ = self.can_enter_field(worker.worker_id, task.field_id, task.category)
            if not can_enter:
                score.is_eligible = False
                score.ineligibility_reasons.extend([c.message_en for c in rei_conflicts])
                return score

        # Check requirements
        if task.requirements:
            # Skill requirements
            for skill_cat, min_level in task.requirements.required_skills:
                if not worker.has_skill(skill_cat, min_level):
                    score.is_eligible = False
                    score.ineligibility_reasons.append(f"Missing skill: {skill_cat.value} at {min_level.value} level")

            # Certification requirements
            for cert_type in task.requirements.required_certifications:
                if not worker.has_valid_certification(cert_type, check_date):
                    score.is_eligible = False
                    score.ineligibility_reasons.append(f"Missing certification: {cert_type.value}")

        if not score.is_eligible:
            return score

        # Calculate scores based on strategy weights
        weights = self._get_strategy_weights(strategy)

        # Skill score (0-100)
        score.skill_score = self._calculate_skill_score(worker, task)

        # Availability score (0-100)
        score.availability_score = self._calculate_availability_score(availability, task.estimated_hours)

        # Certification score (0-100)
        score.certification_score = self._calculate_certification_score(worker, task)

        # Workload score (0-100) - higher if worker has less workload
        score.workload_score = self._calculate_workload_score(availability)

        # Cost score (0-100) - higher if worker is cheaper
        score.cost_score = self._calculate_cost_score(worker, task)

        # Calculate weighted total
        score.total_score = (
            score.skill_score * weights["skill"]
            + score.availability_score * weights["availability"]
            + score.certification_score * weights["certification"]
            + score.workload_score * weights["workload"]
            + score.cost_score * weights["cost"]
        )

        return score

    def _get_strategy_weights(self, strategy: SchedulingStrategy) -> dict[str, float]:
        """Get scoring weights for scheduling strategy"""
        weights = {
            SchedulingStrategy.SKILL_PRIORITY: {
                "skill": 0.40,
                "availability": 0.20,
                "certification": 0.20,
                "workload": 0.10,
                "cost": 0.10,
            },
            SchedulingStrategy.WORKLOAD_BALANCE: {
                "skill": 0.15,
                "availability": 0.15,
                "certification": 0.15,
                "workload": 0.45,
                "cost": 0.10,
            },
            SchedulingStrategy.AVAILABILITY_FIRST: {
                "skill": 0.15,
                "availability": 0.45,
                "certification": 0.15,
                "workload": 0.15,
                "cost": 0.10,
            },
            SchedulingStrategy.COST_OPTIMIZED: {
                "skill": 0.15,
                "availability": 0.15,
                "certification": 0.15,
                "workload": 0.10,
                "cost": 0.45,
            },
            SchedulingStrategy.SAFETY_PRIORITY: {
                "skill": 0.20,
                "availability": 0.15,
                "certification": 0.45,
                "workload": 0.10,
                "cost": 0.10,
            },
        }
        return weights.get(strategy, weights[SchedulingStrategy.SKILL_PRIORITY])

    def _calculate_skill_score(self, worker: Worker, task: Task) -> float:
        """Calculate skill match score"""
        if not task.requirements or not task.requirements.required_skills:
            return 50.0  # Neutral score if no requirements

        skill_order = [
            SkillLevel.NONE,
            SkillLevel.BEGINNER,
            SkillLevel.INTERMEDIATE,
            SkillLevel.ADVANCED,
            SkillLevel.EXPERT,
        ]

        total_score = 0.0
        for skill_cat, min_level in task.requirements.required_skills:
            min_index = skill_order.index(min_level)
            worker_level = SkillLevel.NONE

            for skill in worker.skills:
                if skill.category == skill_cat:
                    worker_level = skill.level
                    break

            worker_index = skill_order.index(worker_level)

            # Score based on how much worker exceeds minimum
            if worker_index >= min_index:
                # 60 base + up to 40 bonus for exceeding
                total_score += 60 + min(40, (worker_index - min_index) * 10)
            else:
                # Below minimum
                total_score += max(0, 30 - (min_index - worker_index) * 10)

        return total_score / len(task.requirements.required_skills)

    def _calculate_availability_score(self, availability: WorkerAvailability, task_hours: float) -> float:
        """Calculate availability score"""
        if not availability.is_available:
            return 0.0

        # Score based on remaining hours vs task needs
        if availability.remaining_hours >= task_hours:
            return 100.0
        elif availability.remaining_hours > 0:
            return (availability.remaining_hours / task_hours) * 80
        return 0.0

    def _calculate_certification_score(self, worker: Worker, task: Task) -> float:
        """Calculate certification score"""
        if not task.requirements or not task.requirements.required_certifications:
            return 50.0  # Neutral if no requirements

        valid_certs = sum(
            1 for cert_type in task.requirements.required_certifications if worker.has_valid_certification(cert_type)
        )

        total = len(task.requirements.required_certifications)
        base_score = (valid_certs / total) * 80

        # Bonus for certifications not expiring soon
        bonus = 0
        for cert in worker.certifications:
            days_remaining = cert.days_until_expiry()
            if days_remaining and days_remaining > 90:
                bonus += 5
        bonus = min(20, bonus)

        return base_score + bonus

    def _calculate_workload_score(self, availability: WorkerAvailability) -> float:
        """Calculate workload balance score - higher if worker has lower workload"""
        if availability.scheduled_hours == 0:
            return 50.0  # Neutral for unscheduled workers

        utilization = 1 - (availability.remaining_hours / availability.scheduled_hours)
        # Higher score for lower utilization (more available capacity)
        return (1 - utilization) * 100

    def _calculate_cost_score(self, worker: Worker, task: Task) -> float:
        """Calculate cost efficiency score - higher for lower cost workers"""
        # Get effective hourly rate
        if worker.hourly_rate:
            rate = worker.hourly_rate
        elif worker.daily_rate:
            rate = worker.daily_rate / 8
        elif worker.monthly_salary:
            rate = worker.monthly_salary / 22 / 8
        else:
            return 50.0  # Neutral if no rate info

        # Normalize to 0-100 (assuming 50 SAR/hour is baseline)
        baseline = 50.0
        if rate <= baseline:
            return 100 - (rate / baseline) * 50
        else:
            return max(0, 50 - ((rate - baseline) / baseline) * 50)

    # ==================== Task Assignment ====================

    def assign_task(
        self,
        task_id: str,
        check_date: date | None = None,
        strategy: SchedulingStrategy = SchedulingStrategy.SKILL_PRIORITY,
        preferred_workers: list[str] | None = None,
        exclude_workers: list[str] | None = None,
    ) -> TaskAssignment:
        """
        Assign workers to a task - تعيين العمال للمهمة

        Args:
            task_id: Task to assign
            check_date: Date for availability check
            strategy: Scheduling strategy to use
            preferred_workers: Optional list of preferred worker IDs
            exclude_workers: Optional list of workers to exclude

        Returns:
            TaskAssignment with assigned workers and any conflicts
        """
        task = self._tasks_by_id.get(task_id)
        if not task:
            return TaskAssignment(
                task_id=task_id,
                worker_ids=[],
                is_successful=False,
                conflicts=[
                    SchedulingConflict(
                        conflict_type=SchedulingConflictType.WORKER_UNAVAILABLE,
                        task_id=task_id,
                        message_en="Task not found",
                        message_ar="المهمة غير موجودة",
                    )
                ],
            )

        check_date = check_date or date.today()
        exclude_workers = exclude_workers or []

        # Get requirements
        min_workers = 1
        max_workers = 10
        if task.requirements:
            min_workers = task.requirements.min_workers
            max_workers = task.requirements.max_workers

        # Score all eligible workers
        worker_scores: list[WorkerScore] = []
        for worker in self.workers:
            if worker.worker_id in exclude_workers:
                continue
            if worker.farm_id != task.farm_id:
                continue

            score = self.score_worker_for_task(worker, task, check_date, strategy)
            if score.is_eligible:
                worker_scores.append(score)

        # Sort by score (highest first)
        worker_scores.sort(key=lambda s: s.total_score, reverse=True)

        # Prioritize preferred workers if specified
        if preferred_workers:
            preferred_scores = [s for s in worker_scores if s.worker_id in preferred_workers]
            other_scores = [s for s in worker_scores if s.worker_id not in preferred_workers]
            worker_scores = preferred_scores + other_scores

        # Select workers
        selected_workers = []
        conflicts = []
        warnings_en = []
        warnings_ar = []

        for score in worker_scores[:max_workers]:
            selected_workers.append(score.worker_id)

        # Check if we have enough workers
        if len(selected_workers) < min_workers:
            conflicts.append(
                SchedulingConflict(
                    conflict_type=SchedulingConflictType.WORKER_UNAVAILABLE,
                    task_id=task_id,
                    message_en=f"Only {len(selected_workers)} of {min_workers} required workers available",
                    message_ar=f"فقط {len(selected_workers)} من {min_workers} عمال مطلوبين متاحين",
                )
            )

        # Check REI restrictions
        if task.field_id:
            active_rei_zones = self.check_rei_restrictions(task.field_id)
            for zone in active_rei_zones:
                if zone.early_entry_allowed and task.category.value in zone.early_entry_tasks_allowed:
                    warnings_en.append(
                        f"Field has active REI zone ({zone.pesticide_name}). "
                        f"Early entry allowed with PPE: {', '.join(p.value for p in zone.early_entry_ppe_required)}"
                    )
                    warnings_ar.append(
                        f"الحقل به منطقة REI نشطة ({zone.pesticide_name_ar}). "
                        f"يُسمح بالدخول المبكر مع: {', '.join(p.value for p in zone.early_entry_ppe_required)}"
                    )
                else:
                    conflicts.append(
                        SchedulingConflict(
                            conflict_type=SchedulingConflictType.REI_RESTRICTION,
                            task_id=task_id,
                            message_en=f"Field blocked by REI ({zone.pesticide_name}). "
                            f"Access allowed after {zone.rei_expiry_time.strftime('%Y-%m-%d %H:%M')}",
                            message_ar=f"الحقل محظور بسبب REI ({zone.pesticide_name_ar}). "
                            f"يُسمح بالوصول بعد {zone.rei_expiry_time.strftime('%Y-%m-%d %H:%M')}",
                        )
                    )

        is_successful = len(selected_workers) >= min_workers and not any(
            c.conflict_type == SchedulingConflictType.REI_RESTRICTION for c in conflicts
        )
        partial = 0 < len(selected_workers) < min_workers

        return TaskAssignment(
            task_id=task_id,
            worker_ids=selected_workers,
            scheduled_start=task.planned_start,
            scheduled_end=task.planned_end,
            is_successful=is_successful,
            partial_assignment=partial,
            conflicts=conflicts,
            warnings_en=warnings_en,
            warnings_ar=warnings_ar,
        )

    def bulk_schedule(
        self,
        task_ids: list[str] | None = None,
        check_date: date | None = None,
        strategy: SchedulingStrategy = SchedulingStrategy.SKILL_PRIORITY,
        prioritize_critical: bool = True,
    ) -> SchedulingResult:
        """
        Schedule multiple tasks - جدولة مهام متعددة

        Args:
            task_ids: Optional list of task IDs (default: all pending tasks)
            check_date: Date for scheduling
            strategy: Scheduling strategy
            prioritize_critical: Whether to schedule critical tasks first

        Returns:
            SchedulingResult with all assignments
        """
        check_date = check_date or date.today()

        # Get tasks to schedule
        if task_ids:
            tasks_to_schedule = [self._tasks_by_id[tid] for tid in task_ids if tid in self._tasks_by_id]
        else:
            tasks_to_schedule = [t for t in self.tasks if t.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED]]

        # Sort by priority if requested
        if prioritize_critical:
            priority_order = {
                TaskPriority.CRITICAL: 0,
                TaskPriority.HIGH: 1,
                TaskPriority.MEDIUM: 2,
                TaskPriority.LOW: 3,
            }
            tasks_to_schedule.sort(key=lambda t: priority_order.get(t.priority, 2))

        # Track assigned workers to avoid double-booking
        assigned_worker_tasks: dict[str, list[str]] = {}  # worker_id -> task_ids

        assignments = []
        all_conflicts = []

        for task in tasks_to_schedule:
            # Get already assigned workers
            exclude = [
                wid
                for wid, tids in assigned_worker_tasks.items()
                if len(tids) >= 3  # Max 3 tasks per worker per day
            ]

            assignment = self.assign_task(
                task.task_id,
                check_date=check_date,
                strategy=strategy,
                exclude_workers=exclude,
            )

            assignments.append(assignment)
            all_conflicts.extend(assignment.conflicts)

            # Track assignments
            for worker_id in assignment.worker_ids:
                if worker_id not in assigned_worker_tasks:
                    assigned_worker_tasks[worker_id] = []
                assigned_worker_tasks[worker_id].append(task.task_id)

        # Calculate summary
        total_tasks = len(tasks_to_schedule)
        tasks_assigned = sum(1 for a in assignments if a.is_successful)
        tasks_partial = sum(1 for a in assignments if a.partial_assignment)
        tasks_unassigned = total_tasks - tasks_assigned - tasks_partial

        workers_assigned = len(assigned_worker_tasks)
        total_hours = sum(
            self._tasks_by_id[a.task_id].estimated_hours * len(a.worker_ids)
            for a in assignments
            if a.is_successful and a.task_id in self._tasks_by_id
        )

        # Generate summary messages
        summary_en = (
            f"Scheduled {tasks_assigned} of {total_tasks} tasks. "
            f"{workers_assigned} workers assigned for {total_hours:.1f} total hours."
        )
        summary_ar = (
            f"تمت جدولة {tasks_assigned} من {total_tasks} مهمة. "
            f"تم تعيين {workers_assigned} عمال لـ {total_hours:.1f} ساعة إجمالية."
        )

        if tasks_partial > 0:
            summary_en += f" {tasks_partial} tasks partially assigned."
            summary_ar += f" {tasks_partial} مهمة معينة جزئياً."

        if tasks_unassigned > 0:
            summary_en += f" {tasks_unassigned} tasks could not be assigned."
            summary_ar += f" {tasks_unassigned} مهمة لم يتم تعيينها."

        return SchedulingResult(
            assignments=assignments,
            total_tasks=total_tasks,
            tasks_assigned=tasks_assigned,
            tasks_partially_assigned=tasks_partial,
            tasks_unassigned=tasks_unassigned,
            workers_assigned=workers_assigned,
            total_worker_hours=total_hours,
            conflicts=all_conflicts,
            summary_en=summary_en,
            summary_ar=summary_ar,
        )

    # ==================== Optimization ====================

    def optimize_schedule(
        self,
        schedule_date: date,
        farm_id: str,
        max_iterations: int = 100,
    ) -> SchedulingResult:
        """
        Optimize worker schedules for a given date - تحسين جداول العمال

        Uses iterative improvement to balance workload and minimize conflicts.
        """
        # Initial schedule with balanced strategy
        result = self.bulk_schedule(
            check_date=schedule_date,
            strategy=SchedulingStrategy.WORKLOAD_BALANCE,
        )

        # Iterative improvement
        for _ in range(max_iterations):
            improved = False

            for assignment in result.assignments:
                if not assignment.is_successful:
                    # Try alternative strategies
                    for strategy in [
                        SchedulingStrategy.SKILL_PRIORITY,
                        SchedulingStrategy.AVAILABILITY_FIRST,
                    ]:
                        new_assignment = self.assign_task(
                            assignment.task_id,
                            check_date=schedule_date,
                            strategy=strategy,
                        )
                        if new_assignment.is_successful and not assignment.is_successful:
                            assignment.worker_ids = new_assignment.worker_ids
                            assignment.is_successful = True
                            assignment.conflicts = new_assignment.conflicts
                            improved = True
                            break

            if not improved:
                break

        # Recalculate summary
        result.tasks_assigned = sum(1 for a in result.assignments if a.is_successful)
        result.tasks_unassigned = result.total_tasks - result.tasks_assigned

        return result

    def get_scheduling_recommendations(
        self,
        task_id: str,
        check_date: date | None = None,
    ) -> dict:
        """
        Get scheduling recommendations for a task - الحصول على توصيات الجدولة

        Returns recommendations for worker assignment and timing.
        """
        check_date = check_date or date.today()
        task = self._tasks_by_id.get(task_id)

        if not task:
            return {
                "success": False,
                "message_en": "Task not found",
                "message_ar": "المهمة غير موجودة",
            }

        recommendations = {
            "task_id": task_id,
            "task_title": task.title,
            "task_title_ar": task.title_ar,
            "recommended_workers": [],
            "alternative_dates": [],
            "rei_status": None,
            "recommendations_en": [],
            "recommendations_ar": [],
        }

        # Get top scored workers
        worker_scores = []
        for worker in self.workers:
            if worker.farm_id == task.farm_id:
                score = self.score_worker_for_task(worker, task, check_date, SchedulingStrategy.SKILL_PRIORITY)
                if score.is_eligible:
                    worker_scores.append(
                        {
                            "worker_id": worker.worker_id,
                            "worker_name": worker.full_name,
                            "worker_name_ar": worker.full_name_ar,
                            "score": score.total_score,
                            "skill_score": score.skill_score,
                            "availability_score": score.availability_score,
                        }
                    )

        worker_scores.sort(key=lambda x: x["score"], reverse=True)
        recommendations["recommended_workers"] = worker_scores[:5]

        # Check REI status
        if task.field_id:
            rei_zones = self.check_rei_restrictions(task.field_id)
            if rei_zones:
                earliest_entry = max(z.rei_expiry_time for z in rei_zones)
                recommendations["rei_status"] = {
                    "is_restricted": True,
                    "earliest_entry": earliest_entry.isoformat(),
                    "pesticides": [{"name": z.pesticide_name, "name_ar": z.pesticide_name_ar} for z in rei_zones],
                }
                recommendations["recommendations_en"].append(
                    f"Field is restricted until {earliest_entry.strftime('%Y-%m-%d %H:%M')} "
                    f"due to pesticide application(s)"
                )
                recommendations["recommendations_ar"].append(
                    f"الحقل مقيد حتى {earliest_entry.strftime('%Y-%m-%d %H:%M')} بسبب تطبيق المبيد(ات)"
                )
            else:
                recommendations["rei_status"] = {"is_restricted": False}

        # General recommendations
        if len(worker_scores) == 0:
            recommendations["recommendations_en"].append(
                "No eligible workers found. Consider adjusting skill or certification requirements."
            )
            recommendations["recommendations_ar"].append(
                "لم يتم العثور على عمال مؤهلين. فكر في تعديل متطلبات المهارات أو الشهادات."
            )
        elif len(worker_scores) < (task.requirements.min_workers if task.requirements else 1):
            recommendations["recommendations_en"].append(
                f"Only {len(worker_scores)} eligible workers available, "
                f"but {task.requirements.min_workers if task.requirements else 1} required."
            )
            recommendations["recommendations_ar"].append(
                f"فقط {len(worker_scores)} عمال مؤهلين متاحين، "
                f"لكن {task.requirements.min_workers if task.requirements else 1} مطلوبين."
            )

        return recommendations
