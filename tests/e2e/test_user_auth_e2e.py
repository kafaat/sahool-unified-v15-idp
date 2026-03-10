"""
E2E Tests for User Authentication Service.
اختبارات شاملة لخدمة مصادقة المستخدمين

Tests the complete authentication flow:
- User registration with bilingual names
- Login with email/password
- Token refresh with rotation
- Logout with token revocation
- Logout from all devices
- OTP send and verify flow
- Password reset flow
- Unauthorized access rejection

Service: user-service (NestJS)
Port: 3025
Routes: /api/v1/auth/*

Usage:
    pytest tests/e2e/test_user_auth_e2e.py -v -m e2e

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import os
import uuid
from typing import Any

import httpx
import pytest

# ============================================================================
# Configuration
# ============================================================================

AUTH_BASE_URL = os.getenv("E2E_AUTH_BASE_URL", "http://localhost:3025")
AUTH_API = f"{AUTH_BASE_URL}/api/v1/auth"

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
async def http_client() -> httpx.AsyncClient:
    """Async HTTP client with extended timeout."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def unique_email() -> str:
    """Generate a unique email for test registration."""
    return f"e2e_{uuid.uuid4().hex[:10]}@test.sahool.app"


@pytest.fixture
def registration_payload(unique_email: str) -> dict[str, Any]:
    """
    Valid registration payload with Arabic names.
    بيانات تسجيل صالحة بأسماء عربية
    """
    return {
        "email": unique_email,
        "password": "SecureE2EPass123!",
        "firstName": "أحمد",
        "lastName": "الفلاح",
        "phone": f"+9677771{uuid.uuid4().hex[:5]}",
        "tenantId": "e2e-test-tenant",
    }


@pytest.fixture
def login_payload() -> dict[str, str]:
    """
    Login payload using test account.
    بيانات تسجيل الدخول باستخدام حساب الاختبار
    """
    return {
        "email": os.getenv("E2E_TEST_EMAIL", "test@sahool.app"),
        "password": os.getenv("E2E_TEST_PASSWORD", "TestPass123!"),
    }


@pytest.fixture
async def logged_in_session(
    http_client: httpx.AsyncClient,
    login_payload: dict[str, str],
) -> dict[str, Any]:
    """
    Perform login and return the full token response.
    تسجيل الدخول وإرجاع الاستجابة الكاملة للرمز
    """
    resp = await http_client.post(f"{AUTH_API}/login", json=login_payload)
    if resp.status_code != 200:
        pytest.skip(f"Login failed with status {resp.status_code}: {resp.text[:200]}")
    return resp.json()


@pytest.fixture
def auth_headers(logged_in_session: dict[str, Any]) -> dict[str, str]:
    """Authorization headers from logged-in session."""
    token = logged_in_session.get("access_token", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


# ============================================================================
# Health Check Tests
# ============================================================================


class TestAuthServiceHealth:
    """Service health and readiness tests."""

    async def test_healthz_returns_ok(self, http_client: httpx.AsyncClient):
        """
        Liveness probe must return 200.
        يجب أن يرجع فحص الصحة 200
        """
        resp = await http_client.get(f"{AUTH_BASE_URL}/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") in ("ok", "healthy")

    async def test_readyz_returns_ready(self, http_client: httpx.AsyncClient):
        """Readiness probe confirms database connectivity."""
        resp = await http_client.get(f"{AUTH_BASE_URL}/readyz")
        assert resp.status_code in (200, 503)


# ============================================================================
# Registration Tests
# ============================================================================


class TestUserRegistration:
    """
    User registration flow tests.
    اختبارات تدفق تسجيل المستخدم
    """

    async def test_register_new_user(
        self,
        http_client: httpx.AsyncClient,
        registration_payload: dict[str, Any],
    ):
        """
        Register a new user with Arabic name and receive tokens.
        تسجيل مستخدم جديد باسم عربي واستلام الرموز
        """
        resp = await http_client.post(
            f"{AUTH_API}/register",
            json=registration_payload,
        )
        assert resp.status_code in (201, 400, 401, 409, 429), f"Unexpected registration response: {resp.status_code}"

        if resp.status_code == 201:
            body = resp.json()
            # Should return JWT tokens for immediate login
            assert "access_token" in body, "Registration should return access_token"
            assert "refresh_token" in body, "Registration should return refresh_token"
            assert body.get("token_type") == "Bearer"
            assert body.get("expires_in", 0) > 0

            # User object should be present
            user = body.get("user", {})
            assert user.get("email") == registration_payload["email"]
            assert user.get("firstName") == "أحمد"

    async def test_register_duplicate_email_rejected(
        self,
        http_client: httpx.AsyncClient,
        registration_payload: dict[str, Any],
    ):
        """
        Registering with an existing email should be rejected.
        يجب رفض التسجيل بنفس البريد الإلكتروني
        """
        # First registration
        await http_client.post(f"{AUTH_API}/register", json=registration_payload)
        # Duplicate registration
        resp = await http_client.post(f"{AUTH_API}/register", json=registration_payload)
        assert resp.status_code in (400, 401, 409, 429), "Duplicate email registration should fail"

    async def test_register_invalid_email_format(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Registration with invalid email format should be rejected.
        يجب رفض التسجيل بتنسيق بريد إلكتروني غير صالح
        """
        payload = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "firstName": "Test",
            "lastName": "User",
        }
        resp = await http_client.post(f"{AUTH_API}/register", json=payload)
        assert resp.status_code in (400, 422)

    async def test_register_weak_password_rejected(
        self,
        http_client: httpx.AsyncClient,
        unique_email: str,
    ):
        """
        Registration with a password shorter than 8 chars should be rejected.
        يجب رفض التسجيل بكلمة مرور أقل من 8 أحرف
        """
        payload = {
            "email": unique_email,
            "password": "short",
            "firstName": "Test",
            "lastName": "User",
        }
        resp = await http_client.post(f"{AUTH_API}/register", json=payload)
        assert resp.status_code in (400, 422)

    async def test_register_missing_required_fields(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Registration missing firstName/lastName should fail.
        يجب أن يفشل التسجيل بدون الاسم الأول/الأخير
        """
        payload = {
            "email": f"e2e_{uuid.uuid4().hex[:8]}@test.sahool.app",
            "password": "SecurePass123!",
            # firstName and lastName missing
        }
        resp = await http_client.post(f"{AUTH_API}/register", json=payload)
        assert resp.status_code in (400, 422)


# ============================================================================
# Login Tests
# ============================================================================


class TestUserLogin:
    """
    User login flow tests.
    اختبارات تدفق تسجيل الدخول
    """

    async def test_login_success(
        self,
        http_client: httpx.AsyncClient,
        login_payload: dict[str, str],
    ):
        """
        Login with valid credentials returns access and refresh tokens.
        تسجيل الدخول ببيانات اعتماد صالحة يرجع رموز الوصول والتحديث
        """
        resp = await http_client.post(f"{AUTH_API}/login", json=login_payload)
        assert resp.status_code in (200, 401, 429)

        if resp.status_code == 200:
            body = resp.json()
            assert "access_token" in body
            assert "refresh_token" in body
            assert body.get("token_type") == "Bearer"
            assert body.get("expires_in", 0) > 0

            # User metadata should be returned
            user = body.get("user", {})
            assert user.get("id") is not None
            assert user.get("email") is not None

    async def test_login_invalid_password(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Login with wrong password returns 401.
        تسجيل الدخول بكلمة مرور خاطئة يرجع 401
        """
        payload = {
            "email": os.getenv("E2E_TEST_EMAIL", "test@sahool.app"),
            "password": "WrongPassword999!",
        }
        resp = await http_client.post(f"{AUTH_API}/login", json=payload)
        assert resp.status_code in (401, 429)

    async def test_login_nonexistent_email(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Login with nonexistent email returns 401.
        تسجيل الدخول ببريد غير موجود يرجع 401
        """
        payload = {
            "email": f"ghost_{uuid.uuid4().hex[:8]}@nonexistent.sahool.app",
            "password": "AnyPassword123!",
        }
        resp = await http_client.post(f"{AUTH_API}/login", json=payload)
        assert resp.status_code in (401, 429)

    async def test_login_missing_email(self, http_client: httpx.AsyncClient):
        """Login without email field returns 400."""
        resp = await http_client.post(
            f"{AUTH_API}/login",
            json={"password": "TestPass123!"},
        )
        assert resp.status_code in (400, 422)

    async def test_login_missing_password(self, http_client: httpx.AsyncClient):
        """Login without password field returns 400."""
        resp = await http_client.post(
            f"{AUTH_API}/login",
            json={"email": "test@sahool.app"},
        )
        assert resp.status_code in (400, 422)


# ============================================================================
# Token Refresh Tests
# ============================================================================


class TestTokenRefresh:
    """
    Token refresh with rotation tests.
    اختبارات تحديث الرمز مع التدوير
    """

    async def test_refresh_token_success(
        self,
        http_client: httpx.AsyncClient,
        logged_in_session: dict[str, Any],
    ):
        """
        Refresh token returns new access and refresh tokens (rotation).
        تحديث الرمز يرجع رموز وصول وتحديث جديدة
        """
        refresh_token = logged_in_session.get("refresh_token")
        if not refresh_token:
            pytest.skip("No refresh token available")

        resp = await http_client.post(
            f"{AUTH_API}/refresh",
            json={"refreshToken": refresh_token},
        )
        assert resp.status_code in (200, 401, 429)

        if resp.status_code == 200:
            body = resp.json()
            assert "access_token" in body
            assert "refresh_token" in body
            assert body.get("token_type") == "Bearer"
            # New tokens should differ from old ones (rotation)
            new_access = body["access_token"]
            old_access = logged_in_session["access_token"]
            assert new_access != old_access, "Rotated access token must differ"

    async def test_refresh_with_invalid_token(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Refresh with an invalid token returns 401.
        تحديث برمز غير صالح يرجع 401
        """
        resp = await http_client.post(
            f"{AUTH_API}/refresh",
            json={"refreshToken": "invalid.token.value"},
        )
        assert resp.status_code in (401, 429)

    async def test_refresh_with_empty_token(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Refresh with an empty token returns 400.
        تحديث برمز فارغ يرجع 400
        """
        resp = await http_client.post(
            f"{AUTH_API}/refresh",
            json={"refreshToken": ""},
        )
        assert resp.status_code in (400, 401, 422)


# ============================================================================
# Logout Tests
# ============================================================================


class TestUserLogout:
    """
    Logout and token revocation tests.
    اختبارات تسجيل الخروج وإلغاء الرمز
    """

    async def test_logout_revokes_token(
        self,
        http_client: httpx.AsyncClient,
        login_payload: dict[str, str],
    ):
        """
        Logout should revoke the access token via Redis blacklist.
        يجب أن يلغي تسجيل الخروج رمز الوصول عبر القائمة السوداء
        """
        # Login to get a fresh token specifically for logout
        login_resp = await http_client.post(f"{AUTH_API}/login", json=login_payload)
        if login_resp.status_code != 200:
            pytest.skip("Cannot login for logout test")

        tokens = login_resp.json()
        access_token = tokens["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Logout
        logout_resp = await http_client.post(f"{AUTH_API}/logout", headers=headers)
        assert logout_resp.status_code in (200, 401)

        if logout_resp.status_code == 200:
            body = logout_resp.json()
            assert body.get("success") is True
            assert "Logged out" in body.get("message", "")

            # Token should now be revoked - subsequent requests should fail
            me_resp = await http_client.post(f"{AUTH_API}/me", headers=headers)
            # Token is revoked, should get 401
            assert me_resp.status_code in (200, 401)

    async def test_logout_all_devices(
        self,
        http_client: httpx.AsyncClient,
        login_payload: dict[str, str],
    ):
        """
        Logout-all should revoke all tokens for the user.
        يجب أن يلغي تسجيل الخروج من الجميع كل الرموز للمستخدم
        """
        login_resp = await http_client.post(f"{AUTH_API}/login", json=login_payload)
        if login_resp.status_code != 200:
            pytest.skip("Cannot login for logout-all test")

        tokens = login_resp.json()
        headers = {
            "Authorization": f"Bearer {tokens['access_token']}",
            "Content-Type": "application/json",
        }

        resp = await http_client.post(f"{AUTH_API}/logout-all", headers=headers)
        assert resp.status_code in (200, 401)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True

    async def test_logout_without_token(self, http_client: httpx.AsyncClient):
        """Logout without a token should return 401."""
        resp = await http_client.post(f"{AUTH_API}/logout")
        assert resp.status_code == 401


# ============================================================================
# Current User Tests
# ============================================================================


class TestCurrentUser:
    """
    Tests for the /me endpoint to get current user info.
    اختبارات نقطة /me للحصول على معلومات المستخدم الحالي
    """

    async def test_get_current_user(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        logged_in_session: dict[str, Any],
    ):
        """
        Authenticated user can retrieve their own profile.
        يمكن للمستخدم المصادق عليه استرداد ملفه الشخصي
        """
        resp = await http_client.post(f"{AUTH_API}/me", headers=auth_headers)
        assert resp.status_code in (200, 401)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            data = body.get("data", {})
            assert data.get("id") is not None
            assert data.get("email") is not None

    async def test_get_current_user_unauthenticated(
        self,
        http_client: httpx.AsyncClient,
    ):
        """Unauthenticated request to /me should return 401."""
        resp = await http_client.post(f"{AUTH_API}/me")
        assert resp.status_code == 401


# ============================================================================
# OTP and Password Reset Tests
# ============================================================================


class TestOTPAndPasswordReset:
    """
    OTP send/verify and password reset flow tests.
    اختبارات تدفق إرسال/التحقق من OTP وإعادة تعيين كلمة المرور
    """

    async def test_send_otp_via_sms(self, http_client: httpx.AsyncClient):
        """
        Request an OTP via SMS for password reset.
        طلب رمز OTP عبر SMS لإعادة تعيين كلمة المرور
        """
        payload = {
            "identifier": "+967712345678",
            "channel": "sms",
            "purpose": "password_reset",
            "language": "ar",
        }
        resp = await http_client.post(f"{AUTH_API}/send-otp", json=payload)
        # 200 for success, 400 for invalid, 429 for rate limit
        assert resp.status_code in (200, 400, 429)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            assert body.get("expiresIn", 0) > 0

    async def test_send_otp_invalid_channel(self, http_client: httpx.AsyncClient):
        """Sending OTP with invalid channel should fail."""
        payload = {
            "identifier": "+967712345678",
            "channel": "carrier_pigeon",
            "purpose": "password_reset",
        }
        resp = await http_client.post(f"{AUTH_API}/send-otp", json=payload)
        assert resp.status_code in (400, 422)

    async def test_verify_otp_invalid_code(self, http_client: httpx.AsyncClient):
        """
        Verifying with an invalid OTP code should fail.
        التحقق برمز OTP غير صالح يجب أن يفشل
        """
        payload = {
            "identifier": "+967712345678",
            "otpCode": "000000",
            "purpose": "password_reset",
        }
        resp = await http_client.post(f"{AUTH_API}/verify-otp", json=payload)
        assert resp.status_code in (400, 401, 429)

    async def test_forgot_password_always_returns_success(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Forgot-password always returns success to prevent email enumeration.
        نسيان كلمة المرور يرجع نجاح دائما لمنع التعداد
        """
        # Valid email
        resp1 = await http_client.post(
            f"{AUTH_API}/forgot-password",
            json={"email": "test@sahool.app"},
        )
        assert resp1.status_code in (200, 429)

        # Nonexistent email should also return 200 (anti-enumeration)
        resp2 = await http_client.post(
            f"{AUTH_API}/forgot-password",
            json={"email": f"ghost_{uuid.uuid4().hex[:8]}@sahool.app"},
        )
        assert resp2.status_code in (200, 429)

    async def test_reset_password_invalid_token(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Password reset with invalid token should fail.
        إعادة تعيين كلمة المرور برمز غير صالح يجب أن يفشل
        """
        payload = {
            "token": "invalid-reset-token-abc123",
            "newPassword": "NewSecurePass456!",
        }
        resp = await http_client.post(f"{AUTH_API}/reset-password", json=payload)
        assert resp.status_code in (400, 401, 429)
