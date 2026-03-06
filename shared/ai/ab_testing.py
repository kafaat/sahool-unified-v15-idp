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
