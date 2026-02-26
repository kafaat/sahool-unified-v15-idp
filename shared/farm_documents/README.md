# shared/farm_documents

Farm document management for the SAHOOL platform. Handles document storage, certification
tracking, regulatory compliance management, expiry alerting, and access-controlled sharing.
Supports LocalFS and S3-compatible backends.

## File Structure

```
shared/farm_documents/
├── __init__.py      # Public API exports
├── models.py        # Pydantic models, enums, domain types
├── storage.py       # Document storage service (local / S3)
├── compliance.py    # Compliance requirement tracking and service
└── alerts.py        # Document expiry and renewal alert service
```

## Key Components

### models.py

Pydantic v2 models for all document domain entities.

**Document types (`DocumentType`):**
Covers all farm record categories: CERTIFICATE, LICENSE, PERMIT, AUDIT_REPORT,
INSPECTION_REPORT, COMPLIANCE_CHECKLIST, SOIL_TEST, WATER_TEST, PESTICIDE_RECORD,
FERTILIZER_RECORD, HARVEST_RECORD, LAND_DEED, LEASE_AGREEMENT, INSURANCE_POLICY,
INVOICE, RECEIPT, TRAINING_CERTIFICATE, SAFETY_CERTIFICATE, PHOTO, MAP, PLAN.

**Certification types (`CertificationType`):**
GLOBALGAP, GLOBALGAP_IFA, ORGANIC_USDA, ORGANIC_EU, ORGANIC_LOCAL, HALAL, SASO,
SFDA, ISO_22000, ISO_14001, HACCP, FAIR_TRADE, RAINFOREST_ALLIANCE, UTZ, LOCAL_GAP,
WATER_STEWARDSHIP, CARBON_NEUTRAL.

**Core models:**

| Model | Purpose |
|-------|---------|
| `FarmDocument` | Main document record with metadata, versioning, and expiry tracking |
| `DocumentMetadata` | File-level data: size, format, MIME type, checksum, OCR text |
| `DocumentCategory` | Hierarchical category with retention rules |
| `DocumentShare` | Share record with permissions, time limits, and download cap |
| `Certification` | Farm certification (e.g. GlobalGAP IFA) with GGN validation |
| `CertificationBody` | Issuing authority with accreditation and contact details |
| `ComplianceRequirement` | Regulatory requirement linked to document types |
| `ComplianceDocument` | Link between a document and a compliance requirement |
| `DocumentAlert` | Expiry or missing-document alert with notification tracking |

`FarmDocument` provides computed properties: `is_expired`, `days_until_expiry`.
`Certification` provides: `is_valid`, `days_until_expiry`, `needs_renewal` (within 90 days).
`Certification.ggn` validates GlobalGAP Number format (13 digits, prefix 40).

**Status enumerations:**
- `DocumentStatus`: DRAFT, PENDING_REVIEW, APPROVED, REJECTED, ARCHIVED, EXPIRED
- `CertificationStatus`: PENDING, ACTIVE, SUSPENDED, EXPIRED, REVOKED, RENEWAL_IN_PROGRESS
- `ComplianceStatus`: COMPLIANT, NON_COMPLIANT, PARTIALLY_COMPLIANT, PENDING_REVIEW, NOT_APPLICABLE
- `AlertPriority`: CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
- `SharePermission`: VIEW, DOWNLOAD, EDIT, FULL_ACCESS

**Summary models:** `DocumentSummary`, `CertificationSummary`, `ComplianceSummary` provide
aggregated stats for dashboard display.

### storage.py

Document storage with pluggable backends.

| Class | Description |
|-------|-------------|
| `StorageProvider` | Abstract base class |
| `LocalStorageProvider` | Local filesystem storage |
| `S3StorageProvider` | MinIO/S3-compatible object storage |
| `StorageConfig` | Backend selection, base path, bucket, presigned URL TTL |
| `DocumentStorageService` | High-level service: upload, retrieve, delete, list |

Helper functions: `get_mime_type_for_format()`, `is_document_format()`, `is_image_format()`.

### compliance.py

Compliance requirement tracking and assessment.

| Class | Description |
|-------|-------------|
| `ComplianceService` | Manages certifications and compliance documents |

Key methods: `create_certification()`, `update_certification_status()`,
`create_compliance_document()`, `get_compliance_summary()`.

### alerts.py

Proactive document expiry scanning and alert generation.

| Class | Description |
|-------|-------------|
| `AlertConfig` | Expiry warning thresholds (default: 90/60/30/7 days) |
| `AlertService` | Scans documents/certifications and generates `DocumentAlert` records |

Key methods: `scan_documents_for_expiry()`, `scan_certifications_for_expiry()`,
`create_missing_document_alert()`.

## Usage Example

```python
from datetime import date, datetime
from shared.farm_documents import (
    DocumentStorageService,
    ComplianceService,
    AlertService,
    AlertConfig,
    DocumentType,
    CertificationType,
    StorageConfig,
)

# Initialize services
storage = DocumentStorageService(StorageConfig(provider="local"))
compliance = ComplianceService()
alerts = AlertService(AlertConfig(warning_days=[90, 30, 7]))

# Upload a document
with open("soil_report.pdf", "rb") as f:
    doc = await storage.upload_document(
        file_content=f.read(),
        filename="soil_report.pdf",
        tenant_id="tenant_001",
        farm_id="farm_001",
        document_type=DocumentType.SOIL_TEST,
        title_en="Soil Analysis Report 2025",
        title_ar="تقرير تحليل التربة 2025",
        uploaded_by="user_001",
        expiry_date=date(2026, 6, 1),
    )

# Track a GlobalGAP certification
cert = await compliance.create_certification(
    tenant_id="tenant_001",
    farm_id="farm_001",
    certification_type=CertificationType.GLOBALGAP,
    certificate_number="GGN-4012345678901",
    name_en="GlobalGAP IFA v6",
    name_ar="GlobalGAP IFA الإصدار السادس",
    issue_date=date(2025, 1, 1),
    expiry_date=date(2026, 1, 1),
    created_by="user_001",
)

# Check if renewal is needed
if cert.needs_renewal:
    print(f"Renewal due in {cert.days_until_expiry} days")

# Scan for expiry alerts
alert_list = await alerts.scan_certifications_for_expiry(
    certifications=[cert],
    recipient_user_ids=["user_001", "manager_002"],
)
for alert in alert_list:
    print(f"[{alert.priority}] {alert.title_en}")
```

## Supported File Formats

PDF, PNG, JPG, JPEG, WEBP, TIFF, DOC, DOCX, XLS, XLSX
