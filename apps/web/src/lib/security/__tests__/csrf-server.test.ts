/**
 * CSRF Server-Side Validation Tests
 * اختبارات التحقق من CSRF من جانب الخادم
 *
 * Tests timing-safe comparison, CSRF token validation,
 * method filtering, and path exclusions.
 */

import { describe, it, expect } from 'vitest';
import {
  validateCsrfToken,
  requiresCsrfValidation,
  validateCsrfRequest,
  CSRF_PROTECTED_METHODS,
} from '../csrf-server';

// Helper to create mock NextRequest
function createMockRequest(
  method: string,
  pathname: string,
  options: {
    csrfCookie?: string;
    csrfHeader?: string;
  } = {}
) {
  return {
    method,
    nextUrl: { pathname },
    cookies: {
      get: (name: string) => {
        if (name === 'csrf_token' && options.csrfCookie) {
          return { value: options.csrfCookie };
        }
        return undefined;
      },
    },
    headers: {
      get: (name: string) => {
        if (name === 'x-csrf-token') {
          return options.csrfHeader ?? null;
        }
        return null;
      },
    },
  } as Parameters<typeof validateCsrfRequest>[0];
}

describe('CSRF Server Validation', () => {
  describe('validateCsrfToken', () => {
    it('should return true for matching tokens', () => {
      const token = 'abc123def456ghi789';
      expect(validateCsrfToken(token, token)).toBe(true);
    });

    it('should return false for mismatched tokens', () => {
      expect(validateCsrfToken('token-a', 'token-b')).toBe(false);
    });

    it('should return false when cookie token is undefined', () => {
      expect(validateCsrfToken(undefined, 'token')).toBe(false);
    });

    it('should return false when header token is undefined', () => {
      expect(validateCsrfToken('token', undefined)).toBe(false);
    });

    it('should return false when both tokens are undefined', () => {
      expect(validateCsrfToken(undefined, undefined)).toBe(false);
    });

    it('should return false for different-length tokens', () => {
      expect(validateCsrfToken('short', 'much-longer-token')).toBe(false);
    });

    it('should use timing-safe comparison (same length, different content)', () => {
      expect(validateCsrfToken('aaaa', 'aaab')).toBe(false);
      expect(validateCsrfToken('aaaa', 'baaa')).toBe(false);
    });
  });

  describe('CSRF_PROTECTED_METHODS', () => {
    it('should include all state-changing HTTP methods', () => {
      expect(CSRF_PROTECTED_METHODS).toContain('POST');
      expect(CSRF_PROTECTED_METHODS).toContain('PUT');
      expect(CSRF_PROTECTED_METHODS).toContain('DELETE');
      expect(CSRF_PROTECTED_METHODS).toContain('PATCH');
    });

    it('should not include safe methods', () => {
      const methods = [...CSRF_PROTECTED_METHODS];
      expect(methods).not.toContain('GET');
      expect(methods).not.toContain('HEAD');
      expect(methods).not.toContain('OPTIONS');
    });
  });

  describe('requiresCsrfValidation', () => {
    it('should require validation for POST requests', () => {
      const req = createMockRequest('POST', '/dashboard/tasks');
      expect(requiresCsrfValidation(req)).toBe(true);
    });

    it('should require validation for PUT requests', () => {
      const req = createMockRequest('PUT', '/dashboard/fields/1');
      expect(requiresCsrfValidation(req)).toBe(true);
    });

    it('should require validation for DELETE requests', () => {
      const req = createMockRequest('DELETE', '/dashboard/tasks/1');
      expect(requiresCsrfValidation(req)).toBe(true);
    });

    it('should not require validation for GET requests', () => {
      const req = createMockRequest('GET', '/dashboard');
      expect(requiresCsrfValidation(req)).toBe(false);
    });

    it('should not require validation for HEAD requests', () => {
      const req = createMockRequest('HEAD', '/dashboard');
      expect(requiresCsrfValidation(req)).toBe(false);
    });

    it('should exclude /api/auth/login path', () => {
      const req = createMockRequest('POST', '/api/auth/login');
      expect(requiresCsrfValidation(req)).toBe(false);
    });

    it('should exclude /api/auth/register path', () => {
      const req = createMockRequest('POST', '/api/auth/register');
      expect(requiresCsrfValidation(req)).toBe(false);
    });

    it('should exclude /api/auth/logout path', () => {
      const req = createMockRequest('POST', '/api/auth/logout');
      expect(requiresCsrfValidation(req)).toBe(false);
    });

    it('should exclude /api/webhooks path', () => {
      const req = createMockRequest('POST', '/api/webhooks/stripe');
      expect(requiresCsrfValidation(req)).toBe(false);
    });
  });

  describe('validateCsrfRequest', () => {
    it('should pass for GET requests (no CSRF needed)', () => {
      const req = createMockRequest('GET', '/dashboard');
      const result = validateCsrfRequest(req);
      expect(result.valid).toBe(true);
    });

    it('should pass for POST with matching tokens', () => {
      const token = 'valid-csrf-token-123';
      const req = createMockRequest('POST', '/dashboard/tasks', {
        csrfCookie: token,
        csrfHeader: token,
      });
      const result = validateCsrfRequest(req);
      expect(result.valid).toBe(true);
    });

    it('should fail for POST without CSRF cookie', () => {
      const req = createMockRequest('POST', '/dashboard/tasks', {
        csrfHeader: 'some-token',
      });
      const result = validateCsrfRequest(req);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('cookie');
    });

    it('should fail for POST without CSRF header', () => {
      const req = createMockRequest('POST', '/dashboard/tasks', {
        csrfCookie: 'some-token',
      });
      const result = validateCsrfRequest(req);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('header');
    });

    it('should fail for POST with mismatched tokens', () => {
      const req = createMockRequest('POST', '/dashboard/tasks', {
        csrfCookie: 'token-a',
        csrfHeader: 'token-b',
      });
      const result = validateCsrfRequest(req);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('mismatch');
    });

    it('should pass for excluded auth paths even without tokens', () => {
      const req = createMockRequest('POST', '/api/auth/login');
      const result = validateCsrfRequest(req);
      expect(result.valid).toBe(true);
    });
  });
});
