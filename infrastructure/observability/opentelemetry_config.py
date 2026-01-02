#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - OpenTelemetry Distributed Tracing Configuration
إعدادات التتبع الموزع
═══════════════════════════════════════════════════════════════════════════════════════

Implements distributed tracing to answer "WHY is login slow?"

Features:
- Automatic trace propagation across services
- Database query tracing with timing
- HTTP request/response tracing
- Custom span attributes for debugging
- Jaeger/Zipkin/OTLP export support

Trace Flow Example:
    Request → Nginx (5ms) → Auth Service (100ms) → Database (3000ms) ← Problem here!

Usage:
    from opentelemetry_config import setup_tracing, get_tracer

    # In main.py
    setup_tracing(service_name="auth-service")

    # In your code
    tracer = get_tracer()
    with tracer.start_as_current_span("authenticate_user") as span:
        span.set_attribute("user.email", email)
        result = await db.query_user(email)

═══════════════════════════════════════════════════════════════════════════════════════
"""

import os
from typing import Optional, Dict, Any
from functools import wraps
import logging

# OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.b3 import B3MultiFormat
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("Warning: OpenTelemetry not installed. Install with:")
    print("  pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp")
    print("  pip install opentelemetry-instrumentation-fastapi")
    print("  pip install opentelemetry-instrumentation-sqlalchemy")
    print("  pip install opentelemetry-instrumentation-redis")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opentelemetry")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# OTLP Collector endpoint (Jaeger, Zipkin, or OpenTelemetry Collector)
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Sampling rate (1.0 = 100%, 0.1 = 10%)
TRACE_SAMPLE_RATE = float(os.getenv("TRACE_SAMPLE_RATE", "1.0"))

# Enable console output for debugging
TRACE_CONSOLE_OUTPUT = os.getenv("TRACE_CONSOLE_OUTPUT", "false").lower() == "true"

# ═══════════════════════════════════════════════════════════════════════════════
# TRACER PROVIDER SETUP
# ═══════════════════════════════════════════════════════════════════════════════

_tracer: Optional[trace.Tracer] = None


def setup_tracing(
    service_name: str,
    service_version: str = "1.0.0",
    environment: str = ENVIRONMENT,
    otlp_endpoint: str = OTLP_ENDPOINT,
    enable_console: bool = TRACE_CONSOLE_OUTPUT,
) -> Optional[trace.Tracer]:
    """
    Initialize OpenTelemetry tracing for a service.

    Args:
        service_name: Name of the service (e.g., "auth-service")
        service_version: Version of the service
        environment: Deployment environment
        otlp_endpoint: OTLP collector endpoint
        enable_console: Enable console output for debugging

    Returns:
        Configured Tracer instance
    """
    global _tracer

    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available - tracing disabled")
        return None

    logger.info(f"Setting up tracing for service: {service_name}")

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: service_name,
        "service.version": service_version,
        "deployment.environment": environment,
        "service.namespace": "sahool-idp",
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter (sends to Jaeger/Zipkin/Collector)
    try:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(f"OTLP exporter configured: {otlp_endpoint}")
    except Exception as e:
        logger.warning(f"Could not configure OTLP exporter: {e}")

    # Add console exporter for debugging
    if enable_console:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info("Console exporter enabled")

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Set up B3 propagation (for compatibility with Zipkin, Kong, etc.)
    set_global_textmap(B3MultiFormat())

    # Get tracer instance
    _tracer = trace.get_tracer(service_name, service_version)

    return _tracer


def get_tracer() -> Optional[trace.Tracer]:
    """Get the configured tracer instance."""
    global _tracer
    if _tracer is None and OTEL_AVAILABLE:
        _tracer = trace.get_tracer("sahool-idp")
    return _tracer


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-INSTRUMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def instrument_fastapi(app):
    """
    Automatically instrument FastAPI application.

    This adds tracing to:
    - All HTTP endpoints
    - Request/response headers
    - Exception tracking
    """
    if not OTEL_AVAILABLE:
        return

    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI instrumentation enabled")


def instrument_sqlalchemy(engine):
    """
    Instrument SQLAlchemy for database query tracing.

    This shows:
    - Query execution time
    - Query text
    - Database connection pool stats
    """
    if not OTEL_AVAILABLE:
        return

    SQLAlchemyInstrumentor().instrument(engine=engine)
    logger.info("SQLAlchemy instrumentation enabled")


def instrument_redis(redis_client):
    """
    Instrument Redis client for cache operation tracing.

    This shows:
    - Redis command execution time
    - Command type (GET, SET, etc.)
    - Key patterns
    """
    if not OTEL_AVAILABLE:
        return

    RedisInstrumentor().instrument()
    logger.info("Redis instrumentation enabled")


def instrument_aiohttp():
    """
    Instrument aiohttp client for outgoing HTTP request tracing.

    This shows:
    - External API call timing
    - Response status codes
    - URL patterns
    """
    if not OTEL_AVAILABLE:
        return

    AioHttpClientInstrumentor().instrument()
    logger.info("aiohttp client instrumentation enabled")


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM SPAN DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════

def traced(
    operation_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to trace a function with custom span.

    Usage:
        @traced("authenticate_user", {"auth.method": "password"})
        async def authenticate(email, password):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if tracer is None:
                return await func(*args, **kwargs)

            span_name = operation_name or func.__name__
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if tracer is None:
                return func(*args, **kwargs)

            span_name = operation_name or func.__name__
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.record_exception(e)
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def trace_database_query(query_name: str):
    """
    Decorator specifically for database queries.

    Adds attributes useful for database debugging.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            if tracer is None:
                return await func(*args, **kwargs)

            with tracer.start_as_current_span(f"db.{query_name}") as span:
                span.set_attribute("db.system", "postgresql")
                span.set_attribute("db.operation", query_name)

                import time
                start = time.time()

                try:
                    result = await func(*args, **kwargs)
                    elapsed = (time.time() - start) * 1000
                    span.set_attribute("db.duration_ms", elapsed)

                    # Flag slow queries (> 100ms)
                    if elapsed > 100:
                        span.set_attribute("db.slow_query", True)
                        logger.warning(f"Slow query detected: {query_name} took {elapsed:.2f}ms")

                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════════

class TracingMiddleware:
    """
    Custom middleware for additional tracing context.

    Adds:
    - User ID to spans
    - Request ID for correlation
    - Custom SAHOOL attributes
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        tracer = get_tracer()
        if tracer is None:
            await self.app(scope, receive, send)
            return

        # Extract request info
        headers = dict(scope.get("headers", []))
        path = scope.get("path", "")
        method = scope.get("method", "")

        # Get current span
        current_span = trace.get_current_span()
        if current_span.is_recording():
            # Add SAHOOL-specific attributes
            current_span.set_attribute("http.route", path)
            current_span.set_attribute("sahool.environment", ENVIRONMENT)

            # Extract user ID from JWT (if available)
            auth_header = headers.get(b"authorization", b"").decode()
            if auth_header.startswith("Bearer "):
                current_span.set_attribute("sahool.authenticated", True)

            # Extract request ID for correlation
            request_id = headers.get(b"x-request-id", b"").decode()
            if request_id:
                current_span.set_attribute("request.id", request_id)

        await self.app(scope, receive, send)


# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER COMPOSE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

JAEGER_DOCKER_COMPOSE = """
# Add to docker-compose.yml for local tracing
# يضاف إلى docker-compose.yml للتتبع المحلي

services:
  jaeger:
    image: jaegertracing/all-in-one:1.50
    container_name: sahool_jaeger
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
      - "14268:14268"  # Jaeger thrift
    networks:
      - sahool_network

  # Optional: OpenTelemetry Collector for advanced routing
  otel-collector:
    image: otel/opentelemetry-collector:0.88.0
    container_name: sahool_otel_collector
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "8889:8889"   # Prometheus metrics
    networks:
      - sahool_network
"""

OTEL_COLLECTOR_CONFIG = """
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

  # Filter out health check spans to reduce noise
  filter:
    spans:
      exclude:
        match_type: regexp
        span_names:
          - "GET /health.*"
          - "GET /readyz"

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  prometheus:
    endpoint: 0.0.0.0:8889

  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, filter]
      exporters: [jaeger, logging]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
"""


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

def example_fastapi_integration():
    """
    Example of integrating tracing with FastAPI.

    Add this to your main.py:

    ```python
    from fastapi import FastAPI
    from opentelemetry_config import (
        setup_tracing,
        instrument_fastapi,
        instrument_sqlalchemy,
        TracingMiddleware,
    )

    app = FastAPI()

    # Setup tracing
    setup_tracing(
        service_name="auth-service",
        service_version="1.0.0",
    )

    # Instrument FastAPI
    instrument_fastapi(app)

    # Add custom middleware
    app.add_middleware(TracingMiddleware)

    # Instrument database
    instrument_sqlalchemy(engine)

    @app.get("/login")
    @traced("user_login", {"auth.method": "password"})
    async def login(credentials: LoginRequest):
        # Your login logic here
        pass
    ```
    """
    pass


if __name__ == "__main__":
    # Test tracing setup
    print("OpenTelemetry Configuration")
    print("=" * 50)
    print(f"OTEL Available: {OTEL_AVAILABLE}")
    print(f"OTLP Endpoint: {OTLP_ENDPOINT}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Sample Rate: {TRACE_SAMPLE_RATE}")
    print("")
    print("Docker Compose for Jaeger:")
    print(JAEGER_DOCKER_COMPOSE)
