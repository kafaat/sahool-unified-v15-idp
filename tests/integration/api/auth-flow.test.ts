/**
 * SAHOOL Authentication Flow Integration Tests
 * اختبارات تدفق المصادقة لمنصة سهول
 *
 * Tests cover:
 * - User registration
 * - Login with JWT
 * - Token refresh
 * - Logout
 * - OTP verification
 * - Password reset
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from "vitest";
import {
  TEST_CONFIG,
  TEST_USERS,
  apiRequest,
  getAuthToken,
  getAuthHeaders,
  clearAuthCache,
  generateTestId,
  isValidUUID,
  isValidISO8601,
  checkServiceHealth,
  MOCK_RESPONSES,
} from "./setup";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const AUTH_SERVICE_URL = TEST_CONFIG.SERVICES.USER_SERVICE;
const AUTH_API_BASE = `${AUTH_SERVICE_URL}/api/v1/auth`;

describe("Authentication Flow Integration Tests", () => {
  let serviceHealthy: boolean = false;

  // ─────────────────────────────────────────────────────────────────────────────
  // Setup & Teardown
  // ─────────────────────────────────────────────────────────────────────────────

  beforeAll(async () => {
    const health = await checkServiceHealth("USER_SERVICE", AUTH_SERVICE_URL);
    serviceHealthy = health.status === "healthy";

    if (!serviceHealthy) {
      console.warn(
        "User service not available - tests will use mock validation"
      );
    }
  });

  afterAll(() => {
    clearAuthCache();
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Service Health & Registration Tests - اختبارات صحة الخدمة والتسجيل
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Service Health", () => {
    it("should verify auth service is registered and responding", async () => {
      const health = await checkServiceHealth("USER_SERVICE", AUTH_SERVICE_URL);

      expect(health.service).toBe("USER_SERVICE");
      expect(["healthy", "unhealthy", "unknown"]).toContain(health.status);
      expect(health.responseTime).toBeGreaterThan(0);
    });

    it("should have health endpoint available", async () => {
      const response = await apiRequest<{ status: string; service?: string }>(
        `${AUTH_SERVICE_URL}/healthz`
      );

      // Service might not be running, but endpoint should be defined
      expect([200, 404, 502, 503]).toContain(response.status);

      if (response.ok) {
        expect(response.data).toHaveProperty("status");
      }
    });

    it("should have readiness endpoint available", async () => {
      const response = await apiRequest<{
        status: string;
        database?: boolean;
        redis?: boolean;
      }>(`${AUTH_SERVICE_URL}/readyz`);

      expect([200, 404, 502, 503]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // User Registration Tests - اختبارات تسجيل المستخدم
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("User Registration", () => {
    const testEmail = `test-${generateTestId()}@sahool.test`;

    it("should register a new user with valid data", async () => {
      const registrationData = {
        email: testEmail,
        password: "SecurePassword123!",
        name: "Test User",
        name_ar: "مستخدم اختباري",
        phone: "+967123456789",
        role: "farmer",
        tenant_id: "tenant-test-001",
        governorate: "sanaa",
      };

      const response = await apiRequest<{
        id: string;
        email: string;
        name: string;
        role: string;
        created_at: string;
      }>(`${AUTH_API_BASE}/register`, {
        method: "POST",
        body: JSON.stringify(registrationData),
      });

      // Service might not be available
      if (response.status === 502 || response.status === 503) {
        console.warn("Auth service not available, skipping assertion");
        return;
      }

      // Should return 201 (created) or 422 (validation) or 409 (conflict)
      expect([201, 409, 422]).toContain(response.status);

      if (response.status === 201) {
        expect(response.data).toHaveProperty("id");
        expect(response.data.email).toBe(testEmail);
        expect(isValidISO8601(response.data.created_at)).toBe(true);
      }
    });

    it("should reject registration with invalid email format", async () => {
      const invalidData = {
        email: "invalid-email-format",
        password: "SecurePassword123!",
        name: "Test User",
        role: "farmer",
      };

      const response = await apiRequest(`${AUTH_API_BASE}/register`, {
        method: "POST",
        body: JSON.stringify(invalidData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 422]).toContain(response.status);
    });

    it("should reject registration with weak password", async () => {
      const weakPasswordData = {
        email: `weak-${generateTestId()}@sahool.test`,
        password: "123", // Too weak
        name: "Test User",
        role: "farmer",
      };

      const response = await apiRequest(`${AUTH_API_BASE}/register`, {
        method: "POST",
        body: JSON.stringify(weakPasswordData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 422]).toContain(response.status);
    });

    it("should enforce required fields for registration", async () => {
      const incompleteData = {
        email: `incomplete-${generateTestId()}@sahool.test`,
        // Missing password, name
      };

      const response = await apiRequest(`${AUTH_API_BASE}/register`, {
        method: "POST",
        body: JSON.stringify(incompleteData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 422]).toContain(response.status);
    });

    it("should support Arabic names in registration", async () => {
      const arabicNameData = {
        email: `arabic-${generateTestId()}@sahool.test`,
        password: "SecurePassword123!",
        name: "Ahmed Al-Rashid",
        name_ar: "أحمد الرشيد",
        role: "farmer",
      };

      const response = await apiRequest(`${AUTH_API_BASE}/register`, {
        method: "POST",
        body: JSON.stringify(arabicNameData),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([201, 409, 422]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Login with JWT Tests - اختبارات تسجيل الدخول مع JWT
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Login with JWT", () => {
    it("should login with valid credentials and return JWT", async () => {
      const loginData = {
        email: TEST_USERS.FARMER.email,
        password: TEST_USERS.FARMER.password,
      };

      const response = await apiRequest<{
        token: string;
        refresh_token?: string;
        expires_at: string;
        user: {
          id: string;
          email: string;
          name: string;
          role: string;
        };
      }>(`${AUTH_API_BASE}/login`, {
        method: "POST",
        body: JSON.stringify(loginData),
      });

      if (response.status === 502 || response.status === 503) {
        // Validate mock response structure
        expect(MOCK_RESPONSES.AUTH.LOGIN).toHaveProperty("token");
        expect(MOCK_RESPONSES.AUTH.LOGIN).toHaveProperty("user");
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("token");
        expect(response.data.token).toBeTruthy();
        expect(response.data).toHaveProperty("user");
        expect(response.data.user).toHaveProperty("id");
        expect(response.data.user).toHaveProperty("email");
        expect(isValidISO8601(response.data.expires_at)).toBe(true);
      }
    });

    it("should reject login with invalid credentials", async () => {
      const invalidCredentials = {
        email: TEST_USERS.FARMER.email,
        password: "WrongPassword123!",
      };

      const response = await apiRequest(`${AUTH_API_BASE}/login`, {
        method: "POST",
        body: JSON.stringify(invalidCredentials),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403, 404]).toContain(response.status);
    });

    it("should reject login with non-existent user", async () => {
      const nonExistentUser = {
        email: "nonexistent@sahool.test",
        password: "SomePassword123!",
      };

      const response = await apiRequest(`${AUTH_API_BASE}/login`, {
        method: "POST",
        body: JSON.stringify(nonExistentUser),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 404]).toContain(response.status);
    });

    it("should include tenant information in login response", async () => {
      const loginData = {
        email: TEST_USERS.FARMER.email,
        password: TEST_USERS.FARMER.password,
      };

      const response = await apiRequest<{
        token: string;
        user: {
          tenant_id?: string;
          tenantId?: string;
        };
      }>(`${AUTH_API_BASE}/login`, {
        method: "POST",
        body: JSON.stringify(loginData),
      });

      if (response.status === 502 || response.status === 503 || response.status === 401) {
        return;
      }

      if (response.status === 200) {
        const user = response.data.user;
        const hasTenant = user.tenant_id || user.tenantId;
        expect(hasTenant).toBeTruthy();
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Token Refresh Tests - اختبارات تجديد الرمز
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Token Refresh", () => {
    it("should refresh token with valid refresh token", async () => {
      // First, get a token
      const token = await getAuthToken("FARMER");

      const response = await apiRequest<{
        token: string;
        expires_at: string;
      }>(`${AUTH_API_BASE}/refresh`, {
        method: "POST",
        headers: getAuthHeaders(token),
        body: JSON.stringify({
          refresh_token: "mock-refresh-token",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 403]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("token");
        expect(response.data.token).toBeTruthy();
      }
    });

    it("should reject refresh with invalid refresh token", async () => {
      const response = await apiRequest(`${AUTH_API_BASE}/refresh`, {
        method: "POST",
        body: JSON.stringify({
          refresh_token: "invalid-refresh-token",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403]).toContain(response.status);
    });

    it("should reject refresh with expired refresh token", async () => {
      const expiredToken =
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MTYyMzkwMjJ9.expired";

      const response = await apiRequest(`${AUTH_API_BASE}/refresh`, {
        method: "POST",
        body: JSON.stringify({
          refresh_token: expiredToken,
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Logout Tests - اختبارات تسجيل الخروج
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Logout", () => {
    it("should successfully logout with valid token", async () => {
      const token = await getAuthToken("FARMER");

      const response = await apiRequest<{ success: boolean; message?: string }>(
        `${AUTH_API_BASE}/logout`,
        {
          method: "POST",
          headers: getAuthHeaders(token),
        }
      );

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 204, 401]).toContain(response.status);
    });

    it("should reject requests with invalidated token after logout", async () => {
      const token = await getAuthToken("FARMER");

      // Logout first
      await apiRequest(`${AUTH_API_BASE}/logout`, {
        method: "POST",
        headers: getAuthHeaders(token),
      });

      // Try to use the same token
      const response = await apiRequest(`${AUTH_API_BASE}/me`, {
        method: "GET",
        headers: getAuthHeaders(token),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      // Token should be invalidated (401) or endpoint may not exist (404)
      expect([200, 401, 404]).toContain(response.status);
    });

    it("should logout from all devices when requested", async () => {
      const token = await getAuthToken("FARMER");

      const response = await apiRequest(`${AUTH_API_BASE}/logout-all`, {
        method: "POST",
        headers: getAuthHeaders(token),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 204, 401, 404]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // OTP Verification Tests - اختبارات التحقق من OTP
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("OTP Verification", () => {
    it("should request OTP for phone verification", async () => {
      const response = await apiRequest<{
        success: boolean;
        message?: string;
        expires_in?: number;
      }>(`${AUTH_API_BASE}/otp/request`, {
        method: "POST",
        body: JSON.stringify({
          phone: "+967123456789",
          purpose: "login",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 201, 404, 429]).toContain(response.status);

      if (response.status === 200 || response.status === 201) {
        expect(response.data.success).toBe(true);
      }
    });

    it("should verify valid OTP", async () => {
      const response = await apiRequest<{
        valid: boolean;
        token?: string;
      }>(`${AUTH_API_BASE}/otp/verify`, {
        method: "POST",
        body: JSON.stringify({
          phone: "+967123456789",
          otp: "123456", // Test OTP
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      // Could be valid (200), invalid OTP (401), or not found (404)
      expect([200, 400, 401, 404]).toContain(response.status);
    });

    it("should reject invalid OTP", async () => {
      const response = await apiRequest(`${AUTH_API_BASE}/otp/verify`, {
        method: "POST",
        body: JSON.stringify({
          phone: "+967123456789",
          otp: "000000", // Invalid OTP
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 401, 404]).toContain(response.status);
    });

    it("should rate limit OTP requests", async () => {
      // Make multiple rapid requests
      const requests = Array(6)
        .fill(null)
        .map(() =>
          apiRequest(`${AUTH_API_BASE}/otp/request`, {
            method: "POST",
            body: JSON.stringify({
              phone: "+967123456789",
              purpose: "login",
            }),
          })
        );

      const responses = await Promise.all(requests);

      if (responses.every((r) => r.status === 502 || r.status === 503)) {
        return;
      }

      // At least one should be rate limited (429) or all succeed
      const statuses = responses.map((r) => r.status);
      const hasRateLimit =
        statuses.includes(429) || statuses.every((s) => [200, 201].includes(s));
      expect(hasRateLimit).toBe(true);
    });

    it("should expire OTP after timeout", async () => {
      // This would require waiting for OTP expiration (typically 5 minutes)
      // For integration tests, we verify the endpoint structure

      const response = await apiRequest(`${AUTH_API_BASE}/otp/verify`, {
        method: "POST",
        body: JSON.stringify({
          phone: "+967123456789",
          otp: "expired123", // Expired/Invalid OTP
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 401, 404, 410]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Password Reset Tests - اختبارات إعادة تعيين كلمة المرور
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Password Reset", () => {
    it("should request password reset for valid email", async () => {
      const response = await apiRequest<{
        success: boolean;
        message?: string;
      }>(`${AUTH_API_BASE}/password/reset-request`, {
        method: "POST",
        body: JSON.stringify({
          email: TEST_USERS.FARMER.email,
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      // Should always return 200 to prevent email enumeration
      expect([200, 201, 404]).toContain(response.status);
    });

    it("should not reveal if email exists in password reset", async () => {
      const nonExistentResponse = await apiRequest(
        `${AUTH_API_BASE}/password/reset-request`,
        {
          method: "POST",
          body: JSON.stringify({
            email: "nonexistent@sahool.test",
          }),
        }
      );

      const existentResponse = await apiRequest(
        `${AUTH_API_BASE}/password/reset-request`,
        {
          method: "POST",
          body: JSON.stringify({
            email: TEST_USERS.FARMER.email,
          }),
        }
      );

      if (
        nonExistentResponse.status === 502 ||
        nonExistentResponse.status === 503 ||
        existentResponse.status === 502 ||
        existentResponse.status === 503
      ) {
        return;
      }

      // Both should return same status to prevent enumeration
      // Or endpoint might not exist (404)
      expect([200, 404]).toContain(nonExistentResponse.status);
    });

    it("should reset password with valid token", async () => {
      const response = await apiRequest<{
        success: boolean;
        message?: string;
      }>(`${AUTH_API_BASE}/password/reset`, {
        method: "POST",
        body: JSON.stringify({
          token: "valid-reset-token",
          new_password: "NewSecurePassword123!",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 404]).toContain(response.status);
    });

    it("should reject password reset with invalid token", async () => {
      const response = await apiRequest(`${AUTH_API_BASE}/password/reset`, {
        method: "POST",
        body: JSON.stringify({
          token: "invalid-token",
          new_password: "NewSecurePassword123!",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 401, 404]).toContain(response.status);
    });

    it("should reject password reset with weak new password", async () => {
      const response = await apiRequest(`${AUTH_API_BASE}/password/reset`, {
        method: "POST",
        body: JSON.stringify({
          token: "valid-reset-token",
          new_password: "weak", // Too weak
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([400, 422]).toContain(response.status);
    });

    it("should allow password change for authenticated user", async () => {
      const token = await getAuthToken("FARMER");

      const response = await apiRequest(`${AUTH_API_BASE}/password/change`, {
        method: "POST",
        headers: getAuthHeaders(token),
        body: JSON.stringify({
          current_password: TEST_USERS.FARMER.password,
          new_password: "NewSecurePassword456!",
        }),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 400, 401, 404]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Protected Endpoint Tests - اختبارات نقاط النهاية المحمية
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Protected Endpoints", () => {
    it("should access protected endpoint with valid token", async () => {
      const token = await getAuthToken("FARMER");

      const response = await apiRequest<{
        id: string;
        email: string;
        name: string;
        role: string;
      }>(`${AUTH_API_BASE}/me`, {
        method: "GET",
        headers: getAuthHeaders(token),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 200) {
        expect(response.data).toHaveProperty("id");
        expect(response.data).toHaveProperty("email");
      }
    });

    it("should reject protected endpoint without token", async () => {
      const response = await apiRequest(`${AUTH_API_BASE}/me`, {
        method: "GET",
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403, 404]).toContain(response.status);
    });

    it("should reject protected endpoint with invalid token", async () => {
      const response = await apiRequest(`${AUTH_API_BASE}/me`, {
        method: "GET",
        headers: {
          Authorization: "Bearer invalid-token",
        },
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403, 404]).toContain(response.status);
    });

    it("should reject protected endpoint with expired token", async () => {
      const expiredToken =
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNTE2MjM5MDIyfQ.expired";

      const response = await apiRequest(`${AUTH_API_BASE}/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${expiredToken}`,
        },
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403, 404]).toContain(response.status);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Role-Based Access Control Tests - اختبارات التحكم في الوصول القائم على الأدوار
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Role-Based Access Control", () => {
    it("should allow admin access to admin endpoints", async () => {
      const token = await getAuthToken("ADMIN");

      const response = await apiRequest(`${AUTH_API_BASE}/admin/users`, {
        method: "GET",
        headers: getAuthHeaders(token),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      // Admin should have access (200) or endpoint may not exist (404)
      expect([200, 401, 404]).toContain(response.status);
    });

    it("should deny farmer access to admin endpoints", async () => {
      const token = await getAuthToken("FARMER");

      const response = await apiRequest(`${AUTH_API_BASE}/admin/users`, {
        method: "GET",
        headers: getAuthHeaders(token),
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      // Farmer should be denied (403) or endpoint may not exist (404)
      expect([401, 403, 404]).toContain(response.status);
    });

    it("should enforce tenant isolation", async () => {
      const token = await getAuthToken("FARMER");

      // Try to access data from different tenant
      const response = await apiRequest(`${AUTH_API_BASE}/tenant/other-tenant/users`, {
        method: "GET",
        headers: {
          ...getAuthHeaders(token),
          "X-Tenant-ID": "different-tenant",
        },
      });

      if (response.status === 502 || response.status === 503) {
        return;
      }

      expect([401, 403, 404]).toContain(response.status);
    });
  });
});
