"""
Tests for UltraRAG Pipeline Module
اختبارات وحدة خط أنابيب UltraRAG
"""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.ultrarag.models import (
    GenerationMode,
    GenerationResult,
    KnowledgeChunk,
    RAGPipelineConfig,
    RAGRequest,
    RAGResult,
    RerankingMethod,
    RerankResult,
    RetrievalResult,
    RetrievalStrategy,
)
from shared.ai.ultrarag.pipeline import (
    PipelineContext,
    RAGPipeline,
    RAGStage,
    StageResult,
)


class TestRAGStage:
    """Tests for RAGStage enum"""

    def test_stage_values(self):
        """Test RAGStage enum values"""
        assert RAGStage.QUERY_PROCESSING.value == "query_processing"
        assert RAGStage.RETRIEVAL.value == "retrieval"
        assert RAGStage.RERANKING.value == "reranking"
        assert RAGStage.CONTEXT_BUILDING.value == "context_building"
        assert RAGStage.GENERATION.value == "generation"
        assert RAGStage.POST_PROCESSING.value == "post_processing"

    def test_all_stages_defined(self):
        """Test that all expected stages are defined"""
        stages = list(RAGStage)
        assert len(stages) == 6


class TestStageResult:
    """Tests for StageResult dataclass"""

    def test_create_result(self):
        """Test creating a stage result"""
        result = StageResult(
            stage=RAGStage.RETRIEVAL,
            success=True,
            data=["result1", "result2"],
            processing_time_ms=50.0,
        )
        assert result.stage == RAGStage.RETRIEVAL
        assert result.success is True
        assert len(result.data) == 2
        assert result.processing_time_ms == 50.0
        assert result.error is None

    def test_result_with_error(self):
        """Test creating a result with error"""
        result = StageResult(
            stage=RAGStage.GENERATION,
            success=False,
            error="LLM timeout",
        )
        assert result.success is False
        assert result.error == "LLM timeout"
        assert result.data is None

    def test_result_defaults(self):
        """Test result default values"""
        result = StageResult(stage=RAGStage.RERANKING, success=True)
        assert result.data is None
        assert result.error is None
        assert result.processing_time_ms == 0.0


class TestPipelineContext:
    """Tests for PipelineContext dataclass"""

    def test_create_context(self):
        """Test creating pipeline context"""
        request = RAGRequest(query="How to irrigate wheat?")
        ctx = PipelineContext(
            request=request,
            query="How to irrigate wheat?",
        )
        assert ctx.request == request
        assert ctx.query == "How to irrigate wheat?"
        assert ctx.expanded_queries == []
        assert ctx.retrieval_results == []
        assert ctx.rerank_result is None
        assert ctx.context_text == ""
        assert ctx.generation_result is None

    def test_context_with_results(self):
        """Test context with populated results"""
        request = RAGRequest(query="Test")
        chunk = KnowledgeChunk(id="c1", text="Content")
        retrieval_results = [RetrievalResult(chunk=chunk, score=0.9)]
        generation = GenerationResult(answer="The answer is...", confidence=0.85)

        ctx = PipelineContext(
            request=request,
            query="Test",
            retrieval_results=retrieval_results,
            generation_result=generation,
            context_text="Relevant context...",
        )
        assert len(ctx.retrieval_results) == 1
        assert ctx.generation_result.answer == "The answer is..."
        assert ctx.context_text == "Relevant context..."

    def test_context_metadata(self):
        """Test context with metadata"""
        request = RAGRequest(query="Test")
        ctx = PipelineContext(
            request=request,
            query="Test",
            metadata={"tenant_id": "farm_001", "language": "ar"},
        )
        assert ctx.metadata["tenant_id"] == "farm_001"
        assert ctx.metadata["language"] == "ar"


class TestRAGPipeline:
    """Tests for RAGPipeline class"""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store"""
        store = MagicMock()
        store.search = AsyncMock(return_value=[])
        store.add = AsyncMock()
        return store

    @pytest.fixture
    def mock_embedding_service(self):
        """Create mock embedding service"""
        service = MagicMock()
        mock_result = MagicMock()
        mock_result.vector = [0.1, 0.2, 0.3]
        service.embed = AsyncMock(return_value=mock_result)
        service.embed_batch = AsyncMock(return_value=[mock_result])
        return service

    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client"""
        client = MagicMock()
        client.generate = AsyncMock(return_value="Generated answer")
        return client

    @pytest.fixture
    def pipeline_config(self):
        """Create pipeline configuration"""
        return RAGPipelineConfig(
            name="test_pipeline",
            retrieval_strategy=RetrievalStrategy.HYBRID,
            reranking_method=RerankingMethod.NONE,
            top_k=5,
        )

    @pytest.fixture
    def pipeline(self, pipeline_config, mock_vector_store, mock_embedding_service):
        """Create pipeline instance"""
        return RAGPipeline(
            config=pipeline_config,
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )

    def test_pipeline_initialization(self, pipeline, pipeline_config):
        """Test pipeline initialization"""
        assert pipeline.config == pipeline_config
        assert pipeline._query_count == 0
        assert pipeline._total_latency_ms == 0.0

    def test_pipeline_retriever_method_dense(self, mock_vector_store, mock_embedding_service):
        """Test retriever property returns correct type for dense"""
        config = RAGPipelineConfig(
            name="test",
            retrieval_strategy=RetrievalStrategy.DENSE,
        )
        pipeline = RAGPipeline(
            config=config,
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )
        retriever = pipeline.retriever
        assert retriever is not None

    def test_pipeline_retriever_method_sparse(self, mock_vector_store, mock_embedding_service):
        """Test retriever property returns correct type for sparse"""
        config = RAGPipelineConfig(
            name="test",
            retrieval_strategy=RetrievalStrategy.SPARSE,
        )
        pipeline = RAGPipeline(
            config=config,
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )
        retriever = pipeline.retriever
        assert retriever is not None

    def test_pipeline_retriever_method_hybrid(self, mock_vector_store, mock_embedding_service):
        """Test retriever property returns correct type for hybrid"""
        config = RAGPipelineConfig(
            name="test",
            retrieval_strategy=RetrievalStrategy.HYBRID,
        )
        pipeline = RAGPipeline(
            config=config,
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )
        retriever = pipeline.retriever
        assert retriever is not None

    def test_pipeline_retriever_method_adaptive(self, mock_vector_store, mock_embedding_service):
        """Test retriever property returns correct type for adaptive"""
        config = RAGPipelineConfig(
            name="test",
            retrieval_strategy=RetrievalStrategy.ADAPTIVE,
        )
        pipeline = RAGPipeline(
            config=config,
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )
        retriever = pipeline.retriever
        assert retriever is not None

    def test_pipeline_retriever_requires_dependencies(self):
        """Test retriever creation fails without dependencies"""
        config = RAGPipelineConfig(name="test")
        pipeline = RAGPipeline(config=config)

        with pytest.raises(ValueError, match="vector_store and embedding_service required"):
            _ = pipeline.retriever()

    def test_pipeline_reranker_property(self, pipeline):
        """Test reranker property returns a reranker"""
        reranker = pipeline.reranker
        assert reranker is not None

    @pytest.mark.asyncio
    async def test_run_simple_query(self, pipeline, mock_vector_store):
        """Test running a simple query through the pipeline"""
        # Mock retrieval results
        mock_search_result = MagicMock()
        mock_search_result.id = "chunk_1"
        mock_search_result.text = "Wheat irrigation guide"
        mock_search_result.score = 0.95
        mock_search_result.metadata = {}
        mock_vector_store.search.return_value = [mock_search_result]

        request = RAGRequest(query="How to irrigate wheat?", top_k=5)
        result = await pipeline.run(request)

        assert result is not None
        assert result.success is True
        assert result.request == request
        assert result.total_time_ms > 0

    @pytest.mark.asyncio
    async def test_run_increments_query_count(self, pipeline, mock_vector_store):
        """Test that query count is incremented"""
        mock_vector_store.search.return_value = []

        request = RAGRequest(query="Test query")
        await pipeline.run(request)
        assert pipeline._query_count == 1

        await pipeline.run(request)
        assert pipeline._query_count == 2

    @pytest.mark.asyncio
    async def test_run_accumulates_latency(self, pipeline, mock_vector_store):
        """Test that latency is accumulated"""
        mock_vector_store.search.return_value = []

        request = RAGRequest(query="Test query")
        await pipeline.run(request)

        assert pipeline._total_latency_ms > 0

    @pytest.mark.asyncio
    async def test_run_with_reranking_disabled(self, mock_vector_store, mock_embedding_service):
        """Test pipeline with reranking disabled"""
        config = RAGPipelineConfig(
            name="test",
            reranking_method=RerankingMethod.NONE,
        )
        pipeline = RAGPipeline(
            config=config,
            vector_store=mock_vector_store,
            embedding_service=mock_embedding_service,
        )

        mock_vector_store.search.return_value = []
        request = RAGRequest(query="Test")
        result = await pipeline.run(request)

        assert result.success is True


class TestPipelineConfiguration:
    """Tests for pipeline configuration options"""

    def test_config_with_all_strategies(self):
        """Test pipeline can be configured with all strategies"""
        for strategy in RetrievalStrategy:
            config = RAGPipelineConfig(
                name=f"test_{strategy.value}",
                retrieval_strategy=strategy,
            )
            assert config.retrieval_strategy == strategy

    def test_config_with_all_reranking_methods(self):
        """Test pipeline can be configured with all reranking methods"""
        for method in RerankingMethod:
            config = RAGPipelineConfig(
                name=f"test_{method.value}",
                reranking_method=method,
            )
            assert config.reranking_method == method

    def test_config_with_all_generation_modes(self):
        """Test pipeline can be configured with all generation modes"""
        for mode in GenerationMode:
            config = RAGPipelineConfig(
                name=f"test_{mode.value}",
                generation_mode=mode,
            )
            assert config.generation_mode == mode
