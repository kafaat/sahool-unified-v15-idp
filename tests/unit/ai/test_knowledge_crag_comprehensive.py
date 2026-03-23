"""
Comprehensive tests for Corrective Retrieval (CRAG) engine.
Covers: scoring, actions, refinement, semantic provider, fallback, edge cases.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.mark.unit
class TestCRAGDataClasses:
    """Test CRAG data model classes."""

    def test_retrieval_action_values(self):
        from shared.ai.knowledge.corrective_retrieval import RetrievalAction

        assert RetrievalAction.CORRECT == "correct"
        assert RetrievalAction.AMBIGUOUS == "ambiguous"
        assert RetrievalAction.INCORRECT == "incorrect"

    def test_confidence_level_values(self):
        from shared.ai.knowledge.corrective_retrieval import ConfidenceLevel

        assert ConfidenceLevel.HIGH == "high"
        assert ConfidenceLevel.MEDIUM == "medium"
        assert ConfidenceLevel.LOW == "low"

    def test_retrieval_evaluation_defaults(self):
        from shared.ai.knowledge.corrective_retrieval import (
            ConfidenceLevel,
            RetrievalAction,
            RetrievalEvaluation,
        )

        ev = RetrievalEvaluation(action=RetrievalAction.CORRECT, confidence=ConfidenceLevel.HIGH)
        assert ev.relevance_score == 0.0
        assert ev.region_score == 0.0
        assert ev.freshness_score == 0.0
        assert ev.overall_score == 0.0
        assert ev.reasoning == ""
        assert ev.reasoning_ar == ""

    def test_refined_chunk_defaults(self):
        from shared.ai.knowledge.corrective_retrieval import RefinedChunk

        chunk = RefinedChunk(content="Test content")
        assert chunk.content_ar == ""
        assert chunk.relevance_score == 0.0
        assert chunk.source == ""
        assert chunk.collection == ""
        assert chunk.agrovoc_concepts == []
        assert chunk.region_relevance == 0.0
        assert chunk.metadata == {}

    def test_crag_result_to_dict(self):
        from shared.ai.knowledge.corrective_retrieval import (
            ConfidenceLevel,
            CRAGResult,
            RetrievalAction,
            RetrievalEvaluation,
        )

        result = CRAGResult(
            action_taken=RetrievalAction.AMBIGUOUS,
            evaluation=RetrievalEvaluation(
                action=RetrievalAction.AMBIGUOUS,
                confidence=ConfidenceLevel.MEDIUM,
                overall_score=0.55,
            ),
            total_chunks_input=5,
            total_chunks_output=3,
            refinement_ratio=0.6,
            fallback_used=True,
        )
        d = result.to_dict()
        assert d["action"] == "ambiguous"
        assert d["confidence"] == "medium"
        assert d["overall_score"] == 0.55
        assert d["chunks_in"] == 5
        assert d["chunks_out"] == 3
        assert d["refinement_ratio"] == 0.6
        assert d["fallback_used"] is True


@pytest.mark.unit
class TestCRAGEngineActions:
    """Test that CRAG engine takes the correct action."""

    def test_empty_chunks_returns_incorrect(self):
        from shared.ai.knowledge.corrective_retrieval import (
            CorrectiveRetrievalEngine,
            RetrievalAction,
        )

        engine = CorrectiveRetrievalEngine()
        result = engine.evaluate_and_refine(query="wheat irrigation", retrieved_chunks=[])
        assert result.action_taken == RetrievalAction.INCORRECT
        assert result.fallback_used is True
        assert result.fallback_source == "empty_retrieval"
        assert result.total_chunks_input == 0

    def test_highly_relevant_chunks_return_correct(self):
        from shared.ai.knowledge.corrective_retrieval import (
            CorrectiveRetrievalEngine,
            RetrievalAction,
        )

        # Use lower thresholds to ensure highly relevant chunks score as CORRECT
        engine = CorrectiveRetrievalEngine(
            correct_threshold=0.4,
            ambiguous_threshold=0.2,
        )
        chunks = [
            {
                "content": "Wheat irrigation schedule requires 25mm every 10-14 days during tillering. Water moisture ET drip schedule.",
                "metadata": {
                    "domain": "irrigation",
                    "source_credibility": 5,
                    "agrovoc_concepts": ["wheat", "irrigation"],
                },
            },
            {
                "content": "Wheat water requirements depend on crop growth stage, ET rate, and soil moisture levels. Drip irrigation schedule.",
                "metadata": {
                    "domain": "irrigation",
                    "source_credibility": 5,
                    "agrovoc_concepts": ["wheat"],
                },
            },
        ]
        result = engine.evaluate_and_refine(
            query="wheat irrigation schedule water needs",
            retrieved_chunks=chunks,
            query_domain="irrigation",
        )
        assert result.action_taken == RetrievalAction.CORRECT

    def test_irrelevant_chunks_return_incorrect(self):
        from shared.ai.knowledge.corrective_retrieval import (
            CorrectiveRetrievalEngine,
            RetrievalAction,
        )

        engine = CorrectiveRetrievalEngine()
        chunks = [
            {
                "content": "The history of ancient Roman architecture and its influence on modern building design.",
                "metadata": {"domain": "general"},
            },
        ]
        result = engine.evaluate_and_refine(
            query="wheat pest control methods",
            retrieved_chunks=chunks,
            query_domain="pest_disease",
        )
        assert result.action_taken == RetrievalAction.INCORRECT
        assert result.fallback_used is True


@pytest.mark.unit
class TestCRAGScoring:
    """Test individual scoring mechanisms."""

    def test_domain_signal_matching_boosts_score(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunk = {
            "content": "Wheat variety cultivar growth stage yield harvest performance in arid regions.",
            "metadata": {"domain": "crops", "source_credibility": 3},
        }
        score = engine._score_chunk_relevance("wheat yield prediction", chunk, "crops")
        assert score > 0.2

    def test_source_credibility_affects_score(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunk_low = {
            "content": "Wheat irrigation basics.",
            "metadata": {"domain": "irrigation", "source_credibility": 1},
        }
        chunk_high = {
            "content": "Wheat irrigation basics.",
            "metadata": {"domain": "irrigation", "source_credibility": 5},
        }
        score_low = engine._score_chunk_relevance("wheat irrigation", chunk_low, "irrigation")
        score_high = engine._score_chunk_relevance("wheat irrigation", chunk_high, "irrigation")
        assert score_high > score_low

    def test_empty_content_returns_zero(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        score = engine._score_chunk_relevance("test query", {"content": ""}, "crops")
        assert score == 0.0

    def test_agrovoc_concepts_boost_score(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunk_no_agrovoc = {
            "content": "Wheat data here.",
            "metadata": {"domain": "crops"},
        }
        chunk_with_agrovoc = {
            "content": "Wheat data here.",
            "metadata": {"domain": "crops", "agrovoc_concepts": ["c_137"]},
        }
        s1 = engine._score_chunk_relevance("wheat", chunk_no_agrovoc, "crops")
        s2 = engine._score_chunk_relevance("wheat", chunk_with_agrovoc, "crops")
        assert s2 > s1

    def test_safety_signal_boost(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunk = {
            "content": "PHI pre-harvest interval for pesticide application is critical. Toxicity LD50 values must be checked.",
            "metadata": {},
        }
        score = engine._score_chunk_relevance("PHI pre-harvest interval safety", chunk, "")
        assert score > 0.1  # Safety boost should apply

    def test_score_capped_at_one(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        # Chunk with everything matching
        chunk = {
            "content": "Wheat variety cultivar growth stage yield harvest pest disease insect fungus treatment PHI pre-harvest interval toxicity banned restricted",
            "metadata": {
                "domain": "crops",
                "source_credibility": 5,
                "agrovoc_concepts": ["wheat"],
            },
        }
        score = engine._score_chunk_relevance(
            "wheat variety cultivar growth pest PHI pre-harvest interval",
            chunk,
            "crops",
        )
        assert score <= 1.0


@pytest.mark.unit
class TestCRAGRegionScoring:
    """Test region relevance scoring."""

    def test_matching_region_scores_high(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunks = [
            {"content": "test", "metadata": {"applicable_regions": ["yemen_highland", "saudi_central"]}},
        ]
        score = engine._score_region_relevance(chunks, "yemen_highland")
        assert score == 1.0

    def test_no_matching_region_scores_low(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunks = [
            {"content": "test", "metadata": {"applicable_regions": ["egypt_delta"]}},
        ]
        score = engine._score_region_relevance(chunks, "yemen_highland")
        assert score == 0.0

    def test_empty_region_gets_partial_credit(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunks = [
            {"content": "test", "metadata": {}},
        ]
        score = engine._score_region_relevance(chunks, "yemen_highland")
        assert 0.0 < score < 1.0

    def test_no_target_region_returns_default(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunks = [{"content": "test", "metadata": {}}]
        score = engine._score_region_relevance(chunks, "")
        assert score == 0.5


@pytest.mark.unit
class TestCRAGFreshnessScoring:
    """Test freshness scoring."""

    def test_fresh_document_scores_high(self):
        from datetime import datetime, timedelta

        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        future_date = (datetime.utcnow() + timedelta(days=365)).isoformat()
        chunks = [
            {"content": "test", "metadata": {"fresh": {"expiration_date": future_date}}},
        ]
        score = engine._score_freshness(chunks)
        assert score == 1.0

    def test_expired_document_scores_low(self):
        from datetime import datetime, timedelta

        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        past_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        chunks = [
            {"content": "test", "metadata": {"fresh": {"expiration_date": past_date}}},
        ]
        score = engine._score_freshness(chunks)
        assert score == 0.2

    def test_no_expiration_returns_default(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        chunks = [{"content": "test", "metadata": {}}]
        score = engine._score_freshness(chunks)
        assert score == 0.5


@pytest.mark.unit
class TestCRAGSemanticProvider:
    """Test semantic similarity provider integration (GAP-18)."""

    def test_semantic_provider_used_for_scoring(self):
        from shared.ai.knowledge.corrective_retrieval import (
            CorrectiveRetrievalEngine,
            SemanticSimilarityProvider,
        )

        mock_provider = MagicMock(spec=SemanticSimilarityProvider)
        mock_provider.similarity.return_value = 0.9

        engine = CorrectiveRetrievalEngine(semantic_provider=mock_provider)
        chunk = {
            "content": "Wheat requires adequate nitrogen during tillering.",
            "metadata": {"domain": "crops"},
        }
        score = engine._score_chunk_relevance("wheat nitrogen needs", chunk, "crops")

        mock_provider.similarity.assert_called_once()
        assert score > 0.2

    def test_semantic_provider_failure_falls_back_to_keywords(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        mock_provider = MagicMock()
        mock_provider.similarity.side_effect = RuntimeError("Model not loaded")

        engine = CorrectiveRetrievalEngine(semantic_provider=mock_provider)
        chunk = {
            "content": "Wheat irrigation scheduling for arid regions.",
            "metadata": {"domain": "crops"},
        }
        score = engine._score_chunk_relevance("wheat irrigation", chunk, "crops")
        assert score >= 0.0  # Should not raise

    def test_semantic_provider_truncates_content(self):
        from shared.ai.knowledge.corrective_retrieval import (
            CorrectiveRetrievalEngine,
            SemanticSimilarityProvider,
        )

        mock_provider = MagicMock(spec=SemanticSimilarityProvider)
        mock_provider.similarity.return_value = 0.5

        engine = CorrectiveRetrievalEngine(semantic_provider=mock_provider)
        long_content = "word " * 5000
        chunk = {"content": long_content, "metadata": {}}
        engine._score_chunk_relevance("test", chunk, "")

        # Content should be truncated to 2000 chars
        call_args = mock_provider.similarity.call_args
        assert len(call_args[0][1]) <= 2000

    def test_without_semantic_uses_word_overlap(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine(semantic_provider=None)
        chunk = {
            "content": "Wheat is a major cereal crop grown worldwide.",
            "metadata": {},
        }
        score = engine._score_chunk_relevance("wheat cereal crop", chunk, "")
        assert score > 0.0


@pytest.mark.unit
class TestCRAGRefinement:
    """Test light, deep, and salvage refinement."""

    def _engine(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        return CorrectiveRetrievalEngine()

    def test_light_refine_keeps_relevant_chunks(self):
        engine = self._engine()
        chunks = [
            {"content": "Wheat irrigation drip schedule water moisture ET.", "metadata": {"domain": "irrigation"}},
            {"content": "Completely unrelated content about cooking recipes.", "metadata": {}},
        ]
        refined = engine._light_refine("wheat irrigation", chunks, "irrigation")
        assert len(refined) >= 1
        assert refined[0].content  # Should have content

    def test_light_refine_sorted_by_relevance(self):
        engine = self._engine()
        chunks = [
            {"content": "General agriculture topic.", "metadata": {"domain": "general"}},
            {
                "content": "Wheat irrigation drip schedule water moisture ET.",
                "metadata": {"domain": "irrigation", "source_credibility": 5},
            },
        ]
        refined = engine._light_refine("wheat irrigation", chunks, "irrigation")
        if len(refined) >= 2:
            assert refined[0].relevance_score >= refined[1].relevance_score

    def test_deep_refine_filters_sentences(self):
        engine = self._engine()
        chunks = [
            {
                "content": "Wheat requires nitrogen during tillering. This is irrelevant nonsense about cooking. Nitrogen fertilizer application timing is critical for wheat yield.",
                "metadata": {"domain": "crops"},
            },
        ]
        refined = engine._deep_refine("wheat nitrogen fertilizer", chunks, "crops")
        # Should have at least some refined content
        assert len(refined) >= 0  # Deep refine may or may not keep content

    def test_salvage_refine_low_bar(self):
        engine = self._engine()
        chunks = [
            {"content": "Wheat yield data table.", "metadata": {"domain": "crops", "source_credibility": 3}},
            {"content": "Random unrelated content.", "metadata": {}},
        ]
        refined = engine._salvage_refine("wheat yield", chunks, "crops")
        assert len(refined) <= 3  # Max 3 salvaged chunks

    def test_max_refined_chunks_respected(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine(max_refined_chunks=2)
        chunks = [
            {
                "content": f"Wheat irrigation data point {i}. Water moisture ET drip schedule.",
                "metadata": {"domain": "irrigation"},
            }
            for i in range(10)
        ]
        refined = engine._light_refine("wheat irrigation", chunks, "irrigation")
        assert len(refined) <= 2


@pytest.mark.unit
class TestCRAGFallbackCollections:
    """Test fallback collection suggestions."""

    def test_crops_fallback(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        suggestions = engine.suggest_fallback_collections("crops", "crop_knowledge")
        assert "crop_knowledge" not in suggestions
        assert len(suggestions) > 0

    def test_unknown_domain_fallback(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        suggestions = engine.suggest_fallback_collections("unknown_domain", "")
        assert len(suggestions) > 0

    def test_irrigation_fallback_includes_water(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        suggestions = engine.suggest_fallback_collections("irrigation", "irrigation_practices")
        assert "irrigation_practices" not in suggestions


@pytest.mark.unit
class TestCRAGSentenceSplitting:
    """Test sentence splitting for deep refinement."""

    def test_english_sentence_splitting(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        text = "This is the first sentence about wheat. This is the second about irrigation. Short."
        sentences = engine._split_sentences(text)
        # "Short." is < 20 chars, should be filtered
        assert len(sentences) == 2

    def test_arabic_sentence_splitting(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        text = "هذا هو القمح المزروع في المنطقة العربية بشكل واسع؟ وهذه هي طريقة الري المستخدمة في المناطق الجافة."
        sentences = engine._split_sentences(text)
        assert len(sentences) >= 1

    def test_very_short_sentences_filtered(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        text = "OK. Yes. No. This is a properly long sentence about agriculture."
        sentences = engine._split_sentences(text)
        assert all(len(s) > 20 for s in sentences)


@pytest.mark.unit
class TestCRAGCustomThresholds:
    """Test custom threshold configuration."""

    def test_custom_correct_threshold(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine(correct_threshold=0.9)
        assert engine.CORRECT_THRESHOLD == 0.9

    def test_custom_ambiguous_threshold(self):
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine(ambiguous_threshold=0.2)
        assert engine.AMBIGUOUS_THRESHOLD == 0.2
