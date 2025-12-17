"""
SAHOOL JWT Unit Tests
Tests for JWT token creation and verification
"""

import os
from datetime import datetime, timedelta, timezone

import pytest

# Set test environment before importing jwt module
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"

from shared.security.jwt import (
    AuthError,
    create_access_token,
    create_refresh_token,
    create_token,
    create_token_pair,
    decode_token_unsafe,
    verify_token,
)


class TestTokenCreation:
    """Tests for token creation functions"""

    def test_create_token_returns_string(self, test_user_id, test_tenant_id):
        """Token creation should return a string"""
        token = create_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=["worker"],
            scopes=["fieldops:task.read"],
        )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_has_three_parts(self, test_user_id, test_tenant_id):
        """JWT should have header.payload.signature format"""
        token = create_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=["worker"],
            scopes=[],
        )

        parts = token.split(".")
        assert len(parts) == 3

    def test_create_access_token(self, test_user_id, test_tenant_id):
        """Access token should be created with correct type"""
        token = create_access_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=["worker"],
            scopes=["fieldops:task.read"],
        )

        payload = decode_token_unsafe(token)
        assert payload["type"] == "access"
        assert payload["sub"] == test_user_id
        assert payload["tid"] == test_tenant_id

    def test_create_refresh_token(self, test_user_id, test_tenant_id):
        """Refresh token should have minimal claims"""
        token = create_refresh_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
        )

        payload = decode_token_unsafe(token)
        assert payload["type"] == "refresh"
        assert payload["roles"] == []
        assert payload["scopes"] == []

    def test_create_token_pair(self, test_user_id, test_tenant_id):
        """Token pair should contain access and refresh tokens"""
        pair = create_token_pair(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=["worker"],
            scopes=["fieldops:task.read"],
        )

        assert "access_token" in pair
        assert "refresh_token" in pair
        assert pair["token_type"] == "bearer"
        assert isinstance(pair["expires_in"], int)

    def test_token_includes_roles_and_scopes(self, test_user_id, test_tenant_id):
        """Token payload should include roles and scopes"""
        roles = ["worker", "supervisor"]
        scopes = ["fieldops:task.read", "fieldops:task.create"]

        token = create_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=roles,
            scopes=scopes,
        )

        payload = decode_token_unsafe(token)
        assert payload["roles"] == roles
        assert payload["scopes"] == scopes

    def test_token_includes_extra_claims(self, test_user_id, test_tenant_id):
        """Token should include extra claims when provided"""
        extra = {"custom_field": "custom_value", "user_name": "Test User"}

        token = create_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=[],
            scopes=[],
            extra_claims=extra,
        )

        payload = decode_token_unsafe(token)
        assert payload["custom_field"] == "custom_value"
        assert payload["user_name"] == "Test User"


class TestTokenVerification:
    """Tests for token verification"""

    def test_verify_valid_token(self, test_user_id, test_tenant_id):
        """Valid token should verify successfully"""
        token = create_access_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=["worker"],
            scopes=["fieldops:task.read"],
        )

        payload = verify_token(token)

        assert payload["sub"] == test_user_id
        assert payload["tid"] == test_tenant_id

    def test_verify_token_sets_default_roles(self, test_user_id, test_tenant_id):
        """Verified token should have roles default to empty list"""
        token = create_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=[],
            scopes=[],
        )

        payload = verify_token(token)
        assert payload["roles"] == []
        assert payload["scopes"] == []

    def test_verify_expired_token_raises(self, test_user_id, test_tenant_id):
        """Expired token should raise AuthError"""
        # Create token that expires in -1 seconds (already expired)
        token = create_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=[],
            scopes=[],
            expires_delta=timedelta(seconds=-1),
        )

        with pytest.raises(AuthError) as exc:
            verify_token(token)

        assert exc.value.code == "token_expired"

    def test_verify_invalid_token_raises(self):
        """Invalid token string should raise AuthError"""
        with pytest.raises(AuthError) as exc:
            verify_token("invalid.token.string")

        assert exc.value.code == "invalid_token"

    def test_verify_tampered_token_raises(self, test_user_id, test_tenant_id):
        """Tampered token should raise AuthError"""
        token = create_access_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=["worker"],
            scopes=[],
        )

        # Tamper with signature
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".tampered_signature"

        with pytest.raises(AuthError) as exc:
            verify_token(tampered)

        assert exc.value.code == "invalid_token"


class TestDecodeTokenUnsafe:
    """Tests for unsafe token decoding"""

    def test_decode_valid_token(self, test_user_id, test_tenant_id):
        """Should decode token without verification"""
        token = create_access_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            roles=["worker"],
            scopes=[],
        )

        payload = decode_token_unsafe(token)

        assert payload["sub"] == test_user_id
        assert payload["tid"] == test_tenant_id

    def test_decode_invalid_token_returns_empty(self):
        """Should return empty dict for invalid token"""
        payload = decode_token_unsafe("not.a.valid.token")

        assert payload == {}

    def test_decode_empty_string_returns_empty(self):
        """Should return empty dict for empty string"""
        payload = decode_token_unsafe("")

        assert payload == {}


class TestAuthError:
    """Tests for AuthError exception"""

    def test_auth_error_has_message_and_code(self):
        """AuthError should store message and code"""
        error = AuthError("Test message", "test_code")

        assert error.message == "Test message"
        assert error.code == "test_code"

    def test_auth_error_default_code(self):
        """AuthError should have default code"""
        error = AuthError("Test message")

        assert error.code == "auth_error"

    def test_auth_error_is_exception(self):
        """AuthError should be raisable"""
        with pytest.raises(AuthError):
            raise AuthError("Test error")
