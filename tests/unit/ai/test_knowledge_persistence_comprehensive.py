"""
Comprehensive tests for persistence, vector store, and cache modules.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest


def _make_doc(**kwargs):
    """Create a BaseKnowledgeDocument with defaults."""
    from shared.ai.knowledge.models import (
        BaseKnowledgeDocument,
        KnowledgeDomain,
        SourceCredibilityLevel,
        KnowledgeSourceMeta,
        GeospatialMetadata,
        VerificationStatus,
    )

    defaults = {
        "title": "Test Document",
        "title_ar": "وثيقة اختبار",
        "content": "Test content about agriculture.",
        "content_ar": "محتوى اختبار عن الزراعة.",
        "domain": KnowledgeDomain.CROPS,
        "tags": ["wheat", "crop"],
    }
    defaults.update(kwargs)
    return BaseKnowledgeDocument(**defaults)


# ═══════════════════════════════════════════════════════════════════════════════
# Persistence Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInMemoryRepositoryCRUD:
    """Full CRUD operations on InMemoryKnowledgeRepository."""

    def test_save_and_retrieve(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        doc = _make_doc()
        doc_id = repo.save(doc)
        assert doc_id == doc.id
        retrieved = repo.get_by_id(doc_id)
        assert retrieved is not None
        assert retrieved.title == "Test Document"

    def test_save_batch(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        docs = [_make_doc(title=f"Doc {i}") for i in range(5)]
        ids = repo.save_batch(docs)
        assert len(ids) == 5
        assert repo.count() == 5

    def test_get_nonexistent_returns_none(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        assert repo.get_by_id("nonexistent-id") is None

    def test_update_existing(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        doc = _make_doc()
        repo.save(doc)
        doc.title = "Updated Title"
        assert repo.update(doc) is True
        retrieved = repo.get_by_id(doc.id)
        assert retrieved.title == "Updated Title"

    def test_update_nonexistent_returns_false(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        doc = _make_doc()
        assert repo.update(doc) is False

    def test_delete_existing(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        doc = _make_doc()
        repo.save(doc)
        result = repo.delete(doc.id)
        assert result is True
        assert repo.get_by_id(doc.id) is None
        assert repo.count() == 0

    def test_delete_nonexistent_returns_false(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        result = repo.delete("nonexistent")
        assert result is False

    def test_count_all(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository

        repo = InMemoryKnowledgeRepository()
        for i in range(3):
            repo.save(_make_doc(title=f"Doc {i}"))
        assert repo.count() == 3

    def test_list_collections(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository
        from shared.ai.knowledge.models import KnowledgeDomain

        repo = InMemoryKnowledgeRepository()
        repo.save(_make_doc(domain=KnowledgeDomain.CROPS))
        repo.save(_make_doc(domain=KnowledgeDomain.SOIL))
        collections = repo.list_collections()
        assert len(collections) >= 1


@pytest.mark.unit
class TestDocumentQueryFilters:
    """Test all query filter combinations."""

    def _setup_repo(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository
        from shared.ai.knowledge.models import (
            KnowledgeDomain,
            GeospatialMetadata,
            KnowledgeSourceMeta,
            SourceCredibilityLevel,
            VerificationStatus,
        )

        repo = InMemoryKnowledgeRepository()
        repo.save(_make_doc(
            title="Wheat Guide",
            domain=KnowledgeDomain.CROPS,
            tags=["wheat", "cereals"],
            geospatial=GeospatialMetadata(applicable_regions=["yemen_highland"]),
            source=KnowledgeSourceMeta(credibility=SourceCredibilityLevel.INTERNATIONAL_ORGANIZATION),
            verification_status=VerificationStatus.APPROVED,
        ))
        repo.save(_make_doc(
            title="Soil pH Guide",
            domain=KnowledgeDomain.SOIL,
            tags=["soil", "ph"],
            geospatial=GeospatialMetadata(applicable_regions=["saudi_central"]),
            source=KnowledgeSourceMeta(credibility=SourceCredibilityLevel.COMMUNITY),
            verification_status=VerificationStatus.PENDING,
        ))
        return repo

    def test_filter_by_domain(self):
        from shared.ai.knowledge.persistence import DocumentQuery
        from shared.ai.knowledge.models import KnowledgeDomain

        repo = self._setup_repo()
        page = repo.find(DocumentQuery(domain=KnowledgeDomain.CROPS))
        assert page.total == 1
        assert page.items[0].title == "Wheat Guide"

    def test_filter_by_tags(self):
        from shared.ai.knowledge.persistence import DocumentQuery

        repo = self._setup_repo()
        page = repo.find(DocumentQuery(tags=["wheat"]))
        assert page.total == 1

    def test_filter_by_regions(self):
        from shared.ai.knowledge.persistence import DocumentQuery

        repo = self._setup_repo()
        page = repo.find(DocumentQuery(regions=["saudi_central"]))
        assert page.total == 1
        assert page.items[0].title == "Soil pH Guide"

    def test_filter_by_min_credibility(self):
        from shared.ai.knowledge.persistence import DocumentQuery

        repo = self._setup_repo()
        page = repo.find(DocumentQuery(min_credibility=4))
        assert page.total == 1  # Only INTERNATIONAL_ORGANIZATION (5)

    def test_filter_by_verification_status(self):
        from shared.ai.knowledge.persistence import DocumentQuery

        repo = self._setup_repo()
        page = repo.find(DocumentQuery(verification_status="approved"))
        assert page.total == 1

    def test_text_search(self):
        from shared.ai.knowledge.persistence import DocumentQuery

        repo = self._setup_repo()
        page = repo.find(DocumentQuery(text_search="wheat"))
        assert page.total == 1

    def test_pagination(self):
        from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository, DocumentQuery

        repo = InMemoryKnowledgeRepository()
        for i in range(10):
            repo.save(_make_doc(title=f"Doc {i}"))

        page = repo.find(DocumentQuery(limit=3, offset=0))
        assert len(page.items) == 3
        assert page.total == 10
        assert page.has_next is True

        page2 = repo.find(DocumentQuery(limit=3, offset=9))
        assert len(page2.items) == 1
        assert page2.has_next is False

    def test_combined_filters(self):
        from shared.ai.knowledge.persistence import DocumentQuery
        from shared.ai.knowledge.models import KnowledgeDomain

        repo = self._setup_repo()
        page = repo.find(DocumentQuery(
            domain=KnowledgeDomain.CROPS,
            tags=["wheat"],
            regions=["yemen_highland"],
        ))
        assert page.total == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Vector Store Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestKnowledgeVectorStoreComprehensive:
    """Comprehensive vector store tests."""

    def _mock_embedding_provider(self, dim=8):
        provider = MagicMock()
        counter = [0]

        def embed(text):
            counter[0] += 1
            # Generate a simple deterministic embedding
            return [float(hash(text + str(i)) % 100) / 100 for i in range(dim)]

        provider.embed = embed
        provider.embed_batch = lambda texts: [embed(t) for t in texts]
        return provider

    def test_store_document_without_chunks(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        provider = self._mock_embedding_provider()
        store = KnowledgeVectorStore(embedding_provider=provider)
        doc = _make_doc()
        ids = store.store_document(doc)
        assert len(ids) == 1

    def test_store_document_with_chunks(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore
        from shared.ai.knowledge.ingestion.chunker import TextChunk

        provider = self._mock_embedding_provider()
        store = KnowledgeVectorStore(embedding_provider=provider)
        doc = _make_doc()
        chunks = [
            TextChunk(content=f"Chunk {i}", chunk_index=i, total_chunks=3)
            for i in range(3)
        ]
        ids = store.store_document(doc, chunks=chunks)
        assert len(ids) == 3

    def test_search_returns_results(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        provider = self._mock_embedding_provider()
        store = KnowledgeVectorStore(embedding_provider=provider)
        doc = _make_doc(content="Wheat irrigation schedule for arid regions.")
        store.store_document(doc)

        results = store.search("wheat irrigation", top_k=5)
        assert len(results) >= 1
        assert results[0].document_id == doc.id

    def test_search_without_provider_returns_empty(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        store = KnowledgeVectorStore(embedding_provider=None)
        doc = _make_doc()
        store.store_document(doc)
        results = store.search("test")
        assert results == []

    def test_delete_document(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        provider = self._mock_embedding_provider()
        store = KnowledgeVectorStore(embedding_provider=provider)
        doc = _make_doc()
        store.store_document(doc)
        assert store.delete_document(doc.id) is True
        assert store.delete_document(doc.id) is False  # Already deleted

    def test_collection_stats(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        provider = self._mock_embedding_provider()
        store = KnowledgeVectorStore(embedding_provider=provider)
        doc = _make_doc()
        store.store_document(doc)
        stats = store.get_collection_stats()
        assert stats["total_vectors"] >= 1

    def test_collection_prefix(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        store = KnowledgeVectorStore(collection_prefix="test_")
        assert store._prefixed_collection("crops") == "test_crops"
        assert store._prefixed_collection("test_crops") == "test_crops"  # No double prefix

    def test_domain_filter_in_search(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore
        from shared.ai.knowledge.models import KnowledgeDomain

        provider = self._mock_embedding_provider()
        store = KnowledgeVectorStore(embedding_provider=provider)
        doc_crop = _make_doc(domain=KnowledgeDomain.CROPS)
        doc_soil = _make_doc(domain=KnowledgeDomain.SOIL, content="Soil analysis data.")
        store.store_document(doc_crop)
        store.store_document(doc_soil)

        results = store.search("test", domain_filter=KnowledgeDomain.CROPS)
        for r in results:
            assert r.metadata.get("domain") == "crops"

    def test_cosine_similarity_identical(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        sim = KnowledgeVectorStore._cosine_similarity([1.0, 0.0], [1.0, 0.0])
        assert abs(sim - 1.0) < 0.01

    def test_cosine_similarity_orthogonal(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        sim = KnowledgeVectorStore._cosine_similarity([1.0, 0.0], [0.0, 1.0])
        assert abs(sim) < 0.01

    def test_cosine_similarity_empty(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        assert KnowledgeVectorStore._cosine_similarity([], []) == 0.0

    def test_cosine_similarity_different_lengths(self):
        from shared.ai.knowledge.vector_store_integration import KnowledgeVectorStore

        assert KnowledgeVectorStore._cosine_similarity([1.0], [1.0, 0.0]) == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Cache Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestKnowledgeCacheComprehensive:
    """Comprehensive cache tests."""

    def test_put_and_get(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        cache.put("key1", {"data": "value"})
        assert cache.get("key1") == {"data": "value"}

    def test_cache_miss(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache(default_ttl=0.01)  # 10ms TTL
        cache.put("key1", "value1")
        time.sleep(0.02)
        assert cache.get("key1") is None

    def test_custom_ttl(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache(default_ttl=300)
        cache.put("short", "val", ttl=0.01)
        cache.put("long", "val", ttl=300)
        time.sleep(0.02)
        assert cache.get("short") is None
        assert cache.get("long") == "val"

    def test_lru_eviction(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache(max_size=3)
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        cache.put("k3", "v3")
        # Access k1 to make it most recently used
        cache.get("k1")
        # Adding k4 should evict k2 (LRU)
        cache.put("k4", "v4")
        assert cache.get("k1") is not None
        assert cache.get("k2") is None  # Evicted
        assert cache.get("k4") is not None

    def test_invalidate(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        cache.put("key1", "val")
        assert cache.invalidate("key1") is True
        assert cache.invalidate("key1") is False
        assert cache.get("key1") is None

    def test_invalidate_by_prefix(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        cache.put("crops:wheat", "v1")
        cache.put("crops:barley", "v2")
        cache.put("soil:ph", "v3")
        count = cache.invalidate_by_prefix("crops:")
        assert count == 2
        assert cache.get("soil:ph") == "v3"

    def test_clear(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        cache.clear()
        assert cache.get("k1") is None
        assert cache.stats["size"] == 0
        assert cache.stats["hits"] == 0

    def test_stats(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache(max_size=100, default_ttl=300)
        cache.put("k1", "v1")
        cache.get("k1")  # Hit
        cache.get("k2")  # Miss
        stats = cache.stats
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_make_key_deterministic(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        key1 = KnowledgeCache.make_key("query", "collection", "domain")
        key2 = KnowledgeCache.make_key("query", "collection", "domain")
        assert key1 == key2

    def test_make_key_different_for_different_inputs(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        key1 = KnowledgeCache.make_key("query1", "col1")
        key2 = KnowledgeCache.make_key("query2", "col1")
        assert key1 != key2

    def test_update_existing_key(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        cache.put("k1", "old_value")
        cache.put("k1", "new_value")
        assert cache.get("k1") == "new_value"

    def test_cache_entry_is_expired(self):
        from shared.ai.knowledge.cache import CacheEntry

        entry = CacheEntry(key="test", value="val", ttl_seconds=0.01)
        time.sleep(0.02)
        assert entry.is_expired is True

    def test_cache_entry_not_expired(self):
        from shared.ai.knowledge.cache import CacheEntry

        entry = CacheEntry(key="test", value="val", ttl_seconds=300)
        assert entry.is_expired is False

    def test_invalidate_collection(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        cache.put("crop_knowledge_query1", "v1")
        cache.put("crop_knowledge_query2", "v2")
        cache.put("soil_knowledge_query", "v3")
        count = cache.invalidate_collection("crop_knowledge")
        assert count == 2
