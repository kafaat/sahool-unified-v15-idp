# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
QUEFTS Nutrient Management Model - نموذج QUEFTS لإدارة المغذيات
================================================================
Quantitative Evaluation of the Fertility of Tropical Soils (QUEFTS).

Implements the constraint-based nutrient supply / crop demand model
originally published by Janssen et al. (1990) for N, P and K nutrition.

Key concepts:
  1. Soil nutrient supply (Ns, Ps, Ks) from soil tests
  2. Maximum accumulation – maximum uptake at zero yield target
  3. Maximum dilution – minimum uptake concentration for target yield
  4. Balanced nutrition envelope – intersection of N, P, K constraints
  5. Recommended fertiliser rate from balance between supply and demand

Additional: 4R Nutrient Stewardship Strategy (Right source, rate, time, place).

Reference:
  Janssen BH et al. (1990). A system for quantitative evaluation of the
  fertility of tropical soils (QUEFTS). Geoderma 46:299-318.
  Witt C et al. (1999). Internal nutrient efficiencies of irrigated lowland rice...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import structlog

from shared.process_models.models import CropParameters, CropType, ModelResult, ModelType

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class NutrientElement(StrEnum):
    NITROGEN = "N"
    PHOSPHORUS = "P"
    POTASSIUM = "K"


class FertilizerSource(StrEnum):
    UREA = "urea_46"
    AMMONIUM_NITRATE = "ammonium_nitrate_34"
    DAP = "dap_18_46"
    TSP = "tsp_0_46"
    MOP = "mop_0_0_60"
    COMPOUND_NPK = "compound_npk"


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class SoilNutrientSupply:
    """
    Soil nutrient supply estimates from soil test.
    تقديرات إمداد التربة بالمغذيات من اختبار التربة.

    Default values represent a medium-fertility calcareous soil (Middle East).
    """

    n_supply_kg_ha: float = 80.0  # Available N from soil (kg ha⁻¹) | النيتروجين المتاح
    p_supply_kg_ha: float = 15.0  # Available P₂O₅ (kg ha⁻¹) | الفوسفور المتاح
    k_supply_kg_ha: float = 120.0  # Available K₂O (kg ha⁻¹) | البوتاسيوم المتاح
    organic_n_mineralisation_kg_ha: float = 20.0  # Mineral N from OM (kg ha⁻¹) | معدنة النيتروجين

    @property
    def total_n_available(self) -> float:
        return self.n_supply_kg_ha + self.organic_n_mineralisation_kg_ha


# QUEFTS nutrient efficiency parameters per crop
# (max_accumulation, max_dilution) for each nutrient — kg nutrient per t yield
_QUEFTS_PARAMS: dict[CropType, dict[str, tuple[float, float]]] = {
    CropType.WHEAT: {
        "N": (37.0, 14.0),
        "P": (6.5, 2.1),
        "K": (8.5, 4.0),
    },
    CropType.RICE: {
        "N": (28.0, 14.0),
        "P": (5.2, 2.0),
        "K": (30.0, 14.0),
    },
    CropType.MAIZE: {
        "N": (35.0, 14.0),
        "P": (6.0, 2.0),
        "K": (12.0, 5.0),
    },
    CropType.BARLEY: {
        "N": (30.0, 12.0),
        "P": (5.5, 1.8),
        "K": (7.5, 3.5),
    },
    CropType.SORGHUM: {
        "N": (28.0, 12.0),
        "P": (5.0, 1.8),
        "K": (10.0, 4.0),
    },
    CropType.TOMATO: {
        "N": (22.0, 9.0),
        "P": (4.0, 1.5),
        "K": (30.0, 12.0),
    },
    CropType.POTATO: {
        "N": (18.0, 7.0),
        "P": (3.5, 1.2),
        "K": (25.0, 10.0),
    },
}
_QUEFTS_DEFAULT = {"N": (32.0, 12.0), "P": (5.5, 1.8), "K": (10.0, 4.0)}


def _quefts_envelope(supply_kg_ha: float, max_acc: float, max_dil: float, target_yield_t_ha: float) -> float:
    """
    QUEFTS nutrient constraint: yield limited by single nutrient.
    قيد المغذي المفرد في نموذج QUEFTS.

    The yield parabola intersects the accumulation line (low yields) and
    dilution line (high yields).  Simplified to linear envelope here.
    """
    # Yield from accumulation side (low-yield regime)
    y_acc = supply_kg_ha / max_acc
    # Yield from dilution side (high-yield regime)
    y_dil = supply_kg_ha / max_dil
    # QUEFTS envelope = max of both sides, capped at target
    return min(target_yield_t_ha, max(y_acc, min(y_dil, target_yield_t_ha)))


# ---------------------------------------------------------------------------
# Main model
# ---------------------------------------------------------------------------


@dataclass
class QueftsResult:
    """QUEFTS fertiliser recommendation output. نتائج توصية الأسمدة من QUEFTS."""

    target_yield_t_ha: float
    yield_n_limited_t_ha: float
    yield_p_limited_t_ha: float
    yield_k_limited_t_ha: float
    balanced_yield_t_ha: float

    n_required_kg_ha: float
    p_required_kg_ha: float
    k_required_kg_ha: float

    n_fertiliser_kg_ha: float
    p2o5_fertiliser_kg_ha: float
    k2o_fertiliser_kg_ha: float

    # 4R guidance
    n_application_time: str = ""
    p_application_time: str = ""
    k_application_time: str = ""
    notes_en: str = ""
    notes_ar: str = ""


class QueftsNutrientModel:
    """
    QUEFTS-based quantitative nutrient management model.
    نموذج QUEFTS الكمي لإدارة المغذيات.

    Estimates optimal N-P-K fertiliser rates to achieve a target yield
    by evaluating soil nutrient supply against crop demand using the
    QUEFTS balanced nutrition framework and 4R nutrient stewardship.

    Usage::

        model = QueftsNutrientModel()
        result = model.recommend(
            crop=CropParameters(crop_type=CropType.WHEAT),
            soil_supply=SoilNutrientSupply(n_supply_kg_ha=60, p_supply_kg_ha=12),
            target_yield_t_ha=5.0,
        )
        print(result.outputs["n_fertiliser_kg_ha"])
    """

    def recommend(
        self,
        crop: CropParameters,
        soil_supply: SoilNutrientSupply,
        target_yield_t_ha: float = 4.0,
    ) -> ModelResult:
        """
        Generate QUEFTS-based fertiliser recommendation.
        إنشاء توصية أسمدة قائمة على QUEFTS.

        Args:
            crop: Crop parameters (nutrient demand per tonne grain).
            soil_supply: Estimated soil nutrient supply (kg ha⁻¹).
            target_yield_t_ha: Farmer's target grain yield (t ha⁻¹).

        Returns:
            ModelResult with recommended N, P₂O₅ and K₂O rates.
        """
        params = _QUEFTS_PARAMS.get(crop.crop_type, _QUEFTS_DEFAULT)

        # Compute single-nutrient limited yields
        n_total = soil_supply.total_n_available
        y_n = _quefts_envelope(n_total, *params["N"], target_yield_t_ha)
        y_p = _quefts_envelope(soil_supply.p_supply_kg_ha, *params["P"], target_yield_t_ha)
        y_k = _quefts_envelope(soil_supply.k_supply_kg_ha, *params["K"], target_yield_t_ha)

        # Balanced yield = minimum of the three constraints
        balanced_yield = min(y_n, y_p, y_k)

        # Crop nutrient requirement for target yield (internal efficiency approach)
        n_req = target_yield_t_ha * crop.n_requirement_kg_per_ton
        p_req = target_yield_t_ha * crop.p_requirement_kg_per_ton  # kg P
        k_req = target_yield_t_ha * crop.k_requirement_kg_per_ton  # kg K

        # Fertiliser to add = requirement minus soil supply (recovery factor ≈ 0.6 for N, 0.25 P, 0.75 K)
        n_fert = max(0.0, (n_req - soil_supply.total_n_available) / 0.60)
        p_fert = max(0.0, (p_req * 2.29 - soil_supply.p_supply_kg_ha) / 0.25)  # P → P₂O₅: ×2.29
        k_fert = max(0.0, (k_req * 1.20 - soil_supply.k_supply_kg_ha) / 0.75)  # K → K₂O: ×1.20

        # 4R timing guidance
        n_timing = "Split: 1/3 at sowing, 1/3 at tillering, 1/3 at stem elongation"
        n_timing_ar = "مقسّم: الثلث عند الزراعة، الثلث عند التفريع، الثلث عند استطالة الساق"
        p_timing = "Full dose at sowing or pre-sowing incorporation"
        p_timing_ar = "جرعة كاملة عند الزراعة أو قبلها مع تقليب التربة"
        k_timing = "Half at sowing, half at mid-season"
        k_timing_ar = "النصف عند الزراعة، النصف في منتصف الموسم"

        notes_en = (
            f"Balanced yield limited by "
            f"{'N' if balanced_yield == y_n else 'P' if balanced_yield == y_p else 'K'}. "
            "Apply phosphorus and potassium before sowing; split nitrogen applications to reduce leaching."
        )
        notes_ar = (
            f"الإنتاجية المتوازنة محدودة بـ"
            f"{'النيتروجين' if balanced_yield == y_n else 'الفوسفور' if balanced_yield == y_p else 'البوتاسيوم'}. "
            "أضف الفوسفور والبوتاسيوم قبل الزراعة؛ وزّع النيتروجين لتقليل الفقد."
        )

        logger.info(
            "quefts_recommendation_complete",
            crop=crop.crop_type,
            target_yield=target_yield_t_ha,
            balanced_yield=round(balanced_yield, 2),
            n_fert=round(n_fert, 1),
            p2o5_fert=round(p_fert, 1),
            k2o_fert=round(k_fert, 1),
        )

        return ModelResult(
            model_name="QueftsNutrientModel (QUEFTS / 4R)",
            model_type=ModelType.NUTRIENT_MANAGEMENT,
            success=True,
            message="QUEFTS nutrient recommendation completed",
            message_ar="اكتملت توصية المغذيات من نموذج QUEFTS",
            outputs={
                "target_yield_t_ha": target_yield_t_ha,
                "balanced_yield_t_ha": round(balanced_yield, 2),
                "yield_n_limited_t_ha": round(y_n, 2),
                "yield_p_limited_t_ha": round(y_p, 2),
                "yield_k_limited_t_ha": round(y_k, 2),
                "n_required_total_kg_ha": round(n_req, 1),
                "p2o5_required_total_kg_ha": round(p_req * 2.29, 1),
                "k2o_required_total_kg_ha": round(k_req * 1.20, 1),
                "n_fertiliser_kg_ha": round(n_fert, 1),
                "p2o5_fertiliser_kg_ha": round(p_fert, 1),
                "k2o_fertiliser_kg_ha": round(k_fert, 1),
                "n_application_time": n_timing,
                "n_application_time_ar": n_timing_ar,
                "p_application_time": p_timing,
                "p_application_time_ar": p_timing_ar,
                "k_application_time": k_timing,
                "k_application_time_ar": k_timing_ar,
                "notes_en": notes_en,
                "notes_ar": notes_ar,
            },
        )
