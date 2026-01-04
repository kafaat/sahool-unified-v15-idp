"""
SAHOOL Notification Template Usage Examples
أمثلة استخدام قوالب الإشعارات

This file demonstrates how to use the notification templating system.
"""

from notification_templates import TemplateCategory, get_template_manager


def example_disease_detection():
    """مثال: إشعار اكتشاف مرض"""
    print("=" * 80)
    print("Example 1: Disease Detection Notification")
    print("=" * 80)

    manager = get_template_manager()

    # Context data
    context = {
        "disease_name": "البياض الدقيقي",  # Powdery Mildew
        "field_name": "حقل القمح الشمالي",
        "field_id": "field_123",
        "confidence": 92,
    }

    # Render for different channels
    print("\n1. Arabic Push Notification:")
    push_ar = manager.format_for_push("disease_detected", context, language="ar")
    print(f"Title: {push_ar['notification']['title']}")
    print(f"Body: {push_ar['notification']['body']}")
    print(f"Action URL: {push_ar['data']['action_url']}")

    print("\n2. English Push Notification:")
    push_en = manager.format_for_push("disease_detected", context, language="en")
    print(f"Title: {push_en['notification']['title']}")
    print(f"Body: {push_en['notification']['body']}")

    print("\n3. Arabic SMS:")
    sms_ar = manager.format_for_sms("disease_detected", context, language="ar")
    print(f"SMS ({len(sms_ar)} chars): {sms_ar}")

    print("\n4. Arabic WhatsApp:")
    whatsapp_ar = manager.format_for_whatsapp(
        "disease_detected", context, language="ar"
    )
    print(f"WhatsApp:\n{whatsapp_ar}")


def example_irrigation_reminder():
    """مثال: تذكير الري"""
    print("\n" + "=" * 80)
    print("Example 2: Irrigation Reminder")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "field_name": "حقل الطماطم",
        "field_id": "field_456",
        "water_amount": 5000,
    }

    print("\n1. Arabic Push:")
    push = manager.format_for_push("irrigation_reminder", context, language="ar")
    print(f"Title: {push['notification']['title']}")
    print(f"Body: {push['notification']['body']}")

    print("\n2. Email (HTML):")
    email = manager.format_for_email("irrigation_reminder", context, language="ar")
    print(f"Subject: {email['subject']}")
    print(f"HTML Body (first 200 chars):\n{email['html_body'][:200]}...")


def example_harvest_ready():
    """مثال: جاهزية الحصاد"""
    print("\n" + "=" * 80)
    print("Example 3: Harvest Ready Notification")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "crop_type": "القمح",
        "field_name": "الحقل الأول",
        "field_id": "field_789",
        "estimated_yield": 2500,
        "days_remaining": 3,
    }

    # Multi-channel delivery
    print("\n1. Arabic Push:")
    push_ar = manager.format_for_push("harvest_ready", context, language="ar")
    print(f"Title: {push_ar['notification']['title']}")
    print(f"Body: {push_ar['notification']['body']}")

    print("\n2. English SMS:")
    sms_en = manager.format_for_sms(
        "harvest_ready", context, language="en", max_length=160
    )
    print(f"SMS: {sms_en}")


def example_weather_alert():
    """مثال: تنبيه طقس"""
    print("\n" + "=" * 80)
    print("Example 4: Weather Alert")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "weather_type": "عاصفة",
        "weather_description": "أمطار غزيرة ورياح قوية",
        "location": "صنعاء",
        "temperature": 18,
        "humidity": 85,
    }

    print("\n1. Arabic Push:")
    push = manager.format_for_push("weather_alert", context, language="ar")
    print(f"Title: {push['notification']['title']}")
    print(f"Body: {push['notification']['body']}")
    print(f"Priority: {push['data']['priority']}")

    print("\n2. WhatsApp:")
    whatsapp = manager.format_for_whatsapp("weather_alert", context, language="ar")
    print(f"Message:\n{whatsapp}")


def example_ai_recommendation():
    """مثال: توصية ذكاء اصطناعي"""
    print("\n" + "=" * 80)
    print("Example 5: AI Recommendation")
    print("=" * 80)

    manager = get_template_manager()

    context = {
        "recommendation_type": "تحسين الري",
        "field_name": "حقل الخضروات",
        "field_id": "field_101",
        "recommendation_id": "rec_555",
        "recommendation_text": "تقليل كمية الري بنسبة 20% لتحسين جودة المحصول",
        "expected_impact": "تحسين جودة الثمار بنسبة 15%",
        "benefit": "توفير 1000 لتر ماء أسبوعياً",
        "confidence": 88,
    }

    print("\n1. Arabic Push:")
    push = manager.format_for_push("ai_recommendation", context, language="ar")
    print(f"Title: {push['notification']['title']}")
    print(f"Body: {push['notification']['body']}")

    print("\n2. English Email:")
    email = manager.format_for_email("ai_recommendation", context, language="en")
    print(f"Subject: {email['subject']}")


def example_daily_report():
    """مثال: تقرير يومي"""
    print("\n" + "=" * 80)
    print("Example 6: Daily Report")
    print("=" * 80)

    manager = get_template_manager()

    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    context = {
        "date": today,
        "total_fields": 5,
        "healthy_fields": 4,
        "tasks_pending": 3,
        "max_temp": 28,
        "rain_probability": 15,
    }

    print("\n1. Arabic Push:")
    push = manager.format_for_push("daily_report", context, language="ar")
    print(f"Title: {push['notification']['title']}")
    print(f"Body: {push['notification']['body']}")


def example_list_templates():
    """مثال: قائمة القوالب"""
    print("\n" + "=" * 80)
    print("Example 7: List Available Templates")
    print("=" * 80)

    manager = get_template_manager()

    print("\nAll Templates:")
    all_templates = manager.list_templates()
    for template_id in all_templates:
        template = manager.get_template(template_id)
        if template:
            print(
                f"  - {template_id} ({template.category.value}): {template.title.get('ar', 'N/A')}"
            )

    print("\nALERT Templates:")
    alerts = manager.list_templates(category=TemplateCategory.ALERT)
    for template_id in alerts:
        template = manager.get_template(template_id)
        print(f"  - {template_id}: {template.title.get('ar', 'N/A')}")

    print("\nREMINDER Templates:")
    reminders = manager.list_templates(category=TemplateCategory.REMINDER)
    for template_id in reminders:
        template = manager.get_template(template_id)
        print(f"  - {template_id}: {template.title.get('ar', 'N/A')}")

    print("\nREPORT Templates:")
    reports = manager.list_templates(category=TemplateCategory.REPORT)
    for template_id in reports:
        template = manager.get_template(template_id)
        print(f"  - {template_id}: {template.title.get('ar', 'N/A')}")

    print("\nRECOMMENDATION Templates:")
    recommendations = manager.list_templates(category=TemplateCategory.RECOMMENDATION)
    for template_id in recommendations:
        template = manager.get_template(template_id)
        print(f"  - {template_id}: {template.title.get('ar', 'N/A')}")


def example_custom_template():
    """مثال: تسجيل قالب مخصص"""
    print("\n" + "=" * 80)
    print("Example 8: Register Custom Template")
    print("=" * 80)

    from notification_templates import NotificationTemplate

    manager = get_template_manager()

    # Create custom template
    custom_template = NotificationTemplate(
        template_id="custom_celebration",
        category=TemplateCategory.REPORT,
        title={"ar": "🎉 تهانينا!", "en": "🎉 Congratulations!"},
        body={
            "ar": "لقد حققت إنجازاً رائعاً في {achievement}! استمر في العمل المتميز.",
            "en": "You've achieved great success in {achievement}! Keep up the excellent work.",
        },
        icon="🎉",
        priority="low",
    )

    # Register it
    manager.register_template("custom_celebration", custom_template)

    # Use it
    context = {"achievement": "زيادة الإنتاج بنسبة 30%"}
    push = manager.format_for_push("custom_celebration", context, language="ar")

    print("Custom Template Registered!")
    print(f"Title: {push['notification']['title']}")
    print(f"Body: {push['notification']['body']}")


def main():
    """تشغيل جميع الأمثلة"""
    print("\n")
    print(
        "╔════════════════════════════════════════════════════════════════════════════╗"
    )
    print(
        "║  SAHOOL Notification Template System - Usage Examples                     ║"
    )
    print(
        "║  نظام قوالب الإشعارات - أمثلة الاستخدام                                  ║"
    )
    print(
        "╚════════════════════════════════════════════════════════════════════════════╝"
    )

    try:
        example_disease_detection()
        example_irrigation_reminder()
        example_harvest_ready()
        example_weather_alert()
        example_ai_recommendation()
        example_daily_report()
        example_list_templates()
        example_custom_template()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
