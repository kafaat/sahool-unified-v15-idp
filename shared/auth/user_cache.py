"""
User Cache Service for JWT Authentication
خدمة تخزين المستخدمين المؤقت للتحقق من JWT

Provides caching for user validation to improve performance.
"""

import json
import logging
from datetime import timedelta
from typing import Optional

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import config

logger = logging.getLogger(__name__)


class UserCache:
    """
    Redis-based cache for user validation data.
    تخزين مؤقت يعتمد على Redis لبيانات التحقق من المستخدم.
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        ttl_seconds: int = 300,  # 5 minutes default
        key_prefix: str = "user_auth:",
    ):
        """
        Initialize user cache.

        Args:
            redis_client: Redis client instance (optional)
            ttl_seconds: Time to live for cached entries in seconds
            key_prefix: Prefix for cache keys
        """
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds
        self.key_prefix = key_prefix
        self._enabled = REDIS_AVAILABLE and redis_client is not None

    async def get_user_status(self, user_id: str) -> Optional[dict]:
        """
        Get cached user status.

        Args:
            user_id: User identifier

        Returns:
            User status dict or None if not cached
        """
        if not self._enabled:
            return None

        try:
            key = f"{self.key_prefix}{user_id}"
            cached_data = await self.redis_client.get(key)

            if cached_data:
                logger.debug(f"Cache hit for user {user_id}")
                return json.loads(cached_data)

            logger.debug(f"Cache miss for user {user_id}")
            return None

        except Exception as e:
            logger.warning(f"Cache get error for user {user_id}: {e}")
            return None

    async def set_user_status(
        self,
        user_id: str,
        is_active: bool,
        is_verified: bool,
        roles: list[str],
        email: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """
        Cache user status.

        Args:
            user_id: User identifier
            is_active: Whether user is active
            is_verified: Whether user is verified
            roles: User roles
            email: User email (optional)
            tenant_id: Tenant ID (optional)

        Returns:
            True if cached successfully
        """
        if not self._enabled:
            return False

        try:
            key = f"{self.key_prefix}{user_id}"
            data = {
                "user_id": user_id,
                "is_active": is_active,
                "is_verified": is_verified,
                "roles": roles,
                "email": email,
                "tenant_id": tenant_id,
            }

            await self.redis_client.setex(
                key,
                timedelta(seconds=self.ttl_seconds),
                json.dumps(data),
            )

            logger.debug(f"Cached user status for {user_id}")
            return True

        except Exception as e:
            logger.warning(f"Cache set error for user {user_id}: {e}")
            return False

    async def invalidate_user(self, user_id: str) -> bool:
        """
        Invalidate cached user data.

        Args:
            user_id: User identifier

        Returns:
            True if invalidated successfully
        """
        if not self._enabled:
            return False

        try:
            key = f"{self.key_prefix}{user_id}"
            await self.redis_client.delete(key)
            logger.debug(f"Invalidated cache for user {user_id}")
            return True

        except Exception as e:
            logger.warning(f"Cache invalidate error for user {user_id}: {e}")
            return False

    async def clear_all(self) -> int:
        """
        Clear all cached user data.

        Returns:
            Number of keys deleted
        """
        if not self._enabled:
            return 0

        try:
            pattern = f"{self.key_prefix}*"
            keys = []

            async for key in self.redis_client.scan_iter(pattern):
                keys.append(key)

            if keys:
                count = await self.redis_client.delete(*keys)
                logger.info(f"Cleared {count} cached users")
                return count

            return 0

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0


# Global cache instance
_user_cache: Optional[UserCache] = None


def get_user_cache() -> Optional[UserCache]:
    """
    Get the global user cache instance.

    Returns:
        UserCache instance or None if Redis not available
    """
    global _user_cache
    return _user_cache


async def init_user_cache(
    redis_url: Optional[str] = None,
    ttl_seconds: int = 300,
) -> Optional[UserCache]:
    """
    Initialize the global user cache.

    Args:
        redis_url: Redis connection URL (defaults to config.REDIS_URL)
        ttl_seconds: Cache TTL in seconds

    Returns:
        UserCache instance or None if Redis not available
    """
    global _user_cache

    if not REDIS_AVAILABLE:
        logger.warning("Redis not available, user caching disabled")
        return None

    try:
        redis_url = redis_url or config.REDIS_URL

        if not redis_url:
            logger.warning("REDIS_URL not configured, user caching disabled")
            return None

        redis_client = await redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

        # Test connection
        await redis_client.ping()

        _user_cache = UserCache(
            redis_client=redis_client,
            ttl_seconds=ttl_seconds,
        )

        logger.info("User cache initialized successfully")
        return _user_cache

    except Exception as e:
        logger.error(f"Failed to initialize user cache: {e}")
        return None


async def close_user_cache() -> None:
    """
    Close the global user cache connection.
    """
    global _user_cache

    if _user_cache and _user_cache.redis_client:
        await _user_cache.redis_client.close()
        _user_cache = None
        logger.info("User cache closed")
