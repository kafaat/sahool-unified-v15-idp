"""
Error Handling Module for YOLO26 Vision Service.

Provides comprehensive error handling with:
- Bilingual error messages (Arabic/English)
- Structured error responses
- Error categorization
- Retry logic
- Circuit breaker pattern
"""

from __future__ import annotations

import asyncio
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from functools import wraps
from typing import Any, TypeVar

import structlog
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class ErrorCategory(StrEnum):
    """Error categories for classification."""

    VALIDATION = "validation"  # Input validation errors
    AUTHENTICATION = "authentication"  # Auth failures
    AUTHORIZATION = "authorization"  # Permission denied
    NOT_FOUND = "not_found"  # Resource not found
    MODEL = "model"  # Model loading/inference errors
    PROCESSING = "processing"  # Image processing errors
    RESOURCE = "resource"  # Resource exhaustion (GPU, memory)
    EXTERNAL = "external"  # External service failures
    INTERNAL = "internal"  # Unexpected internal errors
    RATE_LIMIT = "rate_limit"  # Rate limiting
    TIMEOUT = "timeout"  # Operation timeout


class ErrorCode(StrEnum):
    """Specific error codes."""

    # Validation errors (1xxx)
    INVALID_IMAGE_FORMAT = "E1001"
    IMAGE_TOO_LARGE = "E1002"
    INVALID_CONFIDENCE = "E1003"
    INVALID_MODEL_VARIANT = "E1004"
    MISSING_REQUIRED_FIELD = "E1005"
    INVALID_BOUNDING_BOX = "E1006"

    # Model errors (2xxx)
    MODEL_NOT_FOUND = "E2001"
    MODEL_LOAD_FAILED = "E2002"
    INFERENCE_FAILED = "E2003"
    MODEL_VERSION_NOT_FOUND = "E2004"
    TENSORRT_ERROR = "E2005"

    # Processing errors (3xxx)
    IMAGE_DECODE_FAILED = "E3001"
    PREPROCESSING_FAILED = "E3002"
    POSTPROCESSING_FAILED = "E3003"
    BATCH_PROCESSING_FAILED = "E3004"

    # Resource errors (4xxx)
    GPU_OUT_OF_MEMORY = "E4001"
    CPU_OUT_OF_MEMORY = "E4002"
    DISK_SPACE_LOW = "E4003"
    MAX_CONCURRENT_REQUESTS = "E4004"

    # External errors (5xxx)
    DATABASE_ERROR = "E5001"
    CACHE_ERROR = "E5002"
    NATS_ERROR = "E5003"

    # Rate limit errors (6xxx)
    RATE_LIMIT_EXCEEDED = "E6001"
    QUOTA_EXCEEDED = "E6002"

    # Timeout errors (7xxx)
    INFERENCE_TIMEOUT = "E7001"
    REQUEST_TIMEOUT = "E7002"

    # Auth errors (8xxx)
    INVALID_TOKEN = "E8001"
    TOKEN_EXPIRED = "E8002"
    PERMISSION_DENIED = "E8003"

    # General errors (9xxx)
    UNKNOWN_ERROR = "E9999"


# Bilingual error messages
ERROR_MESSAGES: dict[ErrorCode, tuple[str, str]] = {
    # Validation
    ErrorCode.INVALID_IMAGE_FORMAT: (
        "Invalid image format. Supported: JPEG, PNG, WebP, BMP, TIFF",
        "تنسيق الصورة غير صالح. المدعوم: JPEG، PNG، WebP، BMP، TIFF",
    ),
    ErrorCode.IMAGE_TOO_LARGE: (
        "Image file too large. Maximum size: {max_size}MB",
        "حجم الصورة كبير جداً. الحد الأقصى: {max_size} ميجابايت",
    ),
    ErrorCode.INVALID_CONFIDENCE: (
        "Confidence threshold must be between 0 and 1",
        "عتبة الثقة يجب أن تكون بين 0 و 1",
    ),
    ErrorCode.INVALID_MODEL_VARIANT: (
        "Invalid model variant. Valid: n, s, m, l, x",
        "نوع النموذج غير صالح. الصالح: n، s، m، l، x",
    ),
    ErrorCode.MISSING_REQUIRED_FIELD: (
        "Missing required field: {field}",
        "حقل مطلوب مفقود: {field}",
    ),
    ErrorCode.INVALID_BOUNDING_BOX: (
        "Invalid bounding box coordinates",
        "إحداثيات المربع المحيط غير صالحة",
    ),
    # Model
    ErrorCode.MODEL_NOT_FOUND: (
        "Model not found: {model}",
        "النموذج غير موجود: {model}",
    ),
    ErrorCode.MODEL_LOAD_FAILED: (
        "Failed to load model: {model}. {details}",
        "فشل تحميل النموذج: {model}. {details}",
    ),
    ErrorCode.INFERENCE_FAILED: (
        "Inference failed: {details}",
        "فشل الاستدلال: {details}",
    ),
    ErrorCode.MODEL_VERSION_NOT_FOUND: (
        "Model version not found: {version}",
        "إصدار النموذج غير موجود: {version}",
    ),
    ErrorCode.TENSORRT_ERROR: (
        "TensorRT optimization error: {details}",
        "خطأ في تحسين TensorRT: {details}",
    ),
    # Processing
    ErrorCode.IMAGE_DECODE_FAILED: (
        "Failed to decode image. The image may be corrupted",
        "فشل فك ترميز الصورة. قد تكون الصورة تالفة",
    ),
    ErrorCode.PREPROCESSING_FAILED: (
        "Image preprocessing failed: {details}",
        "فشل معالجة الصورة المسبقة: {details}",
    ),
    ErrorCode.POSTPROCESSING_FAILED: (
        "Result postprocessing failed: {details}",
        "فشل معالجة النتائج اللاحقة: {details}",
    ),
    ErrorCode.BATCH_PROCESSING_FAILED: (
        "Batch processing failed: {count} of {total} images failed",
        "فشلت معالجة الدفعة: {count} من {total} صورة فشلت",
    ),
    # Resource
    ErrorCode.GPU_OUT_OF_MEMORY: (
        "GPU out of memory. Try reducing image size or batch size",
        "نفدت ذاكرة وحدة معالجة الرسومات. حاول تقليل حجم الصورة أو حجم الدفعة",
    ),
    ErrorCode.CPU_OUT_OF_MEMORY: (
        "System out of memory",
        "نفدت ذاكرة النظام",
    ),
    ErrorCode.DISK_SPACE_LOW: (
        "Low disk space for caching",
        "مساحة القرص منخفضة للتخزين المؤقت",
    ),
    ErrorCode.MAX_CONCURRENT_REQUESTS: (
        "Maximum concurrent requests exceeded. Please retry later",
        "تم تجاوز الحد الأقصى للطلبات المتزامنة. يرجى المحاولة لاحقاً",
    ),
    # External
    ErrorCode.DATABASE_ERROR: (
        "Database error: {details}",
        "خطأ في قاعدة البيانات: {details}",
    ),
    ErrorCode.CACHE_ERROR: (
        "Cache error: {details}",
        "خطأ في ذاكرة التخزين المؤقت: {details}",
    ),
    ErrorCode.NATS_ERROR: (
        "Message queue error: {details}",
        "خطأ في قائمة الرسائل: {details}",
    ),
    # Rate limit
    ErrorCode.RATE_LIMIT_EXCEEDED: (
        "Rate limit exceeded. Retry after {retry_after} seconds",
        "تم تجاوز حد المعدل. أعد المحاولة بعد {retry_after} ثانية",
    ),
    ErrorCode.QUOTA_EXCEEDED: (
        "API quota exceeded for this billing period",
        "تم تجاوز حصة API لفترة الفوترة هذه",
    ),
    # Timeout
    ErrorCode.INFERENCE_TIMEOUT: (
        "Inference timed out after {timeout}s",
        "انتهت مهلة الاستدلال بعد {timeout} ثانية",
    ),
    ErrorCode.REQUEST_TIMEOUT: (
        "Request timed out",
        "انتهت مهلة الطلب",
    ),
    # Auth
    ErrorCode.INVALID_TOKEN: (
        "Invalid authentication token",
        "رمز المصادقة غير صالح",
    ),
    ErrorCode.TOKEN_EXPIRED: (
        "Authentication token has expired",
        "انتهت صلاحية رمز المصادقة",
    ),
    ErrorCode.PERMISSION_DENIED: (
        "Permission denied for this operation",
        "تم رفض الإذن لهذه العملية",
    ),
    # General
    ErrorCode.UNKNOWN_ERROR: (
        "An unexpected error occurred",
        "حدث خطأ غير متوقع",
    ),
}


@dataclass
class VisionError(Exception):
    """Custom exception for vision service errors."""

    code: ErrorCode
    category: ErrorCategory
    message_params: dict[str, Any] = field(default_factory=dict)
    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    details: str | None = None
    cause: Exception | None = None
    retry_after: int | None = None

    @property
    def message_en(self) -> str:
        """Get English error message."""
        template = ERROR_MESSAGES.get(self.code, ("Unknown error", "خطأ غير معروف"))[0]
        try:
            return template.format(**self.message_params)
        except KeyError:
            return template

    @property
    def message_ar(self) -> str:
        """Get Arabic error message."""
        template = ERROR_MESSAGES.get(self.code, ("Unknown error", "خطأ غير معروف"))[1]
        try:
            return template.format(**self.message_params)
        except KeyError:
            return template

    def to_dict(self) -> dict[str, Any]:
        """Convert to response dictionary."""
        response = {
            "error": {
                "code": self.code.value,
                "category": self.category.value,
                "message": self.message_en,
                "message_ar": self.message_ar,
            }
        }

        if self.details:
            response["error"]["details"] = self.details

        if self.retry_after:
            response["error"]["retry_after"] = self.retry_after

        return response

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message_en}"


# Convenience error constructors
class ValidationError(VisionError):
    """Validation error."""

    def __init__(
        self,
        code: ErrorCode,
        message_params: dict[str, Any] | None = None,
        details: str | None = None,
    ):
        super().__init__(
            code=code,
            category=ErrorCategory.VALIDATION,
            message_params=message_params or {},
            http_status=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ModelError(VisionError):
    """Model-related error."""

    def __init__(
        self,
        code: ErrorCode,
        message_params: dict[str, Any] | None = None,
        details: str | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(
            code=code,
            category=ErrorCategory.MODEL,
            message_params=message_params or {},
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
            cause=cause,
        )


class ResourceError(VisionError):
    """Resource exhaustion error."""

    def __init__(
        self,
        code: ErrorCode,
        message_params: dict[str, Any] | None = None,
        retry_after: int = 30,
    ):
        super().__init__(
            code=code,
            category=ErrorCategory.RESOURCE,
            message_params=message_params or {},
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            retry_after=retry_after,
        )


class RateLimitError(VisionError):
    """Rate limit exceeded error."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            category=ErrorCategory.RATE_LIMIT,
            message_params={"retry_after": retry_after},
            http_status=status.HTTP_429_TOO_MANY_REQUESTS,
            retry_after=retry_after,
        )


class VisionTimeoutError(VisionError):
    """Timeout error for vision operations."""

    def __init__(self, timeout: float):
        super().__init__(
            code=ErrorCode.INFERENCE_TIMEOUT,
            category=ErrorCategory.TIMEOUT,
            message_params={"timeout": timeout},
            http_status=status.HTTP_504_GATEWAY_TIMEOUT,
        )


# Exception handlers for FastAPI
async def vision_error_handler(request: Request, exc: VisionError) -> JSONResponse:
    """Handle VisionError exceptions."""
    logger.warning(
        "vision_error",
        code=exc.code.value,
        category=exc.category.value,
        path=request.url.path,
        details=exc.details,
    )

    headers = {}
    if exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)

    return JSONResponse(
        status_code=exc.http_status,
        content=exc.to_dict(),
        headers=headers,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    error_id = f"ERR-{int(time.time())}"

    logger.error(
        "unhandled_exception",
        error_id=error_id,
        path=request.url.path,
        error=str(exc),
        traceback=traceback.format_exc(),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.UNKNOWN_ERROR.value,
                "category": ErrorCategory.INTERNAL.value,
                "message": "An unexpected error occurred",
                "message_ar": "حدث خطأ غير متوقع",
                "error_id": error_id,
            }
        },
    )


def setup_error_handlers(app) -> None:
    """Setup error handlers for FastAPI app."""
    app.add_exception_handler(VisionError, vision_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


# Retry decorator
def with_retry(
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    exponential_backoff: bool = True,
    retryable_exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator for retry logic.

    Args:
        max_retries: Maximum number of retries
        delay_seconds: Initial delay between retries
        exponential_backoff: Use exponential backoff
        retryable_exceptions: Exception types to retry

    Usage:
        @with_retry(max_retries=3, delay_seconds=1.0)
        async def unstable_operation():
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay_seconds

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            "operation_retry",
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            delay=current_delay,
                            error=str(e),
                        )
                        await asyncio.sleep(current_delay)
                        if exponential_backoff:
                            current_delay *= 2

            raise last_exception

        return wrapper

    return decorator


# Circuit breaker pattern
@dataclass
class CircuitBreakerState:
    """Circuit breaker state."""

    failures: int = 0
    last_failure_time: float = 0
    state: str = "closed"  # closed, open, half-open


class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.

    Prevents cascading failures by temporarily disabling operations
    that are likely to fail.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self._states: dict[str, CircuitBreakerState] = {}
        self._half_open_calls: dict[str, int] = {}

    def _get_state(self, key: str) -> CircuitBreakerState:
        """Get or create state for key."""
        if key not in self._states:
            self._states[key] = CircuitBreakerState()
        return self._states[key]

    def is_open(self, key: str) -> bool:
        """Check if circuit is open."""
        state = self._get_state(key)

        if state.state == "closed":
            return False

        if state.state == "open":
            # Check if recovery timeout has passed
            if time.time() - state.last_failure_time > self.recovery_timeout:
                state.state = "half-open"
                self._half_open_calls[key] = 0
                return False
            return True

        # half-open state
        return self._half_open_calls.get(key, 0) >= self.half_open_max_calls

    def record_success(self, key: str) -> None:
        """Record successful operation."""
        state = self._get_state(key)

        if state.state == "half-open":
            # Reset to closed after success in half-open
            state.state = "closed"
            state.failures = 0
            logger.info("circuit_closed", key=key)
        elif state.state == "closed":
            state.failures = 0

    def record_failure(self, key: str) -> None:
        """Record failed operation."""
        state = self._get_state(key)
        state.failures += 1
        state.last_failure_time = time.time()

        if state.state == "half-open":
            # Open circuit on failure in half-open
            state.state = "open"
            logger.warning("circuit_reopened", key=key)
        elif state.failures >= self.failure_threshold:
            state.state = "open"
            logger.warning("circuit_opened", key=key, failures=state.failures)

        if state.state == "half-open":
            self._half_open_calls[key] = self._half_open_calls.get(key, 0) + 1

    def call(
        self,
        key: str,
    ) -> Callable:
        """
        Decorator for circuit breaker protection.

        Usage:
            @circuit_breaker.call("model_inference")
            async def inference():
                ...
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                if self.is_open(key):
                    raise ResourceError(
                        code=ErrorCode.MAX_CONCURRENT_REQUESTS,
                        message_params={},
                        retry_after=int(self.recovery_timeout),
                    )

                try:
                    result = await func(*args, **kwargs)
                    self.record_success(key)
                    return result
                except Exception:
                    self.record_failure(key)
                    raise

            return wrapper

        return decorator

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status for all keys."""
        return {
            key: {
                "state": state.state,
                "failures": state.failures,
                "last_failure": state.last_failure_time,
            }
            for key, state in self._states.items()
        }


# Global circuit breaker instance
circuit_breaker = CircuitBreaker()
