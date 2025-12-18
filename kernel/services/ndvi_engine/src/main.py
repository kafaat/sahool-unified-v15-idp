"""
SAHOOL NDVI Engine - Main API Service
Remote sensing NDVI computation and analysis
Port: 8097

Enhanced with multi-satellite support from satellite-service v15.3
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .compute import (
    analyze_ndvi_zones,
    calculate_vegetation_indices,
    classify_ndvi_health,
    compute_from_sentinel,
    compute_mock,
    detect_anomalies,
)
from .events import get_publisher
from .satellites import (
    SatelliteSource,
    compare_satellites,
    extract_bands,
    list_all_satellites,
    simulate_imagery,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🛰️ Starting NDVI Engine Service...")
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        print("✅ NDVI Engine ready on port 8097")
    except Exception as e:
        print(f"⚠️ NATS connection failed: {e}")
        app.state.publisher = None
    yield
    if app.state.publisher:
        await app.state.publisher.close()
    print("👋 NDVI Engine shutting down")


app = FastAPI(
    title="SAHOOL NDVI Engine",
    description="Remote sensing NDVI computation and vegetation analysis",
    version="15.3.3",
    lifespan=lifespan,
)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "ndvi_engine", "version": "15.3.3"}


# ============== Request Models ==============


class NdviComputeRequest(BaseModel):
    tenant_id: str
    field_id: str
    correlation_id: Optional[str] = None
    use_sentinel: bool = False
    geometry: Optional[dict] = None


class NdviZonesRequest(BaseModel):
    tenant_id: str
    field_id: str


class IndicesRequest(BaseModel):
    red: float = Field(ge=0, le=1)
    nir: float = Field(ge=0, le=1)
    blue: Optional[float] = Field(default=None, ge=0, le=1)
    green: Optional[float] = Field(default=None, ge=0, le=1)
    swir: Optional[float] = Field(default=None, ge=0, le=1)


class AnomalyRequest(BaseModel):
    tenant_id: str
    field_id: str
    current_ndvi: float = Field(ge=-1, le=1)
    historical_mean: float = Field(ge=-1, le=1)
    historical_std: float = Field(ge=0)
    correlation_id: Optional[str] = None


# ============== NDVI Endpoints ==============


@app.post("/ndvi/compute")
async def compute_ndvi(req: NdviComputeRequest):
    """
    Compute NDVI for a field

    Supports mock data or Sentinel-2 imagery
    """
    if req.use_sentinel and req.geometry:
        result = compute_from_sentinel(req.field_id, req.geometry)
    else:
        result = compute_mock(req.field_id)

    # Get health classification
    health_en, health_ar = classify_ndvi_health(result.ndvi_mean)

    # Publish event
    event_id = None
    if app.state.publisher:
        event_id = await app.state.publisher.publish_ndvi_computed(
            tenant_id=req.tenant_id,
            field_id=req.field_id,
            ndvi_mean=result.ndvi_mean,
            ndvi_trend_7d=result.ndvi_trend_7d,
            scene_date=result.scene_date,
            correlation_id=req.correlation_id,
            ndvi_min=result.ndvi_min,
            ndvi_max=result.ndvi_max,
            data_source=result.data_source,
        )

    return {
        "field_id": result.field_id,
        "ndvi": {
            "mean": result.ndvi_mean,
            "min": result.ndvi_min,
            "max": result.ndvi_max,
            "std": result.ndvi_std,
        },
        "trends": {
            "trend_7d": result.ndvi_trend_7d,
            "trend_30d": result.ndvi_trend_30d,
        },
        "health": {
            "status_en": health_en,
            "status_ar": health_ar,
        },
        "metadata": {
            "scene_date": result.scene_date,
            "cloud_cover_pct": result.cloud_cover_pct,
            "data_source": result.data_source,
            "quality_score": result.quality_score,
        },
        "event_id": event_id,
        "published": event_id is not None,
    }


@app.post("/ndvi/zones")
async def get_ndvi_zones(req: NdviZonesRequest):
    """Analyze NDVI zones within a field"""
    zones = analyze_ndvi_zones(req.field_id)

    return {
        "field_id": req.field_id,
        "zones": [
            {
                "zone_id": z.zone_id,
                "name_ar": z.zone_name_ar,
                "name_en": z.zone_name_en,
                "ndvi_mean": z.ndvi_mean,
                "area_pct": z.area_pct,
                "health_status": z.health_status,
            }
            for z in zones
        ],
        "count": len(zones),
    }


@app.post("/ndvi/indices")
def calculate_indices(req: IndicesRequest):
    """Calculate multiple vegetation indices from band values"""
    indices = calculate_vegetation_indices(
        red=req.red,
        nir=req.nir,
        blue=req.blue,
        green=req.green,
        swir=req.swir,
    )

    return {
        "indices": indices,
        "input": {
            "red": req.red,
            "nir": req.nir,
            "blue": req.blue,
            "green": req.green,
            "swir": req.swir,
        },
    }


@app.post("/ndvi/anomaly")
async def check_anomaly(req: AnomalyRequest):
    """Check for NDVI anomalies"""
    anomaly = detect_anomalies(
        current_ndvi=req.current_ndvi,
        historical_mean=req.historical_mean,
        historical_std=req.historical_std,
    )

    # Publish anomaly event if detected
    event_id = None
    if anomaly and app.state.publisher:
        event_id = await app.state.publisher.publish_ndvi_anomaly(
            tenant_id=req.tenant_id,
            field_id=req.field_id,
            anomaly_type=anomaly["type"],
            severity=anomaly["severity"],
            z_score=anomaly["z_score"],
            current_ndvi=req.current_ndvi,
            historical_mean=req.historical_mean,
            correlation_id=req.correlation_id,
        )

    return {
        "field_id": req.field_id,
        "anomaly_detected": anomaly is not None,
        "anomaly": anomaly,
        "event_id": event_id,
    }


@app.get("/ndvi/health/{ndvi_value}")
def get_health_status(ndvi_value: float):
    """Get health classification for NDVI value"""
    if not -1 <= ndvi_value <= 1:
        raise HTTPException(status_code=400, detail="NDVI must be between -1 and 1")

    health_en, health_ar = classify_ndvi_health(ndvi_value)

    return {
        "ndvi": ndvi_value,
        "health_en": health_en,
        "health_ar": health_ar,
    }


# ============== Satellite Endpoints (from v15.3) ==============


class SatelliteImageryRequest(BaseModel):
    tenant_id: str
    field_id: str
    satellite: str = "sentinel-2"
    cloud_cover_max: float = Field(default=20.0, ge=0, le=100)
    correlation_id: Optional[str] = None


@app.get("/satellites")
def get_satellites():
    """
    List available satellite sources

    Returns information about supported satellites:
    - Sentinel-2: High resolution (10m), 5-day revisit
    - Landsat-8/9: Medium resolution (30m), 16-day revisit
    - MODIS: Daily coverage, lower resolution (250m)
    """
    return {
        "satellites": list_all_satellites(),
        "comparison": compare_satellites(),
    }


@app.get("/satellites/{satellite_id}")
def get_satellite_info(satellite_id: str):
    """Get detailed information about a specific satellite"""
    try:
        satellite = SatelliteSource(satellite_id.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown satellite: {satellite_id}. Use: sentinel-2, landsat-8, landsat-9, modis",
        )

    from .satellites import get_satellite_info as get_info

    return get_info(satellite)


@app.post("/satellites/imagery")
async def request_satellite_imagery(req: SatelliteImageryRequest):
    """
    Request satellite imagery for a field

    Simulates satellite imagery acquisition.
    In production, integrates with SentinelHub, Google Earth Engine, etc.

    Returns:
        Band values, metadata, and scene information
    """
    try:
        satellite = SatelliteSource(req.satellite.lower())
    except ValueError:
        satellite = SatelliteSource.SENTINEL2

    imagery = simulate_imagery(
        field_id=req.field_id,
        satellite=satellite,
        cloud_cover_max=req.cloud_cover_max,
    )

    # Extract standardized bands
    bands = extract_bands(imagery)

    # Calculate all indices
    indices = calculate_vegetation_indices(
        red=bands["red"],
        nir=bands["nir"],
        blue=bands.get("blue"),
        green=bands.get("green"),
        swir=bands.get("swir1"),
    )

    # Get health status
    health_en, health_ar = classify_ndvi_health(indices.get("ndvi", 0))

    return {
        "field_id": req.field_id,
        "satellite": {
            "source": imagery.satellite.value,
            "scene_id": imagery.scene_id,
            "tile_id": imagery.tile_id,
            "acquisition_date": imagery.acquisition_date.isoformat(),
            "cloud_cover_pct": imagery.cloud_cover_pct,
            "processing_level": imagery.processing_level,
        },
        "bands": {
            b.band_id: {
                "name": b.name,
                "wavelength": b.wavelength_nm,
                "resolution_m": b.resolution_m,
                "value": b.value,
            }
            for b in imagery.bands
        },
        "indices": indices,
        "health": {
            "status_en": health_en,
            "status_ar": health_ar,
        },
    }


@app.post("/satellites/analyze")
async def analyze_with_satellite(req: SatelliteImageryRequest):
    """
    Full field analysis using satellite data

    Combines imagery acquisition with comprehensive vegetation analysis.
    Returns health score, anomalies, and recommendations.
    """
    try:
        satellite = SatelliteSource(req.satellite.lower())
    except ValueError:
        satellite = SatelliteSource.SENTINEL2

    imagery = simulate_imagery(
        field_id=req.field_id,
        satellite=satellite,
        cloud_cover_max=req.cloud_cover_max,
    )

    bands = extract_bands(imagery)
    indices = calculate_vegetation_indices(
        red=bands["red"],
        nir=bands["nir"],
        blue=bands.get("blue"),
        green=bands.get("green"),
        swir=bands.get("swir1"),
    )

    # Calculate health score (0-100)
    ndvi = indices.get("ndvi", 0)
    lai = indices.get("lai", 0)
    ndmi = indices.get("ndmi", 0)

    health_score = 50.0
    anomalies = []

    # NDVI contribution
    if ndvi >= 0.6:
        health_score += 20
    elif ndvi >= 0.4:
        health_score += 10
    elif ndvi < 0.2:
        health_score -= 20
        anomalies.append("low_vegetation_cover")

    # LAI contribution
    if lai >= 3:
        health_score += 10
    elif lai < 1:
        health_score -= 5
        anomalies.append("sparse_leaf_coverage")

    # Moisture contribution
    if ndmi and ndmi < 0:
        health_score -= 10
        anomalies.append("moisture_deficit")

    health_score = max(0, min(100, health_score))

    # Health status
    if health_score >= 80:
        status = "excellent"
        status_ar = "ممتاز"
    elif health_score >= 60:
        status = "good"
        status_ar = "جيد"
    elif health_score >= 40:
        status = "fair"
        status_ar = "متوسط"
    elif health_score >= 20:
        status = "poor"
        status_ar = "ضعيف"
    else:
        status = "critical"
        status_ar = "حرج"

    # Generate recommendations
    recommendations_ar = []
    recommendations_en = []

    if "low_vegetation_cover" in anomalies:
        recommendations_ar.append("الغطاء النباتي منخفض - تحقق من صحة المحصول")
        recommendations_en.append("Low vegetation - check crop health")

    if "moisture_deficit" in anomalies:
        recommendations_ar.append("نقص الرطوبة - ري تكميلي مطلوب")
        recommendations_en.append("Moisture deficit - irrigation needed")

    if "sparse_leaf_coverage" in anomalies:
        recommendations_ar.append("تغطية الأوراق متناثرة - تحقق من التسميد")
        recommendations_en.append("Sparse leaves - check fertilization")

    if not anomalies:
        recommendations_ar.append("المحصول في حالة صحية جيدة")
        recommendations_en.append("Crop is healthy - continue current practices")

    return {
        "field_id": req.field_id,
        "satellite": imagery.satellite.value,
        "analysis_date": imagery.acquisition_date.isoformat(),
        "indices": indices,
        "health": {
            "score": round(health_score, 1),
            "status": status,
            "status_ar": status_ar,
        },
        "anomalies": anomalies,
        "recommendations_ar": recommendations_ar,
        "recommendations_en": recommendations_en,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8097))
    uvicorn.run(app, host="0.0.0.0", port=port)
