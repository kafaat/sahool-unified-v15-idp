"""
E2E Real Tests - Vegetation Analysis Service
اختبارات تكاملية حقيقية لخدمة تحليل الغطاء النباتي

These tests use the Copernicus STAC API (free, no key required) and the
service's built-in simulated provider (always available) to verify
end-to-end flows without mocking the HTTP layer.

Gating strategy:
  - VEGETATION_E2E=true  → run all tests including real Copernicus STAC calls
  - (absent / false)     → run only the simulated-provider E2E tests (always pass in CI)

Run locally with real data:
    VEGETATION_E2E=true pytest tests/test_e2e_real.py -v

Why Copernicus STAC?
  - Free public endpoint: https://catalogue.dataspace.copernicus.eu/stac
  - No API key required for scene *search* (metadata only, no imagery download)
  - Reliable for CI environments that have internet access
  - Sanaa (15.37 N, 44.21 E) is the primary SAHOOL test location (Yemen)
"""

from __future__ import annotations

import os
import sys

import pytest

# ---------------------------------------------------------------------------
# Path setup — mirrors how other vegetation service tests work
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
try:
    from unittest.mock import AsyncMock, MagicMock, patch

    from fastapi.testclient import TestClient
except ImportError as exc:
    pytest.skip(f"missing dependency: {exc}", allow_module_level=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SANAA_LAT = 15.3694
SANAA_LON = 44.1910
TENANT_ID = "00000000-0000-0000-0000-000000000002"
FIELD_ID = "field-sanaa-e2e-veg"

# Header sent with every request so TenantContextMiddleware doesn't reject it
_TENANT_HEADERS = {"X-Tenant-ID": TENANT_ID}

_REAL_E2E = os.getenv("VEGETATION_E2E", "").lower() == "true"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_fake_user(tenant_id: str = TENANT_ID):
    """Return a mock User whose tenant matches TENANT_ID."""
    from shared.auth.models import User

    u = MagicMock(spec=User)
    u.id = "e2e-user"
    u.email = "e2e@sahool.sa"
    u.roles = ["farmer"]
    u.tenant_id = tenant_id
    return u


def _make_app(tenant_id: str = TENANT_ID):
    """Return the FastAPI app with auth and field-ownership bypassed."""
    from src.main import app as veg_app

    from shared.auth.dependencies import get_current_user

    async def _fake_field_ownership(*args, **kwargs):
        return tenant_id

    veg_app.dependency_overrides[get_current_user] = lambda: _make_fake_user(tenant_id)

    # Bypass the cross-service field-ownership check (field-management-service
    # is not running in the test environment).
    with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=tenant_id)):
        yield veg_app

    veg_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Suite A — Simulated-provider E2E (always runs; no network required)
# ---------------------------------------------------------------------------


class TestSimulatedProviderE2E:
    """
    End-to-end tests that exercise the complete FastAPI → simulated-provider
    → response pipeline without any network calls.

    These tests verify:
      * The route stack is wired up and reachable
      * Request validation is enforced
      * Response shapes match the Pydantic models declared in main.py
      * The data_source / data_provider transparency fields are present
    """

    def test_healthz_returns_200_with_service_key(self):
        """GET /healthz must return 200 and identify the service."""
        with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
            from src.main import app

            app.dependency_overrides = {}
            client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
            resp = client.get("/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("service") == "vegetation-analysis-service"
        assert "version" in body
        assert "satellites" in body

    def test_readyz_returns_200_or_degraded_structure(self):
        """GET /readyz returns a JSON body with 'status' and 'checks' keys."""
        with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
            from src.main import app

            app.dependency_overrides = {}
            client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
            resp = client.get("/readyz")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "checks" in body

    def test_satellites_list_non_empty(self):
        """GET /v1/satellites lists at least 3 satellite configurations."""
        with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
            from src.main import app

            app.dependency_overrides = {}
            client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
            resp = client.get("/v1/satellites")
        assert resp.status_code == 200
        body = resp.json()
        satellites = body.get("satellites", [])
        assert len(satellites) >= 3
        for sat in satellites:
            assert "id" in sat
            assert "name" in sat

    def test_regions_list_returns_all_22_yemen_governorates(self):
        """GET /v1/regions must return all 22 Yemen governorates."""
        with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
            from src.main import app

            app.dependency_overrides = {}
            client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
            resp = client.get("/v1/regions")
        assert resp.status_code == 200
        body = resp.json()
        regions = body.get("regions", [])
        assert len(regions) == 22, f"Expected 22 Yemen governorates, got {len(regions)}"
        for r in regions:
            assert "id" in r
            assert "name_ar" in r

    def test_analyze_simulated_returns_valid_shape(self):
        """POST /v1/analyze with simulated provider returns the full FieldAnalysis shape."""
        from src.main import app
        from shared.auth.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: _make_fake_user()

        with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
            # Disable multi-provider so we hit the pure simulated path
            with patch("src.main._multi_provider", None):
                with patch("src.main.USE_MULTI_PROVIDER", False):
                    client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
                    resp = client.post(
                        "/v1/analyze",
                        json={
                            "field_id": FIELD_ID,
                            "latitude": SANAA_LAT,
                            "longitude": SANAA_LON,
                            "satellite": "sentinel-2",
                        },
                    )

        app.dependency_overrides.clear()

        assert resp.status_code == 200, resp.text
        body = resp.json()
        # Required fields from the FieldAnalysis Pydantic model
        assert "field_id" in body
        assert "indices" in body
        assert "ndvi" in body["indices"]
        assert "health_score" in body
        assert "data_source" in body
        assert body["data_source"] in ("real", "simulated")

    def test_imagery_request_simulated_returns_bands(self):
        """POST /v1/imagery/request (simulated path) returns bands list."""
        from src.main import app
        from shared.auth.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: _make_fake_user()

        with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
            with patch("src.main.EO_LEARN_AVAILABLE", False):
                client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
                resp = client.post(
                    "/v1/imagery/request",
                    json={
                        "field_id": FIELD_ID,
                        "latitude": SANAA_LAT,
                        "longitude": SANAA_LON,
                        "satellite": "sentinel-2",
                    },
                )

        app.dependency_overrides.clear()

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "imagery_id" in body
        assert isinstance(body.get("bands"), list)
        assert len(body["bands"]) > 0
        # Simulated path marks the response header and body field
        assert body.get("data_source") == "simulated"

    def test_analyze_invalid_field_id_returns_400(self):
        """POST /v1/analyze with empty field_id must return 400."""
        from src.main import app
        from shared.auth.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: _make_fake_user()

        with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
            client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
            resp = client.post(
                "/v1/analyze",
                json={
                    "field_id": "",  # empty → invalid
                    "latitude": SANAA_LAT,
                    "longitude": SANAA_LON,
                },
            )

        app.dependency_overrides.clear()
        # _validate_field_id raises 400 for empty field_id
        assert resp.status_code == 400

    def test_tenant_mismatch_returns_403(self):
        """Requesting imagery for a tenant that doesn't match the JWT returns 403."""
        from src.main import app
        from shared.auth.dependencies import get_current_user

        # Caller has tenant A, but field-management-service would report tenant B
        app.dependency_overrides[get_current_user] = lambda: _make_fake_user(tenant_id=TENANT_ID)

        # Simulate the cross-service check failing with a mismatch
        from fastapi import HTTPException

        async def _mismatch(*a, **kw):
            raise HTTPException(
                status_code=403,
                detail={"error": "tenant_mismatch"},
            )

        with patch("src.main._verify_field_owned_by_tenant", new=_mismatch):
            client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
            resp = client.post(
                "/v1/analyze",
                json={
                    "field_id": FIELD_ID,
                    "latitude": SANAA_LAT,
                    "longitude": SANAA_LON,
                },
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 403

    def test_providers_endpoint_returns_provider_list(self):
        """GET /v1/providers returns a dictionary with a 'providers' key."""
        from src.main import app

        app.dependency_overrides = {}
        client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
        resp = client.get("/v1/providers")
        assert resp.status_code == 200
        body = resp.json()
        assert "providers" in body
        assert isinstance(body["providers"], list)

    def test_eo_status_endpoint_returns_status_key(self):
        """GET /v1/eo-status returns a dict with 'status' key."""
        from src.main import app

        app.dependency_overrides = {}
        client = TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)
        resp = client.get("/v1/eo-status")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body


# ---------------------------------------------------------------------------
# Suite B — Real Copernicus STAC Scene Search (gated)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _REAL_E2E, reason="VEGETATION_E2E=true required for real API calls")
class TestCopernicusSTACRealE2E:
    """
    Tests that hit the real Copernicus Data Space STAC endpoint
    (https://catalogue.dataspace.copernicus.eu/stac) for scene search.

    No credentials needed — the Copernicus STAC catalogue search is
    publicly accessible. Only scene *metadata* is fetched; no imagery
    download occurs (which would require authentication).

    These tests verify that MultiSatelliteService → CopernicusSTACProvider
    can locate recent Sentinel-2 scenes over Yemen.
    """

    def test_copernicus_stac_scene_search_sanaa(self):
        """MultiSatelliteService can find Sentinel-2 scenes over Sanaa via STAC."""
        import asyncio
        from datetime import date, timedelta

        from src.multi_provider import MultiSatelliteService, SatelliteType

        service = MultiSatelliteService()
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        scenes = asyncio.run(
            service.search_scenes(
                lat=SANAA_LAT,
                lon=SANAA_LON,
                start_date=start_date,
                end_date=end_date,
                satellite=SatelliteType.SENTINEL2,
                max_cloud_cover=80.0,
            )
        )

        # The Copernicus catalogue has global coverage; at least one scene
        # should be available for Yemen in any 30-day window.
        assert isinstance(scenes, list), "search_scenes must return a list"
        assert len(scenes) > 0, "Expected at least 1 Sentinel-2 scene over Sanaa"
        scene = scenes[0]
        assert hasattr(scene, "scene_id")
        assert hasattr(scene, "acquisition_date")
        assert hasattr(scene, "cloud_cover_pct")

    def test_multi_provider_analyze_field_sanaa(self):
        """Full analyze_field call over Sanaa using the real provider cascade."""
        import asyncio
        from datetime import date, timedelta

        from src.multi_provider import MultiSatelliteService, SatelliteType

        service = MultiSatelliteService()
        result = asyncio.run(
            service.analyze_field(
                field_id=FIELD_ID,
                lat=SANAA_LAT,
                lon=SANAA_LON,
                acquisition_date=date.today() - timedelta(days=7),
                satellite=SatelliteType.SENTINEL2,
            )
        )

        # Result is a SatelliteResult wrapper — it may be simulated when no
        # credentials are set, but it must not be None and must carry indices.
        assert result is not None
        assert result.data is not None
        analysis = result.data
        assert hasattr(analysis, "indices")
        indices = analysis.indices
        # NDVI must be a valid float in the physical range [-1, 1]
        assert -1.0 <= indices.ndvi <= 1.0, f"NDVI out of range: {indices.ndvi}"
        # The data_source transparency field must be set
        assert analysis.is_simulated in (True, False)
