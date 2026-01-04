#!/usr/bin/env python3
"""
Quick Test for SAHOOL Notification Templates
اختبار سريع لقوالب الإشعارات
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from notification_templates import (
    NotificationChannel,
    TemplateCategory,
    get_template_manager,
    render_notification,
)


def test_template_loading():
    """Test 1: Template Loading"""
    print("=" * 80)
    print("Test 1: Loading Templates")
    print("=" * 80)

    manager = get_template_manager()
    templates = manager.list_templates()

    print(f"✓ Loaded {len(templates)} templates")
    print(f"  Templates: {', '.join(templates)}")

    return len(templates) > 0


def test_template_categories():
    """Test 2: Template Categories"""
    print("\n" + "=" * 80)
    print("Test 2: Template Categories")
    print("=" * 80)

    manager = get_template_manager()

    alerts = manager.list_templates(category=TemplateCategory.ALERT)
    reminders = manager.list_templates(category=TemplateCategory.REMINDER)
    reports = manager.list_templates(category=TemplateCategory.REPORT)
    recommendations = manager.list_templates(category=TemplateCategory.RECOMMENDATION)

    print(f"✓ ALERT templates: {len(alerts)} - {alerts}")
    print(f"✓ REMINDER templates: {len(reminders)} - {reminders}")
    print(f"✓ REPORT templates: {len(reports)} - {reports}")
    print(f"✓ RECOMMENDATION templates: {len(recommendations)} - {recommendations}")

    return len(alerts) > 0 and len(reminders) > 0


def test_arabic_rendering():
    """Test 3: Arabic Template Rendering"""
    print("\n" + "=" * 80)
    print("Test 3: Arabic Template Rendering")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "disease_name": "البياض الدقيقي",
        "field_name": "حقل القمح",
        "field_id": "field_123",
        "confidence": 92
    }

    rendered = manager.render_template("disease_detected", context, language="ar")

    print(f"✓ Title: {rendered['title']}")
    print(f"✓ Body: {rendered['body']}")
    print(f"✓ Priority: {rendered['priority']}")

    # Check placeholders were replaced
    assert "{disease_name}" not in rendered['body'], "Placeholder not replaced!"
    assert "البياض الدقيقي" in rendered['body'], "Context value not found!"

    return True


def test_english_rendering():
    """Test 4: English Template Rendering"""
    print("\n" + "=" * 80)
    print("Test 4: English Template Rendering")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "field_name": "Wheat Field North",
        "field_id": "field_456",
        "water_amount": 5000
    }

    rendered = manager.render_template("irrigation_reminder", context, language="en")

    print(f"✓ Title: {rendered['title']}")
    print(f"✓ Body: {rendered['body']}")

    assert "Wheat Field North" in rendered['body']
    assert "5000" in rendered['body']

    return True


def test_push_formatting():
    """Test 5: Push Notification Formatting"""
    print("\n" + "=" * 80)
    print("Test 5: Push Notification Formatting")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "crop_type": "القمح",
        "field_name": "الحقل الأول",
        "field_id": "field_789",
        "estimated_yield": 2500,
        "days_remaining": 3
    }

    push = manager.format_for_push("harvest_ready", context, language="ar")

    print(f"✓ Notification Title: {push['notification']['title']}")
    print(f"✓ Notification Body: {push['notification']['body']}")
    print(f"✓ Icon: {push['notification']['icon']}")
    print(f"✓ Priority: {push['data']['priority']}")
    print(f"✓ Action URL: {push['data']['action_url']}")

    assert 'notification' in push
    assert 'data' in push
    assert push['notification']['icon'] == "🌾"

    return True


def test_sms_formatting():
    """Test 6: SMS Formatting"""
    print("\n" + "=" * 80)
    print("Test 6: SMS Formatting (160 char limit)")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "disease_name": "البياض الدقيقي",
        "field_name": "حقل القمح الشمالي",
        "field_id": "field_123",
        "confidence": 92
    }

    sms = manager.format_for_sms("disease_detected", context, language="ar", max_length=160)

    print(f"✓ SMS Text ({len(sms)} chars): {sms}")

    assert len(sms) <= 160, f"SMS too long! {len(sms)} chars"
    # Check no emojis (most should be removed)
    assert "🦠" not in sms, "Emoji should be removed from SMS"

    return True


def test_email_formatting():
    """Test 7: Email HTML Formatting"""
    print("\n" + "=" * 80)
    print("Test 7: Email HTML Formatting")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "field_name": "حقل الطماطم",
        "field_id": "field_456",
        "water_amount": 5000
    }

    email = manager.format_for_email("irrigation_reminder", context, language="ar")

    print(f"✓ Subject: {email['subject']}")
    print(f"✓ HTML Body length: {len(email['html_body'])} chars")
    print(f"✓ Text Body length: {len(email['text_body'])} chars")

    assert 'subject' in email
    assert 'html_body' in email
    assert 'text_body' in email
    assert '<html' in email['html_body']
    assert 'dir="rtl"' in email['html_body'], "RTL not set for Arabic"

    return True


def test_whatsapp_formatting():
    """Test 8: WhatsApp Formatting"""
    print("\n" + "=" * 80)
    print("Test 8: WhatsApp Formatting")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "weather_type": "عاصفة",
        "weather_description": "أمطار غزيرة ورياح قوية",
        "location": "صنعاء",
        "temperature": 18,
        "humidity": 85
    }

    whatsapp = manager.format_for_whatsapp("weather_alert", context, language="ar")

    print(f"✓ WhatsApp Message:\n{whatsapp}")

    assert "*" in whatsapp, "Title should be bold (surrounded by *)"
    assert "سَهُول SAHOOL" in whatsapp, "SAHOOL branding should be present"

    return True


def test_missing_context():
    """Test 9: Missing Context Handling"""
    print("\n" + "=" * 80)
    print("Test 9: Missing Context Value Handling")
    print("=" * 80)

    manager = get_template_manager()

    # Context with missing field
    context = {
        "field_name": "الحقل",
        # Missing water_amount
    }

    rendered = manager.render_template("irrigation_reminder", context, language="ar")

    print(f"✓ Title: {rendered['title']}")
    print(f"✓ Body (with missing context): {rendered['body']}")
    print("  Note: Missing values should be empty or show placeholder")

    return True


def test_convenience_function():
    """Test 10: Convenience Function"""
    print("\n" + "=" * 80)
    print("Test 10: Convenience Function render_notification()")
    print("=" * 80)

    context = {
        "field_name": "حقل الخضروات",
        "field_id": "field_101",
        "water_amount": 3000
    }

    # Test different channels
    push = render_notification("irrigation_reminder", context, "ar", NotificationChannel.PUSH)
    sms = render_notification("irrigation_reminder", context, "ar", NotificationChannel.SMS)

    print(f"✓ Push: {push['notification']['title']}")
    print(f"✓ SMS: {sms[:50]}...")

    return True


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║  SAHOOL Notification Template System - Test Suite                         ║")
    print("║  نظام قوالب الإشعارات - مجموعة الاختبارات                                ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()

    tests = [
        test_template_loading,
        test_template_categories,
        test_arabic_rendering,
        test_english_rendering,
        test_push_formatting,
        test_sms_formatting,
        test_email_formatting,
        test_whatsapp_formatting,
        test_missing_context,
        test_convenience_function
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result, None))
        except Exception as e:
            results.append((test.__name__, False, str(e)))
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY / ملخص الاختبارات")
    print("=" * 80)

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for test_name, result, error in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
        if error:
            print(f"       Error: {error}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed! / جميع الاختبارات نجحت!")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
