"""
AI Farm Memory Module
======================
وحدة ذاكرة المزرعة للذكاء الاصطناعي

Provides memory management for AI interactions with tenant isolation.
Implements sliding window for recent history and context retrieval.

المميزات:
- عزل البيانات لكل مستأجر (Tenant Isolation)
- نافذة منزلقة للسجل الأخير
- استرجاع السياق ذي الصلة
- تخزين واسترجاع الذاكرة

Author: SAHOOL Platform Team
Updated: January 2025
"""

from __future__ import annotations

import hashlib
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Constants & Configuration
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_WINDOW_SIZE = 20
DEFAULT_TTL_HOURS = 24
DEFAULT_MAX_ENTRIES = 1000
DEFAULT_RELEVANCE_THRESHOLD = 0.5


# ─────────────────────────────────────────────────────────────────────────────
# Enums & Models
# ─────────────────────────────────────────────────────────────────────────────


class MemoryType(str, Enum):
    """
    Type of memory entry.
    نوع إدخال الذاكرة
    """

    CONVERSATION = "conversation"  # Chat/interaction history
    FIELD_STATE = "field_state"  # Field status snapshots
    RECOMMENDATION = "recommendation"  # AI recommendations
    OBSERVATION = "observation"  # Field observations
    WEATHER = "weather"  # Weather data
    ACTION = "action"  # User actions
    SYSTEM = "system"  # System events


class RelevanceScore(str, Enum):
    """
    Relevance scoring for memory retrieval.
    تقييم الصلة لاسترجاع الذاكرة
    """

    CRITICAL = "critical"  # Always include
    HIGH = "high"  # Include if space
    MEDIUM = "medium"  # Include if relevant
    LOW = "low"  # Only if specifically requested


@dataclass
class MemoryConfig:
    """
    Configuration for farm memory.
    إعدادات ذاكرة المزرعة

    Attributes:
        window_size: حجم النافذة - Number of recent entries to keep in sliding window
        max_entries: الحد الأقصى للإدخالات - Maximum total entries per tenant
        ttl_hours: مدة الصلاحية - Time-to-live for entries in hours
        relevance_threshold: عتبة الصلة - Minimum relevance score for retrieval
        enable_compression: تفعيل الضغط - Enable automatic compression
        persist_to_storage: الحفظ الدائم - Persist to external storage
    """

    window_size: int = DEFAULT_WINDOW_SIZE
    max_entries: int = DEFAULT_MAX_ENTRIES
    ttl_hours: int = DEFAULT_TTL_HOURS
    relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD
    enable_compression: bool = True
    persist_to_storage: bool = False


@dataclass
class MemoryEntry:
    """
    A single memory entry.
    إدخال ذاكرة واحد

    Attributes:
        id: المعرف - Unique identifier
        tenant_id: معرف المستأجر - Tenant identifier for isolation
        field_id: معرف الحقل - Field identifier (optional)
        memory_type: نوع الذاكرة - Type of memory entry
        content: المحتوى - The actual content/data
        metadata: البيانات الوصفية - Additional metadata
        timestamp: الطابع الزمني - When entry was created
        relevance: الصلة - Relevance score
        embedding: التضمين - Vector embedding (optional)
        expires_at: تاريخ الانتهاء - Expiration timestamp
    """

    id: str
    tenant_id: str
    field_id: str | None
    memory_type: MemoryType
    content: dict[str, Any] | str
    metadata: dict[str, Any]
    timestamp: datetime
    relevance: RelevanceScore
    embedding: list[float] | None = None
    expires_at: datetime | None = None

    @classmethod
    def create(
        cls,
        tenant_id: str,
        memory_type: MemoryType,
        content: dict[str, Any] | str,
        field_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        relevance: RelevanceScore = RelevanceScore.MEDIUM,
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> MemoryEntry:
        """
        Factory method to create a memory entry.
        طريقة إنشاء إدخال ذاكرة

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
            memory_type: نوع الذاكرة - Type of entry
            content: المحتوى - Content to store
            field_id: معرف الحقل - Optional field identifier
            metadata: البيانات الوصفية - Optional metadata
            relevance: الصلة - Relevance score
            ttl_hours: مدة الصلاحية - Time-to-live in hours

        Returns:
            MemoryEntry: إدخال الذاكرة الجديد - New memory entry
        """
        now = datetime.now(UTC)
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            field_id=field_id,
            memory_type=memory_type,
            content=content,
            metadata=metadata or {},
            timestamp=now,
            relevance=relevance,
            embedding=None,
            expires_at=now + timedelta(hours=ttl_hours) if ttl_hours > 0 else None,
        )

    def is_expired(self) -> bool:
        """Check if entry has expired / التحقق من انتهاء الصلاحية"""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary / التحويل إلى قاموس"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "relevance": self.relevance.value,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        """Create from dictionary / الإنشاء من قاموس"""
        return cls(
            id=data["id"],
            tenant_id=data["tenant_id"],
            field_id=data.get("field_id"),
            memory_type=MemoryType(data["memory_type"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            relevance=RelevanceScore(data["relevance"]),
            embedding=data.get("embedding"),
            expires_at=(
                datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
            ),
        )


@dataclass
class RecallResult:
    """
    Result of a memory recall operation.
    نتيجة عملية استرجاع الذاكرة

    Attributes:
        entries: الإدخالات - Retrieved memory entries
        total_found: إجمالي الموجود - Total matching entries
        query_time_ms: وقت الاستعلام - Query execution time in ms
        context_text: نص السياق - Formatted context text
    """

    entries: list[MemoryEntry]
    total_found: int
    query_time_ms: float
    context_text: str = ""

    @property
    def is_empty(self) -> bool:
        """Check if no entries found / التحقق من عدم وجود إدخالات"""
        return len(self.entries) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Farm Memory Class
# ─────────────────────────────────────────────────────────────────────────────


class FarmMemory:
    """
    Memory management for AI interactions with tenant isolation.
    إدارة الذاكرة للتفاعلات مع الذكاء الاصطناعي مع عزل المستأجرين

    Implements a sliding window approach for recent history while
    maintaining full history within configured limits.

    يُنفذ نهج النافذة المنزلقة للسجل الأخير مع الحفاظ على
    السجل الكامل ضمن الحدود المُعدة.

    Features:
    - Tenant isolation: Each tenant has separate memory space
    - Sliding window: Recent entries always accessible
    - TTL-based expiration: Automatic cleanup of old entries
    - Relevance scoring: Prioritize important memories
    - Context retrieval: Get relevant context for AI queries

    المميزات:
    - عزل المستأجرين: كل مستأجر له مساحة ذاكرة منفصلة
    - النافذة المنزلقة: الإدخالات الأخيرة دائماً متاحة
    - انتهاء الصلاحية: التنظيف التلقائي للإدخالات القديمة
    - تقييم الصلة: إعطاء الأولوية للذكريات المهمة
    - استرجاع السياق: الحصول على السياق ذي الصلة للاستعلامات

    Example:
        >>> memory = FarmMemory()
        >>> memory.store(
        ...     tenant_id="tenant_123",
        ...     content={"observation": "Wheat showing yellow tips"},
        ...     memory_type=MemoryType.OBSERVATION,
        ...     field_id="field_456"
        ... )
        >>> result = memory.recall(
        ...     tenant_id="tenant_123",
        ...     field_id="field_456",
        ...     memory_types=[MemoryType.OBSERVATION]
        ... )
    """

    def __init__(
        self,
        config: MemoryConfig | None = None,
        storage_backend: Any = None,
    ):
        """
        Initialize farm memory.
        تهيئة ذاكرة المزرعة

        Args:
            config: الإعدادات - Memory configuration
            storage_backend: الواجهة الخلفية - Optional external storage
        """
        self.config = config or MemoryConfig()
        self.storage_backend = storage_backend

        # In-memory storage: tenant_id -> list of entries
        self._memory: dict[str, list[MemoryEntry]] = defaultdict(list)

        # Index for faster field lookups: (tenant_id, field_id) -> entry ids
        self._field_index: dict[tuple[str, str | None], set[str]] = defaultdict(set)

        # Statistics
        self._stats = {
            "stores": 0,
            "recalls": 0,
            "forgets": 0,
            "expirations": 0,
        }

        logger.info(
            f"FarmMemory initialized with window_size={self.config.window_size}, "
            f"max_entries={self.config.max_entries}"
        )

    def store(
        self,
        tenant_id: str,
        content: dict[str, Any] | str,
        memory_type: MemoryType = MemoryType.OBSERVATION,
        field_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        relevance: RelevanceScore = RelevanceScore.MEDIUM,
        ttl_hours: int | None = None,
    ) -> MemoryEntry:
        """
        Store a new memory entry.
        تخزين إدخال ذاكرة جديد

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
            content: المحتوى - Content to store
            memory_type: نوع الذاكرة - Type of memory
            field_id: معرف الحقل - Optional field identifier
            metadata: البيانات الوصفية - Optional metadata
            relevance: الصلة - Relevance score
            ttl_hours: مدة الصلاحية - Override default TTL

        Returns:
            MemoryEntry: الإدخال المُخزن - The stored entry

        Example:
            >>> entry = memory.store(
            ...     tenant_id="t1",
            ...     content={"action": "irrigation", "duration": "30min"},
            ...     memory_type=MemoryType.ACTION,
            ...     field_id="f1"
            ... )
        """
        ttl = ttl_hours if ttl_hours is not None else self.config.ttl_hours

        entry = MemoryEntry.create(
            tenant_id=tenant_id,
            memory_type=memory_type,
            content=content,
            field_id=field_id,
            metadata=metadata,
            relevance=relevance,
            ttl_hours=ttl,
        )

        # Add to memory
        self._memory[tenant_id].append(entry)

        # Update field index
        self._field_index[(tenant_id, field_id)].add(entry.id)

        # Enforce limits
        self._enforce_limits(tenant_id)

        # Clean expired entries periodically
        if self._stats["stores"] % 100 == 0:
            self._cleanup_expired(tenant_id)

        self._stats["stores"] += 1

        logger.debug(
            f"Stored memory entry: tenant={tenant_id}, type={memory_type.value}, "
            f"field={field_id}, id={entry.id}"
        )

        # Persist if configured
        if self.config.persist_to_storage and self.storage_backend:
            self._persist_entry(entry)

        return entry

    def recall(
        self,
        tenant_id: str,
        field_id: str | None = None,
        memory_types: list[MemoryType] | None = None,
        min_relevance: RelevanceScore | None = None,
        limit: int | None = None,
        since: datetime | None = None,
        include_expired: bool = False,
    ) -> RecallResult:
        """
        Recall memory entries.
        استرجاع إدخالات الذاكرة

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
            field_id: معرف الحقل - Filter by field
            memory_types: أنواع الذاكرة - Filter by memory types
            min_relevance: الحد الأدنى للصلة - Minimum relevance score
            limit: الحد الأقصى - Maximum entries to return
            since: منذ - Only entries after this time
            include_expired: تضمين المنتهية - Include expired entries

        Returns:
            RecallResult: نتيجة الاسترجاع - Recall result with entries

        Example:
            >>> result = memory.recall(
            ...     tenant_id="t1",
            ...     field_id="f1",
            ...     memory_types=[MemoryType.OBSERVATION, MemoryType.ACTION],
            ...     limit=10
            ... )
            >>> for entry in result.entries:
            ...     print(entry.content)
        """
        start_time = time.time()

        entries = self._memory.get(tenant_id, [])

        # Apply filters
        filtered = self._filter_entries(
            entries=entries,
            field_id=field_id,
            memory_types=memory_types,
            min_relevance=min_relevance,
            since=since,
            include_expired=include_expired,
        )

        total_found = len(filtered)

        # Sort by timestamp (most recent first) and relevance
        sorted_entries = sorted(
            filtered,
            key=lambda e: (
                self._relevance_to_int(e.relevance),
                e.timestamp,
            ),
            reverse=True,
        )

        # Apply limit
        limit = limit or self.config.window_size
        result_entries = sorted_entries[:limit]

        query_time = (time.time() - start_time) * 1000

        self._stats["recalls"] += 1

        logger.debug(
            f"Recalled {len(result_entries)} entries for tenant={tenant_id}, "
            f"field={field_id}, found={total_found}, time={query_time:.2f}ms"
        )

        return RecallResult(
            entries=result_entries,
            total_found=total_found,
            query_time_ms=query_time,
            context_text=self._entries_to_context(result_entries),
        )

    def forget(
        self,
        tenant_id: str,
        entry_id: str | None = None,
        field_id: str | None = None,
        memory_types: list[MemoryType] | None = None,
        before: datetime | None = None,
    ) -> int:
        """
        Forget (delete) memory entries.
        نسيان (حذف) إدخالات الذاكرة

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
            entry_id: معرف الإدخال - Specific entry to forget
            field_id: معرف الحقل - Forget all for field
            memory_types: أنواع الذاكرة - Forget specific types
            before: قبل - Forget entries before this time

        Returns:
            int: عدد الإدخالات المحذوفة - Number of entries forgotten

        Example:
            >>> # Forget a specific entry
            >>> memory.forget(tenant_id="t1", entry_id="entry_123")
            >>> # Forget all entries for a field
            >>> memory.forget(tenant_id="t1", field_id="f1")
            >>> # Forget old entries
            >>> memory.forget(tenant_id="t1", before=datetime.now() - timedelta(days=7))
        """
        if tenant_id not in self._memory:
            return 0

        entries = self._memory[tenant_id]
        original_count = len(entries)
        forgotten_count = 0

        # Filter entries to keep
        entries_to_keep = []
        for entry in entries:
            should_forget = False

            if (entry_id and entry.id == entry_id) or (
                field_id and entry.field_id == field_id
            ):
                should_forget = True
            elif memory_types and entry.memory_type in memory_types:
                if field_id is None or entry.field_id == field_id:
                    should_forget = True
            elif before and entry.timestamp < before:
                should_forget = True

            if should_forget:
                # Remove from field index
                self._field_index[(tenant_id, entry.field_id)].discard(entry.id)
                forgotten_count += 1
            else:
                entries_to_keep.append(entry)

        self._memory[tenant_id] = entries_to_keep
        self._stats["forgets"] += forgotten_count

        logger.info(
            f"Forgot {forgotten_count} entries for tenant={tenant_id}, "
            f"remaining={len(entries_to_keep)}"
        )

        return forgotten_count

    def get_relevant_context(
        self,
        tenant_id: str,
        query: str,
        field_id: str | None = None,
        max_tokens: int = 2000,
        memory_types: list[MemoryType] | None = None,
    ) -> str:
        """
        Get relevant context for an AI query.
        الحصول على السياق ذي الصلة لاستعلام الذكاء الاصطناعي

        Retrieves and formats memory entries most relevant to the given query.
        Uses keyword matching and recency to determine relevance.

        يسترجع ويُنسق إدخالات الذاكرة الأكثر صلة بالاستعلام المحدد.
        يستخدم مطابقة الكلمات المفتاحية والحداثة لتحديد الصلة.

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
            query: الاستعلام - User query for relevance matching
            field_id: معرف الحقل - Filter by field
            max_tokens: الحد الأقصى للرموز - Maximum tokens in context
            memory_types: أنواع الذاكرة - Filter by memory types

        Returns:
            str: السياق المُنسق - Formatted context string

        Example:
            >>> context = memory.get_relevant_context(
            ...     tenant_id="t1",
            ...     query="What is the irrigation status?",
            ...     field_id="f1",
            ...     max_tokens=1500
            ... )
            >>> prompt = f"Context:\\n{context}\\n\\nQuestion: {query}"
        """
        from .compression import estimate_tokens

        # Recall all relevant entries
        result = self.recall(
            tenant_id=tenant_id,
            field_id=field_id,
            memory_types=memory_types,
            limit=self.config.window_size * 2,  # Get more for filtering
        )

        if result.is_empty:
            return ""

        # Score entries by relevance to query
        scored_entries = [
            (entry, self._calculate_relevance_score(entry, query))
            for entry in result.entries
        ]

        # Sort by relevance score
        scored_entries.sort(key=lambda x: x[1], reverse=True)

        # Build context within token limit
        context_parts = []
        current_tokens = 0

        for entry, score in scored_entries:
            entry_text = self._format_entry_for_context(entry)
            entry_tokens = estimate_tokens(entry_text)

            if current_tokens + entry_tokens > max_tokens:
                break

            context_parts.append(entry_text)
            current_tokens += entry_tokens

        context = "\n---\n".join(context_parts)

        logger.debug(
            f"Generated context for tenant={tenant_id}: "
            f"{len(context_parts)} entries, ~{current_tokens} tokens"
        )

        return context

    def get_sliding_window(
        self,
        tenant_id: str,
        field_id: str | None = None,
    ) -> list[MemoryEntry]:
        """
        Get the sliding window of recent entries.
        الحصول على النافذة المنزلقة للإدخالات الأخيرة

        Args:
            tenant_id: معرف المستأجر - Tenant identifier
            field_id: معرف الحقل - Filter by field

        Returns:
            list[MemoryEntry]: الإدخالات الأخيرة - Recent entries
        """
        result = self.recall(
            tenant_id=tenant_id,
            field_id=field_id,
            limit=self.config.window_size,
        )
        return result.entries

    def get_stats(self) -> dict[str, Any]:
        """
        Get memory statistics.
        الحصول على إحصائيات الذاكرة

        Returns:
            dict: الإحصائيات - Memory statistics
        """
        total_entries = sum(len(entries) for entries in self._memory.values())
        tenant_count = len(self._memory)

        return {
            **self._stats,
            "total_entries": total_entries,
            "tenant_count": tenant_count,
            "avg_entries_per_tenant": total_entries / max(tenant_count, 1),
        }

    def clear_tenant(self, tenant_id: str) -> int:
        """
        Clear all memory for a tenant.
        مسح كل الذاكرة للمستأجر

        Args:
            tenant_id: معرف المستأجر - Tenant identifier

        Returns:
            int: عدد الإدخالات المحذوفة - Number of entries cleared
        """
        if tenant_id not in self._memory:
            return 0

        count = len(self._memory[tenant_id])

        # Clear field index entries
        keys_to_remove = [k for k in self._field_index if k[0] == tenant_id]
        for key in keys_to_remove:
            del self._field_index[key]

        del self._memory[tenant_id]

        logger.info(f"Cleared {count} entries for tenant={tenant_id}")
        return count

    # ─────────────────────────────────────────────────────────────────────────
    # Private Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _filter_entries(
        self,
        entries: list[MemoryEntry],
        field_id: str | None,
        memory_types: list[MemoryType] | None,
        min_relevance: RelevanceScore | None,
        since: datetime | None,
        include_expired: bool,
    ) -> list[MemoryEntry]:
        """Filter entries based on criteria"""
        result = []

        for entry in entries:
            # Skip expired unless requested
            if not include_expired and entry.is_expired():
                continue

            # Filter by field_id
            if field_id is not None and entry.field_id != field_id:
                continue

            # Filter by memory type
            if memory_types and entry.memory_type not in memory_types:
                continue

            # Filter by relevance
            if min_relevance:
                if self._relevance_to_int(entry.relevance) < self._relevance_to_int(
                    min_relevance
                ):
                    continue

            # Filter by time
            if since and entry.timestamp < since:
                continue

            result.append(entry)

        return result

    def _relevance_to_int(self, relevance: RelevanceScore) -> int:
        """Convert relevance score to integer for sorting"""
        mapping = {
            RelevanceScore.CRITICAL: 4,
            RelevanceScore.HIGH: 3,
            RelevanceScore.MEDIUM: 2,
            RelevanceScore.LOW: 1,
        }
        return mapping.get(relevance, 0)

    def _enforce_limits(self, tenant_id: str) -> None:
        """Enforce max entries limit for tenant"""
        entries = self._memory.get(tenant_id, [])

        if len(entries) > self.config.max_entries:
            # Remove oldest low-relevance entries first
            entries.sort(
                key=lambda e: (self._relevance_to_int(e.relevance), e.timestamp)
            )

            # Keep the most relevant/recent entries
            entries_to_remove = entries[: len(entries) - self.config.max_entries]
            entries_to_keep = entries[len(entries) - self.config.max_entries :]

            # Update index
            for entry in entries_to_remove:
                self._field_index[(tenant_id, entry.field_id)].discard(entry.id)

            self._memory[tenant_id] = entries_to_keep

            logger.debug(
                f"Enforced limits for tenant={tenant_id}: removed {len(entries_to_remove)}"
            )

    def _cleanup_expired(self, tenant_id: str) -> int:
        """Remove expired entries"""
        if tenant_id not in self._memory:
            return 0

        entries = self._memory[tenant_id]
        original_count = len(entries)

        valid_entries = []
        for entry in entries:
            if entry.is_expired():
                self._field_index[(tenant_id, entry.field_id)].discard(entry.id)
                self._stats["expirations"] += 1
            else:
                valid_entries.append(entry)

        self._memory[tenant_id] = valid_entries
        removed = original_count - len(valid_entries)

        if removed > 0:
            logger.debug(f"Cleaned up {removed} expired entries for tenant={tenant_id}")

        return removed

    def _calculate_relevance_score(self, entry: MemoryEntry, query: str) -> float:
        """Calculate relevance score for entry against query"""
        score = 0.0

        # Base score from relevance level
        score += self._relevance_to_int(entry.relevance) * 0.25

        # Recency bonus (entries from last 24h get bonus)
        hours_old = (datetime.now(UTC) - entry.timestamp).total_seconds() / 3600
        recency_bonus = max(0, 1 - (hours_old / 24)) * 0.3
        score += recency_bonus

        # Keyword matching
        query_lower = query.lower()
        content_str = str(entry.content).lower()

        # Extract keywords from query
        keywords = set(query_lower.split())
        keywords.discard("")

        if keywords:
            matches = sum(1 for kw in keywords if kw in content_str)
            keyword_score = (matches / len(keywords)) * 0.45
            score += keyword_score

        return min(score, 1.0)

    def _entries_to_context(self, entries: list[MemoryEntry]) -> str:
        """Convert entries to context text"""
        if not entries:
            return ""

        parts = [self._format_entry_for_context(entry) for entry in entries]
        return "\n---\n".join(parts)

    def _format_entry_for_context(self, entry: MemoryEntry) -> str:
        """Format a single entry for context"""
        lines = []

        # Header
        time_str = entry.timestamp.strftime("%Y-%m-%d %H:%M")
        lines.append(f"[{entry.memory_type.value.upper()}] {time_str}")

        # Field reference if present
        if entry.field_id:
            lines.append(f"Field: {entry.field_id}")

        # Content
        if isinstance(entry.content, dict):
            for key, value in entry.content.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append(f"  {entry.content}")

        return "\n".join(lines)

    def _persist_entry(self, entry: MemoryEntry) -> None:
        """Persist entry to external storage"""
        if self.storage_backend:
            try:
                self.storage_backend.save(entry.to_dict())
            except Exception as e:
                logger.error(f"Failed to persist entry {entry.id}: {e}")

    def _content_hash(self, content: Any) -> str:
        """Generate hash for content deduplication"""
        import json

        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
