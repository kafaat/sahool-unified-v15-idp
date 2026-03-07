# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Pest & Disease Epidemiological Models - نماذج وبائيات الآفات والأمراض
======================================================================
Mechanistic population-dynamics models for crop pest and disease management.

Implemented models:
  • SIR (Susceptible-Infected-Removed) – fungal / bacterial disease spread
  • Degree-Day accumulation – insect phenology and pest emergence timing
  • Lotka-Volterra predator-prey – pest vs. natural enemy dynamics

Reference article sections covered: Chapter 10 (Pest/Disease Epidemiology)

References:
  Kermack WO & McKendrick AG (1927). Contribution to the mathematical theory
  of epidemics. Proc R Soc London Ser A 115:700-721.
  Madden LV et al. (2007). The Study of Plant Disease Epidemics. APS Press.
  Baumgärtner J & Baronio P (1998). Degree-day models for gypsy moth...
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import structlog

from shared.process_models.models import DailyWeather, ModelResult, ModelType

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Pest / disease identifiers
# ---------------------------------------------------------------------------


class PestType(StrEnum):
    """Known pest/disease types with degree-day parameters."""

    RED_PALM_WEEVIL = "red_palm_weevil"
    WHEAT_RUST = "wheat_rust"
    APHID = "aphid"
    WHITEFLY = "whitefly"
    FUSARIUM_WILT = "fusarium_wilt"
    POWDERY_MILDEW = "powdery_mildew"
    LOCUST = "locust"
    ARMYWORM = "armyworm"
    GENERIC = "generic"


# ---------------------------------------------------------------------------
# SIR model
# ---------------------------------------------------------------------------


@dataclass
class SIRState:
    """
    SIR epidemiological compartment state.
    حالة أحواض نموذج SIR الوبائي.

    Fractions of host plant population:
      S – Susceptible (healthy) | القابلة للإصابة (سليمة)
      I – Infected               | المصابة
      R – Removed (dead / resistant / harvested) | المُزالة
    """

    susceptible: float = 0.95  # fraction [0, 1]
    infected: float = 0.05  # fraction [0, 1]
    removed: float = 0.0  # fraction [0, 1]

    @property
    def total(self) -> float:
        return self.susceptible + self.infected + self.removed


# Disease-specific SIR parameters (β = transmission, γ = removal rate, day⁻¹)
_SIR_PARAMS: dict[PestType, tuple[float, float]] = {
    PestType.WHEAT_RUST: (0.35, 0.10),
    PestType.POWDERY_MILDEW: (0.30, 0.08),
    PestType.FUSARIUM_WILT: (0.20, 0.05),
    PestType.APHID: (0.40, 0.15),
    PestType.WHITEFLY: (0.25, 0.08),
    PestType.GENERIC: (0.20, 0.07),
}


def sir_daily_step(
    state: SIRState,
    beta: float,
    gamma: float,
    temp_modifier: float = 1.0,
) -> SIRState:
    """
    Advance SIR model by one day.
    تقدم نموذج SIR ليوم واحد.

    dS/dt = -β S I                  (new infections)
    dI/dt =  β S I − γ I            (infected minus removed)
    dR/dt =  γ I                    (removed/immune)

    Temperature modifier scales transmission rate.
    """
    beta_eff = beta * temp_modifier
    new_infections = beta_eff * state.susceptible * state.infected
    new_removed = gamma * state.infected

    new_s = max(0.0, state.susceptible - new_infections)
    new_i = max(0.0, state.infected + new_infections - new_removed)
    new_r = min(1.0, state.removed + new_removed)

    return SIRState(susceptible=new_s, infected=new_i, removed=new_r)


# ---------------------------------------------------------------------------
# Degree-day model for insect phenology
# ---------------------------------------------------------------------------


@dataclass
class InsectPhenoParams:
    """
    Degree-day parameters for insect development.
    معاملات الدرجات-الأيام لتطور الحشرات.
    """

    t_base_c: float = 10.0  # Lower developmental threshold (°C) | عتبة التطور الدنيا
    t_upper_c: float = 35.0  # Upper threshold (°C) | العتبة العليا
    dd_egg_hatch: float = 120.0  # DD to egg hatch | وحدات الحرارة للفقس
    dd_adult_emergence: float = 350.0  # DD to adult | وحدات الحرارة للبلوغ
    dd_generation: float = 600.0  # DD per complete generation | وحدات الحرارة للجيل الكامل


# Pre-calibrated insect parameters for key regional pests
INSECT_PARAMS: dict[PestType, InsectPhenoParams] = {
    PestType.RED_PALM_WEEVIL: InsectPhenoParams(
        t_base_c=10.0,
        t_upper_c=38.0,
        dd_egg_hatch=100.0,
        dd_adult_emergence=320.0,
        dd_generation=550.0,
    ),
    PestType.APHID: InsectPhenoParams(
        t_base_c=4.0,
        t_upper_c=32.0,
        dd_egg_hatch=80.0,
        dd_adult_emergence=200.0,
        dd_generation=350.0,
    ),
    PestType.ARMYWORM: InsectPhenoParams(
        t_base_c=9.0,
        t_upper_c=36.0,
        dd_egg_hatch=130.0,
        dd_adult_emergence=400.0,
        dd_generation=700.0,
    ),
    PestType.LOCUST: InsectPhenoParams(
        t_base_c=14.0,
        t_upper_c=40.0,
        dd_egg_hatch=200.0,
        dd_adult_emergence=500.0,
        dd_generation=800.0,
    ),
    PestType.GENERIC: InsectPhenoParams(),
}


def daily_degree_days(weather: DailyWeather, t_base: float, t_upper: float) -> float:
    """
    Single-triangle method for degree-day computation.
    طريقة المثلث الأحادي لحساب الدرجات-الأيام.
    """
    tmax = min(weather.tmax_c, t_upper)
    tmin = max(weather.tmin_c, t_base)
    if tmax < t_base or tmin > t_upper:
        return 0.0
    return max(0.0, (tmax + tmin) / 2.0 - t_base)


# ---------------------------------------------------------------------------
# Lotka-Volterra predator-prey
# ---------------------------------------------------------------------------


@dataclass
class LVState:
    """
    Lotka-Volterra pest (prey) – natural enemy (predator) state.
    حالة نموذج لوتكا-فولتيرا للآفة والعدو الطبيعي.
    """

    pest_density: float = 100.0  # Pest population (ind. m⁻²) | كثافة الآفة
    enemy_density: float = 5.0  # Natural enemy population (ind. m⁻²) | كثافة العدو الطبيعي


def lv_daily_step(
    state: LVState,
    pest_growth_rate: float = 0.15,
    predation_rate: float = 0.01,
    enemy_growth_rate: float = 0.005,
    enemy_mortality_rate: float = 0.08,
    carrying_capacity: float = 5000.0,
) -> LVState:
    """
    Advance Lotka-Volterra model by one day.
    تقدم نموذج لوتكا-فولتيرا ليوم واحد.

    dN/dt = r·N·(1 - N/K) − α·N·P     (pest with logistic growth)
    dP/dt = β·N·P − δ·P                (enemy)
    """
    n = state.pest_density
    p = state.enemy_density

    dn = pest_growth_rate * n * (1.0 - n / carrying_capacity) - predation_rate * n * p
    dp = enemy_growth_rate * n * p - enemy_mortality_rate * p

    return LVState(
        pest_density=max(0.0, n + dn),
        enemy_density=max(0.0, p + dp),
    )


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------


class PestEpidemiologyEngine:
    """
    Integrated pest epidemiology and population dynamics engine.
    محرك وبائيات الآفات وديناميكيات السكان المتكامل.

    Combines:
      • SIR disease spread model (temperature-modulated)
      • Degree-day based pest phenology
      • Lotka-Volterra predator-prey dynamics

    Usage::

        engine = PestEpidemiologyEngine()

        # Disease spread
        result = engine.simulate_disease(
            pest_type=PestType.WHEAT_RUST,
            weather_series=[DailyWeather(...)],
            initial_infected_fraction=0.02,
        )

        # Pest phenology
        result2 = engine.simulate_pest_phenology(
            pest_type=PestType.RED_PALM_WEEVIL,
            weather_series=[DailyWeather(...)],
        )
    """

    def simulate_disease(
        self,
        pest_type: PestType,
        weather_series: list[DailyWeather],
        initial_infected_fraction: float = 0.01,
    ) -> ModelResult:
        """
        SIR disease spread simulation.
        محاكاة انتشار المرض باستخدام نموذج SIR.
        """
        beta, gamma = _SIR_PARAMS.get(pest_type, _SIR_PARAMS[PestType.GENERIC])
        state = SIRState(
            susceptible=1.0 - initial_infected_fraction,
            infected=initial_infected_fraction,
            removed=0.0,
        )
        daily_log = []
        peak_infected = initial_infected_fraction
        peak_day = 0

        for day_idx, weather in enumerate(weather_series):
            # Temperature modifier (Q10 style, reference 20°C)
            temp_mod = 2.0 ** ((weather.tmean_c - 20.0) / 10.0)
            temp_mod = max(0.2, min(2.0, temp_mod))
            # Leaf wetness proxy (humidity > 80% → wet)
            wetness_mod = 1.5 if weather.relative_humidity_pct > 80.0 else 1.0
            state = sir_daily_step(state, beta, gamma, temp_mod * wetness_mod)

            if state.infected > peak_infected:
                peak_infected = state.infected
                peak_day = day_idx + 1

            daily_log.append(
                {
                    "day": day_idx + 1,
                    "susceptible": round(state.susceptible, 4),
                    "infected": round(state.infected, 4),
                    "removed": round(state.removed, 4),
                }
            )
            if state.infected < 0.001 and day_idx > 10:
                break

        r0 = beta / gamma  # Basic reproduction number
        epidemic = peak_infected > 0.20

        logger.info(
            "disease_simulation_complete",
            pest_type=pest_type,
            peak_infected=round(peak_infected, 3),
            r0=round(r0, 2),
            epidemic=epidemic,
        )

        return ModelResult(
            model_name=f"PestEpidemiologyEngine (SIR) – {pest_type}",
            model_type=ModelType.PEST_EPIDEMIOLOGY,
            success=True,
            message="Disease spread simulation completed",
            message_ar="اكتملت محاكاة انتشار المرض",
            outputs={
                "pest_type": pest_type,
                "r0_reproduction_number": round(r0, 2),
                "peak_infected_fraction": round(peak_infected, 4),
                "peak_day": peak_day,
                "epidemic_risk": epidemic,
                "final_removed_fraction": round(state.removed, 4),
                "days_simulated": len(daily_log),
            },
            metadata={"daily_log": daily_log},
        )

    def simulate_pest_phenology(
        self,
        pest_type: PestType,
        weather_series: list[DailyWeather],
    ) -> ModelResult:
        """
        Degree-day pest phenology prediction.
        تنبؤ بفينولوجيا الآفة باستخدام الدرجات-الأيام.
        """
        params = INSECT_PARAMS.get(pest_type, INSECT_PARAMS[PestType.GENERIC])
        cum_dd = 0.0
        daily_log = []
        egg_hatch_day = None
        adult_emergence_day = None
        generation_1_day = None

        for day_idx, weather in enumerate(weather_series):
            dd = daily_degree_days(weather, params.t_base_c, params.t_upper_c)
            cum_dd += dd

            if egg_hatch_day is None and cum_dd >= params.dd_egg_hatch:
                egg_hatch_day = day_idx + 1
            if adult_emergence_day is None and cum_dd >= params.dd_adult_emergence:
                adult_emergence_day = day_idx + 1
            if generation_1_day is None and cum_dd >= params.dd_generation:
                generation_1_day = day_idx + 1
                break  # stop after first generation

            daily_log.append({"day": day_idx + 1, "dd": round(dd, 2), "cum_dd": round(cum_dd, 1)})

        logger.info(
            "pest_phenology_simulation_complete",
            pest_type=pest_type,
            cum_dd=round(cum_dd, 1),
            adult_emergence_day=adult_emergence_day,
        )

        return ModelResult(
            model_name=f"PestEpidemiologyEngine (DegreeDay) – {pest_type}",
            model_type=ModelType.PEST_EPIDEMIOLOGY,
            success=True,
            message="Pest phenology simulation completed",
            message_ar="اكتملت محاكاة فينولوجيا الآفة",
            outputs={
                "pest_type": pest_type,
                "cumulative_dd": round(cum_dd, 1),
                "egg_hatch_day": egg_hatch_day,
                "adult_emergence_day": adult_emergence_day,
                "generation_1_complete_day": generation_1_day,
                "days_simulated": len(daily_log),
            },
            metadata={"daily_log": daily_log[:30]},  # truncate log
        )

    def simulate_predator_prey(
        self,
        initial_pest_density: float = 100.0,
        initial_enemy_density: float = 5.0,
        days: int = 60,
    ) -> ModelResult:
        """
        Lotka-Volterra predator-prey dynamics for IPM.
        ديناميكيات المفترس-الفريسة لإدارة الآفات المتكاملة.
        """
        state = LVState(pest_density=initial_pest_density, enemy_density=initial_enemy_density)
        daily_log = []

        for day in range(1, days + 1):
            state = lv_daily_step(state)
            daily_log.append(
                {
                    "day": day,
                    "pest": round(state.pest_density, 1),
                    "enemy": round(state.enemy_density, 2),
                }
            )
            if state.pest_density < 0.1:
                break

        return ModelResult(
            model_name="PestEpidemiologyEngine (Lotka-Volterra)",
            model_type=ModelType.PEST_EPIDEMIOLOGY,
            success=True,
            message="Predator-prey simulation completed",
            message_ar="اكتملت محاكاة المفترس-الفريسة",
            outputs={
                "final_pest_density": round(state.pest_density, 2),
                "final_enemy_density": round(state.enemy_density, 3),
                "days_simulated": len(daily_log),
            },
            metadata={"daily_log": daily_log},
        )
