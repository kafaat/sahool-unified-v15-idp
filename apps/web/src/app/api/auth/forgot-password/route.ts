/**
 * Forgot Password Proxy Route
 * مسار وكيل لنسيان كلمة المرور
 *
 * Proxies the forgot-password request to the backend auth service.
 * The Next.js server acts as a secure intermediary so no auth headers
 * need to be managed client-side.
 *
 * Flow: Browser → POST /api/auth/forgot-password
 *               → backend POST /api/v1/auth/forgot-password
 *               → Email with reset link sent
 */

import { NextRequest, NextResponse } from 'next/server';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 5, // Strict limit — prevents email enumeration
  keyPrefix: 'auth-forgot-password',
};

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

  // Rate limiting: max 5 forgot-password requests per minute per IP
  const limited = await isRateLimited(ip, RATE_LIMIT_CONFIG);
  if (limited) {
    logger.warn('[Auth ForgotPassword] Rate limited', { ip });
    return NextResponse.json(
      { success: false, error: 'Too many requests. Please try again later.' },
      { status: 429, headers: { 'Retry-After': String(60) } }
    );
  }

  if (!API_BASE_URL) {
    logger.error('[Auth ForgotPassword] NEXT_PUBLIC_API_URL is not configured');
    return NextResponse.json(
      { success: false, error: 'Server configuration error' },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();

    if (!body?.email && !body?.phone) {
      return NextResponse.json(
        { success: false, error: 'Email or phone number is required' },
        { status: 400 }
      );
    }

    const backendResponse = await fetch(`${API_BASE_URL}/api/v1/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await backendResponse.json().catch(() => ({}));

    if (!backendResponse.ok) {
      logger.warn('[Auth ForgotPassword] Backend returned error', {
        status: backendResponse.status,
      });
      return NextResponse.json(
        { success: false, error: data?.message || data?.error || 'Failed to send reset email' },
        { status: backendResponse.status }
      );
    }

    return NextResponse.json({ success: true, message: data?.message || 'Reset email sent' });
  } catch (error) {
    logger.error('[Auth ForgotPassword] Error:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
