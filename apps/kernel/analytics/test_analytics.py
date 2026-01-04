"""
اختبار نظام التحليلات - Analytics System Tests
==============================================
اختبارات بسيطة للتحقق من عمل النظام

Simple tests to verify system functionality
"""

import sys
from pathlib import Path

# إضافة المسار للاستيراد - Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.kernel.analytics import (
    EventType,
    Governorate,
    TimePeriod,
    UserAnalyticsService,
)


def test_event_tracking():
    """
    اختبار تتبع الأحداث
    Test event tracking
    """
    print("=" * 70)
    print("اختبار تتبع الأحداث - Testing Event Tracking")
    print("=" * 70)

    analytics = UserAnalyticsService()

    # تتبع حدث - Track event
    event = analytics.track_event(
        user_id="test_user_001",
        event_type=EventType.FIELD_VIEWED,
        field_id="field_test_001",
        governorate=Governorate.SANAA,
        metadata={"test": True},
    )

    assert event.event_id is not None, "Event ID should be generated"
    assert event.user_id == "test_user_001", "User ID should match"
    assert event.event_type == EventType.FIELD_VIEWED, "Event type should match"

    print("✓ تم تتبع الحدث بنجاح - Event tracked successfully")
    print(f"  Event ID: {event.event_id}")
    print(f"  User ID: {event.user_id}")
    print(f"  Event Type: {event.event_type}")
    print()


def test_user_metrics():
    """
    اختبار مقاييس المستخدم
    Test user metrics
    """
    print("=" * 70)
    print("اختبار مقاييس المستخدم - Testing User Metrics")
    print("=" * 70)

    analytics = UserAnalyticsService()

    # إنشاء أحداث تجريبية - Create test events
    user_id = "test_user_002"

    # تسجيل الدخول - Login
    analytics.track_session(user_id, "session_001", "start")

    # عدة أحداث - Multiple events
    analytics.track_event(user_id, EventType.FIELD_VIEWED, field_id="field_001")
    analytics.track_event(user_id, EventType.FIELD_CREATED, field_id="field_002")
    analytics.track_event(
        user_id,
        EventType.RECOMMENDATION_VIEWED,
        metadata={"recommendation_id": "rec_001"},
    )
    analytics.track_event(
        user_id,
        EventType.RECOMMENDATION_APPLIED,
        metadata={"recommendation_id": "rec_001"},
    )
    analytics.track_event(
        user_id, EventType.ALERT_RECEIVED, metadata={"alert_id": "alert_001"}
    )
    analytics.track_event(
        user_id, EventType.ALERT_ACKNOWLEDGED, metadata={"alert_id": "alert_001"}
    )

    # تسجيل الخروج - Logout
    analytics.track_session(user_id, "session_001", "end")

    # الحصول على المقاييس - Get metrics
    metrics = analytics.get_user_engagement(user_id, TimePeriod.DAILY)

    assert metrics.total_events >= 7, "Should have at least 7 events"
    assert metrics.fields_created >= 1, "Should have created at least 1 field"
    assert (
        metrics.recommendation_application_rate == 1.0
    ), "Should have 100% recommendation rate"

    print("✓ تم حساب المقاييس بنجاح - Metrics calculated successfully")
    print(f"  Total Events: {metrics.total_events}")
    print(f"  Fields Created: {metrics.fields_created}")
    print(f"  Recommendations Viewed: {metrics.recommendations_viewed}")
    print(f"  Recommendations Applied: {metrics.recommendations_applied}")
    print(f"  Recommendation Rate: {metrics.recommendation_application_rate:.2%}")
    print(f"  Alerts Received: {metrics.alerts_received}")
    print(f"  Alerts Acknowledged: {metrics.alerts_acknowledged}")
    print(f"  Alert Response Rate: {metrics.alert_response_rate:.2%}")
    print()


def test_general_metrics():
    """
    اختبار المقاييس العامة
    Test general metrics
    """
    print("=" * 70)
    print("اختبار المقاييس العامة - Testing General Metrics")
    print("=" * 70)

    analytics = UserAnalyticsService()

    # إنشاء أحداث لمستخدمين متعددين - Create events for multiple users
    for i in range(5):
        user_id = f"test_user_{i:03d}"
        analytics.track_event(user_id, EventType.LOGIN)
        analytics.track_event(user_id, EventType.FIELD_VIEWED, field_id=f"field_{i}")

    # اختبار المقاييس - Test metrics
    dau = analytics.daily_active_users()
    wau = analytics.weekly_active_users()
    mau = analytics.monthly_active_users()

    assert dau >= 5, "Should have at least 5 daily active users"
    assert wau >= 5, "Should have at least 5 weekly active users"
    assert mau >= 5, "Should have at least 5 monthly active users"

    print("✓ تم حساب المقاييس العامة بنجاح - General metrics calculated successfully")
    print(f"  Daily Active Users: {dau}")
    print(f"  Weekly Active Users: {wau}")
    print(f"  Monthly Active Users: {mau}")
    print()


def test_feature_usage():
    """
    اختبار استخدام الميزات
    Test feature usage
    """
    print("=" * 70)
    print("اختبار استخدام الميزات - Testing Feature Usage")
    print("=" * 70)

    analytics = UserAnalyticsService()

    # إنشاء أحداث لميزة معينة - Create events for a specific feature
    for i in range(10):
        user_id = f"test_user_{i:03d}"
        analytics.track_event(
            user_id, EventType.FIELD_VIEWED, metadata={"feature": "field_management"}
        )

    # الحصول على إحصائيات الميزة - Get feature statistics
    feature_usage = analytics.get_feature_usage("field_management")

    assert feature_usage.total_uses >= 10, "Should have at least 10 uses"

    print("✓ تم حساب استخدام الميزات بنجاح - Feature usage calculated successfully")
    print("  Feature: field_management")
    print(f"  Total Uses: {feature_usage.total_uses}")
    print(f"  Unique Users: {feature_usage.unique_users}")
    print()


def test_farmer_analytics():
    """
    اختبار تحليلات المزارعين
    Test farmer analytics
    """
    print("=" * 70)
    print("اختبار تحليلات المزارعين - Testing Farmer Analytics")
    print("=" * 70)

    analytics = UserAnalyticsService()
    user_id = "farmer_test_001"

    # إنشاء أحداث مزارع - Create farmer events
    analytics.track_event(
        user_id, EventType.CROP_PLANTED, crop_type="tomato", field_id="field_001"
    )
    analytics.track_event(
        user_id, EventType.CROP_PLANTED, crop_type="cucumber", field_id="field_002"
    )

    # التوصيات - Recommendations
    analytics.track_event(
        user_id,
        EventType.RECOMMENDATION_VIEWED,
        metadata={"recommendation_id": "rec_001"},
    )
    analytics.track_event(
        user_id,
        EventType.RECOMMENDATION_APPLIED,
        metadata={"recommendation_id": "rec_001"},
    )

    # اختبار المقاييس - Test metrics
    crops_count = analytics.crops_monitored_count(user_id)
    follow_rate = analytics.recommendation_follow_rate(user_id)

    assert crops_count >= 2, "Should have at least 2 crops"
    assert follow_rate == 1.0, "Should have 100% follow rate"

    print(
        "✓ تم حساب تحليلات المزارعين بنجاح - Farmer analytics calculated successfully"
    )
    print(f"  Crops Monitored: {crops_count}")
    print(f"  Recommendation Follow Rate: {follow_rate:.2%}")
    print()


def test_regional_analytics():
    """
    اختبار التحليلات الإقليمية
    Test regional analytics
    """
    print("=" * 70)
    print("اختبار التحليلات الإقليمية - Testing Regional Analytics")
    print("=" * 70)

    analytics = UserAnalyticsService()

    # إنشاء أحداث لمحافظات مختلفة - Create events for different governorates
    governorates = [Governorate.SANAA, Governorate.TAIZ, Governorate.ADEN]

    for i, gov in enumerate(governorates):
        user_id = f"user_{gov.value}_{i}"
        analytics.track_event(
            user_id, EventType.FIELD_VIEWED, governorate=gov, field_id=f"field_{i}"
        )
        analytics.track_event(
            user_id, EventType.CROP_PLANTED, governorate=gov, crop_type="tomato"
        )

    # اختبار التوزيع الإقليمي - Test regional distribution
    users_by_gov = analytics.users_by_governorate()
    fields_by_region = analytics.active_fields_by_region()
    crop_dist = analytics.crop_distribution()

    assert len(users_by_gov) >= 3, "Should have users in at least 3 governorates"
    assert len(crop_dist) >= 1, "Should have at least 1 crop type"

    print(
        "✓ تم حساب التحليلات الإقليمية بنجاح - Regional analytics calculated successfully"
    )
    print(f"  Users by Governorate: {dict(users_by_gov)}")
    print(f"  Fields by Region: {dict(fields_by_region)}")
    print(f"  Crop Distribution: {crop_dist}")
    print()


def run_all_tests():
    """
    تشغيل جميع الاختبارات
    Run all tests
    """
    print("\n" + "=" * 70)
    print("تشغيل اختبارات نظام التحليلات - Running Analytics System Tests")
    print("=" * 70 + "\n")

    try:
        test_event_tracking()
        test_user_metrics()
        test_general_metrics()
        test_feature_usage()
        test_farmer_analytics()
        test_regional_analytics()

        print("=" * 70)
        print("✓ نجحت جميع الاختبارات - All Tests Passed Successfully")
        print("=" * 70 + "\n")

        return True

    except AssertionError as e:
        print(f"\n✗ فشل الاختبار - Test Failed: {str(e)}\n")
        return False

    except Exception as e:
        print(f"\n✗ خطأ غير متوقع - Unexpected Error: {str(e)}\n")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
