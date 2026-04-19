# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Intent Classifier for LLM Orchestrator Service.

This module classifies user intents from natural language input
(Arabic and English) and extracts relevant entities.

مصنف النوايا لخدمة تنسيق نماذج اللغة الكبيرة.
تصنف هذه الوحدة نوايا المستخدم من الإدخال باللغة الطبيعية
(العربية والإنجليزية) وتستخرج الكيانات ذات الصلة.
"""

import re
from typing import Any

import structlog

from ..api.schemas import IntentClassification, IntentType, UserIntent
from ..core.config import settings

logger = structlog.get_logger(__name__)

# Intent keywords for pattern matching (Arabic and English)
INTENT_KEYWORDS: dict[IntentType, dict[str, list[str]]] = {
    IntentType.CROP_DISEASE: {
        "ar": [
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
        ],
        "en": [
            "disease",
            "fungus",
            "fungi",
            "bacteria",
            "rot",
            "rust",
            "spots",
            "wilt",
            "yellow",
            "yellowing",
            "blight",
            "infection",
        ],
    },
    IntentType.IRRIGATION_QUERY: {
        "ar": ["ري", "ماء", "سقي", "رطوبة", "جفاف", "عطش", "مياه", "رش", "تنقيط"],
        "en": [
            "irrigation",
            "irrigate",
            "water",
            "watering",
            "moisture",
            "dry",
            "drought",
            "drip",
            "sprinkler",
        ],
    },
    IntentType.FERTILIZER_ADVICE: {
        "ar": [
            "سماد",
            "تسميد",
            "نيتروجين",
            "فوسفور",
            "بوتاسيوم",
            "عناصر",
            "غذائية",
            "يوريا",
            "مغذيات",
        ],
        "en": [
            "fertilizer",
            "fertilize",
            "nitrogen",
            "phosphorus",
            "potassium",
            "nutrient",
            "urea",
            "npk",
        ],
    },
    IntentType.PEST_DETECTION: {
        "ar": ["آفة", "آفات", "حشرات", "دودة", "يرقة", "ذبابة", "من", "سوس", "جراد"],
        "en": [
            "pest",
            "insect",
            "worm",
            "larva",
            "fly",
            "aphid",
            "mite",
            "locust",
            "bug",
        ],
    },
    IntentType.WEATHER_QUERY: {
        "ar": [
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
        ],
        "en": [
            "weather",
            "temperature",
            "rain",
            "wind",
            "humidity",
            "forecast",
            "cold",
            "frost",
            "climate",
        ],
    },
    IntentType.YIELD_PREDICTION: {
        # NOTE: "crop" / "محصول" / "كمية" / "توقع" were removed from this
        # category because they are overly generic and appear in crop-disease,
        # fertilizer, and pest queries too. With the old scoring formula they
        # caused YIELD_PREDICTION to win over the correct intent on a single
        # weak match. Specific yield terms (yield / harvest / إنتاجية / غلة)
        # remain as the disambiguating signal.
        "ar": [
            "إنتاج",
            "حصاد",
            "غلة",
            "إنتاجية",
            "تنبؤ",
        ],
        "en": [
            "yield",
            "harvest",
            "production",
            "predict",
            "estimate",
            "output",
        ],
    },
    IntentType.FIELD_ANALYSIS: {
        "ar": [
            "حقل",
            "أرض",
            "تربة",
            "مساحة",
            "منطقة",
            "قطعة",
            "تحليل",
            "فحص",
        ],
        "en": ["field", "land", "soil", "area", "zone", "plot", "analysis", "assess"],
    },
    IntentType.TERRAIN_ANALYSIS: {
        "ar": ["تضاريس", "ارتفاع", "انحدار", "ميل", "جبل", "وادي", "سطح"],
        "en": [
            "terrain",
            "elevation",
            "slope",
            "gradient",
            "topography",
            "contour",
            "dem",
        ],
    },
    IntentType.HYDROLOGY_QUERY: {
        "ar": ["صرف", "تصريف", "مستجمع", "جريان", "هيدرولوجي", "مياه", "فيضان"],
        "en": [
            "drainage",
            "watershed",
            "hydrology",
            "flow",
            "runoff",
            "catchment",
            "flood",
        ],
    },
    IntentType.LEVELING_QUERY: {
        "ar": ["تسوية", "استصلاح", "تمهيد", "قطع", "ردم", "مستوى"],
        "en": ["leveling", "grading", "cut", "fill", "land", "preparation", "level"],
    },
    IntentType.IMAGE_ANALYSIS: {
        "ar": ["صورة", "صور", "تصوير", "كاميرا", "فحص", "مرئي"],
        "en": ["image", "photo", "picture", "camera", "visual", "scan", "detect"],
    },
}

# Intent scoring constants — each matched keyword contributes
# PER_KEYWORD_WEIGHT, capped at MAX_INTENT_SCORE. See
# `calculate_intent_score()` for rationale.
PER_KEYWORD_WEIGHT: float = 0.55
MAX_INTENT_SCORE: float = 0.95

# Entity patterns (Arabic and English)
ENTITY_PATTERNS: dict[str, dict[str, str]] = {
    "crop_type": {
        "ar": r"(قمح|شعير|أرز|ذرة|طماطم|خيار|بصل|ثوم|نخيل|زيتون|عنب|تفاح|برتقال|موز)",
        "en": r"(wheat|barley|rice|corn|maize|tomato|cucumber|onion|garlic|palm|olive|grape|apple|orange|banana)",
    },
    "field_id": {
        "ar": r"(?:حقل|قطعة)\s*(?:رقم|#)?\s*(\w+)",
        "en": r"(?:field|plot)\s*(?:id|#|number)?\s*(\w+)",
    },
    "severity": {
        "ar": r"(شديد|متوسط|خفيف|حاد|بسيط)",
        "en": r"(severe|moderate|mild|critical|minor)",
    },
    "growth_stage": {
        "ar": r"(إنبات|نمو|إزهار|إثمار|نضج|حصاد)",
        "en": r"(germination|vegetative|flowering|fruiting|maturity|harvest)",
    },
}


def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    كشف لغة النص المدخل.
    """
    # Check for Arabic characters
    arabic_pattern = re.compile(r"[\u0600-\u06FF]")
    arabic_count = len(arabic_pattern.findall(text))

    # Check for English characters
    english_pattern = re.compile(r"[a-zA-Z]")
    english_count = len(english_pattern.findall(text))

    if arabic_count > english_count:
        return "ar"
    elif english_count > arabic_count:
        return "en"
    else:
        return "ar"  # Default to Arabic


def extract_entities(text: str, language: str) -> dict[str, Any]:
    """
    Extract entities from text using regex patterns.
    استخراج الكيانات من النص باستخدام أنماط التعبيرات النمطية.
    """
    entities: dict[str, Any] = {}

    for entity_name, patterns in ENTITY_PATTERNS.items():
        pattern = patterns.get(language, patterns.get("en", ""))
        if pattern:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities[entity_name] = match.group(1) if match.groups() else match.group()

    return entities


def calculate_intent_score(text: str, intent_type: IntentType, language: str) -> float:
    """
    Calculate confidence score for an intent based on keyword matching.
    حساب درجة الثقة للنية بناءً على مطابقة الكلمات المفتاحية.

    Each matched keyword contributes PER_KEYWORD_WEIGHT (0.55), up to
    MAX_INTENT_SCORE (0.95). Keeping the weight flat makes scores
    interpretable regardless of how many keywords a category defines — the
    previous per-category denominator made a single strong match unreachable
    above a threshold whenever the category had many keywords, so a one-word
    irrigation query scored 0.09 while a generic "crop" match in
    YIELD_PREDICTION could out-score a specific disease query.
    """
    keywords_data = INTENT_KEYWORDS.get(intent_type, {})
    keywords = keywords_data.get(language, [])

    if not keywords:
        return 0.0

    text_lower = text.lower()
    matched_keywords = sum(1 for kw in keywords if kw in text_lower)

    if matched_keywords == 0:
        return 0.0

    return min(matched_keywords * PER_KEYWORD_WEIGHT, MAX_INTENT_SCORE)


class IntentClassifier:
    """
    Intent classifier for user queries.
    مصنف النوايا لاستفسارات المستخدم.
    """

    def __init__(self, use_llm: bool = False) -> None:
        """
        Initialize the intent classifier.

        Args:
            use_llm: Whether to use LLM for classification (optional enhancement)
        """
        self._use_llm = use_llm
        self._ollama_url = settings.ollama_url
        self._model_name = settings.intent_model_name

    async def classify(self, user_intent: UserIntent) -> IntentClassification:
        """
        Classify user intent from input.
        تصنيف نية المستخدم من الإدخال.
        """
        text = user_intent.text

        # Detect language
        language = user_intent.language
        if language == "auto":
            language = detect_language(text)

        # Calculate scores for all intents
        intent_scores: dict[IntentType, float] = {}
        for intent_type in IntentType:
            if intent_type not in (IntentType.MULTI_INTENT, IntentType.UNKNOWN):
                score = calculate_intent_score(text, intent_type, language)
                if score > 0:
                    intent_scores[intent_type] = score

        # Extract entities
        entities = extract_entities(text, language)

        # Add context from user intent
        if user_intent.field_id:
            entities["field_id"] = user_intent.field_id
        if user_intent.context:
            entities.update(user_intent.context)

        # Handle image-based queries
        if user_intent.image_base64 or user_intent.image_url:
            if IntentType.IMAGE_ANALYSIS not in intent_scores:
                intent_scores[IntentType.IMAGE_ANALYSIS] = 0.8
            else:
                intent_scores[IntentType.IMAGE_ANALYSIS] = min(intent_scores[IntentType.IMAGE_ANALYSIS] + 0.3, 0.95)

        # Determine primary intent
        if not intent_scores:
            primary_intent = IntentType.GENERAL_ADVISORY
            confidence = 0.5
        else:
            sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
            primary_intent = sorted_intents[0][0]
            confidence = sorted_intents[0][1]

            # Check for multi-intent (multiple high-scoring intents)
            high_scoring = [i for i, s in sorted_intents if s > 0.5]
            if len(high_scoring) > 2:
                primary_intent = IntentType.MULTI_INTENT

        # Get secondary intents
        secondary_intents = [
            intent_type for intent_type, score in intent_scores.items() if score > 0.3 and intent_type != primary_intent
        ][:3]  # Limit to top 3 secondary intents

        logger.info(
            "intent_classified",
            primary_intent=primary_intent.value,
            confidence=confidence,
            language=language,
            entities=list(entities.keys()),
            secondary_count=len(secondary_intents),
        )

        return IntentClassification(
            intent_type=primary_intent,
            confidence=confidence,
            entities=entities,
            secondary_intents=secondary_intents,
            language_detected=language,
            reasoning=self._generate_reasoning(primary_intent, confidence, language, entities),
        )

    def _generate_reasoning(
        self,
        intent: IntentType,
        confidence: float,
        language: str,
        entities: dict[str, Any],
    ) -> str:
        """Generate reasoning for the classification."""
        entity_list = ", ".join(entities.keys()) if entities else "none"

        if language == "ar":
            return f"تم تصنيف النية كـ {intent.value} بثقة {confidence:.0%}. الكيانات المكتشفة: {entity_list}"
        else:
            return (
                f"Intent classified as {intent.value} with {confidence:.0%} confidence. "
                f"Detected entities: {entity_list}"
            )


async def classify_intent(user_intent: UserIntent) -> IntentClassification:
    """
    Convenience function to classify intent.
    دالة مساعدة لتصنيف النية.
    """
    classifier = IntentClassifier()
    return await classifier.classify(user_intent)
