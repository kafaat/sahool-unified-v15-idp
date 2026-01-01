"""
Metrics Collection for Python Services
جمع المقاييس لخدمات Python

Provides Prometheus-compatible metrics for monitoring.
"""

from typing import Optional, Callable, Any
from functools import wraps
import time
from contextlib import contextmanager

try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Info,
        CollectorRegistry,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class MetricsCollector:
    """
    Metrics collector for service monitoring.
    جامع المقاييس لمراقبة الخدمات.
    """

    def __init__(
        self, service_name: str, registry: Optional["CollectorRegistry"] = None
    ):
        self.service_name = service_name
        self.registry = registry
        self._metrics: dict[str, Any] = {}

        if not PROMETHEUS_AVAILABLE:
            return

        # Default metrics
        self._setup_default_metrics()

    def _setup_default_metrics(self) -> None:
        """Setup default metrics for all services."""
        if not PROMETHEUS_AVAILABLE:
            return

        # Request metrics
        self._metrics["requests_total"] = Counter(
            f"{self.service_name}_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self._metrics["request_duration"] = Histogram(
            f"{self.service_name}_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        # Error metrics
        self._metrics["errors_total"] = Counter(
            f"{self.service_name}_errors_total",
            "Total number of errors",
            ["type", "severity"],
            registry=self.registry,
        )

        # Active connections/workers
        self._metrics["active_connections"] = Gauge(
            f"{self.service_name}_active_connections",
            "Number of active connections",
            registry=self.registry,
        )

        # Service info
        self._metrics["info"] = Info(
            f"{self.service_name}_info",
            "Service information",
            registry=self.registry,
        )

    def record_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
    ) -> None:
        """
        Record a request metric.
        تسجيل مقياس طلب.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["requests_total"].labels(
            method=method,
            endpoint=endpoint,
            status=str(status),
        ).inc()

        self._metrics["request_duration"].labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

    def record_error(self, error_type: str, severity: str = "error") -> None:
        """
        Record an error metric.
        تسجيل مقياس خطأ.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["errors_total"].labels(
            type=error_type,
            severity=severity,
        ).inc()

    def set_active_connections(self, count: int) -> None:
        """
        Set active connections gauge.
        تعيين عداد الاتصالات النشطة.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["active_connections"].set(count)

    def increment_active_connections(self) -> None:
        """Increment active connections."""
        if not PROMETHEUS_AVAILABLE:
            return
        self._metrics["active_connections"].inc()

    def decrement_active_connections(self) -> None:
        """Decrement active connections."""
        if not PROMETHEUS_AVAILABLE:
            return
        self._metrics["active_connections"].dec()

    def set_info(self, version: str, environment: str, **kwargs: str) -> None:
        """
        Set service info.
        تعيين معلومات الخدمة.
        """
        if not PROMETHEUS_AVAILABLE:
            return

        info_dict = {
            "version": version,
            "environment": environment,
            **kwargs,
        }
        self._metrics["info"].info(info_dict)

    def create_counter(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
    ) -> Optional["Counter"]:
        """
        Create a custom counter.
        إنشاء عداد مخصص.
        """
        if not PROMETHEUS_AVAILABLE:
            return None

        full_name = f"{self.service_name}_{name}"
        counter = Counter(
            full_name,
            description,
            labels or [],
            registry=self.registry,
        )
        self._metrics[name] = counter
        return counter

    def create_histogram(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
        buckets: Optional[list[float]] = None,
    ) -> Optional["Histogram"]:
        """
        Create a custom histogram.
        إنشاء مدرج تكراري مخصص.
        """
        if not PROMETHEUS_AVAILABLE:
            return None

        full_name = f"{self.service_name}_{name}"
        histogram = Histogram(
            full_name,
            description,
            labels or [],
            buckets=buckets or Histogram.DEFAULT_BUCKETS,
            registry=self.registry,
        )
        self._metrics[name] = histogram
        return histogram

    def create_gauge(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
    ) -> Optional["Gauge"]:
        """
        Create a custom gauge.
        إنشاء مقياس مخصص.
        """
        if not PROMETHEUS_AVAILABLE:
            return None

        full_name = f"{self.service_name}_{name}"
        gauge = Gauge(
            full_name,
            description,
            labels or [],
            registry=self.registry,
        )
        self._metrics[name] = gauge
        return gauge

    @contextmanager
    def measure_time(self, metric_name: str, labels: Optional[dict[str, str]] = None):
        """
        Context manager to measure execution time.
        مدير سياق لقياس وقت التنفيذ.
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            if PROMETHEUS_AVAILABLE and metric_name in self._metrics:
                metric = self._metrics[metric_name]
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

    def get_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format.
        الحصول على المقاييس بتنسيق Prometheus.
        """
        if not PROMETHEUS_AVAILABLE:
            return b""

        return generate_latest(self.registry)


def timed(
    metric_name: str, labels_func: Optional[Callable[..., dict[str, str]]] = None
):
    """
    Decorator to measure function execution time.
    مزخرف لقياس وقت تنفيذ الدالة.

    Example:
        @timed('process_duration', lambda field_id: {'field_id': field_id})
        def process_field(field_id: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start
                labels = labels_func(*args, **kwargs) if labels_func else {}
                # Log timing (metrics collector would need to be injected)
                # For now, just print in debug mode
                import os

                if os.getenv("DEBUG"):
                    print(f"[TIMING] {metric_name}: {duration:.4f}s {labels}")

        return wrapper

    return decorator


# NDVI-specific metrics
class NDVIMetrics(MetricsCollector):
    """
    NDVI-specific metrics collector.
    جامع مقاييس NDVI.
    """

    def __init__(self, registry: Optional["CollectorRegistry"] = None):
        super().__init__("ndvi_processor", registry)
        self._setup_ndvi_metrics()

    def _setup_ndvi_metrics(self) -> None:
        """Setup NDVI-specific metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["calculations_total"] = Counter(
            "ndvi_calculations_total",
            "Total NDVI calculations",
            ["satellite_source"],
            registry=self.registry,
        )

        self._metrics["calculation_duration"] = Histogram(
            "ndvi_calculation_duration_seconds",
            "NDVI calculation duration",
            ["field_size_category"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry,
        )

        self._metrics["ndvi_values"] = Histogram(
            "ndvi_mean_values",
            "Distribution of mean NDVI values",
            buckets=[-1.0, -0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        self._metrics["anomalies_detected"] = Counter(
            "ndvi_anomalies_detected_total",
            "Total NDVI anomalies detected",
            ["anomaly_type"],
            registry=self.registry,
        )

    def record_calculation(
        self,
        satellite_source: str,
        duration: float,
        field_size_hectares: float,
        mean_ndvi: float,
    ) -> None:
        """Record an NDVI calculation."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["calculations_total"].labels(
            satellite_source=satellite_source,
        ).inc()

        # Categorize field size
        if field_size_hectares < 10:
            size_category = "small"
        elif field_size_hectares < 50:
            size_category = "medium"
        else:
            size_category = "large"

        self._metrics["calculation_duration"].labels(
            field_size_category=size_category,
        ).observe(duration)

        self._metrics["ndvi_values"].observe(mean_ndvi)

    def record_anomaly(self, anomaly_type: str) -> None:
        """Record an NDVI anomaly detection."""
        if not PROMETHEUS_AVAILABLE:
            return

        self._metrics["anomalies_detected"].labels(
            anomaly_type=anomaly_type,
        ).inc()


# AI/Agent-specific metrics
class AgentMetrics(MetricsCollector):
    """
    AI Agent-specific metrics collector.
    جامع مقاييس عامل الذكاء الاصطناعي.

    Tracks:
    - Token usage
    - Model costs
    - Success/failure rates
    - Response times
    - Cache hit rates
    """

    def __init__(
        self,
        service_name: str = "ai_agent",
        registry: Optional["CollectorRegistry"] = None,
    ):
        super().__init__(service_name, registry)
        self._setup_agent_metrics()

    def _setup_agent_metrics(self) -> None:
        """Setup AI agent-specific metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        # Token usage metrics
        self._metrics["tokens_used"] = Counter(
            f"{self.service_name}_tokens_used_total",
            "Total tokens used by agent",
            ["agent_name", "model", "token_type"],
            registry=self.registry,
        )

        # Cost tracking
        self._metrics["cost_usd"] = Counter(
            f"{self.service_name}_cost_usd_total",
            "Total cost in USD",
            ["agent_name", "model"],
            registry=self.registry,
        )

        # Agent calls
        self._metrics["agent_calls"] = Counter(
            f"{self.service_name}_calls_total",
            "Total agent calls",
            ["agent_name", "model", "status"],
            registry=self.registry,
        )

        # Agent response time
        self._metrics["agent_duration"] = Histogram(
            f"{self.service_name}_duration_seconds",
            "Agent call duration in seconds",
            ["agent_name", "model"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0],
            registry=self.registry,
        )

        # Success rate
        self._metrics["agent_success"] = Counter(
            f"{self.service_name}_success_total",
            "Successful agent calls",
            ["agent_name", "model"],
            registry=self.registry,
        )

        self._metrics["agent_failure"] = Counter(
            f"{self.service_name}_failure_total",
            "Failed agent calls",
            ["agent_name", "model", "error_type"],
            registry=self.registry,
        )

        # Cache metrics
        self._metrics["cache_hits"] = Counter(
            f"{self.service_name}_cache_hits_total",
            "Cache hits",
            ["agent_name"],
            registry=self.registry,
        )

        self._metrics["cache_misses"] = Counter(
            f"{self.service_name}_cache_misses_total",
            "Cache misses",
            ["agent_name"],
            registry=self.registry,
        )

        # Token limits and throttling
        self._metrics["rate_limit_hits"] = Counter(
            f"{self.service_name}_rate_limit_hits_total",
            "Rate limit hits",
            ["agent_name", "model"],
            registry=self.registry,
        )

        # Response quality metrics
        self._metrics["response_length"] = Histogram(
            f"{self.service_name}_response_length_chars",
            "Response length in characters",
            ["agent_name", "model"],
            buckets=[100, 500, 1000, 2000, 5000, 10000, 20000],
            registry=self.registry,
        )

    def record_agent_call(
        self,
        agent_name: str,
        model: str,
        duration: float,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        cost: Optional[float] = None,
        success: bool = True,
        error_type: Optional[str] = None,
        response_length: Optional[int] = None,
    ) -> None:
        """
        Record an agent call with all relevant metrics.
        تسجيل استدعاء عامل مع جميع المقاييس ذات الصلة.

        Args:
            agent_name: Name of the agent
            model: Model name (e.g., 'gpt-4', 'claude-3-opus')
            duration: Call duration in seconds
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            total_tokens: Total tokens used
            cost: Cost in USD
            success: Whether the call succeeded
            error_type: Type of error if failed
            response_length: Length of response in characters
        """
        if not PROMETHEUS_AVAILABLE:
            return

        # Record call
        status = "success" if success else "failure"
        self._metrics["agent_calls"].labels(
            agent_name=agent_name,
            model=model,
            status=status,
        ).inc()

        # Record duration
        self._metrics["agent_duration"].labels(
            agent_name=agent_name,
            model=model,
        ).observe(duration)

        # Record tokens
        if prompt_tokens:
            self._metrics["tokens_used"].labels(
                agent_name=agent_name,
                model=model,
                token_type="prompt",
            ).inc(prompt_tokens)

        if completion_tokens:
            self._metrics["tokens_used"].labels(
                agent_name=agent_name,
                model=model,
                token_type="completion",
            ).inc(completion_tokens)

        if total_tokens:
            self._metrics["tokens_used"].labels(
                agent_name=agent_name,
                model=model,
                token_type="total",
            ).inc(total_tokens)

        # Record cost
        if cost:
            self._metrics["cost_usd"].labels(
                agent_name=agent_name,
                model=model,
            ).inc(cost)

        # Record success/failure
        if success:
            self._metrics["agent_success"].labels(
                agent_name=agent_name,
                model=model,
            ).inc()
        else:
            self._metrics["agent_failure"].labels(
                agent_name=agent_name,
                model=model,
                error_type=error_type or "unknown",
            ).inc()

        # Record response length
        if response_length:
            self._metrics["response_length"].labels(
                agent_name=agent_name,
                model=model,
            ).observe(response_length)

    def record_cache_hit(self, agent_name: str) -> None:
        """Record a cache hit."""
        if not PROMETHEUS_AVAILABLE:
            return
        self._metrics["cache_hits"].labels(agent_name=agent_name).inc()

    def record_cache_miss(self, agent_name: str) -> None:
        """Record a cache miss."""
        if not PROMETHEUS_AVAILABLE:
            return
        self._metrics["cache_misses"].labels(agent_name=agent_name).inc()

    def record_rate_limit(self, agent_name: str, model: str) -> None:
        """Record a rate limit hit."""
        if not PROMETHEUS_AVAILABLE:
            return
        self._metrics["rate_limit_hits"].labels(
            agent_name=agent_name,
            model=model,
        ).inc()


class CostTracker:
    """
    Cost tracking utility for AI/LLM services.
    أداة تتبع التكلفة لخدمات الذكاء الاصطناعي/LLM.

    Provides centralized cost calculation based on token usage and model pricing.
    """

    # Pricing per 1K tokens (as of December 2024, in USD)
    MODEL_PRICING = {
        # OpenAI GPT-4
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
        # OpenAI GPT-3.5
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
        "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
        # Anthropic Claude
        "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
        "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
        "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
        "claude-3-5-sonnet": {"prompt": 0.003, "completion": 0.015},
        # Google Gemini
        "gemini-pro": {"prompt": 0.00025, "completion": 0.0005},
        "gemini-ultra": {"prompt": 0.00125, "completion": 0.00375},
        # Default fallback
        "default": {"prompt": 0.001, "completion": 0.002},
    }

    @classmethod
    def calculate_cost(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """
        Calculate cost based on token usage.
        حساب التكلفة بناءً على استخدام الرموز.

        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Cost in USD
        """
        # Normalize model name
        model_key = model.lower()

        # Get pricing or use default
        pricing = cls.MODEL_PRICING.get(model_key, cls.MODEL_PRICING["default"])

        # Calculate cost
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]

        return prompt_cost + completion_cost

    @classmethod
    def update_pricing(
        cls, model: str, prompt_price: float, completion_price: float
    ) -> None:
        """
        Update pricing for a model.
        تحديث الأسعار لنموذج.

        Args:
            model: Model name
            prompt_price: Price per 1K prompt tokens
            completion_price: Price per 1K completion tokens
        """
        cls.MODEL_PRICING[model.lower()] = {
            "prompt": prompt_price,
            "completion": completion_price,
        }
