# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Crop Growth Model Adapter for Calibration
==========================================
محوّل نموذج نمو المحاصيل للمعايرة

Wraps ``CropGrowthEngine.simulate()`` so the CalibrationEngine can optimise
crop parameters against observed LAI, biomass and soil moisture time-series.

Adapts the notes-specification to the **actual** SAHOOL codebase:
  • CropParameters field names: ``rue_g_mj``, ``k_extinction``, ``gdd_emergence``, etc.
  • DailyWeather from ``shared.process_models.models``
  • FieldDailyState from ``shared.digital_twin.models`` (Pydantic, not dataclass)
  • CropGrowthEngine.simulate() is a batch runner returning ModelResult with daily_log

The predictor interface consumed by CalibrationEngine::

    predictor(theta, targets) -> {
        "LAI": {"YYYY-MM-DD": yhat, ...},
        "biomass": {"YYYY-MM-DD": yhat, ...},
        "soil_moisture": {"YYYY-MM-DD": yhat, ...},
    }
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Protocol

import structlog

from shared.calibration.types import CalibrationTarget
from shared.process_models.models import (
    CropParameters,
    DailyWeather,
    SoilProfile,
)

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_date(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def _date_str(d: date) -> str:
    return d.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Weather provider protocol
# ---------------------------------------------------------------------------


class WeatherProvider(Protocol):
    """
    Callable that returns DailyWeather for a given date string.
    مزود الطقس: يعيد بيانات الطقس اليومية لتاريخ معين.
    """

    def __call__(self, day: str) -> DailyWeather: ...


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CropGrowthPredictorConfig:
    """
    Controls prediction runtime vs fidelity.
    يتحكم في وقت التشغيل مقابل الدقة.
    """

    spinup_days: int = 0  # Warm-up before first obs date | أيام الإحماء
    max_days: int = 370  # Guard against runaway loops | حد أقصى للأيام


# ---------------------------------------------------------------------------
# Parameter mapping
# ---------------------------------------------------------------------------


_THETA_BOUNDS: dict[str, tuple[float, float]] = {
    "rue_g_mj": (0.1, 5.0),
    "lai_max": (0.2, 15.0),
    "k_extinction": (0.1, 1.2),
    "gdd_emergence": (0.0, 2000.0),
    "gdd_heading": (0.0, 5000.0),
    "gdd_maturity": (0.0, 8000.0),
    "base_temp_c": (-5.0, 15.0),
    "harvest_index": (0.1, 0.65),
    "crop_coefficient_kcb_mid": (0.3, 1.4),
}


def _clip(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def theta_to_crop_params(
    theta: dict[str, float],
    base_params: CropParameters | None = None,
) -> CropParameters:
    """
    Map calibration theta dict → CropParameters.
    This is the **only** mapping point.

    Parameters not present in theta keep their base_params defaults.
    All values are clipped to physically plausible bounds.
    """
    bp = base_params or CropParameters()

    def get(name: str, default: float) -> float:
        val = float(theta.get(name, default))
        bounds = _THETA_BOUNDS.get(name)
        if bounds:
            return _clip(val, bounds[0], bounds[1])
        return val

    return CropParameters(
        crop_type=bp.crop_type,
        name_en=bp.name_en,
        name_ar=bp.name_ar,
        rue_g_mj=get("rue_g_mj", bp.rue_g_mj),
        lai_max=get("lai_max", bp.lai_max),
        k_extinction=get("k_extinction", bp.k_extinction),
        gdd_emergence=get("gdd_emergence", bp.gdd_emergence),
        gdd_heading=get("gdd_heading", bp.gdd_heading),
        gdd_maturity=get("gdd_maturity", bp.gdd_maturity),
        base_temp_c=get("base_temp_c", bp.base_temp_c),
        harvest_index=get("harvest_index", bp.harvest_index),
        crop_coefficient_kcb_mid=get("crop_coefficient_kcb_mid", bp.crop_coefficient_kcb_mid),
        water_productivity_kg_m3=bp.water_productivity_kg_m3,
        n_requirement_kg_per_ton=bp.n_requirement_kg_per_ton,
        p_requirement_kg_per_ton=bp.p_requirement_kg_per_ton,
        k_requirement_kg_per_ton=bp.k_requirement_kg_per_ton,
    )


# ---------------------------------------------------------------------------
# Predictor
# ---------------------------------------------------------------------------


class CropGrowthPredictor:
    """
    Adapter that runs CropGrowthEngine over a timeline and returns
    predictions keyed by observation dates.

    محوّل يشغّل محرك نمو المحاصيل ويعيد التنبؤات حسب تواريخ الأرصاد.

    Expected output for CalibrationEngine::

        {
            "LAI": {"2026-02-15": 1.3, "2026-03-10": 3.8, ...},
            "biomass": {"2026-02-15": 120.5, ...},
            "soil_moisture": {"2026-02-15": 185.0, ...},
        }
    """

    def __init__(
        self,
        *,
        weather_provider: WeatherProvider,
        soil_profile: SoilProfile,
        sowing_date: date,
        base_crop_params: CropParameters | None = None,
        n_supply_kg_ha: float = 80.0,
        config: CropGrowthPredictorConfig | None = None,
    ) -> None:
        self._weather_provider = weather_provider
        self._soil = soil_profile
        self._sowing_date = sowing_date
        self._base_params = base_crop_params or CropParameters()
        self._n_supply = n_supply_kg_ha
        self._config = config or CropGrowthPredictorConfig()

    def _timeline_bounds(self, targets: list[CalibrationTarget]) -> tuple[date, date]:
        """Compute start/end dates from targets + config."""
        all_dates: list[str] = []
        for t in targets:
            for o in t.observations:
                all_dates.append(o.t)
        if not all_dates:
            raise ValueError("No observation dates found in targets")

        # Start at sowing or spinup before first obs, whichever is earlier
        first_obs = _parse_date(min(all_dates))
        end = _parse_date(max(all_dates))
        start = min(self._sowing_date, first_obs - timedelta(days=self._config.spinup_days))

        if (end - start).days > self._config.max_days:
            raise ValueError(
                f"Calibration window too large: {(end - start).days} days "
                f"(max {self._config.max_days})"
            )
        return start, end

    def _build_weather_series(self, start: date, end: date) -> list[DailyWeather]:
        """Build ordered weather series from provider."""
        series = []
        cur = start
        while cur <= end:
            w = self._weather_provider(_date_str(cur))
            series.append(w)
            cur += timedelta(days=1)
        return series

    def _extract_daily_values(
        self, daily_log: list[dict], start: date
    ) -> dict[str, dict[str, float]]:
        """
        Convert CropGrowthEngine daily_log (day-indexed) → date-keyed dicts.

        daily_log entries have:
          {day: int, stage: str, dvs: float, gdd_cum: float,
           biomass_g_m2: float, lai: float, ws: float, wn: float}
        """
        values: dict[str, dict[str, float]] = {"LAI": {}, "biomass": {}, "soil_moisture": {}}

        for entry in daily_log:
            day_idx = entry["day"]  # 1-based
            entry_date = start + timedelta(days=day_idx - 1)
            ds = _date_str(entry_date)

            if "lai" in entry:
                values["LAI"][ds] = float(entry["lai"])
            if "biomass_g_m2" in entry:
                # Convert g/m² → kg/ha (1 g/m² = 10 kg/ha)
                values["biomass"][ds] = float(entry["biomass_g_m2"]) * 10.0

        return values

    def predict(
        self, theta: dict[str, float], targets: list[CalibrationTarget]
    ) -> dict[str, dict[str, float]]:
        """
        Main interface consumed by CalibrationEngine.
        الواجهة الرئيسية التي يستهلكها محرك المعايرة.

        Args:
            theta: Parameter values to evaluate.
            targets: Calibration targets with observation dates/values.

        Returns:
            Predicted values keyed by variable and date.
        """
        if not targets:
            return {}

        # Lazy import to avoid circular dependencies
        from shared.process_models.crop_growth import CropGrowthEngine

        start, end = self._timeline_bounds(targets)
        weather_series = self._build_weather_series(start, end)

        # Map theta → CropParameters (clipped to physical bounds)
        crop_params = theta_to_crop_params(theta, self._base_params)

        # Run batch simulation
        engine = CropGrowthEngine()
        result = engine.simulate(
            crop=crop_params,
            soil=self._soil,
            weather_series=weather_series,
            sowing_date=start,
            n_supply_kg_ha=self._n_supply,
        )

        if not result.success:
            logger.warning("calibration_simulation_failed", message=result.message)
            return {}

        daily_log = result.metadata.get("daily_log", [])
        all_values = self._extract_daily_values(daily_log, start)

        # Filter to only requested observation dates
        out: dict[str, dict[str, float]] = {}
        for tgt in targets:
            var = tgt.variable
            var_values = all_values.get(var, {})
            if not var_values:
                continue
            out.setdefault(var, {})
            for obs in tgt.observations:
                if obs.t in var_values:
                    out[var][obs.t] = var_values[obs.t]

        return {k: v for k, v in out.items() if v}
