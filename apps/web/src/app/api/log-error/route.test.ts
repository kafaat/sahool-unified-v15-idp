/**
 * Log Error API Route Tests
 * اختبارات نقطة API لتسجيل الأخطاء
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { POST } from './route';
import { NextRequest } from 'next/server';

// Mock the rate limiter to always allow requests in tests
vi.mock('@/lib/rate-limiter', () => ({
  isRateLimited: vi.fn().mockResolvedValue(false),
}));

// Helper to create mock NextRequest
function createMockRequest(body: unknown, headers: Record<string, string> = {}): NextRequest {
  const url = 'http://localhost:3000/api/log-error';
  return new NextRequest(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'user-agent': 'test-agent',
      ...headers,
    },
    body: JSON.stringify(body),
  });
}

describe('POST /api/log-error', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock console.error to prevent test output noise
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Successful logging', () => {
    it('should log error with minimum required fields', async () => {
      const payload = {
        type: 'runtime_error',
        message: 'Test error message',
        timestamp: new Date().toISOString(),
      };

      const request = createMockRequest(payload);
      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.logged).toBe(true);
    });

    it('should log error with full payload', async () => {
      const payload = {
        type: 'unhandled_exception',
        message: 'Full error test',
        stack: 'Error: Full error test\n    at Test.run (test.ts:10)',
        componentStack: 'at Component\n    at App',
        url: 'http://localhost:3000/dashboard',
        timestamp: new Date().toISOString(),
        environment: 'test',
        context: {
          userId: '123',
          action: 'click_button',
        },
        user: {
          id: 'user-123',
          email: 'test@example.com',
        },
      };

      const request = createMockRequest(payload);
      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it('should handle error with Arabic message', async () => {
      const payload = {
        type: 'validation_error',
        message: 'خطأ في التحقق من البيانات',
        timestamp: new Date().toISOString(),
        context: {
          field: 'اسم المستخدم',
        },
      };

      const request = createMockRequest(payload);
      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });
  });

  describe('Validation errors', () => {
    it('should reject request without message', async () => {
      const payload = {
        type: 'error',
        timestamp: new Date().toISOString(),
      };

      const request = createMockRequest(payload);
      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toContain('Missing required fields');
    });

    it('should reject request without type', async () => {
      const payload = {
        message: 'Error without type',
        timestamp: new Date().toISOString(),
      };

      const request = createMockRequest(payload);
      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toContain('Missing required fields');
    });

    it('should reject empty payload', async () => {
      const request = createMockRequest({});
      const response = await POST(request);
      // const data = await response.json();

      expect(response.status).toBe(400);
    });
  });

  describe('Error handling', () => {
    it('should handle invalid JSON gracefully', async () => {
      const url = 'http://localhost:3000/api/log-error';
      const request = new NextRequest(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: 'invalid json{',
      });

      const response = await POST(request);
      expect(response.status).toBe(500);
    });
  });

  describe('Request headers', () => {
    it('should capture user-agent header', async () => {
      const payload = {
        type: 'test_error',
        message: 'Test with custom user-agent',
        timestamp: new Date().toISOString(),
      };

      const request = createMockRequest(payload, {
        'user-agent': 'Mozilla/5.0 Custom Browser',
      });

      const response = await POST(request);
      expect(response.status).toBe(200);

      // Verify console.error was called with structured log
      expect(console.error).toHaveBeenCalled();
    });

    it('should capture referer header', async () => {
      const payload = {
        type: 'navigation_error',
        message: 'Error during navigation',
        timestamp: new Date().toISOString(),
      };

      const request = createMockRequest(payload, {
        referer: 'http://localhost:3000/previous-page',
      });

      const response = await POST(request);
      expect(response.status).toBe(200);
    });
  });

  describe('Error types', () => {
    const errorTypes = [
      'runtime_error',
      'unhandled_exception',
      'network_error',
      'validation_error',
      'authentication_error',
      'authorization_error',
      'api_error',
      'render_error',
    ];

    errorTypes.forEach((errorType) => {
      it(`should accept error type: ${errorType}`, async () => {
        const payload = {
          type: errorType,
          message: `Test ${errorType}`,
          timestamp: new Date().toISOString(),
        };

        const request = createMockRequest(payload);
        const response = await POST(request);

        expect(response.status).toBe(200);
      });
    });
  });
});
