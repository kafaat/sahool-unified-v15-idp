/**
 * Server-side send OTP proxy route
 * Routes request through Next.js server to Kong gateway
 *
 * مسار الخادم لإرسال رمز التحقق
 */

import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/lib/logger";
import { API_URL, TIMEOUT_TIERS } from "@/config/api";
import { AUTH_ENDPOINTS } from "@sahool/shared-types/contracts";
import { checkRateLimit } from "@/lib/rate-limiter";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { identifier, channel, purpose } = body;

    if (!identifier || !channel) {
      return NextResponse.json(
        { error: "Identifier and channel are required" },
        { status: 400 },
      );
    }

    // Rate limiting: 3 attempts per 15 minutes
    const rateLimit = checkRateLimit(`send-otp:${identifier}`, {
      maxAttempts: 3,
      windowMs: 15 * 60 * 1000,
      lockoutDurationMs: 60 * 60 * 1000,
    });

    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: rateLimit.message || "Too many requests",
          resetTime: rateLimit.resetTime,
        },
        { status: 429 },
      );
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}${AUTH_ENDPOINTS.SEND_OTP}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, channel, purpose }),
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
        { error: data.message || data.detail || "Failed to send OTP" },
        { status: response.status },
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    logger.production("Send OTP error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
