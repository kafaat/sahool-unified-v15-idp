"""
Tests for JWT Module
"""

import pytest
from datetime import timedelta
import os

# Set test environment
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests"
os.environ["JWT_ALGORITHM"] = "HS256"

from shared.security.jwt import (
    create_token,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    verify_token,
    decode_token_unsafe,
    AuthError,
)


class TestTokenCreation:
    """Test JWT token creation"""

    def test_create_access_token(self):
        """Test creating an access token"""
        token = create_access_token(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=["worker"],
            scopes=["fieldops:task.read"],
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test creating a refresh token"""
        token = create_refresh_token(
            user_id="user-123",
            tenant_id="tenant-456",
        )

        assert token is not None
        payload = decode_token_unsafe(token)
        assert payload["type"] == "refresh"
        assert payload["roles"] == []
        assert payload["scopes"] == []

    def test_create_token_pair(self):
        """Test creating both access and refresh tokens"""
        pair = create_token_pair(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=["worker", "supervisor"],
            scopes=["fieldops:task.read", "fieldops:task.write"],
        )

        assert "access_token" in pair
        assert "refresh_token" in pair
        assert pair["token_type"] == "bearer"
        assert pair["expires_in"] > 0

    def test_create_token_with_custom_expiry(self):
        """Test creating token with custom expiration"""
        token = create_token(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=["admin"],
            scopes=[],
            expires_delta=timedelta(hours=1),
        )

        payload = decode_token_unsafe(token)
        assert payload is not None

    def test_create_token_with_extra_claims(self):
        """Test creating token with extra claims"""
        token = create_token(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=["worker"],
            scopes=[],
            extra_claims={"custom_field": "custom_value"},
        )

        payload = decode_token_unsafe(token)
        assert payload["custom_field"] == "custom_value"


class TestTokenVerification:
    """Test JWT token verification"""

    def test_verify_valid_token(self):
        """Test verifying a valid token"""
        token = create_access_token(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=["worker"],
            scopes=["fieldops:task.read"],
        )

        payload = verify_token(token)

        assert payload["sub"] == "user-123"
        assert payload["tid"] == "tenant-456"
        assert "worker" in payload["roles"]
        assert "fieldops:task.read" in payload["scopes"]

    def test_verify_expired_token(self):
        """Test verifying an expired token raises error"""
        token = create_token(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=[],
            scopes=[],
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        with pytest.raises(AuthError) as exc_info:
            verify_token(token)

        assert exc_info.value.code == "token_expired"

    def test_verify_invalid_token(self):
        """Test verifying an invalid token raises error"""
        with pytest.raises(AuthError):
            verify_token("invalid.token.here")

    def test_verify_tampered_token(self):
        """Test verifying a tampered token raises error"""
        token = create_access_token(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=[],
            scopes=[],
        )

        # Tamper with the token
        tampered = token[:-5] + "XXXXX"

        with pytest.raises(AuthError):
            verify_token(tampered)


class TestDecodeUnsafe:
    """Test unsafe token decoding"""

    def test_decode_valid_token(self):
        """Test decoding a valid token without verification"""
        token = create_access_token(
            user_id="user-123",
            tenant_id="tenant-456",
            roles=["admin"],
            scopes=[],
        )

        payload = decode_token_unsafe(token)

        assert payload["sub"] == "user-123"
        assert payload["tid"] == "tenant-456"

    def test_decode_invalid_token(self):
        """Test decoding invalid token returns empty dict"""
        payload = decode_token_unsafe("not-a-valid-token")
        assert payload == {}
