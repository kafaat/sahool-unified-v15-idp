"""
OpenTelemetry Distributed Tracing for SAHOOL Platform
======================================================

This module provides comprehensive distributed tracing instrumentation for all
Python-based services in the SAHOOL agricultural platform.

Features:
- Auto-instrumentation for FastAPI, httpx, SQLAlchemy, Redis, PostgreSQL
- OTLP exporter configuration for Jaeger/Zipkin
- Custom span creation helpers
- Baggage and context propagation
- Service name auto-detection

Usage:
    from shared.telemetry.tracing import init_tracer, trace_method, get_tracer

    # Initialize at application startup
    tracer_provider = init_tracer(service_name="field_core")

    # Use decorator for automatic tracing
    @trace_method(name="process_field_data")
    def process_field(field_id: str):
        pass

    # Or use tracer directly
    tracer = get_tracer()
    with tracer.start_as_current_span("custom_operation") as span:
        span.set_attribute("field.id", field_id)
        # ... your code

Author: SAHOOL Platform Team
Date: 2025-12-26
"""

import logging
import os
from typing import Optional, Dict, Any, Callable
from functools import wraps

from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.trace import Status, StatusCode, Span
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ParentBased

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Optional[trace.Tracer] = None
_tracer_provider: Optional[TracerProvider] = None


def init_tracer(
    service_name: Optional[str] = None,
    service_version: Optional[str] = None,
    environment: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    console_export: bool = False,
    sampling_ratio: float = 0.1,
) -> TracerProvider:
    """
    Initialize OpenTelemetry tracer with OTLP exporter.

    Args:
        service_name: Name of the service (auto-detected from env if not provided)
        service_version: Version of the service
        environment: Deployment environment (development, staging, production)
        otlp_endpoint: OTLP collector endpoint (e.g., http://otel-collector:4317)
        console_export: Enable console exporter for debugging
        sampling_ratio: Sampling ratio for traces (0.0 to 1.0)

    Returns:
        TracerProvider instance
    """
    global _tracer_provider

    # Auto-detect service name from environment
    if not service_name:
        service_name = os.getenv("OTEL_SERVICE_NAME") or os.getenv(
            "SERVICE_NAME", "sahool-service"
        )

    if not service_version:
        service_version = os.getenv("SERVICE_VERSION", "1.0.0")

    if not environment:
        environment = os.getenv("ENVIRONMENT", "development")

    if not otlp_endpoint:
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"
        )

    # Create resource with service information
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: environment,
            "service.namespace": "sahool",
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
        }
    )

    # Configure sampling - use parent-based with ratio-based sampling
    sampler = ParentBased(root=TraceIdRatioBased(sampling_ratio))

    # Create tracer provider
    _tracer_provider = TracerProvider(
        resource=resource,
        sampler=sampler,
    )

    # Add OTLP exporter for production tracing
    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True,  # Use TLS in production
        )
        _tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter, max_export_batch_size=512)
        )
        logger.info(f"OTLP trace exporter configured: {otlp_endpoint}")
    except Exception as e:
        logger.warning(f"Failed to configure OTLP exporter: {e}")

    # Add console exporter for debugging
    if console_export or os.getenv("OTEL_CONSOLE_EXPORT", "false").lower() == "true":
        _tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        logger.info("Console trace exporter enabled")

    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)

    # Configure context propagation (W3C Trace Context + Baggage)
    set_global_textmap(TraceContextTextMapPropagator())

    logger.info(
        f"OpenTelemetry tracer initialized: service={service_name}, env={environment}, sampling={sampling_ratio}"
    )

    return _tracer_provider


def get_tracer(name: Optional[str] = None) -> trace.Tracer:
    """
    Get a tracer instance.

    Args:
        name: Tracer name (defaults to module name)

    Returns:
        Tracer instance
    """
    if not _tracer_provider:
        logger.warning("Tracer provider not initialized, using default")
        return trace.get_tracer(name or __name__)

    return trace.get_tracer(name or __name__)


def instrument_fastapi(app) -> None:
    """
    Auto-instrument FastAPI application.

    Args:
        app: FastAPI application instance
    """
    try:
        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls=os.getenv("OTEL_EXCLUDED_URLS", "/health,/metrics,/ready"),
        )
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {e}")


def instrument_http_clients() -> None:
    """Auto-instrument HTTP clients (httpx)."""
    try:
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX client instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument HTTPX: {e}")


def instrument_sqlalchemy(engine) -> None:
    """
    Auto-instrument SQLAlchemy database engine.

    Args:
        engine: SQLAlchemy engine instance
    """
    try:
        SQLAlchemyInstrumentor().instrument(
            engine=engine,
            enable_commenter=True,
            commenter_options={
                "db_driver": True,
                "db_framework": True,
            },
        )
        logger.info("SQLAlchemy instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument SQLAlchemy: {e}")


def instrument_redis() -> None:
    """Auto-instrument Redis client."""
    try:
        RedisInstrumentor().instrument()
        logger.info("Redis instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument Redis: {e}")


def instrument_postgres() -> None:
    """Auto-instrument PostgreSQL (psycopg2)."""
    try:
        Psycopg2Instrumentor().instrument()
        logger.info("PostgreSQL (psycopg2) instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument PostgreSQL: {e}")


def instrument_all(app=None, db_engine=None) -> None:
    """
    Auto-instrument all supported libraries.

    Args:
        app: FastAPI application (optional)
        db_engine: SQLAlchemy engine (optional)
    """
    if app:
        instrument_fastapi(app)

    instrument_http_clients()
    instrument_redis()
    instrument_postgres()

    if db_engine:
        instrument_sqlalchemy(db_engine)

    logger.info("All instrumentations enabled")


def trace_method(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to trace a method/function.

    Args:
        name: Span name (defaults to function name)
        attributes: Additional attributes to add to span

    Example:
        @trace_method(name="process_field", attributes={"field.type": "agricultural"})
        def process_field(field_id: str):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function metadata
                span.set_attribute("code.function", func.__name__)
                span.set_attribute("code.namespace", func.__module__)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


async def trace_async_method(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to trace an async method/function.

    Args:
        name: Span name (defaults to function name)
        attributes: Additional attributes to add to span
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function metadata
                span.set_attribute("code.function", func.__name__)
                span.set_attribute("code.namespace", func.__module__)

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


def add_span_attributes(span: Span, attributes: Dict[str, Any]) -> None:
    """
    Add multiple attributes to a span.

    Args:
        span: Current span
        attributes: Dictionary of attributes to add
    """
    for key, value in attributes.items():
        if value is not None:
            span.set_attribute(key, value)


def add_baggage_item(key: str, value: str) -> None:
    """
    Add item to baggage for cross-service context propagation.

    Args:
        key: Baggage key
        value: Baggage value
    """
    baggage.set_baggage(key, value)


def get_baggage_item(key: str) -> Optional[str]:
    """
    Get item from baggage.

    Args:
        key: Baggage key

    Returns:
        Baggage value or None
    """
    return baggage.get_baggage(key)


def get_current_trace_id() -> Optional[str]:
    """
    Get current trace ID for logging correlation.

    Returns:
        Trace ID as hex string or None
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, "032x")
    return None


def get_current_span_id() -> Optional[str]:
    """
    Get current span ID for logging correlation.

    Returns:
        Span ID as hex string or None
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, "016x")
    return None


# Service name mappings for all 44+ SAHOOL services
SAHOOL_SERVICES = {
    # Core services
    "field_core": "Field Core Service",
    "field_ops": "Field Operations Service",
    "field_service": "Field Management Service",
    # Weather services
    "weather_core": "Weather Core Service",
    "weather_advanced": "Advanced Weather Service",
    # Satellite & imagery
    "satellite_service": "Satellite Imagery Service",
    "ndvi_engine": "NDVI Calculation Engine",
    "ndvi_processor": "NDVI Processor Service",
    # Agriculture AI/ML
    "crop_health_ai": "Crop Health AI Service",
    "crop_health": "Crop Health Monitoring",
    "crop_growth_model": "Crop Growth Model Service",
    "lai_estimation": "Leaf Area Index Estimation",
    "yield_engine": "Yield Calculation Engine",
    "yield_prediction": "Yield Prediction Service",
    # Advisory services
    "ai_advisor": "AI Agricultural Advisor",
    "agro_advisor": "Agronomy Advisor Service",
    "agro_rules": "Agronomy Rules Engine",
    "fertilizer_advisor": "Fertilizer Recommendation",
    "irrigation_smart": "Smart Irrigation Service",
    # IoT & sensors
    "iot_gateway": "IoT Gateway Service",
    "iot_service": "IoT Management Service",
    "virtual_sensors": "Virtual Sensors Service",
    # Analytics & monitoring
    "indicators_service": "Agricultural Indicators",
    "astronomical_calendar": "Astronomical Calendar",
    "disaster_assessment": "Disaster Assessment",
    # Communication
    "notification_service": "Notification Service",
    "alert_service": "Alert Management Service",
    "chat_service": "Chat Service",
    "community_chat": "Community Chat Service",
    "field_chat": "Field Chat Service",
    # Business services
    "billing_core": "Billing Core Service",
    "marketplace_service": "Marketplace Service",
    "inventory_service": "Inventory Management",
    "equipment_service": "Equipment Management",
    "task_service": "Task Management Service",
    # Research
    "research_core": "Research Core Service",
    # Infrastructure
    "ws_gateway": "WebSocket Gateway",
    "kong": "API Gateway (Kong)",
}


__all__ = [
    "init_tracer",
    "get_tracer",
    "instrument_all",
    "instrument_fastapi",
    "instrument_http_clients",
    "instrument_sqlalchemy",
    "instrument_redis",
    "instrument_postgres",
    "trace_method",
    "trace_async_method",
    "add_span_attributes",
    "add_baggage_item",
    "get_baggage_item",
    "get_current_trace_id",
    "get_current_span_id",
    "SAHOOL_SERVICES",
]
