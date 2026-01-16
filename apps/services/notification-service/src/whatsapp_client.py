"""
SAHOOL WhatsApp Client - Multi-Provider Integration
عميل واتساب - تكامل مع مزودين متعددين

Supports:
- Twilio WhatsApp Business API (External)
- WhatsApp Cloud API (Meta) (External)
- Local providers (e.g., UltraMsg, Wassenger)

Features:
- Async message sending with bilingual support (Arabic/English)
- Template message support
- OTP sending for authentication
- Retry logic for failed sends
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx

from .security_utils import mask_phone, sanitize_for_log

logger = logging.getLogger(__name__)


class WhatsAppProvider(str, Enum):
    """مزودي خدمة واتساب"""
    TWILIO = "twilio"
    META_CLOUD = "meta_cloud"
    ULTRAMSG = "ultramsg"  # Local provider example


@dataclass
class WhatsAppMessage:
    """رسالة واتساب"""
    to: str  # Phone number in E.164 format
    body: str
    body_ar: str | None = None
    template_name: str | None = None
    template_params: dict[str, Any] | None = None

    def get_content(self, language: str = "ar") -> str:
        """الحصول على المحتوى بناءً على اللغة"""
        if language == "ar" and self.body_ar:
            return self.body_ar
        return self.body


class BaseWhatsAppProvider(ABC):
    """قاعدة مزود واتساب"""

    @abstractmethod
    async def send_message(
        self,
        to: str,
        body: str,
        language: str = "ar",
    ) -> str | None:
        """إرسال رسالة"""
        pass

    @abstractmethod
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        template_params: dict[str, Any],
        language: str = "ar",
    ) -> str | None:
        """إرسال رسالة قالب"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """التحقق من توفر المزود"""
        pass


class TwilioWhatsAppProvider(BaseWhatsAppProvider):
    """مزود واتساب Twilio"""

    def __init__(self):
        self._initialized = False
        self._client = None
        self._from_number: str | None = None

    def initialize(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_number: str | None = None,
    ) -> bool:
        """تهيئة Twilio WhatsApp"""
        try:
            from twilio.rest import Client as TwilioClient

            account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
            from_number = from_number or os.getenv("TWILIO_WHATSAPP_NUMBER")

            if not all([account_sid, auth_token, from_number]):
                logger.warning("Twilio WhatsApp credentials not provided")
                return False

            self._client = TwilioClient(account_sid, auth_token)
            self._from_number = from_number
            self._initialized = True
            logger.info(f"✅ Twilio WhatsApp initialized (from: {from_number})")
            return True
        except ImportError:
            logger.warning("Twilio SDK not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Twilio WhatsApp: {e}")
            return False

    def is_available(self) -> bool:
        return self._initialized

    async def send_message(
        self,
        to: str,
        body: str,
        language: str = "ar",
    ) -> str | None:
        if not self._initialized:
            logger.warning("Twilio WhatsApp not initialized")
            return None

        try:
            # Ensure proper WhatsApp format
            whatsapp_to = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
            whatsapp_from = f"whatsapp:{self._from_number}" if not self._from_number.startswith("whatsapp:") else self._from_number

            message = await asyncio.to_thread(
                self._client.messages.create,
                body=body,
                from_=whatsapp_from,
                to=whatsapp_to,
            )
            logger.info(f"✅ WhatsApp sent via Twilio to ***{to[-4:]}: {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Twilio WhatsApp error: {e}")
            return None

    async def send_template_message(
        self,
        to: str,
        template_name: str,
        template_params: dict[str, Any],
        language: str = "ar",
    ) -> str | None:
        # Twilio uses content templates differently
        # For now, fall back to regular message
        template_body = template_params.get("body", "")
        return await self.send_message(to, template_body, language)


class MetaCloudWhatsAppProvider(BaseWhatsAppProvider):
    """مزود واتساب Meta Cloud API"""

    def __init__(self):
        self._initialized = False
        self._access_token: str | None = None
        self._phone_number_id: str | None = None
        self._api_version = "v18.0"

    def initialize(
        self,
        access_token: str | None = None,
        phone_number_id: str | None = None,
    ) -> bool:
        """تهيئة Meta Cloud API"""
        try:
            access_token = access_token or os.getenv("META_WHATSAPP_ACCESS_TOKEN")
            phone_number_id = phone_number_id or os.getenv("META_WHATSAPP_PHONE_NUMBER_ID")

            if not all([access_token, phone_number_id]):
                logger.warning("Meta WhatsApp credentials not provided")
                return False

            self._access_token = access_token
            self._phone_number_id = phone_number_id
            self._initialized = True
            logger.info("✅ Meta Cloud WhatsApp initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Meta WhatsApp: {e}")
            return False

    def is_available(self) -> bool:
        return self._initialized

    async def send_message(
        self,
        to: str,
        body: str,
        language: str = "ar",
    ) -> str | None:
        if not self._initialized:
            logger.warning("Meta WhatsApp not initialized")
            return None

        try:
            # Remove + if present
            phone = to.lstrip("+")

            url = f"https://graph.facebook.com/{self._api_version}/{self._phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone,
                "type": "text",
                "text": {"body": body},
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                message_id = data.get("messages", [{}])[0].get("id")
                logger.info(f"✅ WhatsApp sent via Meta to ***{to[-4:]}: {message_id}")
                return message_id
        except Exception as e:
            logger.error(f"Meta WhatsApp error: {e}")
            return None

    async def send_template_message(
        self,
        to: str,
        template_name: str,
        template_params: dict[str, Any],
        language: str = "ar",
    ) -> str | None:
        if not self._initialized:
            return None

        try:
            phone = to.lstrip("+")
            url = f"https://graph.facebook.com/{self._api_version}/{self._phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }

            # Build template components
            components = []
            if "body_params" in template_params:
                components.append({
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": param}
                        for param in template_params["body_params"]
                    ],
                })

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "ar" if language == "ar" else "en"},
                    "components": components,
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                message_id = data.get("messages", [{}])[0].get("id")
                return message_id
        except Exception as e:
            logger.error(f"Meta WhatsApp template error: {e}")
            return None


class UltraMsgProvider(BaseWhatsAppProvider):
    """مزود واتساب UltraMsg (مزود محلي)"""

    def __init__(self):
        self._initialized = False
        self._instance_id: str | None = None
        self._api_token: str | None = None
        self._base_url = "https://api.ultramsg.com"

    def initialize(
        self,
        instance_id: str | None = None,
        api_token: str | None = None,
    ) -> bool:
        """تهيئة UltraMsg"""
        try:
            instance_id = instance_id or os.getenv("ULTRAMSG_INSTANCE_ID")
            api_token = api_token or os.getenv("ULTRAMSG_API_TOKEN")

            if not all([instance_id, api_token]):
                logger.warning("UltraMsg credentials not provided")
                return False

            self._instance_id = instance_id
            self._api_token = api_token
            self._initialized = True
            logger.info("✅ UltraMsg WhatsApp initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize UltraMsg: {e}")
            return False

    def is_available(self) -> bool:
        return self._initialized

    async def send_message(
        self,
        to: str,
        body: str,
        language: str = "ar",
    ) -> str | None:
        if not self._initialized:
            return None

        try:
            url = f"{self._base_url}/{self._instance_id}/messages/chat"
            payload = {
                "token": self._api_token,
                "to": to,
                "body": body,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload)
                response.raise_for_status()
                data = response.json()
                if data.get("sent") == "true":
                    message_id = data.get("id", "sent")
                    logger.info(f"✅ WhatsApp sent via UltraMsg to ***{to[-4:]}")
                    return message_id
                return None
        except Exception as e:
            logger.error(f"UltraMsg error: {e}")
            return None

    async def send_template_message(
        self,
        to: str,
        template_name: str,
        template_params: dict[str, Any],
        language: str = "ar",
    ) -> str | None:
        # UltraMsg doesn't support templates in the same way
        body = template_params.get("body", "")
        return await self.send_message(to, body, language)


class WhatsAppClient:
    """
    عميل واتساب متعدد المزودين
    Multi-provider WhatsApp client with failover support
    """

    def __init__(self):
        self._providers: dict[WhatsAppProvider, BaseWhatsAppProvider] = {}
        self._primary_provider: WhatsAppProvider | None = None
        self._initialized = False

    def initialize(self) -> bool:
        """تهيئة جميع المزودين المتاحين"""
        providers_initialized = []

        # Try to initialize Twilio
        twilio = TwilioWhatsAppProvider()
        if twilio.initialize():
            self._providers[WhatsAppProvider.TWILIO] = twilio
            providers_initialized.append(WhatsAppProvider.TWILIO)

        # Try to initialize Meta Cloud
        meta = MetaCloudWhatsAppProvider()
        if meta.initialize():
            self._providers[WhatsAppProvider.META_CLOUD] = meta
            providers_initialized.append(WhatsAppProvider.META_CLOUD)

        # Try to initialize UltraMsg (local)
        ultramsg = UltraMsgProvider()
        if ultramsg.initialize():
            self._providers[WhatsAppProvider.ULTRAMSG] = ultramsg
            providers_initialized.append(WhatsAppProvider.ULTRAMSG)

        if providers_initialized:
            # Set primary provider (prefer Twilio, then Meta, then local)
            priority = [WhatsAppProvider.TWILIO, WhatsAppProvider.META_CLOUD, WhatsAppProvider.ULTRAMSG]
            for provider in priority:
                if provider in providers_initialized:
                    self._primary_provider = provider
                    break

            self._initialized = True
            logger.info(f"✅ WhatsApp client initialized with {len(providers_initialized)} provider(s). Primary: {self._primary_provider}")
            return True

        logger.warning("⚠️ No WhatsApp providers configured")
        return False

    async def send_message(
        self,
        to: str,
        body: str,
        body_ar: str | None = None,
        language: str = "ar",
        provider: WhatsAppProvider | None = None,
    ) -> str | None:
        """إرسال رسالة واتساب مع دعم failover"""
        if not self._initialized:
            logger.warning("WhatsApp client not initialized")
            return None

        # Select content based on language
        content = body_ar if language == "ar" and body_ar else body

        # Ensure phone is in E.164 format
        if not to.startswith("+"):
            to = f"+{to}"

        # Try specified provider or primary
        target_provider = provider or self._primary_provider

        if target_provider and target_provider in self._providers:
            result = await self._providers[target_provider].send_message(to, content, language)
            if result:
                return result

        # Failover to other providers
        for prov, client in self._providers.items():
            if prov != target_provider:
                result = await client.send_message(to, content, language)
                if result:
                    logger.info(f"WhatsApp failover to {prov.value} successful")
                    return result

        logger.error(f"All WhatsApp providers failed for {mask_phone(to)}")
        return None

    async def send_otp(
        self,
        to: str,
        otp_code: str,
        language: str = "ar",
    ) -> str | None:
        """إرسال رمز OTP عبر واتساب"""
        if language == "ar":
            body = f"رمز التحقق الخاص بك في SAHOOL: {otp_code}\n\nهذا الرمز صالح لمدة 10 دقائق.\nلا تشارك هذا الرمز مع أي شخص."
        else:
            body = f"Your SAHOOL verification code: {otp_code}\n\nThis code is valid for 10 minutes.\nDo not share this code with anyone."

        return await self.send_message(
            to=to,
            body=body,
            body_ar=body if language == "ar" else None,
            language=language,
        )

    async def send_password_reset(
        self,
        to: str,
        reset_link: str,
        language: str = "ar",
    ) -> str | None:
        """إرسال رابط إعادة تعيين كلمة المرور"""
        if language == "ar":
            body = f"طلب إعادة تعيين كلمة المرور لحساب SAHOOL الخاص بك.\n\nاضغط على الرابط التالي:\n{reset_link}\n\nالرابط صالح لمدة ساعة واحدة.\n\nإذا لم تطلب ذلك، تجاهل هذه الرسالة."
        else:
            body = f"Password reset request for your SAHOOL account.\n\nClick the following link:\n{reset_link}\n\nThis link is valid for 1 hour.\n\nIf you didn't request this, ignore this message."

        return await self.send_message(
            to=to,
            body=body,
            body_ar=body if language == "ar" else None,
            language=language,
        )


# Global client instance
_whatsapp_client: WhatsAppClient | None = None


def get_whatsapp_client() -> WhatsAppClient:
    """الحصول على instance عام من WhatsAppClient"""
    global _whatsapp_client

    if _whatsapp_client is None:
        _whatsapp_client = WhatsAppClient()
        _whatsapp_client.initialize()

    return _whatsapp_client
