"""
Extended unit tests for shared/auth/jwt_handler.py
Covers extra_claims protection, decode_token alias, _get_debug_decode_options,
token with wrong issuer/audience, and edge cases.
"""

import os
from datetime import UTC, datetime, timedelta

import jwt
import pytest

os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"

from shared.auth.jwt_handler import (
    ALLOWED_ALGORITHMS,
    _get_debug_decode_options,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    decode_token_unsafe,
    refresh_access_token,
    verify_token,
)
from shared.auth.models import AuthErrors, AuthException


class TestExtraClaimsSecurity:
    """Test that extra_claims cannot overwrite protected fields."""

    def test_extra_claims_cannot_overwrite_sub(self):
        """extra_claims cannot overwrite the 'sub' (user_id) claim."""
        token = create_access_token(
            user_id="real_user",
            roles=["farmer"],
            extra_claims={"sub": "attacker"},
        )
        payload = verify_token(token)
        assert payload.user_id == "real_user"

    def test_extra_claims_cannot_overwrite_roles(self):
        """extra_claims cannot overwrite the 'roles' claim."""
        token = create_access_token(
            user_id="user1",
            roles=["farmer"],
            extra_claims={"roles": ["admin", "superadmin"]},
        )
        payload = verify_token(token)
        assert payload.roles == ["farmer"]

    def test_extra_claims_cannot_overwrite_exp(self):
        """extra_claims cannot overwrite the 'exp' claim."""
        far_future = datetime.now(UTC) + timedelta(days=365)
        token = create_access_token(
            user_id="user1",
            roles=["farmer"],
            extra_claims={"exp": far_future.timestamp()},
        )
        payload = verify_token(token)
        # exp should be ~30 minutes from now, not 365 days
        assert payload.exp < datetime.now(UTC) + timedelta(hours=2)

    def test_extra_claims_cannot_overwrite_jti(self):
        """extra_claims cannot overwrite the 'jti' claim."""
        token = create_access_token(
            user_id="user1",
            roles=["farmer"],
            extra_claims={"jti": "attacker-controlled-jti"},
        )
        payload = verify_token(token)
        assert payload.jti != "attacker-controlled-jti"

    def test_extra_claims_cannot_overwrite_type(self):
        """extra_claims cannot overwrite the 'type' claim."""
        token = create_access_token(
            user_id="user1",
            roles=["farmer"],
            extra_claims={"type": "refresh"},
        )
        payload = verify_token(token)
        assert payload.token_type == "access"

    def test_extra_claims_cannot_overwrite_tid(self):
        """extra_claims cannot overwrite 'tid' (tenant_id)."""
        token = create_access_token(
            user_id="user1",
            roles=["farmer"],
            tenant_id="real_tenant",
            extra_claims={"tid": "attacker_tenant"},
        )
        payload = verify_token(token)
        assert payload.tenant_id == "real_tenant"

    def test_safe_extra_claims_are_included(self):
        """Non-protected extra_claims are included in the token."""
        token = create_access_token(
            user_id="user1",
            roles=["farmer"],
            extra_claims={"custom_field": "hello", "level": 5},
        )
        decoded = decode_token_unsafe(token)
        assert decoded.get("custom_field") == "hello"
        assert decoded.get("level") == 5


class TestVerifyTokenSecurity:
    """Test security edge cases in verify_token."""

    def test_wrong_issuer_raises(self):
        """Token with wrong issuer is rejected."""
        payload = {
            "sub": "user1",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "wrong-issuer",
            "aud": "sahool-api",
            "type": "access",
        }
        token = jwt.encode(
            payload,
            os.environ["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error == AuthErrors.INVALID_ISSUER

    def test_wrong_audience_raises(self):
        """Token with wrong audience is rejected."""
        payload = {
            "sub": "user1",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "sahool-platform",
            "aud": "wrong-audience",
            "type": "access",
        }
        token = jwt.encode(
            payload,
            os.environ["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error == AuthErrors.INVALID_AUDIENCE

    def test_missing_sub_raises(self):
        """Token without 'sub' claim is rejected."""
        payload = {
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "sahool-platform",
            "aud": "sahool-api",
        }
        token = jwt.encode(
            payload,
            os.environ["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        with pytest.raises(AuthException):
            verify_token(token)

    def test_rs256_algorithm_rejected(self):
        """Token claiming RS256 algorithm is rejected."""
        # We can't easily forge an RS256 token, but we can test the
        # ALLOWED_ALGORITHMS check
        assert "RS256" not in ALLOWED_ALGORITHMS
        assert "RS384" not in ALLOWED_ALGORITHMS
        assert "RS512" not in ALLOWED_ALGORITHMS


class TestDecodeTokenAlias:
    """Test that decode_token is an alias for verify_token."""

    def test_decode_token_returns_same_as_verify(self):
        """decode_token and verify_token return identical payloads."""
        token = create_access_token(user_id="user1", roles=["farmer"])
        v = verify_token(token)
        d = decode_token(token)
        assert v.user_id == d.user_id
        assert v.roles == d.roles
        assert v.jti == d.jti

    def test_decode_token_raises_on_invalid(self):
        """decode_token raises AuthException on invalid token."""
        with pytest.raises(AuthException):
            decode_token("invalid")


class TestGetDebugDecodeOptions:
    """Test _get_debug_decode_options helper."""

    def test_returns_dict_with_verify_false(self):
        """Returns options dict with verify_signature=False."""
        opts = _get_debug_decode_options()
        assert isinstance(opts, dict)
        assert opts.get("verify_signature") is False


class TestRefreshAccessTokenEdgeCases:
    """Extended refresh_access_token tests."""

    def test_refresh_with_permissions(self):
        """refresh_access_token passes permissions to new token."""
        refresh = create_refresh_token(user_id="user1", tenant_id="t1")
        new_token = refresh_access_token(
            refresh,
            roles=["farmer"],
            permissions=["farm:read", "farm:write"],
        )
        payload = verify_token(new_token)
        assert "farm:read" in payload.permissions
        assert "farm:write" in payload.permissions

    def test_refresh_preserves_tenant(self):
        """refresh_access_token preserves tenant_id from refresh token."""
        refresh = create_refresh_token(user_id="user1", tenant_id="t1")
        new_token = refresh_access_token(refresh, roles=["farmer"])
        payload = verify_token(new_token)
        assert payload.tenant_id == "t1"

    def test_refresh_with_expired_token_raises(self):
        """Expired refresh token raises AuthException."""
        expired_refresh = create_refresh_token(user_id="user1")
        # We can't easily create an expired refresh token via the API
        # so we manually create one
        from shared.auth.config import config

        expired_payload = {
            "sub": "user1",
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
            "type": "refresh",
        }
        expired_token = jwt.encode(
            expired_payload,
            config.get_signing_key(),
            algorithm="HS256",
        )

        with pytest.raises(AuthException) as exc_info:
            refresh_access_token(expired_token, roles=["farmer"])

        assert exc_info.value.error == AuthErrors.EXPIRED_TOKEN


class TestTokenPairEdgeCases:
    """Extended create_token_pair tests."""

    def test_pair_with_tenant_and_permissions(self):
        """create_token_pair with all optional fields."""
        pair = create_token_pair(
            user_id="user1",
            roles=["farmer", "admin"],
            tenant_id="t1",
            permissions=["farm:read"],
        )

        access = verify_token(pair["access_token"])
        refresh = verify_token(pair["refresh_token"])

        assert access.tenant_id == "t1"
        assert access.permissions == ["farm:read"]
        assert refresh.tenant_id == "t1"

    def test_pair_expires_in_is_positive(self):
        """expires_in field is a positive integer in seconds."""
        pair = create_token_pair(user_id="user1", roles=[])
        assert pair["expires_in"] > 0
        assert isinstance(pair["expires_in"], int)
