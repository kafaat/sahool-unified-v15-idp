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

from .collections import (
    CROP_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    IRRIGATION_PRACTICES,
    PEST_KNOWLEDGE,
    REMOTE_SENSING_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)
from .models import (
    CropKnowledgeDocument,
    FertilizerKnowledgeDocument,
    FRESHMetadata,
    GeospatialMetadata,
    IrrigationKnowledgeDocument,
    KnowledgeDomain,
    KnowledgeSourceMeta,
    RemoteSensingGuideDocument,
    SoilTypeDocument,
    WeatherPatternDocument,
)

__version__ = "1.0.0"
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
    "GENERAL_AGRICULTURE",
    # Models
    "KnowledgeDomain",
    "FRESHMetadata",
    "GeospatialMetadata",
    "KnowledgeSourceMeta",
    "CropKnowledgeDocument",
    "SoilTypeDocument",
    "IrrigationKnowledgeDocument",
    "FertilizerKnowledgeDocument",
    "WeatherPatternDocument",
    "RemoteSensingGuideDocument",
]
