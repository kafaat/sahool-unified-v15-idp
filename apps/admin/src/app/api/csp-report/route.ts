/**
 * CSP Report API Route
 * مسار API لتقارير CSP
 *
 * Receives Content Security Policy violation reports from browsers
 */

import { NextRequest, NextResponse } from "next/server";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface CSPReport {
  "document-uri": string;
  "violated-directive": string;
  "effective-directive"?: string;
  "original-policy"?: string;
  "blocked-uri": string;
  "status-code"?: number;
  "source-file"?: string;
  "line-number"?: number;
  "column-number"?: number;
  referrer?: string;
  disposition?: string;
}

interface CSPReportBody {
  "csp-report": CSPReport;
}

// ═══════════════════════════════════════════════════════════════════════════
// Rate Limiting
// ═══════════════════════════════════════════════════════════════════════════

const rateLimitMap = new Map<string, { count: number; resetTime: number }>();
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX = 100; // 100 reports per minute per IP

function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(ip);

  if (!record || now > record.resetTime) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return true;
  }

  if (record.count >= RATE_LIMIT_MAX) {
    return false;
  }

  record.count++;
  return true;
}

// Clean up old entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [ip, record] of rateLimitMap.entries()) {
    if (now > record.resetTime) {
      rateLimitMap.delete(ip);
    }
  }
}, 60 * 1000);

// ═══════════════════════════════════════════════════════════════════════════
// Validation
// ═══════════════════════════════════════════════════════════════════════════

function isValidCSPReport(report: unknown): report is CSPReportBody {
  if (!report || typeof report !== "object") return false;

  const cspReport = (report as CSPReportBody)["csp-report"];
  if (!cspReport || typeof cspReport !== "object") return false;

  // Required fields
  if (typeof cspReport["document-uri"] !== "string") return false;
  if (typeof cspReport["violated-directive"] !== "string") return false;
  if (typeof cspReport["blocked-uri"] !== "string") return false;

  return true;
}

function shouldFilterReport(report: CSPReport): boolean {
  const blockedUri = report["blocked-uri"] || "";

  // Filter browser extensions
  if (
    blockedUri.startsWith("chrome-extension://") ||
    blockedUri.startsWith("moz-extension://") ||
    blockedUri.startsWith("safari-extension://") ||
    blockedUri.startsWith("ms-browser-extension://")
  ) {
    return true;
  }

  // Filter development artifacts in dev mode
  if (process.env.NODE_ENV === "development") {
    if (blockedUri === "about:blank" || blockedUri.startsWith("data:")) {
      return true;
    }
  }

  return false;
}

// ═══════════════════════════════════════════════════════════════════════════
// Route Handler
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/csp-report
 * Receive CSP violation reports
 */
export async function POST(request: NextRequest) {
  // Get client IP
  const ip =
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    request.headers.get("x-real-ip") ||
    "unknown";

  // Rate limit check
  if (!checkRateLimit(ip)) {
    return new NextResponse(null, {
      status: 429,
      headers: {
        "Retry-After": "60",
        "X-Content-Type-Options": "nosniff",
      },
    });
  }

  try {
    // Parse report
    const body = await request.json();

    // Validate report format
    if (!isValidCSPReport(body)) {
      return NextResponse.json(
        { error: "Invalid CSP report format" },
        {
          status: 400,
          headers: { "X-Content-Type-Options": "nosniff" },
        },
      );
    }

    const report = body["csp-report"];

    // Filter known false positives
    if (shouldFilterReport(report)) {
      return new NextResponse(null, { status: 204 });
    }

    // Log the violation
    const logEntry = {
      timestamp: new Date().toISOString(),
      service: "sahool-admin",
      type: "csp-violation",
      documentUri: report["document-uri"],
      violatedDirective: report["violated-directive"],
      effectiveDirective: report["effective-directive"],
      blockedUri: report["blocked-uri"],
      statusCode: report["status-code"],
      sourceFile: report["source-file"],
      lineNumber: report["line-number"],
      columnNumber: report["column-number"],
      clientIP: ip,
      userAgent: request.headers.get("user-agent"),
    };

    // Log to console (in production, send to logging service)
    if (process.env.NODE_ENV === "production") {
      logger.critical(JSON.stringify(logEntry));
    } else {
      logger.warn("[CSP Violation]", logEntry);
    }

    // Return 204 No Content (success, no body)
    return new NextResponse(null, {
      status: 204,
      headers: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
      },
    });
  } catch (error) {
    logger.critical("[CSP Report] Parse error:", error);
    return NextResponse.json(
      { error: "Failed to process CSP report" },
      {
        status: 400,
        headers: { "X-Content-Type-Options": "nosniff" },
      },
    );
  }
}

/**
 * OPTIONS /api/csp-report
 * Handle CORS preflight
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
    },
  });
}
