# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Agricultural Hydrology Engine - محرك الهيدرولوجيا الزراعية
===========================================================
Process-based soil-water balance, runoff and infiltration models.

Implemented methods:
  • FAO-56 Daily soil water balance (SWAP-compatible)
  • SCS-CN (Curve Number) storm runoff estimation
  • Green-Ampt infiltration model (physically-based)
  • Drainage / deep percolation (Darcy-based)

References:
  Allen RG et al. (1998). FAO Paper No. 56.
  USDA-SCS (1972). National Engineering Handbook, Section 4.
  Green WH & Ampt GA (1911). Flow of air and water through soils. J Agric Sci 4:1-24.
  van Dam JC et al. (2008). SWAP 3.2 Theory description.
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from shared.process_models.models import (
    DailyWeather,
    ModelResult,
    ModelType,
    SoilProfile,
)

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# SCS Curve Number runoff
# ---------------------------------------------------------------------------

# CN values per land use / soil group (USDA hydrologic soil group B)
_CN_TABLE: dict[str, dict[str, int]] = {
    "row_crops_good": {"A": 67, "B": 78, "C": 85, "D": 89},
    "row_crops_poor": {"A": 72, "B": 81, "C": 88, "D": 91},
    "small_grains_good": {"A": 63, "B": 75, "C": 83, "D": 87},
    "meadow_good": {"A": 30, "B": 58, "C": 71, "D": 78},
    "fallow_bare": {"A": 77, "B": 86, "C": 91, "D": 94},
    "irrigated_field": {"A": 72, "B": 81, "C": 88, "D": 91},
}


def scs_cn_runoff(precipitation_mm: float, cn: int = 80) -> float:
    """
    SCS Curve Number direct runoff estimate.
    تقدير الجريان السطحي بطريقة رقم المنحنى.

    Q = (P - Ia)² / (P - Ia + S),  Ia = 0.2 S,  S = 25400/CN - 254   [mm]

    Returns 0 if precipitation less than initial abstraction Ia.
    """
    if cn <= 0 or cn >= 100:
        raise ValueError(f"CN must be in (0, 100); got {cn}")
    s = 25400.0 / cn - 254.0  # Potential maximum retention (mm)
    ia = 0.2 * s  # Initial abstraction (mm)
    if precipitation_mm <= ia:
        return 0.0
    q = (precipitation_mm - ia) ** 2 / (precipitation_mm - ia + s)
    return max(0.0, q)


# ---------------------------------------------------------------------------
# Green-Ampt infiltration
# ---------------------------------------------------------------------------


@dataclass
class GreenAmptParams:
    """
    Green-Ampt hydraulic parameters.
    معاملات نموذج غرين-أمبت الهيدرولوجية.

    Derived from soil texture class following Rawls et al. (1983).
    """

    hydraulic_conductivity_mm_h: float = 11.0  # Ks (mm h⁻¹) | الناقلية الهيدروليكية
    suction_head_mm: float = 88.0  # ψ_f (mm) | ضغط الشفط عند الجبهة
    porosity: float = 0.43  # η (m³ m⁻³) | المسامية الكلية
    initial_water_content: float = 0.20  # θ_i | المحتوى المائي الابتدائي

    @property
    def moisture_deficit(self) -> float:
        """Δθ = η − θ_i. عجز الرطوبة."""
        return max(0.01, self.porosity - self.initial_water_content)


def green_ampt_infiltration(
    rainfall_rate_mm_h: float,
    duration_h: float,
    params: GreenAmptParams,
) -> dict[str, float]:
    """
    Green-Ampt event infiltration and runoff.
    تسلل وجريان نموذج غرين-أمبت لحدث مطري.

    Uses the simplified iterative Mein-Larson procedure:
      f_p = Ks · (1 + ψ_f · Δθ / F)   [mm h⁻¹]
      F   = cumulative infiltration (mm)

    Returns:
        total_infiltration_mm, total_runoff_mm, peak_runoff_rate_mm_h
    """
    ks = params.hydraulic_conductivity_mm_h
    psi = params.suction_head_mm
    dtheta = params.moisture_deficit

    # Time to ponding (tp in hours)
    if rainfall_rate_mm_h <= ks:
        return {
            "total_infiltration_mm": rainfall_rate_mm_h * duration_h,
            "total_runoff_mm": 0.0,
            "peak_runoff_rate_mm_h": 0.0,
        }

    fp = ks * (1.0 + psi * dtheta / 0.001)  # initial high infiltration
    f_cumulative = 0.0
    total_runoff = 0.0
    dt = 0.05  # time step 3-min
    peak_runoff = 0.0

    for _ in range(int(duration_h / dt) + 1):
        if f_cumulative > 1e-9:
            fp = ks * (1.0 + psi * dtheta / f_cumulative)
        else:
            fp = rainfall_rate_mm_h  # no ponding yet

        actual_infiltration = min(rainfall_rate_mm_h, fp) * dt
        f_cumulative += actual_infiltration
        excess = max(0.0, rainfall_rate_mm_h - fp) * dt
        total_runoff += excess
        if excess / dt > peak_runoff:
            peak_runoff = excess / dt

    return {
        "total_infiltration_mm": round(f_cumulative, 2),
        "total_runoff_mm": round(total_runoff, 2),
        "peak_runoff_rate_mm_h": round(peak_runoff, 2),
    }


# ---------------------------------------------------------------------------
# Daily FAO-56 soil water balance
# ---------------------------------------------------------------------------


@dataclass
class SoilWaterState:
    """Daily soil water balance state. الحالة اليومية لميزانية مياه التربة."""

    water_mm: float  # Current soil water in root zone (mm) | مياه التربة الحالية
    drainage_cum_mm: float = 0.0  # Cumulative deep drainage | الصرف العميق التراكمي
    runoff_cum_mm: float = 0.0  # Cumulative runoff | الجريان التراكمي
    et_cum_mm: float = 0.0  # Cumulative ET | التبخر-النتح التراكمي


def soil_water_daily_step(
    state: SoilWaterState,
    weather: DailyWeather,
    soil: SoilProfile,
    et0_mm: float,
    crop_coefficient: float,
    cn: int = 80,
    irrigation_mm: float = 0.0,
) -> SoilWaterState:
    """
    Single-day soil water balance step (FAO-56 / SWAP-compatible).
    خطوة ميزانية مياه التربة اليومية (متوافق مع FAO-56 / SWAP).
    """
    fc_mm = soil.field_capacity_mm_per_m * soil.depth_m
    wp_mm = soil.wilting_point_mm_per_m * soil.depth_m

    # Rainfall + irrigation
    total_input = weather.precipitation_mm + irrigation_mm

    # Surface runoff (SCS-CN)
    runoff = scs_cn_runoff(weather.precipitation_mm, cn)
    net_infiltration = total_input - runoff

    # Soil water after infiltration
    sw_after_infil = state.water_mm + net_infiltration

    # Deep drainage (Darcy-based, only when above FC)
    if sw_after_infil > fc_mm:
        drainage = (sw_after_infil - fc_mm) * 0.5  # k_drain factor
        sw_after_infil -= drainage
    else:
        drainage = 0.0

    # Actual ET (water-stressed)
    taw = fc_mm - wp_mm
    p_depl = 0.5  # Fraction of TAW depleted before stress (crop-specific)
    raw = p_depl * taw  # Readily available water
    sw_adj = sw_after_infil - wp_mm
    if taw > 0:
        ks = 1.0 if sw_adj >= raw else max(0.0, sw_adj / raw)
    else:
        ks = 1.0
    etc_mm = et0_mm * crop_coefficient * ks
    sw_final = max(0.0, sw_after_infil - etc_mm)

    return SoilWaterState(
        water_mm=sw_final,
        drainage_cum_mm=state.drainage_cum_mm + drainage,
        runoff_cum_mm=state.runoff_cum_mm + runoff,
        et_cum_mm=state.et_cum_mm + etc_mm,
    )


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------


class HydrologyEngine:
    """
    Agricultural hydrology engine.
    محرك الهيدرولوجيا الزراعية.

    Combines FAO-56 soil water balance, SCS-CN runoff and Green-Ampt
    infiltration for field- to farm-scale water management analysis.

    Usage::

        engine = HydrologyEngine()
        result = engine.run_water_balance(
            soil=SoilProfile(),
            weather_series=[DailyWeather(...)],
            et0_series=[4.5, 5.0, ...],
        )
        print(result.outputs["total_drainage_mm"])
    """

    def run_water_balance(
        self,
        soil: SoilProfile,
        weather_series: list[DailyWeather],
        et0_series: list[float],
        crop_coefficient: float = 1.0,
        irrigation_schedule: dict[int, float] | None = None,
        cn: int = 80,
    ) -> ModelResult:
        """
        Seasonal soil water balance simulation.
        محاكاة ميزانية مياه التربة الموسمية.

        Args:
            soil: Soil physical properties.
            weather_series: Daily weather records.
            et0_series: Pre-computed ET₀ per day (mm d⁻¹).
            crop_coefficient: Kc (constant or mean season value).
            irrigation_schedule: {day_index: irrigation_mm}.
            cn: SCS curve number for runoff estimation.

        Returns:
            ModelResult with water balance components.
        """
        if irrigation_schedule is None:
            irrigation_schedule = {}

        fc_mm = soil.field_capacity_mm_per_m * soil.depth_m
        state = SoilWaterState(water_mm=fc_mm * 0.8)  # start at 80% FC
        daily_log = []

        for day_idx, (weather, et0) in enumerate(zip(weather_series, et0_series)):
            irr = irrigation_schedule.get(day_idx, 0.0)
            state = soil_water_daily_step(
                state, weather, soil, et0, crop_coefficient, cn, irr
            )
            daily_log.append(
                {
                    "day": day_idx + 1,
                    "sw_mm": round(state.water_mm, 1),
                    "drainage_mm": round(state.drainage_cum_mm, 1),
                    "runoff_mm": round(state.runoff_cum_mm, 1),
                    "et_cum_mm": round(state.et_cum_mm, 1),
                    "irr_mm": irr,
                }
            )

        logger.info(
            "hydrology_balance_complete",
            days=len(weather_series),
            total_drainage=round(state.drainage_cum_mm, 1),
            total_runoff=round(state.runoff_cum_mm, 1),
            total_et=round(state.et_cum_mm, 1),
        )

        return ModelResult(
            model_name="HydrologyEngine (FAO-56 SWB + SCS-CN + Green-Ampt)",
            model_type=ModelType.HYDROLOGY,
            success=True,
            message="Soil water balance completed",
            message_ar="اكتملت محاكاة ميزانية مياه التربة",
            outputs={
                "final_soil_water_mm": round(state.water_mm, 1),
                "total_drainage_mm": round(state.drainage_cum_mm, 1),
                "total_runoff_mm": round(state.runoff_cum_mm, 1),
                "total_et_mm": round(state.et_cum_mm, 1),
                "days_simulated": len(weather_series),
            },
            metadata={"daily_log": daily_log},
        )

    def estimate_event_runoff(
        self,
        precipitation_mm: float,
        cn: int = 80,
    ) -> dict[str, float]:
        """
        Quick SCS-CN single-event runoff estimation.
        تقدير سريع للجريان السطحي بطريقة SCS-CN.
        """
        runoff = scs_cn_runoff(precipitation_mm, cn)
        return {
            "precipitation_mm": precipitation_mm,
            "runoff_mm": round(runoff, 2),
            "infiltration_mm": round(precipitation_mm - runoff, 2),
            "runoff_coefficient": (
                round(runoff / precipitation_mm, 3) if precipitation_mm > 0 else 0.0
            ),
        }

    def estimate_green_ampt_event(
        self,
        rainfall_rate_mm_h: float,
        duration_h: float,
        soil: SoilProfile,
    ) -> dict[str, float]:
        """
        Green-Ampt infiltration for a single storm event.
        تسلل وجريان غرين-أمبت لحدث عاصفة واحدة.
        """
        # Map soil texture to Green-Ampt parameters (Rawls et al. 1983)
        from shared.process_models.models import SoilTextureClass

        ks_map = {
            SoilTextureClass.SAND: 117.8,
            SoilTextureClass.LOAMY_SAND: 29.9,
            SoilTextureClass.SANDY_LOAM: 10.9,
            SoilTextureClass.LOAM: 3.3,
            SoilTextureClass.SILT_LOAM: 6.8,
            SoilTextureClass.SANDY_CLAY_LOAM: 1.5,
            SoilTextureClass.CLAY_LOAM: 1.0,
            SoilTextureClass.SILTY_CLAY_LOAM: 1.0,
            SoilTextureClass.SANDY_CLAY: 0.6,
            SoilTextureClass.SILTY_CLAY: 0.5,
            SoilTextureClass.CLAY: 0.3,
        }
        psi_map = {
            SoilTextureClass.SAND: 49.5,
            SoilTextureClass.LOAMY_SAND: 61.3,
            SoilTextureClass.SANDY_LOAM: 110.1,
            SoilTextureClass.LOAM: 88.9,
            SoilTextureClass.SILT_LOAM: 166.8,
            SoilTextureClass.SANDY_CLAY_LOAM: 218.5,
            SoilTextureClass.CLAY_LOAM: 208.8,
            SoilTextureClass.SILTY_CLAY_LOAM: 273.0,
            SoilTextureClass.SANDY_CLAY: 239.0,
            SoilTextureClass.SILTY_CLAY: 292.2,
            SoilTextureClass.CLAY: 316.3,
        }
        ks = ks_map.get(soil.texture, 11.0)
        psi = psi_map.get(soil.texture, 88.0)
        n = (soil.saturation_mm_per_m - soil.wilting_point_mm_per_m) / 1000.0 + 0.1
        theta_i = soil.field_capacity_mm_per_m / 1000.0 * 0.5

        params = GreenAmptParams(
            hydraulic_conductivity_mm_h=ks,
            suction_head_mm=psi,
            porosity=n,
            initial_water_content=theta_i,
        )
        return green_ampt_infiltration(rainfall_rate_mm_h, duration_h, params)
