/**
 * Reset Password Proxy Route
 * مسار وكيل لإعادة تعيين كلمة المرور
 *
 * Accepts a reset_token (from the OTP verify step) plus a new password,
 * proxies the request to the backend, and on success clears any stale
 * auth cookies so the user is forced to log in with the new password.
 *
 * Flow: Browser → POST /api/auth/reset-password { token, password, confirm_password }
 *               → backend POST /api/v1/auth/reset-password
 *               → clears access_token + refresh_token cookies
 *               → client redirects to /login
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

const RATE_LIMIT_CONFIG = {
  windowMs: 60000,
  maxRequests: 5,
  keyPrefix: 'auth-reset-password',
};

/** Minimum password strength: at least 8 chars */
function isStrongPassword(password: string): boolean {
  return typeof password === 'string' && password.length >= 8;
}

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
    logger.warn('[Auth ResetPassword] Rate limited', { ip });
    return NextResponse.json(
      { success: false, error: 'Too many requests. Please try again later.' },
      { status: 429, headers: { 'Retry-After': String(60) } }
    );
  }

  if (!API_BASE_URL) {
    logger.error('[Auth ResetPassword] NEXT_PUBLIC_API_URL is not configured');
    return NextResponse.json(
      { success: false, error: 'Server configuration error' },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();

    if (!body?.token) {
      return NextResponse.json(
        { success: false, error: 'Reset token is required' },
        { status: 400 }
      );
    }

    if (!body?.password) {
      return NextResponse.json(
        { success: false, error: 'New password is required' },
        { status: 400 }
      );
    }

    if (!isStrongPassword(body.password)) {
      return NextResponse.json(
        { success: false, error: 'Password must be at least 8 characters' },
        { status: 400 }
      );
    }

    if (body.confirm_password && body.confirm_password !== body.password) {
      return NextResponse.json(
        { success: false, error: 'Passwords do not match' },
        { status: 400 }
      );
    }

    const backendResponse = await fetch(`${API_BASE_URL}/api/v1/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: body.token,
        password: body.password,
        confirm_password: body.confirm_password,
      }),
    });

    const data = await backendResponse.json().catch(() => ({}));

    if (!backendResponse.ok) {
      logger.warn('[Auth ResetPassword] Backend returned error', {
        status: backendResponse.status,
      });
      return NextResponse.json(
        {
          success: false,
          error: data?.message || data?.error || 'Password reset failed',
        },
        { status: backendResponse.status }
      );
    }

    // Clear any stale auth cookies — user must log in with new password
    const cookieStore = await cookies();
    cookieStore.delete({ name: 'access_token', path: '/' });
    cookieStore.delete({ name: 'refresh_token', path: '/' });

    return NextResponse.json({
      success: true,
      message: data?.message || 'Password reset successfully',
    });
  } catch (error) {
    logger.error('[Auth ResetPassword] Error:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
