"""
SAHOOL Notification Templating System
نظام قوالب الإشعارات

Advanced notification template manager with bilingual support, channel-specific formatting,
and comprehensive template categories for Yemen's agricultural context.
"""

import json
import os
import re
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TemplateCategory(str, Enum):
    """فئات القوالب - Template Categories"""
    ALERT = "alert"  # تنبيهات عاجلة
    REMINDER = "reminder"  # تذكيرات
    REPORT = "report"  # تقارير
    RECOMMENDATION = "recommendation"  # توصيات


class NotificationChannel(str, Enum):
    """قنوات الإشعارات - Notification Channels"""
    PUSH = "push"  # إشعار دفع
    SMS = "sms"  # رسالة نصية
    EMAIL = "email"  # بريد إلكتروني
    WHATSAPP = "whatsapp"  # واتساب


class NotificationTemplate:
    """
    قالب إشعار - Notification Template

    Represents a single notification template with support for multiple languages
    and channel-specific formatting.
    """

    def __init__(
        self,
        template_id: str,
        category: TemplateCategory,
        title: Dict[str, str],
        body: Dict[str, str],
        action_url: Optional[str] = None,
        icon: Optional[str] = None,
        priority: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.template_id = template_id
        self.category = category
        self.title = title  # {"ar": "...", "en": "..."}
        self.body = body  # {"ar": "...", "en": "..."}
        self.action_url = action_url
        self.icon = icon
        self.priority = priority
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """تحويل القالب إلى قاموس"""
        return {
            "template_id": self.template_id,
            "category": self.category,
            "title": self.title,
            "body": self.body,
            "action_url": self.action_url,
            "icon": self.icon,
            "priority": self.priority,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationTemplate":
        """إنشاء قالب من قاموس"""
        return cls(
            template_id=data["template_id"],
            category=TemplateCategory(data["category"]),
            title=data["title"],
            body=data["body"],
            action_url=data.get("action_url"),
            icon=data.get("icon"),
            priority=data.get("priority", "medium"),
            metadata=data.get("metadata", {})
        )


class NotificationTemplateManager:
    """
    مدير قوالب الإشعارات - Notification Template Manager

    Manages notification templates with support for:
    - Bilingual templates (Arabic/English)
    - Template registration and retrieval
    - Context-based rendering with placeholders
    - Channel-specific formatting (Push, SMS, Email, WhatsApp)
    - Template categories (Alert, Reminder, Report, Recommendation)
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template manager

        Args:
            templates_dir: مسار دليل القوالب (optional)
        """
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Default to templates directory relative to this file
            self.templates_dir = Path(__file__).parent

        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        """تحميل القوالب من ملفات JSON"""
        try:
            # Load Arabic templates
            ar_dir = self.templates_dir / "ar"
            if ar_dir.exists():
                for template_file in ar_dir.glob("*.json"):
                    try:
                        with open(template_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                            # Load corresponding English template if exists
                            en_file = self.templates_dir / "en" / template_file.name
                            en_data = {}
                            if en_file.exists():
                                with open(en_file, 'r', encoding='utf-8') as ef:
                                    en_data = json.load(ef)

                            # Register template
                            self._register_from_json(data, en_data)
                    except Exception as e:
                        logger.error(f"Error loading template {template_file}: {e}")

            logger.info(f"Loaded {len(self.templates)} notification templates")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")

    def _register_from_json(self, ar_data: Dict, en_data: Dict):
        """تسجيل قالب من بيانات JSON"""
        template_id = ar_data.get("template_id")
        if not template_id:
            return

        template = NotificationTemplate(
            template_id=template_id,
            category=TemplateCategory(ar_data.get("category", "alert")),
            title={
                "ar": ar_data.get("title", ""),
                "en": en_data.get("title", ar_data.get("title", ""))
            },
            body={
                "ar": ar_data.get("body", ""),
                "en": en_data.get("body", ar_data.get("body", ""))
            },
            action_url=ar_data.get("action_url"),
            icon=ar_data.get("icon"),
            priority=ar_data.get("priority", "medium"),
            metadata=ar_data.get("metadata", {})
        )

        self.templates[template_id] = template

    def get_template(
        self,
        template_id: str,
        language: str = 'ar'
    ) -> Optional[NotificationTemplate]:
        """
        الحصول على قالب

        Args:
            template_id: معرف القالب
            language: اللغة (ar أو en)

        Returns:
            NotificationTemplate أو None
        """
        return self.templates.get(template_id)

    def render_template(
        self,
        template_id: str,
        context: Dict[str, Any],
        language: str = 'ar'
    ) -> Dict[str, str]:
        """
        عرض قالب مع السياق

        Args:
            template_id: معرف القالب
            context: سياق البيانات للعرض
            language: اللغة (ar أو en)

        Returns:
            Dict مع title و body معروضين
        """
        template = self.get_template(template_id, language)

        if not template:
            logger.warning(f"Template {template_id} not found")
            return {
                "title": "إشعار" if language == "ar" else "Notification",
                "body": "محتوى الإشعار" if language == "ar" else "Notification content"
            }

        # Render title and body with context
        try:
            rendered_title = self._render_string(
                template.title.get(language, template.title.get("ar", "")),
                context
            )
            rendered_body = self._render_string(
                template.body.get(language, template.body.get("ar", "")),
                context
            )

            result = {
                "title": rendered_title,
                "body": rendered_body,
                "action_url": template.action_url,
                "icon": template.icon,
                "priority": template.priority
            }

            # Render action_url if it has placeholders
            if template.action_url:
                result["action_url"] = self._render_string(template.action_url, context)

            return result

        except Exception as e:
            logger.error(f"Error rendering template {template_id}: {e}")
            return {
                "title": template.title.get(language, ""),
                "body": template.body.get(language, "")
            }

    def _render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """
        عرض نص مع السياق

        Replaces placeholders like {field_name}, {crop_type}, etc.
        """
        if not template_str:
            return ""

        # Use str.format() with context
        try:
            # Create a safe context that converts None to empty string
            safe_context = {k: (v if v is not None else "") for k, v in context.items()}
            return template_str.format(**safe_context)
        except KeyError as e:
            # Missing key in context, return template with available replacements
            logger.warning(f"Missing context key: {e}")
            # Do partial replacement
            result = template_str
            for key, value in context.items():
                result = result.replace(f"{{{key}}}", str(value if value is not None else ""))
            return result

    def register_template(
        self,
        template_id: str,
        template: NotificationTemplate
    ):
        """
        تسجيل قالب

        Args:
            template_id: معرف القالب
            template: القالب
        """
        self.templates[template_id] = template
        logger.info(f"Registered template: {template_id}")

    def list_templates(
        self,
        category: Optional[TemplateCategory] = None
    ) -> List[str]:
        """
        قائمة القوالب

        Args:
            category: فئة القوالب (اختياري)

        Returns:
            List of template IDs
        """
        if category:
            return [
                tid for tid, template in self.templates.items()
                if template.category == category
            ]
        return list(self.templates.keys())

    # =========================================================================
    # Channel-Specific Formatting
    # =========================================================================

    def format_for_push(
        self,
        template_id: str,
        context: Dict[str, Any],
        language: str = 'ar'
    ) -> Dict[str, Any]:
        """
        تنسيق للإشعارات الدفعية

        Args:
            template_id: معرف القالب
            context: السياق
            language: اللغة

        Returns:
            Dict formatted for push notifications
        """
        rendered = self.render_template(template_id, context, language)
        template = self.get_template(template_id, language)

        return {
            "title": rendered["title"],
            "body": rendered["body"],
            "data": {
                "action_url": rendered.get("action_url"),
                "template_id": template_id,
                "priority": rendered.get("priority", "medium"),
                **context
            },
            "notification": {
                "title": rendered["title"],
                "body": rendered["body"],
                "icon": rendered.get("icon", "🌾"),
                "sound": "default",
                "badge": 1
            }
        }

    def format_for_sms(
        self,
        template_id: str,
        context: Dict[str, Any],
        language: str = 'ar',
        max_length: int = 160
    ) -> str:
        """
        تنسيق للرسائل النصية (SMS)

        Args:
            template_id: معرف القالب
            context: السياق
            language: اللغة
            max_length: الحد الأقصى للطول (default 160 chars)

        Returns:
            SMS message text (truncated to max_length)
        """
        rendered = self.render_template(template_id, context, language)

        # Combine title and body for SMS
        # Remove emojis for SMS
        title = self._remove_emojis(rendered["title"])
        body = self._remove_emojis(rendered["body"])

        sms_text = f"{title}: {body}"

        # Truncate if too long
        if len(sms_text) > max_length:
            sms_text = sms_text[:max_length - 3] + "..."

        return sms_text

    def format_for_email(
        self,
        template_id: str,
        context: Dict[str, Any],
        language: str = 'ar'
    ) -> Dict[str, str]:
        """
        تنسيق للبريد الإلكتروني (HTML)

        Args:
            template_id: معرف القالب
            context: السياق
            language: اللغة

        Returns:
            Dict with subject, html_body, and text_body
        """
        rendered = self.render_template(template_id, context, language)
        template = self.get_template(template_id, language)

        # Create HTML email
        html_body = self._create_html_email(
            title=rendered["title"],
            body=rendered["body"],
            action_url=rendered.get("action_url"),
            icon=rendered.get("icon"),
            language=language
        )

        # Plain text version
        text_body = f"{rendered['title']}\n\n{rendered['body']}"
        if rendered.get("action_url"):
            text_body += f"\n\n{rendered['action_url']}"

        return {
            "subject": rendered["title"],
            "html_body": html_body,
            "text_body": text_body
        }

    def format_for_whatsapp(
        self,
        template_id: str,
        context: Dict[str, Any],
        language: str = 'ar'
    ) -> str:
        """
        تنسيق لواتساب

        Args:
            template_id: معرف القالب
            context: السياق
            language: اللغة

        Returns:
            WhatsApp message text (with emojis and formatting)
        """
        rendered = self.render_template(template_id, context, language)

        # WhatsApp supports emojis and basic formatting
        whatsapp_text = f"*{rendered['title']}*\n\n{rendered['body']}"

        if rendered.get("action_url"):
            whatsapp_text += f"\n\n🔗 {rendered['action_url']}"

        # Add SAHOOL branding
        footer = "\n\n_سَهُول SAHOOL - الزراعة الذكية_" if language == "ar" else "\n\n_SAHOOL - Smart Agriculture_"
        whatsapp_text += footer

        return whatsapp_text

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _remove_emojis(self, text: str) -> str:
        """إزالة الرموز التعبيرية من النص"""
        # Remove emojis using comprehensive regex
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U0001F900-\U0001F9FF"  # supplemental symbols (includes 🦠)
            u"\U0001FA00-\U0001FA6F"  # chess symbols
            u"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
            u"\U00002702-\U000027B0"  # dingbats
            u"\U000024C2-\U0001F251"
            u"\U0001F780-\U0001F7FF"  # geometric shapes
            u"\U0001F800-\U0001F8FF"  # supplemental arrows-C
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text).strip()

    def _create_html_email(
        self,
        title: str,
        body: str,
        action_url: Optional[str] = None,
        icon: Optional[str] = None,
        language: str = 'ar'
    ) -> str:
        """إنشاء بريد إلكتروني HTML"""
        direction = "rtl" if language == "ar" else "ltr"

        html = f"""
<!DOCTYPE html>
<html dir="{direction}" lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #2e7d32;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .title {{
            color: #2e7d32;
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .body {{
            font-size: 16px;
            margin: 20px 0;
            line-height: 1.8;
        }}
        .action-button {{
            display: inline-block;
            padding: 12px 30px;
            background-color: #2e7d32;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .logo {{
            color: #2e7d32;
            font-weight: bold;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {f'<div class="icon">{icon}</div>' if icon else ''}
            <div class="title">{title}</div>
        </div>
        <div class="body">
            {body.replace(chr(10), '<br>')}
        </div>
        {f'<div style="text-align: center;"><a href="{action_url}" class="action-button">{"عرض التفاصيل" if language == "ar" else "View Details"}</a></div>' if action_url else ''}
        <div class="footer">
            <div class="logo">🌾 سَهُول SAHOOL</div>
            <div>{"الزراعة الذكية لليمن" if language == "ar" else "Smart Agriculture for Yemen"}</div>
        </div>
    </div>
</body>
</html>
        """

        return html.strip()


# =============================================================================
# Global Template Manager Instance
# =============================================================================

# Create a global instance for easy access
_template_manager: Optional[NotificationTemplateManager] = None


def get_template_manager() -> NotificationTemplateManager:
    """الحصول على مدير القوالب العمومي"""
    global _template_manager
    if _template_manager is None:
        _template_manager = NotificationTemplateManager()
    return _template_manager


# =============================================================================
# Convenience Functions
# =============================================================================

def render_notification(
    template_id: str,
    context: Dict[str, Any],
    language: str = 'ar',
    channel: NotificationChannel = NotificationChannel.PUSH
) -> Any:
    """
    عرض إشعار

    Convenience function to render a notification for a specific channel.

    Args:
        template_id: معرف القالب
        context: سياق البيانات
        language: اللغة
        channel: قناة الإشعار

    Returns:
        Formatted notification for the specified channel
    """
    manager = get_template_manager()

    if channel == NotificationChannel.PUSH:
        return manager.format_for_push(template_id, context, language)
    elif channel == NotificationChannel.SMS:
        return manager.format_for_sms(template_id, context, language)
    elif channel == NotificationChannel.EMAIL:
        return manager.format_for_email(template_id, context, language)
    elif channel == NotificationChannel.WHATSAPP:
        return manager.format_for_whatsapp(template_id, context, language)
    else:
        return manager.render_template(template_id, context, language)
