/**
 * Unified Client Tests (Web)
 * اختبارات عميل API الموحد للويب
 *
 * Tests CSRF interceptor behavior, configuration, and exports.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
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

// Mock @sahool/api-client — capture interceptor registration
const mockInterceptorUse = vi.fn();
const mockAxiosInstance = {
  defaults: {
    withCredentials: true,
    headers: { "Accept-Language": "ar,en", "Content-Type": "application/json" },
    timeout: 15000,
  },
  interceptors: {
    request: { use: mockInterceptorUse },
    response: { use: vi.fn() },
  },
  request: vi.fn(),
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
};

vi.mock("@sahool/api-client", () => ({
  SahoolApiClient: vi.fn().mockImplementation(() => ({
    axiosInstance: mockAxiosInstance,
  })),
}));

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Unified Client (Web)", () => {
  // Import the module once — the CSRF interceptor is registered at module
  // scope so re-importing via vi.resetModules() is unnecessary and breaks
  // the vi.mock() factory on subsequent dynamic imports.
  let mod: typeof import("../unified-client");
  let csrfInterceptor: (config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig;

  beforeAll(async () => {
    mod = await import("../unified-client");
    // Capture the CSRF interceptor registered during module initialization
    csrfInterceptor = mockInterceptorUse.mock.calls[0][0];
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Module Exports", () => {
    it("exports sahoolClient", () => {
      expect(mod.sahoolClient).toBeDefined();
    });

    it("exports unifiedApiClient as the axios instance", () => {
      expect(mod.unifiedApiClient).toBeDefined();
      expect(mod.unifiedApiClient.interceptors).toBeDefined();
    });
  });

  describe("Configuration", () => {
    it("configures withCredentials: true for httpOnly cookie auth", () => {
      expect(mod.unifiedApiClient.defaults.withCredentials).toBe(true);
    });
  });

  describe("CSRF Interceptor", () => {
    it("registers a request interceptor", () => {
      // Interceptor was registered during module initialization (beforeAll)
      expect(csrfInterceptor).toBeTypeOf("function");
    });

    it("injects X-CSRF-Token header on POST requests when cookie exists", () => {

      // Simulate _csrf cookie being available
      mockCookiesGet.mockReturnValue("csrf-token-abc123");

      // Create a mock config for a POST request
      const mockHeaders = {
        set: vi.fn(),
      };
      const config = {
        method: "post",
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      const result = csrfInterceptor(config);

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

      csrfInterceptor(config);

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

      csrfInterceptor(config);

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

      csrfInterceptor(config);

      expect(mockHeaders.set).not.toHaveBeenCalled();
    });

    it("does NOT inject header when _csrf cookie is missing", () => {
      mockCookiesGet.mockReturnValue(undefined);

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: "post",
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      csrfInterceptor(config);

      expect(mockCookiesGet).toHaveBeenCalledWith("_csrf");
      expect(mockHeaders.set).not.toHaveBeenCalled();
    });
  });
});
