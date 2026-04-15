/**
 * Server-side verify OTP proxy route
 * Routes request through Next.js server to Kong gateway
 *
 * مسار الخادم للتحقق من رمز OTP
 */

import { NextRequest, NextResponse } from 'next/server';
import { logger } from '@/lib/logger';
import { API_URL, TIMEOUT_TIERS } from '@/config/api';
import {
  AUTH_ENDPOINTS,
  OTP_PURPOSE,
  type VerifyOtpRequest,
} from '@sahool/shared-types/contracts';
import { checkRateLimit } from '@/lib/rate-limiter';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { identifier, purpose } = body;
    // Backend DTO expects `otpCode`; accept legacy `otp` from older clients.
    const otpCode = body?.otpCode ?? body?.otp;

    if (!identifier || !otpCode) {
      return NextResponse.json({ error: 'Identifier and OTP are required' }, { status: 400 });
    }

    // Build canonical backend payload matching the user-service DTO.
    // `channel` is never consumed by verify-otp (only by send-otp) so drop it.
    const backendPayload: VerifyOtpRequest = {
      identifier,
      otpCode,
      purpose: purpose ?? OTP_PURPOSE.LOGIN,
      ...(body?.tenantId && { tenantId: body.tenantId }),
    };

    // Rate limiting: 5 attempts per 15 minutes
    const rateLimit = checkRateLimit(`verify-otp:${identifier}`, {
      maxAttempts: 5,
      windowMs: 15 * 60 * 1000,
      lockoutDurationMs: 30 * 60 * 1000,
    });

    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: rateLimit.message || 'Too many verification attempts',
          resetTime: rateLimit.resetTime,
        },
        { status: 429 }
      );
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}${AUTH_ENDPOINTS.VERIFY_OTP}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(backendPayload),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    const contentType = response.headers.get('content-type');
    if (!contentType?.includes('application/json')) {
      return NextResponse.json({ error: 'Invalid response from backend' }, { status: 502 });
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.message || data.detail || 'OTP verification failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    logger.production('Verify OTP error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
