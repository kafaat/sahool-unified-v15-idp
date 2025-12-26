"""
JWT Authentication Middleware for FastAPI
Middleware to extract and validate JWT tokens from requests
"""

import logging
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import config
from .jwt_handler import verify_token
from .models import AuthErrors, AuthException, User

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware for FastAPI.

    This middleware extracts and validates JWT tokens from the Authorization header
    and adds the authenticated user to the request state.

    Example:
        ```python
        from fastapi import FastAPI
        from shared.auth.middleware import JWTAuthMiddleware

        app = FastAPI()
        app.add_middleware(JWTAuthMiddleware, exclude_paths=["/health", "/docs"])

        @app.get("/protected")
        async def protected_route(request: Request):
            user = request.state.user
            return {"user_id": user.id, "roles": user.roles}
        ```
    """

    def __init__(
        self,
        app,
        exclude_paths: Optional[list[str]] = None,
        require_auth: bool = False,
    ):
        """
        Initialize JWT authentication middleware.

        Args:
            app: FastAPI application instance
            exclude_paths: List of paths to exclude from authentication
            require_auth: If True, all requests require authentication (except excluded paths)
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.require_auth = require_auth

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request and validate JWT token.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response from the route handler
        """
        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)

        # Extract token from Authorization header
        token = self._extract_token(request)

        if token:
            try:
                # Verify token and create user object
                payload = verify_token(token)

                user = User(
                    id=payload.user_id,
                    email="",
                    roles=payload.roles,
                    tenant_id=payload.tenant_id,
                    permissions=payload.permissions,
                )

                # Add user to request state
                request.state.user = user

                logger.debug(f"Authenticated user: {user.id}")

            except AuthException as e:
                logger.warning(f"Authentication failed: {e.error.code}")

                if self.require_auth:
                    return JSONResponse(
                        status_code=e.status_code,
                        content={
                            "error": e.error.code,
                            "message": e.error.en,
                        }
                    )

        elif self.require_auth:
            return JSONResponse(
                status_code=401,
                content={
                    "error": AuthErrors.MISSING_TOKEN.code,
                    "message": AuthErrors.MISSING_TOKEN.en,
                }
            )

        # Continue to next middleware or route handler
        return await call_next(request)

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Args:
            request: FastAPI request object

        Returns:
            JWT token string or None if not found
        """
        authorization = request.headers.get(config.TOKEN_HEADER)

        if not authorization:
            return None

        try:
            scheme, token = authorization.split()

            if scheme.lower() != config.TOKEN_PREFIX.lower():
                return None

            return token

        except ValueError:
            return None


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate tenant context from requests.

    This middleware extracts the tenant ID from the JWT token or headers
    and adds it to the request state.

    Example:
        ```python
        from fastapi import FastAPI
        from shared.auth.middleware import TenantContextMiddleware

        app = FastAPI()
        app.add_middleware(TenantContextMiddleware)

        @app.get("/data")
        async def get_data(request: Request):
            tenant_id = request.state.tenant_id
            return {"tenant_id": tenant_id}
        ```
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request and extract tenant context.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response from the route handler
        """
        tenant_id = None

        # Try to get tenant from user (if authenticated)
        if hasattr(request.state, "user") and request.state.user:
            tenant_id = request.state.user.tenant_id

        # Fallback to X-Tenant-ID header
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")

        # Add tenant to request state
        request.state.tenant_id = tenant_id

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware based on user ID or IP address.

    This middleware implements a simple rate limiting mechanism to prevent abuse.

    Example:
        ```python
        from fastapi import FastAPI
        from shared.auth.middleware import RateLimitMiddleware

        app = FastAPI()
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=60,
            exclude_paths=["/health"]
        )
        ```
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        exclude_paths: Optional[list[str]] = None,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application instance
            requests_per_minute: Maximum requests per minute per user/IP
            exclude_paths: List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc"]
        self.request_counts = {}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request and apply rate limiting.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response from the route handler or rate limit error
        """
        if not config.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get identifier (user ID or IP)
        identifier = self._get_identifier(request)

        # Check rate limit (this is a simplified implementation)
        # In production, use Redis or similar distributed cache
        if self._is_rate_limited(identifier):
            return JSONResponse(
                status_code=429,
                content={
                    "error": AuthErrors.RATE_LIMIT_EXCEEDED.code,
                    "message": AuthErrors.RATE_LIMIT_EXCEEDED.en,
                }
            )

        return await call_next(request)

    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"

        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _is_rate_limited(self, identifier: str) -> bool:
        """
        Check if identifier has exceeded rate limit.

        This is a simplified implementation. In production, use Redis with
        sliding window or token bucket algorithm.
        """
        # TODO: Implement proper rate limiting with Redis
        # For now, always allow (middleware is present but not enforcing)
        return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.

    Example:
        ```python
        from fastapi import FastAPI
        from shared.auth.middleware import SecurityHeadersMiddleware

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)
        ```
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Add security headers to response.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
