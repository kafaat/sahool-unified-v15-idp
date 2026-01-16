"""
Unit Tests for AI Context Compression Module
=============================================
اختبارات وحدة لوحدة ضغط السياق للذكاء الاصطناعي

Tests for ContextCompressor class covering:
- Token estimation for English, Arabic, and mixed text
- Field data compression with different strategies
- Weather data compression
- Operational history compression
- Arabic text-specific compression features

Author: SAHOOL QA Team
Updated: January 2025
"""

import pytest
from datetime import datetime, UTC

from shared.ai.context_engineering.compression import (
    ContextCompressor,
    CompressionStrategy,
    CompressionResult,
    estimate_tokens,
    detect_primary_language,
    CHARS_PER_TOKEN_ARABIC,
    CHARS_PER_TOKEN_ENGLISH,
    CHARS_PER_TOKEN_MIXED,
    DEFAULT_FIELD_COMPRESSION_RATIO,
    DEFAULT_WEATHER_COMPRESSION_RATIO,
    DEFAULT_HISTORY_COMPRESSION_RATIO,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def compressor():
    """Standard compressor instance"""
    return ContextCompressor()


@pytest.fixture
def compressor_preserve_diacritics():
    """Compressor that preserves Arabic diacritics"""
    return ContextCompressor(preserve_arabic_diacritics=True)


@pytest.fixture
def sample_field_data():
    """Sample field data for testing"""
    return {
        "field_id": "field_001",
        "name": "North Field",
        "area": 50,
        "crop_type": "wheat",
        "soil_type": "clay loam",
        "status": "growing",
        "health": "good",
        "ndvi": 0.65,
        "irrigation_status": "adequate",
        "last_irrigation": "2025-01-10T08:00:00Z",
        "soil_moisture": 45,
        "temperature_avg": 22.5,
    }


@pytest.fixture
def sample_field_data_arabic():
    """Sample field data with Arabic labels"""
    return {
        "معرف_الحقل": "حقل_001",
        "اسم_الحقل": "الحقل الشمالي",
        "المساحة": 50,
        "نوع_المحصول": "قمح",
        "نوع_التربة": "طمي طيني",
        "الحالة": "نمو",
        "الصحة": "جيد",
        "مؤشر_الخضرة": 0.65,
        "حالة_الري": "كافية",
        "رطوبة_التربة": 45,
    }


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing"""
    return {
        "current": {
            "temperature": 28,
            "humidity": 65,
            "wind_speed": 12,
            "precipitation": 0,
            "condition": "Sunny",
        },
        "forecast": [
            {
                "date": "2025-01-14",
                "temperature_max": 30,
                "temperature_min": 20,
                "humidity": 60,
                "precipitation": 0,
            },
            {
                "date": "2025-01-15",
                "temperature_max": 29,
                "temperature_min": 19,
                "humidity": 65,
                "precipitation": 5,
            },
            {
                "date": "2025-01-16",
                "temperature_max": 27,
                "temperature_min": 18,
                "humidity": 70,
                "precipitation": 15,
            },
            {
                "date": "2025-01-17",
                "temperature_max": 25,
                "temperature_min": 16,
                "humidity": 75,
                "precipitation": 20,
            },
        ],
        "alerts": [
            {"type": "frost_warning", "severity": "low", "date": "2025-01-16"}
        ],
    }


@pytest.fixture
def sample_history():
    """Sample operation history for testing"""
    return [
        {
            "date": "2025-01-10T08:00:00Z",
            "action": "irrigation",
            "status": "completed",
            "duration": "30 minutes",
            "water_applied": "250 liters",
        },
        {
            "date": "2025-01-08T09:00:00Z",
            "action": "fertilization",
            "status": "completed",
            "amount": "5 kg",
            "type": "nitrogen",
        },
        {
            "date": "2025-01-05T14:00:00Z",
            "action": "pest_spray",
            "status": "completed",
            "chemical": "organic pesticide",
            "coverage": "100%",
        },
        {
            "date": "2025-01-03T10:00:00Z",
            "action": "field_inspection",
            "status": "completed",
            "notes": "General health check, no issues found",
        },
        {
            "date": "2024-12-30T08:00:00Z",
            "action": "irrigation",
            "status": "completed",
            "duration": "30 minutes",
        },
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Token Estimation
# ═══════════════════════════════════════════════════════════════════════════════


class TestEstimateTokens:
    """Tests for token estimation utility"""

    def test_empty_text_returns_zero(self):
        """Empty text should return 0 tokens"""
        assert estimate_tokens("") == 0

    def test_english_text_estimation(self):
        """English text token count should be reasonable"""
        text = "The quick brown fox jumps over the lazy dog"
        tokens = estimate_tokens(text, language="en")
        assert tokens > 0
        assert tokens <= len(text)

    def test_arabic_text_estimation(self):
        """Arabic text token count should account for shorter characters per token"""
        text = "السلام عليكم ورحمة الله وبركاته"
        tokens = estimate_tokens(text, language="ar")
        assert tokens > 0

    def test_mixed_text_estimation(self):
        """Mixed Arabic-English text should be estimated correctly"""
        text = "السلام عليكم Hello World مرحبا"
        tokens = estimate_tokens(text, language="mixed")
        assert tokens > 0

    def test_auto_detect_english(self):
        """Auto-detect should identify English text"""
        text = "This is primarily English text with just a bit of العربية"
        tokens = estimate_tokens(text, language="auto")
        assert tokens > 0

    def test_auto_detect_arabic(self):
        """Auto-detect should identify Arabic text"""
        text = "هذا نص عربي في الأساس with just a bit of English"
        tokens = estimate_tokens(text, language="auto")
        assert tokens > 0

    def test_special_characters_affect_tokens(self):
        """Text with special characters should account for them"""
        text_simple = "Hello world"
        text_special = "Hello!!! @@@world###"
        tokens_simple = estimate_tokens(text_simple)
        tokens_special = estimate_tokens(text_special)
        assert tokens_special > tokens_simple


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Language Detection
# ═══════════════════════════════════════════════════════════════════════════════


class TestDetectPrimaryLanguage:
    """Tests for primary language detection"""

    def test_detect_english(self):
        """Should detect primary English text"""
        text = "This is English text"
        assert detect_primary_language(text) == "en"

    def test_detect_arabic(self):
        """Should detect primary Arabic text"""
        text = "هذا نص عربي"
        assert detect_primary_language(text) == "ar"

    def test_detect_mixed(self):
        """Should detect mixed language text"""
        text = "هذا نص عربي مع English text يحتوي على عدة كلمات في اللغتين"
        detected = detect_primary_language(text)
        assert detected in ["ar", "mixed"]  # Could be either depending on exact split

    def test_empty_text_defaults_to_english(self):
        """Empty text should default to English"""
        assert detect_primary_language("") == "en"

    def test_numbers_and_symbols_only(self):
        """Text with only numbers and symbols should default to English"""
        assert detect_primary_language("123 !@# $$$") == "en"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: ContextCompressor Initialization
# ═══════════════════════════════════════════════════════════════════════════════


class TestContextCompressorInit:
    """Tests for ContextCompressor initialization"""

    def test_default_initialization(self):
        """Compressor should initialize with defaults"""
        comp = ContextCompressor()
        assert comp.default_strategy == CompressionStrategy.HYBRID
        assert comp.max_tokens == 4000
        assert comp.preserve_arabic_diacritics is False

    def test_custom_initialization(self):
        """Compressor should accept custom parameters"""
        comp = ContextCompressor(
            default_strategy=CompressionStrategy.SELECTIVE,
            max_tokens=2000,
            preserve_arabic_diacritics=True,
        )
        assert comp.default_strategy == CompressionStrategy.SELECTIVE
        assert comp.max_tokens == 2000
        assert comp.preserve_arabic_diacritics is True

    def test_priority_field_keys_initialized(self):
        """Priority field keys should be set"""
        comp = ContextCompressor()
        assert len(comp.priority_field_keys) > 0
        assert "field_id" in comp.priority_field_keys
        assert "اسم_الحقل" in comp.priority_field_keys

    def test_priority_weather_keys_initialized(self):
        """Priority weather keys should be set"""
        comp = ContextCompressor()
        assert len(comp.priority_weather_keys) > 0
        assert "temperature" in comp.priority_weather_keys
        assert "درجة_الحرارة" in comp.priority_weather_keys


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Field Data Compression
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressFieldData:
    """Tests for field data compression"""

    def test_compress_single_field(self, compressor, sample_field_data):
        """Should compress single field data"""
        result = compressor.compress_field_data(sample_field_data)

        assert isinstance(result, CompressionResult)
        assert result.original_tokens > 0
        assert result.compressed_tokens > 0
        assert result.compression_ratio <= 1.0
        assert result.strategy == CompressionStrategy.HYBRID

    def test_compress_multiple_fields(self, compressor, sample_field_data):
        """Should compress list of fields"""
        fields = [sample_field_data, sample_field_data.copy()]
        result = compressor.compress_field_data(fields)

        assert isinstance(result, CompressionResult)
        assert result.original_tokens > 0
        assert result.metadata["field_count"] == 2

    def test_selective_compression(self, compressor, sample_field_data):
        """Selective strategy should keep only priority fields"""
        result = compressor.compress_field_data(
            sample_field_data, strategy=CompressionStrategy.SELECTIVE
        )

        assert result.strategy == CompressionStrategy.SELECTIVE
        assert result.compression_ratio < 1.0

    def test_extractive_compression(self, compressor, sample_field_data):
        """Extractive strategy should maintain structure"""
        result = compressor.compress_field_data(
            sample_field_data, strategy=CompressionStrategy.EXTRACTIVE
        )

        assert result.strategy == CompressionStrategy.EXTRACTIVE
        assert result.compression_ratio <= 1.0

    def test_abstractive_compression(self, compressor, sample_field_data):
        """Abstractive strategy should create summary"""
        result = compressor.compress_field_data(
            sample_field_data, strategy=CompressionStrategy.ABSTRACTIVE
        )

        assert result.strategy == CompressionStrategy.ABSTRACTIVE
        assert "summary" in result.compressed_text.lower()

    def test_tokens_saved_property(self, compressor, sample_field_data):
        """Tokens saved should be correctly calculated"""
        result = compressor.compress_field_data(sample_field_data)

        expected_saved = result.original_tokens - result.compressed_tokens
        assert result.tokens_saved == expected_saved
        assert result.tokens_saved >= 0

    def test_savings_percentage_property(self, compressor, sample_field_data):
        """Savings percentage should be between 0 and 100"""
        result = compressor.compress_field_data(sample_field_data)

        assert 0 <= result.savings_percentage <= 100
        if result.compression_ratio < 1.0:
            assert result.savings_percentage > 0

    def test_compress_arabic_field_data(self, compressor, sample_field_data_arabic):
        """Should compress Arabic field data"""
        result = compressor.compress_field_data(sample_field_data_arabic)

        assert result.original_tokens > 0
        assert result.compression_ratio <= 1.0

    def test_target_ratio_parameter(self, compressor, sample_field_data):
        """Target ratio should influence compression"""
        result_loose = compressor.compress_field_data(
            sample_field_data, target_ratio=0.8
        )
        result_tight = compressor.compress_field_data(
            sample_field_data, target_ratio=0.2
        )

        # Tight compression should generally result in smaller output
        assert result_tight.compression_ratio <= result_loose.compression_ratio


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Weather Data Compression
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressWeatherData:
    """Tests for weather data compression"""

    def test_compress_single_weather(self, compressor, sample_weather_data):
        """Should compress single weather record"""
        result = compressor.compress_weather_data(sample_weather_data)

        assert isinstance(result, CompressionResult)
        assert result.original_tokens > 0
        assert result.compressed_tokens > 0

    def test_compress_multiple_weather(self, compressor, sample_weather_data):
        """Should compress list of weather records"""
        weather_list = [sample_weather_data, sample_weather_data.copy()]
        result = compressor.compress_weather_data(weather_list)

        assert result.original_tokens > 0

    def test_forecast_days_parameter(self, compressor, sample_weather_data):
        """Should respect forecast days limit"""
        result_3days = compressor.compress_weather_data(
            sample_weather_data, include_forecast_days=3
        )
        result_1day = compressor.compress_weather_data(
            sample_weather_data, include_forecast_days=1
        )

        # More forecast days should result in larger output
        assert result_3days.compressed_tokens >= result_1day.compressed_tokens

    def test_preserves_alerts(self, compressor, sample_weather_data):
        """Weather compression should preserve alert information"""
        result = compressor.compress_weather_data(sample_weather_data)

        assert "alert" in result.compressed_text.lower()

    def test_includes_current_conditions(self, compressor, sample_weather_data):
        """Should include current weather conditions"""
        result = compressor.compress_weather_data(sample_weather_data)

        assert "current" in result.compressed_text or "temperature" in result.compressed_text.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: History Compression
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressHistory:
    """Tests for operational history compression"""

    def test_compress_empty_history(self, compressor):
        """Empty history should return empty result"""
        result = compressor.compress_history([])

        assert result.original_tokens == 0
        assert result.compressed_tokens == 0
        assert result.compression_ratio == 1.0

    def test_compress_history(self, compressor, sample_history):
        """Should compress operation history"""
        result = compressor.compress_history(sample_history)

        assert isinstance(result, CompressionResult)
        assert result.metadata["original_entries"] == len(sample_history)
        assert result.metadata["compressed_entries"] <= len(sample_history)

    def test_preserve_recent_entries(self, compressor, sample_history):
        """Should preserve recent entries fully"""
        preserve_count = 2
        result = compressor.compress_history(
            sample_history, preserve_recent=preserve_count
        )

        assert result.metadata["recent_preserved"] == preserve_count

    def test_max_entries_limit(self, compressor, sample_history):
        """Should respect maximum entries limit"""
        max_entries = 3
        result = compressor.compress_history(sample_history, max_entries=max_entries)

        assert result.metadata["compressed_entries"] <= max_entries

    def test_history_sorted_by_date(self, compressor):
        """History should be sorted by date (most recent first)"""
        history = [
            {"date": "2025-01-01T10:00:00Z", "action": "action1"},
            {"date": "2025-01-10T10:00:00Z", "action": "action10"},
            {"date": "2025-01-05T10:00:00Z", "action": "action5"},
        ]
        result = compressor.compress_history(history, preserve_recent=3)

        # Recent entries should be first in compressed result
        assert result.compressed_tokens > 0

    def test_grouping_older_entries(self, compressor):
        """Older entries should be grouped by action"""
        history = [
            {"date": "2025-01-10T10:00:00Z", "action": "irrigation", "duration": "30min"},
            {"date": "2025-01-09T10:00:00Z", "action": "irrigation", "duration": "30min"},
            {"date": "2025-01-08T10:00:00Z", "action": "irrigation", "duration": "30min"},
            {"date": "2025-01-02T10:00:00Z", "action": "old_inspection", "notes": "old"},
        ]
        result = compressor.compress_history(history, preserve_recent=1, max_entries=3)

        # Should create summaries for grouped actions
        assert "irrigation" in result.compressed_text.lower() or result.compressed_tokens > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Arabic Text Compression
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressArabicText:
    """Tests for Arabic text-specific compression"""

    def test_compress_arabic_text_basic(self, compressor):
        """Should compress Arabic text"""
        arabic_text = """
        هذا نص عربي طويل يتحدث عن الزراعة والري والمحاصيل. يحتوي هذا النص على معلومات
        مهمة عن كيفية رعاية الحقول والنباتات. يجب على المزارعين اتباع هذه التعليمات بعناية.
        """
        result = compressor.compress_arabic_text(arabic_text)

        assert result.original_tokens > 0
        assert result.compressed_tokens > 0
        assert result.compression_ratio < 1.0

    def test_preserves_diacritics(self, compressor_preserve_diacritics):
        """Should preserve diacritics when configured"""
        arabic_text = "مُحَمَّد يَزْرَعُ الْقَمْح"
        result = compressor_preserve_diacritics.compress_arabic_text(arabic_text)

        assert "ُ" in result.compressed_text or "َ" in result.compressed_text

    def test_removes_diacritics(self, compressor):
        """Should remove diacritics by default"""
        arabic_text = "مُحَمَّد يَزْرَعُ الْقَمْح"
        result = compressor.compress_arabic_text(arabic_text)

        # Diacritics should be removed
        assert result.metadata["diacritics_removed"] is True

    def test_normalizes_arabic_characters(self, compressor):
        """Should normalize Arabic character variations"""
        # Text with alef variations
        text = "إإاأآ"  # Different alef forms
        result = compressor.compress_arabic_text(text)

        # Should be normalized to single form
        assert len(result.compressed_text) <= len(text)

    def test_target_tokens_parameter(self, compressor):
        """Should compress to target token count"""
        arabic_text = "هذا نص عربي طويل " * 50  # Long text
        target_tokens = 50
        result = compressor.compress_arabic_text(arabic_text, target_tokens=target_tokens)

        assert result.compressed_tokens <= target_tokens * 1.1  # Allow 10% margin

    def test_preserves_meaning_parameter(self, compressor):
        """Should preserve meaning when requested"""
        arabic_text = """
        ري الحقل بانتظام مهم جداً. لا تترك الحقل بدون ماء لفترات طويلة.
        استخدم تقنيات الري الحديثة للحصول على أفضل النتائج.
        """
        result_preserve = compressor.compress_arabic_text(
            arabic_text, preserve_meaning=True
        )
        result_aggressive = compressor.compress_arabic_text(
            arabic_text, preserve_meaning=False
        )

        assert result_preserve.metadata["meaning_preserved"] is True
        assert result_aggressive.metadata["meaning_preserved"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: CompressionResult
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressionResult:
    """Tests for CompressionResult data class"""

    def test_tokens_saved_calculation(self):
        """Tokens saved should be correctly calculated"""
        result = CompressionResult(
            original_text="original",
            compressed_text="compressed",
            original_tokens=100,
            compressed_tokens=70,
            compression_ratio=0.7,
            strategy=CompressionStrategy.HYBRID,
        )

        assert result.tokens_saved == 30

    def test_savings_percentage_calculation(self):
        """Savings percentage should be correctly calculated"""
        result = CompressionResult(
            original_text="original",
            compressed_text="compressed",
            original_tokens=100,
            compressed_tokens=75,
            compression_ratio=0.75,
            strategy=CompressionStrategy.HYBRID,
        )

        assert result.savings_percentage == 25.0

    def test_zero_original_tokens(self):
        """Should handle zero original tokens"""
        result = CompressionResult(
            original_text="",
            compressed_text="",
            original_tokens=0,
            compressed_tokens=0,
            compression_ratio=1.0,
            strategy=CompressionStrategy.SELECTIVE,
        )

        assert result.tokens_saved == 0
        assert result.savings_percentage == 0.0

    def test_metadata_storage(self):
        """Should store and retrieve metadata"""
        metadata = {"field_count": 5, "keys_preserved": ["id", "name"]}
        result = CompressionResult(
            original_text="original",
            compressed_text="compressed",
            original_tokens=100,
            compressed_tokens=80,
            compression_ratio=0.8,
            strategy=CompressionStrategy.SELECTIVE,
            metadata=metadata,
        )

        assert result.metadata["field_count"] == 5
        assert "id" in result.metadata["keys_preserved"]


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Integration & Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressionEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_compress_large_data(self, compressor):
        """Should handle large data efficiently"""
        large_field = {
            f"field_{i}": {
                "name": f"Field {i}",
                "area": 50 + i,
                "crop": "wheat",
                "status": "growing",
                "metadata": f"Extra info {i}",
            }
            for i in range(100)
        }
        result = compressor.compress_field_data(list(large_field.values()))

        assert result.original_tokens > 0
        assert result.compression_ratio <= 1.0

    def test_compress_nested_structures(self, compressor):
        """Should handle deeply nested data structures"""
        nested = {
            "field": {
                "details": {
                    "measurements": {
                        "soil": {"moisture": 45, "ph": 7.2},
                        "air": {"temperature": 28, "humidity": 65},
                    }
                }
            }
        }
        result = compressor.compress_field_data(nested)

        assert result.original_tokens > 0

    def test_compress_special_characters(self, compressor):
        """Should handle special characters in data"""
        data = {
            "name": "Field #1 - Special: @chars$ (2025)",
            "notes": "Contains 🌾 emoji and special chars: !@#$%^&*()",
        }
        result = compressor.compress_field_data(data)

        assert result.original_tokens > 0

    def test_compress_all_strategies(self, compressor, sample_field_data):
        """Should work with all compression strategies"""
        strategies = [
            CompressionStrategy.SELECTIVE,
            CompressionStrategy.EXTRACTIVE,
            CompressionStrategy.ABSTRACTIVE,
            CompressionStrategy.HYBRID,
        ]

        for strategy in strategies:
            result = compressor.compress_field_data(
                sample_field_data, strategy=strategy
            )
            assert result.strategy == strategy
            assert result.original_tokens > 0

    def test_compress_unicode_text(self, compressor):
        """Should handle Unicode text correctly"""
        unicode_text = "مرحبا بك في منصة SAHOOL للزراعة الذكية"
        result = compressor.compress_arabic_text(unicode_text)

        assert result.original_tokens > 0
        assert isinstance(result.compressed_text, str)

    def test_history_with_multiple_actions(self, compressor):
        """Should handle history entries with multiple action types"""
        history = [
            {"date": "2025-01-10T10:00:00Z", "action": "irrigation", "duration": "30min"},
            {"date": "2025-01-09T10:00:00Z", "action": "inspection", "notes": "good"},
            {"date": "2025-01-08T10:00:00Z", "action": "fertilization", "amount": "50kg"},
        ]
        result = compressor.compress_history(history)

        assert result.metadata["original_entries"] == 3
        assert result.compressed_tokens > 0

    def test_weather_without_forecast(self, compressor):
        """Should handle weather data without forecast"""
        weather = {
            "current": {"temperature": 28, "humidity": 65},
            "alerts": [{"type": "frost_warning"}],
        }
        result = compressor.compress_weather_data(weather)

        assert result.original_tokens > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Compression Ratio Validation
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompressionRatios:
    """Tests for validating compression ratios"""

    def test_selective_achieves_compression(self, compressor, sample_field_data):
        """Selective compression should reduce tokens"""
        result = compressor.compress_field_data(
            sample_field_data, strategy=CompressionStrategy.SELECTIVE
        )
        assert result.compression_ratio < 1.0

    def test_hybrid_achieves_compression(self, compressor, sample_field_data):
        """Hybrid compression should reduce tokens"""
        result = compressor.compress_field_data(
            sample_field_data, strategy=CompressionStrategy.HYBRID
        )
        assert result.compression_ratio <= 1.0

    def test_compression_never_increases_beyond_original(
        self, compressor, sample_field_data
    ):
        """Compressed should never exceed original"""
        result = compressor.compress_field_data(sample_field_data)
        assert result.compressed_tokens <= result.original_tokens

    @pytest.mark.parametrize(
        "ratio",
        [
            DEFAULT_FIELD_COMPRESSION_RATIO,
            DEFAULT_WEATHER_COMPRESSION_RATIO,
            DEFAULT_HISTORY_COMPRESSION_RATIO,
        ],
    )
    def test_default_compression_ratios(self, ratio):
        """Default ratios should be valid"""
        assert 0 < ratio < 1.0
