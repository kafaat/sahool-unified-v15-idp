/**
 * Verify OTP Proxy Route
 * مسار وكيل للتحقق من رمز OTP
 *
 * Proxies OTP verification to the backend. On successful login OTP,
 * sets httpOnly cookies. On password-reset OTP, returns a short-lived
 * reset_token for the reset-password step.
 *
 * Flow (login): Browser → POST /api/auth/verify-otp
 *                       → backend POST /api/v1/auth/verify-otp
 *                       → sets httpOnly access_token + refresh_token cookies
 *
 * Flow (reset):  Browser → POST /api/auth/verify-otp { purpose: "reset" }
 *                       → backend → returns JSON with reset_token
 *                       → client uses reset_token for the reset-password step
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';
import {
  AUTH_ENDPOINTS,
  OTP_PURPOSE,
  type VerifyOtpRequest,
} from '@sahool/shared-types/contracts';

const API_BASE_URL = process.env.API_GATEWAY_URL || process.env.NEXT_PUBLIC_API_URL || '';

const RATE_LIMIT_CONFIG = {
  windowMs: 60000,
  maxRequests: 10, // 10 attempts per minute per IP
  keyPrefix: 'auth-verify-otp',
};

function parseMaxAge(envValue: string | undefined, fallback: number): number {
  const parsed = parseInt(envValue || String(fallback), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

const ACCESS_TOKEN_MAX_AGE = parseMaxAge(process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS, 1800);
const REFRESH_TOKEN_MAX_AGE = parseMaxAge(process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS, 604800);

function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');
  if (forwarded) {
    const firstIp = forwarded.split(',')[0];
    return firstIp ? firstIp.trim() : 'unknown';
  }
  return realIp ?? 'unknown';
}

export async function POST(request: NextRequest) {
  const ip = getClientIP(request);

  const limited = await isRateLimited(ip, RATE_LIMIT_CONFIG);
  if (limited) {
    logger.warn('[Auth VerifyOTP] Rate limited', { ip });
    return NextResponse.json(
      { success: false, error: 'Too many verification attempts. Please try again later.' },
      { status: 429, headers: { 'Retry-After': String(60) } }
    );
  }

  if (!API_BASE_URL) {
    logger.error('[Auth VerifyOTP] NEXT_PUBLIC_API_URL is not configured');
    return NextResponse.json(
      { success: false, error: 'Server configuration error' },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();

    // Accept either `otp` (legacy client) or `otpCode` (backend DTO field)
    const otpCode = body?.otpCode ?? body?.otp;
    if (!otpCode) {
      return NextResponse.json(
        { success: false, error: 'OTP code is required' },
        { status: 400 }
      );
    }

    // Normalize payload to match backend DTO (uses `otpCode`, not `otp`)
    const backendPayload: VerifyOtpRequest = {
      identifier: body?.identifier,
      otpCode,
      purpose: body?.purpose ?? OTP_PURPOSE.LOGIN,
      ...(body?.tenantId && { tenantId: body.tenantId }),
    };

    const backendResponse = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.VERIFY_OTP}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backendPayload),
    });

    const data = await backendResponse.json().catch(() => ({}));

    if (!backendResponse.ok) {
      logger.warn('[Auth VerifyOTP] Backend returned error', { status: backendResponse.status });
      return NextResponse.json(
        {
          success: false,
          error: data?.message || data?.error || 'OTP verification failed',
          attempts_remaining: data?.attempts_remaining,
        },
        { status: backendResponse.status }
      );
    }

    const purpose = body?.purpose ?? OTP_PURPOSE.LOGIN;

    // Password-reset OTP: return the reset_token to the client (no session cookies set)
    // Backend purpose is `password_reset`; legacy clients may send `reset`.
    if (purpose === OTP_PURPOSE.PASSWORD_RESET || purpose === 'reset') {
      const resetToken = data?.reset_token ?? data?.resetToken ?? data?.token;

      if (!resetToken) {
        logger.warn('[Auth VerifyOTP] Backend response missing reset token');
        return NextResponse.json(
          { success: false, error: 'No reset token received from backend' },
          { status: 502 }
        );
      }

      return NextResponse.json({
        success: true,
        reset_token: resetToken,
        message: data?.message || 'OTP verified',
      });
    }

    // Phone verification: no session cookies, just confirm status
    if (purpose === OTP_PURPOSE.VERIFY_PHONE) {
      return NextResponse.json({
        success: true,
        verified: data?.verified ?? true,
        message: data?.message || 'Phone verified successfully',
      });
    }

    // Login OTP: set httpOnly session cookies
    const accessToken = data?.access_token ?? data?.data?.access_token;
    const refreshToken = data?.refresh_token ?? data?.data?.refresh_token;

    if (!accessToken) {
      return NextResponse.json(
        { success: false, error: 'No access token received from backend' },
        { status: 502 }
      );
    }

    const cookieStore = await cookies();
    const isSecure = process.env.NODE_ENV === 'production';

    cookieStore.set('access_token', accessToken, {
      httpOnly: true,
      secure: isSecure,
      sameSite: 'strict',
      maxAge: ACCESS_TOKEN_MAX_AGE,
      path: '/',
    });

    if (refreshToken) {
      cookieStore.set('refresh_token', refreshToken, {
        httpOnly: true,
        secure: isSecure,
        sameSite: 'strict',
        maxAge: REFRESH_TOKEN_MAX_AGE,
        path: '/',
      });
    }

    return NextResponse.json({
      success: true,
      user: data?.user ?? data?.data?.user,
      message: data?.message || 'OTP verified successfully',
    });
  } catch (error) {
    logger.error('[Auth VerifyOTP] Error:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
