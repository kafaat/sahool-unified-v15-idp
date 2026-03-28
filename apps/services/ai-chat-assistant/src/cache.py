"""
Cache manager for AI responses using Redis.
مدير التخزين المؤقت للاستجابات الذكية باستخدام Redis.
"""

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from src.config import settings
from src.models import CachedResponse, ResponseMetadata

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of AI responses in Redis."""

    def __init__(self):
        self.redis_client: Redis | None = None
        self.namespace = "ai-chat"

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

    def _generate_cache_key(
        self, query: str, language: str, field_id: str | None = None, tenant_id: str | None = None
    ) -> str:
        """Generate cache key from query parameters, scoped by tenant_id."""
        # Normalize query (lowercase, strip)
        normalized_query = query.lower().strip()

        # Create hash input - tenant_id first for proper isolation
        hash_input = f"{tenant_id or 'global'}:{normalized_query}:{language}"
        if field_id:
            hash_input += f":{field_id}"

        # Generate hash
        cache_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

        # Include tenant_id in key prefix for easy per-tenant invalidation
        tenant_prefix = f"t:{tenant_id}" if tenant_id else "t:global"
        return f"{self.namespace}:{tenant_prefix}:exact:{cache_hash}"

    async def get(
        self, query: str, language: str, field_id: str | None = None, tenant_id: str | None = None
    ) -> CachedResponse | None:
        """
        Get cached response if exists.

        Args:
            query: User query
            language: Query language
            field_id: Optional field ID for context
            tenant_id: Optional tenant ID for isolation

        Returns:
            CachedResponse if found, None otherwise
        """
        if not settings.CACHE_ENABLED or not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(query, language, field_id, tenant_id)

            # Get from Redis
            cached_data = await self.redis_client.get(cache_key)

            if not cached_data:
                logger.debug(f"Cache miss for query: {query[:50]}...")
                return None

            # Parse cached response
            cached_dict = json.loads(cached_data)
            cached_response = CachedResponse(**cached_dict)

            # Increment hit count
            cached_response.hit_count += 1
            await self._update_hit_count(cache_key, cached_response)

            logger.info(f"Cache hit for query: {query[:50]}... (hits: {cached_response.hit_count})")
            return cached_response

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    async def set(
        self,
        query: str,
        language: str,
        answer: str,
        answer_en: str | None,
        metadata: ResponseMetadata,
        field_id: str | None = None,
        tenant_id: str | None = None,
    ) -> bool:
        """
        Cache AI response.

        Args:
            query: User query
            language: Query language
            answer: AI answer
            answer_en: English translation (if applicable)
            metadata: Response metadata
            field_id: Optional field ID
            tenant_id: Optional tenant ID for isolation

        Returns:
            True if cached successfully, False otherwise
        """
        if not settings.CACHE_ENABLED or not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(query, language, field_id, tenant_id)

            # Create cached response
            cached_response = CachedResponse(
                query=query,
                answer=answer,
                answer_en=answer_en,
                metadata=metadata,
                cached_at=datetime.now(UTC),
                hit_count=0,
            )

            # Serialize to JSON
            cached_data = cached_response.model_dump_json()

            # Store in Redis with TTL
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_SECONDS,
                cached_data,
            )

            logger.info(f"Cached response for query: {query[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def _update_hit_count(self, cache_key: str, cached_response: CachedResponse):
        """Update hit count for cached response."""
        try:
            cached_data = cached_response.model_dump_json()
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_SECONDS,
                cached_data,
            )
        except Exception as e:
            logger.error(f"Error updating hit count: {e}")

    async def invalidate(self, query: str, language: str, field_id: str | None = None, tenant_id: str | None = None):
        """Invalidate cache for a specific query."""
        try:
            cache_key = self._generate_cache_key(query, language, field_id, tenant_id)
            await self.redis_client.delete(cache_key)
            logger.info(f"Invalidated cache for query: {query[:50]}...")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    async def get_stats(self) -> dict:
        """Get cache statistics using SCAN (safe for production)."""
        try:
            if not self.redis_client:
                return {}

            pattern = f"{self.namespace}:*"
            total_entries = 0
            total_hits = 0
            cursor = 0

            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                total_entries += len(keys)
                if keys:
                    # Use pipeline to batch GET requests
                    pipe = self.redis_client.pipeline()
                    for key in keys:
                        pipe.get(key)
                    results = await pipe.execute()
                    for data in results:
                        if data:
                            cached = json.loads(data)
                            total_hits += cached.get("hit_count", 0)
                if cursor == 0:
                    break

            return {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "avg_hits_per_entry": total_hits / total_entries if total_entries > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# Global cache manager instance
cache_manager = CacheManager()
