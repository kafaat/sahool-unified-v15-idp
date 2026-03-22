"""
Tests for src/sms_providers.py - SMS Provider Abstraction

Covers:
- SMSProvider enum
- SMSResult dataclass
- MultiProviderSMSClient init and configuration
- get_multi_sms_client singleton
"""

import pytest
from unittest.mock import MagicMock, patch

from src.sms_providers import (
    SMSProvider,
    SMSResult,
    MultiProviderSMSClient,
    get_multi_sms_client,
)


class TestSMSProviderEnum:
    def test_all_providers(self):
        assert SMSProvider.TWILIO == "twilio"
        assert SMSProvider.VONAGE == "vonage"
        assert SMSProvider.LOCAL_YEMENMOBILE == "yemenmobile"
        assert SMSProvider.LOCAL_MTN_YEMEN == "mtn_yemen"
        assert SMSProvider.LOCAL_MOBILY == "mobily"
        assert SMSProvider.LOCAL_STC == "stc"
        assert SMSProvider.MSEGAT == "msegat"


class TestSMSResult:
    def test_success_result(self):
        result = SMSResult(
            success=True,
            message_id="SM123",
            provider="twilio",
            cost=0.05,
        )
        assert result.success is True
        assert result.message_id == "SM123"
        assert result.provider == "twilio"
        assert result.error is None

    def test_failure_result(self):
        result = SMSResult(
            success=False,
            error="Connection timeout",
            provider="vonage",
        )
        assert result.success is False
        assert result.error == "Connection timeout"
        assert result.message_id is None

    def test_default_values(self):
        result = SMSResult(success=True)
        assert result.message_id is None
        assert result.provider is None
        assert result.error is None
        assert result.cost is None


class TestMultiProviderSMSClient:
    def test_init(self):
        client = MultiProviderSMSClient()
        assert isinstance(client, MultiProviderSMSClient)

    def test_get_available_providers(self):
        client = MultiProviderSMSClient()
        providers = client.get_available_providers()
        assert isinstance(providers, list)


class TestGetMultiSmsClient:
    def test_returns_singleton(self):
        import src.sms_providers as mod
        old = mod._multi_sms_client
        mod._multi_sms_client = None

        client1 = get_multi_sms_client()
        client2 = get_multi_sms_client()
        assert client1 is client2

        mod._multi_sms_client = old
"""
Tests for src/whatsapp_client.py - WhatsApp client data models

Covers:
- WhatsAppClient init
- get_whatsapp_client singleton
"""


from src.whatsapp_client import WhatsAppClient, get_whatsapp_client


class TestWhatsAppClient:
    def test_init(self):
        client = WhatsAppClient()
        assert isinstance(client, WhatsAppClient)

    def test_not_initialized_by_default(self):
        client = WhatsAppClient()
        assert client._initialized is False


class TestGetWhatsAppClient:
    def test_returns_singleton(self):
        import src.whatsapp_client as mod
        old = mod._whatsapp_client
        mod._whatsapp_client = None

        client1 = get_whatsapp_client()
        client2 = get_whatsapp_client()
        assert client1 is client2

        mod._whatsapp_client = old


"""
Tests for src/telegram_client.py

Covers:
- TelegramClient init
- get_telegram_client singleton
"""


from src.telegram_client import TelegramClient, get_telegram_client


class TestTelegramClient:
    def test_init(self):
        client = TelegramClient()
        assert isinstance(client, TelegramClient)


class TestGetTelegramClient:
    def test_returns_singleton(self):
        import src.telegram_client as mod
        old = mod._telegram_client
        mod._telegram_client = None

        client1 = get_telegram_client()
        client2 = get_telegram_client()
        assert client1 is client2

        mod._telegram_client = old


"""
Tests for src/firebase_client.py

Covers:
- FirebaseClient init
- get_firebase_client singleton
"""


from src.firebase_client import FirebaseClient, get_firebase_client


class TestFirebaseClient:
    def test_init(self):
        client = FirebaseClient()
        assert isinstance(client, FirebaseClient)

    def test_not_initialized_by_default(self):
        client = FirebaseClient()
        assert client._initialized is False


class TestGetFirebaseClient:
    def test_returns_singleton(self):
        import src.firebase_client as mod
        old = mod._firebase_client
        mod._firebase_client = None

        client1 = get_firebase_client()
        client2 = get_firebase_client()
        assert client1 is client2

        mod._firebase_client = old
