"""
Tests for Knowledge Content Preprocessors
===========================================
اختبارات المعالجات المسبقة للمحتوى المعرفي

Tests for Arabic text normalization, agricultural term normalization,
and metadata enrichment.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.ingestion.preprocessors import (
    AgriculturalTermNormalizer,
    ArabicTextPreprocessor,
    MetadataEnricher,
)
from shared.ai.knowledge.models import KnowledgeDomain


@pytest.fixture
def arabic_preprocessor() -> ArabicTextPreprocessor:
    """Create an ArabicTextPreprocessor instance."""
    return ArabicTextPreprocessor()


@pytest.fixture
def term_normalizer() -> AgriculturalTermNormalizer:
    """Create an AgriculturalTermNormalizer instance."""
    return AgriculturalTermNormalizer()


@pytest.fixture
def metadata_enricher() -> MetadataEnricher:
    """Create a MetadataEnricher instance."""
    return MetadataEnricher()


# ─── Arabic Text Preprocessor Tests ──────────────────────────────────────────


class TestArabicTextPreprocessor:
    """Tests for Arabic text normalization | اختبارات تطبيع النص العربي"""

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_remove_diacritics(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test diacritics (tashkeel) removal | اختبار إزالة التشكيل"""
        text = "القَمْحُ يَحْتَاجُ"
        result = arabic_preprocessor.normalize(text)
        assert "َ" not in result
        assert "ْ" not in result
        assert "ُ" not in result

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_remove_tatweel(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test tatweel (kashida) removal | اختبار إزالة التطويل"""
        text = "الـقـمـح"
        result = arabic_preprocessor.normalize(text)
        assert "\u0640" not in result

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_normalize_alef_variants(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test alef variant normalization | اختبار توحيد أشكال الألف"""
        text = "إسلام أحمد آخر"
        result = arabic_preprocessor.normalize(text)
        assert "إ" not in result
        assert "أ" not in result
        assert "آ" not in result
        assert "ا" in result

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_normalize_taa_marbuta(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test taa marbuta normalization | اختبار توحيد التاء المربوطة"""
        text = "الزراعة"
        result = arabic_preprocessor.normalize(text)
        assert result == "الزراعه"

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_normalize_alef_maqsura(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test alef maqsura normalization | اختبار توحيد الألف المقصورة"""
        text = "مستوى"
        result = arabic_preprocessor.normalize(text)
        assert result == "مستوي"

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_normalize_whitespace(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test whitespace normalization."""
        text = "القمح    يحتاج    ماء"
        result = arabic_preprocessor.normalize(text)
        assert "  " not in result

    @pytest.mark.unit
    def test_empty_text(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test empty text returns empty string."""
        assert arabic_preprocessor.normalize("") == ""

    @pytest.mark.unit
    def test_english_text_unchanged(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test English text passes through unchanged."""
        text = "Wheat irrigation guide"
        result = arabic_preprocessor.normalize(text)
        assert result == text

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_is_arabic_true(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test detection of Arabic text."""
        assert arabic_preprocessor.is_arabic("القمح يحتاج ماء") is True

    @pytest.mark.unit
    def test_is_arabic_false_for_english(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test English text is not detected as Arabic."""
        assert arabic_preprocessor.is_arabic("Wheat needs water") is False

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_is_arabic_mixed_text(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test mixed text with more Arabic."""
        # More than 50% Arabic chars → True
        assert arabic_preprocessor.is_arabic("القمح wheat القمح") is True
        # More English → False
        assert arabic_preprocessor.is_arabic("wheat القمح barley rice") is False

    @pytest.mark.unit
    def test_is_arabic_empty(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test empty text returns False."""
        assert arabic_preprocessor.is_arabic("") is False

    @pytest.mark.unit
    def test_is_arabic_numbers_only(self, arabic_preprocessor: ArabicTextPreprocessor):
        """Test numbers only returns False."""
        assert arabic_preprocessor.is_arabic("12345") is False


# ─── Agricultural Term Normalizer Tests ──────────────────────────────────────


class TestAgriculturalTermNormalizer:
    """Tests for agricultural term normalization."""

    @pytest.mark.unit
    def test_normalize_ndvi(self, term_normalizer: AgriculturalTermNormalizer):
        """Test NDVI term normalization."""
        text = "Use ndvi to monitor crop health"
        result = term_normalizer.normalize_terms(text)
        assert "NDVI" in result

    @pytest.mark.unit
    def test_normalize_lai(self, term_normalizer: AgriculturalTermNormalizer):
        """Test LAI term normalization."""
        text = "Calculate lai for canopy analysis"
        result = term_normalizer.normalize_terms(text)
        assert "LAI" in result

    @pytest.mark.unit
    def test_normalize_irrigation_terms(self, term_normalizer: AgriculturalTermNormalizer):
        """Test irrigation term normalization."""
        text = "Use drip for vegetables"
        result = term_normalizer.normalize_terms(text)
        assert "drip irrigation" in result

    @pytest.mark.unit
    def test_normalize_rpw(self, term_normalizer: AgriculturalTermNormalizer):
        """Test red palm weevil abbreviation."""
        text = "Check for rpw infestation"
        result = term_normalizer.normalize_terms(text)
        assert "red palm weevil" in result

    @pytest.mark.unit
    def test_normalize_et(self, term_normalizer: AgriculturalTermNormalizer):
        """Test ET abbreviation."""
        text = "Calculate et for scheduling"
        result = term_normalizer.normalize_terms(text)
        assert "evapotranspiration" in result

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_normalize_arabic_irrigation(self, term_normalizer: AgriculturalTermNormalizer):
        """Test Arabic irrigation term normalization."""
        text = "استخدم ري بالتنقيط"
        result = term_normalizer.normalize_terms(text)
        assert "ري تنقيط" in result

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_normalize_arabic_rpw(self, term_normalizer: AgriculturalTermNormalizer):
        """Test Arabic red palm weevil normalization."""
        text = "كشف سوسة حمراء"
        result = term_normalizer.normalize_terms(text)
        assert "سوسة النخيل الحمراء" in result

    @pytest.mark.unit
    def test_case_insensitive(self, term_normalizer: AgriculturalTermNormalizer):
        """Test case-insensitive English normalization."""
        text = "Use NPK fertilizer"
        result = term_normalizer.normalize_terms(text)
        assert "NPK compound fertilizer" in result

    @pytest.mark.unit
    def test_no_match_unchanged(self, term_normalizer: AgriculturalTermNormalizer):
        """Test text without terms passes through unchanged."""
        text = "The weather is nice today."
        result = term_normalizer.normalize_terms(text)
        assert result == text


# ─── Metadata Enricher Tests ────────────────────────────────────────────────


class TestMetadataEnricher:
    """Tests for automatic metadata enrichment."""

    @pytest.mark.unit
    def test_detect_crop_domain(self, metadata_enricher: MetadataEnricher):
        """Test crop domain detection."""
        text = "Wheat is a major crop with specific growth stages and varieties."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.CROPS in domains

    @pytest.mark.unit
    def test_detect_irrigation_domain(self, metadata_enricher: MetadataEnricher):
        """Test irrigation domain detection."""
        text = "Drip irrigation provides efficient water delivery with moisture control."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.IRRIGATION in domains

    @pytest.mark.unit
    def test_detect_soil_domain(self, metadata_enricher: MetadataEnricher):
        """Test soil domain detection."""
        text = "Sandy soil with low organic matter and high pH requires amendments."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.SOIL in domains

    @pytest.mark.unit
    def test_detect_fertilizer_domain(self, metadata_enricher: MetadataEnricher):
        """Test fertilizer domain detection."""
        text = "Apply urea fertilizer with nitrogen and NPK for potassium."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.FERTILIZER in domains

    @pytest.mark.unit
    def test_detect_pest_domain(self, metadata_enricher: MetadataEnricher):
        """Test pest/disease domain detection."""
        text = "Wheat rust disease and insect pest management with fungicide."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.PEST_DISEASE in domains

    @pytest.mark.unit
    def test_detect_weather_domain(self, metadata_enricher: MetadataEnricher):
        """Test weather domain detection."""
        text = "Climate change affects rainfall patterns and temperature increases drought risk."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.WEATHER in domains

    @pytest.mark.unit
    def test_detect_remote_sensing_domain(self, metadata_enricher: MetadataEnricher):
        """Test remote sensing domain detection."""
        text = "Use Sentinel-2 satellite NDVI and LAI for crop monitoring."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.REMOTE_SENSING in domains

    @pytest.mark.unit
    def test_detect_smart_agriculture_domain(self, metadata_enricher: MetadataEnricher):
        """Test smart agriculture domain detection."""
        text = "IoT sensors and blockchain enable smart farming with edge computing drones."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.SMART_AGRICULTURE in domains

    @pytest.mark.unit
    def test_detect_precision_farming_domain(self, metadata_enricher: MetadataEnricher):
        """Test precision farming domain detection | كشف مجال الزراعة الدقيقة"""
        text = "Variable rate application using GPS and RTK guidance for yield map analysis."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.PRECISION_FARMING in domains

    @pytest.mark.unit
    def test_detect_digital_twin_domain(self, metadata_enricher: MetadataEnricher):
        """Test digital twin domain detection | كشف مجال التوأم الرقمي"""
        text = "Digital twin simulation creates a virtual model for farm cyber-physical system."
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.DIGITAL_TWIN in domains

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_detect_arabic_domain(self, metadata_enricher: MetadataEnricher):
        """Test domain detection from Arabic text | كشف المجال من النص العربي"""
        text = "محصول القمح يحتاج إلى ري وبذور ومراحل نمو محددة"
        domains = metadata_enricher.detect_domains(text)
        assert KnowledgeDomain.CROPS in domains

    @pytest.mark.unit
    def test_detect_multiple_domains(self, metadata_enricher: MetadataEnricher):
        """Test detecting multiple domains from rich text."""
        text = "Irrigation water management for crop growth in sandy soil."
        domains = metadata_enricher.detect_domains(text)
        assert len(domains) >= 2

    @pytest.mark.unit
    def test_detect_no_domains(self, metadata_enricher: MetadataEnricher):
        """Test text with no agricultural content returns empty."""
        text = "The quick brown fox jumps over the lazy dog."
        domains = metadata_enricher.detect_domains(text)
        assert len(domains) == 0

    # ─── Tag Extraction ──────────────────────────────────────────────────

    @pytest.mark.unit
    def test_extract_tags_from_metadata(self, metadata_enricher: MetadataEnricher):
        """Test tag extraction from frontmatter metadata."""
        metadata = {"tags": ["wheat", "irrigation"], "category": "crops"}
        tags = metadata_enricher.extract_tags("Some text about wheat", metadata)
        assert "wheat" in tags
        assert "irrigation" in tags
        assert "crops" in tags

    @pytest.mark.unit
    def test_extract_tags_from_comma_string(self, metadata_enricher: MetadataEnricher):
        """Test tag extraction from comma-separated string."""
        metadata = {"tags": "wheat, barley, corn"}
        tags = metadata_enricher.extract_tags("About grains", metadata)
        assert "wheat" in tags

    @pytest.mark.unit
    def test_extract_crop_tags(self, metadata_enricher: MetadataEnricher):
        """Test crop name detection in tags."""
        text = "This guide covers wheat and barley cultivation."
        tags = metadata_enricher.extract_tags(text)
        assert "crop:wheat" in tags
        assert "crop:barley" in tags

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_extract_arabic_crop_tags(self, metadata_enricher: MetadataEnricher):
        """Test Arabic crop name detection | كشف أسماء المحاصيل العربية"""
        text = "زراعة القمح والشعير والتمور"
        tags = metadata_enricher.extract_tags(text)
        assert "crop:wheat" in tags or "crop:barley" in tags

    @pytest.mark.unit
    def test_tags_deduplicated(self, metadata_enricher: MetadataEnricher):
        """Test tags are deduplicated."""
        metadata = {"tags": ["wheat", "wheat"], "category": "crops"}
        tags = metadata_enricher.extract_tags("About wheat crops", metadata)
        # No duplicates
        assert len(tags) == len(set(tags))

    # ─── Region Detection ────────────────────────────────────────────────

    @pytest.mark.unit
    def test_detect_yemen_region(self, metadata_enricher: MetadataEnricher):
        """Test Yemen region detection."""
        text = "Farming practices in Yemen, especially in Sana'a"
        regions = metadata_enricher.detect_regions(text)
        assert "yemen" in regions

    @pytest.mark.unit
    def test_detect_saudi_region(self, metadata_enricher: MetadataEnricher):
        """Test Saudi Arabia region detection."""
        text = "Agricultural development in Saudi Arabia"
        regions = metadata_enricher.detect_regions(text)
        assert "saudi_arabia" in regions

    @pytest.mark.unit
    @pytest.mark.arabic
    def test_detect_arabic_region(self, metadata_enricher: MetadataEnricher):
        """Test region detection from Arabic text."""
        text = "الزراعة في اليمن وخاصة في تهامة وحضرموت"
        regions = metadata_enricher.detect_regions(text)
        assert "yemen" in regions

    @pytest.mark.unit
    def test_detect_multiple_regions(self, metadata_enricher: MetadataEnricher):
        """Test detecting multiple regions."""
        text = "Agriculture in Yemen, Saudi Arabia, and the GCC countries"
        regions = metadata_enricher.detect_regions(text)
        assert "yemen" in regions
        assert "saudi_arabia" in regions
        assert "gcc" in regions

    @pytest.mark.unit
    def test_detect_mena_region(self, metadata_enricher: MetadataEnricher):
        """Test MENA region detection."""
        text = "Farming in the Middle East region."
        regions = metadata_enricher.detect_regions(text)
        assert "mena" in regions

    @pytest.mark.unit
    def test_detect_no_regions(self, metadata_enricher: MetadataEnricher):
        """Test text with no region mentions."""
        text = "General principles of photosynthesis."
        regions = metadata_enricher.detect_regions(text)
        assert len(regions) == 0
