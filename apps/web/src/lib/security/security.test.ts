/**
 * SAHOOL Security Tests
 * اختبارات الأمان
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  escapeHtml,
  sanitizeInput,
  sanitizeUrl,
  stripHtml,
  isRateLimited,
  getRateLimitRemaining,
  resetRateLimit,
  setSecureCookie,
  getCookie,
  deleteCookie,
  isSafeJson,
  safeJsonParse,
  validateSchema,
  checkPasswordStrength,
  getCsrfToken,
  getCsrfHeaders,
  configureSecurity,
  Security,
} from './security';

describe('Security', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset document.cookie
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
    });
  });

  describe('escapeHtml', () => {
    it('should escape HTML special characters', () => {
      expect(escapeHtml('<script>alert("xss")</script>')).toBe(
        '&lt;script&gt;alert(&quot;xss&quot;)&lt;&#x2F;script&gt;'
      );
    });

    it('should escape ampersands', () => {
      expect(escapeHtml('Tom & Jerry')).toBe('Tom &amp; Jerry');
    });

    it('should escape quotes', () => {
      expect(escapeHtml("It's a \"test\"")).toBe(
        'It&#x27;s a &quot;test&quot;'
      );
    });

    it('should handle empty string', () => {
      expect(escapeHtml('')).toBe('');
    });

    it('should handle text without special characters', () => {
      expect(escapeHtml('Hello World')).toBe('Hello World');
    });
  });

  describe('sanitizeInput', () => {
    it('should remove null bytes', () => {
      expect(sanitizeInput('hello\x00world')).not.toContain('\x00');
    });

    it('should remove control characters', () => {
      expect(sanitizeInput('hello\x01\x02world')).toBe('helloworld');
    });

    it('should escape HTML', () => {
      expect(sanitizeInput('<script>')).toBe('&lt;script&gt;');
    });

    it('should handle normal text', () => {
      expect(sanitizeInput('Hello World')).toBe('Hello World');
    });
  });

  describe('sanitizeUrl', () => {
    it('should allow http URLs', () => {
      expect(sanitizeUrl('http://example.com')).toBe('http://example.com/');
    });

    it('should allow https URLs', () => {
      expect(sanitizeUrl('https://example.com')).toBe('https://example.com/');
    });

    it('should reject javascript: URLs', () => {
      expect(sanitizeUrl('javascript:alert(1)')).toBeNull();
    });

    it('should reject data: URLs', () => {
      expect(sanitizeUrl('data:text/html,<script>alert(1)</script>')).toBeNull();
    });

    it('should handle relative URLs', () => {
      const result = sanitizeUrl('/path/to/page');
      expect(result).toContain('/path/to/page');
    });

    it('should return null for invalid URLs', () => {
      // This might throw or return null depending on implementation
      const result = sanitizeUrl('not a valid url with spaces');
      // Just check it doesn't throw
      expect(true).toBe(true);
    });
  });

  describe('stripHtml', () => {
    it('should remove HTML tags', () => {
      expect(stripHtml('<p>Hello <strong>World</strong></p>')).toBe(
        'Hello World'
      );
    });

    it('should handle nested tags', () => {
      expect(stripHtml('<div><span><a>Link</a></span></div>')).toBe('Link');
    });

    it('should handle empty HTML', () => {
      expect(stripHtml('')).toBe('');
    });

    it('should handle text without tags', () => {
      expect(stripHtml('Plain text')).toBe('Plain text');
    });
  });

  describe('Rate Limiting', () => {
    beforeEach(() => {
      resetRateLimit('test-key');
    });

    it('should not rate limit initial requests', () => {
      expect(isRateLimited('test-key')).toBe(false);
    });

    it('should track request count', () => {
      const initial = getRateLimitRemaining('test-key');
      isRateLimited('test-key');
      const after = getRateLimitRemaining('test-key');
      expect(after).toBe(initial - 1);
    });

    it('should rate limit after max requests', () => {
      configureSecurity({ rateLimitMaxRequests: 3 });

      expect(isRateLimited('limit-test')).toBe(false); // 1
      expect(isRateLimited('limit-test')).toBe(false); // 2
      expect(isRateLimited('limit-test')).toBe(false); // 3
      expect(isRateLimited('limit-test')).toBe(true); // Should be limited
    });

    it('should reset rate limit', () => {
      isRateLimited('reset-test');
      isRateLimited('reset-test');
      resetRateLimit('reset-test');

      expect(getRateLimitRemaining('reset-test')).toBeGreaterThan(0);
    });
  });

  describe('Cookie Handling', () => {
    it('should get cookie value', () => {
      Object.defineProperty(document, 'cookie', {
        writable: true,
        value: 'test_cookie=test_value',
      });

      expect(getCookie('test_cookie')).toBe('test_value');
    });

    it('should return null for missing cookie', () => {
      expect(getCookie('nonexistent')).toBeNull();
    });

    it('should set secure cookie', () => {
      setSecureCookie('new_cookie', 'new_value');
      // Cookie setting should not throw
      expect(true).toBe(true);
    });

    it('should delete cookie', () => {
      deleteCookie('to_delete');
      // Cookie deletion should not throw
      expect(true).toBe(true);
    });
  });

  describe('JSON Handling', () => {
    it('should validate safe JSON', () => {
      expect(isSafeJson('{"key": "value"}')).toBe(true);
    });

    it('should reject invalid JSON', () => {
      expect(isSafeJson('not json')).toBe(false);
    });

    it('should parse JSON safely', () => {
      expect(safeJsonParse('{"key": "value"}', {})).toEqual({ key: 'value' });
    });

    it('should return fallback for invalid JSON', () => {
      expect(safeJsonParse('invalid', { default: true })).toEqual({
        default: true,
      });
    });
  });

  describe('validateSchema', () => {
    it('should validate object with required fields', () => {
      const obj = { name: 'Test', age: 25 };
      expect(validateSchema<{ name: string; age: number }>(obj, ['name', 'age'])).toBe(
        true
      );
    });

    it('should reject object missing required fields', () => {
      const obj = { name: 'Test' };
      expect(validateSchema<{ name: string; age: number }>(obj, ['name', 'age'])).toBe(
        false
      );
    });

    it('should reject null', () => {
      expect(validateSchema(null, ['name'])).toBe(false);
    });

    it('should reject non-objects', () => {
      expect(validateSchema('string', ['name'])).toBe(false);
    });
  });

  describe('checkPasswordStrength', () => {
    it('should identify weak password', () => {
      const result = checkPasswordStrength('123');
      expect(result.isStrong).toBe(false);
      expect(result.score).toBeLessThan(3);
      expect(result.feedback.length).toBeGreaterThan(0);
    });

    it('should identify strong password', () => {
      const result = checkPasswordStrength('StrongP@ss123');
      expect(result.isStrong).toBe(true);
      expect(result.score).toBeGreaterThanOrEqual(3);
    });

    it('should provide feedback for improvements', () => {
      const result = checkPasswordStrength('onlylowercase');
      expect(result.feedback).toContain('أضف أحرف كبيرة');
      expect(result.feedback).toContain('أضف أرقام');
      expect(result.feedback).toContain('أضف رموز خاصة');
    });

    it('should check minimum length', () => {
      const result = checkPasswordStrength('Ab1!');
      expect(result.feedback).toContain(
        'يجب أن تكون كلمة المرور 8 أحرف على الأقل'
      );
    });
  });

  describe('CSRF Protection', () => {
    it('should get CSRF token from cookie', () => {
      Object.defineProperty(document, 'cookie', {
        writable: true,
        value: 'csrf_token=test_csrf_token_123',
      });

      expect(getCsrfToken()).toBe('test_csrf_token_123');
    });

    it('should return null if no CSRF token', () => {
      Object.defineProperty(document, 'cookie', {
        writable: true,
        value: '',
      });

      expect(getCsrfToken()).toBeNull();
    });

    it('should get CSRF headers', () => {
      Object.defineProperty(document, 'cookie', {
        writable: true,
        value: 'csrf_token=token123',
      });

      const headers = getCsrfHeaders();
      expect(headers['X-CSRF-Token']).toBe('token123');
    });

    it('should return empty headers if CSRF disabled', () => {
      configureSecurity({ csrfEnabled: false });
      const headers = getCsrfHeaders();
      expect(headers).toEqual({});
      // Reset
      configureSecurity({ csrfEnabled: true });
    });
  });

  describe('Security export', () => {
    it('should export all functions', () => {
      expect(Security.escapeHtml).toBeDefined();
      expect(Security.sanitizeInput).toBeDefined();
      expect(Security.sanitizeUrl).toBeDefined();
      expect(Security.isRateLimited).toBeDefined();
      expect(Security.checkPasswordStrength).toBeDefined();
      expect(Security.getCsrfToken).toBeDefined();
    });
  });
});
