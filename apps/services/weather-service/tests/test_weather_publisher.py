"""
Tests for WeatherPublisher NATS reconnection behavior.
Verifies connect() uses reconnection parameters and callbacks update state.
"""

import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def publisher():
    """Import WeatherPublisher with mocked dependencies and NATS class."""
    # Stub the relative-import dependency (src.events.types) so publish.py loads
    types_stub = ModuleType("src.events.types")
    types_stub.IRRIGATION_ADJUSTMENT = "irrigation_adjustment"
    types_stub.WEATHER_ALERT = "weather_alert"
    types_stub.WEATHER_FORECAST_ISSUED = "weather_forecast_issued"
    types_stub.get_subject = lambda *a, **kw: "test.subject"
    types_stub.get_version = lambda *a, **kw: 1

    # Stub nats.aio.client so publish.py import gets our mock
    mock_nc = AsyncMock()
    mock_cls = MagicMock(return_value=mock_nc)

    nats_stub = ModuleType("nats")
    nats_aio = ModuleType("nats.aio")
    nats_client = ModuleType("nats.aio.client")
    nats_client.Client = mock_cls
    nats_stub.aio = nats_aio

    saved = {}
    for name, mod in [
        ("src", ModuleType("src")),
        ("src.events", ModuleType("src.events")),
        ("src.events.types", types_stub),
        ("nats", nats_stub),
        ("nats.aio", nats_aio),
        ("nats.aio.client", nats_client),
    ]:
        saved[name] = sys.modules.get(name)
        sys.modules[name] = mod

    # Force re-import so publish.py picks up the stubs
    sys.modules.pop("src.events.publish", None)
    import src.events.publish as pub_mod

    yield pub_mod.WeatherPublisher(nats_url="nats://test:4222"), mock_nc

    # Restore sys.modules
    for name, original in saved.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original
    sys.modules.pop("src.events.publish", None)


@pytest.mark.asyncio
async def test_connect_passes_reconnection_params(publisher):
    """connect() must pass reconnect_time_wait, max_reconnect_attempts, and callbacks."""
    pub, mock_nc = publisher
    await pub.connect()

    mock_nc.connect.assert_called_once()
    kw = mock_nc.connect.call_args.kwargs
    assert kw["reconnect_time_wait"] == 2
    assert kw["max_reconnect_attempts"] == 60
    assert callable(kw["error_cb"])
    assert callable(kw["disconnected_cb"])
    assert callable(kw["reconnected_cb"])
    assert pub._connected is True


@pytest.mark.asyncio
async def test_disconnect_callback_clears_connected(publisher):
    """_on_disconnect must set _connected=False."""
    pub, _ = publisher
    pub._connected = True

    await pub._on_disconnect()
    assert pub._connected is False


@pytest.mark.asyncio
async def test_reconnect_callback_restores_connected(publisher):
    """_on_reconnect must set _connected=True."""
    pub, _ = publisher
    pub._connected = False

    await pub._on_reconnect()
    assert pub._connected is True


@pytest.mark.asyncio
async def test_close_resets_state(publisher):
    """close() must close the NATS client and reset _connected."""
    pub, mock_nc = publisher
    pub.nc = mock_nc
    pub._connected = True

    await pub.close()
    assert pub._connected is False
    mock_nc.close.assert_called_once()
