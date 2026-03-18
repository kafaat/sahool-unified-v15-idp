/**
 * Server-side resend OTP proxy route
 * Routes request through Next.js server to Kong gateway
 *
 * مسار الخادم لإعادة إرسال رمز التحقق
 */

import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/lib/logger";
import { API_URL, TIMEOUT_TIERS } from "@/config/api";
import { checkRateLimit } from "@/lib/rate-limiter";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { identifier, purpose, channel } = body;

    if (!identifier || !channel) {
      return NextResponse.json(
        { error: "Identifier and channel are required" },
        { status: 400 },
      );
    }

    // Rate limiting: 3 attempts per 5 minutes (stricter for resend)
    const rateLimit = checkRateLimit(`resend-otp:${identifier}`, {
      maxAttempts: 3,
      windowMs: 5 * 60 * 1000,
      lockoutDurationMs: 15 * 60 * 1000,
    });

    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: rateLimit.message || "Too many resend attempts",
          resetTime: rateLimit.resetTime,
        },
        { status: 429 },
      );
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      // Note: AUTH_ENDPOINTS doesn't include RESEND_OTP — hardcoded path matches backend route
      response = await fetch(`${API_URL}/api/v1/auth/resend-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, purpose, channel }),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    const contentType = response.headers.get("content-type");
    if (!contentType?.includes("application/json")) {
      return NextResponse.json(
        { error: "Invalid response from backend" },
        { status: 502 },
      );
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.message || data.detail || "Failed to resend OTP" },
        { status: response.status },
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    logger.production("Resend OTP error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
