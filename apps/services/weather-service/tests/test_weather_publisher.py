"""
Tests for WeatherPublisher NATS reconnection behavior.
Verifies connect() uses reconnection parameters and callbacks update state.
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

import pytest

# Resolve file paths relative to this test file
_EVENTS_DIR = Path(__file__).resolve().parent.parent / "src" / "events"


def _load_weather_publisher(mock_nats_cls):
    """
    Load WeatherPublisher by file path with mocked NATS dependency.

    Uses importlib.util.spec_from_file_location to avoid conflicts
    with other 'src' packages when CI runs from repo root.
    """
    # 1. Load types.py as a standalone module (no relative import issues)
    types_path = _EVENTS_DIR / "types.py"
    types_spec = importlib.util.spec_from_file_location("weather_events_types", types_path)
    types_mod = importlib.util.module_from_spec(types_spec)
    types_spec.loader.exec_module(types_mod)

    # 2. Create a fake package so publish.py's `from .types import ...` resolves
    pkg_name = "_weather_events_pkg"
    pkg = ModuleType(pkg_name)
    pkg.__path__ = [str(_EVENTS_DIR)]
    pkg.__package__ = pkg_name

    sys.modules[pkg_name] = pkg
    sys.modules[f"{pkg_name}.types"] = types_mod

    # 3. Stub nats
    nats_stub = ModuleType("nats")
    nats_aio = ModuleType("nats.aio")
    nats_client = ModuleType("nats.aio.client")
    nats_client.Client = mock_nats_cls

    saved = {}
    for name, mod in [
        ("nats", nats_stub),
        ("nats.aio", nats_aio),
        ("nats.aio.client", nats_client),
    ]:
        saved[name] = sys.modules.get(name)
        sys.modules[name] = mod

    # 4. Load publish.py inside the fake package
    pub_path = _EVENTS_DIR / "publish.py"
    pub_spec = importlib.util.spec_from_file_location(
        f"{pkg_name}.publish",
        pub_path,
        submodule_search_locations=[],
    )
    pub_mod = importlib.util.module_from_spec(pub_spec)
    pub_mod.__package__ = pkg_name
    sys.modules[f"{pkg_name}.publish"] = pub_mod
    pub_spec.loader.exec_module(pub_mod)

    return pub_mod, saved


@pytest.fixture
def publisher():
    """Provide a WeatherPublisher with mocked NATS."""
    mock_nc = AsyncMock()
    mock_cls = MagicMock(return_value=mock_nc)

    pub_mod, saved_nats = _load_weather_publisher(mock_cls)

    yield pub_mod.WeatherPublisher(nats_url="nats://test:4222"), mock_nc

    # Cleanup
    for name, original in saved_nats.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original
    for key in list(sys.modules):
        if key.startswith("_weather_events_pkg"):
            del sys.modules[key]


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
