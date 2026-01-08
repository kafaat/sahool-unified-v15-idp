"""
⚠️ DEPRECATED: This service is deprecated and will be removed in a future release.
Please use 'vegetation-analysis-service' instead.

SAHOOL NDVI Engine - Main API Service
Remote sensing NDVI computation and analysis
Port: 8107

Migration Path:
- Replacement: vegetation-analysis-service (Port 8090)
- Deprecation Date: 2026-01-06
- Sunset Date: 2026-06-01
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, Field

# Import authentication dependencies
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback if auth module not available
    AUTH_AVAILABLE = False
    # Fallback error handling
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    User = None

    def get_current_user():
        """Placeholder when auth not available"""
        return None


from .compute import (
    analyze_ndvi_zones,
    calculate_vegetation_indices,
    classify_ndvi_health,
    compute_from_sentinel,
    compute_mock,
    detect_anomalies,
)
from .events import get_publisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 80)
    print("⚠️  DEPRECATION WARNING")
    print("=" * 80)
    print("This service (ndvi-engine) is DEPRECATED and will be removed in a future release.")
    print("Please migrate to 'vegetation-analysis-service' instead.")
    print("Replacement service: vegetation-analysis-service (Port 8090)")
    print("Deprecation date: 2026-01-06")
    print("Sunset date: 2026-06-01")
    print("=" * 80)

    print("🛰️ Starting NDVI Engine Service...")
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        print("✅ NDVI Engine ready on port 8107")
    except Exception as e:
        print(f"⚠️ NATS connection failed: {e}")
        app.state.publisher = None
    yield
    if app.state.publisher:
        await app.state.publisher.close()
    print("👋 NDVI Engine shutting down")


app = FastAPI(
    title="SAHOOL NDVI Engine (DEPRECATED)",
    description="⚠️ DEPRECATED - Use vegetation-analysis-service instead. Remote sensing NDVI computation and vegetation analysis",
    version="15.3.3",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Add deprecation headers middleware
from fastapi import Request


@app.middleware("http")
async def add_deprecation_header(request: Request, call_next):
    """Add deprecation headers to all responses"""
    response = await call_next(request)
    response.headers["X-API-Deprecated"] = "true"
    response.headers["X-API-Deprecation-Date"] = "2026-01-06"
    response.headers["X-API-Deprecation-Info"] = (
        "This service is deprecated. Use vegetation-analysis-service instead."
    )
    response.headers["X-API-Sunset"] = "2026-06-01"
    response.headers["Link"] = '<http://vegetation-analysis-service:8090>; rel="successor-version"'
    response.headers["Deprecation"] = "true"
    return response


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "ndvi_engine", "version": "15.3.3"}


# ============== Request Models ==============


class NdviComputeRequest(BaseModel):
    tenant_id: str
    field_id: str
    correlation_id: str | None = None
    use_sentinel: bool = False
    geometry: dict | None = None


class NdviZonesRequest(BaseModel):
    tenant_id: str
    field_id: str


class IndicesRequest(BaseModel):
    red: float = Field(ge=0, le=1)
    nir: float = Field(ge=0, le=1)
    blue: float | None = Field(default=None, ge=0, le=1)
    green: float | None = Field(default=None, ge=0, le=1)
    swir: float | None = Field(default=None, ge=0, le=1)


class AnomalyRequest(BaseModel):
    tenant_id: str
    field_id: str
    current_ndvi: float = Field(ge=-1, le=1)
    historical_mean: float = Field(ge=-1, le=1)
    historical_std: float = Field(ge=0)
    correlation_id: str | None = None


# ============== NDVI Endpoints ==============


@app.post("/ndvi/compute")
async def compute_ndvi(
    req: NdviComputeRequest, user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
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
async def get_ndvi_zones(
    req: NdviZonesRequest, user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
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
async def check_anomaly(
    req: AnomalyRequest, user: User = Depends(get_current_user) if AUTH_AVAILABLE else None
):
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
