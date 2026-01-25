"""
🛰️ SAHOOL Satellite Service - eo-learn Integration
تكامل خدمة الأقمار الصناعية مع eo-learn

This module provides integration between the satellite-service API
and the sahool-eo package for real satellite data processing.

When sahool-eo and sentinelhub are installed, the service uses
real satellite data. Otherwise, it falls back to simulated data.
"""

import logging
import os
from datetime import date, datetime
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

        # Execute field monitoring workflow
        workflow = FieldMonitoringWorkflow(
            client=client,
            resolution=10,
            max_cloud_coverage=max_cloud_cover,
        )

        result = workflow.execute(
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
        "analysis_date": datetime.utcnow().isoformat(),
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
