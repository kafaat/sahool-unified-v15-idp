"""
Event Types - SAHOOL Agro Advisor
Event type constants and subjects
Unified namespace: sahool.advisory.*
"""

# Event Types
RECOMMENDATION_ISSUED = "recommendation_issued"
FERTILIZER_PLAN_ISSUED = "fertilizer_plan_issued"
NUTRIENT_ASSESSMENT_ISSUED = "nutrient_assessment_issued"
DISEASE_DETECTED = "disease_detected"

# Subject prefix (unified with sahool.* namespace)
SUBJECT_PREFIX = "sahool.advisory"

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


def get_subject(event_type: str, tenant_id: str | None = None) -> str:
    """Get NATS subject for event type, optionally scoped to a tenant.

    Returns a tenant-scoped subject when tenant_id is provided for multi-tenant isolation.
    يرجع موضوع مخصص للمستأجر عند توفر معرف المستأجر لعزل البيانات.

    Args:
        event_type: The event type (e.g., 'recommendation_issued')
        tenant_id: Optional tenant ID for scoped subjects

    Returns:
        Global subject: sahool.advisory.{event_type}
        Tenant subject: sahool.tenant.{tenant_id}.advisory.{event_type}
    """
    # Use tenant-scoped subject for data isolation | استخدام موضوع مخصص للمستأجر لعزل البيانات
    if tenant_id:
        from shared.events.subjects import get_tenant_subject
        action = SUBJECTS.get(event_type, f"{SUBJECT_PREFIX}.{event_type}").removeprefix(f"{SUBJECT_PREFIX}.")
        return get_tenant_subject(tenant_id, "advisory", action)
    return SUBJECTS.get(event_type, f"{SUBJECT_PREFIX}.{event_type}")


def get_version(event_type: str) -> int:
    """Get current version for event type"""
    return VERSIONS.get(event_type, 1)
