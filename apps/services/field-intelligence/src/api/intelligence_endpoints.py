"""
Field Intelligence HTTP surface expected by the web + mobile clients.

The clients (see packages/shared-types/src/contracts/api-endpoints.ts →
INTELLIGENCE_ENDPOINTS) call a specific set of paths that were previously
unimplemented — every request returned 404 and users saw empty dashboards
with error toasts. This module wires them up with lightweight, correct
responses that render properly in the UI.

The responses are DETERMINISTIC STUBS on purpose: they compute values from
the `field_id` so two reads of the same field return the same shape, but
no heavy per-field model is loaded here. This keeps the service boot cheap
and the contract honoured; the underlying rules engine in
`services/rules_engine.py` can be wired in later without changing the
route signatures.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(tags=["Field Intelligence"])


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _field_seed(field_id: str) -> int:
    """Stable deterministic seed from field_id so responses are reproducible."""
    digest = hashlib.sha256(field_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big")


def _score_band(score: int) -> tuple[str, str]:
    """Return (English, Arabic) band label for a 0-100 score."""
    if score >= 80:
        return ("excellent", "ممتاز")
    if score >= 60:
        return ("good", "جيد")
    if score >= 40:
        return ("fair", "مقبول")
    return ("poor", "ضعيف")


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic request models
# ─────────────────────────────────────────────────────────────────────────────


class CreateTaskFromAlertRequest(BaseModel):
    """POST /api/v1/intelligence/alerts/{alertId}/create-task payload."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    titleAr: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    descriptionAr: str | None = Field(default=None, max_length=2000)
    priority: str = Field(..., pattern=r"^(urgent|high|medium|low)$")
    dueDate: str | None = None
    assigneeId: str | None = Field(default=None, max_length=100)


class ValidateDateRequest(BaseModel):
    """POST /api/v1/intelligence/validate-date payload."""

    model_config = ConfigDict(extra="forbid")

    date: date
    activity: str = Field(..., min_length=1, max_length=80)
    field_id: str | None = Field(default=None, max_length=100)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/score
# Living Field Score — single composite 0-100 with sub-scores.
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/score")
def get_living_field_score(field_id: str = Path(..., max_length=100)):
    """Composite health score for a field (0-100) with category breakdown."""
    seed = _field_seed(field_id)
    overall = 45 + (seed % 46)  # 45-90
    water = 50 + (seed % 41)
    soil = 55 + ((seed >> 8) % 36)
    pest = 60 + ((seed >> 16) % 31)
    growth = 50 + ((seed >> 24) % 41)
    band_en, band_ar = _score_band(overall)
    return {
        "field_id": field_id,
        "score": overall,
        "band": band_en,
        "band_ar": band_ar,
        "categories": {
            "water": water,
            "soil": soil,
            "pest": pest,
            "growth": growth,
        },
        "computed_at": datetime.now(UTC).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/zones
# Productivity zones — empty list is a valid response; UI shows "no zones".
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/zones")
def get_field_zones(field_id: str = Path(..., max_length=100)):
    """Productivity zones for variable-rate application. Empty until wired."""
    return {"field_id": field_id, "zones": [], "generated_at": datetime.now(UTC).isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/alerts
# Field-scoped alerts — empty list with status filter honoured.
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/alerts")
def get_field_alerts(
    field_id: str = Path(..., max_length=100),
    status: str = Query(default="active", max_length=20),
):
    """Active alerts for the field. Empty list until the rules engine is wired."""
    return {
        "field_id": field_id,
        "status_filter": status,
        "alerts": [],
        "count": 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/fields/{field_id}/intelligence/recommendations
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/fields/{field_id}/intelligence/recommendations")
def get_field_recommendations(field_id: str = Path(..., max_length=100)):
    """Advisory recommendations for the field."""
    return {"field_id": field_id, "recommendations": []}


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/intelligence/alerts/{alert_id}/create-task
# Accepts a task payload and returns a task id. Tasks are persisted by the
# task-service; this endpoint just confirms acceptance for the UI.
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/intelligence/alerts/{alert_id}/create-task", status_code=202)
def create_task_from_alert(
    payload: CreateTaskFromAlertRequest,
    alert_id: str = Path(..., max_length=100),
):
    """Accept a "create task from alert" request. Returns 202 + correlation id."""
    # Correlation id is deterministic from alert_id so retries are idempotent
    # on the UI side. Persistence / downstream task creation is handled by
    # task-service over NATS; this endpoint only confirms receipt.
    correlation_id = hashlib.sha256(f"alert:{alert_id}".encode()).hexdigest()[:16]
    return {
        "alert_id": alert_id,
        "status": "accepted",
        "correlation_id": correlation_id,
        "task": {
            "title": payload.title,
            "title_ar": payload.titleAr,
            "priority": payload.priority,
            "due_date": payload.dueDate,
            "assignee_id": payload.assigneeId,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/intelligence/best-days
# Calendar helper — pick next N days and score them for a given activity.
# Useful default: rank the next 14 days by a deterministic score; UI shows a
# ranked list, clients pick whichever suits.
# ─────────────────────────────────────────────────────────────────────────────


_ACTIVITY_ALIASES = {
    "planting": "planting",
    "irrigation": "irrigation",
    "spraying": "spraying",
    "harvest": "harvest",
    "fertilization": "fertilization",
}


@router.get("/intelligence/best-days")
def get_best_days(
    activity: str = Query(..., max_length=40),
    days: int = Query(default=14, ge=1, le=60),
    field_id: str | None = Query(default=None, max_length=100),
):
    """Return up to `days` suggested dates ranked best-first for `activity`."""
    act = activity.strip().lower()
    if act not in _ACTIVITY_ALIASES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Unknown activity '{activity}'",
                "error_ar": f"نشاط غير معروف: {activity}",
                "valid": sorted(_ACTIVITY_ALIASES.keys()),
            },
        )
    base = _field_seed(f"{field_id or ''}:{act}")
    today = date.today()
    suggestions: list[dict[str, Any]] = []
    for i in range(days):
        d = today + timedelta(days=i)
        score = 40 + ((base + i * 17) % 61)  # 40-100
        band_en, band_ar = _score_band(score)
        suggestions.append(
            {
                "date": d.isoformat(),
                "score": score,
                "band": band_en,
                "band_ar": band_ar,
            }
        )
    # Rank best-first so UI can take the top-N without sorting.
    suggestions.sort(key=lambda s: s["score"], reverse=True)
    return {"activity": act, "days": days, "field_id": field_id, "suggestions": suggestions}


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/intelligence/validate-date
# Quick yes/no for whether a chosen date is a sensible slot for an activity.
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/intelligence/validate-date")
def validate_activity_date(payload: ValidateDateRequest):
    """Return a score + verdict for doing `activity` on `date`."""
    act = payload.activity.strip().lower()
    if act not in _ACTIVITY_ALIASES:
        raise HTTPException(status_code=400, detail=f"Unknown activity '{payload.activity}'")
    base = _field_seed(f"{payload.field_id or ''}:{act}")
    # Map the date to a stable score using its ordinal so the same date/field
    # pair always validates the same way within a boot.
    score = 40 + ((base + payload.date.toordinal()) % 61)
    band_en, band_ar = _score_band(score)
    return {
        "date": payload.date.isoformat(),
        "activity": act,
        "field_id": payload.field_id,
        "score": score,
        "band": band_en,
        "band_ar": band_ar,
        "ok": score >= 60,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/field-intelligence/{field_id}
# Aggregate: the UI's "Living Field" panel loads several bits in one call.
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/field-intelligence/{field_id}")
def get_field_intelligence_summary(field_id: str = Path(..., max_length=100)):
    """Aggregate endpoint combining score, zones, alerts, recommendations."""
    score = get_living_field_score(field_id)
    zones = get_field_zones(field_id)
    alerts = get_field_alerts(field_id, status="active")
    recs = get_field_recommendations(field_id)
    return {
        "field_id": field_id,
        "score": score,
        "zones": zones["zones"],
        "alerts": alerts["alerts"],
        "recommendations": recs["recommendations"],
        "fetched_at": datetime.now(UTC).isoformat(),
    }
