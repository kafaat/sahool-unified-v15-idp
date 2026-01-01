"""
SAHOOL Alert Service - Data Models
نماذج بيانات خدمة التنبيهات
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ═══════════════════════════════════════════════════════════════════════════════
# Enums - التعدادات
# ═══════════════════════════════════════════════════════════════════════════════


class AlertType(str, Enum):
    """أنواع التنبيهات"""

    WEATHER = "weather"  # تنبيهات الطقس
    PEST = "pest"  # تنبيهات الآفات
    DISEASE = "disease"  # تنبيهات الأمراض
    IRRIGATION = "irrigation"  # تنبيهات الري
    FERTILIZER = "fertilizer"  # تنبيهات التسميد
    HARVEST = "harvest"  # تنبيهات الحصاد
    NDVI_LOW = "ndvi_low"  # انخفاض NDVI
    NDVI_ANOMALY = "ndvi_anomaly"  # شذوذ NDVI
    SOIL_MOISTURE = "soil_moisture"  # رطوبة التربة
    EQUIPMENT = "equipment"  # تنبيهات المعدات
    GENERAL = "general"  # تنبيهات عامة


class AlertSeverity(str, Enum):
    """مستويات الخطورة"""

    CRITICAL = "critical"  # حرج - يتطلب إجراء فوري
    HIGH = "high"  # عالي - يتطلب انتباه عاجل
    MEDIUM = "medium"  # متوسط - يحتاج مراجعة
    LOW = "low"  # منخفض - للعلم والإحاطة
    INFO = "info"  # معلوماتي


class AlertStatus(str, Enum):
    """حالة التنبيه"""

    ACTIVE = "active"  # نشط
    ACKNOWLEDGED = "acknowledged"  # تم الإقرار به
    DISMISSED = "dismissed"  # تم رفضه
    RESOLVED = "resolved"  # تم حله
    EXPIRED = "expired"  # منتهي الصلاحية


class ConditionOperator(str, Enum):
    """عوامل المقارنة للقواعد"""

    EQ = "eq"  # يساوي
    NE = "ne"  # لا يساوي
    GT = "gt"  # أكبر من
    GTE = "gte"  # أكبر من أو يساوي
    LT = "lt"  # أصغر من
    LTE = "lte"  # أصغر من أو يساوي


# ═══════════════════════════════════════════════════════════════════════════════
# Request Models - نماذج الطلبات
# ═══════════════════════════════════════════════════════════════════════════════


class AlertCreate(BaseModel):
    """إنشاء تنبيه جديد"""

    field_id: str = Field(..., description="معرف الحقل")
    tenant_id: Optional[str] = Field(None, description="معرف المستأجر")
    type: AlertType = Field(..., description="نوع التنبيه")
    severity: AlertSeverity = Field(..., description="مستوى الخطورة")
    title: str = Field(..., min_length=1, max_length=200, description="عنوان التنبيه")
    title_en: Optional[str] = Field(
        None, max_length=200, description="العنوان بالإنجليزية"
    )
    message: str = Field(
        ..., min_length=1, max_length=2000, description="رسالة التنبيه"
    )
    message_en: Optional[str] = Field(
        None, max_length=2000, description="الرسالة بالإنجليزية"
    )
    recommendations: Optional[List[str]] = Field(default=[], description="التوصيات")
    recommendations_en: Optional[List[str]] = Field(
        default=[], description="التوصيات بالإنجليزية"
    )
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="بيانات إضافية")
    expires_at: Optional[datetime] = Field(None, description="تاريخ انتهاء الصلاحية")
    source_service: Optional[str] = Field(None, description="الخدمة المصدر")
    correlation_id: Optional[str] = Field(None, description="معرف الارتباط")


class AlertUpdate(BaseModel):
    """تحديث تنبيه"""

    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = None
    dismissed_by: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_note: Optional[str] = Field(None, max_length=1000)


class RuleCondition(BaseModel):
    """شرط قاعدة التنبيه"""

    metric: str = Field(..., description="اسم المقياس (مثل: soil_moisture, ndvi)")
    operator: ConditionOperator = Field(..., description="عامل المقارنة")
    value: float = Field(..., description="القيمة للمقارنة")
    duration_minutes: Optional[int] = Field(
        0, ge=0, description="المدة بالدقائق قبل الإطلاق"
    )


class AlertRuleConfig(BaseModel):
    """إعدادات التنبيه للقاعدة"""

    type: AlertType
    severity: AlertSeverity
    title: str = Field(..., max_length=200)
    title_en: Optional[str] = None
    message_template: Optional[str] = None


class AlertRuleCreate(BaseModel):
    """إنشاء قاعدة تنبيه"""

    field_id: str
    tenant_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    name_en: Optional[str] = None
    enabled: bool = True
    condition: RuleCondition
    alert_config: AlertRuleConfig
    cooldown_hours: int = Field(24, ge=0, le=168, description="فترة الانتظار بالساعات")


# ═══════════════════════════════════════════════════════════════════════════════
# Response Models - نماذج الاستجابة
# ═══════════════════════════════════════════════════════════════════════════════


class AlertResponse(BaseModel):
    """استجابة التنبيه"""

    id: str
    field_id: str
    tenant_id: Optional[str]
    type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    title: str
    title_en: Optional[str]
    message: str
    message_en: Optional[str]
    recommendations: List[str]
    recommendations_en: List[str]
    metadata: Dict[str, Any]
    source_service: Optional[str]
    correlation_id: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[str]
    dismissed_at: Optional[datetime]
    dismissed_by: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution_note: Optional[str]

    class Config:
        from_attributes = True


class AlertRuleResponse(BaseModel):
    """استجابة قاعدة التنبيه"""

    id: str
    field_id: str
    tenant_id: Optional[str]
    name: str
    name_en: Optional[str]
    enabled: bool
    condition: RuleCondition
    alert_config: AlertRuleConfig
    cooldown_hours: int
    last_triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertStats(BaseModel):
    """إحصائيات التنبيهات"""

    total_alerts: int
    active_alerts: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    acknowledged_rate: float
    resolved_rate: float
    average_resolution_hours: Optional[float]


class PaginatedResponse(BaseModel):
    """استجابة مع ترقيم الصفحات"""

    items: List[AlertResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
