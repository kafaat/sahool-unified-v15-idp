/**
 * CSP Configuration Tests
 * اختبارات إعدادات سياسة أمان المحتوى
 *
 * Tests nonce generation, CSP directives, header building,
 * and CSP violation report validation.
 */

import { describe, it, expect } from 'vitest';
import {
  generateNonce,
  getCSPDirectives,
  buildCSPHeader,
  getCSPConfig,
  getCSPHeader,
  getCSPHeaderName,
  isValidCSPReport,
  sanitizeCSPReport,
} from '../csp-config';

describe('CSP Configuration', () => {
  describe('generateNonce', () => {
    it('should generate a non-empty string', () => {
      const nonce = generateNonce();
      expect(nonce).toBeTruthy();
      expect(typeof nonce).toBe('string');
    });

    it('should generate unique nonces', () => {
      const nonces = new Set(Array.from({ length: 10 }, () => generateNonce()));
      expect(nonces.size).toBe(10);
    });

    it('should generate base64-encoded string', () => {
      const nonce = generateNonce();
      // Base64 characters: A-Z, a-z, 0-9, +, /, =
      expect(nonce).toMatch(/^[A-Za-z0-9+/=]+$/);
    });
  });

  describe('getCSPDirectives', () => {
    it('should include default-src self', () => {
      const directives = getCSPDirectives();
      expect(directives['default-src']).toContain("'self'");
    });

    it('should include script-src self', () => {
      const directives = getCSPDirectives();
      expect(directives['script-src']).toContain("'self'");
    });

    it('should include nonce in script-src when provided', () => {
      const nonce = 'test-nonce-123';
      const directives = getCSPDirectives(nonce);
      expect(directives['script-src']).toContain(`'nonce-${nonce}'`);
    });

    it('should include nonce in style-src when provided', () => {
      const nonce = 'test-nonce-123';
      const directives = getCSPDirectives(nonce);
      expect(directives['style-src']).toContain(`'nonce-${nonce}'`);
    });

    it('should block object-src', () => {
      const directives = getCSPDirectives();
      expect(directives['object-src']).toContain("'none'");
    });

    it('should block frame-src', () => {
      const directives = getCSPDirectives();
      expect(directives['frame-src']).toContain("'none'");
    });

    it('should prevent clickjacking with frame-ancestors', () => {
      const directives = getCSPDirectives();
      expect(directives['frame-ancestors']).toContain("'none'");
    });

    it('should restrict form-action to self', () => {
      const directives = getCSPDirectives();
      expect(directives['form-action']).toContain("'self'");
    });

    it('should restrict base-uri to self', () => {
      const directives = getCSPDirectives();
      expect(directives['base-uri']).toContain("'self'");
    });

    it('should allow Google Fonts in font-src', () => {
      const directives = getCSPDirectives();
      expect(directives['font-src']).toContain('https://fonts.gstatic.com');
    });

    it('should allow OpenStreetMap tiles in img-src', () => {
      const directives = getCSPDirectives();
      expect(directives['img-src']).toContain('https://tile.openstreetmap.org');
    });

    it('should include CSP report-uri', () => {
      const directives = getCSPDirectives();
      expect(directives['report-uri']).toContain('/api/csp-report');
    });

    it('should allow worker-src self and blob', () => {
      const directives = getCSPDirectives();
      expect(directives['worker-src']).toContain("'self'");
      expect(directives['worker-src']).toContain('blob:');
    });
  });

  describe('buildCSPHeader', () => {
    it('should build semicolon-separated header string', () => {
      const header = buildCSPHeader({
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'"],
      });
      expect(header).toContain("default-src 'self'");
      expect(header).toContain("script-src 'self' 'unsafe-inline'");
      expect(header).toContain('; ');
    });

    it('should include boolean directives when true', () => {
      const header = buildCSPHeader({
        'upgrade-insecure-requests': true,
      });
      expect(header).toContain('upgrade-insecure-requests');
    });

    it('should exclude boolean directives when false', () => {
      const header = buildCSPHeader({
        'upgrade-insecure-requests': false,
      });
      expect(header).not.toContain('upgrade-insecure-requests');
    });

    it('should handle empty directives', () => {
      const header = buildCSPHeader({});
      expect(header).toBe('');
    });
  });

  describe('getCSPConfig', () => {
    it('should return config with directives', () => {
      const config = getCSPConfig();
      expect(config.directives).toBeDefined();
      expect(config.directives['default-src']).toBeDefined();
    });

    it('should pass nonce to directives', () => {
      const config = getCSPConfig('my-nonce');
      expect(config.directives['script-src']).toContain("'nonce-my-nonce'");
    });
  });

  describe('getCSPHeader', () => {
    it('should return a non-empty CSP header string', () => {
      const header = getCSPHeader();
      expect(header).toBeTruthy();
      expect(header).toContain('default-src');
    });

    it('should include nonce when provided', () => {
      const header = getCSPHeader('test-nonce');
      expect(header).toContain('nonce-test-nonce');
    });
  });

  describe('getCSPHeaderName', () => {
    it('should return enforce header by default', () => {
      const name = getCSPHeaderName();
      expect(name).toBe('Content-Security-Policy');
    });

    it('should return report-only header when specified', () => {
      const name = getCSPHeaderName(true);
      expect(name).toBe('Content-Security-Policy-Report-Only');
    });
  });

  describe('isValidCSPReport', () => {
    it('should validate a correct CSP report', () => {
      const report = {
        'csp-report': {
          'document-uri': 'https://sahool.app/dashboard',
          'violated-directive': 'script-src',
          'effective-directive': 'script-src',
          'original-policy': "script-src 'self'",
          'blocked-uri': 'https://evil.com/script.js',
          'status-code': 200,
        },
      };
      expect(isValidCSPReport(report)).toBe(true);
    });

    it('should reject null body', () => {
      expect(isValidCSPReport(null)).toBe(false);
    });

    it('should reject non-object body', () => {
      expect(isValidCSPReport('string')).toBe(false);
    });

    it('should reject body without csp-report key', () => {
      expect(isValidCSPReport({ other: 'data' })).toBe(false);
    });

    it('should reject report missing document-uri', () => {
      const report = {
        'csp-report': {
          'violated-directive': 'script-src',
          'blocked-uri': 'https://evil.com',
        },
      };
      expect(isValidCSPReport(report)).toBe(false);
    });

    it('should reject report missing violated-directive', () => {
      const report = {
        'csp-report': {
          'document-uri': 'https://sahool.app',
          'blocked-uri': 'https://evil.com',
        },
      };
      expect(isValidCSPReport(report)).toBe(false);
    });
  });

  describe('sanitizeCSPReport', () => {
    it('should sanitize report for logging', () => {
      const report = {
        'document-uri': 'https://sahool.app/dashboard',
        'violated-directive': "script-src 'self'",
        'effective-directive': 'script-src',
        'original-policy': "script-src 'self'",
        'blocked-uri': 'https://evil.com/script.js',
        'status-code': 200,
        'source-file': 'https://sahool.app/main.js',
        'line-number': 42,
        'column-number': 10,
      };

      const sanitized = sanitizeCSPReport(report);

      expect(sanitized.documentUri).toBe('https://sahool.app/dashboard');
      expect(sanitized.violatedDirective).toBe("script-src 'self'");
      expect(sanitized.blockedUri).toBe('https://evil.com/script.js');
      expect(sanitized.statusCode).toBe(200);
      expect(sanitized.sourceFile).toBe('https://sahool.app/main.js');
      expect(sanitized.lineNumber).toBe(42);
      expect(sanitized.timestamp).toBeDefined();
    });
  });
});
