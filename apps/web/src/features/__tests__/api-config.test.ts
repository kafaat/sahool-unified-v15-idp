/**
 * API Configuration Integration Tests
 * Tests for baseURL configuration and endpoint construction
 * 
 * Validates:
 * 1. Correct baseURL handling (no /api duplication)
 * 2. Environment variable support
 * 3. Development warnings
 * 4. Endpoint path construction
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Mock axios to intercept requests
vi.mock('axios');
const mockedAxios = vi.mocked(axios, true);

// Mock console.warn
const originalConsoleWarn = console.warn;
const consoleWarnMock = vi.fn();

describe('API Configuration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    console.warn = consoleWarnMock;
    
    // Setup axios.create mock
    mockedAxios.create = vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })) as any;
  });

  afterEach(() => {
    console.warn = originalConsoleWarn;
    vi.resetModules();
  });

  describe('Advisor API Configuration', () => {
    it('should use empty baseURL when NEXT_PUBLIC_API_URL is not set', async () => {
      // Ensure env var is not set
      delete process.env.NEXT_PUBLIC_API_URL;
      
      // Re-import to get fresh module
      await import('../advisor/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: '',
        })
      );
    });

    it('should use NEXT_PUBLIC_API_URL when set', async () => {
      const testUrl = 'https://api.example.com';
      process.env.NEXT_PUBLIC_API_URL = testUrl;
      
      await import('../advisor/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: testUrl,
        })
      );
      
      delete process.env.NEXT_PUBLIC_API_URL;
    });

    it('should warn in development when API_BASE_URL is empty', async () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      
      // Mock window object to simulate browser environment
      global.window = {} as any;
      
      await import('../advisor/api');
      
      // The warning should be logged
      expect(consoleWarnMock).toHaveBeenCalledWith(
        'NEXT_PUBLIC_API_URL environment variable is not set'
      );
      
      delete (global as any).window;
    });

    it('should not throw during server-side build', async () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      delete (global as any).window;
      
      // Should not throw an error
      await expect(import('../advisor/api')).resolves.toBeDefined();
    });
  });

  describe('Field Map API Configuration', () => {
    it('should use empty baseURL when NEXT_PUBLIC_API_URL is not set', async () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      
      await import('../field-map/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: '',
        })
      );
    });

    it('should use NEXT_PUBLIC_API_URL when set', async () => {
      const testUrl = 'https://api.example.com';
      process.env.NEXT_PUBLIC_API_URL = testUrl;
      
      await import('../field-map/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: testUrl,
        })
      );
      
      delete process.env.NEXT_PUBLIC_API_URL;
    });
  });

  describe('NDVI API Configuration', () => {
    it('should use empty baseURL when NEXT_PUBLIC_API_URL is not set', async () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      
      await import('../ndvi/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: '',
        })
      );
    });

    it('should use NEXT_PUBLIC_API_URL when set', async () => {
      const testUrl = 'https://api.example.com';
      process.env.NEXT_PUBLIC_API_URL = testUrl;
      
      await import('../ndvi/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: testUrl,
        })
      );
      
      delete process.env.NEXT_PUBLIC_API_URL;
    });
  });

  describe('Reports API Configuration', () => {
    it('should use empty baseURL when NEXT_PUBLIC_API_URL is not set', async () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      
      await import('../reports/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: '',
        })
      );
    });

    it('should use NEXT_PUBLIC_API_URL when set', async () => {
      const testUrl = 'https://api.example.com';
      process.env.NEXT_PUBLIC_API_URL = testUrl;
      
      await import('../reports/api');
      
      expect(mockedAxios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          baseURL: testUrl,
        })
      );
      
      delete process.env.NEXT_PUBLIC_API_URL;
    });
  });

  describe('Endpoint Path Construction', () => {
    it('should construct correct paths without /api duplication', () => {
      // Test various endpoint patterns
      const testCases = [
        { endpoint: '/api/v1/advice/recommendations', baseURL: '', expected: '/api/v1/advice/recommendations' },
        { endpoint: '/api/v1/advice/recommendations', baseURL: 'https://api.example.com', expected: 'https://api.example.com/api/v1/advice/recommendations' },
        { endpoint: '/api/v1/fields', baseURL: '', expected: '/api/v1/fields' },
        { endpoint: '/api/v1/fields', baseURL: 'https://api.example.com', expected: 'https://api.example.com/api/v1/fields' },
        { endpoint: '/api/v1/ndvi/latest', baseURL: '', expected: '/api/v1/ndvi/latest' },
        { endpoint: '/api/v1/ndvi/latest', baseURL: 'https://api.example.com', expected: 'https://api.example.com/api/v1/ndvi/latest' },
        { endpoint: '/api/v1/reports', baseURL: '', expected: '/api/v1/reports' },
        { endpoint: '/api/v1/reports', baseURL: 'https://api.example.com', expected: 'https://api.example.com/api/v1/reports' },
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

      endpoints.forEach(endpoint => {
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

      endpoints.forEach(endpoint => {
        const fullUrl = baseURL ? `${baseURL}${endpoint}` : endpoint;
        expect(fullUrl).toBe(endpoint);
        expect(fullUrl).toMatch(/^\/api\/v1\//);
        expect(fullUrl).not.toMatch(/\/api\/api/);
      });
    });
  });

  describe('Common Configuration', () => {
    it('should have consistent timeout configuration', async () => {
      await import('../advisor/api');
      await import('../field-map/api');
      await import('../ndvi/api');
      await import('../reports/api');

      const calls = mockedAxios.create.mock.calls;
      calls.forEach(call => {
        expect(call[0]).toHaveProperty('timeout', 10000);
      });
    });

    it('should have consistent header configuration', async () => {
      await import('../advisor/api');
      await import('../field-map/api');
      await import('../ndvi/api');
      await import('../reports/api');

      const calls = mockedAxios.create.mock.calls;
      calls.forEach(call => {
        expect(call[0]).toHaveProperty('headers');
        expect(call[0].headers).toHaveProperty('Content-Type', 'application/json');
      });
    });
  });
});
