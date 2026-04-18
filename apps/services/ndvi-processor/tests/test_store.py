"""
Unit Tests for NDVI Processor – store.py
اختبارات وحدة مخزن معالج NDVI

Covers: configure(), save_result(), save_composite(), ensure_tables(),
in-memory stores, DB persistence, and NATS event publishing.
"""

import json
import os
import sys

import pytest

# Ensure the project root and service root are on sys.path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _service_root not in sys.path:
    sys.path.insert(0, _service_root)

try:
    from unittest.mock import AsyncMock, MagicMock, patch

    from src.store import (
        _cfg,
        _composites,
        _jobs,
        _results,
        _StoreConfig,
        configure,
        ensure_tables,
        save_composite,
        save_result,
    )
except ImportError:
    pytest.skip("ndvi-processor dependencies not installed", allow_module_level=True)


def _clear_stores():
    """Reset in-memory stores and config between tests."""
    _jobs.clear()
    _results.clear()
    _composites.clear()
    _cfg.db_pool = None
    _cfg.nats_client = None


# ---------------------------------------------------------------------------
# configure()
# ---------------------------------------------------------------------------


class TestConfigure:
    """Tests for the configure() function."""

    def setup_method(self):
        _clear_stores()

    def test_configure_no_args(self):
        """configure() with no args keeps in-memory fallback."""
        configure()
        assert _cfg.db_pool is None
        assert _cfg.nats_client is None

    def test_configure_with_db_pool(self):
        """configure() stores the DB pool reference."""
        mock_pool = MagicMock()
        configure(db_pool=mock_pool)
        assert _cfg.db_pool is mock_pool

    def test_configure_with_nats_client(self):
        """configure() stores the NATS client reference."""
        mock_nc = MagicMock()
        configure(nats_client=mock_nc)
        assert _cfg.nats_client is mock_nc

    def test_configure_with_both(self):
        """configure() stores both DB pool and NATS client."""
        mock_pool = MagicMock()
        mock_nc = MagicMock()
        configure(db_pool=mock_pool, nats_client=mock_nc)
        assert _cfg.db_pool is mock_pool
        assert _cfg.nats_client is mock_nc

    def test_configure_replaces_previous(self):
        """configure() replaces previous configuration."""
        configure(db_pool=MagicMock())
        new_pool = MagicMock()
        configure(db_pool=new_pool)
        assert _cfg.db_pool is new_pool


# ---------------------------------------------------------------------------
# save_result() – in-memory only
# ---------------------------------------------------------------------------


class TestSaveResultInMemory:
    """Tests for save_result() with no DB/NATS configured."""

    def setup_method(self):
        _clear_stores()

    @pytest.mark.asyncio
    async def test_save_result_creates_field_entry(self):
        """save_result() creates a new field entry in _results."""
        result_dict = _make_result_dict("r1", "field-1", "2025-06-01")
        await save_result("field-1", "tenant-1", result_dict)

        assert "field-1" in _results
        assert len(_results["field-1"]) == 1
        assert _results["field-1"][0]["id"] == "r1"

    @pytest.mark.asyncio
    async def test_save_result_appends_to_existing(self):
        """save_result() appends to an existing field entry."""
        r1 = _make_result_dict("r1", "field-1", "2025-06-01")
        r2 = _make_result_dict("r2", "field-1", "2025-06-15")
        await save_result("field-1", "tenant-1", r1)
        await save_result("field-1", "tenant-1", r2)

        assert len(_results["field-1"]) == 2

    @pytest.mark.asyncio
    async def test_save_result_different_fields(self):
        """save_result() keeps results separate per field_id."""
        r1 = _make_result_dict("r1", "field-1", "2025-06-01")
        r2 = _make_result_dict("r2", "field-2", "2025-06-01")
        await save_result("field-1", "tenant-1", r1)
        await save_result("field-2", "tenant-1", r2)

        assert len(_results["field-1"]) == 1
        assert len(_results["field-2"]) == 1


# ---------------------------------------------------------------------------
# save_result() – with DB pool
# ---------------------------------------------------------------------------


class TestSaveResultWithDB:
    """Tests for save_result() when a DB pool is configured."""

    def setup_method(self):
        _clear_stores()

    @pytest.mark.asyncio
    async def test_save_result_calls_db_execute(self):
        """save_result() calls db_pool.execute when pool is set."""
        mock_pool = AsyncMock()
        configure(db_pool=mock_pool)

        result_dict = _make_result_dict("r1", "field-1", "2025-06-01")
        await save_result("field-1", "tenant-1", result_dict)

        mock_pool.execute.assert_awaited_once()
        call_args = mock_pool.execute.call_args
        sql = call_args[0][0]
        assert "INSERT INTO ndvi_result" in sql

    @pytest.mark.asyncio
    async def test_save_result_db_error_does_not_raise(self):
        """save_result() logs and continues if DB write fails."""
        mock_pool = AsyncMock()
        mock_pool.execute.side_effect = Exception("DB connection lost")
        configure(db_pool=mock_pool)

        result_dict = _make_result_dict("r1", "field-1", "2025-06-01")
        # Should not raise
        await save_result("field-1", "tenant-1", result_dict)

        # In-memory store should still work
        assert "field-1" in _results

    @pytest.mark.asyncio
    async def test_save_result_passes_correct_params(self):
        """save_result() passes correct params to DB execute."""
        mock_pool = AsyncMock()
        configure(db_pool=mock_pool)

        result_dict = _make_result_dict("r1", "field-1", "2025-06-01")
        await save_result("field-1", "tenant-1", result_dict)

        call_args = mock_pool.execute.call_args[0]
        # Verify positional args after SQL: id, tenant_id, field_id, date, ...
        assert call_args[1] == "r1"  # id
        assert call_args[2] == "tenant-1"  # tenant_id
        assert call_args[3] == "field-1"  # field_id
        assert call_args[4] == "2025-06-01"  # acquisition_date


# ---------------------------------------------------------------------------
# save_result() – with NATS client
# ---------------------------------------------------------------------------


class TestSaveResultWithNATS:
    """Tests for save_result() NATS event publishing."""

    def setup_method(self):
        _clear_stores()

    # UUID-shaped tenant_id so the new tenant-scoped subject helper accepts it.
    # `get_tenant_subject` validates tenant_id against a UUID regex.
    _TENANT = "a1b2c3d4-e5f6-4789-abcd-0123456789ab"

    @pytest.mark.asyncio
    async def test_save_result_publishes_ndvi_computed_event(self):
        """save_result() publishes the tenant-scoped ndvi.computed event."""
        mock_nc = AsyncMock()
        configure(nats_client=mock_nc)

        result_dict = _make_result_dict("r1", "field-1", "2025-06-01")
        await save_result("field-1", self._TENANT, result_dict)

        # Should have published two events
        assert mock_nc.publish.await_count == 2
        first_call = mock_nc.publish.call_args_list[0]
        assert first_call[0][0] == f"sahool.tenant.{self._TENANT}.satellite.ndvi.computed"

        payload = json.loads(first_call[0][1].decode())
        assert payload["event_type"] == "ndvi.computed"
        assert payload["field_id"] == "field-1"
        assert payload["tenant_id"] == self._TENANT

    @pytest.mark.asyncio
    async def test_save_result_publishes_observation_event(self):
        """save_result() publishes the tenant-scoped field.observation.ingested.v1 event."""
        mock_nc = AsyncMock()
        configure(nats_client=mock_nc)

        result_dict = _make_result_dict("r1", "field-1", "2025-06-01")
        await save_result("field-1", self._TENANT, result_dict)

        second_call = mock_nc.publish.call_args_list[1]
        assert second_call[0][0] == f"sahool.tenant.{self._TENANT}.field.observation.ingested.v1"

        payload = json.loads(second_call[0][1].decode())
        assert payload["event_type"] == "field.observation.ingested"
        assert payload["obs_type"] == "ndvi"
        assert payload["field_id"] == "field-1"

    @pytest.mark.asyncio
    async def test_save_result_nats_error_does_not_raise(self):
        """save_result() continues if NATS publish fails."""
        mock_nc = AsyncMock()
        mock_nc.publish.side_effect = Exception("NATS timeout")
        configure(nats_client=mock_nc)

        result_dict = _make_result_dict("r1", "field-1", "2025-06-01")
        # Should not raise
        await save_result("field-1", "tenant-1", result_dict)

        # In-memory should still have the result
        assert "field-1" in _results


# ---------------------------------------------------------------------------
# save_composite()
# ---------------------------------------------------------------------------


class TestSaveComposite:
    """Tests for save_composite()."""

    def setup_method(self):
        _clear_stores()

    @pytest.mark.asyncio
    async def test_save_composite_in_memory(self):
        """save_composite() stores composite in _composites dict."""
        composite = _make_composite_dict("c1", "field-1", 2025, 6)
        await save_composite("c1", "tenant-1", composite)

        assert "c1" in _composites
        assert _composites["c1"]["field_id"] == "field-1"

    @pytest.mark.asyncio
    async def test_save_composite_with_db(self):
        """save_composite() calls DB execute when pool is set."""
        mock_pool = AsyncMock()
        configure(db_pool=mock_pool)

        composite = _make_composite_dict("c1", "field-1", 2025, 6)
        await save_composite("c1", "tenant-1", composite)

        mock_pool.execute.assert_awaited_once()
        sql = mock_pool.execute.call_args[0][0]
        assert "INSERT INTO ndvi_composite" in sql

    @pytest.mark.asyncio
    async def test_save_composite_db_error_does_not_raise(self):
        """save_composite() logs and continues on DB error."""
        mock_pool = AsyncMock()
        mock_pool.execute.side_effect = Exception("DB write failed")
        configure(db_pool=mock_pool)

        composite = _make_composite_dict("c1", "field-1", 2025, 6)
        await save_composite("c1", "tenant-1", composite)

        # In-memory still saved
        assert "c1" in _composites

    @pytest.mark.asyncio
    async def test_save_composite_overwrites_same_id(self):
        """save_composite() overwrites a composite with the same id."""
        c1 = _make_composite_dict("c1", "field-1", 2025, 6)
        c1_updated = _make_composite_dict("c1", "field-1", 2025, 6)
        c1_updated["images_used"] = 99

        await save_composite("c1", "tenant-1", c1)
        await save_composite("c1", "tenant-1", c1_updated)

        assert _composites["c1"]["images_used"] == 99


# ---------------------------------------------------------------------------
# ensure_tables()
# ---------------------------------------------------------------------------


class TestEnsureTables:
    """Tests for ensure_tables()."""

    @pytest.mark.asyncio
    async def test_ensure_tables_calls_execute(self):
        """ensure_tables() calls db_pool.execute with CREATE TABLE SQL."""
        mock_pool = AsyncMock()
        await ensure_tables(mock_pool)

        mock_pool.execute.assert_awaited_once()
        sql = mock_pool.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS ndvi_result" in sql
        assert "CREATE TABLE IF NOT EXISTS ndvi_composite" in sql

    @pytest.mark.asyncio
    async def test_ensure_tables_error_does_not_raise(self):
        """ensure_tables() does not raise on error."""
        mock_pool = AsyncMock()
        mock_pool.execute.side_effect = Exception("permission denied")

        # Should not raise
        await ensure_tables(mock_pool)


# ---------------------------------------------------------------------------
# _StoreConfig
# ---------------------------------------------------------------------------


class TestStoreConfig:
    """Tests for _StoreConfig dataclass."""

    def test_default_values(self):
        """_StoreConfig defaults to None for both fields."""
        cfg = _StoreConfig()
        assert cfg.db_pool is None
        assert cfg.nats_client is None

    def test_set_values(self):
        """_StoreConfig stores arbitrary objects."""
        pool = object()
        nc = object()
        cfg = _StoreConfig(db_pool=pool, nats_client=nc)
        assert cfg.db_pool is pool
        assert cfg.nats_client is nc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result_dict(result_id: str, field_id: str, date: str) -> dict:
    """Create a minimal NDVI result dict for testing."""
    return {
        "id": result_id,
        "field_id": field_id,
        "date": date,
        "statistics": {
            "mean": 0.65,
            "min": 0.4,
            "max": 0.85,
            "std": 0.08,
        },
        "quality": {
            "cloud_cover_percent": 5.0,
            "valid_pixels_percent": 95.0,
        },
        "source": {
            "satellite": "sentinel-2",
            "scene_id": "S2_20250601_field1",
            "resolution_meters": 10,
        },
        "processing": {
            "processed_at": "2025-06-01T12:00:00Z",
        },
        "files": {
            "geotiff": "s3://bucket/field-1/2025-06-01.tif",
            "png": "s3://bucket/field-1/2025-06-01.png",
            "thumbnail": "s3://bucket/field-1/2025-06-01_thumb.png",
        },
    }


def _make_composite_dict(composite_id: str, field_id: str, year: int, month: int) -> dict:
    """Create a minimal composite dict for testing."""
    return {
        "composite_id": composite_id,
        "field_id": field_id,
        "year": year,
        "month": month,
        "method": "max_ndvi",
        "source": "sentinel-2",
        "statistics": {
            "mean": 0.6,
            "min": 0.35,
            "max": 0.8,
            "std": 0.05,
        },
        "images_used": 6,
        "files": {
            "geotiff": f"s3://bucket/composites/{field_id}/{year}-{month:02d}_max_ndvi.tif",
            "png": None,
            "thumbnail": None,
        },
        "created_at": "2025-06-15T10:00:00Z",
    }
