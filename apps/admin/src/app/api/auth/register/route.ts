/**
 * Server-side registration API route
 * Proxies registration requests to the backend user-service via Kong Gateway
 *
 * مسار API التسجيل من جانب الخادم
 */

import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/lib/logger";
import { API_URL } from "@/config/api";
import { checkRateLimit } from "@/lib/rate-limiter";

const REGISTER_ENDPOINT = "/api/v1/auth/register";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, firstName, lastName, phone } = body;

    // Rate limiting by email to prevent automated signup abuse
    const rateLimit = checkRateLimit(`register:${email}`, {
      maxAttempts: 3,
      windowMs: 15 * 60 * 1000, // 15 minutes
      lockoutDurationMs: 60 * 60 * 1000, // 1 hour lockout
    });

    if (!rateLimit.allowed) {
      logger.warn(`Registration rate limit exceeded for email: ${email}`);
      return NextResponse.json(
        {
          error: rateLimit.message || "تم تجاوز الحد الأقصى لمحاولات التسجيل",
          resetTime: rateLimit.resetTime,
        },
        { status: 429 }
      );
    }

    // Forward to backend auth API with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    let response: Response;
    try {
      response = await fetch(`${API_URL}${REGISTER_ENDPOINT}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          firstName,
          lastName,
          ...(phone && { phone }),
        }),
        signal: controller.signal,
      });
    } catch (fetchError) {
      clearTimeout(timeoutId);
      // Network error - backend not reachable
      logger.error("Register fetch error:", fetchError);
      return NextResponse.json(
        {
          error:
            "تعذر الاتصال بخادم المصادقة. تأكد من تشغيل خدمات البنية التحتية",
        },
        { status: 503 }
      );
    } finally {
      clearTimeout(timeoutId);
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.message || data.detail || "فشل التسجيل" },
        { status: response.status }
      );
    }

    return NextResponse.json({
      success: true,
      user: data.user,
    });
  } catch (error) {
    logger.error("Register error:", error);
    return NextResponse.json(
      { error: "حدث خطأ في الخادم" },
      { status: 500 }
    );
  }
}
