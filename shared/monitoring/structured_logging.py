"""
SAHOOL Platform - Enhanced Structured Logging
التسجيل المنظم المحسّن

Provides production-grade structured logging with:
- JSON output for log aggregation (ELK, Loki, etc.)
- OpenTelemetry trace correlation
- Sensitive data masking
- Agricultural domain context
- Request/response logging
- Performance metrics integration
"""

from __future__ import annotations

import json
import logging
import sys
import traceback
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from functools import wraps
from typing import Any

# Context variables for distributed tracing
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
span_id_var: ContextVar[str] = ContextVar("span_id", default="")
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
tenant_id_var: ContextVar[str] = ContextVar("tenant_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
field_id_var: ContextVar[str] = ContextVar("field_id", default="")
operation_var: ContextVar[str] = ContextVar("operation", default="")


class LogLevel(StrEnum):
    """Log level enumeration"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(StrEnum):
    """Log categories for filtering and routing"""

    # Infrastructure
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    HEALTH = "health"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"

    # HTTP/API
    REQUEST = "request"
    RESPONSE = "response"
    AUTH = "auth"
    RATE_LIMIT = "rate_limit"

    # Business Logic
    FIELD = "field"
    CROP = "crop"
    IRRIGATION = "irrigation"
    WEATHER = "weather"
    ADVISORY = "advisory"
    HARVEST = "harvest"

    # AI/ML
    AI_INFERENCE = "ai_inference"
    MODEL_TRAINING = "model_training"
    NDVI = "ndvi"
    VISION = "vision"

    # IoT
    SENSOR = "sensor"
    DEVICE = "device"
    TELEMETRY = "telemetry"

    # Security
    SECURITY = "security"
    AUDIT = "audit"

    # Other
    GENERAL = "general"
    PERFORMANCE = "performance"
    ERROR = "error"


@dataclass
class LogContext:
    """
    Structured log context.
    سياق السجل المنظم.
    """

    # Distributed tracing
    trace_id: str = ""
    span_id: str = ""
    request_id: str = ""

    # Multi-tenancy
    tenant_id: str = ""
    user_id: str = ""

    # Agricultural domain
    field_id: str = ""
    farm_id: str = ""
    crop_type: str = ""
    region: str = ""

    # Service context
    service_name: str = ""
    service_version: str = ""
    environment: str = ""
    instance_id: str = ""

    # Operation context
    operation: str = ""
    method: str = ""
    path: str = ""
    status_code: int = 0
    duration_ms: float = 0.0

    # Additional fields
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}

        # Add non-empty fields
        for key, value in self.__dict__.items():
            if key == "extra":
                result.update(value)
            elif value:
                result[key] = value

        return result

    @classmethod
    def from_context_vars(cls) -> LogContext:
        """Create context from context variables."""
        return cls(
            trace_id=trace_id_var.get(),
            span_id=span_id_var.get(),
            request_id=request_id_var.get(),
            tenant_id=tenant_id_var.get(),
            user_id=user_id_var.get(),
            field_id=field_id_var.get(),
            operation=operation_var.get(),
        )


class SensitivePatterns:
    """
    Patterns for masking sensitive data.
    أنماط إخفاء البيانات الحساسة.
    """

    # Fields to completely redact
    REDACT_FIELDS = {
        "password",
        "passwd",
        "pwd",
        "secret",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "private_key",
        "client_secret",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "jwt",
        "token",
    }

    # Fields to partially mask
    PARTIAL_MASK_FIELDS = {
        "email",
        "phone",
        "mobile",
        "ssn",
        "national_id",
    }

    @classmethod
    def mask_value(cls, key: str, value: Any) -> Any:
        """Mask sensitive values based on key name."""
        if not isinstance(value, str):
            return value

        key_lower = key.lower()

        # Check for complete redaction
        for redact_field in cls.REDACT_FIELDS:
            if redact_field in key_lower:
                return "***REDACTED***"

        # Check for partial masking
        for mask_field in cls.PARTIAL_MASK_FIELDS:
            if mask_field in key_lower:
                if len(value) > 4:
                    return value[:2] + "*" * (len(value) - 4) + value[-2:]
                return "***"

        return value

    @classmethod
    def mask_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively mask sensitive data in dictionary."""
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = cls.mask_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    cls.mask_dict(item) if isinstance(item, dict) else cls.mask_value(key, item) for item in value
                ]
            else:
                result[key] = cls.mask_value(key, value)
        return result


class StructuredJSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    منسق JSON للتسجيل المنظم.

    Outputs logs in a format compatible with:
    - ELK Stack (Elasticsearch, Logstash, Kibana)
    - Grafana Loki
    - Google Cloud Logging
    - AWS CloudWatch
    """

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        environment: str = "development",
        mask_sensitive: bool = True,
    ):
        super().__init__()
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.mask_sensitive = mask_sensitive

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""

        # Base log entry
        log_entry = {
            "@timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": {
                "name": self.service_name,
                "version": self.service_version,
                "environment": self.environment,
            },
        }

        # Add source location
        log_entry["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add context from context variables
        context = LogContext.from_context_vars()
        context_dict = context.to_dict()
        if context_dict:
            log_entry["context"] = context_dict

        # Add category if provided
        if hasattr(record, "category"):
            log_entry["category"] = record.category

        # Add extra fields
        if hasattr(record, "structured_data"):
            data = record.structured_data
            if self.mask_sensitive:
                data = SensitivePatterns.mask_dict(data)
            log_entry["data"] = data

        # Add exception info
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            log_entry["error"] = {
                "type": exc_type.__name__ if exc_type else None,
                "message": str(exc_value) if exc_value else None,
                "stack_trace": traceback.format_exception(exc_type, exc_value, exc_tb),
            }

        # Add performance metrics if available
        if hasattr(record, "duration_ms"):
            log_entry["performance"] = {
                "duration_ms": record.duration_ms,
            }

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored formatter for development console output.
    منسق ملون لمخرجات وحدة التحكم في التطوير.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format timestamp
        timestamp = datetime.now(UTC).strftime("%H:%M:%S.%f")[:-3]

        # Build parts
        parts = [
            f"{self.DIM}[{timestamp}]{self.RESET}",
            f"{color}[{record.levelname:8}]{self.RESET}",
            f"{self.BOLD}[{record.name}]{self.RESET}",
        ]

        # Add context
        if trace_id := trace_id_var.get():
            parts.append(f"{self.DIM}[trace:{trace_id[:8]}]{self.RESET}")
        if request_id := request_id_var.get():
            parts.append(f"{self.DIM}[req:{request_id[:8]}]{self.RESET}")

        parts.append(record.getMessage())

        message = " ".join(parts)

        # Add structured data if present
        if hasattr(record, "structured_data") and record.structured_data:
            data_str = json.dumps(record.structured_data, indent=2, ensure_ascii=False)
            message += f"\n{self.DIM}{data_str}{self.RESET}"

        # Add exception if present
        if record.exc_info:
            message += "\n" + "".join(traceback.format_exception(*record.exc_info))

        return message


class StructuredLogger:
    """
    Structured logger with domain context support.
    مسجل منظم مع دعم سياق المجال.
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        json_output: bool = True,
        service_name: str = "",
        service_version: str = "1.0.0",
        environment: str = "development",
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()
        self.service_name = service_name or name

        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))

        if json_output:
            handler.setFormatter(
                StructuredJSONFormatter(
                    service_name=self.service_name,
                    service_version=service_version,
                    environment=environment,
                )
            )
        else:
            handler.setFormatter(ColoredConsoleFormatter())

        self.logger.addHandler(handler)
        self.logger.propagate = False

    def _log(
        self,
        level: int,
        message: str,
        category: LogCategory | str = LogCategory.GENERAL,
        exc_info: bool = False,
        **kwargs: Any,
    ) -> None:
        """Internal log method with structured data support."""
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=exc_info if exc_info else None,
        )

        # Add category
        record.category = category.value if isinstance(category, LogCategory) else category

        # Add structured data
        if kwargs:
            record.structured_data = kwargs

        self.logger.handle(record)

    def debug(self, message: str, category: LogCategory = LogCategory.GENERAL, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, category, **kwargs)

    def info(self, message: str, category: LogCategory = LogCategory.GENERAL, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, message, category, **kwargs)

    def warning(self, message: str, category: LogCategory = LogCategory.GENERAL, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, category, **kwargs)

    def error(
        self,
        message: str,
        category: LogCategory = LogCategory.ERROR,
        exc_info: bool = True,
        **kwargs: Any,
    ) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, category, exc_info=exc_info, **kwargs)

    def critical(
        self,
        message: str,
        category: LogCategory = LogCategory.ERROR,
        exc_info: bool = True,
        **kwargs: Any,
    ) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, category, exc_info=exc_info, **kwargs)

    # Domain-specific logging methods
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs: Any,
    ) -> None:
        """Log HTTP request."""
        self.info(
            f"{method} {path} {status_code} ({duration_ms:.2f}ms)",
            category=LogCategory.REQUEST,
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_database_query(
        self,
        query_type: str,
        table: str,
        duration_ms: float,
        rows_affected: int = 0,
        **kwargs: Any,
    ) -> None:
        """Log database query."""
        self.debug(
            f"DB {query_type} on {table} ({duration_ms:.2f}ms, {rows_affected} rows)",
            category=LogCategory.DATABASE,
            query_type=query_type,
            table=table,
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            **kwargs,
        )

    def log_field_event(
        self,
        event_type: str,
        field_id: str,
        **kwargs: Any,
    ) -> None:
        """Log field-related event."""
        self.info(
            f"Field event: {event_type} for field {field_id}",
            category=LogCategory.FIELD,
            event_type=event_type,
            field_id=field_id,
            **kwargs,
        )

    def log_ai_inference(
        self,
        model_name: str,
        duration_ms: float,
        success: bool = True,
        **kwargs: Any,
    ) -> None:
        """Log AI model inference."""
        status = "success" if success else "failure"
        self.info(
            f"AI inference {model_name}: {status} ({duration_ms:.2f}ms)",
            category=LogCategory.AI_INFERENCE,
            model_name=model_name,
            duration_ms=duration_ms,
            success=success,
            **kwargs,
        )

    def log_sensor_reading(
        self,
        device_id: str,
        sensor_type: str,
        value: float,
        unit: str = "",
        **kwargs: Any,
    ) -> None:
        """Log IoT sensor reading."""
        self.debug(
            f"Sensor {device_id}/{sensor_type}: {value}{unit}",
            category=LogCategory.SENSOR,
            device_id=device_id,
            sensor_type=sensor_type,
            value=value,
            unit=unit,
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Context Management | إدارة السياق
# ═══════════════════════════════════════════════════════════════════════════════


def set_log_context(
    trace_id: str | None = None,
    span_id: str | None = None,
    request_id: str | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
    field_id: str | None = None,
    operation: str | None = None,
) -> None:
    """
    Set logging context variables.
    تعيين متغيرات سياق التسجيل.
    """
    if trace_id:
        trace_id_var.set(trace_id)
    if span_id:
        span_id_var.set(span_id)
    if request_id:
        request_id_var.set(request_id)
    if tenant_id:
        tenant_id_var.set(tenant_id)
    if user_id:
        user_id_var.set(user_id)
    if field_id:
        field_id_var.set(field_id)
    if operation:
        operation_var.set(operation)


def clear_log_context() -> None:
    """
    Clear all logging context variables.
    مسح جميع متغيرات سياق التسجيل.
    """
    trace_id_var.set("")
    span_id_var.set("")
    request_id_var.set("")
    tenant_id_var.set("")
    user_id_var.set("")
    field_id_var.set("")
    operation_var.set("")


def log_operation(operation: str, category: LogCategory = LogCategory.GENERAL):
    """
    Decorator to log function execution with timing.
    مزخرف لتسجيل تنفيذ الدالة مع التوقيت.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            import time

            operation_var.set(operation)
            start = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                logging.getLogger(func.__module__).info(f"Operation {operation} completed in {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logging.getLogger(func.__module__).error(
                    f"Operation {operation} failed after {duration_ms:.2f}ms: {e}",
                    exc_info=True,
                )
                raise
            finally:
                operation_var.set("")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time

            operation_var.set(operation)
            start = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                logging.getLogger(func.__module__).info(f"Operation {operation} completed in {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logging.getLogger(func.__module__).error(
                    f"Operation {operation} failed after {duration_ms:.2f}ms: {e}",
                    exc_info=True,
                )
                raise
            finally:
                operation_var.set("")

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# Factory Functions | دوال المصنع
# ═══════════════════════════════════════════════════════════════════════════════


def get_structured_logger(
    name: str,
    level: str | None = None,
    json_output: bool | None = None,
) -> StructuredLogger:
    """
    Get a structured logger instance.
    الحصول على مثيل مسجل منظم.
    """
    import os

    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")

    if json_output is None:
        json_output = os.getenv("ENVIRONMENT", "development") == "production"

    return StructuredLogger(
        name=name,
        level=level,
        json_output=json_output,
        service_name=name,
        service_version=os.getenv("SERVICE_VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "development"),
    )
