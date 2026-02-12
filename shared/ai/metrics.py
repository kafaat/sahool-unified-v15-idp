"""
AI Metrics Module for Observability
====================================
وحدة مقاييس الذكاء الاصطناعي للمراقبة

Provides Prometheus-compatible metrics for AI operations including:
- Agent invocation counts and latencies
- LLM provider health and response times
- Token usage and costs
- Safety violation tracking
- Circuit breaker states

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class MetricType(StrEnum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricValue:
    """A metric value with labels."""

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metric_type: MetricType = MetricType.GAUGE

    def to_prometheus(self) -> str:
        """Convert to Prometheus format."""
        label_str = ""
        if self.labels:
            label_parts = [f'{k}="{v}"' for k, v in self.labels.items()]
            label_str = "{" + ",".join(label_parts) + "}"
        return f"{self.name}{label_str} {self.value}"


class AIMetricsCollector:
    """
    Collector for AI-related metrics.

    جامع مقاييس الذكاء الاصطناعي

    Example:
        collector = AIMetricsCollector()

        # Record agent invocation
        collector.record_agent_invocation("field-analyst", latency_ms=1250)

        # Record LLM call
        collector.record_llm_call(
            provider="anthropic",
            model="claude-3-haiku",
            latency_ms=850,
            tokens_input=150,
            tokens_output=80
        )

        # Get Prometheus metrics
        metrics = collector.get_prometheus_metrics()
    """

    def __init__(self, namespace: str = "sahool_ai"):
        """
        Initialize AIMetricsCollector.

        Args:
            namespace: Prefix for all metric names
        """
        self.namespace = namespace

        # Counters
        self._agent_invocations: dict[str, int] = {}
        self._agent_errors: dict[str, int] = {}
        self._llm_calls: dict[str, int] = {}
        self._llm_errors: dict[str, int] = {}
        self._llm_fallbacks: dict[str, int] = {}
        self._safety_violations: dict[str, int] = {}
        self._tokens_input: dict[str, int] = {}
        self._tokens_output: dict[str, int] = {}

        # Gauges
        self._agent_latencies: dict[str, list[float]] = {}
        self._llm_latencies: dict[str, list[float]] = {}
        self._circuit_breaker_states: dict[str, int] = {}  # 0=closed, 1=open, 2=half-open

        # Cost tracking
        self._costs: dict[str, float] = {}

        # Timestamps
        self._last_success: dict[str, datetime] = {}
        self._last_error: dict[str, datetime] = {}

    def record_agent_invocation(
        self,
        agent_id: str,
        latency_ms: float,
        success: bool = True,
        tenant_id: str = "default",
    ) -> None:
        """
        Record an agent invocation.

        تسجيل استدعاء وكيل
        """
        key = f"{agent_id}:{tenant_id}"

        # Increment counter
        self._agent_invocations[key] = self._agent_invocations.get(key, 0) + 1

        # Record latency
        if key not in self._agent_latencies:
            self._agent_latencies[key] = []
        self._agent_latencies[key].append(latency_ms)
        # Keep only last 1000 samples
        if len(self._agent_latencies[key]) > 1000:
            self._agent_latencies[key] = self._agent_latencies[key][-1000:]

        if success:
            self._last_success[key] = datetime.now(UTC)
        else:
            self._agent_errors[key] = self._agent_errors.get(key, 0) + 1
            self._last_error[key] = datetime.now(UTC)

    def record_agent_error(
        self,
        agent_id: str,
        error_type: str = "unknown",
        tenant_id: str = "default",
    ) -> None:
        """
        Record an agent error.

        تسجيل خطأ وكيل
        """
        key = f"{agent_id}:{tenant_id}:{error_type}"
        self._agent_errors[key] = self._agent_errors.get(key, 0) + 1
        self._last_error[f"{agent_id}:{tenant_id}"] = datetime.now(UTC)

    def record_llm_call(
        self,
        provider: str,
        model: str,
        latency_ms: float,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: float = 0.0,
        success: bool = True,
    ) -> None:
        """
        Record an LLM API call.

        تسجيل طلب LLM API
        """
        key = f"{provider}:{model}"

        # Increment counter
        self._llm_calls[key] = self._llm_calls.get(key, 0) + 1

        # Record latency
        if key not in self._llm_latencies:
            self._llm_latencies[key] = []
        self._llm_latencies[key].append(latency_ms)
        if len(self._llm_latencies[key]) > 1000:
            self._llm_latencies[key] = self._llm_latencies[key][-1000:]

        # Record tokens
        self._tokens_input[key] = self._tokens_input.get(key, 0) + tokens_input
        self._tokens_output[key] = self._tokens_output.get(key, 0) + tokens_output

        # Record cost
        self._costs[key] = self._costs.get(key, 0.0) + cost_usd

        if not success:
            self._llm_errors[key] = self._llm_errors.get(key, 0) + 1

    def record_llm_fallback(
        self,
        from_provider: str,
        to_provider: str,
        reason: str = "error",
    ) -> None:
        """
        Record an LLM provider fallback.

        تسجيل انتقال احتياطي لمزود LLM
        """
        key = f"{from_provider}:{to_provider}:{reason}"
        self._llm_fallbacks[key] = self._llm_fallbacks.get(key, 0) + 1

    def record_safety_violation(
        self,
        violation_type: str,
        severity: str = "medium",
        agent_id: str | None = None,
    ) -> None:
        """
        Record a safety violation.

        تسجيل انتهاك أمان
        """
        key = f"{violation_type}:{severity}"
        if agent_id:
            key = f"{agent_id}:{key}"
        self._safety_violations[key] = self._safety_violations.get(key, 0) + 1

    def update_circuit_breaker_state(
        self,
        name: str,
        state: str,  # closed, open, half_open
    ) -> None:
        """
        Update circuit breaker state metric.

        تحديث حالة قاطع الدائرة
        """
        state_value = {"closed": 0, "open": 1, "half_open": 2}.get(state, 0)
        self._circuit_breaker_states[name] = state_value

    def get_agent_stats(self, agent_id: str, tenant_id: str = "default") -> dict[str, Any]:
        """
        Get statistics for an agent.

        الحصول على إحصائيات وكيل
        """
        key = f"{agent_id}:{tenant_id}"
        latencies = self._agent_latencies.get(key, [])

        return {
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "total_invocations": self._agent_invocations.get(key, 0),
            "total_errors": sum(v for k, v in self._agent_errors.items() if k.startswith(f"{agent_id}:{tenant_id}")),
            "latency_p50_ms": self._percentile(latencies, 50),
            "latency_p95_ms": self._percentile(latencies, 95),
            "latency_p99_ms": self._percentile(latencies, 99),
            "latency_avg_ms": sum(latencies) / len(latencies) if latencies else 0,
            "last_success": self._last_success.get(key),
            "last_error": self._last_error.get(key),
        }

    def get_llm_stats(self, provider: str | None = None) -> dict[str, Any]:
        """
        Get statistics for LLM providers.

        الحصول على إحصائيات مزودي LLM
        """
        stats: dict[str, Any] = {
            "total_calls": 0,
            "total_errors": 0,
            "total_fallbacks": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_cost_usd": 0.0,
            "providers": {},
        }

        for key, count in self._llm_calls.items():
            prov, model = key.split(":", 1)
            if provider and prov != provider:
                continue

            stats["total_calls"] += count

            if prov not in stats["providers"]:
                stats["providers"][prov] = {
                    "calls": 0,
                    "errors": 0,
                    "tokens_input": 0,
                    "tokens_output": 0,
                    "cost_usd": 0.0,
                    "models": {},
                }

            stats["providers"][prov]["calls"] += count
            stats["providers"][prov]["errors"] += self._llm_errors.get(key, 0)
            stats["providers"][prov]["tokens_input"] += self._tokens_input.get(key, 0)
            stats["providers"][prov]["tokens_output"] += self._tokens_output.get(key, 0)
            stats["providers"][prov]["cost_usd"] += self._costs.get(key, 0.0)

            latencies = self._llm_latencies.get(key, [])
            stats["providers"][prov]["models"][model] = {
                "calls": count,
                "errors": self._llm_errors.get(key, 0),
                "latency_p50_ms": self._percentile(latencies, 50),
                "latency_p95_ms": self._percentile(latencies, 95),
            }

        # Totals
        stats["total_errors"] = sum(self._llm_errors.values())
        stats["total_fallbacks"] = sum(self._llm_fallbacks.values())
        stats["total_tokens_input"] = sum(self._tokens_input.values())
        stats["total_tokens_output"] = sum(self._tokens_output.values())
        stats["total_cost_usd"] = round(sum(self._costs.values()), 4)

        return stats

    def get_safety_stats(self) -> dict[str, Any]:
        """
        Get safety violation statistics.

        الحصول على إحصائيات انتهاكات الأمان
        """
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}

        for key, count in self._safety_violations.items():
            parts = key.split(":")
            if len(parts) >= 2:
                vtype = parts[-2] if len(parts) > 2 else parts[0]
                severity = parts[-1]
                by_type[vtype] = by_type.get(vtype, 0) + count
                by_severity[severity] = by_severity.get(severity, 0) + count

        return {
            "total_violations": sum(self._safety_violations.values()),
            "by_type": by_type,
            "by_severity": by_severity,
        }

    def get_prometheus_metrics(self) -> str:
        """
        Get all metrics in Prometheus format.

        الحصول على جميع المقاييس بتنسيق Prometheus
        """
        lines: list[str] = []
        ns = self.namespace

        # Agent invocations
        lines.append(f"# HELP {ns}_agent_invocations_total Total agent invocations")
        lines.append(f"# TYPE {ns}_agent_invocations_total counter")
        for key, count in self._agent_invocations.items():
            agent_id, tenant_id = key.split(":", 1)
            lines.append(f'{ns}_agent_invocations_total{{agent_id="{agent_id}",tenant_id="{tenant_id}"}} {count}')

        # Agent errors
        lines.append(f"# HELP {ns}_agent_errors_total Total agent errors")
        lines.append(f"# TYPE {ns}_agent_errors_total counter")
        for key, count in self._agent_errors.items():
            parts = key.split(":")
            agent_id = parts[0]
            tenant_id = parts[1] if len(parts) > 1 else "default"
            error_type = parts[2] if len(parts) > 2 else "unknown"
            lines.append(
                f'{ns}_agent_errors_total{{agent_id="{agent_id}",tenant_id="{tenant_id}",error_type="{error_type}"}} {count}'
            )

        # Agent latencies (p50, p95, p99)
        lines.append(f"# HELP {ns}_agent_latency_ms Agent response latency in milliseconds")
        lines.append(f"# TYPE {ns}_agent_latency_ms gauge")
        for key, latencies in self._agent_latencies.items():
            agent_id, tenant_id = key.split(":", 1)
            for quantile, value in [("0.5", 50), ("0.95", 95), ("0.99", 99)]:
                p = self._percentile(latencies, value)
                lines.append(
                    f'{ns}_agent_latency_ms{{agent_id="{agent_id}",tenant_id="{tenant_id}",quantile="{quantile}"}} {p}'
                )

        # LLM calls
        lines.append(f"# HELP {ns}_llm_calls_total Total LLM API calls")
        lines.append(f"# TYPE {ns}_llm_calls_total counter")
        for key, count in self._llm_calls.items():
            provider, model = key.split(":", 1)
            lines.append(f'{ns}_llm_calls_total{{provider="{provider}",model="{model}"}} {count}')

        # LLM errors
        lines.append(f"# HELP {ns}_llm_errors_total Total LLM API errors")
        lines.append(f"# TYPE {ns}_llm_errors_total counter")
        for key, count in self._llm_errors.items():
            provider, model = key.split(":", 1)
            lines.append(f'{ns}_llm_errors_total{{provider="{provider}",model="{model}"}} {count}')

        # Tokens
        lines.append(f"# HELP {ns}_tokens_total Total tokens used")
        lines.append(f"# TYPE {ns}_tokens_total counter")
        for key, count in self._tokens_input.items():
            provider, model = key.split(":", 1)
            lines.append(f'{ns}_tokens_total{{provider="{provider}",model="{model}",direction="input"}} {count}')
        for key, count in self._tokens_output.items():
            provider, model = key.split(":", 1)
            lines.append(f'{ns}_tokens_total{{provider="{provider}",model="{model}",direction="output"}} {count}')

        # Costs
        lines.append(f"# HELP {ns}_cost_usd_total Total cost in USD")
        lines.append(f"# TYPE {ns}_cost_usd_total counter")
        for key, cost in self._costs.items():
            provider, model = key.split(":", 1)
            lines.append(f'{ns}_cost_usd_total{{provider="{provider}",model="{model}"}} {cost:.6f}')

        # Safety violations
        lines.append(f"# HELP {ns}_safety_violations_total Total safety violations")
        lines.append(f"# TYPE {ns}_safety_violations_total counter")
        for key, count in self._safety_violations.items():
            lines.append(f'{ns}_safety_violations_total{{type="{key}"}} {count}')

        # Circuit breaker states
        lines.append(f"# HELP {ns}_circuit_breaker_state Circuit breaker state (0=closed, 1=open, 2=half_open)")
        lines.append(f"# TYPE {ns}_circuit_breaker_state gauge")
        for name, state in self._circuit_breaker_states.items():
            lines.append(f'{ns}_circuit_breaker_state{{name="{name}"}} {state}')

        return "\n".join(lines)

    def _percentile(self, values: list[float], p: int) -> float:
        """Calculate percentile."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        idx = int(len(sorted_values) * p / 100)
        idx = min(idx, len(sorted_values) - 1)
        return round(sorted_values[idx], 2)

    def reset(self) -> None:
        """Reset all metrics."""
        self._agent_invocations.clear()
        self._agent_errors.clear()
        self._llm_calls.clear()
        self._llm_errors.clear()
        self._llm_fallbacks.clear()
        self._safety_violations.clear()
        self._tokens_input.clear()
        self._tokens_output.clear()
        self._agent_latencies.clear()
        self._llm_latencies.clear()
        self._circuit_breaker_states.clear()
        self._costs.clear()
        self._last_success.clear()
        self._last_error.clear()


# Global metrics collector
_global_collector: AIMetricsCollector | None = None


def get_metrics_collector(namespace: str = "sahool_ai") -> AIMetricsCollector:
    """
    Get or create the global metrics collector.

    الحصول على أو إنشاء جامع المقاييس العالمي
    """
    global _global_collector
    if _global_collector is None:
        _global_collector = AIMetricsCollector(namespace=namespace)
    return _global_collector
