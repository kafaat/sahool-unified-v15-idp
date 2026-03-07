"""
Tests for Knowledge Vector Store Integration
=============================================
اختبارات تكامل مخزن المتجهات
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.ingestion.chunker import TextChunk
from shared.ai.knowledge.models import BaseKnowledgeDocument, KnowledgeDomain
from shared.ai.knowledge.vector_store_integration import (
    KnowledgeVectorStore,
    VectorSearchResult,
)


def _make_doc(title: str = "Test", domain: KnowledgeDomain = KnowledgeDomain.CROPS) -> BaseKnowledgeDocument:
    return BaseKnowledgeDocument(
        title=title,
        domain=domain,
        content=f"Content about {title.lower()}",
        tags=["test"],
    )


class TestKnowledgeVectorStore:
    """Tests for KnowledgeVectorStore."""

    @pytest.fixture
    def store(self) -> KnowledgeVectorStore:
        return KnowledgeVectorStore(collection_prefix="test_kb_")

    @pytest.mark.unit
    def test_store_document(self, store: KnowledgeVectorStore):
        doc = _make_doc("Wheat Guide")
        ids = store.store_document(doc)
        assert isinstance(ids, list)
        assert len(ids) >= 1

    @pytest.mark.unit
    def test_store_document_with_chunks(self, store: KnowledgeVectorStore):
        doc = _make_doc("Wheat Guide")
        chunks = [
            TextChunk(content="Chunk 1 about wheat planting"),
            TextChunk(content="Chunk 2 about wheat irrigation"),
        ]
        ids = store.store_document(doc, chunks=chunks)
        assert len(ids) == 2

    @pytest.mark.unit
    def test_search_returns_results(self, store: KnowledgeVectorStore):
        doc = _make_doc("Wheat Irrigation")
        store.store_document(doc)
        results = store.search("wheat irrigation")
        assert isinstance(results, list)

    @pytest.mark.unit
    def test_search_with_domain_filter(self, store: KnowledgeVectorStore):
        store.store_document(_make_doc("Crop Doc", KnowledgeDomain.CROPS))
        store.store_document(_make_doc("Soil Doc", KnowledgeDomain.SOIL))
        results = store.search("agriculture", domain_filter=KnowledgeDomain.CROPS)
        assert isinstance(results, list)

    @pytest.mark.unit
    def test_delete_document(self, store: KnowledgeVectorStore):
        doc = _make_doc("To Delete")
        store.store_document(doc)
        result = store.delete_document(doc.id)
        assert isinstance(result, bool)

    @pytest.mark.unit
    def test_get_collection_stats(self, store: KnowledgeVectorStore):
        stats = store.get_collection_stats()
        assert isinstance(stats, dict)

    @pytest.mark.unit
    def test_build_metadata_filter(self, store: KnowledgeVectorStore):
        filters = store._build_metadata_filter(
            domain_filter=KnowledgeDomain.CROPS,
            region_filter=["yemen"],
            min_credibility=3,
        )
        assert isinstance(filters, dict)

    @pytest.mark.unit
    def test_search_bilingual(self, store: KnowledgeVectorStore):
        doc = _make_doc("Wheat")
        store.store_document(doc)
        results = store.search_bilingual("wheat irrigation", query_ar="ري القمح")
        assert isinstance(results, list)


class TestVectorSearchResult:
    """Tests for VectorSearchResult dataclass."""

    @pytest.mark.unit
    def test_result_fields(self):
        result = VectorSearchResult(
            document_id="kb_test123",
            content="Wheat cultivation guide",
            content_ar="دليل زراعة القمح",
            score=0.95,
            collection="crop_knowledge",
        )
        assert result.document_id == "kb_test123"
        assert result.score == 0.95
        assert result.collection == "crop_knowledge"
