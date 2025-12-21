"""
Event Types - SAHOOL Agro Advisor
Event type constants and subjects
"""

# Event Types
RECOMMENDATION_ISSUED = "recommendation_issued"
FERTILIZER_PLAN_ISSUED = "fertilizer_plan_issued"
NUTRIENT_ASSESSMENT_ISSUED = "nutrient_assessment_issued"
DISEASE_DETECTED = "disease_detected"

# NATS Subjects
SUBJECTS = {
    RECOMMENDATION_ISSUED: "advisor.recommendation_issued",
    FERTILIZER_PLAN_ISSUED: "advisor.fertilizer_plan_issued",
    NUTRIENT_ASSESSMENT_ISSUED: "advisor.nutrient_assessment_issued",
    DISEASE_DETECTED: "advisor.disease_detected",
}

# Event Versions
VERSIONS = {
    RECOMMENDATION_ISSUED: 1,
    FERTILIZER_PLAN_ISSUED: 1,
    NUTRIENT_ASSESSMENT_ISSUED: 1,
    DISEASE_DETECTED: 1,
}


def get_subject(event_type: str) -> str:
    """Get NATS subject for event type"""
    return SUBJECTS.get(event_type, f"advisor.{event_type}")


def get_version(event_type: str) -> int:
    """Get current version for event type"""
    return VERSIONS.get(event_type, 1)
