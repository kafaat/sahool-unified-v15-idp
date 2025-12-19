"""
Logging Configuration for Python Services
إعدادات التسجيل لخدمات Python

Provides structured logging with JSON output for production
and human-readable output for development.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Optional
from contextvars import ContextVar
import traceback

# Context variables for request tracing
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
tenant_id_var: ContextVar[str] = ContextVar('tenant_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.
    منسق JSON للتسجيل المنظم في الإنتاج.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'service': getattr(record, 'service', 'unknown'),
        }

        # Add context from context vars
        if request_id := request_id_var.get():
            log_entry['request_id'] = request_id
        if tenant_id := tenant_id_var.get():
            log_entry['tenant_id'] = tenant_id
        if user_id := user_id_var.get():
            log_entry['user_id'] = user_id

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception info
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info),
            }

        # Add source location
        log_entry['source'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName,
        }

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for development.
    منسق ملون للتطوير.
    """

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Build message
        parts = [
            f"{color}[{record.levelname:8}]{self.RESET}",
            f"[{timestamp}]",
            f"[{record.name}]",
        ]

        # Add context
        if request_id := request_id_var.get():
            parts.append(f"[req:{request_id[:8]}]")

        parts.append(record.getMessage())

        message = ' '.join(parts)

        # Add exception if present
        if record.exc_info:
            message += '\n' + ''.join(traceback.format_exception(*record.exc_info))

        return message


class ServiceLogger:
    """
    Service-specific logger with context support.
    مسجل خاص بالخدمة مع دعم السياق.
    """

    def __init__(self, service_name: str, logger: logging.Logger):
        self.service_name = service_name
        self.logger = logger

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Internal log method with extra fields support."""
        record_extra = {
            'service': self.service_name,
        }
        if extra:
            record_extra['extra_fields'] = extra

        self.logger.log(level, message, extra=record_extra, exc_info=exc_info)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, kwargs if kwargs else None)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, message, kwargs if kwargs else None)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, kwargs if kwargs else None)

    def error(self, message: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, kwargs if kwargs else None, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, kwargs if kwargs else None, exc_info=exc_info)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._log(logging.ERROR, message, kwargs if kwargs else None, exc_info=True)


def setup_logging(
    service_name: str,
    level: str = 'INFO',
    json_output: bool = True,
) -> ServiceLogger:
    """
    Setup logging for a service.
    إعداد التسجيل لخدمة.

    Args:
        service_name: Name of the service
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Use JSON format (True for production, False for development)

    Returns:
        ServiceLogger instance
    """
    # Get or create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Set formatter based on environment
    if json_output:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(ColoredFormatter())

    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return ServiceLogger(service_name, logger)


def set_request_context(
    request_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """
    Set request context for logging.
    تعيين سياق الطلب للتسجيل.
    """
    if request_id:
        request_id_var.set(request_id)
    if tenant_id:
        tenant_id_var.set(tenant_id)
    if user_id:
        user_id_var.set(user_id)


def clear_request_context() -> None:
    """
    Clear request context.
    مسح سياق الطلب.
    """
    request_id_var.set('')
    tenant_id_var.set('')
    user_id_var.set('')


# Convenience function to get logger
def get_logger(service_name: str) -> ServiceLogger:
    """
    Get a logger for a service.
    الحصول على مسجل لخدمة.
    """
    import os

    env = os.getenv('ENVIRONMENT', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    json_output = env == 'production'

    return setup_logging(service_name, log_level, json_output)
