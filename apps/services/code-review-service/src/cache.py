"""
Review Cache Module
وحدة التخزين المؤقت للمراجعات

Supports multiple backends: memory, redis, file
يدعم عدة واجهات: الذاكرة، Redis، الملفات
"""

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_cache_key(code: str, language: str | None = None, model: str | None = None) -> str:
    """Generate a unique cache key for the code content"""
    content = f"{code}:{language or ''}:{model or ''}"
    return hashlib.sha256(content.encode()).hexdigest()[:32]


class CacheBackend(ABC):
    """Abstract base class for cache backends"""

    @abstractmethod
    async def get(self, key: str) -> dict | None:
        """Get a cached review"""
        pass

    @abstractmethod
    async def set(self, key: str, value: dict, ttl: int = 3600) -> bool:
        """Store a review in cache"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a cached review"""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cached reviews"""
        pass

    @abstractmethod
    async def stats(self) -> dict:
        """Get cache statistics"""
        pass


class MemoryCache(CacheBackend):
    """In-memory LRU cache with TTL support"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[dict, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> dict | None:
        """Get a cached review with TTL check"""
        if key not in self._cache:
            self._misses += 1
            return None

        value, expiry = self._cache[key]

        # Check if expired
        if time.time() > expiry:
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (LRU)
        self._cache.move_to_end(key)
        self._hits += 1
        return value

    async def set(self, key: str, value: dict, ttl: int = None) -> bool:
        """Store a review with TTL"""
        try:
            ttl = ttl or self.default_ttl
            expiry = time.time() + ttl

            # Remove oldest if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            self._cache[key] = (value, expiry)
            self._cache.move_to_end(key)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a cached entry"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def clear(self) -> bool:
        """Clear all cached entries"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        return True

    async def stats(self) -> dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "backend": "memory",
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
        }


class RedisCache(CacheBackend):
    """Redis-based cache backend"""

    def __init__(self, redis_url: str, prefix: str = "code_review:", default_ttl: int = 3600):
        self.redis_url = redis_url
        self.prefix = prefix
        self.default_ttl = default_ttl
        self._client = None
        self._hits = 0
        self._misses = 0

    async def _get_client(self):
        """Lazy initialization of Redis client"""
        if self._client is None:
            try:
                import redis.asyncio as redis

                self._client = redis.from_url(self.redis_url, decode_responses=True)
            except ImportError:
                logger.error("redis package not installed. Install with: pip install redis")
                raise
        return self._client

    def _make_key(self, key: str) -> str:
        """Create prefixed key"""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> dict | None:
        """Get a cached review from Redis"""
        try:
            client = await self._get_client()
            data = await client.get(self._make_key(key))
            if data:
                self._hits += 1
                return json.loads(data)
            self._misses += 1
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self._misses += 1
            return None

    async def set(self, key: str, value: dict, ttl: int = None) -> bool:
        """Store a review in Redis"""
        try:
            client = await self._get_client()
            ttl = ttl or self.default_ttl
            await client.setex(self._make_key(key), ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a cached entry from Redis"""
        try:
            client = await self._get_client()
            result = await client.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cached entries with prefix"""
        try:
            client = await self._get_client()
            cursor = 0
            while True:
                cursor, keys = await client.scan(cursor, match=f"{self.prefix}*", count=100)
                if keys:
                    await client.delete(*keys)
                if cursor == 0:
                    break
            self._hits = 0
            self._misses = 0
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

    async def stats(self) -> dict:
        """Get cache statistics"""
        try:
            client = await self._get_client()
            info = await client.info("keyspace")
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                "backend": "redis",
                "url": self.redis_url,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
                "redis_info": info,
            }
        except Exception as e:
            return {"backend": "redis", "error": str(e)}


class FileCache(CacheBackend):
    """File-based cache backend"""

    def __init__(self, cache_path: str, default_ttl: int = 3600):
        self.cache_path = Path(cache_path)
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_path.exists():
            self._save_cache({})

    def _load_cache(self) -> dict:
        """Load cache from file"""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Cache load error: {e}")
        return {}

    def _save_cache(self, data: dict) -> bool:
        """Save cache to file"""
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Cache save error: {e}")
            return False

    async def get(self, key: str) -> dict | None:
        """Get a cached review from file"""
        cache = self._load_cache()
        if key not in cache:
            self._misses += 1
            return None

        entry = cache[key]
        if time.time() > entry.get("expiry", 0):
            # Expired, remove it
            del cache[key]
            self._save_cache(cache)
            self._misses += 1
            return None

        self._hits += 1
        return entry.get("value")

    async def set(self, key: str, value: dict, ttl: int = None) -> bool:
        """Store a review in file cache"""
        try:
            ttl = ttl or self.default_ttl
            cache = self._load_cache()
            cache[key] = {"value": value, "expiry": time.time() + ttl, "created": time.time()}
            return self._save_cache(cache)
        except Exception as e:
            logger.error(f"File cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a cached entry from file"""
        cache = self._load_cache()
        if key in cache:
            del cache[key]
            return self._save_cache(cache)
        return False

    async def clear(self) -> bool:
        """Clear all cached entries"""
        self._hits = 0
        self._misses = 0
        return self._save_cache({})

    async def stats(self) -> dict:
        """Get cache statistics"""
        cache = self._load_cache()
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "backend": "file",
            "path": str(self.cache_path),
            "size": len(cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
        }


def create_cache_backend(
    backend: str = "memory",
    redis_url: str = None,
    cache_path: str = None,
    max_size: int = 1000,
    default_ttl: int = 3600,
) -> CacheBackend:
    """Factory function to create the appropriate cache backend"""
    if backend == "redis":
        if not redis_url:
            raise ValueError("redis_url required for redis backend")
        return RedisCache(redis_url, default_ttl=default_ttl)
    elif backend == "file":
        if not cache_path:
            cache_path = "/app/cache/reviews.json"
        return FileCache(cache_path, default_ttl=default_ttl)
    else:
        return MemoryCache(max_size=max_size, default_ttl=default_ttl)
