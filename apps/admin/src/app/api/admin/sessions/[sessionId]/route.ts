/**
 * Admin Sessions API — Revoke a specific session
 * واجهة API للجلسات الإدارية — إلغاء جلسة محددة
 *
 * DELETE /api/admin/sessions/[sessionId]
 *
 * Proxies the revoke request to the user-service with the admin's auth token
 * from the httpOnly cookie.
 *
 * Role requirement: admin only (enforced by middleware via PROTECTED_ROUTES).
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { API_URL, TIMEOUT_TIERS } from '@/config/api';

interface RouteParams {
  params: Promise<{ sessionId: string }>;
}

export async function DELETE(_request: NextRequest, { params }: RouteParams) {
  try {
    const { sessionId } = await params;

    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID is required' }, { status: 400 });
    }

    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;

    if (!token) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

    let response: Response;
    try {
      response = await fetch(`${API_URL}/api/v1/users/sessions/${encodeURIComponent(sessionId)}`, {
        method: 'DELETE',
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
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.message || errorData.detail || 'Failed to revoke session' },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    logger.error('Session revoke error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
