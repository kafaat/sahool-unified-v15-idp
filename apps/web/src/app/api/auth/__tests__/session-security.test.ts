/**
 * Session Route Security Tests
 * اختبارات أمان مسار الجلسة
 *
 * Tests for security fixes:
 * - ACCESS_TOKEN_MAX_AGE defaults to 1800 (30 min) not 604800 (7 days)
 * - Environment variable override for JWT_ACCESS_TOKEN_EXPIRE_SECONDS
 * - REFRESH_TOKEN_MAX_AGE defaults to 604800 (7 days) not 2592000 (30 days)
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════
// Module Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock("next/headers", () => {
  const mockCookieStore = {
    get: vi.fn(),
    set: vi.fn(),
    delete: vi.fn(),
  };
  return {
    cookies: vi.fn(() => Promise.resolve(mockCookieStore)),
  };
});

vi.mock("@/lib/rate-limiter", () => ({
  isRateLimited: vi.fn(() => Promise.resolve(false)),
}));

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

function createNextRequest(
  method: string,
  body?: Record<string, unknown>,
): Request {
  const url = "http://localhost:3000/api/auth/session";
  const init: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      "x-forwarded-for": "127.0.0.1",
    },
  };
  if (body) {
    init.body = JSON.stringify(body);
  }
  return new Request(url, init);
}

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Session Route Security - Token MaxAge", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ACCESS_TOKEN_MAX_AGE defaults
  // ═══════════════════════════════════════════════════════════════════════════

  describe("ACCESS_TOKEN_MAX_AGE", () => {
    it("should default to 1800 (30 minutes) not 604800 (7 days)", async () => {
      // Ensure env var is not set so the default is used
      process.env = { ...originalEnv };
      delete process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS;

      // Re-mock after resetModules
      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      // Find the access_token cookie set call
      const accessTokenCall = setCalls.find(
        (call) => call[0] === "access_token",
      );

      expect(accessTokenCall).toBeDefined();
      // The third argument is the cookie options
      const options = accessTokenCall![2] as Record<string, unknown>;
      expect(options.maxAge).toBe(1800); // 30 minutes, NOT 604800 (7 days)
    });

    it("should NOT be 604800 (the old insecure 7-day value)", async () => {
      process.env = { ...originalEnv };
      delete process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS;

      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      const accessTokenCall = setCalls.find(
        (call) => call[0] === "access_token",
      );

      expect(accessTokenCall).toBeDefined();
      const options = accessTokenCall![2] as Record<string, unknown>;
      // Explicitly verify the old insecure value is not used
      expect(options.maxAge).not.toBe(604800);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Environment variable override
  // ═══════════════════════════════════════════════════════════════════════════

  describe("JWT_ACCESS_TOKEN_EXPIRE_SECONDS env override", () => {
    it("should use env var value when JWT_ACCESS_TOKEN_EXPIRE_SECONDS is set", async () => {
      process.env = {
        ...originalEnv,
        JWT_ACCESS_TOKEN_EXPIRE_SECONDS: "3600", // 1 hour
      };

      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      const accessTokenCall = setCalls.find(
        (call) => call[0] === "access_token",
      );

      expect(accessTokenCall).toBeDefined();
      const options = accessTokenCall![2] as Record<string, unknown>;
      expect(options.maxAge).toBe(3600);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // REFRESH_TOKEN_MAX_AGE defaults
  // ═══════════════════════════════════════════════════════════════════════════

  describe("REFRESH_TOKEN_MAX_AGE", () => {
    it("should default to 604800 (7 days) not 2592000 (30 days)", async () => {
      process.env = { ...originalEnv };
      delete process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS;

      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
        refresh_token: "eyJhbGciOiJIUzI1NiJ9.valid-refresh-token-for-session-test",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      // Find the refresh_token cookie set call
      const refreshTokenCall = setCalls.find(
        (call) => call[0] === "refresh_token",
      );

      expect(refreshTokenCall).toBeDefined();
      const options = refreshTokenCall![2] as Record<string, unknown>;
      expect(options.maxAge).toBe(604800); // 7 days, NOT 2592000 (30 days)
    });

    it("should NOT be 2592000 (the old insecure 30-day value)", async () => {
      process.env = { ...originalEnv };
      delete process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS;

      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
        refresh_token: "eyJhbGciOiJIUzI1NiJ9.valid-refresh-token-for-session-test",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      const refreshTokenCall = setCalls.find(
        (call) => call[0] === "refresh_token",
      );

      expect(refreshTokenCall).toBeDefined();
      const options = refreshTokenCall![2] as Record<string, unknown>;
      // Explicitly verify the old insecure value is not used
      expect(options.maxAge).not.toBe(2592000);
    });

    it("should use env var value when JWT_REFRESH_TOKEN_EXPIRE_SECONDS is set", async () => {
      process.env = {
        ...originalEnv,
        JWT_REFRESH_TOKEN_EXPIRE_SECONDS: "1209600", // 14 days
      };

      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
        refresh_token: "eyJhbGciOiJIUzI1NiJ9.valid-refresh-token-for-session-test",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      const refreshTokenCall = setCalls.find(
        (call) => call[0] === "refresh_token",
      );

      expect(refreshTokenCall).toBeDefined();
      const options = refreshTokenCall![2] as Record<string, unknown>;
      expect(options.maxAge).toBe(1209600);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Cookie security flags
  // ═══════════════════════════════════════════════════════════════════════════

  describe("Cookie security flags", () => {
    it("should set httpOnly: true on access_token cookie", async () => {
      process.env = { ...originalEnv };

      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      const accessTokenCall = setCalls.find(
        (call) => call[0] === "access_token",
      );

      expect(accessTokenCall).toBeDefined();
      const options = accessTokenCall![2] as Record<string, unknown>;
      expect(options.httpOnly).toBe(true);
      expect(options.sameSite).toBe("strict");
    });

    it("should set httpOnly: true on refresh_token cookie", async () => {
      process.env = { ...originalEnv };

      vi.doMock("next/headers", () => {
        const store = { get: vi.fn(), set: vi.fn(), delete: vi.fn() };
        return { cookies: vi.fn(() => Promise.resolve(store)) };
      });
      vi.doMock("@/lib/rate-limiter", () => ({
        isRateLimited: vi.fn(() => Promise.resolve(false)),
      }));

      const { POST } = await import("../session/route");
      const { cookies } = await import("next/headers");

      const request = createNextRequest("POST", {
        access_token: "eyJhbGciOiJIUzI1NiJ9.valid-test-token-for-session-testing",
        refresh_token: "eyJhbGciOiJIUzI1NiJ9.valid-refresh-token-for-session-test",
      });

      await POST(request as never);

      const cookieStore = await cookies();
      const setCalls = vi.mocked(cookieStore.set).mock.calls;

      const refreshTokenCall = setCalls.find(
        (call) => call[0] === "refresh_token",
      );

      expect(refreshTokenCall).toBeDefined();
      const options = refreshTokenCall![2] as Record<string, unknown>;
      expect(options.httpOnly).toBe(true);
      expect(options.sameSite).toBe("strict");
    });
  });
});
