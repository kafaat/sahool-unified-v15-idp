"""
Tests for UltraRAG Retriever Module
اختبارات وحدة مسترجع UltraRAG
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from shared.ai.ultrarag.retriever import (
    RetrievalConfig,
    Retriever,
    DenseRetriever,
    SparseRetriever,
    HybridRetriever,
    AdaptiveRetriever,
)
from shared.ai.ultrarag.models import (
    KnowledgeChunk,
    RetrievalResult,
    RetrievalStrategy,
)


class TestRetrievalConfig:
    """Tests for RetrievalConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = RetrievalConfig()
        assert config.strategy == RetrievalStrategy.HYBRID
        assert config.top_k == 10
        assert config.dense_weight == 0.7
        assert config.sparse_weight == 0.3
        assert config.min_score_threshold == 0.1
        assert config.use_query_expansion is True
        assert config.max_query_terms == 10
        assert config.collection == "default"
        assert config.filters == {}

    def test_custom_config(self):
        """Test custom configuration"""
        config = RetrievalConfig(
            strategy=RetrievalStrategy.DENSE,
            top_k=20,
            dense_weight=0.9,
            sparse_weight=0.1,
            min_score_threshold=0.2,
            collection="agriculture",
            filters={"crop": "wheat"},
        )
        assert config.strategy == RetrievalStrategy.DENSE
        assert config.top_k == 20
        assert config.dense_weight == 0.9
        assert config.filters["crop"] == "wheat"


class TestSparseRetriever:
    """Tests for SparseRetriever (BM25)"""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store"""
        store = MagicMock()
        store.get = AsyncMock()
        return store

    @pytest.fixture
    def sparse_retriever(self, mock_vector_store):
        """Create sparse retriever instance"""
        return SparseRetriever(mock_vector_store)

    def test_tokenize_english(self, sparse_retriever):
        """Test tokenization of English text"""
        text = "The quick brown fox jumps over the lazy dog"
        tokens = sparse_retriever._tokenize(text)
        assert "quick" in tokens
        assert "brown" in tokens
        assert "jumps" in tokens
        # Words > 2 chars are kept (including "the" which has 3 chars)
        assert "the" in tokens
        assert "fox" in tokens
        assert "lazy" in tokens

    def test_tokenize_arabic(self, sparse_retriever):
        """Test tokenization of Arabic text"""
        text = "الري بالتنقيط يوفر المياه"
        tokens = sparse_retriever._tokenize(text)
        assert len(tokens) > 0
        # Arabic words should be preserved
        assert any("\u0600" <= c <= "\u06ff" for token in tokens for c in token)

    def test_tokenize_mixed(self, sparse_retriever):
        """Test tokenization of mixed Arabic/English text"""
        text = "Wheat القمح irrigation الري"
        tokens = sparse_retriever._tokenize(text)
        assert "wheat" in tokens
        assert "irrigation" in tokens
        # Arabic words should also be present
        assert len([t for t in tokens if any("\u0600" <= c <= "\u06ff" for c in t)]) >= 1

    def test_tokenize_removes_short_tokens(self, sparse_retriever):
        """Test that short tokens are removed"""
        text = "I am a test"
        tokens = sparse_retriever._tokenize(text)
        assert "i" not in tokens
        assert "am" not in tokens
        assert "a" not in tokens
        assert "test" in tokens

    def test_calculate_idf(self, sparse_retriever):
        """Test IDF calculation"""
        # Common term (appears in many docs)
        idf_common = sparse_retriever._calculate_idf(100, 50)
        # Rare term (appears in few docs)
        idf_rare = sparse_retriever._calculate_idf(100, 5)
        # Rare terms should have higher IDF
        assert idf_rare > idf_common

    def test_calculate_bm25_score(self, sparse_retriever):
        """Test BM25 score calculation"""
        score = sparse_retriever._calculate_bm25_score(
            tf=3,  # Term frequency
            idf=2.0,  # IDF value
            dl=100,  # Document length
            avg_dl=100,  # Average document length
        )
        assert score > 0

    def test_bm25_score_increases_with_tf(self, sparse_retriever):
        """Test that BM25 score increases with term frequency"""
        score_low_tf = sparse_retriever._calculate_bm25_score(tf=1, idf=1.0, dl=100, avg_dl=100)
        score_high_tf = sparse_retriever._calculate_bm25_score(tf=5, idf=1.0, dl=100, avg_dl=100)
        assert score_high_tf > score_low_tf

    @pytest.mark.asyncio
    async def test_add_documents(self, sparse_retriever):
        """Test adding documents to BM25 index"""
        chunks = [
            KnowledgeChunk(id="c1", text="Wheat cultivation requires irrigation"),
            KnowledgeChunk(id="c2", text="Barley grows in dry conditions"),
            KnowledgeChunk(id="c3", text="Irrigation systems for wheat fields"),
        ]
        result = await sparse_retriever.add_documents(chunks, collection="test")
        assert result is True
        assert "test" in sparse_retriever._index
        assert "test" in sparse_retriever._doc_lengths
        assert len(sparse_retriever._doc_lengths["test"]) == 3

    @pytest.mark.asyncio
    async def test_retrieve_empty_index(self, sparse_retriever):
        """Test retrieval from empty index"""
        config = RetrievalConfig(collection="empty")
        results = await sparse_retriever.retrieve("test query", config)
        assert results == []

    @pytest.mark.asyncio
    async def test_retrieve_with_documents(self, sparse_retriever, mock_vector_store):
        """Test retrieval after adding documents"""
        # Add documents
        chunks = [
            KnowledgeChunk(id="c1", text="Wheat irrigation schedule for summer"),
            KnowledgeChunk(id="c2", text="Barley harvest timing"),
        ]
        await sparse_retriever.add_documents(chunks, collection="agri")

        # Mock vector store get method
        mock_doc = MagicMock()
        mock_doc.text = "Wheat irrigation schedule for summer"
        mock_doc.metadata = {"document_id": "doc1"}
        mock_vector_store.get = AsyncMock(return_value=mock_doc)

        # Retrieve
        config = RetrievalConfig(collection="agri", top_k=5)
        results = await sparse_retriever.retrieve("wheat irrigation", config)

        # Should find wheat irrigation document
        assert len(results) >= 1


class TestDenseRetriever:
    """Tests for DenseRetriever"""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store"""
        store = MagicMock()
        store.search = AsyncMock()
        store.add = AsyncMock()
        return store

    @pytest.fixture
    def mock_embedding_service(self):
        """Create mock embedding service"""
        service = MagicMock()
        service.embed = AsyncMock()
        service.embed_batch = AsyncMock()
        return service

    @pytest.fixture
    def dense_retriever(self, mock_vector_store, mock_embedding_service):
        """Create dense retriever instance"""
        return DenseRetriever(mock_vector_store, mock_embedding_service)

    @pytest.mark.asyncio
    async def test_get_embedding_with_cache(self, dense_retriever, mock_embedding_service):
        """Test embedding caching"""
        mock_result = MagicMock()
        mock_result.vector = [0.1, 0.2, 0.3]
        mock_embedding_service.embed.return_value = mock_result

        # First call
        vec1 = await dense_retriever._get_embedding("test text")
        # Second call - should use cache
        vec2 = await dense_retriever._get_embedding("test text")

        assert vec1 == vec2
        # Embed should only be called once
        assert mock_embedding_service.embed.call_count == 1

    @pytest.mark.asyncio
    async def test_get_embedding_cache_limit(self, dense_retriever, mock_embedding_service):
        """Test cache size limit"""
        mock_result = MagicMock()
        mock_result.vector = [0.1, 0.2, 0.3]
        mock_embedding_service.embed.return_value = mock_result

        # Set a small cache size for testing
        dense_retriever._cache_max_size = 10

        # Add entries up to and beyond limit
        for i in range(15):
            await dense_retriever._get_embedding(f"text_{i}")

        # Cache should have cleaned up some entries
        assert len(dense_retriever._cache) <= dense_retriever._cache_max_size

    @pytest.mark.asyncio
    async def test_retrieve(self, dense_retriever, mock_vector_store, mock_embedding_service):
        """Test dense retrieval"""
        # Mock embedding
        mock_embed_result = MagicMock()
        mock_embed_result.vector = [0.1, 0.2, 0.3]
        mock_embedding_service.embed.return_value = mock_embed_result

        # Mock search results
        mock_search_result = MagicMock()
        mock_search_result.id = "chunk_1"
        mock_search_result.text = "Wheat irrigation best practices"
        mock_search_result.score = 0.95
        mock_search_result.metadata = {"document_id": "doc1"}
        mock_vector_store.search.return_value = [mock_search_result]

        config = RetrievalConfig(collection="test", top_k=5)
        results = await dense_retriever.retrieve("wheat irrigation", config)

        assert len(results) == 1
        assert results[0].chunk.id == "chunk_1"
        assert results[0].score == 0.95
        assert results[0].retrieval_method == "dense"

    @pytest.mark.asyncio
    async def test_retrieve_filters_by_min_score(self, dense_retriever, mock_vector_store, mock_embedding_service):
        """Test that results below min score are filtered"""
        mock_embed_result = MagicMock()
        mock_embed_result.vector = [0.1, 0.2, 0.3]
        mock_embedding_service.embed.return_value = mock_embed_result

        # Mock search results with varying scores
        results = [
            MagicMock(id="c1", text="Text 1", score=0.95, metadata={}),
            MagicMock(id="c2", text="Text 2", score=0.05, metadata={}),  # Below threshold
            MagicMock(id="c3", text="Text 3", score=0.50, metadata={}),
        ]
        mock_vector_store.search.return_value = results

        config = RetrievalConfig(min_score_threshold=0.1)
        retrieval_results = await dense_retriever.retrieve("query", config)

        # Only 2 results should pass the threshold
        assert len(retrieval_results) == 2

    @pytest.mark.asyncio
    async def test_add_documents(self, dense_retriever, mock_vector_store, mock_embedding_service):
        """Test adding documents with embeddings"""
        chunks = [
            KnowledgeChunk(id="c1", text="Document 1", document_id="d1"),
            KnowledgeChunk(id="c2", text="Document 2", document_id="d2"),
        ]

        mock_result1 = MagicMock()
        mock_result1.vector = [0.1, 0.2]
        mock_result2 = MagicMock()
        mock_result2.vector = [0.3, 0.4]
        mock_embedding_service.embed_batch.return_value = [mock_result1, mock_result2]

        result = await dense_retriever.add_documents(chunks, "test_collection")

        assert result is True
        mock_vector_store.add.assert_called_once()


class TestHybridRetriever:
    """Tests for HybridRetriever"""

    @pytest.fixture
    def mock_dense_retriever(self):
        """Create mock dense retriever"""
        retriever = MagicMock(spec=DenseRetriever)
        retriever.retrieve = AsyncMock(return_value=[])
        retriever.add_documents = AsyncMock(return_value=True)
        return retriever

    @pytest.fixture
    def mock_sparse_retriever(self):
        """Create mock sparse retriever"""
        retriever = MagicMock(spec=SparseRetriever)
        retriever.retrieve = AsyncMock(return_value=[])
        retriever.add_documents = AsyncMock(return_value=True)
        return retriever

    @pytest.fixture
    def hybrid_retriever(self, mock_dense_retriever, mock_sparse_retriever):
        """Create hybrid retriever instance"""
        return HybridRetriever(mock_dense_retriever, mock_sparse_retriever)

    @pytest.mark.asyncio
    async def test_retrieve_combines_results(self, hybrid_retriever, mock_dense_retriever, mock_sparse_retriever):
        """Test that hybrid retriever combines dense and sparse results"""
        chunk1 = KnowledgeChunk(id="c1", text="From dense")
        chunk2 = KnowledgeChunk(id="c2", text="From sparse")
        chunk3 = KnowledgeChunk(id="c3", text="From both")

        mock_dense_retriever.retrieve.return_value = [
            RetrievalResult(chunk=chunk1, score=0.9, rank=1),
            RetrievalResult(chunk=chunk3, score=0.8, rank=2),
        ]
        mock_sparse_retriever.retrieve.return_value = [
            RetrievalResult(chunk=chunk2, score=0.85, rank=1),
            RetrievalResult(chunk=chunk3, score=0.75, rank=2),
        ]

        config = RetrievalConfig(top_k=5)
        results = await hybrid_retriever.retrieve("test query", config)

        # Should combine unique results
        result_ids = [r.chunk.id for r in results]
        assert "c1" in result_ids
        assert "c2" in result_ids
        assert "c3" in result_ids
        # All should be marked as hybrid
        for r in results:
            assert r.retrieval_method == "hybrid"

    @pytest.mark.asyncio
    async def test_add_documents_to_both(self, hybrid_retriever, mock_dense_retriever, mock_sparse_retriever):
        """Test that documents are added to both indices"""
        chunks = [KnowledgeChunk(id="c1", text="Test document")]

        result = await hybrid_retriever.add_documents(chunks, "test")

        assert result is True
        mock_dense_retriever.add_documents.assert_called_once()
        mock_sparse_retriever.add_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_documents_fails_if_one_fails(
        self, hybrid_retriever, mock_dense_retriever, mock_sparse_retriever
    ):
        """Test that add fails if either index fails"""
        chunks = [KnowledgeChunk(id="c1", text="Test")]
        mock_sparse_retriever.add_documents.return_value = False

        result = await hybrid_retriever.add_documents(chunks, "test")

        assert result is False


class TestAdaptiveRetriever:
    """Tests for AdaptiveRetriever"""

    @pytest.fixture
    def mock_dense_retriever(self):
        retriever = MagicMock(spec=DenseRetriever)
        retriever.retrieve = AsyncMock(return_value=[])
        return retriever

    @pytest.fixture
    def mock_sparse_retriever(self):
        retriever = MagicMock(spec=SparseRetriever)
        retriever.retrieve = AsyncMock(return_value=[])
        return retriever

    @pytest.fixture
    def mock_hybrid_retriever(self):
        retriever = MagicMock(spec=HybridRetriever)
        retriever.retrieve = AsyncMock(return_value=[])
        retriever.add_documents = AsyncMock(return_value=True)
        return retriever

    @pytest.fixture
    def adaptive_retriever(self, mock_dense_retriever, mock_sparse_retriever, mock_hybrid_retriever):
        return AdaptiveRetriever(mock_dense_retriever, mock_sparse_retriever, mock_hybrid_retriever)

    def test_analyze_query_keyword(self, adaptive_retriever):
        """Test keyword query detection"""
        assert adaptive_retriever._analyze_query("wheat") == "keyword"
        assert adaptive_retriever._analyze_query("irrigation rate") == "keyword"
        assert adaptive_retriever._analyze_query("القمح") == "keyword"

    def test_analyze_query_semantic(self, adaptive_retriever):
        """Test semantic query detection"""
        assert (
            adaptive_retriever._analyze_query("What is the best irrigation schedule for wheat in summer?") == "semantic"
        )
        assert adaptive_retriever._analyze_query("How do I prevent wheat rust disease from spreading?") == "semantic"
        assert adaptive_retriever._analyze_query("كيف يمكنني ري القمح بشكل صحيح؟") == "semantic"

    def test_analyze_query_hybrid(self, adaptive_retriever):
        """Test hybrid query detection"""
        # Medium-length queries without question words
        assert adaptive_retriever._analyze_query("wheat irrigation best practices summer") == "hybrid"
        assert adaptive_retriever._analyze_query("fertilizer application timing wheat") == "hybrid"

    @pytest.mark.asyncio
    async def test_uses_sparse_for_keyword(self, adaptive_retriever, mock_sparse_retriever):
        """Test that sparse retriever is used for keyword queries"""
        chunk = KnowledgeChunk(id="c1", text="Wheat info")
        mock_sparse_retriever.retrieve.return_value = [RetrievalResult(chunk=chunk, score=0.9, rank=1)]

        config = RetrievalConfig()
        await adaptive_retriever.retrieve("wheat", config)

        mock_sparse_retriever.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_dense_for_semantic(self, adaptive_retriever, mock_dense_retriever):
        """Test that dense retriever is used for semantic queries"""
        chunk = KnowledgeChunk(id="c1", text="Wheat info")
        mock_dense_retriever.retrieve.return_value = [RetrievalResult(chunk=chunk, score=0.9, rank=1)]

        config = RetrievalConfig()
        await adaptive_retriever.retrieve("What is the best way to irrigate wheat in dry conditions?", config)

        mock_dense_retriever.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_hybrid_for_mixed(self, adaptive_retriever, mock_hybrid_retriever):
        """Test that hybrid retriever is used for mixed queries"""
        chunk = KnowledgeChunk(id="c1", text="Wheat info")
        mock_hybrid_retriever.retrieve.return_value = [RetrievalResult(chunk=chunk, score=0.9, rank=1)]

        config = RetrievalConfig()
        await adaptive_retriever.retrieve("wheat irrigation best practices", config)

        mock_hybrid_retriever.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_documents_delegates_to_hybrid(self, adaptive_retriever, mock_hybrid_retriever):
        """Test that add_documents delegates to hybrid retriever"""
        chunks = [KnowledgeChunk(id="c1", text="Test")]

        result = await adaptive_retriever.add_documents(chunks, "test")

        assert result is True
        mock_hybrid_retriever.add_documents.assert_called_once()
