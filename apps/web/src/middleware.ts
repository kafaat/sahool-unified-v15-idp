/**
 * SAHOOL Web Authentication Middleware
 * ميدل وير التوثيق لتطبيق الويب
 *
 * Protects dashboard routes with server-side authentication
 * يحمي مسارات لوحة التحكم بالتوثيق من جانب الخادم
 *
 * Security Features:
 * - JWT token validation with signature verification
 * - CSRF protection for state-changing requests
 * - Security headers (CSP, X-Frame-Options, HSTS, etc.)
 * - Secure redirect handling
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import createMiddleware from "next-intl/middleware";
import {
  generateNonce,
  getCSPHeader,
  getCSPHeaderName,
  getCSPConfig,
} from "@/lib/security/csp-config";
import { locales, defaultLocale } from "@sahool/i18n";
import { randomBytes } from "crypto";
import { validateJwtToken } from "@/lib/security/jwt-middleware";
import { validateCsrfRequest } from "@/lib/security/csrf-server";

// Routes that don't require authentication
const publicRoutes = [
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/api/auth",
  "/",
];

// Routes that require authentication
const protectedRoutes = [
  "/dashboard",
  "/fields",
  "/tasks",
  "/weather",
  "/analytics",
  "/settings",
  "/iot",
  "/equipment",
  "/wallet",
  "/community",
  "/marketplace",
  "/crop-health",
];

// Create i18n middleware
const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localePrefix: "as-needed", // Don't prefix default locale (ar)
});

export async function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  // ═══════════════════════════════════════════════════════════════════════════
  // 1. Allow static files and Next.js internals (no security headers needed)
  // ═══════════════════════════════════════════════════════════════════════════
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/static") ||
    pathname.startsWith("/api") ||
    pathname.includes(".") // files with extensions (images, etc.)
  ) {
    return NextResponse.next();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 2. Handle i18n routing
  // ═══════════════════════════════════════════════════════════════════════════
  const intlResponse = intlMiddleware(request);
  if (intlResponse) {
    // If i18n middleware returns a redirect, use that
    if (intlResponse.headers.get("location")) {
      return intlResponse;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 3. CSRF Protection for state-changing requests
  // ═══════════════════════════════════════════════════════════════════════════
  const csrfValidation = validateCsrfRequest(request);
  if (!csrfValidation.valid) {
    // Log CSRF failure in development
    if (process.env.NODE_ENV === "development") {
      console.error(`[CSRF] Validation failed: ${csrfValidation.error}`, {
        method: request.method,
        path: pathname,
      });
    }

    // Return 403 Forbidden for CSRF validation failures
    return new NextResponse("CSRF validation failed", {
      status: 403,
      headers: {
        "Content-Type": "text/plain",
        "X-CSRF-Error": csrfValidation.error || "CSRF token mismatch",
      },
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 4. Allow public routes (without authentication)
  // ═══════════════════════════════════════════════════════════════════════════
  const isPublicRoute = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (isPublicRoute) {
    // Still add basic security headers for public routes
    const response = NextResponse.next();
    addSecurityHeaders(response);
    return response;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 5. Check if route requires authentication
  // ═══════════════════════════════════════════════════════════════════════════
  const isProtectedRoute = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (!isProtectedRoute) {
    // Not a protected route - allow with security headers
    const response = NextResponse.next();
    addSecurityHeaders(response);
    return response;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 6. JWT Token Validation (with signature verification)
  // ═══════════════════════════════════════════════════════════════════════════
  const jwtValidation = await validateJwtToken(request);

  if (!jwtValidation.valid) {
    // Log JWT failure in development
    if (process.env.NODE_ENV === "development") {
      console.error(`[JWT] Validation failed: ${jwtValidation.error}`, {
        path: pathname,
      });
    }

    // Redirect to login with secure return URL
    const loginUrl = new URL("/login", request.url);

    // Sanitize and validate return URL to prevent open redirect
    const returnTo = sanitizeReturnUrl(pathname + search, request.url);
    if (returnTo) {
      loginUrl.searchParams.set("returnTo", returnTo);
    }

    // Add reason for development debugging
    if (process.env.NODE_ENV === "development" && jwtValidation.error) {
      loginUrl.searchParams.set("reason", jwtValidation.error);
    }

    return NextResponse.redirect(loginUrl);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 7. Token is valid - proceed with security headers
  // ═══════════════════════════════════════════════════════════════════════════
  const response = NextResponse.next();

  // Add all security headers
  addSecurityHeaders(response);

  // Generate CSRF token if not present
  let csrfToken = request.cookies.get("csrf_token")?.value;
  if (!csrfToken) {
    csrfToken = randomBytes(32).toString("base64url");
    response.cookies.set("csrf_token", csrfToken, {
      httpOnly: false, // Must be readable by client JavaScript for AJAX requests
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 60 * 60 * 24, // 24 hours
    });
  }

  return response;
}

/**
 * Add comprehensive security headers to response
 */
function addSecurityHeaders(response: NextResponse): void {
  // Generate nonce for CSP
  const nonce = generateNonce();
  response.headers.set("X-Nonce", nonce);

  // ═══════════════════════════════════════════════════════════════════════════
  // Standard Security Headers
  // ═══════════════════════════════════════════════════════════════════════════

  // Prevent clickjacking attacks
  response.headers.set("X-Frame-Options", "DENY");

  // Prevent MIME type sniffing
  response.headers.set("X-Content-Type-Options", "nosniff");

  // Control referrer information
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

  // Legacy XSS protection (modern browsers use CSP)
  response.headers.set("X-XSS-Protection", "1; mode=block");

  // Permissions Policy - restrict browser features
  response.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=(self), payment=()",
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // HSTS - Force HTTPS in production
  // ═══════════════════════════════════════════════════════════════════════════
  if (process.env.NODE_ENV === "production") {
    response.headers.set(
      "Strict-Transport-Security",
      "max-age=31536000; includeSubDomains; preload",
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Content Security Policy
  // ═══════════════════════════════════════════════════════════════════════════
  const cspConfig = getCSPConfig(nonce);
  const cspHeader = getCSPHeader(nonce);
  const cspHeaderName = getCSPHeaderName(cspConfig.reportOnly);
  response.headers.set(cspHeaderName, cspHeader);
}

/**
 * Sanitize return URL to prevent open redirect vulnerabilities
 *
 * @param returnTo - Requested return URL
 * @param baseUrl - Base URL of the application
 * @returns Sanitized return URL or null if invalid
 */
function sanitizeReturnUrl(returnTo: string, baseUrl: string): string | null {
  try {
    // Parse the return URL
    const returnUrl = new URL(returnTo, baseUrl);
    const base = new URL(baseUrl);

    // Only allow same-origin redirects
    if (returnUrl.origin !== base.origin) {
      return null;
    }

    // Return only the pathname and search (no protocol, host, hash)
    return returnUrl.pathname + returnUrl.search;
  } catch {
    // Invalid URL - return null
    return null;
  }
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
    "/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)",
  ],
};
