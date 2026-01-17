"""
AI Context Compression Module
==============================
وحدة ضغط السياق للذكاء الاصطناعي

Provides context compression utilities for optimizing AI context windows.
Supports field data, weather data, and history compression with Arabic text support.

المميزات:
- ضغط بيانات الحقول الزراعية
- ضغط بيانات الطقس والمناخ
- ضغط سجل العمليات
- دعم النص العربي
- تقدير عدد الرموز (Tokens)

Author: SAHOOL Platform Team
Updated: January 2025
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Constants & Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Average characters per token for different languages
# Arabic text typically has ~2.5 characters per token due to word structure
CHARS_PER_TOKEN_ARABIC = 2.5
CHARS_PER_TOKEN_ENGLISH = 4.0
CHARS_PER_TOKEN_MIXED = 3.0

# Default compression ratios
DEFAULT_FIELD_COMPRESSION_RATIO = 0.3
DEFAULT_WEATHER_COMPRESSION_RATIO = 0.4
DEFAULT_HISTORY_COMPRESSION_RATIO = 0.25


# ─────────────────────────────────────────────────────────────────────────────
# Enums & Models
# ─────────────────────────────────────────────────────────────────────────────


class CompressionStrategy(str, Enum):
    """
    Context compression strategy.
    استراتيجية ضغط السياق
    """

    EXTRACTIVE = "extractive"  # Extract key sentences
    ABSTRACTIVE = "abstractive"  # Generate summaries
    HYBRID = "hybrid"  # Combine both approaches
    SELECTIVE = "selective"  # Select most relevant fields


@dataclass
class CompressionResult:
    """
    Result of context compression operation.
    نتيجة عملية ضغط السياق

    Attributes:
        original_text: النص الأصلي - Original text before compression
        compressed_text: النص المضغوط - Compressed text output
        original_tokens: عدد الرموز الأصلية - Estimated original token count
        compressed_tokens: عدد الرموز المضغوطة - Estimated compressed token count
        compression_ratio: نسبة الضغط - Compression ratio achieved
        strategy: الاستراتيجية - Strategy used for compression
        metadata: البيانات الوصفية - Additional metadata about compression
    """

    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    strategy: CompressionStrategy
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def tokens_saved(self) -> int:
        """Number of tokens saved by compression / عدد الرموز الموفرة"""
        return self.original_tokens - self.compressed_tokens

    @property
    def savings_percentage(self) -> float:
        """Percentage of tokens saved / نسبة التوفير"""
        if self.original_tokens == 0:
            return 0.0
        return (self.tokens_saved / self.original_tokens) * 100


# ─────────────────────────────────────────────────────────────────────────────
# Token Estimation
# ─────────────────────────────────────────────────────────────────────────────


def estimate_tokens(text: str, language: str = "auto") -> int:
    """
    Estimate the number of tokens in a text.
    تقدير عدد الرموز في النص

    Args:
        text: النص المراد تقدير رموزه - Text to estimate tokens for
        language: لغة النص - Language hint ("ar", "en", "auto")

    Returns:
        int: عدد الرموز المقدر - Estimated token count

    Note:
        This is an approximation. For exact counts, use a tokenizer like tiktoken.
        هذا تقدير تقريبي. للحصول على عدد دقيق، استخدم مُرمِّز مثل tiktoken.
    """
    if not text:
        return 0

    if language == "auto":
        language = detect_primary_language(text)

    chars_per_token = {
        "ar": CHARS_PER_TOKEN_ARABIC,
        "en": CHARS_PER_TOKEN_ENGLISH,
        "mixed": CHARS_PER_TOKEN_MIXED,
    }.get(language, CHARS_PER_TOKEN_MIXED)

    # Account for whitespace and special characters
    char_count = len(text)
    whitespace_count = len(re.findall(r"\s", text))
    special_count = len(re.findall(r"[^\w\s]", text))

    # Adjust for whitespace (doesn't add tokens in most tokenizers)
    effective_chars = char_count - (whitespace_count * 0.5)

    # Special characters often become individual tokens
    special_token_adjustment = special_count * 0.5

    estimated_tokens = (effective_chars / chars_per_token) + special_token_adjustment

    return max(1, int(estimated_tokens))


def detect_primary_language(text: str) -> str:
    """
    Detect the primary language of text.
    تحديد اللغة الأساسية للنص

    Args:
        text: النص - Text to analyze

    Returns:
        str: كود اللغة - Language code ("ar", "en", or "mixed")
    """
    if not text:
        return "en"

    # Count Arabic characters (Unicode range for Arabic)
    arabic_chars = len(re.findall(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", text))
    # Count Latin characters
    latin_chars = len(re.findall(r"[a-zA-Z]", text))

    total_chars = arabic_chars + latin_chars
    if total_chars == 0:
        return "en"

    arabic_ratio = arabic_chars / total_chars

    if arabic_ratio > 0.7:
        return "ar"
    elif arabic_ratio < 0.3:
        return "en"
    else:
        return "mixed"


# ─────────────────────────────────────────────────────────────────────────────
# Context Compressor Class
# ─────────────────────────────────────────────────────────────────────────────


class ContextCompressor:
    """
    Context compression for AI interactions.
    ضاغط السياق للتفاعلات مع الذكاء الاصطناعي

    Provides compression utilities for field data, weather data, and
    operational history to optimize AI context window usage.

    يوفر أدوات ضغط لبيانات الحقول وبيانات الطقس وسجل العمليات
    لتحسين استخدام نافذة سياق الذكاء الاصطناعي.

    Example:
        >>> compressor = ContextCompressor()
        >>> result = compressor.compress_field_data(field_info)
        >>> print(f"Saved {result.savings_percentage:.1f}% tokens")

    المثال:
        >>> compressor = ContextCompressor()
        >>> result = compressor.compress_field_data(field_info)
        >>> print(f"تم توفير {result.savings_percentage:.1f}% من الرموز")
    """

    def __init__(
        self,
        default_strategy: CompressionStrategy = CompressionStrategy.HYBRID,
        max_tokens: int = 4000,
        preserve_arabic_diacritics: bool = False,
    ):
        """
        Initialize the context compressor.
        تهيئة ضاغط السياق

        Args:
            default_strategy: الاستراتيجية الافتراضية - Default compression strategy
            max_tokens: الحد الأقصى للرموز - Maximum tokens target
            preserve_arabic_diacritics: الحفاظ على التشكيل - Keep Arabic diacritics
        """
        self.default_strategy = default_strategy
        self.max_tokens = max_tokens
        self.preserve_arabic_diacritics = preserve_arabic_diacritics

        # Key field names for prioritization (English and Arabic)
        self.priority_field_keys = {
            # English
            "field_id",
            "name",
            "area",
            "crop_type",
            "crop",
            "status",
            "health",
            "ndvi",
            "irrigation_status",
            "soil_type",
            "location",
            # Arabic
            "اسم_الحقل",
            "المساحة",
            "نوع_المحصول",
            "الحالة",
            "الصحة",
        }

        # Key weather fields
        self.priority_weather_keys = {
            "temperature",
            "humidity",
            "precipitation",
            "wind_speed",
            "forecast",
            "alert",
            "درجة_الحرارة",
            "الرطوبة",
            "الأمطار",
        }

        logger.info(
            f"ContextCompressor initialized with strategy={default_strategy.value}, "
            f"max_tokens={max_tokens}"
        )

    def compress_field_data(
        self,
        field_data: dict[str, Any] | list[dict[str, Any]],
        strategy: CompressionStrategy | None = None,
        target_ratio: float = DEFAULT_FIELD_COMPRESSION_RATIO,
    ) -> CompressionResult:
        """
        Compress field data for AI context.
        ضغط بيانات الحقل لسياق الذكاء الاصطناعي

        Args:
            field_data: بيانات الحقل - Field data dict or list of fields
            strategy: الاستراتيجية - Compression strategy (optional)
            target_ratio: نسبة الضغط المستهدفة - Target compression ratio

        Returns:
            CompressionResult: نتيجة الضغط - Compression result

        Example:
            >>> field = {"name": "North Field", "area": 50, "crop": "wheat", ...}
            >>> result = compressor.compress_field_data(field)
        """
        strategy = strategy or self.default_strategy

        # Convert to list if single dict
        fields = [field_data] if isinstance(field_data, dict) else field_data

        # Build original text representation
        original_text = self._dict_to_text(fields)
        original_tokens = estimate_tokens(original_text)

        # Apply compression strategy
        if strategy == CompressionStrategy.SELECTIVE:
            compressed_fields = self._selective_compress_fields(fields)
        elif strategy == CompressionStrategy.EXTRACTIVE:
            compressed_fields = self._extractive_compress_fields(fields, target_ratio)
        elif strategy == CompressionStrategy.ABSTRACTIVE:
            compressed_fields = self._abstractive_compress_fields(fields)
        else:  # HYBRID
            compressed_fields = self._hybrid_compress_fields(fields, target_ratio)

        compressed_text = self._dict_to_text(compressed_fields)
        compressed_tokens = estimate_tokens(compressed_text)

        actual_ratio = compressed_tokens / max(original_tokens, 1)

        logger.info(
            f"Field data compressed: {original_tokens} -> {compressed_tokens} tokens "
            f"(ratio: {actual_ratio:.2f})"
        )

        return CompressionResult(
            original_text=original_text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=actual_ratio,
            strategy=strategy,
            metadata={
                "field_count": len(fields),
                "keys_preserved": list(self.priority_field_keys),
                "target_ratio": target_ratio,
            },
        )

    def compress_weather_data(
        self,
        weather_data: dict[str, Any] | list[dict[str, Any]],
        strategy: CompressionStrategy | None = None,
        include_forecast_days: int = 3,
    ) -> CompressionResult:
        """
        Compress weather data for AI context.
        ضغط بيانات الطقس لسياق الذكاء الاصطناعي

        Args:
            weather_data: بيانات الطقس - Weather data dict or list
            strategy: الاستراتيجية - Compression strategy (optional)
            include_forecast_days: أيام التوقعات - Number of forecast days to include

        Returns:
            CompressionResult: نتيجة الضغط - Compression result

        Example:
            >>> weather = {"current": {...}, "forecast": [...], "alerts": [...]}
            >>> result = compressor.compress_weather_data(weather, include_forecast_days=5)
        """
        strategy = strategy or self.default_strategy

        # Handle single dict or list
        weather_list = [weather_data] if isinstance(weather_data, dict) else weather_data

        original_text = self._dict_to_text(weather_list)
        original_tokens = estimate_tokens(original_text)

        compressed_weather = []
        for weather in weather_list:
            compressed = self._compress_single_weather(weather, include_forecast_days)
            compressed_weather.append(compressed)

        compressed_text = self._dict_to_text(compressed_weather)
        compressed_tokens = estimate_tokens(compressed_text)

        actual_ratio = compressed_tokens / max(original_tokens, 1)

        logger.info(
            f"Weather data compressed: {original_tokens} -> {compressed_tokens} tokens "
            f"(ratio: {actual_ratio:.2f})"
        )

        return CompressionResult(
            original_text=original_text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=actual_ratio,
            strategy=strategy,
            metadata={
                "forecast_days_included": include_forecast_days,
                "has_alerts": any("alert" in str(w).lower() for w in weather_list),
            },
        )

    def compress_history(
        self,
        history: list[dict[str, Any]],
        max_entries: int = 10,
        strategy: CompressionStrategy | None = None,
        preserve_recent: int = 3,
    ) -> CompressionResult:
        """
        Compress operational history for AI context.
        ضغط سجل العمليات لسياق الذكاء الاصطناعي

        Uses a sliding window approach to preserve recent entries while
        summarizing older history.

        يستخدم نهج النافذة المنزلقة للحفاظ على الإدخالات الأخيرة
        مع تلخيص السجل الأقدم.

        Args:
            history: سجل العمليات - List of history entries
            max_entries: الحد الأقصى للإدخالات - Maximum entries to include
            strategy: الاستراتيجية - Compression strategy (optional)
            preserve_recent: عدد الإدخالات الحديثة - Recent entries to preserve fully

        Returns:
            CompressionResult: نتيجة الضغط - Compression result

        Example:
            >>> history = [{"date": "2025-01-01", "action": "irrigation", ...}, ...]
            >>> result = compressor.compress_history(history, max_entries=10)
        """
        strategy = strategy or self.default_strategy

        if not history:
            return CompressionResult(
                original_text="",
                compressed_text="",
                original_tokens=0,
                compressed_tokens=0,
                compression_ratio=1.0,
                strategy=strategy,
                metadata={"entries_count": 0},
            )

        original_text = self._dict_to_text(history)
        original_tokens = estimate_tokens(original_text)

        # Sort by date if available (most recent first)
        sorted_history = self._sort_by_date(history)

        # Preserve recent entries fully
        recent_entries = sorted_history[:preserve_recent]
        older_entries = sorted_history[preserve_recent:]

        # Compress older entries
        compressed_older = self._compress_older_history(
            older_entries, max_entries - preserve_recent
        )

        # Combine
        compressed_history = recent_entries + compressed_older

        compressed_text = self._dict_to_text(compressed_history)
        compressed_tokens = estimate_tokens(compressed_text)

        actual_ratio = compressed_tokens / max(original_tokens, 1)

        logger.info(
            f"History compressed: {len(history)} entries -> {len(compressed_history)} entries, "
            f"{original_tokens} -> {compressed_tokens} tokens (ratio: {actual_ratio:.2f})"
        )

        return CompressionResult(
            original_text=original_text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=actual_ratio,
            strategy=strategy,
            metadata={
                "original_entries": len(history),
                "compressed_entries": len(compressed_history),
                "recent_preserved": preserve_recent,
            },
        )

    def compress_arabic_text(
        self,
        text: str,
        target_tokens: int | None = None,
        preserve_meaning: bool = True,
    ) -> CompressionResult:
        """
        Compress Arabic text specifically.
        ضغط النص العربي بشكل خاص

        Handles Arabic-specific compression including:
        - Removing diacritics (تشكيل) if allowed
        - Condensing repeated phrases
        - Removing redundant conjunctions

        Args:
            text: النص العربي - Arabic text to compress
            target_tokens: عدد الرموز المستهدف - Target token count
            preserve_meaning: الحفاظ على المعنى - Preserve semantic meaning

        Returns:
            CompressionResult: نتيجة الضغط - Compression result
        """
        original_tokens = estimate_tokens(text, language="ar")
        target_tokens = target_tokens or int(original_tokens * 0.5)

        compressed_text = text

        # Step 1: Remove diacritics if not preserving
        if not self.preserve_arabic_diacritics:
            compressed_text = self._remove_arabic_diacritics(compressed_text)

        # Step 2: Normalize Arabic characters
        compressed_text = self._normalize_arabic(compressed_text)

        # Step 3: Remove redundant conjunctions and filler words
        if not preserve_meaning:
            compressed_text = self._remove_arabic_fillers(compressed_text)

        # Step 4: Condense repeated information
        compressed_text = self._condense_repetitions(compressed_text)

        # Step 5: Trim to target if still over
        current_tokens = estimate_tokens(compressed_text, language="ar")
        if current_tokens > target_tokens:
            compressed_text = self._truncate_to_tokens(
                compressed_text, target_tokens, language="ar"
            )

        compressed_tokens = estimate_tokens(compressed_text, language="ar")
        actual_ratio = compressed_tokens / max(original_tokens, 1)

        return CompressionResult(
            original_text=text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=actual_ratio,
            strategy=CompressionStrategy.HYBRID,
            metadata={
                "language": "ar",
                "diacritics_removed": not self.preserve_arabic_diacritics,
                "meaning_preserved": preserve_meaning,
            },
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Private Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _dict_to_text(self, data: Any) -> str:
        """Convert dict/list to text representation"""
        if isinstance(data, str):
            return data
        import json

        return json.dumps(data, ensure_ascii=False, indent=2)

    def _selective_compress_fields(
        self, fields: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Select only priority fields"""
        compressed = []
        for field_data in fields:
            compressed_field = {}
            for key, value in field_data.items():
                key_lower = key.lower().replace(" ", "_")
                if key_lower in self.priority_field_keys or key in self.priority_field_keys:
                    compressed_field[key] = value
            compressed.append(compressed_field)
        return compressed

    def _extractive_compress_fields(
        self, fields: list[dict[str, Any]], target_ratio: float
    ) -> list[dict[str, Any]]:
        """Extract key information maintaining structure"""
        # Start with selective compression
        compressed = self._selective_compress_fields(fields)

        # Add additional important fields based on target ratio
        for i, field_data in enumerate(fields):
            for key, value in field_data.items():
                if key not in compressed[i] and self._is_important_value(value):
                    compressed[i][key] = value

        return compressed

    def _abstractive_compress_fields(
        self, fields: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create summaries of field data"""
        compressed = []
        for field_data in fields:
            summary = {
                "summary": self._create_field_summary(field_data),
            }
            # Include critical identifiers
            for key in ["field_id", "id", "name"]:
                if key in field_data:
                    summary[key] = field_data[key]
            compressed.append(summary)
        return compressed

    def _hybrid_compress_fields(
        self, fields: list[dict[str, Any]], target_ratio: float
    ) -> list[dict[str, Any]]:
        """Combine selective extraction with summarization"""
        compressed = []
        for field_data in fields:
            compressed_field = {}

            # Keep priority fields
            for key, value in field_data.items():
                key_lower = key.lower().replace(" ", "_")
                if key_lower in self.priority_field_keys or key in self.priority_field_keys:
                    compressed_field[key] = value

            # Add summary for complex nested data
            nested_keys = [k for k, v in field_data.items() if isinstance(v, (dict, list))]
            if nested_keys:
                compressed_field["_nested_summary"] = f"Contains: {', '.join(nested_keys)}"

            compressed.append(compressed_field)
        return compressed

    def _compress_single_weather(
        self, weather: dict[str, Any], forecast_days: int
    ) -> dict[str, Any]:
        """Compress a single weather data entry"""
        compressed = {}

        # Always include current conditions
        if "current" in weather:
            compressed["current"] = self._extract_key_weather_fields(weather["current"])

        # Include limited forecast
        if "forecast" in weather and isinstance(weather["forecast"], list):
            compressed["forecast"] = [
                self._extract_key_weather_fields(day)
                for day in weather["forecast"][:forecast_days]
            ]

        # Always include alerts
        if "alerts" in weather:
            compressed["alerts"] = weather["alerts"]
        elif "alert" in weather:
            compressed["alert"] = weather["alert"]

        # Include any other priority keys
        for key, value in weather.items():
            if key not in compressed and key.lower() in self.priority_weather_keys:
                compressed[key] = value

        return compressed

    def _extract_key_weather_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract key fields from weather data"""
        if not isinstance(data, dict):
            return data

        extracted = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(pk in key_lower for pk in self.priority_weather_keys):
                extracted[key] = value

        return extracted or data

    def _sort_by_date(self, history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort history entries by date (most recent first)"""
        date_keys = ["date", "timestamp", "created_at", "time", "التاريخ"]

        def get_date(entry: dict) -> datetime:
            for key in date_keys:
                if key in entry:
                    value = entry[key]
                    if isinstance(value, datetime):
                        return value
                    if isinstance(value, str):
                        try:
                            return datetime.fromisoformat(value.replace("Z", "+00:00"))
                        except (ValueError, TypeError):
                            continue
            return datetime.min

        return sorted(history, key=get_date, reverse=True)

    def _compress_older_history(
        self, history: list[dict[str, Any]], max_entries: int
    ) -> list[dict[str, Any]]:
        """Compress older history entries"""
        if not history or max_entries <= 0:
            return []

        if len(history) <= max_entries:
            # Just remove non-essential fields
            return [self._compress_history_entry(entry) for entry in history]

        # Group by action type and summarize
        action_groups: dict[str, list] = {}
        for entry in history:
            action = entry.get("action", entry.get("type", "unknown"))
            if action not in action_groups:
                action_groups[action] = []
            action_groups[action].append(entry)

        # Create summary entries
        summaries = []
        for action, entries in action_groups.items():
            if len(entries) == 1:
                summaries.append(self._compress_history_entry(entries[0]))
            else:
                summaries.append(
                    {
                        "action": action,
                        "count": len(entries),
                        "summary": f"{action}: {len(entries)} occurrences",
                        "date_range": self._get_date_range(entries),
                    }
                )

        return summaries[:max_entries]

    def _compress_history_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Compress a single history entry"""
        important_keys = {
            "date",
            "timestamp",
            "action",
            "type",
            "status",
            "result",
            "field_id",
            "التاريخ",
            "الإجراء",
        }
        return {k: v for k, v in entry.items() if k in important_keys}

    def _get_date_range(self, entries: list[dict[str, Any]]) -> str:
        """Get date range string for entries"""
        sorted_entries = self._sort_by_date(entries)
        if not sorted_entries:
            return "unknown"

        first = sorted_entries[-1].get("date", sorted_entries[-1].get("timestamp", "?"))
        last = sorted_entries[0].get("date", sorted_entries[0].get("timestamp", "?"))

        return f"{first} to {last}"

    def _is_important_value(self, value: Any) -> bool:
        """Check if a value is likely important"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value  # True values are important
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) < 100 and len(value) > 0
        return False

    def _create_field_summary(self, field: dict[str, Any]) -> str:
        """Create a brief summary of field data"""
        parts = []

        name = field.get("name", field.get("اسم_الحقل", "Unknown"))
        parts.append(f"Field: {name}")

        if "area" in field or "المساحة" in field:
            area = field.get("area", field.get("المساحة"))
            parts.append(f"Area: {area}")

        if "crop" in field or "crop_type" in field or "نوع_المحصول" in field:
            crop = field.get("crop", field.get("crop_type", field.get("نوع_المحصول")))
            parts.append(f"Crop: {crop}")

        if "status" in field or "الحالة" in field:
            status = field.get("status", field.get("الحالة"))
            parts.append(f"Status: {status}")

        return " | ".join(parts)

    def _remove_arabic_diacritics(self, text: str) -> str:
        """Remove Arabic diacritical marks (تشكيل)"""
        # Arabic diacritics Unicode range
        diacritics_pattern = re.compile(r"[\u064B-\u065F\u0670]")
        return diacritics_pattern.sub("", text)

    def _normalize_arabic(self, text: str) -> str:
        """Normalize Arabic character variations"""
        # Normalize alef variations
        text = re.sub(r"[إأآا]", "ا", text)
        # Normalize yaa
        text = re.sub(r"[ىي]", "ي", text)
        # Normalize taa marbouta
        text = re.sub(r"ة", "ه", text)
        return text

    def _remove_arabic_fillers(self, text: str) -> str:
        """Remove Arabic filler words and redundant conjunctions"""
        # Common filler words in Arabic
        fillers = [
            r"\bو\s+",  # و (and) at word boundary
            r"\bمن\s+",  # من (from)
            r"\bإلى\s+",  # إلى (to)
            r"\bفي\s+",  # في (in)
            r"\bعلى\s+",  # على (on)
            r"\bهذا\s+",  # هذا (this)
            r"\bهذه\s+",  # هذه (this f)
            r"\bالذي\s+",  # الذي (which)
            r"\bالتي\s+",  # التي (which f)
        ]

        result = text
        for filler in fillers:
            # Only remove if not changing meaning significantly
            test_removal = re.sub(filler, "", result)
            if len(test_removal) > len(result) * 0.5:  # Don't remove too much
                result = test_removal

        return result

    def _condense_repetitions(self, text: str) -> str:
        """Condense repeated phrases or information"""
        # Remove duplicate consecutive words
        text = re.sub(r"\b(\w+)\s+\1\b", r"\1", text)

        # Remove multiple spaces
        text = re.sub(r"\s+", " ", text)

        # Remove repeated punctuation
        text = re.sub(r"([.،,!?])\1+", r"\1", text)

        return text.strip()

    def _truncate_to_tokens(self, text: str, target_tokens: int, language: str) -> str:
        """Truncate text to approximately target token count"""
        current_tokens = estimate_tokens(text, language)
        if current_tokens <= target_tokens:
            return text

        # Estimate characters needed
        chars_per_token = {
            "ar": CHARS_PER_TOKEN_ARABIC,
            "en": CHARS_PER_TOKEN_ENGLISH,
            "mixed": CHARS_PER_TOKEN_MIXED,
        }.get(language, CHARS_PER_TOKEN_MIXED)

        target_chars = int(target_tokens * chars_per_token)

        # Truncate at word boundary
        if len(text) > target_chars:
            truncated = text[:target_chars]
            last_space = truncated.rfind(" ")
            if last_space > target_chars * 0.8:
                truncated = truncated[:last_space]
            return truncated + "..."

        return text
