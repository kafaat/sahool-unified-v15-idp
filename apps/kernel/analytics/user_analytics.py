"""
خدمة تحليلات المستخدمين - SAHOOL User Analytics Service
=========================================================
نظام متقدم لتتبع وتحليل نشاط المستخدمين والمزارعين

Advanced user activity tracking and analytics system
"""

import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict, Counter

from .models import (
    AnalyticsEvent,
    UserMetrics,
    CohortAnalysis,
    FeatureUsage,
    RegionalMetrics,
    FarmerAnalytics,
    EventType,
    UserRole,
    Governorate,
    TimePeriod,
)


# ============== خدمة تحليلات المستخدمين - User Analytics Service ==============

class UserAnalyticsService:
    """
    خدمة تحليلات المستخدمين
    User Analytics Service

    الميزات الرئيسية:
    - تتبع أحداث نشاط المستخدمين
    - حساب مقاييس التفاعل
    - تحليل معدلات الاحتفاظ
    - إحصائيات استخدام الميزات
    - تحليلات خاصة بالمزارعين
    - مقاييس إقليمية

    Main features:
    - Track user activity events
    - Calculate engagement metrics
    - Analyze retention rates
    - Feature usage statistics
    - Farmer-specific analytics
    - Regional metrics
    """

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        تهيئة خدمة التحليلات
        Initialize analytics service

        Args:
            storage_backend: نظام التخزين (اختياري) - Storage backend (optional)
                           يمكن استخدام قاعدة بيانات، Redis، أو ملفات JSON
                           Can use database, Redis, or JSON files
        """
        self.storage = storage_backend or InMemoryStorage()
        self.events: List[AnalyticsEvent] = []

    # ============== تتبع الأحداث - Event Tracking ==============

    def track_event(
        self,
        user_id: str,
        event_type: EventType,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AnalyticsEvent:
        """
        تتبع حدث نشاط مستخدم
        Track user activity event

        Args:
            user_id: معرّف المستخدم - User ID
            event_type: نوع الحدث - Event type
            metadata: بيانات إضافية - Additional metadata
            **kwargs: معلمات إضافية - Additional parameters

        Returns:
            AnalyticsEvent: الحدث المسجل - Tracked event

        مثال - Example:
            >>> service.track_event(
            ...     user_id="user123",
            ...     event_type=EventType.FIELD_VIEWED,
            ...     metadata={"field_name": "حقل الطماطم"},
            ...     field_id="field456",
            ...     governorate=Governorate.SANAA
            ... )
        """
        # إنشاء معرّف فريد للحدث - Create unique event ID
        event_id = str(uuid.uuid4())

        # دمج البيانات الوصفية - Merge metadata
        event_metadata = metadata or {}

        # إنشاء حدث - Create event
        event = AnalyticsEvent(
            event_id=event_id,
            user_id=user_id,
            event_type=event_type,
            metadata=event_metadata,
            timestamp=datetime.utcnow(),
            **kwargs
        )

        # حفظ الحدث - Save event
        self.storage.save_event(event)
        self.events.append(event)

        return event

    def track_session(
        self,
        user_id: str,
        session_id: str,
        action: str = "start",
        **kwargs
    ) -> AnalyticsEvent:
        """
        تتبع جلسة المستخدم
        Track user session

        Args:
            user_id: معرّف المستخدم - User ID
            session_id: معرّف الجلسة - Session ID
            action: الإجراء (start/end) - Action (start/end)
            **kwargs: معلمات إضافية - Additional parameters
        """
        event_type = EventType.LOGIN if action == "start" else EventType.LOGOUT

        return self.track_event(
            user_id=user_id,
            event_type=event_type,
            session_id=session_id,
            **kwargs
        )

    # ============== مقاييس التفاعل - Engagement Metrics ==============

    def get_user_engagement(
        self,
        user_id: str,
        period: TimePeriod = TimePeriod.MONTHLY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> UserMetrics:
        """
        الحصول على مقاييس تفاعل المستخدم
        Get user engagement metrics

        Args:
            user_id: معرّف المستخدم - User ID
            period: الفترة الزمنية - Time period
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            UserMetrics: مقاييس المستخدم - User metrics
        """
        # تحديد الفترة الزمنية - Determine time period
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = self._get_period_start(end_date, period)

        # الحصول على أحداث المستخدم - Get user events
        user_events = self.storage.get_user_events(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        # حساب المقاييس - Calculate metrics
        metrics = self._calculate_user_metrics(
            user_id=user_id,
            events=user_events,
            period_start=start_date,
            period_end=end_date,
            period_type=period
        )

        return metrics

    def _calculate_user_metrics(
        self,
        user_id: str,
        events: List[AnalyticsEvent],
        period_start: datetime,
        period_end: datetime,
        period_type: TimePeriod
    ) -> UserMetrics:
        """
        حساب مقاييس المستخدم من الأحداث
        Calculate user metrics from events
        """
        # مقاييس أساسية - Basic metrics
        total_events = len(events)

        # أيام النشاط الفريدة - Unique active days
        unique_days = len(set(event.timestamp.date() for event in events))

        # مقاييس الجلسة - Session metrics
        sessions = self._extract_sessions(events)
        total_session_duration = sum(s['duration_minutes'] for s in sessions)
        avg_session_duration = total_session_duration / len(sessions) if sessions else 0

        # مقاييس الحقول - Field metrics
        field_events = [e for e in events if 'field' in e.event_type.value]
        fields_created = len([e for e in events if e.event_type == EventType.FIELD_CREATED])
        fields_updated = len([e for e in events if e.event_type == EventType.FIELD_UPDATED])
        fields_viewed = len([e for e in events if e.event_type == EventType.FIELD_VIEWED])

        # عدد الحقول الفريدة المدارة - Unique fields managed
        unique_fields = len(set(e.field_id for e in field_events if e.field_id))

        # مقاييس التوصيات - Recommendation metrics
        rec_viewed = len([e for e in events if e.event_type == EventType.RECOMMENDATION_VIEWED])
        rec_applied = len([e for e in events if e.event_type == EventType.RECOMMENDATION_APPLIED])
        rec_rate = rec_applied / rec_viewed if rec_viewed > 0 else 0

        # مقاييس التنبيهات - Alert metrics
        alerts_received = len([e for e in events if e.event_type == EventType.ALERT_RECEIVED])
        alerts_acknowledged = len([e for e in events if e.event_type == EventType.ALERT_ACKNOWLEDGED])
        alert_rate = alerts_acknowledged / alerts_received if alerts_received > 0 else 0

        # وقت الاستجابة للتنبيهات - Alert response time
        avg_alert_response = self._calculate_alert_response_time(events)

        # مقاييس التقارير - Report metrics
        reports_generated = len([e for e in events if e.event_type == EventType.REPORT_GENERATED])
        reports_exported = len([e for e in events if e.event_type == EventType.REPORT_EXPORTED])

        # مقاييس المستشعرات - Sensor metrics
        sensors_added = len([e for e in events if e.event_type == EventType.SENSOR_ADDED])
        sensors_configured = len([e for e in events if e.event_type == EventType.SENSOR_CONFIGURED])

        # مقاييس المحاصيل - Crop metrics
        crops_planted = len([e for e in events if e.event_type == EventType.CROP_PLANTED])
        crops_harvested = len([e for e in events if e.event_type == EventType.CROP_HARVESTED])

        # مقاييس الري - Irrigation metrics
        irrigation_scheduled = len([e for e in events if e.event_type == EventType.IRRIGATION_SCHEDULED])
        irrigation_completed = len([e for e in events if e.event_type == EventType.IRRIGATION_COMPLETED])

        # استخدام الميزات - Feature usage
        feature_usage = self._calculate_feature_usage(events)
        most_used = sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        most_used_features = [feature for feature, count in most_used]

        # معلومات المستخدم - User info
        user_role = events[0].metadata.get('user_role') if events else None
        governorate = events[0].governorate if events else None

        return UserMetrics(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            period_type=period_type,
            user_role=user_role,
            governorate=governorate,
            total_events=total_events,
            unique_days_active=unique_days,
            total_session_duration_minutes=total_session_duration,
            average_session_duration_minutes=avg_session_duration,
            fields_created=fields_created,
            fields_updated=fields_updated,
            fields_viewed=fields_viewed,
            total_fields_managed=unique_fields,
            recommendations_viewed=rec_viewed,
            recommendations_applied=rec_applied,
            recommendation_application_rate=rec_rate,
            alerts_received=alerts_received,
            alerts_acknowledged=alerts_acknowledged,
            alert_response_rate=alert_rate,
            average_alert_response_time_minutes=avg_alert_response,
            reports_generated=reports_generated,
            reports_exported=reports_exported,
            sensors_added=sensors_added,
            sensors_configured=sensors_configured,
            crops_planted=crops_planted,
            crops_harvested=crops_harvested,
            irrigation_events_scheduled=irrigation_scheduled,
            irrigation_events_completed=irrigation_completed,
            feature_usage=feature_usage,
            most_used_features=most_used_features,
        )

    # ============== معدلات الاحتفاظ - Retention Rates ==============

    def calculate_retention_rate(
        self,
        cohort: str,
        cohort_period: date,
        days: int = 30
    ) -> CohortAnalysis:
        """
        حساب معدل الاحتفاظ لفوج معين
        Calculate retention rate for a specific cohort

        Args:
            cohort: معرّف الفوج - Cohort identifier
            cohort_period: فترة الفوج - Cohort period (signup month/week)
            days: عدد الأيام للتحليل - Number of days to analyze

        Returns:
            CohortAnalysis: تحليل الفوج - Cohort analysis

        مثال - Example:
            >>> service.calculate_retention_rate(
            ...     cohort="2024-01",
            ...     cohort_period=date(2024, 1, 1),
            ...     days=90
            ... )
        """
        # الحصول على مستخدمي الفوج - Get cohort users
        cohort_users = self.storage.get_cohort_users(cohort_period)
        total_users = len(cohort_users)

        if total_users == 0:
            return CohortAnalysis(
                cohort_id=cohort,
                cohort_name=f"Cohort {cohort}",
                cohort_period=cohort_period,
                total_users=0,
                retention_day_1=0,
                retention_day_7=0,
                retention_day_30=0,
                retention_day_90=0,
            )

        # حساب معدلات الاحتفاظ - Calculate retention rates
        retention_1 = self._calculate_retention_for_day(cohort_users, cohort_period, 1)
        retention_7 = self._calculate_retention_for_day(cohort_users, cohort_period, 7)
        retention_30 = self._calculate_retention_for_day(cohort_users, cohort_period, 30)
        retention_90 = self._calculate_retention_for_day(cohort_users, cohort_period, 90)

        return CohortAnalysis(
            cohort_id=cohort,
            cohort_name=f"Cohort {cohort}",
            cohort_period=cohort_period,
            total_users=total_users,
            retention_day_1=retention_1,
            retention_day_7=retention_7,
            retention_day_30=retention_30,
            retention_day_90=retention_90,
        )

    def _calculate_retention_for_day(
        self,
        users: List[str],
        start_date: date,
        day: int
    ) -> float:
        """
        حساب معدل الاحتفاظ ليوم محدد
        Calculate retention rate for a specific day
        """
        target_date = start_date + timedelta(days=day)
        active_users = 0

        for user_id in users:
            # التحقق من نشاط المستخدم في اليوم المحدد
            # Check if user was active on target day
            events = self.storage.get_user_events(
                user_id=user_id,
                start_date=datetime.combine(target_date, datetime.min.time()),
                end_date=datetime.combine(target_date, datetime.max.time())
            )
            if events:
                active_users += 1

        return active_users / len(users) if users else 0

    # ============== استخدام الميزات - Feature Usage ==============

    def get_feature_usage(
        self,
        feature_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: TimePeriod = TimePeriod.MONTHLY
    ) -> FeatureUsage:
        """
        الحصول على إحصائيات استخدام ميزة معينة
        Get feature usage statistics

        Args:
            feature_name: اسم الميزة - Feature name
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date
            period: الفترة الزمنية - Time period

        Returns:
            FeatureUsage: إحصائيات استخدام الميزة - Feature usage statistics
        """
        # تحديد الفترة الزمنية - Determine time period
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = self._get_period_start(end_date, period)

        # الحصول على أحداث الميزة - Get feature events
        feature_events = self.storage.get_feature_events(
            feature_name=feature_name,
            start_date=start_date,
            end_date=end_date
        )

        # حساب المقاييس - Calculate metrics
        total_uses = len(feature_events)
        unique_users = len(set(event.user_id for event in feature_events))

        # متوسط الاستخدامات لكل مستخدم - Average uses per user
        avg_uses_per_user = total_uses / unique_users if unique_users > 0 else 0

        # معدل التبني - Adoption rate (نسبة المستخدمين الذين استخدموا الميزة)
        total_users = self.storage.get_total_active_users(start_date, end_date)
        adoption_rate = unique_users / total_users if total_users > 0 else 0

        # المستخدمون المكثفون (استخدموا الميزة أكثر من 10 مرات)
        # Power users (used feature more than 10 times)
        user_counts = Counter(event.user_id for event in feature_events)
        power_users = sum(1 for count in user_counts.values() if count > 10)

        return FeatureUsage(
            feature_name=feature_name,
            period_start=start_date,
            period_end=end_date,
            total_uses=total_uses,
            unique_users=unique_users,
            average_uses_per_user=avg_uses_per_user,
            adoption_rate=adoption_rate,
            power_users_count=power_users,
        )

    # ============== المقاييس العامة - General Metrics ==============

    def daily_active_users(
        self,
        date_val: Optional[date] = None
    ) -> int:
        """
        عدد المستخدمين النشطين يومياً
        Daily Active Users (DAU)

        Args:
            date_val: التاريخ - Date (default: today)

        Returns:
            int: عدد المستخدمين النشطين - Number of active users
        """
        if not date_val:
            date_val = date.today()

        start_time = datetime.combine(date_val, datetime.min.time())
        end_time = datetime.combine(date_val, datetime.max.time())

        events = self.storage.get_events_in_range(start_time, end_time)
        return len(set(event.user_id for event in events))

    def weekly_active_users(
        self,
        week_start: Optional[date] = None
    ) -> int:
        """
        عدد المستخدمين النشطين أسبوعياً
        Weekly Active Users (WAU)

        Args:
            week_start: بداية الأسبوع - Week start date

        Returns:
            int: عدد المستخدمين النشطين - Number of active users
        """
        if not week_start:
            week_start = date.today() - timedelta(days=7)

        start_time = datetime.combine(week_start, datetime.min.time())
        end_time = datetime.combine(week_start + timedelta(days=7), datetime.max.time())

        events = self.storage.get_events_in_range(start_time, end_time)
        return len(set(event.user_id for event in events))

    def monthly_active_users(
        self,
        month_start: Optional[date] = None
    ) -> int:
        """
        عدد المستخدمين النشطين شهرياً
        Monthly Active Users (MAU)

        Args:
            month_start: بداية الشهر - Month start date

        Returns:
            int: عدد المستخدمين النشطين - Number of active users
        """
        if not month_start:
            month_start = date.today() - timedelta(days=30)

        start_time = datetime.combine(month_start, datetime.min.time())
        end_time = datetime.combine(month_start + timedelta(days=30), datetime.max.time())

        events = self.storage.get_events_in_range(start_time, end_time)
        return len(set(event.user_id for event in events))

    def average_session_duration(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """
        متوسط مدة الجلسة
        Average session duration in minutes

        Args:
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            float: متوسط المدة بالدقائق - Average duration in minutes
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        events = self.storage.get_events_in_range(start_date, end_date)
        sessions = self._extract_sessions(events)

        if not sessions:
            return 0.0

        total_duration = sum(s['duration_minutes'] for s in sessions)
        return total_duration / len(sessions)

    def feature_adoption_rate(
        self,
        feature_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """
        معدل تبني ميزة معينة
        Feature adoption rate

        Args:
            feature_name: اسم الميزة - Feature name
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            float: معدل التبني (0-1) - Adoption rate (0-1)
        """
        feature_usage = self.get_feature_usage(feature_name, start_date, end_date)
        return feature_usage.adoption_rate

    # ============== تحليلات المزارعين - Farmer Analytics ==============

    def crops_monitored_count(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        عدد المحاصيل المراقبة للمزارع
        Count of crops monitored by farmer

        Args:
            user_id: معرّف المزارع - Farmer ID
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            int: عدد المحاصيل - Number of crops
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=365)  # سنة واحدة - One year

        events = self.storage.get_user_events(user_id, start_date, end_date)

        # الحصول على المحاصيل الفريدة - Get unique crops
        crops = set()
        for event in events:
            if event.crop_type:
                crops.add(event.crop_type)
            if event.field_id:
                # يمكن أيضاً الحصول على المحاصيل من الحقول
                # Can also get crops from fields
                crops.add(event.field_id)

        return len(crops)

    def alerts_response_time(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[float]:
        """
        متوسط وقت الاستجابة للتنبيهات
        Average alert response time in hours

        Args:
            user_id: معرّف المزارع - Farmer ID
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            Optional[float]: متوسط الوقت بالساعات - Average time in hours
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        events = self.storage.get_user_events(user_id, start_date, end_date)

        # حساب وقت الاستجابة - Calculate response time
        response_times = []
        alert_received_times = {}

        for event in sorted(events, key=lambda e: e.timestamp):
            if event.event_type == EventType.ALERT_RECEIVED:
                # حفظ وقت استلام التنبيه - Save alert received time
                alert_id = event.metadata.get('alert_id')
                if alert_id:
                    alert_received_times[alert_id] = event.timestamp

            elif event.event_type == EventType.ALERT_ACKNOWLEDGED:
                # حساب الفرق الزمني - Calculate time difference
                alert_id = event.metadata.get('alert_id')
                if alert_id and alert_id in alert_received_times:
                    received_time = alert_received_times[alert_id]
                    response_time = (event.timestamp - received_time).total_seconds() / 3600  # hours
                    response_times.append(response_time)

        if not response_times:
            return None

        return sum(response_times) / len(response_times)

    def recommendation_follow_rate(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """
        معدل اتباع التوصيات
        Recommendation follow rate

        Args:
            user_id: معرّف المزارع - Farmer ID
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            float: معدل الاتباع (0-1) - Follow rate (0-1)
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        events = self.storage.get_user_events(user_id, start_date, end_date)

        viewed = len([e for e in events if e.event_type == EventType.RECOMMENDATION_VIEWED])
        applied = len([e for e in events if e.event_type == EventType.RECOMMENDATION_APPLIED])

        return applied / viewed if viewed > 0 else 0.0

    def yield_improvement_trend(
        self,
        user_id: str,
        baseline_period_days: int = 180,
        current_period_days: int = 90
    ) -> Optional[float]:
        """
        اتجاه تحسن الإنتاجية
        Yield improvement trend percentage

        Args:
            user_id: معرّف المزارع - Farmer ID
            baseline_period_days: أيام الفترة الأساسية - Baseline period days
            current_period_days: أيام الفترة الحالية - Current period days

        Returns:
            Optional[float]: نسبة التحسن - Improvement percentage
        """
        # الحصول على بيانات الإنتاجية - Get yield data
        current_end = datetime.utcnow()
        current_start = current_end - timedelta(days=current_period_days)

        baseline_end = current_start
        baseline_start = baseline_end - timedelta(days=baseline_period_days)

        # الحصول على أحداث الحصاد - Get harvest events
        baseline_events = self.storage.get_user_events(user_id, baseline_start, baseline_end)
        current_events = self.storage.get_user_events(user_id, current_start, current_end)

        baseline_harvests = [e for e in baseline_events if e.event_type == EventType.CROP_HARVESTED]
        current_harvests = [e for e in current_events if e.event_type == EventType.CROP_HARVESTED]

        if not baseline_harvests or not current_harvests:
            return None

        # حساب متوسط الإنتاجية - Calculate average yield
        baseline_yield = sum(e.metadata.get('yield', 0) for e in baseline_harvests) / len(baseline_harvests)
        current_yield = sum(e.metadata.get('yield', 0) for e in current_harvests) / len(current_harvests)

        if baseline_yield == 0:
            return None

        # حساب نسبة التحسن - Calculate improvement percentage
        improvement = ((current_yield - baseline_yield) / baseline_yield) * 100
        return improvement

    # ============== التحليلات الإقليمية - Regional Analytics ==============

    def users_by_governorate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[Governorate, int]:
        """
        توزيع المستخدمين حسب المحافظة
        User distribution by governorate

        Args:
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            Dict[Governorate, int]: عدد المستخدمين لكل محافظة - Users per governorate
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        events = self.storage.get_events_in_range(start_date, end_date)

        # تجميع المستخدمين حسب المحافظة - Group users by governorate
        governorate_users = defaultdict(set)
        for event in events:
            if event.governorate:
                governorate_users[event.governorate].add(event.user_id)

        return {gov: len(users) for gov, users in governorate_users.items()}

    def active_fields_by_region(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[Governorate, int]:
        """
        الحقول النشطة حسب المنطقة
        Active fields by region

        Args:
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            Dict[Governorate, int]: عدد الحقول النشطة لكل محافظة - Active fields per governorate
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        events = self.storage.get_events_in_range(start_date, end_date)

        # تجميع الحقول حسب المحافظة - Group fields by governorate
        governorate_fields = defaultdict(set)
        for event in events:
            if event.governorate and event.field_id:
                governorate_fields[event.governorate].add(event.field_id)

        return {gov: len(fields) for gov, fields in governorate_fields.items()}

    def crop_distribution(
        self,
        governorate: Optional[Governorate] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        توزيع المحاصيل
        Crop distribution

        Args:
            governorate: المحافظة (اختياري) - Governorate (optional)
            start_date: تاريخ البداية - Start date
            end_date: تاريخ النهاية - End date

        Returns:
            Dict[str, int]: عدد المحاصيل لكل نوع - Crop count by type
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=365)

        events = self.storage.get_events_in_range(start_date, end_date)

        # تصفية حسب المحافظة إذا تم تحديدها - Filter by governorate if specified
        if governorate:
            events = [e for e in events if e.governorate == governorate]

        # تجميع المحاصيل - Group crops
        crop_events = [e for e in events if e.event_type == EventType.CROP_PLANTED]
        crop_counts = Counter(e.crop_type for e in crop_events if e.crop_type)

        return dict(crop_counts)

    # ============== دوال مساعدة - Helper Functions ==============

    def _get_period_start(self, end_date: datetime, period: TimePeriod) -> datetime:
        """
        حساب تاريخ بداية الفترة
        Calculate period start date
        """
        if period == TimePeriod.DAILY:
            return end_date - timedelta(days=1)
        elif period == TimePeriod.WEEKLY:
            return end_date - timedelta(days=7)
        elif period == TimePeriod.MONTHLY:
            return end_date - timedelta(days=30)
        elif period == TimePeriod.QUARTERLY:
            return end_date - timedelta(days=90)
        elif period == TimePeriod.YEARLY:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)

    def _extract_sessions(self, events: List[AnalyticsEvent]) -> List[Dict[str, Any]]:
        """
        استخراج الجلسات من الأحداث
        Extract sessions from events
        """
        sessions = []
        session_map = {}

        for event in sorted(events, key=lambda e: e.timestamp):
            if event.event_type == EventType.LOGIN:
                session_map[event.session_id] = {
                    'start': event.timestamp,
                    'end': None,
                    'duration_minutes': 0
                }
            elif event.event_type == EventType.LOGOUT and event.session_id in session_map:
                session = session_map[event.session_id]
                session['end'] = event.timestamp
                duration = (event.timestamp - session['start']).total_seconds() / 60
                session['duration_minutes'] = duration
                sessions.append(session)

        # الجلسات غير المنتهية - Sessions without logout
        # افتراض مدة 30 دقيقة - Assume 30 minutes duration
        for session_id, session in session_map.items():
            if session['end'] is None:
                session['duration_minutes'] = 30
                sessions.append(session)

        return sessions

    def _calculate_feature_usage(self, events: List[AnalyticsEvent]) -> Dict[str, int]:
        """
        حساب استخدام الميزات
        Calculate feature usage
        """
        feature_map = {
            EventType.FIELD_VIEWED: "field_management",
            EventType.FIELD_CREATED: "field_management",
            EventType.FIELD_UPDATED: "field_management",
            EventType.RECOMMENDATION_VIEWED: "recommendations",
            EventType.RECOMMENDATION_APPLIED: "recommendations",
            EventType.ALERT_RECEIVED: "alerts",
            EventType.ALERT_ACKNOWLEDGED: "alerts",
            EventType.REPORT_GENERATED: "reports",
            EventType.REPORT_EXPORTED: "reports",
            EventType.SENSOR_ADDED: "sensors",
            EventType.SENSOR_CONFIGURED: "sensors",
            EventType.IRRIGATION_SCHEDULED: "irrigation",
            EventType.IRRIGATION_COMPLETED: "irrigation",
        }

        usage = defaultdict(int)
        for event in events:
            feature = feature_map.get(event.event_type)
            if feature:
                usage[feature] += 1

        return dict(usage)

    def _calculate_alert_response_time(self, events: List[AnalyticsEvent]) -> Optional[float]:
        """
        حساب متوسط وقت الاستجابة للتنبيهات
        Calculate average alert response time
        """
        response_times = []
        alert_times = {}

        for event in sorted(events, key=lambda e: e.timestamp):
            if event.event_type == EventType.ALERT_RECEIVED:
                alert_id = event.metadata.get('alert_id')
                if alert_id:
                    alert_times[alert_id] = event.timestamp
            elif event.event_type == EventType.ALERT_ACKNOWLEDGED:
                alert_id = event.metadata.get('alert_id')
                if alert_id and alert_id in alert_times:
                    diff = (event.timestamp - alert_times[alert_id]).total_seconds() / 60
                    response_times.append(diff)

        return sum(response_times) / len(response_times) if response_times else None


# ============== نظام تخزين بسيط في الذاكرة - Simple In-Memory Storage ==============

class InMemoryStorage:
    """
    نظام تخزين بسيط في الذاكرة للأحداث
    Simple in-memory storage for events

    ملاحظة: في الإنتاج، يجب استخدام قاعدة بيانات حقيقية
    Note: In production, use a real database (PostgreSQL, MongoDB, etc.)
    """

    def __init__(self):
        """تهيئة التخزين - Initialize storage"""
        self.events: List[AnalyticsEvent] = []
        self.users: Dict[str, Dict[str, Any]] = {}

    def save_event(self, event: AnalyticsEvent) -> None:
        """
        حفظ حدث - Save event
        """
        self.events.append(event)

    def get_user_events(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[AnalyticsEvent]:
        """
        الحصول على أحداث مستخدم معين - Get user events
        """
        return [
            e for e in self.events
            if e.user_id == user_id and start_date <= e.timestamp <= end_date
        ]

    def get_events_in_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[AnalyticsEvent]:
        """
        الحصول على الأحداث في فترة زمنية - Get events in date range
        """
        return [
            e for e in self.events
            if start_date <= e.timestamp <= end_date
        ]

    def get_feature_events(
        self,
        feature_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[AnalyticsEvent]:
        """
        الحصول على أحداث ميزة معينة - Get feature events
        """
        return [
            e for e in self.events
            if e.metadata.get('feature') == feature_name
            and start_date <= e.timestamp <= end_date
        ]

    def get_total_active_users(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """
        عدد المستخدمين النشطين الإجمالي - Total active users
        """
        events = self.get_events_in_range(start_date, end_date)
        return len(set(e.user_id for e in events))

    def get_cohort_users(self, cohort_period: date) -> List[str]:
        """
        الحصول على مستخدمي فوج معين - Get cohort users
        """
        # البحث عن المستخدمين الذين سجلوا في الفترة المحددة
        # Find users who signed up in the specified period
        start = datetime.combine(cohort_period, datetime.min.time())
        end = start + timedelta(days=30)  # شهر واحد - One month

        signup_events = [
            e for e in self.events
            if e.event_type == EventType.LOGIN
            and start <= e.timestamp <= end
        ]

        return list(set(e.user_id for e in signup_events))


# ============== مصدّر الوحدة - Module Exports ==============

__all__ = [
    "UserAnalyticsService",
    "InMemoryStorage",
]
