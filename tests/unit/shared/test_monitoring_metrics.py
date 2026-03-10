"""
Tests for shared/monitoring/metrics.py module
اختبارات وحدة المقاييس للمراقبة
"""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from shared.monitoring.metrics import (
    MetricsRegistry,
    Counter,
    Gauge,
    Histogram,
    get_registry,
    track_db_query,
    track_external_call,
)


class TestCounter:
    """Tests for Counter metric"""

    def test_counter_creation(self):
        """Test creating a counter"""
        data = {"value": 0, "name": "test", "description": "test counter", "labels": {}}
        counter = Counter(data)
        assert counter.value == 0

    def test_counter_increment(self):
        """Test incrementing counter"""
        data = {"value": 0, "name": "test", "description": "test", "labels": {}}
        counter = Counter(data)
        counter.inc()
        assert counter.value == 1
        counter.inc()
        assert counter.value == 2

    def test_counter_increment_by_value(self):
        """Test incrementing counter by specific value"""
        data = {"value": 0, "name": "test", "description": "test", "labels": {}}
        counter = Counter(data)
        counter.inc(5)
        assert counter.value == 5
        counter.inc(3)
        assert counter.value == 8

    def test_counter_increment_float(self):
        """Test incrementing counter by float value"""
        data = {"value": 0, "name": "test", "description": "test", "labels": {}}
        counter = Counter(data)
        counter.inc(0.5)
        assert counter.value == 0.5
        counter.inc(0.5)
        assert counter.value == 1.0


class TestGauge:
    """Tests for Gauge metric"""

    def test_gauge_creation(self):
        """Test creating a gauge"""
        data = {"value": 0, "name": "test", "description": "test gauge", "labels": {}}
        gauge = Gauge(data)
        assert gauge.value == 0

    def test_gauge_set(self):
        """Test setting gauge value"""
        data = {"value": 0, "name": "test", "description": "test", "labels": {}}
        gauge = Gauge(data)
        gauge.set(10)
        assert gauge.value == 10
        gauge.set(5)
        assert gauge.value == 5

    def test_gauge_increment(self):
        """Test incrementing gauge"""
        data = {"value": 0, "name": "test", "description": "test", "labels": {}}
        gauge = Gauge(data)
        gauge.inc()
        assert gauge.value == 1
        gauge.inc(5)
        assert gauge.value == 6

    def test_gauge_decrement(self):
        """Test decrementing gauge"""
        data = {"value": 10, "name": "test", "description": "test", "labels": {}}
        gauge = Gauge(data)
        gauge.dec()
        assert gauge.value == 9
        gauge.dec(4)
        assert gauge.value == 5

    def test_gauge_negative_value(self):
        """Test gauge can go negative"""
        data = {"value": 0, "name": "test", "description": "test", "labels": {}}
        gauge = Gauge(data)
        gauge.dec(5)
        assert gauge.value == -5


class TestHistogram:
    """Tests for Histogram metric"""

    def test_histogram_creation(self):
        """Test creating a histogram"""
        data = {
            "value": 0,
            "name": "test",
            "description": "test histogram",
            "labels": {},
            "buckets": [0.1, 0.5, 1.0],
            "bucket_counts": {0.1: 0, 0.5: 0, 1.0: 0},
            "sum": 0,
            "count": 0,
        }
        histogram = Histogram(data)
        assert histogram.count == 0
        assert histogram.sum == 0

    def test_histogram_observe(self):
        """Test observing values"""
        data = {
            "name": "test",
            "description": "test",
            "labels": {},
            "buckets": [0.1, 0.5, 1.0],
            "bucket_counts": {0.1: 0, 0.5: 0, 1.0: 0},
            "sum": 0,
            "count": 0,
        }
        histogram = Histogram(data)
        histogram.observe(0.05)
        assert histogram.count == 1
        assert histogram.sum == 0.05
        assert data["bucket_counts"][0.1] == 1

    def test_histogram_multiple_observations(self):
        """Test multiple observations"""
        data = {
            "name": "test",
            "description": "test",
            "labels": {},
            "buckets": [0.1, 0.5, 1.0],
            "bucket_counts": {0.1: 0, 0.5: 0, 1.0: 0},
            "sum": 0,
            "count": 0,
        }
        histogram = Histogram(data)
        histogram.observe(0.05)  # Goes to 0.1 bucket
        histogram.observe(0.3)  # Goes to 0.5 bucket
        histogram.observe(0.8)  # Goes to 1.0 bucket
        assert histogram.count == 3
        assert histogram.sum == pytest.approx(1.15)


class TestMetricsRegistry:
    """Tests for MetricsRegistry"""

    def test_registry_creation(self):
        """Test creating a registry"""
        registry = MetricsRegistry(service_name="test_service")
        assert registry.service_name == "test_service"

    def test_registry_default_name(self):
        """Test registry with default service name"""
        registry = MetricsRegistry()
        assert registry.service_name == "sahool"

    def test_create_counter(self):
        """Test creating counter through registry"""
        registry = MetricsRegistry()
        counter = registry.counter("requests_total", "Total requests")
        assert counter.value == 0
        counter.inc()
        assert counter.value == 1

    def test_create_counter_with_labels(self):
        """Test creating counter with labels"""
        registry = MetricsRegistry()
        counter = registry.counter("requests_total", "Total requests", labels={"method": "GET", "path": "/api"})
        counter.inc()
        assert counter.value == 1

    def test_create_gauge(self):
        """Test creating gauge through registry"""
        registry = MetricsRegistry()
        gauge = registry.gauge("active_connections", "Active connections")
        assert gauge.value == 0
        gauge.set(10)
        assert gauge.value == 10

    def test_create_histogram(self):
        """Test creating histogram through registry"""
        registry = MetricsRegistry()
        histogram = registry.histogram("request_duration", "Request duration in seconds")
        histogram.observe(0.1)
        assert histogram.count == 1

    def test_create_histogram_custom_buckets(self):
        """Test creating histogram with custom buckets"""
        registry = MetricsRegistry()
        buckets = [0.01, 0.05, 0.1, 0.5, 1.0]
        histogram = registry.histogram("custom_duration", "Custom duration", buckets=buckets)
        histogram.observe(0.03)
        assert histogram.count == 1

    def test_get_same_counter(self):
        """Test getting the same counter returns same instance"""
        registry = MetricsRegistry()
        counter1 = registry.counter("test", "Test counter")
        counter1.inc(5)
        counter2 = registry.counter("test", "Test counter")
        assert counter2.value == 5

    def test_export_format(self):
        """Test exporting metrics in Prometheus format"""
        registry = MetricsRegistry(service_name="test")
        counter = registry.counter("requests", "Total requests")
        counter.inc(10)

        export = registry.export()
        assert "# HELP test_requests Total requests" in export
        assert "# TYPE test_requests counter" in export
        assert "test_requests 10" in export

    def test_export_with_labels(self):
        """Test exporting metrics with labels"""
        registry = MetricsRegistry(service_name="test")
        counter = registry.counter("requests", "Total requests", labels={"method": "GET"})
        counter.inc()

        export = registry.export()
        assert 'method="GET"' in export

    def test_export_histogram(self):
        """Test exporting histogram metrics"""
        registry = MetricsRegistry(service_name="test")
        histogram = registry.histogram("duration", "Duration", buckets=[0.1, 0.5, 1.0])
        histogram.observe(0.2)
        histogram.observe(0.8)

        export = registry.export()
        assert "test_duration_bucket" in export
        assert "test_duration_sum" in export
        assert "test_duration_count" in export
        assert 'le="0.1"' in export
        assert 'le="+Inf"' in export

    def test_export_includes_uptime(self):
        """Test export includes uptime metric"""
        registry = MetricsRegistry(service_name="test")
        export = registry.export()
        assert "test_uptime_seconds" in export

    def test_format_labels_empty(self):
        """Test formatting empty labels"""
        registry = MetricsRegistry()
        result = registry._format_labels({})
        assert result == ""

    def test_format_labels_single(self):
        """Test formatting single label"""
        registry = MetricsRegistry()
        result = registry._format_labels({"method": "GET"})
        assert result == '{method="GET"}'

    def test_format_labels_multiple(self):
        """Test formatting multiple labels"""
        registry = MetricsRegistry()
        result = registry._format_labels({"method": "GET", "path": "/api"})
        # Labels should be sorted alphabetically
        assert result == '{method="GET",path="/api"}'


class TestGetRegistry:
    """Tests for get_registry function"""

    def test_get_registry_creates_singleton(self):
        """Test get_registry creates singleton"""
        # Reset global registry for test
        import shared.monitoring.metrics as metrics_module

        metrics_module._registry = None

        registry1 = get_registry("test")
        registry2 = get_registry("test")
        assert registry1 is registry2

    def test_get_registry_default_name(self):
        """Test get_registry with default name"""
        import shared.monitoring.metrics as metrics_module

        metrics_module._registry = None

        registry = get_registry()
        assert registry.service_name == "sahool"


class TestTrackDbQuery:
    """Tests for track_db_query decorator"""

    @pytest.mark.asyncio
    async def test_track_successful_query(self):
        """Test tracking successful database query"""
        import shared.monitoring.metrics as metrics_module

        metrics_module._registry = None

        @track_db_query
        async def sample_query():
            return "result"

        result = await sample_query()
        assert result == "result"

    @pytest.mark.asyncio
    async def test_track_failed_query(self):
        """Test tracking failed database query"""
        import shared.monitoring.metrics as metrics_module

        metrics_module._registry = None

        @track_db_query
        async def failing_query():
            raise ValueError("Database error")

        with pytest.raises(ValueError, match="Database error"):
            await failing_query()


class TestTrackExternalCall:
    """Tests for track_external_call decorator"""

    @pytest.mark.asyncio
    async def test_track_successful_call(self):
        """Test tracking successful external call"""
        import shared.monitoring.metrics as metrics_module

        metrics_module._registry = None

        @track_external_call("weather-service")
        async def call_weather_api():
            return {"temp": 25}

        result = await call_weather_api()
        assert result == {"temp": 25}

    @pytest.mark.asyncio
    async def test_track_failed_call(self):
        """Test tracking failed external call"""
        import shared.monitoring.metrics as metrics_module

        metrics_module._registry = None

        @track_external_call("payment-service")
        async def call_payment_api():
            raise ConnectionError("Service unavailable")

        with pytest.raises(ConnectionError, match="Service unavailable"):
            await call_payment_api()

    @pytest.mark.asyncio
    async def test_track_call_with_args(self):
        """Test tracking call with arguments"""
        import shared.monitoring.metrics as metrics_module

        metrics_module._registry = None

        @track_external_call("notification-service")
        async def send_notification(user_id: str, message: str):
            return {"sent": True, "user": user_id}

        result = await send_notification("user123", "Hello")
        assert result["sent"] is True
        assert result["user"] == "user123"


class TestMetricsMakeKey:
    """Tests for _make_key method"""

    def test_make_key_no_labels(self):
        """Test making key without labels"""
        registry = MetricsRegistry()
        key = registry._make_key("test_metric", None)
        assert key == "test_metric{}"

    def test_make_key_with_labels(self):
        """Test making key with labels"""
        registry = MetricsRegistry()
        key = registry._make_key("test_metric", {"env": "prod"})
        assert key == 'test_metric{env="prod"}'

    def test_make_key_multiple_labels_sorted(self):
        """Test making key with multiple labels (sorted)"""
        registry = MetricsRegistry()
        key = registry._make_key("test_metric", {"z": "last", "a": "first"})
        assert key == 'test_metric{a="first",z="last"}'


class TestHistogramBuckets:
    """Tests for histogram bucket behavior"""

    def test_value_in_first_bucket(self):
        """Test value falls in first bucket"""
        data = {
            "name": "test",
            "description": "test",
            "labels": {},
            "buckets": [0.1, 0.5, 1.0],
            "bucket_counts": {0.1: 0, 0.5: 0, 1.0: 0},
            "sum": 0,
            "count": 0,
        }
        histogram = Histogram(data)
        histogram.observe(0.05)
        assert data["bucket_counts"][0.1] == 1
        assert data["bucket_counts"][0.5] == 0
        assert data["bucket_counts"][1.0] == 0

    def test_value_in_middle_bucket(self):
        """Test value falls in middle bucket"""
        data = {
            "name": "test",
            "description": "test",
            "labels": {},
            "buckets": [0.1, 0.5, 1.0],
            "bucket_counts": {0.1: 0, 0.5: 0, 1.0: 0},
            "sum": 0,
            "count": 0,
        }
        histogram = Histogram(data)
        histogram.observe(0.3)
        assert data["bucket_counts"][0.1] == 0
        assert data["bucket_counts"][0.5] == 1
        assert data["bucket_counts"][1.0] == 0

    def test_value_in_last_bucket(self):
        """Test value falls in last bucket"""
        data = {
            "name": "test",
            "description": "test",
            "labels": {},
            "buckets": [0.1, 0.5, 1.0],
            "bucket_counts": {0.1: 0, 0.5: 0, 1.0: 0},
            "sum": 0,
            "count": 0,
        }
        histogram = Histogram(data)
        histogram.observe(0.8)
        assert data["bucket_counts"][0.1] == 0
        assert data["bucket_counts"][0.5] == 0
        assert data["bucket_counts"][1.0] == 1

    def test_value_exceeds_all_buckets(self):
        """Test value exceeds all buckets"""
        data = {
            "name": "test",
            "description": "test",
            "labels": {},
            "buckets": [0.1, 0.5, 1.0],
            "bucket_counts": {0.1: 0, 0.5: 0, 1.0: 0},
            "sum": 0,
            "count": 0,
        }
        histogram = Histogram(data)
        histogram.observe(5.0)
        # Value exceeds all buckets, so it's not counted in any bucket
        # but still counted in sum and count
        assert histogram.count == 1
        assert histogram.sum == 5.0


class TestExportGauge:
    """Tests for gauge export"""

    def test_export_gauge(self):
        """Test exporting gauge metrics"""
        registry = MetricsRegistry(service_name="test")
        gauge = registry.gauge("connections", "Active connections")
        gauge.set(42)

        export = registry.export()
        assert "# HELP test_connections Active connections" in export
        assert "# TYPE test_connections gauge" in export
        assert "test_connections 42" in export

    def test_export_gauge_with_labels(self):
        """Test exporting gauge with labels"""
        registry = MetricsRegistry(service_name="test")
        gauge = registry.gauge("connections", "Active connections", labels={"pool": "main"})
        gauge.set(10)

        export = registry.export()
        assert 'pool="main"' in export


class TestRegistryTimestamp:
    """Tests for registry timestamp in export"""

    def test_export_contains_timestamp(self):
        """Test export contains generation timestamp"""
        registry = MetricsRegistry(service_name="test")
        export = registry.export()
        assert "Generated at" in export

    def test_export_contains_service_header(self):
        """Test export contains service header"""
        registry = MetricsRegistry(service_name="my_service")
        export = registry.export()
        assert "# SAHOOL my_service Metrics" in export
