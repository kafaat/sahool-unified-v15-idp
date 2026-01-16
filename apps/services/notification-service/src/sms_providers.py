"""
SAHOOL SMS Providers - Multi-Provider Abstraction
مزودي الرسائل النصية - تجريد متعدد المزودين

Supports:
- Twilio (External/International)
- Vonage/Nexmo (External)
- Local providers (Yemen, Saudi Arabia, UAE)

Features:
- Provider abstraction with failover
- OTP sending with bilingual support
- Cost-aware routing (prefer local for local numbers)
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class SMSProvider(str, Enum):
    """مزودي خدمة SMS"""
    TWILIO = "twilio"
    VONAGE = "vonage"
    LOCAL_YEMENMOBILE = "yemenmobile"  # Yemen Mobile
    LOCAL_MTN_YEMEN = "mtn_yemen"  # MTN Yemen
    LOCAL_MOBILY = "mobily"  # Mobily Saudi
    LOCAL_STC = "stc"  # STC Saudi
    MSEGAT = "msegat"  # Popular Arabic SMS gateway


@dataclass
class SMSResult:
    """نتيجة إرسال SMS"""
    success: bool
    message_id: str | None = None
    provider: str | None = None
    error: str | None = None
    cost: float | None = None


class BaseSMSProvider(ABC):
    """قاعدة مزود SMS"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def send_sms(
        self,
        to: str,
        body: str,
        sender_id: str | None = None,
    ) -> SMSResult:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def supports_region(self, phone_number: str) -> bool:
        """Check if provider supports the phone number's region"""
        pass


class TwilioSMSProvider(BaseSMSProvider):
    """مزود Twilio للرسائل النصية"""

    def __init__(self):
        self._initialized = False
        self._client = None
        self._from_number: str | None = None

    @property
    def provider_name(self) -> str:
        return "twilio"

    def initialize(self) -> bool:
        try:
            from twilio.rest import Client as TwilioClient

            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            from_number = os.getenv("TWILIO_FROM_NUMBER")

            if not all([account_sid, auth_token, from_number]):
                return False

            self._client = TwilioClient(account_sid, auth_token)
            self._from_number = from_number
            self._initialized = True
            logger.info(f"✅ Twilio SMS initialized (from: {from_number})")
            return True
        except ImportError:
            logger.warning("Twilio SDK not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Twilio: {e}")
            return False

    def is_available(self) -> bool:
        return self._initialized

    def supports_region(self, phone_number: str) -> bool:
        # Twilio supports international
        return True

    async def send_sms(
        self,
        to: str,
        body: str,
        sender_id: str | None = None,
    ) -> SMSResult:
        if not self._initialized:
            return SMSResult(success=False, error="Provider not initialized")

        try:
            from_number = sender_id or self._from_number
            message = await asyncio.to_thread(
                self._client.messages.create,
                body=body,
                from_=from_number,
                to=to,
            )
            return SMSResult(
                success=True,
                message_id=message.sid,
                provider=self.provider_name,
            )
        except Exception as e:
            return SMSResult(success=False, error=str(e), provider=self.provider_name)


class VonageSMSProvider(BaseSMSProvider):
    """مزود Vonage/Nexmo للرسائل النصية"""

    def __init__(self):
        self._initialized = False
        self._api_key: str | None = None
        self._api_secret: str | None = None
        self._from_number: str | None = None

    @property
    def provider_name(self) -> str:
        return "vonage"

    def initialize(self) -> bool:
        try:
            api_key = os.getenv("VONAGE_API_KEY")
            api_secret = os.getenv("VONAGE_API_SECRET")
            from_number = os.getenv("VONAGE_FROM_NUMBER", "SAHOOL")

            if not all([api_key, api_secret]):
                return False

            self._api_key = api_key
            self._api_secret = api_secret
            self._from_number = from_number
            self._initialized = True
            logger.info("✅ Vonage SMS initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Vonage: {e}")
            return False

    def is_available(self) -> bool:
        return self._initialized

    def supports_region(self, phone_number: str) -> bool:
        return True

    async def send_sms(
        self,
        to: str,
        body: str,
        sender_id: str | None = None,
    ) -> SMSResult:
        if not self._initialized:
            return SMSResult(success=False, error="Provider not initialized")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://rest.nexmo.com/sms/json",
                    data={
                        "api_key": self._api_key,
                        "api_secret": self._api_secret,
                        "from": sender_id or self._from_number,
                        "to": to.lstrip("+"),
                        "text": body,
                        "type": "unicode",
                    },
                )
                data = response.json()
                messages = data.get("messages", [{}])
                if messages and messages[0].get("status") == "0":
                    return SMSResult(
                        success=True,
                        message_id=messages[0].get("message-id"),
                        provider=self.provider_name,
                    )
                else:
                    return SMSResult(
                        success=False,
                        error=messages[0].get("error-text", "Unknown error"),
                        provider=self.provider_name,
                    )
        except Exception as e:
            return SMSResult(success=False, error=str(e), provider=self.provider_name)


class MsegatSMSProvider(BaseSMSProvider):
    """
    مزود Msegat للرسائل النصية (مزود عربي شهير)
    Popular Arabic SMS gateway supporting Saudi Arabia, UAE, Kuwait, Yemen, etc.
    """

    def __init__(self):
        self._initialized = False
        self._username: str | None = None
        self._api_key: str | None = None
        self._sender_id: str | None = None
        self._base_url = "https://www.msegat.com/gw/sendsms.php"

    @property
    def provider_name(self) -> str:
        return "msegat"

    def initialize(self) -> bool:
        try:
            username = os.getenv("MSEGAT_USERNAME")
            api_key = os.getenv("MSEGAT_API_KEY")
            sender_id = os.getenv("MSEGAT_SENDER_ID", "SAHOOL")

            if not all([username, api_key]):
                return False

            self._username = username
            self._api_key = api_key
            self._sender_id = sender_id
            self._initialized = True
            logger.info("✅ Msegat SMS initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Msegat: {e}")
            return False

    def is_available(self) -> bool:
        return self._initialized

    def supports_region(self, phone_number: str) -> bool:
        # Msegat primarily supports Arab countries
        arab_prefixes = [
            "+967",  # Yemen
            "+966",  # Saudi Arabia
            "+971",  # UAE
            "+965",  # Kuwait
            "+968",  # Oman
            "+973",  # Bahrain
            "+974",  # Qatar
            "+20",   # Egypt
            "+962",  # Jordan
            "+961",  # Lebanon
            "+963",  # Syria
            "+964",  # Iraq
        ]
        return any(phone_number.startswith(prefix) for prefix in arab_prefixes)

    async def send_sms(
        self,
        to: str,
        body: str,
        sender_id: str | None = None,
    ) -> SMSResult:
        if not self._initialized:
            return SMSResult(success=False, error="Provider not initialized")

        try:
            # Msegat expects numbers without + prefix
            phone = to.lstrip("+")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._base_url,
                    json={
                        "userName": self._username,
                        "apiKey": self._api_key,
                        "numbers": phone,
                        "userSender": sender_id or self._sender_id,
                        "msg": body,
                        "msgEncoding": "UTF8",
                    },
                )
                data = response.json()

                # Msegat response codes:
                # 1 = Success
                # Other codes = Failure
                if data.get("code") == "1" or data.get("code") == 1:
                    return SMSResult(
                        success=True,
                        message_id=data.get("id", "sent"),
                        provider=self.provider_name,
                    )
                else:
                    return SMSResult(
                        success=False,
                        error=data.get("message", f"Error code: {data.get('code')}"),
                        provider=self.provider_name,
                    )
        except Exception as e:
            return SMSResult(success=False, error=str(e), provider=self.provider_name)


class LocalYemenSMSProvider(BaseSMSProvider):
    """
    مزود SMS محلي يمني (مثال للتكامل مع مزودين محليين)
    Example local Yemen SMS provider integration
    """

    def __init__(self):
        self._initialized = False
        self._api_url: str | None = None
        self._api_key: str | None = None
        self._sender_id: str | None = None

    @property
    def provider_name(self) -> str:
        return "local_yemen"

    def initialize(self) -> bool:
        try:
            api_url = os.getenv("YEMEN_SMS_API_URL")
            api_key = os.getenv("YEMEN_SMS_API_KEY")
            sender_id = os.getenv("YEMEN_SMS_SENDER_ID", "SAHOOL")

            if not all([api_url, api_key]):
                return False

            self._api_url = api_url
            self._api_key = api_key
            self._sender_id = sender_id
            self._initialized = True
            logger.info("✅ Local Yemen SMS initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Local Yemen SMS: {e}")
            return False

    def is_available(self) -> bool:
        return self._initialized

    def supports_region(self, phone_number: str) -> bool:
        # Only supports Yemen numbers
        return phone_number.startswith("+967")

    async def send_sms(
        self,
        to: str,
        body: str,
        sender_id: str | None = None,
    ) -> SMSResult:
        if not self._initialized:
            return SMSResult(success=False, error="Provider not initialized")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._api_url,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "to": to,
                        "message": body,
                        "sender": sender_id or self._sender_id,
                    },
                )
                data = response.json()

                if response.status_code == 200 and data.get("success"):
                    return SMSResult(
                        success=True,
                        message_id=data.get("message_id"),
                        provider=self.provider_name,
                    )
                else:
                    return SMSResult(
                        success=False,
                        error=data.get("error", "Unknown error"),
                        provider=self.provider_name,
                    )
        except Exception as e:
            return SMSResult(success=False, error=str(e), provider=self.provider_name)


class MultiProviderSMSClient:
    """
    عميل SMS متعدد المزودين مع دعم failover وتوجيه ذكي
    Multi-provider SMS client with failover and smart routing
    """

    def __init__(self):
        self._providers: dict[SMSProvider, BaseSMSProvider] = {}
        self._provider_priority: list[SMSProvider] = []
        self._initialized = False

    def initialize(self) -> bool:
        """تهيئة جميع المزودين المتاحين"""
        providers_initialized = []

        # Initialize all providers
        provider_classes = [
            (SMSProvider.TWILIO, TwilioSMSProvider),
            (SMSProvider.VONAGE, VonageSMSProvider),
            (SMSProvider.MSEGAT, MsegatSMSProvider),
            (SMSProvider.LOCAL_YEMENMOBILE, LocalYemenSMSProvider),
        ]

        for provider_type, provider_class in provider_classes:
            try:
                provider = provider_class()
                if provider.initialize():
                    self._providers[provider_type] = provider
                    providers_initialized.append(provider_type)
            except Exception as e:
                logger.warning(f"Failed to initialize {provider_type.value}: {e}")

        if providers_initialized:
            # Set priority (prefer local for cost savings)
            # Priority: Msegat (Arab countries) > Local > Twilio > Vonage
            priority_order = [
                SMSProvider.MSEGAT,
                SMSProvider.LOCAL_YEMENMOBILE,
                SMSProvider.TWILIO,
                SMSProvider.VONAGE,
            ]
            self._provider_priority = [p for p in priority_order if p in providers_initialized]
            self._initialized = True
            logger.info(
                f"✅ Multi-provider SMS initialized with {len(providers_initialized)} provider(s): "
                f"{', '.join(p.value for p in providers_initialized)}"
            )
            return True

        logger.warning("⚠️ No SMS providers configured")
        return False

    def _get_best_provider_for_number(self, phone_number: str) -> BaseSMSProvider | None:
        """Get the best provider for a phone number based on region and availability"""
        for provider_type in self._provider_priority:
            provider = self._providers.get(provider_type)
            if provider and provider.is_available() and provider.supports_region(phone_number):
                return provider
        return None

    async def send_sms(
        self,
        to: str,
        body: str,
        body_ar: str | None = None,
        language: str = "ar",
        sender_id: str | None = None,
        preferred_provider: SMSProvider | None = None,
    ) -> SMSResult:
        """إرسال SMS مع توجيه ذكي ودعم failover"""
        if not self._initialized:
            return SMSResult(success=False, error="SMS client not initialized")

        # Ensure phone is in E.164 format
        if not to.startswith("+"):
            to = f"+{to}"

        # Select content based on language
        content = body_ar if language == "ar" and body_ar else body

        # Try preferred provider first
        if preferred_provider and preferred_provider in self._providers:
            provider = self._providers[preferred_provider]
            if provider.is_available():
                result = await provider.send_sms(to, content, sender_id)
                if result.success:
                    return result
                logger.warning(f"Preferred provider {preferred_provider.value} failed: {result.error}")

        # Get best provider for the number
        provider = self._get_best_provider_for_number(to)
        if provider:
            result = await provider.send_sms(to, content, sender_id)
            if result.success:
                return result
            logger.warning(f"Best provider {provider.provider_name} failed: {result.error}")

        # Failover to remaining providers
        for provider_type, provider in self._providers.items():
            if provider.is_available():
                result = await provider.send_sms(to, content, sender_id)
                if result.success:
                    logger.info(f"SMS failover to {provider_type.value} successful")
                    return result

        return SMSResult(success=False, error="All SMS providers failed")

    async def send_otp(
        self,
        to: str,
        otp_code: str,
        language: str = "ar",
    ) -> SMSResult:
        """إرسال رمز OTP"""
        if language == "ar":
            body = f"رمز التحقق الخاص بك في SAHOOL: {otp_code}\nصالح لمدة 10 دقائق."
        else:
            body = f"Your SAHOOL verification code: {otp_code}\nValid for 10 minutes."

        return await self.send_sms(
            to=to,
            body=body,
            language=language,
        )

    async def send_password_reset_otp(
        self,
        to: str,
        otp_code: str,
        language: str = "ar",
    ) -> SMSResult:
        """إرسال رمز OTP لإعادة تعيين كلمة المرور"""
        if language == "ar":
            body = f"رمز إعادة تعيين كلمة المرور لحساب SAHOOL: {otp_code}\nصالح لمدة 10 دقائق.\nإذا لم تطلب ذلك، تجاهل هذه الرسالة."
        else:
            body = f"SAHOOL password reset code: {otp_code}\nValid for 10 minutes.\nIf you didn't request this, ignore this message."

        return await self.send_sms(
            to=to,
            body=body,
            language=language,
        )

    def get_available_providers(self) -> list[str]:
        """الحصول على قائمة المزودين المتاحين"""
        return [p.value for p in self._providers.keys() if self._providers[p].is_available()]


# Global client instance
_multi_sms_client: MultiProviderSMSClient | None = None


def get_multi_sms_client() -> MultiProviderSMSClient:
    """الحصول على instance عام من MultiProviderSMSClient"""
    global _multi_sms_client

    if _multi_sms_client is None:
        _multi_sms_client = MultiProviderSMSClient()
        _multi_sms_client.initialize()

    return _multi_sms_client
