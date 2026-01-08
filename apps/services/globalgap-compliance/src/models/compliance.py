"""
Compliance Models
نماذج الامتثال

Data models for compliance status, records, and audit results.
نماذج البيانات لحالة الامتثال والسجلات ونتائج التدقيق.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ComplianceStatus(str, Enum):
    """
    Compliance status enumeration
    تعداد حالات الامتثال
    """

    COMPLIANT = "compliant"  # متوافق
    NON_COMPLIANT = "non_compliant"  # غير متوافق
    PARTIALLY_COMPLIANT = "partially_compliant"  # متوافق جزئيًا
    PENDING_REVIEW = "pending_review"  # قيد المراجعة
    NOT_ASSESSED = "not_assessed"  # لم يتم التقييم


class SeverityLevel(str, Enum):
    """
    Severity level for non-compliance
    مستوى خطورة عدم الامتثال
    """

    CRITICAL = "critical"  # حرج
    MAJOR = "major"  # رئيسي
    MINOR = "minor"  # ثانوي
    OBSERVATION = "observation"  # ملاحظة


class ComplianceRecord(BaseModel):
    """
    Compliance record for a farm
    سجل الامتثال للمزرعة
    """

    id: str | None = None
    farm_id: str = Field(..., description="Farm identifier | معرف المزرعة")
    tenant_id: str = Field(..., description="Tenant identifier | معرف المستأجر")

    # Compliance details | تفاصيل الامتثال
    overall_status: ComplianceStatus = Field(
        default=ComplianceStatus.NOT_ASSESSED,
        description="Overall compliance status | حالة الامتثال الإجمالية",
    )
    compliance_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Compliance percentage | نسبة الامتثال",
    )

    # Control points | نقاط التحكم
    total_control_points: int = Field(
        default=0, description="Total control points | إجمالي نقاط التحكم"
    )
    compliant_points: int = Field(
        default=0, description="Compliant control points | نقاط التحكم المتوافقة"
    )
    non_compliant_points: int = Field(
        default=0, description="Non-compliant points | نقاط عدم التوافق"
    )

    # Critical non-conformities | عدم المطابقات الحرجة
    major_must_fails: int = Field(
        default=0,
        description="Major Must non-conformities | عدم المطابقات الرئيسية الإلزامية",
    )
    minor_must_fails: int = Field(
        default=0,
        description="Minor Must non-conformities | عدم المطابقات الثانوية الإلزامية",
    )

    # Assessment details | تفاصيل التقييم
    assessed_by: str | None = None
    assessment_date: datetime | None = None
    next_assessment_date: datetime | None = None

    # Metadata | بيانات وصفية
    ifa_version: str = Field(default="6.0", description="IFA version | إصدار معايير IFA")
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "farm_id": "farm_12345",
                "tenant_id": "tenant_001",
                "overall_status": "partially_compliant",
                "compliance_percentage": 85.5,
                "total_control_points": 200,
                "compliant_points": 171,
                "non_compliant_points": 29,
                "major_must_fails": 2,
                "minor_must_fails": 5,
                "ifa_version": "6.0",
            }
        }


class NonConformity(BaseModel):
    """
    Non-conformity finding
    نتيجة عدم المطابقة
    """

    id: str | None = None
    compliance_record_id: str
    control_point_id: str
    control_point_number: str = Field(..., description="CP number e.g., AF.1.1.1 | رقم نقطة التحكم")

    # Non-conformity details | تفاصيل عدم المطابقة
    severity: SeverityLevel
    description_ar: str = Field(..., description="Description in Arabic | الوصف بالعربية")
    description_en: str = Field(..., description="Description in English | الوصف بالإنجليزية")

    # Corrective actions | الإجراءات التصحيحية
    corrective_action_required: bool = True
    corrective_action_taken: str | None = None
    corrective_action_deadline: datetime | None = None
    corrective_action_completed: bool = False

    # Evidence | الأدلة
    evidence_photos: list[str] = Field(default_factory=list, description="Photo URLs | روابط الصور")
    evidence_documents: list[str] = Field(
        default_factory=list, description="Document URLs | روابط المستندات"
    )

    # Tracking | المتابعة
    identified_date: datetime = Field(default_factory=datetime.utcnow)
    resolved_date: datetime | None = None
    verified_by: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "compliance_record_id": "comp_123",
                "control_point_id": "cp_af_1_1_1",
                "control_point_number": "AF.1.1.1",
                "severity": "major",
                "description_ar": "عدم وجود سجلات تطبيق المبيدات الحشرية",
                "description_en": "Lack of pesticide application records",
                "corrective_action_required": True,
            }
        }


class AuditResult(BaseModel):
    """
    Audit result summary
    ملخص نتائج التدقيق
    """

    id: str | None = None
    farm_id: str
    tenant_id: str
    compliance_record_id: str

    # Audit information | معلومات التدقيق
    audit_type: str = Field(
        ..., description="internal, external, certification | داخلي، خارجي، إصدار شهادة"
    )
    auditor_name: str = Field(..., description="Auditor name | اسم المدقق")
    auditor_organization: str | None = None

    # Audit dates | تواريخ التدقيق
    audit_date: datetime
    audit_duration_days: int = Field(
        default=1, description="Audit duration in days | مدة التدقيق بالأيام"
    )

    # Results | النتائج
    audit_status: str = Field(..., description="passed, failed, conditional | نجح، فشل، مشروط")
    overall_score: float = Field(
        ge=0.0, le=100.0, description="Overall audit score | الدرجة الإجمالية للتدقيق"
    )

    # Findings | النتائج
    total_findings: int = Field(default=0)
    critical_findings: int = Field(default=0)
    major_findings: int = Field(default=0)
    minor_findings: int = Field(default=0)
    observations: int = Field(default=0)

    # Report | التقرير
    report_url: str | None = None
    executive_summary_ar: str | None = None
    executive_summary_en: str | None = None

    # Recommendations | التوصيات
    recommendations: list[str] = Field(default_factory=list)

    # Follow-up | المتابعة
    follow_up_required: bool = False
    follow_up_deadline: datetime | None = None

    # Metadata | بيانات وصفية
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "farm_id": "farm_12345",
                "tenant_id": "tenant_001",
                "compliance_record_id": "comp_123",
                "audit_type": "internal",
                "auditor_name": "أحمد محمد",
                "audit_date": "2025-12-15T09:00:00Z",
                "audit_status": "conditional",
                "overall_score": 87.5,
                "total_findings": 12,
                "major_findings": 3,
                "minor_findings": 9,
            }
        }
