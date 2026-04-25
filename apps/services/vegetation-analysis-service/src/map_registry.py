"""Registry of mappable vegetation indices + Sentinel Hub WMS helper.

Extracted from ``main.py`` so tests (and, later, a separate
tile-proxy service) can import these without dragging in the full
FastAPI app, every router, the NATS client, the ML models, and the
Sentinel Hub SDK.

Keep this module import-pure: no FastAPI, no logging side-effects,
no env reads at import time.
"""

from __future__ import annotations

import os
from typing import Any

# Indices whose raster tiles the MapLibre web layer has a colour ramp +
# bilingual legend copy for. Backend accepts more indices over the value
# API, but only these are advertised as map layers. Keep in sync with
# ``apps/web/src/features/fields/components/NdviTileLayer.tsx``.
MAPPABLE_INDICES: dict[str, dict[str, Any]] = {
    "ndvi": {
        "min": -1.0,
        "max": 1.0,
        "colors": ["#8B4513", "#FF0000", "#FFAA00", "#FFFF00", "#55FF00", "#00FF00", "#006600"],
        "label_en": "Normalized Difference Vegetation Index",
        "label_ar": "مؤشر الاختلاف الطبيعي للغطاء النباتي",
        "unit": "index",
    },
    "ndwi": {
        "min": -1.0,
        "max": 1.0,
        "colors": ["#8B0000", "#FF8C00", "#FFD700", "#87CEEB", "#4169E1", "#00008B"],
        "label_en": "Normalized Difference Water Index",
        "label_ar": "مؤشر الاختلاف الطبيعي للماء",
        "unit": "index",
    },
    "evi": {
        "min": -1.0,
        "max": 1.0,
        "colors": ["#8B4513", "#FF0000", "#FFFF00", "#00CC00", "#006600"],
        "label_en": "Enhanced Vegetation Index",
        "label_ar": "مؤشر الغطاء النباتي المحسّن",
        "unit": "index",
    },
    "savi": {
        "min": -1.0,
        "max": 1.0,
        "colors": ["#8B4513", "#D2691E", "#FFAA00", "#FFFF00", "#00CC00", "#006600"],
        "label_en": "Soil-Adjusted Vegetation Index",
        "label_ar": "مؤشر الغطاء النباتي المعدّل للتربة",
        "unit": "index",
    },
    "ndre": {
        "min": -1.0,
        "max": 1.0,
        "colors": ["#4B0082", "#FF0000", "#FFAA00", "#FFFF00", "#00CC00", "#006400"],
        "label_en": "Normalized Difference Red-Edge",
        "label_ar": "مؤشر الاختلاف الطبيعي للحافة الحمراء",
        "unit": "index (chlorophyll proxy)",
    },
    "lai": {
        "min": 0.0,
        "max": 8.0,
        "colors": ["#F5DEB3", "#FFD700", "#ADFF2F", "#32CD32", "#228B22", "#006400", "#003300"],
        "label_en": "Leaf Area Index",
        "label_ar": "مؤشر مساحة الأوراق",
        "unit": "m²/m²",
    },
}


def sentinel_hub_wms_url(index_name: str, date_str: str | None = None) -> str | None:
    """Return a Sentinel Hub WMS tile-URL template for *index_name* if
    the SH instance is configured via ``SENTINEL_HUB_INSTANCE_ID``,
    else None.

    The template uses MapLibre's raster-tile placeholders
    (``{bbox-epsg-3857}`` / ``{width}`` / ``{height}``) so the browser
    can fetch each tile directly.

    Per-index layer names can be overridden with
    ``SENTINEL_HUB_LAYER_<INDEX>`` env vars (so ops can re-map NDRE to
    a custom instance layer without a code change).
    """
    instance_id = os.getenv("SENTINEL_HUB_INSTANCE_ID")
    if not instance_id:
        return None

    layer = os.getenv(f"SENTINEL_HUB_LAYER_{index_name.upper()}", index_name.upper())
    base = "https://services.sentinel-hub.com/ogc/wms"
    params = [
        "service=WMS",
        "request=GetMap",
        "version=1.3.0",
        f"layers={layer}",
        "format=image/png",
        "transparent=true",
        "bbox={bbox-epsg-3857}",
        "crs=EPSG:3857",
        "width={width}",
        "height={height}",
    ]
    if date_str:
        params.append(f"time={date_str}")
    return f"{base}/{instance_id}?" + "&".join(params)
