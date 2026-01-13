"""
Token Revocation System with Redis (Python/FastAPI)
نظام إلغاء الرموز مع Redis

Port of NestJS token-revocation.ts to Python for FastAPI services.
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def _sanitize_log_value(value: str | None, max_length: int = 100) -> str:
    """
    Sanitize a value for safe logging to prevent log injection attacks.

    Args:
        value: The value to sanitize
        max_length: Maximum length of the output string

    Returns:
        Sanitized string safe for logging
    """
    if value is None:
        return "None"
    # Remove newlines, carriage returns, and other control characters
    sanitized = re.sub(r"[\r\n\t\x00-\x1f\x7f-\x9f]", "", str(value))
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    return sanitized


@dataclass
class RevocationInfo:
    """Revocation information"""

    revoked_at: float
    reason: str
    user_id: str | None = None
    tenant_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "revoked_at": self.revoked_at,
            "reason": self.reason,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RevocationInfo":
        """Create from dictionary"""
        return cls(
            revoked_at=data["revoked_at"],
            reason=data["reason"],
            user_id=data.get("user_id"),
            tenant_id=data.get("tenant_id"),
        )


@dataclass
class RevocationCheckResult:
    """Token revocation check result"""

    is_revoked: bool
    reason: str | None = None


@dataclass
class RevocationStats:
    """Revocation statistics"""

    initialized: bool
    revoked_tokens: int = 0
    revoked_users: int = 0
    revoked_tenants: int = 0
    redis_url: str | None = None


class RedisTokenRevocationStore:
    """
    Redis-based token revocation service
    خدمة إلغاء الرموز القائمة على Redis

    Port of NestJS RedisTokenRevocationStore to Python.
    """

    # Redis key prefixes
    TOKEN_PREFIX = "revoked:token:"
    USER_PREFIX = "revoked:user:"
    TENANT_PREFIX = "revoked:tenant:"
    FAMILY_PREFIX = "revoked:family:"

    def __init__(self, redis_url: str | None = None):
        """
        Initialize token revocation store

        Args:
            redis_url: Redis connection URL. If None, will build from env vars.
        """
        self._redis_url = redis_url
        self._redis: Redis | None = None
        self._initialized = False

    def _build_redis_url(self) -> str:
        """
        Build Redis URL from configuration

        Environment variables:
            REDIS_URL: Full Redis URL (takes precedence)
            REDIS_HOST: Redis host (default: localhost)
            REDIS_PORT: Redis port (default: 6379)
            REDIS_PASSWORD: Redis password (optional)
            REDIS_DB: Redis database number (default: 0)
        """
        if self._redis_url:
            return self._redis_url

        # Check for full URL first
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            return redis_url

        # Build from components
        password = os.getenv("REDIS_PASSWORD")
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))

        if password:
            return f"redis://:{password}@{host}:{port}/{db}"

        return f"redis://{host}:{port}/{db}"

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        if self._initialized:
            return

        try:
            url = self._build_redis_url()

            self._redis = await redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )

            # Test connection
            await self._redis.ping()

            self._initialized = True
            logger.info("Redis token revocation store initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._initialized = False
            logger.info("Redis token revocation store closed")

    async def revoke_token(
        self,
        jti: str,
        expires_in: int = 86400,
        reason: str = "manual",
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        """
        Revoke a single token by JTI

        Args:
            jti: JWT ID to revoke
            expires_in: TTL in seconds (default: 24 hours)
            reason: Revocation reason
            user_id: User ID who owned the token
            tenant_id: Tenant ID

        Returns:
            True if successfully revoked, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not jti:
            return False

        key = f"{self.TOKEN_PREFIX}{jti}"
        value = RevocationInfo(
            revoked_at=datetime.now().timestamp(),
            reason=reason,
            user_id=user_id,
            tenant_id=tenant_id,
        )

        try:
            await self._redis.setex(key, expires_in, json.dumps(value.to_dict()))

            logger.info(
                "Token revoked: jti=%s, reason=%s, ttl=%ss",
                _sanitize_log_value(jti[:8] if len(jti) > 8 else jti) + "...",
                _sanitize_log_value(reason),
                expires_in,
            )

            return True

        except RedisError as e:
            logger.error(f"Failed to revoke token: {e}")
            return False

    async def is_token_revoked(self, jti: str) -> bool:
        """
        Check if a token is revoked by JTI

        Args:
            jti: JWT ID to check

        Returns:
            True if token is revoked, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not jti:
            return False

        try:
            key = f"{self.TOKEN_PREFIX}{jti}"
            exists = await self._redis.exists(key)
            return exists > 0

        except RedisError as e:
            logger.error(f"Error checking token revocation: {e}")
            return False

    async def revoke_all_user_tokens(self, user_id: str, reason: str = "user_logout") -> bool:
        """
        Revoke all tokens for a user

        Args:
            user_id: User ID whose tokens to revoke
            reason: Revocation reason

        Returns:
            True if successfully revoked, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not user_id:
            return False

        try:
            key = f"{self.USER_PREFIX}{user_id}"
            value = RevocationInfo(
                revoked_at=datetime.now().timestamp(),
                reason=reason,
            )

            # Store for 30 days (longer than typical token lifetime)
            await self._redis.setex(key, 2592000, json.dumps(value.to_dict()))

            logger.info(
                "All user tokens revoked: user_id=%s, reason=%s",
                _sanitize_log_value(user_id),
                _sanitize_log_value(reason),
            )

            return True

        except RedisError as e:
            logger.error(f"Failed to revoke user tokens: {e}")
            return False

    async def is_user_token_revoked(self, user_id: str, token_issued_at: float) -> bool:
        """
        Check if a user's token is revoked

        Args:
            user_id: User ID to check
            token_issued_at: Token issued timestamp (Unix timestamp)

        Returns:
            True if token was issued before user revocation, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not user_id:
            return False

        try:
            key = f"{self.USER_PREFIX}{user_id}"
            value_str = await self._redis.get(key)

            if value_str:
                data = json.loads(value_str)
                revoked_at = data.get("revoked_at", 0)
                return token_issued_at < revoked_at

            return False

        except RedisError as e:
            logger.error(f"Error checking user token revocation: {e}")
            return False

    async def revoke_all_tenant_tokens(
        self, tenant_id: str, reason: str = "tenant_suspended"
    ) -> bool:
        """
        Revoke all tokens for a tenant

        Args:
            tenant_id: Tenant ID whose tokens to revoke
            reason: Revocation reason

        Returns:
            True if successfully revoked, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not tenant_id:
            return False

        try:
            key = f"{self.TENANT_PREFIX}{tenant_id}"
            value = RevocationInfo(
                revoked_at=datetime.now().timestamp(),
                reason=reason,
            )

            # Store for 30 days
            await self._redis.setex(key, 2592000, json.dumps(value.to_dict()))

            logger.info(
                "All tenant tokens revoked: tenant_id=%s, reason=%s",
                _sanitize_log_value(tenant_id),
                _sanitize_log_value(reason),
            )

            return True

        except RedisError as e:
            logger.error(f"Failed to revoke tenant tokens: {e}")
            return False

    async def is_tenant_token_revoked(self, tenant_id: str, token_issued_at: float) -> bool:
        """
        Check if a tenant's token is revoked

        Args:
            tenant_id: Tenant ID to check
            token_issued_at: Token issued timestamp (Unix timestamp)

        Returns:
            True if token was issued before tenant revocation, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not tenant_id:
            return False

        try:
            key = f"{self.TENANT_PREFIX}{tenant_id}"
            value_str = await self._redis.get(key)

            if value_str:
                data = json.loads(value_str)
                revoked_at = data.get("revoked_at", 0)
                return token_issued_at < revoked_at

            return False

        except RedisError as e:
            logger.error(f"Error checking tenant token revocation: {e}")
            return False

    async def revoke_token_family(
        self, family_id: str, reason: str = "refresh_token_rotation"
    ) -> bool:
        """
        Revoke all tokens in a token family (for refresh token rotation)

        Args:
            family_id: Token family ID
            reason: Revocation reason

        Returns:
            True if successfully revoked, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not family_id:
            return False

        try:
            key = f"{self.FAMILY_PREFIX}{family_id}"
            value = RevocationInfo(
                revoked_at=datetime.now().timestamp(),
                reason=reason,
            )

            # Store for 30 days
            await self._redis.setex(key, 2592000, json.dumps(value.to_dict()))

            logger.info(
                "Token family revoked: family_id=%s, reason=%s",
                _sanitize_log_value(family_id),
                _sanitize_log_value(reason),
            )

            return True

        except RedisError as e:
            logger.error(f"Failed to revoke token family: {e}")
            return False

    async def is_token_family_revoked(self, family_id: str) -> bool:
        """
        Check if a token family is revoked

        Args:
            family_id: Token family ID to check

        Returns:
            True if family is revoked, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        if not family_id:
            return False

        try:
            key = f"{self.FAMILY_PREFIX}{family_id}"
            exists = await self._redis.exists(key)
            return exists > 0

        except RedisError as e:
            logger.error(f"Error checking token family revocation: {e}")
            return False

    async def is_revoked(
        self,
        jti: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        family_id: str | None = None,
        issued_at: float | None = None,
    ) -> RevocationCheckResult:
        """
        Check if a token is revoked by any method

        Args:
            jti: JWT ID
            user_id: User ID
            tenant_id: Tenant ID
            family_id: Token family ID
            issued_at: Token issued timestamp

        Returns:
            RevocationCheckResult with revocation status and reason
        """
        if not self._initialized:
            await self.initialize()

        # Check individual token revocation by JTI
        if jti and await self.is_token_revoked(jti):
            return RevocationCheckResult(is_revoked=True, reason="token_revoked")

        # Check token family revocation
        if family_id and await self.is_token_family_revoked(family_id):
            return RevocationCheckResult(is_revoked=True, reason="family_revoked")

        # Check user-level revocation
        if user_id and issued_at and await self.is_user_token_revoked(user_id, issued_at):
            return RevocationCheckResult(is_revoked=True, reason="user_tokens_revoked")

        # Check tenant-level revocation
        if tenant_id and issued_at:
            if await self.is_tenant_token_revoked(tenant_id, issued_at):
                return RevocationCheckResult(is_revoked=True, reason="tenant_tokens_revoked")

        return RevocationCheckResult(is_revoked=False)

    async def health_check(self) -> bool:
        """
        Check if Redis connection is healthy

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            if not self._initialized:
                await self.initialize()

            await self._redis.ping()
            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def get_stats(self) -> RevocationStats:
        """
        Get revocation statistics

        Returns:
            RevocationStats with current statistics
        """
        if not self._initialized:
            return RevocationStats(initialized=False)

        try:
            # Count keys by prefix (this can be expensive on large datasets)
            revoked_tokens = len(await self._redis.keys(f"{self.TOKEN_PREFIX}*") or [])
            revoked_users = len(await self._redis.keys(f"{self.USER_PREFIX}*") or [])
            revoked_tenants = len(await self._redis.keys(f"{self.TENANT_PREFIX}*") or [])

            return RevocationStats(
                initialized=True,
                revoked_tokens=revoked_tokens,
                revoked_users=revoked_users,
                revoked_tenants=revoked_tenants,
                redis_url=self._build_redis_url().split("@")[-1]
                if "@" in self._build_redis_url()
                else self._build_redis_url(),
            )

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return RevocationStats(initialized=True)


# Global instance
_revocation_store: RedisTokenRevocationStore | None = None


def get_revocation_store() -> RedisTokenRevocationStore:
    """
    Get or create the global token revocation store

    Returns:
        RedisTokenRevocationStore instance
    """
    global _revocation_store
    if _revocation_store is None:
        _revocation_store = RedisTokenRevocationStore()
    return _revocation_store


def set_revocation_store(store: RedisTokenRevocationStore) -> None:
    """
    Set the global token revocation store

    Args:
        store: RedisTokenRevocationStore instance to set
    """
    global _revocation_store
    _revocation_store = store
