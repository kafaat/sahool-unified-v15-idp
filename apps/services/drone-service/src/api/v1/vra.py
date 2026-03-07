"""
VRA (Variable Rate Application) endpoints - نقاط نهاية التطبيق بالمعدل المتغير
Integrates with shared.drone_integration.vra for prescription map generation.
"""

from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
logger = structlog.get_logger()

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    _bearer_scheme = HTTPBearer(auto_error=False)
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}

router = APIRouter(prefix="/api/v1/vra", tags=["vra"])

_prescriptions: dict[str, dict] = {}


class Coordinate(BaseModel):
    lat: float
    lng: float


class BoundsInput(BaseModel):
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


class NDVIPrescriptionRequest(BaseModel):
    field_id: str
    tenant_id: str
    ndvi_grid: list[list[float]]
    bounds: BoundsInput
    base_rate_l_ha: float = 10.0
    name: str = "NDVI Prescription"
    name_ar: str = "وصفة NDVI"


class SpotSprayRequest(BaseModel):
    field_id: str
    tenant_id: str
    detection_points: list[dict]
    boundary: list[Coordinate]
    detection_type: str = "weed"
    base_rate_l_ha: float = 5.0
    name: str = "Spot Spray Map"
    name_ar: str = "خريطة الرش النقطي"


@router.post("/prescription/ndvi", status_code=201)
async def create_ndvi_prescription(request: NDVIPrescriptionRequest, _user=Depends(get_current_user)):
    """Create NDVI-based prescription map - إنشاء خريطة وصفة مبنية على NDVI"""
    try:
        from shared.drone_integration import create_ndvi_prescription
        from shared.drone_integration.models import BoundingBox

        bounds = BoundingBox(
            min_lat=request.bounds.min_lat,
            max_lat=request.bounds.max_lat,
            min_lng=request.bounds.min_lng,
            max_lng=request.bounds.max_lng,
        )
        prescription = create_ndvi_prescription(
            field_id=request.field_id,
            tenant_id=request.tenant_id,
            ndvi_grid=request.ndvi_grid,
            bounds=bounds,
            base_rate_l_ha=request.base_rate_l_ha,
            name=request.name,
            name_ar=request.name_ar,
        )

        result = {
            "id": prescription.id,
            "field_id": prescription.field_id,
            "name": prescription.name,
            "name_ar": prescription.name_ar,
            "zones_count": len(prescription.zones) if hasattr(prescription, "zones") else 0,
            "created_at": datetime.now(UTC).isoformat(),
        }
        _prescriptions[prescription.id] = result
        logger.info("ndvi_prescription_created", prescription_id=prescription.id, field_id=request.field_id)
        return result
    except ImportError:
        raise HTTPException(status_code=503, detail={"error": "VRA module not available", "error_ar": "وحدة التطبيق المتغير غير متوفرة"})


@router.post("/prescription/spot-spray", status_code=201)
async def create_spot_spray(request: SpotSprayRequest, _user=Depends(get_current_user)):
    """Create spot spray map from detection points - إنشاء خريطة رش نقطي من نقاط الكشف"""
    try:
        from shared.drone_integration import Coordinate as DCoord, create_spot_spray_map

        boundary = [DCoord(lat=c.lat, lng=c.lng) for c in request.boundary]
        prescription = create_spot_spray_map(
            field_id=request.field_id,
            tenant_id=request.tenant_id,
            detection_points=request.detection_points,
            boundary=boundary,
            detection_type=request.detection_type,
            base_rate_l_ha=request.base_rate_l_ha,
            name=request.name,
            name_ar=request.name_ar,
        )

        result = {
            "id": prescription.id,
            "field_id": prescription.field_id,
            "name": prescription.name,
            "name_ar": prescription.name_ar,
            "detection_type": request.detection_type,
            "detection_points_count": len(request.detection_points),
            "zones_count": len(prescription.zones) if hasattr(prescription, "zones") else 0,
            "created_at": datetime.now(UTC).isoformat(),
        }
        _prescriptions[prescription.id] = result
        logger.info("spot_spray_map_created", prescription_id=prescription.id, detection_type=request.detection_type)
        return result
    except ImportError:
        raise HTTPException(status_code=503, detail={"error": "VRA module not available", "error_ar": "وحدة التطبيق المتغير غير متوفرة"})


@router.get("/prescriptions")
async def list_prescriptions(field_id: str | None = None):
    """List prescription maps - قائمة خرائط الوصفات"""
    results = list(_prescriptions.values())
    if field_id:
        results = [p for p in results if p.get("field_id") == field_id]
    return {"prescriptions": results, "count": len(results)}


@router.get("/prescriptions/{prescription_id}")
async def get_prescription(prescription_id: str):
    """Get prescription map details - تفاصيل خريطة الوصفة"""
    if prescription_id not in _prescriptions:
        raise HTTPException(status_code=404, detail={"error": "Prescription not found", "error_ar": "الوصفة غير موجودة"})
    return _prescriptions[prescription_id]
