"""
Tests for UltraRAG Reranker Module
اختبارات وحدة إعادة الترتيب UltraRAG
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.ultrarag.models import (
    KnowledgeChunk,
    RerankingMethod,
    RerankResult,
    RetrievalResult,
)
from shared.ai.ultrarag.reranker import (
    CrossEncoderReranker,
    LLMReranker,
    NoReranker,
    ReciprocalRankFusionReranker,
    RerankConfig,
    Reranker,
    get_reranker,
)


class TestRerankConfig:
    """Tests for RerankConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = RerankConfig()
        assert config.method == RerankingMethod.CROSS_ENCODER
        assert config.top_k == 5
        assert config.model == "cross-encoder/ms-marco-MiniLM-L-6-v2"
        assert config.batch_size == 32
        assert config.min_score_threshold == 0.0

    def test_custom_config(self):
        """Test custom configuration"""
        config = RerankConfig(
            method=RerankingMethod.LLM,
            top_k=10,
            model="codellama:13b",
            min_score_threshold=0.5,
        )
        assert config.method == RerankingMethod.LLM
        assert config.top_k == 10
        assert config.model == "codellama:13b"
        assert config.min_score_threshold == 0.5


class TestNoReranker:
    """Tests for NoReranker (pass-through)"""

    @pytest.fixture
    def no_reranker(self):
        return NoReranker()

    @pytest.fixture
    def sample_results(self):
        """Create sample retrieval results"""
        return [
            RetrievalResult(
                chunk=KnowledgeChunk(id="c1", text="Document 1"),
                score=0.7,
                rank=1,
            ),
            RetrievalResult(
                chunk=KnowledgeChunk(id="c2", text="Document 2"),
                score=0.9,
                rank=2,
            ),
            RetrievalResult(
                chunk=KnowledgeChunk(id="c3", text="Document 3"),
                score=0.5,
                rank=3,
            ),
        ]

    @pytest.mark.asyncio
    async def test_rerank_empty_results(self, no_reranker):
        """Test reranking empty results"""
        config = RerankConfig()
        result = await no_reranker.rerank("query", [], config)
        assert result.results == []
        assert result.method == RerankingMethod.NONE

    @pytest.mark.asyncio
    async def test_rerank_sorts_by_score(self, no_reranker, sample_results):
        """Test that results are sorted by score"""
        config = RerankConfig(top_k=5)
        result = await no_reranker.rerank("query", sample_results, config)

        # Should be sorted by score descending
        assert result.results[0].chunk.id == "c2"  # score 0.9
        assert result.results[1].chunk.id == "c1"  # score 0.7
        assert result.results[2].chunk.id == "c3"  # score 0.5

    @pytest.mark.asyncio
    async def test_rerank_respects_top_k(self, no_reranker, sample_results):
        """Test that top_k is respected"""
        config = RerankConfig(top_k=2)
        result = await no_reranker.rerank("query", sample_results, config)

        assert len(result.results) == 2

    @pytest.mark.asyncio
    async def test_rerank_updates_ranks(self, no_reranker, sample_results):
        """Test that ranks are updated correctly"""
        config = RerankConfig(top_k=5)
        result = await no_reranker.rerank("query", sample_results, config)

        for i, r in enumerate(result.results):
            assert r.rank == i + 1

    @pytest.mark.asyncio
    async def test_rerank_has_processing_time(self, no_reranker, sample_results):
        """Test that processing time is recorded"""
        config = RerankConfig()
        result = await no_reranker.rerank("query", sample_results, config)

        assert result.processing_time_ms >= 0


class TestCrossEncoderReranker:
    """Tests for CrossEncoderReranker"""

    @pytest.fixture
    def cross_encoder_reranker(self):
        return CrossEncoderReranker()

    @pytest.fixture
    def sample_results(self):
        return [
            RetrievalResult(
                chunk=KnowledgeChunk(id="c1", text="Wheat irrigation guide"),
                score=0.6,
                rank=1,
            ),
            RetrievalResult(
                chunk=KnowledgeChunk(id="c2", text="Barley cultivation tips"),
                score=0.8,
                rank=2,
            ),
        ]

    @pytest.mark.asyncio
    async def test_rerank_empty_results(self, cross_encoder_reranker):
        """Test reranking empty results"""
        config = RerankConfig()
        result = await cross_encoder_reranker.rerank("query", [], config)

        assert result.results == []
        assert result.method == RerankingMethod.CROSS_ENCODER
        assert result.processing_time_ms == 0.0

    @pytest.mark.asyncio
    async def test_rerank_fallback_without_model(self, cross_encoder_reranker, sample_results):
        """Test reranking falls back gracefully when model unavailable"""
        # Force initialization without model
        cross_encoder_reranker._initialized = True
        cross_encoder_reranker._model = None

        config = RerankConfig(top_k=5)
        result = await cross_encoder_reranker.rerank("wheat", sample_results, config)

        # Should still return results (fallback to original ranking)
        assert len(result.results) == 2
        assert result.method == RerankingMethod.CROSS_ENCODER

    @pytest.mark.asyncio
    async def test_rerank_with_mocked_model(self, sample_results):
        """Test reranking with mocked cross-encoder model"""
        reranker = CrossEncoderReranker()
        reranker._initialized = True

        # Mock the cross-encoder model
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.95, 0.3]  # c1 more relevant than c2
        reranker._model = mock_model

        config = RerankConfig(top_k=2)
        result = await reranker.rerank("wheat irrigation", sample_results, config)

        # c1 should be ranked higher after reranking
        assert result.results[0].chunk.id == "c1"
        assert result.results[0].score == 0.95

    @pytest.mark.asyncio
    async def test_rerank_respects_min_score_threshold(self, sample_results):
        """Test that min score threshold is applied"""
        reranker = CrossEncoderReranker()
        reranker._initialized = True

        mock_model = MagicMock()
        mock_model.predict.return_value = [0.8, 0.2]  # c2 below threshold
        reranker._model = mock_model

        config = RerankConfig(top_k=5, min_score_threshold=0.5)
        result = await reranker.rerank("query", sample_results, config)

        # Only c1 should pass the threshold
        assert len(result.results) == 1
        assert result.results[0].chunk.id == "c1"


class TestLLMReranker:
    """Tests for LLMReranker"""

    @pytest.fixture
    def mock_llm_client(self):
        client = MagicMock()
        client.generate = AsyncMock()
        return client

    @pytest.fixture
    def llm_reranker(self, mock_llm_client):
        return LLMReranker(llm_client=mock_llm_client, model="codellama:7b")

    @pytest.fixture
    def sample_results(self):
        return [
            RetrievalResult(
                chunk=KnowledgeChunk(id="c1", text="Wheat irrigation requires 25mm"),
                score=0.5,
                rank=1,
            ),
            RetrievalResult(
                chunk=KnowledgeChunk(id="c2", text="Barley needs less water"),
                score=0.6,
                rank=2,
            ),
        ]

    @pytest.mark.asyncio
    async def test_rerank_empty_results(self, llm_reranker):
        """Test reranking empty results"""
        config = RerankConfig()
        result = await llm_reranker.rerank("query", [], config)

        assert result.results == []
        assert result.method == RerankingMethod.LLM

    @pytest.mark.asyncio
    async def test_rerank_without_client(self, sample_results):
        """Test reranking without LLM client falls back"""
        reranker = LLMReranker(llm_client=None)
        config = RerankConfig(top_k=2)

        result = await reranker.rerank("query", sample_results, config)

        # Should return original results
        assert len(result.results) == 2
        assert result.method == RerankingMethod.LLM

    @pytest.mark.asyncio
    async def test_rerank_with_llm_scoring(self, llm_reranker, mock_llm_client, sample_results):
        """Test reranking with LLM scoring"""
        # Mock LLM responses with scores
        mock_llm_client.generate.side_effect = ["8", "3"]  # c1 gets higher score

        config = RerankConfig(top_k=2)
        result = await llm_reranker.rerank("wheat irrigation", sample_results, config)

        # c1 should be ranked first (score 8/10 = 0.8)
        assert result.results[0].chunk.id == "c1"
        assert result.method == RerankingMethod.LLM

    def test_parse_score_valid_number(self, llm_reranker):
        """Test parsing valid score"""
        assert llm_reranker._parse_score("8") == 0.8
        assert llm_reranker._parse_score("10") == 1.0
        assert llm_reranker._parse_score("0") == 0.0

    def test_parse_score_with_text(self, llm_reranker):
        """Test parsing score from text response"""
        assert llm_reranker._parse_score("The relevance score is 7") == 0.7
        assert llm_reranker._parse_score("Score: 9/10") == 0.9

    def test_parse_score_invalid(self, llm_reranker):
        """Test parsing invalid response returns default"""
        assert llm_reranker._parse_score("no number here") == 0.5
        assert llm_reranker._parse_score("") == 0.5

    def test_parse_score_clamped(self, llm_reranker):
        """Test that scores are clamped to 0-1"""
        assert llm_reranker._parse_score("15") == 1.0  # Clamped to max
        assert llm_reranker._parse_score("-5") == 0.5  # Fallback for negative

    def test_create_scoring_prompt(self, llm_reranker):
        """Test scoring prompt creation"""
        prompt = llm_reranker._create_scoring_prompt(
            "wheat irrigation", "Wheat requires regular irrigation during growth"
        )
        assert "wheat irrigation" in prompt
        assert "Wheat requires regular irrigation" in prompt
        assert "0-10" in prompt


class TestReciprocalRankFusionReranker:
    """Tests for ReciprocalRankFusionReranker"""

    @pytest.fixture
    def rrf_reranker(self):
        return ReciprocalRankFusionReranker(k=60)

    @pytest.fixture
    def sample_results_multi_method(self):
        """Results from multiple retrieval methods"""
        return [
            # Dense results
            RetrievalResult(
                chunk=KnowledgeChunk(id="c1", text="Document 1"),
                score=0.9,
                rank=1,
                retrieval_method="dense",
            ),
            RetrievalResult(
                chunk=KnowledgeChunk(id="c2", text="Document 2"),
                score=0.8,
                rank=2,
                retrieval_method="dense",
            ),
            # Sparse results
            RetrievalResult(
                chunk=KnowledgeChunk(id="c2", text="Document 2"),  # Same doc
                score=0.85,
                rank=1,
                retrieval_method="sparse",
            ),
            RetrievalResult(
                chunk=KnowledgeChunk(id="c3", text="Document 3"),
                score=0.7,
                rank=2,
                retrieval_method="sparse",
            ),
        ]

    @pytest.mark.asyncio
    async def test_rerank_empty_results(self, rrf_reranker):
        """Test reranking empty results"""
        config = RerankConfig()
        result = await rrf_reranker.rerank("query", [], config)

        assert result.results == []
        assert result.method == RerankingMethod.RECIPROCAL_RANK

    @pytest.mark.asyncio
    async def test_rerank_boosts_common_results(self, rrf_reranker, sample_results_multi_method):
        """Test that results appearing in multiple methods get boosted"""
        config = RerankConfig(top_k=5)
        result = await rrf_reranker.rerank("query", sample_results_multi_method, config)

        # c2 appears in both dense and sparse, should be ranked high
        result_ids = [r.chunk.id for r in result.results]
        assert "c2" in result_ids

    @pytest.mark.asyncio
    async def test_rerank_assigns_rrf_scores(self, rrf_reranker, sample_results_multi_method):
        """Test that RRF scores are calculated correctly"""
        config = RerankConfig(top_k=5)
        result = await rrf_reranker.rerank("query", sample_results_multi_method, config)

        # All results should have RRF-based scores
        for r in result.results:
            assert r.score > 0

    @pytest.mark.asyncio
    async def test_rerank_respects_top_k(self, rrf_reranker, sample_results_multi_method):
        """Test that top_k is respected"""
        config = RerankConfig(top_k=2)
        result = await rrf_reranker.rerank("query", sample_results_multi_method, config)

        assert len(result.results) <= 2

    @pytest.mark.asyncio
    async def test_rerank_updates_ranks(self, rrf_reranker, sample_results_multi_method):
        """Test that ranks are updated correctly"""
        config = RerankConfig(top_k=5)
        result = await rrf_reranker.rerank("query", sample_results_multi_method, config)

        for i, r in enumerate(result.results):
            assert r.rank == i + 1

    @pytest.mark.asyncio
    async def test_rrf_constant_k(self):
        """Test different k values affect scoring"""
        # Lower k gives more weight to top ranks
        reranker_low_k = ReciprocalRankFusionReranker(k=10)
        reranker_high_k = ReciprocalRankFusionReranker(k=100)

        # Create separate result lists to avoid mutation issues
        results_low = [
            RetrievalResult(
                chunk=KnowledgeChunk(id="c1", text="Doc 1"),
                score=0.9,
                rank=1,
                retrieval_method="dense",
            ),
        ]
        results_high = [
            RetrievalResult(
                chunk=KnowledgeChunk(id="c1", text="Doc 1"),
                score=0.9,
                rank=1,
                retrieval_method="dense",
            ),
        ]

        config = RerankConfig(top_k=5)
        result_low = await reranker_low_k.rerank("q", results_low, config)
        result_high = await reranker_high_k.rerank("q", results_high, config)

        # Lower k should give higher RRF scores
        # k=10: 1/(10+1) ≈ 0.0909
        # k=100: 1/(100+1) ≈ 0.0099
        assert result_low.results[0].score > result_high.results[0].score


class TestGetReranker:
    """Tests for get_reranker factory function"""

    def test_get_cross_encoder_reranker(self):
        """Test getting cross-encoder reranker"""
        reranker = get_reranker(RerankingMethod.CROSS_ENCODER)
        assert isinstance(reranker, CrossEncoderReranker)

    def test_get_cross_encoder_with_model(self):
        """Test getting cross-encoder with custom model"""
        reranker = get_reranker(RerankingMethod.CROSS_ENCODER, model="custom-cross-encoder")
        assert isinstance(reranker, CrossEncoderReranker)
        assert reranker.model_name == "custom-cross-encoder"

    def test_get_llm_reranker(self):
        """Test getting LLM reranker"""
        mock_client = MagicMock()
        reranker = get_reranker(RerankingMethod.LLM, llm_client=mock_client, model="codellama:13b")
        assert isinstance(reranker, LLMReranker)
        assert reranker.llm_client == mock_client
        assert reranker.model == "codellama:13b"

    def test_get_rrf_reranker(self):
        """Test getting RRF reranker"""
        reranker = get_reranker(RerankingMethod.RECIPROCAL_RANK, k=30)
        assert isinstance(reranker, ReciprocalRankFusionReranker)
        assert reranker.k == 30

    def test_get_no_reranker(self):
        """Test getting no reranker"""
        reranker = get_reranker(RerankingMethod.NONE)
        assert isinstance(reranker, NoReranker)

    def test_get_reranker_default_no_reranker(self):
        """Test that unknown method returns NoReranker"""
        # Using COHERE which might not have implementation
        reranker = get_reranker(RerankingMethod.COHERE)
        assert isinstance(reranker, NoReranker)
