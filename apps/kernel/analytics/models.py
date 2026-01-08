"""
نماذج التحليلات - SAHOOL Analytics Models
==========================================
نماذج البيانات لتحليل نشاط المستخدمين والمزارعين

Pydantic models for user activity analytics and metrics
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ============== التعدادات - Enumerations ==============


class EventType(str, Enum):
    """
    أنواع أحداث نشاط المستخدم
    User activity event types
    """

    # أحداث الحقول - Field events
    FIELD_VIEWED = "field_viewed"  # عرض الحقل
    FIELD_CREATED = "field_created"  # إنشاء حقل
    FIELD_UPDATED = "field_updated"  # تحديث حقل
    FIELD_DELETED = "field_deleted"  # حذف حقل

    # أحداث التوصيات - Recommendation events
    RECOMMENDATION_VIEWED = "recommendation_viewed"  # عرض توصية
    RECOMMENDATION_APPLIED = "recommendation_applied"  # تطبيق توصية
    RECOMMENDATION_DISMISSED = "recommendation_dismissed"  # تجاهل توصية

    # أحداث التنبيهات - Alert events
    ALERT_RECEIVED = "alert_received"  # استلام تنبيه
    ALERT_ACKNOWLEDGED = "alert_acknowledged"  # الاطلاع على تنبيه
    ALERT_DISMISSED = "alert_dismissed"  # تجاهل تنبيه
    ALERT_ACTION_TAKEN = "alert_action_taken"  # اتخاذ إجراء بناءً على تنبيه

    # أحداث التقارير - Report events
    REPORT_GENERATED = "report_generated"  # إنشاء تقرير
    REPORT_VIEWED = "report_viewed"  # عرض تقرير
    REPORT_EXPORTED = "report_exported"  # تصدير تقرير
    REPORT_SHARED = "report_shared"  # مشاركة تقرير

    # أحداث المستشعرات - Sensor events
    SENSOR_ADDED = "sensor_added"  # إضافة مستشعر
    SENSOR_CONFIGURED = "sensor_configured"  # تكوين مستشعر
    SENSOR_DATA_VIEWED = "sensor_data_viewed"  # عرض بيانات المستشعر
    SENSOR_REMOVED = "sensor_removed"  # إزالة مستشعر

    # أحداث الري - Irrigation events
    IRRIGATION_SCHEDULED = "irrigation_scheduled"  # جدولة الري
    IRRIGATION_STARTED = "irrigation_started"  # بدء الري
    IRRIGATION_COMPLETED = "irrigation_completed"  # إكمال الري
    IRRIGATION_CANCELLED = "irrigation_cancelled"  # إلغاء الري

    # أحداث الجلسة - Session events
    LOGIN = "login"  # تسجيل الدخول
    LOGOUT = "logout"  # تسجيل الخروج
    SESSION_TIMEOUT = "session_timeout"  # انتهاء الجلسة

    # أحداث المحاصيل - Crop events
    CROP_PLANTED = "crop_planted"  # زراعة محصول
    CROP_HARVESTED = "crop_harvested"  # حصاد محصول
    CROP_STAGE_UPDATED = "crop_stage_updated"  # تحديث مرحلة المحصول

    # أحداث أخرى - Other events
    SEARCH_PERFORMED = "search_performed"  # إجراء بحث
    SETTINGS_UPDATED = "settings_updated"  # تحديث الإعدادات
    HELP_ACCESSED = "help_accessed"  # الوصول إلى المساعدة
    FEEDBACK_SUBMITTED = "feedback_submitted"  # إرسال ملاحظات


class UserRole(str, Enum):
    """
    أدوار المستخدمين
    User roles
    """

    FARMER = "farmer"  # مزارع
    AGRONOMIST = "agronomist"  # مهندس زراعي
    ADMIN = "admin"  # مسؤول النظام
    EXTENSION_OFFICER = "extension_officer"  # مرشد زراعي
    RESEARCHER = "researcher"  # باحث


class Governorate(str, Enum):
    """
    محافظات اليمن
    Yemen governorates
    """

    SANAA = "sanaa"  # صنعاء
    ADEN = "aden"  # عدن
    TAIZ = "taiz"  # تعز
    HODEIDAH = "hodeidah"  # الحديدة
    IBB = "ibb"  # إب
    DHAMAR = "dhamar"  # ذمار
    HAJJAH = "hajjah"  # حجة
    AMRAN = "amran"  # عمران
    SAADA = "saada"  # صعدة
    MAHWIT = "mahwit"  # المحويت
    RAYMAH = "raymah"  # ريمة
    ABYAN = "abyan"  # أبين
    SHABWAH = "shabwah"  # شبوة
    HADRAMAWT = "hadramawt"  # حضرموت
    MARIB = "marib"  # مأرب
    JAWF = "jawf"  # الجوف
    LAHIJ = "lahij"  # لحج
    DALEH = "daleh"  # الضالع
    BAYDA = "bayda"  # البيضاء
    SOCOTRA = "socotra"  # سقطرى
    MAHRAH = "mahrah"  # المهرة
    ADAN_ISLAH = "adan_islah"  # عدن الإصلاح


class TimePeriod(str, Enum):
    """
    الفترات الزمنية للتحليل
    Time periods for analysis
    """

    DAILY = "daily"  # يومي
    WEEKLY = "weekly"  # أسبوعي
    MONTHLY = "monthly"  # شهري
    QUARTERLY = "quarterly"  # ربع سنوي
    YEARLY = "yearly"  # سنوي


# ============== النماذج الأساسية - Base Models ==============


class AnalyticsEvent(BaseModel):
    """
    حدث نشاط مستخدم
    User activity event
    """

    model_config = ConfigDict(populate_by_name=True)

    # المعرفات - Identifiers
    event_id: str | None = Field(None, description="معرّف الحدث - Event ID")
    user_id: str = Field(..., description="معرّف المستخدم - User ID")
    tenant_id: str | None = Field(None, description="معرّف المستأجر - Tenant ID")
    session_id: str | None = Field(None, description="معرّف الجلسة - Session ID")

    # نوع الحدث - Event type
    event_type: EventType = Field(..., description="نوع الحدث - Event type")

    # التوقيت - Timing
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="وقت الحدث - Event timestamp"
    )

    # البيانات الوصفية - Metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="بيانات إضافية - Additional metadata"
    )

    # السياق - Context
    field_id: str | None = Field(None, description="معرّف الحقل - Field ID")
    crop_type: str | None = Field(None, description="نوع المحصول - Crop type")
    device_type: str | None = Field(None, description="نوع الجهاز - Device type (mobile/web)")
    ip_address: str | None = Field(None, description="عنوان IP - IP address")
    user_agent: str | None = Field(None, description="وكيل المستخدم - User agent")

    # الموقع - Location
    governorate: Governorate | None = Field(None, description="المحافظة - Governorate")
    district: str | None = Field(None, description="المديرية - District")

    # القيم - Values
    duration_seconds: float | None = Field(
        None, ge=0, description="المدة بالثواني - Duration in seconds"
    )
    value: float | None = Field(None, description="قيمة رقمية - Numeric value")

    # العلامات - Tags
    tags: list[str] = Field(default_factory=list, description="علامات - Tags for categorization")


class UserMetrics(BaseModel):
    """
    مقاييس نشاط المستخدم
    User activity metrics
    """

    model_config = ConfigDict(populate_by_name=True)

    # المعرفات - Identifiers
    user_id: str = Field(..., description="معرّف المستخدم - User ID")
    tenant_id: str | None = Field(None, description="معرّف المستأجر - Tenant ID")

    # الفترة الزمنية - Time period
    period_start: datetime = Field(..., description="بداية الفترة - Period start")
    period_end: datetime = Field(..., description="نهاية الفترة - Period end")
    period_type: TimePeriod = Field(..., description="نوع الفترة - Period type")

    # معلومات المستخدم - User info
    user_role: UserRole | None = Field(None, description="دور المستخدم - User role")
    governorate: Governorate | None = Field(None, description="المحافظة - Governorate")

    # مقاييس النشاط - Activity metrics
    total_events: int = Field(0, ge=0, description="إجمالي الأحداث - Total events")
    unique_days_active: int = Field(0, ge=0, description="أيام النشاط الفريدة - Unique active days")
    total_session_duration_minutes: float = Field(
        0, ge=0, description="مدة الجلسات الإجمالية - Total session duration"
    )
    average_session_duration_minutes: float = Field(
        0, ge=0, description="متوسط مدة الجلسة - Average session duration"
    )

    # مقاييس الحقول - Field metrics
    fields_created: int = Field(0, ge=0, description="الحقول المنشأة - Fields created")
    fields_updated: int = Field(0, ge=0, description="الحقول المحدثة - Fields updated")
    fields_viewed: int = Field(0, ge=0, description="الحقول المشاهدة - Fields viewed")
    total_fields_managed: int = Field(
        0, ge=0, description="إجمالي الحقول المدارة - Total fields managed"
    )

    # مقاييس التوصيات - Recommendation metrics
    recommendations_viewed: int = Field(
        0, ge=0, description="التوصيات المشاهدة - Recommendations viewed"
    )
    recommendations_applied: int = Field(
        0, ge=0, description="التوصيات المطبقة - Recommendations applied"
    )
    recommendation_application_rate: float = Field(
        0, ge=0, le=1, description="معدل تطبيق التوصيات - Recommendation application rate"
    )

    # مقاييس التنبيهات - Alert metrics
    alerts_received: int = Field(0, ge=0, description="التنبيهات المستلمة - Alerts received")
    alerts_acknowledged: int = Field(
        0, ge=0, description="التنبيهات المطلع عليها - Alerts acknowledged"
    )
    alert_response_rate: float = Field(
        0, ge=0, le=1, description="معدل الاستجابة للتنبيهات - Alert response rate"
    )
    average_alert_response_time_minutes: float | None = Field(
        None, ge=0, description="متوسط وقت الاستجابة - Average response time"
    )

    # مقاييس التقارير - Report metrics
    reports_generated: int = Field(0, ge=0, description="التقارير المنشأة - Reports generated")
    reports_exported: int = Field(0, ge=0, description="التقارير المصدرة - Reports exported")

    # مقاييس المستشعرات - Sensor metrics
    sensors_added: int = Field(0, ge=0, description="المستشعرات المضافة - Sensors added")
    sensors_configured: int = Field(0, ge=0, description="المستشعرات المكونة - Sensors configured")

    # مقاييس المحاصيل - Crop metrics
    crops_planted: int = Field(0, ge=0, description="المحاصيل المزروعة - Crops planted")
    crops_harvested: int = Field(0, ge=0, description="المحاصيل المحصودة - Crops harvested")

    # مقاييس الري - Irrigation metrics
    irrigation_events_scheduled: int = Field(
        0, ge=0, description="أحداث الري المجدولة - Irrigation events scheduled"
    )
    irrigation_events_completed: int = Field(
        0, ge=0, description="أحداث الري المكتملة - Irrigation events completed"
    )

    # مقاييس التفاعل - Engagement metrics
    feature_usage: dict[str, int] = Field(
        default_factory=dict, description="استخدام الميزات - Feature usage counts"
    )
    most_used_features: list[str] = Field(
        default_factory=list, description="الميزات الأكثر استخداماً - Most used features"
    )

    # البيانات الإضافية - Additional data
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="بيانات إضافية - Additional metadata"
    )

    # التحديث - Update tracking
    calculated_at: datetime = Field(
        default_factory=datetime.utcnow, description="وقت الحساب - Calculation timestamp"
    )


class CohortAnalysis(BaseModel):
    """
    تحليل الفوج (مجموعة المستخدمين الذين انضموا في نفس الفترة)
    Cohort analysis for user retention
    """

    model_config = ConfigDict(populate_by_name=True)

    # معلومات الفوج - Cohort info
    cohort_id: str = Field(..., description="معرّف الفوج - Cohort ID")
    cohort_name: str = Field(..., description="اسم الفوج - Cohort name")
    cohort_period: date = Field(..., description="فترة الفوج - Cohort period (month/week)")

    # الحجم - Size
    total_users: int = Field(0, ge=0, description="إجمالي المستخدمين - Total users in cohort")

    # معدلات الاحتفاظ - Retention rates
    retention_day_1: float = Field(
        0, ge=0, le=1, description="الاحتفاظ في اليوم 1 - Day 1 retention"
    )
    retention_day_7: float = Field(
        0, ge=0, le=1, description="الاحتفاظ في اليوم 7 - Day 7 retention"
    )
    retention_day_30: float = Field(
        0, ge=0, le=1, description="الاحتفاظ في اليوم 30 - Day 30 retention"
    )
    retention_day_90: float = Field(
        0, ge=0, le=1, description="الاحتفاظ في اليوم 90 - Day 90 retention"
    )

    # معلومات إضافية - Additional info
    metadata: dict[str, Any] = Field(default_factory=dict, description="بيانات إضافية - Metadata")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="وقت الإنشاء - Created at"
    )


class FeatureUsage(BaseModel):
    """
    استخدام ميزة معينة
    Feature usage statistics
    """

    model_config = ConfigDict(populate_by_name=True)

    # معلومات الميزة - Feature info
    feature_name: str = Field(..., description="اسم الميزة - Feature name")
    feature_category: str | None = Field(None, description="فئة الميزة - Feature category")

    # الفترة الزمنية - Time period
    period_start: datetime = Field(..., description="بداية الفترة - Period start")
    period_end: datetime = Field(..., description="نهاية الفترة - Period end")

    # مقاييس الاستخدام - Usage metrics
    total_uses: int = Field(0, ge=0, description="إجمالي الاستخدامات - Total uses")
    unique_users: int = Field(0, ge=0, description="المستخدمون الفريدون - Unique users")
    average_uses_per_user: float = Field(
        0, ge=0, description="متوسط الاستخدامات لكل مستخدم - Average uses per user"
    )

    # معدل التبني - Adoption metrics
    adoption_rate: float = Field(0, ge=0, le=1, description="معدل التبني - Adoption rate")
    power_users_count: int = Field(
        0, ge=0, description="عدد المستخدمين المكثفين - Power users count"
    )

    # البيانات الإضافية - Additional data
    metadata: dict[str, Any] = Field(default_factory=dict, description="بيانات إضافية - Metadata")
    calculated_at: datetime = Field(
        default_factory=datetime.utcnow, description="وقت الحساب - Calculated at"
    )


class RegionalMetrics(BaseModel):
    """
    مقاييس إقليمية حسب المحافظة
    Regional metrics by governorate
    """

    model_config = ConfigDict(populate_by_name=True)

    # الموقع - Location
    governorate: Governorate = Field(..., description="المحافظة - Governorate")
    district: str | None = Field(None, description="المديرية - District")

    # الفترة الزمنية - Time period
    period_start: datetime = Field(..., description="بداية الفترة - Period start")
    period_end: datetime = Field(..., description="نهاية الفترة - Period end")

    # مقاييس المستخدمين - User metrics
    total_users: int = Field(0, ge=0, description="إجمالي المستخدمين - Total users")
    active_users: int = Field(0, ge=0, description="المستخدمون النشطون - Active users")
    new_users: int = Field(0, ge=0, description="المستخدمون الجدد - New users")

    # مقاييس الحقول - Field metrics
    total_fields: int = Field(0, ge=0, description="إجمالي الحقول - Total fields")
    active_fields: int = Field(0, ge=0, description="الحقول النشطة - Active fields")
    total_area_hectares: float = Field(
        0, ge=0, description="المساحة الإجمالية (هكتار) - Total area (ha)"
    )

    # توزيع المحاصيل - Crop distribution
    crop_distribution: dict[str, int] = Field(
        default_factory=dict, description="توزيع المحاصيل - Crop distribution by type"
    )

    # مقاييس الأداء - Performance metrics
    average_yield_improvement: float | None = Field(
        None, description="متوسط تحسن الإنتاجية - Average yield improvement %"
    )
    total_water_saved_m3: float | None = Field(
        None, ge=0, description="إجمالي المياه الموفرة (م³) - Total water saved"
    )

    # البيانات الإضافية - Additional data
    metadata: dict[str, Any] = Field(default_factory=dict, description="بيانات إضافية - Metadata")
    calculated_at: datetime = Field(
        default_factory=datetime.utcnow, description="وقت الحساب - Calculated at"
    )


class FarmerAnalytics(BaseModel):
    """
    تحليلات خاصة بالمزارع
    Farmer-specific analytics
    """

    model_config = ConfigDict(populate_by_name=True)

    # معرف المزارع - Farmer ID
    user_id: str = Field(..., description="معرّف المزارع - Farmer user ID")

    # الفترة الزمنية - Time period
    period_start: datetime = Field(..., description="بداية الفترة - Period start")
    period_end: datetime = Field(..., description="نهاية الفترة - Period end")

    # المحاصيل المراقبة - Monitored crops
    crops_monitored_count: int = Field(
        0, ge=0, description="عدد المحاصيل المراقبة - Monitored crops count"
    )
    crops_by_type: dict[str, int] = Field(
        default_factory=dict, description="المحاصيل حسب النوع - Crops by type"
    )

    # الاستجابة للتنبيهات - Alert response
    alerts_response_time_avg_hours: float | None = Field(
        None,
        ge=0,
        description="متوسط وقت الاستجابة للتنبيهات (ساعات) - Average alert response time",
    )
    alerts_action_taken_rate: float = Field(
        0, ge=0, le=1, description="معدل اتخاذ الإجراء على التنبيهات - Alert action taken rate"
    )

    # التوصيات - Recommendations
    recommendation_follow_rate: float = Field(
        0, ge=0, le=1, description="معدل اتباع التوصيات - Recommendation follow rate"
    )
    recommendations_total: int = Field(
        0, ge=0, description="إجمالي التوصيات - Total recommendations"
    )
    recommendations_applied: int = Field(
        0, ge=0, description="التوصيات المطبقة - Applied recommendations"
    )

    # تحسن الإنتاجية - Yield improvement
    yield_improvement_trend: float | None = Field(
        None, description="اتجاه تحسن الإنتاجية (%) - Yield improvement trend %"
    )
    baseline_yield: float | None = Field(
        None, ge=0, description="الإنتاجية الأساسية - Baseline yield"
    )
    current_yield: float | None = Field(None, ge=0, description="الإنتاجية الحالية - Current yield")

    # كفاءة المياه - Water efficiency
    water_usage_efficiency: float | None = Field(
        None, ge=0, le=1, description="كفاءة استخدام المياه - Water usage efficiency"
    )
    water_saved_m3: float | None = Field(
        None, ge=0, description="المياه الموفرة (م³) - Water saved"
    )

    # المستشعرات - Sensors
    active_sensors_count: int = Field(
        0, ge=0, description="عدد المستشعرات النشطة - Active sensors count"
    )
    sensor_data_checks_per_week: float = Field(
        0, ge=0, description="فحوصات بيانات المستشعر أسبوعياً - Sensor checks per week"
    )

    # البيانات الإضافية - Additional data
    metadata: dict[str, Any] = Field(default_factory=dict, description="بيانات إضافية - Metadata")
    calculated_at: datetime = Field(
        default_factory=datetime.utcnow, description="وقت الحساب - Calculated at"
    )


# ============== مصدّر الوحدة - Module Exports ==============

__all__ = [
    # Enums
    "EventType",
    "UserRole",
    "Governorate",
    "TimePeriod",
    # Models
    "AnalyticsEvent",
    "UserMetrics",
    "CohortAnalysis",
    "FeatureUsage",
    "RegionalMetrics",
    "FarmerAnalytics",
]
