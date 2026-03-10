"""
Unit tests for shared/digital_twin – Digital Twin integration layer
====================================================================
Covers:
  1. Feature flags           – environment toggle reading
  2. Domain models           – FieldDailyState, FieldObservation, IrrigationRecommendation
  3. TwinRepository          – in-memory save/get (no DB required)
  4. TwinPipeline            – daily step produces valid state
  5. AssimilationEngine      – Kalman-lite NDVI/soil corrections
  6. DecisionEngine          – irrigation recommendation logic
  7. New NATS subjects       – subjects.py additions
  8. twin_router             – FastAPI endpoint smoke tests
"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone, UTC
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

# Make async tests work without extra CLI flags (mirrors tests/unit/ai/test_ai_metrics.py)
pytest_plugins = ("pytest_asyncio",)
# NOTE: do NOT set a module-level pytestmark here – it would apply asyncio marks
# to synchronous helper tests and produce spurious PytestWarnings.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT = uuid4()
FIELD = uuid4()
TODAY = date.today()


def _make_state(**kwargs) -> Any:
    from shared.digital_twin.models import FieldDailyState

    defaults = {
        "tenant_id": TENANT,
        "field_id": FIELD,
        "day": TODAY,
        "et0_mm": 5.2,
        "etc_mm": 4.5,
        "phenology_stage": "tillering",
        "gdd_cum": 320.0,
        "lai": 2.5,
        "biomass_kg_ha": 1800.0,
        "root_depth_m": 0.40,
        "soil_water_mm": 240.0,
        "depletion_mm": 60.0,
        "water_stress": 0.85,
        "n_stress": 0.90,
        "runoff_mm": 0.0,
        "deep_perc_mm": 0.0,
        "rainfall_mm": 0.0,
        "irrigation_applied_mm": 0.0,
        "nitrogen_applied_kg_ha": 0.0,
        "confidence": 0.70,
    }
    defaults.update(kwargs)
    return FieldDailyState(**defaults)


def _make_observation(**kwargs) -> Any:
    from shared.digital_twin.models import (
        FieldObservation,
        ObservationSource,
        ObservationType,
    )

    defaults = {
        "tenant_id": TENANT,
        "field_id": FIELD,
        "ts": datetime.now(UTC),
        "source": ObservationSource.SENTINEL_2,
        "obs_type": ObservationType.NDVI,
        "value": 0.72,
        "quality": 0.85,
    }
    defaults.update(kwargs)
    return FieldObservation(**defaults)


# ===========================================================================
# 1. Feature Flags
# ===========================================================================


class TestDigitalTwinFlags:
    def test_defaults_process_models_on(self):
        from shared.digital_twin.feature_flags import DigitalTwinFlags

        flags = DigitalTwinFlags()
        assert flags.process_models_enabled is True

    def test_defaults_assimilation_off(self):
        from shared.digital_twin.feature_flags import DigitalTwinFlags

        flags = DigitalTwinFlags()
        assert flags.assimilation_enabled is False

    def test_env_override_process_models_false(self, monkeypatch):
        monkeypatch.setenv("PROCESS_MODELS_ENABLED", "false")
        from shared.digital_twin.feature_flags import DigitalTwinFlags

        flags = DigitalTwinFlags()
        assert flags.process_models_enabled is False

    def test_env_override_assimilation_true(self, monkeypatch):
        monkeypatch.setenv("ASSIMILATION_ENABLED", "true")
        from shared.digital_twin.feature_flags import DigitalTwinFlags

        flags = DigitalTwinFlags()
        assert flags.assimilation_enabled is True

    def test_as_dict_keys(self):
        from shared.digital_twin.feature_flags import DigitalTwinFlags

        d = DigitalTwinFlags().as_dict()
        for key in (
            "process_models_enabled",
            "assimilation_enabled",
            "db_persist_enabled",
            "nats_events_enabled",
        ):
            assert key in d


# ===========================================================================
# 2. Domain Models
# ===========================================================================


class TestDomainModels:
    def test_field_daily_state_defaults(self):
        from shared.digital_twin.models import AssimilationFlag, FieldDailyState

        s = FieldDailyState(tenant_id=TENANT, field_id=FIELD, day=TODAY)
        assert s.confidence == pytest.approx(0.6)
        assert s.assimilation_flags == []
        assert s.rainfall_mm == 0.0

    def test_field_daily_state_summary_keys(self):
        s = _make_state()
        summary = s.summary()
        for k in (
            "lai",
            "depletion_mm",
            "water_stress",
            "phenology_stage",
            "confidence",
        ):
            assert k in summary

    def test_irrigation_recommendation_defaults(self):
        from shared.digital_twin.models import IrrigationRecommendation

        rec = IrrigationRecommendation(tenant_id=TENANT, field_id=FIELD, day=TODAY, recommended_mm=25.0)
        assert rec.confidence == pytest.approx(0.7)
        assert rec.reason_codes == []

    def test_observation_model(self):
        obs = _make_observation()
        assert obs.quality == pytest.approx(0.85)
        assert obs.value == pytest.approx(0.72)

    def test_assimilation_flag_values(self):
        from shared.digital_twin.models import AssimilationFlag

        assert AssimilationFlag.NDVI_USED == "NDVI_USED"
        assert AssimilationFlag.ASSIMILATED == "ASSIMILATED"
        assert AssimilationFlag.MODEL_ONLY == "MODEL_ONLY"

    def test_observation_type_values(self):
        from shared.digital_twin.models import ObservationType

        assert ObservationType.NDVI == "ndvi"
        assert ObservationType.SOIL_MOISTURE == "soil_moisture"


# ===========================================================================
# 3. TwinRepository (in-memory fallback)
# ===========================================================================


class TestTwinRepositoryMemory:
    def setup_method(self):
        from shared.digital_twin.repository import (
            TwinRepository,
            _mem_states,
            _mem_observations,
            _mem_recommendations,
        )

        # Clear in-memory stores
        _mem_states.clear()
        _mem_observations.clear()
        _mem_recommendations.clear()
        self.repo = TwinRepository(db_pool=None)

    @pytest.mark.asyncio
    async def test_save_and_get_state(self):
        state = _make_state()
        await self.repo.save_state(state)
        loaded = await self.repo.get_state(TENANT, FIELD, TODAY)
        assert loaded is not None
        assert loaded.lai == pytest.approx(2.5)

    @pytest.mark.asyncio
    async def test_get_state_missing_returns_none(self):
        result = await self.repo.get_state(TENANT, uuid4(), TODAY)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_states_range(self):
        for i in range(5):
            s = _make_state(day=TODAY - timedelta(days=i), lai=float(i))
            await self.repo.save_state(s)

        states = await self.repo.get_states(TENANT, FIELD, TODAY - timedelta(days=4), TODAY)
        assert len(states) == 5
        # Should be sorted ascending by day
        days = [s.day for s in states]
        assert days == sorted(days)

    @pytest.mark.asyncio
    async def test_save_and_get_observation(self):
        from shared.digital_twin.models import ObservationType

        obs = _make_observation()
        await self.repo.save_observation(obs)
        results = await self.repo.get_recent_observations(TENANT, FIELD, ObservationType.NDVI, days_back=7)
        assert len(results) >= 1
        assert results[0].value == pytest.approx(0.72)

    @pytest.mark.asyncio
    async def test_save_and_get_recommendation(self):
        from shared.digital_twin.models import IrrigationRecommendation

        rec = IrrigationRecommendation(
            tenant_id=TENANT,
            field_id=FIELD,
            day=TODAY,
            recommended_mm=30.0,
            reason_codes=["DEPLETION_EXCEEDS_RAW"],
        )
        await self.repo.save_recommendation(rec)
        loaded = await self.repo.get_recommendation(TENANT, FIELD, TODAY)
        assert loaded is not None
        assert loaded.recommended_mm == pytest.approx(30.0)

    @pytest.mark.asyncio
    async def test_recommendation_upsert(self):
        from shared.digital_twin.models import IrrigationRecommendation

        rec1 = IrrigationRecommendation(tenant_id=TENANT, field_id=FIELD, day=TODAY, recommended_mm=20.0)
        rec2 = IrrigationRecommendation(tenant_id=TENANT, field_id=FIELD, day=TODAY, recommended_mm=35.0)
        await self.repo.save_recommendation(rec1)
        await self.repo.save_recommendation(rec2)
        loaded = await self.repo.get_recommendation(TENANT, FIELD, TODAY)
        assert loaded.recommended_mm == pytest.approx(35.0)


# ===========================================================================
# 4. TwinPipeline – daily step
# ===========================================================================


class TestTwinPipeline:
    def setup_method(self):
        from shared.digital_twin.repository import (
            _mem_states,
            _mem_observations,
            _mem_recommendations,
        )

        _mem_states.clear()
        _mem_observations.clear()
        _mem_recommendations.clear()

    @pytest.mark.asyncio
    async def test_step_returns_valid_state(self):
        from datetime import date

        from shared.digital_twin.pipeline import TwinPipeline
        from shared.digital_twin.repository import TwinRepository
        from shared.process_models.models import (
            CropParameters,
            CropType,
            DailyWeather,
            SoilProfile,
        )

        repo = TwinRepository(db_pool=None)
        pipeline = TwinPipeline(repo=repo, nats_client=None)

        weather = DailyWeather(
            date=TODAY,
            tmax_c=28.0,
            tmin_c=14.0,
            solar_radiation_mj_m2=18.0,
            relative_humidity_pct=55.0,
            wind_speed_m_s=2.5,
            precipitation_mm=0.0,
        )
        soil = SoilProfile()
        crop = CropParameters(crop_type=CropType.WHEAT)

        state = await pipeline.step(
            tenant_id=TENANT,
            field_id=FIELD,
            day=TODAY,
            weather=weather,
            soil=soil,
            crop=crop,
        )
        assert state.et0_mm is not None
        assert state.et0_mm > 0.0
        assert state.soil_water_mm is not None
        assert state.soil_water_mm >= 0.0
        assert state.phenology_stage is not None

    @pytest.mark.asyncio
    async def test_step_persists_to_repo(self):
        from shared.digital_twin.pipeline import TwinPipeline
        from shared.digital_twin.repository import TwinRepository
        from shared.process_models.models import (
            CropParameters,
            CropType,
            DailyWeather,
            SoilProfile,
        )

        repo = TwinRepository(db_pool=None)
        pipeline = TwinPipeline(repo=repo, nats_client=None)
        weather = DailyWeather(
            date=TODAY,
            tmax_c=25.0,
            tmin_c=12.0,
            solar_radiation_mj_m2=16.0,
            relative_humidity_pct=60.0,
            wind_speed_m_s=2.0,
            precipitation_mm=0.0,
        )
        await pipeline.step(TENANT, FIELD, TODAY, weather, SoilProfile(), CropParameters())
        saved = await repo.get_state(TENANT, FIELD, TODAY)
        assert saved is not None

    @pytest.mark.asyncio
    async def test_step_increments_gdd(self):
        """Second day should have higher GDD than first."""
        from shared.digital_twin.pipeline import TwinPipeline
        from shared.digital_twin.repository import TwinRepository
        from shared.process_models.models import (
            CropParameters,
            CropType,
            DailyWeather,
            SoilProfile,
        )

        repo = TwinRepository(db_pool=None)
        pipeline = TwinPipeline(repo=repo, nats_client=None)
        day1 = TODAY - timedelta(days=1)
        day2 = TODAY

        for day in (day1, day2):
            weather = DailyWeather(
                date=day,
                tmax_c=26.0,
                tmin_c=12.0,
                solar_radiation_mj_m2=16.0,
                relative_humidity_pct=60.0,
                wind_speed_m_s=2.0,
                precipitation_mm=0.0,
            )
            await pipeline.step(TENANT, FIELD, day, weather, SoilProfile(), CropParameters())

        s1 = await repo.get_state(TENANT, FIELD, day1)
        s2 = await repo.get_state(TENANT, FIELD, day2)
        assert s2.gdd_cum >= s1.gdd_cum


# ===========================================================================
# 5. AssimilationEngine
# ===========================================================================


class TestAssimilationEngine:
    def setup_method(self):
        from shared.digital_twin.repository import _mem_observations

        _mem_observations.clear()

    @pytest.mark.asyncio
    async def test_assimilate_no_observations_returns_unchanged(self):
        from shared.digital_twin.assimilation import AssimilationEngine
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        engine = AssimilationEngine(repo=repo)
        state = _make_state(lai=2.0)
        corrected = await engine.assimilate(state)
        # No observations → same object returned
        assert corrected is state

    @pytest.mark.asyncio
    async def test_assimilate_ndvi_corrects_lai(self):
        from shared.digital_twin.assimilation import AssimilationEngine
        from shared.digital_twin.models import AssimilationFlag, ObservationType
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        # Inject a high-NDVI observation
        obs = _make_observation(value=0.82, quality=0.90)
        await repo.save_observation(obs)

        engine = AssimilationEngine(repo=repo)
        state = _make_state(lai=1.5, confidence=0.70)  # low model LAI
        corrected = await engine.assimilate(state)

        assert AssimilationFlag.NDVI_USED in corrected.assimilation_flags
        assert AssimilationFlag.ASSIMILATED in corrected.assimilation_flags
        # LAI should be pulled up toward the NDVI-derived value
        assert corrected.lai > state.lai

    @pytest.mark.asyncio
    async def test_assimilate_soil_moisture_corrects_water(self):
        from shared.digital_twin.assimilation import AssimilationEngine
        from shared.digital_twin.models import (
            AssimilationFlag,
            FieldObservation,
            ObservationSource,
            ObservationType,
        )
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        obs = FieldObservation(
            tenant_id=TENANT,
            field_id=FIELD,
            ts=datetime.now(UTC),
            source=ObservationSource.IOT_SENSOR,
            obs_type=ObservationType.SOIL_MOISTURE,
            value=0.32,  # 32% VWC
            quality=0.80,
            meta={"soil_depth_m": 0.6},
        )
        await repo.save_observation(obs)

        engine = AssimilationEngine(repo=repo)
        state = _make_state(soil_water_mm=100.0, confidence=0.65)
        corrected = await engine.assimilate(state)

        assert AssimilationFlag.SOIL_MOISTURE_USED in corrected.assimilation_flags
        # Sensor says 0.32 * 600mm = 192mm → corrected value should be > original 100mm
        assert corrected.soil_water_mm > state.soil_water_mm

    def test_ndvi_to_lai_increases_with_ndvi(self):
        from shared.digital_twin.assimilation import ndvi_to_lai

        lai_low = ndvi_to_lai(0.30)
        lai_high = ndvi_to_lai(0.70)
        assert lai_high > lai_low

    def test_ndvi_to_lai_bounds(self):
        from shared.digital_twin.assimilation import ndvi_to_lai

        assert ndvi_to_lai(0.01) >= 0.0
        assert ndvi_to_lai(0.99) <= 10.0

    def test_kalman_gain_range(self):
        from shared.digital_twin.assimilation import _kalman_gain

        for q, c in [(0.9, 0.6), (0.5, 0.8), (0.1, 0.9)]:
            gain = _kalman_gain(q, c)
            assert 0.05 <= gain <= 0.80


# ===========================================================================
# 6. DecisionEngine – irrigation recommendations
# ===========================================================================


class TestDecisionEngine:
    def setup_method(self):
        from shared.digital_twin.repository import _mem_recommendations

        _mem_recommendations.clear()

    @pytest.mark.asyncio
    async def test_no_irrigation_when_no_depletion(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        # Full soil water, no stress
        state = _make_state(depletion_mm=5.0, water_stress=1.0)
        rec = await engine.recommend_irrigation(state, taw_mm=180.0)
        assert rec.recommended_mm == pytest.approx(0.0)
        assert "NO_IRRIGATION_NEEDED" in rec.reason_codes

    @pytest.mark.asyncio
    async def test_irrigation_when_depletion_exceeds_raw(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        # p=0.45 for heading stage → RAW = 0.45*180 = 81mm; depletion=120mm
        state = _make_state(depletion_mm=120.0, water_stress=0.30, phenology_stage="heading")
        rec = await engine.recommend_irrigation(state, taw_mm=180.0)
        assert rec.recommended_mm > 0.0
        assert "DEPLETION_EXCEEDS_RAW" in rec.reason_codes

    @pytest.mark.asyncio
    async def test_irrigation_bounded(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo, max_irrigation_mm=80.0)
        state = _make_state(depletion_mm=400.0, water_stress=0.0)
        rec = await engine.recommend_irrigation(state, taw_mm=180.0)
        assert rec.recommended_mm <= 80.0

    @pytest.mark.asyncio
    async def test_explanation_bilingual(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        state = _make_state(depletion_mm=120.0, water_stress=0.3)
        rec = await engine.recommend_irrigation(state, taw_mm=180.0)
        assert "en" in rec.explanation
        assert "ar" in rec.explanation
        assert len(rec.explanation["en"]) > 10
        assert len(rec.explanation["ar"]) > 10

    @pytest.mark.asyncio
    async def test_fertilizer_recommendation_runs(self):
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        state = _make_state()
        result = await engine.recommend_fertilizer(state, crop_type="wheat", target_yield_t_ha=4.0)
        assert "n_fertiliser_kg_ha" in result
        assert result["n_fertiliser_kg_ha"] >= 0.0

    @pytest.mark.asyncio
    async def test_stress_triggers_irrigation(self):
        """Low water_stress but depletion below RAW → stress fallback trigger."""
        from shared.digital_twin.decisions import DecisionEngine
        from shared.digital_twin.repository import TwinRepository

        repo = TwinRepository(db_pool=None)
        engine = DecisionEngine(repo=repo)
        state = _make_state(depletion_mm=10.0, water_stress=0.50)  # severe stress
        rec = await engine.recommend_irrigation(state, taw_mm=180.0)
        assert rec.recommended_mm > 0.0
        assert "WATER_STRESS_DETECTED" in rec.reason_codes


# ===========================================================================
# 7. NATS Subjects
# ===========================================================================


class TestNATSSubjects:
    def test_observation_ingested_subject(self):
        from shared.events.subjects import SAHOOL_FIELD_OBSERVATION_INGESTED

        assert SAHOOL_FIELD_OBSERVATION_INGESTED == "sahool.field.observation.ingested.v1"

    def test_state_updated_subject(self):
        from shared.events.subjects import SAHOOL_FIELD_STATE_UPDATED

        assert SAHOOL_FIELD_STATE_UPDATED == "sahool.field.state.updated.v1"

    def test_irrigation_recommendation_ready_subject(self):
        from shared.events.subjects import SAHOOL_IRRIGATION_RECOMMENDATION_READY

        assert SAHOOL_IRRIGATION_RECOMMENDATION_READY == "sahool.irrigation.recommendation.ready.v1"

    def test_subjects_in_registry(self):
        from shared.events.subjects import SUBJECT_REGISTRY

        assert "field.observation.ingested" in SUBJECT_REGISTRY
        assert "field.state.updated" in SUBJECT_REGISTRY
        assert "irrigation.recommendation.ready" in SUBJECT_REGISTRY

    def test_all_subjects_valid_format(self):
        from shared.events.subjects import (
            SAHOOL_FIELD_OBSERVATION_INGESTED,
            SAHOOL_FIELD_STATE_UPDATED,
            SAHOOL_IRRIGATION_RECOMMENDATION_READY,
            is_valid_subject,
        )

        for subj in (
            SAHOOL_FIELD_OBSERVATION_INGESTED,
            SAHOOL_FIELD_STATE_UPDATED,
            SAHOOL_IRRIGATION_RECOMMENDATION_READY,
        ):
            assert is_valid_subject(subj), f"Invalid subject: {subj}"


# ===========================================================================
# 8. twin_router FastAPI smoke tests
# ===========================================================================


class TestTwinRouterSmoke:
    """Integration smoke tests using FastAPI TestClient (no DB/NATS)."""

    @pytest.fixture
    def client(self):
        try:
            import os
            import sys

            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            from shared.digital_twin.repository import (
                _mem_observations,
                _mem_recommendations,
                _mem_states,
            )

            # Clear state before each test
            _mem_states.clear()
            _mem_observations.clear()
            _mem_recommendations.clear()

            # Add service source to path and import router
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            service_src = os.path.join(repo_root, "apps", "services", "crop-intelligence-service")
            # Evict any cached src.* modules from other services
            stale = [k for k in sys.modules if k == "src" or k.startswith("src.")]
            for k in stale:
                del sys.modules[k]
            if service_src not in sys.path:
                sys.path.insert(0, service_src)
            else:
                sys.path.remove(service_src)
                sys.path.insert(0, service_src)
            from src.twin_router import router
            from shared.auth.dependencies import get_current_user
            from unittest.mock import MagicMock

            app = FastAPI()
            app.include_router(router, prefix="/api/v1")

            # Override auth dependency with a mock user
            mock_user = MagicMock()
            mock_user.id = "user-001"
            mock_user.tenant_id = "tenant-001"
            mock_user.roles = ["farmer"]
            app.dependency_overrides[get_current_user] = lambda: mock_user

            return TestClient(app)
        except ImportError as exc:
            pytest.skip(f"twin_router not importable: {exc}")

    def test_flags_endpoint(self, client):
        response = client.get(f"/api/v1/fields/{FIELD}/twin/flags")
        assert response.status_code == 200
        data = response.json()
        assert "flags" in data
        assert "process_models_enabled" in data["flags"]

    def test_twin_step_endpoint(self, client, monkeypatch):
        monkeypatch.setenv("PROCESS_MODELS_ENABLED", "true")
        monkeypatch.setenv("ASSIMILATION_ENABLED", "false")
        payload = {
            "tenant_id": str(TENANT),
            "day": TODAY.isoformat(),
            "weather": {
                "tmax_c": 28.0,
                "tmin_c": 14.0,
                "solar_radiation_mj_m2": 18.0,
                "relative_humidity_pct": 55.0,
                "wind_speed_m_s": 2.5,
                "precipitation_mm": 0.0,
            },
            "crop_type": "wheat",
            "soil": {"field_capacity_mm_per_m": 300.0, "wilting_point_mm_per_m": 150.0},
            "taw_mm": 180.0,
        }
        response = client.post(f"/api/v1/fields/{FIELD}/twin/step", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "state" in data
        assert "irrigation_recommendation" in data
        assert data["state"]["et0_mm"] > 0.0

    def test_get_state_empty(self, client):
        response = client.get(
            f"/api/v1/fields/{FIELD}/twin/state",
            params={"tenant_id": str(TENANT), "from_date": TODAY.isoformat()},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_recommendation_404_no_state(self, client):
        response = client.get(
            f"/api/v1/fields/{FIELD}/irrigation/recommendation",
            params={"tenant_id": str(TENANT), "day": TODAY.isoformat()},
        )
        assert response.status_code == 404

    def test_ingest_observations(self, client):
        payload = {
            "tenant_id": str(TENANT),
            "observations": [
                {
                    "obs_type": "ndvi",
                    "value": 0.72,
                    "quality": 0.85,
                    "source": "sentinel-2",
                }
            ],
        }
        response = client.post(f"/api/v1/fields/{FIELD}/observations", json=payload)
        assert response.status_code == 200
        assert response.json()["saved"] == 1

    def test_step_then_get_recommendation(self, client, monkeypatch):
        monkeypatch.setenv("PROCESS_MODELS_ENABLED", "true")
        monkeypatch.setenv("ASSIMILATION_ENABLED", "false")
        step_payload = {
            "tenant_id": str(TENANT),
            "day": TODAY.isoformat(),
            "weather": {"tmax_c": 35.0, "tmin_c": 20.0},
            "crop_type": "wheat",
            "taw_mm": 150.0,
        }
        # Run step first
        r1 = client.post(f"/api/v1/fields/{FIELD}/twin/step", json=step_payload)
        assert r1.status_code == 200

        # Get recommendation
        r2 = client.get(
            f"/api/v1/fields/{FIELD}/irrigation/recommendation",
            params={"tenant_id": str(TENANT), "day": TODAY.isoformat()},
        )
        assert r2.status_code == 200
        rec = r2.json()
        assert "recommended_mm" in rec
        assert rec["recommended_mm"] >= 0.0


# ===========================================================================
# 9. Package import smoke
# ===========================================================================


class TestDigitalTwinImport:
    def test_all_exports(self):
        import shared.digital_twin as dt

        assert dt.TwinPipeline is not None
        assert dt.TwinRepository is not None
        assert dt.AssimilationEngine is not None
        assert dt.DecisionEngine is not None
        assert dt.DigitalTwinFlags is not None
        assert dt.FieldDailyState is not None
        assert dt.FieldObservation is not None
        assert dt.IrrigationRecommendation is not None
