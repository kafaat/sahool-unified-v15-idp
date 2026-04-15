/**
 * Security Libraries Comprehensive Tests
 * اختبارات شاملة لمكتبات الأمان
 *
 * Tests csrf-server.ts and csp-config.ts via source analysis and runtime behavior
 */

import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// ---------------------------------------------------------------------------
// Source analysis
// ---------------------------------------------------------------------------
const CSRF_PATH = path.resolve(__dirname, '../csrf-server.ts');
const CSP_PATH = path.resolve(__dirname, '../csp-config.ts');

const csrfSource = fs.readFileSync(CSRF_PATH, 'utf-8');
const cspSource = fs.readFileSync(CSP_PATH, 'utf-8');

// ---------------------------------------------------------------------------
// Runtime imports
// ---------------------------------------------------------------------------
import {
  generateCsrfToken,
  validateCsrfToken,
  requiresCsrfValidation,
  validateCsrfRequest,
  CSRF_PROTECTED_METHODS,
} from '../csrf-server';

import {
  generateNonce,
  getCSPDirectives,
  buildCSPHeader,
  getCSPConfig,
  getCSPHeader,
  getCSPHeaderName,
  isValidCSPReport,
  sanitizeCSPReport,
  CSP,
} from '../csp-config';

// ═══════════════════════════════════════════════════════════════════════════
// CSRF Server Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('csrf-server.ts — source structure', () => {
  it('file exists and is non-empty', () => {
    expect(csrfSource.length).toBeGreaterThan(0);
  });

  it('exports generateCsrfToken function', () => {
    expect(csrfSource).toMatch(/export\s+function\s+generateCsrfToken/);
  });

  it('exports validateCsrfToken function', () => {
    expect(csrfSource).toMatch(/export\s+function\s+validateCsrfToken/);
  });

  it('exports validateCsrfRequest function', () => {
    expect(csrfSource).toMatch(/export\s+function\s+validateCsrfRequest/);
  });

  it('exports requiresCsrfValidation function', () => {
    expect(csrfSource).toMatch(/export\s+function\s+requiresCsrfValidation/);
  });

  it('exports CSRF_PROTECTED_METHODS constant', () => {
    expect(csrfSource).toMatch(/export\s+const\s+CSRF_PROTECTED_METHODS/);
  });

  it('implements timingSafeCompare for timing attack prevention', () => {
    expect(csrfSource).toContain('timingSafeCompare');
    expect(csrfSource).toContain('charCodeAt');
  });

  it('uses Web Crypto API for edge runtime compatibility', () => {
    expect(csrfSource).toContain('crypto.getRandomValues');
  });

  it('defines CsrfConfig interface', () => {
    expect(csrfSource).toContain('interface CsrfConfig');
    expect(csrfSource).toContain('cookieName');
    expect(csrfSource).toContain('headerName');
    expect(csrfSource).toContain('excludePaths');
  });
});

describe('csrf-server — token generation', () => {
  it('generates a hex string token', () => {
    const token = generateCsrfToken();
    expect(token).toMatch(/^[0-9a-f]+$/);
  });

  it('generates 64-character tokens (32 bytes as hex)', () => {
    const token = generateCsrfToken();
    expect(token).toHaveLength(64);
  });

  it('generates unique tokens on each call', () => {
    const tokens = new Set(Array.from({ length: 20 }, () => generateCsrfToken()));
    expect(tokens.size).toBe(20);
  });
});

describe('csrf-server — token validation', () => {
  it('returns true when cookie and header tokens match', () => {
    const token = generateCsrfToken();
    expect(validateCsrfToken(token, token)).toBe(true);
  });

  it('returns false when tokens differ', () => {
    const a = generateCsrfToken();
    const b = generateCsrfToken();
    expect(validateCsrfToken(a, b)).toBe(false);
  });

  it('returns false when cookie token is undefined', () => {
    expect(validateCsrfToken(undefined, 'some-token')).toBe(false);
  });

  it('returns false when header token is undefined', () => {
    expect(validateCsrfToken('some-token', undefined)).toBe(false);
  });

  it('returns false when both tokens are undefined', () => {
    expect(validateCsrfToken(undefined, undefined)).toBe(false);
  });

  it('returns false when tokens have different lengths', () => {
    expect(validateCsrfToken('short', 'muchlongertoken')).toBe(false);
  });

  it('returns false for empty string tokens', () => {
    expect(validateCsrfToken('', '')).toBe(false);
    // The timingSafeCompare returns true for two empty strings (length 0, result 0),
    // but validateCsrfToken checks for falsy first — empty strings are falsy
  });
});

describe('csrf-server — CSRF_PROTECTED_METHODS', () => {
  it('includes POST', () => {
    expect(CSRF_PROTECTED_METHODS).toContain('POST');
  });

  it('includes PUT', () => {
    expect(CSRF_PROTECTED_METHODS).toContain('PUT');
  });

  it('includes DELETE', () => {
    expect(CSRF_PROTECTED_METHODS).toContain('DELETE');
  });

  it('includes PATCH', () => {
    expect(CSRF_PROTECTED_METHODS).toContain('PATCH');
  });

  it('does not include GET', () => {
    expect(CSRF_PROTECTED_METHODS).not.toContain('GET');
  });

  it('does not include HEAD', () => {
    expect(CSRF_PROTECTED_METHODS).not.toContain('HEAD');
  });
});

describe('csrf-server — requiresCsrfValidation', () => {
  function makeRequest(method: string, pathname: string) {
    return {
      method,
      nextUrl: { pathname },
      cookies: { get: () => undefined },
      headers: { get: () => null },
    } as unknown as import('next/server').NextRequest;
  }

  it('returns true for POST to protected path', () => {
    expect(requiresCsrfValidation(makeRequest('POST', '/api/farms'))).toBe(true);
  });

  it('returns true for PUT to protected path', () => {
    expect(requiresCsrfValidation(makeRequest('PUT', '/api/farms/1'))).toBe(true);
  });

  it('returns true for DELETE to protected path', () => {
    expect(requiresCsrfValidation(makeRequest('DELETE', '/api/farms/1'))).toBe(true);
  });

  it('returns true for PATCH to protected path', () => {
    expect(requiresCsrfValidation(makeRequest('PATCH', '/api/farms/1'))).toBe(true);
  });

  it('returns false for GET requests', () => {
    expect(requiresCsrfValidation(makeRequest('GET', '/api/farms'))).toBe(false);
  });

  it('returns false for HEAD requests', () => {
    expect(requiresCsrfValidation(makeRequest('HEAD', '/api/farms'))).toBe(false);
  });

  it('returns false for excluded paths: /api/auth/login', () => {
    expect(requiresCsrfValidation(makeRequest('POST', '/api/auth/login'))).toBe(false);
  });

  it('returns false for excluded paths: /api/health', () => {
    expect(requiresCsrfValidation(makeRequest('POST', '/api/health'))).toBe(false);
  });

  it('returns false for excluded paths: /login', () => {
    expect(requiresCsrfValidation(makeRequest('POST', '/login'))).toBe(false);
  });
});

describe('csrf-server — validateCsrfRequest', () => {
  function makeRequest(
    method: string,
    pathname: string,
    cookieValue?: string,
    headerValue?: string | null,
  ) {
    return {
      method,
      nextUrl: { pathname },
      cookies: {
        get: (name: string) =>
          name === 'sahool_admin_csrf' && cookieValue ? { value: cookieValue } : undefined,
      },
      headers: {
        get: (name: string) => (name === 'x-csrf-token' ? (headerValue ?? null) : null),
      },
    } as unknown as import('next/server').NextRequest;
  }

  it('returns valid for GET requests (no CSRF needed)', () => {
    const result = validateCsrfRequest(makeRequest('GET', '/api/farms'));
    expect(result.valid).toBe(true);
  });

  it('returns invalid when cookie token is missing', () => {
    const result = validateCsrfRequest(makeRequest('POST', '/api/farms', undefined, 'header-token'));
    expect(result.valid).toBe(false);
    expect(result.error).toContain('cookie');
  });

  it('returns invalid when header token is missing', () => {
    const result = validateCsrfRequest(makeRequest('POST', '/api/farms', 'cookie-token', null));
    expect(result.valid).toBe(false);
    expect(result.error).toContain('header');
  });

  it('returns invalid when tokens do not match', () => {
    const result = validateCsrfRequest(
      makeRequest('POST', '/api/farms', 'aaaa'.repeat(16), 'bbbb'.repeat(16))
    );
    expect(result.valid).toBe(false);
    expect(result.error).toContain('mismatch');
  });

  it('returns valid when tokens match', () => {
    const token = generateCsrfToken();
    const result = validateCsrfRequest(makeRequest('POST', '/api/farms', token, token));
    expect(result.valid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it('returns valid for excluded path even with POST', () => {
    const result = validateCsrfRequest(makeRequest('POST', '/api/auth/login'));
    expect(result.valid).toBe(true);
  });
});

describe('csrf-server — default config', () => {
  it('uses sahool_admin_csrf as cookie name', () => {
    expect(csrfSource).toContain("'sahool_admin_csrf'");
  });

  it('uses x-csrf-token as header name', () => {
    expect(csrfSource).toContain("'x-csrf-token'");
  });

  it('excludes /api/auth/login from CSRF', () => {
    expect(csrfSource).toContain("'/api/auth/login'");
  });

  it('excludes /api/health from CSRF', () => {
    expect(csrfSource).toContain("'/api/health'");
  });

  it('does NOT exclude /api/auth/logout (prevents logout CSRF)', () => {
    // The source explicitly notes logout is not excluded
    expect(csrfSource).toContain('logout is NOT excluded');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// CSP Config Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('csp-config.ts — source structure', () => {
  it('file exists and is non-empty', () => {
    expect(cspSource.length).toBeGreaterThan(0);
  });

  it('exports generateNonce function', () => {
    expect(cspSource).toMatch(/export\s+function\s+generateNonce/);
  });

  it('exports getCSPDirectives function', () => {
    expect(cspSource).toMatch(/export\s+function\s+getCSPDirectives/);
  });

  it('exports buildCSPHeader function', () => {
    expect(cspSource).toMatch(/export\s+function\s+buildCSPHeader/);
  });

  it('exports getCSPConfig function', () => {
    expect(cspSource).toMatch(/export\s+function\s+getCSPConfig/);
  });

  it('exports getCSPHeader function', () => {
    expect(cspSource).toMatch(/export\s+function\s+getCSPHeader/);
  });

  it('exports getCSPHeaderName function', () => {
    expect(cspSource).toMatch(/export\s+function\s+getCSPHeaderName/);
  });

  it('exports CSPDirectives interface', () => {
    expect(cspSource).toContain('interface CSPDirectives');
  });

  it('exports CSPConfig interface', () => {
    expect(cspSource).toContain('interface CSPConfig');
  });

  it('exports a default CSP namespace object', () => {
    expect(cspSource).toMatch(/export\s+const\s+CSP\s*=/);
    expect(cspSource).toContain('export default CSP');
  });

  it('exports isValidCSPReport function', () => {
    expect(cspSource).toMatch(/export\s+function\s+isValidCSPReport/);
  });

  it('exports sanitizeCSPReport function', () => {
    expect(cspSource).toMatch(/export\s+function\s+sanitizeCSPReport/);
  });
});

describe('csp-config — nonce generation', () => {
  it('generates a base64 string nonce', () => {
    const nonce = generateNonce();
    expect(typeof nonce).toBe('string');
    expect(nonce.length).toBeGreaterThan(0);
  });

  it('generates unique nonces', () => {
    const nonces = new Set(Array.from({ length: 20 }, () => generateNonce()));
    expect(nonces.size).toBe(20);
  });

  it('uses Web Crypto API (crypto.getRandomValues)', () => {
    expect(cspSource).toContain('crypto.getRandomValues');
  });

  it('uses 16 bytes of randomness', () => {
    expect(cspSource).toContain('Uint8Array(16)');
  });
});

describe('csp-config — directive configuration', () => {
  it('includes default-src self', () => {
    const directives = getCSPDirectives();
    expect(directives['default-src']).toContain("'self'");
  });

  it('includes script-src self', () => {
    const directives = getCSPDirectives();
    expect(directives['script-src']).toContain("'self'");
  });

  it('includes nonce in script-src when provided', () => {
    const nonce = 'test-nonce-123';
    const directives = getCSPDirectives(nonce);
    expect(directives['script-src']).toContain(`'nonce-${nonce}'`);
  });

  it('includes nonce in style-src when provided', () => {
    const nonce = 'test-nonce-123';
    const directives = getCSPDirectives(nonce);
    expect(directives['style-src']).toContain(`'nonce-${nonce}'`);
  });

  it('blocks object-src (none)', () => {
    const directives = getCSPDirectives();
    expect(directives['object-src']).toContain("'none'");
  });

  it('restricts frame-src to self + Google embeds only (no wildcard)', () => {
    // `'none'` was over-restrictive and broke Google Maps / reCAPTCHA in
    // Chrome. We now allow only the specific third-party iframes we embed.
    // Clickjacking protection is still enforced by `frame-ancestors: 'none'`.
    const directives = getCSPDirectives();
    const frameSrc = directives['frame-src'] ?? [];
    expect(frameSrc).toContain("'self'");
    expect(frameSrc).toContain('https://maps.google.com');
    expect(frameSrc).toContain('https://www.google.com');
    expect(frameSrc).not.toContain('*');
    expect(frameSrc.some((s) => /unsafe/i.test(s))).toBe(false);
  });

  it('blocks frame-ancestors (none) to prevent clickjacking', () => {
    const directives = getCSPDirectives();
    expect(directives['frame-ancestors']).toContain("'none'");
  });

  it('restricts form-action to self', () => {
    const directives = getCSPDirectives();
    expect(directives['form-action']).toContain("'self'");
  });

  it('restricts base-uri to self', () => {
    const directives = getCSPDirectives();
    expect(directives['base-uri']).toContain("'self'");
  });

  it('allows data: and blob: for img-src', () => {
    const directives = getCSPDirectives();
    expect(directives['img-src']).toContain('data:');
    expect(directives['img-src']).toContain('blob:');
  });

  it('includes Google Fonts in style-src', () => {
    const directives = getCSPDirectives();
    expect(directives['style-src']).toContain('https://fonts.googleapis.com');
  });

  it('includes Google Fonts CDN in font-src', () => {
    const directives = getCSPDirectives();
    expect(directives['font-src']).toContain('https://fonts.gstatic.com');
  });

  it('includes SAHOOL API servers in connect-src', () => {
    const directives = getCSPDirectives();
    expect(directives['connect-src']).toContain('https://api.sahool.io');
    expect(directives['connect-src']).toContain('https://api.sahool.app');
  });

  it('includes OpenStreetMap tile server in img-src', () => {
    const directives = getCSPDirectives();
    expect(directives['img-src']).toContain('https://tile.openstreetmap.org');
  });

  it('allows blob: and self for worker-src', () => {
    const directives = getCSPDirectives();
    expect(directives['worker-src']).toContain("'self'");
    expect(directives['worker-src']).toContain('blob:');
  });

  it('includes CSP report-uri', () => {
    const directives = getCSPDirectives();
    expect(directives['report-uri']).toContain('/api/csp-report');
  });

  it('sets manifest-src to self', () => {
    const directives = getCSPDirectives();
    expect(directives['manifest-src']).toContain("'self'");
  });
});

describe('csp-config — header building', () => {
  it('builds a semicolon-separated CSP header string', () => {
    const directives = getCSPDirectives();
    const header = buildCSPHeader(directives);
    expect(header).toContain(';');
    expect(header).toContain("default-src 'self'");
  });

  it('includes object-src none in built header', () => {
    const header = buildCSPHeader(getCSPDirectives());
    expect(header).toContain("object-src 'none'");
  });

  it('handles boolean directives correctly', () => {
    const header = buildCSPHeader({
      'upgrade-insecure-requests': true,
      'block-all-mixed-content': false,
    });
    expect(header).toContain('upgrade-insecure-requests');
    expect(header).not.toContain('block-all-mixed-content');
  });

  it('skips empty array directives', () => {
    const header = buildCSPHeader({ 'media-src': [] });
    expect(header).not.toContain('media-src');
  });

  it('includes nonce in script-src when built with nonce', () => {
    const nonce = 'abc123';
    const header = getCSPHeader(nonce);
    expect(header).toContain(`'nonce-${nonce}'`);
  });
});

describe('csp-config — getCSPConfig', () => {
  it('returns an object with directives and reportOnly', () => {
    const config = getCSPConfig();
    expect(config).toHaveProperty('directives');
    expect(config).toHaveProperty('reportOnly');
  });

  it('directives contain default-src', () => {
    const config = getCSPConfig();
    expect(config.directives['default-src']).toBeDefined();
  });

  it('passes nonce through to directives', () => {
    const nonce = 'my-nonce';
    const config = getCSPConfig(nonce);
    expect(config.directives['script-src']).toContain(`'nonce-${nonce}'`);
  });
});

describe('csp-config — getCSPHeaderName', () => {
  it('returns Content-Security-Policy by default', () => {
    expect(getCSPHeaderName()).toBe('Content-Security-Policy');
  });

  it('returns Content-Security-Policy when reportOnly is false', () => {
    expect(getCSPHeaderName(false)).toBe('Content-Security-Policy');
  });

  it('returns Content-Security-Policy-Report-Only when reportOnly is true', () => {
    expect(getCSPHeaderName(true)).toBe('Content-Security-Policy-Report-Only');
  });
});

describe('csp-config — CSP violation report validation', () => {
  it('returns true for valid report', () => {
    const report = {
      'csp-report': {
        'document-uri': 'https://example.com',
        'violated-directive': 'script-src',
        'effective-directive': 'script-src',
        'original-policy': "default-src 'self'",
        'blocked-uri': 'https://evil.com/script.js',
        'status-code': 200,
      },
    };
    expect(isValidCSPReport(report)).toBe(true);
  });

  it('returns false for null', () => {
    expect(isValidCSPReport(null)).toBe(false);
  });

  it('returns false for non-object', () => {
    expect(isValidCSPReport('string')).toBe(false);
    expect(isValidCSPReport(42)).toBe(false);
  });

  it('returns false when csp-report key is missing', () => {
    expect(isValidCSPReport({ other: 'data' })).toBe(false);
  });

  it('returns false when required fields are missing', () => {
    expect(
      isValidCSPReport({
        'csp-report': {
          'document-uri': 'https://example.com',
          // missing violated-directive and blocked-uri
        },
      })
    ).toBe(false);
  });

  it('returns false when csp-report is not an object', () => {
    expect(isValidCSPReport({ 'csp-report': 'string' })).toBe(false);
  });
});

describe('csp-config — sanitizeCSPReport', () => {
  it('maps violation fields to camelCase properties', () => {
    const report = {
      'document-uri': 'https://example.com/page',
      'violated-directive': 'script-src',
      'effective-directive': 'script-src',
      'original-policy': "default-src 'self'",
      'blocked-uri': 'https://evil.com/bad.js',
      'status-code': 200,
      'source-file': 'https://example.com/app.js',
      'line-number': 42,
      'column-number': 10,
    };

    const sanitized = sanitizeCSPReport(report);

    expect(sanitized.documentUri).toBe('https://example.com/page');
    expect(sanitized.violatedDirective).toBe('script-src');
    expect(sanitized.effectiveDirective).toBe('script-src');
    expect(sanitized.blockedUri).toBe('https://evil.com/bad.js');
    expect(sanitized.statusCode).toBe(200);
    expect(sanitized.sourceFile).toBe('https://example.com/app.js');
    expect(sanitized.lineNumber).toBe(42);
    expect(sanitized.columnNumber).toBe(10);
  });

  it('includes a timestamp', () => {
    const report = {
      'document-uri': 'https://example.com',
      'violated-directive': 'script-src',
      'effective-directive': 'script-src',
      'original-policy': '',
      'blocked-uri': '',
      'status-code': 0,
    };

    const sanitized = sanitizeCSPReport(report);
    expect(sanitized.timestamp).toBeDefined();
    expect(typeof sanitized.timestamp).toBe('string');
    // Should be ISO format
    expect(new Date(sanitized.timestamp as string).toISOString()).toBe(sanitized.timestamp);
  });
});

describe('csp-config — CSP namespace export', () => {
  it('CSP.generateNonce is the same as generateNonce', () => {
    expect(CSP.generateNonce).toBe(generateNonce);
  });

  it('CSP.getDirectives is the same as getCSPDirectives', () => {
    expect(CSP.getDirectives).toBe(getCSPDirectives);
  });

  it('CSP.buildHeader is the same as buildCSPHeader', () => {
    expect(CSP.buildHeader).toBe(buildCSPHeader);
  });

  it('CSP.getConfig is the same as getCSPConfig', () => {
    expect(CSP.getConfig).toBe(getCSPConfig);
  });

  it('CSP.getHeader is the same as getCSPHeader', () => {
    expect(CSP.getHeader).toBe(getCSPHeader);
  });

  it('CSP.getHeaderName is the same as getCSPHeaderName', () => {
    expect(CSP.getHeaderName).toBe(getCSPHeaderName);
  });

  it('CSP.isValidReport is the same as isValidCSPReport', () => {
    expect(CSP.isValidReport).toBe(isValidCSPReport);
  });

  it('CSP.sanitizeReport is the same as sanitizeCSPReport', () => {
    expect(CSP.sanitizeReport).toBe(sanitizeCSPReport);
  });
});
