# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration API Router - موجّه API المعايرة
=============================================
FastAPI router providing Calibration Engine endpoints.

Endpoints:
  POST /calibration/runs                  – Create calibration run
  GET  /calibration/runs                  – List runs for field+season
  GET  /calibration/runs/{run_id}         – Get run details
  GET  /calibration/parameters            – List parameter sets
  GET  /calibration/parameters/active     – Get active parameter set
  POST /calibration/parameters/{id}/activate – Promote candidate → active
  GET  /calibration/settings              – Feature flag / config status
"""

from __future__ import annotations

import json as _json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as http_status
from pydantic import BaseModel, Field

from shared.calibration.errors import CalibrationNotEnabled, InsufficientObservations
from shared.calibration.fingerprint import fingerprint_dataset
from shared.calibration.repository import CalibrationRepository
from shared.calibration.types import (
    CalibrationObservation,
    CalibrationTarget,
    TimestampedObservation,
)
from shared.process_models.uncertainty import QualityFlag, ValueWithUncertainty

from .calibration_settings import CalibrationSettings

logger = structlog.get_logger()

# Authentication (graceful fallback)
try:
    from shared.auth.dependencies import get_current_user

    _AUTH = True
except ImportError:
    _AUTH = False

    async def get_current_user():  # type: ignore[misc]
        return None


# ---------------------------------------------------------------------------
# DTOs (Pydantic request/response models)
# ---------------------------------------------------------------------------


class ObsDTO(BaseModel):
    """Single observation in a target. رصد واحد في هدف."""

    t: str = Field(..., description="ISO date YYYY-MM-DD")
    variable: str = Field(..., description="LAI | biomass | soil_moisture")
    value: float
    std: float = Field(ge=0, default=0.1, description="Observation std dev (σ)")
    quality: str = Field(default="observed", description="QualityFlag value")
    quality_score: float = Field(ge=0, le=1, default=0.7)
    source_ref: dict[str, Any] = Field(default_factory=dict)


class TargetDTO(BaseModel):
    """Calibration target (one per variable). هدف المعايرة."""

    variable: str
    weight: float = Field(gt=0, default=1.0)
    min_quality_score: float = Field(ge=0, le=1, default=0.5)
    observations: list[ObsDTO]


class CreateRunDTO(BaseModel):
    """Request body for POST /calibration/runs."""

    field_id: str
    season_id: str
    crop_type: str = "wheat"
    model_name: str = "crop_growth"
    model_version: str = "v16"
    method: str = "bayes_opt"
    targets: list[TargetDTO]


class ActivateDTO(BaseModel):
    """Request body for POST /calibration/parameters/{id}/activate."""

    reason: str = Field(..., min_length=3, description="Activation justification")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_settings = CalibrationSettings()


def _get_repo(request: Request) -> CalibrationRepository:
    pool = getattr(getattr(request.app, "state", None), "db_pool", None)
    return CalibrationRepository(db_pool=pool)


def _get_tenant_id(request: Request) -> str:
    """Extract tenant_id from JWT or header. استخراج معرف المستأجر."""
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "tenant_id"):
        return str(user.tenant_id)
    return request.headers.get("x-tenant-id", "default")


def _get_actor(request: Request) -> str:
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return str(user.id)
    return "system"


def _get_nats(request: Request) -> Any:
    return getattr(getattr(request.app, "state", None), "nc", None)


async def _publish_calibration_event(nats: Any, subject: str, payload: dict[str, Any]) -> None:
    """Publish a calibration lifecycle event to NATS."""
    if nats is None:
        return
    try:
        payload["ts"] = datetime.now(UTC).isoformat()
        await nats.publish(subject, _json.dumps(payload).encode())
    except Exception as exc:
        logger.warning("calibration_nats_publish_failed", subject=subject, error=str(exc))


def _dto_to_targets(dtos: list[TargetDTO]) -> list[CalibrationTarget]:
    """Convert DTO list to domain CalibrationTarget list."""
    out: list[CalibrationTarget] = []
    for t in dtos:
        obs: list[TimestampedObservation] = []
        for o in t.observations:
            obs.append(
                TimestampedObservation(
                    t=o.t,
                    variable=o.variable,  # type: ignore[arg-type]
                    obs=ValueWithUncertainty(
                        value=o.value,
                        std=o.std,
                        quality=QualityFlag(o.quality),
                    ),
                    source_ref=o.source_ref,
                    quality_score=o.quality_score,
                )
            )
        out.append(
            CalibrationTarget(
                variable=t.variable,
                observations=obs,
                weight=t.weight,
                min_quality_score=t.min_quality_score,
            )
        )
    return out


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/calibration",
    tags=["Calibration"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/settings")
async def get_settings():
    """Return current calibration configuration. إرجاع إعدادات المعايرة الحالية."""
    return _settings.as_dict()


@router.post("/runs", status_code=http_status.HTTP_201_CREATED)
async def create_run(
    payload: CreateRunDTO,
    request: Request,
    repo: CalibrationRepository = Depends(_get_repo),
):
    """
    Create a new calibration run.
    إنشاء تشغيل معايرة جديد.

    The run is created with status ``queued``.  A background worker
    will pick it up and transition it through ``running → succeeded|failed``.
    """
    if not _settings.enabled:
        raise CalibrationNotEnabled()

    tenant_id = _get_tenant_id(request)
    targets = _dto_to_targets(payload.targets)

    # Validate minimum observations
    for tgt in targets:
        if len(tgt.observations) < _settings.min_observations:
            raise InsufficientObservations(
                variable=tgt.variable,
                got=len(tgt.observations),
                minimum=_settings.min_observations,
            )

    # Fingerprint
    fp_payload = {
        "tenant_id": tenant_id,
        "field_id": payload.field_id,
        "season_id": payload.season_id,
        "model_name": payload.model_name,
        "model_version": payload.model_version,
        "targets": [
            {
                "variable": t.variable,
                "weight": t.weight,
                "min_quality_score": t.min_quality_score,
                "obs_refs": [o.source_ref for o in t.observations],
            }
            for t in targets
        ],
    }
    dataset_fp = fingerprint_dataset(fp_payload)

    run_id = await repo.create_run(
        {
            "tenant_id": tenant_id,
            "field_id": payload.field_id,
            "season_id": payload.season_id,
            "crop_type": payload.crop_type,
            "model_name": payload.model_name,
            "model_version": payload.model_version,
            "method": payload.method,
            "dataset_fingerprint": dataset_fp,
        }
    )

    logger.info(
        "calibration_run_created",
        run_id=run_id,
        tenant_id=tenant_id,
        field_id=payload.field_id,
        method=payload.method,
        n_targets=len(targets),
    )

    # Publish NATS event
    from shared.events.subjects import SAHOOL_CALIBRATION_RUN_QUEUED

    nats = _get_nats(request)
    await _publish_calibration_event(
        nats,
        SAHOOL_CALIBRATION_RUN_QUEUED,
        {
            "run_id": run_id,
            "tenant_id": tenant_id,
            "field_id": payload.field_id,
            "season_id": payload.season_id,
            "method": payload.method,
            "dataset_fingerprint": dataset_fp,
        },
    )

    return {
        "run_id": run_id,
        "status": "queued",
        "tenant_id": tenant_id,
        "field_id": payload.field_id,
        "season_id": payload.season_id,
        "dataset_fingerprint": dataset_fp,
    }


@router.get("/runs")
async def list_runs(
    field_id: str = Query(...),
    season_id: str = Query(...),
    model_name: str = Query("crop_growth"),
    limit: int = Query(20, ge=1, le=100),
    request: Request = None,  # type: ignore[assignment]
    repo: CalibrationRepository = Depends(_get_repo),
):
    """List calibration runs for a field+season. قائمة تشغيلات المعايرة."""
    tenant_id = _get_tenant_id(request)
    runs = await repo.list_runs(tenant_id, field_id, season_id, model_name=model_name, limit=limit)
    return {"runs": runs, "count": len(runs)}


@router.get("/runs/{run_id}")
async def get_run(
    run_id: str,
    repo: CalibrationRepository = Depends(_get_repo),
):
    """Get details of a single calibration run. تفاصيل تشغيل معايرة."""
    row = await repo.get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Calibration run not found")
    return row


@router.get("/parameters")
async def list_parameter_sets(
    field_id: str = Query(...),
    season_id: str = Query(...),
    model_name: str = Query("crop_growth"),
    limit: int = Query(20, ge=1, le=100),
    request: Request = None,  # type: ignore[assignment]
    repo: CalibrationRepository = Depends(_get_repo),
):
    """List parameter sets for a field+season. قائمة مجموعات المعاملات."""
    tenant_id = _get_tenant_id(request)
    sets = await repo.list_parameter_sets(tenant_id, field_id, season_id, model_name=model_name, limit=limit)
    return {"parameter_sets": sets, "count": len(sets)}


@router.get("/parameters/active")
async def get_active_parameters(
    field_id: str = Query(...),
    season_id: str = Query(...),
    model_name: str = Query("crop_growth"),
    request: Request = None,  # type: ignore[assignment]
    repo: CalibrationRepository = Depends(_get_repo),
):
    """Get the currently active parameter set. المعاملات النشطة حاليًا."""
    tenant_id = _get_tenant_id(request)
    ps = await repo.get_active_parameter_set(tenant_id, field_id, season_id, model_name)
    if not ps:
        raise HTTPException(status_code=404, detail="No active parameter set found")
    return ps


@router.post("/parameters/{set_id}/activate")
async def activate_parameter_set(
    set_id: str,
    body: ActivateDTO,
    field_id: str = Query(...),
    season_id: str = Query(...),
    model_name: str = Query("crop_growth"),
    request: Request = None,  # type: ignore[assignment]
    repo: CalibrationRepository = Depends(_get_repo),
):
    """
    Promote a candidate parameter set to active.
    ترقية مجموعة معاملات مرشحة إلى نشطة.

    This deprecates the previously active set and writes an audit entry.
    """
    if not _settings.enabled:
        raise CalibrationNotEnabled()

    tenant_id = _get_tenant_id(request)
    actor = _get_actor(request)

    await repo.activate_parameter_set(
        tenant_id=tenant_id,
        field_id=field_id,
        season_id=season_id,
        model_name=model_name,
        new_set_id=set_id,
        actor=actor,
        reason=body.reason,
    )

    logger.info(
        "parameter_set_activated_via_api",
        set_id=set_id,
        tenant_id=tenant_id,
        field_id=field_id,
        actor=actor,
    )

    # Publish NATS event
    from shared.events.subjects import SAHOOL_CALIBRATION_PARAMS_ACTIVATED

    nats = _get_nats(request)
    await _publish_calibration_event(
        nats,
        SAHOOL_CALIBRATION_PARAMS_ACTIVATED,
        {
            "parameter_set_id": set_id,
            "tenant_id": tenant_id,
            "field_id": field_id,
            "season_id": season_id,
            "model_name": model_name,
            "actor": actor,
            "reason": body.reason,
        },
    )

    return {"status": "activated", "parameter_set_id": set_id}
