"""
Tests for Hydrology Service main module - lifecycle, events, and database helpers.
اختبارات الوحدة الرئيسية لخدمة الهيدرولوجيا
"""

import json
import os
import sys
import types
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_shared_modules(monkeypatch):
    """Mock shared modules."""
    shared = types.ModuleType("shared")
    errors_py = types.ModuleType("shared.errors_py")
    errors_py.add_request_id_middleware = lambda app: None
    errors_py.setup_exception_handlers = lambda app: None
    shared.errors_py = errors_py

    middleware = types.ModuleType("shared.middleware")
    tenant_ctx = types.ModuleType("shared.middleware.tenant_context")

    class FakeTenantMiddleware:
        def __init__(self, app, **kwargs):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    tenant_ctx.TenantContextMiddleware = FakeTenantMiddleware
    shared.middleware = middleware
    shared.middleware.tenant_context = tenant_ctx

    monkeypatch.setitem(sys.modules, "shared", shared)
    monkeypatch.setitem(sys.modules, "shared.errors_py", errors_py)
    monkeypatch.setitem(sys.modules, "shared.middleware", middleware)
    monkeypatch.setitem(sys.modules, "shared.middleware.tenant_context", tenant_ctx)


class _AsyncCtxMgr:
    """Helper async context manager for mocking pool.acquire()."""

    def __init__(self, return_value):
        self._return_value = return_value

    async def __aenter__(self):
        return self._return_value

    async def __aexit__(self, *args):
        return False


@pytest.fixture
def app_instance(mock_shared_modules):
    """Get the FastAPI app instance."""
    with patch.dict(os.environ, {"DATABASE_URL": "", "NATS_URL": "", "ENVIRONMENT": "test"}):
        from src.core.config import get_settings

        get_settings.cache_clear()
        from src.main import app

        app.state.db_pool = None
        app.state.nc = None
        yield app
        get_settings.cache_clear()


# ==============================================================================
# publish_event tests
# ==============================================================================
class TestPublishEvent:
    """Tests for the publish_event helper."""

    @pytest.mark.asyncio
    async def test_publish_event_with_nats(self, app_instance):
        """Test event publishing when NATS is connected."""
        from src.main import publish_event

        mock_nc = AsyncMock()
        app_instance.state.nc = mock_nc

        await publish_event("sahool.hydrology.test", {"field_id": "F1"})

        mock_nc.publish.assert_called_once()
        call_args = mock_nc.publish.call_args
        assert call_args[0][0] == "sahool.hydrology.test"
        payload = json.loads(call_args[0][1].decode())
        assert payload["field_id"] == "F1"

    @pytest.mark.asyncio
    async def test_publish_event_no_nats(self, app_instance):
        """Test event publishing when NATS is not connected."""
        from src.main import publish_event

        app_instance.state.nc = None
        # Should not raise
        await publish_event("sahool.hydrology.test", {"field_id": "F1"})

    @pytest.mark.asyncio
    async def test_publish_event_nats_error(self, app_instance):
        """Test event publishing handles NATS errors gracefully."""
        from src.main import publish_event

        mock_nc = AsyncMock()
        mock_nc.publish.side_effect = Exception("NATS connection lost")
        app_instance.state.nc = mock_nc

        # Should not raise
        await publish_event("sahool.hydrology.test", {"field_id": "F1"})


# ==============================================================================
# save_analysis tests
# ==============================================================================
class TestSaveAnalysis:
    """Tests for the save_analysis database helper."""

    @pytest.mark.asyncio
    async def test_save_analysis_success(self, app_instance):
        """Test saving analysis to database successfully."""
        from src.main import save_analysis

        mock_conn = AsyncMock()
        mock_pool = MagicMock()
        mock_pool.acquire.return_value = _AsyncCtxMgr(mock_conn)
        app_instance.state.db_pool = mock_pool

        result = await save_analysis(
            field_id="FIELD-001",
            analysis_type="drainage",
            result={"drainage_density": 50.0},
            tenant_id="TENANT-001",
            dem_source="srtm",
            resolution_m=30.0,
        )

        assert result is True
        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_analysis_no_db(self, app_instance):
        """Test save_analysis returns False when no DB pool."""
        from src.main import save_analysis

        app_instance.state.db_pool = None
        result = await save_analysis("F1", "drainage", {"test": True})
        assert result is False

    @pytest.mark.asyncio
    async def test_save_analysis_db_error(self, app_instance):
        """Test save_analysis handles DB errors."""
        from src.main import save_analysis

        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = Exception("DB write error")
        mock_pool = MagicMock()
        mock_pool.acquire.return_value = _AsyncCtxMgr(mock_conn)
        app_instance.state.db_pool = mock_pool

        result = await save_analysis("F1", "drainage", {"test": True})
        assert result is False


# ==============================================================================
# get_analysis tests
# ==============================================================================
class TestGetAnalysis:
    """Tests for the get_analysis database helper."""

    @pytest.mark.asyncio
    async def test_get_analysis_with_tenant(self, app_instance):
        """Test getting analysis with tenant_id."""
        from src.main import get_analysis

        mock_row = {
            "result": json.dumps({"drainage_density": 50.0}),
            "analyzed_at": datetime(2025, 1, 1, tzinfo=UTC),
            "dem_source": "srtm",
            "resolution_m": 30.0,
        }
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = mock_row
        mock_pool = MagicMock()
        mock_pool.acquire.return_value = _AsyncCtxMgr(mock_conn)
        app_instance.state.db_pool = mock_pool

        result = await get_analysis("FIELD-001", "drainage", tenant_id="TENANT-001")

        assert result is not None
        assert result["drainage_density"] == 50.0
        assert "_metadata" in result
        assert result["_metadata"]["dem_source"] == "srtm"

    @pytest.mark.asyncio
    async def test_get_analysis_without_tenant(self, app_instance):
        """Test getting analysis without tenant_id."""
        from src.main import get_analysis

        mock_row = {
            "result": json.dumps({"twi_mean": 8.5}),
            "analyzed_at": datetime(2025, 1, 1, tzinfo=UTC),
            "dem_source": None,
            "resolution_m": 30.0,
        }
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = mock_row
        mock_pool = MagicMock()
        mock_pool.acquire.return_value = _AsyncCtxMgr(mock_conn)
        app_instance.state.db_pool = mock_pool

        result = await get_analysis("FIELD-001", "wetness")
        assert result is not None
        assert result["twi_mean"] == 8.5

    @pytest.mark.asyncio
    async def test_get_analysis_not_found(self, app_instance):
        """Test getting analysis when no record exists."""
        from src.main import get_analysis

        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = None
        mock_pool = MagicMock()
        mock_pool.acquire.return_value = _AsyncCtxMgr(mock_conn)
        app_instance.state.db_pool = mock_pool

        result = await get_analysis("NONEXISTENT", "drainage")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_analysis_no_db(self, app_instance):
        """Test get_analysis returns None when no DB pool."""
        from src.main import get_analysis

        app_instance.state.db_pool = None
        result = await get_analysis("F1", "drainage")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_analysis_db_error(self, app_instance):
        """Test get_analysis handles DB errors."""
        from src.main import get_analysis

        mock_conn = AsyncMock()
        mock_conn.fetchrow.side_effect = Exception("DB read error")
        mock_pool = MagicMock()
        mock_pool.acquire.return_value = _AsyncCtxMgr(mock_conn)
        app_instance.state.db_pool = mock_pool

        result = await get_analysis("F1", "drainage")
        assert result is None
