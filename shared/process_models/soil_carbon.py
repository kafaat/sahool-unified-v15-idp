# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Soil Carbon Model - نموذج الكربون العضوي للتربة
================================================
Multi-pool soil organic carbon (SOC) and nitrogen cycling model
inspired by RothC and DNDC.

Pool structure (three-pool model):
  Active  – Microbial biomass.  Turnover: days–weeks.   نشط  (كتلة حيوية ميكروبية)
  Slow    – Humified organic matter.  Turnover: years.   بطيء (مواد هيومينية)
  Passive – Chemically stabilised C.  Turnover: decades.  سلبي (مستقر كيميائياً)

References:
  Coleman K & Jenkinson DS (1996). RothC-26.3 – A Model for Turnover of Carbon in Soil.
  Li C et al. (1992). A process-oriented model of N2O emissions from natural soils.
  DNDC – Denitrification-Decomposition model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import structlog

from shared.process_models.models import ModelResult, ModelType, SoilProfile

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Pool definitions
# ---------------------------------------------------------------------------


@dataclass
class CarbonPools:
    """
    Three-pool SOM decomposition structure.
    بنية تحلل المادة العضوية ذات الثلاثة أحواض.
    """

    active_t_ha: float = 0.5  # Microbial biomass C (t ha⁻¹) | الكربون الميكروبي
    slow_t_ha: float = 8.0  # Slow-cycling humus (t ha⁻¹) | الهيومس البطيء
    passive_t_ha: float = 30.0  # Passive / stabilised C (t ha⁻¹) | الكربون السلبي
    inert_t_ha: float = 5.0  # Inert organic matter (t ha⁻¹) | المادة العضوية الخاملة

    @property
    def total_soc_t_ha(self) -> float:
        """Total SOC excluding inert pool. إجمالي كربون التربة العضوي."""
        return self.active_t_ha + self.slow_t_ha + self.passive_t_ha + self.inert_t_ha


@dataclass
class NitrogenPools:
    """Soil inorganic nitrogen pools (kg N ha⁻¹). أحواض النيتروجين المعدني."""

    ammonium_kg_ha: float = 15.0  # NH₄⁺ | الأمونيوم
    nitrate_kg_ha: float = 25.0  # NO₃⁻ | النترات

    @property
    def mineral_n_kg_ha(self) -> float:
        return self.ammonium_kg_ha + self.nitrate_kg_ha


# ---------------------------------------------------------------------------
# Temperature and moisture modifiers (CENTURY/RothC style)
# ---------------------------------------------------------------------------


def temperature_modifier(temp_c: float) -> float:
    """
    Q₁₀-based temperature modifier for decomposition rates (0–2).
    معدّل درجة الحرارة لمعدلات التحلل.

    f_T = Q10^((T-Tref)/10),   Q10=2.0, Tref=10°C
    Clamped to [0.1, 3.0].
    """
    q10 = 2.0
    t_ref = 10.0
    ft = q10 ** ((temp_c - t_ref) / 10.0)
    return max(0.1, min(3.0, ft))


def moisture_modifier(
    soil_water_mm: float, field_capacity_mm: float, wilting_point_mm: float
) -> float:
    """
    Moisture modifier for decomposition (0–1).
    معدّل الرطوبة لمعدلات التحلل.

    Decomposition peaks at 60% WFPS (water-filled pore space proxy).
    """
    taw = max(1.0, field_capacity_mm - wilting_point_mm)
    wfps = max(0.0, min(1.0, (soil_water_mm - wilting_point_mm) / taw))
    # Bell-shaped response peaking at WFPS = 0.6
    fm = math.exp(-0.5 * ((wfps - 0.6) / 0.2) ** 2)
    return max(0.01, fm)


# ---------------------------------------------------------------------------
# Annual decomposition step
# ---------------------------------------------------------------------------


@dataclass
class CarbonFluxes:
    """Annual SOC fluxes (t C ha⁻¹ yr⁻¹). تدفقات الكربون السنوية."""

    active_to_slow: float = 0.0  # Active → Slow | من النشط إلى البطيء
    active_to_passive: float = 0.0  # Active → Passive | من النشط إلى السلبي
    active_to_co2: float = 0.0  # Mineralised CO₂ from active | CO₂ من النشط
    slow_to_passive: float = 0.0  # Slow → Passive | من البطيء إلى السلبي
    slow_to_co2: float = 0.0  # CO₂ from slow | CO₂ من البطيء
    passive_to_co2: float = 0.0  # CO₂ from passive | CO₂ من السلبي
    n2o_kg_ha: float = 0.0  # N₂O emission (DNDC-inspired) | انبعاثات أكسيد النيتروز
    ch4_kg_ha: float = 0.0  # CH₄ emission (rice/wetland) | انبعاثات الميثان


def annual_decomposition(
    pools: CarbonPools,
    nitrogen: NitrogenPools,
    soil: SoilProfile,
    mean_temp_c: float,
    mean_soil_water_mm: float,
    carbon_input_t_ha: float = 2.0,
    is_anaerobic: bool = False,
) -> tuple[CarbonPools, NitrogenPools, CarbonFluxes]:
    """
    Simulate one year of SOC turnover and N cycling.
    محاكاة سنة واحدة من دوران الكربون والنيتروجين.

    Pool decomposition rate constants (yr⁻¹) from RothC:
      k_active  = 0.80 yr⁻¹
      k_slow    = 0.030 yr⁻¹
      k_passive = 0.0045 yr⁻¹

    Decay fraction allocations (partitioning to CO₂ / other pools):
      Active:  55 % → CO₂, 30 % → Slow, 15 % → Passive
      Slow:    60 % → CO₂, 40 % → Passive
      Passive: 100 % → CO₂ (then re-humified fraction is re-added)
    """
    ft = temperature_modifier(mean_temp_c)
    fm = moisture_modifier(
        mean_soil_water_mm, soil.field_capacity_mm_per_m, soil.wilting_point_mm_per_m
    )
    env = ft * fm

    # Rate constants (yr⁻¹)
    k_active = 0.80 * env
    k_slow = 0.030 * env
    k_passive = 0.0045 * env

    # Compute fluxes
    dec_active = pools.active_t_ha * k_active
    dec_slow = pools.slow_t_ha * k_slow
    dec_passive = pools.passive_t_ha * k_passive

    fluxes = CarbonFluxes(
        active_to_slow=dec_active * 0.30,
        active_to_passive=dec_active * 0.15,
        active_to_co2=dec_active * 0.55,
        slow_to_passive=dec_slow * 0.40,
        slow_to_co2=dec_slow * 0.60,
        passive_to_co2=dec_passive,
    )

    # Update pools
    new_active = (
        pools.active_t_ha - dec_active + carbon_input_t_ha * 0.50  # FOM → active
    )
    new_slow = (
        pools.slow_t_ha
        + fluxes.active_to_slow
        - dec_slow
        + carbon_input_t_ha * 0.25  # FOM → slow
    )
    new_passive = (
        pools.passive_t_ha
        + fluxes.active_to_passive
        + fluxes.slow_to_passive
        - dec_passive
    )
    # Inert pool is unchanged by decomposition
    new_pools = CarbonPools(
        active_t_ha=max(0.01, new_active),
        slow_t_ha=max(0.1, new_slow),
        passive_t_ha=max(1.0, new_passive),
        inert_t_ha=pools.inert_t_ha,
    )

    # N mineralisation (C:N ratio approach; C:N active ≈ 10, slow ≈ 14, passive ≈ 12)
    n_mineralised = dec_active / 10.0 + dec_slow / 14.0 + dec_passive / 12.0  # t N ha⁻¹
    n_mineralised_kg = n_mineralised * 1000.0  # kg N ha⁻¹

    # DNDC-inspired N₂O (nitrification + denitrification, simplified)
    # N₂O = 1.25 % of mineral N under aerobic; 3 % under anaerobic
    n2o_factor = 0.03 if is_anaerobic else 0.0125
    fluxes.n2o_kg_ha = nitrogen.mineral_n_kg_ha * n2o_factor

    # CH₄ from wetland / flooded rice (DNDC-inspired)
    fluxes.ch4_kg_ha = max(0.0, pools.active_t_ha * 50.0) if is_anaerobic else 0.0

    # Update N pools
    new_nitrogen = NitrogenPools(
        ammonium_kg_ha=max(0.0, nitrogen.ammonium_kg_ha + n_mineralised_kg * 0.6),
        nitrate_kg_ha=max(
            0.0, nitrogen.nitrate_kg_ha + n_mineralised_kg * 0.4 - fluxes.n2o_kg_ha
        ),
    )

    return new_pools, new_nitrogen, fluxes


# ---------------------------------------------------------------------------
# Main model class
# ---------------------------------------------------------------------------


class SoilCarbonModel:
    """
    Multi-year soil organic carbon and nitrogen cycling model.
    نموذج دوران الكربون العضوي والنيتروجين متعدد السنوات.

    Inspired by RothC (carbon pools) and DNDC (GHG emissions).
    Usage::

        model = SoilCarbonModel()
        result = model.simulate(
            soil=SoilProfile(organic_carbon_pct=1.2),
            years=20,
            mean_temp_c=18.0,
            annual_carbon_input_t_ha=2.5,
        )
        print(result.outputs["final_soc_t_ha"])
    """

    def simulate(
        self,
        soil: SoilProfile,
        years: int = 20,
        mean_temp_c: float = 18.0,
        mean_soil_water_fraction: float = 0.6,
        annual_carbon_input_t_ha: float = 2.0,
        is_anaerobic: bool = False,
    ) -> ModelResult:
        """
        Simulate multi-year SOC dynamics.
        محاكاة ديناميكيات الكربون العضوي متعددة السنوات.

        Args:
            soil: Soil physical properties.
            years: Number of years to simulate.
            mean_temp_c: Mean annual temperature (°C).
            mean_soil_water_fraction: Mean soil water as fraction of field capacity.
            annual_carbon_input_t_ha: Annual fresh organic matter input (t C ha⁻¹ yr⁻¹).
            is_anaerobic: True for flooded/wetland soils (rice paddies).

        Returns:
            ModelResult with final SOC, N₂O and CH₄ emissions timeline.
        """
        # Initialise pools from measured SOC
        initial_soc = (
            soil.organic_carbon_pct
            / 100.0
            * soil.bulk_density_g_cm3
            * soil.depth_m
            * 10000.0
        )
        # Approximate pool partitioning from initial SOC
        pools = CarbonPools(
            active_t_ha=initial_soc * 0.03,
            slow_t_ha=initial_soc * 0.35,
            passive_t_ha=initial_soc * 0.50,
            inert_t_ha=initial_soc * 0.12,
        )
        nitrogen = NitrogenPools()

        mean_sw_mm = (
            mean_soil_water_fraction * soil.field_capacity_mm_per_m * soil.depth_m
        )
        annual_log = []
        cumulative_n2o = 0.0
        cumulative_ch4 = 0.0

        for yr in range(1, years + 1):
            pools, nitrogen, fluxes = annual_decomposition(
                pools,
                nitrogen,
                soil,
                mean_temp_c,
                mean_sw_mm,
                annual_carbon_input_t_ha,
                is_anaerobic,
            )
            cumulative_n2o += fluxes.n2o_kg_ha
            cumulative_ch4 += fluxes.ch4_kg_ha
            annual_log.append(
                {
                    "year": yr,
                    "total_soc_t_ha": round(pools.total_soc_t_ha, 2),
                    "active_t_ha": round(pools.active_t_ha, 3),
                    "slow_t_ha": round(pools.slow_t_ha, 2),
                    "passive_t_ha": round(pools.passive_t_ha, 2),
                    "mineral_n_kg_ha": round(nitrogen.mineral_n_kg_ha, 1),
                    "n2o_kg_ha": round(fluxes.n2o_kg_ha, 3),
                    "ch4_kg_ha": round(fluxes.ch4_kg_ha, 2),
                }
            )

        final_soc = pools.total_soc_t_ha
        final_soc_pct = (
            final_soc / (soil.bulk_density_g_cm3 * soil.depth_m * 10000.0) * 100.0
        )

        logger.info(
            "soil_carbon_simulation_complete",
            years=years,
            initial_soc_t_ha=round(initial_soc, 2),
            final_soc_t_ha=round(final_soc, 2),
            cumulative_n2o_kg_ha=round(cumulative_n2o, 2),
        )

        return ModelResult(
            model_name="SoilCarbonModel (RothC/DNDC-inspired)",
            model_type=ModelType.SOIL_CARBON,
            success=True,
            message="Soil carbon simulation completed",
            message_ar="اكتملت محاكاة الكربون العضوي للتربة",
            outputs={
                "initial_soc_t_ha": round(initial_soc, 2),
                "final_soc_t_ha": round(final_soc, 2),
                "soc_change_t_ha": round(final_soc - initial_soc, 2),
                "final_soc_pct": round(final_soc_pct, 3),
                "final_mineral_n_kg_ha": round(nitrogen.mineral_n_kg_ha, 1),
                "cumulative_n2o_kg_ha": round(cumulative_n2o, 2),
                "cumulative_ch4_kg_ha": round(cumulative_ch4, 2),
                "years_simulated": years,
            },
            metadata={"annual_log": annual_log},
        )
