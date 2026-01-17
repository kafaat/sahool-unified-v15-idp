"""
Unit tests for shared/auth/jwt_handler.py
Tests JWT token creation, verification, and security features.
"""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock
import jwt

# Set test environment before imports
import os
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"

from shared.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
    create_token_pair,
    refresh_access_token,
    decode_token_unsafe,
    ALLOWED_ALGORITHMS,
)
from shared.auth.models import AuthException, AuthErrors


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_creates_valid_token(self):
        """Test that a valid JWT token is created."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_required_claims(self):
        """Test that token contains all required claims."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer", "admin"],
        )

        payload = verify_token(token)

        assert payload.user_id == "user123"
        assert "farmer" in payload.roles
        assert "admin" in payload.roles
        assert payload.token_type == "access"
        assert payload.jti is not None

    def test_token_with_tenant_id(self):
        """Test token creation with tenant_id."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
            tenant_id="tenant456",
        )

        payload = verify_token(token)

        assert payload.tenant_id == "tenant456"

    def test_token_with_permissions(self):
        """Test token creation with permissions."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
            permissions=["farm:read", "farm:write"],
        )

        payload = verify_token(token)

        assert "farm:read" in payload.permissions
        assert "farm:write" in payload.permissions

    def test_custom_expiration(self):
        """Test token with custom expiration time."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
            expires_delta=timedelta(hours=2),
        )

        payload = verify_token(token)

        expected_exp = datetime.now(UTC) + timedelta(hours=2)
        assert abs((payload.exp - expected_exp).total_seconds()) < 5

    def test_extra_claims(self):
        """Test token with extra custom claims."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
            extra_claims={"custom_field": "custom_value"},
        )

        # Use unsafe decode to check extra claims
        decoded = decode_token_unsafe(token)

        assert decoded.get("custom_field") == "custom_value"


class TestCreateRefreshToken:
    """Tests for create_refresh_token function."""

    def test_creates_valid_refresh_token(self):
        """Test that a valid refresh token is created."""
        token = create_refresh_token(user_id="user123")

        assert token is not None
        assert isinstance(token, str)

    def test_refresh_token_type(self):
        """Test that refresh token has correct type."""
        token = create_refresh_token(user_id="user123")

        payload = verify_token(token)

        assert payload.token_type == "refresh"

    def test_refresh_token_no_roles(self):
        """Test that refresh token does not contain roles."""
        token = create_refresh_token(user_id="user123")

        payload = verify_token(token)

        assert payload.roles == []

    def test_refresh_token_with_tenant(self):
        """Test refresh token with tenant_id."""
        token = create_refresh_token(
            user_id="user123",
            tenant_id="tenant456",
        )

        payload = verify_token(token)

        assert payload.tenant_id == "tenant456"


class TestVerifyToken:
    """Tests for verify_token function."""

    def test_verify_valid_token(self):
        """Test verification of a valid token."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
        )

        payload = verify_token(token)

        assert payload.user_id == "user123"

    def test_verify_expired_token(self):
        """Test that expired tokens are rejected."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
            expires_delta=timedelta(seconds=-10),  # Already expired
        )

        with pytest.raises(AuthException) as exc_info:
            verify_token(token)

        assert exc_info.value.error == AuthErrors.EXPIRED_TOKEN

    def test_verify_invalid_token(self):
        """Test that invalid tokens are rejected."""
        with pytest.raises(AuthException) as exc_info:
            verify_token("invalid.token.here")

        assert exc_info.value.error == AuthErrors.INVALID_TOKEN

    def test_verify_tampered_token(self):
        """Test that tampered tokens are rejected."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
        )

        # Tamper with the token by modifying characters
        tampered = token[:-5] + "xxxxx"

        with pytest.raises(AuthException):
            verify_token(tampered)

    def test_verify_none_algorithm_rejected(self):
        """Test that 'none' algorithm is explicitly rejected."""
        # Create an unsigned token with 'none' algorithm
        payload = {
            "sub": "user123",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
        }

        # Manually create a token with 'none' algorithm
        # This should be rejected by our security checks
        unsigned_token = jwt.encode(payload, "", algorithm="none")

        with pytest.raises(AuthException) as exc_info:
            verify_token(unsigned_token)

        assert exc_info.value.error == AuthErrors.INVALID_TOKEN

    def test_algorithm_whitelist(self):
        """Test that only whitelisted algorithms are accepted."""
        assert "HS256" in ALLOWED_ALGORITHMS
        assert "RS256" in ALLOWED_ALGORITHMS
        assert "none" not in ALLOWED_ALGORITHMS


class TestCreateTokenPair:
    """Tests for create_token_pair function."""

    def test_creates_both_tokens(self):
        """Test that both access and refresh tokens are created."""
        tokens = create_token_pair(
            user_id="user123",
            roles=["farmer"],
        )

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert "expires_in" in tokens

    def test_token_type_is_bearer(self):
        """Test that token type is bearer."""
        tokens = create_token_pair(
            user_id="user123",
            roles=["farmer"],
        )

        assert tokens["token_type"] == "bearer"

    def test_both_tokens_are_valid(self):
        """Test that both tokens can be verified."""
        tokens = create_token_pair(
            user_id="user123",
            roles=["farmer"],
        )

        access_payload = verify_token(tokens["access_token"])
        refresh_payload = verify_token(tokens["refresh_token"])

        assert access_payload.user_id == "user123"
        assert refresh_payload.user_id == "user123"
        assert access_payload.token_type == "access"
        assert refresh_payload.token_type == "refresh"


class TestRefreshAccessToken:
    """Tests for refresh_access_token function."""

    def test_refresh_creates_new_access_token(self):
        """Test that refresh creates a new access token."""
        tokens = create_token_pair(
            user_id="user123",
            roles=["farmer"],
        )

        new_access = refresh_access_token(
            refresh_token=tokens["refresh_token"],
            roles=["farmer", "admin"],  # Roles from database
        )

        payload = verify_token(new_access)

        assert payload.user_id == "user123"
        assert "admin" in payload.roles
        assert payload.token_type == "access"

    def test_refresh_rejects_access_token(self):
        """Test that access tokens cannot be used as refresh tokens."""
        tokens = create_token_pair(
            user_id="user123",
            roles=["farmer"],
        )

        with pytest.raises(AuthException) as exc_info:
            refresh_access_token(
                refresh_token=tokens["access_token"],  # Wrong token type
                roles=["farmer"],
            )

        assert exc_info.value.error == AuthErrors.INVALID_TOKEN


class TestDecodeTokenUnsafe:
    """Tests for decode_token_unsafe function."""

    def test_decode_valid_token(self):
        """Test decoding a valid token without verification."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
        )

        payload = decode_token_unsafe(token)

        assert payload.get("sub") == "user123"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token returns empty dict."""
        payload = decode_token_unsafe("invalid.token.here")

        assert payload == {}

    def test_decode_expired_token(self):
        """Test that expired tokens can still be decoded (unsafe)."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
            expires_delta=timedelta(seconds=-10),
        )

        payload = decode_token_unsafe(token)

        # Should decode even though expired (for debugging)
        assert payload.get("sub") == "user123"


class TestSecurityFeatures:
    """Tests for security features of the JWT handler."""

    def test_unique_jti_per_token(self):
        """Test that each token has a unique jti."""
        token1 = create_access_token(user_id="user123", roles=["farmer"])
        token2 = create_access_token(user_id="user123", roles=["farmer"])

        payload1 = verify_token(token1)
        payload2 = verify_token(token2)

        assert payload1.jti != payload2.jti

    def test_iat_is_current_time(self):
        """Test that iat (issued at) is set to current time."""
        before = datetime.now(UTC)
        token = create_access_token(user_id="user123", roles=["farmer"])
        after = datetime.now(UTC)

        payload = verify_token(token)

        assert before <= payload.iat <= after

    def test_token_has_issuer(self):
        """Test that token has issuer claim."""
        token = create_access_token(user_id="user123", roles=["farmer"])

        decoded = decode_token_unsafe(token)

        assert "iss" in decoded

    def test_token_has_audience(self):
        """Test that token has audience claim."""
        token = create_access_token(user_id="user123", roles=["farmer"])

        decoded = decode_token_unsafe(token)

        assert "aud" in decoded
