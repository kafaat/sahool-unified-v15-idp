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

from .constants import (
    IFA_VERSION,
    COMPLIANCE_THRESHOLDS,
    CERTIFICATE_VALIDITY_DAYS,
    GGN_FORMAT_PATTERN,
    COMPLIANCE_LEVELS,
    AUDIT_TYPES,
    CERTIFICATION_SCOPES,
)

from .models import (
    ChecklistItem,
    ChecklistCategory,
    ComplianceRequirement,
    AuditFinding,
    NonConformance,
    CorrectiveAction,
    ProducerProfile,
    FarmRegistration,
    ComplianceLevel,
    AuditType,
)

from .validators import (
    validate_ggn_number,
    validate_compliance_percentage,
    check_major_must_compliance,
    validate_certificate_validity,
    validate_farm_registration,
)

from .ifa_v6_checklist import (
    IFA_V6_CHECKLIST,
    get_category,
    get_checklist_item,
    get_items_by_compliance_level,
    calculate_compliance_score,
)

# GlobalGAP Supply Chain Portal API Client
# عميل واجهة برمجة بوابة سلسلة التوريد GlobalGAP
from .api_client import (
    GlobalGAPClient,
    CertificateInfo,
    CertificateStatus,
    Producer,
    GlobalGAPAPIError,
    CertificateNotFound,
    InvalidGGN,
    RateLimitExceeded,
    AuthenticationError,
    RateLimiter,
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
