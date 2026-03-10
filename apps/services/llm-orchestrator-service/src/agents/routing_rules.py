# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Routing rules for agent selection.

Simple rule-based definitions for mapping intents to agents.
Fast, no LLM needed, easy to modify.

قواعد التوجيه لاختيار الوكلاء.
تعريفات بسيطة قائمة على القواعد لربط النوايا بالوكلاء.
سريعة، لا تحتاج إلى نماذج لغوية، سهلة التعديل.
"""

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Literal


class Priority(StrEnum):
    """Routing priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RoutingRule:
    """
    A single routing rule definition.
    تعريف قاعدة توجيه واحدة.
    """

    intent: str
    agents: list[str]
    priority: Priority = Priority.MEDIUM
    requires_image: bool = False
    requires_field_id: bool = False
    description_en: str = ""
    description_ar: str = ""
    keywords_en: list[str] = field(default_factory=list)
    keywords_ar: list[str] = field(default_factory=list)
    fallback_agents: list[str] = field(default_factory=list)


# Main routing rules - Intent -> Agents mapping
ROUTING_RULES: dict[str, RoutingRule] = {
    # Crop Disease Detection - High priority, may need vision
    "crop_disease": RoutingRule(
        intent="crop_disease",
        agents=["yolo-vision", "crop-intelligence", "advisory"],
        priority=Priority.HIGH,
        requires_image=True,
        description_en="Crop disease detection and diagnosis",
        description_ar="كشف وتشخيص أمراض المحاصيل",
        keywords_en=[
            "disease",
            "sick",
            "infected",
            "fungus",
            "bacteria",
            "rot",
            "rust",
            "spots",
            "wilt",
            "yellowing",
            "blight",
            "infection",
            "leaf",
            "brown",
        ],
        keywords_ar=[
            "مرض",
            "أمراض",
            "فطريات",
            "بكتيريا",
            "عفن",
            "صدأ",
            "بقع",
            "ذبول",
            "اصفرار",
            "تعفن",
            "لفحة",
            "تبقع",
            "ورقة",
            "أوراق",
        ],
        fallback_agents=["crop-intelligence", "advisory"],
    ),
    # Pest Detection - High priority, needs vision
    "pest_detection": RoutingRule(
        intent="pest_detection",
        agents=["yolo-vision", "pest-detection", "advisory"],
        priority=Priority.HIGH,
        requires_image=True,
        description_en="Pest identification and control advice",
        description_ar="تحديد الآفات ونصائح المكافحة",
        keywords_en=[
            "pest",
            "bug",
            "insect",
            "worm",
            "larva",
            "fly",
            "aphid",
            "mite",
            "locust",
            "caterpillar",
            "beetle",
            "weevil",
        ],
        keywords_ar=[
            "آفة",
            "آفات",
            "حشرات",
            "دودة",
            "يرقة",
            "ذبابة",
            "من",
            "سوس",
            "جراد",
            "خنفساء",
            "سوسة",
        ],
        fallback_agents=["pest-detection", "advisory"],
    ),
    # Irrigation Query - Medium priority
    "irrigation_query": RoutingRule(
        intent="irrigation_query",
        agents=["weather", "irrigation", "advisory"],
        priority=Priority.MEDIUM,
        requires_field_id=True,
        description_en="Irrigation scheduling and water management",
        description_ar="جدولة الري وإدارة المياه",
        keywords_en=[
            "irrigation",
            "water",
            "watering",
            "moisture",
            "dry",
            "drought",
            "drip",
            "sprinkler",
            "thirsty",
            "schedule",
        ],
        keywords_ar=[
            "ري",
            "ماء",
            "سقي",
            "رطوبة",
            "جفاف",
            "عطش",
            "مياه",
            "رش",
            "تنقيط",
            "جدول",
        ],
        fallback_agents=["irrigation", "advisory"],
    ),
    # Fertilizer Advice - Medium priority
    "fertilizer_advice": RoutingRule(
        intent="fertilizer_advice",
        agents=["crop-intelligence", "advisory"],
        priority=Priority.MEDIUM,
        requires_field_id=True,
        description_en="Fertilizer recommendations and nutrient management",
        description_ar="توصيات الأسمدة وإدارة العناصر الغذائية",
        keywords_en=[
            "fertilizer",
            "fertilize",
            "nitrogen",
            "phosphorus",
            "potassium",
            "nutrient",
            "urea",
            "npk",
            "deficiency",
            "feed",
        ],
        keywords_ar=[
            "سماد",
            "تسميد",
            "نيتروجين",
            "فوسفور",
            "بوتاسيوم",
            "عناصر",
            "غذائية",
            "يوريا",
            "مغذيات",
            "نقص",
        ],
        fallback_agents=["advisory"],
    ),
    # Weather Query - Low priority
    "weather_query": RoutingRule(
        intent="weather_query",
        agents=["weather"],
        priority=Priority.LOW,
        description_en="Weather information and forecasts",
        description_ar="معلومات الطقس والتنبؤات",
        keywords_en=[
            "weather",
            "temperature",
            "rain",
            "wind",
            "humidity",
            "forecast",
            "cold",
            "frost",
            "climate",
            "hot",
            "sunny",
        ],
        keywords_ar=[
            "طقس",
            "حرارة",
            "مطر",
            "رياح",
            "رطوبة",
            "جو",
            "درجة",
            "توقعات",
            "برد",
            "صقيع",
            "حار",
        ],
        fallback_agents=[],
    ),
    # Yield Prediction - Medium priority
    "yield_prediction": RoutingRule(
        intent="yield_prediction",
        agents=["crop-intelligence", "yield-prediction-service", "field-intelligence"],
        priority=Priority.MEDIUM,
        requires_field_id=True,
        description_en="Yield estimation and harvest planning",
        description_ar="تقدير المحصول وتخطيط الحصاد",
        keywords_en=[
            "yield",
            "harvest",
            "production",
            "predict",
            "estimate",
            "output",
            "ton",
            "kg",
            "quantity",
        ],
        keywords_ar=[
            "محصول",
            "إنتاج",
            "حصاد",
            "غلة",
            "إنتاجية",
            "كمية",
            "توقع",
            "تنبؤ",
            "طن",
        ],
        fallback_agents=["yield-prediction-service"],
    ),
    # Field Analysis - Medium priority
    "field_analysis": RoutingRule(
        intent="field_analysis",
        agents=["field-intelligence", "indicators", "crop-intelligence"],
        priority=Priority.MEDIUM,
        requires_field_id=True,
        description_en="Field status and health analysis",
        description_ar="تحليل حالة الحقل وصحته",
        keywords_en=[
            "field",
            "land",
            "soil",
            "area",
            "zone",
            "plot",
            "analysis",
            "assess",
            "ndvi",
            "status",
        ],
        keywords_ar=[
            "حقل",
            "أرض",
            "تربة",
            "مساحة",
            "منطقة",
            "قطعة",
            "تحليل",
            "فحص",
            "حالة",
        ],
        fallback_agents=["field-intelligence"],
    ),
    # Terrain Analysis - Low priority
    "terrain_analysis": RoutingRule(
        intent="terrain_analysis",
        agents=["terrain", "hydrology", "leveling"],
        priority=Priority.LOW,
        requires_field_id=True,
        description_en="Terrain and topography analysis",
        description_ar="تحليل التضاريس والطبوغرافيا",
        keywords_en=[
            "terrain",
            "elevation",
            "slope",
            "gradient",
            "topography",
            "contour",
            "dem",
            "height",
        ],
        keywords_ar=[
            "تضاريس",
            "ارتفاع",
            "انحدار",
            "ميل",
            "جبل",
            "وادي",
            "سطح",
            "طبوغرافيا",
        ],
        fallback_agents=["terrain"],
    ),
    # Hydrology Query - Low priority
    "hydrology_query": RoutingRule(
        intent="hydrology_query",
        agents=["hydrology", "terrain"],
        priority=Priority.LOW,
        requires_field_id=True,
        description_en="Hydrology and drainage analysis",
        description_ar="تحليل الهيدرولوجيا والصرف",
        keywords_en=[
            "drainage",
            "watershed",
            "hydrology",
            "flow",
            "runoff",
            "catchment",
            "flood",
            "water",
        ],
        keywords_ar=[
            "صرف",
            "تصريف",
            "مستجمع",
            "جريان",
            "هيدرولوجي",
            "مياه",
            "فيضان",
        ],
        fallback_agents=["hydrology"],
    ),
    # Leveling Query - Low priority
    "leveling_query": RoutingRule(
        intent="leveling_query",
        agents=["leveling", "terrain"],
        priority=Priority.LOW,
        requires_field_id=True,
        description_en="Land leveling and grading optimization",
        description_ar="تحسين تسوية الأراضي والتمهيد",
        keywords_en=[
            "leveling",
            "grading",
            "cut",
            "fill",
            "land",
            "preparation",
            "level",
            "flat",
        ],
        keywords_ar=[
            "تسوية",
            "استصلاح",
            "تمهيد",
            "قطع",
            "ردم",
            "مستوى",
        ],
        fallback_agents=["leveling"],
    ),
    # Image Analysis - High priority when image present
    "image_analysis": RoutingRule(
        intent="image_analysis",
        agents=["yolo-vision", "pest-detection", "crop-intelligence"],
        priority=Priority.HIGH,
        requires_image=True,
        description_en="General image analysis for crops",
        description_ar="تحليل عام للصور الزراعية",
        keywords_en=[
            "image",
            "photo",
            "picture",
            "camera",
            "visual",
            "scan",
            "detect",
            "what",
            "identify",
        ],
        keywords_ar=[
            "صورة",
            "صور",
            "تصوير",
            "كاميرا",
            "فحص",
            "مرئي",
            "حدد",
        ],
        fallback_agents=["yolo-vision"],
    ),
    # General Advisory - Low priority, fallback
    "general_advisory": RoutingRule(
        intent="general_advisory",
        agents=["advisory", "crop-intelligence"],
        priority=Priority.LOW,
        description_en="General agricultural advice",
        description_ar="نصائح زراعية عامة",
        keywords_en=[
            "advice",
            "help",
            "recommend",
            "suggest",
            "best",
            "how",
            "when",
            "what",
            "should",
        ],
        keywords_ar=[
            "نصيحة",
            "مساعدة",
            "توصية",
            "اقتراح",
            "أفضل",
            "كيف",
            "متى",
            "ماذا",
        ],
        fallback_agents=["advisory"],
    ),
}


# Intent synonyms for flexible matching
INTENT_SYNONYMS: dict[str, list[str]] = {
    "crop_disease": ["disease", "infection", "sick_plant", "plant_disease"],
    "pest_detection": ["pest", "insect", "bug", "worm"],
    "irrigation_query": ["irrigation", "watering", "water"],
    "fertilizer_advice": ["fertilizer", "nutrient", "feeding"],
    "weather_query": ["weather", "forecast", "climate"],
    "yield_prediction": ["yield", "harvest", "production"],
    "field_analysis": ["field", "soil", "land"],
    "terrain_analysis": ["terrain", "topography", "elevation"],
    "hydrology_query": ["hydrology", "drainage", "watershed"],
    "leveling_query": ["leveling", "grading"],
    "image_analysis": ["image", "photo", "picture", "scan"],
    "general_advisory": ["advice", "help", "general"],
}


def get_rule(intent: str) -> RoutingRule | None:
    """
    Get routing rule for an intent.
    الحصول على قاعدة التوجيه للنية.
    """
    return ROUTING_RULES.get(intent)


def get_all_rules() -> dict[str, RoutingRule]:
    """
    Get all routing rules.
    الحصول على جميع قواعد التوجيه.
    """
    return ROUTING_RULES


def get_rules_for_display() -> list[dict]:
    """
    Get routing rules formatted for API display.
    الحصول على قواعد التوجيه منسقة للعرض في API.
    """
    return [
        {
            "intent": rule.intent,
            "agents": rule.agents,
            "priority": rule.priority.value,
            "requires_image": rule.requires_image,
            "requires_field_id": rule.requires_field_id,
            "description_en": rule.description_en,
            "description_ar": rule.description_ar,
            "keywords_en": rule.keywords_en[:5],  # Show first 5
            "keywords_ar": rule.keywords_ar[:5],
            "fallback_agents": rule.fallback_agents,
        }
        for rule in ROUTING_RULES.values()
    ]
