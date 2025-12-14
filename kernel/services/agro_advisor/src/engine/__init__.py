"""
SAHOOL Agro Advisor - Engine
Rule-based assessment and planning engines
"""

from .disease_rules import (
    DiseaseAssessment,
    assess_from_image_event,
    assess_from_symptoms,
    get_action_details,
)
from .nutrient_rules import (
    NutrientAssessment,
    assess_from_ndvi,
    assess_from_visual,
    assess_from_soil_test,
    get_correction_plan,
)
from .planner import (
    FertilizerPlan,
    fertilizer_plan,
    get_stage_timeline,
    CROP_REQUIREMENTS,
)

__all__ = [
    # Disease
    "DiseaseAssessment",
    "assess_from_image_event",
    "assess_from_symptoms",
    "get_action_details",
    # Nutrient
    "NutrientAssessment",
    "assess_from_ndvi",
    "assess_from_visual",
    "assess_from_soil_test",
    "get_correction_plan",
    # Planner
    "FertilizerPlan",
    "fertilizer_plan",
    "get_stage_timeline",
    "CROP_REQUIREMENTS",
]
