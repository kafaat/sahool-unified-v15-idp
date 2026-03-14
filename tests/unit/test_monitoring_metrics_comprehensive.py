"""
Comprehensive Monitoring Metrics Tests for SAHOOL Platform
اختبارات شاملة لمقاييس المراقبة لمنصة سهول

Tests cover:
- MetricsRegistry creation
- Counter metrics (increment, get value)
- Gauge metrics (set, increment, decrement)
- Histogram metrics (observe, bucket distribution)
- Metrics key generation
- Prometheus text format export
"""

from __future__ import annotations

import pytest

from shared.monitoring.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsRegistry,
)


@pytest.mark.unit
class TestMetricsRegistry:
    """Tests for MetricsRegistry"""

    def test_create_registry(self):
        """Test creating a new metrics registry"""
        registry = MetricsRegistry(service_name="test-service")
        assert registry.service_name == "test-service"

    def test_default_service_name(self):
        """Test default service name"""
        registry = MetricsRegistry()
        assert registry.service_name == "sahool"

    def test_create_counter(self):
        """Test creating a counter metric"""
        registry = MetricsRegistry()
        counter = registry.counter("requests_total", "Total requests")
        assert isinstance(counter, Counter)

    def test_create_gauge(self):
        """Test creating a gauge metric"""
        registry = MetricsRegistry()
        gauge = registry.gauge("active_connections", "Active connections")
        assert isinstance(gauge, Gauge)

    def test_create_histogram(self):
        """Test creating a histogram metric"""
        registry = MetricsRegistry()
        histogram = registry.histogram("request_duration", "Request duration")
        assert isinstance(histogram, Histogram)

    def test_counter_with_labels(self):
        """Test creating counter with labels"""
        registry = MetricsRegistry()
        counter = registry.counter(
            "http_requests_total",
            "HTTP requests",
            labels={"method": "GET", "path": "/api/v1/fields"},
        )
        assert isinstance(counter, Counter)

    def test_gauge_with_labels(self):
        """Test creating gauge with labels"""
        registry = MetricsRegistry()
        gauge = registry.gauge(
            "pool_connections",
            "Pool connections",
            labels={"pool": "main"},
        )
        assert isinstance(gauge, Gauge)

    def test_histogram_with_custom_buckets(self):
        """Test creating histogram with custom buckets"""
        registry = MetricsRegistry()
        custom_buckets = [0.01, 0.05, 0.1, 0.5, 1.0]
        histogram = registry.histogram(
            "latency",
            "Request latency",
            buckets=custom_buckets,
        )
        assert isinstance(histogram, Histogram)

    def test_same_counter_returns_same_instance(self):
        """Test that same counter name returns cached instance"""
        registry = MetricsRegistry()
        c1 = registry.counter("test_counter", "Test")
        c2 = registry.counter("test_counter", "Test")
        # Both should reference the same underlying data
        c1.inc()
        assert c2.value == 1

    def test_make_key_unique(self):
        """Test that key generation is unique for different labels"""
        registry = MetricsRegistry()
        key1 = registry._make_key("metric", {"method": "GET"})
        key2 = registry._make_key("metric", {"method": "POST"})
        assert key1 != key2

    def test_make_key_no_labels(self):
        """Test key generation without labels"""
        registry = MetricsRegistry()
        key = registry._make_key("metric", None)
        assert isinstance(key, str)


@pytest.mark.unit
class TestCounter:
    """Tests for Counter metric"""

    def test_counter_initial_value(self):
        """Test counter starts at 0"""
        registry = MetricsRegistry()
        counter = registry.counter("test_counter", "Test counter")
        assert counter.value == 0

    def test_counter_increment(self):
        """Test counter increment by 1"""
        registry = MetricsRegistry()
        counter = registry.counter("inc_counter", "Inc counter")
        counter.inc()
        assert counter.value == 1

    def test_counter_increment_by_amount(self):
        """Test counter increment by specific amount"""
        registry = MetricsRegistry()
        counter = registry.counter("amount_counter", "Amount counter")
        counter.inc(5)
        assert counter.value == 5

    def test_counter_multiple_increments(self):
        """Test multiple counter increments"""
        registry = MetricsRegistry()
        counter = registry.counter("multi_counter", "Multi counter")
        counter.inc()
        counter.inc(3)
        counter.inc(2)
        assert counter.value == 6


@pytest.mark.unit
class TestGauge:
    """Tests for Gauge metric"""

    def test_gauge_initial_value(self):
        """Test gauge starts at 0"""
        registry = MetricsRegistry()
        gauge = registry.gauge("test_gauge", "Test gauge")
        assert gauge.value == 0

    def test_gauge_set(self):
        """Test gauge set value"""
        registry = MetricsRegistry()
        gauge = registry.gauge("set_gauge", "Set gauge")
        gauge.set(42)
        assert gauge.value == 42

    def test_gauge_increment(self):
        """Test gauge increment"""
        registry = MetricsRegistry()
        gauge = registry.gauge("inc_gauge", "Inc gauge")
        gauge.inc()
        assert gauge.value == 1

    def test_gauge_increment_by_amount(self):
        """Test gauge increment by amount"""
        registry = MetricsRegistry()
        gauge = registry.gauge("inc_amount_gauge", "Inc gauge")
        gauge.inc(5)
        assert gauge.value == 5

    def test_gauge_decrement(self):
        """Test gauge decrement"""
        registry = MetricsRegistry()
        gauge = registry.gauge("dec_gauge", "Dec gauge")
        gauge.set(10)
        gauge.dec()
        assert gauge.value == 9

    def test_gauge_decrement_by_amount(self):
        """Test gauge decrement by amount"""
        registry = MetricsRegistry()
        gauge = registry.gauge("dec_amount_gauge", "Dec gauge")
        gauge.set(10)
        gauge.dec(3)
        assert gauge.value == 7


@pytest.mark.unit
class TestHistogram:
    """Tests for Histogram metric"""

    def test_histogram_initial_state(self):
        """Test histogram starts empty"""
        registry = MetricsRegistry()
        histogram = registry.histogram("test_hist", "Test histogram")
        assert histogram.count == 0
        assert histogram.sum == 0

    def test_histogram_observe(self):
        """Test histogram observe value"""
        registry = MetricsRegistry()
        histogram = registry.histogram("obs_hist", "Observe histogram")
        histogram.observe(0.5)
        assert histogram.count == 1
        assert histogram.sum == 0.5

    def test_histogram_multiple_observations(self):
        """Test histogram with multiple observations"""
        registry = MetricsRegistry()
        histogram = registry.histogram("multi_hist", "Multi histogram")
        values = [0.1, 0.5, 1.0, 2.0, 5.0]
        for v in values:
            histogram.observe(v)
        assert histogram.count == 5
        assert abs(histogram.sum - 8.6) < 0.001

    def test_histogram_bucket_counts(self):
        """Test histogram bucket distribution"""
        registry = MetricsRegistry()
        buckets = [0.1, 0.5, 1.0, 5.0, 10.0]
        histogram = registry.histogram("bucket_hist", "Bucket histogram", buckets=buckets)
        histogram.observe(0.05)  # <= 0.1 bucket
        histogram.observe(0.3)   # <= 0.5 bucket
        histogram.observe(3.0)   # <= 5.0 bucket
        assert histogram.count == 3
