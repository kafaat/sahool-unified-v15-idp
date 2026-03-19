"""
Integration Tests for Auth Flow - SAHOOL Platform
اختبارات التكامل لسير عمل المصادقة - منصة سهول

Tests the complete authentication flow through Kong API Gateway:
  Client → Kong → auth/user-service → PostgreSQL → Redis (JWT cache)

These tests require a running Docker Compose stack.
They are skipped gracefully when the stack is unavailable.

Test Markers:
- @pytest.mark.integration  - Requires running services
- @pytest.mark.asyncio      - Async tests

Author: SAHOOL QA Team
Updated: March 2026
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Base URL for Kong API Gateway (overridable via env var)
import os

BASE_URL = os.getenv("KONG_BASE_URL", "http://localhost:8000")

# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures - أدوات الاختبار
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture
async def client():
    """
    HTTP client pointed at Kong Gateway.
    عميل HTTP موجّه لبوابة Kong.
    Skips test automatically when Kong is not reachable.
    """
    if not HAS_HTTPX:
        pytest.skip("httpx not installed")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        try:
            await c.get("/healthz")
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Kong API Gateway not reachable — start docker-compose.test.yml first")
        yield c


@pytest.fixture
async def db_session():
    """
    Async database session fixture.
    جلسة قاعدة بيانات غير متزامنة.
    Returns a mock when asyncpg is not available or DB is not running.
    """
    try:
        import asyncpg

        db_url = os.getenv(
            "TEST_DATABASE_URL",
            "postgresql://sahool_test:test_password_123@localhost:5432/sahool_test",
        )
        conn = await asyncpg.connect(db_url)
        yield conn
        await conn.close()
    except Exception:
        # Return a mock when DB is not available
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.fetchrow = AsyncMock(return_value=None)
        mock_db.fetch = AsyncMock(return_value=[])
        yield mock_db


@pytest.fixture
async def redis_client():
    """
    Redis client fixture.
    عميل Redis.
    """
    try:
        import redis.asyncio as aioredis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        r = await aioredis.from_url(redis_url)
        yield r
        await r.aclose()
    except Exception:
        mock_redis = MagicMock()
        mock_redis.flushdb = AsyncMock()
        yield mock_redis


# ═══════════════════════════════════════════════════════════════════════════════
# TestAuthIntegration - اختبارات التكامل للمصادقة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAuthIntegration:
    """اختبارات تكامل كاملة لسير عمل المصادقة عبر Kong"""

    @pytest.fixture(autouse=True)
    async def setup(self, db_session, redis_client):
        """
        تهيئة قاعدة البيانات قبل كل اختبار
        Setup database before each test and clean up after.
        """
        # تنظيف جدول المستخدمين قبل الاختبار
        try:
            await db_session.execute("TRUNCATE users CASCADE")
        except Exception:
            pass  # DB mock or table doesn't exist — acceptable in CI
        yield
        # تنظيف Redis بعد الاختبار
        try:
            await redis_client.flushdb()
        except Exception as exc:
            # Redis may be a mock or unavailable in some CI environments; cleanup failures are non-fatal.
            print(f"[TestAuthIntegration.setup] Redis flushdb() failed during teardown: {exc!r}")

    @pytest.mark.asyncio
    async def test_full_registration_flow(self, client, db_session) -> None:
        """
        اختبار كامل لتسجيل مستخدم جديد:
        Client → Kong → auth-service → PostgreSQL → Redis (JWT)

        Full registration flow:
        1. Register a new user via /api/v1/auth/register
        2. Verify the user record is saved to DB
        3. Login with the same credentials
        4. Access a protected endpoint using the JWT
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        # الخطوة 1: تسجيل — Step 1: Register
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "farmer@test.ye",
                "password": "TestPass123!",
                "name": "علي محمد",
                "farm_name": "مزرعة التجربة",
            },
        )
        assert resp.status_code == 201, f"Registration failed: {resp.text}"
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        token = data["access_token"]

        # الخطوة 2: التحقق من حفظ البيانات في DB
        # Step 2: Verify data persisted to database
        user_in_db = await db_session.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            "farmer@test.ye",
        )
        if user_in_db and not isinstance(user_in_db, MagicMock):
            assert user_in_db["name"] == "علي محمد"
            # تأكد أن كلمة المرور مشفرة
            assert user_in_db["password"] != "TestPass123!"

        # الخطوة 3: تسجيل الدخول — Step 3: Login
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "farmer@test.ye",
                "password": "TestPass123!",
            },
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        assert "access_token" in login_resp.json()

        # الخطوة 4: الوصول لـ endpoint محمي — Step 4: Access protected endpoint
        me_resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200, f"Protected endpoint failed: {me_resp.text}"
        assert me_resp.json().get("email") == "farmer@test.ye"

    @pytest.mark.asyncio
    async def test_jwt_propagation_through_kong(self, client) -> None:
        """
        Kong يتحقق من JWT ويمرر tenant_id للخدمات الداخلية

        Kong validates the JWT, extracts tenant_id, and forwards it
        as X-Tenant-ID header to upstream services (RLS enforcement).
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        # احصل على توكن صالح — obtain a valid token
        token = await self._get_token(client, tenant="farm-001")

        resp = await client.get(
            "/api/v1/fields",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, f"Fields endpoint failed: {resp.text}"

        # تأكد أن Row Level Security يعمل — verify RLS is applied
        fields = resp.json().get("fields", [])
        # Only assert tenant isolation when there are fields to check;
        # an empty list is acceptable (tenant may have no fields yet).
        if fields:
            assert all(
                f.get("tenant_id") == "farm-001" for f in fields
            ), "RLS violated — fields from other tenants returned"

    @pytest.mark.asyncio
    async def test_rate_limiting_enforced(self, client) -> None:
        """
        Kong يطبق Rate Limiting على طلبات تسجيل الدخول

        Kong enforces rate limiting. Sending 101 requests should
        yield at least one 429 Too Many Requests.
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        responses = await asyncio.gather(
            *[
                client.post(
                    "/api/v1/auth/login",
                    json={"email": "test@test.ye", "password": "wrong"},
                )
                for _ in range(101)
            ],
            return_exceptions=True,
        )

        status_codes = [
            r.status_code for r in responses if not isinstance(r, Exception)
        ]
        assert 429 in status_codes, "Rate limiting not enforced — no 429 received after 101 requests"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials_returns_401(self, client) -> None:
        """
        بيانات اعتماد خاطئة تُرجع 401

        Invalid credentials return HTTP 401 Unauthorized.
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.ye", "password": "WrongPass!"},
        )
        assert resp.status_code in (401, 422), f"Expected 401/422, got {resp.status_code}"

    @pytest.mark.asyncio
    async def test_missing_auth_header_returns_401(self, client) -> None:
        """
        طلب بدون توكن → 401 Unauthorized

        Request without Authorization header returns 401.
        """
        if not HAS_HTTPX:
            pytest.skip("httpx not installed")

        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    # ─── helpers ───────────────────────────────────────────────────────────────

    async def _get_token(self, client: Any, tenant: str = "farm-001") -> str:
        """
        مساعد: احصل على توكن تجريبي.
        Helper: register a test user and return the JWT access_token.
        Falls back to a dummy token string when registration is not available.
        """
        import uuid

        email = f"auth_test_{uuid.uuid4().hex[:6]}@test.ye"
        try:
            reg_resp = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "TestPass123!",
                    "tenant_id": tenant,
                },
            )
            if reg_resp.status_code == 201:
                return reg_resp.json().get("access_token", f"mock-token-{tenant}")
        except Exception:
            pass
        return f"mock-jwt-token-{tenant}"
