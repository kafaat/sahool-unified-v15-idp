"""
Tests for Corrective Retrieval Augmented Generation (CRAG)
===========================================================
اختبارات الاسترجاع التصحيحي المعزز للتوليد

Tests for CorrectiveRetrievalEngine, evaluation, refinement, and fallback logic.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.corrective_retrieval import (
    ConfidenceLevel,
    CorrectiveRetrievalEngine,
    CRAGResult,
    RefinedChunk,
    RetrievalAction,
    RetrievalEvaluation,
)


# ─── Enum Tests ──────────────────────────────────────────────────────────────


class TestRetrievalAction:
    """Tests for RetrievalAction enum."""

    @pytest.mark.unit
    def test_values(self):
        assert RetrievalAction.CORRECT == "correct"
        assert RetrievalAction.AMBIGUOUS == "ambiguous"
        assert RetrievalAction.INCORRECT == "incorrect"

    @pytest.mark.unit
    def test_count(self):
        assert len(RetrievalAction) == 3


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""

    @pytest.mark.unit
    def test_values(self):
        assert ConfidenceLevel.HIGH == "high"
        assert ConfidenceLevel.MEDIUM == "medium"
        assert ConfidenceLevel.LOW == "low"


# ─── Data Model Tests ────────────────────────────────────────────────────────


class TestRetrievalEvaluation:
    """Tests for RetrievalEvaluation dataclass."""

    @pytest.mark.unit
    def test_defaults(self):
        evaluation = RetrievalEvaluation(
            action=RetrievalAction.CORRECT,
            confidence=ConfidenceLevel.HIGH,
        )
        assert evaluation.relevance_score == 0.0
        assert evaluation.region_score == 0.0
        assert evaluation.freshness_score == 0.0
        assert evaluation.overall_score == 0.0
        assert evaluation.reasoning == ""
        assert evaluation.reasoning_ar == ""

    @pytest.mark.unit
    def test_custom_values(self):
        evaluation = RetrievalEvaluation(
            action=RetrievalAction.AMBIGUOUS,
            confidence=ConfidenceLevel.MEDIUM,
            relevance_score=0.55,
            overall_score=0.52,
            reasoning="Partial match",
            reasoning_ar="تطابق جزئي",
        )
        assert evaluation.relevance_score == 0.55
        assert evaluation.reasoning_ar == "تطابق جزئي"


class TestRefinedChunk:
    """Tests for RefinedChunk dataclass."""

    @pytest.mark.unit
    def test_defaults(self):
        chunk = RefinedChunk(content="Wheat irrigation schedule")
        assert chunk.content_ar == ""
        assert chunk.relevance_score == 0.0
        assert chunk.source == ""
        assert chunk.collection == ""
        assert chunk.agrovoc_concepts == []
        assert chunk.metadata == {}

    @pytest.mark.unit
    def test_bilingual_chunk(self):
        chunk = RefinedChunk(
            content="Apply 25mm water",
            content_ar="تطبيق 25 ملم ماء",
            relevance_score=0.85,
            collection="crop_water_requirements",
        )
        assert chunk.content_ar == "تطبيق 25 ملم ماء"
        assert chunk.relevance_score == 0.85


class TestCRAGResult:
    """Tests for CRAGResult dataclass."""

    @pytest.mark.unit
    def test_defaults(self):
        result = CRAGResult(
            action_taken=RetrievalAction.CORRECT,
            evaluation=RetrievalEvaluation(
                action=RetrievalAction.CORRECT,
                confidence=ConfidenceLevel.HIGH,
            ),
        )
        assert result.refined_chunks == []
        assert result.fallback_used is False
        assert result.fallback_source == ""
        assert result.total_chunks_input == 0
        assert result.total_chunks_output == 0
        assert result.refinement_ratio == 0.0

    @pytest.mark.unit
    def test_to_dict(self):
        evaluation = RetrievalEvaluation(
            action=RetrievalAction.CORRECT,
            confidence=ConfidenceLevel.HIGH,
            overall_score=0.85,
        )
        result = CRAGResult(
            action_taken=RetrievalAction.CORRECT,
            evaluation=evaluation,
            total_chunks_input=10,
            total_chunks_output=8,
            refinement_ratio=0.8,
        )
        d = result.to_dict()
        assert d["action"] == "correct"
        assert d["confidence"] == "high"
        assert d["overall_score"] == 0.85
        assert d["chunks_in"] == 10
        assert d["chunks_out"] == 8
        assert d["refinement_ratio"] == 0.8
        assert d["fallback_used"] is False


# ─── Engine Tests ────────────────────────────────────────────────────────────


class TestCorrectiveRetrievalEngine:
    """Tests for CorrectiveRetrievalEngine."""

    @pytest.fixture
    def engine(self) -> CorrectiveRetrievalEngine:
        return CorrectiveRetrievalEngine()

    @pytest.fixture
    def high_relevance_chunks(self) -> list[dict]:
        """Chunks highly relevant to wheat irrigation query."""
        return [
            {
                "content": "Wheat requires 450-650mm water per season. Irrigation schedule depends on growth stage. "
                           "During tillering, apply 25mm every 10-14 days. ET values guide precise scheduling.",
                "relevance_score": 0.9,
                "metadata": {"domain": "irrigation", "region": "mena"},
            },
            {
                "content": "Drip irrigation for wheat achieves 85-95% efficiency. Schedule based on soil moisture "
                           "sensors and ET calculations. Water requirement varies by variety and climate.",
                "relevance_score": 0.85,
                "metadata": {"domain": "irrigation"},
            },
            {
                "content": "Wheat irrigation management in arid regions requires careful moisture monitoring. "
                           "Apply water when soil moisture drops below 50% field capacity.",
                "relevance_score": 0.82,
                "metadata": {"domain": "irrigation"},
            },
        ]

    @pytest.fixture
    def low_relevance_chunks(self) -> list[dict]:
        """Chunks not relevant to wheat irrigation query."""
        return [
            {
                "content": "Blockchain technology enables supply chain traceability for agricultural products.",
                "relevance_score": 0.15,
                "metadata": {"domain": "smart_agriculture"},
            },
            {
                "content": "Market prices for cotton rose 5% this quarter due to global demand.",
                "relevance_score": 0.1,
                "metadata": {},
            },
        ]

    @pytest.mark.unit
    def test_engine_initialization(self, engine: CorrectiveRetrievalEngine):
        """Test default engine configuration."""
        assert engine.CORRECT_THRESHOLD == 0.7
        assert engine.AMBIGUOUS_THRESHOLD == 0.4

    @pytest.mark.unit
    def test_custom_thresholds(self):
        """Test engine with custom thresholds."""
        engine = CorrectiveRetrievalEngine(
            correct_threshold=0.8,
            ambiguous_threshold=0.5,
        )
        assert engine.CORRECT_THRESHOLD == 0.8
        assert engine.AMBIGUOUS_THRESHOLD == 0.5

    @pytest.mark.unit
    def test_evaluate_empty_chunks(self, engine: CorrectiveRetrievalEngine):
        """Test evaluation with no chunks returns INCORRECT."""
        result = engine.evaluate_and_refine(query="wheat irrigation", retrieved_chunks=[])
        assert result.action_taken == RetrievalAction.INCORRECT
        assert result.evaluation.confidence == ConfidenceLevel.LOW
        assert result.fallback_used is True
        assert result.total_chunks_input == 0

    @pytest.mark.unit
    def test_evaluate_high_relevance(self, engine: CorrectiveRetrievalEngine, high_relevance_chunks: list[dict]):
        """Test evaluation with relevant chunks processes all input."""
        result = engine.evaluate_and_refine(
            query="How much water does wheat need?",
            retrieved_chunks=high_relevance_chunks,
            query_domain="irrigation",
        )
        assert isinstance(result, CRAGResult)
        assert result.total_chunks_input == 3
        # Engine evaluates quality and takes appropriate action
        assert result.action_taken in (RetrievalAction.CORRECT, RetrievalAction.AMBIGUOUS)

    @pytest.mark.unit
    def test_evaluate_low_relevance(self, engine: CorrectiveRetrievalEngine, low_relevance_chunks: list[dict]):
        """Test evaluation with irrelevant chunks triggers fallback."""
        result = engine.evaluate_and_refine(
            query="wheat irrigation schedule",
            retrieved_chunks=low_relevance_chunks,
            query_domain="irrigation",
        )
        assert result.action_taken in (RetrievalAction.INCORRECT, RetrievalAction.AMBIGUOUS)

    @pytest.mark.unit
    def test_result_has_evaluation(self, engine: CorrectiveRetrievalEngine, high_relevance_chunks: list[dict]):
        """Test result contains proper evaluation."""
        result = engine.evaluate_and_refine(
            query="wheat water requirements",
            retrieved_chunks=high_relevance_chunks,
        )
        assert isinstance(result.evaluation, RetrievalEvaluation)
        assert result.evaluation.action in RetrievalAction
        assert result.evaluation.confidence in ConfidenceLevel

    @pytest.mark.unit
    def test_refinement_ratio_calculated(self, engine: CorrectiveRetrievalEngine, high_relevance_chunks: list[dict]):
        """Test refinement ratio is properly calculated."""
        result = engine.evaluate_and_refine(
            query="irrigation scheduling",
            retrieved_chunks=high_relevance_chunks,
        )
        if result.total_chunks_input > 0:
            expected = result.total_chunks_output / result.total_chunks_input
            assert abs(result.refinement_ratio - expected) < 0.01

    @pytest.mark.unit
    def test_suggest_fallback_collections(self, engine: CorrectiveRetrievalEngine):
        """Test fallback collection suggestions."""
        suggestions = engine.suggest_fallback_collections("irrigation", "irrigation_practices")
        assert len(suggestions) > 0
        assert "irrigation_practices" not in suggestions  # should exclude current

    @pytest.mark.unit
    def test_suggest_fallback_unknown_domain(self, engine: CorrectiveRetrievalEngine):
        """Test fallback for unknown domain returns general."""
        suggestions = engine.suggest_fallback_collections("unknown_domain", "some_collection")
        assert len(suggestions) > 0

    @pytest.mark.unit
    def test_domain_signals_exist(self, engine: CorrectiveRetrievalEngine):
        """Test that domain signals are defined for core domains."""
        assert "crops" in engine._DOMAIN_SIGNALS
        assert "irrigation" in engine._DOMAIN_SIGNALS
        assert "pest_disease" in engine._DOMAIN_SIGNALS
        assert "fertilizer" in engine._DOMAIN_SIGNALS
        assert "soil" in engine._DOMAIN_SIGNALS
        assert "weather" in engine._DOMAIN_SIGNALS

    @pytest.mark.unit
    def test_safety_signals_defined(self, engine: CorrectiveRetrievalEngine):
        """Test safety-critical keywords are defined."""
        assert len(engine._SAFETY_SIGNALS) > 0
        safety_terms = [s.lower() for s in engine._SAFETY_SIGNALS]
        assert any("phi" in s for s in safety_terms)
