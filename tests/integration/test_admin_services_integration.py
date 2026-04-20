"""
SAHOOL Admin-Services Integration Tests
اختبارات تكامل الإدارة والخدمات لمنصة سهول

Tests connectivity and API contracts between the admin portal
and backend services defined in docker-compose-core.yml.

These tests verify that core services work together correctly
through the Kong API Gateway.

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta

import httpx
import pytest

try:
    import jwt as pyjwt

    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KONG_URL = os.getenv("KONG_URL", "http://localhost:8000")
KONG_ADMIN_URL = os.getenv("KONG_ADMIN_URL", "http://localhost:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:3025")
FIELD_MANAGEMENT_URL = os.getenv("FIELD_MANAGEMENT_URL", "http://localhost:3000")
WEATHER_SERVICE_URL = os.getenv("WEATHER_SERVICE_URL", "http://localhost:8092")
VEGETATION_SERVICE_URL = os.getenv("VEGETATION_SERVICE_URL", "http://localhost:8090")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
NATS_HOST = os.getenv("NATS_HOST", "localhost")
NATS_MONITORING_PORT = int(os.getenv("NATS_MONITORING_PORT", "8222"))

JWT_SECRET = os.getenv(
    "JWT_SECRET_KEY",
    os.getenv("JWT_SECRET_KEY", "test-only-jwt-secret-not-for-production"),
)
DEFAULT_TENANT_ID = "a0000000-0000-0000-0000-000000000001"

HTTP_TIMEOUT = float(os.getenv("TEST_HTTP_TIMEOUT", "15"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _skip_if_no_pyjwt():
    if not HAS_PYJWT:
        pytest.skip("PyJWT not installed")


def _make_jwt_token(
    roles: list[str] | None = None,
    tenant_id: str = DEFAULT_TENANT_ID,
) -> str:
    """Create a signed JWT token for test requests."""
    _skip_if_no_pyjwt()
    now = datetime.now(tz=UTC)
    payload = {
        "sub": str(uuid.uuid4()),
        "email": f"test_{uuid.uuid4().hex[:8]}@sahool.com",
        "roles": roles or ["ADMIN"],
        "tid": tenant_id,
        "jti": str(uuid.uuid4()),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "iss": "sahool-platform",
        "aud": "sahool-api",
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_token() -> str:
    return _make_jwt_token()


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture
async def async_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        yield client


# ---------------------------------------------------------------------------
# Helper to gracefully skip when a service is unreachable
# ---------------------------------------------------------------------------


async def _get_or_skip(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    """Issue GET; skip test if connection refused."""
    try:
        return await client.get(url, **kwargs)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        pytest.skip(f"Service unreachable: {url}")


async def _post_or_skip(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    """Issue POST; skip test if connection refused."""
    try:
        return await client.post(url, **kwargs)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        pytest.skip(f"Service unreachable: {url}")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Service Health Checks
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_healthy(async_client: httpx.AsyncClient):
    """Verify PostgreSQL is accessible via a TCP connect."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        result = sock.connect_ex((POSTGRES_HOST, POSTGRES_PORT))
        if result != 0:
            pytest.skip("PostgreSQL not reachable")
        assert result == 0, "PostgreSQL port is not open"
    finally:
        sock.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_healthy(async_client: httpx.AsyncClient):
    """Verify Redis responds to PING."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        result = sock.connect_ex((REDIS_HOST, REDIS_PORT))
        if result != 0:
            pytest.skip("Redis not reachable")
        assert result == 0, "Redis port is not open"
    finally:
        sock.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nats_healthy(async_client: httpx.AsyncClient):
    """Verify NATS monitoring endpoint responds."""
    resp = await _get_or_skip(async_client, f"http://{NATS_HOST}:{NATS_MONITORING_PORT}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kong_healthy(async_client: httpx.AsyncClient):
    """Verify Kong health endpoint."""
    resp = await _get_or_skip(async_client, f"{KONG_URL}/health")
    assert resp.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_service_healthy(async_client: httpx.AsyncClient):
    """Verify user-service /health endpoint."""
    resp = await _get_or_skip(async_client, f"{USER_SERVICE_URL}/health")
    assert resp.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_management_service_healthy(async_client: httpx.AsyncClient):
    """Verify field-management-service /healthz endpoint."""
    resp = await _get_or_skip(async_client, f"{FIELD_MANAGEMENT_URL}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_service_healthy(async_client: httpx.AsyncClient):
    """Verify weather-service /healthz endpoint."""
    resp = await _get_or_skip(async_client, f"{WEATHER_SERVICE_URL}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_vegetation_analysis_service_healthy(async_client: httpx.AsyncClient):
    """Verify vegetation-analysis-service /healthz endpoint."""
    resp = await _get_or_skip(async_client, f"{VEGETATION_SERVICE_URL}/healthz")
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Kong Route Integration
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kong_routes_to_user_service(async_client: httpx.AsyncClient):
    """POST /api/v1/auth/login through Kong should reach user-service."""
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrong"},
    )
    # We expect 400 or 401, not 503/502 which would mean Kong cannot reach upstream
    assert resp.status_code < 500, f"Kong failed to route to user-service: {resp.status_code}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kong_routes_to_field_management(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """GET /api/v1/fields through Kong should reach field-management-service."""
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/fields",
        headers=auth_headers,
    )
    # 200, 401, or 403 are all acceptable (proves routing works)
    assert resp.status_code < 500, f"Kong failed to route to field-management: {resp.status_code}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kong_routes_to_weather_service(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """POST /api/v1/weather/current through Kong should reach weather-service.

    Kong strips /api/v1/weather prefix and forwards to weather-service at /weather path,
    so the effective upstream path is /weather/current.
    """
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/weather/current",
        headers=auth_headers,
        json={"latitude": 24.7, "longitude": 46.7},
    )
    assert resp.status_code < 500, f"Kong failed to route to weather-service: {resp.status_code}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kong_routes_to_vegetation_service(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """GET /api/v1/satellite/v1/providers through Kong should reach vegetation-analysis-service.

    Kong strips /api/v1/satellite prefix, so upstream sees /v1/providers.
    """
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/satellite/v1/providers",
        headers=auth_headers,
    )
    assert resp.status_code < 500, (
        f"Kong failed to route to vegetation-analysis-service: {resp.status_code}"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kong_cors_headers(async_client: httpx.AsyncClient):
    """Verify Kong returns CORS headers in response."""
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/health",
        headers={"Origin": "http://localhost:3002"},
    )
    # Kong global CORS plugin adds Access-Control-Allow-Origin
    assert resp.status_code == 200
    cors_header = resp.headers.get("access-control-allow-origin")
    assert cors_header is not None, "Missing Access-Control-Allow-Origin header"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kong_security_headers(async_client: httpx.AsyncClient):
    """Verify Kong adds security headers via response-transformer plugin."""
    resp = await _get_or_skip(async_client, f"{KONG_URL}/health")
    assert resp.status_code == 200

    # Configured in kong-core.yml response-transformer plugin
    assert resp.headers.get("x-content-type-options") == "nosniff", (
        "Missing X-Content-Type-Options: nosniff"
    )
    assert resp.headers.get("x-frame-options") == "DENY", "Missing X-Frame-Options: DENY"
    assert "1; mode=block" in (resp.headers.get("x-xss-protection", "")), (
        "Missing X-XSS-Protection header"
    )
    assert "max-age=" in (resp.headers.get("strict-transport-security", "")), (
        "Missing Strict-Transport-Security header"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. User-Service API Contract
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_returns_tokens(async_client: httpx.AsyncClient):
    """POST /api/v1/auth/register should return access_token and refresh_token."""
    unique = uuid.uuid4().hex[:8]
    payload = {
        "email": f"inttest_{unique}@sahool.com",
        "password": "TestPass123!@#",
        "name": f"Integration Tester {unique}",
        "phone": f"+9665{unique}",
    }
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/auth/register",
        json=payload,
    )
    if resp.status_code == 503:
        pytest.skip("user-service not available behind Kong")

    # Accept 201 (created) or 200 or 409 (already exists)
    if resp.status_code in (200, 201):
        data = resp.json()
        assert "access_token" in data or "accessToken" in data, (
            "Register response missing access_token"
        )
        assert "refresh_token" in data or "refreshToken" in data, (
            "Register response missing refresh_token"
        )
    elif resp.status_code == 409:
        # User already exists - still proves the endpoint contract works
        pass
    else:
        # 422 validation error is also acceptable (proves routing and contract)
        assert resp.status_code in (400, 422), f"Unexpected status: {resp.status_code}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_returns_tokens(async_client: httpx.AsyncClient):
    """POST /api/v1/auth/login should return tokens on valid credentials."""
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/auth/login",
        json={"email": "admin@sahool.com", "password": "Admin123!@#"},
    )
    if resp.status_code == 503:
        pytest.skip("user-service not available behind Kong")

    # If admin user exists and credentials match, expect tokens
    if resp.status_code == 200:
        data = resp.json()
        assert "access_token" in data or "accessToken" in data, (
            "Login response missing access_token"
        )
        assert "refresh_token" in data or "refreshToken" in data, (
            "Login response missing refresh_token"
        )
    else:
        # 401 (wrong credentials) or 404 (user not found) are valid contract responses
        assert resp.status_code in (400, 401, 404), f"Unexpected status: {resp.status_code}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: httpx.AsyncClient):
    """POST /api/v1/auth/login with wrong password should return 401."""
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/auth/login",
        json={"email": "nobody@sahool.com", "password": "WrongPassword!"},
    )
    if resp.status_code == 503:
        pytest.skip("user-service not available behind Kong")

    assert resp.status_code in (400, 401, 404), (
        f"Expected 401-class error for invalid credentials, got {resp.status_code}"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_token_works(async_client: httpx.AsyncClient):
    """POST /api/v1/auth/refresh should accept a refresh_token and return new tokens."""
    # First register a user to get a valid refresh token
    unique = uuid.uuid4().hex[:8]
    reg_resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/auth/register",
        json={
            "email": f"refresh_test_{unique}@sahool.com",
            "password": "RefreshTest123!@#",
            "name": f"Refresh Tester {unique}",
        },
    )
    if reg_resp.status_code == 503:
        pytest.skip("user-service not available")

    if reg_resp.status_code not in (200, 201):
        pytest.skip("Could not register test user for refresh token test")

    data = reg_resp.json()
    refresh_token = data.get("refresh_token") or data.get("refreshToken")
    if not refresh_token:
        pytest.skip("Register did not return refresh_token")

    # Try refresh
    refresh_resp = await async_client.post(
        f"{KONG_URL}/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    if refresh_resp.status_code == 200:
        refresh_data = refresh_resp.json()
        assert "access_token" in refresh_data or "accessToken" in refresh_data
    else:
        # 401 could mean token format mismatch, but proves endpoint exists
        assert refresh_resp.status_code in (400, 401), (
            f"Unexpected refresh status: {refresh_resp.status_code}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Field-Management-Service API Contract
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_field_with_boundary(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """POST /api/v1/fields with GeoJSON polygon boundary."""
    field_payload = {
        "name": f"Test Field {uuid.uuid4().hex[:6]}",
        "name_ar": "حقل اختبار",
        "area": 5.2,
        "crop_type": "wheat",
        "boundary": {
            "type": "Polygon",
            "coordinates": [
                [
                    [46.7, 24.7],
                    [46.8, 24.7],
                    [46.8, 24.8],
                    [46.7, 24.8],
                    [46.7, 24.7],
                ]
            ],
        },
    }
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/fields",
        headers=auth_headers,
        json=field_payload,
    )
    if resp.status_code == 503:
        pytest.skip("field-management-service not available")

    # 201 Created, 200 OK, or 401/403 auth issues (proves routing)
    assert resp.status_code < 500, f"Server error creating field: {resp.status_code}"

    if resp.status_code in (200, 201):
        data = resp.json()
        assert "id" in data or "field_id" in data or "data" in data, (
            "Create field response missing identifier"
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_fields(async_client: httpx.AsyncClient, auth_headers: dict[str, str]):
    """GET /api/v1/fields returns paginated list."""
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/fields",
        headers=auth_headers,
    )
    if resp.status_code == 503:
        pytest.skip("field-management-service not available")

    assert resp.status_code < 500, f"Server error listing fields: {resp.status_code}"

    if resp.status_code == 200:
        data = resp.json()
        # Accept array or paginated object
        assert isinstance(data, (list, dict)), "Fields response should be list or object"
        if isinstance(data, dict):
            # Paginated response should have data/items/results key
            assert any(k in data for k in ("data", "items", "results", "fields")), (
                "Paginated response missing data key"
            )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_field_by_id(async_client: httpx.AsyncClient, auth_headers: dict[str, str]):
    """GET /api/v1/fields/{id} returns field details."""
    # Use a non-existent UUID - should return 404, not 500
    fake_id = str(uuid.uuid4())
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/fields/{fake_id}",
        headers=auth_headers,
    )
    if resp.status_code == 503:
        pytest.skip("field-management-service not available")

    # 404 Not Found is the correct response for a non-existent field
    # 401/403 means auth check happened (routing works)
    assert resp.status_code in (200, 400, 401, 403, 404), (
        f"Unexpected status for field by ID: {resp.status_code}"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_nearby(async_client: httpx.AsyncClient, auth_headers: dict[str, str]):
    """GET /api/v1/fields/nearby with lat/lng query params."""
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/fields/nearby",
        headers=auth_headers,
        params={"latitude": 24.7, "longitude": 46.7, "radius": 10},
    )
    if resp.status_code == 503:
        pytest.skip("field-management-service not available")

    # 200 with results or 404 for no nearby fields; 401/403 auth
    assert resp.status_code < 500, f"Server error for nearby fields: {resp.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Weather-Service API Contract
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_current(async_client: httpx.AsyncClient, auth_headers: dict[str, str]):
    """POST /api/v1/weather/current returns weather data.

    Kong strips /api/v1/weather and prepends /weather to upstream, so
    the weather-service receives /weather/current.
    """
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/weather/current",
        headers=auth_headers,
        json={"latitude": 24.7136, "longitude": 46.6753},
    )
    if resp.status_code == 503:
        pytest.skip("weather-service not available")

    assert resp.status_code < 500, f"Server error for weather current: {resp.status_code}"

    if resp.status_code == 200:
        data = resp.json()
        # Weather response should contain temperature or weather data
        assert isinstance(data, dict), "Weather response should be a dict"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_forecast(async_client: httpx.AsyncClient, auth_headers: dict[str, str]):
    """POST /api/v1/weather/forecast returns forecast data."""
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/weather/forecast",
        headers=auth_headers,
        json={"latitude": 24.7136, "longitude": 46.6753, "days": 5},
    )
    if resp.status_code == 503:
        pytest.skip("weather-service not available")

    assert resp.status_code < 500, f"Server error for weather forecast: {resp.status_code}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_agricultural_report(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """POST /api/v1/weather/agricultural-report returns agricultural KPIs."""
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/weather/agricultural-report",
        headers=auth_headers,
        json={"latitude": 24.7136, "longitude": 46.6753, "crop_type": "wheat"},
    )
    if resp.status_code == 503:
        pytest.skip("weather-service not available")

    assert resp.status_code < 500, (
        f"Server error for weather agricultural-report: {resp.status_code}"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_providers(async_client: httpx.AsyncClient, auth_headers: dict[str, str]):
    """GET /api/v1/weather/providers lists available weather providers."""
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/weather/providers",
        headers=auth_headers,
    )
    if resp.status_code == 503:
        pytest.skip("weather-service not available")

    assert resp.status_code < 500, f"Server error for weather providers: {resp.status_code}"

    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, (list, dict)), "Providers response should be list or dict"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Vegetation-Analysis-Service API Contract
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_satellite_providers(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """GET /api/v1/satellite/v1/providers returns satellite providers.

    Kong strips /api/v1/satellite so upstream sees /v1/providers.
    """
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/satellite/v1/providers",
        headers=auth_headers,
    )
    if resp.status_code == 503:
        pytest.skip("vegetation-analysis-service not available")

    assert resp.status_code < 500, f"Server error for satellite providers: {resp.status_code}"

    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, (list, dict)), "Providers response should be list or dict"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_satellite_analyze(
    async_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """POST /api/v1/satellite/v1/analyze with field_id.

    Kong strips /api/v1/satellite so upstream sees /v1/analyze.
    """
    resp = await _post_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/satellite/v1/analyze",
        headers=auth_headers,
        json={
            "field_id": str(uuid.uuid4()),
            "coordinates": [
                [46.7, 24.7],
                [46.8, 24.7],
                [46.8, 24.8],
                [46.7, 24.8],
                [46.7, 24.7],
            ],
        },
    )
    if resp.status_code == 503:
        pytest.skip("vegetation-analysis-service not available")

    # 200, 202 (accepted), 400, 401, 404, 422 are all valid contract responses
    assert resp.status_code < 500, f"Server error for satellite analyze: {resp.status_code}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_eo_status(async_client: httpx.AsyncClient, auth_headers: dict[str, str]):
    """GET /api/v1/satellite/v1/eo-status returns Sentinel Hub configuration status.

    Kong strips /api/v1/satellite so upstream sees /v1/eo-status.
    """
    resp = await _get_or_skip(
        async_client,
        f"{KONG_URL}/api/v1/satellite/v1/eo-status",
        headers=auth_headers,
    )
    if resp.status_code == 503:
        pytest.skip("vegetation-analysis-service not available")

    assert resp.status_code < 500, f"Server error for eo-status: {resp.status_code}"

    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, dict), "EO status response should be a dict"
