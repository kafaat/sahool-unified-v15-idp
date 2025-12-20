/**
 * Error Logging API Endpoint
 * نقطة نهاية API لتسجيل الأخطاء
 */

import { NextRequest, NextResponse } from 'next/server';

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

export async function POST(request: NextRequest) {
  try {
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
      console.error('[Error Log]', JSON.stringify(payload, null, 2));
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

    // Log structured error
    console.error(JSON.stringify(logEntry));

    // If you have Sentry server-side:
    // Sentry.captureException(new Error(payload.message), {
    //   extra: payload,
    // });

    return NextResponse.json({ success: true, logged: true });
  } catch (error) {
    console.error('[Error Log API] Failed to process error:', error);
    return NextResponse.json(
      { error: 'Failed to log error' },
      { status: 500 }
    );
  }
}
