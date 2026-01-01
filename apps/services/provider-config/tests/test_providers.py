"""
SAHOOL Provider Configuration Service - Unit Tests
اختبارات خدمة إدارة المزودين
"""

import pytest
from fastapi.testclient import TestClient

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app, MAP_PROVIDERS, WEATHER_PROVIDERS, SATELLITE_PROVIDERS


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


class TestRootEndpoint:
    """Root endpoint tests"""

    def test_root(self, client):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "SAHOOL" in data["service"]


class TestHealthEndpoint:
    """Health check endpoint tests"""

    def test_health_check(self, client):
        """Test health check returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestListProviders:
    """Provider listing tests"""

    def test_list_all_providers(self, client):
        """Test listing all providers"""
        response = client.get("/providers")
        assert response.status_code == 200
        data = response.json()
        assert "map_providers" in data
        assert "weather_providers" in data
        assert "satellite_providers" in data
        assert len(data["map_providers"]) > 0
        assert len(data["weather_providers"]) > 0
        assert len(data["satellite_providers"]) > 0

    def test_list_map_providers(self, client):
        """Test listing map providers"""
        response = client.get("/providers/maps")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "free_providers" in data
        assert len(data["providers"]) == len(MAP_PROVIDERS)
        # OpenStreetMap should be in free providers
        assert "openstreetmap" in data["free_providers"]

    def test_list_weather_providers(self, client):
        """Test listing weather providers"""
        response = client.get("/providers/weather")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "free_providers" in data
        assert len(data["providers"]) == len(WEATHER_PROVIDERS)
        # Open-Meteo should be in free providers
        assert "open_meteo" in data["free_providers"]

    def test_list_satellite_providers(self, client):
        """Test listing satellite providers"""
        response = client.get("/providers/satellite")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "free_providers" in data
        assert len(data["providers"]) == len(SATELLITE_PROVIDERS)


class TestMapProviderDetails:
    """Map provider detail tests"""

    def test_map_provider_has_required_fields(self, client):
        """Test that map providers have all required fields"""
        response = client.get("/providers/maps")
        data = response.json()

        for provider in data["providers"]:
            assert "id" in provider
            assert "name" in provider
            assert "name_ar" in provider
            assert "url_template" in provider
            assert "requires_api_key" in provider
            assert "max_zoom" in provider
            assert "attribution" in provider

    def test_openstreetmap_is_free(self, client):
        """Test that OpenStreetMap doesn't require API key"""
        response = client.get("/providers/maps")
        data = response.json()

        osm = next((p for p in data["providers"] if p["id"] == "openstreetmap"), None)
        assert osm is not None
        assert osm["requires_api_key"] is False
        assert osm["cost_per_1k_requests"] == 0


class TestWeatherProviderDetails:
    """Weather provider detail tests"""

    def test_weather_provider_has_required_fields(self, client):
        """Test that weather providers have all required fields"""
        response = client.get("/providers/weather")
        data = response.json()

        for provider in data["providers"]:
            assert "id" in provider
            assert "name" in provider
            assert "name_ar" in provider
            assert "base_url" in provider
            assert "requires_api_key" in provider
            assert "forecast_days" in provider

    def test_open_meteo_is_free(self, client):
        """Test that Open-Meteo doesn't require API key"""
        response = client.get("/providers/weather")
        data = response.json()

        om = next((p for p in data["providers"] if p["id"] == "open_meteo"), None)
        assert om is not None
        assert om["requires_api_key"] is False
        assert om["cost_per_1k_requests"] == 0
        assert om["forecast_days"] == 16


class TestSatelliteProviderDetails:
    """Satellite provider detail tests"""

    def test_satellite_provider_has_required_fields(self, client):
        """Test that satellite providers have all required fields"""
        response = client.get("/providers/satellite")
        data = response.json()

        for provider in data["providers"]:
            assert "id" in provider
            assert "name" in provider
            assert "name_ar" in provider
            assert "base_url" in provider
            assert "resolution_meters" in provider
            assert "revisit_days" in provider
            assert "indices" in provider


class TestProviderHealthCheck:
    """Provider health check tests"""

    def test_check_map_provider(self, client):
        """Test checking a map provider health"""
        response = client.post(
            "/providers/check",
            json={
                "provider_type": "map",
                "provider_name": "openstreetmap",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "provider_name" in data
        assert "status" in data
        assert "last_check" in data

    def test_check_unknown_provider(self, client):
        """Test checking unknown provider returns error"""
        response = client.post(
            "/providers/check",
            json={
                "provider_type": "map",
                "provider_name": "unknown_provider",
            },
        )
        assert response.status_code == 400

    def test_check_weather_provider_without_key(self, client):
        """Test checking weather provider that requires API key"""
        response = client.post(
            "/providers/check",
            json={
                "provider_type": "weather",
                "provider_name": "openweathermap",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should report error because API key is required
        assert data["status"] == "error"
        assert "API key required" in data["error_message"]


class TestTenantConfiguration:
    """Tenant configuration tests"""

    def test_get_default_config(self, client):
        """Test getting default config for new tenant"""
        response = client.get("/config/new_tenant")
        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == "new_tenant"
        assert data["is_default"] is True
        assert "map_providers" in data
        assert "weather_providers" in data
        # Default should have OSM and Open-Meteo
        assert len(data["map_providers"]) > 0
        assert len(data["weather_providers"]) > 0

    def test_update_tenant_config(self, client):
        """Test updating tenant configuration"""
        config = {
            "tenant_id": "test_tenant",
            "map_providers": [
                {
                    "provider_name": "mapbox_streets",
                    "api_key": "test_key",
                    "priority": "primary",
                    "enabled": True,
                }
            ],
            "weather_providers": [],
            "satellite_providers": [],
        }
        response = client.post("/config/test_tenant", json=config)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_reset_tenant_config(self, client):
        """Test resetting tenant configuration"""
        # First set a config
        config = {
            "tenant_id": "reset_tenant",
            "map_providers": [],
            "weather_providers": [],
            "satellite_providers": [],
        }
        client.post("/config/reset_tenant", json=config)

        # Then reset
        response = client.delete("/config/reset_tenant")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestProviderRecommendations:
    """Provider recommendations tests"""

    def test_get_free_recommendations(self, client):
        """Test getting free provider recommendations"""
        response = client.get("/providers/recommend?budget=free&use_case=agricultural")
        assert response.status_code == 200
        data = response.json()
        assert data["budget"] == "free"
        assert data["use_case"] == "agricultural"
        assert "map" in data
        assert "weather" in data
        # Should recommend OSM and Open-Meteo for free tier
        map_providers = [r["provider"] for r in data["map"]]
        assert "openstreetmap" in map_providers

    def test_get_low_budget_recommendations(self, client):
        """Test getting low budget recommendations"""
        response = client.get("/providers/recommend?budget=low")
        assert response.status_code == 200
        data = response.json()
        assert data["budget"] == "low"
        assert "satellite" in data

    def test_get_high_budget_recommendations(self, client):
        """Test getting high budget recommendations"""
        response = client.get("/providers/recommend?budget=high")
        assert response.status_code == 200
        data = response.json()
        assert data["budget"] == "high"
        # Should include premium providers
        sat_providers = [r["provider"] for r in data.get("satellite", [])]
        assert "planet_labs" in sat_providers

    def test_offline_required_recommendations(self, client):
        """Test recommendations with offline requirement"""
        response = client.get("/providers/recommend?offline_required=true&budget=free")
        assert response.status_code == 200
        data = response.json()
        assert data["offline_required"] is True


class TestProviderEnums:
    """Provider enum tests"""

    def test_all_map_provider_ids_valid(self, client):
        """Test that all map provider IDs are valid enum values"""
        response = client.get("/providers/maps")
        data = response.json()

        valid_ids = [
            "openstreetmap",
            "google_maps",
            "google_satellite",
            "google_hybrid",
            "mapbox_streets",
            "mapbox_satellite",
            "mapbox_hybrid",
            "esri_satellite",
            "esri_streets",
            "opentopomap",
        ]
        for provider in data["providers"]:
            assert provider["id"] in valid_ids

    def test_all_weather_provider_ids_valid(self, client):
        """Test that all weather provider IDs are valid enum values"""
        response = client.get("/providers/weather")
        data = response.json()

        valid_ids = ["open_meteo", "openweathermap", "weather_api", "visual_crossing"]
        for provider in data["providers"]:
            assert provider["id"] in valid_ids

    def test_all_satellite_provider_ids_valid(self, client):
        """Test that all satellite provider IDs are valid enum values"""
        response = client.get("/providers/satellite")
        data = response.json()

        valid_ids = ["sentinel_hub", "planet_labs", "maxar", "landsat"]
        for provider in data["providers"]:
            assert provider["id"] in valid_ids
