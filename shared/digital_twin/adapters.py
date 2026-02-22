# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Digital Twin Adapters - محولات التوأم الرقمي
===============================================
Converters between external service data and twin pipeline domain objects.

Adapters:
  - Weather service → DailyWeather
  - Satellite/NDVI → FieldObservation (LAI TimestampedObservation)
  - Calibration parameter set → CropParameters
  - IoT soil sensor → SoilProfile update
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

import structlog

from shared.digital_twin.models import FieldObservation, ObservationSource, ObservationType
from shared.process_models.models import (
    CropParameters,
    CropType,
    DailyWeather,
    SoilProfile,
    SoilTextureClass,
)

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Weather → DailyWeather
# ---------------------------------------------------------------------------


def weather_payload_to_daily(payload: dict[str, Any]) -> DailyWeather:
    """
    Convert a weather-service NATS payload or API response to DailyWeather.
    تحويل بيانات خدمة الطقس إلى كائن الطقس اليومي.

    Expected keys (flexible — uses defaults for missing):
      day/date, tmax_c/temp_max, tmin_c/temp_min,
      solar_radiation_mj_m2/solar_rad, relative_humidity_pct/humidity,
      wind_speed_m_s/wind_speed, precipitation_mm/rain_mm
    """
    # Date parsing
    raw_date = payload.get("day") or payload.get("date") or payload.get("forecast_date")
    if isinstance(raw_date, str):
        day = date.fromisoformat(raw_date[:10])
    elif isinstance(raw_date, (date, datetime)):
        day = raw_date if isinstance(raw_date, date) else raw_date.date()
    else:
        day = date.today()

    return DailyWeather(
        date=day,
        tmax_c=float(payload.get("tmax_c") or payload.get("temp_max") or 30.0),
        tmin_c=float(payload.get("tmin_c") or payload.get("temp_min") or 15.0),
        solar_radiation_mj_m2=float(
            payload.get("solar_radiation_mj_m2")
            or payload.get("solar_rad")
            or 18.0
        ),
        relative_humidity_pct=float(
            payload.get("relative_humidity_pct")
            or payload.get("humidity")
            or 55.0
        ),
        wind_speed_m_s=float(
            payload.get("wind_speed_m_s") or payload.get("wind_speed") or 2.0
        ),
        precipitation_mm=float(
            payload.get("precipitation_mm") or payload.get("rain_mm") or 0.0
        ),
    )


def weather_series_from_rows(rows: list[dict[str, Any]]) -> list[DailyWeather]:
    """Convert a list of weather rows to DailyWeather series (sorted by date)."""
    series = [weather_payload_to_daily(r) for r in rows]
    series.sort(key=lambda w: w.date)
    return series


# ---------------------------------------------------------------------------
# Satellite NDVI → FieldObservation / TimestampedObservation
# ---------------------------------------------------------------------------


def ndvi_to_field_observation(
    payload: dict[str, Any],
    *,
    tenant_id: Any,
    field_id: Any,
) -> FieldObservation:
    """
    Convert an NDVI computation result into a FieldObservation for assimilation.
    تحويل نتيجة حساب NDVI إلى رصد ميداني للاستيعاب.

    Expected payload keys: mean_ndvi/value, quality/cloud_cover, ts/date
    """
    ts_raw = payload.get("ts") or payload.get("date") or payload.get("acquisition_date")
    if isinstance(ts_raw, str):
        ts = datetime.fromisoformat(ts_raw)
    elif isinstance(ts_raw, datetime):
        ts = ts_raw
    else:
        from datetime import timezone
        ts = datetime.now(timezone.utc)

    ndvi_value = float(payload.get("mean_ndvi") or payload.get("value") or payload.get("ndvi", 0.0))

    # Quality: invert cloud_cover (0=clear → 1.0 quality, 1=cloudy → 0.0)
    cloud_cover = float(payload.get("cloud_cover", 0.1))
    quality = max(0.0, min(1.0, 1.0 - cloud_cover))
    quality = float(payload.get("quality", quality))

    return FieldObservation(
        tenant_id=tenant_id,
        field_id=field_id,
        ts=ts,
        source=ObservationSource.SENTINEL_2,
        obs_type=ObservationType.NDVI,
        value=ndvi_value,
        quality=quality,
        meta={
            "source_service": "vegetation-analysis-service",
            "cloud_cover": cloud_cover,
            **{k: v for k, v in payload.items() if k not in ("mean_ndvi", "value", "ts", "date")},
        },
    )


def ndvi_to_lai_estimate(ndvi: float) -> float:
    """
    Convert NDVI to LAI using Beer-Lambert approximation.
    تحويل NDVI إلى مؤشر مساحة الورقة باستخدام تقريب بير-لامبرت.

    LAI ≈ -ln(1 - NDVI) / k_ext  (k_ext ≈ 0.5 for most crops)
    """
    import math
    ndvi_clamped = max(0.01, min(0.98, ndvi))
    k_ext = 0.5
    return -math.log(1.0 - ndvi_clamped) / k_ext


# ---------------------------------------------------------------------------
# Calibration → CropParameters
# ---------------------------------------------------------------------------


def calibrated_params_to_crop(
    parameters: dict[str, Any],
    *,
    crop_type: CropType = CropType.WHEAT,
    base: CropParameters | None = None,
) -> CropParameters:
    """
    Merge calibrated parameter values onto a CropParameters base.
    دمج قيم المعاملات المعايرة على أساس CropParameters.

    Only overrides fields that exist in ``parameters``.
    Unrecognized keys are silently ignored.
    """
    if isinstance(parameters, str):
        parameters = json.loads(parameters)

    b = base or CropParameters(crop_type=crop_type)

    return CropParameters(
        crop_type=crop_type,
        rue_g_mj=float(parameters.get("rue_g_mj", b.rue_g_mj)),
        k_extinction=float(parameters.get("k_extinction", b.k_extinction)),
        base_temp_c=float(parameters.get("base_temp_c", b.base_temp_c)),
        gdd_maturity=float(parameters.get("gdd_maturity", b.gdd_maturity)),
        max_lai=float(parameters.get("max_lai", b.max_lai)),
        harvest_index=float(parameters.get("harvest_index", b.harvest_index)),
        n_requirement_kg_per_ton=float(
            parameters.get("n_requirement_kg_per_ton", b.n_requirement_kg_per_ton)
        ),
        root_depth_max_m=float(parameters.get("root_depth_max_m", b.root_depth_max_m)),
        sla_cm2_g=float(parameters.get("sla_cm2_g", b.sla_cm2_g)),
    )


# ---------------------------------------------------------------------------
# IoT Soil Sensor → SoilProfile
# ---------------------------------------------------------------------------


def soil_sensor_to_profile(
    payload: dict[str, Any],
    *,
    base: SoilProfile | None = None,
) -> SoilProfile:
    """
    Update SoilProfile from IoT soil sensor data.
    تحديث ملف التربة من بيانات حساس التربة.

    Expected keys: field_capacity, wilting_point, texture, depth_m
    """
    b = base or SoilProfile()
    texture_map = {t.value: t for t in SoilTextureClass}

    return SoilProfile(
        field_capacity_mm_per_m=float(
            payload.get("field_capacity") or payload.get("field_capacity_mm_per_m") or b.field_capacity_mm_per_m
        ),
        wilting_point_mm_per_m=float(
            payload.get("wilting_point") or payload.get("wilting_point_mm_per_m") or b.wilting_point_mm_per_m
        ),
        saturation_mm_per_m=float(
            payload.get("saturation") or payload.get("saturation_mm_per_m") or b.saturation_mm_per_m
        ),
        depth_m=float(payload.get("depth_m", b.depth_m)),
        texture=texture_map.get(
            payload.get("texture", b.texture.value if hasattr(b.texture, "value") else "loam"),
            SoilTextureClass.LOAM,
        ),
    )
