"""
GlobalGAP NATS Event Definitions
أحداث GlobalGAP عبر NATS

Event contracts for GlobalGAP compliance management integration across SAHOOL platform.
عقود الأحداث لإدارة الامتثال لـ GlobalGAP عبر منصة سهول.

Usage:
    from shared.globalgap.integrations.events import (
        ComplianceUpdatedEvent,
        AuditScheduledEvent,
        NonConformanceDetectedEvent,
        CertificateExpiringEvent
    )
    from shared.events.publisher import EventPublisher

    publisher = EventPublisher()
    await publisher.connect()

    event = ComplianceUpdatedEvent(
        farm_id=uuid4(),
        ggn="4000000000001",
        compliance_score=95.5
    )
    await publisher.publish_event("sahool.globalgap.compliance.updated", event)
"""

from datetime import date, datetime
from uuid import UUID, uuid4

from pydantic import Field

from shared.events.contracts import BaseEvent

# ─────────────────────────────────────────────────────────────────────────────
# GlobalGAP Event Subjects - موضوعات أحداث GlobalGAP
# ─────────────────────────────────────────────────────────────────────────────


class GlobalGAPSubjects:
    """
    NATS subject constants for GlobalGAP events
    ثوابت موضوعات NATS لأحداث GlobalGAP
    """

    # Compliance events - أحداث الامتثال
    COMPLIANCE_UPDATED = "sahool.globalgap.compliance.updated"
    COMPLIANCE_REQUIREMENT_FAILED = "sahool.globalgap.compliance.requirement.failed"
    COMPLIANCE_SCORE_CHANGED = "sahool.globalgap.compliance.score.changed"

    # Audit events - أحداث التدقيق
    AUDIT_SCHEDULED = "sahool.globalgap.audit.scheduled"
    AUDIT_STARTED = "sahool.globalgap.audit.started"
    AUDIT_COMPLETED = "sahool.globalgap.audit.completed"
    AUDIT_REPORT_ISSUED = "sahool.globalgap.audit.report.issued"

    # Non-conformance events - أحداث عدم المطابقة
    NON_CONFORMANCE_DETECTED = "sahool.globalgap.nonconformance.detected"
    NON_CONFORMANCE_RESOLVED = "sahool.globalgap.nonconformance.resolved"
    CORRECTIVE_ACTION_CREATED = "sahool.globalgap.corrective_action.created"
    CORRECTIVE_ACTION_COMPLETED = "sahool.globalgap.corrective_action.completed"

    # Certificate events - أحداث الشهادات
    CERTIFICATE_ISSUED = "sahool.globalgap.certificate.issued"
    CERTIFICATE_EXPIRING = "sahool.globalgap.certificate.expiring"
    CERTIFICATE_EXPIRED = "sahool.globalgap.certificate.expired"
    CERTIFICATE_SUSPENDED = "sahool.globalgap.certificate.suspended"
    CERTIFICATE_RENEWED = "sahool.globalgap.certificate.renewed"

    # Farm registration events - أحداث تسجيل المزرعة
    FARM_REGISTERED = "sahool.globalgap.farm.registered"
    FARM_UPDATED = "sahool.globalgap.farm.updated"
    GGN_ASSIGNED = "sahool.globalgap.ggn.assigned"

    # Documentation events - أحداث التوثيق
    DOCUMENTATION_UPDATED = "sahool.globalgap.documentation.updated"
    RECORD_ADDED = "sahool.globalgap.record.added"
    EVIDENCE_UPLOADED = "sahool.globalgap.evidence.uploaded"

    # Integration events - أحداث التكامل
    WATER_USAGE_RECORDED = "sahool.globalgap.water_usage.recorded"
    IPM_ACTIVITY_RECORDED = "sahool.globalgap.ipm.activity.recorded"
    FERTILIZER_APPLICATION_RECORDED = "sahool.globalgap.fertilizer.application.recorded"
    TRACEABILITY_RECORD_CREATED = "sahool.globalgap.traceability.record.created"

    # Wildcards
    ALL_EVENTS = "sahool.globalgap.*"
    ALL_COMPLIANCE = "sahool.globalgap.compliance.*"
    ALL_AUDITS = "sahool.globalgap.audit.*"
    ALL_NON_CONFORMANCES = "sahool.globalgap.nonconformance.*"
    ALL_CERTIFICATES = "sahool.globalgap.certificate.*"


# ─────────────────────────────────────────────────────────────────────────────
# Compliance Events - أحداث الامتثال
# ─────────────────────────────────────────────────────────────────────────────


class ComplianceUpdatedEvent(BaseEvent):
    """
    Event emitted when farm compliance status is updated.
    حدث يُطلق عند تحديث حالة امتثال المزرعة
    """

    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    # Compliance metrics
    overall_compliance_score: float = Field(
        ..., ge=0, le=100, description="Overall compliance percentage"
    )
    major_must_compliance: float = Field(
        ..., ge=0, le=100, description="Major Must compliance %"
    )
    minor_must_compliance: float = Field(
        ..., ge=0, le=100, description="Minor Must compliance %"
    )

    # Status
    is_compliant: bool = Field(..., description="Overall compliance status")
    certification_eligible: bool = Field(..., description="Eligible for certification")

    # Change tracking
    previous_score: float | None = Field(
        None, ge=0, le=100, description="Previous compliance score"
    )
    score_change: float | None = Field(None, description="Score change amount")

    # Categories
    category_scores: dict[str, float] | None = Field(
        None,
        description="Compliance scores by category (e.g., {'FS': 95.0, 'ENV': 88.0})",
    )

    updated_by: UUID | None = Field(None, description="User who triggered update")
    update_reason: str | None = Field(None, description="Reason for update")


class ComplianceRequirementFailedEvent(BaseEvent):
    """
    Event emitted when a critical compliance requirement fails.
    حدث يُطلق عند فشل متطلب امتثال حرج
    """

    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    requirement_id: str = Field(..., description="Control point ID (e.g., AF.1.1.1)")
    requirement_title_en: str = Field(..., description="Requirement title in English")
    requirement_title_ar: str = Field(..., description="Requirement title in Arabic")

    compliance_level: str = Field(
        ...,
        pattern="^(MAJOR_MUST|MINOR_MUST|RECOMMENDED)$",
        description="Requirement level",
    )

    severity: str = Field(
        ..., pattern="^(low|medium|high|critical)$", description="Failure severity"
    )

    failure_reason_en: str | None = Field(
        None, description="Failure reason in English"
    )
    failure_reason_ar: str | None = Field(
        None, description="Failure reason in Arabic"
    )

    action_required_en: str = Field(..., description="Required action in English")
    action_required_ar: str = Field(..., description="Required action in Arabic")

    due_date: datetime | None = Field(None, description="Correction due date")


# ─────────────────────────────────────────────────────────────────────────────
# Audit Events - أحداث التدقيق
# ─────────────────────────────────────────────────────────────────────────────


class AuditScheduledEvent(BaseEvent):
    """
    Event emitted when an audit is scheduled.
    حدث يُطلق عند جدولة تدقيق
    """

    audit_id: UUID = Field(default_factory=uuid4, description="Audit identifier")
    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    audit_type: str = Field(
        ...,
        pattern="^(INITIAL|SURVEILLANCE|RENEWAL|SPECIAL)$",
        description="Type of audit",
    )

    audit_scope: list[str] = Field(
        default_factory=lambda: ["FV"], description="Audit scope (FV, CROPS_BASE, etc.)"
    )

    scheduled_date: date = Field(..., description="Scheduled audit date")
    estimated_duration_hours: int | None = Field(
        None, ge=1, description="Estimated duration in hours"
    )

    # Auditor information
    lead_auditor_name: str | None = Field(None, description="Lead auditor name")
    certification_body: str = Field(..., description="Certification body name")
    cb_code: str = Field(..., description="Certification body code")

    # Contact information
    contact_email: str | None = Field(None, description="Audit contact email")
    contact_phone: str | None = Field(None, description="Audit contact phone")

    # Preparation
    preparation_checklist_url: str | None = Field(
        None, description="Preparation checklist URL"
    )
    documents_required: list[str] | None = Field(
        default_factory=list, description="Required documents for audit"
    )

    scheduled_by: UUID | None = Field(
        None, description="User who scheduled the audit"
    )


class AuditCompletedEvent(BaseEvent):
    """
    Event emitted when an audit is completed.
    حدث يُطلق عند إكمال تدقيق
    """

    audit_id: UUID = Field(..., description="Audit identifier")
    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    audit_type: str = Field(..., description="Type of audit")
    completion_date: datetime = Field(
        default_factory=datetime.utcnow, description="Completion date"
    )

    # Results
    total_items_checked: int = Field(..., ge=0, description="Total items checked")
    compliant_items: int = Field(..., ge=0, description="Number of compliant items")
    non_compliant_items: int = Field(
        ..., ge=0, description="Number of non-compliant items"
    )
    not_applicable_items: int = Field(..., ge=0, description="Number of N/A items")

    overall_compliance_score: float = Field(
        ..., ge=0, le=100, description="Overall compliance percentage"
    )

    # Non-conformances
    critical_non_conformances: int = Field(default=0, ge=0, description="Critical NCs")
    major_non_conformances: int = Field(default=0, ge=0, description="Major NCs")
    minor_non_conformances: int = Field(default=0, ge=0, description="Minor NCs")

    # Recommendation
    audit_recommendation: str | None = Field(
        None,
        pattern="^(APPROVE|REJECT|CONDITIONAL)$",
        description="Auditor recommendation",
    )

    # Auditor
    lead_auditor_name: str = Field(..., description="Lead auditor name")
    certification_body: str = Field(..., description="Certification body")

    # Next steps
    corrective_actions_required: bool = Field(
        ..., description="Corrective actions needed"
    )
    follow_up_audit_required: bool = Field(
        default=False, description="Follow-up audit required"
    )
    estimated_report_date: date | None = Field(
        None, description="Estimated report issue date"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Non-Conformance Events - أحداث عدم المطابقة
# ─────────────────────────────────────────────────────────────────────────────


class NonConformanceDetectedEvent(BaseEvent):
    """
    Event emitted when a non-conformance is detected.
    حدث يُطلق عند اكتشاف عدم مطابقة
    """

    non_conformance_id: UUID = Field(default_factory=uuid4, description="NC identifier")
    nc_number: str = Field(..., description="NC reference number (e.g., NC-2024-001)")

    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    audit_id: UUID | None = Field(None, description="Related audit ID")

    severity: str = Field(
        ..., pattern="^(CRITICAL|MAJOR|MINOR)$", description="NC severity"
    )

    # Control point
    control_point_id: str = Field(..., description="Control point ID (e.g., AF.1.1.1)")
    control_point_title_en: str = Field(
        ..., description="Control point title in English"
    )
    control_point_title_ar: str = Field(
        ..., description="Control point title in Arabic"
    )

    category_code: str = Field(..., description="Category code (e.g., FS, ENV)")

    # Description
    description_en: str = Field(..., description="NC description in English")
    description_ar: str = Field(..., description="NC description in Arabic")

    root_cause_en: str | None = Field(None, description="Root cause in English")
    root_cause_ar: str | None = Field(None, description="Root cause in Arabic")

    # Dates
    identified_date: datetime = Field(
        default_factory=datetime.utcnow, description="Date identified"
    )
    due_date: datetime = Field(..., description="Correction due date")

    # Evidence
    evidence_photos: list[str] = Field(default_factory=list, description="Photo URLs")
    evidence_documents: list[str] = Field(
        default_factory=list, description="Document URLs"
    )

    # Impact
    certification_impact: str = Field(
        ...,
        pattern="^(BLOCKING|WARNING|INFORMATIONAL)$",
        description="Impact on certification",
    )

    # Responsible
    identified_by: UUID | None = Field(
        None, description="User/auditor who identified NC"
    )
    assigned_to: UUID | None = Field(
        None, description="User responsible for correction"
    )


class CorrectiveActionCompletedEvent(BaseEvent):
    """
    Event emitted when a corrective action is completed.
    حدث يُطلق عند إكمال إجراء تصحيحي
    """

    action_id: UUID = Field(..., description="Corrective action ID")
    non_conformance_id: UUID = Field(..., description="Related NC ID")
    nc_number: str = Field(..., description="NC reference number")

    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    completion_date: datetime = Field(
        default_factory=datetime.utcnow, description="Completion date"
    )
    planned_date: date = Field(..., description="Originally planned date")

    # Status
    completed_on_time: bool = Field(..., description="Completed before due date")
    days_overdue: int | None = Field(None, description="Days overdue (if late)")

    # Evidence
    completion_evidence_photos: list[str] = Field(
        default_factory=list, description="Completion photos"
    )
    completion_evidence_documents: list[str] = Field(
        default_factory=list, description="Completion documents"
    )

    # Verification
    effectiveness_verified: bool = Field(
        default=False, description="Effectiveness verified"
    )
    verification_notes_en: str | None = Field(
        None, description="Verification notes in English"
    )
    verification_notes_ar: str | None = Field(
        None, description="Verification notes in Arabic"
    )

    completed_by: UUID = Field(..., description="User who completed the action")
    verified_by: UUID | None = Field(
        None, description="User who verified effectiveness"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Certificate Events - أحداث الشهادات
# ─────────────────────────────────────────────────────────────────────────────


class CertificateExpiringEvent(BaseEvent):
    """
    Event emitted when a certificate is approaching expiry.
    حدث يُطلق عند اقتراب انتهاء صلاحية شهادة
    """

    certificate_id: UUID = Field(..., description="Certificate ID")
    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    certificate_number: str = Field(..., description="Certificate number")
    certificate_type: str = Field(..., description="Certificate type")

    issue_date: date = Field(..., description="Certificate issue date")
    expiry_date: date = Field(..., description="Certificate expiry date")

    # Expiry details
    days_until_expiry: int = Field(..., description="Days until expiry")
    expiry_urgency: str = Field(
        ..., pattern="^(info|warning|critical)$", description="Urgency level"
    )

    # Renewal information
    renewal_required: bool = Field(default=True, description="Renewal required")
    renewal_window_start: date | None = Field(
        None, description="Renewal window start date"
    )
    renewal_audit_scheduled: bool = Field(
        default=False, description="Renewal audit scheduled"
    )
    renewal_audit_date: date | None = Field(
        None, description="Scheduled renewal audit date"
    )

    # Contact
    certification_body: str = Field(..., description="Certification body")
    cb_contact_email: str | None = Field(None, description="CB contact email")

    # Actions
    action_required_en: str = Field(..., description="Action required in English")
    action_required_ar: str = Field(..., description="Action required in Arabic")


class CertificateIssuedEvent(BaseEvent):
    """
    Event emitted when a new certificate is issued.
    حدث يُطلق عند إصدار شهادة جديدة
    """

    certificate_id: UUID = Field(default_factory=uuid4, description="Certificate ID")
    farm_id: UUID = Field(..., description="Farm registration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    certificate_number: str = Field(..., description="Certificate number")
    certificate_type: str = Field(..., description="Certificate type")

    issue_date: date = Field(..., description="Issue date")
    expiry_date: date = Field(..., description="Expiry date")
    validity_months: int = Field(..., ge=1, description="Validity period in months")

    # Scope
    certification_scope: list[str] = Field(
        default_factory=list, description="Certification scope (FV, CROPS_BASE, etc.)"
    )
    product_types_en: list[str] = Field(
        default_factory=list, description="Certified products (English)"
    )
    product_types_ar: list[str] = Field(
        default_factory=list, description="Certified products (Arabic)"
    )

    # Certification body
    certification_body: str = Field(..., description="Certification body name")
    cb_code: str = Field(..., description="Certification body code")

    # Audit details
    audit_id: UUID | None = Field(None, description="Related audit ID")
    final_compliance_score: float = Field(
        ..., ge=0, le=100, description="Final compliance score"
    )

    # Certificate documents
    certificate_url: str | None = Field(None, description="Certificate PDF URL")
    public_listing: bool = Field(default=True, description="Listed in public database")

    issued_by: UUID | None = Field(
        None, description="User who issued the certificate"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Integration-Specific Events - أحداث خاصة بالتكامل
# ─────────────────────────────────────────────────────────────────────────────


class WaterUsageRecordedEvent(BaseEvent):
    """
    Event emitted when water usage is recorded for GlobalGAP compliance.
    حدث يُطلق عند تسجيل استخدام المياه للامتثال لـ GlobalGAP
    """

    record_id: UUID = Field(default_factory=uuid4, description="Record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    field_id: UUID | None = Field(None, description="Field ID")

    # Water usage
    water_volume_m3: float = Field(
        ..., ge=0, description="Water volume in cubic meters"
    )
    water_source: str = Field(
        ..., description="Water source (well, river, municipal, etc.)"
    )
    water_quality_tested: bool = Field(..., description="Water quality tested")

    # Period
    recording_date: date = Field(..., description="Recording date")
    usage_period_start: date | None = Field(None, description="Usage period start")
    usage_period_end: date | None = Field(None, description="Usage period end")

    # Irrigation details
    irrigation_method: str | None = Field(None, description="Irrigation method")
    irrigation_efficiency: float | None = Field(
        None, ge=0, le=100, description="Efficiency %"
    )

    # Compliance
    spring_water_requirement_met: bool = Field(
        ..., description="SPRING water requirement compliance"
    )
    water_rights_documented: bool = Field(..., description="Water rights documented")

    recorded_by: UUID | None = Field(None, description="User who recorded")


class IPMActivityRecordedEvent(BaseEvent):
    """
    Event emitted when IPM (Integrated Pest Management) activity is recorded.
    حدث يُطلق عند تسجيل نشاط الإدارة المتكاملة للآفات
    """

    record_id: UUID = Field(default_factory=uuid4, description="Record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    field_id: UUID | None = Field(None, description="Field ID")

    activity_date: date = Field(..., description="Activity date")
    activity_type: str = Field(
        ...,
        pattern="^(MONITORING|PREVENTION|CONTROL|TREATMENT)$",
        description="IPM activity type",
    )

    # Pest/Disease information
    pest_or_disease_name_en: str = Field(..., description="Pest/disease name (English)")
    pest_or_disease_name_ar: str | None = Field(
        None, description="Pest/disease name (Arabic)"
    )
    pest_category: str | None = Field(
        None, description="Category (insect, fungal, bacterial, etc.)"
    )

    # Detection
    detection_method: str = Field(
        ..., description="Detection method (AI, manual, trap, etc.)"
    )
    severity_level: str = Field(
        ..., pattern="^(low|medium|high|critical)$", description="Severity level"
    )

    # Treatment (if applicable)
    treatment_applied: bool = Field(default=False, description="Treatment applied")
    ppp_product_name: str | None = Field(
        None, description="Plant Protection Product used"
    )
    ppp_active_ingredient: str | None = Field(None, description="Active ingredient")
    ppp_dosage: str | None = Field(None, description="Dosage applied")
    ppp_compliant: bool | None = Field(None, description="PPP GlobalGAP compliant")

    # Documentation
    justification_en: str = Field(..., description="Treatment justification (English)")
    justification_ar: str | None = Field(
        None, description="Treatment justification (Arabic)"
    )

    recorded_by: UUID | None = Field(None, description="User who recorded")


class FertilizerApplicationRecordedEvent(BaseEvent):
    """
    Event emitted when fertilizer application is recorded for compliance.
    حدث يُطلق عند تسجيل تطبيق الأسمدة للامتثال
    """

    record_id: UUID = Field(default_factory=uuid4, description="Record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    field_id: UUID | None = Field(None, description="Field ID")

    application_date: date = Field(..., description="Application date")

    # Fertilizer details
    fertilizer_name: str = Field(..., description="Fertilizer product name")
    fertilizer_type: str = Field(
        ..., description="Type (organic, inorganic, foliar, etc.)"
    )
    npk_ratio: str | None = Field(None, description="NPK ratio (e.g., 20-20-20)")

    # Quantities
    quantity_applied_kg: float = Field(..., ge=0, description="Quantity in kg")
    application_rate_kg_per_ha: float | None = Field(
        None, ge=0, description="Rate per hectare"
    )
    area_applied_ha: float | None = Field(
        None, ge=0, description="Area applied in hectares"
    )

    # Method
    application_method: str = Field(
        ..., description="Application method (broadcast, banding, foliar, etc.)"
    )

    # Compliance
    based_on_soil_test: bool = Field(..., description="Based on soil test results")
    soil_test_date: date | None = Field(None, description="Soil test date")
    nutrient_plan_followed: bool = Field(
        ..., description="Nutrient management plan followed"
    )
    mrl_compliant: bool | None = Field(None, description="MRL compliance checked")

    # Justification
    application_reason_en: str = Field(..., description="Application reason (English)")
    application_reason_ar: str | None = Field(
        None, description="Application reason (Arabic)"
    )

    recorded_by: UUID | None = Field(None, description="User who recorded")


class TraceabilityRecordCreatedEvent(BaseEvent):
    """
    Event emitted when a traceability record is created.
    حدث يُطلق عند إنشاء سجل تتبع
    """

    record_id: UUID = Field(default_factory=uuid4, description="Traceability record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    field_id: UUID | None = Field(None, description="Field ID")

    # Batch information
    batch_number: str = Field(..., description="Batch/lot number")
    harvest_date: date = Field(..., description="Harvest date")

    # Product
    product_name_en: str = Field(..., description="Product name (English)")
    product_name_ar: str | None = Field(None, description="Product name (Arabic)")
    product_variety: str | None = Field(None, description="Product variety")

    # Quantities
    quantity_kg: float = Field(..., ge=0, description="Quantity in kg")
    quantity_units: int | None = Field(
        None, ge=0, description="Quantity in units (boxes, pallets, etc.)"
    )

    # Traceability
    ggn: str = Field(..., description="GlobalGAP Number")
    planting_date: date | None = Field(None, description="Planting date")

    # Activities tracked
    irrigation_records_linked: int = Field(
        default=0, ge=0, description="Linked irrigation records"
    )
    fertilizer_records_linked: int = Field(
        default=0, ge=0, description="Linked fertilizer records"
    )
    pest_control_records_linked: int = Field(
        default=0, ge=0, description="Linked pest control records"
    )
    harvest_records_linked: int = Field(
        default=0, ge=0, description="Linked harvest records"
    )

    # Compliance
    full_traceability: bool = Field(..., description="Full farm-to-fork traceability")
    withdrawal_period_respected: bool = Field(
        default=True, description="Withdrawal period respected"
    )

    created_by: UUID | None = Field(None, description="User who created record")


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Subject constants
    "GlobalGAPSubjects",
    # Compliance events
    "ComplianceUpdatedEvent",
    "ComplianceRequirementFailedEvent",
    # Audit events
    "AuditScheduledEvent",
    "AuditCompletedEvent",
    # Non-conformance events
    "NonConformanceDetectedEvent",
    "CorrectiveActionCompletedEvent",
    # Certificate events
    "CertificateExpiringEvent",
    "CertificateIssuedEvent",
    # Integration events
    "WaterUsageRecordedEvent",
    "IPMActivityRecordedEvent",
    "FertilizerApplicationRecordedEvent",
    "TraceabilityRecordCreatedEvent",
]
