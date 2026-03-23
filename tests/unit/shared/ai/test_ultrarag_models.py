"""
Tests for shared/ai/ultrarag/models.py
=========================================

Tests cover:
- All enums: RetrievalStrategy, ChunkingStrategy, RerankingMethod, GenerationMode,
  EntityType, RelationType
- Dataclass models: KnowledgeChunk, KnowledgeDocument, RetrievalResult, RerankResult,
  GenerationResult, RAGRequest, RAGResult, PipelineStageConfig, RAGPipelineConfig,
  WorkflowStep, WorkflowConfig, KnowledgeEntity, KnowledgeRelation,
  KnowledgeGraphResult, TriRAGConfig
- to_dict() and from_yaml() conversions
- Default values and field validation
"""

import pytest

from shared.ai.ultrarag.models import (
    ChunkingStrategy,
    EntityType,
    GenerationMode,
    GenerationResult,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeEntity,
    KnowledgeGraphResult,
    KnowledgeRelation,
    PipelineStageConfig,
    RAGPipelineConfig,
    RAGRequest,
    RAGResult,
    RelationType,
    RerankingMethod,
    RerankResult,
    RetrievalResult,
    RetrievalStrategy,
    TriRAGConfig,
    WorkflowConfig,
    WorkflowStep,
)


# ─────────────────────────────────────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestRetrievalStrategy:
    def test_all_values(self):
        assert RetrievalStrategy.DENSE.value == "dense"
        assert RetrievalStrategy.SPARSE.value == "sparse"
        assert RetrievalStrategy.HYBRID.value == "hybrid"
        assert RetrievalStrategy.ADAPTIVE.value == "adaptive"
        assert RetrievalStrategy.TRI_RAG.value == "tri_rag"

    def test_member_count(self):
        assert len(RetrievalStrategy) == 5


class TestChunkingStrategy:
    def test_all_values(self):
        assert ChunkingStrategy.FIXED_SIZE.value == "fixed_size"
        assert ChunkingStrategy.SENTENCE.value == "sentence"
        assert ChunkingStrategy.PARAGRAPH.value == "paragraph"
        assert ChunkingStrategy.SEMANTIC.value == "semantic"
        assert ChunkingStrategy.HIERARCHICAL.value == "hierarchical"
        assert ChunkingStrategy.RECURSIVE.value == "recursive"

    def test_member_count(self):
        assert len(ChunkingStrategy) == 6


class TestRerankingMethod:
    def test_all_values(self):
        assert RerankingMethod.NONE.value == "none"
        assert RerankingMethod.CROSS_ENCODER.value == "cross_encoder"
        assert RerankingMethod.LLM.value == "llm"
        assert RerankingMethod.COHERE.value == "cohere"
        assert RerankingMethod.RECIPROCAL_RANK.value == "reciprocal_rank"

    def test_member_count(self):
        assert len(RerankingMethod) == 5


class TestGenerationMode:
    def test_all_values(self):
        assert GenerationMode.STANDARD.value == "standard"
        assert GenerationMode.CHAIN_OF_THOUGHT.value == "cot"
        assert GenerationMode.SELF_REFLECTIVE.value == "self_reflective"
        assert GenerationMode.ITERATIVE.value == "iterative"

    def test_member_count(self):
        assert len(GenerationMode) == 4


class TestEntityType:
    def test_core_entities(self):
        assert EntityType.CROP.value == "crop"
        assert EntityType.PEST.value == "pest"
        assert EntityType.DISEASE.value == "disease"
        assert EntityType.SOIL.value == "soil"
        assert EntityType.WEATHER.value == "weather"

    def test_satellite_entities(self):
        assert EntityType.SENSOR.value == "sensor"
        assert EntityType.INDICATOR.value == "indicator"
        assert EntityType.METHOD.value == "method"
        assert EntityType.EVENT.value == "event"
        assert EntityType.LOCATION.value == "location"

    def test_member_count(self):
        assert len(EntityType) == 17


class TestRelationType:
    def test_core_relations(self):
        assert RelationType.AFFECTS.value == "affects"
        assert RelationType.TREATS.value == "treats"
        assert RelationType.PREVENTS.value == "prevents"
        assert RelationType.REQUIRES.value == "requires"
        assert RelationType.CAUSES.value == "causes"

    def test_satellite_relations(self):
        assert RelationType.PROVIDES.value == "provides"
        assert RelationType.INDICATES.value == "indicates"
        assert RelationType.DETECTS.value == "detects"
        assert RelationType.ANALYZES.value == "analyzes"
        assert RelationType.CLASSIFIES.value == "classifies"
        assert RelationType.EXHIBITS.value == "exhibits"

    def test_member_count(self):
        assert len(RelationType) == 18


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestKnowledgeChunk:
    def test_basic_creation(self):
        chunk = KnowledgeChunk(id="c1", text="Test content")
        assert chunk.id == "c1"
        assert chunk.text == "Test content"
        assert chunk.text_ar is None
        assert chunk.document_id == ""
        assert chunk.collection == "default"
        assert chunk.metadata == {}
        assert chunk.vector is None
        assert chunk.start_char == 0
        assert chunk.end_char == 0
        assert chunk.chunk_index == 0

    def test_to_dict(self):
        chunk = KnowledgeChunk(
            id="c1",
            text="Test",
            text_ar="اختبار",
            document_id="doc1",
            collection="crops",
            metadata={"tag": "wheat"},
            start_char=10,
            end_char=50,
            chunk_index=2,
        )
        d = chunk.to_dict()
        assert d["id"] == "c1"
        assert d["text"] == "Test"
        assert d["text_ar"] == "اختبار"
        assert d["document_id"] == "doc1"
        assert d["collection"] == "crops"
        assert d["metadata"] == {"tag": "wheat"}
        assert d["start_char"] == 10
        assert d["end_char"] == 50
        assert d["chunk_index"] == 2

    def test_to_dict_excludes_vector_and_created_at(self):
        chunk = KnowledgeChunk(id="c1", text="Test", vector=[0.1, 0.2])
        d = chunk.to_dict()
        assert "vector" not in d
        assert "created_at" not in d


class TestKnowledgeDocument:
    def test_basic_creation(self):
        doc = KnowledgeDocument(id="doc1", title="Wheat Guide")
        assert doc.id == "doc1"
        assert doc.title == "Wheat Guide"
        assert doc.content == ""
        assert doc.source == ""
        assert doc.collection == "default"
        assert doc.chunks == []

    def test_generate_id(self):
        id1 = KnowledgeDocument.generate_id()
        id2 = KnowledgeDocument.generate_id()
        assert id1.startswith("doc_")
        assert len(id1) == 16  # "doc_" + 12 hex chars
        assert id1 != id2


class TestRetrievalResult:
    def test_creation_and_to_dict(self):
        chunk = KnowledgeChunk(id="c1", text="Test", metadata={"k": "v"})
        result = RetrievalResult(chunk=chunk, score=0.95, retrieval_method="dense", rank=1)
        d = result.to_dict()
        assert d["chunk_id"] == "c1"
        assert d["text"] == "Test"
        assert d["score"] == 0.95
        assert d["method"] == "dense"
        assert d["rank"] == 1
        assert d["metadata"] == {"k": "v"}

    def test_defaults(self):
        chunk = KnowledgeChunk(id="c1", text="Test")
        result = RetrievalResult(chunk=chunk, score=0.5)
        assert result.retrieval_method == "dense"
        assert result.rank == 0


class TestRerankResult:
    def test_creation(self):
        result = RerankResult(
            results=[],
            method=RerankingMethod.CROSS_ENCODER,
            processing_time_ms=12.5,
        )
        assert result.results == []
        assert result.method == RerankingMethod.CROSS_ENCODER
        assert result.processing_time_ms == 12.5

    def test_defaults(self):
        result = RerankResult(results=[], method=RerankingMethod.NONE)
        assert result.processing_time_ms == 0.0


class TestGenerationResult:
    def test_creation(self):
        gen = GenerationResult(answer="Use drip irrigation")
        assert gen.answer == "Use drip irrigation"
        assert gen.answer_ar is None
        assert gen.confidence == 0.0
        assert gen.sources == []
        assert gen.mode == GenerationMode.STANDARD
        assert gen.tokens_used == 0

    def test_to_dict(self):
        gen = GenerationResult(
            answer="Test",
            answer_ar="اختبار",
            confidence=0.9,
            mode=GenerationMode.CHAIN_OF_THOUGHT,
            tokens_used=100,
            processing_time_ms=50.0,
        )
        d = gen.to_dict()
        assert d["answer"] == "Test"
        assert d["answer_ar"] == "اختبار"
        assert d["confidence"] == 0.9
        assert d["mode"] == "cot"
        assert d["tokens_used"] == 100
        assert d["processing_time_ms"] == 50.0
        assert d["sources"] == []

    def test_to_dict_with_sources(self):
        chunk = KnowledgeChunk(id="c1", text="Source text")
        source = RetrievalResult(chunk=chunk, score=0.8)
        gen = GenerationResult(answer="Answer", sources=[source])
        d = gen.to_dict()
        assert len(d["sources"]) == 1
        assert d["sources"][0]["chunk_id"] == "c1"


class TestRAGRequest:
    def test_defaults(self):
        req = RAGRequest(query="How to irrigate wheat?")
        assert req.query == "How to irrigate wheat?"
        assert req.query_ar is None
        assert req.collection == "default"
        assert req.top_k == 5
        assert req.rerank_top_k == 3
        assert req.strategy == RetrievalStrategy.HYBRID
        assert req.reranking == RerankingMethod.CROSS_ENCODER
        assert req.generation_mode == GenerationMode.STANDARD
        assert req.language == "en"
        assert req.include_sources is True
        assert req.max_tokens == 1024

    def test_custom_values(self):
        req = RAGRequest(
            query="Q",
            query_ar="س",
            collection="crops",
            top_k=10,
            strategy=RetrievalStrategy.TRI_RAG,
            tenant_id="tenant_1",
            language="ar",
        )
        assert req.query_ar == "س"
        assert req.collection == "crops"
        assert req.top_k == 10
        assert req.strategy == RetrievalStrategy.TRI_RAG
        assert req.tenant_id == "tenant_1"
        assert req.language == "ar"


class TestRAGResult:
    def test_to_dict_without_generation(self):
        req = RAGRequest(query="Q")
        result = RAGResult(request=req, retrieval_results=[], success=True)
        d = result.to_dict()
        assert d["query"] == "Q"
        assert d["answer"] is None
        assert d["answer_ar"] is None
        assert d["confidence"] == 0.0
        assert d["success"] is True

    def test_to_dict_with_generation(self):
        req = RAGRequest(query="Q", rerank_top_k=2)
        gen = GenerationResult(answer="A", answer_ar="ج", confidence=0.85)
        result = RAGResult(
            request=req,
            retrieval_results=[],
            generation_result=gen,
            total_time_ms=100.0,
        )
        d = result.to_dict()
        assert d["answer"] == "A"
        assert d["answer_ar"] == "ج"
        assert d["confidence"] == 0.85
        assert d["total_time_ms"] == 100.0

    def test_error_result(self):
        req = RAGRequest(query="Q")
        result = RAGResult(
            request=req,
            retrieval_results=[],
            success=False,
            error="Model unavailable",
        )
        d = result.to_dict()
        assert d["success"] is False
        assert d["error"] == "Model unavailable"


class TestRAGPipelineConfig:
    def test_defaults(self):
        config = RAGPipelineConfig(name="test-pipeline")
        assert config.name == "test-pipeline"
        assert config.version == "1.0.0"
        assert config.retrieval_strategy == RetrievalStrategy.HYBRID
        assert config.dense_weight == 0.7
        assert config.sparse_weight == 0.3
        assert config.top_k == 10
        assert config.chunking_strategy == ChunkingStrategy.RECURSIVE
        assert config.chunk_size == 500
        assert config.chunk_overlap == 50
        assert config.reranking_method == RerankingMethod.CROSS_ENCODER
        assert config.rerank_top_k == 5
        assert config.generation_mode == GenerationMode.STANDARD
        assert config.llm_model == "codellama:7b"
        assert config.llm_provider == "ollama"
        assert config.embedding_dimension == 384
        assert config.arabic_enabled is True
        assert config.cache_enabled is True
        assert config.offline_first is True

    def test_to_dict(self):
        config = RAGPipelineConfig(name="test")
        d = config.to_dict()
        assert d["name"] == "test"
        assert d["retrieval_strategy"] == "hybrid"
        assert d["chunking_strategy"] == "recursive"
        assert d["reranking_method"] == "cross_encoder"
        assert d["generation_mode"] == "standard"
        assert d["arabic_enabled"] is True
        assert d["offline_first"] is True


class TestPipelineStageConfig:
    def test_creation(self):
        stage = PipelineStageConfig(name="retrieve", type="retrieval")
        assert stage.name == "retrieve"
        assert stage.type == "retrieval"
        assert stage.enabled is True
        assert stage.config == {}
        assert stage.conditions == {}

    def test_disabled_stage(self):
        stage = PipelineStageConfig(name="s1", type="rerank", enabled=False)
        assert stage.enabled is False


class TestWorkflowStep:
    def test_creation(self):
        step = WorkflowStep(id="step1", type="retrieve", name="Get crops")
        assert step.id == "step1"
        assert step.type == "retrieve"
        assert step.name == "Get crops"
        assert step.next_step is None
        assert step.on_success is None
        assert step.on_failure is None
        assert step.condition is None
        assert step.loop_config is None


class TestWorkflowConfig:
    def test_from_yaml_basic(self):
        yaml_dict = {
            "id": "wf1",
            "name": "Crop Advisory",
            "name_ar": "استشارة المحاصيل",
            "description": "Advisory workflow",
            "version": "2.0.0",
            "steps": [
                {
                    "id": "s1",
                    "type": "retrieve",
                    "name": "Get crop data",
                    "next_step": "s2",
                },
                {
                    "id": "s2",
                    "type": "generate",
                    "name": "Generate advice",
                },
            ],
            "entry_point": "s1",
            "variables": {"top_k": 5},
        }
        config = WorkflowConfig.from_yaml(yaml_dict)
        assert config.id == "wf1"
        assert config.name == "Crop Advisory"
        assert config.name_ar == "استشارة المحاصيل"
        assert config.version == "2.0.0"
        assert len(config.steps) == 2
        assert config.steps[0].id == "s1"
        assert config.steps[0].next_step == "s2"
        assert config.entry_point == "s1"
        assert config.variables == {"top_k": 5}

    def test_from_yaml_defaults(self):
        yaml_dict = {
            "name": "Simple",
            "steps": [{"id": "s1", "type": "retrieve", "name": "Step 1"}],
        }
        config = WorkflowConfig.from_yaml(yaml_dict)
        assert config.id.startswith("workflow_")
        assert config.name == "Simple"
        assert config.version == "1.0.0"
        assert config.entry_point == "s1"

    def test_from_yaml_no_steps(self):
        yaml_dict = {"name": "Empty"}
        config = WorkflowConfig.from_yaml(yaml_dict)
        assert config.steps == []
        assert config.entry_point == ""


class TestKnowledgeEntity:
    def test_creation(self):
        entity = KnowledgeEntity(id="e1", name="Wheat")
        assert entity.id == "e1"
        assert entity.name == "Wheat"
        assert entity.name_ar is None
        assert entity.entity_type == EntityType.CROP
        assert entity.description == ""
        assert entity.aliases == []
        assert entity.properties == {}
        assert entity.embedding is None

    def test_generate_id(self):
        id1 = KnowledgeEntity.generate_id()
        assert id1.startswith("entity_")
        assert len(id1) == 19  # "entity_" + 12 hex


class TestKnowledgeRelation:
    def test_creation(self):
        rel = KnowledgeRelation(
            id="r1",
            source_id="e1",
            target_id="e2",
            relation_type=RelationType.AFFECTS,
        )
        assert rel.id == "r1"
        assert rel.source_id == "e1"
        assert rel.target_id == "e2"
        assert rel.relation_type == RelationType.AFFECTS
        assert rel.weight == 1.0
        assert rel.properties == {}
        assert rel.evidence == []

    def test_generate_id(self):
        id1 = KnowledgeRelation.generate_id()
        assert id1.startswith("rel_")
        assert len(id1) == 16  # "rel_" + 12 hex


class TestKnowledgeGraphResult:
    def test_creation(self):
        result = KnowledgeGraphResult(entities=[], relations=[])
        assert result.entities == []
        assert result.relations == []
        assert result.paths == []
        assert result.score == 0.0
        assert result.reasoning == ""
        assert result.reasoning_ar == ""


class TestTriRAGConfig:
    def test_defaults(self):
        config = TriRAGConfig()
        assert config.dense_weight == 0.4
        assert config.sparse_weight == 0.3
        assert config.kg_weight == 0.3
        assert config.dense_top_k == 10
        assert config.sparse_top_k == 10
        assert config.kg_max_hops == 2
        assert config.kg_top_entities == 5
        assert config.rrf_k == 60
        assert config.final_top_k == 10
        assert config.include_kg_reasoning is True
        assert config.max_context_tokens == 4096

    def test_validate_valid_weights(self):
        config = TriRAGConfig(dense_weight=0.4, sparse_weight=0.3, kg_weight=0.3)
        assert config.validate() is True

    def test_validate_invalid_weights(self):
        config = TriRAGConfig(dense_weight=0.5, sparse_weight=0.5, kg_weight=0.5)
        assert config.validate() is False

    def test_validate_near_one(self):
        config = TriRAGConfig(dense_weight=0.333, sparse_weight=0.333, kg_weight=0.334)
        assert config.validate() is True
