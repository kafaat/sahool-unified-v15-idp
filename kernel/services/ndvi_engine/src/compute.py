"""
NDVI Computation Engine - SAHOOL
Remote sensing NDVI calculation and analysis
"""

from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional
import random


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
    Compute NDVI from Sentinel-2 imagery

    Placeholder for SentinelHub integration

    Args:
        field_id: Field identifier
        geometry: GeoJSON geometry of field
        start_date: Start of date range
        end_date: End of date range

    Returns:
        NdviResult from satellite imagery
    """
    # TODO: Implement SentinelHub integration
    # For now, return mock data
    return compute_mock(field_id)


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
) -> Optional[dict]:
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
            "message_ar": "انحراف إيجابي عن المعدل" if anomaly_type == "positive" else "انحراف سلبي عن المعدل",
            "message_en": "Positive deviation from mean" if anomaly_type == "positive" else "Negative deviation from mean",
        }

    return None
