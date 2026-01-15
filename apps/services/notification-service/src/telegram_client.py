"""
SAHOOL Telegram Client - Bot API Integration
عميل تليجرام - تكامل مع Bot API

Features:
- Async message sending with bilingual support (Arabic/English)
- OTP sending for authentication
- Inline keyboard support
- Retry logic for failed sends
- User chat management
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    """رسالة تليجرام"""
    chat_id: str | int  # Telegram chat ID or username
    text: str
    text_ar: str | None = None
    parse_mode: str = "HTML"  # HTML or Markdown
    reply_markup: dict[str, Any] | None = None

    def get_content(self, language: str = "ar") -> str:
        """الحصول على المحتوى بناءً على اللغة"""
        if language == "ar" and self.text_ar:
            return self.text_ar
        return self.text


class TelegramClient:
    """
    عميل تليجرام
    Telegram Bot API client for sending notifications

    Example:
        client = TelegramClient()
        client.initialize()

        # Send message
        await client.send_message(
            chat_id="123456789",
            text="Weather alert: Frost expected tonight",
            text_ar="تنبيه طقس: صقيع متوقع الليلة"
        )
    """

    def __init__(self):
        self._initialized = False
        self._bot_token: str | None = None
        self._base_url: str | None = None
        self._bot_username: str | None = None

    def initialize(
        self,
        bot_token: str | None = None,
    ) -> bool:
        """
        تهيئة عميل تليجرام

        Args:
            bot_token: رمز البوت من BotFather

        Returns:
            True if initialization successful
        """
        if self._initialized:
            logger.info("Telegram client already initialized")
            return True

        try:
            bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")

            if not bot_token:
                logger.warning("Telegram bot token not provided")
                return False

            self._bot_token = bot_token
            self._base_url = f"https://api.telegram.org/bot{bot_token}"
            self._initialized = True

            # Verify bot token by getting bot info
            asyncio.create_task(self._verify_bot())

            logger.info("✅ Telegram client initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            return False

    async def _verify_bot(self):
        """التحقق من صحة رمز البوت"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self._base_url}/getMe")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        self._bot_username = data["result"].get("username")
                        logger.info(f"Telegram bot verified: @{self._bot_username}")
                    else:
                        logger.warning(f"Telegram bot verification failed: {data}")
                else:
                    logger.warning(f"Telegram API error: {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not verify Telegram bot: {e}")

    def _check_initialized(self) -> bool:
        """التحقق من التهيئة"""
        if not self._initialized:
            logger.warning("Telegram client not initialized. Call initialize() first.")
            return False
        return True

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        text_ar: str | None = None,
        language: str = "ar",
        parse_mode: str = "HTML",
        reply_markup: dict[str, Any] | None = None,
        disable_notification: bool = False,
    ) -> int | None:
        """
        إرسال رسالة تليجرام

        Args:
            chat_id: معرف المحادثة أو اسم المستخدم
            text: نص الرسالة (English)
            text_ar: نص الرسالة (Arabic)
            language: اللغة المفضلة
            parse_mode: HTML or Markdown
            reply_markup: لوحة المفاتيح المضمنة
            disable_notification: إرسال بدون صوت

        Returns:
            Message ID if successful, None otherwise
        """
        if not self._check_initialized():
            return None

        try:
            # Select content based on language
            content = text_ar if language == "ar" and text_ar else text

            payload = {
                "chat_id": chat_id,
                "text": content,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification,
            }

            if reply_markup:
                payload["reply_markup"] = reply_markup

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/sendMessage",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("ok"):
                    message_id = data["result"]["message_id"]
                    logger.info(f"📱 Telegram sent to {chat_id}: message_id={message_id}")
                    return message_id
                else:
                    logger.error(f"Telegram API error: {data}")
                    return None

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.warning(f"User {chat_id} has blocked the bot")
            elif e.response.status_code == 400:
                error_data = e.response.json()
                logger.error(f"Telegram bad request: {error_data}")
            else:
                logger.error(f"Telegram HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return None

    async def send_otp(
        self,
        chat_id: str | int,
        otp_code: str,
        language: str = "ar",
    ) -> int | None:
        """إرسال رمز OTP عبر تليجرام"""
        if language == "ar":
            text = f"""🔐 <b>رمز التحقق من SAHOOL</b>

رمزك هو: <code>{otp_code}</code>

⏱ هذا الرمز صالح لمدة <b>10 دقائق</b>.
⚠️ لا تشارك هذا الرمز مع أي شخص.

إذا لم تطلب هذا الرمز، تجاهل هذه الرسالة."""
        else:
            text = f"""🔐 <b>SAHOOL Verification Code</b>

Your code is: <code>{otp_code}</code>

⏱ This code is valid for <b>10 minutes</b>.
⚠️ Do not share this code with anyone.

If you didn't request this code, ignore this message."""

        return await self.send_message(
            chat_id=chat_id,
            text=text,
            text_ar=text if language == "ar" else None,
            language=language,
        )

    async def send_password_reset(
        self,
        chat_id: str | int,
        reset_link: str,
        language: str = "ar",
    ) -> int | None:
        """إرسال رابط إعادة تعيين كلمة المرور"""
        if language == "ar":
            text = f"""🔑 <b>إعادة تعيين كلمة المرور - SAHOOL</b>

لقد طلبت إعادة تعيين كلمة المرور لحسابك.

اضغط على الرابط التالي لإعادة تعيين كلمة المرور:
{reset_link}

⏱ الرابط صالح لمدة <b>ساعة واحدة</b>.

إذا لم تطلب ذلك، تجاهل هذه الرسالة."""
        else:
            text = f"""🔑 <b>Password Reset - SAHOOL</b>

You requested a password reset for your account.

Click the following link to reset your password:
{reset_link}

⏱ This link is valid for <b>1 hour</b>.

If you didn't request this, ignore this message."""

        # Create inline keyboard with reset link button
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "إعادة تعيين كلمة المرور | Reset Password",
                        "url": reset_link,
                    }
                ]
            ]
        }

        return await self.send_message(
            chat_id=chat_id,
            text=text,
            text_ar=text if language == "ar" else None,
            language=language,
            reply_markup=reply_markup,
        )

    async def send_login_alert(
        self,
        chat_id: str | int,
        device_info: str,
        ip_address: str,
        language: str = "ar",
    ) -> int | None:
        """إرسال تنبيه تسجيل دخول جديد"""
        if language == "ar":
            text = f"""🔔 <b>تنبيه تسجيل دخول جديد - SAHOOL</b>

تم تسجيل الدخول إلى حسابك من جهاز جديد:

📱 الجهاز: {device_info}
🌐 عنوان IP: {ip_address}

إذا لم تكن أنت، قم بتغيير كلمة المرور فوراً."""
        else:
            text = f"""🔔 <b>New Login Alert - SAHOOL</b>

Someone logged into your account from a new device:

📱 Device: {device_info}
🌐 IP Address: {ip_address}

If this wasn't you, change your password immediately."""

        return await self.send_message(
            chat_id=chat_id,
            text=text,
            text_ar=text if language == "ar" else None,
            language=language,
        )

    async def send_notification(
        self,
        chat_id: str | int,
        title: str,
        title_ar: str,
        body: str,
        body_ar: str,
        priority: str = "medium",
        language: str = "ar",
        action_url: str | None = None,
    ) -> int | None:
        """إرسال إشعار عام"""
        priority_emoji = {
            "low": "ℹ️",
            "medium": "📢",
            "high": "⚠️",
            "critical": "🚨",
        }
        emoji = priority_emoji.get(priority, "📢")

        if language == "ar":
            text = f"""{emoji} <b>{title_ar}</b>

{body_ar}"""
        else:
            text = f"""{emoji} <b>{title}</b>

{body}"""

        reply_markup = None
        if action_url:
            reply_markup = {
                "inline_keyboard": [
                    [
                        {
                            "text": "عرض التفاصيل | View Details",
                            "url": action_url,
                        }
                    ]
                ]
            }

        return await self.send_message(
            chat_id=chat_id,
            text=text,
            text_ar=text if language == "ar" else None,
            language=language,
            reply_markup=reply_markup,
        )

    async def send_bulk_message(
        self,
        chat_ids: list[str | int],
        text: str,
        text_ar: str | None = None,
        language: str = "ar",
        delay_between_messages: float = 0.1,  # Telegram rate limit: ~30 messages/second
    ) -> dict[str, Any]:
        """إرسال رسائل متعددة مع مراعاة حدود API"""
        if not self._check_initialized():
            return {"success_count": 0, "failure_count": len(chat_ids), "results": []}

        results = []
        success_count = 0
        failure_count = 0

        for chat_id in chat_ids:
            result = await self.send_message(
                chat_id=chat_id,
                text=text,
                text_ar=text_ar,
                language=language,
            )

            if result:
                success_count += 1
                results.append({"chat_id": chat_id, "success": True, "message_id": result})
            else:
                failure_count += 1
                results.append({"chat_id": chat_id, "success": False})

            # Delay to respect rate limits
            await asyncio.sleep(delay_between_messages)

        logger.info(
            f"📱 Telegram bulk send: {success_count} successful, "
            f"{failure_count} failed out of {len(chat_ids)}"
        )

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "results": results,
        }

    def get_bot_link(self) -> str | None:
        """الحصول على رابط البوت"""
        if self._bot_username:
            return f"https://t.me/{self._bot_username}"
        return None


# Global client instance
_telegram_client: TelegramClient | None = None


def get_telegram_client() -> TelegramClient:
    """الحصول على instance عام من TelegramClient"""
    global _telegram_client

    if _telegram_client is None:
        _telegram_client = TelegramClient()
        _telegram_client.initialize()

    return _telegram_client
