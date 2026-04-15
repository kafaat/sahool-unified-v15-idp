"""
Collective Memory
=================
الذاكرة الجماعية

Shared memory system for multi-agent knowledge sharing.
Provides LRU caching, pattern matching, and similarity search.

Inspired by Claude-Flow architecture for distributed memory.

Features:
- LRU cache for performance
- Namespace-based organization
- Pattern matching for similar tasks
- Vector similarity search (optional)
- TTL-based expiration

المميزات:
- ذاكرة التخزين المؤقت LRU للأداء
- تنظيم على أساس مساحات الأسماء
- مطابقة الأنماط للمهام المماثلة
- البحث بالتشابه المتجه (اختياري)
- انتهاء الصلاحية على أساس TTL

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import re
import time
from collections import OrderedDict
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from threading import RLock
from typing import Any, TypeVar
from uuid import uuid4

import structlog

from .models import (
    MemoryEntry,
    MemoryNamespace,
    MemoryStats,
    PatternMatch,
)

logger = structlog.get_logger()

T = TypeVar("T")


# ─────────────────────────────────────────────────────────────────────────────
# LRU Cache Implementation
# ─────────────────────────────────────────────────────────────────────────────


class LRUCache(OrderedDict[str, MemoryEntry]):
    """
    Thread-safe LRU (Least Recently Used) cache.
    ذاكرة التخزين المؤقت LRU آمنة الخيوط

    Automatically evicts least recently used entries when capacity is reached.
    يقوم تلقائياً بطرد الإدخالات الأقل استخداماً عند الوصول للسعة.
    """

    def __init__(self, maxsize: int = 1000):
        """
        Initialize LRU cache.
        تهيئة ذاكرة التخزين المؤقت LRU

        Args:
            maxsize: الحجم الأقصى - Maximum number of entries
        """
        super().__init__()
        self.maxsize = maxsize
        self._lock = RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str, default: MemoryEntry | None = None) -> MemoryEntry | None:
        """Get item and move to end (most recently used)."""
        with self._lock:
            if key not in self:
                self._misses += 1
                return default
            self._hits += 1
            self.move_to_end(key)
            entry = super().__getitem__(key)
            entry.access_count += 1
            entry.last_accessed = datetime.now(UTC)
            return entry

    def set(self, key: str, value: MemoryEntry) -> None:
        """Set item and enforce size limit."""
        with self._lock:
            if key in self:
                self.move_to_end(key)
            super().__setitem__(key, value)
            while len(self) > self.maxsize:
                oldest = next(iter(self))
                del self[oldest]

    def delete(self, key: str) -> bool:
        """Delete item if exists."""
        with self._lock:
            if key in self:
                del self[key]
                return True
            return False

    def clear_all(self) -> None:
        """Clear all entries."""
        with self._lock:
            super().clear()

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate | حساب معدل الإصابة"""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics | الحصول على إحصائيات الذاكرة المؤقتة"""
        with self._lock:
            return {
                "size": len(self),
                "maxsize": self.maxsize,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self.hit_rate,
            }


# ─────────────────────────────────────────────────────────────────────────────
# Similarity Utilities
# ─────────────────────────────────────────────────────────────────────────────


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    حساب تشابه جيب التمام بين متجهين

    Args:
        vec1: المتجه الأول - First vector
        vec2: المتجه الثاني - Second vector

    Returns:
        float: Similarity score between -1 and 1
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Calculate Jaccard similarity between two sets.
    حساب تشابه جاكارد بين مجموعتين

    Args:
        set1: المجموعة الأولى - First set
        set2: المجموعة الثانية - Second set

    Returns:
        float: Similarity score between 0 and 1
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def text_similarity(text1: str, text2: str) -> float:
    """
    Calculate text similarity using word overlap.
    حساب تشابه النص باستخدام تداخل الكلمات

    Simple bag-of-words approach for fast matching.

    Args:
        text1: النص الأول - First text
        text2: النص الثاني - Second text

    Returns:
        float: Similarity score between 0 and 1
    """
    # Tokenize and normalize
    words1 = set(re.findall(r"\w+", text1.lower()))
    words2 = set(re.findall(r"\w+", text2.lower()))

    return jaccard_similarity(words1, words2)


# ─────────────────────────────────────────────────────────────────────────────
# Collective Memory
# ─────────────────────────────────────────────────────────────────────────────


class CollectiveMemory:
    """
    Shared memory system for multi-agent knowledge.
    نظام الذاكرة المشتركة لمعرفة الوكلاء المتعددين

    Provides a centralized memory store that agents can use to:
    - Store and retrieve knowledge
    - Find similar past tasks
    - Share learned patterns
    - Cache frequently accessed data

    يوفر مخزن ذاكرة مركزي يمكن للوكلاء استخدامه لـ:
    - تخزين واسترجاع المعرفة
    - العثور على المهام السابقة المماثلة
    - مشاركة الأنماط المتعلمة
    - تخزين البيانات المتكررة الوصول

    Example:
        >>> memory = CollectiveMemory()
        >>> memory.store(
        ...     namespace=MemoryNamespace.PATTERNS,
        ...     key="wheat_disease_pattern",
        ...     value={"pattern": "yellow_tips", "cause": "nitrogen_deficiency"},
        ... )
        >>> entry = memory.retrieve(MemoryNamespace.PATTERNS, "wheat_disease_pattern")
        >>> matches = memory.find_similar("wheat leaves turning yellow", top_k=5)
    """

    def __init__(
        self,
        max_size: int = 10000,
        default_ttl_hours: int = 24,
        enable_embeddings: bool = False,
        embedding_function: Callable[[str], list[float]] | None = None,
        tenant_id: str = "sahool",
    ):
        """
        Initialize collective memory.
        تهيئة الذاكرة الجماعية

        Args:
            max_size: الحجم الأقصى - Maximum entries in memory
            default_ttl_hours: مدة الصلاحية الافتراضية - Default time-to-live
            enable_embeddings: تفعيل التضمينات - Enable vector embeddings
            embedding_function: دالة التضمين - Function to generate embeddings
            tenant_id: معرف المستأجر - Tenant identifier
        """
        self.max_size = max_size
        self.default_ttl_hours = default_ttl_hours
        self.enable_embeddings = enable_embeddings
        self.embedding_function = embedding_function
        self.tenant_id = tenant_id

        # Main storage with LRU caching
        self._cache = LRUCache(maxsize=max_size)

        # Secondary index by namespace
        self._namespace_index: dict[MemoryNamespace, set[str]] = {ns: set() for ns in MemoryNamespace}

        # Pattern index for fast lookup
        self._pattern_index: dict[str, list[str]] = {}  # keyword -> entry_ids

        # Statistics
        self._stats = MemoryStats()
        self._last_cleanup = datetime.now(UTC)

        # Lock for thread safety
        self._lock = RLock()

        logger.info(
            "collective_memory_initialized",
            max_size=max_size,
            enable_embeddings=enable_embeddings,
            tenant_id=tenant_id,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Core Operations
    # ─────────────────────────────────────────────────────────────────────────

    def store(
        self,
        namespace: MemoryNamespace,
        key: str,
        value: Any,
        metadata: dict[str, Any] | None = None,
        ttl_hours: int | None = None,
        generate_embedding: bool = True,
    ) -> MemoryEntry:
        """
        Store a value in collective memory.
        تخزين قيمة في الذاكرة الجماعية

        Args:
            namespace: مساحة الاسم - Memory namespace
            key: المفتاح - Unique key for retrieval
            value: القيمة - Value to store
            metadata: البيانات الوصفية - Optional metadata
            ttl_hours: مدة الصلاحية - Override default TTL
            generate_embedding: إنشاء تضمين - Generate embedding for value

        Returns:
            MemoryEntry: الإدخال المُخزن - The stored entry
        """
        with self._lock:
            ttl = ttl_hours if ttl_hours is not None else self.default_ttl_hours

            # Create entry
            entry = MemoryEntry(
                entry_id=str(uuid4()),
                namespace=namespace,
                key=key,
                value=value,
                metadata=metadata or {},
                tenant_id=self.tenant_id,
                expires_at=(datetime.now(UTC) + timedelta(hours=ttl) if ttl > 0 else None),
            )

            # Generate embedding if enabled
            if self.enable_embeddings and generate_embedding and self.embedding_function:
                text_value = str(value) if not isinstance(value, str) else value
                try:
                    entry.embedding = self.embedding_function(text_value)
                except Exception as e:
                    logger.warning(
                        "embedding_generation_failed",
                        key=key,
                        error=str(e),
                    )

            # Store in cache
            cache_key = self._make_cache_key(namespace, key)
            self._cache.set(cache_key, entry)

            # Update namespace index
            self._namespace_index[namespace].add(cache_key)

            # Update pattern index
            self._update_pattern_index(entry)

            # Update stats
            self._stats.total_entries = len(self._cache)
            self._stats.by_namespace[namespace.value] = len(self._namespace_index[namespace])

            logger.debug(
                "memory_stored",
                namespace=namespace.value,
                key=key,
                has_embedding=entry.embedding is not None,
            )

            return entry

    def retrieve(
        self,
        namespace: MemoryNamespace,
        key: str,
    ) -> MemoryEntry | None:
        """
        Retrieve a value from collective memory.
        استرجاع قيمة من الذاكرة الجماعية

        Args:
            namespace: مساحة الاسم - Memory namespace
            key: المفتاح - Entry key

        Returns:
            MemoryEntry | None: الإدخال أو None إذا لم يوجد
        """
        cache_key = self._make_cache_key(namespace, key)
        entry = self._cache.get(cache_key)

        if entry and entry.is_expired:
            self.delete(namespace, key)
            return None

        return entry

    def delete(
        self,
        namespace: MemoryNamespace,
        key: str,
    ) -> bool:
        """
        Delete an entry from memory.
        حذف إدخال من الذاكرة

        Args:
            namespace: مساحة الاسم - Memory namespace
            key: المفتاح - Entry key

        Returns:
            bool: True if deleted, False if not found
        """
        with self._lock:
            cache_key = self._make_cache_key(namespace, key)

            entry = self._cache.get(cache_key)
            if entry:
                # Remove from pattern index
                self._remove_from_pattern_index(entry)

            if self._cache.delete(cache_key):
                self._namespace_index[namespace].discard(cache_key)
                self._stats.total_entries = len(self._cache)
                return True

            return False

    def exists(self, namespace: MemoryNamespace, key: str) -> bool:
        """Check if entry exists | التحقق من وجود الإدخال"""
        entry = self.retrieve(namespace, key)
        return entry is not None

    # ─────────────────────────────────────────────────────────────────────────
    # Pattern Matching and Search
    # ─────────────────────────────────────────────────────────────────────────

    def find_similar(
        self,
        query: str,
        namespace: MemoryNamespace | None = None,
        top_k: int = 5,
        min_similarity: float = 0.3,
    ) -> list[PatternMatch]:
        """
        Find similar entries using text or vector similarity.
        البحث عن إدخالات مماثلة باستخدام تشابه النص أو المتجه

        Args:
            query: الاستعلام - Search query
            namespace: مساحة الاسم - Filter by namespace (optional)
            top_k: أعلى k - Maximum results to return
            min_similarity: الحد الأدنى للتشابه - Minimum similarity score

        Returns:
            list[PatternMatch]: قائمة المطابقات - Matching entries with scores
        """
        start_time = time.time()
        matches: list[tuple[MemoryEntry, float, str]] = []

        # Generate query embedding if enabled
        query_embedding: list[float] | None = None
        if self.enable_embeddings and self.embedding_function:
            try:
                query_embedding = self.embedding_function(query)
            except Exception as e:
                logger.warning("query_embedding_failed", error=str(e))

        # Get entries to search
        entries = self._get_entries_for_search(namespace)

        for entry in entries:
            if entry.is_expired:
                continue

            # Calculate similarity
            similarity = 0.0
            match_type = "text"

            # Try vector similarity first
            if query_embedding and entry.embedding:
                similarity = cosine_similarity(query_embedding, entry.embedding)
                match_type = "semantic"
            else:
                # Fall back to text similarity
                entry_text = self._entry_to_text(entry)
                similarity = text_similarity(query, entry_text)
                match_type = "text"

            if similarity >= min_similarity:
                matches.append((entry, similarity, match_type))

        # Sort by similarity and limit
        matches.sort(key=lambda x: x[1], reverse=True)
        top_matches = matches[:top_k]

        # Update stats
        query_time = (time.time() - start_time) * 1000
        total_queries = self._stats.cache_hits + self._stats.cache_misses + 1
        self._stats.avg_access_time_ms = (
            self._stats.avg_access_time_ms * (total_queries - 1) + query_time
        ) / total_queries

        result = [
            PatternMatch(
                entry=entry,
                similarity=sim,
                match_type=match_type,
            )
            for entry, sim, match_type in top_matches
        ]

        logger.debug(
            "find_similar_completed",
            query_length=len(query),
            results=len(result),
            query_time_ms=query_time,
        )

        return result

    def find_by_pattern(
        self,
        pattern: str,
        namespace: MemoryNamespace | None = None,
        max_results: int = 100,
    ) -> list[MemoryEntry]:
        """
        Find entries matching a keyword pattern.
        البحث عن إدخالات مطابقة لنمط الكلمات المفتاحية

        Args:
            pattern: النمط - Keyword or regex pattern
            namespace: مساحة الاسم - Filter by namespace
            max_results: الحد الأقصى للنتائج - Maximum results

        Returns:
            list[MemoryEntry]: الإدخالات المطابقة
        """
        with self._lock:
            matching_ids: set[str] = set()

            # Check pattern index
            keywords = re.findall(r"\w+", pattern.lower())
            for keyword in keywords:
                if keyword in self._pattern_index:
                    matching_ids.update(self._pattern_index[keyword])

            # Get entries
            entries = []
            for cache_key in matching_ids:
                entry = self._cache.get(cache_key)
                if entry and not entry.is_expired:
                    if namespace is None or entry.namespace == namespace:
                        entries.append(entry)

                if len(entries) >= max_results:
                    break

            return entries

    def query(
        self,
        namespace: MemoryNamespace | None = None,
        filter_fn: Callable[[MemoryEntry], bool] | None = None,
        sort_by: str = "last_accessed",
        limit: int = 100,
        descending: bool = True,
    ) -> list[MemoryEntry]:
        """
        Query entries with filtering and sorting.
        استعلام الإدخالات مع التصفية والترتيب

        Args:
            namespace: مساحة الاسم - Filter by namespace
            filter_fn: دالة التصفية - Custom filter function
            sort_by: الترتيب بواسطة - Field to sort by
            limit: الحد - Maximum results
            descending: تنازلي - Sort direction

        Returns:
            list[MemoryEntry]: الإدخالات المطابقة
        """
        entries = self._get_entries_for_search(namespace)

        # Apply filter
        if filter_fn:
            entries = [e for e in entries if filter_fn(e)]

        # Filter expired
        entries = [e for e in entries if not e.is_expired]

        # Sort
        if sort_by == "last_accessed":
            entries.sort(key=lambda e: e.last_accessed, reverse=descending)
        elif sort_by == "access_count":
            entries.sort(key=lambda e: e.access_count, reverse=descending)
        elif sort_by == "created_at":
            entries.sort(key=lambda e: e.created_at, reverse=descending)

        return entries[:limit]

    # ─────────────────────────────────────────────────────────────────────────
    # Namespace Operations
    # ─────────────────────────────────────────────────────────────────────────

    def list_namespace(
        self,
        namespace: MemoryNamespace,
        limit: int = 100,
    ) -> list[MemoryEntry]:
        """
        List all entries in a namespace.
        عرض جميع الإدخالات في مساحة الاسم

        Args:
            namespace: مساحة الاسم - Namespace to list
            limit: الحد - Maximum entries

        Returns:
            list[MemoryEntry]: الإدخالات
        """
        with self._lock:
            entries = []
            for cache_key in self._namespace_index[namespace]:
                entry = self._cache.get(cache_key)
                if entry and not entry.is_expired:
                    entries.append(entry)
                if len(entries) >= limit:
                    break
            return entries

    def clear_namespace(self, namespace: MemoryNamespace) -> int:
        """
        Clear all entries in a namespace.
        مسح جميع الإدخالات في مساحة الاسم

        Args:
            namespace: مساحة الاسم - Namespace to clear

        Returns:
            int: Number of entries cleared
        """
        with self._lock:
            count = 0
            for cache_key in list(self._namespace_index[namespace]):
                entry = self._cache.get(cache_key)
                if entry:
                    self._remove_from_pattern_index(entry)
                if self._cache.delete(cache_key):
                    count += 1

            self._namespace_index[namespace].clear()
            self._stats.by_namespace[namespace.value] = 0

            logger.info(
                "namespace_cleared",
                namespace=namespace.value,
                entries_cleared=count,
            )

            return count

    def get_namespace_count(self, namespace: MemoryNamespace) -> int:
        """Get count of entries in namespace | الحصول على عدد الإدخالات"""
        return len(self._namespace_index[namespace])

    # ─────────────────────────────────────────────────────────────────────────
    # Maintenance
    # ─────────────────────────────────────────────────────────────────────────

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        إزالة الإدخالات المنتهية الصلاحية

        Returns:
            int: Number of entries removed
        """
        with self._lock:
            expired_keys = []

            for namespace, keys in self._namespace_index.items():
                for cache_key in keys:
                    entry = self._cache.get(cache_key)
                    if entry and entry.is_expired:
                        expired_keys.append((namespace, cache_key, entry))

            count = 0
            for namespace, cache_key, entry in expired_keys:
                self._remove_from_pattern_index(entry)
                self._cache.delete(cache_key)
                self._namespace_index[namespace].discard(cache_key)
                count += 1

            self._stats.last_cleanup = datetime.now(UTC)
            self._stats.total_entries = len(self._cache)

            logger.info("memory_cleanup_completed", expired_removed=count)
            return count

    def get_stats(self) -> MemoryStats:
        """
        Get memory statistics.
        الحصول على إحصائيات الذاكرة

        Returns:
            MemoryStats: إحصائيات الذاكرة
        """
        cache_stats = self._cache.get_stats()

        self._stats.total_entries = cache_stats["size"]
        self._stats.cache_hits = cache_stats["hits"]
        self._stats.cache_misses = cache_stats["misses"]

        # Update namespace counts
        for namespace in MemoryNamespace:
            self._stats.by_namespace[namespace.value] = len(self._namespace_index[namespace])

        return self._stats

    def clear(self) -> None:
        """Clear all memory | مسح كل الذاكرة"""
        with self._lock:
            self._cache.clear_all()
            for namespace in MemoryNamespace:
                self._namespace_index[namespace].clear()
            self._pattern_index.clear()
            self._stats = MemoryStats()

            logger.info("collective_memory_cleared")

    # ─────────────────────────────────────────────────────────────────────────
    # Private Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _make_cache_key(self, namespace: MemoryNamespace, key: str) -> str:
        """Create a unique cache key."""
        return f"{namespace.value}:{key}"

    def _entry_to_text(self, entry: MemoryEntry) -> str:
        """Convert entry to searchable text."""
        parts = [entry.key]

        if isinstance(entry.value, str):
            parts.append(entry.value)
        elif isinstance(entry.value, dict):
            for k, v in entry.value.items():
                parts.append(f"{k} {v}")
        else:
            parts.append(str(entry.value))

        for k, v in entry.metadata.items():
            parts.append(f"{k} {v}")

        return " ".join(parts)

    def _update_pattern_index(self, entry: MemoryEntry) -> None:
        """Update pattern index with entry keywords."""
        text = self._entry_to_text(entry)
        keywords = set(re.findall(r"\w+", text.lower()))

        cache_key = self._make_cache_key(entry.namespace, entry.key)

        for keyword in keywords:
            if len(keyword) >= 3:  # Skip very short words
                if keyword not in self._pattern_index:
                    self._pattern_index[keyword] = []
                if cache_key not in self._pattern_index[keyword]:
                    self._pattern_index[keyword].append(cache_key)

    def _remove_from_pattern_index(self, entry: MemoryEntry) -> None:
        """Remove entry from pattern index."""
        text = self._entry_to_text(entry)
        keywords = set(re.findall(r"\w+", text.lower()))

        cache_key = self._make_cache_key(entry.namespace, entry.key)

        for keyword in keywords:
            if keyword in self._pattern_index:
                if cache_key in self._pattern_index[keyword]:
                    self._pattern_index[keyword].remove(cache_key)
                if not self._pattern_index[keyword]:
                    del self._pattern_index[keyword]

    def _get_entries_for_search(
        self,
        namespace: MemoryNamespace | None = None,
    ) -> list[MemoryEntry]:
        """Get entries for search, optionally filtered by namespace."""
        with self._lock:
            if namespace:
                keys = self._namespace_index[namespace]
            else:
                keys = set()
                for ns_keys in self._namespace_index.values():
                    keys.update(ns_keys)

            entries = []
            for cache_key in keys:
                entry = self._cache.get(cache_key)
                if entry:
                    entries.append(entry)

            return entries


# ─────────────────────────────────────────────────────────────────────────────
# Module-level Singleton
# ─────────────────────────────────────────────────────────────────────────────

_memory_instances: dict[str, CollectiveMemory] = {}


def get_collective_memory(
    tenant_id: str = "sahool",
    max_size: int = 10000,
    enable_embeddings: bool = False,
) -> CollectiveMemory:
    """
    Get or create a collective memory instance for a tenant.
    الحصول على أو إنشاء نسخة الذاكرة الجماعية للمستأجر

    Args:
        tenant_id: معرف المستأجر - Tenant identifier
        max_size: الحجم الأقصى - Maximum entries
        enable_embeddings: تفعيل التضمينات - Enable vector embeddings

    Returns:
        CollectiveMemory: نسخة الذاكرة الجماعية
    """
    if tenant_id not in _memory_instances:
        _memory_instances[tenant_id] = CollectiveMemory(
            max_size=max_size,
            enable_embeddings=enable_embeddings,
            tenant_id=tenant_id,
        )
    return _memory_instances[tenant_id]


def reset_collective_memory(tenant_id: str = "sahool") -> None:
    """Reset memory instance for a tenant | إعادة تعيين نسخة الذاكرة للمستأجر"""
    if tenant_id in _memory_instances:
        del _memory_instances[tenant_id]
