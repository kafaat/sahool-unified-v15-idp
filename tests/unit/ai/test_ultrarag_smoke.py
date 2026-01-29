"""
UltraRAG Smoke Tests - Verify all imports work correctly
اختبارات الدخان لـ UltraRAG - التحقق من عمل جميع الاستيرادات
"""

import pytest


class TestUltraRAGImports:
    """Basic import tests to verify module structure"""

    def test_import_models(self):
        """Test that models can be imported"""
        from shared.ai.ultrarag.models import (
            RetrievalStrategy,
            ChunkingStrategy,
            RerankingMethod,
            GenerationMode,
            KnowledgeChunk,
            KnowledgeDocument,
            RetrievalResult,
            RerankResult,
            GenerationResult,
            RAGRequest,
            RAGResult,
            RAGPipelineConfig,
            WorkflowConfig,
            WorkflowStep,
        )
        assert RetrievalStrategy.HYBRID is not None

    def test_import_retriever(self):
        """Test that retriever can be imported"""
        from shared.ai.ultrarag.retriever import (
            RetrievalConfig,
            DenseRetriever,
            SparseRetriever,
            HybridRetriever,
            AdaptiveRetriever,
        )
        assert RetrievalConfig is not None

    def test_import_reranker(self):
        """Test that reranker can be imported"""
        from shared.ai.ultrarag.reranker import (
            RerankConfig,
            CrossEncoderReranker,
            LLMReranker,
            ReciprocalRankFusionReranker,
            NoReranker,
            get_reranker,
        )
        assert get_reranker is not None

    def test_import_generator(self):
        """Test that generator can be imported"""
        from shared.ai.ultrarag.generator import (
            GeneratorConfig,
            OllamaGenerator,
        )
        assert GeneratorConfig is not None

    def test_import_pipeline(self):
        """Test that pipeline can be imported"""
        from shared.ai.ultrarag.pipeline import (
            RAGPipeline,
            RAGStage,
            StageResult,
            PipelineContext,
        )
        assert RAGPipeline is not None

    def test_import_workflow(self):
        """Test that workflow can be imported"""
        from shared.ai.ultrarag.workflow import (
            WorkflowEngine,
            WorkflowExecutionContext,
            StepExecutionResult,
        )
        assert WorkflowEngine is not None
