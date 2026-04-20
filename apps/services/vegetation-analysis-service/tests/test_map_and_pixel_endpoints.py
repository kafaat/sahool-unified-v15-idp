"""Regression tests for Phase-1 + Phase-2 map visualization endpoints.

Pins:

  * The 6 mappable indices are exactly the ones the web client has colour
    ramps for (NDVI, NDRE, NDWI, EVI, SAVI, LAI). If backend and frontend
    drift we break the index picker silently.
  * `/v1/indices/{field_id}/{index_name}/map` exists, requires auth,
    calls ``_verify_field_owned_by_tenant``, and rejects unknown indices
    with 400.
  * `/v1/indices/{field_id}/pixel` exists, requires auth, calls
    ``_verify_field_owned_by_tenant``, and accepts (lat, lon) query
    params.
  * `_sentinel_hub_wms_url` returns None when SENTINEL_HUB_INSTANCE_ID
    is unset, and a valid WMS-template URL when set.
  * Every colour ramp has at least 3 stops (otherwise the MapLibre
    interpolator degenerates).
"""

from __future__ import annotations

import ast
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


_MAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
with open(_MAIN_PATH, encoding="utf-8") as _f:
    _MAIN_SRC = _f.read()
_MAIN_AST = ast.parse(_MAIN_SRC)


# =============================================================================
# _MAPPABLE_INDICES registry
# =============================================================================


def test_mappable_indices_match_web_client_ramps():
    """The 6 indices must match the web client's INDEX_COLOR_STOPS keys
    in NdviTileLayer.tsx. Adding a 7th here without updating the client
    would advertise a layer the browser can't render."""
    from map_registry import MAPPABLE_INDICES as _MAPPABLE_INDICES

    assert set(_MAPPABLE_INDICES) == {"ndvi", "ndre", "ndwi", "evi", "savi", "lai"}


def test_every_mappable_index_has_complete_metadata():
    from map_registry import MAPPABLE_INDICES as _MAPPABLE_INDICES

    required = {"min", "max", "colors", "label_en", "label_ar", "unit"}
    for key, meta in _MAPPABLE_INDICES.items():
        assert required.issubset(meta.keys()), f"{key}: missing {required - set(meta)}"
        # Colour ramp must have enough stops for MapLibre interpolator.
        assert len(meta["colors"]) >= 3, f"{key}: ramp has <3 stops"
        # Min < max — otherwise raster-color interpolation breaks.
        assert meta["min"] < meta["max"], f"{key}: min/max inverted"
        # Bilingual label.
        assert meta["label_en"].strip(), f"{key}: empty English label"
        assert meta["label_ar"].strip(), f"{key}: empty Arabic label"


def test_lai_has_non_negative_min_unlike_vegetation_indices():
    """LAI is a physical quantity (m²/m²); its min must be >= 0.
    Accidentally setting it to -1 like the spectral indices would
    make the entire lower half of the colour ramp unreachable."""
    from map_registry import MAPPABLE_INDICES as _MAPPABLE_INDICES

    assert _MAPPABLE_INDICES["lai"]["min"] >= 0.0
    assert _MAPPABLE_INDICES["lai"]["max"] >= 6.0  # typical max canopy


# =============================================================================
# Sentinel Hub WMS URL helper
# =============================================================================


def test_wms_url_returns_none_when_unconfigured(monkeypatch):
    from map_registry import sentinel_hub_wms_url as _sentinel_hub_wms_url

    monkeypatch.delenv("SENTINEL_HUB_INSTANCE_ID", raising=False)
    assert _sentinel_hub_wms_url("ndvi") is None
    assert _sentinel_hub_wms_url("lai", "2026-04-12") is None


def test_wms_url_shape_when_configured(monkeypatch):
    """When the instance is configured we return a MapLibre-compatible
    raster-tile URL template (with {bbox-epsg-3857}/{width}/{height})."""
    from map_registry import sentinel_hub_wms_url as _sentinel_hub_wms_url

    monkeypatch.setenv("SENTINEL_HUB_INSTANCE_ID", "test-instance-id")
    url = _sentinel_hub_wms_url("ndre", "2026-04-12")

    assert url is not None
    assert "test-instance-id" in url
    assert "layers=NDRE" in url
    assert "{bbox-epsg-3857}" in url
    assert "{width}" in url
    assert "{height}" in url
    assert "time=2026-04-12" in url
    assert url.startswith("https://services.sentinel-hub.com/ogc/wms/")


def test_wms_url_honours_per_index_layer_override(monkeypatch):
    """Allow ops to map ``NDRE`` → ``NDRE_CUSTOM_INSTANCE_CONFIG`` without
    a code change."""
    from map_registry import sentinel_hub_wms_url as _sentinel_hub_wms_url

    monkeypatch.setenv("SENTINEL_HUB_INSTANCE_ID", "test")
    monkeypatch.setenv("SENTINEL_HUB_LAYER_NDRE", "CUSTOM_NDRE_LAYER")

    url = _sentinel_hub_wms_url("ndre")
    assert "layers=CUSTOM_NDRE_LAYER" in url


def test_wms_url_omits_time_when_date_missing(monkeypatch):
    from map_registry import sentinel_hub_wms_url as _sentinel_hub_wms_url

    monkeypatch.setenv("SENTINEL_HUB_INSTANCE_ID", "test")
    url = _sentinel_hub_wms_url("ndvi")
    assert "time=" not in url


# =============================================================================
# AST-pin: endpoints exist with correct signature + security
# =============================================================================


def _find_route(path: str):
    """Locate the async function decorated with @app.get/post(path)."""
    for node in ast.walk(_MAIN_AST):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for deco in node.decorator_list:
            if not isinstance(deco, ast.Call):
                continue
            if not isinstance(deco.func, ast.Attribute):
                continue
            if deco.func.attr not in {"get", "post", "put", "delete"}:
                continue
            if deco.args and isinstance(deco.args[0], ast.Constant):
                if deco.args[0].value == path:
                    return node
    return None


def test_index_map_endpoint_registered():
    node = _find_route("/v1/indices/{field_id}/{index_name}/map")
    assert node is not None, "Map endpoint missing from main.py"
    assert node.name == "get_index_map"


def test_index_map_endpoint_requires_auth_and_ownership():
    node = _find_route("/v1/indices/{field_id}/{index_name}/map")
    assert node is not None
    src = ast.get_source_segment(_MAIN_SRC, node) or ""
    # Auth dependency
    assert "get_current_user" in src, "endpoint must use get_current_user"
    # Ownership verification
    assert "_verify_field_owned_by_tenant" in src, (
        "endpoint must call _verify_field_owned_by_tenant — otherwise a "
        "caller with a valid JWT can read any tenant's field tiles"
    )
    # field_id validation
    assert "_validate_field_id" in src


def test_index_map_endpoint_rejects_unknown_indices():
    """The endpoint must use `_MAPPABLE_INDICES` as its allowlist — not
    the full `VegetationIndex` enum — or we'd advertise raster layers
    for indices the web client has no colour ramp for."""
    node = _find_route("/v1/indices/{field_id}/{index_name}/map")
    assert node is not None
    src = ast.get_source_segment(_MAIN_SRC, node) or ""
    assert "_MAPPABLE_INDICES" in src


def test_pixel_endpoint_registered():
    node = _find_route("/v1/indices/{field_id}/pixel")
    assert node is not None, "Pixel endpoint missing from main.py"
    assert node.name == "get_pixel_inspection"


def test_pixel_endpoint_requires_auth_and_ownership():
    node = _find_route("/v1/indices/{field_id}/pixel")
    assert node is not None
    src = ast.get_source_segment(_MAIN_SRC, node) or ""
    assert "get_current_user" in src
    assert "_verify_field_owned_by_tenant" in src
    assert "_validate_field_id" in src


def test_pixel_endpoint_accepts_lat_lon_query():
    node = _find_route("/v1/indices/{field_id}/pixel")
    assert node is not None
    arg_names = [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
    assert "lat" in arg_names
    assert "lon" in arg_names


def test_pixel_endpoint_reuses_all_indices_pipeline():
    """To keep FPAR/fAPAR and the 16 dedicated interpretations in sync,
    the pixel endpoint must delegate to `get_all_indices` instead of
    re-running the BandData → calculator pipeline itself."""
    node = _find_route("/v1/indices/{field_id}/pixel")
    src = ast.get_source_segment(_MAIN_SRC, node) or ""
    assert "get_all_indices" in src


# =============================================================================
# Parametrised pins on the 6 mappable indices
# =============================================================================


@pytest.mark.parametrize("index", ["ndvi", "ndre", "ndwi", "evi", "savi", "lai"])
def test_every_mappable_index_is_renderable(index):
    """Each mappable index must:
      * be in `_MAPPABLE_INDICES`
      * also be in the `VegetationIndex` enum (so `get_specific_index`
        stays consistent)
    """
    from map_registry import MAPPABLE_INDICES as _MAPPABLE_INDICES
    from vegetation_indices import VegetationIndex

    assert index in _MAPPABLE_INDICES
    enum_values = {v.value for v in VegetationIndex}
    assert index in enum_values, f"{index} in map registry but missing from enum"
