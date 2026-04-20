"""
SAHOOL Satellite Service - eo-learn Integration
تكامل خدمة الأقمار الصناعية مع eo-learn

This module provides integration between the vegetation-analysis-service API
and the sahool-eo package for real satellite data processing.

When sahool-eo and sentinelhub are installed, the service uses
real satellite data. Otherwise, it falls back to simulated data.
"""

import asyncio
import logging
import os
from datetime import UTC, date, datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Check for eo-learn availability
# =============================================================================

EO_LEARN_AVAILABLE = False
SENTINEL_HUB_CONFIGURED = False

try:
    from sahool_eo import (
        AllIndicesTask,
        FieldMonitoringWorkflow,
        SahoolEOClient,
        SentinelHubConfig,
    )

    EO_LEARN_AVAILABLE = True
    logger.info("sahool-eo package available")

    # Check if Sentinel Hub is configured
    if os.environ.get("SENTINEL_HUB_CLIENT_ID") and os.environ.get("SENTINEL_HUB_CLIENT_SECRET"):
        SENTINEL_HUB_CONFIGURED = True
        logger.info("Sentinel Hub credentials configured")
    else:
        logger.warning("Sentinel Hub credentials not set - using simulated data")

except ImportError:
    logger.warning("sahool-eo not installed - using simulated data")
    logger.info("Install with: pip install sahool-eo[full]")


# =============================================================================
# EO Client Singleton
# =============================================================================

_eo_client: Any | None = None


def get_eo_client():
    """Get or create the EO client singleton"""
    global _eo_client

    if not EO_LEARN_AVAILABLE:
        return None

    if _eo_client is None and SENTINEL_HUB_CONFIGURED:
        try:
            config = SentinelHubConfig.from_env()
            _eo_client = SahoolEOClient(config)
            _eo_client.initialize()
            logger.info("EO Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EO Client: {e}")
            return None

    return _eo_client


# =============================================================================
# Real Data Fetching
# =============================================================================


async def fetch_real_satellite_data(
    field_id: str,
    tenant_id: str,
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date | None,
    max_cloud_cover: float = 30.0,
    buffer_degrees: float = 0.01,  # ~1km buffer
    timeout_seconds: float = 60.0,
) -> dict[str, Any] | None:
    """
    Fetch real satellite data using sahool-eo

    Args:
        field_id: Field identifier
        tenant_id: Tenant identifier
        latitude: Center latitude
        longitude: Center longitude
        start_date: Start date
        end_date: End date (None = same as start)
        max_cloud_cover: Maximum cloud coverage %
        buffer_degrees: Buffer around center point
        timeout_seconds: Maximum seconds to wait for the workflow (default 60)

    Returns:
        Analysis results or None if unavailable
    """
    client = get_eo_client()

    if client is None:
        logger.info("EO Client not available, falling back to simulation")
        return None

    try:
        # Create bounding box around point
        bbox = (
            longitude - buffer_degrees,
            latitude - buffer_degrees,
            longitude + buffer_degrees,
            latitude + buffer_degrees,
        )

        # Create time interval
        start_str = start_date.isoformat()
        end_str = (end_date or start_date).isoformat()
        time_interval = (start_str, end_str)

        # Execute field monitoring workflow with a hard timeout so the calling
        # request never hangs indefinitely waiting for Sentinel Hub.
        workflow = FieldMonitoringWorkflow(
            client=client,
            resolution=10,
            max_cloud_coverage=max_cloud_cover,
        )

        async with asyncio.timeout(timeout_seconds):
            result = await asyncio.to_thread(
                workflow.execute,
                field_id=field_id,
                tenant_id=tenant_id,
                bbox=bbox,
                time_interval=time_interval,
                generate_events=True,
            )

        if result.get("status") == "completed":
            logger.info(f"Real satellite data fetched for {field_id}")
            return result
        else:
            logger.warning(f"Workflow failed: {result.get('error')}")
            return None

    except TimeoutError:
        logger.error(
            "Satellite data fetch timed out after %ss for field %s. Falling back to simulation.",
            timeout_seconds,
            field_id,
        )
        return None
    except Exception as e:
        logger.error(f"Failed to fetch real data: {e}")
        return None


def convert_eo_result_to_api_format(
    eo_result: dict[str, Any],
    field_id: str,
    satellite: str = "sentinel-2",
) -> dict[str, Any]:
    """
    Convert sahool-eo result to API response format

    Maps the eo-learn workflow output to the existing API schema
    for backwards compatibility.
    """
    indices = eo_result.get("indices", {})
    health = eo_result.get("health_assessment", {})

    # Extract index values
    ndvi = indices.get("ndvi", {}).get("value", 0)
    evi = indices.get("evi", {}).get("value", 0)
    lai = indices.get("lai", {}).get("value", 0)
    ndwi = indices.get("ndwi", {}).get("value", 0)
    savi = indices.get("savi", {}).get("value", 0)
    ndmi = indices.get("ndmi", {}).get("value", 0)

    return {
        "field_id": field_id,
        "analysis_date": datetime.now(UTC).isoformat(),
        "satellite": satellite,
        "data_source": "real",  # Indicates real data
        "indices": {
            "ndvi": ndvi,
            "ndwi": ndwi,
            "evi": evi,
            "savi": savi,
            "lai": lai,
            "ndmi": ndmi,
        },
        "health_score": health.get("health_score", 50),
        "health_status": health.get("health_status", "unknown"),
        "anomalies": health.get("anomalies", []),
        "recommendations_ar": health.get("recommendations_ar", []),
        "recommendations_en": health.get("recommendations_en", []),
        "metadata": eo_result.get("metadata", {}),
        "events": eo_result.get("events", []),
    }


# =============================================================================
# Data Source Status
# =============================================================================


def get_data_source_status() -> dict[str, Any]:
    """Get current data source status"""
    return {
        "eo_learn_available": EO_LEARN_AVAILABLE,
        "sentinel_hub_configured": SENTINEL_HUB_CONFIGURED,
        "data_mode": ("real" if (EO_LEARN_AVAILABLE and SENTINEL_HUB_CONFIGURED) else "simulated"),
        "message": (
            "Using real Sentinel Hub data"
            if SENTINEL_HUB_CONFIGURED
            else "Using simulated data - configure SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET for real data"
        ),
    }


# =============================================================================
# Configuration Check
# =============================================================================


def check_eo_configuration() -> dict[str, Any]:
    """Check eo-learn configuration and dependencies"""
    checks = {
        "sahool_eo_installed": False,
        "sentinelhub_installed": False,
        "eolearn_installed": False,
        "s2cloudless_installed": False,
        "credentials_configured": False,
        "all_ready": False,
    }

    try:
        import sahool_eo

        checks["sahool_eo_installed"] = True
    except ImportError:
        pass

    try:
        import sentinelhub

        checks["sentinelhub_installed"] = True
    except ImportError:
        pass

    try:
        import eolearn

        checks["eolearn_installed"] = True
    except ImportError:
        pass

    try:
        import s2cloudless

        checks["s2cloudless_installed"] = True
    except ImportError:
        pass

    checks["credentials_configured"] = bool(
        os.environ.get("SENTINEL_HUB_CLIENT_ID") and os.environ.get("SENTINEL_HUB_CLIENT_SECRET")
    )

    checks["all_ready"] = all(
        [
            checks["sahool_eo_installed"],
            checks["sentinelhub_installed"],
            checks["eolearn_installed"],
            checks["credentials_configured"],
        ]
    )

    return checks


# =============================================================================
# Per-band reflectance fetch (Gap A)
# =============================================================================
#
# `fetch_real_satellite_data` above runs the full FieldMonitoringWorkflow
# which calculates indices but discards the raw band array (SahoolExportTask
# has `include_bands=False` by default). For `/v1/imagery/request` we need
# the other shape: raw per-band reflectance without the indices overhead.
#
# This helper uses `SahoolSentinelFetchTask` directly — it's the same
# Sentinel Hub Process API + evalscript that FieldMonitoringWorkflow uses
# internally, just without the post-processing layers.


# Sentinel-2 L2A band order — matches the 10-band evalscript in
# `packages/sahool-eo/tasks/fetch.py`. Maps the NumPy column index to
# the Sentinel-2 band code the API contract expects.
_S2_BAND_ORDER = (
    ("B02", "490nm", 10),
    ("B03", "560nm", 10),
    ("B04", "665nm", 10),
    ("B05", "705nm", 20),
    ("B06", "740nm", 20),
    ("B07", "783nm", 20),
    ("B08", "842nm", 10),
    ("B8A", "865nm", 20),
    ("B11", "1610nm", 20),
    ("B12", "2190nm", 20),
)


async def fetch_real_bands(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date | None = None,
    max_cloud_cover: float = 30.0,
    buffer_degrees: float = 0.01,
    timeout_seconds: float = 60.0,
) -> dict[str, Any] | None:
    """Fetch per-band reflectance from Sentinel Hub Process API.

    Returns a dict with the mean reflectance of each band over the field's
    bbox, plus scene metadata. ``None`` when ``sahool-eo`` isn't
    installed, Sentinel Hub credentials aren't configured, or the request
    fails — caller falls back to the simulated generator.

    Returned shape::

        {
            "bands": [
                {"band_name": "B02", "wavelength_nm": "490nm",
                 "resolution_m": 10, "value": 0.042},
                ...
            ],
            "cloud_cover_percent": 5.2,
            "acquisition_date": "2026-04-20T00:00:00+00:00",
            "scene_id": "SENTINEL2_L2A_2026-04-20",
            "provider": "sentinel_hub",
        }

    Mean-per-band (rather than per-pixel) is the honest summary for the
    simulated-bands API contract — callers that want the raster itself
    should use the dedicated NDVI / imagery-export endpoints.
    """
    if not (EO_LEARN_AVAILABLE and SENTINEL_HUB_CONFIGURED):
        return None

    try:
        import numpy as np
        from eolearn.core import FeatureType
        from sahool_eo import SentinelHubConfig
        from sahool_eo.tasks.fetch import SahoolSentinelFetchTask
        from sentinelhub import CRS, BBox
    except ImportError as e:
        logger.warning(f"sahool-eo deps missing for band fetch: {e}")
        return None

    try:
        sh_config = SentinelHubConfig.from_env()
    except Exception as e:
        # Don't interpolate the full exception — some configuration
        # loaders include credential snippets in error messages. Log
        # only the exception type so a leaked log doesn't expose secrets.
        logger.warning(
            "Sentinel Hub config invalid (exception_type=%s) — falling back to simulated bands",
            type(e).__name__,
        )
        return None

    bbox = BBox(
        bbox=(
            longitude - buffer_degrees,
            latitude - buffer_degrees,
            longitude + buffer_degrees,
            latitude + buffer_degrees,
        ),
        crs=CRS.WGS84,
    )
    end = end_date or start_date
    time_interval = (start_date.isoformat(), end.isoformat())

    task = SahoolSentinelFetchTask(
        max_cloud_coverage=max_cloud_cover,
        config=sh_config,
    )

    try:
        async with asyncio.timeout(timeout_seconds):
            eopatch = await asyncio.to_thread(task.execute, bbox, time_interval)
    except TimeoutError:
        logger.error(f"Band fetch timed out after {timeout_seconds}s")
        return None
    except Exception as e:
        logger.warning(f"SahoolSentinelFetchTask.execute failed: {e}")
        return None

    if eopatch is None:
        return None

    try:
        bands_array = eopatch[FeatureType.DATA].get("BANDS")
        if bands_array is None or bands_array.size == 0:
            return None
        # Shape: (time, h, w, bands) — mean over time + spatial dims
        mean_per_band = np.nanmean(bands_array, axis=(0, 1, 2))
    except Exception as e:
        logger.warning(f"Failed to compute band means: {e}")
        return None

    import math

    bands_payload = []
    for idx, (band_name, wavelength, res) in enumerate(_S2_BAND_ORDER):
        if idx >= len(mean_per_band):
            break
        try:
            value = float(mean_per_band[idx])
        except (TypeError, ValueError):
            continue
        # NaN / inf guard (happens when the whole footprint is cloud-masked).
        # Use math.isnan / math.isinf — the old ``value == value`` trick
        # triggers CodeQL's "comparison of identical values" warning.
        if math.isnan(value) or math.isinf(value):
            continue
        bands_payload.append(
            {
                "band_name": band_name,
                "wavelength_nm": wavelength,
                "resolution_m": res,
                "value": round(value, 4),
            }
        )

    if not bands_payload:
        return None

    # Compute cloud cover from the CLP mask if available (0-255, scale to %)
    cloud_cover_pct: float | None = None
    try:
        clp = eopatch[FeatureType.MASK].get("CLP")
        if clp is not None and clp.size > 0:
            cloud_cover_pct = float(np.mean(clp)) / 2.55  # CLP: 0-255 → %
    except Exception:  # noqa: BLE001
        # CLP is an optional convenience field; any failure here (missing
        # key, empty mask, numeric overflow) just means we report 0.0
        # cloud cover. The caller doesn't depend on this being accurate.
        pass

    return {
        "bands": bands_payload,
        "cloud_cover_percent": round(cloud_cover_pct, 1) if cloud_cover_pct is not None else 0.0,
        "acquisition_date": datetime.combine(start_date, datetime.min.time(), tzinfo=UTC).isoformat(),
        "scene_id": f"SENTINEL2_L2A_{start_date.isoformat()}",
        "provider": "sentinel_hub",
    }
