"""
SAHOOL Shared Structured Logging Configuration
===============================================

Provides standardized JSON structured logging for all SAHOOL Python/FastAPI services.

Features:
- JSON structured logging with structlog
- Correlation ID tracking
- Automatic service name, timestamp, level, traceId
- FastAPI middleware for request logging
- Context-aware logging

Usage:
    from shared.logging_config import setup_logging, get_logger, RequestLoggingMiddleware

    # In main.py:
    setup_logging(service_name="my-service")
    logger = get_logger(__name__)

    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware, service_name="my-service")

    # In your code:
    logger.info("operation_completed", user_id="123", field_id="456")
"""

import logging
import os
import sys
from contextvars import ContextVar
from typing import Any, Optional
from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Context variables for correlation tracking
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
tenant_id_var: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def add_correlation_id(
    logger: logging.Logger, method_name: str, event_dict: dict
) -> dict:
    """Add correlation ID to log entries"""
    correlation_id = correlation_id_var.get()
    if correlation_id:
        event_dict["correlationId"] = correlation_id
        event_dict["traceId"] = correlation_id  # Alias for OpenTelemetry compatibility

    tenant_id = tenant_id_var.get()
    if tenant_id:
        event_dict["tenantId"] = tenant_id

    user_id = user_id_var.get()
    if user_id:
        event_dict["userId"] = user_id

    return event_dict


def setup_logging(
    service_name: str,
    log_level: Optional[str] = None,
    json_logs: bool = True,
) -> None:
    """
    Configure structured logging for a service.

    Args:
        service_name: Name of the service (e.g., "crop-health", "weather-core")
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to use JSON format (True) or pretty console format (False)
    """
    # Determine log level
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Determine if we should use JSON based on environment
    environment = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
    if environment == "production":
        json_logs = True

    # Configure processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_correlation_id,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add service name processor
    processors.append(
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        )
    )

    # Add renderer (JSON or Console)
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )

    # Set service name globally
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create initial logger to set service name
    logger = structlog.get_logger()
    logger = logger.bind(service=service_name)

    # Store in global context
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for logging HTTP requests with structured logging.

    Automatically adds correlation IDs, tracks request/response timing,
    and logs all HTTP interactions.
    """

    # Paths to exclude from logging
    EXCLUDE_PATHS = {
        "/health",
        "/healthz",
        "/health/live",
        "/health/ready",
        "/readyz",
        "/livez",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    def __init__(self, app: ASGIApp, service_name: str):
        super().__init__(app)
        self.service_name = service_name
        self.logger = get_logger(__name__)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and add structured logging"""
        # Skip health check endpoints
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        # Extract or generate correlation ID
        correlation_id = (
            request.headers.get("x-correlation-id")
            or request.headers.get("x-request-id")
            or str(uuid4())
        )

        # Extract tenant and user IDs
        tenant_id = request.headers.get("x-tenant-id")
        user_id = request.headers.get("x-user-id")

        # Set context variables
        correlation_id_var.set(correlation_id)
        if tenant_id:
            tenant_id_var.set(tenant_id)
        if user_id:
            user_id_var.set(user_id)

        # Bind to structlog context
        structlog.contextvars.bind_contextvars(
            correlationId=correlation_id,
            traceId=correlation_id,
            tenantId=tenant_id,
            userId=user_id,
        )

        # Log incoming request
        self.logger.info(
            "http_request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        # Process request and time it
        import time

        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = correlation_id

            # Log response
            log_method = self.logger.info
            if response.status_code >= 500:
                log_method = self.logger.error
            elif response.status_code >= 400:
                log_method = self.logger.warning

            log_method(
                "http_request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            self.logger.error(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True,
            )
            raise

        finally:
            # Clear context variables
            structlog.contextvars.clear_contextvars()
            correlation_id_var.set(None)
            tenant_id_var.set(None)
            user_id_var.set(None)


def set_correlation_id(correlation_id: str) -> None:
    """Manually set correlation ID for the current context"""
    correlation_id_var.set(correlation_id)
    structlog.contextvars.bind_contextvars(
        correlationId=correlation_id, traceId=correlation_id
    )


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID"""
    return correlation_id_var.get()


def set_tenant_id(tenant_id: str) -> None:
    """Manually set tenant ID for the current context"""
    tenant_id_var.set(tenant_id)
    structlog.contextvars.bind_contextvars(tenantId=tenant_id)


def set_user_id(user_id: str) -> None:
    """Manually set user ID for the current context"""
    user_id_var.set(user_id)
    structlog.contextvars.bind_contextvars(userId=user_id)
