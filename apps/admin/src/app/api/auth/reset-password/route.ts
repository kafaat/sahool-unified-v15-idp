/**
 * Server-side reset password proxy route
 * Routes request through Next.js server to Kong gateway
 *
 * مسار الخادم لإعادة تعيين كلمة المرور
 */

import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/lib/logger";
import { API_URL, TIMEOUT_TIERS } from "@/config/api";
import { AUTH_ENDPOINTS } from "@sahool/shared-types/contracts";
import { checkRateLimit } from "@/lib/rate-limiter";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { token, newPassword } = body;

    if (!token || !newPassword) {
      return NextResponse.json(
        { error: "Token and new password are required" },
        { status: 400 },
      );
    }

    if (newPassword.length < 8) {
      return NextResponse.json(
        { error: "Password must be at least 8 characters" },
        { status: 400 },
      );
    }

    // Rate limiting: 5 attempts per 15 minutes
    const rateLimit = checkRateLimit(`reset-password:${token.slice(0, 16)}`, {
      maxAttempts: 5,
      windowMs: 15 * 60 * 1000,
      lockoutDurationMs: 30 * 60 * 1000,
    });

    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: rateLimit.message || "Too many attempts",
          resetTime: rateLimit.resetTime,
        },
        { status: 429 },
      );
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}${AUTH_ENDPOINTS.RESET_PASSWORD}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, newPassword }),
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
        { error: data.message || data.detail || "Password reset failed" },
        { status: response.status },
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    logger.production("Reset password error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
