"""Utility functions for web scraping.

This module provides helper functions for HTML parsing, data cleaning,
and date parsing with support for Arabic and English formats.
"""

from __future__ import annotations

import html
import re
import unicodedata
from datetime import datetime, timedelta
from typing import Any

# Arabic to English digit mapping
ARABIC_DIGITS: dict[str, str] = {
    "\u0660": "0",  # ٠
    "\u0661": "1",  # ١
    "\u0662": "2",  # ٢
    "\u0663": "3",  # ٣
    "\u0664": "4",  # ٤
    "\u0665": "5",  # ٥
    "\u0666": "6",  # ٦
    "\u0667": "7",  # ٧
    "\u0668": "8",  # ٨
    "\u0669": "9",  # ٩
}

# Arabic month names to numbers
ARABIC_MONTHS: dict[str, int] = {
    "يناير": 1,
    "فبراير": 2,
    "مارس": 3,
    "أبريل": 4,
    "ابريل": 4,
    "مايو": 5,
    "يونيو": 6,
    "يوليو": 7,
    "أغسطس": 8,
    "اغسطس": 8,
    "سبتمبر": 9,
    "أكتوبر": 10,
    "اكتوبر": 10,
    "نوفمبر": 11,
    "ديسمبر": 12,
    # Alternative names
    "كانون الثاني": 1,
    "شباط": 2,
    "آذار": 3,
    "نيسان": 4,
    "أيار": 5,
    "حزيران": 6,
    "تموز": 7,
    "آب": 8,
    "أيلول": 9,
    "تشرين الأول": 10,
    "تشرين الثاني": 11,
    "كانون الأول": 12,
}

# English month abbreviations
ENGLISH_MONTHS: dict[str, int] = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

# Arabic relative time expressions
ARABIC_RELATIVE_TIME: dict[str, timedelta] = {
    "اليوم": timedelta(days=0),
    "أمس": timedelta(days=-1),
    "امس": timedelta(days=-1),
    "غدا": timedelta(days=1),
    "غداً": timedelta(days=1),
    "منذ ساعة": timedelta(hours=-1),
    "منذ ساعتين": timedelta(hours=-2),
    "منذ يوم": timedelta(days=-1),
    "منذ يومين": timedelta(days=-2),
    "منذ أسبوع": timedelta(weeks=-1),
    "منذ اسبوع": timedelta(weeks=-1),
}


def convert_arabic_digits(text: str) -> str:
    """Convert Arabic-Indic digits to Western Arabic digits.

    Args:
        text: Text containing Arabic-Indic digits.

    Returns:
        Text with Western Arabic digits.

    Example:
        >>> convert_arabic_digits("١٢٣")
        '123'
    """
    result = text
    for arabic, western in ARABIC_DIGITS.items():
        result = result.replace(arabic, western)
    return result


def clean_text(text: str, preserve_newlines: bool = False) -> str:
    """Clean and normalize text content.

    Args:
        text: Raw text to clean.
        preserve_newlines: Whether to preserve newline characters.

    Returns:
        Cleaned text.
    """
    if not text:
        return ""

    # Decode HTML entities
    text = html.unescape(text)

    # Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Convert Arabic digits
    text = convert_arabic_digits(text)

    # Remove zero-width characters
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)

    if preserve_newlines:
        # Normalize multiple newlines to single
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Normalize whitespace within lines
        lines = text.split("\n")
        lines = [" ".join(line.split()) for line in lines]
        text = "\n".join(lines)
    else:
        # Replace all whitespace with single space
        text = " ".join(text.split())

    return text.strip()


def extract_numbers(text: str) -> list[float]:
    """Extract all numbers from text.

    Args:
        text: Text containing numbers.

    Returns:
        List of extracted numbers.

    Example:
        >>> extract_numbers("Temperature: 25.5°C, Humidity: 60%")
        [25.5, 60.0]
    """
    # Convert Arabic digits first
    text = convert_arabic_digits(text)

    # Find all numbers (including decimals and negatives)
    pattern = r"-?\d+\.?\d*"
    matches = re.findall(pattern, text)

    return [float(m) for m in matches if m and m != "-"]


def extract_first_number(text: str) -> float | None:
    """Extract the first number from text.

    Args:
        text: Text containing a number.

    Returns:
        First number found or None.
    """
    numbers = extract_numbers(text)
    return numbers[0] if numbers else None


def parse_price(text: str) -> tuple[float, str] | None:
    """Parse price from text with currency detection.

    Args:
        text: Text containing price information.

    Returns:
        Tuple of (price, currency) or None.

    Example:
        >>> parse_price("السعر: 150 ريال")
        (150.0, 'SAR')
    """
    text = clean_text(text)
    text = convert_arabic_digits(text)

    # Currency patterns
    currency_patterns = [
        (r"(\d+\.?\d*)\s*(?:ريال|ر\.س|SAR)", "SAR"),
        (r"(?:ريال|ر\.س|SAR)\s*(\d+\.?\d*)", "SAR"),
        (r"(\d+\.?\d*)\s*(?:دولار|\$|USD)", "USD"),
        (r"(?:دولار|\$|USD)\s*(\d+\.?\d*)", "USD"),
        (r"(\d+\.?\d*)\s*(?:درهم|AED)", "AED"),
        (r"(\d+\.?\d*)\s*(?:دينار|KWD)", "KWD"),
        (r"(\d+\.?\d*)", "SAR"),  # Default to SAR
    ]

    for pattern, currency in currency_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                price = float(match.group(1))
                return (price, currency)
            except (ValueError, IndexError):
                continue

    return None


def parse_date(
    text: str,
    default_year: int | None = None,
    timezone_offset: int = 3,  # Saudi Arabia UTC+3
) -> datetime | None:
    """Parse date from text supporting Arabic and English formats.

    Args:
        text: Text containing date information.
        default_year: Year to use if not specified.
        timezone_offset: Timezone offset in hours.

    Returns:
        Parsed datetime or None.

    Example:
        >>> parse_date("15 يناير 2025")
        datetime.datetime(2025, 1, 15, 0, 0)
    """
    if not text:
        return None

    text = clean_text(text)
    text = convert_arabic_digits(text)
    now = datetime.now()
    default_year = default_year or now.year

    # Check for relative time expressions
    for expr, delta in ARABIC_RELATIVE_TIME.items():
        if expr in text:
            return now + delta

    # English relative time
    if "today" in text.lower():
        return now
    if "yesterday" in text.lower():
        return now - timedelta(days=1)
    if "tomorrow" in text.lower():
        return now + timedelta(days=1)

    # Try common date formats
    date_patterns = [
        # ISO format
        (r"(\d{4})-(\d{1,2})-(\d{1,2})", lambda m: (int(m[1]), int(m[2]), int(m[3]))),
        # DD/MM/YYYY
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", lambda m: (int(m[3]), int(m[2]), int(m[1]))),
        # DD-MM-YYYY
        (r"(\d{1,2})-(\d{1,2})-(\d{4})", lambda m: (int(m[3]), int(m[2]), int(m[1]))),
        # DD/MM/YY
        (
            r"(\d{1,2})/(\d{1,2})/(\d{2})",
            lambda m: (2000 + int(m[3]), int(m[2]), int(m[1])),
        ),
    ]

    for pattern, extractor in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                year, month, day = extractor(match.groups())
                return datetime(year, month, day)
            except (ValueError, IndexError):
                continue

    # Arabic month patterns
    for month_name, month_num in ARABIC_MONTHS.items():
        if month_name in text:
            # Try to find day and year
            day_match = re.search(r"(\d{1,2})", text)
            year_match = re.search(r"(\d{4})", text)

            day = int(day_match.group(1)) if day_match else 1
            year = int(year_match.group(1)) if year_match else default_year

            try:
                return datetime(year, month_num, day)
            except ValueError:
                continue

    # English month patterns
    for month_name, month_num in ENGLISH_MONTHS.items():
        if month_name in text.lower():
            day_match = re.search(r"(\d{1,2})", text)
            year_match = re.search(r"(\d{4})", text)

            day = int(day_match.group(1)) if day_match else 1
            year = int(year_match.group(1)) if year_match else default_year

            try:
                return datetime(year, month_num, day)
            except ValueError:
                continue

    return None


def parse_temperature(text: str) -> float | None:
    """Parse temperature from text.

    Args:
        text: Text containing temperature.

    Returns:
        Temperature in Celsius or None.

    Example:
        >>> parse_temperature("درجة الحرارة: 25°م")
        25.0
    """
    text = convert_arabic_digits(clean_text(text))

    # Patterns for temperature
    patterns = [
        r"(-?\d+\.?\d*)\s*°?\s*[Cc]",  # Celsius
        r"(-?\d+\.?\d*)\s*°?\s*[مم]",  # Arabic م = C
        r"(-?\d+\.?\d*)\s*درجة",  # Arabic "degrees"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    # Fahrenheit conversion
    f_match = re.search(r"(-?\d+\.?\d*)\s*°?\s*[Ff]", text)
    if f_match:
        try:
            f_temp = float(f_match.group(1))
            return round((f_temp - 32) * 5 / 9, 1)
        except ValueError:
            pass

    return None


def parse_percentage(text: str) -> float | None:
    """Parse percentage from text.

    Args:
        text: Text containing percentage.

    Returns:
        Percentage value (0-100) or None.
    """
    text = convert_arabic_digits(clean_text(text))

    patterns = [
        r"(\d+\.?\d*)\s*%",
        r"(\d+\.?\d*)\s*بالمائة",
        r"(\d+\.?\d*)\s*في المائة",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    return None


def extract_table_data(
    rows: list[list[str]],
    headers: list[str] | None = None,
) -> list[dict[str, str]]:
    """Convert table rows to list of dictionaries.

    Args:
        rows: List of row data (each row is a list of cell values).
        headers: Optional header names. If None, uses first row.

    Returns:
        List of dictionaries with cleaned data.
    """
    if not rows:
        return []

    if headers is None:
        headers = [clean_text(h) for h in rows[0]]
        data_rows = rows[1:]
    else:
        headers = [clean_text(h) for h in headers]
        data_rows = rows

    result = []
    for row in data_rows:
        if len(row) >= len(headers):
            row_dict = {}
            for i, header in enumerate(headers):
                row_dict[header] = clean_text(row[i]) if i < len(row) else ""
            result.append(row_dict)

    return result


def normalize_location(text: str) -> str:
    """Normalize location name (Arabic/English).

    Args:
        text: Location name.

    Returns:
        Normalized location name.
    """
    text = clean_text(text)

    # Common Saudi city name mappings
    city_mappings = {
        "الرياض": "Riyadh",
        "جدة": "Jeddah",
        "جده": "Jeddah",
        "مكة": "Makkah",
        "مكة المكرمة": "Makkah",
        "المدينة": "Madinah",
        "المدينة المنورة": "Madinah",
        "الدمام": "Dammam",
        "الخبر": "Khobar",
        "الظهران": "Dhahran",
        "تبوك": "Tabuk",
        "أبها": "Abha",
        "جازان": "Jazan",
        "حائل": "Hail",
        "القصيم": "Qassim",
        "بريدة": "Buraidah",
        "الطائف": "Taif",
        "نجران": "Najran",
        "الباحة": "Baha",
        "عرعر": "Arar",
        "سكاكا": "Sakaka",
        "الجوف": "Jouf",
    }

    # Check for Arabic name
    for arabic, english in city_mappings.items():
        if arabic in text:
            return english

    # Return original if no mapping found
    return text


def sanitize_filename(text: str, max_length: int = 100) -> str:
    """Create a safe filename from text.

    Args:
        text: Text to convert to filename.
        max_length: Maximum filename length.

    Returns:
        Safe filename string.
    """
    # Remove or replace unsafe characters
    text = clean_text(text)
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")

    if len(text) > max_length:
        text = text[:max_length].rsplit("_", 1)[0]

    return text or "unnamed"


def is_arabic_text(text: str) -> bool:
    """Check if text contains Arabic characters.

    Args:
        text: Text to check.

    Returns:
        True if text contains Arabic characters.
    """
    arabic_pattern = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
    return bool(arabic_pattern.search(text))


def detect_language(text: str) -> str:
    """Detect the primary language of text.

    Args:
        text: Text to analyze.

    Returns:
        Language code ('ar' for Arabic, 'en' for English).
    """
    if not text:
        return "en"

    # Count Arabic vs Latin characters
    arabic_count = len(
        re.findall(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", text)
    )
    latin_count = len(re.findall(r"[a-zA-Z]", text))

    return "ar" if arabic_count > latin_count else "en"


def merge_dict_lists(
    list1: list[dict[str, Any]],
    list2: list[dict[str, Any]],
    key: str,
) -> list[dict[str, Any]]:
    """Merge two lists of dictionaries by key.

    Args:
        list1: First list of dictionaries.
        list2: Second list of dictionaries.
        key: Key to merge on.

    Returns:
        Merged list with combined data.
    """
    merged = {item.get(key): item.copy() for item in list1}

    for item in list2:
        item_key = item.get(key)
        if item_key in merged:
            merged[item_key].update(item)
        else:
            merged[item_key] = item.copy()

    return list(merged.values())
