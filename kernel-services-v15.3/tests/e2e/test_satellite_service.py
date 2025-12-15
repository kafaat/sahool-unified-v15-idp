"""
E2E Tests for Satellite Service - خدمة الأقمار الصناعية
Tests satellite imagery analysis and vegetation indices
"""

import pytest
import httpx
from conftest import SATELLITE_URL, TEST_FIELD_ID


class TestSatelliteServiceHealth:
    """Health check tests for satellite service."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: httpx.AsyncClient):
        """Test /healthz returns healthy status."""
        response = await async_client.get(f"{SATELLITE_URL}/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "satellites" in data
        assert len(data["satellites"]) >= 3  # Sentinel-2, Landsat, MODIS


class TestSatellitesEndpoint:
    """Tests for /v1/satellites endpoint."""

    @pytest.mark.asyncio
    async def test_get_available_satellites(self, async_client: httpx.AsyncClient):
        """Test listing available satellites."""
        response = await async_client.get(f"{SATELLITE_URL}/v1/satellites")
        assert response.status_code == 200
        data = response.json()

        assert "satellites" in data
        satellites = data["satellites"]

        # Check for expected satellites
        satellite_ids = [s["id"] for s in satellites]
        assert "sentinel-2" in satellite_ids
        assert "landsat-8" in satellite_ids
        assert "modis" in satellite_ids

        # Validate satellite structure
        sentinel = next(s for s in satellites if s["id"] == "sentinel-2")
        assert "resolution" in sentinel
        assert "bands" in sentinel
        assert sentinel["resolution"] == 10


class TestRegionsEndpoint:
    """Tests for /v1/regions (Yemen governorates)."""

    @pytest.mark.asyncio
    async def test_get_yemen_regions(self, async_client: httpx.AsyncClient):
        """Test listing Yemen regions with all 22 governorates."""
        response = await async_client.get(f"{SATELLITE_URL}/v1/regions")
        assert response.status_code == 200
        data = response.json()

        assert "regions" in data
        regions = data["regions"]

        # Should have all 22 Yemen governorates
        assert len(regions) >= 22

        # Check for key regions
        region_ids = [r["id"] for r in regions]
        assert "sana'a" in region_ids
        assert "aden" in region_ids
        assert "taiz" in region_ids
        assert "hodeidah" in region_ids
        assert "socotra" in region_ids  # Island governorate

        # Validate region structure
        sanaa = next(r for r in regions if r["id"] == "sana'a")
        assert "name_ar" in sanaa
        assert "lat" in sanaa
        assert "lon" in sanaa
        assert sanaa["name_ar"] == "صنعاء"


class TestImageryRequest:
    """Tests for /v1/imagery/request endpoint."""

    @pytest.mark.asyncio
    async def test_request_satellite_imagery(self, async_client: httpx.AsyncClient, test_field_data):
        """Test requesting satellite imagery for a field."""
        request_data = {
            "field_id": test_field_data["field_id"],
            "satellite": "sentinel-2",
            "bands": ["B04", "B08", "B03"],
            "location": test_field_data["location"],
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            }
        }

        response = await async_client.post(
            f"{SATELLITE_URL}/v1/imagery/request",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "status" in data
        assert "imagery" in data

        imagery = data["imagery"]
        assert "scene_id" in imagery
        assert "acquisition_date" in imagery
        assert "cloud_cover" in imagery
        assert imagery["cloud_cover"] <= 100

    @pytest.mark.asyncio
    async def test_request_imagery_invalid_satellite(self, async_client: httpx.AsyncClient):
        """Test requesting imagery with invalid satellite."""
        request_data = {
            "field_id": "test_field",
            "satellite": "invalid-satellite",
            "location": {"lat": 15.3694, "lon": 44.1910}
        }

        response = await async_client.post(
            f"{SATELLITE_URL}/v1/imagery/request",
            json=request_data
        )
        assert response.status_code in [400, 422]


class TestFieldAnalysis:
    """Tests for /v1/analyze endpoint - vegetation indices."""

    @pytest.mark.asyncio
    async def test_analyze_field_health(self, async_client: httpx.AsyncClient, test_field_data):
        """Test comprehensive field health analysis."""
        analysis_request = {
            "field_id": test_field_data["field_id"],
            "satellite": "sentinel-2",
            "location": test_field_data["location"],
            "area_hectares": test_field_data["area_hectares"]
        }

        response = await async_client.post(
            f"{SATELLITE_URL}/v1/analyze",
            json=analysis_request
        )
        assert response.status_code == 200
        data = response.json()

        # Check vegetation indices
        assert "vegetation_indices" in data
        indices = data["vegetation_indices"]

        # All 6 indices should be present
        assert "ndvi" in indices
        assert "ndwi" in indices
        assert "evi" in indices
        assert "savi" in indices
        assert "lai" in indices
        assert "ndmi" in indices

        # NDVI should be between -1 and 1
        assert -1 <= indices["ndvi"] <= 1

        # Check health score
        assert "health_score" in data
        assert 0 <= data["health_score"] <= 100

        # Check bilingual status
        assert "status" in data
        assert "status_ar" in data

    @pytest.mark.asyncio
    async def test_analyze_returns_anomalies(self, async_client: httpx.AsyncClient, test_field_data):
        """Test that analysis includes anomaly detection."""
        analysis_request = {
            "field_id": test_field_data["field_id"],
            "satellite": "sentinel-2",
            "location": test_field_data["location"]
        }

        response = await async_client.post(
            f"{SATELLITE_URL}/v1/analyze",
            json=analysis_request
        )
        assert response.status_code == 200
        data = response.json()

        assert "anomalies" in data
        # Anomalies should be a list
        assert isinstance(data["anomalies"], list)


class TestTimeSeries:
    """Tests for /v1/timeseries/{field_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_ndvi_timeseries(self, async_client: httpx.AsyncClient):
        """Test historical NDVI trend data."""
        response = await async_client.get(
            f"{SATELLITE_URL}/v1/timeseries/{TEST_FIELD_ID}",
            params={"days": 30, "index": "ndvi"}
        )
        assert response.status_code == 200
        data = response.json()

        assert "field_id" in data
        assert "timeseries" in data
        assert "trend" in data

        timeseries = data["timeseries"]
        assert len(timeseries) > 0

        # Each point should have date and value
        for point in timeseries:
            assert "date" in point
            assert "value" in point
            assert -1 <= point["value"] <= 1

    @pytest.mark.asyncio
    async def test_timeseries_different_periods(self, async_client: httpx.AsyncClient):
        """Test timeseries for different time periods."""
        for days in [7, 30, 90, 365]:
            response = await async_client.get(
                f"{SATELLITE_URL}/v1/timeseries/{TEST_FIELD_ID}",
                params={"days": days}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["timeseries"]) > 0
