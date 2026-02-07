"""
SAHOOL Field Management Service - Error Handling
=================================================
Provides structured error handling with bilingual messages.

Features:
- Custom exception classes for domain errors
- Consistent error response format
- Bilingual error messages (Arabic/English)
- Error categorization and logging
- Safe error message sanitization
"""

from __future__ import annotations

import logging
import re
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Exception Classes
# ─────────────────────────────────────────────────────────────────────────────


class FieldServiceError(Exception):
    """Base exception for field management service."""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        message_ar: str,
        details: dict[str, Any] | None = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.message_ar = message_ar
        self.details = details or {}
        super().__init__(message)


class FieldNotFoundError(FieldServiceError):
    """Field not found exception."""

    def __init__(self, field_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="FIELD_NOT_FOUND",
            message=f"Field with ID {field_id} not found",
            message_ar=f"الحقل برقم {field_id} غير موجود",
            details={"field_id": field_id},
        )


class CropNotFoundError(FieldServiceError):
    """Crop not found exception."""

    def __init__(self, crop_code: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CROP_NOT_FOUND",
            message=f"Crop with code {crop_code} not found",
            message_ar=f"المحصول برمز {crop_code} غير موجود",
            details={"crop_code": crop_code},
        )


class CropSeasonNotFoundError(FieldServiceError):
    """Crop season not found exception."""

    def __init__(self, crop_season_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CROP_SEASON_NOT_FOUND",
            message=f"Crop season with ID {crop_season_id} not found",
            message_ar=f"موسم المحصول برقم {crop_season_id} غير موجود",
            details={"crop_season_id": crop_season_id},
        )


class InvalidAreaError(FieldServiceError):
    """Invalid area exception."""

    def __init__(self, area_ha: float, min_area: float = 0.01, max_area: float = 10000):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_AREA",
            message=f"Area must be between {min_area} and {max_area} hectares",
            message_ar=f"المساحة يجب أن تكون بين {min_area} و {max_area} هكتار",
            details={
                "area_ha": area_ha,
                "min_area": min_area,
                "max_area": max_area,
            },
        )


class InvalidCostDataError(FieldServiceError):
    """Invalid cost data exception."""

    def __init__(self, message: str, message_ar: str | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_COST_DATA",
            message=message,
            message_ar=message_ar or "بيانات التكلفة غير صالحة",
        )


class InvalidRevenueDataError(FieldServiceError):
    """Invalid revenue data exception."""

    def __init__(self, message: str, message_ar: str | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_REVENUE_DATA",
            message=message,
            message_ar=message_ar or "بيانات الإيرادات غير صالحة",
        )


class RegionNotFoundError(FieldServiceError):
    """Region not found exception."""

    def __init__(self, region: str, available_regions: list[str] | None = None):
        details = {"region": region}
        if available_regions:
            details["available_regions"] = available_regions

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="REGION_NOT_FOUND",
            message=f"Region '{region}' not found or not supported",
            message_ar=f"المنطقة '{region}' غير موجودة أو غير مدعومة",
            details=details,
        )


class AnalysisError(FieldServiceError):
    """Analysis error exception."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="ANALYSIS_ERROR",
            message=f"Failed to perform {operation}: {reason}",
            message_ar=f"فشل في تنفيذ {operation}: {reason}",
            details={"operation": operation, "reason": reason},
        )


class DatabaseError(FieldServiceError):
    """Database error exception."""

    def __init__(self, operation: str, error_id: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="DATABASE_ERROR",
            message="A database error occurred. Please try again later.",
            message_ar="حدث خطأ في قاعدة البيانات. يرجى المحاولة لاحقاً.",
            details={"error_id": error_id, "operation": operation},
        )


# ─────────────────────────────────────────────────────────────────────────────
# Error Response Builder
# ─────────────────────────────────────────────────────────────────────────────


def create_error_response(
    error_code: str,
    message: str,
    message_ar: str,
    status_code: int,
    error_id: str | None = None,
    details: dict | None = None,
) -> dict[str, Any]:
    """Create a consistent error response format."""
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "message_ar": message_ar,
        },
    }

    if error_id:
        response["error"]["error_id"] = error_id

    if details:
        # Filter out sensitive keys
        safe_details = {
            k: v for k, v in details.items()
            if k.lower() not in ("password", "secret", "token", "api_key", "authorization")
        }
        if safe_details:
            response["error"]["details"] = safe_details

    return response


def sanitize_error_message(message: str) -> str:
    """Remove sensitive information from error messages."""
    patterns = [
        r"password[=:]\s*\S+",
        r"secret[=:]\s*\S+",
        r"token[=:]\s*\S+",
        r"api_key[=:]\s*\S+",
        r"authorization[=:]\s*\S+",
        r"/home/\S+",
        r"/app/\S+",
        r"postgresql://\S+@",
        r"redis://\S+@",
    ]

    sanitized = message
    for pattern in patterns:
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

    return sanitized


# ─────────────────────────────────────────────────────────────────────────────
# Exception Handlers
# ─────────────────────────────────────────────────────────────────────────────


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the FastAPI app."""

    @app.exception_handler(FieldServiceError)
    async def field_service_error_handler(
        request: Request,
        exc: FieldServiceError,
    ) -> JSONResponse:
        """Handle custom field service errors."""
        error_id = str(uuid.uuid4())[:8]

        logger.warning(
            f"FieldServiceError [{error_id}]: {exc.error_code} - {exc.message}",
            extra={
                "error_id": error_id,
                "error_code": exc.error_code,
                "path": str(request.url.path),
                "method": request.method,
                "details": exc.details,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                error_code=exc.error_code,
                message=exc.message,
                message_ar=exc.message_ar,
                status_code=exc.status_code,
                error_id=error_id,
                details=exc.details,
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        error_id = str(uuid.uuid4())[:8]

        # Map status codes to error codes
        error_code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
        }

        error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
        message = sanitize_error_message(str(exc.detail))

        logger.warning(
            f"HTTPException [{error_id}]: {exc.status_code} - {message}",
            extra={
                "error_id": error_id,
                "status_code": exc.status_code,
                "path": str(request.url.path),
            },
        )

        # Arabic messages for common errors
        message_ar_map = {
            400: "طلب غير صالح",
            401: "المصادقة مطلوبة",
            403: "الإذن مرفوض",
            404: "غير موجود",
            422: "بيانات غير صالحة",
            429: "طلبات كثيرة جداً",
            500: "خطأ داخلي في الخادم",
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                error_code=error_code,
                message=message,
                message_ar=message_ar_map.get(exc.status_code, message),
                status_code=exc.status_code,
                error_id=error_id,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle request validation errors."""
        error_id = str(uuid.uuid4())[:8]

        # Extract validation errors
        errors = []
        for error in exc.errors():
            loc = " -> ".join(str(loc) for loc in error.get("loc", []))
            msg = error.get("msg", "Validation error")
            errors.append(f"{loc}: {msg}")

        error_message = "; ".join(errors) if errors else "Validation failed"

        logger.warning(
            f"ValidationError [{error_id}]: {error_message}",
            extra={
                "error_id": error_id,
                "path": str(request.url.path),
                "errors": exc.errors(),
            },
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=create_error_response(
                error_code="VALIDATION_ERROR",
                message=error_message,
                message_ar="خطأ في التحقق من البيانات",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_id=error_id,
                details={
                    "validation_errors": [
                        {
                            "field": " -> ".join(str(loc) for loc in e.get("loc", [])),
                            "message": e.get("msg"),
                            "type": e.get("type"),
                        }
                        for e in exc.errors()
                    ]
                },
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle all unhandled exceptions."""
        error_id = str(uuid.uuid4())[:8]

        # Log full exception for debugging
        logger.error(
            f"UnhandledException [{error_id}]: {type(exc).__name__}",
            extra={
                "error_id": error_id,
                "exception_type": type(exc).__name__,
                "path": str(request.url.path),
                "method": request.method,
            },
            exc_info=True,
        )

        # Return generic error response - never expose internal details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred. Please contact support if this persists.",
                message_ar="حدث خطأ غير متوقع. يرجى التواصل مع الدعم إذا استمرت المشكلة.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_id=error_id,
            ),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────


def raise_if_field_not_found(field: Any | None, field_id: str) -> None:
    """Raise FieldNotFoundError if field is None."""
    if field is None:
        raise FieldNotFoundError(field_id)


def raise_if_crop_not_found(crop: Any | None, crop_code: str) -> None:
    """Raise CropNotFoundError if crop is None."""
    if crop is None:
        raise CropNotFoundError(crop_code)


def validate_area_ha(area_ha: float, min_area: float = 0.01, max_area: float = 10000) -> None:
    """Validate area in hectares."""
    if not (min_area <= area_ha <= max_area):
        raise InvalidAreaError(area_ha, min_area, max_area)


def wrap_database_error(operation: str):
    """Decorator to wrap database errors."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            error_id = str(uuid.uuid4())[:8]
            try:
                return await func(*args, **kwargs)
            except FieldServiceError:
                raise
            except Exception as e:
                logger.error(
                    f"Database error in {operation} [{error_id}]: {e}",
                    exc_info=True,
                )
                raise DatabaseError(operation, error_id) from e
        return wrapper
    return decorator
