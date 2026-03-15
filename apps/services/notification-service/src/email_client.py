"""
SAHOOL Email Client - SendGrid Integration
عميل البريد الإلكتروني عبر SendGrid

Features:
- Async SendGrid integration
- Email sending with bilingual support (Arabic/English)
- HTML and plain text support
- Template support
- Retry logic for failed sends
- Environment variable configuration
- Proper error handling and logging
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any

from .security_utils import mask_email, sanitize_for_log

logger = logging.getLogger(__name__)

# SendGrid SDK imports
try:
    from python_http_client.exceptions import HTTPError
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import (
        Attachment,
        Content,
        Disposition,
        Email,
        FileContent,
        FileName,
        FileType,
        Mail,
        Personalization,
        Subject,
        To,
    )

    _SENDGRID_AVAILABLE = True
except ImportError:
    _SENDGRID_AVAILABLE = False
    SendGridAPIClient = None  # type: ignore[misc,assignment]
    Mail = None  # type: ignore[misc,assignment]
    Email = None  # type: ignore[misc,assignment]
    Content = None  # type: ignore[misc,assignment]
    Subject = None  # type: ignore[misc,assignment]
    To = None  # type: ignore[misc,assignment]
    Personalization = None  # type: ignore[misc,assignment]
    Attachment = None  # type: ignore[misc,assignment]
    FileContent = None  # type: ignore[misc,assignment]
    FileName = None  # type: ignore[misc,assignment]
    FileType = None  # type: ignore[misc,assignment]
    Disposition = None  # type: ignore[misc,assignment]
    HTTPError = Exception  # type: ignore[misc,assignment]
    logger.warning("SendGrid SDK not installed. Install with: pip install sendgrid")


@dataclass
class EmailMessage:
    """رسالة بريد إلكتروني - Email Message"""

    to: str  # Recipient email
    subject: str  # Subject line
    body: str  # Plain text or HTML content
    subject_ar: str | None = None  # Arabic subject
    body_ar: str | None = None  # Arabic body
    is_html: bool = True  # Whether body contains HTML

    def get_subject(self, language: str = "ar") -> str:
        """الحصول على العنوان بناءً على اللغة"""
        if language == "ar" and self.subject_ar:
            return self.subject_ar
        return self.subject

    def get_body(self, language: str = "ar") -> str:
        """الحصول على المحتوى بناءً على اللغة"""
        if language == "ar" and self.body_ar:
            return self.body_ar
        return self.body


class EmailClient:
    """
    عميل إرسال البريد الإلكتروني عبر SendGrid

    Example:
        client = EmailClient()
        client.initialize()

        # Send email
        await client.send_email(
            to="farmer@example.com",
            subject="Weather Alert",
            subject_ar="تنبيه طقس",
            body="<h1>Frost Warning</h1><p>Frost expected tonight</p>",
            body_ar="<h1>تحذير من الصقيع</h1><p>صقيع متوقع الليلة</p>"
        )
    """

    def __init__(self):
        self._initialized = False
        self._client: SendGridAPIClient | None = None
        self._from_email: str | None = None
        self._from_name: str | None = None

    def initialize(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> bool:
        """
        تهيئة عميل SendGrid

        Args:
            api_key: مفتاح API من SendGrid
            from_email: البريد الإلكتروني للمرسل
            from_name: اسم المرسل

        Returns:
            True if initialization successful
        """
        if not _SENDGRID_AVAILABLE:
            logger.error("SendGrid SDK not available")
            return False

        if self._initialized:
            logger.info("Email client already initialized")
            return True

        try:
            # Get credentials from environment if not provided
            if not api_key:
                api_key = os.getenv("SENDGRID_API_KEY")
            if not from_email:
                from_email = os.getenv("SENDGRID_FROM_EMAIL")
            if not from_name:
                from_name = os.getenv("SENDGRID_FROM_NAME", "SAHOOL Agriculture Platform")

            # Validate credentials
            if not api_key:
                logger.error("SendGrid API key not provided")
                return False

            if not from_email:
                logger.error("SendGrid from_email not provided")
                return False

            # Initialize SendGrid client
            self._client = SendGridAPIClient(api_key)
            self._from_email = from_email
            self._from_name = from_name
            self._initialized = True

            logger.info(
                f"✅ Email client initialized successfully (from: ***@{from_email.split('@')[-1] if from_email and '@' in from_email else '***'})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Email client: {e}")
            return False

    def _check_initialized(self) -> bool:
        """التحقق من التهيئة"""
        if not self._initialized:
            logger.warning("Email client not initialized. Call initialize() first.")
            return False
        return True

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        subject_ar: str | None = None,
        body_ar: str | None = None,
        language: str = "ar",
        is_html: bool = True,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[dict[str, str]] | None = None,
    ) -> str | None:
        """
        إرسال بريد إلكتروني

        Args:
            to: البريد الإلكتروني للمستلم
            subject: عنوان البريد (English)
            body: محتوى البريد (English)
            subject_ar: عنوان البريد (Arabic)
            body_ar: محتوى البريد (Arabic)
            language: اللغة المفضلة
            is_html: هل المحتوى HTML
            cc: قائمة CC
            bcc: قائمة BCC
            attachments: قائمة المرفقات

        Returns:
            Message ID if successful, None otherwise
        """
        if not self._check_initialized():
            return None

        try:
            # Validate email
            if not self._validate_email(to):
                logger.error(f"Invalid email address: {mask_email(to)}")
                return None

            # Select content based on language
            message = EmailMessage(
                to=to,
                subject=subject,
                body=body,
                subject_ar=subject_ar,
                body_ar=body_ar,
                is_html=is_html,
            )

            email_subject = message.get_subject(language)
            email_body = message.get_body(language)

            # Build email
            mail = Mail(
                from_email=Email(self._from_email, self._from_name),
                to_emails=To(to),
                subject=Subject(email_subject),
                plain_text_content=(Content("text/plain", email_body) if not is_html else None),
                html_content=Content("text/html", email_body) if is_html else None,
            )

            # Add CC
            if cc:
                personalization = Personalization()
                personalization.add_to(Email(to))
                for cc_email in cc:
                    personalization.add_cc(Email(cc_email))
                mail.add_personalization(personalization)

            # Add BCC
            if bcc:
                if not cc:  # Need personalization
                    personalization = Personalization()
                    personalization.add_to(Email(to))
                for bcc_email in bcc:
                    personalization.add_bcc(Email(bcc_email))
                if not cc:
                    mail.add_personalization(personalization)

            # Add attachments
            if attachments:
                for attachment_data in attachments:
                    attachment = Attachment(
                        FileContent(attachment_data.get("content")),
                        FileName(attachment_data.get("filename")),
                        FileType(attachment_data.get("type", "application/octet-stream")),
                        Disposition(attachment_data.get("disposition", "attachment")),
                    )
                    mail.add_attachment(attachment)

            # Send email via SendGrid (async wrapper)
            response = await asyncio.to_thread(self._send_sync, mail=mail)

            if response:
                logger.info(f"📧 Email sent successfully to {mask_email(to)}: {sanitize_for_log(response)}")
                return response
            else:
                logger.error(f"Failed to send email to {mask_email(to)}")
                return None

        except Exception as e:
            logger.error(f"Error sending email to {mask_email(to)}: {sanitize_for_log(e)}")
            return None

    def _send_sync(self, mail: Mail) -> str | None:
        """Synchronous send (for thread executor)"""
        try:
            response = self._client.send(mail)

            # Check response status
            if response.status_code >= 200 and response.status_code < 300:
                # Extract message ID from headers
                message_id = response.headers.get("X-Message-Id", "unknown")
                return message_id
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return None

        except HTTPError as e:
            logger.error(f"SendGrid HTTP error: {e.to_dict}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return None

    async def send_bulk_email(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        subject_ar: str | None = None,
        body_ar: str | None = None,
        language: str = "ar",
        is_html: bool = True,
    ) -> dict[str, Any]:
        """
        إرسال بريد متعدد

        Args:
            recipients: قائمة البريد الإلكتروني للمستلمين
            subject: عنوان البريد
            body: محتوى البريد
            subject_ar: عنوان البريد بالعربية
            body_ar: محتوى البريد بالعربية
            language: اللغة
            is_html: هل المحتوى HTML

        Returns:
            Dict with success_count, failure_count, results
        """
        if not self._check_initialized():
            return {"success_count": 0, "failure_count": len(recipients), "results": []}

        results = []
        success_count = 0
        failure_count = 0

        for recipient in recipients:
            result = await self.send_email(
                to=recipient,
                subject=subject,
                body=body,
                subject_ar=subject_ar,
                body_ar=body_ar,
                language=language,
                is_html=is_html,
            )

            if result:
                success_count += 1
                results.append({"to": recipient, "success": True, "message_id": result})
            else:
                failure_count += 1
                results.append({"to": recipient, "success": False, "error": "Failed to send"})

        logger.info(
            f"📧 Bulk email sent: {success_count} successful, "
            f"{failure_count} failed out of {len(recipients)} recipients"
        )

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "results": results,
        }

    async def send_email_with_retry(
        self,
        to: str,
        subject: str,
        body: str,
        max_retries: int = 3,
        retry_delay: int = 5,
        **kwargs,
    ) -> str | None:
        """
        إرسال بريد مع إعادة المحاولة

        Args:
            to: البريد الإلكتروني للمستلم
            subject: عنوان البريد
            body: محتوى البريد
            max_retries: عدد المحاولات
            retry_delay: التأخير بين المحاولات (ثواني)
            **kwargs: معاملات إضافية

        Returns:
            Message ID if successful
        """
        for attempt in range(max_retries):
            result = await self.send_email(to, subject, body, **kwargs)
            if result:
                return result

            if attempt < max_retries - 1:
                # Mask email for safe logging
                masked = f"***@{to.split('@')[-1]}" if to and "@" in to else "***"
                logger.warning(f"Retry {attempt + 1}/{max_retries} for {masked}...")
                await asyncio.sleep(retry_delay)

        # Mask email for safe logging
        masked = f"***@{to.split('@')[-1]}" if to and "@" in to else "***"
        logger.error(f"Failed to send email to {masked} after {max_retries} attempts")
        return None

    async def send_template_email(
        self,
        to: str,
        template_id: str,
        template_data: dict[str, Any],
        language: str = "ar",
    ) -> str | None:
        """
        إرسال بريد باستخدام قالب SendGrid

        Args:
            to: البريد الإلكتروني للمستلم
            template_id: معرف القالب في SendGrid
            template_data: بيانات القالب
            language: اللغة

        Returns:
            Message ID if successful
        """
        if not self._check_initialized():
            return None

        try:
            # Build email with template
            mail = Mail(from_email=Email(self._from_email, self._from_name), to_emails=To(to))

            # Set template ID
            mail.template_id = template_id

            # Add dynamic template data
            personalization = Personalization()
            personalization.add_to(Email(to))
            for key, value in template_data.items():
                personalization.add_dynamic_template_data(key, value)

            # Add language
            personalization.add_dynamic_template_data("language", language)

            mail.add_personalization(personalization)

            # Send email
            response = await asyncio.to_thread(self._send_sync, mail=mail)

            # Mask email for safe logging
            masked = f"***@{to.split('@')[-1]}" if to and "@" in to else "***"

            if response:
                logger.info(f"📧 Template email sent to {masked}: {response}")
                return response
            else:
                logger.error(f"Failed to send template email to {masked}")
                return None

        except Exception as e:
            # Mask email for safe logging
            masked = f"***@{to.split('@')[-1]}" if to and "@" in to else "***"
            logger.error(f"Error sending template email to {masked}: {e}")
            return None

    def _validate_email(self, email: str) -> bool:
        """
        التحقق من صحة البريد الإلكتروني

        Args:
            email: البريد الإلكتروني

        Returns:
            True if valid format
        """
        # Basic validation
        if "@" not in email:
            return False

        parts = email.split("@")
        if len(parts) != 2:
            return False

        local, domain = parts
        if not local or not domain:
            return False

        return "." in domain


# Global client instance
_email_client: EmailClient | None = None


def get_email_client() -> EmailClient:
    """
    الحصول على instance عام من EmailClient

    Returns:
        EmailClient instance
    """
    global _email_client

    if _email_client is None:
        _email_client = EmailClient()

        # Auto-initialize if credentials available
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL")
        from_name = os.getenv("SENDGRID_FROM_NAME")

        if api_key and from_email:
            _email_client.initialize(from_name=from_name)

    return _email_client
