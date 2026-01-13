/**
 * SAHOOL CSP Violation Reporting Endpoint
 * نقطة نهاية الإبلاغ عن انتهاكات CSP
 *
 * Receives and logs Content Security Policy violation reports
 * يستقبل ويسجل تقارير انتهاكات سياسة أمان المحتوى
 */

import { NextRequest, NextResponse } from "next/server";
import {
  isValidCSPReport,
  sanitizeCSPReport,
  type CSPReportBody,
} from "@/lib/security/csp-config";
import { isRateLimited } from "@/lib/rate-limiter";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 100,
  keyPrefix: "csp-report",
};

/**
 * Get client IP address
 * الحصول على عنوان IP للعميل
 */
function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get("x-forwarded-for");
  const realIp = request.headers.get("x-real-ip");

  if (forwarded) {
    const firstIp = forwarded.split(",")[0];
    return firstIp ? firstIp.trim() : "unknown";
  }

  if (realIp) {
    return realIp;
  }

  return "unknown";
}

// ═══════════════════════════════════════════════════════════════════════════
// CSP Report Handler
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/csp-report
 * Handle CSP violation reports
 */
export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);

    if (rateLimited) {
      return NextResponse.json({ error: "Too many reports" }, { status: 429 });
    }

    // Parse request body
    const body = (await request.json()) as unknown;

    // Validate report format
    if (!isValidCSPReport(body)) {
      return NextResponse.json(
        { error: "Invalid CSP report format" },
        { status: 400 },
      );
    }

    const reportBody = body as CSPReportBody;
    const report = reportBody["csp-report"];

    // Sanitize and format report
    const sanitized = sanitizeCSPReport(report);

    // Filter out known false positives
    const blockedUri = report["blocked-uri"];

    // Skip browser extensions
    if (
      blockedUri.startsWith("chrome-extension://") ||
      blockedUri.startsWith("moz-extension://") ||
      blockedUri.startsWith("safari-extension://") ||
      blockedUri.startsWith("ms-browser-extension://")
    ) {
      return NextResponse.json({ status: "ignored" }, { status: 200 });
    }

    // Skip about:blank and data URIs in development
    if (
      process.env.NODE_ENV === "development" &&
      (blockedUri === "about:blank" || blockedUri.startsWith("data:"))
    ) {
      return NextResponse.json({ status: "ignored" }, { status: 200 });
    }

    // Log CSP violation
    logger.warn("[CSP Violation]", {
      ...sanitized,
      clientIP,
      userAgent: request.headers.get("user-agent"),
    });

    // In production, you might want to send this to a logging service
    // such as Sentry, LogRocket, or your own analytics platform
    if (process.env.NODE_ENV === "production") {
      // Example: Send to external monitoring service
      // await sendToMonitoringService(sanitized);

      // Log to stderr for container log aggregation (always log in production)
      logger.production({
        type: "csp-violation",
        ...sanitized,
        clientIP,
        userAgent: request.headers.get("user-agent"),
        environment: process.env.NODE_ENV,
      });
    }

    // Return 204 No Content (cannot have body)
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    // Critical error - always log
    logger.critical("[CSP Report Handler Error]", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}

/**
 * OPTIONS /api/csp-report
 * Handle preflight requests
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
