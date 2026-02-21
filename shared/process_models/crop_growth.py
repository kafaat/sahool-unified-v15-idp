# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Crop Growth Engine - محرك نمو المحاصيل
========================================
Mechanistic crop growth model inspired by WOFOST, AquaCrop and APSIM.

Implements the four core sub-units described in the scientific literature:
  1. Phenology       – GDD-driven growth stage progression
  2. Photosynthesis  – RUE-based biomass accumulation (with Farquhar upgrade path)
  3. Partitioning    – Source-sink distribution of assimilates
  4. Stress          – Water and nitrogen stress scaling factors

Reference:
  van Ittersum & Rabbinge (1997). Concepts in production ecology for analysis
  and quantification of agricultural input-output combinations.
  Field Crops Research 52: 197-208.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

import structlog

from shared.process_models.models import (
    CropParameters,
    DailyWeather,
    GrowthStage,
    ModelResult,
    ModelType,
    SoilProfile,
)

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Phenology – الفينولوجيا
# ---------------------------------------------------------------------------


@dataclass
class PhenologyState:
    """Daily phenology state. الحالة الفينولوجية اليومية."""

    doy: int = 1  # Day of year | يوم السنة
    gdd_cumulative: float = 0.0  # Cumulative GDD since sowing | وحدات الحرارة التراكمية
    stage: GrowthStage = GrowthStage.SOWING
    dvs: float = 0.0  # Development stage (0=sowing, 1=heading, 2=maturity) | مرحلة التطور


def compute_gdd(weather: DailyWeather, base_temp: float = 0.0, max_temp_cap: float = 35.0) -> float:
    """
    Compute Growing Degree Days for a single day.
    حساب وحدات الحرارة الزراعية ليوم واحد.

    GDD = max(0, Tmean - T_base),  capped at T_max.
    """
    tmean = min(weather.tmean_c, max_temp_cap)
    return max(0.0, tmean - base_temp)


def update_phenology(state: PhenologyState, gdd_today: float, params: CropParameters) -> PhenologyState:
    """
    Advance phenological stage based on accumulated GDD.
    تحديث مرحلة النمو استنادًا إلى وحدات الحرارة المتراكمة.
    """
    state.gdd_cumulative += gdd_today
    state.doy += 1

    gdd = state.gdd_cumulative
    # DVS: 0 → emergence, 1 → heading, 2 → maturity (linear interpolation)
    if gdd < params.gdd_emergence:
        state.stage = GrowthStage.GERMINATION
        state.dvs = 0.0
    elif gdd < params.gdd_heading:
        state.stage = GrowthStage.VEGETATIVE
        state.dvs = (gdd - params.gdd_emergence) / max(1.0, params.gdd_heading - params.gdd_emergence)
    elif gdd < params.gdd_maturity:
        state.stage = GrowthStage.GRAIN_FILL
        state.dvs = 1.0 + (gdd - params.gdd_heading) / max(1.0, params.gdd_maturity - params.gdd_heading)
    else:
        state.stage = GrowthStage.MATURITY
        state.dvs = 2.0
    return state


# ---------------------------------------------------------------------------
# Photosynthesis / Biomass – التمثيل الضوئي والكتلة الحيوية
# ---------------------------------------------------------------------------


def compute_intercepted_radiation(solar_rad_mj_m2: float, lai: float, k: float = 0.5) -> float:
    """
    Intercepted PAR using Beer-Lambert law.
    الإشعاع الفعال المعترض باستخدام قانون بير-لامبرت.

    IPAR = 0.5 · Rs · (1 − exp(−k · LAI))
    Factor 0.5 converts total solar to PAR fraction.
    """
    par = 0.5 * solar_rad_mj_m2
    fpar = 1.0 - math.exp(-k * max(0.0, lai))
    return par * fpar


def compute_biomass_increment(intercepted_par_mj: float, rue_g_mj: float, stress_factor: float = 1.0) -> float:
    """
    Daily biomass increment via Radiation Use Efficiency.
    الزيادة اليومية في الكتلة الحيوية باستخدام كفاءة استخدام الإشعاع.

    ΔBM = IPAR × RUE × min(Ws, Wn)
    """
    return intercepted_par_mj * rue_g_mj * max(0.0, min(1.0, stress_factor))


# ---------------------------------------------------------------------------
# Partitioning – توزيع المنتجات الضوئية
# ---------------------------------------------------------------------------

# Source-sink partitioning fractions per DVS interval (WOFOST-style)
# fmt: off
_PARTITION_TABLE: dict[str, list[tuple[float, float]]] = {
    # DVS →  fraction
    "leaves":    [(0.0, 0.65), (1.0, 0.12), (1.3, 0.0),  (2.0, 0.0)],
    "stems":     [(0.0, 0.20), (1.0, 0.25), (1.3, 0.0),  (2.0, 0.0)],
    "roots":     [(0.0, 0.15), (1.0, 0.10), (1.3, 0.05), (2.0, 0.0)],
    "storage":   [(0.0, 0.00), (1.0, 0.53), (1.3, 0.95), (2.0, 1.0)],
}
# fmt: on


def _interpolate(table: list[tuple[float, float]], dvs: float) -> float:
    """Linear interpolation in a (DVS, fraction) lookup table."""
    if dvs <= table[0][0]:
        return table[0][1]
    if dvs >= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        x0, y0 = table[i]
        x1, y1 = table[i + 1]
        if x0 <= dvs <= x1:
            return y0 + (y1 - y0) * (dvs - x0) / (x1 - x0)
    return 0.0


@dataclass
class PartitioningResult:
    """Daily biomass allocation. توزيع الكتلة الحيوية اليومي."""

    total_dm_g_m2: float
    leaves_g_m2: float
    stems_g_m2: float
    roots_g_m2: float
    storage_g_m2: float


def partition_biomass(delta_bm: float, dvs: float) -> PartitioningResult:
    """
    Distribute daily biomass increment across organs using DVS-based fractions.
    توزيع الزيادة اليومية في الكتلة الحيوية على الأعضاء النباتية.
    """
    fl = _interpolate(_PARTITION_TABLE["leaves"], dvs)
    fs = _interpolate(_PARTITION_TABLE["stems"], dvs)
    fr = _interpolate(_PARTITION_TABLE["roots"], dvs)
    fg = _interpolate(_PARTITION_TABLE["storage"], dvs)
    total = fl + fs + fr + fg
    if total > 0:
        fl, fs, fr, fg = fl / total, fs / total, fr / total, fg / total
    return PartitioningResult(
        total_dm_g_m2=delta_bm,
        leaves_g_m2=delta_bm * fl,
        stems_g_m2=delta_bm * fs,
        roots_g_m2=delta_bm * fr,
        storage_g_m2=delta_bm * fg,
    )


# ---------------------------------------------------------------------------
# Stress factors – عوامل الإجهاد
# ---------------------------------------------------------------------------


def water_stress_factor(soil_water_mm: float, field_capacity_mm: float, wilting_point_mm: float) -> float:
    """
    Water stress factor Ws ∈ [0, 1].
    معامل إجهاد الرطوبة.

    Ws = 1 (no stress) when SW > 0.5*TAW above WP.
    Linear reduction to 0 at WP.
    """
    taw = field_capacity_mm - wilting_point_mm
    if taw <= 0:
        return 1.0
    rew = 0.5 * taw  # Readily evaporable water threshold
    sw_adj = soil_water_mm - wilting_point_mm
    if sw_adj >= rew:
        return 1.0
    return max(0.0, sw_adj / rew)


def nitrogen_stress_factor(n_supply_kg_ha: float, n_demand_kg_ha: float) -> float:
    """
    Nitrogen stress factor Wn ∈ [0, 1].
    معامل إجهاد النيتروجين.
    """
    if n_demand_kg_ha <= 0:
        return 1.0
    return min(1.0, max(0.0, n_supply_kg_ha / n_demand_kg_ha))


# ---------------------------------------------------------------------------
# Main Engine
# ---------------------------------------------------------------------------


@dataclass
class CropGrowthState:
    """Accumulated crop growth state over the season. الحالة التراكمية لنمو المحصول."""

    phenology: PhenologyState = field(default_factory=PhenologyState)
    total_biomass_g_m2: float = 0.0  # Aboveground DM (g m⁻²) | الكتلة الحيوية الكلية
    leaves_g_m2: float = 0.0
    stems_g_m2: float = 0.0
    storage_g_m2: float = 0.0  # Grain / storage organ | حبوب/ثمار
    lai: float = 0.01  # Leaf Area Index | مؤشر مساحة الأوراق
    soil_water_mm: float = 200.0  # Current soil water (mm) | مياه التربة الحالية
    n_supply_kg_ha: float = 0.0  # Mineral N available (kg ha⁻¹) | النيتروجين المتاح
    daily_log: list[dict] = field(default_factory=list)


class CropGrowthEngine:
    """
    WOFOST/AquaCrop-inspired daily crop growth simulator.
    محاكي يومي لنمو المحاصيل مستوحى من WOFOST/AquaCrop.

    Usage::

        engine = CropGrowthEngine()
        result = engine.simulate(
            crop=CropParameters(crop_type=CropType.WHEAT),
            soil=SoilProfile(),
            weather_series=[DailyWeather(...)],
        )
        print(result.outputs["grain_yield_t_ha"])
    """

    def simulate(
        self,
        crop: CropParameters,
        soil: SoilProfile,
        weather_series: list[DailyWeather],
        sowing_date: date | None = None,
        n_supply_kg_ha: float = 80.0,
    ) -> ModelResult:
        """
        Run daily crop growth simulation.
        تشغيل محاكاة نمو المحصول اليومية.

        Args:
            crop: Crop-specific parameters.
            soil: Soil physical properties.
            weather_series: Ordered list of daily weather records.
            sowing_date: Optional explicit sowing date.
            n_supply_kg_ha: Total mineral N available (kg ha⁻¹).

        Returns:
            ModelResult with grain_yield_t_ha, biomass_t_ha, and daily log.
        """
        state = CropGrowthState(soil_water_mm=soil.field_capacity_mm_per_m * soil.depth_m * 0.75)
        state.n_supply_kg_ha = n_supply_kg_ha

        fc_mm = soil.field_capacity_mm_per_m * soil.depth_m
        wp_mm = soil.wilting_point_mm_per_m * soil.depth_m

        for day_idx, weather in enumerate(weather_series):
            if state.phenology.stage == GrowthStage.MATURITY:
                break

            # 1. Phenology
            gdd = compute_gdd(weather, crop.base_temp_c)
            state.phenology = update_phenology(state.phenology, gdd, crop)
            dvs = state.phenology.dvs

            # 2. Soil water balance (simplified FAO-56 daily step)
            et0_approx = max(0.0, (weather.solar_radiation_mj_m2 * 0.0135 * (weather.tmean_c + 17.8)))
            kcb = crop.crop_coefficient_kcb_mid * min(1.0, dvs + 0.1) if dvs < 2.0 else 0.2
            etc_mm = et0_approx * kcb
            state.soil_water_mm += weather.precipitation_mm
            state.soil_water_mm = min(state.soil_water_mm, fc_mm)
            ws = water_stress_factor(state.soil_water_mm, fc_mm, wp_mm)
            state.soil_water_mm = max(wp_mm * 0.1, state.soil_water_mm - etc_mm)

            # 3. N stress
            n_demand = (crop.n_requirement_kg_per_ton / 1000.0) * state.total_biomass_g_m2 * 0.01 + 0.05
            wn = nitrogen_stress_factor(state.n_supply_kg_ha, n_demand)
            state.n_supply_kg_ha = max(0.0, state.n_supply_kg_ha - n_demand * 0.05)

            combined_stress = ws * wn

            # 4. Photosynthesis / biomass
            ipar = compute_intercepted_radiation(weather.solar_radiation_mj_m2, state.lai, crop.k_extinction)
            delta_bm = compute_biomass_increment(ipar, crop.rue_g_mj, combined_stress) * 100.0  # g m⁻² d⁻¹

            # 5. Partitioning
            part = partition_biomass(delta_bm, dvs)
            state.total_biomass_g_m2 += delta_bm
            state.leaves_g_m2 += part.leaves_g_m2
            state.stems_g_m2 += part.stems_g_m2
            state.storage_g_m2 += part.storage_g_m2

            # 6. Update LAI (SLA-based; SLA ≈ 20 cm² g⁻¹)
            sla_cm2_g = 20.0
            state.lai = max(0.01, min(crop.lai_max, state.leaves_g_m2 * sla_cm2_g / 10000.0))

            state.daily_log.append(
                {
                    "day": day_idx + 1,
                    "stage": state.phenology.stage,
                    "dvs": round(dvs, 3),
                    "gdd_cum": round(state.phenology.gdd_cumulative, 1),
                    "biomass_g_m2": round(state.total_biomass_g_m2, 1),
                    "lai": round(state.lai, 3),
                    "ws": round(ws, 3),
                    "wn": round(wn, 3),
                }
            )

        grain_yield_t_ha = state.storage_g_m2 * crop.harvest_index / 100.0
        biomass_t_ha = state.total_biomass_g_m2 / 100.0

        logger.info(
            "crop_growth_simulation_complete",
            crop=crop.crop_type,
            grain_yield_t_ha=round(grain_yield_t_ha, 2),
            biomass_t_ha=round(biomass_t_ha, 2),
            days_simulated=len(state.daily_log),
        )

        return ModelResult(
            model_name="CropGrowthEngine (WOFOST/AquaCrop-inspired)",
            model_type=ModelType.CROP_GROWTH,
            success=True,
            message="Simulation completed successfully",
            message_ar="اكتملت المحاكاة بنجاح",
            outputs={
                "grain_yield_t_ha": round(grain_yield_t_ha, 3),
                "biomass_t_ha": round(biomass_t_ha, 3),
                "final_lai": round(state.lai, 3),
                "final_stage": state.phenology.stage,
                "final_dvs": round(state.phenology.dvs, 3),
                "total_gdd": round(state.phenology.gdd_cumulative, 1),
                "days_simulated": len(state.daily_log),
            },
            metadata={"daily_log": state.daily_log},
        )
