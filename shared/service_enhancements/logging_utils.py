"""
SAHOOL Logging Utilities Module
===============================
Provides structured logging with context for SAHOOL services.

Features:
- Service-specific loggers with structured output
- Context propagation (tenant, user, correlation ID)
- Performance logging with timing
- Operation tracking for debugging
- Arabic/English bilingual log messages

Usage:
    from shared.service_enhancements.logging_utils import (
        ServiceLogger,
        get_service_logger,
        log_operation,
        log_performance,
    )

    logger = get_service_logger("advisory-service")
    logger.info("Processing request", field_id="FIELD-001", crop="wheat")

    with log_operation(logger, "calculate_irrigation"):
        result = calculate()
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import wraps
from typing import Any, Callable, TypeVar

# Context variables for request tracking
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_tenant_id: ContextVar[str | None] = ContextVar("tenant_id", default=None)
_user_id: ContextVar[str | None] = ContextVar("user_id", default=None)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class LogContext:
    """Context for structured logging."""

    correlation_id: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    service_name: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        result = {}
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        if self.tenant_id:
            result["tenant_id"] = self.tenant_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.service_name:
            result["service"] = self.service_name
        result.update(self.extra)
        return result


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Includes context, timestamp, and service metadata.
    """

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation/tenant/user from context
        correlation_id = _correlation_id.get()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        tenant_id = _tenant_id.get()
        if tenant_id:
            log_entry["tenant_id"] = tenant_id

        user_id = _user_id.get()
        if user_id:
            log_entry["user_id"] = user_id

        # Add extra fields from record
        if hasattr(record, "__dict__"):
            extras = {
                k: v
                for k, v in record.__dict__.items()
                if k
                not in (
                    "name",
                    "msg",
                    "args",
                    "created",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "stack_info",
                    "exc_info",
                    "exc_text",
                    "thread",
                    "threadName",
                    "message",
                    "asctime",
                )
                and not k.startswith("_")
            }
            if extras:
                log_entry["extra"] = extras

        # Add exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add location
        log_entry["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ServiceLogger:
    """
    Enhanced logger with context support for SAHOOL services.

    Provides:
    - Structured JSON logging
    - Automatic context inclusion (tenant, user, correlation)
    - Performance metrics
    - Bilingual message support
    """

    def __init__(
        self,
        name: str,
        service_name: str | None = None,
        level: int = logging.INFO,
        use_json: bool = True,
    ):
        self.name = name
        self.service_name = service_name or name
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        # Remove existing handlers
        self._logger.handlers.clear()

        # Configure handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        if use_json:
            handler.setFormatter(StructuredFormatter(self.service_name))
        else:
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        self._logger.addHandler(handler)
        self._logger.propagate = False

    def _log(
        self,
        level: int,
        message: str,
        message_ar: str | None = None,
        **kwargs,
    ):
        """Internal log method with context."""
        extra = {
            "correlation_id": _correlation_id.get(),
            "tenant_id": _tenant_id.get(),
            "user_id": _user_id.get(),
        }

        if message_ar:
            extra["message_ar"] = message_ar

        extra.update(kwargs)

        self._logger.log(level, message, extra=extra)

    def debug(self, message: str, message_ar: str | None = None, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, message_ar, **kwargs)

    def info(self, message: str, message_ar: str | None = None, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, message_ar, **kwargs)

    def warning(self, message: str, message_ar: str | None = None, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, message_ar, **kwargs)

    def error(
        self,
        message: str,
        message_ar: str | None = None,
        exc_info: bool = False,
        **kwargs,
    ):
        """Log error message."""
        if exc_info:
            self._logger.exception(message, extra=kwargs)
        else:
            self._log(logging.ERROR, message, message_ar, **kwargs)

    def critical(self, message: str, message_ar: str | None = None, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, message_ar, **kwargs)

    def set_context(
        self,
        correlation_id: str | None = None,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ):
        """Set context variables for subsequent log calls."""
        if correlation_id:
            _correlation_id.set(correlation_id)
        if tenant_id:
            _tenant_id.set(tenant_id)
        if user_id:
            _user_id.set(user_id)

    def clear_context(self):
        """Clear all context variables."""
        _correlation_id.set(None)
        _tenant_id.set(None)
        _user_id.set(None)


# Global logger registry
_loggers: dict[str, ServiceLogger] = {}


def get_service_logger(
    name: str,
    service_name: str | None = None,
    level: int | None = None,
    use_json: bool | None = None,
) -> ServiceLogger:
    """
    Get or create a service logger.

    Args:
        name: Logger name
        service_name: Service name for structured logs
        level: Log level (default from LOG_LEVEL env var)
        use_json: Whether to use JSON formatting (default from env)

    Returns:
        ServiceLogger instance
    """
    if name in _loggers:
        return _loggers[name]

    # Determine settings from environment
    if level is None:
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)

    if use_json is None:
        use_json = os.getenv("LOG_FORMAT", "json").lower() == "json"

    logger = ServiceLogger(
        name=name,
        service_name=service_name,
        level=level,
        use_json=use_json,
    )

    _loggers[name] = logger
    return logger


@contextmanager
def log_operation(
    logger: ServiceLogger,
    operation_name: str,
    log_start: bool = True,
    log_end: bool = True,
    **context,
):
    """
    Context manager for logging operation start/end with timing.

    Usage:
        with log_operation(logger, "process_field", field_id="FIELD-001"):
            result = process()
    """
    operation_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    if log_start:
        logger.info(
            f"Starting operation: {operation_name}",
            message_ar=f"بدء العملية: {operation_name}",
            operation=operation_name,
            operation_id=operation_id,
            **context,
        )

    try:
        yield operation_id
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            f"Operation failed: {operation_name}",
            message_ar=f"فشلت العملية: {operation_name}",
            operation=operation_name,
            operation_id=operation_id,
            duration_ms=round(duration_ms, 2),
            error=str(e),
            error_type=type(e).__name__,
            **context,
        )
        raise
    else:
        if log_end:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"Completed operation: {operation_name}",
                message_ar=f"اكتملت العملية: {operation_name}",
                operation=operation_name,
                operation_id=operation_id,
                duration_ms=round(duration_ms, 2),
                **context,
            )


def log_performance(
    logger: ServiceLogger,
    operation_name: str,
    warn_threshold_ms: float = 1000,
    error_threshold_ms: float = 5000,
):
    """
    Decorator for logging function performance.

    Args:
        logger: ServiceLogger instance
        operation_name: Name of the operation
        warn_threshold_ms: Log warning if duration exceeds this
        error_threshold_ms: Log error if duration exceeds this

    Usage:
        @log_performance(logger, "calculate_irrigation", warn_threshold_ms=500)
        async def calculate_irrigation(field_id: str):
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000

                log_data = {
                    "operation": operation_name,
                    "function": func.__name__,
                    "duration_ms": round(duration_ms, 2),
                }

                if duration_ms >= error_threshold_ms:
                    logger.error(
                        f"Performance critical: {operation_name} took {duration_ms:.2f}ms",
                        message_ar=f"أداء حرج: استغرقت {operation_name} {duration_ms:.2f} مللي ثانية",
                        **log_data,
                    )
                elif duration_ms >= warn_threshold_ms:
                    logger.warning(
                        f"Performance warning: {operation_name} took {duration_ms:.2f}ms",
                        message_ar=f"تحذير أداء: استغرقت {operation_name} {duration_ms:.2f} مللي ثانية",
                        **log_data,
                    )
                else:
                    logger.debug(
                        f"Performance: {operation_name} took {duration_ms:.2f}ms",
                        **log_data,
                    )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000

                log_data = {
                    "operation": operation_name,
                    "function": func.__name__,
                    "duration_ms": round(duration_ms, 2),
                }

                if duration_ms >= error_threshold_ms:
                    logger.error(
                        f"Performance critical: {operation_name} took {duration_ms:.2f}ms",
                        **log_data,
                    )
                elif duration_ms >= warn_threshold_ms:
                    logger.warning(
                        f"Performance warning: {operation_name} took {duration_ms:.2f}ms",
                        **log_data,
                    )
                else:
                    logger.debug(
                        f"Performance: {operation_name} took {duration_ms:.2f}ms",
                        **log_data,
                    )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Import asyncio for checking coroutine functions
import asyncio
