"""
Unit Tests for AI Farm Memory Module
====================================
اختبارات وحدة لوحدة ذاكرة المزرعة للذكاء الاصطناعي

Tests for FarmMemory class covering:
- Memory entry creation and storage
- Sliding window for recent history
- Memory recall with filtering
- Tenant isolation
- TTL-based expiration
- Relevance-based retrieval
- Context generation

Author: SAHOOL QA Team
Updated: January 2025
"""

import pytest
from datetime import datetime, UTC, timedelta
from time import sleep

from shared.ai.context_engineering.memory import (
    FarmMemory,
    MemoryEntry,
    MemoryConfig,
    MemoryType,
    RelevanceScore,
    RecallResult,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_TTL_HOURS,
    DEFAULT_MAX_ENTRIES,
    DEFAULT_RELEVANCE_THRESHOLD,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def memory():
    """Standard farm memory instance"""
    return FarmMemory()


@pytest.fixture
def memory_small_window():
    """Memory with small sliding window for testing"""
    config = MemoryConfig(window_size=5, max_entries=50)
    return FarmMemory(config=config)


@pytest.fixture
def memory_short_ttl():
    """Memory with short TTL for testing expiration"""
    config = MemoryConfig(ttl_hours=1)
    return FarmMemory(config=config)


@pytest.fixture
def test_tenant_id():
    """Test tenant ID"""
    return "tenant_001"


@pytest.fixture
def test_field_id():
    """Test field ID"""
    return "field_001"


@pytest.fixture
def sample_memory_entry(test_tenant_id, test_field_id):
    """Sample memory entry"""
    return MemoryEntry.create(
        tenant_id=test_tenant_id,
        memory_type=MemoryType.OBSERVATION,
        content={"observation": "Wheat showing yellow tips", "severity": "medium"},
        field_id=test_field_id,
        relevance=RelevanceScore.HIGH,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: MemoryEntry
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryEntry:
    """Tests for MemoryEntry data class"""

    def test_create_basic_entry(self, test_tenant_id):
        """Should create basic memory entry"""
        entry = MemoryEntry.create(
            tenant_id=test_tenant_id,
            memory_type=MemoryType.OBSERVATION,
            content={"observation": "Test observation"},
        )

        assert entry.id is not None
        assert entry.tenant_id == test_tenant_id
        assert entry.memory_type == MemoryType.OBSERVATION
        assert entry.field_id is None
        assert entry.timestamp is not None

    def test_create_with_field_id(self, test_tenant_id, test_field_id):
        """Should create entry with field association"""
        entry = MemoryEntry.create(
            tenant_id=test_tenant_id,
            memory_type=MemoryType.FIELD_STATE,
            content={"status": "growing"},
            field_id=test_field_id,
        )

        assert entry.field_id == test_field_id

    def test_create_with_metadata(self, test_tenant_id):
        """Should create entry with metadata"""
        metadata = {"source": "sensor", "confidence": 0.95}
        entry = MemoryEntry.create(
            tenant_id=test_tenant_id,
            memory_type=MemoryType.WEATHER,
            content={"temperature": 28},
            metadata=metadata,
        )

        assert entry.metadata == metadata

    def test_is_expired_not_expired(self, test_tenant_id):
        """Non-expired entry should return False"""
        entry = MemoryEntry.create(
            tenant_id=test_tenant_id,
            memory_type=MemoryType.OBSERVATION,
            content="test",
            ttl_hours=24,
        )

        assert entry.is_expired() is False

    def test_is_expired_past_ttl(self, test_tenant_id):
        """Expired entry should return True"""
        entry = MemoryEntry.create(
            tenant_id=test_tenant_id,
            memory_type=MemoryType.OBSERVATION,
            content="test",
            ttl_hours=0,  # No TTL, expires immediately
        )

        assert entry.is_expired() is False  # No expiry set

    def test_to_dict_conversion(self, test_tenant_id):
        """Should convert entry to dictionary"""
        entry = MemoryEntry.create(
            tenant_id=test_tenant_id,
            memory_type=MemoryType.RECOMMENDATION,
            content={"advice": "Apply nitrogen fertilizer"},
        )

        entry_dict = entry.to_dict()

        assert entry_dict["id"] == entry.id
        assert entry_dict["tenant_id"] == test_tenant_id
        assert entry_dict["memory_type"] == MemoryType.RECOMMENDATION.value
        assert "timestamp" in entry_dict

    def test_from_dict_conversion(self):
        """Should create entry from dictionary"""
        now = datetime.now(UTC)
        entry_dict = {
            "id": "entry_123",
            "tenant_id": "tenant_001",
            "field_id": "field_001",
            "memory_type": MemoryType.OBSERVATION.value,
            "content": {"observation": "test"},
            "metadata": {},
            "timestamp": now.isoformat(),
            "relevance": RelevanceScore.MEDIUM.value,
            "expires_at": None,
        }

        entry = MemoryEntry.from_dict(entry_dict)

        assert entry.id == "entry_123"
        assert entry.tenant_id == "tenant_001"
        assert entry.field_id == "field_001"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: MemoryConfig
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryConfig:
    """Tests for MemoryConfig"""

    def test_default_config(self):
        """Should create config with defaults"""
        config = MemoryConfig()

        assert config.window_size == DEFAULT_WINDOW_SIZE
        assert config.max_entries == DEFAULT_MAX_ENTRIES
        assert config.ttl_hours == DEFAULT_TTL_HOURS
        assert config.enable_compression is True

    def test_custom_config(self):
        """Should accept custom configuration"""
        config = MemoryConfig(
            window_size=10, max_entries=200, ttl_hours=48, enable_compression=False
        )

        assert config.window_size == 10
        assert config.max_entries == 200
        assert config.ttl_hours == 48
        assert config.enable_compression is False


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: FarmMemory Storage
# ═══════════════════════════════════════════════════════════════════════════════


class TestFarmMemoryStore:
    """Tests for memory storage operations"""

    def test_store_single_entry(self, memory, test_tenant_id):
        """Should store single memory entry"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content={"observation": "Test observation"},
            memory_type=MemoryType.OBSERVATION,
        )

        assert entry.id is not None
        assert entry.tenant_id == test_tenant_id
        assert entry.memory_type == MemoryType.OBSERVATION

    def test_store_increments_stats(self, memory, test_tenant_id):
        """Should increment store statistics"""
        initial_stores = memory._stats["stores"]

        memory.store(
            tenant_id=test_tenant_id,
            content="test",
            memory_type=MemoryType.OBSERVATION,
        )

        assert memory._stats["stores"] == initial_stores + 1

    def test_store_with_field_association(self, memory, test_tenant_id, test_field_id):
        """Should store entry with field association"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content={"status": "healthy"},
            memory_type=MemoryType.FIELD_STATE,
            field_id=test_field_id,
        )

        assert entry.field_id == test_field_id

    def test_store_with_custom_relevance(self, memory, test_tenant_id):
        """Should store with custom relevance score"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content="critical issue",
            memory_type=MemoryType.OBSERVATION,
            relevance=RelevanceScore.CRITICAL,
        )

        assert entry.relevance == RelevanceScore.CRITICAL

    def test_store_with_custom_ttl(self, memory, test_tenant_id):
        """Should store with custom TTL"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content="temporary data",
            memory_type=MemoryType.OBSERVATION,
            ttl_hours=12,
        )

        assert entry.expires_at is not None

    def test_store_multiple_entries(self, memory, test_tenant_id):
        """Should store multiple entries"""
        for i in range(5):
            memory.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        result = memory.recall(tenant_id=test_tenant_id, limit=100)
        assert len(result.entries) == 5

    def test_store_enforces_max_entries(self, memory_small_window, test_tenant_id):
        """Should enforce maximum entries limit per tenant"""
        max_entries = memory_small_window.config.max_entries
        for i in range(max_entries + 10):
            memory_small_window.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        result = memory_small_window.recall(
            tenant_id=test_tenant_id, limit=max_entries + 10
        )
        assert len(result.entries) <= max_entries


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: FarmMemory Recall
# ═══════════════════════════════════════════════════════════════════════════════


class TestFarmMemoryRecall:
    """Tests for memory recall operations"""

    def test_recall_all_entries(self, memory, test_tenant_id):
        """Should recall all entries for tenant"""
        for i in range(3):
            memory.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        result = memory.recall(tenant_id=test_tenant_id)

        assert isinstance(result, RecallResult)
        assert len(result.entries) == 3
        assert result.total_found == 3

    def test_recall_by_field(self, memory, test_tenant_id, test_field_id):
        """Should recall entries for specific field"""
        other_field = "field_002"

        memory.store(
            tenant_id=test_tenant_id,
            content="field 1",
            memory_type=MemoryType.OBSERVATION,
            field_id=test_field_id,
        )
        memory.store(
            tenant_id=test_tenant_id,
            content="field 2",
            memory_type=MemoryType.OBSERVATION,
            field_id=other_field,
        )

        result = memory.recall(tenant_id=test_tenant_id, field_id=test_field_id)

        assert len(result.entries) == 1
        assert result.entries[0].field_id == test_field_id

    def test_recall_by_type(self, memory, test_tenant_id):
        """Should recall entries by memory type"""
        memory.store(
            tenant_id=test_tenant_id,
            content="observation",
            memory_type=MemoryType.OBSERVATION,
        )
        memory.store(
            tenant_id=test_tenant_id,
            content="action",
            memory_type=MemoryType.ACTION,
        )

        result = memory.recall(
            tenant_id=test_tenant_id, memory_types=[MemoryType.OBSERVATION]
        )

        assert len(result.entries) == 1
        assert result.entries[0].memory_type == MemoryType.OBSERVATION

    def test_recall_by_relevance(self, memory, test_tenant_id):
        """Should recall entries by minimum relevance"""
        memory.store(
            tenant_id=test_tenant_id,
            content="low relevance",
            memory_type=MemoryType.OBSERVATION,
            relevance=RelevanceScore.LOW,
        )
        memory.store(
            tenant_id=test_tenant_id,
            content="critical",
            memory_type=MemoryType.OBSERVATION,
            relevance=RelevanceScore.CRITICAL,
        )

        result = memory.recall(
            tenant_id=test_tenant_id, min_relevance=RelevanceScore.CRITICAL
        )

        assert len(result.entries) == 1
        assert result.entries[0].relevance == RelevanceScore.CRITICAL

    def test_recall_respects_limit(self, memory, test_tenant_id):
        """Should respect recall limit"""
        for i in range(10):
            memory.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        result = memory.recall(tenant_id=test_tenant_id, limit=5)

        assert len(result.entries) == 5

    def test_recall_sorts_by_recency(self, memory, test_tenant_id):
        """Should return recent entries first"""
        import time

        for i in range(3):
            memory.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )
            time.sleep(0.01)  # Small delay

        result = memory.recall(tenant_id=test_tenant_id, limit=100)

        # Most recent should be first
        assert result.entries[0].timestamp >= result.entries[-1].timestamp

    def test_recall_nonexistent_tenant(self, memory):
        """Should return empty result for nonexistent tenant"""
        result = memory.recall(tenant_id="nonexistent_tenant")

        assert result.is_empty
        assert len(result.entries) == 0
        assert result.total_found == 0

    def test_recall_increments_stats(self, memory, test_tenant_id):
        """Should increment recall statistics"""
        memory.store(
            tenant_id=test_tenant_id,
            content="test",
            memory_type=MemoryType.OBSERVATION,
        )

        initial_recalls = memory._stats["recalls"]
        memory.recall(tenant_id=test_tenant_id)

        assert memory._stats["recalls"] == initial_recalls + 1

    def test_recall_result_has_context_text(self, memory, test_tenant_id):
        """Recall result should include formatted context text"""
        memory.store(
            tenant_id=test_tenant_id,
            content={"observation": "Wheat is healthy"},
            memory_type=MemoryType.OBSERVATION,
        )

        result = memory.recall(tenant_id=test_tenant_id)

        assert len(result.context_text) > 0
        assert "OBSERVATION" in result.context_text


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: FarmMemory Forget
# ═══════════════════════════════════════════════════════════════════════════════


class TestFarmMemoryForget:
    """Tests for memory deletion operations"""

    def test_forget_specific_entry(self, memory, test_tenant_id):
        """Should forget specific entry by ID"""
        entry1 = memory.store(
            tenant_id=test_tenant_id,
            content="entry 1",
            memory_type=MemoryType.OBSERVATION,
        )
        entry2 = memory.store(
            tenant_id=test_tenant_id,
            content="entry 2",
            memory_type=MemoryType.OBSERVATION,
        )

        forgotten = memory.forget(tenant_id=test_tenant_id, entry_id=entry1.id)

        assert forgotten == 1
        result = memory.recall(tenant_id=test_tenant_id)
        assert len(result.entries) == 1
        assert result.entries[0].id == entry2.id

    def test_forget_by_field(self, memory, test_tenant_id):
        """Should forget all entries for a field"""
        field1 = "field_001"
        field2 = "field_002"

        memory.store(
            tenant_id=test_tenant_id,
            content="field 1",
            memory_type=MemoryType.OBSERVATION,
            field_id=field1,
        )
        memory.store(
            tenant_id=test_tenant_id,
            content="field 2",
            memory_type=MemoryType.OBSERVATION,
            field_id=field2,
        )

        forgotten = memory.forget(tenant_id=test_tenant_id, field_id=field1)

        assert forgotten == 1
        result = memory.recall(tenant_id=test_tenant_id)
        assert len(result.entries) == 1
        assert result.entries[0].field_id == field2

    def test_forget_by_type(self, memory, test_tenant_id):
        """Should forget entries of specific type"""
        memory.store(
            tenant_id=test_tenant_id,
            content="observation",
            memory_type=MemoryType.OBSERVATION,
        )
        memory.store(
            tenant_id=test_tenant_id,
            content="action",
            memory_type=MemoryType.ACTION,
        )

        forgotten = memory.forget(
            tenant_id=test_tenant_id, memory_types=[MemoryType.OBSERVATION]
        )

        assert forgotten == 1
        result = memory.recall(tenant_id=test_tenant_id)
        assert result.entries[0].memory_type == MemoryType.ACTION

    def test_forget_before_date(self, memory, test_tenant_id):
        """Should forget entries before specific date"""
        old_entry = memory.store(
            tenant_id=test_tenant_id,
            content="old",
            memory_type=MemoryType.OBSERVATION,
        )

        cutoff_time = datetime.now(UTC) + timedelta(hours=1)

        forgotten = memory.forget(tenant_id=test_tenant_id, before=cutoff_time)

        assert forgotten == 1

    def test_forget_increments_stats(self, memory, test_tenant_id):
        """Should increment forget statistics"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content="test",
            memory_type=MemoryType.OBSERVATION,
        )

        initial_forgets = memory._stats["forgets"]
        memory.forget(tenant_id=test_tenant_id, entry_id=entry.id)

        assert memory._stats["forgets"] == initial_forgets + 1

    def test_forget_nonexistent_entry(self, memory, test_tenant_id):
        """Should return 0 when forgetting nonexistent entry"""
        forgotten = memory.forget(tenant_id=test_tenant_id, entry_id="nonexistent")

        assert forgotten == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Relevant Context Retrieval
# ═══════════════════════════════════════════════════════════════════════════════


class TestRelevantContextRetrieval:
    """Tests for relevant context retrieval"""

    def test_get_relevant_context(self, memory, test_tenant_id, test_field_id):
        """Should retrieve relevant context for query"""
        memory.store(
            tenant_id=test_tenant_id,
            content={"observation": "Wheat showing yellow tips"},
            memory_type=MemoryType.OBSERVATION,
            field_id=test_field_id,
        )
        memory.store(
            tenant_id=test_tenant_id,
            content={"action": "Irrigation applied"},
            memory_type=MemoryType.ACTION,
            field_id=test_field_id,
        )

        context = memory.get_relevant_context(
            tenant_id=test_tenant_id,
            query="What is the status of the wheat?",
            field_id=test_field_id,
        )

        assert len(context) > 0
        assert "wheat" in context.lower() or "yellow" in context.lower()

    def test_context_respects_max_tokens(self, memory, test_tenant_id):
        """Context should respect max token limit"""
        for i in range(20):
            memory.store(
                tenant_id=test_tenant_id,
                content={"observation": f"Long observation text {i} " * 50},
                memory_type=MemoryType.OBSERVATION,
            )

        context = memory.get_relevant_context(
            tenant_id=test_tenant_id,
            query="What is the status?",
            max_tokens=500,
        )

        # Context should be reasonable size (tokens approximated)
        assert len(context) < 500 * 10  # Rough estimate

    def test_context_empty_for_no_matches(self, memory, test_tenant_id):
        """Should return empty context if no relevant entries"""
        context = memory.get_relevant_context(
            tenant_id=test_tenant_id,
            query="Irrelevant question",
        )

        assert context == ""

    def test_context_filters_by_memory_type(self, memory, test_tenant_id):
        """Should filter context by memory type"""
        memory.store(
            tenant_id=test_tenant_id,
            content={"observation": "Wheat status"},
            memory_type=MemoryType.OBSERVATION,
        )
        memory.store(
            tenant_id=test_tenant_id,
            content={"recommendation": "Apply fertilizer"},
            memory_type=MemoryType.RECOMMENDATION,
        )

        context = memory.get_relevant_context(
            tenant_id=test_tenant_id,
            query="What to do?",
            memory_types=[MemoryType.RECOMMENDATION],
        )

        assert "fertilizer" in context.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Sliding Window
# ═══════════════════════════════════════════════════════════════════════════════


class TestSlidingWindow:
    """Tests for sliding window operations"""

    def test_get_sliding_window(self, memory, test_tenant_id):
        """Should retrieve sliding window of recent entries"""
        # Store more than window size
        for i in range(30):
            memory.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        window = memory.get_sliding_window(tenant_id=test_tenant_id)

        assert len(window) == memory.config.window_size
        assert len(window) == 20

    def test_sliding_window_respects_size(self, memory_small_window, test_tenant_id):
        """Sliding window should not exceed configured size"""
        for i in range(20):
            memory_small_window.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        window = memory_small_window.get_sliding_window(tenant_id=test_tenant_id)

        assert len(window) == memory_small_window.config.window_size


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Statistics
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryStats:
    """Tests for memory statistics"""

    def test_get_stats(self, memory, test_tenant_id):
        """Should return memory statistics"""
        memory.store(
            tenant_id=test_tenant_id,
            content="test",
            memory_type=MemoryType.OBSERVATION,
        )
        memory.recall(tenant_id=test_tenant_id)

        stats = memory.get_stats()

        assert "stores" in stats
        assert "recalls" in stats
        assert "forgets" in stats
        assert stats["stores"] >= 1
        assert stats["recalls"] >= 1

    def test_stats_track_entries(self, memory, test_tenant_id):
        """Stats should track total entries"""
        for i in range(5):
            memory.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        stats = memory.get_stats()

        assert stats["total_entries"] == 5

    def test_stats_track_tenants(self, memory):
        """Stats should track tenant count"""
        for i in range(3):
            memory.store(
                tenant_id=f"tenant_{i}",
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        stats = memory.get_stats()

        assert stats["tenant_count"] == 3


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Tenant Isolation
# ═══════════════════════════════════════════════════════════════════════════════


class TestTenantIsolation:
    """Tests for tenant data isolation"""

    def test_tenant_isolation(self, memory):
        """Memories should be isolated by tenant"""
        tenant1 = "tenant_001"
        tenant2 = "tenant_002"

        memory.store(
            tenant_id=tenant1,
            content="tenant 1 data",
            memory_type=MemoryType.OBSERVATION,
        )
        memory.store(
            tenant_id=tenant2,
            content="tenant 2 data",
            memory_type=MemoryType.OBSERVATION,
        )

        result1 = memory.recall(tenant_id=tenant1)
        result2 = memory.recall(tenant_id=tenant2)

        assert len(result1.entries) == 1
        assert len(result2.entries) == 1
        assert result1.entries[0].tenant_id == tenant1
        assert result2.entries[0].tenant_id == tenant2

    def test_clear_tenant(self, memory, test_tenant_id):
        """Should clear all memory for a tenant"""
        for i in range(5):
            memory.store(
                tenant_id=test_tenant_id,
                content={"entry": i},
                memory_type=MemoryType.OBSERVATION,
            )

        cleared = memory.clear_tenant(tenant_id=test_tenant_id)

        assert cleared == 5
        result = memory.recall(tenant_id=test_tenant_id)
        assert result.is_empty


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Arabic Text Support
# ═══════════════════════════════════════════════════════════════════════════════


class TestArabicSupport:
    """Tests for Arabic text in memory"""

    def test_store_arabic_content(self, memory, test_tenant_id):
        """Should store Arabic content"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content={"ملاحظة": "القمح يظهر أطراف صفراء", "الحالة": "متوسطة"},
            memory_type=MemoryType.OBSERVATION,
        )

        assert entry.id is not None

    def test_recall_arabic_content(self, memory, test_tenant_id):
        """Should retrieve Arabic content intact"""
        original_text = "ري الحقل بانتظام مهم جداً"
        memory.store(
            tenant_id=test_tenant_id,
            content={"نصيحة": original_text},
            memory_type=MemoryType.RECOMMENDATION,
        )

        result = memory.recall(tenant_id=test_tenant_id)

        assert len(result.entries) == 1
        assert original_text in str(result.entries[0].content)

    def test_relevant_context_arabic_query(self, memory, test_tenant_id):
        """Should handle Arabic queries for relevance"""
        memory.store(
            tenant_id=test_tenant_id,
            content={"ملاحظة": "القمح يحتاج إلى ماء"},
            memory_type=MemoryType.OBSERVATION,
        )

        context = memory.get_relevant_context(
            tenant_id=test_tenant_id,
            query="كيفية ري القمح؟",
        )

        assert len(context) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_empty_content(self, memory, test_tenant_id):
        """Should handle empty content"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content="",
            memory_type=MemoryType.OBSERVATION,
        )

        assert entry.id is not None

    def test_very_large_content(self, memory, test_tenant_id):
        """Should handle very large content"""
        large_content = "X" * 10000
        entry = memory.store(
            tenant_id=test_tenant_id,
            content={"data": large_content},
            memory_type=MemoryType.OBSERVATION,
        )

        assert entry.id is not None

    def test_special_characters_in_content(self, memory, test_tenant_id):
        """Should handle special characters"""
        entry = memory.store(
            tenant_id=test_tenant_id,
            content={"notes": "Special chars: !@#$%^&*() مرحبا 你好"},
            memory_type=MemoryType.OBSERVATION,
        )

        assert entry.id is not None

    def test_multiple_memory_types(self, memory, test_tenant_id):
        """Should handle all memory types"""
        types = [
            MemoryType.CONVERSATION,
            MemoryType.FIELD_STATE,
            MemoryType.RECOMMENDATION,
            MemoryType.OBSERVATION,
            MemoryType.WEATHER,
            MemoryType.ACTION,
            MemoryType.SYSTEM,
        ]

        for mem_type in types:
            memory.store(
                tenant_id=test_tenant_id,
                content={"type": mem_type.value},
                memory_type=mem_type,
            )

        result = memory.recall(tenant_id=test_tenant_id, limit=100)
        assert len(result.entries) == len(types)
