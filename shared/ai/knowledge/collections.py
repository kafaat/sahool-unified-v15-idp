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

# Collection-to-directory mapping for population
COLLECTION_DIRECTORY_MAP: dict[str, list[str]] = {
    CROP_KNOWLEDGE: ["docs/knowledge-base/crops/"],
    PEST_KNOWLEDGE: ["docs/knowledge-base/diseases/"],
    CROP_WATER_REQUIREMENTS: ["docs/knowledge-base/irrigation/"],
    IRRIGATION_PRACTICES: ["docs/knowledge-base/irrigation/"],
    SOIL_KNOWLEDGE: ["docs/knowledge-base/soils/"],
    FERTILIZER_KNOWLEDGE: ["docs/knowledge-base/fertilization/"],
    WEATHER_KNOWLEDGE: ["docs/knowledge-base/weather/"],
    REMOTE_SENSING_KNOWLEDGE: ["docs/knowledge-base/remote-sensing/"],
    GENERAL_AGRICULTURE: ["docs/knowledge-base/"],
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
    GENERAL_AGRICULTURE,
]
