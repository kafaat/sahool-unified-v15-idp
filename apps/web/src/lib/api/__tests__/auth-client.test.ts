/**
 * AuthApiClient Tests
 * اختبارات عميل API المصادقة
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Mock js-cookie before importing the module
vi.mock("js-cookie", () => ({
  default: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

// Mock logger
vi.mock("../../logger", () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}));

import Cookies from "js-cookie";

// We need to test the class directly, so we'll import and re-create
// Since authApiClient is a singleton, we test via the exported instance
describe("AuthApiClient", () => {
  let originalFetch: typeof global.fetch;

  beforeEach(() => {
    originalFetch = global.fetch;
    vi.clearAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // LOGIN
  // ═══════════════════════════════════════════════════════════════════════════

  describe("login", () => {
    it("should reject invalid email format", async () => {
      // Dynamically import to get fresh instance after mocks
      const { authApiClient } = await import("../auth-client");

      const result = await authApiClient.login("not-an-email", "password123");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Invalid email format");
    });

    it("should reject empty email", async () => {
      const { authApiClient } = await import("../auth-client");

      const result = await authApiClient.login("", "password123");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Invalid email format");
    });

    it("should reject whitespace-only email", async () => {
      const { authApiClient } = await import("../auth-client");

      const result = await authApiClient.login("   ", "password123");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Invalid email format");
    });

    it("should trim and lowercase email before sending", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () =>
          Promise.resolve({
            success: true,
            data: {
              access_token: "token123",
              user: { id: "1", email: "test@sahool.com", name: "Test", role: "farmer" },
            },
          }),
      });

      await authApiClient.login("  Test@Sahool.COM  ", "password123");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/login"),
        expect.objectContaining({
          method: "POST",
          body: expect.stringContaining('"email":"test@sahool.com"'),
        }),
      );
    });

    it("should return success with user data on valid login", async () => {
      const { authApiClient } = await import("../auth-client");

      const mockResponse = {
        success: true,
        data: {
          access_token: "jwt-token",
          refresh_token: "refresh-token",
          user: {
            id: "user-1",
            email: "farmer@sahool.com",
            name: "Ahmed",
            role: "farmer",
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve(mockResponse),
      });

      const result = await authApiClient.login("farmer@sahool.com", "SecurePass123");

      expect(result.success).toBe(true);
      expect(result.data?.access_token).toBe("jwt-token");
      expect(result.data?.user.email).toBe("farmer@sahool.com");
    });

    it("should return error on server failure", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({ error: "Invalid credentials" }),
      });

      const result = await authApiClient.login("user@sahool.com", "wrong-pass");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Invalid credentials");
    });

    it("should handle network errors", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockRejectedValue(new Error("Network failure"));

      const result = await authApiClient.login("user@sahool.com", "password");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Network failure");
    });

    it("should handle timeout (AbortError)", async () => {
      const { authApiClient } = await import("../auth-client");

      // DOMException with AbortError name may not be available in jsdom
      const abortError = new Error("Aborted");
      abortError.name = "AbortError";
      global.fetch = vi.fn().mockRejectedValue(abortError);

      const result = await authApiClient.login("user@sahool.com", "password");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Request timeout");
    });

    it("should handle non-JSON responses", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "text/plain" }),
        text: () => Promise.resolve("OK"),
      });

      const result = await authApiClient.login("user@sahool.com", "password");

      expect(result.success).toBe(true);
    });

    it("should handle invalid JSON response", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.reject(new Error("Invalid JSON")),
      });

      const result = await authApiClient.login("user@sahool.com", "password");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Invalid JSON response from server");
    });

    it("should handle error response with message field", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({ message: "Account locked" }),
      });

      const result = await authApiClient.login("user@sahool.com", "password");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Account locked");
    });

    it("should handle error response without message or error field", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({}),
      });

      const result = await authApiClient.login("user@sahool.com", "password");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Request failed with status 500");
    });

    it("should handle non-Error thrown objects", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockRejectedValue("string error");

      const result = await authApiClient.login("user@sahool.com", "password");

      expect(result.success).toBe(false);
      expect(result.error).toBe("Network error - please check your connection");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // TOKEN MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  describe("token management", () => {
    it("should include Authorization header when token is set", async () => {
      const { authApiClient } = await import("../auth-client");

      authApiClient.setToken("my-token");

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({ success: true, data: {} }),
      });

      await authApiClient.getCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer my-token",
          }),
        }),
      );

      authApiClient.clearToken();
    });

    it("should not include Authorization header when no token", async () => {
      const { authApiClient } = await import("../auth-client");

      authApiClient.clearToken();

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({ success: true, data: {} }),
      });

      await authApiClient.getCurrentUser();

      const fetchCall = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const headers = fetchCall[1]?.headers as Record<string, string>;
      expect(headers.Authorization).toBeUndefined();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GET CURRENT USER
  // ═══════════════════════════════════════════════════════════════════════════

  describe("getCurrentUser", () => {
    it("should make GET request to /api/v1/auth/me", async () => {
      const { authApiClient } = await import("../auth-client");

      const mockUser = {
        id: "user-1",
        email: "user@sahool.com",
        name: "Test User",
        role: "farmer",
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({ success: true, data: mockUser }),
      });

      const result = await authApiClient.getCurrentUser();

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockUser);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // REFRESH TOKEN
  // ═══════════════════════════════════════════════════════════════════════════

  describe("refreshToken", () => {
    it("should send refresh token to /api/v1/auth/refresh", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () =>
          Promise.resolve({
            success: true,
            data: { access_token: "new-token" },
          }),
      });

      const result = await authApiClient.refreshToken("my-refresh-token");

      expect(result.success).toBe(true);
      expect(result.data?.access_token).toBe("new-token");
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/auth/refresh"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ refresh_token: "my-refresh-token" }),
        }),
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ATTEMPT TOKEN REFRESH
  // ═══════════════════════════════════════════════════════════════════════════

  describe("attemptTokenRefresh", () => {
    it("should return false when no refresh token in cookies", async () => {
      const { authApiClient } = await import("../auth-client");

      vi.mocked(Cookies.get).mockReturnValue(undefined);

      const result = await authApiClient.attemptTokenRefresh();

      expect(result).toBe(false);
    });

    it("should refresh and set new token when refresh token exists", async () => {
      const { authApiClient } = await import("../auth-client");

      vi.mocked(Cookies.get).mockReturnValue("existing-refresh-token");

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () =>
          Promise.resolve({
            success: true,
            data: { access_token: "new-access-token" },
          }),
      });

      const result = await authApiClient.attemptTokenRefresh();

      expect(result).toBe(true);
      expect(Cookies.set).toHaveBeenCalledWith("access_token", "new-access-token", {
        expires: 7,
        secure: true,
        sameSite: "strict",
        path: "/",
      });
    });

    it("should clear tokens when refresh fails", async () => {
      const { authApiClient } = await import("../auth-client");

      vi.mocked(Cookies.get).mockReturnValue("expired-refresh-token");

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({ success: false, error: "Token expired" }),
      });

      const result = await authApiClient.attemptTokenRefresh();

      expect(result).toBe(false);
      expect(Cookies.remove).toHaveBeenCalledWith("access_token");
      expect(Cookies.remove).toHaveBeenCalledWith("refresh_token");
    });

    it("should handle errors during refresh gracefully", async () => {
      const { authApiClient } = await import("../auth-client");

      vi.mocked(Cookies.get).mockReturnValue("token");

      global.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

      const result = await authApiClient.attemptTokenRefresh();

      expect(result).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // REQUEST CREDENTIALS
  // ═══════════════════════════════════════════════════════════════════════════

  describe("request credentials", () => {
    it("should include credentials: include in all requests", async () => {
      const { authApiClient } = await import("../auth-client");

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve({ success: true, data: {} }),
      });

      await authApiClient.getCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: "include",
        }),
      );
    });
  });
});
