"""
JWT Authentication Middleware for FastAPI
Middleware to extract and validate JWT tokens from requests
"""

import json
import logging
import time
from collections import defaultdict
from collections.abc import Callable

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
        exclude_paths: list[str] | None = None,
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

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
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
                        },
                    )

        elif self.require_auth:
            return JSONResponse(
                status_code=401,
                content={
                    "error": AuthErrors.MISSING_TOKEN.code,
                    "message": AuthErrors.MISSING_TOKEN.en,
                },
            )

        # Continue to next middleware or route handler
        return await call_next(request)

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _extract_token(self, request: Request) -> str | None:
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

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
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

    This middleware implements rate limiting with Redis support and in-memory fallback.
    Uses sliding window algorithm for accurate rate limiting.

    Example:
        ```python
        from fastapi import FastAPI
        from shared.auth.middleware import RateLimitMiddleware

        app = FastAPI()
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=60,
            burst_limit=10,
            exclude_paths=["/health"]
        )
        ```
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        requests_per_hour: int = 2000,
        burst_limit: int = 20,
        exclude_paths: list[str] | None = None,
        redis_url: str | None = None,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application instance
            requests_per_minute: Maximum requests per minute per user/IP
            requests_per_hour: Maximum requests per hour per user/IP
            burst_limit: Maximum burst requests allowed
            exclude_paths: List of paths to exclude from rate limiting
            redis_url: Redis connection URL (optional, will use in-memory if not provided)
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/metrics"]

        # Redis connection (lazy initialized)
        self._redis_url = (
            redis_url or config.REDIS_URL if hasattr(config, "REDIS_URL") else None
        )
        self._redis = None
        self._redis_available = False

        # In-memory fallback storage
        self._request_timestamps: dict[str, list[float]] = defaultdict(list)
        self._burst_tokens: dict[str, dict] = defaultdict(
            lambda: {"tokens": burst_limit, "last_update": time.time()}
        )

    async def _ensure_redis_connection(self):
        """Lazily initialize Redis connection."""
        if self._redis is not None or not self._redis_url:
            return

        try:
            import redis.asyncio as redis

            self._redis = redis.from_url(
                self._redis_url, encoding="utf-8", decode_responses=True
            )
            await self._redis.ping()
            self._redis_available = True
            logger.info("Rate limiter connected to Redis successfully")
        except ImportError:
            logger.warning("redis package not installed, using in-memory rate limiting")
            self._redis_available = False
        except Exception as e:
            logger.warning(
                f"Redis connection failed: {e}, using in-memory rate limiting"
            )
            self._redis_available = False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
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

        # Ensure Redis connection
        await self._ensure_redis_connection()

        # Get identifier (user ID or IP)
        identifier = self._get_identifier(request)

        # Check rate limit
        is_limited, remaining, reset_time = await self._check_rate_limit(identifier)

        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {identifier}",
                extra={
                    "identifier": identifier,
                    "path": request.url.path,
                    "method": request.method,
                },
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": AuthErrors.RATE_LIMIT_EXCEEDED.code,
                    "message": AuthErrors.RATE_LIMIT_EXCEEDED.en,
                    "retry_after": reset_time,
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": str(max(0, remaining)),
                    "X-RateLimit-Reset": str(int(time.time() + reset_time)),
                    "Retry-After": str(reset_time),
                },
            )

        # Add rate limit headers to successful response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + reset_time))

        return response

    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting (not a Flask route)"""
        if hasattr(request.state, "user") and request.state.user:
            # nosemgrep
            return f"user:{request.state.user.id}"

        # Fallback to IP address (check for proxy headers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # nosemgrep
        return f"ip:{client_ip}"

    async def _check_rate_limit(self, identifier: str) -> tuple[bool, int, int]:
        """
        Check if identifier has exceeded rate limit using Redis or in-memory storage.

        Args:
            identifier: Unique identifier for the client

        Returns:
            Tuple of (is_limited, remaining_requests, reset_time_seconds)
        """
        if self._redis_available:
            return await self._check_rate_limit_redis(identifier)
        else:
            return self._check_rate_limit_memory(identifier)

    async def _check_rate_limit_redis(self, identifier: str) -> tuple[bool, int, int]:
        """Check rate limit using Redis with sliding window algorithm."""
        now = time.time()
        minute_key = f"ratelimit:{identifier}:minute"
        hour_key = f"ratelimit:{identifier}:hour"
        burst_key = f"ratelimit:{identifier}:burst"

        try:
            pipe = self._redis.pipeline()

            # === Minute window ===
            # Remove old entries
            pipe.zremrangebyscore(minute_key, 0, now - 60)
            # Count current requests
            pipe.zcard(minute_key)
            # Add current request timestamp
            pipe.zadd(minute_key, {str(now): now})
            # Set expiry
            pipe.expire(minute_key, 120)

            # === Hour window ===
            pipe.zremrangebyscore(hour_key, 0, now - 3600)
            pipe.zcard(hour_key)
            pipe.zadd(hour_key, {str(now): now})
            pipe.expire(hour_key, 7200)

            # === Burst protection (token bucket) ===
            pipe.get(burst_key)

            results = await pipe.execute()

            minute_count = results[1]
            hour_count = results[5]
            burst_data = results[8]

            # Check burst limit using token bucket
            if burst_data:
                burst_info = json.loads(burst_data)
                tokens = burst_info["tokens"]
                last_update = burst_info["last_update"]

                # Refill tokens based on time elapsed
                elapsed = now - last_update
                refill_rate = self.burst_limit / 60.0  # tokens per second
                tokens = min(self.burst_limit, tokens + elapsed * refill_rate)

                if tokens < 1:
                    # Remove the request we just added
                    await self._redis.zrem(minute_key, str(now))
                    await self._redis.zrem(hour_key, str(now))
                    return True, 0, 60

                # Consume one token
                tokens -= 1
                await self._redis.set(
                    burst_key, str({"tokens": tokens, "last_update": now}), ex=120
                )
            else:
                # Initialize burst tokens
                await self._redis.set(
                    burst_key,
                    str({"tokens": self.burst_limit - 1, "last_update": now}),
                    ex=120,
                )

            # Check minute limit
            if minute_count >= self.requests_per_minute:
                await self._redis.zrem(minute_key, str(now))
                await self._redis.zrem(hour_key, str(now))
                return True, 0, 60

            # Check hour limit
            if hour_count >= self.requests_per_hour:
                await self._redis.zrem(minute_key, str(now))
                await self._redis.zrem(hour_key, str(now))
                return True, 0, 3600

            remaining = min(
                self.requests_per_minute - minute_count - 1,
                self.requests_per_hour - hour_count - 1,
            )

            return False, remaining, 60

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fail open - allow request if Redis fails
            return False, self.requests_per_minute, 60

    def _check_rate_limit_memory(self, identifier: str) -> tuple[bool, int, int]:
        """Check rate limit using in-memory storage with sliding window."""
        now = time.time()

        # Get or create timestamps list for this identifier
        timestamps = self._request_timestamps[identifier]

        # Remove timestamps older than 1 hour
        timestamps[:] = [ts for ts in timestamps if now - ts < 3600]

        # Count requests in last minute
        minute_requests = sum(1 for ts in timestamps if now - ts < 60)

        # Count requests in last hour
        hour_requests = len(timestamps)

        # Check burst limit using token bucket
        burst_info = self._burst_tokens[identifier]
        tokens = burst_info["tokens"]
        last_update = burst_info["last_update"]

        # Refill tokens
        elapsed = now - last_update
        refill_rate = self.burst_limit / 60.0  # tokens per second
        tokens = min(self.burst_limit, tokens + elapsed * refill_rate)

        # Check burst
        if tokens < 1:
            return True, 0, 60

        # Check minute limit
        if minute_requests >= self.requests_per_minute:
            return True, 0, 60

        # Check hour limit
        if hour_requests >= self.requests_per_hour:
            return True, 0, 3600

        # Allow request - record it
        timestamps.append(now)
        self._burst_tokens[identifier] = {"tokens": tokens - 1, "last_update": now}

        remaining = min(
            self.requests_per_minute - minute_requests - 1,
            self.requests_per_hour - hour_requests - 1,
        )

        return False, remaining, 60


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

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
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
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response
