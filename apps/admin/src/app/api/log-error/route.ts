/**
 * Error Logging API Endpoint - Admin Dashboard
 * نقطة نهاية API لتسجيل الأخطاء - لوحة التحكم
 */

import { NextRequest, NextResponse } from "next/server";
import { logger } from "../../../lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ErrorLogPayload {
  message: string;
  stack?: string;
  componentStack?: string;
  url?: string;
  userAgent?: string;
  timestamp: string;
  environment?: string;
  context?: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Input Validation & Sanitization
// SECURITY: Prevent log injection attacks by sanitizing all inputs
// ═══════════════════════════════════════════════════════════════════════════

const MAX_MESSAGE_LENGTH = 10000;
const MAX_STACK_LENGTH = 50000;
const MAX_URL_LENGTH = 2048;
const MAX_CONTEXT_DEPTH = 3;

/**
 * Sanitize a string to prevent log injection attacks
 * Removes control characters and limits length
 */
function sanitizeLogString(input: string, maxLength: number): string {
  if (typeof input !== "string") return "";
  // Remove control characters except newlines and tabs
  const sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");
  return sanitized.slice(0, maxLength);
}

/**
 * Sanitize context object to prevent deep nesting attacks
 */
function sanitizeContext(
  context: unknown,
  depth: number = 0,
): Record<string, unknown> | null {
  if (depth > MAX_CONTEXT_DEPTH) return null;
  if (!context || typeof context !== "object" || Array.isArray(context)) {
    return null;
  }

  const sanitized: Record<string, unknown> = {};
  const keys = Object.keys(context as Record<string, unknown>).slice(0, 20); // Limit keys

  for (const key of keys) {
    const value = (context as Record<string, unknown>)[key];
    const sanitizedKey = sanitizeLogString(key, 100);

    if (typeof value === "string") {
      sanitized[sanitizedKey] = sanitizeLogString(value, 1000);
    } else if (typeof value === "number" || typeof value === "boolean") {
      sanitized[sanitizedKey] = value;
    } else if (typeof value === "object" && value !== null) {
      const nested = sanitizeContext(value, depth + 1);
      if (nested) sanitized[sanitizedKey] = nested;
    }
  }

  return sanitized;
}

/**
 * Validate and sanitize the error payload
 * SECURITY: Prevents log injection and DoS via oversized payloads
 */
function validateAndSanitizePayload(
  payload: unknown,
): { valid: boolean; sanitized?: ErrorLogPayload; error?: string } {
  if (!payload || typeof payload !== "object") {
    return { valid: false, error: "Invalid payload format" };
  }

  const raw = payload as Record<string, unknown>;

  // Validate required fields
  if (typeof raw.message !== "string" || !raw.message.trim()) {
    return { valid: false, error: "Missing required field: message" };
  }
  if (typeof raw.timestamp !== "string" || !raw.timestamp.trim()) {
    return { valid: false, error: "Missing required field: timestamp" };
  }

  // Validate timestamp format (ISO 8601)
  const timestampDate = new Date(raw.timestamp);
  if (isNaN(timestampDate.getTime())) {
    return { valid: false, error: "Invalid timestamp format" };
  }

  // Build sanitized payload
  const sanitized: ErrorLogPayload = {
    message: sanitizeLogString(raw.message, MAX_MESSAGE_LENGTH),
    timestamp: timestampDate.toISOString(),
  };

  // Optional fields with sanitization
  if (typeof raw.stack === "string") {
    sanitized.stack = sanitizeLogString(raw.stack, MAX_STACK_LENGTH);
  }
  if (typeof raw.componentStack === "string") {
    sanitized.componentStack = sanitizeLogString(
      raw.componentStack,
      MAX_STACK_LENGTH,
    );
  }
  if (typeof raw.url === "string") {
    sanitized.url = sanitizeLogString(raw.url, MAX_URL_LENGTH);
  }
  if (typeof raw.userAgent === "string") {
    sanitized.userAgent = sanitizeLogString(raw.userAgent, 500);
  }
  if (typeof raw.environment === "string") {
    sanitized.environment = sanitizeLogString(raw.environment, 50);
  }
  if (raw.context) {
    const sanitizedContext = sanitizeContext(raw.context);
    if (sanitizedContext) {
      sanitized.context = sanitizedContext;
    }
  }

  return { valid: true, sanitized };
}

// ═══════════════════════════════════════════════════════════════════════════
// Rate Limiting
// ═══════════════════════════════════════════════════════════════════════════

const MAX_ERRORS_PER_MINUTE = 20;
const errorCounts = new Map<string, { count: number; resetTime: number }>();

/**
 * Check if client is rate limited
 * التحقق مما إذا كان العميل محدودًا
 */
function isRateLimited(ip: string): boolean {
  const now = Date.now();
  const entry = errorCounts.get(ip);

  if (!entry || now > entry.resetTime) {
    errorCounts.set(ip, {
      count: 1,
      resetTime: now + 60000, // 1 minute
    });
    return false;
  }

  if (entry.count >= MAX_ERRORS_PER_MINUTE) {
    return true;
  }

  entry.count++;
  return false;
}

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
// Error Log Handler
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/log-error
 * Handle error logging from client
 *
 * SECURITY: All inputs are validated and sanitized to prevent:
 * - Log injection attacks
 * - DoS via oversized payloads
 * - Rate limiting abuse
 */
export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    if (isRateLimited(clientIP)) {
      return NextResponse.json(
        { error: "Too many error reports" },
        { status: 429 },
      );
    }

    // Parse and validate request body
    let rawPayload: unknown;
    try {
      rawPayload = await request.json();
    } catch {
      return NextResponse.json(
        { error: "Invalid JSON payload" },
        { status: 400 },
      );
    }

    // Validate and sanitize the payload
    const validation = validateAndSanitizePayload(rawPayload);
    if (!validation.valid || !validation.sanitized) {
      return NextResponse.json(
        { error: validation.error || "Invalid payload" },
        { status: 400 },
      );
    }

    const payload = validation.sanitized;

    // Log to console in development
    if (process.env.NODE_ENV === "development") {
      logger.error("[Admin Error Log]", JSON.stringify(payload, null, 2));
    }

    // Create structured log entry with sanitized data
    const logEntry = {
      level: "error",
      service: "sahool-admin",
      ...payload,
      clientIP,
      receivedAt: new Date().toISOString(),
      requestHeaders: {
        userAgent: sanitizeLogString(
          request.headers.get("user-agent") || "",
          500,
        ),
        referer: sanitizeLogString(request.headers.get("referer") || "", 2048),
      },
    };

    // Log structured error
    logger.error(JSON.stringify(logEntry));

    // In production, you would:
    // 1. Send to external logging service (e.g., LogRocket, Datadog, Sentry)
    // 2. Store in database for analysis
    // 3. Send alerts for critical admin dashboard errors

    // Example: If you have Sentry server-side:
    // Sentry.captureException(new Error(payload.message), {
    //   extra: payload,
    //   tags: {
    //     service: 'admin',
    //     clientIP,
    //   },
    // });

    return NextResponse.json({ success: true, logged: true });
  } catch (error) {
    logger.error("[Error Log API] Failed to process error:", error);
    return NextResponse.json({ error: "Failed to log error" }, { status: 500 });
  }
}
