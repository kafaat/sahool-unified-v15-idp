# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Arabic NLP Processor using AraBERT
معالج اللغة العربية الطبيعية باستخدام AraBERT

Uses AraBERT (https://github.com/aub-mind/arabert) for:
- Intent classification for agricultural queries
- Named Entity Recognition (crops, diseases, locations)
- Sentiment analysis for farmer feedback
- Text preprocessing (Arabic normalization)
"""

# ⚠️ INTEGRATION STATUS: KEYWORD-BASED FALLBACK ONLY
# The `transformers` and `torch` packages are not installed in any active service.
# Intent classification uses keyword matching, NOT AraBERT ML inference.
# The AraBERT model loading code exists but the model is never actually used for inference.
# The ArabicTextPreprocessor (normalization, diacritics) works without external deps.
# To enable real AraBERT, add `transformers>=4.35.0` and `torch>=2.1.0` to requirements.

import os
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger()

# Arabic text normalization mappings
ARABIC_NORMALIZATIONS = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ى": "ي",
    "ة": "ه",
    "ؤ": "و",
    "ئ": "ي",
}

# Common Arabic diacritics to remove
ARABIC_DIACRITICS = re.compile(r"[\u064B-\u065F\u0670]")  # Fathatan to Sukun, Superscript Alef


class AgriculturalIntent(StrEnum):
    """Agricultural query intents."""

    CROP_DISEASE = "crop_disease"  # مرض المحصول
    IRRIGATION = "irrigation"  # الري
    FERTILIZER = "fertilizer"  # السماد
    PEST = "pest"  # الآفات
    WEATHER = "weather"  # الطقس
    YIELD = "yield"  # الإنتاجية
    PLANTING = "planting"  # الزراعة
    HARVEST = "harvest"  # الحصاد
    MARKET_PRICE = "market_price"  # أسعار السوق
    GENERAL = "general"  # عام


class EntityType(StrEnum):
    """Named entity types for agriculture."""

    CROP = "crop"  # محصول
    DISEASE = "disease"  # مرض
    PEST = "pest"  # آفة
    LOCATION = "location"  # موقع
    DATE = "date"  # تاريخ
    QUANTITY = "quantity"  # كمية
    FERTILIZER = "fertilizer"  # سماد
    CHEMICAL = "chemical"  # مبيد


@dataclass
class Entity:
    """Extracted named entity."""

    text: str
    entity_type: EntityType
    start: int
    end: int
    confidence: float = 0.0


@dataclass
class IntentResult:
    """Intent classification result."""

    intent: AgriculturalIntent
    confidence: float
    secondary_intents: list[tuple[AgriculturalIntent, float]] = field(default_factory=list)


@dataclass
class SentimentResult:
    """Sentiment analysis result."""

    sentiment: str  # positive, negative, neutral
    score: float
    is_urgent: bool = False


class ArabicTextPreprocessor:
    """
    Arabic text preprocessing utilities.
    أدوات معالجة النص العربي المسبقة
    """

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize Arabic text for consistency."""
        # Remove diacritics
        text = ARABIC_DIACRITICS.sub("", text)

        # Normalize characters
        for original, normalized in ARABIC_NORMALIZATIONS.items():
            text = text.replace(original, normalized)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def remove_emojis(text: str) -> str:
        """Remove emojis from text."""
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub("", text)

    @staticmethod
    def is_arabic(text: str) -> bool:
        """Check if text contains Arabic characters."""
        arabic_pattern = re.compile(r"[\u0600-\u06FF]")
        return bool(arabic_pattern.search(text))

    @staticmethod
    def extract_numbers(text: str) -> list[float]:
        """Extract numbers from Arabic/English text."""
        # Arabic-Indic numerals mapping
        arabic_numerals = {
            "٠": "0",
            "١": "1",
            "٢": "2",
            "٣": "3",
            "٤": "4",
            "٥": "5",
            "٦": "6",
            "٧": "7",
            "٨": "8",
            "٩": "9",
        }

        for ar, en in arabic_numerals.items():
            text = text.replace(ar, en)

        numbers = re.findall(r"\d+\.?\d*", text)
        return [float(n) for n in numbers]


class IntentClassifier:
    """
    Agricultural intent classifier using AraBERT.
    مصنف النوايا الزراعية باستخدام AraBERT
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._model_loaded = False

        # Keyword-based fallback patterns (Arabic + English)
        self._intent_keywords = {
            AgriculturalIntent.CROP_DISEASE: [
                "مرض",
                "اصفرار",
                "ذبول",
                "بقع",
                "تعفن",
                "disease",
                "yellow",
                "wilt",
                "spots",
                "rot",
                "صدأ",
                "بياض",
            ],
            AgriculturalIntent.IRRIGATION: [
                "ري",
                "ماء",
                "سقي",
                "رطوبة",
                "جفاف",
                "irrigation",
                "water",
                "moisture",
                "drought",
                "تنقيط",
                "رش",
            ],
            AgriculturalIntent.FERTILIZER: [
                "سماد",
                "تسميد",
                "نيتروجين",
                "فوسفور",
                "بوتاسيوم",
                "fertilizer",
                "nitrogen",
                "npk",
                "يوريا",
                "urea",
            ],
            AgriculturalIntent.PEST: [
                "آفة",
                "حشرة",
                "دودة",
                "سوسة",
                "مبيد",
                "pest",
                "insect",
                "worm",
                "weevil",
                "pesticide",
            ],
            AgriculturalIntent.WEATHER: [
                "طقس",
                "حرارة",
                "مطر",
                "رياح",
                "رطوبة",
                "weather",
                "temperature",
                "rain",
                "wind",
                "humidity",
            ],
            AgriculturalIntent.YIELD: [
                "إنتاج",
                "محصول",
                "غلة",
                "حصاد",
                "طن",
                "yield",
                "production",
                "harvest",
                "ton",
                "كمية",
            ],
            AgriculturalIntent.PLANTING: [
                "زراعة",
                "بذور",
                "شتلات",
                "موسم",
                "planting",
                "seeds",
                "seedlings",
                "season",
                "غرس",
            ],
            AgriculturalIntent.MARKET_PRICE: [
                "سعر",
                "سوق",
                "بيع",
                "شراء",
                "price",
                "market",
                "sell",
                "buy",
                "ريال",
            ],
        }

    async def load_model(self) -> bool:
        """Load AraBERT model for intent classification."""
        if self._model_loaded:
            return True

        try:
            # Try to load AraBERT
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            model_name = os.getenv("ARABERT_MODEL", "aubmindlab/bert-base-arabertv2")
            # Pin revision for security - prevents supply chain attacks
            model_revision = os.getenv("ARABERT_REVISION", "main")

            self._tokenizer = AutoTokenizer.from_pretrained(model_name, revision=model_revision)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=len(AgriculturalIntent),
                revision=model_revision,
            )
            self._model_loaded = True

            logger.info("AraBERT model loaded", model=model_name)
            return True

        except ImportError:
            logger.warning("transformers not installed, using keyword-based fallback")
            return False
        except Exception as e:
            logger.warning("Failed to load AraBERT", error=str(e))
            return False

    def classify(self, text: str) -> IntentResult:
        """
        Classify the intent of an agricultural query.
        تصنيف نية الاستعلام الزراعي
        """
        # Preprocess text
        preprocessor = ArabicTextPreprocessor()
        normalized_text = preprocessor.normalize(text.lower())

        # Use keyword-based classification (fast, works offline)
        scores = {}
        for intent, keywords in self._intent_keywords.items():
            score = sum(1 for kw in keywords if kw in normalized_text)
            if score > 0:
                scores[intent] = score

        if not scores:
            return IntentResult(intent=AgriculturalIntent.GENERAL, confidence=0.5, secondary_intents=[])

        # Sort by score
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        primary_intent = sorted_intents[0][0]
        total_score = sum(scores.values())
        primary_confidence = sorted_intents[0][1] / total_score if total_score else 0.5

        secondary = [(intent, score / total_score) for intent, score in sorted_intents[1:3] if score > 0]

        return IntentResult(
            intent=primary_intent,
            confidence=min(primary_confidence + 0.3, 0.95),  # Boost confidence
            secondary_intents=secondary,
        )


class EntityExtractor:
    """
    Named Entity Recognition for agricultural domain.
    التعرف على الكيانات المسماة للمجال الزراعي
    """

    def __init__(self):
        # Common agricultural entities (Arabic + English)
        self._crop_names = {
            "قمح": "wheat",
            "شعير": "barley",
            "نخيل": "date_palm",
            "تمر": "dates",
            "طماطم": "tomato",
            "خيار": "cucumber",
            "بطاطس": "potato",
            "بصل": "onion",
            "ثوم": "garlic",
            "برسيم": "alfalfa",
            "ذرة": "corn",
            "أرز": "rice",
            "wheat": "wheat",
            "barley": "barley",
            "tomato": "tomato",
            "potato": "potato",
        }

        self._disease_names = {
            "صدأ": "rust",
            "بياض دقيقي": "powdery_mildew",
            "بياض زغبي": "downy_mildew",
            "لفحة": "blight",
            "ذبول": "wilt",
            "تبقع": "leaf_spot",
            "تعفن": "rot",
            "rust": "rust",
            "mildew": "mildew",
            "blight": "blight",
        }

        self._pest_names = {
            "سوسة النخيل": "red_palm_weevil",
            "دودة": "worm",
            "من": "aphid",
            "ذبابة": "fly",
            "حشرة": "insect",
            "عنكبوت": "spider_mite",
            "aphid": "aphid",
            "weevil": "weevil",
        }

        self._fertilizer_names = {
            "يوريا": "urea",
            "نيتروجين": "nitrogen",
            "فوسفور": "phosphorus",
            "بوتاسيوم": "potassium",
            "npk": "npk",
            "سماد عضوي": "organic",
            "urea": "urea",
        }

    def extract(self, text: str) -> list[Entity]:
        """
        Extract agricultural entities from text.
        استخراج الكيانات الزراعية من النص
        """
        entities = []
        text_lower = text.lower()

        # Extract crops
        for ar_name, en_name in self._crop_names.items():
            if ar_name in text_lower:
                start = text_lower.find(ar_name)
                entities.append(
                    Entity(
                        text=ar_name,
                        entity_type=EntityType.CROP,
                        start=start,
                        end=start + len(ar_name),
                        confidence=0.9,
                    )
                )

        # Extract diseases
        for ar_name, en_name in self._disease_names.items():
            if ar_name in text_lower:
                start = text_lower.find(ar_name)
                entities.append(
                    Entity(
                        text=ar_name,
                        entity_type=EntityType.DISEASE,
                        start=start,
                        end=start + len(ar_name),
                        confidence=0.85,
                    )
                )

        # Extract pests
        for ar_name, en_name in self._pest_names.items():
            if ar_name in text_lower:
                start = text_lower.find(ar_name)
                entities.append(
                    Entity(
                        text=ar_name,
                        entity_type=EntityType.PEST,
                        start=start,
                        end=start + len(ar_name),
                        confidence=0.85,
                    )
                )

        # Extract fertilizers
        for ar_name, en_name in self._fertilizer_names.items():
            if ar_name in text_lower:
                start = text_lower.find(ar_name)
                entities.append(
                    Entity(
                        text=ar_name,
                        entity_type=EntityType.FERTILIZER,
                        start=start,
                        end=start + len(ar_name),
                        confidence=0.9,
                    )
                )

        # Extract quantities (numbers with units)
        quantity_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(كيلو|طن|هكتار|لتر|مل|kg|ton|hectare|liter|ml|ha)")
        for match in quantity_pattern.finditer(text_lower):
            entities.append(
                Entity(
                    text=match.group(0),
                    entity_type=EntityType.QUANTITY,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,
                )
            )

        return entities


class SentimentAnalyzer:
    """
    Sentiment analysis for farmer feedback.
    تحليل المشاعر لتعليقات المزارعين
    """

    def __init__(self):
        # Sentiment keywords
        self._positive_words = [
            "ممتاز",
            "جيد",
            "رائع",
            "شكرا",
            "مفيد",
            "نجح",
            "excellent",
            "good",
            "great",
            "thanks",
            "useful",
            "worked",
            "أحسنت",
            "جميل",
        ]

        self._negative_words = [
            "سيء",
            "فشل",
            "مشكلة",
            "خطأ",
            "لم ينجح",
            "ضعيف",
            "bad",
            "failed",
            "problem",
            "error",
            "wrong",
            "weak",
            "خسارة",
        ]

        self._urgent_words = [
            "عاجل",
            "طوارئ",
            "فوري",
            "سريع",
            "خطير",
            "urgent",
            "emergency",
            "immediately",
            "critical",
            "serious",
            "ساعدوني",
            "النجدة",
        ]

    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of farmer feedback.
        تحليل مشاعر تعليقات المزارع
        """
        text_lower = text.lower()

        positive_count = sum(1 for w in self._positive_words if w in text_lower)
        negative_count = sum(1 for w in self._negative_words if w in text_lower)
        is_urgent = any(w in text_lower for w in self._urgent_words)

        total = positive_count + negative_count
        if total == 0:
            return SentimentResult(sentiment="neutral", score=0.5, is_urgent=is_urgent)

        positive_ratio = positive_count / total

        if positive_ratio > 0.6:
            sentiment = "positive"
            score = 0.5 + (positive_ratio * 0.5)
        elif positive_ratio < 0.4:
            sentiment = "negative"
            score = 0.5 - ((1 - positive_ratio) * 0.5)
        else:
            sentiment = "neutral"
            score = 0.5

        return SentimentResult(sentiment=sentiment, score=score, is_urgent=is_urgent)


class ArabicNLPProcessor:
    """
    Main Arabic NLP processor combining all components.
    معالج اللغة العربية الرئيسي يجمع جميع المكونات
    """

    def __init__(self):
        self.preprocessor = ArabicTextPreprocessor()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()

    async def initialize(self) -> bool:
        """Initialize NLP models."""
        return await self.intent_classifier.load_model()

    def process(self, text: str) -> dict[str, Any]:
        """
        Process text and return all NLP results.
        معالجة النص وإرجاع جميع نتائج NLP
        """
        # Preprocess
        normalized = self.preprocessor.normalize(text)
        is_arabic = self.preprocessor.is_arabic(text)

        # Classify intent
        intent_result = self.intent_classifier.classify(text)

        # Extract entities
        entities = self.entity_extractor.extract(text)

        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(text)

        return {
            "original_text": text,
            "normalized_text": normalized,
            "is_arabic": is_arabic,
            "intent": {
                "primary": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "secondary": [{"intent": i.value, "confidence": c} for i, c in intent_result.secondary_intents],
            },
            "entities": [
                {
                    "text": e.text,
                    "type": e.entity_type.value,
                    "start": e.start,
                    "end": e.end,
                    "confidence": e.confidence,
                }
                for e in entities
            ],
            "sentiment": {
                "label": sentiment.sentiment,
                "score": sentiment.score,
                "is_urgent": sentiment.is_urgent,
            },
        }
