"""
SAHOOL Performance Monitoring Module
وحدة مراقبة أداء سهول

Comprehensive performance monitoring and metrics collection for the SAHOOL platform.

Features:
- HTTP request tracking and latency monitoring
- Database query performance analysis
- External API call monitoring
- System resource usage tracking
- Prometheus metrics export
- Automatic alerting on threshold violations

Usage:
    Basic monitoring:
    >>> from apps.kernel.common.monitoring import get_monitor
    >>> monitor = get_monitor()
    >>> monitor.track_request("/api/fields", 150.5, 200, "GET")
    >>> summary = monitor.get_metrics_summary(period="1h")

    With Prometheus export:
    >>> from apps.kernel.common.monitoring import setup_prometheus_endpoint
    >>> setup_prometheus_endpoint(app, service_name="field-service")

    Using decorators:
    >>> from apps.kernel.common.monitoring import track_db_operation
    >>> @track_db_operation("SELECT", "fields")
    >>> async def get_field(field_id: int):
    >>>     ...
"""

from .performance_monitor import (
    CircularBuffer,
    MetricPoint,
    PerformanceAlert,
    PerformanceMonitor,
    get_monitor,
)

try:
    from .prometheus_exporter import (
        PrometheusExporter,
        get_exporter,
        setup_prometheus_endpoint,
        track_db_operation,
        track_external_api,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Provide dummy functions when prometheus_client is not installed
    def get_exporter(*args, **kwargs):
        raise ImportError("prometheus_client not installed")

    def setup_prometheus_endpoint(*args, **kwargs):
        raise ImportError("prometheus_client not installed")

    def track_db_operation(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def track_external_api(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    PrometheusExporter = None


__all__ = [
    # Core monitoring
    "PerformanceMonitor",
    "MetricPoint",
    "PerformanceAlert",
    "CircularBuffer",
    "get_monitor",

    # Prometheus integration (if available)
    "PrometheusExporter",
    "get_exporter",
    "setup_prometheus_endpoint",
    "track_db_operation",
    "track_external_api",

    # Feature flag
    "PROMETHEUS_AVAILABLE",
]


__version__ = "1.0.0"
__author__ = "SAHOOL Development Team"
__description__ = "Performance monitoring and metrics collection for SAHOOL platform"
__description_ar__ = "مراقبة الأداء وجمع المقاييس لمنصة سهول"
