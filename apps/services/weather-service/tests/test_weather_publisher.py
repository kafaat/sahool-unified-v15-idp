"""
Tests for WeatherPublisher NATS reconnection behavior.
Verifies connect() uses reconnection parameters and callbacks update state.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.events.publish import WeatherPublisher


@pytest.fixture
def publisher(monkeypatch):
    """Create a WeatherPublisher with a mocked NATS class."""
    mock_nc = AsyncMock()
    mock_cls = MagicMock(return_value=mock_nc)
    monkeypatch.setattr("src.events.publish.NATS", mock_cls)
    return WeatherPublisher(nats_url="nats://test:4222"), mock_nc


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
