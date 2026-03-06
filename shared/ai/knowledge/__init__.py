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
from .collections import (
    CROP_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    IRRIGATION_PRACTICES,
    PEST_KNOWLEDGE,
    REMOTE_SENSING_KNOWLEDGE,
    RESEARCH_REFERENCES,
    SMART_AGRICULTURE_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)
from .graph_builder import (
    AgriculturalKnowledgeGraph,
    KGEntity,
    KGRelation,
    build_agricultural_knowledge_graph,
)
from .corrective_retrieval import (
    ConfidenceLevel,
    CorrectiveRetrievalEngine,
    CRAGResult,
    RefinedChunk,
    RetrievalAction,
    RetrievalEvaluation,
)
from .models import (
    CropKnowledgeDocument,
    FertilizerKnowledgeDocument,
    FRESHMetadata,
    GeospatialMetadata,
    IrrigationKnowledgeDocument,
    KnowledgeDomain,
    KnowledgeSourceMeta,
    PestVisionDocument,
    RemoteSensingGuideDocument,
    SeasonalRelevance,
    SmartAgricultureDocument,
    SoilTypeDocument,
    WeatherPatternDocument,
)

__version__ = "2.0.0"
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
]
