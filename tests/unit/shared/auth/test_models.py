"""
Tests for Authentication Models
================================
Tests for Permission enum, TokenPayload, User, AuthErrorMessage,
AuthErrors, and AuthException classes.
"""

from __future__ import annotations

from datetime import datetime, timezone, UTC

import pytest

from shared.auth.models import (
    AuthErrorMessage,
    AuthErrors,
    AuthException,
    Permission,
    TokenPayload,
    User,
)


# =============================================================================
# Permission Enum Tests
# =============================================================================


class TestPermission:
    """Test Permission enum values and behavior."""

    def test_permission_is_str_enum(self):
        """Permission values are strings."""
        assert isinstance(Permission.FARM_READ, str)
        assert Permission.FARM_READ == "farm:read"

    def test_farm_permissions(self):
        """Farm permissions follow naming convention."""
        assert Permission.FARM_READ == "farm:read"
        assert Permission.FARM_WRITE == "farm:write"
        assert Permission.FARM_DELETE == "farm:delete"

    def test_field_permissions(self):
        """Field permissions follow naming convention."""
        assert Permission.FIELD_READ == "field:read"
        assert Permission.FIELD_WRITE == "field:write"
        assert Permission.FIELD_DELETE == "field:delete"

    def test_crop_permissions(self):
        """Crop permissions follow naming convention."""
        assert Permission.CROP_READ == "crop:read"
        assert Permission.CROP_WRITE == "crop:write"
        assert Permission.CROP_DELETE == "crop:delete"

    def test_weather_permissions(self):
        """Weather permissions."""
        assert Permission.WEATHER_READ == "weather:read"
        assert Permission.WEATHER_SUBSCRIBE == "weather:subscribe"

    def test_advisory_permissions(self):
        """Advisory permissions."""
        assert Permission.ADVISORY_READ == "advisory:read"
        assert Permission.ADVISORY_REQUEST == "advisory:request"

    def test_admin_permissions(self):
        """Admin permissions."""
        assert Permission.ADMIN_ACCESS == "admin:access"
        assert Permission.ADMIN_SETTINGS == "admin:settings"
        assert Permission.ADMIN_BILLING == "admin:billing"

    def test_precision_agriculture_permissions(self):
        """Precision agriculture permissions exist."""
        assert Permission.VRA_READ == "vra:read"
        assert Permission.VRA_WRITE == "vra:write"
        assert Permission.SPRAY_TIMING_READ == "spray:read"
        assert Permission.SPRAY_TIMING_WRITE == "spray:write"
        assert Permission.GDD_READ == "gdd:read"
        assert Permission.ROTATION_READ == "rotation:read"
        assert Permission.ROTATION_WRITE == "rotation:write"
        assert Permission.PROFITABILITY_READ == "profitability:read"

    def test_permissions_use_colon_separator(self):
        """All permissions use domain:action format."""
        for perm in Permission:
            assert ":" in perm.value, f"{perm.name} missing colon separator"

    def test_permission_can_be_used_as_string(self):
        """Permission values work in string comparisons."""
        assert Permission.FARM_READ in ["farm:read", "farm:write"]
        assert str(Permission.FARM_READ) == "farm:read"


# =============================================================================
# TokenPayload Tests
# =============================================================================


class TestTokenPayload:
    """Test JWT TokenPayload dataclass."""

    @pytest.fixture
    def now(self):
        return datetime.now(UTC)

    @pytest.fixture
    def sample_payload(self, now):
        return TokenPayload(
            user_id="user-123",
            roles=["farmer", "admin"],
            exp=now,
            iat=now,
            tenant_id="tenant-456",
            jti="token-id-789",
            token_type="access",
            permissions=["farm:read", "farm:write"],
        )

    def test_basic_creation(self, now):
        """TokenPayload can be created with required fields."""
        payload = TokenPayload(
            user_id="user-123",
            roles=["farmer"],
            exp=now,
            iat=now,
        )
        assert payload.user_id == "user-123"
        assert payload.roles == ["farmer"]
        assert payload.exp == now
        assert payload.iat == now

    def test_defaults(self, now):
        """TokenPayload has correct default values."""
        payload = TokenPayload(
            user_id="u1",
            roles=[],
            exp=now,
            iat=now,
        )
        assert payload.tenant_id is None
        assert payload.jti is None
        assert payload.token_type == "access"
        assert payload.permissions == []

    def test_has_role_true(self, sample_payload):
        """has_role returns True for existing role."""
        assert sample_payload.has_role("farmer") is True
        assert sample_payload.has_role("admin") is True

    def test_has_role_false(self, sample_payload):
        """has_role returns False for non-existing role."""
        assert sample_payload.has_role("superadmin") is False

    def test_has_any_role_true(self, sample_payload):
        """has_any_role returns True when at least one role matches."""
        assert sample_payload.has_any_role("superadmin", "farmer") is True

    def test_has_any_role_false(self, sample_payload):
        """has_any_role returns False when no roles match."""
        assert sample_payload.has_any_role("superadmin", "viewer") is False

    def test_has_all_roles_true(self, sample_payload):
        """has_all_roles returns True when all roles match."""
        assert sample_payload.has_all_roles("farmer", "admin") is True

    def test_has_all_roles_false(self, sample_payload):
        """has_all_roles returns False when some roles are missing."""
        assert sample_payload.has_all_roles("farmer", "superadmin") is False

    def test_has_permission_true(self, sample_payload):
        """has_permission returns True for existing permission."""
        assert sample_payload.has_permission("farm:read") is True

    def test_has_permission_false(self, sample_payload):
        """has_permission returns False for non-existing permission."""
        assert sample_payload.has_permission("admin:access") is False

    def test_empty_roles(self, now):
        """TokenPayload works with empty roles list."""
        payload = TokenPayload(user_id="u1", roles=[], exp=now, iat=now)
        assert payload.has_role("anything") is False
        assert payload.has_any_role("a", "b") is False
        assert payload.has_all_roles() is True  # vacuously true

    def test_token_type_refresh(self, now):
        """TokenPayload supports refresh token type."""
        payload = TokenPayload(
            user_id="u1",
            roles=[],
            exp=now,
            iat=now,
            token_type="refresh",
        )
        assert payload.token_type == "refresh"


# =============================================================================
# User Tests
# =============================================================================


class TestUser:
    """Test User dataclass."""

    @pytest.fixture
    def sample_user(self):
        return User(
            id="user-001",
            email="farmer@sahool.app",
            roles=["farmer", "field_manager"],
            farm_ids=["farm-001", "farm-002"],
            tenant_id="tenant-001",
            permissions=["farm:read", "field:write"],
            is_active=True,
            is_verified=True,
        )

    def test_basic_creation(self):
        """User can be created with required fields."""
        user = User(
            id="u1",
            email="u@example.com",
            roles=["farmer"],
        )
        assert user.id == "u1"
        assert user.email == "u@example.com"
        assert user.roles == ["farmer"]

    def test_defaults(self):
        """User has correct default values."""
        user = User(id="u1", email="u@e.com", roles=[])
        assert user.farm_ids == []
        assert user.tenant_id is None
        assert user.permissions == []
        assert user.is_active is True
        assert user.is_verified is True

    def test_has_role_true(self, sample_user):
        """has_role returns True for existing role."""
        assert sample_user.has_role("farmer") is True

    def test_has_role_false(self, sample_user):
        """has_role returns False for non-existing role."""
        assert sample_user.has_role("admin") is False

    def test_has_any_role(self, sample_user):
        """has_any_role checks for any matching role."""
        assert sample_user.has_any_role("admin", "farmer") is True
        assert sample_user.has_any_role("admin", "viewer") is False

    def test_has_all_roles(self, sample_user):
        """has_all_roles checks all roles are present."""
        assert sample_user.has_all_roles("farmer", "field_manager") is True
        assert sample_user.has_all_roles("farmer", "admin") is False

    def test_has_farm_access_true(self, sample_user):
        """has_farm_access returns True for accessible farm."""
        assert sample_user.has_farm_access("farm-001") is True

    def test_has_farm_access_false(self, sample_user):
        """has_farm_access returns False for inaccessible farm."""
        assert sample_user.has_farm_access("farm-999") is False

    def test_has_permission_true(self, sample_user):
        """has_permission returns True for granted permission."""
        assert sample_user.has_permission("farm:read") is True

    def test_has_permission_false(self, sample_user):
        """has_permission returns False for missing permission."""
        assert sample_user.has_permission("admin:access") is False

    def test_inactive_user(self):
        """User can be marked inactive."""
        user = User(
            id="u1", email="u@e.com", roles=["farmer"], is_active=False
        )
        assert user.is_active is False

    def test_unverified_user(self):
        """User can be marked unverified."""
        user = User(
            id="u1", email="u@e.com", roles=["farmer"], is_verified=False
        )
        assert user.is_verified is False

    def test_empty_farm_ids(self):
        """User with no farms has no farm access."""
        user = User(id="u1", email="u@e.com", roles=[])
        assert user.has_farm_access("any-farm") is False


# =============================================================================
# AuthErrorMessage Tests
# =============================================================================


class TestAuthErrorMessage:
    """Test AuthErrorMessage dataclass."""

    def test_creation(self):
        """AuthErrorMessage can be created with all fields."""
        msg = AuthErrorMessage(
            en="Invalid token",
            ar="رمز غير صالح",
            code="invalid_token",
        )
        assert msg.en == "Invalid token"
        assert msg.ar == "رمز غير صالح"
        assert msg.code == "invalid_token"


# =============================================================================
# AuthErrors Tests
# =============================================================================


class TestAuthErrors:
    """Test predefined authentication error messages."""

    def test_invalid_token(self):
        """INVALID_TOKEN error message."""
        err = AuthErrors.INVALID_TOKEN
        assert err.code == "invalid_token"
        assert err.en != ""
        assert err.ar != ""

    def test_expired_token(self):
        """EXPIRED_TOKEN error message."""
        err = AuthErrors.EXPIRED_TOKEN
        assert err.code == "expired_token"

    def test_missing_token(self):
        """MISSING_TOKEN error message."""
        err = AuthErrors.MISSING_TOKEN
        assert err.code == "missing_token"

    def test_invalid_credentials(self):
        """INVALID_CREDENTIALS error message."""
        err = AuthErrors.INVALID_CREDENTIALS
        assert err.code == "invalid_credentials"

    def test_insufficient_permissions(self):
        """INSUFFICIENT_PERMISSIONS error message."""
        err = AuthErrors.INSUFFICIENT_PERMISSIONS
        assert err.code == "insufficient_permissions"

    def test_account_disabled(self):
        """ACCOUNT_DISABLED error message."""
        err = AuthErrors.ACCOUNT_DISABLED
        assert err.code == "account_disabled"

    def test_account_not_verified(self):
        """ACCOUNT_NOT_VERIFIED error message."""
        err = AuthErrors.ACCOUNT_NOT_VERIFIED
        assert err.code == "account_not_verified"

    def test_token_revoked(self):
        """TOKEN_REVOKED error message."""
        err = AuthErrors.TOKEN_REVOKED
        assert err.code == "token_revoked"

    def test_rate_limit_exceeded(self):
        """RATE_LIMIT_EXCEEDED error message."""
        err = AuthErrors.RATE_LIMIT_EXCEEDED
        assert err.code == "rate_limit_exceeded"

    def test_invalid_issuer(self):
        """INVALID_ISSUER error message."""
        err = AuthErrors.INVALID_ISSUER
        assert err.code == "invalid_issuer"

    def test_invalid_audience(self):
        """INVALID_AUDIENCE error message."""
        err = AuthErrors.INVALID_AUDIENCE
        assert err.code == "invalid_audience"

    def test_all_errors_have_bilingual_messages(self):
        """All error messages have both English and Arabic text."""
        for attr_name in dir(AuthErrors):
            attr = getattr(AuthErrors, attr_name)
            if isinstance(attr, AuthErrorMessage):
                assert attr.en, f"{attr_name} missing English message"
                assert attr.ar, f"{attr_name} missing Arabic message"
                assert attr.code, f"{attr_name} missing error code"


# =============================================================================
# AuthException Tests
# =============================================================================


class TestAuthException:
    """Test AuthException class."""

    def test_basic_creation(self):
        """AuthException can be created with an error message."""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        assert exc.error == AuthErrors.INVALID_TOKEN
        assert exc.status_code == 401
        assert str(exc) == AuthErrors.INVALID_TOKEN.en

    def test_custom_status_code(self):
        """AuthException can have a custom status code."""
        exc = AuthException(
            AuthErrors.INSUFFICIENT_PERMISSIONS, status_code=403
        )
        assert exc.status_code == 403

    def test_custom_detail(self):
        """AuthException can have custom detail text."""
        exc = AuthException(
            AuthErrors.INVALID_TOKEN, detail="Token has been tampered with"
        )
        assert str(exc) == "Token has been tampered with"
        assert exc.detail == "Token has been tampered with"

    def test_to_dict_english(self):
        """to_dict returns English message by default."""
        exc = AuthException(AuthErrors.EXPIRED_TOKEN)
        result = exc.to_dict(lang="en")
        assert result["error"] == "expired_token"
        assert result["message"] == AuthErrors.EXPIRED_TOKEN.en
        assert result["status_code"] == 401

    def test_to_dict_arabic(self):
        """to_dict returns Arabic message when lang='ar'."""
        exc = AuthException(AuthErrors.EXPIRED_TOKEN)
        result = exc.to_dict(lang="ar")
        assert result["message"] == AuthErrors.EXPIRED_TOKEN.ar

    def test_is_exception_subclass(self):
        """AuthException is a proper Exception subclass."""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        assert isinstance(exc, Exception)

    def test_default_detail_is_none(self):
        """Detail defaults to None when not provided."""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        assert exc.detail is None
