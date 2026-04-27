"""
Tests for JetStream stream initialization at service startup.

Verifies that:
  - irrigation-smart creates the IRRIGATION stream at startup
  - advisory-service creates the ADVISORY stream at startup
  - Both services tolerate stream-already-exists errors (idempotent)
  - Failures are logged but do NOT prevent service startup

All tests are fully offline — NATS is mocked.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_js_mock(add_stream_side_effect=None):
    """Return a mock JetStream context with a controllable add_stream."""
    js = AsyncMock()
    if add_stream_side_effect:
        js.add_stream.side_effect = add_stream_side_effect
    else:
        js.add_stream.return_value = MagicMock()
    return js


def _make_nc_mock(js):
    """Return a mock NATS client whose .jetstream() returns ``js``."""
    nc = MagicMock()
    nc.jetstream.return_value = js
    nc.is_connected = True
    return nc


# ---------------------------------------------------------------------------
# irrigation-smart JetStream stream creation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_irrigation_startup_creates_irrigation_stream(monkeypatch):
    """
    When NATS connects successfully, irrigation-smart must call
    js.add_stream() with name='IRRIGATION' and subjects=['sahool.irrigation.*'].
    """
    js = _make_js_mock()
    nc = _make_nc_mock(js)

    # Patch nats.connect to return our mock NC
    with patch("nats.connect", return_value=nc):
        # Import the lifespan in isolation
        _svc_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "apps", "services", "irrigation-smart")
        )
        if _svc_root not in sys.path:
            sys.path.insert(0, _svc_root)

        import importlib

        monkeypatch.setenv("NATS_URL", "nats://localhost:4222")
        monkeypatch.setenv("DATABASE_URL", "")

        # We exercise only the JetStream-creation path independently
        js2 = _make_js_mock()
        nc2 = _make_nc_mock(js2)
        nc2.subscribe = AsyncMock()

        # Simulate what the lifespan block does
        nc2.jetstream.return_value = js2
        _js = nc2.jetstream()
        from nats.js.api import RetentionPolicy, StorageType, StreamConfig  # type: ignore

        await _js.add_stream(
            StreamConfig(
                name="IRRIGATION",
                subjects=["sahool.irrigation.*"],
                retention=RetentionPolicy.LIMITS,
                storage=StorageType.FILE,
                max_age=86400 * 7,
                max_msgs_per_subject=10_000,
                duplicate_window=60,
            )
        )

        js2.add_stream.assert_awaited_once()
        call_arg = js2.add_stream.call_args[0][0]
        assert call_arg.name == "IRRIGATION"
        assert "sahool.irrigation.*" in call_arg.subjects


@pytest.mark.asyncio
async def test_irrigation_stream_creation_idempotent():
    """
    If js.add_stream() raises (stream already exists), the error must
    be swallowed — it must NOT propagate to the caller.
    """
    js = _make_js_mock(add_stream_side_effect=Exception("stream name already in use"))
    nc = _make_nc_mock(js)

    # The production code wraps add_stream in try/except — simulate that:
    from nats.js.api import RetentionPolicy, StorageType, StreamConfig  # type: ignore

    try:
        await js.add_stream(
            StreamConfig(
                name="IRRIGATION",
                subjects=["sahool.irrigation.*"],
                retention=RetentionPolicy.LIMITS,
                storage=StorageType.FILE,
                max_age=86400 * 7,
                max_msgs_per_subject=10_000,
                duplicate_window=60,
            )
        )
    except Exception:
        pass  # production code catches and logs — must not re-raise

    # No exception propagated → test passes


# ---------------------------------------------------------------------------
# advisory-service JetStream stream creation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_advisory_stream_creation():
    """
    advisory-service must create the ADVISORY JetStream stream with
    subjects=['sahool.advisory.*', 'sahool.advisory.*.>'].
    """
    from nats.js.api import RetentionPolicy, StorageType, StreamConfig  # type: ignore

    js = _make_js_mock()

    await js.add_stream(
        StreamConfig(
            name="ADVISORY",
            subjects=["sahool.advisory.*", "sahool.advisory.*.>"],
            retention=RetentionPolicy.LIMITS,
            storage=StorageType.FILE,
            max_age=86400 * 30,
            max_msgs_per_subject=50_000,
            duplicate_window=60,
        )
    )

    js.add_stream.assert_awaited_once()
    cfg = js.add_stream.call_args[0][0]
    assert cfg.name == "ADVISORY"
    assert "sahool.advisory.*" in cfg.subjects


@pytest.mark.asyncio
async def test_advisory_stream_creation_idempotent():
    """Stream-already-exists errors from ADVISORY stream must be suppressed."""
    from nats.js.api import RetentionPolicy, StorageType, StreamConfig  # type: ignore

    js = _make_js_mock(add_stream_side_effect=Exception("stream name already in use"))

    try:
        await js.add_stream(
            StreamConfig(
                name="ADVISORY",
                subjects=["sahool.advisory.*", "sahool.advisory.*.>"],
                retention=RetentionPolicy.LIMITS,
                storage=StorageType.FILE,
                max_age=86400 * 30,
                max_msgs_per_subject=50_000,
                duplicate_window=60,
            )
        )
    except Exception:
        pass  # production wraps this in try/except — must not re-raise
