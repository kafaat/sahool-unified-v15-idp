"""
Authentication Middleware Tests for SAHOOL Platform.

Tests validate JWT middleware, authorization, and request handling.
"""

import time
from typing import Any, Callable, Dict, Optional
from unittest.mock import Mock

import jwt
import pytest

TEST_SECRET_KEY = "test-secret-key-for-unit-tests-only-32chars"


class MockRequest:
    """Mock HTTP request for testing."""

    def __init__(self):
        self.headers: dict[str, str] = {}
        self.cookies: dict[str, str] = {}
        self.method: str = "GET"
        self.url: str = "/api/v1/fields"
        self.path: str = "/api/v1/fields"
        self.state: Any = Mock()


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status_code: int = 200, body: dict = None):
        self.status_code = status_code
        self.body = body or {}
        self.headers: dict[str, str] = {}


class AuthMiddleware:
    """Mock authentication middleware for testing."""

    def __init__(self, secret_key: str, algorithm: str = "HS256", excluded_paths: list = None):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.excluded_paths = excluded_paths or ["/healthz", "/readyz", "/docs"]

    def extract_token(self, request: MockRequest) -> str | None:
        """Extract JWT token from request."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]

        return request.cookies.get("access_token")

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify JWT token and return payload."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.InvalidTokenError:
            return None

    def is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication."""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    async def __call__(self, request: MockRequest, call_next: Callable) -> MockResponse:
        """Process request through middleware."""
        if self.is_excluded_path(request.path):
            return await call_next(request)

        token = self.extract_token(request)
        if not token:
            return MockResponse(status_code=401, body={"detail": "Not authenticated"})

        payload = self.verify_token(token)
        if not payload:
            return MockResponse(status_code=401, body={"detail": "Invalid token"})

        request.state.user = payload
        request.state.tenant_id = payload.get("tenant_id")

        return await call_next(request)


@pytest.fixture
def auth_middleware():
    """Create auth middleware instance."""
    return AuthMiddleware(secret_key=TEST_SECRET_KEY, excluded_paths=["/healthz", "/readyz", "/docs", "/openapi.json"])


@pytest.fixture
def mock_request():
    """Create mock request."""
    return MockRequest()


@pytest.fixture
def valid_token():
    """Create valid JWT token."""
    payload = {
        "sub": "user123",
        "tenant_id": "tenant456",
        "roles": ["farmer"],
        "exp": time.time() + 3600,
        "iat": time.time(),
    }
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")


@pytest.fixture
def expired_token():
    """Create expired JWT token."""
    payload = {
        "sub": "user123",
        "tenant_id": "tenant456",
        "exp": time.time() - 3600,
        "iat": time.time() - 7200,
    }
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")


class TestTokenExtraction:
    """Tests for token extraction from requests."""

    def test_extract_from_authorization_header(self, auth_middleware, mock_request, valid_token):
        """Test extracting token from Authorization header."""
        mock_request.headers["Authorization"] = f"Bearer {valid_token}"

        token = auth_middleware.extract_token(mock_request)
        assert token == valid_token

    def test_extract_from_cookie(self, auth_middleware, mock_request, valid_token):
        """Test extracting token from cookie."""
        mock_request.cookies["access_token"] = valid_token

        token = auth_middleware.extract_token(mock_request)
        assert token == valid_token

    def test_header_takes_priority_over_cookie(self, auth_middleware, mock_request, valid_token):
        """Test Authorization header takes priority over cookie."""
        header_token = valid_token
        cookie_token = "different-token"

        mock_request.headers["Authorization"] = f"Bearer {header_token}"
        mock_request.cookies["access_token"] = cookie_token

        token = auth_middleware.extract_token(mock_request)
        assert token == header_token

    def test_no_token_returns_none(self, auth_middleware, mock_request):
        """Test no token returns None."""
        token = auth_middleware.extract_token(mock_request)
        assert token is None

    def test_invalid_authorization_format(self, auth_middleware, mock_request):
        """Test invalid Authorization header format."""
        mock_request.headers["Authorization"] = "InvalidFormat token123"

        token = auth_middleware.extract_token(mock_request)
        assert token is None


class TestTokenVerification:
    """Tests for token verification."""

    def test_valid_token_verification(self, auth_middleware, valid_token):
        """Test valid token is verified successfully."""
        payload = auth_middleware.verify_token(valid_token)

        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["tenant_id"] == "tenant456"

    def test_expired_token_rejected(self, auth_middleware, expired_token):
        """Test expired token is rejected."""
        payload = auth_middleware.verify_token(expired_token)
        assert payload is None

    def test_invalid_signature_rejected(self, auth_middleware):
        """Test token with invalid signature is rejected."""
        payload = {
            "sub": "user123",
            "tenant_id": "tenant456",
            "exp": time.time() + 3600,
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

        result = auth_middleware.verify_token(token)
        assert result is None

    def test_malformed_token_rejected(self, auth_middleware):
        """Test malformed token is rejected."""
        result = auth_middleware.verify_token("not-a-valid-token")
        assert result is None


class TestExcludedPaths:
    """Tests for path exclusion."""

    def test_healthz_excluded(self, auth_middleware):
        """Test /healthz is excluded from auth."""
        assert auth_middleware.is_excluded_path("/healthz")

    def test_readyz_excluded(self, auth_middleware):
        """Test /readyz is excluded from auth."""
        assert auth_middleware.is_excluded_path("/readyz")

    def test_docs_excluded(self, auth_middleware):
        """Test /docs is excluded from auth."""
        assert auth_middleware.is_excluded_path("/docs")

    def test_api_paths_not_excluded(self, auth_middleware):
        """Test API paths are not excluded."""
        assert not auth_middleware.is_excluded_path("/api/v1/fields")
        assert not auth_middleware.is_excluded_path("/api/v1/users")


class TestMiddlewareExecution:
    """Tests for middleware execution flow."""

    @pytest.mark.asyncio
    async def test_authenticated_request_passes(self, auth_middleware, mock_request, valid_token):
        """Test authenticated request passes through."""
        mock_request.headers["Authorization"] = f"Bearer {valid_token}"

        async def call_next(request):
            return MockResponse(status_code=200, body={"data": "success"})

        response = await auth_middleware(mock_request, call_next)

        assert response.status_code == 200
        assert mock_request.state.user["sub"] == "user123"

    @pytest.mark.asyncio
    async def test_unauthenticated_request_rejected(self, auth_middleware, mock_request):
        """Test unauthenticated request is rejected."""
        mock_request.path = "/api/v1/fields"

        async def call_next(request):
            return MockResponse(status_code=200)

        response = await auth_middleware(mock_request, call_next)

        assert response.status_code == 401
        assert "Not authenticated" in response.body.get("detail", "")

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, auth_middleware, mock_request, expired_token):
        """Test request with invalid token is rejected."""
        mock_request.headers["Authorization"] = f"Bearer {expired_token}"

        async def call_next(request):
            return MockResponse(status_code=200)

        response = await auth_middleware(mock_request, call_next)

        assert response.status_code == 401
        assert "Invalid token" in response.body.get("detail", "")

    @pytest.mark.asyncio
    async def test_excluded_path_bypasses_auth(self, auth_middleware, mock_request):
        """Test excluded path bypasses authentication."""
        mock_request.path = "/healthz"

        async def call_next(request):
            return MockResponse(status_code=200, body={"status": "ok"})

        response = await auth_middleware(mock_request, call_next)

        assert response.status_code == 200


class TestTenantIsolation:
    """Tests for tenant isolation in middleware."""

    @pytest.mark.asyncio
    async def test_tenant_id_set_on_request(self, auth_middleware, mock_request, valid_token):
        """Test tenant_id is set on request state."""
        mock_request.headers["Authorization"] = f"Bearer {valid_token}"

        async def call_next(request):
            return MockResponse(status_code=200)

        await auth_middleware(mock_request, call_next)

        assert mock_request.state.tenant_id == "tenant456"

    @pytest.mark.asyncio
    async def test_user_payload_set_on_request(self, auth_middleware, mock_request, valid_token):
        """Test user payload is set on request state."""
        mock_request.headers["Authorization"] = f"Bearer {valid_token}"

        async def call_next(request):
            return MockResponse(status_code=200)

        await auth_middleware(mock_request, call_next)

        assert mock_request.state.user is not None
        assert mock_request.state.user["sub"] == "user123"


class TestRoleBasedAccess:
    """Tests for role-based access control."""

    def test_roles_extracted_from_token(self, auth_middleware, valid_token):
        """Test roles are extracted from token."""
        payload = auth_middleware.verify_token(valid_token)

        assert "roles" in payload
        assert "farmer" in payload["roles"]

    def test_admin_role_detection(self):
        """Test admin role detection."""
        payload = {
            "sub": "admin123",
            "tenant_id": "tenant456",
            "roles": ["admin", "farmer"],
            "exp": time.time() + 3600,
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm="HS256")

        middleware = AuthMiddleware(TEST_SECRET_KEY)
        result = middleware.verify_token(token)

        assert "admin" in result["roles"]


class TestSecurityHeaders:
    """Tests for security header handling."""

    def test_bearer_scheme_required(self, auth_middleware, mock_request, valid_token):
        """Test Bearer scheme is required in Authorization header."""
        mock_request.headers["Authorization"] = valid_token

        token = auth_middleware.extract_token(mock_request)
        assert token is None

    def test_case_sensitive_bearer(self, auth_middleware, mock_request, valid_token):
        """Test Bearer scheme is case-sensitive."""
        mock_request.headers["Authorization"] = f"bearer {valid_token}"

        token = auth_middleware.extract_token(mock_request)
        assert token is None


@pytest.mark.unit
class TestMiddlewareConfiguration:
    """Tests for middleware configuration."""

    def test_custom_excluded_paths(self):
        """Test custom excluded paths configuration."""
        middleware = AuthMiddleware(secret_key=TEST_SECRET_KEY, excluded_paths=["/custom/path", "/another/path"])

        assert middleware.is_excluded_path("/custom/path")
        assert middleware.is_excluded_path("/another/path")
        assert not middleware.is_excluded_path("/healthz")

    def test_custom_algorithm(self):
        """Test custom algorithm configuration."""
        middleware = AuthMiddleware(secret_key=TEST_SECRET_KEY, algorithm="HS384")

        assert middleware.algorithm == "HS384"


@pytest.mark.unit
class TestErrorResponses:
    """Tests for error response formatting."""

    @pytest.mark.asyncio
    async def test_401_response_format(self, auth_middleware, mock_request):
        """Test 401 response format."""
        mock_request.path = "/api/v1/fields"

        async def call_next(request):
            return MockResponse(status_code=200)

        response = await auth_middleware(mock_request, call_next)

        assert response.status_code == 401
        assert "detail" in response.body

    @pytest.mark.asyncio
    async def test_error_response_no_token_leak(self, auth_middleware, mock_request, expired_token):
        """Test error response doesn't leak token info."""
        mock_request.headers["Authorization"] = f"Bearer {expired_token}"

        async def call_next(request):
            return MockResponse(status_code=200)

        response = await auth_middleware(mock_request, call_next)

        assert expired_token not in str(response.body)
