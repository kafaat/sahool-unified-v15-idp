/**
 * Server-side current user API route
 * Proxies request to backend with httpOnly cookie token
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { API_URL, TIMEOUT_TIERS, API_PATHS } from '@/config/api';

export async function GET(_request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;

    if (!token) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    }

    // Forward request to backend API with token and timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}${API_PATHS.auth.me}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
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
      // Token might be expired or invalid - clear cookies
      if (response.status === 401) {
        const logoutResponse = NextResponse.json(
          { error: data.message || data.detail || 'Unauthorized' },
          { status: 401 }
        );
        logoutResponse.cookies.delete('sahool_admin_token');
        logoutResponse.cookies.delete('sahool_admin_refresh_token');
        logoutResponse.cookies.delete('sahool_admin_last_activity');
        return logoutResponse;
      }

      return NextResponse.json(
        { error: data.message || data.detail || 'Failed to fetch user' },
        { status: response.status }
      );
    }

    return NextResponse.json({
      success: true,
      data: data,
    });
  } catch (error) {
    logger.production('Get current user error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
