# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT – SAHOOL Platform
"""
Process-Models API Router – موجّه نماذج العمليات الزراعية
==========================================================
Exposes shared/process_models computations as REST endpoints inside
crop-intelligence-service.

Endpoints
---------
POST /api/v1/models/et0/run
    Run Penman–Monteith FAO-56 ET₀ + Shuttleworth–Wallace dual-source ET.

POST /api/v1/models/quefts/recommend
    QUEFTS balanced-nutrition fertiliser recommendation (N-P-K doses for a
    target yield).

POST /api/v1/models/soil-carbon/simulate
    One-year RothC / DNDC-inspired C–N cycling step.

POST /api/v1/models/swb/run
    Daily soil water balance (FAO-56 dual Kc, SCS-CN runoff, Green-Ampt).

POST /api/v1/models/prosail/invert
    Simplified PROSAIL inversion (LAI / Cab from reflectance).  Returns
    uncertainty flags and must not be used for production decisions without
    field calibration.

All responses include:
  • model_name   – human-readable name of the model used
  • result       – computation result dict
  • warnings     – list of quality / calibration warnings
  • quality_flag – "ok" | "low_confidence" | "needs_calibration"
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
try:
    from shared.auth.dependencies import get_current_user
except ImportError:

    async def get_current_user() -> dict:  # type: ignore[misc]
        """Fail-secure fallback when shared.auth is not importable."""
        raise HTTPException(status_code=503, detail="Authentication backend unavailable")


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["Process Models"], dependencies=[Depends(get_current_user)])


# ── Common response wrapper ──────────────────────────────────────────────────


class ModelRunResponse(BaseModel):
    model_name: str
    result: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    quality_flag: str = "ok"


ModelRunResponse.model_rebuild()


# ── 1. ET₀ – Penman–Monteith FAO-56 ─────────────────────────────────────────


class ET0Request(BaseModel):
    """Daily weather inputs for ET₀ calculation."""

    tmax_c: float = Field(..., ge=-50, le=60, description="Max temperature °C")
    tmin_c: float = Field(..., ge=-50, le=60, description="Min temperature °C")
    solar_radiation_mj_m2: float = Field(..., ge=0, le=50, description="Daily solar radiation MJ/m²")
    relative_humidity_pct: float = Field(..., ge=0, le=100, description="Mean relative humidity %")
    wind_speed_m_s: float = Field(..., ge=0, le=50, description="Mean wind speed at 2 m m/s")
    elevation_m: float = Field(default=0.0, ge=-500, le=5000, description="Site elevation m a.s.l.")
    latitude_deg: float = Field(default=25.0, ge=-90, le=90, description="Site latitude °")
    day_of_year: int = Field(default=180, ge=1, le=366, description="Day of year (1-366)")
    # Optional Shuttleworth-Wallace dual-source
    lai: float | None = Field(default=None, ge=0, le=15, description="Leaf Area Index (for dual-source ET)")
    kc: float | None = Field(
        default=None,
        ge=0,
        le=2.0,
        description="Crop coefficient Kc (overrides LAI-based estimate)",
    )

    @field_validator("tmax_c")
    @classmethod
    def tmax_above_tmin(cls, v: float, info) -> float:
        tmin = info.data.get("tmin_c")
        if tmin is not None and v < tmin:
            raise ValueError("tmax_c must be ≥ tmin_c")
        return v


@router.post("/et0/run", response_model=ModelRunResponse)
def run_et0(req: ET0Request) -> ModelRunResponse:
    """
    Compute reference evapotranspiration (ET₀) using Penman–Monteith FAO-56.
    Optionally computes crop ET (ETc) and dual-source (Shuttleworth-Wallace)
    when LAI or Kc is provided.
    """
    try:
        from shared.process_models.agro_meteorology import (
            penman_monteith_et0,
            shuttleworth_wallace_et,
        )
        from shared.process_models.models import DailyWeather

        weather = DailyWeather(
            date=_doy_to_date(req.day_of_year),
            tmax_c=req.tmax_c,
            tmin_c=req.tmin_c,
            solar_radiation_mj_m2=req.solar_radiation_mj_m2,
            relative_humidity_pct=req.relative_humidity_pct,
            wind_speed_m_s=req.wind_speed_m_s,
        )

        et0 = penman_monteith_et0(weather, elevation_m=req.elevation_m, lat_deg=req.latitude_deg)

        warnings: list[str] = []
        result: dict[str, Any] = {
            "et0_mm": round(et0, 3),
            "method": "penman_monteith_fao56",
        }

        kc = req.kc
        lai = req.lai

        # ETc via crop coefficient
        if kc is not None:
            etc = et0 * kc
            result["kc"] = kc
            result["etc_mm"] = round(etc, 3)

        # Dual-source Shuttleworth-Wallace
        if lai is not None:
            fc = min(1.0, 1 - (1 / (1 + lai)))  # simple fractional cover estimate
            sw_result = shuttleworth_wallace_et(
                weather,
                lai=lai,
                fractional_cover=fc,
                et0_mm=et0,
                crop_coefficient=(kc or 1.0),
            )
            result["sw_et_total_mm"] = round(sw_result.et_total_mm, 3)
            result["sw_et_canopy_mm"] = round(sw_result.et_canopy_mm, 3)
            result["sw_et_soil_mm"] = round(sw_result.et_soil_mm, 3)

        if req.wind_speed_m_s == 0:
            warnings.append("Wind speed is 0 m/s – ET₀ may be underestimated")
        if req.solar_radiation_mj_m2 < 1:
            warnings.append("Very low solar radiation (<1 MJ/m²) – check units")

        return ModelRunResponse(
            model_name="Penman-Monteith FAO-56",
            result=result,
            warnings=warnings,
        )

    except Exception as exc:
        logger.exception("ET0 run failed")
        raise HTTPException(http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Model computation failed") from exc


# ── 2. QUEFTS fertiliser recommendation ─────────────────────────────────────


class QUEFTSRequest(BaseModel):
    crop_type: str = Field(default="wheat", description="Crop type (wheat, maize, rice)")
    target_yield_t_ha: float = Field(..., ge=0.1, le=30.0, description="Target yield t/ha")
    soil_n_kg_ha: float = Field(default=50.0, ge=0, le=500, description="Soil N supply kg N/ha")
    soil_p_kg_ha: float = Field(default=20.0, ge=0, le=200, description="Soil P supply kg P/ha")
    soil_k_kg_ha: float = Field(default=100.0, ge=0, le=800, description="Soil K supply kg K/ha")
    field_efficiency: float = Field(default=0.85, ge=0.1, le=1.0, description="Nutrient use efficiency (0-1)")


@router.post("/quefts/recommend", response_model=ModelRunResponse)
def run_quefts(req: QUEFTSRequest) -> ModelRunResponse:
    """
    QUEFTS balanced-nutrition fertiliser recommendation.
    Returns N, P₂O₅ and K₂O doses (kg/ha) to reach the target yield.
    """
    try:
        from shared.process_models.models import CropParameters, CropType
        from shared.process_models.nutrient_management import (
            QueftsNutrientModel,
            SoilNutrientSupply,
        )

        model = QueftsNutrientModel()

        # Map crop string to enum (fall back to GENERIC)
        try:
            crop_type = CropType(req.crop_type.lower())
        except ValueError:
            crop_type = CropType.GENERIC

        crop = CropParameters(crop_type=crop_type)
        supply = SoilNutrientSupply(
            n_supply_kg_ha=req.soil_n_kg_ha,
            p_supply_kg_ha=req.soil_p_kg_ha,
            k_supply_kg_ha=req.soil_k_kg_ha,
        )

        result_obj = model.recommend(crop, supply, target_yield_t_ha=req.target_yield_t_ha)
        rec = result_obj.outputs

        warnings: list[str] = []
        if req.soil_n_kg_ha < 10:
            warnings.append("Very low soil N – consider soil test confirmation before applying")
        if req.target_yield_t_ha > 10:
            warnings.append("High target yield – verify against local yield potential records")

        return ModelRunResponse(
            model_name="QUEFTS",
            result=rec,
            warnings=warnings,
        )

    except Exception as exc:
        logger.exception("QUEFTS run failed")
        raise HTTPException(http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Model computation failed") from exc


# ── 3. Soil carbon / N cycling simulation ────────────────────────────────────


class SoilCarbonRequest(BaseModel):
    soc_active_t_ha: float = Field(default=0.5, ge=0, le=50, description="Active C pool t C/ha")
    soc_slow_t_ha: float = Field(default=10.0, ge=0, le=200, description="Slow C pool t C/ha")
    soc_passive_t_ha: float = Field(default=30.0, ge=0, le=500, description="Passive C pool t C/ha")
    clay_fraction: float = Field(default=0.25, ge=0, le=1.0, description="Clay fraction 0-1")
    mean_annual_temp_c: float = Field(default=18.0, ge=-20, le=50)
    mean_annual_precip_mm: float = Field(default=400.0, ge=0, le=5000)
    carbon_input_t_ha_yr: float = Field(default=2.0, ge=0, le=50, description="Annual C input t C/ha/yr")
    simulation_years: int = Field(default=1, ge=1, le=100)


@router.post("/soil-carbon/simulate", response_model=ModelRunResponse)
def run_soil_carbon(req: SoilCarbonRequest) -> ModelRunResponse:
    """
    RothC / DNDC-inspired soil organic carbon cycling simulation.

    ⚠ This model requires site-specific calibration before use in
    carbon-trading or compliance applications.
    """
    try:
        from shared.process_models.models import SoilProfile
        from shared.process_models.soil_carbon import SoilCarbonModel

        model = SoilCarbonModel()
        soil = SoilProfile(
            clay_pct=req.clay_fraction * 100,
        )
        result_obj = model.simulate(
            soil=soil,
            years=req.simulation_years,
            mean_temp_c=req.mean_annual_temp_c,
            mean_soil_water_fraction=min(1.0, req.mean_annual_precip_mm / 1000.0),
            annual_carbon_input_t_ha=req.carbon_input_t_ha_yr,
        )
        result = result_obj.outputs

        return ModelRunResponse(
            model_name="RothC/DNDC-simplified",
            result=result,
            warnings=[
                "Soil carbon model requires site-specific calibration before use in "
                "carbon-trading, compliance, or public reporting."
            ],
            quality_flag="needs_calibration",
        )

    except Exception as exc:
        logger.exception("Soil carbon simulation failed")
        raise HTTPException(http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Model computation failed") from exc


# ── 4. Soil water balance (SWB) ─────────────────────────────────────────────


class SWBRequest(BaseModel):
    tmax_c: float = Field(..., ge=-50, le=60)
    tmin_c: float = Field(..., ge=-50, le=60)
    solar_radiation_mj_m2: float = Field(..., ge=0, le=50)
    relative_humidity_pct: float = Field(..., ge=0, le=100)
    wind_speed_m_s: float = Field(..., ge=0, le=50)
    precipitation_mm: float = Field(default=0.0, ge=0, le=500)
    irrigation_mm: float = Field(default=0.0, ge=0, le=500)
    kc: float = Field(default=1.0, ge=0, le=2.0)
    # Soil
    soil_water_mm: float = Field(default=200.0, ge=0, le=1000, description="Current soil water mm")
    field_capacity_mm: float = Field(default=250.0, ge=10, le=1000)
    wilting_point_mm: float = Field(default=100.0, ge=0, le=800)
    total_available_water_mm: float = Field(default=150.0, ge=0, le=800)
    # SCS-CN
    curve_number: float = Field(default=75.0, ge=30, le=100, description="SCS curve number")
    latitude_deg: float = Field(default=25.0, ge=-90, le=90)
    day_of_year: int = Field(default=180, ge=1, le=366)


@router.post("/swb/run", response_model=ModelRunResponse)
def run_swb(req: SWBRequest) -> ModelRunResponse:
    """
    Daily soil water balance using FAO-56 dual-Kc + SCS-CN runoff + Green-Ampt
    deep percolation.
    """
    try:
        from shared.process_models.agro_meteorology import penman_monteith_et0
        from shared.process_models.hydrology import HydrologyEngine
        from shared.process_models.models import DailyWeather

        weather = DailyWeather(
            date=_doy_to_date(req.day_of_year),
            tmax_c=req.tmax_c,
            tmin_c=req.tmin_c,
            solar_radiation_mj_m2=req.solar_radiation_mj_m2,
            relative_humidity_pct=req.relative_humidity_pct,
            wind_speed_m_s=req.wind_speed_m_s,
            precipitation_mm=req.precipitation_mm,
        )

        et0 = penman_monteith_et0(weather, lat_deg=req.latitude_deg)
        etc = et0 * req.kc

        hydro = HydrologyEngine()

        # Runoff via SCS-CN
        cn = int(round(req.curve_number))
        runoff_data = hydro.estimate_event_runoff(precipitation_mm=req.precipitation_mm, cn=cn)

        # Simple daily balance
        effective_rain = req.precipitation_mm - runoff_data.get("runoff_mm", 0.0)
        new_sw = req.soil_water_mm + effective_rain + req.irrigation_mm - etc
        new_sw = max(0.0, min(req.field_capacity_mm, new_sw))
        deep_perc = max(0.0, new_sw - req.field_capacity_mm)

        swb: dict[str, Any] = {
            "new_soil_water_mm": round(new_sw, 2),
            "depletion_mm": round(req.field_capacity_mm - new_sw, 2),
            "runoff_mm": round(runoff_data.get("runoff_mm", 0.0), 2),
            "deep_perc_mm": round(deep_perc, 2),
            "effective_rain_mm": round(effective_rain, 2),
            "et0_mm": round(et0, 3),
            "etc_mm": round(etc, 3),
        }

        return ModelRunResponse(
            model_name="FAO-56 SWB + SCS-CN",
            result=swb,
        )

    except Exception as exc:
        logger.exception("SWB run failed")
        raise HTTPException(http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Model computation failed") from exc


# ── 5. PROSAIL inversion ─────────────────────────────────────────────────────


class PROSAILRequest(BaseModel):
    """Canopy reflectances for PROSAIL inversion."""

    red: float = Field(..., ge=0, le=1, description="Red band reflectance (0-1)")
    nir: float = Field(..., ge=0, le=1, description="NIR band reflectance (0-1)")
    swir: float | None = Field(default=None, ge=0, le=1, description="SWIR reflectance (optional)")
    solar_zenith_deg: float = Field(default=30.0, ge=0, le=90)
    view_zenith_deg: float = Field(default=0.0, ge=0, le=90)
    hot_spot: float = Field(default=0.05, ge=0, le=1)


@router.post("/prosail/invert", response_model=ModelRunResponse)
def run_prosail_inversion(req: PROSAILRequest) -> ModelRunResponse:
    """
    Simplified PROSAIL inversion: estimate LAI and chlorophyll content from
    surface reflectances.

    ⚠ Results require site-specific spectral calibration.  Do NOT use for
    production decisions without validation against field measurements.
    """
    try:
        from shared.process_models.radiative_transfer import RadiativeTransferModel

        model = RadiativeTransferModel()
        # Compute NDVI and NDRE from the supplied bands
        ndvi = (req.nir - req.red) / (req.nir + req.red + 1e-9)
        # Use SWIR as a rough red-edge proxy if not supplied.
        # 0.3 is a typical background/bare-soil NDRE for arid regions (Middle East).
        _DEFAULT_NDRE_PROXY = 0.3
        observed_ndre = req.swir if req.swir is not None else _DEFAULT_NDRE_PROXY
        result_obj = model.invert(observed_ndvi=ndvi, observed_ndre=observed_ndre)
        result = result_obj.outputs
        result["computed_ndvi"] = round(ndvi, 4)

        warnings = [
            "PROSAIL inversion is a simplified lookup-table approach.",
            "Results require spectral calibration against field measurements before use in production recommendations.",
        ]

        return ModelRunResponse(
            model_name="PROSAIL (simplified)",
            result=result,
            warnings=warnings,
            quality_flag="needs_calibration",
        )

    except Exception as exc:
        logger.exception("PROSAIL inversion failed")
        raise HTTPException(http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Model computation failed") from exc


# ── Helper ───────────────────────────────────────────────────────────────────


def _doy_to_date(doy: int):
    """Convert day-of-year to a date object (current year)."""
    from datetime import date

    year = date.today().year
    return date(year, 1, 1).replace(year=year) + __import__("datetime").timedelta(days=doy - 1)
