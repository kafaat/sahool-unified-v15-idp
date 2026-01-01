"""
SAHOOL Global Exception Handler Middleware
معالج الاستثناءات العالمي

Provides consistent error responses and prevents information disclosure.
يوفر استجابات خطأ متسقة ويمنع تسرب المعلومات.
"""

import logging
import traceback
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """
    Base application error class.
    فئة خطأ التطبيق الأساسية.
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        message_ar: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.message_ar = message_ar or message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation error"""

    def __init__(
        self,
        message: str,
        message_ar: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            message_ar=message_ar,
            details=details,
        )


class AuthenticationError(AppError):
    """Authentication error"""

    def __init__(
        self,
        message: str = "Authentication required",
        message_ar: str = "المصادقة مطلوبة",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            message=message,
            message_ar=message_ar,
        )


class AuthorizationError(AppError):
    """Authorization error"""

    def __init__(
        self, message: str = "Permission denied", message_ar: str = "الإذن مرفوض"
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            message=message,
            message_ar=message_ar,
        )


class NotFoundError(AppError):
    """Resource not found error"""

    def __init__(self, resource: str, message_ar: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=f"{resource} not found",
            message_ar=message_ar or f"{resource} غير موجود",
        )


class ConflictError(AppError):
    """Conflict error (e.g., optimistic locking failure)"""

    def __init__(
        self,
        message: str,
        message_ar: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            message_ar=message_ar,
            details=details,
        )


class RateLimitError(AppError):
    """Rate limit exceeded error"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please try again later.",
            message_ar="طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
            details={"retry_after": retry_after},
        )


class InternalError(AppError):
    """Internal server error"""

    def __init__(self, error_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An internal error occurred. Please try again later.",
            message_ar="حدث خطأ داخلي. يرجى المحاولة لاحقاً.",
            details={"error_id": error_id} if error_id else {},
        )


def sanitize_error_message(message: str) -> str:
    """
    Remove sensitive information from error messages.
    إزالة المعلومات الحساسة من رسائل الخطأ.
    """
    import re

    # Patterns to remove
    sensitive_patterns = [
        r"password[=:]\s*\S+",
        r"secret[=:]\s*\S+",
        r"token[=:]\s*\S+",
        r"api_key[=:]\s*\S+",
        r"authorization[=:]\s*\S+",
        r"/home/\S+",
        r"/app/\S+",
        r"postgresql://\S+@",
        r"redis://\S+@",
        r"mongodb://\S+@",
    ]

    sanitized = message
    for pattern in sensitive_patterns:
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

    return sanitized


def create_error_response(
    error_code: str,
    message: str,
    message_ar: str,
    status_code: int,
    error_id: Optional[str] = None,
    details: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Create a consistent error response format.
    إنشاء تنسيق استجابة خطأ متسق.
    """
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
        # Filter out sensitive keys from details
        safe_details = {
            k: v
            for k, v in details.items()
            if k.lower()
            not in ("password", "secret", "token", "api_key", "authorization")
        }
        if safe_details:
            response["error"]["details"] = safe_details

    return response


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup global exception handlers for a FastAPI application.
    إعداد معالجات الاستثناءات العالمية لتطبيق FastAPI.

    Usage:
        from apps.services.shared.middleware.exception_handler import setup_exception_handlers
        setup_exception_handlers(app)
    """

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Handle custom application errors"""
        error_id = str(uuid.uuid4())[:8]

        logger.warning(
            f"AppError [{error_id}]: {exc.error_code} - {exc.message}",
            extra={
                "error_id": error_id,
                "error_code": exc.error_code,
                "path": str(request.url.path),
                "method": request.method,
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

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions"""
        error_id = str(uuid.uuid4())[:8]

        # Map common HTTP status codes to error codes
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

        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                error_code=error_code,
                message=message,
                message_ar=message,  # Could be translated
                status_code=exc.status_code,
                error_id=error_id,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors"""
        error_id = str(uuid.uuid4())[:8]

        # Extract validation errors
        errors = []
        for error in exc.errors():
            loc = " -> ".join(str(l) for l in error.get("loc", []))
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
                            "field": " -> ".join(str(l) for l in e.get("loc", [])),
                            "message": e.get("msg"),
                        }
                        for e in exc.errors()
                    ]
                },
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handle all unhandled exceptions.
        This is the last line of defense - never expose internal details.
        """
        error_id = str(uuid.uuid4())[:8]

        # Log the full exception for debugging
        logger.error(
            f"UnhandledException [{error_id}]: {type(exc).__name__}",
            extra={
                "error_id": error_id,
                "exception_type": type(exc).__name__,
                "path": str(request.url.path),
                "method": request.method,
            },
            exc_info=True,  # Include stack trace in logs only
        )

        # Return a generic error response - never expose internal details
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


# Export commonly used errors
__all__ = [
    "AppError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "InternalError",
    "setup_exception_handlers",
    "sanitize_error_message",
]
