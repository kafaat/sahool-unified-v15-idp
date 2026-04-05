/**
 * Admin Sessions API — List active sessions
 * واجهة API للجلسات الإدارية — عرض الجلسات النشطة
 *
 * GET /api/admin/sessions
 *
 * Proxies to the user-service sessions endpoint with the admin's auth token
 * from the httpOnly cookie, so the client never handles the token directly.
 *
 * Role requirement: admin only (enforced by middleware via PROTECTED_ROUTES).
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { API_URL, TIMEOUT_TIERS } from '@/config/api';

export async function GET() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;

    if (!token) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}/api/v1/users/sessions`, {
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

    if (!response.ok) {
      // Backend may not yet expose this endpoint — return a graceful empty list
      // so the UI shows "no active sessions" instead of an unhandled error.
      if (response.status === 404) {
        return NextResponse.json({ sessions: [] });
      }

      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.message || errorData.detail || 'Failed to fetch sessions' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    logger.error('Sessions fetch error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
