/**
 * Server-side login API route
 * Sets httpOnly cookies for security
 * Now includes rate limiting to prevent brute-force attacks
 * 
 * يتضمن الآن حماية ضد هجمات القوة الغاشمة
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { logger } from "@/lib/logger";
import { API_URL, API_ENDPOINTS, TIMEOUT_TIERS } from "@/config/api";
import { checkRateLimit, resetRateLimit } from "@/lib/rate-limiter";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, totp_code } = body;

    // Rate limiting check by email (prevent brute-force)
    const rateLimit = checkRateLimit(`login:${email}`, {
      maxAttempts: 5,
      windowMs: 15 * 60 * 1000, // 15 minutes
      lockoutDurationMs: 30 * 60 * 1000, // 30 minutes lockout
    });

    if (!rateLimit.allowed) {
      logger.warn(`Rate limit exceeded for email: ${email}`);
      return NextResponse.json(
        {
          error: rateLimit.message || "Too many login attempts",
          resetTime: rateLimit.resetTime,
        },
        { status: 429 }
      );
    }

    // Forward to backend auth API with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}${API_ENDPOINTS.auth.login}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          ...(totp_code && { totp_code }),
        }),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    // Validate response content-type before parsing JSON
    const contentType = response.headers.get("content-type");
    if (!contentType?.includes("application/json")) {
      logger.error(
        `Login upstream returned non-JSON response: ${response.status} ${contentType}`,
      );
      return NextResponse.json(
        { error: "An invalid response was received from the upstream server" },
        { status: 502 },
      );
    }

    let data: any;
    try {
      data = await response.json();
    } catch {
      logger.error("Login upstream returned invalid JSON");
      return NextResponse.json(
        { error: "Invalid response from authentication server" },
        { status: 502 },
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        { error: data.message || data.detail || "Login failed" },
        { status: response.status },
      );
    }

    // If 2FA required, return temp token
    if (data.requires_2fa) {
      return NextResponse.json({
        requires_2fa: true,
        temp_token: data.temp_token,
      });
    }

    // Set secure httpOnly cookies
    const cookieStore = await cookies();

    // Access token - aligned with JWT expiry (default 30 min)
    // SECURITY FIX: Cookie maxAge must match JWT expiry to prevent stale tokens
    const accessTokenMaxAge = parseInt(
      process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS || "1800",
      10,
    ); // 30 minutes default
    cookieStore.set("sahool_admin_token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: accessTokenMaxAge,
      path: "/",
    });

    // Refresh token if provided - aligned with refresh token expiry (default 7 days)
    if (data.refresh_token) {
      const refreshTokenMaxAge = parseInt(
        process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS || "604800",
        10,
      ); // 7 days default
      cookieStore.set("sahool_admin_refresh_token", data.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
        maxAge: refreshTokenMaxAge,
        path: "/",
      });
    }

    // Last activity timestamp for idle timeout tracking
    cookieStore.set("sahool_admin_last_activity", Date.now().toString(), {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: accessTokenMaxAge,
      path: "/",
    });

    // Reset rate limit on successful login
    resetRateLimit(`login:${email}`);

    return NextResponse.json({
      success: true,
      user: data.user,
    });
  } catch (error) {
    logger.error("Login error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
