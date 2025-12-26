"""
Structured Logging with OpenTelemetry Integration for SAHOOL Platform
======================================================================

This module provides structured JSON logging with automatic trace ID injection
for correlation between logs and distributed traces.

Features:
- Structured JSON logging
- Automatic trace ID and span ID injection
- Log level configuration from environment
- Correlation with OpenTelemetry traces
- Support for Arabic log messages
- FastAPI request logging middleware

Usage:
    from shared.telemetry.logging import setup_logging, get_logger

    # Setup at application startup
    setup_logging(service_name="field_core", log_level="INFO")

    # Get logger instance
    logger = get_logger(__name__)

    # Log with automatic trace correlation
    logger.info("Processing field", extra={"field_id": "123", "user_id": "456"})
    logger.error("Failed to process field", exc_info=True)

Author: SAHOOL Platform Team
Date: 2025-12-26
"""

import logging
import sys
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


class TraceContextFilter(logging.Filter):
    """
    Logging filter to inject trace context (trace_id, span_id) into log records.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add trace context to log record.

        Args:
            record: Log record to filter

        Returns:
            True to allow the record to be logged
        """
        # Get current span context
        span = trace.get_current_span()
        span_context = span.get_span_context()

        if span_context.is_valid:
            # Add trace ID and span ID to record
            record.trace_id = format(span_context.trace_id, '032x')
            record.span_id = format(span_context.span_id, '016x')
            record.trace_flags = span_context.trace_flags
        else:
            record.trace_id = "0" * 32
            record.span_id = "0" * 16
            record.trace_flags = 0

        return True


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    """

    def __init__(
        self,
        service_name: str = "sahool-service",
        service_version: str = "1.0.0",
        environment: str = "development",
        include_trace: bool = True,
    ):
        """
        Initialize JSON formatter.

        Args:
            service_name: Name of the service
            service_version: Version of the service
            environment: Deployment environment
            include_trace: Include trace context in logs
        """
        super().__init__()
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.include_trace = include_trace

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON formatted log string
        """
        # Base log structure
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": {
                "name": self.service_name,
                "version": self.service_version,
                "environment": self.environment,
            },
            "process": {
                "pid": record.process,
                "thread_id": record.thread,
            },
            "location": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
        }

        # Add trace context if available
        if self.include_trace and hasattr(record, "trace_id"):
            log_data["trace"] = {
                "trace_id": record.trace_id,
                "span_id": record.span_id,
                "trace_flags": record.trace_flags,
            }

        # Add exception information if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add custom fields from extra
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add any additional attributes
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs", "message",
                "pathname", "process", "processName", "relativeCreated", "thread",
                "threadName", "exc_info", "exc_text", "stack_info", "trace_id",
                "span_id", "trace_flags", "extra_fields",
            ]:
                # Only include serializable values
                try:
                    json.dumps(value)
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)

        return json.dumps(log_data, ensure_ascii=False)


class SahoolLogger(logging.LoggerAdapter):
    """
    Custom logger adapter for SAHOOL platform with automatic context injection.
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message and add extra context.

        Args:
            msg: Log message
            kwargs: Keyword arguments

        Returns:
            Tuple of (message, kwargs)
        """
        # Merge extra fields
        extra = kwargs.get("extra", {})

        # Store extra fields in a single attribute
        if "extra_fields" not in extra:
            extra["extra_fields"] = {}

        # Add context from logger adapter
        if self.extra:
            extra["extra_fields"].update(self.extra)

        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    service_name: Optional[str] = None,
    service_version: Optional[str] = None,
    environment: Optional[str] = None,
    log_level: Optional[str] = None,
    json_format: bool = True,
    include_trace: bool = True,
) -> None:
    """
    Setup structured logging with trace context.

    Args:
        service_name: Name of the service (auto-detected from env if not provided)
        service_version: Version of the service
        environment: Deployment environment
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting
        include_trace: Include trace context in logs
    """
    # Auto-detect configuration from environment
    if not service_name:
        service_name = os.getenv("OTEL_SERVICE_NAME") or os.getenv("SERVICE_NAME", "sahool-service")

    if not service_version:
        service_version = os.getenv("SERVICE_VERSION", "1.0.0")

    if not environment:
        environment = os.getenv("ENVIRONMENT", "development")

    if not log_level:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Add trace context filter
    if include_trace:
        trace_filter = TraceContextFilter()
        console_handler.addFilter(trace_filter)

    # Set formatter
    if json_format or os.getenv("LOG_FORMAT", "json").lower() == "json":
        formatter = JSONFormatter(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            include_trace=include_trace,
        )
    else:
        # Simple text format with trace IDs
        format_str = (
            "%(asctime)s [%(levelname)s] %(name)s "
            "[trace_id=%(trace_id)s span_id=%(span_id)s] "
            "%(message)s"
        )
        formatter = logging.Formatter(format_str)

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info(
        f"Logging configured: service={service_name}, level={log_level}, format={'JSON' if json_format else 'TEXT'}"
    )


def get_logger(name: str, extra: Optional[Dict[str, Any]] = None) -> SahoolLogger:
    """
    Get a logger instance with SAHOOL platform context.

    Args:
        name: Logger name (typically __name__)
        extra: Extra context to include in all log messages

    Returns:
        SahoolLogger instance
    """
    logger = logging.getLogger(name)
    return SahoolLogger(logger, extra or {})


def log_exception(
    logger: logging.Logger,
    exception: Exception,
    message: str = "Exception occurred",
    **kwargs
) -> None:
    """
    Log exception with trace context and record in current span.

    Args:
        logger: Logger instance
        exception: Exception to log
        message: Log message
        **kwargs: Additional context
    """
    # Log exception
    logger.error(message, exc_info=exception, extra=kwargs)

    # Record exception in current span
    span = trace.get_current_span()
    if span and span.is_recording():
        span.record_exception(exception)
        span.set_status(Status(StatusCode.ERROR, str(exception)))


def log_with_trace(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
) -> None:
    """
    Log message with automatic trace context.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra=kwargs)


# FastAPI middleware for request logging
class RequestLoggingMiddleware:
    """
    Middleware to log all HTTP requests with trace context.
    """

    def __init__(self, app, logger: Optional[logging.Logger] = None):
        """
        Initialize middleware.

        Args:
            app: FastAPI application
            logger: Logger instance (defaults to root logger)
        """
        self.app = app
        self.logger = logger or logging.getLogger("sahool.request")

    async def __call__(self, scope, receive, send):
        """
        Process HTTP request.

        Args:
            scope: ASGI scope
            receive: Receive callable
            send: Send callable
        """
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Extract request info
        method = scope["method"]
        path = scope["path"]
        client_host = scope.get("client", ["unknown"])[0] if scope.get("client") else "unknown"

        # Log request start
        self.logger.info(
            f"Request started: {method} {path}",
            extra={
                "http_method": method,
                "http_path": path,
                "client_host": client_host,
                "event": "request_started",
            }
        )

        # Process request
        try:
            await self.app(scope, receive, send)

            # Log request completion
            self.logger.info(
                f"Request completed: {method} {path}",
                extra={
                    "http_method": method,
                    "http_path": path,
                    "event": "request_completed",
                }
            )
        except Exception as e:
            # Log request error
            self.logger.error(
                f"Request failed: {method} {path}",
                exc_info=e,
                extra={
                    "http_method": method,
                    "http_path": path,
                    "event": "request_failed",
                }
            )
            raise


__all__ = [
    "setup_logging",
    "get_logger",
    "log_exception",
    "log_with_trace",
    "TraceContextFilter",
    "JSONFormatter",
    "SahoolLogger",
    "RequestLoggingMiddleware",
]
