"""
SAHOOL Observability - Prometheus Metrics & OpenTelemetry Tracing

Provides pre-configured metrics counters, histograms, and gauges for
SAHOOL microservices, plus OpenTelemetry tracing setup.

Usage (assuming ``packages/platform-bootstrap/src`` is on ``PYTHONPATH``):
    from observability import instrument_fastapi, setup_tracing

    tracer = setup_tracing("my-service")
    instrument_fastapi(app, "my-service")
"""

import asyncio
import time
from datetime import UTC, datetime
from functools import wraps

try:
    from prometheus_client import Counter, Gauge, Histogram, Info

    _HAS_PROMETHEUS = True
except ImportError:
    _HAS_PROMETHEUS = False

# ═══════════════════════════════════════════════════════════════════════════
# Prometheus Metrics
# ═══════════════════════════════════════════════════════════════════════════

if _HAS_PROMETHEUS:
    # Service info
    SERVICE_INFO = Info("sahool_service", "Service information")

    # HTTP requests — avoid high-cardinality labels (endpoint full-path, tenant_id)
    # to prevent unbounded time-series growth that crashes Prometheus.
    HTTP_REQUESTS_TOTAL = Counter(
        "sahool_http_requests_total",
        "Total HTTP requests",
        ["method", "status"],
    )

    HTTP_REQUEST_DURATION = Histogram(
        "sahool_http_request_duration_seconds",
        "HTTP request duration",
        ["method"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )

    # NATS events — tenant_id excluded to avoid cardinality explosion
    NATS_EVENTS_PUBLISHED = Counter(
        "sahool_nats_events_published_total",
        "Events published to NATS",
        ["domain", "action"],
    )

    NATS_EVENTS_CONSUMED = Counter(
        "sahool_nats_events_consumed_total",
        "Events consumed from NATS",
        ["domain", "consumer"],
    )

    NATS_EVENT_PROCESSING_DURATION = Histogram(
        "sahool_nats_event_processing_seconds",
        "Event processing duration",
        ["domain", "action"],
    )

    # Database
    DB_CONNECTIONS_ACTIVE = Gauge(
        "sahool_db_connections_active",
        "Active database connections",
        ["pool_name"],
    )

    DB_QUERY_DURATION = Histogram(
        "sahool_db_query_duration_seconds",
        "Database query duration",
        ["query_type", "table"],
    )

    # Business metrics — tenant_id/field_id excluded to avoid cardinality explosion
    FIELDS_MONITORED = Gauge(
        "sahool_fields_monitored_total",
        "Total fields being monitored",
        ["region"],
    )

    IRRIGATION_COMMANDS = Counter(
        "sahool_irrigation_commands_total",
        "Irrigation commands executed",
        ["status"],
    )

    AI_PREDICTIONS = Counter(
        "sahool_ai_predictions_total",
        "AI predictions generated",
        ["model_type"],
    )


# ═══════════════════════════════════════════════════════════════════════════
# OpenTelemetry Tracing
# ═══════════════════════════════════════════════════════════════════════════


def setup_tracing(service_name: str, otlp_endpoint: str = "http://tempo:4317"):
    """Initialize distributed tracing with OpenTelemetry."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider()
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        return trace.get_tracer(service_name)
    except ImportError:
        return None


def trace_method(operation_name: str):
    """Decorator to trace method execution with OpenTelemetry spans."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                from opentelemetry import trace

                tracer = trace.get_tracer(__name__)
            except ImportError:
                return await func(*args, **kwargs)

            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("function", func.__name__)
                span.set_attribute("module", func.__module__)
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("duration_ms", duration * 1000)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                from opentelemetry import trace

                tracer = trace.get_tracer(__name__)
            except ImportError:
                return func(*args, **kwargs)

            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("function", func.__name__)
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("duration_ms", duration * 1000)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# FastAPI Integration
# ═══════════════════════════════════════════════════════════════════════════


def instrument_fastapi(app, service_name: str):
    """Add Prometheus metrics middleware and health endpoints to a FastAPI app."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        # OpenTelemetry auto-instrumentation is optional; degrade gracefully
        pass

    if _HAS_PROMETHEUS:
        SERVICE_INFO.info({"service": service_name, "version": "16.0.0"})

    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        if _HAS_PROMETHEUS:
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                status=response.status_code,
            ).inc()

            HTTP_REQUEST_DURATION.labels(
                method=request.method,
            ).observe(duration)

        return response

    @app.get("/metrics", tags=["observability"])
    async def prometheus_metrics():
        if not _HAS_PROMETHEUS:
            from starlette.responses import JSONResponse

            return JSONResponse({"error": "prometheus_client not installed"}, status_code=501)
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
        from starlette.responses import Response

        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    @app.get("/health", tags=["observability"])
    async def health():
        return {
            "status": "healthy",
            "service": service_name,
            "version": "16.0.0",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    return app
