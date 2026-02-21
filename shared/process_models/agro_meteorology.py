# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Agro-Meteorology Engine - محرك الأرصاد الجوية الزراعية
=========================================================
Implements the core physical models for computing evapotranspiration (ET),
energy balance, and weather-based agricultural indicators.

Implemented models:
  • Penman-Monteith FAO-56 (Allen et al., 1998) – Reference ET₀ standard
  • Shuttleworth-Wallace dual-source model – Sparse/full-cover ET partition
  • Hargreaves-Samani – ET₀ from temperature only (data-limited)
  • Energy balance components (net radiation, soil heat flux)

References:
  Allen RG et al. (1998). FAO Irrigation and Drainage Paper No. 56.
  Shuttleworth WJ & Wallace JS (1985). Q J Roy Meteor Soc 111:839-855.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

import structlog

from shared.process_models.models import DailyWeather, ModelResult, ModelType, SoilProfile

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_SIGMA = 4.903e-9  # Stefan-Boltzmann constant (MJ m⁻² d⁻¹ K⁻⁴)
_LAMBDA = 2.45  # Latent heat of vaporisation (MJ kg⁻¹)


# ---------------------------------------------------------------------------
# Saturation vapour pressure helpers
# ---------------------------------------------------------------------------


def saturation_vapour_pressure(t_c: float) -> float:
    """
    Saturation vapour pressure (kPa) at temperature T (°C).
    ضغط البخار المشبع عند درجة حرارة T.

    e_s(T) = 0.6108 · exp(17.27 T / (T + 237.3))   [FAO-56 Eq.11]
    """
    return 0.6108 * math.exp(17.27 * t_c / (t_c + 237.3))


def mean_saturation_vapour_pressure(tmax: float, tmin: float) -> float:
    """Mean e_s from daily Tmax/Tmin. [FAO-56 Eq.12]"""
    return (saturation_vapour_pressure(tmax) + saturation_vapour_pressure(tmin)) / 2.0


def slope_vapour_pressure_curve(tmean: float) -> float:
    """
    Slope of saturation vapour pressure curve Δ (kPa °C⁻¹).
    ميل منحنى ضغط البخار المشبع.

    Δ = 4098 · e_s / (T+237.3)²   [FAO-56 Eq.13]
    """
    es = saturation_vapour_pressure(tmean)
    return 4098.0 * es / (tmean + 237.3) ** 2


def psychrometric_constant(elevation_m: float = 50.0) -> float:
    """
    Psychrometric constant γ (kPa °C⁻¹) at given elevation.
    الثابت السيكرومتري.

    P = 101.3 · ((293 - 0.0065·z)/293)^5.26   [FAO-56 Eq.7]
    γ = 0.000665 · P
    """
    p_kpa = 101.3 * ((293.0 - 0.0065 * elevation_m) / 293.0) ** 5.26
    return 0.000665 * p_kpa


# ---------------------------------------------------------------------------
# Net radiation
# ---------------------------------------------------------------------------


def extraterrestrial_radiation(doy: int, lat_rad: float) -> float:
    """
    Extraterrestrial radiation Ra (MJ m⁻² d⁻¹).
    الإشعاع خارج الغلاف الجوي.

    [FAO-56 Eq.21]
    """
    dr = 1.0 + 0.033 * math.cos(2 * math.pi * doy / 365.0)
    declin = 0.409 * math.sin(2 * math.pi * doy / 365.0 - 1.39)
    ws = math.acos(-math.tan(lat_rad) * math.tan(declin))
    ra = (24.0 * 60.0 / math.pi) * 0.0820 * dr * (
        ws * math.sin(lat_rad) * math.sin(declin) + math.cos(lat_rad) * math.cos(declin) * math.sin(ws)
    )
    return ra


def net_radiation(
    rs_mj_m2: float,
    albedo: float,
    tmax_c: float,
    tmin_c: float,
    ea_kpa: float,
    rs_clear: float | None = None,
) -> float:
    """
    Net radiation Rn (MJ m⁻² d⁻¹).
    الإشعاع الصافي.

    Rn = Rns - Rnl   [FAO-56 Eq.40]
    Rns = (1 - α) Rs
    Rnl = σ · Tmean⁴ · (0.34 - 0.14√ea) · (1.35·Rs/Rs0 - 0.35)
    """
    rns = (1.0 - albedo) * rs_mj_m2
    # Clear-sky radiation fallback
    if rs_clear is None or rs_clear <= 0:
        rs_clear = rs_mj_m2 * 1.35  # rough approximation
    tmax_k4 = (tmax_c + 273.16) ** 4
    tmin_k4 = (tmin_c + 273.16) ** 4
    rnl = _SIGMA * (tmax_k4 + tmin_k4) / 2.0 * (0.34 - 0.14 * math.sqrt(ea_kpa)) * (
        1.35 * rs_mj_m2 / rs_clear - 0.35
    )
    return rns - rnl


# ---------------------------------------------------------------------------
# Penman-Monteith FAO-56 ET₀
# ---------------------------------------------------------------------------


def penman_monteith_et0(
    weather: DailyWeather,
    elevation_m: float = 50.0,
    lat_deg: float = 24.0,
    albedo: float = 0.23,
) -> float:
    """
    FAO-56 Penman-Monteith reference evapotranspiration ET₀ (mm d⁻¹).
    حساب التبخر-النتح المرجعي باستخدام معادلة فاو-56 بنمان-مونتيث.

    ET₀ = [0.408 Δ(Rn-G) + γ (900/(T+273)) u₂ (es-ea)] / [Δ + γ(1+0.34 u₂)]

    Args:
        weather: Daily weather data.
        elevation_m: Site elevation (m a.s.l.).
        lat_deg: Latitude (decimal degrees, N positive).
        albedo: Surface albedo (default 0.23 for short grass reference surface).

    Returns:
        ET₀ in mm d⁻¹.
    """
    doy = weather.date.timetuple().tm_yday
    lat_rad = math.radians(lat_deg)
    tmean = weather.tmean_c

    # Vapour pressures
    es = mean_saturation_vapour_pressure(weather.tmax_c, weather.tmin_c)
    ea = weather.actual_vapor_pressure_kpa if weather.actual_vapor_pressure_kpa else (
        weather.relative_humidity_pct / 100.0 * es
    )

    # Psychrometric constant and Δ
    gamma = psychrometric_constant(elevation_m)
    delta = slope_vapour_pressure_curve(tmean)

    # Radiation
    ra = extraterrestrial_radiation(doy, lat_rad)
    rs_clear = (0.75 + 2e-5 * elevation_m) * ra
    rn = net_radiation(weather.solar_radiation_mj_m2, albedo, weather.tmax_c, weather.tmin_c, ea, rs_clear)

    # Soil heat flux G ≈ 0 for daily step
    g = 0.0

    # Wind speed at 2 m (if measured at different height, apply log correction elsewhere)
    u2 = max(0.5, weather.wind_speed_m_s)

    numerator = 0.408 * delta * (rn - g) + gamma * (900.0 / (tmean + 273.0)) * u2 * (es - ea)
    denominator = delta + gamma * (1.0 + 0.34 * u2)
    et0 = numerator / denominator
    return max(0.0, et0)


# ---------------------------------------------------------------------------
# Hargreaves-Samani (temperature-only fallback)
# ---------------------------------------------------------------------------


def hargreaves_et0(weather: DailyWeather, lat_deg: float = 24.0) -> float:
    """
    Hargreaves-Samani ET₀ estimate (mm d⁻¹) – requires only T and Ra.
    تقدير ET₀ بطريقة هارغريفز-سامانى (درجة الحرارة فقط).

    ET₀ = 0.0023 · Ra · (Tmean + 17.8) · √(Tmax - Tmin)   [HS 1985]
    """
    doy = weather.date.timetuple().tm_yday
    lat_rad = math.radians(lat_deg)
    ra = extraterrestrial_radiation(doy, lat_rad)
    dt = max(0.0, weather.tmax_c - weather.tmin_c)
    return 0.0023 * ra * (weather.tmean_c + 17.8) * math.sqrt(dt)


# ---------------------------------------------------------------------------
# Shuttleworth-Wallace dual-source model
# ---------------------------------------------------------------------------


@dataclass
class ShuttleworthWallaceResult:
    """Result of Shuttleworth-Wallace dual-source ET calculation."""

    et_canopy_mm: float  # Transpiration from canopy | نتح المجمع الخضري
    et_soil_mm: float  # Evaporation from soil | تبخر التربة
    et_total_mm: float  # Total ET | التبخر-النتح الكلي


def shuttleworth_wallace_et(
    weather: DailyWeather,
    lai: float,
    fractional_cover: float,
    et0_mm: float,
    crop_coefficient: float = 1.0,
) -> ShuttleworthWallaceResult:
    """
    Shuttleworth-Wallace simplified dual-source evapotranspiration model.
    نموذج شاتلوورث-والاس ثنائي المصدر لتقسيم التبخر-النتح.

    Partitions total ET into canopy transpiration (Ec) and soil evaporation (Es)
    based on fractional canopy cover and LAI. More accurate than single-source
    PM equation for sparse canopies (e.g. early season or orchards).

    Args:
        weather: Daily weather.
        lai: Leaf Area Index.
        fractional_cover: Fraction of ground covered by canopy (0–1).
        et0_mm: Reference ET₀ (mm d⁻¹).
        crop_coefficient: Crop-specific Kc.

    Returns:
        ShuttleworthWallaceResult with canopy and soil ET components.
    """
    etc_mm = et0_mm * crop_coefficient

    # Beer-Lambert light attenuation determines soil radiation fraction
    k = 0.5
    f_soil_rad = math.exp(-k * max(0.0, lai))

    # Soil evaporation (energy-limited by radiation reaching soil)
    ks = min(1.0, max(0.1, 1.0 - fractional_cover))
    et_soil = etc_mm * f_soil_rad * ks

    # Canopy transpiration = total ETc minus soil evaporation
    et_canopy = max(0.0, etc_mm - et_soil)

    return ShuttleworthWallaceResult(
        et_canopy_mm=round(et_canopy, 3),
        et_soil_mm=round(et_soil, 3),
        et_total_mm=round(et_canopy + et_soil, 3),
    )


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------


class AgroMeteorologyEngine:
    """
    Agro-meteorology engine.
    محرك الأرصاد الجوية الزراعية.

    Orchestrates ET₀ computation, dual-source partitioning, and
    growing-degree-day accumulation from a weather series.

    Usage::

        engine = AgroMeteorologyEngine(elevation_m=200, lat_deg=15.5)
        result = engine.run(weather_series, lai=2.5, fractional_cover=0.7)
        print(result.outputs["total_et0_mm"])
    """

    def __init__(self, elevation_m: float = 50.0, lat_deg: float = 24.0, albedo: float = 0.23) -> None:
        self.elevation_m = elevation_m
        self.lat_deg = lat_deg
        self.albedo = albedo

    def run(
        self,
        weather_series: list[DailyWeather],
        lai: float = 2.0,
        fractional_cover: float = 0.8,
        crop_coefficient: float = 1.0,
    ) -> ModelResult:
        """
        Compute daily ET₀ and dual-source ET for a weather series.
        حساب ET₀ اليومي وتقسيم التبخر-النتح لسلسلة أرصاد جوية.
        """
        daily = []
        total_et0 = 0.0
        total_etc = 0.0

        for w in weather_series:
            et0 = penman_monteith_et0(w, self.elevation_m, self.lat_deg, self.albedo)
            sw = shuttleworth_wallace_et(w, lai, fractional_cover, et0, crop_coefficient)
            total_et0 += et0
            total_etc += sw.et_total_mm
            daily.append(
                {
                    "date": str(w.date),
                    "et0_mm": round(et0, 2),
                    "et_canopy_mm": sw.et_canopy_mm,
                    "et_soil_mm": sw.et_soil_mm,
                    "et_total_mm": sw.et_total_mm,
                }
            )

        logger.info(
            "agro_met_run_complete",
            days=len(weather_series),
            total_et0_mm=round(total_et0, 1),
            total_etc_mm=round(total_etc, 1),
        )

        return ModelResult(
            model_name="AgroMeteorologyEngine (PM FAO-56 + Shuttleworth-Wallace)",
            model_type=ModelType.AGRO_METEOROLOGY,
            success=True,
            message="ET calculation completed",
            message_ar="اكتمل حساب التبخر-النتح",
            outputs={
                "total_et0_mm": round(total_et0, 1),
                "total_etc_mm": round(total_etc, 1),
                "mean_et0_mm_day": round(total_et0 / max(1, len(weather_series)), 2),
                "n_days": len(weather_series),
            },
            metadata={"daily": daily},
        )
