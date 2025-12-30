/**
 * SAHOOL Admin Authentication Middleware
 * ميدل وير التوثيق للوحة الإدارة
 *
 * Protects all routes except /login with JWT verification
 * يحمي جميع المسارات ما عدا /login مع التحقق من JWT
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { jwtVerify } from 'jose';

// Routes that don't require authentication
const publicRoutes = ['/login', '/api/auth'];

/**
 * Generate a cryptographically secure nonce for CSP
 * Uses Web Crypto API which is available in Edge Runtime
 */
function generateNonce(): string {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array));
}

/**
 * Build Content Security Policy based on environment
 */
function buildCSP(nonce: string, isDevelopment: boolean): string {
  const scriptSrc = isDevelopment
    ? `'self' 'nonce-${nonce}' 'unsafe-eval'` // unsafe-eval needed for Next.js hot reload in dev
    : `'self' 'nonce-${nonce}'`; // Strict policy for production

  const styleSrc = isDevelopment
    ? `'self' 'nonce-${nonce}' 'unsafe-inline' https://fonts.googleapis.com` // unsafe-inline for dev convenience
    : `'self' 'nonce-${nonce}' https://fonts.googleapis.com`; // Use nonces in production

  const connectSrc = isDevelopment
    ? `'self' http://localhost:* ws://localhost:* wss://localhost:*`
    : `'self' wss: https:`;

  // Build CSP directives
  const directives = [
    `default-src 'self'`,
    `script-src ${scriptSrc}`,
    `style-src ${styleSrc}`,
    `img-src 'self' data: https: blob:`,
    `font-src 'self' https://fonts.gstatic.com`,
    `connect-src ${connectSrc}`,
    `frame-ancestors 'none'`,
    `base-uri 'self'`,
    `form-action 'self'`,
    `object-src 'none'`,
    `upgrade-insecure-requests`,
  ];

  // Add CSP reporting endpoint for production
  if (!isDevelopment) {
    directives.push(`report-uri /api/csp-report`);
    directives.push(`report-to csp-endpoint`);
  }

  return directives.join('; ') + ';';
}

/**
 * Verify JWT token using jose library (edge-compatible)
 */
async function verifyToken(token: string): Promise<boolean> {
  try {
    // Get JWT secret from environment
    const secret = process.env.JWT_SECRET_KEY || process.env.JWT_SECRET;

    if (!secret) {
      console.error('❌ JWT_SECRET_KEY or JWT_SECRET not configured');
      return false;
    }

    // Convert secret to Uint8Array for jose
    const secretKey = new TextEncoder().encode(secret);

    // Get JWT configuration from environment
    const issuer = process.env.JWT_ISSUER || 'sahool-platform';
    const audience = process.env.JWT_AUDIENCE || 'sahool-api';

    // Verify JWT token with jose
    const { payload } = await jwtVerify(token, secretKey, {
      issuer,
      audience,
      algorithms: ['HS256'], // Only allow HS256 for security
    });

    // Additional validation: Check if user has admin role
    if (payload.role && typeof payload.role === 'string') {
      const validAdminRoles = ['admin', 'supervisor', 'viewer'];
      if (!validAdminRoles.includes(payload.role)) {
        console.warn('⚠️ Invalid admin role in token:', payload.role);
        return false;
      }
    }

    return true;
  } catch (error) {
    // Log specific error types for debugging
    if (error instanceof Error) {
      if (error.message.includes('expired')) {
        console.warn('⚠️ JWT token expired');
      } else if (error.message.includes('signature')) {
        console.error('❌ JWT signature verification failed');
      } else {
        console.error('❌ JWT verification error:', error.message);
      }
    }
    return false;
  }
}

/**
 * Add security headers to response
 * CRITICAL: These headers MUST be added to ALL responses including login page and errors
 */
function addSecurityHeaders(response: NextResponse): NextResponse {
  // Detect environment
  const isDevelopment = process.env.NODE_ENV === 'development';

  // Generate nonce for inline scripts and styles
  const nonce = generateNonce();

  // Add security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');

  // Add CSP nonce to response headers for use in components
  response.headers.set('X-CSP-Nonce', nonce);

  // Content Security Policy - Environment-aware
  response.headers.set('Content-Security-Policy', buildCSP(nonce, isDevelopment));

  // Add Report-To header for CSP reporting (only in production)
  if (!isDevelopment) {
    response.headers.set(
      'Report-To',
      JSON.stringify({
        group: 'csp-endpoint',
        max_age: 10886400,
        endpoints: [{ url: '/api/csp-report' }],
      })
    );
  }

  // HSTS - only in production with HTTPS
  if (process.env.NODE_ENV === 'production') {
    response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  }

  return response;
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes with security headers
  if (publicRoutes.some((route) => pathname.startsWith(route))) {
    const response = NextResponse.next();
    return addSecurityHeaders(response);
  }

  // Allow static files and Next.js internals without security headers (they have their own)
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
    // Redirect to login with return URL - add security headers to redirect
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    const response = NextResponse.redirect(loginUrl);
    return addSecurityHeaders(response);
  }

  // CRITICAL: Verify JWT token signature and claims
  const isValid = await verifyToken(token);

  if (!isValid) {
    // Token is invalid or expired - redirect to login with security headers
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    loginUrl.searchParams.set('reason', 'session_expired');

    // Clear invalid token
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('sahool_admin_token');

    return addSecurityHeaders(response);
  }

  // Token is valid - continue with security headers
  const response = NextResponse.next();
  return addSecurityHeaders(response);
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
