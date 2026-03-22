"""
Bug-hunting tests for SAHOOL Authentication Flow.

Tests target:
- shared/auth/jwt_handler.py: create_access_token, create_refresh_token, verify_token
- shared/security/jwt.py: create_token, verify_token (alternate module)
- Token creation -> verification roundtrip
- Expired token rejection
- Tampered payload rejection
- Refresh token misuse as access token
- Issuer/audience mismatch detection
- Concurrent token verification thread safety

Run:
    ENVIRONMENT=test PYTHONPATH=. pytest tests/unit/auth/test_auth_flow_bugs.py -v --timeout=30
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import jwt as pyjwt
import pytest

# Set test env vars BEFORE importing auth modules (they read env at import time)
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from shared.auth.jwt_handler import (  # noqa: E402
    create_access_token,
    create_refresh_token,
    create_token_pair,
    refresh_access_token,
    verify_token,
)
from shared.auth.models import AuthErrors, AuthException, TokenPayload  # noqa: E402

# Also test the shared/security/jwt.py module
from shared.security.jwt import AuthError  # noqa: E402
from shared.security.jwt import JWT_SECRET_KEY as SECURITY_JWT_SECRET  # noqa: E402
from shared.security.jwt import create_access_token as sec_create_access_token  # noqa: E402
from shared.security.jwt import create_refresh_token as sec_create_refresh_token  # noqa: E402
from shared.security.jwt import create_token as sec_create_token  # noqa: E402
from shared.security.jwt import create_token_pair as sec_create_token_pair  # noqa: E402
from shared.security.jwt import verify_token as sec_verify_token  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# 1. Token Creation -> Verification Roundtrip (shared/auth/jwt_handler.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestAuthHandlerRoundtrip:
    """BUG HUNT: Verify that tokens created by jwt_handler can be verified."""

    def test_access_token_roundtrip(self):
        """Create access token -> verify -> get back same user_id and roles."""
        token = create_access_token(
            user_id="user-123",
            roles=["farmer", "admin"],
            tenant_id="tenant-abc",
            permissions=["farm:read", "farm:write"],
        )
        payload = verify_token(token)
        assert isinstance(payload, TokenPayload)
        assert payload.user_id == "user-123"
        assert payload.roles == ["farmer", "admin"]
        assert payload.token_type == "access"
        assert payload.permissions == ["farm:read", "farm:write"]

    def test_refresh_token_roundtrip(self):
        """Create refresh token -> verify -> get back same user_id."""
        token = create_refresh_token(user_id="user-456", tenant_id="tenant-xyz")
        payload = verify_token(token)
        assert payload.user_id == "user-456"
        assert payload.token_type == "refresh"

    def test_token_pair_both_valid(self):
        """create_token_pair -> both tokens must be verifiable."""
        pair = create_token_pair(
            user_id="user-789",
            roles=["farmer"],
            tenant_id="tenant-123",
            permissions=["farm:read"],
        )
        assert "access_token" in pair
        assert "refresh_token" in pair
        assert pair["token_type"] == "bearer"
        assert pair["expires_in"] > 0

        access_payload = verify_token(pair["access_token"])
        assert access_payload.user_id == "user-789"
        assert access_payload.token_type == "access"

        refresh_payload = verify_token(pair["refresh_token"])
        assert refresh_payload.user_id == "user-789"
        assert refresh_payload.token_type == "refresh"

    def test_tenant_id_roundtrip(self):
        """BUG HUNT: tenant_id stored as 'tid' must be extracted correctly."""
        token = create_access_token(
            user_id="user-001",
            roles=["farmer"],
            tenant_id="tenant-special-id",
        )
        payload = verify_token(token)
        # verify_token extracts from payload.get("tenant_id") or payload.get("tid")
        assert payload.tenant_id == "tenant-special-id"

    def test_jti_is_present_and_unique(self):
        """Each token must have a unique JTI for revocation support."""
        t1 = create_access_token(user_id="u1", roles=["farmer"])
        t2 = create_access_token(user_id="u1", roles=["farmer"])
        p1 = verify_token(t1)
        p2 = verify_token(t2)
        assert p1.jti is not None
        assert p2.jti is not None
        assert p1.jti != p2.jti, "Two tokens got the same JTI"

    def test_extra_claims_preserved(self):
        """Extra claims passed to create_access_token should be in the token."""
        token = create_access_token(
            user_id="u1",
            roles=["farmer"],
            extra_claims={"custom_field": "custom_value"},
        )
        # Decode without full verification to check custom fields
        from shared.auth.jwt_handler import decode_token_unsafe

        payload = decode_token_unsafe(token)
        assert payload.get("custom_field") == "custom_value"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Expired Token Rejection
# ─────────────────────────────────────────────────────────────────────────────


class TestExpiredTokenRejection:
    """BUG HUNT: Expired tokens MUST be rejected, not just flagged."""

    def test_expired_access_token_rejected(self):
        """A token with negative expiry delta must be rejected."""
        token = create_access_token(
            user_id="user-expired",
            roles=["farmer"],
            expires_delta=timedelta(seconds=-10),  # Already expired
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "expired_token"

    def test_very_short_lived_token_expires(self):
        """A token with 1-second expiry should expire after waiting."""
        token = create_access_token(
            user_id="user-short",
            roles=["farmer"],
            expires_delta=timedelta(seconds=1),
        )
        # Should be valid immediately
        payload = verify_token(token)
        assert payload.user_id == "user-short"

        # Wait for it to expire
        time.sleep(2)
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "expired_token"

    def test_expired_token_error_message_bilingual(self):
        """BUG HUNT: Expired token error must have both Arabic and English messages."""
        token = create_access_token(
            user_id="user-exp",
            roles=[],
            expires_delta=timedelta(seconds=-10),
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        error = exc_info.value.error
        assert error.en, "Missing English error message"
        assert error.ar, "Missing Arabic error message"
        assert error.code, "Missing error code"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Tampered Payload Rejection
# ─────────────────────────────────────────────────────────────────────────────


class TestTamperedPayloadRejection:
    """BUG HUNT: Tokens with tampered payloads must be rejected."""

    def test_tampered_user_id_rejected(self):
        """Modifying the payload after signing must cause verification failure."""
        token = create_access_token(user_id="user-original", roles=["farmer"])

        # Tamper: decode, modify, re-encode with wrong signature
        parts = token.split(".")
        assert len(parts) == 3

        import base64
        import json

        # Decode payload
        payload_b64 = parts[1]
        # Add padding if needed
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes)

        # Tamper with user_id
        payload["sub"] = "user-hacker"
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b"=").decode()

        # Reconstruct token with tampered payload but original signature
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        with pytest.raises(AuthException):
            verify_token(tampered_token)

    def test_empty_token_rejected(self):
        """Empty string token must be rejected."""
        with pytest.raises(AuthException):
            verify_token("")

    def test_garbage_token_rejected(self):
        """Random garbage string must be rejected."""
        with pytest.raises(AuthException):
            verify_token("not.a.valid.jwt.token")

    def test_none_algorithm_rejected(self):
        """BUG HUNT: 'none' algorithm attack must be blocked."""
        # Create a token with 'none' algorithm
        payload = {
            "sub": "attacker",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "sahool-platform",
            "aud": "sahool-api",
            "type": "access",
        }
        # PyJWT won't encode with alg=none by default, so we construct manually
        import base64
        import json

        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "none", "typ": "JWT"}).encode()
        ).rstrip(b"=").decode()
        body = base64.urlsafe_b64encode(
            json.dumps(payload, default=str).encode()
        ).rstrip(b"=").decode()
        none_token = f"{header}.{body}."

        with pytest.raises(AuthException):
            verify_token(none_token)

    def test_rs256_algorithm_confusion_rejected(self):
        """BUG HUNT: Algorithm confusion attack (RS256 with HMAC secret) must be blocked."""
        from shared.auth.config import config

        payload = {
            "sub": "attacker",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
            "type": "access",
        }
        # Try to sign with RS256 using the HS256 secret as key
        # This should fail at verification because RS256 is not in ALLOWED_ALGORITHMS
        try:
            # This will fail if PyJWT rejects RS256 with a symmetric key at encode time
            evil_token = pyjwt.encode(payload, config.get_signing_key(), algorithm="RS256")
            with pytest.raises(AuthException):
                verify_token(evil_token)
        except Exception:
            # PyJWT may refuse to encode RS256 with a string key, which is fine
            pass


# ─────────────────────────────────────────────────────────────────────────────
# 4. Refresh Token Cannot Be Used As Access Token
# ─────────────────────────────────────────────────────────────────────────────


class TestRefreshTokenMisuse:
    """BUG HUNT: Refresh tokens should not be usable as access tokens."""

    def test_refresh_token_type_is_refresh(self):
        """Verify refresh tokens have type='refresh'."""
        token = create_refresh_token(user_id="u1")
        payload = verify_token(token)
        assert payload.token_type == "refresh"

    def test_access_token_type_is_access(self):
        """Verify access tokens have type='access'."""
        token = create_access_token(user_id="u1", roles=["farmer"])
        payload = verify_token(token)
        assert payload.token_type == "access"

    def test_refresh_access_token_rejects_access_token(self):
        """BUG HUNT: refresh_access_token() must reject an access token as input."""
        access_token = create_access_token(user_id="u1", roles=["farmer"])

        with pytest.raises(AuthException):
            refresh_access_token(access_token, roles=["farmer"])

    def test_refresh_access_token_accepts_refresh_token(self):
        """refresh_access_token() with a valid refresh token should succeed."""
        refresh_tok = create_refresh_token(user_id="u1", tenant_id="t1")
        new_access = refresh_access_token(refresh_tok, roles=["farmer"])
        payload = verify_token(new_access)
        assert payload.user_id == "u1"
        assert payload.token_type == "access"
        assert payload.roles == ["farmer"]

    def test_refresh_token_has_no_roles(self):
        """BUG HUNT: Refresh tokens should not carry roles (minimal claims)."""
        token = create_refresh_token(user_id="u1")
        payload = verify_token(token)
        # Refresh tokens in jwt_handler.py don't include roles at all
        # verify_token defaults missing roles to []
        assert payload.roles == []


# ─────────────────────────────────────────────────────────────────────────────
# 5. Issuer/Audience Mismatch
# ─────────────────────────────────────────────────────────────────────────────


class TestIssuerAudienceMismatch:
    """BUG HUNT: Tokens with wrong issuer or audience must be rejected."""

    def test_wrong_issuer_rejected(self):
        """Token signed with wrong issuer must be rejected."""
        from shared.auth.config import config

        payload = {
            "sub": "user-1",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "wrong-issuer",  # Wrong issuer
            "aud": config.JWT_AUDIENCE,
            "type": "access",
        }
        token = pyjwt.encode(payload, config.get_signing_key(), algorithm="HS256")
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_issuer"

    def test_wrong_audience_rejected(self):
        """Token signed with wrong audience must be rejected."""
        from shared.auth.config import config

        payload = {
            "sub": "user-1",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": "wrong-audience",  # Wrong audience
            "type": "access",
        }
        token = pyjwt.encode(payload, config.get_signing_key(), algorithm="HS256")
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_audience"

    def test_missing_issuer_rejected(self):
        """Token without issuer claim must be rejected."""
        from shared.auth.config import config

        payload = {
            "sub": "user-1",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            # No 'iss' claim
            "aud": config.JWT_AUDIENCE,
            "type": "access",
        }
        token = pyjwt.encode(payload, config.get_signing_key(), algorithm="HS256")
        with pytest.raises(AuthException):
            verify_token(token)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Concurrent Token Verification Thread Safety
# ─────────────────────────────────────────────────────────────────────────────


class TestConcurrentTokenVerification:
    """BUG HUNT: Token verification must be thread-safe."""

    def test_concurrent_verification_no_errors(self):
        """Multiple threads verifying different tokens simultaneously."""
        tokens = [
            create_access_token(user_id=f"user-{i}", roles=["farmer"])
            for i in range(20)
        ]

        results = []
        errors = []

        def verify_one(token, expected_user):
            try:
                payload = verify_token(token)
                return (payload.user_id, expected_user, True)
            except Exception as e:
                return (str(e), expected_user, False)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(verify_one, tok, f"user-{i}"): i
                for i, tok in enumerate(tokens)
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if not result[2]:
                    errors.append(result)

        assert len(errors) == 0, f"Concurrent verification errors: {errors}"
        # Each result should have matching user_id
        for actual_uid, expected_uid, success in results:
            assert actual_uid == expected_uid, (
                f"Thread safety bug: expected {expected_uid}, got {actual_uid}"
            )

    def test_concurrent_creation_unique_jti(self):
        """Multiple tokens created concurrently must have unique JTIs."""
        tokens = []

        def create_one(i):
            return create_access_token(user_id=f"user-{i}", roles=["farmer"])

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_one, i) for i in range(50)]
            for f in as_completed(futures):
                tokens.append(f.result())

        jtis = set()
        for tok in tokens:
            payload = verify_token(tok)
            assert payload.jti not in jtis, f"Duplicate JTI found: {payload.jti}"
            jtis.add(payload.jti)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Security Module (shared/security/jwt.py) Roundtrip
# ─────────────────────────────────────────────────────────────────────────────


class TestSecurityJwtModule:
    """BUG HUNT: Test the alternate JWT module at shared/security/jwt.py."""

    @pytest.fixture(autouse=True)
    def skip_if_no_secret(self):
        """Skip tests if JWT_SECRET_KEY is not configured."""
        if not SECURITY_JWT_SECRET:
            pytest.skip("JWT_SECRET_KEY not configured for security module")

    def test_create_and_verify_roundtrip(self):
        """create_token -> verify_token roundtrip."""
        token = sec_create_token(
            user_id="sec-user-1",
            tenant_id="sec-tenant-1",
            roles=["farmer"],
            scopes=["farm:read"],
        )
        payload = sec_verify_token(token, check_revocation=False)
        assert payload["sub"] == "sec-user-1"
        assert payload["tid"] == "sec-tenant-1"
        assert payload["roles"] == ["farmer"]

    def test_expired_token_rejected(self):
        """Expired token must raise AuthError."""
        token = sec_create_token(
            user_id="sec-user-exp",
            tenant_id="sec-tenant-1",
            roles=[],
            scopes=[],
            expires_delta=timedelta(seconds=-10),
        )
        with pytest.raises(AuthError) as exc_info:
            sec_verify_token(token, check_revocation=False, leeway=0)
        assert exc_info.value.code == "token_expired"

    def test_wrong_issuer_rejected(self):
        """Token with wrong issuer must be rejected."""
        from shared.security.jwt import JWT_AUDIENCE

        secret = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
        payload = {
            "sub": "user-1",
            "tid": "tenant-1",
            "roles": [],
            "scopes": [],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "evil-issuer",
            "aud": JWT_AUDIENCE,
            "type": "access",
        }
        token = pyjwt.encode(payload, secret, algorithm="HS256")
        with pytest.raises(AuthError) as exc_info:
            sec_verify_token(token, check_revocation=False)
        assert exc_info.value.code == "invalid_issuer"

    def test_missing_tenant_id_rejected(self):
        """BUG HUNT: shared/security/jwt.py requires 'tid' claim. Missing it must fail."""
        from shared.security.jwt import JWT_AUDIENCE, JWT_ISSUER

        secret = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
        payload = {
            "sub": "user-1",
            # No 'tid' claim!
            "roles": [],
            "scopes": [],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
            "type": "access",
        }
        token = pyjwt.encode(payload, secret, algorithm="HS256")
        with pytest.raises(AuthError):
            sec_verify_token(token, check_revocation=False)

    def test_access_vs_refresh_token_types(self):
        """Security module must set correct type for access vs refresh tokens."""
        access = sec_create_access_token("u1", "t1", ["farmer"], ["read"])
        refresh = sec_create_refresh_token("u1", "t1")

        ap = sec_verify_token(access, check_revocation=False)
        rp = sec_verify_token(refresh, check_revocation=False)

        assert ap["type"] == "access"
        assert rp["type"] == "refresh"

    def test_none_algorithm_attack_blocked(self):
        """BUG HUNT: 'none' algorithm tokens must be blocked."""
        import base64
        import json

        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "none", "typ": "JWT"}).encode()
        ).rstrip(b"=").decode()
        body = base64.urlsafe_b64encode(
            json.dumps({
                "sub": "attacker",
                "tid": "t1",
                "exp": (datetime.now(UTC) + timedelta(hours=1)).timestamp(),
                "iat": datetime.now(UTC).timestamp(),
            }, default=str).encode()
        ).rstrip(b"=").decode()
        none_token = f"{header}.{body}."

        with pytest.raises(AuthError):
            sec_verify_token(none_token, check_revocation=False)

    def test_token_pair_consistency(self):
        """create_token_pair must return both tokens with matching user/tenant."""
        pair = sec_create_token_pair("u1", "t1", ["farmer"], ["read"])
        assert "access_token" in pair
        assert "refresh_token" in pair

        ap = sec_verify_token(pair["access_token"], check_revocation=False)
        rp = sec_verify_token(pair["refresh_token"], check_revocation=False)

        assert ap["sub"] == rp["sub"] == "u1"
        assert ap["tid"] == rp["tid"] == "t1"
