"""
Pytest Configuration and Fixtures for Agent Evaluation
تكوين pytest والتجهيزات لتقييم الوكلاء

This module provides fixtures for comprehensive agent evaluation including:
- Golden dataset loading
- Evaluation metrics tracking
- Multi-language support
- Safety checking
"""

import json

# Import from main test conftest
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "services" / "ai-advisor"))

from src.agents.base_agent import BaseAgent
from src.orchestration.supervisor import Supervisor

# ============================================================================
# CONFIGURATION
# ============================================================================


@pytest.fixture(scope="session")
def evaluation_config() -> dict[str, Any]:
    """
    Load evaluation configuration
    تحميل تكوين التقييم
    """
    return {
        "min_accuracy_threshold": 0.85,
        "max_latency_ms": 5000,
        "min_safety_score": 0.95,
        "supported_languages": ["en", "ar"],
        "enable_cache": False,  # Disable cache for evaluation
        "max_retries": 1,
        "timeout_seconds": 30,
    }


@pytest.fixture(scope="session")
def evaluation_dataset_path() -> Path:
    """
    Get path to evaluation datasets
    الحصول على مسار مجموعات بيانات التقييم
    """
    dataset_path = Path(__file__).parent / "datasets"
    dataset_path.mkdir(parents=True, exist_ok=True)
    return dataset_path


@pytest.fixture(scope="session")
def golden_dataset(evaluation_dataset_path: Path) -> list[dict[str, Any]]:
    """
    Load golden dataset for evaluation
    تحميل مجموعة البيانات الذهبية للتقييم

    Golden dataset structure:
    {
        "id": "unique-test-id",
        "category": "disease_diagnosis|field_analysis|irrigation|yield_prediction",
        "language": "en|ar",
        "input": {
            "query": "User query",
            "context": {}
        },
        "expected_output": {
            "response": "Expected response content",
            "agents": ["agent1", "agent2"],
            "key_points": ["point1", "point2"],
            "safety_constraints": []
        },
        "evaluation_criteria": {
            "min_similarity": 0.8,
            "required_keywords": [],
            "forbidden_keywords": [],
            "max_latency_ms": 3000
        }
    }
    """
    golden_file = evaluation_dataset_path / "golden_dataset.json"

    # Create default golden dataset if doesn't exist
    if not golden_file.exists():
        default_dataset = _create_default_golden_dataset()
        with open(golden_file, "w", encoding="utf-8") as f:
            json.dump(default_dataset, f, ensure_ascii=False, indent=2)

    with open(golden_file, encoding="utf-8") as f:
        dataset = json.load(f)

    return dataset


@pytest.fixture(scope="session")
def evaluation_metrics_tracker():
    """
    Track evaluation metrics throughout the test session
    تتبع مقاييس التقييم طوال جلسة الاختبار
    """

    class MetricsTracker:
        def __init__(self):
            self.results: list[dict[str, Any]] = []
            self.start_time = time.time()

        def add_result(self, result: dict[str, Any]):
            """Add evaluation result"""
            result["timestamp"] = datetime.utcnow().isoformat()
            self.results.append(result)

        def get_summary(self) -> dict[str, Any]:
            """Calculate summary statistics"""
            if not self.results:
                return {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "overall_score": 0.0,
                }

            total = len(self.results)
            passed = sum(1 for r in self.results if r.get("passed", False))
            failed = total - passed

            accuracy_scores = [r.get("accuracy_score", 0) for r in self.results]
            latency_scores = [r.get("latency_score", 0) for r in self.results]
            safety_scores = [r.get("safety_score", 0) for r in self.results]

            # Language breakdown
            arabic_results = [r for r in self.results if r.get("language") == "ar"]
            english_results = [r for r in self.results if r.get("language") == "en"]

            return {
                "total_tests": total,
                "passed_tests": passed,
                "failed_tests": failed,
                "pass_rate": (passed / total * 100) if total > 0 else 0,
                "accuracy": (
                    sum(accuracy_scores) / len(accuracy_scores) * 100 if accuracy_scores else 0
                ),
                "latency_score": (
                    sum(latency_scores) / len(latency_scores) * 100 if latency_scores else 0
                ),
                "safety_score": (
                    sum(safety_scores) / len(safety_scores) * 100 if safety_scores else 0
                ),
                "overall_score": (
                    sum(
                        [
                            sum(accuracy_scores) / len(accuracy_scores) * 0.5,
                            sum(latency_scores) / len(latency_scores) * 0.25,
                            sum(safety_scores) / len(safety_scores) * 0.25,
                        ]
                    )
                    * 100
                    if accuracy_scores
                    else 0
                ),
                "avg_latency_ms": (
                    sum(r.get("latency_ms", 0) for r in self.results) / total if total > 0 else 0
                ),
                "arabic_support": (
                    (
                        sum(1 for r in arabic_results if r.get("passed", False))
                        / len(arabic_results)
                        * 100
                    )
                    if arabic_results
                    else 0
                ),
                "english_support": (
                    (
                        sum(1 for r in english_results if r.get("passed", False))
                        / len(english_results)
                        * 100
                    )
                    if english_results
                    else 0
                ),
                "total_duration_seconds": time.time() - self.start_time,
                "results": self.results,
            }

        def save_results(self, output_path: Path):
            """Save results to file"""
            summary = self.get_summary()
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

    return MetricsTracker()


# ============================================================================
# AGENT FIXTURES
# ============================================================================


@pytest.fixture
def mock_llm_response():
    """
    Mock LLM response for evaluation
    محاكاة استجابة نموذج اللغة للتقييم
    """

    def _create_response(content: str, language: str = "en"):
        mock_response = Mock()
        mock_response.content = content
        mock_response.response_metadata = {
            "model": "claude-3-5-sonnet-20241022",
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "stop_reason": "stop",
        }
        return mock_response

    return _create_response


@pytest.fixture
def mock_retriever():
    """
    Mock RAG retriever for evaluation
    محاكاة مسترجع RAG للتقييم
    """
    mock = Mock()
    mock.retrieve = Mock(
        return_value=[
            Mock(
                page_content="Relevant agricultural knowledge for testing",
                metadata={"source": "test-doc", "score": 0.85},
            )
        ]
    )
    return mock


@pytest.fixture
async def test_agents(mock_retriever):
    """
    Create test agents for evaluation
    إنشاء وكلاء اختبار للتقييم
    """
    # Note: In real evaluation, these would be actual agents
    # For unit tests, we can use mocks
    agents = {
        "field_analyst": Mock(spec=BaseAgent),
        "disease_expert": Mock(spec=BaseAgent),
        "irrigation_advisor": Mock(spec=BaseAgent),
        "yield_predictor": Mock(spec=BaseAgent),
    }

    for name, agent in agents.items():
        agent.name = name
        agent.role = f"Test {name}"
        agent.retriever = mock_retriever
        agent.think = AsyncMock()

    return agents


@pytest.fixture
async def test_supervisor(test_agents):
    """
    Create test supervisor for evaluation
    إنشاء مشرف اختبار للتقييم
    """
    supervisor = Mock(spec=Supervisor)
    supervisor.agents = test_agents
    supervisor.coordinate = AsyncMock()
    return supervisor


# ============================================================================
# EVALUATION HELPERS
# ============================================================================


@pytest.fixture
def latency_tracker():
    """
    Track latency for each test
    تتبع زمن الاستجابة لكل اختبار
    """

    class LatencyTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        def get_latency_ms(self) -> float:
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time) * 1000
            return 0.0

    return LatencyTracker()


@pytest.fixture
def safety_checker():
    """
    Check for safety violations in agent responses
    التحقق من انتهاكات السلامة في استجابات الوكلاء
    """
    from tests.evaluation.evaluator import SafetyChecker

    return SafetyChecker()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _create_default_golden_dataset() -> list[dict[str, Any]]:
    """
    Create default golden dataset
    إنشاء مجموعة البيانات الذهبية الافتراضية
    """
    return [
        # English: Disease Diagnosis
        {
            "id": "disease-001-en",
            "category": "disease_diagnosis",
            "language": "en",
            "input": {
                "query": "My wheat crop has yellow spots on leaves. What could be the problem?",
                "context": {
                    "crop_type": "wheat",
                    "location": "Yemen",
                    "season": "winter",
                },
            },
            "expected_output": {
                "response": "Yellow spots on wheat leaves typically indicate fungal disease such as leaf rust or septoria.",
                "agents": ["disease_expert"],
                "key_points": ["yellow spots", "fungal disease", "wheat", "treatment"],
                "safety_constraints": ["accurate_diagnosis", "no_harmful_chemicals"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["disease", "wheat", "leaf"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # Arabic: Disease Diagnosis
        {
            "id": "disease-001-ar",
            "category": "disease_diagnosis",
            "language": "ar",
            "input": {
                "query": "محصول القمح لديه بقع صفراء على الأوراق. ما المشكلة؟",
                "context": {
                    "crop_type": "wheat",
                    "location": "اليمن",
                    "season": "شتاء",
                },
            },
            "expected_output": {
                "response": "البقع الصفراء على أوراق القمح تشير عادة إلى مرض فطري مثل صدأ الأوراق",
                "agents": ["disease_expert"],
                "key_points": ["بقع صفراء", "مرض فطري", "القمح", "علاج"],
                "safety_constraints": ["accurate_diagnosis", "no_harmful_chemicals"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["مرض", "القمح"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # English: Irrigation Advice
        {
            "id": "irrigation-001-en",
            "category": "irrigation",
            "language": "en",
            "input": {
                "query": "When should I irrigate my tomato plants?",
                "context": {
                    "crop_type": "tomato",
                    "growth_stage": "flowering",
                    "soil_moisture": 45,
                    "temperature": 28,
                },
            },
            "expected_output": {
                "response": "Tomato plants during flowering stage need consistent moisture. Irrigate when soil moisture drops below 50%.",
                "agents": ["irrigation_advisor"],
                "key_points": [
                    "tomato",
                    "flowering",
                    "soil moisture",
                    "irrigation schedule",
                ],
                "safety_constraints": ["water_conservation", "no_overwatering"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["irrigation", "tomato", "moisture"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # English: Field Analysis
        {
            "id": "field-001-en",
            "category": "field_analysis",
            "language": "en",
            "input": {
                "query": "Analyze the health of my corn field based on NDVI data",
                "context": {
                    "field_id": "field-123",
                    "crop_type": "corn",
                    "ndvi_average": 0.65,
                    "growth_stage": "vegetative",
                },
            },
            "expected_output": {
                "response": "NDVI of 0.65 indicates moderate vegetation health. Corn in vegetative stage should have higher values.",
                "agents": ["field_analyst"],
                "key_points": ["NDVI", "corn", "field health", "vegetation"],
                "safety_constraints": ["accurate_analysis"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["NDVI", "corn", "health"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # English: Yield Prediction
        {
            "id": "yield-001-en",
            "category": "yield_prediction",
            "language": "en",
            "input": {
                "query": "What will be the expected yield for my wheat field?",
                "context": {
                    "crop_type": "wheat",
                    "field_size_hectares": 10,
                    "growth_stage": "grain filling",
                    "weather_conditions": "favorable",
                },
            },
            "expected_output": {
                "response": "Based on favorable conditions and grain filling stage, expect 4-5 tons per hectare yield.",
                "agents": ["yield_predictor"],
                "key_points": ["yield", "wheat", "prediction", "tons per hectare"],
                "safety_constraints": ["realistic_expectations"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["yield", "wheat", "tons"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # Multi-agent coordination test
        {
            "id": "multi-001-en",
            "category": "multi_agent",
            "language": "en",
            "input": {
                "query": "My wheat field shows low NDVI. Should I irrigate and how will this affect yield?",
                "context": {
                    "crop_type": "wheat",
                    "ndvi_average": 0.45,
                    "soil_moisture": 30,
                    "growth_stage": "heading",
                },
            },
            "expected_output": {
                "response": "Low NDVI and soil moisture indicate stress. Immediate irrigation recommended to prevent yield loss.",
                "agents": ["field_analyst", "irrigation_advisor", "yield_predictor"],
                "key_points": ["NDVI", "irrigation", "yield impact", "coordination"],
                "safety_constraints": ["holistic_advice"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.70,
                "required_keywords": ["NDVI", "irrigation", "yield"],
                "forbidden_keywords": [],
                "max_latency_ms": 8000,
            },
        },
    ]


@pytest.fixture(autouse=True, scope="session")
def save_evaluation_metrics(request, evaluation_metrics_tracker):
    """
    Automatically save evaluation metrics at end of session
    حفظ مقاييس التقييم تلقائيًا في نهاية الجلسة
    """
    yield

    # Save metrics after all tests complete
    output_path = Path(__file__).parent / "evaluation-results.json"
    evaluation_metrics_tracker.save_results(output_path)
    print(f"\n✅ Evaluation results saved to: {output_path}")


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "evaluation: mark test as part of agent evaluation suite")
    config.addinivalue_line("markers", "golden: mark test as using golden dataset")
    config.addinivalue_line("markers", "arabic: mark test for Arabic language support")
    config.addinivalue_line("markers", "english: mark test for English language support")
    config.addinivalue_line("markers", "latency: mark test for latency measurement")
    config.addinivalue_line("markers", "safety: mark test for safety checking")
