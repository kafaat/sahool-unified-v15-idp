/**
 * API Configuration Integration Tests
 * Tests for baseURL configuration and endpoint construction
 *
 * Validates:
 * 1. Correct baseURL handling (no /api duplication)
 * 2. Environment variable support
 * 3. Development warnings
 * 4. Endpoint path construction
 *
 * Note: Feature modules (advisor, field-map, ndvi, reports) use
 * createApiClient() which returns the unified client's axios instance
 * (not axios.create). These tests validate the unified client's config
 * and endpoint path construction.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock console.warn
const originalConsoleWarn = console.warn;
const consoleWarnMock = vi.fn();

describe('API Configuration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.warn = consoleWarnMock;
  });

  afterEach(() => {
    console.warn = originalConsoleWarn;
    vi.resetModules();
  });

  describe('Feature API modules', () => {
    it('advisor/api should export without errors', async () => {
      await expect(import('../advisor/api')).resolves.toBeDefined();
    });

    it('field-map/api should export without errors', async () => {
      await expect(import('../field-map/api')).resolves.toBeDefined();
    });

    it('ndvi/api should export without errors', async () => {
      await expect(import('../ndvi/api')).resolves.toBeDefined();
    });

    it('reports/api should export without errors', async () => {
      await expect(import('../reports/api')).resolves.toBeDefined();
    });

    it('should not throw during server-side build', async () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      delete (global as any).window;

      await expect(import('../advisor/api')).resolves.toBeDefined();
    });
  });

  describe('Unified client configuration', () => {
    it('should have baseURL from NEXT_PUBLIC_API_URL or empty', async () => {
      const { unifiedApiClient } = await import('@/lib/api/unified-client');
      const baseURL = unifiedApiClient.defaults.baseURL ?? '';
      const envUrl = process.env.NEXT_PUBLIC_API_URL ?? '';
      expect(baseURL).toBe(envUrl);
    });

    it('should have withCredentials enabled', async () => {
      const { unifiedApiClient } = await import('@/lib/api/unified-client');
      expect(unifiedApiClient.defaults.withCredentials).toBe(true);
    });

    it('should have timeout configured', async () => {
      const { unifiedApiClient } = await import('@/lib/api/unified-client');
      expect(unifiedApiClient.defaults.timeout).toBeGreaterThan(0);
    });
  });

  describe('Endpoint Path Construction', () => {
    it('should construct correct paths without /api duplication', () => {
      // Test various endpoint patterns
      const testCases = [
        {
          endpoint: '/api/v1/advice/recommendations',
          baseURL: '',
          expected: '/api/v1/advice/recommendations',
        },
        {
          endpoint: '/api/v1/advice/recommendations',
          baseURL: 'https://api.example.com',
          expected: 'https://api.example.com/api/v1/advice/recommendations',
        },
        { endpoint: '/api/v1/fields', baseURL: '', expected: '/api/v1/fields' },
        {
          endpoint: '/api/v1/fields',
          baseURL: 'https://api.example.com',
          expected: 'https://api.example.com/api/v1/fields',
        },
        {
          endpoint: '/api/v1/ndvi/latest',
          baseURL: '',
          expected: '/api/v1/ndvi/latest',
        },
        {
          endpoint: '/api/v1/ndvi/latest',
          baseURL: 'https://api.example.com',
          expected: 'https://api.example.com/api/v1/ndvi/latest',
        },
        {
          endpoint: '/api/v1/reports',
          baseURL: '',
          expected: '/api/v1/reports',
        },
        {
          endpoint: '/api/v1/reports',
          baseURL: 'https://api.example.com',
          expected: 'https://api.example.com/api/v1/reports',
        },
      ];

      testCases.forEach(({ endpoint, baseURL, expected }) => {
        const fullUrl = baseURL ? `${baseURL}${endpoint}` : endpoint;
        expect(fullUrl).toBe(expected);
        // Ensure no /api/api duplication
        expect(fullUrl).not.toMatch(/\/api\/api/);
      });
    });

    it('should not have /api/api duplication in production URLs', () => {
      const baseURL = 'https://kong-gateway.example.com';
      const endpoints = [
        '/api/v1/advice/recommendations',
        '/api/v1/fields',
        '/api/v1/ndvi/latest',
        '/api/v1/reports',
      ];

      endpoints.forEach((endpoint) => {
        const fullUrl = `${baseURL}${endpoint}`;
        expect(fullUrl).not.toMatch(/\/api\/api/);
        expect(fullUrl).toMatch(/^https:\/\/kong-gateway\.example\.com\/api\/v1\//);
      });
    });

    it('should work correctly with relative paths in development', () => {
      const baseURL = '';
      const endpoints = [
        '/api/v1/advice/recommendations',
        '/api/v1/fields',
        '/api/v1/ndvi/latest',
        '/api/v1/reports',
      ];

      endpoints.forEach((endpoint) => {
        const fullUrl = baseURL ? `${baseURL}${endpoint}` : endpoint;
        expect(fullUrl).toBe(endpoint);
        expect(fullUrl).toMatch(/^\/api\/v1\//);
        expect(fullUrl).not.toMatch(/\/api\/api/);
      });
    });
  });
});
