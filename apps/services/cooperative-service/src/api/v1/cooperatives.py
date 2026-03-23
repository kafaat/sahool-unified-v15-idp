"""
Cooperative management API endpoints - نقاط نهاية إدارة التعاونيات
Integrates with shared.cooperatives module and PostgreSQL persistence.
"""

import json
import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel

# NATS event subject constants
from shared.events.subjects import (
    SAHOOL_COOPERATIVE_CREATED,
    SAHOOL_COOPERATIVE_MEMBER_ADDED,
    SAHOOL_COOPERATIVE_MEMBER_REMOVED,
    SAHOOL_COOPERATIVE_RESOURCE_BOOKED,
    SAHOOL_COOPERATIVE_REVENUE_DISTRIBUTED,
    SAHOOL_NOTIFICATION_SEND,
)

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    async def get_current_user(  # type: ignore[misc]
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Fallback auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}


logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/cooperatives", tags=["cooperatives"])


# === Tenant Extraction ===


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header."""
    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail={"error": "X-Tenant-Id header is required", "error_ar": "ترويسة معرّف المستأجر مطلوبة"},
        )
    try:
        uuid.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "X-Tenant-Id must be a valid UUID", "error_ar": "معرّف المستأجر يجب أن يكون UUID صالح"},
        )
    return x_tenant_id


# === Database Helpers ===


async def _get_db(request: Request):
    """Get database pool from app state."""
    pool = getattr(request.app.state, "db_pool", None)
    if not pool:
        raise HTTPException(
            status_code=503,
            detail={"error": "Database not available", "error_ar": "قاعدة البيانات غير متوفرة"},
        )
    return pool


async def _get_coop_or_404(pool, coop_id: str, tenant_id: str) -> dict:
    """Get cooperative by ID with mandatory tenant isolation or raise 404."""
    row = await pool.fetchrow(
        "SELECT * FROM cooperatives WHERE id = $1 AND tenant_id = $2",
        uuid.UUID(coop_id),
        uuid.UUID(tenant_id),
    )
    if not row:
        raise HTTPException(
            status_code=404, detail={"error": "Cooperative not found", "error_ar": "التعاونية غير موجودة"}
        )
    return dict(row)


def _row_to_dict(row) -> dict:
    """Convert asyncpg Record to JSON-serializable dict."""
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, uuid.UUID):
            d[k] = str(v)
        elif isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


# === Request Models ===


class CooperativeCreateRequest(BaseModel):
    name: str
    name_ar: str
    type: str = "multi_purpose"
    description: str | None = None
    description_ar: str | None = None
    region: str | None = None


class CooperativeUpdateRequest(BaseModel):
    name: str | None = None
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    region: str | None = None
    status: str | None = None


class MemberCreateRequest(BaseModel):
    farmer_id: str
    name: str
    name_ar: str
    phone: str | None = None
    role: str = "member"
    share_count: int = 1
    land_area_ha: float = 0.0


class ResourceCreateRequest(BaseModel):
    name: str
    name_ar: str
    type: str = "equipment"
    capacity: float | None = None
    capacity_unit: str | None = None
    model: str | None = None
    hourly_rate: float = 0.0


class BookingCreateRequest(BaseModel):
    member_id: str
    purpose: str
    purpose_ar: str | None = None
    start_time: datetime
    duration_hours: float = 4.0


class RevenueDistributionRequest(BaseModel):
    total_revenue: float
    method: str = "production"
    period_name: str | None = None


# === Cooperative Endpoints ===


@router.post("/", status_code=201)
async def create_cooperative(request: CooperativeCreateRequest, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Create a new cooperative - إنشاء تعاونية جديدة"""
    pool = await _get_db(req)

    row = await pool.fetchrow(
        """
        INSERT INTO cooperatives (tenant_id, name, name_ar, type, description, description_ar, region, status, member_count)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'active', 0)
        RETURNING *
        """,
        tenant_id,
        request.name,
        request.name_ar,
        request.type,
        request.description,
        request.description_ar,
        request.region,
    )
    coop_data = _row_to_dict(row)

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            SAHOOL_COOPERATIVE_CREATED,
            json.dumps({"cooperative_id": coop_data["id"], "tenant_id": tenant_id}).encode(),
        )

    logger.info("cooperative_created", coop_id=coop_data["id"])
    return coop_data


@router.get("/")
async def list_cooperatives(req: Request, tenant_id: str = Depends(get_tenant_id)):
    """List cooperatives - قائمة التعاونيات"""
    pool = await _get_db(req)

    rows = await pool.fetch("SELECT * FROM cooperatives WHERE tenant_id = $1 ORDER BY created_at DESC", tenant_id)

    result = [_row_to_dict(r) for r in rows]
    return {"cooperatives": result, "count": len(result)}


@router.get("/{coop_id}")
async def get_cooperative(coop_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Get cooperative details - تفاصيل التعاونية"""
    pool = await _get_db(req)
    coop = _row_to_dict(await _get_coop_or_404(pool, coop_id, tenant_id))

    members = await pool.fetch(
        "SELECT * FROM cooperative_members WHERE cooperative_id = $1 ORDER BY joined_at", uuid.UUID(coop_id)
    )
    resources = await pool.fetch(
        "SELECT * FROM shared_resources WHERE cooperative_id = $1 ORDER BY created_at", uuid.UUID(coop_id)
    )

    return {
        **coop,
        "members": [_row_to_dict(m) for m in members],
        "resources": [_row_to_dict(r) for r in resources],
    }


@router.put("/{coop_id}")
async def update_cooperative(
    coop_id: str, request: CooperativeUpdateRequest, req: Request, tenant_id: str = Depends(get_tenant_id), _user=Depends(get_current_user)
):
    """Update cooperative - تحديث التعاونية"""
    pool = await _get_db(req)
    await _get_coop_or_404(pool, coop_id, tenant_id)

    ALLOWED_COLUMNS = {"name", "name_ar", "description", "description_ar", "region", "status"}
    updates = {k: v for k, v in request.model_dump(exclude_none=True).items() if k in ALLOWED_COLUMNS}
    if not updates:
        raise HTTPException(
            status_code=400, detail={"error": "No fields to update", "error_ar": "لا توجد حقول للتحديث"}
        )

    set_clauses = []
    values = []
    for i, (key, val) in enumerate(updates.items(), 1):
        set_clauses.append(f"{key} = ${i}")
        values.append(val)
    values.append(uuid.UUID(coop_id))

    row = await pool.fetchrow(
        f"UPDATE cooperatives SET {', '.join(set_clauses)} WHERE id = ${len(values)} RETURNING *",  # nosec B608 - keys validated against ALLOWED_COLUMNS allowlist  # nosemgrep: python.lang.security.audit.formatted-sql-query
        *values,
    )
    logger.info("cooperative_updated", coop_id=coop_id, fields=list(updates.keys()))
    return _row_to_dict(row)


@router.delete("/{coop_id}", status_code=204)
async def delete_cooperative(coop_id: str, req: Request, tenant_id: str = Depends(get_tenant_id), _user=Depends(get_current_user)):
    """Delete cooperative - حذف التعاونية"""
    pool = await _get_db(req)
    await _get_coop_or_404(pool, coop_id, tenant_id)

    # CASCADE in DB handles members, resources, bookings
    await pool.execute("DELETE FROM cooperatives WHERE id = $1", uuid.UUID(coop_id))
    logger.info("cooperative_deleted", coop_id=coop_id)


# === Member Endpoints ===


@router.post("/{coop_id}/members", status_code=201)
async def add_member(coop_id: str, request: MemberCreateRequest, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Add member to cooperative - إضافة عضو للتعاونية"""
    pool = await _get_db(req)
    await _get_coop_or_404(pool, coop_id, tenant_id)

    coop_uuid = uuid.UUID(coop_id)

    row = await pool.fetchrow(
        """
        INSERT INTO cooperative_members (cooperative_id, farmer_id, name, name_ar, phone, role, share_count, land_area_ha, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'active')
        RETURNING *
        """,
        coop_uuid,
        request.farmer_id,
        request.name,
        request.name_ar,
        request.phone,
        request.role,
        request.share_count,
        request.land_area_ha,
    )

    # Update member count
    await pool.execute(
        "UPDATE cooperatives SET member_count = (SELECT COUNT(*) FROM cooperative_members WHERE cooperative_id = $1 AND status = 'active') WHERE id = $1",
        coop_uuid,
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        member_data = _row_to_dict(row)
        await nc.publish(
            SAHOOL_COOPERATIVE_MEMBER_ADDED,
            json.dumps({"cooperative_id": coop_id, "member_id": member_data["id"]}).encode(),
        )

    logger.info("member_added", coop_id=coop_id, member_id=str(row["id"]))
    return _row_to_dict(row)


@router.get("/{coop_id}/members")
async def list_members(coop_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """List cooperative members - قائمة أعضاء التعاونية"""
    pool = await _get_db(req)
    await _get_coop_or_404(pool, coop_id, tenant_id)

    rows = await pool.fetch(
        "SELECT * FROM cooperative_members WHERE cooperative_id = $1 ORDER BY joined_at", uuid.UUID(coop_id)
    )
    members = [_row_to_dict(r) for r in rows]
    return {"cooperative_id": coop_id, "members": members, "count": len(members)}


@router.delete("/{coop_id}/members/{member_id}", status_code=204)
async def remove_member(coop_id: str, member_id: str, req: Request, _user=Depends(get_current_user)):
    """Remove member from cooperative - إزالة عضو من التعاونية"""
    pool = await _get_db(req)
    coop_uuid = uuid.UUID(coop_id)

    row = await pool.fetchrow(
        "SELECT * FROM cooperative_members WHERE id = $1 AND cooperative_id = $2",
        uuid.UUID(member_id),
        coop_uuid,
    )
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"error": "Member not found in this cooperative", "error_ar": "العضو غير موجود في هذه التعاونية"},
        )

    await pool.execute("DELETE FROM cooperative_members WHERE id = $1", uuid.UUID(member_id))

    # Update member count
    await pool.execute(
        "UPDATE cooperatives SET member_count = (SELECT COUNT(*) FROM cooperative_members WHERE cooperative_id = $1 AND status = 'active') WHERE id = $1",
        coop_uuid,
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            SAHOOL_COOPERATIVE_MEMBER_REMOVED,
            json.dumps({"cooperative_id": coop_id, "member_id": member_id}).encode(),
        )

    logger.info("member_removed", coop_id=coop_id, member_id=member_id)


# === Resource Pool Endpoints ===


@router.post("/{coop_id}/resources", status_code=201)
async def register_resource(coop_id: str, request: ResourceCreateRequest, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Register shared resource - تسجيل مورد مشترك"""
    pool = await _get_db(req)
    await _get_coop_or_404(pool, coop_id, tenant_id)

    row = await pool.fetchrow(
        """
        INSERT INTO shared_resources (cooperative_id, name, name_ar, type, capacity, capacity_unit, model, hourly_rate, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'available')
        RETURNING *
        """,
        uuid.UUID(coop_id),
        request.name,
        request.name_ar,
        request.type,
        request.capacity,
        request.capacity_unit,
        request.model,
        request.hourly_rate,
    )
    logger.info("resource_registered", coop_id=coop_id, resource_id=str(row["id"]))
    return _row_to_dict(row)


@router.get("/{coop_id}/resources")
async def list_resources(coop_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """List cooperative resources - قائمة موارد التعاونية"""
    pool = await _get_db(req)
    await _get_coop_or_404(pool, coop_id, tenant_id)

    rows = await pool.fetch(
        "SELECT * FROM shared_resources WHERE cooperative_id = $1 ORDER BY created_at", uuid.UUID(coop_id)
    )
    resources = [_row_to_dict(r) for r in rows]
    return {"cooperative_id": coop_id, "resources": resources, "count": len(resources)}


@router.post("/{coop_id}/resources/{resource_id}/book", status_code=201)
async def book_resource(coop_id: str, resource_id: str, request: BookingCreateRequest, req: Request):
    """Book a shared resource - حجز مورد مشترك"""
    pool = await _get_db(req)

    resource = await pool.fetchrow(
        "SELECT * FROM shared_resources WHERE id = $1 AND cooperative_id = $2",
        uuid.UUID(resource_id),
        uuid.UUID(coop_id),
    )
    if not resource:
        raise HTTPException(status_code=404, detail={"error": "Resource not found", "error_ar": "المورد غير موجود"})

    member = await pool.fetchrow(
        "SELECT * FROM cooperative_members WHERE id = $1 AND cooperative_id = $2",
        uuid.UUID(request.member_id),
        uuid.UUID(coop_id),
    )
    if not member:
        raise HTTPException(status_code=404, detail={"error": "Member not found", "error_ar": "العضو غير موجود"})

    cost = float(resource["hourly_rate"] or 0) * request.duration_hours

    row = await pool.fetchrow(
        """
        INSERT INTO resource_bookings (resource_id, member_id, purpose, purpose_ar, start_time, duration_hours, cost, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'confirmed')
        RETURNING *
        """,
        uuid.UUID(resource_id),
        uuid.UUID(request.member_id),
        request.purpose,
        request.purpose_ar,
        request.start_time,
        request.duration_hours,
        cost,
    )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            SAHOOL_COOPERATIVE_RESOURCE_BOOKED,
            json.dumps({"cooperative_id": coop_id, "resource_id": resource_id, "booking_id": str(row["id"])}).encode(),
        )

    logger.info("resource_booked", resource_id=resource_id, booking_id=str(row["id"]))
    return _row_to_dict(row)


# === Revenue Distribution Endpoints ===


@router.post("/{coop_id}/revenue/distribute")
async def distribute_revenue(coop_id: str, request: RevenueDistributionRequest, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Distribute revenue among members - توزيع الإيرادات بين الأعضاء"""
    pool = await _get_db(req)
    await _get_coop_or_404(pool, coop_id, tenant_id)

    members = await pool.fetch(
        "SELECT * FROM cooperative_members WHERE cooperative_id = $1 AND status = 'active'",
        uuid.UUID(coop_id),
    )
    if not members:
        raise HTTPException(
            status_code=400, detail={"error": "No members in cooperative", "error_ar": "لا يوجد أعضاء في التعاونية"}
        )

    if request.method == "land_area":
        shares_data = {str(m["id"]): float(m.get("land_area_ha") or 1.0) for m in members}
    elif request.method == "contribution":
        shares_data = {str(m["id"]): float(m.get("share_count") or 1) for m in members}
    else:
        shares_data = {str(m["id"]): 1.0 for m in members}

    total_shares = sum(shares_data.values()) or 1.0
    distributions = []
    for m in members:
        mid = str(m["id"])
        share_ratio = shares_data.get(mid, 1.0) / total_shares
        amount = round(request.total_revenue * share_ratio, 2)
        distributions.append(
            {
                "member_id": mid,
                "member_name": m["name"],
                "member_name_ar": m["name_ar"],
                "share_ratio": round(share_ratio, 4),
                "amount": amount,
            }
        )

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            SAHOOL_COOPERATIVE_REVENUE_DISTRIBUTED,
            json.dumps(
                {"cooperative_id": coop_id, "total_revenue": request.total_revenue, "method": request.method}
            ).encode(),
        )
        # Notify members about revenue distribution
        await nc.publish(
            SAHOOL_NOTIFICATION_SEND,
            json.dumps(
                {
                    "type": "cooperative_revenue",
                    "cooperative_id": coop_id,
                    "title_en": f"Revenue Distribution: {request.total_revenue}",
                    "title_ar": f"توزيع الإيرادات: {request.total_revenue}",
                    "member_count": len(distributions),
                }
            ).encode(),
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
async def get_cooperative_stats(coop_id: str, req: Request, tenant_id: str = Depends(get_tenant_id)):
    """Get cooperative statistics - إحصائيات التعاونية"""
    pool = await _get_db(req)
    coop = _row_to_dict(await _get_coop_or_404(pool, coop_id, tenant_id))
    coop_uuid = uuid.UUID(coop_id)

    stats = await pool.fetchrow(
        """
        SELECT
            (SELECT COUNT(*) FROM cooperative_members WHERE cooperative_id = $1 AND status = 'active') AS member_count,
            (SELECT COUNT(*) FROM shared_resources WHERE cooperative_id = $1) AS resource_count,
            (SELECT COALESCE(SUM(land_area_ha), 0) FROM cooperative_members WHERE cooperative_id = $1 AND status = 'active') AS total_land_area_ha,
            (SELECT COALESCE(SUM(share_count), 0) FROM cooperative_members WHERE cooperative_id = $1 AND status = 'active') AS total_shares,
            (SELECT COUNT(*) FROM resource_bookings rb
             JOIN shared_resources sr ON rb.resource_id = sr.id
             WHERE sr.cooperative_id = $1 AND rb.status = 'confirmed') AS active_bookings,
            (SELECT COALESCE(SUM(rb.cost), 0) FROM resource_bookings rb
             JOIN shared_resources sr ON rb.resource_id = sr.id
             WHERE sr.cooperative_id = $1) AS total_booking_revenue
        """,
        coop_uuid,
    )

    return {
        "cooperative_id": coop_id,
        "name": coop["name"],
        "name_ar": coop["name_ar"],
        "member_count": stats["member_count"],
        "resource_count": stats["resource_count"],
        "total_land_area_ha": float(stats["total_land_area_ha"]),
        "total_shares": stats["total_shares"],
        "active_bookings": stats["active_bookings"],
        "total_booking_revenue": float(stats["total_booking_revenue"]),
    }
