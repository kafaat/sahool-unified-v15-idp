"""
Tests for UltraRAG Models Module
اختبارات وحدة نماذج UltraRAG
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from shared.ai.ultrarag.models import (
    ChunkingStrategy,
    GenerationMode,
    GenerationResult,
    KnowledgeChunk,
    KnowledgeDocument,
    PipelineStageConfig,
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


class TestEnums:
    """Tests for enum types"""

    def test_retrieval_strategy_values(self):
        """Test RetrievalStrategy enum values"""
        assert RetrievalStrategy.DENSE.value == "dense"
        assert RetrievalStrategy.SPARSE.value == "sparse"
        assert RetrievalStrategy.HYBRID.value == "hybrid"
        assert RetrievalStrategy.ADAPTIVE.value == "adaptive"

    def test_chunking_strategy_values(self):
        """Test ChunkingStrategy enum values"""
        assert ChunkingStrategy.FIXED_SIZE.value == "fixed_size"
        assert ChunkingStrategy.SENTENCE.value == "sentence"
        assert ChunkingStrategy.PARAGRAPH.value == "paragraph"
        assert ChunkingStrategy.SEMANTIC.value == "semantic"
        assert ChunkingStrategy.HIERARCHICAL.value == "hierarchical"
        assert ChunkingStrategy.RECURSIVE.value == "recursive"

    def test_reranking_method_values(self):
        """Test RerankingMethod enum values"""
        assert RerankingMethod.NONE.value == "none"
        assert RerankingMethod.CROSS_ENCODER.value == "cross_encoder"
        assert RerankingMethod.LLM.value == "llm"
        assert RerankingMethod.COHERE.value == "cohere"
        assert RerankingMethod.RECIPROCAL_RANK.value == "reciprocal_rank"

    def test_generation_mode_values(self):
        """Test GenerationMode enum values"""
        assert GenerationMode.STANDARD.value == "standard"
        assert GenerationMode.CHAIN_OF_THOUGHT.value == "cot"
        assert GenerationMode.SELF_REFLECTIVE.value == "self_reflective"
        assert GenerationMode.ITERATIVE.value == "iterative"


class TestKnowledgeChunk:
    """Tests for KnowledgeChunk dataclass"""

    def test_create_chunk(self):
        """Test creating a knowledge chunk"""
        chunk = KnowledgeChunk(
            id="chunk_001",
            text="This is test content",
            document_id="doc_001",
            collection="test_collection",
        )
        assert chunk.id == "chunk_001"
        assert chunk.text == "This is test content"
        assert chunk.document_id == "doc_001"
        assert chunk.collection == "test_collection"

    def test_chunk_with_arabic(self):
        """Test chunk with Arabic text"""
        chunk = KnowledgeChunk(
            id="chunk_002",
            text="English content",
            text_ar="محتوى عربي",
            document_id="doc_001",
        )
        assert chunk.text_ar == "محتوى عربي"

    def test_chunk_with_metadata(self):
        """Test chunk with metadata"""
        metadata = {"crop": "wheat", "region": "central"}
        chunk = KnowledgeChunk(
            id="chunk_003",
            text="Wheat irrigation advice",
            metadata=metadata,
        )
        assert chunk.metadata["crop"] == "wheat"
        assert chunk.metadata["region"] == "central"

    def test_chunk_with_vector(self):
        """Test chunk with embedding vector"""
        vector = [0.1, 0.2, 0.3, 0.4]
        chunk = KnowledgeChunk(
            id="chunk_004",
            text="Test content",
            vector=vector,
        )
        assert chunk.vector == vector
        assert len(chunk.vector) == 4

    def test_chunk_to_dict(self):
        """Test chunk serialization to dictionary"""
        chunk = KnowledgeChunk(
            id="chunk_005",
            text="Test content",
            text_ar="محتوى اختباري",
            document_id="doc_001",
            collection="test",
            metadata={"key": "value"},
            start_char=0,
            end_char=100,
            chunk_index=0,
        )
        d = chunk.to_dict()
        assert d["id"] == "chunk_005"
        assert d["text"] == "Test content"
        assert d["text_ar"] == "محتوى اختباري"
        assert d["document_id"] == "doc_001"
        assert d["collection"] == "test"
        assert d["metadata"]["key"] == "value"

    def test_chunk_default_values(self):
        """Test chunk default values"""
        chunk = KnowledgeChunk(id="chunk_006", text="Test")
        assert chunk.text_ar is None
        assert chunk.document_id == ""
        assert chunk.collection == "default"
        assert chunk.metadata == {}
        assert chunk.vector is None
        assert chunk.start_char == 0
        assert chunk.end_char == 0
        assert chunk.chunk_index == 0
        assert isinstance(chunk.created_at, datetime)


class TestKnowledgeDocument:
    """Tests for KnowledgeDocument dataclass"""

    def test_create_document(self):
        """Test creating a knowledge document"""
        doc = KnowledgeDocument(
            id="doc_001",
            title="Wheat Cultivation Guide",
            content="Detailed guide for wheat cultivation...",
            source="agricultural_handbook",
        )
        assert doc.id == "doc_001"
        assert doc.title == "Wheat Cultivation Guide"
        assert doc.content == "Detailed guide for wheat cultivation..."
        assert doc.source == "agricultural_handbook"

    def test_document_with_arabic(self):
        """Test document with Arabic content"""
        doc = KnowledgeDocument(
            id="doc_002",
            title="Irrigation Guide",
            title_ar="دليل الري",
            content="Irrigation best practices",
            content_ar="أفضل ممارسات الري",
        )
        assert doc.title_ar == "دليل الري"
        assert doc.content_ar == "أفضل ممارسات الري"

    def test_document_with_chunks(self):
        """Test document with chunks"""
        chunks = [
            KnowledgeChunk(id="c1", text="Chunk 1", document_id="doc_003"),
            KnowledgeChunk(id="c2", text="Chunk 2", document_id="doc_003"),
        ]
        doc = KnowledgeDocument(
            id="doc_003",
            title="Test Doc",
            chunks=chunks,
        )
        assert len(doc.chunks) == 2
        assert doc.chunks[0].id == "c1"

    def test_document_generate_id(self):
        """Test document ID generation"""
        id1 = KnowledgeDocument.generate_id()
        id2 = KnowledgeDocument.generate_id()
        assert id1.startswith("doc_")
        assert id2.startswith("doc_")
        assert id1 != id2
        assert len(id1) == 16  # "doc_" + 12 hex chars

    def test_document_default_values(self):
        """Test document default values"""
        doc = KnowledgeDocument(id="doc_004", title="Test")
        assert doc.title_ar is None
        assert doc.content == ""
        assert doc.content_ar is None
        assert doc.source == ""
        assert doc.collection == "default"
        assert doc.metadata == {}
        assert doc.chunks == []


class TestRetrievalResult:
    """Tests for RetrievalResult dataclass"""

    def test_create_result(self):
        """Test creating a retrieval result"""
        chunk = KnowledgeChunk(id="c1", text="Test content")
        result = RetrievalResult(
            chunk=chunk,
            score=0.95,
            retrieval_method="dense",
            rank=1,
        )
        assert result.chunk.id == "c1"
        assert result.score == 0.95
        assert result.retrieval_method == "dense"
        assert result.rank == 1

    def test_result_to_dict(self):
        """Test result serialization"""
        chunk = KnowledgeChunk(
            id="c2",
            text="English text",
            text_ar="نص عربي",
            metadata={"source": "test"},
        )
        result = RetrievalResult(
            chunk=chunk,
            score=0.85,
            retrieval_method="hybrid",
            rank=2,
        )
        d = result.to_dict()
        assert d["chunk_id"] == "c2"
        assert d["text"] == "English text"
        assert d["text_ar"] == "نص عربي"
        assert d["score"] == 0.85
        assert d["method"] == "hybrid"
        assert d["rank"] == 2
        assert d["metadata"]["source"] == "test"

    def test_result_default_values(self):
        """Test result default values"""
        chunk = KnowledgeChunk(id="c3", text="Test")
        result = RetrievalResult(chunk=chunk, score=0.5)
        assert result.retrieval_method == "dense"
        assert result.rank == 0


class TestRerankResult:
    """Tests for RerankResult dataclass"""

    def test_create_rerank_result(self):
        """Test creating a rerank result"""
        chunk1 = KnowledgeChunk(id="c1", text="Text 1")
        chunk2 = KnowledgeChunk(id="c2", text="Text 2")
        results = [
            RetrievalResult(chunk=chunk1, score=0.9, rank=1),
            RetrievalResult(chunk=chunk2, score=0.8, rank=2),
        ]
        rerank = RerankResult(
            results=results,
            method=RerankingMethod.CROSS_ENCODER,
            processing_time_ms=50.5,
        )
        assert len(rerank.results) == 2
        assert rerank.method == RerankingMethod.CROSS_ENCODER
        assert rerank.processing_time_ms == 50.5

    def test_rerank_result_default_time(self):
        """Test rerank result default processing time"""
        rerank = RerankResult(
            results=[],
            method=RerankingMethod.LLM,
        )
        assert rerank.processing_time_ms == 0.0


class TestGenerationResult:
    """Tests for GenerationResult dataclass"""

    def test_create_generation_result(self):
        """Test creating a generation result"""
        result = GenerationResult(
            answer="The recommended irrigation amount is 25mm.",
            answer_ar="كمية الري الموصى بها هي 25 ملم.",
            confidence=0.92,
            reasoning="Based on soil moisture and weather conditions",
            mode=GenerationMode.CHAIN_OF_THOUGHT,
            tokens_used=150,
            processing_time_ms=500.0,
        )
        assert "25mm" in result.answer
        assert "25 ملم" in result.answer_ar
        assert result.confidence == 0.92
        assert result.mode == GenerationMode.CHAIN_OF_THOUGHT
        assert result.tokens_used == 150

    def test_generation_result_with_sources(self):
        """Test generation result with sources"""
        chunk = KnowledgeChunk(id="src1", text="Source content")
        sources = [RetrievalResult(chunk=chunk, score=0.95)]
        result = GenerationResult(
            answer="Answer based on sources",
            sources=sources,
        )
        assert len(result.sources) == 1
        assert result.sources[0].chunk.id == "src1"

    def test_generation_result_to_dict(self):
        """Test generation result serialization"""
        result = GenerationResult(
            answer="Test answer",
            answer_ar="إجابة اختبارية",
            confidence=0.85,
            mode=GenerationMode.SELF_REFLECTIVE,
            tokens_used=100,
            processing_time_ms=250.0,
        )
        d = result.to_dict()
        assert d["answer"] == "Test answer"
        assert d["answer_ar"] == "إجابة اختبارية"
        assert d["confidence"] == 0.85
        assert d["mode"] == "self_reflective"
        assert d["tokens_used"] == 100

    def test_generation_result_defaults(self):
        """Test generation result default values"""
        result = GenerationResult(answer="Simple answer")
        assert result.answer_ar is None
        assert result.confidence == 0.0
        assert result.sources == []
        assert result.reasoning is None
        assert result.mode == GenerationMode.STANDARD
        assert result.tokens_used == 0


class TestRAGRequest:
    """Tests for RAGRequest dataclass"""

    def test_create_request(self):
        """Test creating a RAG request"""
        request = RAGRequest(
            query="How to irrigate wheat?",
            query_ar="كيف يتم ري القمح؟",
            collection="agriculture",
            top_k=10,
            tenant_id="farm_001",
        )
        assert request.query == "How to irrigate wheat?"
        assert request.query_ar == "كيف يتم ري القمح؟"
        assert request.collection == "agriculture"
        assert request.top_k == 10
        assert request.tenant_id == "farm_001"

    def test_request_with_strategy(self):
        """Test request with specific strategy"""
        request = RAGRequest(
            query="Test query",
            strategy=RetrievalStrategy.ADAPTIVE,
            reranking=RerankingMethod.LLM,
            generation_mode=GenerationMode.ITERATIVE,
        )
        assert request.strategy == RetrievalStrategy.ADAPTIVE
        assert request.reranking == RerankingMethod.LLM
        assert request.generation_mode == GenerationMode.ITERATIVE

    def test_request_with_filters(self):
        """Test request with filters"""
        filters = {"crop_type": "wheat", "region": "central"}
        request = RAGRequest(
            query="Irrigation advice",
            filters=filters,
        )
        assert request.filters["crop_type"] == "wheat"
        assert request.filters["region"] == "central"

    def test_request_defaults(self):
        """Test request default values"""
        request = RAGRequest(query="Test")
        assert request.query_ar is None
        assert request.collection == "default"
        assert request.top_k == 5
        assert request.rerank_top_k == 3
        assert request.strategy == RetrievalStrategy.HYBRID
        assert request.reranking == RerankingMethod.CROSS_ENCODER
        assert request.generation_mode == GenerationMode.STANDARD
        assert request.language == "en"
        assert request.include_sources is True
        assert request.max_tokens == 1024


class TestRAGResult:
    """Tests for RAGResult dataclass"""

    def test_create_result(self):
        """Test creating a RAG result"""
        request = RAGRequest(query="Test query")
        chunk = KnowledgeChunk(id="c1", text="Content")
        retrieval_results = [RetrievalResult(chunk=chunk, score=0.9)]
        generation = GenerationResult(answer="Generated answer", confidence=0.88)

        result = RAGResult(
            request=request,
            retrieval_results=retrieval_results,
            generation_result=generation,
            total_time_ms=750.0,
        )
        assert result.request.query == "Test query"
        assert len(result.retrieval_results) == 1
        assert result.generation_result.answer == "Generated answer"
        assert result.total_time_ms == 750.0
        assert result.success is True

    def test_result_with_error(self):
        """Test result with error"""
        request = RAGRequest(query="Test")
        result = RAGResult(
            request=request,
            retrieval_results=[],
            success=False,
            error="Failed to retrieve documents",
        )
        assert result.success is False
        assert result.error == "Failed to retrieve documents"

    def test_result_to_dict(self):
        """Test result serialization"""
        request = RAGRequest(query="Test query", rerank_top_k=2)
        chunk = KnowledgeChunk(id="c1", text="Content")
        retrieval_results = [
            RetrievalResult(chunk=chunk, score=0.9),
            RetrievalResult(chunk=KnowledgeChunk(id="c2", text="Content 2"), score=0.8),
            RetrievalResult(chunk=KnowledgeChunk(id="c3", text="Content 3"), score=0.7),
        ]
        generation = GenerationResult(
            answer="Answer",
            answer_ar="إجابة",
            confidence=0.85,
        )

        result = RAGResult(
            request=request,
            retrieval_results=retrieval_results,
            generation_result=generation,
            total_time_ms=500.0,
        )
        d = result.to_dict()
        assert d["query"] == "Test query"
        assert d["answer"] == "Answer"
        assert d["answer_ar"] == "إجابة"
        assert d["confidence"] == 0.85
        assert len(d["sources"]) == 2  # Limited by rerank_top_k
        assert d["total_time_ms"] == 500.0
        assert d["success"] is True


class TestPipelineStageConfig:
    """Tests for PipelineStageConfig dataclass"""

    def test_create_stage_config(self):
        """Test creating a pipeline stage config"""
        stage = PipelineStageConfig(
            name="retrieval_stage",
            type="retrieval",
            enabled=True,
            config={"top_k": 10, "strategy": "hybrid"},
        )
        assert stage.name == "retrieval_stage"
        assert stage.type == "retrieval"
        assert stage.enabled is True
        assert stage.config["top_k"] == 10

    def test_stage_with_conditions(self):
        """Test stage with conditions"""
        stage = PipelineStageConfig(
            name="conditional_stage",
            type="transform",
            conditions={"min_score": 0.5, "language": "ar"},
        )
        assert stage.conditions["min_score"] == 0.5
        assert stage.conditions["language"] == "ar"

    def test_stage_defaults(self):
        """Test stage default values"""
        stage = PipelineStageConfig(name="test", type="retrieval")
        assert stage.enabled is True
        assert stage.config == {}
        assert stage.conditions == {}


class TestRAGPipelineConfig:
    """Tests for RAGPipelineConfig dataclass"""

    def test_create_pipeline_config(self):
        """Test creating a pipeline config"""
        config = RAGPipelineConfig(
            name="agricultural_rag",
            version="2.0.0",
            description="RAG pipeline for agricultural queries",
        )
        assert config.name == "agricultural_rag"
        assert config.version == "2.0.0"

    def test_pipeline_config_strategies(self):
        """Test pipeline config with strategies"""
        config = RAGPipelineConfig(
            name="test",
            retrieval_strategy=RetrievalStrategy.ADAPTIVE,
            chunking_strategy=ChunkingStrategy.SEMANTIC,
            reranking_method=RerankingMethod.LLM,
            generation_mode=GenerationMode.CHAIN_OF_THOUGHT,
        )
        assert config.retrieval_strategy == RetrievalStrategy.ADAPTIVE
        assert config.chunking_strategy == ChunkingStrategy.SEMANTIC
        assert config.reranking_method == RerankingMethod.LLM
        assert config.generation_mode == GenerationMode.CHAIN_OF_THOUGHT

    def test_pipeline_config_weights(self):
        """Test pipeline config weights"""
        config = RAGPipelineConfig(
            name="test",
            dense_weight=0.8,
            sparse_weight=0.2,
        )
        assert config.dense_weight == 0.8
        assert config.sparse_weight == 0.2

    def test_pipeline_config_arabic(self):
        """Test pipeline config Arabic settings"""
        config = RAGPipelineConfig(
            name="test",
            arabic_enabled=True,
            arabic_embedding_model="CAMeL-Lab/bert-base-arabic-camelbert-mix",
        )
        assert config.arabic_enabled is True
        assert "camelbert" in config.arabic_embedding_model.lower()

    def test_pipeline_config_to_dict(self):
        """Test pipeline config serialization"""
        config = RAGPipelineConfig(
            name="test_pipeline",
            version="1.0.0",
            retrieval_strategy=RetrievalStrategy.HYBRID,
            chunking_strategy=ChunkingStrategy.RECURSIVE,
            top_k=15,
            chunk_size=600,
            llm_model="codellama:13b",
        )
        d = config.to_dict()
        assert d["name"] == "test_pipeline"
        assert d["retrieval_strategy"] == "hybrid"
        assert d["chunking_strategy"] == "recursive"
        assert d["top_k"] == 15
        assert d["chunk_size"] == 600
        assert d["llm_model"] == "codellama:13b"

    def test_pipeline_config_defaults(self):
        """Test pipeline config default values"""
        config = RAGPipelineConfig(name="test")
        assert config.version == "1.0.0"
        assert config.retrieval_strategy == RetrievalStrategy.HYBRID
        assert config.dense_weight == 0.7
        assert config.sparse_weight == 0.3
        assert config.top_k == 10
        assert config.chunk_size == 500
        assert config.chunk_overlap == 50
        assert config.rerank_top_k == 5
        assert config.max_tokens == 1024
        assert config.temperature == 0.1
        assert config.cache_enabled is True
        assert config.offline_first is True


class TestWorkflowStep:
    """Tests for WorkflowStep dataclass"""

    def test_create_step(self):
        """Test creating a workflow step"""
        step = WorkflowStep(
            id="step_001",
            type="retrieve",
            name="Retrieve Documents",
            config={"top_k": 10},
            next_step="step_002",
        )
        assert step.id == "step_001"
        assert step.type == "retrieve"
        assert step.name == "Retrieve Documents"
        assert step.config["top_k"] == 10
        assert step.next_step == "step_002"

    def test_step_with_branching(self):
        """Test step with success/failure branching"""
        step = WorkflowStep(
            id="step_002",
            type="condition",
            name="Check Score",
            on_success="step_003",
            on_failure="step_004",
            condition="score > 0.8",
        )
        assert step.on_success == "step_003"
        assert step.on_failure == "step_004"
        assert step.condition == "score > 0.8"

    def test_step_with_loop(self):
        """Test step with loop configuration"""
        step = WorkflowStep(
            id="step_003",
            type="loop",
            name="Iterative Refinement",
            loop_config={"max_iterations": 3, "exit_condition": "confidence > 0.9"},
        )
        assert step.loop_config["max_iterations"] == 3
        assert step.loop_config["exit_condition"] == "confidence > 0.9"

    def test_step_defaults(self):
        """Test step default values"""
        step = WorkflowStep(id="step", type="retrieve", name="Test")
        assert step.config == {}
        assert step.next_step is None
        assert step.on_success is None
        assert step.on_failure is None
        assert step.condition is None
        assert step.loop_config is None


class TestWorkflowConfig:
    """Tests for WorkflowConfig dataclass"""

    def test_create_workflow(self):
        """Test creating a workflow config"""
        steps = [
            WorkflowStep(id="s1", type="retrieve", name="Retrieve"),
            WorkflowStep(id="s2", type="generate", name="Generate"),
        ]
        workflow = WorkflowConfig(
            id="wf_001",
            name="Simple RAG Workflow",
            name_ar="سير عمل RAG بسيط",
            description="A simple RAG workflow",
            steps=steps,
            entry_point="s1",
        )
        assert workflow.id == "wf_001"
        assert workflow.name == "Simple RAG Workflow"
        assert workflow.name_ar == "سير عمل RAG بسيط"
        assert len(workflow.steps) == 2
        assert workflow.entry_point == "s1"

    def test_workflow_with_variables(self):
        """Test workflow with variables"""
        workflow = WorkflowConfig(
            id="wf_002",
            name="Test Workflow",
            variables={"max_retries": 3, "timeout": 30},
        )
        assert workflow.variables["max_retries"] == 3
        assert workflow.variables["timeout"] == 30

    def test_workflow_from_yaml(self):
        """Test creating workflow from YAML dictionary"""
        yaml_dict = {
            "id": "wf_yaml",
            "name": "YAML Workflow",
            "name_ar": "سير عمل YAML",
            "description": "Created from YAML",
            "version": "2.0.0",
            "steps": [
                {
                    "id": "retrieve",
                    "type": "retrieve",
                    "name": "Retrieve Step",
                    "config": {"top_k": 5},
                    "next_step": "rerank",
                },
                {
                    "id": "rerank",
                    "type": "rerank",
                    "name": "Rerank Step",
                    "config": {"method": "cross_encoder"},
                    "next_step": "generate",
                },
                {
                    "id": "generate",
                    "type": "generate",
                    "name": "Generate Step",
                    "config": {"max_tokens": 512},
                },
            ],
            "entry_point": "retrieve",
            "variables": {"threshold": 0.5},
        }
        workflow = WorkflowConfig.from_yaml(yaml_dict)
        assert workflow.id == "wf_yaml"
        assert workflow.name == "YAML Workflow"
        assert workflow.name_ar == "سير عمل YAML"
        assert workflow.version == "2.0.0"
        assert len(workflow.steps) == 3
        assert workflow.steps[0].id == "retrieve"
        assert workflow.steps[0].config["top_k"] == 5
        assert workflow.steps[1].next_step == "generate"
        assert workflow.entry_point == "retrieve"
        assert workflow.variables["threshold"] == 0.5

    def test_workflow_from_yaml_minimal(self):
        """Test creating workflow from minimal YAML"""
        yaml_dict = {
            "name": "Minimal Workflow",
            "steps": [
                {"id": "only_step", "type": "retrieve", "name": "Only Step"},
            ],
        }
        workflow = WorkflowConfig.from_yaml(yaml_dict)
        assert workflow.name == "Minimal Workflow"
        assert workflow.id.startswith("workflow_")
        assert workflow.version == "1.0.0"
        assert workflow.entry_point == "only_step"

    def test_workflow_from_yaml_empty_steps(self):
        """Test creating workflow from YAML with no steps"""
        yaml_dict = {
            "name": "Empty Workflow",
        }
        workflow = WorkflowConfig.from_yaml(yaml_dict)
        assert len(workflow.steps) == 0
        assert workflow.entry_point == ""

    def test_workflow_defaults(self):
        """Test workflow default values"""
        workflow = WorkflowConfig(id="wf", name="Test")
        assert workflow.name_ar is None
        assert workflow.description == ""
        assert workflow.description_ar == ""
        assert workflow.version == "1.0.0"
        assert workflow.steps == []
        assert workflow.entry_point == ""
        assert workflow.variables == {}
