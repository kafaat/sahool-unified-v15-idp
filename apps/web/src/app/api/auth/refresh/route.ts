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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

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
    const backendResponse = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!backendResponse.ok) {
      // Refresh failed — clear cookies
      cookieStore.delete('access_token');
      cookieStore.delete('refresh_token');
      return NextResponse.json({ success: false, error: 'Token refresh failed' }, { status: 401 });
    }

    const data = await backendResponse.json();
    const newAccessToken = data?.access_token ?? data?.data?.access_token ?? null;

    if (!newAccessToken) {
      return NextResponse.json(
        { success: false, error: 'No access token in refresh response' },
        { status: 401 }
      );
    }

    // Parse env var for cookie maxAge
    const maxAge = parseInt(process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS || '1800', 10);

    // Set new httpOnly access_token cookie
    cookieStore.set('access_token', newAccessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: Number.isFinite(maxAge) && maxAge > 0 ? maxAge : 1800,
      path: '/',
    });

    return NextResponse.json({
      success: true,
      access_token: newAccessToken,
    });
  } catch (error) {
    logger.error('[Auth Refresh API] Error refreshing token:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
