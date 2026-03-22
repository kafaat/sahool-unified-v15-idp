"""
Tests for RAG Service (rag/service.py)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit]
def _make_rag_service():
    """Helper to create a RAG service with mocked embedding service."""
    from src.rag.embeddings import EmbeddingResult
    from src.rag.service import CopilotRAGService, RAGConfig

    mock_embedding = MagicMock()
    mock_embedding.dimension = 384
    mock_embedding.initialize = AsyncMock()
    mock_embedding.embed = AsyncMock(
        return_value=EmbeddingResult(
            embedding=[0.1] * 384,
            text="test",
            dimension=384,
            latency_ms=1.0,
        )
    )
    mock_embedding.config = MagicMock()
    mock_embedding.config.provider.value = "sentence_transformers"

    config = RAGConfig(use_qdrant=False)
    service = CopilotRAGService(config=config, embedding_service=mock_embedding)
    return service
class TestRAGDocument:
    def test_to_dict(self):
        from src.rag.service import RAGDocument

        doc = RAGDocument(id="d1", text="hello", text_ar="مرحبا", metadata={"cat": "test"})
        d = doc.to_dict()
        assert d["id"] == "d1"
        assert d["text"] == "hello"
        assert d["text_ar"] == "مرحبا"
        assert "created_at" in d

    def test_defaults(self):
        from src.rag.service import RAGDocument

        doc = RAGDocument(id="d1", text="hello")
        assert doc.text_ar is None
        assert doc.metadata == {}
        assert doc.embedding is None
class TestSearchResult:
    def test_defaults(self):
        from src.rag.service import RAGDocument, SearchResult

        doc = RAGDocument(id="1", text="t")
        sr = SearchResult(document=doc, score=0.8)
        assert sr.match_type == "semantic"
class TestRAGConfig:
    def test_defaults(self):
        from src.rag.service import RAGConfig

        config = RAGConfig()
        assert config.default_top_k == 5
        assert config.min_score_threshold == 0.3
        assert config.chunk_size == 500
class TestCopilotRAGService:
    @pytest.mark.asyncio
    async def test_initialize(self):
        service = _make_rag_service()
        result = await service.initialize()
        assert result is True
        assert service._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_idempotent(self):
        service = _make_rag_service()
        await service.initialize()
        result = await service.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_add_document(self):
        service = _make_rag_service()
        await service.initialize()

        doc = await service.add_document(text="Wheat irrigation info", text_ar="معلومات ري القمح")
        assert doc.text == "Wheat irrigation info"
        assert doc.id in service._documents

    @pytest.mark.asyncio
    async def test_add_document_with_custom_id(self):
        service = _make_rag_service()
        await service.initialize()

        doc = await service.add_document(text="test", doc_id="custom-id")
        assert doc.id == "custom-id"
        assert "custom-id" in service._documents

    @pytest.mark.asyncio
    async def test_add_documents_batch(self):
        service = _make_rag_service()
        await service.initialize()

        docs = [
            {"text": "Doc 1", "metadata": {"cat": "a"}},
            {"text": "Doc 2", "text_ar": "وثيقة 2"},
        ]
        results = await service.add_documents_batch(docs)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_keyword_search_finds_matching_doc(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="Wheat irrigation during tillering stage", doc_id="d1")
        await service.add_document(text="Date palm pest management", doc_id="d2")

        results = await service.search("wheat irrigation", top_k=5)
        assert len(results) > 0
        assert results[0].document.id == "d1"
        assert results[0].match_type == "keyword"

    @pytest.mark.asyncio
    async def test_keyword_search_no_match(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="Wheat irrigation", doc_id="d1")

        results = await service.search("zzzzunrelatedquery", top_k=5)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_keyword_search_exact_phrase_boost(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="wheat irrigation schedule for winter", doc_id="d1")
        await service.add_document(text="wheat barley corn rice", doc_id="d2")

        results = await service.search("wheat irrigation schedule", top_k=5)
        assert len(results) >= 1
        # d1 should score higher due to exact phrase boost
        assert results[0].document.id == "d1"

    @pytest.mark.asyncio
    async def test_search_with_tenant_filter(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="Doc for tenant A", metadata={"tenant_id": "A"}, doc_id="d1")
        await service.add_document(text="Doc for tenant B", metadata={"tenant_id": "B"}, doc_id="d2")

        results = await service.search("Doc for tenant", top_k=5, tenant_id="A")
        ids = [r.document.id for r in results]
        assert "d1" in ids
        assert "d2" not in ids

    @pytest.mark.asyncio
    async def test_search_with_metadata_filter(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="Wheat disease info", metadata={"category": "disease"}, doc_id="d1")
        await service.add_document(text="Wheat irrigation info", metadata={"category": "irrigation"}, doc_id="d2")

        results = await service.search("wheat info", top_k=5, metadata_filter={"category": "disease"})
        ids = [r.document.id for r in results]
        assert "d1" in ids
        assert "d2" not in ids

    @pytest.mark.asyncio
    async def test_delete_document(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="to delete", doc_id="del-1")
        assert "del-1" in service._documents

        result = await service.delete_document("del-1")
        assert result is True
        assert "del-1" not in service._documents

    @pytest.mark.asyncio
    async def test_delete_nonexistent_document(self):
        service = _make_rag_service()
        await service.initialize()

        result = await service.delete_document("nonexistent")
        assert result is True  # No error for missing doc

    @pytest.mark.asyncio
    async def test_list_documents(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="Doc 1", doc_id="d1")
        await service.add_document(text="Doc 2", doc_id="d2")

        docs = await service.list_documents()
        assert len(docs) == 2

    @pytest.mark.asyncio
    async def test_list_documents_with_limit(self):
        service = _make_rag_service()
        await service.initialize()

        for i in range(5):
            await service.add_document(text=f"Doc {i}", doc_id=f"d{i}")

        docs = await service.list_documents(limit=3)
        assert len(docs) == 3

    @pytest.mark.asyncio
    async def test_list_documents_with_tenant_filter(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="A", metadata={"tenant_id": "t1"}, doc_id="d1")
        await service.add_document(text="B", metadata={"tenant_id": "t2"}, doc_id="d2")

        docs = await service.list_documents(tenant_id="t1")
        assert len(docs) == 1
        assert docs[0].id == "d1"

    @pytest.mark.asyncio
    async def test_get_stats(self):
        service = _make_rag_service()
        await service.initialize()

        await service.add_document(text="test", doc_id="d1")
        stats = await service.get_stats()
        assert stats["total_documents"] == 1
        assert stats["qdrant_available"] is False
        assert stats["embedding_dimension"] == 384
class TestFormatContextForPrompt:
    def _make_results(self, count=3):
        from src.rag.service import RAGDocument, SearchResult

        results = []
        for i in range(count):
            doc = RAGDocument(
                id=str(i),
                text=f"English text {i}",
                text_ar=f"نص عربي {i}",
                metadata={},
            )
            results.append(SearchResult(document=doc, score=0.9 - i * 0.1))
        return results

    def test_empty_results(self):
        service = _make_rag_service()
        context = service.format_context_for_prompt([], language="en")
        assert context == ""

    def test_english_language(self):
        service = _make_rag_service()
        results = self._make_results(2)
        context = service.format_context_for_prompt(results, language="en")
        assert "English text 0" in context
        assert "نص عربي" not in context

    def test_arabic_language(self):
        service = _make_rag_service()
        results = self._make_results(2)
        context = service.format_context_for_prompt(results, language="ar")
        assert "نص عربي 0" in context

    def test_max_chars_limit(self):
        service = _make_rag_service()
        results = self._make_results(10)
        context = service.format_context_for_prompt(results, max_chars=100, language="en")
        assert len(context) <= 200  # Some overhead for [DOC N] prefix

    def test_doc_numbering(self):
        service = _make_rag_service()
        results = self._make_results(3)
        context = service.format_context_for_prompt(results, language="en")
        assert "[DOC 1]" in context
        assert "[DOC 2]" in context
class TestGetRagService:
    def test_singleton(self):
        import src.rag.service as smod

        smod._rag_service = None
        s1 = smod.get_rag_service()
        s2 = smod.get_rag_service()
        assert s1 is s2
        smod._rag_service = None
