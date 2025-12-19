"""
Observability Module
وحدة المراقبة

Provides logging, metrics, tracing, and health check utilities.
"""

from .logging import (
    setup_logging,
    get_logger,
    set_request_context,
    clear_request_context,
    ServiceLogger,
)

from .metrics import (
    MetricsCollector,
    NDVIMetrics,
    timed,
)

from .health import (
    HealthChecker,
    HealthStatus,
    ComponentHealth,
    ServiceHealth,
    create_health_router,
    check_database,
    check_redis,
    check_nats,
    check_disk_space,
    check_memory,
)

from .endpoints import (
    create_metrics_router,
    create_observability_router,
    setup_opentelemetry,
    instrument_fastapi,
    get_trace_context,
    inject_trace_headers,
    extract_trace_from_headers,
)

__all__ = [
    # Logging
    'setup_logging',
    'get_logger',
    'set_request_context',
    'clear_request_context',
    'ServiceLogger',
    # Metrics
    'MetricsCollector',
    'NDVIMetrics',
    'timed',
    # Health
    'HealthChecker',
    'HealthStatus',
    'ComponentHealth',
    'ServiceHealth',
    'create_health_router',
    'check_database',
    'check_redis',
    'check_nats',
    'check_disk_space',
    'check_memory',
    # Endpoints
    'create_metrics_router',
    'create_observability_router',
    'setup_opentelemetry',
    'instrument_fastapi',
    'get_trace_context',
    'inject_trace_headers',
    'extract_trace_from_headers',
]
