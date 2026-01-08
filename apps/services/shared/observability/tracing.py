"""
Distributed Tracing with OpenTelemetry
التتبع الموزع باستخدام OpenTelemetry

Provides comprehensive distributed tracing following Google Cloud best practices.
"""

import logging
import os
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any, Optional

try:
    from opentelemetry import trace
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.cloud_trace_propagator import (
        CloudTraceFormatPropagator,
    )
    from opentelemetry.propagators.composite import CompositeHTTPPropagator
    from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )
    from opentelemetry.trace import SpanKind, Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None


logger = logging.getLogger(__name__)


class TracingConfig:
    """
    Tracing configuration.
    إعدادات التتبع.
    """

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str | None = None,
        gcp_project_id: str | None = None,
        otlp_endpoint: str | None = None,
        sample_rate: float = 1.0,
        enable_console_export: bool = False,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.gcp_project_id = gcp_project_id or os.getenv("GCP_PROJECT_ID")
        self.otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        self.sample_rate = float(os.getenv("OTEL_SAMPLE_RATE", str(sample_rate)))
        self.enable_console_export = (
            enable_console_export or os.getenv("OTEL_CONSOLE_EXPORT", "false").lower() == "true"
        )

        # Additional service attributes
        self.service_namespace = os.getenv("SERVICE_NAMESPACE", "sahool")
        self.service_instance_id = os.getenv("HOSTNAME", os.getenv("POD_NAME", "unknown"))
        self.deployment_environment = os.getenv("DEPLOYMENT_ENV", self.environment)


class DistributedTracer:
    """
    Distributed tracer with OpenTelemetry.
    تتبع موزع مع OpenTelemetry.

    Provides comprehensive tracing capabilities following Google Cloud best practices:
    - Automatic context propagation
    - Custom span attributes
    - Agent call tracking
    - Token usage tracking
    - Error tracking
    """

    def __init__(self, config: TracingConfig):
        if not OTEL_AVAILABLE:
            logger.warning("OpenTelemetry not available. Tracing will be disabled.")
            self.tracer = None
            self.enabled = False
            return

        self.config = config
        self.enabled = True
        self._setup_tracing()

    def _setup_tracing(self) -> None:
        """Setup OpenTelemetry tracing with exporters."""
        if not OTEL_AVAILABLE:
            return

        # Create resource with service information
        resource = Resource.create(
            {
                SERVICE_NAME: self.config.service_name,
                SERVICE_VERSION: self.config.service_version,
                "service.namespace": self.config.service_namespace,
                "service.instance.id": self.config.service_instance_id,
                "deployment.environment": self.config.deployment_environment,
            }
        )

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Add exporters
        self._add_exporters(provider)

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Setup context propagation for Google Cloud
        self._setup_propagation()

        # Get tracer
        self.tracer = trace.get_tracer(
            self.config.service_name,
            self.config.service_version,
        )

        logger.info(
            f"OpenTelemetry tracing initialized for {self.config.service_name} "
            f"v{self.config.service_version}"
        )

    def _add_exporters(self, provider: "TracerProvider") -> None:
        """Add span exporters based on configuration."""
        if not OTEL_AVAILABLE:
            return

        # Google Cloud Trace exporter (preferred for GCP)
        if self.config.gcp_project_id:
            try:
                cloud_trace_exporter = CloudTraceSpanExporter(
                    project_id=self.config.gcp_project_id,
                )
                provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
                logger.info(
                    f"Google Cloud Trace exporter enabled for project: {self.config.gcp_project_id}"
                )
            except Exception as e:
                logger.warning(f"Failed to setup Google Cloud Trace exporter: {e}")

        # OTLP exporter (for custom collectors or other backends)
        if self.config.otlp_endpoint:
            try:
                otlp_exporter = OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                logger.info(f"OTLP exporter enabled: {self.config.otlp_endpoint}")
            except Exception as e:
                logger.warning(f"Failed to setup OTLP exporter: {e}")

        # Console exporter (for development/debugging)
        if self.config.enable_console_export:
            console_exporter = ConsoleSpanExporter()
            provider.add_span_processor(BatchSpanProcessor(console_exporter))
            logger.info("Console trace exporter enabled")

    def _setup_propagation(self) -> None:
        """Setup context propagation for distributed tracing."""
        if not OTEL_AVAILABLE:
            return

        # Support both W3C Trace Context and Google Cloud Trace format
        set_global_textmap(
            CompositeHTTPPropagator(
                [
                    TraceContextTextMapPropagator(),
                    CloudTraceFormatPropagator(),
                    W3CBaggagePropagator(),
                ]
            )
        )

    def instrument_fastapi(self, app) -> None:
        """
        Instrument FastAPI application.
        إضافة أدوات FastAPI.
        """
        if not self.enabled or not OTEL_AVAILABLE:
            return

        try:
            FastAPIInstrumentor.instrument_app(
                app,
                excluded_urls="health,metrics,/health,/metrics",
            )
            logger.info("FastAPI instrumentation enabled")
        except Exception as e:
            logger.error(f"Failed to instrument FastAPI: {e}")

    def instrument_libraries(self) -> None:
        """
        Auto-instrument common libraries.
        إضافة أدوات المكتبات الشائعة.
        """
        if not self.enabled or not OTEL_AVAILABLE:
            return

        # Instrument HTTPX (for HTTP client calls)
        try:
            HTTPXClientInstrumentor().instrument()
            logger.info("HTTPX instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument HTTPX: {e}")

        # Instrument Redis
        try:
            RedisInstrumentor().instrument()
            logger.info("Redis instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument Redis: {e}")

        # Instrument AsyncPG (PostgreSQL)
        try:
            AsyncPGInstrumentor().instrument()
            logger.info("AsyncPG instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument AsyncPG: {e}")

    @contextmanager
    def span(
        self,
        name: str,
        kind: Optional["SpanKind"] = None,
        attributes: dict[str, Any] | None = None,
    ):
        """
        Create a custom span.
        إنشاء نطاق مخصص.

        Usage:
            with tracer.span("process_field", attributes={"field_id": field_id}):
                # Your code here
                pass
        """
        if not self.enabled or not self.tracer:
            yield None
            return

        span_kind = kind or SpanKind.INTERNAL

        with self.tracer.start_as_current_span(
            name,
            kind=span_kind,
            attributes=attributes or {},
        ) as span:
            try:
                yield span
            except Exception as e:
                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise

    def trace_agent_call(
        self,
        agent_name: str,
        model: str,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
        cost: float | None = None,
    ):
        """
        Decorator to trace AI agent calls.
        مزخرف لتتبع استدعاءات عامل الذكاء الاصطناعي.

        Usage:
            @tracer.trace_agent_call("crop_advisor", "gpt-4")
            async def get_crop_advice(field_id: str):
                # Your agent code
                pass
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.enabled or not self.tracer:
                    return await func(*args, **kwargs)

                with self.tracer.start_as_current_span(
                    f"agent.{agent_name}",
                    kind=SpanKind.INTERNAL,
                ) as span:
                    # Set agent attributes
                    span.set_attribute("agent.name", agent_name)
                    span.set_attribute("agent.model", model)
                    span.set_attribute("agent.type", "llm")

                    # Set token usage if provided
                    if prompt_tokens:
                        span.set_attribute("agent.tokens.prompt", prompt_tokens)
                    if completion_tokens:
                        span.set_attribute("agent.tokens.completion", completion_tokens)
                    if total_tokens:
                        span.set_attribute("agent.tokens.total", total_tokens)
                    if cost:
                        span.set_attribute("agent.cost.usd", cost)

                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.enabled or not self.tracer:
                    return func(*args, **kwargs)

                with self.tracer.start_as_current_span(
                    f"agent.{agent_name}",
                    kind=SpanKind.INTERNAL,
                ) as span:
                    # Set agent attributes
                    span.set_attribute("agent.name", agent_name)
                    span.set_attribute("agent.model", model)
                    span.set_attribute("agent.type", "llm")

                    if prompt_tokens:
                        span.set_attribute("agent.tokens.prompt", prompt_tokens)
                    if completion_tokens:
                        span.set_attribute("agent.tokens.completion", completion_tokens)
                    if total_tokens:
                        span.set_attribute("agent.tokens.total", total_tokens)
                    if cost:
                        span.set_attribute("agent.cost.usd", cost)

                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise

            # Return appropriate wrapper based on function type
            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def get_trace_context(self) -> dict[str, str]:
        """
        Get current trace context for propagation.
        الحصول على سياق التتبع الحالي.

        Returns:
            Dictionary with trace context
        """
        if not self.enabled or not OTEL_AVAILABLE:
            return {}

        span = trace.get_current_span()
        if not span or not span.get_span_context().is_valid:
            return {}

        ctx = span.get_span_context()
        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
            "trace_flags": format(ctx.trace_flags, "02x"),
            "trace_state": str(ctx.trace_state),
        }

    def add_span_attributes(self, **attributes: Any) -> None:
        """
        Add attributes to current span.
        إضافة سمات إلى النطاق الحالي.
        """
        if not self.enabled or not OTEL_AVAILABLE:
            return

        span = trace.get_current_span()
        if span and span.is_recording():
            for key, value in attributes.items():
                # Convert to supported types
                if isinstance(value, str | int | float | bool):
                    span.set_attribute(key, value)
                elif isinstance(value, list | tuple):
                    # OpenTelemetry supports lists of homogeneous types
                    if value and isinstance(value[0], str | int | float | bool):
                        span.set_attribute(key, list(value))
                else:
                    # Convert complex types to string
                    span.set_attribute(key, str(value))

    def add_span_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """
        Add an event to current span.
        إضافة حدث إلى النطاق الحالي.
        """
        if not self.enabled or not OTEL_AVAILABLE:
            return

        span = trace.get_current_span()
        if span and span.is_recording():
            span.add_event(name, attributes=attributes or {})

    def set_span_error(self, error: Exception) -> None:
        """
        Mark current span as error.
        وضع علامة على النطاق الحالي كخطأ.
        """
        if not self.enabled or not OTEL_AVAILABLE:
            return

        span = trace.get_current_span()
        if span and span.is_recording():
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.record_exception(error)


# Global tracer instance
_tracer: DistributedTracer | None = None


def setup_tracing(
    service_name: str,
    service_version: str = "1.0.0",
    **config_kwargs,
) -> DistributedTracer:
    """
    Setup distributed tracing for a service.
    إعداد التتبع الموزع لخدمة.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        **config_kwargs: Additional configuration parameters

    Returns:
        DistributedTracer instance
    """
    global _tracer

    config = TracingConfig(
        service_name=service_name,
        service_version=service_version,
        **config_kwargs,
    )

    _tracer = DistributedTracer(config)

    # Auto-instrument common libraries
    _tracer.instrument_libraries()

    return _tracer


def get_tracer() -> DistributedTracer | None:
    """
    Get the global tracer instance.
    الحصول على مثيل التتبع العالمي.
    """
    return _tracer


def trace_function(name: str | None = None, attributes: dict[str, Any] | None = None):
    """
    Decorator to trace a function.
    مزخرف لتتبع دالة.

    Usage:
        @trace_function("process_ndvi")
        async def process_ndvi_data(field_id: str):
            # Your code
            pass
    """

    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if not tracer or not tracer.enabled:
                return await func(*args, **kwargs)

            with tracer.span(span_name, attributes=attributes):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if not tracer or not tracer.enabled:
                return func(*args, **kwargs)

            with tracer.span(span_name, attributes=attributes):
                return func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
