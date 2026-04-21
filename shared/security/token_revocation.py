"""
SAHOOL Token Revocation Service
خدمة إلغاء التوكنات

Security Features:
- Redis-backed revocation for multi-instance deployments
- In-memory fallback when Redis is unavailable
- JTI (JWT ID) based revocation
- User-level revocation (revoke all tokens for a user)
- Tenant-level revocation (revoke all tokens for a tenant)
- Automatic cleanup of expired entries
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Redis Backend (distributed revocation)
# ─────────────────────────────────────────────────────────────────────────────

_REDIS_PREFIX = "sahool:revocation:"

# TTL for user/tenant revocation keys in Redis.
# Must be >= max token lifetime so that a revocation entry outlives every
# token that could have been issued before the revocation was recorded.
# Aligned with the maximum refresh token lifetime (see MAX_REFRESH_TOKEN_DAYS
# configuration, typically defined in shared/auth/config.py).
_MAX_REFRESH_TOKEN_DAYS = int(os.getenv("MAX_REFRESH_TOKEN_DAYS", "30"))
_REVOCATION_TTL = _MAX_REFRESH_TOKEN_DAYS * 24 * 3600  # seconds


class RedisRevocationBackend:
    """
    Redis-backed token revocation for multi-instance deployments.

    Keys:
    - sahool:revocation:jti:{jti}         → reason  (TTL = token expiry)
    - sahool:revocation:user:{user_id}    → revoked_at timestamp
    - sahool:revocation:tenant:{tenant_id} → revoked_at timestamp
    """

    def __init__(self, redis_url: str | None = None):
        self._redis: object | None = None
        self._available = False
        redis_url = redis_url or os.getenv("REDIS_URL", "")
        if redis_url:
            try:
                import redis as redis_lib

                self._redis = redis_lib.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=3,
                    socket_timeout=2,
                )
                self._redis.ping()  # type: ignore[union-attr]
                self._available = True
                logger.info("Redis revocation backend connected to %s", redis_url.split("@")[-1])
            except ImportError:
                logger.warning(
                    "Redis package not installed — token revocation will use "
                    "in-memory backend only. Install with: pip install redis"
                )
                self._redis = None
                self._available = False
            except Exception as exc:
                logger.warning(
                    "Redis revocation backend unavailable (url=%s), falling back to in-memory: %s",
                    redis_url.split("@")[-1],
                    exc,
                )
                self._redis = None
                self._available = False

    @property
    def available(self) -> bool:
        return self._available

    # -- JTI ----------------------------------------------------------------

    def revoke_token(self, jti: str, expires_at: float, reason: str) -> bool:
        try:
            ttl = max(int(expires_at - time.time()), 1)
            self._redis.setex(f"{_REDIS_PREFIX}jti:{jti}", ttl, reason)  # type: ignore[union-attr]
            return True
        except Exception as exc:
            logger.warning(
                "Redis revoke_token failed: %s", exc
            )  # nosemgrep: python-logger-credential-disclosure -- logs operational Redis error, no credentials
            return False

    def is_token_revoked(self, jti: str) -> bool:
        try:
            return self._redis.exists(f"{_REDIS_PREFIX}jti:{jti}") > 0  # type: ignore[union-attr]
        except Exception as exc:
            # Fail-closed: if Redis was available but now errors, treat token
            # as revoked to prevent accepting tokens revoked by other instances.
            logger.warning(
                "Redis is_token_revoked read error (fail-closed): %s", exc
            )  # nosemgrep: python-logger-credential-disclosure -- logs operational Redis error, no credentials
            return True

    # -- User ---------------------------------------------------------------

    def revoke_user_tokens(self, user_id: str) -> bool:
        try:
            # setex with TTL to prevent unbounded key growth; TTL covers the
            # maximum possible token lifetime (30 days = max refresh token).
            self._redis.setex(  # type: ignore[union-attr]
                f"{_REDIS_PREFIX}user:{user_id}",
                _REVOCATION_TTL,
                str(time.time()),
            )
            return True
        except Exception as exc:
            logger.warning(
                "Redis revoke_user_tokens failed: %s", exc
            )  # nosemgrep: python-logger-credential-disclosure -- logs operational Redis error, no credentials
            return False

    def is_user_token_revoked(self, user_id: str, token_issued_at: float) -> bool:
        try:
            val = self._redis.get(f"{_REDIS_PREFIX}user:{user_id}")  # type: ignore[union-attr]
            if val is not None and token_issued_at < float(val):
                return True
            return False
        except Exception as exc:
            # Fail-closed: treat as revoked when Redis read fails to prevent
            # accepting tokens that were revoked on another instance.
            logger.warning(
                "Redis is_user_token_revoked read error (fail-closed): %s", exc
            )  # nosemgrep: python-logger-credential-disclosure -- logs operational Redis error, no credentials
            return True

    def clear_user_revocation(self, user_id: str) -> bool:
        try:
            self._redis.delete(f"{_REDIS_PREFIX}user:{user_id}")  # type: ignore[union-attr]
            return True
        except Exception as exc:
            logger.warning(
                "Redis clear_user_revocation failed: %s", exc
            )  # nosemgrep: python-logger-credential-disclosure -- logs operational Redis error, no credentials
            return False

    # -- Tenant -------------------------------------------------------------

    def revoke_tenant_tokens(self, tenant_id: str) -> bool:
        try:
            # setex with TTL to prevent unbounded key growth; TTL covers the
            # maximum possible token lifetime (30 days = max refresh token).
            self._redis.setex(  # type: ignore[union-attr]
                f"{_REDIS_PREFIX}tenant:{tenant_id}",
                _REVOCATION_TTL,
                str(time.time()),
            )
            return True
        except Exception as exc:
            logger.warning(
                "Redis revoke_tenant_tokens failed: %s", exc
            )  # nosemgrep: python-logger-credential-disclosure -- logs operational Redis error, no credentials
            return False

    def is_tenant_token_revoked(self, tenant_id: str, token_issued_at: float) -> bool:
        try:
            val = self._redis.get(f"{_REDIS_PREFIX}tenant:{tenant_id}")  # type: ignore[union-attr]
            if val is not None and token_issued_at < float(val):
                return True
            return False
        except Exception as exc:
            # Fail-closed: treat as revoked when Redis read fails to prevent
            # accepting tokens that were revoked on another instance.
            logger.warning(
                "Redis is_tenant_token_revoked read error (fail-closed): %s", exc
            )  # nosemgrep: python-logger-credential-disclosure -- logs operational Redis error, no credentials
            return True


@dataclass
class RevocationEntry:
    """Single revocation entry"""

    revoked_at: float
    expires_at: float
    reason: str = "manual"


class TokenRevocationService:
    """
    Token revocation service with multiple revocation strategies.

    Supports:
    - JTI revocation (single token)
    - User revocation (all tokens for a user)
    - Tenant revocation (all tokens for a tenant)

    Uses Redis backend when REDIS_URL is configured; falls back to in-memory.
    """

    def __init__(
        self,
        cleanup_interval: int = 3600,
        redis_url: str | None = None,
    ):
        # JTI-based revocation: {jti: RevocationEntry}
        self._revoked_tokens: dict[str, RevocationEntry] = {}

        # User-based revocation: {user_id: revoked_before_timestamp}
        self._revoked_users: dict[str, float] = {}

        # Tenant-based revocation: {tenant_id: revoked_before_timestamp}
        self._revoked_tenants: dict[str, float] = {}

        # Lock for thread safety
        self._lock = threading.RLock()

        # Cleanup interval
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()

        # Redis backend (optional, for multi-instance)
        self._redis_backend = RedisRevocationBackend(redis_url)
        if self._redis_backend.available:
            logger.info("Token revocation using Redis backend (distributed)")
        else:
            logger.info("Token revocation using in-memory backend (single-instance)")

    def _cleanup_expired(self) -> None:
        """Remove expired revocation entries"""
        now = time.time()

        # Only cleanup periodically
        if now - self._last_cleanup < self._cleanup_interval:
            return

        with self._lock:
            # Cleanup expired token revocations
            expired_tokens = [jti for jti, entry in self._revoked_tokens.items() if entry.expires_at < now]
            for jti in expired_tokens:
                del self._revoked_tokens[jti]

            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired token revocations")

            self._last_cleanup = now

    # ─────────────────────────────────────────────────────────────────────────
    # Token (JTI) Revocation
    # ─────────────────────────────────────────────────────────────────────────

    def revoke_token(
        self,
        jti: str,
        expires_at: float | None = None,
        reason: str = "manual",
    ) -> bool:
        """
        Revoke a single token by JTI.

        Args:
            jti: JWT ID to revoke
            expires_at: When the token expires (for cleanup)
            reason: Reason for revocation

        Returns:
            True if revoked successfully
        """
        if not jti:
            return False

        # Default expiry: 24 hours from now
        if expires_at is None:
            expires_at = time.time() + 86400

        # RACE-CONDITION FIX: persist to Redis FIRST so other instances
        # see the revocation before the local in-memory dict is updated.
        # The previous order (in-memory first, Redis second) left a window
        # where another instance could accept a just-revoked token.
        if self._redis_backend.available:
            if not self._redis_backend.revoke_token(jti, expires_at, reason):
                logger.error(  # nosemgrep: python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure
                    "Redis revoke_token write failed for jti=%s... — revocation is local-only; "
                    "other instances may still accept this token.",
                    jti[:8] if len(jti) >= 8 else jti,
                )

        with self._lock:
            self._revoked_tokens[jti] = RevocationEntry(
                revoked_at=time.time(),
                expires_at=expires_at,
                reason=reason,
            )

        logger.info(f"Token revoked: jti={jti[:8]}..., reason={reason}")
        self._cleanup_expired()
        return True

    def is_token_revoked(self, jti: str) -> bool:
        """Check if a token is revoked by JTI"""
        if not jti:
            return False

        # Check Redis first (distributed)
        if self._redis_backend.available:
            if self._redis_backend.is_token_revoked(jti):
                return True

        with self._lock:
            entry = self._revoked_tokens.get(jti)
            if entry:
                # Check if still valid (not expired)
                if entry.expires_at > time.time():
                    return True
                # Expired revocation, clean it up
                del self._revoked_tokens[jti]

        return False

    # ─────────────────────────────────────────────────────────────────────────
    # User Revocation
    # ─────────────────────────────────────────────────────────────────────────

    def revoke_user_tokens(self, user_id: str, reason: str = "user_logout") -> bool:
        """
        Revoke all tokens for a user.
        Any token issued before this timestamp will be considered invalid.

        Args:
            user_id: User ID to revoke tokens for
            reason: Reason for revocation

        Returns:
            True if revoked successfully
        """
        if not user_id:
            return False

        # RACE-CONDITION FIX: write Redis first so other instances see the
        # user revocation before the local dict is updated.
        if self._redis_backend.available:
            if not self._redis_backend.revoke_user_tokens(user_id):
                logger.error(  # nosemgrep: python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure
                    "Redis revoke_user_tokens write failed for user=%s — revocation is local-only; "
                    "other instances may still accept tokens for this user.",
                    user_id,
                )

        with self._lock:
            self._revoked_users[user_id] = time.time()

        logger.info(f"All tokens revoked for user: {user_id}, reason={reason}")
        return True

    def is_user_token_revoked(self, user_id: str, token_issued_at: float) -> bool:
        """
        Check if a user's token is revoked.

        Args:
            user_id: User ID
            token_issued_at: When the token was issued (iat claim)

        Returns:
            True if the token was issued before user revocation
        """
        if not user_id:
            return False

        # Check Redis first (distributed)
        if self._redis_backend.available:
            if self._redis_backend.is_user_token_revoked(user_id, token_issued_at):
                return True

        with self._lock:
            revoked_at = self._revoked_users.get(user_id)
            if revoked_at and token_issued_at < revoked_at:
                return True

        return False

    def clear_user_revocation(self, user_id: str) -> bool:
        """Clear user revocation (e.g., after password change confirmation)"""
        if self._redis_backend.available:
            self._redis_backend.clear_user_revocation(user_id)
        with self._lock:
            if user_id in self._revoked_users:
                del self._revoked_users[user_id]
                return True
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Tenant Revocation
    # ─────────────────────────────────────────────────────────────────────────

    def revoke_tenant_tokens(self, tenant_id: str, reason: str = "security") -> bool:
        """
        Revoke all tokens for a tenant.
        Use with caution - affects all users in the tenant.

        Args:
            tenant_id: Tenant ID to revoke tokens for
            reason: Reason for revocation

        Returns:
            True if revoked successfully
        """
        if not tenant_id:
            return False

        # RACE-CONDITION FIX: write Redis first so other instances see the
        # tenant revocation before the local dict is updated.
        if self._redis_backend.available:
            if not self._redis_backend.revoke_tenant_tokens(tenant_id):
                logger.error(  # nosemgrep: python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure
                    "Redis revoke_tenant_tokens write failed for tenant=%s — revocation is local-only; "
                    "other instances may still accept tokens for this tenant.",
                    tenant_id,
                )

        with self._lock:
            self._revoked_tenants[tenant_id] = time.time()

        logger.warning(f"All tokens revoked for tenant: {tenant_id}, reason={reason}")
        return True

    def is_tenant_token_revoked(self, tenant_id: str, token_issued_at: float) -> bool:
        """Check if a tenant's token is revoked"""
        if not tenant_id:
            return False

        # Check Redis first (distributed)
        if self._redis_backend.available:
            if self._redis_backend.is_tenant_token_revoked(tenant_id, token_issued_at):
                return True

        with self._lock:
            revoked_at = self._revoked_tenants.get(tenant_id)
            if revoked_at and token_issued_at < revoked_at:
                return True

        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Combined Check
    # ─────────────────────────────────────────────────────────────────────────

    def is_revoked(
        self,
        jti: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        issued_at: float | None = None,
    ) -> tuple[bool, str | None]:
        """
        Check if a token is revoked by any method.

        Args:
            jti: JWT ID
            user_id: User ID from token
            tenant_id: Tenant ID from token
            issued_at: Token issued at timestamp

        Returns:
            (is_revoked, reason)
        """
        # Check JTI revocation
        if jti and self.is_token_revoked(jti):
            return True, "token_revoked"

        # Check user revocation
        if user_id and issued_at and self.is_user_token_revoked(user_id, issued_at):
            return True, "user_tokens_revoked"

        # Check tenant revocation
        if tenant_id and issued_at and self.is_tenant_token_revoked(tenant_id, issued_at):
            return True, "tenant_tokens_revoked"

        return False, None

    # ─────────────────────────────────────────────────────────────────────────
    # Stats
    # ─────────────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get revocation statistics"""
        with self._lock:
            return {
                "revoked_tokens": len(self._revoked_tokens),
                "revoked_users": len(self._revoked_users),
                "revoked_tenants": len(self._revoked_tenants),
                "last_cleanup": datetime.fromtimestamp(self._last_cleanup).isoformat(),
            }


# Global instance
_revocation_service: TokenRevocationService | None = None


def get_revocation_service() -> TokenRevocationService:
    """Get the global revocation service instance"""
    global _revocation_service
    if _revocation_service is None:
        _revocation_service = TokenRevocationService()
    return _revocation_service


# Convenience functions
def revoke_token(jti: str, reason: str = "manual") -> bool:
    """Revoke a single token"""
    return get_revocation_service().revoke_token(jti, reason=reason)


def revoke_user_tokens(user_id: str, reason: str = "logout") -> bool:
    """Revoke all tokens for a user"""
    return get_revocation_service().revoke_user_tokens(user_id, reason=reason)


def revoke_tenant_tokens(tenant_id: str, reason: str = "security") -> bool:
    """Revoke all tokens for a tenant"""
    return get_revocation_service().revoke_tenant_tokens(tenant_id, reason=reason)


def is_token_revoked(
    jti: str | None = None,
    user_id: str | None = None,
    tenant_id: str | None = None,
    issued_at: float | None = None,
) -> tuple[bool, str | None]:
    """Check if a token is revoked"""
    return get_revocation_service().is_revoked(jti, user_id, tenant_id, issued_at)
