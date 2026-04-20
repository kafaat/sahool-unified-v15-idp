"""Regression tests for Gap A — per-band reflectance via Sentinel Hub
Process API (``/v1/imagery/request``).

Pins:
  * ``eo_integration.fetch_real_bands`` exists with the expected signature.
  * ``/v1/imagery/request`` uses the real-bands path when
    ``EO_LEARN_AVAILABLE`` and ``SENTINEL_HUB_CONFIGURED`` are True,
    tagging the response with ``X-Data-Source: real``.
  * Falls back cleanly to the simulated generator when the real path
    isn't available or returns None, tagging
    ``X-Data-Source: simulated``.
  * The ``SahoolSentinelFetchTask`` + evalscript infrastructure in
    ``packages/sahool-eo/tasks/fetch.py`` stays wired to the fetch
    helper (pins against accidental refactor).
"""

from __future__ import annotations

import inspect
import os
import sys
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)


# =============================================================================
# eo_integration.fetch_real_bands — signature + return shape
# =============================================================================


def test_fetch_real_bands_signature():
    """``fetch_real_bands`` must accept the minimal kwargs clients need
    to build a Sentinel Hub request — pinning the contract so future
    edits don't silently remove a parameter the endpoint depends on."""
    from eo_integration import fetch_real_bands

    sig = inspect.signature(fetch_real_bands)
    required = {"latitude", "longitude", "start_date"}
    assert required <= set(sig.parameters)


@pytest.mark.asyncio
async def test_fetch_real_bands_returns_none_when_eo_unavailable(monkeypatch):
    """When the sahool-eo package isn't installed, the helper must
    short-circuit to ``None`` (not raise) so the caller can fall back
    to the simulated generator."""
    import eo_integration

    monkeypatch.setattr(eo_integration, "EO_LEARN_AVAILABLE", False)
    monkeypatch.setattr(eo_integration, "SENTINEL_HUB_CONFIGURED", True)

    result = await eo_integration.fetch_real_bands(
        latitude=15.5,
        longitude=44.2,
        start_date=date.today(),
    )
    assert result is None


@pytest.mark.asyncio
async def test_fetch_real_bands_returns_none_when_credentials_missing(monkeypatch):
    """Credentials not configured → return None (fall back to sim)."""
    import eo_integration

    monkeypatch.setattr(eo_integration, "EO_LEARN_AVAILABLE", True)
    monkeypatch.setattr(eo_integration, "SENTINEL_HUB_CONFIGURED", False)

    result = await eo_integration.fetch_real_bands(
        latitude=15.5,
        longitude=44.2,
        start_date=date.today(),
    )
    assert result is None


# =============================================================================
# /v1/imagery/request — real path vs fallback
# =============================================================================


@pytest.mark.asyncio
async def test_imagery_endpoint_uses_real_path_when_available(monkeypatch):
    """When ``fetch_real_bands`` returns real data, the imagery endpoint
    must build the response from that payload and tag ``X-Data-Source: real``."""
    import src.main as main_mod
    from fastapi import Response
    from src.main import ImageryRequest, SatelliteSource, request_imagery

    monkeypatch.setattr(main_mod, "EO_LEARN_AVAILABLE", True)
    monkeypatch.setattr(main_mod, "SENTINEL_HUB_CONFIGURED", True)

    async def _fake_fetch(**kwargs):
        return {
            "bands": [
                {"band_name": "B02", "wavelength_nm": "490nm", "resolution_m": 10, "value": 0.042},
                {"band_name": "B04", "wavelength_nm": "665nm", "resolution_m": 10, "value": 0.081},
                {"band_name": "B08", "wavelength_nm": "842nm", "resolution_m": 10, "value": 0.310},
            ],
            "cloud_cover_percent": 5.2,
            "acquisition_date": "2026-04-20T00:00:00+00:00",
            "scene_id": "SENTINEL2_L2A_2026-04-20",
            "provider": "sentinel_hub",
        }

    monkeypatch.setattr(main_mod, "fetch_real_bands", _fake_fetch)

    req = ImageryRequest(
        field_id="real-test-field",
        latitude=15.5,
        longitude=44.2,
        satellite=SatelliteSource.SENTINEL2,
    )
    response = Response()
    mock_user = MagicMock(tenant_id="t1")

    result = await request_imagery(req, response, user=mock_user)

    # Bands must match the real payload exactly (not simulated)
    assert len(result.bands) == 3
    band_names = [b.band_name for b in result.bands]
    assert band_names == ["B02", "B04", "B08"]
    assert result.bands[0].value == 0.042
    assert result.bands[2].value == 0.310
    assert result.cloud_cover_percent == 5.2

    # Response headers carry the transparency marker
    assert response.headers["X-Data-Source"] == "real"
    assert response.headers["X-Data-Provider"] == "sentinel_hub"


@pytest.mark.asyncio
async def test_imagery_endpoint_falls_back_to_simulated_when_eo_unavailable(monkeypatch):
    """When sahool-eo isn't configured, the endpoint must fall back to
    the simulated generator and tag ``X-Data-Source: simulated``."""
    import src.main as main_mod
    from fastapi import Response
    from src.main import ImageryRequest, SatelliteSource, request_imagery

    monkeypatch.setattr(main_mod, "EO_LEARN_AVAILABLE", False)

    req = ImageryRequest(
        field_id="sim-fallback-test",
        latitude=15.5,
        longitude=44.2,
        satellite=SatelliteSource.SENTINEL2,
    )
    response = Response()
    mock_user = MagicMock(tenant_id="t1")

    result = await request_imagery(req, response, user=mock_user)

    # Must still produce a well-formed SatelliteImagery, with bands
    assert result.field_id == "sim-fallback-test"
    assert len(result.bands) > 0
    assert response.headers["X-Data-Source"] == "simulated"
    assert response.headers["X-Data-Provider"] == "simulated"


@pytest.mark.asyncio
async def test_imagery_endpoint_falls_back_when_fetch_returns_none(monkeypatch):
    """When fetch_real_bands returns None (e.g. Sentinel Hub 404, no
    clear scenes in window) the endpoint still serves an envelope —
    via the simulated fallback."""
    import src.main as main_mod
    from fastapi import Response
    from src.main import ImageryRequest, SatelliteSource, request_imagery

    monkeypatch.setattr(main_mod, "EO_LEARN_AVAILABLE", True)
    monkeypatch.setattr(main_mod, "SENTINEL_HUB_CONFIGURED", True)

    async def _fetch_returns_none(**kwargs):
        return None

    monkeypatch.setattr(main_mod, "fetch_real_bands", _fetch_returns_none)

    req = ImageryRequest(
        field_id="fetch-none-test",
        latitude=15.5,
        longitude=44.2,
        satellite=SatelliteSource.SENTINEL2,
    )
    response = Response()
    mock_user = MagicMock(tenant_id="t1")

    result = await request_imagery(req, response, user=mock_user)
    assert result.field_id == "fetch-none-test"
    assert response.headers["X-Data-Source"] == "simulated"


@pytest.mark.asyncio
async def test_imagery_endpoint_requires_tenant(monkeypatch):
    """Defense-in-depth: the imagery endpoint must 403 when the user
    has no tenant_id, regardless of which data-source path is active."""
    from fastapi import HTTPException, Response
    from src.main import ImageryRequest, SatelliteSource, request_imagery

    req = ImageryRequest(
        field_id="no-tenant-test",
        latitude=15.5,
        longitude=44.2,
        satellite=SatelliteSource.SENTINEL2,
    )
    response = Response()
    # User without tenant_id
    bad_user = MagicMock(tenant_id="")

    with pytest.raises(HTTPException) as exc_info:
        await request_imagery(req, response, user=bad_user)
    assert exc_info.value.status_code == 403


# =============================================================================
# Infrastructure wiring — sahool-eo Process API integration exists
# =============================================================================


def test_sahool_sentinel_fetch_task_has_evalscript():
    """Infra pin: the Sentinel Hub Process API wiring lives in
    ``packages/sahool-eo/tasks/fetch.py``. If someone removes the
    evalscript, this test will catch it before the endpoint starts
    returning wrong band counts."""
    src_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "packages",
        "sahool-eo",
        "tasks",
        "fetch.py",
    )
    with open(src_path) as f:
        src = f.read()
    # The 10-band evalscript must still be present
    assert "SahoolSentinelFetchTask" in src
    assert "EVALSCRIPT" in src
    # All 10 bands in the evalscript output array
    for band in ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]:
        assert band in src, f"Evalscript is missing band {band}"
    # Still uses SentinelHubRequest (the Process API entry point)
    assert "SentinelHubRequest" in src
