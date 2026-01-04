/**
 * Error Logging API Endpoint - Admin Dashboard
 * نقطة نهاية API لتسجيل الأخطاء - لوحة التحكم
 */

import { NextRequest, NextResponse } from 'next/server';
import { logger } from '../../../lib/logger';

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
      return NextResponse.json(
        { error: 'Too many error reports' },
        { status: 429 }
      );
    }

    const payload: ErrorLogPayload = await request.json();

    // Validate required fields
    if (!payload.message || !payload.timestamp) {
      return NextResponse.json(
        { error: 'Missing required fields: message, timestamp' },
        { status: 400 }
      );
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      logger.error('[Admin Error Log]', JSON.stringify(payload, null, 2));
    }

    // Create structured log entry
    const logEntry = {
      level: 'error',
      service: 'sahool-admin',
      ...payload,
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
    return NextResponse.json(
      { error: 'Failed to log error' },
      { status: 500 }
    );
  }
}
