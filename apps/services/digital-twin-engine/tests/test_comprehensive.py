"""
Comprehensive unit tests for SAHOOL Digital Twin Engine.
Targets >60% code coverage across models, engine logic, endpoints, and edge cases.
"""
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import os
import sys
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

from src.main import (
    DigitalTwinEngine,
    DTLevel,
    FieldState,
    KalmanStateEstimator,
    OptimizationObjective,
    OptimizationRequest,
    OptimizationResult,
    ScenarioComparison,
    ScenarioRequest,
    ScenarioType,
    SimulationDay,
    SimulationRequest,
    SimulationResult,
    app,
    get_current_user,
)

# Valid UUID for tenant context middleware
VALID_TENANT = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
TENANT_HEADER = {"X-Tenant-ID": VALID_TENANT}
# Override auth dependency for testing
async def _mock_current_user():
    return {"id": "test-user", "tenant_id": VALID_TENANT}
app.dependency_overrides[get_current_user] = _mock_current_user
@pytest.fixture
def client():
    return TestClient(app)
@pytest.fixture
def engine():
    """Create a fresh DigitalTwinEngine for unit tests."""
    return DigitalTwinEngine()
@pytest.fixture
def basic_field_state():
    return FieldState(
        field_id="TEST-001",
        crop="wheat",
        soil_moisture_pct=50.0,
        soil_ec_dsm=1.0,
        lai=2.0,
        biomass_kg_ha=500.0,
        canopy_cover_pct=40.0,
        et0_mm_day=5.0,
        days_after_planting=30,
    )
# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------
class TestEnums:
    def test_dt_level_values(self):
        assert DTLevel.L1_MONITORING == "l1_monitoring"
        assert DTLevel.L3_PREDICTION == "l3_prediction"
        assert DTLevel.L5_AUTONOMY == "l5_autonomy"

    def test_scenario_type_values(self):
        assert ScenarioType.IRRIGATION_STRATEGY == "irrigation_strategy"
        assert ScenarioType.SALINITY_MANAGEMENT == "salinity_management"

    def test_optimization_objective_values(self):
        assert OptimizationObjective.BALANCED == "balanced"
        assert OptimizationObjective.MINIMIZE_WATER == "minimize_water"
        assert OptimizationObjective.MAXIMIZE_YIELD == "maximize_yield"
        assert OptimizationObjective.MINIMIZE_COST == "minimize_cost"
# ---------------------------------------------------------------------------
# Pydantic model tests
# ---------------------------------------------------------------------------
class TestPydanticModels:
    def test_field_state_defaults(self):
        fs = FieldState(field_id="F1")
        assert fs.soil_moisture_pct == 50.0
        assert fs.crop == "wheat"
        assert fs.growth_stage == "vegetative"
        assert fs.lai == 2.0

    def test_simulation_request_defaults(self):
        fs = FieldState(field_id="F1")
        req = SimulationRequest(field_state=fs)
        assert req.days_to_simulate == 30
        assert req.irrigation_schedule is None
        assert req.rainfall_forecast is None

    def test_simulation_day_structure(self):
        sd = SimulationDay(
            day=1,
            date=date.today(),
            soil_moisture_pct=45.0,
            soil_ec_dsm=1.0,
            etc_mm=4.5,
            irrigation_mm=0.0,
            rainfall_mm=5.0,
            drainage_mm=0.0,
            lai=2.1,
            biomass_kg_ha=510.0,
            canopy_cover_pct=41.0,
            water_stress=0.0,
            salinity_stress=0.0,
            cumulative_water_mm=0.0,
            yield_estimate_pct=98.5,
        )
        assert sd.day == 1
        assert sd.yield_estimate_pct == 98.5

    def test_scenario_request(self):
        fs = FieldState(field_id="F1")
        req = ScenarioRequest(
            field_state=fs,
            scenarios=[{"name": "A"}, {"name": "B"}],
        )
        assert req.days == 90

    def test_optimization_request_defaults(self):
        fs = FieldState(field_id="F1")
        req = OptimizationRequest(field_state=fs)
        assert req.days == 90
        assert OptimizationObjective.BALANCED in req.objectives
        assert req.constraints["max_water_mm"] == 500
# ---------------------------------------------------------------------------
# KalmanStateEstimator tests
# ---------------------------------------------------------------------------
class TestKalmanStateEstimator:
    def test_initial_predict(self):
        kf = KalmanStateEstimator(state_dim=3)
        assert kf.initialized is False
        result = kf.predict([50.0, 1.0, 2.0])
        assert kf.initialized is True
        assert result == [50.0, 1.0, 2.0]

    def test_predict_after_init(self):
        kf = KalmanStateEstimator(state_dim=3)
        kf.predict([50.0, 1.0, 2.0])
        result = kf.predict([48.0, 1.1, 2.1])
        assert result[0] == 48.0
        assert result[1] == 1.1

    def test_initial_update(self):
        kf = KalmanStateEstimator(state_dim=3)
        result = kf.update([42.0, 1.5, 3.0])
        assert kf.initialized is True
        assert result == [42.0, 1.5, 3.0]

    def test_update_after_predict(self):
        kf = KalmanStateEstimator(state_dim=3)
        kf.predict([50.0, 1.0, 2.0])
        result = kf.update([48.0, 1.2, 2.5])
        # Kalman gain should pull state toward measurement
        assert 48.0 <= result[0] <= 50.0 or result[0] <= 50.0

    def test_kalman_convergence(self):
        """Repeated updates with same measurement should converge."""
        kf = KalmanStateEstimator(state_dim=3)
        kf.predict([50.0, 1.0, 2.0])
        for _ in range(20):
            result = kf.update([42.0, 1.5, 3.0])
        assert abs(result[0] - 42.0) < 1.0
        assert abs(result[1] - 1.5) < 0.5

    def test_kalman_none_measurement_skip(self):
        """None measurement values should not update corresponding state."""
        kf = KalmanStateEstimator(state_dim=3)
        kf.predict([50.0, 1.0, 2.0])
        result = kf.update([None, 1.5, None])
        # Soil moisture and LAI should remain near original
        assert result[0] == 50.0
        assert abs(result[1] - 1.5) < 1.0
# ---------------------------------------------------------------------------
# DigitalTwinEngine simulation tests
# ---------------------------------------------------------------------------
class TestDigitalTwinEngineSimulation:
    def test_basic_simulation(self, engine, basic_field_state):
        req = SimulationRequest(
            field_state=basic_field_state,
            days_to_simulate=10,
        )
        result = engine.simulate(req)
        assert result.field_id == "TEST-001"
        assert result.crop == "wheat"
        assert result.simulation_days == 10
        assert len(result.daily_states) == 10
        assert result.total_irrigation_mm == 0
        assert result.final_yield_pct > 0

    def test_simulation_with_irrigation(self, engine, basic_field_state):
        req = SimulationRequest(
            field_state=basic_field_state,
            days_to_simulate=10,
            irrigation_schedule=[
                {"day": 3, "amount_mm": 25.0},
                {"day": 7, "amount_mm": 25.0},
            ],
        )
        result = engine.simulate(req)
        assert result.total_irrigation_mm == 50.0
        # Day 3 should have irrigation
        assert result.daily_states[2].irrigation_mm == 25.0

    def test_simulation_with_rainfall(self, engine, basic_field_state):
        req = SimulationRequest(
            field_state=basic_field_state,
            days_to_simulate=5,
            rainfall_forecast=[
                {"day": 2, "amount_mm": 15.0},
            ],
        )
        result = engine.simulate(req)
        assert result.total_rainfall_mm == 15.0
        assert result.daily_states[1].rainfall_mm == 15.0

    def test_simulation_low_moisture_causes_stress(self, engine):
        state = FieldState(
            field_id="DRY-001",
            crop="wheat",
            soil_moisture_pct=15.0,
            et0_mm_day=8.0,
            days_after_planting=30,
        )
        req = SimulationRequest(
            field_state=state,
            days_to_simulate=15,
        )
        result = engine.simulate(req)
        assert result.max_water_stress > 0

    def test_simulation_daily_states_monotonic_biomass(self, engine, basic_field_state):
        """Biomass should generally increase (or at least not go below initial)."""
        basic_field_state.soil_moisture_pct = 35.0  # Above wilting point
        req = SimulationRequest(
            field_state=basic_field_state,
            days_to_simulate=5,
            irrigation_schedule=[
                {"day": 1, "amount_mm": 30},
                {"day": 3, "amount_mm": 30},
                {"day": 5, "amount_mm": 30},
            ],
        )
        result = engine.simulate(req)
        assert result.daily_states[-1].biomass_kg_ha >= basic_field_state.biomass_kg_ha

    def test_simulation_water_use_efficiency(self, engine, basic_field_state):
        req = SimulationRequest(
            field_state=basic_field_state,
            days_to_simulate=10,
            irrigation_schedule=[{"day": 5, "amount_mm": 50}],
        )
        result = engine.simulate(req)
        assert result.water_use_efficiency >= 0
# ---------------------------------------------------------------------------
# Scenario comparison tests
# ---------------------------------------------------------------------------
class TestScenarioComparison:
    def test_compare_two_scenarios(self, engine, basic_field_state):
        req = ScenarioRequest(
            field_state=basic_field_state,
            days=30,
            scenarios=[
                {
                    "name": "Conservative",
                    "irrigation_schedule": [
                        {"day": 10, "amount_mm": 20},
                        {"day": 20, "amount_mm": 20},
                    ],
                },
                {
                    "name": "Aggressive",
                    "irrigation_schedule": [
                        {"day": 5, "amount_mm": 30},
                        {"day": 10, "amount_mm": 30},
                        {"day": 15, "amount_mm": 30},
                        {"day": 20, "amount_mm": 30},
                        {"day": 25, "amount_mm": 30},
                    ],
                },
            ],
        )
        result = engine.compare_scenarios(req)
        assert result.field_id == "TEST-001"
        assert len(result.scenarios) == 2
        assert result.best_for_water in ["Conservative", "Aggressive"]
        assert result.best_for_yield in ["Conservative", "Aggressive"]
        assert result.best_for_cost in ["Conservative", "Aggressive"]
        assert result.recommended != ""
        assert result.recommendation_reason != ""
        assert result.recommendation_reason_ar != ""
# ---------------------------------------------------------------------------
# Optimization tests
# ---------------------------------------------------------------------------
class TestOptimization:
    def test_balanced_optimization(self, engine, basic_field_state):
        req = OptimizationRequest(
            field_state=basic_field_state,
            days=30,
            objectives=[OptimizationObjective.BALANCED],
        )
        result = engine.optimize(req)
        assert result.field_id == "TEST-001"
        assert len(result.pareto_solutions) > 0
        assert result.metrics["score"] > 0
        assert result.recommendation != ""
        assert result.recommendation_ar != ""

    def test_minimize_water_optimization(self, engine, basic_field_state):
        req = OptimizationRequest(
            field_state=basic_field_state,
            days=30,
            objectives=[OptimizationObjective.MINIMIZE_WATER],
        )
        result = engine.optimize(req)
        assert result.objectives == ["minimize_water"]
        assert len(result.pareto_solutions) > 0

    def test_maximize_yield_optimization(self, engine, basic_field_state):
        req = OptimizationRequest(
            field_state=basic_field_state,
            days=30,
            objectives=[OptimizationObjective.MAXIMIZE_YIELD],
        )
        result = engine.optimize(req)
        assert result.objectives == ["maximize_yield"]

    def test_minimize_cost_optimization(self, engine, basic_field_state):
        req = OptimizationRequest(
            field_state=basic_field_state,
            days=30,
            objectives=[OptimizationObjective.MINIMIZE_COST],
        )
        result = engine.optimize(req)
        assert result.objectives == ["minimize_cost"]

    def test_minimize_environmental_optimization(self, engine, basic_field_state):
        req = OptimizationRequest(
            field_state=basic_field_state,
            days=30,
            objectives=[OptimizationObjective.MINIMIZE_ENVIRONMENTAL_IMPACT],
        )
        result = engine.optimize(req)
        assert "minimize_environmental" in result.objectives

    def test_candidate_schedule_generation(self, engine):
        candidates = engine._generate_candidate_schedules(
            days=30,
            constraints={"max_water_mm": 300},
        )
        assert len(candidates) == 5
        names = [c["name"] for c in candidates]
        assert "Fixed 7-day cycle" in names
        assert "Fixed 5-day cycle" in names
        assert "Fixed 10-day cycle" in names
        assert "Front-loaded" in names
        assert "Conservation (60%)" in names

    def test_calculate_score_balanced(self, engine):
        score = engine._calculate_score(
            water=200,
            yield_pct=90,
            cost=2000,
            drainage=20,
            objectives=[OptimizationObjective.BALANCED],
            constraints={"max_water_mm": 500, "max_cost_sar": 5000, "min_yield_pct": 80},
        )
        assert 0 <= score <= 1

    def test_calculate_score_penalty_for_low_yield(self, engine):
        score_good = engine._calculate_score(
            water=200, yield_pct=90, cost=2000, drainage=20,
            objectives=[OptimizationObjective.BALANCED],
            constraints={"max_water_mm": 500, "max_cost_sar": 5000, "min_yield_pct": 80},
        )
        score_bad = engine._calculate_score(
            water=200, yield_pct=50, cost=2000, drainage=20,
            objectives=[OptimizationObjective.BALANCED],
            constraints={"max_water_mm": 500, "max_cost_sar": 5000, "min_yield_pct": 80},
        )
        assert score_good > score_bad

    def test_calculate_score_penalty_for_excess_water(self, engine):
        score_good = engine._calculate_score(
            water=200, yield_pct=90, cost=2000, drainage=20,
            objectives=[OptimizationObjective.BALANCED],
            constraints={"max_water_mm": 500, "max_cost_sar": 5000, "min_yield_pct": 80},
        )
        score_bad = engine._calculate_score(
            water=600, yield_pct=90, cost=2000, drainage=20,
            objectives=[OptimizationObjective.BALANCED],
            constraints={"max_water_mm": 500, "max_cost_sar": 5000, "min_yield_pct": 80},
        )
        assert score_good > score_bad
# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------
class TestHealthEndpoints:
    def test_healthz(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "digital-twin-engine"

    def test_readyz(self, client):
        resp = client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["dt_level"] == "l3_prediction"

    def test_info_endpoint(self, client):
        resp = client.get("/api/v1/digital-twin/info", headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "digital-twin-engine"
        assert "capabilities" in data
        assert data["dt_level"] == "l3_prediction"
class TestSimulationEndpoint:
    def test_simulate_basic(self, client):
        payload = {
            "field_state": {
                "field_id": "F-API-001",
                "crop": "wheat",
                "soil_moisture_pct": 50.0,
                "et0_mm_day": 5.0,
            },
            "days_to_simulate": 5,
        }
        resp = client.post("/api/v1/digital-twin/simulate", json=payload, headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["simulation_days"] == 5
        assert len(data["daily_states"]) == 5

    def test_simulate_with_irrigation_and_rain(self, client):
        payload = {
            "field_state": {
                "field_id": "F-API-002",
                "crop": "wheat",
                "soil_moisture_pct": 45.0,
                "et0_mm_day": 4.0,
            },
            "days_to_simulate": 10,
            "irrigation_schedule": [{"day": 3, "amount_mm": 20}, {"day": 7, "amount_mm": 20}],
            "rainfall_forecast": [{"day": 5, "amount_mm": 10}],
        }
        resp = client.post("/api/v1/digital-twin/simulate", json=payload, headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_irrigation_mm"] == 40.0
        assert data["total_rainfall_mm"] == 10.0
class TestScenariosEndpoint:
    def test_scenarios_valid(self, client):
        payload = {
            "field_state": {
                "field_id": "F-SC-001",
                "crop": "wheat",
                "soil_moisture_pct": 50.0,
                "et0_mm_day": 5.0,
            },
            "days": 20,
            "scenarios": [
                {
                    "name": "Low",
                    "irrigation_schedule": [{"day": 10, "amount_mm": 15}],
                },
                {
                    "name": "High",
                    "irrigation_schedule": [
                        {"day": 5, "amount_mm": 20},
                        {"day": 10, "amount_mm": 20},
                        {"day": 15, "amount_mm": 20},
                    ],
                },
            ],
        }
        resp = client.post("/api/v1/digital-twin/scenarios", json=payload, headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["scenarios"]) == 2
        assert data["recommended"] in ["Low", "High"]

    def test_scenarios_needs_at_least_two(self, client):
        payload = {
            "field_state": {"field_id": "F1", "crop": "wheat"},
            "days": 10,
            "scenarios": [{"name": "Only"}],
        }
        resp = client.post("/api/v1/digital-twin/scenarios", json=payload, headers=TENANT_HEADER)
        assert resp.status_code == 400
class TestOptimizeEndpoint:
    def test_optimize_balanced(self, client):
        payload = {
            "field_state": {
                "field_id": "F-OPT-001",
                "crop": "wheat",
                "soil_moisture_pct": 50.0,
                "et0_mm_day": 5.0,
            },
            "days": 30,
            "objectives": ["balanced"],
        }
        resp = client.post("/api/v1/digital-twin/optimize", json=payload, headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["pareto_solutions"]) > 0
        assert data["metrics"]["score"] > 0
class TestStateUpdateEndpoint:
    def test_update_new_field(self, client):
        payload = {
            "field_id": "KALMAN-NEW",
            "soil_moisture_pct": 42.0,
            "soil_ec_dsm": 1.5,
            "lai": 3.0,
            "crop": "wheat",
        }
        resp = client.post("/api/v1/digital-twin/state/update", json=payload, headers=TENANT_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["field_id"] == "KALMAN-NEW"
        assert "estimated_state" in data
        assert "raw_state" in data

    def test_update_existing_field_converges(self, client):
        """Multiple updates should show Kalman filter convergence."""
        for sm in [40.0, 42.0, 41.0, 41.5]:
            resp = client.post(
                "/api/v1/digital-twin/state/update",
                json={
                    "field_id": "KALMAN-CONV",
                    "soil_moisture_pct": sm,
                    "soil_ec_dsm": 1.0,
                    "lai": 2.5,
                    "crop": "wheat",
                },
                headers=TENANT_HEADER,
            )
        data = resp.json()
        est = data["estimated_state"]["soil_moisture_pct"]
        assert 39.0 < est < 43.0
# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------
class TestEdgeCases:
    def test_simulation_single_day(self, engine, basic_field_state):
        req = SimulationRequest(
            field_state=basic_field_state,
            days_to_simulate=1,
        )
        result = engine.simulate(req)
        assert result.simulation_days == 1
        assert len(result.daily_states) == 1

    def test_field_state_extreme_values(self, engine):
        state = FieldState(
            field_id="EXTREME",
            soil_moisture_pct=0.0,
            soil_ec_dsm=10.0,
            lai=0.1,
            biomass_kg_ha=10.0,
            et0_mm_day=15.0,
        )
        req = SimulationRequest(field_state=state, days_to_simulate=5)
        result = engine.simulate(req)
        # Should not crash
        assert result.simulation_days == 5
        assert result.max_water_stress > 0

    def test_optimization_tight_constraints(self, engine, basic_field_state):
        req = OptimizationRequest(
            field_state=basic_field_state,
            days=30,
            objectives=[OptimizationObjective.BALANCED],
            constraints={
                "max_water_mm": 50,
                "max_cost_sar": 100,
                "min_yield_pct": 95,
                "max_ec_dsm": 1.0,
            },
        )
        result = engine.optimize(req)
        # Should still produce results, even if penalized
        assert len(result.pareto_solutions) > 0
