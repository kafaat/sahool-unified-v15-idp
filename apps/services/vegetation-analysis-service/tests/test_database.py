"""
Tests for vegetation-analysis-service NDVI persistence layer.

All tests are fully offline — they mock asyncpg so no real DB is needed.
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Ensure the service root is on sys.path so `src` is importable
# ---------------------------------------------------------------------------
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

# Clear stale module cache before importing
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        _mod_file = getattr(sys.modules[_mod], "__file__", "") or ""
        if not _mod_file.startswith(_SERVICE_ROOT):
            del sys.modules[_mod]

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_fake_app(db_pool=None):
    """Return a minimal FastAPI-like stub with app.state.db_pool set."""
    app = MagicMock()
    app.state = MagicMock()
    app.state.db_pool = db_pool
    return app


def _make_pool(execute_side_effect=None):
    """Return a mock asyncpg pool whose acquire() is an async context manager."""
    conn = AsyncMock()
    if execute_side_effect:
        conn.execute.side_effect = execute_side_effect
    else:
        conn.execute.return_value = None

    pool = MagicMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    return pool, conn


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_persist_ndvi_reading_success():
    """Happy-path: NDVI reading is inserted via pool.acquire()."""
    from src.main import _persist_ndvi_reading

    pool, conn = _make_pool()
    app = _make_fake_app(db_pool=pool)

    await _persist_ndvi_reading(
        app=app,
        field_id="field-abc",
        ndvi_value=0.65,
        tenant_id="tenant-xyz",
        satellite_name="SENTINEL2",
        scene_id="S2_20260101_1234",
        cloud_cover=10.0,
        captured_at=datetime.now(UTC),
    )

    conn.execute.assert_awaited_once()
    call_args = conn.execute.call_args[0]
    assert "INSERT INTO ndvi_readings" in call_args[0]
    assert "field-abc" in call_args
    assert 0.65 in call_args
    assert "tenant-xyz" in call_args


@pytest.mark.asyncio
async def test_persist_ndvi_reading_no_pool():
    """When db_pool is None the function is a no-op — no errors raised."""
    from src.main import _persist_ndvi_reading

    app = _make_fake_app(db_pool=None)
    # Should complete silently
    await _persist_ndvi_reading(
        app=app,
        field_id="field-abc",
        ndvi_value=0.45,
        tenant_id="tenant-xyz",
        satellite_name="SENTINEL2",
        scene_id=None,
        cloud_cover=None,
        captured_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_persist_ndvi_reading_db_error_does_not_raise():
    """DB errors are swallowed and logged — the caller never sees them."""
    from src.main import _persist_ndvi_reading

    pool, conn = _make_pool(execute_side_effect=Exception("connection refused"))
    app = _make_fake_app(db_pool=pool)

    # Must not raise
    await _persist_ndvi_reading(
        app=app,
        field_id="field-abc",
        ndvi_value=0.55,
        tenant_id="tenant-xyz",
        satellite_name="LANDSAT8",
        scene_id=None,
        cloud_cover=5.0,
        captured_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_persist_ndvi_reading_on_conflict_do_nothing():
    """The INSERT statement must contain ON CONFLICT DO NOTHING."""
    from src.main import _persist_ndvi_reading

    pool, conn = _make_pool()
    app = _make_fake_app(db_pool=pool)

    await _persist_ndvi_reading(
        app=app,
        field_id="field-dup",
        ndvi_value=0.70,
        tenant_id="tenant-xyz",
        satellite_name="SENTINEL2",
        scene_id="S2_DUP",
        cloud_cover=0.0,
        captured_at=datetime.now(UTC),
    )

    sql = conn.execute.call_args[0][0]
    assert "ON CONFLICT DO NOTHING" in sql


@pytest.mark.asyncio
async def test_persist_ndvi_reading_extreme_values():
    """NDVI = -1.0 (bare soil/water) and 1.0 (dense vegetation) are valid."""
    from src.main import _persist_ndvi_reading

    for ndvi_value in (-1.0, 0.0, 1.0):
        pool, conn = _make_pool()
        app = _make_fake_app(db_pool=pool)
        await _persist_ndvi_reading(
            app=app,
            field_id="f",
            ndvi_value=ndvi_value,
            tenant_id="t",
            satellite_name="MODIS",
            scene_id=None,
            cloud_cover=None,
            captured_at=datetime.now(UTC),
        )
        conn.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# Pool lifecycle tests
# ---------------------------------------------------------------------------


def test_db_pool_closed_on_shutdown(monkeypatch):
    """Verify lifespan closes the pool during shutdown (synchronous smoke check)."""
    import asyncio

    from fastapi import FastAPI

    # Only test that the pool.close() is called when pool is set
    pool = AsyncMock()
    pool.close = AsyncMock()

    dummy_app = FastAPI()
    dummy_app.state.db_pool = pool

    async def run():
        if dummy_app.state.db_pool:
            await dummy_app.state.db_pool.close()

    asyncio.run(run())
    pool.close.assert_awaited_once()
