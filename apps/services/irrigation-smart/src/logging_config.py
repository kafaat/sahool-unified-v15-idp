"""
SAHOOL Irrigation Smart Service - Logging Configuration
=========================================================
Provides structured logging for irrigation service with context.

Features:
- Structured JSON logging
- Context propagation (tenant, user, field)
- Performance metrics logging
- Irrigation event tracking
- Arabic/English bilingual log messages
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import wraps
from typing import Any

# Context variables for request tracking
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_tenant_id: ContextVar[str | None] = ContextVar("tenant_id", default=None)
_user_id: ContextVar[str | None] = ContextVar("user_id", default=None)
_field_id: ContextVar[str | None] = ContextVar("field_id", default=None)


@dataclass
class IrrigationLogContext:
    """Context for irrigation-specific logging."""

    field_id: str | None = None
    crop: str | None = None
    water_amount_m3: float | None = None
    urgency: str | None = None
    method: str | None = None


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, service_name: str = "irrigation-smart"):
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

        # Add context from context variables
        correlation_id = _correlation_id.get()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        tenant_id = _tenant_id.get()
        if tenant_id:
            log_entry["tenant_id"] = tenant_id

        user_id = _user_id.get()
        if user_id:
            log_entry["user_id"] = user_id

        field_id = _field_id.get()
        if field_id:
            log_entry["field_id"] = field_id

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in (
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
            ) and not key.startswith("_"):
                log_entry[key] = value

        # Add exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class IrrigationLogger:
    """Enhanced logger for irrigation service."""

    def __init__(
        self,
        name: str = "irrigation-smart",
        level: int = logging.INFO,
        use_json: bool = True,
    ):
        self.name = name
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.handlers.clear()

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        if use_json:
            handler.setFormatter(StructuredFormatter(name))
        else:
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        self._logger.addHandler(handler)
        self._logger.propagate = False

    def set_context(
        self,
        correlation_id: str | None = None,
        tenant_id: str | None = None,
        user_id: str | None = None,
        field_id: str | None = None,
    ):
        """Set context for subsequent log calls."""
        if correlation_id:
            _correlation_id.set(correlation_id)
        if tenant_id:
            _tenant_id.set(tenant_id)
        if user_id:
            _user_id.set(user_id)
        if field_id:
            _field_id.set(field_id)

    def clear_context(self):
        """Clear all context variables."""
        _correlation_id.set(None)
        _tenant_id.set(None)
        _user_id.set(None)
        _field_id.set(None)

    def _log(
        self,
        level: int,
        message: str,
        message_ar: str | None = None,
        **kwargs,
    ):
        """Internal log method with context."""
        if message_ar:
            kwargs["message_ar"] = message_ar

        self._logger.log(level, message, extra=kwargs)

    def debug(self, message: str, message_ar: str | None = None, **kwargs):
        self._log(logging.DEBUG, message, message_ar, **kwargs)

    def info(self, message: str, message_ar: str | None = None, **kwargs):
        self._log(logging.INFO, message, message_ar, **kwargs)

    def warning(self, message: str, message_ar: str | None = None, **kwargs):
        self._log(logging.WARNING, message, message_ar, **kwargs)

    def error(
        self,
        message: str,
        message_ar: str | None = None,
        exc_info: bool = False,
        **kwargs,
    ):
        if exc_info:
            self._logger.exception(message, extra=kwargs)
        else:
            self._log(logging.ERROR, message, message_ar, **kwargs)

    # ─────────────────────────────────────────────────────────────────────────
    # Irrigation-Specific Logging
    # ─────────────────────────────────────────────────────────────────────────

    def log_irrigation_plan_created(
        self,
        plan_id: str,
        field_id: str,
        crop: str,
        water_m3: float,
        schedules_count: int,
        urgency: str,
    ):
        """Log irrigation plan creation."""
        self.info(
            f"Irrigation plan created: {plan_id}",
            message_ar=f"تم إنشاء خطة الري: {plan_id}",
            event_type="irrigation_plan_created",
            plan_id=plan_id,
            field_id=field_id,
            crop=crop,
            water_m3=water_m3,
            schedules_count=schedules_count,
            urgency=urgency,
        )

    def log_irrigation_executed(
        self,
        execution_id: str,
        field_id: str,
        amount_mm: float,
        duration_minutes: int,
        method: str,
    ):
        """Log irrigation execution."""
        self.info(
            f"Irrigation executed: {execution_id}",
            message_ar=f"تم تنفيذ الري: {execution_id}",
            event_type="irrigation_executed",
            execution_id=execution_id,
            field_id=field_id,
            amount_mm=amount_mm,
            duration_minutes=duration_minutes,
            method=method,
        )

    def log_sensor_reading(
        self,
        sensor_id: str,
        field_id: str,
        moisture_percent: float,
        status: str,
    ):
        """Log sensor reading processed."""
        self.info(
            f"Sensor reading processed: {sensor_id}",
            message_ar=f"تمت معالجة قراءة المستشعر: {sensor_id}",
            event_type="sensor_reading",
            sensor_id=sensor_id,
            field_id=field_id,
            moisture_percent=moisture_percent,
            status=status,
        )

    def log_water_deficit_alert(
        self,
        field_id: str,
        deficit_mm: float,
        urgency: str,
        recommended_action: str,
    ):
        """Log water deficit alert."""
        self.warning(
            f"Water deficit alert for field {field_id}: {deficit_mm}mm",
            message_ar=f"تنبيه عجز مائي للحقل {field_id}: {deficit_mm} ملم",
            event_type="water_deficit_alert",
            field_id=field_id,
            deficit_mm=deficit_mm,
            urgency=urgency,
            recommended_action=recommended_action,
        )

    def log_calculation_error(
        self,
        field_id: str,
        operation: str,
        error: str,
    ):
        """Log calculation error."""
        self.error(
            f"Calculation error for {operation} on field {field_id}: {error}",
            message_ar=f"خطأ في حساب {operation} للحقل {field_id}",
            event_type="calculation_error",
            field_id=field_id,
            operation=operation,
            error=error,
        )


# Global logger instance
_irrigation_logger: IrrigationLogger | None = None


def get_irrigation_logger() -> IrrigationLogger:
    """Get the global irrigation logger instance."""
    global _irrigation_logger
    if _irrigation_logger is None:
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)
        use_json = os.getenv("LOG_FORMAT", "json").lower() == "json"

        _irrigation_logger = IrrigationLogger(
            name="irrigation-smart",
            level=level,
            use_json=use_json,
        )
    return _irrigation_logger


def log_performance(operation_name: str, warn_threshold_ms: float = 500):
    """Decorator for logging function performance."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_irrigation_logger()
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000

                if duration_ms >= warn_threshold_ms:
                    logger.warning(
                        f"Slow operation: {operation_name} took {duration_ms:.2f}ms",
                        message_ar=f"عملية بطيئة: استغرقت {operation_name} {duration_ms:.2f} مللي ثانية",
                        operation=operation_name,
                        duration_ms=round(duration_ms, 2),
                    )
                else:
                    logger.debug(
                        f"Operation {operation_name} completed in {duration_ms:.2f}ms",
                        operation=operation_name,
                        duration_ms=round(duration_ms, 2),
                    )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_irrigation_logger()
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000

                if duration_ms >= warn_threshold_ms:
                    logger.warning(
                        f"Slow operation: {operation_name} took {duration_ms:.2f}ms",
                        operation=operation_name,
                        duration_ms=round(duration_ms, 2),
                    )

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
