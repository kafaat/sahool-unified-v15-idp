"""
Rate Limiter for AI Advisor
محدد معدل الطلبات
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size

        # Track requests per client
        self._minute_requests: dict[str, list] = defaultdict(list)
        self._hour_requests: dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from auth header
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            return f"auth:{hash(auth_header)}"

        # Fall back to IP
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        return f"ip:{request.client.host if request.client else 'unknown'}"

    def _cleanup_old_requests(self, requests: list, window: timedelta) -> list:
        """Remove requests outside the time window"""
        cutoff = datetime.now() - window
        return [r for r in requests if r > cutoff]

    async def check_rate_limit(self, request: Request) -> tuple[bool, str]:
        """
        Check if request is within rate limits
        Returns: (is_allowed, reason)
        """
        client_id = self._get_client_id(request)
        now = datetime.now()

        async with self._lock:
            # Clean up old requests
            self._minute_requests[client_id] = self._cleanup_old_requests(
                self._minute_requests[client_id], timedelta(minutes=1)
            )
            self._hour_requests[client_id] = self._cleanup_old_requests(
                self._hour_requests[client_id], timedelta(hours=1)
            )

            # Check minute limit
            if len(self._minute_requests[client_id]) >= self.requests_per_minute:
                return False, "Rate limit exceeded: too many requests per minute"

            # Check hour limit
            if len(self._hour_requests[client_id]) >= self.requests_per_hour:
                return False, "Rate limit exceeded: too many requests per hour"

            # Record this request
            self._minute_requests[client_id].append(now)
            self._hour_requests[client_id].append(now)

            return True, ""

    def get_remaining(self, client_id: str) -> dict[str, int]:
        """Get remaining requests for client"""
        minute_used = len(self._minute_requests.get(client_id, []))
        hour_used = len(self._hour_requests.get(client_id, []))

        return {
            "minute_remaining": max(0, self.requests_per_minute - minute_used),
            "hour_remaining": max(0, self.requests_per_hour - hour_used),
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""

    def __init__(self, app, rate_limiter: RateLimiter = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/healthz", "/ready"]:
            return await call_next(request)

        is_allowed, reason = await self.rate_limiter.check_rate_limit(request)

        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {request.client.host}: {reason}")
            raise HTTPException(status_code=429, detail=reason, headers={"Retry-After": "60"})

        response = await call_next(request)
        return response


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=30,  # Conservative for AI endpoints
    requests_per_hour=500,
    burst_size=5,
)
