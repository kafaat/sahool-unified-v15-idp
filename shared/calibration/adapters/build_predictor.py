# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Predictor Factory - مصنع المتنبئ
==================================
Factory functions for building CropGrowthPredictor instances from DB/config.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import structlog

from shared.calibration.adapters.crop_growth_adapter import (
    CropGrowthPredictor,
    CropGrowthPredictorConfig,
)
from shared.process_models.models import (
    CropParameters,
    CropType,
    DailyWeather,
    SoilProfile,
)

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# In-memory weather provider from pre-loaded series
# ---------------------------------------------------------------------------


def weather_provider_from_series(
    series: list[DailyWeather],
) -> Any:
    """
    Build a WeatherProvider callable from a pre-loaded list.
    بناء مزود طقس من قائمة مُحمّلة مسبقًا.

    Args:
        series: List of DailyWeather records (any order; indexed by date).

    Returns:
        Callable(day: str) -> DailyWeather
    """
    index = {w.date.isoformat(): w for w in series}

    def provider(day: str) -> DailyWeather:
        w = index.get(day)
        if w is None:
            raise KeyError(f"No weather data for {day}")
        return w

    return provider


# ---------------------------------------------------------------------------
# Factory: build from explicit configuration
# ---------------------------------------------------------------------------


def build_predictor_from_config(
    *,
    weather_series: list[DailyWeather],
    soil_profile: SoilProfile,
    sowing_date: date,
    crop_type: CropType = CropType.WHEAT,
    n_supply_kg_ha: float = 80.0,
    config: CropGrowthPredictorConfig | None = None,
) -> CropGrowthPredictor:
    """
    Build a CropGrowthPredictor from explicit configuration.
    بناء المتنبئ من تكوين صريح.

    Usage::

        predictor = build_predictor_from_config(
            weather_series=weather_data,
            soil_profile=SoilProfile(texture=SoilTextureClass.LOAM),
            sowing_date=date(2026, 1, 1),
            crop_type=CropType.WHEAT,
        )
        result = predictor.predict(theta={"rue_g_mj": 1.3}, targets=[...])
    """
    return CropGrowthPredictor(
        weather_provider=weather_provider_from_series(weather_series),
        soil_profile=soil_profile,
        sowing_date=sowing_date,
        base_crop_params=CropParameters(crop_type=crop_type),
        n_supply_kg_ha=n_supply_kg_ha,
        config=config or CropGrowthPredictorConfig(),
    )


# ---------------------------------------------------------------------------
# Factory: build from DB (placeholder for service integration)
# ---------------------------------------------------------------------------


async def _load_soil_profile(pool: Any, tenant_id: str, field_id: str) -> SoilProfile:
    """Load soil profile from field_soil_profile table."""
    from shared.process_models.models import SoilTextureClass

    sql = """
    SELECT field_capacity_mm_per_m, wilting_point_mm_per_m,
           saturation_mm_per_m, depth_m, texture
    FROM field_soil_profile
    WHERE tenant_id = $1 AND field_id = $2
    ORDER BY updated_at DESC
    LIMIT 1
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, tenant_id, field_id)

    if row is None:
        logger.warning("soil_profile_not_found", tenant_id=tenant_id, field_id=field_id)
        return SoilProfile()

    texture_map = {t.value: t for t in SoilTextureClass}
    return SoilProfile(
        field_capacity_mm_per_m=row["field_capacity_mm_per_m"],
        wilting_point_mm_per_m=row["wilting_point_mm_per_m"],
        saturation_mm_per_m=row.get("saturation_mm_per_m", 450.0),
        depth_m=row.get("depth_m", 0.6),
        texture=texture_map.get(row.get("texture", "loam"), SoilTextureClass.LOAM),
    )


async def _load_sowing_date(
    pool: Any, tenant_id: str, field_id: str, season_id: str
) -> date:
    """Load sowing date from field_season table."""
    sql = """
    SELECT sowing_date
    FROM field_season
    WHERE tenant_id = $1 AND field_id = $2 AND id = $3::uuid
    LIMIT 1
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, tenant_id, field_id, season_id)

    if row is None or row["sowing_date"] is None:
        logger.warning(
            "sowing_date_not_found",
            tenant_id=tenant_id, field_id=field_id, season_id=season_id,
        )
        return date(2026, 1, 1)
    return row["sowing_date"]


async def _load_crop_type(
    pool: Any, tenant_id: str, field_id: str, season_id: str
) -> CropType:
    """Load crop type from field_season table."""
    sql = """
    SELECT crop_type
    FROM field_season
    WHERE tenant_id = $1 AND field_id = $2 AND id = $3::uuid
    LIMIT 1
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, tenant_id, field_id, season_id)

    crop_map = {t.value: t for t in CropType}
    if row and row["crop_type"]:
        return crop_map.get(row["crop_type"], CropType.WHEAT)
    return CropType.WHEAT


async def _load_weather_series(
    pool: Any,
    tenant_id: str,
    field_id: str,
    sowing: date,
    end: date,
) -> list[DailyWeather]:
    """Load daily weather records from weather_daily cache table."""
    sql = """
    SELECT day, tmax_c, tmin_c, solar_radiation_mj_m2,
           relative_humidity_pct, wind_speed_m_s, precipitation_mm
    FROM weather_daily
    WHERE tenant_id = $1 AND field_id = $2
      AND day >= $3 AND day <= $4
    ORDER BY day
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, tenant_id, field_id, sowing, end)

    if not rows:
        logger.warning(
            "weather_series_not_found",
            tenant_id=tenant_id, field_id=field_id,
            sowing=str(sowing), end=str(end),
            msg="Falling back to synthetic mild weather",
        )
        from datetime import timedelta
        return [
            DailyWeather(
                date=sowing + timedelta(days=d),
                tmax_c=28.0, tmin_c=14.0,
                solar_radiation_mj_m2=18.0,
                relative_humidity_pct=55.0,
                wind_speed_m_s=2.0,
                precipitation_mm=0.0,
            )
            for d in range((end - sowing).days + 1)
        ]

    return [
        DailyWeather(
            date=r["day"],
            tmax_c=r["tmax_c"],
            tmin_c=r["tmin_c"],
            solar_radiation_mj_m2=r.get("solar_radiation_mj_m2", 18.0),
            relative_humidity_pct=r.get("relative_humidity_pct", 55.0),
            wind_speed_m_s=r.get("wind_speed_m_s", 2.0),
            precipitation_mm=r.get("precipitation_mm", 0.0),
        )
        for r in rows
    ]


async def build_predictor_from_db(
    *,
    tenant_id: str,
    field_id: str,
    season_id: str,
    pool: Any,  # asyncpg.Pool
) -> CropGrowthPredictor:
    """
    Build a CropGrowthPredictor by loading field configuration from DB.
    بناء المتنبئ عبر تحميل تكوين الحقل من قاعدة البيانات.

    Loads:
      1. Soil profile from ``field_soil_profile``
      2. Sowing date + crop type from ``field_season``
      3. Weather series from ``weather_daily``

    Falls back to defaults when tables are empty or missing.

    Args:
        tenant_id: Tenant UUID string.
        field_id: Field UUID string.
        season_id: Season/campaign UUID string.
        pool: asyncpg connection pool.

    Returns:
        CropGrowthPredictor ready for calibration.
    """
    from datetime import timedelta

    soil = await _load_soil_profile(pool, tenant_id, field_id)
    sowing = await _load_sowing_date(pool, tenant_id, field_id, season_id)
    crop_type = await _load_crop_type(pool, tenant_id, field_id, season_id)

    # Weather from sowing to sowing+365d
    end = sowing + timedelta(days=365)
    weather_series = await _load_weather_series(pool, tenant_id, field_id, sowing, end)

    logger.info(
        "build_predictor_from_db",
        tenant_id=tenant_id,
        field_id=field_id,
        season_id=season_id,
        crop_type=crop_type.value,
        sowing=str(sowing),
        weather_days=len(weather_series),
    )

    return build_predictor_from_config(
        weather_series=weather_series,
        soil_profile=soil,
        sowing_date=sowing,
        crop_type=crop_type,
    )
