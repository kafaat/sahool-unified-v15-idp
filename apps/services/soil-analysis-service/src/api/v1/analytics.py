"""
Cross-field soil analytics endpoints - نقاط نهاية تحليلات التربة

Provides tenant-scoped listing across fields for the web analytics dashboard.
Query is keyed on `tenant_id` (enforced via JWT) with optional filters for
field, date range, and cursor pagination.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = structlog.get_logger()

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover - defensive
    from fastapi import HTTPException as _HTTPException

    class User:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():  # type: ignore[no-redef]
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(prefix="/api/v1/soil", tags=["soil-analytics"])


# === Response Models ===


class SoilTestRow(BaseModel):
    """Single soil test row as returned by the analytics list endpoint."""

    id: str
    tenant_id: str
    field_id: str | None = None
    sample_date: datetime
    ph: float | None = None
    ec: float | None = None
    organic_matter: float | None = None
    nitrogen_ppm: float | None = None
    phosphorus_ppm: float | None = None
    potassium_ppm: float | None = None
    calcium_ppm: float | None = None
    magnesium_ppm: float | None = None
    created_at: datetime


class PaginatedSoilTestsResponse(BaseModel):
    items: list[SoilTestRow]
    next_cursor: str | None = Field(None, alias="nextCursor")
    total: int | None = None

    model_config = {"populate_by_name": True}


# === Cursor helpers ===


def _encode_cursor(created_at: datetime, test_id: str) -> str:
    payload = json.dumps({"ts": created_at.isoformat(), "id": str(test_id)})
    return base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")


def _decode_cursor(cursor: str) -> tuple[datetime, str]:
    # Restore padding stripped above
    padding = "=" * (-len(cursor) % 4)
    try:
        raw = base64.urlsafe_b64decode((cursor + padding).encode()).decode()
        data = json.loads(raw)
        return datetime.fromisoformat(data["ts"]), str(data["id"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid cursor: {exc}") from exc


# === Endpoint ===


@router.get("/tests", response_model=PaginatedSoilTestsResponse, response_model_by_alias=True)
async def list_soil_tests(
    request: Request,
    tenant_id: str = Query(..., alias="tenantId"),
    field_id: str | None = Query(None, alias="fieldId"),
    from_date: datetime | None = Query(None, alias="fromDate"),
    to_date: datetime | None = Query(None, alias="toDate"),
    limit: int = Query(100, ge=1, le=500),
    cursor: str | None = Query(None),
    user: User = Depends(get_current_user),
) -> PaginatedSoilTestsResponse:
    """
    List soil tests for the authenticated tenant across fields.

    Tenant isolation: the caller's JWT `tenant_id` MUST equal the
    `tenantId` query parameter. Mismatch returns HTTP 403.

    Default ordering: `created_at DESC, id DESC`.
    Pagination: cursor-based on `(created_at, id)`.
    """
    # Enforce tenant isolation — non-negotiable.
    if getattr(user, "tenant_id", None) != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    pool = getattr(request.app.state, "db_pool", None)

    # Fallback path: in-memory store used in tests / when DB is unavailable.
    if pool is None:
        from src.api.v1.soil_tests import _soil_tests

        rows = [
            t
            for t in _soil_tests.values()
            if t.get("tenant_id") == tenant_id and (field_id is None or t.get("field_id") == field_id)
        ]
        rows.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        items = [
            SoilTestRow(
                id=str(t["id"]),
                tenant_id=str(t["tenant_id"]),
                field_id=t.get("field_id"),
                sample_date=datetime.fromisoformat(t["sample_date"]),
                ph=(t.get("soil_properties") or {}).get("ph"),
                ec=(t.get("soil_properties") or {}).get("ec_ds_m"),
                organic_matter=(t.get("soil_properties") or {}).get("organic_matter_percent"),
                nitrogen_ppm=(t.get("macronutrients") or {}).get("nitrogen_nitrate_ppm"),
                phosphorus_ppm=(t.get("macronutrients") or {}).get("phosphorus_ppm"),
                potassium_ppm=(t.get("macronutrients") or {}).get("potassium_ppm"),
                calcium_ppm=(t.get("macronutrients") or {}).get("calcium_ppm"),
                magnesium_ppm=(t.get("macronutrients") or {}).get("magnesium_ppm"),
                created_at=datetime.fromisoformat(t["created_at"]),
            )
            for t in rows[:limit]
        ]
        return PaginatedSoilTestsResponse(items=items, next_cursor=None, total=len(rows))

    # SQL path — always scoped to tenant_id.
    where = ["tenant_id = $1"]
    params: list[object] = [tenant_id]
    if field_id is not None:
        where.append(f"field_id = ${len(params) + 1}")
        params.append(field_id)
    if from_date is not None:
        where.append(f"sample_date >= ${len(params) + 1}")
        params.append(from_date)
    if to_date is not None:
        where.append(f"sample_date <= ${len(params) + 1}")
        params.append(to_date)
    if cursor is not None:
        cur_ts, cur_id = _decode_cursor(cursor)
        where.append(f"(created_at, id) < (${len(params) + 1}, ${len(params) + 2})")
        params.extend([cur_ts, cur_id])

    where_sql = " AND ".join(where)
    # Request `limit + 1` rows to determine whether a next page exists.
    query = (
        "SELECT id, tenant_id, field_id, sample_date, ph, ec, organic_matter, "
        "nitrogen_nitrate_ppm, phosphorus_ppm, potassium_ppm, "
        "calcium_ppm, magnesium_ppm, created_at "
        f"FROM soil_tests WHERE {where_sql} "
        "ORDER BY created_at DESC, id DESC "
        f"LIMIT ${len(params) + 1}"
    )
    params.append(limit + 1)

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
    except Exception as exc:  # noqa: BLE001
        logger.error("soil_tests_query_failed", error=str(exc))
        raise HTTPException(status_code=502, detail="Database query failed") from exc

    has_more = len(rows) > limit
    rows = rows[:limit]

    items = [
        SoilTestRow(
            id=str(r["id"]),
            tenant_id=str(r["tenant_id"]),
            field_id=str(r["field_id"]) if r["field_id"] is not None else None,
            sample_date=r["sample_date"],
            ph=float(r["ph"]) if r["ph"] is not None else None,
            ec=float(r["ec"]) if r["ec"] is not None else None,
            organic_matter=float(r["organic_matter"]) if r["organic_matter"] is not None else None,
            nitrogen_ppm=float(r["nitrogen_nitrate_ppm"]) if r["nitrogen_nitrate_ppm"] is not None else None,
            phosphorus_ppm=float(r["phosphorus_ppm"]) if r["phosphorus_ppm"] is not None else None,
            potassium_ppm=float(r["potassium_ppm"]) if r["potassium_ppm"] is not None else None,
            calcium_ppm=float(r["calcium_ppm"]) if r["calcium_ppm"] is not None else None,
            magnesium_ppm=float(r["magnesium_ppm"]) if r["magnesium_ppm"] is not None else None,
            created_at=r["created_at"],
        )
        for r in rows
    ]

    next_cursor = _encode_cursor(rows[-1]["created_at"], str(rows[-1]["id"])) if has_more and rows else None
    # total is deliberately None — counting is expensive for cross-field listing.
    return PaginatedSoilTestsResponse(items=items, next_cursor=next_cursor, total=None)
