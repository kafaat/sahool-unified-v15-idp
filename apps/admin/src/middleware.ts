/**
 * SAHOOL Admin Authentication Middleware
 * ميدل وير التوثيق للوحة الإدارة
 *
 * Protects all routes except /login
 * يحمي جميع المسارات ما عدا /login
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import {
  generateNonce,
  getCSPHeader,
  getCSPHeaderName,
  getCSPConfig,
} from '@/lib/security/csp-config';

// Routes that don't require authentication
const publicRoutes = ['/login', '/api/auth'];

// Idle timeout: 30 minutes in milliseconds
const IDLE_TIMEOUT = 30 * 60 * 1000;

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes
  if (publicRoutes.some((route) => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Allow static files and Next.js internals
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.includes('.') // files with extensions
  ) {
    return NextResponse.next();
  }

  // Check for auth token
  const token = request.cookies.get('sahool_admin_token')?.value;

  if (!token) {
    // Redirect to login with return URL
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Check for idle timeout
  const lastActivityStr = request.cookies.get('sahool_admin_last_activity')?.value;
  if (lastActivityStr) {
    const lastActivity = parseInt(lastActivityStr, 10);
    const now = Date.now();
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

  // Token exists - add security headers
  const response = NextResponse.next();

  // Generate nonce for CSP
  const nonce = generateNonce();

  // Store nonce in response headers for use in HTML
  response.headers.set('X-Nonce', nonce);

  // Add security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('X-XSS-Protection', '1; mode=block');

  // HSTS - only in production with HTTPS
  if (process.env.NODE_ENV === 'production') {
    response.headers.set(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains'
    );
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
