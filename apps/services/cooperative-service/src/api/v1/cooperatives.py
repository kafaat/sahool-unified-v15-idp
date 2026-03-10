"""
Cooperative management API endpoints - نقاط نهاية إدارة التعاونيات
Integrates with shared.cooperatives module.
"""

import json
import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Fallback auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}


# Domain enums - used for request validation
try:
    from shared.cooperatives.models import CooperativeType, MemberRole, ResourceType, RevenueShareMethod
except ImportError:
    CooperativeType = None
    MemberRole = None
    ResourceType = None
    RevenueShareMethod = None

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/cooperatives", tags=["cooperatives"])

# In-memory storage
_cooperatives: dict[str, dict] = {}
_members: dict[str, dict] = {}
_resources: dict[str, dict] = {}
_bookings: dict[str, dict] = {}


# === Helpers ===


def _get_coop_or_404(coop_id: str) -> dict:
    """Get cooperative by ID or raise 404."""
    if coop_id not in _cooperatives:
        raise HTTPException(
            status_code=404, detail={"error": "Cooperative not found", "error_ar": "التعاونية غير موجودة"}
        )
    return _cooperatives[coop_id]


def _members_for_coop(coop_id: str) -> list[dict]:
    """Get all members belonging to a cooperative."""
    return [m for m in _members.values() if m.get("cooperative_id") == coop_id]


def _resources_for_coop(coop_id: str) -> list[dict]:
    """Get all resources belonging to a cooperative."""
    return [r for r in _resources.values() if r.get("cooperative_id") == coop_id]


# === Request Models ===


class CooperativeCreateRequest(BaseModel):
    tenant_id: str
    name: str
    name_ar: str
    type: str = "multi_purpose"
    description: str | None = None
    description_ar: str | None = None
    region: str | None = None


class MemberCreateRequest(BaseModel):
    cooperative_id: str
    farmer_id: str
    name: str
    name_ar: str
    phone: str | None = None
    role: str = "member"
    share_count: int = 1
    land_area_ha: float = 0.0


class ResourceCreateRequest(BaseModel):
    cooperative_id: str
    name: str
    name_ar: str
    type: str = "equipment"
    capacity: float | None = None
    capacity_unit: str | None = None
    model: str | None = None
    hourly_rate: float = 0.0


class BookingCreateRequest(BaseModel):
    resource_id: str
    member_id: str
    purpose: str
    purpose_ar: str | None = None
    start_time: datetime
    duration_hours: float = 4.0


class RevenueDistributionRequest(BaseModel):
    cooperative_id: str
    total_revenue: float
    method: str = "production"
    period_name: str | None = None


# === Cooperative Endpoints ===


@router.post("/", status_code=201)
async def create_cooperative(request: CooperativeCreateRequest, req: Request):
    """Create a new cooperative - إنشاء تعاونية جديدة"""
    coop_id = f"COOP-{uuid.uuid4().hex[:8].upper()}"

    try:
        from shared.cooperatives import Cooperative, CooperativeType

        coop_type = (
            CooperativeType(request.type) if hasattr(CooperativeType, request.type.upper()) else CooperativeType.MULTI_PURPOSE
        )
        coop = Cooperative.create(
            tenant_id=request.tenant_id,
            name=request.name,
            name_ar=request.name_ar,
            type=coop_type,
        )
        coop_id = coop.cooperative_id
    except ImportError:
        logger.warning("cooperative_create_fallback", error="shared.cooperatives not available")

    coop_data = {
        "id": coop_id,
        "tenant_id": request.tenant_id,
        "name": request.name,
        "name_ar": request.name_ar,
        "type": request.type,
        "description": request.description,
        "description_ar": request.description_ar,
        "region": request.region,
        "status": "active",
        "member_count": 0,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _cooperatives[coop_id] = coop_data

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            "sahool.cooperative.created",
            json.dumps({"cooperative_id": coop_id, "tenant_id": request.tenant_id}).encode(),
        )

    logger.info("cooperative_created", coop_id=coop_id)
    return coop_data


@router.get("/")
async def list_cooperatives(tenant_id: str | None = None):
    """List cooperatives - قائمة التعاونيات"""
    result = list(_cooperatives.values())
    if tenant_id:
        result = [c for c in result if c.get("tenant_id") == tenant_id]
    return {"cooperatives": result, "count": len(result)}


@router.get("/{coop_id}")
async def get_cooperative(coop_id: str):
    """Get cooperative details - تفاصيل التعاونية"""
    coop = _get_coop_or_404(coop_id)
    return {
        **coop,
        "members": _members_for_coop(coop_id),
        "resources": _resources_for_coop(coop_id),
    }


@router.delete("/{coop_id}", status_code=204)
async def delete_cooperative(coop_id: str, _user=Depends(get_current_user)):
    """Delete cooperative - حذف التعاونية"""
    _get_coop_or_404(coop_id)

    # Cascade: remove associated resources, bookings, and members
    resource_ids = {r["id"] for r in _resources_for_coop(coop_id)}
    for bk_id in [k for k, v in _bookings.items() if v.get("resource_id") in resource_ids]:
        del _bookings[bk_id]
    for res_id in resource_ids:
        del _resources[res_id]
    for mem_id in [k for k, v in _members.items() if v.get("cooperative_id") == coop_id]:
        del _members[mem_id]

    del _cooperatives[coop_id]


# === Member Endpoints ===


@router.post("/{coop_id}/members", status_code=201)
async def add_member(coop_id: str, request: MemberCreateRequest, req: Request):
    """Add member to cooperative - إضافة عضو للتعاونية"""
    _get_coop_or_404(coop_id)

    member_id = f"MBR-{uuid.uuid4().hex[:8].upper()}"

    try:
        from shared.cooperatives import CooperativeMember

        member = CooperativeMember.create(
            cooperative_id=coop_id,
            farmer_id=request.farmer_id,
            name=request.name,
            name_ar=request.name_ar,
            phone=request.phone or "",
            share_count=request.share_count,
            land_area_ha=request.land_area_ha,
        )
        member_id = member.member_id
    except ImportError:
        logger.warning("member_create_fallback", error="shared.cooperatives not available")

    member_data = {
        "id": member_id,
        "cooperative_id": coop_id,
        "farmer_id": request.farmer_id,
        "name": request.name,
        "name_ar": request.name_ar,
        "phone": request.phone,
        "role": request.role,
        "share_count": request.share_count,
        "land_area_ha": request.land_area_ha,
        "status": "active",
        "joined_at": datetime.now(UTC).isoformat(),
    }
    _members[member_id] = member_data
    _cooperatives[coop_id]["member_count"] = _cooperatives[coop_id].get("member_count", 0) + 1

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            "sahool.cooperative.member_added", json.dumps({"cooperative_id": coop_id, "member_id": member_id}).encode()
        )

    logger.info("member_added", coop_id=coop_id, member_id=member_id)
    return member_data


@router.get("/{coop_id}/members")
async def list_members(coop_id: str):
    """List cooperative members - قائمة أعضاء التعاونية"""
    _get_coop_or_404(coop_id)
    members = _members_for_coop(coop_id)
    return {"cooperative_id": coop_id, "members": members, "count": len(members)}


@router.delete("/{coop_id}/members/{member_id}", status_code=204)
async def remove_member(coop_id: str, member_id: str, _user=Depends(get_current_user)):
    """Remove member from cooperative - إزالة عضو من التعاونية"""
    if member_id not in _members:
        raise HTTPException(status_code=404, detail={"error": "Member not found", "error_ar": "العضو غير موجود"})
    if _members[member_id].get("cooperative_id") != coop_id:
        raise HTTPException(status_code=404, detail={"error": "Member not found in this cooperative", "error_ar": "العضو غير موجود في هذه التعاونية"})
    del _members[member_id]
    _cooperatives[coop_id]["member_count"] = max(0, _cooperatives[coop_id].get("member_count", 1) - 1)


# === Resource Pool Endpoints ===


@router.post("/{coop_id}/resources", status_code=201)
async def register_resource(coop_id: str, request: ResourceCreateRequest):
    """Register shared resource - تسجيل مورد مشترك"""
    _get_coop_or_404(coop_id)

    resource_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
    resource_data = {
        "id": resource_id,
        "cooperative_id": coop_id,
        "name": request.name,
        "name_ar": request.name_ar,
        "type": request.type,
        "capacity": request.capacity,
        "capacity_unit": request.capacity_unit,
        "model": request.model,
        "hourly_rate": request.hourly_rate,
        "status": "available",
        "created_at": datetime.now(UTC).isoformat(),
    }
    _resources[resource_id] = resource_data
    logger.info("resource_registered", coop_id=coop_id, resource_id=resource_id)
    return resource_data


@router.get("/{coop_id}/resources")
async def list_resources(coop_id: str):
    """List cooperative resources - قائمة موارد التعاونية"""
    _get_coop_or_404(coop_id)
    resources = _resources_for_coop(coop_id)
    return {"cooperative_id": coop_id, "resources": resources, "count": len(resources)}


@router.post("/{coop_id}/resources/{resource_id}/book", status_code=201)
async def book_resource(coop_id: str, resource_id: str, request: BookingCreateRequest):
    """Book a shared resource - حجز مورد مشترك"""
    if resource_id not in _resources:
        raise HTTPException(status_code=404, detail={"error": "Resource not found", "error_ar": "المورد غير موجود"})
    if request.member_id not in _members:
        raise HTTPException(status_code=404, detail={"error": "Member not found", "error_ar": "العضو غير موجود"})

    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
    booking_data = {
        "id": booking_id,
        "resource_id": resource_id,
        "member_id": request.member_id,
        "purpose": request.purpose,
        "purpose_ar": request.purpose_ar,
        "start_time": request.start_time.isoformat(),
        "duration_hours": request.duration_hours,
        "status": "confirmed",
        "cost": _resources[resource_id].get("hourly_rate", 0) * request.duration_hours,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _bookings[booking_id] = booking_data
    logger.info("resource_booked", resource_id=resource_id, booking_id=booking_id)
    return booking_data


# === Revenue Distribution Endpoints ===


@router.post("/{coop_id}/revenue/distribute")
async def distribute_revenue(coop_id: str, request: RevenueDistributionRequest):
    """Distribute revenue among members - توزيع الإيرادات بين الأعضاء"""
    _get_coop_or_404(coop_id)

    members = _members_for_coop(coop_id)
    if not members:
        raise HTTPException(
            status_code=400, detail={"error": "No members in cooperative", "error_ar": "لا يوجد أعضاء في التعاونية"}
        )

    if request.method == "land_area":
        shares_data = {m["id"]: m.get("land_area_ha", 1.0) for m in members}
    elif request.method == "contribution":
        shares_data = {m["id"]: float(m.get("share_count", 1)) for m in members}
    else:
        shares_data = {m["id"]: 1.0 for m in members}

    total_shares = sum(shares_data.values()) or 1.0
    distributions = []
    for m in members:
        share_ratio = shares_data.get(m["id"], 1.0) / total_shares
        amount = round(request.total_revenue * share_ratio, 2)
        distributions.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "member_name_ar": m["name_ar"],
                "share_ratio": round(share_ratio, 4),
                "amount": amount,
            }
        )

    return {
        "cooperative_id": coop_id,
        "total_revenue": request.total_revenue,
        "method": request.method,
        "period": request.period_name,
        "distributions": distributions,
        "distributed_at": datetime.now(UTC).isoformat(),
    }


@router.get("/{coop_id}/stats")
async def get_cooperative_stats(coop_id: str):
    """Get cooperative statistics - إحصائيات التعاونية"""
    coop = _get_coop_or_404(coop_id)

    members = _members_for_coop(coop_id)
    resources = _resources_for_coop(coop_id)
    resource_ids = {r["id"] for r in resources}
    coop_bookings = [b for b in _bookings.values() if b.get("resource_id") in resource_ids]

    return {
        "cooperative_id": coop_id,
        "name": coop["name"],
        "name_ar": coop["name_ar"],
        "member_count": len(members),
        "resource_count": len(resources),
        "total_land_area_ha": sum(m.get("land_area_ha", 0) for m in members),
        "total_shares": sum(m.get("share_count", 0) for m in members),
        "active_bookings": len([b for b in coop_bookings if b.get("status") == "confirmed"]),
        "total_booking_revenue": sum(b.get("cost", 0) for b in coop_bookings),
    }
