# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Digital Twin API Router - موجّه API التوأم الرقمي
===================================================
FastAPI router providing the Digital Twin endpoints for crop-intelligence-service.

Endpoints:
  POST /fields/{field_id}/twin/step
    – Run one daily twin simulation step for a field

  GET  /fields/{field_id}/twin/state
    – Retrieve daily states (with optional date range)

  POST /fields/{field_id}/observations
    – Ingest NDVI / LAI / sensor observations (triggers assimilation)

  GET  /fields/{field_id}/irrigation/recommendation
    – Retrieve or compute irrigation recommendation for a day

All endpoints:
  • Respect feature flags (PROCESS_MODELS_ENABLED, ASSIMILATION_ENABLED, …)
  • Require JWT authentication (inherits auth from parent app)
  • Fall back gracefully when DB is not available
  • Publish NATS events on state changes
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone, UTC
from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status as http_status
from pydantic import BaseModel, Field

from shared.digital_twin.assimilation import AssimilationEngine
from shared.digital_twin.decisions import DecisionEngine
from shared.digital_twin.feature_flags import DigitalTwinFlags
from shared.digital_twin.models import (
    AssimilationFlag,
    FieldDailyState,
    FieldObservation,
    IrrigationRecommendation,
    ObservationSource,
    ObservationType,
)
from shared.digital_twin.pipeline import TwinPipeline
from shared.digital_twin.repository import TwinRepository
from shared.process_models.models import (
    CropParameters,
    CropType,
    DailyWeather,
    SoilProfile,
    SoilTextureClass,
)

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User as AuthUser

    _AUTH_AVAILABLE = True
except ImportError:
    _AUTH_AVAILABLE = False

    class AuthUser:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str = "default"

    async def get_current_user() -> AuthUser:  # type: ignore[misc]
        return AuthUser()

router = APIRouter(prefix="/fields", tags=["Digital Twin"], dependencies=[Depends(get_current_user)])
_flags = DigitalTwinFlags()


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


def _get_repo(request: Request) -> TwinRepository:
    pool = getattr(getattr(request.app, "state", None), "db_pool", None)
    return TwinRepository(db_pool=pool)


def _get_nats(request: Request) -> Any:
    return getattr(getattr(request.app, "state", None), "nc", None)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class WeatherIn(BaseModel):
    """Daily weather input for the twin step. بيانات الطقس اليومية."""

    tmax_c: float = Field(..., description="Maximum temperature (°C)")
    tmin_c: float = Field(..., description="Minimum temperature (°C)")
    solar_radiation_mj_m2: float = Field(
        default=18.0, description="Solar radiation (MJ m⁻²)"
    )
    relative_humidity_pct: float = Field(default=60.0, ge=0, le=100)
    wind_speed_m_s: float = Field(default=2.0, ge=0)
    precipitation_mm: float = Field(default=0.0, ge=0)


class SoilIn(BaseModel):
    """Soil physical properties input. خصائص التربة الفيزيائية."""

    field_capacity_mm_per_m: float = Field(default=300.0)
    wilting_point_mm_per_m: float = Field(default=150.0)
    saturation_mm_per_m: float = Field(default=450.0)
    depth_m: float = Field(default=0.60)
    texture: str = Field(default="loam")


class TwinStepIn(BaseModel):
    """Request body for daily twin step. جسم طلب الخطوة اليومية."""

    day: date | None = None
    tenant_id: UUID
    weather: WeatherIn
    crop_type: str = Field(default="wheat")
    irrigation_applied_mm: float = Field(default=0.0, ge=0)
    nitrogen_applied_kg_ha: float = Field(default=0.0, ge=0)
    lat_deg: float = Field(default=15.0)
    elevation_m: float = Field(default=100.0)
    soil: SoilIn = Field(default_factory=SoilIn)
    taw_mm: float = Field(default=180.0, description="Total available water (mm)")


class ObservationIn(BaseModel):
    """Single field observation for ingestion. رصد ميداني للإدخال."""

    ts: datetime | None = None
    source: str = Field(default="sentinel-2")
    obs_type: str  # ndvi | lai | soil_moisture | …
    value: float
    quality: float = Field(default=0.7, ge=0, le=1)
    meta: dict[str, Any] = Field(default_factory=dict)


class ObservationsIn(BaseModel):
    """Batch observation ingestion request. طلب إدخال دفعة من الأرصاد."""

    tenant_id: UUID
    observations: list[ObservationIn]


# ---------------------------------------------------------------------------
# POST /fields/{field_id}/twin/step
# ---------------------------------------------------------------------------


@router.post(
    "/{field_id}/twin/step",
    response_model=dict,
    summary="Run daily twin step | تشغيل خطوة يومية للتوأم الرقمي",
)
async def twin_step(
    field_id: UUID,
    body: TwinStepIn,
    request: Request,
) -> dict:
    """
    Execute one daily simulation step for a field.
    تنفيذ خطوة محاكاة يومية لحقل.

    Calls: ET₀ → Soil Water Balance → Crop Growth → persist → NATS event.
    """
    if not _flags.process_models_enabled:
        raise HTTPException(
            http_status.HTTP_503_SERVICE_UNAVAILABLE, "process_models_enabled=false"
        )

    step_day = body.day or date.today()

    # Build domain objects from request
    weather = DailyWeather(
        date=step_day,
        tmax_c=body.weather.tmax_c,
        tmin_c=body.weather.tmin_c,
        solar_radiation_mj_m2=body.weather.solar_radiation_mj_m2,
        relative_humidity_pct=body.weather.relative_humidity_pct,
        wind_speed_m_s=body.weather.wind_speed_m_s,
        precipitation_mm=body.weather.precipitation_mm,
    )

    texture_map = {t.value: t for t in SoilTextureClass}
    soil = SoilProfile(
        field_capacity_mm_per_m=body.soil.field_capacity_mm_per_m,
        wilting_point_mm_per_m=body.soil.wilting_point_mm_per_m,
        saturation_mm_per_m=body.soil.saturation_mm_per_m,
        depth_m=body.soil.depth_m,
        texture=texture_map.get(body.soil.texture, SoilTextureClass.LOAM),
    )

    crop_map = {t.value: t for t in CropType}
    crop = CropParameters(crop_type=crop_map.get(body.crop_type, CropType.WHEAT))

    repo = _get_repo(request)
    nats = _get_nats(request)

    pipeline = TwinPipeline(repo=repo, nats_client=nats)
    state = await pipeline.step(
        tenant_id=body.tenant_id,
        field_id=field_id,
        day=step_day,
        weather=weather,
        soil=soil,
        crop=crop,
        irrigation_applied_mm=body.irrigation_applied_mm,
        nitrogen_applied_kg_ha=body.nitrogen_applied_kg_ha,
        lat_deg=body.lat_deg,
        elevation_m=body.elevation_m,
    )

    # Optional assimilation pass
    if _flags.assimilation_enabled:
        assimilator = AssimilationEngine(repo=repo)
        state = await assimilator.assimilate(state, crop_type=body.crop_type)
        await repo.save_state(state)

    # Auto-generate irrigation recommendation
    decision = DecisionEngine(repo=repo, nats_client=nats)
    rec = await decision.recommend_irrigation(state, taw_mm=body.taw_mm)
    await repo.save_recommendation(rec)

    # Publish observation-ingested event for field state
    await _publish_observation_ingested(
        nats=nats,
        tenant_id=body.tenant_id,
        field_id=field_id,
        obs_type="state_updated",
        value=state.depletion_mm or 0.0,
    )

    return {
        "field_id": str(field_id),
        "day": step_day.isoformat(),
        "state": state.model_dump(mode="json"),
        "irrigation_recommendation": rec.model_dump(mode="json"),
    }


# ---------------------------------------------------------------------------
# GET /fields/{field_id}/twin/state
# ---------------------------------------------------------------------------


@router.get(
    "/{field_id}/twin/state",
    response_model=list,
    summary="Get field twin state history | جلب سجل حالة التوأم",
)
async def get_twin_state(
    field_id: UUID,
    tenant_id: UUID = Query(...),
    from_date: date = Query(default=None),
    to_date: date = Query(default=None),
    request: Request = None,
) -> list:
    """
    Retrieve FieldDailyState records for a date range.
    استرجاع سجلات الحالة اليومية لنطاق زمني.
    """
    today = date.today()
    from_date = from_date or today
    to_date = to_date or today

    if (to_date - from_date).days > 365:
        raise HTTPException(
            http_status.HTTP_400_BAD_REQUEST, "Date range exceeds 365 days"
        )

    repo = _get_repo(request)
    states = await repo.get_states(tenant_id, field_id, from_date, to_date)
    return [s.model_dump(mode="json") for s in states]


# ---------------------------------------------------------------------------
# POST /fields/{field_id}/observations
# ---------------------------------------------------------------------------


@router.post(
    "/{field_id}/observations",
    summary="Ingest field observations | إدخال أرصاد ميدانية",
)
async def ingest_observations(
    field_id: UUID,
    body: ObservationsIn,
    request: Request,
) -> dict:
    """
    Ingest NDVI / LAI / soil-moisture observations.
    إدخال أرصاد NDVI / LAI / رطوبة التربة.

    Persists each observation and publishes NATS event per record.
    If assimilation is enabled, re-runs assimilation on today's state.
    """
    repo = _get_repo(request)
    nats = _get_nats(request)
    saved = 0
    errors = []

    obs_type_map = {t.value: t for t in ObservationType}
    source_map = {s.value: s for s in ObservationSource}

    for raw in body.observations:
        try:
            obs = FieldObservation(
                tenant_id=body.tenant_id,
                field_id=field_id,
                ts=raw.ts or datetime.now(UTC),
                source=source_map.get(raw.source, ObservationSource.MANUAL),
                obs_type=obs_type_map.get(raw.obs_type, ObservationType.NDVI),
                value=raw.value,
                quality=raw.quality,
                meta=raw.meta,
            )
            await repo.save_observation(obs)
            await _publish_observation_ingested(
                nats=nats,
                tenant_id=body.tenant_id,
                field_id=field_id,
                obs_type=obs.obs_type.value,
                value=obs.value,
            )
            saved += 1
        except Exception as exc:
            errors.append(str(exc))

    # If assimilation enabled, re-correct today's state
    if _flags.assimilation_enabled and saved > 0:
        today_state = await repo.get_state(body.tenant_id, field_id, date.today())
        if today_state:
            assimilator = AssimilationEngine(repo=repo)
            corrected = await assimilator.assimilate(today_state)
            await repo.save_state(corrected)

    return {"saved": saved, "errors": errors, "field_id": str(field_id)}


# ---------------------------------------------------------------------------
# GET /fields/{field_id}/irrigation/recommendation
# ---------------------------------------------------------------------------


@router.get(
    "/{field_id}/irrigation/recommendation",
    summary="Get irrigation recommendation | جلب توصية الري",
)
async def get_irrigation_recommendation(
    field_id: UUID,
    tenant_id: UUID = Query(...),
    day: date = Query(default=None),
    taw_mm: float = Query(default=180.0),
    request: Request = None,
) -> dict:
    """
    Return the irrigation recommendation for a field-day.
    إرجاع توصية الري ليوم حقل معين.

    If no recommendation exists for the day, compute one from the latest state.
    """
    target_day = day or date.today()
    repo = _get_repo(request)
    nats = _get_nats(request)

    # Check if already stored
    rec = await repo.get_recommendation(tenant_id, field_id, target_day)
    if rec:
        return rec.model_dump(mode="json")

    # Try to compute from state
    state = await repo.get_state(tenant_id, field_id, target_day)
    if state is None:
        raise HTTPException(
            http_status.HTTP_404_NOT_FOUND,
            f"No twin state found for field {field_id} on {target_day}. Run POST /fields/{{field_id}}/twin/step first.",
        )

    decision = DecisionEngine(repo=repo, nats_client=nats)
    rec = await decision.recommend_irrigation(state, taw_mm=taw_mm)
    await repo.save_recommendation(rec)
    return rec.model_dump(mode="json")


# ---------------------------------------------------------------------------
# GET /fields/{field_id}/twin/flags
# ---------------------------------------------------------------------------


@router.get(
    "/{field_id}/twin/flags",
    summary="Get feature flags | جلب رايات الميزات",
)
async def get_flags(field_id: UUID) -> dict:
    """Return current feature flags for the Digital Twin module."""
    return {"field_id": str(field_id), "flags": _flags.as_dict()}


# ---------------------------------------------------------------------------
# NATS helper
# ---------------------------------------------------------------------------


async def _publish_observation_ingested(
    nats: Any,
    tenant_id: UUID,
    field_id: UUID,
    obs_type: str,
    value: float,
) -> None:
    if nats is None:
        return
    try:
        from shared.events.subjects import SAHOOL_FIELD_OBSERVATION_INGESTED

        payload = json.dumps(
            {
                "tenant_id": str(tenant_id),
                "field_id": str(field_id),
                "ts": datetime.now(UTC).isoformat(),
                "obs_type": obs_type,
                "value": value,
            }
        ).encode()
        await nats.publish(SAHOOL_FIELD_OBSERVATION_INGESTED, payload)
    except Exception as exc:
        logger.warning("twin_router_nats_failed", error=str(exc))
