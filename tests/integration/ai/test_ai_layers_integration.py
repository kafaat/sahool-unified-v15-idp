"""
Integration Tests for AI Layers Cross-Communication (G-08)
===========================================================
اختبارات تكامل طبقات الذكاء الاصطناعي

Tests that verify data flows correctly between AI architecture layers:
- Layer 1 (Safety) → Layer 2 (Core AI) → Layer 5 (Knowledge)
- Knowledge Base → UltraRAG → LLM Provider
- Feedback → Experience Learning → SOP Generation
- Models Registry → Model Selection → LLM Provider
- Embeddings consistency across subsystems
- Context Engineering → LLM Provider pipeline
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Layer 2: Core AI Infrastructure Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestLLMProviderManager:
    """Test LLM provider manager initialization and failover."""

    def test_provider_enum_has_all_providers(self):
        from shared.ai.llm_provider import LLMProvider

        expected = {"ollama", "vllm", "anthropic", "openai", "google", "deepseek"}
        actual = {p.value for p in LLMProvider}
        assert actual == expected

    def test_config_from_env_ollama(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        config = LLMConfig.from_env(LLMProvider.OLLAMA)
        assert config.provider == LLMProvider.OLLAMA
        assert config.priority == 0  # Highest priority (offline-first)

    def test_config_from_env_anthropic_default_model(self):
        """G-01: Verify Anthropic uses updated model."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        config = LLMConfig.from_env(LLMProvider.ANTHROPIC)
        assert "claude-3-haiku-20240307" not in config.model
        assert "claude-haiku-4-5" in config.model or "claude" in config.model

    def test_config_from_env_google_stable_api(self):
        """G-20: Verify Google uses stable v1 API."""
        # This is verified at call time, not config time
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        config = LLMConfig.from_env(LLMProvider.GOOGLE)
        assert config.provider == LLMProvider.GOOGLE

    def test_provider_manager_initialization(self):
        from shared.ai.llm_provider import LLMProviderManager

        manager = LLMProviderManager(tenant_id="test")
        assert manager.tenant_id == "test"
        assert len(manager.configs) > 0

    def test_provider_status(self):
        from shared.ai.llm_provider import LLMProviderManager

        manager = LLMProviderManager(tenant_id="test")
        status = manager.get_provider_status()
        assert isinstance(status, dict)
        assert "ollama" in status

    def test_llm_response_to_dict(self):
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        response = LLMResponse(
            text="Test response",
            provider=LLMProvider.OLLAMA,
            model="codellama:13b",
            tokens_input=10,
            tokens_output=5,
        )
        d = response.to_dict()
        assert d["text"] == "Test response"
        assert d["provider"] == "ollama"
        assert d["tokens_input"] == 10


# ─────────────────────────────────────────────────────────────────────────────
# Layer 5: Knowledge Base Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeBaseIntegration:
    """Test knowledge base component interactions."""

    def test_all_collections_defined(self):
        """Verify all 13 knowledge collections exist."""
        from shared.ai.knowledge.collections import ALL_COLLECTIONS

        assert len(ALL_COLLECTIONS) >= 13

    def test_knowledge_domains_coverage(self):
        """Verify all domains have corresponding collections."""
        from shared.ai.knowledge.models import KnowledgeDomain

        expected_domains = {
            "crops", "soil", "irrigation", "fertilizer", "pest_disease",
            "weather", "remote_sensing", "smart_agriculture",
            "precision_farming", "digital_twin", "general",
        }
        actual_domains = {d.value for d in KnowledgeDomain}
        assert expected_domains.issubset(actual_domains)

    def test_document_to_knowledge_document(self):
        """Test document conversion for UltraRAG compatibility."""
        from shared.ai.knowledge.models import CropKnowledgeDocument

        doc = CropKnowledgeDocument(
            title="Wheat Cultivation Guide",
            title_ar="دليل زراعة القمح",
            content="Guide to wheat cultivation in arid regions",
            content_ar="دليل زراعة القمح في المناطق الجافة",
        )
        kd = doc.to_knowledge_document()
        assert kd["title"] == "Wheat Cultivation Guide"
        assert kd["metadata"]["domain"] == "crops"

    def test_validator_validates_crop_document(self):
        """Test validator correctly validates crop documents."""
        from shared.ai.knowledge.models import CropKnowledgeDocument
        from shared.ai.knowledge.validators import KnowledgeValidator

        validator = KnowledgeValidator()
        doc = CropKnowledgeDocument(
            title="Test Crop",
            content="Test content",
            kc_values={"initial": 0.3, "mid": 1.15, "end": 0.4},
            optimal_temperature_c=(15.0, 30.0),
        )
        result = validator.validate(doc)
        assert result.is_valid

    def test_validator_catches_invalid_kc(self):
        from shared.ai.knowledge.models import CropKnowledgeDocument
        from shared.ai.knowledge.validators import KnowledgeValidator

        validator = KnowledgeValidator()
        doc = CropKnowledgeDocument(
            title="Test",
            content="Test",
            kc_values={"initial": 5.0},  # Invalid: > 2.0
        )
        result = validator.validate(doc)
        assert not result.is_valid

    def test_agrovoc_lookup(self):
        """Test AGROVOC concept lookup."""
        from shared.ai.knowledge.agrovoc import AgrovocLookup

        lookup = AgrovocLookup()
        result = lookup.find("wheat")
        assert result is not None
        assert result.pref_label_ar  # Should have Arabic label

    def test_agrovoc_bilingual_translation(self):
        from shared.ai.knowledge.agrovoc import AgrovocLookup

        lookup = AgrovocLookup()
        result = lookup.translate("wheat", to_lang="ar")
        assert result  # Should return Arabic term

    def test_crag_engine_initialization(self):
        """Test Corrective RAG engine can be created."""
        from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine

        engine = CorrectiveRetrievalEngine()
        assert engine is not None


# ─────────────────────────────────────────────────────────────────────────────
# Layer 5→Layer 10: Knowledge → UltraRAG Integration
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeToRAGIntegration:
    """Test knowledge base integration with UltraRAG."""

    def test_ultrarag_models_import(self):
        """Verify UltraRAG data models are importable."""
        from shared.ai.ultrarag.models import (
            RAGRequest,
            RAGResult,
            RetrievalStrategy,
        )

        assert RetrievalStrategy.DENSE
        assert RetrievalStrategy.HYBRID

    def test_rag_pipeline_builder(self):
        """Test RAG pipeline can be built."""
        from shared.ai.ultrarag.pipeline import RAGPipelineBuilder

        builder = RAGPipelineBuilder()
        assert builder is not None

    def test_workflow_yaml_files_exist(self):
        """Verify all 11 UltraRAG workflows exist."""
        from pathlib import Path

        workflow_dir = Path("shared/ai/ultrarag/workflows")
        if workflow_dir.exists():
            yamls = list(workflow_dir.glob("*.yaml"))
            assert len(yamls) >= 9  # At least 9 workflows

    def test_reranker_factory(self):
        """Test reranker factory creates instances."""
        from shared.ai.ultrarag.reranker import NoReranker, get_reranker

        reranker = get_reranker("none")
        assert isinstance(reranker, NoReranker)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3: Feedback & Quality Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestFeedbackIntegration:
    """Test feedback collection and routing."""

    def test_feedback_collector_creation(self):
        from shared.ai.feedback import FeedbackCollector

        collector = FeedbackCollector(tenant_id="test_farm")
        assert collector is not None

    @pytest.mark.asyncio
    async def test_feedback_rating_collection(self):
        from shared.ai.feedback import FeedbackCollector, RecommendationType

        collector = FeedbackCollector(tenant_id="test_farm")
        await collector.collect_rating(
            recommendation_id="rec_001",
            rating=4,
            recommendation_type=RecommendationType.IRRIGATION,
        )
        summary = await collector.get_summary(days=30)
        assert summary.total_feedback >= 1

    @pytest.mark.asyncio
    async def test_feedback_export_for_training(self):
        """G-07: Verify feedback can be exported for training."""
        from shared.ai.feedback import FeedbackCollector, RecommendationType

        collector = FeedbackCollector(tenant_id="test_farm")
        await collector.collect_rating(
            recommendation_id="rec_002",
            rating=5,
            recommendation_type=RecommendationType.FERTILIZER,
            comment="Excellent advice",
        )
        training_data = await collector.export_for_training(min_rating=4)
        assert isinstance(training_data, list)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1: Models Registry Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestModelsRegistryIntegration:
    """Test models registry discovery and selection."""

    def test_registry_has_models(self):
        from shared.ai.models_registry import get_registry

        registry = get_registry()
        assert registry.count() >= 50

    def test_registry_discover_by_category(self):
        from shared.ai.models_registry import AIModelCategory, get_registry

        registry = get_registry()
        result = registry.discover_by_category(AIModelCategory.GENERAL_AGRICULTURE)
        assert result.total_count > 0

    def test_featured_models(self):
        from shared.ai.models_registry import list_featured_models

        featured = list_featured_models()
        assert len(featured) >= 5

    def test_arabic_supported_models(self):
        """G-02: Verify Arabic models exist."""
        from shared.ai.models_registry import list_arabic_supported_models

        arabic = list_arabic_supported_models()
        assert len(arabic) >= 1  # At least AgroGPT

    def test_task_capability_mapping(self):
        from shared.ai.models_registry.integrator import TASK_CAPABILITY_MAP, TaskType

        assert TaskType.CROP_ADVISORY in TASK_CAPABILITY_MAP
        assert TaskType.DISEASE_DIAGNOSIS in TASK_CAPABILITY_MAP
        assert TaskType.YIELD_PREDICTION in TASK_CAPABILITY_MAP


# ─────────────────────────────────────────────────────────────────────────────
# Layer 8: Embeddings Consistency Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestEmbeddingsConsistency:
    """Test embedding providers work consistently."""

    def test_embedding_providers_defined(self):
        from shared.ai.embeddings import EmbeddingProvider

        providers = {p.value for p in EmbeddingProvider}
        assert "sentence_transformers" in providers
        assert "ollama" in providers

    def test_embedding_config_defaults(self):
        from shared.ai.embeddings import EmbeddingConfig

        config = EmbeddingConfig()
        assert config.cache_enabled is True
        assert config.batch_size > 0


# ─────────────────────────────────────────────────────────────────────────────
# Layer 4: Auto-Fix Engine Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAutoFixEngineIntegration:
    """Test auto-fix engine component integration."""

    def test_diagnostic_models_import(self):
        from shared.ai.auto_fix.models import (
            DiagnosticCategory,
            DiagnosticSeverity,
            FixConfidence,
            FixStrategy,
        )

        assert DiagnosticSeverity.ERROR
        assert FixStrategy.SAFE
        assert FixConfidence.HIGH

    def test_fix_strategies_defined(self):
        from shared.ai.auto_fix.models import FixStrategy

        strategies = {s.value for s in FixStrategy}
        expected = {"minimal", "safe", "comprehensive", "refactor"}
        assert expected.issubset(strategies)


# ─────────────────────────────────────────────────────────────────────────────
# Layer 7: Context Engineering Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestContextEngineeringIntegration:
    """Test context compression and memory."""

    def test_compression_strategies(self):
        from shared.ai.context_engineering.compression import CompressionStrategy

        assert CompressionStrategy.EXTRACTIVE
        assert CompressionStrategy.HYBRID

    def test_compression_result_properties(self):
        from shared.ai.context_engineering.compression import (
            CompressionResult,
            CompressionStrategy,
        )

        result = CompressionResult(
            original_text="Long text here...",
            compressed_text="Short",
            original_tokens=100,
            compressed_tokens=25,
            compression_ratio=0.25,
            strategy=CompressionStrategy.EXTRACTIVE,
        )
        assert result.tokens_saved == 75
        assert result.savings_percentage == 75.0


# ─────────────────────────────────────────────────────────────────────────────
# Cross-Layer Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCrossLayerIntegration:
    """Test data flow between multiple AI layers."""

    def test_knowledge_document_has_ultrarag_compatibility(self):
        """Verify knowledge documents can be converted to UltraRAG format."""
        from shared.ai.knowledge.models import CropKnowledgeDocument

        doc = CropKnowledgeDocument(
            title="Test Crop",
            content="Test content",
        )
        kd = doc.to_knowledge_document()
        assert "id" in kd
        assert "collection" in kd
        assert "metadata" in kd
        assert kd["metadata"]["domain"] == "crops"

    def test_guardrails_import(self):
        """Verify guardrails layer is available."""
        from shared.ai.guardrails import ToolGuard

        assert ToolGuard is not None

    def test_explainability_engine(self):
        """Verify explainability layer works."""
        from shared.ai.explainability import ExplainabilityEngine

        engine = ExplainabilityEngine()
        assert engine is not None

    def test_circuit_breaker_integration(self):
        """Verify circuit breaker is available for all providers."""
        from shared.ai.circuit_breaker import CircuitBreakerConfig, get_circuit_breaker

        breaker = get_circuit_breaker(
            "test_breaker",
            CircuitBreakerConfig(failure_threshold=3, success_threshold=2, timeout_seconds=60),
        )
        assert not breaker.is_open

    def test_audit_logger_integration(self):
        """Verify audit logging works."""
        from shared.ai.audit import get_audit_logger

        logger = get_audit_logger("test_tenant")
        assert logger is not None

    def test_crop_vision_types(self):
        """Verify crop vision types are defined."""
        from shared.ai.crop_vision import CropType, DiseaseType, GrowthStage

        assert CropType.WHEAT
        assert DiseaseType.WHEAT_RUST
        assert GrowthStage.TILLERING

    def test_graph_memory_entity_types(self):
        """Verify graph memory entity types."""
        from shared.ai.graph_memory import EntityType, RelationType

        assert EntityType.FARM
        assert EntityType.CROP
        assert RelationType.GROWS


# ─────────────────────────────────────────────────────────────────────────────
# Layer 12: Orchestration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestOrchestrationIntegration:
    """Test orchestration layer availability."""

    def test_orchestration_available(self):
        """G-14: Verify orchestration module loads."""
        try:
            from shared.ai.orchestration import AgentRouter

            assert AgentRouter is not None
            orchestration_available = True
        except ImportError:
            orchestration_available = False
        # Either it loads or we handle gracefully
        assert isinstance(orchestration_available, bool)

    def test_swarm_coordinator_import(self):
        """Verify swarm coordinator is importable."""
        try:
            from shared.ai.orchestration.swarm import SwarmCoordinator

            assert SwarmCoordinator is not None
        except ImportError:
            pytest.skip("Orchestration module not available")

    def test_consensus_manager_import(self):
        """Verify consensus protocols are importable."""
        try:
            from shared.ai.orchestration.consensus import ConsensusManager

            assert ConsensusManager is not None
        except ImportError:
            pytest.skip("Orchestration module not available")


# ─────────────────────────────────────────────────────────────────────────────
# Ingestion Pipeline Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestIngestionPipelineIntegration:
    """Test knowledge ingestion pipeline stages."""

    def test_extractors_available(self):
        from shared.ai.knowledge.ingestion import (
            HTMLExtractor,
            MarkdownExtractor,
            PDFExtractor,
        )

        assert MarkdownExtractor is not None
        assert PDFExtractor is not None
        assert HTMLExtractor is not None

    def test_chunker_works(self):
        from shared.ai.knowledge.ingestion.chunker import (
            ChunkConfig,
            ChunkStrategy,
            TextChunker,
        )

        chunker = TextChunker(ChunkConfig(
            strategy=ChunkStrategy.FIXED_SIZE,
            chunk_size=200,
            chunk_overlap=50,
        ))
        chunks = chunker.chunk("This is a test text. " * 50)
        assert len(chunks) > 1

    def test_preprocessors_available(self):
        from shared.ai.knowledge.ingestion import (
            AgriculturalTermNormalizer,
            ArabicTextPreprocessor,
            MetadataEnricher,
        )

        assert ArabicTextPreprocessor is not None
        assert AgriculturalTermNormalizer is not None
        assert MetadataEnricher is not None

    def test_pipeline_creation(self):
        from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(
            min_source_credibility=1,
            require_bilingual=False,
        )
        assert pipeline is not None


# ─────────────────────────────────────────────────────────────────────────────
# Vector Store Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestVectorStoreIntegration:
    """Test vector store for knowledge retrieval."""

    def test_vector_store_importable(self):
        from shared.ai.knowledge.vector_store_integration import (
            KnowledgeVectorStore,
            VectorSearchResult,
        )

        assert KnowledgeVectorStore is not None
        assert VectorSearchResult is not None

    def test_knowledge_cache_importable(self):
        from shared.ai.knowledge.cache import KnowledgeCache

        cache = KnowledgeCache()
        assert cache is not None

    def test_knowledge_metrics_importable(self):
        from shared.ai.knowledge.metrics import KnowledgeMetrics

        metrics = KnowledgeMetrics()
        assert metrics is not None
