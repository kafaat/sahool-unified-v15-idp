# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Models - Data Classes and Type Definitions
# نماذج البيانات لـ UltraRAG
# ═══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import uuid


class RetrievalStrategy(Enum):
    """Retrieval strategy types | أنواع استراتيجيات الاسترجاع"""
    DENSE = "dense"              # Vector similarity only
    SPARSE = "sparse"            # BM25/keyword based
    HYBRID = "hybrid"            # Dense + Sparse combination
    ADAPTIVE = "adaptive"        # Query-dependent strategy selection


class ChunkingStrategy(Enum):
    """Document chunking strategies | استراتيجيات تقسيم المستندات"""
    FIXED_SIZE = "fixed_size"           # Fixed character/token count
    SENTENCE = "sentence"               # Sentence-based chunking
    PARAGRAPH = "paragraph"             # Paragraph-based chunking
    SEMANTIC = "semantic"               # Semantic similarity based
    HIERARCHICAL = "hierarchical"       # Multi-level chunking
    RECURSIVE = "recursive"             # Recursive character splitting


class RerankingMethod(Enum):
    """Reranking methods | طرق إعادة الترتيب"""
    NONE = "none"                       # No reranking
    CROSS_ENCODER = "cross_encoder"     # Cross-encoder model
    LLM = "llm"                         # LLM-based reranking
    COHERE = "cohere"                   # Cohere rerank API
    RECIPROCAL_RANK = "reciprocal_rank" # Reciprocal Rank Fusion


class GenerationMode(Enum):
    """Generation modes | أوضاع التوليد"""
    STANDARD = "standard"               # Standard RAG generation
    CHAIN_OF_THOUGHT = "cot"           # Chain-of-thought reasoning
    SELF_REFLECTIVE = "self_reflective" # Self-reflective RAG
    ITERATIVE = "iterative"             # Iterative refinement


@dataclass
class KnowledgeChunk:
    """A chunk of knowledge from a document | قطعة من المعرفة من مستند"""
    id: str
    text: str
    text_ar: Optional[str] = None  # Arabic text
    document_id: str = ""
    collection: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)
    vector: Optional[List[float]] = None
    start_char: int = 0
    end_char: int = 0
    chunk_index: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "text_ar": self.text_ar,
            "document_id": self.document_id,
            "collection": self.collection,
            "metadata": self.metadata,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "chunk_index": self.chunk_index,
        }


@dataclass
class KnowledgeDocument:
    """A document in the knowledge base | مستند في قاعدة المعرفة"""
    id: str
    title: str
    title_ar: Optional[str] = None
    content: str = ""
    content_ar: Optional[str] = None
    source: str = ""
    collection: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunks: List[KnowledgeChunk] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def generate_id() -> str:
        return f"doc_{uuid.uuid4().hex[:12]}"


@dataclass
class RetrievalResult:
    """Result from retrieval | نتيجة الاسترجاع"""
    chunk: KnowledgeChunk
    score: float
    retrieval_method: str = "dense"
    rank: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk.id,
            "text": self.chunk.text,
            "text_ar": self.chunk.text_ar,
            "score": self.score,
            "method": self.retrieval_method,
            "rank": self.rank,
            "metadata": self.chunk.metadata,
        }


@dataclass
class RerankResult:
    """Result from reranking | نتيجة إعادة الترتيب"""
    results: List[RetrievalResult]
    method: RerankingMethod
    processing_time_ms: float = 0.0


@dataclass
class GenerationResult:
    """Result from generation | نتيجة التوليد"""
    answer: str
    answer_ar: Optional[str] = None
    confidence: float = 0.0
    sources: List[RetrievalResult] = field(default_factory=list)
    reasoning: Optional[str] = None
    mode: GenerationMode = GenerationMode.STANDARD
    tokens_used: int = 0
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "answer_ar": self.answer_ar,
            "confidence": self.confidence,
            "sources": [s.to_dict() for s in self.sources],
            "reasoning": self.reasoning,
            "mode": self.mode.value,
            "tokens_used": self.tokens_used,
            "processing_time_ms": self.processing_time_ms,
        }


@dataclass
class RAGRequest:
    """RAG request | طلب RAG"""
    query: str
    query_ar: Optional[str] = None
    collection: str = "default"
    top_k: int = 5
    rerank_top_k: int = 3
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    reranking: RerankingMethod = RerankingMethod.CROSS_ENCODER
    generation_mode: GenerationMode = GenerationMode.STANDARD
    filters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    language: str = "en"  # "en" or "ar"
    include_sources: bool = True
    max_tokens: int = 1024


@dataclass
class RAGResult:
    """Complete RAG result | نتيجة RAG الكاملة"""
    request: RAGRequest
    retrieval_results: List[RetrievalResult]
    rerank_result: Optional[RerankResult] = None
    generation_result: Optional[GenerationResult] = None
    total_time_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.request.query,
            "answer": self.generation_result.answer if self.generation_result else None,
            "answer_ar": self.generation_result.answer_ar if self.generation_result else None,
            "confidence": self.generation_result.confidence if self.generation_result else 0.0,
            "sources": [r.to_dict() for r in self.retrieval_results[:self.request.rerank_top_k]],
            "total_time_ms": self.total_time_ms,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class PipelineStageConfig:
    """Configuration for a pipeline stage | تكوين مرحلة في خط الأنابيب"""
    name: str
    type: str  # "retrieval", "rerank", "generation", "transform"
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)  # For conditional execution


@dataclass
class RAGPipelineConfig:
    """Configuration for RAG pipeline | تكوين خط أنابيب RAG"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    description_ar: str = ""

    # Retrieval settings
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    top_k: int = 10

    # Chunking settings
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Reranking settings
    reranking_method: RerankingMethod = RerankingMethod.CROSS_ENCODER
    rerank_top_k: int = 5
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Generation settings
    generation_mode: GenerationMode = GenerationMode.STANDARD
    llm_model: str = "codellama:7b"
    llm_provider: str = "ollama"
    max_tokens: int = 1024
    temperature: float = 0.1

    # Embedding settings
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_provider: str = "sentence_transformers"
    embedding_dimension: int = 384

    # Arabic support
    arabic_enabled: bool = True
    arabic_embedding_model: str = "CAMeL-Lab/bert-base-arabic-camelbert-mix"

    # Pipeline stages
    stages: List[PipelineStageConfig] = field(default_factory=list)

    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600

    # Offline mode
    offline_first: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "retrieval_strategy": self.retrieval_strategy.value,
            "chunking_strategy": self.chunking_strategy.value,
            "reranking_method": self.reranking_method.value,
            "generation_mode": self.generation_mode.value,
            "top_k": self.top_k,
            "chunk_size": self.chunk_size,
            "llm_model": self.llm_model,
            "embedding_model": self.embedding_model,
            "arabic_enabled": self.arabic_enabled,
            "offline_first": self.offline_first,
        }


@dataclass
class WorkflowStep:
    """A step in a workflow | خطوة في سير العمل"""
    id: str
    type: str  # "retrieve", "rerank", "generate", "condition", "loop", "transform"
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    next_step: Optional[str] = None
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    condition: Optional[str] = None  # For conditional steps
    loop_config: Optional[Dict[str, Any]] = None  # For loop steps


@dataclass
class WorkflowConfig:
    """Configuration for a workflow | تكوين سير العمل"""
    id: str
    name: str
    name_ar: Optional[str] = None
    description: str = ""
    description_ar: str = ""
    version: str = "1.0.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    entry_point: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_yaml(yaml_dict: Dict[str, Any]) -> "WorkflowConfig":
        """Create WorkflowConfig from YAML dictionary"""
        steps = []
        for step_dict in yaml_dict.get("steps", []):
            steps.append(WorkflowStep(
                id=step_dict.get("id", ""),
                type=step_dict.get("type", ""),
                name=step_dict.get("name", ""),
                config=step_dict.get("config", {}),
                next_step=step_dict.get("next_step"),
                on_success=step_dict.get("on_success"),
                on_failure=step_dict.get("on_failure"),
                condition=step_dict.get("condition"),
                loop_config=step_dict.get("loop_config"),
            ))

        return WorkflowConfig(
            id=yaml_dict.get("id", f"workflow_{uuid.uuid4().hex[:8]}"),
            name=yaml_dict.get("name", "Unnamed Workflow"),
            name_ar=yaml_dict.get("name_ar"),
            description=yaml_dict.get("description", ""),
            description_ar=yaml_dict.get("description_ar", ""),
            version=yaml_dict.get("version", "1.0.0"),
            steps=steps,
            entry_point=yaml_dict.get("entry_point", steps[0].id if steps else ""),
            variables=yaml_dict.get("variables", {}),
        )
