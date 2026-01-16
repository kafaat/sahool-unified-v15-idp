/**
 * CSRF Token API Route
 * مسار API لرمز CSRF
 *
 * GET  - Generate new CSRF token
 * POST - Refresh existing token
 */

import { NextRequest, NextResponse } from "next/server";
import {
  createCsrfTokenPayload,
  serializeCsrfTokenPayload,
  getCsrfCookieOptions,
  CSRF_CONFIG,
} from "@/lib/csrf";
import { logger } from "@/lib/logger";

/**
 * GET /api/csrf-token
 * Generate and return a new CSRF token
 */
export async function GET(request: NextRequest) {
  try {
    // Generate new token payload
    const payload = createCsrfTokenPayload();
    const serialized = serializeCsrfTokenPayload(payload);
    const cookieOptions = getCsrfCookieOptions();

    // Create response with token
    const response = NextResponse.json({
      token: payload.token,
      expiresAt: payload.expiresAt,
    });

    // Set httpOnly cookie with full payload
    response.cookies.set(CSRF_CONFIG.COOKIE_NAME, serialized, {
      httpOnly: cookieOptions.httpOnly,
      secure: cookieOptions.secure,
      sameSite: cookieOptions.sameSite,
      path: cookieOptions.path,
      maxAge: cookieOptions.maxAge,
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
    // Generate new token payload
    const payload = createCsrfTokenPayload();
    const serialized = serializeCsrfTokenPayload(payload);
    const cookieOptions = getCsrfCookieOptions();

    // Create response with new token
    const response = NextResponse.json({
      token: payload.token,
      expiresAt: payload.expiresAt,
      refreshed: true,
    });

    // Set httpOnly cookie with full payload
    response.cookies.set(CSRF_CONFIG.COOKIE_NAME, serialized, {
      httpOnly: cookieOptions.httpOnly,
      secure: cookieOptions.secure,
      sameSite: cookieOptions.sameSite,
      path: cookieOptions.path,
      maxAge: cookieOptions.maxAge,
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
