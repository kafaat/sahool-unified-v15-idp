"""
SAHOOL Unified Error Handling Module
وحدة معالجة الأخطاء الموحدة لمنصة سهول

Provides consistent error handling across all Python services:
- Standardized error codes and response formats
- Exception handlers for FastAPI applications
- Request ID middleware for tracing
- Success response wrapper
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorCode(StrEnum):
    """Standardized error codes for SAHOOL platform."""

    # General errors (1xxx)
    INTERNAL_ERROR = "E1001"
    VALIDATION_ERROR = "E1002"
    NOT_FOUND = "E1003"
    CONFLICT = "E1004"
    METHOD_NOT_ALLOWED = "E1005"

    # Authentication errors (2xxx)
    UNAUTHORIZED = "E2001"
    FORBIDDEN = "E2002"
    TOKEN_EXPIRED = "E2003"
    TOKEN_INVALID = "E2004"

    # Business logic errors (3xxx)
    BUSINESS_RULE_VIOLATION = "E3001"
    QUOTA_EXCEEDED = "E3002"
    RESOURCE_EXHAUSTED = "E3003"

    # External service errors (4xxx)
    EXTERNAL_SERVICE_ERROR = "E4001"
    DATABASE_ERROR = "E4002"
    CACHE_ERROR = "E4003"
    MESSAGING_ERROR = "E4004"

    # AI/ML errors (5xxx)
    AI_MODEL_ERROR = "E5001"
    INFERENCE_TIMEOUT = "E5002"
    MODEL_NOT_AVAILABLE = "E5003"


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = False
    error: dict[str, Any]
    request_id: str | None = None


class SahoolException(Exception):
    """Base exception for all SAHOOL errors."""

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.message_ar = message_ar or message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationException(SahoolException):
    """Validation error exception."""

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            message_ar=message_ar,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details,
        )


class NotFoundException(SahoolException):
    """Resource not found exception."""

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        combined_details = details or {}
        if resource_type:
            combined_details["resource_type"] = resource_type
        if resource_id:
            combined_details["resource_id"] = resource_id

        super().__init__(
            message=message,
            message_ar=message_ar,
            code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=combined_details,
        )


class UnauthorizedException(SahoolException):
    """Unauthorized access exception."""

    def __init__(
        self,
        message: str = "Authentication required",
        message_ar: str = "المصادقة مطلوبة",
    ):
        super().__init__(
            message=message,
            message_ar=message_ar,
            code=ErrorCode.UNAUTHORIZED,
            status_code=401,
        )


class ForbiddenException(SahoolException):
    """Forbidden access exception."""

    def __init__(
        self,
        message: str = "Access denied",
        message_ar: str = "الوصول مرفوض",
    ):
        super().__init__(
            message=message,
            message_ar=message_ar,
            code=ErrorCode.FORBIDDEN,
            status_code=403,
        )


class ExternalServiceException(SahoolException):
    """External service error exception."""

    def __init__(
        self,
        message: str = "External service error",
        message_ar: str = "خطأ في الخدمة الخارجية",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            message_ar=message_ar,
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=502,
            details=details,
        )

    @classmethod
    def weather_service(
        cls,
        error: Exception | None = None,
        details: dict[str, Any] | None = None,
    ) -> ExternalServiceException:
        msg = f"Weather service error: {error}" if error else "Weather service unavailable"
        return cls(
            message=msg,
            message_ar="خطأ في خدمة الطقس",
            details=details,
        )


class InternalServerException(SahoolException):
    """Internal server error exception."""

    def __init__(
        self,
        message: str = "Internal server error",
        message_ar: str = "خطأ داخلي في الخادم",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            message_ar=message_ar,
            code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
            details=details,
        )


def create_error_response(
    exc: SahoolException,
    request_id: str | None = None,
) -> JSONResponse:
    """Create a standardized error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "message_ar": exc.message_ar,
                "details": exc.details,
            },
            "request_id": request_id,
        },
    )


def create_success_response(
    data: Any = None,
    message: str | None = None,
    message_ar: str | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized success response."""
    response = {
        "success": True,
        "data": data,
    }

    if message:
        response["message"] = message
    if message_ar:
        response["message_ar"] = message_ar
    if meta:
        response["meta"] = meta

    return response


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for a FastAPI application."""

    @app.exception_handler(SahoolException)
    async def sahool_exception_handler(
        request: Request,
        exc: SahoolException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return create_error_response(exc, request_id)

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Request,
        exc: ValidationException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return create_error_response(exc, request_id)

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(
        request: Request,
        exc: NotFoundException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return create_error_response(exc, request_id)

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(
        request: Request,
        exc: UnauthorizedException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return create_error_response(exc, request_id)

    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(
        request: Request,
        exc: ForbiddenException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return create_error_response(exc, request_id)

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch-all handler for unexpected exceptions."""
        request_id = getattr(request.state, "request_id", None)
        # Log the actual exception type internally for debugging,
        # but never expose it to clients (information disclosure risk).
        logger.error(
            "Unhandled exception: %s: %s",
            type(exc).__name__,
            exc,
            exc_info=True,
            extra={"request_id": request_id},
        )
        sahool_exc = SahoolException(
            message="An unexpected error occurred",
            message_ar="حدث خطأ غير متوقع",
            code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
        )
        return create_error_response(sahool_exc, request_id)


def add_request_id_middleware(app: FastAPI) -> None:
    """Add request ID middleware for request tracing."""

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        # Get request ID from header or generate new one
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        # Store in request state for access in handlers
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
