"""
Observability Module
وحدة المراقبة

Provides comprehensive observability infrastructure:
- Structured logging with sensitive data masking
- Prometheus metrics collection
- OpenTelemetry distributed tracing
- FastAPI middleware for auto-instrumentation
- Health checks
- Agent-specific metrics and cost tracking
"""

# Logging
from .logging import (
    setup_logging,
    get_logger,
    set_request_context,
    clear_request_context,
    ServiceLogger,
    SensitiveDataMasker,
    JSONFormatter,
    ColoredFormatter,
)

# Metrics
from .metrics import (
    MetricsCollector,
    NDVIMetrics,
    AgentMetrics,
    CostTracker,
    timed,
)

# Tracing
from .tracing import (
    TracingConfig,
    DistributedTracer,
    setup_tracing,
    get_tracer,
    trace_function,
)

# Middleware
from .middleware import (
    ObservabilityMiddleware,
    RequestLoggingMiddleware,
    MetricsMiddleware,
    setup_observability_middleware,
)

# Health
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

# Endpoints
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
    'SensitiveDataMasker',
    'JSONFormatter',
    'ColoredFormatter',

    # Metrics
    'MetricsCollector',
    'NDVIMetrics',
    'AgentMetrics',
    'CostTracker',
    'timed',

    # Tracing
    'TracingConfig',
    'DistributedTracer',
    'setup_tracing',
    'get_tracer',
    'trace_function',

    # Middleware
    'ObservabilityMiddleware',
    'RequestLoggingMiddleware',
    'MetricsMiddleware',
    'setup_observability_middleware',

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
