"""
Fertilizer Planner - SAHOOL Agro Advisor
Crop-stage-based fertilizer planning for Yemen agriculture
"""

from ..kb.fertilizers import get_fertilizer

# Crop nutrient requirements (kg/ha for target yield)
CROP_REQUIREMENTS = {
    "tomato": {
        "yield_target_ton_ha": 40,
        "total_needs": {"N": 150, "P": 60, "K": 200, "Ca": 80},
        "stages": {
            "transplant": {"N": 0.10, "P": 0.30, "K": 0.10},
            "vegetative": {"N": 0.30, "P": 0.20, "K": 0.20},
            "flowering": {"N": 0.25, "P": 0.25, "K": 0.25},
            "fruiting": {"N": 0.25, "P": 0.15, "K": 0.35},
            "harvest": {"N": 0.10, "P": 0.10, "K": 0.10},
        },
    },
    "wheat": {
        "yield_target_ton_ha": 5,
        "total_needs": {"N": 120, "P": 40, "K": 60},
        "stages": {
            "planting": {"N": 0.20, "P": 0.50, "K": 0.40},
            "tillering": {"N": 0.40, "P": 0.30, "K": 0.30},
            "booting": {"N": 0.30, "P": 0.15, "K": 0.20},
            "heading": {"N": 0.10, "P": 0.05, "K": 0.10},
        },
    },
    "potato": {
        "yield_target_ton_ha": 30,
        "total_needs": {"N": 180, "P": 80, "K": 250},
        "stages": {
            "planting": {"N": 0.15, "P": 0.40, "K": 0.15},
            "vegetative": {"N": 0.35, "P": 0.25, "K": 0.25},
            "tuber_init": {"N": 0.30, "P": 0.20, "K": 0.30},
            "bulking": {"N": 0.15, "P": 0.10, "K": 0.25},
            "maturation": {"N": 0.05, "P": 0.05, "K": 0.05},
        },
    },
    "maize": {
        "yield_target_ton_ha": 8,
        "total_needs": {"N": 200, "P": 50, "K": 100},
        "stages": {
            "planting": {"N": 0.15, "P": 0.50, "K": 0.30},
            "v6": {"N": 0.35, "P": 0.25, "K": 0.30},
            "v12": {"N": 0.30, "P": 0.15, "K": 0.25},
            "tasseling": {"N": 0.15, "P": 0.08, "K": 0.10},
            "grain_fill": {"N": 0.05, "P": 0.02, "K": 0.05},
        },
    },
    "onion": {
        "yield_target_ton_ha": 35,
        "total_needs": {"N": 120, "P": 50, "K": 150},
        "stages": {
            "transplant": {"N": 0.15, "P": 0.35, "K": 0.15},
            "vegetative": {"N": 0.35, "P": 0.30, "K": 0.25},
            "bulb_init": {"N": 0.30, "P": 0.20, "K": 0.35},
            "bulbing": {"N": 0.15, "P": 0.10, "K": 0.20},
            "maturation": {"N": 0.05, "P": 0.05, "K": 0.05},
        },
    },
    "coffee": {
        "yield_target_ton_ha": 1.5,
        "total_needs": {"N": 150, "P": 30, "K": 180, "Mg": 20},
        "stages": {
            "dormant": {"N": 0.10, "P": 0.20, "K": 0.10},
            "flowering": {"N": 0.25, "P": 0.30, "K": 0.20},
            "fruit_dev": {"N": 0.35, "P": 0.30, "K": 0.35},
            "ripening": {"N": 0.20, "P": 0.15, "K": 0.30},
            "post_harvest": {"N": 0.10, "P": 0.05, "K": 0.05},
        },
    },
    "qat": {
        "yield_target_ton_ha": 4,
        "total_needs": {"N": 200, "P": 40, "K": 150},
        "stages": {
            "pruning": {"N": 0.20, "P": 0.30, "K": 0.15},
            "flush_1": {"N": 0.30, "P": 0.25, "K": 0.30},
            "flush_2": {"N": 0.30, "P": 0.25, "K": 0.30},
            "flush_3": {"N": 0.20, "P": 0.20, "K": 0.25},
        },
    },
}


class FertilizerPlan:
    """Generated fertilizer plan"""

    def __init__(
        self,
        crop: str,
        stage: str,
        field_size_ha: float,
        applications: list[dict],
        total_cost_estimate: float = None,
        notes: list[str] = None,
    ):
        self.crop = crop
        self.stage = stage
        self.field_size_ha = field_size_ha
        self.applications = applications
        self.total_cost_estimate = total_cost_estimate
        self.notes = notes or []

    def to_dict(self) -> dict:
        return {
            "crop": self.crop,
            "stage": self.stage,
            "field_size_ha": self.field_size_ha,
            "applications": self.applications,
            "total_cost_estimate": self.total_cost_estimate,
            "notes": self.notes,
        }


def fertilizer_plan(
    crop: str,
    stage: str,
    field_size_ha: float = 1.0,
    soil_fertility: str = "medium",
    irrigation_type: str = "drip",
    budget_constraint: str = None,
) -> FertilizerPlan:
    """
    Generate fertilizer plan for crop and stage

    Args:
        crop: Crop type
        stage: Growth stage
        field_size_ha: Field size in hectares
        soil_fertility: low/medium/high
        irrigation_type: drip/surface/sprinkler
        budget_constraint: low/medium/high or None

    Returns:
        FertilizerPlan with applications
    """
    crop_data = CROP_REQUIREMENTS.get(crop)
    if not crop_data:
        return _default_plan(crop, stage, field_size_ha)

    stage_ratios = crop_data["stages"].get(stage)
    if not stage_ratios:
        # Try to find closest stage
        stages = list(crop_data["stages"].keys())
        stage = stages[0] if stages else "general"
        stage_ratios = crop_data["stages"].get(stage, {"N": 0.25, "P": 0.25, "K": 0.25})

    # Calculate nutrient needs for this stage
    total_needs = crop_data["total_needs"]
    stage_needs = {
        nutrient: total_needs.get(nutrient, 0) * stage_ratios.get(nutrient, 0)
        for nutrient in ["N", "P", "K"]
    }

    # Adjust for soil fertility
    fertility_factor = {"low": 1.2, "medium": 1.0, "high": 0.8}.get(soil_fertility, 1.0)
    stage_needs = {k: v * fertility_factor for k, v in stage_needs.items()}

    # Select fertilizers based on irrigation type
    applications = _select_fertilizers(
        stage_needs, field_size_ha, irrigation_type, budget_constraint
    )

    # Add notes
    notes = []
    if irrigation_type == "drip":
        notes.append("يفضل تقسيم الجرعة على 2-3 ريات")
        notes.append("Divide dose over 2-3 irrigations")
    if stage in ["fruiting", "bulking", "grain_fill"]:
        notes.append("مرحلة حرجة - لا تؤخر التسميد")
        notes.append("Critical stage - do not delay fertilization")

    return FertilizerPlan(
        crop=crop,
        stage=stage,
        field_size_ha=field_size_ha,
        applications=applications,
        notes=notes,
    )


def _select_fertilizers(
    needs: dict,
    field_size_ha: float,
    irrigation_type: str,
    budget: str,
) -> list[dict]:
    """Select appropriate fertilizers for given needs"""
    applications = []

    # Prefer soluble for drip, granular for others
    prefer_soluble = irrigation_type == "drip"

    # NPK needs
    n_need = needs.get("N", 0)
    p_need = needs.get("P", 0)
    k_need = needs.get("K", 0)

    # Try compound first if balanced needs
    if abs(n_need - p_need) < 10 and abs(p_need - k_need) < 10:
        # Balanced - use NPK compound
        npk = get_fertilizer("npk_20_20_20" if prefer_soluble else "npk_15_15_15")
        if npk:
            avg_need = (n_need + p_need + k_need) / 3
            dose = (avg_need / 20) * 100  # Assuming 20% content
            applications.append(
                {
                    "product": npk["name_en"],
                    "product_ar": npk["name_ar"],
                    "dose_kg_per_ha": round(dose, 1),
                    "total_kg": round(dose * field_size_ha, 1),
                    "timing_days": 0,
                    "method": "fertigation" if prefer_soluble else "broadcast",
                }
            )
            return applications

    # Otherwise, use individual fertilizers
    if n_need > 10:
        if prefer_soluble:
            fert = get_fertilizer("calcium_nitrate")
            dose = (n_need / 15.5) * 100
        else:
            fert = get_fertilizer("urea")
            dose = (n_need / 46) * 100

        if fert:
            applications.append(
                {
                    "product": fert["name_en"],
                    "product_ar": fert["name_ar"],
                    "dose_kg_per_ha": round(dose, 1),
                    "total_kg": round(dose * field_size_ha, 1),
                    "timing_days": 0,
                    "method": "fertigation" if prefer_soluble else "side_dress",
                }
            )

    if p_need > 5:
        fert = get_fertilizer("dap")
        if fert:
            dose = (p_need / 46) * 100
            applications.append(
                {
                    "product": fert["name_en"],
                    "product_ar": fert["name_ar"],
                    "dose_kg_per_ha": round(dose, 1),
                    "total_kg": round(dose * field_size_ha, 1),
                    "timing_days": 0,
                    "method": "banding" if not prefer_soluble else "fertigation",
                }
            )

    if k_need > 10:
        fert = get_fertilizer("potassium_sulfate")
        if fert:
            dose = (k_need / 50) * 100
            applications.append(
                {
                    "product": fert["name_en"],
                    "product_ar": fert["name_ar"],
                    "dose_kg_per_ha": round(dose, 1),
                    "total_kg": round(dose * field_size_ha, 1),
                    "timing_days": 3,  # Stagger K application
                    "method": "fertigation" if prefer_soluble else "broadcast",
                }
            )

    return applications


def _default_plan(crop: str, stage: str, field_size_ha: float) -> FertilizerPlan:
    """Generate default plan for unknown crop"""
    npk = get_fertilizer("npk_15_15_15")

    return FertilizerPlan(
        crop=crop,
        stage=stage,
        field_size_ha=field_size_ha,
        applications=[
            {
                "product": npk["name_en"] if npk else "NPK 15-15-15",
                "product_ar": npk["name_ar"] if npk else "NPK 15-15-15",
                "dose_kg_per_ha": 100,
                "total_kg": 100 * field_size_ha,
                "timing_days": 0,
                "method": "broadcast",
            }
        ],
        notes=[
            "خطة عامة - راجع المختص للتوصية المخصصة",
            "General plan - consult specialist for customized recommendation",
        ],
    )


def get_stage_timeline(crop: str) -> list[dict]:
    """Get growth stages timeline for a crop"""
    crop_data = CROP_REQUIREMENTS.get(crop)
    if not crop_data:
        return []

    stages = list(crop_data["stages"].keys())

    # Typical durations (simplified)
    STAGE_DURATIONS = {
        "tomato": {
            "transplant": 14,
            "vegetative": 30,
            "flowering": 21,
            "fruiting": 45,
            "harvest": 30,
        },
        "wheat": {"planting": 21, "tillering": 35, "booting": 21, "heading": 28},
        "potato": {
            "planting": 21,
            "vegetative": 28,
            "tuber_init": 21,
            "bulking": 35,
            "maturation": 21,
        },
    }

    durations = STAGE_DURATIONS.get(crop, {})
    timeline = []
    day = 0

    for stage in stages:
        duration = durations.get(stage, 21)
        timeline.append(
            {
                "stage": stage,
                "start_day": day,
                "duration_days": duration,
                "nutrient_focus": list(crop_data["stages"][stage].keys()),
            }
        )
        day += duration

    return timeline
