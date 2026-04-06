"""
Tests for Weather Publisher - weather-service
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add service src to path for imports
_service_root = Path(__file__).resolve().parent.parent / "src"
if str(_service_root) not in sys.path:
    sys.path.insert(0, str(_service_root))

from events.publish import WeatherPublisher


class TestWeatherPublisher:
    """Tests for WeatherPublisher"""

    def test_connect_passes_reconnection_params(self):
        """connect() should pass reconnect kwargs to NATS."""
        publisher = WeatherPublisher(nats_url="nats://test:4222")
        mock_nc = AsyncMock()
        with patch("events.publish.NATS", return_value=mock_nc):
            asyncio.run(publisher.connect())
            mock_nc.connect.assert_called_once()
            call_args = mock_nc.connect.call_args
            assert call_args[0][0] == "nats://test:4222"
            assert call_args[1]["reconnect_time_wait"] == 2
            assert call_args[1]["max_reconnect_attempts"] == 60
            assert publisher._connected is True

    def test_disconnect_callback_clears_connected(self):
        """_on_disconnect should set _connected to False."""
        publisher = WeatherPublisher()
        publisher._connected = True
        asyncio.run(publisher._on_disconnect())
        assert publisher._connected is False

    def test_reconnect_callback_restores_connected(self):
        """_on_reconnect should set _connected to True."""
        publisher = WeatherPublisher()
        publisher._connected = False
        asyncio.run(publisher._on_reconnect())
        assert publisher._connected is True

    def test_close_resets_state(self):
        """close() should close connection and reset _connected."""
        publisher = WeatherPublisher()
        publisher.nc = AsyncMock()
        publisher._connected = True
        asyncio.run(publisher.close())
        publisher.nc.close.assert_called_once()
        assert publisher._connected is False
