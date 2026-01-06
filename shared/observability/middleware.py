"""
FastAPI Middleware for Observability
البرمجيات الوسيطة لـ FastAPI للمراقبة

Provides automatic tracing, metrics, and logging for all requests.
"""

import logging
import time
import uuid
from collections.abc import Callable
from typing import Any, Optional

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

try:
    from opentelemetry import trace
    from opentelemetry.propagate import extract, inject
    from opentelemetry.trace import SpanKind, Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

from .logging import clear_request_context, set_request_context

logger = logging.getLogger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic observability instrumentation.
    برمجيات وسيطة للإضافة التلقائية لأدوات المراقبة.

    Features:
    - Automatic trace context extraction
    - Request ID generation
    - Request/response logging
    - Metrics collection
    - Error tracking
    """

    def __init__(
        self,
        app: FastAPI,
        service_name: str,
        metrics_collector: Optional[Any] = None,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.metrics_collector = metrics_collector
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process each request with observability instrumentation."""

        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Extract tenant and user from headers or auth
        tenant_id = request.headers.get("X-Tenant-ID", "")
        user_id = request.headers.get("X-User-ID", "")

        # Set request context for logging
        set_request_context(
            request_id=request_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        # Start timing
        start_time = time.perf_counter()

        # Create span if tracing is enabled
        span = None
        if OTEL_AVAILABLE:
            tracer = trace.get_tracer(__name__)

            # Extract trace context from headers
            ctx = extract(dict(request.headers))

            # Start span with extracted context
            span = tracer.start_span(
                f"{request.method} {request.url.path}",
                kind=SpanKind.SERVER,
                context=ctx,
            )

            # Add request attributes
            if span and span.is_recording():
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.url", str(request.url))
                span.set_attribute("http.scheme", request.url.scheme)
                span.set_attribute("http.host", request.url.hostname or "")
                span.set_attribute("http.target", request.url.path)
                span.set_attribute("request.id", request_id)

                if tenant_id:
                    span.set_attribute("tenant.id", tenant_id)
                if user_id:
                    span.set_attribute("user.id", user_id)

                # Add user agent
                if user_agent := request.headers.get("user-agent"):
                    span.set_attribute("http.user_agent", user_agent)

        # Store request ID in request state
        request.state.request_id = request_id
        request.state.start_time = start_time

        # Process request
        response = None
        error = None
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code

            # Add trace headers to response
            if span and span.is_recording():
                span.set_attribute("http.status_code", status_code)

                # Inject trace context into response headers
                if OTEL_AVAILABLE:
                    carrier = {}
                    inject(carrier)
                    for key, value in carrier.items():
                        response.headers[key] = value

            return response

        except Exception as e:
            error = e
            logger.exception(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                },
            )

            if span and span.is_recording():
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)

            raise

        finally:
            # Calculate duration
            duration = time.perf_counter() - start_time

            # Record metrics if available
            if self.metrics_collector:
                try:
                    self.metrics_collector.record_request(
                        method=request.method,
                        endpoint=request.url.path,
                        status=status_code,
                        duration=duration,
                    )

                    if error:
                        self.metrics_collector.record_error(
                            error_type=type(error).__name__,
                            severity="error",
                        )
                except Exception as e:
                    logger.warning(f"Failed to record metrics: {e}")

            # Log request completion
            logger.info(
                f"{request.method} {request.url.path} - {status_code} - {duration:.3f}s",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration": duration,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                },
            )

            # End span
            if span:
                if not error:
                    span.set_status(Status(StatusCode.OK))
                span.end()

            # Clear request context
            clear_request_context()

            # Add request ID header to response
            if response:
                response.headers["X-Request-ID"] = request_id


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request/response logging.
    برمجيات وسيطة لتسجيل الطلبات والردود بالتفصيل.
    """

    def __init__(
        self,
        app: FastAPI,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_size: int = 1024,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""

        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Log request
        request_log = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": self._filter_headers(dict(request.headers)),
        }

        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    request_log["body"] = body.decode("utf-8")
                else:
                    request_log["body"] = f"<truncated, size: {len(body)} bytes>"

                # Reconstruct request for further processing
                from starlette.requests import Request as StarletteRequest

                async def receive():
                    return {"type": "http.request", "body": body}

                request = StarletteRequest(request.scope, receive)
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")

        logger.debug("Incoming request", extra=request_log)

        # Process request
        response = await call_next(request)

        # Log response
        response_log = {
            "status_code": response.status_code,
            "headers": self._filter_headers(dict(response.headers)),
        }

        if self.log_response_body and response.status_code >= 400:
            # Log error responses
            try:
                # Note: This is simplified; in production, you'd need to
                # handle streaming responses properly
                response_log["logged_error"] = True
            except Exception as e:
                logger.warning(f"Failed to read response body: {e}")

        logger.debug("Outgoing response", extra=response_log)

        return response

    def _filter_headers(self, headers: dict) -> dict:
        """Filter sensitive headers."""
        sensitive_headers = {
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
        }

        return {
            k: "***REDACTED***" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        }


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting HTTP metrics.
    برمجيات وسيطة لجمع مقاييس HTTP.
    """

    def __init__(
        self,
        app: FastAPI,
        metrics_collector: any,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.metrics_collector = metrics_collector
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Collect metrics for each request."""

        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Increment active connections
        self.metrics_collector.increment_active_connections()

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as e:
            # Record error
            self.metrics_collector.record_error(
                error_type=type(e).__name__,
                severity="error",
            )
            raise

        finally:
            # Decrement active connections
            self.metrics_collector.decrement_active_connections()

            # Record request metrics
            duration = time.perf_counter() - start_time
            self.metrics_collector.record_request(
                method=request.method,
                endpoint=request.url.path,
                status=status_code,
                duration=duration,
            )


def setup_observability_middleware(
    app: FastAPI,
    service_name: str,
    metrics_collector: Optional[Any] = None,
    enable_request_logging: bool = False,
    log_request_body: bool = False,
    log_response_body: bool = False,
) -> None:
    """
    Setup all observability middleware for a FastAPI app.
    إعداد جميع البرمجيات الوسيطة للمراقبة لتطبيق FastAPI.

    Args:
        app: FastAPI application
        service_name: Name of the service
        metrics_collector: Optional metrics collector instance
        enable_request_logging: Enable detailed request/response logging
        log_request_body: Log request bodies
        log_response_body: Log response bodies
    """
    # Add observability middleware (always)
    app.add_middleware(
        ObservabilityMiddleware,
        service_name=service_name,
        metrics_collector=metrics_collector,
    )

    # Add request logging middleware (optional, for debugging)
    if enable_request_logging:
        app.add_middleware(
            RequestLoggingMiddleware,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
        )

    # Add metrics middleware if collector is provided
    if metrics_collector:
        app.add_middleware(
            MetricsMiddleware,
            metrics_collector=metrics_collector,
        )

    logger.info(f"Observability middleware configured for {service_name}")
