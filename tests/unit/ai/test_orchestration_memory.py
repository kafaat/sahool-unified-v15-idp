"""
Tests for AI Orchestration Collective Memory
============================================
اختبارات الذاكرة الجماعية لتنسيق الذكاء الاصطناعي

Comprehensive tests for CollectiveMemory that provides shared memory
across agents with LRU caching, pattern matching, and persistence.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# Collective Memory Data Models (Module Under Test)
# ═══════════════════════════════════════════════════════════════════════════


class MemoryType(StrEnum):
    """Types of memory entries | أنواع إدخالات الذاكرة"""

    FACT = "fact"  # Verified facts | حقائق موثقة
    OBSERVATION = "observation"  # Observations | ملاحظات
    DECISION = "decision"  # Past decisions | قرارات سابقة
    CONTEXT = "context"  # Contextual info | معلومات سياقية
    PATTERN = "pattern"  # Detected patterns | أنماط مكتشفة
    EXPERIENCE = "experience"  # Learned experiences | تجارب مكتسبة


class MemoryPriority(StrEnum):
    """Memory entry priority | أولوية إدخال الذاكرة"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MemoryEntry:
    """Single memory entry | إدخال ذاكرة واحد"""

    entry_id: str
    key: str
    value: Any
    memory_type: MemoryType = MemoryType.FACT
    priority: MemoryPriority = MemoryPriority.MEDIUM
    tags: list[str] = field(default_factory=list)
    source_agent: str | None = None
    confidence: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    access_count: int = 0
    last_accessed: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "key": self.key,
            "value": self.value,
            "memory_type": self.memory_type.value,
            "priority": self.priority.value,
            "tags": self.tags,
            "source_agent": self.source_agent,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "access_count": self.access_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary"""
        return cls(
            entry_id=data["entry_id"],
            key=data["key"],
            value=data["value"],
            memory_type=MemoryType(data.get("memory_type", "fact")),
            priority=MemoryPriority(data.get("priority", "medium")),
            tags=data.get("tags", []),
            source_agent=data.get("source_agent"),
            confidence=data.get("confidence", 1.0),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(UTC),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            access_count=data.get("access_count", 0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class PatternMatch:
    """Result of pattern matching | نتيجة مطابقة النمط"""

    entry: MemoryEntry
    score: float
    matched_tags: list[str]
    matched_keys: list[str]


class LRUCache:
    """
    LRU (Least Recently Used) cache implementation.
    تطبيق ذاكرة التخزين المؤقت LRU (الأقل استخداماً مؤخراً).
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize LRU cache | تهيئة ذاكرة التخزين المؤقت LRU

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self._cache: dict[str, MemoryEntry] = {}
        self._access_order: list[str] = []

    def get(self, key: str) -> MemoryEntry | None:
        """
        Get entry from cache | الحصول على إدخال من ذاكرة التخزين المؤقت
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Update access tracking
        entry.access_count += 1
        entry.last_accessed = datetime.now(UTC)

        # Move to end (most recently used)
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return entry

    def put(self, entry: MemoryEntry) -> None:
        """
        Put entry in cache | وضع إدخال في ذاكرة التخزين المؤقت
        """
        key = entry.key

        if key in self._cache:
            # Update existing entry
            self._cache[key] = entry
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
        else:
            # Add new entry
            if len(self._cache) >= self.max_size:
                # Evict least recently used
                self._evict_lru()

            self._cache[key] = entry
            self._access_order.append(key)

    def _evict_lru(self) -> str | None:
        """Evict least recently used entry"""
        if not self._access_order:
            return None

        lru_key = self._access_order.pop(0)
        if lru_key in self._cache:
            del self._cache[lru_key]
        return lru_key

    def remove(self, key: str) -> bool:
        """Remove entry from cache"""
        if key not in self._cache:
            return False

        del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)
        return True

    def clear(self) -> None:
        """Clear all entries"""
        self._cache.clear()
        self._access_order.clear()

    def get_all(self) -> list[MemoryEntry]:
        """Get all entries"""
        return list(self._cache.values())

    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_access = sum(e.access_count for e in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0.0,
            "total_access_count": total_access,
            "entries_by_priority": {
                p.value: sum(1 for e in self._cache.values() if e.priority == p) for p in MemoryPriority
            },
        }


class CollectiveMemory:
    """
    Shared memory system for agent collaboration.
    نظام ذاكرة مشترك لتعاون الوكلاء.

    Features:
    - LRU caching with configurable size
    - Pattern matching for memory retrieval
    - Memory persistence to file
    - TTL (time-to-live) support for entries
    - Tag-based organization

    الميزات:
    - تخزين مؤقت LRU مع حجم قابل للتكوين
    - مطابقة الأنماط لاسترجاع الذاكرة
    - حفظ الذاكرة في ملف
    - دعم TTL (وقت البقاء) للإدخالات
    - تنظيم قائم على العلامات
    """

    def __init__(
        self,
        max_entries: int = 10000,
        persistence_path: str | None = None,
        auto_cleanup: bool = True,
    ):
        """
        Initialize collective memory | تهيئة الذاكرة الجماعية

        Args:
            max_entries: Maximum number of memory entries
            persistence_path: Path for persistent storage
            auto_cleanup: Automatically remove expired entries
        """
        self.max_entries = max_entries
        self.persistence_path = persistence_path
        self.auto_cleanup = auto_cleanup

        self._cache = LRUCache(max_size=max_entries)
        self._tag_index: dict[str, set[str]] = {}  # tag -> entry_ids
        self._type_index: dict[MemoryType, set[str]] = {}  # type -> entry_ids
        self._agent_index: dict[str, set[str]] = {}  # agent_id -> entry_ids

    async def store(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.FACT,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        tags: list[str] | None = None,
        source_agent: str | None = None,
        ttl_seconds: int | None = None,
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """
        Store a memory entry | تخزين إدخال ذاكرة

        Args:
            key: Unique key for the entry
            value: Value to store
            memory_type: Type of memory
            priority: Entry priority
            tags: List of tags for organization
            source_agent: ID of agent storing the memory
            ttl_seconds: Time-to-live in seconds
            confidence: Confidence level (0-1)
            metadata: Additional metadata

        Returns:
            Created memory entry
        """
        entry_id = str(uuid4())
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)

        entry = MemoryEntry(
            entry_id=entry_id,
            key=key,
            value=value,
            memory_type=memory_type,
            priority=priority,
            tags=tags or [],
            source_agent=source_agent,
            confidence=confidence,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        # Store in cache
        self._cache.put(entry)

        # Update indexes
        self._update_indexes(entry)

        # Auto cleanup if enabled
        if self.auto_cleanup:
            await self._cleanup_expired()

        return entry

    def _update_indexes(self, entry: MemoryEntry) -> None:
        """Update search indexes"""
        # Tag index
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(entry.key)

        # Type index
        if entry.memory_type not in self._type_index:
            self._type_index[entry.memory_type] = set()
        self._type_index[entry.memory_type].add(entry.key)

        # Agent index
        if entry.source_agent:
            if entry.source_agent not in self._agent_index:
                self._agent_index[entry.source_agent] = set()
            self._agent_index[entry.source_agent].add(entry.key)

    async def retrieve(self, key: str) -> MemoryEntry | None:
        """
        Retrieve a memory entry by key | استرجاع إدخال ذاكرة بواسطة المفتاح

        Args:
            key: Entry key

        Returns:
            Memory entry or None if not found
        """
        entry = self._cache.get(key)

        if entry and entry.is_expired():
            # Remove expired entry
            self._cache.remove(key)
            self._remove_from_indexes(entry)
            return None

        return entry

    def _remove_from_indexes(self, entry: MemoryEntry) -> None:
        """Remove entry from all indexes"""
        for tag in entry.tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(entry.key)

        if entry.memory_type in self._type_index:
            self._type_index[entry.memory_type].discard(entry.key)

        if entry.source_agent and entry.source_agent in self._agent_index:
            self._agent_index[entry.source_agent].discard(entry.key)

    async def delete(self, key: str) -> bool:
        """
        Delete a memory entry | حذف إدخال ذاكرة

        Args:
            key: Entry key

        Returns:
            True if deleted, False if not found
        """
        entry = self._cache.get(key)
        if not entry:
            return False

        self._remove_from_indexes(entry)
        return self._cache.remove(key)

    async def match_pattern(
        self,
        pattern: str | None = None,
        tags: list[str] | None = None,
        memory_type: MemoryType | None = None,
        source_agent: str | None = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> list[PatternMatch]:
        """
        Find entries matching a pattern | البحث عن إدخالات تطابق نمطاً

        Args:
            pattern: Key pattern (supports * wildcard)
            tags: Tags to match
            memory_type: Filter by memory type
            source_agent: Filter by source agent
            min_confidence: Minimum confidence threshold
            limit: Maximum results to return

        Returns:
            List of matching entries with scores
        """
        candidates = self._cache.get_all()
        matches = []

        for entry in candidates:
            if entry.is_expired():
                continue

            if entry.confidence < min_confidence:
                continue

            score = 0.0
            matched_tags = []
            matched_keys = []

            # Pattern matching
            if pattern:
                if self._key_matches_pattern(entry.key, pattern):
                    score += 0.4
                    matched_keys.append(entry.key)
                else:
                    continue

            # Tag matching
            if tags:
                common_tags = set(tags) & set(entry.tags)
                if common_tags:
                    score += 0.3 * (len(common_tags) / len(tags))
                    matched_tags.extend(common_tags)
                elif pattern is None:  # Require tag match if no pattern
                    continue

            # Type matching
            if memory_type:
                if entry.memory_type != memory_type:
                    continue
                score += 0.2

            # Agent matching
            if source_agent:
                if entry.source_agent != source_agent:
                    continue
                score += 0.1

            # Base score if no specific criteria
            if score == 0.0 and pattern is None and tags is None:
                score = 0.1  # Minimal score for unfiltered entries

            if score > 0:
                matches.append(
                    PatternMatch(
                        entry=entry,
                        score=score,
                        matched_tags=matched_tags,
                        matched_keys=matched_keys,
                    )
                )

        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)

        return matches[:limit]

    def _key_matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (with * wildcard)"""
        if "*" not in pattern:
            return key == pattern

        # Simple wildcard matching
        if pattern == "*":
            return True

        if pattern.startswith("*") and pattern.endswith("*"):
            return pattern[1:-1] in key

        if pattern.startswith("*"):
            return key.endswith(pattern[1:])

        if pattern.endswith("*"):
            return key.startswith(pattern[:-1])

        # Pattern like "prefix*suffix"
        parts = pattern.split("*")
        if len(parts) == 2:
            return key.startswith(parts[0]) and key.endswith(parts[1])

        return False

    async def get_by_tags(
        self,
        tags: list[str],
        match_all: bool = False,
    ) -> list[MemoryEntry]:
        """
        Get entries by tags | الحصول على إدخالات حسب العلامات

        Args:
            tags: Tags to search for
            match_all: If True, entry must have all tags

        Returns:
            List of matching entries
        """
        if not tags:
            return []

        matching_keys: set[str] = set()

        if match_all:
            # Intersection of all tag indexes
            for i, tag in enumerate(tags):
                tag_keys = self._tag_index.get(tag, set())
                if i == 0:
                    matching_keys = tag_keys.copy()
                else:
                    matching_keys &= tag_keys
        else:
            # Union of all tag indexes
            for tag in tags:
                matching_keys |= self._tag_index.get(tag, set())

        entries = []
        for key in matching_keys:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                entries.append(entry)

        return entries

    async def get_by_type(self, memory_type: MemoryType) -> list[MemoryEntry]:
        """Get entries by memory type"""
        keys = self._type_index.get(memory_type, set())
        entries = []

        for key in keys:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                entries.append(entry)

        return entries

    async def get_by_agent(self, agent_id: str) -> list[MemoryEntry]:
        """Get entries by source agent"""
        keys = self._agent_index.get(agent_id, set())
        entries = []

        for key in keys:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                entries.append(entry)

        return entries

    async def persist(self) -> int:
        """
        Persist memory to file | حفظ الذاكرة في ملف

        Returns:
            Number of entries persisted
        """
        if not self.persistence_path:
            return 0

        entries = self._cache.get_all()
        data = {
            "version": "1.0",
            "persisted_at": datetime.now(UTC).isoformat(),
            "entries": [e.to_dict() for e in entries if not e.is_expired()],
        }

        with open(self.persistence_path, "w") as f:
            json.dump(data, f, indent=2)

        return len(data["entries"])

    async def load(self) -> int:
        """
        Load memory from file | تحميل الذاكرة من ملف

        Returns:
            Number of entries loaded
        """
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return 0

        with open(self.persistence_path) as f:
            data = json.load(f)

        entries_loaded = 0
        for entry_data in data.get("entries", []):
            entry = MemoryEntry.from_dict(entry_data)
            if not entry.is_expired():
                self._cache.put(entry)
                self._update_indexes(entry)
                entries_loaded += 1

        return entries_loaded

    async def _cleanup_expired(self) -> int:
        """Remove expired entries"""
        entries = self._cache.get_all()
        removed = 0

        for entry in entries:
            if entry.is_expired():
                self._cache.remove(entry.key)
                self._remove_from_indexes(entry)
                removed += 1

        return removed

    def clear(self) -> None:
        """Clear all memory"""
        self._cache.clear()
        self._tag_index.clear()
        self._type_index.clear()
        self._agent_index.clear()

    def size(self) -> int:
        """Get total number of entries"""
        return self._cache.size()

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics"""
        cache_stats = self._cache.get_stats()
        return {
            **cache_stats,
            "total_tags": len(self._tag_index),
            "total_agents": len(self._agent_index),
            "entries_by_type": {t.value: len(keys) for t, keys in self._type_index.items()},
            "persistence_enabled": self.persistence_path is not None,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def memory() -> CollectiveMemory:
    """Create a collective memory instance."""
    return CollectiveMemory(max_entries=1000)


@pytest.fixture
def lru_cache() -> LRUCache:
    """Create an LRU cache instance."""
    return LRUCache(max_size=10)


@pytest.fixture
def sample_entry() -> MemoryEntry:
    """Create a sample memory entry."""
    return MemoryEntry(
        entry_id="entry_001",
        key="field_analysis_FIELD-003",
        value={"ndvi": 0.72, "health": "good"},
        memory_type=MemoryType.OBSERVATION,
        priority=MemoryPriority.HIGH,
        tags=["field", "ndvi", "wheat"],
        source_agent="field_analyst",
        confidence=0.9,
    )


@pytest.fixture
def persistence_path(tmp_path) -> str:
    """Create a temporary persistence path."""
    return str(tmp_path / "memory.json")


# ═══════════════════════════════════════════════════════════════════════════
# Test Store and Retrieve - test_store_and_retrieve
# ═══════════════════════════════════════════════════════════════════════════


class TestStoreAndRetrieve:
    """Tests for storing and retrieving memory entries."""

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, memory: CollectiveMemory):
        """Test basic store and retrieve operations."""
        entry = await memory.store(
            key="test_key",
            value={"data": "test_value"},
            memory_type=MemoryType.FACT,
        )

        retrieved = await memory.retrieve("test_key")

        assert retrieved is not None
        assert retrieved.key == "test_key"
        assert retrieved.value == {"data": "test_value"}

    @pytest.mark.asyncio
    async def test_store_with_all_options(self, memory: CollectiveMemory):
        """Test storing with all options specified."""
        entry = await memory.store(
            key="full_entry",
            value={"complete": True},
            memory_type=MemoryType.DECISION,
            priority=MemoryPriority.CRITICAL,
            tags=["important", "decision"],
            source_agent="supervisor",
            ttl_seconds=3600,
            confidence=0.95,
            metadata={"reason": "Strategic decision"},
        )

        assert entry.key == "full_entry"
        assert entry.memory_type == MemoryType.DECISION
        assert entry.priority == MemoryPriority.CRITICAL
        assert "important" in entry.tags
        assert entry.source_agent == "supervisor"
        assert entry.confidence == 0.95
        assert entry.expires_at is not None

    @pytest.mark.asyncio
    async def test_store_updates_existing(self, memory: CollectiveMemory):
        """Test that storing with same key updates entry."""
        await memory.store(key="update_key", value="original")
        await memory.store(key="update_key", value="updated")

        retrieved = await memory.retrieve("update_key")

        assert retrieved.value == "updated"

    @pytest.mark.asyncio
    async def test_retrieve_nonexistent(self, memory: CollectiveMemory):
        """Test retrieving nonexistent key returns None."""
        retrieved = await memory.retrieve("nonexistent_key")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_retrieve_updates_access_count(self, memory: CollectiveMemory):
        """Test that retrieving updates access count."""
        await memory.store(key="access_key", value="data")

        retrieved1 = await memory.retrieve("access_key")
        assert retrieved1.access_count == 1

        retrieved2 = await memory.retrieve("access_key")
        assert retrieved2.access_count == 2

    @pytest.mark.asyncio
    async def test_store_with_tags(self, memory: CollectiveMemory):
        """Test storing with tags updates indexes."""
        await memory.store(
            key="tagged_entry",
            value="data",
            tags=["crop", "wheat", "irrigation"],
        )

        # Tags should be indexed
        assert "crop" in memory._tag_index
        assert "tagged_entry" in memory._tag_index["crop"]

    @pytest.mark.asyncio
    async def test_delete_entry(self, memory: CollectiveMemory):
        """Test deleting a memory entry."""
        await memory.store(key="delete_key", value="data")

        deleted = await memory.delete("delete_key")
        assert deleted is True

        retrieved = await memory.retrieve("delete_key")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, memory: CollectiveMemory):
        """Test deleting nonexistent entry returns False."""
        deleted = await memory.delete("nonexistent")
        assert deleted is False


# ═══════════════════════════════════════════════════════════════════════════
# Test LRU Cache Eviction - test_lru_cache_eviction
# ═══════════════════════════════════════════════════════════════════════════


class TestLRUCacheEviction:
    """Tests for LRU cache eviction."""

    def test_lru_cache_eviction(self, lru_cache: LRUCache):
        """Test that LRU entries are evicted when cache is full."""
        # Fill cache to capacity (10)
        for i in range(10):
            entry = MemoryEntry(
                entry_id=f"entry_{i}",
                key=f"key_{i}",
                value=f"value_{i}",
            )
            lru_cache.put(entry)

        assert lru_cache.size() == 10

        # Access some entries to update their recency
        lru_cache.get("key_5")
        lru_cache.get("key_7")

        # Add new entry - should evict LRU (key_0)
        new_entry = MemoryEntry(
            entry_id="entry_new",
            key="key_new",
            value="new_value",
        )
        lru_cache.put(new_entry)

        # key_0 should be evicted (first in, not accessed)
        assert lru_cache.get("key_0") is None
        assert lru_cache.get("key_new") is not None
        assert lru_cache.size() == 10

    def test_lru_preserves_recently_accessed(self, lru_cache: LRUCache):
        """Test that recently accessed entries are preserved."""
        # Fill cache
        for i in range(10):
            entry = MemoryEntry(
                entry_id=f"entry_{i}",
                key=f"key_{i}",
                value=f"value_{i}",
            )
            lru_cache.put(entry)

        # Access key_0 to make it recently used
        lru_cache.get("key_0")

        # Add new entry - key_1 should be evicted (oldest not accessed)
        new_entry = MemoryEntry(
            entry_id="entry_new",
            key="key_new",
            value="new_value",
        )
        lru_cache.put(new_entry)

        # key_0 should still be present
        assert lru_cache.get("key_0") is not None
        # key_1 should be evicted
        assert lru_cache.get("key_1") is None

    def test_lru_cache_clear(self, lru_cache: LRUCache):
        """Test clearing the cache."""
        for i in range(5):
            entry = MemoryEntry(
                entry_id=f"entry_{i}",
                key=f"key_{i}",
                value=f"value_{i}",
            )
            lru_cache.put(entry)

        lru_cache.clear()

        assert lru_cache.size() == 0

    def test_lru_cache_stats(self, lru_cache: LRUCache):
        """Test cache statistics."""
        for i in range(5):
            entry = MemoryEntry(
                entry_id=f"entry_{i}",
                key=f"key_{i}",
                value=f"value_{i}",
                priority=MemoryPriority.HIGH if i % 2 == 0 else MemoryPriority.LOW,
            )
            lru_cache.put(entry)

        # Access some entries
        lru_cache.get("key_0")
        lru_cache.get("key_0")
        lru_cache.get("key_1")

        stats = lru_cache.get_stats()

        assert stats["size"] == 5
        assert stats["max_size"] == 10
        assert stats["utilization"] == 0.5
        assert stats["total_access_count"] == 3

    def test_lru_cache_remove(self, lru_cache: LRUCache):
        """Test removing specific entry."""
        entry = MemoryEntry(
            entry_id="entry_1",
            key="key_1",
            value="value_1",
        )
        lru_cache.put(entry)

        removed = lru_cache.remove("key_1")
        assert removed is True
        assert lru_cache.get("key_1") is None

    def test_lru_cache_remove_nonexistent(self, lru_cache: LRUCache):
        """Test removing nonexistent entry."""
        removed = lru_cache.remove("nonexistent")
        assert removed is False


# ═══════════════════════════════════════════════════════════════════════════
# Test Pattern Matching - test_pattern_matching
# ═══════════════════════════════════════════════════════════════════════════


class TestPatternMatching:
    """Tests for pattern matching in memory retrieval."""

    @pytest.mark.asyncio
    async def test_pattern_matching(self, memory: CollectiveMemory):
        """Test pattern matching with wildcard."""
        await memory.store(key="field_001_ndvi", value={"ndvi": 0.7})
        await memory.store(key="field_002_ndvi", value={"ndvi": 0.8})
        await memory.store(key="field_001_temperature", value={"temp": 25})

        matches = await memory.match_pattern(pattern="field_*_ndvi")

        assert len(matches) == 2
        assert all("ndvi" in m.entry.key for m in matches)

    @pytest.mark.asyncio
    async def test_pattern_matching_prefix(self, memory: CollectiveMemory):
        """Test pattern matching with prefix wildcard."""
        await memory.store(key="field_analysis", value="data1")
        await memory.store(key="crop_analysis", value="data2")
        await memory.store(key="weather_report", value="data3")

        matches = await memory.match_pattern(pattern="*_analysis")

        assert len(matches) == 2

    @pytest.mark.asyncio
    async def test_pattern_matching_suffix(self, memory: CollectiveMemory):
        """Test pattern matching with suffix wildcard."""
        await memory.store(key="wheat_field", value="data1")
        await memory.store(key="barley_field", value="data2")
        await memory.store(key="wheat_crop", value="data3")

        matches = await memory.match_pattern(pattern="wheat_*")

        assert len(matches) == 2

    @pytest.mark.asyncio
    async def test_pattern_matching_by_tags(self, memory: CollectiveMemory):
        """Test pattern matching with tags."""
        await memory.store(key="entry1", value="v1", tags=["wheat", "irrigation"])
        await memory.store(key="entry2", value="v2", tags=["wheat", "pest"])
        await memory.store(key="entry3", value="v3", tags=["barley", "irrigation"])

        matches = await memory.match_pattern(tags=["wheat"])

        assert len(matches) == 2

    @pytest.mark.asyncio
    async def test_pattern_matching_by_type(self, memory: CollectiveMemory):
        """Test pattern matching by memory type."""
        await memory.store(key="fact1", value="v1", memory_type=MemoryType.FACT)
        await memory.store(key="obs1", value="v2", memory_type=MemoryType.OBSERVATION)
        await memory.store(key="fact2", value="v3", memory_type=MemoryType.FACT)

        matches = await memory.match_pattern(memory_type=MemoryType.FACT)

        assert len(matches) == 2
        assert all(m.entry.memory_type == MemoryType.FACT for m in matches)

    @pytest.mark.asyncio
    async def test_pattern_matching_by_agent(self, memory: CollectiveMemory):
        """Test pattern matching by source agent."""
        await memory.store(key="e1", value="v1", source_agent="agent_A")
        await memory.store(key="e2", value="v2", source_agent="agent_B")
        await memory.store(key="e3", value="v3", source_agent="agent_A")

        matches = await memory.match_pattern(source_agent="agent_A")

        assert len(matches) == 2

    @pytest.mark.asyncio
    async def test_pattern_matching_min_confidence(self, memory: CollectiveMemory):
        """Test pattern matching with minimum confidence."""
        await memory.store(key="high_conf", value="v1", confidence=0.9)
        await memory.store(key="low_conf", value="v2", confidence=0.3)
        await memory.store(key="med_conf", value="v3", confidence=0.6)

        matches = await memory.match_pattern(pattern="*", min_confidence=0.5)

        assert len(matches) == 2

    @pytest.mark.asyncio
    async def test_pattern_matching_combined(self, memory: CollectiveMemory):
        """Test pattern matching with multiple criteria."""
        await memory.store(
            key="field_001_analysis",
            value="data1",
            tags=["wheat"],
            memory_type=MemoryType.OBSERVATION,
            source_agent="analyst",
        )
        await memory.store(
            key="field_002_analysis",
            value="data2",
            tags=["barley"],
            memory_type=MemoryType.OBSERVATION,
            source_agent="analyst",
        )
        await memory.store(
            key="field_001_report",
            value="data3",
            tags=["wheat"],
            memory_type=MemoryType.FACT,
            source_agent="reporter",
        )

        matches = await memory.match_pattern(
            pattern="field_*",
            memory_type=MemoryType.OBSERVATION,
            source_agent="analyst",
        )

        assert len(matches) == 2

    @pytest.mark.asyncio
    async def test_pattern_matching_limit(self, memory: CollectiveMemory):
        """Test pattern matching respects limit."""
        for i in range(20):
            await memory.store(key=f"item_{i}", value=f"value_{i}")

        matches = await memory.match_pattern(pattern="item_*", limit=5)

        assert len(matches) == 5


# ═══════════════════════════════════════════════════════════════════════════
# Test Memory Persistence - test_memory_persistence
# ═══════════════════════════════════════════════════════════════════════════


class TestMemoryPersistence:
    """Tests for memory persistence."""

    @pytest.mark.asyncio
    async def test_memory_persistence(self, persistence_path: str):
        """Test persisting and loading memory."""
        # Create and populate memory
        memory = CollectiveMemory(persistence_path=persistence_path)

        await memory.store(key="persist_1", value="value_1", tags=["test"])
        await memory.store(key="persist_2", value="value_2", tags=["test"])

        # Persist to file
        persisted = await memory.persist()
        assert persisted == 2

        # Create new memory and load
        new_memory = CollectiveMemory(persistence_path=persistence_path)
        loaded = await new_memory.load()

        assert loaded == 2

        # Verify data
        entry = await new_memory.retrieve("persist_1")
        assert entry is not None
        assert entry.value == "value_1"

    @pytest.mark.asyncio
    async def test_persistence_excludes_expired(self, persistence_path: str):
        """Test that expired entries are not persisted."""
        memory = CollectiveMemory(persistence_path=persistence_path)

        # Store entry with very short TTL
        await memory.store(key="short_lived", value="data", ttl_seconds=1)
        await memory.store(key="permanent", value="data")

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Persist
        persisted = await memory.persist()

        # Only permanent entry should be persisted
        assert persisted == 1

    @pytest.mark.asyncio
    async def test_persistence_no_path(self, memory: CollectiveMemory):
        """Test persistence returns 0 when no path configured."""
        await memory.store(key="data", value="value")

        persisted = await memory.persist()

        assert persisted == 0

    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self, tmp_path):
        """Test loading from nonexistent file."""
        memory = CollectiveMemory(persistence_path=str(tmp_path / "nonexistent.json"))

        loaded = await memory.load()

        assert loaded == 0

    @pytest.mark.asyncio
    async def test_persistence_preserves_metadata(self, persistence_path: str):
        """Test that metadata is preserved through persistence."""
        memory = CollectiveMemory(persistence_path=persistence_path)

        await memory.store(
            key="meta_entry",
            value="data",
            memory_type=MemoryType.DECISION,
            priority=MemoryPriority.HIGH,
            tags=["important"],
            source_agent="supervisor",
            confidence=0.95,
            metadata={"custom": "metadata"},
        )

        await memory.persist()

        # Load into new memory
        new_memory = CollectiveMemory(persistence_path=persistence_path)
        await new_memory.load()

        entry = await new_memory.retrieve("meta_entry")

        assert entry is not None
        assert entry.memory_type == MemoryType.DECISION
        assert entry.priority == MemoryPriority.HIGH
        assert "important" in entry.tags
        assert entry.source_agent == "supervisor"
        assert entry.confidence == 0.95
        assert entry.metadata["custom"] == "metadata"


# ═══════════════════════════════════════════════════════════════════════════
# Test TTL and Expiration
# ═══════════════════════════════════════════════════════════════════════════


class TestTTLAndExpiration:
    """Tests for TTL and entry expiration."""

    @pytest.mark.asyncio
    async def test_ttl_entry_expires(self, memory: CollectiveMemory):
        """Test that entries with TTL expire."""
        await memory.store(key="expiring", value="data", ttl_seconds=1)

        # Should exist initially
        entry = await memory.retrieve("expiring")
        assert entry is not None

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be None now
        entry = await memory.retrieve("expiring")
        assert entry is None

    @pytest.mark.asyncio
    async def test_entry_without_ttl_persists(self, memory: CollectiveMemory):
        """Test that entries without TTL don't expire."""
        await memory.store(key="permanent", value="data")

        entry = await memory.retrieve("permanent")
        assert entry is not None
        assert entry.expires_at is None
        assert entry.is_expired() is False

    @pytest.mark.asyncio
    async def test_expired_entries_cleaned_on_store(self, memory: CollectiveMemory):
        """Test that expired entries are cleaned when storing new entries."""
        await memory.store(key="short_ttl", value="data", ttl_seconds=1)

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Store new entry (triggers cleanup)
        await memory.store(key="new_entry", value="new_data")

        # Expired entry should be cleaned
        entry = await memory.retrieve("short_ttl")
        assert entry is None

    @pytest.mark.asyncio
    async def test_manual_cleanup(self, memory: CollectiveMemory):
        """Test manual cleanup of expired entries."""
        memory.auto_cleanup = False

        await memory.store(key="exp1", value="data", ttl_seconds=1)
        await memory.store(key="exp2", value="data", ttl_seconds=1)
        await memory.store(key="permanent", value="data")

        await asyncio.sleep(1.1)

        removed = await memory._cleanup_expired()

        assert removed == 2
        assert memory.size() == 1


# ═══════════════════════════════════════════════════════════════════════════
# Test Index Operations
# ═══════════════════════════════════════════════════════════════════════════


class TestIndexOperations:
    """Tests for index-based retrieval."""

    @pytest.mark.asyncio
    async def test_get_by_tags(self, memory: CollectiveMemory):
        """Test getting entries by tags."""
        await memory.store(key="e1", value="v1", tags=["tag_a", "tag_b"])
        await memory.store(key="e2", value="v2", tags=["tag_a", "tag_c"])
        await memory.store(key="e3", value="v3", tags=["tag_b", "tag_c"])

        # Match any tag
        entries = await memory.get_by_tags(["tag_a"], match_all=False)
        assert len(entries) == 2

    @pytest.mark.asyncio
    async def test_get_by_tags_match_all(self, memory: CollectiveMemory):
        """Test getting entries matching all tags."""
        await memory.store(key="e1", value="v1", tags=["tag_a", "tag_b"])
        await memory.store(key="e2", value="v2", tags=["tag_a", "tag_c"])
        await memory.store(key="e3", value="v3", tags=["tag_a", "tag_b", "tag_c"])

        entries = await memory.get_by_tags(["tag_a", "tag_b"], match_all=True)

        assert len(entries) == 2  # e1 and e3 have both tags

    @pytest.mark.asyncio
    async def test_get_by_type(self, memory: CollectiveMemory):
        """Test getting entries by type."""
        await memory.store(key="f1", value="v1", memory_type=MemoryType.FACT)
        await memory.store(key="f2", value="v2", memory_type=MemoryType.FACT)
        await memory.store(key="o1", value="v3", memory_type=MemoryType.OBSERVATION)

        entries = await memory.get_by_type(MemoryType.FACT)

        assert len(entries) == 2

    @pytest.mark.asyncio
    async def test_get_by_agent(self, memory: CollectiveMemory):
        """Test getting entries by source agent."""
        await memory.store(key="a1", value="v1", source_agent="agent_1")
        await memory.store(key="a2", value="v2", source_agent="agent_1")
        await memory.store(key="b1", value="v3", source_agent="agent_2")

        entries = await memory.get_by_agent("agent_1")

        assert len(entries) == 2


# ═══════════════════════════════════════════════════════════════════════════
# Test Statistics
# ═══════════════════════════════════════════════════════════════════════════


class TestMemoryStatistics:
    """Tests for memory statistics."""

    @pytest.mark.asyncio
    async def test_get_stats(self, memory: CollectiveMemory):
        """Test getting memory statistics."""
        await memory.store(
            key="e1",
            value="v1",
            tags=["tag1", "tag2"],
            source_agent="agent1",
            memory_type=MemoryType.FACT,
        )
        await memory.store(
            key="e2",
            value="v2",
            tags=["tag1"],
            source_agent="agent2",
            memory_type=MemoryType.OBSERVATION,
        )

        stats = memory.get_stats()

        assert stats["size"] == 2
        assert stats["total_tags"] == 2
        assert stats["total_agents"] == 2

    @pytest.mark.asyncio
    async def test_memory_size(self, memory: CollectiveMemory):
        """Test memory size tracking."""
        assert memory.size() == 0

        await memory.store(key="e1", value="v1")
        assert memory.size() == 1

        await memory.store(key="e2", value="v2")
        assert memory.size() == 2

    @pytest.mark.asyncio
    async def test_memory_clear(self, memory: CollectiveMemory):
        """Test clearing all memory."""
        await memory.store(key="e1", value="v1", tags=["tag"])
        await memory.store(key="e2", value="v2")

        memory.clear()

        assert memory.size() == 0
        assert len(memory._tag_index) == 0
