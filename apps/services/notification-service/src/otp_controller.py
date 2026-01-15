"""
SAHOOL Notification Service - OTP Controller
وحدة التحكم في رموز التحقق OTP - FastAPI Routes

Handles HTTP endpoints for OTP (One-Time Password) operations:
- Sending OTP via SMS, WhatsApp, Telegram, Email
- Verifying OTP codes
- Checking OTP status

Security Features:
- Rate limiting (3 requests/minute for send)
- OTP expiration (10 minutes default)
- Maximum verification attempts (5)
- Secure random OTP generation
"""

import logging
import os
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator

# Import rate limiting decorator
try:
    from shared.middleware.rate_limit import rate_limit
    RATE_LIMIT_AVAILABLE = True
except ImportError:
    RATE_LIMIT_AVAILABLE = False
    # Fallback no-op decorator
    def rate_limit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import notification clients
from .email_client import get_email_client
from .sms_client import get_sms_client
from .telegram_client import get_telegram_client
from .whatsapp_client import get_whatsapp_client

logger = logging.getLogger("sahool-notifications.otp-controller")

# Create router
# Note: Router uses prefix="/otp" for OTP operations
# Kong handles /api/v1/otp routing with strip_path: true
router = APIRouter(prefix="/otp", tags=["OTP - رموز التحقق"])


# =============================================================================
# Enums
# =============================================================================


class OTPChannel(str, Enum):
    """قناة إرسال OTP - OTP Delivery Channel"""
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    EMAIL = "email"


class OTPPurpose(str, Enum):
    """غرض OTP - OTP Purpose"""
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"
    VERIFY_PHONE = "verify_phone"
    VERIFY_EMAIL = "verify_email"
    TWO_FACTOR = "two_factor"


class Language(str, Enum):
    """اللغة - Language"""
    ARABIC = "ar"
    ENGLISH = "en"


# =============================================================================
# Request/Response Models
# =============================================================================


class SendOTPRequest(BaseModel):
    """طلب إرسال OTP - Send OTP Request"""

    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Phone number (E.164) or email address | رقم الهاتف أو البريد الإلكتروني"
    )
    channel: OTPChannel = Field(
        ...,
        description="Delivery channel: sms, whatsapp, telegram, email | قناة الإرسال"
    )
    purpose: OTPPurpose = Field(
        ...,
        description="OTP purpose: login, password_reset, verify_phone, verify_email, two_factor | غرض OTP"
    )
    language: Language = Field(
        default=Language.ARABIC,
        description="Preferred language: ar, en | اللغة المفضلة"
    )
    tenant_id: str | None = Field(
        None,
        description="Tenant ID for multi-tenancy | معرف المستأجر"
    )

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """Validate identifier format"""
        v = v.strip()
        # Phone number validation (basic E.164 check)
        if v.startswith("+") or v[0].isdigit():
            # Remove spaces and dashes
            cleaned = "".join(c for c in v if c.isdigit() or c == "+")
            if len(cleaned) < 7 or len(cleaned) > 16:
                raise ValueError("Invalid phone number format | رقم هاتف غير صالح")
            return cleaned
        # Email validation (basic check)
        if "@" in v and "." in v:
            return v.lower()
        raise ValueError("Invalid identifier format (phone or email expected) | صيغة غير صالحة")

    class Config:
        json_schema_extra = {
            "example": {
                "identifier": "+967771234567",
                "channel": "sms",
                "purpose": "login",
                "language": "ar"
            }
        }


class SendOTPResponse(BaseModel):
    """استجابة إرسال OTP - Send OTP Response"""

    success: bool = Field(..., description="Whether OTP was sent successfully")
    message: str = Field(..., description="Response message (bilingual)")
    message_en: str = Field(..., description="English message")
    message_ar: str = Field(..., description="Arabic message")
    expires_in_seconds: int = Field(..., description="OTP validity period in seconds")
    channel: str = Field(..., description="Channel used to send OTP")
    masked_identifier: str = Field(..., description="Masked identifier for display")


class VerifyOTPRequest(BaseModel):
    """طلب التحقق من OTP - Verify OTP Request"""

    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Phone number or email used to send OTP | رقم الهاتف أو البريد"
    )
    otp_code: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="OTP code received | رمز التحقق"
    )
    purpose: OTPPurpose = Field(
        ...,
        description="OTP purpose (must match the sent OTP) | غرض OTP"
    )
    tenant_id: str | None = Field(
        None,
        description="Tenant ID for multi-tenancy | معرف المستأجر"
    )

    @field_validator("otp_code")
    @classmethod
    def validate_otp_code(cls, v: str) -> str:
        """Validate OTP code format"""
        v = v.strip()
        if not v.isdigit():
            raise ValueError("OTP code must contain only digits | يجب أن يحتوي الرمز على أرقام فقط")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "identifier": "+967771234567",
                "otp_code": "123456",
                "purpose": "login"
            }
        }


class VerifyOTPResponse(BaseModel):
    """استجابة التحقق من OTP - Verify OTP Response"""

    success: bool = Field(..., description="Whether OTP verification succeeded")
    message: str = Field(..., description="Response message (bilingual)")
    message_en: str = Field(..., description="English message")
    message_ar: str = Field(..., description="Arabic message")
    token: str | None = Field(
        None,
        description="Reset token (only for password_reset purpose) | رمز إعادة التعيين"
    )


class OTPStatusResponse(BaseModel):
    """استجابة حالة OTP - OTP Status Response"""

    sent: bool = Field(..., description="Whether OTP was sent")
    remaining_seconds: int = Field(..., description="Remaining validity in seconds")
    attempts_remaining: int = Field(..., description="Remaining verification attempts")
    expired: bool = Field(..., description="Whether OTP has expired")
    last_sent_at: str | None = Field(None, description="Last sent timestamp (ISO format)")


# =============================================================================
# OTP Storage (In-Memory with optional Redis)
# =============================================================================


class OTPStorage:
    """
    تخزين OTP - OTP Storage
    In-memory storage with optional Redis backend
    """

    # OTP configuration
    OTP_LENGTH = 6
    OTP_EXPIRY_SECONDS = 600  # 10 minutes
    MAX_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 60  # 1 minute between resends

    def __init__(self):
        # In-memory storage: {key: {otp, created_at, expires_at, attempts, verified}}
        self._storage: dict[str, dict[str, Any]] = {}
        self._last_sent: dict[str, float] = {}  # Rate limiting for resends
        self._redis_client = None
        self._use_redis = False

        # Try to initialize Redis
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis if available"""
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(redis_url)
                self._redis_client.ping()
                self._use_redis = True
                logger.info("OTP storage using Redis")
            except Exception as e:
                logger.warning(f"Redis not available for OTP storage, using in-memory: {e}")

    def _get_key(self, identifier: str, purpose: str, tenant_id: str | None = None) -> str:
        """Generate storage key"""
        tenant = tenant_id or "default"
        return f"otp:{tenant}:{purpose}:{identifier}"

    def _generate_otp(self) -> str:
        """Generate cryptographically secure OTP"""
        # Generate a secure random 6-digit code
        return "".join(str(secrets.randbelow(10)) for _ in range(self.OTP_LENGTH))

    def _mask_identifier(self, identifier: str) -> str:
        """Mask identifier for display"""
        if "@" in identifier:
            # Email: show first 2 chars and domain
            parts = identifier.split("@")
            masked_local = parts[0][:2] + "***"
            return f"{masked_local}@{parts[1]}"
        else:
            # Phone: show last 4 digits
            return f"***{identifier[-4:]}" if len(identifier) >= 4 else "***"

    def create_otp(
        self,
        identifier: str,
        purpose: str,
        tenant_id: str | None = None,
    ) -> tuple[str, int]:
        """
        Create a new OTP

        Returns:
            Tuple of (otp_code, expires_in_seconds)
        """
        key = self._get_key(identifier, purpose, tenant_id)
        otp_code = self._generate_otp()
        now = time.time()
        expires_at = now + self.OTP_EXPIRY_SECONDS

        otp_data = {
            "otp": otp_code,
            "created_at": now,
            "expires_at": expires_at,
            "attempts": 0,
            "verified": False,
            "identifier": identifier,
            "purpose": purpose,
        }

        if self._use_redis and self._redis_client:
            try:
                import json
                self._redis_client.setex(
                    key,
                    self.OTP_EXPIRY_SECONDS,
                    json.dumps(otp_data)
                )
            except Exception as e:
                logger.warning(f"Redis error, falling back to memory: {e}")
                self._storage[key] = otp_data
        else:
            self._storage[key] = otp_data

        # Track last sent time
        self._last_sent[key] = now

        return otp_code, self.OTP_EXPIRY_SECONDS

    def verify_otp(
        self,
        identifier: str,
        otp_code: str,
        purpose: str,
        tenant_id: str | None = None,
    ) -> tuple[bool, str, str]:
        """
        Verify OTP code

        Returns:
            Tuple of (success, message_en, message_ar)
        """
        key = self._get_key(identifier, purpose, tenant_id)
        otp_data = self._get_otp_data(key)

        if not otp_data:
            return False, "No OTP found for this identifier", "لم يتم العثور على رمز لهذا المعرف"

        # Check if already verified
        if otp_data.get("verified"):
            return False, "OTP already used", "تم استخدام الرمز مسبقاً"

        # Check expiration
        if time.time() > otp_data.get("expires_at", 0):
            self._delete_otp(key)
            return False, "OTP has expired", "انتهت صلاحية الرمز"

        # Check attempts
        attempts = otp_data.get("attempts", 0)
        if attempts >= self.MAX_ATTEMPTS:
            self._delete_otp(key)
            return False, "Maximum attempts exceeded", "تم تجاوز الحد الأقصى للمحاولات"

        # Verify code
        if otp_data.get("otp") != otp_code:
            # Increment attempts
            otp_data["attempts"] = attempts + 1
            self._save_otp_data(key, otp_data)
            remaining = self.MAX_ATTEMPTS - otp_data["attempts"]
            return (
                False,
                f"Invalid OTP code. {remaining} attempts remaining",
                f"رمز غير صحيح. متبقي {remaining} محاولات"
            )

        # Mark as verified
        otp_data["verified"] = True
        self._save_otp_data(key, otp_data)

        return True, "OTP verified successfully", "تم التحقق من الرمز بنجاح"

    def get_status(
        self,
        identifier: str,
        purpose: str,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """Get OTP status"""
        key = self._get_key(identifier, purpose, tenant_id)
        otp_data = self._get_otp_data(key)

        if not otp_data:
            return {
                "sent": False,
                "remaining_seconds": 0,
                "attempts_remaining": self.MAX_ATTEMPTS,
                "expired": True,
                "last_sent_at": None,
            }

        now = time.time()
        expires_at = otp_data.get("expires_at", 0)
        remaining = max(0, int(expires_at - now))
        attempts = otp_data.get("attempts", 0)

        return {
            "sent": True,
            "remaining_seconds": remaining,
            "attempts_remaining": max(0, self.MAX_ATTEMPTS - attempts),
            "expired": now > expires_at,
            "last_sent_at": datetime.fromtimestamp(
                otp_data.get("created_at", now)
            ).isoformat(),
        }

    def can_resend(
        self,
        identifier: str,
        purpose: str,
        tenant_id: str | None = None,
    ) -> tuple[bool, int]:
        """
        Check if OTP can be resent (cooldown check)

        Returns:
            Tuple of (can_resend, seconds_until_can_resend)
        """
        key = self._get_key(identifier, purpose, tenant_id)
        last_sent = self._last_sent.get(key, 0)
        now = time.time()
        elapsed = now - last_sent

        if elapsed < self.RESEND_COOLDOWN_SECONDS:
            wait_time = int(self.RESEND_COOLDOWN_SECONDS - elapsed)
            return False, wait_time

        return True, 0

    def _get_otp_data(self, key: str) -> dict[str, Any] | None:
        """Get OTP data from storage"""
        if self._use_redis and self._redis_client:
            try:
                import json
                data = self._redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        return self._storage.get(key)

    def _save_otp_data(self, key: str, data: dict[str, Any]):
        """Save OTP data to storage"""
        if self._use_redis and self._redis_client:
            try:
                import json
                ttl = max(1, int(data.get("expires_at", time.time()) - time.time()))
                self._redis_client.setex(key, ttl, json.dumps(data))
                return
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        self._storage[key] = data

    def _delete_otp(self, key: str):
        """Delete OTP from storage"""
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")

        self._storage.pop(key, None)
        self._last_sent.pop(key, None)

    def cleanup_expired(self):
        """Clean up expired OTPs from in-memory storage"""
        now = time.time()
        expired_keys = [
            key for key, data in self._storage.items()
            if data.get("expires_at", 0) < now
        ]
        for key in expired_keys:
            del self._storage[key]


# Global OTP storage instance
_otp_storage = OTPStorage()


# =============================================================================
# OTP Sending Functions
# =============================================================================


def _get_otp_message(otp_code: str, purpose: OTPPurpose, language: Language) -> tuple[str, str]:
    """Get OTP message based on purpose and language"""
    purpose_messages = {
        OTPPurpose.LOGIN: {
            "en": f"Your SAHOOL login code is: {otp_code}\n\nValid for 10 minutes.\nDo not share this code.",
            "ar": f"رمز تسجيل الدخول في SAHOOL: {otp_code}\n\nصالح لمدة 10 دقائق.\nلا تشارك هذا الرمز."
        },
        OTPPurpose.PASSWORD_RESET: {
            "en": f"Your SAHOOL password reset code is: {otp_code}\n\nValid for 10 minutes.\nIf you didn't request this, ignore this message.",
            "ar": f"رمز إعادة تعيين كلمة المرور في SAHOOL: {otp_code}\n\nصالح لمدة 10 دقائق.\nإذا لم تطلب ذلك، تجاهل هذه الرسالة."
        },
        OTPPurpose.VERIFY_PHONE: {
            "en": f"Your SAHOOL phone verification code is: {otp_code}\n\nValid for 10 minutes.",
            "ar": f"رمز التحقق من رقم الهاتف في SAHOOL: {otp_code}\n\nصالح لمدة 10 دقائق."
        },
        OTPPurpose.VERIFY_EMAIL: {
            "en": f"Your SAHOOL email verification code is: {otp_code}\n\nValid for 10 minutes.",
            "ar": f"رمز التحقق من البريد الإلكتروني في SAHOOL: {otp_code}\n\nصالح لمدة 10 دقائق."
        },
        OTPPurpose.TWO_FACTOR: {
            "en": f"Your SAHOOL 2FA code is: {otp_code}\n\nValid for 10 minutes.\nDo not share this code.",
            "ar": f"رمز التحقق الثنائي في SAHOOL: {otp_code}\n\nصالح لمدة 10 دقائق.\nلا تشارك هذا الرمز."
        },
    }

    messages = purpose_messages.get(purpose, purpose_messages[OTPPurpose.LOGIN])
    return messages["en"], messages["ar"]


async def send_otp_via_channel(
    identifier: str,
    otp_code: str,
    channel: OTPChannel,
    purpose: OTPPurpose,
    language: Language,
) -> bool:
    """Send OTP via the specified channel"""
    message_en, message_ar = _get_otp_message(otp_code, purpose, language)

    try:
        if channel == OTPChannel.SMS:
            sms_client = get_sms_client()
            if not sms_client._initialized:
                logger.warning("SMS client not initialized")
                return False

            result = await sms_client.send_sms(
                to=identifier,
                body=message_en,
                body_ar=message_ar,
                language=language.value,
            )
            return result is not None

        elif channel == OTPChannel.WHATSAPP:
            whatsapp_client = get_whatsapp_client()
            if not whatsapp_client._initialized:
                logger.warning("WhatsApp client not initialized")
                return False

            result = await whatsapp_client.send_otp(
                to=identifier,
                otp_code=otp_code,
                language=language.value,
            )
            return result is not None

        elif channel == OTPChannel.TELEGRAM:
            telegram_client = get_telegram_client()
            if not telegram_client._initialized:
                logger.warning("Telegram client not initialized")
                return False

            result = await telegram_client.send_otp(
                chat_id=identifier,
                otp_code=otp_code,
                language=language.value,
            )
            return result is not None

        elif channel == OTPChannel.EMAIL:
            email_client = get_email_client()
            if not email_client._initialized:
                logger.warning("Email client not initialized")
                return False

            subject = "SAHOOL Verification Code" if language == Language.ENGLISH else "رمز التحقق من SAHOOL"
            result = await email_client.send_email(
                to=identifier,
                subject=subject,
                subject_ar="رمز التحقق من SAHOOL",
                body=message_en,
                body_ar=message_ar,
                language=language.value,
            )
            return result is not None

        else:
            logger.error(f"Unknown OTP channel: {channel}")
            return False

    except Exception as e:
        logger.error(f"Failed to send OTP via {channel.value}: {e}")
        return False


# =============================================================================
# API Endpoints
# =============================================================================


@router.post(
    "/send",
    response_model=SendOTPResponse,
    summary="إرسال رمز OTP - Send OTP Code",
    responses={
        200: {"description": "OTP sent successfully"},
        400: {"description": "Invalid request"},
        429: {"description": "Too many requests - rate limited"},
        503: {"description": "Channel unavailable"},
    },
)
@rate_limit(requests_per_minute=3, requests_per_hour=20, burst_limit=2)
async def send_otp(request: Request, body: SendOTPRequest):
    """
    إرسال رمز OTP إلى المستخدم
    Send OTP code to user via specified channel

    Rate limited to 3 requests per minute.

    Channels:
    - **sms**: SMS text message (requires phone number in E.164 format)
    - **whatsapp**: WhatsApp message (requires phone number)
    - **telegram**: Telegram message (requires Telegram chat ID)
    - **email**: Email message (requires email address)

    Purposes:
    - **login**: User login verification
    - **password_reset**: Password reset request
    - **verify_phone**: Phone number verification
    - **verify_email**: Email address verification
    - **two_factor**: Two-factor authentication
    """
    # Check resend cooldown
    can_resend, wait_seconds = _otp_storage.can_resend(
        identifier=body.identifier,
        purpose=body.purpose.value,
        tenant_id=body.tenant_id,
    )

    if not can_resend:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limited",
                "error_ar": "تم تجاوز حد الطلبات",
                "message": f"Please wait {wait_seconds} seconds before requesting a new OTP",
                "message_ar": f"يرجى الانتظار {wait_seconds} ثانية قبل طلب رمز جديد",
                "retry_after": wait_seconds,
            }
        )

    # Validate channel-identifier compatibility
    if body.channel in [OTPChannel.SMS, OTPChannel.WHATSAPP]:
        if "@" in body.identifier:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid identifier for channel",
                    "error_ar": "معرف غير صالح للقناة",
                    "message": f"Phone number required for {body.channel.value} channel",
                    "message_ar": f"مطلوب رقم هاتف لقناة {body.channel.value}",
                }
            )
    elif body.channel == OTPChannel.EMAIL:
        if "@" not in body.identifier:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid identifier for channel",
                    "error_ar": "معرف غير صالح للقناة",
                    "message": "Email address required for email channel",
                    "message_ar": "مطلوب بريد إلكتروني لقناة البريد",
                }
            )

    # Generate OTP
    otp_code, expires_in = _otp_storage.create_otp(
        identifier=body.identifier,
        purpose=body.purpose.value,
        tenant_id=body.tenant_id,
    )

    # Send OTP via channel
    send_success = await send_otp_via_channel(
        identifier=body.identifier,
        otp_code=otp_code,
        channel=body.channel,
        purpose=body.purpose,
        language=body.language,
    )

    if not send_success:
        # Channel unavailable
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Channel unavailable",
                "error_ar": "القناة غير متاحة",
                "message": f"Failed to send OTP via {body.channel.value}. Please try another channel.",
                "message_ar": f"فشل إرسال الرمز عبر {body.channel.value}. جرب قناة أخرى.",
            }
        )

    masked = _otp_storage._mask_identifier(body.identifier)

    logger.info(
        f"OTP sent to {masked} via {body.channel.value} for {body.purpose.value}"
    )

    return SendOTPResponse(
        success=True,
        message="تم إرسال رمز التحقق بنجاح" if body.language == Language.ARABIC else "OTP sent successfully",
        message_en="OTP sent successfully",
        message_ar="تم إرسال رمز التحقق بنجاح",
        expires_in_seconds=expires_in,
        channel=body.channel.value,
        masked_identifier=masked,
    )


@router.post(
    "/verify",
    response_model=VerifyOTPResponse,
    summary="التحقق من رمز OTP - Verify OTP Code",
    responses={
        200: {"description": "Verification result"},
        400: {"description": "Invalid request"},
        401: {"description": "Invalid or expired OTP"},
    },
)
async def verify_otp(body: VerifyOTPRequest):
    """
    التحقق من رمز OTP
    Verify the OTP code entered by user

    Returns success status and optional reset token (for password reset purpose).
    """
    success, message_en, message_ar = _otp_storage.verify_otp(
        identifier=body.identifier,
        otp_code=body.otp_code,
        purpose=body.purpose.value,
        tenant_id=body.tenant_id,
    )

    # Generate reset token for password reset purpose
    reset_token = None
    if success and body.purpose == OTPPurpose.PASSWORD_RESET:
        # Generate a secure reset token
        reset_token = secrets.token_urlsafe(32)
        # In production, store this token and associate with user
        logger.info(f"Password reset token generated for {_otp_storage._mask_identifier(body.identifier)}")

    if not success:
        # Return 200 with success=False for invalid OTP (not 401)
        # This allows client to show remaining attempts
        return VerifyOTPResponse(
            success=False,
            message=message_ar,
            message_en=message_en,
            message_ar=message_ar,
            token=None,
        )

    logger.info(
        f"OTP verified for {_otp_storage._mask_identifier(body.identifier)} "
        f"purpose={body.purpose.value}"
    )

    return VerifyOTPResponse(
        success=True,
        message=message_ar,
        message_en=message_en,
        message_ar=message_ar,
        token=reset_token,
    )


@router.get(
    "/status",
    response_model=OTPStatusResponse,
    summary="حالة OTP - OTP Status",
    responses={
        200: {"description": "OTP status information"},
    },
)
async def get_otp_status(
    identifier: str = Query(
        ...,
        min_length=3,
        description="Phone number or email | رقم الهاتف أو البريد"
    ),
    purpose: OTPPurpose = Query(
        ...,
        description="OTP purpose | غرض OTP"
    ),
    tenant_id: str | None = Query(
        None,
        description="Tenant ID | معرف المستأجر"
    ),
):
    """
    التحقق من حالة OTP
    Check OTP status including:
    - Whether OTP was sent
    - Remaining validity time
    - Remaining verification attempts
    """
    status = _otp_storage.get_status(
        identifier=identifier.strip(),
        purpose=purpose.value,
        tenant_id=tenant_id,
    )

    return OTPStatusResponse(
        sent=status["sent"],
        remaining_seconds=status["remaining_seconds"],
        attempts_remaining=status["attempts_remaining"],
        expired=status["expired"],
        last_sent_at=status["last_sent_at"],
    )


# =============================================================================
# Error Messages (Bilingual)
# =============================================================================

ERROR_MESSAGES = {
    "rate_limited": {
        "en": "Too many requests. Please try again later.",
        "ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
    },
    "invalid_channel": {
        "en": "Invalid notification channel",
        "ar": "قناة إشعار غير صالحة",
    },
    "invalid_identifier": {
        "en": "Invalid phone number or email address",
        "ar": "رقم هاتف أو بريد إلكتروني غير صالح",
    },
    "otp_expired": {
        "en": "OTP has expired. Please request a new one.",
        "ar": "انتهت صلاحية الرمز. يرجى طلب رمز جديد.",
    },
    "invalid_otp": {
        "en": "Invalid OTP code",
        "ar": "رمز تحقق غير صحيح",
    },
    "max_attempts": {
        "en": "Maximum verification attempts exceeded",
        "ar": "تم تجاوز الحد الأقصى للمحاولات",
    },
    "channel_unavailable": {
        "en": "Notification channel is currently unavailable",
        "ar": "قناة الإشعار غير متاحة حالياً",
    },
}
