/**
 * Send OTP Proxy Route
 * مسار وكيل لإرسال رمز التحقق (OTP)
 *
 * Proxies OTP send requests (SMS/WhatsApp/Telegram) to the backend.
 *
 * Flow: Browser → POST /api/auth/send-otp
 *               → backend POST /api/v1/auth/send-otp
 *               → OTP sent via configured channel (SMS/WhatsApp/Telegram)
 */

import { NextRequest, NextResponse } from 'next/server';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 5, // Strict limit — prevents OTP flooding
  keyPrefix: 'auth-send-otp',
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

  // Rate limiting: max 5 OTP requests per minute per IP
  const limited = await isRateLimited(ip, RATE_LIMIT_CONFIG);
  if (limited) {
    logger.warn('[Auth SendOTP] Rate limited', { ip });
    return NextResponse.json(
      { success: false, error: 'Too many OTP requests. Please try again later.' },
      { status: 429, headers: { 'Retry-After': String(60) } }
    );
  }

  if (!API_BASE_URL) {
    logger.error('[Auth SendOTP] NEXT_PUBLIC_API_URL is not configured');
    return NextResponse.json(
      { success: false, error: 'Server configuration error' },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();

    if (!body?.phone && !body?.email) {
      return NextResponse.json(
        { success: false, error: 'Phone number or email is required' },
        { status: 400 }
      );
    }

    const backendResponse = await fetch(`${API_BASE_URL}/api/v1/auth/send-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await backendResponse.json().catch(() => ({}));

    if (!backendResponse.ok) {
      logger.warn('[Auth SendOTP] Backend returned error', { status: backendResponse.status });
      return NextResponse.json(
        { success: false, error: data?.message || data?.error || 'Failed to send OTP' },
        { status: backendResponse.status }
      );
    }

    return NextResponse.json({
      success: true,
      message: data?.message || 'OTP sent successfully',
      expires_in: data?.expires_in,
    });
  } catch (error) {
    logger.error('[Auth SendOTP] Error:', error);
    return NextResponse.json({ success: false, error: 'Internal server error' }, { status: 500 });
  }
}
