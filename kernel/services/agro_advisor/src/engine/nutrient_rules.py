"""
Nutrient Rules Engine - SAHOOL Agro Advisor
Rule-based nutrient deficiency assessment
"""

from ..kb.nutrients import (
    NUTRIENT_DEFICIENCIES,
    get_deficiency,
    get_deficiency_by_nutrient,
    diagnose_from_ndvi,
)
from ..kb.fertilizers import get_fertilizers_for_nutrient


class NutrientAssessment:
    """Result of nutrient assessment"""

    def __init__(
        self,
        deficiency_id: str,
        nutrient: str,
        category: str,
        severity: str,
        title_ar: str,
        title_en: str,
        corrections: list[dict],
        confidence: float,
        urgency_hours: int,
        details: dict = None,
    ):
        self.deficiency_id = deficiency_id
        self.nutrient = nutrient
        self.category = category
        self.severity = severity
        self.title_ar = title_ar
        self.title_en = title_en
        self.corrections = corrections
        self.confidence = confidence
        self.urgency_hours = urgency_hours
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "deficiency_id": self.deficiency_id,
            "nutrient": self.nutrient,
            "category": self.category,
            "severity": self.severity,
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "corrections": self.corrections,
            "confidence": self.confidence,
            "urgency_hours": self.urgency_hours,
            "details": self.details,
        }


def assess_from_ndvi(
    ndvi: float,
    ndvi_history: list[float] = None,
    crop: str = None,
    growth_stage: str = None,
) -> list[NutrientAssessment]:
    """
    Assess potential nutrient deficiencies from NDVI data

    Args:
        ndvi: Current NDVI value
        ndvi_history: Historical NDVI values for trend analysis
        crop: Crop type for context
        growth_stage: Current growth stage

    Returns:
        List of possible nutrient assessments
    """
    diagnoses = diagnose_from_ndvi(ndvi, ndvi_history)
    assessments = []

    for diag in diagnoses:
        deficiency = get_deficiency(diag["id"])
        if not deficiency:
            continue

        assessments.append(
            NutrientAssessment(
                deficiency_id=diag["id"],
                nutrient=deficiency["nutrient"],
                category="nutrient_deficiency",
                severity=deficiency["severity_default"],
                title_ar=deficiency["name_ar"],
                title_en=deficiency["name_en"],
                corrections=deficiency["corrections"],
                confidence=diag["confidence"],
                urgency_hours=deficiency["urgency_hours"],
                details={
                    "diagnosis_reason": diag["reason"],
                    "ndvi_value": ndvi,
                    "symptoms_ar": deficiency["symptoms_ar"],
                },
            )
        )

    return assessments


def assess_from_visual(
    indicators: dict,
    crop: str = None,
    lang: str = "ar",
) -> list[NutrientAssessment]:
    """
    Assess nutrient deficiency from visual indicators

    Args:
        indicators: Dict with visual observations:
            - leaf_color: e.g., "pale_yellow", "purple", "brown_edges"
            - pattern: e.g., "uniform", "interveinal", "marginal"
            - location: e.g., "older_leaves", "new_leaves", "all"
        crop: Crop type
        lang: Language for output

    Returns:
        List of matching nutrient assessments
    """
    assessments = []
    leaf_color = indicators.get("leaf_color", "").lower()
    pattern = indicators.get("pattern", "").lower()
    location = indicators.get("location", "").lower()

    for def_id, deficiency in NUTRIENT_DEFICIENCIES.items():
        visual = deficiency.get("visual_indicators", {})
        score = 0
        matches = []

        # Check leaf color
        if leaf_color and visual.get("leaf_color"):
            if leaf_color in visual["leaf_color"] or visual["leaf_color"] in leaf_color:
                score += 3
                matches.append("leaf_color")

        # Check pattern
        if pattern and visual.get("pattern"):
            if pattern in visual["pattern"] or visual["pattern"] in pattern:
                score += 2
                matches.append("pattern")

        # Check location
        if location and visual.get("location"):
            if location in visual["location"] or visual["location"] in location:
                score += 2
                matches.append("location")

        if score >= 3:  # Minimum match threshold
            confidence = min(0.9, 0.3 + (score * 0.1))

            symptoms_field = "symptoms_ar" if lang == "ar" else "symptoms_en"

            assessments.append(
                NutrientAssessment(
                    deficiency_id=def_id,
                    nutrient=deficiency["nutrient"],
                    category="nutrient_deficiency",
                    severity=deficiency["severity_default"],
                    title_ar=deficiency["name_ar"],
                    title_en=deficiency["name_en"],
                    corrections=deficiency["corrections"],
                    confidence=round(confidence, 2),
                    urgency_hours=deficiency["urgency_hours"],
                    details={
                        "matched_indicators": matches,
                        "match_score": score,
                        "symptoms": deficiency[symptoms_field],
                    },
                )
            )

    # Sort by confidence
    assessments.sort(key=lambda x: x.confidence, reverse=True)
    return assessments[:3]


def assess_from_soil_test(
    soil_data: dict,
    crop: str,
    target_yield: float = None,
) -> list[NutrientAssessment]:
    """
    Assess nutrient status from soil test results

    Args:
        soil_data: Dict with soil test values:
            - N_ppm: Nitrogen in ppm
            - P_ppm: Phosphorus in ppm
            - K_ppm: Potassium in ppm
            - pH: Soil pH
            - EC: Electrical conductivity
        crop: Crop type
        target_yield: Optional target yield for recommendations

    Returns:
        List of deficiency assessments
    """
    # Optimal ranges (simplified)
    OPTIMAL_RANGES = {
        "N": {"low": 20, "optimal": 40, "high": 80},
        "P": {"low": 10, "optimal": 25, "high": 50},
        "K": {"low": 100, "optimal": 200, "high": 400},
    }

    assessments = []

    for nutrient, ranges in OPTIMAL_RANGES.items():
        key = f"{nutrient}_ppm"
        value = soil_data.get(key)

        if value is None:
            continue

        if value < ranges["low"]:
            deficiency = get_deficiency_by_nutrient(nutrient)
            if deficiency:
                severity = "high" if value < ranges["low"] / 2 else "medium"
                confidence = 0.9 if value < ranges["low"] / 2 else 0.7

                assessments.append(
                    NutrientAssessment(
                        deficiency_id=deficiency["id"],
                        nutrient=nutrient,
                        category="nutrient_deficiency",
                        severity=severity,
                        title_ar=deficiency["name_ar"],
                        title_en=deficiency["name_en"],
                        corrections=deficiency["corrections"],
                        confidence=confidence,
                        urgency_hours=deficiency["urgency_hours"],
                        details={
                            "soil_value": value,
                            "optimal_range": ranges,
                            "deficit_pct": round(
                                (1 - value / ranges["optimal"]) * 100, 1
                            ),
                        },
                    )
                )

    return assessments


def get_correction_plan(
    assessment: NutrientAssessment,
    field_size_ha: float = 1.0,
    preferred_method: str = None,
) -> list[dict]:
    """
    Generate detailed correction plan for a nutrient deficiency

    Args:
        assessment: Nutrient assessment result
        field_size_ha: Field size in hectares
        preferred_method: Preferred application method (fertigation, foliar, etc.)

    Returns:
        List of correction steps with doses
    """
    plan = []
    fertilizers = get_fertilizers_for_nutrient(assessment.nutrient)

    for correction in assessment.corrections[:3]:  # Top 3 corrections
        if correction["type"] == "fertilizer":
            product_id = correction["product"]
            dose_per_ha = correction["dose_kg_ha"]

            # Find matching fertilizer
            fert_info = next(
                (
                    f
                    for f in fertilizers
                    if f["id"] == product_id or product_id in f["name_en"].lower()
                ),
                None,
            )

            if fert_info:
                plan.append(
                    {
                        "type": "fertilizer",
                        "product_id": fert_info["id"],
                        "product_name_ar": fert_info["name_ar"],
                        "product_name_en": fert_info["name_en"],
                        "dose_kg_per_ha": dose_per_ha,
                        "total_kg": round(dose_per_ha * field_size_ha, 1),
                        "application_method": preferred_method
                        or fert_info["application_methods"][0],
                        "timing": "immediate",
                    }
                )

        elif correction["type"] == "practice":
            plan.append(
                {
                    "type": "practice",
                    "action": correction["action"],
                    "timing": "immediate",
                }
            )

    return plan
