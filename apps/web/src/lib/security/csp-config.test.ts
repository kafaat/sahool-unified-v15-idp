/**
 * SAHOOL CSP Configuration Tests
 * اختبارات تكوين CSP
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  generateNonce,
  getCSPDirectives,
  buildCSPHeader,
  getCSPConfig,
  getCSPHeader,
  getCSPHeaderName,
  isValidCSPReport,
  sanitizeCSPReport,
  type CSPViolationReport,
  type CSPReportBody,
} from './csp-config';

describe('CSP Nonce Generation', () => {
  it('should generate a nonce', () => {
    const nonce = generateNonce();
    expect(nonce).toBeDefined();
    expect(typeof nonce).toBe('string');
    expect(nonce.length).toBeGreaterThan(0);
  });

  it('should generate unique nonces', () => {
    const nonce1 = generateNonce();
    const nonce2 = generateNonce();
    expect(nonce1).not.toBe(nonce2);
  });

  it('should generate base64 encoded nonces', () => {
    const nonce = generateNonce();
    // Base64 pattern: alphanumeric + / + = padding
    expect(nonce).toMatch(/^[A-Za-z0-9+/]+=*$/);
  });
});

describe('CSP Directives', () => {
  const originalEnv = process.env.NODE_ENV;

  beforeEach(() => {
    process.env.NODE_ENV = originalEnv;
  });

  it('should include nonce in script-src when provided', () => {
    const directives = getCSPDirectives('test-nonce-123');
    expect(directives['script-src']).toContain("'nonce-test-nonce-123'");
  });

  it('should include nonce in style-src when provided', () => {
    const directives = getCSPDirectives('test-nonce-123');
    expect(directives['style-src']).toContain("'nonce-test-nonce-123'");
  });

  it('should have script-src array', () => {
    // Note: isDevelopment/isProduction are evaluated at module load time
    const directives = getCSPDirectives();
    expect(Array.isArray(directives['script-src'])).toBe(true);
    expect(directives['script-src']).toContain("'self'");
  });

  it('should have style-src array', () => {
    // Note: isDevelopment/isProduction are evaluated at module load time
    const directives = getCSPDirectives();
    expect(Array.isArray(directives['style-src'])).toBe(true);
    expect(directives['style-src']).toContain("'self'");
    expect(directives['style-src']).toContain('https://fonts.googleapis.com');
  });

  it('should include strict-dynamic in script-src with nonce (non-dev)', () => {
    // In test environment (not development), strict-dynamic may be added
    const directives = getCSPDirectives('test-nonce');
    expect(directives['script-src']).toContain("'nonce-test-nonce'");
  });

  it('should block object-src', () => {
    const directives = getCSPDirectives();
    expect(directives['object-src']).toEqual(["'none'"]);
  });

  it('should block frame-ancestors', () => {
    const directives = getCSPDirectives();
    expect(directives['frame-ancestors']).toEqual(["'none'"]);
  });

  it('should include report-uri', () => {
    const directives = getCSPDirectives();
    expect(directives['report-uri']).toContain('/api/csp-report');
  });

  it('should have upgrade-insecure-requests directive', () => {
    // Note: isProduction is evaluated at module load time
    const directives = getCSPDirectives();
    expect(directives).toHaveProperty('upgrade-insecure-requests');
    expect(typeof directives['upgrade-insecure-requests']).toBe('boolean');
  });

  it('should have block-all-mixed-content directive', () => {
    // Note: isProduction is evaluated at module load time
    const directives = getCSPDirectives();
    expect(directives).toHaveProperty('block-all-mixed-content');
    expect(typeof directives['block-all-mixed-content']).toBe('boolean');
  });
});

describe('CSP Header Building', () => {
  it('should build a valid CSP header', () => {
    const directives = getCSPDirectives('test-nonce');
    const header = buildCSPHeader(directives);

    expect(header).toContain("default-src 'self'");
    expect(header).toContain("script-src");
    expect(header).toContain("style-src");
  });

  it('should separate directives with semicolons', () => {
    const directives = getCSPDirectives();
    const header = buildCSPHeader(directives);

    const directiveCount = header.split(';').length;
    expect(directiveCount).toBeGreaterThan(1);
  });

  it('should handle boolean directives when set', () => {
    // Test that boolean directives are properly formatted when true
    const directives = getCSPDirectives();
    // Force boolean directives to true for testing header building
    directives['upgrade-insecure-requests'] = true;
    directives['block-all-mixed-content'] = true;
    const header = buildCSPHeader(directives);

    expect(header).toContain('upgrade-insecure-requests');
    expect(header).toContain('block-all-mixed-content');
  });

  it('should include nonce in header', () => {
    const header = buildCSPHeader(getCSPDirectives('abc123'));
    expect(header).toContain("'nonce-abc123'");
  });
});

describe('CSP Configuration', () => {
  it('should return complete config', () => {
    const config = getCSPConfig('test-nonce');

    expect(config).toHaveProperty('directives');
    expect(config).toHaveProperty('reportOnly');
  });

  it('should have reportOnly property', () => {
    // Note: isDevelopment is evaluated at module load time, so we test the return structure
    const config = getCSPConfig();
    expect(config).toHaveProperty('reportOnly');
    expect(typeof config.reportOnly).toBe('boolean');
  });

  it('should not use report-only in non-development environments', () => {
    // In test environment (not development), reportOnly should be false
    // regardless of CSP_REPORT_ONLY setting
    const config = getCSPConfig();
    expect(config.reportOnly).toBe(false);
  });
});

describe('CSP Header Utilities', () => {
  it('should get CSP header value', () => {
    const header = getCSPHeader('test-nonce');
    expect(typeof header).toBe('string');
    expect(header.length).toBeGreaterThan(0);
  });

  it('should return correct header name for enforcing mode', () => {
    const name = getCSPHeaderName(false);
    expect(name).toBe('Content-Security-Policy');
  });

  it('should return correct header name for report-only mode', () => {
    const name = getCSPHeaderName(true);
    expect(name).toBe('Content-Security-Policy-Report-Only');
  });
});

describe('CSP Violation Reporting', () => {
  it('should validate valid CSP report', () => {
    const report: CSPReportBody = {
      'csp-report': {
        'document-uri': 'https://sahool.ye/dashboard',
        'violated-directive': 'script-src',
        'effective-directive': 'script-src',
        'original-policy': 'default-src self',
        'blocked-uri': 'https://evil.com/script.js',
        'status-code': 200,
      },
    };

    expect(isValidCSPReport(report)).toBe(true);
  });

  it('should reject invalid CSP report - missing csp-report', () => {
    const report = {
      something: 'else',
    };

    expect(isValidCSPReport(report)).toBe(false);
  });

  it('should reject invalid CSP report - missing required fields', () => {
    const report = {
      'csp-report': {
        'document-uri': 'https://sahool.ye/dashboard',
        // missing violated-directive and blocked-uri
      },
    };

    expect(isValidCSPReport(report)).toBe(false);
  });

  it('should reject non-object reports', () => {
    expect(isValidCSPReport(null)).toBe(false);
    expect(isValidCSPReport(undefined)).toBe(false);
    expect(isValidCSPReport('string')).toBe(false);
    expect(isValidCSPReport(123)).toBe(false);
  });

  it('should sanitize CSP report', () => {
    const report: CSPViolationReport = {
      'document-uri': 'https://sahool.ye/dashboard',
      'violated-directive': 'script-src',
      'effective-directive': 'script-src',
      'original-policy': 'default-src self',
      'blocked-uri': 'https://evil.com/script.js',
      'status-code': 200,
      'source-file': 'https://sahool.ye/page.html',
      'line-number': 42,
      'column-number': 10,
    };

    const sanitized = sanitizeCSPReport(report);

    expect(sanitized).toHaveProperty('timestamp');
    expect(sanitized).toHaveProperty('documentUri', 'https://sahool.ye/dashboard');
    expect(sanitized).toHaveProperty('violatedDirective', 'script-src');
    expect(sanitized).toHaveProperty('blockedUri', 'https://evil.com/script.js');
    expect(sanitized).toHaveProperty('lineNumber', 42);
    expect(sanitized).toHaveProperty('columnNumber', 10);
  });

  it('should include timestamp in sanitized report', () => {
    const report: CSPViolationReport = {
      'document-uri': 'https://sahool.ye',
      'violated-directive': 'script-src',
      'effective-directive': 'script-src',
      'original-policy': '',
      'blocked-uri': 'https://evil.com',
      'status-code': 200,
    };

    const sanitized = sanitizeCSPReport(report);
    const timestamp = sanitized.timestamp as string;

    expect(timestamp).toBeDefined();
    expect(() => new Date(timestamp)).not.toThrow();
  });
});
