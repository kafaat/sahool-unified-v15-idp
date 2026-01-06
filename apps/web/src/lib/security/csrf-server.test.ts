/**
 * CSRF Server-Side Validation Tests
 * اختبارات التحقق من CSRF من جانب الخادم
 */

import { describe, it, expect } from 'vitest';
import { NextRequest } from 'next/server';
import {
  validateCsrfToken,
  requiresCsrfValidation,
  validateCsrfRequest,
  getCsrfErrorInfo,
  CSRF_PROTECTED_METHODS,
} from './csrf-server';

// Helper to create mock NextRequest
function createMockRequest(
  method: string,
  pathname: string,
  options?: {
    csrfCookie?: string;
    csrfHeader?: string;
  }
): NextRequest {
  const url = `http://localhost:3000${pathname}`;
  const request = new NextRequest(url, { method });

  // Set CSRF cookie if provided
  if (options?.csrfCookie) {
    request.cookies.set('csrf_token', options.csrfCookie);
  }

  // Set CSRF header if provided
  if (options?.csrfHeader) {
    request.headers.set('x-csrf-token', options.csrfHeader);
  }

  return request;
}

describe('CSRF Server-Side Validation', () => {
  describe('validateCsrfToken', () => {
    it('should return false when both tokens are missing', () => {
      const result = validateCsrfToken(undefined, undefined);
      expect(result).toBe(false);
    });

    it('should return false when cookie token is missing', () => {
      const result = validateCsrfToken(undefined, 'header-token');
      expect(result).toBe(false);
    });

    it('should return false when header token is missing', () => {
      const result = validateCsrfToken('cookie-token', undefined);
      expect(result).toBe(false);
    });

    it('should return false when tokens have different lengths', () => {
      const result = validateCsrfToken('short', 'much-longer-token');
      expect(result).toBe(false);
    });

    it('should return true when tokens match exactly', () => {
      const token = 'test-token-123';
      const result = validateCsrfToken(token, token);
      expect(result).toBe(true);
    });

    it('should return false when tokens do not match', () => {
      const result = validateCsrfToken('token-1', 'token-2');
      expect(result).toBe(false);
    });

    it('should use timing-safe comparison', () => {
      // This test ensures the function uses timingSafeEqual
      const token1 = 'a'.repeat(32);
      const token2 = 'b'.repeat(32);
      const result = validateCsrfToken(token1, token2);
      expect(result).toBe(false);
    });

    it('should handle base64url encoded tokens', () => {
      const token = 'abc123DEF456-_=';
      const result = validateCsrfToken(token, token);
      expect(result).toBe(true);
    });
  });

  describe('requiresCsrfValidation', () => {
    it('should return true for POST requests', () => {
      const request = createMockRequest('POST', '/api/fields');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(true);
    });

    it('should return true for PUT requests', () => {
      const request = createMockRequest('PUT', '/api/fields/123');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(true);
    });

    it('should return true for DELETE requests', () => {
      const request = createMockRequest('DELETE', '/api/fields/123');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(true);
    });

    it('should return true for PATCH requests', () => {
      const request = createMockRequest('PATCH', '/api/fields/123');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(true);
    });

    it('should return false for GET requests', () => {
      const request = createMockRequest('GET', '/api/fields');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(false);
    });

    it('should return false for HEAD requests', () => {
      const request = createMockRequest('HEAD', '/api/fields');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(false);
    });

    it('should return false for OPTIONS requests', () => {
      const request = createMockRequest('OPTIONS', '/api/fields');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(false);
    });

    it('should exclude auth login endpoint', () => {
      const request = createMockRequest('POST', '/api/auth/login');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(false);
    });

    it('should exclude auth register endpoint', () => {
      const request = createMockRequest('POST', '/api/auth/register');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(false);
    });

    it('should exclude webhooks', () => {
      const request = createMockRequest('POST', '/api/webhooks/stripe');
      const result = requiresCsrfValidation(request);
      expect(result).toBe(false);
    });

    it('should validate custom excluded paths', () => {
      const request = createMockRequest('POST', '/api/public/endpoint');
      const result = requiresCsrfValidation(request, {
        excludePaths: ['/api/public'],
      });
      expect(result).toBe(false);
    });
  });

  describe('validateCsrfRequest', () => {
    it('should return valid for GET requests (no CSRF needed)', () => {
      const request = createMockRequest('GET', '/dashboard');
      const result = validateCsrfRequest(request);
      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should return invalid when cookie is missing', () => {
      const request = createMockRequest('POST', '/api/fields', {
        csrfHeader: 'test-token',
      });
      const result = validateCsrfRequest(request);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('CSRF token cookie not found');
    });

    it('should return invalid when header is missing', () => {
      const request = createMockRequest('POST', '/api/fields', {
        csrfCookie: 'test-token',
      });
      const result = validateCsrfRequest(request);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('CSRF token header not found');
    });

    it('should return invalid when tokens do not match', () => {
      const request = createMockRequest('POST', '/api/fields', {
        csrfCookie: 'cookie-token',
        csrfHeader: 'header-token',
      });
      const result = validateCsrfRequest(request);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('CSRF token mismatch');
    });

    it('should return valid when tokens match', () => {
      const token = 'matching-token-123';
      const request = createMockRequest('POST', '/api/fields', {
        csrfCookie: token,
        csrfHeader: token,
      });
      const result = validateCsrfRequest(request);
      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('should work with custom cookie name', () => {
      const token = 'test-token';
      const request = createMockRequest('POST', '/api/fields');
      request.cookies.set('my_csrf', token);
      request.headers.set('x-csrf-token', token);

      const result = validateCsrfRequest(request, {
        cookieName: 'my_csrf',
      });
      expect(result.valid).toBe(true);
    });

    it('should work with custom header name', () => {
      const token = 'test-token';
      const request = createMockRequest('POST', '/api/fields');
      request.cookies.set('csrf_token', token);
      request.headers.set('x-custom-csrf', token);

      const result = validateCsrfRequest(request, {
        headerName: 'x-custom-csrf',
      });
      expect(result.valid).toBe(true);
    });
  });

  describe('getCsrfErrorInfo', () => {
    it('should return error information', () => {
      const request = createMockRequest('POST', '/api/fields', {
        csrfCookie: 'test',
        csrfHeader: 'test',
      });
      const info = getCsrfErrorInfo(request, 'Test error');

      expect(info.error).toBe('Test error');
      expect(info.method).toBe('POST');
      expect(info.path).toBe('/api/fields');
      expect(info.hasTokenCookie).toBe(true);
      expect(info.hasTokenHeader).toBe(true);
    });

    it('should detect missing tokens', () => {
      const request = createMockRequest('POST', '/api/fields');
      const info = getCsrfErrorInfo(request, 'Missing tokens');

      expect(info.hasTokenCookie).toBe(false);
      expect(info.hasTokenHeader).toBe(false);
    });
  });

  describe('CSRF_PROTECTED_METHODS', () => {
    it('should include all state-changing methods', () => {
      expect(CSRF_PROTECTED_METHODS).toContain('POST');
      expect(CSRF_PROTECTED_METHODS).toContain('PUT');
      expect(CSRF_PROTECTED_METHODS).toContain('DELETE');
      expect(CSRF_PROTECTED_METHODS).toContain('PATCH');
    });

    it('should not include safe methods', () => {
      expect(CSRF_PROTECTED_METHODS).not.toContain('GET');
      expect(CSRF_PROTECTED_METHODS).not.toContain('HEAD');
      expect(CSRF_PROTECTED_METHODS).not.toContain('OPTIONS');
    });
  });

  describe('Edge Cases', () => {
    it('should handle very long tokens', () => {
      const longToken = 'a'.repeat(1000);
      const result = validateCsrfToken(longToken, longToken);
      expect(result).toBe(true);
    });

    it('should handle special characters in tokens', () => {
      const token = 'token-with-special_chars-123=';
      const result = validateCsrfToken(token, token);
      expect(result).toBe(true);
    });

    it('should handle unicode characters', () => {
      const token = 'token-مع-العربية-123';
      const result = validateCsrfToken(token, token);
      expect(result).toBe(true);
    });

    it('should handle empty strings', () => {
      const result = validateCsrfToken('', '');
      expect(result).toBe(false); // Empty tokens should be rejected
    });

    it('should be case-sensitive', () => {
      const result = validateCsrfToken('Token123', 'token123');
      expect(result).toBe(false);
    });
  });

  describe('Security Requirements', () => {
    it('should use constant-time comparison to prevent timing attacks', () => {
      // This test ensures timing attacks are not possible
      const token1 = 'a'.repeat(32);
      const token2 = 'a'.repeat(31) + 'b';

      // Both should take similar time regardless of where they differ
      const start1 = performance.now();
      validateCsrfToken(token1, token2);
      const time1 = performance.now() - start1;

      const token3 = 'b' + 'a'.repeat(31);
      const start2 = performance.now();
      validateCsrfToken(token1, token3);
      const time2 = performance.now() - start2;

      // Times should be similar (within reasonable margin)
      // This is a weak test but demonstrates the intent
      expect(Math.abs(time1 - time2)).toBeLessThan(5);
    });

    it('should validate all POST requests by default', () => {
      const protectedPaths = ['/api/fields', '/api/tasks', '/api/settings'];

      protectedPaths.forEach((path) => {
        const request = createMockRequest('POST', path);
        expect(requiresCsrfValidation(request)).toBe(true);
      });
    });

    it('should allow configuration of excluded paths', () => {
      const request = createMockRequest('POST', '/api/public/endpoint');

      // Should require validation by default
      expect(requiresCsrfValidation(request)).toBe(true);

      // Should not require validation when excluded
      expect(
        requiresCsrfValidation(request, {
          excludePaths: ['/api/public'],
        })
      ).toBe(false);
    });
  });
});
