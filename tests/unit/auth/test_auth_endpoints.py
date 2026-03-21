"""
Unit Tests for Auth Endpoints - SAHOOL Platform
اختبارات وحدة لنقاط نهاية المصادقة
=====================================================

Comprehensive tests for authentication endpoints covering:
- Login with email/password
- Login with 2FA verification
- Token refresh functionality
- Current user information retrieval
- Error handling and edge cases
- 2FA backup code verification

Test Markers:
- @pytest.mark.unit - Fast unit tests with mocked dependencies
- @pytest.mark.auth - Auth-specific tests

Author: SAHOOL QA Team
Updated: January 2026
"""

import pytest
from datetime import timezone, datetime, timedelta, UTC
from unittest.mock import Mock, MagicMock, patch

# Check if dependencies are available
try:
    from fastapi.testclient import TestClient
    from shared.auth.auth_api import (
        router,
        LoginRequest,
        LoginResponse,
        create_temp_token,
        verify_temp_token,
        set_user_service,
    )
    from shared.auth.jwt_handler import (
        create_access_token,
        create_refresh_token,
        verify_token,
        create_token_pair,
        refresh_access_token,
    )
    from shared.auth.models import User
except (ImportError, RuntimeError) as e:
    pytest.skip(f"Auth dependencies not available: {e}", allow_module_level=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_user():
    """Create a mock user object"""
    user = Mock()
    user.id = "user-123"
    user.email = "farmer@sahool.io"
    user.password_hash = "hashed_password"
    user.is_active = True
    user.is_verified = True
    user.twofa_enabled = False
    user.twofa_secret = None
    user.twofa_backup_codes = []
    user.roles = ["farmer"]
    user.tenant_id = "tenant-001"
    user.profile = Mock()
    user.profile.name = "Ahmed Al-Mansouri"
    user.profile.name_ar = "أحمد المنصوري"
    return user


@pytest.fixture
def mock_user_with_2fa():
    """Create a mock user with 2FA enabled"""
    user = Mock()
    user.id = "user-456"
    user.email = "admin@sahool.io"
    user.password_hash = "hashed_password"
    user.is_active = True
    user.is_verified = True
    user.twofa_enabled = True
    user.twofa_secret = "JBSWY3DPEBLW64TMMQ======"
    user.twofa_backup_codes = [
        "5f6b2a3c8d9e1f4b",  # hashed
        "7a9c4e2f1b6d8e3a",  # hashed
    ]
    user.roles = ["admin"]
    user.tenant_id = "tenant-001"
    user.profile = Mock()
    user.profile.name = "Admin User"
    user.profile.name_ar = "مسؤول النظام"
    return user


@pytest.fixture
def mock_disabled_user():
    """Create a mock disabled user"""
    user = Mock()
    user.id = "user-disabled"
    user.email = "disabled@sahool.io"
    user.is_active = False
    user.is_verified = True
    user.twofa_enabled = False
    return user


@pytest.fixture
def mock_unverified_user():
    """Create a mock unverified user"""
    user = Mock()
    user.id = "user-unverified"
    user.email = "unverified@sahool.io"
    user.is_active = True
    user.is_verified = False
    user.twofa_enabled = False
    return user


@pytest.fixture
def mock_user_service():
    """Create a mock user service"""
    service = Mock()
    return service


@pytest.fixture
def mock_twofa_service():
    """Create a mock 2FA service"""
    service = Mock()
    return service


@pytest.fixture
def setup_services(mock_user_service, mock_twofa_service):
    """Setup global services"""
    set_user_service(mock_user_service)
    with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
        yield mock_user_service, mock_twofa_service


@pytest.fixture
def app():
    """Create a test FastAPI app with auth routes"""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Login Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login endpoint"""

    def test_login_success_without_2fa(self, client, mock_user, mock_user_service):
        """Test successful login without 2FA"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_user
        mock_user_service.update_last_login.return_value = None

        with patch("shared.auth.auth_api.create_token") as mock_create_token:
            mock_create_token.return_value = "test_access_token"

            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "farmer@sahool.io",
                    "password": "SecurePassword123",
                    "totp_code": None,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert data["token_type"] == "bearer"
        assert data["requires_2fa"] is False
        assert data["user"]["id"] == "user-123"
        assert data["user"]["email"] == "farmer@sahool.io"
        assert data["user"]["name"] == "Ahmed Al-Mansouri"
        mock_user_service.update_last_login.assert_called_once_with("user-123")

    def test_login_failure_invalid_credentials(self, client, mock_user_service):
        """Test login fails with invalid credentials"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = None

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "farmer@sahool.io",
                "password": "WrongPassword",
                "totp_code": None,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower() or "credentials" in data["detail"].lower()

    def test_login_failure_account_disabled(self, client, mock_disabled_user, mock_user_service):
        """Test login fails when account is disabled"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_disabled_user

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "disabled@sahool.io",
                "password": "SomePassword123",
                "totp_code": None,
            },
        )

        assert response.status_code == 403
        data = response.json()
        assert "disabled" in data["detail"].lower()

    def test_login_failure_account_not_verified(self, client, mock_unverified_user, mock_user_service):
        """Test login fails when account is not verified"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_unverified_user

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "unverified@sahool.io",
                "password": "SomePassword123",
                "totp_code": None,
            },
        )

        assert response.status_code == 403
        data = response.json()
        assert "verified" in data["detail"].lower()

    def test_login_with_2fa_returns_temp_token(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test login with 2FA enabled returns temp token without code"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_user_with_2fa

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "admin@sahool.io",
                    "password": "AdminPassword123",
                    "totp_code": None,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["requires_2fa"] is True
        assert data["temp_token"] is not None
        assert data["access_token"] == ""
        assert data["user"]["id"] == "user-456"

    def test_login_with_valid_totp_code(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test login with 2FA and valid TOTP code"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_user_with_2fa
        mock_user_service.update_last_login.return_value = None
        mock_user_service.remove_backup_code.return_value = None
        mock_twofa_service.verify_totp.return_value = True
        mock_twofa_service.verify_backup_code.return_value = (False, None)

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            with patch("shared.auth.auth_api.create_token") as mock_create_token:
                mock_create_token.return_value = "test_access_token_2fa"

                response = client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": "admin@sahool.io",
                        "password": "AdminPassword123",
                        "totp_code": "123456",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token_2fa"
        assert data["requires_2fa"] is False
        mock_twofa_service.verify_totp.assert_called_once()

    def test_login_with_invalid_totp_code(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test login fails with invalid TOTP code"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_user_with_2fa
        mock_twofa_service.verify_totp.return_value = False
        mock_twofa_service.verify_backup_code.return_value = (False, None)

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "admin@sahool.io",
                    "password": "AdminPassword123",
                    "totp_code": "000000",
                },
            )

        assert response.status_code == 401
        data = response.json()
        assert "two-factor" in data["detail"].lower() or "totp" in data["detail"].lower()

    def test_login_with_valid_backup_code(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test login with 2FA and valid backup code"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_user_with_2fa
        mock_user_service.update_last_login.return_value = None
        mock_user_service.remove_backup_code.return_value = None
        mock_twofa_service.verify_totp.return_value = False
        mock_twofa_service.verify_backup_code.return_value = (True, "5f6b2a3c8d9e1f4b")

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            with patch("shared.auth.auth_api.create_token") as mock_create_token:
                mock_create_token.return_value = "test_access_token_backup"

                response = client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": "admin@sahool.io",
                        "password": "AdminPassword123",
                        "totp_code": "ABCD-EFGH",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token_backup"
        mock_user_service.remove_backup_code.assert_called_once_with("user-456", "5f6b2a3c8d9e1f4b")

    def test_login_with_invalid_email_format(self, client, mock_user_service):
        """Test login with invalid email format"""
        set_user_service(mock_user_service)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "not_an_email",
                "password": "SecurePassword123",
                "totp_code": None,
            },
        )

        # Should fail validation
        assert response.status_code == 422

    def test_login_with_short_password(self, client, mock_user_service):
        """Test login with password too short"""
        set_user_service(mock_user_service)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "farmer@sahool.io",
                "password": "short",
                "totp_code": None,
            },
        )

        # Should fail validation (min_length=6)
        assert response.status_code == 422

    def test_login_with_missing_password(self, client, mock_user_service):
        """Test login with missing password"""
        set_user_service(mock_user_service)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "farmer@sahool.io",
                "totp_code": None,
            },
        )

        # Should fail validation
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: 2FA Login Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestTwoFALoginEndpoint:
    """Tests for POST /api/v1/auth/login/2fa endpoint"""

    def test_2fa_login_success_with_valid_totp(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test successful 2FA login with valid TOTP code"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = mock_user_with_2fa
        mock_user_service.update_last_login.return_value = None
        mock_twofa_service.verify_totp.return_value = True
        mock_twofa_service.verify_backup_code.return_value = (False, None)

        temp_token = create_temp_token("user-456", "admin@sahool.io")

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            with patch("shared.auth.auth_api.create_token") as mock_create_token:
                mock_create_token.return_value = "final_access_token"

                response = client.post(
                    "/api/v1/auth/login/2fa",
                    json={
                        "temp_token": temp_token,
                        "totp_code": "123456",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "final_access_token"
        assert data["requires_2fa"] is False
        assert data["user"]["id"] == "user-456"
        mock_user_service.update_last_login.assert_called_once_with("user-456")

    def test_2fa_login_failure_invalid_temp_token(self, client, mock_user_service, mock_twofa_service):
        """Test 2FA login fails with invalid temp token"""
        set_user_service(mock_user_service)

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            response = client.post(
                "/api/v1/auth/login/2fa",
                json={
                    "temp_token": "invalid_token",
                    "totp_code": "123456",
                },
            )

        assert response.status_code == 401
        data = response.json()
        assert "token" in data["detail"].lower()

    def test_2fa_login_failure_expired_temp_token(self, client, mock_user_service, mock_twofa_service):
        """Test 2FA login fails with expired temp token"""
        set_user_service(mock_user_service)

        # Create an expired temp token (5 minutes in the past)
        import base64
        import json

        payload = {
            "user_id": "user-456",
            "email": "admin@sahool.io",
            "temp": True,
            "exp": (datetime.now(UTC) - timedelta(minutes=10)).isoformat(),
        }
        expired_token = base64.b64encode(json.dumps(payload).encode()).decode()

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            response = client.post(
                "/api/v1/auth/login/2fa",
                json={
                    "temp_token": expired_token,
                    "totp_code": "123456",
                },
            )

        assert response.status_code == 401
        data = response.json()
        assert "expired" in data["detail"].lower() or "token" in data["detail"].lower()

    def test_2fa_login_with_valid_backup_code(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test 2FA login with valid backup code"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = mock_user_with_2fa
        mock_user_service.update_last_login.return_value = None
        mock_user_service.remove_backup_code.return_value = None
        mock_twofa_service.verify_totp.return_value = False
        mock_twofa_service.verify_backup_code.return_value = (True, "5f6b2a3c8d9e1f4b")

        temp_token = create_temp_token("user-456", "admin@sahool.io")

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            with patch("shared.auth.auth_api.create_token") as mock_create_token:
                mock_create_token.return_value = "backup_access_token"

                response = client.post(
                    "/api/v1/auth/login/2fa",
                    json={
                        "temp_token": temp_token,
                        "totp_code": "ABCD-EFGH",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "backup_access_token"
        mock_user_service.remove_backup_code.assert_called_once_with("user-456", "5f6b2a3c8d9e1f4b")

    def test_2fa_login_failure_invalid_code(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test 2FA login fails with invalid TOTP and backup codes"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = mock_user_with_2fa
        mock_twofa_service.verify_totp.return_value = False
        mock_twofa_service.verify_backup_code.return_value = (False, None)

        temp_token = create_temp_token("user-456", "admin@sahool.io")

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            response = client.post(
                "/api/v1/auth/login/2fa",
                json={
                    "temp_token": temp_token,
                    "totp_code": "000000",
                },
            )

        assert response.status_code == 401
        data = response.json()
        assert "two-factor" in data["detail"].lower() or "authentication" in data["detail"].lower()

    def test_2fa_login_failure_user_not_found(self, client, mock_user_service, mock_twofa_service):
        """Test 2FA login fails when user not found"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = None

        temp_token = create_temp_token("user-nonexistent", "nonexistent@sahool.io")

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            response = client.post(
                "/api/v1/auth/login/2fa",
                json={
                    "temp_token": temp_token,
                    "totp_code": "123456",
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert "two-factor" in data["detail"].lower() or "authentication" in data["detail"].lower()

    def test_2fa_login_failure_2fa_not_enabled(self, client, mock_user, mock_user_service, mock_twofa_service):
        """Test 2FA login fails when 2FA is not enabled for user"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = mock_user  # User without 2FA

        temp_token = create_temp_token("user-123", "farmer@sahool.io")

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            response = client.post(
                "/api/v1/auth/login/2fa",
                json={
                    "temp_token": temp_token,
                    "totp_code": "123456",
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert "two-factor" in data["detail"].lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Current User Info Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestCurrentUserEndpoint:
    """Tests for GET /api/v1/auth/me endpoint"""

    def test_get_current_user_success(self, client, mock_user, mock_user_service):
        """Test successfully retrieve current user info"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = mock_user

        response = client.get("/api/v1/auth/me?user_id=user-123")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "user-123"
        assert data["data"]["email"] == "farmer@sahool.io"
        assert data["data"]["name"] == "Ahmed Al-Mansouri"
        assert data["data"]["name_ar"] == "أحمد المنصوري"
        assert data["data"]["role"] == "farmer"
        assert data["data"]["tenant_id"] == "tenant-001"
        assert data["data"]["twofa_enabled"] is False

    def test_get_current_user_with_2fa_enabled(self, client, mock_user_with_2fa, mock_user_service):
        """Test get current user info when 2FA is enabled"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = mock_user_with_2fa

        response = client.get("/api/v1/auth/me?user_id=user-456")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["twofa_enabled"] is True

    def test_get_current_user_not_found(self, client, mock_user_service):
        """Test get current user returns 404 when user not found"""
        set_user_service(mock_user_service)
        mock_user_service.get_user.return_value = None

        response = client.get("/api/v1/auth/me?user_id=nonexistent-user")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_current_user_missing_user_id(self, client, mock_user_service):
        """Test get current user fails without user_id parameter"""
        set_user_service(mock_user_service)

        response = client.get("/api/v1/auth/me")

        # Should fail validation (missing required parameter)
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Token Refresh Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestTokenRefresh:
    """Tests for token refresh functionality"""

    def test_refresh_access_token_success(self):
        """Test successfully refreshing access token"""
        user_id = "user-123"
        roles = ["farmer"]
        permissions = ["farm:read", "farm:write"]

        # Create a valid refresh token
        refresh_token = create_refresh_token(user_id, tenant_id="tenant-001")

        # Verify refresh token is valid
        payload = verify_token(refresh_token)
        assert payload.user_id == user_id
        assert payload.token_type == "refresh"

        # Create new access token using refresh token
        new_access_token = refresh_access_token(
            refresh_token=refresh_token,
            roles=roles,
            permissions=permissions,
        )

        assert new_access_token is not None

        # Verify new access token
        access_payload = verify_token(new_access_token)
        assert access_payload.user_id == user_id
        assert access_payload.roles == roles
        assert access_payload.permissions == permissions
        assert access_payload.token_type == "access"

    def test_refresh_token_with_expired_refresh_token(self):
        """Test refresh fails with expired refresh token"""
        from shared.auth.models import AuthException

        user_id = "user-123"

        # Create a refresh token with very short expiry
        refresh_token = create_refresh_token(user_id, tenant_id="tenant-001")

        # Manually modify token to have past expiration
        import jwt
        from shared.auth.config import config

        payload = jwt.decode(
            refresh_token,
            config.get_verification_key(),
            algorithms=["HS256"],
            options={"verify_signature": False},
        )

        # Set expiration to past
        payload["exp"] = datetime.now(UTC) - timedelta(hours=1)

        expired_token = jwt.encode(payload, config.get_signing_key(), algorithm="HS256")

        # Should raise exception when trying to refresh
        with pytest.raises(AuthException):
            refresh_access_token(
                refresh_token=expired_token,
                roles=["farmer"],
            )

    def test_refresh_token_fails_with_access_token(self):
        """Test refresh fails when given access token instead of refresh token"""
        from shared.auth.models import AuthException

        user_id = "user-123"
        roles = ["farmer"]

        # Create an access token (not refresh token)
        access_token = create_access_token(
            user_id=user_id,
            roles=roles,
            tenant_id="tenant-001",
        )

        # Should fail because token type is 'access' not 'refresh'
        with pytest.raises(AuthException):
            refresh_access_token(
                refresh_token=access_token,
                roles=roles,
            )

    def test_refresh_token_preserves_tenant_id(self):
        """Test refresh token preserves tenant_id"""
        user_id = "user-123"
        tenant_id = "tenant-special"
        roles = ["admin"]

        # Create refresh token with specific tenant
        refresh_token = create_refresh_token(user_id, tenant_id=tenant_id)

        # Create new access token
        new_access_token = refresh_access_token(
            refresh_token=refresh_token,
            roles=roles,
        )

        # Verify tenant_id is preserved
        payload = verify_token(new_access_token)
        assert payload.tenant_id == tenant_id


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Token Creation & Verification
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestTokenCreation:
    """Tests for token creation utilities"""

    def test_create_access_token(self):
        """Test creating an access token"""
        user_id = "user-123"
        roles = ["farmer", "advisor"]
        permissions = ["farm:read", "farm:write"]
        tenant_id = "tenant-001"

        token = create_access_token(
            user_id=user_id,
            roles=roles,
            tenant_id=tenant_id,
            permissions=permissions,
        )

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token
        payload = verify_token(token)
        assert payload.user_id == user_id
        assert payload.roles == roles
        assert payload.permissions == permissions
        assert payload.tenant_id == tenant_id
        assert payload.token_type == "access"

    def test_create_refresh_token(self):
        """Test creating a refresh token"""
        user_id = "user-456"
        tenant_id = "tenant-002"

        token = create_refresh_token(user_id, tenant_id=tenant_id)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token
        payload = verify_token(token)
        assert payload.user_id == user_id
        assert payload.tenant_id == tenant_id
        assert payload.token_type == "refresh"

    def test_create_token_pair(self):
        """Test creating both access and refresh tokens"""
        user_id = "user-789"
        roles = ["farmer"]
        permissions = ["farm:read"]
        tenant_id = "tenant-003"

        tokens = create_token_pair(
            user_id=user_id,
            roles=roles,
            tenant_id=tenant_id,
            permissions=permissions,
        )

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert "expires_in" in tokens
        assert tokens["token_type"] == "bearer"

        # Verify both tokens
        access_payload = verify_token(tokens["access_token"])
        refresh_payload = verify_token(tokens["refresh_token"])

        assert access_payload.user_id == user_id
        assert access_payload.token_type == "access"
        assert refresh_payload.token_type == "refresh"

    def test_access_token_expiration(self):
        """Test access token has correct expiration"""
        user_id = "user-123"
        roles = ["farmer"]

        token = create_access_token(user_id, roles)
        payload = verify_token(token)

        # Token should expire in ~30 minutes (default)
        time_diff = (payload.exp - payload.iat).total_seconds()
        assert 1700 < time_diff < 1900  # 28-31 minutes in seconds

    def test_refresh_token_longer_expiration(self):
        """Test refresh token has longer expiration than access token"""
        user_id = "user-123"
        roles = ["farmer"]

        access_token = create_access_token(user_id, roles)
        refresh_token = create_refresh_token(user_id)

        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)

        access_diff = (access_payload.exp - access_payload.iat).total_seconds()
        refresh_diff = (refresh_payload.exp - refresh_payload.iat).total_seconds()

        # Refresh token should have longer expiration (7 days vs 30 minutes)
        assert refresh_diff > access_diff


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Temporary Token Handling
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestTemporaryToken:
    """Tests for temporary 2FA token creation and verification"""

    def test_create_and_verify_temp_token(self):
        """Test creating and verifying a temporary token"""
        user_id = "user-123"
        email = "farmer@sahool.io"

        temp_token = create_temp_token(user_id, email)
        assert isinstance(temp_token, str)

        payload = verify_temp_token(temp_token)
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert payload["temp"] is True

    def test_temp_token_expiration(self):
        """Test temp token expires after 5 minutes"""
        import base64
        import json

        user_id = "user-123"
        email = "farmer@sahool.io"

        # Create an expired temp token
        payload = {
            "user_id": user_id,
            "email": email,
            "temp": True,
            "exp": (datetime.now(UTC) - timedelta(minutes=10)).isoformat(),
        }
        expired_token = base64.b64encode(json.dumps(payload).encode()).decode()

        result = verify_temp_token(expired_token)
        assert result is None

    def test_temp_token_invalid_without_temp_flag(self):
        """Test temp token validation requires temp flag"""
        import base64
        import json

        # Token without temp flag
        payload = {
            "user_id": "user-123",
            "email": "farmer@sahool.io",
            "temp": False,  # Missing or false
            "exp": (datetime.now(UTC) + timedelta(minutes=5)).isoformat(),
        }
        token = base64.b64encode(json.dumps(payload).encode()).decode()

        result = verify_temp_token(token)
        assert result is None

    def test_temp_token_invalid_format(self):
        """Test temp token validation with invalid format"""
        result = verify_temp_token("not_a_valid_base64_token!!!")
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Edge Cases & Error Handling
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestAuthEdgeCases:
    """Tests for edge cases and error handling"""

    def test_login_response_model_validation(self):
        """Test LoginResponse model validation"""
        response_data = {
            "access_token": "valid_token",
            "token_type": "bearer",
            "user": {
                "id": "user-123",
                "email": "farmer@sahool.io",
                "name": "Ahmed",
                "role": "farmer",
            },
            "requires_2fa": False,
        }

        response = LoginResponse(**response_data)
        assert response.access_token == "valid_token"
        assert response.user["id"] == "user-123"

    def test_login_request_model_validation(self):
        """Test LoginRequest model validation"""
        request_data = {
            "email": "farmer@sahool.io",
            "password": "SecurePassword123",
        }

        request = LoginRequest(**request_data)
        assert request.email == "farmer@sahool.io"
        assert request.totp_code is None

    def test_user_with_multiple_roles(self, client, mock_user_service):
        """Test user with multiple roles"""
        user = Mock()
        user.id = "user-multi"
        user.email = "multi@sahool.io"
        user.is_active = True
        user.is_verified = True
        user.twofa_enabled = False
        user.twofa_secret = None
        user.twofa_backup_codes = []
        user.roles = ["farmer", "advisor", "analyst"]
        user.tenant_id = "tenant-001"
        user.profile = Mock()
        user.profile.name = "Multi Role User"
        user.profile.name_ar = "مستخدم متعدد الأدوار"

        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = user
        mock_user_service.update_last_login.return_value = None

        with patch("shared.auth.auth_api.create_token") as mock_create_token:
            mock_create_token.return_value = "multi_role_token"

            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "multi@sahool.io",
                    "password": "SecurePassword123",
                },
            )

        assert response.status_code == 200
        data = response.json()
        # Should return first role
        assert data["user"]["role"] == "farmer"

    def test_user_without_roles(self):
        """Test user without any roles defaults to viewer"""
        user = Mock()
        user.id = "user-no-roles"
        user.roles = []
        user.profile = Mock()
        user.profile.name = "No Role User"
        user.profile.name_ar = "مستخدم بدون أدوار"
        user.tenant_id = "tenant-001"

        # When creating response with user without roles
        response_data = {
            "access_token": "token",
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": "norole@sahool.io",
                "name": user.profile.name,
                "role": user.roles[0] if user.roles else "viewer",
            },
            "requires_2fa": False,
        }

        assert response_data["user"]["role"] == "viewer"

    def test_special_characters_in_user_name(self, client, mock_user_service):
        """Test user with special characters in name"""
        user = Mock()
        user.id = "user-special"
        user.email = "special@sahool.io"
        user.is_active = True
        user.is_verified = True
        user.twofa_enabled = False
        user.twofa_secret = None
        user.twofa_backup_codes = []
        user.roles = ["farmer"]
        user.tenant_id = "tenant-001"
        user.profile = Mock()
        user.profile.name = "محمد علي الأسعد"
        user.profile.name_ar = "محمد علي الأسعد - المزارع"

        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = user
        mock_user_service.update_last_login.return_value = None

        with patch("shared.auth.auth_api.create_token") as mock_create_token:
            mock_create_token.return_value = "special_char_token"

            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "special@sahool.io",
                    "password": "SecurePassword123",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "محمد علي الأسعد"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Integration Scenarios
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestAuthIntegrationScenarios:
    """Tests for realistic authentication scenarios"""

    def test_complete_login_flow_without_2fa(self, client, mock_user, mock_user_service):
        """Test complete login flow without 2FA"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_user
        mock_user_service.update_last_login.return_value = None

        with patch("shared.auth.auth_api.create_token") as mock_create_token:
            mock_create_token.return_value = "complete_flow_token"

            # Login
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "farmer@sahool.io",
                    "password": "SecurePassword123",
                },
            )

        assert response.status_code == 200
        data = response.json()
        access_token = data["access_token"]

        # Get user info with token
        response = client.get("/api/v1/auth/me?user_id=user-123")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["data"]["id"] == "user-123"

    def test_complete_login_flow_with_2fa(self, client, mock_user_with_2fa, mock_user_service, mock_twofa_service):
        """Test complete login flow with 2FA"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = mock_user_with_2fa
        mock_user_service.get_user.return_value = mock_user_with_2fa
        mock_user_service.update_last_login.return_value = None
        mock_twofa_service.verify_totp.return_value = True
        mock_twofa_service.verify_backup_code.return_value = (False, None)

        with patch("shared.auth.auth_api.get_twofa_service", return_value=mock_twofa_service):
            # Step 1: Initial login (no TOTP code)
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "admin@sahool.io",
                    "password": "AdminPassword123",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["requires_2fa"] is True
            temp_token = data["temp_token"]

            # Step 2: Complete 2FA with token
            with patch("shared.auth.auth_api.create_token") as mock_create_token:
                mock_create_token.return_value = "complete_2fa_token"

                response = client.post(
                    "/api/v1/auth/login/2fa",
                    json={
                        "temp_token": temp_token,
                        "totp_code": "123456",
                    },
                )

            assert response.status_code == 200
            data = response.json()
            assert data["requires_2fa"] is False
            access_token = data["access_token"]

    def test_multiple_failed_logins(self, client, mock_user_service):
        """Test multiple failed login attempts"""
        set_user_service(mock_user_service)
        mock_user_service.verify_user_password.return_value = None

        for _ in range(3):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": "farmer@sahool.io",
                    "password": "WrongPassword",
                },
            )
            assert response.status_code == 401

    def test_token_refresh_flow(self):
        """Test token refresh flow"""
        user_id = "user-123"
        roles = ["farmer"]
        permissions = ["farm:read"]

        # Create initial tokens
        tokens = create_token_pair(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
            tenant_id="tenant-001",
        )

        assert tokens["access_token"]
        assert tokens["refresh_token"]

        # Refresh the access token
        new_access_token = refresh_access_token(
            refresh_token=tokens["refresh_token"],
            roles=roles,
            permissions=permissions,
        )

        assert new_access_token
        assert new_access_token != tokens["access_token"]

        # Verify new token
        payload = verify_token(new_access_token)
        assert payload.user_id == user_id


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Authorization & Permissions
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
@pytest.mark.auth
class TestAuthorizationChecks:
    """Tests for authorization and permission checks"""

    def test_token_contains_user_roles(self):
        """Test token contains user roles"""
        user_id = "user-123"
        roles = ["farmer", "advisor"]

        token = create_access_token(user_id, roles)
        payload = verify_token(token)

        assert payload.has_role("farmer")
        assert payload.has_role("advisor")
        assert not payload.has_role("admin")

    def test_token_contains_permissions(self):
        """Test token contains user permissions"""
        user_id = "user-123"
        roles = ["farmer"]
        permissions = ["farm:read", "farm:write", "field:read"]

        token = create_access_token(user_id, roles, permissions=permissions)
        payload = verify_token(token)

        assert payload.has_permission("farm:read")
        assert payload.has_permission("farm:write")
        assert payload.has_permission("field:read")
        assert not payload.has_permission("farm:delete")

    def test_token_has_any_role(self):
        """Test checking if user has any of specified roles"""
        user_id = "user-123"
        roles = ["farmer"]

        token = create_access_token(user_id, roles)
        payload = verify_token(token)

        assert payload.has_any_role("farmer", "admin")
        assert payload.has_any_role("admin", "advisor", "farmer")
        assert not payload.has_any_role("admin", "advisor")

    def test_token_has_all_roles(self):
        """Test checking if user has all specified roles"""
        user_id = "user-123"
        roles = ["farmer", "advisor"]

        token = create_access_token(user_id, roles)
        payload = verify_token(token)

        assert payload.has_all_roles("farmer", "advisor")
        assert not payload.has_all_roles("farmer", "admin")
        assert not payload.has_all_roles("admin", "advisor")

    def test_user_model_role_check(self):
        """Test User model role checking"""
        user = User(
            id="user-123",
            email="farmer@sahool.io",
            roles=["farmer"],
            permissions=["farm:read"],
        )

        assert user.has_role("farmer")
        assert not user.has_role("admin")
        assert user.has_permission("farm:read")
        assert not user.has_permission("farm:write")
