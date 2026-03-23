"""
Tests for Authentication Dependencies (api/deps.py)
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import jwt as pyjwt
import pytest
from fastapi import HTTPException

pytestmark = [pytest.mark.unit]


def _make_token(
    payload: dict, secret: str = "test-secret-key-for-unit-tests-only-32chars", algorithm: str = "HS256"
) -> str:
    return pyjwt.encode(payload, secret, algorithm=algorithm)


class TestValidateJwtConfig:
    def test_production_with_short_key_raises(self):
        from src.api.deps import validate_jwt_config

        with patch("src.api.deps.JWT_SECRET_KEY", "short"):
            with pytest.raises(RuntimeError, match="32 characters"):
                validate_jwt_config("production")

    def test_production_with_long_key_ok(self):
        from src.api.deps import validate_jwt_config

        with patch("src.api.deps.JWT_SECRET_KEY", "a" * 32):
            validate_jwt_config("production")  # Should not raise

    def test_development_with_empty_key_warns(self):
        from src.api.deps import validate_jwt_config

        with patch("src.api.deps.JWT_SECRET_KEY", ""):
            validate_jwt_config("development")  # Should not raise, just warns


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_no_credentials_raises_401(self):
        from src.api.deps import get_current_user

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self):
        from src.api.deps import get_current_user

        secret = "test-secret-key-for-unit-tests-only-32chars"
        token = _make_token(
            {
                "sub": "user-123",
                "tid": "tenant-456",
                "role": "admin",
                "email": "test@test.com",
                "exp": int(time.time()) + 3600,
            },
            secret=secret,
        )

        creds = MagicMock()
        creds.credentials = token

        with patch("src.api.deps.JWT_SECRET_KEY", secret):
            with patch("src.api.deps.JWT_ALGORITHM", "HS256"):
                user = await get_current_user(creds)
                assert user["user_id"] == "user-123"
                assert user["tenant_id"] == "tenant-456"
                assert user["role"] == "admin"
                assert user["email"] == "test@test.com"

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self):
        from src.api.deps import get_current_user

        secret = "test-secret-key-for-unit-tests-only-32chars"
        token = _make_token(
            {"sub": "user-1", "exp": int(time.time()) - 3600},
            secret=secret,
        )

        creds = MagicMock()
        creds.credentials = token

        with patch("src.api.deps.JWT_SECRET_KEY", secret):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(creds)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        from src.api.deps import get_current_user

        creds = MagicMock()
        creds.credentials = "invalid.token.here"

        with patch("src.api.deps.JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars"):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(creds)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_without_sub_raises_401(self):
        from src.api.deps import get_current_user

        secret = "test-secret-key-for-unit-tests-only-32chars"
        # Token with exp but no sub
        token = _make_token(
            {"exp": int(time.time()) + 3600, "role": "user"},
            secret=secret,
        )

        creds = MagicMock()
        creds.credentials = token

        with patch("src.api.deps.JWT_SECRET_KEY", secret):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(creds)
            assert exc_info.value.status_code == 401


class TestGetOptionalUser:
    @pytest.mark.asyncio
    async def test_no_credentials_returns_none(self):
        from src.api.deps import get_optional_user

        result = await get_optional_user(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_credentials_returns_none(self):
        from src.api.deps import get_optional_user

        creds = MagicMock()
        creds.credentials = "bad.token"

        with patch("src.api.deps.JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars"):
            result = await get_optional_user(creds)
            assert result is None

    @pytest.mark.asyncio
    async def test_valid_credentials_returns_user(self):
        from src.api.deps import get_optional_user

        secret = "test-secret-key-for-unit-tests-only-32chars"
        token = _make_token(
            {"sub": "u1", "exp": int(time.time()) + 3600},
            secret=secret,
        )

        creds = MagicMock()
        creds.credentials = token

        with patch("src.api.deps.JWT_SECRET_KEY", secret):
            with patch("src.api.deps.JWT_ALGORITHM", "HS256"):
                result = await get_optional_user(creds)
                assert result is not None
                assert result["user_id"] == "u1"
