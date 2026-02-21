# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Assimilation Engine - محرك التمثيل البياني
===========================================
Corrects the Digital Twin model state using real-world observations
(NDVI → LAI, soil moisture sensors → soil_water_mm).

Implements a "Kalman-lite" sequential update rule:
    corrected = model_value + gain * (observed - model_value)
where:
    gain ∈ (0, 1) is modulated by observation quality and model confidence.

This is a deliberate simplification of Ensemble Kalman Filter (EnKF) that
avoids the computational overhead of covariance matrices while still providing
the essential benefit: pulling the model towards observations.

Reference:
    Reichle RH (2008). Data assimilation methods in the Earth sciences.
    Advances in Water Resources 31:1411-1418.
    Dorigo WA et al. (2007). A review on reflective remote sensing and data
    assimilation techniques for enhanced agroecosystem modelling. IJAEOG 9:165-193.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID

import structlog

from shared.digital_twin.models import AssimilationFlag, FieldDailyState, FieldObservation, ObservationType
from shared.digital_twin.repository import TwinRepository

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# NDVI → LAI look-up (Baret & Guyot 1991; WOFOST calibration)
# ---------------------------------------------------------------------------

def ndvi_to_lai(ndvi: float, crop_type: str = "wheat") -> float:
    """
    Convert NDVI to LAI using an exponential relationship.
    تحويل NDVI إلى LAI باستخدام علاقة أسية.

    Calibrated for cereal crops in arid/semi-arid environments.
    For best accuracy use PROSAIL inversion (feature-flagged separately).

    LAI ≈ −(ln(1 − NDVI_scaled) / k)   with k ≈ 0.5 (Beer-Lambert proxy)
    """
    ndvi = max(0.01, min(0.99, ndvi))
    # Scale NDVI to fractional cover approximation
    ndvi_max = {"wheat": 0.85, "maize": 0.90, "rice": 0.80, "date_palm": 0.70}
    nmax = ndvi_max.get(crop_type, 0.85)
    scaled = min(0.99, ndvi / nmax)
    k = 0.5
    import math
    lai = -math.log(1.0 - scaled) / k
    return max(0.0, min(10.0, lai))


# ---------------------------------------------------------------------------
# Kalman-lite gain
# ---------------------------------------------------------------------------

def _kalman_gain(obs_quality: float, model_confidence: float) -> float:
    """
    Compute scalar Kalman gain from quality/confidence scores.
    حساب معامل كالمان من درجات الجودة والثقة.

    gain = obs_variance_weight / (obs_variance_weight + model_variance_weight)
    Approximated as: gain = obs_quality / (obs_quality + model_confidence)
    Bounded to (0.05, 0.80) to prevent overcorrection.
    """
    denom = obs_quality + model_confidence
    if denom < 1e-6:
        return 0.3
    gain = obs_quality / denom
    return max(0.05, min(0.80, gain))


def _update_value(model_val: float | None, observed: float, gain: float) -> float:
    """Sequential Kalman update: x_a = x_b + K*(y - x_b). تحديث قيمة واحدة."""
    if model_val is None:
        return observed
    return model_val + gain * (observed - model_val)


# ---------------------------------------------------------------------------
# Assimilation Engine
# ---------------------------------------------------------------------------


class AssimilationEngine:
    """
    Lightweight data assimilation for the Digital Twin.
    محرك التمثيل البياني الخفيف للتوأم الرقمي.

    Pulls the latest NDVI/LAI/soil-moisture observations from the repository
    and corrects the model state with a Kalman-lite update.

    Usage::

        engine = AssimilationEngine(repo=TwinRepository(pool))
        corrected = await engine.assimilate(state, crop_type="wheat")
    """

    def __init__(self, repo: TwinRepository) -> None:
        self._repo = repo

    async def assimilate(
        self,
        state: FieldDailyState,
        crop_type: str = "wheat",
    ) -> FieldDailyState:
        """
        Correct state with any available observations from the last 7 days.
        تصحيح الحالة بالأرصاد المتاحة خلال 7 أيام الأخيرة.

        Returns a new FieldDailyState (does NOT mutate the input).
        """
        updated = state.model_copy(deep=True)
        flags: list[AssimilationFlag] = list(state.assimilation_flags)
        corrections: dict[str, Any] = {}

        # ── NDVI → LAI correction ─────────────────────────────────────────
        ndvi_obs = await self._repo.get_recent_observations(
            state.tenant_id, state.field_id, ObservationType.NDVI, days_back=7
        )
        if ndvi_obs:
            best = max(ndvi_obs, key=lambda o: o.quality)
            lai_obs = ndvi_to_lai(best.value, crop_type)
            gain = _kalman_gain(best.quality, state.confidence)
            new_lai = _update_value(state.lai, lai_obs, gain)
            corrections["lai_before"] = state.lai
            corrections["lai_after"] = round(new_lai, 3)
            corrections["ndvi_used"] = best.value
            updated = updated.model_copy(update={"lai": round(new_lai, 3)})
            if AssimilationFlag.NDVI_USED not in flags:
                flags.append(AssimilationFlag.NDVI_USED)

        # ── Direct LAI observation ────────────────────────────────────────
        lai_obs_list = await self._repo.get_recent_observations(
            state.tenant_id, state.field_id, ObservationType.LAI, days_back=7
        )
        if lai_obs_list:
            best_lai = max(lai_obs_list, key=lambda o: o.quality)
            gain = _kalman_gain(best_lai.quality, state.confidence)
            new_lai2 = _update_value(updated.lai, best_lai.value, gain)
            corrections["lai_direct"] = round(new_lai2, 3)
            updated = updated.model_copy(update={"lai": round(new_lai2, 3)})
            if AssimilationFlag.LAI_USED not in flags:
                flags.append(AssimilationFlag.LAI_USED)

        # ── Soil moisture correction ──────────────────────────────────────
        sm_obs_list = await self._repo.get_recent_observations(
            state.tenant_id, state.field_id, ObservationType.SOIL_MOISTURE, days_back=3
        )
        if sm_obs_list:
            # Sensor gives volumetric water content (m³ m⁻³); convert to mm
            best_sm = max(sm_obs_list, key=lambda o: o.quality)
            # Assume sensor depth = soil depth → soil_water_mm = vwc * depth_mm
            # depth_mm is not in state; use a default of 600 mm
            depth_mm = 600.0
            if best_sm.meta.get("soil_depth_m"):
                depth_mm = float(best_sm.meta["soil_depth_m"]) * 1000.0
            sw_obs_mm = best_sm.value * depth_mm
            gain = _kalman_gain(best_sm.quality, state.confidence)
            new_sw = _update_value(state.soil_water_mm, sw_obs_mm, gain)
            corrections["soil_water_before"] = state.soil_water_mm
            corrections["soil_water_after"] = round(new_sw, 1)
            updated = updated.model_copy(update={"soil_water_mm": round(new_sw, 1)})
            if AssimilationFlag.SOIL_MOISTURE_USED not in flags:
                flags.append(AssimilationFlag.SOIL_MOISTURE_USED)

        if not corrections:
            return state  # Nothing to correct

        # Mark as assimilated, boost confidence slightly
        if AssimilationFlag.ASSIMILATED not in flags:
            flags.append(AssimilationFlag.ASSIMILATED)
        # Remove MODEL_ONLY flag if it was set
        flags = [f for f in flags if f != AssimilationFlag.MODEL_ONLY]

        new_confidence = min(0.95, state.confidence + 0.05 * len(corrections))
        updated = updated.model_copy(
            update={
                "assimilation_flags": flags,
                "confidence": round(new_confidence, 3),
                "notes": (state.notes or "") + f" | assimilation: {corrections}",
            }
        )

        logger.info(
            "assimilation_complete",
            field_id=str(state.field_id),
            day=str(state.day),
            corrections=corrections,
            new_confidence=round(new_confidence, 3),
        )
        return updated
