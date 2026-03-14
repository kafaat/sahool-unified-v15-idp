"""
Comprehensive Auth Models Tests for SAHOOL Platform
اختبارات شاملة لنماذج المصادقة لمنصة سهول

Tests cover:
- Permission enum values
- TokenPayload dataclass
- User dataclass
- AuthErrorMessage
- AuthErrors constants
- AuthException
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from shared.auth.models import (
    AuthErrorMessage,
    AuthErrors,
    AuthException,
    Permission,
    TokenPayload,
    User,
)


@pytest.mark.unit
class TestPermission:
    """Tests for Permission enum"""

    def test_farm_permissions(self):
        """Test farm management permissions"""
        assert Permission.FARM_READ == "farm:read"
        assert Permission.FARM_WRITE == "farm:write"
        assert Permission.FARM_DELETE == "farm:delete"

    def test_field_permissions(self):
        """Test field management permissions"""
        assert Permission.FIELD_READ == "field:read"
        assert Permission.FIELD_WRITE == "field:write"
        assert Permission.FIELD_DELETE == "field:delete"

    def test_admin_permissions(self):
        """Test admin permissions"""
        assert Permission.ADMIN_ACCESS == "admin:access"
        assert Permission.ADMIN_SETTINGS == "admin:settings"
        assert Permission.ADMIN_BILLING == "admin:billing"

    def test_precision_agriculture_permissions(self):
        """Test precision agriculture permissions"""
        assert Permission.VRA_READ == "vra:read"
        assert Permission.VRA_WRITE == "vra:write"
        assert Permission.SPRAY_TIMING_READ == "spray:read"
        assert Permission.GDD_READ == "gdd:read"
        assert Permission.ROTATION_READ == "rotation:read"

    def test_permission_format(self):
        """Test all permissions follow domain:action format"""
        for perm in Permission:
            assert ":" in perm.value
            parts = perm.value.split(":")
            assert len(parts) == 2
            assert all(len(p) > 0 for p in parts)


@pytest.mark.unit
class TestTokenPayload:
    """Tests for TokenPayload dataclass"""

    def setup_method(self):
        """Set up common test data"""
        self.now = datetime.now(UTC)
        self.payload = TokenPayload(
            user_id="user-123",
            roles=["farmer", "admin"],
            exp=self.now + timedelta(hours=1),
            iat=self.now,
            tenant_id="tenant-456",
            jti="jti-789",
            token_type="access",
            permissions=["farm:read", "field:write"],
        )

    def test_basic_fields(self):
        """Test basic field access"""
        assert self.payload.user_id == "user-123"
        assert self.payload.roles == ["farmer", "admin"]
        assert self.payload.tenant_id == "tenant-456"
        assert self.payload.jti == "jti-789"
        assert self.payload.token_type == "access"

    def test_default_values(self):
        """Test default values for optional fields"""
        payload = TokenPayload(
            user_id="user-1",
            roles=["worker"],
            exp=self.now + timedelta(hours=1),
            iat=self.now,
        )
        assert payload.tenant_id is None
        assert payload.jti is None
        assert payload.token_type == "access"
        assert payload.permissions == []

    def test_has_role(self):
        """Test has_role method"""
        assert self.payload.has_role("farmer") is True
        assert self.payload.has_role("admin") is True
        assert self.payload.has_role("super_admin") is False

    def test_has_any_role(self):
        """Test has_any_role method"""
        assert self.payload.has_any_role("farmer", "super_admin") is True
        assert self.payload.has_any_role("super_admin", "moderator") is False

    def test_has_all_roles(self):
        """Test has_all_roles method"""
        assert self.payload.has_all_roles("farmer", "admin") is True
        assert self.payload.has_all_roles("farmer", "super_admin") is False

    def test_has_permission(self):
        """Test has_permission method"""
        assert self.payload.has_permission("farm:read") is True
        assert self.payload.has_permission("farm:delete") is False


@pytest.mark.unit
class TestUser:
    """Tests for User dataclass"""

    def setup_method(self):
        """Set up common test data"""
        self.user = User(
            id="user-1",
            email="farmer@sahool.app",
            roles=["farmer", "admin"],
            farm_ids=["farm-1", "farm-2"],
            tenant_id="tenant-1",
            permissions=["farm:read", "field:write"],
            is_active=True,
            is_verified=True,
        )

    def test_basic_fields(self):
        """Test basic user fields"""
        assert self.user.id == "user-1"
        assert self.user.email == "farmer@sahool.app"
        assert self.user.tenant_id == "tenant-1"

    def test_default_values(self):
        """Test default values"""
        user = User(id="u-1", email="test@test.com", roles=["worker"])
        assert user.farm_ids == []
        assert user.tenant_id is None
        assert user.permissions == []
        assert user.is_active is True
        assert user.is_verified is True

    def test_has_role(self):
        """Test has_role method"""
        assert self.user.has_role("farmer") is True
        assert self.user.has_role("super_admin") is False

    def test_has_any_role(self):
        """Test has_any_role method"""
        assert self.user.has_any_role("farmer", "worker") is True
        assert self.user.has_any_role("worker", "moderator") is False

    def test_has_all_roles(self):
        """Test has_all_roles method"""
        assert self.user.has_all_roles("farmer", "admin") is True
        assert self.user.has_all_roles("farmer", "worker") is False

    def test_has_farm_access(self):
        """Test has_farm_access method"""
        assert self.user.has_farm_access("farm-1") is True
        assert self.user.has_farm_access("farm-3") is False

    def test_has_permission(self):
        """Test has_permission method"""
        assert self.user.has_permission("farm:read") is True
        assert self.user.has_permission("admin:access") is False


@pytest.mark.unit
class TestAuthErrors:
    """Tests for AuthErrors constants"""

    def test_invalid_token_error(self):
        """Test invalid token error messages"""
        err = AuthErrors.INVALID_TOKEN
        assert isinstance(err, AuthErrorMessage)
        assert err.code == "invalid_token"
        assert "Invalid" in err.en
        assert "غير صالح" in err.ar

    def test_expired_token_error(self):
        """Test expired token error"""
        err = AuthErrors.EXPIRED_TOKEN
        assert err.code == "expired_token"
        assert "expired" in err.en.lower()
        assert "انتهت" in err.ar

    def test_missing_token_error(self):
        """Test missing token error"""
        err = AuthErrors.MISSING_TOKEN
        assert err.code == "missing_token"

    def test_insufficient_permissions_error(self):
        """Test insufficient permissions error"""
        err = AuthErrors.INSUFFICIENT_PERMISSIONS
        assert err.code == "insufficient_permissions"
        assert "permissions" in err.en.lower()

    def test_rate_limit_error(self):
        """Test rate limit error"""
        err = AuthErrors.RATE_LIMIT_EXCEEDED
        assert err.code == "rate_limit_exceeded"

    def test_all_errors_bilingual(self):
        """Test that all error messages have both EN and AR"""
        errors = [
            AuthErrors.INVALID_TOKEN,
            AuthErrors.EXPIRED_TOKEN,
            AuthErrors.MISSING_TOKEN,
            AuthErrors.INVALID_CREDENTIALS,
            AuthErrors.INSUFFICIENT_PERMISSIONS,
            AuthErrors.ACCOUNT_DISABLED,
            AuthErrors.ACCOUNT_NOT_VERIFIED,
            AuthErrors.TOKEN_REVOKED,
            AuthErrors.RATE_LIMIT_EXCEEDED,
            AuthErrors.INVALID_ISSUER,
            AuthErrors.INVALID_AUDIENCE,
        ]
        for err in errors:
            assert len(err.en) > 0
            assert len(err.ar) > 0
            assert len(err.code) > 0


@pytest.mark.unit
class TestAuthException:
    """Tests for AuthException"""

    def test_basic_exception(self):
        """Test creating a basic AuthException"""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        assert exc.error == AuthErrors.INVALID_TOKEN
        assert exc.status_code == 401
        assert exc.detail is None

    def test_exception_with_custom_status(self):
        """Test exception with custom status code"""
        exc = AuthException(AuthErrors.INSUFFICIENT_PERMISSIONS, status_code=403)
        assert exc.status_code == 403

    def test_exception_with_detail(self):
        """Test exception with detail message"""
        exc = AuthException(
            AuthErrors.INVALID_TOKEN,
            detail="Token signature mismatch",
        )
        assert exc.detail == "Token signature mismatch"

    def test_to_dict_english(self):
        """Test to_dict with English language"""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        result = exc.to_dict(lang="en")
        assert result["error"] == "invalid_token"
        assert result["message"] == AuthErrors.INVALID_TOKEN.en
        assert result["status_code"] == 401

    def test_to_dict_arabic(self):
        """Test to_dict with Arabic language"""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        result = exc.to_dict(lang="ar")
        assert result["message"] == AuthErrors.INVALID_TOKEN.ar

    def test_exception_string(self):
        """Test exception string representation"""
        exc = AuthException(AuthErrors.EXPIRED_TOKEN)
        assert str(exc) == AuthErrors.EXPIRED_TOKEN.en

    def test_exception_with_detail_string(self):
        """Test exception string with detail"""
        exc = AuthException(AuthErrors.INVALID_TOKEN, detail="Custom detail")
        assert str(exc) == "Custom detail"
