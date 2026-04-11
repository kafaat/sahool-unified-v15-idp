"""
Cooperative Bookings API - حجوزات التعاونية

Exposes booking management endpoints required by the admin portal and mobile app:
- list/create bookings with filters
- get single booking
- approve/reject workflow with optimistic locking
"""

import json
import uuid
from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

try:
    from shared.events.subjects import (
        SAHOOL_COOPERATIVE_RESOURCE_BOOKED,
        SAHOOL_NOTIFICATION_SEND,
    )
except ImportError:  # pragma: no cover
    SAHOOL_COOPERATIVE_RESOURCE_BOOKED = "sahool.cooperative.resource_booked"
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

router = APIRouter(prefix="/api/v1/cooperatives/bookings", tags=["cooperative-bookings"])


# === Request/Response Models ===


class CooperativeBookingCreateRequest(BaseModel):
    cooperative_id: str
    resource_id: str | None = None
    booking_date: datetime
    duration_hours: float = Field(default=4.0, ge=0.0)
    notes: str | None = None


class BookingApprovalRequest(BaseModel):
    notes: str | None = None
    version: int | None = None


class BookingRejectionRequest(BaseModel):
    reason: str
    version: int | None = None


# === Helpers ===


async def _get_booking_or_404(pool, booking_id: str, tenant_id: str) -> dict[str, Any]:
    row = await pool.fetchrow(
        "SELECT * FROM cooperative_bookings WHERE id = $1 AND tenant_id = $2",
        uuid.UUID(booking_id),
        uuid.UUID(tenant_id),
    )
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"error": "Booking not found", "error_ar": "الحجز غير موجود"},
        )
    return dict(row)


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


async def _publish_event(req: Request, subject: str, payload: dict[str, Any]) -> None:
    nc = getattr(req.app.state, "nc", None)
    if not nc:
        return
    try:
        await nc.publish(subject, json.dumps(payload, default=str).encode())
    except Exception as exc:  # pragma: no cover - event publishing is best-effort
        logger.warning("event_publish_failed", subject=subject, error=str(exc))


# === Endpoints ===


@router.get("")
async def list_bookings(
    req: Request,
    status: str | None = Query(None, description="Filter by status"),
    cooperative_id: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """List cooperative bookings with optional filters - قائمة حجوزات التعاونية"""
    pool = await _get_db(req)

    conditions = ["tenant_id = $1"]
    params: list[Any] = [uuid.UUID(tenant_id)]

    if status:
        params.append(status)
        conditions.append(f"status = ${len(params)}")
    if cooperative_id:
        _validate_uuid(cooperative_id, "cooperative_id")
        params.append(uuid.UUID(cooperative_id))
        conditions.append(f"cooperative_id = ${len(params)}")
    if start_date:
        params.append(start_date)
        conditions.append(f"booking_date >= ${len(params)}")
    if end_date:
        params.append(end_date)
        conditions.append(f"booking_date <= ${len(params)}")

    where_clause = " AND ".join(conditions)
    params.append(limit)
    params.append(offset)

    # nosec B608 - conditions built from validated params
    query = (  # nosemgrep: python.lang.security.audit.formatted-sql-query
        f"SELECT * FROM cooperative_bookings WHERE {where_clause} "
        f"ORDER BY booking_date DESC LIMIT ${len(params) - 1} OFFSET ${len(params)}"
    )
    rows = await pool.fetch(query, *params)

    bookings = [_row_to_dict(r) for r in rows]
    return {"bookings": bookings, "count": len(bookings), "limit": limit, "offset": offset}


@router.post("", status_code=201)
async def create_booking(
    request: CooperativeBookingCreateRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create a new cooperative booking - إنشاء حجز جديد"""
    pool = await _get_db(req)

    _validate_uuid(request.cooperative_id, "cooperative_id")
    if request.resource_id:
        _validate_uuid(request.resource_id, "resource_id")

    requested_by = getattr(current_user, "id", None) or "00000000-0000-0000-0000-000000000000"
    try:
        requested_by_uuid = uuid.UUID(str(requested_by))
    except ValueError:
        # Deterministic namespace UUID for non-UUID user identifiers
        requested_by_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(requested_by))

    row = await pool.fetchrow(
        """
        INSERT INTO cooperative_bookings (
            tenant_id, cooperative_id, resource_id, requested_by,
            booking_date, duration_hours, status, notes, version
        )
        VALUES ($1, $2, $3, $4, $5, $6, 'pending', $7, 1)
        RETURNING *
        """,
        uuid.UUID(tenant_id),
        uuid.UUID(request.cooperative_id),
        uuid.UUID(request.resource_id) if request.resource_id else None,
        requested_by_uuid,
        request.booking_date,
        request.duration_hours,
        request.notes,
    )

    booking = _row_to_dict(row)
    await _publish_event(
        req,
        SAHOOL_COOPERATIVE_RESOURCE_BOOKED,
        {
            "booking_id": booking["id"],
            "cooperative_id": booking["cooperative_id"],
            "tenant_id": tenant_id,
            "status": "pending",
        },
    )
    logger.info("cooperative_booking_created", booking_id=booking["id"])
    return booking


@router.get("/{booking_id}")
async def get_booking(
    booking_id: str,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get booking details - تفاصيل الحجز"""
    _validate_uuid(booking_id, "booking_id")
    pool = await _get_db(req)
    booking = await _get_booking_or_404(pool, booking_id, tenant_id)
    return _row_to_dict(booking)


@router.post("/{booking_id}/approve")
async def approve_booking(
    booking_id: str,
    request: BookingApprovalRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Approve a pending booking - الموافقة على الحجز"""
    _validate_uuid(booking_id, "booking_id")
    pool = await _get_db(req)
    current = await _get_booking_or_404(pool, booking_id, tenant_id)

    if current["status"] != "pending":
        raise HTTPException(
            status_code=409,
            detail={
                "error": f"Booking cannot be approved from status '{current['status']}'",
                "error_ar": "لا يمكن الموافقة على الحجز في حالته الحالية",
            },
        )

    if request.version is not None and request.version != current.get("version"):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Version conflict - booking was modified by another operation",
                "error_ar": "تعارض الإصدار - تم تعديل الحجز بواسطة عملية أخرى",
            },
        )

    approver = getattr(current_user, "id", None) or "00000000-0000-0000-0000-000000000000"
    try:
        approver_uuid = uuid.UUID(str(approver))
    except ValueError:
        approver_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(approver))

    row = await pool.fetchrow(
        """
        UPDATE cooperative_bookings
        SET status = 'approved',
            approved_by = $1,
            approved_at = NOW(),
            notes = COALESCE($2, notes),
            version = version + 1
        WHERE id = $3 AND tenant_id = $4 AND status = 'pending' AND version = $5
        RETURNING *
        """,
        approver_uuid,
        request.notes,
        uuid.UUID(booking_id),
        uuid.UUID(tenant_id),
        current.get("version", 1),
    )

    if not row:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Booking state changed concurrently, please retry",
                "error_ar": "تغيرت حالة الحجز بشكل متزامن، يرجى المحاولة مجدداً",
            },
        )

    booking = _row_to_dict(row)
    await _publish_event(
        req,
        SAHOOL_NOTIFICATION_SEND,
        {
            "type": "cooperative_booking_approved",
            "booking_id": booking["id"],
            "tenant_id": tenant_id,
        },
    )
    logger.info("cooperative_booking_approved", booking_id=booking["id"], approver=str(approver_uuid))
    return booking


@router.post("/{booking_id}/reject")
async def reject_booking(
    booking_id: str,
    request: BookingRejectionRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Reject a pending booking - رفض الحجز"""
    _validate_uuid(booking_id, "booking_id")
    pool = await _get_db(req)
    current = await _get_booking_or_404(pool, booking_id, tenant_id)

    if current["status"] != "pending":
        raise HTTPException(
            status_code=409,
            detail={
                "error": f"Booking cannot be rejected from status '{current['status']}'",
                "error_ar": "لا يمكن رفض الحجز في حالته الحالية",
            },
        )

    if request.version is not None and request.version != current.get("version"):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Version conflict - booking was modified by another operation",
                "error_ar": "تعارض الإصدار - تم تعديل الحجز بواسطة عملية أخرى",
            },
        )

    approver = getattr(current_user, "id", None) or "00000000-0000-0000-0000-000000000000"
    try:
        approver_uuid = uuid.UUID(str(approver))
    except ValueError:
        approver_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(approver))

    existing_notes = current.get("notes") or ""
    rejection_note = f"REJECTED: {request.reason}"
    merged_notes = f"{existing_notes}\n{rejection_note}".strip() if existing_notes else rejection_note

    row = await pool.fetchrow(
        """
        UPDATE cooperative_bookings
        SET status = 'rejected',
            approved_by = $1,
            approved_at = NOW(),
            notes = $2,
            version = version + 1
        WHERE id = $3 AND tenant_id = $4 AND status = 'pending' AND version = $5
        RETURNING *
        """,
        approver_uuid,
        merged_notes,
        uuid.UUID(booking_id),
        uuid.UUID(tenant_id),
        current.get("version", 1),
    )

    if not row:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Booking state changed concurrently, please retry",
                "error_ar": "تغيرت حالة الحجز بشكل متزامن، يرجى المحاولة مجدداً",
            },
        )

    booking = _row_to_dict(row)
    await _publish_event(
        req,
        SAHOOL_NOTIFICATION_SEND,
        {
            "type": "cooperative_booking_rejected",
            "booking_id": booking["id"],
            "tenant_id": tenant_id,
            "reason": request.reason,
        },
    )
    logger.info("cooperative_booking_rejected", booking_id=booking["id"], reason=request.reason)
    return booking
