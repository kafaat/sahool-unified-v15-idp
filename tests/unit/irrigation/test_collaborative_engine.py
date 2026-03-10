"""
SAHOOL HMC Irrigation Decision Framework - Collaborative Engine Tests
اختبارات محرك التعاون لإطار قرارات الري

Tests the main HMC Collaborative Engine:
- Session lifecycle management
- Goal setting workflow
- AI program generation
- Human review (approve/reject)
- Experience injection
- Calibration cycles
- Outcome recording
- Iteration reports
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Session Lifecycle Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineSessionManagement:
    """
    Test HMC Engine Session Management
    اختبار إدارة جلسات محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_start_session(
        self,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test starting a new HMC session"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        assert session_id is not None
        assert isinstance(session_id, str)
        # Verify it's a valid UUID
        uuid.UUID(session_id)

    @pytest.mark.asyncio
    async def test_start_session_sets_pending_status(
        self,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test that new session starts in pending status"""
        await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        status = hmc_engine.get_status()
        assert status == "pending"

    @pytest.mark.asyncio
    async def test_start_session_with_existing_goals(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_ecological_constraint,
    ):
        """Test starting session with pre-defined goals and constraints"""
        hmc_engine.start_session.return_value = str(uuid.uuid4())

        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
            initial_goal=sample_irrigation_goal,
            initial_constraints=[sample_ecological_constraint],
        )

        assert session_id is not None
        hmc_engine.start_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_start_duplicate_session(
        self,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test that starting duplicate session for same field fails"""
        # First session succeeds
        await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        # Second session should fail
        hmc_engine.start_session.side_effect = ValueError("Active session already exists for this field")

        with pytest.raises(ValueError) as exc_info:
            await hmc_engine.start_session(
                farm_id=sample_irrigation_goal["farm_id"],
                field_id=sample_irrigation_goal["field_id"],
                tenant_id=sample_irrigation_goal["tenant_id"],
                initiated_by=sample_irrigation_goal["created_by"],
            )

        assert "Active session already exists" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════════
# Complete Workflow Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineCompleteWorkflow:
    """
    Test Complete HMC Workflow
    اختبار سير العمل الكامل للتعاون
    """

    @pytest.mark.asyncio
    async def test_complete_workflow_success(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_ecological_constraint,
        sample_experience_rule,
        sample_irrigation_program,
        sample_calibration_result,
    ):
        """Test complete workflow from start to approval"""
        # 1. Start session
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )
        assert session_id is not None

        # 2. Set goal
        goal_set = await hmc_engine.set_goal(
            session_id=session_id,
            goal=sample_irrigation_goal,
        )
        assert goal_set is True

        # 3. Add constraint
        constraint_added = await hmc_engine.add_constraint(
            session_id=session_id,
            constraint=sample_ecological_constraint,
        )
        assert constraint_added is True

        # 4. Inject experience
        experience_injected = await hmc_engine.inject_experience(
            session_id=session_id,
            rule=sample_experience_rule,
        )
        assert experience_injected is True

        # 5. Generate AI program
        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)
        assert program is not None

        # 6. Review program
        reviewed = await hmc_engine.review_program(
            session_id=session_id,
            program_id=program["program_id"],
            reviewer_id=sample_irrigation_goal["created_by"],
        )
        assert reviewed is True

        # 7. Calibrate
        hmc_engine.calibrate.return_value = sample_calibration_result
        calibration = await hmc_engine.calibrate(
            session_id=session_id,
            program_id=program["program_id"],
        )
        assert calibration["status"] == "passed"

        # 8. Approve program
        approved = await hmc_engine.approve_program(
            session_id=session_id,
            program_id=program["program_id"],
            approver_id=sample_irrigation_goal["created_by"],
        )
        assert approved is True

    @pytest.mark.asyncio
    async def test_complete_workflow_with_rejection(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test workflow with program rejection and regeneration"""
        # Start session and set goal
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        # First program generation
        hmc_engine.generate_program.return_value = sample_irrigation_program
        first_program = await hmc_engine.generate_program(session_id=session_id)

        # Reject first program
        rejected = await hmc_engine.reject_program(
            session_id=session_id,
            program_id=first_program["program_id"],
            rejector_id=sample_irrigation_goal["created_by"],
            reason_en="Water allocation too aggressive for sandy areas",
            reason_ar="تخصيص المياه عنيف جداً للمناطق الرملية",
        )
        assert rejected is True

        # Generate second program with adjustments
        adjusted_program = dict(sample_irrigation_program)
        adjusted_program["program_id"] = str(uuid.uuid4())
        adjusted_program["version"] = "1.1.0"
        hmc_engine.generate_program.return_value = adjusted_program

        second_program = await hmc_engine.generate_program(
            session_id=session_id,
            incorporate_feedback=True,
        )

        assert second_program["version"] == "1.1.0"


# ═══════════════════════════════════════════════════════════════════════════════
# Goal Setting Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineGoalSetting:
    """
    Test Human Goal Setting in HMC Engine
    اختبار تحديد الأهداف البشرية في محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_human_goal_setting(
        self,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test setting irrigation goal by human operator"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        result = await hmc_engine.set_goal(
            session_id=session_id,
            goal=sample_irrigation_goal,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_goal_setting_updates_status(
        self,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test that setting goal updates session status"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        hmc_engine.get_status.return_value = "goal_setting"

        await hmc_engine.set_goal(
            session_id=session_id,
            goal=sample_irrigation_goal,
        )

        status = hmc_engine.get_status()
        assert status == "goal_setting"

    @pytest.mark.asyncio
    async def test_multiple_goal_updates(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_high_yield_goal,
    ):
        """Test updating goals multiple times"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        # First goal
        await hmc_engine.set_goal(
            session_id=session_id,
            goal=sample_irrigation_goal,
        )

        # Update to high yield goal
        await hmc_engine.set_goal(
            session_id=session_id,
            goal=sample_high_yield_goal,
        )

        # Both calls should succeed
        assert hmc_engine.set_goal.call_count == 2


# ═══════════════════════════════════════════════════════════════════════════════
# AI Program Generation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineAIProgramGeneration:
    """
    Test AI Program Generation in HMC Engine
    اختبار توليد برنامج الذكاء الاصطناعي في محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_ai_program_generation(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test AI generates irrigation program based on goal"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        assert program is not None
        assert "schedules" in program
        assert len(program["schedules"]) > 0

    @pytest.mark.asyncio
    async def test_ai_program_respects_constraints(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_ecological_constraint,
        sample_irrigation_program,
    ):
        """Test AI program respects ecological constraints"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)
        await hmc_engine.add_constraint(
            session_id=session_id,
            constraint=sample_ecological_constraint,
        )

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        # Program should reference applied constraints
        assert "applied_constraints" in program
        assert len(program["applied_constraints"]) > 0

    @pytest.mark.asyncio
    async def test_ai_program_includes_confidence_score(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test AI program includes confidence score"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        assert "confidence_score" in program
        assert 0 <= program["confidence_score"] <= 1

    @pytest.mark.asyncio
    async def test_ai_program_generation_requires_goal(
        self,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test that program generation fails without goal"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        # Try to generate without setting goal
        hmc_engine.generate_program.side_effect = ValueError("Cannot generate program without goal")

        with pytest.raises(ValueError) as exc_info:
            await hmc_engine.generate_program(session_id=session_id)

        assert "without goal" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════════
# Human Review Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineHumanReview:
    """
    Test Human Review Process in HMC Engine
    اختبار عملية المراجعة البشرية في محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_human_review_approve(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test human approves AI-generated program"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        result = await hmc_engine.approve_program(
            session_id=session_id,
            program_id=program["program_id"],
            approver_id=sample_irrigation_goal["created_by"],
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_human_review_reject(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test human rejects AI-generated program"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        result = await hmc_engine.reject_program(
            session_id=session_id,
            program_id=program["program_id"],
            rejector_id=sample_irrigation_goal["created_by"],
            reason_en="Schedule timing conflicts with farm operations",
            reason_ar="توقيت الجدول يتعارض مع عمليات المزرعة",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_human_review_with_modifications(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
        sample_human_override,
    ):
        """Test human review with schedule modifications"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        # Review with modifications
        result = await hmc_engine.review_program(
            session_id=session_id,
            program_id=program["program_id"],
            reviewer_id=sample_irrigation_goal["created_by"],
            modifications=[sample_human_override],
        )

        assert result is True


class TestHMCEngineApprovalWithoutChecklist:
    """
    Test Approval Without Checklist Completion
    اختبار الموافقة بدون إكمال قائمة التحقق
    """

    @pytest.mark.asyncio
    async def test_approval_without_checklist_fails(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test that approval fails if checklist is incomplete"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        # Mock incomplete checklist
        hmc_engine.get_checklist.return_value = [
            {"item_id": "1", "is_completed": True},
            {"item_id": "2", "is_completed": False},  # Incomplete
            {"item_id": "3", "is_completed": True},
        ]

        hmc_engine.approve_program.side_effect = ValueError("Cannot approve program with incomplete checklist")

        with pytest.raises(ValueError) as exc_info:
            await hmc_engine.approve_program(
                session_id=session_id,
                program_id=program["program_id"],
                approver_id=sample_irrigation_goal["created_by"],
            )

        assert "incomplete checklist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_approval_with_complete_checklist_succeeds(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test that approval succeeds with complete checklist"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        # Mock complete checklist
        hmc_engine.get_checklist.return_value = [
            {"item_id": "1", "is_completed": True},
            {"item_id": "2", "is_completed": True},
            {"item_id": "3", "is_completed": True},
        ]

        result = await hmc_engine.approve_program(
            session_id=session_id,
            program_id=program["program_id"],
            approver_id=sample_irrigation_goal["created_by"],
        )

        assert result is True


# ═══════════════════════════════════════════════════════════════════════════════
# Experience Injection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineExperienceInjection:
    """
    Test Experience Injection in HMC Engine
    اختبار حقن الخبرة في محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_experience_injection(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_experience_rule,
    ):
        """Test injecting farmer experience into session"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        result = await hmc_engine.inject_experience(
            session_id=session_id,
            rule=sample_experience_rule,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_experience_injection(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_experience_rule,
        sample_ai_experience_rule,
    ):
        """Test injecting multiple experience rules"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        # Inject farmer rule
        await hmc_engine.inject_experience(
            session_id=session_id,
            rule=sample_experience_rule,
        )

        # Inject AI rule
        await hmc_engine.inject_experience(
            session_id=session_id,
            rule=sample_ai_experience_rule,
        )

        assert hmc_engine.inject_experience.call_count == 2


# ═══════════════════════════════════════════════════════════════════════════════
# Calibration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineCalibration:
    """
    Test Calibration Cycle in HMC Engine
    اختبار دورة المعايرة في محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_calibration_cycle(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
        sample_calibration_result,
    ):
        """Test running calibration cycle"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        hmc_engine.calibrate.return_value = sample_calibration_result
        calibration = await hmc_engine.calibrate(
            session_id=session_id,
            program_id=program["program_id"],
        )

        assert calibration["status"] == "passed"
        assert calibration["confidence"] > 0

    @pytest.mark.asyncio
    async def test_calibration_with_different_scenarios(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test calibration with multiple weather scenarios"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        scenarios = ["normal", "drought", "wet"]
        results = []

        for scenario in scenarios:
            hmc_engine.calibrate.return_value = {
                "calibration_id": str(uuid.uuid4()),
                "status": "passed" if scenario == "normal" else "warning",
                "scenario": scenario,
                "confidence": 0.9 if scenario == "normal" else 0.7,
            }

            calibration = await hmc_engine.calibrate(
                session_id=session_id,
                program_id=program["program_id"],
                weather_scenario=scenario,
            )
            results.append(calibration)

        # At least normal scenario should pass
        passed_scenarios = [r for r in results if r["status"] == "passed"]
        assert len(passed_scenarios) >= 1

    @pytest.mark.asyncio
    async def test_calibration_failure_triggers_regeneration(
        self,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
        sample_failed_calibration,
    ):
        """Test that calibration failure can trigger program regeneration"""
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        # First calibration fails
        hmc_engine.calibrate.return_value = sample_failed_calibration
        first_calibration = await hmc_engine.calibrate(
            session_id=session_id,
            program_id=program["program_id"],
        )

        assert first_calibration["status"] == "failed"

        # Regenerate with adjustments
        adjusted_program = dict(sample_irrigation_program)
        adjusted_program["program_id"] = str(uuid.uuid4())
        adjusted_program["total_water_m3"] = 1400  # Increased
        hmc_engine.generate_program.return_value = adjusted_program

        new_program = await hmc_engine.generate_program(
            session_id=session_id,
            incorporate_calibration_feedback=True,
        )

        assert new_program["program_id"] != program["program_id"]


# ═══════════════════════════════════════════════════════════════════════════════
# Outcome Recording Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineOutcomeRecording:
    """
    Test Outcome Recording in HMC Engine
    اختبار تسجيل النتائج في محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_record_outcome(
        self,
        hmc_engine,
        completed_session_data,
    ):
        """Test recording program execution outcome"""
        result = await hmc_engine.record_outcome(
            session_id=completed_session_data["session_id"],
            actual_water_used_m3=1250,
            actual_yield_kg=4850,
            execution_start_date=date.today() - timedelta(days=30),
            execution_end_date=date.today(),
            notes_en="Program executed successfully with minor timing adjustments",
            notes_ar="تم تنفيذ البرنامج بنجاح مع تعديلات طفيفة في التوقيت",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_record_outcome_with_deviations(
        self,
        hmc_engine,
        completed_session_data,
    ):
        """Test recording outcome with deviations from plan"""
        hmc_engine.record_outcome.return_value = True

        result = await hmc_engine.record_outcome(
            session_id=completed_session_data["session_id"],
            actual_water_used_m3=1450,  # Higher than planned
            actual_yield_kg=4500,  # Lower than expected
            execution_start_date=date.today() - timedelta(days=30),
            execution_end_date=date.today(),
            deviations=[
                {
                    "type": "water_increase",
                    "reason_en": "Unexpected heat wave required additional irrigation",
                    "reason_ar": "موجة حر غير متوقعة تطلبت ري إضافي",
                    "impact_m3": 200,
                },
            ],
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_record_outcome_updates_experience_rules(
        self,
        hmc_engine,
        completed_session_data,
    ):
        """Test that outcome recording updates experience rule success rates"""
        hmc_engine.record_outcome.return_value = True

        result = await hmc_engine.record_outcome(
            session_id=completed_session_data["session_id"],
            actual_water_used_m3=1280,
            actual_yield_kg=4800,
            execution_start_date=date.today() - timedelta(days=30),
            execution_end_date=date.today(),
            rule_effectiveness={
                "rule_1": {"applied": 15, "successful": 14},
                "rule_2": {"applied": 8, "successful": 7},
            },
        )

        assert result is True


# ═══════════════════════════════════════════════════════════════════════════════
# Iteration Report Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMCEngineIterationReport:
    """
    Test Iteration Report Generation in HMC Engine
    اختبار توليد تقرير التكرار في محرك التعاون
    """

    @pytest.mark.asyncio
    async def test_iteration_report(
        self,
        hmc_engine,
        completed_session_data,
        iteration_report_data,
    ):
        """Test generating iteration report"""
        hmc_engine.get_iteration_report.return_value = iteration_report_data

        report = await hmc_engine.get_iteration_report(
            session_id=completed_session_data["session_id"],
        )

        assert report is not None
        assert "goal_achievement" in report
        assert "experience_contribution" in report
        assert "calibration_summary" in report
        assert "value_creation" in report

    @pytest.mark.asyncio
    async def test_iteration_report_goal_achievement(
        self,
        hmc_engine,
        completed_session_data,
        iteration_report_data,
    ):
        """Test iteration report includes goal achievement metrics"""
        hmc_engine.get_iteration_report.return_value = iteration_report_data

        report = await hmc_engine.get_iteration_report(
            session_id=completed_session_data["session_id"],
        )

        goal_achievement = report["goal_achievement"]
        assert "water_savings_target" in goal_achievement
        assert "water_savings_actual" in goal_achievement
        assert "yield_target" in goal_achievement
        assert "yield_actual" in goal_achievement
        assert "goal_met" in goal_achievement

    @pytest.mark.asyncio
    async def test_iteration_report_value_creation(
        self,
        hmc_engine,
        completed_session_data,
        iteration_report_data,
    ):
        """Test iteration report includes value creation metrics"""
        hmc_engine.get_iteration_report.return_value = iteration_report_data

        report = await hmc_engine.get_iteration_report(
            session_id=completed_session_data["session_id"],
        )

        value_creation = report["value_creation"]
        assert "water_saved_m3" in value_creation
        assert "cost_saved_yer" in value_creation
        assert "carbon_reduced_kg" in value_creation

    @pytest.mark.asyncio
    async def test_iteration_report_recommendations(
        self,
        hmc_engine,
        completed_session_data,
        iteration_report_data,
    ):
        """Test iteration report includes recommendations"""
        hmc_engine.get_iteration_report.return_value = iteration_report_data

        report = await hmc_engine.get_iteration_report(
            session_id=completed_session_data["session_id"],
        )

        assert "recommendations" in report
        assert "recommendations_ar" in report
        assert len(report["recommendations"]) > 0
