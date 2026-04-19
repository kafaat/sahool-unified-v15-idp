# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Tests for LLM Orchestrator Service lifespan behavior.

Verifies the fix for the startup-hang bug where heavy integration
initialization (AraBERT / Sentinel / AgML / CrewAI) blocked the container
healthcheck and caused docker-compose to mark the service as unhealthy.

اختبارات سلوك دورة حياة الخدمة للتحقق من إصلاح الخلل الذي كان يحجب
نقطة فحص الصحة بسبب تهيئة التكاملات الثقيلة.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

try:
    from src import main as main_module
    from src.main import _initialize_integrations_background, app
except ImportError:
    pytest.skip("llm-orchestrator-service dependencies not installed", allow_module_level=True)


@pytest.fixture
def stub_integrations(monkeypatch):
    """
    Patch the four integration service classes so TestClient(app)-based tests
    are deterministic and don't trigger real model downloads / HTTP calls.

    Each stub's initialize() is a no-op coroutine returning True. Tests that
    want to observe the pre-initialized state should still use this fixture —
    the background task completes near-instantly so /readyz will report
    integrations_ready=True very quickly.
    """

    class _StubService:
        def __init__(self):
            self._initialized = False

        async def initialize(self):
            self._initialized = True
            return True

    for attr in ("NLPService", "SatelliteService", "MLService", "CrewService"):
        monkeypatch.setattr(main_module, attr, _StubService)
    return _StubService


class TestHealthzResponsiveness:
    """Health probe must respond immediately regardless of integration state."""

    def test_healthz_responds_during_background_init(self, stub_integrations):
        """
        /healthz must return 200 without waiting for integrations.
        Regression test: previous implementation blocked lifespan on model loads
        and caused the container to be marked unhealthy after start_period.
        """
        with TestClient(app) as c:
            response = c.get("/healthz")
            assert response.status_code == 200
            body = response.json()
            assert body["status"] == "ok"
            assert body["service"] == "llm-orchestrator-service"

    def test_readyz_exposes_integration_status(self, stub_integrations):
        """
        /readyz must include per-integration status so operators can tell
        whether NLP / satellite / ML / crew are warming up or ready.
        """
        with TestClient(app) as c:
            response = c.get("/readyz")
            assert response.status_code == 200
            body = response.json()
            assert body["status"] == "ready"
            checks = body["checks"]
            assert "integrations_initialized" in checks
            assert "integrations_ready" in checks
            assert "integrations" in checks
            # Each integration must have a status string
            for name in ("nlp", "satellite", "ml", "crew"):
                assert name in checks["integrations"]
                assert isinstance(checks["integrations"][name], str)


class TestLifespanState:
    """Verify lifespan populates all expected state slots."""

    def test_app_state_initialized(self, stub_integrations):
        """Service instances and state flags must exist after lifespan start."""
        with TestClient(app) as c:
            # Touching the client drives the lifespan startup
            c.get("/healthz")
            assert hasattr(app.state, "executor")
            assert hasattr(app.state, "nlp_service")
            assert hasattr(app.state, "satellite_service")
            assert hasattr(app.state, "ml_service")
            assert hasattr(app.state, "crew_service")
            assert hasattr(app.state, "integrations_initialized")
            assert hasattr(app.state, "integrations_ready")
            assert hasattr(app.state, "integration_status")
            # integration_status is a dict keyed by integration name
            assert isinstance(app.state.integration_status, dict)
            assert set(app.state.integration_status.keys()) == {"nlp", "satellite", "ml", "crew"}


class TestBackgroundInitResilience:
    """The background initializer must tolerate integration failures."""

    @pytest.mark.asyncio
    async def test_failed_integration_does_not_raise(self):
        """
        If an integration's initialize() raises, the background task must record
        the failure in integration_status and continue with other integrations —
        not propagate the exception up to uvicorn.
        """
        from fastapi import FastAPI

        fake = FastAPI()
        fake.state.nlp_service = AsyncMock()
        fake.state.nlp_service.initialize = AsyncMock(side_effect=RuntimeError("boom"))
        fake.state.satellite_service = AsyncMock()
        fake.state.satellite_service.initialize = AsyncMock(return_value=True)
        fake.state.ml_service = AsyncMock()
        fake.state.ml_service.initialize = AsyncMock(return_value=False)
        fake.state.crew_service = AsyncMock()
        fake.state.crew_service.initialize = AsyncMock(return_value=True)
        fake.state.integrations_initialized = False
        fake.state.integrations_ready = False
        fake.state.integration_status = {
            "nlp": "pending",
            "satellite": "pending",
            "ml": "pending",
            "crew": "pending",
        }

        await _initialize_integrations_background(fake)

        # Warmup completed, but one integration outright failed → not fully ready.
        assert fake.state.integrations_initialized is True
        assert fake.state.integrations_ready is False
        assert fake.state.integration_status["nlp"] == "failed"
        assert fake.state.integration_status["satellite"] == "ready"
        assert fake.state.integration_status["ml"] == "fallback"
        assert fake.state.integration_status["crew"] == "ready"

    @pytest.mark.asyncio
    async def test_cancellation_propagates(self):
        """
        asyncio.CancelledError must propagate so that shutdown can cleanly
        cancel the task without it being swallowed as a generic failure.
        """
        from fastapi import FastAPI

        started = asyncio.Event()
        release = asyncio.Event()

        async def slow_init():
            started.set()
            await release.wait()
            return True

        fake = FastAPI()
        fake.state.nlp_service = AsyncMock()
        fake.state.nlp_service.initialize = slow_init
        fake.state.satellite_service = AsyncMock()
        fake.state.satellite_service.initialize = AsyncMock(return_value=True)
        fake.state.ml_service = AsyncMock()
        fake.state.ml_service.initialize = AsyncMock(return_value=True)
        fake.state.crew_service = AsyncMock()
        fake.state.crew_service.initialize = AsyncMock(return_value=True)
        fake.state.integrations_initialized = False
        fake.state.integrations_ready = False
        fake.state.integration_status = {
            "nlp": "pending",
            "satellite": "pending",
            "ml": "pending",
            "crew": "pending",
        }

        task = asyncio.create_task(_initialize_integrations_background(fake))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert fake.state.integration_status["nlp"] == "cancelled"


class TestEagerInitEscapeHatch:
    """ORCHESTRATOR_EAGER_INIT=true runs integrations inline (tests / CI)."""

    @pytest.mark.asyncio
    async def test_eager_flag_awaits_integrations_inline(self, monkeypatch):
        """
        With ORCHESTRATOR_EAGER_INIT=true the lifespan must complete integration
        init before yielding so deterministic tests can assert the final state.
        """
        monkeypatch.setenv("ORCHESTRATOR_EAGER_INIT", "true")

        from src.main import lifespan

        # Patch out network-heavy pieces so only our integration init runs
        with patch("src.main.REDIS_AVAILABLE", False), patch("src.main.NATS_AVAILABLE", False), patch(
            "src.main.ASYNCPG_AVAILABLE", False
        ), patch("src.main.NLPService") as MockNLP, patch("src.main.SatelliteService") as MockSat, patch(
            "src.main.MLService"
        ) as MockML, patch(
            "src.main.CrewService"
        ) as MockCrew:
            for mock_cls in (MockNLP, MockSat, MockML, MockCrew):
                instance = mock_cls.return_value
                instance.initialize = AsyncMock(return_value=True)

            from fastapi import FastAPI

            fake = FastAPI()
            async with lifespan(fake):
                # In eager mode integrations must already be reported ready
                assert fake.state.integrations_initialized is True
                assert fake.state.integrations_ready is True
                assert fake.state.integrations_task is None
                assert all(s == "ready" for s in fake.state.integration_status.values())
