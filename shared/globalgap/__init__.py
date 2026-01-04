"""
GlobalGAP IFA v6 Module
وحدة GlobalGAP IFA v6

Integrated Farm Assurance (IFA) v6 compliance management
for Fruit & Vegetables certification.

إدارة الامتثال للضمان الزراعي المتكامل (IFA) الإصدار 6
لشهادة الفواكه والخضروات.

Also includes GlobalGAP Supply Chain Portal API client
for certificate verification and producer search.

يتضمن أيضاً عميل واجهة برمجة بوابة سلسلة التوريد GlobalGAP
للتحقق من الشهادات والبحث عن المنتجين.
"""

# GlobalGAP Supply Chain Portal API Client
# عميل واجهة برمجة بوابة سلسلة التوريد GlobalGAP
from .api_client import (
    AuthenticationError,
    CertificateInfo,
    CertificateNotFound,
    CertificateStatus,
    GlobalGAPAPIError,
    GlobalGAPClient,
    InvalidGGN,
    Producer,
    RateLimiter,
    RateLimitExceeded,
)
from .constants import (
    AUDIT_TYPES,
    CERTIFICATE_VALIDITY_DAYS,
    CERTIFICATION_SCOPES,
    COMPLIANCE_LEVELS,
    COMPLIANCE_THRESHOLDS,
    GGN_FORMAT_PATTERN,
    IFA_VERSION,
)
from .ifa_v6_checklist import (
    IFA_V6_CHECKLIST,
    calculate_compliance_score,
    get_category,
    get_checklist_item,
    get_items_by_compliance_level,
)
from .models import (
    AuditFinding,
    AuditType,
    ChecklistCategory,
    ChecklistItem,
    ComplianceLevel,
    ComplianceRequirement,
    CorrectiveAction,
    FarmRegistration,
    NonConformance,
    ProducerProfile,
)
from .validators import (
    check_major_must_compliance,
    validate_certificate_validity,
    validate_compliance_percentage,
    validate_farm_registration,
    validate_ggn_number,
)

__all__ = [
    # Constants
    "IFA_VERSION",
    "COMPLIANCE_THRESHOLDS",
    "CERTIFICATE_VALIDITY_DAYS",
    "GGN_FORMAT_PATTERN",
    "COMPLIANCE_LEVELS",
    "AUDIT_TYPES",
    "CERTIFICATION_SCOPES",
    # Models
    "ChecklistItem",
    "ChecklistCategory",
    "ComplianceRequirement",
    "AuditFinding",
    "NonConformance",
    "CorrectiveAction",
    "ProducerProfile",
    "FarmRegistration",
    "ComplianceLevel",
    "AuditType",
    # Validators
    "validate_ggn_number",
    "validate_compliance_percentage",
    "check_major_must_compliance",
    "validate_certificate_validity",
    "validate_farm_registration",
    # Checklist
    "IFA_V6_CHECKLIST",
    "get_category",
    "get_checklist_item",
    "get_items_by_compliance_level",
    "calculate_compliance_score",
    # API Client / عميل واجهة البرمجة
    "GlobalGAPClient",
    "CertificateInfo",
    "CertificateStatus",
    "Producer",
    "GlobalGAPAPIError",
    "CertificateNotFound",
    "InvalidGGN",
    "RateLimitExceeded",
    "AuthenticationError",
    "RateLimiter",
]

__version__ = "6.0.0"
