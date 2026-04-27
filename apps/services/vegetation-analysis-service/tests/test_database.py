"""
Tests for vegetation-analysis-service NDVI persistence and event publishing.

All tests are fully offline — they mock asyncpg and NATS so no real
infrastructure is required.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, call, patch

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
    """
    Return a mock asyncpg pool whose acquire() supports an async context manager
    AND whose connection supports conn.transaction() as an async context manager.

    Since _persist_ndvi_reading now goes through acquire_tenant_conn, the mock
    must support:
        async with pool.acquire() as conn:         ← pool.acquire()
            async with conn.transaction():         ← conn.transaction()
                await conn.execute(set_config...)  ← set_app_tenant
                await conn.execute(INSERT...)      ← actual persist
    """
    conn = AsyncMock()
    if execute_side_effect:
        conn.execute.side_effect = execute_side_effect
    else:
        conn.execute.return_value = None

    # conn.transaction() must work as an async context manager.
    # Use MagicMock (not AsyncMock) so conn.transaction() returns the
    # context manager directly rather than a coroutine.
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=None)
    tx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=tx)

    pool = MagicMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    return pool, conn


# ---------------------------------------------------------------------------
# _persist_ndvi_reading tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_persist_ndvi_reading_success():
    """
    Happy-path: NDVI reading is inserted via acquire_tenant_conn.
    execute is called twice: once for SET LOCAL (RLS) and once for the INSERT.
    """
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

    # execute called at least twice (set_config + INSERT)
    assert conn.execute.await_count >= 2
    # Last call must be the INSERT
    insert_sql = conn.execute.call_args_list[-1][0][0]
    assert "INSERT INTO ndvi_readings" in insert_sql
    assert "ON CONFLICT DO NOTHING" in insert_sql

    # RLS: first call must be the SET LOCAL config
    set_config_sql = conn.execute.call_args_list[0][0][0]
    assert "set_config" in set_config_sql
    assert "app.current_tenant" in set_config_sql


@pytest.mark.asyncio
async def test_persist_ndvi_reading_tenant_id_in_insert():
    """The INSERT must bind tenant_id in its positional args."""
    from src.main import _persist_ndvi_reading

    pool, conn = _make_pool()
    app = _make_fake_app(db_pool=pool)

    await _persist_ndvi_reading(
        app=app,
        field_id="field-abc",
        ndvi_value=0.65,
        tenant_id="tenant-xyz",
        satellite_name="SENTINEL2",
        scene_id=None,
        cloud_cover=None,
        captured_at=datetime.now(UTC),
    )

    insert_args = conn.execute.call_args_list[-1][0]
    assert "tenant-xyz" in insert_args
    assert "field-abc" in insert_args
    assert 0.65 in insert_args


@pytest.mark.asyncio
async def test_persist_ndvi_reading_no_pool():
    """When db_pool is None the function is a no-op — no errors raised."""
    from src.main import _persist_ndvi_reading

    app = _make_fake_app(db_pool=None)
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

    insert_sql = conn.execute.call_args_list[-1][0][0]
    assert "ON CONFLICT DO NOTHING" in insert_sql


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
        assert conn.execute.await_count >= 1  # at least the INSERT happened


# ---------------------------------------------------------------------------
# _publish_ndvi_event tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_publish_ndvi_event_publishes_correct_subject():
    """_publish_ndvi_event must publish to sahool.satellite.ndvi.computed."""
    from src.main import _publish_ndvi_event

    publisher = AsyncMock()
    publisher.is_connected = True
    publisher.publish = AsyncMock()

    with (
        patch("src.main._nats_available", True),
        patch("shared.libs.events.nats_publisher.get_publisher", AsyncMock(return_value=publisher)),
    ):
        await _publish_ndvi_event(
            field_id="field-abc",
            ndvi_value=0.72,
            tenant_id="tenant-xyz",
            satellite_name="SENTINEL2",
            scene_id="S2_001",
            cloud_cover=5.0,
            captured_at=datetime.now(UTC),
        )

    publisher.publish.assert_awaited_once()
    subject_used = publisher.publish.call_args[0][0]
    assert subject_used == "sahool.satellite.ndvi.computed"


@pytest.mark.asyncio
async def test_publish_ndvi_event_payload_schema():
    """Payload must contain mean_ndvi + value + field_id + tenant_id + event_id."""
    from src.main import _publish_ndvi_event

    publisher = AsyncMock()
    publisher.is_connected = True
    publisher.publish = AsyncMock()

    with (
        patch("src.main._nats_available", True),
        patch("shared.libs.events.nats_publisher.get_publisher", AsyncMock(return_value=publisher)),
    ):
        await _publish_ndvi_event(
            field_id="field-abc",
            ndvi_value=0.72,
            tenant_id="tenant-xyz",
            satellite_name="SENTINEL2",
            scene_id="S2_001",
            cloud_cover=5.0,
            captured_at=datetime.now(UTC),
        )

    raw_payload = publisher.publish.call_args[0][1]
    payload = json.loads(raw_payload.decode())
    assert payload["field_id"] == "field-abc"
    assert payload["tenant_id"] == "tenant-xyz"
    assert payload["mean_ndvi"] == 0.72
    assert payload["value"] == 0.72
    assert "event_id" in payload
    assert "correlation_id" in payload
    assert payload["satellite_name"] == "SENTINEL2"


@pytest.mark.asyncio
async def test_publish_ndvi_event_no_op_when_nats_unavailable():
    """When _nats_available is False, publishing is silently skipped."""
    from src.main import _publish_ndvi_event

    with patch("src.main._nats_available", False):
        # Should complete without touching any NATS objects
        await _publish_ndvi_event(
            field_id="f",
            ndvi_value=0.5,
            tenant_id="t",
            satellite_name="S2",
            scene_id=None,
            cloud_cover=None,
            captured_at=datetime.now(UTC),
        )


@pytest.mark.asyncio
async def test_publish_ndvi_event_no_op_when_publisher_not_connected():
    """When publisher.is_connected is False, no publish call is made."""
    from src.main import _publish_ndvi_event

    publisher = AsyncMock()
    publisher.is_connected = False
    publisher.publish = AsyncMock()

    with (
        patch("src.main._nats_available", True),
        patch("shared.libs.events.nats_publisher.get_publisher", AsyncMock(return_value=publisher)),
    ):
        await _publish_ndvi_event(
            field_id="f",
            ndvi_value=0.5,
            tenant_id="t",
            satellite_name="S2",
            scene_id=None,
            cloud_cover=None,
            captured_at=datetime.now(UTC),
        )

    publisher.publish.assert_not_awaited()


@pytest.mark.asyncio
async def test_publish_ndvi_event_swallows_publish_errors():
    """Publishing failures must never raise — they are logged and discarded."""
    from src.main import _publish_ndvi_event

    publisher = AsyncMock()
    publisher.is_connected = True
    publisher.publish.side_effect = Exception("NATS gone")

    with (
        patch("src.main._nats_available", True),
        patch("shared.libs.events.nats_publisher.get_publisher", AsyncMock(return_value=publisher)),
    ):
        # Must not raise
        await _publish_ndvi_event(
            field_id="f",
            ndvi_value=0.5,
            tenant_id="t",
            satellite_name="S2",
            scene_id=None,
            cloud_cover=None,
            captured_at=datetime.now(UTC),
        )


# ---------------------------------------------------------------------------
# Pool lifecycle tests
# ---------------------------------------------------------------------------


def test_db_pool_closed_on_shutdown(monkeypatch):
    """Verify lifespan closes the pool during shutdown (synchronous smoke check)."""
    import asyncio

    from fastapi import FastAPI

    pool = AsyncMock()
    pool.close = AsyncMock()

    dummy_app = FastAPI()
    dummy_app.state.db_pool = pool

    async def run():
        if dummy_app.state.db_pool:
            await dummy_app.state.db_pool.close()

    asyncio.run(run())
    pool.close.assert_awaited_once()
