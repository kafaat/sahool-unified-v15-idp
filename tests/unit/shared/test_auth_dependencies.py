"""
Unit tests for shared/auth/dependencies.py
Tests FastAPI authentication dependencies and rate limiting.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import time

# Set test environment before imports
import os
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"

from shared.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    require_roles,
    require_permissions,
    require_farm_access,
    rate_limit_dependency,
    get_optional_user,
    RateLimiter,
)
from shared.auth.jwt_handler import create_access_token
from shared.auth.models import User, AuthErrors


@pytest.fixture
def valid_token():
    """Create a valid access token for testing."""
    return create_access_token(
        user_id="user123",
        roles=["farmer", "admin"],
        tenant_id="tenant456",
        permissions=["farm:read", "farm:write"],
    )


@pytest.fixture
def valid_credentials(valid_token):
    """Create valid HTTP credentials."""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request."""
    request = MagicMock()
    request.state = MagicMock()
    request.path_params = {"farm_id": "farm123"}
    return request


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_missing_credentials_raises_401(self):
        """Test that missing credentials raises 401."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None, request=None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == AuthErrors.MISSING_TOKEN.en

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        """Test that invalid token raises 401."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here",
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, request=None)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_valid_token_returns_user(
        self, mock_repo, mock_cache, valid_credentials, mock_request
    ):
        """Test that valid token returns user."""
        mock_cache.return_value = None  # No cache
        mock_repo.return_value = None  # No repository

        user = await get_current_user(
            credentials=valid_credentials,
            request=mock_request,
        )

        assert user.id == "user123"
        assert "farmer" in user.roles
        assert "admin" in user.roles

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_user_stored_in_request_state(
        self, mock_repo, mock_cache, valid_credentials, mock_request
    ):
        """Test that user is stored in request state."""
        mock_cache.return_value = None
        mock_repo.return_value = None

        user = await get_current_user(
            credentials=valid_credentials,
            request=mock_request,
        )

        assert mock_request.state.user == user

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_cached_inactive_user_raises_403(self, mock_repo, mock_cache, valid_credentials):
        """Test that inactive cached user raises 403."""
        cache = AsyncMock()
        cache.get_user_status.return_value = {
            "is_active": False,
            "is_verified": True,
        }
        mock_cache.return_value = cache
        mock_repo.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=valid_credentials, request=None)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == AuthErrors.ACCOUNT_DISABLED.en


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_active_user_passes(self):
        """Test that active user passes."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["farmer"],
            is_active=True,
        )

        result = await get_current_active_user(user=user)

        assert result == user

    @pytest.mark.asyncio
    async def test_inactive_user_raises_403(self):
        """Test that inactive user raises 403."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["farmer"],
            is_active=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(user=user)

        assert exc_info.value.status_code == 403


class TestRequireRoles:
    """Tests for require_roles dependency factory."""

    @pytest.mark.asyncio
    async def test_user_with_required_role_passes(self):
        """Test that user with required role passes."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["admin"],
            is_active=True,
        )

        checker = require_roles("admin")

        with patch.object(
            type(user), "has_any_role", return_value=True
        ):
            # Mock the dependency chain
            with patch(
                "shared.auth.dependencies.get_current_active_user",
                return_value=user,
            ):
                result = await checker(user=user)
                assert result == user

    @pytest.mark.asyncio
    async def test_user_without_required_role_raises_403(self):
        """Test that user without required role raises 403."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["farmer"],
            is_active=True,
        )

        checker = require_roles("admin")

        with pytest.raises(HTTPException) as exc_info:
            await checker(user=user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_user_with_one_of_multiple_roles_passes(self):
        """Test that user with at least one required role passes."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["manager"],
            is_active=True,
        )

        checker = require_roles("admin", "manager")

        result = await checker(user=user)
        assert result == user


class TestRequirePermissions:
    """Tests for require_permissions dependency factory."""

    @pytest.mark.asyncio
    async def test_user_with_permission_passes(self):
        """Test that user with required permission passes."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["farmer"],
            permissions=["farm:read"],
            is_active=True,
        )

        checker = require_permissions("farm:read")

        result = await checker(user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_user_without_permission_raises_403(self):
        """Test that user without required permission raises 403."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["farmer"],
            permissions=["farm:read"],
            is_active=True,
        )

        checker = require_permissions("farm:delete")

        with pytest.raises(HTTPException) as exc_info:
            await checker(user=user)

        assert exc_info.value.status_code == 403


class TestRequireFarmAccess:
    """Tests for require_farm_access dependency factory."""

    @pytest.mark.asyncio
    async def test_admin_has_access_to_all_farms(self):
        """Test that admin user has access to all farms."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["admin"],
            is_active=True,
        )

        request = MagicMock()
        request.path_params = {"farm_id": "any_farm"}

        checker = require_farm_access()

        result = await checker(request=request, user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_missing_farm_id_raises_400(self):
        """Test that missing farm_id raises 400."""
        user = User(
            id="user123",
            email="test@example.com",
            roles=["farmer"],
            is_active=True,
        )

        request = MagicMock()
        request.path_params = {}

        checker = require_farm_access()

        with pytest.raises(HTTPException) as exc_info:
            await checker(request=request, user=user)

        assert exc_info.value.status_code == 400


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allows_requests_under_limit(self):
        """Test that requests under limit are allowed."""
        limiter = RateLimiter(requests=5, window_seconds=60)

        for i in range(5):
            allowed, remaining = limiter.is_allowed("user123")
            assert allowed is True
            assert remaining == 5 - i - 1

    def test_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked."""
        limiter = RateLimiter(requests=3, window_seconds=60)

        # Use up the limit
        for _ in range(3):
            limiter.is_allowed("user123")

        # This should be blocked
        allowed, remaining = limiter.is_allowed("user123")

        assert allowed is False
        assert remaining == 0

    def test_tracks_violations(self):
        """Test that violations are tracked."""
        limiter = RateLimiter(requests=1, window_seconds=60)

        limiter.is_allowed("user123")
        limiter.is_allowed("user123")  # First violation
        limiter.is_allowed("user123")  # Second violation

        assert limiter.get_violation_count("user123") == 2

    def test_reset_violations(self):
        """Test that violations can be reset."""
        limiter = RateLimiter(requests=1, window_seconds=60)

        limiter.is_allowed("user123")
        limiter.is_allowed("user123")  # Violation

        limiter.reset_violations("user123")

        assert limiter.get_violation_count("user123") == 0

    def test_window_expiration(self):
        """Test that old requests expire after window."""
        limiter = RateLimiter(requests=2, window_seconds=1)

        limiter.is_allowed("user123")
        limiter.is_allowed("user123")

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        allowed, remaining = limiter.is_allowed("user123")
        assert allowed is True

    def test_separate_limits_per_user(self):
        """Test that each user has separate limit."""
        limiter = RateLimiter(requests=2, window_seconds=60)

        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        limiter.is_allowed("user2")

        allowed1, _ = limiter.is_allowed("user1")
        allowed2, _ = limiter.is_allowed("user2")

        assert allowed1 is False  # User1 hit limit
        assert allowed2 is True  # User2 still has quota


class TestGetOptionalUser:
    """Tests for get_optional_user dependency."""

    def test_returns_none_without_credentials(self):
        """Test that None is returned without credentials."""
        result = get_optional_user(credentials=None)

        assert result is None

    def test_returns_user_with_valid_credentials(self):
        """Test that user is returned with valid credentials."""
        token = create_access_token(
            user_id="user123",
            roles=["farmer"],
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

        result = get_optional_user(credentials=credentials)

        assert result is not None
        assert result.id == "user123"

    def test_returns_none_with_invalid_credentials(self):
        """Test that None is returned with invalid credentials."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token",
        )

        result = get_optional_user(credentials=credentials)

        assert result is None
