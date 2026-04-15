"""
Unit tests for AgriIntentClassifier
اختبارات وحدة لمصنّف النوايا الزراعية

Tests the Phase 1 core component of Component Unification Plan (PR #1344)
"""
import pytest
from shared.ai.intent_classifier import AgriIntentClassifier, AgriIntent

pytestmark = pytest.mark.unit

@pytest.fixture
def classifier():
    return AgriIntentClassifier()

class TestLanguageDetection:
    def test_arabic_text(self, classifier):
        assert classifier.detect_language("القمح يعاني من اصفرار الأوراق") == "ar"

    def test_english_text(self, classifier):
        assert classifier.detect_language("My wheat has yellow leaves") == "en"

    def test_mixed_text_mostly_arabic(self, classifier):
        assert classifier.detect_language("القمح NDVI منخفض") == "ar"

    def test_empty_text(self, classifier):
        assert classifier.detect_language("") == "en"

class TestArabicIntentClassification:
    @pytest.mark.asyncio
    async def test_crop_disease_arabic(self, classifier):
        result = await classifier.classify("القمح يعاني من اصفرار وبقع على الأوراق")
        assert result.intent == AgriIntent.CROP_DISEASE
        assert result.language == "ar"
        assert result.confidence > 0.5

    @pytest.mark.asyncio
    async def test_irrigation_arabic(self, classifier):
        result = await classifier.classify("متى أسقي القمح؟ التربة جافة")
        assert result.intent == AgriIntent.IRRIGATION
        assert result.language == "ar"

    @pytest.mark.asyncio
    async def test_fertilizer_arabic(self, classifier):
        result = await classifier.classify("كم كمية سماد اليوريا للقمح؟")
        assert result.intent == AgriIntent.FERTILIZER

    @pytest.mark.asyncio
    async def test_pest_arabic(self, classifier):
        result = await classifier.classify("وجدت حشرات وديدان في المحصول")
        assert result.intent == AgriIntent.PEST_DETECTION

    @pytest.mark.asyncio
    async def test_weather_arabic(self, classifier):
        result = await classifier.classify("ما توقعات الطقس والمطر هذا الأسبوع؟")
        assert result.intent == AgriIntent.WEATHER

    @pytest.mark.asyncio
    async def test_market_arabic(self, classifier):
        result = await classifier.classify("ما سعر القمح في السوق اليوم؟")
        assert result.intent == AgriIntent.MARKET_PRICE

    @pytest.mark.asyncio
    async def test_ndvi_arabic(self, classifier):
        result = await classifier.classify("أريد صور القمر الصناعي لحقلي")
        assert result.intent == AgriIntent.NDVI_ANALYSIS

    @pytest.mark.asyncio
    async def test_greeting_arabic(self, classifier):
        result = await classifier.classify("السلام عليكم")
        assert result.intent == AgriIntent.GREETING

class TestEnglishIntentClassification:
    @pytest.mark.asyncio
    async def test_crop_disease_english(self, classifier):
        result = await classifier.classify("My wheat has yellow spots and wilt")
        assert result.intent == AgriIntent.CROP_DISEASE
        assert result.language == "en"

    @pytest.mark.asyncio
    async def test_irrigation_english(self, classifier):
        result = await classifier.classify("When should I water my field? Soil is dry")
        assert result.intent == AgriIntent.IRRIGATION

    @pytest.mark.asyncio
    async def test_weather_english(self, classifier):
        result = await classifier.classify("What is the weather forecast for tomorrow?")
        assert result.intent == AgriIntent.WEATHER

class TestFallback:
    @pytest.mark.asyncio
    async def test_unknown_query_falls_back(self, classifier):
        result = await classifier.classify("random text that matches nothing specific")
        assert result.intent == AgriIntent.GENERAL_ADVISORY
        assert result.confidence <= 0.5

class TestIntentServiceMap:
    def test_all_intents_have_services(self):
        from shared.ai.intent_classifier import INTENT_SERVICE_MAP
        for intent in [AgriIntent.CROP_DISEASE, AgriIntent.IRRIGATION, AgriIntent.WEATHER, AgriIntent.PEST_DETECTION]:
            assert intent in INTENT_SERVICE_MAP
            assert "service" in INTENT_SERVICE_MAP[intent]
            assert "port" in INTENT_SERVICE_MAP[intent]
