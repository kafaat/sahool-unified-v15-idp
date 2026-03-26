"""Tests for irrigation-cycle-engine health and core endpoints."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

try:
    from fastapi.testclient import TestClient
    from src.main import app
except ImportError:
    pytest.skip("irrigation-cycle-engine dependencies not installed", allow_module_level=True)

TENANT_HEADER = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}


@pytest.fixture
def client():
    return TestClient(app, headers=TENANT_HEADER)


@pytest.mark.unit
class TestHealthEndpoints:
    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "irrigation-cycle-engine"
        assert "version" in data

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.unit
class TestET0Calculation:
    def test_et0_basic(self, client):
        """Test basic ET0 calculation."""
        response = client.post(
            "/api/v1/irrigation/et0",
            json={
                "latitude": 15.35,
                "elevation_m": 2200,
                "weather": [
                    {
                        "date": "2026-01-15",
                        "temp_min_c": 5.0,
                        "temp_max_c": 22.0,
                        "humidity_min_pct": 30.0,
                        "humidity_max_pct": 65.0,
                        "wind_speed_2m_ms": 2.0,
                        "solar_radiation_mjm2": 18.0,
                        "rainfall_mm": 0.0,
                    }
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["et0_mm"] > 0
        assert data[0]["et0_mm"] < 15  # Reasonable range
        assert data[0]["method"] == "penman_monteith_fao56"

    def test_et0_multiple_days(self, client):
        """Test multi-day ET0 calculation."""
        response = client.post(
            "/api/v1/irrigation/et0",
            json={
                "latitude": 15.35,
                "elevation_m": 2200,
                "weather": [
                    {
                        "date": "2026-01-15",
                        "temp_min_c": 5,
                        "temp_max_c": 22,
                        "solar_radiation_mjm2": 18,
                    },
                    {
                        "date": "2026-01-16",
                        "temp_min_c": 6,
                        "temp_max_c": 23,
                        "solar_radiation_mjm2": 19,
                    },
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Both days should have positive ET0
        assert all(d["et0_mm"] > 0 for d in data)

    def test_et0_zero_wind_radiation(self, client):
        """Test ET0 with zero wind and minimal radiation (edge case)."""
        response = client.post(
            "/api/v1/irrigation/et0",
            json={
                "latitude": 15.35,
                "elevation_m": 2200,
                "weather": [
                    {
                        "date": "2026-06-15",
                        "temp_min_c": 20.0,
                        "temp_max_c": 35.0,
                        "wind_speed_2m_ms": 0.0,
                        "solar_radiation_mjm2": 1.0,
                    }
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should still return non-negative ET0
        assert data[0]["et0_mm"] >= 0


@pytest.mark.unit
class TestIrrigationCycle:
    def test_cycle_basic(self, client):
        """Test basic irrigation cycle calculation."""
        response = client.post(
            "/api/v1/irrigation/cycle",
            json={
                "crop": "wheat",
                "field_capacity": 0.32,
                "wilting_point": 0.15,
                "root_depth_m": 1.2,
                "bulk_density": 1.35,
                "depletion_fraction": 0.55,
                "et0_mm_day": 4.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["cycle_days"] > 0
        assert data["net_irrigation_mm"] > 0
        assert data["etc_mm_day"] > 0
        assert data["crop_name"] == "wheat"
        assert data["crop_name_ar"] == "القمح"

    def test_cycle_with_salinity(self, client):
        """Test cycle with salinity adjustment - EC above wheat threshold."""
        response = client.post(
            "/api/v1/irrigation/cycle",
            json={
                "crop": "tomato",
                "field_capacity": 0.28,
                "wilting_point": 0.12,
                "et0_mm_day": 5.0,
                "ec_water": 3.0,
                "ec_soil": 5.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Tomato threshold is 2.5, EC soil 5.0 > 2.5, so adjustment expected
        assert data["kc_adjusted"] is not None
        assert data["kc_adjusted"] < data["kc_used"]
        assert data["leaching_fraction"] is not None
        assert data["leaching_fraction"] > 0

    def test_cycle_zero_et(self, client):
        """Test cycle when ET0 is zero (no evapotranspiration)."""
        response = client.post(
            "/api/v1/irrigation/cycle",
            json={
                "crop": "wheat",
                "field_capacity": 0.30,
                "wilting_point": 0.12,
                "et0_mm_day": 0.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should default to 30 days when ET is zero
        assert data["cycle_days"] == 30.0


@pytest.mark.unit
class TestIrrigationSchedule:
    def test_schedule_basic(self, client):
        """Test multi-day irrigation schedule generation."""
        response = client.post(
            "/api/v1/irrigation/schedule",
            json={
                "crop": "wheat",
                "soil_profile": "highland_clay_loam",
                "climate_zone": "highlands",
                "start_date": "2026-01-15",
                "days": 30,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "wheat"
        assert data["crop_ar"] == "القمح"
        assert len(data["schedule"]) == 30
        assert data["total_water_mm"] >= 0
        assert data["irrigation_events"] >= 0

    def test_schedule_with_salinity(self, client):
        """Test schedule with saline water."""
        response = client.post(
            "/api/v1/irrigation/schedule",
            json={
                "crop": "date_palm",
                "soil_profile": "hadhramaut_silt_loam",
                "climate_zone": "hadhramaut",
                "start_date": "2026-03-01",
                "days": 60,
                "ec_water": 3.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "date_palm"
        assert data["total_water_mm"] > 0  # Should have irrigation events

    def test_schedule_unknown_crop(self, client):
        """Test schedule with unknown crop returns 400."""
        response = client.post(
            "/api/v1/irrigation/schedule",
            json={
                "crop": "nonexistent_crop",
                "soil_profile": "highland_clay_loam",
                "climate_zone": "highlands",
                "start_date": "2026-01-15",
                "days": 10,
            },
        )
        assert response.status_code == 400


@pytest.mark.unit
class TestSalinityAssessment:
    def test_salinity_assessment(self, client):
        """Test salinity assessment endpoint."""
        response = client.post(
            "/api/v1/irrigation/salinity-assessment",
            params={"ec_water": 3.0, "crop": "tomato", "kc": 1.15},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ec_water"] == 3.0
        assert data["risk"] in ["none", "slight_moderate", "severe"]
        assert data["yield_reduction_pct"] >= 0
        assert data["leaching_fraction"] >= 0
        assert len(data["recommendations"]) > 0
        assert len(data["recommendations_ar"]) > 0

    def test_salinity_assessment_with_sar(self, client):
        """Test salinity assessment with SAR inputs."""
        response = client.post(
            "/api/v1/irrigation/salinity-assessment",
            params={
                "ec_water": 2.0,
                "crop": "wheat",
                "kc": 1.15,
                "na": 10.0,
                "ca": 4.0,
                "mg": 2.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sar"] > 0


@pytest.mark.unit
class TestYemenData:
    def test_list_crops(self, client):
        response = client.get("/api/v1/yemen/crops")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["crops"]) > 0

    def test_list_crops_filtered(self, client):
        """Test crop listing with filters."""
        response = client.get("/api/v1/yemen/crops", params={"crop_type": "cereal"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert all(c["crop_type"] == "cereal" for c in data["crops"])

    def test_list_crops_by_region(self, client):
        """Test crop listing filtered by southern_coast region."""
        response = client.get("/api/v1/yemen/crops", params={"region": "southern_coast"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0  # Should now have crops after fix

    def test_get_crop_info(self, client):
        response = client.get("/api/v1/yemen/crops/wheat")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Wheat"
        assert data["name_ar"] == "القمح"
        assert len(data["growth_stages"]) > 0

    def test_list_climate_zones(self, client):
        response = client.get("/api/v1/yemen/climate-zones")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0

    def test_list_soils(self, client):
        response = client.get("/api/v1/yemen/soils")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0

    def test_list_soils_by_region(self, client):
        """Test soil listing filtered by region."""
        response = client.get("/api/v1/yemen/soils", params={"region": "highlands"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert all("highland" in p["name"].lower() or p["region"] == "highlands" for p in data["profiles"])

    def test_crop_not_found(self, client):
        response = client.get("/api/v1/yemen/crops/nonexistent_crop")
        assert response.status_code == 404
