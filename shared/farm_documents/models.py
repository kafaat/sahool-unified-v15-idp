"""
Farm Document Management Models
نماذج إدارة وثائق المزرعة

Pydantic models for farm document storage, certification tracking,
and compliance document management.

نماذج Pydantic لتخزين وثائق المزرعة، وتتبع الشهادات،
وإدارة وثائق الامتثال.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ─────────────────────────────────────────────────────────────────────────────
# Enums - التعدادات
# ─────────────────────────────────────────────────────────────────────────────


class DocumentType(StrEnum):
    """Document type enumeration - تعداد أنواع الوثائق"""

    # Certifications - الشهادات
    CERTIFICATE = "certificate"  # شهادة
    LICENSE = "license"  # رخصة
    PERMIT = "permit"  # تصريح

    # Compliance - الامتثال
    AUDIT_REPORT = "audit_report"  # تقرير التدقيق
    INSPECTION_REPORT = "inspection_report"  # تقرير التفتيش
    COMPLIANCE_CHECKLIST = "compliance_checklist"  # قائمة التحقق من الامتثال

    # Farm Records - سجلات المزرعة
    SOIL_TEST = "soil_test"  # اختبار التربة
    WATER_TEST = "water_test"  # اختبار المياه
    PESTICIDE_RECORD = "pesticide_record"  # سجل المبيدات
    FERTILIZER_RECORD = "fertilizer_record"  # سجل الأسمدة
    HARVEST_RECORD = "harvest_record"  # سجل الحصاد

    # Legal Documents - الوثائق القانونية
    LAND_DEED = "land_deed"  # سند الملكية
    LEASE_AGREEMENT = "lease_agreement"  # عقد الإيجار
    INSURANCE_POLICY = "insurance_policy"  # وثيقة التأمين
    CONTRACT = "contract"  # عقد

    # Financial - المالية
    INVOICE = "invoice"  # فاتورة
    RECEIPT = "receipt"  # إيصال
    PAYMENT_PROOF = "payment_proof"  # إثبات الدفع

    # Training - التدريب
    TRAINING_CERTIFICATE = "training_certificate"  # شهادة تدريب
    SAFETY_CERTIFICATE = "safety_certificate"  # شهادة السلامة

    # Other - أخرى
    PHOTO = "photo"  # صورة
    MAP = "map"  # خريطة
    PLAN = "plan"  # خطة
    REPORT = "report"  # تقرير
    OTHER = "other"  # أخرى


class CertificationType(StrEnum):
    """Certification type enumeration - تعداد أنواع الشهادات"""

    GLOBALGAP = "globalgap"  # GlobalGAP
    GLOBALGAP_IFA = "globalgap_ifa"  # GlobalGAP IFA
    ORGANIC_USDA = "organic_usda"  # عضوي USDA
    ORGANIC_EU = "organic_eu"  # عضوي EU
    ORGANIC_LOCAL = "organic_local"  # عضوي محلي
    HALAL = "halal"  # حلال
    SASO = "saso"  # هيئة المواصفات السعودية
    SFDA = "sfda"  # الهيئة العامة للغذاء والدواء
    ISO_22000 = "iso_22000"  # ISO 22000
    ISO_14001 = "iso_14001"  # ISO 14001
    HACCP = "haccp"  # HACCP
    FAIR_TRADE = "fair_trade"  # التجارة العادلة
    RAINFOREST_ALLIANCE = "rainforest_alliance"  # تحالف الغابات المطيرة
    UTZ = "utz"  # UTZ
    LOCAL_GAP = "local_gap"  # الممارسات الزراعية المحلية
    GOOD_AGRICULTURAL_PRACTICES = "gap"  # الممارسات الزراعية الجيدة
    WATER_STEWARDSHIP = "water_stewardship"  # إدارة المياه
    CARBON_NEUTRAL = "carbon_neutral"  # محايد للكربون
    OTHER = "other"  # أخرى


class CertificationStatus(StrEnum):
    """Certification status - حالة الشهادة"""

    PENDING = "pending"  # قيد الانتظار
    ACTIVE = "active"  # نشط
    SUSPENDED = "suspended"  # معلق
    EXPIRED = "expired"  # منتهي
    REVOKED = "revoked"  # ملغى
    RENEWAL_IN_PROGRESS = "renewal_in_progress"  # التجديد قيد التقدم


class DocumentStatus(StrEnum):
    """Document status - حالة الوثيقة"""

    DRAFT = "draft"  # مسودة
    PENDING_REVIEW = "pending_review"  # في انتظار المراجعة
    APPROVED = "approved"  # معتمد
    REJECTED = "rejected"  # مرفوض
    ARCHIVED = "archived"  # مؤرشف
    EXPIRED = "expired"  # منتهي


class ComplianceStatus(StrEnum):
    """Compliance document status - حالة وثيقة الامتثال"""

    COMPLIANT = "compliant"  # متوافق
    NON_COMPLIANT = "non_compliant"  # غير متوافق
    PARTIALLY_COMPLIANT = "partially_compliant"  # متوافق جزئياً
    PENDING_REVIEW = "pending_review"  # في انتظار المراجعة
    NOT_APPLICABLE = "not_applicable"  # غير قابل للتطبيق


class AlertPriority(StrEnum):
    """Alert priority levels - مستويات أولوية التنبيه"""

    CRITICAL = "critical"  # حرج
    HIGH = "high"  # عالي
    MEDIUM = "medium"  # متوسط
    LOW = "low"  # منخفض
    INFORMATIONAL = "informational"  # معلوماتي


class SharePermission(StrEnum):
    """Document share permissions - صلاحيات مشاركة الوثيقة"""

    VIEW = "view"  # عرض فقط
    DOWNLOAD = "download"  # تحميل
    EDIT = "edit"  # تعديل
    FULL_ACCESS = "full_access"  # وصول كامل


class FileFormat(StrEnum):
    """Supported file formats - تنسيقات الملفات المدعومة"""

    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    WEBP = "webp"
    TIFF = "tiff"
    DOC = "doc"
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"


# ─────────────────────────────────────────────────────────────────────────────
# Category Models - نماذج الفئات
# ─────────────────────────────────────────────────────────────────────────────


class DocumentCategory(BaseModel):
    """
    Document category for organization
    فئة الوثائق للتنظيم
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Category ID")
    code: str = Field(..., description="Category code (e.g., CERT, COMP, FARM)")

    name_en: str = Field(..., description="Category name in English")
    name_ar: str = Field(..., description="Category name in Arabic")

    description_en: str | None = Field(None, description="Description in English")
    description_ar: str | None = Field(None, description="Description in Arabic")

    parent_category_id: str | None = Field(None, description="Parent category ID")

    icon: str | None = Field(None, description="Icon name or URL")
    color: str | None = Field(None, description="Category color (hex)")

    document_types: list[DocumentType] = Field(
        default_factory=list, description="Allowed document types in this category"
    )

    retention_days: int | None = Field(None, description="Default document retention period in days")

    requires_expiry: bool = Field(default=False, description="Documents in this category require expiry date")

    is_active: bool = Field(default=True, description="Category active status")
    order: int = Field(default=0, description="Display order")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ─────────────────────────────────────────────────────────────────────────────
# Document Models - نماذج الوثائق
# ─────────────────────────────────────────────────────────────────────────────


class DocumentMetadata(BaseModel):
    """
    Document metadata
    البيانات الوصفية للوثيقة
    """

    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    file_format: FileFormat = Field(..., description="File format")
    mime_type: str = Field(..., description="MIME type")

    # Dimensions for images
    width: int | None = Field(None, description="Image width in pixels")
    height: int | None = Field(None, description="Image height in pixels")

    # PDF specific
    page_count: int | None = Field(None, description="Number of pages (PDF)")

    # Checksums
    md5_hash: str | None = Field(None, description="MD5 checksum")
    sha256_hash: str | None = Field(None, description="SHA256 checksum")

    # Processing
    ocr_processed: bool = Field(default=False, description="OCR processing completed")
    ocr_text: str | None = Field(None, description="Extracted OCR text")

    # Storage
    storage_path: str = Field(..., description="Storage path or URL")
    storage_provider: str = Field(default="local", description="Storage provider (local, s3, azure)")
    thumbnail_path: str | None = Field(None, description="Thumbnail path or URL")


class FarmDocument(BaseModel):
    """
    Farm document model
    نموذج وثيقة المزرعة

    Represents a document stored for a farm.
    يمثل وثيقة مخزنة للمزرعة.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Document ID")

    # Ownership
    tenant_id: str = Field(..., description="Tenant ID")
    farm_id: str = Field(..., description="Farm ID")
    field_id: str | None = Field(None, description="Associated field ID (optional)")

    # Document info
    document_type: DocumentType = Field(..., description="Document type")
    category_id: str | None = Field(None, description="Category ID")

    # Titles and descriptions
    title_en: str = Field(..., description="Document title in English")
    title_ar: str = Field(..., description="Document title in Arabic")

    description_en: str | None = Field(None, description="Description in English")
    description_ar: str | None = Field(None, description="Description in Arabic")

    # File metadata
    metadata: DocumentMetadata = Field(..., description="File metadata")

    # Status
    status: DocumentStatus = Field(default=DocumentStatus.APPROVED, description="Document status")

    # Dates
    document_date: date | None = Field(None, description="Date of the document (e.g., report date)")
    issue_date: date | None = Field(None, description="Document issue date")
    expiry_date: date | None = Field(None, description="Document expiry date")

    # References
    reference_number: str | None = Field(None, description="External reference number")
    related_document_ids: list[str] = Field(default_factory=list, description="Related document IDs")

    # Tags
    tags: list[str] = Field(default_factory=list, description="Document tags")
    tags_ar: list[str] = Field(default_factory=list, description="Document tags in Arabic")

    # Version control
    version: int = Field(default=1, description="Document version")
    previous_version_id: str | None = Field(None, description="Previous version ID")

    # Access control
    is_confidential: bool = Field(default=False, description="Confidential document")
    access_level: str = Field(default="farm", description="Access level (farm, tenant, public)")

    # Audit
    uploaded_by: str = Field(..., description="User ID who uploaded")
    approved_by: str | None = Field(None, description="User ID who approved")
    approved_at: datetime | None = Field(None, description="Approval timestamp")

    # Notes
    notes_en: str | None = Field(None, description="Internal notes in English")
    notes_ar: str | None = Field(None, description="Internal notes in Arabic")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_expired(self) -> bool:
        """Check if document is expired"""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date

    @property
    def days_until_expiry(self) -> int | None:
        """Calculate days until expiry"""
        if self.expiry_date is None:
            return None
        delta = self.expiry_date - date.today()
        return delta.days

    model_config = ConfigDict()


# ─────────────────────────────────────────────────────────────────────────────
# Certification Models - نماذج الشهادات
# ─────────────────────────────────────────────────────────────────────────────


class CertificationBody(BaseModel):
    """
    Certification body / issuing authority
    جهة منح الشهادات / السلطة المصدرة
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="CB ID")

    name_en: str = Field(..., description="Name in English")
    name_ar: str = Field(..., description="Name in Arabic")

    code: str | None = Field(None, description="CB code")
    accreditation_number: str | None = Field(None, description="Accreditation number")

    # Contact
    website: str | None = Field(None, description="Website URL")
    email: str | None = Field(None, description="Contact email")
    phone: str | None = Field(None, description="Contact phone")

    # Address
    address_en: str | None = Field(None, description="Address in English")
    address_ar: str | None = Field(None, description="Address in Arabic")
    country_code: str | None = Field(None, description="Country code")

    # Certification types offered
    certification_types: list[CertificationType] = Field(
        default_factory=list, description="Types of certifications offered"
    )

    is_active: bool = Field(default=True, description="Active status")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Certification(BaseModel):
    """
    Farm certification record
    سجل شهادة المزرعة

    Tracks certifications like GlobalGAP, Organic, etc.
    يتتبع الشهادات مثل GlobalGAP، العضوي، إلخ.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Certification ID")

    # Ownership
    tenant_id: str = Field(..., description="Tenant ID")
    farm_id: str = Field(..., description="Farm ID")

    # Certification info
    certification_type: CertificationType = Field(..., description="Certification type")
    certificate_number: str = Field(..., description="Certificate number")

    # Names
    name_en: str = Field(..., description="Certification name in English")
    name_ar: str = Field(..., description="Certification name in Arabic")

    # Certification body
    certification_body_id: str | None = Field(None, description="Certification body ID")
    certification_body_name_en: str | None = Field(None, description="CB name in English")
    certification_body_name_ar: str | None = Field(None, description="CB name in Arabic")

    # Scope
    scope_en: str | None = Field(None, description="Certification scope in English")
    scope_ar: str | None = Field(None, description="Certification scope in Arabic")
    products_covered: list[str] = Field(default_factory=list, description="Products covered by certification")
    certified_area_hectares: float | None = Field(None, description="Certified area in hectares")

    # Dates
    issue_date: date = Field(..., description="Certificate issue date")
    expiry_date: date = Field(..., description="Certificate expiry date")
    last_audit_date: date | None = Field(None, description="Last audit date")
    next_audit_date: date | None = Field(None, description="Next scheduled audit")

    # Status
    status: CertificationStatus = Field(default=CertificationStatus.PENDING, description="Certification status")

    # Documents
    certificate_document_id: str | None = Field(None, description="Certificate document ID")
    audit_report_document_ids: list[str] = Field(default_factory=list, description="Audit report document IDs")

    # Verification
    verification_url: str | None = Field(None, description="URL to verify certificate online")
    ggn: str | None = Field(None, description="GlobalGAP Number (if applicable)")

    # Notes
    notes_en: str | None = Field(None, description="Notes in English")
    notes_ar: str | None = Field(None, description="Notes in Arabic")

    # Audit
    created_by: str = Field(..., description="User ID who created")
    updated_by: str | None = Field(None, description="User ID who last updated")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("ggn")
    @classmethod
    def validate_ggn(cls, v: str | None) -> str | None:
        """Validate GlobalGAP Number format"""
        if v is None:
            return v
        import re

        if not re.match(r"^40\d{11}$", v):
            raise ValueError("GGN must be 13 digits starting with 40")
        return v

    @property
    def is_valid(self) -> bool:
        """Check if certification is currently valid"""
        if self.status != CertificationStatus.ACTIVE:
            return False
        return date.today() <= self.expiry_date

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until expiry"""
        delta = self.expiry_date - date.today()
        return delta.days

    @property
    def needs_renewal(self) -> bool:
        """Check if certification needs renewal (within 90 days)"""
        return self.days_until_expiry <= 90

    model_config = ConfigDict()


# ─────────────────────────────────────────────────────────────────────────────
# Compliance Models - نماذج الامتثال
# ─────────────────────────────────────────────────────────────────────────────


class ComplianceRequirement(BaseModel):
    """
    Compliance requirement definition
    تعريف متطلبات الامتثال
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Requirement ID")

    code: str = Field(..., description="Requirement code")
    category: str = Field(..., description="Category (e.g., FOOD_SAFETY, ENVIRONMENT)")

    title_en: str = Field(..., description="Title in English")
    title_ar: str = Field(..., description="Title in Arabic")

    description_en: str = Field(..., description="Description in English")
    description_ar: str = Field(..., description="Description in Arabic")

    # Related certification
    certification_type: CertificationType | None = Field(None, description="Related certification type")

    # Document requirements
    required_documents: list[DocumentType] = Field(default_factory=list, description="Required document types")
    document_renewal_days: int | None = Field(None, description="Document validity period in days")

    # Compliance criteria
    is_mandatory: bool = Field(default=True, description="Mandatory requirement")
    compliance_level: str = Field(
        default="MAJOR_MUST", description="Compliance level (MAJOR_MUST, MINOR_MUST, RECOMMENDED)"
    )

    # Guidance
    guidance_en: str | None = Field(None, description="Guidance notes in English")
    guidance_ar: str | None = Field(None, description="Guidance notes in Arabic")

    # References
    regulatory_reference: str | None = Field(None, description="Regulatory reference (law, standard)")

    is_active: bool = Field(default=True, description="Active status")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ComplianceDocument(BaseModel):
    """
    Compliance document tracking
    تتبع وثائق الامتثال

    Links documents to compliance requirements.
    يربط الوثائق بمتطلبات الامتثال.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Compliance doc ID")

    # Ownership
    tenant_id: str = Field(..., description="Tenant ID")
    farm_id: str = Field(..., description="Farm ID")

    # Links
    requirement_id: str = Field(..., description="Compliance requirement ID")
    document_id: str = Field(..., description="Farm document ID")
    certification_id: str | None = Field(None, description="Related certification ID")

    # Status
    status: ComplianceStatus = Field(default=ComplianceStatus.PENDING_REVIEW, description="Compliance status")

    # Review
    reviewed_by: str | None = Field(None, description="Reviewer user ID")
    reviewed_at: datetime | None = Field(None, description="Review timestamp")
    review_notes_en: str | None = Field(None, description="Review notes in English")
    review_notes_ar: str | None = Field(None, description="Review notes in Arabic")

    # Validity
    valid_from: date | None = Field(None, description="Document validity start")
    valid_until: date | None = Field(None, description="Document validity end")

    # Non-conformance
    non_conformance_id: str | None = Field(None, description="Related NC ID if applicable")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_valid(self) -> bool:
        """Check if compliance document is currently valid"""
        if self.status != ComplianceStatus.COMPLIANT:
            return False
        if self.valid_until is None:
            return True
        return date.today() <= self.valid_until

    model_config = ConfigDict()


# ─────────────────────────────────────────────────────────────────────────────
# Alert Models - نماذج التنبيهات
# ─────────────────────────────────────────────────────────────────────────────


class DocumentAlert(BaseModel):
    """
    Document expiry or renewal alert
    تنبيه انتهاء أو تجديد الوثيقة
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Alert ID")

    # Ownership
    tenant_id: str = Field(..., description="Tenant ID")
    farm_id: str = Field(..., description="Farm ID")

    # Related entities
    document_id: str | None = Field(None, description="Related document ID")
    certification_id: str | None = Field(None, description="Related certification ID")
    compliance_document_id: str | None = Field(None, description="Related compliance document ID")

    # Alert info
    alert_type: str = Field(..., description="Alert type (EXPIRY, RENEWAL, MISSING, COMPLIANCE)")
    priority: AlertPriority = Field(default=AlertPriority.MEDIUM, description="Alert priority")

    # Messages
    title_en: str = Field(..., description="Alert title in English")
    title_ar: str = Field(..., description="Alert title in Arabic")

    message_en: str = Field(..., description="Alert message in English")
    message_ar: str = Field(..., description="Alert message in Arabic")

    # Action required
    action_required_en: str | None = Field(None, description="Required action in English")
    action_required_ar: str | None = Field(None, description="Required action in Arabic")
    action_due_date: date | None = Field(None, description="Action due date")

    # Status
    is_read: bool = Field(default=False, description="Alert read status")
    is_acknowledged: bool = Field(default=False, description="Alert acknowledged")
    acknowledged_by: str | None = Field(None, description="Acknowledger user ID")
    acknowledged_at: datetime | None = Field(None, description="Acknowledgement time")

    is_resolved: bool = Field(default=False, description="Alert resolved")
    resolved_by: str | None = Field(None, description="Resolver user ID")
    resolved_at: datetime | None = Field(None, description="Resolution time")
    resolution_notes: str | None = Field(None, description="Resolution notes")

    # Notification
    notification_sent: bool = Field(default=False, description="Notification sent")
    notification_sent_at: datetime | None = Field(None, description="Notification timestamp")
    notification_channels: list[str] = Field(default_factory=list, description="Channels used (email, sms, push)")

    # Recipients
    recipient_user_ids: list[str] = Field(default_factory=list, description="User IDs to notify")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict()


# ─────────────────────────────────────────────────────────────────────────────
# Sharing Models - نماذج المشاركة
# ─────────────────────────────────────────────────────────────────────────────


class DocumentShare(BaseModel):
    """
    Document sharing record
    سجل مشاركة الوثيقة

    Tracks document sharing with external parties or internal users.
    يتتبع مشاركة الوثائق مع الأطراف الخارجية أو المستخدمين الداخليين.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Share ID")

    # Document
    document_id: str = Field(..., description="Document ID being shared")

    # Sharing info
    shared_by: str = Field(..., description="User ID who shared")
    shared_with_user_id: str | None = Field(None, description="Internal user ID (if internal)")
    shared_with_email: str | None = Field(None, description="External email (if external)")
    shared_with_name: str | None = Field(None, description="Recipient name")

    # Permissions
    permission: SharePermission = Field(default=SharePermission.VIEW, description="Share permission level")

    # Access control
    access_token: str | None = Field(None, description="Secure access token")
    access_url: str | None = Field(None, description="Shareable URL")
    password_protected: bool = Field(default=False, description="Password protected")

    # Validity
    valid_from: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Share start time")
    valid_until: datetime | None = Field(None, description="Share expiry time")
    max_downloads: int | None = Field(None, description="Maximum download count")
    download_count: int = Field(default=0, description="Current download count")

    # Purpose
    purpose_en: str | None = Field(None, description="Sharing purpose in English")
    purpose_ar: str | None = Field(None, description="Sharing purpose in Arabic")

    # Status
    is_active: bool = Field(default=True, description="Share is active")
    revoked: bool = Field(default=False, description="Share has been revoked")
    revoked_by: str | None = Field(None, description="User who revoked")
    revoked_at: datetime | None = Field(None, description="Revocation time")

    # Audit
    last_accessed_at: datetime | None = Field(None, description="Last access time")
    access_log: list[dict] = Field(default_factory=list, description="Access log entries")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_valid(self) -> bool:
        """Check if share is currently valid"""
        if not self.is_active or self.revoked:
            return False
        now = datetime.now(UTC)
        if now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_downloads and self.download_count >= self.max_downloads:
            return False
        return True

    model_config = ConfigDict()


# ─────────────────────────────────────────────────────────────────────────────
# Summary/Report Models - نماذج الملخصات/التقارير
# ─────────────────────────────────────────────────────────────────────────────


class DocumentSummary(BaseModel):
    """
    Document summary for quick overview
    ملخص الوثيقة للعرض السريع
    """

    total_documents: int = Field(default=0, description="Total documents")
    by_type: dict[str, int] = Field(default_factory=dict, description="Count by document type")
    by_status: dict[str, int] = Field(default_factory=dict, description="Count by status")
    by_category: dict[str, int] = Field(default_factory=dict, description="Count by category")

    expiring_soon: int = Field(default=0, description="Documents expiring in 30 days")
    expired: int = Field(default=0, description="Expired documents")

    storage_used_bytes: int = Field(default=0, description="Total storage used")

    last_upload_at: datetime | None = Field(None, description="Last upload timestamp")


class CertificationSummary(BaseModel):
    """
    Certification summary for farm
    ملخص الشهادات للمزرعة
    """

    total_certifications: int = Field(default=0, description="Total certifications")
    active_certifications: int = Field(default=0, description="Active certifications")
    expired_certifications: int = Field(default=0, description="Expired certifications")
    pending_certifications: int = Field(default=0, description="Pending certifications")

    by_type: dict[str, int] = Field(default_factory=dict, description="Count by certification type")

    expiring_soon: list[dict] = Field(default_factory=list, description="Certifications expiring in 90 days")

    next_audit_date: date | None = Field(None, description="Next scheduled audit")

    compliance_score: float | None = Field(None, description="Overall compliance score (0-100)")


class ComplianceSummary(BaseModel):
    """
    Compliance summary for farm
    ملخص الامتثال للمزرعة
    """

    total_requirements: int = Field(default=0, description="Total requirements")
    compliant: int = Field(default=0, description="Compliant requirements")
    non_compliant: int = Field(default=0, description="Non-compliant requirements")
    partially_compliant: int = Field(default=0, description="Partially compliant requirements")
    pending_review: int = Field(default=0, description="Pending review")

    compliance_percentage: float = Field(default=0.0, description="Overall compliance percentage")

    by_category: dict[str, dict] = Field(default_factory=dict, description="Compliance by category")

    missing_documents: list[dict] = Field(default_factory=list, description="Missing required documents")

    upcoming_renewals: list[dict] = Field(default_factory=list, description="Documents needing renewal")
