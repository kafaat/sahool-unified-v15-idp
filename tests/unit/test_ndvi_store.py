"""
Unit tests for ndvi-processor store integration
================================================
Verifies that create_composite() delegates persistence to ndvi_store.save_composite()
rather than writing to _composites directly, so composites are always persisted via
the production store path (DB + in-memory + NATS when configured).
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Bootstrap: load the ndvi-processor src as a properly-namespaced package so
# that relative imports (from .models, from .store, from . import store) work.
# We cannot use a regular "import apps.services.ndvi-processor..." because
# the directory name contains a hyphen which is invalid in Python identifiers.
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SRC = os.path.join(_REPO_ROOT, "apps", "services", "ndvi-processor", "src")
_PKG = "_ndvi_svc_test"


def _bootstrap_ndvi_pkg() -> None:
    if _PKG in sys.modules:
        return
    pkg = types.ModuleType(_PKG)
    pkg.__path__ = [_SRC]  # type: ignore[attr-defined]
    pkg.__package__ = _PKG
    sys.modules[_PKG] = pkg

    for mod_name in ("models", "store", "processing"):
        spec = importlib.util.spec_from_file_location(
            f"{_PKG}.{mod_name}",
            os.path.join(_SRC, f"{mod_name}.py"),
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = _PKG
        sys.modules[f"{_PKG}.{mod_name}"] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]


_bootstrap_ndvi_pkg()

_processing = sys.modules[f"{_PKG}.processing"]
_store = sys.modules[f"{_PKG}.store"]

CompositeMethod = _processing.CompositeMethod
SatelliteSource = _processing.SatelliteSource
create_composite = _processing.create_composite


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCreateCompositeStore:
    """create_composite() must route all persistence through ndvi_store.save_composite()."""

    async def test_create_composite_calls_save_composite(self, monkeypatch: pytest.MonkeyPatch):
        """save_composite is awaited with the correct tenant/field IDs."""
        calls: dict = {}

        async def fake_save_composite(composite_id: str, tenant_id: str, composite_dict: dict):
            calls["composite_id"] = composite_id
            calls["tenant_id"] = tenant_id
            calls["field_id"] = composite_dict["field_id"]

        monkeypatch.setattr(_store, "save_composite", fake_save_composite)

        result = await create_composite(
            tenant_id="00000000-0000-0000-0000-000000000001",
            field_id="field-test-99",
            year=2026,
            month=2,
            method=CompositeMethod.MEDIAN_NDVI,
            source=SatelliteSource.SENTINEL_2,
        )

        assert result["field_id"] == "field-test-99"
        assert calls["tenant_id"] == "00000000-0000-0000-0000-000000000001"
        assert calls["field_id"] == "field-test-99"
        assert calls["composite_id"] == result["composite_id"]

    async def test_create_composite_returns_expected_shape(self, monkeypatch: pytest.MonkeyPatch):
        """Returned dict has all required CompositeResponse keys."""

        async def _noop(*_a, **_kw):
            pass

        monkeypatch.setattr(_store, "save_composite", _noop)

        result = await create_composite(
            tenant_id="t1",
            field_id="f1",
            year=2026,
            month=3,
            method=CompositeMethod.MAX_NDVI,
            source=SatelliteSource.LANDSAT_8,
        )

        for key in (
            "composite_id",
            "field_id",
            "year",
            "month",
            "method",
            "source",
            "statistics",
            "images_used",
            "files",
            "created_at",
        ):
            assert key in result, f"Missing key: {key}"

        assert result["year"] == 2026
        assert result["month"] == 3
        assert result["method"] == CompositeMethod.MAX_NDVI.value
        assert result["source"] == SatelliteSource.LANDSAT_8.value

    async def test_create_composite_does_not_write_composites_directly(self, monkeypatch: pytest.MonkeyPatch):
        """_composites dict is updated only via save_composite, not bypassed directly."""

        async def _noop(*_a, **_kw):
            pass

        monkeypatch.setattr(_store, "save_composite", _noop)
        _store._composites.clear()

        await create_composite(
            tenant_id="t2",
            field_id="f2",
            year=2025,
            month=12,
            method=CompositeMethod.MEAN_NDVI,
            source=SatelliteSource.MODIS,
        )

        # _noop did NOT write to _composites → dict stays empty
        assert len(_store._composites) == 0, "_composites must only be written via save_composite, not bypassed"
