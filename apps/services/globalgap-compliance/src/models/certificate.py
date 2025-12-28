"""
Certificate Models
نماذج الشهادات

Data models for GlobalGAP GGN certificates.
نماذج البيانات لشهادات GGN الخاصة بـ GlobalGAP.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CertificateStatus(str, Enum):
    """
    Certificate status
    حالة الشهادة
    """
    ACTIVE = "active"  # نشطة
    EXPIRED = "expired"  # منتهية الصلاحية
    SUSPENDED = "suspended"  # معلقة
    WITHDRAWN = "withdrawn"  # مسحوبة
    PENDING_APPROVAL = "pending_approval"  # في انتظار الموافقة
    RENEWAL_REQUIRED = "renewal_required"  # تتطلب التجديد


class CertificationScope(str, Enum):
    """
    Certification scope
    نطاق الشهادة
    """
    CROPS_BASE = "crops_base"  # قاعدة المحاصيل - Crops Base
    FRUIT_VEGETABLES = "fruit_vegetables"  # الفواكه والخضروات - Fruit and Vegetables
    COMBINABLE_CROPS = "combinable_crops"  # المحاصيل القابلة للدمج - Combinable Crops
    PLANT_PROPAGATION = "plant_propagation"  # إكثار النباتات - Plant Propagation Material
    FLOWERS_ORNAMENTALS = "flowers_ornamentals"  # الزهور والنباتات الزينة - Flowers and Ornamentals


class CertificationBody(BaseModel):
    """
    Certification body information
    معلومات الجهة المانحة للشهادة
    """
    name: str = Field(..., description="Certification body name | اسم الجهة المانحة للشهادة")
    code: str = Field(..., description="CB code | رمز الجهة")
    country: str = Field(..., description="Country | الدولة")
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    accreditation_number: Optional[str] = None


class GGNCertificate(BaseModel):
    """
    GlobalGAP GGN Certificate
    شهادة GlobalGAP GGN
    """
    id: Optional[str] = None
    farm_id: str = Field(..., description="Farm identifier | معرف المزرعة")
    tenant_id: str = Field(..., description="Tenant identifier | معرف المستأجر")

    # GGN Details | تفاصيل GGN
    ggn_number: str = Field(
        ...,
        description="GlobalGAP Number (GGN) - 13 digits | رقم GlobalGAP (GGN) - 13 رقم",
        min_length=13,
        max_length=13
    )
    gln_number: Optional[str] = Field(
        None,
        description="Global Location Number (GLN) | رقم الموقع العالمي",
        min_length=13,
        max_length=13
    )

    # Certificate information | معلومات الشهادة
    certificate_number: str = Field(..., description="Certificate number | رقم الشهادة")
    status: CertificateStatus = Field(
        default=CertificateStatus.PENDING_APPROVAL,
        description="Certificate status | حالة الشهادة"
    )

    # Certification scope | نطاق الشهادة
    scope: CertificationScope = Field(..., description="Certification scope | نطاق الشهادة")
    products: List[str] = Field(
        default_factory=list,
        description="Certified products | المنتجات المعتمدة"
    )
    production_methods: List[str] = Field(
        default_factory=list,
        description="e.g., conventional, organic | مثل: تقليدي، عضوي"
    )

    # Certificate dates | تواريخ الشهادة
    issue_date: date = Field(..., description="Issue date | تاريخ الإصدار")
    valid_from: date = Field(..., description="Valid from date | صالح من تاريخ")
    valid_until: date = Field(..., description="Valid until date | صالح حتى تاريخ")
    last_audit_date: Optional[date] = None
    next_audit_date: Optional[date] = None

    # Certification body | الجهة المانحة للشهادة
    certification_body: CertificationBody = Field(
        ...,
        description="Certification body details | تفاصيل الجهة المانحة للشهادة"
    )

    # Farm details | تفاصيل المزرعة
    farm_name: str = Field(..., description="Farm name | اسم المزرعة")
    farm_address: str = Field(..., description="Farm address | عنوان المزرعة")
    farm_country: str = Field(default="Yemen", description="Country | الدولة")
    total_area_ha: float = Field(..., gt=0, description="Total certified area in hectares | المساحة الكلية المعتمدة بالهكتار")

    # Producer information | معلومات المنتج
    producer_name: str = Field(..., description="Producer/farmer name | اسم المنتج/المزارع")
    producer_contact: Optional[str] = None

    # Compliance information | معلومات الامتثال
    ifa_version: str = Field(default="6.0", description="IFA version | إصدار معايير IFA")
    compliance_percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Overall compliance percentage | نسبة الامتثال الإجمالية"
    )
    major_must_compliance: bool = Field(
        default=False,
        description="All Major Must points compliant | جميع النقاط الإلزامية الرئيسية متوافقة"
    )
    minor_must_compliance_percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Minor Must compliance (must be >= 95%) | نسبة الامتثال للنقاط الإلزامية الثانوية (يجب أن تكون >= 95%)"
    )

    # Certificate documents | مستندات الشهادة
    certificate_pdf_url: Optional[str] = None
    audit_report_url: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)

    # Public information | معلومات عامة
    publicly_searchable: bool = Field(
        default=True,
        description="Certificate searchable in GlobalGAP database | الشهادة قابلة للبحث في قاعدة بيانات GlobalGAP"
    )

    # Renewal tracking | تتبع التجديد
    renewal_notification_sent: bool = Field(default=False)
    renewal_notification_date: Optional[datetime] = None

    # Metadata | بيانات وصفية
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "farm_id": "farm_12345",
                "tenant_id": "tenant_001",
                "ggn_number": "4063061234567",
                "gln_number": "4063061234567",
                "certificate_number": "GGN-YE-2025-001234",
                "status": "active",
                "scope": "fruit_vegetables",
                "products": ["tomatoes", "cucumbers", "peppers"],
                "production_methods": ["conventional"],
                "issue_date": "2025-01-15",
                "valid_from": "2025-01-15",
                "valid_until": "2026-01-14",
                "certification_body": {
                    "name": "Yemen Certification Body",
                    "code": "CB-YE-001",
                    "country": "Yemen"
                },
                "farm_name": "مزرعة النصر للخضروات",
                "farm_address": "صنعاء، اليمن",
                "total_area_ha": 5.5,
                "producer_name": "أحمد محمد علي",
                "ifa_version": "6.0",
                "compliance_percentage": 98.5,
                "major_must_compliance": True,
                "minor_must_compliance_percentage": 97.5
            }
        }

    def is_expiring_soon(self, days: int = 90) -> bool:
        """
        Check if certificate is expiring within specified days
        التحقق من انتهاء صلاحية الشهادة خلال عدد الأيام المحدد
        """
        if self.status != CertificateStatus.ACTIVE:
            return False

        days_until_expiry = (self.valid_until - date.today()).days
        return 0 < days_until_expiry <= days

    def is_expired(self) -> bool:
        """
        Check if certificate is expired
        التحقق من انتهاء صلاحية الشهادة
        """
        return date.today() > self.valid_until

    def days_until_expiry(self) -> int:
        """
        Calculate days until certificate expiry
        حساب الأيام المتبقية حتى انتهاء صلاحية الشهادة
        """
        return (self.valid_until - date.today()).days


class CertificateRenewal(BaseModel):
    """
    Certificate renewal request
    طلب تجديد الشهادة
    """
    id: Optional[str] = None
    certificate_id: str
    farm_id: str
    tenant_id: str

    # Renewal details | تفاصيل التجديد
    renewal_type: str = Field(..., description="regular, exceptional | عادي، استثنائي")
    requested_date: datetime = Field(default_factory=datetime.utcnow)
    requested_by: str = Field(..., description="Requester name | اسم مقدم الطلب")

    # Pre-renewal audit | التدقيق قبل التجديد
    pre_renewal_audit_scheduled: bool = False
    pre_renewal_audit_date: Optional[datetime] = None
    pre_renewal_audit_completed: bool = False

    # Renewal status | حالة التجديد
    renewal_status: str = Field(
        default="pending",
        description="pending, in_progress, approved, rejected | معلق، قيد التنفيذ، موافق عليه، مرفوض"
    )
    approval_date: Optional[datetime] = None
    approved_by: Optional[str] = None

    # New certificate | الشهادة الجديدة
    new_certificate_id: Optional[str] = None
    new_valid_from: Optional[date] = None
    new_valid_until: Optional[date] = None

    # Notes | ملاحظات
    notes: Optional[str] = None

    # Metadata | بيانات وصفية
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "certificate_id": "cert_12345",
                "farm_id": "farm_12345",
                "tenant_id": "tenant_001",
                "renewal_type": "regular",
                "requested_by": "أحمد محمد علي",
                "renewal_status": "pending"
            }
        }
