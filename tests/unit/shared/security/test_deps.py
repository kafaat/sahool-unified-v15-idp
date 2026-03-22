"""
Tests for shared/security/deps.py
FastAPI security dependency injection
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from shared.security.deps import (
    get_api_key,
    get_optional_principal,
    get_principal,
    get_tenant_from_header,
    get_tenant_id,
    get_user_id,
    require_api_key,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_request():
    """Create a mock FastAPI Request with state"""
    request = MagicMock()
    request.state = MagicMock()
    return request


def _make_credentials(token="valid-token"):
    """Create mock HTTPAuthorizationCredentials"""
    creds = MagicMock()
    creds.credentials = token
    return creds


VALID_PAYLOAD = {
    "sub": "user-123",
    "tenant_id": "tenant-456",
    "tid": "tenant-456",
    "roles": ["worker"],
    "scopes": [],
}


# ─────────────────────────────────────────────────────────────────────────────
# get_principal
# ─────────────────────────────────────────────────────────────────────────────


class TestGetPrincipal:
    @pytest.mark.asyncio
    async def test_missing_credentials_raises_401(self):
        request = _make_request()
        with pytest.raises(HTTPException) as exc_info:
            await get_principal(request, credentials=None)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "missing_token"

    @pytest.mark.asyncio
    @patch("shared.security.deps.verify_token")
    async def test_valid_token(self, mock_verify):
        mock_verify.return_value = VALID_PAYLOAD
        request = _make_request()
        creds = _make_credentials("my-jwt")

        result = await get_principal(request, credentials=creds)

        assert result == VALID_PAYLOAD
        mock_verify.assert_called_once_with("my-jwt")
        assert request.state.principal == VALID_PAYLOAD
        assert request.state.user_id == "user-123"
        assert request.state.tenant_id == "tenant-456"

    @pytest.mark.asyncio
    @patch("shared.security.deps.verify_token")
    async def test_valid_token_tid_fallback(self, mock_verify):
        """When tenant_id is absent, falls back to tid"""
        payload = {"sub": "u1", "tid": "t1", "roles": []}
        mock_verify.return_value = payload
        request = _make_request()
        creds = _make_credentials()

        result = await get_principal(request, credentials=creds)
        assert request.state.tenant_id == "t1"

    @pytest.mark.asyncio
    @patch("shared.security.deps.verify_token")
    async def test_invalid_token_raises_401(self, mock_verify):
        from shared.security.jwt import AuthError
        mock_verify.side_effect = AuthError("Token is invalid", code="invalid_token")
        request = _make_request()
        creds = _make_credentials("bad-token")

        with pytest.raises(HTTPException) as exc_info:
            await get_principal(request, credentials=creds)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "invalid_token"


# ─────────────────────────────────────────────────────────────────────────────
# get_optional_principal
# ─────────────────────────────────────────────────────────────────────────────


class TestGetOptionalPrincipal:
    @pytest.mark.asyncio
    async def test_no_credentials_returns_none(self):
        request = _make_request()
        result = await get_optional_principal(request, credentials=None)
        assert result is None

    @pytest.mark.asyncio
    @patch("shared.security.deps.verify_token")
    async def test_valid_token(self, mock_verify):
        mock_verify.return_value = VALID_PAYLOAD
        request = _make_request()
        creds = _make_credentials()

        result = await get_optional_principal(request, credentials=creds)
        assert result == VALID_PAYLOAD
        assert request.state.user_id == "user-123"

    @pytest.mark.asyncio
    @patch("shared.security.deps.verify_token")
    async def test_invalid_token_returns_none(self, mock_verify):
        from shared.security.jwt import AuthError
        mock_verify.side_effect = AuthError("Token expired", code="expired")
        request = _make_request()
        creds = _make_credentials("expired-token")

        result = await get_optional_principal(request, credentials=creds)
        assert result is None


# ─────────────────────────────────────────────────────────────────────────────
# get_tenant_id / get_user_id
# ─────────────────────────────────────────────────────────────────────────────


class TestTenantAndUserId:
    @pytest.mark.asyncio
    async def test_get_tenant_id_from_tenant_id(self):
        principal = {"sub": "u1", "tenant_id": "t-abc", "tid": "t-def"}
        result = await get_tenant_id(principal)
        assert result == "t-abc"

    @pytest.mark.asyncio
    async def test_get_tenant_id_falls_back_to_tid(self):
        principal = {"sub": "u1", "tid": "t-from-tid"}
        result = await get_tenant_id(principal)
        assert result == "t-from-tid"

    @pytest.mark.asyncio
    async def test_get_tenant_id_empty(self):
        principal = {"sub": "u1"}
        result = await get_tenant_id(principal)
        assert result == ""

    @pytest.mark.asyncio
    async def test_get_user_id(self):
        principal = {"sub": "user-xyz"}
        result = await get_user_id(principal)
        assert result == "user-xyz"

    @pytest.mark.asyncio
    async def test_get_user_id_missing(self):
        principal = {}
        result = await get_user_id(principal)
        assert result == ""


# ─────────────────────────────────────────────────────────────────────────────
# get_tenant_from_header
# ─────────────────────────────────────────────────────────────────────────────


class TestGetTenantFromHeader:
    @pytest.mark.asyncio
    async def test_from_jwt_principal(self):
        principal = {"tenant_id": "jwt-tenant", "tid": "jwt-tenant"}
        result = await get_tenant_from_header(x_tenant_id=None, principal=principal)
        assert result == "jwt-tenant"

    @pytest.mark.asyncio
    async def test_from_header(self):
        result = await get_tenant_from_header(x_tenant_id="header-tenant", principal=None)
        assert result == "header-tenant"

    @pytest.mark.asyncio
    async def test_jwt_takes_precedence(self):
        principal = {"tenant_id": "jwt-tenant"}
        result = await get_tenant_from_header(x_tenant_id="header-tenant", principal=principal)
        assert result == "jwt-tenant"

    @pytest.mark.asyncio
    async def test_missing_both_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            await get_tenant_from_header(x_tenant_id=None, principal=None)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["error"] == "missing_tenant"


# ─────────────────────────────────────────────────────────────────────────────
# API Key dependencies
# ─────────────────────────────────────────────────────────────────────────────


class TestApiKey:
    @pytest.mark.asyncio
    async def test_get_api_key_present(self):
        result = await get_api_key(x_api_key="my-api-key")
        assert result == "my-api-key"

    @pytest.mark.asyncio
    async def test_get_api_key_absent(self):
        result = await get_api_key(x_api_key=None)
        assert result is None

    @pytest.mark.asyncio
    async def test_require_api_key_present(self):
        result = await require_api_key(api_key="valid-key")
        assert result == "valid-key"

    @pytest.mark.asyncio
    async def test_require_api_key_absent_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            await require_api_key(api_key=None)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error"] == "missing_api_key"
