"""Regression tests for the deep-scan fixes landed on 2026-04-20.

Each test pins one behavioural invariant so future refactors cannot silently
reintroduce the defect. Cross-references the best-practice conventions from
OneSoil / EOSDA Crop Monitoring (data_source transparency), Climate FieldView
(synthetic-prescription safety), and EOSDA / Sentera (cache-first fetch).
"""

from __future__ import annotations

import asyncio
import os
import sys

import pytest

# For leaf-module imports (vra_generator, yield_predictor, cache) — these
# modules have no relative imports, so the flat path works.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# For main.py imports — main.py uses relative imports (from .boundary_endpoints
# etc.), so we must import it as `src.main` via the service root on sys.path.
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)


# =============================================================================
# Fix #5 — yield_predictor no longer has the dead-compute line
# =============================================================================


def test_yield_predictor_no_dead_ndvi_mean_line():
    """yield_predictor.py:216 used to have `sum(...)/len(...)` discarded
    as a statement after a ruff auto-fix stripped `ndvi_mean =`. The
    fix deletes that dead-compute line entirely."""
    src_path = os.path.join(os.path.dirname(__file__), "..", "src", "yield_predictor.py")
    with open(src_path) as f:
        src = f.read()
    # The offending pattern used to appear verbatim; it must not re-appear.
    assert "sum(ndvi_series) / len(ndvi_series) if ndvi_series else 0.5" not in src, (
        "Dead-compute line reintroduced. If you need ndvi_mean, assign it: "
        "ndvi_mean = sum(ndvi_series) / len(ndvi_series) if ndvi_series else 0.5"
    )


# =============================================================================
# Fix #4 — dead files removed
# =============================================================================


def test_no_dead_endpoint_files():
    """export_endpoints.py and yield_endpoints.py were template/DummyApp
    files never imported anywhere. They must not be reintroduced — any
    route they claim to define is already registered from main.py."""
    src_dir = os.path.join(os.path.dirname(__file__), "..", "src")
    assert not os.path.exists(os.path.join(src_dir, "export_endpoints.py"))
    assert not os.path.exists(os.path.join(src_dir, "yield_endpoints.py"))


# =============================================================================
# Fix #6 — dead helpers removed
# =============================================================================


def test_dead_helpers_removed_from_main():
    """_validate_days_range and _validate_ndvi_value were defined but
    never referenced. Removed to keep the helper surface honest."""
    src_path = os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
    with open(src_path) as f:
        src = f.read()
    assert "def _validate_days_range" not in src
    assert "def _validate_ndvi_value" not in src


# =============================================================================
# Fix #2 — VRA synthetic marker
# =============================================================================


@pytest.mark.asyncio
async def test_vra_prescription_marked_synthetic_when_no_real_ndvi():
    """OneSoil / Climate FieldView pattern: prescriptions built without
    real imagery must carry is_synthetic=True and a bilingual warning,
    so the UI can refuse to dispatch to the variable-rate controller."""
    from vra_generator import VRAGenerator, VRAType

    generator = VRAGenerator(multi_provider=None)
    prescription = await generator.generate_prescription(
        field_id="field_synth_test",
        latitude=15.5,
        longitude=44.2,
        vra_type=VRAType.FERTILIZER,
        target_rate=100.0,
        unit="kg/ha",
        tenant_id="test-tenant-synth",
        num_zones=3,
    )

    # Because classify_zones has no real NDVI integration, every
    # prescription from the current code path is synthetic.
    assert prescription.is_synthetic is True
    assert prescription.data_warning_en is not None
    assert prescription.data_warning_ar is not None
    assert "synthetic" in prescription.data_warning_en.lower() or "real" in prescription.data_warning_en.lower()
    # Arabic warning must mention "افتراضية" (synthetic) or "حقيقية" (real)
    assert ("افتراضي" in prescription.data_warning_ar) or ("حقيقي" in prescription.data_warning_ar)


@pytest.mark.asyncio
async def test_vra_zone_statistics_carries_is_synthetic():
    """ZoneStatistics is the internal contract. The flag must be set at
    the source so it propagates deterministically into every call site."""
    from vra_generator import VRAGenerator

    generator = VRAGenerator(multi_provider=None)
    stats = await generator.classify_zones(
        field_id="field_synth_test",
        latitude=15.5,
        longitude=44.2,
        num_zones=3,
    )
    assert stats.is_synthetic is True


# =============================================================================
# Fix #1 — data_source marker on FieldAnalysis / SatelliteImagery
# =============================================================================


def test_field_analysis_has_data_source_default_simulated():
    """Pydantic model must default data_source='simulated' so legacy
    consumers that don't set it explicitly still see the honest value."""
    from datetime import UTC, datetime

    from src.main import (
        FieldAnalysis,
        SatelliteBand,
        SatelliteImagery,
        SatelliteSource,
        VegetationIndices,
    )

    imagery = SatelliteImagery(
        imagery_id="test",
        field_id="f1",
        satellite=SatelliteSource.SENTINEL2,
        acquisition_date=datetime.now(UTC),
        cloud_cover_percent=5.0,
        sun_elevation=60.0,
        bands=[SatelliteBand(band_name="B04", wavelength_nm="665", resolution_m=10, value=0.1)],
        scene_id="S2_test",
        tile_id="T30QAA",
        processing_level="L2A",
    )
    assert imagery.data_source == "simulated"
    assert imagery.data_provider == "simulated"

    analysis = FieldAnalysis(
        field_id="f1",
        analysis_date=datetime.now(UTC),
        satellite=SatelliteSource.SENTINEL2,
        imagery=imagery,
        indices=VegetationIndices(ndvi=0.5, ndwi=0.1, evi=0.4, savi=0.4, lai=2.0, ndmi=0.1),
        health_score=75.0,
        health_status="good",
        anomalies=[],
        recommendations_ar=[],
        recommendations_en=[],
    )
    assert analysis.data_source == "simulated"
    assert analysis.data_provider == "simulated"


def test_field_analysis_accepts_real_data_source():
    """When multi_provider returns real data, data_source must be "real"
    and data_provider should name the provider (sentinel_hub, etc.)."""
    from datetime import UTC, datetime

    from src.main import (
        FieldAnalysis,
        SatelliteBand,
        SatelliteImagery,
        SatelliteSource,
        VegetationIndices,
    )

    imagery = SatelliteImagery(
        imagery_id="test",
        field_id="f1",
        satellite=SatelliteSource.SENTINEL2,
        acquisition_date=datetime.now(UTC),
        cloud_cover_percent=5.0,
        sun_elevation=60.0,
        bands=[SatelliteBand(band_name="B04", wavelength_nm="665", resolution_m=10, value=0.1)],
        scene_id="S2_test",
        tile_id="T30QAA",
        processing_level="L2A",
        data_source="real",
        data_provider="sentinel_hub",
    )
    assert imagery.data_source == "real"
    assert imagery.data_provider == "sentinel_hub"

    analysis = FieldAnalysis(
        field_id="f1",
        analysis_date=datetime.now(UTC),
        satellite=SatelliteSource.SENTINEL2,
        imagery=imagery,
        indices=VegetationIndices(ndvi=0.5, ndwi=0.1, evi=0.4, savi=0.4, lai=2.0, ndmi=0.1),
        health_score=75.0,
        health_status="good",
        anomalies=[],
        recommendations_ar=[],
        recommendations_en=[],
        data_source="real",
        data_provider="sentinel_hub",
    )
    assert analysis.data_source == "real"
    assert analysis.data_provider == "sentinel_hub"


# =============================================================================
# Fix #3 — cache layer now accepts tenant_id and scopes keys
# =============================================================================


def test_cache_keys_are_tenant_scoped():
    """Redis cache keys must embed tenant_id to prevent cross-tenant leakage.
    Two different tenants querying the same field on the same day must not
    share a cache bucket."""
    from cache import _analysis_cache_key, _ns, _timeseries_cache_key

    # Same field, different tenants → different keys
    key_a = _analysis_cache_key("field1", "sentinel2", tenant_id="tenant-a")
    key_b = _analysis_cache_key("field1", "sentinel2", tenant_id="tenant-b")
    assert key_a != key_b
    assert "tenant-a" in key_a
    assert "tenant-b" in key_b

    # Same tenant same field → same key (cache-hit path)
    key_a2 = _analysis_cache_key("field1", "sentinel2", tenant_id="tenant-a")
    assert key_a == key_a2

    # No tenant → "global" bucket (fallback only; must never be used for
    # tenant-owned data — enforced at the caller's type contract)
    key_global = _analysis_cache_key("field1", "sentinel2")
    assert ":global:" in key_global
    assert _ns(None) == "global"
    assert _ns("") == "global"
    assert _ns("   ") == "global"

    # timeseries cache same invariant
    t_a = _timeseries_cache_key("field1", 30, "sentinel2", tenant_id="tenant-a")
    t_b = _timeseries_cache_key("field1", 30, "sentinel2", tenant_id="tenant-b")
    assert t_a != t_b


@pytest.mark.asyncio
async def test_cache_functions_accept_tenant_id_kwarg():
    """The public cache_* / get_cached_* wrappers must forward tenant_id
    so no call site accidentally falls through to the 'global' bucket."""
    import inspect

    from cache import cache_analysis, cache_timeseries, get_cached_analysis, get_cached_timeseries

    for fn in (cache_analysis, cache_timeseries, get_cached_analysis, get_cached_timeseries):
        sig = inspect.signature(fn)
        assert "tenant_id" in sig.parameters, (
            f"{fn.__name__} is missing tenant_id kwarg — cache keys will "
            f"collapse to the 'global' bucket and leak across tenants"
        )


# =============================================================================
# Fix #3 — timeseries helper now threads tenant_id + cache-first pattern
# =============================================================================


def test_get_timeseries_data_signature_has_tenant_id():
    """_get_timeseries_data must accept tenant_id so cache writes/reads
    are tenant-scoped (Sentera / EOSDA cost-control pattern)."""
    import inspect

    from src.main import _get_timeseries_data

    sig = inspect.signature(_get_timeseries_data)
    assert "tenant_id" in sig.parameters


@pytest.mark.asyncio
async def test_get_timeseries_data_returns_data_source_marker():
    """The simulated fallback must tag its output data_source='simulated'
    — OneSoil / EOSDA transparency convention."""
    from src.main import SatelliteSource, _get_timeseries_data

    result = await _get_timeseries_data("test-field", days=30, satellite=SatelliteSource.SENTINEL2)
    assert result["data_source"] == "simulated"
    assert result["data_provider"] == "simulated"
    # Structural invariants still hold
    assert "timeseries" in result
    assert isinstance(result["timeseries"], list)
    assert len(result["timeseries"]) > 0


# =============================================================================
# Previously fixed — NameError regression pins
# =============================================================================


def test_weather_integration_no_hardcoded_sandbox_path():
    """Earlier commit 95b0869e: weather_integration.py used
    sys.path.insert(0, "/home/user/sahool-unified-v15-idp") which silently
    degraded get_crop() in production. Pin so it can't come back."""
    src_path = os.path.join(os.path.dirname(__file__), "..", "src", "weather_integration.py")
    with open(src_path) as f:
        src = f.read()
    assert "/home/user/sahool-unified-v15-idp" not in src


def test_analyze_ndvi_timeseries_captures_tenant_id():
    """Earlier commit 776b4d09: analyze_ndvi_timeseries dropped
    `tenant_id =` but still referenced the name on line 1693, raising
    NameError silently swallowed by the NATS-publish try block. Pin so
    the variable is captured when referenced downstream."""
    src_path = os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
    with open(src_path) as f:
        src = f.read()
    # The function body must assign tenant_id before referencing it
    func_start = src.index("async def analyze_ndvi_timeseries")
    func_end = src.index("async def", func_start + 10)
    body = src[func_start:func_end]
    # There must not be a bare tenant-check call followed later by
    # `tenant_id=tenant_id` without capturing the return value.
    # Accept either the bare `_require_tenant_id(user)` path OR the
    # ownership-aware `_verify_field_owned_by_tenant(user, field_id)`
    # path (both return the tenant_id).
    if "tenant_id=tenant_id" in body:
        has_require_capture = "tenant_id = _require_tenant_id(user)" in body
        has_verify_capture = "tenant_id = await _verify_field_owned_by_tenant(user, field_id" in body
        assert has_require_capture or has_verify_capture, (
            "analyze_ndvi_timeseries uses tenant_id without capturing it — "
            "NameError regression. Capture via "
            "`tenant_id = await _verify_field_owned_by_tenant(user, field_id)` "
            "(preferred, includes ownership check) or "
            "`tenant_id = _require_tenant_id(user)` (tenant-presence only)."
        )
