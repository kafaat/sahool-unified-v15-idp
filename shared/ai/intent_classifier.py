"""
Unified Agricultural Intent Classifier
مصنّف النوايا الزراعية الموحد

Used by: copilot-api, whatsapp-bot, ussd-gateway, wechat-service
Phase 1 of Component Unification Plan (PR #1344)
"""

import re
from dataclasses import dataclass, field
from enum import StrEnum


class AgriIntent(StrEnum):
    CROP_DISEASE = "crop_disease"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PEST_DETECTION = "pest_detection"
    WEATHER = "weather"
    MARKET_PRICE = "market_price"
    POLICY_QUERY = "policy_query"
    NDVI_ANALYSIS = "ndvi_analysis"
    GENERAL_ADVISORY = "general_advisory"
    GREETING = "greeting"
    HELP = "help"


# Service ports mirror from packages/shared-types/src/contracts/service-ports.ts
# IMPORTANT: Keep in sync with TypeScript contract SERVICE_PORTS.
INTENT_SERVICE_MAP = {
    AgriIntent.CROP_DISEASE: {
        "service": "pest-detection-service",
        "port": 8125,
        "fallback": "yolo26-vision-service",
        "fallback_port": 8150,
    },
    AgriIntent.IRRIGATION: {"service": "irrigation-smart", "port": 8094},
    AgriIntent.FERTILIZER: {"service": "advisory-service", "port": 8093},
    AgriIntent.PEST_DETECTION: {"service": "pest-detection-service", "port": 8125},
    AgriIntent.WEATHER: {"service": "weather-service", "port": 8092},
    AgriIntent.MARKET_PRICE: {"service": "marketplace-service", "port": 3010},
    AgriIntent.NDVI_ANALYSIS: {"service": "vegetation-analysis-service", "port": 8090},
    AgriIntent.GENERAL_ADVISORY: {"service": "copilot-api", "port": 8088},
}


@dataclass
class IntentResult:
    intent: AgriIntent
    confidence: float  # 0.0 - 1.0
    method: str  # "pattern" | "llm" | "vision"
    language: str  # "ar" | "en"
    entities: dict = field(default_factory=dict)  # extracted entities like crop_type, field_id


class AgriIntentClassifier:
    """Unified intent classifier for all SAHOOL farmer-facing channels.

    Provides fast offline pattern matching (<1ms) with optional LLM fallback.
    Supports Arabic and English with bilingual entity extraction.

    Consolidates duplicate intent detection from:
    - whatsapp-bot-service/src/handlers/message_handler.py
    - copilot-api intent routing
    - ussd-gateway menu mapping
    - wechat-service message classification
    """

    # Arabic patterns for each intent (fast, offline, <1ms)
    ARABIC_PATTERNS = {
        AgriIntent.CROP_DISEASE: [r"مرض", r"اصفرار", r"ذبول", r"بقع", r"آفة.*ورق", r"تعفن"],
        AgriIntent.IRRIGATION: [r"ري", r"سقي", r"ماء", r"عطش", r"جفاف", r"رطوبة"],
        AgriIntent.FERTILIZER: [r"سماد", r"تسميد", r"يوريا", r"نيتروجين", r"فوسف", r"بوتاس"],
        AgriIntent.PEST_DETECTION: [r"حشر", r"دود", r"من\b", r"جراد", r"سوسة", r"آفة"],
        AgriIntent.WEATHER: [r"طقس", r"حرارة", r"مطر", r"رياح", r"رطوبة.*جو", r"صقيع"],
        AgriIntent.MARKET_PRICE: [r"سعر", r"سوق", r"بيع", r"شراء", r"تسويق"],
        AgriIntent.NDVI_ANALYSIS: [r"ndvi", r"قمر.*صناعي", r"صور.*فضائ", r"غطاء.*نبات"],
        AgriIntent.GREETING: [r"سلام", r"مرحب", r"أهل", r"صباح", r"مساء"],
        AgriIntent.HELP: [r"مساعد", r"كيف", r"شرح", r"ساعد"],
    }

    # English patterns
    ENGLISH_PATTERNS = {
        AgriIntent.CROP_DISEASE: [r"disease", r"yellow", r"wilt", r"spots", r"blight", r"rust"],
        AgriIntent.IRRIGATION: [r"irrig", r"water", r"drought", r"moisture", r"dry"],
        AgriIntent.FERTILIZER: [r"fertil", r"urea", r"nitrogen", r"phosph", r"potass", r"nutrient"],
        AgriIntent.PEST_DETECTION: [r"pest", r"insect", r"worm", r"aphid", r"locust", r"weevil"],
        AgriIntent.WEATHER: [r"weather", r"temp", r"rain", r"wind", r"frost", r"forecast"],
        AgriIntent.MARKET_PRICE: [r"price", r"market", r"sell", r"buy", r"cost"],
        AgriIntent.NDVI_ANALYSIS: [r"ndvi", r"satellite", r"vegetation", r"remote.sens"],
        AgriIntent.GREETING: [r"hello", r"hi\b", r"good morning", r"good evening"],
        AgriIntent.HELP: [r"help", r"how to", r"explain", r"guide"],
    }

    def detect_language(self, text: str) -> str:
        """Detect whether text is Arabic or English based on character ratio."""
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
        return "ar" if arabic_chars / max(len(text), 1) > 0.3 else "en"

    async def classify(self, text: str, image: bytes | None = None) -> IntentResult:
        """Classify farmer query into an agricultural intent.

        Uses a tiered approach:
        1. Fast pattern matching (offline, <1ms)
        2. Fallback to general advisory if no confident match

        Args:
            text: The farmer's query text (Arabic or English).
            image: Optional image bytes for vision-based classification.

        Returns:
            IntentResult with intent, confidence, method, and language.
        """
        lang = self.detect_language(text)

        # 1. Fast pattern matching (offline, <1ms)
        result = self._classify_by_pattern(text, lang)
        if result and result.confidence >= 0.7:
            return result

        # 2. Fallback to general advisory
        return IntentResult(
            intent=AgriIntent.GENERAL_ADVISORY,
            confidence=0.5,
            method="fallback",
            language=lang,
        )

    def _classify_by_pattern(self, text: str, lang: str) -> IntentResult | None:
        """Classify text using regex pattern matching.

        Args:
            text: Input text to classify.
            lang: Detected language ("ar" or "en").

        Returns:
            IntentResult if any pattern matches, None otherwise.
        """
        patterns = self.ARABIC_PATTERNS if lang == "ar" else self.ENGLISH_PATTERNS
        text_lower = text.lower()

        best_intent = None
        best_score = 0

        for intent, pattern_list in patterns.items():
            matches = sum(1 for p in pattern_list if re.search(p, text_lower))
            score = matches / len(pattern_list)
            if score > best_score:
                best_score = score
                best_intent = intent

        if best_intent and best_score > 0:
            return IntentResult(
                intent=best_intent,
                confidence=min(best_score * 2, 1.0),
                method="pattern",
                language=lang,
            )
        return None
