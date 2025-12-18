"""
Multi-Satellite Support - SAHOOL NDVI Engine
Sentinel-2, Landsat-8/9, MODIS Integration
Merged from satellite-service v15.3
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import random


class SatelliteSource(str, Enum):
    """Supported satellite sources"""
    SENTINEL2 = "sentinel-2"
    LANDSAT8 = "landsat-8"
    LANDSAT9 = "landsat-9"
    MODIS = "modis"


@dataclass
class SatelliteBand:
    """Satellite band information"""
    band_id: str
    name: str
    wavelength_nm: str
    resolution_m: int
    value: float


@dataclass
class SatelliteImagery:
    """Satellite imagery metadata and bands"""
    imagery_id: str
    field_id: str
    satellite: SatelliteSource
    acquisition_date: datetime
    cloud_cover_pct: float
    sun_elevation: float
    bands: list[SatelliteBand]
    scene_id: str
    tile_id: str
    processing_level: str


# Satellite configuration database
SATELLITE_CONFIGS = {
    SatelliteSource.SENTINEL2: {
        "name": "Sentinel-2 MSI",
        "name_ar": "سينتنل-2",
        "operator": "ESA",
        "revisit_days": 5,
        "resolution_m": 10,
        "bands": {
            "B02": {"name": "Blue", "wavelength": "490nm", "resolution": 10},
            "B03": {"name": "Green", "wavelength": "560nm", "resolution": 10},
            "B04": {"name": "Red", "wavelength": "665nm", "resolution": 10},
            "B08": {"name": "NIR", "wavelength": "842nm", "resolution": 10},
            "B8A": {"name": "NIR Narrow", "wavelength": "865nm", "resolution": 20},
            "B11": {"name": "SWIR1", "wavelength": "1610nm", "resolution": 20},
            "B12": {"name": "SWIR2", "wavelength": "2190nm", "resolution": 20},
        },
    },
    SatelliteSource.LANDSAT8: {
        "name": "Landsat-8 OLI/TIRS",
        "name_ar": "لاندسات-8",
        "operator": "NASA/USGS",
        "revisit_days": 16,
        "resolution_m": 30,
        "bands": {
            "B2": {"name": "Blue", "wavelength": "482nm", "resolution": 30},
            "B3": {"name": "Green", "wavelength": "561nm", "resolution": 30},
            "B4": {"name": "Red", "wavelength": "654nm", "resolution": 30},
            "B5": {"name": "NIR", "wavelength": "865nm", "resolution": 30},
            "B6": {"name": "SWIR1", "wavelength": "1609nm", "resolution": 30},
            "B7": {"name": "SWIR2", "wavelength": "2201nm", "resolution": 30},
            "B10": {"name": "Thermal1", "wavelength": "10895nm", "resolution": 100},
        },
    },
    SatelliteSource.LANDSAT9: {
        "name": "Landsat-9 OLI-2/TIRS-2",
        "name_ar": "لاندسات-9",
        "operator": "NASA/USGS",
        "revisit_days": 16,
        "resolution_m": 30,
        "bands": {
            "B2": {"name": "Blue", "wavelength": "482nm", "resolution": 30},
            "B3": {"name": "Green", "wavelength": "561nm", "resolution": 30},
            "B4": {"name": "Red", "wavelength": "654nm", "resolution": 30},
            "B5": {"name": "NIR", "wavelength": "865nm", "resolution": 30},
            "B6": {"name": "SWIR1", "wavelength": "1609nm", "resolution": 30},
            "B7": {"name": "SWIR2", "wavelength": "2201nm", "resolution": 30},
            "B10": {"name": "Thermal1", "wavelength": "10600nm", "resolution": 100},
        },
    },
    SatelliteSource.MODIS: {
        "name": "MODIS Terra/Aqua",
        "name_ar": "موديس",
        "operator": "NASA",
        "revisit_days": 1,
        "resolution_m": 250,
        "bands": {
            "B01": {"name": "Red", "wavelength": "645nm", "resolution": 250},
            "B02": {"name": "NIR", "wavelength": "858nm", "resolution": 250},
            "B03": {"name": "Blue", "wavelength": "469nm", "resolution": 500},
            "B04": {"name": "Green", "wavelength": "555nm", "resolution": 500},
            "B06": {"name": "SWIR1", "wavelength": "1640nm", "resolution": 500},
        },
    },
}


def get_satellite_info(satellite: SatelliteSource) -> dict:
    """Get satellite configuration information"""
    config = SATELLITE_CONFIGS.get(satellite, SATELLITE_CONFIGS[SatelliteSource.SENTINEL2])
    return {
        "id": satellite.value,
        "name": config["name"],
        "name_ar": config["name_ar"],
        "operator": config["operator"],
        "revisit_days": config["revisit_days"],
        "resolution_m": config["resolution_m"],
        "bands_count": len(config["bands"]),
    }


def list_all_satellites() -> list[dict]:
    """List all available satellites"""
    return [get_satellite_info(sat) for sat in SatelliteSource]


def simulate_imagery(
    field_id: str,
    satellite: SatelliteSource = SatelliteSource.SENTINEL2,
    cloud_cover_max: float = 20.0,
) -> SatelliteImagery:
    """
    Simulate satellite imagery acquisition

    In production, this would call SentinelHub, Google Earth Engine,
    or other satellite data providers.

    Args:
        field_id: Field identifier
        satellite: Satellite source
        cloud_cover_max: Maximum acceptable cloud cover

    Returns:
        SatelliteImagery with simulated band values
    """
    import uuid

    config = SATELLITE_CONFIGS[satellite]

    # Generate realistic band reflectance values
    band_values = {
        "blue": random.uniform(0.02, 0.08),
        "green": random.uniform(0.03, 0.12),
        "red": random.uniform(0.02, 0.15),
        "nir": random.uniform(0.15, 0.55),
        "nir narrow": random.uniform(0.15, 0.50),
        "swir1": random.uniform(0.08, 0.35),
        "swir2": random.uniform(0.05, 0.25),
        "thermal1": random.uniform(0.20, 0.40),
    }

    bands = []
    for band_id, band_info in config["bands"].items():
        band_type = band_info["name"].lower()
        value = band_values.get(band_type, random.uniform(0.05, 0.3))
        bands.append(
            SatelliteBand(
                band_id=band_id,
                name=band_info["name"],
                wavelength_nm=band_info["wavelength"],
                resolution_m=band_info["resolution"],
                value=round(value, 4),
            )
        )

    return SatelliteImagery(
        imagery_id=str(uuid.uuid4()),
        field_id=field_id,
        satellite=satellite,
        acquisition_date=datetime.utcnow(),
        cloud_cover_pct=round(random.uniform(0, cloud_cover_max), 1),
        sun_elevation=round(random.uniform(45, 75), 1),
        bands=bands,
        scene_id=f"{satellite.value.upper()}_{datetime.now().strftime('%Y%m%d')}_{random.randint(1000, 9999)}",
        tile_id=f"T{random.randint(30, 40)}Q{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}",
        processing_level="L2A" if satellite == SatelliteSource.SENTINEL2 else "L2",
    )


def extract_bands(imagery: SatelliteImagery) -> dict[str, float]:
    """
    Extract standardized band values from imagery

    Maps satellite-specific bands to standard names (red, green, blue, nir, swir)

    Args:
        imagery: SatelliteImagery object

    Returns:
        Dictionary with standardized band values
    """
    bands_dict = {b.band_id: b.value for b in imagery.bands}

    if imagery.satellite == SatelliteSource.SENTINEL2:
        return {
            "red": bands_dict.get("B04", 0.1),
            "green": bands_dict.get("B03", 0.1),
            "blue": bands_dict.get("B02", 0.05),
            "nir": bands_dict.get("B08", 0.3),
            "swir1": bands_dict.get("B11", 0.2),
            "swir2": bands_dict.get("B12", 0.15),
        }
    elif imagery.satellite in [SatelliteSource.LANDSAT8, SatelliteSource.LANDSAT9]:
        return {
            "red": bands_dict.get("B4", 0.1),
            "green": bands_dict.get("B3", 0.1),
            "blue": bands_dict.get("B2", 0.05),
            "nir": bands_dict.get("B5", 0.3),
            "swir1": bands_dict.get("B6", 0.2),
            "swir2": bands_dict.get("B7", 0.15),
        }
    else:  # MODIS
        return {
            "red": bands_dict.get("B01", 0.1),
            "green": bands_dict.get("B04", 0.1),
            "blue": bands_dict.get("B03", 0.05),
            "nir": bands_dict.get("B02", 0.3),
            "swir1": bands_dict.get("B06", 0.2),
            "swir2": 0.15,  # Not available at this resolution
        }


def compare_satellites() -> dict:
    """Compare satellite capabilities"""
    return {
        "comparison": [
            {
                "satellite": sat.value,
                "resolution_m": config["resolution_m"],
                "revisit_days": config["revisit_days"],
                "operator": config["operator"],
                "best_for": _get_best_use_case(sat),
            }
            for sat, config in SATELLITE_CONFIGS.items()
        ],
        "recommendation": {
            "high_resolution": SatelliteSource.SENTINEL2.value,
            "frequent_monitoring": SatelliteSource.MODIS.value,
            "thermal_analysis": SatelliteSource.LANDSAT8.value,
        },
    }


def _get_best_use_case(satellite: SatelliteSource) -> str:
    """Get best use case for satellite"""
    use_cases = {
        SatelliteSource.SENTINEL2: "High-resolution field analysis (10m)",
        SatelliteSource.LANDSAT8: "Thermal analysis and historical data",
        SatelliteSource.LANDSAT9: "Latest Landsat data with improved sensors",
        SatelliteSource.MODIS: "Daily monitoring at regional scale",
    }
    return use_cases.get(satellite, "General purpose")
