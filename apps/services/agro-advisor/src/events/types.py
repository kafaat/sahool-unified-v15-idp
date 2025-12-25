"""
Event Types - SAHOOL Agro Advisor
Event type constants and subjects
Unified namespace: sahool.advisor.*
"""

# Event Types
RECOMMENDATION_ISSUED = "recommendation_issued"
FERTILIZER_PLAN_ISSUED = "fertilizer_plan_issued"
NUTRIENT_ASSESSMENT_ISSUED = "nutrient_assessment_issued"
DISEASE_DETECTED = "disease_detected"

# Subject prefix (unified with sahool.* namespace)
SUBJECT_PREFIX = "sahool.advisor"

# NATS Subjects
SUBJECTS = {
    RECOMMENDATION_ISSUED: f"{SUBJECT_PREFIX}.recommendation_issued",
    FERTILIZER_PLAN_ISSUED: f"{SUBJECT_PREFIX}.fertilizer_plan_issued",
    NUTRIENT_ASSESSMENT_ISSUED: f"{SUBJECT_PREFIX}.nutrient_assessment_issued",
    DISEASE_DETECTED: f"{SUBJECT_PREFIX}.disease_detected",
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
    return SUBJECTS.get(event_type, f"{SUBJECT_PREFIX}.{event_type}")


def get_version(event_type: str) -> int:
    """Get current version for event type"""
    return VERSIONS.get(event_type, 1)
