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

from shared.ai.knowledge._logging import get_logger

logger = get_logger(__name__)


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
        # ── Bacterial Diseases ──
        KGEntity(
            id="disease_bacterial_wilt",
            name="Bacterial Wilt",
            name_ar="الذبول البكتيري",
            entity_type="disease",
            properties={
                "pathogen_type": "bacterial",
                "severity": "critical",
                "severity_level": 9,
                "symptoms_en": ["Sudden wilting", "Vascular browning", "Bacterial ooze"],
                "symptoms_ar": ["ذبول مفاجئ", "اسمرار الأوعية", "إفرازات بكتيرية"],
            },
        ),
        KGEntity(
            id="disease_fire_blight",
            name="Fire Blight",
            name_ar="لفحة النار",
            entity_type="disease",
            properties={
                "pathogen_type": "bacterial",
                "severity": "critical",
                "severity_level": 9,
                "symptoms_en": ["Shepherd's crook", "Blackened flowers", "Ooze"],
                "symptoms_ar": ["انحناء الأغصان", "احتراق الأزهار", "إفرازات لزجة"],
            },
        ),
        KGEntity(
            id="disease_bacterial_canker",
            name="Bacterial Canker",
            name_ar="التقرح البكتيري",
            entity_type="disease",
            properties={
                "pathogen_type": "bacterial",
                "severity": "high",
                "severity_level": 7,
                "symptoms_en": ["Sunken lesions", "Gumming", "Bark cracking"],
                "symptoms_ar": ["تقرحات غائرة", "إفرازات صمغية", "تشقق القلف"],
            },
        ),
        KGEntity(
            id="disease_blackleg",
            name="Blackleg",
            name_ar="الساق الأسود",
            entity_type="disease",
            properties={
                "pathogen_type": "bacterial",
                "severity": "high",
                "severity_level": 7,
                "symptoms_en": ["Black stem base rot", "Foul smell", "Tuber rot"],
                "symptoms_ar": ["تعفن أسود في قاعدة الساق", "رائحة كريهة", "تعفن الدرنات"],
            },
        ),
        # ── Viral Diseases ──
        KGEntity(
            id="disease_mosaic_virus",
            name="Mosaic Virus",
            name_ar="فيروس الموزايك",
            entity_type="disease",
            properties={
                "pathogen_type": "viral",
                "severity": "high",
                "severity_level": 7,
                "symptoms_en": ["Leaf mottling", "Stunting", "Fruit deformation"],
                "symptoms_ar": ["تبرقش الأوراق", "تقزم", "تشوه الثمار"],
                "vectors": ["aphid"],
            },
        ),
        KGEntity(
            id="disease_tylcv",
            name="Tomato Yellow Leaf Curl Virus",
            name_ar="فيروس تجعد أوراق الطماطم الأصفر",
            entity_type="disease",
            properties={
                "pathogen_type": "viral",
                "severity": "critical",
                "severity_level": 9,
                "symptoms_en": ["Leaf curling upward", "Yellowing", "Severe stunting"],
                "symptoms_ar": ["تجعد الأوراق للأعلى", "اصفرار", "تقزم شديد"],
                "vectors": ["whitefly"],
            },
        ),
        KGEntity(
            id="disease_ctv",
            name="Citrus Tristeza Virus",
            name_ar="فيروس تريستيزا الحمضيات",
            entity_type="disease",
            properties={
                "pathogen_type": "viral",
                "severity": "critical",
                "severity_level": 10,
                "symptoms_en": ["Tree decline", "Stem pitting", "Leaf drop"],
                "symptoms_ar": ["تدهور الشجرة", "حفر في الخشب", "تساقط الأوراق"],
                "vectors": ["aphid"],
            },
        ),
        KGEntity(
            id="disease_cotton_leaf_curl",
            name="Cotton Leaf Curl Virus",
            name_ar="فيروس تجعد أوراق القطن",
            entity_type="disease",
            properties={
                "pathogen_type": "viral",
                "severity": "critical",
                "severity_level": 9,
                "symptoms_en": ["Leaf curling", "Vein swelling", "Boll deformation"],
                "symptoms_ar": ["تجعد الأوراق", "تورم العروق", "تشوه اللوز"],
                "vectors": ["whitefly"],
            },
        ),
        # ── Nutrient Deficiency Disorders ──
        KGEntity(
            id="disease_nitrogen_deficiency",
            name="Nitrogen Deficiency",
            name_ar="نقص النيتروجين",
            entity_type="disease",
            properties={
                "pathogen_type": "abiotic",
                "severity": "high",
                "severity_level": 7,
                "symptoms_en": ["Lower leaf yellowing", "Stunted growth", "Delayed flowering"],
                "symptoms_ar": ["اصفرار الأوراق السفلية", "تقزم النمو", "تأخر التزهير"],
            },
        ),
        KGEntity(
            id="disease_phosphorus_deficiency",
            name="Phosphorus Deficiency",
            name_ar="نقص الفوسفور",
            entity_type="disease",
            properties={
                "pathogen_type": "abiotic",
                "severity": "medium",
                "severity_level": 6,
                "symptoms_en": ["Purple leaves", "Delayed maturity", "Weak roots"],
                "symptoms_ar": ["أوراق بنفسجية", "تأخر النضج", "جذور ضعيفة"],
            },
        ),
        KGEntity(
            id="disease_potassium_deficiency",
            name="Potassium Deficiency",
            name_ar="نقص البوتاسيوم",
            entity_type="disease",
            properties={
                "pathogen_type": "abiotic",
                "severity": "medium",
                "severity_level": 5,
                "symptoms_en": ["Marginal leaf burn", "Weak stems", "Poor fruit quality"],
                "symptoms_ar": ["احتراق حواف الأوراق", "ضعف الساق", "ثمار سيئة الجودة"],
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
        KGEntity(
            id="pest_sunn_pest",
            name="Sunn Pest",
            name_ar="حشرة السونة",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "high",
                "severity_level": 8,
            },
        ),
        KGEntity(
            id="pest_armyworm",
            name="Fall Armyworm",
            name_ar="دودة الحشد",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "high",
                "severity_level": 8,
                "activity": "nocturnal",
            },
        ),
        KGEntity(
            id="pest_thrips",
            name="Thrips",
            name_ar="التربس",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "medium",
                "severity_level": 6,
                "vector_for": ["tomato_spotted_wilt_virus"],
            },
        ),
        KGEntity(
            id="pest_spider_mite",
            name="Red Spider Mite",
            name_ar="العنكبوت الأحمر",
            entity_type="pest",
            properties={
                "type": "arachnid",
                "severity": "medium",
                "severity_level": 6,
            },
        ),
        KGEntity(
            id="pest_date_bunch_borer",
            name="Date Bunch Borer",
            name_ar="حفار العذوق",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "medium",
                "severity_level": 5,
            },
        ),
        KGEntity(
            id="pest_bollworm",
            name="Cotton Bollworm",
            name_ar="دودة اللوز",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "high",
                "severity_level": 8,
            },
        ),
        KGEntity(
            id="pest_stem_borer",
            name="Corn Stem Borer",
            name_ar="حفار ساق الذرة",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "high",
                "severity_level": 7,
            },
        ),
        KGEntity(
            id="pest_fruit_fly",
            name="Fruit Fly",
            name_ar="ذبابة الفاكهة",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "high",
                "severity_level": 7,
                "reportable": True,
            },
        ),
        KGEntity(
            id="pest_citrus_psyllid",
            name="Citrus Psyllid",
            name_ar="بسيلا الحمضيات",
            entity_type="pest",
            properties={
                "type": "insect",
                "severity": "critical",
                "severity_level": 9,
                "vector_for": ["huanglongbing"],
                "reportable": True,
            },
        ),
        KGEntity(
            id="pest_nematode",
            name="Root-Knot Nematode",
            name_ar="نيماتودا تعقد الجذور",
            entity_type="pest",
            properties={
                "type": "nematode",
                "severity": "high",
                "severity_level": 7,
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
            properties={
                "efficiency": 85,
                "type": "mechanical",
                "brands": ["Valley", "Zimmatic", "Reinke"],
                "coverage_ha": (20, 200),
                "pressure_bar": (1.0, 4.0),
            },
        ),
        KGEntity(
            id="irr_pivot_lepa",
            name="LEPA Center Pivot",
            name_ar="المحوري منخفض الضغط (LEPA)",
            entity_type="irrigation",
            properties={
                "efficiency": 97,
                "type": "mechanical",
                "pressure_bar": (0.4, 1.0),
                "application": "near_surface",
                "energy_saving_pct": 50,
                "best_for_soil": ["clay", "clay_loam"],
            },
        ),
        KGEntity(
            id="irr_pivot_vri",
            name="VRI Center Pivot",
            name_ar="المحوري بمعدل متغير (VRI)",
            entity_type="irrigation",
            properties={
                "efficiency": 92,
                "type": "mechanical",
                "precision": "zone_or_individual_nozzle",
                "water_saving_pct": (15, 25),
                "requires": ["NDVI_map", "soil_moisture_sensors", "GPS"],
                "brands": ["Valley ICON", "FieldNET"],
            },
        ),
        KGEntity(
            id="irr_linear_move",
            name="Linear Move",
            name_ar="الري الخطي المتحرك",
            entity_type="irrigation",
            properties={
                "efficiency": 88,
                "type": "mechanical",
                "coverage_ha": (20, 100),
                "pressure_bar": (2.0, 4.0),
                "field_shape": "rectangular",
                "brands": ["Valley Linear", "Zimmatic"],
            },
        ),
        KGEntity(
            id="irr_flood",
            name="Flood Irrigation",
            name_ar="الري بالغمر",
            entity_type="irrigation",
            properties={"efficiency": 50, "type": "surface"},
        ),
        KGEntity(
            id="irr_chemigation",
            name="Chemigation via Pivot",
            name_ar="التسميد والمعالجة عبر المحور",
            entity_type="irrigation",
            properties={
                "efficiency": 90,
                "type": "application",
                "parent": "center_pivot",
                "applications": ["fertigation", "herbigation", "insectigation", "fungigation"],
                "requires": ["check_valve", "injection_pump", "calibration"],
            },
        ),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # Pivot Equipment Entities - معدات المحور
    # ═══════════════════════════════════════════════════════════════════════
    pivot_equipment = [
        KGEntity(
            id="equip_icon5",
            name="Valley ICON 5 Smart Panel",
            name_ar="لوحة تحكم Valley ICON 5 الذكية",
            entity_type="equipment",
            properties={
                "type": "control_panel",
                "brand": "Valley",
                "connectivity": ["4G_LTE", "Wi-Fi", "Satellite"],
                "features": ["GPS", "VRI", "scheduling", "alerts", "telemetry"],
                "app": "AgSense 365",
                "operating_temp_c": (-20, 60),
            },
        ),
        KGEntity(
            id="equip_submersible_pump",
            name="Submersible Well Pump",
            name_ar="مضخة غاطسة",
            entity_type="equipment",
            properties={
                "type": "pump",
                "power_kw": (15, 150),
                "depth_m": (30, 300),
                "flow_m3h": (20, 200),
                "brands": ["Grundfos", "Caprari", "Pedrollo", "KSB"],
                "drive": ["electric", "solar_vfd"],
            },
        ),
        KGEntity(
            id="equip_booster_pump",
            name="Booster Pump",
            name_ar="مضخة تعزيز (بوستر)",
            entity_type="equipment",
            properties={
                "type": "pump",
                "purpose": "increase_pressure",
                "power_kw": (5, 50),
                "use_case": "low_well_pressure_or_long_pipeline",
                "brands": ["Grundfos", "DAB", "Pentair"],
            },
        ),
        KGEntity(
            id="equip_vfd",
            name="Variable Frequency Drive",
            name_ar="محول تردد متغير (VFD/إنفرتر)",
            entity_type="equipment",
            properties={
                "type": "drive",
                "purpose": "pump_speed_control",
                "energy_saving_pct": (20, 40),
                "brands": ["ABB", "Danfoss", "Siemens", "Yaskawa"],
                "compatible": ["solar", "grid", "diesel_generator"],
            },
        ),
        KGEntity(
            id="equip_solar_pump_system",
            name="Solar Pump System",
            name_ar="نظام ضخ بالطاقة الشمسية",
            entity_type="equipment",
            properties={
                "type": "energy_system",
                "components": ["solar_panels", "solar_vfd", "pump", "combiner_box"],
                "panel_power_w": 550,
                "system_kw": (5, 150),
                "roi_years": (3, 5),
                "brands": ["Lorentz", "Grundfos SQFlex", "Franklin Electric"],
            },
        ),
        KGEntity(
            id="equip_filtration",
            name="Irrigation Filtration System",
            name_ar="نظام ترشيح مياه الري",
            entity_type="equipment",
            properties={
                "type": "filtration",
                "filter_types": ["sand_media", "disc", "screen", "hydrocyclone"],
                "purpose": "prevent_nozzle_clogging",
                "mesh_size": (80, 200),
                "auto_flush": True,
                "brands": ["Amiad", "Netafim", "Arkal"],
            },
        ),
        KGEntity(
            id="equip_flow_meter",
            name="Flow Meter",
            name_ar="عداد تدفق",
            entity_type="equipment",
            properties={
                "type": "sensor",
                "sensor_types": ["electromagnetic", "ultrasonic", "propeller"],
                "accuracy_pct": (0.5, 2.0),
                "output": ["pulse", "4-20mA", "modbus"],
                "brands": ["McCrometer", "Seametrics", "Badger"],
            },
        ),
        KGEntity(
            id="equip_pressure_regulator",
            name="Pressure Regulator",
            name_ar="منظم ضغط",
            entity_type="equipment",
            properties={
                "type": "accessory",
                "purpose": "uniform_application",
                "pressure_range_psi": (6, 30),
                "location": "at_each_drop_or_nozzle",
                "brands": ["Nelson", "Senninger"],
            },
        ),
        KGEntity(
            id="equip_sprinkler_package",
            name="Sprinkler/Nozzle Package",
            name_ar="حزمة الرشاشات والفوهات",
            entity_type="equipment",
            properties={
                "type": "nozzle",
                "nozzle_types": [
                    "i-Wob (Senninger)",
                    "Rotator (Nelson)",
                    "Spinner (Nelson)",
                    "LEPA Bubble (Senninger)",
                    "LDN (Senninger)",
                    "S3000 (Senninger)",
                ],
                "selection_by": ["soil_type", "crop_height", "wind_speed", "pressure"],
            },
        ),
    ]

    all_entities = crops + diseases + pests + treatments + fertilizers + irrigation_methods + pivot_equipment

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
        # Bacterial Disease → Crop (affects)
        KGRelation("disease_bacterial_wilt", "crop_tomato", "affects", 0.90),
        KGRelation("disease_bacterial_wilt", "crop_potato", "affects", 0.85),
        KGRelation("disease_fire_blight", "crop_date_palm", "affects", 0.60),
        KGRelation("disease_bacterial_canker", "crop_tomato", "affects", 0.75),
        KGRelation("disease_blackleg", "crop_potato", "affects", 0.90),
        # Viral Disease → Crop (affects)
        KGRelation("disease_mosaic_virus", "crop_tomato", "affects", 0.90),
        KGRelation("disease_mosaic_virus", "crop_cucumber", "affects", 0.85),
        KGRelation("disease_tylcv", "crop_tomato", "affects", 0.99),
        KGRelation("disease_ctv", "crop_date_palm", "affects", 0.50),
        # Nutrient Deficiency → Crop (affects)
        KGRelation("disease_nitrogen_deficiency", "crop_wheat", "affects", 0.90),
        KGRelation("disease_nitrogen_deficiency", "crop_barley", "affects", 0.85),
        KGRelation("disease_phosphorus_deficiency", "crop_wheat", "affects", 0.80),
        KGRelation("disease_potassium_deficiency", "crop_date_palm", "affects", 0.85),
        KGRelation("disease_potassium_deficiency", "crop_tomato", "affects", 0.80),
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
        # New Pest → Crop (affects)
        KGRelation("pest_sunn_pest", "crop_wheat", "affects", 0.90),
        KGRelation("pest_sunn_pest", "crop_barley", "affects", 0.85),
        KGRelation("pest_armyworm", "crop_wheat", "affects", 0.85),
        KGRelation("pest_armyworm", "crop_sorghum", "affects", 0.80),
        KGRelation("pest_thrips", "crop_tomato", "affects", 0.80),
        KGRelation("pest_thrips", "crop_onion", "affects", 0.85),
        KGRelation("pest_spider_mite", "crop_date_palm", "affects", 0.80),
        KGRelation("pest_spider_mite", "crop_cucumber", "affects", 0.75),
        KGRelation("pest_date_bunch_borer", "crop_date_palm", "affects", 0.85),
        KGRelation("pest_bollworm", "crop_tomato", "affects", 0.80),
        KGRelation("pest_stem_borer", "crop_sorghum", "affects", 0.80),
        KGRelation("pest_fruit_fly", "crop_date_palm", "affects", 0.75),
        KGRelation("pest_citrus_psyllid", "crop_date_palm", "affects", 0.40),
        KGRelation("pest_nematode", "crop_tomato", "affects", 0.85),
        KGRelation("pest_nematode", "crop_cucumber", "affects", 0.80),
        KGRelation("pest_nematode", "crop_potato", "affects", 0.80),
        # Viral disease vectored by pests
        KGRelation("pest_whitefly", "disease_tylcv", "transmits", 0.95),
        KGRelation("pest_whitefly", "disease_cotton_leaf_curl", "transmits", 0.90),
        KGRelation("pest_aphid", "disease_mosaic_virus", "transmits", 0.85),
        KGRelation("pest_aphid", "disease_ctv", "transmits", 0.80),
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
        KGRelation("treat_imidacloprid", "pest_thrips", "treats", 0.75),
        KGRelation("treat_emamectin", "pest_armyworm", "treats", 0.90),
        KGRelation("treat_emamectin", "pest_bollworm", "treats", 0.85),
        KGRelation("treat_copper_fungicide", "disease_bacterial_blight", "treats", 0.80),
        KGRelation("treat_copper_fungicide", "disease_bacterial_canker", "treats", 0.75),
        KGRelation("treat_copper_fungicide", "disease_fire_blight", "treats", 0.70),
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
        KGRelation("irr_pivot", "crop_sorghum", "compatible_with", 0.80),
        KGRelation("irr_pivot", "crop_potato", "compatible_with", 0.80),
        # LEPA pivot - best for clay soils and water-scarce regions
        KGRelation("irr_pivot_lepa", "crop_wheat", "compatible_with", 0.98),
        KGRelation("irr_pivot_lepa", "crop_barley", "compatible_with", 0.95),
        KGRelation("irr_pivot_lepa", "crop_alfalfa", "compatible_with", 0.90),
        # VRI pivot - precision irrigation
        KGRelation("irr_pivot_vri", "crop_wheat", "compatible_with", 0.95),
        KGRelation("irr_pivot_vri", "crop_potato", "compatible_with", 0.95),
        KGRelation("irr_pivot_vri", "crop_barley", "compatible_with", 0.90),
        # Linear move - rectangular fields
        KGRelation("irr_linear_move", "crop_wheat", "compatible_with", 0.90),
        KGRelation("irr_linear_move", "crop_barley", "compatible_with", 0.85),
        KGRelation("irr_linear_move", "crop_alfalfa", "compatible_with", 0.85),
        KGRelation("irr_linear_move", "crop_potato", "compatible_with", 0.85),
        # LEPA/VRI are subtypes of center pivot
        KGRelation("irr_pivot_lepa", "irr_pivot", "subtype_of", 1.0),
        KGRelation("irr_pivot_vri", "irr_pivot", "subtype_of", 1.0),
        # Sprinkler and flood
        KGRelation("irr_sprinkler", "crop_alfalfa", "compatible_with", 0.85),
        KGRelation("irr_sprinkler", "crop_potato", "compatible_with", 0.80),
        KGRelation("irr_flood", "crop_alfalfa", "compatible_with", 0.70),
        # Chemigation → Crops
        KGRelation("irr_chemigation", "crop_wheat", "compatible_with", 0.90),
        KGRelation("irr_chemigation", "crop_alfalfa", "compatible_with", 0.85),
        KGRelation("irr_chemigation", "crop_potato", "compatible_with", 0.90),
        # Equipment → Irrigation (requires)
        KGRelation("irr_pivot", "equip_icon5", "requires", 0.90),
        KGRelation("irr_pivot", "equip_submersible_pump", "requires", 0.95),
        KGRelation("irr_pivot", "equip_filtration", "requires", 0.90),
        KGRelation("irr_pivot", "equip_flow_meter", "requires", 0.85),
        KGRelation("irr_pivot", "equip_pressure_regulator", "requires", 0.95),
        KGRelation("irr_pivot", "equip_sprinkler_package", "requires", 0.99),
        KGRelation("irr_pivot_vri", "equip_icon5", "requires", 0.99),
        KGRelation("equip_submersible_pump", "equip_vfd", "compatible_with", 0.95),
        KGRelation("equip_submersible_pump", "equip_solar_pump_system", "compatible_with", 0.90),
        KGRelation("equip_solar_pump_system", "equip_vfd", "requires", 0.99),
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
        equipment=len(pivot_equipment),
    )

    return kg
