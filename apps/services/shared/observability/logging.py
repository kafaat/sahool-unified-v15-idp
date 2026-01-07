"""
Logging Configuration for Python Services
إعدادات التسجيل لخدمات Python

Provides structured logging with JSON output for production
and human-readable output for development.

Features:
- Structured JSON logging for production
- Colored output for development
- Request context propagation
- Sensitive data masking
- Correlation IDs
"""

import json
import logging
import re
import sys
import traceback
from contextvars import ContextVar
from datetime import datetime
from typing import Any

# Context variables for request tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
tenant_id_var: ContextVar[str] = ContextVar("tenant_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class SensitiveDataMasker:
    """
    Utility class for masking sensitive data in logs.
    فئة مساعدة لإخفاء البيانات الحساسة في السجلات.
    """

    # Patterns for sensitive data
    PATTERNS = {
        # API Keys and Tokens
        "api_key": re.compile(
            r'(["\']?(?:api[-_]?key|apikey)["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})(["\']?)',
            re.IGNORECASE,
        ),
        "bearer_token": re.compile(r"(Bearer\s+)([a-zA-Z0-9_\-\.]+)", re.IGNORECASE),
        "access_token": re.compile(
            r'(["\']?(?:access[-_]?token|token)["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-\.]{20,})(["\']?)',
            re.IGNORECASE,
        ),
        # Passwords
        "password": re.compile(
            r'(["\']?(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?)([^"\'}\s,]{3,})(["\']?)',
            re.IGNORECASE,
        ),
        # Authorization headers
        "auth_header": re.compile(r"(Authorization\s*:\s*)(.+?)(\s|$)", re.IGNORECASE),
        # Database URLs with credentials
        "database_url": re.compile(
            r"((?:postgresql|mysql|mongodb)://[^:]+:)([^@]+)(@)", re.IGNORECASE
        ),
        # AWS Keys
        "aws_access_key": re.compile(r"((?:AKIA|ASIA)[A-Z0-9]{16})"),
        "aws_secret_key": re.compile(
            r'(["\']?aws[-_]?secret[-_]?(?:access[-_]?)?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9/+=]{40})(["\']?)',
            re.IGNORECASE,
        ),
        # Google Cloud Keys
        "gcp_key": re.compile(
            r'(["\']?private[-_]?key["\']?\s*[:=]\s*["\']?)(-----BEGIN PRIVATE KEY-----[^-]+-----END PRIVATE KEY-----)(["\']?)',
            re.IGNORECASE,
        ),
        # JWT Tokens
        "jwt": re.compile(
            r"(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})"
        ),
        # Credit Card Numbers (basic pattern)
        "credit_card": re.compile(r"\b([0-9]{4}[\s\-]?){3}[0-9]{4}\b"),
        # Email addresses (optional - only mask domain part)
        "email": re.compile(r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"),
        # IP Addresses (optional - only mask last octet)
        "ip_address": re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.)(\d{1,3})\b"),
        # Phone Numbers (international format)
        "phone": re.compile(r"\+?[1-9]\d{1,14}"),
    }

    # Sensitive field names to mask completely
    SENSITIVE_FIELDS = {
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
        "auth",
        "token",
        "credential",
        "credentials",
    }

    @classmethod
    def mask_string(
        cls, text: str, mask_char: str = "*", preserve_length: bool = False
    ) -> str:
        """
        Mask sensitive data in a string.
        إخفاء البيانات الحساسة في سلسلة نصية.

        Args:
            text: Input text
            mask_char: Character to use for masking
            preserve_length: Whether to preserve the length of masked values

        Returns:
            Masked text
        """
        if not isinstance(text, str):
            return text

        result = text

        # Apply all patterns
        for pattern_name, pattern in cls.PATTERNS.items():
            if pattern_name == "password" or pattern_name == "api_key":
                result = pattern.sub(r"\1***REDACTED***\3", result)
            elif pattern_name == "bearer_token":
                result = pattern.sub(r"\1***REDACTED***", result)
            elif pattern_name == "access_token" or pattern_name == "auth_header" or pattern_name == "database_url":
                result = pattern.sub(r"\1***REDACTED***\3", result)
            elif pattern_name == "aws_access_key":
                result = pattern.sub(r"***AWS_KEY_REDACTED***", result)
            elif pattern_name == "aws_secret_key":
                result = pattern.sub(r"\1***REDACTED***\3", result)
            elif pattern_name == "gcp_key":
                result = pattern.sub(r"\1***GCP_KEY_REDACTED***\3", result)
            elif pattern_name == "jwt":
                result = pattern.sub(r"***JWT_REDACTED***", result)
            elif pattern_name == "credit_card":
                result = pattern.sub(r"****-****-****-****", result)
            elif pattern_name == "email":
                # Partially mask email
                result = pattern.sub(r"\1@***", result)
            elif pattern_name == "ip_address":
                # Mask last octet
                result = pattern.sub(r"\1***", result)
            elif pattern_name == "phone":
                result = pattern.sub(r"***PHONE***", result)

        return result

    @classmethod
    def mask_dict(cls, data: dict[str, Any], deep: bool = True) -> dict[str, Any]:
        """
        Mask sensitive data in a dictionary.
        إخفاء البيانات الحساسة في قاموس.

        Args:
            data: Input dictionary
            deep: Whether to recursively mask nested dictionaries

        Returns:
            Masked dictionary
        """
        if not isinstance(data, dict):
            return data

        result = {}

        for key, value in data.items():
            # Check if key is sensitive
            if any(sensitive in key.lower() for sensitive in cls.SENSITIVE_FIELDS):
                result[key] = "***REDACTED***"
            elif isinstance(value, str):
                result[key] = cls.mask_string(value)
            elif isinstance(value, dict) and deep:
                result[key] = cls.mask_dict(value, deep=True)
            elif isinstance(value, list | tuple) and deep:
                result[key] = [
                    (
                        cls.mask_dict(item, deep=True)
                        if isinstance(item, dict)
                        else cls.mask_string(item) if isinstance(item, str) else item
                    )
                    for item in value
                ]
            else:
                result[key] = value

        return result

    @classmethod
    def mask_value(cls, value: Any) -> Any:
        """
        Mask sensitive data in any value.
        إخفاء البيانات الحساسة في أي قيمة.
        """
        if isinstance(value, str):
            return cls.mask_string(value)
        elif isinstance(value, dict):
            return cls.mask_dict(value)
        elif isinstance(value, list | tuple):
            return [cls.mask_value(item) for item in value]
        else:
            return value


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.
    منسق JSON للتسجيل المنظم في الإنتاج.

    Supports sensitive data masking for security.
    """

    def __init__(self, mask_sensitive: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mask_sensitive = mask_sensitive

    def format(self, record: logging.LogRecord) -> str:
        # Get base message
        message = record.getMessage()

        # Mask sensitive data in message if enabled
        if self.mask_sensitive:
            message = SensitiveDataMasker.mask_string(message)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "service": getattr(record, "service", "unknown"),
        }

        # Add context from context vars
        if request_id := request_id_var.get():
            log_entry["request_id"] = request_id
        if tenant_id := tenant_id_var.get():
            log_entry["tenant_id"] = tenant_id
        if user_id := user_id_var.get():
            log_entry["user_id"] = user_id

        # Add extra fields
        if hasattr(record, "extra_fields"):
            extra_fields = record.extra_fields
            # Mask sensitive data in extra fields
            if self.mask_sensitive:
                extra_fields = SensitiveDataMasker.mask_dict(extra_fields)
            log_entry.update(extra_fields)

        # Add exception info
        if record.exc_info:
            exc_message = str(record.exc_info[1]) if record.exc_info[1] else None
            # Mask sensitive data in exception message
            if self.mask_sensitive and exc_message:
                exc_message = SensitiveDataMasker.mask_string(exc_message)

            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": exc_message,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add source location
        log_entry["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for development.
    منسق ملون للتطوير.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

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

        message = " ".join(parts)

        # Add exception if present
        if record.exc_info:
            message += "\n" + "".join(traceback.format_exception(*record.exc_info))

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
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        """Internal log method with extra fields support."""
        record_extra = {
            "service": self.service_name,
        }
        if extra:
            record_extra["extra_fields"] = extra

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
        self._log(
            logging.CRITICAL, message, kwargs if kwargs else None, exc_info=exc_info
        )

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._log(logging.ERROR, message, kwargs if kwargs else None, exc_info=True)


def setup_logging(
    service_name: str,
    level: str = "INFO",
    json_output: bool = True,
    mask_sensitive: bool = True,
) -> ServiceLogger:
    """
    Setup logging for a service.
    إعداد التسجيل لخدمة.

    Args:
        service_name: Name of the service
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Use JSON format (True for production, False for development)
        mask_sensitive: Mask sensitive data in logs (recommended for production)

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
        handler.setFormatter(JSONFormatter(mask_sensitive=mask_sensitive))
    else:
        handler.setFormatter(ColoredFormatter())

    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return ServiceLogger(service_name, logger)


def set_request_context(
    request_id: str | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
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
    request_id_var.set("")
    tenant_id_var.set("")
    user_id_var.set("")


# Convenience function to get logger
def get_logger(service_name: str) -> ServiceLogger:
    """
    Get a logger for a service.
    الحصول على مسجل لخدمة.
    """
    import os

    env = os.getenv("ENVIRONMENT", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    json_output = env == "production"

    return setup_logging(service_name, log_level, json_output)
