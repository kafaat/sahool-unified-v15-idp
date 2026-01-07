"""
Unit Tests for Shared Authentication Module
Tests JWT token creation, verification, and user authentication
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pytest

from shared.auth.config import JWTConfig
from shared.auth.jwt_handler import (
    ALLOWED_ALGORITHMS,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    refresh_access_token,
    verify_token,
)
from shared.auth.models import AuthErrors, AuthException, TokenPayload


# ═══════════════════════════════════════════════════════════════════════════
# JWT Token Creation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCreateAccessToken:
    """Test access token creation"""

    @patch("shared.auth.jwt_handler.config")
    def test_create_basic_access_token(self, mock_config):
        """Test creating basic access token"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        token = create_access_token(
            user_id="user123", roles=["farmer", "admin"], permissions=["farm:read"]
        )

        assert isinstance(token, str)
        assert len(token) > 0

    @patch("shared.auth.jwt_handler.config")
    def test_access_token_with_tenant(self, mock_config):
        """Test creating access token with tenant ID"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        token = create_access_token(
            user_id="user123", roles=["farmer"], tenant_id="tenant456"
        )

        # Decode token to verify tenant is included
        payload = jwt.decode(
            token,
            "test_secret_key_32_bytes_long!!",
            algorithms=["HS256"],
            issuer="sahool",
            audience="sahool-api",
        )
        assert payload["tid"] == "tenant456"

    @patch("shared.auth.jwt_handler.config")
    def test_access_token_with_custom_expiry(self, mock_config):
        """Test creating access token with custom expiry"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        custom_delta = timedelta(minutes=60)
        token = create_access_token(
            user_id="user123", roles=["farmer"], expires_delta=custom_delta
        )

        payload = jwt.decode(
            token,
            "test_secret_key_32_bytes_long!!",
            algorithms=["HS256"],
            issuer="sahool",
            audience="sahool-api",
        )
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=UTC)
        delta = exp_time - iat_time

        assert abs(delta.total_seconds() - 3600) < 5  # Should be ~60 minutes

    @patch("shared.auth.jwt_handler.config")
    def test_access_token_includes_jti(self, mock_config):
        """Test access token includes unique JTI for revocation"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        token = create_access_token(user_id="user123", roles=["farmer"])

        payload = jwt.decode(
            token,
            "test_secret_key_32_bytes_long!!",
            algorithms=["HS256"],
            issuer="sahool",
            audience="sahool-api",
        )
        assert "jti" in payload
        assert uuid.UUID(payload["jti"])  # Should be valid UUID

    @patch("shared.auth.jwt_handler.config")
    def test_access_token_with_extra_claims(self, mock_config):
        """Test adding extra claims to access token"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        extra_claims = {"farm_id": "farm789", "region": "north"}
        token = create_access_token(
            user_id="user123", roles=["farmer"], extra_claims=extra_claims
        )

        payload = jwt.decode(
            token,
            "test_secret_key_32_bytes_long!!",
            algorithms=["HS256"],
            issuer="sahool",
            audience="sahool-api",
        )
        assert payload["farm_id"] == "farm789"
        assert payload["region"] == "north"


class TestCreateRefreshToken:
    """Test refresh token creation"""

    @patch("shared.auth.jwt_handler.config")
    def test_create_basic_refresh_token(self, mock_config):
        """Test creating basic refresh token"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        token = create_refresh_token(user_id="user123")

        assert isinstance(token, str)
        assert len(token) > 0

    @patch("shared.auth.jwt_handler.config")
    def test_refresh_token_type(self, mock_config):
        """Test refresh token has correct type"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        token = create_refresh_token(user_id="user123")

        payload = jwt.decode(
            token,
            "test_secret_key_32_bytes_long!!",
            algorithms=["HS256"],
            issuer="sahool",
            audience="sahool-api",
        )
        assert payload["type"] == "refresh"

    @patch("shared.auth.jwt_handler.config")
    def test_refresh_token_with_tenant(self, mock_config):
        """Test refresh token with tenant ID"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        token = create_refresh_token(user_id="user123", tenant_id="tenant456")

        payload = jwt.decode(
            token,
            "test_secret_key_32_bytes_long!!",
            algorithms=["HS256"],
            issuer="sahool",
            audience="sahool-api",
        )
        assert payload["tid"] == "tenant456"


class TestCreateTokenPair:
    """Test creating token pair"""

    @patch("shared.auth.jwt_handler.config")
    def test_create_token_pair(self, mock_config):
        """Test creating access and refresh token pair"""
        mock_config.get_signing_key.return_value = "test_secret_key_32_bytes_long!!"
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        tokens = create_token_pair(user_id="user123", roles=["farmer"])

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert "expires_in" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] == 30 * 60  # 30 minutes in seconds


# ═══════════════════════════════════════════════════════════════════════════
# JWT Token Verification Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVerifyToken:
    """Test token verification"""

    @patch("shared.auth.jwt_handler.config")
    def test_verify_valid_token(self, mock_config):
        """Test verifying valid token"""
        secret = "test_secret_key_32_bytes_long!!"
        mock_config.get_signing_key.return_value = secret
        mock_config.get_verification_key.return_value = secret
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Create token
        token = create_access_token(
            user_id="user123", roles=["farmer"], permissions=["farm:read"]
        )

        # Verify token
        payload = verify_token(token)

        assert isinstance(payload, TokenPayload)
        assert payload.user_id == "user123"
        assert "farmer" in payload.roles
        assert "farm:read" in payload.permissions

    @patch("shared.auth.jwt_handler.config")
    def test_verify_expired_token(self, mock_config):
        """Test verifying expired token raises exception"""
        secret = "test_secret_key_32_bytes_long!!"
        mock_config.get_signing_key.return_value = secret
        mock_config.get_verification_key.return_value = secret
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Create token that expires immediately
        token = create_access_token(
            user_id="user123", roles=["farmer"], expires_delta=timedelta(seconds=-1)
        )

        # Verify should raise expired token exception
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error == AuthErrors.EXPIRED_TOKEN

    @patch("shared.auth.jwt_handler.config")
    def test_verify_invalid_signature(self, mock_config):
        """Test verifying token with invalid signature"""
        mock_config.get_verification_key.return_value = "wrong_secret_key!!"
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Create token with different secret
        token = jwt.encode(
            {"sub": "user123", "roles": ["farmer"]},
            "different_secret!!",
            algorithm="HS256",
        )

        # Verify should raise invalid token exception
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error == AuthErrors.INVALID_TOKEN

    def test_verify_none_algorithm_rejected(self):
        """Test that 'none' algorithm is rejected"""
        # Create token with 'none' algorithm
        token = jwt.encode({"sub": "user123"}, "", algorithm="none")

        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error == AuthErrors.INVALID_TOKEN

    def test_verify_malformed_token(self):
        """Test verifying malformed token"""
        with pytest.raises(AuthException) as exc_info:
            verify_token("not.a.valid.jwt.token")
        assert exc_info.value.error == AuthErrors.INVALID_TOKEN

    @patch("shared.auth.jwt_handler.config")
    def test_verify_token_missing_required_fields(self, mock_config):
        """Test verifying token missing required fields"""
        secret = "test_secret_key_32_bytes_long!!"
        mock_config.get_verification_key.return_value = secret
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Create token without 'sub' field
        now = datetime.now(UTC)
        token = jwt.encode(
            {"exp": now + timedelta(minutes=30), "iat": now},
            secret,
            algorithm="HS256",
            headers={"alg": "HS256"},
        )

        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error == AuthErrors.INVALID_TOKEN


class TestRefreshAccessToken:
    """Test refreshing access tokens"""

    @patch("shared.auth.jwt_handler.config")
    def test_refresh_access_token_success(self, mock_config):
        """Test successfully refreshing access token"""
        secret = "test_secret_key_32_bytes_long!!"
        mock_config.get_signing_key.return_value = secret
        mock_config.get_verification_key.return_value = secret
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Create refresh token
        refresh_token = create_refresh_token(user_id="user123")

        # Use refresh token to get new access token
        new_access_token = refresh_access_token(
            refresh_token, roles=["farmer"], permissions=["farm:read"]
        )

        # Verify new access token
        payload = verify_token(new_access_token)
        assert payload.user_id == "user123"
        assert payload.token_type == "access"

    @patch("shared.auth.jwt_handler.config")
    def test_refresh_with_access_token_fails(self, mock_config):
        """Test refreshing with access token instead of refresh token fails"""
        secret = "test_secret_key_32_bytes_long!!"
        mock_config.get_signing_key.return_value = secret
        mock_config.get_verification_key.return_value = secret
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Try to use access token as refresh token
        access_token = create_access_token(user_id="user123", roles=["farmer"])

        with pytest.raises(AuthException) as exc_info:
            refresh_access_token(access_token, roles=["farmer"])
        assert exc_info.value.error == AuthErrors.INVALID_TOKEN


# ═══════════════════════════════════════════════════════════════════════════
# Security Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestAlgorithmSecurity:
    """Test algorithm security features"""

    def test_allowed_algorithms_hardcoded(self):
        """Test that allowed algorithms are hardcoded"""
        assert "HS256" in ALLOWED_ALGORITHMS
        assert "RS256" in ALLOWED_ALGORITHMS
        assert "none" not in ALLOWED_ALGORITHMS

    def test_algorithm_whitelist_prevents_confusion(self):
        """Test algorithm whitelist prevents algorithm confusion attacks"""
        # Try to create token with disallowed algorithm
        with pytest.raises(Exception):
            # This should fail when trying to verify
            token = jwt.encode(
                {"sub": "user123"}, "secret", algorithm="HS384", headers={"alg": "RS256"}
            )
            verify_token(token)


# ═══════════════════════════════════════════════════════════════════════════
# Token Payload Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestTokenPayload:
    """Test TokenPayload model"""

    def test_token_payload_creation(self):
        """Test creating TokenPayload"""
        now = datetime.now(UTC)
        payload = TokenPayload(
            user_id="user123",
            roles=["farmer", "admin"],
            exp=now + timedelta(minutes=30),
            iat=now,
            tenant_id="tenant456",
            jti="unique-jti-123",
            token_type="access",
            permissions=["farm:read", "farm:write"],
        )

        assert payload.user_id == "user123"
        assert len(payload.roles) == 2
        assert payload.tenant_id == "tenant456"
        assert payload.token_type == "access"
        assert len(payload.permissions) == 2


# ═══════════════════════════════════════════════════════════════════════════
# Auth Exception Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestAuthException:
    """Test AuthException"""

    def test_auth_exception_creation(self):
        """Test creating AuthException"""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        assert exc.error == AuthErrors.INVALID_TOKEN

    def test_auth_exception_with_detail(self):
        """Test AuthException with detail message"""
        exc = AuthException(AuthErrors.EXPIRED_TOKEN, detail="Token expired at 2024-01-01")
        assert exc.error == AuthErrors.EXPIRED_TOKEN
        assert "Token expired" in exc.detail


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestAuthenticationFlow:
    """Test complete authentication flow"""

    @patch("shared.auth.jwt_handler.config")
    def test_full_authentication_flow(self, mock_config):
        """Test complete authentication flow"""
        secret = "test_secret_key_32_bytes_long!!"
        mock_config.get_signing_key.return_value = secret
        mock_config.get_verification_key.return_value = secret
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Step 1: User logs in, gets token pair
        tokens = create_token_pair(
            user_id="user123",
            roles=["farmer"],
            tenant_id="tenant456",
            permissions=["farm:read", "farm:write"],
        )

        # Step 2: Verify access token
        access_payload = verify_token(tokens["access_token"])
        assert access_payload.user_id == "user123"
        assert access_payload.token_type == "access"

        # Step 3: Access token expires, use refresh token to get new one
        new_access_token = refresh_access_token(
            tokens["refresh_token"], roles=["farmer"], permissions=["farm:read", "farm:write"]
        )

        # Step 4: Verify new access token
        new_payload = verify_token(new_access_token)
        assert new_payload.user_id == "user123"
        assert new_payload.token_type == "access"

    @patch("shared.auth.jwt_handler.config")
    def test_multi_tenant_authentication(self, mock_config):
        """Test multi-tenant authentication"""
        secret = "test_secret_key_32_bytes_long!!"
        mock_config.get_signing_key.return_value = secret
        mock_config.get_verification_key.return_value = secret
        mock_config.JWT_ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_config.JWT_ISSUER = "sahool"
        mock_config.JWT_AUDIENCE = "sahool-api"

        # Create tokens for different tenants
        token1 = create_access_token(user_id="user123", roles=["farmer"], tenant_id="tenant1")
        token2 = create_access_token(user_id="user123", roles=["farmer"], tenant_id="tenant2")

        payload1 = verify_token(token1)
        payload2 = verify_token(token2)

        assert payload1.tenant_id == "tenant1"
        assert payload2.tenant_id == "tenant2"
        assert payload1.user_id == payload2.user_id  # Same user, different tenants
