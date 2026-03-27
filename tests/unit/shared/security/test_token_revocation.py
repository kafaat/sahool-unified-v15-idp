"""
Tests for shared/security/token_revocation.py
Token revocation service (JTI, user, tenant level)
"""

import time

import pytest

from shared.security.token_revocation import (
    RevocationEntry,
    TokenRevocationService,
    get_revocation_service,
    is_token_revoked,
    revoke_tenant_tokens,
    revoke_token,
    revoke_user_tokens,
)


# ─────────────────────────────────────────────────────────────────────────────
# RevocationEntry
# ─────────────────────────────────────────────────────────────────────────────


class TestRevocationEntry:
    def test_defaults(self):
        entry = RevocationEntry(revoked_at=1000.0, expires_at=2000.0)
        assert entry.revoked_at == 1000.0
        assert entry.expires_at == 2000.0
        assert entry.reason == "manual"

    def test_custom_reason(self):
        entry = RevocationEntry(revoked_at=1000.0, expires_at=2000.0, reason="password_change")
        assert entry.reason == "password_change"


# ─────────────────────────────────────────────────────────────────────────────
# TokenRevocationService - Token (JTI) Revocation
# ─────────────────────────────────────────────────────────────────────────────


class TestTokenRevocation:
    def test_revoke_token_success(self):
        svc = TokenRevocationService()
        result = svc.revoke_token("jti-123", reason="logout")
        assert result is True
        assert svc.is_token_revoked("jti-123") is True

    def test_revoke_token_empty_jti(self):
        svc = TokenRevocationService()
        result = svc.revoke_token("")
        assert result is False

    def test_is_token_revoked_empty_jti(self):
        svc = TokenRevocationService()
        assert svc.is_token_revoked("") is False

    def test_is_token_revoked_not_revoked(self):
        svc = TokenRevocationService()
        assert svc.is_token_revoked("unknown-jti") is False

    def test_revoke_token_with_custom_expiry(self):
        svc = TokenRevocationService()
        future = time.time() + 3600
        svc.revoke_token("jti-456", expires_at=future)
        assert svc.is_token_revoked("jti-456") is True

    def test_revoke_token_default_expiry(self):
        svc = TokenRevocationService()
        svc.revoke_token("jti-default")
        assert svc.is_token_revoked("jti-default") is True

    def test_expired_revocation_cleaned_on_check(self):
        svc = TokenRevocationService()
        # Revoke with an expiry in the past
        svc.revoke_token("jti-old", expires_at=time.time() - 1)
        # Should not be considered revoked since expiry has passed
        assert svc.is_token_revoked("jti-old") is False
        # Entry should be cleaned up
        assert "jti-old" not in svc._revoked_tokens


# ─────────────────────────────────────────────────────────────────────────────
# TokenRevocationService - User Revocation
# ─────────────────────────────────────────────────────────────────────────────


class TestUserRevocation:
    def test_revoke_user_tokens(self):
        svc = TokenRevocationService()
        result = svc.revoke_user_tokens("user-1", reason="logout")
        assert result is True

    def test_revoke_user_tokens_empty_user(self):
        svc = TokenRevocationService()
        result = svc.revoke_user_tokens("")
        assert result is False

    def test_is_user_token_revoked_old_token(self):
        svc = TokenRevocationService()
        old_iat = time.time() - 100
        svc.revoke_user_tokens("user-1")
        assert svc.is_user_token_revoked("user-1", old_iat) is True

    def test_is_user_token_revoked_new_token(self):
        svc = TokenRevocationService()
        svc.revoke_user_tokens("user-1")
        new_iat = time.time() + 100  # Issued after revocation
        assert svc.is_user_token_revoked("user-1", new_iat) is False

    def test_is_user_token_revoked_empty_user(self):
        svc = TokenRevocationService()
        assert svc.is_user_token_revoked("", 1000.0) is False

    def test_is_user_token_revoked_not_revoked(self):
        svc = TokenRevocationService()
        assert svc.is_user_token_revoked("user-2", time.time()) is False

    def test_clear_user_revocation(self):
        svc = TokenRevocationService()
        svc.revoke_user_tokens("user-1")
        result = svc.clear_user_revocation("user-1")
        assert result is True
        # Should no longer be revoked
        old_iat = time.time() - 100
        assert svc.is_user_token_revoked("user-1", old_iat) is False

    def test_clear_user_revocation_not_found(self):
        svc = TokenRevocationService()
        result = svc.clear_user_revocation("nonexistent")
        assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# TokenRevocationService - Tenant Revocation
# ─────────────────────────────────────────────────────────────────────────────


class TestTenantRevocation:
    def test_revoke_tenant_tokens(self):
        svc = TokenRevocationService()
        result = svc.revoke_tenant_tokens("tenant-1", reason="security")
        assert result is True

    def test_revoke_tenant_tokens_empty(self):
        svc = TokenRevocationService()
        result = svc.revoke_tenant_tokens("")
        assert result is False

    def test_is_tenant_token_revoked_old_token(self):
        svc = TokenRevocationService()
        old_iat = time.time() - 100
        svc.revoke_tenant_tokens("tenant-1")
        assert svc.is_tenant_token_revoked("tenant-1", old_iat) is True

    def test_is_tenant_token_revoked_new_token(self):
        svc = TokenRevocationService()
        svc.revoke_tenant_tokens("tenant-1")
        new_iat = time.time() + 100
        assert svc.is_tenant_token_revoked("tenant-1", new_iat) is False

    def test_is_tenant_token_revoked_empty(self):
        svc = TokenRevocationService()
        assert svc.is_tenant_token_revoked("", 1000.0) is False

    def test_is_tenant_token_revoked_not_revoked(self):
        svc = TokenRevocationService()
        assert svc.is_tenant_token_revoked("tenant-2", time.time()) is False


# ─────────────────────────────────────────────────────────────────────────────
# TokenRevocationService - Combined Check
# ─────────────────────────────────────────────────────────────────────────────


class TestCombinedRevocationCheck:
    def test_token_revoked(self):
        svc = TokenRevocationService()
        svc.revoke_token("jti-1")
        is_rev, reason = svc.is_revoked(jti="jti-1")
        assert is_rev is True
        assert reason == "token_revoked"

    def test_user_revoked(self):
        svc = TokenRevocationService()
        svc.revoke_user_tokens("user-1")
        old_iat = time.time() - 100
        is_rev, reason = svc.is_revoked(user_id="user-1", issued_at=old_iat)
        assert is_rev is True
        assert reason == "user_tokens_revoked"

    def test_tenant_revoked(self):
        svc = TokenRevocationService()
        svc.revoke_tenant_tokens("tenant-1")
        old_iat = time.time() - 100
        is_rev, reason = svc.is_revoked(tenant_id="tenant-1", issued_at=old_iat)
        assert is_rev is True
        assert reason == "tenant_tokens_revoked"

    def test_not_revoked(self):
        svc = TokenRevocationService()
        is_rev, reason = svc.is_revoked(jti="clean-jti", user_id="clean-user", issued_at=time.time())
        assert is_rev is False
        assert reason is None

    def test_all_none_not_revoked(self):
        svc = TokenRevocationService()
        is_rev, reason = svc.is_revoked()
        assert is_rev is False
        assert reason is None

    def test_jti_checked_first(self):
        svc = TokenRevocationService()
        svc.revoke_token("jti-1")
        svc.revoke_user_tokens("user-1")
        old_iat = time.time() - 100
        is_rev, reason = svc.is_revoked(jti="jti-1", user_id="user-1", issued_at=old_iat)
        assert is_rev is True
        assert reason == "token_revoked"


# ─────────────────────────────────────────────────────────────────────────────
# TokenRevocationService - Stats
# ─────────────────────────────────────────────────────────────────────────────


class TestStats:
    def test_empty_stats(self):
        svc = TokenRevocationService()
        stats = svc.get_stats()
        assert stats["revoked_tokens"] == 0
        assert stats["revoked_users"] == 0
        assert stats["revoked_tenants"] == 0
        assert "last_cleanup" in stats

    def test_stats_after_revocations(self):
        svc = TokenRevocationService()
        svc.revoke_token("jti-1")
        svc.revoke_token("jti-2")
        svc.revoke_user_tokens("user-1")
        svc.revoke_tenant_tokens("tenant-1")

        stats = svc.get_stats()
        assert stats["revoked_tokens"] == 2
        assert stats["revoked_users"] == 1
        assert stats["revoked_tenants"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# TokenRevocationService - Cleanup
# ─────────────────────────────────────────────────────────────────────────────


class TestCleanup:
    def test_cleanup_removes_expired_entries(self):
        svc = TokenRevocationService(cleanup_interval=0)  # Cleanup every call
        # Add expired entry
        svc._revoked_tokens["old-jti"] = RevocationEntry(
            revoked_at=time.time() - 200,
            expires_at=time.time() - 100,
        )
        # Add valid entry
        svc._revoked_tokens["new-jti"] = RevocationEntry(
            revoked_at=time.time(),
            expires_at=time.time() + 3600,
        )
        # Force last_cleanup to be old enough to trigger cleanup
        svc._last_cleanup = 0

        svc._cleanup_expired()
        assert "old-jti" not in svc._revoked_tokens
        assert "new-jti" in svc._revoked_tokens

    def test_cleanup_skipped_if_recent(self):
        svc = TokenRevocationService(cleanup_interval=3600)
        svc._revoked_tokens["old-jti"] = RevocationEntry(
            revoked_at=time.time() - 200,
            expires_at=time.time() - 100,
        )
        # last_cleanup was just set, so cleanup should be skipped
        svc._cleanup_expired()
        assert "old-jti" in svc._revoked_tokens  # Not cleaned up


# ─────────────────────────────────────────────────────────────────────────────
# Global instance and convenience functions
# ─────────────────────────────────────────────────────────────────────────────


class TestGlobalInstance:
    def setup_method(self):
        import shared.security.token_revocation as tr_mod
        tr_mod._revocation_service = None

    def teardown_method(self):
        import shared.security.token_revocation as tr_mod
        tr_mod._revocation_service = None

    def test_get_revocation_service_singleton(self):
        svc1 = get_revocation_service()
        svc2 = get_revocation_service()
        assert svc1 is svc2

    def test_revoke_token_convenience(self):
        result = revoke_token("jti-conv", reason="test")
        assert result is True

    def test_revoke_user_tokens_convenience(self):
        result = revoke_user_tokens("user-conv", reason="test")
        assert result is True

    def test_revoke_tenant_tokens_convenience(self):
        result = revoke_tenant_tokens("tenant-conv", reason="test")
        assert result is True

    def test_is_token_revoked_convenience(self):
        revoke_token("jti-check")
        is_rev, reason = is_token_revoked(jti="jti-check")
        assert is_rev is True
        assert reason == "token_revoked"

    def test_is_token_revoked_not_found(self):
        is_rev, reason = is_token_revoked(jti="clean-jti")
        assert is_rev is False
        assert reason is None
