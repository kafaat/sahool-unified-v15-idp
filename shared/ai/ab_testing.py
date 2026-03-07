"""
A/B Testing Infrastructure for AI Models and RAG Configurations
===============================================================
بنية اختبار A/B لنماذج الذكاء الاصطناعي وإعدادات RAG

Provides A/B testing capabilities for:
- Model variant comparison (G-17)
- RAG workflow A/B testing with different chunk sizes, retrieval methods (G-16)
- Statistical significance determination
- Tenant-based traffic routing

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import hashlib
import math
import os
import random
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ABTestStatus(StrEnum):
    """Status of an A/B test | حالة اختبار A/B"""

    DRAFT = "draft"  # مسودة
    RUNNING = "running"  # قيد التشغيل
    PAUSED = "paused"  # متوقف مؤقتاً
    COMPLETED = "completed"  # مكتمل


class MetricGoal(StrEnum):
    """Optimisation direction for a metric | اتجاه تحسين المقياس"""

    HIGHER_IS_BETTER = "higher_is_better"  # الأعلى أفضل
    LOWER_IS_BETTER = "lower_is_better"  # الأقل أفضل


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class ABTest:
    """
    Definition of a single A/B test.
    تعريف اختبار A/B واحد.
    """

    test_id: str
    name: str
    name_ar: str

    # Variant configuration (model params, RAG config, etc.)
    variant_a: dict[str, Any]
    variant_b: dict[str, Any]

    # Traffic split – fraction routed to variant A (0.0-1.0)
    traffic_split: float = 0.5

    status: ABTestStatus = ABTestStatus.DRAFT

    start_time: datetime | None = None
    end_time: datetime | None = None

    # Minimum samples per variant before significance check
    min_samples: int = 30

    # Which metric to use for the primary winner decision
    primary_metric: str = "quality_score"
    primary_metric_goal: MetricGoal = MetricGoal.HIGHER_IS_BETTER

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class VariantMetrics:
    """
    Aggregated metrics for one variant.
    المقاييس المجمعة لمتغير واحد.
    """

    total_samples: int = 0
    latency_sum: float = 0.0
    quality_score_sum: float = 0.0
    satisfaction_sum: float = 0.0
    success_count: int = 0

    # Raw records kept for custom analysis
    records: list[dict[str, Any]] = field(default_factory=list)

    # -- Derived helpers --------------------------------------------------

    @property
    def avg_latency(self) -> float:
        """Average latency (ms) | متوسط زمن الاستجابة"""
        return self.latency_sum / self.total_samples if self.total_samples else 0.0

    @property
    def avg_quality(self) -> float:
        """Average quality score | متوسط درجة الجودة"""
        return self.quality_score_sum / self.total_samples if self.total_samples else 0.0

    @property
    def avg_satisfaction(self) -> float:
        """Average user satisfaction | متوسط رضا المستخدم"""
        return self.satisfaction_sum / self.total_samples if self.total_samples else 0.0

    @property
    def success_rate(self) -> float:
        """Success rate (0-1) | معدل النجاح"""
        return self.success_count / self.total_samples if self.total_samples else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict | تحويل إلى قاموس"""
        return {
            "total_samples": self.total_samples,
            "avg_latency_ms": round(self.avg_latency, 2),
            "avg_quality_score": round(self.avg_quality, 4),
            "avg_satisfaction": round(self.avg_satisfaction, 4),
            "success_rate": round(self.success_rate, 4),
        }


@dataclass
class ABTestResult:
    """
    Result of an A/B test evaluation.
    نتيجة تقييم اختبار A/B.
    """

    test_id: str
    variant_a_metrics: dict[str, Any]
    variant_b_metrics: dict[str, Any]

    winner: str | None  # "A", "B", or None if inconclusive
    confidence: float  # 0.0-1.0

    total_samples_a: int
    total_samples_b: int

    is_significant: bool


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------


class ABTestManager:
    """
    Manages A/B tests for AI model variants and RAG configurations.
    يدير اختبارات A/B لمتغيرات نماذج الذكاء الاصطناعي وإعدادات RAG.

    Usage::

        manager = ABTestManager()
        test = manager.create_test(
            name="Chunk-512 vs Chunk-1024",
            name_ar="مقارنة حجم القطعة 512 مع 1024",
            variant_a={"chunk_size": 512, "retrieval": "dense"},
            variant_b={"chunk_size": 1024, "retrieval": "dense"},
        )
        manager.start_test(test.test_id)

        variant = manager.route_request(test.test_id, tenant_id="t-123")
        # ... run inference with chosen variant ...
        manager.record_result(test.test_id, variant, {
            "latency_ms": 120,
            "quality_score": 0.85,
            "satisfaction": 4.0,
            "success": True,
        })

        result = manager.get_results(test.test_id)
    """

    def __init__(self) -> None:
        self._tests: dict[str, ABTest] = {}
        self._metrics: dict[str, dict[str, VariantMetrics]] = {}  # test_id -> {"A": …, "B": …}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def create_test(
        self,
        name: str,
        variant_a: dict[str, Any],
        variant_b: dict[str, Any],
        *,
        name_ar: str = "",
        traffic_split: float = 0.5,
        min_samples: int = 30,
        primary_metric: str = "quality_score",
        primary_metric_goal: MetricGoal = MetricGoal.HIGHER_IS_BETTER,
    ) -> ABTest:
        """
        Create a new A/B test definition.
        إنشاء تعريف اختبار A/B جديد.
        """
        test = ABTest(
            test_id=str(uuid.uuid4()),
            name=name,
            name_ar=name_ar or name,
            variant_a=variant_a,
            variant_b=variant_b,
            traffic_split=max(0.0, min(1.0, traffic_split)),
            min_samples=min_samples,
            primary_metric=primary_metric,
            primary_metric_goal=primary_metric_goal,
        )
        self._tests[test.test_id] = test
        self._metrics[test.test_id] = {
            "A": VariantMetrics(),
            "B": VariantMetrics(),
        }
        logger.info("ab_test_created", test_id=test.test_id, name=name)
        return test

    def start_test(self, test_id: str) -> ABTest:
        """Start a test | بدء الاختبار"""
        test = self._get_test(test_id)
        test.status = ABTestStatus.RUNNING
        test.start_time = datetime.now(UTC)
        logger.info("ab_test_started", test_id=test_id)
        return test

    def pause_test(self, test_id: str) -> ABTest:
        """Pause a running test | إيقاف الاختبار مؤقتاً"""
        test = self._get_test(test_id)
        test.status = ABTestStatus.PAUSED
        logger.info("ab_test_paused", test_id=test_id)
        return test

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def route_request(self, test_id: str, tenant_id: str) -> str:
        """
        Deterministically route a tenant to variant A or B.
        توجيه المستأجر بشكل حتمي إلى المتغير A أو B.

        Uses a stable hash of (test_id + tenant_id) so the same tenant
        always sees the same variant within one test.
        """
        test = self._get_test(test_id)
        digest = hashlib.sha256(f"{test_id}:{tenant_id}".encode()).hexdigest()
        bucket = int(digest[:8], 16) / 0xFFFFFFFF
        return "A" if bucket < test.traffic_split else "B"

    def get_variant_config(self, test_id: str, variant: str) -> dict[str, Any]:
        """
        Return the configuration dict for a variant.
        إرجاع إعدادات المتغير.
        """
        test = self._get_test(test_id)
        if variant == "A":
            return test.variant_a
        return test.variant_b

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_result(self, test_id: str, variant: str, metrics: dict[str, Any]) -> None:
        """
        Record a single observation for a variant.
        تسجيل ملاحظة واحدة لمتغير.

        Expected *metrics* keys (all optional):
        - ``latency_ms``   : float
        - ``quality_score``: float (0-1)
        - ``satisfaction`` : float (1-5)
        - ``success``      : bool
        """
        variant = variant.upper()
        if variant not in ("A", "B"):
            raise ValueError(f"variant must be 'A' or 'B', got '{variant}'")

        vm = self._metrics[test_id][variant]
        vm.total_samples += 1
        vm.latency_sum += float(metrics.get("latency_ms", 0))
        vm.quality_score_sum += float(metrics.get("quality_score", 0))
        vm.satisfaction_sum += float(metrics.get("satisfaction", 0))
        if metrics.get("success"):
            vm.success_count += 1
        vm.records.append(metrics)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def get_results(self, test_id: str) -> ABTestResult:
        """
        Compute current results and statistical significance.
        حساب النتائج الحالية والدلالة الإحصائية.
        """
        test = self._get_test(test_id)
        vm_a = self._metrics[test_id]["A"]
        vm_b = self._metrics[test_id]["B"]

        winner, confidence, significant = self._evaluate(test, vm_a, vm_b)

        return ABTestResult(
            test_id=test_id,
            variant_a_metrics=vm_a.to_dict(),
            variant_b_metrics=vm_b.to_dict(),
            winner=winner,
            confidence=round(confidence, 4),
            total_samples_a=vm_a.total_samples,
            total_samples_b=vm_b.total_samples,
            is_significant=significant,
        )

    def conclude_test(self, test_id: str) -> ABTestResult:
        """
        Mark the test as completed and return final results.
        تحديد الاختبار كمكتمل وإرجاع النتائج النهائية.
        """
        test = self._get_test(test_id)
        result = self.get_results(test_id)
        test.status = ABTestStatus.COMPLETED
        test.end_time = datetime.now(UTC)
        logger.info(
            "ab_test_concluded",
            test_id=test_id,
            winner=result.winner,
            confidence=result.confidence,
            is_significant=result.is_significant,
        )
        return result

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get_test(self, test_id: str) -> ABTest:
        """Retrieve test or raise | جلب الاختبار أو رفع خطأ"""
        test = self._tests.get(test_id)
        if test is None:
            raise KeyError(f"A/B test '{test_id}' not found | اختبار A/B غير موجود")
        return test

    def _evaluate(
        self,
        test: ABTest,
        vm_a: VariantMetrics,
        vm_b: VariantMetrics,
    ) -> tuple[str | None, float, bool]:
        """
        Determine winner using a simple chi-squared test on the primary
        metric discretised into success/failure buckets.
        تحديد الفائز باستخدام اختبار كاي تربيع بسيط.

        Returns ``(winner, confidence, is_significant)``.
        """
        n_a = vm_a.total_samples
        n_b = vm_b.total_samples

        # Not enough data yet
        if n_a < test.min_samples or n_b < test.min_samples:
            return None, 0.0, False

        # Use the primary metric average for comparison
        metric_key = test.primary_metric
        val_a = self._metric_value(vm_a, metric_key)
        val_b = self._metric_value(vm_b, metric_key)

        higher_better = test.primary_metric_goal == MetricGoal.HIGHER_IS_BETTER

        # Discretise: treat above-median as "success" for chi-squared
        s_a = vm_a.success_count
        f_a = n_a - s_a
        s_b = vm_b.success_count
        f_b = n_b - s_b

        chi2 = self._chi_squared(s_a, f_a, s_b, f_b)
        confidence = self._chi2_to_confidence(chi2)
        significant = confidence >= 0.95

        # Determine directional winner
        if higher_better:
            winner = "A" if val_a > val_b else "B" if val_b > val_a else None
        else:
            winner = "A" if val_a < val_b else "B" if val_b < val_a else None

        if not significant:
            winner = None

        return winner, confidence, significant

    @staticmethod
    def _metric_value(vm: VariantMetrics, key: str) -> float:
        """Resolve a named aggregate metric | حساب قيمة المقياس"""
        mapping: dict[str, float] = {
            "quality_score": vm.avg_quality,
            "latency": vm.avg_latency,
            "satisfaction": vm.avg_satisfaction,
            "success_rate": vm.success_rate,
        }
        return mapping.get(key, vm.avg_quality)

    @staticmethod
    def _chi_squared(s_a: int, f_a: int, s_b: int, f_b: int) -> float:
        """
        2x2 chi-squared statistic with Yates correction.
        إحصائية كاي تربيع 2×2 مع تصحيح ييتس.
        """
        n = s_a + f_a + s_b + f_b
        if n == 0:
            return 0.0

        expected = [
            [(s_a + f_a) * (s_a + s_b) / n, (s_a + f_a) * (f_a + f_b) / n],
            [(s_b + f_b) * (s_a + s_b) / n, (s_b + f_b) * (f_a + f_b) / n],
        ]
        observed = [[s_a, f_a], [s_b, f_b]]

        chi2 = 0.0
        for i in range(2):
            for j in range(2):
                e = expected[i][j]
                if e > 0:
                    diff = abs(observed[i][j] - e) - 0.5  # Yates correction
                    chi2 += (max(diff, 0) ** 2) / e
        return chi2

    @staticmethod
    def _chi2_to_confidence(chi2: float) -> float:
        """
        Approximate p-value for 1-df chi-squared → confidence.
        تحويل تقريبي لقيمة كاي تربيع إلى مستوى ثقة.

        Uses the survival function approximation for 1 degree of freedom:
        p ≈ erfc(sqrt(chi2 / 2))
        """
        if chi2 <= 0:
            return 0.0
        p_value = math.erfc(math.sqrt(chi2 / 2))
        return max(0.0, min(1.0, 1.0 - p_value))


# ---------------------------------------------------------------------------
# Extended A/B Testing: ABTestConfig, ABTestRunner, ModelVersionTracker
# (G-16 + G-17)
# ---------------------------------------------------------------------------

# Optional imports for LLM-based testing
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False



class SignificanceLevel(StrEnum):
    """Statistical significance levels | مستويات الدلالة الإحصائية"""

    NOT_SIGNIFICANT = "not_significant"  # غير دال
    MARGINALLY_SIGNIFICANT = "marginally_significant"  # دال هامشياً (p < 0.10)
    SIGNIFICANT = "significant"  # دال (p < 0.05)
    HIGHLY_SIGNIFICANT = "highly_significant"  # دال بشدة (p < 0.01)


@dataclass
class ModelVariant:
    """
    A model variant in an A/B test.
    متغير نموذج في اختبار A/B.
    """

    name: str
    name_ar: str = ""
    provider: str = "ollama"  # ollama, vllm, anthropic, openai, deepseek
    model: str = ""
    base_url: str = ""
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "metadata": self.metadata,
        }


@dataclass
class ABTestConfig:
    """
    Configuration for an A/B test between two LLM model variants.
    إعدادات اختبار A/B بين متغيرين لنموذج LLM.

    Defines the two model variants, traffic split ratio, evaluation
    metrics, and stopping criteria.

    Example:
        config = ABTestConfig(
            name="irrigation-advisor-v1-vs-v2",
            variant_a=ModelVariant(name="v1", model="sahool-advisor:v1"),
            variant_b=ModelVariant(name="v2", model="sahool-advisor:v2"),
            split_ratio=0.5,
            metric_names=["accuracy", "latency_ms", "relevance"],
            min_samples=100,
        )
    """

    name: str
    name_ar: str = ""
    variant_a: ModelVariant = field(default_factory=lambda: ModelVariant(name="control"))
    variant_b: ModelVariant = field(default_factory=lambda: ModelVariant(name="treatment"))
    split_ratio: float = 0.5  # Fraction of traffic to variant B
    metric_names: list[str] = field(
        default_factory=lambda: ["accuracy", "latency_ms"]
    )
    # Metrics where lower values are better (e.g., latency_ms, cost)
    lower_is_better_metrics: set[str] = field(
        default_factory=lambda: {"latency_ms", "cost"}
    )
    min_samples: int = 30  # Minimum samples per variant before significance test
    max_samples: int = 1000  # Maximum samples before auto-completion
    significance_threshold: float = 0.05  # p-value threshold
    domain: str = "agricultural"
    description: str = ""
    description_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "variant_a": self.variant_a.to_dict(),
            "variant_b": self.variant_b.to_dict(),
            "split_ratio": self.split_ratio,
            "metric_names": self.metric_names,
            "min_samples": self.min_samples,
            "max_samples": self.max_samples,
            "significance_threshold": self.significance_threshold,
            "domain": self.domain,
        }


@dataclass
class MetricComparison:
    """
    Statistical comparison of a single metric between variants.
    مقارنة إحصائية لمقياس واحد بين المتغيرات.
    """

    metric: str
    a_mean: float = 0.0
    a_std: float = 0.0
    a_count: int = 0
    b_mean: float = 0.0
    b_std: float = 0.0
    b_count: int = 0
    difference: float = 0.0  # b_mean - a_mean
    relative_change_pct: float = 0.0
    p_value: float = 1.0
    significance: SignificanceLevel = SignificanceLevel.NOT_SIGNIFICANT
    winner: str = "none"  # "a", "b", or "none"
    lower_is_better: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "a_mean": round(self.a_mean, 4),
            "a_std": round(self.a_std, 4),
            "a_count": self.a_count,
            "b_mean": round(self.b_mean, 4),
            "b_std": round(self.b_std, 4),
            "b_count": self.b_count,
            "difference": round(self.difference, 4),
            "relative_change_pct": round(self.relative_change_pct, 2),
            "p_value": round(self.p_value, 4),
            "significance": self.significance.value,
            "winner": self.winner,
        }


@dataclass
class ABTestRunnerResult:
    """
    Complete A/B test result from ABTestRunner with statistical analysis.
    نتيجة اختبار A/B الكاملة من منفذ الاختبار مع التحليل الإحصائي.
    """

    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    config_name: str = ""
    variant_a_name: str = ""
    variant_b_name: str = ""
    total_samples: int = 0
    a_samples: int = 0
    b_samples: int = 0
    comparisons: list[MetricComparison] = field(default_factory=list)
    overall_winner: str = "none"  # "a", "b", or "none"
    overall_confidence: float = 0.0
    recommendation: str = ""
    recommendation_ar: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "config_name": self.config_name,
            "variant_a": self.variant_a_name,
            "variant_b": self.variant_b_name,
            "total_samples": self.total_samples,
            "a_samples": self.a_samples,
            "b_samples": self.b_samples,
            "comparisons": [c.to_dict() for c in self.comparisons],
            "overall_winner": self.overall_winner,
            "overall_confidence": round(self.overall_confidence, 3),
            "recommendation": self.recommendation,
            "recommendation_ar": self.recommendation_ar,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Statistical Helpers
# ---------------------------------------------------------------------------

def _welch_t_test(
    mean_a: float, std_a: float, n_a: int,
    mean_b: float, std_b: float, n_b: int,
) -> float:
    """
    Compute approximate p-value using Welch's t-test (two-sample, unequal
    variance). Uses the normal approximation, valid for n >= 30.
    """
    if n_a < 2 or n_b < 2:
        return 1.0

    se = math.sqrt(std_a ** 2 / n_a + std_b ** 2 / n_b)
    if se < 1e-10:
        return 1.0 if abs(mean_a - mean_b) < 1e-10 else 0.0

    z = abs(mean_b - mean_a) / se
    # Two-tailed p-value via Abramowitz & Stegun normal CDF complement
    p = 2.0 * _normal_cdf_complement(z)
    return max(0.0, min(1.0, p))


def _normal_cdf_complement(z: float) -> float:
    """Approximate P(Z > z) for standard normal (Abramowitz & Stegun)."""
    if z < 0:
        return 1.0 - _normal_cdf_complement(-z)
    b0 = 0.2316419
    b1, b2, b3, b4, b5 = 0.319381530, -0.356563782, 1.781477937, -1.821255978, 1.330274429
    t = 1.0 / (1.0 + b0 * z)
    phi = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    return phi * t * (b1 + t * (b2 + t * (b3 + t * (b4 + t * b5))))


def _classify_significance(p_value: float, threshold: float = 0.05) -> SignificanceLevel:
    """Classify p-value into significance level."""
    if p_value < 0.01:
        return SignificanceLevel.HIGHLY_SIGNIFICANT
    if p_value < threshold:
        return SignificanceLevel.SIGNIFICANT
    if p_value < 0.10:
        return SignificanceLevel.MARGINALLY_SIGNIFICANT
    return SignificanceLevel.NOT_SIGNIFICANT


# ---------------------------------------------------------------------------
# ABTestRunner
# ---------------------------------------------------------------------------

class ABTestRunner:
    """
    Runs A/B tests across LLM providers with proper statistical analysis.
    يشغل اختبارات A/B عبر مزودي LLM مع تحليل إحصائي سليم.

    Uses Welch's t-test for per-metric significance and generates bilingual
    recommendations.

    Example:
        runner = ABTestRunner()
        config = ABTestConfig(
            name="advisor-v1-vs-v2",
            variant_a=ModelVariant(name="v1", provider="ollama", model="sahool:v1"),
            variant_b=ModelVariant(name="v2", provider="ollama", model="sahool:v2"),
        )
        test_id = runner.create_test(config)

        prompts = ["How to irrigate wheat?", "When to apply nitrogen?"]
        result = await runner.run_test(test_id, prompts)
        print(result.overall_winner)
    """

    def __init__(self) -> None:
        self._tests: dict[str, dict[str, Any]] = {}
        self._results: dict[str, ABTestRunnerResult] = {}

    def create_test(self, config: ABTestConfig) -> str:
        """
        Create a new A/B test.
        إنشاء اختبار A/B جديد.

        Returns:
            Test ID
        """
        test_id = str(uuid.uuid4())
        self._tests[test_id] = {
            "config": config,
            "samples_a": [],
            "samples_b": [],
            "created_at": datetime.now(UTC),
        }
        logger.info("ab_runner_test_created", test_id=test_id, name=config.name)
        return test_id

    async def run_test(
        self,
        test_id: str,
        prompts: list[str],
        evaluator: Any | None = None,
        generate_fn_a: Any | None = None,
        generate_fn_b: Any | None = None,
    ) -> ABTestRunnerResult:
        """
        Run an A/B test on a set of prompts.
        تشغيل اختبار A/B على مجموعة من المحفزات.

        For each prompt, randomly assigns to variant A or B, generates a
        response, evaluates metrics, and computes statistical significance.

        Args:
            test_id: Test identifier
            prompts: List of test prompts
            evaluator: Async fn(prompt, response, variant_name) -> dict[str, float]
            generate_fn_a: Async fn(prompt, ModelVariant) -> str for variant A
            generate_fn_b: Async fn(prompt, ModelVariant) -> str for variant B

        Returns:
            ABTestRunnerResult with statistical analysis
        """
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test not found: {test_id}")

        config: ABTestConfig = test["config"]
        started_at = datetime.now(UTC)

        for prompt in prompts:
            is_b = random.random() < config.split_ratio
            variant = config.variant_b if is_b else config.variant_a
            gen_fn = generate_fn_b if is_b else generate_fn_a

            start = datetime.now(UTC)
            try:
                if gen_fn:
                    response = await gen_fn(prompt, variant)
                else:
                    response = await self._default_generate(prompt, variant)
                latency_ms = (datetime.now(UTC) - start).total_seconds() * 1000

                if evaluator:
                    metrics = await evaluator(prompt, response, variant.name)
                else:
                    metrics = self._default_evaluate(prompt, response)
                metrics["latency_ms"] = latency_ms

            except Exception as e:
                logger.warning("ab_sample_failed", variant=variant.name, error=str(e))
                latency_ms = (datetime.now(UTC) - start).total_seconds() * 1000
                metrics = dict.fromkeys(config.metric_names, 0.0)
                metrics["latency_ms"] = latency_ms
                response = ""

            sample = {"prompt": prompt, "response": response, "metrics": metrics}
            (test["samples_b"] if is_b else test["samples_a"]).append(sample)

            total = len(test["samples_a"]) + len(test["samples_b"])
            if total >= config.max_samples:
                break

        result = self._analyze(test_id, config, test, started_at)
        self._results[test_id] = result
        return result

    def _analyze(
        self,
        test_id: str,
        config: ABTestConfig,
        test: dict[str, Any],
        started_at: datetime,
    ) -> ABTestRunnerResult:
        """Analyze results with Welch's t-test per metric."""
        samples_a = test["samples_a"]
        samples_b = test["samples_b"]

        comparisons: list[MetricComparison] = []
        a_wins = 0
        b_wins = 0
        total_scored = 0

        for metric_name in config.metric_names:
            lower_better = metric_name in config.lower_is_better_metrics

            vals_a = [s["metrics"].get(metric_name, 0.0) for s in samples_a if metric_name in s["metrics"]]
            vals_b = [s["metrics"].get(metric_name, 0.0) for s in samples_b if metric_name in s["metrics"]]

            if not vals_a or not vals_b:
                comparisons.append(MetricComparison(
                    metric=metric_name, a_count=len(vals_a), b_count=len(vals_b),
                    lower_is_better=lower_better,
                ))
                continue

            mean_a = sum(vals_a) / len(vals_a)
            mean_b = sum(vals_b) / len(vals_b)
            std_a = math.sqrt(sum((x - mean_a) ** 2 for x in vals_a) / max(len(vals_a) - 1, 1))
            std_b = math.sqrt(sum((x - mean_b) ** 2 for x in vals_b) / max(len(vals_b) - 1, 1))

            diff = mean_b - mean_a
            rel_change = (diff / mean_a * 100) if abs(mean_a) > 1e-10 else 0.0
            p = _welch_t_test(mean_a, std_a, len(vals_a), mean_b, std_b, len(vals_b))
            sig = _classify_significance(p, config.significance_threshold)

            winner = "none"
            if sig in (SignificanceLevel.SIGNIFICANT, SignificanceLevel.HIGHLY_SIGNIFICANT):
                winner = ("b" if mean_b < mean_a else "a") if lower_better else ("b" if mean_b > mean_a else "a")
                if winner == "b":
                    b_wins += 1
                else:
                    a_wins += 1
            total_scored += 1

            comparisons.append(MetricComparison(
                metric=metric_name, a_mean=mean_a, a_std=std_a, a_count=len(vals_a),
                b_mean=mean_b, b_std=std_b, b_count=len(vals_b),
                difference=diff, relative_change_pct=rel_change,
                p_value=p, significance=sig, winner=winner,
                lower_is_better=lower_better,
            ))

        overall_winner = "none"
        if b_wins > a_wins:
            overall_winner = "b"
        elif a_wins > b_wins:
            overall_winner = "a"

        sig_count = sum(
            1 for c in comparisons
            if c.significance in (SignificanceLevel.SIGNIFICANT, SignificanceLevel.HIGHLY_SIGNIFICANT)
        )
        overall_confidence = sig_count / max(total_scored, 1)

        rec, rec_ar = self._gen_recommendation(config, overall_winner, overall_confidence, comparisons)

        return ABTestRunnerResult(
            test_id=test_id,
            config_name=config.name,
            variant_a_name=config.variant_a.name,
            variant_b_name=config.variant_b.name,
            total_samples=len(samples_a) + len(samples_b),
            a_samples=len(samples_a),
            b_samples=len(samples_b),
            comparisons=comparisons,
            overall_winner=overall_winner,
            overall_confidence=overall_confidence,
            recommendation=rec,
            recommendation_ar=rec_ar,
            started_at=started_at,
            completed_at=datetime.now(UTC),
        )

    @staticmethod
    def _gen_recommendation(
        config: ABTestConfig,
        winner: str,
        confidence: float,
        comparisons: list[MetricComparison],
    ) -> tuple[str, str]:
        """Generate bilingual recommendation."""
        if winner == "none":
            return (
                f"No statistically significant difference between "
                f"'{config.variant_a.name}' and '{config.variant_b.name}'. "
                f"Consider collecting more samples.",
                f"لا يوجد فرق ذو دلالة إحصائية بين "
                f"'{config.variant_a.name_ar or config.variant_a.name}' و "
                f"'{config.variant_b.name_ar or config.variant_b.name}'. "
                f"يُنصح بجمع المزيد من العينات.",
            )
        wv = config.variant_b if winner == "b" else config.variant_a
        sig_metrics = [c for c in comparisons if c.winner == winner
                       and c.significance in (SignificanceLevel.SIGNIFICANT, SignificanceLevel.HIGHLY_SIGNIFICANT)]
        detail = ", ".join(f"{c.metric} ({c.relative_change_pct:+.1f}%)" for c in sig_metrics)
        en = f"Recommend deploying '{wv.name}' (confidence: {confidence:.0%}). Significant improvements: {detail}."
        ar = f"يُوصى بنشر '{wv.name_ar or wv.name}' (ثقة: {confidence:.0%}). تحسينات دالة: {detail}."
        return en, ar

    async def _default_generate(self, prompt: str, variant: ModelVariant) -> str:
        """Default generation using httpx to call provider API."""
        if not HTTPX_AVAILABLE:
            return f"[Mock response from {variant.name}]"

        if variant.provider == "ollama":
            base_url = variant.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{base_url}/api/generate",
                    json={"model": variant.model, "prompt": prompt, "stream": False,
                          "options": {"temperature": variant.temperature}},
                )
                return resp.json().get("response", "") if resp.status_code == 200 else ""

        elif variant.provider == "vllm":
            base_url = variant.base_url or os.getenv("VLLM_BASE_URL", "http://localhost:8270/v1")
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{base_url}/completions",
                    json={"model": variant.model, "prompt": prompt,
                          "max_tokens": variant.max_tokens, "temperature": variant.temperature},
                    headers={"Authorization": f"Bearer {variant.api_key or 'dummy'}"},
                )
                if resp.status_code == 200:
                    choices = resp.json().get("choices", [])
                    return choices[0].get("text", "") if choices else ""
                return ""

        return f"[Response from {variant.name}: {variant.provider}/{variant.model}]"

    @staticmethod
    def _default_evaluate(prompt: str, response: str) -> dict[str, float]:
        """Simple heuristic evaluator when no custom evaluator is provided."""
        metrics: dict[str, float] = {}
        if response.strip():
            length = len(response.split())
            metrics["accuracy"] = 0.7 if 10 <= length <= 1000 else (0.4 if length > 0 else 0.0)
        else:
            metrics["accuracy"] = 0.0

        prompt_words = set(prompt.lower().split())
        resp_words = set(response.lower().split())
        metrics["relevance"] = min(1.0, len(prompt_words & resp_words) / max(len(prompt_words), 1) * 2)
        return metrics

    def get_result(self, test_id: str) -> ABTestRunnerResult | None:
        """Get test result."""
        return self._results.get(test_id)

    def list_tests(self) -> list[dict[str, Any]]:
        """List all tests."""
        return [
            {"test_id": tid, "name": t["config"].name,
             "samples": len(t["samples_a"]) + len(t["samples_b"])}
            for tid, t in self._tests.items()
        ]


# ---------------------------------------------------------------------------
# Model Version Tracker (G-17)
# ---------------------------------------------------------------------------

@dataclass
class ModelVersion:
    """
    A tracked model version with performance metrics.
    إصدار نموذج متتبع مع مقاييس الأداء.
    """

    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    model_name_ar: str = ""
    version: str = ""  # e.g., "1.0.0", "v2"
    provider: str = "ollama"
    status: str = "active"  # active, deprecated, archived
    metrics: dict[str, float] = field(default_factory=dict)
    sample_count: int = 0
    deployed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    deprecated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    ab_test_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version_id": self.version_id,
            "model_name": self.model_name,
            "model_name_ar": self.model_name_ar,
            "version": self.version,
            "provider": self.provider,
            "status": self.status,
            "metrics": {k: round(v, 4) for k, v in self.metrics.items()},
            "sample_count": self.sample_count,
            "deployed_at": self.deployed_at.isoformat(),
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
            "ab_test_ids": self.ab_test_ids,
        }


class ModelVersionTracker:
    """
    Tracks deployed model versions with performance metrics.
    يتتبع إصدارات النماذج المنشورة مع مقاييس الأداء.

    Maintains a registry of model versions, their running-average metrics,
    and links to A/B tests that validated them.

    Example:
        tracker = ModelVersionTracker()
        v1 = tracker.register_version("sahool-advisor", "1.0.0")
        tracker.record_metrics(v1.version_id, {"accuracy": 0.85, "latency_ms": 120.0}, 100)
        comparison = tracker.compare_versions(v1.version_id, v2.version_id)
    """

    def __init__(self) -> None:
        self._versions: dict[str, ModelVersion] = {}
        self._model_index: dict[str, list[str]] = {}  # model_name -> [version_ids]

    def register_version(
        self,
        model_name: str,
        version: str,
        provider: str = "ollama",
        model_name_ar: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ModelVersion:
        """
        Register a new model version.
        تسجيل إصدار نموذج جديد.
        """
        mv = ModelVersion(
            model_name=model_name,
            model_name_ar=model_name_ar or model_name,
            version=version,
            provider=provider,
            metadata=metadata or {},
        )
        self._versions[mv.version_id] = mv
        self._model_index.setdefault(model_name, []).append(mv.version_id)
        logger.info("model_version_registered", model=model_name, version=version, id=mv.version_id)
        return mv

    def record_metrics(
        self,
        version_id: str,
        metrics: dict[str, float],
        sample_count: int = 0,
    ) -> ModelVersion | None:
        """
        Record performance metrics using running average.
        تسجيل مقاييس الأداء باستخدام المتوسط المتحرك.
        """
        mv = self._versions.get(version_id)
        if not mv:
            return None

        old_n = mv.sample_count
        new_n = old_n + sample_count

        for key, value in metrics.items():
            if key in mv.metrics and old_n > 0 and new_n > 0:
                mv.metrics[key] = (mv.metrics[key] * old_n + value * sample_count) / new_n
            else:
                mv.metrics[key] = value

        mv.sample_count = new_n
        return mv

    def link_ab_test(self, version_id: str, test_id: str) -> None:
        """Link an A/B test to a model version."""
        mv = self._versions.get(version_id)
        if mv and test_id not in mv.ab_test_ids:
            mv.ab_test_ids.append(test_id)

    def deprecate_version(self, version_id: str) -> bool:
        """Mark a model version as deprecated | تعليم إصدار نموذج كمهمل"""
        mv = self._versions.get(version_id)
        if not mv:
            return False
        mv.status = "deprecated"
        mv.deprecated_at = datetime.now(UTC)
        return True

    def get_version(self, version_id: str) -> ModelVersion | None:
        """Get a model version by ID."""
        return self._versions.get(version_id)

    def get_active_version(self, model_name: str) -> ModelVersion | None:
        """Get the latest active version | الحصول على أحدث إصدار نشط"""
        for vid in reversed(self._model_index.get(model_name, [])):
            mv = self._versions.get(vid)
            if mv and mv.status == "active":
                return mv
        return None

    def get_version_history(self, model_name: str) -> list[ModelVersion]:
        """Get all versions ordered by deployment date."""
        vids = self._model_index.get(model_name, [])
        versions = [self._versions[vid] for vid in vids if vid in self._versions]
        return sorted(versions, key=lambda v: v.deployed_at)

    def compare_versions(self, version_id_a: str, version_id_b: str) -> dict[str, Any]:
        """
        Compare metrics between two model versions.
        مقارنة المقاييس بين إصدارين.
        """
        va = self._versions.get(version_id_a)
        vb = self._versions.get(version_id_b)
        if not va or not vb:
            return {"error": "One or both versions not found"}

        all_metrics = sorted(set(va.metrics.keys()) | set(vb.metrics.keys()))
        comps: dict[str, dict[str, Any]] = {}
        for m in all_metrics:
            a_val = va.metrics.get(m)
            b_val = vb.metrics.get(m)
            if a_val is not None and b_val is not None:
                diff = b_val - a_val
                rel = (diff / a_val * 100) if abs(a_val) > 1e-10 else 0.0
                comps[m] = {"a": round(a_val, 4), "b": round(b_val, 4),
                            "difference": round(diff, 4), "relative_change_pct": round(rel, 2)}
            else:
                comps[m] = {"a": round(a_val, 4) if a_val is not None else None,
                            "b": round(b_val, 4) if b_val is not None else None}

        return {
            "version_a": {"id": va.version_id, "version": va.version, "model": va.model_name},
            "version_b": {"id": vb.version_id, "version": vb.version, "model": vb.model_name},
            "metrics": comps,
            "a_samples": va.sample_count,
            "b_samples": vb.sample_count,
        }

    def get_status(self) -> dict[str, Any]:
        """Get tracker status summary."""
        active = sum(1 for v in self._versions.values() if v.status == "active")
        deprecated = sum(1 for v in self._versions.values() if v.status == "deprecated")
        return {
            "total_versions": len(self._versions),
            "active": active,
            "deprecated": deprecated,
            "models_tracked": list(self._model_index.keys()),
        }


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_runner_instance: ABTestRunner | None = None
_tracker_instance: ModelVersionTracker | None = None


def get_ab_test_runner() -> ABTestRunner:
    """Get the global ABTestRunner instance | الحصول على نسخة منفذ اختبار A/B العامة"""
    global _runner_instance
    if _runner_instance is None:
        _runner_instance = ABTestRunner()
    return _runner_instance


def get_model_version_tracker() -> ModelVersionTracker:
    """Get the global ModelVersionTracker instance | الحصول على نسخة متتبع إصدارات النماذج العامة"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ModelVersionTracker()
    return _tracker_instance
