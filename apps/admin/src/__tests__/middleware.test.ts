/**
 * Middleware Tests
 * اختبارات ميدل وير التوثيق والأمان
 *
 * Tests middleware.ts: structure, exports, JWT checks, public routes,
 * security headers, CSRF validation, idle timeout, matcher config
 */

import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

const MIDDLEWARE_PATH = path.resolve(__dirname, '../middleware.ts');
const middlewareSource = fs.readFileSync(MIDDLEWARE_PATH, 'utf-8');

describe('middleware.ts — file structure', () => {
  it('file exists and is non-empty', () => {
    expect(middlewareSource.length).toBeGreaterThan(0);
  });

  it('exports an async middleware function', () => {
    expect(middlewareSource).toMatch(/export\s+async\s+function\s+middleware\s*\(/);
  });

  it('exports a config object with matcher', () => {
    expect(middlewareSource).toMatch(/export\s+const\s+config\s*=/);
    expect(middlewareSource).toContain('matcher');
  });

  it('imports NextResponse and NextRequest from next/server', () => {
    expect(middlewareSource).toContain("from 'next/server'");
    expect(middlewareSource).toContain('NextResponse');
    expect(middlewareSource).toContain('NextRequest');
  });
});

describe('middleware.ts — JWT token checks', () => {
  it('reads token from sahool_admin_token cookie', () => {
    expect(middlewareSource).toContain("sahool_admin_token");
    expect(middlewareSource).toMatch(/request\.cookies\.get\(['"]sahool_admin_token['"]\)/);
  });

  it('imports verifyToken for JWT signature verification', () => {
    expect(middlewareSource).toContain('verifyToken');
    expect(middlewareSource).toMatch(/import\s*\{[^}]*verifyToken[^}]*\}\s*from/);
  });

  it('imports isTokenExpired for quick expiry check', () => {
    expect(middlewareSource).toContain('isTokenExpired');
  });

  it('calls verifyToken to verify JWT payload', () => {
    expect(middlewareSource).toMatch(/await\s+verifyToken\s*\(\s*token\s*\)/);
  });

  it('calls isTokenExpired for fast expiry detection', () => {
    expect(middlewareSource).toMatch(/isTokenExpired\s*\(\s*token\s*\)/);
  });

  it('redirects to /login when no token is present', () => {
    expect(middlewareSource).toContain("'/login'");
    // After no-token check, it builds a redirect URL
    expect(middlewareSource).toMatch(/if\s*\(\s*!token\s*\)/);
  });

  it('sets returnTo query param on login redirect', () => {
    expect(middlewareSource).toContain("'returnTo'");
    expect(middlewareSource).toContain('pathname');
  });

  it('clears auth cookies on expired token', () => {
    expect(middlewareSource).toContain("response.cookies.delete('sahool_admin_token')");
    expect(middlewareSource).toContain("response.cookies.delete('sahool_admin_refresh_token')");
    expect(middlewareSource).toContain("response.cookies.delete('sahool_admin_last_activity')");
  });

  it('sets reason=token_expired on expiry redirect', () => {
    expect(middlewareSource).toContain("'token_expired'");
  });

  it('sets reason=invalid_token when verification fails', () => {
    expect(middlewareSource).toContain("'invalid_token'");
  });

  it('handles token with roles array (backend format)', () => {
    expect(middlewareSource).toContain('payload.roles');
    expect(middlewareSource).toContain('Array.isArray(payload.roles)');
  });

  it('handles singular role field for backward compatibility', () => {
    expect(middlewareSource).toContain('payload.role');
  });

  it('normalizes role strings to lowercase', () => {
    expect(middlewareSource).toContain('.toLowerCase()');
  });

  it('maps administrator to admin role', () => {
    expect(middlewareSource).toContain("'administrator'");
  });

  it('maps manager to supervisor role', () => {
    expect(middlewareSource).toContain("'manager'");
  });

  it('defaults unknown roles to viewer', () => {
    // The default fallback assignment
    expect(middlewareSource).toContain("userRole = 'viewer'");
  });
});

describe('middleware.ts — public routes', () => {
  it('imports isPublicRoute from route-protection', () => {
    expect(middlewareSource).toContain('isPublicRoute');
    expect(middlewareSource).toMatch(/import\s*\{[^}]*isPublicRoute[^}]*\}\s*from/);
  });

  it('calls isPublicRoute(pathname) and returns NextResponse.next()', () => {
    expect(middlewareSource).toMatch(/isPublicRoute\s*\(\s*pathname\s*\)/);
    // The block that handles public routes calls NextResponse.next()
    expect(middlewareSource).toContain('NextResponse.next()');
  });

  it('skips auth for _next paths', () => {
    expect(middlewareSource).toContain("'/_next'");
    expect(middlewareSource).toMatch(/pathname\.startsWith\s*\(\s*'\/_next'\s*\)/);
  });

  it('skips auth for static file paths', () => {
    expect(middlewareSource).toContain("'/static'");
  });

  it('skips auth for files with extensions (.js, .css, .png)', () => {
    // Regex pattern for file extensions
    expect(middlewareSource).toMatch(/\\\.\\w\{2,5\}\$/);
  });
});

describe('middleware.ts — security headers', () => {
  it('sets X-Frame-Options to DENY', () => {
    expect(middlewareSource).toContain("'X-Frame-Options'");
    expect(middlewareSource).toContain("'DENY'");
  });

  it('sets X-Content-Type-Options to nosniff', () => {
    expect(middlewareSource).toContain("'X-Content-Type-Options'");
    expect(middlewareSource).toContain("'nosniff'");
  });

  it('sets Referrer-Policy header', () => {
    expect(middlewareSource).toContain("'Referrer-Policy'");
    expect(middlewareSource).toContain("'strict-origin-when-cross-origin'");
  });

  it('does NOT set deprecated X-XSS-Protection header', () => {
    // X-XSS-Protection was deprecated (MDN, 2020+) and removed in favor of CSP + nonce.
    // https://developer.mozilla.org/docs/Web/HTTP/Headers/X-XSS-Protection
    expect(middlewareSource).not.toContain("'X-XSS-Protection'");
  });

  it('sets HSTS in production only', () => {
    expect(middlewareSource).toContain("'Strict-Transport-Security'");
    expect(middlewareSource).toContain("'max-age=31536000; includeSubDomains'");
    // Conditional on production
    expect(middlewareSource).toMatch(/process\.env\.NODE_ENV\s*===\s*['"]production['"]/);
  });

  it('generates CSP nonce via generateNonce()', () => {
    expect(middlewareSource).toContain('generateNonce');
    expect(middlewareSource).toMatch(/const\s+nonce\s*=\s*generateNonce\s*\(\s*\)/);
  });

  it('sets CSP header via getCSPHeader and getCSPHeaderName', () => {
    expect(middlewareSource).toContain('getCSPHeader');
    expect(middlewareSource).toContain('getCSPHeaderName');
    expect(middlewareSource).toContain('getCSPConfig');
  });

  it('passes nonce in X-Nonce request and response headers', () => {
    expect(middlewareSource).toContain("'X-Nonce'");
    expect(middlewareSource).toMatch(/requestHeaders\.set\s*\(\s*'X-Nonce'\s*,\s*nonce\s*\)/);
    expect(middlewareSource).toMatch(/response\.headers\.set\s*\(\s*'X-Nonce'\s*,\s*nonce\s*\)/);
  });

  it('sets X-User-Role header for downstream components', () => {
    expect(middlewareSource).toContain("'X-User-Role'");
    expect(middlewareSource).toMatch(/requestHeaders\.set\s*\(\s*'X-User-Role'\s*,\s*userRole\s*\)/);
  });
});

describe('middleware.ts — CSRF validation', () => {
  it('imports validateCsrfRequest and generateCsrfToken', () => {
    expect(middlewareSource).toContain('validateCsrfRequest');
    expect(middlewareSource).toContain('generateCsrfToken');
  });

  it('calls validateCsrfRequest(request)', () => {
    expect(middlewareSource).toMatch(/validateCsrfRequest\s*\(\s*request\s*\)/);
  });

  it('checks csrfValidation.valid for pass/fail', () => {
    expect(middlewareSource).toContain('csrfValidation.valid');
  });

  it('returns 403 JSON for API routes on CSRF failure', () => {
    expect(middlewareSource).toContain("'CSRF validation failed'");
    expect(middlewareSource).toContain('status: 403');
  });

  it('redirects page routes to login on CSRF failure', () => {
    expect(middlewareSource).toContain("'csrf_failed'");
  });

  it('generates CSRF token cookie if not present', () => {
    expect(middlewareSource).toContain("'sahool_admin_csrf'");
    expect(middlewareSource).toMatch(/generateCsrfToken\s*\(\s*\)/);
  });

  it('sets CSRF cookie as non-httpOnly for JS access', () => {
    expect(middlewareSource).toContain('httpOnly: false');
  });

  it('sets CSRF cookie with sameSite strict', () => {
    expect(middlewareSource).toContain("sameSite: 'strict'");
  });
});

describe('middleware.ts — idle timeout tracking', () => {
  it('defines IDLE_TIMEOUT as 30 minutes (1800000 ms)', () => {
    expect(middlewareSource).toContain('IDLE_TIMEOUT');
    expect(middlewareSource).toContain('30 * 60 * 1000');
  });

  it('reads sahool_admin_last_activity cookie', () => {
    expect(middlewareSource).toContain("'sahool_admin_last_activity'");
    expect(middlewareSource).toMatch(/request\.cookies\.get\s*\(\s*'sahool_admin_last_activity'\s*\)/);
  });

  it('parses lastActivity as integer', () => {
    expect(middlewareSource).toContain('parseInt(lastActivityStr, 10)');
  });

  it('handles NaN from corrupted activity cookie', () => {
    expect(middlewareSource).toContain('Number.isNaN(lastActivity)');
  });

  it('compares elapsed time against IDLE_TIMEOUT', () => {
    expect(middlewareSource).toContain('timeSinceLastActivity');
    expect(middlewareSource).toMatch(/timeSinceLastActivity\s*>=\s*IDLE_TIMEOUT/);
  });

  it('redirects with reason=session_expired on timeout', () => {
    expect(middlewareSource).toContain("'session_expired'");
  });

  it('updates last_activity cookie on successful requests (sliding session)', () => {
    expect(middlewareSource).toContain("'sahool_admin_last_activity'");
    expect(middlewareSource).toContain('String(Date.now())');
  });
});

describe('middleware.ts — role-based authorization', () => {
  it('imports getRequiredRoles and hasRouteAccess', () => {
    expect(middlewareSource).toContain('getRequiredRoles');
    expect(middlewareSource).toContain('hasRouteAccess');
  });

  it('checks route access with hasRouteAccess(pathname, userRole)', () => {
    expect(middlewareSource).toMatch(/hasRouteAccess\s*\(\s*pathname\s*,\s*userRole\s*\)/);
  });

  it('returns 403 JSON for unauthorized API routes', () => {
    expect(middlewareSource).toContain("'Forbidden'");
    expect(middlewareSource).toContain('required_roles');
    expect(middlewareSource).toContain('your_role');
  });

  it('redirects page routes to getUnauthorizedRedirect on 403', () => {
    expect(middlewareSource).toContain('getUnauthorizedRedirect');
    expect(middlewareSource).toContain("'unauthorized'");
    expect(middlewareSource).toContain("'attempted_route'");
  });
});

describe('middleware.ts — matcher config', () => {
  it('excludes _next/static from matching', () => {
    expect(middlewareSource).toContain('_next/static');
  });

  it('excludes _next/image from matching', () => {
    expect(middlewareSource).toContain('_next/image');
  });

  it('excludes favicon.ico from matching', () => {
    expect(middlewareSource).toContain('favicon.ico');
  });

  it('excludes public folder from matching', () => {
    // The matcher regex uses a negative lookahead that includes 'public'
    expect(middlewareSource).toMatch(/public/);
  });

  it('uses negative lookahead regex pattern in matcher', () => {
    // The regex pattern: '/((?!_next/static|_next/image|favicon.ico|public).*)'
    expect(middlewareSource).toContain('(?!_next/static|_next/image|favicon.ico|public)');
  });
});

describe('middleware.ts — development bypass', () => {
  it('supports ENABLE_AUTH_BYPASS for local development', () => {
    expect(middlewareSource).toContain('ENABLE_AUTH_BYPASS');
    expect(middlewareSource).toContain('ENABLE_DEV_BYPASS');
  });

  it('only enables bypass when both development mode and env flag are set', () => {
    expect(middlewareSource).toMatch(/isDevelopment\s*&&\s*process\.env\.ENABLE_AUTH_BYPASS\s*===\s*'true'/);
  });

  it('sets mock admin role in development bypass', () => {
    expect(middlewareSource).toContain("'X-User-Role', 'admin'");
  });
});
