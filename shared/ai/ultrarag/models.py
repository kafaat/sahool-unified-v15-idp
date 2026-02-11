# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Models - Data Classes and Type Definitions
# نماذج البيانات لـ UltraRAG
# ═══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid


class RetrievalStrategy(Enum):
    """Retrieval strategy types | أنواع استراتيجيات الاسترجاع"""

    DENSE = "dense"  # Vector similarity only
    SPARSE = "sparse"  # BM25/keyword based
    HYBRID = "hybrid"  # Dense + Sparse combination
    ADAPTIVE = "adaptive"  # Query-dependent strategy selection
    TRI_RAG = "tri_rag"  # AgriGPT Tri-RAG: Dense + Sparse + Knowledge Graph


class ChunkingStrategy(Enum):
    """Document chunking strategies | استراتيجيات تقسيم المستندات"""

    FIXED_SIZE = "fixed_size"  # Fixed character/token count
    SENTENCE = "sentence"  # Sentence-based chunking
    PARAGRAPH = "paragraph"  # Paragraph-based chunking
    SEMANTIC = "semantic"  # Semantic similarity based
    HIERARCHICAL = "hierarchical"  # Multi-level chunking
    RECURSIVE = "recursive"  # Recursive character splitting


class RerankingMethod(Enum):
    """Reranking methods | طرق إعادة الترتيب"""

    NONE = "none"  # No reranking
    CROSS_ENCODER = "cross_encoder"  # Cross-encoder model
    LLM = "llm"  # LLM-based reranking
    COHERE = "cohere"  # Cohere rerank API
    RECIPROCAL_RANK = "reciprocal_rank"  # Reciprocal Rank Fusion


class GenerationMode(Enum):
    """Generation modes | أوضاع التوليد"""

    STANDARD = "standard"  # Standard RAG generation
    CHAIN_OF_THOUGHT = "cot"  # Chain-of-thought reasoning
    SELF_REFLECTIVE = "self_reflective"  # Self-reflective RAG
    ITERATIVE = "iterative"  # Iterative refinement


@dataclass
class KnowledgeChunk:
    """A chunk of knowledge from a document | قطعة من المعرفة من مستند"""

    id: str
    text: str
    text_ar: str | None = None  # Arabic text
    document_id: str = ""
    collection: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)
    vector: list[float] | None = None
    start_char: int = 0
    end_char: int = 0
    chunk_index: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
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
    title_ar: str | None = None
    content: str = ""
    content_ar: str | None = None
    source: str = ""
    collection: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)
    chunks: list[KnowledgeChunk] = field(default_factory=list)
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

    def to_dict(self) -> dict[str, Any]:
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

    results: list[RetrievalResult]
    method: RerankingMethod
    processing_time_ms: float = 0.0


@dataclass
class GenerationResult:
    """Result from generation | نتيجة التوليد"""

    answer: str
    answer_ar: str | None = None
    confidence: float = 0.0
    sources: list[RetrievalResult] = field(default_factory=list)
    reasoning: str | None = None
    mode: GenerationMode = GenerationMode.STANDARD
    tokens_used: int = 0
    processing_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
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
    query_ar: str | None = None
    collection: str = "default"
    top_k: int = 5
    rerank_top_k: int = 3
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    reranking: RerankingMethod = RerankingMethod.CROSS_ENCODER
    generation_mode: GenerationMode = GenerationMode.STANDARD
    filters: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    tenant_id: str | None = None
    language: str = "en"  # "en" or "ar"
    include_sources: bool = True
    max_tokens: int = 1024


@dataclass
class RAGResult:
    """Complete RAG result | نتيجة RAG الكاملة"""

    request: RAGRequest
    retrieval_results: list[RetrievalResult]
    rerank_result: RerankResult | None = None
    generation_result: GenerationResult | None = None
    total_time_ms: float = 0.0
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.request.query,
            "answer": self.generation_result.answer if self.generation_result else None,
            "answer_ar": self.generation_result.answer_ar if self.generation_result else None,
            "confidence": self.generation_result.confidence if self.generation_result else 0.0,
            "sources": [r.to_dict() for r in self.retrieval_results[: self.request.rerank_top_k]],
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
    config: dict[str, Any] = field(default_factory=dict)
    conditions: dict[str, Any] = field(default_factory=dict)  # For conditional execution


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
    stages: list[PipelineStageConfig] = field(default_factory=list)

    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600

    # Offline mode
    offline_first: bool = True

    def to_dict(self) -> dict[str, Any]:
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
    config: dict[str, Any] = field(default_factory=dict)
    next_step: str | None = None
    on_success: str | None = None
    on_failure: str | None = None
    condition: str | None = None  # For conditional steps
    loop_config: dict[str, Any] | None = None  # For loop steps


@dataclass
class WorkflowConfig:
    """Configuration for a workflow | تكوين سير العمل"""

    id: str
    name: str
    name_ar: str | None = None
    description: str = ""
    description_ar: str = ""
    version: str = "1.0.0"
    steps: list[WorkflowStep] = field(default_factory=list)
    entry_point: str = ""
    variables: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_yaml(yaml_dict: dict[str, Any]) -> "WorkflowConfig":
        """Create WorkflowConfig from YAML dictionary"""
        steps = []
        for step_dict in yaml_dict.get("steps", []):
            steps.append(
                WorkflowStep(
                    id=step_dict.get("id", ""),
                    type=step_dict.get("type", ""),
                    name=step_dict.get("name", ""),
                    config=step_dict.get("config", {}),
                    next_step=step_dict.get("next_step"),
                    on_success=step_dict.get("on_success"),
                    on_failure=step_dict.get("on_failure"),
                    condition=step_dict.get("condition"),
                    loop_config=step_dict.get("loop_config"),
                )
            )

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


# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Graph Models for Tri-RAG (AgriGPT Integration)
# نماذج خرائط المعرفة لـ Tri-RAG (تكامل AgriGPT)
# ═══════════════════════════════════════════════════════════════════════════════


class EntityType(Enum):
    """Types of entities in the agricultural knowledge graph"""

    CROP = "crop"  # محصول
    PEST = "pest"  # آفة
    DISEASE = "disease"  # مرض
    FERTILIZER = "fertilizer"  # سماد
    PESTICIDE = "pesticide"  # مبيد
    IRRIGATION = "irrigation"  # ري
    SOIL = "soil"  # تربة
    WEATHER = "weather"  # طقس
    EQUIPMENT = "equipment"  # معدات
    TECHNIQUE = "technique"  # تقنية
    REGION = "region"  # منطقة
    SEASON = "season"  # موسم
    # Satellite & GEE Entity Types - أنواع كيانات الأقمار الصناعية
    SENSOR = "sensor"  # مستشعر (satellite sensor)
    INDICATOR = "indicator"  # مؤشر (vegetation index)
    METHOD = "method"  # طريقة (analysis method)
    EVENT = "event"  # حدث (change event)
    LOCATION = "location"  # موقع (land cover type)


class RelationType(Enum):
    """Types of relationships in the knowledge graph"""

    AFFECTS = "affects"  # يؤثر على
    TREATS = "treats"  # يعالج
    PREVENTS = "prevents"  # يمنع
    REQUIRES = "requires"  # يتطلب
    PRODUCES = "produces"  # ينتج
    COMPATIBLE_WITH = "compatible_with"  # متوافق مع
    INCOMPATIBLE_WITH = "incompatible_with"  # غير متوافق مع
    GROWS_IN = "grows_in"  # ينمو في
    OCCURS_IN = "occurs_in"  # يحدث في
    PART_OF = "part_of"  # جزء من
    CAUSES = "causes"  # يسبب
    SYMPTOM_OF = "symptom_of"  # عرض لـ
    # Satellite & GEE Relations - علاقات الأقمار الصناعية
    PROVIDES = "provides"  # يوفر (satellite provides index)
    INDICATES = "indicates"  # يشير إلى (index indicates land cover)
    DETECTS = "detects"  # يكشف (index detects change)
    ANALYZES = "analyzes"  # يحلل (method analyzes data)
    CLASSIFIES = "classifies"  # يصنف (method classifies land cover)
    EXHIBITS = "exhibits"  # يظهر (land cover exhibits change)


@dataclass
class KnowledgeEntity:
    """An entity in the knowledge graph | كيان في خريطة المعرفة"""

    id: str
    name: str
    name_ar: str | None = None
    entity_type: EntityType = EntityType.CROP
    description: str = ""
    description_ar: str = ""
    aliases: list[str] = field(default_factory=list)
    aliases_ar: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def generate_id() -> str:
        return f"entity_{uuid.uuid4().hex[:12]}"


@dataclass
class KnowledgeRelation:
    """A relationship between entities | علاقة بين الكيانات"""

    id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0  # Relationship strength
    properties: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)  # Source document IDs
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def generate_id() -> str:
        return f"rel_{uuid.uuid4().hex[:12]}"


@dataclass
class KnowledgeGraphResult:
    """Result from knowledge graph query | نتيجة استعلام خريطة المعرفة"""

    entities: list[KnowledgeEntity]
    relations: list[KnowledgeRelation]
    paths: list[list[str]] = field(default_factory=list)  # Multi-hop paths
    score: float = 0.0
    reasoning: str = ""
    reasoning_ar: str = ""


@dataclass
class TriRAGConfig:
    """Configuration for Tri-RAG retrieval (AgriGPT style)
    تكوين الاسترجاع ثلاثي القنوات (نمط AgriGPT)
    """

    # Channel weights (should sum to 1.0)
    dense_weight: float = 0.4  # Semantic retrieval weight
    sparse_weight: float = 0.3  # Keyword retrieval weight
    kg_weight: float = 0.3  # Knowledge graph weight

    # Dense retrieval settings
    dense_top_k: int = 10
    dense_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # Sparse retrieval settings
    sparse_top_k: int = 10
    bm25_k1: float = 1.5
    bm25_b: float = 0.75

    # Knowledge graph settings
    kg_max_hops: int = 2  # Maximum hops for multi-hop reasoning
    kg_top_entities: int = 5  # Top entities to start from
    kg_expansion_limit: int = 20  # Max expanded nodes

    # Fusion settings
    rrf_k: int = 60  # RRF constant
    final_top_k: int = 10  # Final results after fusion

    # Context settings
    include_kg_reasoning: bool = True  # Include reasoning in context
    max_context_tokens: int = 4096

    def validate(self) -> bool:
        """Validate that weights sum to 1.0"""
        total = self.dense_weight + self.sparse_weight + self.kg_weight
        return abs(total - 1.0) < 0.01
