"""
Fertigation Engine - SAHOOL Platform v3.0

Integrated fertilizer + irrigation management engine with crop simulation,
NPK database by growth stage, and nutrient loss monitoring.

Features:
- NPK requirement database by crop × growth stage
- Fertigation scheduling (N, P, K injection rates)
- Nutrient balance tracking and loss estimation
- WOFOST-compatible crop growth simulation interface
- Salinity-aware fertigation (EC contribution of fertilizers)
- Environmental alerts for N/P leaching
- LSTM-ready data pipeline for yield prediction

Port: 8252

References:
- PCSE/WOFOST (Wageningen University)
- IrriPro Article 4 (Fertigation Integration)
- LSTM Vineyard Prediction (MDPI, 2025): MSE 0.37
"""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from enum import Enum, StrEnum
from typing import Any, Optional

sys.path.insert(0, "/app")
sys.path.insert(0, "/app/shared")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    _has_tenant_middleware = True
except ImportError:
    _has_tenant_middleware = False

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


VERSION = "16.0.0"
SERVICE_NAME = "fertigation-engine"
PORT = int(os.getenv("PORT", "8252"))


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class NutrientType(StrEnum):
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    CALCIUM = "calcium"
    MAGNESIUM = "magnesium"
    SULFUR = "sulfur"
    IRON = "iron"
    ZINC = "zinc"
    BORON = "boron"


class FertilizerType(StrEnum):
    UREA = "urea"  # 46-0-0
    DAP = "dap"  # 18-46-0
    MAP = "map"  # 11-52-0
    KCL = "kcl"  # 0-0-60 (Muriate of Potash)
    SOP = "sop"  # 0-0-50 (Sulfate of Potash)
    AMMONIUM_NITRATE = "ammonium_nitrate"  # 34-0-0
    CALCIUM_NITRATE = "calcium_nitrate"  # 15.5-0-0 + 19% Ca
    POTASSIUM_NITRATE = "potassium_nitrate"  # 13-0-46
    NPK_20_20_20 = "npk_20_20_20"
    NPK_15_15_15 = "npk_15_15_15"
    PHOSPHORIC_ACID = "phosphoric_acid"  # 0-52-0
    SULFURIC_ACID = "sulfuric_acid"  # For pH correction


class GrowthPhase(StrEnum):
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    TILLERING = "tillering"
    FLOWERING = "flowering"
    FRUIT_DEVELOPMENT = "fruit_development"
    RIPENING = "ripening"
    HARVEST = "harvest"


# ---------------------------------------------------------------------------
# Fertilizer Database
# ---------------------------------------------------------------------------

# NPK content (% by weight) and EC contribution
FERTILIZER_DB: dict[str, dict] = {
    FertilizerType.UREA: {
        "name": "Urea",
        "name_ar": "يوريا",
        "n": 46.0,
        "p": 0.0,
        "k": 0.0,
        "ec_per_gl": 1.1,  # dS/m per g/L
        "solubility_gl": 1080,  # g/L at 20°C
        "price_sar_kg": 2.5,
    },
    FertilizerType.DAP: {
        "name": "Di-Ammonium Phosphate",
        "name_ar": "فوسفات ثنائي الأمونيوم",
        "n": 18.0,
        "p": 46.0,
        "k": 0.0,
        "ec_per_gl": 0.86,
        "solubility_gl": 575,
        "price_sar_kg": 3.0,
    },
    FertilizerType.MAP: {
        "name": "Mono-Ammonium Phosphate",
        "name_ar": "فوسفات أحادي الأمونيوم",
        "n": 11.0,
        "p": 52.0,
        "k": 0.0,
        "ec_per_gl": 0.80,
        "solubility_gl": 370,
        "price_sar_kg": 3.5,
    },
    FertilizerType.KCL: {
        "name": "Potassium Chloride (MOP)",
        "name_ar": "كلوريد البوتاسيوم",
        "n": 0.0,
        "p": 0.0,
        "k": 60.0,
        "ec_per_gl": 1.87,
        "solubility_gl": 340,
        "price_sar_kg": 2.8,
    },
    FertilizerType.SOP: {
        "name": "Potassium Sulfate (SOP)",
        "name_ar": "سلفات البوتاسيوم",
        "n": 0.0,
        "p": 0.0,
        "k": 50.0,
        "ec_per_gl": 1.20,
        "solubility_gl": 110,
        "price_sar_kg": 4.0,
    },
    FertilizerType.AMMONIUM_NITRATE: {
        "name": "Ammonium Nitrate",
        "name_ar": "نترات الأمونيوم",
        "n": 34.0,
        "p": 0.0,
        "k": 0.0,
        "ec_per_gl": 1.50,
        "solubility_gl": 1870,
        "price_sar_kg": 2.0,
    },
    FertilizerType.CALCIUM_NITRATE: {
        "name": "Calcium Nitrate",
        "name_ar": "نترات الكالسيوم",
        "n": 15.5,
        "p": 0.0,
        "k": 0.0,
        "ec_per_gl": 1.00,
        "solubility_gl": 1290,
        "price_sar_kg": 3.5,
    },
    FertilizerType.POTASSIUM_NITRATE: {
        "name": "Potassium Nitrate",
        "name_ar": "نترات البوتاسيوم",
        "n": 13.0,
        "p": 0.0,
        "k": 46.0,
        "ec_per_gl": 1.20,
        "solubility_gl": 316,
        "price_sar_kg": 5.0,
    },
    FertilizerType.NPK_20_20_20: {
        "name": "NPK 20-20-20",
        "name_ar": "سماد مركب 20-20-20",
        "n": 20.0,
        "p": 20.0,
        "k": 20.0,
        "ec_per_gl": 1.30,
        "solubility_gl": 500,
        "price_sar_kg": 6.0,
    },
    FertilizerType.NPK_15_15_15: {
        "name": "NPK 15-15-15",
        "name_ar": "سماد مركب 15-15-15",
        "n": 15.0,
        "p": 15.0,
        "k": 15.0,
        "ec_per_gl": 1.10,
        "solubility_gl": 450,
        "price_sar_kg": 5.0,
    },
    FertilizerType.PHOSPHORIC_ACID: {
        "name": "Phosphoric Acid (85%)",
        "name_ar": "حمض الفوسفوريك",
        "n": 0.0,
        "p": 52.0,
        "k": 0.0,
        "ec_per_gl": 0.60,
        "solubility_gl": 5480,
        "price_sar_kg": 4.5,
    },
}

# NPK requirements by crop × growth phase (kg/ha)
CROP_NPK_REQUIREMENTS: dict[str, dict[str, dict]] = {
    "wheat": {
        GrowthPhase.SEEDLING: {"n": 20, "p": 30, "k": 15, "pct_of_total": 15},
        GrowthPhase.TILLERING: {"n": 60, "p": 15, "k": 20, "pct_of_total": 35},
        GrowthPhase.FLOWERING: {"n": 30, "p": 10, "k": 25, "pct_of_total": 25},
        GrowthPhase.RIPENING: {"n": 10, "p": 5, "k": 15, "pct_of_total": 15},
        GrowthPhase.HARVEST: {"n": 0, "p": 0, "k": 0, "pct_of_total": 0},
        "_total": {"n": 120, "p": 60, "k": 75},
    },
    "barley": {
        GrowthPhase.SEEDLING: {"n": 15, "p": 25, "k": 12, "pct_of_total": 15},
        GrowthPhase.TILLERING: {"n": 50, "p": 12, "k": 18, "pct_of_total": 35},
        GrowthPhase.FLOWERING: {"n": 25, "p": 8, "k": 20, "pct_of_total": 25},
        GrowthPhase.RIPENING: {"n": 10, "p": 5, "k": 10, "pct_of_total": 15},
        "_total": {"n": 100, "p": 50, "k": 60},
    },
    "date_palm": {
        GrowthPhase.VEGETATIVE: {"n": 40, "p": 20, "k": 60, "pct_of_total": 25},
        GrowthPhase.FLOWERING: {"n": 30, "p": 25, "k": 40, "pct_of_total": 20},
        GrowthPhase.FRUIT_DEVELOPMENT: {"n": 50, "p": 15, "k": 80, "pct_of_total": 35},
        GrowthPhase.RIPENING: {"n": 10, "p": 5, "k": 30, "pct_of_total": 15},
        "_total": {"n": 130, "p": 65, "k": 210},
    },
    "tomato": {
        GrowthPhase.SEEDLING: {"n": 15, "p": 20, "k": 10, "pct_of_total": 10},
        GrowthPhase.VEGETATIVE: {"n": 50, "p": 25, "k": 30, "pct_of_total": 25},
        GrowthPhase.FLOWERING: {"n": 40, "p": 30, "k": 50, "pct_of_total": 25},
        GrowthPhase.FRUIT_DEVELOPMENT: {"n": 60, "p": 20, "k": 80, "pct_of_total": 30},
        GrowthPhase.RIPENING: {"n": 15, "p": 5, "k": 20, "pct_of_total": 10},
        "_total": {"n": 180, "p": 100, "k": 190},
    },
    "sorghum": {
        GrowthPhase.SEEDLING: {"n": 10, "p": 20, "k": 10, "pct_of_total": 12},
        GrowthPhase.VEGETATIVE: {"n": 40, "p": 10, "k": 20, "pct_of_total": 35},
        GrowthPhase.FLOWERING: {"n": 25, "p": 8, "k": 20, "pct_of_total": 28},
        GrowthPhase.RIPENING: {"n": 10, "p": 5, "k": 10, "pct_of_total": 15},
        "_total": {"n": 85, "p": 43, "k": 60},
    },
    "qat": {
        GrowthPhase.VEGETATIVE: {"n": 60, "p": 20, "k": 40, "pct_of_total": 40},
        GrowthPhase.FLOWERING: {"n": 30, "p": 15, "k": 25, "pct_of_total": 25},
        GrowthPhase.HARVEST: {"n": 40, "p": 10, "k": 30, "pct_of_total": 25},
        "_total": {"n": 130, "p": 45, "k": 95},
    },
    "coffee_arabica": {
        GrowthPhase.VEGETATIVE: {"n": 40, "p": 15, "k": 35, "pct_of_total": 30},
        GrowthPhase.FLOWERING: {"n": 30, "p": 20, "k": 30, "pct_of_total": 25},
        GrowthPhase.FRUIT_DEVELOPMENT: {"n": 40, "p": 15, "k": 45, "pct_of_total": 30},
        GrowthPhase.RIPENING: {"n": 10, "p": 5, "k": 15, "pct_of_total": 15},
        "_total": {"n": 120, "p": 55, "k": 125},
    },
    "alfalfa": {
        GrowthPhase.SEEDLING: {"n": 10, "p": 30, "k": 20, "pct_of_total": 15},
        GrowthPhase.VEGETATIVE: {"n": 5, "p": 15, "k": 60, "pct_of_total": 50},
        GrowthPhase.HARVEST: {"n": 5, "p": 10, "k": 30, "pct_of_total": 25},
        "_total": {"n": 20, "p": 55, "k": 110},
    },
}


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class FertigationRequest(BaseModel):
    """Calculate fertigation schedule for a field."""

    crop: str = Field(..., description="Crop name")
    growth_phase: GrowthPhase
    field_area_ha: float = Field(default=1.0, ge=0.01, description="Field area (ha)")
    soil_n_ppm: float | None = Field(None, description="Current soil N (ppm)")
    soil_p_ppm: float | None = Field(None, description="Current soil P (ppm)")
    soil_k_ppm: float | None = Field(None, description="Current soil K (ppm)")
    irrigation_volume_m3: float = Field(..., description="Irrigation volume per event (m³)")
    ec_water: float = Field(default=0.5, description="Irrigation water EC (dS/m)")
    max_ec_solution: float = Field(default=2.5, description="Max EC of fertigation solution (dS/m)")
    target_yield_tha: float | None = Field(None, description="Target yield (t/ha)")
    preferred_fertilizers: list[FertilizerType] | None = None


class FertigationPlan(BaseModel):
    """Fertigation schedule result."""

    crop: str
    crop_ar: str | None = None
    growth_phase: str
    field_area_ha: float
    # NPK requirements
    n_required_kg_ha: float
    p_required_kg_ha: float
    k_required_kg_ha: float
    # Adjustments for soil
    n_adjusted_kg_ha: float
    p_adjusted_kg_ha: float
    k_adjusted_kg_ha: float
    # Fertilizer recommendations
    fertilizer_plan: list[dict]
    # EC management
    ec_water: float
    ec_fertilizer_contribution: float
    ec_total: float
    ec_within_limit: bool
    # Cost
    total_cost_sar: float
    cost_per_ha_sar: float
    # Environmental
    n_loss_risk: str
    n_loss_risk_ar: str
    p_loss_risk: str
    p_loss_risk_ar: str
    recommendations: list[str]
    recommendations_ar: list[str]


class NutrientBalanceRequest(BaseModel):
    """Track nutrient balance over time."""

    field_id: str
    crop: str
    entries: list[dict] = Field(
        ...,
        description="List of {date, type: 'applied'|'removed', n_kg, p_kg, k_kg}",
    )


class NutrientBalance(BaseModel):
    """Nutrient balance summary."""

    field_id: str
    crop: str
    n_balance_kg_ha: float
    p_balance_kg_ha: float
    k_balance_kg_ha: float
    n_efficiency_pct: float
    p_efficiency_pct: float
    k_efficiency_pct: float
    surplus_alert: bool
    deficit_alert: bool
    recommendations: list[str]
    recommendations_ar: list[str]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class FertigationEngine:
    """Core fertigation calculation engine."""

    def __init__(self):
        self._yemen_crops = {}
        try:
            from shared.yemen.crops import YEMEN_CROPS

            self._yemen_crops = YEMEN_CROPS
        except ImportError:
            pass

    def calculate_fertigation(self, req: FertigationRequest) -> FertigationPlan:
        """Calculate fertigation plan for given crop and growth phase."""
        crop_key = req.crop.lower().replace(" ", "_")
        npk_data = CROP_NPK_REQUIREMENTS.get(crop_key, {})

        # Get phase requirements
        phase_data = npk_data.get(req.growth_phase)
        if not phase_data:
            # Fallback to generic medium requirements
            phase_data = {"n": 30, "p": 15, "k": 25, "pct_of_total": 25}

        n_req = phase_data["n"]
        p_req = phase_data["p"]
        k_req = phase_data["k"]

        # Adjust for existing soil nutrients (credit)
        n_adj = n_req
        p_adj = p_req
        k_adj = k_req
        if req.soil_n_ppm is not None:
            # N credit: roughly 1 ppm soil N ≈ 2 kg/ha available N
            n_credit = req.soil_n_ppm * 2.0
            n_adj = max(0, n_req - n_credit * 0.3)  # Use 30% of soil N
        if req.soil_p_ppm is not None:
            p_credit = req.soil_p_ppm * 1.5
            p_adj = max(0, p_req - p_credit * 0.2)
        if req.soil_k_ppm is not None:
            k_credit = req.soil_k_ppm * 1.2
            k_adj = max(0, k_req - k_credit * 0.2)

        # Select fertilizers and calculate rates
        fertilizer_plan = self._select_fertilizers(
            n_adj,
            p_adj,
            k_adj,
            req.field_area_ha,
            req.irrigation_volume_m3,
            req.ec_water,
            req.max_ec_solution,
            req.preferred_fertilizers,
        )

        # Calculate EC contribution
        total_ec_fert = sum(f.get("ec_contribution", 0) for f in fertilizer_plan)
        ec_total = req.ec_water + total_ec_fert
        ec_ok = ec_total <= req.max_ec_solution

        # Calculate cost
        total_cost = sum(f.get("cost_sar", 0) for f in fertilizer_plan)
        cost_per_ha = total_cost / max(req.field_area_ha, 0.01)

        # Assess environmental risk
        n_risk, n_risk_ar = self._assess_n_loss_risk(n_adj, req.crop)
        p_risk, p_risk_ar = self._assess_p_loss_risk(p_adj)

        # Generate recommendations
        recs, recs_ar = self._generate_recommendations(
            n_adj,
            p_adj,
            k_adj,
            ec_total,
            req.max_ec_solution,
            req.growth_phase,
            crop_key,
        )

        crop_data = self._yemen_crops.get(crop_key)

        return FertigationPlan(
            crop=req.crop,
            crop_ar=crop_data.name_ar if crop_data else None,
            growth_phase=req.growth_phase.value,
            field_area_ha=req.field_area_ha,
            n_required_kg_ha=round(n_req, 1),
            p_required_kg_ha=round(p_req, 1),
            k_required_kg_ha=round(k_req, 1),
            n_adjusted_kg_ha=round(n_adj, 1),
            p_adjusted_kg_ha=round(p_adj, 1),
            k_adjusted_kg_ha=round(k_adj, 1),
            fertilizer_plan=fertilizer_plan,
            ec_water=req.ec_water,
            ec_fertilizer_contribution=round(total_ec_fert, 2),
            ec_total=round(ec_total, 2),
            ec_within_limit=ec_ok,
            total_cost_sar=round(total_cost, 2),
            cost_per_ha_sar=round(cost_per_ha, 2),
            n_loss_risk=n_risk,
            n_loss_risk_ar=n_risk_ar,
            p_loss_risk=p_risk,
            p_loss_risk_ar=p_risk_ar,
            recommendations=recs,
            recommendations_ar=recs_ar,
        )

    def _select_fertilizers(
        self,
        n_kg: float,
        p_kg: float,
        k_kg: float,
        area_ha: float,
        irr_vol_m3: float,
        ec_water: float,
        max_ec: float,
        preferred: list[FertilizerType] | None,
    ) -> list[dict]:
        """Select optimal fertilizer combination, respecting user preferences."""
        plan = []
        remaining_n = n_kg * area_ha
        remaining_p = p_kg * area_ha
        remaining_k = k_kg * area_ha
        max_ec - ec_water

        # Helper: pick preferred fertilizer with nutrient, or fallback to default
        def _pick_fert(nutrient: str, default: FertilizerType) -> FertilizerType:
            if preferred:
                for pf in preferred:
                    fdata = FERTILIZER_DB.get(pf, {})
                    if fdata.get(nutrient, 0) > 0:
                        return pf
            return default

        # Greedy approach: satisfy P first, then N, then K
        # P sources
        if remaining_p > 0:
            p_type = _pick_fert("p", FertilizerType.MAP)
            fert = FERTILIZER_DB[p_type]
            amount_kg = remaining_p / (fert["p"] / 100.0)
            ec_contrib = (amount_kg / max(irr_vol_m3, 1)) * fert["ec_per_gl"]
            plan.append(
                {
                    "fertilizer": p_type.value,
                    "name": fert["name"],
                    "name_ar": fert["name_ar"],
                    "amount_kg": round(amount_kg, 2),
                    "n_supplied_kg": round(amount_kg * fert["n"] / 100, 2),
                    "p_supplied_kg": round(amount_kg * fert["p"] / 100, 2),
                    "k_supplied_kg": 0.0,
                    "ec_contribution": round(ec_contrib, 3),
                    "cost_sar": round(amount_kg * fert["price_sar_kg"], 2),
                }
            )
            remaining_n -= amount_kg * fert["n"] / 100
            remaining_p = 0

        # N sources (remaining)
        if remaining_n > 0:
            n_type = _pick_fert("n", FertilizerType.UREA)
            fert = FERTILIZER_DB[n_type]
            amount_kg = remaining_n / (fert["n"] / 100.0)
            ec_contrib = (amount_kg / max(irr_vol_m3, 1)) * fert["ec_per_gl"]
            plan.append(
                {
                    "fertilizer": n_type.value,
                    "name": fert["name"],
                    "name_ar": fert["name_ar"],
                    "amount_kg": round(amount_kg, 2),
                    "n_supplied_kg": round(amount_kg * fert["n"] / 100, 2),
                    "p_supplied_kg": 0.0,
                    "k_supplied_kg": 0.0,
                    "ec_contribution": round(ec_contrib, 3),
                    "cost_sar": round(amount_kg * fert["price_sar_kg"], 2),
                }
            )

        # K sources
        if remaining_k > 0:
            # Use SOP in saline conditions, KCL otherwise
            default_k = FertilizerType.SOP if ec_water > 1.5 else FertilizerType.KCL
            fert_type = _pick_fert("k", default_k)
            fert = FERTILIZER_DB[fert_type]
            amount_kg = remaining_k / (fert["k"] / 100.0)
            ec_contrib = (amount_kg / max(irr_vol_m3, 1)) * fert["ec_per_gl"]
            plan.append(
                {
                    "fertilizer": fert_type.value,
                    "name": fert["name"],
                    "name_ar": fert["name_ar"],
                    "amount_kg": round(amount_kg, 2),
                    "n_supplied_kg": 0.0,
                    "p_supplied_kg": 0.0,
                    "k_supplied_kg": round(amount_kg * fert["k"] / 100, 2),
                    "ec_contribution": round(ec_contrib, 3),
                    "cost_sar": round(amount_kg * fert["price_sar_kg"], 2),
                }
            )

        return plan

    def _assess_n_loss_risk(self, n_kg_ha: float, crop: str) -> tuple[str, str]:
        if n_kg_ha > 80:
            return "high", "مرتفع"
        elif n_kg_ha > 40:
            return "moderate", "متوسط"
        return "low", "منخفض"

    def _assess_p_loss_risk(self, p_kg_ha: float) -> tuple[str, str]:
        if p_kg_ha > 50:
            return "high", "مرتفع"
        elif p_kg_ha > 25:
            return "moderate", "متوسط"
        return "low", "منخفض"

    def _generate_recommendations(
        self,
        n: float,
        p: float,
        k: float,
        ec_total: float,
        max_ec: float,
        phase: GrowthPhase,
        crop: str,
    ) -> tuple[list[str], list[str]]:
        recs: list[str] = []
        recs_ar: list[str] = []

        if ec_total > max_ec:
            recs.append(
                f"EC total ({ec_total:.1f} dS/m) exceeds limit ({max_ec:.1f}). "
                "Split fertigation into multiple applications."
            )
            recs_ar.append(
                f"الموصلية الكهربائية الكلية ({ec_total:.1f} dS/m) تتجاوز الحد ({max_ec:.1f}). "
                "قسّم التسميد على عدة تطبيقات."
            )

        if n > 60:
            recs.append("High N application. Apply early morning to reduce volatilization losses.")
            recs_ar.append("تطبيق نيتروجين مرتفع. طبّق في الصباح الباكر لتقليل فقد التطاير.")

        if phase == GrowthPhase.FLOWERING:
            recs.append("Reduce N during flowering to prevent excessive vegetative growth.")
            recs_ar.append("قلل النيتروجين أثناء الإزهار لمنع النمو الخضري المفرط.")

        if phase == GrowthPhase.FRUIT_DEVELOPMENT:
            recs.append("Increase K during fruit development for quality and size.")
            recs_ar.append("زد البوتاسيوم أثناء نمو الثمار لتحسين الجودة والحجم.")

        return recs, recs_ar

    def calculate_nutrient_balance(self, req: NutrientBalanceRequest) -> NutrientBalance:
        """Calculate cumulative nutrient balance for a field."""
        applied = {"n": 0.0, "p": 0.0, "k": 0.0}
        removed = {"n": 0.0, "p": 0.0, "k": 0.0}

        for entry in req.entries:
            target = applied if entry.get("type") == "applied" else removed
            target["n"] += entry.get("n_kg", 0)
            target["p"] += entry.get("p_kg", 0)
            target["k"] += entry.get("k_kg", 0)

        n_bal = applied["n"] - removed["n"]
        p_bal = applied["p"] - removed["p"]
        k_bal = applied["k"] - removed["k"]

        n_eff = (removed["n"] / max(applied["n"], 0.01)) * 100
        p_eff = (removed["p"] / max(applied["p"], 0.01)) * 100
        k_eff = (removed["k"] / max(applied["k"], 0.01)) * 100

        surplus = n_bal > 50 or p_bal > 30 or k_bal > 40
        deficit = n_bal < -20 or p_bal < -10 or k_bal < -15

        recs = []
        recs_ar = []
        if n_bal > 50:
            recs.append("Nitrogen surplus detected. Risk of groundwater contamination.")
            recs_ar.append("فائض نيتروجين. خطر تلوث المياه الجوفية.")
        if n_bal < -20:
            recs.append("Nitrogen deficit. Crop may show yellowing symptoms.")
            recs_ar.append("نقص نيتروجين. قد يظهر اصفرار على المحصول.")

        return NutrientBalance(
            field_id=req.field_id,
            crop=req.crop,
            n_balance_kg_ha=round(n_bal, 1),
            p_balance_kg_ha=round(p_bal, 1),
            k_balance_kg_ha=round(k_bal, 1),
            n_efficiency_pct=round(n_eff, 1),
            p_efficiency_pct=round(p_eff, 1),
            k_efficiency_pct=round(k_eff, 1),
            surplus_alert=surplus,
            deficit_alert=deficit,
            recommendations=recs,
            recommendations_ar=recs_ar,
        )


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

fert_engine = FertigationEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        import structlog

        logger = structlog.get_logger(SERVICE_NAME)
    except ImportError:
        import logging

        logger = logging.getLogger(SERVICE_NAME)
    logger.info(f"Starting {SERVICE_NAME} v{VERSION} on port {PORT}")

    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats as nats_lib

            app.state.nc = await nats_lib.connect(nats_url)
        except Exception as e:
            logger.warning(f"NATS connection failed: {e}")
            app.state.nc = None
    else:
        app.state.nc = None

    yield

    if getattr(app.state, "nc", None):
        await app.state.nc.close()


app = FastAPI(
    title="Fertigation Engine",
    description="Integrated fertilizer + irrigation management with NPK scheduling",
    version=VERSION,
    lifespan=lifespan,
)

try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

if _has_tenant_middleware:
    app.add_middleware(TenantContextMiddleware)


# Health endpoints
@app.get("/healthz")
def health():
    return {"status": "ok", "service": SERVICE_NAME, "version": VERSION}


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "crops_with_npk": len(CROP_NPK_REQUIREMENTS),
        "fertilizers_available": len(FERTILIZER_DB),
        "nats": getattr(app.state, "nc", None) is not None,
    }


# Fertigation endpoints
@app.post("/api/v1/fertigation/plan", response_model=FertigationPlan)
async def create_fertigation_plan(req: FertigationRequest, current_user: User = Depends(get_current_user)):
    """
    Calculate fertigation plan with NPK requirements, fertilizer selection,
    EC management, and environmental risk assessment.
    """
    try:
        result = fert_engine.calculate_fertigation(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    nc = getattr(app.state, "nc", None)
    if nc:
        try:
            tenant_id = getattr(current_user, "tenant_id", None) or os.getenv("TENANT_ID", "default")
            await nc.publish(
                f"sahool.{tenant_id}.fertigation.plan_created",
                json.dumps(
                    {
                        "crop": req.crop,
                        "phase": req.growth_phase.value,
                        "n_kg": result.n_adjusted_kg_ha,
                        "ec_total": result.ec_total,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ).encode(),
            )
        except Exception as e:
            logger.error("Failed to publish NATS event: %s", e)

    return result


@app.post("/api/v1/fertigation/nutrient-balance", response_model=NutrientBalance)
async def calculate_balance(req: NutrientBalanceRequest, current_user: User = Depends(get_current_user)):
    """Track and analyze nutrient balance for a field."""
    return fert_engine.calculate_nutrient_balance(req)


# Reference data endpoints
@app.get("/api/v1/fertigation/fertilizers")
async def list_fertilizers():
    """List available fertilizers with NPK content and pricing."""
    return {
        "fertilizers": [
            {
                "type": ftype,
                **dict(fdata.items()),
            }
            for ftype, fdata in FERTILIZER_DB.items()
        ],
        "total": len(FERTILIZER_DB),
    }


@app.get("/api/v1/fertigation/crops/{crop_name}/npk")
async def get_crop_npk(crop_name: str):
    """Get NPK requirements by growth phase for a crop."""
    crop_key = crop_name.lower().replace(" ", "_")
    npk = CROP_NPK_REQUIREMENTS.get(crop_key)
    if not npk:
        raise HTTPException(status_code=404, detail=f"NPK data not found for: {crop_name}")

    total = npk.get("_total", {})
    phases = {k: v for k, v in npk.items() if k != "_total"}
    return {
        "crop": crop_name,
        "total_requirements_kg_ha": total,
        "by_phase": phases,
    }


@app.get("/api/v1/fertigation/crops")
async def list_crops_with_npk():
    """List crops with NPK data available."""
    return {
        "crops": [
            {
                "name": crop,
                "total_n": data.get("_total", {}).get("n", 0),
                "total_p": data.get("_total", {}).get("p", 0),
                "total_k": data.get("_total", {}).get("k", 0),
                "phases": len([k for k in data if k != "_total"]),
            }
            for crop, data in CROP_NPK_REQUIREMENTS.items()
        ],
        "total": len(CROP_NPK_REQUIREMENTS),
    }


@app.get("/api/v1/fertigation/growth-phases")
async def list_growth_phases():
    """List available growth phases."""
    return {"phases": [p.value for p in GrowthPhase]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
