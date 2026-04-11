"""
Cooperative Purchase Orders API - أوامر الشراء للتعاونية

Exposes purchase order management endpoints required by the admin portal:
- list/create purchase orders with filters
- get single purchase order
- update purchase order with optimistic locking
"""

import json
import uuid
from decimal import Decimal
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

# Purchase-order specific event subjects (not yet in shared.events.subjects)
SAHOOL_COOPERATIVE_PURCHASE_ORDER_CREATED = "sahool.cooperative.purchase_order_created"
SAHOOL_COOPERATIVE_PURCHASE_ORDER_UPDATED = "sahool.cooperative.purchase_order_updated"

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

router = APIRouter(prefix="/api/v1/cooperatives/purchase-orders", tags=["cooperative-purchase-orders"])


# === Allowed Status Values ===

ALLOWED_STATUSES: set[str] = {"draft", "sent", "received", "paid", "cancelled"}


# === Request / Response Models ===


class PurchaseOrderItem(BaseModel):
    sku: str | None = None
    description: str
    description_ar: str | None = None
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    unit: str | None = None


class PurchaseOrderCreateRequest(BaseModel):
    cooperative_id: str
    supplier_id: str | None = None
    items: list[PurchaseOrderItem] = Field(..., min_length=1)
    currency: str = "SAR"
    total_amount: float | None = Field(default=None, ge=0)
    status: str = "draft"


class PurchaseOrderUpdateRequest(BaseModel):
    supplier_id: str | None = None
    items: list[PurchaseOrderItem] | None = None
    currency: str | None = None
    total_amount: float | None = Field(default=None, ge=0)
    status: str | None = None
    version: int | None = None


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


def _validate_status(status: str) -> None:
    if status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Invalid status '{status}'. Allowed: {sorted(ALLOWED_STATUSES)}",
                "error_ar": "حالة غير صالحة",
            },
        )


async def _get_order_or_404(pool, order_id: str, tenant_id: str) -> dict[str, Any]:
    row = await pool.fetchrow(
        "SELECT * FROM cooperative_purchase_orders WHERE id = $1 AND tenant_id = $2",
        uuid.UUID(order_id),
        uuid.UUID(tenant_id),
    )
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"error": "Purchase order not found", "error_ar": "أمر الشراء غير موجود"},
        )
    return dict(row)


async def _publish_event(req: Request, subject: str, payload: dict[str, Any]) -> None:
    nc = getattr(req.app.state, "nc", None)
    if not nc:
        return
    try:
        await nc.publish(subject, json.dumps(payload, default=str).encode())
    except Exception as exc:  # pragma: no cover - event publishing is best-effort
        logger.warning("event_publish_failed", subject=subject, error=str(exc))


def _compute_total(items: list[PurchaseOrderItem]) -> float:
    total = Decimal("0")
    for item in items:
        total += Decimal(str(item.quantity)) * Decimal(str(item.unit_price))
    return float(total)


def _serialize_order(row: dict[str, Any]) -> dict[str, Any]:
    data = _row_to_dict(row)
    # Items column is JSONB - parse if returned as string
    items = data.get("items")
    if isinstance(items, str):
        try:
            data["items"] = json.loads(items)
        except (TypeError, ValueError):  # pragma: no cover
            pass
    # Coerce total_amount to float for JSON
    if isinstance(data.get("total_amount"), Decimal):
        data["total_amount"] = float(data["total_amount"])
    return data


# === Endpoints ===


@router.get("")
async def list_purchase_orders(
    req: Request,
    status: str | None = Query(None, description="Filter by status"),
    cooperative_id: str | None = Query(None),
    supplier_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """List cooperative purchase orders - قائمة أوامر الشراء"""
    pool = await _get_db(req)

    conditions = ["tenant_id = $1"]
    params: list[Any] = [uuid.UUID(tenant_id)]

    if status:
        _validate_status(status)
        params.append(status)
        conditions.append(f"status = ${len(params)}")
    if cooperative_id:
        _validate_uuid(cooperative_id, "cooperative_id")
        params.append(uuid.UUID(cooperative_id))
        conditions.append(f"cooperative_id = ${len(params)}")
    if supplier_id:
        _validate_uuid(supplier_id, "supplier_id")
        params.append(uuid.UUID(supplier_id))
        conditions.append(f"supplier_id = ${len(params)}")

    where_clause = " AND ".join(conditions)
    params.append(limit)
    params.append(offset)

    # WHERE clause built from `conditions` (static `column = $N` strings
    # — see ALLOWED_FILTERS allowlist); user values flow through asyncpg
    # parameters, never into the SQL string. Safe SQL composition.
    query = (
        f"SELECT * FROM cooperative_purchase_orders WHERE {where_clause} "  # nosec B608  # nosemgrep: python.lang.security.audit.formatted-sql-query
        f"ORDER BY created_at DESC LIMIT ${len(params) - 1} OFFSET ${len(params)}"
    )
    rows = await pool.fetch(query, *params)
    orders = [_serialize_order(r) for r in rows]
    return {"purchase_orders": orders, "count": len(orders), "limit": limit, "offset": offset}


@router.post("", status_code=201)
async def create_purchase_order(
    request: PurchaseOrderCreateRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Create a new purchase order - إنشاء أمر شراء جديد"""
    _validate_uuid(request.cooperative_id, "cooperative_id")
    if request.supplier_id:
        _validate_uuid(request.supplier_id, "supplier_id")
    _validate_status(request.status)

    pool = await _get_db(req)
    total_amount = request.total_amount if request.total_amount is not None else _compute_total(request.items)
    items_json = json.dumps([item.model_dump() for item in request.items])

    row = await pool.fetchrow(
        """
        INSERT INTO cooperative_purchase_orders (
            tenant_id, cooperative_id, supplier_id,
            total_amount, currency, status, items, version
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, 1)
        RETURNING *
        """,
        uuid.UUID(tenant_id),
        uuid.UUID(request.cooperative_id),
        uuid.UUID(request.supplier_id) if request.supplier_id else None,
        total_amount,
        request.currency,
        request.status,
        items_json,
    )

    order = _serialize_order(row)
    await _publish_event(
        req,
        SAHOOL_COOPERATIVE_PURCHASE_ORDER_CREATED,
        {
            "purchase_order_id": order["id"],
            "cooperative_id": order["cooperative_id"],
            "tenant_id": tenant_id,
            "total_amount": order.get("total_amount"),
            "status": order["status"],
        },
    )
    logger.info("purchase_order_created", order_id=order["id"], total=total_amount)
    return order


@router.get("/{order_id}")
async def get_purchase_order(
    order_id: str,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get purchase order details - تفاصيل أمر الشراء"""
    _validate_uuid(order_id, "order_id")
    pool = await _get_db(req)
    order = await _get_order_or_404(pool, order_id, tenant_id)
    return _serialize_order(order)


@router.put("/{order_id}")
async def update_purchase_order(
    order_id: str,
    request: PurchaseOrderUpdateRequest,
    req: Request,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update purchase order with optimistic locking - تحديث أمر الشراء"""
    _validate_uuid(order_id, "order_id")
    pool = await _get_db(req)
    current = await _get_order_or_404(pool, order_id, tenant_id)

    if request.version is not None and request.version != current.get("version"):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Version conflict - purchase order was modified by another operation",
                "error_ar": "تعارض الإصدار - تم تعديل أمر الشراء بواسطة عملية أخرى",
            },
        )

    if request.status is not None:
        _validate_status(request.status)
    if request.supplier_id:
        _validate_uuid(request.supplier_id, "supplier_id")

    # Build update dict
    allowed: dict[str, Any] = {}
    if request.supplier_id is not None:
        allowed["supplier_id"] = uuid.UUID(request.supplier_id)
    if request.currency is not None:
        allowed["currency"] = request.currency
    if request.status is not None:
        allowed["status"] = request.status
    if request.items is not None:
        allowed["items"] = json.dumps([item.model_dump() for item in request.items])
        if request.total_amount is None:
            allowed["total_amount"] = _compute_total(request.items)
    if request.total_amount is not None:
        allowed["total_amount"] = request.total_amount

    if not allowed:
        raise HTTPException(
            status_code=400,
            detail={"error": "No fields to update", "error_ar": "لا توجد حقول للتحديث"},
        )

    ALLOWED_COLUMNS = {"supplier_id", "currency", "status", "items", "total_amount"}
    set_clauses: list[str] = []
    values: list[Any] = []
    for key, val in allowed.items():
        if key not in ALLOWED_COLUMNS:
            continue
        values.append(val)
        if key == "items":
            set_clauses.append(f"items = ${len(values)}::jsonb")
        else:
            set_clauses.append(f"{key} = ${len(values)}")

    # version bump + locking
    set_clauses.append("version = version + 1")
    values.append(uuid.UUID(order_id))
    values.append(uuid.UUID(tenant_id))
    values.append(current.get("version", 1))

    # `set_clauses` built from `column = $N` fragments where `column` is
    # validated against ALLOWED_COLUMNS allowlist; user values bound via
    # asyncpg parameters. Safe SQL composition.
    query = (
        f"UPDATE cooperative_purchase_orders SET {', '.join(set_clauses)} "  # nosec B608  # nosemgrep: python.lang.security.audit.formatted-sql-query
        f"WHERE id = ${len(values) - 2} AND tenant_id = ${len(values) - 1} AND version = ${len(values)} "
        f"RETURNING *"
    )
    row = await pool.fetchrow(query, *values)
    if not row:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Purchase order state changed concurrently, please retry",
                "error_ar": "تغيرت حالة أمر الشراء بشكل متزامن، يرجى المحاولة مجدداً",
            },
        )

    order = _serialize_order(row)
    await _publish_event(
        req,
        SAHOOL_COOPERATIVE_PURCHASE_ORDER_UPDATED,
        {
            "purchase_order_id": order["id"],
            "cooperative_id": order["cooperative_id"],
            "tenant_id": tenant_id,
            "status": order["status"],
        },
    )
    logger.info("purchase_order_updated", order_id=order["id"], fields=list(allowed.keys()))
    return order
