"""
SAHOOL Context Builder
Sprint 9: Unified field context aggregation

Combines data from multiple sources (NDVI, Weather, Soil, Field metadata)
into a structured context for LLM prompts.
"""

from __future__ import annotations

from typing import Any


def build_field_context(
    *,
    field: dict[str, Any],
    ndvi_summary: dict[str, Any] | None = None,
    weather: dict[str, Any] | None = None,
    soil: dict[str, Any] | None = None,
) -> str:
    """Build a unified field context string.

    Args:
        field: Field metadata (id, name, crop, etc.)
        ndvi_summary: NDVI summary data from ndvi_engine
        weather: Current/forecast weather data
        soil: Soil analysis data

    Returns:
        Formatted context string for LLM prompt
    """
    parts: list[str] = []

    # Field basics
    field_name = field.get("name", "غير معروف")
    field_id = field.get("id", "")
    crop = field.get("crop", "")
    area = field.get("area_hectares", "")

    parts.append(f"- الحقل: {field_name} (ID: {field_id})")
    if crop:
        parts.append(f"- المحصول: {crop}")
    if area:
        parts.append(f"- المساحة: {area} هكتار")

    # NDVI data
    if ndvi_summary:
        ndvi_mean = ndvi_summary.get("ndvi_mean", "غير متوفر")
        trend = ndvi_summary.get("trend", "غير متوفر")
        confidence = ndvi_summary.get("confidence_mean", "غير متوفر")
        parts.append(f"- NDVI: متوسط={ndvi_mean} اتجاه={trend} ثقة={confidence}")

    # Weather data
    if weather:
        summary = weather.get("summary", "")
        if summary:
            parts.append(f"- الطقس: {summary}")
        else:
            temp = weather.get("temperature", "")
            humidity = weather.get("humidity", "")
            if temp or humidity:
                parts.append(f"- الطقس: درجة الحرارة={temp}°C رطوبة={humidity}%")

    # Soil data
    if soil:
        summary = soil.get("summary", "")
        if summary:
            parts.append(f"- التربة: {summary}")
        else:
            ph = soil.get("ph", "")
            organic_matter = soil.get("organic_matter", "")
            if ph or organic_matter:
                parts.append(f"- التربة: pH={ph} مادة عضوية={organic_matter}%")

    return "\n".join(parts)


def build_minimal_context(field_id: str, field_name: str) -> str:
    """Build minimal context when full data is unavailable.

    Args:
        field_id: Field identifier
        field_name: Field name

    Returns:
        Minimal context string
    """
    return f"- الحقل: {field_name} (ID: {field_id})"
