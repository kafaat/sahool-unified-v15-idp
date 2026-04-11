"""
Carbon footprint API endpoints — نقاط نهاية البصمة الكربونية

Exposes:
    POST /api/v1/carbon/compute                       — stateless compute
    POST /api/v1/carbon/operations/{id}/compute       — DB-backed compute
    GET  /api/v1/carbon/fields/{id}/summary           — field-level summary
    GET  /api/v1/carbon/crop-seasons/{id}/summary     — season-level summary

All endpoints are:
  * Tenant-scoped via the X-Tenant-Id header (extracted by TenantGuard
    middleware in production, validated here defensively).
  * Authenticated via the shared JWT bearer dependency. Unauthenticated
    requests get 401 before the handler runs. When `shared.auth` isn't
    importable (local dev without the shared package), a stub raises
    503 so the service never silently runs open.

Business logic sits in `src.engine.ipcc_tier1.IpccTier1Engine`, a pure
computation class that's trivially unit-testable.
"""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from src.engine import IpccTier1Engine, OperationInput

# -------------------------------------------------------------------------
# Authentication dependency (shared.auth when available, safe stub otherwise)
# -------------------------------------------------------------------------
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover - only hit in minimal local dev
    from fastapi import HTTPException as _HTTPException

    class User:  # type: ignore[no-redef]
        """Stub user model used only when shared.auth isn't installed."""

        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user() -> User:  # type: ignore[no-redef]
        raise _HTTPException(
            status_code=503,
            detail={
                "message": "Authentication backend unavailable",
                "message_ar": "خدمة المصادقة غير متاحة",
            },
        )


logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/carbon", tags=["Carbon - الكربون"])

engine = IpccTier1Engine()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ComputeRequest(BaseModel):
    """Stateless compute request — caller supplies all inputs inline."""

    operation_id: str = Field(..., description="Operation UUID or synthetic id")
    operation_type: str
    area_hectares: float | None = None
    duration_hours: float | None = None
    fuel_liters: float | None = None
    fuel_type: str = "diesel"
    nitrogen_kg: float | None = None
    phosphorus_kg: float | None = None
    potassium_kg: float | None = None
    pesticide_kg: float | None = None
    biochar_tonnes: float | None = None
    is_cover_cropping: bool = False
    is_no_till: bool = False
    is_residue_burning: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CarbonBreakdownResponse(BaseModel):
    fuel: float
    fertilizer_n: float
    fertilizer_p: float
    fertilizer_k: float
    machinery: float
    pesticide: float
    residue_burning: float
    cover_cropping_seq: float
    no_till_seq: float
    biochar_seq: float


class ComputeResponse(BaseModel):
    operation_id: str
    operation_type: str
    emissions_kg: float
    sequestration_kg: float
    net_kg: float
    methodology: str
    emission_source_type: str
    carbon_credit_eligible: bool
    breakdown: CarbonBreakdownResponse
    warnings: list[str]


class FieldCarbonSummary(BaseModel):
    field_id: str
    total_operations: int
    total_emissions_kg: float
    total_sequestration_kg: float
    total_net_kg: float
    currency: str = "kgCO2e"
    by_source: dict[str, float]
    first_operation_at: str | None
    last_operation_at: str | None


class CropSeasonCarbonSummary(BaseModel):
    crop_season_id: str
    field_id: str
    crop_type: str
    sowing_date: str
    total_operations: int
    total_emissions_kg: float
    total_sequestration_kg: float
    total_net_kg: float
    by_source: dict[str, float]
    by_operation_type: dict[str, dict[str, float]]


# ---------------------------------------------------------------------------
# Tenant helper
# ---------------------------------------------------------------------------


def _require_tenant(x_tenant_id: str | None) -> str:
    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "X-Tenant-Id header is required",
                "message_ar": "رأس X-Tenant-Id مطلوب",
            },
        )
    return x_tenant_id


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/compute", response_model=ComputeResponse)
async def compute_stateless(
    body: ComputeRequest,
    current_user: User = Depends(get_current_user),
) -> ComputeResponse:
    """
    Stateless compute — runs the engine on a fully-populated request
    without touching the DB. Useful for what-if analysis from the web
    client ("if I halve my fertiliser, what happens to my emissions?").

    Requires a valid JWT; does NOT persist anything, so tenant header
    isn't mandatory for this endpoint.
    """
    op = OperationInput(
        operation_id=body.operation_id,
        operation_type=body.operation_type,
        area_hectares=body.area_hectares,
        duration_hours=body.duration_hours,
        fuel_liters=body.fuel_liters,
        fuel_type=body.fuel_type,
        nitrogen_kg=body.nitrogen_kg,
        phosphorus_kg=body.phosphorus_kg,
        potassium_kg=body.potassium_kg,
        pesticide_kg=body.pesticide_kg,
        biochar_tonnes=body.biochar_tonnes,
        is_cover_cropping=body.is_cover_cropping,
        is_no_till=body.is_no_till,
        is_residue_burning=body.is_residue_burning,
        metadata=body.metadata,
    )
    result = engine.compute(op)
    return ComputeResponse(
        operation_id=result.operation_id,
        operation_type=result.operation_type,
        emissions_kg=result.emissions_kg,
        sequestration_kg=result.sequestration_kg,
        net_kg=result.net_kg,
        methodology=result.methodology,
        emission_source_type=result.emission_source_type,
        carbon_credit_eligible=result.carbon_credit_eligible,
        breakdown=CarbonBreakdownResponse(
            fuel=result.breakdown.fuel,
            fertilizer_n=result.breakdown.fertilizer_n,
            fertilizer_p=result.breakdown.fertilizer_p,
            fertilizer_k=result.breakdown.fertilizer_k,
            machinery=result.breakdown.machinery,
            pesticide=result.breakdown.pesticide,
            residue_burning=result.breakdown.residue_burning,
            cover_cropping_seq=result.breakdown.cover_cropping_seq,
            no_till_seq=result.breakdown.no_till_seq,
            biochar_seq=result.breakdown.biochar_seq,
        ),
        warnings=result.warnings,
    )


@router.post("/operations/{operation_id}/compute", response_model=ComputeResponse)
async def compute_for_operation(
    operation_id: str,
    request: Request,
    x_tenant_id: str | None = Header(default=None),
    current_user: User = Depends(get_current_user),
) -> ComputeResponse:
    """
    DB-backed compute — reads the FieldOperation row from the
    field-management-service DB, maps it into the engine's input shape
    (using operation_type + metadata + cost breakdown columns as a
    heuristic for inputs), runs the engine, and writes the result back
    onto the same row. Used by:

      - The NATS subscriber when a new operation is recorded
      - The admin API for re-computing after formula updates
      - Batch backfill jobs
    """
    tenant_id = _require_tenant(x_tenant_id)
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Database is unavailable",
                "message_ar": "قاعدة البيانات غير متاحة",
            },
        )

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                op.id, op.operation_type, op.duration_hours,
                op.fuel_liters, op.metadata,
                f.area_hectares
            FROM field_operations op
            JOIN fields f ON f.id = op.field_id
            WHERE op.id = $1::uuid
              AND op.tenant_id = $2
              AND op.deleted_at IS NULL
            """,
            operation_id,
            tenant_id,
        )
        if not row:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Operation not found",
                    "message_ar": "العملية غير موجودة",
                },
            )

        metadata = row["metadata"] or {}
        op = _map_row_to_input(dict(row), metadata)
        result = engine.compute(op)

        await conn.execute(
            """
            UPDATE field_operations
            SET co2_emissions_kg       = $1,
                co2_sequestration_kg   = $2,
                co2_net_kg             = $3,
                carbon_credit_eligible = $4,
                carbon_methodology     = $5,
                emission_source_type   = $6,
                carbon_computed_at     = NOW()
            WHERE id = $7::uuid
            """,
            result.emissions_kg,
            result.sequestration_kg,
            result.net_kg,
            result.carbon_credit_eligible,
            result.methodology,
            result.emission_source_type,
            operation_id,
        )

    return ComputeResponse(
        operation_id=result.operation_id,
        operation_type=result.operation_type,
        emissions_kg=result.emissions_kg,
        sequestration_kg=result.sequestration_kg,
        net_kg=result.net_kg,
        methodology=result.methodology,
        emission_source_type=result.emission_source_type,
        carbon_credit_eligible=result.carbon_credit_eligible,
        breakdown=CarbonBreakdownResponse(
            fuel=result.breakdown.fuel,
            fertilizer_n=result.breakdown.fertilizer_n,
            fertilizer_p=result.breakdown.fertilizer_p,
            fertilizer_k=result.breakdown.fertilizer_k,
            machinery=result.breakdown.machinery,
            pesticide=result.breakdown.pesticide,
            residue_burning=result.breakdown.residue_burning,
            cover_cropping_seq=result.breakdown.cover_cropping_seq,
            no_till_seq=result.breakdown.no_till_seq,
            biochar_seq=result.breakdown.biochar_seq,
        ),
        warnings=result.warnings,
    )


@router.get("/fields/{field_id}/summary", response_model=FieldCarbonSummary)
async def field_summary(
    field_id: str,
    request: Request,
    x_tenant_id: str | None = Header(default=None),
    current_user: User = Depends(get_current_user),
) -> FieldCarbonSummary:
    """Aggregate carbon data for a single field across all operations."""
    tenant_id = _require_tenant(x_tenant_id)
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    async with pool.acquire() as conn:
        # Parent-field tenant check
        field = await conn.fetchrow(
            """
            SELECT id FROM fields
            WHERE id = $1::uuid AND tenant_id = $2 AND is_deleted = FALSE
            """,
            field_id,
            tenant_id,
        )
        if not field:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Field not found",
                    "message_ar": "الحقل غير موجود",
                },
            )

        rows = await conn.fetch(
            """
            SELECT
                id, operation_type, performed_at,
                co2_emissions_kg, co2_sequestration_kg, co2_net_kg,
                emission_source_type
            FROM field_operations
            WHERE tenant_id = $1
              AND field_id = $2::uuid
              AND deleted_at IS NULL
              AND carbon_computed_at IS NOT NULL
            ORDER BY performed_at ASC
            """,
            tenant_id,
            field_id,
        )

    total_emissions = 0.0
    total_sequestration = 0.0
    total_net = 0.0
    by_source: dict[str, float] = {}
    first_at: str | None = None
    last_at: str | None = None

    for r in rows:
        emit = float(r["co2_emissions_kg"] or 0)
        seq = float(r["co2_sequestration_kg"] or 0)
        net = float(r["co2_net_kg"] or 0)
        total_emissions += emit
        total_sequestration += seq
        total_net += net
        src = r["emission_source_type"] or "mixed"
        by_source[src] = by_source.get(src, 0.0) + net
        if first_at is None:
            first_at = r["performed_at"].isoformat()
        last_at = r["performed_at"].isoformat()

    return FieldCarbonSummary(
        field_id=field_id,
        total_operations=len(rows),
        total_emissions_kg=round(total_emissions, 2),
        total_sequestration_kg=round(total_sequestration, 2),
        total_net_kg=round(total_net, 2),
        by_source={k: round(v, 2) for k, v in by_source.items()},
        first_operation_at=first_at,
        last_operation_at=last_at,
    )


@router.get(
    "/crop-seasons/{crop_season_id}/summary",
    response_model=CropSeasonCarbonSummary,
)
async def crop_season_summary(
    crop_season_id: str,
    request: Request,
    x_tenant_id: str | None = Header(default=None),
    current_user: User = Depends(get_current_user),
) -> CropSeasonCarbonSummary:
    """Aggregate carbon data for all operations in a crop season."""
    tenant_id = _require_tenant(x_tenant_id)
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    async with pool.acquire() as conn:
        season = await conn.fetchrow(
            """
            SELECT id, field_id, crop_type, sowing_date
            FROM crop_seasons
            WHERE id = $1::uuid AND tenant_id = $2 AND deleted_at IS NULL
            """,
            crop_season_id,
            tenant_id,
        )
        if not season:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Crop season not found",
                    "message_ar": "الموسم المحصولي غير موجود",
                },
            )

        rows = await conn.fetch(
            """
            SELECT operation_type, co2_emissions_kg,
                   co2_sequestration_kg, co2_net_kg,
                   emission_source_type
            FROM field_operations
            WHERE tenant_id = $1
              AND crop_season_id = $2::uuid
              AND deleted_at IS NULL
              AND carbon_computed_at IS NOT NULL
            """,
            tenant_id,
            crop_season_id,
        )

        # Update cached totals on the crop_seasons row so dashboards can
        # skip this endpoint for bulk listings.
        total_emit = sum(float(r["co2_emissions_kg"] or 0) for r in rows)
        total_seq = sum(float(r["co2_sequestration_kg"] or 0) for r in rows)
        total_net = sum(float(r["co2_net_kg"] or 0) for r in rows)

        await conn.execute(
            """
            UPDATE crop_seasons
            SET total_co2_emissions_kg = $1,
                total_co2_sequestration_kg = $2,
                total_co2_net_kg = $3,
                carbon_totals_updated_at = NOW()
            WHERE id = $4::uuid
            """,
            total_emit,
            total_seq,
            total_net,
            crop_season_id,
        )

    by_source: dict[str, float] = {}
    by_op_type: dict[str, dict[str, float]] = {}
    for r in rows:
        src = r["emission_source_type"] or "mixed"
        by_source[src] = by_source.get(src, 0.0) + float(r["co2_net_kg"] or 0)
        op_type = r["operation_type"]
        bucket = by_op_type.setdefault(op_type, {"emissions": 0.0, "sequestration": 0.0, "net": 0.0})
        bucket["emissions"] += float(r["co2_emissions_kg"] or 0)
        bucket["sequestration"] += float(r["co2_sequestration_kg"] or 0)
        bucket["net"] += float(r["co2_net_kg"] or 0)

    return CropSeasonCarbonSummary(
        crop_season_id=crop_season_id,
        field_id=str(season["field_id"]),
        crop_type=season["crop_type"],
        sowing_date=season["sowing_date"].isoformat(),
        total_operations=len(rows),
        total_emissions_kg=round(total_emit, 2),
        total_sequestration_kg=round(total_seq, 2),
        total_net_kg=round(total_net, 2),
        by_source={k: round(v, 2) for k, v in by_source.items()},
        by_operation_type={k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in by_op_type.items()},
    )


# ---------------------------------------------------------------------------
# DB row → engine input mapping
# ---------------------------------------------------------------------------


def _map_row_to_input(row: dict, metadata: dict) -> OperationInput:
    """
    Convert a field_operations row + its JSON metadata into an
    OperationInput the engine can consume.

    metadata schema (additive — all keys optional):
      {
        "fuel_liters": 12.5,
        "fuel_type": "diesel",
        "fertilizer": {"n_kg": 46, "p_kg": 20, "k_kg": 10},
        "pesticide_kg": 0.5,
        "biochar_tonnes": 0.0,
        "is_cover_cropping": false,
        "is_no_till": false,
        "is_residue_burning": false
      }
    """
    fert = metadata.get("fertilizer", {}) if isinstance(metadata, dict) else {}
    return OperationInput(
        operation_id=str(row["id"]),
        operation_type=row["operation_type"],
        area_hectares=float(row["area_hectares"]) if row.get("area_hectares") else None,
        duration_hours=float(row["duration_hours"]) if row.get("duration_hours") else None,
        fuel_liters=float(row.get("fuel_liters") or metadata.get("fuel_liters") or 0) or None,
        fuel_type=metadata.get("fuel_type", "diesel"),
        nitrogen_kg=float(fert.get("n_kg") or 0) or None,
        phosphorus_kg=float(fert.get("p_kg") or 0) or None,
        potassium_kg=float(fert.get("k_kg") or 0) or None,
        pesticide_kg=float(metadata.get("pesticide_kg") or 0) or None,
        biochar_tonnes=float(metadata.get("biochar_tonnes") or 0) or None,
        is_cover_cropping=bool(metadata.get("is_cover_cropping", False)),
        is_no_till=bool(metadata.get("is_no_till", False)),
        is_residue_burning=bool(metadata.get("is_residue_burning", False)),
        metadata=metadata if isinstance(metadata, dict) else {},
    )
