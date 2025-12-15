"""
Shared Error Handling and Logging Utilities
معالجة الأخطاء والتسجيل المشترك

This module provides standardized error handling, logging configuration,
and response formatting for all SAHOOL kernel services.
"""

import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Optional
from functools import wraps
from enum import Enum

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# ═══════════════════════════════════════════════════════════════════════════════
# Logging Configuration
# ═══════════════════════════════════════════════════════════════════════════════

def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configure structured logging for a service.
    إعداد التسجيل المنظم للخدمة

    Args:
        service_name: Name of the service (e.g., 'satellite-service')
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Structured format for production
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# ═══════════════════════════════════════════════════════════════════════════════
# Error Response Models
# ═══════════════════════════════════════════════════════════════════════════════

class ErrorCode(str, Enum):
    """Standard error codes for API responses"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    CALCULATION_ERROR = "CALCULATION_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


class ErrorResponse(BaseModel):
    """
    Standard error response format
    تنسيق الاستجابة للأخطاء
    """
    success: bool = False
    error_code: str
    message: str
    message_ar: Optional[str] = None
    details: Optional[dict] = None
    timestamp: str
    request_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "NOT_FOUND",
                "message": "Resource not found",
                "message_ar": "المورد غير موجود",
                "details": {"resource_id": "123"},
                "timestamp": "2024-12-15T10:30:00Z",
                "request_id": "req_abc123"
            }
        }


# Arabic error messages mapping
ERROR_MESSAGES_AR = {
    ErrorCode.VALIDATION_ERROR: "خطأ في التحقق من البيانات",
    ErrorCode.NOT_FOUND: "المورد غير موجود",
    ErrorCode.UNAUTHORIZED: "غير مصرح - يرجى تسجيل الدخول",
    ErrorCode.FORBIDDEN: "ممنوع - لا يوجد صلاحية",
    ErrorCode.CONFLICT: "تعارض في البيانات",
    ErrorCode.RATE_LIMITED: "تم تجاوز حد الطلبات",
    ErrorCode.SERVICE_UNAVAILABLE: "الخدمة غير متاحة حالياً",
    ErrorCode.INTERNAL_ERROR: "خطأ داخلي في الخادم",
    ErrorCode.BAD_REQUEST: "طلب غير صالح",
    ErrorCode.CALCULATION_ERROR: "خطأ في الحساب",
    ErrorCode.EXTERNAL_SERVICE_ERROR: "خطأ في الخدمة الخارجية",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Custom Exceptions
# ═══════════════════════════════════════════════════════════════════════════════

class SAHOOLException(Exception):
    """Base exception for SAHOOL services"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(SAHOOLException):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details
        )


class ResourceNotFoundError(SAHOOLException):
    """Raised when a resource is not found"""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class CalculationError(SAHOOLException):
    """Raised when a calculation fails"""

    def __init__(self, message: str, calculation_type: str):
        super().__init__(
            message=message,
            error_code=ErrorCode.CALCULATION_ERROR,
            status_code=500,
            details={"calculation_type": calculation_type}
        )


class ExternalServiceError(SAHOOLException):
    """Raised when an external service call fails"""

    def __init__(self, service_name: str, original_error: str):
        super().__init__(
            message=f"External service '{service_name}' error: {original_error}",
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=502,
            details={"service": service_name, "original_error": original_error}
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Exception Handlers
# ═══════════════════════════════════════════════════════════════════════════════

def create_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int = 500,
    details: Optional[dict] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create a standardized error response.
    إنشاء استجابة خطأ موحدة
    """
    response = ErrorResponse(
        error_code=error_code.value,
        message=message,
        message_ar=ERROR_MESSAGES_AR.get(error_code, "حدث خطأ"),
        details=details,
        timestamp=datetime.utcnow().isoformat() + "Z",
        request_id=request_id
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )


async def sahool_exception_handler(request: Request, exc: SAHOOLException) -> JSONResponse:
    """Handler for SAHOOL custom exceptions"""
    request_id = getattr(request.state, 'request_id', None)
    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        request_id=request_id
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for FastAPI HTTP exceptions"""
    error_code_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMITED,
        500: ErrorCode.INTERNAL_ERROR,
        502: ErrorCode.EXTERNAL_SERVICE_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }

    error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    request_id = getattr(request.state, 'request_id', None)

    return create_error_response(
        error_code=error_code,
        message=str(exc.detail),
        status_code=exc.status_code,
        request_id=request_id
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unexpected exceptions"""
    # Log the full traceback
    logger = logging.getLogger("sahool")
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")

    request_id = getattr(request.state, 'request_id', None)

    return create_error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred. Please try again later.",
        status_code=500,
        request_id=request_id
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Decorator for Safe Calculations
# ═══════════════════════════════════════════════════════════════════════════════

def safe_calculation(calculation_name: str, default_value: Any = None):
    """
    Decorator for safely executing calculations with error handling.
    مزخرف للحسابات الآمنة مع معالجة الأخطاء

    Usage:
        @safe_calculation("ndvi_calculation", default_value=0.0)
        def calculate_ndvi(nir: float, red: float) -> float:
            return (nir - red) / (nir + red)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("sahool.calculations")
            try:
                result = func(*args, **kwargs)
                return result
            except ZeroDivisionError:
                logger.warning(f"{calculation_name}: Division by zero, returning default")
                return default_value
            except ValueError as e:
                logger.warning(f"{calculation_name}: Value error - {e}, returning default")
                return default_value
            except Exception as e:
                logger.error(f"{calculation_name}: Unexpected error - {e}")
                if default_value is not None:
                    return default_value
                raise CalculationError(
                    message=f"Calculation failed: {str(e)}",
                    calculation_type=calculation_name
                )
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# Request Logging Middleware
# ═══════════════════════════════════════════════════════════════════════════════

import uuid
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and adding request IDs.
    وسيط لتسجيل الطلبات وإضافة معرفات الطلبات
    """

    def __init__(self, app, logger: logging.Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Log request
        self.logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        start_time = datetime.utcnow()
        response = await call_next(request)
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Log response
        self.logger.info(
            f"[{request_id}] Response: {response.status_code} - {duration:.2f}ms"
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


# ═══════════════════════════════════════════════════════════════════════════════
# Setup Function for Services
# ═══════════════════════════════════════════════════════════════════════════════

def setup_error_handling(app, service_name: str, log_level: str = "INFO"):
    """
    Setup error handling and logging for a FastAPI app.
    إعداد معالجة الأخطاء والتسجيل لتطبيق FastAPI

    Usage:
        from shared.error_handling import setup_error_handling

        app = FastAPI()
        logger = setup_error_handling(app, "satellite-service")
    """
    # Setup logger
    logger = setup_logging(service_name, log_level)

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware, logger=logger)

    # Register exception handlers
    app.add_exception_handler(SAHOOLException, sahool_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info(f"🚀 {service_name} error handling configured")

    return logger
