# GlobalGAP IFA v6 Compliance Module

> وحدة الامتثال لمعايير GlobalGAP IFA v6 | GlobalGAP IFA v6 Compliance Module

Comprehensive GlobalGAP IFA (Integrated Farm Assurance) v6 compliance management for Fruit & Vegetables certification. Provides checklist management, audit tracking, compliance scoring, and Supply Chain Portal API integration.

**Version**: 6.0.0

## Features

- **IFA v6 Checklist**: Full compliance checklist with Major Must, Minor Must, and Recommendation levels
- **Compliance Scoring**: Automated score calculation against GlobalGAP thresholds
- **GGN Validation**: GlobalGAP Number format validation
- **Audit Management**: Non-conformance tracking with corrective actions
- **API Client**: Supply Chain Portal API integration for certificate verification
- **Bilingual**: Full Arabic/English support for all checklist items

## Module Structure

```
shared/globalgap/
├── __init__.py                    # Module exports (v6.0.0)
├── models.py                      # Pydantic data models (ChecklistItem, AuditFinding, etc.)
├── constants.py                   # IFA v6 constants and thresholds
├── validators.py                  # GGN validation, compliance checks
├── ifa_v6_checklist.py           # Complete IFA v6 checklist definitions
├── api_client.py                  # GlobalGAP Supply Chain Portal API client
├── api_client_examples.py         # API client usage examples
├── addons/                        # Additional compliance modules
├── integrations/                  # External system integrations
├── API_CLIENT_README.md           # API client detailed documentation
└── IFA_V6_CHECKLIST_README.md     # Checklist detailed documentation
```

## Usage

```python
from shared.globalgap import (
    # Constants
    IFA_VERSION,              # "6.0"
    COMPLIANCE_THRESHOLDS,    # Major Must: 100%, Minor Must: 95%
    CERTIFICATE_VALIDITY_DAYS,

    # Models
    ChecklistItem,
    ChecklistCategory,
    AuditFinding,
    NonConformance,

    # Validators
    validate_ggn_number,
    check_major_must_compliance,

    # Checklist
    IFA_V6_CHECKLIST,
    calculate_compliance_score,

    # API Client
    GlobalGAPClient,
    CertificateInfo,
    CertificateStatus,
    Producer,
)
```

## Compliance Thresholds

| Level | Threshold | Description |
|-------|-----------|-------------|
| Major Must | 100% | All Major Must items must be compliant |
| Minor Must | 95% | At least 95% of Minor Must items |
| Recommendation | N/A | Not scored, advisory only |

## Checklist Item Model

```python
class ChecklistItem(BaseModel):
    id: str                    # Control point number (e.g., "CB.1.1")
    category_code: str         # Category code
    subcategory: str           # Subcategory
    title_en: str              # English title
    title_ar: str              # Arabic title
    description_en: str        # English description
    description_ar: str        # Arabic description
    compliance_level: str      # "major_must" | "minor_must" | "recommendation"
    evidence_required: list    # Required evidence types
    guidance_en: str           # English guidance
    guidance_ar: str           # Arabic guidance
```

## API Client

The `GlobalGAPClient` connects to GlobalGAP's Supply Chain Portal for certificate verification:

```python
client = GlobalGAPClient(api_key="your-key")
cert = await client.verify_certificate(ggn="4049929000001")
print(cert.status)  # CertificateStatus.VALID
```

See [API_CLIENT_README.md](./API_CLIENT_README.md) for detailed API documentation.

## Related

- [GlobalGAP Compliance Service](../../apps/services/globalgap-compliance/) — Microservice implementation
- [Farm Documents](../farm_documents/) — Farm documentation & compliance alerts
- [Traceability](../traceability/) — Supply chain traceability & QR codes
