"""
Input application HTTP endpoints — نقاط نهاية تطبيقات المدخلات
=============================================================

Exposes ``ApplicationTracker`` over HTTP. Same tenant model as the
warehouse router: every call extracts tenant_id from the JWT and threads
it down to the manager — cross-tenant IDs silently return 404 via the
``id_tenantId`` composite unique in schema.prisma.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from .application_tracker import ApplicationMethod, ApplicationPurpose

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover

    class User(BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str | None = None
        roles: list[str] = []

    async def get_current_user() -> User:  # type: ignore[no-redef]
        raise HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(prefix="/v1/applications", tags=["applications"])


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _require_tenant_id(user: User | None) -> str:
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


def _require_tracker(request: Request) -> Any:
    tracker = getattr(request.app.state, "tracker", None)
    if tracker is None or not getattr(request.app.state, "prisma_ready", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Applications subsystem unavailable (Prisma client not initialised)",
                "errorAr": "نظام تتبع التطبيقات غير متاح حالياً",
            },
        )
    return tracker


# ─────────────────────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────────────────────


class RecordApplicationRequest(BaseModel):
    field_id: str
    crop_season_id: str
    item_id: str
    quantity: float = Field(gt=0)
    method: ApplicationMethod
    purpose: ApplicationPurpose
    area_ha: float = Field(gt=0)
    application_date: datetime | None = None
    # Optional environmental context
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    growth_stage: str | None = None
    equipment_used: str | None = None
    ppe_used: list[str] | None = None
    target_pest_disease: str | None = None
    efficacy_rating: int | None = Field(default=None, ge=1, le=5)
    withholding_period_days: int | None = Field(default=None, ge=0)
    notes: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.post("", status_code=status.HTTP_201_CREATED)
async def record_application(
    dto: RecordApplicationRequest,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Record an input application — deducts from inventory, audits FIFO batch."""
    tenant_id = _require_tenant_id(user)
    tracker = _require_tracker(request)
    extras = dto.model_dump(
        exclude={
            "field_id",
            "crop_season_id",
            "item_id",
            "quantity",
            "method",
            "purpose",
            "area_ha",
            "application_date",
        },
        exclude_none=True,
    )
    try:
        record = await tracker.record_application(
            field_id=dto.field_id,
            crop_season_id=dto.crop_season_id,
            item_id=dto.item_id,
            quantity=dto.quantity,
            method=dto.method,
            purpose=dto.purpose,
            applied_by=str(getattr(user, "id", "unknown")),
            area_ha=dto.area_ha,
            tenant_id=tenant_id,
            application_date=dto.application_date,
            **extras,
        )
    except ValueError as e:
        # Inventory not found / insufficient stock → 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return _input_application_to_dict(record)


@router.get("/{application_id}")
async def get_application(
    application_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Get a single input application by ID (tenant-scoped)."""
    tenant_id = _require_tenant_id(user)
    tracker = _require_tracker(request)
    record = await tracker.get_application_by_id(application_id, tenant_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return _input_application_to_dict(record)


@router.get("/field/{field_id}")
async def list_field_applications(
    field_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    crop_season_id: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> list[dict]:
    """List applications for a field (tenant-scoped)."""
    tenant_id = _require_tenant_id(user)
    tracker = _require_tracker(request)
    records = await tracker.get_field_applications(
        field_id=field_id,
        tenant_id=tenant_id,
        crop_season_id=crop_season_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )
    return [_input_application_to_dict(r) for r in records]


@router.get("/field/{field_id}/summary/{crop_season_id}")
async def get_application_summary(
    field_id: str,
    crop_season_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Aggregate summary (NPK breakdown, totals, timeline)."""
    tenant_id = _require_tenant_id(user)
    tracker = _require_tracker(request)
    return await tracker.get_application_summary(field_id, crop_season_id, tenant_id)


@router.get("/field/{field_id}/costs/{crop_season_id}")
async def get_input_costs(
    field_id: str,
    crop_season_id: str,
    request: Request,
    user: User = Depends(get_current_user),
) -> dict:
    """Total input costs for a crop season."""
    tenant_id = _require_tenant_id(user)
    tracker = _require_tracker(request)
    return await tracker.calculate_input_costs(field_id, crop_season_id, tenant_id)


@router.get("/field/{field_id}/harvest-safety/{crop_season_id}")
async def check_harvest_safety(
    field_id: str,
    crop_season_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    harvest_date: date | None = Query(default=None),
) -> dict:
    """PHI / withholding-period gate for a planned harvest."""
    tenant_id = _require_tenant_id(user)
    tracker = _require_tracker(request)
    return await tracker.check_withholding_period(
        field_id=field_id,
        crop_season_id=crop_season_id,
        tenant_id=tenant_id,
        harvest_date=harvest_date,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Serialization helper
# ─────────────────────────────────────────────────────────────────────────────


def _input_application_to_dict(record) -> dict:
    """Convert InputApplication dataclass → FastAPI-serialisable dict.

    Delegates to the dataclass's own ``to_dict()`` when available so the
    serialisation stays consistent with the rest of the service.
    """
    if hasattr(record, "to_dict") and callable(record.to_dict):
        return record.to_dict()
    # Fallback for unusual record types — keep keys stable for clients.
    return {
        "id": getattr(record, "id", None),
        "field_id": getattr(record, "field_id", None),
        "crop_season_id": getattr(record, "crop_season_id", None),
        "item_id": getattr(record, "item_id", None),
        "quantity_applied": getattr(record, "quantity_applied", None),
    }
