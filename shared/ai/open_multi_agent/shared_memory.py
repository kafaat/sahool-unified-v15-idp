"""
Shared Memory
=============
الذاكرة المشتركة

Redis-backed shared memory for OpenMultiAgent framework.
Extends CollectiveMemory with persistent Redis storage and agent-scoped contexts.

Features:
- Redis-backed persistence with graceful in-memory fallback
- Namespace-based organization (AGENT, TASK, RESULT, PATTERN, CONVERSATION, SHARED)
- Agent context retrieval and inter-agent memory sharing
- TTL-based expiration via Redis or in-memory cleanup
- Async-first API with structlog instrumentation

المميزات:
- تخزين مستمر مدعوم بـ Redis مع تراجع سلس للذاكرة الداخلية
- تنظيم على أساس مساحات الأسماء
- استرجاع سياق الوكيل ومشاركة الذاكرة بين الوكلاء
- انتهاء الصلاحية على أساس TTL عبر Redis أو التنظيف الداخلي
- واجهة برمجة غير متزامنة مع أدوات structlog

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import uuid4

import structlog

from shared.ai.orchestration.memory import CollectiveMemory, text_similarity
from shared.ai.orchestration.models import (
    MemoryEntry,
    MemoryNamespace,
    PatternMatch,
)

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Shared Memory Namespaces
# ─────────────────────────────────────────────────────────────────────────────


class SharedMemoryNamespace(StrEnum):
    """
    Extended memory namespaces for OpenMultiAgent.
    مساحات أسماء الذاكرة الموسعة لـ OpenMultiAgent
    """

    AGENT = "agent"  # Per-agent state and context | حالة وسياق كل وكيل
    TASK = "task"  # Task assignments and progress | تعيينات المهام والتقدم
    RESULT = "result"  # Task execution results | نتائج تنفيذ المهام
    PATTERN = "pattern"  # Learned patterns and heuristics | الأنماط المتعلمة
    CONVERSATION = "conversation"  # Conversation history | تاريخ المحادثة
    SHARED = "shared"  # Cross-agent shared data | بيانات مشتركة بين الوكلاء


# Map SharedMemoryNamespace to orchestration MemoryNamespace where possible
_NAMESPACE_MAP: dict[str, MemoryNamespace] = {
    SharedMemoryNamespace.AGENT: MemoryNamespace.AGENTS,
    SharedMemoryNamespace.TASK: MemoryNamespace.TASKS,
    SharedMemoryNamespace.RESULT: MemoryNamespace.DECISIONS,
    SharedMemoryNamespace.PATTERN: MemoryNamespace.PATTERNS,
    SharedMemoryNamespace.CONVERSATION: MemoryNamespace.KNOWLEDGE,
    SharedMemoryNamespace.SHARED: MemoryNamespace.KNOWLEDGE,
}

# Redis key prefix for all shared memory entries
_REDIS_PREFIX = "sahool:oma:memory"


# ─────────────────────────────────────────────────────────────────────────────
# Shared Memory
# ─────────────────────────────────────────────────────────────────────────────


class SharedMemory:
    """
    Redis-backed shared memory for OpenMultiAgent.
    الذاكرة المشتركة المدعومة بـ Redis لـ OpenMultiAgent

    Wraps CollectiveMemory for in-memory operations and adds optional
    Redis persistence. Falls back gracefully to in-memory-only mode
    when Redis is unavailable.

    يغلف CollectiveMemory للعمليات الداخلية ويضيف تخزين Redis اختياري.
    يتراجع بسلاسة إلى وضع الذاكرة الداخلية فقط عند عدم توفر Redis.

    Example:
        >>> memory = SharedMemory()
        >>> await memory.connect()
        >>> await memory.store("wheat_pattern", {"type": "disease"}, "pattern")
        >>> result = await memory.retrieve("wheat_pattern", "pattern")
        >>> await memory.close()
    """

    def __init__(
        self,
        tenant_id: str = "sahool",
        max_size: int = 10000,
        default_ttl_seconds: int = 3600,
        redis_url: str | None = None,
    ) -> None:
        """
        Initialize shared memory.
        تهيئة الذاكرة المشتركة

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
            max_size: الحجم الأقصى - Maximum in-memory entries
            default_ttl_seconds: مدة الصلاحية الافتراضية - Default TTL in seconds
            redis_url: رابط Redis - Redis connection URL (or REDIS_URL env var)
        """
        self.tenant_id = tenant_id
        self.default_ttl_seconds = default_ttl_seconds
        self._redis_url = redis_url or os.getenv("REDIS_URL", "")
        self._redis: Any = None  # redis.asyncio.Redis instance
        self._redis_available = False

        # In-memory backing store via CollectiveMemory
        self._memory = CollectiveMemory(
            max_size=max_size,
            default_ttl_hours=max(1, default_ttl_seconds // 3600),
            tenant_id=tenant_id,
        )

        logger.info(
            "shared_memory_initialized",
            tenant_id=tenant_id,
            max_size=max_size,
            redis_configured=bool(self._redis_url),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Connection Lifecycle
    # ─────────────────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """
        Connect to Redis backend if configured.
        الاتصال بخلفية Redis إذا تم التكوين

        Falls back to in-memory mode if Redis is unreachable.
        """
        if not self._redis_url:
            logger.info("shared_memory_redis_skipped", reason="no_redis_url")
            return

        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            await self._redis.ping()
            self._redis_available = True
            logger.info("shared_memory_redis_connected", url=self._redis_url.split("@")[-1])
        except Exception as e:
            self._redis_available = False
            self._redis = None
            logger.warning(
                "shared_memory_redis_fallback",
                error=str(e),
                mode="in_memory",
            )

    async def close(self) -> None:
        """Close Redis connection if open. | إغلاق اتصال Redis"""
        if self._redis is not None:
            try:
                await self._redis.aclose()
            except Exception:
                pass
            self._redis = None
            self._redis_available = False
            logger.info("shared_memory_redis_closed")

    # ─────────────────────────────────────────────────────────────────────────
    # Core Operations
    # ─────────────────────────────────────────────────────────────────────────

    async def store(
        self,
        key: str,
        value: Any,
        namespace: str,
        ttl_seconds: int = 3600,
    ) -> MemoryEntry:
        """
        Store a value in shared memory.
        تخزين قيمة في الذاكرة المشتركة

        Args:
            key: المفتاح - Storage key
            value: القيمة - Value to store (must be JSON-serializable)
            namespace: مساحة الاسم - Namespace string (maps to SharedMemoryNamespace)
            ttl_seconds: مدة الصلاحية - Time-to-live in seconds

        Returns:
            MemoryEntry: The stored memory entry
        """
        mem_ns = _NAMESPACE_MAP.get(namespace, MemoryNamespace.KNOWLEDGE)
        ttl_hours = max(1, ttl_seconds // 3600)

        # Store in CollectiveMemory (in-memory)
        entry = self._memory.store(
            namespace=mem_ns,
            key=self._scoped_key(key, namespace),
            value=value,
            metadata={"namespace": namespace, "original_key": key},
            ttl_hours=ttl_hours,
        )

        # Persist to Redis if available
        if self._redis_available and self._redis is not None:
            try:
                redis_key = self._redis_key(key, namespace)
                payload = json.dumps(
                    {
                        "entry_id": entry.entry_id,
                        "key": key,
                        "namespace": namespace,
                        "value": value,
                        "tenant_id": self.tenant_id,
                        "created_at": entry.created_at.isoformat(),
                    },
                    default=str,
                )
                await self._redis.set(redis_key, payload, ex=ttl_seconds)
            except Exception as e:
                logger.warning("shared_memory_redis_store_failed", key=key, error=str(e))

        logger.debug("shared_memory_stored", key=key, namespace=namespace)
        return entry

    async def retrieve(self, key: str, namespace: str) -> Any | None:
        """
        Retrieve a value from shared memory.
        استرجاع قيمة من الذاكرة المشتركة

        Checks in-memory first, then falls back to Redis.

        Args:
            key: المفتاح - Storage key
            namespace: مساحة الاسم - Namespace string

        Returns:
            The stored value, or None if not found
        """
        mem_ns = _NAMESPACE_MAP.get(namespace, MemoryNamespace.KNOWLEDGE)
        scoped = self._scoped_key(key, namespace)

        # Try in-memory first
        entry = self._memory.retrieve(mem_ns, scoped)
        if entry is not None:
            return entry.value

        # Try Redis if available
        if self._redis_available and self._redis is not None:
            try:
                redis_key = self._redis_key(key, namespace)
                raw = await self._redis.get(redis_key)
                if raw is not None:
                    data = json.loads(raw)
                    # Backfill into in-memory cache
                    self._memory.store(
                        namespace=mem_ns,
                        key=scoped,
                        value=data["value"],
                        metadata={"namespace": namespace, "original_key": key},
                    )
                    return data["value"]
            except Exception as e:
                logger.warning("shared_memory_redis_retrieve_failed", key=key, error=str(e))

        return None

    async def search(
        self,
        query: str,
        namespace: str,
        top_k: int = 5,
    ) -> list[MemoryEntry]:
        """
        Search memory entries by text similarity.
        البحث في إدخالات الذاكرة بتشابه النص

        Args:
            query: الاستعلام - Search query text
            namespace: مساحة الاسم - Namespace to search within
            top_k: أعلى k - Maximum results to return

        Returns:
            list[MemoryEntry]: Matching entries sorted by relevance
        """
        mem_ns = _NAMESPACE_MAP.get(namespace, MemoryNamespace.KNOWLEDGE)

        matches: list[PatternMatch] = self._memory.find_similar(
            query=query,
            namespace=mem_ns,
            top_k=top_k,
            min_similarity=0.1,
        )

        # Filter to entries that belong to the requested namespace
        results: list[MemoryEntry] = []
        for match in matches:
            entry_ns = match.entry.metadata.get("namespace", "")
            if entry_ns == namespace or not entry_ns:
                results.append(match.entry)

        logger.debug(
            "shared_memory_search",
            query_length=len(query),
            namespace=namespace,
            results=len(results),
        )
        return results

    async def clear(self, namespace: str) -> int:
        """
        Clear all entries in a namespace.
        مسح جميع الإدخالات في مساحة الاسم

        Args:
            namespace: مساحة الاسم - Namespace to clear

        Returns:
            int: Number of entries cleared
        """
        mem_ns = _NAMESPACE_MAP.get(namespace, MemoryNamespace.KNOWLEDGE)
        count = self._memory.clear_namespace(mem_ns)

        # Clear Redis keys for namespace
        if self._redis_available and self._redis is not None:
            try:
                pattern = f"{_REDIS_PREFIX}:{self.tenant_id}:{namespace}:*"
                cursor = 0
                while True:
                    cursor, keys = await self._redis.scan(cursor=cursor, match=pattern, count=100)
                    if keys:
                        await self._redis.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.warning("shared_memory_redis_clear_failed", namespace=namespace, error=str(e))

        logger.info("shared_memory_cleared", namespace=namespace, entries_cleared=count)
        return count

    # ─────────────────────────────────────────────────────────────────────────
    # Agent Context Operations
    # ─────────────────────────────────────────────────────────────────────────

    async def get_agent_context(self, agent_id: str) -> dict:
        """
        Get all memory entries associated with a specific agent.
        الحصول على جميع إدخالات الذاكرة المرتبطة بوكيل محدد

        Collects entries from the AGENT namespace keyed by agent_id,
        plus any entries in other namespaces that reference the agent.

        Args:
            agent_id: معرف الوكيل - Agent identifier

        Returns:
            dict: Agent context with tasks, results, patterns, and shared data
        """
        context: dict[str, Any] = {
            "agent_id": agent_id,
            "state": None,
            "tasks": [],
            "results": [],
            "patterns": [],
            "shared": [],
        }

        # Agent state from AGENT namespace
        state = await self.retrieve(agent_id, SharedMemoryNamespace.AGENT)
        if state is not None:
            context["state"] = state

        # Collect from other namespaces via in-memory query
        all_entries = self._memory.query(
            filter_fn=lambda e: (
                e.metadata.get("agent_id") == agent_id
                or e.key.startswith(f"{SharedMemoryNamespace.AGENT}:{agent_id}")
                or agent_id in str(e.value)
            ),
            limit=100,
        )

        for entry in all_entries:
            entry_ns = entry.metadata.get("namespace", "")
            if entry_ns == SharedMemoryNamespace.TASK:
                context["tasks"].append({"key": entry.metadata.get("original_key", entry.key), "value": entry.value})
            elif entry_ns == SharedMemoryNamespace.RESULT:
                context["results"].append({"key": entry.metadata.get("original_key", entry.key), "value": entry.value})
            elif entry_ns == SharedMemoryNamespace.PATTERN:
                context["patterns"].append(
                    {"key": entry.metadata.get("original_key", entry.key), "value": entry.value}
                )
            elif entry_ns == SharedMemoryNamespace.SHARED:
                context["shared"].append({"key": entry.metadata.get("original_key", entry.key), "value": entry.value})

        logger.debug(
            "shared_memory_agent_context",
            agent_id=agent_id,
            tasks=len(context["tasks"]),
            results=len(context["results"]),
        )
        return context

    async def share_between(
        self,
        from_agent: str,
        to_agent: str,
        keys: list[str],
    ) -> int:
        """
        Share memory entries from one agent to another.
        مشاركة إدخالات الذاكرة من وكيل إلى آخر

        Copies entries from the source agent's scope into a shared namespace
        accessible by the target agent.

        Args:
            from_agent: من الوكيل - Source agent ID
            to_agent: إلى الوكيل - Target agent ID
            keys: المفاتيح - Keys to share

        Returns:
            int: Number of entries successfully shared
        """
        shared_count = 0

        for key in keys:
            # Try to find the value in any namespace
            value = None
            for ns in SharedMemoryNamespace:
                value = await self.retrieve(key, ns.value)
                if value is not None:
                    break

            if value is None:
                # Try with agent-scoped key
                value = await self.retrieve(f"{from_agent}:{key}", SharedMemoryNamespace.AGENT)

            if value is not None:
                shared_key = f"shared:{from_agent}:{to_agent}:{key}"
                await self.store(
                    key=shared_key,
                    value=value,
                    namespace=SharedMemoryNamespace.SHARED,
                    ttl_seconds=self.default_ttl_seconds,
                )
                shared_count += 1
                logger.debug(
                    "shared_memory_shared",
                    from_agent=from_agent,
                    to_agent=to_agent,
                    key=key,
                )
            else:
                logger.debug(
                    "shared_memory_share_key_not_found",
                    from_agent=from_agent,
                    key=key,
                )

        logger.info(
            "shared_memory_share_completed",
            from_agent=from_agent,
            to_agent=to_agent,
            requested=len(keys),
            shared=shared_count,
        )
        return shared_count

    # ─────────────────────────────────────────────────────────────────────────
    # Utility
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def is_redis_available(self) -> bool:
        """Check if Redis backend is connected. | التحقق من اتصال Redis"""
        return self._redis_available

    def get_stats(self) -> dict[str, Any]:
        """
        Get memory statistics.
        الحصول على إحصائيات الذاكرة

        Returns:
            dict: Statistics including in-memory and Redis status
        """
        mem_stats = self._memory.get_stats()
        return {
            "total_entries": mem_stats.total_entries,
            "by_namespace": mem_stats.by_namespace,
            "cache_hits": mem_stats.cache_hits,
            "cache_misses": mem_stats.cache_misses,
            "redis_available": self._redis_available,
            "tenant_id": self.tenant_id,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Private Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _scoped_key(self, key: str, namespace: str) -> str:
        """Create a namespace-scoped key for CollectiveMemory."""
        return f"{namespace}:{key}"

    def _redis_key(self, key: str, namespace: str) -> str:
        """Create a Redis key with prefix, tenant, and namespace."""
        return f"{_REDIS_PREFIX}:{self.tenant_id}:{namespace}:{key}"
