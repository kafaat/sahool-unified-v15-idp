# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Simplified Radiative Transfer Model – PROSAIL (PROSPECT + SAIL)
================================================================
نموذج النقل الإشعاعي المبسّط (PROSAIL)

Implements a simplified version of the PROSAIL leaf-canopy radiative transfer
model for inverting satellite/UAV multispectral data into biophysical crop
parameters (LAI, Chl, CWC).

Architecture:
  PROSPECT (leaf model) → SAIL (canopy model) → PROSAIL (combined)

Key bands simulated:
  Blue ~490 nm, Green ~560 nm, Red ~665 nm,
  RedEdge ~705 nm, NIR ~842 nm, SWIR ~1610 nm

References:
  Jacquemoud & Baret (1990). PROSPECT: A model of leaf optical properties.
  Verhoef (1984). Earth observation modelling based on layer scattering matrices.
  Houborg et al. (2015). A curvelet-based supervised classification approach...
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import structlog

from shared.process_models.models import ModelResult, ModelType

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# PROSPECT leaf model – parameters and reflectance
# ---------------------------------------------------------------------------


@dataclass
class LeafOpticalProperties:
    """
    PROSPECT leaf optical parameter set.
    معاملات الخصائص البصرية للورقة.
    """

    n_layers: float = 1.5  # Leaf structure parameter (1–3) | معامل بنية الورقة
    chlorophyll_ug_cm2: float = 40.0  # Chl a+b content (µg cm⁻²) | محتوى الكلوروفيل
    carotenoid_ug_cm2: float = 8.0  # Carotenoid content (µg cm⁻²) | الكاروتينات
    water_cm: float = 0.012  # Equivalent water thickness (cm) | سُمك الماء
    dry_matter_g_cm2: float = 0.005  # Dry matter per unit area (g cm⁻²) | المادة الجافة


def prospect_reflectance(leaf: LeafOpticalProperties) -> dict[str, float]:
    """
    Simplified PROSPECT leaf reflectance for 6 key wavelength bands.
    انعكاس الورقة المبسّط لستة نطاقات طيفية رئيسية.

    Uses empirical approximations of the PROSPECT 5D physics to estimate
    reflectance at major satellite sensor bands without the full look-up-table.

    Returns:
        Dictionary of {band_name: reflectance_0_to_1}.
    """
    chl = leaf.chlorophyll_ug_cm2
    caro = leaf.carotenoid_ug_cm2
    water = leaf.water_cm
    dm = leaf.dry_matter_g_cm2
    n = leaf.n_layers

    # Chlorophyll absorption dominates Red and Blue bands
    # (simplified exponential absorption + multiple-scattering term)
    chl_abs_blue = 1.0 - math.exp(-0.045 * chl)
    chl_abs_red = 1.0 - math.exp(-0.030 * chl)
    water_abs_swir = 1.0 - math.exp(-60.0 * water)
    water_abs_nir = 1.0 - math.exp(-5.0 * water)

    # Base leaf scattering from mesophyll structure (n-dependent)
    scatter = 0.06 + 0.02 * (n - 1.0)

    r_blue = scatter * (1.0 - chl_abs_blue) * (1.0 - 0.3 * caro / 40.0)
    r_green = scatter * (1.0 - 0.4 * chl_abs_red) * (1.0 - 0.1 * caro / 40.0) + 0.04
    r_red = scatter * (1.0 - chl_abs_red)
    r_re = scatter * (1.0 - 0.5 * chl_abs_red) + 0.06  # RedEdge (705 nm)
    r_nir = 0.45 + scatter * (1.0 - water_abs_nir) - 0.01 * dm * 100.0
    r_swir = 0.15 * (1.0 - water_abs_swir) * (1.0 - 0.05 * dm * 100.0)

    return {
        "blue": round(max(0.0, min(1.0, r_blue)), 4),
        "green": round(max(0.0, min(1.0, r_green)), 4),
        "red": round(max(0.0, min(1.0, r_red)), 4),
        "red_edge": round(max(0.0, min(1.0, r_re)), 4),
        "nir": round(max(0.0, min(1.0, r_nir)), 4),
        "swir": round(max(0.0, min(1.0, r_swir)), 4),
    }


# ---------------------------------------------------------------------------
# SAIL canopy model – turbid medium approximation
# ---------------------------------------------------------------------------


@dataclass
class CanopyParameters:
    """
    SAIL canopy structural parameters.
    معاملات هيكل المجمع الخضري.
    """

    lai: float = 3.0  # Leaf Area Index | مؤشر مساحة الأوراق
    leaf_angle_deg: float = 57.0  # Mean leaf inclination angle (°) | زاوية ميل الأوراق
    hot_spot: float = 0.05  # Hot-spot parameter (sl/h) | معامل النقطة الساخنة
    soil_reflectance: float = 0.15  # Background soil reflectance | انعكاس التربة
    view_zenith_deg: float = 0.0  # Sensor view zenith angle (°) | زاوية السمت للمستشعر
    sun_zenith_deg: float = 30.0  # Solar zenith angle (°) | زاوية السمت للشمس


def sail_canopy_reflectance(
    leaf_ref: dict[str, float],
    canopy: CanopyParameters,
) -> dict[str, float]:
    """
    SAIL turbid-medium canopy reflectance (simplified analytical solution).
    انعكاس المجمع الخضري بنموذج SAIL (حل تحليلي مبسّط).

    Approximates the two-stream (Verhoef 1984) solution using:
      R_canopy = R_leaf · (1 - exp(-k·LAI)) + R_soil · exp(-k·LAI)

    where k is the extinction coefficient projected onto sensor/sun geometry.
    Hot-spot correction modifies the retro-reflectance peak.

    Returns:
        Dictionary {band: canopy_reflectance}.
    """
    k_ex = 0.5 / max(0.1, math.cos(math.radians(canopy.leaf_angle_deg)))  # G(θ)/cos(θ_s)
    theta_s_rad = math.radians(canopy.sun_zenith_deg)
    theta_v_rad = math.radians(canopy.view_zenith_deg)

    # Beer-Lambert gap fraction
    gap_frac = math.exp(-k_ex * canopy.lai)

    # Hot-spot correction (simplified)
    if abs(canopy.view_zenith_deg - canopy.sun_zenith_deg) < 5.0:
        hotspot_boost = 1.0 + canopy.hot_spot * canopy.lai
    else:
        hotspot_boost = 1.0

    result = {}
    for band, r_leaf in leaf_ref.items():
        r_canopy = r_leaf * (1.0 - gap_frac) * hotspot_boost + canopy.soil_reflectance * gap_frac
        result[band] = round(max(0.0, min(1.0, r_canopy)), 4)
    return result


# ---------------------------------------------------------------------------
# Vegetation index computation
# ---------------------------------------------------------------------------


def compute_vegetation_indices(canopy_ref: dict[str, float]) -> dict[str, float]:
    """
    Derive common vegetation indices from simulated canopy reflectance.
    حساب مؤشرات الغطاء النباتي من الانعكاس المحاكى.

    NDVI, EVI, NDRE (RedEdge NDVI), CHL-RED (Chlorophyll RedEdge Index).
    """
    nir = canopy_ref.get("nir", 0.5)
    red = canopy_ref.get("red", 0.1)
    blue = canopy_ref.get("blue", 0.05)
    re = canopy_ref.get("red_edge", 0.15)
    swir = canopy_ref.get("swir", 0.1)

    ndvi = (nir - red) / (nir + red + 1e-9)
    evi = 2.5 * (nir - red) / (nir + 6.0 * red - 7.5 * blue + 1.0 + 1e-9)
    ndre = (nir - re) / (nir + re + 1e-9)  # RedEdge NDVI
    ndwi = (nir - swir) / (nir + swir + 1e-9)
    chl_re = (nir / re) - 1.0  # Gitelson chlorophyll index

    return {
        "ndvi": round(max(-1.0, min(1.0, ndvi)), 4),
        "evi": round(max(-1.0, min(2.0, evi)), 4),
        "ndre": round(max(-1.0, min(1.0, ndre)), 4),
        "ndwi": round(max(-1.0, min(1.0, ndwi)), 4),
        "chl_re": round(max(0.0, chl_re), 4),
    }


# ---------------------------------------------------------------------------
# Model inversion – LUT-based LAI and Chl retrieval
# ---------------------------------------------------------------------------


def invert_lai_chlorophyll(
    observed_ndvi: float,
    observed_ndre: float,
) -> dict[str, float]:
    """
    Simple inversion of PROSAIL to estimate LAI and chlorophyll from
    NDVI and RedEdge NDVI using empirical relationships derived from
    PROSAIL look-up table simulations.
    عكس بسيط للنموذج لتقدير LAI والكلوروفيل.

    These regression coefficients are representative of typical agricultural
    canopies (wheat, barley, maize) over calcareous soils (Middle East).
    """
    # LAI from NDVI (asymptotic relationship)
    lai_estimated = -2.0 * math.log(1.0 - max(0.0, min(0.95, observed_ndvi))) if observed_ndvi > 0.05 else 0.1

    # Chlorophyll from RedEdge NDVI (Gitelson & Merzlyak 1996 relationship)
    chl_estimated = max(5.0, min(80.0, 148.0 * observed_ndre - 20.0))

    return {
        "lai_estimated": round(max(0.01, lai_estimated), 2),
        "chlorophyll_ug_cm2_estimated": round(chl_estimated, 1),
    }


# ---------------------------------------------------------------------------
# Main model class
# ---------------------------------------------------------------------------


class RadiativeTransferModel:
    """
    PROSAIL-simplified radiative transfer model for satellite calibration.
    نموذج PROSAIL المبسّط لمعايرة صور الأقمار الصناعية.

    Supports both forward (parameters → reflectance) and inverse
    (reflectance → biophysical parameters) modes.

    Usage::

        rtm = RadiativeTransferModel()
        result = rtm.forward(
            leaf=LeafOpticalProperties(chlorophyll_ug_cm2=45, water_cm=0.015),
            canopy=CanopyParameters(lai=3.5, sun_zenith_deg=25),
        )
        print(result.outputs["vegetation_indices"]["ndvi"])

        inv = rtm.invert(observed_ndvi=0.72, observed_ndre=0.35)
        print(inv.outputs["lai_estimated"])
    """

    def forward(self, leaf: LeafOpticalProperties, canopy: CanopyParameters) -> ModelResult:
        """
        Forward RTM run: parameters → simulated canopy reflectance + indices.
        تشغيل النموذج للأمام: المعاملات ← الانعكاس المحاكى.
        """
        leaf_ref = prospect_reflectance(leaf)
        canopy_ref = sail_canopy_reflectance(leaf_ref, canopy)
        vi = compute_vegetation_indices(canopy_ref)

        logger.info(
            "rtm_forward_run",
            lai=canopy.lai,
            chl=leaf.chlorophyll_ug_cm2,
            ndvi=vi["ndvi"],
        )

        return ModelResult(
            model_name="RadiativeTransferModel (PROSAIL-simplified)",
            model_type=ModelType.RADIATIVE_TRANSFER,
            success=True,
            message="Forward RTM simulation completed",
            message_ar="اكتملت محاكاة النقل الإشعاعي للأمام",
            outputs={
                "leaf_reflectance": leaf_ref,
                "canopy_reflectance": canopy_ref,
                "vegetation_indices": vi,
            },
        )

    def invert(self, observed_ndvi: float, observed_ndre: float = 0.3) -> ModelResult:
        """
        Inverse RTM: observed spectral indices → biophysical parameters.
        عكس النموذج: المؤشرات الطيفية → المعاملات البيوفيزيائية.
        """
        estimates = invert_lai_chlorophyll(observed_ndvi, observed_ndre)

        logger.info(
            "rtm_inversion_run",
            observed_ndvi=observed_ndvi,
            observed_ndre=observed_ndre,
            lai_estimated=estimates["lai_estimated"],
        )

        return ModelResult(
            model_name="RadiativeTransferModel (PROSAIL-simplified inversion)",
            model_type=ModelType.RADIATIVE_TRANSFER,
            success=True,
            message="RTM inversion completed",
            message_ar="اكتمل عكس نموذج النقل الإشعاعي",
            outputs=estimates,
        )
