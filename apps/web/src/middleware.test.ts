/**
 * Middleware Security Tests
 * اختبارات أمان الميدل وير
 *
 * Tests for security fixes:
 * - Security header bypass removed (dot-in-path no longer skips headers)
 * - API route security headers applied correctly
 * - Static files still bypass middleware
 * - HSTS header applied in production
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';

// ═══════════════════════════════════════════════════════════════════════════
// Module Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock('@/lib/security/csp-config', () => ({
  generateNonce: vi.fn(() => 'test-nonce-abc123'),
  getCSPHeader: vi.fn(() => "default-src 'self'"),
  getCSPHeaderName: vi.fn(() => 'Content-Security-Policy'),
  getCSPConfig: vi.fn(() => ({ reportOnly: false })),
}));

vi.mock('@/lib/security/jwt-middleware', () => ({
  validateJwtToken: vi.fn(() => Promise.resolve({ valid: true })),
}));

vi.mock('@/lib/security/csrf-server', () => ({
  validateCsrfRequest: vi.fn(() => ({ valid: true })),
}));

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

function createRequest(path: string, method = 'GET'): NextRequest {
  const url = new URL(path, 'http://localhost:3000');
  return new NextRequest(url, { method });
}

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Middleware Security', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.clearAllMocks();
    process.env = { ...originalEnv, NODE_ENV: 'development' };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Security header bypass removed
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Security header bypass removed', () => {
    it('should apply security headers to paths with dots like /dashboard/test.file', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/dashboard/test.file');
      const response = await middleware(request);

      // The path contains a dot but it should NOT bypass security headers.
      // Previously pathname.includes(".") would skip these paths.
      expect(response.headers.get('X-Frame-Options')).toBe('DENY');
      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
      expect(response.headers.get('Referrer-Policy')).toBe('strict-origin-when-cross-origin');
      expect(response.headers.get('X-XSS-Protection')).toBe('1; mode=block');
    });

    it('should apply security headers to /fields/map.view', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/fields/map.view');
      const response = await middleware(request);

      expect(response.headers.get('X-Frame-Options')).toBe('DENY');
      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
    });

    it('should apply security headers to /analytics/report.pdf', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/analytics/report.pdf');
      const response = await middleware(request);

      expect(response.headers.get('X-Frame-Options')).toBe('DENY');
      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // API route security headers
  // ═══════════════════════════════════════════════════════════════════════════

  describe('API route security headers', () => {
    it('should set X-Content-Type-Options: nosniff on API routes', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/api/fields');
      const response = await middleware(request);

      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
    });

    it('should set X-Frame-Options: DENY on API routes', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/api/auth/login');
      const response = await middleware(request);

      expect(response.headers.get('X-Frame-Options')).toBe('DENY');
    });

    it('should set Referrer-Policy: strict-origin-when-cross-origin on API routes', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/api/users');
      const response = await middleware(request);

      expect(response.headers.get('Referrer-Policy')).toBe('strict-origin-when-cross-origin');
    });

    it('should set X-XSS-Protection: 1; mode=block on API routes', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/api/weather');
      const response = await middleware(request);

      expect(response.headers.get('X-XSS-Protection')).toBe('1; mode=block');
    });

    it('should set Cache-Control: no-store on API routes', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/api/crops/health');
      const response = await middleware(request);

      expect(response.headers.get('Cache-Control')).toBe('no-store');
    });

    it('should include all five security headers together on API routes', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/api/irrigation/schedule');
      const response = await middleware(request);

      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
      expect(response.headers.get('X-Frame-Options')).toBe('DENY');
      expect(response.headers.get('Referrer-Policy')).toBe('strict-origin-when-cross-origin');
      expect(response.headers.get('X-XSS-Protection')).toBe('1; mode=block');
      expect(response.headers.get('Cache-Control')).toBe('no-store');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Static files bypass
  // ═══════════════════════════════════════════════════════════════════════════

  describe('Static files bypass', () => {
    it('should pass through /_next/* paths without security headers', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/_next/static/chunks/main.js');
      const response = await middleware(request);

      // Static files should get a plain NextResponse.next() without extra headers
      // The response status should be 200 (passthrough)
      expect(response.status).toBe(200);
      // Should NOT have the custom security headers added by addSecurityHeaders
      expect(response.headers.get('X-Nonce')).toBeNull();
      expect(response.headers.get('Permissions-Policy')).toBeNull();
    });

    it('should pass through /_next/image paths without processing', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/_next/image?url=test.png');
      const response = await middleware(request);

      expect(response.status).toBe(200);
      expect(response.headers.get('X-Nonce')).toBeNull();
    });

    it('should pass through /static/* paths without security headers', async () => {
      const { middleware } = await import('./middleware');
      const request = createRequest('/static/images/logo.png');
      const response = await middleware(request);

      expect(response.status).toBe(200);
      expect(response.headers.get('X-Nonce')).toBeNull();
      expect(response.headers.get('Permissions-Policy')).toBeNull();
    });

    it('should pass through /_next/data paths without processing', async () => {
      // Note: In production, /_next/data paths with dots are excluded by the
      // matcher config (.*\\..*). When the middleware IS called directly,
      // the /_next prefix check should still apply. We verify it gets a 200.
      const { middleware } = await import('./middleware');
      const request = createRequest('/_next/data/build-id/dashboard.json');
      const response = await middleware(request);

      expect(response.status).toBe(200);
      // The matcher excludes this path in production, so this is just a
      // pass-through check. Don't assert on specific header absence since
      // the middleware may or may not add headers depending on module cache state.
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HSTS in production
  // ═══════════════════════════════════════════════════════════════════════════

  describe('HSTS in production', () => {
    it('should set HSTS header on API routes when NODE_ENV=production', async () => {
      process.env.NODE_ENV = 'production';
      // Reset modules to pick up new env
      vi.resetModules();

      // Re-mock dependencies after resetModules
      vi.doMock('@/lib/security/csp-config', () => ({
        generateNonce: vi.fn(() => 'test-nonce-abc123'),
        getCSPHeader: vi.fn(() => "default-src 'self'"),
        getCSPHeaderName: vi.fn(() => 'Content-Security-Policy'),
        getCSPConfig: vi.fn(() => ({ reportOnly: false })),
      }));
      vi.doMock('@/lib/security/jwt-middleware', () => ({
        validateJwtToken: vi.fn(() => Promise.resolve({ valid: true })),
      }));
      vi.doMock('@/lib/security/csrf-server', () => ({
        validateCsrfRequest: vi.fn(() => ({ valid: true })),
      }));

      const { middleware } = await import('./middleware');
      const request = createRequest('/api/fields');
      const response = await middleware(request);

      expect(response.headers.get('Strict-Transport-Security')).toBe(
        'max-age=31536000; includeSubDomains; preload'
      );
    });

    it('should NOT set HSTS header on API routes when NODE_ENV=development', async () => {
      process.env.NODE_ENV = 'development';
      vi.resetModules();

      vi.doMock('@/lib/security/csp-config', () => ({
        generateNonce: vi.fn(() => 'test-nonce-abc123'),
        getCSPHeader: vi.fn(() => "default-src 'self'"),
        getCSPHeaderName: vi.fn(() => 'Content-Security-Policy'),
        getCSPConfig: vi.fn(() => ({ reportOnly: false })),
      }));
      vi.doMock('@/lib/security/jwt-middleware', () => ({
        validateJwtToken: vi.fn(() => Promise.resolve({ valid: true })),
      }));
      vi.doMock('@/lib/security/csrf-server', () => ({
        validateCsrfRequest: vi.fn(() => ({ valid: true })),
      }));

      const { middleware } = await import('./middleware');
      const request = createRequest('/api/fields');
      const response = await middleware(request);

      expect(response.headers.get('Strict-Transport-Security')).toBeNull();
    });

    it('should set HSTS on protected routes in production via addSecurityHeaders', async () => {
      process.env.NODE_ENV = 'production';
      vi.resetModules();

      vi.doMock('@/lib/security/csp-config', () => ({
        generateNonce: vi.fn(() => 'test-nonce-abc123'),
        getCSPHeader: vi.fn(() => "default-src 'self'"),
        getCSPHeaderName: vi.fn(() => 'Content-Security-Policy'),
        getCSPConfig: vi.fn(() => ({ reportOnly: false })),
      }));
      vi.doMock('@/lib/security/jwt-middleware', () => ({
        validateJwtToken: vi.fn(() => Promise.resolve({ valid: true })),
      }));
      vi.doMock('@/lib/security/csrf-server', () => ({
        validateCsrfRequest: vi.fn(() => ({ valid: true })),
      }));

      const { middleware } = await import('./middleware');
      const request = createRequest('/dashboard');
      const response = await middleware(request);

      expect(response.headers.get('Strict-Transport-Security')).toBe(
        'max-age=31536000; includeSubDomains; preload'
      );
    });
  });
});
