/**
 * Unified Client Tests (Web)
 * اختبارات عميل API الموحد للويب
 *
 * Tests CSRF interceptor behavior, configuration, and exports.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import type { InternalAxiosRequestConfig } from 'axios';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

const mockCookiesGet = vi.fn();
vi.mock('js-cookie', () => ({
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
    headers: { 'Accept-Language': 'ar,en', 'Content-Type': 'application/json' },
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

vi.mock('@sahool/api-client', () => ({
  SahoolApiClient: vi.fn().mockImplementation(() => ({
    axiosInstance: mockAxiosInstance,
  })),
}));

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Unified Client (Web)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset module registry so each test re-executes the module code,
    // including the CSRF interceptor registration.
    vi.resetModules();
  });

  afterEach(() => {
    // Use clearAllMocks instead of restoreAllMocks: restoreAllMocks calls
    // mockRestore() on every vi.fn(), which strips mockImplementation from
    // the SahoolApiClient factory mock.  On the next vi.resetModules() +
    // dynamic import the cleared constructor returns an empty object (no
    // axiosInstance), causing the module-level CSRF interceptor setup to throw.
    vi.clearAllMocks();
  });

  describe('Module Exports', () => {
    it('exports sahoolClient', async () => {
      const mod = await import('../unified-client');
      expect(mod.sahoolClient).toBeDefined();
    });

    it('exports unifiedApiClient as the axios instance', async () => {
      const mod = await import('../unified-client');
      expect(mod.unifiedApiClient).toBeDefined();
      expect(mod.unifiedApiClient.interceptors).toBeDefined();
    });
  });

  describe('Configuration', () => {
    it('configures withCredentials: true for httpOnly cookie auth', async () => {
      const mod = await import('../unified-client');
      expect(mod.unifiedApiClient.defaults.withCredentials).toBe(true);
    });
  });

  describe('CSRF Interceptor', () => {
    it('registers a request interceptor', async () => {
      // Import triggers interceptor registration
      await import('../unified-client');
      expect(mockInterceptorUse).toHaveBeenCalled();
    });

    it('injects X-CSRF-Token header on POST requests when cookie exists', async () => {
      await import('../unified-client');

      // Get the interceptor function that was registered
      const interceptorFn = mockInterceptorUse.mock.calls[0][0];
      expect(interceptorFn).toBeTypeOf('function');

      // Simulate _csrf cookie being available
      mockCookiesGet.mockReturnValue('csrf-token-abc123');

      // Create a mock config for a POST request
      const mockHeaders = {
        set: vi.fn(),
      };
      const config = {
        method: 'post',
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      const result = interceptorFn(config);

      expect(mockCookiesGet).toHaveBeenCalledWith('_csrf');
      expect(mockHeaders.set).toHaveBeenCalledWith('X-CSRF-Token', 'csrf-token-abc123');
      expect(result).toBe(config);
    });

    it('injects X-CSRF-Token header on PUT requests', async () => {
      await import('../unified-client');
      const interceptorFn = mockInterceptorUse.mock.calls[0][0];

      mockCookiesGet.mockReturnValue('csrf-token-xyz');

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: 'put',
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorFn(config);

      expect(mockHeaders.set).toHaveBeenCalledWith('X-CSRF-Token', 'csrf-token-xyz');
    });

    it('injects X-CSRF-Token header on DELETE requests', async () => {
      await import('../unified-client');
      const interceptorFn = mockInterceptorUse.mock.calls[0][0];

      mockCookiesGet.mockReturnValue('csrf-del-token');

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: 'delete',
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorFn(config);

      expect(mockHeaders.set).toHaveBeenCalledWith('X-CSRF-Token', 'csrf-del-token');
    });

    it('does NOT inject X-CSRF-Token on GET requests', async () => {
      await import('../unified-client');
      const interceptorFn = mockInterceptorUse.mock.calls[0][0];

      mockCookiesGet.mockReturnValue('csrf-token-abc123');

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: 'get',
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorFn(config);

      expect(mockHeaders.set).not.toHaveBeenCalled();
    });

    it('does NOT inject header when _csrf cookie is missing', async () => {
      await import('../unified-client');
      const interceptorFn = mockInterceptorUse.mock.calls[0][0];

      mockCookiesGet.mockReturnValue(undefined);

      const mockHeaders = { set: vi.fn() };
      const config = {
        method: 'post',
        headers: mockHeaders,
      } as unknown as InternalAxiosRequestConfig;

      interceptorFn(config);

      expect(mockCookiesGet).toHaveBeenCalledWith('_csrf');
      expect(mockHeaders.set).not.toHaveBeenCalled();
    });
  });
});
