"""
Session Management for SAHOOL Platform
إدارة الجلسات لمنصة سهول

This module provides comprehensive session management:
- Session tracking and lifecycle management
- Concurrent session limits per user
- Device/browser identification
- Session activity monitoring
- Automatic session expiry and cleanup
- Session security (binding, fingerprinting)

Security Features:
- Session binding to device fingerprint
- Idle timeout and absolute timeout
- Concurrent session limit enforcement
- Session activity logging
- Suspicious activity detection
"""

from __future__ import annotations

import json
import logging
import math
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import geoip2.database as _geoip2_database

    GEOIP_AVAILABLE = True
except ImportError:
    _geoip2_database = None  # type: ignore[assignment]
    GEOIP_AVAILABLE = False

from .config import config
from .security_enhancements import TokenFingerprint

logger = logging.getLogger(__name__)


class SessionStatus(StrEnum):
    """Session status"""

    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"  # Explicitly ended
    REVOKED = "revoked"  # Security revocation


@dataclass
class SessionInfo:
    """
    Session information container.
    حاوية معلومات الجلسة.
    """

    session_id: str
    user_id: str
    tenant_id: str | None
    created_at: float
    last_activity_at: float
    expires_at: float
    status: SessionStatus
    ip_address: str
    user_agent: str
    device_type: str  # mobile, desktop, tablet
    fingerprint_hash: str
    refresh_token_jti: str | None = None
    access_token_jti: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at,
            "last_activity_at": self.last_activity_at,
            "expires_at": self.expires_at,
            "status": self.status.value,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_type": self.device_type,
            "fingerprint_hash": self.fingerprint_hash,
            "refresh_token_jti": self.refresh_token_jti,
            "access_token_jti": self.access_token_jti,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SessionInfo:
        """Create from dictionary"""
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            tenant_id=data.get("tenant_id"),
            created_at=data["created_at"],
            last_activity_at=data["last_activity_at"],
            expires_at=data["expires_at"],
            status=SessionStatus(data.get("status", "active")),
            ip_address=data.get("ip_address", ""),
            user_agent=data.get("user_agent", ""),
            device_type=data.get("device_type", "unknown"),
            fingerprint_hash=data.get("fingerprint_hash", ""),
            refresh_token_jti=data.get("refresh_token_jti"),
            access_token_jti=data.get("access_token_jti"),
            metadata=data.get("metadata", {}),
        )

    def is_expired(self) -> bool:
        """Check if session is expired"""
        return time.time() > self.expires_at

    def is_idle_timeout(self, idle_timeout_seconds: int) -> bool:
        """Check if session has exceeded idle timeout"""
        return time.time() - self.last_activity_at > idle_timeout_seconds

    def is_active(self, idle_timeout_seconds: int = 1800) -> bool:
        """Check if session is currently active"""
        return (
            self.status == SessionStatus.ACTIVE
            and not self.is_expired()
            and not self.is_idle_timeout(idle_timeout_seconds)
        )


def _detect_device_type(user_agent: str) -> str:
    """
    Detect device type from user agent.
    كشف نوع الجهاز من وكيل المستخدم.
    """
    ua_lower = user_agent.lower()

    if any(mobile in ua_lower for mobile in ["mobile", "android", "iphone", "ipad"]):
        if "ipad" in ua_lower or "tablet" in ua_lower:
            return "tablet"
        return "mobile"
    return "desktop"


class SessionManager:
    """
    Session Manager for user session lifecycle.
    مدير الجلسات لدورة حياة جلسة المستخدم.

    Features:
    - Create and track user sessions
    - Enforce concurrent session limits
    - Automatic session expiry
    - Session activity tracking
    - Device fingerprint binding

    Example:
        >>> manager = SessionManager()
        >>> await manager.initialize()
        >>>
        >>> # Create session on login
        >>> session = await manager.create_session(
        ...     user_id="user123",
        ...     request=request,
        ...     refresh_token_jti="token-jti"
        ... )
        >>>
        >>> # Update activity
        >>> await manager.update_activity(session.session_id)
        >>>
        >>> # List user sessions
        >>> sessions = await manager.get_user_sessions("user123")
        >>>
        >>> # Terminate session
        >>> await manager.terminate_session(session.session_id)
    """

    # Redis key prefixes
    SESSION_PREFIX = "session:"
    USER_SESSIONS_PREFIX = "user_sessions:"
    SESSION_LOCK_PREFIX = "session_lock:"

    # Default configuration
    DEFAULT_IDLE_TIMEOUT = 1800  # 30 minutes
    DEFAULT_ABSOLUTE_TIMEOUT = 86400  # 24 hours
    DEFAULT_MAX_CONCURRENT_SESSIONS = 5

    def __init__(
        self,
        redis_url: str | None = None,
        idle_timeout_seconds: int = DEFAULT_IDLE_TIMEOUT,
        absolute_timeout_seconds: int = DEFAULT_ABSOLUTE_TIMEOUT,
        max_concurrent_sessions: int = DEFAULT_MAX_CONCURRENT_SESSIONS,
        enable_fingerprint_binding: bool = True,
    ):
        """
        Initialize session manager.

        Args:
            redis_url: Redis connection URL
            idle_timeout_seconds: Inactivity timeout (default: 30 min)
            absolute_timeout_seconds: Max session lifetime (default: 24 hours)
            max_concurrent_sessions: Max sessions per user (default: 5)
            enable_fingerprint_binding: Bind sessions to device fingerprint
        """
        self._redis: aioredis.Redis | None = None
        self._redis_url = redis_url or getattr(config, "REDIS_URL", None) or self._build_redis_url()
        self._initialized = False

        self._idle_timeout = idle_timeout_seconds
        self._absolute_timeout = absolute_timeout_seconds
        self._max_concurrent_sessions = max_concurrent_sessions
        self._enable_fingerprint_binding = enable_fingerprint_binding

        # In-memory fallback
        self._memory_sessions: dict[str, SessionInfo] = {}
        self._memory_user_sessions: dict[str, set[str]] = {}

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
            logger.warning("Redis not available, using in-memory session storage")
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
            logger.info("Session manager initialized with Redis")
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

    async def create_session(
        self,
        user_id: str,
        request: Any = None,
        tenant_id: str | None = None,
        refresh_token_jti: str | None = None,
        access_token_jti: str | None = None,
        metadata: dict | None = None,
    ) -> SessionInfo:
        """
        Create a new session for user.
        إنشاء جلسة جديدة للمستخدم.

        This will:
        1. Check concurrent session limit
        2. Create new session with device info
        3. Optionally terminate oldest session if limit exceeded

        Args:
            user_id: User ID
            request: FastAPI Request object (for fingerprinting)
            tenant_id: Optional tenant ID
            refresh_token_jti: Associated refresh token JTI
            access_token_jti: Associated access token JTI
            metadata: Additional session metadata

        Returns:
            SessionInfo instance

        Raises:
            SessionLimitExceeded: If max sessions reached and policy is strict
        """
        if not self._initialized:
            await self.initialize()

        now = time.time()
        session_id = str(uuid.uuid4())

        # Extract request info
        if request:
            fingerprint = TokenFingerprint.from_request(request)
            ip_address = fingerprint.ip_address
            user_agent = fingerprint.user_agent
            fingerprint_hash = fingerprint.to_hash()
        else:
            ip_address = "unknown"
            user_agent = "unknown"
            fingerprint_hash = ""

        device_type = _detect_device_type(user_agent)

        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
            created_at=now,
            last_activity_at=now,
            expires_at=now + self._absolute_timeout,
            status=SessionStatus.ACTIVE,
            ip_address=ip_address,
            user_agent=user_agent[:500],  # Limit user agent length
            device_type=device_type,
            fingerprint_hash=fingerprint_hash,
            refresh_token_jti=refresh_token_jti,
            access_token_jti=access_token_jti,
            metadata=metadata or {},
        )

        # Check concurrent session limit
        await self._enforce_session_limit(user_id)

        # Store session
        await self._store_session(session)
        await self._add_user_session(user_id, session_id)

        logger.info(f"Created session {session_id[:8]}... for user {user_id} (device: {device_type}, ip: {ip_address})")

        return session

    async def get_session(self, session_id: str) -> SessionInfo | None:
        """
        Get session by ID.
        الحصول على الجلسة بالمعرف.

        Args:
            session_id: Session ID

        Returns:
            SessionInfo or None if not found
        """
        if not self._initialized:
            await self.initialize()

        session = await self._get_session(session_id)

        if session and session.is_expired():
            session.status = SessionStatus.EXPIRED
            await self._store_session(session)
            return None

        return session

    async def validate_session(
        self,
        session_id: str,
        fingerprint_hash: str | None = None,
    ) -> tuple[bool, str | None]:
        """
        Validate session is active and optionally check fingerprint.
        التحقق من أن الجلسة نشطة وفحص البصمة اختياريا.

        Args:
            session_id: Session ID
            fingerprint_hash: Current request fingerprint

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self._initialized:
            await self.initialize()

        session = await self._get_session(session_id)

        if not session:
            return False, "Session not found"

        if session.status != SessionStatus.ACTIVE:
            return False, f"Session is {session.status.value}"

        if session.is_expired():
            session.status = SessionStatus.EXPIRED
            await self._store_session(session)
            return False, "Session expired"

        if session.is_idle_timeout(self._idle_timeout):
            session.status = SessionStatus.IDLE
            await self._store_session(session)
            return False, "Session idle timeout"

        # Check fingerprint if enabled
        if self._enable_fingerprint_binding and session.fingerprint_hash and fingerprint_hash:
            if fingerprint_hash != session.fingerprint_hash:
                logger.warning(f"Session {session_id[:8]}... fingerprint mismatch. Possible session hijacking attempt.")
                # Log but don't fail - fingerprints can change legitimately
                # Could implement stricter policy here

        return True, None

    async def update_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp.
        تحديث طابع زمني آخر نشاط للجلسة.

        Call this on each authenticated request.

        Args:
            session_id: Session ID

        Returns:
            True if updated, False if session not found
        """
        if not self._initialized:
            await self.initialize()

        session = await self._get_session(session_id)
        if not session:
            return False

        session.last_activity_at = time.time()
        session.status = SessionStatus.ACTIVE
        await self._store_session(session)

        return True

    async def terminate_session(
        self,
        session_id: str,
        reason: str = "user_logout",
    ) -> bool:
        """
        Terminate a session.
        إنهاء جلسة.

        Args:
            session_id: Session ID
            reason: Termination reason

        Returns:
            True if terminated, False if not found
        """
        if not self._initialized:
            await self.initialize()

        session = await self._get_session(session_id)
        if not session:
            return False

        session.status = SessionStatus.TERMINATED
        await self._store_session(session)

        logger.info(f"Session {session_id[:8]}... terminated. Reason: {reason}")
        return True

    async def revoke_session(
        self,
        session_id: str,
        reason: str = "security",
    ) -> bool:
        """
        Revoke a session (security termination).
        إلغاء جلسة (إنهاء أمني).

        Args:
            session_id: Session ID
            reason: Revocation reason

        Returns:
            True if revoked, False if not found
        """
        if not self._initialized:
            await self.initialize()

        session = await self._get_session(session_id)
        if not session:
            return False

        session.status = SessionStatus.REVOKED
        await self._store_session(session)

        logger.warning(f"Session {session_id[:8]}... REVOKED. Reason: {reason}")
        return True

    async def terminate_all_user_sessions(
        self,
        user_id: str,
        except_session_id: str | None = None,
        reason: str = "user_logout_all",
    ) -> int:
        """
        Terminate all sessions for a user.
        إنهاء جميع جلسات المستخدم.

        Args:
            user_id: User ID
            except_session_id: Session ID to exclude (current session)
            reason: Termination reason

        Returns:
            Number of sessions terminated
        """
        if not self._initialized:
            await self.initialize()

        session_ids = await self._get_user_session_ids(user_id)
        count = 0

        for session_id in session_ids:
            if except_session_id and session_id == except_session_id:
                continue

            if await self.terminate_session(session_id, reason):
                count += 1

        logger.info(f"Terminated {count} sessions for user {user_id}")
        return count

    async def get_user_sessions(
        self,
        user_id: str,
        include_expired: bool = False,
    ) -> list[SessionInfo]:
        """
        Get all sessions for a user.
        الحصول على جميع جلسات المستخدم.

        Args:
            user_id: User ID
            include_expired: Include expired sessions

        Returns:
            List of SessionInfo objects
        """
        if not self._initialized:
            await self.initialize()

        session_ids = await self._get_user_session_ids(user_id)
        sessions = []

        for session_id in session_ids:
            session = await self._get_session(session_id)
            if session:
                if include_expired or session.is_active(self._idle_timeout):
                    sessions.append(session)

        return sessions

    async def get_active_session_count(self, user_id: str) -> int:
        """
        Get count of active sessions for user.
        الحصول على عدد الجلسات النشطة للمستخدم.

        Args:
            user_id: User ID

        Returns:
            Number of active sessions
        """
        sessions = await self.get_user_sessions(user_id)
        return len([s for s in sessions if s.is_active(self._idle_timeout)])

    # ─────────────────────────────────────────────────────────────────────────
    # Internal Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def _store_session(self, session: SessionInfo) -> None:
        """Store session data"""
        key = f"{self.SESSION_PREFIX}{session.session_id}"
        data = json.dumps(session.to_dict())
        ttl = int(session.expires_at - time.time())

        if ttl <= 0:
            ttl = 60  # Keep expired sessions briefly for cleanup

        if self._redis:
            await self._redis.setex(key, ttl, data)
        else:
            self._memory_sessions[session.session_id] = session

    async def _get_session(self, session_id: str) -> SessionInfo | None:
        """Get session by ID"""
        if self._redis:
            key = f"{self.SESSION_PREFIX}{session_id}"
            data = await self._redis.get(key)
            if data:
                return SessionInfo.from_dict(json.loads(data))
            return None
        else:
            return self._memory_sessions.get(session_id)

    async def _add_user_session(self, user_id: str, session_id: str) -> None:
        """Add session to user's session list"""
        key = f"{self.USER_SESSIONS_PREFIX}{user_id}"

        if self._redis:
            await self._redis.sadd(key, session_id)
            await self._redis.expire(key, self._absolute_timeout)
        else:
            if user_id not in self._memory_user_sessions:
                self._memory_user_sessions[user_id] = set()
            self._memory_user_sessions[user_id].add(session_id)

    async def _get_user_session_ids(self, user_id: str) -> set[str]:
        """Get all session IDs for a user"""
        if self._redis:
            key = f"{self.USER_SESSIONS_PREFIX}{user_id}"
            return await self._redis.smembers(key) or set()
        else:
            return self._memory_user_sessions.get(user_id, set())

    async def _enforce_session_limit(self, user_id: str) -> None:
        """Enforce concurrent session limit by terminating oldest sessions"""
        sessions = await self.get_user_sessions(user_id)
        active_sessions = [s for s in sessions if s.is_active(self._idle_timeout)]

        if len(active_sessions) >= self._max_concurrent_sessions:
            # Sort by last activity and terminate oldest
            active_sessions.sort(key=lambda s: s.last_activity_at)

            sessions_to_terminate = len(active_sessions) - self._max_concurrent_sessions + 1

            for session in active_sessions[:sessions_to_terminate]:
                await self.terminate_session(
                    session.session_id,
                    reason="concurrent_session_limit",
                )
                logger.info(
                    f"Terminated oldest session {session.session_id[:8]}... "
                    f"for user {user_id} due to concurrent session limit"
                )


# ─────────────────────────────────────────────────────────────────────────────
# Session Security Utilities
# ─────────────────────────────────────────────────────────────────────────────


class SessionSecurityChecker:
    """
    Security checker for session validation.
    مدقق الأمان للتحقق من الجلسة.
    """

    def __init__(
        self,
        max_ip_changes: int = 5,
        max_rapid_requests: int = 100,
        rapid_request_window: int = 60,
    ):
        """
        Initialize security checker.

        Args:
            max_ip_changes: Max IP changes before flagging session
            max_rapid_requests: Max requests in window before flagging
            rapid_request_window: Window in seconds for rapid request detection
        """
        self.max_ip_changes = max_ip_changes
        self.max_rapid_requests = max_rapid_requests
        self.rapid_request_window = rapid_request_window

    @staticmethod
    def _calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points using the Haversine formula.
        حساب المسافة بين نقطتين باستخدام صيغة هافرساين.

        Args:
            lat1: Latitude of first point in degrees
            lon1: Longitude of first point in degrees
            lat2: Latitude of second point in degrees
            lon2: Longitude of second point in degrees

        Returns:
            Distance in kilometers
        """
        earth_radius_km = 6371.0

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius_km * c

    # Cached GeoIP reader (class-level, opened once on first use)
    _geoip_reader: Any = None
    _geoip_resolved: bool = False

    @classmethod
    def _get_geoip_reader(cls) -> Any:
        """Get or initialize the cached GeoIP reader (opened once)."""
        if cls._geoip_resolved:
            return cls._geoip_reader

        cls._geoip_resolved = True

        if not GEOIP_AVAILABLE or _geoip2_database is None:
            return None

        import os

        db_paths = [
            os.environ.get("GEOIP_DB_PATH", ""),
            "/usr/share/GeoIP/GeoLite2-City.mmdb",
            "/var/lib/GeoIP/GeoLite2-City.mmdb",
            "/opt/geoip/GeoLite2-City.mmdb",
            "/app/data/GeoLite2-City.mmdb",
        ]

        for db_path in db_paths:
            if not db_path or not os.path.isfile(db_path):
                continue
            try:
                cls._geoip_reader = _geoip2_database.Reader(db_path)
                logger.info("GeoIP database loaded from %s", db_path)
                return cls._geoip_reader
            except Exception:
                continue

        return None

    @staticmethod
    def _get_ip_location(ip: str) -> tuple[float, float] | None:
        """
        Get geographic coordinates for an IP address using GeoIP2.
        الحصول على الإحداثيات الجغرافية لعنوان IP.

        Uses a cached GeoIP reader to avoid reopening the database on every call.

        Args:
            ip: IP address string

        Returns:
            Tuple of (latitude, longitude) or None
        """
        reader = SessionSecurityChecker._get_geoip_reader()
        if reader is None:
            return None

        try:
            response = reader.city(ip)
            lat = response.location.latitude
            lon = response.location.longitude
            if lat is not None and lon is not None:
                return (float(lat), float(lon))
        except Exception:
            # Any lookup failure (invalid IP, missing record, etc.) — skip gracefully
            pass

        return None

    def check_ip_anomaly(
        self,
        session: SessionInfo,
        current_ip: str,
        ip_history: list[str],
    ) -> tuple[bool, str | None]:
        """
        Check for suspicious IP changes including geographic anomaly detection.
        التحقق من تغييرات IP المشبوهة بما في ذلك الكشف عن الشذوذ الجغرافي.

        Detects:
        1. Too many unique IPs in session history
        2. Impossible travel — geographically distant IPs in a short time window

        Args:
            session: Current session
            current_ip: Current request IP
            ip_history: Recent IP addresses for session

        Returns:
            Tuple of (is_suspicious, reason)
        """
        unique_ips = set(ip_history + [current_ip])

        if len(unique_ips) > self.max_ip_changes:
            return True, f"Too many IP changes: {len(unique_ips)}"

        # Geographic anomaly detection (impossible travel)
        # We compare the two most recent distinct IPs to detect large jumps.
        try:
            if len(ip_history) >= 1 and current_ip != ip_history[-1]:
                previous_ip = ip_history[-1]
                loc_current = self._get_ip_location(current_ip)
                loc_previous = self._get_ip_location(previous_ip)

                if loc_current is not None and loc_previous is not None:
                    distance_km = self._calculate_distance_km(
                        loc_previous[0],
                        loc_previous[1],
                        loc_current[0],
                        loc_current[1],
                    )

                    # Estimate time between requests.
                    # Use session.last_activity_at as the timestamp of the previous IP,
                    # and current time as the timestamp of the current request.
                    time_diff_hours = (time.time() - session.last_activity_at) / 3600.0

                    # Guard against zero/negative time differences
                    if time_diff_hours <= 0:
                        time_diff_hours = 0.01  # ~36 seconds minimum

                    # Flag if distance > 500 km in less than 1 hour
                    if distance_km > 500 and time_diff_hours < 1.0:
                        return True, f"Impossible travel detected: {distance_km:.0f}km in {time_diff_hours * 60:.0f}min"
        except Exception:
            # If anything goes wrong with GeoIP lookup or distance calculation,
            # just skip the geographic check rather than breaking session validation.
            logger.debug("Geographic anomaly check skipped due to error", exc_info=True)

        return False, None

    def check_request_rate(
        self,
        request_timestamps: list[float],
    ) -> tuple[bool, str | None]:
        """
        Check for abnormal request rate.
        التحقق من معدل الطلبات غير الطبيعي.

        Args:
            request_timestamps: Recent request timestamps

        Returns:
            Tuple of (is_suspicious, reason)
        """
        now = time.time()
        recent = [ts for ts in request_timestamps if now - ts < self.rapid_request_window]

        if len(recent) > self.max_rapid_requests:
            return True, f"Rapid requests: {len(recent)} in {self.rapid_request_window}s"

        return False, None


# ─────────────────────────────────────────────────────────────────────────────
# Global Instance
# ─────────────────────────────────────────────────────────────────────────────

_session_manager: SessionManager | None = None


async def get_session_manager() -> SessionManager:
    """
    Get global session manager.
    الحصول على مدير الجلسات العام.

    Returns:
        SessionManager instance
    """
    global _session_manager

    if _session_manager is None:
        _session_manager = SessionManager()
        await _session_manager.initialize()

    return _session_manager


def generate_session_id() -> str:
    """
    Generate a secure session ID.
    إنشاء معرف جلسة آمن.

    Returns:
        UUID4 string
    """
    return str(uuid.uuid4())
