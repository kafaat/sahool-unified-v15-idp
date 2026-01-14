"""
AI Context Engineering Metrics
===============================
وحدة قياس هندسة السياق للذكاء الاصطناعي

Prometheus metrics for AI context engineering operations.
Tracks compression ratios, memory usage, evaluation scores, and latency.

المميزات:
- قياس نسبة ضغط الرموز
- قياس استخدام الذاكرة
- توزيع درجات التقييم
- قياس الكمون

Author: SAHOOL Platform Team
Updated: January 2025
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Callable

from shared.monitoring.metrics import get_registry

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Metrics Registry & Constants
# ─────────────────────────────────────────────────────────────────────────────

_registry = None


def get_ai_metrics_registry():
    """Get or initialize AI metrics registry"""
    global _registry
    if _registry is None:
        _registry = AIMetricsRegistry()
    return _registry


# ─────────────────────────────────────────────────────────────────────────────
# AI Metrics Registry Class
# ─────────────────────────────────────────────────────────────────────────────


class AIMetricsRegistry:
    """
    Registry for AI context engineering metrics.
    سجل قياسات هندسة السياق للذكاء الاصطناعي
    """

    def __init__(self):
        """Initialize AI metrics registry"""
        self.registry = get_registry("sahool_ai")

        # ─────────────────────────────────────────────────────────────────────
        # Token Compression Metrics
        # قياسات ضغط الرموز
        # ─────────────────────────────────────────────────────────────────────

        self.compression_operations = self.registry.counter(
            "compression_operations_total",
            "Total context compression operations performed",
            {"service": "ai_context_engineering", "component": "compression"},
        )

        self.compression_errors = self.registry.counter(
            "compression_errors_total",
            "Total context compression errors",
            {"service": "ai_context_engineering", "component": "compression"},
        )

        self.original_tokens = self.registry.histogram(
            "compression_original_tokens",
            "Original token count before compression",
            buckets=[100, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000],
            labels={"service": "ai_context_engineering", "component": "compression"},
        )

        self.compressed_tokens = self.registry.histogram(
            "compression_compressed_tokens",
            "Compressed token count after compression",
            buckets=[50, 100, 250, 500, 1000, 2000, 4000, 8000, 16000],
            labels={"service": "ai_context_engineering", "component": "compression"},
        )

        self.compression_ratio = self.registry.histogram(
            "compression_ratio",
            "Compression ratio achieved (compressed/original)",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            labels={"service": "ai_context_engineering", "component": "compression"},
        )

        self.tokens_saved = self.registry.histogram(
            "compression_tokens_saved",
            "Number of tokens saved by compression",
            buckets=[10, 50, 100, 500, 1000, 2000, 5000, 10000, 20000],
            labels={"service": "ai_context_engineering", "component": "compression"},
        )

        self.compression_by_strategy = self.registry.counter(
            "compression_by_strategy_total",
            "Compression operations by strategy",
            {"service": "ai_context_engineering", "component": "compression"},
        )

        # ─────────────────────────────────────────────────────────────────────
        # Memory Management Metrics
        # قياسات إدارة الذاكرة
        # ─────────────────────────────────────────────────────────────────────

        self.memory_operations = self.registry.counter(
            "memory_operations_total",
            "Total memory management operations",
            {"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_errors = self.registry.counter(
            "memory_errors_total",
            "Total memory management errors",
            {"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_entries_stored = self.registry.gauge(
            "memory_entries_stored",
            "Current number of memory entries stored",
            {"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_usage_bytes = self.registry.gauge(
            "memory_usage_bytes",
            "Current memory usage in bytes",
            {"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_entry_size = self.registry.histogram(
            "memory_entry_size_bytes",
            "Size of individual memory entries in bytes",
            buckets=[
                100,
                500,
                1000,
                5000,
                10000,
                50000,
                100000,
                500000,
                1000000,
            ],
            labels={"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_entries_by_type = self.registry.counter(
            "memory_entries_by_type_total",
            "Number of memory entries created by type",
            {"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_evictions = self.registry.counter(
            "memory_evictions_total",
            "Total memory entries evicted due to limits",
            {"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_ttl_expirations = self.registry.counter(
            "memory_ttl_expirations_total",
            "Total memory entries expired by TTL",
            {"service": "ai_context_engineering", "component": "memory"},
        )

        # ─────────────────────────────────────────────────────────────────────
        # Evaluation Score Metrics
        # قياسات درجات التقييم
        # ─────────────────────────────────────────────────────────────────────

        self.evaluation_operations = self.registry.counter(
            "evaluation_operations_total",
            "Total recommendation evaluations performed",
            {"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_errors = self.registry.counter(
            "evaluation_errors_total",
            "Total evaluation errors",
            {"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_score_overall = self.registry.histogram(
            "evaluation_score_overall",
            "Overall evaluation score distribution (0-1)",
            buckets=[
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6,
                0.7,
                0.8,
                0.9,
                1.0,
            ],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_score_accuracy = self.registry.histogram(
            "evaluation_score_accuracy",
            "Evaluation accuracy criterion score distribution",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_score_actionability = self.registry.histogram(
            "evaluation_score_actionability",
            "Evaluation actionability criterion score distribution",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_score_safety = self.registry.histogram(
            "evaluation_score_safety",
            "Evaluation safety criterion score distribution",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_score_relevance = self.registry.histogram(
            "evaluation_score_relevance",
            "Evaluation relevance criterion score distribution",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_score_completeness = self.registry.histogram(
            "evaluation_score_completeness",
            "Evaluation completeness criterion score distribution",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_score_clarity = self.registry.histogram(
            "evaluation_score_clarity",
            "Evaluation clarity criterion score distribution",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluation_grades = self.registry.counter(
            "evaluation_grades_total",
            "Number of evaluations by grade",
            {"service": "ai_context_engineering", "component": "evaluation"},
        )

        self.evaluations_by_type = self.registry.counter(
            "evaluations_by_type_total",
            "Number of evaluations by recommendation type",
            {"service": "ai_context_engineering", "component": "evaluation"},
        )

        # ─────────────────────────────────────────────────────────────────────
        # Latency Metrics
        # قياسات الكمون
        # ─────────────────────────────────────────────────────────────────────

        self.compression_latency = self.registry.histogram(
            "compression_latency_seconds",
            "Context compression latency in seconds",
            buckets=[
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
            ],
            labels={"service": "ai_context_engineering", "component": "compression"},
        )

        self.memory_retrieval_latency = self.registry.histogram(
            "memory_retrieval_latency_seconds",
            "Memory retrieval operation latency in seconds",
            buckets=[
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
            ],
            labels={"service": "ai_context_engineering", "component": "memory"},
        )

        self.memory_storage_latency = self.registry.histogram(
            "memory_storage_latency_seconds",
            "Memory storage operation latency in seconds",
            buckets=[
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
            ],
            labels={"service": "ai_context_engineering", "component": "memory"},
        )

        self.evaluation_latency = self.registry.histogram(
            "evaluation_latency_seconds",
            "Recommendation evaluation latency in seconds",
            buckets=[
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
                25.0,
                60.0,
            ],
            labels={"service": "ai_context_engineering", "component": "evaluation"},
        )


# ─────────────────────────────────────────────────────────────────────────────
# Metric Collection Decorators
# ─────────────────────────────────────────────────────────────────────────────


def track_compression(func: Callable) -> Callable:
    """
    Decorator to track context compression metrics.
    استديكوريتر لتتبع قياسات ضغط السياق

    Tracks:
    - Compression operations
    - Original/compressed token counts
    - Compression ratio
    - Tokens saved
    - Latency
    - Errors
    """
    metrics = get_ai_metrics_registry()

    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            latency = time.time() - start_time

            # Record metrics
            metrics.compression_operations.inc()
            metrics.compression_latency.observe(latency)

            # Extract metrics from result if available
            if hasattr(result, "original_tokens"):
                metrics.original_tokens.observe(result.original_tokens)
            if hasattr(result, "compressed_tokens"):
                metrics.compressed_tokens.observe(result.compressed_tokens)
            if hasattr(result, "compression_ratio"):
                metrics.compression_ratio.observe(result.compression_ratio)
            if hasattr(result, "tokens_saved"):
                metrics.tokens_saved.observe(result.tokens_saved)
            if hasattr(result, "strategy"):
                metrics.compression_by_strategy.inc()

            logger.info(
                f"compression_completed: latency={latency:.3f}s, "
                f"original_tokens={getattr(result, 'original_tokens', 0)}, "
                f"compressed_tokens={getattr(result, 'compressed_tokens', 0)}"
            )

            return result
        except Exception as e:
            metrics.compression_errors.inc()
            logger.error(f"compression_failed: {str(e)}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            latency = time.time() - start_time

            # Record metrics
            metrics.compression_operations.inc()
            metrics.compression_latency.observe(latency)

            # Extract metrics from result if available
            if hasattr(result, "original_tokens"):
                metrics.original_tokens.observe(result.original_tokens)
            if hasattr(result, "compressed_tokens"):
                metrics.compressed_tokens.observe(result.compressed_tokens)
            if hasattr(result, "compression_ratio"):
                metrics.compression_ratio.observe(result.compression_ratio)
            if hasattr(result, "tokens_saved"):
                metrics.tokens_saved.observe(result.tokens_saved)

            logger.info(
                f"compression_completed: latency={latency:.3f}s, "
                f"original_tokens={getattr(result, 'original_tokens', 0)}, "
                f"compressed_tokens={getattr(result, 'compressed_tokens', 0)}"
            )

            return result
        except Exception as e:
            metrics.compression_errors.inc()
            logger.error(f"compression_failed: {str(e)}")
            raise

    # Return appropriate wrapper based on function type
    if hasattr(func, "__await__"):
        return async_wrapper
    return sync_wrapper if not hasattr(func, "__code__") else (
        async_wrapper if "async" in func.__code__.co_names else sync_wrapper
    )


def track_memory_operation(operation_type: str = "general") -> Callable:
    """
    Decorator to track memory management metrics.
    استديكوريتر لتتبع قياسات إدارة الذاكرة

    Args:
        operation_type: Type of memory operation (store, retrieve, delete, etc.)

    Tracks:
    - Memory operations
    - Entry sizes
    - Entries by type
    - Latency
    - Errors
    """

    def decorator(func: Callable) -> Callable:
        metrics = get_ai_metrics_registry()

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start_time

                # Record metrics
                metrics.memory_operations.inc()
                metrics.memory_retrieval_latency.observe(
                    latency
                ) if operation_type == "retrieve" else metrics.memory_storage_latency.observe(
                    latency
                )

                logger.info(
                    f"memory_{operation_type}_completed: latency={latency:.3f}s"
                )

                return result
            except Exception as e:
                metrics.memory_errors.inc()
                logger.error(f"memory_{operation_type}_failed: {str(e)}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time

                # Record metrics
                metrics.memory_operations.inc()
                metrics.memory_retrieval_latency.observe(
                    latency
                ) if operation_type == "retrieve" else metrics.memory_storage_latency.observe(
                    latency
                )

                logger.info(
                    f"memory_{operation_type}_completed: latency={latency:.3f}s"
                )

                return result
            except Exception as e:
                metrics.memory_errors.inc()
                logger.error(f"memory_{operation_type}_failed: {str(e)}")
                raise

        return async_wrapper if hasattr(func, "__await__") else sync_wrapper

    return decorator


def track_evaluation(recommendation_type: str = "general") -> Callable:
    """
    Decorator to track recommendation evaluation metrics.
    استديكوريتر لتتبع قياسات تقييم التوصيات

    Args:
        recommendation_type: Type of recommendation being evaluated

    Tracks:
    - Evaluation operations
    - Overall scores
    - Individual criterion scores
    - Grades
    - Latency
    - Errors
    """

    def decorator(func: Callable) -> Callable:
        metrics = get_ai_metrics_registry()

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start_time

                # Record metrics
                metrics.evaluation_operations.inc()
                metrics.evaluation_latency.observe(latency)
                metrics.evaluations_by_type.inc()

                # Extract evaluation scores if available
                if hasattr(result, "overall_score"):
                    metrics.evaluation_score_overall.observe(result.overall_score)

                if hasattr(result, "criteria_scores"):
                    scores = result.criteria_scores
                    if "accuracy" in scores:
                        metrics.evaluation_score_accuracy.observe(scores["accuracy"])
                    if "actionability" in scores:
                        metrics.evaluation_score_actionability.observe(
                            scores["actionability"]
                        )
                    if "safety" in scores:
                        metrics.evaluation_score_safety.observe(scores["safety"])
                    if "relevance" in scores:
                        metrics.evaluation_score_relevance.observe(scores["relevance"])
                    if "completeness" in scores:
                        metrics.evaluation_score_completeness.observe(
                            scores["completeness"]
                        )
                    if "clarity" in scores:
                        metrics.evaluation_score_clarity.observe(scores["clarity"])

                if hasattr(result, "grade"):
                    metrics.evaluation_grades.inc()

                logger.info(
                    f"evaluation_completed: latency={latency:.3f}s, "
                    f"overall_score={getattr(result, 'overall_score', None)}"
                )

                return result
            except Exception as e:
                metrics.evaluation_errors.inc()
                logger.error(f"evaluation_failed: {str(e)}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time

                # Record metrics
                metrics.evaluation_operations.inc()
                metrics.evaluation_latency.observe(latency)
                metrics.evaluations_by_type.inc()

                # Extract evaluation scores if available
                if hasattr(result, "overall_score"):
                    metrics.evaluation_score_overall.observe(result.overall_score)

                if hasattr(result, "criteria_scores"):
                    scores = result.criteria_scores
                    if "accuracy" in scores:
                        metrics.evaluation_score_accuracy.observe(scores["accuracy"])
                    if "actionability" in scores:
                        metrics.evaluation_score_actionability.observe(
                            scores["actionability"]
                        )
                    if "safety" in scores:
                        metrics.evaluation_score_safety.observe(scores["safety"])
                    if "relevance" in scores:
                        metrics.evaluation_score_relevance.observe(scores["relevance"])
                    if "completeness" in scores:
                        metrics.evaluation_score_completeness.observe(
                            scores["completeness"]
                        )
                    if "clarity" in scores:
                        metrics.evaluation_score_clarity.observe(scores["clarity"])

                if hasattr(result, "grade"):
                    metrics.evaluation_grades.inc()

                logger.info(
                    f"evaluation_completed: latency={latency:.3f}s, "
                    f"overall_score={getattr(result, 'overall_score', None)}"
                )

                return result
            except Exception as e:
                metrics.evaluation_errors.inc()
                logger.error(f"evaluation_failed: {str(e)}")
                raise

        return async_wrapper if hasattr(func, "__await__") else sync_wrapper

    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions for Manual Metric Recording
# ─────────────────────────────────────────────────────────────────────────────


def record_memory_entry_stored(entry_size_bytes: int, entry_type: str) -> None:
    """
    Record a memory entry being stored.
    سجل حفظ إدخال ذاكرة

    Args:
        entry_size_bytes: Size of the entry in bytes
        entry_type: Type of memory entry
    """
    metrics = get_ai_metrics_registry()
    metrics.memory_entry_size.observe(entry_size_bytes)
    metrics.memory_entries_by_type.inc()


def record_memory_eviction(entry_type: str = "general") -> None:
    """
    Record a memory entry being evicted.
    سجل حذف إدخال ذاكرة

    Args:
        entry_type: Type of memory entry evicted
    """
    metrics = get_ai_metrics_registry()
    metrics.memory_evictions.inc()


def record_memory_ttl_expiration(entry_type: str = "general") -> None:
    """
    Record a memory entry expiring by TTL.
    سجل انتهاء صلاحية إدخال ذاكرة

    Args:
        entry_type: Type of memory entry that expired
    """
    metrics = get_ai_metrics_registry()
    metrics.memory_ttl_expirations.inc()


def update_memory_usage(total_entries: int, total_bytes: int) -> None:
    """
    Update current memory usage metrics.
    حدّث قياسات استخدام الذاكرة الحالية

    Args:
        total_entries: Total number of entries in memory
        total_bytes: Total memory usage in bytes
    """
    metrics = get_ai_metrics_registry()
    metrics.memory_entries_stored.set(total_entries)
    metrics.memory_usage_bytes.set(total_bytes)


@asynccontextmanager
async def track_operation_async(operation_name: str):
    """
    Context manager to track async operations.
    مدير السياق لتتبع العمليات غير المتزامنة

    Usage:
        async with track_operation_async("compression"):
            # perform operation
    """
    start_time = time.time()

    try:
        yield
        latency = time.time() - start_time
        logger.info(f"{operation_name}_completed: latency={latency:.3f}s")
    except Exception as e:
        logger.error(f"{operation_name}_failed: {str(e)}")
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Export Public API
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    "AIMetricsRegistry",
    "get_ai_metrics_registry",
    "track_compression",
    "track_memory_operation",
    "track_evaluation",
    "record_memory_entry_stored",
    "record_memory_eviction",
    "record_memory_ttl_expiration",
    "update_memory_usage",
    "track_operation_async",
]
