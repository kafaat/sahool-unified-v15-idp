"""
أمثلة استخدام تحليلات SAHOOL - SAHOOL Analytics Usage Examples
================================================================
أمثلة عملية على استخدام نظام التحليلات

Practical examples of using the analytics system
"""

from datetime import date

from analytics import (
    EventType,
    Governorate,
    TimePeriod,
    UserAnalyticsService,
)


def main():
    """
    أمثلة استخدام الخدمة
    Service usage examples
    """

    # ============== 1. إنشاء خدمة التحليلات - Create Analytics Service ==============
    print("=" * 70)
    print("إنشاء خدمة التحليلات - Creating Analytics Service")
    print("=" * 70)

    analytics = UserAnalyticsService()
    print("✓ تم إنشاء خدمة التحليلات بنجاح - Analytics service created successfully\n")

    # ============== 2. تتبع الأحداث - Track Events ==============
    print("=" * 70)
    print("تتبع أحداث المستخدم - Tracking User Events")
    print("=" * 70)

    # تتبع تسجيل دخول مزارع - Track farmer login
    login_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.LOGIN,
        session_id="session_123",
        governorate=Governorate.SANAA,
        metadata={"user_role": "farmer", "device": "mobile"},
    )
    print(f"✓ تم تتبع تسجيل الدخول - Login tracked: {login_event.event_id}")

    # تتبع عرض حقل - Track field view
    field_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.FIELD_VIEWED,
        field_id="field_tomato_001",
        crop_type="tomato",
        governorate=Governorate.SANAA,
        metadata={"field_name": "حقل الطماطم الرئيسي"},
    )
    print(f"✓ تم تتبع عرض الحقل - Field view tracked: {field_event.event_id}")

    # تتبع إنشاء حقل جديد - Track field creation
    create_field_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.FIELD_CREATED,
        field_id="field_cucumber_001",
        crop_type="cucumber",
        governorate=Governorate.SANAA,
        metadata={"field_name": "حقل الخيار", "area_ha": 2.5},
    )
    print(
        f"✓ تم تتبع إنشاء الحقل - Field creation tracked: {create_field_event.event_id}"
    )

    # تتبع عرض توصية - Track recommendation view
    rec_view_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.RECOMMENDATION_VIEWED,
        field_id="field_tomato_001",
        metadata={
            "recommendation_id": "rec_001",
            "recommendation_type": "irrigation",
            "recommendation": "يُنصح بالري اليوم في المساء",
        },
    )
    print(
        f"✓ تم تتبع عرض التوصية - Recommendation view tracked: {rec_view_event.event_id}"
    )

    # تتبع تطبيق توصية - Track recommendation application
    rec_apply_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.RECOMMENDATION_APPLIED,
        field_id="field_tomato_001",
        metadata={
            "recommendation_id": "rec_001",
            "action_taken": "scheduled_irrigation",
        },
    )
    print(
        f"✓ تم تتبع تطبيق التوصية - Recommendation application tracked: {rec_apply_event.event_id}"
    )

    # تتبع استلام تنبيه - Track alert received
    alert_received_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.ALERT_RECEIVED,
        field_id="field_tomato_001",
        metadata={
            "alert_id": "alert_001",
            "alert_type": "high_temperature",
            "message": "درجة الحرارة مرتفعة جداً",
        },
    )
    print(
        f"✓ تم تتبع استلام التنبيه - Alert received tracked: {alert_received_event.event_id}"
    )

    # تتبع الاطلاع على التنبيه - Track alert acknowledgment
    alert_ack_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.ALERT_ACKNOWLEDGED,
        field_id="field_tomato_001",
        metadata={"alert_id": "alert_001", "action_taken": "increased_irrigation"},
    )
    print(
        f"✓ تم تتبع الاطلاع على التنبيه - Alert acknowledgment tracked: {alert_ack_event.event_id}"
    )

    # تتبع إضافة مستشعر - Track sensor addition
    sensor_event = analytics.track_event(
        user_id="farmer_001",
        event_type=EventType.SENSOR_ADDED,
        field_id="field_tomato_001",
        metadata={"sensor_type": "soil_moisture", "sensor_id": "sensor_001"},
    )
    print(
        f"✓ تم تتبع إضافة المستشعر - Sensor addition tracked: {sensor_event.event_id}"
    )

    # تتبع تسجيل الخروج - Track logout
    logout_event = analytics.track_event(
        user_id="farmer_001", event_type=EventType.LOGOUT, session_id="session_123"
    )
    print(f"✓ تم تتبع تسجيل الخروج - Logout tracked: {logout_event.event_id}\n")

    # ============== 3. الحصول على مقاييس التفاعل - Get Engagement Metrics ==============
    print("=" * 70)
    print("حساب مقاييس التفاعل - Calculating Engagement Metrics")
    print("=" * 70)

    # الحصول على مقاييس المستخدم - Get user metrics
    metrics = analytics.get_user_engagement(
        user_id="farmer_001", period=TimePeriod.MONTHLY
    )

    print("\nمقاييس المستخدم farmer_001 - User Metrics for farmer_001:")
    print(f"  • إجمالي الأحداث - Total Events: {metrics.total_events}")
    print(f"  • أيام النشاط - Active Days: {metrics.unique_days_active}")
    print(
        f"  • متوسط مدة الجلسة - Avg Session Duration: {metrics.average_session_duration_minutes:.2f} دقيقة"
    )
    print(f"  • الحقول المنشأة - Fields Created: {metrics.fields_created}")
    print(f"  • الحقول المشاهدة - Fields Viewed: {metrics.fields_viewed}")
    print(
        f"  • التوصيات المشاهدة - Recommendations Viewed: {metrics.recommendations_viewed}"
    )
    print(
        f"  • التوصيات المطبقة - Recommendations Applied: {metrics.recommendations_applied}"
    )
    print(
        f"  • معدل تطبيق التوصيات - Recommendation Rate: {metrics.recommendation_application_rate:.2%}"
    )
    print(f"  • التنبيهات المستلمة - Alerts Received: {metrics.alerts_received}")
    print(
        f"  • التنبيهات المطلع عليها - Alerts Acknowledged: {metrics.alerts_acknowledged}"
    )
    print(
        f"  • معدل الاستجابة للتنبيهات - Alert Response Rate: {metrics.alert_response_rate:.2%}"
    )
    print(f"  • المستشعرات المضافة - Sensors Added: {metrics.sensors_added}")
    print(f"  • استخدام الميزات - Feature Usage: {metrics.feature_usage}")
    print(
        f"  • الميزات الأكثر استخداماً - Most Used Features: {metrics.most_used_features}\n"
    )

    # ============== 4. المقاييس العامة - General Metrics ==============
    print("=" * 70)
    print("المقاييس العامة - General Metrics")
    print("=" * 70)

    # المستخدمون النشطون يومياً - Daily Active Users
    dau = analytics.daily_active_users()
    print(f"  • المستخدمون النشطون اليوم - Daily Active Users: {dau}")

    # المستخدمون النشطون أسبوعياً - Weekly Active Users
    wau = analytics.weekly_active_users()
    print(f"  • المستخدمون النشطون أسبوعياً - Weekly Active Users: {wau}")

    # المستخدمون النشطون شهرياً - Monthly Active Users
    mau = analytics.monthly_active_users()
    print(f"  • المستخدمون النشطون شهرياً - Monthly Active Users: {mau}")

    # متوسط مدة الجلسة - Average Session Duration
    avg_session = analytics.average_session_duration()
    print(f"  • متوسط مدة الجلسة - Average Session Duration: {avg_session:.2f} دقيقة\n")

    # ============== 5. استخدام الميزات - Feature Usage ==============
    print("=" * 70)
    print("إحصائيات استخدام الميزات - Feature Usage Statistics")
    print("=" * 70)

    # استخدام ميزة إدارة الحقول - Field management feature usage
    field_usage = analytics.get_feature_usage("field_management")
    print("\nميزة إدارة الحقول - Field Management Feature:")
    print(f"  • إجمالي الاستخدامات - Total Uses: {field_usage.total_uses}")
    print(f"  • المستخدمون الفريدون - Unique Users: {field_usage.unique_users}")
    print(
        f"  • متوسط الاستخدامات لكل مستخدم - Avg Uses per User: {field_usage.average_uses_per_user:.2f}"
    )
    print(f"  • معدل التبني - Adoption Rate: {field_usage.adoption_rate:.2%}\n")

    # ============== 6. تحليلات المزارعين - Farmer Analytics ==============
    print("=" * 70)
    print("تحليلات المزارعين - Farmer Analytics")
    print("=" * 70)

    # عدد المحاصيل المراقبة - Monitored crops count
    crops_count = analytics.crops_monitored_count("farmer_001")
    print(f"  • المحاصيل المراقبة - Monitored Crops: {crops_count}")

    # معدل اتباع التوصيات - Recommendation follow rate
    follow_rate = analytics.recommendation_follow_rate("farmer_001")
    print(f"  • معدل اتباع التوصيات - Recommendation Follow Rate: {follow_rate:.2%}")

    # وقت الاستجابة للتنبيهات - Alert response time
    response_time = analytics.alerts_response_time("farmer_001")
    if response_time:
        print(
            f"  • متوسط وقت الاستجابة للتنبيهات - Avg Alert Response Time: {response_time:.2f} ساعة\n"
        )
    else:
        print(
            "  • متوسط وقت الاستجابة للتنبيهات - Avg Alert Response Time: لا توجد بيانات كافية\n"
        )

    # ============== 7. التحليلات الإقليمية - Regional Analytics ==============
    print("=" * 70)
    print("التحليلات الإقليمية - Regional Analytics")
    print("=" * 70)

    # المستخدمون حسب المحافظة - Users by governorate
    users_by_gov = analytics.users_by_governorate()
    print("\nالمستخدمون حسب المحافظة - Users by Governorate:")
    for gov, count in users_by_gov.items():
        print(f"  • {gov.value}: {count} مستخدم")

    # الحقول النشطة حسب المنطقة - Active fields by region
    fields_by_region = analytics.active_fields_by_region()
    print("\nالحقول النشطة حسب المنطقة - Active Fields by Region:")
    for gov, count in fields_by_region.items():
        print(f"  • {gov.value}: {count} حقل")

    # توزيع المحاصيل - Crop distribution
    crop_dist = analytics.crop_distribution()
    print("\nتوزيع المحاصيل - Crop Distribution:")
    for crop, count in crop_dist.items():
        print(f"  • {crop}: {count} حقل\n")

    # ============== 8. معدلات الاحتفاظ - Retention Rates ==============
    print("=" * 70)
    print("تحليل معدلات الاحتفاظ - Retention Analysis")
    print("=" * 70)

    # حساب معدل الاحتفاظ للفوج - Calculate cohort retention
    cohort_analysis = analytics.calculate_retention_rate(
        cohort="2024-01", cohort_period=date(2024, 1, 1), days=90
    )

    print(f"\nتحليل الفوج {cohort_analysis.cohort_name} - Cohort Analysis:")
    print(f"  • إجمالي المستخدمين - Total Users: {cohort_analysis.total_users}")
    print(
        f"  • الاحتفاظ في اليوم 1 - Day 1 Retention: {cohort_analysis.retention_day_1:.2%}"
    )
    print(
        f"  • الاحتفاظ في اليوم 7 - Day 7 Retention: {cohort_analysis.retention_day_7:.2%}"
    )
    print(
        f"  • الاحتفاظ في اليوم 30 - Day 30 Retention: {cohort_analysis.retention_day_30:.2%}"
    )
    print(
        f"  • الاحتفاظ في اليوم 90 - Day 90 Retention: {cohort_analysis.retention_day_90:.2%}\n"
    )

    print("=" * 70)
    print("✓ تم إكمال جميع الأمثلة بنجاح - All examples completed successfully")
    print("=" * 70)


def simulate_farmer_activity():
    """
    محاكاة نشاط مزارع كامل ليوم واحد
    Simulate complete farmer activity for one day
    """
    print("\n" + "=" * 70)
    print("محاكاة نشاط مزارع ليوم كامل - Simulating Full Day Farmer Activity")
    print("=" * 70 + "\n")

    analytics = UserAnalyticsService()

    # صباحاً: تسجيل الدخول وفحص الحقول
    # Morning: Login and check fields
    print("صباحاً (8:00 AM) - Morning:")
    analytics.track_session("farmer_002", "session_morning", "start")
    analytics.track_event(
        "farmer_002",
        EventType.FIELD_VIEWED,
        field_id="field_001",
        metadata={"time": "08:00"},
    )
    analytics.track_event(
        "farmer_002",
        EventType.SENSOR_DATA_VIEWED,
        field_id="field_001",
        metadata={"sensor_type": "soil_moisture", "value": 45},
    )
    print("  ✓ فحص حالة الحقل والمستشعرات")

    # استلام تنبيه
    # Receive alert
    analytics.track_event(
        "farmer_002",
        EventType.ALERT_RECEIVED,
        metadata={"alert_id": "alert_morning", "type": "low_moisture"},
    )
    print("  ✓ استلام تنبيه: رطوبة التربة منخفضة")

    # ظهراً: جدولة الري
    # Noon: Schedule irrigation
    print("\nظهراً (12:00 PM) - Noon:")
    analytics.track_event(
        "farmer_002",
        EventType.ALERT_ACKNOWLEDGED,
        metadata={"alert_id": "alert_morning"},
    )
    analytics.track_event(
        "farmer_002",
        EventType.IRRIGATION_SCHEDULED,
        field_id="field_001",
        metadata={"scheduled_time": "18:00", "duration": 60},
    )
    print("  ✓ جدولة الري المسائي")

    # عصراً: عرض التوصيات
    # Afternoon: View recommendations
    print("\nعصراً (3:00 PM) - Afternoon:")
    analytics.track_event(
        "farmer_002",
        EventType.RECOMMENDATION_VIEWED,
        metadata={"recommendation": "تطبيق سماد عضوي"},
    )
    analytics.track_event(
        "farmer_002",
        EventType.RECOMMENDATION_APPLIED,
        metadata={"action": "fertilizer_applied"},
    )
    analytics.track_event(
        "farmer_002",
        EventType.REPORT_GENERATED,
        field_id="field_001",
        metadata={"report_type": "weekly_summary"},
    )
    print("  ✓ تطبيق التوصيات وإنشاء التقرير")

    # مساءً: إكمال الري
    # Evening: Complete irrigation
    print("\nمساءً (7:00 PM) - Evening:")
    analytics.track_event(
        "farmer_002", EventType.IRRIGATION_STARTED, field_id="field_001"
    )
    analytics.track_event(
        "farmer_002",
        EventType.IRRIGATION_COMPLETED,
        field_id="field_001",
        metadata={"water_used_m3": 150},
    )
    analytics.track_session("farmer_002", "session_morning", "end")
    print("  ✓ إكمال الري وتسجيل الخروج")

    # عرض ملخص النشاط
    # Show activity summary
    print("\nملخص نشاط اليوم - Daily Activity Summary:")
    metrics = analytics.get_user_engagement("farmer_002", TimePeriod.DAILY)
    print(f"  • إجمالي الأحداث: {metrics.total_events}")
    print(f"  • التوصيات المطبقة: {metrics.recommendations_applied}")
    print(f"  • التنبيهات المعالجة: {metrics.alerts_acknowledged}")
    print(f"  • أحداث الري: {metrics.irrigation_events_completed}\n")


if __name__ == "__main__":
    # تشغيل الأمثلة الأساسية - Run basic examples
    main()

    # تشغيل محاكاة نشاط المزارع - Run farmer activity simulation
    simulate_farmer_activity()

    print("\n" + "=" * 70)
    print("شكراً لاستخدام نظام تحليلات SAHOOL")
    print("Thank you for using SAHOOL Analytics System")
    print("=" * 70 + "\n")
