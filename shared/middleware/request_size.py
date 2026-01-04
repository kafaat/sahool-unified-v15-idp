"""
SAHOOL Request Size Limiting Middleware
Protects against oversized payloads and DoS attacks

Security Features:
- Configurable max body size per endpoint
- Content-Type validation
- Large payload audit logging
"""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# Default limits (in bytes)
DEFAULT_MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_MAX_JSON_SIZE = 1 * 1024 * 1024  # 1MB
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class RequestSizeLimiter:
    """Request size validation middleware"""

    def __init__(
        self,
        max_body_size: int = DEFAULT_MAX_BODY_SIZE,
        max_json_size: int = DEFAULT_MAX_JSON_SIZE,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        allowed_content_types: set[str] | None = None,
    ):
        self.max_body_size = max_body_size
        self.max_json_size = max_json_size
        self.max_file_size = max_file_size
        self.allowed_content_types = allowed_content_types or {
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
            "application/octet-stream",
        }

    def _get_max_size_for_content_type(self, content_type: str) -> int:
        """Get max allowed size based on content type"""
        if not content_type:
            return self.max_body_size

        ct_lower = content_type.lower()

        if "application/json" in ct_lower:
            return self.max_json_size
        elif "multipart/form-data" in ct_lower:
            return self.max_file_size
        else:
            return self.max_body_size

    def _is_content_type_allowed(self, content_type: str) -> bool:
        """Check if content type is allowed"""
        if not content_type:
            return True  # Allow requests without Content-Type (GET, etc.)

        # Extract base content type (without parameters)
        base_ct = content_type.split(";")[0].strip().lower()

        # Check against allowed types
        return any(base_ct.startswith(allowed) for allowed in self.allowed_content_types)

    def check_request(
        self, request: Request
    ) -> tuple[bool, str | None, int | None]:
        """
        Check if request meets size/type requirements.
        Returns (allowed, error_message, status_code)
        """
        content_type = request.headers.get("content-type", "")
        content_length = request.headers.get("content-length")

        # Only check for methods that have body
        if request.method not in ["POST", "PUT", "PATCH"]:
            return True, None, None

        # Check content type
        if content_type and not self._is_content_type_allowed(content_type):
            return False, f"Unsupported Content-Type: {content_type}", 415

        # Check content length
        if content_length:
            try:
                size = int(content_length)
                max_size = self._get_max_size_for_content_type(content_type)

                if size > max_size:
                    return False, f"Payload too large. Max: {max_size} bytes", 413

            except ValueError:
                return False, "Invalid Content-Length header", 400

        return True, None, None


# Global instance
_size_limiter = RequestSizeLimiter()


async def request_size_middleware(request: Request, call_next: Callable) -> Response:
    """FastAPI middleware for request size validation"""

    # Skip for health checks and safe methods
    if request.url.path in ["/healthz", "/readyz", "/metrics"]:
        return await call_next(request)

    if request.method in ["GET", "HEAD", "OPTIONS"]:
        return await call_next(request)

    allowed, error_message, status_code = _size_limiter.check_request(request)

    if not allowed:
        # Log the rejection
        client_ip = request.client.host if request.client else "unknown"
        content_length = request.headers.get("content-length", "unknown")

        logger.warning(
            "Request rejected due to size/type",
            extra={
                "event": "security.request_rejected",
                "client_ip": client_ip,
                "path": str(request.url.path),
                "method": request.method,
                "content_length": content_length,
                "content_type": request.headers.get("content-type", ""),
                "reason": error_message,
            },
        )

        return JSONResponse(
            status_code=status_code or 400,
            content={
                "error": error_message,
                "error_ar": (
                    "حجم الطلب غير مسموح به"
                    if status_code == 413
                    else "نوع المحتوى غير مدعوم"
                ),
            },
        )

    return await call_next(request)


def configure_size_limits(
    max_body_size: int = DEFAULT_MAX_BODY_SIZE,
    max_json_size: int = DEFAULT_MAX_JSON_SIZE,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> None:
    """Configure global size limits"""
    global _size_limiter
    _size_limiter = RequestSizeLimiter(
        max_body_size=max_body_size,
        max_json_size=max_json_size,
        max_file_size=max_file_size,
    )
