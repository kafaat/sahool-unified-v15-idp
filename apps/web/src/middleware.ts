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
 *
 * Edge Bundle Optimization:
 * - Locale detection is done inline (no next-intl/middleware import ~200KB+)
 * - Logger is edge-safe console-only (no @sentry/nextjs import ~300KB+)
 * - Locale constants are inlined (no @sahool/i18n barrel import ~24KB+ JSON)
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  generateNonce,
  getCSPHeader,
  getCSPHeaderName,
  getCSPConfig,
} from "@/lib/security/csp-config";
import { validateJwtToken } from "@/lib/security/jwt-middleware";
import { validateCsrfRequest } from "@/lib/security/csrf-server";

// ---------------------------------------------------------------------------
// Inline locale constants to avoid pulling in the full @sahool/i18n barrel
// which imports all locale JSON files and re-exports next-intl client code.
// These MUST stay in sync with packages/i18n/src/index.ts.
// ---------------------------------------------------------------------------
const locales = ["ar", "en"] as const;
const defaultLocale: (typeof locales)[number] = "ar";

// ---------------------------------------------------------------------------
// Edge-safe logger - avoids importing @/lib/logger which references
// @sentry/nextjs (~300KB). In the edge middleware we only need console output.
// ---------------------------------------------------------------------------
const edgeLogger = {
  error: (...args: unknown[]) => {
    if (process.env.NODE_ENV === "development") {
      console.error(...args);
    }
  },
};

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
  "/copilot",
];

/**
 * Detect preferred locale from the request.
 *
 * Lightweight replacement for next-intl/middleware createMiddleware() which
 * pulls in the entire next-intl runtime (~200KB+). Since we use
 * localePrefix: "never" (no locale segment in the URL), the only job of
 * the i18n middleware was to:
 *   1. Detect locale from NEXT_LOCALE cookie or Accept-Language header
 *   2. Set the NEXT_LOCALE cookie so next-intl server picks it up
 *
 * This function replicates that behaviour at a fraction of the bundle cost.
 */
function detectLocale(request: NextRequest): (typeof locales)[number] {
  // 1. Explicit cookie takes priority
  const cookieLocale = request.cookies.get("NEXT_LOCALE")?.value;
  if (cookieLocale && (locales as readonly string[]).includes(cookieLocale)) {
    return cookieLocale as (typeof locales)[number];
  }

  // 2. Parse Accept-Language header (first match wins)
  const acceptLang = request.headers.get("accept-language") ?? "";
  for (const part of acceptLang.split(",")) {
    const lang = (part.split(";")[0] ?? "").trim().toLowerCase();
    // Match exact ("ar", "en") or prefix ("ar-SA" -> "ar", "en-US" -> "en")
    const prefix = lang.split("-")[0] ?? "";
    if (prefix && (locales as readonly string[]).includes(prefix)) {
      return prefix as (typeof locales)[number];
    }
  }

  return defaultLocale;
}

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
  // 2. Lightweight locale detection (replaces next-intl/middleware)
  //    Sets NEXT_LOCALE cookie so that next-intl server config picks it up.
  // ═══════════════════════════════════════════════════════════════════════════
  const detectedLocale = detectLocale(request);

  // ═══════════════════════════════════════════════════════════════════════════
  // 3. Allow public routes (without authentication or CSRF)
  //    Public routes are checked BEFORE CSRF to avoid blocking login/register
  //    Server Actions (POST) that don't yet have a CSRF token.
  // ═══════════════════════════════════════════════════════════════════════════
  const isPublicRoute = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (isPublicRoute) {
    // Still add basic security headers for public routes
    const response = NextResponse.next();
    addSecurityHeaders(response);
    setLocaleCookie(response, detectedLocale);
    return response;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 4. CSRF Protection for state-changing requests (after public route check)
  // ═══════════════════════════════════════════════════════════════════════════
  const csrfValidation = validateCsrfRequest(request);
  if (!csrfValidation.valid) {
    // Log CSRF failure
    edgeLogger.error(`[CSRF] Validation failed: ${csrfValidation.error}`, {
      method: request.method,
      path: pathname,
    });

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
  // 5. Check if route requires authentication (unchanged)
  // ═══════════════════════════════════════════════════════════════════════════
  const isProtectedRoute = protectedRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );

  if (!isProtectedRoute) {
    // Not a protected route - allow with security headers
    const response = NextResponse.next();
    addSecurityHeaders(response);
    setLocaleCookie(response, detectedLocale);
    return response;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 6. JWT Token Validation (with signature verification)
  // ═══════════════════════════════════════════════════════════════════════════
  const jwtValidation = await validateJwtToken(request);

  if (!jwtValidation.valid) {
    // Log JWT failure
    edgeLogger.error(`[JWT] Validation failed: ${jwtValidation.error}`, {
      path: pathname,
    });

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

  // Add all security headers and locale cookie
  addSecurityHeaders(response);
  setLocaleCookie(response, detectedLocale);

  // Generate CSRF token if not present
  let csrfToken = request.cookies.get("csrf_token")?.value;
  if (!csrfToken) {
    // Use Web Crypto API for Edge Runtime compatibility
    const randomValues = new Uint8Array(32);
    crypto.getRandomValues(randomValues);
    csrfToken = btoa(String.fromCharCode(...randomValues))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=/g, "");
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
 * Persist the detected locale in the NEXT_LOCALE cookie so that
 * next-intl's server-side getRequestConfig() can read it on
 * subsequent requests. This replaces the cookie-setting behaviour
 * that was previously handled by next-intl/middleware.
 */
function setLocaleCookie(
  response: NextResponse,
  locale: (typeof locales)[number],
): void {
  response.cookies.set("NEXT_LOCALE", locale, {
    path: "/",
    maxAge: 60 * 60 * 24 * 365, // 1 year
    sameSite: "lax",
  });
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
