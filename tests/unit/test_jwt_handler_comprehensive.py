"""
Comprehensive JWT Handler Tests for SAHOOL Platform
اختبارات شاملة لمعالج JWT لمنصة سهول

Tests cover:
- Token creation (access + refresh)
- Token verification & decoding
- Algorithm confusion attack prevention
- Token pair creation
- Refresh token flow
- Expired token handling
- Invalid token rejection
- Token claims validation
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime, timedelta

import jwt
import pytest

# Ensure test environment
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_ISSUER", "sahool-platform")
os.environ.setdefault("JWT_AUDIENCE", "sahool-api")

from shared.auth.config import JWTConfig, config
from shared.auth.jwt_handler import (
    ALLOWED_ALGORITHMS,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    decode_token_unsafe,
    refresh_access_token,
    verify_token,
)
from shared.auth.models import AuthException, TokenPayload


@pytest.mark.unit
class TestCreateAccessToken:
    """Tests for access token creation"""

    def test_create_basic_access_token(self):
        """Test creating a basic access token with required fields"""
        token = create_access_token(user_id="user-123", roles=["farmer"])
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_contains_required_claims(self):
        """Test that access token contains all required JWT claims"""
        token = create_access_token(user_id="user-456", roles=["admin", "farmer"])
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )

        assert payload["sub"] == "user-456"
        assert payload["roles"] == ["admin", "farmer"]
        assert payload["type"] == "access"
        assert payload["iss"] == config.JWT_ISSUER
        assert payload["aud"] == config.JWT_AUDIENCE
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload

    def test_access_token_with_tenant_id(self):
        """Test access token includes tenant ID when provided"""
        token = create_access_token(
            user_id="user-789",
            roles=["farmer"],
            tenant_id="tenant-abc",
        )
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert payload["tid"] == "tenant-abc"

    def test_access_token_without_tenant_id(self):
        """Test access token without tenant ID"""
        token = create_access_token(user_id="user-789", roles=["farmer"])
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert "tid" not in payload

    def test_access_token_with_permissions(self):
        """Test access token includes permissions"""
        token = create_access_token(
            user_id="user-1",
            roles=["farmer"],
            permissions=["farm:read", "field:write"],
        )
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert payload["permissions"] == ["farm:read", "field:write"]

    def test_access_token_custom_expiration(self):
        """Test access token with custom expiration delta"""
        token = create_access_token(
            user_id="user-1",
            roles=["farmer"],
            expires_delta=timedelta(minutes=5),
        )
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat = datetime.fromtimestamp(payload["iat"], tz=UTC)
        # Should be approximately 5 minutes
        diff = (exp - iat).total_seconds()
        assert 295 <= diff <= 305  # ~5 minutes with small tolerance

    def test_access_token_with_extra_claims(self):
        """Test access token with extra custom claims"""
        token = create_access_token(
            user_id="user-1",
            roles=["farmer"],
            extra_claims={"custom_field": "value", "farm_count": 3},
        )
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert payload["custom_field"] == "value"
        assert payload["farm_count"] == 3

    def test_access_token_unique_jti(self):
        """Test that each access token gets a unique JTI"""
        token1 = create_access_token(user_id="user-1", roles=["farmer"])
        token2 = create_access_token(user_id="user-1", roles=["farmer"])

        payload1 = jwt.decode(
            token1,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        payload2 = jwt.decode(
            token2,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert payload1["jti"] != payload2["jti"]

    def test_access_token_empty_roles(self):
        """Test access token with empty roles list"""
        token = create_access_token(user_id="user-1", roles=[])
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert payload["roles"] == []


@pytest.mark.unit
class TestCreateRefreshToken:
    """Tests for refresh token creation"""

    def test_create_basic_refresh_token(self):
        """Test creating a basic refresh token"""
        token = create_refresh_token(user_id="user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_refresh_token_type(self):
        """Test that refresh token has correct type claim"""
        token = create_refresh_token(user_id="user-123")
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert payload["type"] == "refresh"

    def test_refresh_token_with_tenant_id(self):
        """Test refresh token includes tenant ID"""
        token = create_refresh_token(user_id="user-1", tenant_id="tenant-xyz")
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert payload["tid"] == "tenant-xyz"

    def test_refresh_token_longer_expiration(self):
        """Test that refresh token has longer expiration than access token"""
        access = create_access_token(user_id="user-1", roles=["farmer"])
        refresh = create_refresh_token(user_id="user-1")

        access_payload = jwt.decode(
            access,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        refresh_payload = jwt.decode(
            refresh,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )

        assert refresh_payload["exp"] > access_payload["exp"]

    def test_refresh_token_no_roles(self):
        """Test that refresh token does not contain roles"""
        token = create_refresh_token(user_id="user-1")
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )
        assert "roles" not in payload


@pytest.mark.unit
class TestVerifyToken:
    """Tests for token verification"""

    def test_verify_valid_access_token(self):
        """Test verifying a valid access token"""
        token = create_access_token(
            user_id="user-123",
            roles=["farmer", "admin"],
            tenant_id="tenant-1",
            permissions=["farm:read"],
        )
        result = verify_token(token)

        assert isinstance(result, TokenPayload)
        assert result.user_id == "user-123"
        assert result.roles == ["farmer", "admin"]
        assert result.tenant_id == "tenant-1"
        assert result.permissions == ["farm:read"]
        assert result.token_type == "access"
        assert result.jti is not None

    def test_verify_valid_refresh_token(self):
        """Test verifying a valid refresh token"""
        token = create_refresh_token(user_id="user-456", tenant_id="tenant-2")
        result = verify_token(token)

        assert result.user_id == "user-456"
        assert result.tenant_id == "tenant-2"
        assert result.token_type == "refresh"

    def test_verify_expired_token(self):
        """Test that expired token raises AuthException"""
        token = create_access_token(
            user_id="user-1",
            roles=["farmer"],
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "expired_token"

    def test_verify_invalid_signature(self):
        """Test that token with wrong signature is rejected"""
        token = jwt.encode(
            {
                "sub": "user-1",
                "roles": ["farmer"],
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "iat": datetime.now(UTC),
                "iss": config.JWT_ISSUER,
                "aud": config.JWT_AUDIENCE,
                "type": "access",
            },
            "wrong-secret-key-that-is-32-chars-long!!",
            algorithm="HS256",
        )
        with pytest.raises(AuthException):
            verify_token(token)

    def test_verify_malformed_token(self):
        """Test that malformed token is rejected"""
        with pytest.raises(AuthException):
            verify_token("not.a.valid.token")

    def test_verify_empty_token(self):
        """Test that empty token is rejected"""
        with pytest.raises(Exception):
            verify_token("")

    def test_verify_token_wrong_issuer(self):
        """Test that token with wrong issuer is rejected"""
        token = jwt.encode(
            {
                "sub": "user-1",
                "roles": ["farmer"],
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "iat": datetime.now(UTC),
                "iss": "wrong-issuer",
                "aud": config.JWT_AUDIENCE,
                "type": "access",
            },
            config.JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_issuer"

    def test_verify_token_wrong_audience(self):
        """Test that token with wrong audience is rejected"""
        token = jwt.encode(
            {
                "sub": "user-1",
                "roles": ["farmer"],
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "iat": datetime.now(UTC),
                "iss": config.JWT_ISSUER,
                "aud": "wrong-audience",
                "type": "access",
            },
            config.JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(AuthException) as exc_info:
            verify_token(token)
        assert exc_info.value.error.code == "invalid_audience"

    def test_verify_token_missing_sub(self):
        """Test that token without sub claim is rejected"""
        token = jwt.encode(
            {
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "iat": datetime.now(UTC),
                "iss": config.JWT_ISSUER,
                "aud": config.JWT_AUDIENCE,
                "type": "access",
            },
            config.JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(AuthException):
            verify_token(token)


@pytest.mark.unit
class TestAlgorithmConfusionPrevention:
    """Security tests for algorithm confusion attack prevention"""

    def test_allowed_algorithms_only_hs256(self):
        """Test that only HS256 is in the allowed algorithms list"""
        assert ALLOWED_ALGORITHMS == ["HS256"]

    def test_reject_none_algorithm(self):
        """Test that 'none' algorithm tokens are rejected"""
        # Create a token with 'none' algorithm header
        header = {"alg": "none", "typ": "JWT"}
        payload = {
            "sub": "attacker",
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
            "iss": config.JWT_ISSUER,
            "aud": config.JWT_AUDIENCE,
        }
        # Manually craft a none-algorithm token
        import base64
        import json

        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).decode().rstrip("=")
        fake_token = f"{header_b64}.{payload_b64}."

        with pytest.raises(AuthException):
            verify_token(fake_token)

    def test_reject_rs256_algorithm(self):
        """Test that RS256 algorithm tokens are rejected (algorithm confusion)"""
        # A token claiming to be RS256 should be rejected
        token = jwt.encode(
            {
                "sub": "user-1",
                "roles": ["admin"],
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "iat": datetime.now(UTC),
                "iss": config.JWT_ISSUER,
                "aud": config.JWT_AUDIENCE,
            },
            config.JWT_SECRET,
            algorithm="HS384",  # Not in allowed list
        )
        with pytest.raises(AuthException):
            verify_token(token)


@pytest.mark.unit
class TestDecodeToken:
    """Tests for decode_token (alias for verify_token)"""

    def test_decode_token_is_alias(self):
        """Test that decode_token works identically to verify_token"""
        token = create_access_token(user_id="user-1", roles=["farmer"])
        result1 = verify_token(token)
        result2 = decode_token(token)

        assert result1.user_id == result2.user_id
        assert result1.roles == result2.roles


@pytest.mark.unit
class TestDecodeTokenUnsafe:
    """Tests for unsafe token decoding (debug only)"""

    def test_decode_unsafe_returns_payload(self):
        """Test unsafe decode returns token payload without verification"""
        token = create_access_token(user_id="user-1", roles=["farmer"])
        result = decode_token_unsafe(token)
        assert result["sub"] == "user-1"
        assert result["roles"] == ["farmer"]

    def test_decode_unsafe_invalid_token_returns_empty(self):
        """Test unsafe decode returns empty dict for invalid tokens"""
        result = decode_token_unsafe("invalid-token")
        assert result == {}


@pytest.mark.unit
class TestCreateTokenPair:
    """Tests for token pair creation"""

    def test_create_token_pair_returns_both_tokens(self):
        """Test that token pair contains both access and refresh tokens"""
        pair = create_token_pair(user_id="user-1", roles=["farmer"])

        assert "access_token" in pair
        assert "refresh_token" in pair
        assert "token_type" in pair
        assert "expires_in" in pair

    def test_token_pair_type_is_bearer(self):
        """Test that token type is bearer"""
        pair = create_token_pair(user_id="user-1", roles=["farmer"])
        assert pair["token_type"] == "bearer"

    def test_token_pair_expires_in_seconds(self):
        """Test that expires_in is in seconds"""
        pair = create_token_pair(user_id="user-1", roles=["farmer"])
        expected_seconds = config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert pair["expires_in"] == expected_seconds

    def test_token_pair_tokens_are_valid(self):
        """Test that both tokens in the pair are valid"""
        pair = create_token_pair(
            user_id="user-1",
            roles=["farmer"],
            tenant_id="tenant-1",
            permissions=["farm:read"],
        )

        access_payload = verify_token(pair["access_token"])
        assert access_payload.user_id == "user-1"
        assert access_payload.token_type == "access"

        refresh_payload = verify_token(pair["refresh_token"])
        assert refresh_payload.user_id == "user-1"
        assert refresh_payload.token_type == "refresh"


@pytest.mark.unit
class TestRefreshAccessToken:
    """Tests for access token refresh flow"""

    def test_refresh_with_valid_refresh_token(self):
        """Test refreshing access token with valid refresh token"""
        refresh = create_refresh_token(user_id="user-1", tenant_id="tenant-1")
        new_access = refresh_access_token(
            refresh_token=refresh,
            roles=["farmer"],
            permissions=["farm:read"],
        )

        payload = verify_token(new_access)
        assert payload.user_id == "user-1"
        assert payload.roles == ["farmer"]
        assert payload.tenant_id == "tenant-1"
        assert payload.token_type == "access"

    def test_refresh_with_access_token_fails(self):
        """Test that using an access token as refresh token fails"""
        access = create_access_token(user_id="user-1", roles=["farmer"])
        with pytest.raises(AuthException):
            refresh_access_token(refresh_token=access, roles=["farmer"])

    def test_refresh_with_expired_refresh_token_fails(self):
        """Test that expired refresh token is rejected"""
        # Create a manually expired refresh token
        token = jwt.encode(
            {
                "sub": "user-1",
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "iat": datetime.now(UTC) - timedelta(days=8),
                "iss": config.JWT_ISSUER,
                "aud": config.JWT_AUDIENCE,
                "type": "refresh",
            },
            config.JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(AuthException):
            refresh_access_token(refresh_token=token, roles=["farmer"])
