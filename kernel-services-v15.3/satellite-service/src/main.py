"""
🛰️ SAHOOL Satellite Service v15.3
خدمة الأقمار الصناعية - Sentinel-2, Landsat, MODIS Integration
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
from typing import Optional, List
from enum import Enum
import asyncio
import json
import uuid

app = FastAPI(
    title="SAHOOL Satellite Service | خدمة الأقمار الصناعية",
    version="15.3.0",
    description="Multi-satellite agricultural monitoring - Sentinel-2, Landsat-8/9, MODIS",
)


# =============================================================================
# Enums & Models
# =============================================================================


class SatelliteSource(str, Enum):
    SENTINEL2 = "sentinel-2"
    LANDSAT8 = "landsat-8"
    LANDSAT9 = "landsat-9"
    MODIS = "modis"


class BandType(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    NIR = "nir"  # Near Infrared
    SWIR1 = "swir1"  # Short Wave Infrared 1
    SWIR2 = "swir2"  # Short Wave Infrared 2
    THERMAL = "thermal"


class ImageryRequest(BaseModel):
    field_id: str = Field(..., description="معرف الحقل")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    satellite: SatelliteSource = SatelliteSource.SENTINEL2
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None
    cloud_cover_max: float = Field(default=20.0, ge=0, le=100)


class SatelliteBand(BaseModel):
    band_name: str
    wavelength_nm: str
    resolution_m: int
    value: float


class SatelliteImagery(BaseModel):
    imagery_id: str
    field_id: str
    satellite: SatelliteSource
    acquisition_date: datetime
    cloud_cover_percent: float
    sun_elevation: float
    bands: List[SatelliteBand]
    scene_id: str
    tile_id: str
    processing_level: str


class VegetationIndices(BaseModel):
    ndvi: float = Field(..., description="Normalized Difference Vegetation Index")
    ndwi: float = Field(..., description="Normalized Difference Water Index")
    evi: float = Field(..., description="Enhanced Vegetation Index")
    savi: float = Field(..., description="Soil Adjusted Vegetation Index")
    lai: float = Field(..., description="Leaf Area Index estimate")
    ndmi: float = Field(..., description="Normalized Difference Moisture Index")


class FieldAnalysis(BaseModel):
    field_id: str
    analysis_date: datetime
    satellite: SatelliteSource
    imagery: SatelliteImagery
    indices: VegetationIndices
    health_score: float = Field(..., ge=0, le=100)
    health_status: str
    anomalies: List[str]
    recommendations_ar: List[str]
    recommendations_en: List[str]


# =============================================================================
# Satellite Configuration
# =============================================================================

SATELLITE_CONFIGS = {
    SatelliteSource.SENTINEL2: {
        "name": "Sentinel-2 MSI",
        "operator": "ESA",
        "revisit_days": 5,
        "resolution_m": 10,
        "bands": {
            "B02": {"name": "Blue", "wavelength": "490nm", "resolution": 10},
            "B03": {"name": "Green", "wavelength": "560nm", "resolution": 10},
            "B04": {"name": "Red", "wavelength": "665nm", "resolution": 10},
            "B08": {"name": "NIR", "wavelength": "842nm", "resolution": 10},
            "B11": {"name": "SWIR1", "wavelength": "1610nm", "resolution": 20},
            "B12": {"name": "SWIR2", "wavelength": "2190nm", "resolution": 20},
        },
    },
    SatelliteSource.LANDSAT8: {
        "name": "Landsat-8 OLI/TIRS",
        "operator": "NASA/USGS",
        "revisit_days": 16,
        "resolution_m": 30,
        "bands": {
            "B2": {"name": "Blue", "wavelength": "482nm", "resolution": 30},
            "B3": {"name": "Green", "wavelength": "561nm", "resolution": 30},
            "B4": {"name": "Red", "wavelength": "654nm", "resolution": 30},
            "B5": {"name": "NIR", "wavelength": "865nm", "resolution": 30},
            "B6": {"name": "SWIR1", "wavelength": "1609nm", "resolution": 30},
            "B10": {"name": "Thermal", "wavelength": "10895nm", "resolution": 100},
        },
    },
    SatelliteSource.MODIS: {
        "name": "MODIS Terra/Aqua",
        "operator": "NASA",
        "revisit_days": 1,
        "resolution_m": 250,
        "bands": {
            "B01": {"name": "Red", "wavelength": "645nm", "resolution": 250},
            "B02": {"name": "NIR", "wavelength": "858nm", "resolution": 250},
            "B03": {"name": "Blue", "wavelength": "469nm", "resolution": 500},
            "B04": {"name": "Green", "wavelength": "555nm", "resolution": 500},
        },
    },
}

# Yemen regions monitoring
YEMEN_REGIONS = {
    "sana'a": {"lat": 15.3694, "lon": 44.1910, "name_ar": "صنعاء"},
    "aden": {"lat": 12.7855, "lon": 45.0187, "name_ar": "عدن"},
    "taiz": {"lat": 13.5789, "lon": 44.0219, "name_ar": "تعز"},
    "hodeidah": {"lat": 14.7979, "lon": 42.9540, "name_ar": "الحديدة"},
    "ibb": {"lat": 13.9667, "lon": 44.1667, "name_ar": "إب"},
    "dhamar": {"lat": 14.5500, "lon": 44.4000, "name_ar": "ذمار"},
    "hajjah": {"lat": 15.6917, "lon": 43.6028, "name_ar": "حجة"},
    "lahij": {"lat": 13.0500, "lon": 44.8833, "name_ar": "لحج"},
}


# =============================================================================
# Calculation Functions
# =============================================================================


def calculate_ndvi(nir: float, red: float) -> float:
    """NDVI = (NIR - Red) / (NIR + Red)"""
    if nir + red == 0:
        return 0.0
    return round((nir - red) / (nir + red), 4)


def calculate_ndwi(nir: float, swir: float) -> float:
    """NDWI = (NIR - SWIR) / (NIR + SWIR)"""
    if nir + swir == 0:
        return 0.0
    return round((nir - swir) / (nir + swir), 4)


def calculate_evi(nir: float, red: float, blue: float) -> float:
    """EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)"""
    denominator = nir + 6 * red - 7.5 * blue + 1
    if denominator == 0:
        return 0.0
    return round(2.5 * (nir - red) / denominator, 4)


def calculate_savi(nir: float, red: float, L: float = 0.5) -> float:
    """SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)"""
    if nir + red + L == 0:
        return 0.0
    return round(((nir - red) / (nir + red + L)) * (1 + L), 4)


def calculate_lai(ndvi: float) -> float:
    """Estimate LAI from NDVI using empirical relationship"""
    if ndvi <= 0:
        return 0.0
    # LAI = -ln((0.69 - NDVI) / 0.59) / 0.91
    import math

    try:
        lai = -math.log((0.69 - min(ndvi, 0.68)) / 0.59) / 0.91
        return round(max(0, min(lai, 8)), 2)
    except:
        return 0.0


def calculate_ndmi(nir: float, swir: float) -> float:
    """NDMI = (NIR - SWIR1) / (NIR + SWIR1)"""
    if nir + swir == 0:
        return 0.0
    return round((nir - swir) / (nir + swir), 4)


def assess_vegetation_health(
    indices: VegetationIndices,
) -> tuple[float, str, List[str]]:
    """Assess crop health based on vegetation indices"""
    anomalies = []
    score = 50.0  # Base score

    # NDVI analysis
    if indices.ndvi >= 0.6:
        score += 20
    elif indices.ndvi >= 0.4:
        score += 10
    elif indices.ndvi >= 0.2:
        score += 0
    else:
        score -= 20
        anomalies.append("low_vegetation_cover")

    # Water stress (NDWI)
    if indices.ndwi < -0.2:
        score -= 15
        anomalies.append("water_stress_detected")
    elif indices.ndwi > 0.3:
        score += 10

    # Moisture stress (NDMI)
    if indices.ndmi < 0:
        score -= 10
        anomalies.append("moisture_deficit")

    # EVI analysis
    if indices.evi >= 0.4:
        score += 10
    elif indices.evi < 0.2:
        score -= 10
        anomalies.append("poor_canopy_structure")

    # LAI analysis
    if indices.lai >= 3:
        score += 10
    elif indices.lai < 1:
        score -= 5
        anomalies.append("sparse_leaf_coverage")

    score = max(0, min(100, score))

    if score >= 80:
        status = "ممتاز | Excellent"
    elif score >= 60:
        status = "جيد | Good"
    elif score >= 40:
        status = "متوسط | Fair"
    elif score >= 20:
        status = "ضعيف | Poor"
    else:
        status = "حرج | Critical"

    return score, status, anomalies


def generate_recommendations(
    indices: VegetationIndices, anomalies: List[str]
) -> tuple[List[str], List[str]]:
    """Generate bilingual recommendations based on analysis"""
    recommendations_ar = []
    recommendations_en = []

    if "low_vegetation_cover" in anomalies:
        recommendations_ar.append(
            "🌱 الغطاء النباتي منخفض - تحقق من صحة المحصول أو أعد الزراعة"
        )
        recommendations_en.append(
            "🌱 Low vegetation cover - check crop health or consider replanting"
        )

    if "water_stress_detected" in anomalies:
        recommendations_ar.append("💧 إجهاد مائي - زيادة الري فوراً")
        recommendations_en.append(
            "💧 Water stress detected - increase irrigation immediately"
        )

    if "moisture_deficit" in anomalies:
        recommendations_ar.append("🌡️ نقص الرطوبة - ري تكميلي مطلوب")
        recommendations_en.append("🌡️ Moisture deficit - supplemental irrigation needed")

    if "poor_canopy_structure" in anomalies:
        recommendations_ar.append("🍃 بنية المظلة ضعيفة - تحقق من التسميد والآفات")
        recommendations_en.append(
            "🍃 Poor canopy structure - check fertilization and pests"
        )

    if "sparse_leaf_coverage" in anomalies:
        recommendations_ar.append(
            "🌿 تغطية الأوراق متناثرة - قد يحتاج المحصول تسميد نيتروجيني"
        )
        recommendations_en.append(
            "🌿 Sparse leaf coverage - crop may need nitrogen fertilization"
        )

    if not anomalies:
        recommendations_ar.append(
            "✅ المحصول في حالة صحية جيدة - استمر في الممارسات الحالية"
        )
        recommendations_en.append("✅ Crop is healthy - continue current practices")

    return recommendations_ar, recommendations_en


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "satellite-service",
        "version": "15.3.0",
        "satellites": list(SATELLITE_CONFIGS.keys()),
    }


@app.get("/v1/satellites", response_model=dict)
def list_satellites():
    """قائمة الأقمار الصناعية المتاحة"""
    return {
        "satellites": [
            {
                "id": sat.value,
                "name": config["name"],
                "operator": config["operator"],
                "revisit_days": config["revisit_days"],
                "resolution_m": config["resolution_m"],
                "bands_count": len(config["bands"]),
            }
            for sat, config in SATELLITE_CONFIGS.items()
        ]
    }


@app.get("/v1/regions", response_model=dict)
def list_monitored_regions():
    """المناطق المراقبة في اليمن"""
    return {
        "regions": [
            {
                "id": region_id,
                "name_ar": data["name_ar"],
                "latitude": data["lat"],
                "longitude": data["lon"],
            }
            for region_id, data in YEMEN_REGIONS.items()
        ]
    }


@app.post("/v1/imagery/request", response_model=SatelliteImagery)
async def request_imagery(request: ImageryRequest):
    """طلب صور الأقمار الصناعية لحقل معين"""

    config = SATELLITE_CONFIGS[request.satellite]

    # Simulate satellite imagery acquisition
    import random

    # Generate realistic band values (reflectance 0-1)
    band_values = {
        "blue": random.uniform(0.02, 0.08),
        "green": random.uniform(0.03, 0.12),
        "red": random.uniform(0.02, 0.15),
        "nir": random.uniform(0.15, 0.55),
        "swir1": random.uniform(0.08, 0.35),
        "swir2": random.uniform(0.05, 0.25),
    }

    bands = []
    for band_id, band_info in config["bands"].items():
        band_type = band_info["name"].lower()
        value = band_values.get(band_type, random.uniform(0.05, 0.3))
        bands.append(
            SatelliteBand(
                band_name=band_id,
                wavelength_nm=band_info["wavelength"],
                resolution_m=band_info["resolution"],
                value=round(value, 4),
            )
        )

    return SatelliteImagery(
        imagery_id=str(uuid.uuid4()),
        field_id=request.field_id,
        satellite=request.satellite,
        acquisition_date=datetime.utcnow(),
        cloud_cover_percent=random.uniform(0, request.cloud_cover_max),
        sun_elevation=random.uniform(45, 75),
        bands=bands,
        scene_id=f"{request.satellite.value.upper()}_{datetime.now().strftime('%Y%m%d')}_{random.randint(1000,9999)}",
        tile_id=f"T{random.randint(30,40)}Q{chr(random.randint(65,90))}{chr(random.randint(65,90))}",
        processing_level=(
            "L2A" if request.satellite == SatelliteSource.SENTINEL2 else "L2"
        ),
    )


@app.post("/v1/analyze", response_model=FieldAnalysis)
async def analyze_field(request: ImageryRequest):
    """تحليل شامل للحقل باستخدام بيانات الأقمار الصناعية"""

    # Get imagery first
    imagery = await request_imagery(request)

    # Extract band values for calculations
    bands_dict = {b.band_name: b.value for b in imagery.bands}

    # Map to standard names based on satellite
    if request.satellite == SatelliteSource.SENTINEL2:
        red = bands_dict.get("B04", 0.1)
        green = bands_dict.get("B03", 0.1)
        blue = bands_dict.get("B02", 0.05)
        nir = bands_dict.get("B08", 0.3)
        swir1 = bands_dict.get("B11", 0.2)
    elif request.satellite in [SatelliteSource.LANDSAT8, SatelliteSource.LANDSAT9]:
        red = bands_dict.get("B4", 0.1)
        green = bands_dict.get("B3", 0.1)
        blue = bands_dict.get("B2", 0.05)
        nir = bands_dict.get("B5", 0.3)
        swir1 = bands_dict.get("B6", 0.2)
    else:  # MODIS
        red = bands_dict.get("B01", 0.1)
        green = bands_dict.get("B04", 0.1)
        blue = bands_dict.get("B03", 0.05)
        nir = bands_dict.get("B02", 0.3)
        swir1 = 0.2  # MODIS doesn't have SWIR at this resolution

    # Calculate vegetation indices
    indices = VegetationIndices(
        ndvi=calculate_ndvi(nir, red),
        ndwi=calculate_ndwi(nir, swir1),
        evi=calculate_evi(nir, red, blue),
        savi=calculate_savi(nir, red),
        lai=calculate_lai(calculate_ndvi(nir, red)),
        ndmi=calculate_ndmi(nir, swir1),
    )

    # Assess health
    health_score, health_status, anomalies = assess_vegetation_health(indices)

    # Generate recommendations
    recommendations_ar, recommendations_en = generate_recommendations(
        indices, anomalies
    )

    return FieldAnalysis(
        field_id=request.field_id,
        analysis_date=datetime.utcnow(),
        satellite=request.satellite,
        imagery=imagery,
        indices=indices,
        health_score=health_score,
        health_status=health_status,
        anomalies=anomalies,
        recommendations_ar=recommendations_ar,
        recommendations_en=recommendations_en,
    )


@app.get("/v1/timeseries/{field_id}")
async def get_timeseries(
    field_id: str,
    days: int = Query(default=30, ge=7, le=365),
    satellite: SatelliteSource = SatelliteSource.SENTINEL2,
):
    """الحصول على سلسلة زمنية للمؤشرات النباتية"""

    import random

    # Generate time series data
    timeseries = []
    base_ndvi = random.uniform(0.3, 0.5)

    for i in range(0, days, SATELLITE_CONFIGS[satellite]["revisit_days"]):
        date_point = datetime.utcnow() - timedelta(days=days - i)
        # Add realistic variation
        ndvi = base_ndvi + random.uniform(-0.1, 0.15) + (i / days) * 0.2
        ndvi = max(0, min(1, ndvi))

        timeseries.append(
            {
                "date": date_point.isoformat(),
                "ndvi": round(ndvi, 4),
                "ndwi": round(random.uniform(-0.2, 0.4), 4),
                "evi": round(ndvi * 0.8, 4),
                "cloud_cover": round(random.uniform(0, 30), 1),
            }
        )

    return {
        "field_id": field_id,
        "satellite": satellite.value,
        "period_days": days,
        "data_points": len(timeseries),
        "timeseries": timeseries,
        "trend": (
            "improving"
            if timeseries[-1]["ndvi"] > timeseries[0]["ndvi"]
            else "declining"
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)
