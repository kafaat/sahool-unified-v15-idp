# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Decision Engine - محرك القرارات
================================
Converts the Digital Twin daily state into actionable decisions:
  • Irrigation recommendation – RAW-threshold based (FAO-56)
  • Fertilizer recommendation – QUEFTS-based N-P-K dosing

Both decisions are bilingual (Arabic/English) and include:
  - Quantitative recommendation
  - Reason codes (machine-readable)
  - Human-readable explanation

Irrigation logic (FAO-56 §7):
    RAW = p * TAW   where p = depletion fraction (crop-specific)
    Irrigate when: depletion > RAW
    Amount: replenish to field capacity minus target depletion allowance
    Net irrigation = (depletion_target - remaining_allowance) / application_efficiency
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any
from uuid import UUID

import structlog

from shared.digital_twin.models import FieldDailyState, IrrigationRecommendation
from shared.digital_twin.repository import TwinRepository

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Stage-specific depletion fraction p (FAO-56 Table 22 simplified)
# ---------------------------------------------------------------------------

_P_FRACTION: dict[str, float] = {
    "sowing": 0.65,
    "emergence": 0.60,
    "tillering": 0.55,
    "stem_elongation": 0.50,
    "heading": 0.45,
    "grain_fill": 0.40,
    "maturity": 0.55,
    "harvest": 0.65,
}


def _p_for_stage(stage: str | None) -> float:
    return _P_FRACTION.get(stage or "heading", 0.50)


# ---------------------------------------------------------------------------
# Irrigation Decision
# ---------------------------------------------------------------------------


class DecisionEngine:
    """
    Translates Digital Twin state into irrigation/fertilizer decisions.
    تحويل حالة التوأم الرقمي إلى قرارات ري وتسميد.

    Usage::

        engine = DecisionEngine(repo=TwinRepository(pool), nats_client=nc)
        rec = await engine.recommend_irrigation(state, taw_mm=180.0)
        await repo.save_recommendation(rec)
    """

    def __init__(
        self,
        repo: TwinRepository,
        nats_client: Any = None,
        application_efficiency: float = 0.80,
        min_irrigation_mm: float = 5.0,
        max_irrigation_mm: float = 80.0,
    ) -> None:
        self._repo = repo
        self._nats = nats_client
        self._eff = application_efficiency
        self._min = min_irrigation_mm
        self._max = max_irrigation_mm

    async def recommend_irrigation(
        self,
        state: FieldDailyState,
        taw_mm: float = 180.0,
    ) -> IrrigationRecommendation:
        """
        Compute irrigation recommendation for a field-day.
        حساب توصية الري ليوم حقل معين.

        Args:
            state: Latest FieldDailyState from pipeline/assimilation.
            taw_mm: Total available water capacity (FC - WP) in mm.
                    Defaults to 180 mm (medium-texture soil, 60 cm depth).

        Returns:
            IrrigationRecommendation (not yet persisted; caller must save).
        """
        stage = state.phenology_stage
        p = _p_for_stage(stage)
        raw_mm = p * taw_mm  # Readily Available Water threshold

        depletion = state.depletion_mm or 0.0
        water_stress = state.water_stress or 1.0

        reason_codes: list[str] = []
        recommended_mm = 0.0

        if depletion >= raw_mm:
            # Primary trigger: depletion exceeded RAW
            reason_codes.append("DEPLETION_EXCEEDS_RAW")
            # Target: replenish to 90% FC (leave 10% allowance for rain)
            refill_target = 0.10 * taw_mm  # depletion target after irrigation
            net_mm = max(0.0, depletion - refill_target)
            gross_mm = net_mm / max(0.1, self._eff)
            recommended_mm = max(self._min, min(self._max, gross_mm))

        if water_stress < 0.70 and recommended_mm == 0.0:
            # Secondary trigger: stress detected even without depletion data
            reason_codes.append("WATER_STRESS_DETECTED")
            recommended_mm = max(self._min, min(self._max, 0.3 * taw_mm / self._eff))

        if not reason_codes:
            reason_codes.append("NO_IRRIGATION_NEEDED")

        # Bilingual explanation
        if recommended_mm > 0:
            en_text = (
                f"Irrigate {recommended_mm:.0f} mm. "
                f"Soil depletion {depletion:.0f} mm exceeds RAW threshold {raw_mm:.0f} mm "
                f"(p={p:.0%}, stage={stage}). "
                f"Application efficiency assumed {self._eff:.0%}."
            )
            ar_text = (
                f"ري بمقدار {recommended_mm:.0f} ملم. "
                f"عجز الرطوبة {depletion:.0f} ملم يتجاوز الحد RAW = {raw_mm:.0f} ملم "
                f"(معامل الاستنفاد p={p:.0%}، المرحلة={stage}). "
                f"كفاءة الري المفترضة {self._eff:.0%}."
            )
        else:
            en_text = f"No irrigation needed. Depletion {depletion:.0f} mm < RAW {raw_mm:.0f} mm (stage={stage})."
            ar_text = f"لا حاجة للري. العجز {depletion:.0f} ملم < RAW {raw_mm:.0f} ملم (المرحلة={stage})."

        confidence = state.confidence * (0.9 if "ASSIMILATED" not in [f.value for f in state.assimilation_flags] else 1.0)

        rec = IrrigationRecommendation(
            tenant_id=state.tenant_id,
            field_id=state.field_id,
            day=state.day,
            recommended_mm=round(recommended_mm, 1),
            reason_codes=reason_codes,
            explanation={
                "en": en_text,
                "ar": ar_text,
                "depletion_mm": round(depletion, 1),
                "raw_mm": round(raw_mm, 1),
                "taw_mm": taw_mm,
                "p_fraction": p,
                "stage": stage,
                "water_stress": round(water_stress, 3),
                "application_efficiency": self._eff,
            },
            confidence=round(min(0.95, confidence), 3),
        )

        # Publish NATS event
        await self._publish_recommendation(rec)

        logger.info(
            "irrigation_recommendation",
            field_id=str(state.field_id),
            day=str(state.day),
            recommended_mm=rec.recommended_mm,
            reason_codes=reason_codes,
        )
        return rec

    async def recommend_fertilizer(
        self,
        state: FieldDailyState,
        crop_type: str = "wheat",
        target_yield_t_ha: float = 4.0,
        n_supply_kg_ha: float = 60.0,
        p_supply_kg_ha: float = 12.0,
        k_supply_kg_ha: float = 90.0,
    ) -> dict[str, Any]:
        """
        QUEFTS-based fertilizer recommendation from current crop state.
        توصية الأسمدة القائمة على QUEFTS من الحالة الراهنة.
        """
        from shared.process_models.models import CropParameters, CropType
        from shared.process_models.nutrient_management import QueftsNutrientModel, SoilNutrientSupply

        crop_map = {
            "wheat": CropType.WHEAT, "rice": CropType.RICE, "maize": CropType.MAIZE,
            "barley": CropType.BARLEY, "tomato": CropType.TOMATO, "potato": CropType.POTATO,
        }
        ct = crop_map.get(crop_type, CropType.WHEAT)
        model = QueftsNutrientModel()
        result = model.recommend(
            crop=CropParameters(crop_type=ct),
            soil_supply=SoilNutrientSupply(
                n_supply_kg_ha=n_supply_kg_ha,
                p_supply_kg_ha=p_supply_kg_ha,
                k_supply_kg_ha=k_supply_kg_ha,
            ),
            target_yield_t_ha=target_yield_t_ha,
        )
        return result.outputs

    async def _publish_recommendation(self, rec: IrrigationRecommendation) -> None:
        """Publish sahool.irrigation.recommendation.ready.v1."""
        if self._nats is None:
            return
        try:
            from shared.events.subjects import SAHOOL_IRRIGATION_RECOMMENDATION_READY

            payload = json.dumps(
                {
                    "tenant_id": str(rec.tenant_id),
                    "field_id": str(rec.field_id),
                    "day": rec.day.isoformat(),
                    "recommended_mm": rec.recommended_mm,
                    "confidence": rec.confidence,
                    "reason_codes": rec.reason_codes,
                }
            ).encode()
            await self._nats.publish(SAHOOL_IRRIGATION_RECOMMENDATION_READY, payload)
        except Exception as exc:
            logger.warning("decision_nats_publish_failed", error=str(exc))
