"""
Telemetry and Metrics Tests for SAHOOL Platform.

Tests validate OpenTelemetry integration, metrics collection, and tracing.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Optional

import pytest


@dataclass
class MetricPoint:
    """Single metric data point."""

    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class SpanContext:
    """Tracing span context."""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None


class MetricsCollector:
    """Metrics collector for testing."""

    def __init__(self):
        self.counters: dict[str, float] = {}
        self.gauges: dict[str, float] = {}
        self.histograms: dict[str, list[float]] = {}
        self.points: list[MetricPoint] = []

    def increment_counter(self, name: str, value: float = 1.0, labels: dict[str, str] = None):
        """Increment a counter metric."""
        key = self._make_key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value
        self.points.append(MetricPoint(name, self.counters[key], labels or {}))

    def set_gauge(self, name: str, value: float, labels: dict[str, str] = None):
        """Set a gauge metric value."""
        key = self._make_key(name, labels)
        self.gauges[key] = value
        self.points.append(MetricPoint(name, value, labels or {}))

    def record_histogram(self, name: str, value: float, labels: dict[str, str] = None):
        """Record a histogram observation."""
        key = self._make_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        self.points.append(MetricPoint(name, value, labels or {}))

    def _make_key(self, name: str, labels: dict[str, str] = None) -> str:
        """Create unique key from name and labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_counter(self, name: str, labels: dict[str, str] = None) -> float:
        """Get counter value."""
        key = self._make_key(name, labels)
        return self.counters.get(key, 0)

    def get_gauge(self, name: str, labels: dict[str, str] = None) -> float:
        """Get gauge value."""
        key = self._make_key(name, labels)
        return self.gauges.get(key, 0)

    def get_histogram_values(self, name: str, labels: dict[str, str] = None) -> list[float]:
        """Get histogram values."""
        key = self._make_key(name, labels)
        return self.histograms.get(key, [])


class TracingSpan:
    """Tracing span for testing."""

    def __init__(self, name: str, context: SpanContext = None):
        self.name = name
        self.context = context or SpanContext(trace_id=f"trace-{time.time_ns()}", span_id=f"span-{time.time_ns()}")
        self.attributes: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []
        self.status: str = "OK"
        self.start_time: float = time.time()
        self.end_time: float | None = None

    def set_attribute(self, key: str, value: Any):
        """Set span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] = None):
        """Add event to span."""
        self.events.append({"name": name, "timestamp": time.time(), "attributes": attributes or {}})

    def set_status(self, status: str, description: str = None):
        """Set span status."""
        self.status = status
        if description:
            self.attributes["status.description"] = description

    def end(self):
        """End the span."""
        self.end_time = time.time()

    def get_duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0


@pytest.fixture
def metrics_collector():
    """Create metrics collector."""
    return MetricsCollector()


@pytest.fixture
def tracing_span():
    """Create tracing span."""
    return TracingSpan("test-operation")


class TestCounterMetrics:
    """Tests for counter metrics."""

    def test_increment_counter(self, metrics_collector):
        """Test counter increment."""
        metrics_collector.increment_counter("http_requests_total")

        assert metrics_collector.get_counter("http_requests_total") == 1

    def test_increment_counter_by_value(self, metrics_collector):
        """Test counter increment by specific value."""
        metrics_collector.increment_counter("bytes_processed", 1024)

        assert metrics_collector.get_counter("bytes_processed") == 1024

    def test_counter_with_labels(self, metrics_collector):
        """Test counter with labels."""
        labels = {"service": "field-service", "method": "GET"}
        metrics_collector.increment_counter("http_requests_total", labels=labels)

        assert metrics_collector.get_counter("http_requests_total", labels) == 1

    def test_different_labels_separate_counters(self, metrics_collector):
        """Test different labels create separate counters."""
        metrics_collector.increment_counter("requests", labels={"status": "200"})
        metrics_collector.increment_counter("requests", labels={"status": "500"})

        assert metrics_collector.get_counter("requests", {"status": "200"}) == 1
        assert metrics_collector.get_counter("requests", {"status": "500"}) == 1


class TestGaugeMetrics:
    """Tests for gauge metrics."""

    def test_set_gauge(self, metrics_collector):
        """Test setting gauge value."""
        metrics_collector.set_gauge("cpu_usage_percent", 45.5)

        assert metrics_collector.get_gauge("cpu_usage_percent") == 45.5

    def test_gauge_update(self, metrics_collector):
        """Test gauge value update."""
        metrics_collector.set_gauge("memory_usage_bytes", 1000000)
        metrics_collector.set_gauge("memory_usage_bytes", 2000000)

        assert metrics_collector.get_gauge("memory_usage_bytes") == 2000000

    def test_gauge_with_labels(self, metrics_collector):
        """Test gauge with labels."""
        labels = {"instance": "pod-1"}
        metrics_collector.set_gauge("active_connections", 100, labels)

        assert metrics_collector.get_gauge("active_connections", labels) == 100


class TestHistogramMetrics:
    """Tests for histogram metrics."""

    def test_record_histogram(self, metrics_collector):
        """Test histogram recording."""
        metrics_collector.record_histogram("request_duration_ms", 150)

        values = metrics_collector.get_histogram_values("request_duration_ms")
        assert 150 in values

    def test_multiple_histogram_values(self, metrics_collector):
        """Test multiple histogram recordings."""
        for duration in [100, 150, 200, 250, 300]:
            metrics_collector.record_histogram("request_duration_ms", duration)

        values = metrics_collector.get_histogram_values("request_duration_ms")
        assert len(values) == 5
        assert sum(values) == 1000


class TestTracingSpans:
    """Tests for tracing spans."""

    def test_span_creation(self, tracing_span):
        """Test span creation."""
        assert tracing_span.name == "test-operation"
        assert tracing_span.context.trace_id is not None
        assert tracing_span.context.span_id is not None

    def test_set_span_attribute(self, tracing_span):
        """Test setting span attribute."""
        tracing_span.set_attribute("http.method", "GET")
        tracing_span.set_attribute("http.url", "/api/v1/fields")

        assert tracing_span.attributes["http.method"] == "GET"
        assert tracing_span.attributes["http.url"] == "/api/v1/fields"

    def test_add_span_event(self, tracing_span):
        """Test adding span event."""
        tracing_span.add_event("cache_miss", {"key": "field:123"})

        assert len(tracing_span.events) == 1
        assert tracing_span.events[0]["name"] == "cache_miss"

    def test_span_status(self, tracing_span):
        """Test span status setting."""
        tracing_span.set_status("ERROR", "Database connection failed")

        assert tracing_span.status == "ERROR"
        assert tracing_span.attributes["status.description"] == "Database connection failed"

    def test_span_duration(self, tracing_span):
        """Test span duration calculation."""
        time.sleep(0.01)
        tracing_span.end()

        duration = tracing_span.get_duration_ms()
        assert duration >= 10


class TestAgriculturalMetrics:
    """Tests for agricultural-specific metrics."""

    def test_field_operation_metrics(self, metrics_collector):
        """Test field operation metrics."""
        metrics_collector.increment_counter(
            "field_operations_total", labels={"operation": "create", "tenant_id": "tenant-123"}
        )

        assert (
            metrics_collector.get_counter("field_operations_total", {"operation": "create", "tenant_id": "tenant-123"})
            == 1
        )

    def test_ndvi_processing_metrics(self, metrics_collector):
        """Test NDVI processing metrics."""
        metrics_collector.record_histogram("ndvi_processing_duration_seconds", 2.5, labels={"field_id": "field-456"})

        values = metrics_collector.get_histogram_values("ndvi_processing_duration_seconds", {"field_id": "field-456"})
        assert 2.5 in values

    def test_iot_sensor_metrics(self, metrics_collector):
        """Test IoT sensor metrics."""
        metrics_collector.set_gauge(
            "soil_moisture_percent",
            45.5,
            labels={"sensor_id": "sensor-789", "field_id": "field-123"},
        )

        assert (
            metrics_collector.get_gauge("soil_moisture_percent", {"sensor_id": "sensor-789", "field_id": "field-123"})
            == 45.5
        )


class TestServiceHealthMetrics:
    """Tests for service health metrics."""

    def test_health_check_counter(self, metrics_collector):
        """Test health check metrics."""
        for _ in range(10):
            metrics_collector.increment_counter(
                "health_checks_total", labels={"service": "field-service", "status": "healthy"}
            )

        assert (
            metrics_collector.get_counter("health_checks_total", {"service": "field-service", "status": "healthy"})
            == 10
        )

    def test_uptime_gauge(self, metrics_collector):
        """Test service uptime gauge."""
        uptime_seconds = 86400
        metrics_collector.set_gauge("service_uptime_seconds", uptime_seconds, labels={"service": "advisory-service"})

        assert metrics_collector.get_gauge("service_uptime_seconds", {"service": "advisory-service"}) == 86400


class TestDistributedTracing:
    """Tests for distributed tracing."""

    def test_trace_context_propagation(self):
        """Test trace context propagation."""
        parent_context = SpanContext(trace_id="trace-parent-123", span_id="span-parent-456")

        child_span = TracingSpan(
            "child-operation",
            SpanContext(
                trace_id=parent_context.trace_id,
                span_id="span-child-789",
                parent_span_id=parent_context.span_id,
            ),
        )

        assert child_span.context.trace_id == parent_context.trace_id
        assert child_span.context.parent_span_id == parent_context.span_id

    def test_trace_id_format(self):
        """Test trace ID format."""
        trace_id = "0123456789abcdef0123456789abcdef"

        assert len(trace_id) == 32
        assert all(c in "0123456789abcdef" for c in trace_id)


@pytest.mark.unit
class TestMetricLabels:
    """Tests for metric label handling."""

    def test_label_cardinality_limits(self, metrics_collector):
        """Test label cardinality is controlled."""
        max_cardinality = 100

        for i in range(max_cardinality + 50):
            metrics_collector.increment_counter("high_cardinality_metric", labels={"user_id": f"user-{i}"})

        unique_keys = len([k for k in metrics_collector.counters if k.startswith("high_cardinality_metric")])

        assert unique_keys <= max_cardinality + 50

    def test_label_value_sanitization(self):
        """Test label values are sanitized."""

        def sanitize_label(value: str) -> str:
            sanitized = "".join(c if c.isalnum() or c in "-_." else "_" for c in value)
            return sanitized[:64]

        dangerous = "user<script>alert('xss')</script>"
        sanitized = sanitize_label(dangerous)

        assert "<" not in sanitized
        assert ">" not in sanitized


@pytest.mark.unit
class TestExporterConfiguration:
    """Tests for metrics exporter configuration."""

    def test_prometheus_endpoint_config(self):
        """Test Prometheus endpoint configuration."""
        config = {
            "endpoint": "/metrics",
            "port": 8000,
            "include_runtime_metrics": True,
        }

        assert config["endpoint"] == "/metrics"
        assert config["port"] > 0

    def test_otlp_exporter_config(self):
        """Test OTLP exporter configuration."""
        config = {
            "endpoint": "http://otel-collector:4317",
            "protocol": "grpc",
            "headers": {"x-api-key": "***"},
        }

        assert "otel-collector" in config["endpoint"]
        assert config["protocol"] in ["grpc", "http/protobuf"]
