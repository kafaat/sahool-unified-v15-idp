"""
SAHOOL OTP Service - One-Time Password Management
خدمة رموز التحقق لمرة واحدة

Features:
- Secure 6-digit OTP generation
- Multi-channel delivery: SMS, WhatsApp, Telegram, Email
- Redis-based storage with expiration (fallback to in-memory)
- Rate limiting (max 3 requests per minute)
- Bilingual support (Arabic/English)
- Password reset flow support
- Proper logging and error handling

Author: SAHOOL Platform Team
License: Proprietary
"""

import hashlib
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Constants & Configuration
# ═══════════════════════════════════════════════════════════════════════════════

OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 600  # 10 minutes
RATE_LIMIT_WINDOW_SECONDS = 60  # 1 minute
RATE_LIMIT_MAX_REQUESTS = 3


class OTPChannel(str, Enum):
    """قنوات إرسال OTP - OTP delivery channels"""

    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    EMAIL = "email"


class OTPPurpose(str, Enum):
    """أغراض OTP - OTP purposes"""

    LOGIN = "login"
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    PHONE_VERIFICATION = "phone_verification"
    EMAIL_VERIFICATION = "email_verification"
    TRANSACTION = "transaction"
    TWO_FACTOR = "two_factor"


@dataclass
class OTPRecord:
    """سجل OTP - OTP Record"""

    user_id: str
    otp_hash: str  # Hashed OTP for security
    purpose: str
    channel: str
    destination: str  # Phone or email (partially masked for logging)
    created_at: float
    expires_at: float
    attempts: int = 0
    max_attempts: int = 3
    verified: bool = False

    def is_expired(self) -> bool:
        """التحقق من انتهاء الصلاحية"""
        return time.time() > self.expires_at

    def has_attempts_remaining(self) -> bool:
        """التحقق من وجود محاولات متبقية"""
        return self.attempts < self.max_attempts

    def time_remaining(self) -> int:
        """الوقت المتبقي بالثواني"""
        remaining = self.expires_at - time.time()
        return max(0, int(remaining))

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى dictionary"""
        return {
            "user_id": self.user_id,
            "otp_hash": self.otp_hash,
            "purpose": self.purpose,
            "channel": self.channel,
            "destination": self.destination,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "verified": self.verified,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OTPRecord":
        """إنشاء من dictionary"""
        return cls(
            user_id=data["user_id"],
            otp_hash=data["otp_hash"],
            purpose=data["purpose"],
            channel=data["channel"],
            destination=data["destination"],
            created_at=float(data["created_at"]),
            expires_at=float(data["expires_at"]),
            attempts=int(data.get("attempts", 0)),
            max_attempts=int(data.get("max_attempts", 3)),
            verified=data.get("verified", False),
        )


@dataclass
class OTPResult:
    """نتيجة عملية OTP - OTP operation result"""

    success: bool
    message: str
    message_ar: str
    otp_sent: bool = False
    time_remaining: int | None = None
    attempts_remaining: int | None = None
    delivery_id: str | None = None
    error_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى dictionary"""
        result = {
            "success": self.success,
            "message": self.message,
            "message_ar": self.message_ar,
        }
        if self.otp_sent:
            result["otp_sent"] = self.otp_sent
        if self.time_remaining is not None:
            result["time_remaining"] = self.time_remaining
        if self.attempts_remaining is not None:
            result["attempts_remaining"] = self.attempts_remaining
        if self.delivery_id:
            result["delivery_id"] = self.delivery_id
        if self.error_code:
            result["error_code"] = self.error_code
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Storage (Fallback for testing)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class InMemoryStorage:
    """
    تخزين في الذاكرة (للاختبار)
    In-memory storage fallback for testing when Redis is unavailable
    """

    _otp_store: dict[str, dict[str, Any]] = field(default_factory=dict)
    _rate_limit_store: dict[str, list[float]] = field(default_factory=dict)

    async def set_otp(self, key: str, record: OTPRecord) -> bool:
        """تخزين OTP"""
        self._otp_store[key] = record.to_dict()
        return True

    async def get_otp(self, key: str) -> OTPRecord | None:
        """استرجاع OTP"""
        data = self._otp_store.get(key)
        if data:
            return OTPRecord.from_dict(data)
        return None

    async def delete_otp(self, key: str) -> bool:
        """حذف OTP"""
        if key in self._otp_store:
            del self._otp_store[key]
            return True
        return False

    async def update_otp(self, key: str, record: OTPRecord) -> bool:
        """تحديث OTP"""
        self._otp_store[key] = record.to_dict()
        return True

    async def check_rate_limit(self, key: str) -> tuple[bool, int]:
        """
        التحقق من حد المعدل
        Returns: (allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW_SECONDS

        # Clean old entries
        if key in self._rate_limit_store:
            self._rate_limit_store[key] = [
                t for t in self._rate_limit_store[key] if t > window_start
            ]
        else:
            self._rate_limit_store[key] = []

        request_count = len(self._rate_limit_store[key])

        if request_count >= RATE_LIMIT_MAX_REQUESTS:
            return False, 0

        return True, RATE_LIMIT_MAX_REQUESTS - request_count

    async def record_request(self, key: str) -> None:
        """تسجيل طلب للحد من المعدل"""
        now = time.time()
        if key not in self._rate_limit_store:
            self._rate_limit_store[key] = []
        self._rate_limit_store[key].append(now)

    def clear(self) -> None:
        """مسح جميع البيانات (للاختبار)"""
        self._otp_store.clear()
        self._rate_limit_store.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# OTP Service Class
# ═══════════════════════════════════════════════════════════════════════════════


class OTPService:
    """
    خدمة رموز التحقق لمرة واحدة
    OTP (One-Time Password) Service

    Features:
        - Secure 6-digit OTP generation
        - Multi-channel delivery (SMS, WhatsApp, Telegram, Email)
        - Redis storage with automatic expiration
        - Rate limiting to prevent abuse
        - Bilingual messages (Arabic/English)
        - Password reset flow support

    Example:
        >>> otp_service = OTPService()
        >>> await otp_service.initialize()
        >>>
        >>> # Generate and send OTP
        >>> result = await otp_service.generate_otp(
        ...     user_id="user123",
        ...     phone_or_email="+967771234567",
        ...     channel=OTPChannel.SMS,
        ...     purpose=OTPPurpose.LOGIN
        ... )
        >>>
        >>> # Verify OTP
        >>> result = await otp_service.verify_otp(
        ...     user_id="user123",
        ...     otp_code="123456",
        ...     purpose=OTPPurpose.LOGIN
        ... )
    """

    def __init__(self):
        self._initialized = False
        self._redis_client = None
        self._in_memory_storage = InMemoryStorage()
        self._use_redis = False

        # Channel clients (lazy loaded)
        self._sms_client = None
        self._whatsapp_client = None
        self._telegram_client = None
        self._email_client = None

    async def initialize(self, use_redis: bool = True) -> bool:
        """
        تهيئة خدمة OTP

        Args:
            use_redis: استخدام Redis (إذا كان متاحاً)

        Returns:
            True if initialization successful
        """
        if self._initialized:
            logger.info("OTP service already initialized")
            return True

        try:
            # Try to initialize Redis client
            if use_redis:
                try:
                    from shared.cache import get_redis_client

                    self._redis_client = get_redis_client()
                    if self._redis_client.ping():
                        self._use_redis = True
                        logger.info("OTP service initialized with Redis storage")
                    else:
                        logger.warning(
                            "Redis ping failed, falling back to in-memory storage"
                        )
                        self._use_redis = False
                except ImportError:
                    logger.warning(
                        "Redis client not available, using in-memory storage"
                    )
                    self._use_redis = False
                except Exception as e:
                    logger.warning(
                        f"Failed to connect to Redis: {e}, using in-memory storage"
                    )
                    self._use_redis = False
            else:
                self._use_redis = False
                logger.info("OTP service initialized with in-memory storage (testing mode)")

            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize OTP service: {e}")
            return False

    def _get_sms_client(self):
        """الحصول على عميل SMS (lazy loading)"""
        if self._sms_client is None:
            try:
                from .sms_client import get_sms_client

                self._sms_client = get_sms_client()
            except ImportError:
                logger.warning("SMS client not available")
        return self._sms_client

    def _get_whatsapp_client(self):
        """الحصول على عميل WhatsApp (lazy loading)"""
        if self._whatsapp_client is None:
            try:
                from .whatsapp_client import get_whatsapp_client

                self._whatsapp_client = get_whatsapp_client()
            except ImportError:
                logger.warning("WhatsApp client not available")
        return self._whatsapp_client

    def _get_telegram_client(self):
        """الحصول على عميل Telegram (lazy loading)"""
        if self._telegram_client is None:
            try:
                from .telegram_client import get_telegram_client

                self._telegram_client = get_telegram_client()
            except ImportError:
                logger.warning("Telegram client not available")
        return self._telegram_client

    def _get_email_client(self):
        """الحصول على عميل Email (lazy loading)"""
        if self._email_client is None:
            try:
                from .email_client import get_email_client

                self._email_client = get_email_client()
            except ImportError:
                logger.warning("Email client not available")
        return self._email_client

    def _check_initialized(self) -> bool:
        """التحقق من التهيئة"""
        if not self._initialized:
            logger.warning("OTP service not initialized. Call initialize() first.")
            return False
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # OTP Key Generation
    # ─────────────────────────────────────────────────────────────────────────

    def _get_otp_key(self, user_id: str, purpose: str) -> str:
        """
        إنشاء مفتاح OTP للتخزين

        Args:
            user_id: معرف المستخدم
            purpose: الغرض من OTP

        Returns:
            مفتاح التخزين
        """
        return f"otp:{user_id}:{purpose}"

    def _get_rate_limit_key(self, user_id: str, channel: str) -> str:
        """
        إنشاء مفتاح حد المعدل

        Args:
            user_id: معرف المستخدم
            channel: القناة

        Returns:
            مفتاح حد المعدل
        """
        return f"otp_rate:{user_id}:{channel}"

    # ─────────────────────────────────────────────────────────────────────────
    # OTP Generation & Hashing
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_otp_code(self, length: int = OTP_LENGTH) -> str:
        """
        إنشاء رمز OTP آمن

        Args:
            length: طول الرمز

        Returns:
            رمز OTP
        """
        # Use secrets module for cryptographically secure random numbers
        otp = "".join([str(secrets.randbelow(10)) for _ in range(length)])
        return otp

    def _hash_otp(self, otp_code: str, user_id: str) -> str:
        """
        تشفير OTP للتخزين الآمن

        Args:
            otp_code: رمز OTP
            user_id: معرف المستخدم (salt)

        Returns:
            OTP مشفر
        """
        # Use SHA-256 with user_id as salt for secure hashing
        salt = f"{user_id}:{os.getenv('JWT_SECRET_KEY', 'default-secret')}"
        combined = f"{otp_code}:{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _verify_otp_hash(self, otp_code: str, user_id: str, stored_hash: str) -> bool:
        """
        التحقق من صحة OTP

        Args:
            otp_code: رمز OTP المدخل
            user_id: معرف المستخدم
            stored_hash: Hash المخزن

        Returns:
            True إذا كان صحيحاً
        """
        computed_hash = self._hash_otp(otp_code, user_id)
        return secrets.compare_digest(computed_hash, stored_hash)

    def _mask_destination(self, destination: str, channel: str) -> str:
        """
        إخفاء جزء من الوجهة للخصوصية

        Args:
            destination: الهاتف أو البريد
            channel: القناة

        Returns:
            وجهة مخفية جزئياً
        """
        if channel == OTPChannel.EMAIL:
            # Mask email: show first 2 chars and domain
            if "@" in destination:
                local, domain = destination.split("@", 1)
                if len(local) > 2:
                    masked_local = local[:2] + "*" * (len(local) - 2)
                else:
                    masked_local = local[0] + "*" if len(local) > 0 else "*"
                return f"{masked_local}@{domain}"
        else:
            # Mask phone: show last 4 digits
            if len(destination) > 4:
                return "*" * (len(destination) - 4) + destination[-4:]
        return destination

    # ─────────────────────────────────────────────────────────────────────────
    # Storage Operations
    # ─────────────────────────────────────────────────────────────────────────

    async def _store_otp(self, key: str, record: OTPRecord) -> bool:
        """تخزين OTP"""
        try:
            if self._use_redis:
                import json

                ttl = int(record.expires_at - time.time())
                if ttl > 0:
                    self._redis_client.set(key, json.dumps(record.to_dict()), ex=ttl)
                    return True
                return False
            else:
                return await self._in_memory_storage.set_otp(key, record)
        except Exception as e:
            logger.error(f"Failed to store OTP: {e}")
            return False

    async def _get_otp(self, key: str) -> OTPRecord | None:
        """استرجاع OTP"""
        try:
            if self._use_redis:
                import json

                data = self._redis_client.get(key)
                if data:
                    return OTPRecord.from_dict(json.loads(data))
                return None
            else:
                return await self._in_memory_storage.get_otp(key)
        except Exception as e:
            logger.error(f"Failed to get OTP: {e}")
            return None

    async def _delete_otp(self, key: str) -> bool:
        """حذف OTP"""
        try:
            if self._use_redis:
                self._redis_client.delete(key)
                return True
            else:
                return await self._in_memory_storage.delete_otp(key)
        except Exception as e:
            logger.error(f"Failed to delete OTP: {e}")
            return False

    async def _update_otp(self, key: str, record: OTPRecord) -> bool:
        """تحديث OTP"""
        try:
            if self._use_redis:
                import json

                ttl = int(record.expires_at - time.time())
                if ttl > 0:
                    self._redis_client.set(key, json.dumps(record.to_dict()), ex=ttl)
                    return True
                return False
            else:
                return await self._in_memory_storage.update_otp(key, record)
        except Exception as e:
            logger.error(f"Failed to update OTP: {e}")
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Rate Limiting
    # ─────────────────────────────────────────────────────────────────────────

    async def _check_rate_limit(self, user_id: str, channel: str) -> tuple[bool, int]:
        """
        التحقق من حد المعدل

        Args:
            user_id: معرف المستخدم
            channel: القناة

        Returns:
            (allowed, remaining_requests)
        """
        rate_key = self._get_rate_limit_key(user_id, channel)

        try:
            if self._use_redis:
                now = time.time()
                window_start = now - RATE_LIMIT_WINDOW_SECONDS

                # Use sorted set for rate limiting
                rate_key_zset = f"{rate_key}:requests"

                # Remove old entries
                self._redis_client._master.zremrangebyscore(
                    rate_key_zset, "-inf", window_start
                )

                # Count current requests
                request_count = self._redis_client._master.zcard(rate_key_zset)

                if request_count >= RATE_LIMIT_MAX_REQUESTS:
                    return False, 0

                return True, RATE_LIMIT_MAX_REQUESTS - request_count
            else:
                return await self._in_memory_storage.check_rate_limit(rate_key)
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Default to allowing the request on error
            return True, RATE_LIMIT_MAX_REQUESTS

    async def _record_rate_limit(self, user_id: str, channel: str) -> None:
        """تسجيل طلب للحد من المعدل"""
        rate_key = self._get_rate_limit_key(user_id, channel)

        try:
            if self._use_redis:
                now = time.time()
                rate_key_zset = f"{rate_key}:requests"

                # Add current timestamp to sorted set
                self._redis_client._master.zadd(rate_key_zset, {str(now): now})

                # Set expiration on the key
                self._redis_client._master.expire(
                    rate_key_zset, RATE_LIMIT_WINDOW_SECONDS * 2
                )
            else:
                await self._in_memory_storage.record_request(rate_key)
        except Exception as e:
            logger.error(f"Failed to record rate limit: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # OTP Message Templates
    # ─────────────────────────────────────────────────────────────────────────

    def _get_otp_message(
        self, otp_code: str, purpose: str, language: str = "ar"
    ) -> tuple[str, str]:
        """
        الحصول على رسالة OTP

        Args:
            otp_code: رمز OTP
            purpose: الغرض
            language: اللغة

        Returns:
            (subject, body) for email, (None, body) for others
        """
        purpose_labels = {
            OTPPurpose.LOGIN: ("تسجيل الدخول", "Login"),
            OTPPurpose.REGISTRATION: ("التسجيل", "Registration"),
            OTPPurpose.PASSWORD_RESET: ("إعادة تعيين كلمة المرور", "Password Reset"),
            OTPPurpose.PHONE_VERIFICATION: ("التحقق من الهاتف", "Phone Verification"),
            OTPPurpose.EMAIL_VERIFICATION: ("التحقق من البريد", "Email Verification"),
            OTPPurpose.TRANSACTION: ("التحقق من المعاملة", "Transaction Verification"),
            OTPPurpose.TWO_FACTOR: ("المصادقة الثنائية", "Two-Factor Authentication"),
        }

        purpose_ar, purpose_en = purpose_labels.get(
            purpose, ("التحقق", "Verification")
        )

        if language == "ar":
            subject = f"رمز التحقق - {purpose_ar} | SAHOOL"
            body = f"""رمز التحقق الخاص بك في SAHOOL ({purpose_ar}):

{otp_code}

هذا الرمز صالح لمدة 10 دقائق.
لا تشارك هذا الرمز مع أي شخص.

إذا لم تطلب هذا الرمز، تجاهل هذه الرسالة.

---
SAHOOL - منصة الزراعة الذكية"""
        else:
            subject = f"Verification Code - {purpose_en} | SAHOOL"
            body = f"""Your SAHOOL verification code ({purpose_en}):

{otp_code}

This code is valid for 10 minutes.
Do not share this code with anyone.

If you didn't request this code, ignore this message.

---
SAHOOL - Smart Agriculture Platform"""

        return subject, body

    def _get_otp_html_email(
        self, otp_code: str, purpose: str, language: str = "ar"
    ) -> tuple[str, str]:
        """
        الحصول على رسالة OTP بصيغة HTML للبريد

        Args:
            otp_code: رمز OTP
            purpose: الغرض
            language: اللغة

        Returns:
            (subject, html_body)
        """
        purpose_labels = {
            OTPPurpose.LOGIN: ("تسجيل الدخول", "Login"),
            OTPPurpose.REGISTRATION: ("التسجيل", "Registration"),
            OTPPurpose.PASSWORD_RESET: ("إعادة تعيين كلمة المرور", "Password Reset"),
            OTPPurpose.PHONE_VERIFICATION: ("التحقق من الهاتف", "Phone Verification"),
            OTPPurpose.EMAIL_VERIFICATION: ("التحقق من البريد", "Email Verification"),
            OTPPurpose.TRANSACTION: ("التحقق من المعاملة", "Transaction Verification"),
            OTPPurpose.TWO_FACTOR: ("المصادقة الثنائية", "Two-Factor Authentication"),
        }

        purpose_ar, purpose_en = purpose_labels.get(
            purpose, ("التحقق", "Verification")
        )

        if language == "ar":
            subject = f"رمز التحقق - {purpose_ar} | SAHOOL"
            html_body = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
        .logo {{ color: #4CAF50; font-size: 28px; font-weight: bold; }}
        .otp-code {{ background: linear-gradient(135deg, #4CAF50, #45a049); color: white; font-size: 32px; letter-spacing: 8px; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; font-weight: bold; }}
        .message {{ color: #333; line-height: 1.8; font-size: 16px; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 20px 0; color: #856404; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SAHOOL</div>
            <p style="color: #666; margin: 5px 0;">منصة الزراعة الذكية</p>
        </div>

        <div class="message">
            <h2 style="color: #333;">رمز التحقق - {purpose_ar}</h2>
            <p>رمز التحقق الخاص بك هو:</p>
        </div>

        <div class="otp-code">{otp_code}</div>

        <div class="warning">
            <strong>تنبيه:</strong>
            <ul style="margin: 10px 0; padding-right: 20px;">
                <li>هذا الرمز صالح لمدة <strong>10 دقائق</strong> فقط</li>
                <li>لا تشارك هذا الرمز مع أي شخص</li>
                <li>فريق SAHOOL لن يطلب منك هذا الرمز أبداً</li>
            </ul>
        </div>

        <p class="message">إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة.</p>

        <div class="footer">
            <p>SAHOOL - منصة الزراعة الذكية الوطنية</p>
            <p>جميع الحقوق محفوظة &copy; 2025</p>
        </div>
    </div>
</body>
</html>
"""
        else:
            subject = f"Verification Code - {purpose_en} | SAHOOL"
            html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
        .logo {{ color: #4CAF50; font-size: 28px; font-weight: bold; }}
        .otp-code {{ background: linear-gradient(135deg, #4CAF50, #45a049); color: white; font-size: 32px; letter-spacing: 8px; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; font-weight: bold; }}
        .message {{ color: #333; line-height: 1.8; font-size: 16px; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 20px 0; color: #856404; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">SAHOOL</div>
            <p style="color: #666; margin: 5px 0;">Smart Agriculture Platform</p>
        </div>

        <div class="message">
            <h2 style="color: #333;">Verification Code - {purpose_en}</h2>
            <p>Your verification code is:</p>
        </div>

        <div class="otp-code">{otp_code}</div>

        <div class="warning">
            <strong>Important:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>This code is valid for <strong>10 minutes</strong> only</li>
                <li>Do not share this code with anyone</li>
                <li>SAHOOL team will never ask you for this code</li>
            </ul>
        </div>

        <p class="message">If you didn't request this code, please ignore this message.</p>

        <div class="footer">
            <p>SAHOOL - National Smart Agriculture Platform</p>
            <p>All rights reserved &copy; 2025</p>
        </div>
    </div>
</body>
</html>
"""

        return subject, html_body

    # ─────────────────────────────────────────────────────────────────────────
    # OTP Delivery
    # ─────────────────────────────────────────────────────────────────────────

    async def _send_otp_via_sms(
        self, phone: str, otp_code: str, purpose: str, language: str
    ) -> str | None:
        """إرسال OTP عبر SMS"""
        client = self._get_sms_client()
        if not client:
            logger.error("SMS client not available")
            return None

        _, body = self._get_otp_message(otp_code, purpose, language)
        _, body_ar = self._get_otp_message(otp_code, purpose, "ar")

        return await client.send_sms(
            to=phone, body=body if language != "ar" else body_ar, body_ar=body_ar, language=language
        )

    async def _send_otp_via_whatsapp(
        self, phone: str, otp_code: str, purpose: str, language: str
    ) -> str | None:
        """إرسال OTP عبر WhatsApp"""
        client = self._get_whatsapp_client()
        if not client:
            logger.error("WhatsApp client not available")
            return None

        return await client.send_otp(to=phone, otp_code=otp_code, language=language)

    async def _send_otp_via_telegram(
        self, chat_id: str, otp_code: str, purpose: str, language: str
    ) -> int | None:
        """إرسال OTP عبر Telegram"""
        client = self._get_telegram_client()
        if not client:
            logger.error("Telegram client not available")
            return None

        return await client.send_otp(chat_id=chat_id, otp_code=otp_code, language=language)

    async def _send_otp_via_email(
        self, email: str, otp_code: str, purpose: str, language: str
    ) -> str | None:
        """إرسال OTP عبر Email"""
        client = self._get_email_client()
        if not client:
            logger.error("Email client not available")
            return None

        subject, html_body = self._get_otp_html_email(otp_code, purpose, language)
        subject_ar, html_body_ar = self._get_otp_html_email(otp_code, purpose, "ar")

        return await client.send_email(
            to=email,
            subject=subject if language != "ar" else subject_ar,
            body=html_body if language != "ar" else html_body_ar,
            subject_ar=subject_ar,
            body_ar=html_body_ar,
            language=language,
            is_html=True,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Public API Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_otp(
        self,
        user_id: str,
        phone_or_email: str,
        channel: OTPChannel | str,
        purpose: OTPPurpose | str,
        language: str = "ar",
    ) -> OTPResult:
        """
        إنشاء وإرسال رمز OTP

        Args:
            user_id: معرف المستخدم
            phone_or_email: رقم الهاتف أو البريد الإلكتروني
            channel: قناة الإرسال (sms, whatsapp, telegram, email)
            purpose: الغرض من OTP
            language: اللغة (ar, en)

        Returns:
            OTPResult مع حالة العملية
        """
        if not self._check_initialized():
            return OTPResult(
                success=False,
                message="OTP service not initialized",
                message_ar="خدمة OTP غير مهيأة",
                error_code="SERVICE_NOT_INITIALIZED",
            )

        # Convert string to enum if needed
        if isinstance(channel, str):
            channel = OTPChannel(channel)
        if isinstance(purpose, str):
            purpose = OTPPurpose(purpose)

        # Check rate limit
        allowed, remaining = await self._check_rate_limit(user_id, channel.value)
        if not allowed:
            logger.warning(f"Rate limit exceeded for user {user_id} on {channel.value}")
            return OTPResult(
                success=False,
                message="Too many OTP requests. Please wait before requesting again.",
                message_ar="طلبات OTP كثيرة جداً. يرجى الانتظار قبل طلب رمز جديد.",
                error_code="RATE_LIMIT_EXCEEDED",
            )

        # Check for existing valid OTP
        otp_key = self._get_otp_key(user_id, purpose.value)
        existing_otp = await self._get_otp(otp_key)

        if existing_otp and not existing_otp.is_expired():
            time_remaining = existing_otp.time_remaining()
            if time_remaining > 60:  # Allow resend if less than 60 seconds remaining
                return OTPResult(
                    success=False,
                    message=f"OTP already sent. Please wait {time_remaining} seconds.",
                    message_ar=f"تم إرسال OTP بالفعل. يرجى الانتظار {time_remaining} ثانية.",
                    time_remaining=time_remaining,
                    error_code="OTP_ALREADY_SENT",
                )

        # Generate new OTP
        otp_code = self._generate_otp_code()
        otp_hash = self._hash_otp(otp_code, user_id)

        # Create OTP record
        now = time.time()
        otp_record = OTPRecord(
            user_id=user_id,
            otp_hash=otp_hash,
            purpose=purpose.value,
            channel=channel.value,
            destination=self._mask_destination(phone_or_email, channel.value),
            created_at=now,
            expires_at=now + OTP_EXPIRY_SECONDS,
        )

        # Send OTP via appropriate channel
        delivery_id = None
        try:
            if channel == OTPChannel.SMS:
                delivery_id = await self._send_otp_via_sms(
                    phone_or_email, otp_code, purpose.value, language
                )
            elif channel == OTPChannel.WHATSAPP:
                delivery_id = await self._send_otp_via_whatsapp(
                    phone_or_email, otp_code, purpose.value, language
                )
            elif channel == OTPChannel.TELEGRAM:
                delivery_id = await self._send_otp_via_telegram(
                    phone_or_email, otp_code, purpose.value, language
                )
            elif channel == OTPChannel.EMAIL:
                delivery_id = await self._send_otp_via_email(
                    phone_or_email, otp_code, purpose.value, language
                )
        except Exception as e:
            logger.error(f"Failed to send OTP via {channel.value}: {e}")
            return OTPResult(
                success=False,
                message=f"Failed to send OTP via {channel.value}",
                message_ar=f"فشل إرسال OTP عبر {channel.value}",
                error_code="DELIVERY_FAILED",
            )

        if delivery_id is None:
            logger.error(f"OTP delivery failed for user {user_id} via {channel.value}")
            return OTPResult(
                success=False,
                message=f"Failed to deliver OTP via {channel.value}",
                message_ar=f"فشل توصيل OTP عبر {channel.value}",
                error_code="DELIVERY_FAILED",
            )

        # Store OTP
        stored = await self._store_otp(otp_key, otp_record)
        if not stored:
            logger.error(f"Failed to store OTP for user {user_id}")
            return OTPResult(
                success=False,
                message="Failed to process OTP request",
                message_ar="فشل معالجة طلب OTP",
                error_code="STORAGE_FAILED",
            )

        # Record rate limit
        await self._record_rate_limit(user_id, channel.value)

        logger.info(
            f"OTP generated and sent to user {user_id} via {channel.value} for {purpose.value}"
        )

        return OTPResult(
            success=True,
            message="OTP sent successfully",
            message_ar="تم إرسال رمز التحقق بنجاح",
            otp_sent=True,
            time_remaining=OTP_EXPIRY_SECONDS,
            attempts_remaining=otp_record.max_attempts,
            delivery_id=str(delivery_id) if delivery_id else None,
        )

    async def verify_otp(
        self,
        user_id: str,
        otp_code: str,
        purpose: OTPPurpose | str,
    ) -> OTPResult:
        """
        التحقق من صحة رمز OTP

        Args:
            user_id: معرف المستخدم
            otp_code: رمز OTP المدخل
            purpose: الغرض من OTP

        Returns:
            OTPResult مع حالة التحقق
        """
        if not self._check_initialized():
            return OTPResult(
                success=False,
                message="OTP service not initialized",
                message_ar="خدمة OTP غير مهيأة",
                error_code="SERVICE_NOT_INITIALIZED",
            )

        # Convert string to enum if needed
        if isinstance(purpose, str):
            purpose = OTPPurpose(purpose)

        otp_key = self._get_otp_key(user_id, purpose.value)
        otp_record = await self._get_otp(otp_key)

        # Check if OTP exists
        if otp_record is None:
            logger.warning(f"No OTP found for user {user_id} with purpose {purpose.value}")
            return OTPResult(
                success=False,
                message="No OTP found. Please request a new one.",
                message_ar="لم يتم العثور على رمز OTP. يرجى طلب رمز جديد.",
                error_code="OTP_NOT_FOUND",
            )

        # Check if OTP is expired
        if otp_record.is_expired():
            await self._delete_otp(otp_key)
            logger.warning(f"Expired OTP verification attempt for user {user_id}")
            return OTPResult(
                success=False,
                message="OTP has expired. Please request a new one.",
                message_ar="انتهت صلاحية رمز OTP. يرجى طلب رمز جديد.",
                error_code="OTP_EXPIRED",
            )

        # Check if already verified
        if otp_record.verified:
            await self._delete_otp(otp_key)
            return OTPResult(
                success=False,
                message="OTP has already been used. Please request a new one.",
                message_ar="تم استخدام رمز OTP بالفعل. يرجى طلب رمز جديد.",
                error_code="OTP_ALREADY_USED",
            )

        # Check attempts
        if not otp_record.has_attempts_remaining():
            await self._delete_otp(otp_key)
            logger.warning(f"Max OTP attempts exceeded for user {user_id}")
            return OTPResult(
                success=False,
                message="Too many failed attempts. Please request a new OTP.",
                message_ar="محاولات فاشلة كثيرة. يرجى طلب رمز OTP جديد.",
                error_code="MAX_ATTEMPTS_EXCEEDED",
            )

        # Verify OTP
        if not self._verify_otp_hash(otp_code, user_id, otp_record.otp_hash):
            # Increment attempts
            otp_record.attempts += 1
            await self._update_otp(otp_key, otp_record)

            attempts_remaining = otp_record.max_attempts - otp_record.attempts
            logger.warning(
                f"Invalid OTP attempt for user {user_id}. Attempts remaining: {attempts_remaining}"
            )

            return OTPResult(
                success=False,
                message=f"Invalid OTP. {attempts_remaining} attempts remaining.",
                message_ar=f"رمز OTP غير صحيح. {attempts_remaining} محاولات متبقية.",
                attempts_remaining=attempts_remaining,
                error_code="INVALID_OTP",
            )

        # Mark as verified and delete
        otp_record.verified = True
        await self._delete_otp(otp_key)

        logger.info(f"OTP verified successfully for user {user_id} with purpose {purpose.value}")

        return OTPResult(
            success=True,
            message="OTP verified successfully",
            message_ar="تم التحقق من رمز OTP بنجاح",
        )

    async def get_otp_status(
        self,
        user_id: str,
        purpose: OTPPurpose | str,
    ) -> OTPResult:
        """
        التحقق من حالة OTP

        Args:
            user_id: معرف المستخدم
            purpose: الغرض من OTP

        Returns:
            OTPResult مع حالة OTP
        """
        if not self._check_initialized():
            return OTPResult(
                success=False,
                message="OTP service not initialized",
                message_ar="خدمة OTP غير مهيأة",
                error_code="SERVICE_NOT_INITIALIZED",
            )

        # Convert string to enum if needed
        if isinstance(purpose, str):
            purpose = OTPPurpose(purpose)

        otp_key = self._get_otp_key(user_id, purpose.value)
        otp_record = await self._get_otp(otp_key)

        if otp_record is None:
            return OTPResult(
                success=True,
                message="No active OTP found",
                message_ar="لم يتم العثور على رمز OTP نشط",
                otp_sent=False,
            )

        if otp_record.is_expired():
            await self._delete_otp(otp_key)
            return OTPResult(
                success=True,
                message="OTP has expired",
                message_ar="انتهت صلاحية رمز OTP",
                otp_sent=False,
            )

        time_remaining = otp_record.time_remaining()
        attempts_remaining = otp_record.max_attempts - otp_record.attempts

        return OTPResult(
            success=True,
            message="Active OTP found",
            message_ar="تم العثور على رمز OTP نشط",
            otp_sent=True,
            time_remaining=time_remaining,
            attempts_remaining=attempts_remaining,
        )

    async def invalidate_otp(
        self,
        user_id: str,
        purpose: OTPPurpose | str,
    ) -> OTPResult:
        """
        إلغاء صلاحية OTP

        Args:
            user_id: معرف المستخدم
            purpose: الغرض من OTP

        Returns:
            OTPResult مع حالة الإلغاء
        """
        if not self._check_initialized():
            return OTPResult(
                success=False,
                message="OTP service not initialized",
                message_ar="خدمة OTP غير مهيأة",
                error_code="SERVICE_NOT_INITIALIZED",
            )

        # Convert string to enum if needed
        if isinstance(purpose, str):
            purpose = OTPPurpose(purpose)

        otp_key = self._get_otp_key(user_id, purpose.value)
        deleted = await self._delete_otp(otp_key)

        if deleted:
            logger.info(f"OTP invalidated for user {user_id} with purpose {purpose.value}")
            return OTPResult(
                success=True,
                message="OTP invalidated successfully",
                message_ar="تم إلغاء صلاحية رمز OTP بنجاح",
            )
        else:
            return OTPResult(
                success=True,
                message="No active OTP to invalidate",
                message_ar="لا يوجد رمز OTP نشط للإلغاء",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Global Instance
# ═══════════════════════════════════════════════════════════════════════════════

_otp_service: OTPService | None = None


def get_otp_service() -> OTPService:
    """
    الحصول على instance عام من OTPService

    Returns:
        OTPService instance
    """
    global _otp_service

    if _otp_service is None:
        _otp_service = OTPService()

    return _otp_service


async def initialize_otp_service(use_redis: bool = True) -> OTPService:
    """
    تهيئة خدمة OTP والحصول عليها

    Args:
        use_redis: استخدام Redis للتخزين

    Returns:
        OTPService instance (initialized)
    """
    service = get_otp_service()
    await service.initialize(use_redis=use_redis)
    return service
