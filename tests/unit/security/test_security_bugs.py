"""
Security Bug-Hunting Tests for SAHOOL Platform
================================================
These tests are designed to FIND BUGS in security-critical code paths.
Each test targets a specific vulnerability class or edge case.

Run with:
    ENVIRONMENT=test JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars \
    PYTHONPATH=. pytest tests/unit/security/test_security_bugs.py -v --timeout=30
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Setup: Configure environment before importing SAHOOL modules
# ─────────────────────────────────────────────────────────────────────────────
import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")

from shared.auth.config import JWTConfig, config
from shared.auth.dependencies import RateLimiter, enforce_tenant
from shared.auth.jwt_handler import (
    ALLOWED_ALGORITHMS,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    refresh_access_token,
    verify_token,
)
from shared.auth.models import AuthErrors, AuthException, TokenPayload, User

SECRET_KEY = os.environ["JWT_SECRET_KEY"]


# =============================================================================
# 1. JWT Expired Tokens Must Be Rejected
# =============================================================================


class TestExpiredTokenRejection:
    """BUG TARGET: Expired tokens being accepted due to clock skew or missing validation."""

    def test_expired_token_is_rejected(self):
        """Bug: If verify_token does not check exp claim, expired tokens pass through."""
        token = create_access_token(
            user_id="user-001",
            roles=["farmer"],
            expires_delta=timedelta(seconds=-10),  # Already expired
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "expired_token"

    def test_token_expired_by_one_second(self):
        """Bug: Off-by-one in expiration check - token expired exactly 1 second ago."""
        now = datetime.now(UTC)
        payload = {
            "sub": "user-001",
            "roles": ["farmer"],
            "exp": now - timedelta(seconds=1),
            "iat": now - timedelta(minutes=30),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
            "jti": str(uuid.uuid4()),
            "type": "access",
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "expired_token"

    def test_token_with_zero_expiry(self):
        """Bug: Token with exp=0 (epoch start) should be rejected as expired."""
        payload = {
            "sub": "user-001",
            "roles": ["farmer"],
            "exp": 0,
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
            "jti": str(uuid.uuid4()),
            "type": "access",
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(AuthException):
            verify_token(token)


# =============================================================================
# 2. JWT Algorithm Confusion Attack
# =============================================================================


class TestAlgorithmConfusion:
    """BUG TARGET: Algorithm confusion allowing RS256 signed tokens to pass as HS256."""

    def test_none_algorithm_rejected(self):
        """Bug: 'none' algorithm bypasses signature verification entirely."""
        payload = {
            "sub": "attacker",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        # Create token with 'none' algorithm
        token = jwt.encode(payload, "", algorithm="HS256")
        # Manually tamper header to 'none'
        parts = token.split(".")
        import base64

        header_data = base64.urlsafe_b64decode(parts[0] + "==")
        import json

        header = json.loads(header_data)
        header["alg"] = "none"
        new_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
        tampered_token = f"{new_header}.{parts[1]}."

        with pytest.raises(AuthException) as exc_info:
            verify_token(tampered_token)
        assert exc_info.value.error.code == "invalid_token"

    def test_hs384_algorithm_rejected(self):
        """Bug: HS384 is not in ALLOWED_ALGORITHMS but might slip through."""
        assert "HS384" not in ALLOWED_ALGORITHMS
        payload = {
            "sub": "attacker",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS384")
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_token"

    def test_hs512_algorithm_rejected(self):
        """Bug: HS512 is not in ALLOWED_ALGORITHMS."""
        payload = {
            "sub": "attacker",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS512")
        with pytest.raises(AuthException):
            verify_token(token)

    def test_only_hs256_allowed(self):
        """Verify the ALLOWED_ALGORITHMS whitelist is exactly HS256."""
        assert ALLOWED_ALGORITHMS == ["HS256"]


# =============================================================================
# 3. JWT Missing Required Claims
# =============================================================================


class TestMissingClaims:
    """BUG TARGET: Tokens without required claims being accepted."""

    def test_missing_sub_claim(self):
        """Bug: Token without 'sub' claim should be rejected."""
        payload = {
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(AuthException):
            verify_token(token)

    def test_empty_sub_claim(self):
        """Bug: Token with empty string 'sub' should be rejected."""
        payload = {
            "sub": "",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_token"

    def test_missing_exp_claim(self):
        """Bug: Token without 'exp' should be rejected - prevents never-expiring tokens."""
        payload = {
            "sub": "user-001",
            "roles": ["farmer"],
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm="HS256",
        )
        with pytest.raises(AuthException):
            verify_token(token)

    def test_missing_iat_claim(self):
        """Bug: Token without 'iat' should be rejected per SAHOOL policy."""
        payload = {
            "sub": "user-001",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(AuthException):
            verify_token(token)

    def test_missing_roles_returns_empty_list(self):
        """Bug: Token without roles should default to empty list, not None."""
        payload = {
            "sub": "user-001",
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        result = verify_token(token)
        assert result.roles == []
        assert isinstance(result.roles, list)

    def test_wrong_issuer_rejected(self):
        """Bug: Token with wrong issuer should be rejected."""
        payload = {
            "sub": "user-001",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "evil-issuer",
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_issuer"

    def test_wrong_audience_rejected(self):
        """Bug: Token with wrong audience should be rejected."""
        payload = {
            "sub": "user-001",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": "evil-audience",
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_audience"


# =============================================================================
# 4. Token Type Confusion
# =============================================================================


class TestTokenTypeConfusion:
    """BUG TARGET: Using refresh token as access token or vice versa."""

    def test_refresh_token_cannot_be_used_for_access(self):
        """Bug: refresh_access_token should reject if the provided token
        is actually an access token, not a refresh token."""
        access_token = create_access_token(
            user_id="user-001",
            roles=["farmer"],
        )
        with pytest.raises(AuthException):
            refresh_access_token(access_token, roles=["farmer"])

    def test_refresh_token_has_type_refresh(self):
        """Bug: Refresh token should have type='refresh'."""
        token = create_refresh_token(user_id="user-001")
        payload = verify_token(token)
        assert payload.token_type == "refresh"

    def test_access_token_has_type_access(self):
        """Bug: Access token should have type='access'."""
        token = create_access_token(user_id="user-001", roles=["farmer"])
        payload = verify_token(token)
        assert payload.token_type == "access"


# =============================================================================
# 5. Tenant Isolation
# =============================================================================


class TestTenantIsolation:
    """BUG TARGET: Cross-tenant data access through enforce_tenant bypass."""

    def test_non_admin_cannot_access_other_tenant(self):
        """Bug: Regular user accessing another tenant's data."""
        user = User(
            id="user-001",
            email="farmer@example.com",
            roles=["farmer"],
            tenant_id="tenant-A",
        )
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user, requested_tenant_id="tenant-B")
        assert exc_info.value.status_code == 403

    def test_admin_can_access_other_tenant(self):
        """Admin users should be able to access any tenant."""
        user = User(
            id="admin-001",
            email="admin@example.com",
            roles=["admin"],
            tenant_id="tenant-A",
        )
        result = enforce_tenant(user, requested_tenant_id="tenant-B")
        assert result == "tenant-B"

    def test_user_without_tenant_raises_error(self):
        """Bug: User with no tenant_id and no requested_tenant_id should fail."""
        user = User(
            id="user-001",
            email="farmer@example.com",
            roles=["farmer"],
            tenant_id=None,
        )
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user)
        assert exc_info.value.status_code == 400

    def test_user_own_tenant_is_returned(self):
        """When no requested_tenant_id, user's own tenant is returned."""
        user = User(
            id="user-001",
            email="farmer@example.com",
            roles=["farmer"],
            tenant_id="tenant-A",
        )
        result = enforce_tenant(user)
        assert result == "tenant-A"

    def test_user_requesting_own_tenant_succeeds(self):
        """User explicitly requesting their own tenant should work."""
        user = User(
            id="user-001",
            email="farmer@example.com",
            roles=["farmer"],
            tenant_id="tenant-A",
        )
        result = enforce_tenant(user, requested_tenant_id="tenant-A")
        assert result == "tenant-A"


# =============================================================================
# 6. SQL Injection in Tenant ID
# =============================================================================


class TestSQLInjectionInTenantId:
    """BUG TARGET: SQL injection through tenant_id in JWT tokens.
    While enforce_tenant itself just returns the string, the tenant_id
    gets passed to database queries. We verify the JWT handler propagates
    tenant_id exactly as received, and test that get_tenant_subject validates."""

    def test_tenant_id_with_sql_injection_in_event_subject(self):
        """Bug: SQL injection patterns in tenant_id used for NATS subjects."""
        from shared.events.subjects import get_tenant_subject

        malicious_tenant_ids = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin'--",
            "1; SELECT * FROM users",
            "' UNION SELECT * FROM secrets --",
        ]
        for tid in malicious_tenant_ids:
            with pytest.raises(ValueError):
                get_tenant_subject(tid, "field", "created")

    def test_tenant_id_with_nats_wildcards(self):
        """Bug: NATS wildcard characters in tenant_id enable subject injection."""
        from shared.events.subjects import get_tenant_subject

        # These should all be rejected due to wildcard/special chars
        malicious_ids = [
            "tenant.*.evil",
            "tenant.>",
            "*.*.>",
        ]
        for tid in malicious_ids:
            with pytest.raises(ValueError):
                get_tenant_subject(tid, "field", "created")

    def test_tenant_id_uuid_validation(self):
        """Bug: Non-UUID tenant_id passes through get_tenant_subject."""
        from shared.events.subjects import get_tenant_subject

        with pytest.raises(ValueError):
            get_tenant_subject("not-a-uuid", "field", "created")

    def test_valid_uuid_tenant_id_passes(self):
        """Valid UUID tenant_id should work."""
        from shared.events.subjects import get_tenant_subject

        tid = str(uuid.uuid4())
        result = get_tenant_subject(tid, "field", "created")
        assert result == f"sahool.tenant.{tid}.field.created"


# =============================================================================
# 7. Rate Limiter
# =============================================================================


class TestRateLimiter:
    """BUG TARGET: Rate limiter not actually blocking after threshold."""

    def test_rate_limiter_blocks_after_threshold(self):
        """Bug: Rate limiter not enforcing limit."""
        limiter = RateLimiter(requests=5, window_seconds=60)
        key = "test-user"

        # First 5 requests should pass
        for i in range(5):
            allowed, remaining = limiter.is_allowed(key)
            assert allowed, f"Request {i+1} should be allowed"

        # 6th request should be blocked
        allowed, remaining = limiter.is_allowed(key)
        assert not allowed, "6th request should be blocked"
        assert remaining == 0

    def test_rate_limiter_tracks_violations(self):
        """Bug: Violation counter not incrementing."""
        limiter = RateLimiter(requests=2, window_seconds=60)
        key = "test-user"

        limiter.is_allowed(key)
        limiter.is_allowed(key)
        limiter.is_allowed(key)  # blocked
        limiter.is_allowed(key)  # blocked again

        assert limiter.get_violation_count(key) == 2

    def test_rate_limiter_different_users_independent(self):
        """Bug: Rate limits leaking between users."""
        limiter = RateLimiter(requests=2, window_seconds=60)

        # Exhaust user-1's quota
        limiter.is_allowed("user-1")
        limiter.is_allowed("user-1")
        allowed, _ = limiter.is_allowed("user-1")
        assert not allowed

        # user-2 should still be allowed
        allowed, _ = limiter.is_allowed("user-2")
        assert allowed

    def test_rate_limiter_reset_violations(self):
        """Bug: Violation reset not working."""
        limiter = RateLimiter(requests=1, window_seconds=60)
        key = "test-user"

        limiter.is_allowed(key)
        limiter.is_allowed(key)  # blocked
        assert limiter.get_violation_count(key) == 1

        limiter.reset_violations(key)
        assert limiter.get_violation_count(key) == 0

    def test_rate_limiter_remaining_count_accuracy(self):
        """Bug: Remaining count off-by-one errors."""
        limiter = RateLimiter(requests=3, window_seconds=60)
        key = "test-user"

        _, remaining = limiter.is_allowed(key)
        assert remaining == 2  # 3 - 1 = 2, but code does remaining - 1

        _, remaining = limiter.is_allowed(key)
        assert remaining == 1

        _, remaining = limiter.is_allowed(key)
        assert remaining == 0


# =============================================================================
# 8. Token Payload Integrity
# =============================================================================


class TestTokenPayloadIntegrity:
    """BUG TARGET: Token data corruption or missing field propagation."""

    def test_tenant_id_round_trips_through_token(self):
        """Bug: tenant_id lost during token creation/verification cycle."""
        tenant_id = str(uuid.uuid4())
        token = create_access_token(
            user_id="user-001",
            roles=["farmer"],
            tenant_id=tenant_id,
        )
        payload = verify_token(token)
        assert payload.tenant_id == tenant_id

    def test_permissions_round_trip_through_token(self):
        """Bug: permissions not preserved in token."""
        permissions = ["farm:read", "farm:write", "field:read"]
        token = create_access_token(
            user_id="user-001",
            roles=["farmer"],
            permissions=permissions,
        )
        payload = verify_token(token)
        assert payload.permissions == permissions

    def test_jti_is_unique_per_token(self):
        """Bug: JTI reuse enables replay attacks."""
        token1 = create_access_token(user_id="user-001", roles=["farmer"])
        token2 = create_access_token(user_id="user-001", roles=["farmer"])
        payload1 = verify_token(token1)
        payload2 = verify_token(token2)
        assert payload1.jti != payload2.jti, "Each token must have a unique JTI"

    def test_token_pair_both_valid(self):
        """Bug: create_token_pair creates invalid tokens."""
        pair = create_token_pair(
            user_id="user-001",
            roles=["farmer"],
            tenant_id="tid-001",
            permissions=["farm:read"],
        )
        assert "access_token" in pair
        assert "refresh_token" in pair
        assert pair["token_type"] == "bearer"

        # Both tokens should verify
        access_payload = verify_token(pair["access_token"])
        assert access_payload.user_id == "user-001"
        assert access_payload.token_type == "access"

        refresh_payload = verify_token(pair["refresh_token"])
        assert refresh_payload.user_id == "user-001"
        assert refresh_payload.token_type == "refresh"

    def test_extra_claims_do_not_overwrite_core_fields(self):
        """BUG FOUND: extra_claims CAN overwrite core JWT fields (sub, iss, exp).

        In jwt_handler.py create_access_token(), the code does:
            payload.update(extra_claims)
        AFTER setting sub, exp, iss. This means extra_claims={'sub': 'attacker'}
        would create a token where sub='attacker', enabling impersonation.

        Similarly, extra_claims={'iss': 'evil'} overwrites the issuer, which
        causes verify_token to reject the token (caught by issuer validation).
        But if the attacker sets iss to the correct issuer value and sub to
        a target user, the token passes verification.

        SEVERITY: CRITICAL - Privilege escalation via extra_claims injection.
        """
        # CRITICAL BUG TEST: extra_claims can overwrite 'sub' to impersonate
        # any user. Since the issuer stays correct, the token passes verification.
        token_impersonate = create_access_token(
            user_id="innocent-user",
            roles=["farmer"],
            extra_claims={"sub": "admin-target-user"},
        )
        payload = verify_token(token_impersonate)
        if payload.user_id == "admin-target-user":
            pytest.fail(
                "BUG CONFIRMED: extra_claims can overwrite 'sub' field, enabling "
                "user impersonation. An attacker who can pass extra_claims to "
                "create_access_token() can create a token for ANY user. "
                "FIX: Filter or reject extra_claims keys that match core JWT fields "
                "(sub, exp, iat, iss, aud, jti, type, roles)."
            )
        # If we get here, sub was NOT overwritten (code is safe for 'sub')
        # But let's also check if 'roles' can be overwritten for privilege escalation
        token_escalate = create_access_token(
            user_id="user-001",
            roles=["farmer"],
            extra_claims={"roles": ["admin", "superuser"]},
        )
        payload_esc = verify_token(token_escalate)
        if "admin" in payload_esc.roles:
            pytest.fail(
                "BUG CONFIRMED: extra_claims can overwrite 'roles' field, enabling "
                "privilege escalation. An attacker can elevate to admin via "
                "extra_claims={'roles': ['admin']}. "
                "FIX: Reject extra_claims keys matching core JWT fields."
            )

    def test_wrong_secret_key_rejected(self):
        """Bug: Token signed with different key being accepted."""
        payload = {
            "sub": "user-001",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        token = jwt.encode(payload, "completely-wrong-secret-key-that-is-32chars!", algorithm="HS256")
        with pytest.raises(AuthException):
            verify_token(token)

    def test_malformed_token_rejected(self):
        """Bug: Malformed JWT strings not properly handled."""
        malformed_tokens = [
            "",
            "not-a-jwt",
            "a.b",
            "a.b.c",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..invalid",
            "null",
            "undefined",
        ]
        for token in malformed_tokens:
            with pytest.raises((AuthException, Exception)):
                verify_token(token)


# =============================================================================
# 9. User Model Permission Checks
# =============================================================================


class TestUserPermissionChecks:
    """BUG TARGET: Permission and role checking logic bugs."""

    def test_has_role_with_empty_roles(self):
        """Bug: has_role crashes or returns True with empty roles list."""
        user = User(id="u1", email="a@b.com", roles=[])
        assert not user.has_role("admin")
        assert not user.has_any_role("admin", "farmer")

    def test_has_any_role_returns_true_for_match(self):
        """Bug: has_any_role returns False even when one role matches."""
        user = User(id="u1", email="a@b.com", roles=["farmer"])
        assert user.has_any_role("admin", "farmer")

    def test_has_all_roles_requires_all(self):
        """Bug: has_all_roles returns True when only some roles match."""
        user = User(id="u1", email="a@b.com", roles=["farmer"])
        assert not user.has_all_roles("farmer", "admin")

    def test_has_farm_access_with_empty_farm_ids(self):
        """Bug: has_farm_access returns True when farm_ids is empty."""
        user = User(id="u1", email="a@b.com", roles=["farmer"], farm_ids=[])
        assert not user.has_farm_access("farm-001")

    def test_has_permission_with_no_permissions(self):
        """Bug: has_permission crashes when permissions list is empty."""
        user = User(id="u1", email="a@b.com", roles=["farmer"], permissions=[])
        assert not user.has_permission("farm:read")
