# نظام تحليلات SAHOOL - SAHOOL Analytics System

نظام متقدم لتتبع وتحليل نشاط المستخدمين والمزارعين في منصة SAHOOL

Advanced user activity tracking and analytics system for the SAHOOL platform

## المحتويات - Contents

- [نظرة عامة - Overview](#نظرة-عامة---overview)
- [الميزات - Features](#الميزات---features)
- [التثبيت - Installation](#التثبيت---installation)
- [الاستخدام - Usage](#الاستخدام---usage)
- [النماذج - Models](#النماذج---models)
- [أمثلة - Examples](#أمثلة---examples)

## نظرة عامة - Overview

يوفر نظام تحليلات SAHOOL مجموعة شاملة من الأدوات لتتبع نشاط المستخدمين، وحساب مقاييس التفاعل، وتحليل سلوك المزارعين، وإنشاء تقارير إقليمية.

The SAHOOL Analytics System provides a comprehensive suite of tools for tracking user activity, calculating engagement metrics, analyzing farmer behavior, and generating regional reports.

## الميزات - Features

### 1. تتبع الأحداث - Event Tracking

تتبع جميع أنواع أحداث نشاط المستخدمين:

Track all types of user activity events:

- **أحداث الحقول - Field Events**
  - عرض الحقول (Field Viewed)
  - إنشاء الحقول (Field Created)
  - تحديث الحقول (Field Updated)
  - حذف الحقول (Field Deleted)

- **أحداث التوصيات - Recommendation Events**
  - عرض التوصيات (Recommendation Viewed)
  - تطبيق التوصيات (Recommendation Applied)
  - تجاهل التوصيات (Recommendation Dismissed)

- **أحداث التنبيهات - Alert Events**
  - استلام التنبيهات (Alert Received)
  - الاطلاع على التنبيهات (Alert Acknowledged)
  - اتخاذ إجراء على التنبيهات (Alert Action Taken)

- **أحداث التقارير - Report Events**
  - إنشاء التقارير (Report Generated)
  - تصدير التقارير (Report Exported)
  - مشاركة التقارير (Report Shared)

- **أحداث المستشعرات - Sensor Events**
  - إضافة المستشعرات (Sensor Added)
  - تكوين المستشعرات (Sensor Configured)
  - عرض بيانات المستشعرات (Sensor Data Viewed)

- **أحداث الري - Irrigation Events**
  - جدولة الري (Irrigation Scheduled)
  - بدء الري (Irrigation Started)
  - إكمال الري (Irrigation Completed)

### 2. مقاييس التفاعل - Engagement Metrics

حساب مقاييس تفاعل شاملة للمستخدمين:

Calculate comprehensive user engagement metrics:

- إجمالي الأحداث (Total Events)
- أيام النشاط الفريدة (Unique Active Days)
- مدة الجلسات (Session Duration)
- معدل تطبيق التوصيات (Recommendation Application Rate)
- معدل الاستجابة للتنبيهات (Alert Response Rate)
- استخدام الميزات (Feature Usage)

### 3. معدلات الاحتفاظ - Retention Rates

تحليل معدلات الاحتفاظ بالمستخدمين:

Analyze user retention rates:

- الاحتفاظ في اليوم الأول (Day 1 Retention)
- الاحتفاظ في اليوم السابع (Day 7 Retention)
- الاحتفاظ بعد 30 يوماً (Day 30 Retention)
- الاحتفاظ بعد 90 يوماً (Day 90 Retention)

### 4. تحليلات المزارعين - Farmer Analytics

تحليلات متخصصة للمزارعين:

Specialized analytics for farmers:

- عدد المحاصيل المراقبة (Crops Monitored Count)
- وقت الاستجابة للتنبيهات (Alerts Response Time)
- معدل اتباع التوصيات (Recommendation Follow Rate)
- اتجاه تحسن الإنتاجية (Yield Improvement Trend)

### 5. التحليلات الإقليمية - Regional Analytics

مقاييس إقليمية حسب المحافظات:

Regional metrics by governorates:

- توزيع المستخدمين حسب المحافظة (Users by Governorate)
- الحقول النشطة حسب المنطقة (Active Fields by Region)
- توزيع المحاصيل (Crop Distribution)

## التثبيت - Installation

```bash
# نسخ الملفات إلى مشروعك - Copy files to your project
cp -r analytics /path/to/your/project/apps/kernel/

# تثبيت المتطلبات - Install dependencies
pip install pydantic
```

## الاستخدام - Usage

### 1. البداية السريعة - Quick Start

```python
from apps.kernel.analytics import (
    UserAnalyticsService,
    EventType,
    Governorate,
    TimePeriod,
)

# إنشاء خدمة التحليلات - Create analytics service
analytics = UserAnalyticsService()

# تتبع حدث - Track an event
event = analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.FIELD_VIEWED,
    field_id="field_001",
    governorate=Governorate.SANAA,
    metadata={"field_name": "حقل الطماطم"}
)

# الحصول على مقاييس المستخدم - Get user metrics
metrics = analytics.get_user_engagement(
    user_id="farmer_123",
    period=TimePeriod.MONTHLY
)

print(f"Total Events: {metrics.total_events}")
print(f"Fields Created: {metrics.fields_created}")
print(f"Recommendation Rate: {metrics.recommendation_application_rate:.2%}")
```

### 2. تتبع نشاط كامل - Track Complete Activity

```python
# تسجيل الدخول - Login
analytics.track_session(
    user_id="farmer_123",
    session_id="session_001",
    action="start"
)

# عرض حقل - View field
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.FIELD_VIEWED,
    field_id="field_001"
)

# إنشاء حقل جديد - Create new field
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.FIELD_CREATED,
    field_id="field_002",
    crop_type="cucumber",
    metadata={"area_ha": 2.5}
)

# عرض توصية - View recommendation
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.RECOMMENDATION_VIEWED,
    metadata={"recommendation_id": "rec_001"}
)

# تطبيق توصية - Apply recommendation
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.RECOMMENDATION_APPLIED,
    metadata={"recommendation_id": "rec_001"}
)

# تسجيل الخروج - Logout
analytics.track_session(
    user_id="farmer_123",
    session_id="session_001",
    action="end"
)
```

### 3. المقاييس العامة - General Metrics

```python
# المستخدمون النشطون يومياً - Daily Active Users
dau = analytics.daily_active_users()

# المستخدمون النشطون أسبوعياً - Weekly Active Users
wau = analytics.weekly_active_users()

# المستخدمون النشطون شهرياً - Monthly Active Users
mau = analytics.monthly_active_users()

# متوسط مدة الجلسة - Average Session Duration
avg_session = analytics.average_session_duration()

print(f"DAU: {dau}, WAU: {wau}, MAU: {mau}")
print(f"Avg Session: {avg_session:.2f} minutes")
```

### 4. استخدام الميزات - Feature Usage

```python
# إحصائيات استخدام ميزة معينة - Feature usage statistics
feature_usage = analytics.get_feature_usage(
    feature_name="field_management",
    period=TimePeriod.MONTHLY
)

print(f"Total Uses: {feature_usage.total_uses}")
print(f"Unique Users: {feature_usage.unique_users}")
print(f"Adoption Rate: {feature_usage.adoption_rate:.2%}")
```

### 5. تحليلات المزارعين - Farmer Analytics

```python
# عدد المحاصيل المراقبة - Monitored crops count
crops_count = analytics.crops_monitored_count("farmer_123")

# وقت الاستجابة للتنبيهات - Alert response time
response_time = analytics.alerts_response_time("farmer_123")

# معدل اتباع التوصيات - Recommendation follow rate
follow_rate = analytics.recommendation_follow_rate("farmer_123")

# اتجاه تحسن الإنتاجية - Yield improvement trend
yield_trend = analytics.yield_improvement_trend("farmer_123")

print(f"Crops Monitored: {crops_count}")
print(f"Alert Response Time: {response_time:.2f} hours")
print(f"Recommendation Follow Rate: {follow_rate:.2%}")
print(f"Yield Improvement: {yield_trend:.2f}%")
```

### 6. التحليلات الإقليمية - Regional Analytics

```python
# المستخدمون حسب المحافظة - Users by governorate
users_by_gov = analytics.users_by_governorate()
for governorate, count in users_by_gov.items():
    print(f"{governorate}: {count} users")

# الحقول النشطة حسب المنطقة - Active fields by region
fields_by_region = analytics.active_fields_by_region()

# توزيع المحاصيل - Crop distribution
crop_dist = analytics.crop_distribution(
    governorate=Governorate.SANAA
)
```

### 7. معدلات الاحتفاظ - Retention Rates

```python
from datetime import date

# تحليل معدل الاحتفاظ - Cohort retention analysis
cohort_analysis = analytics.calculate_retention_rate(
    cohort="2024-01",
    cohort_period=date(2024, 1, 1),
    days=90
)

print(f"Total Users: {cohort_analysis.total_users}")
print(f"Day 1 Retention: {cohort_analysis.retention_day_1:.2%}")
print(f"Day 7 Retention: {cohort_analysis.retention_day_7:.2%}")
print(f"Day 30 Retention: {cohort_analysis.retention_day_30:.2%}")
```

## النماذج - Models

### AnalyticsEvent

نموذج حدث نشاط المستخدم - User activity event model

```python
class AnalyticsEvent(BaseModel):
    event_id: Optional[str]
    user_id: str
    event_type: EventType
    timestamp: datetime
    metadata: Dict[str, Any]
    field_id: Optional[str]
    crop_type: Optional[str]
    governorate: Optional[Governorate]
    # ... المزيد من الحقول
```

### UserMetrics

نموذج مقاييس المستخدم - User metrics model

```python
class UserMetrics(BaseModel):
    user_id: str
    period_start: datetime
    period_end: datetime
    period_type: TimePeriod
    total_events: int
    unique_days_active: int
    fields_created: int
    recommendations_applied: int
    recommendation_application_rate: float
    # ... المزيد من المقاييس
```

### FarmerAnalytics

نموذج تحليلات المزارع - Farmer analytics model

```python
class FarmerAnalytics(BaseModel):
    user_id: str
    crops_monitored_count: int
    alerts_response_time_avg_hours: Optional[float]
    recommendation_follow_rate: float
    yield_improvement_trend: Optional[float]
    water_usage_efficiency: Optional[float]
    # ... المزيد من المقاييس
```

### RegionalMetrics

نموذج المقاييس الإقليمية - Regional metrics model

```python
class RegionalMetrics(BaseModel):
    governorate: Governorate
    total_users: int
    active_users: int
    total_fields: int
    crop_distribution: Dict[str, int]
    average_yield_improvement: Optional[float]
    # ... المزيد من المقاييس
```

## أمثلة متقدمة - Advanced Examples

### مثال: تتبع دورة حياة حقل كاملة

```python
# زراعة محصول - Plant crop
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.CROP_PLANTED,
    field_id="field_001",
    crop_type="tomato",
    metadata={"planting_date": "2024-01-01", "area_ha": 2.0}
)

# إضافة مستشعرات - Add sensors
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.SENSOR_ADDED,
    field_id="field_001",
    metadata={"sensor_type": "soil_moisture"}
)

# جدولة الري - Schedule irrigation
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.IRRIGATION_SCHEDULED,
    field_id="field_001",
    metadata={"water_amount_mm": 25}
)

# حصاد المحصول - Harvest crop
analytics.track_event(
    user_id="farmer_123",
    event_type=EventType.CROP_HARVESTED,
    field_id="field_001",
    metadata={"yield_tons": 15.5, "harvest_date": "2024-06-01"}
)
```

### مثال: لوحة تحكم تحليلية

```python
def generate_dashboard(user_id: str):
    """إنشاء لوحة تحكم تحليلية - Generate analytics dashboard"""

    # الحصول على المقاييس - Get metrics
    metrics = analytics.get_user_engagement(user_id, TimePeriod.MONTHLY)

    # تحليلات المزارع - Farmer analytics
    crops_count = analytics.crops_monitored_count(user_id)
    follow_rate = analytics.recommendation_follow_rate(user_id)
    response_time = analytics.alerts_response_time(user_id)

    # عرض اللوحة - Display dashboard
    dashboard = {
        "user_id": user_id,
        "activity_summary": {
            "total_events": metrics.total_events,
            "active_days": metrics.unique_days_active,
            "avg_session_minutes": metrics.average_session_duration_minutes,
        },
        "field_management": {
            "fields_created": metrics.fields_created,
            "fields_updated": metrics.fields_updated,
            "fields_viewed": metrics.fields_viewed,
        },
        "recommendations": {
            "viewed": metrics.recommendations_viewed,
            "applied": metrics.recommendations_applied,
            "follow_rate": follow_rate,
        },
        "alerts": {
            "received": metrics.alerts_received,
            "acknowledged": metrics.alerts_acknowledged,
            "avg_response_hours": response_time,
        },
        "crops": {
            "monitored_count": crops_count,
        },
        "top_features": metrics.most_used_features,
    }

    return dashboard
```

## التكامل مع قاعدة البيانات - Database Integration

لاستخدام قاعدة بيانات حقيقية بدلاً من التخزين في الذاكرة:

To use a real database instead of in-memory storage:

```python
class PostgresStorage:
    """مثال على نظام تخزين PostgreSQL"""

    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)

    def save_event(self, event: AnalyticsEvent):
        # حفظ الحدث في قاعدة البيانات
        pass

    def get_user_events(self, user_id, start_date, end_date):
        # استرجاع أحداث المستخدم
        pass

# استخدام التخزين المخصص
storage = PostgresStorage("postgresql://...")
analytics = UserAnalyticsService(storage_backend=storage)
```

## الترخيص - License

هذا المشروع جزء من منصة SAHOOL

This project is part of the SAHOOL platform

## الدعم - Support

للأسئلة والدعم، يرجى التواصل مع فريق SAHOOL

For questions and support, please contact the SAHOOL team
