"""Tests for irrigation-cycle-engine health and core endpoints."""

import pytest
from fastapi.testclient import TestClient

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from src.main import app


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
        assert data["service"] == "irrigation-cycle-engine"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.unit
class TestET0Calculation:
    def test_et0_basic(self, client):
        """Test basic ET0 calculation."""
        response = client.post("/api/v1/irrigation/et0", json={
            "latitude": 15.35,
            "elevation_m": 2200,
            "weather": [{
                "date": "2026-01-15",
                "temp_min_c": 5.0,
                "temp_max_c": 22.0,
                "humidity_min_pct": 30.0,
                "humidity_max_pct": 65.0,
                "wind_speed_2m_ms": 2.0,
                "solar_radiation_mjm2": 18.0,
                "rainfall_mm": 0.0,
            }],
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["et0_mm"] > 0
        assert data[0]["et0_mm"] < 15  # Reasonable range
        assert data[0]["method"] == "penman_monteith_fao56"

    def test_et0_multiple_days(self, client):
        """Test multi-day ET0 calculation."""
        response = client.post("/api/v1/irrigation/et0", json={
            "latitude": 15.35,
            "elevation_m": 2200,
            "weather": [
                {"date": "2026-01-15", "temp_min_c": 5, "temp_max_c": 22,
                 "solar_radiation_mjm2": 18},
                {"date": "2026-01-16", "temp_min_c": 6, "temp_max_c": 23,
                 "solar_radiation_mjm2": 19},
            ],
        })
        assert response.status_code == 200
        assert len(response.json()) == 2


@pytest.mark.unit
class TestIrrigationCycle:
    def test_cycle_basic(self, client):
        """Test basic irrigation cycle calculation."""
        response = client.post("/api/v1/irrigation/cycle", json={
            "crop": "wheat",
            "field_capacity": 0.32,
            "wilting_point": 0.15,
            "root_depth_m": 1.2,
            "bulk_density": 1.35,
            "depletion_fraction": 0.55,
            "et0_mm_day": 4.5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["cycle_days"] > 0
        assert data["net_irrigation_mm"] > 0
        assert data["etc_mm_day"] > 0
        assert data["crop_name"] == "wheat"

    def test_cycle_with_salinity(self, client):
        """Test cycle with salinity adjustment."""
        response = client.post("/api/v1/irrigation/cycle", json={
            "crop": "wheat",
            "field_capacity": 0.32,
            "wilting_point": 0.15,
            "et0_mm_day": 5.0,
            "ec_water": 3.0,
            "ec_soil": 5.0,
        })
        assert response.status_code == 200
        data = response.json()
        # With salinity, Kc should be adjusted
        if data.get("kc_adjusted"):
            assert data["kc_adjusted"] <= data["kc_used"]


@pytest.mark.unit
class TestYemenData:
    def test_list_crops(self, client):
        response = client.get("/api/v1/yemen/crops")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["crops"]) > 0

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

    def test_crop_not_found(self, client):
        response = client.get("/api/v1/yemen/crops/nonexistent_crop")
        assert response.status_code == 404
