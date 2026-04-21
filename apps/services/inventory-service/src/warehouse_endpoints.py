"""
Warehouse HTTP endpoints — نقاط نهاية المستودعات
===============================================

Thin FastAPI router that exposes the existing ``WarehouseManager``
operations (Prisma-backed) over HTTP. Every endpoint is tenant-scoped via
the authenticated JWT's ``tid`` claim — SUPER_ADMIN bypass is explicit
(opt-in via a keyword argument on ``WarehouseManager.get_warehouse``).

If the Prisma subsystem failed to come up at startup (see ``main.lifespan``)
the endpoints here return 503 instead of crashing the request. That keeps
the SQLAlchemy analytics surface (see ``api/v1/inventory.py``) fully
available even when Prisma isn't generated in the image.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover — dev environment without shared auth

    class User(BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str | None = None
        roles: list[str] = []

    async def get_current_user() -> User:  # type: ignore[no-redef]
        raise HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(prefix="/v1/warehouses", tags=["warehouses"])


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _require_tenant_id(user: User | None) -> str:
    """Extract tenant_id strictly from the authenticated user."""
    tenant_id = getattr(user, "tenant_id", None) if user is not None else None
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "tenant_id missing from JWT",
                "errorAr": "معرف المستأجر مفقود من الرمز",
            },
        )
    return str(tenant_id)


def _require_warehouse_manager(request: Request) -> Any:
    """Guard that returns the live WarehouseManager or raises 503."""
    wm = getattr(request.app.state, "warehouse_manager", None)
    if wm is None or not getattr(request.app.state, "prisma_ready", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Warehouse subsystem unavailable (Prisma client not initialised)",
                "errorAr": "نظام المستودعات غير متاح حالياً",
            },
        )
    return wm


# ─────────────────────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────────────────────


class TransferStockRequest(BaseModel):
    item_id: str
    to_warehouse: str
    quantity: float = Field(gt=0)
    from_warehouse: str | None = None
    transfer_type: str = "INTER_WAREHOUSE"
    notes: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/{warehouse_id}")
async def get_warehouse(
    warehouse_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Fetch a warehouse (tenant-scoped)."""
    tenant_id = _require_tenant_id(user)
    wm = _require_warehouse_manager(request)
    warehouse = await wm.get_warehouse(warehouse_id, tenant_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    # Return as dict (dataclass → dict) so FastAPI JSON-serialises cleanly.
    return {
        "id": warehouse.id,
        "name": warehouse.name,
        "name_ar": warehouse.name_ar,
        "warehouse_type": warehouse.warehouse_type.value,
        "capacity": warehouse.capacity,
        "capacity_unit": warehouse.capacity_unit,
        "current_utilization": warehouse.current_utilization,
        "storage_condition": warehouse.storage_condition.value,
        "is_active": warehouse.is_active,
    }


@router.get("/{warehouse_id}/utilization")
async def get_warehouse_utilization(
    warehouse_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Get current capacity utilization per zone."""
    tenant_id = _require_tenant_id(user)
    wm = _require_warehouse_manager(request)
    result = await wm.get_warehouse_utilization(warehouse_id, tenant_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get("/{warehouse_id}/conditions")
async def get_storage_conditions(
    warehouse_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Check storage conditions (configured ranges + any active alerts)."""
    tenant_id = _require_tenant_id(user)
    wm = _require_warehouse_manager(request)
    result = await wm.check_storage_conditions(warehouse_id, tenant_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.post("/transfers")
async def create_transfer(
    dto: TransferStockRequest,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Create a stock transfer request (PENDING status)."""
    tenant_id = _require_tenant_id(user)
    wm = _require_warehouse_manager(request)
    return await wm.transfer_stock(
        item_id=dto.item_id,
        from_warehouse=dto.from_warehouse,
        to_warehouse=dto.to_warehouse,
        quantity=dto.quantity,
        requested_by=str(getattr(user, "id", "unknown")),
        tenant_id=tenant_id,
        transfer_type=dto.transfer_type,
        notes=dto.notes,
    )


@router.post("/transfers/{transfer_id}/approve")
async def approve_transfer(
    transfer_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Approve a pending transfer (manager role)."""
    tenant_id = _require_tenant_id(user)
    wm = _require_warehouse_manager(request)
    try:
        return await wm.approve_transfer(
            transfer_id=transfer_id,
            approved_by=str(getattr(user, "id", "unknown")),
            tenant_id=tenant_id,
        )
    except Exception as e:  # Prisma RecordNotFound etc.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/transfers/{transfer_id}/complete")
async def complete_transfer(
    transfer_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Mark an approved transfer as completed (warehouse operator)."""
    tenant_id = _require_tenant_id(user)
    wm = _require_warehouse_manager(request)
    try:
        return await wm.complete_transfer(
            transfer_id=transfer_id,
            performed_by=str(getattr(user, "id", "unknown")),
            tenant_id=tenant_id,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
