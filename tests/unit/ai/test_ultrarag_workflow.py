"""
Tests for UltraRAG Workflow Engine Module
اختبارات وحدة محرك سير العمل UltraRAG
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from shared.ai.ultrarag.workflow import (
    WorkflowExecutionContext,
    StepExecutionResult,
    WorkflowEngine,
)
from shared.ai.ultrarag.models import (
    WorkflowConfig,
    WorkflowStep,
)


class TestWorkflowExecutionContext:
    """Tests for WorkflowExecutionContext dataclass"""

    def test_create_context(self):
        """Test creating execution context"""
        ctx = WorkflowExecutionContext(workflow_id="wf_001")
        assert ctx.workflow_id == "wf_001"
        assert ctx.variables == {}
        assert ctx.step_results == {}
        assert ctx.current_step is None
        assert ctx.execution_path == []
        assert ctx.errors == []
        assert ctx.start_time == 0.0

    def test_context_with_variables(self):
        """Test context with initial variables"""
        ctx = WorkflowExecutionContext(
            workflow_id="wf_002",
            variables={"query": "test", "top_k": 5},
        )
        assert ctx.variables["query"] == "test"
        assert ctx.variables["top_k"] == 5

    def test_context_tracking(self):
        """Test context tracking during execution"""
        ctx = WorkflowExecutionContext(workflow_id="wf_003")
        ctx.current_step = "step_1"
        ctx.execution_path.append("step_1")
        ctx.step_results["step_1"] = {"output": "result"}

        assert ctx.current_step == "step_1"
        assert len(ctx.execution_path) == 1
        assert "step_1" in ctx.step_results

    def test_context_error_tracking(self):
        """Test error tracking in context"""
        ctx = WorkflowExecutionContext(workflow_id="wf_004")
        ctx.errors.append("Step 1 failed")
        ctx.errors.append("Step 2 failed")

        assert len(ctx.errors) == 2
        assert "Step 1 failed" in ctx.errors


class TestStepExecutionResult:
    """Tests for StepExecutionResult dataclass"""

    def test_create_success_result(self):
        """Test creating a successful step result"""
        result = StepExecutionResult(
            step_id="step_001",
            success=True,
            output={"data": "result"},
            execution_time_ms=50.0,
            next_step="step_002",
        )
        assert result.step_id == "step_001"
        assert result.success is True
        assert result.output["data"] == "result"
        assert result.execution_time_ms == 50.0
        assert result.next_step == "step_002"
        assert result.error is None

    def test_create_failure_result(self):
        """Test creating a failed step result"""
        result = StepExecutionResult(
            step_id="step_002",
            success=False,
            error="Database connection failed",
        )
        assert result.success is False
        assert result.error == "Database connection failed"
        assert result.output is None

    def test_result_defaults(self):
        """Test result default values"""
        result = StepExecutionResult(step_id="step", success=True)
        assert result.output is None
        assert result.error is None
        assert result.execution_time_ms == 0.0
        assert result.next_step is None


class TestWorkflowEngine:
    """Tests for WorkflowEngine"""

    @pytest.fixture
    def mock_rag_pipeline(self):
        """Create mock RAG pipeline"""
        pipeline = MagicMock()
        pipeline.run = AsyncMock()
        return pipeline

    @pytest.fixture
    def engine(self, mock_rag_pipeline):
        """Create workflow engine instance"""
        return WorkflowEngine(rag_pipeline=mock_rag_pipeline)

    @pytest.fixture
    def simple_workflow(self):
        """Create a simple workflow config"""
        return WorkflowConfig(
            id="simple_wf",
            name="Simple Workflow",
            steps=[
                WorkflowStep(
                    id="step1",
                    type="retrieve",
                    name="Retrieve Documents",
                    config={"top_k": 5},
                    next_step="step2",
                ),
                WorkflowStep(
                    id="step2",
                    type="generate",
                    name="Generate Response",
                    config={"max_tokens": 512},
                ),
            ],
            entry_point="step1",
        )

    def test_engine_initialization(self, engine, mock_rag_pipeline):
        """Test engine initialization"""
        assert engine.rag_pipeline == mock_rag_pipeline
        assert len(engine._workflows) == 0
        assert len(engine._step_handlers) > 0

    def test_builtin_handlers_registered(self, engine):
        """Test that built-in handlers are registered"""
        expected_handlers = [
            "retrieve",
            "rerank",
            "generate",
            "condition",
            "loop",
            "transform",
            "filter",
            "parallel",
            "aggregate",
            "call_rag",
        ]
        for handler in expected_handlers:
            assert handler in engine._step_handlers

    def test_builtin_conditions_registered(self, engine):
        """Test that built-in conditions are registered"""
        expected_conditions = [
            "has_results",
            "confidence_above",
            "result_count_above",
            "language_is",
        ]
        for condition in expected_conditions:
            assert condition in engine._condition_evaluators

    def test_register_workflow(self, engine, simple_workflow):
        """Test workflow registration"""
        engine.register_workflow(simple_workflow)
        assert simple_workflow.id in engine._workflows
        assert engine._workflows[simple_workflow.id] == simple_workflow

    def test_register_custom_handler(self, engine):
        """Test registering custom step handler"""

        async def custom_handler(step, ctx):
            return StepExecutionResult(step_id=step.id, success=True)

        engine.register_step_handler("custom", custom_handler)
        assert "custom" in engine._step_handlers

    def test_register_custom_condition(self, engine):
        """Test registering custom condition"""

        def custom_condition(ctx, params):
            return ctx.variables.get("custom_flag", False)

        engine.register_condition("custom_check", custom_condition)
        assert "custom_check" in engine._condition_evaluators

    @pytest.mark.asyncio
    async def test_execute_by_id_not_found(self, engine):
        """Test execution fails for unknown workflow"""
        with pytest.raises(ValueError, match="Workflow not found"):
            await engine.execute("unknown_workflow")

    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self, engine, simple_workflow):
        """Test executing a simple workflow"""
        engine.register_workflow(simple_workflow)

        # Mock the step handlers - handlers return (output, next_step) tuple
        engine._step_handlers["retrieve"] = AsyncMock(return_value=({"results": []}, "step2"))
        engine._step_handlers["generate"] = AsyncMock(return_value=({"answer": "Generated response"}, None))

        result = await engine.execute("simple_wf")

        assert result["success"] is True
        assert result["workflow_id"] == "simple_wf"
        assert len(result["execution_path"]) == 2
        assert "step1" in result["execution_path"]
        assert "step2" in result["execution_path"]

    @pytest.mark.asyncio
    async def test_execute_workflow_with_variables(self, engine):
        """Test executing workflow with initial variables"""
        workflow = WorkflowConfig(
            id="var_wf",
            name="Variable Workflow",
            steps=[
                WorkflowStep(
                    id="start",
                    type="transform",
                    name="Transform",
                    config={},
                ),
            ],
            entry_point="start",
            variables={"default_var": "default"},
        )
        engine.register_workflow(workflow)

        # Handler returns (output, next_step) tuple
        engine._step_handlers["transform"] = AsyncMock(return_value=({"transformed": True}, None))

        result = await engine.execute(
            "var_wf",
            initial_variables={"query": "test query"},
        )

        assert result["success"] is True
        assert result["variables"]["query"] == "test query"
        assert result["variables"]["default_var"] == "default"

    @pytest.mark.asyncio
    async def test_execute_workflow_step_failure(self, engine):
        """Test workflow handles step failure"""
        workflow = WorkflowConfig(
            id="fail_wf",
            name="Failing Workflow",
            steps=[
                WorkflowStep(
                    id="fail_step",
                    type="retrieve",
                    name="Failing Step",
                ),
            ],
            entry_point="fail_step",
        )
        engine.register_workflow(workflow)

        # Handler raises exception to simulate failure
        engine._step_handlers["retrieve"] = AsyncMock(side_effect=ValueError("Database unavailable"))

        result = await engine.execute("fail_wf")

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "Database unavailable" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_execute_workflow_with_branching(self, engine):
        """Test workflow with success/failure branching"""
        workflow = WorkflowConfig(
            id="branch_wf",
            name="Branching Workflow",
            steps=[
                WorkflowStep(
                    id="check",
                    type="condition",
                    name="Check Condition",
                    on_success="success_step",
                    on_failure="failure_step",
                ),
                WorkflowStep(
                    id="success_step",
                    type="generate",
                    name="Success Path",
                ),
                WorkflowStep(
                    id="failure_step",
                    type="generate",
                    name="Failure Path",
                ),
            ],
            entry_point="check",
        )
        engine.register_workflow(workflow)

        # Handlers return (output, next_step) tuple
        # Condition returns next_step to indicate branching
        engine._step_handlers["condition"] = AsyncMock(return_value=({"condition_result": True}, "success_step"))
        engine._step_handlers["generate"] = AsyncMock(return_value=({"answer": "Generated"}, None))

        result = await engine.execute("branch_wf")

        assert "success_step" in result["execution_path"]

    @pytest.mark.asyncio
    async def test_execute_workflow_step_not_found(self, engine):
        """Test workflow fails when step not found"""
        workflow = WorkflowConfig(
            id="invalid_wf",
            name="Invalid Workflow",
            steps=[
                WorkflowStep(
                    id="start",
                    type="retrieve",
                    name="Start",
                    next_step="nonexistent",
                ),
            ],
            entry_point="start",
        )
        engine.register_workflow(workflow)

        # Handler returns (output, next_step) - next_step points to nonexistent step
        engine._step_handlers["retrieve"] = AsyncMock(return_value=({"results": []}, "nonexistent"))

        # execute_workflow catches exceptions and returns error in result
        result = await engine.execute("invalid_wf")

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "Step not found: nonexistent" in result["errors"][0]


class TestBuiltinConditions:
    """Tests for built-in condition evaluators"""

    @pytest.fixture
    def engine(self):
        return WorkflowEngine()

    def test_has_results_true(self, engine):
        """Test has_results condition when results exist"""
        ctx = WorkflowExecutionContext(
            workflow_id="test",
            variables={"results": ["r1", "r2", "r3"]},
        )
        evaluator = engine._condition_evaluators["has_results"]
        assert evaluator(ctx, {}) is True

    def test_has_results_false(self, engine):
        """Test has_results condition when no results"""
        ctx = WorkflowExecutionContext(
            workflow_id="test",
            variables={"results": []},
        )
        evaluator = engine._condition_evaluators["has_results"]
        assert evaluator(ctx, {}) is False

    def test_confidence_above_true(self, engine):
        """Test confidence_above condition when above threshold"""
        ctx = WorkflowExecutionContext(
            workflow_id="test",
            variables={"confidence": 0.8},
        )
        evaluator = engine._condition_evaluators["confidence_above"]
        assert evaluator(ctx, {"threshold": 0.7}) is True

    def test_confidence_above_false(self, engine):
        """Test confidence_above condition when below threshold"""
        ctx = WorkflowExecutionContext(
            workflow_id="test",
            variables={"confidence": 0.4},
        )
        evaluator = engine._condition_evaluators["confidence_above"]
        assert evaluator(ctx, {"threshold": 0.5}) is False

    def test_result_count_above(self, engine):
        """Test result_count_above condition"""
        ctx = WorkflowExecutionContext(
            workflow_id="test",
            variables={"results": ["r1", "r2", "r3"]},
        )
        evaluator = engine._condition_evaluators["result_count_above"]
        assert evaluator(ctx, {"count": 2}) is True
        assert evaluator(ctx, {"count": 5}) is False

    def test_language_is(self, engine):
        """Test language_is condition"""
        ctx = WorkflowExecutionContext(
            workflow_id="test",
            variables={"language": "ar"},
        )
        evaluator = engine._condition_evaluators["language_is"]
        assert evaluator(ctx, {"lang": "ar"}) is True
        assert evaluator(ctx, {"lang": "en"}) is False


class TestWorkflowFromYAML:
    """Tests for creating workflows from YAML"""

    def test_workflow_from_yaml_dict(self):
        """Test creating workflow from YAML dictionary"""
        yaml_dict = {
            "id": "yaml_workflow",
            "name": "YAML-defined Workflow",
            "name_ar": "سير عمل من YAML",
            "description": "Test workflow",
            "version": "1.0.0",
            "steps": [
                {
                    "id": "retrieve",
                    "type": "retrieve",
                    "name": "Retrieve Step",
                    "config": {"top_k": 10},
                    "next_step": "generate",
                },
                {
                    "id": "generate",
                    "type": "generate",
                    "name": "Generate Step",
                    "config": {"max_tokens": 1024},
                },
            ],
            "entry_point": "retrieve",
            "variables": {"language": "en"},
        }

        workflow = WorkflowConfig.from_yaml(yaml_dict)

        assert workflow.id == "yaml_workflow"
        assert workflow.name == "YAML-defined Workflow"
        assert workflow.name_ar == "سير عمل من YAML"
        assert len(workflow.steps) == 2
        assert workflow.steps[0].config["top_k"] == 10
        assert workflow.entry_point == "retrieve"
        assert workflow.variables["language"] == "en"

    def test_workflow_from_yaml_minimal(self):
        """Test creating workflow from minimal YAML"""
        yaml_dict = {
            "name": "Minimal Workflow",
            "steps": [
                {"id": "only", "type": "retrieve", "name": "Only Step"},
            ],
        }

        workflow = WorkflowConfig.from_yaml(yaml_dict)

        assert workflow.name == "Minimal Workflow"
        assert workflow.entry_point == "only"
        assert workflow.version == "1.0.0"
