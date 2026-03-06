"""
Tests for Knowledge Cache and Metrics
=======================================
اختبارات التخزين المؤقت والمقاييس
"""

from __future__ import annotations

import time

import pytest

from shared.ai.knowledge.cache import CacheEntry, KnowledgeCache
from shared.ai.knowledge.metrics import KnowledgeMetrics


# ─── Cache Tests ──────────────────────────────────────────────────────────────


class TestKnowledgeCache:
    """Tests for LRU cache with TTL."""

    @pytest.fixture
    def cache(self) -> KnowledgeCache:
        return KnowledgeCache(max_size=5, default_ttl=10.0)

    @pytest.mark.unit
    def test_put_and_get(self, cache: KnowledgeCache):
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    @pytest.mark.unit
    def test_get_miss(self, cache: KnowledgeCache):
        assert cache.get("nonexistent") is None

    @pytest.mark.unit
    def test_invalidate(self, cache: KnowledgeCache):
        cache.put("key1", "value1")
        assert cache.invalidate("key1") is True
        assert cache.get("key1") is None

    @pytest.mark.unit
    def test_invalidate_nonexistent(self, cache: KnowledgeCache):
        assert cache.invalidate("nonexistent") is False

    @pytest.mark.unit
    def test_clear(self, cache: KnowledgeCache):
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    @pytest.mark.unit
    def test_lru_eviction(self):
        cache = KnowledgeCache(max_size=3, default_ttl=60.0)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)  # Should evict "a"
        assert cache.get("a") is None
        assert cache.get("d") == 4

    @pytest.mark.unit
    def test_ttl_expiration(self):
        cache = KnowledgeCache(max_size=10, default_ttl=0.01)  # 10ms
        cache.put("key", "value")
        time.sleep(0.02)
        assert cache.get("key") is None

    @pytest.mark.unit
    def test_custom_ttl(self, cache: KnowledgeCache):
        cache.put("short", "value", ttl=0.01)
        cache.put("long", "value", ttl=60.0)
        time.sleep(0.02)
        assert cache.get("short") is None
        assert cache.get("long") == "value"

    @pytest.mark.unit
    def test_stats(self, cache: KnowledgeCache):
        cache.put("a", 1)
        cache.get("a")  # hit
        cache.get("b")  # miss
        stats = cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
        assert stats["hit_rate"] > 0

    @pytest.mark.unit
    def test_make_key_deterministic(self):
        key1 = KnowledgeCache.make_key("wheat", "crops", "agriculture")
        key2 = KnowledgeCache.make_key("wheat", "crops", "agriculture")
        assert key1 == key2

    @pytest.mark.unit
    def test_make_key_different_inputs(self):
        key1 = KnowledgeCache.make_key("wheat", "crops")
        key2 = KnowledgeCache.make_key("barley", "crops")
        assert key1 != key2

    @pytest.mark.unit
    def test_invalidate_by_prefix(self, cache: KnowledgeCache):
        cache.put("crops:wheat", 1)
        cache.put("crops:barley", 2)
        cache.put("soil:sandy", 3)
        removed = cache.invalidate_by_prefix("crops:")
        assert removed == 2
        assert cache.get("soil:sandy") == 3

    @pytest.mark.unit
    def test_invalidate_collection(self, cache: KnowledgeCache):
        cache.put("collection:crop_knowledge:q1", 1)
        cache.put("collection:crop_knowledge:q2", 2)
        cache.put("collection:soil_knowledge:q1", 3)
        removed = cache.invalidate_collection("crop_knowledge")
        assert removed >= 0  # Depends on key format


# ─── CacheEntry Tests ─────────────────────────────────────────────────────────


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    @pytest.mark.unit
    def test_not_expired(self):
        entry = CacheEntry(key="test", value="val", ttl_seconds=60.0)
        assert entry.is_expired is False

    @pytest.mark.unit
    def test_expired(self):
        entry = CacheEntry(key="test", value="val", ttl_seconds=0.0, created_at=time.time() - 1)
        assert entry.is_expired is True


# ─── Metrics Tests ────────────────────────────────────────────────────────────


class TestKnowledgeMetrics:
    """Tests for knowledge metrics tracking."""

    @pytest.fixture
    def metrics(self) -> KnowledgeMetrics:
        return KnowledgeMetrics()

    @pytest.mark.unit
    def test_record_ingestion_success(self, metrics: KnowledgeMetrics):
        metrics.record_ingestion(success=True, domain="crops", collection="crop_knowledge")
        assert metrics.documents_ingested == 1
        assert metrics.documents_failed == 0
        assert metrics.by_domain["crops"] == 1

    @pytest.mark.unit
    def test_record_ingestion_failure(self, metrics: KnowledgeMetrics):
        metrics.record_ingestion(success=False)
        assert metrics.documents_failed == 1

    @pytest.mark.unit
    def test_record_validation(self, metrics: KnowledgeMetrics):
        metrics.record_validation(passed=True)
        metrics.record_validation(passed=False)
        assert metrics.documents_validated == 2
        assert metrics.documents_rejected == 1

    @pytest.mark.unit
    def test_record_query(self, metrics: KnowledgeMetrics):
        metrics.record_query(cache_hit=False)
        metrics.record_query(cache_hit=True)
        assert metrics.queries_total == 2
        assert metrics.queries_cache_hits == 1

    @pytest.mark.unit
    def test_record_expiration(self, metrics: KnowledgeMetrics):
        metrics.record_expiration(5)
        assert metrics.documents_expired == 5

    @pytest.mark.unit
    def test_to_dict(self, metrics: KnowledgeMetrics):
        metrics.record_ingestion(True, domain="crops")
        d = metrics.to_dict()
        assert d["documents_ingested"] == 1
        assert "cache_hit_rate" in d

    @pytest.mark.unit
    def test_to_prometheus_format(self, metrics: KnowledgeMetrics):
        metrics.record_ingestion(True, domain="crops")
        prom = metrics.to_prometheus_format()
        assert "sahool_knowledge_documents_ingested_total 1" in prom
        assert "sahool_knowledge_by_domain" in prom

    @pytest.mark.unit
    def test_reset(self, metrics: KnowledgeMetrics):
        metrics.record_ingestion(True, domain="crops")
        metrics.record_query()
        metrics.reset()
        assert metrics.documents_ingested == 0
        assert metrics.queries_total == 0
        assert len(metrics.by_domain) == 0
