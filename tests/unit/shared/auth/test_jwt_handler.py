"""
Tests for JWT Handler Module
=============================
اختبارات وحدة معالج JWT

Comprehensive tests for JWT token creation and verification.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock

import pytest

# Set up test environment before imports
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_ISSUER", "sahool-idp")
os.environ.setdefault("JWT_AUDIENCE", "sahool-platform")

pytest.importorskip("_cffi_backend", reason="cffi backend not available")

from shared.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    verify_token,
    decode_token,
    decode_token_unsafe,
    refresh_access_token,
    ALLOWED_ALGORITHMS,
)
from shared.auth.models import AuthException, TokenPayload


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def test_user_id() -> str:
    """Standard test user ID."""
    return "user-123-abc"


@pytest.fixture
def test_roles() -> list[str]:
    """Standard test roles."""
    return ["farmer", "admin"]


@pytest.fixture
def test_permissions() -> list[str]:
    """Standard test permissions."""
    return ["farm:read", "farm:write", "field:manage"]


@pytest.fixture
def test_tenant_id() -> str:
    """Standard test tenant ID."""
    return "tenant-456-xyz"


@pytest.fixture
def valid_access_token(test_user_id, test_roles, test_permissions, test_tenant_id) -> str:
    """Create a valid access token for testing."""
    return create_access_token(
        user_id=test_user_id,
        roles=test_roles,
        permissions=test_permissions,
        tenant_id=test_tenant_id,
    )


@pytest.fixture
def valid_refresh_token(test_user_id, test_tenant_id) -> str:
    """Create a valid refresh token for testing."""
    return create_refresh_token(
        user_id=test_user_id,
        tenant_id=test_tenant_id,
    )


# =============================================================================
# Test ALLOWED_ALGORITHMS Constant
# =============================================================================


class TestAllowedAlgorithms:
    """Tests for algorithm whitelist."""

    def test_allowed_algorithms_exist(self):
        """Test that allowed algorithms are defined."""
        assert ALLOWED_ALGORITHMS is not None
        assert len(ALLOWED_ALGORITHMS) > 0

    def test_contains_secure_algorithms(self):
        """Test that only HS256 is allowed (other algorithms excluded to prevent confusion attacks)."""
        assert "HS256" in ALLOWED_ALGORITHMS
        assert len(ALLOWED_ALGORITHMS) == 1

    def test_none_algorithm_not_allowed(self):
        """Test that 'none' algorithm is NOT in the whitelist."""
        assert "none" not in ALLOWED_ALGORITHMS
        assert "None" not in ALLOWED_ALGORITHMS
        assert "NONE" not in ALLOWED_ALGORITHMS


# =============================================================================
# Test create_access_token
# =============================================================================


class TestCreateAccessToken:
    """Tests for access token creation."""

    def test_create_basic_token(self, test_user_id, test_roles):
        """Test creating a basic access token."""
        token = create_access_token(user_id=test_user_id, roles=test_roles)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long

    def test_create_token_with_permissions(self, test_user_id, test_roles, test_permissions):
        """Test creating a token with permissions."""
        token = create_access_token(
            user_id=test_user_id,
            roles=test_roles,
            permissions=test_permissions,
        )

        payload = verify_token(token)
        assert payload.permissions == test_permissions

    def test_create_token_with_tenant(self, test_user_id, test_roles, test_tenant_id):
        """Test creating a token with tenant ID."""
        token = create_access_token(
            user_id=test_user_id,
            roles=test_roles,
            tenant_id=test_tenant_id,
        )

        payload = verify_token(token)
        assert payload.tenant_id == test_tenant_id

    def test_create_token_with_custom_expiry(self, test_user_id, test_roles):
        """Test creating a token with custom expiration."""
        expires_delta = timedelta(hours=2)
        token = create_access_token(
            user_id=test_user_id,
            roles=test_roles,
            expires_delta=expires_delta,
        )

        payload = verify_token(token)
        # Token should expire approximately 2 hours from now
        expected_exp = datetime.now(UTC) + expires_delta
        assert abs((payload.exp - expected_exp).total_seconds()) < 5

    def test_create_token_with_extra_claims(self, test_user_id, test_roles):
        """Test creating a token with extra claims."""
        extra_claims = {"custom_field": "custom_value", "user_level": 5}
        token = create_access_token(
            user_id=test_user_id,
            roles=test_roles,
            extra_claims=extra_claims,
        )

        # Token should still be valid
        payload = verify_token(token)
        assert payload is not None

    def test_token_has_jti(self, test_user_id, test_roles):
        """Test that token has unique JTI claim."""
        token = create_access_token(user_id=test_user_id, roles=test_roles)
        payload = verify_token(token)

        assert payload.jti is not None
        assert len(payload.jti) > 0

    def test_token_has_correct_type(self, test_user_id, test_roles):
        """Test that token has 'access' type."""
        token = create_access_token(user_id=test_user_id, roles=test_roles)
        payload = verify_token(token)

        assert payload.token_type == "access"

    def test_multiple_tokens_have_unique_jti(self, test_user_id, test_roles):
        """Test that multiple tokens have unique JTI values."""
        token1 = create_access_token(user_id=test_user_id, roles=test_roles)
        token2 = create_access_token(user_id=test_user_id, roles=test_roles)

        payload1 = verify_token(token1)
        payload2 = verify_token(token2)

        assert payload1.jti != payload2.jti


# =============================================================================
# Test create_refresh_token
# =============================================================================


class TestCreateRefreshToken:
    """Tests for refresh token creation."""

    def test_create_basic_refresh_token(self, test_user_id):
        """Test creating a basic refresh token."""
        token = create_refresh_token(user_id=test_user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_refresh_token_with_tenant(self, test_user_id, test_tenant_id):
        """Test creating refresh token with tenant ID."""
        token = create_refresh_token(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
        )

        payload = verify_token(token)
        assert payload.tenant_id == test_tenant_id

    def test_refresh_token_has_correct_type(self, test_user_id):
        """Test that refresh token has 'refresh' type."""
        token = create_refresh_token(user_id=test_user_id)
        payload = verify_token(token)

        assert payload.token_type == "refresh"

    def test_refresh_token_longer_expiry(self, test_user_id):
        """Test that refresh token has longer expiry than access token."""
        access_token = create_access_token(user_id=test_user_id, roles=[])
        refresh_token = create_refresh_token(user_id=test_user_id)

        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)

        assert refresh_payload.exp > access_payload.exp


# =============================================================================
# Test create_token_pair
# =============================================================================


class TestCreateTokenPair:
    """Tests for token pair creation."""

    def test_create_basic_pair(self, test_user_id, test_roles):
        """Test creating a basic token pair."""
        pair = create_token_pair(user_id=test_user_id, roles=test_roles)

        assert "access_token" in pair
        assert "refresh_token" in pair
        assert "token_type" in pair
        assert "expires_in" in pair

    def test_pair_has_bearer_type(self, test_user_id, test_roles):
        """Test that token pair has 'bearer' type."""
        pair = create_token_pair(user_id=test_user_id, roles=test_roles)

        assert pair["token_type"] == "bearer"

    def test_pair_expires_in_seconds(self, test_user_id, test_roles):
        """Test that expires_in is in seconds."""
        pair = create_token_pair(user_id=test_user_id, roles=test_roles)

        # Should be positive integer representing seconds
        assert pair["expires_in"] > 0
        assert isinstance(pair["expires_in"], int)

    def test_pair_tokens_are_valid(self, test_user_id, test_roles):
        """Test that both tokens in pair are valid."""
        pair = create_token_pair(user_id=test_user_id, roles=test_roles)

        access_payload = verify_token(pair["access_token"])
        refresh_payload = verify_token(pair["refresh_token"])

        assert access_payload.user_id == test_user_id
        assert refresh_payload.user_id == test_user_id

    def test_pair_with_permissions(self, test_user_id, test_roles, test_permissions):
        """Test creating pair with permissions."""
        pair = create_token_pair(
            user_id=test_user_id,
            roles=test_roles,
            permissions=test_permissions,
        )

        access_payload = verify_token(pair["access_token"])
        assert access_payload.permissions == test_permissions


# =============================================================================
# Test verify_token
# =============================================================================


class TestVerifyToken:
    """Tests for token verification."""

    def test_verify_valid_token(self, valid_access_token, test_user_id, test_roles):
        """Test verifying a valid token."""
        payload = verify_token(valid_access_token)

        assert payload is not None
        assert isinstance(payload, TokenPayload)
        assert payload.user_id == test_user_id
        assert payload.roles == test_roles

    def test_verify_returns_token_payload(self, valid_access_token):
        """Test that verify returns TokenPayload object."""
        payload = verify_token(valid_access_token)

        assert isinstance(payload, TokenPayload)
        assert hasattr(payload, "user_id")
        assert hasattr(payload, "roles")
        assert hasattr(payload, "exp")
        assert hasattr(payload, "iat")

    def test_verify_expired_token_raises(self, test_user_id, test_roles):
        """Test that expired token raises AuthException."""
        # Create token that expired 1 hour ago
        expired_token = create_access_token(
            user_id=test_user_id,
            roles=test_roles,
            expires_delta=timedelta(hours=-1),
        )

        with pytest.raises(AuthException):
            verify_token(expired_token)

    def test_verify_invalid_token_raises(self):
        """Test that invalid token raises AuthException."""
        with pytest.raises(AuthException):
            verify_token("invalid.token.here")

    def test_verify_malformed_token_raises(self):
        """Test that malformed token raises AuthException."""
        with pytest.raises(AuthException):
            verify_token("not-a-jwt-token")

    def test_verify_empty_token_raises(self):
        """Test that empty token raises AuthException."""
        with pytest.raises(AuthException):
            verify_token("")

    def test_verify_rejects_none_algorithm(self):
        """Test that 'none' algorithm tokens are rejected."""
        import jwt

        # Create a token with 'none' algorithm (security attack)
        payload = {
            "sub": "attacker",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": "sahool-idp",
            "aud": "sahool-platform",
        }

        # This should NOT be accepted
        # nosemgrep: python.jwt.security.jwt-hardcode-secret
        fake_token = jwt.encode(payload, "", algorithm="none")

        with pytest.raises(AuthException):
            verify_token(fake_token)


# =============================================================================
# Test decode_token
# =============================================================================


class TestDecodeToken:
    """Tests for decode_token (alias for verify_token)."""

    def test_decode_is_alias_for_verify(self, valid_access_token):
        """Test that decode_token works the same as verify_token."""
        verify_result = verify_token(valid_access_token)
        decode_result = decode_token(valid_access_token)

        assert verify_result.user_id == decode_result.user_id
        assert verify_result.roles == decode_result.roles


# =============================================================================
# Test decode_token_unsafe
# =============================================================================


class TestDecodeTokenUnsafe:
    """Tests for unsafe token decoding (debug only)."""

    def test_decode_unsafe_returns_dict(self, valid_access_token):
        """Test that unsafe decode returns dictionary."""
        result = decode_token_unsafe(valid_access_token)

        assert isinstance(result, dict)

    def test_decode_unsafe_does_not_verify(self):
        """Test that unsafe decode does not verify signature."""
        import jwt

        # Create token with wrong secret
        payload = {
            "sub": "user-123",
            "roles": ["farmer"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
        }
        # nosemgrep: python.jwt.security.jwt-hardcode-secret
        fake_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

        # Unsafe decode should still work
        result = decode_token_unsafe(fake_token)
        assert result.get("sub") == "user-123"

    def test_decode_unsafe_returns_empty_on_invalid(self):
        """Test that unsafe decode returns empty dict on invalid token."""
        result = decode_token_unsafe("not-a-valid-token")
        assert result == {}


# =============================================================================
# Test refresh_access_token
# =============================================================================


class TestRefreshAccessToken:
    """Tests for token refresh functionality."""

    def test_refresh_creates_new_access_token(self, valid_refresh_token, test_roles, test_permissions):
        """Test that refresh creates a new access token."""
        new_token = refresh_access_token(
            refresh_token=valid_refresh_token,
            roles=test_roles,
            permissions=test_permissions,
        )

        assert new_token is not None
        payload = verify_token(new_token)
        assert payload.token_type == "access"

    def test_refresh_with_access_token_fails(self, valid_access_token, test_roles):
        """Test that using access token for refresh fails."""
        with pytest.raises(AuthException):
            refresh_access_token(
                refresh_token=valid_access_token,
                roles=test_roles,
            )

    def test_refresh_preserves_user_id(self, valid_refresh_token, test_user_id, test_roles):
        """Test that refresh preserves user ID."""
        new_token = refresh_access_token(
            refresh_token=valid_refresh_token,
            roles=test_roles,
        )

        payload = verify_token(new_token)
        assert payload.user_id == test_user_id

    def test_refresh_preserves_tenant_id(self, valid_refresh_token, test_tenant_id, test_roles):
        """Test that refresh preserves tenant ID."""
        new_token = refresh_access_token(
            refresh_token=valid_refresh_token,
            roles=test_roles,
        )

        payload = verify_token(new_token)
        assert payload.tenant_id == test_tenant_id


# =============================================================================
# Test Security Edge Cases
# =============================================================================


class TestSecurityEdgeCases:
    """Tests for security-related edge cases."""

    def test_token_with_modified_payload_fails(self, valid_access_token):
        """Test that modifying token payload invalidates it."""
        import base64
        import json

        # Split token into parts
        parts = valid_access_token.split(".")
        assert len(parts) == 3

        # Decode and modify payload
        payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")
        payload = json.loads(payload_bytes)
        payload["roles"] = ["super_admin"]  # Attempt privilege escalation

        # Re-encode payload
        modified_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

        # Create modified token
        modified_token = f"{parts[0]}.{modified_payload}.{parts[2]}"

        # Should fail verification
        with pytest.raises(AuthException):
            verify_token(modified_token)

    def test_empty_roles_allowed(self, test_user_id):
        """Test that empty roles list is allowed."""
        token = create_access_token(user_id=test_user_id, roles=[])

        payload = verify_token(token)
        assert payload.roles == []

    def test_special_characters_in_user_id(self):
        """Test handling of special characters in user ID."""
        special_user_id = "user@domain.com"
        token = create_access_token(user_id=special_user_id, roles=["farmer"])

        payload = verify_token(token)
        assert payload.user_id == special_user_id

    def test_unicode_in_claims(self):
        """Test handling of Unicode characters in claims."""
        arabic_tenant = "مزرعة-123"
        token = create_access_token(
            user_id="user-123",
            roles=["farmer"],
            tenant_id=arabic_tenant,
        )

        payload = verify_token(token)
        assert payload.tenant_id == arabic_tenant


# =============================================================================
# Test Token Payload Structure
# =============================================================================


class TestTokenPayloadStructure:
    """Tests for TokenPayload structure."""

    def test_payload_has_required_fields(self, valid_access_token):
        """Test that payload has all required fields."""
        payload = verify_token(valid_access_token)

        assert payload.user_id is not None
        assert payload.roles is not None
        assert payload.exp is not None
        assert payload.iat is not None

    def test_exp_is_datetime(self, valid_access_token):
        """Test that exp is a datetime object."""
        payload = verify_token(valid_access_token)

        assert isinstance(payload.exp, datetime)

    def test_iat_is_datetime(self, valid_access_token):
        """Test that iat is a datetime object."""
        payload = verify_token(valid_access_token)

        assert isinstance(payload.iat, datetime)

    def test_exp_is_in_future(self, valid_access_token):
        """Test that exp is in the future."""
        payload = verify_token(valid_access_token)

        assert payload.exp > datetime.now(UTC)

    def test_iat_is_in_past_or_now(self, valid_access_token):
        """Test that iat is in the past or now."""
        payload = verify_token(valid_access_token)

        # Allow small margin for execution time
        assert payload.iat <= datetime.now(UTC) + timedelta(seconds=5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
