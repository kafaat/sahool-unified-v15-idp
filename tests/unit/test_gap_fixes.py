# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Integration Gap Fix Tests - اختبارات إصلاح فجوات التكامل
=========================================================
Tests covering GAP-01 through GAP-18 fixes.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
from datetime import date, datetime, timezone

import pytest

# Helper to check if pydantic is available
try:
    import pydantic  # noqa: F401

    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False

_SKIP_PYDANTIC = pytest.mark.skipif(not _HAS_PYDANTIC, reason="pydantic not available")

# Project root for file-path assertions
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _make_daily_weather(day, tmax=30.0, tmin=15.0):
    """Helper to create DailyWeather with all required fields."""
    from shared.process_models.models import DailyWeather

    return DailyWeather(
        date=day,
        tmax_c=tmax,
        tmin_c=tmin,
        solar_radiation_mj_m2=18.0,
        relative_humidity_pct=55.0,
        wind_speed_m_s=2.0,
        precipitation_mm=0.0,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 1. NATS Calibration Event Subjects (GAP-05)
# ═══════════════════════════════════════════════════════════════════════════


def _import_subjects():
    """Import subjects module directly, bypassing shared.events.__init__."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "shared.events.subjects",
        os.path.join(_ROOT, "shared", "events", "subjects.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestCalibrationEventSubjects:
    def test_subjects_exist(self):
        m = _import_subjects()
        assert "sahool.calibration.run.queued" in m.SAHOOL_CALIBRATION_RUN_QUEUED
        assert "sahool.calibration.run.started" in m.SAHOOL_CALIBRATION_RUN_STARTED
        assert "sahool.calibration.run.succeeded" in m.SAHOOL_CALIBRATION_RUN_SUCCEEDED
        assert "sahool.calibration.run.failed" in m.SAHOOL_CALIBRATION_RUN_FAILED
        assert "parameters.activated" in m.SAHOOL_CALIBRATION_PARAMS_ACTIVATED
        assert "parameters.deprecated" in m.SAHOOL_CALIBRATION_PARAMS_DEPRECATED

    def test_in_registry(self):
        m = _import_subjects()
        assert "calibration.run.queued" in m.SUBJECT_REGISTRY
        assert "calibration.run.succeeded" in m.SUBJECT_REGISTRY
        assert "calibration.parameters.activated" in m.SUBJECT_REGISTRY

    def test_valid_format(self):
        m = _import_subjects()
        assert m.is_valid_subject(m.SAHOOL_CALIBRATION_RUN_QUEUED)

    def test_lookup(self):
        m = _import_subjects()
        assert m.lookup_subject("calibration.run.queued") == m.SAHOOL_CALIBRATION_RUN_QUEUED

    def test_wildcards(self):
        m = _import_subjects()
        assert m.SAHOOL_CALIBRATION_ALL == "sahool.calibration.>"
        assert m.SAHOOL_CALIBRATION_RUN_ALL == "sahool.calibration.run.>"


# ═══════════════════════════════════════════════════════════════════════════
# 2. Weather Adapter (GAP-09)
# ═══════════════════════════════════════════════════════════════════════════


@_SKIP_PYDANTIC
class TestWeatherAdapter:
    def test_basic_conversion(self):
        from shared.digital_twin.adapters import weather_payload_to_daily

        payload = {
            "day": "2026-02-20",
            "tmax_c": 32.0,
            "tmin_c": 18.0,
            "solar_radiation_mj_m2": 20.5,
            "relative_humidity_pct": 45.0,
            "wind_speed_m_s": 3.0,
            "precipitation_mm": 5.2,
        }
        w = weather_payload_to_daily(payload)
        assert w.date == date(2026, 2, 20)
        assert w.tmax_c == 32.0
        assert w.precipitation_mm == 5.2

    def test_alternative_keys(self):
        from shared.digital_twin.adapters import weather_payload_to_daily

        payload = {
            "forecast_date": "2026-03-01",
            "temp_max": 35.0,
            "temp_min": 20.0,
            "solar_rad": 22.0,
            "humidity": 40.0,
            "wind_speed": 4.5,
            "rain_mm": 0.0,
        }
        w = weather_payload_to_daily(payload)
        assert w.date == date(2026, 3, 1)
        assert w.tmax_c == 35.0

    def test_defaults(self):
        from shared.digital_twin.adapters import weather_payload_to_daily

        w = weather_payload_to_daily({})
        assert w.tmax_c == 30.0
        assert w.tmin_c == 15.0

    def test_series_sorted(self):
        from shared.digital_twin.adapters import weather_series_from_rows

        rows = [
            {
                "day": "2026-02-22",
                "tmax_c": 30,
                "tmin_c": 15,
                "solar_radiation_mj_m2": 18,
                "relative_humidity_pct": 55,
                "wind_speed_m_s": 2,
            },
            {
                "day": "2026-02-20",
                "tmax_c": 28,
                "tmin_c": 14,
                "solar_radiation_mj_m2": 18,
                "relative_humidity_pct": 55,
                "wind_speed_m_s": 2,
            },
        ]
        series = weather_series_from_rows(rows)
        assert series[0].date == date(2026, 2, 20)
        assert series[1].date == date(2026, 2, 22)


# ═══════════════════════════════════════════════════════════════════════════
# 3. NDVI Adapter (GAP-09)
# ═══════════════════════════════════════════════════════════════════════════


@_SKIP_PYDANTIC
class TestNDVIAdapter:
    def test_ndvi_to_observation(self):
        from uuid import uuid4
        from shared.digital_twin.adapters import ndvi_to_field_observation

        payload = {"mean_ndvi": 0.72, "ts": "2026-02-20T10:30:00Z", "cloud_cover": 0.15}
        obs = ndvi_to_field_observation(payload, tenant_id=uuid4(), field_id=uuid4())
        assert obs.value == 0.72
        assert obs.quality == pytest.approx(0.85)

    def test_lai_estimate(self):
        from shared.digital_twin.adapters import ndvi_to_lai_estimate

        assert ndvi_to_lai_estimate(0.2) < ndvi_to_lai_estimate(0.6) < ndvi_to_lai_estimate(0.8)
        assert ndvi_to_lai_estimate(0.8) > 2.0

    def test_lai_boundary_safety(self):
        from shared.digital_twin.adapters import ndvi_to_lai_estimate

        assert math.isfinite(ndvi_to_lai_estimate(0.0))
        assert math.isfinite(ndvi_to_lai_estimate(1.0))


# ═══════════════════════════════════════════════════════════════════════════
# 4. Calibrated Params Adapter (GAP-09)
# ═══════════════════════════════════════════════════════════════════════════


@_SKIP_PYDANTIC
class TestCalibratedParamsAdapter:
    def test_merge(self):
        from shared.digital_twin.adapters import calibrated_params_to_crop
        from shared.process_models.models import CropType

        crop = calibrated_params_to_crop({"rue_g_mj": 1.8, "k_extinction": 0.45}, crop_type=CropType.WHEAT)
        assert crop.rue_g_mj == 1.8
        assert crop.k_extinction == 0.45

    def test_from_json_string(self):
        from shared.digital_twin.adapters import calibrated_params_to_crop

        crop = calibrated_params_to_crop('{"rue_g_mj": 2.0, "lai_max": 7.5}')
        assert crop.rue_g_mj == 2.0
        assert crop.lai_max == 7.5

    def test_unknown_keys_ignored(self):
        from shared.digital_twin.adapters import calibrated_params_to_crop

        crop = calibrated_params_to_crop({"rue_g_mj": 1.5, "unknown_param": 999})
        assert crop.rue_g_mj == 1.5


# ═══════════════════════════════════════════════════════════════════════════
# 5. Soil Sensor Adapter (GAP-09)
# ═══════════════════════════════════════════════════════════════════════════


@_SKIP_PYDANTIC
class TestSoilSensorAdapter:
    def test_basic(self):
        from shared.digital_twin.adapters import soil_sensor_to_profile

        payload = {"field_capacity": 320.0, "wilting_point": 160.0, "depth_m": 0.8, "texture": "clay"}
        soil = soil_sensor_to_profile(payload)
        assert soil.field_capacity_mm_per_m == 320.0
        assert soil.depth_m == 0.8

    def test_with_base(self):
        from shared.digital_twin.adapters import soil_sensor_to_profile
        from shared.process_models.models import SoilProfile

        base = SoilProfile(field_capacity_mm_per_m=300.0, depth_m=0.6)
        soil = soil_sensor_to_profile({"wilting_point": 170.0}, base=base)
        assert soil.field_capacity_mm_per_m == 300.0
        assert soil.wilting_point_mm_per_m == 170.0


# ═══════════════════════════════════════════════════════════════════════════
# 6. Calibration Worker (GAP-11)
# ═══════════════════════════════════════════════════════════════════════════


class TestCalibrationWorker:
    def test_instantiation(self):
        from shared.calibration.worker import CalibrationWorker

        worker = CalibrationWorker(db_pool=None, nats_client=None, n_trials=30)
        assert worker._n_trials == 30

    def test_process_pending_no_pool(self):
        from shared.calibration.worker import CalibrationWorker

        worker = CalibrationWorker(db_pool=None)
        result = asyncio.get_event_loop().run_until_complete(worker.process_pending())
        assert result == []

    def test_default_param_bounds(self):
        from shared.calibration.worker import _DEFAULT_PARAM_BOUNDS

        names = {b.name for b in _DEFAULT_PARAM_BOUNDS}
        assert "rue_g_mj" in names
        assert "k_extinction" in names
        assert "gdd_maturity" in names
        assert len(_DEFAULT_PARAM_BOUNDS) >= 5


# ═══════════════════════════════════════════════════════════════════════════
# 7. DecisionEngine Calibrated Thresholds (GAP-14)
# ═══════════════════════════════════════════════════════════════════════════


@_SKIP_PYDANTIC
class TestDecisionEngineCalibrated:
    def test_default_thresholds(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        engine = DecisionEngine(repo=TwinRepository(db_pool=None))
        assert engine._eff == 0.80
        assert engine._p_offset == 0.0

    def test_custom_thresholds(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        engine = DecisionEngine(
            repo=TwinRepository(db_pool=None),
            calibrated_thresholds={"application_efficiency": 0.90, "p_fraction_offset": -0.05},
        )
        assert engine._eff == 0.90
        assert engine._p_offset == -0.05

    def test_p_offset_triggers_irrigation(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.models import AssimilationFlag, FieldDailyState
        from shared.digital_twin.repository import TwinRepository
        from uuid import uuid4

        repo = TwinRepository(db_pool=None)
        state = FieldDailyState(
            tenant_id=uuid4(),
            field_id=uuid4(),
            day=date(2026, 2, 20),
            et0_mm=5.0,
            etc_mm=4.0,
            phenology_stage="heading",
            gdd_cum=1200,
            lai=4.0,
            biomass_kg_ha=5000,
            root_depth_m=0.4,
            soil_water_mm=120,
            depletion_mm=60,
            water_stress=0.7,
            n_stress=0.9,
            runoff_mm=0,
            deep_perc_mm=0,
            rainfall_mm=0,
            irrigation_applied_mm=0,
            nitrogen_applied_kg_ha=0,
            confidence=0.8,
            assimilation_flags=[AssimilationFlag.MODEL_ONLY],
        )

        loop = asyncio.get_event_loop()

        # Default p for heading=0.45, RAW=81, depletion=60<81 → NO irrigation
        rec_default = loop.run_until_complete(DecisionEngine(repo=repo).recommend_irrigation(state, taw_mm=180.0))
        assert rec_default.recommended_mm == 0.0

        # Strict: p_offset=-0.30 → p=0.15, RAW=27, depletion=60>27 → YES
        rec_strict = loop.run_until_complete(
            DecisionEngine(repo=repo, calibrated_thresholds={"p_fraction_offset": -0.30}).recommend_irrigation(
                state, taw_mm=180.0
            )
        )
        assert rec_strict.recommended_mm > 0.0


# ═══════════════════════════════════════════════════════════════════════════
# 8. build_predictor Helpers (GAP-03)
# ═══════════════════════════════════════════════════════════════════════════


class TestBuildPredictorHelpers:
    def test_weather_provider_from_series(self):
        from shared.calibration.adapters.build_predictor import weather_provider_from_series

        series = [
            _make_daily_weather(date(2026, 1, 1), 30, 15),
            _make_daily_weather(date(2026, 1, 2), 31, 16),
        ]
        provider = weather_provider_from_series(series)
        assert provider("2026-01-01").tmax_c == 30

        with pytest.raises(KeyError):
            provider("2099-12-25")

    def test_build_predictor_from_config(self):
        from datetime import timedelta
        from shared.calibration.adapters.build_predictor import build_predictor_from_config
        from shared.process_models.models import SoilProfile

        sowing = date(2026, 1, 1)
        weather = [_make_daily_weather(sowing + timedelta(days=d)) for d in range(200)]
        predictor = build_predictor_from_config(
            weather_series=weather,
            soil_profile=SoilProfile(),
            sowing_date=sowing,
        )
        assert predictor is not None
        assert callable(predictor.predict)


# ═══════════════════════════════════════════════════════════════════════════
# 9. TwinStepIn season_id (GAP-02)
# ═══════════════════════════════════════════════════════════════════════════


class TestTwinStepInSeasonId:
    def test_season_id_in_source(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "twin_router.py")
        with open(path) as f:
            content = f.read()
        assert "season_id: str | None" in content
        assert "calibrated parameter lookup" in content.lower() or "calibrated" in content.lower()


# ═══════════════════════════════════════════════════════════════════════════
# 10. Requirements Presence (GAP-04/06)
# ═══════════════════════════════════════════════════════════════════════════


class TestRequirements:
    def test_numpy_in_requirements(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "requirements.txt")
        with open(path) as f:
            content = f.read()
        assert "numpy" in content

    def test_optuna_in_requirements(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "requirements.txt")
        with open(path) as f:
            content = f.read()
        assert "optuna" in content

    def test_optuna_in_constraints(self):
        path = os.path.join(_ROOT, "constraints.txt")
        with open(path) as f:
            content = f.read()
        assert "optuna" in content


# ═══════════════════════════════════════════════════════════════════════════
# 11. Event Subscribers (GAP-07)
# ═══════════════════════════════════════════════════════════════════════════


class TestEventSubscribers:
    def test_module_exists(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "event_subscribers.py")
        assert os.path.exists(path)

    def test_subscribes_to_ndvi_and_calibration(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "event_subscribers.py")
        with open(path) as f:
            content = f.read()
        assert "setup_nats_subscriptions" in content
        assert "SAHOOL_NDVI_COMPUTED" in content
        assert "SAHOOL_CALIBRATION_RUN_SUCCEEDED" in content
        assert "SAHOOL_WEATHER_FORECAST" in content


# ═══════════════════════════════════════════════════════════════════════════
# 12. Worker Module (GAP-11)
# ═══════════════════════════════════════════════════════════════════════════


class TestWorkerModule:
    def test_worker_module_exists(self):
        path = os.path.join(_ROOT, "shared", "calibration", "worker.py")
        assert os.path.exists(path)

    def test_worker_has_process_pending(self):
        path = os.path.join(_ROOT, "shared", "calibration", "worker.py")
        with open(path) as f:
            content = f.read()
        assert "class CalibrationWorker" in content
        assert "async def process_pending" in content
        assert "async def _process_one" in content

    def test_worker_publishes_events(self):
        path = os.path.join(_ROOT, "shared", "calibration", "worker.py")
        with open(path) as f:
            content = f.read()
        assert "calibration.run.succeeded" in content
        assert "calibration.run.failed" in content
        assert "calibration.run.started" in content


# ═══════════════════════════════════════════════════════════════════════════
# 13. Adapters Module (GAP-09)
# ═══════════════════════════════════════════════════════════════════════════


class TestAdaptersModule:
    def test_module_exists(self):
        path = os.path.join(_ROOT, "shared", "digital_twin", "adapters.py")
        assert os.path.exists(path)

    def test_all_adapters_present(self):
        path = os.path.join(_ROOT, "shared", "digital_twin", "adapters.py")
        with open(path) as f:
            content = f.read()
        assert "def weather_payload_to_daily" in content
        assert "def ndvi_to_field_observation" in content
        assert "def ndvi_to_lai_estimate" in content
        assert "def calibrated_params_to_crop" in content
        assert "def soil_sensor_to_profile" in content


# ═══════════════════════════════════════════════════════════════════════════
# 14. Calibration Router NATS Events (GAP-05 wiring)
# ═══════════════════════════════════════════════════════════════════════════


class TestCalibrationRouterEvents:
    def test_router_publishes_events(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "calibration_router.py")
        with open(path) as f:
            content = f.read()
        assert "SAHOOL_CALIBRATION_RUN_QUEUED" in content
        assert "SAHOOL_CALIBRATION_PARAMS_ACTIVATED" in content
        assert "_publish_calibration_event" in content


# ═══════════════════════════════════════════════════════════════════════════
# 15. Assimilation with Calibrated k_extinction (GAP-16)
# ═══════════════════════════════════════════════════════════════════════════


@_SKIP_PYDANTIC
class TestAssimilationCalibratedK:
    def test_ndvi_to_lai_default_k(self):
        from shared.digital_twin.assimilation import ndvi_to_lai

        # Default k=0.5
        lai = ndvi_to_lai(0.6, crop_type="wheat")
        assert lai > 0.0
        assert lai < 10.0

    def test_ndvi_to_lai_custom_k(self):
        from shared.digital_twin.assimilation import ndvi_to_lai

        lai_default = ndvi_to_lai(0.6, crop_type="wheat")
        lai_low_k = ndvi_to_lai(0.6, crop_type="wheat", k_extinction=0.3)
        lai_high_k = ndvi_to_lai(0.6, crop_type="wheat", k_extinction=0.8)
        # Lower k → higher LAI (less extinction means more leaf area needed to explain NDVI)
        assert lai_low_k > lai_default
        assert lai_high_k < lai_default

    def test_ndvi_to_lai_k_clamped(self):
        from shared.digital_twin.assimilation import ndvi_to_lai

        # k_extinction out of range should be clamped
        lai_extreme_low = ndvi_to_lai(0.5, k_extinction=0.001)  # clamped to 0.1
        lai_at_min = ndvi_to_lai(0.5, k_extinction=0.1)
        assert lai_extreme_low == pytest.approx(lai_at_min, rel=1e-3)

        lai_extreme_high = ndvi_to_lai(0.5, k_extinction=5.0)  # clamped to 1.0
        lai_at_max = ndvi_to_lai(0.5, k_extinction=1.0)
        assert lai_extreme_high == pytest.approx(lai_at_max, rel=1e-3)

    def test_calibrated_params_used_flag(self):
        from shared.digital_twin.models import AssimilationFlag

        assert hasattr(AssimilationFlag, "CALIBRATED_PARAMS_USED")
        assert AssimilationFlag.CALIBRATED_PARAMS_USED == "CALIBRATED_PARAMS_USED"

    def test_twin_router_passes_calibrated_k(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "twin_router.py")
        with open(path) as f:
            content = f.read()
        assert "calibrated_k_ext" in content
        assert "calibrated_k_extinction" in content
        assert "calibrated_thresholds" in content


# ═══════════════════════════════════════════════════════════════════════════
# 16. Soil & Fertility Router (GAP-17)
# ═══════════════════════════════════════════════════════════════════════════


class TestSoilFertilityRouter:
    def test_module_exists(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "soil_fertility_router.py")
        assert os.path.exists(path)

    def test_endpoints_present(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "soil_fertility_router.py")
        with open(path) as f:
            content = f.read()
        assert "/soil/interpret" in content
        assert "/soil/amendment-plan" in content
        assert "/soil/trends" in content
        assert "/fertilizer/crops" in content
        assert "/fertilizer/recommend" in content
        assert "/fertilizer/blend" in content

    def test_imports_shared_modules(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "soil_fertility_router.py")
        with open(path) as f:
            content = f.read()
        assert "shared.soil_testing" in content
        assert "shared.fertilizer_management" in content

    def test_registered_in_main(self):
        path = os.path.join(_ROOT, "apps", "services", "crop-intelligence-service", "src", "main.py")
        with open(path) as f:
            content = f.read()
        assert "soil_fertility_router" in content


# ═══════════════════════════════════════════════════════════════════════════
# 17. Fertilizer Management Module (GAP-18)
# ═══════════════════════════════════════════════════════════════════════════


class TestFertilizerManagement:
    def test_imports(self):
        from shared.fertilizer_management import (
            CROP_NUTRIENT_REQUIREMENTS,
            FertilizerCalculator,
            FertilizerRecommendationEngine,
            calculate_blend_for_targets,
            get_supported_crops,
        )

        assert CROP_NUTRIENT_REQUIREMENTS is not None
        assert FertilizerCalculator is not None
        assert FertilizerRecommendationEngine is not None
        assert callable(calculate_blend_for_targets)
        assert callable(get_supported_crops)

    def test_crop_requirements_structure(self):
        from shared.fertilizer_management import CROP_NUTRIENT_REQUIREMENTS

        assert "wheat" in CROP_NUTRIENT_REQUIREMENTS
        wheat = CROP_NUTRIENT_REQUIREMENTS["wheat"]
        assert "N" in wheat
        assert "P2O5" in wheat
        assert "K2O" in wheat
        assert "name_ar" in wheat
        assert "typical_yield" in wheat

    def test_supported_crops_list(self):
        from shared.fertilizer_management import get_supported_crops

        crops = get_supported_crops()
        assert isinstance(crops, list)
        assert len(crops) >= 5  # wheat, barley, tomato, date_palm, etc.

    def test_quick_recommendation(self):
        from shared.fertilizer_management import calculate_quick_recommendation

        rec = calculate_quick_recommendation(
            crop="wheat",
            soil_n_ppm=20,
            soil_p_ppm=15,
            soil_k_ppm=150,
        )
        assert isinstance(rec, dict)
        assert "crop" in rec
        assert "recommendations" in rec
        assert rec["crop"] == "wheat"

    def test_quick_recommendation_unknown_crop(self):
        from shared.fertilizer_management import calculate_quick_recommendation

        rec = calculate_quick_recommendation(
            crop="unknown_crop",
            soil_n_ppm=20,
            soil_p_ppm=15,
            soil_k_ppm=150,
        )
        assert "error" in rec

    def test_blend_for_targets(self):
        from shared.fertilizer_management import calculate_blend_for_targets

        blend = calculate_blend_for_targets(n_kg_ha=100, p_kg_ha=50, k_kg_ha=60)
        assert isinstance(blend, dict)

    def test_recommendation_engine(self):
        from shared.fertilizer_management import FertilizerRecommendationEngine

        engine = FertilizerRecommendationEngine()
        reqs = engine.calculate_crop_requirements("wheat", target_yield_tons_ha=5.0)
        assert "N" in reqs
        assert reqs["N"] > 0

    def test_nutrient_status(self):
        from shared.fertilizer_management import FertilizerRecommendationEngine

        engine = FertilizerRecommendationEngine()
        status, desc_en, desc_ar = engine.get_nutrient_status("N", 5.0)
        assert desc_ar  # has Arabic description
        status2, _, _ = engine.get_nutrient_status("N", 50.0)
        # 5 ppm should be worse than 50 ppm
        assert status != status2


# ═══════════════════════════════════════════════════════════════════════════
# 18. Soil Testing Module (GAP-18)
# ═══════════════════════════════════════════════════════════════════════════


class TestSoilTestingModule:
    def test_imports(self):
        from shared.soil_testing import (
            NUTRIENT_THRESHOLDS,
            SoilAmendmentRecommender,
            SoilTestInterpreter,
            SoilTrendAnalyzer,
            get_nutrient_status,
            get_ph_status,
            get_ec_status,
        )

        assert NUTRIENT_THRESHOLDS is not None
        assert SoilTestInterpreter is not None
        assert SoilAmendmentRecommender is not None
        assert SoilTrendAnalyzer is not None
        assert callable(get_nutrient_status)
        assert callable(get_ph_status)
        assert callable(get_ec_status)

    def test_nutrient_thresholds_structure(self):
        from shared.soil_testing import NUTRIENT_THRESHOLDS

        assert "N" in NUTRIENT_THRESHOLDS
        n_thresh = NUTRIENT_THRESHOLDS["N"]
        assert "deficient" in n_thresh
        assert "adequate" in n_thresh
        assert "name_ar" in n_thresh

    def test_get_nutrient_status(self):
        from shared.soil_testing import get_nutrient_status

        status, en, ar = get_nutrient_status("N", 5.0)
        assert ar  # has Arabic text
        status2, _, _ = get_nutrient_status("N", 50.0)
        # 5 ppm should be worse status than 50 ppm
        assert status != status2

    def test_ph_status(self):
        from shared.soil_testing import get_ph_status

        en, ar = get_ph_status(7.0)
        assert en  # has English text
        assert ar  # has Arabic text

    def test_ec_status(self):
        from shared.soil_testing import get_ec_status

        en, ar = get_ec_status(1.5)
        assert en  # has English text
        assert ar  # has Arabic text

    def test_interpreter_instantiation(self):
        from shared.soil_testing import SoilTestInterpreter

        interpreter = SoilTestInterpreter()
        assert interpreter is not None

    def test_recommender_instantiation(self):
        from shared.soil_testing import SoilAmendmentRecommender

        recommender = SoilAmendmentRecommender()
        assert recommender is not None

    def test_trend_analyzer_instantiation(self):
        from shared.soil_testing import SoilTrendAnalyzer

        analyzer = SoilTrendAnalyzer()
        assert analyzer is not None


# ═══════════════════════════════════════════════════════════════════════════
# 19. CI Workflow & Helm Chart Existence (GAP-12, GAP-13)
# ═══════════════════════════════════════════════════════════════════════════


class TestCIAndHelmChart:
    def test_ci_workflow_exists(self):
        path = os.path.join(_ROOT, ".github", "workflows", "ci-crop-intelligence.yml")
        assert os.path.exists(path)

    def test_ci_workflow_covers_shared_modules(self):
        path = os.path.join(_ROOT, ".github", "workflows", "ci-crop-intelligence.yml")
        with open(path) as f:
            content = f.read()
        assert "crop-intelligence-service" in content
        assert "shared/digital_twin" in content
        assert "shared/calibration" in content
        assert "shared/process_models" in content
        assert "shared/fertilizer_management" in content
        assert "shared/soil_testing" in content

    def test_helm_chart_exists(self):
        chart_path = os.path.join(_ROOT, "helm", "services", "crop-intelligence-service", "Chart.yaml")
        assert os.path.exists(chart_path)

    def test_helm_values_exists(self):
        values_path = os.path.join(_ROOT, "helm", "services", "crop-intelligence-service", "values.yaml")
        assert os.path.exists(values_path)

    def test_helm_chart_metadata(self):
        chart_path = os.path.join(_ROOT, "helm", "services", "crop-intelligence-service", "Chart.yaml")
        with open(chart_path) as f:
            content = f.read()
        assert "crop-intelligence-service" in content
        assert "16.0.0" in content

    def test_helm_values_port(self):
        values_path = os.path.join(_ROOT, "helm", "services", "crop-intelligence-service", "values.yaml")
        with open(values_path) as f:
            content = f.read()
        assert "8095" in content

    def test_helm_templates_exist(self):
        templates_dir = os.path.join(_ROOT, "helm", "services", "crop-intelligence-service", "templates")
        for tpl in [
            "deployment.yaml",
            "service.yaml",
            "hpa.yaml",
            "pdb.yaml",
            "configmap.yaml",
            "serviceaccount.yaml",
            "_helpers.tpl",
        ]:
            assert os.path.exists(os.path.join(templates_dir, tpl)), f"Missing template: {tpl}"

    def test_helm_startup_probe_defined(self):
        """Verify startupProbe was added for calibration/assimilation init."""
        dep_path = os.path.join(_ROOT, "helm", "services", "crop-intelligence-service", "templates", "deployment.yaml")
        with open(dep_path) as f:
            content = f.read()
        assert "startupProbe" in content

    def test_helm_resource_requests_adequate(self):
        """Resource requests should be >= 1000m CPU for ML workloads."""
        values_path = os.path.join(_ROOT, "helm", "services", "crop-intelligence-service", "values.yaml")
        with open(values_path) as f:
            content = f.read()
        assert "1000m" in content  # CPU request
        assert "1536Mi" in content  # Memory request


# ═══════════════════════════════════════════════════════════════════════════
# 20. Numerical Edge Cases & Boundary Conditions
# ═══════════════════════════════════════════════════════════════════════════


class TestNumericalEdgeCases:
    """Tests for critical numerical safety in digital twin calculations."""

    @_SKIP_PYDANTIC
    def test_ndvi_to_lai_bare_soil(self):
        """NDVI near 0 (bare soil) should return LAI near 0."""
        from shared.digital_twin.assimilation import ndvi_to_lai

        lai = ndvi_to_lai(0.01)
        assert 0.0 <= lai <= 0.5
        assert math.isfinite(lai)

    @_SKIP_PYDANTIC
    def test_ndvi_to_lai_maximum(self):
        """NDVI = 0.99 should not cause log(0) error."""
        from shared.digital_twin.assimilation import ndvi_to_lai

        lai = ndvi_to_lai(0.99)
        assert 0.0 <= lai <= 10.0
        assert math.isfinite(lai)

    @_SKIP_PYDANTIC
    def test_ndvi_to_lai_extreme_values_clamped(self):
        """NDVI outside [-1,1] should be safely clamped, not crash."""
        from shared.digital_twin.assimilation import ndvi_to_lai

        # Below range
        lai_low = ndvi_to_lai(-0.5)
        assert math.isfinite(lai_low)
        assert lai_low >= 0.0
        # Above range
        lai_high = ndvi_to_lai(1.5)
        assert math.isfinite(lai_high)
        assert lai_high <= 10.0

    @_SKIP_PYDANTIC
    def test_ndvi_to_lai_k_extinction_extremes(self):
        """k_extinction near boundaries should not crash."""
        from shared.digital_twin.assimilation import ndvi_to_lai

        # Very small k (clamped to 0.1)
        lai_small_k = ndvi_to_lai(0.5, k_extinction=0.01)
        assert math.isfinite(lai_small_k)
        # Very large k (clamped to 1.0)
        lai_large_k = ndvi_to_lai(0.5, k_extinction=5.0)
        assert math.isfinite(lai_large_k)
        # Lower k → higher LAI (Beer-Lambert inverse)
        assert lai_small_k > lai_large_k

    @_SKIP_PYDANTIC
    def test_adapters_ndvi_to_lai_boundary(self):
        """Adapters version also safe at boundaries."""
        from shared.digital_twin.adapters import ndvi_to_lai_estimate

        # Near maximum
        lai = ndvi_to_lai_estimate(0.99)
        assert math.isfinite(lai)
        assert 0.0 <= lai <= 10.0
        # Near minimum
        lai_min = ndvi_to_lai_estimate(0.01)
        assert math.isfinite(lai_min)
        assert lai_min >= 0.0

    @_SKIP_PYDANTIC
    def test_kalman_gain_zero_inputs(self):
        """Both quality=0 and confidence=0 should return default, not crash."""
        from shared.digital_twin.assimilation import _kalman_gain

        gain = _kalman_gain(0.0, 0.0)
        assert 0.0 < gain < 1.0
        assert math.isfinite(gain)

    @_SKIP_PYDANTIC
    def test_stress_factor_validation_bounds(self):
        """Pydantic should reject water_stress/n_stress outside [0,1]."""
        from shared.digital_twin.models import FieldDailyState
        from uuid import uuid4
        from pydantic import ValidationError

        # Valid
        state = FieldDailyState(
            tenant_id=uuid4(),
            field_id=uuid4(),
            day=date.today(),
            water_stress=0.5,
            n_stress=0.8,
        )
        assert state.water_stress == 0.5
        # Invalid: water_stress > 1
        with pytest.raises(ValidationError):
            FieldDailyState(
                tenant_id=uuid4(),
                field_id=uuid4(),
                day=date.today(),
                water_stress=1.5,
            )
        # Invalid: negative n_stress
        with pytest.raises(ValidationError):
            FieldDailyState(
                tenant_id=uuid4(),
                field_id=uuid4(),
                day=date.today(),
                n_stress=-0.1,
            )


# ═══════════════════════════════════════════════════════════════════════════
# 21. Enum Deserialization Safety
# ═══════════════════════════════════════════════════════════════════════════


class TestEnumSafety:
    """Tests for AssimilationFlag serialization roundtrip."""

    @_SKIP_PYDANTIC
    def test_flag_roundtrip_by_value(self):
        """Flags stored as string values should deserialize correctly."""
        from shared.digital_twin.models import AssimilationFlag

        for flag in AssimilationFlag:
            # StrEnum: name == value for our flags
            recovered = AssimilationFlag(flag.value)
            assert recovered == flag

    @_SKIP_PYDANTIC
    def test_flag_unknown_value_handled(self):
        """Unknown flag values in DB should not crash repository."""
        from shared.digital_twin.models import AssimilationFlag

        # Simulate what _row_to_state does
        flags_raw = ["NDVI_USED", "UNKNOWN_FLAG", "ASSIMILATED"]
        flags = []
        for f in flags_raw:
            if f in AssimilationFlag.__members__:
                flags.append(AssimilationFlag[f])
            else:
                try:
                    flags.append(AssimilationFlag(f))
                except ValueError:
                    pass  # skip unknown
        assert len(flags) == 2
        assert AssimilationFlag.NDVI_USED in flags
        assert AssimilationFlag.ASSIMILATED in flags

    @_SKIP_PYDANTIC
    def test_calibrated_params_flag_included(self):
        """CALIBRATED_PARAMS_USED must be in the enum."""
        from shared.digital_twin.models import AssimilationFlag

        assert "CALIBRATED_PARAMS_USED" in AssimilationFlag.__members__


# ═══════════════════════════════════════════════════════════════════════════
# 22. Decision Engine Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


class TestDecisionEngineEdgeCases:
    """Tests for irrigation decision edge cases."""

    @_SKIP_PYDANTIC
    def test_zero_depletion_no_irrigation(self):
        """When depletion is 0, no irrigation should be recommended."""
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.models import FieldDailyState
        from shared.digital_twin.repository import TwinRepository
        from uuid import uuid4

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        state = FieldDailyState(
            tenant_id=uuid4(),
            field_id=uuid4(),
            day=date.today(),
            depletion_mm=0.0,
            water_stress=1.0,
            phenology_stage="heading",
        )
        loop = asyncio.get_event_loop()
        rec = loop.run_until_complete(engine.recommend_irrigation(state, taw_mm=180.0))
        assert rec.recommended_mm == 0.0
        assert "NO_IRRIGATION_NEEDED" in rec.reason_codes

    @_SKIP_PYDANTIC
    def test_high_depletion_triggers_irrigation(self):
        """Depletion exceeding RAW should trigger irrigation."""
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.models import FieldDailyState
        from shared.digital_twin.repository import TwinRepository
        from uuid import uuid4

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        state = FieldDailyState(
            tenant_id=uuid4(),
            field_id=uuid4(),
            day=date.today(),
            depletion_mm=120.0,
            water_stress=0.4,
            phenology_stage="heading",
        )
        loop = asyncio.get_event_loop()
        rec = loop.run_until_complete(engine.recommend_irrigation(state, taw_mm=180.0))
        assert rec.recommended_mm > 0.0
        assert "DEPLETION_EXCEEDS_RAW" in rec.reason_codes

    @_SKIP_PYDANTIC
    def test_none_depletion_uses_zero_fallback(self):
        """Missing depletion_mm should default to 0, not crash."""
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.models import FieldDailyState
        from shared.digital_twin.repository import TwinRepository
        from uuid import uuid4

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        state = FieldDailyState(
            tenant_id=uuid4(),
            field_id=uuid4(),
            day=date.today(),
            depletion_mm=None,
            water_stress=None,
        )
        loop = asyncio.get_event_loop()
        rec = loop.run_until_complete(engine.recommend_irrigation(state, taw_mm=180.0))
        assert rec.recommended_mm >= 0.0
        assert math.isfinite(rec.recommended_mm)

    @_SKIP_PYDANTIC
    def test_taw_clamped_to_valid_range(self):
        """Extreme taw_mm values should be clamped, not crash."""
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.models import FieldDailyState
        from shared.digital_twin.repository import TwinRepository
        from uuid import uuid4

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        state = FieldDailyState(
            tenant_id=uuid4(),
            field_id=uuid4(),
            day=date.today(),
            depletion_mm=50.0,
            water_stress=0.8,
        )
        loop = asyncio.get_event_loop()
        # taw_mm = 0 → clamped to 1.0
        rec = loop.run_until_complete(engine.recommend_irrigation(state, taw_mm=0.0))
        assert math.isfinite(rec.recommended_mm)
        # taw_mm = 999 → clamped to 500
        rec2 = loop.run_until_complete(engine.recommend_irrigation(state, taw_mm=999.0))
        assert math.isfinite(rec2.recommended_mm)

    @_SKIP_PYDANTIC
    def test_calibrated_p_fraction_offset(self):
        """p_fraction_offset from calibration should shift the threshold."""
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.models import FieldDailyState
        from shared.digital_twin.repository import TwinRepository
        from uuid import uuid4

        repo = TwinRepository(db_pool=None)
        # Positive offset raises RAW threshold → less likely to trigger irrigation
        engine_offset = DecisionEngine(
            repo=repo,
            calibrated_thresholds={"p_fraction_offset": 0.15},
        )
        engine_default = DecisionEngine(repo=repo)
        state = FieldDailyState(
            tenant_id=uuid4(),
            field_id=uuid4(),
            day=date.today(),
            depletion_mm=100.0,
            water_stress=0.7,
            phenology_stage="heading",
        )
        loop = asyncio.get_event_loop()
        rec_offset = loop.run_until_complete(engine_offset.recommend_irrigation(state))
        rec_default = loop.run_until_complete(engine_default.recommend_irrigation(state))
        # Higher p → higher RAW → needs more depletion to trigger → less irrigation
        assert rec_offset.recommended_mm <= rec_default.recommended_mm
