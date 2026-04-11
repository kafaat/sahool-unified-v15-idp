"""
Cooperative Revenue API - إيرادات التعاونية

Exposes revenue aggregation and distribution endpoints for the admin portal:
- GET  /revenue?period=month|quarter|year → aggregate revenue
- POST /revenue/calculate → trigger revenue distribution calculation
"""

import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

try:
    from shared.events.subjects import (
        SAHOOL_COOPERATIVE_REVENUE_DISTRIBUTED,
        SAHOOL_NOTIFICATION_SEND,
    )
except ImportError:  # pragma: no cover
    SAHOOL_COOPERATIVE_REVENUE_DISTRIBUTED = "sahool.cooperative.revenue_distributed"
    SAHOOL_NOTIFICATION_SEND = "sahool.notification.send"

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover
    from fastapi import HTTPException as _HTTPException

    class User:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():  # type: ignore[misc]
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


from src.api.v1.cooperatives import _get_db, _row_to_dict, get_tenant_id

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/cooperatives/revenue", tags=["cooperative-revenue"])


ALLOWED_PERIODS = {"month", "quarter", "year"}
ALLOWED_METHODS = {"equal", "land_area", "contribution", "production"}


# === Request / Response Models ===


class RevenueCalculateRequest(BaseModel):
    cooperative_id: str
    total_revenue: float = Field(..., gt=0)
    method: str = "production"
    period_name: str | None = None


# === Helpers ===


def _validate_uuid(value: str, field: str) -> str:
    try:
        uuid.UUID(value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{field} must be a valid UUID",
                "error_ar": f"{field} يجب أن يكون UUID صالح",
            },
        )
    return value


def _period_start(period: str, now: datetime | None = None) -> datetime:
    now = now or datetime.now(UTC)
    if period == "month":
        return now - timedelta(days=30)
    if period == "quarter":
        return now - timedelta(days=90)
    if period == "year":
        return now - timedelta(days=365)
    raise HTTPException(
        status_code=400,
        detail={
            "error": f"Invalid period '{period}'. Allowed: {sorted(ALLOWED_PERIODS)}",
            "error_ar": "فترة غير صالحة",
        },
    )


async def _publish_event(req: Request, subject: str, payload: dict[str, Any]) -> None:
    nc = getattr(req.app.state, "nc", None)
    if not nc:
        return
    try:
        await nc.publish(subject, json.dumps(payload, default=str).encode())
    except Exception as exc:  # pragma: no cover
        logger.warning("event_publish_failed", subject=subject, error=str(exc))


async def _aggregate_booking_revenue(pool, tenant_id: str, cooperative_id: str | None, since: datetime) -> float:
    """Aggregate booking revenue for a tenant (optionally filtered by cooperative)."""
    try:
        if cooperative_id:
            row = await pool.fetchrow(
                """
                SELECT COALESCE(SUM(rb.cost), 0) AS total
                FROM resource_bookings rb
                JOIN shared_resources sr ON rb.resource_id = sr.id
                JOIN cooperatives c ON sr.cooperative_id = c.id
                WHERE c.tenant_id = $1
                  AND c.id = $2
                  AND rb.created_at >= $3
                """,
                uuid.UUID(tenant_id),
                uuid.UUID(cooperative_id),
                since,
            )
        else:
            row = await pool.fetchrow(
                """
                SELECT COALESCE(SUM(rb.cost), 0) AS total
                FROM resource_bookings rb
                JOIN shared_resources sr ON rb.resource_id = sr.id
                JOIN cooperatives c ON sr.cooperative_id = c.id
                WHERE c.tenant_id = $1 AND rb.created_at >= $2
                """,
                uuid.UUID(tenant_id),
                since,
            )
        return float(row["total"]) if row and row.get("total") is not None else 0.0
    except Exception as exc:  # pragma: no cover - stub when tables absent
        logger.warning("revenue_aggregation_failed", error=str(exc))
        return 0.0


async def _breakdown_by_member(
    pool, tenant_id: str, cooperative_id: str | None, since: datetime
) -> list[dict[str, Any]]:
    """Compute per-member booking revenue breakdown."""
    try:
        if cooperative_id:
            rows = await pool.fetch(
                """
                SELECT cm.id AS member_id, cm.name, cm.name_ar,
                       COALESCE(SUM(rb.cost), 0) AS total
                FROM cooperative_members cm
                JOIN cooperatives c ON cm.cooperative_id = c.id
                LEFT JOIN resource_bookings rb
                    ON rb.member_id = cm.id AND rb.created_at >= $3
                WHERE c.tenant_id = $1 AND c.id = $2
                GROUP BY cm.id, cm.name, cm.name_ar
                ORDER BY total DESC
                """,
                uuid.UUID(tenant_id),
                uuid.UUID(cooperative_id),
                since,
            )
        else:
            rows = await pool.fetch(
                """
                SELECT cm.id AS member_id, cm.name, cm.name_ar,
                       COALESCE(SUM(rb.cost), 0) AS total
                FROM cooperative_members cm
                JOIN cooperatives c ON cm.cooperative_id = c.id
                LEFT JOIN resource_bookings rb
                    ON rb.member_id = cm.id AND rb.created_at >= $2
                WHERE c.tenant_id = $1
                GROUP BY cm.id, cm.name, cm.name_ar
                ORDER BY total DESC
                """,
                uuid.UUID(tenant_id),
                since,
            )
        return [
            {
                "member_id": str(r["member_id"]),
                "name": r["name"],
                "name_ar": r["name_ar"],
                "amount": float(r["total"]) if r["total"] is not None else 0.0,
            }
            for r in rows
        ]
    except Exception as exc:  # pragma: no cover
        logger.warning("revenue_breakdown_failed", error=str(exc))
        return []


def _compute_distribution(
    total_revenue: float, members: list[dict[str, Any]], method: str
) -> list[dict[str, Any]]:
    if not members:
        return []

    if method == "land_area":
        shares = {str(m["id"]): float(m.get("land_area_ha") or 1.0) for m in members}
    elif method == "contribution":
        shares = {str(m["id"]): float(m.get("share_count") or 1) for m in members}
    else:
        # equal / production fall back to equal split
        shares = {str(m["id"]): 1.0 for m in members}

    total_shares = sum(shares.values()) or 1.0
    distributions = []
    for m in members:
        mid = str(m["id"])
        ratio = shares.get(mid, 1.0) / total_shares
        amount = round(total_revenue * ratio, 2)
        distributions.append(
            {
                "member_id": mid,
                "member_name": m["name"],
                "member_name_ar": m["name_ar"],
                "share_ratio": round(ratio, 4),
                "amount": amount,
            }
        )
    return distributions


# === Endpoints ===


@router.get("")
async def aggregate_revenue(
    req: Request,
    period: str = Query("month", description="Aggregation period: month|quarter|year"),
    cooperative_id: str | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Aggregate revenue for a period - إيرادات مجمّعة حسب الفترة"""
    if period not in ALLOWED_PERIODS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Invalid period '{period}'. Allowed: {sorted(ALLOWED_PERIODS)}",
                "error_ar": "فترة غير صالحة",
            },
        )
    if cooperative_id:
        _validate_uuid(cooperative_id, "cooperative_id")

    pool = await _get_db(req)
    since = _period_start(period)

    total_revenue = await _aggregate_booking_revenue(pool, tenant_id, cooperative_id, since)
    breakdown = await _breakdown_by_member(pool, tenant_id, cooperative_id, since)
    total_distributed = sum(entry["amount"] for entry in breakdown)

    return {
        "period": period,
        "period_start": since.isoformat(),
        "period_end": datetime.now(UTC).isoformat(),
        "cooperative_id": cooperative_id,
        "total_revenue": round(total_revenue, 2),
        "total_distributed": round(total_distributed, 2),
        "breakdown_by_member": breakdown,
    }


@router.post("/calculate")
async def calculate_revenue(
    request: RevenueCalculateRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Trigger revenue distribution calculation - حساب وتوزيع الإيرادات

    This re-uses the same distribution logic as
    POST /api/v1/cooperatives/{coop_id}/revenue/distribute but exposes a
    single top-level endpoint expected by the admin portal.
    """
    _validate_uuid(request.cooperative_id, "cooperative_id")
    if request.method not in ALLOWED_METHODS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Invalid method '{request.method}'. Allowed: {sorted(ALLOWED_METHODS)}",
                "error_ar": "طريقة غير صالحة",
            },
        )

    pool = await _get_db(req)

    # Tenant-isolated cooperative lookup
    coop = await pool.fetchrow(
        "SELECT * FROM cooperatives WHERE id = $1 AND tenant_id = $2",
        uuid.UUID(request.cooperative_id),
        uuid.UUID(tenant_id),
    )
    if not coop:
        raise HTTPException(
            status_code=404,
            detail={"error": "Cooperative not found", "error_ar": "التعاونية غير موجودة"},
        )

    members_rows = await pool.fetch(
        "SELECT * FROM cooperative_members WHERE cooperative_id = $1 AND status = 'active'",
        uuid.UUID(request.cooperative_id),
    )
    if not members_rows:
        raise HTTPException(
            status_code=400,
            detail={"error": "No active members in cooperative", "error_ar": "لا يوجد أعضاء نشطون"},
        )

    members = [_row_to_dict(m) for m in members_rows]
    distributions = _compute_distribution(request.total_revenue, members, request.method)

    await _publish_event(
        req,
        SAHOOL_COOPERATIVE_REVENUE_DISTRIBUTED,
        {
            "cooperative_id": request.cooperative_id,
            "tenant_id": tenant_id,
            "total_revenue": request.total_revenue,
            "method": request.method,
            "period": request.period_name,
        },
    )
    await _publish_event(
        req,
        SAHOOL_NOTIFICATION_SEND,
        {
            "type": "cooperative_revenue",
            "cooperative_id": request.cooperative_id,
            "tenant_id": tenant_id,
            "title_en": f"Revenue Distribution: {request.total_revenue}",
            "title_ar": f"توزيع الإيرادات: {request.total_revenue}",
            "member_count": len(distributions),
        },
    )
    logger.info(
        "revenue_calculated",
        coop_id=request.cooperative_id,
        total=request.total_revenue,
        members=len(distributions),
    )

    return {
        "cooperative_id": request.cooperative_id,
        "total_revenue": request.total_revenue,
        "method": request.method,
        "period": request.period_name,
        "distributions": distributions,
        "distributed_at": datetime.now(UTC).isoformat(),
    }
