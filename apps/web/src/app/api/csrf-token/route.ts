/**
 * CSRF Token API Route
 * مسار API لإنشاء رموز CSRF
 *
 * Generates and returns CSRF tokens for client-side requests
 */

import { NextRequest, NextResponse } from "next/server";
import { randomBytes } from "node:crypto";

/**
 * Generate a cryptographically secure CSRF token
 */
function generateCsrfToken(): string {
  return randomBytes(32).toString("base64url");
}

/**
 * GET /api/csrf-token
 * Returns a new CSRF token and sets it in a cookie
 */
export async function GET(_request: NextRequest) {
  try {
    // Generate new CSRF token
    const csrfToken = generateCsrfToken();

    // Create response with token
    const response = NextResponse.json({
      success: true,
      token: csrfToken,
    });

    // Set CSRF token in HTTP-only cookie
    response.cookies.set("csrf_token", csrfToken, {
      httpOnly: false, // Must be readable by client-side JavaScript
      secure: process.env.NODE_ENV === "production", // HTTPS only in production
      sameSite: "strict", // CSRF protection
      path: "/",
      maxAge: 60 * 60 * 24, // 24 hours
    });

    // Also set in a readable cookie for the client to include in headers
    response.cookies.set("_csrf", csrfToken, {
      httpOnly: false,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 60 * 60 * 24, // 24 hours
    });

    return response;
  } catch (error) {
    console.error("Error generating CSRF token:", error);
    return NextResponse.json(
      {
        success: false,
        error: "Failed to generate CSRF token",
      },
      { status: 500 },
    );
  }
}

/**
 * POST /api/csrf-token/validate
 * Validates a CSRF token (for testing purposes)
 */
export async function POST(request: NextRequest) {
  try {
    const { token } = await request.json();
    const cookieToken = request.cookies.get("csrf_token")?.value;

    if (!token || !cookieToken) {
      return NextResponse.json(
        {
          success: false,
          error: "CSRF token missing",
        },
        { status: 400 },
      );
    }

    if (token !== cookieToken) {
      return NextResponse.json(
        {
          success: false,
          error: "CSRF token mismatch",
        },
        { status: 403 },
      );
    }

    return NextResponse.json({
      success: true,
      message: "CSRF token valid",
    });
  } catch (error) {
    console.error("Error validating CSRF token:", error);
    return NextResponse.json(
      {
        success: false,
        error: "Failed to validate CSRF token",
      },
      { status: 500 },
    );
  }
}
