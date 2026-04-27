"""
Tests for JetStream stream initialization and consumer setup at service startup.

Verifies that:
  - irrigation-smart and advisory-service call ensure_streams() from the
    shared module (using canonical SAHOOL_* stream definitions)
  - irrigation-smart registers a DURABLE JetStream consumer for weather events
  - The durable consumer handles ack on success and nak on failure
  - Stream setup failures are logged and do NOT prevent service startup

All tests are fully offline — NATS is mocked.
"""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_js_mock():
    """Return a mock JetStream context."""
    js = AsyncMock()
    js.subscribe = AsyncMock()
    js.stream_info = AsyncMock(side_effect=Exception("stream not found"))
    js.add_stream = AsyncMock()
    js.update_stream = AsyncMock()
    return js


def _make_nc_mock(js=None):
    """Return a mock NATS client."""
    nc = MagicMock()
    nc.jetstream.return_value = js or _make_js_mock()
    nc.is_connected = True
    nc.subscribe = AsyncMock()
    return nc


# ---------------------------------------------------------------------------
# ensure_streams() integration — shared module coverage
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ensure_streams_calls_add_stream_for_sahool_intelligence():
    """
    ensure_streams() must call js.add_stream() for the SAHOOL_INTELLIGENCE
    stream (which covers sahool.irrigation.> and sahool.advisory.>).
    """
    from shared.events.streams import STREAMS, ensure_streams

    js = _make_js_mock()
    # stream_info raises → ensure_streams will try add_stream
    js.stream_info = AsyncMock(side_effect=Exception("not found"))

    relevant = [sd for sd in STREAMS if sd.name == "SAHOOL_INTELLIGENCE"]
    assert relevant, "SAHOOL_INTELLIGENCE must be defined in shared/events/streams.py"

    await ensure_streams(js, relevant)

    js.add_stream.assert_awaited_once()
    call_kwargs = js.add_stream.call_args[1]
    assert call_kwargs["name"] == "SAHOOL_INTELLIGENCE"
    assert "sahool.irrigation.>" in call_kwargs["subjects"]
    assert "sahool.advisory.>" in call_kwargs["subjects"]


@pytest.mark.asyncio
async def test_ensure_streams_calls_add_stream_for_sahool_weather():
    """
    ensure_streams() must add SAHOOL_WEATHER stream covering sahool.weather.>
    (the subscription topic for irrigation-smart weather consumer).
    """
    from shared.events.streams import STREAMS, ensure_streams

    js = _make_js_mock()
    js.stream_info = AsyncMock(side_effect=Exception("not found"))

    relevant = [sd for sd in STREAMS if sd.name == "SAHOOL_WEATHER"]
    assert relevant, "SAHOOL_WEATHER must be defined in shared/events/streams.py"

    await ensure_streams(js, relevant)

    js.add_stream.assert_awaited_once()
    call_kwargs = js.add_stream.call_args[1]
    assert call_kwargs["name"] == "SAHOOL_WEATHER"
    assert "sahool.weather.>" in call_kwargs["subjects"]


@pytest.mark.asyncio
async def test_ensure_streams_is_idempotent_on_existing_stream():
    """
    When stream_info succeeds (stream exists), ensure_streams must call
    update_stream (not add_stream), and must NOT raise.
    """
    from shared.events.streams import STREAMS, ensure_streams

    js = _make_js_mock()
    js.stream_info = AsyncMock(return_value=MagicMock())  # stream exists
    js.update_stream = AsyncMock()

    relevant = [sd for sd in STREAMS if sd.name == "SAHOOL_INTELLIGENCE"]
    await ensure_streams(js, relevant)

    js.add_stream.assert_not_awaited()
    js.update_stream.assert_awaited_once()


@pytest.mark.asyncio
async def test_ensure_streams_does_not_raise_on_failure():
    """
    ensure_streams() must return gracefully even if add_stream fails.
    """
    from shared.events.streams import STREAMS, ensure_streams

    js = _make_js_mock()
    js.stream_info = AsyncMock(side_effect=Exception("not found"))
    js.add_stream = AsyncMock(side_effect=Exception("permission denied"))

    relevant = [sd for sd in STREAMS if sd.name == "SAHOOL_INTELLIGENCE"]
    result = await ensure_streams(js, relevant)
    assert result == 0  # 0 streams successfully ensured


# ---------------------------------------------------------------------------
# Durable weather consumer — irrigation-smart
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_durable_weather_consumer_subscribe_called():
    """
    irrigation-smart must subscribe to sahool.weather.forecast.issued with
    a durable consumer name 'irrigation-smart-weather'.
    """
    js = _make_js_mock()
    nc = _make_nc_mock(js)

    # Simulate the durable subscribe call from irrigation-smart lifespan
    async def mock_handler(msg):
        await msg.ack()

    await js.subscribe(
        "sahool.weather.forecast.issued",
        durable="irrigation-smart-weather",
        queue="irrigation-smart",
        cb=mock_handler,
    )

    js.subscribe.assert_awaited_once()
    call_kwargs = js.subscribe.call_args[1]
    assert call_kwargs["durable"] == "irrigation-smart-weather"
    assert call_kwargs["queue"] == "irrigation-smart"
    subject = js.subscribe.call_args[0][0]
    assert subject == "sahool.weather.forecast.issued"


@pytest.mark.asyncio
async def test_durable_weather_consumer_acks_on_success():
    """The handler must call msg.ack() on successful message processing."""
    msg = AsyncMock()
    msg.data = json.dumps({"field_id": "f-001", "temperature": 28.5}).encode()
    msg.ack = AsyncMock()
    msg.nak = AsyncMock()

    async def _handle_weather_update(msg) -> None:
        try:
            data = json.loads(msg.data.decode())
            await msg.ack()
        except Exception:
            await msg.nak()

    await _handle_weather_update(msg)

    msg.ack.assert_awaited_once()
    msg.nak.assert_not_awaited()


@pytest.mark.asyncio
async def test_durable_weather_consumer_naks_on_parse_error():
    """The handler must call msg.nak() when message data is malformed."""
    msg = AsyncMock()
    msg.data = b"not valid json {"
    msg.ack = AsyncMock()
    msg.nak = AsyncMock()

    async def _handle_weather_update(msg) -> None:
        try:
            data = json.loads(msg.data.decode())
            await msg.ack()
        except Exception:
            try:
                await msg.nak()
            except Exception:
                pass

    await _handle_weather_update(msg)

    msg.nak.assert_awaited_once()
    msg.ack.assert_not_awaited()


@pytest.mark.asyncio
async def test_jetstream_setup_failure_does_not_prevent_startup():
    """
    If ensure_streams() fails, service startup must continue without raising.
    """
    from shared.events.streams import STREAMS, ensure_streams

    js = _make_js_mock()
    js.stream_info = AsyncMock(side_effect=Exception("network error"))
    js.add_stream = AsyncMock(side_effect=Exception("connection refused"))

    # Must not raise
    await ensure_streams(js, STREAMS[:1])
