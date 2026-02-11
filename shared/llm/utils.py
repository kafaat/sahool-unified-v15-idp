"""
LLM Utilities Module
====================
وحدة أدوات نماذج اللغة الكبيرة

Utility functions for:
- Token counting (approximation)
- Response parsing
- JSON extraction from LLM output
- Text preprocessing

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")


# ============================================================================
# TOKEN COUNTING
# ============================================================================


def estimate_tokens(text: str, model: str | None = None) -> int:
    """
    Estimate token count for text.

    تقدير عدد الرموز للنص

    Uses a simple heuristic: ~4 characters per token for English,
    ~2 characters per token for Arabic (more tokens per character).

    Args:
        text: Text to count tokens for
        model: Model name (for model-specific estimation)

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Check for Arabic content
    arabic_pattern = re.compile(r"[\u0600-\u06FF]")
    arabic_chars = len(arabic_pattern.findall(text))
    total_chars = len(text)

    # Arabic text tends to use more tokens
    if arabic_chars > total_chars * 0.3:
        # Predominantly Arabic: ~2 chars per token
        return max(1, total_chars // 2)
    else:
        # Predominantly English/Latin: ~4 chars per token
        return max(1, total_chars // 4)


def estimate_tokens_messages(messages: list[dict[str, str]]) -> int:
    """
    Estimate token count for chat messages.

    تقدير عدد الرموز لرسائل الدردشة

    Args:
        messages: List of message dicts with "role" and "content"

    Returns:
        Estimated token count
    """
    total = 0
    for msg in messages:
        # Add overhead for role and formatting (~4 tokens per message)
        total += 4
        content = msg.get("content", "")
        total += estimate_tokens(content)
    return total


def check_context_limit(
    text: str,
    max_tokens: int = 4096,
    reserved_output_tokens: int = 1024,
) -> tuple[bool, int]:
    """
    Check if text fits within context limit.

    التحقق مما إذا كان النص يتناسب مع حد السياق

    Args:
        text: Text to check
        max_tokens: Maximum context length
        reserved_output_tokens: Tokens reserved for output

    Returns:
        Tuple of (fits, estimated_tokens)
    """
    estimated = estimate_tokens(text)
    available = max_tokens - reserved_output_tokens
    return estimated <= available, estimated


def truncate_to_token_limit(
    text: str,
    max_tokens: int = 4096,
    reserved_output_tokens: int = 1024,
    truncate_from: str = "end",
) -> str:
    """
    Truncate text to fit within token limit.

    اقتطاع النص ليتناسب مع حد الرموز

    Args:
        text: Text to truncate
        max_tokens: Maximum context length
        reserved_output_tokens: Tokens reserved for output
        truncate_from: Where to truncate ("start" or "end")

    Returns:
        Truncated text
    """
    fits, estimated = check_context_limit(text, max_tokens, reserved_output_tokens)
    if fits:
        return text

    available = max_tokens - reserved_output_tokens
    # Rough calculation: multiply by 4 for char estimate
    target_chars = available * 4

    if truncate_from == "start":
        return "..." + text[-target_chars:]
    else:
        return text[:target_chars] + "..."


# ============================================================================
# JSON EXTRACTION
# ============================================================================


@dataclass
class JSONExtractionResult:
    """Result of JSON extraction."""

    success: bool
    data: Any
    raw_text: str
    error: str | None = None


def extract_json(text: str) -> JSONExtractionResult:
    """
    Extract JSON from LLM response text.

    استخراج JSON من نص استجابة LLM

    Handles common patterns:
    - Pure JSON response
    - JSON in markdown code blocks
    - JSON mixed with explanatory text

    Args:
        text: LLM response text

    Returns:
        JSONExtractionResult with parsed data or error
    """
    if not text:
        return JSONExtractionResult(
            success=False,
            data=None,
            raw_text=text,
            error="Empty text",
        )

    text = text.strip()

    # Try 1: Direct JSON parse
    try:
        data = json.loads(text)
        return JSONExtractionResult(success=True, data=data, raw_text=text)
    except json.JSONDecodeError:
        pass

    # Try 2: Extract from markdown code block
    code_block_patterns = [
        r"```json\s*([\s\S]*?)\s*```",
        r"```\s*([\s\S]*?)\s*```",
    ]

    for pattern in code_block_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                data = json.loads(match.group(1))
                return JSONExtractionResult(success=True, data=data, raw_text=text)
            except json.JSONDecodeError:
                pass

    # Try 3: Find JSON object or array in text
    # Look for outermost braces/brackets
    json_patterns = [
        (r"\{[\s\S]*\}", "object"),
        (r"\[[\s\S]*\]", "array"),
    ]

    for pattern, _ in json_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                # Find the balanced JSON
                data = json.loads(match)
                return JSONExtractionResult(success=True, data=data, raw_text=text)
            except json.JSONDecodeError:
                # Try to find balanced braces
                balanced = _find_balanced_json(match)
                if balanced:
                    try:
                        data = json.loads(balanced)
                        return JSONExtractionResult(success=True, data=data, raw_text=text)
                    except json.JSONDecodeError:
                        pass

    return JSONExtractionResult(
        success=False,
        data=None,
        raw_text=text,
        error="Could not extract valid JSON from response",
    )


def _find_balanced_json(text: str) -> str | None:
    """Find balanced JSON object or array in text."""
    if not text:
        return None

    start_char = text[0] if text else None
    if start_char == "{":
        end_char = "}"
    elif start_char == "[":
        end_char = "]"
    else:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i, char in enumerate(text):
        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == start_char:
            depth += 1
        elif char == end_char:
            depth -= 1
            if depth == 0:
                return text[: i + 1]

    return None


def extract_json_list(text: str) -> list[Any]:
    """
    Extract all JSON objects/arrays from text.

    استخراج جميع كائنات/مصفوفات JSON من النص

    Args:
        text: Text containing JSON

    Returns:
        List of extracted JSON objects
    """
    results = []

    # Find all potential JSON blocks
    patterns = [
        r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",
        r"\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                results.append(data)
            except json.JSONDecodeError:
                pass

    return results


# ============================================================================
# RESPONSE PARSING
# ============================================================================


def parse_numbered_list(text: str) -> list[str]:
    """
    Parse a numbered list from LLM response.

    تحليل قائمة مرقمة من استجابة LLM

    Args:
        text: Text containing numbered list

    Returns:
        List of items
    """
    items = []
    # Match patterns like "1.", "1)", "1-", "(1)"
    pattern = r"^\s*(?:\d+[.\)\-]|\(\d+\))\s*(.+)$"

    for line in text.split("\n"):
        match = re.match(pattern, line)
        if match:
            items.append(match.group(1).strip())

    return items


def parse_bullet_list(text: str) -> list[str]:
    """
    Parse a bullet list from LLM response.

    تحليل قائمة نقطية من استجابة LLM

    Args:
        text: Text containing bullet list

    Returns:
        List of items
    """
    items = []
    # Match patterns like "•", "-", "*", "○"
    pattern = r"^\s*[•\-\*○●]\s*(.+)$"

    for line in text.split("\n"):
        match = re.match(pattern, line)
        if match:
            items.append(match.group(1).strip())

    return items


def parse_key_value_pairs(text: str) -> dict[str, str]:
    """
    Parse key-value pairs from LLM response.

    تحليل أزواج المفتاح-القيمة من استجابة LLM

    Handles patterns like:
    - "Key: Value"
    - "Key = Value"
    - "**Key**: Value"

    Args:
        text: Text containing key-value pairs

    Returns:
        Dictionary of key-value pairs
    """
    pairs = {}
    patterns = [
        r"^\s*\*{0,2}([^:=\*]+)\*{0,2}\s*[:=]\s*(.+)$",
    ]

    for line in text.split("\n"):
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                pairs[key] = value
                break

    return pairs


def extract_code_blocks(text: str, language: str | None = None) -> list[str]:
    """
    Extract code blocks from markdown-formatted response.

    استخراج كتل الكود من استجابة بتنسيق Markdown

    Args:
        text: Text containing code blocks
        language: Optional language filter (e.g., "python", "json")

    Returns:
        List of code block contents
    """
    blocks = []

    if language:
        pattern = rf"```{language}\s*([\s\S]*?)\s*```"
    else:
        pattern = r"```(?:\w+)?\s*([\s\S]*?)\s*```"

    matches = re.findall(pattern, text, re.IGNORECASE)
    blocks.extend(matches)

    return blocks


# ============================================================================
# TEXT PREPROCESSING
# ============================================================================


def clean_response(text: str) -> str:
    """
    Clean LLM response text.

    تنظيف نص استجابة LLM

    Removes common artifacts and normalizes whitespace.

    Args:
        text: Raw LLM response

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove common prefixes
    prefixes_to_remove = [
        "Sure, ",
        "Sure! ",
        "Of course, ",
        "Of course! ",
        "Here's ",
        "Here is ",
        "Certainly, ",
        "Certainly! ",
    ]

    for prefix in prefixes_to_remove:
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.

    تقسيم النص إلى جمل

    Handles both English and Arabic sentence boundaries.

    Args:
        text: Text to split

    Returns:
        List of sentences
    """
    # Sentence-ending patterns for both English and Arabic
    pattern = r"(?<=[.!?؟。])\s+"
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text.

    تطبيع النص العربي

    Normalizes common variations:
    - Alef variations → ا
    - Teh marbuta → ه
    - Remove tatweel (kashida)

    Args:
        text: Arabic text

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Normalize Alef variations
    text = re.sub(r"[أإآ]", "ا", text)

    # Normalize Yeh
    text = re.sub(r"[ى]", "ي", text)

    # Remove tatweel (kashida)
    text = text.replace("\u0640", "")

    # Remove diacritics (tashkeel)
    text = re.sub(r"[\u064B-\u065F]", "", text)

    return text


def detect_language(text: str) -> str:
    """
    Detect primary language of text.

    كشف اللغة الأساسية للنص

    Args:
        text: Text to analyze

    Returns:
        Language code ("ar", "en", or "mixed")
    """
    if not text:
        return "en"

    arabic_pattern = re.compile(r"[\u0600-\u06FF]")
    arabic_chars = len(arabic_pattern.findall(text))
    total_chars = len(re.sub(r"\s", "", text))

    if total_chars == 0:
        return "en"

    arabic_ratio = arabic_chars / total_chars

    if arabic_ratio > 0.5:
        return "ar"
    elif arabic_ratio > 0.2:
        return "mixed"
    else:
        return "en"


# ============================================================================
# RESPONSE VALIDATION
# ============================================================================


def validate_response_format(
    text: str,
    expected_format: str,
) -> tuple[bool, str | None]:
    """
    Validate that response matches expected format.

    التحقق من تطابق الاستجابة مع التنسيق المتوقع

    Args:
        text: Response text
        expected_format: Expected format ("json", "list", "text")

    Returns:
        Tuple of (is_valid, error_message)
    """
    if expected_format == "json":
        result = extract_json(text)
        if not result.success:
            return False, result.error
        return True, None

    elif expected_format == "list":
        items = parse_numbered_list(text) or parse_bullet_list(text)
        if not items:
            return False, "No list items found in response"
        return True, None

    elif expected_format == "text":
        if not text.strip():
            return False, "Empty response"
        return True, None

    else:
        return True, None


def ensure_type(value: Any, expected_type: type[T], default: T) -> T:
    """
    Ensure value is of expected type.

    التأكد من أن القيمة من النوع المتوقع

    Args:
        value: Value to check
        expected_type: Expected type
        default: Default value if type doesn't match

    Returns:
        Value cast to expected type, or default
    """
    if isinstance(value, expected_type):
        return value
    try:
        return expected_type(value)
    except (ValueError, TypeError):
        return default
