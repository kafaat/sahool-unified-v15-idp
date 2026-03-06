# ═══════════════════════════════════════════════════════════════════════════════
# Agricultural Knowledge Graph Builder
# بناء الرسم البياني للمعرفة الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Unified knowledge graph data source for all SAHOOL components:
# - knowledge-graph service (apps/services/knowledge-graph/)
# - AgriRAGProvider (shared/ai/ultrarag/providers/agri_provider.py)
# - KnowledgeGraphRetriever (shared/ai/ultrarag/retriever.py)
#
# Provides a single source of truth for agricultural entities and relations,
# eliminating duplication across 3 separate hardcoded datasets.
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class KGEntity:
    """Agricultural knowledge graph entity | كيان في الرسم البياني"""

    id: str
    name: str
    name_ar: str
    entity_type: str  # crop, disease, pest, treatment, fertilizer, irrigation
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class KGRelation:
    """Agricultural knowledge graph relation | علاقة في الرسم البياني"""

    source_id: str
    target_id: str
    relation_type: str  # affects, treats, compatible_with, requires
    confidence: float = 1.0
    evidence: list[str] = field(default_factory=list)


@dataclass
class AgriculturalKnowledgeGraph:
    """Complete agricultural knowledge graph dataset | مجموعة بيانات الرسم البياني الزراعي"""

    entities: list[KGEntity] = field(default_factory=list)
    relations: list[KGRelation] = field(default_factory=list)


def build_agricultural_knowledge_graph() -> AgriculturalKnowledgeGraph:
    """Build the canonical agricultural knowledge graph.

    بناء الرسم البياني المرجعي للمعرفة الزراعية

    This is the single source of truth for all agricultural entities
    and their relationships in the SAHOOL platform.
    """

    # ═══════════════════════════════════════════════════════════════════════
    # Crop Entities - كيانات المحاصيل
    # ═══════════════════════════════════════════════════════════════════════
    crops = [
        KGEntity(
            id="crop_wheat",
            name="Wheat",
            name_ar="قمح",
            entity_type="crop",
            properties={
                "family": "Poaceae",
                "season": "winter",
                "growing_season": "winter",
                "varieties": ["Sakha 95", "Misr 1", "Gemmiza 12"],
                "optimal_temp_c": (15, 25),
                "water_req_mm": (450, 650),
            },
        ),
        KGEntity(
            id="crop_barley",
            name="Barley",
            name_ar="شعير",
            entity_type="crop",
            properties={
                "family": "Poaceae",
                "season": "winter",
                "growing_season": "winter",
                "drought_tolerant": True,
                "optimal_temp_c": (12, 22),
                "water_req_mm": (350, 500),
            },
        ),
        KGEntity(
            id="crop_date_palm",
            name="Date Palm",
            name_ar="نخيل",
            entity_type="crop",
            properties={
                "family": "Arecaceae",
                "season": "perennial",
                "growing_season": "perennial",
                "varieties": ["Barhi", "Khalas", "Sukkari", "Medjool"],
                "optimal_temp_c": (25, 40),
                "lifespan_years": 100,
            },
        ),
        KGEntity(
            id="crop_tomato",
            name="Tomato",
            name_ar="طماطم",
            entity_type="crop",
            properties={
                "family": "Solanaceae",
                "season": "summer",
                "growing_season": "summer",
                "optimal_temp_c": (20, 30),
                "water_req_mm": (400, 600),
            },
        ),
        KGEntity(
            id="crop_cucumber",
            name="Cucumber",
            name_ar="خيار",
            entity_type="crop",
            properties={
                "family": "Cucurbitaceae",
                "season": "summer",
                "growing_season": "summer",
                "optimal_temp_c": (18, 30),
            },
        ),
        KGEntity(
            id="crop_alfalfa",
            name="Alfalfa",
            name_ar="برسيم",
            entity_type="crop",
            properties={
                "family": "Fabaceae",
                "season": "perennial",
                "growing_season": "perennial",
                "nitrogen_fixing": True,
                "cuts_per_year": 8,
            },
        ),
        KGEntity(
            id="crop_potato",
            name="Potato",
            name_ar="بطاطس",
            entity_type="crop",
            properties={
                "family": "Solanaceae",
                "season": "spring",
                "growing_season": "spring",
                "optimal_temp_c": (15, 20),
                "water_req_mm": (500, 700),
            },
        ),
        KGEntity(
            id="crop_onion",
            name="Onion",
            name_ar="بصل",
            entity_type="crop",
            properties={
                "family": "Amaryllidaceae",
                "season": "winter",
                "growing_season": "winter",
                "optimal_temp_c": (13, 24),
            },
        ),
        KGEntity(
            id="crop_sorghum",
            name="Sorghum",
            name_ar="ذرة رفيعة",
            entity_type="crop",
            properties={
                "family": "Poaceae",
                "season": "summer",
                "growing_season": "summer",
                "drought_tolerant": True,
                "optimal_temp_c": (25, 35),
            },
        ),
        KGEntity(
            id="crop_millet",
            name="Millet",
            name_ar="دخن",
            entity_type="crop",
            properties={
                "family": "Poaceae",
                "season": "summer",
                "growing_season": "summer",
                "drought_tolerant": True,
                "optimal_temp_c": (25, 35),
            },
        ),
        KGEntity(
            id="crop_coffee",
            name="Coffee",
            name_ar="بن",
            entity_type="crop",
            properties={
                "family": "Rubiaceae",
                "season": "perennial",
                "growing_season": "perennial",
                "altitude_m": (1200, 2000),
                "optimal_temp_c": (15, 24),
            },
        ),
        KGEntity(
            id="crop_qat",
            name="Qat",
            name_ar="قات",
            entity_type="crop",
            properties={
                "family": "Celastraceae",
                "season": "perennial",
                "growing_season": "perennial",
                "altitude_m": (1000, 2500),
            },
        ),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # Disease Entities - كيانات الأمراض
    # ═══════════════════════════════════════════════════════════════════════
    diseases = [
        KGEntity(
            id="disease_rust",
            name="Rust Disease",
            name_ar="مرض الصدأ",
            entity_type="disease",
            properties={
                "pathogen_type": "fungal",
                "severity": "high",
                "severity_level": 8,
                "symptoms_en": ["Orange-brown pustules", "Leaf yellowing"],
                "symptoms_ar": ["بثور برتقالية-بنية", "اصفرار الأوراق"],
            },
        ),
        KGEntity(
            id="disease_powdery_mildew",
            name="Powdery Mildew",
            name_ar="البياض الدقيقي",
            entity_type="disease",
            properties={
                "pathogen_type": "fungal",
                "severity": "medium",
                "severity_level": 7,
                "symptoms_en": ["White powder coating", "Leaf distortion"],
                "symptoms_ar": ["طلاء أبيض ناعم", "تشويه الأوراق"],
            },
        ),
        KGEntity(
            id="disease_fusarium",
            name="Fusarium Wilt",
            name_ar="ذبول الفيوزاريوم",
            entity_type="disease",
            properties={
                "pathogen_type": "fungal",
                "severity": "high",
                "severity_level": 8,
                "symptoms_en": ["Wilting", "Vascular browning"],
                "symptoms_ar": ["ذبول", "اسمرار الأوعية"],
            },
        ),
        KGEntity(
            id="disease_bacterial_blight",
            name="Bacterial Blight",
            name_ar="اللفحة البكتيرية",
            entity_type="disease",
            properties={
                "pathogen_type": "bacterial",
                "severity": "high",
                "severity_level": 7,
                "symptoms_en": ["Water-soaked lesions", "Leaf necrosis"],
                "symptoms_ar": ["آفات مليئة بالماء", "نخر الأوراق"],
            },
        ),
        KGEntity(
            id="disease_late_blight",
            name="Late Blight",
            name_ar="الآفة المتأخرة",
            entity_type="disease",
            properties={
                "pathogen_type": "fungal",
                "severity": "critical",
                "severity_level": 9,
                "symptoms_en": ["Water-soaked lesions", "Brown spots", "White mold"],
                "symptoms_ar": ["آفات مليئة بالماء", "بقع بنية", "عفن أبيض"],
            },
        ),
        KGEntity(
            id="disease_leaf_spot",
            name="Leaf Spot",
            name_ar="بقعة الأوراق",
            entity_type="disease",
            properties={
                "pathogen_type": "fungal",
                "severity": "medium",
                "severity_level": 5,
                "symptoms_en": ["Circular spots", "Yellow halo"],
                "symptoms_ar": ["بقع دائرية", "هالة صفراء"],
            },
        ),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # Pest Entities - كيانات الآفات
    # ═══════════════════════════════════════════════════════════════════════
    pests = [
        KGEntity(
            id="pest_rpw",
            name="Red Palm Weevil",
            name_ar="سوسة النخيل الحمراء",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "critical",
                "severity_level": 10,
                "response_window_hours": 48,
                "reportable": True,
            },
        ),
        KGEntity(
            id="pest_leaf_miner",
            name="Leaf Miner",
            name_ar="حافرة الأوراق",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "medium",
                "severity_level": 5,
            },
        ),
        KGEntity(
            id="pest_aphid",
            name="Aphid",
            name_ar="المن",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "medium",
                "severity_level": 6,
                "vector_for": ["barley_yellow_dwarf_virus"],
            },
        ),
        KGEntity(
            id="pest_whitefly",
            name="Whitefly",
            name_ar="الذبابة البيضاء",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "high",
                "severity_level": 7,
                "vector_for": ["tomato_yellow_leaf_curl_virus"],
            },
        ),
        KGEntity(
            id="pest_locust",
            name="Desert Locust",
            name_ar="الجراد الصحراوي",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "critical",
                "severity_level": 10,
                "response_window_hours": 24,
                "reportable": True,
            },
        ),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # Treatment Entities - كيانات العلاج
    # ═══════════════════════════════════════════════════════════════════════
    treatments = [
        KGEntity(
            id="treat_propiconazole",
            name="Propiconazole",
            name_ar="بروبيكونازول",
            entity_type="treatment",
            properties={
                "type": "fungicide",
                "target": "rust",
                "treatment_type": "fungicide",
                "active_ingredient": "Propiconazole",
                "application_method": "spray",
                "safety_level": 2,
            },
        ),
        KGEntity(
            id="treat_sulfur",
            name="Sulfur",
            name_ar="كبريت",
            entity_type="treatment",
            properties={
                "type": "fungicide",
                "target": "powdery_mildew",
                "treatment_type": "fungicide",
                "active_ingredient": "Sulfur",
                "concentration": "100%",
                "application_method": "dust",
                "safety_level": 1,
                "cost_per_liter": 5.0,
            },
        ),
        KGEntity(
            id="treat_emamectin",
            name="Emamectin Benzoate",
            name_ar="إيمامكتين بنزوات",
            entity_type="treatment",
            properties={
                "type": "insecticide",
                "target": "rpw",
                "treatment_type": "insecticide",
                "active_ingredient": "Emamectin benzoate 5%",
                "application_method": "trunk_injection",
                "safety_level": 2,
                "dose_ml_per_point": (50, 100),
            },
        ),
        KGEntity(
            id="treat_copper_fungicide",
            name="Copper Fungicide",
            name_ar="مبيد فطري نحاسي",
            entity_type="treatment",
            properties={
                "type": "fungicide",
                "treatment_type": "fungicide",
                "active_ingredient": "Copper sulfate",
                "concentration": "0.5%",
                "application_method": "spray",
                "safety_level": 2,
                "cost_per_liter": 8.0,
            },
        ),
        KGEntity(
            id="treat_neem_oil",
            name="Neem Oil",
            name_ar="زيت النيم",
            entity_type="treatment",
            properties={
                "type": "organic",
                "treatment_type": "organic",
                "active_ingredient": "Azadirachtin",
                "concentration": "3%",
                "application_method": "spray",
                "safety_level": 1,
                "cost_per_liter": 12.0,
            },
        ),
        KGEntity(
            id="treat_imidacloprid",
            name="Imidacloprid",
            name_ar="إيميداكلوبريد",
            entity_type="treatment",
            properties={
                "type": "insecticide",
                "treatment_type": "systemic_insecticide",
                "target": "aphid",
                "application_method": "soil_drench",
                "safety_level": 3,
            },
        ),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # Fertilizer Entities - كيانات الأسمدة
    # ═══════════════════════════════════════════════════════════════════════
    fertilizers = [
        KGEntity(
            id="fert_urea",
            name="Urea 46%",
            name_ar="يوريا 46%",
            entity_type="fertilizer",
            properties={"type": "nitrogen", "n_content": 46, "p_content": 0, "k_content": 0},
        ),
        KGEntity(
            id="fert_dap",
            name="DAP 18-46-0",
            name_ar="داب 18-46-0",
            entity_type="fertilizer",
            properties={"type": "phosphorus", "n_content": 18, "p_content": 46, "k_content": 0},
        ),
        KGEntity(
            id="fert_potash",
            name="Potassium Sulfate",
            name_ar="سلفات البوتاسيوم",
            entity_type="fertilizer",
            properties={"type": "potassium", "n_content": 0, "p_content": 0, "k_content": 50},
        ),
        KGEntity(
            id="fert_npk",
            name="NPK 20-20-20",
            name_ar="NPK 20-20-20",
            entity_type="fertilizer",
            properties={"type": "compound", "n_content": 20, "p_content": 20, "k_content": 20},
        ),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # Irrigation Entities - كيانات الري
    # ═══════════════════════════════════════════════════════════════════════
    irrigation_methods = [
        KGEntity(
            id="irr_drip",
            name="Drip Irrigation",
            name_ar="الري بالتنقيط",
            entity_type="irrigation",
            properties={"efficiency": 90, "type": "localized"},
        ),
        KGEntity(
            id="irr_sprinkler",
            name="Sprinkler Irrigation",
            name_ar="الري بالرش",
            entity_type="irrigation",
            properties={"efficiency": 75, "type": "overhead"},
        ),
        KGEntity(
            id="irr_pivot",
            name="Center Pivot",
            name_ar="الري المحوري",
            entity_type="irrigation",
            properties={"efficiency": 85, "type": "mechanical"},
        ),
        KGEntity(
            id="irr_flood",
            name="Flood Irrigation",
            name_ar="الري بالغمر",
            entity_type="irrigation",
            properties={"efficiency": 50, "type": "surface"},
        ),
    ]

    all_entities = crops + diseases + pests + treatments + fertilizers + irrigation_methods

    # ═══════════════════════════════════════════════════════════════════════
    # Relations - العلاقات
    # ═══════════════════════════════════════════════════════════════════════
    relations = [
        # Disease → Crop (affects)
        KGRelation("disease_rust", "crop_wheat", "affects", 0.95),
        KGRelation("disease_rust", "crop_barley", "affects", 0.90),
        KGRelation("disease_powdery_mildew", "crop_wheat", "affects", 0.85),
        KGRelation("disease_powdery_mildew", "crop_cucumber", "affects", 0.90),
        KGRelation("disease_powdery_mildew", "crop_tomato", "affects", 0.80),
        KGRelation("disease_fusarium", "crop_tomato", "affects", 0.90),
        KGRelation("disease_fusarium", "crop_cucumber", "affects", 0.85),
        KGRelation("disease_bacterial_blight", "crop_tomato", "affects", 0.80),
        KGRelation("disease_late_blight", "crop_potato", "affects", 0.99),
        KGRelation("disease_late_blight", "crop_tomato", "affects", 0.95),
        KGRelation("disease_leaf_spot", "crop_tomato", "affects", 0.85),
        # Pest → Crop (affects)
        KGRelation("pest_rpw", "crop_date_palm", "affects", 0.99),
        KGRelation("pest_aphid", "crop_wheat", "affects", 0.85),
        KGRelation("pest_aphid", "crop_barley", "affects", 0.80),
        KGRelation("pest_whitefly", "crop_tomato", "affects", 0.90),
        KGRelation("pest_whitefly", "crop_cucumber", "affects", 0.85),
        KGRelation("pest_locust", "crop_wheat", "affects", 0.95),
        KGRelation("pest_locust", "crop_barley", "affects", 0.95),
        KGRelation("pest_locust", "crop_sorghum", "affects", 0.90),
        KGRelation("pest_locust", "crop_millet", "affects", 0.90),
        # Treatment → Disease/Pest (treats)
        KGRelation("treat_propiconazole", "disease_rust", "treats", 0.95),
        KGRelation("treat_sulfur", "disease_powdery_mildew", "treats", 0.95),
        KGRelation("treat_copper_fungicide", "disease_powdery_mildew", "treats", 0.90),
        KGRelation("treat_copper_fungicide", "disease_late_blight", "treats", 0.85),
        KGRelation("treat_neem_oil", "disease_late_blight", "treats", 0.70),
        KGRelation("treat_neem_oil", "pest_aphid", "treats", 0.65),
        KGRelation("treat_emamectin", "pest_rpw", "treats", 0.90),
        KGRelation("treat_imidacloprid", "pest_aphid", "treats", 0.85),
        KGRelation("treat_imidacloprid", "pest_whitefly", "treats", 0.80),
        # Treatment → Crop (compatible_with)
        KGRelation("treat_sulfur", "crop_wheat", "compatible_with", 0.99),
        KGRelation("treat_sulfur", "crop_cucumber", "compatible_with", 0.90),
        KGRelation("treat_propiconazole", "crop_wheat", "compatible_with", 0.95),
        KGRelation("treat_propiconazole", "crop_barley", "compatible_with", 0.95),
        # Fertilizer → Crop (compatible_with)
        KGRelation("fert_urea", "crop_wheat", "compatible_with", 0.95),
        KGRelation("fert_urea", "crop_barley", "compatible_with", 0.90),
        KGRelation("fert_dap", "crop_wheat", "compatible_with", 0.90),
        KGRelation("fert_dap", "crop_tomato", "compatible_with", 0.85),
        KGRelation("fert_potash", "crop_date_palm", "compatible_with", 0.90),
        KGRelation("fert_potash", "crop_tomato", "compatible_with", 0.85),
        KGRelation("fert_npk", "crop_tomato", "compatible_with", 0.90),
        KGRelation("fert_npk", "crop_cucumber", "compatible_with", 0.90),
        # Irrigation → Crop (compatible_with)
        KGRelation("irr_drip", "crop_tomato", "compatible_with", 0.95),
        KGRelation("irr_drip", "crop_date_palm", "compatible_with", 0.90),
        KGRelation("irr_drip", "crop_cucumber", "compatible_with", 0.90),
        KGRelation("irr_pivot", "crop_wheat", "compatible_with", 0.95),
        KGRelation("irr_pivot", "crop_barley", "compatible_with", 0.90),
        KGRelation("irr_pivot", "crop_alfalfa", "compatible_with", 0.85),
        KGRelation("irr_sprinkler", "crop_alfalfa", "compatible_with", 0.85),
        KGRelation("irr_sprinkler", "crop_potato", "compatible_with", 0.80),
        KGRelation("irr_flood", "crop_alfalfa", "compatible_with", 0.70),
    ]

    kg = AgriculturalKnowledgeGraph(entities=all_entities, relations=relations)

    logger.info(
        "agricultural_knowledge_graph_built",
        entities=len(all_entities),
        relations=len(relations),
        crops=len(crops),
        diseases=len(diseases),
        pests=len(pests),
        treatments=len(treatments),
        fertilizers=len(fertilizers),
        irrigation=len(irrigation_methods),
    )

    return kg
