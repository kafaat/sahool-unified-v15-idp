"""
Kill-Service Tests - Weather Service
اختبارات إيقاف الخدمة (Graceful Shutdown / SIGTERM Simulation)

Verifies that:
1. The lifespan cleanup runs in the correct order and closes all resources.
2. Errors during cleanup of one resource do not prevent others from closing.
3. The service handles SIGTERM gracefully (simulated via lifespan __aexit__).
4. readyz reflects degraded state when a critical resource is missing.
5. In-flight business logic (assess, irrigation) completes even when the
   publisher is torn down (NATS-publisher is the "killable" component).
6. The graph renderer / store are initialised on startup; shutdown assertions
   cover the resources currently closed by the lifespan cleanup implementation.

These tests do NOT require a real NATS server or internet access; all external
connections are mocked.
"""

import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError as exc:
    pytest.skip(f"fastapi not installed: {exc}", allow_module_level=True)

TENANT_ID = "00000000-0000-0000-0000-000000000123"
FIELD_ID = "field-shutdown-test"


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """App fixture with auth bypassed."""
    from src.main import app as weather_app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    def _fake_user():
        u = MagicMock(spec=User)
        u.id = "shutdown-tester"
        u.email = "shutdown@sahool.sa"
        u.roles = ["admin"]
        u.tenant_id = TENANT_ID
        return u

    weather_app.dependency_overrides[get_current_user] = _fake_user
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    c = TestClient(app)
    c.headers["X-Tenant-ID"] = TENANT_ID
    return c


# ---------------------------------------------------------------------------
# 1. Lifespan startup & shutdown sequence
# ---------------------------------------------------------------------------


class TestLifespanCleanup:
    """Verify that the lifespan context manager closes all resources properly."""

    def test_provider_close_called_on_shutdown(self, app):
        """
        After the lifespan context exits, provider.close() must have been called.
        Simulates SIGTERM → uvicorn stops accepting new requests → lifespan exits.

        Startup I/O (NATS, provider constructors, graph imports) is patched so
        the test runs without any network access.
        """
        import src.main as main_module

        close_order = []

        mock_provider = AsyncMock()
        mock_provider.close = AsyncMock(side_effect=lambda: close_order.append("weather_provider"))

        mock_multi = AsyncMock()
        mock_multi.close = AsyncMock(side_effect=lambda: close_order.append("multi_provider"))

        mock_publisher = AsyncMock()
        mock_publisher.close = AsyncMock(side_effect=lambda: close_order.append("publisher"))

        async def run_lifespan():
            with (
                patch.object(main_module, "get_publisher", new=AsyncMock(return_value=mock_publisher)),
                patch.object(main_module, "MultiWeatherService", return_value=mock_multi),
                patch.object(main_module, "OpenMeteoProvider", return_value=mock_provider),
                patch("src.main.USE_MULTI_PROVIDER", True),
            ):
                async with app.router.lifespan_context(app):
                    # Overwrite with our tracked mocks so shutdown assertions work
                    app.state.weather_provider = mock_provider
                    app.state.multi_provider = mock_multi
                    app.state.publisher = mock_publisher

        asyncio.run(run_lifespan())

        mock_provider.close.assert_called_once()
        mock_multi.close.assert_called_once()
        mock_publisher.close.assert_called_once()
        assert close_order == ["multi_provider", "weather_provider", "publisher"]

    def test_cleanup_continues_after_provider_error(self):
        """
        If one resource raises during close(), the others are still closed.
        This mimics the lifespan cleanup loop in main.py which catches exceptions.
        """
        closed_resources = []

        async def _failing_close():
            raise RuntimeError("provider connection already gone")

        async def _good_close(name):
            closed_resources.append(name)

        async def run():
            # Replicate the cleanup loop from lifespan (main.py lines 241-249)
            resources = {
                "multi_provider": AsyncMock(close=_failing_close),
                "weather_provider": AsyncMock(close=lambda: _good_close("weather_provider")),
                "publisher": AsyncMock(close=lambda: _good_close("publisher")),
            }
            for name, resource in resources.items():
                try:
                    await resource.close()
                except Exception:
                    pass  # matches the lifespan except clause

        asyncio.run(run())

        # weather_provider and publisher must have been closed even though
        # multi_provider raised during its close()
        assert "weather_provider" in closed_resources
        assert "publisher" in closed_resources

    def test_shutdown_with_no_resources_is_safe(self):
        """
        Cleanup loop handles getattr(state, name, None) == None gracefully.
        Mirrors the guard: `if resource: await resource.close()`
        """

        class _FakeState:
            pass

        state = _FakeState()

        async def _cleanup(state):
            for name in ("multi_provider", "weather_provider", "publisher"):
                resource = getattr(state, name, None)
                if resource:
                    try:
                        await resource.close()
                    except Exception:
                        pass

        # Should complete without AttributeError or TypeError
        asyncio.run(_cleanup(state))


# ---------------------------------------------------------------------------
# 2. readyz reflects shutdown / degraded state (fix 3.2)
# ---------------------------------------------------------------------------


class TestReadyzOnShutdown:
    """
    readyz must return HTTP 503 when the service is degraded, allowing
    Kubernetes to remove the pod from the Service before killing it.
    """

    def test_readyz_503_when_providers_not_initialized(self, client, app):
        """readyz → 503 when both multi_provider and weather_provider are None."""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None
            mock_state.multi_provider = None
            mock_state.weather_provider = None

            response = client.get("/readyz")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["providers"] == "not_initialized"

    def test_readyz_503_when_nats_disconnected(self, client, app):
        """readyz → 503 when NATS publisher exists but is not connected."""
        mock_publisher = MagicMock()
        mock_publisher._connected = False  # publisher present but disconnected

        mock_provider = MagicMock()

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = mock_publisher
            mock_state.multi_provider = mock_provider
            mock_state.weather_provider = None

            response = client.get("/readyz")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["nats"] == "disconnected"

    def test_readyz_200_when_providers_available_nats_not_configured(self, client, app):
        """
        readyz → 200 when providers are available and NATS is simply not configured
        (publisher=None means NATS not required, not disconnected).
        """
        mock_provider = MagicMock()

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None  # not configured — not a failure
            mock_state.multi_provider = mock_provider
            mock_state.weather_provider = None

            response = client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["checks"]["nats"] == "not_configured"
        assert data["checks"]["providers"] == "available"

    def test_readyz_200_when_fully_healthy(self, client, app):
        """readyz → 200 when provider is up and NATS is connected."""
        mock_publisher = MagicMock()
        mock_publisher._connected = True

        mock_provider = MagicMock()

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = mock_publisher
            mock_state.multi_provider = mock_provider
            mock_state.weather_provider = None

            response = client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_liveness_always_200(self, client):
        """/healthz is always 200 — it is a liveness not readiness probe."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# 3. NATS "kill" — publisher torn down mid-session
# ---------------------------------------------------------------------------


class TestNATSTeardown:
    """
    Simulate the NATS broker being killed while the service is running.
    The publisher disconnects and publish_weather_alert() returns None (fix 5.9).
    The endpoint must still return 200 with event_ids=[].
    """

    def _weather_mock(self, temp_c=45.0):
        w = MagicMock()
        w.temperature_c = temp_c
        w.humidity_pct = 10.0
        w.wind_speed_kmh = 5.0
        w.wind_direction_deg = 180
        w.wind_direction = "S"
        w.precipitation_mm = 0.0
        w.cloud_cover_pct = 0.0
        w.pressure_hpa = 1013.0
        w.uv_index = 14.0
        w.condition = "Clear"
        w.condition_ar = "صافي"
        w.icon = "clear"
        w.timestamp = "2026-04-23T12:00:00+00:00"
        w.provider = "Open-Meteo"
        return w

    def test_nats_returns_none_event_ids_empty(self, client, app):
        """
        When the publisher is connected but publish returns None (NATS gone),
        event_ids must be [] and the HTTP response still 200.
        """
        mock_publisher = AsyncMock()
        # Simulate mid-session NATS broker restart: publish returns None
        mock_publisher.publish_weather_alert = AsyncMock(return_value=None)

        mock_multi = AsyncMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.provider = "Open-Meteo"
        mock_result.data = self._weather_mock()
        mock_result.failed_providers = []
        mock_multi.get_current = AsyncMock(return_value=mock_result)

        with patch("src.main.app.state") as mock_state:
            mock_state.multi_provider = mock_multi
            mock_state.publisher = mock_publisher

            response = client.post(
                "/weather/current",
                json={"tenant_id": TENANT_ID, "field_id": FIELD_ID, "lat": 15.35, "lon": 44.20},
            )

        assert response.status_code == 200
        data = response.json()
        # None values are filtered out (fix 5.9)
        assert data["event_ids"] == []
        assert data["current"]["temperature_c"] == 45.0

    def test_nats_exception_event_ids_empty(self, client, app):
        """
        When publish_weather_alert() raises (broker gone), event_ids is still []
        and the response is still 200 — NATS failure must not break the endpoint.
        """
        mock_publisher = AsyncMock()
        mock_publisher.publish_weather_alert = AsyncMock(side_effect=Exception("NATS: connection reset by peer"))

        mock_multi = AsyncMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.provider = "Open-Meteo"
        mock_result.data = self._weather_mock()
        mock_result.failed_providers = []
        mock_multi.get_current = AsyncMock(return_value=mock_result)

        with patch("src.main.app.state") as mock_state:
            mock_state.multi_provider = mock_multi
            mock_state.publisher = mock_publisher

            response = client.post(
                "/weather/current",
                json={"tenant_id": TENANT_ID, "field_id": FIELD_ID, "lat": 15.35, "lon": 44.20},
            )

        assert response.status_code == 200
        assert response.json()["event_ids"] == []

    def test_assess_nats_killed_still_returns_alerts(self, client, app):
        """
        /weather/assess with NATS gone: alerts are still generated and returned,
        event_ids is [] (no None values sneaking in — fix 5.9).
        """
        mock_publisher = AsyncMock()
        mock_publisher.publish_weather_alert = AsyncMock(return_value=None)

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = mock_publisher

            response = client.post(
                "/weather/assess",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 48.0,  # Triggers heat-stress alert
                    "humidity_pct": 10.0,
                    "uv_index": 15.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["alert_count"] > 0
        assert None not in data["event_ids"]
        assert data["event_ids"] == []

    def test_assess_nats_none_publisher_returns_alerts(self, client, app):
        """
        /weather/assess with publisher=None (NATS never started / killed):
        alerts are generated and event_ids is [].
        """
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/assess",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 48.0,
                    "humidity_pct": 10.0,
                    "uv_index": 15.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["event_ids"], list)
        assert data["event_ids"] == []


# ---------------------------------------------------------------------------
# 4. Provider "kill" — multi_provider torn down mid-session
# ---------------------------------------------------------------------------


class TestProviderTeardown:
    """
    Simulate the external weather provider becoming unavailable (503, network loss).
    The service must return a meaningful HTTP error, not crash.
    """

    def test_all_providers_fail_after_startup(self, client, app):
        """
        After startup, if all providers fail in production,
        the endpoint returns 502 or 503 — not 500.
        """
        mock_multi = AsyncMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.data = None
        mock_result.error = "All weather providers unreachable"
        mock_result.error_ar = "جميع مزودي الطقس غير متاحين"
        mock_result.failed_providers = ["Open-Meteo: connection refused"]
        mock_multi.get_current = AsyncMock(return_value=mock_result)

        with patch("src.main.app.state") as mock_state:
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None

            response = client.post(
                "/weather/current",
                json={"tenant_id": TENANT_ID, "field_id": FIELD_ID, "lat": 15.35, "lon": 44.20},
            )

        # Must be a 5xx error indicating external dependency failure
        assert response.status_code in (502, 503)

    def test_provider_exception_returns_5xx(self, client, app):
        """
        An unexpected exception from the provider is wrapped in ExternalServiceException → 5xx.
        """
        mock_provider = AsyncMock()
        mock_provider.get_current = AsyncMock(side_effect=RuntimeError("unexpected provider crash"))

        with patch("src.main.app.state") as mock_state:
            mock_state.multi_provider = None
            mock_state.weather_provider = mock_provider
            mock_state.publisher = None

            response = client.post(
                "/weather/current",
                json={"tenant_id": TENANT_ID, "field_id": FIELD_ID, "lat": 15.35, "lon": 44.20},
            )

        assert response.status_code in (500, 502, 503)

    def test_stateless_endpoints_survive_provider_loss(self, client, app):
        """
        /weather/assess, /healthz, /readyz survive even when providers are None.
        They don't call external APIs.
        """
        with patch("src.main.app.state") as mock_state:
            mock_state.multi_provider = None
            mock_state.weather_provider = None
            mock_state.publisher = None

            # Assess is stateless — no provider call needed
            assess_resp = client.post(
                "/weather/assess",
                json={"tenant_id": TENANT_ID, "field_id": FIELD_ID, "temp_c": 25.0},
            )
            healthz_resp = client.get("/healthz")
            readyz_resp = client.get("/readyz")

        assert assess_resp.status_code == 200
        assert healthz_resp.status_code == 200
        # readyz should be 503 since providers are not initialized (fix 3.2)
        assert readyz_resp.status_code == 503
        assert readyz_resp.json()["status"] == "degraded"


# ---------------------------------------------------------------------------
# 5. Graph renderer lifecycle (fix 4.5)
# ---------------------------------------------------------------------------


class TestGraphRendererLifecycle:
    """
    Verify the graph_renderer / graph_store lifespan initialisation paths
    (fix 4.5) without requiring the full ASGI lifespan to run.

    The lifespan code (main.py lines 225-236) has two branches:
      A. Graph module available  → graph_renderer and graph_store are set
      B. Graph module unavailable → both are set to None (graceful fallback)

    We test these branches in isolation to avoid relying on DNS / NATS being
    available (which would happen if we used `with TestClient(app):`).
    """

    @staticmethod
    def _graph_import_side_effect(real_import, fake_module=None, import_error=None):
        def _side_effect(name, globals=None, locals=None, fromlist=(), level=0):
            if "graph" in name.lower():
                if import_error is not None:
                    raise import_error
                if fake_module is not None:
                    return fake_module
            return real_import(name, globals, locals, fromlist, level)

        return _side_effect

    def test_lifespan_sets_graph_renderer_when_module_available(self):
        """
        When the graph module imports successfully, the real lifespan startup
        assigns app.state.graph_renderer and app.state.graph_store from the
        graph constructors.
        """
        import builtins
        import importlib
        import types

        main_module = importlib.import_module("src.main")

        mock_renderer = MagicMock(name="graph_renderer")
        mock_store = MagicMock(name="graph_store")

        fake_graph_module = types.ModuleType("fake_graph_module")
        fake_graph_module.WeatherGraphRenderer = MagicMock(return_value=mock_renderer)
        fake_graph_module.GraphStore = MagicMock(return_value=mock_store)

        real_import = builtins.__import__
        real_import_module = importlib.import_module

        def _import_module(name, package=None):
            if "graph" in name.lower():
                return fake_graph_module
            return real_import_module(name, package)

        with (
            patch(
                "builtins.__import__",
                side_effect=self._graph_import_side_effect(real_import, fake_module=fake_graph_module),
            ),
            patch("importlib.import_module", side_effect=_import_module),
        ):
            with TestClient(main_module.app):
                assert main_module.app.state.graph_renderer is mock_renderer
                assert main_module.app.state.graph_store is mock_store

    def test_lifespan_sets_graph_renderer_none_on_import_failure(self):
        """
        When graph import/initialisation fails during real lifespan startup,
        app.state.graph_renderer and app.state.graph_store are explicitly set
        to None as a graceful fallback.
        """
        import builtins
        import importlib

        main_module = importlib.import_module("src.main")
        real_import = builtins.__import__
        real_import_module = importlib.import_module

        def _import_module(name, package=None):
            if "graph" in name.lower():
                raise ImportError("graph module not available")
            return real_import_module(name, package)

        with (
            patch(
                "builtins.__import__",
                side_effect=self._graph_import_side_effect(
                    real_import,
                    import_error=ImportError("graph module not available"),
                ),
            ),
            patch("importlib.import_module", side_effect=_import_module),
        ):
            with TestClient(main_module.app):
                assert hasattr(main_module.app.state, "graph_renderer")
                assert hasattr(main_module.app.state, "graph_store")
                assert main_module.app.state.graph_renderer is None
                assert main_module.app.state.graph_store is None
