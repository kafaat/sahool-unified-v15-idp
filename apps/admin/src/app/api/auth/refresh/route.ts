/**
 * Server-side token refresh API route
 * Refreshes access token using refresh token
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { API_URL, TIMEOUT_TIERS, API_PATHS } from '@/config/api';

export async function POST(_request: NextRequest) {
  try {
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

    // Use env vars for cookie maxAge, aligned with login route (30 min default)
    const accessTokenMaxAge = parseInt(process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS || '1800', 10); // 30 minutes default - must match login route
    const refreshTokenMaxAge = parseInt(
      process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS || '604800',
      10
    ); // 7 days default

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
