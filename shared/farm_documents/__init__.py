"""
Farm Document Management Module
وحدة إدارة وثائق المزرعة

A comprehensive module for farm document storage, certification tracking,
compliance management, and document expiry alerts.

وحدة شاملة لتخزين وثائق المزرعة، وتتبع الشهادات،
وإدارة الامتثال، وتنبيهات انتهاء الوثائق.

Features:
- Document storage and categorization (PDF, images, certificates)
- Certification tracking (GlobalGAP, Organic, SFDA, etc.)
- Compliance document management
- Document expiry and renewal alerts
- Document sharing with access control

الميزات:
- تخزين وتصنيف الوثائق (PDF، صور، شهادات)
- تتبع الشهادات (GlobalGAP، عضوي، SFDA، إلخ)
- إدارة وثائق الامتثال
- تنبيهات انتهاء وتجديد الوثائق
- مشاركة الوثائق مع التحكم في الوصول

Example Usage:
--------------

>>> from shared.farm_documents import (
...     DocumentStorageService,
...     ComplianceService,
...     AlertService,
...     DocumentType,
...     CertificationType,
... )

# Upload a document
>>> storage = DocumentStorageService()
>>> doc = await storage.upload_document(
...     file_content=pdf_bytes,
...     filename="soil_analysis_2025.pdf",
...     tenant_id="tenant_001",
...     farm_id="farm_001",
...     document_type=DocumentType.SOIL_TEST,
...     title_en="Soil Analysis Report 2025",
...     title_ar="تقرير تحليل التربة 2025",
...     uploaded_by="user_001",
...     expiry_date=datetime(2026, 1, 15),
... )

# Track certification
>>> compliance = ComplianceService()
>>> cert = await compliance.create_certification(
...     tenant_id="tenant_001",
...     farm_id="farm_001",
...     certification_type=CertificationType.GLOBALGAP,
...     certificate_number="GGN-12345",
...     name_en="GlobalGAP IFA v6",
...     name_ar="GlobalGAP IFA v6",
...     issue_date=date(2025, 1, 1),
...     expiry_date=date(2026, 1, 1),
...     created_by="user_001",
... )

# Check expiry alerts
>>> alerts = AlertService()
>>> expiry_alerts = await alerts.scan_documents_for_expiry(
...     documents=[doc],
...     recipient_user_ids=["user_001"],
... )
"""

# Models - النماذج
# Alerts - التنبيهات
from .alerts import (
    AlertConfig,
    AlertService,
)

# Compliance - الامتثال
from .compliance import (
    ComplianceError,
    ComplianceService,
)
from .models import (
    # Enums
    AlertPriority,
    # Certification Models
    Certification,
    CertificationBody,
    CertificationStatus,
    CertificationSummary,
    CertificationType,
    # Compliance Models
    ComplianceDocument,
    ComplianceRequirement,
    ComplianceStatus,
    ComplianceSummary,
    # Alert Models
    DocumentAlert,
    # Document Models
    DocumentCategory,
    DocumentMetadata,
    DocumentShare,
    DocumentStatus,
    DocumentSummary,
    DocumentType,
    FarmDocument,
    FileFormat,
    SharePermission,
)

# Storage - التخزين
from .storage import (
    DocumentStorageService,
    LocalStorageProvider,
    S3StorageProvider,
    StorageConfig,
    StorageError,
    StorageProvider,
    get_mime_type_for_format,
    is_document_format,
    is_image_format,
)

__all__ = [
    # ─────────────────────────────────────────────────────────────────────────
    # Enums - التعدادات
    # ─────────────────────────────────────────────────────────────────────────
    "AlertPriority",
    "CertificationStatus",
    "CertificationType",
    "ComplianceStatus",
    "DocumentStatus",
    "DocumentType",
    "FileFormat",
    "SharePermission",
    # ─────────────────────────────────────────────────────────────────────────
    # Document Models - نماذج الوثائق
    # ─────────────────────────────────────────────────────────────────────────
    "DocumentCategory",
    "DocumentMetadata",
    "DocumentShare",
    "DocumentSummary",
    "FarmDocument",
    # ─────────────────────────────────────────────────────────────────────────
    # Certification Models - نماذج الشهادات
    # ─────────────────────────────────────────────────────────────────────────
    "Certification",
    "CertificationBody",
    "CertificationSummary",
    # ─────────────────────────────────────────────────────────────────────────
    # Compliance Models - نماذج الامتثال
    # ─────────────────────────────────────────────────────────────────────────
    "ComplianceDocument",
    "ComplianceRequirement",
    "ComplianceSummary",
    # ─────────────────────────────────────────────────────────────────────────
    # Alert Models - نماذج التنبيهات
    # ─────────────────────────────────────────────────────────────────────────
    "DocumentAlert",
    # ─────────────────────────────────────────────────────────────────────────
    # Storage - التخزين
    # ─────────────────────────────────────────────────────────────────────────
    "DocumentStorageService",
    "LocalStorageProvider",
    "S3StorageProvider",
    "StorageConfig",
    "StorageError",
    "StorageProvider",
    "get_mime_type_for_format",
    "is_document_format",
    "is_image_format",
    # ─────────────────────────────────────────────────────────────────────────
    # Compliance - الامتثال
    # ─────────────────────────────────────────────────────────────────────────
    "ComplianceError",
    "ComplianceService",
    # ─────────────────────────────────────────────────────────────────────────
    # Alerts - التنبيهات
    # ─────────────────────────────────────────────────────────────────────────
    "AlertConfig",
    "AlertService",
]

__version__ = "1.0.0"
