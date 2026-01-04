"""
Exception Handlers for FastAPI
معالجات الاستثناءات لـ FastAPI

@module shared/errors_py
@description Global exception handlers with request ID correlation and proper logging
"""

import logging
import os
import traceback
import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .error_codes import ERROR_REGISTRY, ErrorCategory, ErrorCode
from .exceptions import AppException

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """
    Get request ID from headers or generate one
    الحصول على معرف الطلب من الرؤوس أو إنشاء واحد
    """
    return (
        request.headers.get("x-request-id")
        or request.headers.get("x-correlation-id")
        or f"req-{int(datetime.utcnow().timestamp() * 1000)}-{uuid.uuid4().hex[:8]}"
    )


def should_include_stack() -> bool:
    """
    Should include stack trace in response
    هل يجب تضمين تتبع المكدس في الاستجابة
    """
    env = os.getenv("ENVIRONMENT", os.getenv("NODE_ENV", "production")).lower()
    return (
        env in ("development", "dev", "local")
        or os.getenv("INCLUDE_STACK_TRACE", "false").lower() == "true"
    )


def sanitize_error_message(message: str) -> str:
    """
    Remove sensitive information from error messages
    إزالة المعلومات الحساسة من رسائل الخطأ
    """
    import re

    # Patterns to remove sensitive information
    sensitive_patterns = [
        (r"password[=:]\s*\S+", "[REDACTED]"),
        (r"secret[=:]\s*\S+", "[REDACTED]"),
        (r"token[=:]\s*\S+", "[REDACTED]"),
        (r"api_key[=:]\s*\S+", "[REDACTED]"),
        (r"authorization[=:]\s*\S+", "[REDACTED]"),
        (r"/home/\S+", "[PATH]"),
        (r"/app/\S+", "[PATH]"),
        (r"postgresql://\S+@", "postgresql://[REDACTED]@"),
        (r"redis://\S+@", "redis://[REDACTED]@"),
        (r"mongodb://\S+@", "mongodb://[REDACTED]@"),
    ]

    sanitized = message
    for pattern, replacement in sensitive_patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def create_error_response(
    error_code: ErrorCode,
    message: str,
    message_ar: str,
    request: Request,
    category: ErrorCategory | None = None,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
    stack_trace: str | None = None,
) -> dict[str, Any]:
    """
    Create a consistent error response format
    إنشاء تنسيق استجابة خطأ متسق
    """
    request_id = get_request_id(request)

    error_details = {
        "code": error_code.value,
        "message": sanitize_error_message(message),
        "messageAr": message_ar,
        "retryable": retryable,
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url.path),
        "requestId": request_id,
    }

    if category:
        error_details["category"] = category.value

    if details:
        # Filter out sensitive keys from details
        safe_details = {
            k: v
            for k, v in details.items()
            if k.lower()
            not in ("password", "secret", "token", "api_key", "authorization")
        }
        if safe_details:
            error_details["details"] = safe_details

    if stack_trace and should_include_stack():
        error_details["stack"] = stack_trace

    return {
        "success": False,
        "error": error_details,
    }


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup global exception handlers for a FastAPI application
    إعداد معالجات الاستثناءات العالمية لتطبيق FastAPI

    Usage:
        from apps.services.shared.errors_py import setup_exception_handlers
        setup_exception_handlers(app)
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handle custom application errors"""
        request_id = get_request_id(request)
        metadata = ERROR_REGISTRY[exc.error_code]

        # Log the error with appropriate level
        if exc.http_status >= 500:
            logger.error(
                f"AppException [{request_id}]: {exc.error_code.value} - {exc.message_en}",
                extra={
                    "request_id": request_id,
                    "error_code": exc.error_code.value,
                    "path": str(request.url.path),
                    "method": request.method,
                    "details": exc.details,
                },
                exc_info=should_include_stack(),
            )
        else:
            logger.warning(
                f"AppException [{request_id}]: {exc.error_code.value} - {exc.message_en}",
                extra={
                    "request_id": request_id,
                    "error_code": exc.error_code.value,
                    "path": str(request.url.path),
                    "method": request.method,
                },
            )

        return JSONResponse(
            status_code=exc.http_status,
            content=create_error_response(
                error_code=exc.error_code,
                message=exc.message_en,
                message_ar=exc.message_ar,
                request=request,
                category=metadata.category,
                retryable=exc.retryable,
                details=exc.details,
                stack_trace=traceback.format_exc() if should_include_stack() else None,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions"""
        request_id = get_request_id(request)

        # Map HTTP status to error code
        status_to_code = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.AUTHENTICATION_FAILED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.RESOURCE_NOT_FOUND,
            409: ErrorCode.RESOURCE_ALREADY_EXISTS,
            422: ErrorCode.VALIDATION_ERROR,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            500: ErrorCode.INTERNAL_SERVER_ERROR,
            502: ErrorCode.EXTERNAL_SERVICE_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }

        error_code = status_to_code.get(
            exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR
        )
        metadata = ERROR_REGISTRY[error_code]

        message = sanitize_error_message(str(exc.detail))

        # Log the error
        if exc.status_code >= 500:
            logger.error(
                f"HTTPException [{request_id}]: {exc.status_code} - {message}",
                extra={
                    "request_id": request_id,
                    "status_code": exc.status_code,
                    "path": str(request.url.path),
                    "method": request.method,
                },
            )
        else:
            logger.warning(
                f"HTTPException [{request_id}]: {exc.status_code} - {message}",
                extra={
                    "request_id": request_id,
                    "status_code": exc.status_code,
                    "path": str(request.url.path),
                },
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                error_code=error_code,
                message=message,
                message_ar=metadata.message.ar,
                request=request,
                category=metadata.category,
                retryable=metadata.retryable,
                stack_trace=traceback.format_exc() if should_include_stack() else None,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors"""
        request_id = get_request_id(request)

        # Extract validation errors
        field_errors = []
        for error in exc.errors():
            loc = " -> ".join(str(loc) for loc in error.get("loc", []))
            msg = error.get("msg", "Validation error")
            field_errors.append(
                {
                    "field": loc,
                    "message": msg,
                    "type": error.get("type"),
                    "value": error.get("input"),
                }
            )

        error_message = "; ".join(f"{e['field']}: {e['message']}" for e in field_errors)

        logger.warning(
            f"ValidationError [{request_id}]: {error_message}",
            extra={
                "request_id": request_id,
                "path": str(request.url.path),
                "method": request.method,
                "errors": field_errors,
            },
        )

        metadata = ERROR_REGISTRY[ErrorCode.VALIDATION_ERROR]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=create_error_response(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=metadata.message.en,
                message_ar=metadata.message.ar,
                request=request,
                category=metadata.category,
                retryable=False,
                details={"fields": field_errors},
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handle all unhandled exceptions
        This is the last line of defense - never expose internal details
        """
        request_id = get_request_id(request)

        # Log the full exception for debugging (server-side only)
        logger.error(
            f"UnhandledException [{request_id}]: {type(exc).__name__}",
            extra={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "path": str(request.url.path),
                "method": request.method,
            },
            exc_info=True,  # Include stack trace in logs only
        )

        metadata = ERROR_REGISTRY[ErrorCode.INTERNAL_SERVER_ERROR]

        # Return a generic error response - never expose internal details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                message=metadata.message.en,
                message_ar=metadata.message.ar,
                request=request,
                category=metadata.category,
                retryable=True,
                details=(
                    {
                        "error": str(exc),
                        "type": type(exc).__name__,
                    }
                    if should_include_stack()
                    else None
                ),
                stack_trace=traceback.format_exc() if should_include_stack() else None,
            ),
        )


def add_request_id_middleware(app: FastAPI) -> None:
    """
    Add middleware to inject request ID into all requests
    إضافة وسيط لحقن معرف الطلب في جميع الطلبات
    """

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        """Inject request ID into request state"""
        request_id = get_request_id(request)
        request.state.request_id = request_id

        # Call the next middleware/route handler
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
