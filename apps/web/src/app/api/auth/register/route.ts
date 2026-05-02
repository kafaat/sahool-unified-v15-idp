/**
 * Registration Proxy Route
 * مسار وكيل التسجيل
 *
 * Proxies the self-registration request directly to the user-service,
 * bypassing Kong (which does not yet have a /api/v1/auth/register route).
 *
 * Flow: Browser → POST /api/auth/register
 *               → user-service POST /api/v1/auth/register
 *               → JWT tokens returned for immediate login
 *
 * Kong route TODO: add the register endpoint to Kong config so
 * API_GATEWAY_URL alone is sufficient in production.
 */

import { NextRequest, NextResponse } from 'next/server';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';
import { AUTH_ENDPOINTS } from '@sahool/shared-types/contracts';

// USER_SERVICE_URL calls user-service directly, bypassing Kong.
// API_GATEWAY_URL / NEXT_PUBLIC_API_URL are kept as fallbacks for when
// Kong is configured with the register route in production.
const BACKEND_URL =
  process.env.USER_SERVICE_URL ||
  process.env.API_GATEWAY_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:3025';

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 10,
  keyPrefix: 'auth-register',
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

  const limited = await isRateLimited(ip, RATE_LIMIT_CONFIG);
  if (limited) {
    logger.warn('[Auth Register] Rate limited', { ip });
    return NextResponse.json(
      { success: false, error: 'Too many registration attempts. Please try again later.' },
      { status: 429, headers: { 'Retry-After': String(60) } }
    );
  }

  if (!BACKEND_URL) {
    logger.error('[Auth Register] Backend URL is not configured');
    return NextResponse.json({ success: false, error: 'Server configuration error' }, { status: 500 });
  }

  try {
    const body = await request.json();

    const backendResponse = await fetch(`${BACKEND_URL}${AUTH_ENDPOINTS.REGISTER}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await backendResponse.json().catch(() => ({}));

    if (!backendResponse.ok) {
      const message =
        // NestJS validation errors arrive as data.message (string or string[])
        (Array.isArray(data?.message) ? data.message[0] : data?.message) ||
        data?.error ||
        `Registration failed (${backendResponse.status})`;
      logger.warn('[Auth Register] Backend returned error', { status: backendResponse.status });
      return NextResponse.json({ success: false, error: message }, { status: backendResponse.status });
    }

    return NextResponse.json({ success: true, ...data });
  } catch (error) {
    logger.error('[Auth Register] Error:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
