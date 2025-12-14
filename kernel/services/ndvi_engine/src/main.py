"""
SAHOOL NDVI Engine - Main API Service
Remote sensing NDVI computation and analysis
Port: 8097
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .compute import (
    compute_mock,
    compute_from_sentinel,
    analyze_ndvi_zones,
    classify_ndvi_health,
    calculate_vegetation_indices,
    detect_anomalies,
)
from .events import get_publisher


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


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8097))
    uvicorn.run(app, host="0.0.0.0", port=port)
