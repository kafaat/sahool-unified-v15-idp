"""
Tests for labor_management models
اختبارات نماذج إدارة العمالة
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta

import pytest

from shared.labor_management.models import (
    AttendanceRecord,
    AttendanceStatus,
    BilingualText,
    LeaveRequest,
    LeaveType,
    PPEType,
    PreTaskSafetyCheck,
    REIZone,
    SafetyCertification,
    SafetyChecklistItem,
    SafetyViolationType,
    SkillCategory,
    SkillLevel,
    Task,
    TaskCategory,
    TaskPriority,
    TaskRequirement,
    TaskStatus,
    Worker,
    WorkerCertification,
    WorkerSkill,
    WorkerStatus,
    WorkerType,
    WorkShift,
    create_rei_zone,
    create_task,
    create_worker,
    generate_id,
)


class TestEnums:
    def test_worker_status_values(self):
        assert WorkerStatus.ACTIVE == "active"
        assert WorkerStatus.SUSPENDED == "suspended"

    def test_worker_type_values(self):
        assert WorkerType.FULL_TIME == "full_time"
        assert WorkerType.SEASONAL == "seasonal"

    def test_task_status_values(self):
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.BLOCKED == "blocked"

    def test_task_priority_values(self):
        assert TaskPriority.CRITICAL == "critical"
        assert TaskPriority.LOW == "low"

    def test_task_category_values(self):
        assert TaskCategory.PLANTING == "planting"
        assert TaskCategory.PESTICIDE_APPLICATION == "pesticide_application"

    def test_skill_level_values(self):
        assert SkillLevel.NONE == "none"
        assert SkillLevel.EXPERT == "expert"

    def test_safety_certification_values(self):
        assert SafetyCertification.PESTICIDE_APPLICATOR == "pesticide_applicator"
        assert SafetyCertification.FIRST_AID == "first_aid"

    def test_ppe_type_values(self):
        assert PPEType.GLOVES == "gloves"
        assert PPEType.RESPIRATOR == "respirator"


class TestBilingualText:
    def test_get_english(self):
        text = BilingualText(en="Hello", ar="مرحبا")
        assert text.get("en") == "Hello"

    def test_get_arabic(self):
        text = BilingualText(en="Hello", ar="مرحبا")
        assert text.get("ar") == "مرحبا"

    def test_get_default(self):
        text = BilingualText(en="Hello", ar="مرحبا")
        assert text.get() == "Hello"


class TestWorkerSkill:
    def _make_skill(self, **kwargs):
        defaults = dict(
            skill_id="SKL001",
            skill_name="Tractor Operation",
            skill_name_ar="تشغيل الجرار",
            category=SkillCategory.EQUIPMENT_OPERATION,
            level=SkillLevel.ADVANCED,
        )
        defaults.update(kwargs)
        return WorkerSkill(**defaults)

    def test_is_certification_valid_no_cert(self):
        skill = self._make_skill(is_certified=False)
        assert skill.is_certification_valid() is False

    def test_is_certification_valid_no_expiry(self):
        skill = self._make_skill(is_certified=True, certification_expiry=None)
        assert skill.is_certification_valid() is False

    def test_is_certification_valid_future(self):
        skill = self._make_skill(
            is_certified=True,
            certification_expiry=date.today() + timedelta(days=30),
        )
        assert skill.is_certification_valid() is True

    def test_is_certification_valid_past(self):
        skill = self._make_skill(
            is_certified=True,
            certification_expiry=date.today() - timedelta(days=1),
        )
        assert skill.is_certification_valid() is False

    def test_days_until_expiry_none(self):
        skill = self._make_skill()
        assert skill.days_until_expiry() is None

    def test_days_until_expiry_value(self):
        skill = self._make_skill(
            certification_expiry=date.today() + timedelta(days=15),
        )
        assert skill.days_until_expiry() == 15


class TestWorkerCertification:
    def _make_cert(self, expiry_days=30, is_verified=True):
        return WorkerCertification(
            certification_id="CERT001",
            certification_type=SafetyCertification.PESTICIDE_APPLICATOR,
            name="Pesticide Applicator",
            name_ar="رخصة تطبيق المبيدات",
            issue_date=date.today() - timedelta(days=365),
            expiry_date=date.today() + timedelta(days=expiry_days),
            issuing_authority="MOA",
            issuing_authority_ar="وزارة الزراعة",
            certificate_number="PA-001",
            is_verified=is_verified,
        )

    def test_is_valid_active(self):
        cert = self._make_cert(expiry_days=30)
        assert cert.is_valid() is True

    def test_is_valid_expired(self):
        cert = self._make_cert(expiry_days=-1)
        assert cert.is_valid() is False

    def test_is_valid_unverified(self):
        cert = self._make_cert(is_verified=False)
        assert cert.is_valid() is False

    def test_days_until_expiry(self):
        cert = self._make_cert(expiry_days=45)
        assert cert.days_until_expiry() == 45


class TestWorker:
    def _make_worker(self, **kwargs):
        defaults = dict(
            worker_id="WRK001",
            tenant_id="t1",
            farm_id="f1",
            first_name="Ali",
            last_name="Ahmed",
            first_name_ar="علي",
            last_name_ar="أحمد",
            phone="0501234567",
        )
        defaults.update(kwargs)
        return Worker(**defaults)

    def test_full_name(self):
        worker = self._make_worker()
        assert worker.full_name == "Ali Ahmed"

    def test_full_name_ar(self):
        worker = self._make_worker()
        assert worker.full_name_ar == "علي أحمد"

    def test_has_skill_true(self):
        skill = WorkerSkill(
            skill_id="s1", skill_name="Tractor", skill_name_ar="جرار",
            category=SkillCategory.EQUIPMENT_OPERATION, level=SkillLevel.ADVANCED,
        )
        worker = self._make_worker(skills=[skill])
        assert worker.has_skill(SkillCategory.EQUIPMENT_OPERATION, SkillLevel.BEGINNER) is True

    def test_has_skill_exact_level(self):
        skill = WorkerSkill(
            skill_id="s1", skill_name="Tractor", skill_name_ar="جرار",
            category=SkillCategory.EQUIPMENT_OPERATION, level=SkillLevel.INTERMEDIATE,
        )
        worker = self._make_worker(skills=[skill])
        assert worker.has_skill(SkillCategory.EQUIPMENT_OPERATION, SkillLevel.INTERMEDIATE) is True

    def test_has_skill_insufficient_level(self):
        skill = WorkerSkill(
            skill_id="s1", skill_name="Tractor", skill_name_ar="جرار",
            category=SkillCategory.EQUIPMENT_OPERATION, level=SkillLevel.BEGINNER,
        )
        worker = self._make_worker(skills=[skill])
        assert worker.has_skill(SkillCategory.EQUIPMENT_OPERATION, SkillLevel.ADVANCED) is False

    def test_has_skill_wrong_category(self):
        skill = WorkerSkill(
            skill_id="s1", skill_name="Irrigation", skill_name_ar="ري",
            category=SkillCategory.IRRIGATION_SYSTEMS, level=SkillLevel.EXPERT,
        )
        worker = self._make_worker(skills=[skill])
        assert worker.has_skill(SkillCategory.EQUIPMENT_OPERATION) is False

    def test_has_valid_certification_true(self):
        cert = WorkerCertification(
            certification_id="c1",
            certification_type=SafetyCertification.PESTICIDE_APPLICATOR,
            name="PA", name_ar="مبيد",
            issue_date=date.today(), expiry_date=date.today() + timedelta(days=30),
            issuing_authority="MOA", issuing_authority_ar="وزارة",
            certificate_number="PA-001",
        )
        worker = self._make_worker(certifications=[cert])
        assert worker.has_valid_certification(SafetyCertification.PESTICIDE_APPLICATOR) is True

    def test_has_valid_certification_expired(self):
        cert = WorkerCertification(
            certification_id="c1",
            certification_type=SafetyCertification.PESTICIDE_APPLICATOR,
            name="PA", name_ar="مبيد",
            issue_date=date.today() - timedelta(days=365),
            expiry_date=date.today() - timedelta(days=1),
            issuing_authority="MOA", issuing_authority_ar="وزارة",
            certificate_number="PA-001",
        )
        worker = self._make_worker(certifications=[cert])
        assert worker.has_valid_certification(SafetyCertification.PESTICIDE_APPLICATOR) is False

    def test_has_valid_certification_wrong_type(self):
        cert = WorkerCertification(
            certification_id="c1",
            certification_type=SafetyCertification.FIRST_AID,
            name="FA", name_ar="إسعاف",
            issue_date=date.today(), expiry_date=date.today() + timedelta(days=30),
            issuing_authority="MOA", issuing_authority_ar="وزارة",
            certificate_number="FA-001",
        )
        worker = self._make_worker(certifications=[cert])
        assert worker.has_valid_certification(SafetyCertification.PESTICIDE_APPLICATOR) is False

    def test_get_expiring_certifications(self):
        cert_expiring = WorkerCertification(
            certification_id="c1",
            certification_type=SafetyCertification.PESTICIDE_APPLICATOR,
            name="PA", name_ar="مبيد",
            issue_date=date.today(), expiry_date=date.today() + timedelta(days=15),
            issuing_authority="MOA", issuing_authority_ar="وزارة",
            certificate_number="PA-001",
        )
        cert_not_expiring = WorkerCertification(
            certification_id="c2",
            certification_type=SafetyCertification.FIRST_AID,
            name="FA", name_ar="إسعاف",
            issue_date=date.today(), expiry_date=date.today() + timedelta(days=365),
            issuing_authority="MOA", issuing_authority_ar="وزارة",
            certificate_number="FA-001",
        )
        worker = self._make_worker(certifications=[cert_expiring, cert_not_expiring])
        expiring = worker.get_expiring_certifications(days_ahead=30)
        assert len(expiring) == 1
        assert expiring[0].certification_id == "c1"


class TestTask:
    def _make_task(self, rei_restricted=False, rei_expiry=None):
        return Task(
            task_id="TSK001",
            tenant_id="t1",
            farm_id="f1",
            rei_restricted=rei_restricted,
            rei_expiry_time=rei_expiry,
        )

    def test_is_blocked_by_rei_not_restricted(self):
        task = self._make_task(rei_restricted=False)
        assert task.is_blocked_by_rei() is False

    def test_is_blocked_by_rei_active(self):
        future = datetime.now(UTC) + timedelta(hours=4)
        task = self._make_task(rei_restricted=True, rei_expiry=future)
        assert task.is_blocked_by_rei() is True

    def test_is_blocked_by_rei_expired(self):
        past = datetime.now(UTC) - timedelta(hours=1)
        task = self._make_task(rei_restricted=True, rei_expiry=past)
        assert task.is_blocked_by_rei() is False

    def test_get_rei_remaining_hours_none(self):
        task = self._make_task()
        assert task.get_rei_remaining_hours() is None

    def test_get_rei_remaining_hours_active(self):
        future = datetime.now(UTC) + timedelta(hours=3)
        task = self._make_task(rei_restricted=True, rei_expiry=future)
        remaining = task.get_rei_remaining_hours()
        assert remaining is not None
        assert 2.9 < remaining < 3.1

    def test_get_rei_remaining_hours_expired(self):
        past = datetime.now(UTC) - timedelta(hours=1)
        task = self._make_task(rei_restricted=True, rei_expiry=past)
        assert task.get_rei_remaining_hours() == 0.0


class TestWorkShift:
    def test_get_duration_hours_normal(self):
        shift = WorkShift(
            shift_id="S1", name="Morning", name_ar="صباحي",
            start_time=time(6, 0), end_time=time(14, 0),
            break_duration_minutes=60,
        )
        assert shift.get_duration_hours() == 7.0

    def test_get_duration_hours_overnight(self):
        shift = WorkShift(
            shift_id="S2", name="Night", name_ar="ليلي",
            start_time=time(22, 0), end_time=time(6, 0),
            break_duration_minutes=30,
        )
        assert shift.get_duration_hours() == 7.5

    def test_get_duration_hours_no_break(self):
        shift = WorkShift(
            shift_id="S3", name="Short", name_ar="قصيرة",
            start_time=time(8, 0), end_time=time(12, 0),
            break_duration_minutes=0,
        )
        assert shift.get_duration_hours() == 4.0


class TestREIZone:
    def _make_zone(self, hours_remaining=4):
        now = datetime.now(UTC)
        return REIZone(
            zone_id="REI001",
            tenant_id="t1",
            farm_id="f1",
            field_id="field1",
            pesticide_application_id="PA001",
            pesticide_id="P001",
            pesticide_name="TestPesticide",
            pesticide_name_ar="مبيد اختبار",
            application_time=now - timedelta(hours=1),
            rei_hours=hours_remaining + 1,
            rei_expiry_time=now + timedelta(hours=hours_remaining),
        )

    def test_is_currently_restricted_active(self):
        zone = self._make_zone(hours_remaining=4)
        assert zone.is_currently_restricted() is True

    def test_is_currently_restricted_expired(self):
        zone = self._make_zone(hours_remaining=-1)
        assert zone.is_currently_restricted() is False

    def test_is_currently_restricted_inactive(self):
        zone = self._make_zone(hours_remaining=4)
        zone.is_active = False
        assert zone.is_currently_restricted() is False

    def test_get_remaining_hours(self):
        zone = self._make_zone(hours_remaining=3)
        remaining = zone.get_remaining_hours()
        assert 2.9 < remaining < 3.1

    def test_get_remaining_hours_expired(self):
        zone = self._make_zone(hours_remaining=-1)
        assert zone.get_remaining_hours() == 0.0


class TestPreTaskSafetyCheck:
    def test_is_complete_all_done(self):
        items = [
            SafetyChecklistItem(item_id="A", description="A", description_ar="أ", category="gen", is_mandatory=True),
            SafetyChecklistItem(item_id="B", description="B", description_ar="ب", category="gen", is_mandatory=True),
            SafetyChecklistItem(item_id="C", description="C", description_ar="ج", category="gen", is_mandatory=False),
        ]
        check = PreTaskSafetyCheck(
            check_id="CHK1", tenant_id="t1", farm_id="f1",
            task_id="TSK1", worker_id="WRK1",
            checklist_items=items,
            completed_items=["A", "B"],
        )
        assert check.is_complete() is True

    def test_is_complete_missing_mandatory(self):
        items = [
            SafetyChecklistItem(item_id="A", description="A", description_ar="أ", category="gen", is_mandatory=True),
            SafetyChecklistItem(item_id="B", description="B", description_ar="ب", category="gen", is_mandatory=True),
        ]
        check = PreTaskSafetyCheck(
            check_id="CHK1", tenant_id="t1", farm_id="f1",
            task_id="TSK1", worker_id="WRK1",
            checklist_items=items,
            completed_items=["A"],
        )
        assert check.is_complete() is False


class TestAttendanceRecord:
    def test_calculate_worked_hours(self):
        record = AttendanceRecord(
            attendance_id="ATT1", tenant_id="t1", farm_id="f1", worker_id="WRK1",
            date=date.today(),
            clock_in=datetime(2025, 1, 1, 6, 0, tzinfo=UTC),
            clock_out=datetime(2025, 1, 1, 14, 0, tzinfo=UTC),
            total_break_minutes=60,
        )
        assert record.calculate_worked_hours() == 7.0

    def test_calculate_worked_hours_no_clock(self):
        record = AttendanceRecord(
            attendance_id="ATT1", tenant_id="t1", farm_id="f1", worker_id="WRK1",
            date=date.today(),
        )
        assert record.calculate_worked_hours() is None


class TestLeaveRequest:
    def test_get_duration_days(self):
        req = LeaveRequest(
            leave_id="LV1", tenant_id="t1", farm_id="f1", worker_id="WRK1",
            leave_type=LeaveType.ANNUAL,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 5),
        )
        assert req.get_duration_days() == 5


class TestFactoryFunctions:
    def test_generate_id_with_prefix(self):
        id_ = generate_id("WRK")
        assert id_.startswith("WRK_")
        assert len(id_) == 16  # "WRK_" + 12 hex chars

    def test_generate_id_no_prefix(self):
        id_ = generate_id()
        assert "_" not in id_
        assert len(id_) == 12

    def test_create_worker(self):
        worker = create_worker(
            tenant_id="t1", farm_id="f1",
            first_name="Ali", last_name="Ahmed",
            first_name_ar="علي", last_name_ar="أحمد",
            phone="0501234567",
        )
        assert worker.worker_id.startswith("WRK_")
        assert worker.full_name == "Ali Ahmed"

    def test_create_task(self):
        task = create_task(
            tenant_id="t1", farm_id="f1",
            title="Plant wheat", title_ar="زراعة القمح",
            category=TaskCategory.PLANTING,
        )
        assert task.task_id.startswith("TSK_")
        assert task.category == TaskCategory.PLANTING

    def test_create_rei_zone(self):
        now = datetime.now(UTC)
        zone = create_rei_zone(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA001",
            pesticide_id="P001",
            pesticide_name="TestPesticide",
            pesticide_name_ar="مبيد اختبار",
            application_time=now,
            rei_hours=24,
        )
        assert zone.zone_id.startswith("REI_")
        assert zone.rei_expiry_time == now + timedelta(hours=24)
        assert "TestPesticide" in zone.warning_message_en
        assert "مبيد اختبار" in zone.warning_message_ar
