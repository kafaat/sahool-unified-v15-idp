"""
Security Audit Logging for SAHOOL Platform
تسجيل تدقيق الأمان لمنصة سهول

This module provides comprehensive security event logging:
- Authentication events (login, logout, failed attempts)
- Authorization events (access denied, permission checks)
- Security incidents (token theft, suspicious activity)
- Session events (create, terminate, expire)
- Configuration changes (role/permission updates)

Designed for:
- Security monitoring and alerting
- Compliance and audit trails
- Incident investigation
- Security analytics

All events include:
- Timestamp with timezone
- User/session context
- Request metadata (IP, user agent)
- Event-specific details
- Bilingual descriptions (AR/EN)
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum, StrEnum
from typing import Any

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import config

logger = logging.getLogger(__name__)


class SecurityEventType(StrEnum):
    """Security event types"""

    # Authentication Events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILED = "auth.login.failed"
    LOGIN_BLOCKED = "auth.login.blocked"
    LOGOUT = "auth.logout"
    LOGOUT_ALL = "auth.logout.all"

    # Token Events
    TOKEN_ISSUED = "auth.token.issued"
    TOKEN_REFRESHED = "auth.token.refreshed"
    TOKEN_REVOKED = "auth.token.revoked"
    TOKEN_EXPIRED = "auth.token.expired"
    TOKEN_THEFT_DETECTED = "auth.token.theft"
    TOKEN_REUSE_DETECTED = "auth.token.reuse"

    # Session Events
    SESSION_CREATED = "session.created"
    SESSION_TERMINATED = "session.terminated"
    SESSION_EXPIRED = "session.expired"
    SESSION_REVOKED = "session.revoked"
    SESSION_LIMIT_EXCEEDED = "session.limit.exceeded"

    # Authorization Events
    ACCESS_GRANTED = "authz.access.granted"
    ACCESS_DENIED = "authz.access.denied"
    PERMISSION_CHECK = "authz.permission.check"
    ROLE_CHECK = "authz.role.check"

    # 2FA Events
    TWOFA_ENABLED = "auth.2fa.enabled"
    TWOFA_DISABLED = "auth.2fa.disabled"
    TWOFA_VERIFIED = "auth.2fa.verified"
    TWOFA_FAILED = "auth.2fa.failed"
    BACKUP_CODE_USED = "auth.2fa.backup.used"

    # Password Events
    PASSWORD_CHANGED = "auth.password.changed"
    PASSWORD_RESET_REQUESTED = "auth.password.reset.requested"
    PASSWORD_RESET_COMPLETED = "auth.password.reset.completed"

    # Account Events
    ACCOUNT_CREATED = "account.created"
    ACCOUNT_VERIFIED = "account.verified"
    ACCOUNT_SUSPENDED = "account.suspended"
    ACCOUNT_ACTIVATED = "account.activated"
    ACCOUNT_DELETED = "account.deleted"

    # Security Incidents
    BRUTE_FORCE_DETECTED = "security.brute_force"
    RATE_LIMIT_EXCEEDED = "security.rate_limit"
    SUSPICIOUS_ACTIVITY = "security.suspicious"
    IP_BLOCKED = "security.ip.blocked"
    FINGERPRINT_MISMATCH = "security.fingerprint.mismatch"

    # Configuration Events
    ROLE_ASSIGNED = "config.role.assigned"
    ROLE_REMOVED = "config.role.removed"
    PERMISSION_GRANTED = "config.permission.granted"
    PERMISSION_REVOKED = "config.permission.revoked"


class SecurityEventSeverity(StrEnum):
    """Event severity levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Severity mapping for event types
EVENT_SEVERITY_MAP: dict[SecurityEventType, SecurityEventSeverity] = {
    # Info level
    SecurityEventType.LOGIN_SUCCESS: SecurityEventSeverity.INFO,
    SecurityEventType.LOGOUT: SecurityEventSeverity.INFO,
    SecurityEventType.TOKEN_ISSUED: SecurityEventSeverity.INFO,
    SecurityEventType.TOKEN_REFRESHED: SecurityEventSeverity.INFO,
    SecurityEventType.SESSION_CREATED: SecurityEventSeverity.INFO,
    SecurityEventType.ACCESS_GRANTED: SecurityEventSeverity.DEBUG,
    SecurityEventType.TWOFA_VERIFIED: SecurityEventSeverity.INFO,
    SecurityEventType.PASSWORD_CHANGED: SecurityEventSeverity.INFO,
    SecurityEventType.ACCOUNT_CREATED: SecurityEventSeverity.INFO,
    SecurityEventType.ACCOUNT_VERIFIED: SecurityEventSeverity.INFO,
    # Warning level
    SecurityEventType.LOGIN_FAILED: SecurityEventSeverity.WARNING,
    SecurityEventType.TOKEN_EXPIRED: SecurityEventSeverity.INFO,
    SecurityEventType.SESSION_EXPIRED: SecurityEventSeverity.INFO,
    SecurityEventType.ACCESS_DENIED: SecurityEventSeverity.WARNING,
    SecurityEventType.TWOFA_FAILED: SecurityEventSeverity.WARNING,
    SecurityEventType.SESSION_LIMIT_EXCEEDED: SecurityEventSeverity.WARNING,
    SecurityEventType.RATE_LIMIT_EXCEEDED: SecurityEventSeverity.WARNING,
    SecurityEventType.FINGERPRINT_MISMATCH: SecurityEventSeverity.WARNING,
    # Error level
    SecurityEventType.LOGIN_BLOCKED: SecurityEventSeverity.ERROR,
    SecurityEventType.TOKEN_REVOKED: SecurityEventSeverity.WARNING,
    SecurityEventType.SESSION_REVOKED: SecurityEventSeverity.WARNING,
    SecurityEventType.BRUTE_FORCE_DETECTED: SecurityEventSeverity.ERROR,
    SecurityEventType.ACCOUNT_SUSPENDED: SecurityEventSeverity.WARNING,
    # Critical level
    SecurityEventType.TOKEN_THEFT_DETECTED: SecurityEventSeverity.CRITICAL,
    SecurityEventType.TOKEN_REUSE_DETECTED: SecurityEventSeverity.CRITICAL,
    SecurityEventType.SUSPICIOUS_ACTIVITY: SecurityEventSeverity.CRITICAL,
    SecurityEventType.IP_BLOCKED: SecurityEventSeverity.ERROR,
}

# Bilingual event descriptions
EVENT_DESCRIPTIONS: dict[SecurityEventType, dict[str, str]] = {
    SecurityEventType.LOGIN_SUCCESS: {
        "en": "User logged in successfully",
        "ar": "تسجيل دخول المستخدم بنجاح",
    },
    SecurityEventType.LOGIN_FAILED: {
        "en": "Login attempt failed",
        "ar": "فشل محاولة تسجيل الدخول",
    },
    SecurityEventType.LOGIN_BLOCKED: {
        "en": "Login blocked due to security policy",
        "ar": "تم حظر تسجيل الدخول بسبب سياسة الأمان",
    },
    SecurityEventType.LOGOUT: {
        "en": "User logged out",
        "ar": "تسجيل خروج المستخدم",
    },
    SecurityEventType.TOKEN_THEFT_DETECTED: {
        "en": "Token theft detected - security breach",
        "ar": "تم اكتشاف سرقة الرمز - خرق أمني",
    },
    SecurityEventType.TOKEN_REUSE_DETECTED: {
        "en": "Token reuse detected - possible theft",
        "ar": "تم اكتشاف إعادة استخدام الرمز - سرقة محتملة",
    },
    SecurityEventType.BRUTE_FORCE_DETECTED: {
        "en": "Brute force attack detected",
        "ar": "تم اكتشاف هجوم القوة الغاشمة",
    },
    SecurityEventType.SUSPICIOUS_ACTIVITY: {
        "en": "Suspicious activity detected",
        "ar": "تم اكتشاف نشاط مشبوه",
    },
    SecurityEventType.ACCESS_DENIED: {
        "en": "Access denied - insufficient permissions",
        "ar": "تم رفض الوصول - أذونات غير كافية",
    },
    SecurityEventType.SESSION_CREATED: {
        "en": "New session created",
        "ar": "تم إنشاء جلسة جديدة",
    },
    SecurityEventType.SESSION_TERMINATED: {
        "en": "Session terminated",
        "ar": "تم إنهاء الجلسة",
    },
    SecurityEventType.TWOFA_ENABLED: {
        "en": "Two-factor authentication enabled",
        "ar": "تم تمكين المصادقة الثنائية",
    },
    SecurityEventType.PASSWORD_CHANGED: {
        "en": "Password changed",
        "ar": "تم تغيير كلمة المرور",
    },
}


@dataclass
class SecurityEvent:
    """
    Security audit event.
    حدث تدقيق الأمان.
    """

    event_id: str
    event_type: SecurityEventType
    timestamp: float
    severity: SecurityEventSeverity

    # Context
    user_id: str | None = None
    tenant_id: str | None = None
    session_id: str | None = None

    # Request metadata
    ip_address: str = ""
    user_agent: str = ""
    request_path: str = ""
    request_method: str = ""

    # Event details
    details: dict = field(default_factory=dict)
    description_en: str = ""
    description_ar: str = ""

    # Outcome
    success: bool = True
    error_code: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage/serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "timestamp_iso": datetime.fromtimestamp(self.timestamp, tz=UTC).isoformat(),
            "severity": self.severity.value,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_path": self.request_path,
            "request_method": self.request_method,
            "details": self.details,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "success": self.success,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SecurityEvent:
        """Create from dictionary"""
        return cls(
            event_id=data["event_id"],
            event_type=SecurityEventType(data["event_type"]),
            timestamp=data["timestamp"],
            severity=SecurityEventSeverity(data.get("severity", "info")),
            user_id=data.get("user_id"),
            tenant_id=data.get("tenant_id"),
            session_id=data.get("session_id"),
            ip_address=data.get("ip_address", ""),
            user_agent=data.get("user_agent", ""),
            request_path=data.get("request_path", ""),
            request_method=data.get("request_method", ""),
            details=data.get("details", {}),
            description_en=data.get("description_en", ""),
            description_ar=data.get("description_ar", ""),
            success=data.get("success", True),
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
        )

    def to_log_format(self) -> str:
        """Format for structured logging"""
        return json.dumps(self.to_dict(), default=str)


class SecurityAuditLogger:
    """
    Security Audit Logger.
    مسجل تدقيق الأمان.

    Provides centralized security event logging with:
    - Multiple output destinations (Redis, log files)
    - Event querying and analysis
    - Failed attempt tracking
    - Alerting integration

    Example:
        >>> audit = SecurityAuditLogger()
        >>> await audit.initialize()
        >>>
        >>> # Log login success
        >>> await audit.log_login_success(
        ...     user_id="user123",
        ...     ip_address="192.168.1.1",
        ...     session_id="session-id"
        ... )
        >>>
        >>> # Log failed login
        >>> await audit.log_login_failed(
        ...     user_id="user123",
        ...     ip_address="192.168.1.1",
        ...     reason="invalid_password"
        ... )
        >>>
        >>> # Check failed attempts
        >>> count = await audit.get_failed_login_count("user123", minutes=15)
    """

    # Redis key prefixes
    EVENT_PREFIX = "audit:event:"
    USER_EVENTS_PREFIX = "audit:user:"
    FAILED_LOGIN_PREFIX = "audit:failed:"
    IP_EVENTS_PREFIX = "audit:ip:"
    RECENT_EVENTS_KEY = "audit:recent"

    # Configuration
    MAX_RECENT_EVENTS = 1000
    EVENT_TTL_DAYS = 90
    FAILED_ATTEMPT_WINDOW = 900  # 15 minutes

    def __init__(
        self,
        redis_url: str | None = None,
        log_to_file: bool = True,
        log_to_console: bool = True,
    ):
        """
        Initialize audit logger.

        Args:
            redis_url: Redis connection URL
            log_to_file: Also log to file via Python logger
            log_to_console: Also log to console
        """
        self._redis: aioredis.Redis | None = None
        self._redis_url = redis_url or getattr(config, "REDIS_URL", None) or self._build_redis_url()
        self._initialized = False
        self._log_to_file = log_to_file
        self._log_to_console = log_to_console

        # In-memory fallback
        self._memory_events: list[SecurityEvent] = []
        self._memory_failed_logins: dict[str, list[float]] = {}

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
            logger.warning("Redis not available, using in-memory audit storage")
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
            logger.info("Security audit logger initialized with Redis")
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

    async def log_event(
        self,
        event_type: SecurityEventType,
        user_id: str | None = None,
        tenant_id: str | None = None,
        session_id: str | None = None,
        ip_address: str = "",
        user_agent: str = "",
        request_path: str = "",
        request_method: str = "",
        details: dict | None = None,
        success: bool = True,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> SecurityEvent:
        """
        Log a security event.
        تسجيل حدث أمني.

        Args:
            event_type: Type of security event
            user_id: User ID (if applicable)
            tenant_id: Tenant ID (if applicable)
            session_id: Session ID (if applicable)
            ip_address: Client IP address
            user_agent: Client user agent
            request_path: API request path
            request_method: HTTP method
            details: Additional event details
            success: Whether the action succeeded
            error_code: Error code if failed
            error_message: Error message if failed

        Returns:
            SecurityEvent instance
        """
        if not self._initialized:
            await self.initialize()

        # Get severity and description
        severity = EVENT_SEVERITY_MAP.get(event_type, SecurityEventSeverity.INFO)
        descriptions = EVENT_DESCRIPTIONS.get(event_type, {"en": "", "ar": ""})

        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=time.time(),
            severity=severity,
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else "",
            request_path=request_path,
            request_method=request_method,
            details=details or {},
            description_en=descriptions.get("en", ""),
            description_ar=descriptions.get("ar", ""),
            success=success,
            error_code=error_code,
            error_message=error_message,
        )

        # Store event
        await self._store_event(event)

        # Log to Python logger
        if self._log_to_file or self._log_to_console:
            self._log_to_python_logger(event)

        return event

    # ─────────────────────────────────────────────────────────────────────────
    # Convenience Methods for Common Events
    # ─────────────────────────────────────────────────────────────────────────

    async def log_login_success(
        self,
        user_id: str,
        ip_address: str,
        session_id: str | None = None,
        tenant_id: str | None = None,
        user_agent: str = "",
        method: str = "password",
    ) -> SecurityEvent:
        """Log successful login"""
        return await self.log_event(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"auth_method": method},
            success=True,
        )

    async def log_login_failed(
        self,
        user_id: str | None,
        ip_address: str,
        reason: str,
        user_agent: str = "",
    ) -> SecurityEvent:
        """Log failed login attempt"""
        # Track failed attempts
        await self._track_failed_login(user_id or ip_address)

        return await self.log_event(
            event_type=SecurityEventType.LOGIN_FAILED,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"reason": reason},
            success=False,
            error_code="login_failed",
            error_message=reason,
        )

    async def log_logout(
        self,
        user_id: str,
        session_id: str | None = None,
        ip_address: str = "",
        logout_all: bool = False,
    ) -> SecurityEvent:
        """Log user logout"""
        event_type = SecurityEventType.LOGOUT_ALL if logout_all else SecurityEventType.LOGOUT

        return await self.log_event(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            details={"logout_all": logout_all},
            success=True,
        )

    async def log_token_issued(
        self,
        user_id: str,
        token_type: str,
        jti: str,
        ip_address: str = "",
    ) -> SecurityEvent:
        """Log token issuance"""
        return await self.log_event(
            event_type=SecurityEventType.TOKEN_ISSUED,
            user_id=user_id,
            ip_address=ip_address,
            details={"token_type": token_type, "jti": jti[:8] + "..."},
            success=True,
        )

    async def log_token_theft_detected(
        self,
        user_id: str,
        family_id: str,
        jti: str,
        ip_address: str = "",
    ) -> SecurityEvent:
        """Log token theft detection - CRITICAL"""
        return await self.log_event(
            event_type=SecurityEventType.TOKEN_THEFT_DETECTED,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "family_id": family_id[:8] + "...",
                "reused_jti": jti[:8] + "...",
            },
            success=False,
            error_code="token_theft",
            error_message="Token reuse detected - possible theft",
        )

    async def log_access_denied(
        self,
        user_id: str,
        resource: str,
        action: str,
        ip_address: str = "",
        required_permission: str = "",
    ) -> SecurityEvent:
        """Log access denied event"""
        return await self.log_event(
            event_type=SecurityEventType.ACCESS_DENIED,
            user_id=user_id,
            ip_address=ip_address,
            request_path=resource,
            details={
                "action": action,
                "required_permission": required_permission,
            },
            success=False,
            error_code="access_denied",
            error_message="Insufficient permissions",
        )

    async def log_session_created(
        self,
        user_id: str,
        session_id: str,
        ip_address: str,
        device_type: str,
        user_agent: str = "",
    ) -> SecurityEvent:
        """Log session creation"""
        return await self.log_event(
            event_type=SecurityEventType.SESSION_CREATED,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"device_type": device_type},
            success=True,
        )

    async def log_2fa_event(
        self,
        user_id: str,
        event_type: SecurityEventType,
        success: bool,
        ip_address: str = "",
        method: str = "totp",
    ) -> SecurityEvent:
        """Log 2FA event"""
        return await self.log_event(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details={"method": method},
            success=success,
        )

    async def log_brute_force_detected(
        self,
        identifier: str,
        attempt_count: int,
        ip_address: str,
        window_minutes: int = 15,
    ) -> SecurityEvent:
        """Log brute force detection"""
        return await self.log_event(
            event_type=SecurityEventType.BRUTE_FORCE_DETECTED,
            user_id=identifier if "@" in identifier else None,
            ip_address=ip_address,
            details={
                "attempt_count": attempt_count,
                "window_minutes": window_minutes,
                "identifier": identifier,
            },
            success=False,
            error_code="brute_force",
            error_message=f"{attempt_count} failed attempts in {window_minutes} minutes",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Query Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def get_failed_login_count(
        self,
        identifier: str,
        minutes: int = 15,
    ) -> int:
        """
        Get count of failed login attempts.
        الحصول على عدد محاولات تسجيل الدخول الفاشلة.

        Args:
            identifier: User ID or IP address
            minutes: Time window in minutes

        Returns:
            Number of failed attempts
        """
        if not self._initialized:
            await self.initialize()

        now = time.time()
        window = now - (minutes * 60)

        if self._redis:
            key = f"{self.FAILED_LOGIN_PREFIX}{identifier}"
            # Remove old entries
            await self._redis.zremrangebyscore(key, 0, window)
            # Count remaining
            return await self._redis.zcard(key)
        else:
            attempts = self._memory_failed_logins.get(identifier, [])
            return len([ts for ts in attempts if ts > window])

    async def get_user_events(
        self,
        user_id: str,
        limit: int = 100,
        event_types: list[SecurityEventType] | None = None,
    ) -> list[SecurityEvent]:
        """
        Get security events for a user.
        الحصول على أحداث الأمان للمستخدم.

        Args:
            user_id: User ID
            limit: Maximum events to return
            event_types: Filter by event types

        Returns:
            List of SecurityEvent objects
        """
        if not self._initialized:
            await self.initialize()

        events = []

        if self._redis:
            key = f"{self.USER_EVENTS_PREFIX}{user_id}"
            event_ids = await self._redis.lrange(key, 0, limit - 1)

            for event_id in event_ids:
                event_key = f"{self.EVENT_PREFIX}{event_id}"
                data = await self._redis.get(event_key)
                if data:
                    event = SecurityEvent.from_dict(json.loads(data))
                    if event_types is None or event.event_type in event_types:
                        events.append(event)
        else:
            for event in reversed(self._memory_events[-limit:]):
                if event.user_id == user_id:
                    if event_types is None or event.event_type in event_types:
                        events.append(event)
                        if len(events) >= limit:
                            break

        return events

    async def get_recent_security_incidents(
        self,
        hours: int = 24,
        severity_min: SecurityEventSeverity = SecurityEventSeverity.WARNING,
    ) -> list[SecurityEvent]:
        """
        Get recent security incidents.
        الحصول على الحوادث الأمنية الأخيرة.

        Args:
            hours: Look back period in hours
            severity_min: Minimum severity level

        Returns:
            List of security incident events
        """
        if not self._initialized:
            await self.initialize()

        cutoff = time.time() - (hours * 3600)
        severity_order = [
            SecurityEventSeverity.DEBUG,
            SecurityEventSeverity.INFO,
            SecurityEventSeverity.WARNING,
            SecurityEventSeverity.ERROR,
            SecurityEventSeverity.CRITICAL,
        ]
        min_index = severity_order.index(severity_min)

        incidents = []

        if self._redis:
            # Get from recent events sorted set
            event_ids = await self._redis.zrangebyscore(
                self.RECENT_EVENTS_KEY,
                cutoff,
                "+inf",
            )

            for event_id in event_ids:
                event_key = f"{self.EVENT_PREFIX}{event_id}"
                data = await self._redis.get(event_key)
                if data:
                    event = SecurityEvent.from_dict(json.loads(data))
                    if severity_order.index(event.severity) >= min_index:
                        incidents.append(event)
        else:
            for event in self._memory_events:
                if event.timestamp >= cutoff:
                    if severity_order.index(event.severity) >= min_index:
                        incidents.append(event)

        return sorted(incidents, key=lambda e: e.timestamp, reverse=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Internal Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def _store_event(self, event: SecurityEvent) -> None:
        """Store security event"""
        ttl = self.EVENT_TTL_DAYS * 86400

        if self._redis:
            # Store event data
            event_key = f"{self.EVENT_PREFIX}{event.event_id}"
            await self._redis.setex(event_key, ttl, json.dumps(event.to_dict()))

            # Add to user events list
            if event.user_id:
                user_key = f"{self.USER_EVENTS_PREFIX}{event.user_id}"
                await self._redis.lpush(user_key, event.event_id)
                await self._redis.ltrim(user_key, 0, 999)
                await self._redis.expire(user_key, ttl)

            # Add to IP events list
            if event.ip_address:
                ip_key = f"{self.IP_EVENTS_PREFIX}{event.ip_address}"
                await self._redis.lpush(ip_key, event.event_id)
                await self._redis.ltrim(ip_key, 0, 499)
                await self._redis.expire(ip_key, ttl)

            # Add to recent events sorted set
            await self._redis.zadd(
                self.RECENT_EVENTS_KEY,
                {event.event_id: event.timestamp},
            )
            # Keep only recent events
            await self._redis.zremrangebyrank(
                self.RECENT_EVENTS_KEY,
                0,
                -self.MAX_RECENT_EVENTS - 1,
            )
            # Ensure TTL on recent events set to prevent unbounded growth
            await self._redis.expire(self.RECENT_EVENTS_KEY, ttl)
        else:
            self._memory_events.append(event)
            # Keep memory bounded
            if len(self._memory_events) > self.MAX_RECENT_EVENTS:
                self._memory_events = self._memory_events[-self.MAX_RECENT_EVENTS :]

    async def _track_failed_login(self, identifier: str) -> None:
        """Track failed login attempt"""
        now = time.time()

        if self._redis:
            key = f"{self.FAILED_LOGIN_PREFIX}{identifier}"
            await self._redis.zadd(key, {str(now): now})
            await self._redis.expire(key, self.FAILED_ATTEMPT_WINDOW)
        else:
            if identifier not in self._memory_failed_logins:
                self._memory_failed_logins[identifier] = []
            self._memory_failed_logins[identifier].append(now)
            # Clean old entries
            window = now - self.FAILED_ATTEMPT_WINDOW
            self._memory_failed_logins[identifier] = [
                ts for ts in self._memory_failed_logins[identifier] if ts > window
            ]

    def _log_to_python_logger(self, event: SecurityEvent) -> None:
        """Log event using Python logger"""
        severity_map = {
            SecurityEventSeverity.DEBUG: logging.DEBUG,
            SecurityEventSeverity.INFO: logging.INFO,
            SecurityEventSeverity.WARNING: logging.WARNING,
            SecurityEventSeverity.ERROR: logging.ERROR,
            SecurityEventSeverity.CRITICAL: logging.CRITICAL,
        }

        level = severity_map.get(event.severity, logging.INFO)

        logger.log(
            level,
            f"[SECURITY] {event.event_type.value} | "
            f"User: {event.user_id or 'N/A'} | "
            f"IP: {event.ip_address or 'N/A'} | "
            f"Success: {event.success}",
            extra={
                "security_event": event.to_dict(),
                "event_type": event.event_type.value,
                "user_id": event.user_id,
                "ip_address": event.ip_address,
            },
        )


# ─────────────────────────────────────────────────────────────────────────────
# Global Instance
# ─────────────────────────────────────────────────────────────────────────────

_security_audit: SecurityAuditLogger | None = None


async def get_security_audit_logger() -> SecurityAuditLogger:
    """
    Get global security audit logger.
    الحصول على مسجل تدقيق الأمان العام.

    Returns:
        SecurityAuditLogger instance
    """
    global _security_audit

    if _security_audit is None:
        _security_audit = SecurityAuditLogger()
        await _security_audit.initialize()

    return _security_audit


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────


async def audit_login_success(
    user_id: str,
    ip_address: str,
    session_id: str | None = None,
    **kwargs,
) -> SecurityEvent:
    """Quick helper for login success audit"""
    audit = await get_security_audit_logger()
    return await audit.log_login_success(
        user_id=user_id,
        ip_address=ip_address,
        session_id=session_id,
        **kwargs,
    )


async def audit_login_failed(
    user_id: str | None,
    ip_address: str,
    reason: str,
    **kwargs,
) -> SecurityEvent:
    """Quick helper for login failure audit"""
    audit = await get_security_audit_logger()
    return await audit.log_login_failed(
        user_id=user_id,
        ip_address=ip_address,
        reason=reason,
        **kwargs,
    )


async def check_brute_force(
    identifier: str,
    ip_address: str,
    max_attempts: int = 5,
    window_minutes: int = 15,
) -> bool:
    """
    Check for brute force attack and log if detected.
    التحقق من هجوم القوة الغاشمة والتسجيل إذا تم اكتشافه.

    Args:
        identifier: User ID or email
        ip_address: Client IP
        max_attempts: Maximum allowed attempts
        window_minutes: Time window in minutes

    Returns:
        True if brute force detected (should block)
    """
    audit = await get_security_audit_logger()
    count = await audit.get_failed_login_count(identifier, window_minutes)

    if count >= max_attempts:
        await audit.log_brute_force_detected(
            identifier=identifier,
            attempt_count=count,
            ip_address=ip_address,
            window_minutes=window_minutes,
        )
        return True

    return False
