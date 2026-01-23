"""
SAHOOL Shared Exceptions Module
===============================
وحدة الاستثناءات المشتركة لمنصة سهول

Provides a unified exception hierarchy for all shared modules in the SAHOOL platform.
This module ensures consistent error handling, logging, and API responses across services.

Features:
    - Base exception with bilingual support (Arabic/English)
    - Structured error codes for categorization
    - Exception chaining and context preservation
    - HTTP status code mapping
    - Serialization for API responses

Author: SAHOOL Platform Team
Updated: January 2026

Example:
    >>> from shared.exceptions import (
    ...     SahoolBaseException,
    ...     ValidationError,
    ...     NotFoundError,
    ...     ServiceUnavailableError,
    ... )
    >>> raise ValidationError(
    ...     message="Invalid field format",
    ...     message_ar="تنسيق الحقل غير صالح",
    ...     field="field_name"
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ErrorCategory(str, Enum):
    """
    Categories for grouping related errors.
    فئات لتجميع الأخطاء ذات الصلة
    """

    VALIDATION = "validation"  # Input validation errors
    AUTHENTICATION = "authentication"  # Auth-related errors
    AUTHORIZATION = "authorization"  # Permission errors
    NOT_FOUND = "not_found"  # Resource not found
    CONFLICT = "conflict"  # State conflicts
    RATE_LIMIT = "rate_limit"  # Rate limiting
    SERVICE = "service"  # External service errors
    DATABASE = "database"  # Database errors
    CACHE = "cache"  # Cache errors
    MESSAGING = "messaging"  # Message queue errors
    AI = "ai"  # AI/ML related errors
    INTERNAL = "internal"  # Internal server errors


class ErrorSeverity(str, Enum):
    """
    Severity levels for error logging and alerting.
    مستويات شدة الأخطاء للتسجيل والتنبيه
    """

    DEBUG = "debug"  # Development only
    INFO = "info"  # Informational
    WARNING = "warning"  # Recoverable issues
    ERROR = "error"  # Operational errors
    CRITICAL = "critical"  # System failures


@dataclass
class ErrorContext:
    """
    Additional context information for errors.
    معلومات سياق إضافية للأخطاء
    """

    request_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    service_name: str | None = None
    operation: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        result = {
            "timestamp": self.timestamp.isoformat(),
        }
        if self.request_id:
            result["request_id"] = self.request_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.tenant_id:
            result["tenant_id"] = self.tenant_id
        if self.service_name:
            result["service_name"] = self.service_name
        if self.operation:
            result["operation"] = self.operation
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class SahoolBaseException(Exception):
    """
    Base exception class for all SAHOOL platform exceptions.
    فئة الاستثناء الأساسية لجميع استثناءات منصة سهول

    All custom exceptions in shared modules should inherit from this class
    to ensure consistent error handling and response formatting.

    Attributes:
        message: Error message in English
        message_ar: Error message in Arabic
        code: Unique error code for identification
        category: Error category for grouping
        severity: Error severity level
        status_code: HTTP status code for API responses
        details: Additional error details
        context: Error context information
        cause: Original exception that caused this error

    Example:
        >>> try:
        ...     # Some operation
        ...     pass
        ... except SomeError as e:
        ...     raise SahoolBaseException(
        ...         message="Operation failed",
        ...         message_ar="فشلت العملية",
        ...         code="E1001",
        ...         cause=e
        ...     )
    """

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        code: str = "E0000",
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        """
        Initialize SahoolBaseException.

        Args:
            message: Human-readable error message in English
            message_ar: Human-readable error message in Arabic (defaults to English)
            code: Unique error code (e.g., "E1001", "AUTH001")
            category: Category for grouping related errors
            severity: Severity level for logging/alerting
            status_code: HTTP status code for API responses
            details: Additional structured error information
            context: Request/operation context
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.message_ar = message_ar or message
        self.code = code
        self.category = category
        self.severity = severity
        self.status_code = status_code
        self.details = details or {}
        self.context = context or ErrorContext()
        self.cause = cause

        # Set the cause for exception chaining
        if cause:
            self.__cause__ = cause

    def to_dict(self, lang: str = "en", include_context: bool = False) -> dict[str, Any]:
        """
        Convert exception to dictionary for API responses.

        Args:
            lang: Language code ('en' for English, 'ar' for Arabic)
            include_context: Include context information in response

        Returns:
            Dictionary suitable for JSON serialization
        """
        result: dict[str, Any] = {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message_ar if lang == "ar" else self.message,
                "category": self.category.value,
            },
        }

        if self.details:
            result["error"]["details"] = self.details

        if include_context:
            result["context"] = self.context.to_dict()

        return result

    def to_log_dict(self) -> dict[str, Any]:
        """
        Convert exception to dictionary for structured logging.

        Returns:
            Dictionary with all error information for logging
        """
        result = {
            "error_code": self.code,
            "error_message": self.message,
            "error_message_ar": self.message_ar,
            "category": self.category.value,
            "severity": self.severity.value,
            "status_code": self.status_code,
            "details": self.details,
            "context": self.context.to_dict(),
        }

        if self.cause:
            result["cause"] = {
                "type": type(self.cause).__name__,
                "message": str(self.cause),
            }

        return result

    def with_context(
        self,
        request_id: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        service_name: str | None = None,
        operation: str | None = None,
        **metadata: Any,
    ) -> SahoolBaseException:
        """
        Add context information to the exception.

        Args:
            request_id: Request identifier for tracing
            user_id: User who triggered the error
            tenant_id: Tenant identifier
            service_name: Service where error occurred
            operation: Operation being performed
            **metadata: Additional context metadata

        Returns:
            Self for method chaining
        """
        if request_id:
            self.context.request_id = request_id
        if user_id:
            self.context.user_id = user_id
        if tenant_id:
            self.context.tenant_id = tenant_id
        if service_name:
            self.context.service_name = service_name
        if operation:
            self.context.operation = operation
        if metadata:
            self.context.metadata.update(metadata)
        return self

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"{self.__class__.__name__}("
            f"code={self.code!r}, "
            f"message={self.message!r}, "
            f"status_code={self.status_code})"
        )

    def __str__(self) -> str:
        """Return human-readable string."""
        return f"[{self.code}] {self.message}"


# ─────────────────────────────────────────────────────────────────────────────
# Validation Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class ValidationError(SahoolBaseException):
    """
    Exception for input validation failures.
    استثناء فشل التحقق من صحة المدخلات

    Raised when user input or data fails validation rules.

    Example:
        >>> raise ValidationError(
        ...     message="Invalid email format",
        ...     message_ar="تنسيق البريد الإلكتروني غير صالح",
        ...     field="email",
        ...     value="invalid-email"
        ... )
    """

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        field: str | None = None,
        value: Any = None,
        constraints: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)[:100]  # Truncate for safety
        if constraints:
            details["constraints"] = constraints

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "VAL001"),
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            status_code=422,
            details=details,
            **kwargs,
        )


class NotFoundError(SahoolBaseException):
    """
    Exception for resource not found errors.
    استثناء عدم العثور على المورد

    Raised when a requested resource does not exist.

    Example:
        >>> raise NotFoundError(
        ...     resource_type="Field",
        ...     resource_id="field-123"
        ... )
    """

    def __init__(
        self,
        message: str | None = None,
        message_ar: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not message:
            message = f"{resource_type or 'Resource'} not found"
            if resource_id:
                message += f": {resource_id}"

        if not message_ar:
            message_ar = f"لم يتم العثور على {resource_type or 'المورد'}"
            if resource_id:
                message_ar += f": {resource_id}"

        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "NF001"),
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.WARNING,
            status_code=404,
            details=details,
            **kwargs,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Authentication & Authorization Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class AuthenticationError(SahoolBaseException):
    """
    Exception for authentication failures.
    استثناء فشل المصادقة

    Raised when authentication credentials are invalid or missing.
    """

    def __init__(
        self,
        message: str = "Authentication required",
        message_ar: str = "المصادقة مطلوبة",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "AUTH001"),
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.WARNING,
            status_code=401,
            **kwargs,
        )


class AuthorizationError(SahoolBaseException):
    """
    Exception for authorization failures.
    استثناء فشل التفويض

    Raised when user lacks required permissions.
    """

    def __init__(
        self,
        message: str = "Access denied",
        message_ar: str = "الوصول مرفوض",
        required_permission: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "AUTHZ001"),
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.WARNING,
            status_code=403,
            details=details,
            **kwargs,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Service & Infrastructure Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class ServiceUnavailableError(SahoolBaseException):
    """
    Exception for external service unavailability.
    استثناء عدم توفر الخدمة الخارجية

    Raised when an external service (database, cache, AI provider) is unavailable.
    """

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        message_ar: str = "الخدمة غير متوفرة مؤقتاً",
        service_name: str | None = None,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if service_name:
            details["service"] = service_name
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "SVC001"),
            category=ErrorCategory.SERVICE,
            severity=ErrorSeverity.ERROR,
            status_code=503,
            details=details,
            **kwargs,
        )


class DatabaseError(SahoolBaseException):
    """
    Exception for database operation failures.
    استثناء فشل عمليات قاعدة البيانات
    """

    def __init__(
        self,
        message: str = "Database operation failed",
        message_ar: str = "فشلت عملية قاعدة البيانات",
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "DB001"),
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.ERROR,
            status_code=500,
            details=details,
            **kwargs,
        )


class CacheError(SahoolBaseException):
    """
    Exception for cache operation failures.
    استثناء فشل عمليات التخزين المؤقت
    """

    def __init__(
        self,
        message: str = "Cache operation failed",
        message_ar: str = "فشلت عملية التخزين المؤقت",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "CACHE001"),
            category=ErrorCategory.CACHE,
            severity=ErrorSeverity.WARNING,
            status_code=500,
            **kwargs,
        )


class MessagingError(SahoolBaseException):
    """
    Exception for message queue operation failures.
    استثناء فشل عمليات قائمة الرسائل
    """

    def __init__(
        self,
        message: str = "Messaging operation failed",
        message_ar: str = "فشلت عملية المراسلة",
        subject: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if subject:
            details["subject"] = subject

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "MSG001"),
            category=ErrorCategory.MESSAGING,
            severity=ErrorSeverity.ERROR,
            status_code=500,
            details=details,
            **kwargs,
        )


# ─────────────────────────────────────────────────────────────────────────────
# AI/ML Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class AIServiceError(SahoolBaseException):
    """
    Exception for AI/ML service failures.
    استثناء فشل خدمات الذكاء الاصطناعي

    Raised when AI model inference or processing fails.
    """

    def __init__(
        self,
        message: str = "AI service error",
        message_ar: str = "خطأ في خدمة الذكاء الاصطناعي",
        model_name: str | None = None,
        provider: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if model_name:
            details["model"] = model_name
        if provider:
            details["provider"] = provider

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "AI001"),
            category=ErrorCategory.AI,
            severity=ErrorSeverity.ERROR,
            status_code=500,
            details=details,
            **kwargs,
        )


class ModelNotAvailableError(AIServiceError):
    """
    Exception when AI model is not available.
    استثناء عدم توفر نموذج الذكاء الاصطناعي
    """

    def __init__(
        self,
        model_name: str,
        message: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message=message or f"Model not available: {model_name}",
            message_ar=f"النموذج غير متوفر: {model_name}",
            model_name=model_name,
            code="AI002",
            **kwargs,
        )


class InferenceTimeoutError(AIServiceError):
    """
    Exception when AI inference times out.
    استثناء انتهاء مهلة الاستدلال
    """

    def __init__(
        self,
        timeout_seconds: float,
        model_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        details["timeout_seconds"] = timeout_seconds

        super().__init__(
            message=f"AI inference timed out after {timeout_seconds}s",
            message_ar=f"انتهت مهلة الاستدلال بعد {timeout_seconds} ثانية",
            model_name=model_name,
            code="AI003",
            details=details,
            **kwargs,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Rate Limiting Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class RateLimitExceededError(SahoolBaseException):
    """
    Exception when rate limit is exceeded.
    استثناء تجاوز حد المعدل

    Raised when a user or service exceeds their allowed request rate.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        message_ar: str = "تم تجاوز حد المعدل",
        limit: int | None = None,
        window_seconds: int | None = None,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if limit:
            details["limit"] = limit
        if window_seconds:
            details["window_seconds"] = window_seconds
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "RATE001"),
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.WARNING,
            status_code=429,
            details=details,
            **kwargs,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Conflict Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class ConflictError(SahoolBaseException):
    """
    Exception for state conflict errors.
    استثناء تعارض الحالة

    Raised when an operation conflicts with the current state.
    """

    def __init__(
        self,
        message: str = "Operation conflicts with current state",
        message_ar: str = "العملية تتعارض مع الحالة الحالية",
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=kwargs.pop("code", "CONF001"),
            category=ErrorCategory.CONFLICT,
            severity=ErrorSeverity.WARNING,
            status_code=409,
            details=details,
            **kwargs,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Export all exceptions
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Base classes
    "SahoolBaseException",
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorContext",
    # Validation
    "ValidationError",
    "NotFoundError",
    # Authentication & Authorization
    "AuthenticationError",
    "AuthorizationError",
    # Service & Infrastructure
    "ServiceUnavailableError",
    "DatabaseError",
    "CacheError",
    "MessagingError",
    # AI/ML
    "AIServiceError",
    "ModelNotAvailableError",
    "InferenceTimeoutError",
    # Rate Limiting
    "RateLimitExceededError",
    # Conflict
    "ConflictError",
]
