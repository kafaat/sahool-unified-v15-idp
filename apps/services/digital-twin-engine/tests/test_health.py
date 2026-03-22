"""Tests for digital-twin-engine health and core endpoints."""

import os
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
import sys

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from src.main import app

# Valid UUID for tenant context middleware
VALID_TENANT = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
TENANT_HEADER = {"X-Tenant-ID": VALID_TENANT}
@pytest.fixture
def client():
    return TestClient(app)
@pytest.mark.unit
class TestHealthEndpoints:
    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "digital-twin-engine"

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["dt_level"] == "l3_prediction"

    def test_dt_info(self, client):
        response = client.get("/api/v1/digital-twin/info", headers=TENANT_HEADER)
        assert response.status_code == 200
        data = response.json()
        assert "capabilities" in data
        assert data["dt_level"] == "l3_prediction"
@pytest.mark.unit
class TestSimulation:
    def test_basic_simulation(self, client):
        response = client.post(
            "/api/v1/digital-twin/simulate",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-001",
                    "soil_moisture_pct": 50.0,
                    "soil_ec_dsm": 1.0,
                    "crop": "wheat",
                    "growth_stage": "vegetative",
                    "days_after_planting": 30,
                    "lai": 2.0,
                    "biomass_kg_ha": 500.0,
                    "et0_mm_day": 4.5,
                },
                "days_to_simulate": 10,
                "irrigation_schedule": [
                    {"day": 5, "amount_mm": 30.0},
                    {"day": 10, "amount_mm": 30.0},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["simulation_days"] == 10
        assert len(data["daily_states"]) == 10
        assert data["total_irrigation_mm"] > 0
        assert data["final_yield_pct"] > 0

    def test_simulation_with_climate_zone(self, client):
        response = client.post(
            "/api/v1/digital-twin/simulate",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-002",
                    "crop": "date_palm",
                    "soil_moisture_pct": 40.0,
                    "days_after_planting": 60,
                },
                "days_to_simulate": 30,
                "climate_zone": "hadhramaut",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "date_palm"
@pytest.mark.unit
class TestScenarios:
    def test_scenario_comparison(self, client):
        response = client.post(
            "/api/v1/digital-twin/scenarios",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-001",
                    "crop": "wheat",
                    "soil_moisture_pct": 45.0,
                    "et0_mm_day": 5.0,
                },
                "days": 30,
                "scenarios": [
                    {
                        "name": "Conservative",
                        "description": "Minimal irrigation",
                        "irrigation_schedule": [
                            {"day": 10, "amount_mm": 20},
                            {"day": 20, "amount_mm": 20},
                        ],
                    },
                    {
                        "name": "Aggressive",
                        "description": "Frequent irrigation",
                        "irrigation_schedule": [
                            {"day": 5, "amount_mm": 25},
                            {"day": 10, "amount_mm": 25},
                            {"day": 15, "amount_mm": 25},
                            {"day": 20, "amount_mm": 25},
                            {"day": 25, "amount_mm": 25},
                        ],
                    },
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["scenarios"]) == 2
        assert data["best_for_water"] in ["Conservative", "Aggressive"]
        assert data["recommended"] is not None

    def test_scenario_minimum(self, client):
        """Need at least 2 scenarios."""
        response = client.post(
            "/api/v1/digital-twin/scenarios",
            headers=TENANT_HEADER,
            json={
                "field_state": {"field_id": "F1", "crop": "wheat"},
                "days": 10,
                "scenarios": [{"name": "Only one"}],
            },
        )
        assert response.status_code == 400
@pytest.mark.unit
class TestOptimization:
    def test_balanced_optimization(self, client):
        response = client.post(
            "/api/v1/digital-twin/optimize",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-001",
                    "crop": "wheat",
                    "soil_moisture_pct": 50.0,
                    "et0_mm_day": 5.0,
                },
                "days": 60,
                "objectives": ["balanced"],
                "constraints": {
                    "max_water_mm": 300,
                    "max_cost_sar": 3000,
                    "min_yield_pct": 75,
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["pareto_solutions"]) > 0
        assert data["metrics"]["score"] > 0
        assert data["recommendation"] != ""
        assert data["recommendation_ar"] != ""

    def test_minimize_water_optimization(self, client):
        response = client.post(
            "/api/v1/digital-twin/optimize",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-001",
                    "crop": "wheat",
                    "soil_moisture_pct": 50.0,
                },
                "days": 30,
                "objectives": ["minimize_water"],
            },
        )
        assert response.status_code == 200
@pytest.mark.unit
class TestStateUpdate:
    def test_update_state(self, client):
        response = client.post(
            "/api/v1/digital-twin/state/update",
            headers=TENANT_HEADER,
            json={
                "field_id": "FIELD-001",
                "soil_moisture_pct": 42.0,
                "soil_ec_dsm": 1.5,
                "lai": 3.0,
                "crop": "wheat",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "estimated_state" in data
        assert "raw_state" in data

    def test_kalman_convergence(self, client):
        """Test that Kalman filter converges with repeated updates."""
        for val in [40.0, 42.0, 41.0, 41.5, 41.2]:
            response = client.post(
                "/api/v1/digital-twin/state/update",
                headers=TENANT_HEADER,
                json={
                    "field_id": "FIELD-KALMAN",
                    "soil_moisture_pct": val,
                    "soil_ec_dsm": 1.0,
                    "lai": 2.5,
                    "crop": "wheat",
                },
            )
        data = response.json()
        est = data["estimated_state"]["soil_moisture_pct"]
        # Should be close to the last few values
        assert 39.0 < est < 43.0
@pytest.mark.unit
class TestSimulationEdgeCases:
    def test_simulation_high_salinity(self, client):
        """Test simulation under high salinity stress."""
        response = client.post(
            "/api/v1/digital-twin/simulate",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-SAL",
                    "crop": "tomato",
                    "soil_moisture_pct": 50.0,
                    "soil_ec_dsm": 8.0,  # High salinity
                    "et0_mm_day": 5.0,
                    "days_after_planting": 30,
                },
                "days_to_simulate": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # High salinity should reduce yield
        assert data["final_yield_pct"] < 100

    def test_simulation_no_irrigation(self, client):
        """Test simulation without any irrigation events."""
        response = client.post(
            "/api/v1/digital-twin/simulate",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-DRY",
                    "crop": "wheat",
                    "soil_moisture_pct": 30.0,
                    "et0_mm_day": 6.0,
                },
                "days_to_simulate": 15,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_irrigation_mm"] == 0
        # Soil moisture should decrease over time without irrigation
        last_day = data["daily_states"][-1]
        assert last_day["soil_moisture_pct"] < 30.0

    def test_simulation_daily_states_structure(self, client):
        """Verify each daily state has required fields."""
        response = client.post(
            "/api/v1/digital-twin/simulate",
            headers=TENANT_HEADER,
            json={
                "field_state": {
                    "field_id": "FIELD-STRUCT",
                    "crop": "wheat",
                    "soil_moisture_pct": 50.0,
                    "et0_mm_day": 4.0,
                },
                "days_to_simulate": 5,
                "irrigation_schedule": [{"day": 3, "amount_mm": 20.0}],
            },
        )
        assert response.status_code == 200
        data = response.json()
        for state in data["daily_states"]:
            assert "day" in state
            assert "soil_moisture_pct" in state
            assert "biomass_kg_ha" in state
            assert "lai" in state
