# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Collection Constants
# ثوابت مجموعات المعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# These constants match the collection names referenced in UltraRAG workflows:
#   - crop_advisory.yaml
#   - irrigation_advisory.yaml
#   - knowledge_search.yaml
#   - (new workflows: fertilizer, soil, weather, remote_sensing, pest, comprehensive)
#
# ═══════════════════════════════════════════════════════════════════════════════

# Core collections referenced by existing workflows
CROP_KNOWLEDGE = "crop_knowledge"
"""Crop data: varieties, growth stages, Kc values, requirements.
Referenced in: crop_advisory.yaml step retrieve_crop_knowledge"""

PEST_KNOWLEDGE = "pest_knowledge"
"""Pest & disease identification, thresholds, IPM recommendations.
Referenced in: crop_advisory.yaml step retrieve_pest_knowledge"""

CROP_WATER_REQUIREMENTS = "crop_water_requirements"
"""Water requirements per crop and growth stage, ET values.
Referenced in: irrigation_advisory.yaml step retrieve_crop_water_needs"""

IRRIGATION_PRACTICES = "irrigation_practices"
"""Irrigation methods, scheduling, efficiency, best practices.
Referenced in: irrigation_advisory.yaml step retrieve_irrigation_best_practices"""

GENERAL_AGRICULTURE = "general_agriculture"
"""General agricultural knowledge, fallback collection.
Referenced in: crop_advisory.yaml confidence_check fallback"""

# New collections for expanded knowledge domains
SOIL_KNOWLEDGE = "soil_knowledge"
"""Soil types, properties (pH, EC, OM), classification, amendments.
Referenced in: soil_analysis_advisory.yaml"""

FERTILIZER_KNOWLEDGE = "fertilizer_knowledge"
"""Fertilizer types, nutrient content, application rates, deficiency guides.
Referenced in: fertilizer_advisory.yaml"""

WEATHER_KNOWLEDGE = "weather_knowledge"
"""Climate zones, frost protection, heat stress, drought management.
Referenced in: weather_advisory.yaml"""

REMOTE_SENSING_KNOWLEDGE = "remote_sensing_knowledge"
"""NDVI interpretation, LAI guide, water stress index, Sentinel-2 usage.
Referenced in: remote_sensing_analysis.yaml"""

SMART_AGRICULTURE_KNOWLEDGE = "smart_agriculture_knowledge"
"""Smart agriculture: IoT, drones, digital twins, AI models, precision farming,
blockchain traceability, edge computing, market intelligence.
References: AGRARIAN (MDPI 2025), China Smart Agriculture Plan 2024-2028,
FAO Digital Agriculture Roadmap 2025, CropIn Cloud architecture."""

RESEARCH_REFERENCES = "research_references"
"""Academic papers and research references backing knowledge base content.
Sources: AgriRegion, Crop GraphRAG, CRAG, KALLM, AgroAskAI, C3PO, RAGOps."""

PRECISION_FARMING_KNOWLEDGE = "precision_farming_knowledge"
"""Precision farming: VRA, GPS/GNSS guidance, yield mapping, site-specific management.
Sources: ISPA, John Deere, Trimble Agriculture."""

DIGITAL_TWIN_KNOWLEDGE = "digital_twin_knowledge"
"""Digital twins: farm simulation, cyber-physical systems, real-time replicas.
Sources: FAO Digital Agriculture, IEEE, Wageningen University."""

# Collection-to-directory mapping for population
# NOTE: Each directory should map to a single primary collection to avoid duplication.
# If two collections need the same directory, use metadata-based routing in the pipeline.
COLLECTION_DIRECTORY_MAP: dict[str, list[str]] = {
    CROP_KNOWLEDGE: ["docs/knowledge-base/crops/"],
    PEST_KNOWLEDGE: ["docs/knowledge-base/diseases/"],
    CROP_WATER_REQUIREMENTS: [],  # Populated via metadata routing from irrigation/ docs tagged with "water_requirements"
    IRRIGATION_PRACTICES: ["docs/knowledge-base/irrigation/"],
    SOIL_KNOWLEDGE: ["docs/knowledge-base/soils/"],
    FERTILIZER_KNOWLEDGE: ["docs/knowledge-base/fertilization/"],
    WEATHER_KNOWLEDGE: ["docs/knowledge-base/weather/"],
    REMOTE_SENSING_KNOWLEDGE: ["docs/knowledge-base/remote-sensing/"],
    SMART_AGRICULTURE_KNOWLEDGE: ["docs/knowledge-base/ai-smart-agriculture/"],
    RESEARCH_REFERENCES: [],  # Populated via metadata routing from docs tagged with "research"
    PRECISION_FARMING_KNOWLEDGE: ["docs/knowledge-base/precision-farming/"],
    DIGITAL_TWIN_KNOWLEDGE: ["docs/knowledge-base/digital-twin/"],
    GENERAL_AGRICULTURE: ["docs/knowledge-base/best-practices/", "docs/knowledge-base/monitoring/"],
}

ALL_COLLECTIONS = [
    CROP_KNOWLEDGE,
    PEST_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    IRRIGATION_PRACTICES,
    SOIL_KNOWLEDGE,
    FERTILIZER_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
    REMOTE_SENSING_KNOWLEDGE,
    SMART_AGRICULTURE_KNOWLEDGE,
    RESEARCH_REFERENCES,
    PRECISION_FARMING_KNOWLEDGE,
    DIGITAL_TWIN_KNOWLEDGE,
    GENERAL_AGRICULTURE,
]
