"""
Tests for AI Metrics Module
============================
اختبارات وحدة مقاييس الذكاء الاصطناعي

Comprehensive tests for Prometheus-compatible metrics collection.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from datetime import datetime

import pytest

from shared.ai.metrics import (
    AIMetricsCollector,
    MetricType,
    MetricValue,
    get_metrics_collector,
)

# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def metrics_collector() -> AIMetricsCollector:
    """Create a fresh metrics collector for testing."""
    return AIMetricsCollector(namespace="test")


# ═══════════════════════════════════════════════════════════════════════════
# Test MetricType Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestMetricType:
    """Tests for MetricType enum."""

    def test_metric_types_exist(self):
        """Test that all expected metric types exist."""
        assert MetricType.COUNTER
        assert MetricType.GAUGE
        assert MetricType.HISTOGRAM
        assert MetricType.SUMMARY

    def test_metric_type_values(self):
        """Test metric type string values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"


# ═══════════════════════════════════════════════════════════════════════════
# Test MetricValue
# ═══════════════════════════════════════════════════════════════════════════


class TestMetricValue:
    """Tests for MetricValue data class."""

    def test_metric_value_creation(self):
        """Test creating a metric value."""
        metric = MetricValue(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE,
            labels={"env": "test"},
            timestamp=datetime.utcnow(),
        )

        assert metric.name == "test_metric"
        assert metric.value == 42.0
        assert metric.metric_type == MetricType.GAUGE
        assert metric.labels["env"] == "test"

    def test_metric_value_to_prometheus(self):
        """Test converting metric to Prometheus format."""
        metric = MetricValue(
            name="request_count",
            value=100.0,
            metric_type=MetricType.COUNTER,
            labels={"service": "api", "method": "GET"},
        )

        prom_str = metric.to_prometheus()

        assert 'request_count{service="api",method="GET"}' in prom_str
        assert "100" in prom_str

    def test_metric_value_without_labels(self):
        """Test metric without labels."""
        metric = MetricValue(
            name="simple_metric",
            value=1.0,
            metric_type=MetricType.GAUGE,
        )

        prom_str = metric.to_prometheus()
        assert "simple_metric" in prom_str


# ═══════════════════════════════════════════════════════════════════════════
# Test AIMetricsCollector
# ═══════════════════════════════════════════════════════════════════════════


class TestAIMetricsCollector:
    """Tests for AIMetricsCollector class."""

    def test_initialization(self, metrics_collector: AIMetricsCollector):
        """Test metrics collector initialization."""
        assert metrics_collector.namespace == "test"

    def test_record_agent_invocation(self, metrics_collector: AIMetricsCollector):
        """Test recording agent invocation."""
        metrics_collector.record_agent_invocation(
            agent_id="test-agent",
            latency_ms=150.5,
            success=True,
            tenant_id="tenant-1",
        )

        # Verify metrics were recorded internally
        key = "test-agent:tenant-1"
        assert metrics_collector._agent_invocations[key] == 1
        assert 150.5 in metrics_collector._agent_latencies[key]

    def test_record_agent_invocation_failure(self, metrics_collector: AIMetricsCollector):
        """Test recording failed agent invocation."""
        metrics_collector.record_agent_invocation(
            agent_id="test-agent",
            latency_ms=50.0,
            success=False,
            tenant_id="tenant-1",
        )

        key = "test-agent:tenant-1"
        assert metrics_collector._agent_invocations[key] == 1
        assert metrics_collector._agent_errors[key] == 1

    def test_record_llm_call(self, metrics_collector: AIMetricsCollector):
        """Test recording LLM call metrics."""
        metrics_collector.record_llm_call(
            provider="anthropic",
            model="claude-3-haiku",
            latency_ms=200.0,
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.0005,
        )

        key = "anthropic:claude-3-haiku"
        assert metrics_collector._llm_calls[key] == 1
        assert metrics_collector._tokens_input[key] == 100
        assert metrics_collector._tokens_output[key] == 50
        assert metrics_collector._costs[key] == pytest.approx(0.0005)

    def test_record_llm_fallback(self, metrics_collector: AIMetricsCollector):
        """Test recording LLM fallback."""
        metrics_collector.record_llm_fallback(
            from_provider="ollama",
            to_provider="anthropic",
            reason="timeout",
        )

        key = "ollama:anthropic:timeout"
        assert metrics_collector._llm_fallbacks[key] == 1

    def test_record_safety_violation(self, metrics_collector: AIMetricsCollector):
        """Test recording safety violation."""
        metrics_collector.record_safety_violation(
            violation_type="prompt_injection",
            severity="high",
            agent_id="test-agent",
        )

        key = "test-agent:prompt_injection:high"
        assert metrics_collector._safety_violations[key] == 1

    def test_update_circuit_breaker_state(self, metrics_collector: AIMetricsCollector):
        """Test updating circuit breaker state."""
        metrics_collector.update_circuit_breaker_state(
            name="ollama",
            state="open",
        )

        assert metrics_collector._circuit_breaker_states["ollama"] == 1  # 1 = open

    def test_get_prometheus_metrics(self, metrics_collector: AIMetricsCollector):
        """Test getting Prometheus-formatted metrics."""
        metrics_collector.record_agent_invocation(
            agent_id="test",
            latency_ms=100,
            success=True,
        )

        prom_output = metrics_collector.get_prometheus_metrics()

        assert isinstance(prom_output, str)


# ═══════════════════════════════════════════════════════════════════════════
# Test Module Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_metrics_collector_singleton(self):
        """Test that get_metrics_collector returns consistent collector."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        assert collector1 is collector2

    def test_get_metrics_collector_default_namespace(self):
        """Test default namespace for metrics collector."""
        collector = get_metrics_collector()

        assert collector.namespace == "sahool_ai"


# ═══════════════════════════════════════════════════════════════════════════
# Test Aggregation
# ═══════════════════════════════════════════════════════════════════════════


class TestAggregation:
    """Tests for metrics aggregation."""

    def test_multiple_agents_tracked(self, metrics_collector: AIMetricsCollector):
        """Test that different agents are tracked separately."""
        metrics_collector.record_agent_invocation(
            agent_id="agent-a",
            latency_ms=100,
            success=True,
        )
        metrics_collector.record_agent_invocation(
            agent_id="agent-b",
            latency_ms=200,
            success=True,
        )

        # Should track both agents separately
        assert metrics_collector._agent_invocations["agent-a:default"] == 1
        assert metrics_collector._agent_invocations["agent-b:default"] == 1
        assert metrics_collector._agent_latencies["agent-a:default"] == [100]
        assert metrics_collector._agent_latencies["agent-b:default"] == [200]

    def test_provider_metrics_aggregation(self, metrics_collector: AIMetricsCollector):
        """Test metrics aggregation by provider."""
        # Record calls to different providers
        metrics_collector.record_llm_call(
            provider="anthropic",
            model="claude-3-haiku",
            latency_ms=100,
            tokens_input=50,
            tokens_output=25,
            cost_usd=0.001,
        )
        metrics_collector.record_llm_call(
            provider="ollama",
            model="codellama:7b",
            latency_ms=200,
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.0,
        )

        # Verify both providers tracked separately
        assert metrics_collector._llm_calls["anthropic:claude-3-haiku"] == 1
        assert metrics_collector._llm_calls["ollama:codellama:7b"] == 1
        assert metrics_collector._tokens_input["anthropic:claude-3-haiku"] == 50
        assert metrics_collector._tokens_input["ollama:codellama:7b"] == 100


# ═══════════════════════════════════════════════════════════════════════════
# Test Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero_latency(self, metrics_collector: AIMetricsCollector):
        """Test recording zero latency."""
        metrics_collector.record_agent_invocation(
            agent_id="fast-agent",
            latency_ms=0.0,
            success=True,
        )

        key = "fast-agent:default"
        assert metrics_collector._agent_invocations[key] == 1
        assert 0.0 in metrics_collector._agent_latencies[key]

    def test_very_large_values(self, metrics_collector: AIMetricsCollector):
        """Test recording very large values."""
        metrics_collector.record_llm_call(
            provider="anthropic",
            model="claude-3-opus",
            latency_ms=1_000_000.0,
            tokens_input=1_000_000,
            tokens_output=500_000,
            cost_usd=10_000.0,
        )

        key = "anthropic:claude-3-opus"
        assert metrics_collector._llm_calls[key] == 1
        assert metrics_collector._tokens_input[key] == 1_000_000
        assert metrics_collector._tokens_output[key] == 500_000
        assert metrics_collector._costs[key] == pytest.approx(10_000.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
