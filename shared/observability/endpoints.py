"""
Observability Endpoints for Services
نقاط المراقبة للخدمات

Provides Prometheus metrics and OpenTelemetry integration endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        generate_latest,
        multiprocess,
    )
    from prometheus_client import (
        CollectorRegistry as PrometheusRegistry,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


def create_metrics_router(
    registry: Optional["PrometheusRegistry"] = None,
    include_default_metrics: bool = True,
) -> APIRouter:
    """
    Create a FastAPI router for Prometheus metrics.
    إنشاء موجه FastAPI لمقاييس Prometheus.

    Args:
        registry: Custom Prometheus registry (optional)
        include_default_metrics: Include default Python/process metrics

    Returns:
        APIRouter with /metrics endpoint
    """
    router = APIRouter(tags=["Observability"])

    if not PROMETHEUS_AVAILABLE:

        @router.get("/metrics", summary="Metrics endpoint (unavailable)")
        async def metrics_unavailable():
            """Prometheus client not installed"""
            return PlainTextResponse(
                "# Prometheus client not installed\n"
                "# Install with: pip install prometheus-client\n",
                status_code=200,
            )

        return router

    @router.get("/metrics", summary="Prometheus metrics")
    async def metrics() -> Response:
        """
        Prometheus metrics endpoint.
        نقطة مقاييس Prometheus.

        Returns metrics in Prometheus exposition format.
        """
        if registry:
            metrics_output = generate_latest(registry)
        else:
            # Use default registry
            from prometheus_client import REGISTRY

            metrics_output = generate_latest(REGISTRY)

        return Response(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST,
        )

    return router


def create_observability_router(
    metrics_registry: Optional["PrometheusRegistry"] = None,
) -> APIRouter:
    """
    Create a combined observability router with multiple endpoints.
    إنشاء موجه مراقبة مشترك مع نقاط متعددة.

    Includes:
    - /metrics - Prometheus metrics
    - /debug/vars - Service variables (for debugging)
    - /debug/pprof (future) - Profiling endpoints
    """
    router = APIRouter(tags=["Observability"], prefix="/debug")

    # Add metrics endpoint
    metrics_router = create_metrics_router(metrics_registry)

    # Mount metrics at /metrics (not under /debug)
    standalone_router = APIRouter()
    standalone_router.include_router(metrics_router)

    @router.get("/vars", summary="Service variables")
    async def debug_vars():
        """
        Service variables for debugging.
        متغيرات الخدمة للتصحيح.

        Returns runtime configuration and statistics.
        """
        import os
        import platform
        import sys
        from datetime import datetime

        return {
            "service": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
            },
            "runtime": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "pid": os.getpid(),
            },
            "config": {
                # Only include non-sensitive config
                "cors_origins": os.getenv("CORS_ALLOWED_ORIGINS", ""),
                "database_configured": bool(os.getenv("DATABASE_URL")),
                "redis_configured": bool(os.getenv("REDIS_URL")),
                "nats_configured": bool(os.getenv("NATS_URL")),
            },
        }

    return standalone_router


# OpenTelemetry integration helpers
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


def setup_opentelemetry(
    service_name: str,
    service_version: str,
    otlp_endpoint: str | None = None,
) -> trace.Tracer | None:
    """
    Setup OpenTelemetry tracing.
    إعداد تتبع OpenTelemetry.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        otlp_endpoint: OTLP collector endpoint (e.g., "http://localhost:4317")

    Returns:
        Tracer instance or None if not available
    """
    if not OTEL_AVAILABLE:
        return None

    import os

    # Use environment variable if not provided
    if not otlp_endpoint:
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if not otlp_endpoint:
        # OpenTelemetry not configured
        return None

    # Create resource with service information
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        }
    )

    # Setup trace provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    # Get tracer
    tracer = trace.get_tracer(service_name, service_version)

    return tracer


def instrument_fastapi(app, service_name: str) -> None:
    """
    Instrument a FastAPI application with OpenTelemetry.
    إضافة أدوات OpenTelemetry لتطبيق FastAPI.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
    """
    if not OTEL_AVAILABLE:
        return

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(
        app,
        server_request_hook=None,
        client_request_hook=None,
        excluded_urls="health,metrics",  # Don't trace health/metrics endpoints
    )


# Context propagation helpers
def get_trace_context() -> dict:
    """
    Get current trace context for propagation.
    الحصول على سياق التتبع الحالي للنشر.

    Returns:
        Dictionary with trace context (trace_id, span_id)
    """
    if not OTEL_AVAILABLE:
        return {}

    span = trace.get_current_span()
    if not span or not span.get_span_context().is_valid:
        return {}

    ctx = span.get_span_context()
    return {
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id": format(ctx.span_id, "016x"),
        "trace_flags": format(ctx.trace_flags, "02x"),
    }


def inject_trace_headers(headers: dict) -> dict:
    """
    Inject trace context into HTTP headers.
    حقن سياق التتبع في رؤوس HTTP.

    Args:
        headers: Existing headers dictionary

    Returns:
        Headers with trace context added
    """
    if not OTEL_AVAILABLE:
        return headers

    from opentelemetry.propagate import inject

    # Create a mutable dict
    carrier = dict(headers)

    # Inject trace context
    inject(carrier)

    return carrier


def extract_trace_from_headers(headers: dict) -> trace.SpanContext | None:
    """
    Extract trace context from HTTP headers.
    استخراج سياق التتبع من رؤوس HTTP.

    Args:
        headers: Request headers

    Returns:
        SpanContext or None
    """
    if not OTEL_AVAILABLE:
        return None

    from opentelemetry.context import attach
    from opentelemetry.propagate import extract

    # Extract context from headers
    ctx = extract(headers)

    # Attach to current context
    attach(ctx)

    return trace.get_current_span().get_span_context()
