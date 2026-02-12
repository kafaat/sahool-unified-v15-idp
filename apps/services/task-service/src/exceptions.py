"""
Custom Exceptions for Task Service - استثناءات مخصصة لخدمة المهام

This module provides domain-specific exceptions with bilingual support
and proper error categorization for the task service.
"""

from enum import Enum, StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Error codes for task service - رموز الأخطاء"""

    # Task errors - أخطاء المهام
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_ALREADY_EXISTS = "TASK_ALREADY_EXISTS"
    TASK_INVALID_STATUS = "TASK_INVALID_STATUS"
    TASK_INVALID_TRANSITION = "TASK_INVALID_TRANSITION"
    TASK_CREATION_FAILED = "TASK_CREATION_FAILED"
    TASK_UPDATE_FAILED = "TASK_UPDATE_FAILED"

    # Validation errors - أخطاء التحقق
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FIELD_ID = "INVALID_FIELD_ID"
    INVALID_DATE_FORMAT = "INVALID_DATE_FORMAT"
    INVALID_TIME_FORMAT = "INVALID_TIME_FORMAT"
    INVALID_PRIORITY = "INVALID_PRIORITY"
    METADATA_TOO_LARGE = "METADATA_TOO_LARGE"

    # External service errors - أخطاء الخدمات الخارجية
    ASTRONOMICAL_SERVICE_ERROR = "ASTRONOMICAL_SERVICE_ERROR"
    ASTRONOMICAL_SERVICE_TIMEOUT = "ASTRONOMICAL_SERVICE_TIMEOUT"
    FIELD_SERVICE_ERROR = "FIELD_SERVICE_ERROR"
    NOTIFICATION_SERVICE_ERROR = "NOTIFICATION_SERVICE_ERROR"
    NDVI_SERVICE_ERROR = "NDVI_SERVICE_ERROR"

    # Database errors - أخطاء قاعدة البيانات
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"

    # Cache errors - أخطاء التخزين المؤقت
    CACHE_ERROR = "CACHE_ERROR"
    CACHE_CONNECTION_ERROR = "CACHE_CONNECTION_ERROR"

    # Authentication/Authorization errors - أخطاء المصادقة
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TENANT = "INVALID_TENANT"


class TaskServiceError(Exception):
    """
    Base exception for task service
    الاستثناء الأساسي لخدمة المهام

    All custom exceptions in the task service should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.message_ar = message_ar or message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "message_ar": self.message_ar,
                "details": self.details,
            }
        }


# ═══════════════════════════════════════════════════════════════════════════
# Task-specific Exceptions - استثناءات خاصة بالمهام
# ═══════════════════════════════════════════════════════════════════════════


class TaskNotFoundError(TaskServiceError):
    """Raised when a task is not found - المهمة غير موجودة"""

    def __init__(self, task_id: str, tenant_id: str | None = None):
        details = {"task_id": task_id}
        if tenant_id:
            details["tenant_id"] = tenant_id

        super().__init__(
            message=f"Task not found: {task_id}",
            message_ar=f"المهمة غير موجودة: {task_id}",
            error_code=ErrorCode.TASK_NOT_FOUND,
            status_code=404,
            details=details,
        )


class TaskAlreadyExistsError(TaskServiceError):
    """Raised when trying to create a task that already exists"""

    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task already exists: {task_id}",
            message_ar=f"المهمة موجودة بالفعل: {task_id}",
            error_code=ErrorCode.TASK_ALREADY_EXISTS,
            status_code=409,
            details={"task_id": task_id},
        )


class TaskInvalidStatusError(TaskServiceError):
    """Raised when task has invalid status for an operation"""

    def __init__(
        self,
        task_id: str,
        current_status: str,
        expected_statuses: list[str],
        operation: str,
    ):
        super().__init__(
            message=f"Task {task_id} has status '{current_status}', expected one of {expected_statuses} for {operation}",
            message_ar=f"المهمة {task_id} حالتها '{current_status}'، المتوقع أحد {expected_statuses} لـ {operation}",
            error_code=ErrorCode.TASK_INVALID_STATUS,
            status_code=400,
            details={
                "task_id": task_id,
                "current_status": current_status,
                "expected_statuses": expected_statuses,
                "operation": operation,
            },
        )


class TaskInvalidTransitionError(TaskServiceError):
    """Raised when attempting an invalid status transition"""

    def __init__(self, task_id: str, from_status: str, to_status: str):
        super().__init__(
            message=f"Invalid status transition for task {task_id}: {from_status} -> {to_status}",
            message_ar=f"انتقال حالة غير صالح للمهمة {task_id}: {from_status} -> {to_status}",
            error_code=ErrorCode.TASK_INVALID_TRANSITION,
            status_code=400,
            details={
                "task_id": task_id,
                "from_status": from_status,
                "to_status": to_status,
            },
        )


class TaskCreationError(TaskServiceError):
    """Raised when task creation fails"""

    def __init__(self, reason: str, reason_ar: str | None = None):
        super().__init__(
            message=f"Failed to create task: {reason}",
            message_ar=f"فشل إنشاء المهمة: {reason_ar or reason}",
            error_code=ErrorCode.TASK_CREATION_FAILED,
            status_code=500,
            details={"reason": reason},
        )


# ═══════════════════════════════════════════════════════════════════════════
# Validation Exceptions - استثناءات التحقق
# ═══════════════════════════════════════════════════════════════════════════


class ValidationError(TaskServiceError):
    """General validation error"""

    def __init__(
        self,
        field: str,
        message: str,
        message_ar: str | None = None,
        value: Any = None,
    ):
        details = {"field": field}
        if value is not None:
            # Don't include sensitive values
            details["value_type"] = type(value).__name__

        super().__init__(
            message=f"Validation error for '{field}': {message}",
            message_ar=f"خطأ تحقق في '{field}': {message_ar or message}",
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details,
        )


class InvalidFieldIdError(ValidationError):
    """Raised when field_id format is invalid"""

    def __init__(self, field_id: str):
        # Sanitize field_id for safe logging
        safe_id = field_id[:50] if field_id else "<empty>"
        super().__init__(
            field="field_id",
            message=f"Invalid field ID format: {safe_id}",
            message_ar=f"تنسيق معرف الحقل غير صالح: {safe_id}",
        )
        self.error_code = ErrorCode.INVALID_FIELD_ID


class InvalidDateFormatError(ValidationError):
    """Raised when date format is invalid"""

    def __init__(self, date_value: str, expected_format: str = "YYYY-MM-DD"):
        super().__init__(
            field="date",
            message=f"Invalid date format. Expected {expected_format}",
            message_ar=f"تنسيق تاريخ غير صالح. المتوقع {expected_format}",
            value=date_value,
        )
        self.error_code = ErrorCode.INVALID_DATE_FORMAT


class InvalidTimeFormatError(ValidationError):
    """Raised when time format is invalid"""

    def __init__(self, time_value: str, expected_format: str = "HH:MM"):
        super().__init__(
            field="scheduled_time",
            message=f"Invalid time format. Expected {expected_format}",
            message_ar=f"تنسيق وقت غير صالح. المتوقع {expected_format}",
            value=time_value,
        )
        self.error_code = ErrorCode.INVALID_TIME_FORMAT


class MetadataTooLargeError(ValidationError):
    """Raised when metadata exceeds size limit"""

    def __init__(self, size: int, max_size: int):
        super().__init__(
            field="metadata",
            message=f"Metadata size ({size} bytes) exceeds limit ({max_size} bytes)",
            message_ar=f"حجم البيانات الوصفية ({size} بايت) يتجاوز الحد ({max_size} بايت)",
        )
        self.error_code = ErrorCode.METADATA_TOO_LARGE
        self.details.update({"size": size, "max_size": max_size})


# ═══════════════════════════════════════════════════════════════════════════
# External Service Exceptions - استثناءات الخدمات الخارجية
# ═══════════════════════════════════════════════════════════════════════════


class ExternalServiceError(TaskServiceError):
    """Base exception for external service errors"""

    def __init__(
        self,
        service_name: str,
        message: str,
        message_ar: str | None = None,
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        status_code: int = 502,
        details: dict[str, Any] | None = None,
    ):
        full_details = {"service": service_name}
        if details:
            full_details.update(details)

        super().__init__(
            message=f"{service_name} error: {message}",
            message_ar=f"خطأ {service_name}: {message_ar or message}",
            error_code=error_code,
            status_code=status_code,
            details=full_details,
        )


class AstronomicalServiceError(ExternalServiceError):
    """Error from astronomical calendar service"""

    def __init__(self, message: str, message_ar: str | None = None):
        super().__init__(
            service_name="Astronomical Calendar",
            message=message,
            message_ar=message_ar or "خدمة التقويم الفلكي غير متاحة",
            error_code=ErrorCode.ASTRONOMICAL_SERVICE_ERROR,
            status_code=502,
        )


class AstronomicalServiceTimeoutError(ExternalServiceError):
    """Timeout from astronomical calendar service"""

    def __init__(self):
        super().__init__(
            service_name="Astronomical Calendar",
            message="Service timeout",
            message_ar="انتهت مهلة خدمة التقويم الفلكي",
            error_code=ErrorCode.ASTRONOMICAL_SERVICE_TIMEOUT,
            status_code=504,
        )


class FieldServiceError(ExternalServiceError):
    """Error from field service"""

    def __init__(self, message: str, field_id: str | None = None):
        details = {}
        if field_id:
            # Sanitize field_id
            details["field_id"] = field_id[:50] if field_id else None

        super().__init__(
            service_name="Field Service",
            message=message,
            message_ar="خطأ في خدمة الحقول",
            error_code=ErrorCode.FIELD_SERVICE_ERROR,
            status_code=502,
            details=details,
        )


class NdviServiceError(ExternalServiceError):
    """Error from NDVI service"""

    def __init__(self, message: str, field_id: str | None = None):
        details = {}
        if field_id:
            details["field_id"] = field_id[:50] if field_id else None

        super().__init__(
            service_name="NDVI Service",
            message=message,
            message_ar="خطأ في خدمة NDVI",
            error_code=ErrorCode.NDVI_SERVICE_ERROR,
            status_code=502,
            details=details,
        )


class NotificationServiceError(ExternalServiceError):
    """Error from notification service"""

    def __init__(self, message: str):
        super().__init__(
            service_name="Notification Service",
            message=message,
            message_ar="خطأ في خدمة الإشعارات",
            error_code=ErrorCode.NOTIFICATION_SERVICE_ERROR,
            status_code=502,
        )


# ═══════════════════════════════════════════════════════════════════════════
# Database Exceptions - استثناءات قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════


class DatabaseError(TaskServiceError):
    """General database error"""

    def __init__(self, message: str, operation: str | None = None):
        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=f"Database error: {message}",
            message_ar=f"خطأ في قاعدة البيانات: {message}",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details=details,
        )


class DatabaseConnectionError(DatabaseError):
    """Database connection error"""

    def __init__(self):
        super().__init__(
            message="Unable to connect to database",
            operation="connect",
        )
        self.error_code = ErrorCode.DATABASE_CONNECTION_ERROR


# ═══════════════════════════════════════════════════════════════════════════
# Cache Exceptions - استثناءات التخزين المؤقت
# ═══════════════════════════════════════════════════════════════════════════


class CacheError(TaskServiceError):
    """General cache error"""

    def __init__(self, message: str, operation: str | None = None):
        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=f"Cache error: {message}",
            message_ar=f"خطأ في التخزين المؤقت: {message}",
            error_code=ErrorCode.CACHE_ERROR,
            status_code=500,
            details=details,
        )


class CacheConnectionError(CacheError):
    """Cache connection error"""

    def __init__(self):
        super().__init__(
            message="Unable to connect to cache",
            operation="connect",
        )
        self.error_code = ErrorCode.CACHE_CONNECTION_ERROR


# ═══════════════════════════════════════════════════════════════════════════
# Authorization Exceptions - استثناءات الصلاحيات
# ═══════════════════════════════════════════════════════════════════════════


class UnauthorizedError(TaskServiceError):
    """Unauthorized access error"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            message_ar="المصادقة مطلوبة",
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401,
        )


class ForbiddenError(TaskServiceError):
    """Forbidden access error"""

    def __init__(self, resource: str = "resource"):
        super().__init__(
            message=f"Access denied to {resource}",
            message_ar=f"تم رفض الوصول إلى {resource}",
            error_code=ErrorCode.FORBIDDEN,
            status_code=403,
            details={"resource": resource},
        )


class InvalidTenantError(TaskServiceError):
    """Invalid tenant error"""

    def __init__(self, tenant_id: str | None = None):
        super().__init__(
            message="Invalid or missing tenant ID",
            message_ar="معرف المستأجر غير صالح أو مفقود",
            error_code=ErrorCode.INVALID_TENANT,
            status_code=400,
        )
