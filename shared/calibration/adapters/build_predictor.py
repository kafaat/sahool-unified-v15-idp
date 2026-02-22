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

    This is a placeholder — wire the actual DB queries for production.

    Steps:
      1. Load soil profile for field
      2. Load sowing date for season
      3. Load weather series (from weather_service cache or precomputed table)
      4. Determine crop type
      5. Build predictor

    Args:
        tenant_id: Tenant UUID string.
        field_id: Field UUID string.
        season_id: Season/campaign UUID string.
        pool: asyncpg connection pool.

    Returns:
        CropGrowthPredictor ready for calibration.
    """
    # TODO: Replace with actual DB queries
    # soil = await _load_soil_profile(pool, tenant_id, field_id)
    # sowing = await _load_sowing_date(pool, tenant_id, field_id, season_id)
    # weather = await _load_weather_series(pool, tenant_id, field_id, sowing, end)
    # crop_type = await _load_crop_type(pool, tenant_id, field_id, season_id)

    logger.warning(
        "build_predictor_from_db_placeholder",
        tenant_id=tenant_id,
        field_id=field_id,
        season_id=season_id,
        msg="Using default soil/weather — replace with real DB queries",
    )

    soil = SoilProfile()
    sowing = date(2026, 1, 1)

    # Stub weather: constant mild conditions
    from datetime import timedelta

    weather_series = [
        DailyWeather(
            date=sowing + timedelta(days=d),
            tmax_c=28.0,
            tmin_c=14.0,
            solar_radiation_mj_m2=18.0,
            relative_humidity_pct=55.0,
            wind_speed_m_s=2.0,
            precipitation_mm=0.0,
        )
        for d in range(370)
    ]

    return build_predictor_from_config(
        weather_series=weather_series,
        soil_profile=soil,
        sowing_date=sowing,
        crop_type=CropType.WHEAT,
    )
