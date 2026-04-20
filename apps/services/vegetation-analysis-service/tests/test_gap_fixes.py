"""Regression tests for the follow-up gap fixes (Gaps #1, #3, #4).

Each test pins one invariant so the gap cannot silently regress:
 * Gap #3 — VRA endpoints require authentication (5 routes)
 * Gap #1 — `_get_timeseries_data` accepts lat/lon and uses multi_provider
             when available; simulated path is clearly marked
 * Gap #4 — VRAGenerator.classify_zones calls multi_provider.get_indices()
             when a multi_provider is supplied, using real NDVI as zone mean
"""

from __future__ import annotations

import inspect
import os
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)


# =============================================================================
# Gap #3 — VRA endpoints require authentication
# =============================================================================


def test_vra_endpoints_have_auth_dependency():
    """The 5 sensitive VRA routes (generate / zones / prescriptions /
    prescription details / export) must take a `_user=Depends(get_current_user)`
    argument — without it, any network-adjacent caller can exfiltrate
    prescriptions or cause the generator to spend compute budget."""
    src_path = os.path.join(os.path.dirname(__file__), "..", "src", "vra_endpoints.py")
    with open(src_path) as f:
        src = f.read()

    # For each sensitive route decorator, verify the next `async def` block
    # includes Depends(get_current_user). /v1/vra/info is reference-only
    # (public OK) so it's excluded.
    protected_routes = [
        '@app.post("/v1/vra/generate"',
        '@app.get("/v1/vra/zones/{field_id}")',
        '@app.get("/v1/vra/prescriptions/{field_id}")',
        '@app.get("/v1/vra/prescription/{prescription_id}")',
        '@app.get("/v1/vra/export/{prescription_id}")',
        '@app.delete("/v1/vra/prescription/{prescription_id}")',
    ]

    for route in protected_routes:
        idx = src.find(route)
        assert idx != -1, f"Route {route} not found in vra_endpoints.py"
        # Look ahead to the signature close `:` of the next `async def`
        sig_start = src.find("async def", idx)
        assert sig_start != -1, f"No async def after {route}"
        # Closing `):` marks end of signature
        sig_end = src.find("):", sig_start)
        assert sig_end != -1, f"Malformed signature after {route}"
        sig = src[sig_start:sig_end]
        assert "Depends(get_current_user)" in sig, (
            f"Route {route} is missing `Depends(get_current_user)` in its "
            f"signature. Any unauthenticated caller can hit it."
        )


# =============================================================================
# Gap #1 — timeseries real-data path via multi_provider
# =============================================================================


def test_get_timeseries_data_accepts_lat_lon():
    """_get_timeseries_data must accept optional lat/lon kwargs so callers
    can opt-in to the real multi_provider path (EOSDA/OneSoil pattern)."""
    from src.main import _get_timeseries_data

    sig = inspect.signature(_get_timeseries_data)
    assert "lat" in sig.parameters, "_get_timeseries_data must accept lat kwarg"
    assert "lon" in sig.parameters, "_get_timeseries_data must accept lon kwarg"
    # Defaults must be None so the simulated path still works for callers
    # that don't know the coordinates (e.g. /v1/phenology/{field_id})
    assert sig.parameters["lat"].default is None
    assert sig.parameters["lon"].default is None


def test_get_timeseries_endpoint_exposes_lat_lon():
    """The public `/v1/timeseries/{field_id}` endpoint must accept lat/lon
    query params so mobile/web clients can opt-in to real data."""
    from src.main import get_timeseries

    sig = inspect.signature(get_timeseries)
    assert "lat" in sig.parameters
    assert "lon" in sig.parameters


@pytest.mark.asyncio
async def test_timeseries_fetches_real_data_via_multi_provider(monkeypatch):
    """When coords are supplied AND _multi_provider is available AND it
    returns non-simulated data, the result must be tagged
    data_source="real" with the provider name."""
    from datetime import date, datetime

    import src.main as main_mod
    from src.main import SatelliteSource, _get_timeseries_data

    # Craft a fake multi_provider that returns non-simulated indices
    class _FakeIndices:
        ndvi = 0.72
        ndwi = 0.30
        evi = 0.55

    class _FakeResult:
        data = _FakeIndices()
        provider = "sentinel_hub"
        is_simulated = False

    class _FakeMP:
        async def get_indices(self, lat, lon, acquisition_date, satellite):
            return _FakeResult()

    monkeypatch.setattr(main_mod, "_multi_provider", _FakeMP())
    monkeypatch.setattr(main_mod, "USE_MULTI_PROVIDER", True)
    # Skip cache so the real-data path is exercised deterministically
    monkeypatch.setattr(main_mod, "_cache_available", False)

    result = await _get_timeseries_data(
        field_id="real-test",
        days=10,
        satellite=SatelliteSource.SENTINEL2,
        lat=15.5,
        lon=44.2,
    )
    assert result["data_source"] == "real"
    assert result["data_provider"] == "sentinel_hub"
    assert len(result["timeseries"]) > 0
    # NDVI should be 0.72 across points (fake provider returns same value)
    assert all(p["ndvi"] == 0.72 for p in result["timeseries"])


@pytest.mark.asyncio
async def test_timeseries_tags_simulated_when_any_provider_is_simulated(monkeypatch):
    """EOSDA honesty convention: if any date in the series was served by
    the SimulatedProvider (last tier in the fallback chain), the entire
    series must be tagged data_source="simulated" so consumers never
    mistake a partial-real result for fully-real data."""
    import src.main as main_mod
    from src.main import SatelliteSource, _get_timeseries_data

    class _FakeIndices:
        ndvi = 0.5
        ndwi = 0.1
        evi = 0.4

    class _FakeResult:
        data = _FakeIndices()
        provider = "Simulated"
        is_simulated = True  # every point is simulated

    class _FakeMP:
        async def get_indices(self, *args, **kwargs):
            return _FakeResult()

    monkeypatch.setattr(main_mod, "_multi_provider", _FakeMP())
    monkeypatch.setattr(main_mod, "USE_MULTI_PROVIDER", True)
    monkeypatch.setattr(main_mod, "_cache_available", False)

    result = await _get_timeseries_data(
        field_id="sim-test",
        days=10,
        satellite=SatelliteSource.SENTINEL2,
        lat=15.5,
        lon=44.2,
    )
    assert result["data_source"] == "simulated"


@pytest.mark.asyncio
async def test_timeseries_falls_back_to_simulated_when_no_coords(monkeypatch):
    """When no coords are supplied the helper must stay on the legacy
    simulated path — backward compatibility for callers that don't have
    field geometry (phenology, anomaly detection from _fetch_ndvi_…)."""
    import src.main as main_mod
    from src.main import SatelliteSource, _get_timeseries_data

    monkeypatch.setattr(main_mod, "_cache_available", False)

    result = await _get_timeseries_data(
        field_id="no-coords-test",
        days=30,
        satellite=SatelliteSource.SENTINEL2,
    )
    assert result["data_source"] == "simulated"
    assert result["data_provider"] == "simulated"


# =============================================================================
# Gap #4 — VRAGenerator.classify_zones uses multi_provider when available
# =============================================================================


@pytest.mark.asyncio
async def test_vra_classify_zones_uses_multi_provider_for_ndvi():
    """When a multi_provider is injected into VRAGenerator, classify_zones
    must call get_indices() and use the returned NDVI as the zone mean
    instead of the hardcoded 0.55 stub."""
    from vra_generator import VRAGenerator

    # Mock multi_provider that returns NDVI=0.78 (clearly different from
    # the hardcoded 0.55 fallback, so we can see it took effect)
    fake_indices = MagicMock(ndvi=0.78, ndwi=0.2, evi=0.6)
    fake_result = MagicMock(data=fake_indices, is_simulated=False, provider="sentinel_hub")
    mock_mp = MagicMock()
    mock_mp.get_indices = AsyncMock(return_value=fake_result)

    generator = VRAGenerator(multi_provider=mock_mp)
    stats = await generator.classify_zones(
        field_id="real-ndvi-test",
        latitude=15.5,
        longitude=44.2,
        num_zones=3,
    )

    # The zone-mean NDVI must now reflect the real provider's value
    assert stats.ndvi_mean == 0.78, (
        f"classify_zones should use the real NDVI from multi_provider "
        f"(0.78) but got {stats.ndvi_mean}. Is get_indices() being called?"
    )
    # get_indices must have been called with field coordinates
    mock_mp.get_indices.assert_called_once()


@pytest.mark.asyncio
async def test_vra_classify_zones_falls_back_to_hardcoded_without_multi_provider():
    """Backward compatibility: when no multi_provider is wired, the zones
    must still be producible — just with the hardcoded 0.55 stub (and
    is_synthetic=True propagates)."""
    from vra_generator import VRAGenerator

    generator = VRAGenerator(multi_provider=None)
    stats = await generator.classify_zones(
        field_id="no-mp-test",
        latitude=15.5,
        longitude=44.2,
        num_zones=3,
    )
    assert stats.ndvi_mean == 0.55  # Hardcoded fallback
    assert stats.is_synthetic is True


@pytest.mark.asyncio
async def test_vra_classify_zones_falls_back_when_provider_raises():
    """Defensive: any exception from multi_provider.get_indices must fall
    back to the hardcoded stub rather than propagating — precision-ag
    prescriptions must remain producible even when providers flake."""
    from vra_generator import VRAGenerator

    mock_mp = MagicMock()
    mock_mp.get_indices = AsyncMock(side_effect=RuntimeError("Sentinel Hub down"))

    generator = VRAGenerator(multi_provider=mock_mp)
    stats = await generator.classify_zones(
        field_id="provider-fail-test",
        latitude=15.5,
        longitude=44.2,
        num_zones=3,
    )
    # Must not raise, must fall back to hardcoded
    assert stats.ndvi_mean == 0.55
    assert stats.is_synthetic is True


@pytest.mark.asyncio
async def test_vra_is_synthetic_remains_true_even_with_real_ndvi():
    """is_synthetic=True tells the UI the prescription is unsafe to
    dispatch — even when the NDVI value is real, the polygons + area
    are still fabricated (no rasterio + field polygon integration).
    This invariant must hold until real field geometry lands."""
    from vra_generator import VRAGenerator

    fake_indices = MagicMock(ndvi=0.82, ndwi=0.3, evi=0.65)
    fake_result = MagicMock(data=fake_indices, is_simulated=False, provider="sentinel_hub")
    mock_mp = MagicMock()
    mock_mp.get_indices = AsyncMock(return_value=fake_result)

    generator = VRAGenerator(multi_provider=mock_mp)
    stats = await generator.classify_zones(
        field_id="real-ndvi-synth-geom",
        latitude=15.5,
        longitude=44.2,
        num_zones=3,
    )
    # Real NDVI → but still synthetic because geometry is fake
    assert stats.ndvi_mean == 0.82
    assert stats.is_synthetic is True, (
        "Even with real NDVI from multi_provider, is_synthetic must stay "
        "True because the zone polygons / total_area_ha are still fabricated. "
        "Climate FieldView / OneSoil refuse to publish without real geometry — "
        "we surface the warning instead."
    )
