"""
Extended unit tests for shared/auth/dependencies.py
Covers enforce_tenant, get_current_user DB paths, cached user paths,
get_optional_user edge cases, and rate_limit_dependency.
"""

import os
import time
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"

from shared.auth.dependencies import (
    RateLimiter,
    enforce_tenant,
    get_current_active_user,
    get_current_user,
    get_optional_user,
    rate_limit_dependency,
    require_farm_access,
    require_permissions,
    require_roles,
)
from shared.auth.jwt_handler import create_access_token
from shared.auth.models import AuthErrors, AuthException, User
from shared.auth.user_repository import UserValidationData


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_token():
    return create_access_token(
        user_id="user123",
        roles=["farmer"],
        tenant_id="tenant456",
        permissions=["farm:read"],
    )


@pytest.fixture
def valid_credentials(valid_token):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)


@pytest.fixture
def admin_token():
    return create_access_token(
        user_id="admin1",
        roles=["admin"],
        tenant_id="tenant456",
        permissions=["admin:access"],
    )


@pytest.fixture
def admin_credentials(admin_token):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=admin_token)


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.state = MagicMock()
    request.path_params = {"farm_id": "farm123"}
    return request


# ---------------------------------------------------------------------------
# enforce_tenant
# ---------------------------------------------------------------------------


class TestEnforceTenant:
    """Tests for enforce_tenant function."""

    def test_returns_user_tenant_when_no_requested(self):
        """Returns user's tenant_id when no requested_tenant_id."""
        user = User(id="u1", email="a@b.com", roles=["farmer"], tenant_id="t1")
        result = enforce_tenant(user)
        assert result == "t1"

    def test_raises_400_when_no_tenant_anywhere(self):
        """Raises 400 when neither user nor request has tenant_id."""
        user = User(id="u1", email="a@b.com", roles=["farmer"], tenant_id=None)
        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user, requested_tenant_id=None)
        assert exc_info.value.status_code == 400

    def test_admin_can_access_any_tenant(self):
        """Admin users can access any requested tenant."""
        user = User(id="u1", email="a@b.com", roles=["admin"], tenant_id="t1")
        result = enforce_tenant(user, requested_tenant_id="t2")
        assert result == "t2"

    def test_non_admin_same_tenant_succeeds(self):
        """Non-admin user accessing own tenant succeeds."""
        user = User(id="u1", email="a@b.com", roles=["farmer"], tenant_id="t1")
        result = enforce_tenant(user, requested_tenant_id="t1")
        assert result == "t1"

    def test_non_admin_different_tenant_raises_403(self):
        """Non-admin user accessing different tenant raises 403."""
        user = User(id="u1", email="a@b.com", roles=["farmer"], tenant_id="t1")
        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user, requested_tenant_id="t2")
        assert exc_info.value.status_code == 403
        assert "tenant mismatch" in exc_info.value.detail

    def test_non_admin_no_user_tenant_with_requested(self):
        """Non-admin user with no tenant_id but with requested_tenant_id."""
        user = User(id="u1", email="a@b.com", roles=["farmer"], tenant_id=None)
        # user_tenant is None and user is not admin, so requested_tenant_id is returned
        result = enforce_tenant(user, requested_tenant_id="t2")
        assert result == "t2"


# ---------------------------------------------------------------------------
# get_current_user – cached verified user path
# ---------------------------------------------------------------------------


class TestGetCurrentUserCachedPaths:
    """Tests for get_current_user with cached user data."""

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_cached_unverified_user_raises_403(self, mock_repo, mock_cache, valid_credentials):
        """Cached user that is not verified raises 403."""
        cache = AsyncMock()
        cache.get_user_status.return_value = {
            "is_active": True,
            "is_verified": False,
        }
        mock_cache.return_value = cache
        mock_repo.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=valid_credentials, request=None)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == AuthErrors.ACCOUNT_NOT_VERIFIED.en

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_cached_active_verified_user_returns_user(
        self, mock_repo, mock_cache, valid_credentials, mock_request
    ):
        """Cached active and verified user returns User object."""
        cache = AsyncMock()
        cache.get_user_status.return_value = {
            "is_active": True,
            "is_verified": True,
            "email": "cached@example.com",
            "roles": ["farmer"],
            "tenant_id": "tenant456",
        }
        mock_cache.return_value = cache
        mock_repo.return_value = None

        user = await get_current_user(credentials=valid_credentials, request=mock_request)

        assert user.id == "user123"
        assert user.email == "cached@example.com"
        assert user.is_active is True
        assert mock_request.state.user == user

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_cached_user_without_request(self, mock_repo, mock_cache, valid_credentials):
        """Cached user returned even when request is None."""
        cache = AsyncMock()
        cache.get_user_status.return_value = {
            "is_active": True,
            "is_verified": True,
            "email": "cached@example.com",
            "roles": ["farmer"],
            "tenant_id": "tenant456",
        }
        mock_cache.return_value = cache
        mock_repo.return_value = None

        user = await get_current_user(credentials=valid_credentials, request=None)

        assert user.id == "user123"


# ---------------------------------------------------------------------------
# get_current_user – database paths
# ---------------------------------------------------------------------------


class TestGetCurrentUserDBPaths:
    """Tests for get_current_user with database repository."""

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_db_user_not_found_raises_401(self, mock_repo, mock_cache, valid_credentials):
        """User not found in database raises 401."""
        mock_cache.return_value = None
        repo = AsyncMock()
        repo.get_user_validation_data.return_value = None
        mock_repo.return_value = repo

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=valid_credentials, request=None)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_db_deleted_user_raises_403(self, mock_repo, mock_cache, valid_credentials):
        """Deleted user in database raises 403."""
        mock_cache.return_value = None
        repo = AsyncMock()
        repo.get_user_validation_data.return_value = UserValidationData(
            user_id="user123",
            email="del@example.com",
            is_active=True,
            is_verified=True,
            roles=["farmer"],
            is_deleted=True,
        )
        mock_repo.return_value = repo

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=valid_credentials, request=None)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_db_suspended_user_raises_403(self, mock_repo, mock_cache, valid_credentials):
        """Suspended user in database raises 403."""
        mock_cache.return_value = None
        repo = AsyncMock()
        repo.get_user_validation_data.return_value = UserValidationData(
            user_id="user123",
            email="sus@example.com",
            is_active=True,
            is_verified=True,
            roles=["farmer"],
            is_suspended=True,
        )
        mock_repo.return_value = repo

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=valid_credentials, request=None)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_db_inactive_user_raises_403(self, mock_repo, mock_cache, valid_credentials):
        """Inactive user in database raises 403."""
        mock_cache.return_value = None
        repo = AsyncMock()
        repo.get_user_validation_data.return_value = UserValidationData(
            user_id="user123",
            email="inact@example.com",
            is_active=False,
            is_verified=True,
            roles=["farmer"],
        )
        mock_repo.return_value = repo

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=valid_credentials, request=None)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_db_unverified_user_raises_403(self, mock_repo, mock_cache, valid_credentials):
        """Unverified user in database raises 403."""
        mock_cache.return_value = None
        repo = AsyncMock()
        repo.get_user_validation_data.return_value = UserValidationData(
            user_id="user123",
            email="unver@example.com",
            is_active=True,
            is_verified=False,
            roles=["farmer"],
        )
        mock_repo.return_value = repo

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=valid_credentials, request=None)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == AuthErrors.ACCOUNT_NOT_VERIFIED.en

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_db_valid_user_returns_user_and_updates_cache(
        self, mock_repo, mock_cache, valid_credentials, mock_request
    ):
        """Valid user from DB is returned and cache is updated."""
        cache = AsyncMock()
        cache.get_user_status.return_value = None  # Cache miss
        mock_cache.return_value = cache

        repo = AsyncMock()
        repo.get_user_validation_data.return_value = UserValidationData(
            user_id="user123",
            email="valid@example.com",
            is_active=True,
            is_verified=True,
            roles=["farmer", "admin"],
            tenant_id="tenant456",
        )
        mock_repo.return_value = repo

        user = await get_current_user(credentials=valid_credentials, request=mock_request)

        assert user.id == "user123"
        assert user.email == "valid@example.com"
        assert "farmer" in user.roles
        assert user.tenant_id == "tenant456"

        # Cache should be updated
        cache.set_user_status.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.get_user_cache")
    @patch("shared.auth.dependencies.get_user_repository")
    async def test_db_valid_user_no_cache_skips_cache_update(
        self, mock_repo, mock_cache, valid_credentials, mock_request
    ):
        """Valid user from DB with no cache available skips cache update."""
        mock_cache.return_value = None  # No cache at all

        repo = AsyncMock()
        repo.get_user_validation_data.return_value = UserValidationData(
            user_id="user123",
            email="valid@example.com",
            is_active=True,
            is_verified=True,
            roles=["farmer"],
            tenant_id="tenant456",
        )
        mock_repo.return_value = repo

        user = await get_current_user(credentials=valid_credentials, request=mock_request)

        assert user.id == "user123"


# ---------------------------------------------------------------------------
# get_current_user – AuthException path
# ---------------------------------------------------------------------------


class TestGetCurrentUserAuthException:
    """Tests for AuthException handling in get_current_user."""

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.verify_token")
    async def test_auth_exception_raises_http_exception(self, mock_verify):
        """AuthException is converted to HTTPException."""
        mock_verify.side_effect = AuthException(AuthErrors.EXPIRED_TOKEN)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired-token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, request=None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == AuthErrors.EXPIRED_TOKEN.en

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.verify_token")
    async def test_generic_exception_raises_401(self, mock_verify):
        """Generic exception is caught and raises 401."""
        mock_verify.side_effect = RuntimeError("unexpected error")

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, request=None)

        assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# require_farm_access – user without farm access
# ---------------------------------------------------------------------------


class TestRequireFarmAccessExtended:
    """Extended tests for require_farm_access."""

    @pytest.mark.asyncio
    async def test_user_without_farm_access_raises_403(self):
        """Non-admin user without farm access raises 403."""
        user = User(
            id="u1",
            email="test@example.com",
            roles=["farmer"],
            farm_ids=["other_farm"],
            is_active=True,
        )
        request = MagicMock()
        request.path_params = {"farm_id": "restricted_farm"}

        checker = require_farm_access()

        with pytest.raises(HTTPException) as exc_info:
            await checker(request=request, user=user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_user_with_farm_access_passes(self):
        """User with matching farm_id in farm_ids passes."""
        user = User(
            id="u1",
            email="test@example.com",
            roles=["farmer"],
            farm_ids=["farm123"],
            is_active=True,
        )
        request = MagicMock()
        request.path_params = {"farm_id": "farm123"}

        checker = require_farm_access()
        result = await checker(request=request, user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_custom_farm_id_param(self):
        """require_farm_access with custom param name."""
        user = User(
            id="u1",
            email="test@example.com",
            roles=["farmer"],
            farm_ids=["my_farm"],
            is_active=True,
        )
        request = MagicMock()
        request.path_params = {"my_farm_id": "my_farm"}

        checker = require_farm_access(farm_id_param="my_farm_id")
        result = await checker(request=request, user=user)
        assert result == user


# ---------------------------------------------------------------------------
# require_permissions – multiple permissions
# ---------------------------------------------------------------------------


class TestRequirePermissionsExtended:
    """Extended tests for require_permissions."""

    @pytest.mark.asyncio
    async def test_user_with_one_of_multiple_permissions_passes(self):
        """User with at least one required permission passes."""
        user = User(
            id="u1",
            email="test@example.com",
            roles=["farmer"],
            permissions=["farm:read"],
            is_active=True,
        )
        checker = require_permissions("farm:read", "farm:delete")
        result = await checker(user=user)
        assert result == user

    @pytest.mark.asyncio
    async def test_user_with_no_matching_permissions_raises_403(self):
        """User without any matching permission raises 403."""
        user = User(
            id="u1",
            email="test@example.com",
            roles=["farmer"],
            permissions=["farm:read"],
            is_active=True,
        )
        checker = require_permissions("admin:access", "admin:settings")
        with pytest.raises(HTTPException) as exc_info:
            await checker(user=user)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# RateLimiter – edge cases
# ---------------------------------------------------------------------------


class TestRateLimiterExtended:
    """Extended tests for RateLimiter."""

    def test_get_violation_count_for_unknown_key(self):
        """get_violation_count returns 0 for unknown key."""
        limiter = RateLimiter(requests=5, window_seconds=60)
        assert limiter.get_violation_count("unknown_key") == 0

    def test_reset_violations_for_unknown_key(self):
        """reset_violations does not raise for unknown key."""
        limiter = RateLimiter(requests=5, window_seconds=60)
        limiter.reset_violations("unknown_key")  # Should not raise

    def test_remaining_decreases(self):
        """remaining count decreases with each request."""
        limiter = RateLimiter(requests=3, window_seconds=60)
        _, r1 = limiter.is_allowed("u1")
        _, r2 = limiter.is_allowed("u1")
        _, r3 = limiter.is_allowed("u1")
        assert r1 == 2
        assert r2 == 1
        assert r3 == 0


# ---------------------------------------------------------------------------
# rate_limit_dependency
# ---------------------------------------------------------------------------


class TestRateLimitDependency:
    """Tests for rate_limit_dependency."""

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.config")
    @patch("shared.auth.dependencies._rate_limiter")
    async def test_rate_limit_disabled_returns_user(self, mock_limiter, mock_config):
        """When rate limiting disabled, user is returned directly."""
        mock_config.RATE_LIMIT_ENABLED = False
        user = User(id="u1", email="a@b.com", roles=["farmer"])
        request = MagicMock()

        result = await rate_limit_dependency(request=request, user=user)

        assert result == user

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.config")
    @patch("shared.auth.dependencies._rate_limiter")
    async def test_rate_limit_exceeded_raises_429(self, mock_limiter, mock_config):
        """When rate limit exceeded, raises 429."""
        mock_config.RATE_LIMIT_ENABLED = True
        mock_limiter.is_allowed.return_value = (False, 0)
        mock_limiter.get_violation_count.return_value = 5
        mock_limiter.requests = 100
        mock_limiter.window_seconds = 60

        user = User(id="u1", email="a@b.com", roles=["farmer"])
        request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await rate_limit_dependency(request=request, user=user)

        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    @patch("shared.auth.dependencies.config")
    @patch("shared.auth.dependencies._rate_limiter")
    async def test_rate_limit_passed_sets_remaining(self, mock_limiter, mock_config):
        """When rate limit passes, remaining is stored on request.state."""
        mock_config.RATE_LIMIT_ENABLED = True
        mock_limiter.is_allowed.return_value = (True, 42)

        user = User(id="u1", email="a@b.com", roles=["farmer"])
        request = MagicMock()

        result = await rate_limit_dependency(request=request, user=user)

        assert result == user
        assert request.state.rate_limit_remaining == 42
