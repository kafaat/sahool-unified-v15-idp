"""
Tests for the ``GET /v1/index-map/{field_id}`` raster-overlay endpoint
on vegetation-analysis-service.

اختبارات نقطة /v1/index-map/{field_id} التي تُرجع بيانات تراكب الراستر
لأي مؤشر طيفي (NDVI/EVI/SAVI/NDRE/NDWI/LAI) — تحقّق أنّها تستجيب 200،
تُرجع colour ramp صحيحاً، وتدعم وضع "محاكاة" عندما لا تتوفّر بيانات
Sentinel Hub الحقيقية.

The endpoint is the unified replacement for the previously-broken
frontend call to ``/api/v1/fields/{fieldId}/ndvi/map`` (which 404'd
because the route never existed). Tests exercise the FastAPI app via
``TestClient`` with ``get_current_user`` overridden to a stub user.
"""

import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.auth.dependencies import get_current_user  # noqa: E402

# Importing main.py initialises FastAPI app + middleware. That's expected.
from src.main import (  # noqa: E402
    _build_sentinel_hub_wms_url,
    _INDEX_MAP_COLOR_STOPS,
    _INDEX_VALUE_RANGES,
    _placeholder_raster_data_url,
    app,
)


@pytest.fixture(scope="module")
def client() -> TestClient:
    """TestClient with a stubbed ``get_current_user`` dependency."""

    def _stub_user() -> SimpleNamespace:
        return SimpleNamespace(
            id="user-1",
            tenant_id="tenant-001",
            email="t@example.com",
            roles=[],
        )

    app.dependency_overrides[get_current_user] = _stub_user
    try:
        c = TestClient(app)
        # Middleware demands an X-Tenant-ID header on every request.
        c.headers.update({"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"})
        yield c
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def no_sentinel_env(monkeypatch):
    """Force simulated mode by clearing the Sentinel Hub instance id."""
    monkeypatch.setenv("SENTINEL_HUB_INSTANCE_ID", "")
    return None


# ---------------------------------------------------------------------------
# Helpers (unit-tested directly — no HTTP needed)
# ---------------------------------------------------------------------------


class TestPlaceholderRasterDataUrl:
    def test_returns_data_url_with_index_marker(self):
        url = _placeholder_raster_data_url("ndvi")
        assert url.startswith("data:image/png;base64,")
        assert url.endswith("#index=ndvi")

    def test_distinct_per_index(self):
        assert _placeholder_raster_data_url("ndvi") != _placeholder_raster_data_url("evi")


class TestSentinelHubWmsUrl:
    def test_includes_required_wms_params(self):
        url = _build_sentinel_hub_wms_url(
            instance_id="abc-123",
            index_name="ndvi",
            bbox=(44.18, 15.34, 44.21, 15.37),
            target_date="2026-01-15",
        )
        assert "https://services.sentinel-hub.com/ogc/wms/abc-123" in url
        assert "REQUEST=GetMap" in url
        assert "BBOX=44.18,15.34,44.21,15.37" in url
        assert "CRS=EPSG:4326" in url
        assert "LAYERS=NDVI" in url
        assert "TIME=2026-01-15" in url
        assert "FORMAT=image/png" in url

    def test_layer_name_uppercased(self):
        url = _build_sentinel_hub_wms_url(
            instance_id="x",
            index_name="ndre",
            bbox=(0, 0, 1, 1),
            target_date="2026-01-01",
        )
        assert "LAYERS=NDRE" in url


# ---------------------------------------------------------------------------
# Color-stop / value-range invariants
# ---------------------------------------------------------------------------


class TestColorMapMetadata:
    @pytest.mark.parametrize("idx", ["ndvi", "evi", "savi", "ndre", "ndwi", "lai"])
    def test_every_supported_index_has_stops_and_range(self, idx):
        assert idx in _INDEX_MAP_COLOR_STOPS
        assert idx in _INDEX_VALUE_RANGES
        stops = _INDEX_MAP_COLOR_STOPS[idx]
        assert len(stops) >= 2
        values = [v for v, _ in stops]
        assert values == sorted(values)
        for _, colour in stops:
            assert colour.startswith("#")
            assert len(colour) in (4, 7)

    def test_value_ranges_match_stops_extremes(self):
        for idx, (vmin, vmax) in _INDEX_VALUE_RANGES.items():
            stops = _INDEX_MAP_COLOR_STOPS[idx]
            assert vmin <= stops[0][0]
            assert vmax >= stops[-1][0]


# ---------------------------------------------------------------------------
# HTTP endpoint behaviour
# ---------------------------------------------------------------------------


class TestGetIndexMapEndpoint:
    def test_simulated_mode_when_no_sentinel_env(self, client, no_sentinel_env):
        r = client.get("/v1/index-map/FIELD-1", params={"index": "ndvi"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["fieldId"] == "FIELD-1"
        assert body["indexType"] == "ndvi"
        assert body["simulated"] is True
        assert body["dataSource"] == "simulated"
        # Bounds shape + ordering
        bounds = body["bounds"]
        assert len(bounds) == 2 and len(bounds[0]) == 2
        south, west = bounds[0]
        north, east = bounds[1]
        assert south < north and west < east
        # Color scale is present and renderable
        cs = body["colorScale"]
        assert cs["min"] < cs["max"]
        assert len(cs["stops"]) >= 2
        # Raster URL is non-null even in simulated mode (transparent PNG)
        assert body["rasterUrl"]

    def test_real_mode_emits_sentinel_hub_url(self, client, monkeypatch):
        monkeypatch.setenv("SENTINEL_HUB_INSTANCE_ID", "demo-instance")
        r = client.get(
            "/v1/index-map/FIELD-2",
            params={
                "index": "evi",
                "date": "2026-04-01",
                "bbox": "44.0,15.0,44.5,15.5",
            },
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["simulated"] is False
        assert body["dataSource"] == "sentinel-hub-wms"
        assert "services.sentinel-hub.com/ogc/wms/demo-instance" in body["rasterUrl"]
        assert "LAYERS=EVI" in body["rasterUrl"]
        assert "TIME=2026-04-01" in body["rasterUrl"]
        assert body["bounds"] == [[15.0, 44.0], [15.5, 44.5]]

    @pytest.mark.parametrize("idx", ["ndvi", "evi", "savi", "ndre", "ndwi", "lai"])
    def test_supports_all_six_indices(self, client, no_sentinel_env, idx):
        r = client.get(f"/v1/index-map/F", params={"index": idx})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["indexType"] == idx
        vmin, vmax = _INDEX_VALUE_RANGES[idx]
        assert body["colorScale"]["min"] == vmin
        assert body["colorScale"]["max"] == vmax

    def test_rejects_unknown_index(self, client, no_sentinel_env):
        r = client.get("/v1/index-map/F", params={"index": "bogus"})
        assert r.status_code == 400

    def test_rejects_malformed_bbox(self, client, no_sentinel_env):
        r = client.get("/v1/index-map/F", params={"index": "ndvi", "bbox": "notabbox"})
        assert r.status_code == 400

    def test_rejects_oversize_field_id(self, client, no_sentinel_env):
        r = client.get(f"/v1/index-map/{"x" * 200}", params={"index": "ndvi"})
        assert r.status_code == 400
