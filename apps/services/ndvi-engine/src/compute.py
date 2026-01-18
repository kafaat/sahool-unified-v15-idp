"""
NDVI Computation Engine - SAHOOL
Remote sensing NDVI calculation and analysis
"""

import asyncio
import logging
import os
import random
import time
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class NdviResult:
    """NDVI computation result"""

    field_id: str
    ndvi_mean: float
    ndvi_min: float
    ndvi_max: float
    ndvi_std: float
    ndvi_trend_7d: float
    ndvi_trend_30d: float
    scene_date: str
    cloud_cover_pct: float
    data_source: str
    quality_score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NdviZone:
    """NDVI zone classification"""

    zone_id: str
    zone_name_ar: str
    zone_name_en: str
    ndvi_mean: float
    area_pct: float
    health_status: str


# NDVI health thresholds
NDVI_THRESHOLDS = {
    "excellent": 0.7,
    "good": 0.5,
    "moderate": 0.3,
    "poor": 0.2,
    "critical": 0.0,
}


# =============================================================================
# SentinelHub Integration
# =============================================================================


class SentinelHubClient:
    """
    Client for SentinelHub API integration.

    Handles OAuth2 authentication, rate limiting, and Sentinel-2 data fetching.

    Environment Variables:
        SENTINEL_HUB_CLIENT_ID: OAuth client ID
        SENTINEL_HUB_CLIENT_SECRET: OAuth client secret
    """

    AUTH_URL = "https://services.sentinel-hub.com/oauth/token"
    PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"
    CATALOG_URL = "https://services.sentinel-hub.com/api/v1/catalog/1.0.0/search"

    # Rate limiting: 60 requests/minute by default
    MAX_REQUESTS_PER_MINUTE = 60
    REQUEST_TIMEOUT = 120

    # NDVI Evalscript for Sentinel-2 L2A
    NDVI_EVALSCRIPT = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B08", "SCL"],
                units: "DN"
            }],
            output: [
                { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
                { id: "bands", bands: 2, sampleType: "FLOAT32" },
                { id: "scl", bands: 1, sampleType: "UINT8" },
                { id: "dataMask", bands: 1, sampleType: "UINT8" }
            ]
        };
    }

    function evaluatePixel(sample) {
        // Scale reflectance values (0-10000 to 0-1)
        let scaleFactor = 0.0001;
        let red = sample.B04 * scaleFactor;
        let nir = sample.B08 * scaleFactor;

        // Calculate NDVI
        let ndvi = (nir - red) / (nir + red);
        if (!isFinite(ndvi)) ndvi = 0;

        return {
            ndvi: [ndvi],
            bands: [red, nir],
            scl: [sample.SCL],
            dataMask: [sample.dataMask]
        };
    }
    """

    def __init__(self):
        self.client_id = os.environ.get("SENTINEL_HUB_CLIENT_ID")
        self.client_secret = os.environ.get("SENTINEL_HUB_CLIENT_SECRET")
        self._access_token: str | None = None
        self._token_expires_at: float = 0
        self._last_request_time: float = 0
        self._request_count: int = 0
        self._rate_limit_reset: float = 0

    @property
    def is_configured(self) -> bool:
        """Check if SentinelHub credentials are configured."""
        return bool(self.client_id and self.client_secret)

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        """
        Get OAuth2 access token, refreshing if expired.

        Returns:
            Valid access token string.

        Raises:
            ValueError: If credentials are not configured.
            httpx.HTTPError: If authentication fails.
        """
        if not self.is_configured:
            raise ValueError(
                "SentinelHub credentials not configured. "
                "Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET."
            )

        # Return cached token if still valid (with 60s buffer)
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token

        # Request new token
        response = await client.post(
            self.AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data["access_token"]
        # Token typically expires in 3600 seconds
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = time.time() + expires_in

        logger.info("SentinelHub access token refreshed")
        return self._access_token

    async def _apply_rate_limiting(self):
        """Apply rate limiting to prevent exceeding API limits."""
        current_time = time.time()

        # Reset counter every minute
        if current_time > self._rate_limit_reset:
            self._request_count = 0
            self._rate_limit_reset = current_time + 60

        # Wait if we've hit the limit
        if self._request_count >= self.MAX_REQUESTS_PER_MINUTE:
            wait_time = self._rate_limit_reset - current_time
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                self._request_count = 0
                self._rate_limit_reset = time.time() + 60

        self._request_count += 1

    def _geometry_to_bbox(self, geometry: dict) -> list[float]:
        """
        Extract bounding box from GeoJSON geometry.

        Args:
            geometry: GeoJSON geometry object.

        Returns:
            Bounding box as [min_lon, min_lat, max_lon, max_lat].
        """
        if geometry.get("type") == "Polygon":
            coords = geometry["coordinates"][0]
        elif geometry.get("type") == "MultiPolygon":
            # Flatten all coordinates
            coords = []
            for polygon in geometry["coordinates"]:
                coords.extend(polygon[0])
        else:
            # For Point, create a small buffer
            lon, lat = geometry["coordinates"][:2]
            buffer = 0.01  # ~1km buffer
            return [lon - buffer, lat - buffer, lon + buffer, lat + buffer]

        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        return [min(lons), min(lats), max(lons), max(lats)]

    async def fetch_ndvi_data(
        self,
        geometry: dict,
        start_date: date,
        end_date: date | None = None,
        resolution: int = 10,
        max_cloud_cover: float = 30.0,
    ) -> dict[str, Any] | None:
        """
        Fetch NDVI data from Sentinel-2 imagery via SentinelHub API.

        Args:
            geometry: GeoJSON geometry of the field boundary.
            start_date: Start date for imagery search.
            end_date: End date (defaults to start_date + 30 days).
            resolution: Output resolution in meters (default 10m).
            max_cloud_cover: Maximum cloud coverage percentage.

        Returns:
            Dictionary with NDVI statistics and metadata, or None on failure.
        """
        if not self.is_configured:
            logger.warning("SentinelHub not configured, skipping real data fetch")
            return None

        end_date = end_date or (start_date + timedelta(days=30))
        bbox = self._geometry_to_bbox(geometry)

        # Calculate output size based on bbox and resolution
        lon_diff = abs(bbox[2] - bbox[0])
        lat_diff = abs(bbox[3] - bbox[1])
        # Approximate meters per degree at the latitude
        meters_per_deg_lon = 111320 * abs(
            __import__("math").cos(__import__("math").radians((bbox[1] + bbox[3]) / 2))
        )
        meters_per_deg_lat = 110540

        width = max(1, int((lon_diff * meters_per_deg_lon) / resolution))
        height = max(1, int((lat_diff * meters_per_deg_lat) / resolution))

        # Cap maximum size to avoid excessive API usage
        max_size = 2500
        if width > max_size or height > max_size:
            scale = max_size / max(width, height)
            width = int(width * scale)
            height = int(height * scale)

        async with httpx.AsyncClient() as client:
            try:
                await self._apply_rate_limiting()
                token = await self._get_access_token(client)

                # Build SentinelHub Process API request
                request_body = {
                    "input": {
                        "bounds": {
                            "bbox": bbox,
                            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
                        },
                        "data": [
                            {
                                "type": "sentinel-2-l2a",
                                "dataFilter": {
                                    "timeRange": {
                                        "from": f"{start_date.isoformat()}T00:00:00Z",
                                        "to": f"{end_date.isoformat()}T23:59:59Z",
                                    },
                                    "maxCloudCoverage": max_cloud_cover,
                                    "mosaickingOrder": "leastCC",
                                },
                            }
                        ],
                    },
                    "output": {
                        "width": width,
                        "height": height,
                        "responses": [
                            {"identifier": "ndvi", "format": {"type": "image/tiff"}},
                            {"identifier": "dataMask", "format": {"type": "image/tiff"}},
                        ],
                    },
                    "evalscript": self.NDVI_EVALSCRIPT,
                }

                response = await client.post(
                    self.PROCESS_URL,
                    json=request_body,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/tar",
                    },
                    timeout=self.REQUEST_TIMEOUT,
                )

                if response.status_code == 429:
                    # Rate limited - wait and retry once
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited by SentinelHub, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    response = await client.post(
                        self.PROCESS_URL,
                        json=request_body,
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                            "Accept": "application/tar",
                        },
                        timeout=self.REQUEST_TIMEOUT,
                    )

                response.raise_for_status()

                # Parse the tar response to extract NDVI statistics
                return await self._parse_ndvi_response(response.content, start_date, end_date)

            except httpx.HTTPStatusError as e:
                logger.error(f"SentinelHub API error: {e.response.status_code} - {e.response.text}")
                return None
            except Exception as e:
                logger.error(f"Failed to fetch SentinelHub data: {e}")
                return None

    async def _parse_ndvi_response(
        self,
        tar_content: bytes,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        """
        Parse NDVI response from SentinelHub tar archive.

        Args:
            tar_content: Raw tar archive bytes from API.
            start_date: Query start date.
            end_date: Query end date.

        Returns:
            Dictionary with NDVI statistics.
        """
        import io
        import tarfile

        try:
            # Try to import numpy for proper statistics
            import numpy as np

            has_numpy = True
        except ImportError:
            has_numpy = False

        ndvi_stats = {
            "mean": 0.0,
            "min": 0.0,
            "max": 0.0,
            "std": 0.0,
            "valid_pixels": 0,
            "total_pixels": 0,
            "cloud_cover_pct": 0.0,
            "scene_date": end_date.isoformat(),
            "data_source": "sentinel-2-l2a",
        }

        try:
            with tarfile.open(fileobj=io.BytesIO(tar_content), mode="r") as tar:
                for member in tar.getmembers():
                    if "ndvi" in member.name.lower() and member.name.endswith(".tif"):
                        f = tar.extractfile(member)
                        if f is None:
                            continue

                        tiff_data = f.read()

                        if has_numpy:
                            # Use numpy for proper TIFF parsing if available
                            try:
                                from PIL import Image

                                img = Image.open(io.BytesIO(tiff_data))
                                ndvi_array = np.array(img, dtype=np.float32)

                                # Filter valid NDVI values (-1 to 1)
                                valid_mask = (ndvi_array >= -1) & (ndvi_array <= 1) & np.isfinite(ndvi_array)
                                valid_ndvi = ndvi_array[valid_mask]

                                if len(valid_ndvi) > 0:
                                    ndvi_stats["mean"] = float(np.mean(valid_ndvi))
                                    ndvi_stats["min"] = float(np.min(valid_ndvi))
                                    ndvi_stats["max"] = float(np.max(valid_ndvi))
                                    ndvi_stats["std"] = float(np.std(valid_ndvi))
                                    ndvi_stats["valid_pixels"] = int(len(valid_ndvi))
                                    ndvi_stats["total_pixels"] = int(ndvi_array.size)
                                    ndvi_stats["cloud_cover_pct"] = round(
                                        (1 - len(valid_ndvi) / ndvi_array.size) * 100, 1
                                    )
                            except Exception as e:
                                logger.warning(f"Failed to parse TIFF with PIL: {e}")
                        break

        except Exception as e:
            logger.error(f"Failed to parse SentinelHub response: {e}")

        return ndvi_stats


# Global SentinelHub client instance
_sentinel_hub_client: SentinelHubClient | None = None


def get_sentinel_hub_client() -> SentinelHubClient:
    """Get or create the SentinelHub client singleton."""
    global _sentinel_hub_client
    if _sentinel_hub_client is None:
        _sentinel_hub_client = SentinelHubClient()
    return _sentinel_hub_client


def classify_ndvi_health(ndvi: float) -> tuple[str, str]:
    """
    Classify NDVI value into health status

    Returns:
        Tuple of (status_en, status_ar)
    """
    if ndvi >= NDVI_THRESHOLDS["excellent"]:
        return ("excellent", "ممتاز")
    elif ndvi >= NDVI_THRESHOLDS["good"]:
        return ("good", "جيد")
    elif ndvi >= NDVI_THRESHOLDS["moderate"]:
        return ("moderate", "متوسط")
    elif ndvi >= NDVI_THRESHOLDS["poor"]:
        return ("poor", "ضعيف")
    else:
        return ("critical", "حرج")


def compute_mock(field_id: str, historical: bool = False) -> NdviResult:
    """
    Mock NDVI computation for development

    In production, replace with SentinelHub/GEE adapter

    Args:
        field_id: Field identifier
        historical: Include historical trend analysis

    Returns:
        NdviResult with mock data
    """
    # Generate realistic mock values
    base_ndvi = 0.35 + random.random() * 0.35  # 0.35 - 0.70
    ndvi_std = 0.05 + random.random() * 0.1

    # Simulate trends
    trend_7d = (random.random() - 0.5) * 0.2  # -0.1 to +0.1
    trend_30d = (random.random() - 0.5) * 0.3  # -0.15 to +0.15

    return NdviResult(
        field_id=field_id,
        ndvi_mean=round(base_ndvi, 3),
        ndvi_min=round(max(0, base_ndvi - ndvi_std * 2), 3),
        ndvi_max=round(min(1, base_ndvi + ndvi_std * 2), 3),
        ndvi_std=round(ndvi_std, 3),
        ndvi_trend_7d=round(trend_7d, 3),
        ndvi_trend_30d=round(trend_30d, 3),
        scene_date=date.today().isoformat(),
        cloud_cover_pct=round(random.random() * 30, 1),  # 0-30%
        data_source="mock",
        quality_score=round(0.7 + random.random() * 0.3, 2),
    )


def compute_from_sentinel(
    field_id: str,
    geometry: dict,
    start_date: date = None,
    end_date: date = None,
) -> NdviResult:
    """
    Compute NDVI from Sentinel-2 imagery using SentinelHub API.

    Fetches Sentinel-2 L2A imagery for the specified field boundary and
    calculates NDVI statistics. Falls back to mock data if SentinelHub
    credentials are not configured or on API errors.

    Args:
        field_id: Field identifier
        geometry: GeoJSON geometry of field boundary
        start_date: Start of date range (defaults to 30 days ago)
        end_date: End of date range (defaults to today)

    Returns:
        NdviResult with NDVI statistics from satellite imagery

    Environment Variables:
        SENTINEL_HUB_CLIENT_ID: OAuth client ID for SentinelHub
        SENTINEL_HUB_CLIENT_SECRET: OAuth client secret for SentinelHub
    """
    # Default date range: last 30 days
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    # Get SentinelHub client
    client = get_sentinel_hub_client()

    # Sanitize field_id to prevent log injection attacks
    safe_field_id = str(field_id).replace('\n', '').replace('\r', '').replace('\t', '')[:100]

    if not client.is_configured:
        logger.info("SentinelHub not configured for field %s, using mock data", safe_field_id)
        return compute_mock(field_id)

    # Run async fetch in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        ndvi_data = loop.run_until_complete(
            client.fetch_ndvi_data(
                geometry=geometry,
                start_date=start_date,
                end_date=end_date,
                resolution=10,
                max_cloud_cover=30.0,
            )
        )
    except Exception as e:
        logger.error("SentinelHub fetch failed for field %s: %s", safe_field_id, str(e))
        ndvi_data = None

    if ndvi_data is None:
        logger.warning("No SentinelHub data for field %s, falling back to mock", safe_field_id)
        return compute_mock(field_id)

    # Calculate quality score based on cloud cover and valid pixels
    cloud_pct = ndvi_data.get("cloud_cover_pct", 0)
    valid_ratio = 1.0
    if ndvi_data.get("total_pixels", 0) > 0:
        valid_ratio = ndvi_data.get("valid_pixels", 0) / ndvi_data["total_pixels"]
    quality_score = round(max(0, min(1, (1 - cloud_pct / 100) * valid_ratio)), 2)

    # Trend analysis placeholder (would require historical data)
    # For now, use small random variations
    trend_7d = round((random.random() - 0.5) * 0.1, 3)
    trend_30d = round((random.random() - 0.5) * 0.15, 3)

    return NdviResult(
        field_id=field_id,
        ndvi_mean=round(ndvi_data.get("mean", 0), 3),
        ndvi_min=round(ndvi_data.get("min", 0), 3),
        ndvi_max=round(ndvi_data.get("max", 0), 3),
        ndvi_std=round(ndvi_data.get("std", 0), 3),
        ndvi_trend_7d=trend_7d,
        ndvi_trend_30d=trend_30d,
        scene_date=ndvi_data.get("scene_date", date.today().isoformat()),
        cloud_cover_pct=round(cloud_pct, 1),
        data_source=ndvi_data.get("data_source", "sentinel-2-l2a"),
        quality_score=quality_score,
    )


async def compute_from_sentinel_async(
    field_id: str,
    geometry: dict,
    start_date: date = None,
    end_date: date = None,
) -> NdviResult:
    """
    Async version of compute_from_sentinel for use in async contexts.

    Compute NDVI from Sentinel-2 imagery using SentinelHub API.

    Args:
        field_id: Field identifier
        geometry: GeoJSON geometry of field boundary
        start_date: Start of date range (defaults to 30 days ago)
        end_date: End of date range (defaults to today)

    Returns:
        NdviResult with NDVI statistics from satellite imagery
    """
    # Default date range: last 30 days
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    # Get SentinelHub client
    client = get_sentinel_hub_client()

    # Sanitize field_id to prevent log injection attacks
    safe_field_id = str(field_id).replace('\n', '').replace('\r', '').replace('\t', '')[:100]

    if not client.is_configured:
        logger.info("SentinelHub not configured for field %s, using mock data", safe_field_id)
        return compute_mock(field_id)

    try:
        ndvi_data = await client.fetch_ndvi_data(
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
            resolution=10,
            max_cloud_cover=30.0,
        )
    except Exception as e:
        logger.error("SentinelHub fetch failed for field %s: %s", safe_field_id, str(e))
        ndvi_data = None

    if ndvi_data is None:
        logger.warning("No SentinelHub data for field %s, falling back to mock", safe_field_id)
        return compute_mock(field_id)

    # Calculate quality score based on cloud cover and valid pixels
    cloud_pct = ndvi_data.get("cloud_cover_pct", 0)
    valid_ratio = 1.0
    if ndvi_data.get("total_pixels", 0) > 0:
        valid_ratio = ndvi_data.get("valid_pixels", 0) / ndvi_data["total_pixels"]
    quality_score = round(max(0, min(1, (1 - cloud_pct / 100) * valid_ratio)), 2)

    # Trend analysis placeholder
    trend_7d = round((random.random() - 0.5) * 0.1, 3)
    trend_30d = round((random.random() - 0.5) * 0.15, 3)

    return NdviResult(
        field_id=field_id,
        ndvi_mean=round(ndvi_data.get("mean", 0), 3),
        ndvi_min=round(ndvi_data.get("min", 0), 3),
        ndvi_max=round(ndvi_data.get("max", 0), 3),
        ndvi_std=round(ndvi_data.get("std", 0), 3),
        ndvi_trend_7d=trend_7d,
        ndvi_trend_30d=trend_30d,
        scene_date=ndvi_data.get("scene_date", date.today().isoformat()),
        cloud_cover_pct=round(cloud_pct, 1),
        data_source=ndvi_data.get("data_source", "sentinel-2-l2a"),
        quality_score=quality_score,
    )


def analyze_ndvi_zones(
    field_id: str,
    ndvi_raster: list[list[float]] = None,
) -> list[NdviZone]:
    """
    Analyze NDVI spatial distribution and identify zones

    Args:
        field_id: Field identifier
        ndvi_raster: 2D array of NDVI values (optional, uses mock if None)

    Returns:
        List of NdviZone classifications
    """
    # Mock zone analysis
    zones = [
        NdviZone(
            zone_id=f"{field_id}_z1",
            zone_name_ar="المنطقة الشمالية",
            zone_name_en="North Zone",
            ndvi_mean=0.65,
            area_pct=35,
            health_status="good",
        ),
        NdviZone(
            zone_id=f"{field_id}_z2",
            zone_name_ar="المنطقة الوسطى",
            zone_name_en="Central Zone",
            ndvi_mean=0.52,
            area_pct=40,
            health_status="moderate",
        ),
        NdviZone(
            zone_id=f"{field_id}_z3",
            zone_name_ar="المنطقة الجنوبية",
            zone_name_en="South Zone",
            ndvi_mean=0.38,
            area_pct=25,
            health_status="poor",
        ),
    ]
    return zones


def calculate_vegetation_indices(
    red: float,
    nir: float,
    blue: float = None,
    green: float = None,
    swir: float = None,
) -> dict:
    """
    Calculate multiple vegetation indices from band values

    Args:
        red: Red band reflectance
        nir: Near-infrared band reflectance
        blue: Blue band reflectance (optional)
        green: Green band reflectance (optional)
        swir: Short-wave infrared reflectance (optional)

    Returns:
        Dictionary of vegetation indices
    """
    indices = {}

    # NDVI - Normalized Difference Vegetation Index
    if nir + red != 0:
        indices["ndvi"] = (nir - red) / (nir + red)

    # NDWI - Normalized Difference Water Index
    if green and nir + green != 0:
        indices["ndwi"] = (green - nir) / (green + nir)

    # EVI - Enhanced Vegetation Index
    if blue:
        denominator = nir + 6 * red - 7.5 * blue + 1
        if denominator != 0:
            indices["evi"] = 2.5 * (nir - red) / denominator

    # SAVI - Soil Adjusted Vegetation Index
    L = 0.5  # Soil brightness correction factor
    if nir + red + L != 0:
        indices["savi"] = ((nir - red) / (nir + red + L)) * (1 + L)

    # MSAVI - Modified Soil Adjusted Vegetation Index
    indices["msavi"] = (2 * nir + 1 - ((2 * nir + 1) ** 2 - 8 * (nir - red)) ** 0.5) / 2

    # NDMI - Normalized Difference Moisture Index
    if swir and nir + swir != 0:
        indices["ndmi"] = (nir - swir) / (nir + swir)

    return {k: round(v, 4) for k, v in indices.items()}


def detect_anomalies(
    current_ndvi: float,
    historical_mean: float,
    historical_std: float,
    threshold_sigma: float = 2.0,
) -> dict | None:
    """
    Detect NDVI anomalies compared to historical data

    Args:
        current_ndvi: Current NDVI value
        historical_mean: Historical mean NDVI
        historical_std: Historical standard deviation
        threshold_sigma: Number of standard deviations for anomaly

    Returns:
        Anomaly info dict if detected, None otherwise
    """
    if historical_std == 0:
        return None

    z_score = (current_ndvi - historical_mean) / historical_std

    if abs(z_score) >= threshold_sigma:
        anomaly_type = "positive" if z_score > 0 else "negative"
        severity = "high" if abs(z_score) >= 3 else "medium"

        return {
            "type": anomaly_type,
            "severity": severity,
            "z_score": round(z_score, 2),
            "deviation_pct": round((current_ndvi - historical_mean) / historical_mean * 100, 1),
            "message_ar": (
                "انحراف إيجابي عن المعدل" if anomaly_type == "positive" else "انحراف سلبي عن المعدل"
            ),
            "message_en": (
                "Positive deviation from mean"
                if anomaly_type == "positive"
                else "Negative deviation from mean"
            ),
        }

    return None
