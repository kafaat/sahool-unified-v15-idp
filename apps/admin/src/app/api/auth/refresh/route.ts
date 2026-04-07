/**
 * Server-side token refresh API route
 * Refreshes access token using refresh token
 * Includes rate limiting to prevent abuse
 *
 * يتضمن حماية ضد إساءة الاستخدام
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { API_URL, TIMEOUT_TIERS, API_PATHS } from '@/config/api';
import { checkRateLimit } from '@/lib/rate-limiter';

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
      const rateLimit = checkRateLimit(`refresh:${ip}`, {
        maxAttempts: 20,           // generous: normal clients refresh ~1/30 min
        windowMs: 5 * 60 * 1000,  // 5-minute window
        lockoutDurationMs: 10 * 60 * 1000, // 10-minute lockout
      });

      if (!rateLimit.allowed) {
        logger.warn(`Refresh rate limit exceeded for IP: ${ip}`);
        return NextResponse.json(
          { error: 'Too many refresh attempts. Please try again later.' },
          { status: 429, headers: { 'Retry-After': '600' } }
        );
      }
    }

    const cookieStore = await cookies();
    const refreshToken = cookieStore.get('sahool_admin_refresh_token')?.value;

    if (!refreshToken) {
      return NextResponse.json({ error: 'No refresh token available' }, { status: 401 });
    }

    // Call backend refresh endpoint with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}${API_PATHS.auth.refresh}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken: refreshToken }),
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
      // Refresh token is invalid or expired - clear cookies
      cookieStore.delete('sahool_admin_token');
      cookieStore.delete('sahool_admin_refresh_token');
      cookieStore.delete('sahool_admin_last_activity');

      return NextResponse.json(
        { error: data.message || data.detail || 'Token refresh failed' },
        { status: response.status }
      );
    }

    // Use env vars for cookie maxAge, aligned with login route (30 min default).
    // Guard against NaN when the env var contains a non-numeric value, matching
    // the same pattern used in the login route.
    const parsedAccess = parseInt(process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS || '1800', 10);
    const accessTokenMaxAge =
      Number.isFinite(parsedAccess) && parsedAccess > 0 ? parsedAccess : 1800; // 30 minutes default

    const parsedRefresh = parseInt(process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS || '604800', 10);
    const refreshTokenMaxAge =
      Number.isFinite(parsedRefresh) && parsedRefresh > 0 ? parsedRefresh : 604800; // 7 days default

    // Update access token
    cookieStore.set('sahool_admin_token', data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: accessTokenMaxAge,
      path: '/',
    });

    // Update refresh token (always rotated now)
    if (data.refresh_token) {
      cookieStore.set('sahool_admin_refresh_token', data.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: refreshTokenMaxAge,
        path: '/',
      });
    }

    // Update last activity
    cookieStore.set('sahool_admin_last_activity', Date.now().toString(), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: accessTokenMaxAge,
      path: '/',
    });

    // Return token so the unified client can retry the failed request
    return NextResponse.json({ success: true, token: data.access_token });
  } catch (error) {
    logger.production('Token refresh error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
