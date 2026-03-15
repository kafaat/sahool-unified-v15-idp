"""
SAHOOL SMS Client - Twilio Integration
عميل الرسائل النصية عبر Twilio

Features:
- Async Twilio integration
- SMS sending with bilingual support (Arabic/English)
- Retry logic for failed sends
- Environment variable configuration
- Proper error handling and logging
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any

from .security_utils import mask_phone, sanitize_for_log

logger = logging.getLogger(__name__)

# Twilio SDK imports
try:
    from twilio.base.exceptions import TwilioRestException
    from twilio.rest import Client as TwilioClient

    _TWILIO_AVAILABLE = True
except ImportError:
    _TWILIO_AVAILABLE = False
    TwilioClient = None  # type: ignore[misc,assignment]
    TwilioRestException = Exception  # type: ignore[misc,assignment]
    logger.warning("Twilio SDK not installed. Install with: pip install twilio")


@dataclass
class SMSMessage:
    """رسالة نصية - SMS Message"""

    to: str  # Phone number in E.164 format (e.g., +967771234567)
    body: str  # Message content
    body_ar: str | None = None  # Arabic version

    def get_content(self, language: str = "ar") -> str:
        """الحصول على المحتوى بناءً على اللغة"""
        if language == "ar" and self.body_ar:
            return self.body_ar
        return self.body


class SMSClient:
    """
    عميل إرسال الرسائل النصية عبر Twilio

    Example:
        client = SMSClient()
        client.initialize()

        # Send SMS
        await client.send_sms(
            to="+967771234567",
            body="Weather alert: Frost expected tonight",
            body_ar="تنبيه طقس: صقيع متوقع الليلة"
        )
    """

    def __init__(self):
        self._initialized = False
        self._client: TwilioClient | None = None
        self._from_number: str | None = None
        self._account_sid: str | None = None

    def initialize(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_number: str | None = None,
    ) -> bool:
        """
        تهيئة عميل Twilio

        Args:
            account_sid: معرف حساب Twilio
            auth_token: رمز المصادقة
            from_number: رقم الإرسال (E.164 format)

        Returns:
            True if initialization successful
        """
        if not _TWILIO_AVAILABLE:
            logger.error("Twilio SDK not available")
            return False

        if self._initialized:
            logger.info("SMS client already initialized")
            return True

        try:
            # Get credentials from environment if not provided
            if not account_sid:
                account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            if not auth_token:
                auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            if not from_number:
                from_number = os.getenv("TWILIO_FROM_NUMBER")

            # Validate credentials
            if not account_sid or not auth_token:
                logger.error("Twilio credentials not provided")
                return False

            if not from_number:
                logger.error("Twilio from_number not provided")
                return False

            # Initialize Twilio client
            self._client = TwilioClient(account_sid, auth_token)
            self._from_number = from_number
            self._account_sid = account_sid
            self._initialized = True

            logger.info(f"✅ SMS client initialized successfully (from: {from_number})")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize SMS client: {e}")
            return False

    def _check_initialized(self) -> bool:
        """التحقق من التهيئة"""
        if not self._initialized:
            logger.warning("SMS client not initialized. Call initialize() first.")
            return False
        return True

    async def send_sms(
        self,
        to: str,
        body: str,
        body_ar: str | None = None,
        language: str = "ar",
        max_length: int = 1600,  # Twilio SMS limit
    ) -> str | None:
        """
        إرسال رسالة نصية

        Args:
            to: رقم المستلم (E.164 format: +967771234567)
            body: نص الرسالة (English)
            body_ar: نص الرسالة (Arabic)
            language: اللغة المفضلة
            max_length: الحد الأقصى لطول الرسالة

        Returns:
            Message SID if successful, None otherwise
        """
        if not self._check_initialized():
            return None

        try:
            # Validate phone number format
            if not to.startswith("+"):
                logger.warning(f"Phone number {mask_phone(to)} should be in E.164 format (+country_code...)")
                to = f"+{to}"  # Try to fix

            # Select content based on language
            message = SMSMessage(to=to, body=body, body_ar=body_ar)
            content = message.get_content(language)

            # Truncate if too long
            if len(content) > max_length:
                content = content[: max_length - 3] + "..."
                logger.warning(f"SMS content truncated to {max_length} characters")

            # Send SMS via Twilio (async wrapper)
            response = await asyncio.to_thread(self._send_sync, to=to, content=content)

            if response:
                logger.info(f"📱 SMS sent successfully to {mask_phone(to)}: {sanitize_for_log(response)}")
                return response
            else:
                logger.error(f"Failed to send SMS to {mask_phone(to)}")
                return None

        except Exception as e:
            logger.error(f"Error sending SMS to {mask_phone(to)}: {sanitize_for_log(e)}")
            return None

    def _send_sync(self, to: str, content: str) -> str | None:
        """Synchronous send (for thread executor)"""
        try:
            message = self._client.messages.create(body=content, from_=self._from_number, to=to)
            return message.sid
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e.msg} (code: {e.code})")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return None

    async def send_bulk_sms(
        self,
        recipients: list[str],
        body: str,
        body_ar: str | None = None,
        language: str = "ar",
    ) -> dict[str, Any]:
        """
        إرسال رسائل متعددة

        Args:
            recipients: قائمة أرقام المستلمين
            body: نص الرسالة
            body_ar: نص الرسالة بالعربية
            language: اللغة

        Returns:
            Dict with success_count, failure_count, results
        """
        if not self._check_initialized():
            return {"success_count": 0, "failure_count": len(recipients), "results": []}

        results = []
        success_count = 0
        failure_count = 0

        for recipient in recipients:
            result = await self.send_sms(to=recipient, body=body, body_ar=body_ar, language=language)

            if result:
                success_count += 1
                results.append({"to": recipient, "success": True, "sid": result})
            else:
                failure_count += 1
                results.append({"to": recipient, "success": False, "error": "Failed to send"})

        logger.info(
            f"📱 Bulk SMS sent: {success_count} successful, {failure_count} failed out of {len(recipients)} recipients"
        )

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "results": results,
        }

    async def send_sms_with_retry(
        self, to: str, body: str, max_retries: int = 3, retry_delay: int = 5, **kwargs
    ) -> str | None:
        """
        إرسال رسالة مع إعادة المحاولة

        Args:
            to: رقم المستلم
            body: نص الرسالة
            max_retries: عدد المحاولات
            retry_delay: التأخير بين المحاولات (ثواني)
            **kwargs: معاملات إضافية

        Returns:
            Message SID if successful
        """
        for attempt in range(max_retries):
            result = await self.send_sms(to, body, **kwargs)
            if result:
                return result

            if attempt < max_retries - 1:
                logger.warning(f"Retry {attempt + 1}/{max_retries} for {to}...")
                await asyncio.sleep(retry_delay)

        logger.error(f"Failed to send SMS to {to} after {max_retries} attempts")
        return None

    async def get_message_status(self, message_sid: str) -> dict[str, Any] | None:
        """
        الحصول على حالة الرسالة

        Args:
            message_sid: معرف الرسالة من Twilio

        Returns:
            Dict with status information
        """
        if not self._check_initialized():
            return None

        try:
            message = await asyncio.to_thread(self._client.messages(message_sid).fetch)

            return {
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent,
                "error_code": message.error_code,
                "error_message": message.error_message,
            }
        except Exception as e:
            logger.error(f"Failed to fetch message status: {e}")
            return None

    def validate_phone_number(self, phone: str) -> bool:
        """
        التحقق من صحة رقم الهاتف

        Args:
            phone: رقم الهاتف

        Returns:
            True if valid E.164 format
        """
        # Basic validation for E.164 format
        if not phone.startswith("+"):
            return False

        # Remove + and check if remaining is digits
        digits = phone[1:]
        if not digits.isdigit():
            return False

        # Should be between 7 and 15 digits
        return not (len(digits) < 7 or len(digits) > 15)


# Global client instance
_sms_client: SMSClient | None = None


def get_sms_client() -> SMSClient:
    """
    الحصول على instance عام من SMSClient

    Returns:
        SMSClient instance
    """
    global _sms_client

    if _sms_client is None:
        _sms_client = SMSClient()

        # Auto-initialize if credentials available
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_FROM_NUMBER")

        if account_sid and auth_token and from_number:
            _sms_client.initialize()

    return _sms_client
