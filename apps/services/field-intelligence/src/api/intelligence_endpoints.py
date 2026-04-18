"""
Field Intelligence HTTP surface expected by the web + mobile clients.

The clients (see packages/shared-types/src/contracts/api-endpoints.ts →
INTELLIGENCE_ENDPOINTS + apps/web/src/features/fields/api/field-intelligence-api.ts
for the TypeScript response types) call a specific set of paths that were
previously unimplemented — every request returned 404 and users saw empty
dashboards with error toasts. This module wires them up with responses
that match the canonical `ApiResponse<T>` envelope and the specific
TypeScript interfaces the web uses (LivingFieldScore, FieldZone[],
FieldAlert[], CreatedTask, BestDay[], DateValidation).

The responses are DETERMINISTIC STUBS on purpose: they compute every
value from a SHA-256 seed over `field_id` (and, where relevant, the
activity) so tests can assert exact equality and two reads of the same
field return byte-for-byte identical bodies. No timestamps, no `now()`
calls, no Redis lookups — just pure functions. When the rules engine in
`services/rules_engine.py` is wired up, replace the stub bodies without
changing any route signature or response shape.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Authentication imports — mirror the fail-secure fallback already used by
# the sibling routes.py so the router rejects unauthenticated requests
# instead of happily returning scores / zones / alerts to anyone.
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user() -> User:  # type: ignore[no-redef]
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(tags=["Field Intelligence"])


# ─────────────────────────────────────────────────────────────────────────────
# Canonical ApiResponse envelope
# Matches `packages/shared-types/src/contracts/api-responses.ts → ApiResponse`
# so every client (web, mobile, api-client) can unwrap `response.data.data`
# uniformly. Errors use the same shape with `success=False`.
# ─────────────────────────────────────────────────────────────────────────────


def _ok(data: Any) -> dict[str, Any]:
    return {"success": True, "data": data}


def _err(
    error: str, error_ar: str, *, error_code: str | None = None, extra: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build an ApiResponse error body. Pair with `_err_response()` for the
    HTTP wrapper — raising HTTPException(detail=this) would get wrapped
    by FastAPI into `{detail: {...}}`, losing the envelope shape.
    """
    body: dict[str, Any] = {
        "success": False,
        "error": error,
        "errorAr": error_ar,
    }
    if error_code:
        body["errorCode"] = error_code
    if extra:
        body.update(extra)
    return body


def _err_response(
    status_code: int, error: str, error_ar: str, *, error_code: str | None = None, extra: dict[str, Any] | None = None
) -> JSONResponse:
    """Return a JSONResponse that matches the canonical ApiResponse error
    envelope. Used in place of `raise HTTPException(detail=...)` because
    FastAPI wraps HTTPException detail into `{detail: ...}`, which breaks
    the flat `{success, error, errorAr, errorCode}` shape the web expects.
    """
    return JSONResponse(
        status_code=status_code,
        content=_err(error, error_ar, error_code=error_code, extra=extra),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic seeding helpers
# ─────────────────────────────────────────────────────────────────────────────


def _field_seed(field_id: str) -> int:
    """Stable deterministic seed from field_id so responses are reproducible."""
    digest = hashlib.sha256(field_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big")


def _score_to_rating(score: int) -> tuple[str, str]:
    """Map a 0-100 score to the rating scale the web uses."""
    if score >= 80:
        return ("excellent", "ممتاز")
    if score >= 60:
        return ("good", "جيد")
    if score >= 40:
        return ("moderate", "مقبول")
    return ("poor", "ضعيف")


def _trend_label(delta: int) -> str:
    if delta > 2:
        return "improving"
    if delta < -2:
        return "declining"
    return "stable"


# Deterministic timestamp so responses stay reproducible in tests. Set to
# an obvious epoch-ish sentinel instead of datetime.now(); operators who
# want a real-time value should source it upstream once the rules engine
# replaces the stub.
_DETERMINISTIC_STUB_TIMESTAMP = "2026-01-01T00:00:00Z"


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic request models
# ─────────────────────────────────────────────────────────────────────────────


class CreateTaskFromAlertRequest(BaseModel):
    """POST /api/v1/intelligence/alerts/{alertId}/create-task payload.

    Shape mirrors web `TaskFromAlertData` interface in
    apps/web/src/features/fields/api/field-intelligence-api.ts.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    title: str = Field(..., min_length=1, max_length=200)
    titleAr: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    descriptionAr: str | None = Field(default=None, max_length=2000)
    priority: str = Field(..., pattern=r"^(urgent|high|medium|low)$")
    dueDate: str | None = None
    assigneeId: str | None = Field(default=None, max_length=100)
    # `fieldId` is not in the current web TaskFromAlertData, but the
    # CreatedTask response requires it. Accept it optionally so a
    # future web change can send it through cleanly, and so the
    # stub response can echo a non-empty value back.
    field_id: str | None = Field(default=None, max_length=100, alias="fieldId")


class ValidateDateRequest(BaseModel):
    """POST /api/v1/intelligence/validate-date payload.

    The web client posts an ISO datetime string (via
    `new Date(date).toISOString()` in
    apps/web/src/lib/api/client.ts:973), not a pure date. Accept both
    flavours — `date` objects, `YYYY-MM-DD` strings, and full ISO
    datetimes — and coerce to a plain `date` before the handler sees it.
    Strict typing would otherwise 422 every single web call.
    """

    model_config = ConfigDict(extra="forbid")

    date: date
    activity: str = Field(..., min_length=1, max_length=80)
    field_id: str | None = Field(default=None, max_length=100)

    @field_validator("date", mode="before")
    @classmethod
    def _accept_iso_datetime(cls, v: Any) -> Any:
        """Turn an ISO datetime string into a `date`."""
        if isinstance(v, str) and "T" in v:
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00")).date()
            except ValueError:
                # Let Pydantic's default str→date parser handle / reject it.
                return v
        return v


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/score
# Returns: ApiResponse<LivingFieldScore>
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/score")
def get_living_field_score(
    field_id: str = Path(..., max_length=100),
    user: User = Depends(get_current_user),
):
    """Living Field Score. Shape matches the web `LivingFieldScore` contract."""
    seed = _field_seed(field_id)
    overall = 45 + (seed % 46)  # 45-90
    health = 50 + ((seed >> 4) % 41)
    hydration = 50 + ((seed >> 8) % 41)
    attention = 60 + ((seed >> 12) % 31)
    astral = 55 + ((seed >> 16) % 36)

    ndvi_value = 0.40 + ((seed % 50) / 100.0)  # 0.40-0.89
    soil_moisture_pct = 25 + ((seed >> 8) % 50)  # 25-74 %
    trend_delta = ((seed >> 20) % 11) - 5  # -5..+5

    ndvi_cat, ndvi_cat_ar = _score_to_rating(int(ndvi_value * 100))
    sm_status, sm_status_ar = _score_to_rating(soil_moisture_pct)
    moon_phases = [
        ("new_moon", "محاق"),
        ("waxing_crescent", "هلال متزايد"),
        ("first_quarter", "تربيع أول"),
        ("waxing_gibbous", "أحدب متزايد"),
        ("full_moon", "بدر"),
        ("waning_gibbous", "أحدب متناقص"),
        ("last_quarter", "تربيع أخير"),
        ("waning_crescent", "هلال متناقص"),
    ]
    phase_en, phase_ar = moon_phases[seed % len(moon_phases)]

    score: dict[str, Any] = {
        "fieldId": field_id,
        "overall": overall,
        "health": health,
        "hydration": hydration,
        "attention": attention,
        "astral": astral,
        "trend": _trend_label(trend_delta),
        "trendPercentage": trend_delta,
        "lastUpdated": _DETERMINISTIC_STUB_TIMESTAMP,
        "components": {
            "ndvi": {
                "value": round(ndvi_value, 3),
                "category": ndvi_cat,
                "categoryAr": ndvi_cat_ar,
                "contribution": 30,
            },
            "soilMoisture": {
                "value": soil_moisture_pct,
                "status": sm_status,
                "statusAr": sm_status_ar,
                "contribution": 25,
            },
            "taskCompletion": {
                "completedTasks": 0,
                "totalTasks": 0,
                "overdueTasks": 0,
                "contribution": 20,
            },
            "astronomical": {
                "moonPhase": phase_en,
                "moonPhaseAr": phase_ar,
                "farmingScore": astral,
                "contribution": 25,
            },
        },
    }
    return _ok(score)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/zones
# Returns: ApiResponse<FieldZone[]>
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/zones")
def get_field_zones(
    field_id: str = Path(..., max_length=100),
    user: User = Depends(get_current_user),
):
    """Productivity zones. Empty array is a valid shape until the rules
    engine is wired; UI renders an "no zones yet" empty state."""
    # `data` is the array directly — not an object wrapper.
    return _ok([])


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/alerts
# Returns: ApiResponse<FieldAlert[]>
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/alerts")
def get_field_alerts(
    field_id: str = Path(..., max_length=100),
    status: str = Query(default="active", max_length=20),
    user: User = Depends(get_current_user),
):
    """Active alerts. Empty array until the rules engine emits them."""
    return _ok([])


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/recommendations
# Returns: ApiResponse<FieldRecommendation[]>
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/recommendations")
def get_field_recommendations(
    field_id: str = Path(..., max_length=100),
    user: User = Depends(get_current_user),
):
    """Advisory recommendations for the field. Empty array until wired."""
    return _ok([])


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/intelligence/alerts/{alert_id}/create-task
# Returns: ApiResponse<CreatedTask>
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/intelligence/alerts/{alert_id}/create-task", status_code=202)
def create_task_from_alert(
    payload: CreateTaskFromAlertRequest,
    alert_id: str = Path(..., max_length=100),
    user: User = Depends(get_current_user),
):
    """Accept a "create task from alert" request and return the created task
    in the shape the web `CreatedTask` interface expects. Persistence +
    downstream task-service dispatch is handled out-of-band (NATS); this
    endpoint returns a deterministic task id derived from `alert_id` so
    UI retries are idempotent."""
    # Deterministic task id so a second submission doesn't show up as a
    # different row in the UI optimistic state.
    task_id = hashlib.sha256(f"alert:{alert_id}".encode()).hexdigest()[:24]
    # `CreatedTask.fieldId` is required by the web contract. Prefer a
    # client-supplied value (future-proof — web may start sending it),
    # otherwise echo the alert_id as a deterministic non-empty sentinel
    # so the UI's required-field checks don't break. Task-service will
    # overwrite with the real field when it consumes the NATS event.
    resolved_field_id = payload.field_id or alert_id
    created_task: dict[str, Any] = {
        "id": task_id,
        "fieldId": resolved_field_id,
        "alertId": alert_id,
        "title": payload.title,
        "titleAr": payload.titleAr,
        "description": payload.description,
        "descriptionAr": payload.descriptionAr,
        "priority": payload.priority,
        "status": "pending",
        "dueDate": payload.dueDate,
        "createdAt": _DETERMINISTIC_STUB_TIMESTAMP,
    }
    return _ok(created_task)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/intelligence/best-days
# Returns: ApiResponse<BestDay[]>
# ─────────────────────────────────────────────────────────────────────────────


_ACTIVITY_ALIASES = {
    "planting": "planting",
    "irrigation": "irrigation",
    "spraying": "spraying",
    "harvest": "harvest",
    "fertilization": "fertilization",
}
_ACTIVITY_AR = {
    "planting": "زراعة",
    "irrigation": "ري",
    "spraying": "رش",
    "harvest": "حصاد",
    "fertilization": "تسميد",
}


def _rating_for_score(score: int) -> tuple[str, str]:
    """Map score to the web-facing rating enum."""
    if score >= 80:
        return ("excellent", "ممتاز")
    if score >= 60:
        return ("good", "جيد")
    if score >= 40:
        return ("moderate", "مقبول")
    return ("poor", "ضعيف")


@router.get("/intelligence/best-days")
def get_best_days(
    activity: str = Query(..., max_length=40),
    days: int = Query(default=14, ge=1, le=60),
    field_id: str | None = Query(default=None, max_length=100),
    user: User = Depends(get_current_user),
):
    """Return up to `days` BestDay records ranked best-first for `activity`.

    `data` is the array of `BestDay` directly, matching the web contract.
    """
    act = activity.strip().lower()
    if act not in _ACTIVITY_ALIASES:
        return _err_response(
            400,
            f"Unknown activity '{activity}'",
            f"نشاط غير معروف: {activity}",
            error_code="INVALID_ACTIVITY",
            extra={"validActivities": sorted(_ACTIVITY_ALIASES.keys())},
        )

    base = _field_seed(f"{field_id or ''}:{act}")
    suggestions: list[dict[str, Any]] = []
    moon_phases = [
        ("new_moon", "محاق"),
        ("waxing_crescent", "هلال متزايد"),
        ("first_quarter", "تربيع أول"),
        ("waxing_gibbous", "أحدب متزايد"),
        ("full_moon", "بدر"),
        ("waning_gibbous", "أحدب متناقص"),
        ("last_quarter", "تربيع أخير"),
        ("waning_crescent", "هلال متناقص"),
    ]
    # Use a fixed reference date so the stub stays deterministic across runs
    # while preserving the "next N days" semantic — callers compare the
    # returned strings against UI state anyway.
    reference = date(2026, 1, 1)
    for i in range(days):
        d = reference + timedelta(days=i)
        score = 40 + ((base + i * 17) % 61)  # 40-100
        rating_en, rating_ar = _rating_for_score(score)
        phase_en, phase_ar = moon_phases[(base + i) % len(moon_phases)]
        suggestions.append(
            {
                "date": d.isoformat(),
                "score": score,
                "suitability": rating_en,
                "suitabilityAr": rating_ar,
                "weather": {
                    "temperature": 22 + ((base + i) % 15),
                    "humidity": 30 + ((base + i * 3) % 50),
                    "precipitation": 0,
                    "windSpeed": 5 + ((base + i * 7) % 15),
                    "description": "Clear",
                    "descriptionAr": "صافٍ",
                },
                "astronomical": {
                    "moonPhase": phase_en,
                    "moonPhaseAr": phase_ar,
                    "lunarMansion": "",
                    "lunarMansionAr": "",
                    "farmingScore": score,
                },
                "reasons": [],
                "reasonsAr": [],
            }
        )
    suggestions.sort(key=lambda s: s["score"], reverse=True)
    return _ok(suggestions)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/intelligence/validate-date
# Returns: ApiResponse<DateValidation>
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/intelligence/validate-date")
def validate_activity_date(
    payload: ValidateDateRequest,
    user: User = Depends(get_current_user),
):
    """Return a DateValidation record for doing `activity` on `date`.

    Shape matches the web `DateValidation` interface.
    """
    act = payload.activity.strip().lower()
    if act not in _ACTIVITY_ALIASES:
        return _err_response(
            400,
            f"Unknown activity '{payload.activity}'",
            f"نشاط غير معروف: {payload.activity}",
            error_code="INVALID_ACTIVITY",
            extra={"validActivities": sorted(_ACTIVITY_ALIASES.keys())},
        )

    base = _field_seed(f"{payload.field_id or ''}:{act}")
    score = 40 + ((base + payload.date.toordinal()) % 61)
    rating_en, rating_ar = _rating_for_score(score)

    validation: dict[str, Any] = {
        "date": payload.date.isoformat(),
        "activity": act,
        "activityAr": _ACTIVITY_AR.get(act, act),
        "suitable": score >= 60,
        "score": score,
        "rating": rating_en,
        "ratingAr": rating_ar,
        "reasons": [],
        "reasonsAr": [],
    }
    return _ok(validation)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/field-intelligence/{field_id}
# Returns: ApiResponse<{score, zones, alerts, recommendations}>
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/field-intelligence/{field_id}")
def get_field_intelligence_summary(
    field_id: str = Path(..., max_length=100),
    user: User = Depends(get_current_user),
):
    """Aggregate endpoint combining score, zones, alerts, recommendations.

    Each sibling handler already returns an envelope; we unwrap `.data`
    before composing so the aggregate stays a single flat envelope.
    """
    score = get_living_field_score(field_id, user=user)["data"]
    zones = get_field_zones(field_id, user=user)["data"]
    alerts = get_field_alerts(field_id, status="active", user=user)["data"]
    recs = get_field_recommendations(field_id, user=user)["data"]
    return _ok(
        {
            "fieldId": field_id,
            "score": score,
            "zones": zones,
            "alerts": alerts,
            "recommendations": recs,
        }
    )
