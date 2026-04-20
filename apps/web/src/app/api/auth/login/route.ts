/**
 * Login Proxy Route
 * مسار وكيل لتسجيل الدخول
 *
 * Proxies login requests to the backend user-service via Kong, server-side.
 * Sets httpOnly cookies on success so tokens are never exposed to client JS.
 * Eliminates the browser→Kong CORS issue (browser now calls same-origin /api/auth/login).
 *
 * Flow: Browser → POST /api/auth/login
 *              → backend POST /api/v1/auth/login (server-to-server, no CORS)
 *              → sets httpOnly access_token + refresh_token cookies
 *              → returns { access_token, refresh_token, user, ... }
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';
import { AUTH_ENDPOINTS } from '@sahool/shared-types/contracts';

const API_BASE_URL = process.env.API_GATEWAY_URL || process.env.NEXT_PUBLIC_API_URL || '';

const RATE_LIMIT_CONFIG = {
  windowMs: 60000,
  maxRequests: 10, // 10 login attempts per minute per IP
  keyPrefix: 'auth-login',
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
    logger.warn('[Auth Login] Rate limited', { ip });
    return NextResponse.json(
      { success: false, error: 'Too many login attempts. Please try again later.' },
      { status: 429, headers: { 'Retry-After': '60' } }
    );
  }

  if (!API_BASE_URL) {
    logger.error('[Auth Login] NEXT_PUBLIC_API_URL is not configured');
    return NextResponse.json({ success: false, error: 'Server configuration error' }, { status: 500 });
  }

  try {
    const body = await request.json();

    const backendResponse = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.LOGIN}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await backendResponse.json().catch(() => ({}));

    if (!backendResponse.ok) {
      logger.warn('[Auth Login] Backend error', { status: backendResponse.status });
      return NextResponse.json(
        { success: false, error: data?.message || data?.error || 'Invalid credentials' },
        { status: backendResponse.status }
      );
    }

    const accessToken = data?.access_token;
    const refreshToken = data?.refresh_token;

    if (!accessToken) {
      logger.error('[Auth Login] No access token in backend response');
      return NextResponse.json(
        { success: false, error: 'Authentication failed: no token received' },
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

    // Return the full backend payload so the auth store can finalize session setup
    return NextResponse.json(data);
  } catch (error) {
    logger.error('[Auth Login] Unexpected error:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
