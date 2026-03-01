"""
SAHOOL Prometheus Metrics
Provides standardized metrics for all services
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

# Conditional import for FastAPI - not required for core metrics functionality
try:
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import PlainTextResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Type hints for when FastAPI is not available
    if TYPE_CHECKING:
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

    def counter(self, name: str, description: str, labels: dict | None = None) -> Counter:
        """Create or get a counter metric"""
        key = self._make_key(name, labels)
        if key not in self._counters:
            self._counters[key] = {
                "name": name,
                "description": description,
                "labels": labels or {},
                "value": 0,
            }
        return Counter(self._counters[key])

    def gauge(self, name: str, description: str, labels: dict | None = None) -> Gauge:
        """Create or get a gauge metric"""
        key = self._make_key(name, labels)
        if key not in self._gauges:
            self._gauges[key] = {
                "name": name,
                "description": description,
                "labels": labels or {},
                "value": 0,
            }
        return Gauge(self._gauges[key])

    def histogram(
        self,
        name: str,
        description: str,
        buckets: list[float] | None = None,
        labels: dict | None = None,
    ) -> Histogram:
        """Create or get a histogram metric"""
        key = self._make_key(name, labels)
        if key not in self._histograms:
            default_buckets = [
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ]
            self._histograms[key] = {
                "name": name,
                "description": description,
                "labels": labels or {},
                "buckets": buckets or default_buckets,
                "bucket_counts": dict.fromkeys(buckets or default_buckets, 0),
                "sum": 0,
                "count": 0,
            }
        return Histogram(self._histograms[key])

    def _make_key(self, name: str, labels: dict | None) -> str:
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
_registry: MetricsRegistry | None = None


def get_registry(service_name: str = "sahool") -> MetricsRegistry:
    """Get or create the global metrics registry"""
    global _registry
    if _registry is None:
        _registry = MetricsRegistry(service_name)
    return _registry


def setup_metrics(app: FastAPI, service_name: str = "sahool"):
    """Setup metrics endpoint and middleware for FastAPI app

    Note: Requires FastAPI to be installed. Will raise RuntimeError if not available.
    """
    if not FASTAPI_AVAILABLE:
        raise RuntimeError(
            "FastAPI is required for setup_metrics(). Install it with: pip install fastapi"
        )

    registry = get_registry(service_name)

    # Create standard metrics
    request_counter = registry.counter(
        "http_requests_total", "Total HTTP requests", {"service": service_name}
    )

    request_latency = registry.histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        labels={"service": service_name},
    )

    active_requests = registry.gauge(
        "http_requests_active",
        "Currently active HTTP requests",
        {"service": service_name},
    )

    error_counter = registry.counter(
        "http_errors_total", "Total HTTP errors", {"service": service_name}
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

            log_level = "debug" if response.status_code < 400 else "warning"
            log_method = getattr(logger, log_level)
            log_method(
                "http_request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                },
            )

            if response.status_code >= 400:
                error_counter.inc()

            return response
        except Exception as e:
            error_counter.inc()
            logger.error(
                "http_request_failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_seconds": time.time() - start_time,
                },
            )
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

    query_counter = registry.counter("db_queries_total", "Total database queries")

    query_latency = registry.histogram(
        "db_query_duration_seconds", "Database query latency in seconds"
    )

    query_errors = registry.counter("db_query_errors_total", "Total database query errors")

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            query_counter.inc()
            duration = time.time() - start_time
            query_latency.observe(duration)
            logger.debug(
                "db_query_completed",
                extra={"function": func.__name__, "duration_seconds": duration},
            )
            return result
        except Exception as e:
            query_errors.inc()
            logger.error(
                "db_query_failed",
                extra={"function": func.__name__, "error": str(e)},
            )
            raise

    return wrapper


def track_external_call(service_name: str):
    """Decorator to track external service calls"""
    registry = get_registry()

    call_counter = registry.counter(
        "external_calls_total", "Total external service calls", {"target": service_name}
    )

    call_latency = registry.histogram(
        "external_call_duration_seconds",
        "External call latency in seconds",
        labels={"target": service_name},
    )

    call_errors = registry.counter(
        "external_call_errors_total",
        "Total external call errors",
        {"target": service_name},
    )

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                call_counter.inc()
                call_latency.observe(time.time() - start_time)
                logger.debug(
                    "external_call_completed",
                    extra={
                        "service": service_name,
                        "duration_seconds": time.time() - start_time,
                    },
                )
                return result
            except Exception as e:
                call_errors.inc()
                logger.error(
                    "external_call_failed",
                    extra={"service": service_name, "error": str(e)},
                )
                raise

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# Database Connection Pool Metrics | مقاييس مجمع اتصالات قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════


class DatabasePoolMetrics:
    """
    Track database connection pool metrics for asyncpg pools.
    تتبع مقاييس مجمع اتصالات قاعدة البيانات لمجمعات asyncpg.

    Captures active connections, idle connections, total pool size,
    and waiting acquires to identify pool exhaustion and connection leaks.

    Usage:
        from shared.monitoring.metrics import DatabasePoolMetrics

        db_pool_metrics = DatabasePoolMetrics(service_name="field-management-service")

        # In a periodic task or health check:
        db_pool_metrics.record_pool_stats(app.state.db_pool)

        # Or use the snapshot helper:
        snapshot = db_pool_metrics.snapshot(app.state.db_pool)
        # snapshot = {"active": 5, "idle": 3, "total": 10, "min": 2, "max": 10, "waiting": 0}
    """

    def __init__(self, service_name: str = "sahool"):
        self._service_name = service_name
        registry = get_registry(service_name)

        self._pool_active = registry.gauge(
            "db_pool_active_connections",
            "Number of currently acquired (in-use) database connections",
            {"service": service_name},
        )
        self._pool_idle = registry.gauge(
            "db_pool_idle_connections",
            "Number of idle (available) database connections in the pool",
            {"service": service_name},
        )
        self._pool_size = registry.gauge(
            "db_pool_total_size",
            "Total number of connections in the pool (active + idle)",
            {"service": service_name},
        )
        self._pool_min = registry.gauge(
            "db_pool_min_size",
            "Configured minimum pool size",
            {"service": service_name},
        )
        self._pool_max = registry.gauge(
            "db_pool_max_size",
            "Configured maximum pool size",
            {"service": service_name},
        )
        self._pool_waiting = registry.gauge(
            "db_pool_waiting_acquires",
            "Number of coroutines waiting to acquire a connection",
            {"service": service_name},
        )

    def record_pool_stats(self, pool) -> None:
        """
        Record current pool statistics from an asyncpg Pool instance.
        تسجيل إحصائيات المجمع الحالية من مثيل asyncpg Pool.

        Args:
            pool: An asyncpg.Pool instance (or any object with get_size(),
                  get_idle_size(), get_min_size(), get_max_size() methods).
                  Safely no-ops if pool is None or methods are unavailable.
        """
        if pool is None:
            return

        try:
            total = pool.get_size() if hasattr(pool, "get_size") else 0
            idle = pool.get_idle_size() if hasattr(pool, "get_idle_size") else 0
            active = total - idle
            min_size = pool.get_min_size() if hasattr(pool, "get_min_size") else 0
            max_size = pool.get_max_size() if hasattr(pool, "get_max_size") else 0

            self._pool_active.set(active)
            self._pool_idle.set(idle)
            self._pool_size.set(total)
            self._pool_min.set(min_size)
            self._pool_max.set(max_size)

            # Some asyncpg versions expose _queue with waiting coroutines
            waiting = 0
            if hasattr(pool, "_queue") and hasattr(pool._queue, "qsize"):
                # _queue.qsize() gives waiting coroutines count on some versions
                waiting = max(0, pool._queue.qsize())
            self._pool_waiting.set(waiting)

            logger.debug(
                "db_pool_stats_recorded",
                extra={
                    "active": active,
                    "idle": idle,
                    "total": total,
                    "min": min_size,
                    "max": max_size,
                    "waiting": waiting,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to record DB pool stats: {e}")

    def snapshot(self, pool) -> dict:
        """
        Return a dict snapshot of pool stats without updating metrics.
        Useful for health check endpoints and diagnostics.

        Args:
            pool: An asyncpg.Pool instance.

        Returns:
            dict with pool statistics, or empty dict if pool is unavailable.
        """
        if pool is None:
            return {}

        try:
            total = pool.get_size() if hasattr(pool, "get_size") else 0
            idle = pool.get_idle_size() if hasattr(pool, "get_idle_size") else 0
            return {
                "active": total - idle,
                "idle": idle,
                "total": total,
                "min": pool.get_min_size() if hasattr(pool, "get_min_size") else 0,
                "max": pool.get_max_size() if hasattr(pool, "get_max_size") else 0,
            }
        except Exception:
            return {}


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Event Metrics | مقاييس أحداث NATS
# ═══════════════════════════════════════════════════════════════════════════════


class NATSEventMetrics:
    """
    Track NATS event publishing and consumption metrics.
    تتبع مقاييس نشر واستهلاك أحداث NATS.

    Provides counters for events published, consumed, and errors,
    plus a histogram for event processing latency. Metrics are labeled
    by subject so operators can identify hot topics and error-prone handlers.

    Usage:
        from shared.monitoring.metrics import NATSEventMetrics

        nats_metrics = NATSEventMetrics(service_name="advisory-service")

        # When publishing:
        nats_metrics.record_published("sahool.field.created")

        # When consuming:
        start = time.time()
        try:
            await handle_event(event)
            nats_metrics.record_consumed("sahool.field.created", time.time() - start)
        except Exception as e:
            nats_metrics.record_error("sahool.field.created", type(e).__name__)
    """

    def __init__(self, service_name: str = "sahool"):
        self._service_name = service_name
        registry = get_registry(service_name)

        self._events_published = registry.counter(
            "nats_events_published_total",
            "Total NATS events published",
            {"service": service_name},
        )
        self._events_consumed = registry.counter(
            "nats_events_consumed_total",
            "Total NATS events consumed and processed successfully",
            {"service": service_name},
        )
        self._event_errors = registry.counter(
            "nats_event_errors_total",
            "Total NATS event processing errors",
            {"service": service_name},
        )
        self._event_processing_latency = registry.histogram(
            "nats_event_processing_duration_seconds",
            "NATS event handler processing time in seconds",
            labels={"service": service_name},
        )
        self._events_retried = registry.counter(
            "nats_events_retried_total",
            "Total NATS events that required retry",
            {"service": service_name},
        )
        self._events_dlq = registry.counter(
            "nats_events_dlq_total",
            "Total NATS events sent to Dead Letter Queue",
            {"service": service_name},
        )

        # Tracking dicts for per-subject breakdowns (logged, not in registry labels
        # to avoid high-cardinality label explosion in Prometheus).
        self._subject_counts: dict[str, int] = {}

    def record_published(self, subject: str) -> None:
        """Record a successfully published event."""
        self._events_published.inc()
        self._subject_counts[subject] = self._subject_counts.get(subject, 0) + 1
        logger.debug("nats_event_published", extra={"subject": subject})

    def record_consumed(self, subject: str, duration_seconds: float = 0.0) -> None:
        """Record a successfully consumed and processed event."""
        self._events_consumed.inc()
        if duration_seconds > 0:
            self._event_processing_latency.observe(duration_seconds)
        logger.debug(
            "nats_event_consumed",
            extra={"subject": subject, "duration_seconds": duration_seconds},
        )

    def record_error(self, subject: str, error_type: str = "unknown") -> None:
        """Record an event processing error."""
        self._event_errors.inc()
        logger.warning(
            "nats_event_error",
            extra={"subject": subject, "error_type": error_type},
        )

    def record_retry(self, subject: str) -> None:
        """Record that an event required retry."""
        self._events_retried.inc()
        logger.debug("nats_event_retried", extra={"subject": subject})

    def record_dlq(self, subject: str) -> None:
        """Record that an event was sent to the Dead Letter Queue."""
        self._events_dlq.inc()
        logger.warning("nats_event_dlq", extra={"subject": subject})

    @property
    def stats(self) -> dict:
        """Return a summary of NATS event metrics for health endpoints."""
        return {
            "events_published": self._events_published.value,
            "events_consumed": self._events_consumed.value,
            "event_errors": self._event_errors.value,
            "events_retried": self._events_retried.value,
            "events_dlq": self._events_dlq.value,
            "processing_latency_count": self._event_processing_latency.count,
            "processing_latency_sum": self._event_processing_latency.sum,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Analytics Endpoint | نقطة تحليلات الأداء
# ═══════════════════════════════════════════════════════════════════════════════


class PerformanceMetrics:
    """
    Aggregated performance metrics for the /api/analytics/performance endpoint.
    مقاييس الأداء المجمعة لنقطة /api/analytics/performance.

    Collects request latency percentiles, error rates, throughput,
    and infrastructure metrics (DB pool, NATS) into a single JSON response.

    Usage:
        from shared.monitoring.metrics import PerformanceMetrics

        perf = PerformanceMetrics(service_name="advisory-service")

        # Register the endpoint on your FastAPI app:
        perf.register_endpoint(app)

        # Or get the data programmatically:
        data = perf.collect(db_pool=app.state.db_pool, nats_client=app.state.nc)
    """

    def __init__(self, service_name: str = "sahool"):
        self._service_name = service_name
        self._start_time = time.time()
        self._db_pool_metrics = DatabasePoolMetrics(service_name)
        self._nats_metrics = NATSEventMetrics(service_name)

    @property
    def db_pool(self) -> DatabasePoolMetrics:
        """Access the database pool metrics instance."""
        return self._db_pool_metrics

    @property
    def nats(self) -> NATSEventMetrics:
        """Access the NATS event metrics instance."""
        return self._nats_metrics

    def collect(self, db_pool=None, nats_client=None) -> dict:
        """
        Collect a performance snapshot.
        جمع لقطة أداء.

        Args:
            db_pool: asyncpg.Pool instance (optional)
            nats_client: NATS client instance (optional)

        Returns:
            dict with performance data suitable for JSON serialization.
        """
        registry = get_registry(self._service_name)
        uptime = time.time() - self._start_time

        result = {
            "service": self._service_name,
            "uptime_seconds": round(uptime, 2),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "http": {
                "total_requests": 0,
                "total_errors": 0,
                "active_requests": 0,
            },
            "database": {},
            "nats": {},
        }

        # Gather HTTP metrics from the registry
        for key, metric in registry._counters.items():
            if "http_requests_total" in metric["name"]:
                result["http"]["total_requests"] = metric["value"]
            elif "http_errors_total" in metric["name"]:
                result["http"]["total_errors"] = metric["value"]

        for key, metric in registry._gauges.items():
            if "http_requests_active" in metric["name"]:
                result["http"]["active_requests"] = metric["value"]

        # Gather histogram stats
        for key, metric in registry._histograms.items():
            if "http_request_duration_seconds" in metric["name"]:
                count = metric["count"]
                total = metric["sum"]
                result["http"]["request_count"] = count
                result["http"]["avg_latency_seconds"] = round(total / count, 4) if count > 0 else 0

        # Database pool snapshot
        if db_pool is not None:
            self._db_pool_metrics.record_pool_stats(db_pool)
            result["database"] = self._db_pool_metrics.snapshot(db_pool)

        # NATS stats
        result["nats"] = self._nats_metrics.stats

        # NATS client connection info
        if nats_client is not None:
            result["nats"]["connected"] = getattr(nats_client, "is_connected", False)

        return result

    def register_endpoint(self, app) -> None:
        """
        Register GET /api/analytics/performance on a FastAPI app.
        تسجيل نقطة GET /api/analytics/performance على تطبيق FastAPI.

        Args:
            app: FastAPI application instance.
        """
        if not FASTAPI_AVAILABLE:
            logger.warning(
                "FastAPI not available; cannot register /api/analytics/performance endpoint"
            )
            return

        @app.get(
            "/api/analytics/performance",
            tags=["Analytics", "التحليلات"],
            summary="Performance analytics | تحليلات الأداء",
        )
        async def performance_analytics():
            """
            Returns aggregated performance metrics including HTTP request stats,
            database connection pool status, and NATS event throughput.

            يرجع مقاييس الأداء المجمعة بما في ذلك إحصائيات طلبات HTTP
            وحالة مجمع اتصالات قاعدة البيانات وإنتاجية أحداث NATS.
            """
            db_pool = getattr(getattr(app, "state", None), "db_pool", None)
            nats_client = getattr(getattr(app, "state", None), "nc", None)
            return self.collect(db_pool=db_pool, nats_client=nats_client)
