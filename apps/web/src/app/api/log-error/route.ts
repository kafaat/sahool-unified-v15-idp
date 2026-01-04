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

    const payload: ErrorLogPayload = await request.json();

    // Validate required fields
    if (!payload.message || !payload.type) {
      return NextResponse.json(
        { error: 'Missing required fields: message, type' },
        { status: 400 }
      );
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      logger.error('[Error Log]', JSON.stringify(payload, null, 2));
    }

    // In production, you would:
    // 1. Send to external logging service (e.g., LogRocket, Datadog, Sentry)
    // 2. Store in database for analysis
    // 3. Send alerts for critical errors

    // Example: Store error in structured log format
    const logEntry = {
      level: 'error',
      service: 'sahool-web',
      ...payload,
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
    return NextResponse.json(
      { error: 'Failed to log error' },
      { status: 500 }
    );
  }
}
