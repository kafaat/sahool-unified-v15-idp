# ═══════════════════════════════════════════════════════════════════════════════
# Agriculture AI Knowledge Base Module
# وحدة قاعدة المعرفة الزراعية للذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════════
#
# Provides structured knowledge management for agricultural AI agents:
# - Domain-specific data models (crops, soil, irrigation, fertilizer, weather)
# - Knowledge ingestion pipeline (Markdown, PDF, HTML, URLs)
# - Source credibility registry (FAO, ICARDA, MEWA)
# - Knowledge verification agent (4-layer validation gate)
# - Region relevance filter (AgriRegion pattern)
# - Collection population and management
#
# Based on best practices from:
# - AgriRegion (arXiv:2512.10114) - region-aware RAG
# - FAO AGROVOC - standardized agricultural terminology
# - FRESH framework - structured data organization
# - FAIR principles - findable, accessible, interoperable, reusable
# - Corrective RAG (CRAG) - self-correcting retrieval
#
# ═══════════════════════════════════════════════════════════════════════════════

from .agrovoc import AgrovocConcept, AgrovocDomain, AgrovocLookup
from .cache import KnowledgeCache
from .collections import (
    CROP_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    DIGITAL_TWIN_KNOWLEDGE,
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    IRRIGATION_PRACTICES,
    PEST_KNOWLEDGE,
    PRECISION_FARMING_KNOWLEDGE,
    REMOTE_SENSING_KNOWLEDGE,
    RESEARCH_REFERENCES,
    SMART_AGRICULTURE_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)
from .corrective_retrieval import (
    ConfidenceLevel,
    CorrectiveRetrievalEngine,
    CRAGResult,
    RefinedChunk,
    RetrievalAction,
    RetrievalEvaluation,
)
from .events import KnowledgeEventPublisher
from .freshness_monitor import KnowledgeFreshnessMonitor
from .graph_builder import (
    AgriculturalKnowledgeGraph,
    KGEntity,
    KGRelation,
    build_agricultural_knowledge_graph,
)
from .metrics import KnowledgeMetrics
from .models import (
    BestPracticesDocument,
    CropKnowledgeDocument,
    DigitalTwinDocument,
    FertilizerKnowledgeDocument,
    FRESHMetadata,
    GeospatialMetadata,
    IrrigationKnowledgeDocument,
    KnowledgeDomain,
    KnowledgeSourceMeta,
    PestVisionDocument,
    PrecisionFarmingDocument,
    RemoteSensingGuideDocument,
    SeasonalRelevance,
    SmartAgricultureDocument,
    SoilTypeDocument,
    WeatherPatternDocument,
)
from .persistence import DocumentPage, DocumentQuery, InMemoryKnowledgeRepository, KnowledgeRepository
from .quality_gate import KnowledgeQualityGate, QualityCheckResult
from .serialization import KnowledgeSerializer
from .vector_store_integration import KnowledgeVectorStore, VectorSearchResult
from .versioning import DocumentVersionManager

__version__ = "3.0.0"
__all__ = [
    # Collections
    "CROP_KNOWLEDGE",
    "PEST_KNOWLEDGE",
    "CROP_WATER_REQUIREMENTS",
    "IRRIGATION_PRACTICES",
    "SOIL_KNOWLEDGE",
    "FERTILIZER_KNOWLEDGE",
    "WEATHER_KNOWLEDGE",
    "REMOTE_SENSING_KNOWLEDGE",
    "SMART_AGRICULTURE_KNOWLEDGE",
    "RESEARCH_REFERENCES",
    "PRECISION_FARMING_KNOWLEDGE",
    "DIGITAL_TWIN_KNOWLEDGE",
    "GENERAL_AGRICULTURE",
    # Models
    "KnowledgeDomain",
    "SeasonalRelevance",
    "FRESHMetadata",
    "GeospatialMetadata",
    "KnowledgeSourceMeta",
    "CropKnowledgeDocument",
    "SoilTypeDocument",
    "IrrigationKnowledgeDocument",
    "FertilizerKnowledgeDocument",
    "WeatherPatternDocument",
    "RemoteSensingGuideDocument",
    "SmartAgricultureDocument",
    "PestVisionDocument",
    "PrecisionFarmingDocument",
    "DigitalTwinDocument",
    "BestPracticesDocument",
    # AGROVOC
    "AgrovocConcept",
    "AgrovocDomain",
    "AgrovocLookup",
    # Graph Builder
    "AgriculturalKnowledgeGraph",
    "KGEntity",
    "KGRelation",
    "build_agricultural_knowledge_graph",
    # Corrective Retrieval (CRAG)
    "CorrectiveRetrievalEngine",
    "CRAGResult",
    "RefinedChunk",
    "RetrievalAction",
    "RetrievalEvaluation",
    "ConfidenceLevel",
    # Vector Store Integration (GAP-01)
    "KnowledgeVectorStore",
    "VectorSearchResult",
    # Persistence (GAP-03)
    "KnowledgeRepository",
    "InMemoryKnowledgeRepository",
    "DocumentQuery",
    "DocumentPage",
    # Metrics (GAP-13)
    "KnowledgeMetrics",
    # Versioning (GAP-14)
    "DocumentVersionManager",
    # Cache (GAP-19)
    "KnowledgeCache",
    # Quality Gate (GAP-20)
    "KnowledgeQualityGate",
    "QualityCheckResult",
    # Serialization (GAP-16)
    "KnowledgeSerializer",
    # Freshness Monitor (GAP-11)
    "KnowledgeFreshnessMonitor",
    # NATS Event Publisher (GAP-12)
    "KnowledgeEventPublisher",
]
