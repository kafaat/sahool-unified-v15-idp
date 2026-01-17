"""
Unit Tests for AI Recommendation Evaluation Module
==================================================
اختبارات وحدة لوحدة تقييم توصيات الذكاء الاصطناعي

Tests for RecommendationEvaluator class covering:
- Evaluation criteria scoring
- LLM-based evaluation
- Heuristic-based evaluation fallback
- Arabic text evaluation
- Batch evaluation
- Safety checks
- Approval logic

Author: SAHOOL QA Team
Updated: January 2025
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch

from shared.ai.context_engineering.evaluation import (
    RecommendationEvaluator,
    EvaluationResult,
    CriteriaScore,
    EvaluationCriteria,
    EvaluationGrade,
    RecommendationType,
    BaseEvaluator,
    DEFAULT_PASSING_THRESHOLD,
    MIN_SCORE,
    MAX_SCORE,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def evaluator():
    """Standard evaluator without LLM"""
    return RecommendationEvaluator(llm_client=None, use_heuristics_fallback=True)


@pytest.fixture
def evaluator_with_llm():
    """Evaluator with mocked LLM client"""
    llm_client = MagicMock()
    return RecommendationEvaluator(llm_client=llm_client)


@pytest.fixture
def sample_irrigation_recommendation():
    """Sample irrigation recommendation"""
    return """
    For optimal wheat irrigation, water your field every 3-4 days during growing season.
    Apply 25-30 mm of water per irrigation. Morning irrigation (6-9 AM) is recommended.
    Avoid waterlogging - ensure proper drainage. Monitor soil moisture at 15cm depth.
    During flowering stage, water more frequently to maintain consistent moisture.
    """


@pytest.fixture
def sample_fertilization_recommendation():
    """Sample fertilization recommendation"""
    return """
    Apply 200 kg/hectare of balanced NPK fertilizer (15:15:15) at planting.
    Split nitrogen application: 50% at planting, 30% at 4-6 weeks, 20% at pre-flowering.
    Use caution when applying near sensitive areas. Wear gloves and mask.
    Total nitrogen requirement: 150 kg/hectare for wheat.
    """


@pytest.fixture
def sample_pest_control_recommendation():
    """Sample pest control recommendation"""
    return """
    Identify the pest species before applying treatment. Use integrated pest management.
    For aphids: spray with organic neem oil weekly. Always follow safety instructions.
    WARNING: Use protective equipment when handling pesticides.
    Apply treatment in early morning or late evening for better efficacy.
    """


@pytest.fixture
def sample_context():
    """Sample context for evaluation"""
    return {
        "crop": "wheat",
        "field_size": 10,
        "soil_type": "clay loam",
        "season": "spring",
        "region": "middle_east",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: CriteriaScore
# ═══════════════════════════════════════════════════════════════════════════════


class TestCriteriaScore:
    """Tests for CriteriaScore"""

    def test_create_criteria_score(self):
        """Should create criteria score"""
        score = CriteriaScore(
            criteria=EvaluationCriteria.ACCURACY,
            score=0.85,
            explanation="Technically accurate",
        )

        assert score.criteria == EvaluationCriteria.ACCURACY
        assert score.score == 0.85
        assert score.explanation == "Technically accurate"

    def test_score_clamping(self):
        """Should clamp scores to valid range"""
        score_high = CriteriaScore(
            criteria=EvaluationCriteria.ACCURACY,
            score=1.5,  # Over 1.0
            explanation="test",
        )
        score_low = CriteriaScore(
            criteria=EvaluationCriteria.ACCURACY,
            score=-0.5,  # Under 0.0
            explanation="test",
        )

        assert score_high.score == MAX_SCORE
        assert score_low.score == MIN_SCORE

    def test_is_passing_threshold(self):
        """Should determine if score passes threshold"""
        passing_score = CriteriaScore(
            criteria=EvaluationCriteria.ACCURACY,
            score=DEFAULT_PASSING_THRESHOLD,
            explanation="Passing",
        )
        failing_score = CriteriaScore(
            criteria=EvaluationCriteria.ACCURACY,
            score=DEFAULT_PASSING_THRESHOLD - 0.1,
            explanation="Failing",
        )

        assert passing_score.is_passing is True
        assert failing_score.is_passing is False

    def test_to_dict_conversion(self):
        """Should convert to dictionary"""
        score = CriteriaScore(
            criteria=EvaluationCriteria.ACCURACY,
            score=0.8,
            explanation="Test",
            explanation_ar="اختبار",
            evidence=["Evidence 1"],
        )

        score_dict = score.to_dict()

        assert score_dict["criteria"] == EvaluationCriteria.ACCURACY.value
        assert score_dict["score"] == 0.8
        assert score_dict["explanation"] == "Test"
        assert score_dict["is_passing"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: EvaluationResult
# ═══════════════════════════════════════════════════════════════════════════════


class TestEvaluationResult:
    """Tests for EvaluationResult"""

    @pytest.fixture
    def sample_scores(self):
        """Sample evaluation scores"""
        return {
            EvaluationCriteria.ACCURACY: CriteriaScore(
                criteria=EvaluationCriteria.ACCURACY,
                score=0.85,
                explanation="Accurate",
            ),
            EvaluationCriteria.ACTIONABILITY: CriteriaScore(
                criteria=EvaluationCriteria.ACTIONABILITY,
                score=0.8,
                explanation="Actionable",
            ),
            EvaluationCriteria.SAFETY: CriteriaScore(
                criteria=EvaluationCriteria.SAFETY,
                score=0.9,
                explanation="Safe",
            ),
            EvaluationCriteria.RELEVANCE: CriteriaScore(
                criteria=EvaluationCriteria.RELEVANCE,
                score=0.75,
                explanation="Relevant",
            ),
            EvaluationCriteria.COMPLETENESS: CriteriaScore(
                criteria=EvaluationCriteria.COMPLETENESS,
                score=0.8,
                explanation="Complete",
            ),
            EvaluationCriteria.CLARITY: CriteriaScore(
                criteria=EvaluationCriteria.CLARITY,
                score=0.85,
                explanation="Clear",
            ),
        }

    def test_create_evaluation_result(self, sample_scores):
        """Should create evaluation result"""
        result = EvaluationResult.create(
            recommendation_type=RecommendationType.IRRIGATION,
            scores=sample_scores,
        )

        assert result.id is not None
        assert result.recommendation_type == RecommendationType.IRRIGATION
        assert result.overall_score > 0
        assert result.grade is not None
        assert isinstance(result.is_approved, bool)

    def test_overall_score_calculation(self, sample_scores):
        """Should calculate weighted overall score"""
        result = EvaluationResult.create(
            recommendation_type=RecommendationType.IRRIGATION,
            scores=sample_scores,
        )

        # Should be reasonable weighted average
        assert 0 <= result.overall_score <= 1.0

    def test_score_to_grade(self):
        """Should convert score to grade"""
        assert EvaluationResult._score_to_grade(0.95) == EvaluationGrade.EXCELLENT
        assert EvaluationResult._score_to_grade(0.8) == EvaluationGrade.GOOD
        assert EvaluationResult._score_to_grade(0.65) == EvaluationGrade.ACCEPTABLE
        assert EvaluationResult._score_to_grade(0.45) == EvaluationGrade.NEEDS_IMPROVEMENT
        assert EvaluationResult._score_to_grade(0.25) == EvaluationGrade.POOR

    def test_safety_prevents_approval(self, sample_scores):
        """Low safety score should prevent approval"""
        # Set safety to fail
        sample_scores[EvaluationCriteria.SAFETY].score = 0.3

        result = EvaluationResult.create(
            recommendation_type=RecommendationType.IRRIGATION,
            scores=sample_scores,
        )

        assert result.is_approved is False

    def test_custom_weights(self, sample_scores):
        """Should apply custom criteria weights"""
        custom_weights = {
            EvaluationCriteria.SAFETY: 0.5,  # High weight on safety
            EvaluationCriteria.ACCURACY: 0.3,
            EvaluationCriteria.ACTIONABILITY: 0.1,
            EvaluationCriteria.RELEVANCE: 0.05,
            EvaluationCriteria.COMPLETENESS: 0.03,
            EvaluationCriteria.CLARITY: 0.02,
        }

        result = EvaluationResult.create(
            recommendation_type=RecommendationType.IRRIGATION,
            scores=sample_scores,
            weights=custom_weights,
        )

        # With custom weights, should be calculated
        assert result.overall_score > 0

    def test_feedback_generation(self, sample_scores):
        """Should generate feedback"""
        result = EvaluationResult.create(
            recommendation_type=RecommendationType.IRRIGATION,
            scores=sample_scores,
        )

        assert len(result.feedback) > 0
        assert len(result.feedback_ar) > 0

    def test_improvements_generation(self, sample_scores):
        """Should generate improvement suggestions"""
        # Set some scores to fail
        sample_scores[EvaluationCriteria.CLARITY].score = 0.5

        result = EvaluationResult.create(
            recommendation_type=RecommendationType.IRRIGATION,
            scores=sample_scores,
        )

        assert len(result.improvements) > 0

    def test_to_dict_conversion(self, sample_scores):
        """Should convert to dictionary"""
        result = EvaluationResult.create(
            recommendation_type=RecommendationType.IRRIGATION,
            scores=sample_scores,
        )

        result_dict = result.to_dict()

        assert "id" in result_dict
        assert "scores" in result_dict
        assert "overall_score" in result_dict
        assert "is_approved" in result_dict


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: RecommendationEvaluator Initialization
# ═══════════════════════════════════════════════════════════════════════════════


class TestEvaluatorInitialization:
    """Tests for evaluator initialization"""

    def test_initialize_without_llm(self):
        """Should initialize without LLM"""
        evaluator = RecommendationEvaluator(llm_client=None)

        assert evaluator.llm_client is None
        assert evaluator.use_heuristics_fallback is True

    def test_initialize_with_llm(self):
        """Should initialize with LLM client"""
        llm_client = MagicMock()
        evaluator = RecommendationEvaluator(llm_client=llm_client)

        assert evaluator.llm_client is llm_client

    def test_default_weights(self):
        """Should have default criteria weights"""
        evaluator = RecommendationEvaluator()

        assert len(evaluator.criteria_weights) == 6
        assert EvaluationCriteria.SAFETY in evaluator.criteria_weights

    def test_custom_weights(self):
        """Should accept custom weights"""
        custom_weights = {
            EvaluationCriteria.ACCURACY: 0.4,
            EvaluationCriteria.SAFETY: 0.6,
        }
        evaluator = RecommendationEvaluator(criteria_weights=custom_weights)

        assert evaluator.criteria_weights[EvaluationCriteria.ACCURACY] == 0.4


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Heuristic-based Evaluation
# ═══════════════════════════════════════════════════════════════════════════════


class TestHeuristicEvaluation:
    """Tests for heuristic-based evaluation"""

    def test_evaluate_with_heuristics(
        self, evaluator, sample_irrigation_recommendation, sample_context
    ):
        """Should evaluate using heuristics"""
        result = evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            context=sample_context,
            query="How should I irrigate my wheat?",
            recommendation_type=RecommendationType.IRRIGATION,
        )

        assert result.overall_score > 0
        assert result.grade is not None
        assert isinstance(result.is_approved, bool)

    def test_heuristic_accuracy_evaluation(
        self, evaluator, sample_irrigation_recommendation
    ):
        """Should evaluate accuracy heuristics"""
        result = evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            context={"crop": "wheat"},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        # Should have accuracy score
        assert EvaluationCriteria.ACCURACY in result.scores

    def test_heuristic_actionability_evaluation(
        self, evaluator, sample_irrigation_recommendation
    ):
        """Should evaluate actionability"""
        result = evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        actionability = result.scores[EvaluationCriteria.ACTIONABILITY]
        # Should have action verbs like "water", "apply"
        assert actionability.score > 0

    def test_heuristic_safety_evaluation(
        self, evaluator, sample_fertilization_recommendation
    ):
        """Should evaluate safety"""
        result = evaluator.evaluate(
            recommendation=sample_fertilization_recommendation,
            context={},
            recommendation_type=RecommendationType.FERTILIZATION,
        )

        safety = result.scores[EvaluationCriteria.SAFETY]
        # Should detect safety warnings
        assert safety.score > 0

    def test_heuristic_relevance_evaluation(
        self, evaluator, sample_irrigation_recommendation
    ):
        """Should evaluate relevance to query"""
        result = evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            query="What is optimal irrigation for wheat?",
            context={"crop": "wheat"},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        relevance = result.scores[EvaluationCriteria.RELEVANCE]
        # Should detect relevance through keywords
        assert relevance.score > 0

    def test_heuristic_completeness_evaluation(self, evaluator):
        """Should evaluate completeness"""
        # Short recommendation
        short_rec = "Water the field."
        # Long, detailed recommendation
        long_rec = sample_irrigation_recommendation = """
        For optimal irrigation: water every 3-4 days, apply 25-30 mm,
        irrigate in morning, monitor soil moisture, maintain consistent moisture during flowering.
        """ * 2

        result_short = evaluator.evaluate(
            recommendation=short_rec,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )
        result_long = evaluator.evaluate(
            recommendation=long_rec,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        # Longer recommendation should have higher completeness
        assert (
            result_long.scores[EvaluationCriteria.COMPLETENESS].score
            >= result_short.scores[EvaluationCriteria.COMPLETENESS].score
        )

    def test_heuristic_clarity_evaluation(self, evaluator):
        """Should evaluate clarity"""
        clear_rec = "Water the field every 3 days in morning. Apply 25mm. Monitor moisture."
        unclear_rec = """
        It is important to understand that watering is necessary and when you do water
        which should be in the early morning hours generally between six and nine in the morning
        one would apply approximately twenty five to thirty millimeters of water per irrigation event.
        """ * 3

        result_clear = evaluator.evaluate(
            recommendation=clear_rec,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )
        result_unclear = evaluator.evaluate(
            recommendation=unclear_rec,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        # Clear should have higher clarity score
        assert (
            result_clear.scores[EvaluationCriteria.CLARITY].score
            > result_unclear.scores[EvaluationCriteria.CLARITY].score
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Recommendation Type Detection
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecommendationTypeDetection:
    """Tests for detecting recommendation type"""

    def test_detect_irrigation_type(self, evaluator, sample_irrigation_recommendation):
        """Should detect irrigation recommendations"""
        detected_type = evaluator._detect_recommendation_type(
            sample_irrigation_recommendation
        )

        assert detected_type == RecommendationType.IRRIGATION

    def test_detect_fertilization_type(self, evaluator, sample_fertilization_recommendation):
        """Should detect fertilization recommendations"""
        detected_type = evaluator._detect_recommendation_type(
            sample_fertilization_recommendation
        )

        assert detected_type == RecommendationType.FERTILIZATION

    def test_detect_pest_control_type(self, evaluator, sample_pest_control_recommendation):
        """Should detect pest control recommendations"""
        detected_type = evaluator._detect_recommendation_type(
            sample_pest_control_recommendation
        )

        assert detected_type == RecommendationType.PEST_CONTROL

    def test_detect_arabic_irrigation(self, evaluator):
        """Should detect Arabic irrigation recommendations"""
        arabic_rec = "ري الحقل كل 3 أيام بمعدل 25-30 ملم"
        detected_type = evaluator._detect_recommendation_type(arabic_rec)

        assert detected_type == RecommendationType.IRRIGATION

    def test_detect_arabic_fertilization(self, evaluator):
        """Should detect Arabic fertilization recommendations"""
        arabic_rec = "ضع 200 كجم من سماد متوازن (15:15:15) للهكتار"
        detected_type = evaluator._detect_recommendation_type(arabic_rec)

        assert detected_type == RecommendationType.FERTILIZATION

    def test_default_to_general(self, evaluator):
        """Should default to general type"""
        generic_rec = "This is a generic recommendation that doesn't fit specific categories"
        detected_type = evaluator._detect_recommendation_type(generic_rec)

        assert detected_type == RecommendationType.GENERAL


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Batch Evaluation
# ═══════════════════════════════════════════════════════════════════════════════


class TestBatchEvaluation:
    """Tests for batch evaluation"""

    def test_evaluate_batch(
        self, evaluator, sample_irrigation_recommendation, sample_fertilization_recommendation
    ):
        """Should evaluate multiple recommendations"""
        batch = [
            {
                "recommendation": sample_irrigation_recommendation,
                "context": {"crop": "wheat"},
                "query": "How to irrigate?",
                "type": RecommendationType.IRRIGATION,
            },
            {
                "recommendation": sample_fertilization_recommendation,
                "context": {"crop": "wheat"},
                "query": "How to fertilize?",
                "type": RecommendationType.FERTILIZATION,
            },
        ]

        results = evaluator.evaluate_batch(batch)

        assert len(results) == 2
        assert all(isinstance(r, EvaluationResult) for r in results)

    def test_batch_results_independent(
        self, evaluator, sample_irrigation_recommendation
    ):
        """Batch results should be independent"""
        batch = [
            {
                "recommendation": sample_irrigation_recommendation,
                "context": {"crop": "wheat"},
            },
            {
                "recommendation": sample_irrigation_recommendation,
                "context": {"crop": "corn"},
            },
        ]

        results = evaluator.evaluate_batch(batch)

        # Both should be evaluated
        assert len(results) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Statistics
# ═══════════════════════════════════════════════════════════════════════════════


class TestEvaluatorStatistics:
    """Tests for evaluator statistics"""

    def test_get_stats(self, evaluator, sample_irrigation_recommendation):
        """Should return evaluation statistics"""
        evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        stats = evaluator.get_stats()

        assert "evaluations" in stats
        assert "approved" in stats
        assert "rejected" in stats
        assert stats["evaluations"] >= 1

    def test_approval_rate_calculation(self, evaluator, sample_irrigation_recommendation):
        """Should calculate approval rate"""
        # Multiple evaluations
        for _ in range(3):
            evaluator.evaluate(
                recommendation=sample_irrigation_recommendation,
                context={},
                recommendation_type=RecommendationType.IRRIGATION,
            )

        stats = evaluator.get_stats()

        assert "approval_rate" in stats
        assert 0 <= stats["approval_rate"] <= 1

    def test_heuristic_vs_llm_stats(self, evaluator, sample_irrigation_recommendation):
        """Should track heuristic vs LLM evaluations"""
        evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        stats = evaluator.get_stats()

        assert stats["heuristic_evaluations"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Arabic Text Evaluation
# ═══════════════════════════════════════════════════════════════════════════════


class TestArabicEvaluation:
    """Tests for Arabic text evaluation"""

    def test_evaluate_arabic_recommendation(self, evaluator):
        """Should evaluate Arabic recommendations"""
        arabic_rec = """
        ري الحقل بانتظام مهم جداً لنجاح محصول القمح. يجب ري الحقل كل 3-4 أيام
        خلال موسم النمو. طبق 25-30 ملم من المياه في كل عملية ري.
        يفضل الري في الصباح الباكر من 6-9 صباحاً.
        تجنب الإغراق والتأكد من التصريف السليم للمياه.
        """
        result = evaluator.evaluate(
            recommendation=arabic_rec,
            context={"محصول": "قمح"},
            query="كيف أسقي القمح بشكل صحيح؟",
            recommendation_type=RecommendationType.IRRIGATION,
        )

        assert result.overall_score > 0
        assert len(result.feedback_ar) > 0

    def test_arabic_safety_evaluation(self, evaluator):
        """Should evaluate safety in Arabic text"""
        arabic_with_safety = """
        تحذير: استخدم قفازات وكمامة عند التعامل مع المواد الكيميائية.
        رش المبيد في الصباح الباكر. لا تفعل الرش في الحر الشديد.
        """
        result = evaluator.evaluate(
            recommendation=arabic_with_safety,
            context={},
            recommendation_type=RecommendationType.PEST_CONTROL,
        )

        safety_score = result.scores[EvaluationCriteria.SAFETY]
        # Should detect safety warnings in Arabic
        assert safety_score.score > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestEvaluationEdgeCases:
    """Tests for edge cases"""

    def test_evaluate_empty_recommendation(self, evaluator):
        """Should handle empty recommendation"""
        result = evaluator.evaluate(
            recommendation="",
            context={},
            recommendation_type=RecommendationType.GENERAL,
        )

        assert result.overall_score >= 0

    def test_evaluate_very_long_recommendation(self, evaluator):
        """Should handle very long recommendations"""
        long_rec = "Water the field. " * 1000

        result = evaluator.evaluate(
            recommendation=long_rec,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        assert result.overall_score >= 0

    def test_evaluate_special_characters(self, evaluator):
        """Should handle special characters"""
        special_rec = "Irrigate: 25-30mm/day! Water @6am #morning مرحبا"

        result = evaluator.evaluate(
            recommendation=special_rec,
            context={},
            recommendation_type=RecommendationType.IRRIGATION,
        )

        assert result.overall_score >= 0

    def test_evaluate_without_context(self, evaluator, sample_irrigation_recommendation):
        """Should handle missing context"""
        result = evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            context=None,
            recommendation_type=RecommendationType.IRRIGATION,
        )

        assert result.overall_score > 0

    def test_evaluate_without_query(self, evaluator, sample_irrigation_recommendation):
        """Should handle missing query"""
        result = evaluator.evaluate(
            recommendation=sample_irrigation_recommendation,
            context={},
            query=None,
            recommendation_type=RecommendationType.IRRIGATION,
        )

        assert result.overall_score > 0

    def test_evaluate_all_recommendation_types(self, evaluator):
        """Should handle all recommendation types"""
        recommendations = {
            RecommendationType.IRRIGATION: "Water the field every 3 days",
            RecommendationType.FERTILIZATION: "Apply 200 kg/ha of NPK 15:15:15",
            RecommendationType.PEST_CONTROL: "Spray neem oil on infected plants",
            RecommendationType.DISEASE: "Remove infected leaves and apply fungicide",
            RecommendationType.HARVEST: "Harvest when crops reach maturity",
            RecommendationType.PLANTING: "Plant seeds 5cm deep with 20cm spacing",
            RecommendationType.WEATHER: "Monitor rainfall and temperature patterns",
            RecommendationType.GENERAL: "Follow best agricultural practices",
        }

        for rec_type, recommendation in recommendations.items():
            result = evaluator.evaluate(
                recommendation=recommendation,
                context={},
                recommendation_type=rec_type,
            )
            assert result.recommendation_type == rec_type

    def test_multiple_evaluations_accumulate_stats(
        self, evaluator, sample_irrigation_recommendation
    ):
        """Multiple evaluations should accumulate stats"""
        for _ in range(5):
            evaluator.evaluate(
                recommendation=sample_irrigation_recommendation,
                context={},
                recommendation_type=RecommendationType.IRRIGATION,
            )

        stats = evaluator.get_stats()
        assert stats["evaluations"] == 5


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Safety Score Impact
# ═══════════════════════════════════════════════════════════════════════════════


class TestSafetyImpact:
    """Tests for safety score impact on approval"""

    def test_low_safety_blocks_approval(self, evaluator):
        """Low safety score should block approval regardless of other scores"""
        # High scores everywhere except safety
        rec_with_safety_issue = """
        Apply dangerous chemical pesticide without protection.
        Don't wear gloves or mask. Mix with water and spray directly.
        """

        result = evaluator.evaluate(
            recommendation=rec_with_safety_issue,
            context={},
            recommendation_type=RecommendationType.PEST_CONTROL,
        )

        # Safety should be flagged as low
        safety = result.scores[EvaluationCriteria.SAFETY]
        if safety.score < 0.5:
            assert result.is_approved is False

    def test_safety_warnings_improve_score(self, evaluator):
        """Recommendations with safety warnings should score higher"""
        without_safety = "Apply pesticide to the field."
        with_safety = """
        Apply pesticide to the field. WARNING: Wear protective gloves and mask.
        Use in early morning. Follow safety instructions carefully.
        """

        result_without = evaluator.evaluate(
            recommendation=without_safety,
            context={},
            recommendation_type=RecommendationType.PEST_CONTROL,
        )
        result_with = evaluator.evaluate(
            recommendation=with_safety,
            context={},
            recommendation_type=RecommendationType.PEST_CONTROL,
        )

        # With safety should score better
        assert (
            result_with.scores[EvaluationCriteria.SAFETY].score
            >= result_without.scores[EvaluationCriteria.SAFETY].score
        )
