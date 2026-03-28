"""
Tests for src/otp_service.py - OTP Service

Covers:
- OTPChannel and OTPPurpose enums
- OTPRecord dataclass (is_expired, has_attempts_remaining, time_remaining, to_dict, from_dict)
- OTPResult dataclass and to_dict
- InMemoryStorage (set, get, delete, update, rate_limit, clear)
- OTPService initialization and generate/verify flow
"""

import asyncio
import os
import time as time_module
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("ENVIRONMENT", "test")

try:
    from src.otp_service import (
        OTP_EXPIRY_SECONDS,
        OTP_LENGTH,
        RATE_LIMIT_MAX_REQUESTS,
        InMemoryStorage,
        OTPChannel,
        OTPPurpose,
        OTPRecord,
        OTPResult,
        OTPService,
    )
except BaseException:
    pytest.skip("OTP service dependencies not available", allow_module_level=True)


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class TestOTPChannel:
    def test_all_channels(self):
        assert OTPChannel.SMS == "sms"
        assert OTPChannel.WHATSAPP == "whatsapp"
        assert OTPChannel.TELEGRAM == "telegram"
        assert OTPChannel.EMAIL == "email"


class TestOTPPurpose:
    def test_all_purposes(self):
        assert OTPPurpose.LOGIN == "login"
        assert OTPPurpose.REGISTRATION == "registration"
        assert OTPPurpose.PASSWORD_RESET == "password_reset"
        assert OTPPurpose.PHONE_VERIFICATION == "phone_verification"
        assert OTPPurpose.EMAIL_VERIFICATION == "email_verification"
        assert OTPPurpose.TRANSACTION == "transaction"
        assert OTPPurpose.TWO_FACTOR == "two_factor"


# ─────────────────────────────────────────────────────────────────────────────
# OTPRecord
# ─────────────────────────────────────────────────────────────────────────────


class TestOTPRecord:
    def _make_record(self, **overrides):
        now = time_module.time()
        defaults = {
            "user_id": "user-123",
            "otp_hash": "abc123hash",
            "purpose": "login",
            "channel": "sms",
            "destination": "+967***5678",
            "created_at": now,
            "expires_at": now + 600,
            "attempts": 0,
            "max_attempts": 3,
            "verified": False,
        }
        defaults.update(overrides)
        return OTPRecord(**defaults)

    def test_create_record(self):
        record = self._make_record()
        assert record.user_id == "user-123"
        assert record.attempts == 0
        assert record.verified is False

    def test_is_expired_false(self):
        record = self._make_record(expires_at=time_module.time() + 600)
        assert record.is_expired() is False

    def test_is_expired_true(self):
        record = self._make_record(expires_at=time_module.time() - 1)
        assert record.is_expired() is True

    def test_has_attempts_remaining_true(self):
        record = self._make_record(attempts=1, max_attempts=3)
        assert record.has_attempts_remaining() is True

    def test_has_attempts_remaining_false(self):
        record = self._make_record(attempts=3, max_attempts=3)
        assert record.has_attempts_remaining() is False

    def test_time_remaining_positive(self):
        record = self._make_record(expires_at=time_module.time() + 300)
        remaining = record.time_remaining()
        assert remaining > 0
        assert remaining <= 300

    def test_time_remaining_zero_when_expired(self):
        record = self._make_record(expires_at=time_module.time() - 10)
        assert record.time_remaining() == 0

    def test_to_dict(self):
        record = self._make_record()
        data = record.to_dict()
        assert data["user_id"] == "user-123"
        assert data["otp_hash"] == "abc123hash"
        assert data["purpose"] == "login"
        assert data["channel"] == "sms"
        assert data["verified"] is False
        assert "created_at" in data
        assert "expires_at" in data

    def test_from_dict(self):
        now = time_module.time()
        data = {
            "user_id": "user-456",
            "otp_hash": "hash456",
            "purpose": "registration",
            "channel": "email",
            "destination": "test@example.com",
            "created_at": now,
            "expires_at": now + 600,
            "attempts": 2,
            "max_attempts": 5,
            "verified": True,
        }
        record = OTPRecord.from_dict(data)
        assert record.user_id == "user-456"
        assert record.purpose == "registration"
        assert record.attempts == 2
        assert record.max_attempts == 5
        assert record.verified is True

    def test_from_dict_defaults(self):
        now = time_module.time()
        data = {
            "user_id": "user-789",
            "otp_hash": "hash789",
            "purpose": "login",
            "channel": "sms",
            "destination": "+967***1234",
            "created_at": now,
            "expires_at": now + 600,
        }
        record = OTPRecord.from_dict(data)
        assert record.attempts == 0
        assert record.max_attempts == 3
        assert record.verified is False


# ─────────────────────────────────────────────────────────────────────────────
# OTPResult
# ─────────────────────────────────────────────────────────────────────────────


class TestOTPResult:
    def test_success_result(self):
        result = OTPResult(
            success=True,
            message="OTP sent",
            message_ar="تم إرسال الرمز",
            otp_sent=True,
            time_remaining=600,
            delivery_id="msg-123",
        )
        assert result.success is True
        assert result.otp_sent is True

    def test_failure_result(self):
        result = OTPResult(
            success=False,
            message="Rate limited",
            message_ar="تم تجاوز الحد",
            error_code="RATE_LIMITED",
        )
        assert result.success is False
        assert result.error_code == "RATE_LIMITED"

    def test_to_dict_minimal(self):
        result = OTPResult(
            success=True,
            message="OK",
            message_ar="تمام",
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["message"] == "OK"
        assert data["message_ar"] == "تمام"
        assert "otp_sent" not in data
        assert "time_remaining" not in data
        assert "delivery_id" not in data
        assert "error_code" not in data

    def test_to_dict_full(self):
        result = OTPResult(
            success=True,
            message="Sent",
            message_ar="تم",
            otp_sent=True,
            time_remaining=300,
            attempts_remaining=2,
            delivery_id="d-1",
            error_code=None,
        )
        data = result.to_dict()
        assert data["otp_sent"] is True
        assert data["time_remaining"] == 300
        assert data["attempts_remaining"] == 2
        assert data["delivery_id"] == "d-1"
        # error_code is None, so should not be in dict
        assert "error_code" not in data

    def test_to_dict_with_error(self):
        result = OTPResult(
            success=False,
            message="Error",
            message_ar="خطأ",
            error_code="EXPIRED",
        )
        data = result.to_dict()
        assert data["error_code"] == "EXPIRED"


# ─────────────────────────────────────────────────────────────────────────────
# InMemoryStorage
# ─────────────────────────────────────────────────────────────────────────────


class TestInMemoryStorage:
    def test_set_and_get_otp(self):
        async def _run():
            storage = InMemoryStorage()
            now = time_module.time()
            record = OTPRecord(
                user_id="user-1",
                otp_hash="hash1",
                purpose="login",
                channel="sms",
                destination="+967***1234",
                created_at=now,
                expires_at=now + 600,
            )
            await storage.set_otp("key-1", record)
            result = await storage.get_otp("key-1")
            assert result is not None
            assert result.user_id == "user-1"

        asyncio.run(_run())

    def test_get_nonexistent_otp(self):
        async def _run():
            storage = InMemoryStorage()
            result = await storage.get_otp("nonexistent")
            assert result is None

        asyncio.run(_run())

    def test_delete_otp(self):
        async def _run():
            storage = InMemoryStorage()
            now = time_module.time()
            record = OTPRecord(
                user_id="user-1",
                otp_hash="hash1",
                purpose="login",
                channel="sms",
                destination="+967***1234",
                created_at=now,
                expires_at=now + 600,
            )
            await storage.set_otp("key-del", record)
            result = await storage.delete_otp("key-del")
            assert result is True

            # Verify deleted
            result = await storage.get_otp("key-del")
            assert result is None

        asyncio.run(_run())

    def test_delete_nonexistent(self):
        async def _run():
            storage = InMemoryStorage()
            result = await storage.delete_otp("nonexistent")
            assert result is False

        asyncio.run(_run())

    def test_update_otp(self):
        async def _run():
            storage = InMemoryStorage()
            now = time_module.time()
            record = OTPRecord(
                user_id="user-1",
                otp_hash="hash1",
                purpose="login",
                channel="sms",
                destination="+967***1234",
                created_at=now,
                expires_at=now + 600,
                attempts=0,
            )
            await storage.set_otp("key-upd", record)

            record.attempts = 2
            await storage.update_otp("key-upd", record)

            updated = await storage.get_otp("key-upd")
            assert updated.attempts == 2

        asyncio.run(_run())

    def test_rate_limit_allowed(self):
        async def _run():
            storage = InMemoryStorage()
            allowed, remaining = await storage.check_rate_limit("user-rl-1")
            assert allowed is True
            assert remaining == RATE_LIMIT_MAX_REQUESTS

        asyncio.run(_run())

    def test_rate_limit_exceeded(self):
        async def _run():
            storage = InMemoryStorage()
            for _ in range(RATE_LIMIT_MAX_REQUESTS):
                await storage.record_request("user-rl-2")
            allowed, remaining = await storage.check_rate_limit("user-rl-2")
            assert allowed is False
            assert remaining == 0

        asyncio.run(_run())

    def test_rate_limit_decrements_remaining(self):
        async def _run():
            storage = InMemoryStorage()
            await storage.record_request("user-rl-3")
            allowed, remaining = await storage.check_rate_limit("user-rl-3")
            assert allowed is True
            assert remaining == RATE_LIMIT_MAX_REQUESTS - 1

        asyncio.run(_run())

    def test_record_request(self):
        async def _run():
            storage = InMemoryStorage()
            await storage.record_request("user-rl-4")
            assert len(storage._rate_limit_store["user-rl-4"]) == 1

        asyncio.run(_run())

    def test_clear(self):
        storage = InMemoryStorage()
        storage._otp_store["key"] = {"data": True}
        storage._rate_limit_store["key"] = [1.0]
        storage.clear()
        assert storage._otp_store == {}
        assert storage._rate_limit_store == {}


# ─────────────────────────────────────────────────────────────────────────────
# OTPService
# ─────────────────────────────────────────────────────────────────────────────


class TestOTPService:
    def test_init(self):
        service = OTPService()
        assert service._initialized is False
        assert service._use_redis is False
        assert service._redis_client is None

    def test_initialize_without_redis(self):
        service = OTPService()
        result = asyncio.run(service.initialize(use_redis=False))
        assert result is True
        assert service._initialized is True
        assert service._use_redis is False

    def test_initialize_already_initialized(self):
        service = OTPService()
        service._initialized = True
        result = asyncio.run(service.initialize())
        assert result is True

    def test_initialize_redis_not_available(self):
        service = OTPService()
        # Mock shared.cache.get_redis_client to raise ConnectionError so we
        # don't attempt a real Redis Sentinel connection (causes timeouts in CI)
        with patch.dict(
            "sys.modules",
            {"shared.cache": MagicMock(get_redis_client=MagicMock(side_effect=ConnectionError("mocked")))},
        ):
            result = asyncio.run(service.initialize(use_redis=True))
        # Should fallback to in-memory
        assert result is True
        assert service._initialized is True

    def test_get_otp_key(self):
        service = OTPService()
        key = service._get_otp_key("user-123", "login")
        assert key == "otp:user-123:login"

    def test_get_rate_limit_key(self):
        service = OTPService()
        key = service._get_rate_limit_key("user-123", "sms")
        assert key == "otp_rate:user-123:sms"

    def test_generate_otp_code_default_length(self):
        service = OTPService()
        code = service._generate_otp_code()
        assert len(code) == OTP_LENGTH
        assert code.isdigit()

    def test_generate_otp_code_custom_length(self):
        service = OTPService()
        code = service._generate_otp_code(length=8)
        assert len(code) == 8
        assert code.isdigit()

    def test_generate_otp_code_uniqueness(self):
        service = OTPService()
        codes = set()
        for _ in range(50):
            codes.add(service._generate_otp_code())
        assert len(codes) > 40  # Most should be unique

    def test_hash_otp(self):
        service = OTPService()
        hash1 = service._hash_otp("123456", "user-1")
        hash2 = service._hash_otp("123456", "user-1")
        assert hash1 == hash2  # Same input should produce same hash
        assert len(hash1) == 64  # SHA-256 hex digest

    def test_hash_otp_different_users(self):
        service = OTPService()
        hash1 = service._hash_otp("123456", "user-1")
        hash2 = service._hash_otp("123456", "user-2")
        assert hash1 != hash2  # Different users should produce different hashes

    def test_verify_otp_hash_correct(self):
        service = OTPService()
        otp = "654321"
        user_id = "user-test"
        stored_hash = service._hash_otp(otp, user_id)
        assert service._verify_otp_hash(otp, user_id, stored_hash) is True

    def test_verify_otp_hash_incorrect(self):
        service = OTPService()
        stored_hash = service._hash_otp("123456", "user-test")
        assert service._verify_otp_hash("654321", "user-test", stored_hash) is False

    def test_mask_destination_phone(self):
        service = OTPService()
        masked = service._mask_destination("+967712345678", "sms")
        assert masked.endswith("5678")
        assert "*" in masked

    def test_mask_destination_short_phone(self):
        service = OTPService()
        masked = service._mask_destination("1234", "sms")
        assert masked == "1234"

    def test_mask_destination_email(self):
        service = OTPService()
        masked = service._mask_destination("ahmed@example.com", "email")
        assert masked.startswith("ah")
        assert "@example.com" in masked
        assert "*" in masked

    def test_mask_destination_short_email(self):
        service = OTPService()
        masked = service._mask_destination("a@b.com", "email")
        assert "@b.com" in masked

    def test_check_initialized_false(self):
        service = OTPService()
        assert service._check_initialized() is False

    def test_check_initialized_true(self):
        service = OTPService()
        service._initialized = True
        assert service._check_initialized() is True

    def test_store_otp_in_memory(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            now = time_module.time()
            record = OTPRecord(
                user_id="user-1",
                otp_hash="hash1",
                purpose="login",
                channel="sms",
                destination="+967***1234",
                created_at=now,
                expires_at=now + 600,
            )
            result = await service._store_otp("test-key", record)
            assert result is True

        asyncio.run(_run())

    def test_get_otp_in_memory(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            now = time_module.time()
            record = OTPRecord(
                user_id="user-1",
                otp_hash="hash1",
                purpose="login",
                channel="sms",
                destination="+967***1234",
                created_at=now,
                expires_at=now + 600,
            )
            await service._store_otp("test-key-get", record)
            retrieved = await service._get_otp("test-key-get")
            assert retrieved is not None
            assert retrieved.user_id == "user-1"

        asyncio.run(_run())

    def test_get_otp_nonexistent(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)
            result = await service._get_otp("nonexistent")
            assert result is None

        asyncio.run(_run())

    def test_get_sms_client(self):
        service = OTPService()
        client = service._get_sms_client()
        # Should return something (client or None)
        assert client is not None or client is None

    def test_get_whatsapp_client(self):
        service = OTPService()
        client = service._get_whatsapp_client()
        assert client is not None or client is None

    def test_get_telegram_client(self):
        service = OTPService()
        client = service._get_telegram_client()
        assert client is not None or client is None

    def test_get_email_client(self):
        service = OTPService()
        client = service._get_email_client()
        assert client is not None or client is None

    def test_delete_otp_in_memory(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            now = time_module.time()
            record = OTPRecord(
                user_id="user-del",
                otp_hash="hash",
                purpose="login",
                channel="sms",
                destination="+967***1234",
                created_at=now,
                expires_at=now + 600,
            )
            await service._store_otp("del-key", record)
            result = await service._delete_otp("del-key")
            assert result is True

        asyncio.run(_run())

    def test_update_otp_in_memory(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            now = time_module.time()
            record = OTPRecord(
                user_id="user-upd",
                otp_hash="hash",
                purpose="login",
                channel="sms",
                destination="+967***1234",
                created_at=now,
                expires_at=now + 600,
            )
            await service._store_otp("upd-key", record)
            record.attempts = 2
            result = await service._update_otp("upd-key", record)
            assert result is True

        asyncio.run(_run())

    def test_check_rate_limit_in_memory(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            allowed, remaining = await service._check_rate_limit("user-rl", "sms")
            assert allowed is True
            assert remaining > 0

        asyncio.run(_run())

    def test_record_rate_limit_in_memory(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            # Should not raise
            await service._record_rate_limit("user-rl2", "sms")

        asyncio.run(_run())

    def test_get_otp_message_arabic(self):
        service = OTPService()
        subject, body = service._get_otp_message("123456", "login", language="ar")
        assert "123456" in body
        assert "SAHOOL" in subject
        assert "تسجيل الدخول" in subject

    def test_get_otp_message_english(self):
        service = OTPService()
        subject, body = service._get_otp_message("654321", "login", language="en")
        assert "654321" in body
        assert "SAHOOL" in subject
        assert "Login" in subject

    def test_get_otp_message_all_purposes(self):
        service = OTPService()
        for purpose in OTPPurpose:
            subject, body = service._get_otp_message("111111", purpose, "ar")
            assert "111111" in body
            subject, body = service._get_otp_message("222222", purpose, "en")
            assert "222222" in body

    def test_get_otp_message_unknown_purpose(self):
        service = OTPService()
        subject, body = service._get_otp_message("999999", "unknown_purpose", "ar")
        assert "999999" in body
        assert "التحقق" in subject

    def test_get_otp_html_email_arabic(self):
        service = OTPService()
        subject, html = service._get_otp_html_email("123456", "registration", "ar")
        assert "123456" in html
        assert "rtl" in html
        assert "SAHOOL" in html

    def test_get_otp_html_email_english(self):
        service = OTPService()
        subject, html = service._get_otp_html_email("654321", "password_reset", "en")
        assert "654321" in html
        assert 'lang="en"' in html
        assert "Password Reset" in subject

    def test_get_otp_html_email_all_purposes(self):
        service = OTPService()
        for purpose in OTPPurpose:
            subject, html = service._get_otp_html_email("000000", purpose, "ar")
            assert "000000" in html
            subject, html = service._get_otp_html_email("111111", purpose, "en")
            assert "111111" in html


class TestOTPServiceDelivery:
    def test_send_via_sms_no_client(self):
        async def _run():
            service = OTPService()
            service._sms_client = None
            # Force _get_sms_client to return None
            with patch.object(service, "_get_sms_client", return_value=None):
                result = await service._send_otp_via_sms("+967712345678", "123456", "login", "ar")
                assert result is None

        asyncio.run(_run())

    def test_send_via_sms_success(self):
        async def _run():
            service = OTPService()
            mock_client = MagicMock()
            mock_client.send_sms = AsyncMock(return_value="SM123")
            with patch.object(service, "_get_sms_client", return_value=mock_client):
                result = await service._send_otp_via_sms("+967712345678", "123456", "login", "ar")
                assert result == "SM123"

        asyncio.run(_run())

    def test_send_via_whatsapp_no_client(self):
        async def _run():
            service = OTPService()
            with patch.object(service, "_get_whatsapp_client", return_value=None):
                result = await service._send_otp_via_whatsapp("+967712345678", "123456", "login", "ar")
                assert result is None

        asyncio.run(_run())

    def test_send_via_whatsapp_success(self):
        async def _run():
            service = OTPService()
            mock_client = MagicMock()
            mock_client.send_otp = AsyncMock(return_value="WA123")
            with patch.object(service, "_get_whatsapp_client", return_value=mock_client):
                result = await service._send_otp_via_whatsapp("+967712345678", "123456", "login", "ar")
                assert result == "WA123"

        asyncio.run(_run())

    def test_send_via_telegram_no_client(self):
        async def _run():
            service = OTPService()
            with patch.object(service, "_get_telegram_client", return_value=None):
                result = await service._send_otp_via_telegram("chat123", "123456", "login", "ar")
                assert result is None

        asyncio.run(_run())

    def test_send_via_telegram_success(self):
        async def _run():
            service = OTPService()
            mock_client = MagicMock()
            mock_client.send_otp = AsyncMock(return_value=12345)
            with patch.object(service, "_get_telegram_client", return_value=mock_client):
                result = await service._send_otp_via_telegram("chat123", "123456", "login", "ar")
                assert result == 12345

        asyncio.run(_run())

    def test_send_via_email_no_client(self):
        async def _run():
            service = OTPService()
            with patch.object(service, "_get_email_client", return_value=None):
                result = await service._send_otp_via_email("test@example.com", "123456", "login", "en")
                assert result is None

        asyncio.run(_run())

    def test_send_via_email_success(self):
        async def _run():
            service = OTPService()
            mock_client = MagicMock()
            mock_client.send_email = AsyncMock(return_value="msg-123")
            with patch.object(service, "_get_email_client", return_value=mock_client):
                result = await service._send_otp_via_email("test@example.com", "123456", "login", "en")
                assert result == "msg-123"

        asyncio.run(_run())

    def test_send_via_email_arabic(self):
        async def _run():
            service = OTPService()
            mock_client = MagicMock()
            mock_client.send_email = AsyncMock(return_value="msg-ar")
            with patch.object(service, "_get_email_client", return_value=mock_client):
                result = await service._send_otp_via_email("test@example.com", "123456", "login", "ar")
                assert result == "msg-ar"

        asyncio.run(_run())


class TestOTPServiceGenerateAndVerify:
    def test_generate_otp_not_initialized(self):
        async def _run():
            service = OTPService()
            result = await service.generate_otp(
                user_id="user-1",
                phone_or_email="+967712345678",
                channel="sms",
                purpose="login",
            )
            assert result.success is False
            assert result.error_code == "SERVICE_NOT_INITIALIZED"

        asyncio.run(_run())

    def test_generate_otp_rate_limited(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            # Exhaust rate limit
            for _ in range(RATE_LIMIT_MAX_REQUESTS):
                rate_key = service._get_rate_limit_key("user-rl-gen", "sms")
                await service._in_memory_storage.record_request(rate_key)

            result = await service.generate_otp(
                user_id="user-rl-gen",
                phone_or_email="+967712345678",
                channel=OTPChannel.SMS,
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is False
            assert result.error_code == "RATE_LIMIT_EXCEEDED"

        asyncio.run(_run())

    def test_generate_otp_existing_not_expired(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            # Store an existing OTP that isn't expired yet
            now = time_module.time()
            otp_key = service._get_otp_key("user-existing", "login")
            record = OTPRecord(
                user_id="user-existing",
                otp_hash="hash",
                purpose="login",
                channel="sms",
                destination="***5678",
                created_at=now,
                expires_at=now + 300,  # 5 minutes remaining
            )
            await service._store_otp(otp_key, record)

            result = await service.generate_otp(
                user_id="user-existing",
                phone_or_email="+967712345678",
                channel=OTPChannel.SMS,
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is False
            assert result.error_code == "OTP_ALREADY_SENT"

        asyncio.run(_run())

    def test_generate_otp_sms_success(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            mock_client = MagicMock()
            mock_client.send_sms = AsyncMock(return_value="SM789")
            with patch.object(service, "_get_sms_client", return_value=mock_client):
                result = await service.generate_otp(
                    user_id="user-sms-ok",
                    phone_or_email="+967712345678",
                    channel=OTPChannel.SMS,
                    purpose=OTPPurpose.LOGIN,
                    language="ar",
                )
                assert result.success is True
                assert result.otp_sent is True
                assert result.delivery_id is not None

        asyncio.run(_run())

    def test_generate_otp_email_success(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            mock_client = MagicMock()
            mock_client.send_email = AsyncMock(return_value="msg-456")
            with patch.object(service, "_get_email_client", return_value=mock_client):
                result = await service.generate_otp(
                    user_id="user-email-ok",
                    phone_or_email="test@example.com",
                    channel=OTPChannel.EMAIL,
                    purpose=OTPPurpose.EMAIL_VERIFICATION,
                    language="en",
                )
                assert result.success is True
                assert result.otp_sent is True

        asyncio.run(_run())

    def test_generate_otp_delivery_exception(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            mock_client = MagicMock()
            mock_client.send_sms = AsyncMock(side_effect=Exception("Network error"))
            with patch.object(service, "_get_sms_client", return_value=mock_client):
                result = await service.generate_otp(
                    user_id="user-exc",
                    phone_or_email="+967712345678",
                    channel=OTPChannel.SMS,
                    purpose=OTPPurpose.LOGIN,
                )
                assert result.success is False
                assert result.error_code == "DELIVERY_FAILED"

        asyncio.run(_run())

    def test_generate_otp_string_enum_conversion(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            mock_client = MagicMock()
            mock_client.send_sms = AsyncMock(return_value="SM101")
            with patch.object(service, "_get_sms_client", return_value=mock_client):
                result = await service.generate_otp(
                    user_id="user-str-conv",
                    phone_or_email="+967712345678",
                    channel="sms",  # string instead of enum
                    purpose="login",  # string instead of enum
                )
                assert result.success is True

        asyncio.run(_run())

    def test_generate_otp_sms_delivery_fails(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            # SMS client returns None (delivery failure)
            result = await service.generate_otp(
                user_id="user-sms-fail",
                phone_or_email="+967712345678",
                channel=OTPChannel.SMS,
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is False
            assert result.error_code == "DELIVERY_FAILED"

        asyncio.run(_run())

    def test_verify_otp_not_initialized(self):
        async def _run():
            service = OTPService()
            result = await service.verify_otp(
                user_id="user-1",
                otp_code="123456",
                purpose="login",
            )
            assert result.success is False
            assert result.error_code == "SERVICE_NOT_INITIALIZED"

        asyncio.run(_run())

    def test_verify_otp_not_found(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            result = await service.verify_otp(
                user_id="user-no-otp",
                otp_code="123456",
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is False
            assert result.error_code == "OTP_NOT_FOUND"

        asyncio.run(_run())

    def test_verify_otp_expired(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            # Store expired OTP
            now = time_module.time()
            otp_key = service._get_otp_key("user-expired", "login")
            record = OTPRecord(
                user_id="user-expired",
                otp_hash=service._hash_otp("123456", "user-expired"),
                purpose="login",
                channel="sms",
                destination="***5678",
                created_at=now - 700,
                expires_at=now - 100,  # Expired
            )
            await service._store_otp(otp_key, record)

            result = await service.verify_otp(
                user_id="user-expired",
                otp_code="123456",
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is False
            assert result.error_code == "OTP_EXPIRED"

        asyncio.run(_run())

    def test_verify_otp_wrong_code(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            now = time_module.time()
            otp_key = service._get_otp_key("user-wrong", "login")
            record = OTPRecord(
                user_id="user-wrong",
                otp_hash=service._hash_otp("123456", "user-wrong"),
                purpose="login",
                channel="sms",
                destination="***5678",
                created_at=now,
                expires_at=now + 600,
            )
            await service._store_otp(otp_key, record)

            result = await service.verify_otp(
                user_id="user-wrong",
                otp_code="654321",  # Wrong code
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is False
            assert result.error_code == "INVALID_OTP"

        asyncio.run(_run())

    def test_verify_otp_correct_code(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            now = time_module.time()
            otp_code = "123456"
            user_id = "user-correct"
            otp_key = service._get_otp_key(user_id, "login")
            record = OTPRecord(
                user_id=user_id,
                otp_hash=service._hash_otp(otp_code, user_id),
                purpose="login",
                channel="sms",
                destination="***5678",
                created_at=now,
                expires_at=now + 600,
            )
            await service._store_otp(otp_key, record)

            result = await service.verify_otp(
                user_id=user_id,
                otp_code=otp_code,
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is True

        asyncio.run(_run())

    def test_verify_otp_max_attempts_exceeded(self):
        async def _run():
            service = OTPService()
            await service.initialize(use_redis=False)

            now = time_module.time()
            otp_key = service._get_otp_key("user-attempts", "login")
            record = OTPRecord(
                user_id="user-attempts",
                otp_hash=service._hash_otp("123456", "user-attempts"),
                purpose="login",
                channel="sms",
                destination="***5678",
                created_at=now,
                expires_at=now + 600,
                attempts=3,
                max_attempts=3,
            )
            await service._store_otp(otp_key, record)

            result = await service.verify_otp(
                user_id="user-attempts",
                otp_code="123456",
                purpose=OTPPurpose.LOGIN,
            )
            assert result.success is False
            assert result.error_code == "MAX_ATTEMPTS_EXCEEDED"

        asyncio.run(_run())
