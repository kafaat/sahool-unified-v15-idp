"""
User Cache Service for JWT Authentication
خدمة تخزين المستخدمين المؤقت للتحقق من JWT

Provides caching for user validation to improve performance.
Includes TTL management, cache invalidation, batch operations, and health checks.
"""

import json
import logging
import time
from datetime import timedelta
from typing import Any

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
        redis_client: redis.Redis | None = None,
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

    async def get_user_status(self, user_id: str) -> dict | None:
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
        email: str | None = None,
        tenant_id: str | None = None,
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

    async def invalidate_multiple(self, user_ids: list[str]) -> int:
        """
        Invalidate cache for multiple users at once.
        تعطيل ذاكرة التخزين المؤقت لعدة مستخدمين في المرة الواحدة.

        Args:
            user_ids: List of user identifiers to invalidate

        Returns:
            Number of users invalidated
        """
        if not self._enabled or not user_ids:
            return 0

        try:
            keys_to_delete = [f"{self.key_prefix}{uid}" for uid in user_ids]
            count = await self.redis_client.delete(*keys_to_delete)
            logger.debug(f"Invalidated cache for {count} users")
            return count

        except Exception as e:
            logger.warning(f"Batch invalidation error: {e}")
            return 0

    async def invalidate_by_tenant(self, tenant_id: str) -> int:
        """
        Invalidate all users from a specific tenant.
        تعطيل جميع المستخدمين من مستأجر معين.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Number of users invalidated
        """
        if not self._enabled or not tenant_id:
            return 0

        try:
            # Scan for all keys with this tenant_id
            count = 0
            async for key in self.redis_client.scan_iter(f"{self.key_prefix}*"):
                try:
                    cached_data = await self.redis_client.get(key)
                    if cached_data:
                        data = json.loads(cached_data)
                        if data.get("tenant_id") == tenant_id:
                            await self.redis_client.delete(key)
                            count += 1
                except (json.JSONDecodeError, Exception):
                    continue

            logger.info(f"Invalidated {count} users for tenant {tenant_id}")
            return count

        except Exception as e:
            logger.error(f"Tenant invalidation error: {e}")
            return 0

    async def get_ttl(self, user_id: str) -> int | None:
        """
        Get the remaining TTL (time to live) for a cached user entry.
        احصل على المدة المتبقية (TTL) لإدخال المستخدم المخزن مؤقتًا.

        Args:
            user_id: User identifier

        Returns:
            Remaining TTL in seconds, or None if key doesn't exist
        """
        if not self._enabled:
            return None

        try:
            key = f"{self.key_prefix}{user_id}"
            ttl = await self.redis_client.ttl(key)

            if ttl == -2:  # Key doesn't exist
                return None
            if ttl == -1:  # Key exists but has no associated expire
                return None

            return ttl

        except Exception as e:
            logger.warning(f"Error getting TTL for user {user_id}: {e}")
            return None

    async def extend_ttl(
        self,
        user_id: str,
        new_ttl_seconds: int | None = None,
    ) -> bool:
        """
        Extend the TTL for an existing cached user entry.
        قم بتمديد TTL لإدخال المستخدم المخزن مؤقتًا الموجود.

        Args:
            user_id: User identifier
            new_ttl_seconds: New TTL in seconds (defaults to self.ttl_seconds)

        Returns:
            True if TTL was extended successfully
        """
        if not self._enabled:
            return False

        try:
            key = f"{self.key_prefix}{user_id}"
            ttl = new_ttl_seconds or self.ttl_seconds

            # Use EXPIRE to extend the TTL of existing key
            result = await self.redis_client.expire(key, ttl)

            if result:
                logger.debug(f"Extended TTL for user {user_id} to {ttl}s")
                return True
            else:
                logger.debug(f"User {user_id} not found in cache, cannot extend TTL")
                return False

        except Exception as e:
            logger.warning(f"Error extending TTL for user {user_id}: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.
        التحقق من صحة اتصال Redis.

        Returns:
            True if cache is healthy and accessible
        """
        if not self._enabled:
            return False

        try:
            await self.redis_client.ping()
            logger.debug("Cache health check passed")
            return True

        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False

    async def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        احصل على إحصائيات التخزين المؤقت.

        Returns:
            Dictionary with cache statistics including:
            - enabled: Whether cache is enabled
            - total_cached_users: Total number of cached users
            - ttl_seconds: Default TTL in seconds
            - key_prefix: Cache key prefix
            - connected: Whether Redis is connected
        """
        stats = {
            "enabled": self._enabled,
            "ttl_seconds": self.ttl_seconds,
            "key_prefix": self.key_prefix,
            "connected": False,
            "total_cached_users": 0,
        }

        if not self._enabled:
            return stats

        try:
            # Check connection
            await self.redis_client.ping()
            stats["connected"] = True

            # Count cached users
            keys = []
            async for key in self.redis_client.scan_iter(f"{self.key_prefix}*"):
                keys.append(key)

            stats["total_cached_users"] = len(keys)

            # Calculate memory usage (approximate)
            if keys:
                try:
                    memory_info = await self.redis_client.info("memory")
                    stats["memory_used_bytes"] = memory_info.get("used_memory", 0)
                except Exception:
                    pass

            logger.debug(f"Cache stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            stats["error"] = str(e)
            return stats

    async def exists(self, user_id: str) -> bool:
        """
        Check if a user is cached without retrieving the data.
        تحقق من تخزين المستخدم مؤقتًا دون استرجاع البيانات.

        Args:
            user_id: User identifier

        Returns:
            True if user is cached, False otherwise
        """
        if not self._enabled:
            return False

        try:
            key = f"{self.key_prefix}{user_id}"
            exists = await self.redis_client.exists(key)
            return exists > 0

        except Exception as e:
            logger.warning(f"Error checking cache existence for user {user_id}: {e}")
            return False


# Global cache instance
_user_cache: UserCache | None = None


def get_user_cache() -> UserCache | None:
    """
    Get the global user cache instance.

    Returns:
        UserCache instance or None if Redis not available
    """
    global _user_cache
    return _user_cache


async def init_user_cache(
    redis_url: str | None = None,
    ttl_seconds: int = 300,
) -> UserCache | None:
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


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions (Module-Level API)
# ─────────────────────────────────────────────────────────────────────────────


async def cache_user(
    user_id: str,
    is_active: bool,
    is_verified: bool,
    roles: list[str],
    email: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """
    Cache user status using the global cache instance.
    تخزين حالة المستخدم مؤقتًا باستخدام نسخة الذاكرة المؤقتة العامة.
    """
    cache = get_user_cache()
    if not cache:
        return False

    return await cache.set_user_status(
        user_id=user_id,
        is_active=is_active,
        is_verified=is_verified,
        roles=roles,
        email=email,
        tenant_id=tenant_id,
    )


async def get_cached_user(user_id: str) -> dict | None:
    """
    Get cached user status using the global cache instance.
    احصل على حالة المستخدم المخزنة مؤقتًا باستخدام نسخة الذاكرة المؤقتة العامة.
    """
    cache = get_user_cache()
    if not cache:
        return None

    return await cache.get_user_status(user_id)


async def invalidate_cached_user(user_id: str) -> bool:
    """
    Invalidate a user from cache using the global cache instance.
    تعطيل مستخدم من الذاكرة المؤقتة باستخدام نسخة الذاكرة المؤقتة العامة.
    """
    cache = get_user_cache()
    if not cache:
        return False

    return await cache.invalidate_user(user_id)


async def invalidate_cached_users(user_ids: list[str]) -> int:
    """
    Invalidate multiple users from cache.
    تعطيل عدة مستخدمين من الذاكرة المؤقتة.
    """
    cache = get_user_cache()
    if not cache:
        return 0

    return await cache.invalidate_multiple(user_ids)


async def invalidate_tenant_cache(tenant_id: str) -> int:
    """
    Invalidate all users from a tenant.
    تعطيل جميع المستخدمين من مستأجر معين.
    """
    cache = get_user_cache()
    if not cache:
        return 0

    return await cache.invalidate_by_tenant(tenant_id)


async def check_cache_health() -> bool:
    """
    Check if the user cache is healthy.
    تحقق من أن ذاكرة التخزين المؤقت للمستخدم صحية.
    """
    cache = get_user_cache()
    if not cache:
        return False

    return await cache.health_check()


async def get_cache_stats() -> dict[str, Any]:
    """
    Get cache statistics.
    احصل على إحصائيات الذاكرة المؤقتة.
    """
    cache = get_user_cache()
    if not cache:
        return {
            "enabled": False,
            "error": "Cache not initialized",
        }

    return await cache.get_stats()
