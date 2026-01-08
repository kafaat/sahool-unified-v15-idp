"""
Error Response Models
نماذج استجابة الأخطاء

@module shared/errors_py
@description Standardized error response formats for FastAPI
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from .error_codes import ErrorCategory


class FieldErrorModel(BaseModel):
    """
    Field Validation Error
    خطأ التحقق من صحة الحقل
    """

    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Error message in English")
    message_ar: str | None = Field(None, description="Error message in Arabic - الرسالة بالعربية")
    constraint: str | None = Field(None, description="Validation constraint that failed")
    value: Any | None = Field(None, description="Invalid value that was provided")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "message_ar": "تنسيق البريد الإلكتروني غير صالح",
                "constraint": "email",
                "value": "invalid-email",
            }
        }


class ErrorDetailsModel(BaseModel):
    """
    Error Details Object
    كائن تفاصيل الخطأ
    """

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message in English")
    messageAr: str = Field(..., description="Error message in Arabic - الرسالة بالعربية")
    category: ErrorCategory | None = Field(None, description="Error category")
    retryable: bool = Field(..., description="Whether the operation can be retried")
    timestamp: str = Field(..., description="Timestamp when error occurred")
    path: str | None = Field(None, description="Request path where error occurred")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    requestId: str | None = Field(None, description="Request ID for tracking")
    stack: str | None = Field(None, description="Stack trace (only in development)")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "ERR_4002",
                "message": "Farm not found",
                "messageAr": "المزرعة غير موجودة",
                "category": "NOT_FOUND",
                "retryable": False,
                "timestamp": "2025-12-31T10:30:00.000Z",
                "path": "/api/v1/farms/123",
                "requestId": "req-123-456-789",
            }
        }


class ErrorResponseModel(BaseModel):
    """
    Standard Error Response
    استجابة الخطأ القياسية
    """

    success: bool = Field(False, description="Success indicator (always false for errors)")
    error: ErrorDetailsModel = Field(..., description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "ERR_4002",
                    "message": "Farm not found",
                    "messageAr": "المزرعة غير موجودة",
                    "category": "NOT_FOUND",
                    "retryable": False,
                    "timestamp": "2025-12-31T10:30:00.000Z",
                    "path": "/api/v1/farms/123",
                    "requestId": "req-123-456-789",
                },
            }
        }


T = TypeVar("T")


class SuccessResponseModel(BaseModel, Generic[T]):
    """
    Success Response (for comparison)
    استجابة النجاح (للمقارنة)
    """

    success: bool = Field(True, description="Success indicator")
    data: T = Field(..., description="Response data")
    message: str | None = Field(None, description="Response message in English")
    messageAr: str | None = Field(None, description="Response message in Arabic - الرسالة بالعربية")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Response timestamp",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "123", "name": "My Farm"},
                "message": "Farm retrieved successfully",
                "messageAr": "تم استرداد المزرعة بنجاح",
                "timestamp": "2025-12-31T10:30:00.000Z",
            }
        }


class PaginationMetaModel(BaseModel):
    """Pagination Metadata - بيانات تقسيم الصفحات"""

    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    totalPages: int = Field(..., description="Total number of pages")
    hasNextPage: bool = Field(..., description="Whether there is a next page")
    hasPreviousPage: bool = Field(..., description="Whether there is a previous page")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "limit": 20,
                "total": 100,
                "totalPages": 5,
                "hasNextPage": True,
                "hasPreviousPage": False,
            }
        }


class PaginatedResponseModel(BaseModel, Generic[T]):
    """
    Paginated Response
    استجابة مقسمة إلى صفحات
    """

    success: bool = Field(True, description="Success indicator")
    data: list[T] = Field(..., description="Response data")
    meta: PaginationMetaModel = Field(..., description="Pagination metadata")
    message: str | None = Field(None, description="Response message in English")
    messageAr: str | None = Field(None, description="Response message in Arabic - الرسالة بالعربية")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Response timestamp",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [{"id": "1", "name": "Farm 1"}, {"id": "2", "name": "Farm 2"}],
                "meta": {
                    "page": 1,
                    "limit": 20,
                    "total": 100,
                    "totalPages": 5,
                    "hasNextPage": True,
                    "hasPreviousPage": False,
                },
                "timestamp": "2025-12-31T10:30:00.000Z",
            }
        }


def create_success_response(
    data: Any,
    message: str | None = None,
    message_ar: str | None = None,
) -> dict[str, Any]:
    """
    Helper function to create success response
    دالة مساعدة لإنشاء استجابة ناجحة
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "messageAr": message_ar,
        "timestamp": datetime.utcnow().isoformat(),
    }


def create_paginated_response(
    data: list[Any],
    page: int,
    limit: int,
    total: int,
    message: str | None = None,
    message_ar: str | None = None,
) -> dict[str, Any]:
    """
    Helper function to create paginated response
    دالة مساعدة لإنشاء استجابة مقسمة إلى صفحات
    """
    total_pages = (total + limit - 1) // limit  # Ceiling division

    return {
        "success": True,
        "data": data,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages,
            "hasNextPage": page * limit < total,
            "hasPreviousPage": page > 1,
        },
        "message": message,
        "messageAr": message_ar,
        "timestamp": datetime.utcnow().isoformat(),
    }
