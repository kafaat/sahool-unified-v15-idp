"""
SAHOOL Request Logging Middleware
==================================
Comprehensive request logging middleware for FastAPI services with structured JSON logging.

Features:
- Logs request method, path, status code, duration
- Tracks user_id and tenant_id from request context
- Generates and propagates correlation IDs
- Structured JSON output format
- Supports OpenTelemetry trace propagation
- Filters sensitive data from logs

Usage:
    from shared.middleware.request_logging import RequestLoggingMiddleware

    app.add_middleware(
        RequestLoggingMiddleware,
        service_name="my-service",
        log_request_body=False,  # Set to True for debugging
        log_response_body=False,
    )
"""

import json
import time
import uuid
import logging
from typing import Optional, Callable, Set
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request logging with structured JSON format.

    Logs all requests with:
    - HTTP method, path, query parameters
    - Status code and response time
    - Correlation ID (X-Correlation-ID or generated)
    - User ID and Tenant ID from headers or JWT
    - Request/Response bodies (optional, for debugging)

    Configuration:
        - service_name: Name of the service (required)
        - log_request_body: Log request bodies (default: False)
        - log_response_body: Log response bodies (default: False)
        - exclude_paths: Paths to exclude from logging (default: health checks, docs)
        - max_body_length: Maximum length of body to log (default: 1000 chars)
    """

    # Sensitive headers to redact
    SENSITIVE_HEADERS: Set[str] = {
        "authorization",
        "cookie",
        "x-api-key",
        "x-auth-token",
        "x-secret-key",
        "password",
        "secret",
        "token",
    }

    def __init__(
        self,
        app,
        service_name: str,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: Optional[list[str]] = None,
        max_body_length: int = 1000,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or [
            "/healthz",
            "/readyz",
            "/livez",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.max_body_length = max_body_length

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process each request with comprehensive logging."""

        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Generate or extract correlation ID
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

        # Extract tenant and user IDs
        tenant_id = self._extract_tenant_id(request)
        user_id = self._extract_user_id(request)

        # Store in request state for downstream use
        request.state.correlation_id = correlation_id
        request.state.tenant_id = tenant_id
        request.state.user_id = user_id

        # Record start time
        start_time = time.perf_counter()

        # Prepare request log data
        request_log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "type": "request",
            "correlation_id": correlation_id,
            "http": {
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params) if request.query_params else None,
                "user_agent": request.headers.get("user-agent"),
            },
            "tenant_id": tenant_id,
            "user_id": user_id,
        }

        # Log request body if enabled
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            request_body = await self._read_request_body(request)
            if request_body:
                request_log["http"]["request_body"] = request_body

        # Log incoming request
        self._log_json("info", "Incoming request", request_log)

        # Process request and capture response
        response = None
        error = None
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            error = e
            error_type = type(e).__name__
            error_message = str(e)

            # Log exception
            exception_log = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": self.service_name,
                "type": "error",
                "correlation_id": correlation_id,
                "error": {
                    "type": error_type,
                    "message": error_message,
                },
                "http": {
                    "method": request.method,
                    "path": request.url.path,
                },
                "tenant_id": tenant_id,
                "user_id": user_id,
            }
            self._log_json("error", f"Request failed: {error_message}", exception_log)
            raise

        finally:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Prepare response log
            response_log = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": self.service_name,
                "type": "response",
                "correlation_id": correlation_id,
                "http": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
                "tenant_id": tenant_id,
                "user_id": user_id,
            }

            # Add error info if present
            if error:
                response_log["error"] = {
                    "type": type(error).__name__,
                    "message": str(error),
                }

            # Determine log level based on status code
            if status_code >= 500:
                log_level = "error"
            elif status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"

            # Log response
            message = (
                f"{request.method} {request.url.path} {status_code} {duration_ms:.2f}ms"
            )
            self._log_json(log_level, message, response_log)

    def _extract_tenant_id(self, request: Request) -> Optional[str]:
        """Extract tenant ID from headers or request state."""
        # Try header first
        tenant_id = request.headers.get("X-Tenant-ID")

        # Try request state (set by auth middleware)
        if not tenant_id and hasattr(request.state, "tenant_id"):
            tenant_id = request.state.tenant_id

        # Try tenant context
        if not tenant_id and hasattr(request.state, "tenant_context"):
            tenant_id = request.state.tenant_context.id

        return tenant_id

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from headers or request state."""
        # Try header first
        user_id = request.headers.get("X-User-ID")

        # Try request state (set by auth middleware)
        if not user_id and hasattr(request.state, "user_id"):
            user_id = request.state.user_id

        # Try principal (JWT claims)
        if not user_id and hasattr(request.state, "principal"):
            user_id = request.state.principal.get("sub")

        return user_id

    async def _read_request_body(self, request: Request) -> Optional[str]:
        """Read and return request body (with size limit)."""
        try:
            body_bytes = await request.body()
            if not body_bytes:
                return None

            # Decode body
            body_str = body_bytes.decode("utf-8")

            # Truncate if too long
            if len(body_str) > self.max_body_length:
                body_str = body_str[: self.max_body_length] + "...[truncated]"

            # Try to parse as JSON for better formatting
            try:
                body_json = json.loads(body_str)
                # Redact sensitive fields
                body_json = self._redact_sensitive_data(body_json)
                return body_json
            except json.JSONDecodeError:
                return body_str

        except Exception as e:
            logger.warning(f"Failed to read request body: {e}")
            return None

    def _redact_sensitive_data(self, data: dict) -> dict:
        """Redact sensitive fields from dictionary."""
        if not isinstance(data, dict):
            return data

        redacted = {}
        for key, value in data.items():
            # Check if key is sensitive
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_HEADERS):
                redacted[key] = "***REDACTED***"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive_data(value)
            elif isinstance(value, list):
                redacted[key] = [
                    (
                        self._redact_sensitive_data(item)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in value
                ]
            else:
                redacted[key] = value

        return redacted

    def _log_json(self, level: str, message: str, data: dict) -> None:
        """Log structured JSON message."""
        # Add message to data
        log_data = {**data, "message": message}

        # Convert to JSON string
        json_str = json.dumps(log_data, ensure_ascii=False)

        # Log at appropriate level
        log_method = getattr(logger, level, logger.info)
        log_method(json_str)


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────


def get_correlation_id(request: Request) -> str:
    """
    Get correlation ID from current request.

    Returns:
        Correlation ID string
    """
    return getattr(request.state, "correlation_id", "unknown")


def get_request_context(request: Request) -> dict:
    """
    Get request context for logging.

    Returns:
        Dictionary with correlation_id, tenant_id, user_id
    """
    return {
        "correlation_id": getattr(request.state, "correlation_id", None),
        "tenant_id": getattr(request.state, "tenant_id", None),
        "user_id": getattr(request.state, "user_id", None),
    }
