/**
 * Auth Store Tests
 * اختبارات مخزن المصادقة
 *
 * Tests for auth store helper functions (non-component logic)
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import _Cookies from "js-cookie";

// Mock modules
vi.mock("js-cookie", () => ({
  default: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

vi.mock("@/lib/logger", () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}));

vi.mock("@/lib/api/auth-client", () => ({
  authApiClient: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn(),
    attemptTokenRefresh: vi.fn(),
    setToken: vi.fn(),
    clearToken: vi.fn(),
  },
}));

describe("Auth Store helpers", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.clearAllMocks();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // isE2ETestModeEnabled
  // ═══════════════════════════════════════════════════════════════════════════

  describe("isE2ETestModeEnabled", () => {
    it("should return false in production", async () => {
      process.env.NODE_ENV = "production";
      process.env.NEXT_PUBLIC_E2E_TEST = "true";
      // Re-import to pick up env changes
      vi.resetModules();
      const { isE2ETestModeEnabled } = await import("../../stores/auth.store");
      expect(isE2ETestModeEnabled()).toBe(false);
    });

    it("should return false in test environment", async () => {
      process.env.NODE_ENV = "test";
      process.env.NEXT_PUBLIC_E2E_TEST = "true";
      vi.resetModules();
      const { isE2ETestModeEnabled } = await import("../../stores/auth.store");
      expect(isE2ETestModeEnabled()).toBe(false);
    });

    it("should return false in development without E2E flag", async () => {
      process.env.NODE_ENV = "development";
      delete process.env.NEXT_PUBLIC_E2E_TEST;
      vi.resetModules();
      const { isE2ETestModeEnabled } = await import("../../stores/auth.store");
      expect(isE2ETestModeEnabled()).toBe(false);
    });

    it("should return false in development with E2E flag set to false", async () => {
      process.env.NODE_ENV = "development";
      process.env.NEXT_PUBLIC_E2E_TEST = "false";
      vi.resetModules();
      const { isE2ETestModeEnabled } = await import("../../stores/auth.store");
      expect(isE2ETestModeEnabled()).toBe(false);
    });

    it("should return true only in development with E2E flag set to true", async () => {
      process.env.NODE_ENV = "development";
      process.env.NEXT_PUBLIC_E2E_TEST = "true";
      vi.resetModules();
      const { isE2ETestModeEnabled } = await import("../../stores/auth.store");
      expect(isE2ETestModeEnabled()).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // tryLoadMockSession
  // ═══════════════════════════════════════════════════════════════════════════

  describe("tryLoadMockSession", () => {
    it("should return null when E2E mode is disabled", async () => {
      process.env.NODE_ENV = "production";
      vi.resetModules();
      const { tryLoadMockSession } = await import("../../stores/auth.store");
      expect(tryLoadMockSession()).toBeNull();
    });

    it("should return null when no mock session cookie", async () => {
      process.env.NODE_ENV = "development";
      process.env.NEXT_PUBLIC_E2E_TEST = "true";
      vi.resetModules();
      const cookiesMod = await import("js-cookie");
      vi.mocked(cookiesMod.default.get).mockReturnValue(undefined);
      const { tryLoadMockSession } = await import("../../stores/auth.store");
      expect(tryLoadMockSession()).toBeNull();
    });

    it("should return null for invalid JSON", async () => {
      process.env.NODE_ENV = "development";
      process.env.NEXT_PUBLIC_E2E_TEST = "true";
      vi.resetModules();
      const cookiesMod = await import("js-cookie");
      vi.mocked(cookiesMod.default.get).mockReturnValue("not-json");
      const { tryLoadMockSession } = await import("../../stores/auth.store");
      expect(tryLoadMockSession()).toBeNull();
    });

    it("should parse valid mock session", async () => {
      process.env.NODE_ENV = "development";
      process.env.NEXT_PUBLIC_E2E_TEST = "true";
      vi.resetModules();
      const cookiesMod = await import("js-cookie");
      vi.mocked(cookiesMod.default.get).mockReturnValue(
        JSON.stringify({
          id: "mock-1",
          email: "test@test.com",
          name: "Tester",
          nameAr: "مختبر",
          role: "admin",
        }),
      );
      const { tryLoadMockSession } = await import("../../stores/auth.store");
      const result = tryLoadMockSession();

      expect(result).toEqual({
        id: "mock-1",
        email: "test@test.com",
        name: "Tester",
        name_ar: "مختبر",
        role: "admin",
      });
    });

    it("should use defaults for missing fields", async () => {
      process.env.NODE_ENV = "development";
      process.env.NEXT_PUBLIC_E2E_TEST = "true";
      vi.resetModules();
      const cookiesMod = await import("js-cookie");
      vi.mocked(cookiesMod.default.get).mockReturnValue("{}");
      const { tryLoadMockSession } = await import("../../stores/auth.store");
      const result = tryLoadMockSession();

      expect(result).toEqual({
        id: "test-user",
        email: "test@sahool.com",
        name: "Test User",
        name_ar: "مستخدم اختباري",
        role: "user",
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // fetchCsrfToken
  // ═══════════════════════════════════════════════════════════════════════════

  describe("fetchCsrfToken", () => {
    it("should return true on successful fetch", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({}),
      });

      const { fetchCsrfToken } = await import("../../stores/auth.store");
      const result = await fetchCsrfToken();
      expect(result).toBe(true);
    });

    it("should return false on failed fetch", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      });

      const { fetchCsrfToken } = await import("../../stores/auth.store");
      const result = await fetchCsrfToken();
      expect(result).toBe(false);
    });

    it("should return false on network error", async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

      const { fetchCsrfToken } = await import("../../stores/auth.store");
      const result = await fetchCsrfToken();
      expect(result).toBe(false);
    });
  });
});

// useAuth hook contract test moved to use-auth-contract.test.ts
// to avoid vi.resetModules() contamination breaking renderHook's React.act
