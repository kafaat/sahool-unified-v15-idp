/**
 * Unified Client Tests (Web)
 * اختبارات عميل API الموحد للويب
 *
 * Tests CSRF interceptor behavior, configuration, and exports.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import type { InternalAxiosRequestConfig } from "axios";

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

const mockCookiesGet = vi.fn();
vi.mock("js-cookie", () => ({
  default: {
    get: (...args: unknown[]) => mockCookiesGet(...args),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

// Track interceptor registration - store the callback in a mutable ref
const interceptorRef: { fn: ((config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig) | null } = { fn: null };

vi.mock("@sahool/api-client", () => ({
  SahoolApiClient: vi.fn().mockImplementation(() => ({
    axiosInstance: {
      defaults: {
        withCredentials: true,
        headers: { "Accept-Language": "ar,en", "Content-Type": "application/json" },
        timeout: 15000,
      },
      interceptors: {
        request: {
          use: (fn: (config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig) => {
            interceptorRef.fn = fn;
          },
        },
        response: { use: vi.fn() },
      },
      request: vi.fn(),
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    },
  })),
}));

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Unified Client (Web)", () => {
  beforeEach(() => {
    mockCookiesGet.mockReset();
  });

  describe("Module Exports", () => {
    it("exports sahoolClient", async () => {
      const mod = await import("../unified-client");
      expect(mod.sahoolClient).toBeDefined();
    });

    it("exports unifiedApiClient as the axios instance", async () => {
      const mod = await import("../unified-client");
      expect(mod.unifiedApiClient).toBeDefined();
      expect(mod.unifiedApiClient.interceptors).toBeDefined();
    });
  });

  describe("Configuration", () => {
    it("configures withCredentials: true for httpOnly cookie auth", async () => {
      const mod = await import("../unified-client");
      expect(mod.unifiedApiClient.defaults.withCredentials).toBe(true);
    });
  });

  describe("CSRF Interceptor", () => {
    beforeEach(async () => {
      // Ensure the module has been loaded (cached after first call)
      await import("../unified-client");
    });

    it("registers a request interceptor", () => {
      expect(interceptorRef.fn).toBeTypeOf("function");
    });

    it("injects X-CSRF-Token header on POST requests when cookie exists", () => {
      mockCookiesGet.mockReturnValue("csrf-token-abc123");

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: "post",
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      const result = interceptorRef.fn!(config);

      expect(mockCookiesGet).toHaveBeenCalledWith("_csrf");
      expect(mockHeaders.set).toHaveBeenCalledWith(
        "X-CSRF-Token",
        "csrf-token-abc123",
      );
      expect(result).toBe(config);
    });

    it("injects X-CSRF-Token header on PUT requests", () => {
      mockCookiesGet.mockReturnValue("csrf-token-xyz");

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: "put",
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorRef.fn!(config);

      expect(mockHeaders.set).toHaveBeenCalledWith(
        "X-CSRF-Token",
        "csrf-token-xyz",
      );
    });

    it("injects X-CSRF-Token header on DELETE requests", () => {
      mockCookiesGet.mockReturnValue("csrf-del-token");

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: "delete",
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorRef.fn!(config);

      expect(mockHeaders.set).toHaveBeenCalledWith(
        "X-CSRF-Token",
        "csrf-del-token",
      );
    });

    it("does NOT inject X-CSRF-Token on GET requests", () => {
      mockCookiesGet.mockReturnValue("csrf-token-abc123");

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: "get",
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorRef.fn!(config);

      expect(mockHeaders.set).not.toHaveBeenCalled();
    });

    it("does NOT inject header when _csrf cookie is missing", () => {
      mockCookiesGet.mockReturnValue(undefined);

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: "post",
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorRef.fn!(config);

      expect(mockCookiesGet).toHaveBeenCalledWith("_csrf");
      expect(mockHeaders.set).not.toHaveBeenCalled();
    });
  });
});
