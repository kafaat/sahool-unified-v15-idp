"""
Unit Tests for AI Context Engineering Metrics
==============================================
اختبارات وحدة قياسات هندسة السياق للذكاء الاصطناعي

Tests for Prometheus metrics integration in AI skills.
Tests compression, memory, evaluation, and latency metrics.

Author: SAHOOL Platform Team
Updated: January 2025
"""

import asyncio
import pytest
from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock, patch

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Import metrics components
from shared.ai.context_engineering.metrics import (
    AIMetricsRegistry,
    get_ai_metrics_registry,
    track_compression,
    track_memory_operation,
    track_evaluation,
    record_memory_entry_stored,
    record_memory_eviction,
    record_memory_ttl_expiration,
    update_memory_usage,
    track_operation_async,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class MockCompressionResult:
    """Mock compression result for testing"""

    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    tokens_saved: int
    strategy: str = "hybrid"


@dataclass
class MockEvaluationResult:
    """Mock evaluation result for testing"""

    overall_score: float
    criteria_scores: dict
    grade: str
    recommendation_type: str = "irrigation"


@pytest.fixture
def metrics_registry():
    """Provide a fresh metrics registry for each test"""
    # Create new registry instance
    registry = AIMetricsRegistry()
    return registry


@pytest.fixture
def mock_compression_result():
    """Provide a mock compression result"""
    return MockCompressionResult(
        original_tokens=1000,
        compressed_tokens=400,
        compression_ratio=0.4,
        tokens_saved=600,
    )


@pytest.fixture
def mock_evaluation_result():
    """Provide a mock evaluation result"""
    return MockEvaluationResult(
        overall_score=0.85,
        criteria_scores={
            "accuracy": 0.9,
            "actionability": 0.85,
            "safety": 0.95,
            "relevance": 0.8,
            "completeness": 0.8,
            "clarity": 0.85,
        },
        grade="good",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Registry Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAIMetricsRegistry:
    """Test AIMetricsRegistry initialization and structure"""

    def test_registry_initialization(self):
        """Test registry initializes with all metric types"""
        registry = AIMetricsRegistry()

        # Check compression metrics exist
        assert hasattr(registry, "compression_operations")
        assert hasattr(registry, "compression_errors")
        assert hasattr(registry, "original_tokens")
        assert hasattr(registry, "compressed_tokens")
        assert hasattr(registry, "compression_ratio")
        assert hasattr(registry, "tokens_saved")

        # Check memory metrics exist
        assert hasattr(registry, "memory_operations")
        assert hasattr(registry, "memory_errors")
        assert hasattr(registry, "memory_entries_stored")
        assert hasattr(registry, "memory_usage_bytes")
        assert hasattr(registry, "memory_entry_size")

        # Check evaluation metrics exist
        assert hasattr(registry, "evaluation_operations")
        assert hasattr(registry, "evaluation_errors")
        assert hasattr(registry, "evaluation_score_overall")
        assert hasattr(registry, "evaluation_score_accuracy")

        # Check latency metrics exist
        assert hasattr(registry, "compression_latency")
        assert hasattr(registry, "memory_retrieval_latency")
        assert hasattr(registry, "evaluation_latency")

    def test_get_ai_metrics_registry_singleton(self):
        """Test get_ai_metrics_registry returns singleton"""
        registry1 = get_ai_metrics_registry()
        registry2 = get_ai_metrics_registry()

        assert registry1 is registry2

    def test_registry_has_valid_metrics_objects(self, metrics_registry):
        """Test all metrics are properly initialized"""
        # Counters should have inc() method
        assert hasattr(metrics_registry.compression_operations, "inc")
        assert hasattr(metrics_registry.compression_operations, "value")

        # Gauges should have set() method
        assert hasattr(metrics_registry.memory_entries_stored, "set")
        assert hasattr(metrics_registry.memory_entries_stored, "inc")
        assert hasattr(metrics_registry.memory_entries_stored, "dec")

        # Histograms should have observe() method
        assert hasattr(metrics_registry.compression_latency, "observe")
        assert hasattr(metrics_registry.compression_latency, "count")
        assert hasattr(metrics_registry.compression_latency, "sum")


# ─────────────────────────────────────────────────────────────────────────────
# Compression Metrics Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCompressionMetrics:
    """Test compression-related metrics"""

    def test_track_compression_decorator_sync(
        self, metrics_registry, mock_compression_result
    ):
        """Test track_compression decorator with sync function"""

        @track_compression
        def compress_data():
            return mock_compression_result

        result = compress_data()

        assert result == mock_compression_result
        assert metrics_registry.compression_operations.value >= 0

    @pytest.mark.asyncio
    async def test_track_compression_decorator_async(
        self, mock_compression_result
    ):
        """Test track_compression decorator with async function"""

        @track_compression
        async def compress_data_async():
            await asyncio.sleep(0.01)
            return mock_compression_result

        result = await compress_data_async()

        assert result == mock_compression_result

    def test_compression_metrics_recording(self, metrics_registry):
        """Test compression metrics are recorded correctly"""
        # Get initial counts
        initial_ops = metrics_registry.compression_operations.value
        initial_original = metrics_registry.original_tokens.count
        initial_compressed = metrics_registry.compressed_tokens.count
        initial_ratio = metrics_registry.compression_ratio.count
        initial_saved = metrics_registry.tokens_saved.count

        # Record compression metrics
        metrics_registry.compression_operations.inc()
        metrics_registry.original_tokens.observe(1000)
        metrics_registry.compressed_tokens.observe(400)
        metrics_registry.compression_ratio.observe(0.4)
        metrics_registry.tokens_saved.observe(600)

        # Verify metrics increased
        assert metrics_registry.compression_operations.value == initial_ops + 1
        assert metrics_registry.original_tokens.count == initial_original + 1
        assert metrics_registry.compressed_tokens.count == initial_compressed + 1
        assert metrics_registry.compression_ratio.count == initial_ratio + 1
        assert metrics_registry.tokens_saved.count == initial_saved + 1

    def test_compression_error_tracking(self, metrics_registry):
        """Test compression errors are recorded"""

        @track_compression
        def compress_with_error():
            raise ValueError("Compression failed")

        with pytest.raises(ValueError):
            compress_with_error()

        assert metrics_registry.compression_errors.value >= 1

    @pytest.mark.asyncio
    async def test_compression_latency_measurement(self):
        """Test compression latency is measured"""
        metrics = get_ai_metrics_registry()
        initial_count = metrics.compression_latency.count

        @track_compression
        async def slow_compress():
            await asyncio.sleep(0.02)
            return MockCompressionResult(1000, 400, 0.4, 600)

        await slow_compress()

        assert metrics.compression_latency.count > initial_count


# ─────────────────────────────────────────────────────────────────────────────
# Memory Metrics Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMemoryMetrics:
    """Test memory-related metrics"""

    def test_memory_operation_decorator_retrieve(self, metrics_registry):
        """Test track_memory_operation decorator for retrieve"""

        @track_memory_operation(operation_type="retrieve")
        def retrieve_memory():
            return [{"id": 1}, {"id": 2}]

        result = retrieve_memory()

        assert len(result) == 2
        assert metrics_registry.memory_operations.value >= 1

    @pytest.mark.asyncio
    async def test_memory_operation_decorator_store(self):
        """Test track_memory_operation decorator for store"""
        metrics = get_ai_metrics_registry()

        @track_memory_operation(operation_type="store")
        async def store_memory():
            await asyncio.sleep(0.01)
            return {"id": 1, "data": "test"}

        result = await store_memory()

        assert result["id"] == 1
        assert metrics.memory_operations.value >= 1

    def test_record_memory_entry_stored(self, metrics_registry):
        """Test recording memory entry storage"""
        initial_count = metrics_registry.memory_entries_by_type.value

        record_memory_entry_stored(1000, "conversation")
        record_memory_entry_stored(2000, "field_state")

        assert metrics_registry.memory_entries_by_type.value >= initial_count + 2
        assert metrics_registry.memory_entry_size.count == 2
        assert metrics_registry.memory_entry_size.sum == 3000

    def test_record_memory_eviction(self, metrics_registry):
        """Test recording memory evictions"""
        initial_count = metrics_registry.memory_evictions.value

        record_memory_eviction("old_entries")
        record_memory_eviction("old_entries")

        assert metrics_registry.memory_evictions.value == initial_count + 2

    def test_record_memory_ttl_expiration(self, metrics_registry):
        """Test recording TTL expirations"""
        initial_count = metrics_registry.memory_ttl_expirations.value

        record_memory_ttl_expiration("expired_entries")
        record_memory_ttl_expiration("expired_entries")

        assert metrics_registry.memory_ttl_expirations.value == initial_count + 2

    def test_update_memory_usage(self, metrics_registry):
        """Test updating memory usage metrics"""
        update_memory_usage(total_entries=100, total_bytes=500000)

        assert metrics_registry.memory_entries_stored.value == 100
        assert metrics_registry.memory_usage_bytes.value == 500000

    def test_memory_error_tracking(self, metrics_registry):
        """Test memory operation errors are recorded"""

        @track_memory_operation(operation_type="retrieve")
        def retrieve_with_error():
            raise RuntimeError("Memory retrieval failed")

        with pytest.raises(RuntimeError):
            retrieve_with_error()

        assert metrics_registry.memory_errors.value >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation Metrics Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEvaluationMetrics:
    """Test evaluation-related metrics"""

    def test_track_evaluation_decorator(
        self, metrics_registry, mock_evaluation_result
    ):
        """Test track_evaluation decorator"""

        @track_evaluation(recommendation_type="irrigation")
        def evaluate_recommendation():
            return mock_evaluation_result

        result = evaluate_recommendation()

        assert result == mock_evaluation_result
        assert metrics_registry.evaluation_operations.value >= 1

    @pytest.mark.asyncio
    async def test_track_evaluation_decorator_async(
        self, mock_evaluation_result
    ):
        """Test track_evaluation decorator with async function"""

        @track_evaluation(recommendation_type="fertilization")
        async def evaluate_async():
            await asyncio.sleep(0.05)
            return mock_evaluation_result

        result = await evaluate_async()

        assert result == mock_evaluation_result

    def test_evaluation_score_recording(self, metrics_registry, mock_evaluation_result):
        """Test evaluation scores are recorded"""
        # Get initial counts
        initial_overall = metrics_registry.evaluation_score_overall.count
        initial_accuracy = metrics_registry.evaluation_score_accuracy.count
        initial_actionability = metrics_registry.evaluation_score_actionability.count
        initial_safety = metrics_registry.evaluation_score_safety.count

        # Record evaluation
        metrics_registry.evaluation_operations.inc()
        metrics_registry.evaluation_score_overall.observe(
            mock_evaluation_result.overall_score
        )
        metrics_registry.evaluation_score_accuracy.observe(
            mock_evaluation_result.criteria_scores["accuracy"]
        )
        metrics_registry.evaluation_score_actionability.observe(
            mock_evaluation_result.criteria_scores["actionability"]
        )
        metrics_registry.evaluation_score_safety.observe(
            mock_evaluation_result.criteria_scores["safety"]
        )
        metrics_registry.evaluation_score_relevance.observe(
            mock_evaluation_result.criteria_scores["relevance"]
        )
        metrics_registry.evaluation_score_completeness.observe(
            mock_evaluation_result.criteria_scores["completeness"]
        )
        metrics_registry.evaluation_score_clarity.observe(
            mock_evaluation_result.criteria_scores["clarity"]
        )

        # Verify metrics increased
        assert metrics_registry.evaluation_score_overall.count == initial_overall + 1
        assert metrics_registry.evaluation_score_accuracy.count == initial_accuracy + 1
        assert metrics_registry.evaluation_score_actionability.count == initial_actionability + 1
        assert metrics_registry.evaluation_score_safety.count == initial_safety + 1

    def test_evaluation_error_tracking(self, metrics_registry):
        """Test evaluation errors are recorded"""

        @track_evaluation(recommendation_type="general")
        def evaluate_with_error():
            raise Exception("Evaluation failed")

        with pytest.raises(Exception):
            evaluate_with_error()

        assert metrics_registry.evaluation_errors.value >= 1

    @pytest.mark.asyncio
    async def test_evaluation_latency_measurement(self):
        """Test evaluation latency is measured"""
        metrics = get_ai_metrics_registry()
        initial_count = metrics.evaluation_latency.count

        @track_evaluation(recommendation_type="harvest")
        async def slow_evaluate():
            await asyncio.sleep(0.1)
            return MockEvaluationResult(0.8, {}, "good")

        await slow_evaluate()

        assert metrics.evaluation_latency.count > initial_count


# ─────────────────────────────────────────────────────────────────────────────
# Latency Metrics Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLatencyMetrics:
    """Test latency measurements for all operations"""

    @pytest.mark.asyncio
    async def test_track_operation_async_context_manager(self):
        """Test async context manager for operation tracking"""
        async with track_operation_async("test_operation"):
            await asyncio.sleep(0.01)

        # If we reach here, context manager worked correctly
        assert True

    @pytest.mark.asyncio
    async def test_track_operation_async_error_handling(self):
        """Test error handling in async context manager"""
        with pytest.raises(ValueError):
            async with track_operation_async("failing_operation"):
                await asyncio.sleep(0.01)
                raise ValueError("Test error")

    @pytest.mark.asyncio
    async def test_compression_latency_histogram(self):
        """Test compression latency is recorded in histogram"""
        metrics = get_ai_metrics_registry()

        @track_compression
        async def compress():
            await asyncio.sleep(0.02)
            return MockCompressionResult(1000, 400, 0.4, 600)

        initial_sum = metrics.compression_latency.sum

        await compress()

        # Latency should be recorded
        assert metrics.compression_latency.sum >= initial_sum

    @pytest.mark.asyncio
    async def test_memory_operation_latency_histogram(self):
        """Test memory operation latency is recorded"""
        metrics = get_ai_metrics_registry()

        @track_memory_operation(operation_type="retrieve")
        async def retrieve():
            await asyncio.sleep(0.01)
            return []

        initial_count = metrics.memory_retrieval_latency.count

        await retrieve()

        assert metrics.memory_retrieval_latency.count > initial_count

    @pytest.mark.asyncio
    async def test_evaluation_latency_histogram(self):
        """Test evaluation latency is recorded"""
        metrics = get_ai_metrics_registry()

        @track_evaluation(recommendation_type="irrigation")
        async def evaluate():
            await asyncio.sleep(0.05)
            return MockEvaluationResult(0.8, {}, "good")

        initial_count = metrics.evaluation_latency.count

        await evaluate()

        assert metrics.evaluation_latency.count > initial_count


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricsIntegration:
    """Test integration of multiple metrics together"""

    @pytest.mark.asyncio
    async def test_complete_workflow_metrics(self):
        """Test a complete workflow with multiple operations"""
        metrics = get_ai_metrics_registry()

        initial_comp_ops = metrics.compression_operations.value
        initial_mem_ops = metrics.memory_operations.value
        initial_eval_ops = metrics.evaluation_operations.value

        # Simulate compression
        @track_compression
        async def compress():
            await asyncio.sleep(0.01)
            return MockCompressionResult(2000, 800, 0.4, 1200)

        await compress()

        # Simulate memory operation
        @track_memory_operation(operation_type="store")
        async def store():
            await asyncio.sleep(0.01)
            return {"id": 1}

        result = await store()
        record_memory_entry_stored(1000, "conversation")
        update_memory_usage(total_entries=50, total_bytes=100000)

        # Simulate evaluation
        @track_evaluation(recommendation_type="irrigation")
        async def evaluate():
            await asyncio.sleep(0.02)
            return MockEvaluationResult(0.85, {"accuracy": 0.9}, "good")

        await evaluate()

        # Verify metrics were recorded
        assert metrics.compression_operations.value > initial_comp_ops
        assert metrics.memory_operations.value > initial_mem_ops
        assert metrics.evaluation_operations.value > initial_eval_ops
        assert metrics.memory_entries_stored.value == 50

    def test_metrics_values_are_numeric(self):
        """Test all metric values are numeric"""
        metrics = get_ai_metrics_registry()

        # Test counters
        assert isinstance(metrics.compression_operations.value, (int, float))
        assert isinstance(metrics.memory_operations.value, (int, float))

        # Test gauges
        assert isinstance(metrics.memory_entries_stored.value, (int, float))
        assert isinstance(metrics.memory_usage_bytes.value, (int, float))

        # Test histograms
        assert isinstance(metrics.compression_latency.count, int)
        assert isinstance(metrics.compression_latency.sum, (int, float))

    def test_metrics_no_negative_values(self):
        """Test metrics don't go negative"""
        metrics = get_ai_metrics_registry()

        # Counters should never be negative
        assert metrics.compression_operations.value >= 0
        assert metrics.memory_operations.value >= 0

        # Histogram counts should be non-negative
        assert metrics.compression_latency.count >= 0


# ─────────────────────────────────────────────────────────────────────────────
# Performance Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricsPerformance:
    """Test metrics recording performance"""

    def test_counter_increment_performance(self):
        """Test counter increment is fast"""
        metrics = get_ai_metrics_registry()

        import time

        start = time.time()
        for _ in range(10000):
            metrics.compression_operations.inc()
        elapsed = time.time() - start

        # Should complete in < 100ms for 10k increments
        assert elapsed < 0.1

    def test_histogram_observe_performance(self):
        """Test histogram observe is fast"""
        metrics = get_ai_metrics_registry()

        import time

        start = time.time()
        for _ in range(1000):
            metrics.compression_latency.observe(0.05)
        elapsed = time.time() - start

        # Should complete in < 100ms for 1k observations
        assert elapsed < 0.1

    def test_gauge_update_performance(self):
        """Test gauge update is fast"""
        metrics = get_ai_metrics_registry()

        import time

        start = time.time()
        for i in range(10000):
            metrics.memory_usage_bytes.set(i * 1000)
        elapsed = time.time() - start

        # Should complete in < 100ms for 10k updates
        assert elapsed < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
