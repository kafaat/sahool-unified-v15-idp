"""
Cache Adapter for Task Service - محول التخزين المؤقت لخدمة المهام

This module provides a Redis-based caching layer for astronomical data
with fallback to in-memory cache when Redis is unavailable.
Supports multi-instance deployments through shared Redis cache.
"""

import hashlib
import json
import logging
import os
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ═══════════════════════════════════════════════════════════════════════════
# Configuration - التكوين
# ═══════════════════════════════════════════════════════════════════════════

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
CACHE_PREFIX = "task-service:"
DEFAULT_TTL_SECONDS = 3600  # 1 hour
ASTRONOMICAL_CACHE_TTL = 3600  # 1 hour for astronomical data


# ═══════════════════════════════════════════════════════════════════════════
# Redis Connection - اتصال Redis
# ═══════════════════════════════════════════════════════════════════════════

_redis_client = None
_redis_available = False


async def get_redis_client():
    """
    Get or create Redis client connection
    الحصول على اتصال عميل Redis أو إنشائه
    """
    global _redis_client, _redis_available

    if _redis_client is not None:
        return _redis_client if _redis_available else None

    try:
        import redis.asyncio as redis

        _redis_client = redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        # Test connection
        await _redis_client.ping()
        _redis_available = True
        # Sanitize URL for logging (remove potential newlines)
        safe_url = str(REDIS_URL).replace("\n", "").replace("\r", "")
        logger.info("Redis connected: %s", safe_url)
        return _redis_client

    except ImportError:
        logger.warning("Redis library not installed, using in-memory cache")
        _redis_available = False
        return None

    except Exception as e:
        logger.warning("Redis connection failed: %s, using in-memory cache", type(e).__name__)
        _redis_available = False
        return None


async def close_redis():
    """Close Redis connection"""
    global _redis_client, _redis_available

    if _redis_client is not None:
        try:
            await _redis_client.close()
        except Exception as e:
            logger.warning("Error closing Redis: %s", type(e).__name__)
        finally:
            _redis_client = None
            _redis_available = False


# ═══════════════════════════════════════════════════════════════════════════
# In-Memory Fallback Cache - التخزين المؤقت الاحتياطي في الذاكرة
# ═══════════════════════════════════════════════════════════════════════════


class InMemoryCache:
    """
    Simple in-memory cache with TTL support
    تخزين مؤقت بسيط في الذاكرة مع دعم TTL

    Used as fallback when Redis is unavailable.
    Note: This cache is NOT shared between instances.
    """

    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._max_size = max_size

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]
        if datetime.now(UTC) > expiry:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        """Set value in cache with TTL"""
        # Evict oldest entries if cache is full
        if len(self._cache) >= self._max_size:
            self._evict_expired()
            if len(self._cache) >= self._max_size:
                # Remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

        expiry = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()

    def _evict_expired(self) -> int:
        """Remove expired entries"""
        now = datetime.now(UTC)
        expired = [k for k, (_, exp) in self._cache.items() if now > exp]
        for key in expired:
            del self._cache[key]
        return len(expired)

    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)


# Global in-memory cache instance
_memory_cache = InMemoryCache()


# ═══════════════════════════════════════════════════════════════════════════
# Cache Adapter Interface - واجهة محول التخزين المؤقت
# ═══════════════════════════════════════════════════════════════════════════


class CacheAdapter:
    """
    Unified cache adapter supporting both Redis and in-memory storage
    محول تخزين مؤقت موحد يدعم Redis والتخزين في الذاكرة

    Automatically falls back to in-memory cache when Redis is unavailable.
    """

    def __init__(self, namespace: str = ""):
        """
        Initialize cache adapter

        Args:
            namespace: Optional namespace prefix for cache keys
        """
        self.namespace = namespace
        self._prefix = f"{CACHE_PREFIX}{namespace}:" if namespace else CACHE_PREFIX

    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix"""
        return f"{self._prefix}{key}"

    def _hash_key(self, *args: Any) -> str:
        """Create a hash key from arguments"""
        key_data = json.dumps(args, sort_keys=True, default=str)
        return hashlib.sha256(key_data.encode()).hexdigest()[:12]

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache
        الحصول على قيمة من التخزين المؤقت

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        full_key = self._make_key(key)

        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                value = await redis_client.get(full_key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                logger.warning("Redis get error: %s", type(e).__name__)

        # Fallback to in-memory
        return _memory_cache.get(full_key)

    async def set(self, key: str, value: Any, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> bool:
        """
        Set value in cache
        تعيين قيمة في التخزين المؤقت

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl_seconds: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        full_key = self._make_key(key)

        # Serialize value
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError) as e:
            logger.error("Cache serialization error: %s", type(e).__name__)
            return False

        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                await redis_client.setex(full_key, ttl_seconds, serialized)
                return True
            except Exception as e:
                logger.warning("Redis set error: %s", type(e).__name__)

        # Fallback to in-memory
        _memory_cache.set(full_key, value, ttl_seconds)
        return True

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache
        حذف مفتاح من التخزين المؤقت

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        full_key = self._make_key(key)

        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                result = await redis_client.delete(full_key)
                return result > 0
            except Exception as e:
                logger.warning("Redis delete error: %s", type(e).__name__)

        # Fallback to in-memory
        return _memory_cache.delete(full_key)

    async def get_or_set(
        self,
        key: str,
        factory: Any,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> Any:
        """
        Get from cache or compute and cache the value
        الحصول من التخزين المؤقت أو حساب القيمة وتخزينها

        Args:
            key: Cache key
            factory: Callable or coroutine function to compute value if not cached
            ttl_seconds: Time to live in seconds

        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        if callable(factory):
            import asyncio

            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
        else:
            value = factory

        # Cache the result
        if value is not None:
            await self.set(key, value, ttl_seconds)

        return value

    async def clear_namespace(self) -> int:
        """
        Clear all keys in this namespace
        مسح جميع المفاتيح في هذه المساحة

        Returns:
            Number of keys deleted (approximate for in-memory)
        """
        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                pattern = f"{self._prefix}*"
                keys = []
                async for key in redis_client.scan_iter(match=pattern):
                    keys.append(key)
                if keys:
                    return await redis_client.delete(*keys)
                return 0
            except Exception as e:
                logger.warning("Redis clear error: %s", type(e).__name__)

        # For in-memory, clear all (can't filter by prefix efficiently)
        size = _memory_cache.size()
        _memory_cache.clear()
        return size


# ═══════════════════════════════════════════════════════════════════════════
# Astronomical Data Cache - التخزين المؤقت للبيانات الفلكية
# ═══════════════════════════════════════════════════════════════════════════


class AstronomicalCache:
    """
    Specialized cache for astronomical calendar data
    تخزين مؤقت متخصص لبيانات التقويم الفلكي

    Provides caching for:
    - Best days for activities
    - Daily astronomical data
    - Activity-specific recommendations
    """

    def __init__(self):
        self._cache = CacheAdapter(namespace="astronomical")

    async def get_best_days(self, activity: str, days: int) -> dict | None:
        """
        Get cached best days for an activity
        الحصول على أفضل الأيام المخزنة مؤقتاً لنشاط ما
        """
        key = f"best_days:{activity}:{days}"
        return await self._cache.get(key)

    async def set_best_days(self, activity: str, days: int, data: dict) -> bool:
        """
        Cache best days for an activity
        تخزين أفضل الأيام لنشاط ما
        """
        key = f"best_days:{activity}:{days}"
        return await self._cache.set(key, data, ASTRONOMICAL_CACHE_TTL)

    async def get_daily_data(self, date_str: str) -> dict | None:
        """
        Get cached daily astronomical data
        الحصول على البيانات الفلكية اليومية المخزنة مؤقتاً
        """
        key = f"daily:{date_str}"
        return await self._cache.get(key)

    async def set_daily_data(self, date_str: str, data: dict) -> bool:
        """
        Cache daily astronomical data
        تخزين البيانات الفلكية اليومية
        """
        key = f"daily:{date_str}"
        return await self._cache.set(key, data, ASTRONOMICAL_CACHE_TTL)

    async def get_date_validation(self, date_str: str, activity: str) -> dict | None:
        """
        Get cached date validation result
        الحصول على نتيجة التحقق من التاريخ المخزنة مؤقتاً
        """
        key = f"validation:{date_str}:{activity}"
        return await self._cache.get(key)

    async def set_date_validation(self, date_str: str, activity: str, data: dict) -> bool:
        """
        Cache date validation result
        تخزين نتيجة التحقق من التاريخ
        """
        key = f"validation:{date_str}:{activity}"
        return await self._cache.set(key, data, ASTRONOMICAL_CACHE_TTL)

    async def clear(self) -> int:
        """Clear all astronomical cache data"""
        return await self._cache.clear_namespace()


# Global astronomical cache instance
astronomical_cache = AstronomicalCache()


# ═══════════════════════════════════════════════════════════════════════════
# Task Cache - التخزين المؤقت للمهام
# ═══════════════════════════════════════════════════════════════════════════


class TaskCache:
    """
    Cache for task-related data
    تخزين مؤقت للبيانات المتعلقة بالمهام

    Provides caching for:
    - Task statistics
    - Field health data
    - Task suggestions
    """

    def __init__(self):
        self._cache = CacheAdapter(namespace="tasks")

    async def get_stats(self, tenant_id: str) -> dict | None:
        """Get cached task statistics for tenant"""
        key = f"stats:{tenant_id}"
        return await self._cache.get(key)

    async def set_stats(self, tenant_id: str, stats: dict, ttl_seconds: int = 300) -> bool:
        """Cache task statistics (5 min default TTL)"""
        key = f"stats:{tenant_id}"
        return await self._cache.set(key, stats, ttl_seconds)

    async def invalidate_stats(self, tenant_id: str) -> bool:
        """Invalidate cached statistics when tasks change"""
        key = f"stats:{tenant_id}"
        return await self._cache.delete(key)

    async def get_field_health(self, field_id: str) -> dict | None:
        """Get cached field health data"""
        key = f"health:{field_id}"
        return await self._cache.get(key)

    async def set_field_health(self, field_id: str, health_data: dict, ttl_seconds: int = 600) -> bool:
        """Cache field health data (10 min default TTL)"""
        key = f"health:{field_id}"
        return await self._cache.set(key, health_data, ttl_seconds)

    async def get_suggestions(self, field_id: str) -> list | None:
        """Get cached task suggestions for field"""
        key = f"suggestions:{field_id}"
        return await self._cache.get(key)

    async def set_suggestions(self, field_id: str, suggestions: list, ttl_seconds: int = 1800) -> bool:
        """Cache task suggestions (30 min default TTL)"""
        key = f"suggestions:{field_id}"
        return await self._cache.set(key, suggestions, ttl_seconds)

    async def clear(self) -> int:
        """Clear all task cache data"""
        return await self._cache.clear_namespace()


# Global task cache instance
task_cache = TaskCache()
