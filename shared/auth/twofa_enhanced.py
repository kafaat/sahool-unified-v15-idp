"""
Enhanced Two-Factor Authentication (2FA) for SAHOOL Platform
المصادقة الثنائية المحسنة لمنصة سهول

This module extends the base 2FA service with:
- Rate limiting on 2FA attempts
- Used backup code tracking
- TOTP replay protection
- Multiple 2FA method support (TOTP, SMS, Email)
- Recovery flow with enhanced security
- Audit logging integration

Security Features:
- Brute force protection on 2FA attempts
- One-time use enforcement for backup codes
- Time-based code replay detection
- Device trust management
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import config
from .twofa_service import TOTP_INTERVAL, TwoFactorAuthService

logger = logging.getLogger(__name__)


class TwoFAMethod(StrEnum):
    """Supported 2FA methods"""

    TOTP = "totp"  # Time-based OTP (Google Authenticator, etc.)
    SMS = "sms"  # SMS-based OTP
    EMAIL = "email"  # Email-based OTP
    BACKUP = "backup"  # Backup recovery codes


class TwoFAStatus(StrEnum):
    """2FA setup status"""

    NOT_CONFIGURED = "not_configured"
    PENDING_VERIFICATION = "pending_verification"
    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass
class TwoFAConfig:
    """
    User 2FA configuration.
    تكوين المصادقة الثنائية للمستخدم.
    """

    user_id: str
    status: TwoFAStatus = TwoFAStatus.NOT_CONFIGURED
    primary_method: TwoFAMethod = TwoFAMethod.TOTP

    # TOTP configuration
    totp_secret: str = ""
    totp_enabled_at: float | None = None

    # Backup codes
    backup_codes_hash: list[str] = field(default_factory=list)
    backup_codes_used: list[str] = field(default_factory=list)
    backup_codes_generated_at: float | None = None

    # SMS/Email configuration
    phone_number: str = ""
    email_verified: bool = False

    # Trusted devices
    trusted_device_ids: list[str] = field(default_factory=list)

    # Metadata
    created_at: float = 0
    updated_at: float = 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "status": self.status.value,
            "primary_method": self.primary_method.value,
            "totp_secret": self.totp_secret,
            "totp_enabled_at": self.totp_enabled_at,
            "backup_codes_hash": self.backup_codes_hash,
            "backup_codes_used": self.backup_codes_used,
            "backup_codes_generated_at": self.backup_codes_generated_at,
            "phone_number": self.phone_number,
            "email_verified": self.email_verified,
            "trusted_device_ids": self.trusted_device_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TwoFAConfig:
        """Create from dictionary"""
        return cls(
            user_id=data["user_id"],
            status=TwoFAStatus(data.get("status", "not_configured")),
            primary_method=TwoFAMethod(data.get("primary_method", "totp")),
            totp_secret=data.get("totp_secret", ""),
            totp_enabled_at=data.get("totp_enabled_at"),
            backup_codes_hash=data.get("backup_codes_hash", []),
            backup_codes_used=data.get("backup_codes_used", []),
            backup_codes_generated_at=data.get("backup_codes_generated_at"),
            phone_number=data.get("phone_number", ""),
            email_verified=data.get("email_verified", False),
            trusted_device_ids=data.get("trusted_device_ids", []),
            created_at=data.get("created_at", 0),
            updated_at=data.get("updated_at", 0),
        )

    def remaining_backup_codes(self) -> int:
        """Count remaining unused backup codes"""
        return len(self.backup_codes_hash) - len(self.backup_codes_used)


@dataclass
class TwoFAAttempt:
    """2FA verification attempt record"""

    user_id: str
    method: TwoFAMethod
    timestamp: float
    success: bool
    ip_address: str = ""
    user_agent: str = ""


class EnhancedTwoFactorAuth:
    """
    Enhanced Two-Factor Authentication Manager.
    مدير المصادقة الثنائية المحسن.

    Features:
    - Rate limiting (max 5 attempts per 15 minutes)
    - TOTP replay protection (each code can only be used once)
    - One-time backup code enforcement
    - Trusted device management
    - SMS/Email OTP support (extensible)
    - Comprehensive audit logging

    Example:
        >>> twofa = EnhancedTwoFactorAuth()
        >>> await twofa.initialize()
        >>>
        >>> # Setup 2FA for user
        >>> setup = await twofa.setup_totp(user_id="user123")
        >>> print(setup["qr_code"])  # Display to user
        >>>
        >>> # Verify initial setup
        >>> result = await twofa.verify_totp_setup(
        ...     user_id="user123",
        ...     code="123456"
        ... )
        >>>
        >>> # Verify on login
        >>> result = await twofa.verify_code(
        ...     user_id="user123",
        ...     code="123456",
        ...     method=TwoFAMethod.TOTP,
        ...     ip_address="192.168.1.1"
        ... )
    """

    # Redis key prefixes
    CONFIG_PREFIX = "2fa:config:"
    ATTEMPT_PREFIX = "2fa:attempts:"
    USED_CODES_PREFIX = "2fa:used:"
    OTP_PREFIX = "2fa:otp:"  # For SMS/Email OTPs

    # Configuration
    MAX_ATTEMPTS = 5
    ATTEMPT_WINDOW = 900  # 15 minutes
    LOCKOUT_DURATION = 1800  # 30 minutes after max attempts
    CODE_REUSE_WINDOW = 90  # Seconds to prevent TOTP reuse (3 intervals)
    OTP_VALIDITY = 300  # 5 minutes for SMS/Email OTP
    BACKUP_CODE_COUNT = 10

    def __init__(self, redis_url: str | None = None):
        """
        Initialize enhanced 2FA manager.

        Args:
            redis_url: Redis connection URL
        """
        self._redis: aioredis.Redis | None = None
        self._redis_url = redis_url or getattr(config, "REDIS_URL", None) or self._build_redis_url()
        self._initialized = False

        # Base TOTP service
        self._totp_service = TwoFactorAuthService()

        # In-memory fallback
        self._memory_configs: dict[str, TwoFAConfig] = {}
        self._memory_attempts: dict[str, list[TwoFAAttempt]] = {}
        self._memory_used_codes: dict[str, set[str]] = {}

    def _build_redis_url(self) -> str:
        """Build Redis URL from configuration"""
        if hasattr(config, "REDIS_PASSWORD") and config.REDIS_PASSWORD:
            return (
                f"redis://:{config.REDIS_PASSWORD}@"
                f"{getattr(config, 'REDIS_HOST', 'localhost')}:"
                f"{getattr(config, 'REDIS_PORT', 6379)}/"
                f"{getattr(config, 'REDIS_DB', 0)}"
            )
        return (
            f"redis://{getattr(config, 'REDIS_HOST', 'localhost')}:"
            f"{getattr(config, 'REDIS_PORT', 6379)}/"
            f"{getattr(config, 'REDIS_DB', 0)}"
        )

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        if self._initialized:
            return

        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory 2FA storage")
            self._initialized = True
            return

        try:
            self._redis = await aioredis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            await self._redis.ping()
            self._initialized = True
            logger.info("Enhanced 2FA manager initialized with Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory storage: {e}")
            self._redis = None
            self._initialized = True

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
        self._initialized = False

    # ─────────────────────────────────────────────────────────────────────────
    # TOTP Setup
    # ─────────────────────────────────────────────────────────────────────────

    async def setup_totp(
        self,
        user_id: str,
        email: str,
    ) -> dict:
        """
        Initialize TOTP setup for user.
        بدء إعداد TOTP للمستخدم.

        Args:
            user_id: User ID
            email: User email for authenticator app display

        Returns:
            Dict with secret, QR code, and backup codes
        """
        if not self._initialized:
            await self.initialize()

        # Generate new secret
        secret = self._totp_service.generate_secret()

        # Generate QR code
        qr_code = self._totp_service.generate_qr_code(secret, email)

        # Generate backup codes
        backup_codes = self._totp_service.generate_backup_codes(self.BACKUP_CODE_COUNT)
        backup_codes_hash = [self._hash_backup_code(code) for code in backup_codes]

        # Create pending config
        now = time.time()
        twofa_config = TwoFAConfig(
            user_id=user_id,
            status=TwoFAStatus.PENDING_VERIFICATION,
            primary_method=TwoFAMethod.TOTP,
            totp_secret=secret,
            backup_codes_hash=backup_codes_hash,
            backup_codes_generated_at=now,
            created_at=now,
            updated_at=now,
        )

        await self._save_config(twofa_config)

        logger.info(f"TOTP setup initiated for user {user_id}")

        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,  # Show once, never store in plain
            "status": "pending_verification",
        }

    async def verify_totp_setup(
        self,
        user_id: str,
        code: str,
    ) -> tuple[bool, str]:
        """
        Verify TOTP setup by validating first code.
        التحقق من إعداد TOTP بالتحقق من الرمز الأول.

        Args:
            user_id: User ID
            code: TOTP code from authenticator

        Returns:
            Tuple of (success, message)
        """
        if not self._initialized:
            await self.initialize()

        twofa_config = await self._get_config(user_id)

        if not twofa_config:
            return False, "2FA not configured"

        if twofa_config.status != TwoFAStatus.PENDING_VERIFICATION:
            return False, "Invalid 2FA state"

        # Verify code
        is_valid = self._totp_service.verify_totp(twofa_config.totp_secret, code)

        if is_valid:
            # Enable 2FA
            twofa_config.status = TwoFAStatus.ENABLED
            twofa_config.totp_enabled_at = time.time()
            twofa_config.updated_at = time.time()
            await self._save_config(twofa_config)

            logger.info(f"TOTP enabled for user {user_id}")
            return True, "2FA enabled successfully"
        else:
            return False, "Invalid verification code"

    # ─────────────────────────────────────────────────────────────────────────
    # Code Verification
    # ─────────────────────────────────────────────────────────────────────────

    async def verify_code(
        self,
        user_id: str,
        code: str,
        method: TwoFAMethod = TwoFAMethod.TOTP,
        ip_address: str = "",
        user_agent: str = "",
    ) -> tuple[bool, str]:
        """
        Verify 2FA code with rate limiting and replay protection.
        التحقق من رمز 2FA مع تحديد المعدل والحماية من إعادة الاستخدام.

        Args:
            user_id: User ID
            code: Verification code
            method: 2FA method
            ip_address: Client IP
            user_agent: Client user agent

        Returns:
            Tuple of (success, message)
        """
        if not self._initialized:
            await self.initialize()

        # Check rate limit
        is_blocked, remaining_lockout = await self._check_rate_limit(user_id)
        if is_blocked:
            logger.warning(f"2FA rate limit exceeded for user {user_id}")
            return False, f"Too many attempts. Try again in {remaining_lockout} seconds"

        twofa_config = await self._get_config(user_id)

        if not twofa_config or twofa_config.status != TwoFAStatus.ENABLED:
            await self._record_attempt(user_id, method, False, ip_address, user_agent)
            return False, "2FA not enabled"

        # Verify based on method
        if method == TwoFAMethod.TOTP:
            success, message = await self._verify_totp(user_id, code, twofa_config)
        elif method == TwoFAMethod.BACKUP:
            success, message = await self._verify_backup_code(user_id, code, twofa_config)
        elif method in (TwoFAMethod.SMS, TwoFAMethod.EMAIL):
            success, message = await self._verify_otp(user_id, code, method)
        else:
            success, message = False, "Unsupported 2FA method"

        # Record attempt
        await self._record_attempt(user_id, method, success, ip_address, user_agent)

        if success:
            logger.info(f"2FA verification successful for user {user_id} via {method.value}")
        else:
            logger.warning(f"2FA verification failed for user {user_id} via {method.value}")

        return success, message

    async def _verify_totp(
        self,
        user_id: str,
        code: str,
        twofa_config: TwoFAConfig,
    ) -> tuple[bool, str]:
        """Verify TOTP code with replay protection"""
        # Check for code reuse
        if await self._is_code_used(user_id, code):
            return False, "Code already used"

        # Verify code
        is_valid = self._totp_service.verify_totp(twofa_config.totp_secret, code)

        if is_valid:
            # Mark code as used to prevent replay
            await self._mark_code_used(user_id, code)
            return True, "Verification successful"

        return False, "Invalid code"

    def _verify_single_backup_hash(self, code: str, stored_hash: str) -> bool:
        """Verify a backup code against a single stored hash.

        Supports bcrypt, salted SHA-256, and legacy unsalted SHA-256 formats.
        """
        import hmac as _hmac

        clean_code = code.replace("-", "").strip().upper()

        if stored_hash.startswith("$2"):
            # bcrypt hash
            try:
                import bcrypt

                return bcrypt.checkpw(clean_code.encode(), stored_hash.encode())
            except ImportError:
                return False
        elif stored_hash.startswith("sha256:"):
            # Salted SHA-256 fallback
            parts = stored_hash.split(":", 2)
            if len(parts) == 3:
                salt = parts[1]
                expected = parts[2]
                computed = hashlib.sha256((salt + clean_code).encode()).hexdigest()
                return _hmac.compare_digest(computed, expected)
            return False
        else:
            # Legacy unsalted SHA-256 (backward compat)
            computed = hashlib.sha256(clean_code.encode()).hexdigest()
            return _hmac.compare_digest(computed, stored_hash)

    async def _verify_backup_code(
        self,
        user_id: str,
        code: str,
        twofa_config: TwoFAConfig,
    ) -> tuple[bool, str]:
        """Verify backup code (one-time use)"""
        # Find matching hash by verifying against each stored hash
        matched_hash = None
        for stored_hash in twofa_config.backup_codes_hash:
            if stored_hash in twofa_config.backup_codes_used:
                continue
            if self._verify_single_backup_hash(code, stored_hash):
                matched_hash = stored_hash
                break

        if matched_hash is None:
            return False, "Invalid backup code"

        # Mark as used
        twofa_config.backup_codes_used.append(matched_hash)
        twofa_config.updated_at = time.time()
        await self._save_config(twofa_config)

        remaining = twofa_config.remaining_backup_codes()
        logger.info(f"Backup code used for user {user_id}. {remaining} codes remaining")

        if remaining <= 2:
            logger.warning(f"User {user_id} has only {remaining} backup codes remaining!")

        return True, f"Verification successful. {remaining} backup codes remaining"

    async def _verify_otp(
        self,
        user_id: str,
        code: str,
        method: TwoFAMethod,
    ) -> tuple[bool, str]:
        """Verify SMS/Email OTP"""
        key = f"{self.OTP_PREFIX}{user_id}:{method.value}"

        if self._redis:
            stored_code = await self._redis.get(key)
            if stored_code and stored_code == code:
                await self._redis.delete(key)  # One-time use
                return True, "Verification successful"
        else:
            # In-memory not supported for SMS/Email OTP
            return False, "OTP verification not available"

        return False, "Invalid or expired code"

    # ─────────────────────────────────────────────────────────────────────────
    # SMS/Email OTP
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_otp(
        self,
        user_id: str,
        method: TwoFAMethod,
    ) -> str:
        """
        Generate and store OTP for SMS/Email delivery.
        إنشاء وتخزين OTP للتسليم عبر SMS/البريد الإلكتروني.

        Args:
            user_id: User ID
            method: TwoFAMethod.SMS or TwoFAMethod.EMAIL

        Returns:
            Generated OTP code (6 digits)
        """
        if not self._initialized:
            await self.initialize()

        if method not in (TwoFAMethod.SMS, TwoFAMethod.EMAIL):
            raise ValueError("Method must be SMS or EMAIL")

        # Generate 6-digit OTP
        otp = "".join(secrets.choice("0123456789") for _ in range(6))

        # Store with expiry
        if self._redis:
            key = f"{self.OTP_PREFIX}{user_id}:{method.value}"
            await self._redis.setex(key, self.OTP_VALIDITY, otp)

        logger.info(f"OTP generated for user {user_id} via {method.value}")
        return otp

    # ─────────────────────────────────────────────────────────────────────────
    # Trusted Devices
    # ─────────────────────────────────────────────────────────────────────────

    async def add_trusted_device(
        self,
        user_id: str,
        device_fingerprint: str,
    ) -> bool:
        """
        Add a trusted device for user.
        إضافة جهاز موثوق للمستخدم.

        Args:
            user_id: User ID
            device_fingerprint: Device fingerprint hash

        Returns:
            True if added successfully
        """
        if not self._initialized:
            await self.initialize()

        twofa_config = await self._get_config(user_id)
        if not twofa_config:
            return False

        if device_fingerprint not in twofa_config.trusted_device_ids:
            twofa_config.trusted_device_ids.append(device_fingerprint)
            # Keep only last 5 trusted devices
            if len(twofa_config.trusted_device_ids) > 5:
                twofa_config.trusted_device_ids = twofa_config.trusted_device_ids[-5:]
            twofa_config.updated_at = time.time()
            await self._save_config(twofa_config)

        logger.info(f"Trusted device added for user {user_id}")
        return True

    async def is_trusted_device(
        self,
        user_id: str,
        device_fingerprint: str,
    ) -> bool:
        """
        Check if device is trusted.
        التحقق مما إذا كان الجهاز موثوقا.

        Args:
            user_id: User ID
            device_fingerprint: Device fingerprint hash

        Returns:
            True if device is trusted
        """
        if not self._initialized:
            await self.initialize()

        twofa_config = await self._get_config(user_id)
        if not twofa_config:
            return False

        return device_fingerprint in twofa_config.trusted_device_ids

    async def remove_trusted_device(
        self,
        user_id: str,
        device_fingerprint: str,
    ) -> bool:
        """Remove a trusted device"""
        if not self._initialized:
            await self.initialize()

        twofa_config = await self._get_config(user_id)
        if not twofa_config:
            return False

        if device_fingerprint in twofa_config.trusted_device_ids:
            twofa_config.trusted_device_ids.remove(device_fingerprint)
            twofa_config.updated_at = time.time()
            await self._save_config(twofa_config)
            return True

        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Management
    # ─────────────────────────────────────────────────────────────────────────

    async def disable_2fa(
        self,
        user_id: str,
        verification_code: str,
    ) -> tuple[bool, str]:
        """
        Disable 2FA for user (requires verification).
        تعطيل المصادقة الثنائية للمستخدم (يتطلب التحقق).

        Args:
            user_id: User ID
            verification_code: TOTP or backup code for confirmation

        Returns:
            Tuple of (success, message)
        """
        if not self._initialized:
            await self.initialize()

        twofa_config = await self._get_config(user_id)
        if not twofa_config or twofa_config.status != TwoFAStatus.ENABLED:
            return False, "2FA not enabled"

        # Verify code before disabling
        success, _ = await self._verify_totp(user_id, verification_code, twofa_config)
        if not success:
            # Try backup code
            success, _ = await self._verify_backup_code(user_id, verification_code, twofa_config)

        if success:
            twofa_config.status = TwoFAStatus.DISABLED
            twofa_config.totp_secret = ""
            twofa_config.backup_codes_hash = []
            twofa_config.backup_codes_used = []
            twofa_config.trusted_device_ids = []
            twofa_config.updated_at = time.time()
            await self._save_config(twofa_config)

            logger.info(f"2FA disabled for user {user_id}")
            return True, "2FA disabled successfully"

        return False, "Invalid verification code"

    async def regenerate_backup_codes(
        self,
        user_id: str,
        verification_code: str,
    ) -> tuple[list[str] | None, str]:
        """
        Regenerate backup codes (requires verification).
        إعادة إنشاء رموز النسخ الاحتياطي (يتطلب التحقق).

        Args:
            user_id: User ID
            verification_code: TOTP code for confirmation

        Returns:
            Tuple of (new_codes or None, message)
        """
        if not self._initialized:
            await self.initialize()

        twofa_config = await self._get_config(user_id)
        if not twofa_config or twofa_config.status != TwoFAStatus.ENABLED:
            return None, "2FA not enabled"

        # Verify TOTP
        success, _ = await self._verify_totp(user_id, verification_code, twofa_config)
        if not success:
            return None, "Invalid verification code"

        # Generate new backup codes
        backup_codes = self._totp_service.generate_backup_codes(self.BACKUP_CODE_COUNT)
        backup_codes_hash = [self._hash_backup_code(code) for code in backup_codes]

        twofa_config.backup_codes_hash = backup_codes_hash
        twofa_config.backup_codes_used = []
        twofa_config.backup_codes_generated_at = time.time()
        twofa_config.updated_at = time.time()
        await self._save_config(twofa_config)

        logger.info(f"Backup codes regenerated for user {user_id}")
        return backup_codes, "Backup codes regenerated successfully"

    async def get_2fa_status(self, user_id: str) -> dict:
        """
        Get 2FA status for user.
        الحصول على حالة المصادقة الثنائية للمستخدم.

        Args:
            user_id: User ID

        Returns:
            Status dictionary
        """
        if not self._initialized:
            await self.initialize()

        twofa_config = await self._get_config(user_id)

        if not twofa_config:
            return {
                "enabled": False,
                "status": TwoFAStatus.NOT_CONFIGURED.value,
            }

        return {
            "enabled": twofa_config.status == TwoFAStatus.ENABLED,
            "status": twofa_config.status.value,
            "primary_method": twofa_config.primary_method.value,
            "backup_codes_remaining": twofa_config.remaining_backup_codes(),
            "trusted_devices_count": len(twofa_config.trusted_device_ids),
            "enabled_at": twofa_config.totp_enabled_at,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Rate Limiting
    # ─────────────────────────────────────────────────────────────────────────

    async def _check_rate_limit(self, user_id: str) -> tuple[bool, int]:
        """
        Check if user is rate limited.
        التحقق مما إذا كان المستخدم محدود المعدل.

        Returns:
            Tuple of (is_blocked, remaining_lockout_seconds)
        """
        key = f"{self.ATTEMPT_PREFIX}{user_id}"
        now = time.time()
        window_start = now - self.ATTEMPT_WINDOW

        if self._redis:
            # Clean old attempts
            await self._redis.zremrangebyscore(key, 0, window_start)

            # Count recent failed attempts
            attempts = await self._redis.zcard(key)

            if attempts >= self.MAX_ATTEMPTS:
                # Get oldest attempt in window to calculate lockout
                oldest = await self._redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    lockout_end = oldest[0][1] + self.LOCKOUT_DURATION
                    remaining = int(lockout_end - now)
                    if remaining > 0:
                        return True, remaining

            return False, 0
        else:
            attempts = self._memory_attempts.get(user_id, [])
            recent_failed = [a for a in attempts if a.timestamp > window_start and not a.success]

            if len(recent_failed) >= self.MAX_ATTEMPTS:
                oldest = min(a.timestamp for a in recent_failed)
                lockout_end = oldest + self.LOCKOUT_DURATION
                remaining = int(lockout_end - now)
                if remaining > 0:
                    return True, remaining

            return False, 0

    async def _record_attempt(
        self,
        user_id: str,
        method: TwoFAMethod,
        success: bool,
        ip_address: str,
        user_agent: str,
    ) -> None:
        """Record 2FA attempt"""
        now = time.time()

        if self._redis:
            key = f"{self.ATTEMPT_PREFIX}{user_id}"
            if not success:
                # Only track failed attempts for rate limiting
                await self._redis.zadd(key, {str(now): now})
                await self._redis.expire(key, self.LOCKOUT_DURATION)
        else:
            if user_id not in self._memory_attempts:
                self._memory_attempts[user_id] = []
            self._memory_attempts[user_id].append(
                TwoFAAttempt(
                    user_id=user_id,
                    method=method,
                    timestamp=now,
                    success=success,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Code Reuse Protection
    # ─────────────────────────────────────────────────────────────────────────

    async def _is_code_used(self, user_id: str, code: str) -> bool:
        """Check if TOTP code was already used (replay protection)"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        key = f"{self.USED_CODES_PREFIX}{user_id}"

        if self._redis:
            return await self._redis.sismember(key, code_hash)
        else:
            return code_hash in self._memory_used_codes.get(user_id, set())

    async def _mark_code_used(self, user_id: str, code: str) -> None:
        """Mark TOTP code as used"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        key = f"{self.USED_CODES_PREFIX}{user_id}"

        if self._redis:
            await self._redis.sadd(key, code_hash)
            await self._redis.expire(key, self.CODE_REUSE_WINDOW)
        else:
            if user_id not in self._memory_used_codes:
                self._memory_used_codes[user_id] = set()
            self._memory_used_codes[user_id].add(code_hash)

    # ─────────────────────────────────────────────────────────────────────────
    # Storage
    # ─────────────────────────────────────────────────────────────────────────

    async def _save_config(self, twofa_config: TwoFAConfig) -> None:
        """Save 2FA config"""
        key = f"{self.CONFIG_PREFIX}{twofa_config.user_id}"

        if self._redis:
            await self._redis.set(key, json.dumps(twofa_config.to_dict()))
        else:
            self._memory_configs[twofa_config.user_id] = twofa_config

    async def _get_config(self, user_id: str) -> TwoFAConfig | None:
        """Get 2FA config"""
        if self._redis:
            key = f"{self.CONFIG_PREFIX}{user_id}"
            data = await self._redis.get(key)
            if data:
                return TwoFAConfig.from_dict(json.loads(data))
            return None
        else:
            return self._memory_configs.get(user_id)

    def _hash_backup_code(self, code: str) -> str:
        """Hash backup code for secure storage.

        Uses bcrypt (preferred) with salted SHA-256 fallback.
        SECURITY: Never use unsalted hashes for backup codes.
        """
        clean_code = code.replace("-", "").strip().upper()
        try:
            import bcrypt

            return bcrypt.hashpw(clean_code.encode(), bcrypt.gensalt(rounds=12)).decode()
        except ImportError:
            # Fallback to SHA-256 with salt if bcrypt not available
            salt = secrets.token_hex(16)
            return f"sha256:{salt}:{hashlib.sha256((salt + clean_code).encode()).hexdigest()}"


# ─────────────────────────────────────────────────────────────────────────────
# Global Instance
# ─────────────────────────────────────────────────────────────────────────────

_enhanced_2fa: EnhancedTwoFactorAuth | None = None


async def get_enhanced_2fa() -> EnhancedTwoFactorAuth:
    """
    Get global enhanced 2FA manager.
    الحصول على مدير المصادقة الثنائية المحسن العام.

    Returns:
        EnhancedTwoFactorAuth instance
    """
    global _enhanced_2fa

    if _enhanced_2fa is None:
        _enhanced_2fa = EnhancedTwoFactorAuth()
        await _enhanced_2fa.initialize()

    return _enhanced_2fa
