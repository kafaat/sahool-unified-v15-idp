"""
Tests for Knowledge Persistence Layer
=======================================
اختبارات طبقة استمرارية المعرفة
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.models import BaseKnowledgeDocument, KnowledgeDomain, VerificationStatus
from shared.ai.knowledge.persistence import (
    DocumentPage,
    DocumentQuery,
    InMemoryKnowledgeRepository,
)


@pytest.fixture
def repo() -> InMemoryKnowledgeRepository:
    return InMemoryKnowledgeRepository()


def _make_doc(
    title: str = "Test",
    domain: KnowledgeDomain = KnowledgeDomain.CROPS,
    tags: list[str] | None = None,
    content: str = "Test content",
    content_ar: str = "",
    regions: list[str] | None = None,
) -> BaseKnowledgeDocument:
    doc = BaseKnowledgeDocument(
        title=title,
        domain=domain,
        content=content,
        content_ar=content_ar,
        tags=tags or [],
    )
    if regions:
        doc.geospatial.applicable_regions = regions
    return doc


class TestInMemoryRepository:
    """Tests for InMemoryKnowledgeRepository."""

    @pytest.mark.unit
    def test_save_and_get(self, repo: InMemoryKnowledgeRepository):
        doc = _make_doc("Wheat Guide")
        doc_id = repo.save(doc)
        assert doc_id == doc.id
        retrieved = repo.get_by_id(doc_id)
        assert retrieved is not None
        assert retrieved.title == "Wheat Guide"

    @pytest.mark.unit
    def test_get_nonexistent(self, repo: InMemoryKnowledgeRepository):
        assert repo.get_by_id("nonexistent") is None

    @pytest.mark.unit
    def test_save_batch(self, repo: InMemoryKnowledgeRepository):
        docs = [_make_doc(f"Doc {i}") for i in range(5)]
        ids = repo.save_batch(docs)
        assert len(ids) == 5
        assert repo.count() == 5

    @pytest.mark.unit
    def test_update(self, repo: InMemoryKnowledgeRepository):
        doc = _make_doc("Original")
        repo.save(doc)
        doc.title = "Updated"
        assert repo.update(doc) is True
        retrieved = repo.get_by_id(doc.id)
        assert retrieved.title == "Updated"

    @pytest.mark.unit
    def test_update_nonexistent(self, repo: InMemoryKnowledgeRepository):
        doc = _make_doc("Ghost")
        assert repo.update(doc) is False

    @pytest.mark.unit
    def test_delete(self, repo: InMemoryKnowledgeRepository):
        doc = _make_doc("To Delete")
        repo.save(doc)
        assert repo.delete(doc.id) is True
        assert repo.get_by_id(doc.id) is None
        assert repo.count() == 0

    @pytest.mark.unit
    def test_delete_nonexistent(self, repo: InMemoryKnowledgeRepository):
        assert repo.delete("nonexistent") is False

    @pytest.mark.unit
    def test_count(self, repo: InMemoryKnowledgeRepository):
        assert repo.count() == 0
        repo.save(_make_doc("A"))
        repo.save(_make_doc("B"))
        assert repo.count() == 2

    @pytest.mark.unit
    def test_list_collections(self, repo: InMemoryKnowledgeRepository):
        repo.save(_make_doc("Crop", domain=KnowledgeDomain.CROPS))
        repo.save(_make_doc("Soil", domain=KnowledgeDomain.SOIL))
        collections = repo.list_collections()
        assert len(collections) >= 2

    @pytest.mark.unit
    def test_find_by_domain(self, repo: InMemoryKnowledgeRepository):
        repo.save(_make_doc("Crop1", domain=KnowledgeDomain.CROPS))
        repo.save(_make_doc("Crop2", domain=KnowledgeDomain.CROPS))
        repo.save(_make_doc("Soil1", domain=KnowledgeDomain.SOIL))

        query = DocumentQuery(domain=KnowledgeDomain.CROPS)
        page = repo.find(query)
        assert isinstance(page, DocumentPage)
        assert page.total == 2
        assert len(page.items) == 2

    @pytest.mark.unit
    def test_find_by_tags(self, repo: InMemoryKnowledgeRepository):
        repo.save(_make_doc("Wheat", tags=["wheat", "grain"]))
        repo.save(_make_doc("Barley", tags=["barley", "grain"]))
        repo.save(_make_doc("Tomato", tags=["tomato", "vegetable"]))

        query = DocumentQuery(tags=["grain"])
        page = repo.find(query)
        assert page.total == 2

    @pytest.mark.unit
    def test_find_pagination(self, repo: InMemoryKnowledgeRepository):
        for i in range(10):
            repo.save(_make_doc(f"Doc {i}"))

        page1 = repo.find(DocumentQuery(limit=3, offset=0))
        assert len(page1.items) == 3
        assert page1.total == 10
        assert page1.has_next is True

        page2 = repo.find(DocumentQuery(limit=3, offset=9))
        assert len(page2.items) == 1
        assert page2.has_next is False

    @pytest.mark.unit
    def test_find_text_search(self, repo: InMemoryKnowledgeRepository):
        repo.save(_make_doc("Wheat Irrigation", content="Wheat needs regular irrigation"))
        repo.save(_make_doc("Soil Testing", content="Test soil pH and EC"))

        query = DocumentQuery(text_search="wheat")
        page = repo.find(query)
        assert page.total >= 1

    @pytest.mark.unit
    def test_find_empty_query(self, repo: InMemoryKnowledgeRepository):
        repo.save(_make_doc("A"))
        repo.save(_make_doc("B"))
        page = repo.find(DocumentQuery())
        assert page.total == 2
