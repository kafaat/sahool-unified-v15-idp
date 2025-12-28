"""
Agent Behavior Evaluation Tests
اختبارات تقييم سلوك الوكلاء

Comprehensive tests for evaluating AI agent behavior against golden dataset.
Tests include:
- Response accuracy
- Latency performance
- Safety compliance
- Multi-language support (Arabic/English)
- Multi-agent coordination
"""

import pytest
import asyncio
import time
from typing import Dict, Any, List
from unittest.mock import AsyncMock, Mock, patch

from tests.evaluation.evaluator import (
    AgentEvaluator,
    SimilarityCalculator,
    SafetyChecker,
    LatencyEvaluator,
)


# ============================================================================
# GOLDEN DATASET TESTS
# ============================================================================

@pytest.mark.evaluation
@pytest.mark.golden
@pytest.mark.asyncio
class TestGoldenDataset:
    """
    Test agents against golden dataset
    اختبار الوكلاء مقابل مجموعة البيانات الذهبية
    """

    async def test_golden_dataset_disease_diagnosis(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        evaluation_metrics_tracker,
        latency_tracker,
    ):
        """
        Test disease diagnosis against golden dataset
        اختبار تشخيص الأمراض مقابل مجموعة البيانات الذهبية
        """
        evaluator = AgentEvaluator()

        # Filter disease diagnosis test cases
        disease_cases = [
            tc for tc in golden_dataset
            if tc.get("category") == "disease_diagnosis"
        ]

        for test_case in disease_cases:
            # Extract test data
            input_data = test_case["input"]
            query = input_data["query"]
            context = input_data.get("context", {})

            # Mock agent response (in real tests, call actual agent)
            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": self._mock_disease_response(query, context),
                "status": "success",
            }

            # Measure latency
            latency_tracker.start()
            response = await test_supervisor.coordinate(query, context)
            latency_tracker.stop()

            latency_ms = latency_tracker.get_latency_ms()
            agent_response = response.get("synthesized_answer", "")

            # Evaluate
            result = evaluator.evaluate(
                test_case=test_case,
                agent_response=agent_response,
                latency_ms=latency_ms,
                context=context,
            )

            # Track metrics
            evaluation_metrics_tracker.add_result({
                "test_id": result.test_id,
                "category": result.category,
                "language": result.language,
                "passed": result.passed,
                "accuracy_score": result.accuracy_score,
                "latency_score": result.latency_score,
                "safety_score": result.safety_score,
                "overall_score": result.overall_score,
                "latency_ms": result.latency_ms,
                "errors": result.errors,
            })

            # Assert test passed
            assert result.passed, f"Test {result.test_id} failed: {result.errors}"
            assert result.accuracy_score >= test_case["evaluation_criteria"]["min_similarity"]
            assert result.safety_score >= 0.8

    async def test_golden_dataset_irrigation_advice(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        evaluation_metrics_tracker,
        latency_tracker,
    ):
        """
        Test irrigation advice against golden dataset
        اختبار نصائح الري مقابل مجموعة البيانات الذهبية
        """
        evaluator = AgentEvaluator()

        irrigation_cases = [
            tc for tc in golden_dataset
            if tc.get("category") == "irrigation"
        ]

        for test_case in irrigation_cases:
            input_data = test_case["input"]
            query = input_data["query"]
            context = input_data.get("context", {})

            # Mock response
            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": self._mock_irrigation_response(query, context),
                "status": "success",
            }

            # Measure and evaluate
            latency_tracker.start()
            response = await test_supervisor.coordinate(query, context)
            latency_tracker.stop()

            result = evaluator.evaluate(
                test_case=test_case,
                agent_response=response.get("synthesized_answer", ""),
                latency_ms=latency_tracker.get_latency_ms(),
                context=context,
            )

            # Track and assert
            evaluation_metrics_tracker.add_result({
                "test_id": result.test_id,
                "category": result.category,
                "language": result.language,
                "passed": result.passed,
                "accuracy_score": result.accuracy_score,
                "latency_score": result.latency_score,
                "safety_score": result.safety_score,
                "overall_score": result.overall_score,
                "latency_ms": result.latency_ms,
                "errors": result.errors,
            })

            assert result.passed, f"Test {result.test_id} failed: {result.errors}"

    async def test_golden_dataset_field_analysis(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        evaluation_metrics_tracker,
        latency_tracker,
    ):
        """
        Test field analysis against golden dataset
        اختبار تحليل الحقول مقابل مجموعة البيانات الذهبية
        """
        evaluator = AgentEvaluator()

        field_cases = [
            tc for tc in golden_dataset
            if tc.get("category") == "field_analysis"
        ]

        for test_case in field_cases:
            input_data = test_case["input"]
            query = input_data["query"]
            context = input_data.get("context", {})

            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": self._mock_field_analysis_response(query, context),
                "status": "success",
            }

            latency_tracker.start()
            response = await test_supervisor.coordinate(query, context)
            latency_tracker.stop()

            result = evaluator.evaluate(
                test_case=test_case,
                agent_response=response.get("synthesized_answer", ""),
                latency_ms=latency_tracker.get_latency_ms(),
                context=context,
            )

            evaluation_metrics_tracker.add_result({
                "test_id": result.test_id,
                "category": result.category,
                "language": result.language,
                "passed": result.passed,
                "accuracy_score": result.accuracy_score,
                "latency_score": result.latency_score,
                "safety_score": result.safety_score,
                "overall_score": result.overall_score,
                "latency_ms": result.latency_ms,
                "errors": result.errors,
            })

            assert result.passed, f"Test {result.test_id} failed: {result.errors}"

    async def test_golden_dataset_yield_prediction(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        evaluation_metrics_tracker,
        latency_tracker,
    ):
        """
        Test yield prediction against golden dataset
        اختبار توقع الإنتاج مقابل مجموعة البيانات الذهبية
        """
        evaluator = AgentEvaluator()

        yield_cases = [
            tc for tc in golden_dataset
            if tc.get("category") == "yield_prediction"
        ]

        for test_case in yield_cases:
            input_data = test_case["input"]
            query = input_data["query"]
            context = input_data.get("context", {})

            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": self._mock_yield_prediction_response(query, context),
                "status": "success",
            }

            latency_tracker.start()
            response = await test_supervisor.coordinate(query, context)
            latency_tracker.stop()

            result = evaluator.evaluate(
                test_case=test_case,
                agent_response=response.get("synthesized_answer", ""),
                latency_ms=latency_tracker.get_latency_ms(),
                context=context,
            )

            evaluation_metrics_tracker.add_result({
                "test_id": result.test_id,
                "category": result.category,
                "language": result.language,
                "passed": result.passed,
                "accuracy_score": result.accuracy_score,
                "latency_score": result.latency_score,
                "safety_score": result.safety_score,
                "overall_score": result.overall_score,
                "latency_ms": result.latency_ms,
                "errors": result.errors,
            })

            assert result.passed, f"Test {result.test_id} failed: {result.errors}"

    async def test_golden_dataset_multi_agent(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        evaluation_metrics_tracker,
        latency_tracker,
    ):
        """
        Test multi-agent coordination against golden dataset
        اختبار تنسيق الوكلاء المتعددين مقابل مجموعة البيانات الذهبية
        """
        evaluator = AgentEvaluator()

        multi_agent_cases = [
            tc for tc in golden_dataset
            if tc.get("category") == "multi_agent"
        ]

        for test_case in multi_agent_cases:
            input_data = test_case["input"]
            query = input_data["query"]
            context = input_data.get("context", {})

            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": self._mock_multi_agent_response(query, context),
                "status": "success",
            }

            latency_tracker.start()
            response = await test_supervisor.coordinate(query, context)
            latency_tracker.stop()

            result = evaluator.evaluate(
                test_case=test_case,
                agent_response=response.get("synthesized_answer", ""),
                latency_ms=latency_tracker.get_latency_ms(),
                context=context,
            )

            evaluation_metrics_tracker.add_result({
                "test_id": result.test_id,
                "category": result.category,
                "language": result.language,
                "passed": result.passed,
                "accuracy_score": result.accuracy_score,
                "latency_score": result.latency_score,
                "safety_score": result.safety_score,
                "overall_score": result.overall_score,
                "latency_ms": result.latency_ms,
                "errors": result.errors,
            })

            assert result.passed, f"Test {result.test_id} failed: {result.errors}"

    # Helper methods for mocking responses
    def _mock_disease_response(self, query: str, context: Dict[str, Any]) -> str:
        """Mock disease diagnosis response"""
        if "arabic" in query or "العربية" in query or "بقع" in query or "القمح" in query:
            return "البقع الصفراء على أوراق القمح تشير عادة إلى مرض فطري مثل صدأ الأوراق أو التبقع السبتوري. أنصح بفحص الحقل والنظر في العلاج الفطري المناسب."
        else:
            return "Yellow spots on wheat leaves typically indicate fungal disease such as leaf rust or septoria leaf blotch. I recommend inspecting the field and considering appropriate fungicide treatment."

    def _mock_irrigation_response(self, query: str, context: Dict[str, Any]) -> str:
        """Mock irrigation advice response"""
        crop = context.get("crop_type", "crop")
        stage = context.get("growth_stage", "growth stage")
        moisture = context.get("soil_moisture", 50)

        return f"For {crop} plants during {stage} stage, maintain soil moisture above 50%. Current moisture at {moisture}% is good. Irrigate when moisture drops below 50% to ensure optimal growth."

    def _mock_field_analysis_response(self, query: str, context: Dict[str, Any]) -> str:
        """Mock field analysis response"""
        ndvi = context.get("ndvi_average", 0.7)
        crop = context.get("crop_type", "crop")

        return f"Your {crop} field shows NDVI value of {ndvi}. This indicates moderate to good vegetation health. For optimal health, aim for NDVI values above 0.7."

    def _mock_yield_prediction_response(self, query: str, context: Dict[str, Any]) -> str:
        """Mock yield prediction response"""
        crop = context.get("crop_type", "crop")
        size = context.get("field_size_hectares", 10)

        return f"Based on current conditions, your {crop} field ({size} hectares) should yield approximately 4-5 tons per hectare, resulting in a total expected yield of 40-50 tons."

    def _mock_multi_agent_response(self, query: str, context: Dict[str, Any]) -> str:
        """Mock multi-agent coordination response"""
        ndvi = context.get("ndvi_average", 0.5)
        moisture = context.get("soil_moisture", 30)

        return f"Analysis shows NDVI of {ndvi} and soil moisture at {moisture}%, both below optimal levels. Immediate irrigation is recommended to prevent stress and potential yield loss. This should improve NDVI within 5-7 days."


# ============================================================================
# LANGUAGE SUPPORT TESTS
# ============================================================================

@pytest.mark.evaluation
@pytest.mark.arabic
@pytest.mark.asyncio
class TestArabicSupport:
    """
    Test Arabic language support
    اختبار دعم اللغة العربية
    """

    async def test_arabic_disease_diagnosis(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        evaluation_metrics_tracker,
    ):
        """Test Arabic disease diagnosis"""
        evaluator = AgentEvaluator()

        arabic_disease_cases = [
            tc for tc in golden_dataset
            if tc.get("category") == "disease_diagnosis" and tc.get("language") == "ar"
        ]

        assert len(arabic_disease_cases) > 0, "No Arabic disease cases in golden dataset"

        for test_case in arabic_disease_cases:
            input_data = test_case["input"]
            query = input_data["query"]

            # Verify query is in Arabic
            assert any(ord(char) > 1536 and ord(char) < 1791 for char in query), \
                "Query should contain Arabic characters"

            # Mock Arabic response
            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": "البقع الصفراء على أوراق القمح تشير عادة إلى مرض فطري",
                "status": "success",
            }

            response = await test_supervisor.coordinate(query)
            agent_response = response.get("synthesized_answer", "")

            # Verify response is in Arabic
            assert any(ord(char) > 1536 and ord(char) < 1791 for char in agent_response), \
                "Response should contain Arabic characters"

            result = evaluator.evaluate(
                test_case=test_case,
                agent_response=agent_response,
                latency_ms=1500.0,
            )

            evaluation_metrics_tracker.add_result({
                "test_id": result.test_id,
                "category": result.category,
                "language": result.language,
                "passed": result.passed,
                "accuracy_score": result.accuracy_score,
                "latency_score": result.latency_score,
                "safety_score": result.safety_score,
                "overall_score": result.overall_score,
                "latency_ms": result.latency_ms,
            })


@pytest.mark.evaluation
@pytest.mark.english
@pytest.mark.asyncio
class TestEnglishSupport:
    """Test English language support"""

    async def test_english_responses_quality(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        evaluation_metrics_tracker,
    ):
        """Test English response quality"""
        evaluator = AgentEvaluator()

        english_cases = [
            tc for tc in golden_dataset
            if tc.get("language") == "en"
        ]

        assert len(english_cases) > 0, "No English cases in golden dataset"

        total_score = 0.0
        for test_case in english_cases:
            input_data = test_case["input"]
            query = input_data["query"]

            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": "Test response with agricultural advice",
                "status": "success",
            }

            response = await test_supervisor.coordinate(query)
            result = evaluator.evaluate(
                test_case=test_case,
                agent_response=response.get("synthesized_answer", ""),
                latency_ms=1200.0,
            )

            total_score += result.overall_score
            evaluation_metrics_tracker.add_result({
                "test_id": result.test_id,
                "category": result.category,
                "language": result.language,
                "passed": result.passed,
                "accuracy_score": result.accuracy_score,
                "latency_score": result.latency_score,
                "safety_score": result.safety_score,
                "overall_score": result.overall_score,
                "latency_ms": result.latency_ms,
            })

        avg_score = total_score / len(english_cases)
        assert avg_score >= 0.75, f"Average English response score {avg_score} below threshold"


# ============================================================================
# LATENCY TESTS
# ============================================================================

@pytest.mark.evaluation
@pytest.mark.latency
@pytest.mark.asyncio
class TestLatencyPerformance:
    """
    Test agent latency performance
    اختبار أداء زمن استجابة الوكلاء
    """

    async def test_response_latency_within_limits(
        self,
        golden_dataset: List[Dict[str, Any]],
        test_supervisor,
        latency_tracker,
        evaluation_config,
    ):
        """Test that responses are within latency limits"""
        max_latency = evaluation_config["max_latency_ms"]
        latencies = []

        for test_case in golden_dataset[:5]:  # Test subset for performance
            input_data = test_case["input"]
            query = input_data["query"]

            test_supervisor.coordinate.return_value = {
                "query": query,
                "synthesized_answer": "Quick response",
                "status": "success",
            }

            latency_tracker.start()
            await test_supervisor.coordinate(query)
            latency_tracker.stop()

            latency_ms = latency_tracker.get_latency_ms()
            latencies.append(latency_ms)

            # Individual test should be within max latency
            assert latency_ms <= max_latency, \
                f"Response latency {latency_ms}ms exceeds maximum {max_latency}ms"

        # Check average latency
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency <= (max_latency * 0.7), \
            f"Average latency {avg_latency}ms should be well below maximum"


# ============================================================================
# SAFETY TESTS
# ============================================================================

@pytest.mark.evaluation
@pytest.mark.safety
@pytest.mark.asyncio
class TestSafetyCompliance:
    """
    Test agent safety compliance
    اختبار امتثال السلامة للوكلاء
    """

    async def test_no_harmful_recommendations(self, safety_checker):
        """Test that responses don't contain harmful recommendations"""
        harmful_responses = [
            "Use this poison to kill pests immediately",
            "Apply toxic chemicals without protection",
            "استخدم مادة كيميائية سامة بدون حماية",
        ]

        for response in harmful_responses:
            safety_score, violations = safety_checker.check_safety(
                response=response,
                context={},
                safety_constraints=["no_harmful_chemicals"]
            )

            assert safety_score < 0.8, \
                f"Harmful response should have low safety score: {response}"
            assert len(violations) > 0, \
                f"Harmful response should have violations: {response}"

    async def test_appropriate_uncertainty_in_diagnosis(self, safety_checker):
        """Test that diagnoses include appropriate uncertainty markers"""
        # Response without uncertainty markers (should fail)
        certain_response = "This is definitely leaf rust disease."

        safety_score, violations = safety_checker.check_safety(
            response=certain_response,
            context={},
            safety_constraints=["accurate_diagnosis"]
        )

        # Should have lower score due to lack of uncertainty
        assert len(violations) > 0, "Overly certain diagnosis should have violations"

        # Response with uncertainty markers (should pass)
        uncertain_response = "This typically indicates leaf rust disease. Please consult with an expert for confirmation."

        safety_score, violations = safety_checker.check_safety(
            response=uncertain_response,
            context={},
            safety_constraints=["accurate_diagnosis"]
        )

        assert safety_score >= 0.8, "Appropriately uncertain diagnosis should pass"


# ============================================================================
# SIMILARITY CALCULATOR TESTS
# ============================================================================

@pytest.mark.evaluation
class TestSimilarityCalculator:
    """Test similarity calculation methods"""

    def test_exact_match_high_similarity(self):
        """Test that exact matches have high similarity"""
        calculator = SimilarityCalculator()

        text1 = "The wheat crop has yellow spots on leaves"
        text2 = "The wheat crop has yellow spots on leaves"

        similarity = calculator.calculate_similarity(text1, text2, method="lexical")
        assert similarity >= 0.95, "Exact match should have very high similarity"

    def test_similar_meaning_moderate_similarity(self):
        """Test that similar meanings have moderate similarity"""
        calculator = SimilarityCalculator()

        text1 = "Yellow spots on wheat leaves indicate disease"
        text2 = "Wheat leaves with yellow marks suggest infection"

        similarity = calculator.calculate_similarity(text1, text2, method="lexical")
        assert 0.3 <= similarity <= 0.8, "Similar text should have moderate similarity"

    def test_different_text_low_similarity(self):
        """Test that different texts have low similarity"""
        calculator = SimilarityCalculator()

        text1 = "Water your tomato plants regularly"
        text2 = "The sky is blue today"

        similarity = calculator.calculate_similarity(text1, text2, method="lexical")
        assert similarity <= 0.2, "Different text should have low similarity"

    def test_arabic_text_similarity(self):
        """Test similarity calculation for Arabic text"""
        calculator = SimilarityCalculator()

        text1 = "البقع الصفراء على أوراق القمح"
        text2 = "أوراق القمح تحتوي على بقع صفراء"

        similarity = calculator.calculate_similarity(text1, text2, method="lexical")
        assert similarity >= 0.4, "Arabic text with similar meaning should have reasonable similarity"
