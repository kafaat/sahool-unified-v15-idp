/**
 * SAHOOL Admin Authentication & Authorization Middleware
 * ميدل وير التوثيق والترخيص للوحة الإدارة
 *
 * Protects all routes with authentication + role-based authorization
 * يحمي جميع المسارات بالتوثيق + الترخيص القائم على الأدوار
 *
 * Security Features:
 * - JWT token validation
 * - Server-side role verification
 * - Idle timeout (30 minutes)
 * - Security headers (CSP, HSTS, etc.)
 * - 403 Forbidden for unauthorized access
 *
 * Edge Bundle Optimization:
 * - Logger is edge-safe console-only (no @sentry/nextjs import ~300KB+)
 * - JWT verification uses jose directly (no @/lib/auth barrel import)
 * - Route protection is imported directly (no barrel re-exports)
 * - CSP & CSRF modules are edge-native (Web Crypto API)
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import {
  generateNonce,
  getCSPHeader,
  getCSPHeaderName,
  getCSPConfig,
} from '@/lib/security/csp-config';
import { validateCsrfRequest, generateCsrfToken } from '@/lib/security/csrf-server';
// ---------------------------------------------------------------------------
// Import jwt-verify directly — NOT through @/lib/auth barrel.
// The barrel re-exports api-middleware.ts which imports @/lib/logger which
// references @sentry/nextjs (~300KB). Importing the leaf module avoids this.
// ---------------------------------------------------------------------------
import { verifyToken, isTokenExpired } from '@/lib/auth/jwt-verify';
// ---------------------------------------------------------------------------
// route-protection.ts is a pure module with no heavy transitive deps.
// ---------------------------------------------------------------------------
import {
  isPublicRoute,
  getRequiredRoles,
  hasRouteAccess,
  getUnauthorizedRedirect,
} from '@/lib/auth/route-protection';

// ---------------------------------------------------------------------------
// Edge-safe logger — avoids importing @/lib/logger which references
// @sentry/nextjs (~300KB). In the edge middleware we only need console output.
// ---------------------------------------------------------------------------
const edgeLogger = {
  /** Security-critical errors — always logged (all environments). */
  error: (...args: unknown[]) => {
    // Always log in production for security-relevant events (token forgery,
    // CSRF attacks, etc.).  In development we use console.error so stack
    // traces show up in the terminal unchanged.
    if (process.env.NODE_ENV === 'development') {
      console.error('[admin-middleware]', ...args);
    } else {
      const details = args.slice(1).map((a) =>
        a instanceof Error ? { error: a.message, stack: a.stack } : a
      );
      console.error(
        JSON.stringify({
          level: 'error',
          service: 'sahool-admin-middleware',
          timestamp: new Date().toISOString(),
          message: args[0] instanceof Error ? args[0].message : String(args[0]),
          ...(args[0] instanceof Error && args[0].stack ? { stack: args[0].stack } : {}),
          ...(details.length > 0 ? { details } : {}),
        })
      );
    }
  },
  warn: (...args: unknown[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.warn('[admin-middleware]', ...args);
    }
  },
};

// Idle timeout: 30 minutes in milliseconds
const IDLE_TIMEOUT = 30 * 60 * 1000;

// Development mode bypass - DISABLED by default for security
// To enable: set ENABLE_AUTH_BYPASS=true explicitly (NEVER in production)
const isDevelopment = process.env.NODE_ENV === 'development';
const ENABLE_DEV_BYPASS = isDevelopment && process.env.ENABLE_AUTH_BYPASS === 'true';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow static files and Next.js internals
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    /\.\w{2,5}$/.test(pathname) // files with extensions (e.g. .js, .css, .png)
  ) {
    return NextResponse.next();
  }

  // Allow public routes (login, health check, etc.)
  if (isPublicRoute(pathname)) {
    return NextResponse.next();
  }

  // Development mode bypass - skip auth for easier local development
  if (ENABLE_DEV_BYPASS) {
    // Generate nonce for CSP
    const nonce = generateNonce();
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('X-Nonce', nonce);

    const response = NextResponse.next({
      request: { headers: requestHeaders },
    });

    // Set mock user role for development
    response.headers.set('X-Nonce', nonce);
    response.headers.set('X-User-Role', 'admin');

    // Add CSP header
    const cspConfig = getCSPConfig(nonce);
    const cspHeader = getCSPHeader(nonce);
    const cspHeaderName = getCSPHeaderName(cspConfig.reportOnly);
    response.headers.set(cspHeaderName, cspHeader);

    return response;
  }

  // ============================================
  // AUTHENTICATION CHECK
  // ============================================
  const token = request.cookies.get('sahool_admin_token')?.value;

  if (!token) {
    // No token - redirect to login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Quick check for expired token (without full verification)
  if (isTokenExpired(token)) {
    // Token expired - clear cookies and redirect
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    loginUrl.searchParams.set('reason', 'token_expired');

    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('sahool_admin_token');
    response.cookies.delete('sahool_admin_refresh_token');
    response.cookies.delete('sahool_admin_last_activity');

    return response;
  }

  // ============================================
  // JWT TOKEN VERIFICATION
  // ============================================
  let userRole: 'admin' | 'supervisor' | 'viewer';

  try {
    // Verify JWT signature and extract role
    const payload = await verifyToken(token);

    // FIXED: Backend sends "roles" (array), not "role" (singular)
    // Extract role from roles array or fallback to role field for backward compatibility
    let extractedRole: string;
    if (payload.roles && Array.isArray(payload.roles) && payload.roles.length > 0) {
      extractedRole = payload.roles[0] ?? 'viewer';
    } else if (payload.role) {
      extractedRole = payload.role;
    } else {
      extractedRole = 'viewer'; // Default fallback
    }

    // Normalize role to lowercase and map to admin panel roles
    const normalizedRole = extractedRole.toLowerCase();
    if (normalizedRole === 'admin' || normalizedRole === 'administrator') {
      userRole = 'admin';
    } else if (normalizedRole === 'supervisor' || normalizedRole === 'manager') {
      userRole = 'supervisor';
    } else {
      userRole = 'viewer'; // Default for farmer, viewer, or any other role
    }
  } catch (error) {
    // Token verification failed — log the original error object so stack traces
    // are preserved in dev tools, then also surface the extracted reason and
    // any attached cause for quick diagnosis.
    const reason = error instanceof Error ? error.message : String(error);
    const cause = error instanceof Error && (error as { cause?: unknown }).cause;
    edgeLogger.error(
      'Token verification failed:',
      error,
      'reason:',
      reason,
      ...(cause ? ['cause:', cause] : [])
    );

    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    loginUrl.searchParams.set('reason', 'invalid_token');

    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('sahool_admin_token');
    response.cookies.delete('sahool_admin_refresh_token');
    response.cookies.delete('sahool_admin_last_activity');

    return response;
  }

  // ============================================
  // ROLE-BASED AUTHORIZATION CHECK
  // ============================================
  const requiredRoles = getRequiredRoles(pathname);

  if (requiredRoles && !hasRouteAccess(pathname, userRole)) {
    // User doesn't have required role - return 403 Forbidden
    // For API routes, return JSON error
    if (pathname.startsWith('/api/')) {
      return NextResponse.json(
        {
          error: 'Forbidden',
          message: 'You do not have permission to access this resource',
          required_roles: requiredRoles,
          your_role: userRole,
        },
        { status: 403 }
      );
    }

    // For page routes, redirect to dashboard with error
    const unauthorizedUrl = new URL(getUnauthorizedRedirect(userRole), request.url);
    unauthorizedUrl.searchParams.set('error', 'unauthorized');
    unauthorizedUrl.searchParams.set('attempted_route', pathname);

    return NextResponse.redirect(unauthorizedUrl);
  }

  // ============================================
  // CSRF VALIDATION (for state-changing requests)
  // ============================================
  const csrfValidation = validateCsrfRequest(request);
  if (!csrfValidation.valid) {
    // For API routes, return JSON error
    if (pathname.startsWith('/api/')) {
      return NextResponse.json(
        {
          error: 'CSRF validation failed',
          message: csrfValidation.error,
        },
        { status: 403 }
      );
    }

    // For page routes, redirect to login with error
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('error', 'csrf_failed');
    return NextResponse.redirect(loginUrl);
  }

  // ============================================
  // IDLE TIMEOUT CHECK
  // ============================================
  const lastActivityStr = request.cookies.get('sahool_admin_last_activity')?.value;
  if (lastActivityStr) {
    const lastActivity = parseInt(lastActivityStr, 10);
    const now = Date.now();
    // Guard against NaN from corrupted/tampered cookies - treat as expired
    if (Number.isNaN(lastActivity)) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('returnTo', pathname);
      loginUrl.searchParams.set('reason', 'session_expired');
      const expiredResponse = NextResponse.redirect(loginUrl);
      expiredResponse.cookies.delete('sahool_admin_token');
      expiredResponse.cookies.delete('sahool_admin_refresh_token');
      expiredResponse.cookies.delete('sahool_admin_last_activity');
      return expiredResponse;
    }
    const timeSinceLastActivity = now - lastActivity;

    if (timeSinceLastActivity >= IDLE_TIMEOUT) {
      // Session expired due to inactivity - clear cookies and redirect
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('returnTo', pathname);
      loginUrl.searchParams.set('reason', 'session_expired');

      const response = NextResponse.redirect(loginUrl);
      response.cookies.delete('sahool_admin_token');
      response.cookies.delete('sahool_admin_refresh_token');
      response.cookies.delete('sahool_admin_last_activity');

      return response;
    }
  }

  // ============================================
  // SECURITY HEADERS
  // ============================================

  // Generate nonce for CSP
  const nonce = generateNonce();

  // Create new request headers with nonce and role for server-side code
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('X-Nonce', nonce);
  requestHeaders.set('X-User-Role', userRole);

  const response = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });

  // ============================================
  // CSRF TOKEN GENERATION
  // ============================================
  let csrfToken = request.cookies.get('sahool_admin_csrf')?.value;
  if (!csrfToken) {
    csrfToken = generateCsrfToken();
    response.cookies.set('sahool_admin_csrf', csrfToken, {
      httpOnly: false, // Must be readable by JavaScript for AJAX requests
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      path: '/',
      maxAge: 60 * 60 * 24, // 24 hours
    });
  }

  // Update last activity timestamp for idle timeout (sliding session)
  response.cookies.set('sahool_admin_last_activity', String(Date.now()), {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    path: '/',
    maxAge: 60 * 60 * 24, // 24 hours
  });

  // Store nonce in response headers for use in HTML
  response.headers.set('X-Nonce', nonce);

  // Add security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('X-XSS-Protection', '1; mode=block');

  // HSTS - only in production with HTTPS
  if (process.env.NODE_ENV === 'production') {
    response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  }

  // Content Security Policy with nonce-based security
  const cspConfig = getCSPConfig(nonce);
  const cspHeader = getCSPHeader(nonce);
  const cspHeaderName = getCSPHeaderName(cspConfig.reportOnly);

  response.headers.set(cspHeaderName, cspHeader);

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
};
