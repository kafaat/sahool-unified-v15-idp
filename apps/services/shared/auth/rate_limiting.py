"""
SAHOOL Authentication Rate Limiting Configuration
تكوين التحكم في معدل طلبات المصادقة

Provides strict rate limiting specifically for authentication endpoints to prevent
brute-force attacks and credential stuffing.

Usage:
    from apps.services.shared.auth.rate_limiting import auth_rate_limiter, LoginRateLimiter

    @app.post("/auth/login")
    async def login(
        request: Request,
        credentials: LoginRequest,
        limiter: LoginRateLimiter = Depends(get_login_rate_limiter),
    ):
        # Login logic here
        ...
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

from fastapi import Request, HTTPException, status
from ..middleware.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    RateLimitTier,
    get_rate_limit_headers,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication-Specific Rate Limit Configurations
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AuthRateLimitConfigs:
    """Predefined rate limit configurations for authentication endpoints.

    Based on OWASP recommendations for preventing brute-force attacks:
    - Login: 5 attempts per minute, 20 per hour
    - Password reset: 3 attempts per minute, 10 per hour
    - Registration: 10 attempts per minute, 50 per hour
    - Token refresh: 10 attempts per minute, 100 per hour
    """

    # Login endpoint - strictest limits to prevent brute force
    LOGIN = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=20,
        burst_limit=2,
        enabled=True,
    )

    # Password reset - very strict to prevent enumeration and abuse
    PASSWORD_RESET = RateLimitConfig(
        requests_per_minute=3,
        requests_per_hour=10,
        burst_limit=1,
        enabled=True,
    )

    # Registration - moderate to prevent spam accounts
    REGISTRATION = RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=50,
        burst_limit=5,
        enabled=True,
    )

    # Token refresh - moderate limits
    TOKEN_REFRESH = RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=100,
        burst_limit=5,
        enabled=True,
    )

    # Email verification - moderate limits
    EMAIL_VERIFICATION = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=30,
        burst_limit=3,
        enabled=True,
    )

    # 2FA verification - strict limits
    TWO_FACTOR_AUTH = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=20,
        burst_limit=2,
        enabled=True,
    )


# Singleton instance
AUTH_RATE_CONFIGS = AuthRateLimitConfigs()


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication Rate Limiter
# ═══════════════════════════════════════════════════════════════════════════════

class AuthRateLimiter:
    """Specialized rate limiter for authentication endpoints.

    Uses IP address + username/email combination for more accurate tracking.
    """

    def __init__(self, base_limiter: Optional[RateLimiter] = None):
        self._limiter = base_limiter or RateLimiter()

    def _get_auth_key(self, request: Request, identifier: Optional[str] = None) -> str:
        """Generate rate limit key combining IP and user identifier.

        Args:
            request: FastAPI request object
            identifier: Username or email from request

        Returns:
            Unique key for rate limiting
        """
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Combine IP with identifier if provided (rate limit key, not HTML)
        # nosemgrep: python.flask.security.audit.directly-returned-format-string.directly-returned-format-string
        if identifier:
            return f"auth:{client_ip}:{identifier}"
        # nosemgrep: python.flask.security.audit.directly-returned-format-string.directly-returned-format-string
        return f"auth:{client_ip}"

    async def check_login_limit(
        self,
        request: Request,
        username: str,
    ) -> tuple[bool, int, int, int]:
        """Check rate limit for login attempts.

        Args:
            request: FastAPI request
            username: Username or email attempting to log in

        Returns:
            Tuple of (allowed, remaining, limit, reset_seconds)

        Raises:
            HTTPException: If rate limit exceeded
        """
        key = self._get_auth_key(request, username)
        allowed, remaining, limit, reset = await self._limiter._in_memory.check_rate_limit(
            key, AUTH_RATE_CONFIGS.LOGIN
        )

        if not allowed:
            logger.warning(
                f"Login rate limit exceeded for {username} from {request.client.host}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many login attempts. Please try again later.",
                    "retry_after": reset,
                },
                headers=get_rate_limit_headers(remaining, limit, reset),
            )

        return allowed, remaining, limit, reset

    async def check_password_reset_limit(
        self,
        request: Request,
        email: str,
    ) -> tuple[bool, int, int, int]:
        """Check rate limit for password reset requests.

        Args:
            request: FastAPI request
            email: Email requesting password reset

        Returns:
            Tuple of (allowed, remaining, limit, reset_seconds)

        Raises:
            HTTPException: If rate limit exceeded
        """
        key = self._get_auth_key(request, email)
        allowed, remaining, limit, reset = await self._limiter._in_memory.check_rate_limit(
            key, AUTH_RATE_CONFIGS.PASSWORD_RESET
        )

        if not allowed:
            logger.warning(
                f"Password reset rate limit exceeded for {email} from {request.client.host}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many password reset attempts. Please try again later.",
                    "retry_after": reset,
                },
                headers=get_rate_limit_headers(remaining, limit, reset),
            )

        return allowed, remaining, limit, reset

    async def check_registration_limit(
        self,
        request: Request,
        email: Optional[str] = None,
    ) -> tuple[bool, int, int, int]:
        """Check rate limit for registration requests.

        Args:
            request: FastAPI request
            email: Email for registration (optional)

        Returns:
            Tuple of (allowed, remaining, limit, reset_seconds)

        Raises:
            HTTPException: If rate limit exceeded
        """
        key = self._get_auth_key(request, email)
        allowed, remaining, limit, reset = await self._limiter._in_memory.check_rate_limit(
            key, AUTH_RATE_CONFIGS.REGISTRATION
        )

        if not allowed:
            logger.warning(
                f"Registration rate limit exceeded from {request.client.host}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many registration attempts. Please try again later.",
                    "retry_after": reset,
                },
                headers=get_rate_limit_headers(remaining, limit, reset),
            )

        return allowed, remaining, limit, reset

    async def check_token_refresh_limit(
        self,
        request: Request,
        user_id: str,
    ) -> tuple[bool, int, int, int]:
        """Check rate limit for token refresh requests.

        Args:
            request: FastAPI request
            user_id: User ID requesting token refresh

        Returns:
            Tuple of (allowed, remaining, limit, reset_seconds)

        Raises:
            HTTPException: If rate limit exceeded
        """
        key = self._get_auth_key(request, user_id)
        allowed, remaining, limit, reset = await self._limiter._in_memory.check_rate_limit(
            key, AUTH_RATE_CONFIGS.TOKEN_REFRESH
        )

        if not allowed:
            logger.warning(
                f"Token refresh rate limit exceeded for user {user_id} from {request.client.host}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many token refresh attempts. Please try again later.",
                    "retry_after": reset,
                },
                headers=get_rate_limit_headers(remaining, limit, reset),
            )

        return allowed, remaining, limit, reset


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Dependencies
# ═══════════════════════════════════════════════════════════════════════════════

# Global instance
_auth_rate_limiter: Optional[AuthRateLimiter] = None


def get_auth_rate_limiter() -> AuthRateLimiter:
    """Get the global authentication rate limiter instance.

    Returns:
        AuthRateLimiter singleton instance
    """
    global _auth_rate_limiter
    if _auth_rate_limiter is None:
        _auth_rate_limiter = AuthRateLimiter()
    return _auth_rate_limiter


# Convenience type aliases for dependencies
LoginRateLimiter = AuthRateLimiter
PasswordResetRateLimiter = AuthRateLimiter
RegistrationRateLimiter = AuthRateLimiter
