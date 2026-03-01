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

.. note:: Preferred Tracing/Observability Package
   This package (``shared.observability``) is the **preferred** module for new
   services that need tracing, metrics, and structured logging. It wraps all
   OpenTelemetry imports in ``try/except`` guards, so services can function
   even if OTel packages are not installed (e.g., lightweight edge services).

   ``shared.telemetry`` provides a similar set of capabilities but requires all
   ``opentelemetry-*`` SDK packages to be present and will fail at import time
   if they are missing. Use ``shared.telemetry`` only when you need low-level
   OTel SDK access (custom samplers, baggage propagation, manual span creation
   with the raw OTel API).

   Both packages can coexist in the same service. They share the global OTel
   TracerProvider, so spans created by either package appear in the same trace.

   A future consolidation effort may merge these into a single package.
"""

# Logging
# Endpoints
from .endpoints import (
    create_metrics_router,
    create_observability_router,
    extract_trace_from_headers,
    get_trace_context,
    inject_trace_headers,
    instrument_fastapi,
    setup_opentelemetry,
)

# Health
from .health import (
    ComponentHealth,
    HealthChecker,
    HealthStatus,
    ServiceHealth,
    check_database,
    check_disk_space,
    check_memory,
    check_nats,
    check_redis,
    create_health_router,
)
from .logging import (
    ColoredFormatter,
    JSONFormatter,
    SensitiveDataMasker,
    ServiceLogger,
    clear_request_context,
    get_logger,
    set_request_context,
    setup_logging,
)

# Metrics
from .metrics import (
    AgentMetrics,
    CostTracker,
    MetricsCollector,
    NDVIMetrics,
    timed,
)

# Middleware
from .middleware import (
    MetricsMiddleware,
    ObservabilityMiddleware,
    RequestLoggingMiddleware,
    setup_observability_middleware,
)

# Tracing
from .tracing import (
    DistributedTracer,
    TracingConfig,
    get_tracer,
    setup_tracing,
    trace_function,
)

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    "set_request_context",
    "clear_request_context",
    "ServiceLogger",
    "SensitiveDataMasker",
    "JSONFormatter",
    "ColoredFormatter",
    # Metrics
    "MetricsCollector",
    "NDVIMetrics",
    "AgentMetrics",
    "CostTracker",
    "timed",
    # Tracing
    "TracingConfig",
    "DistributedTracer",
    "setup_tracing",
    "get_tracer",
    "trace_function",
    # Middleware
    "ObservabilityMiddleware",
    "RequestLoggingMiddleware",
    "MetricsMiddleware",
    "setup_observability_middleware",
    # Health
    "HealthChecker",
    "HealthStatus",
    "ComponentHealth",
    "ServiceHealth",
    "create_health_router",
    "check_database",
    "check_redis",
    "check_nats",
    "check_disk_space",
    "check_memory",
    # Endpoints
    "create_metrics_router",
    "create_observability_router",
    "setup_opentelemetry",
    "instrument_fastapi",
    "get_trace_context",
    "inject_trace_headers",
    "extract_trace_from_headers",
]
