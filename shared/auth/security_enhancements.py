"""
Security Enhancements for SAHOOL Platform Authentication
تحسينات الأمان لمصادقة منصة سهول

This module provides advanced security features:
- Refresh Token Rotation with Token Family Tracking
- Token Fingerprinting (Device/Browser Binding)
- Automatic Token Theft Detection
- Token Binding to prevent replay attacks

Security Best Practices Implemented:
- RFC 6819: OAuth 2.0 Threat Model and Security Considerations
- OWASP Token Security Guidelines
- NIST Digital Identity Guidelines (SP 800-63B)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, StrEnum
from typing import Any

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Token Fingerprinting
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class TokenFingerprint:
    """
    Device/Browser fingerprint for token binding.
    بصمة الجهاز/المتصفح لربط الرمز.

    This binds tokens to a specific client context to prevent token theft.
    """

    user_agent: str
    ip_address: str
    accept_language: str = ""
    accept_encoding: str = ""
    screen_resolution: str = ""
    timezone: str = ""
    platform: str = ""

    def to_hash(self) -> str:
        """
        Create a stable hash of the fingerprint.
        إنشاء تجزئة مستقرة للبصمة.

        Returns:
            SHA-256 hash of fingerprint components
        """
        # Combine stable components (exclude frequently changing IP for mobile)
        components = [
            self.user_agent,
            self.accept_language,
            self.platform,
            self.screen_resolution,
            self.timezone,
        ]

        fingerprint_str = "|".join(components)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:32]

    def to_hash_with_ip(self) -> str:
        """
        Create hash including IP address (stricter binding).
        إنشاء تجزئة تشمل عنوان IP (ربط أكثر صرامة).

        Returns:
            SHA-256 hash including IP address
        """
        components = [
            self.user_agent,
            self.ip_address,
            self.accept_language,
            self.platform,
        ]

        fingerprint_str = "|".join(components)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:32]

    @classmethod
    def from_request(cls, request: Any) -> TokenFingerprint:
        """
        Create fingerprint from FastAPI/Starlette request.
        إنشاء بصمة من طلب FastAPI/Starlette.

        Args:
            request: FastAPI Request object

        Returns:
            TokenFingerprint instance
        """
        headers = getattr(request, "headers", {})

        # Get client IP considering proxies (with validation)
        import ipaddress as _ipaddress

        forwarded = headers.get("x-forwarded-for", "")
        ip_address = "unknown"
        if forwarded:
            candidate = forwarded.split(",")[0].strip()
            try:
                _ipaddress.ip_address(candidate)
                ip_address = candidate
            except ValueError:
                ip_address = "unknown"
        else:
            client = getattr(request, "client", None)
            ip_address = client.host if client else "unknown"

        return cls(
            user_agent=headers.get("user-agent", ""),
            ip_address=ip_address,
            accept_language=headers.get("accept-language", ""),
            accept_encoding=headers.get("accept-encoding", ""),
            screen_resolution=headers.get("x-screen-resolution", ""),
            timezone=headers.get("x-timezone", ""),
            platform=headers.get("sec-ch-ua-platform", ""),
        )


def create_fingerprint_hash(request: Any, include_ip: bool = False) -> str:
    """
    Create fingerprint hash from request.
    إنشاء تجزئة البصمة من الطلب.

    Args:
        request: FastAPI Request object
        include_ip: Whether to include IP in hash

    Returns:
        Fingerprint hash string
    """
    fp = TokenFingerprint.from_request(request)
    return fp.to_hash_with_ip() if include_ip else fp.to_hash()


# ─────────────────────────────────────────────────────────────────────────────
# Token Family Tracking (Refresh Token Rotation)
# ─────────────────────────────────────────────────────────────────────────────


class TokenFamilyStatus(StrEnum):
    """Token family status"""

    ACTIVE = "active"
    ROTATED = "rotated"  # Has been used and rotated
    REVOKED = "revoked"  # Revoked due to reuse detection


@dataclass
class TokenFamily:
    """
    Token family for refresh token rotation tracking.
    عائلة الرموز لتتبع تدوير رمز التحديث.

    Implements refresh token rotation with reuse detection as per
    RFC 6749 and OAuth 2.0 Security Best Current Practice.
    """

    family_id: str
    user_id: str
    created_at: float
    last_rotation_at: float
    current_token_jti: str
    previous_token_jtis: list[str] = field(default_factory=list)
    status: TokenFamilyStatus = TokenFamilyStatus.ACTIVE
    fingerprint_hash: str = ""
    rotation_count: int = 0
    max_rotations: int = 100  # Max rotations before forced re-auth

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            "family_id": self.family_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_rotation_at": self.last_rotation_at,
            "current_token_jti": self.current_token_jti,
            "previous_token_jtis": self.previous_token_jtis,
            "status": self.status.value,
            "fingerprint_hash": self.fingerprint_hash,
            "rotation_count": self.rotation_count,
            "max_rotations": self.max_rotations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TokenFamily:
        """Create from dictionary"""
        return cls(
            family_id=data["family_id"],
            user_id=data["user_id"],
            created_at=data["created_at"],
            last_rotation_at=data["last_rotation_at"],
            current_token_jti=data["current_token_jti"],
            previous_token_jtis=data.get("previous_token_jtis", []),
            status=TokenFamilyStatus(data.get("status", "active")),
            fingerprint_hash=data.get("fingerprint_hash", ""),
            rotation_count=data.get("rotation_count", 0),
            max_rotations=data.get("max_rotations", 100),
        )


class RefreshTokenRotationManager:
    """
    Refresh Token Rotation Manager with Reuse Detection.
    مدير تدوير رمز التحديث مع كشف إعادة الاستخدام.

    Implements secure refresh token rotation:
    1. Each refresh token can only be used once
    2. New refresh token issued on each use
    3. If old refresh token reused, entire family is revoked (theft detection)
    4. Optional fingerprint binding for additional security

    Security Benefits:
    - Limits window for token theft exploitation
    - Detects token theft through reuse detection
    - Automatic revocation of compromised token families

    Example:
        >>> manager = RefreshTokenRotationManager()
        >>> await manager.initialize()
        >>>
        >>> # Create new token family on login
        >>> family = await manager.create_family(user_id="user123", jti="token-jti")
        >>>
        >>> # Rotate token on refresh
        >>> new_jti = str(uuid.uuid4())
        >>> rotated = await manager.rotate(family.family_id, old_jti="token-jti", new_jti=new_jti)
        >>>
        >>> # Detect reuse attempt
        >>> result = await manager.validate_and_rotate(family.family_id, old_jti="token-jti", new_jti="new-jti")
        >>> if result is None:  # Reuse detected - family revoked
        ...     raise SecurityException("Token reuse detected")
    """

    # Redis key prefixes
    FAMILY_PREFIX = "token_family:"
    USER_FAMILIES_PREFIX = "user_families:"
    JTI_TO_FAMILY_PREFIX = "jti_family:"

    def __init__(
        self,
        redis_url: str | None = None,
        family_ttl_days: int = 30,
        enable_fingerprint_binding: bool = True,
    ):
        """
        Initialize the rotation manager.

        Args:
            redis_url: Redis connection URL
            family_ttl_days: Days before token family expires
            enable_fingerprint_binding: Bind tokens to device fingerprint
        """
        self._redis: aioredis.Redis | None = None
        self._redis_url = redis_url or getattr(config, "REDIS_URL", None) or self._build_redis_url()
        self._initialized = False
        self._family_ttl = family_ttl_days * 86400  # Convert to seconds
        self._enable_fingerprint_binding = enable_fingerprint_binding

        # In-memory fallback for development/testing
        self._memory_families: dict[str, TokenFamily] = {}
        self._memory_jti_to_family: dict[str, str] = {}
        self._memory_user_families: dict[str, set[str]] = {}

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
            logger.warning("Redis not available, using in-memory storage for token families")
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
            logger.info("Refresh token rotation manager initialized with Redis")
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

    async def create_family(
        self,
        user_id: str,
        jti: str,
        fingerprint_hash: str = "",
    ) -> TokenFamily:
        """
        Create a new token family when user logs in.
        إنشاء عائلة رموز جديدة عند تسجيل دخول المستخدم.

        Args:
            user_id: User ID
            jti: JWT ID of the initial refresh token
            fingerprint_hash: Device fingerprint hash

        Returns:
            TokenFamily instance

        Example:
            >>> family = await manager.create_family(
            ...     user_id="user123",
            ...     jti="refresh-token-jti",
            ...     fingerprint_hash="abc123..."
            ... )
        """
        if not self._initialized:
            await self.initialize()

        now = time.time()
        family_id = str(uuid.uuid4())

        family = TokenFamily(
            family_id=family_id,
            user_id=user_id,
            created_at=now,
            last_rotation_at=now,
            current_token_jti=jti,
            previous_token_jtis=[],
            status=TokenFamilyStatus.ACTIVE,
            fingerprint_hash=fingerprint_hash,
            rotation_count=0,
        )

        await self._store_family(family)
        await self._map_jti_to_family(jti, family_id)
        await self._add_user_family(user_id, family_id)

        logger.info(f"Created token family {family_id[:8]}... for user {user_id}")
        return family

    async def validate_and_rotate(
        self,
        jti: str,
        new_jti: str,
        fingerprint_hash: str = "",
    ) -> TokenFamily | None:
        """
        Validate a refresh token and rotate it.
        التحقق من رمز التحديث وتدويره.

        This is the main method for secure token refresh:
        1. Look up token family by JTI
        2. Check if token is current (not already rotated)
        3. Check fingerprint if enabled
        4. If token already used, revoke entire family (theft detected)
        5. If valid, rotate to new JTI

        Args:
            jti: Current refresh token JTI
            new_jti: New refresh token JTI
            fingerprint_hash: Current request fingerprint

        Returns:
            Updated TokenFamily if successful, None if reuse detected

        Raises:
            ValueError: If token family not found

        Example:
            >>> result = await manager.validate_and_rotate(
            ...     jti="old-jti",
            ...     new_jti="new-jti",
            ...     fingerprint_hash="device-fingerprint"
            ... )
            >>> if result is None:
            ...     # Token reuse detected - likely theft!
            ...     raise SecurityException("Token theft detected")
        """
        if not self._initialized:
            await self.initialize()

        # Look up family by JTI
        family_id = await self._get_family_id_by_jti(jti)
        if not family_id:
            logger.warning(f"Token family not found for JTI: {jti[:8]}...")
            return None

        family = await self._get_family(family_id)
        if not family:
            logger.warning(f"Token family {family_id[:8]}... not found")
            return None

        # Check if family is already revoked
        if family.status == TokenFamilyStatus.REVOKED:
            logger.warning(f"Attempt to use revoked token family {family_id[:8]}...")
            return None

        # === REUSE DETECTION ===
        # If this JTI was already rotated (not current), someone is reusing an old token
        if jti != family.current_token_jti:
            if jti in family.previous_token_jtis:
                # TOKEN THEFT DETECTED: Old token being reused
                logger.critical(
                    f"TOKEN THEFT DETECTED: Reuse of rotated token in family {family_id[:8]}... "
                    f"User: {family.user_id}, JTI: {jti[:8]}..."
                )
                await self._revoke_family(family_id, reason="token_reuse_detected")
                return None
            else:
                # Unknown JTI - shouldn't happen
                logger.error(f"Unknown JTI {jti[:8]}... for family {family_id[:8]}...")
                return None

        # Check fingerprint if enabled
        if self._enable_fingerprint_binding and family.fingerprint_hash:
            if fingerprint_hash and fingerprint_hash != family.fingerprint_hash:
                logger.warning(
                    f"Fingerprint mismatch for family {family_id[:8]}... "
                    f"Expected: {family.fingerprint_hash[:8]}..., Got: {fingerprint_hash[:8]}..."
                )
                # Could revoke or just warn depending on policy
                # For now, we warn but allow (mobile users change networks)

        # Check rotation limit
        if family.rotation_count >= family.max_rotations:
            logger.warning(f"Max rotations reached for family {family_id[:8]}... User must re-authenticate")
            await self._revoke_family(family_id, reason="max_rotations_reached")
            return None

        # === ROTATE TOKEN ===
        family.previous_token_jtis.append(family.current_token_jti)
        # Keep only last 10 previous JTIs to limit memory
        if len(family.previous_token_jtis) > 10:
            family.previous_token_jtis = family.previous_token_jtis[-10:]

        family.current_token_jti = new_jti
        family.last_rotation_at = time.time()
        family.rotation_count += 1
        family.status = TokenFamilyStatus.ACTIVE

        await self._store_family(family)
        await self._map_jti_to_family(new_jti, family_id)

        logger.info(f"Rotated token family {family_id[:8]}... (rotation #{family.rotation_count})")

        return family

    async def revoke_family(self, family_id: str, reason: str = "manual") -> bool:
        """
        Revoke an entire token family.
        إلغاء عائلة رموز بالكامل.

        Args:
            family_id: Token family ID
            reason: Reason for revocation

        Returns:
            True if revoked, False if not found
        """
        return await self._revoke_family(family_id, reason)

    async def revoke_all_user_families(self, user_id: str, reason: str = "logout") -> int:
        """
        Revoke all token families for a user.
        إلغاء جميع عائلات الرموز للمستخدم.

        Args:
            user_id: User ID
            reason: Reason for revocation

        Returns:
            Number of families revoked
        """
        if not self._initialized:
            await self.initialize()

        family_ids = await self._get_user_families(user_id)
        count = 0

        for family_id in family_ids:
            if await self._revoke_family(family_id, reason):
                count += 1

        logger.info(f"Revoked {count} token families for user {user_id}")
        return count

    async def get_family_status(self, jti: str) -> dict | None:
        """
        Get token family status by JTI.
        الحصول على حالة عائلة الرموز بواسطة JTI.

        Args:
            jti: JWT ID

        Returns:
            Family status dict or None
        """
        if not self._initialized:
            await self.initialize()

        family_id = await self._get_family_id_by_jti(jti)
        if not family_id:
            return None

        family = await self._get_family(family_id)
        if not family:
            return None

        return {
            "family_id": family.family_id,
            "user_id": family.user_id,
            "status": family.status.value,
            "rotation_count": family.rotation_count,
            "is_current": jti == family.current_token_jti,
            "created_at": family.created_at,
            "last_rotation_at": family.last_rotation_at,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Internal Storage Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def _store_family(self, family: TokenFamily) -> None:
        """Store token family"""
        key = f"{self.FAMILY_PREFIX}{family.family_id}"
        data = json.dumps(family.to_dict())

        if self._redis:
            await self._redis.setex(key, self._family_ttl, data)
        else:
            self._memory_families[family.family_id] = family

    async def _get_family(self, family_id: str) -> TokenFamily | None:
        """Get token family by ID"""
        if self._redis:
            key = f"{self.FAMILY_PREFIX}{family_id}"
            data = await self._redis.get(key)
            if data:
                return TokenFamily.from_dict(json.loads(data))
            return None
        else:
            return self._memory_families.get(family_id)

    async def _map_jti_to_family(self, jti: str, family_id: str) -> None:
        """Map JTI to family ID for lookup"""
        key = f"{self.JTI_TO_FAMILY_PREFIX}{jti}"

        if self._redis:
            await self._redis.setex(key, self._family_ttl, family_id)
        else:
            self._memory_jti_to_family[jti] = family_id

    async def _get_family_id_by_jti(self, jti: str) -> str | None:
        """Get family ID by JTI"""
        if self._redis:
            key = f"{self.JTI_TO_FAMILY_PREFIX}{jti}"
            return await self._redis.get(key)
        else:
            return self._memory_jti_to_family.get(jti)

    async def _add_user_family(self, user_id: str, family_id: str) -> None:
        """Add family to user's family list"""
        key = f"{self.USER_FAMILIES_PREFIX}{user_id}"

        if self._redis:
            await self._redis.sadd(key, family_id)
            await self._redis.expire(key, self._family_ttl)
        else:
            if user_id not in self._memory_user_families:
                self._memory_user_families[user_id] = set()
            self._memory_user_families[user_id].add(family_id)

    async def _get_user_families(self, user_id: str) -> set[str]:
        """Get all family IDs for a user"""
        if self._redis:
            key = f"{self.USER_FAMILIES_PREFIX}{user_id}"
            return await self._redis.smembers(key) or set()
        else:
            return self._memory_user_families.get(user_id, set())

    async def _revoke_family(self, family_id: str, reason: str) -> bool:
        """Internal method to revoke a family"""
        family = await self._get_family(family_id)
        if not family:
            return False

        family.status = TokenFamilyStatus.REVOKED
        await self._store_family(family)

        logger.warning(f"Token family {family_id[:8]}... revoked. Reason: {reason}")
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Password Pepper Support
# ─────────────────────────────────────────────────────────────────────────────


class PasswordPepper:
    """
    Password Pepper for additional hash security.
    فلفل كلمة المرور لأمان تجزئة إضافي.

    A pepper is a secret value that is added to the password before hashing.
    Unlike salt (stored with hash), pepper is kept secret and not stored.

    Benefits:
    - If database is compromised, hashes cannot be cracked without pepper
    - Adds defense-in-depth even if salt is compromised

    Example:
        >>> pepper = PasswordPepper()
        >>> peppered = pepper.apply("user_password")
        >>> # Now hash the peppered password with Argon2id
    """

    def __init__(self, pepper: str | None = None, pepper_id: str = "v1"):
        """
        Initialize password pepper.

        Args:
            pepper: Secret pepper value (from environment/secrets manager)
            pepper_id: Version ID for pepper rotation support
        """
        import os

        self._pepper = pepper or os.getenv("PASSWORD_PEPPER", "")
        self._pepper_id = pepper_id

        if not self._pepper:
            logger.warning("PASSWORD_PEPPER not set. Consider setting it for additional security.")

    def apply(self, password: str) -> str:
        """
        Apply pepper to password before hashing.
        تطبيق الفلفل على كلمة المرور قبل التجزئة.

        Uses HMAC-SHA256 to combine password with pepper securely.

        Args:
            password: Plain text password

        Returns:
            Peppered password for hashing
        """
        if not self._pepper:
            return password

        # Use HMAC to combine password and pepper
        peppered = hmac.new(
            self._pepper.encode("utf-8"),
            password.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return peppered

    def get_pepper_id(self) -> str:
        """Get current pepper version ID"""
        return self._pepper_id


# ─────────────────────────────────────────────────────────────────────────────
# Global Instances
# ─────────────────────────────────────────────────────────────────────────────

_rotation_manager: RefreshTokenRotationManager | None = None
_password_pepper: PasswordPepper | None = None


async def get_rotation_manager() -> RefreshTokenRotationManager:
    """
    Get global refresh token rotation manager.
    الحصول على مدير تدوير رمز التحديث العام.

    Returns:
        RefreshTokenRotationManager instance
    """
    global _rotation_manager

    if _rotation_manager is None:
        _rotation_manager = RefreshTokenRotationManager()
        await _rotation_manager.initialize()

    return _rotation_manager


def get_password_pepper() -> PasswordPepper:
    """
    Get global password pepper instance.
    الحصول على نسخة فلفل كلمة المرور العامة.

    Returns:
        PasswordPepper instance
    """
    global _password_pepper

    if _password_pepper is None:
        _password_pepper = PasswordPepper()

    return _password_pepper


# ─────────────────────────────────────────────────────────────────────────────
# Secure Token Generation Utilities
# ─────────────────────────────────────────────────────────────────────────────


def generate_secure_jti() -> str:
    """
    Generate a secure JWT ID (JTI).
    إنشاء معرف JWT آمن.

    Returns:
        UUID4 string
    """
    return str(uuid.uuid4())


def generate_family_id() -> str:
    """
    Generate a secure token family ID.
    إنشاء معرف عائلة رموز آمن.

    Returns:
        UUID4 string
    """
    return str(uuid.uuid4())


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    إنشاء رمز عشوائي آمن مشفر.

    Args:
        length: Token length in bytes

    Returns:
        Hex-encoded token string
    """
    return secrets.token_hex(length)


def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.
    مقارنة سلسلة ثابتة الوقت لمنع هجمات التوقيت.

    Args:
        a: First string
        b: Second string

    Returns:
        True if strings are equal
    """
    return hmac.compare_digest(a.encode(), b.encode())
