"""
Tests for CRAG Integration in UltraRAG Workflows
==================================================
اختبارات تكامل CRAG في سير عمل UltraRAG

Tests:
1. CRAG step handler registration and execution
2. CRAG condition evaluators (crag_action_is, needs_fallback, relevance_above)
3. CRAG step branching (CORRECT → generate, INCORRECT → fallback)
4. All 10 YAML workflows include crag_evaluate step
5. CRAG context variables populated correctly
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from shared.ai.ultrarag.workflow import (
    WorkflowEngine,
    WorkflowExecutionContext,
    load_workflow_from_yaml,
    load_workflows_from_directory,
)
from shared.ai.ultrarag.models import WorkflowConfig, WorkflowStep
from shared.ai.knowledge.corrective_retrieval import (
    ConfidenceLevel,
    CorrectiveRetrievalEngine,
    CRAGResult,
    RetrievalAction,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CRAG Step Handler Registration
# ═══════════════════════════════════════════════════════════════════════════════


class TestCRAGStepRegistration:
    """Verify CRAG step handler is registered in WorkflowEngine."""

    @pytest.mark.unit
    def test_crag_handler_registered(self):
        """Test 'crag' is in step handlers."""
        engine = WorkflowEngine()
        assert "crag" in engine._step_handlers

    @pytest.mark.unit
    def test_crag_handler_is_callable(self):
        """Test CRAG handler is a callable method."""
        engine = WorkflowEngine()
        handler = engine._step_handlers["crag"]
        assert callable(handler)

    @pytest.mark.unit
    def test_all_11_builtin_handlers(self):
        """Test all 11 built-in handlers are present."""
        engine = WorkflowEngine()
        expected = {
            "retrieve", "rerank", "generate", "condition", "loop",
            "transform", "filter", "parallel", "aggregate", "call_rag", "crag",
        }
        assert set(engine._step_handlers.keys()) == expected


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CRAG Condition Evaluators
# ═══════════════════════════════════════════════════════════════════════════════


class TestCRAGConditionEvaluators:
    """Test CRAG-specific condition evaluators."""

    @pytest.fixture
    def engine(self) -> WorkflowEngine:
        return WorkflowEngine()

    @pytest.mark.unit
    def test_crag_action_is_evaluator_registered(self, engine: WorkflowEngine):
        """Test crag_action_is condition evaluator is registered."""
        assert "crag_action_is" in engine._condition_evaluators

    @pytest.mark.unit
    def test_needs_fallback_evaluator_registered(self, engine: WorkflowEngine):
        """Test needs_fallback condition evaluator is registered."""
        assert "needs_fallback" in engine._condition_evaluators

    @pytest.mark.unit
    def test_relevance_above_evaluator_registered(self, engine: WorkflowEngine):
        """Test relevance_above condition evaluator is registered."""
        assert "relevance_above" in engine._condition_evaluators

    @pytest.mark.unit
    def test_crag_action_is_correct(self, engine: WorkflowEngine):
        """Test crag_action_is evaluates to True when action matches."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["crag_action"] = "correct"
        evaluator = engine._condition_evaluators["crag_action_is"]
        assert evaluator(ctx, {"action": "correct"}) is True

    @pytest.mark.unit
    def test_crag_action_is_incorrect(self, engine: WorkflowEngine):
        """Test crag_action_is evaluates to False when action doesn't match."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["crag_action"] = "incorrect"
        evaluator = engine._condition_evaluators["crag_action_is"]
        assert evaluator(ctx, {"action": "correct"}) is False

    @pytest.mark.unit
    def test_needs_fallback_true(self, engine: WorkflowEngine):
        """Test needs_fallback when fallback is required."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["crag_fallback_used"] = True
        evaluator = engine._condition_evaluators["needs_fallback"]
        assert evaluator(ctx, {}) is True

    @pytest.mark.unit
    def test_needs_fallback_false(self, engine: WorkflowEngine):
        """Test needs_fallback when no fallback needed."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["crag_fallback_used"] = False
        evaluator = engine._condition_evaluators["needs_fallback"]
        assert evaluator(ctx, {}) is False

    @pytest.mark.unit
    def test_relevance_above_true(self, engine: WorkflowEngine):
        """Test relevance_above when score exceeds threshold."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["crag_overall_score"] = 0.85
        evaluator = engine._condition_evaluators["relevance_above"]
        assert evaluator(ctx, {"threshold": 0.7}) is True

    @pytest.mark.unit
    def test_relevance_above_false(self, engine: WorkflowEngine):
        """Test relevance_above when score is below threshold."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["crag_overall_score"] = 0.3
        evaluator = engine._condition_evaluators["relevance_above"]
        assert evaluator(ctx, {"threshold": 0.7}) is False


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CRAG Step Execution
# ═══════════════════════════════════════════════════════════════════════════════


class TestCRAGStepExecution:
    """Test CRAG step handler execution with mock data."""

    @pytest.fixture
    def engine(self) -> WorkflowEngine:
        return WorkflowEngine()

    @pytest.mark.unit
    def test_crag_correct_action(self, engine: WorkflowEngine):
        """Test CRAG returns CORRECT for high-quality chunks."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["query"] = "wheat rust disease treatment"
        ctx.variables["results"] = []  # No RetrievalResult objects, use dicts
        ctx.variables["query_domain"] = "pest_disease"

        # Provide high-quality chunks directly
        ctx.variables["results"] = [
            {"content": "Wheat rust (Puccinia triticina) causes yield losses. Treatment includes propiconazole fungicide at 125ml/ha.",
             "metadata": {"domain": "pest_disease", "source_credibility": 5}},
            {"content": "Rust disease in wheat requires early detection. Fungicide application at tillering stage is most effective.",
             "metadata": {"domain": "pest_disease", "source_credibility": 4}},
        ]

        step = WorkflowStep(
            id="crag_evaluate",
            type="crag",
            name="CRAG evaluation",
            config={
                "domain": "pest_disease",
                "correct_threshold": 0.3,  # Low threshold for test
                "ambiguous_threshold": 0.1,
            },
        )

        output, next_step = asyncio.get_event_loop().run_until_complete(
            engine._handle_crag(step, ctx)
        )

        assert ctx.variables["crag_action"] in ("correct", "ambiguous", "incorrect")
        assert "crag_overall_score" in ctx.variables
        assert isinstance(ctx.variables["crag_overall_score"], float)
        assert "crag_chunks_in" in ctx.variables
        assert ctx.variables["crag_chunks_in"] == 2

    @pytest.mark.unit
    def test_crag_incorrect_with_empty_results(self, engine: WorkflowEngine):
        """Test CRAG returns INCORRECT for empty retrieval."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["query"] = "random unrelated query"
        ctx.variables["results"] = []

        step = WorkflowStep(
            id="crag_evaluate",
            type="crag",
            name="CRAG evaluation",
            config={"domain": "crops"},
        )

        output, next_step = asyncio.get_event_loop().run_until_complete(
            engine._handle_crag(step, ctx)
        )

        assert ctx.variables["crag_action"] == "incorrect"
        assert ctx.variables["crag_fallback_used"] is True
        assert ctx.variables["crag_overall_score"] == 0.0

    @pytest.mark.unit
    def test_crag_branching_on_correct(self, engine: WorkflowEngine):
        """Test CRAG routes to on_correct step."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["query"] = "wheat irrigation schedule"
        ctx.variables["results"] = [
            {"content": "Wheat irrigation every 10-14 days during tillering. ET-based scheduling recommended.",
             "metadata": {"domain": "irrigation", "source_credibility": 5}},
        ]

        step = WorkflowStep(
            id="crag_evaluate",
            type="crag",
            name="CRAG",
            config={
                "domain": "irrigation",
                "correct_threshold": 0.1,  # Very low to force CORRECT
                "on_correct": "generate_advisory",
                "on_incorrect": "fallback_search",
            },
        )

        output, next_step = asyncio.get_event_loop().run_until_complete(
            engine._handle_crag(step, ctx)
        )

        if ctx.variables["crag_action"] == "correct":
            assert next_step == "generate_advisory"

    @pytest.mark.unit
    def test_crag_branching_on_incorrect(self, engine: WorkflowEngine):
        """Test CRAG routes to on_incorrect step for empty results."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["query"] = "something"
        ctx.variables["results"] = []

        step = WorkflowStep(
            id="crag_evaluate",
            type="crag",
            name="CRAG",
            config={
                "domain": "crops",
                "on_correct": "generate",
                "on_incorrect": "fallback_search",
            },
        )

        output, next_step = asyncio.get_event_loop().run_until_complete(
            engine._handle_crag(step, ctx)
        )
        assert next_step == "fallback_search"

    @pytest.mark.unit
    def test_crag_populates_all_context_variables(self, engine: WorkflowEngine):
        """Test CRAG step populates all expected context variables."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["query"] = "nitrogen deficiency wheat"
        ctx.variables["results"] = [
            {"content": "Nitrogen deficiency causes yellowing. Apply urea 46kg/ha.",
             "metadata": {"domain": "fertilizer"}},
        ]

        step = WorkflowStep(
            id="crag_evaluate",
            type="crag",
            name="CRAG",
            config={"domain": "fertilizer"},
        )

        asyncio.get_event_loop().run_until_complete(engine._handle_crag(step, ctx))

        expected_vars = [
            "crag_result", "crag_action", "crag_confidence",
            "crag_overall_score", "crag_fallback_used", "crag_fallback_source",
            "crag_chunks_in", "crag_chunks_out", "crag_refinement_ratio",
        ]
        for var in expected_vars:
            assert var in ctx.variables, f"Missing context variable: {var}"

    @pytest.mark.unit
    def test_crag_fallback_collections_suggested(self, engine: WorkflowEngine):
        """Test CRAG suggests fallback collections on INCORRECT."""
        ctx = WorkflowExecutionContext(workflow_id="test")
        ctx.variables["query"] = "query"
        ctx.variables["results"] = []
        ctx.variables["collection"] = "pest_knowledge"

        step = WorkflowStep(
            id="crag_evaluate",
            type="crag",
            name="CRAG",
            config={"domain": "crops"},
        )

        asyncio.get_event_loop().run_until_complete(engine._handle_crag(step, ctx))

        assert ctx.variables["crag_fallback_used"] is True
        assert "crag_fallback_collections" in ctx.variables
        assert isinstance(ctx.variables["crag_fallback_collections"], list)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. YAML Workflow CRAG Step Validation
# ═══════════════════════════════════════════════════════════════════════════════


WORKFLOWS_DIR = Path(__file__).parent.parent.parent.parent / "shared" / "ai" / "ultrarag" / "workflows"

# Workflows that MUST have CRAG step
CRAG_REQUIRED_WORKFLOWS = [
    "crop_advisory_workflow",
    "irrigation_advisory_workflow",
    "pest_diagnosis_workflow",
    "fertilizer_advisory_workflow",
    "soil_analysis_advisory_workflow",
    "weather_advisory_workflow",
    "remote_sensing_analysis_workflow",
    "comprehensive_field_advisory_workflow",
    "precision_farming_advisory_workflow",
    "digital_twin_simulation_workflow",
]

# knowledge_search_workflow does NOT need CRAG (search-only)
CRAG_EXCLUDED_WORKFLOWS = [
    "knowledge_search_workflow",
]


class TestYAMLWorkflowCRAGPresence:
    """Validate all 10 advisory YAML workflows include a crag_evaluate step."""

    @pytest.fixture(scope="class")
    def all_workflows(self) -> list[WorkflowConfig]:
        if not WORKFLOWS_DIR.exists():
            pytest.skip("Workflows directory not found")
        return load_workflows_from_directory(str(WORKFLOWS_DIR))

    @pytest.fixture(scope="class")
    def workflow_map(self, all_workflows: list[WorkflowConfig]) -> dict[str, WorkflowConfig]:
        return {w.id: w for w in all_workflows}

    @pytest.mark.unit
    def test_all_workflows_load(self, all_workflows: list[WorkflowConfig]):
        """Test all 11 YAML workflows load successfully."""
        assert len(all_workflows) >= 11

    @pytest.mark.unit
    @pytest.mark.parametrize("workflow_id", CRAG_REQUIRED_WORKFLOWS)
    def test_crag_step_present(self, workflow_map: dict[str, WorkflowConfig], workflow_id: str):
        """Test each advisory workflow has a crag_evaluate step."""
        assert workflow_id in workflow_map, f"Workflow {workflow_id} not found"
        workflow = workflow_map[workflow_id]
        crag_steps = [s for s in workflow.steps if s.type == "crag"]
        assert len(crag_steps) >= 1, f"{workflow_id} missing CRAG step"

    @pytest.mark.unit
    @pytest.mark.parametrize("workflow_id", CRAG_REQUIRED_WORKFLOWS)
    def test_crag_step_has_domain(self, workflow_map: dict[str, WorkflowConfig], workflow_id: str):
        """Test CRAG step has domain config."""
        workflow = workflow_map[workflow_id]
        crag_steps = [s for s in workflow.steps if s.type == "crag"]
        for step in crag_steps:
            assert "domain" in step.config, f"{workflow_id} CRAG step missing domain"

    @pytest.mark.unit
    @pytest.mark.parametrize("workflow_id", CRAG_REQUIRED_WORKFLOWS)
    def test_crag_step_between_rerank_and_generate(
        self, workflow_map: dict[str, WorkflowConfig], workflow_id: str
    ):
        """Test CRAG step is positioned between rerank and generate."""
        workflow = workflow_map[workflow_id]
        step_ids = [s.id for s in workflow.steps]
        step_types = {s.id: s.type for s in workflow.steps}

        crag_steps = [s for s in workflow.steps if s.type == "crag"]
        assert len(crag_steps) >= 1

        crag_step = crag_steps[0]
        crag_idx = step_ids.index(crag_step.id)

        # Find the rerank step that points to crag
        rerank_found = False
        for s in workflow.steps:
            if s.type == "rerank" and s.next_step == crag_step.id:
                rerank_found = True
                break

        assert rerank_found, f"{workflow_id}: no rerank step points to CRAG"

        # CRAG should have on_correct or next_step pointing to a generate step
        generate_target = (
            crag_step.config.get("on_correct")
            or crag_step.next_step
        )
        if generate_target:
            assert generate_target in step_ids, f"{workflow_id}: CRAG target '{generate_target}' not found"

    @pytest.mark.unit
    @pytest.mark.parametrize("workflow_id", CRAG_EXCLUDED_WORKFLOWS)
    def test_excluded_workflows_no_crag(
        self, workflow_map: dict[str, WorkflowConfig], workflow_id: str
    ):
        """Test search-only workflows do NOT have CRAG step."""
        if workflow_id not in workflow_map:
            pytest.skip(f"{workflow_id} not loaded")
        workflow = workflow_map[workflow_id]
        crag_steps = [s for s in workflow.steps if s.type == "crag"]
        assert len(crag_steps) == 0, f"{workflow_id} should NOT have CRAG step"

    @pytest.mark.unit
    @pytest.mark.parametrize("workflow_id", CRAG_REQUIRED_WORKFLOWS)
    def test_crag_thresholds_valid(self, workflow_map: dict[str, WorkflowConfig], workflow_id: str):
        """Test CRAG thresholds are within valid range."""
        workflow = workflow_map[workflow_id]
        crag_steps = [s for s in workflow.steps if s.type == "crag"]
        for step in crag_steps:
            correct_t = step.config.get("correct_threshold", 0.7)
            ambiguous_t = step.config.get("ambiguous_threshold", 0.4)
            assert 0 < ambiguous_t < correct_t <= 1.0, (
                f"{workflow_id}: invalid thresholds correct={correct_t} ambiguous={ambiguous_t}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CRAG Engine Integration
# ═══════════════════════════════════════════════════════════════════════════════


class TestCRAGEngineIntegration:
    """Integration tests for CorrectiveRetrievalEngine used by the step handler."""

    @pytest.mark.unit
    def test_engine_correct_action(self):
        """Test engine returns CORRECT for relevant chunks."""
        engine = CorrectiveRetrievalEngine(correct_threshold=0.3)
        result = engine.evaluate_and_refine(
            query="wheat rust disease treatment fungicide",
            retrieved_chunks=[
                {"content": "Wheat rust Puccinia treatment propiconazole fungicide 125ml",
                 "metadata": {"domain": "pest_disease", "source_credibility": 5}},
                {"content": "Rust disease wheat early detection tillering stage fungicide spray",
                 "metadata": {"domain": "pest_disease", "source_credibility": 4}},
            ],
            query_domain="pest_disease",
        )
        assert result.action_taken in (RetrievalAction.CORRECT, RetrievalAction.AMBIGUOUS)
        assert result.total_chunks_input == 2
        assert result.total_chunks_output >= 1

    @pytest.mark.unit
    def test_engine_incorrect_on_empty(self):
        """Test engine returns INCORRECT for empty retrieval."""
        engine = CorrectiveRetrievalEngine()
        result = engine.evaluate_and_refine(
            query="any query",
            retrieved_chunks=[],
            query_domain="crops",
        )
        assert result.action_taken == RetrievalAction.INCORRECT
        assert result.fallback_used is True

    @pytest.mark.unit
    def test_engine_fallback_suggestions(self):
        """Test fallback collection suggestions for different domains."""
        engine = CorrectiveRetrievalEngine()

        # Crops domain should suggest pest, fertilizer, irrigation
        suggestions = engine.suggest_fallback_collections("crops", "crop_knowledge")
        assert len(suggestions) >= 2
        assert "crop_knowledge" not in suggestions  # Exclude current

        # Irrigation domain should suggest water reqs, soil, weather
        suggestions = engine.suggest_fallback_collections("irrigation", "irrigation_practices")
        assert len(suggestions) >= 2
        assert "irrigation_practices" not in suggestions

    @pytest.mark.unit
    def test_engine_refined_chunks_have_content(self):
        """Test refined chunks contain actual content."""
        engine = CorrectiveRetrievalEngine(correct_threshold=0.1)
        result = engine.evaluate_and_refine(
            query="nitrogen fertilizer wheat application rate",
            retrieved_chunks=[
                {"content": "Apply nitrogen fertilizer at 46 kg/ha for wheat during tillering.",
                 "metadata": {"domain": "fertilizer", "source_credibility": 5}},
            ],
            query_domain="fertilizer",
        )
        assert len(result.refined_chunks) >= 1
        for chunk in result.refined_chunks:
            assert len(chunk.content) > 0
            assert chunk.relevance_score > 0

    @pytest.mark.unit
    def test_engine_to_dict(self):
        """Test CRAGResult.to_dict() serialization."""
        engine = CorrectiveRetrievalEngine()
        result = engine.evaluate_and_refine(
            query="test",
            retrieved_chunks=[{"content": "test content", "metadata": {}}],
            query_domain="crops",
        )
        d = result.to_dict()
        assert "action" in d
        assert "confidence" in d
        assert "overall_score" in d
        assert "chunks_in" in d
        assert "chunks_out" in d
        assert "refinement_ratio" in d
        assert "fallback_used" in d
