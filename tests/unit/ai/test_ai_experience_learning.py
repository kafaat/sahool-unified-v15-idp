"""
Tests for shared/ai/experience_learning.py module
اختبارات وحدة التعلم القائم على الخبرة
"""

import pytest
from datetime import datetime, UTC


class TestExecutionStatus:
    """Tests for ExecutionStatus enum"""

    def test_status_values(self):
        """Test all status values exist"""
        from shared.ai.experience_learning import ExecutionStatus

        assert ExecutionStatus.SUCCESS == "success"
        assert ExecutionStatus.PARTIAL == "partial"
        assert ExecutionStatus.FAILURE == "failure"
        assert ExecutionStatus.TIMEOUT == "timeout"

    def test_status_is_string_enum(self):
        """Test ExecutionStatus is a string enum"""
        from shared.ai.experience_learning import ExecutionStatus

        assert isinstance(ExecutionStatus.SUCCESS, str)


class TestSOPConfidence:
    """Tests for SOPConfidence enum"""

    def test_confidence_values(self):
        """Test all confidence values exist"""
        from shared.ai.experience_learning import SOPConfidence

        assert SOPConfidence.HIGH == "high"
        assert SOPConfidence.MEDIUM == "medium"
        assert SOPConfidence.LOW == "low"
        assert SOPConfidence.EXPERIMENTAL == "experimental"


class TestExecutionStep:
    """Tests for ExecutionStep dataclass"""

    def test_create_minimal_step(self):
        """Test creating step with minimal fields"""
        from shared.ai.experience_learning import ExecutionStep

        step = ExecutionStep(step_number=1, action="fetch_data")

        assert step.step_number == 1
        assert step.action == "fetch_data"
        assert step.action_ar is None
        assert step.parameters == {}
        assert step.result is None
        assert step.duration_ms == 0
        assert step.success is True
        assert step.error_message is None

    def test_create_full_step(self):
        """Test creating step with all fields"""
        from shared.ai.experience_learning import ExecutionStep

        step = ExecutionStep(
            step_number=1,
            action="fetch_weather",
            action_ar="جلب الطقس",
            parameters={"location": "Aden"},
            result={"temp": 28},
            duration_ms=150,
            success=True,
        )

        assert step.action_ar == "جلب الطقس"
        assert step.parameters["location"] == "Aden"
        assert step.result["temp"] == 28
        assert step.duration_ms == 150

    def test_step_to_dict(self):
        """Test step serialization to dict"""
        from shared.ai.experience_learning import ExecutionStep

        step = ExecutionStep(
            step_number=2,
            action="analyze_ndvi",
            parameters={"field_id": "F001"},
            duration_ms=500,
        )

        result = step.to_dict()

        assert result["step_number"] == 2
        assert result["action"] == "analyze_ndvi"
        assert result["parameters"] == {"field_id": "F001"}
        assert result["duration_ms"] == 500
        assert result["success"] is True

    def test_step_from_dict(self):
        """Test step deserialization from dict"""
        from shared.ai.experience_learning import ExecutionStep

        data = {
            "step_number": 3,
            "action": "send_alert",
            "action_ar": "إرسال تنبيه",
            "parameters": {"type": "warning"},
            "result": {"sent": True},
            "duration_ms": 200,
            "success": True,
        }

        step = ExecutionStep.from_dict(data)

        assert step.step_number == 3
        assert step.action == "send_alert"
        assert step.action_ar == "إرسال تنبيه"

    def test_step_roundtrip(self):
        """Test step roundtrip through dict"""
        from shared.ai.experience_learning import ExecutionStep

        original = ExecutionStep(
            step_number=1,
            action="test_action",
            parameters={"key": "value"},
            duration_ms=100,
        )

        data = original.to_dict()
        restored = ExecutionStep.from_dict(data)

        assert restored.step_number == original.step_number
        assert restored.action == original.action
        assert restored.parameters == original.parameters

    def test_failed_step(self):
        """Test creating a failed step"""
        from shared.ai.experience_learning import ExecutionStep

        step = ExecutionStep(
            step_number=1,
            action="connect_db",
            success=False,
            error_message="Connection timeout",
        )

        assert step.success is False
        assert step.error_message == "Connection timeout"


class TestTaskExecution:
    """Tests for TaskExecution dataclass"""

    def test_create_execution(self):
        """Test creating task execution"""
        from shared.ai.experience_learning import TaskExecution, ExecutionStep, ExecutionStatus

        steps = [
            ExecutionStep(step_number=1, action="step1", duration_ms=100),
            ExecutionStep(step_number=2, action="step2", duration_ms=200),
        ]

        execution = TaskExecution(
            id="exec-001",
            task_type="irrigation_advisory",
            task_description="Generate irrigation recommendation",
            task_description_ar="توليد توصية الري",
            context={"field_id": "F001", "crop": "wheat"},
            steps=steps,
            status=ExecutionStatus.SUCCESS,
            total_duration_ms=300,
            timestamp=datetime.now(UTC),
            tenant_id="tenant-001",
            agent_id="agent-001",
        )

        assert execution.id == "exec-001"
        assert execution.task_type == "irrigation_advisory"
        assert len(execution.steps) == 2
        assert execution.status == ExecutionStatus.SUCCESS

    def test_execution_to_dict(self):
        """Test execution serialization to dict"""
        from shared.ai.experience_learning import TaskExecution, ExecutionStep, ExecutionStatus

        execution = TaskExecution(
            id="exec-002",
            task_type="fertilizer_advisory",
            task_description="Generate fertilizer recommendation",
            task_description_ar=None,
            context={"soil_n": 18},
            steps=[ExecutionStep(step_number=1, action="analyze")],
            status=ExecutionStatus.SUCCESS,
            total_duration_ms=500,
            timestamp=datetime.now(UTC),
            tenant_id="tenant-001",
            agent_id="agent-001",
            outcome_score=0.85,
        )

        result = execution.to_dict()

        assert result["id"] == "exec-002"
        assert result["task_type"] == "fertilizer_advisory"
        assert result["status"] == "success"
        assert result["outcome_score"] == 0.85
        assert len(result["steps"]) == 1

    def test_execution_from_dict(self):
        """Test execution deserialization from dict"""
        from shared.ai.experience_learning import TaskExecution, ExecutionStatus

        data = {
            "id": "exec-003",
            "task_type": "pest_detection",
            "task_description": "Detect pests in field",
            "context": {},
            "steps": [{"step_number": 1, "action": "scan"}],
            "status": "failure",
            "total_duration_ms": 1000,
            "timestamp": "2025-01-15T10:00:00+00:00",
            "tenant_id": "t001",
            "agent_id": "a001",
        }

        execution = TaskExecution.from_dict(data)

        assert execution.id == "exec-003"
        assert execution.status == ExecutionStatus.FAILURE
        assert len(execution.steps) == 1


class TestSOP:
    """Tests for SOP (Standard Operating Procedure) dataclass"""

    def test_create_sop(self):
        """Test creating SOP"""
        from shared.ai.experience_learning import SOP, SOPConfidence

        sop = SOP(
            id="sop-001",
            task_type="irrigation_advisory",
            name="Irrigation SOP",
            name_ar="إجراء الري القياسي",
            description="Standard procedure for irrigation advisory",
            description_ar="إجراء قياسي لاستشارات الري",
            steps=[{"step_number": 1, "action": "check_soil_moisture"}],
            preconditions=["Field ID required"],
            postconditions=["Recommendation generated"],
            confidence=SOPConfidence.MEDIUM,
            success_count=3,
            failure_count=1,
            avg_duration_ms=450,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            source_executions=["exec-001", "exec-002"],
        )

        assert sop.id == "sop-001"
        assert sop.task_type == "irrigation_advisory"
        assert sop.confidence == SOPConfidence.MEDIUM
        assert sop.success_count == 3

    def test_sop_success_rate(self):
        """Test SOP success rate calculation"""
        from shared.ai.experience_learning import SOP, SOPConfidence

        sop = SOP(
            id="sop-002",
            task_type="test",
            name="Test SOP",
            name_ar=None,
            description="Test",
            description_ar=None,
            steps=[],
            preconditions=[],
            postconditions=[],
            confidence=SOPConfidence.HIGH,
            success_count=8,
            failure_count=2,
            avg_duration_ms=100,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            source_executions=[],
        )

        assert sop.success_rate == 0.8  # 8/10

    def test_sop_success_rate_no_executions(self):
        """Test SOP success rate with no executions"""
        from shared.ai.experience_learning import SOP, SOPConfidence

        sop = SOP(
            id="sop-003",
            task_type="test",
            name="Empty SOP",
            name_ar=None,
            description="Test",
            description_ar=None,
            steps=[],
            preconditions=[],
            postconditions=[],
            confidence=SOPConfidence.EXPERIMENTAL,
            success_count=0,
            failure_count=0,
            avg_duration_ms=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            source_executions=[],
        )

        assert sop.success_rate == 0.0

    def test_sop_to_dict(self):
        """Test SOP serialization to dict"""
        from shared.ai.experience_learning import SOP, SOPConfidence

        sop = SOP(
            id="sop-004",
            task_type="weather_fetch",
            name="Weather Fetch SOP",
            name_ar="إجراء جلب الطقس",
            description="Fetch weather data",
            description_ar="جلب بيانات الطقس",
            steps=[{"step_number": 1, "action": "call_api"}],
            preconditions=["API key required"],
            postconditions=["Weather data returned"],
            confidence=SOPConfidence.HIGH,
            success_count=10,
            failure_count=1,
            avg_duration_ms=200,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            source_executions=["e1", "e2"],
        )

        result = sop.to_dict()

        assert result["id"] == "sop-004"
        assert result["confidence"] == "high"
        assert result["success_rate"] == pytest.approx(0.909, rel=0.01)
        assert len(result["steps"]) == 1

    def test_sop_from_dict(self):
        """Test SOP deserialization from dict"""
        from shared.ai.experience_learning import SOP, SOPConfidence

        data = {
            "id": "sop-005",
            "task_type": "analysis",
            "name": "Analysis SOP",
            "description": "Data analysis procedure",
            "steps": [],
            "preconditions": [],
            "postconditions": [],
            "confidence": "medium",
            "success_count": 5,
            "failure_count": 2,
            "avg_duration_ms": 300,
            "created_at": "2025-01-15T10:00:00+00:00",
            "updated_at": "2025-01-15T12:00:00+00:00",
            "source_executions": [],
        }

        sop = SOP.from_dict(data)

        assert sop.id == "sop-005"
        assert sop.confidence == SOPConfidence.MEDIUM


class TestExperienceStore:
    """Tests for ExperienceStore class"""

    @pytest.fixture
    def store(self):
        """Create a fresh store for each test"""
        from shared.ai.experience_learning import ExperienceStore

        return ExperienceStore()

    @pytest.fixture
    def sample_execution(self):
        """Create a sample execution"""
        from shared.ai.experience_learning import TaskExecution, ExecutionStep, ExecutionStatus

        return TaskExecution(
            id="test-exec-001",
            task_type="irrigation_advisory",
            task_description="Test execution",
            task_description_ar=None,
            context={"field_id": "F001"},
            steps=[ExecutionStep(step_number=1, action="test")],
            status=ExecutionStatus.SUCCESS,
            total_duration_ms=100,
            timestamp=datetime.now(UTC),
            tenant_id="t001",
            agent_id="a001",
        )

    @pytest.mark.asyncio
    async def test_store_execution(self, store, sample_execution):
        """Test storing an execution"""
        await store.store_execution(sample_execution)

        result = await store.get_execution(sample_execution.id)
        assert result is not None
        assert result.id == sample_execution.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_execution(self, store):
        """Test getting nonexistent execution returns None"""
        result = await store.get_execution("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_executions_by_type(self, store):
        """Test getting executions by task type"""
        from shared.ai.experience_learning import TaskExecution, ExecutionStep, ExecutionStatus

        # Store multiple executions
        for i in range(3):
            exec_ = TaskExecution(
                id=f"exec-{i}",
                task_type="irrigation_advisory",
                task_description=f"Test {i}",
                task_description_ar=None,
                context={},
                steps=[ExecutionStep(step_number=1, action="test")],
                status=ExecutionStatus.SUCCESS,
                total_duration_ms=100,
                timestamp=datetime.now(UTC),
                tenant_id="t001",
                agent_id="a001",
            )
            await store.store_execution(exec_)

        results = await store.get_executions_by_type("irrigation_advisory")
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_executions_by_type_with_status_filter(self, store):
        """Test filtering executions by status"""
        from shared.ai.experience_learning import TaskExecution, ExecutionStep, ExecutionStatus

        # Store success and failure
        success_exec = TaskExecution(
            id="success-1",
            task_type="test_type",
            task_description="Success",
            task_description_ar=None,
            context={},
            steps=[ExecutionStep(step_number=1, action="test")],
            status=ExecutionStatus.SUCCESS,
            total_duration_ms=100,
            timestamp=datetime.now(UTC),
            tenant_id="t001",
            agent_id="a001",
        )
        failure_exec = TaskExecution(
            id="failure-1",
            task_type="test_type",
            task_description="Failure",
            task_description_ar=None,
            context={},
            steps=[ExecutionStep(step_number=1, action="test")],
            status=ExecutionStatus.FAILURE,
            total_duration_ms=100,
            timestamp=datetime.now(UTC),
            tenant_id="t001",
            agent_id="a001",
        )

        await store.store_execution(success_exec)
        await store.store_execution(failure_exec)

        success_results = await store.get_executions_by_type("test_type", status=ExecutionStatus.SUCCESS)
        assert len(success_results) == 1
        assert success_results[0].id == "success-1"

    @pytest.mark.asyncio
    async def test_store_and_get_sop(self, store):
        """Test storing and getting SOP"""
        from shared.ai.experience_learning import SOP, SOPConfidence

        sop = SOP(
            id="sop-test-001",
            task_type="irrigation_advisory",
            name="Test SOP",
            name_ar=None,
            description="Test",
            description_ar=None,
            steps=[],
            preconditions=[],
            postconditions=[],
            confidence=SOPConfidence.HIGH,
            success_count=5,
            failure_count=1,
            avg_duration_ms=100,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            source_executions=[],
        )

        await store.store_sop(sop)
        result = await store.get_sop("sop-test-001")

        assert result is not None
        assert result.id == "sop-test-001"

    @pytest.mark.asyncio
    async def test_get_best_sop(self, store):
        """Test getting best SOP by confidence"""
        from shared.ai.experience_learning import SOP, SOPConfidence

        # Create SOPs with different confidence levels
        low_sop = SOP(
            id="low-sop",
            task_type="test_type",
            name="Low SOP",
            name_ar=None,
            description="Low confidence",
            description_ar=None,
            steps=[],
            preconditions=[],
            postconditions=[],
            confidence=SOPConfidence.LOW,
            success_count=2,
            failure_count=1,
            avg_duration_ms=100,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            source_executions=[],
        )
        high_sop = SOP(
            id="high-sop",
            task_type="test_type",
            name="High SOP",
            name_ar=None,
            description="High confidence",
            description_ar=None,
            steps=[],
            preconditions=[],
            postconditions=[],
            confidence=SOPConfidence.HIGH,
            success_count=10,
            failure_count=1,
            avg_duration_ms=100,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            source_executions=[],
        )

        await store.store_sop(low_sop)
        await store.store_sop(high_sop)

        best = await store.get_best_sop("test_type")
        assert best is not None
        assert best.id == "high-sop"

    @pytest.mark.asyncio
    async def test_get_best_sop_no_sops(self, store):
        """Test getting best SOP when none exist"""
        result = await store.get_best_sop("nonexistent_type")
        assert result is None


class TestExperienceLearner:
    """Tests for ExperienceLearner class"""

    @pytest.fixture
    def learner(self):
        """Create a fresh learner for each test"""
        from shared.ai.experience_learning import ExperienceLearner

        return ExperienceLearner()

    @pytest.mark.asyncio
    async def test_record_execution(self, learner):
        """Test recording an execution"""
        from shared.ai.experience_learning import ExecutionStep, ExecutionStatus

        steps = [
            ExecutionStep(step_number=1, action="fetch_data", duration_ms=100),
            ExecutionStep(step_number=2, action="process", duration_ms=200),
        ]

        execution = await learner.record_execution(
            task_type="data_processing",
            task_description="Process field data",
            steps=steps,
            status=ExecutionStatus.SUCCESS,
            context={"field_id": "F001"},
            tenant_id="tenant-001",
            agent_id="agent-001",
        )

        assert execution.id is not None
        assert execution.task_type == "data_processing"
        assert execution.total_duration_ms == 300

    @pytest.mark.asyncio
    async def test_sop_generated_after_multiple_successes(self, learner):
        """Test SOP is generated after multiple successful executions"""
        from shared.ai.experience_learning import ExecutionStep, ExecutionStatus

        # Record multiple successful executions
        for i in range(3):
            steps = [
                ExecutionStep(step_number=1, action="step_a", duration_ms=100),
                ExecutionStep(step_number=2, action="step_b", duration_ms=100),
            ]
            await learner.record_execution(
                task_type="recurring_task",
                task_description=f"Recurring task {i}",
                steps=steps,
                status=ExecutionStatus.SUCCESS,
                context={"iteration": i},
                tenant_id="t001",
                agent_id="a001",
            )

        # Check if SOP was generated
        sop = await learner.get_recommended_sop("recurring_task")
        assert sop is not None
        assert sop.task_type == "recurring_task"
        assert len(sop.steps) == 2

    @pytest.mark.asyncio
    async def test_get_execution_guidance_no_sop(self, learner):
        """Test getting guidance when no SOP exists"""
        guidance = await learner.get_execution_guidance("unknown_task")

        assert guidance["has_sop"] is False
        assert "message" in guidance
        assert "message_ar" in guidance

    @pytest.mark.asyncio
    async def test_get_execution_guidance_with_sop(self, learner):
        """Test getting guidance when SOP exists"""
        from shared.ai.experience_learning import ExecutionStep, ExecutionStatus

        # Create enough executions for SOP
        for i in range(3):
            steps = [ExecutionStep(step_number=1, action="test_action", duration_ms=50)]
            await learner.record_execution(
                task_type="guided_task",
                task_description="Task with guidance",
                steps=steps,
                status=ExecutionStatus.SUCCESS,
                context={},
                tenant_id="t001",
                agent_id="a001",
            )

        guidance = await learner.get_execution_guidance("guided_task")

        assert guidance["has_sop"] is True
        assert "sop_id" in guidance
        assert "recommended_steps" in guidance

    @pytest.mark.asyncio
    async def test_get_learning_stats(self, learner):
        """Test getting learning statistics"""
        from shared.ai.experience_learning import ExecutionStep, ExecutionStatus

        # Record some executions
        steps = [ExecutionStep(step_number=1, action="test", duration_ms=100)]

        await learner.record_execution(
            task_type="stats_test",
            task_description="Test 1",
            steps=steps,
            status=ExecutionStatus.SUCCESS,
            context={},
            tenant_id="t001",
            agent_id="a001",
        )
        await learner.record_execution(
            task_type="stats_test",
            task_description="Test 2",
            steps=steps,
            status=ExecutionStatus.FAILURE,
            context={},
            tenant_id="t001",
            agent_id="a001",
        )

        stats = await learner.get_learning_stats("stats_test")

        assert stats["total_executions"] == 2
        assert stats["successful_executions"] == 1
        assert stats["failed_executions"] == 1
        assert stats["success_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_failed_execution_updates_sop(self, learner):
        """Test that failed execution updates SOP statistics"""
        from shared.ai.experience_learning import ExecutionStep, ExecutionStatus, SOPConfidence

        # Create successful executions to generate SOP
        for i in range(5):
            steps = [ExecutionStep(step_number=1, action="test", duration_ms=100)]
            await learner.record_execution(
                task_type="failure_test",
                task_description="Success",
                steps=steps,
                status=ExecutionStatus.SUCCESS,
                context={},
                tenant_id="t001",
                agent_id="a001",
            )

        # Check initial SOP
        initial_sop = await learner.get_recommended_sop("failure_test")
        assert initial_sop is not None
        initial_failures = initial_sop.failure_count

        # Record a failure
        steps = [ExecutionStep(step_number=1, action="test", duration_ms=100)]
        await learner.record_execution(
            task_type="failure_test",
            task_description="Failure",
            steps=steps,
            status=ExecutionStatus.FAILURE,
            context={},
            tenant_id="t001",
            agent_id="a001",
        )

        # Check updated SOP
        updated_sop = await learner.get_recommended_sop("failure_test")
        assert updated_sop.failure_count == initial_failures + 1


class TestConvenienceFunctions:
    """Tests for module-level convenience functions"""

    @pytest.mark.asyncio
    async def test_record_task_execution(self):
        """Test convenience function for recording execution"""
        from shared.ai.experience_learning import record_task_execution

        execution = await record_task_execution(
            task_type="convenience_test",
            task_description="Test via convenience function",
            steps=[
                {"action": "step1", "duration_ms": 100},
                {"action": "step2", "duration_ms": 200},
            ],
            success=True,
            context={"key": "value"},
            tenant_id="t001",
            agent_id="a001",
        )

        assert execution.id is not None
        assert execution.task_type == "convenience_test"
        assert len(execution.steps) == 2

    @pytest.mark.asyncio
    async def test_get_task_guidance(self):
        """Test convenience function for getting guidance"""
        from shared.ai.experience_learning import get_task_guidance

        guidance = await get_task_guidance("unknown_task_type")

        assert "has_sop" in guidance

    def test_get_experience_learner_singleton(self):
        """Test that get_experience_learner returns singleton"""
        from shared.ai.experience_learning import get_experience_learner

        learner1 = get_experience_learner()
        learner2 = get_experience_learner()

        assert learner1 is learner2


class TestSOPConfidenceProgression:
    """Tests for SOP confidence level progression"""

    @pytest.mark.asyncio
    async def test_confidence_increases_with_successes(self):
        """Test SOP confidence increases with more successes"""
        from shared.ai.experience_learning import (
            ExperienceLearner,
            ExecutionStep,
            ExecutionStatus,
            SOPConfidence,
        )

        learner = ExperienceLearner()

        # Record 2 successes - should be LOW confidence
        for i in range(2):
            steps = [ExecutionStep(step_number=1, action="test", duration_ms=100)]
            await learner.record_execution(
                task_type="confidence_test",
                task_description=f"Test {i}",
                steps=steps,
                status=ExecutionStatus.SUCCESS,
                context={},
                tenant_id="t001",
                agent_id="a001",
            )

        sop = await learner.get_recommended_sop("confidence_test")
        assert sop.confidence == SOPConfidence.LOW

        # Record 1 more success - should be MEDIUM confidence (3 total)
        steps = [ExecutionStep(step_number=1, action="test", duration_ms=100)]
        await learner.record_execution(
            task_type="confidence_test",
            task_description="Test 3",
            steps=steps,
            status=ExecutionStatus.SUCCESS,
            context={},
            tenant_id="t001",
            agent_id="a001",
        )

        sop = await learner.get_recommended_sop("confidence_test")
        assert sop.confidence == SOPConfidence.MEDIUM

        # Record 2 more successes - should be HIGH confidence (5 total)
        for i in range(2):
            steps = [ExecutionStep(step_number=1, action="test", duration_ms=100)]
            await learner.record_execution(
                task_type="confidence_test",
                task_description=f"Test {i + 4}",
                steps=steps,
                status=ExecutionStatus.SUCCESS,
                context={},
                tenant_id="t001",
                agent_id="a001",
            )

        sop = await learner.get_recommended_sop("confidence_test")
        assert sop.confidence == SOPConfidence.HIGH


class TestArabicSupport:
    """Tests for Arabic language support"""

    @pytest.mark.asyncio
    async def test_arabic_task_description(self):
        """Test storing and retrieving Arabic task descriptions"""
        from shared.ai.experience_learning import ExperienceLearner, ExecutionStep, ExecutionStatus

        learner = ExperienceLearner()

        steps = [ExecutionStep(step_number=1, action="check_soil", action_ar="فحص التربة", duration_ms=100)]

        execution = await learner.record_execution(
            task_type="irrigation_advisory",
            task_description="Generate irrigation advice",
            task_description_ar="توليد نصيحة الري",
            steps=steps,
            status=ExecutionStatus.SUCCESS,
            context={"field_id": "F001"},
            tenant_id="t001",
            agent_id="a001",
        )

        assert execution.task_description_ar == "توليد نصيحة الري"
        assert execution.steps[0].action_ar == "فحص التربة"

    @pytest.mark.asyncio
    async def test_arabic_in_guidance(self):
        """Test Arabic text in guidance response"""
        from shared.ai.experience_learning import ExperienceLearner

        learner = ExperienceLearner()
        guidance = await learner.get_execution_guidance("nonexistent")

        assert "message_ar" in guidance
        assert guidance["message_ar"] is not None
