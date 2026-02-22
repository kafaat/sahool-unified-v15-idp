# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit tests for the CropGrowthPredictor calibration adapter.
اختبارات وحدة لمحوّل نموذج نمو المحاصيل للمعايرة.

Tests the full integration: adapter → CropGrowthEngine → daily_log → predictions.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from shared.calibration.adapters.build_predictor import (
    build_predictor_from_config,
    weather_provider_from_series,
)
from shared.calibration.adapters.crop_growth_adapter import (
    CropGrowthPredictor,
    CropGrowthPredictorConfig,
    theta_to_crop_params,
)
from shared.calibration.engine import CalibrationEngine
from shared.calibration.types import (
    CalibrationObservation,
    CalibrationTarget,
    ParameterBound,
)
from shared.process_models.models import (
    CropParameters,
    CropType,
    DailyWeather,
    SoilProfile,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_weather_series(
    start: date, n_days: int = 200
) -> list[DailyWeather]:
    """Generate synthetic weather for testing."""
    return [
        DailyWeather(
            date=start + timedelta(days=d),
            tmax_c=30.0,
            tmin_c=15.0,
            solar_radiation_mj_m2=20.0,
            relative_humidity_pct=50.0,
            wind_speed_m_s=2.0,
            precipitation_mm=2.0 if d % 7 == 0 else 0.0,
        )
        for d in range(n_days)
    ]


@pytest.fixture
def sowing_date() -> date:
    return date(2026, 1, 1)


@pytest.fixture
def weather_series(sowing_date) -> list[DailyWeather]:
    return _make_weather_series(sowing_date, 200)


@pytest.fixture
def soil() -> SoilProfile:
    return SoilProfile()


@pytest.fixture
def predictor(weather_series, soil, sowing_date) -> CropGrowthPredictor:
    return build_predictor_from_config(
        weather_series=weather_series,
        soil_profile=soil,
        sowing_date=sowing_date,
        crop_type=CropType.WHEAT,
    )


@pytest.fixture
def lai_targets() -> list[CalibrationTarget]:
    """Synthetic LAI observations at 30-day intervals."""
    return [
        CalibrationTarget(
            variable="LAI",
            observations=[
                CalibrationObservation(t="2026-02-01", value=0.5, uncertainty=0.2),
                CalibrationObservation(t="2026-03-01", value=2.0, uncertainty=0.3),
                CalibrationObservation(t="2026-04-01", value=3.5, uncertainty=0.3),
                CalibrationObservation(t="2026-05-01", value=2.0, uncertainty=0.4),
            ],
        )
    ]


# ---------------------------------------------------------------------------
# theta_to_crop_params
# ---------------------------------------------------------------------------


class TestThetaToCropParams:
    def test_default_values(self):
        params = theta_to_crop_params({})
        assert params.rue_g_mj == 1.2  # CropParameters default
        assert params.k_extinction == 0.5
        assert params.crop_type == CropType.WHEAT

    def test_override_values(self):
        params = theta_to_crop_params({"rue_g_mj": 2.5, "k_extinction": 0.65})
        assert params.rue_g_mj == 2.5
        assert params.k_extinction == 0.65

    def test_clips_to_bounds(self):
        params = theta_to_crop_params({"rue_g_mj": 999.0, "k_extinction": -5.0})
        assert params.rue_g_mj == 5.0  # upper bound
        assert params.k_extinction == 0.1  # lower bound

    def test_preserves_base_params(self):
        base = CropParameters(crop_type=CropType.MAIZE, name_en="Maize")
        params = theta_to_crop_params({"rue_g_mj": 1.8}, base)
        assert params.crop_type == CropType.MAIZE
        assert params.name_en == "Maize"
        assert params.rue_g_mj == 1.8


# ---------------------------------------------------------------------------
# WeatherProvider from series
# ---------------------------------------------------------------------------


class TestWeatherProviderFromSeries:
    def test_valid_date(self, weather_series):
        provider = weather_provider_from_series(weather_series)
        w = provider("2026-01-01")
        assert w.tmax_c == 30.0

    def test_missing_date_raises(self, weather_series):
        provider = weather_provider_from_series(weather_series)
        with pytest.raises(KeyError, match="No weather data"):
            provider("2099-12-31")


# ---------------------------------------------------------------------------
# CropGrowthPredictor
# ---------------------------------------------------------------------------


class TestCropGrowthPredictor:
    def test_predict_returns_lai(self, predictor, lai_targets):
        result = predictor.predict(theta={"rue_g_mj": 1.2}, targets=lai_targets)
        assert "LAI" in result
        assert len(result["LAI"]) > 0
        # All predicted dates should be from the targets
        for dt in result["LAI"]:
            assert dt in {"2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01"}

    def test_predict_values_are_positive(self, predictor, lai_targets):
        result = predictor.predict(theta={"rue_g_mj": 1.5}, targets=lai_targets)
        for val in result.get("LAI", {}).values():
            assert val >= 0.0

    def test_predict_biomass_target(self, predictor, sowing_date):
        targets = [
            CalibrationTarget(
                variable="biomass",
                observations=[
                    CalibrationObservation(t="2026-03-01", value=1000.0, uncertainty=200.0),
                ],
            )
        ]
        result = predictor.predict(theta={"rue_g_mj": 1.5}, targets=targets)
        assert "biomass" in result
        # biomass should be in kg/ha (converted from g/m²)
        for val in result["biomass"].values():
            assert val >= 0.0

    def test_empty_targets(self, predictor):
        result = predictor.predict(theta={"rue_g_mj": 1.0}, targets=[])
        assert result == {}

    def test_higher_rue_gives_more_biomass(self, predictor, sowing_date):
        targets = [
            CalibrationTarget(
                variable="biomass",
                observations=[
                    CalibrationObservation(t="2026-04-01", value=2000.0),
                ],
            )
        ]
        low = predictor.predict(theta={"rue_g_mj": 0.5}, targets=targets)
        high = predictor.predict(theta={"rue_g_mj": 2.5}, targets=targets)
        if "biomass" in low and "biomass" in high:
            low_bm = list(low["biomass"].values())[0]
            high_bm = list(high["biomass"].values())[0]
            assert high_bm > low_bm

    def test_max_days_guard(self, weather_series, soil, sowing_date):
        predictor = CropGrowthPredictor(
            weather_provider=weather_provider_from_series(weather_series),
            soil_profile=soil,
            sowing_date=sowing_date,
            config=CropGrowthPredictorConfig(max_days=10),
        )
        targets = [
            CalibrationTarget(
                variable="LAI",
                observations=[
                    CalibrationObservation(t="2026-06-01", value=3.0),
                ],
            )
        ]
        with pytest.raises(ValueError, match="too large"):
            predictor.predict(theta={}, targets=targets)


# ---------------------------------------------------------------------------
# End-to-end: adapter + CalibrationEngine (toy integration)
# ---------------------------------------------------------------------------


class TestCropGrowthCalibrationE2E:
    def test_calibration_pipeline_runs(self, predictor, sowing_date):
        """
        Verify the full calibration pipeline (adapter → engine → result)
        runs end-to-end without errors and produces a valid result.
        """
        # Use biomass targets (more sensitive to RUE than LAI at early stages)
        obs_dates = [
            sowing_date + timedelta(days=d) for d in [30, 60, 90, 120]
        ]

        # Generate 'true' biomass predictions with known RUE
        true_theta = {"rue_g_mj": 1.5}
        synthetic_targets = [
            CalibrationTarget(
                variable="biomass",
                observations=[
                    CalibrationObservation(t=d.isoformat(), value=0.0, uncertainty=50.0)
                    for d in obs_dates
                ],
            )
        ]
        true_preds = predictor.predict(true_theta, synthetic_targets)
        assert "biomass" in true_preds

        # Build targets from model-generated values
        real_targets = [
            CalibrationTarget(
                variable="biomass",
                observations=[
                    CalibrationObservation(
                        t=d.isoformat(),
                        value=true_preds["biomass"].get(d.isoformat(), 100.0),
                        uncertainty=50.0,
                    )
                    for d in obs_dates
                    if d.isoformat() in true_preds.get("biomass", {})
                ],
            )
        ]

        engine = CalibrationEngine(
            predictor=predictor.predict,
            bounds=[
                ParameterBound("rue_g_mj", 0.5, 3.0, initial=0.8),
            ],
            seed=42,
        )
        result = engine.calibrate(
            targets=real_targets, max_iter=50, n_restarts=2
        )

        assert result.success
        assert result.n_evaluations > 0
        assert result.best_cost < float("inf")
        assert "rue_g_mj" in result.best_theta

    def test_different_rue_produces_different_biomass(self, predictor, sowing_date):
        """
        Verify that the predictor is actually sensitive to RUE changes,
        confirming the adapter correctly wires theta → CropGrowthEngine.
        """
        obs_date = (sowing_date + timedelta(days=90)).isoformat()
        targets = [
            CalibrationTarget(
                variable="biomass",
                observations=[CalibrationObservation(t=obs_date, value=0.0)],
            )
        ]
        low = predictor.predict({"rue_g_mj": 0.5}, targets)
        high = predictor.predict({"rue_g_mj": 3.0}, targets)
        if "biomass" in low and "biomass" in high:
            low_bm = low["biomass"].get(obs_date, 0.0)
            high_bm = high["biomass"].get(obs_date, 0.0)
            # Higher RUE must produce more biomass
            assert high_bm > low_bm
