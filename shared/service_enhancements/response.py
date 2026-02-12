"""
SAHOOL API Response Utilities Module
====================================
Provides consistent API response formatting for SAHOOL services.

Features:
- Standardized success/error response format
- Pagination response helpers
- Bilingual message support (Arabic/English)
- Response metadata (timestamps, versions)

Usage:
    from shared.service_enhancements.response import (
        SuccessResponse,
        ErrorResponse,
        PaginatedResponse,
        create_response,
    )

    @app.get("/fields/{field_id}")
    async def get_field(field_id: str):
        field = await get_field_by_id(field_id)
        return SuccessResponse(
            data=field,
            message="Field retrieved successfully",
            message_ar="تم جلب الحقل بنجاح"
        )
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel):
    """
    Base API response model.
    All API responses should use this format for consistency.
    """

    success: bool
    message: str
    message_ar: str
    timestamp: str
    version: str = "16.0.0"


class SuccessResponse(ApiResponse):
    """
    Success response with data payload.

    Example:
        {
            "success": true,
            "message": "Field retrieved successfully",
            "message_ar": "تم جلب الحقل بنجاح",
            "timestamp": "2026-01-15T10:30:00Z",
            "version": "16.0.0",
            "data": {...}
        }
    """

    success: bool = True
    data: Any = None

    def __init__(
        self,
        data: Any = None,
        message: str = "Operation successful",
        message_ar: str = "تمت العملية بنجاح",
        **kwargs,
    ):
        super().__init__(
            success=True,
            message=message,
            message_ar=message_ar,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            data=data,
            **kwargs,
        )


class ErrorResponse(ApiResponse):
    """
    Error response with error details.

    Example:
        {
            "success": false,
            "message": "Field not found",
            "message_ar": "الحقل غير موجود",
            "timestamp": "2026-01-15T10:30:00Z",
            "version": "16.0.0",
            "error": {
                "code": "NOT_FOUND",
                "details": {"field_id": "FIELD-001"}
            }
        }
    """

    success: bool = False
    error: dict[str, Any] | None = None

    def __init__(
        self,
        error_code: str,
        message: str = "An error occurred",
        message_ar: str = "حدث خطأ",
        details: dict[str, Any] | None = None,
        **kwargs,
    ):
        super().__init__(
            success=False,
            message=message,
            message_ar=message_ar,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            error={
                "code": error_code,
                "details": details or {},
            },
            **kwargs,
        )


@dataclass
class PaginationMeta:
    """Pagination metadata."""

    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }


class PaginatedResponse(ApiResponse):
    """
    Paginated response for list endpoints.

    Example:
        {
            "success": true,
            "message": "Fields retrieved successfully",
            "message_ar": "تم جلب الحقول بنجاح",
            "timestamp": "2026-01-15T10:30:00Z",
            "version": "16.0.0",
            "data": [...],
            "pagination": {
                "page": 1,
                "page_size": 20,
                "total": 150,
                "total_pages": 8,
                "has_next": true,
                "has_previous": false
            }
        }
    """

    success: bool = True
    data: list[Any] = []
    pagination: dict[str, Any] | None = None

    def __init__(
        self,
        items: list[Any],
        page: int,
        page_size: int,
        total: int,
        message: str = "Items retrieved successfully",
        message_ar: str = "تم جلب العناصر بنجاح",
        **kwargs,
    ):
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        pagination = PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

        super().__init__(
            success=True,
            message=message,
            message_ar=message_ar,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            data=items,
            pagination=pagination.to_dict(),
            **kwargs,
        )


def create_response(
    success: bool = True,
    data: Any = None,
    message: str | None = None,
    message_ar: str | None = None,
    error_code: str | None = None,
    error_details: dict[str, Any] | None = None,
    pagination: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a standardized API response dictionary.

    Args:
        success: Whether the operation was successful
        data: Response data payload
        message: English message
        message_ar: Arabic message
        error_code: Error code (for error responses)
        error_details: Additional error details
        pagination: Pagination metadata

    Returns:
        Formatted response dictionary
    """
    response = {
        "success": success,
        "message": message or ("Operation successful" if success else "An error occurred"),
        "message_ar": message_ar or ("تمت العملية بنجاح" if success else "حدث خطأ"),
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "version": "16.0.0",
    }

    if success:
        response["data"] = data
    else:
        response["error"] = {
            "code": error_code or "UNKNOWN_ERROR",
            "details": error_details or {},
        }

    if pagination:
        response["pagination"] = pagination

    return response


# ─────────────────────────────────────────────────────────────────────────────
# Common Response Messages
# ─────────────────────────────────────────────────────────────────────────────


class ResponseMessages:
    """Common response messages in English and Arabic."""

    # Success messages
    CREATED = ("Resource created successfully", "تم إنشاء المورد بنجاح")
    UPDATED = ("Resource updated successfully", "تم تحديث المورد بنجاح")
    DELETED = ("Resource deleted successfully", "تم حذف المورد بنجاح")
    RETRIEVED = ("Resource retrieved successfully", "تم جلب المورد بنجاح")
    LIST_RETRIEVED = ("Items retrieved successfully", "تم جلب العناصر بنجاح")

    # Field-specific
    FIELD_CREATED = ("Field created successfully", "تم إنشاء الحقل بنجاح")
    FIELD_UPDATED = ("Field updated successfully", "تم تحديث الحقل بنجاح")
    FIELD_DELETED = ("Field deleted successfully", "تم حذف الحقل بنجاح")

    # Irrigation-specific
    IRRIGATION_SCHEDULED = (
        "Irrigation scheduled successfully",
        "تمت جدولة الري بنجاح",
    )
    IRRIGATION_EXECUTED = (
        "Irrigation executed successfully",
        "تم تنفيذ الري بنجاح",
    )

    # Advisory-specific
    ADVISORY_GENERATED = (
        "Advisory generated successfully",
        "تم إنشاء الإرشاد بنجاح",
    )

    # Notification-specific
    NOTIFICATION_SENT = ("Notification sent successfully", "تم إرسال الإشعار بنجاح")
    NOTIFICATION_READ = (
        "Notification marked as read",
        "تم تحديد الإشعار كمقروء",
    )

    # Error messages
    NOT_FOUND = ("Resource not found", "المورد غير موجود")
    VALIDATION_ERROR = ("Validation error", "خطأ في التحقق من البيانات")
    UNAUTHORIZED = ("Authentication required", "المصادقة مطلوبة")
    FORBIDDEN = ("Permission denied", "الإذن مرفوض")
    RATE_LIMITED = ("Too many requests", "طلبات كثيرة جداً")
    INTERNAL_ERROR = ("Internal server error", "خطأ داخلي في الخادم")


def get_message(key: str) -> tuple[str, str]:
    """Get message tuple by key from ResponseMessages."""
    return getattr(ResponseMessages, key, ResponseMessages.RETRIEVED)
