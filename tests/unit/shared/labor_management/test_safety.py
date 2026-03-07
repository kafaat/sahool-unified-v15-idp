"""
Tests for labor_management safety module
اختبارات وحدة سلامة إدارة العمالة
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta

import pytest

from shared.labor_management.models import (
    PPEType,
    SafetyCertification,
    Task,
    TaskCategory,
    TaskRequirement,
    Worker,
    WorkerCertification,
    WorkerStatus,
)
from shared.labor_management.safety import (
    GENERAL_SAFETY_CHECKLIST,
    PESTICIDE_SAFETY_CHECKLIST,
    REI_ENTRY_CHECKLIST,
    TASK_PPE_REQUIREMENTS,
    HeatRiskLevel,
    SafetyCheckStatus,
    SafetyComplianceManager,
    SafetyViolationType,
)


@pytest.fixture
def worker_ali():
    return Worker(
        worker_id="W1", tenant_id="t1", farm_id="f1",
        first_name="Ali", last_name="Ahmed",
        first_name_ar="علي", last_name_ar="أحمد",
        phone="050", status=WorkerStatus.ACTIVE,
        certifications=[
            WorkerCertification(
                certification_id="c1",
                certification_type=SafetyCertification.PESTICIDE_APPLICATOR,
                name="PA", name_ar="مبيد",
                issue_date=date.today() - timedelta(days=180),
                expiry_date=date.today() + timedelta(days=180),
                issuing_authority="MOA", issuing_authority_ar="وزارة",
                certificate_number="PA-001",
            ),
        ],
    )


@pytest.fixture
def worker_no_cert():
    return Worker(
        worker_id="W2", tenant_id="t1", farm_id="f1",
        first_name="Omar", last_name="Hassan",
        first_name_ar="عمر", last_name_ar="حسن",
        phone="051", status=WorkerStatus.ACTIVE,
    )


@pytest.fixture
def safety_manager(worker_ali, worker_no_cert):
    return SafetyComplianceManager(workers=[worker_ali, worker_no_cert])


class TestSafetyChecklists:
    def test_general_checklist_not_empty(self):
        assert len(GENERAL_SAFETY_CHECKLIST) >= 5

    def test_pesticide_checklist_not_empty(self):
        assert len(PESTICIDE_SAFETY_CHECKLIST) >= 5

    def test_rei_entry_checklist_not_empty(self):
        assert len(REI_ENTRY_CHECKLIST) >= 3

    def test_task_ppe_requirements_coverage(self):
        assert TaskCategory.PESTICIDE_APPLICATION in TASK_PPE_REQUIREMENTS
        assert TaskCategory.IRRIGATION in TASK_PPE_REQUIREMENTS
        assert PPEType.RESPIRATOR in TASK_PPE_REQUIREMENTS[TaskCategory.PESTICIDE_APPLICATION]


class TestREIZoneManagement:
    def test_create_rei_zone(self, safety_manager):
        now = datetime.now(UTC)
        zone = safety_manager.create_rei_zone_from_pesticide_application(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA1", pesticide_id="P1",
            pesticide_name="Herbicide", pesticide_name_ar="مبيد أعشاب",
            application_time=now, rei_hours=24,
        )
        assert zone.zone_id.startswith("REI_")
        assert zone.rei_expiry_time == now + timedelta(hours=24)
        assert len(safety_manager.rei_zones) == 1

    def test_get_active_rei_zones(self, safety_manager):
        now = datetime.now(UTC)
        safety_manager.create_rei_zone_from_pesticide_application(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA1", pesticide_id="P1",
            pesticide_name="Herb", pesticide_name_ar="مبيد",
            application_time=now, rei_hours=24,
        )
        active = safety_manager.get_active_rei_zones(field_id="field1")
        assert len(active) == 1

    def test_get_active_rei_zones_none(self, safety_manager):
        active = safety_manager.get_active_rei_zones(field_id="field1")
        assert len(active) == 0

    def test_check_rei_compliance_no_zones(self, safety_manager):
        result = safety_manager.check_rei_compliance("field1")
        assert result.is_compliant is True
        assert result.can_enter is True

    def test_check_rei_compliance_restricted(self, safety_manager):
        now = datetime.now(UTC)
        safety_manager.create_rei_zone_from_pesticide_application(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA1", pesticide_id="P1",
            pesticide_name="Herb", pesticide_name_ar="مبيد",
            application_time=now, rei_hours=24,
        )
        result = safety_manager.check_rei_compliance("field1")
        assert result.is_compliant is False
        assert result.can_enter is False
        assert result.earliest_safe_entry is not None

    def test_check_rei_compliance_early_entry(self, safety_manager):
        now = datetime.now(UTC)
        safety_manager.create_rei_zone_from_pesticide_application(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA1", pesticide_id="P1",
            pesticide_name="Herb", pesticide_name_ar="مبيد",
            application_time=now, rei_hours=24,
            early_entry_allowed=True,
            early_entry_tasks=["irrigation"],
            early_entry_ppe=[PPEType.GLOVES, PPEType.BOOTS],
        )
        result = safety_manager.check_rei_compliance(
            "field1", task_category=TaskCategory.IRRIGATION,
        )
        assert result.can_enter is True
        assert result.requires_ppe is True
        assert PPEType.GLOVES in result.early_entry_ppe

    def test_expire_rei_zones(self, safety_manager):
        past = datetime.now(UTC) - timedelta(hours=48)
        safety_manager.create_rei_zone_from_pesticide_application(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA1", pesticide_id="P1",
            pesticide_name="Herb", pesticide_name_ar="مبيد",
            application_time=past, rei_hours=24,
        )
        expired = safety_manager.expire_rei_zones()
        assert len(expired) == 1
        assert expired[0].is_active is False


class TestPPERequirements:
    def test_get_ppe_for_pesticide(self, safety_manager):
        ppe_set = safety_manager.get_ppe_requirements(TaskCategory.PESTICIDE_APPLICATION)
        assert PPEType.RESPIRATOR in ppe_set.required_ppe
        assert PPEType.GLOVES in ppe_set.required_ppe

    def test_get_ppe_for_irrigation(self, safety_manager):
        ppe_set = safety_manager.get_ppe_requirements(TaskCategory.IRRIGATION)
        assert PPEType.BOOTS in ppe_set.required_ppe

    def test_get_ppe_with_rei_zone(self, safety_manager):
        now = datetime.now(UTC)
        safety_manager.create_rei_zone_from_pesticide_application(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA1", pesticide_id="P1",
            pesticide_name="Herb", pesticide_name_ar="مبيد",
            application_time=now, rei_hours=24,
            early_entry_allowed=True,
            early_entry_tasks=["irrigation"],
            early_entry_ppe=[PPEType.COVERALL],
        )
        ppe_set = safety_manager.get_ppe_requirements(
            TaskCategory.IRRIGATION, field_id="field1",
        )
        assert PPEType.COVERALL in ppe_set.required_ppe

    def test_verify_worker_ppe_passed(self, safety_manager):
        result = safety_manager.verify_worker_ppe(
            "W1",
            required_ppe=[PPEType.GLOVES, PPEType.BOOTS],
            actual_ppe=[PPEType.GLOVES, PPEType.BOOTS, PPEType.HAT],
        )
        assert result.status == SafetyCheckStatus.PASSED

    def test_verify_worker_ppe_failed(self, safety_manager):
        result = safety_manager.verify_worker_ppe(
            "W1",
            required_ppe=[PPEType.GLOVES, PPEType.RESPIRATOR],
            actual_ppe=[PPEType.GLOVES],
        )
        assert result.status == SafetyCheckStatus.FAILED
        assert "respirator" in result.message_en.lower()


class TestCertificationVerification:
    def test_valid_certifications(self, safety_manager):
        result = safety_manager.verify_worker_certifications(
            "W1", [SafetyCertification.PESTICIDE_APPLICATOR],
        )
        assert result.status == SafetyCheckStatus.PASSED

    def test_missing_certification(self, safety_manager):
        result = safety_manager.verify_worker_certifications(
            "W2", [SafetyCertification.PESTICIDE_APPLICATOR],
        )
        assert result.status == SafetyCheckStatus.FAILED
        assert len(result.issues) > 0

    def test_worker_not_found(self, safety_manager):
        result = safety_manager.verify_worker_certifications(
            "NOPE", [SafetyCertification.PESTICIDE_APPLICATOR],
        )
        assert result.status == SafetyCheckStatus.FAILED

    def test_expiring_soon_warning(self, safety_manager):
        # Replace cert with one expiring in 20 days
        safety_manager.workers[0].certifications = [
            WorkerCertification(
                certification_id="c1",
                certification_type=SafetyCertification.PESTICIDE_APPLICATOR,
                name="PA", name_ar="مبيد",
                issue_date=date.today() - timedelta(days=345),
                expiry_date=date.today() + timedelta(days=20),
                issuing_authority="MOA", issuing_authority_ar="وزارة",
                certificate_number="PA-001",
            ),
        ]
        safety_manager._rebuild_indexes()
        result = safety_manager.verify_worker_certifications(
            "W1", [SafetyCertification.PESTICIDE_APPLICATOR],
        )
        assert result.status == SafetyCheckStatus.WARNING


class TestHeatStressAssessment:
    def test_low_risk(self, safety_manager):
        assessment = safety_manager.assess_heat_stress("f1", temperature_c=22, humidity_percent=40)
        assert assessment.risk_level == HeatRiskLevel.LOW
        assert assessment.max_continuous_work_minutes == 60

    def test_moderate_risk(self, safety_manager):
        assessment = safety_manager.assess_heat_stress("f1", temperature_c=30, humidity_percent=50)
        assert assessment.risk_level == HeatRiskLevel.MODERATE

    def test_high_risk(self, safety_manager):
        assessment = safety_manager.assess_heat_stress("f1", temperature_c=33, humidity_percent=50)
        assert assessment.risk_level == HeatRiskLevel.HIGH
        assert assessment.water_intake_liters_per_hour >= 1.0

    def test_extreme_risk(self, safety_manager):
        assessment = safety_manager.assess_heat_stress("f1", temperature_c=42, humidity_percent=70)
        assert assessment.risk_level == HeatRiskLevel.EXTREME
        assert assessment.max_continuous_work_minutes == 15
        assert "EXTREME" in assessment.message_en

    def test_wind_cooling_effect(self, safety_manager):
        no_wind = safety_manager.assess_heat_stress("f1", temperature_c=33, humidity_percent=50, wind_speed_kmh=0)
        with_wind = safety_manager.assess_heat_stress("f1", temperature_c=33, humidity_percent=50, wind_speed_kmh=20)
        assert with_wind.heat_index_c < no_wind.heat_index_c

    def test_assessment_validity(self, safety_manager):
        assessment = safety_manager.assess_heat_stress("f1", temperature_c=30, humidity_percent=50)
        assert assessment.is_valid() is True


class TestPreTaskSafetyCheck:
    def test_create_general_task_check(self, safety_manager):
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            title="Harvest", title_ar="حصاد",
            category=TaskCategory.HARVESTING,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        assert len(check.checklist_items) >= len(GENERAL_SAFETY_CHECKLIST)

    def test_create_pesticide_task_check(self, safety_manager):
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            title="Spray", title_ar="رش",
            category=TaskCategory.PESTICIDE_APPLICATION,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        # Should include general + pesticide checklists
        assert len(check.checklist_items) >= len(GENERAL_SAFETY_CHECKLIST) + len(PESTICIDE_SAFETY_CHECKLIST)
        assert SafetyCertification.PESTICIDE_APPLICATOR in check.missing_certifications

    def test_create_check_with_rei_zone(self, safety_manager):
        now = datetime.now(UTC)
        safety_manager.create_rei_zone_from_pesticide_application(
            tenant_id="t1", farm_id="f1", field_id="field1",
            pesticide_application_id="PA1", pesticide_id="P1",
            pesticide_name="Herb", pesticide_name_ar="مبيد",
            application_time=now, rei_hours=24,
        )
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            field_id="field1",
            title="Irrigate", title_ar="ري",
            category=TaskCategory.IRRIGATION,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        assert check.rei_check_passed is False
        assert check.rei_zone_id is not None

    def test_complete_safety_check_item(self, safety_manager):
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            title="Harvest", title_ar="حصاد",
            category=TaskCategory.HARVESTING,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        item_id = check.checklist_items[0].item_id
        result = safety_manager.complete_safety_check_item(check, item_id)
        assert result is True
        assert item_id in check.completed_items

    def test_complete_invalid_item(self, safety_manager):
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            title="Harvest", title_ar="حصاد",
            category=TaskCategory.HARVESTING,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        result = safety_manager.complete_safety_check_item(check, "INVALID")
        assert result is False

    def test_verify_ppe_item(self, safety_manager):
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            title="Harvest", title_ar="حصاد",
            category=TaskCategory.HARVESTING,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        if check.ppe_missing:
            ppe = check.ppe_missing[0]
            safety_manager.verify_ppe_item(check, ppe)
            assert ppe in check.ppe_verified
            assert ppe not in check.ppe_missing

    def test_finalize_safety_check_pass(self, safety_manager):
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            title="General", title_ar="عام",
            category=TaskCategory.GENERAL_LABOR,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        # Complete all mandatory items
        for item in check.checklist_items:
            if item.is_mandatory:
                safety_manager.complete_safety_check_item(check, item.item_id)
        # Verify all PPE
        for ppe in list(check.ppe_missing):
            safety_manager.verify_ppe_item(check, ppe)
        # Clear certifications
        check.missing_certifications = []
        check.certifications_verified = True

        result = safety_manager.finalize_safety_check(check, "supervisor1")
        assert result.status == SafetyCheckStatus.PASSED
        assert check.is_approved is True

    def test_finalize_safety_check_fail_incomplete(self, safety_manager):
        task = Task(
            task_id="T1", tenant_id="t1", farm_id="f1",
            title="General", title_ar="عام",
            category=TaskCategory.GENERAL_LABOR,
        )
        check = safety_manager.create_pre_task_safety_check("t1", "f1", task, "W1")
        # Don't complete anything
        result = safety_manager.finalize_safety_check(check, "supervisor1")
        assert result.status == SafetyCheckStatus.FAILED
        assert len(result.issues) > 0


class TestSafetyViolations:
    def test_record_violation(self, safety_manager):
        violation = safety_manager.record_violation(
            tenant_id="t1", farm_id="f1",
            violation_type=SafetyViolationType.PPE_MISSING,
            severity="minor",
            worker_id="W1",
            description="Missing gloves",
            description_ar="قفازات مفقودة",
            missing_ppe=[PPEType.GLOVES],
        )
        assert violation.violation_id.startswith("VIO_")
        assert len(safety_manager.violations) == 1

    def test_get_violations_by_worker(self, safety_manager):
        safety_manager.record_violation(
            "t1", "f1", SafetyViolationType.PPE_MISSING, worker_id="W1",
        )
        safety_manager.record_violation(
            "t1", "f1", SafetyViolationType.REI_VIOLATION, worker_id="W2",
        )
        violations = safety_manager.get_violations(worker_id="W1")
        assert len(violations) == 1

    def test_get_violations_by_type(self, safety_manager):
        safety_manager.record_violation(
            "t1", "f1", SafetyViolationType.PPE_MISSING,
        )
        safety_manager.record_violation(
            "t1", "f1", SafetyViolationType.PPE_MISSING,
        )
        safety_manager.record_violation(
            "t1", "f1", SafetyViolationType.REI_VIOLATION,
        )
        violations = safety_manager.get_violations(
            violation_type=SafetyViolationType.PPE_MISSING,
        )
        assert len(violations) == 2

    def test_get_violations_unresolved_only(self, safety_manager):
        v1 = safety_manager.record_violation("t1", "f1", SafetyViolationType.PPE_MISSING)
        safety_manager.record_violation("t1", "f1", SafetyViolationType.REI_VIOLATION)
        safety_manager.resolve_violation(v1.violation_id, "admin")
        unresolved = safety_manager.get_violations(unresolved_only=True)
        assert len(unresolved) == 1

    def test_resolve_violation(self, safety_manager):
        v = safety_manager.record_violation("t1", "f1", SafetyViolationType.PPE_MISSING)
        resolved = safety_manager.resolve_violation(v.violation_id, "admin", "Fixed")
        assert resolved is not None
        assert resolved.is_resolved is True
        assert resolved.resolved_by == "admin"
        assert resolved.resolution_notes == "Fixed"

    def test_resolve_violation_not_found(self, safety_manager):
        result = safety_manager.resolve_violation("NOPE", "admin")
        assert result is None

    def test_get_safety_summary(self, safety_manager):
        safety_manager.record_violation(
            "t1", "f1", SafetyViolationType.PPE_MISSING, severity="minor",
        )
        safety_manager.record_violation(
            "t1", "f1", SafetyViolationType.REI_VIOLATION, severity="major",
        )
        summary = safety_manager.get_safety_summary("f1")
        assert summary["total_violations"] == 2
        assert summary["unresolved_violations"] == 2
        assert "ppe_missing" in summary["violations_by_type"]
        assert "minor" in summary["violations_by_severity"]
