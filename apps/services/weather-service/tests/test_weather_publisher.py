"""
Tests for WeatherPublisher NATS reconnection behavior.
Verifies connect() uses reconnection parameters and callbacks update state.
"""

import importlib.util
import pytest
from unittest.mock import AsyncMock, MagicMock


def _load_publish_module(mock_nats_cls):
    """Load publish.py with a mocked NATS class."""
    spec = importlib.util.spec_from_file_location(
        "publish",
        "apps/services/weather-service/src/events/publish.py",
    )
    mod = importlib.util.module_from_spec(spec)
    mod.NATS = mock_nats_cls
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def publish_mod():
    mock_nc = AsyncMock()
    mock_cls = MagicMock(return_value=mock_nc)
    mod = _load_publish_module(mock_cls)
    return mod, mock_nc


@pytest.mark.asyncio
async def test_connect_passes_reconnection_params(publish_mod):
    """connect() must pass reconnect_time_wait, max_reconnect_attempts, and callbacks."""
    mod, mock_nc = publish_mod
    pub = mod.WeatherPublisher(nats_url="nats://test:4222")
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
async def test_disconnect_callback_clears_connected(publish_mod):
    """_on_disconnect must set _connected=False."""
    mod, _ = publish_mod
    pub = mod.WeatherPublisher()
    pub._connected = True

    await pub._on_disconnect()
    assert pub._connected is False


@pytest.mark.asyncio
async def test_reconnect_callback_restores_connected(publish_mod):
    """_on_reconnect must set _connected=True."""
    mod, _ = publish_mod
    pub = mod.WeatherPublisher()
    pub._connected = False

    await pub._on_reconnect()
    assert pub._connected is True


@pytest.mark.asyncio
async def test_close_resets_state(publish_mod):
    """close() must close the NATS client and reset _connected."""
    mod, mock_nc = publish_mod
    pub = mod.WeatherPublisher()
    pub.nc = mock_nc
    pub._connected = True

    await pub.close()
    assert pub._connected is False
    mock_nc.close.assert_called_once()
