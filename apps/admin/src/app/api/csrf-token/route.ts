/**
 * CSRF Token API Route
 * مسار API لرمز CSRF
 *
 * GET  - Generate new CSRF token
 * POST - Refresh existing token
 *
 * Uses the same token format as middleware expects (simple hex string)
 * to avoid cookie/header mismatch during validation.
 */

import { NextRequest, NextResponse } from "next/server";
import { generateCsrfToken } from "@/lib/security/csrf-server";
import { logger } from "@/lib/logger";

/**
 * CSRF cookie configuration - must match middleware settings
 */
const CSRF_COOKIE_NAME = "sahool_admin_csrf";
const CSRF_COOKIE_MAX_AGE = 60 * 60 * 24; // 24 hours in seconds

/**
 * GET /api/csrf-token
 * Generate and return a new CSRF token
 */
export async function GET(request: NextRequest) {
  try {
    // Generate new token using the same function as middleware
    const token = generateCsrfToken();

    // Create response with token
    const response = NextResponse.json({
      token: token,
    });

    // Set cookie with same settings as middleware (httpOnly: false so client can read)
    response.cookies.set(CSRF_COOKIE_NAME, token, {
      httpOnly: false, // Must be readable by JavaScript for AJAX requests
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: CSRF_COOKIE_MAX_AGE,
    });

    // Security headers
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set(
      "Cache-Control",
      "no-store, no-cache, must-revalidate",
    );
    response.headers.set("Pragma", "no-cache");

    return response;
  } catch (error) {
    logger.error("[CSRF] Token generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate CSRF token" },
      { status: 500 },
    );
  }
}

/**
 * POST /api/csrf-token
 * Refresh existing CSRF token
 */
export async function POST(request: NextRequest) {
  try {
    // Generate new token using the same function as middleware
    const token = generateCsrfToken();

    // Create response with new token
    const response = NextResponse.json({
      token: token,
      refreshed: true,
    });

    // Set cookie with same settings as middleware
    response.cookies.set(CSRF_COOKIE_NAME, token, {
      httpOnly: false, // Must be readable by JavaScript for AJAX requests
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: CSRF_COOKIE_MAX_AGE,
    });

    // Security headers
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set(
      "Cache-Control",
      "no-store, no-cache, must-revalidate",
    );

    return response;
  } catch (error) {
    logger.error("[CSRF] Token refresh error:", error);
    return NextResponse.json(
      { error: "Failed to refresh CSRF token" },
      { status: 500 },
    );
  }
}

/**
 * OPTIONS /api/csrf-token
 * Handle CORS preflight
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-CSRF-Token",
      "Access-Control-Max-Age": "86400",
    },
  });
}
