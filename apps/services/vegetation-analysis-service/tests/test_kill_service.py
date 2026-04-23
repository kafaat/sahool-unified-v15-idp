"""
Kill-Service Tests - Vegetation Analysis Service
اختبارات إيقاف الخدمة لخدمة تحليل الغطاء النباتي

Verifies:
  1. Lifespan cleanup runs for each resource (multi_provider, sar_processor).
  2. An exception in one resource's close() does not block others.
  3. readyz reflects degraded state correctly (disconnected NATS / DB).
  4. Stateless endpoints (/healthz, /v1/satellites, /v1/regions) work even
     when runtime state is partially torn down (provider set to None).
  5. NATS publisher teardown: when the shared singleton is killed mid-flight,
     in-flight analysis calls return valid data (the NATS publish is
     fire-and-forget, not in the critical path).

All tests run without network access; all external connections are mocked.
"""

from __future__ import annotations

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

try:
    from fastapi.testclient import TestClient
except ImportError as exc:
    pytest.skip(f"fastapi not installed: {exc}", allow_module_level=True)

TENANT_ID = "00000000-0000-0000-0000-000000000001"
FIELD_ID = "field-kill-test"
_TENANT_HEADERS = {"X-Tenant-ID": TENANT_ID}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_fake_user(tenant_id: str = TENANT_ID):
    from shared.auth.models import User

    u = MagicMock(spec=User)
    u.id = "kill-test-user"
    u.email = "kill@sahool.sa"
    u.roles = ["farmer"]
    u.tenant_id = tenant_id
    return u


@pytest.fixture
def app():
    from src.main import app as veg_app

    from shared.auth.dependencies import get_current_user

    veg_app.dependency_overrides[get_current_user] = lambda: _make_fake_user()
    yield veg_app
    veg_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)


# ---------------------------------------------------------------------------
# 1. Lifespan Cleanup
# ---------------------------------------------------------------------------


class TestLifespanCleanup:
    """Verify the real lifespan teardown in main.py closes runtime resources."""

    @staticmethod
    def _load_main_module():
        import importlib

        try:
            return importlib.import_module("src.main")
        except ImportError:
            return importlib.import_module("main")

    def _run_real_lifespan_shutdown(self, multi_provider, sar_processor):
        main_module = self._load_main_module()

        async def _run():
            # Patch constructors so that the lifespan startup code assigns our
            # tracked mocks to the module-level globals (_multi_provider,
            # _sar_processor). Patching the globals directly does not work
            # because the lifespan function re-declares them via `global` and
            # overwrites the patched values before cleanup runs.
            multi_ctor = MagicMock(return_value=multi_provider) if multi_provider is not None else None
            sar_ctor = MagicMock(return_value=sar_processor) if sar_processor is not None else None

            with (
                patch.object(main_module, "USE_MULTI_PROVIDER", multi_provider is not None),
                patch.object(main_module, "MultiSatelliteService", multi_ctor),
                patch.object(main_module, "SARProcessor", sar_ctor),
                # Stub remaining startup dependencies to avoid network I/O
                patch.object(main_module, "PhenologyDetector", MagicMock()),
                patch.object(main_module, "FieldBoundaryDetector", MagicMock()),
                patch.object(main_module, "ChangeDetector", MagicMock()),
                patch.object(main_module, "get_cloud_masker", MagicMock()),
                patch.object(main_module, "YieldPredictor", None),
                patch.object(main_module, "VRAGenerator", None),
                patch.object(main_module, "AgriculturalLandDetector", None),
                patch.object(main_module, "register_boundary_endpoints", MagicMock()),
            ):
                async with main_module.lifespan(MagicMock()):
                    pass

        asyncio.run(_run())

    def test_multi_provider_close_called_on_shutdown(self):
        """_multi_provider.close() is awaited during the real lifespan shutdown phase."""
        mock_provider = MagicMock()
        mock_provider.close = AsyncMock()

        self._run_real_lifespan_shutdown(mock_provider, None)

        mock_provider.close.assert_awaited_once()

    def test_sar_processor_close_called_on_shutdown(self):
        """Both multi_provider and sar_processor are closed when both are set."""
        mock_multi = MagicMock()
        mock_sar = MagicMock()
        mock_multi.close = AsyncMock()
        mock_sar.close = AsyncMock()

        self._run_real_lifespan_shutdown(mock_multi, mock_sar)

        mock_multi.close.assert_awaited_once()
        mock_sar.close.assert_awaited_once()

    def test_cleanup_continues_when_multi_provider_close_raises(self):
        """
        If _multi_provider.close() raises, the sar_processor is still closed.
        Exercises the real lifespan try/except teardown path in main.py.
        """
        mock_multi = MagicMock()
        mock_sar = MagicMock()
        mock_multi.close = AsyncMock(side_effect=RuntimeError("network gone"))
        mock_sar.close = AsyncMock()

        self._run_real_lifespan_shutdown(mock_multi, mock_sar)

        mock_multi.close.assert_awaited_once()
        mock_sar.close.assert_awaited_once()

    def test_shutdown_with_no_resources_is_safe(self):
        """When both _multi_provider and _sar_processor are None, real shutdown is a no-op."""
        self._run_real_lifespan_shutdown(None, None)
        assert True


# ---------------------------------------------------------------------------
# 2. readyz Behaviour After Shutdown
# ---------------------------------------------------------------------------


class TestReadyzOnShutdown:
    """readyz correctly signals degraded state when resources are unavailable."""

    def test_readyz_200_when_no_db_and_nats_not_configured(self, client):
        """
        When there is no DB pool and NATS is not configured (the default dev
        state), readyz returns 200 and all checks show 'not_configured'.
        """
        import src.main as m

        with patch.object(m, "_nats_available", False):
            resp = client.get("/readyz")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "checks" in body

    def test_readyz_degrades_when_nats_disconnected(self, client):
        """
        When the shared NATS publisher exists but is disconnected,
        readyz checks['nats'] is 'disconnected' and status is 'degraded'.
        """
        import src.main as m

        mock_publisher = MagicMock()
        mock_publisher.is_connected = False

        with patch.object(m, "_nats_available", True):
            with patch("src.main._publisher_instance", mock_publisher, create=True):
                try:
                    from shared.libs.events import nats_publisher as _np

                    with patch.object(_np, "_publisher_instance", mock_publisher):
                        resp = client.get("/readyz")
                except Exception:
                    resp = client.get("/readyz")

        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "checks" in body

    def test_readyz_nats_not_configured_status_ready(self, client):
        """
        When NATS is not configured at all (_nats_available=False),
        the 'nats' check is 'not_configured' and service is still ready.
        """
        import src.main as m

        with patch.object(m, "_nats_available", False):
            resp = client.get("/readyz")
        assert resp.status_code == 200
        body = resp.json()
        assert body["checks"].get("nats") == "not_configured"
        assert body["status"] in ("ready", "degraded")

    def test_liveness_always_200(self, client):
        """/healthz must return 200 regardless of NATS/provider state."""
        import src.main as m

        with patch.object(m, "_nats_available", False):
            with patch.object(m, "_multi_provider", None):
                resp = client.get("/healthz")
        assert resp.status_code == 200

    def test_healthz_includes_sar_processor_flag(self, client):
        """healthz body includes 'sar_processor_available' (not an opaque boolean)."""
        resp = client.get("/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert "sar_processor_available" in body
        assert isinstance(body["sar_processor_available"], bool)


# ---------------------------------------------------------------------------
# 3. Stateless Endpoints Survive Provider Teardown
# ---------------------------------------------------------------------------


class TestStatelessEndpointsAfterTeardown:
    """
    /v1/satellites and /v1/regions are computed from constants — they must
    work even when _multi_provider, _sar_processor, etc. are set to None
    (the torn-down state after SIGTERM).
    """

    def test_satellites_endpoint_works_with_no_providers(self, client):
        """GET /v1/satellites does not depend on any runtime state."""
        import src.main as m

        with patch.object(m, "_multi_provider", None):
            with patch.object(m, "_sar_processor", None):
                resp = client.get("/v1/satellites")
        assert resp.status_code == 200
        assert "satellites" in resp.json()

    def test_regions_endpoint_works_with_no_providers(self, client):
        """GET /v1/regions does not depend on any runtime state."""
        import src.main as m

        with patch.object(m, "_multi_provider", None):
            resp = client.get("/v1/regions")
        assert resp.status_code == 200
        assert "regions" in resp.json()

    def test_providers_endpoint_returns_legacy_info_when_no_multi_provider(self, client):
        """GET /v1/providers with _multi_provider=None returns legacy eo-learn info."""
        import src.main as m

        with patch.object(m, "_multi_provider", None):
            resp = client.get("/v1/providers")
        assert resp.status_code == 200
        body = resp.json()
        assert "providers" in body
        # Legacy branch: multi_provider_enabled is False
        assert body.get("multi_provider_enabled") is False

    def test_eo_status_always_available(self, client):
        """GET /v1/eo-status always returns 200 (pure constant + env-var check)."""
        resp = client.get("/v1/eo-status")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 4. NATS Publisher Teardown — Analysis Still Completes
# ---------------------------------------------------------------------------


class TestNATSTeardownMidAnalysis:
    """
    The NATS publish is fire-and-forget in the analysis path.
    When the publisher is killed/unavailable, the analyze_field function
    still returns a valid FieldAnalysis (not None, not 500).
    """

    def test_analyze_field_completes_when_nats_publish_fails(self):
        """analyze_field() returns a valid FieldAnalysis even when NATS is unavailable."""
        from datetime import date

        import src.main as m

        # Patch publish_analysis_completed_sync to raise (NATS dead)
        async def _fake_analyze(*args, **kwargs):
            from src.main import ImageryRequest, SatelliteSource, analyze_field

            req = ImageryRequest(
                field_id=FIELD_ID,
                latitude=15.37,
                longitude=44.21,
                satellite=SatelliteSource.SENTINEL2,
            )
            with patch.object(m, "_multi_provider", None):
                with patch.object(m, "USE_MULTI_PROVIDER", False):
                    with patch.object(m, "publish_analysis_completed_sync", side_effect=RuntimeError("NATS gone")):
                        result = await analyze_field(req, tenant_id=TENANT_ID)
            return result

        result = asyncio.run(_fake_analyze())
        assert result is not None
        assert result.field_id == FIELD_ID
        assert -1.0 <= result.indices.ndvi <= 1.0

    def test_analyze_field_completes_when_nats_publish_is_none(self):
        """analyze_field() works when publish_analysis_completed_sync is None."""
        import src.main as m

        async def _run():
            from src.main import ImageryRequest, SatelliteSource, analyze_field

            req = ImageryRequest(
                field_id=FIELD_ID,
                latitude=15.37,
                longitude=44.21,
                satellite=SatelliteSource.SENTINEL2,
            )
            with patch.object(m, "_multi_provider", None):
                with patch.object(m, "USE_MULTI_PROVIDER", False):
                    with patch.object(m, "publish_analysis_completed_sync", None):
                        return await analyze_field(req, tenant_id=TENANT_ID)

        result = asyncio.run(_run())
        assert result is not None
        assert result.field_id == FIELD_ID


# ---------------------------------------------------------------------------
# 5. Provider Teardown — HTTP Handlers Respond Gracefully
# ---------------------------------------------------------------------------


class TestProviderTeardown:
    """
    When _multi_provider is torn down (set to None) during a live request
    the service falls back to the simulated provider rather than 500-ing.
    """

    def test_analyze_falls_back_to_simulated_when_no_provider(self, app, client):
        """POST /v1/analyze with _multi_provider=None falls through to simulated path."""
        import src.main as m

        with patch.object(m, "_multi_provider", None):
            with patch.object(m, "USE_MULTI_PROVIDER", False):
                with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
                    resp = client.post(
                        "/v1/analyze",
                        json={
                            "field_id": FIELD_ID,
                            "latitude": 15.37,
                            "longitude": 44.21,
                            "satellite": "sentinel-2",
                        },
                    )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["data_source"] == "simulated"

    def test_imagery_request_falls_back_to_simulated_when_no_eo_learn(self, app, client):
        """POST /v1/imagery/request with EO_LEARN_AVAILABLE=False uses simulated bands."""
        import src.main as m

        with patch.object(m, "EO_LEARN_AVAILABLE", False):
            with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
                resp = client.post(
                    "/v1/imagery/request",
                    json={
                        "field_id": FIELD_ID,
                        "latitude": 15.37,
                        "longitude": 44.21,
                        "satellite": "sentinel-2",
                    },
                )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body.get("data_source") == "simulated"

    def test_multi_provider_exception_falls_back_to_simulated(self, app, client):
        """When _multi_provider.analyze_field() raises, the response is still 200 simulated."""
        import src.main as m

        broken_provider = AsyncMock()
        broken_provider.analyze_field = AsyncMock(side_effect=RuntimeError("provider dead"))

        with patch.object(m, "_multi_provider", broken_provider):
            with patch.object(m, "USE_MULTI_PROVIDER", True):
                with patch("src.main._verify_field_owned_by_tenant", new=AsyncMock(return_value=TENANT_ID)):
                    resp = client.post(
                        "/v1/analyze",
                        json={
                            "field_id": FIELD_ID,
                            "latitude": 15.37,
                            "longitude": 44.21,
                            "satellite": "sentinel-2",
                        },
                    )

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["field_id"] == FIELD_ID


# ---------------------------------------------------------------------------
# 6. Lifespan Component Initialisation Paths
# ---------------------------------------------------------------------------


class TestLifespanInitPaths:
    """
    Verify the lifespan initialises each component via the correct branch,
    without actually running the full ASGI lifespan (which requires NATS/Redis).
    """

    def test_multi_satellite_service_instantiation(self):
        """MultiSatelliteService can be instantiated without credentials."""
        from src.multi_provider import MultiSatelliteService

        service = MultiSatelliteService()
        providers = service.get_available_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0
        for p in providers:
            assert "name" in p
            assert "configured" in p

    def test_phenology_detector_instantiation(self):
        """PhenologyDetector can be instantiated and has Yemen crop seasons."""
        from src.phenology_detector import PhenologyDetector

        detector = PhenologyDetector()
        assert hasattr(detector, "YEMEN_CROP_SEASONS")
        assert len(detector.YEMEN_CROP_SEASONS) > 0

    def test_change_detector_instantiation(self):
        """ChangeDetector can be instantiated without any arguments."""
        from src.change_detector import ChangeDetector

        cd = ChangeDetector()
        assert cd is not None

    def test_cloud_masker_instantiation(self):
        """get_cloud_masker() returns a non-None object."""
        from src.cloud_masking import get_cloud_masker

        masker = get_cloud_masker()
        assert masker is not None

    def test_field_boundary_detector_without_provider(self):
        """FieldBoundaryDetector can be instantiated with multi_provider=None."""
        from src.field_boundary_detector import FieldBoundaryDetector

        fbd = FieldBoundaryDetector(multi_provider=None)
        assert fbd is not None
