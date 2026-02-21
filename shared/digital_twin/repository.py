# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Digital Twin Repository - مستودع التوأم الرقمي
================================================
asyncpg-backed persistence for FieldDailyState, FieldObservation and
IrrigationRecommendation with transparent in-memory fallback when no
database connection is available (mirrors existing SAHOOL service pattern).

Tables are created by:  shared/digital_twin/migrations/001_digital_twin_tables.sql
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime
from typing import Any
from uuid import UUID

import structlog

from shared.digital_twin.models import (
    AssimilationFlag,
    FieldDailyState,
    FieldObservation,
    IrrigationRecommendation,
    ObservationType,
)

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# In-memory fallback storage (used when DB pool is None)
# ---------------------------------------------------------------------------
_mem_states: dict[tuple, FieldDailyState] = {}  # (tenant_id, field_id, day) → state
_mem_observations: dict[tuple, list[FieldObservation]] = defaultdict(
    list
)  # (tid, fid) → obs list
_mem_recommendations: dict[tuple, IrrigationRecommendation] = (
    {}
)  # (tid, fid, day) → rec


# ---------------------------------------------------------------------------
# SQL queries
# ---------------------------------------------------------------------------

_SQL_UPSERT_STATE = """
INSERT INTO field_daily_state (
    id, tenant_id, field_id, day,
    et0_mm, etc_mm,
    phenology_stage, gdd_cum, lai, biomass_kg_ha, root_depth_m,
    soil_water_mm, depletion_mm, water_stress, n_stress,
    runoff_mm, deep_perc_mm,
    rainfall_mm, irrigation_applied_mm, nitrogen_applied_kg_ha,
    confidence, assimilation_flags, notes,
    created_at, updated_at
) VALUES (
    $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25
)
ON CONFLICT (tenant_id, field_id, day) DO UPDATE SET
    et0_mm = EXCLUDED.et0_mm,
    etc_mm = EXCLUDED.etc_mm,
    phenology_stage = EXCLUDED.phenology_stage,
    gdd_cum = EXCLUDED.gdd_cum,
    lai = EXCLUDED.lai,
    biomass_kg_ha = EXCLUDED.biomass_kg_ha,
    root_depth_m = EXCLUDED.root_depth_m,
    soil_water_mm = EXCLUDED.soil_water_mm,
    depletion_mm = EXCLUDED.depletion_mm,
    water_stress = EXCLUDED.water_stress,
    n_stress = EXCLUDED.n_stress,
    runoff_mm = EXCLUDED.runoff_mm,
    deep_perc_mm = EXCLUDED.deep_perc_mm,
    rainfall_mm = EXCLUDED.rainfall_mm,
    irrigation_applied_mm = EXCLUDED.irrigation_applied_mm,
    nitrogen_applied_kg_ha = EXCLUDED.nitrogen_applied_kg_ha,
    confidence = EXCLUDED.confidence,
    assimilation_flags = EXCLUDED.assimilation_flags,
    notes = EXCLUDED.notes,
    updated_at = EXCLUDED.updated_at
"""

_SQL_GET_STATE = """
SELECT * FROM field_daily_state
WHERE tenant_id=$1 AND field_id=$2 AND day=$3
"""

_SQL_GET_STATES_RANGE = """
SELECT * FROM field_daily_state
WHERE tenant_id=$1 AND field_id=$2 AND day BETWEEN $3 AND $4
ORDER BY day ASC
"""

_SQL_INSERT_OBSERVATION = """
INSERT INTO field_observation
    (id, tenant_id, field_id, ts, source, obs_type, value, quality, meta, created_at)
VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
"""

_SQL_GET_OBSERVATIONS = """
SELECT * FROM field_observation
WHERE tenant_id=$1 AND field_id=$2 AND obs_type=$3
  AND ts >= NOW() - ($4 || ' days')::interval
ORDER BY ts DESC
"""

_SQL_UPSERT_RECOMMENDATION = """
INSERT INTO irrigation_recommendation
    (id, tenant_id, field_id, day, recommended_mm, reason_codes, explanation, confidence, created_at)
VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
ON CONFLICT (tenant_id, field_id, day) DO UPDATE SET
    recommended_mm = EXCLUDED.recommended_mm,
    reason_codes   = EXCLUDED.reason_codes,
    explanation    = EXCLUDED.explanation,
    confidence     = EXCLUDED.confidence
"""

_SQL_GET_RECOMMENDATION = """
SELECT * FROM irrigation_recommendation
WHERE tenant_id=$1 AND field_id=$2 AND day=$3
"""


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------


class TwinRepository:
    """
    Persistence layer for the Digital Twin domain.
    طبقة الاستمرارية لوحدة التوأم الرقمي.

    Accepts an optional asyncpg pool.  When the pool is None (or a DB error
    occurs), all operations fall back transparently to in-memory storage.

    Usage::

        repo = TwinRepository(db_pool=app.state.db_pool)
        await repo.save_state(state)
        state = await repo.get_state(tenant_id, field_id, today)
    """

    def __init__(self, db_pool: Any = None) -> None:
        self._pool = db_pool

    # ------------------------------------------------------------------
    # FieldDailyState
    # ------------------------------------------------------------------

    async def save_state(self, state: FieldDailyState) -> None:
        """Upsert a FieldDailyState. حفظ/تحديث حالة الحقل اليومية."""
        # Always update in-memory cache
        key = (str(state.tenant_id), str(state.field_id), state.day.isoformat())
        _mem_states[key] = state

        if self._pool is None:
            return

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    _SQL_UPSERT_STATE,
                    state.id,
                    state.tenant_id,
                    state.field_id,
                    state.day,
                    state.et0_mm,
                    state.etc_mm,
                    state.phenology_stage,
                    state.gdd_cum,
                    state.lai,
                    state.biomass_kg_ha,
                    state.root_depth_m,
                    state.soil_water_mm,
                    state.depletion_mm,
                    state.water_stress,
                    state.n_stress,
                    state.runoff_mm,
                    state.deep_perc_mm,
                    state.rainfall_mm,
                    state.irrigation_applied_mm,
                    state.nitrogen_applied_kg_ha,
                    state.confidence,
                    [f.value for f in state.assimilation_flags],
                    state.notes,
                    state.created_at,
                    state.updated_at,
                )
        except Exception as exc:
            logger.warning("twin_repo.save_state failed, using memory", error=str(exc))

    async def get_state(
        self,
        tenant_id: UUID,
        field_id: UUID,
        day: date,
    ) -> FieldDailyState | None:
        """Load state for a specific field-day. تحميل حالة يوم محدد."""
        key = (str(tenant_id), str(field_id), day.isoformat())

        if self._pool is not None:
            try:
                async with self._pool.acquire() as conn:
                    row = await conn.fetchrow(_SQL_GET_STATE, tenant_id, field_id, day)
                    if row:
                        return _row_to_state(row)
            except Exception as exc:
                logger.warning(
                    "twin_repo.get_state failed, using memory", error=str(exc)
                )

        return _mem_states.get(key)

    async def get_states(
        self,
        tenant_id: UUID,
        field_id: UUID,
        from_date: date,
        to_date: date,
    ) -> list[FieldDailyState]:
        """Load a date range of states. تحميل سلسلة من الحالات."""
        if self._pool is not None:
            try:
                async with self._pool.acquire() as conn:
                    rows = await conn.fetch(
                        _SQL_GET_STATES_RANGE, tenant_id, field_id, from_date, to_date
                    )
                    return [_row_to_state(r) for r in rows]
            except Exception as exc:
                logger.warning(
                    "twin_repo.get_states failed, using memory", error=str(exc)
                )

        # Fallback: filter in-memory
        tid, fid = str(tenant_id), str(field_id)
        return sorted(
            [
                s
                for k, s in _mem_states.items()
                if k[0] == tid
                and k[1] == fid
                and from_date <= date.fromisoformat(k[2]) <= to_date
            ],
            key=lambda s: s.day,
        )

    # ------------------------------------------------------------------
    # FieldObservation
    # ------------------------------------------------------------------

    async def save_observation(self, obs: FieldObservation) -> None:
        """Persist a field observation. حفظ رصد ميداني."""
        mem_key = (str(obs.tenant_id), str(obs.field_id))
        _mem_observations[mem_key].append(obs)

        if self._pool is None:
            return

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    _SQL_INSERT_OBSERVATION,
                    obs.id,
                    obs.tenant_id,
                    obs.field_id,
                    obs.ts,
                    obs.source.value,
                    obs.obs_type.value,
                    obs.value,
                    obs.quality,
                    json.dumps(obs.meta),
                    obs.created_at,
                )
        except Exception as exc:
            logger.warning(
                "twin_repo.save_observation failed, using memory", error=str(exc)
            )

    async def get_recent_observations(
        self,
        tenant_id: UUID,
        field_id: UUID,
        obs_type: ObservationType,
        days_back: int = 14,
    ) -> list[FieldObservation]:
        """Retrieve recent observations of a given type. استرجاع الأرصاد الأخيرة."""
        if self._pool is not None:
            try:
                async with self._pool.acquire() as conn:
                    rows = await conn.fetch(
                        _SQL_GET_OBSERVATIONS,
                        tenant_id,
                        field_id,
                        obs_type.value,
                        days_back,
                    )
                    return [_row_to_observation(r) for r in rows]
            except Exception as exc:
                logger.warning(
                    "twin_repo.get_observations failed, using memory", error=str(exc)
                )

        # In-memory fallback
        cutoff = datetime.now().timestamp() - days_back * 86400
        mem_key = (str(tenant_id), str(field_id))
        return [
            o
            for o in _mem_observations.get(mem_key, [])
            if o.obs_type == obs_type and o.ts.timestamp() >= cutoff
        ]

    # ------------------------------------------------------------------
    # IrrigationRecommendation
    # ------------------------------------------------------------------

    async def save_recommendation(self, rec: IrrigationRecommendation) -> None:
        """Upsert an irrigation recommendation. حفظ توصية الري."""
        key = (str(rec.tenant_id), str(rec.field_id), rec.day.isoformat())
        _mem_recommendations[key] = rec

        if self._pool is None:
            return

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    _SQL_UPSERT_RECOMMENDATION,
                    rec.id,
                    rec.tenant_id,
                    rec.field_id,
                    rec.day,
                    rec.recommended_mm,
                    rec.reason_codes,
                    json.dumps(rec.explanation),
                    rec.confidence,
                    rec.created_at,
                )
        except Exception as exc:
            logger.warning(
                "twin_repo.save_recommendation failed, using memory", error=str(exc)
            )

    async def get_recommendation(
        self,
        tenant_id: UUID,
        field_id: UUID,
        day: date,
    ) -> IrrigationRecommendation | None:
        """Load recommendation for a field-day. تحميل توصية يوم محدد."""
        key = (str(tenant_id), str(field_id), day.isoformat())

        if self._pool is not None:
            try:
                async with self._pool.acquire() as conn:
                    row = await conn.fetchrow(
                        _SQL_GET_RECOMMENDATION, tenant_id, field_id, day
                    )
                    if row:
                        return _row_to_recommendation(row)
            except Exception as exc:
                logger.warning(
                    "twin_repo.get_recommendation failed, using memory", error=str(exc)
                )

        return _mem_recommendations.get(key)


# ---------------------------------------------------------------------------
# Row conversion helpers
# ---------------------------------------------------------------------------


def _row_to_state(row: Any) -> FieldDailyState:
    flags_raw = row["assimilation_flags"] or []
    flags = [
        AssimilationFlag(f)
        for f in flags_raw
        if f in AssimilationFlag.__members__.values()
    ]
    return FieldDailyState(
        id=row["id"],
        tenant_id=row["tenant_id"],
        field_id=row["field_id"],
        day=row["day"],
        et0_mm=row["et0_mm"],
        etc_mm=row["etc_mm"],
        phenology_stage=row["phenology_stage"],
        gdd_cum=row["gdd_cum"],
        lai=row["lai"],
        biomass_kg_ha=row["biomass_kg_ha"],
        root_depth_m=row["root_depth_m"],
        soil_water_mm=row["soil_water_mm"],
        depletion_mm=row["depletion_mm"],
        water_stress=row["water_stress"],
        n_stress=row["n_stress"],
        runoff_mm=row["runoff_mm"],
        deep_perc_mm=row["deep_perc_mm"],
        rainfall_mm=row["rainfall_mm"] or 0.0,
        irrigation_applied_mm=row["irrigation_applied_mm"] or 0.0,
        nitrogen_applied_kg_ha=row["nitrogen_applied_kg_ha"] or 0.0,
        confidence=row["confidence"] or 0.6,
        assimilation_flags=flags,
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_observation(row: Any) -> FieldObservation:
    from shared.digital_twin.models import ObservationSource

    meta = row["meta"]
    if isinstance(meta, str):
        meta = json.loads(meta)
    elif meta is None:
        meta = {}
    return FieldObservation(
        id=row["id"],
        tenant_id=row["tenant_id"],
        field_id=row["field_id"],
        ts=row["ts"],
        source=ObservationSource(row["source"]),
        obs_type=ObservationType(row["obs_type"]),
        value=row["value"],
        quality=row["quality"] or 0.7,
        meta=meta,
        created_at=row["created_at"],
    )


def _row_to_recommendation(row: Any) -> IrrigationRecommendation:
    explanation = row["explanation"]
    if isinstance(explanation, str):
        explanation = json.loads(explanation)
    elif explanation is None:
        explanation = {}
    return IrrigationRecommendation(
        id=row["id"],
        tenant_id=row["tenant_id"],
        field_id=row["field_id"],
        day=row["day"],
        recommended_mm=row["recommended_mm"],
        reason_codes=list(row["reason_codes"] or []),
        explanation=explanation,
        confidence=row["confidence"] or 0.7,
        created_at=row["created_at"],
    )
