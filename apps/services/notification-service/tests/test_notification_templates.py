"""
Tests for src/templates/notification_templates.py - Template System

Covers:
- NotificationTemplate model (to_dict, from_dict)
- NotificationTemplateManager (register, get, render, list)
- Channel-specific formatting (push, SMS, email, WhatsApp)
- Emoji removal
- HTML email generation
- Placeholder rendering
- Global template manager singleton
- render_notification convenience function
"""

import pytest
from src.templates.notification_templates import (
    NotificationChannel,
    NotificationTemplate,
    NotificationTemplateManager,
    TemplateCategory,
    get_template_manager,
    render_notification,
)

# ─────────────────────────────────────────────────────────────────────────────
# TemplateCategory and NotificationChannel Enums
# ─────────────────────────────────────────────────────────────────────────────


class TestEnums:
    def test_template_categories(self):
        assert TemplateCategory.ALERT == "alert"
        assert TemplateCategory.REMINDER == "reminder"
        assert TemplateCategory.REPORT == "report"
        assert TemplateCategory.RECOMMENDATION == "recommendation"

    def test_notification_channels(self):
        assert NotificationChannel.PUSH == "push"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.EMAIL == "email"
        assert NotificationChannel.WHATSAPP == "whatsapp"


# ─────────────────────────────────────────────────────────────────────────────
# NotificationTemplate
# ─────────────────────────────────────────────────────────────────────────────


class TestNotificationTemplate:
    def test_create_template(self):
        template = NotificationTemplate(
            template_id="test-1",
            category=TemplateCategory.ALERT,
            title={"ar": "تنبيه", "en": "Alert"},
            body={"ar": "نص التنبيه", "en": "Alert body"},
        )
        assert template.template_id == "test-1"
        assert template.category == TemplateCategory.ALERT
        assert template.priority == "medium"
        assert template.metadata == {}

    def test_to_dict(self):
        template = NotificationTemplate(
            template_id="test-2",
            category=TemplateCategory.REMINDER,
            title={"ar": "تذكير", "en": "Reminder"},
            body={"ar": "نص", "en": "Body"},
            action_url="https://sahool.app/field/123",
            icon="💧",
            priority="high",
            metadata={"crop": "wheat"},
        )
        data = template.to_dict()
        assert data["template_id"] == "test-2"
        assert data["category"] == "reminder"
        assert data["title"]["ar"] == "تذكير"
        assert data["action_url"] == "https://sahool.app/field/123"
        assert data["icon"] == "💧"
        assert data["priority"] == "high"
        assert data["metadata"] == {"crop": "wheat"}

    def test_from_dict(self):
        data = {
            "template_id": "test-3",
            "category": "alert",
            "title": {"ar": "تنبيه", "en": "Alert"},
            "body": {"ar": "نص", "en": "Body"},
            "action_url": "https://example.com",
            "icon": "⚠️",
            "priority": "critical",
            "metadata": {"key": "value"},
        }
        template = NotificationTemplate.from_dict(data)
        assert template.template_id == "test-3"
        assert template.category == TemplateCategory.ALERT
        assert template.priority == "critical"

    def test_from_dict_defaults(self):
        data = {
            "template_id": "test-4",
            "category": "reminder",
            "title": {"ar": "t"},
            "body": {"ar": "b"},
        }
        template = NotificationTemplate.from_dict(data)
        assert template.action_url is None
        assert template.icon is None
        assert template.priority == "medium"
        assert template.metadata == {}


# ─────────────────────────────────────────────────────────────────────────────
# NotificationTemplateManager
# ─────────────────────────────────────────────────────────────────────────────


class TestNotificationTemplateManager:
    def setup_method(self):
        self.manager = NotificationTemplateManager()
        # Register a test template
        self.test_template = NotificationTemplate(
            template_id="irrigation-reminder",
            category=TemplateCategory.REMINDER,
            title={"ar": "تذكير ري لحقل {field_name}", "en": "Irrigation reminder for {field_name}"},
            body={
                "ar": "حقل {field_name} يحتاج {amount}mm من المياه",
                "en": "Field {field_name} needs {amount}mm of water",
            },
            action_url="https://sahool.app/field/{field_id}",
            icon="💧",
            priority="high",
        )
        self.manager.register_template("irrigation-reminder", self.test_template)

    def test_register_and_get_template(self):
        template = self.manager.get_template("irrigation-reminder")
        assert template is not None
        assert template.template_id == "irrigation-reminder"

    def test_get_nonexistent_template(self):
        template = self.manager.get_template("nonexistent")
        assert template is None

    def test_list_all_templates(self):
        templates = self.manager.list_templates()
        assert "irrigation-reminder" in templates

    def test_list_templates_by_category(self):
        alert_template = NotificationTemplate(
            template_id="pest-alert",
            category=TemplateCategory.ALERT,
            title={"ar": "آفات", "en": "Pest"},
            body={"ar": "نص", "en": "Body"},
        )
        self.manager.register_template("pest-alert", alert_template)

        reminder_templates = self.manager.list_templates(TemplateCategory.REMINDER)
        assert "irrigation-reminder" in reminder_templates
        assert "pest-alert" not in reminder_templates

        alert_templates = self.manager.list_templates(TemplateCategory.ALERT)
        assert "pest-alert" in alert_templates

    def test_render_template_arabic(self):
        result = self.manager.render_template(
            "irrigation-reminder",
            {"field_name": "الحقل الشمالي", "amount": 25, "field_id": "f-123"},
            language="ar",
        )
        assert "الحقل الشمالي" in result["title"]
        assert "25" in result["body"]
        assert result["action_url"] == "https://sahool.app/field/f-123"
        assert result["priority"] == "high"

    def test_render_template_english(self):
        result = self.manager.render_template(
            "irrigation-reminder",
            {"field_name": "North Field", "amount": 30, "field_id": "f-456"},
            language="en",
        )
        assert "North Field" in result["title"]
        assert "30" in result["body"]

    def test_render_nonexistent_template(self):
        result = self.manager.render_template("nonexistent", {}, language="ar")
        assert result["title"] == "إشعار"
        assert result["body"] == "محتوى الإشعار"

    def test_render_nonexistent_template_english(self):
        result = self.manager.render_template("nonexistent", {}, language="en")
        assert result["title"] == "Notification"

    def test_render_with_missing_context_key(self):
        result = self.manager.render_template(
            "irrigation-reminder",
            {"field_name": "Test"},
            language="en",
        )
        # Should do partial replacement without raising
        assert "Test" in result["title"]

    def test_render_with_none_context_values(self):
        result = self.manager.render_template(
            "irrigation-reminder",
            {"field_name": None, "amount": None, "field_id": None},
            language="en",
        )
        # None should be converted to empty string
        assert isinstance(result["title"], str)


# ─────────────────────────────────────────────────────────────────────────────
# Channel-Specific Formatting
# ─────────────────────────────────────────────────────────────────────────────


class TestChannelFormatting:
    def setup_method(self):
        self.manager = NotificationTemplateManager()
        self.template = NotificationTemplate(
            template_id="weather-alert",
            category=TemplateCategory.ALERT,
            title={"ar": "⚠️ تحذير طقس", "en": "⚠️ Weather Warning"},
            body={"ar": "صقيع متوقع في {location}", "en": "Frost expected in {location}"},
            action_url="https://sahool.app/weather/{alert_id}",
            icon="🌡️",
            priority="critical",
        )
        self.manager.register_template("weather-alert", self.template)
        self.context = {"location": "Sana'a", "alert_id": "a-1"}

    def test_format_for_push(self):
        result = self.manager.format_for_push("weather-alert", self.context, language="en")
        assert "title" in result
        assert "body" in result
        assert "data" in result
        assert "notification" in result
        assert result["data"]["template_id"] == "weather-alert"
        assert result["notification"]["sound"] == "default"

    def test_format_for_sms(self):
        result = self.manager.format_for_sms("weather-alert", self.context, language="en")
        assert isinstance(result, str)
        # Emojis should be removed for SMS
        assert "⚠️" not in result
        assert "Sana'a" in result

    def test_format_for_sms_truncation(self):
        result = self.manager.format_for_sms("weather-alert", self.context, language="en", max_length=30)
        assert len(result) <= 30
        assert result.endswith("...")

    def test_format_for_sms_no_truncation_needed(self):
        result = self.manager.format_for_sms("weather-alert", self.context, language="en", max_length=500)
        assert not result.endswith("...")

    def test_format_for_email(self):
        result = self.manager.format_for_email("weather-alert", self.context, language="ar")
        assert "subject" in result
        assert "html_body" in result
        assert "text_body" in result
        assert "rtl" in result["html_body"]
        assert "SAHOOL" in result["html_body"]

    def test_format_for_email_english(self):
        result = self.manager.format_for_email("weather-alert", self.context, language="en")
        assert "ltr" in result["html_body"]

    def test_format_for_email_with_action_url(self):
        result = self.manager.format_for_email("weather-alert", self.context, language="en")
        assert "action_url" in result["text_body"] or "sahool.app" in result["text_body"]

    def test_format_for_whatsapp(self):
        result = self.manager.format_for_whatsapp("weather-alert", self.context, language="ar")
        assert isinstance(result, str)
        # Bold title
        assert result.startswith("*")
        # Footer
        assert "سَهُول" in result

    def test_format_for_whatsapp_english(self):
        result = self.manager.format_for_whatsapp("weather-alert", self.context, language="en")
        assert "SAHOOL - Smart Agriculture" in result

    def test_format_for_whatsapp_with_action_url(self):
        result = self.manager.format_for_whatsapp("weather-alert", self.context, language="en")
        assert "🔗" in result


# ─────────────────────────────────────────────────────────────────────────────
# Helper Methods
# ─────────────────────────────────────────────────────────────────────────────


class TestHelperMethods:
    def test_remove_emojis(self):
        manager = NotificationTemplateManager()
        result = manager._remove_emojis("⚠️ Warning! 🌡️ Hot")
        assert "⚠️" not in result
        assert "🌡️" not in result
        assert "Warning" in result
        assert "Hot" in result

    def test_remove_emojis_no_emojis(self):
        manager = NotificationTemplateManager()
        result = manager._remove_emojis("Normal text")
        assert result == "Normal text"

    def test_remove_emojis_arabic(self):
        manager = NotificationTemplateManager()
        result = manager._remove_emojis("⚠️ تحذير")
        assert "⚠️" not in result
        assert "تحذير" in result

    def test_render_string_empty(self):
        manager = NotificationTemplateManager()
        result = manager._render_string("", {"key": "value"})
        assert result == ""

    def test_render_string_with_placeholders(self):
        manager = NotificationTemplateManager()
        result = manager._render_string("Hello {name}!", {"name": "World"})
        assert result == "Hello World!"

    def test_render_string_missing_key(self):
        manager = NotificationTemplateManager()
        result = manager._render_string("Hello {name}! Your field {field} is ready.", {"name": "Ahmed"})
        assert "Ahmed" in result

    def test_render_string_none_values(self):
        manager = NotificationTemplateManager()
        result = manager._render_string("Hello {name}!", {"name": None})
        assert result == "Hello !"

    def test_create_html_email(self):
        manager = NotificationTemplateManager()
        html = manager._create_html_email(
            title="Test Title",
            body="Test body content",
            action_url="https://sahool.app",
            icon="🌾",
            language="en",
        )
        assert "Test Title" in html
        assert "Test body content" in html
        assert "https://sahool.app" in html
        assert "🌾" in html
        assert 'dir="ltr"' in html

    def test_create_html_email_arabic(self):
        manager = NotificationTemplateManager()
        html = manager._create_html_email(
            title="عنوان",
            body="نص",
            language="ar",
        )
        assert 'dir="rtl"' in html
        assert "عرض التفاصيل" not in html  # No action_url

    def test_create_html_email_without_action_url(self):
        manager = NotificationTemplateManager()
        html = manager._create_html_email(
            title="Title",
            body="Body",
            language="en",
        )
        assert "View Details" not in html

    def test_create_html_email_without_icon(self):
        manager = NotificationTemplateManager()
        html = manager._create_html_email(
            title="Title",
            body="Body",
            language="en",
        )
        assert 'class="icon"' not in html


# ─────────────────────────────────────────────────────────────────────────────
# Global Template Manager & Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────


class TestGlobalFunctions:
    def test_get_template_manager_returns_singleton(self):
        # Reset global to test creation
        import src.templates.notification_templates as mod

        old = mod._template_manager
        mod._template_manager = None
        try:
            manager1 = get_template_manager()
            manager2 = get_template_manager()
            assert manager1 is manager2
        finally:
            mod._template_manager = old

    def test_render_notification_push(self):
        manager = get_template_manager()
        template = NotificationTemplate(
            template_id="test-render",
            category=TemplateCategory.ALERT,
            title={"ar": "عنوان", "en": "Title"},
            body={"ar": "نص", "en": "Body"},
        )
        manager.register_template("test-render", template)

        result = render_notification("test-render", {}, language="en", channel=NotificationChannel.PUSH)
        assert "title" in result
        assert "notification" in result

    def test_render_notification_sms(self):
        manager = get_template_manager()
        template = NotificationTemplate(
            template_id="test-sms",
            category=TemplateCategory.ALERT,
            title={"ar": "عنوان", "en": "Title"},
            body={"ar": "نص", "en": "Body text"},
        )
        manager.register_template("test-sms", template)

        result = render_notification("test-sms", {}, language="en", channel=NotificationChannel.SMS)
        assert isinstance(result, str)
        assert "Title" in result

    def test_render_notification_email(self):
        manager = get_template_manager()
        template = NotificationTemplate(
            template_id="test-email",
            category=TemplateCategory.ALERT,
            title={"ar": "عنوان", "en": "Email Title"},
            body={"ar": "نص", "en": "Email body"},
        )
        manager.register_template("test-email", template)

        result = render_notification("test-email", {}, language="en", channel=NotificationChannel.EMAIL)
        assert "subject" in result
        assert "html_body" in result

    def test_render_notification_whatsapp(self):
        manager = get_template_manager()
        template = NotificationTemplate(
            template_id="test-wa",
            category=TemplateCategory.ALERT,
            title={"ar": "عنوان", "en": "WA Title"},
            body={"ar": "نص", "en": "WA Body"},
        )
        manager.register_template("test-wa", template)

        result = render_notification("test-wa", {}, language="en", channel=NotificationChannel.WHATSAPP)
        assert isinstance(result, str)
        assert "WA Title" in result

    def test_format_for_whatsapp_without_action_url(self):
        manager = NotificationTemplateManager()
        template = NotificationTemplate(
            template_id="no-url",
            category=TemplateCategory.ALERT,
            title={"ar": "عنوان", "en": "Title"},
            body={"ar": "نص", "en": "Body"},
            action_url=None,
        )
        manager.register_template("no-url", template)
        result = manager.format_for_whatsapp("no-url", {}, language="en")
        assert "🔗" not in result

    def test_format_for_email_without_action_url(self):
        manager = NotificationTemplateManager()
        template = NotificationTemplate(
            template_id="no-url-email",
            category=TemplateCategory.ALERT,
            title={"ar": "عنوان", "en": "Title"},
            body={"ar": "نص", "en": "Body"},
            action_url=None,
        )
        manager.register_template("no-url-email", template)
        result = manager.format_for_email("no-url-email", {}, language="en")
        # text_body should not contain action URL
        assert "\n\nNone" not in result["text_body"]
