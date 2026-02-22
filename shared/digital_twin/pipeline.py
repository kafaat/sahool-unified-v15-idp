# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Daily Twin Step Pipeline - خط أنابيب الخطوة اليومية للتوأم
==============================================================
Orchestrates the process-based simulation for a single field-day:

  1. agro_meteorology.penman_monteith_et0(weather)
  2. hydrology.soil_water_daily_step(prev_state, weather, soil, et0, Kc)
  3. crop_growth.step(prev_state, weather, soil_water, n_supply)
  4. Build FieldDailyState
  5. Persist via TwinRepository
  6. Publish NATS events  (sahool.field.state.updated.v1)

Designed to run daily (scheduled or on-demand via API).
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any
from uuid import UUID

import structlog

from shared.digital_twin.models import AssimilationFlag, FieldDailyState
from shared.digital_twin.repository import TwinRepository
from shared.process_models.agro_meteorology import (
    AgroMeteorologyEngine,
    penman_monteith_et0,
)
from shared.process_models.crop_growth import (
    CropGrowthEngine,
    compute_gdd,
    partition_biomass,
)
from shared.process_models.hydrology import SoilWaterState, soil_water_daily_step
from shared.process_models.models import CropParameters, DailyWeather, SoilProfile

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Crop coefficient (Kc) per growth stage – FAO-56 Table 11 approximations
# ---------------------------------------------------------------------------

_KC_TABLE: dict[str, float] = {
    "initial": 0.40,
    "sowing": 0.40,
    "emergence": 0.55,
    "tillering": 0.80,
    "stem_elongation": 1.00,
    "heading": 1.15,
    "grain_fill": 1.10,
    "maturity": 0.50,
    "ripening": 0.40,
    "harvest": 0.25,
}

_STAGE_TO_DVS: dict[str, tuple[float, float]] = {
    "sowing": (0.0, 0.1),
    "emergence": (0.1, 0.3),
    "tillering": (0.3, 0.6),
    "stem_elongation": (0.6, 1.0),
    "heading": (1.0, 1.2),
    "grain_fill": (1.2, 1.7),
    "maturity": (1.7, 2.0),
}

_DVS_TO_STAGE: list[tuple[float, str]] = [
    (0.0, "sowing"),
    (0.1, "emergence"),
    (0.3, "tillering"),
    (0.6, "stem_elongation"),
    (1.0, "heading"),
    (1.2, "grain_fill"),
    (1.7, "maturity"),
    (2.0, "harvest"),
]


def _dvs_to_stage(dvs: float) -> str:
    stage = "sowing"
    for threshold, name in _DVS_TO_STAGE:
        if dvs >= threshold:
            stage = name
    return stage


def _kc_for_stage(stage: str) -> float:
    return _KC_TABLE.get(stage, 0.85)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


class TwinPipeline:
    """
    Daily simulation pipeline for a single field.
    خط الأنابيب اليومي للمحاكاة لحقل واحد.

    Usage::

        pipeline = TwinPipeline(repo=TwinRepository(db_pool))

        state = await pipeline.step(
            tenant_id=UUID("..."),
            field_id=UUID("..."),
            day=date.today(),
            weather=DailyWeather(...),
            soil=SoilProfile(...),
            crop=CropParameters(crop_type=CropType.WHEAT),
            irrigation_applied_mm=0.0,
            nitrogen_applied_kg_ha=0.0,
            lat_deg=15.5,
            elevation_m=300.0,
        )
    """

    def __init__(
        self,
        repo: TwinRepository,
        nats_client: Any = None,
    ) -> None:
        self._repo = repo
        self._nats = nats_client
        self._crop_engine = CropGrowthEngine()
        self._met_engine = AgroMeteorologyEngine()

    async def step(
        self,
        tenant_id: UUID,
        field_id: UUID,
        day: date,
        weather: DailyWeather,
        soil: SoilProfile,
        crop: CropParameters,
        irrigation_applied_mm: float = 0.0,
        nitrogen_applied_kg_ha: float = 0.0,
        lat_deg: float = 15.0,
        elevation_m: float = 100.0,
        cn: int = 80,
    ) -> FieldDailyState:
        """
        Execute one daily twin step for a field.
        تنفيذ خطوة يومية واحدة للتوأم الرقمي.

        Returns the persisted FieldDailyState.
        """
        # ── 1. Load previous state ────────────────────────────────────────
        from datetime import timedelta

        prev_day = date(day.year, day.month, day.day) - timedelta(days=1)
        prev_state = await self._repo.get_state(tenant_id, field_id, prev_day)

        # ── 2. ET₀ (Penman-Monteith FAO-56) ──────────────────────────────
        et0 = penman_monteith_et0(weather, elevation_m=elevation_m, lat_deg=lat_deg)

        # ── 3. Crop state extraction / initialisation ─────────────────────
        prev_dvs = 0.0
        prev_gdd = 0.0
        prev_lai = 0.0
        prev_bm = 0.0
        prev_root = soil.depth_m * 0.3
        fc_mm = soil.field_capacity_mm_per_m * soil.depth_m
        prev_sw = fc_mm * 0.8  # Initial soil water at 80% FC

        if prev_state is not None:
            prev_gdd = prev_state.gdd_cum or 0.0
            prev_lai = prev_state.lai or 0.0
            prev_bm = prev_state.biomass_kg_ha or 0.0
            prev_root = prev_state.root_depth_m or (soil.depth_m * 0.3)
            prev_sw = prev_state.soil_water_mm or prev_sw
            # Recover DVS from gdd cumulative (crop-type-aware thresholds)
            prev_dvs = min(2.0, prev_gdd / max(1.0, crop.gdd_maturity))

        # ── 4. Soil water balance ─────────────────────────────────────────
        stage_name = _dvs_to_stage(prev_dvs)
        kc = _kc_for_stage(stage_name)

        sw_state_in = SoilWaterState(
            water_mm=prev_sw,
            drainage_cum_mm=0.0,
            runoff_cum_mm=0.0,
            et_cum_mm=0.0,
        )
        sw_state_out = soil_water_daily_step(
            state=sw_state_in,
            weather=weather,
            soil=soil,
            et0_mm=et0,
            crop_coefficient=kc,
            cn=cn,
            irrigation_mm=irrigation_applied_mm,
        )

        fc_mm = soil.field_capacity_mm_per_m * soil.depth_m
        wp_mm = soil.wilting_point_mm_per_m * soil.depth_m
        depletion = max(0.0, fc_mm - sw_state_out.water_mm)
        taw = max(1.0, fc_mm - wp_mm)
        raw = 0.5 * taw
        sw_adj = max(0.0, sw_state_out.water_mm - wp_mm)
        water_stress = 1.0 if sw_adj >= raw else max(0.0, sw_adj / raw)

        # ── 5. Crop growth step ───────────────────────────────────────────
        gdd = compute_gdd(weather, base_temp=crop.base_temp_c, max_temp_cap=35.0)
        new_gdd = prev_gdd + gdd
        new_dvs = min(
            2.0,
            new_dvs if (new_dvs := new_gdd / max(1.0, crop.gdd_maturity)) else prev_dvs,
        )

        # N stress from total available N supply (simple: applied / requirement)
        n_demand_today = (crop.n_requirement_kg_per_ton * 5.0) / max(
            1.0, crop.gdd_maturity / max(gdd, 0.01)
        )
        n_available = nitrogen_applied_kg_ha + 1.0  # soil background
        n_stress = min(1.0, n_available / max(0.1, n_demand_today))

        # RUE-based biomass increment (Beer-Lambert, stress-adjusted)
        from shared.process_models.crop_growth import compute_intercepted_radiation

        # NOTE: compute_intercepted_radiation already applies the 0.5 PAR
        # fraction internally, so we pass total solar radiation here.
        ipar = compute_intercepted_radiation(
            weather.solar_radiation_mj_m2, prev_lai
        )
        delta_bm_potential = ipar * crop.rue_g_mj  # g m⁻² d⁻¹
        delta_bm = delta_bm_potential * water_stress * n_stress
        new_bm = prev_bm + delta_bm * 10.0  # g m⁻² → kg ha⁻¹

        # Partitioning (harvest index for storage fraction)
        parts = partition_biomass(delta_bm, new_dvs)

        # LAI update (simplified SLA approach)
        sla = 20.0  # cm² g⁻¹
        new_lai = max(0.0, prev_lai + parts.leaves_g_m2 * sla / 10000.0)
        if new_dvs >= 1.7:
            new_lai = max(0.0, new_lai * 0.95)  # senescence post-maturity

        # Root depth growth
        new_root = min(soil.depth_m, prev_root + 0.003 * water_stress)

        new_stage = _dvs_to_stage(new_dvs)
        etc = et0 * kc * water_stress

        # ── 6. Build FieldDailyState ──────────────────────────────────────
        state = FieldDailyState(
            tenant_id=tenant_id,
            field_id=field_id,
            day=day,
            et0_mm=round(et0, 2),
            etc_mm=round(etc, 2),
            phenology_stage=new_stage,
            gdd_cum=round(new_gdd, 1),
            lai=round(new_lai, 3),
            biomass_kg_ha=round(new_bm, 1),
            root_depth_m=round(new_root, 3),
            soil_water_mm=round(sw_state_out.water_mm, 1),
            depletion_mm=round(depletion, 1),
            water_stress=round(water_stress, 3),
            n_stress=round(n_stress, 3),
            runoff_mm=round(sw_state_out.runoff_cum_mm, 2),
            deep_perc_mm=round(sw_state_out.drainage_cum_mm, 2),
            rainfall_mm=round(weather.precipitation_mm, 1),
            irrigation_applied_mm=round(irrigation_applied_mm, 1),
            nitrogen_applied_kg_ha=round(nitrogen_applied_kg_ha, 1),
            confidence=0.75 if prev_state is not None else 0.55,
            assimilation_flags=[AssimilationFlag.MODEL_ONLY],
        )

        # ── 7. Persist ────────────────────────────────────────────────────
        await self._repo.save_state(state)

        # ── 8. Publish NATS event ─────────────────────────────────────────
        await self._publish_state_updated(state)

        logger.info(
            "twin_step_complete",
            field_id=str(field_id),
            day=str(day),
            stage=new_stage,
            depletion_mm=round(depletion, 1),
            water_stress=round(water_stress, 3),
        )
        return state

    async def _publish_state_updated(self, state: FieldDailyState) -> None:
        """Publish sahool.field.state.updated.v1. نشر حدث تحديث الحالة."""
        if self._nats is None:
            return
        try:
            from shared.events.subjects import SAHOOL_FIELD_STATE_UPDATED

            payload = json.dumps(
                {
                    "tenant_id": str(state.tenant_id),
                    "field_id": str(state.field_id),
                    "day": state.day.isoformat(),
                    "state_summary": state.summary(),
                }
            ).encode()
            await self._nats.publish(SAHOOL_FIELD_STATE_UPDATED, payload)
        except Exception as exc:
            logger.warning("twin_nats_publish_failed", error=str(exc))
