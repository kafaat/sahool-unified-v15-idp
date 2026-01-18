"""
Token Revocation System Unit Tests
Tests for Redis-based token revocation storage and verification
"""

import json
import os
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set test environment before importing token_revocation module
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["REDIS_URL"] = ""  # Empty for unit tests
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_DB"] = "0"
os.environ["REDIS_PASSWORD"] = ""

from shared.auth.token_revocation import (
    RedisTokenRevocationStore,
    RevocationInfo,
    get_revocation_store,
    is_token_revoked,
    revoke_all_user_tokens,
    revoke_token,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def test_jti() -> str:
    """Standard test JTI"""
    return "test-jti-12345abcde"


@pytest.fixture
def test_user_id() -> str:
    """Standard test user ID"""
    return "test-user-123"


@pytest.fixture
def test_tenant_id() -> str:
    """Standard test tenant ID"""
    return "test-tenant-456"


@pytest.fixture
def revocation_store():
    """Create and return a RedisTokenRevocationStore instance with mocked Redis"""
    store = RedisTokenRevocationStore(redis_url="redis://localhost:6379/0")
    return store


@pytest.fixture
async def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    mock.exists = AsyncMock(return_value=1)
    mock.get = AsyncMock(return_value=None)
    mock.delete = AsyncMock(return_value=1)
    mock.keys = AsyncMock(return_value=[])
    mock.close = AsyncMock(return_value=None)
    return mock


# ═══════════════════════════════════════════════════════════════════════════════
# RevocationInfo Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestRevocationInfo:
    """Tests for RevocationInfo dataclass"""

    def test_revocation_info_creation(self, test_jti, test_user_id):
        """Test creating RevocationInfo instance"""
        revoked_at = time.time()
        info = RevocationInfo(
            revoked_at=revoked_at,
            reason="logout",
            user_id=test_user_id,
        )

        assert info.revoked_at == revoked_at
        assert info.reason == "logout"
        assert info.user_id == test_user_id
        assert info.tenant_id is None

    def test_revocation_info_with_all_fields(self, test_user_id, test_tenant_id):
        """Test creating RevocationInfo with all fields"""
        revoked_at = time.time()
        info = RevocationInfo(
            revoked_at=revoked_at,
            reason="password_change",
            user_id=test_user_id,
            tenant_id=test_tenant_id,
        )

        assert info.revoked_at == revoked_at
        assert info.reason == "password_change"
        assert info.user_id == test_user_id
        assert info.tenant_id == test_tenant_id


# ═══════════════════════════════════════════════════════════════════════════════
# Token Revocation Tests (JTI-based)
# ═══════════════════════════════════════════════════════════════════════════════


class TestTokenRevocation:
    """Tests for individual token revocation by JTI"""

    @pytest.mark.asyncio
    async def test_revoke_token_success(self, revocation_store, test_jti, test_user_id):
        """Test successful token revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.setex = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.revoke_token(
                jti=test_jti,
                expires_in=3600,
                reason="logout",
                user_id=test_user_id,
            )

            assert result is True
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            assert call_args[0][0] == f"revoked:token:{test_jti}"
            assert call_args[0][1] == 3600

    @pytest.mark.asyncio
    async def test_revoke_token_with_default_ttl(self, revocation_store, test_jti):
        """Test token revocation with default TTL"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.setex = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.revoke_token(jti=test_jti)

            assert result is True
            call_args = mock_redis.setex.call_args
            # Default TTL is 24 hours = 86400 seconds
            assert call_args[0][1] == 86400

    @pytest.mark.asyncio
    async def test_revoke_token_with_empty_jti(self, revocation_store):
        """Test that revoking empty JTI returns False"""
        result = await revocation_store.revoke_token(jti="")

        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_token_with_none_jti(self, revocation_store):
        """Test that revoking None JTI returns False"""
        result = await revocation_store.revoke_token(jti=None)

        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_token_redis_error(self, revocation_store, test_jti):
        """Test handling of Redis errors during revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.setex = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.revoke_token(jti=test_jti)

            assert result is False

    @pytest.mark.asyncio
    async def test_is_token_revoked_true(self, revocation_store, test_jti):
        """Test checking if revoked token exists"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.exists = AsyncMock(return_value=1)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_token_revoked(test_jti)

            assert result is True
            mock_redis.exists.assert_called_once_with(f"revoked:token:{test_jti}")

    @pytest.mark.asyncio
    async def test_is_token_revoked_false(self, revocation_store, test_jti):
        """Test checking if non-revoked token exists"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.exists = AsyncMock(return_value=0)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_token_revoked(test_jti)

            assert result is False

    @pytest.mark.asyncio
    async def test_is_token_revoked_with_empty_jti(self, revocation_store):
        """Test checking empty JTI returns False"""
        result = await revocation_store.is_token_revoked("")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_token_revoked_redis_error(self, revocation_store, test_jti):
        """Test Redis error handling during revocation check"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.exists = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_token_revoked(test_jti)

            # Should fail open on Redis errors
            assert result is False

    @pytest.mark.asyncio
    async def test_get_revocation_info(self, revocation_store, test_jti):
        """Test getting detailed revocation information"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            revocation_data = {
                "revoked_at": time.time(),
                "reason": "logout",
                "user_id": "user-123",
                "tenant_id": "tenant-456",
            }
            mock_redis.get = AsyncMock(return_value=str(revocation_data))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.get_revocation_info(test_jti)

            assert result is not None
            assert result["reason"] == "logout"

    @pytest.mark.asyncio
    async def test_get_revocation_info_not_found(self, revocation_store, test_jti):
        """Test getting revocation info for non-revoked token"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.get_revocation_info(test_jti)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_revocation_info_redis_error(self, revocation_store, test_jti):
        """Test Redis error handling during info retrieval"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.get_revocation_info(test_jti)

            assert result is None


# ═══════════════════════════════════════════════════════════════════════════════
# User-Level Revocation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestUserLevelRevocation:
    """Tests for user-level token revocation"""

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_success(self, revocation_store, test_user_id):
        """Test successful revocation of all user tokens"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.setex = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.revoke_all_user_tokens(
                user_id=test_user_id,
                reason="password_change",
            )

            assert result is True
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            assert call_args[0][0] == f"revoked:user:{test_user_id}"
            # Should use 30-day TTL
            assert call_args[0][1] == 2592000

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_empty_user_id(self, revocation_store):
        """Test that revoking empty user_id returns False"""
        result = await revocation_store.revoke_all_user_tokens(user_id="")

        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_redis_error(self, revocation_store, test_user_id):
        """Test Redis error handling during user revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.setex = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.revoke_all_user_tokens(user_id=test_user_id)

            assert result is False

    @pytest.mark.asyncio
    async def test_is_user_token_revoked_true(self, revocation_store, test_user_id):
        """Test checking if user tokens are revoked (token issued before revocation)"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            revoked_at = time.time()
            token_issued_at = revoked_at - 100  # Token issued before revocation
            revocation_data = {
                "revoked_at": revoked_at,
                "reason": "password_change",
            }
            mock_redis.get = AsyncMock(return_value=str(revocation_data))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_user_token_revoked(
                user_id=test_user_id,
                token_issued_at=token_issued_at,
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_is_user_token_revoked_false_no_revocation(self, revocation_store, test_user_id):
        """Test checking if user tokens are revoked (no revocation entry)"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_user_token_revoked(
                user_id=test_user_id,
                token_issued_at=time.time(),
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_is_user_token_revoked_false_token_issued_after(self, revocation_store, test_user_id):
        """Test checking if user tokens are revoked (token issued after revocation)"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            revoked_at = time.time()
            token_issued_at = revoked_at + 100  # Token issued after revocation
            revocation_data = {
                "revoked_at": revoked_at,
                "reason": "password_change",
            }
            mock_redis.get = AsyncMock(return_value=str(revocation_data))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_user_token_revoked(
                user_id=test_user_id,
                token_issued_at=token_issued_at,
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_clear_user_revocation_success(self, revocation_store, test_user_id):
        """Test clearing user-level revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.delete = AsyncMock(return_value=1)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.clear_user_revocation(user_id=test_user_id)

            assert result is True
            mock_redis.delete.assert_called_once_with(f"revoked:user:{test_user_id}")

    @pytest.mark.asyncio
    async def test_clear_user_revocation_not_found(self, revocation_store, test_user_id):
        """Test clearing revocation when none exists"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.delete = AsyncMock(return_value=0)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.clear_user_revocation(user_id=test_user_id)

            assert result is False

    @pytest.mark.asyncio
    async def test_clear_user_revocation_empty_user_id(self, revocation_store):
        """Test clearing revocation with empty user_id"""
        result = await revocation_store.clear_user_revocation(user_id="")

        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# Tenant-Level Revocation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestTenantLevelRevocation:
    """Tests for tenant-level token revocation"""

    @pytest.mark.asyncio
    async def test_revoke_all_tenant_tokens_success(self, revocation_store, test_tenant_id):
        """Test successful revocation of all tenant tokens"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.setex = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.revoke_all_tenant_tokens(
                tenant_id=test_tenant_id,
                reason="security",
            )

            assert result is True
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            assert call_args[0][0] == f"revoked:tenant:{test_tenant_id}"
            # Should use 30-day TTL
            assert call_args[0][1] == 2592000

    @pytest.mark.asyncio
    async def test_revoke_all_tenant_tokens_empty_tenant_id(self, revocation_store):
        """Test that revoking empty tenant_id returns False"""
        result = await revocation_store.revoke_all_tenant_tokens(tenant_id="")

        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_all_tenant_tokens_redis_error(self, revocation_store, test_tenant_id):
        """Test Redis error handling during tenant revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.setex = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.revoke_all_tenant_tokens(tenant_id=test_tenant_id)

            assert result is False

    @pytest.mark.asyncio
    async def test_is_tenant_token_revoked_true(self, revocation_store, test_tenant_id):
        """Test checking if tenant tokens are revoked (token issued before revocation)"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            revoked_at = time.time()
            token_issued_at = revoked_at - 100  # Token issued before revocation
            revocation_data = {
                "revoked_at": revoked_at,
                "reason": "security",
            }
            mock_redis.get = AsyncMock(return_value=str(revocation_data))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_tenant_token_revoked(
                tenant_id=test_tenant_id,
                token_issued_at=token_issued_at,
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_is_tenant_token_revoked_false_no_revocation(self, revocation_store, test_tenant_id):
        """Test checking if tenant tokens are revoked (no revocation entry)"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_tenant_token_revoked(
                tenant_id=test_tenant_id,
                token_issued_at=time.time(),
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_is_tenant_token_revoked_false_token_issued_after(self, revocation_store, test_tenant_id):
        """Test checking if tenant tokens are revoked (token issued after revocation)"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            revoked_at = time.time()
            token_issued_at = revoked_at + 100  # Token issued after revocation
            revocation_data = {
                "revoked_at": revoked_at,
                "reason": "security",
            }
            mock_redis.get = AsyncMock(return_value=str(revocation_data))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.is_tenant_token_revoked(
                tenant_id=test_tenant_id,
                token_issued_at=token_issued_at,
            )

            assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# Combined Revocation Check Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCombinedRevocationCheck:
    """Tests for combined revocation check across all levels"""

    @pytest.mark.asyncio
    async def test_is_revoked_by_jti(self, revocation_store, test_jti):
        """Test combined check with JTI revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.exists = AsyncMock(return_value=1)
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            is_revoked, reason = await revocation_store.is_revoked(jti=test_jti)

            assert is_revoked is True
            assert reason == "token_revoked"

    @pytest.mark.asyncio
    async def test_is_revoked_by_user(self, revocation_store, test_user_id):
        """Test combined check with user revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.exists = AsyncMock(return_value=0)
            revoked_at = time.time()
            token_issued_at = revoked_at - 100
            revocation_data = {
                "revoked_at": revoked_at,
                "reason": "password_change",
            }
            mock_redis.get = AsyncMock(return_value=str(revocation_data))
            mock_redis_factory.return_value = mock_redis

            is_revoked, reason = await revocation_store.is_revoked(
                user_id=test_user_id,
                issued_at=token_issued_at,
            )

            assert is_revoked is True
            assert reason == "user_tokens_revoked"

    @pytest.mark.asyncio
    async def test_is_revoked_by_tenant(self, revocation_store, test_tenant_id):
        """Test combined check with tenant revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            revoked_at = time.time()
            token_issued_at = revoked_at - 100
            revocation_data = {
                "revoked_at": revoked_at,
                "reason": "security",
            }
            mock_redis.get = AsyncMock(return_value=str(revocation_data))
            mock_redis.exists = AsyncMock(return_value=0)
            mock_redis_factory.return_value = mock_redis

            is_revoked, reason = await revocation_store.is_revoked(
                tenant_id=test_tenant_id,
                issued_at=token_issued_at,
            )

            assert is_revoked is True
            assert reason == "tenant_tokens_revoked"

    @pytest.mark.asyncio
    async def test_is_revoked_none(self, revocation_store, test_jti):
        """Test combined check when token is not revoked"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.exists = AsyncMock(return_value=0)
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            is_revoked, reason = await revocation_store.is_revoked(jti=test_jti)

            assert is_revoked is False
            assert reason is None

    @pytest.mark.asyncio
    async def test_is_revoked_priority_jti_over_user(self, revocation_store, test_jti, test_user_id):
        """Test that JTI revocation is checked before user revocation"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.exists = AsyncMock(return_value=1)  # JTI is revoked
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            is_revoked, reason = await revocation_store.is_revoked(
                jti=test_jti,
                user_id=test_user_id,
                issued_at=time.time(),
            )

            # Should return JTI revocation reason, not user revocation
            assert is_revoked is True
            assert reason == "token_revoked"


# ═══════════════════════════════════════════════════════════════════════════════
# Statistics and Health Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestStatsAndHealth:
    """Tests for statistics and health check methods"""

    @pytest.mark.asyncio
    async def test_get_stats(self, revocation_store):
        """Test getting revocation statistics"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.keys = AsyncMock(side_effect=[
                ["revoked:token:jti1", "revoked:token:jti2"],
                ["revoked:user:user1"],
                ["revoked:tenant:tenant1"],
            ])
            mock_redis_factory.return_value = mock_redis

            stats = await revocation_store.get_stats()

            assert stats["initialized"] is True
            assert stats["revoked_tokens"] == 2
            assert stats["revoked_users"] == 1
            assert stats["revoked_tenants"] == 1

    @pytest.mark.asyncio
    async def test_get_stats_error(self, revocation_store):
        """Test stats retrieval with Redis error"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.keys = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            stats = await revocation_store.get_stats()

            assert stats["initialized"] is True
            assert "error" in stats

    @pytest.mark.asyncio
    async def test_health_check_success(self, revocation_store):
        """Test successful health check"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.health_check()

            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, revocation_store):
        """Test failed health check"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await revocation_store.health_check()

            assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# Initialization and Lifecycle Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestInitializationAndLifecycle:
    """Tests for store initialization and lifecycle"""

    @pytest.mark.asyncio
    async def test_store_initialization(self, revocation_store):
        """Test store initialization"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            await revocation_store.initialize()

            assert revocation_store._initialized is True
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_initialization_idempotent(self, revocation_store):
        """Test that initialization is idempotent"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            await revocation_store.initialize()
            await revocation_store.initialize()

            # Should only call redis factory once
            assert mock_redis_factory.call_count == 1

    @pytest.mark.asyncio
    async def test_store_initialization_redis_error(self, revocation_store):
        """Test initialization failure with Redis error"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            with pytest.raises(Exception):
                await revocation_store.initialize()

    @pytest.mark.asyncio
    async def test_store_close(self, revocation_store):
        """Test closing the store"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.close = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            await revocation_store.initialize()
            await revocation_store.close()

            assert revocation_store._initialized is False
            mock_redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_close_idempotent(self, revocation_store):
        """Test that closing is idempotent"""
        with patch("redis.asyncio.from_url") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.close = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_redis

            await revocation_store.initialize()
            await revocation_store.close()
            await revocation_store.close()

            # Should not raise error
            assert revocation_store._initialized is False


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience Function Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestConvenienceFunctions:
    """Tests for module-level convenience functions"""

    @pytest.mark.asyncio
    async def test_revoke_token_function(self, test_jti):
        """Test convenience revoke_token function"""
        with patch("shared.auth.token_revocation.get_revocation_store") as mock_get_store:
            mock_store = AsyncMock()
            mock_store.revoke_token = AsyncMock(return_value=True)
            mock_get_store.return_value = mock_store

            result = await revoke_token(jti=test_jti, reason="logout")

            assert result is True
            mock_store.revoke_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_function(self, test_user_id):
        """Test convenience revoke_all_user_tokens function"""
        with patch("shared.auth.token_revocation.get_revocation_store") as mock_get_store:
            mock_store = AsyncMock()
            mock_store.revoke_all_user_tokens = AsyncMock(return_value=True)
            mock_get_store.return_value = mock_store

            result = await revoke_all_user_tokens(user_id=test_user_id)

            assert result is True
            mock_store.revoke_all_user_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_token_revoked_function(self, test_jti):
        """Test convenience is_token_revoked function"""
        with patch("shared.auth.token_revocation.get_revocation_store") as mock_get_store:
            mock_store = AsyncMock()
            mock_store.is_revoked = AsyncMock(return_value=(True, "token_revoked"))
            mock_get_store.return_value = mock_store

            is_revoked, reason = await is_token_revoked(jti=test_jti)

            assert is_revoked is True
            assert reason == "token_revoked"
            mock_store.is_revoked.assert_called_once()
