"""
SAHOOL AI Monitoring Metrics
مقاييس مراقبة الذكاء الاصطناعي
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any


@dataclass
class MetricPoint:
    """نقطة بيانات مقياس واحدة."""

    value: float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    جامع مقاييس آمن للخيوط.

    مصمم ليتم تصديره بسهولة إلى Prometheus/OpenTelemetry لاحقًا.
    """

    def __init__(self):
        self._lock = Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}

    def inc_counter(self, name: str, value: float = 1.0, labels: dict | None = None):
        """زيادة عداد."""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value

    def record_histogram(self, name: str, value: float, labels: dict | None = None):
        """تسجيل قيمة في المدرج التكراري."""
        key = self._make_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)

    def set_gauge(self, name: str, value: float, labels: dict | None = None):
        """تعيين قيمة المقياس."""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def get_stats(self) -> dict[str, Any]:
        """الحصول على كل المقاييس كقاموس."""
        with self._lock:
            result = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {},
            }

            for key, values in self._histograms.items():
                if values:
                    result["histograms"][key] = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                    }

            return result

    def reset(self):
        """إعادة تعيين جميع المقاييس."""
        with self._lock:
            self._counters.clear()
            self._histograms.clear()
            self._gauges.clear()

    def _make_key(self, name: str, labels: dict | None) -> str:
        """إنشاء مفتاح المقياس من الاسم والتسميات."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"


# نسخة المقاييس العالمية
metrics = MetricsCollector()


class RAGMetrics:
    """مقاييس متخصصة لخط أنابيب RAG."""

    @staticmethod
    def record_query(latency_ms: float, chunks_retrieved: int, confidence: float):
        """تسجيل استعلام RAG."""
        metrics.inc_counter("rag_queries_total")
        metrics.record_histogram("rag_latency_ms", latency_ms)
        metrics.record_histogram("rag_chunks_retrieved", chunks_retrieved)
        metrics.record_histogram("rag_confidence", confidence)

    @staticmethod
    def record_fallback():
        """تسجيل تراجع إلى الاستجابة الافتراضية."""
        metrics.inc_counter("rag_fallbacks_total")

    @staticmethod
    def record_error(error_type: str):
        """تسجيل خطأ."""
        metrics.inc_counter("rag_errors_total", labels={"type": error_type})


class ContextMetrics:
    """مقاييس متخصصة لتجميع السياق."""

    @staticmethod
    def record_aggregation(latency_ms: float, completeness: float):
        """تسجيل تجميع سياق."""
        metrics.inc_counter("context_aggregations_total")
        metrics.record_histogram("context_latency_ms", latency_ms)
        metrics.record_histogram("context_completeness", completeness)


class FeedbackMetrics:
    """مقاييس متخصصة للتغذية الراجعة."""

    @staticmethod
    def record_feedback(rating: int | None, sentiment: str):
        """تسجيل تقديم تغذية راجعة."""
        metrics.inc_counter("feedback_total")
        if rating:
            metrics.record_histogram("feedback_rating", rating)
        metrics.inc_counter("feedback_sentiment", labels={"sentiment": sentiment})
