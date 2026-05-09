/**
 * Token Refresh Proxy Route
 * مسار وكيل لتجديد التوكن
 *
 * Server-side proxy that reads the httpOnly refresh_token cookie
 * and forwards it to the backend auth service. This is required
 * because httpOnly cookies cannot be read by client-side JavaScript.
 *
 * Flow: Browser → this route (reads httpOnly cookie) → backend /api/v1/auth/refresh
 *       → sets new httpOnly access_token cookie → returns success/failure
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { isRateLimited } from '@/lib/rate-limiter';
import { AUTH_ENDPOINTS } from '@sahool/shared-types/contracts';

const API_BASE_URL = process.env.API_GATEWAY_URL || process.env.NEXT_PUBLIC_API_URL || '';

export async function POST(request: NextRequest) {
  try {
    // Rate limiting — keyed on client IP to prevent refresh-token abuse
    // Skip rate limiting when IP cannot be determined to avoid a shared
    // 'unknown' bucket that could unfairly throttle unrelated clients.
    const ip =
      request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
      request.headers.get('x-real-ip') ||
      '';

    if (ip) {
      const limited = await isRateLimited(ip, {
        keyPrefix: 'refresh',
        maxRequests: 20,          // generous: normal clients refresh ~1/30 min
        windowMs: 5 * 60 * 1000,  // 5-minute window
      });

      if (limited) {
        logger.error(`[Auth Refresh API] Rate limit exceeded for IP: ${ip}`);
        return NextResponse.json(
          { success: false, error: 'Too many refresh attempts. Please try again later.' },
          { status: 429, headers: { 'Retry-After': '300' } }
        );
      }
    }

    if (!API_BASE_URL) {
      logger.error('[Auth Refresh API] NEXT_PUBLIC_API_URL is not configured');
      return NextResponse.json(
        { success: false, error: 'Server configuration error' },
        { status: 500 }
      );
    }

    const cookieStore = await cookies();
    const refreshToken = cookieStore.get('refresh_token')?.value;

    if (!refreshToken) {
      return NextResponse.json({ success: false, error: 'No refresh token' }, { status: 401 });
    }

    // Forward refresh request to the backend
    // NestJS RefreshTokenDto expects camelCase `refreshToken` (whitelist: true strips unknown keys)
    const backendResponse = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.REFRESH}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken }),
    });

    if (!backendResponse.ok) {
      // Refresh failed — clear cookies directly on the response object so the
      // browser receives the Set-Cookie headers that expire the old tokens.
      const failResponse = NextResponse.json(
        { success: false, error: 'Token refresh failed' },
        { status: 401 }
      );
      failResponse.cookies.delete('access_token');
      failResponse.cookies.delete('refresh_token');
      return failResponse;
    }

    const data = await backendResponse.json();
    const newAccessToken = data?.access_token ?? data?.data?.access_token ?? null;
    const newRefreshToken = data?.refresh_token ?? data?.data?.refresh_token ?? null;

    if (!newAccessToken) {
      return NextResponse.json(
        { success: false, error: 'No access token in refresh response' },
        { status: 401 }
      );
    }

    const isProduction = process.env.NODE_ENV === 'production';

    // Parse env vars for cookie maxAge
    const accessMaxAge = parseInt(process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS || '1800', 10);
    const refreshMaxAge = parseInt(
      process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS ||
        String((parseInt(process.env.JWT_REFRESH_TOKEN_EXPIRE_DAYS || '7', 10) * 86400)),
      10
    );

    // Set new httpOnly tokens directly on the NextResponse so the Set-Cookie
    // headers are guaranteed to be present. Using cookies().set() in a Route
    // Handler does NOT automatically merge into a NextResponse object returned
    // from the same handler — they are different response objects.
    const response = NextResponse.json({
      success: true,
      access_token: newAccessToken,
    });

    response.cookies.set('access_token', newAccessToken, {
      httpOnly: true,
      secure: isProduction,
      sameSite: 'strict',
      maxAge: Number.isFinite(accessMaxAge) && accessMaxAge > 0 ? accessMaxAge : 1800,
      path: '/',
    });

    // Persist the rotated refresh token; if omitted the old (now-invalidated)
    // token stays in the cookie and the next refresh triggers "token reuse detected".
    if (newRefreshToken) {
      response.cookies.set('refresh_token', newRefreshToken, {
        httpOnly: true,
        secure: isProduction,
        sameSite: 'strict',
        maxAge: Number.isFinite(refreshMaxAge) && refreshMaxAge > 0 ? refreshMaxAge : 604800,
        path: '/',
      });
    }

    return response;
  } catch (error) {
    logger.error('[Auth Refresh API] Error refreshing token:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
