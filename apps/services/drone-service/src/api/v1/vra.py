"""
VRA (Variable Rate Application) endpoints - نقاط نهاية التطبيق بالمعدل المتغير
Integrates with shared.drone_integration.vra for prescription map generation.
"""

from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

# Unified error handling
try:
    from shared.errors_py import NotFoundException
except ImportError:

    class NotFoundException(HTTPException):  # type: ignore[no-redef]
        """Fallback when shared.errors_py is unavailable."""

        def __init__(self, message: str = "", message_ar: str | None = None, resource_type: str | None = None, **_kw):
            detail = {"error": message}
            if message_ar:
                detail["error_ar"] = message_ar
            if resource_type:
                detail["resource_type"] = resource_type
            super().__init__(status_code=404, detail=detail)


# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    class User:  # type: ignore[no-redef]
        def __init__(self, **kw):
            self.id = kw.get("id", "anonymous")
            self.tenant_id = kw.get("tenant_id", "default")

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return User(id="anonymous", tenant_id="default")


logger = structlog.get_logger()


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
    ndvi_grid: list[list[float]]
    bounds: BoundsInput
    base_rate_l_ha: float = 10.0
    name: str = "NDVI Prescription"
    name_ar: str = "وصفة NDVI"


class SpotSprayRequest(BaseModel):
    field_id: str
    detection_points: list[dict]
    boundary: list[Coordinate]
    detection_type: str = "weed"
    base_rate_l_ha: float = 5.0
    name: str = "Spot Spray Map"
    name_ar: str = "خريطة الرش النقطي"


def _get_tenant_id(user) -> str:
    return getattr(user, "tenant_id", "default")


def _raise_not_found():
    """Raise NotFoundException for missing prescriptions."""
    raise NotFoundException(
        "Prescription not found",
        "الوصفة غير موجودة",
        "prescription",
    )


@router.post("/prescription/ndvi", status_code=201)
async def create_ndvi_prescription(
    request: NDVIPrescriptionRequest,
    req: Request,
    user=Depends(get_current_user),
):
    """Create NDVI-based prescription map - إنشاء خريطة وصفة مبنية على NDVI"""
    try:
        from shared.drone_integration import create_ndvi_prescription
        from shared.drone_integration.models import BoundingBox
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail={"error": "VRA module not available", "error_ar": "وحدة التطبيق المتغير غير متوفرة"},
        )

    tenant_id = _get_tenant_id(user)
    bounds = BoundingBox(
        min_lat=request.bounds.min_lat,
        max_lat=request.bounds.max_lat,
        min_lng=request.bounds.min_lng,
        max_lng=request.bounds.max_lng,
    )
    prescription = create_ndvi_prescription(
        field_id=request.field_id,
        tenant_id=tenant_id,
        ndvi_grid=request.ndvi_grid,
        bounds=bounds,
        base_rate_l_ha=request.base_rate_l_ha,
        name=request.name,
        name_ar=request.name_ar,
    )

    zones_summary = []
    for z in prescription.zones or []:
        zones_summary.append(
            {
                "zone_type": z.zone_type.value if z.zone_type else None,
                "area_ha": z.area_ha,
                "rate_l_ha": z.rate_l_ha,
                "label_en": z.label_en,
                "label_ar": z.label_ar,
            }
        )

    result = {
        "id": prescription.id,
        "field_id": prescription.field_id,
        "tenant_id": tenant_id,
        "name": prescription.name,
        "name_ar": prescription.name_ar,
        "zones_count": len(prescription.zones),
        "zones": zones_summary,
        "total_area_ha": getattr(prescription, "total_area_ha", 0),
        "avg_rate_l_ha": getattr(prescription, "avg_rate_l_ha", 0),
        "total_volume_l": getattr(prescription, "total_volume_l", 0),
        "created_at": datetime.now(UTC).isoformat(),
    }
    _prescriptions[prescription.id] = result

    try:
        from src.events import VRA_PRESCRIPTION_CREATED, publish_drone_event

        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(
            nc,
            VRA_PRESCRIPTION_CREATED,
            tenant_id,
            prescription_id=prescription.id,
            field_id=request.field_id,
            zones_count=len(prescription.zones),
        )
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info(
        "ndvi_prescription_created", prescription_id=prescription.id, field_id=request.field_id, tenant_id=tenant_id
    )
    return result


@router.post("/prescription/spot-spray", status_code=201)
async def create_spot_spray(
    request: SpotSprayRequest,
    req: Request,
    user=Depends(get_current_user),
):
    """Create spot spray map from detection points - إنشاء خريطة رش نقطي من نقاط الكشف"""
    try:
        from shared.drone_integration import Coordinate as DCoord
        from shared.drone_integration import create_spot_spray_map
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail={"error": "VRA module not available", "error_ar": "وحدة التطبيق المتغير غير متوفرة"},
        )

    tenant_id = _get_tenant_id(user)
    boundary = [DCoord(lat=c.lat, lng=c.lng) for c in request.boundary]
    prescription = create_spot_spray_map(
        field_id=request.field_id,
        tenant_id=tenant_id,
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
        "tenant_id": tenant_id,
        "name": prescription.name,
        "name_ar": prescription.name_ar,
        "detection_type": request.detection_type,
        "detection_points_count": len(request.detection_points),
        "zones_count": len(prescription.zones) if prescription.zones else 0,
        "total_volume_l": getattr(prescription, "total_volume_l", 0),
        "created_at": datetime.now(UTC).isoformat(),
    }
    _prescriptions[prescription.id] = result

    try:
        from src.events import VRA_SPOT_SPRAY_CREATED, publish_drone_event

        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(
            nc,
            VRA_SPOT_SPRAY_CREATED,
            tenant_id,
            prescription_id=prescription.id,
            field_id=request.field_id,
            detection_type=request.detection_type,
        )
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info(
        "spot_spray_map_created",
        prescription_id=prescription.id,
        detection_type=request.detection_type,
        tenant_id=tenant_id,
    )
    return result


@router.get("/prescriptions")
async def list_prescriptions(
    field_id: str | None = None,
    user=Depends(get_current_user),
):
    """List prescription maps - قائمة خرائط الوصفات"""
    tenant_id = _get_tenant_id(user)
    results = [p for p in _prescriptions.values() if p.get("tenant_id") == tenant_id]
    if field_id:
        results = [p for p in results if p.get("field_id") == field_id]
    return {"prescriptions": results, "count": len(results)}


@router.get("/prescriptions/{prescription_id}")
async def get_prescription(prescription_id: str, user=Depends(get_current_user)):
    """Get prescription map details - تفاصيل خريطة الوصفة"""
    tenant_id = _get_tenant_id(user)
    if prescription_id not in _prescriptions or _prescriptions[prescription_id].get("tenant_id") != tenant_id:
        _raise_not_found()
    return _prescriptions[prescription_id]
