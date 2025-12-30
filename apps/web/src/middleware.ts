/**
 * SAHOOL Web Authentication Middleware
 * ميدل وير التوثيق لتطبيق الويب
 *
 * Protects dashboard routes with server-side authentication
 * يحمي مسارات لوحة التحكم بالتوثيق من جانب الخادم
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { jwtVerify } from 'jose';

// Routes that don't require authentication
const publicRoutes = [
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/api/auth',
  '/',
];

// Routes that require authentication
const protectedRoutes = [
  '/dashboard',
  '/fields',
  '/tasks',
  '/weather',
  '/analytics',
  '/settings',
  '/iot',
  '/equipment',
  '/wallet',
  '/community',
  '/marketplace',
  '/crop-health',
];

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
 * Verify JWT token using jose library (edge-compatible)
 * Returns true if valid, false otherwise
 */
async function verifyJWT(token: string): Promise<boolean> {
  try {
    // Get JWT secret from environment or use fallback
    const secret = process.env.JWT_SECRET || 'sahool-default-secret-change-in-production';
    const secretKey = new TextEncoder().encode(secret);

    // Verify the JWT token
    await jwtVerify(token, secretKey, {
      // Verify standard claims (exp, nbf, etc.)
      algorithms: ['HS256'],
    });

    return true;
  } catch (error) {
    // Token verification failed (invalid signature, expired, etc.)
    console.error('JWT verification failed:', error instanceof Error ? error.message : 'Unknown error');
    return false;
  }
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
    ? `'self' http://localhost:* ws://localhost:* wss://localhost:* https://tile.openstreetmap.org https://sentinel-hub.com`
    : `'self' wss://*.sahool.com https://*.sahool.com https://tile.openstreetmap.org https://sentinel-hub.com`;

  // Build CSP directives
  const directives = [
    `default-src 'self'`,
    `script-src ${scriptSrc}`,
    `style-src ${styleSrc}`,
    `img-src 'self' data: blob: https://tile.openstreetmap.org https://*.sahool.com`,
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

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow static files and Next.js internals
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') // files with extensions (images, etc.)
  ) {
    return NextResponse.next();
  }

  // Allow public routes
  if (publicRoutes.some((route) => pathname === route || pathname.startsWith(`${route}/`))) {
    return NextResponse.next();
  }

  // Check if route requires protection
  const isProtectedRoute = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  if (!isProtectedRoute) {
    return NextResponse.next();
  }

  // Check for auth token
  const token = request.cookies.get('access_token')?.value;

  if (!token) {
    // Redirect to login with return URL
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Verify JWT token
  const isValidToken = await verifyJWT(token);

  if (!isValidToken) {
    // Token is invalid or expired - redirect to login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    loginUrl.searchParams.set('error', 'session_expired');
    return NextResponse.redirect(loginUrl);
  }

  // Token is valid - add security headers
  const response = NextResponse.next();

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

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)',
  ],
};
