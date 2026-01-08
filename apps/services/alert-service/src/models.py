"""
SAHOOL Alert Service - Data Models
نماذج بيانات خدمة التنبيهات
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

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
    tenant_id: str | None = Field(None, description="معرف المستأجر")
    type: AlertType = Field(..., description="نوع التنبيه")
    severity: AlertSeverity = Field(..., description="مستوى الخطورة")
    title: str = Field(..., min_length=1, max_length=200, description="عنوان التنبيه")
    title_en: str | None = Field(None, max_length=200, description="العنوان بالإنجليزية")
    message: str = Field(..., min_length=1, max_length=2000, description="رسالة التنبيه")
    message_en: str | None = Field(None, max_length=2000, description="الرسالة بالإنجليزية")
    recommendations: list[str] | None = Field(default=[], description="التوصيات")
    recommendations_en: list[str] | None = Field(default=[], description="التوصيات بالإنجليزية")
    metadata: dict[str, Any] | None = Field(default={}, description="بيانات إضافية")
    expires_at: datetime | None = Field(None, description="تاريخ انتهاء الصلاحية")
    source_service: str | None = Field(None, description="الخدمة المصدر")
    correlation_id: str | None = Field(None, description="معرف الارتباط")


class AlertUpdate(BaseModel):
    """تحديث تنبيه"""

    status: AlertStatus | None = None
    acknowledged_by: str | None = None
    dismissed_by: str | None = None
    resolved_by: str | None = None
    resolution_note: str | None = Field(None, max_length=1000)


class RuleCondition(BaseModel):
    """شرط قاعدة التنبيه"""

    metric: str = Field(..., description="اسم المقياس (مثل: soil_moisture, ndvi)")
    operator: ConditionOperator = Field(..., description="عامل المقارنة")
    value: float = Field(..., description="القيمة للمقارنة")
    duration_minutes: int | None = Field(0, ge=0, description="المدة بالدقائق قبل الإطلاق")


class AlertRuleConfig(BaseModel):
    """إعدادات التنبيه للقاعدة"""

    type: AlertType
    severity: AlertSeverity
    title: str = Field(..., max_length=200)
    title_en: str | None = None
    message_template: str | None = None


class AlertRuleCreate(BaseModel):
    """إنشاء قاعدة تنبيه"""

    field_id: str
    tenant_id: str | None = None
    name: str = Field(..., min_length=1, max_length=100)
    name_en: str | None = None
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
    tenant_id: str | None
    type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    title: str
    title_en: str | None
    message: str
    message_en: str | None
    recommendations: list[str]
    recommendations_en: list[str]
    metadata: dict[str, Any]
    source_service: str | None
    correlation_id: str | None
    created_at: datetime
    expires_at: datetime | None
    acknowledged_at: datetime | None
    acknowledged_by: str | None
    dismissed_at: datetime | None
    dismissed_by: str | None
    resolved_at: datetime | None
    resolved_by: str | None
    resolution_note: str | None

    class Config:
        from_attributes = True


class AlertRuleResponse(BaseModel):
    """استجابة قاعدة التنبيه"""

    id: str
    field_id: str
    tenant_id: str | None
    name: str
    name_en: str | None
    enabled: bool
    condition: RuleCondition
    alert_config: AlertRuleConfig
    cooldown_hours: int
    last_triggered_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertStats(BaseModel):
    """إحصائيات التنبيهات"""

    total_alerts: int
    active_alerts: int
    by_type: dict[str, int]
    by_severity: dict[str, int]
    by_status: dict[str, int]
    acknowledged_rate: float
    resolved_rate: float
    average_resolution_hours: float | None


class PaginatedResponse(BaseModel):
    """استجابة مع ترقيم الصفحات"""

    items: list[AlertResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
