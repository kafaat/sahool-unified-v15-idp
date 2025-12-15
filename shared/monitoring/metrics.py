"""
SAHOOL Prometheus Metrics
Provides standardized metrics for all services
"""

import time
from typing import Callable, Optional
from functools import wraps

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse


class MetricsRegistry:
    """Simple metrics registry for Prometheus format"""

    def __init__(self, service_name: str = "sahool"):
        self.service_name = service_name
        self._counters: dict[str, dict] = {}
        self._gauges: dict[str, dict] = {}
        self._histograms: dict[str, dict] = {}
        self._start_time = time.time()

    def counter(
        self,
        name: str,
        description: str,
        labels: Optional[dict] = None
    ) -> "Counter":
        """Create or get a counter metric"""
        key = self._make_key(name, labels)
        if key not in self._counters:
            self._counters[key] = {
                "name": name,
                "description": description,
                "labels": labels or {},
                "value": 0
            }
        return Counter(self._counters[key])

    def gauge(
        self,
        name: str,
        description: str,
        labels: Optional[dict] = None
    ) -> "Gauge":
        """Create or get a gauge metric"""
        key = self._make_key(name, labels)
        if key not in self._gauges:
            self._gauges[key] = {
                "name": name,
                "description": description,
                "labels": labels or {},
                "value": 0
            }
        return Gauge(self._gauges[key])

    def histogram(
        self,
        name: str,
        description: str,
        buckets: Optional[list[float]] = None,
        labels: Optional[dict] = None
    ) -> "Histogram":
        """Create or get a histogram metric"""
        key = self._make_key(name, labels)
        if key not in self._histograms:
            default_buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            self._histograms[key] = {
                "name": name,
                "description": description,
                "labels": labels or {},
                "buckets": buckets or default_buckets,
                "bucket_counts": {b: 0 for b in (buckets or default_buckets)},
                "sum": 0,
                "count": 0
            }
        return Histogram(self._histograms[key])

    def _make_key(self, name: str, labels: Optional[dict]) -> str:
        """Create unique key for metric"""
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted((labels or {}).items()))
        return f"{name}{{{label_str}}}"

    def _format_labels(self, labels: dict) -> str:
        """Format labels for Prometheus"""
        if not labels:
            return ""
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{{{label_str}}}"

    def export(self) -> str:
        """Export all metrics in Prometheus format"""
        lines = []

        # Add service info
        lines.append(f"# SAHOOL {self.service_name} Metrics")
        lines.append(f"# Generated at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
        lines.append("")

        # Export counters
        for metric in self._counters.values():
            name = f"{self.service_name}_{metric['name']}"
            labels = self._format_labels(metric["labels"])
            lines.append(f"# HELP {name} {metric['description']}")
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name}{labels} {metric['value']}")
            lines.append("")

        # Export gauges
        for metric in self._gauges.values():
            name = f"{self.service_name}_{metric['name']}"
            labels = self._format_labels(metric["labels"])
            lines.append(f"# HELP {name} {metric['description']}")
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name}{labels} {metric['value']}")
            lines.append("")

        # Export histograms
        for metric in self._histograms.values():
            name = f"{self.service_name}_{metric['name']}"
            base_labels = metric["labels"]
            lines.append(f"# HELP {name} {metric['description']}")
            lines.append(f"# TYPE {name} histogram")

            cumulative = 0
            for bucket in sorted(metric["buckets"]):
                cumulative += metric["bucket_counts"].get(bucket, 0)
                bucket_labels = {**base_labels, "le": str(bucket)}
                lines.append(f"{name}_bucket{self._format_labels(bucket_labels)} {cumulative}")

            # +Inf bucket
            inf_labels = {**base_labels, "le": "+Inf"}
            lines.append(f"{name}_bucket{self._format_labels(inf_labels)} {metric['count']}")

            # Sum and count
            lines.append(f"{name}_sum{self._format_labels(base_labels)} {metric['sum']}")
            lines.append(f"{name}_count{self._format_labels(base_labels)} {metric['count']}")
            lines.append("")

        # Add uptime gauge
        uptime = time.time() - self._start_time
        lines.append(f"# HELP {self.service_name}_uptime_seconds Service uptime in seconds")
        lines.append(f"# TYPE {self.service_name}_uptime_seconds gauge")
        lines.append(f"{self.service_name}_uptime_seconds {uptime:.2f}")

        return "\n".join(lines)


class Counter:
    """Counter metric - only increases"""

    def __init__(self, data: dict):
        self._data = data

    def inc(self, value: float = 1):
        """Increment counter"""
        self._data["value"] += value

    @property
    def value(self) -> float:
        return self._data["value"]


class Gauge:
    """Gauge metric - can increase or decrease"""

    def __init__(self, data: dict):
        self._data = data

    def set(self, value: float):
        """Set gauge value"""
        self._data["value"] = value

    def inc(self, value: float = 1):
        """Increment gauge"""
        self._data["value"] += value

    def dec(self, value: float = 1):
        """Decrement gauge"""
        self._data["value"] -= value

    @property
    def value(self) -> float:
        return self._data["value"]


class Histogram:
    """Histogram metric - observes values in buckets"""

    def __init__(self, data: dict):
        self._data = data

    def observe(self, value: float):
        """Record a value"""
        self._data["sum"] += value
        self._data["count"] += 1

        # Find the right bucket
        for bucket in sorted(self._data["buckets"]):
            if value <= bucket:
                self._data["bucket_counts"][bucket] += 1
                break

    @property
    def count(self) -> int:
        return self._data["count"]

    @property
    def sum(self) -> float:
        return self._data["sum"]


# Global registry
_registry: Optional[MetricsRegistry] = None


def get_registry(service_name: str = "sahool") -> MetricsRegistry:
    """Get or create the global metrics registry"""
    global _registry
    if _registry is None:
        _registry = MetricsRegistry(service_name)
    return _registry


def setup_metrics(app: FastAPI, service_name: str = "sahool"):
    """Setup metrics endpoint and middleware for FastAPI app"""
    registry = get_registry(service_name)

    # Create standard metrics
    request_counter = registry.counter(
        "http_requests_total",
        "Total HTTP requests",
        {"service": service_name}
    )

    request_latency = registry.histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        labels={"service": service_name}
    )

    active_requests = registry.gauge(
        "http_requests_active",
        "Currently active HTTP requests",
        {"service": service_name}
    )

    error_counter = registry.counter(
        "http_errors_total",
        "Total HTTP errors",
        {"service": service_name}
    )

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next: Callable) -> Response:
        """Middleware to collect request metrics"""
        # Skip metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.time()
        active_requests.inc()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            request_counter.inc()
            request_latency.observe(duration)

            if response.status_code >= 400:
                error_counter.inc()

            return response
        except Exception as e:
            error_counter.inc()
            raise
        finally:
            active_requests.dec()

    @app.get("/metrics", response_class=PlainTextResponse)
    async def metrics_endpoint():
        """Prometheus metrics endpoint"""
        return registry.export()


def track_db_query(func: Callable):
    """Decorator to track database query metrics"""
    registry = get_registry()

    query_counter = registry.counter(
        "db_queries_total",
        "Total database queries"
    )

    query_latency = registry.histogram(
        "db_query_duration_seconds",
        "Database query latency in seconds"
    )

    query_errors = registry.counter(
        "db_query_errors_total",
        "Total database query errors"
    )

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            query_counter.inc()
            query_latency.observe(time.time() - start_time)
            return result
        except Exception as e:
            query_errors.inc()
            raise

    return wrapper


def track_external_call(service_name: str):
    """Decorator to track external service calls"""
    registry = get_registry()

    call_counter = registry.counter(
        "external_calls_total",
        "Total external service calls",
        {"target": service_name}
    )

    call_latency = registry.histogram(
        "external_call_duration_seconds",
        "External call latency in seconds",
        labels={"target": service_name}
    )

    call_errors = registry.counter(
        "external_call_errors_total",
        "Total external call errors",
        {"target": service_name}
    )

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                call_counter.inc()
                call_latency.observe(time.time() - start_time)
                return result
            except Exception as e:
                call_errors.inc()
                raise

        return wrapper
    return decorator
