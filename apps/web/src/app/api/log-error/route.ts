/**
 * Error Logging API Endpoint
 * نقطة نهاية API لتسجيل الأخطاء
 */

import { NextRequest, NextResponse } from 'next/server';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

interface ErrorLogPayload {
  type: string;
  message: string;
  stack?: string;
  componentStack?: string;
  url?: string;
  timestamp: string;
  environment?: string;
  context?: Record<string, unknown>;
  user?: {
    id?: string;
    email?: string;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 10,
  keyPrefix: 'error-log',
};

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

export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);

    if (rateLimited) {
      return NextResponse.json(
        { error: 'Too many error reports. Please try again later.' },
        { status: 429 }
      );
    }

    // Validate content-type before parsing JSON
    const contentType = request.headers.get('content-type');
    if (!contentType?.includes('application/json')) {
      return NextResponse.json({ error: 'Content-Type must be application/json' }, { status: 400 });
    }

    let payload: ErrorLogPayload;
    try {
      payload = await request.json();
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }

    // Validate required fields
    if (!payload.message || !payload.type) {
      return NextResponse.json(
        { error: 'Missing required fields: message, type' },
        { status: 400 }
      );
    }

    // Truncate oversized fields to prevent log flooding
    const MAX_MESSAGE_LEN = 2000;
    const MAX_STACK_LEN = 5000;
    const safeMessage = String(payload.message).slice(0, MAX_MESSAGE_LEN);
    const safeStack = payload.stack ? String(payload.stack).slice(0, MAX_STACK_LEN) : undefined;

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      logger.error('[Error Log]', JSON.stringify(payload, null, 2));
    }

    // Build log entry with explicit fields (avoid spread to prevent log injection)
    const logEntry = {
      level: 'error',
      service: 'sahool-web',
      type: String(payload.type),
      message: safeMessage,
      stack: safeStack,
      url: payload.url ? String(payload.url).slice(0, 500) : undefined,
      timestamp: payload.timestamp,
      receivedAt: new Date().toISOString(),
      requestHeaders: {
        userAgent: request.headers.get('user-agent'),
        referer: request.headers.get('referer'),
      },
    };

    // Log structured error (always log in production for server logs)
    logger.production(logEntry);

    // If you have Sentry server-side:
    // Sentry.captureException(new Error(payload.message), {
    //   extra: payload,
    // });

    return NextResponse.json({ success: true, logged: true });
  } catch (error) {
    // Critical error - always log
    logger.critical('[Error Log API] Failed to process error:', error);
    return NextResponse.json({ error: 'Failed to log error' }, { status: 500 });
  }
}
