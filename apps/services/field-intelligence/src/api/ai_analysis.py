"""
Field AI Analysis — Multi-Agent Agricultural Intelligence
تحليل الحقول بالذكاء الاصطناعي — وكلاء متعددون متوازيون

Runs three Anthropic Claude agents in parallel:
  1. Vegetation Analyst  — interprets the CDSE satellite index values
  2. Weather Analyst      — interprets OpenWeather + OpenMeteo conditions
  3. Recommendations Agent — synthesizes all raw data into actions

Returns structured bullet-point analysis in EN/AR.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

ai_router = APIRouter()

# ── Anthropic client (lazy, shared) ──────────────────────────────────────────

_anthropic_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set in environment")
        _anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
    return _anthropic_client


MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# ── Request / Response schemas ────────────────────────────────────────────────


class CdseStats(BaseModel):
    indice: str
    value: float | None = None
    minValue: float | None = None
    maxValue: float | None = None
    stdDev: float | None = None
    date: str = ""
    cloudCover: float | None = None


class WeatherData(BaseModel):
    temperature: float | None = None
    feelsLike: float | None = None
    humidity: float | None = None
    windSpeed: float | None = None
    windDirection: float | None = None
    precipitation: float | None = None
    description: str = ""
    pressure: float | None = None
    cloudCover: float | None = None
    visibility: float | None = None


class MeteoData(BaseModel):
    temperature2m: float | None = None
    relativeHumidity2m: float | None = None
    precipitation: float | None = None
    windSpeed10m: float | None = None
    soilMoisture0to1cm: float | None = None
    et0FaoEvapotranspiration: float | None = None
    surfacePressure: float | None = None
    cloudCover: float | None = None
    shortwaveRadiation: float | None = None


class FieldInfo(BaseModel):
    id: str
    name: str
    nameAr: str | None = None
    lat: float
    lng: float
    areaHa: float | None = None
    cropType: str | None = None
    soilType: str | None = None


class AnalyzeFieldRequest(BaseModel):
    field: FieldInfo
    cdse: CdseStats
    weather: WeatherData | None = None
    meteo: MeteoData | None = None
    indice: str = "NDVI"
    fetchedAt: str = ""


class AnalyzeFieldResponse(BaseModel):
    field_id: str
    indice: str
    current_status: list[str] = Field(description="Bullet-point current field status")
    recommendations: list[str] = Field(description="Bullet-point actionable recommendations")
    analyzed_at: str


# ── Prompt helpers ────────────────────────────────────────────────────────────

SYSTEM_PERSONA = """You are Dr. Khalid Al-Rashidi, a Senior Agricultural Specialist with 25 years of expertise in precision agriculture, remote sensing, and crop management across the Middle East and North Africa. You hold a PhD in Agronomy from Jordan University of Science and Technology and have worked extensively with smallholder farmers across Yemen, Saudi Arabia, and Egypt.

Your expertise spans:
- Satellite remote sensing indices (NDVI, EVI, NDWI, NDMI, SAVI, NBR, BSI, etc.) and their agronomic interpretation
- Crop stress detection: water stress, nutrient deficiency, pest/disease pressure, salinity
- Weather-crop interaction: evapotranspiration, heat stress, frost risk, precipitation efficiency
- Soil moisture dynamics, irrigation scheduling, and water use efficiency
- Climate-smart agriculture practices for arid and semi-arid regions
- Arabic and English bilingual field communications

You provide precise, actionable, evidence-based analysis. Your tone is professional yet accessible to farmers. You always quantify findings where possible, state confidence levels, and flag critical risks clearly."""


def _build_vegetation_prompt(req: AnalyzeFieldRequest) -> str:
    cdse = req.cdse
    field = req.field
    val_str = f"{cdse.value:.4f}" if cdse.value is not None else "unavailable"
    range_str = (
        f"(min={cdse.minValue:.4f}, max={cdse.maxValue:.4f}, σ={cdse.stdDev:.4f})"
        if cdse.value is not None and cdse.minValue is not None
        else ""
    )

    return f"""<task>
Analyze the satellite index data for an agricultural field and produce a concise vegetation/land-cover status report.

<field_context>
Field name: {field.name} ({field.nameAr or 'N/A'})
Location: {field.lat:.4f}°N, {field.lng:.4f}°E
Area: {field.areaHa or 'unknown'} ha
Crop type: {field.cropType or 'unknown'}
Soil type: {field.soilType or 'unknown'}
</field_context>

<cdse_data>
Index: {cdse.indice}
Mean value: {val_str} {range_str}
Data date: {cdse.date}
Cloud cover: {f"{cdse.cloudCover:.1f}%" if cdse.cloudCover is not None else "unknown"}
</cdse_data>

Produce EXACTLY 4–6 concise bullet points describing:
1. What the {cdse.indice} value means agronomically for this field RIGHT NOW
2. Vegetation health category (critical/stressed/moderate/healthy/excellent) with justification
3. Detected stress signals or anomalies (water, nutrient, disease, senescence)
4. Spatial variability insight from min/max range if available
5. Confidence in assessment (factor in cloud cover, data age)

Format: Plain bullet points starting with "•". Be specific and quantitative. No headers. Max 120 words per bullet.
</task>"""


def _build_weather_prompt(req: AnalyzeFieldRequest) -> str:
    w = req.weather
    m = req.meteo
    field = req.field

    weather_block = ""
    if w:
        weather_block = f"""
OpenWeather (current):
  Temperature: {w.temperature}°C (feels like {w.feelsLike}°C)
  Humidity: {w.humidity}%
  Wind: {w.windSpeed} m/s at {w.windDirection}°
  Precipitation (1h): {w.precipitation} mm
  Cloud cover: {w.cloudCover}%
  Pressure: {w.pressure} hPa
  Visibility: {w.visibility} km
  Conditions: {w.description}"""

    meteo_block = ""
    if m:
        meteo_block = f"""
OpenMeteo (current):
  Temperature 2m: {m.temperature2m}°C
  Relative humidity 2m: {m.relativeHumidity2m}%
  Precipitation: {m.precipitation} mm
  Wind speed 10m: {m.windSpeed10m} m/s
  Soil moisture (0–1 cm): {m.soilMoisture0to1cm} m³/m³
  ET₀ (FAO-56): {m.et0FaoEvapotranspiration} mm/day
  Surface pressure: {m.surfacePressure} hPa
  Cloud cover: {m.cloudCover}%
  Shortwave radiation: {m.shortwaveRadiation} W/m²"""

    return f"""<task>
Analyze the weather and agro-meteorological conditions for the following agricultural field.

<field_context>
Field: {field.name}, Crop: {field.cropType or 'unknown'}, Area: {field.areaHa or '?'} ha
Location: {field.lat:.4f}°N, {field.lng:.4f}°E
</field_context>

<weather_data>{weather_block or '  No OpenWeather data available'}{meteo_block or '  No OpenMeteo data available'}
</weather_data>

Produce EXACTLY 4–6 concise bullet points covering:
1. Current weather suitability for agricultural operations (field work, spraying, harvesting)
2. Evapotranspiration load and irrigation urgency based on ET₀
3. Soil moisture status and implications for root uptake
4. Heat/cold/wind stress risks for the crop
5. Precipitation adequacy vs. crop water demand
6. Any weather-related pest/disease risk (humidity, temperature conducive to fungal/bacterial issues)

Format: Plain bullet points starting with "•". Quantitative where possible. No headers. Max 120 words per bullet.
</task>"""


def _build_recommendations_prompt(req: AnalyzeFieldRequest) -> str:
    cdse = req.cdse
    w = req.weather
    m = req.meteo
    field = req.field

    data_summary = f"""
Field: {field.name}, Crop: {field.cropType or 'unknown'}, Area: {field.areaHa or '?'} ha
Index {cdse.indice}: {f"{cdse.value:.4f}" if cdse.value is not None else 'N/A'}
Temperature: {w.temperature if w else (m.temperature2m if m else 'N/A')}°C
Humidity: {w.humidity if w else (m.relativeHumidity2m if m else 'N/A')}%
Soil moisture (0–1 cm): {m.soilMoisture0to1cm if m else 'N/A'} m³/m³
ET₀: {m.et0FaoEvapotranspiration if m else 'N/A'} mm/day
Precipitation (recent): {w.precipitation if w else (m.precipitation if m else 'N/A')} mm
Wind: {w.windSpeed if w else (m.windSpeed10m if m else 'N/A')} m/s
Cloud cover: {w.cloudCover if w else (m.cloudCover if m else 'N/A')}%"""

    return f"""<task>
You are advising a farmer on immediate and near-term actions for their agricultural field based on satellite index and weather data.

<all_field_data>{data_summary}
</all_field_data>

Produce EXACTLY 5–7 actionable recommendation bullet points. Each recommendation must be:
- Specific and immediately executable (within 24–72 hours where critical, 1–2 weeks for planning)
- Tied directly to at least one data point from the field data above
- Include timing, quantity/rate, or method where applicable
- Flagged with priority: [URGENT] [HIGH] [MEDIUM] [LOW]

Cover at minimum: irrigation decision, fertilization/nutrition, crop protection, field operations timing, monitoring actions.

Format: Plain bullet points starting with "•". No headers. Max 150 words per bullet.
</task>"""


# ── Agent runners ─────────────────────────────────────────────────────────────


async def _run_agent(system: str, user_prompt: str, max_tokens: int = 800) -> str:
    """Call Claude claude-sonnet with extended thinking disabled for fast parallel execution."""
    client = _get_client()
    try:
        msg = await client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return msg.content[0].text if msg.content else ""
    except Exception as exc:
        logger.error("Anthropic API call failed: %s", exc)
        raise


def _parse_bullets(text: str) -> list[str]:
    """Extract bullet-point lines from Claude response."""
    bullets = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("•"):
            bullet = stripped[1:].strip()
            if bullet:
                bullets.append(bullet)
        elif stripped.startswith("-") or stripped.startswith("*"):
            bullet = stripped[1:].strip()
            if bullet and len(bullet) > 15:
                bullets.append(bullet)
    # Fallback: split by double newline paragraphs if no bullets found
    if not bullets:
        for para in text.split("\n\n"):
            para = para.strip()
            if para and len(para) > 20:
                bullets.append(para)
    return bullets[:8]  # cap at 8


# ── Endpoint ─────────────────────────────────────────────────────────────────


@ai_router.post(
    "/analyze/field",
    response_model=AnalyzeFieldResponse,
    summary="AI field analysis",
    description="Multi-agent Claude analysis: vegetation health + weather impact + recommendations",
    tags=["AI Analysis"],
)
async def analyze_field(req: AnalyzeFieldRequest) -> AnalyzeFieldResponse:
    """
    Run three Claude agents in parallel:
    - Agent 1: Vegetation/CDSE index analysis → contributes to current_status
    - Agent 2: Weather/agro-meteorological analysis → contributes to current_status
    - Agent 3: Actionable recommendations based on all raw data
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="AI analysis service not configured: ANTHROPIC_API_KEY missing",
        )

    veg_prompt = _build_vegetation_prompt(req)
    weather_prompt = _build_weather_prompt(req)
    reco_prompt = _build_recommendations_prompt(req)

    try:
        veg_task = _run_agent(SYSTEM_PERSONA, veg_prompt, max_tokens=600)
        weather_task = _run_agent(SYSTEM_PERSONA, weather_prompt, max_tokens=600)
        reco_task = _run_agent(SYSTEM_PERSONA, reco_prompt, max_tokens=900)

        # Run all three agents in parallel
        veg_text, weather_text, reco_text = await asyncio.gather(
            veg_task, weather_task, reco_task
        )

    except Exception as exc:
        logger.error("Multi-agent analysis failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {exc}",
        )

    current_status_bullets = _parse_bullets(veg_text) + _parse_bullets(weather_text)
    recommendation_bullets = _parse_bullets(reco_text)

    from datetime import datetime, timezone

    return AnalyzeFieldResponse(
        field_id=req.field.id,
        indice=req.indice,
        current_status=current_status_bullets,
        recommendations=recommendation_bullets,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )
