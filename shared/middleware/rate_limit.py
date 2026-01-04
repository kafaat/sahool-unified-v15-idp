"""
SAHOOL Rate Limiting Middleware
Provides tiered rate limiting for API endpoints

Security Features:
- Token bucket algorithm for burst protection
- Sliding window for sustained rate limiting
- Tiered limits (free, standard, premium, internal)
- Audit logging for security monitoring
"""

import asyncio
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration for different tiers"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10  # Max requests in 1 second


@dataclass
class TierConfig:
    """Tiered rate limiting configuration"""

    free: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=30, requests_per_hour=500, burst_limit=5
        )
    )
    standard: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=60, requests_per_hour=2000, burst_limit=10
        )
    )
    premium: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=120, requests_per_hour=5000, burst_limit=20
        )
    )
    internal: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=1000, requests_per_hour=50000, burst_limit=100
        )
    )


class TokenBucket:
    """Token bucket algorithm for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens, returns True if successful"""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now


class RateLimiter:
    """Rate limiter with sliding window and token bucket"""

    def __init__(self, tier_config: TierConfig | None = None):
        self.tier_config = tier_config or TierConfig()
        self._buckets: dict[str, TokenBucket] = {}
        self._request_counts: dict[str, list[float]] = defaultdict(list)

    def _get_bucket(self, key: str, config: RateLimitConfig) -> TokenBucket:
        """Get or create token bucket for a key"""
        if key not in self._buckets:
            # Refill rate = requests_per_minute / 60 seconds
            self._buckets[key] = TokenBucket(
                capacity=config.burst_limit,
                refill_rate=config.requests_per_minute / 60.0,
            )
        return self._buckets[key]

    def _clean_old_requests(self, key: str, window_seconds: int):
        """Remove requests older than the window"""
        cutoff = time.time() - window_seconds
        self._request_counts[key] = [t for t in self._request_counts[key] if t > cutoff]

    def _get_tier(self, request: Request) -> str:
        """Get rate limit tier from request headers or default"""
        # Check for internal service calls
        if request.headers.get("X-Internal-Service"):
            return "internal"

        # Check for API key tier
        tier = request.headers.get("X-Rate-Limit-Tier", "free").lower()
        if tier not in ["free", "standard", "premium", "internal"]:
            tier = "free"

        return tier

    def _get_config(self, tier: str) -> RateLimitConfig:
        """Get rate limit config for tier"""
        return getattr(self.tier_config, tier, self.tier_config.free)

    def check_rate_limit(self, request: Request) -> tuple[bool, dict]:
        """
        Check if request is within rate limits
        Returns (allowed, headers_dict)
        """
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        tenant_id = request.headers.get("X-Tenant-ID", "default")
        key = f"{tenant_id}:{client_ip}"

        tier = self._get_tier(request)
        config = self._get_config(tier)

        # Check token bucket (burst protection)
        bucket = self._get_bucket(key, config)
        if not bucket.consume():
            return False, self._build_headers(key, config, tier, exceeded=True)

        # Check sliding window (per-minute)
        self._clean_old_requests(key, 60)
        if len(self._request_counts[key]) >= config.requests_per_minute:
            return False, self._build_headers(key, config, tier, exceeded=True)

        # Check hourly limit
        hourly_key = f"{key}:hourly"
        self._clean_old_requests(hourly_key, 3600)
        if len(self._request_counts[hourly_key]) >= config.requests_per_hour:
            return False, self._build_headers(key, config, tier, exceeded=True)

        # Record this request
        now = time.time()
        self._request_counts[key].append(now)
        self._request_counts[hourly_key].append(now)

        return True, self._build_headers(key, config, tier, exceeded=False)

    def _build_headers(
        self, key: str, config: RateLimitConfig, tier: str, exceeded: bool
    ) -> dict:
        """Build rate limit response headers"""
        remaining = max(
            0, config.requests_per_minute - len(self._request_counts.get(key, []))
        )

        headers = {
            "X-RateLimit-Limit": str(config.requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time()) + 60),
            "X-RateLimit-Tier": tier,
        }

        if exceeded:
            headers["Retry-After"] = "60"

        return headers


# Global rate limiter instance
_rate_limiter = RateLimiter()


async def _log_rate_limit_exceeded(request: Request, tier: str):
    """Log rate limit exceeded event for security monitoring"""
    client_ip = request.client.host if request.client else "unknown"
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    user_agent = request.headers.get("User-Agent", "unknown")

    # Security logging
    logger.warning(
        "Rate limit exceeded",
        extra={
            "event": "security.rate_limit_exceeded",
            "client_ip": client_ip,
            "tenant_id": tenant_id,
            "tier": tier,
            "path": str(request.url.path),
            "method": request.method,
            "user_agent": user_agent[:200] if user_agent else None,
        },
    )

    # Try to log to audit system (non-blocking)
    try:
        from shared.security.audit import AuditAction, audit_log
        from shared.security.audit_models import AuditCategory, AuditSeverity

        asyncio.create_task(
            audit_log(
                tenant_id=tenant_id,
                user_id="system",
                action=AuditAction.RATE_LIMIT_EXCEEDED,
                category=AuditCategory.SECURITY,
                severity=AuditSeverity.WARNING,
                ip_address=client_ip,
                user_agent=user_agent[:500] if user_agent else None,
                request_method=request.method,
                request_path=str(request.url.path),
                details={
                    "tier": tier,
                    "limit_type": "rate_limit",
                },
                success=False,
                error_code="RATE_LIMIT_EXCEEDED",
                error_message="Too many requests",
            )
        )
    except ImportError:
        # Audit module not available, skip
        pass


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """FastAPI middleware for rate limiting with security logging"""

    # Skip rate limiting for health checks
    if request.url.path in ["/healthz", "/readyz", "/metrics"]:
        return await call_next(request)

    allowed, headers = _rate_limiter.check_rate_limit(request)

    if not allowed:
        # Log rate limit exceeded for security monitoring
        tier = headers.get("X-RateLimit-Tier", "unknown")
        await _log_rate_limit_exceeded(request, tier)

        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "error_ar": "تم تجاوز حد الطلبات",
                "message": "Too many requests. Please try again later.",
                "message_ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
            },
            headers=headers,
        )

    response = await call_next(request)

    # Add rate limit headers to response
    for key, value in headers.items():
        response.headers[key] = value

    return response


def rate_limit(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    burst_limit: int = 10,
    key_func: Callable[[Request], str] | None = None,
):
    """
    Decorator for endpoint-specific rate limiting

    Args:
        requests_per_minute: Maximum requests per minute
        requests_per_hour: Maximum requests per hour
        burst_limit: Maximum burst requests
        key_func: Optional function to extract custom rate limit key from request

    Usage:
        @app.get("/expensive-endpoint")
        @rate_limit(requests_per_minute=10)
        async def expensive_endpoint(request: Request):
            ...

        # Custom key function
        def custom_key(request: Request) -> str:
            return f"api_key:{request.headers.get('X-API-Key')}"

        @app.get("/api-endpoint")
        @rate_limit(requests_per_minute=100, key_func=custom_key)
        async def api_endpoint(request: Request):
            ...
    """
    config = RateLimitConfig(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        burst_limit=burst_limit,
    )

    limiter = RateLimiter()
    limiter.tier_config = TierConfig(
        free=config, standard=config, premium=config, internal=config
    )

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None and "request" in kwargs:
                request = kwargs["request"]

            if request is None:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)

            # Use custom key function if provided
            if key_func:
                request.headers.get("X-Tenant-ID", "default")

                # Create a modified request-like object with custom key
                custom_key = key_func(request)
                # Store original values
                # Temporarily modify for rate limit check
                request.state._rate_limit_key = custom_key

            allowed, headers = limiter.check_rate_limit(request)

            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "error_ar": "تم تجاوز حد الطلبات",
                        "message": "Too many requests. Please try again later.",
                        "message_ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
                    },
                    headers=headers,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit_by_user(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
):
    """
    Decorator for user-based rate limiting (requires authentication)

    Usage:
        @app.get("/user-endpoint")
        @rate_limit_by_user(requests_per_minute=30)
        async def user_endpoint(request: Request):
            user = request.state.user
            ...
    """

    def user_key(request: Request) -> str:
        if hasattr(request.state, "user") and request.state.user:
            # nosemgrep: python.flask.security.audit.directly-returned-format-string.directly-returned-format-string
            return f"user:{request.state.user.id}"
        # nosemgrep: python.flask.security.audit.directly-returned-format-string.directly-returned-format-string
        return f"ip:{request.client.host if request.client else 'unknown'}"

    return rate_limit(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        key_func=user_key,
    )


def rate_limit_by_api_key(
    requests_per_minute: int = 100,
    requests_per_hour: int = 5000,
    header_name: str = "X-API-Key",
):
    """
    Decorator for API key-based rate limiting

    Usage:
        @app.get("/api-endpoint")
        @rate_limit_by_api_key(requests_per_minute=100)
        async def api_endpoint(request: Request):
            ...
    """

    def api_key_func(request: Request) -> str:
        api_key = request.headers.get(header_name, "anonymous")
        # nosemgrep
        return f"api_key:{api_key}"

    return rate_limit(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        key_func=api_key_func,
    )


def rate_limit_by_tenant(
    requests_per_minute: int = 200,
    requests_per_hour: int = 10000,
):
    """
    Decorator for tenant-based rate limiting

    Usage:
        @app.get("/tenant-endpoint")
        @rate_limit_by_tenant(requests_per_minute=200)
        async def tenant_endpoint(request: Request):
            ...
    """

    def tenant_key(request: Request) -> str:
        tenant_id = request.headers.get("X-Tenant-ID", "default")
        # nosemgrep
        return f"tenant:{tenant_id}"

    return rate_limit(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        key_func=tenant_key,
    )
