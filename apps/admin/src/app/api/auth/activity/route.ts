/**
 * Server-side activity tracking API route
 * Updates last activity timestamp for idle timeout
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';
import { AUTH_ENDPOINTS } from '@sahool/shared-types/contracts';

export async function POST() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;

    if (!token) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    }

    const expireSeconds = Number(process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS) || 1800;

    // Update last activity timestamp (aligned with JWT expiry)
    cookieStore.set('sahool_admin_last_activity', Date.now().toString(), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: expireSeconds,
      path: '/',
    });

    // Forward activity to backend for server-side audit trail (fire-and-forget)
    const apiUrl = process.env.API_GATEWAY_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    fetch(`${apiUrl}${AUTH_ENDPOINTS.ACTIVITY}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000),
    }).catch(() => {
      // Best-effort — don't block client on backend activity tracking
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    logger.error('Activity update error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
