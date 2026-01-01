"""
SAHOOL Token Revocation Service
خدمة إلغاء التوكنات

Security Features:
- In-memory revocation list (can be upgraded to Redis)
- JTI (JWT ID) based revocation
- User-level revocation (revoke all tokens for a user)
- Tenant-level revocation (revoke all tokens for a tenant)
- Automatic cleanup of expired entries
"""

import time
import logging
import threading
from typing import Optional, Set, Dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


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

    Note: For production with multiple instances, replace with Redis.
    """

    def __init__(self, cleanup_interval: int = 3600):
        # JTI-based revocation: {jti: RevocationEntry}
        self._revoked_tokens: Dict[str, RevocationEntry] = {}

        # User-based revocation: {user_id: revoked_before_timestamp}
        self._revoked_users: Dict[str, float] = {}

        # Tenant-based revocation: {tenant_id: revoked_before_timestamp}
        self._revoked_tenants: Dict[str, float] = {}

        # Lock for thread safety
        self._lock = threading.RLock()

        # Cleanup interval
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()

    def _cleanup_expired(self) -> None:
        """Remove expired revocation entries"""
        now = time.time()

        # Only cleanup periodically
        if now - self._last_cleanup < self._cleanup_interval:
            return

        with self._lock:
            # Cleanup expired token revocations
            expired_tokens = [
                jti
                for jti, entry in self._revoked_tokens.items()
                if entry.expires_at < now
            ]
            for jti in expired_tokens:
                del self._revoked_tokens[jti]

            if expired_tokens:
                logger.info(
                    f"Cleaned up {len(expired_tokens)} expired token revocations"
                )

            self._last_cleanup = now

    # ─────────────────────────────────────────────────────────────────────────
    # Token (JTI) Revocation
    # ─────────────────────────────────────────────────────────────────────────

    def revoke_token(
        self,
        jti: str,
        expires_at: Optional[float] = None,
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

        with self._lock:
            revoked_at = self._revoked_users.get(user_id)
            if revoked_at and token_issued_at < revoked_at:
                return True

        return False

    def clear_user_revocation(self, user_id: str) -> bool:
        """Clear user revocation (e.g., after password change confirmation)"""
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

        with self._lock:
            self._revoked_tenants[tenant_id] = time.time()

        logger.warning(f"All tokens revoked for tenant: {tenant_id}, reason={reason}")
        return True

    def is_tenant_token_revoked(self, tenant_id: str, token_issued_at: float) -> bool:
        """Check if a tenant's token is revoked"""
        if not tenant_id:
            return False

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
        jti: Optional[str] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        issued_at: Optional[float] = None,
    ) -> tuple[bool, Optional[str]]:
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
        if (
            tenant_id
            and issued_at
            and self.is_tenant_token_revoked(tenant_id, issued_at)
        ):
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
_revocation_service: Optional[TokenRevocationService] = None


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
    jti: Optional[str] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    issued_at: Optional[float] = None,
) -> tuple[bool, Optional[str]]:
    """Check if a token is revoked"""
    return get_revocation_service().is_revoked(jti, user_id, tenant_id, issued_at)
