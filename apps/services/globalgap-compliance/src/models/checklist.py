"""
Checklist Models
نماذج قوائم المراجعة

Data models for GlobalGAP IFA checklists and control points.
نماذج البيانات لقوائم المراجعة ونقاط التحكم الخاصة بمعايير GlobalGAP IFA.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ComplianceLevel(str, Enum):
    """
    Compliance level according to IFA standards
    مستوى الامتثال وفقًا لمعايير IFA
    """

    MAJOR_MUST = "major_must"  # إلزامي رئيسي - Major Must (failure = no certification)
    MINOR_MUST = "minor_must"  # إلزامي ثانوي - Minor Must (95% compliance required)
    RECOMMENDATION = "recommendation"  # توصية - Recommendation (good practice)


class ChecklistCategory(str, Enum):
    """
    Main checklist categories from IFA v6
    فئات قائمة المراجعة الرئيسية من معايير IFA v6
    """

    # All Farm Base (AF) | قاعدة جميع المزارع
    AF_SITE_MANAGEMENT = "af_site_management"  # إدارة الموقع
    AF_SOIL_MANAGEMENT = "af_soil_management"  # إدارة التربة
    AF_FERTILIZER_USE = "af_fertilizer_use"  # استخدام الأسمدة
    AF_IRRIGATION = "af_irrigation"  # الري
    AF_CROP_PROTECTION = "af_crop_protection"  # حماية المحاصيل
    AF_HARVEST = "af_harvest"  # الحصاد
    AF_PRODUCE_HANDLING = "af_produce_handling"  # التعامل مع المنتجات
    AF_WASTE_POLLUTION = "af_waste_pollution"  # النفايات والتلوث
    AF_WORKER_HEALTH = "af_worker_health"  # صحة وسلامة العمال
    AF_ENVIRONMENT = "af_environment"  # البيئة والتنوع البيولوجي

    # Crops Base (CB) | قاعدة المحاصيل
    CB_PROPAGATION_MATERIAL = "cb_propagation_material"  # مواد الإكثار
    CB_SITE_HISTORY = "cb_site_history"  # تاريخ الموقع


class ControlPointStatus(str, Enum):
    """
    Status of a control point assessment
    حالة تقييم نقطة التحكم
    """

    COMPLIANT = "compliant"  # متوافق
    NON_COMPLIANT = "non_compliant"  # غير متوافق
    NOT_APPLICABLE = "not_applicable"  # غير قابل للتطبيق
    NOT_ASSESSED = "not_assessed"  # لم يتم التقييم


class ChecklistItem(BaseModel):
    """
    Individual checklist item (control point)
    عنصر قائمة المراجعة (نقطة التحكم)
    """

    id: str | None = None

    # Control point identification | تعريف نقطة التحكم
    control_point_number: str = Field(
        ..., description="CP number e.g., AF.1.1.1 | رقم نقطة التحكم"
    )
    category: ChecklistCategory = Field(..., description="Category | الفئة")
    compliance_level: ComplianceLevel = Field(
        ..., description="Compliance level | مستوى الامتثال"
    )

    # Content | المحتوى
    title_ar: str = Field(..., description="Title in Arabic | العنوان بالعربية")
    title_en: str = Field(..., description="Title in English | العنوان بالإنجليزية")
    requirement_ar: str = Field(
        ..., description="Requirement description in Arabic | وصف المتطلب بالعربية"
    )
    requirement_en: str = Field(
        ..., description="Requirement description in English | وصف المتطلب بالإنجليزية"
    )

    # Compliance criteria | معايير الامتثال
    compliance_criteria_ar: list[str] = Field(
        default_factory=list,
        description="Compliance criteria in Arabic | معايير الامتثال بالعربية",
    )
    compliance_criteria_en: list[str] = Field(
        default_factory=list,
        description="Compliance criteria in English | معايير الامتثال بالإنجليزية",
    )

    # Guidance | الإرشادات
    guidance_ar: str | None = None
    guidance_en: str | None = None

    # Verification methods | طرق التحقق
    verification_methods: list[str] = Field(
        default_factory=list,
        description="Visual inspection, document review, interview | فحص بصري، مراجعة مستندات، مقابلة",
    )

    # Required evidence | الأدلة المطلوبة
    required_evidence: list[str] = Field(
        default_factory=list,
        description="Documents, records, photos required | المستندات والسجلات والصور المطلوبة",
    )

    # Related control points | نقاط التحكم ذات الصلة
    related_control_points: list[str] = Field(default_factory=list)

    # Metadata | بيانات وصفية
    ifa_version: str = Field(
        default="6.0", description="IFA version | إصدار معايير IFA"
    )
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "control_point_number": "AF.1.1.1",
                "category": "af_site_management",
                "compliance_level": "major_must",
                "title_ar": "يجب أن يكون لدى المزرعة نظام موثق لإدارة الجودة",
                "title_en": "The farm must have a documented quality management system",
                "requirement_ar": "يجب أن تكون هناك سجلات موثقة لجميع الأنشطة الزراعية",
                "requirement_en": "There must be documented records of all agricultural activities",
            }
        }


class ChecklistAssessment(BaseModel):
    """
    Assessment of a checklist item for a specific farm
    تقييم عنصر قائمة المراجعة لمزرعة معينة
    """

    id: str | None = None
    farm_id: str
    tenant_id: str
    checklist_item_id: str
    control_point_number: str

    # Assessment result | نتيجة التقييم
    status: ControlPointStatus = Field(
        default=ControlPointStatus.NOT_ASSESSED,
        description="Assessment status | حالة التقييم",
    )

    # Evidence | الأدلة
    evidence_description: str | None = None
    evidence_photos: list[str] = Field(default_factory=list)
    evidence_documents: list[str] = Field(default_factory=list)

    # Assessor notes | ملاحظات المقيم
    assessor_notes: str | None = None
    non_compliance_reason: str | None = None

    # Corrective action | الإجراء التصحيحي
    corrective_action_required: bool = False
    corrective_action_plan: str | None = None
    corrective_action_deadline: datetime | None = None
    corrective_action_status: str | None = None  # pending, in_progress, completed

    # Assessment details | تفاصيل التقييم
    assessed_by: str = Field(..., description="Assessor name | اسم المقيم")
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    verified_by: str | None = None
    verification_date: datetime | None = None

    # Metadata | بيانات وصفية
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "farm_id": "farm_12345",
                "tenant_id": "tenant_001",
                "checklist_item_id": "item_af_1_1_1",
                "control_point_number": "AF.1.1.1",
                "status": "compliant",
                "assessed_by": "أحمد محمد",
                "assessment_date": "2025-12-28T10:00:00Z",
            }
        }


class Checklist(BaseModel):
    """
    Complete checklist for IFA compliance
    قائمة المراجعة الكاملة للامتثال لمعايير IFA
    """

    id: str | None = None
    name_ar: str = Field(
        ..., description="Checklist name in Arabic | اسم القائمة بالعربية"
    )
    name_en: str = Field(
        ..., description="Checklist name in English | اسم القائمة بالإنجليزية"
    )

    # Checklist details | تفاصيل القائمة
    ifa_version: str = Field(
        default="6.0", description="IFA version | إصدار معايير IFA"
    )
    checklist_type: str = Field(
        ..., description="full, partial, follow_up | كامل، جزئي، متابعة"
    )

    # Scope | النطاق
    applicable_categories: list[ChecklistCategory] = Field(
        default_factory=list,
        description="Applicable categories | الفئات القابلة للتطبيق",
    )
    crop_types: list[str] = Field(
        default_factory=list,
        description="Applicable crop types | أنواع المحاصيل القابلة للتطبيق",
    )

    # Items | العناصر
    total_items: int = Field(
        default=0, description="Total checklist items | إجمالي عناصر القائمة"
    )
    major_must_count: int = Field(
        default=0,
        description="Number of Major Must items | عدد العناصر الإلزامية الرئيسية",
    )
    minor_must_count: int = Field(
        default=0,
        description="Number of Minor Must items | عدد العناصر الإلزامية الثانوية",
    )
    recommendation_count: int = Field(
        default=0, description="Number of Recommendations | عدد التوصيات"
    )

    # Metadata | بيانات وصفية
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name_ar": "قائمة المراجعة الكاملة لمعايير IFA v6",
                "name_en": "Full IFA v6 Checklist",
                "ifa_version": "6.0",
                "checklist_type": "full",
                "total_items": 250,
                "major_must_count": 50,
                "minor_must_count": 150,
                "recommendation_count": 50,
            }
        }
