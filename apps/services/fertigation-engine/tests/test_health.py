"""Tests for fertigation-engine health and core endpoints."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

try:
    from fastapi.testclient import TestClient
    from src.main import app
except ImportError:
    pytest.skip("fertigation-engine dependencies not installed", allow_module_level=True)

TENANT_HEADER = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}


class _MockUser:
    id = "test-user-fertigation"
    tenant_id = "00000000-0000-0000-0000-000000000001"
    email = "test@sahool.app"
    role = "admin"


@pytest.fixture
def client():
    from src.main import get_current_user as real_get_current_user

    app.dependency_overrides[real_get_current_user] = lambda: _MockUser()
    c = TestClient(app, headers=TENANT_HEADER)
    yield c
    app.dependency_overrides.clear()


@pytest.mark.unit
class TestHealthEndpoints:
    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "fertigation-engine"

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["crops_with_npk"] > 0
        assert data["fertilizers_available"] > 0


@pytest.mark.unit
class TestFertigationPlan:
    def test_basic_plan(self, client):
        response = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "wheat",
                "growth_phase": "tillering",
                "field_area_ha": 1.0,
                "irrigation_volume_m3": 50.0,
                "ec_water": 0.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "wheat"
        assert data["n_required_kg_ha"] > 0
        assert len(data["fertilizer_plan"]) > 0
        assert data["ec_total"] > 0

    def test_plan_with_soil_nutrients(self, client):
        """Test that soil nutrients reduce applied amounts."""
        # Without soil data
        resp1 = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "tomato",
                "growth_phase": "vegetative",
                "irrigation_volume_m3": 30.0,
            },
        )
        # With existing soil N
        resp2 = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "tomato",
                "growth_phase": "vegetative",
                "irrigation_volume_m3": 30.0,
                "soil_n_ppm": 40.0,
            },
        )
        data1 = resp1.json()
        data2 = resp2.json()
        assert data2["n_adjusted_kg_ha"] <= data1["n_adjusted_kg_ha"]

    def test_ec_limit_warning(self, client):
        """Test EC limit checking."""
        response = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "wheat",
                "growth_phase": "tillering",
                "field_area_ha": 5.0,
                "irrigation_volume_m3": 10.0,  # Small volume → high concentration
                "ec_water": 2.0,
                "max_ec_solution": 2.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ec_total"] > 0
        # With small volume and high ec_water, likely exceeds limit
        if not data["ec_within_limit"]:
            assert any("EC" in r or "الموصلية" in r for r in data["recommendations"] + data["recommendations_ar"])

    def test_unknown_crop_fallback(self, client):
        """Test that unknown crops use generic NPK fallback."""
        response = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "dragon_fruit",
                "growth_phase": "vegetative",
                "irrigation_volume_m3": 40.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "dragon_fruit"
        # Should use fallback values (n=30, p=15, k=25)
        assert data["n_required_kg_ha"] == 30.0
        assert data["p_required_kg_ha"] == 15.0
        assert data["k_required_kg_ha"] == 25.0

    def test_preferred_fertilizers(self, client):
        """Test that preferred_fertilizers are respected."""
        response = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "wheat",
                "growth_phase": "tillering",
                "irrigation_volume_m3": 50.0,
                "preferred_fertilizers": ["ammonium_nitrate", "sop"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        fert_names = [f["fertilizer"] for f in data["fertilizer_plan"]]
        # Should use ammonium_nitrate for N instead of default urea
        assert "ammonium_nitrate" in fert_names
        # Should use sop for K instead of default kcl
        assert "sop" in fert_names

    def test_plan_with_all_soil_nutrients(self, client):
        """Test soil N, P, K credits all reduce applied amounts."""
        resp = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "tomato",
                "growth_phase": "fruit_development",
                "irrigation_volume_m3": 50.0,
                "soil_n_ppm": 50.0,
                "soil_p_ppm": 30.0,
                "soil_k_ppm": 100.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # Adjusted values should be less than or equal to required
        assert data["n_adjusted_kg_ha"] <= data["n_required_kg_ha"]
        assert data["p_adjusted_kg_ha"] <= data["p_required_kg_ha"]
        assert data["k_adjusted_kg_ha"] <= data["k_required_kg_ha"]


@pytest.mark.unit
class TestNutrientBalance:
    def test_balance_surplus(self, client):
        response = client.post(
            "/api/v1/fertigation/nutrient-balance",
            json={
                "field_id": "FIELD-001",
                "crop": "wheat",
                "entries": [
                    {"type": "applied", "n_kg": 120, "p_kg": 60, "k_kg": 75},
                    {"type": "removed", "n_kg": 50, "p_kg": 20, "k_kg": 30},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["n_balance_kg_ha"] > 0  # Surplus
        assert data["surplus_alert"] is True

    def test_balance_deficit(self, client):
        response = client.post(
            "/api/v1/fertigation/nutrient-balance",
            json={
                "field_id": "FIELD-001",
                "crop": "tomato",
                "entries": [
                    {"type": "applied", "n_kg": 20, "p_kg": 10, "k_kg": 15},
                    {"type": "removed", "n_kg": 60, "p_kg": 30, "k_kg": 40},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["n_balance_kg_ha"] < 0  # Deficit
        assert data["deficit_alert"] is True


@pytest.mark.unit
class TestReferenceData:
    def test_list_fertilizers(self, client):
        response = client.get("/api/v1/fertigation/fertilizers")
        assert response.status_code == 200
        assert response.json()["total"] > 0

    def test_get_crop_npk(self, client):
        response = client.get("/api/v1/fertigation/crops/wheat/npk")
        assert response.status_code == 200
        data = response.json()
        assert "total_requirements_kg_ha" in data
        assert data["total_requirements_kg_ha"]["n"] > 0

    def test_crop_npk_not_found(self, client):
        response = client.get("/api/v1/fertigation/crops/nonexistent/npk")
        assert response.status_code == 404

    def test_list_crops_with_npk(self, client):
        response = client.get("/api/v1/fertigation/crops")
        assert response.status_code == 200
        assert response.json()["total"] > 0

    def test_list_growth_phases(self, client):
        response = client.get("/api/v1/fertigation/growth-phases")
        assert response.status_code == 200
        assert len(response.json()["phases"]) > 0
