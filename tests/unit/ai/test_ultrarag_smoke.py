"""
UltraRAG Smoke Tests - Verify all imports work correctly
اختبارات الدخان لـ UltraRAG - التحقق من عمل جميع الاستيرادات
"""

import sys

import pytest


class TestUltraRAGImports:
    """Basic import tests to verify module structure"""

    def test_import_models(self):
        """Test that models can be imported"""
        try:
            from shared.ai.ultrarag.models import (
                ChunkingStrategy,
                GenerationMode,
                GenerationResult,
                KnowledgeChunk,
                KnowledgeDocument,
                RAGPipelineConfig,
                RAGRequest,
                RAGResult,
                RerankingMethod,
                RerankResult,
                RetrievalResult,
                RetrievalStrategy,
                WorkflowConfig,
                WorkflowStep,
            )

            assert RetrievalStrategy.HYBRID is not None
        except Exception as e:
            pytest.fail(f"Failed to import models: {type(e).__name__}: {e}")

    def test_import_retriever(self):
        """Test that retriever can be imported"""
        try:
            from shared.ai.ultrarag.retriever import (
                AdaptiveRetriever,
                DenseRetriever,
                HybridRetriever,
                RetrievalConfig,
                SparseRetriever,
            )

            assert RetrievalConfig is not None
        except Exception as e:
            pytest.fail(f"Failed to import retriever: {type(e).__name__}: {e}")

    def test_import_reranker(self):
        """Test that reranker can be imported"""
        try:
            from shared.ai.ultrarag.reranker import (
                CrossEncoderReranker,
                LLMReranker,
                NoReranker,
                ReciprocalRankFusionReranker,
                RerankConfig,
                get_reranker,
            )

            assert get_reranker is not None
        except Exception as e:
            pytest.fail(f"Failed to import reranker: {type(e).__name__}: {e}")

    def test_import_generator(self):
        """Test that generator can be imported"""
        try:
            from shared.ai.ultrarag.generator import (
                GeneratorConfig,
                OllamaGenerator,
            )

            assert GeneratorConfig is not None
        except Exception as e:
            pytest.fail(f"Failed to import generator: {type(e).__name__}: {e}")

    def test_import_pipeline(self):
        """Test that pipeline can be imported"""
        try:
            from shared.ai.ultrarag.pipeline import (
                PipelineContext,
                RAGPipeline,
                RAGStage,
                StageResult,
            )

            assert RAGPipeline is not None
        except Exception as e:
            pytest.fail(f"Failed to import pipeline: {type(e).__name__}: {e}")

    def test_import_workflow(self):
        """Test that workflow can be imported"""
        try:
            from shared.ai.ultrarag.workflow import (
                StepExecutionResult,
                WorkflowEngine,
                WorkflowExecutionContext,
            )

            assert WorkflowEngine is not None
        except Exception as e:
            pytest.fail(f"Failed to import workflow: {type(e).__name__}: {e}")
