/**
 * Error Logging API Endpoint - Admin Dashboard
 * نقطة نهاية API لتسجيل الأخطاء - لوحة التحكم
 */

import { NextRequest, NextResponse } from 'next/server';
import { logger } from '../../../lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Validation Schema (lightweight Zod-like runtime validation without extra dep)
// ═══════════════════════════════════════════════════════════════════════════

const MAX_MESSAGE_LEN = 4096;
const MAX_STACK_LEN = 16384;
const MAX_URL_LEN = 2048;
const MAX_ENV_LEN = 64;

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

/**
 * Validate and sanitise the request body.
 * Returns either a sanitised payload or an error string.
 */
function validatePayload(
  body: unknown,
): { ok: true; data: ErrorLogPayload } | { ok: false; error: string } {
  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    return { ok: false, error: 'Request body must be a JSON object' };
  }

  const obj = body as Record<string, unknown>;

  // ── Required fields ─────────────────────────────────────────────────
  if (typeof obj.message !== 'string' || obj.message.length === 0) {
    return { ok: false, error: 'Missing or invalid field: message (non-empty string required)' };
  }
  if (typeof obj.timestamp !== 'string' || obj.timestamp.length === 0) {
    return { ok: false, error: 'Missing or invalid field: timestamp (non-empty string required)' };
  }

  // ── Optional string fields ──────────────────────────────────────────
  for (const field of ['stack', 'componentStack', 'url', 'userAgent', 'environment'] as const) {
    if (obj[field] !== undefined && typeof obj[field] !== 'string') {
      return { ok: false, error: `Invalid field: ${field} (string expected)` };
    }
  }

  // ── Optional object field ───────────────────────────────────────────
  if (
    obj.context !== undefined &&
    (typeof obj.context !== 'object' || obj.context === null || Array.isArray(obj.context))
  ) {
    return { ok: false, error: 'Invalid field: context (object expected)' };
  }

  // ── Length limits to prevent log injection / oversized payloads ──────
  const truncate = (v: string | undefined, max: number): string | undefined =>
    v && v.length > max ? v.slice(0, max) + '…[truncated]' : v;

  const data: ErrorLogPayload = {
    message: truncate(obj.message as string, MAX_MESSAGE_LEN)!,
    timestamp: obj.timestamp as string,
    stack: truncate(obj.stack as string | undefined, MAX_STACK_LEN),
    componentStack: truncate(obj.componentStack as string | undefined, MAX_STACK_LEN),
    url: truncate(obj.url as string | undefined, MAX_URL_LEN),
    userAgent: obj.userAgent as string | undefined,
    environment: truncate(obj.environment as string | undefined, MAX_ENV_LEN),
    context: obj.context as Record<string, unknown> | undefined,
  };

  return { ok: true, data };
}

// ═══════════════════════════════════════════════════════════════════════════
// Rate Limiting
// ═══════════════════════════════════════════════════════════════════════════

const MAX_ERRORS_PER_MINUTE = 20;
const MAX_TRACKED_IPS = 1000;
const errorCounts = new Map<string, { count: number; resetTime: number }>();

/**
 * Evict expired entries to prevent unbounded memory growth
 * حذف المدخلات منتهية الصلاحية لمنع نمو الذاكرة بلا حدود
 */
function evictExpiredEntries(): void {
  const now = Date.now();
  for (const [ip, entry] of errorCounts) {
    if (now > entry.resetTime) {
      errorCounts.delete(ip);
    }
  }
}

/**
 * Check if client is rate limited
 * التحقق مما إذا كان العميل محدودًا
 */
function isRateLimited(ip: string): boolean {
  const now = Date.now();

  // Evict stale entries when the map grows too large
  if (errorCounts.size >= MAX_TRACKED_IPS) {
    evictExpiredEntries();
  }

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
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');

  if (forwarded) {
    const firstIp = forwarded.split(',')[0];
    return firstIp ? firstIp.trim() : 'unknown';
  }

  if (realIp) {
    return realIp;
  }

  return 'unknown';
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Log Handler
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/log-error
 * Handle error logging from client
 */
export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    if (isRateLimited(clientIP)) {
      return NextResponse.json({ error: 'Too many error reports' }, { status: 429 });
    }

    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }

    // ── Validate & sanitise payload ─────────────────────────────────────
    const result = validatePayload(body);
    if (!result.ok) {
      return NextResponse.json({ error: result.error }, { status: 400 });
    }
    const sanitized = result.data;

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      logger.error('[Admin Error Log]', JSON.stringify(sanitized, null, 2));
    }

    // Create structured log entry
    const logEntry = {
      level: 'error',
      service: 'sahool-admin',
      ...sanitized,
      clientIP,
      receivedAt: new Date().toISOString(),
      requestHeaders: {
        userAgent: request.headers.get('user-agent'),
        referer: request.headers.get('referer'),
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
    logger.error('[Error Log API] Failed to process error:', error);
    return NextResponse.json({ error: 'Failed to log error' }, { status: 500 });
  }
}
