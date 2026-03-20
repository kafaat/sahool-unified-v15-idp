"""
Salinity Module for SAHOOL Platform.

Provides EC/SAR calculations, leaching fraction computation,
Kc adjustment under saline conditions, and yield reduction estimation.

Based on:
- FAO Irrigation & Drainage Paper 29 (Ayers & Westcot, 1985)
- FAO-56 Penman-Monteith salinity adjustments
- Yemen coastal groundwater salinity data (Frontiers, 2023)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import StrEnum

logger = logging.getLogger(__name__)


class SalinityRisk(StrEnum):
    """Salinity risk classification per FAO-29."""

    NONE = "none"
    SLIGHT_MODERATE = "slight_moderate"
    SEVERE = "severe"


@dataclass
class SalinityAssessment:
    """Complete salinity assessment for a field/water source."""

    ec_water: float  # dS/m - Electrical Conductivity of irrigation water
    ec_soil: float  # dS/m - Electrical Conductivity of soil saturation extract
    sar: float  # Sodium Adsorption Ratio
    risk: SalinityRisk
    risk_ar: str  # Arabic risk label
    yield_reduction_pct: float  # Estimated yield reduction %
    leaching_fraction: float  # Required leaching fraction (0-1)
    adjusted_kc: float  # Kc adjusted for salinity
    original_kc: float  # Original Kc before adjustment
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)


@dataclass
class LeachingRequirement:
    """Leaching requirement calculation result."""

    leaching_fraction: float  # LF (0-1)
    extra_water_mm: float  # Additional water needed per irrigation (mm)
    total_water_mm: float  # Total water including leaching (mm)
    ec_drainage: float  # Expected EC of drainage water (dS/m)


# --- Crop salinity tolerance thresholds (FAO-29) ---
# Format: (ECe_threshold dS/m, slope %/dS/m)
# ECe_threshold: max soil salinity with no yield loss
# slope: yield decrease per unit ECe above threshold
CROP_SALINITY_TOLERANCE: dict[str, tuple[float, float]] = {
    # Cereals
    "wheat": (6.0, 7.1),
    "barley": (8.0, 5.0),
    "rice": (3.0, 12.0),
    "sorghum": (6.8, 16.0),
    "corn": (1.7, 12.0),
    "millet": (6.8, 16.0),
    # Vegetables
    "tomato": (2.5, 9.9),
    "cucumber": (2.5, 13.0),
    "pepper": (1.5, 14.0),
    "onion": (1.2, 16.0),
    "potato": (1.7, 12.0),
    "lettuce": (1.3, 13.0),
    "cabbage": (1.8, 9.7),
    "eggplant": (1.1, 6.9),
    "okra": (1.2, 15.0),
    # Fruits
    "date_palm": (4.0, 3.6),
    "grape": (1.5, 9.6),
    "mango": (1.0, 10.0),
    "banana": (1.0, 14.0),
    "papaya": (1.0, 12.0),
    "citrus": (1.7, 16.0),
    "pomegranate": (3.0, 8.0),
    "fig": (2.7, 14.0),
    # Yemen-specific
    "qat": (2.0, 12.0),  # Estimated - limited research data
    "coffee_arabica": (1.0, 15.0),  # Sensitive
    "sesame": (2.5, 11.0),
    "alfalfa": (2.0, 7.3),
    "cotton": (7.7, 5.2),
}

RISK_AR_LABELS = {
    SalinityRisk.NONE: "لا يوجد خطر",
    SalinityRisk.SLIGHT_MODERATE: "خطر خفيف إلى متوسط",
    SalinityRisk.SEVERE: "خطر شديد",
}


def calculate_sar(na: float, ca: float, mg: float) -> float:
    """
    Calculate Sodium Adsorption Ratio (SAR).

    Args:
        na: Sodium concentration (meq/L)
        ca: Calcium concentration (meq/L)
        mg: Magnesium concentration (meq/L)

    Returns:
        SAR value (dimensionless)
    """
    if ca + mg <= 0:
        logger.warning("SAR calculation: ca + mg <= 0, returning 0.0")
        return 0.0
    denominator = math.sqrt((ca + mg) / 2.0)
    if denominator <= 0:
        return 0.0
    return na / denominator


def classify_salinity_risk(ec_water: float, sar: float) -> SalinityRisk:
    """
    Classify salinity risk based on EC and SAR per FAO-29 guidelines.

    Args:
        ec_water: EC of irrigation water (dS/m)
        sar: Sodium Adsorption Ratio

    Returns:
        SalinityRisk classification
    """
    # Salinity hazard (EC-based)
    if ec_water < 0.7:
        ec_risk = SalinityRisk.NONE
    elif ec_water < 3.0:
        ec_risk = SalinityRisk.SLIGHT_MODERATE
    else:
        ec_risk = SalinityRisk.SEVERE

    # Sodicity hazard (SAR-based)
    if sar < 3.0:
        sar_risk = SalinityRisk.NONE
    elif sar < 9.0:
        sar_risk = SalinityRisk.SLIGHT_MODERATE
    else:
        sar_risk = SalinityRisk.SEVERE

    # Return the higher risk
    risk_order = [SalinityRisk.NONE, SalinityRisk.SLIGHT_MODERATE, SalinityRisk.SEVERE]
    return max(ec_risk, sar_risk, key=lambda r: risk_order.index(r))


def calculate_yield_reduction(
    ec_soil: float,
    crop: str,
    custom_threshold: float | None = None,
    custom_slope: float | None = None,
) -> float:
    """
    Calculate expected yield reduction due to salinity (FAO-29 linear model).

    Yr = 100 - slope * (ECe - ECe_threshold)  for ECe > threshold
    Yr = 100  for ECe <= threshold

    Args:
        ec_soil: Soil salinity (ECe) in dS/m
        crop: Crop name (lowercase)
        custom_threshold: Override default ECe threshold
        custom_slope: Override default slope

    Returns:
        Yield reduction as percentage (0-100)
    """
    threshold, slope = CROP_SALINITY_TOLERANCE.get(crop, (2.0, 12.0))

    if custom_threshold is not None:
        threshold = custom_threshold
    if custom_slope is not None:
        slope = custom_slope

    if ec_soil <= threshold:
        return 0.0

    reduction = slope * (ec_soil - threshold)
    return min(reduction, 100.0)


def calculate_leaching_fraction(
    ec_water: float,
    ec_soil_threshold: float,
    efficiency: float = 0.8,
) -> float:
    """
    Calculate leaching fraction required to maintain soil salinity below threshold.

    LF = ECw / (5 * ECe_threshold - ECw)  (FAO-29 simplified)

    Args:
        ec_water: EC of irrigation water (dS/m)
        ec_soil_threshold: Maximum allowable ECe (dS/m)
        efficiency: Irrigation system efficiency (0-1)

    Returns:
        Leaching fraction (0-1), clamped to [0, 0.5]
    """
    denominator = 5.0 * ec_soil_threshold - ec_water
    if denominator <= 0:
        return 0.5  # Maximum practical LF

    lf = ec_water / denominator
    # Adjust for irrigation efficiency (guard against zero/negative)
    if efficiency > 0:
        lf = lf / efficiency
    return max(0.0, min(lf, 0.5))


def adjust_kc_for_salinity(
    kc: float,
    ec_soil: float,
    crop: str,
    custom_threshold: float | None = None,
    custom_slope: float | None = None,
) -> float:
    """
    Adjust crop coefficient (Kc) for salinity stress.

    Under saline conditions, actual ET is reduced. The Kc is adjusted
    proportionally to the expected yield reduction:
    Kc_adj = Kc * (1 - yield_reduction/200)

    The divisor of 200 (not 100) accounts for the fact that ET reduction
    is typically less severe than yield reduction under moderate salinity.

    Args:
        kc: Original crop coefficient
        ec_soil: Soil salinity (ECe) in dS/m
        crop: Crop name
        custom_threshold: Override ECe threshold
        custom_slope: Override slope

    Returns:
        Adjusted Kc value
    """
    yield_red = calculate_yield_reduction(ec_soil, crop, custom_threshold, custom_slope)
    # ET reduction is roughly half of yield reduction under moderate salinity
    adjustment_factor = 1.0 - (yield_red / 200.0)
    return max(kc * adjustment_factor, kc * 0.5)  # Floor at 50% of original Kc


class SalinityModule:
    """
    Main salinity analysis module for SAHOOL platform.

    Integrates EC/SAR calculations, leaching requirements, Kc adjustment,
    and yield impact estimation. Designed to complement pyfao56 and
    AquaCrop-OSPy which lack salinity stress modeling.
    """

    def __init__(
        self,
        default_irrigation_efficiency: float = 0.85,
        custom_crop_tolerances: dict[str, tuple[float, float]] | None = None,
    ):
        self.default_efficiency = default_irrigation_efficiency
        self.crop_tolerances = {**CROP_SALINITY_TOLERANCE}
        if custom_crop_tolerances:
            self.crop_tolerances.update(custom_crop_tolerances)

    def assess(
        self,
        ec_water: float,
        crop: str,
        kc: float,
        na: float = 0.0,
        ca: float = 0.0,
        mg: float = 0.0,
        ec_soil: float | None = None,
        sar: float | None = None,
    ) -> SalinityAssessment:
        """
        Perform complete salinity assessment.

        Args:
            ec_water: EC of irrigation water (dS/m)
            crop: Crop name
            kc: Current crop coefficient
            na: Sodium (meq/L) - for SAR calculation
            ca: Calcium (meq/L)
            mg: Magnesium (meq/L)
            ec_soil: Measured soil EC (dS/m). If None, estimated as 1.5 * ec_water
            sar: Pre-computed SAR. If None, calculated from na/ca/mg

        Returns:
            SalinityAssessment with all analysis results
        """
        # Calculate or use provided SAR
        if sar is None:
            sar = calculate_sar(na, ca, mg)

        # Estimate soil EC if not measured (FAO rule of thumb: ECe ≈ 1.5 * ECw)
        if ec_soil is None:
            ec_soil = ec_water * 1.5

        # Classify risk
        risk = classify_salinity_risk(ec_water, sar)

        # Get crop tolerance
        crop_lower = crop.lower().replace(" ", "_")
        if crop_lower in self.crop_tolerances:
            threshold, slope = self.crop_tolerances[crop_lower]
        else:
            threshold, slope = 2.0, 12.0

        # Calculate yield reduction
        yield_reduction = calculate_yield_reduction(
            ec_soil,
            crop_lower,
            threshold,
            slope,
        )

        # Calculate leaching fraction
        lf = calculate_leaching_fraction(
            ec_water,
            threshold,
            self.default_efficiency,
        )

        # Adjust Kc
        adjusted_kc = adjust_kc_for_salinity(kc, ec_soil, crop_lower, threshold, slope)

        # Generate recommendations
        recs, recs_ar = self._generate_recommendations(
            ec_water,
            ec_soil,
            sar,
            risk,
            crop_lower,
            yield_reduction,
            lf,
        )

        return SalinityAssessment(
            ec_water=ec_water,
            ec_soil=ec_soil,
            sar=sar,
            risk=risk,
            risk_ar=RISK_AR_LABELS[risk],
            yield_reduction_pct=round(yield_reduction, 1),
            leaching_fraction=round(lf, 3),
            adjusted_kc=round(adjusted_kc, 3),
            original_kc=kc,
            recommendations=recs,
            recommendations_ar=recs_ar,
        )

    def calculate_leaching_requirement(
        self,
        ec_water: float,
        crop: str,
        irrigation_depth_mm: float,
    ) -> LeachingRequirement:
        """
        Calculate the leaching water requirement for an irrigation event.

        Args:
            ec_water: EC of irrigation water (dS/m)
            crop: Crop name
            irrigation_depth_mm: Planned irrigation depth (mm)

        Returns:
            LeachingRequirement with extra water needs
        """
        crop_lower = crop.lower().replace(" ", "_")
        if crop_lower in self.crop_tolerances:
            threshold, _ = self.crop_tolerances[crop_lower]
        else:
            threshold = 2.0

        lf = calculate_leaching_fraction(ec_water, threshold, self.default_efficiency)
        extra_mm = irrigation_depth_mm * lf / (1.0 - lf) if lf < 1.0 else irrigation_depth_mm
        total_mm = irrigation_depth_mm + extra_mm

        # Estimate drainage EC (ECdw ≈ ECw / LF for steady state)
        ec_drainage = ec_water / lf if lf > 0 else 0.0

        return LeachingRequirement(
            leaching_fraction=round(lf, 3),
            extra_water_mm=round(extra_mm, 1),
            total_water_mm=round(total_mm, 1),
            ec_drainage=round(ec_drainage, 2),
        )

    def _generate_recommendations(
        self,
        ec_water: float,
        ec_soil: float,
        sar: float,
        risk: SalinityRisk,
        crop: str,
        yield_reduction: float,
        lf: float,
    ) -> tuple[list[str], list[str]]:
        """Generate bilingual recommendations based on salinity assessment."""
        recs: list[str] = []
        recs_ar: list[str] = []

        if risk == SalinityRisk.NONE:
            recs.append("Water quality is suitable for irrigation. No salinity management needed.")
            recs_ar.append("جودة المياه مناسبة للري. لا حاجة لإدارة الملوحة.")
            return recs, recs_ar

        # Leaching recommendation
        if lf > 0.05:
            lf_pct = round(lf * 100, 0)
            recs.append(f"Apply {lf_pct:.0f}% extra water for leaching to maintain soil salinity below threshold.")
            recs_ar.append(f"أضف {lf_pct:.0f}% مياه إضافية للغسيل للحفاظ على ملوحة التربة دون الحد الأقصى.")

        # High SAR
        if sar > 6.0:
            recs.append("High SAR detected. Consider gypsum application to improve soil structure.")
            recs_ar.append("نسبة امتصاص الصوديوم مرتفعة. يُنصح بإضافة الجبس لتحسين بنية التربة.")

        # Yield impact
        if yield_reduction > 10.0:
            recs.append(
                f"Expected yield reduction: {yield_reduction:.0f}%. Consider switching to more salt-tolerant varieties."
            )
            recs_ar.append(
                f"الانخفاض المتوقع في الإنتاج: {yield_reduction:.0f}%. يُنصح بالتحول إلى أصناف أكثر تحملاً للملوحة."
            )

        # Severe risk
        if risk == SalinityRisk.SEVERE:
            recs.append(
                "CRITICAL: Severe salinity risk. Immediate intervention required. "
                "Consider blending water sources or alternative water supply."
            )
            recs_ar.append("حرج: خطر ملوحة شديد. يلزم تدخل فوري. يُنصح بخلط مصادر المياه أو البحث عن مصدر بديل.")

        # Drip irrigation recommendation for saline water
        if ec_water > 1.5:
            recs.append(
                "Use drip irrigation to minimize salt accumulation in root zone. "
                "Frequent light irrigations are more effective than infrequent heavy ones."
            )
            recs_ar.append(
                "استخدم الري بالتنقيط لتقليل تراكم الأملاح في منطقة الجذور. "
                "الري الخفيف المتكرر أكثر فعالية من الري الغزير المتباعد."
            )

        return recs, recs_ar
