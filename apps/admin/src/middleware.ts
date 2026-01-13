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
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  generateNonce,
  getCSPHeader,
  getCSPHeaderName,
  getCSPConfig,
} from "@/lib/security/csp-config";
import {
  validateCsrfRequest,
  generateCsrfToken,
} from "@/lib/security/csrf-server";
import { verifyToken, isTokenExpired } from "@/lib/auth/jwt-verify";
import {
  isPublicRoute,
  getRequiredRoles,
  hasRouteAccess,
  getUnauthorizedRedirect,
} from "@/lib/auth/route-protection";

// Idle timeout: 30 minutes in milliseconds
const IDLE_TIMEOUT = 30 * 60 * 1000;

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow static files and Next.js internals
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/static") ||
    pathname.includes(".") // files with extensions
  ) {
    return NextResponse.next();
  }

  // Allow public routes (login, health check, etc.)
  if (isPublicRoute(pathname)) {
    return NextResponse.next();
  }

  // ============================================
  // AUTHENTICATION CHECK
  // ============================================
  const token = request.cookies.get("sahool_admin_token")?.value;

  if (!token) {
    // No token - redirect to login
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("returnTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Quick check for expired token (without full verification)
  if (isTokenExpired(token)) {
    // Token expired - clear cookies and redirect
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("returnTo", pathname);
    loginUrl.searchParams.set("reason", "token_expired");

    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete("sahool_admin_token");
    response.cookies.delete("sahool_admin_refresh_token");
    response.cookies.delete("sahool_admin_last_activity");

    return response;
  }

  // ============================================
  // JWT TOKEN VERIFICATION
  // ============================================
  let userRole: "admin" | "supervisor" | "viewer";

  try {
    // Verify JWT signature and extract role
    const payload = await verifyToken(token);
    userRole = payload.role || "viewer";
  } catch (error) {
    // Token verification failed (invalid signature, malformed, etc.)
    console.error("Token verification failed:", error);

    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("returnTo", pathname);
    loginUrl.searchParams.set("reason", "invalid_token");

    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete("sahool_admin_token");
    response.cookies.delete("sahool_admin_refresh_token");
    response.cookies.delete("sahool_admin_last_activity");

    return response;
  }

  // ============================================
  // ROLE-BASED AUTHORIZATION CHECK
  // ============================================
  const requiredRoles = getRequiredRoles(pathname);

  if (requiredRoles && !hasRouteAccess(pathname, userRole)) {
    // User doesn't have required role - return 403 Forbidden
    // For API routes, return JSON error
    if (pathname.startsWith("/api/")) {
      return NextResponse.json(
        {
          error: "Forbidden",
          message: "You do not have permission to access this resource",
          required_roles: requiredRoles,
          your_role: userRole,
        },
        { status: 403 },
      );
    }

    // For page routes, redirect to dashboard with error
    const unauthorizedUrl = new URL(
      getUnauthorizedRedirect(userRole),
      request.url,
    );
    unauthorizedUrl.searchParams.set("error", "unauthorized");
    unauthorizedUrl.searchParams.set("attempted_route", pathname);

    return NextResponse.redirect(unauthorizedUrl);
  }

  // ============================================
  // CSRF VALIDATION (for state-changing requests)
  // ============================================
  const csrfValidation = validateCsrfRequest(request);
  if (!csrfValidation.valid) {
    // For API routes, return JSON error
    if (pathname.startsWith("/api/")) {
      return NextResponse.json(
        {
          error: "CSRF validation failed",
          message: csrfValidation.error,
        },
        { status: 403 },
      );
    }

    // For page routes, redirect to login with error
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("error", "csrf_failed");
    return NextResponse.redirect(loginUrl);
  }

  // ============================================
  // IDLE TIMEOUT CHECK
  // ============================================
  const lastActivityStr = request.cookies.get(
    "sahool_admin_last_activity",
  )?.value;
  if (lastActivityStr) {
    const lastActivity = parseInt(lastActivityStr, 10);
    const now = Date.now();
    const timeSinceLastActivity = now - lastActivity;

    if (timeSinceLastActivity >= IDLE_TIMEOUT) {
      // Session expired due to inactivity - clear cookies and redirect
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("returnTo", pathname);
      loginUrl.searchParams.set("reason", "session_expired");

      const response = NextResponse.redirect(loginUrl);
      response.cookies.delete("sahool_admin_token");
      response.cookies.delete("sahool_admin_refresh_token");
      response.cookies.delete("sahool_admin_last_activity");

      return response;
    }
  }

  // ============================================
  // SECURITY HEADERS
  // ============================================
  const response = NextResponse.next();

  // Generate nonce for CSP
  const nonce = generateNonce();

  // ============================================
  // CSRF TOKEN GENERATION
  // ============================================
  let csrfToken = request.cookies.get("sahool_admin_csrf")?.value;
  if (!csrfToken) {
    csrfToken = generateCsrfToken();
    response.cookies.set("sahool_admin_csrf", csrfToken, {
      httpOnly: false, // Must be readable by JavaScript for AJAX requests
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 60 * 60 * 24, // 24 hours
    });
  }

  // Store nonce in response headers for use in HTML
  response.headers.set("X-Nonce", nonce);

  // Store user role in header for API routes to use
  response.headers.set("X-User-Role", userRole);

  // Add security headers
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set("X-XSS-Protection", "1; mode=block");

  // HSTS - only in production with HTTPS
  if (process.env.NODE_ENV === "production") {
    response.headers.set(
      "Strict-Transport-Security",
      "max-age=31536000; includeSubDomains",
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
    "/((?!_next/static|_next/image|favicon.ico|public).*)",
  ],
};
