"""
Token Revocation System with Redis
نظام إلغاء الرموز مع Redis

Provides:
- Redis-based token revocation storage
- Individual token revocation by JTI
- User-level revocation (revoke all user tokens)
- Tenant-level revocation (revoke all tenant tokens)
- Automatic TTL management
- High-performance async operations
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import config

logger = logging.getLogger(__name__)


@dataclass
class RevocationInfo:
    """Information about a revoked token"""

    revoked_at: float
    reason: str
    user_id: str | None = None
    tenant_id: str | None = None


class RedisTokenRevocationStore:
    """
    Redis-based token revocation storage.
    مخزن إلغاء الرموز القائم على Redis.

    Features:
    - Fast O(1) token lookup
    - Automatic expiration with TTL
    - Distributed across multiple instances
    - Support for different revocation strategies

    Example:
        >>> store = RedisTokenRevocationStore()
        >>> await store.initialize()
        >>> await store.revoke_token("jti-123", expires_in=3600, reason="logout")
        >>> is_revoked = await store.is_token_revoked("jti-123")
    """

    # Redis key prefixes
    TOKEN_PREFIX = "revoked:token:"  # Individual token revocation
    USER_PREFIX = "revoked:user:"  # User-level revocation
    TENANT_PREFIX = "revoked:tenant:"  # Tenant-level revocation

    def __init__(self, redis_url: str | None = None):
        """
        Initialize the Redis token revocation store.

        Args:
            redis_url: Redis connection URL (defaults to config)
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis is required for token revocation. "
                "Install with: pip install redis[asyncio]"
            )

        self._redis: aioredis.Redis | None = None
        self._redis_url = redis_url or config.REDIS_URL or self._build_redis_url()
        self._initialized = False

    def _build_redis_url(self) -> str:
        """Build Redis URL from configuration"""
        if config.REDIS_PASSWORD:
            return (
                f"redis://:{config.REDIS_PASSWORD}@"
                f"{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}"
            )
        return f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}"

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        if self._initialized:
            return

        try:
            self._redis = await aioredis.from_url(
                self._redis_url,
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
            logger.error(f"Failed to initialize Redis token revocation: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._initialized = False
            logger.info("Redis token revocation store closed")

    # ─────────────────────────────────────────────────────────────────────────
    # Token (JTI) Revocation
    # ─────────────────────────────────────────────────────────────────────────

    async def revoke_token(
        self,
        jti: str,
        expires_in: int | None = None,
        reason: str = "manual",
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        """
        Revoke a single token by JTI.
        إلغاء رمز واحد بواسطة JTI.

        Args:
            jti: JWT ID to revoke
            expires_in: Seconds until token expires (for TTL)
            reason: Reason for revocation
            user_id: Optional user ID
            tenant_id: Optional tenant ID

        Returns:
            True if revoked successfully

        Example:
            >>> await store.revoke_token(
            ...     jti="abc123",
            ...     expires_in=3600,
            ...     reason="user_logout",
            ...     user_id="user-456"
            ... )
        """
        if not self._initialized:
            await self.initialize()

        if not jti:
            return False

        # Default TTL: 24 hours
        ttl = expires_in or 86400

        # Store revocation info
        key = f"{self.TOKEN_PREFIX}{jti}"
        value = {
            "revoked_at": time.time(),
            "reason": reason,
            "user_id": user_id,
            "tenant_id": tenant_id,
        }

        try:
            # Store with TTL (auto-cleanup)
            await self._redis.setex(
                key, ttl, str(value)  # Store as string for simplicity
            )

            logger.info(
                f"Token revoked: jti={jti[:8]}..., " f"reason={reason}, ttl={ttl}s"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False

    async def is_token_revoked(self, jti: str) -> bool:
        """
        Check if a token is revoked by JTI.
        التحقق من إلغاء الرمز بواسطة JTI.

        Args:
            jti: JWT ID to check

        Returns:
            True if token is revoked

        Example:
            >>> is_revoked = await store.is_token_revoked("abc123")
        """
        if not self._initialized:
            await self.initialize()

        if not jti:
            return False

        try:
            key = f"{self.TOKEN_PREFIX}{jti}"
            exists = await self._redis.exists(key)
            return exists > 0

        except Exception as e:
            logger.error(f"Error checking token revocation: {e}")
            # Fail open: don't block access on Redis errors
            return False

    async def get_revocation_info(self, jti: str) -> dict[str, Any] | None:
        """
        Get detailed revocation information for a token.
        الحصول على معلومات إلغاء مفصلة للرمز.

        Args:
            jti: JWT ID

        Returns:
            Revocation info dict or None
        """
        if not self._initialized:
            await self.initialize()

        if not jti:
            return None

        try:
            key = f"{self.TOKEN_PREFIX}{jti}"
            value = await self._redis.get(key)

            if value:
                # Parse stored value
                return json.loads(value)

            return None

        except Exception as e:
            logger.error(f"Error getting revocation info: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # User-Level Revocation
    # ─────────────────────────────────────────────────────────────────────────

    async def revoke_all_user_tokens(
        self,
        user_id: str,
        reason: str = "user_logout",
    ) -> bool:
        """
        Revoke all tokens for a user.
        إلغاء جميع الرموز للمستخدم.

        Any token issued before this timestamp will be invalid.

        Args:
            user_id: User ID
            reason: Reason for revocation

        Returns:
            True if revoked successfully

        Example:
            >>> await store.revoke_all_user_tokens(
            ...     user_id="user-456",
            ...     reason="password_change"
            ... )
        """
        if not self._initialized:
            await self.initialize()

        if not user_id:
            return False

        try:
            key = f"{self.USER_PREFIX}{user_id}"
            value = {
                "revoked_at": time.time(),
                "reason": reason,
            }

            # Store with long TTL (30 days)
            # This ensures old tokens are rejected even if they haven't expired
            await self._redis.setex(key, 2592000, str(value))  # 30 days

            logger.info(f"All user tokens revoked: user_id={user_id}, reason={reason}")
            return True

        except Exception as e:
            logger.error(f"Failed to revoke user tokens: {e}")
            return False

    async def is_user_token_revoked(
        self,
        user_id: str,
        token_issued_at: float,
    ) -> bool:
        """
        Check if a user's token is revoked.
        التحقق من إلغاء رمز المستخدم.

        Args:
            user_id: User ID
            token_issued_at: When token was issued (iat claim)

        Returns:
            True if token was issued before user revocation

        Example:
            >>> is_revoked = await store.is_user_token_revoked(
            ...     user_id="user-456",
            ...     token_issued_at=1640000000.0
            ... )
        """
        if not self._initialized:
            await self.initialize()

        if not user_id:
            return False

        try:
            key = f"{self.USER_PREFIX}{user_id}"
            value = await self._redis.get(key)

            if value:
                data = json.loads(value)
                revoked_at = data.get("revoked_at", 0)

                # Token is revoked if it was issued before revocation
                return token_issued_at < revoked_at

            return False

        except Exception as e:
            logger.error(f"Error checking user token revocation: {e}")
            return False

    async def clear_user_revocation(self, user_id: str) -> bool:
        """
        Clear user-level revocation.
        مسح إلغاء على مستوى المستخدم.

        Use after user re-authenticates with new password.

        Args:
            user_id: User ID

        Returns:
            True if cleared successfully
        """
        if not self._initialized:
            await self.initialize()

        if not user_id:
            return False

        try:
            key = f"{self.USER_PREFIX}{user_id}"
            deleted = await self._redis.delete(key)

            if deleted:
                logger.info(f"User revocation cleared: user_id={user_id}")

            return deleted > 0

        except Exception as e:
            logger.error(f"Failed to clear user revocation: {e}")
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Tenant-Level Revocation
    # ─────────────────────────────────────────────────────────────────────────

    async def revoke_all_tenant_tokens(
        self,
        tenant_id: str,
        reason: str = "security",
    ) -> bool:
        """
        Revoke all tokens for a tenant.
        إلغاء جميع الرموز للمستأجر.

        Use with caution - affects all users in the tenant.

        Args:
            tenant_id: Tenant ID
            reason: Reason for revocation

        Returns:
            True if revoked successfully
        """
        if not self._initialized:
            await self.initialize()

        if not tenant_id:
            return False

        try:
            key = f"{self.TENANT_PREFIX}{tenant_id}"
            value = {
                "revoked_at": time.time(),
                "reason": reason,
            }

            # Store with long TTL (30 days)
            await self._redis.setex(key, 2592000, str(value))

            logger.warning(
                f"All tenant tokens revoked: tenant_id={tenant_id}, " f"reason={reason}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to revoke tenant tokens: {e}")
            return False

    async def is_tenant_token_revoked(
        self,
        tenant_id: str,
        token_issued_at: float,
    ) -> bool:
        """
        Check if a tenant's token is revoked.
        التحقق من إلغاء رمز المستأجر.

        Args:
            tenant_id: Tenant ID
            token_issued_at: When token was issued (iat claim)

        Returns:
            True if token was issued before tenant revocation
        """
        if not self._initialized:
            await self.initialize()

        if not tenant_id:
            return False

        try:
            key = f"{self.TENANT_PREFIX}{tenant_id}"
            value = await self._redis.get(key)

            if value:
                data = json.loads(value)
                revoked_at = data.get("revoked_at", 0)

                return token_issued_at < revoked_at

            return False

        except Exception as e:
            logger.error(f"Error checking tenant token revocation: {e}")
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Combined Check
    # ─────────────────────────────────────────────────────────────────────────

    async def is_revoked(
        self,
        jti: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        issued_at: float | None = None,
    ) -> tuple[bool, str | None]:
        """
        Check if a token is revoked by any method.
        التحقق من إلغاء الرمز بأي طريقة.

        Args:
            jti: JWT ID
            user_id: User ID
            tenant_id: Tenant ID
            issued_at: Token issued at timestamp

        Returns:
            (is_revoked, reason)

        Example:
            >>> is_revoked, reason = await store.is_revoked(
            ...     jti="abc123",
            ...     user_id="user-456",
            ...     issued_at=1640000000.0
            ... )
            >>> if is_revoked:
            ...     print(f"Token revoked: {reason}")
        """
        if not self._initialized:
            await self.initialize()

        # Check JTI revocation
        if jti and await self.is_token_revoked(jti):
            return True, "token_revoked"

        # Check user revocation
        if user_id and issued_at and await self.is_user_token_revoked(user_id, issued_at):
            return True, "user_tokens_revoked"

        # Check tenant revocation
        if tenant_id and issued_at:
            if await self.is_tenant_token_revoked(tenant_id, issued_at):
                return True, "tenant_tokens_revoked"

        return False, None

    # ─────────────────────────────────────────────────────────────────────────
    # Statistics and Health
    # ─────────────────────────────────────────────────────────────────────────

    async def get_stats(self) -> dict[str, Any]:
        """
        Get revocation statistics.
        الحصول على إحصائيات الإلغاء.

        Returns:
            Statistics dictionary
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Count keys by prefix
            token_keys = await self._redis.keys(f"{self.TOKEN_PREFIX}*")
            user_keys = await self._redis.keys(f"{self.USER_PREFIX}*")
            tenant_keys = await self._redis.keys(f"{self.TENANT_PREFIX}*")

            return {
                "initialized": self._initialized,
                "revoked_tokens": len(token_keys),
                "revoked_users": len(user_keys),
                "revoked_tenants": len(tenant_keys),
                "redis_url": self._redis_url.split("@")[-1],  # Hide password
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "initialized": self._initialized,
                "error": str(e),
            }

    async def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.
        التحقق من صحة اتصال Redis.

        Returns:
            True if healthy
        """
        try:
            if not self._initialized:
                await self.initialize()

            await self._redis.ping()
            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
# Global Instance and Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────

_store: RedisTokenRevocationStore | None = None


async def get_revocation_store() -> RedisTokenRevocationStore:
    """
    Get the global token revocation store instance.
    الحصول على نسخة مخزن إلغاء الرموز العامة.

    Returns:
        RedisTokenRevocationStore instance
    """
    global _store

    if _store is None:
        _store = RedisTokenRevocationStore()
        await _store.initialize()

    return _store


async def revoke_token(
    jti: str,
    expires_in: int | None = None,
    reason: str = "manual",
    user_id: str | None = None,
) -> bool:
    """
    Revoke a single token.
    إلغاء رمز واحد.

    Args:
        jti: JWT ID
        expires_in: Seconds until expiry
        reason: Revocation reason
        user_id: Optional user ID

    Returns:
        True if revoked successfully
    """
    store = await get_revocation_store()
    return await store.revoke_token(
        jti=jti,
        expires_in=expires_in,
        reason=reason,
        user_id=user_id,
    )


async def revoke_all_user_tokens(user_id: str, reason: str = "logout") -> bool:
    """
    Revoke all tokens for a user.
    إلغاء جميع رموز المستخدم.

    Args:
        user_id: User ID
        reason: Revocation reason

    Returns:
        True if revoked successfully
    """
    store = await get_revocation_store()
    return await store.revoke_all_user_tokens(user_id=user_id, reason=reason)


async def is_token_revoked(
    jti: str | None = None,
    user_id: str | None = None,
    tenant_id: str | None = None,
    issued_at: float | None = None,
) -> tuple[bool, str | None]:
    """
    Check if a token is revoked.
    التحقق من إلغاء الرمز.

    Args:
        jti: JWT ID
        user_id: User ID
        tenant_id: Tenant ID
        issued_at: Token issued at timestamp

    Returns:
        (is_revoked, reason)
    """
    store = await get_revocation_store()
    return await store.is_revoked(
        jti=jti,
        user_id=user_id,
        tenant_id=tenant_id,
        issued_at=issued_at,
    )
