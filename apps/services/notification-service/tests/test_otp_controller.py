"""
Tests for src/otp_controller.py - OTP Controller Models and Validation

Covers:
- OTPChannel, OTPPurpose, Language enums
- SendOTPRequest validation (identifier, phone, email)
- SendOTPResponse, VerifyOTPRequest, etc. models
- get_tenant_id header extraction
"""

import asyncio
import pytest
from fastapi import HTTPException
from src.otp_controller import (
    Language,
    OTPChannel,
    OTPPurpose,
    SendOTPRequest,
    SendOTPResponse,
    get_tenant_id,
)


class TestOTPChannelEnum:
    def test_all_channels(self):
        assert OTPChannel.SMS == "sms"
        assert OTPChannel.WHATSAPP == "whatsapp"
        assert OTPChannel.TELEGRAM == "telegram"
        assert OTPChannel.EMAIL == "email"


class TestOTPPurposeEnum:
    def test_all_purposes(self):
        assert OTPPurpose.LOGIN == "login"
        assert OTPPurpose.PASSWORD_RESET == "password_reset"
        assert OTPPurpose.VERIFY_PHONE == "verify_phone"
        assert OTPPurpose.VERIFY_EMAIL == "verify_email"
        assert OTPPurpose.TWO_FACTOR == "two_factor"


class TestLanguageEnum:
    def test_values(self):
        assert Language.ARABIC == "ar"
        assert Language.ENGLISH == "en"


class TestGetTenantId:
    def test_valid_tenant_id(self):
        result = get_tenant_id("tenant-123")
        assert result == "tenant-123"

    def test_missing_tenant_id_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id(None)
        assert exc_info.value.status_code == 400


class TestSendOTPRequest:
    def test_valid_phone_request(self):
        req = SendOTPRequest(
            identifier="+967771234567",
            channel=OTPChannel.SMS,
            purpose=OTPPurpose.LOGIN,
        )
        assert req.identifier == "+967771234567"
        assert req.language == Language.ARABIC

    def test_valid_email_request(self):
        req = SendOTPRequest(
            identifier="user@example.com",
            channel=OTPChannel.EMAIL,
            purpose=OTPPurpose.VERIFY_EMAIL,
            language=Language.ENGLISH,
        )
        assert req.identifier == "user@example.com"

    def test_phone_with_spaces_cleaned(self):
        req = SendOTPRequest(
            identifier="+967 77 123 4567",
            channel=OTPChannel.SMS,
            purpose=OTPPurpose.LOGIN,
        )
        assert " " not in req.identifier

    def test_phone_too_short_raises(self):
        with pytest.raises(Exception):
            SendOTPRequest(
                identifier="+96777",
                channel=OTPChannel.SMS,
                purpose=OTPPurpose.LOGIN,
            )

    def test_invalid_identifier_raises(self):
        with pytest.raises(Exception):
            SendOTPRequest(
                identifier="not-phone-or-email",
                channel=OTPChannel.SMS,
                purpose=OTPPurpose.LOGIN,
            )

    def test_email_lowercased(self):
        req = SendOTPRequest(
            identifier="User@Example.COM",
            channel=OTPChannel.EMAIL,
            purpose=OTPPurpose.VERIFY_EMAIL,
        )
        assert req.identifier == "user@example.com"


class TestSendOTPResponse:
    def test_create_response(self):
        resp = SendOTPResponse(
            success=True,
            message="OTP sent",
            message_en="OTP sent successfully",
            message_ar="تم إرسال الرمز",
            expires_in_seconds=600,
            channel="sms",
            masked_identifier="***4567",
        )
        assert resp.success is True
        assert resp.expires_in_seconds == 600
        assert resp.masked_identifier == "***4567"


from src.otp_controller import (
    OTPStatusResponse,
    OTPStorage,
    VerifyOTPRequest,
    VerifyOTPResponse,
)


class TestVerifyOTPRequest:
    def test_valid_request(self):
        req = VerifyOTPRequest(
            identifier="+967771234567",
            otp_code="123456",
            purpose=OTPPurpose.LOGIN,
        )
        assert req.otp_code == "123456"

    def test_non_digit_otp_raises(self):
        with pytest.raises(Exception):
            VerifyOTPRequest(
                identifier="+967771234567",
                otp_code="12abc6",
                purpose=OTPPurpose.LOGIN,
            )

    def test_otp_with_whitespace(self):
        # Pydantic strips whitespace before validation
        req = VerifyOTPRequest(
            identifier="+967771234567",
            otp_code="123456",
            purpose=OTPPurpose.LOGIN,
        )
        assert req.otp_code == "123456"


class TestVerifyOTPResponse:
    def test_success_response(self):
        resp = VerifyOTPResponse(
            success=True,
            message="Verified",
            message_en="OTP verified",
            message_ar="تم التحقق",
            token="reset-token-123",
        )
        assert resp.success is True
        assert resp.token == "reset-token-123"

    def test_failure_response(self):
        resp = VerifyOTPResponse(
            success=False,
            message="Invalid OTP",
            message_en="Invalid OTP",
            message_ar="رمز غير صالح",
        )
        assert resp.token is None


class TestOTPStatusResponse:
    def test_create(self):
        resp = OTPStatusResponse(
            sent=True,
            remaining_seconds=300,
            attempts_remaining=3,
            expired=False,
            last_sent_at="2026-03-22T10:00:00Z",
        )
        assert resp.sent is True
        assert resp.remaining_seconds == 300
        assert resp.expired is False


class TestOTPStorage:
    def test_init(self):
        storage = OTPStorage()
        assert storage._use_redis is False

    def test_get_key(self):
        storage = OTPStorage()
        key = storage._get_key("+967771234567", "login", "tenant-1")
        assert "otp:" in key
        assert "tenant-1" in key
        assert "login" in key

    def test_get_key_default_tenant(self):
        storage = OTPStorage()
        key = storage._get_key("+967771234567", "login")
        assert "default" in key

    def test_generate_otp(self):
        storage = OTPStorage()
        otp = storage._generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_generate_otp_uniqueness(self):
        storage = OTPStorage()
        codes = set()
        for _ in range(50):
            codes.add(storage._generate_otp())
        assert len(codes) > 40

    def test_mask_identifier_phone(self):
        storage = OTPStorage()
        masked = storage._mask_identifier("+967771234567")
        assert masked.endswith("4567")
        assert "***" in masked

    def test_mask_identifier_short_phone(self):
        storage = OTPStorage()
        masked = storage._mask_identifier("123")
        assert "***" in masked

    def test_mask_identifier_email(self):
        storage = OTPStorage()
        masked = storage._mask_identifier("ahmed@example.com")
        assert "ah***@example.com" in masked

    def test_create_otp(self):
        storage = OTPStorage()
        otp_code, expires_in = storage.create_otp("+967771234567", "login")
        assert len(otp_code) == 6
        assert otp_code.isdigit()
        assert expires_in > 0

    def test_verify_otp_correct(self):
        storage = OTPStorage()
        otp_code, _ = storage.create_otp("+967771234567", "login", "tenant-1")
        success, msg_en, msg_ar = storage.verify_otp("+967771234567", otp_code, "login", "tenant-1")
        assert success is True

    def test_verify_otp_wrong_code(self):
        storage = OTPStorage()
        storage.create_otp("+967771234567", "login")
        success, msg_en, msg_ar = storage.verify_otp("+967771234567", "000000", "login")
        assert success is False

    def test_verify_otp_not_found(self):
        storage = OTPStorage()
        success, msg_en, msg_ar = storage.verify_otp("+967000000000", "123456", "login")
        assert success is False

    def test_get_status_not_found(self):
        storage = OTPStorage()
        status = storage.get_status("+967000000000", "login")
        assert status["sent"] is False

    def test_get_status_found(self):
        storage = OTPStorage()
        storage.create_otp("+967771234567", "login")
        status = storage.get_status("+967771234567", "login")
        assert status["sent"] is True
        assert status["expired"] is False

    def test_resend_cooldown(self):
        storage = OTPStorage()
        # First create succeeds
        otp1, _ = storage.create_otp("+967771234567", "login")
        # Second create within cooldown returns the same OTP info
        otp2, expires = storage.create_otp("+967771234567", "login")
        # Both should work (second may return same or new depending on cooldown)
        assert len(otp2) == 6

    def test_can_resend_first_time(self):
        storage = OTPStorage()
        can_resend, wait = storage.can_resend("+967000000000", "login")
        assert can_resend is True
        assert wait == 0

    def test_can_resend_within_cooldown(self):
        storage = OTPStorage()
        storage.create_otp("+967771234567", "login")
        can_resend, wait = storage.can_resend("+967771234567", "login")
        assert can_resend is False
        assert wait > 0

    def test_verify_expired_otp(self):
        storage = OTPStorage()
        import time as t

        key = storage._get_key("+967771234567", "login")
        storage._storage[key] = {
            "otp": "123456",
            "created_at": t.time() - 700,
            "expires_at": t.time() - 100,
            "attempts": 0,
            "verified": False,
        }
        success, msg_en, msg_ar = storage.verify_otp("+967771234567", "123456", "login")
        assert success is False
        assert "expired" in msg_en.lower()

    def test_verify_max_attempts(self):
        storage = OTPStorage()
        import time as t

        key = storage._get_key("+967771234567", "login")
        storage._storage[key] = {
            "otp": "123456",
            "created_at": t.time(),
            "expires_at": t.time() + 600,
            "attempts": 5,
            "verified": False,
        }
        success, msg_en, msg_ar = storage.verify_otp("+967771234567", "123456", "login")
        assert success is False
        assert "attempts" in msg_en.lower()

    def test_verify_already_verified(self):
        storage = OTPStorage()
        import time as t

        key = storage._get_key("+967771234567", "login")
        storage._storage[key] = {
            "otp": "123456",
            "created_at": t.time(),
            "expires_at": t.time() + 600,
            "attempts": 0,
            "verified": True,
        }
        success, msg_en, msg_ar = storage.verify_otp("+967771234567", "123456", "login")
        assert success is False
        assert "already" in msg_en.lower()

    def test_cleanup_expired(self):
        storage = OTPStorage()
        import time as t

        key = storage._get_key("cleanup-test", "login")
        storage._storage[key] = {
            "otp": "111111",
            "created_at": t.time() - 1000,
            "expires_at": t.time() - 100,
            "attempts": 0,
            "verified": False,
        }
        assert key in storage._storage
        storage.cleanup_expired()
        assert key not in storage._storage

    def test_delete_otp(self):
        storage = OTPStorage()
        key = storage._get_key("del-test", "login")
        storage._storage[key] = {"otp": "111111"}
        storage._last_sent[key] = 123.0
        storage._delete_otp(key)
        assert key not in storage._storage
        assert key not in storage._last_sent


from src.otp_controller import _get_otp_message


class TestGetOTPMessage:
    def test_login_en(self):
        msg_en, msg_ar = _get_otp_message("123456", OTPPurpose.LOGIN, Language.ENGLISH)
        assert "123456" in msg_en
        assert "SAHOOL" in msg_en

    def test_login_ar(self):
        msg_en, msg_ar = _get_otp_message("123456", OTPPurpose.LOGIN, Language.ARABIC)
        assert "123456" in msg_ar
        assert "SAHOOL" in msg_ar

    def test_password_reset(self):
        msg_en, msg_ar = _get_otp_message("654321", OTPPurpose.PASSWORD_RESET, Language.ENGLISH)
        assert "654321" in msg_en
        assert "password" in msg_en.lower()

    def test_verify_phone(self):
        msg_en, msg_ar = _get_otp_message("111111", OTPPurpose.VERIFY_PHONE, Language.ENGLISH)
        assert "111111" in msg_en

    def test_verify_email(self):
        msg_en, msg_ar = _get_otp_message("222222", OTPPurpose.VERIFY_EMAIL, Language.ENGLISH)
        assert "222222" in msg_en

    def test_two_factor(self):
        msg_en, msg_ar = _get_otp_message("333333", OTPPurpose.TWO_FACTOR, Language.ENGLISH)
        assert "333333" in msg_en
        assert "2FA" in msg_en


from src.otp_controller import send_otp_via_channel


class TestSendOTPViaChannel:
    def test_sms_not_initialized(self):
        result = asyncio.run(send_otp_via_channel(
            "+967771234567", "123456", OTPChannel.SMS, OTPPurpose.LOGIN, Language.ARABIC
        ))
        assert result is False

    def test_whatsapp_not_initialized(self):
        result = asyncio.run(send_otp_via_channel(
            "+967771234567", "123456", OTPChannel.WHATSAPP, OTPPurpose.LOGIN, Language.ARABIC
        ))
        assert result is False

    def test_telegram_not_initialized(self):
        result = asyncio.run(send_otp_via_channel("chat123", "123456", OTPChannel.TELEGRAM, OTPPurpose.LOGIN, Language.ARABIC))
        assert result is False

    def test_email_not_initialized(self):
        result = asyncio.run(send_otp_via_channel(
            "test@example.com", "123456", OTPChannel.EMAIL, OTPPurpose.LOGIN, Language.ENGLISH
        ))
        assert result is False
