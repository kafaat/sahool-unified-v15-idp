"""
GlobalGAP IFA v6 Data Models
نماذج بيانات GlobalGAP IFA v6

Pydantic models for IFA v6 compliance management.
نماذج Pydantic لإدارة الامتثال لـ IFA v6.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationInfo, field_validator

from .constants import (
    GGN_FORMAT_PATTERN,
    AuditType,
    ComplianceLevel,
)

logger = logging.getLogger(__name__)


def _compute_integrity_hash(data: dict) -> str:
    """
    Compute HMAC-SHA256 integrity hash for GlobalGAP compliance records.
    حساب تجزئة HMAC-SHA256 لسجلات الامتثال GlobalGAP

    Uses GLOBALGAP_HMAC_SECRET for keyed hashing so that stored hashes
    cannot be forged without the server-side secret.  Falls back to
    plain SHA-256 when no secret is configured (development only).
    """
    payload = json.dumps(data, sort_keys=True, default=str).encode()
    secret = os.getenv("GLOBALGAP_HMAC_SECRET", "")
    if secret:
        return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "production":
        raise RuntimeError(
            "GLOBALGAP_HMAC_SECRET must be set in production. Cannot fall back to plain SHA-256 for compliance records."
        )
    logger.warning(
        "GLOBALGAP_HMAC_SECRET is not set — falling back to plain SHA-256. "
        "This is acceptable in development but MUST be configured in production."
    )
    return hashlib.sha256(payload).hexdigest()


class ChecklistItem(BaseModel):
    """
    Individual checklist item
    عنصر قائمة التحقق الفردي

    Represents a single control point in the IFA v6 checklist.
    يمثل نقطة تحكم واحدة في قائمة التحقق IFA v6.
    """

    id: str = Field(..., description="Control point number (e.g., AF.1.1.1)")
    category_code: str = Field(..., description="Category code (e.g., FS, ENV, WHS)")
    subcategory: str | None = Field(None, description="Subcategory name")

    title_en: str = Field(..., description="Control point title in English")
    title_ar: str = Field(..., description="Control point title in Arabic")

    description_en: str = Field(..., description="Detailed description in English")
    description_ar: str = Field(..., description="Detailed description in Arabic")

    compliance_level: ComplianceLevel = Field(..., description="Compliance level requirement")

    evidence_required: list[str] = Field(default_factory=list, description="Types of evidence required")

    guidance_en: str | None = Field(None, description="Implementation guidance in English")
    guidance_ar: str | None = Field(None, description="Implementation guidance in Arabic")

    applicable_to: list[str] = Field(
        default_factory=lambda: ["FV"],
        description="Applicable scopes (FV, CROPS_BASE, etc.)",
    )

    not_applicable_allowed: bool = Field(default=False, description="Whether N/A is an acceptable response")

    order: int = Field(..., description="Display order within category")

    model_config = ConfigDict(use_enum_values=True)


class ChecklistCategory(BaseModel):
    """
    Checklist category or module
    فئة أو وحدة قائمة التحقق

    Groups related control points into modules.
    تجميع نقاط التحكم ذات الصلة في وحدات.
    """

    code: str = Field(..., description="Category code (e.g., FS, ENV)")
    name_en: str = Field(..., description="Category name in English")
    name_ar: str = Field(..., description="Category name in Arabic")

    description_en: str = Field(..., description="Category description in English")
    description_ar: str = Field(..., description="Category description in Arabic")

    items: list[ChecklistItem] = Field(default_factory=list, description="Control points in this category")

    order: int = Field(..., description="Display order")

    def get_item_by_id(self, item_id: str) -> ChecklistItem | None:
        """Get a specific item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def count_by_compliance_level(self, level: ComplianceLevel) -> int:
        """Count items by compliance level"""
        return sum(1 for item in self.items if item.compliance_level == level)


class ComplianceRequirement(BaseModel):
    """
    Compliance requirement calculation
    حساب متطلبات الامتثال

    Tracks compliance status for a specific requirement level.
    تتبع حالة الامتثال لمستوى متطلبات محدد.
    """

    compliance_level: ComplianceLevel = Field(..., description="Requirement level")
    total_items: int = Field(..., description="Total applicable items")
    compliant_items: int = Field(default=0, description="Number of compliant items")
    non_compliant_items: int = Field(default=0, description="Number of non-compliant items")
    not_applicable_items: int = Field(default=0, description="Number of N/A items")

    @property
    def compliance_percentage(self) -> float:
        """Calculate compliance percentage"""
        applicable = self.total_items - self.not_applicable_items
        if applicable == 0:
            return 100.0
        return (self.compliant_items / applicable) * 100

    @property
    def meets_threshold(self) -> bool:
        """Check if threshold is met"""
        from .constants import COMPLIANCE_THRESHOLDS

        if self.compliance_level == ComplianceLevel.MAJOR_MUST:
            return self.compliance_percentage >= COMPLIANCE_THRESHOLDS["major_must"]
        elif self.compliance_level == ComplianceLevel.MINOR_MUST:
            return self.compliance_percentage >= COMPLIANCE_THRESHOLDS["minor_must"]
        else:
            return True  # Recommendations always pass

    model_config = ConfigDict(use_enum_values=True)


class AuditFinding(BaseModel):
    """
    Audit finding
    نتيجة التدقيق

    Records findings from an audit against a control point.
    تسجيل النتائج من التدقيق مقابل نقطة تحكم.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Finding ID")
    audit_id: str = Field(..., description="Associated audit ID")
    checklist_item_id: str = Field(..., description="Control point ID")

    is_compliant: bool = Field(..., description="Compliance status")
    is_not_applicable: bool = Field(default=False, description="Not applicable flag")

    evidence_collected: list[str] = Field(default_factory=list, description="Evidence types collected")

    notes_en: str | None = Field(None, description="Auditor notes in English")
    notes_ar: str | None = Field(None, description="Auditor notes in Arabic")

    photos: list[str] = Field(default_factory=list, description="Photo URLs")
    documents: list[str] = Field(default_factory=list, description="Document URLs")

    auditor_id: str = Field(..., description="Auditor ID")
    audit_date: datetime = Field(..., description="Date of finding")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Integrity verification (A-06)
    data_hash: str | None = Field(None, description="HMAC-SHA256 integrity hash")

    model_config = ConfigDict()

    def calculate_data_hash(self) -> str:
        """Calculate HMAC-SHA256 hash of all integrity-relevant fields."""
        hash_data = {
            "id": self.id,
            "audit_id": self.audit_id,
            "checklist_item_id": self.checklist_item_id,
            "is_compliant": self.is_compliant,
            "is_not_applicable": self.is_not_applicable,
            "evidence_collected": self.evidence_collected,
            "notes_en": self.notes_en,
            "notes_ar": self.notes_ar,
            "photos": self.photos,
            "documents": self.documents,
            "auditor_id": self.auditor_id,
            "audit_date": self.audit_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return _compute_integrity_hash(hash_data)

    def seal(self) -> None:
        """Seal the record by computing its integrity hash."""
        self.data_hash = self.calculate_data_hash()

    def verify_integrity(self) -> bool:
        """Verify that the record has not been tampered with."""
        if self.data_hash is None:
            return False
        return hmac.compare_digest(self.data_hash, self.calculate_data_hash())


class NonConformanceSeverity(StrEnum):
    """Non-conformance severity / خطورة عدم المطابقة"""

    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class NonConformance(BaseModel):
    """
    Non-conformance record
    سجل عدم المطابقة

    Documents deviations from requirements.
    توثيق الانحرافات عن المتطلبات.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="NC ID")
    nc_number: str = Field(..., description="NC reference number (e.g., NC-2024-001)")

    audit_id: str = Field(..., description="Associated audit ID")
    finding_id: str = Field(..., description="Associated finding ID")
    checklist_item_id: str = Field(..., description="Control point ID")

    severity: NonConformanceSeverity = Field(..., description="Severity level")

    description_en: str = Field(..., description="NC description in English")
    description_ar: str = Field(..., description="NC description in Arabic")

    root_cause_en: str | None = Field(None, description="Root cause in English")
    root_cause_ar: str | None = Field(None, description="Root cause in Arabic")

    identified_date: datetime = Field(..., description="Date identified")
    due_date: datetime = Field(..., description="Correction due date")

    status: str = Field(default="OPEN", description="NC status (OPEN, CLOSED, VERIFIED)")

    auditor_id: str = Field(..., description="Identifying auditor ID")
    farm_id: str = Field(..., description="Farm/producer ID")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Integrity verification (A-06)
    data_hash: str | None = Field(None, description="HMAC-SHA256 integrity hash")

    model_config = ConfigDict(use_enum_values=True)

    def calculate_data_hash(self) -> str:
        """Calculate HMAC-SHA256 hash of all integrity-relevant fields."""
        hash_data = {
            "id": self.id,
            "nc_number": self.nc_number,
            "audit_id": self.audit_id,
            "finding_id": self.finding_id,
            "checklist_item_id": self.checklist_item_id,
            "severity": self.severity if isinstance(self.severity, str) else self.severity.value,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "root_cause_en": self.root_cause_en,
            "root_cause_ar": self.root_cause_ar,
            "identified_date": self.identified_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "status": self.status,
            "auditor_id": self.auditor_id,
            "farm_id": self.farm_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return _compute_integrity_hash(hash_data)

    def seal(self) -> None:
        """Seal the record by computing its integrity hash."""
        self.data_hash = self.calculate_data_hash()

    def verify_integrity(self) -> bool:
        """Verify that the record has not been tampered with."""
        if self.data_hash is None:
            return False
        return hmac.compare_digest(self.data_hash, self.calculate_data_hash())


class CorrectiveActionStatus(StrEnum):
    """Corrective action status / حالة الإجراء التصحيحي"""

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class CorrectiveAction(BaseModel):
    """
    Corrective action plan
    خطة الإجراء التصحيحي

    Documents corrective actions for non-conformances.
    توثيق الإجراءات التصحيحية لعدم المطابقات.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Action ID")
    non_conformance_id: str = Field(..., description="Associated NC ID")

    action_description_en: str = Field(..., description="Action description in English")
    action_description_ar: str = Field(..., description="Action description in Arabic")

    responsible_person: str = Field(..., description="Person responsible")
    responsible_email: str | None = Field(None, description="Contact email")

    planned_date: date = Field(..., description="Planned completion date")
    actual_date: date | None = Field(None, description="Actual completion date")

    status: CorrectiveActionStatus = Field(default=CorrectiveActionStatus.PLANNED, description="Action status")

    effectiveness_verified: bool = Field(default=False, description="Effectiveness verified")
    verification_date: datetime | None = Field(None, description="Verification date")
    verification_notes_en: str | None = Field(None, description="Verification notes in English")
    verification_notes_ar: str | None = Field(None, description="Verification notes in Arabic")

    evidence_documents: list[str] = Field(default_factory=list, description="Supporting document URLs")
    evidence_photos: list[str] = Field(default_factory=list, description="Supporting photo URLs")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Integrity verification (A-06)
    data_hash: str | None = Field(None, description="HMAC-SHA256 integrity hash")

    model_config = ConfigDict(use_enum_values=True)

    def calculate_data_hash(self) -> str:
        """Calculate HMAC-SHA256 hash of all integrity-relevant fields."""
        hash_data = {
            "id": self.id,
            "non_conformance_id": self.non_conformance_id,
            "action_description_en": self.action_description_en,
            "action_description_ar": self.action_description_ar,
            "responsible_person": self.responsible_person,
            "responsible_email": self.responsible_email,
            "planned_date": self.planned_date.isoformat(),
            "actual_date": self.actual_date.isoformat() if self.actual_date else None,
            "status": self.status if isinstance(self.status, str) else self.status.value,
            "effectiveness_verified": self.effectiveness_verified,
            "verification_date": self.verification_date.isoformat() if self.verification_date else None,
            "verification_notes_en": self.verification_notes_en,
            "verification_notes_ar": self.verification_notes_ar,
            "evidence_documents": list(self.evidence_documents),
            "evidence_photos": list(self.evidence_photos),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return _compute_integrity_hash(hash_data)

    def seal(self) -> None:
        """Seal the record by computing its integrity hash."""
        self.data_hash = self.calculate_data_hash()

    def verify_integrity(self) -> bool:
        """Verify that the record has not been tampered with."""
        if self.data_hash is None:
            return False
        return hmac.compare_digest(self.data_hash, self.calculate_data_hash())


class ProducerProfile(BaseModel):
    """
    Producer/farm operator profile
    ملف المنتج/مشغل المزرعة

    Information about the farm operator or producer.
    معلومات حول مشغل المزرعة أو المنتج.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Producer ID")

    # Basic Information
    name_en: str = Field(..., description="Producer name in English")
    name_ar: str = Field(..., description="Producer name in Arabic")

    legal_name: str = Field(..., description="Legal business name")
    commercial_registration: str | None = Field(None, description="CR number")

    # Contact Information
    email: str = Field(..., description="Contact email")
    phone: str = Field(..., description="Contact phone")
    address_en: str | None = Field(None, description="Address in English")
    address_ar: str | None = Field(None, description="Address in Arabic")

    country_code: str = Field(..., description="Country code (ISO 2-letter)")
    region: str | None = Field(None, description="State/region")
    city: str | None = Field(None, description="City")
    postal_code: str | None = Field(None, description="Postal code")

    # Contact Person
    contact_person_en: str = Field(..., description="Contact person name in English")
    contact_person_ar: str | None = Field(None, description="Contact person name in Arabic")
    contact_position: str | None = Field(None, description="Contact person position")

    # Website and Social
    website: HttpUrl | None = Field(None, description="Website URL")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v.lower()


class FarmRegistration(BaseModel):
    """
    Farm registration and GlobalGAP number
    تسجيل المزرعة ورقم GlobalGAP

    Farm registration details and GGN assignment.
    تفاصيل تسجيل المزرعة وتعيين رقم GGN.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Registration ID")

    # GGN Information
    ggn: str = Field(..., description="GlobalGAP Number (13 digits)")
    producer_id: str = Field(..., description="Associated producer ID")

    # Farm Information
    farm_name_en: str = Field(..., description="Farm name in English")
    farm_name_ar: str = Field(..., description="Farm name in Arabic")

    farm_size_hectares: float = Field(..., description="Total farm size in hectares", gt=0)
    certified_area_hectares: float = Field(..., description="Certified area in hectares", gt=0)

    # Location
    country_code: str = Field(..., description="Country code (ISO 2-letter)")
    region: str = Field(..., description="State/region")
    location_coordinates: dict[str, float] | None = Field(None, description="GPS coordinates {lat, lng}")

    # Certification Scope
    certification_scope: list[str] = Field(
        default_factory=lambda: ["FV"],
        description="Certification scopes (FV, CROPS_BASE, etc.)",
    )

    product_types_en: list[str] = Field(default_factory=list, description="Product types in English")
    product_types_ar: list[str] = Field(default_factory=list, description="Product types in Arabic")

    # Certification Body
    certification_body: str | None = Field(None, description="CB name")
    cb_code: str | None = Field(None, description="CB code")

    # Certificate Information
    certificate_number: str | None = Field(None, description="Certificate number")
    certificate_issue_date: date | None = Field(None, description="Issue date")
    certificate_expiry_date: date | None = Field(None, description="Expiry date")
    certificate_status: str = Field(default="PENDING", description="Status (PENDING, ACTIVE, SUSPENDED, EXPIRED)")

    # Parallel Production/Ownership
    parallel_production: bool = Field(default=False, description="Parallel production with non-certified")
    parallel_ownership: bool = Field(default=False, description="Parallel ownership situations")

    # Registration Dates
    registration_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_audit_date: datetime | None = Field(None, description="Last audit date")
    next_audit_date: datetime | None = Field(None, description="Next audit date")

    # Status
    is_active: bool = Field(default=True, description="Registration active status")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("ggn")
    @classmethod
    def validate_ggn(cls, v: str) -> str:
        """Validate GGN format"""
        import re

        if not re.match(GGN_FORMAT_PATTERN, v):
            raise ValueError("GGN must be 13 digits starting with 40 (e.g., 4000000000000)")
        return v

    @field_validator("certified_area_hectares")
    @classmethod
    def validate_certified_area(cls, v: float, info: ValidationInfo) -> float:
        """Ensure certified area doesn't exceed farm size"""
        if info.data.get("farm_size_hectares") and v > info.data["farm_size_hectares"]:
            raise ValueError("Certified area cannot exceed total farm size")
        return v

    # Integrity verification (A-06)
    data_hash: str | None = Field(None, description="HMAC-SHA256 integrity hash")

    model_config = ConfigDict()

    def calculate_data_hash(self) -> str:
        """Calculate HMAC-SHA256 hash of all integrity-relevant fields."""
        hash_data = {
            "id": self.id,
            "ggn": self.ggn,
            "producer_id": self.producer_id,
            "farm_name_en": self.farm_name_en,
            "farm_name_ar": self.farm_name_ar,
            "farm_size_hectares": self.farm_size_hectares,
            "certified_area_hectares": self.certified_area_hectares,
            "country_code": self.country_code,
            "region": self.region,
            "certification_scope": self.certification_scope,
            "product_types_en": self.product_types_en,
            "product_types_ar": self.product_types_ar,
            "certification_body": self.certification_body,
            "cb_code": self.cb_code,
            "certificate_number": self.certificate_number,
            "certificate_issue_date": self.certificate_issue_date.isoformat() if self.certificate_issue_date else None,
            "certificate_expiry_date": self.certificate_expiry_date.isoformat()
            if self.certificate_expiry_date
            else None,
            "certificate_status": self.certificate_status,
            "parallel_production": self.parallel_production,
            "parallel_ownership": self.parallel_ownership,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
        return _compute_integrity_hash(hash_data)

    def seal(self) -> None:
        """Seal the record by computing its integrity hash."""
        self.data_hash = self.calculate_data_hash()

    def verify_integrity(self) -> bool:
        """Verify that the record has not been tampered with."""
        if self.data_hash is None:
            return False
        return hmac.compare_digest(self.data_hash, self.calculate_data_hash())


class AuditSession(BaseModel):
    """
    Audit session record
    سجل جلسة التدقيق

    Complete audit session with findings and results.
    جلسة تدقيق كاملة مع النتائج والنتائج.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Audit ID")
    audit_number: str = Field(..., description="Audit reference number")

    farm_id: str = Field(..., description="Farm registration ID")
    ggn: str = Field(..., description="GlobalGAP Number")

    audit_type: AuditType = Field(..., description="Type of audit")
    audit_scope: list[str] = Field(default_factory=lambda: ["FV"], description="Audit scope")

    # Audit Team
    lead_auditor_id: str = Field(..., description="Lead auditor ID")
    auditor_ids: list[str] = Field(default_factory=list, description="Team auditor IDs")

    # Certification Body
    certification_body: str = Field(..., description="CB name")
    cb_code: str = Field(..., description="CB code")

    # Dates
    scheduled_date: date = Field(..., description="Scheduled audit date")
    actual_start_date: datetime | None = Field(None, description="Actual start")
    actual_end_date: datetime | None = Field(None, description="Actual end")

    # Status
    status: str = Field(
        default="SCHEDULED",
        description="Status (SCHEDULED, IN_PROGRESS, COMPLETED, REPORT_ISSUED)",
    )

    # Results
    findings: list[AuditFinding] = Field(default_factory=list, description="Audit findings")
    non_conformances: list[NonConformance] = Field(default_factory=list, description="Non-conformances")

    overall_compliance: ComplianceRequirement | None = Field(None, description="Overall compliance result")

    recommendation: str | None = Field(None, description="Audit recommendation (APPROVE, REJECT, CONDITIONAL)")

    # Report
    report_url: str | None = Field(None, description="Audit report URL")
    report_issued_date: datetime | None = Field(None, description="Report issue date")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Integrity verification (A-06)
    data_hash: str | None = Field(None, description="HMAC-SHA256 integrity hash")

    model_config = ConfigDict(use_enum_values=True)

    def calculate_data_hash(self) -> str:
        """Calculate HMAC-SHA256 hash of the full session payload for integrity verification."""
        hash_data = self.model_dump(mode="json", exclude={"data_hash"})
        return _compute_integrity_hash(hash_data)

    def seal(self) -> None:
        """Seal the record by computing its integrity hash."""
        self.data_hash = self.calculate_data_hash()

    def verify_integrity(self) -> bool:
        """Verify that the record has not been tampered with."""
        if self.data_hash is None:
            return False
        return hmac.compare_digest(self.data_hash, self.calculate_data_hash())
