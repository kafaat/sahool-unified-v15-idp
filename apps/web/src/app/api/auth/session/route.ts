/**
 * Authentication Session API Endpoint
 * نقطة نهاية API لجلسة المصادقة
 *
 * Handles secure cookie setting with httpOnly flag to prevent XSS attacks
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface SetSessionRequest {
  access_token: string;
  refresh_token?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const ACCESS_TOKEN_COOKIE = 'access_token';
const REFRESH_TOKEN_COOKIE = 'refresh_token';
const ACCESS_TOKEN_MAX_AGE = 7 * 24 * 60 * 60; // 7 days in seconds
const REFRESH_TOKEN_MAX_AGE = 30 * 24 * 60 * 60; // 30 days in seconds

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 20, // Allow reasonable number of auth requests
  keyPrefix: 'auth-session',
};

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get client IP address for rate limiting
 */
function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');

  if (forwarded) {
    const firstIp = forwarded.split(',')[0];
    return firstIp ? firstIp.trim() : 'unknown';
  }

  if (realIp) {
    return realIp;
  }

  return 'unknown';
}

/**
 * Validate token format (basic validation)
 */
function isValidToken(token: string): boolean {
  // Basic validation: token should be a non-empty string with reasonable length
  if (!token || typeof token !== 'string') {
    return false;
  }

  // Token should be at least 20 characters (prevents trivial tokens)
  if (token.length < 20) {
    return false;
  }

  // Token should not be excessively long (prevents abuse)
  if (token.length > 2048) {
    return false;
  }

  return true;
}

// ═══════════════════════════════════════════════════════════════════════════
// POST: Set Session Cookie
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Sets a secure session cookie with httpOnly flag
 *
 * Security features:
 * - httpOnly: true (prevents JavaScript access, mitigates XSS)
 * - secure: true (requires HTTPS in production)
 * - sameSite: 'strict' (prevents CSRF attacks)
 */
export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);

    if (rateLimited) {
      return NextResponse.json(
        { success: false, error: 'Too many requests. Please try again later.' },
        { status: 429 }
      );
    }

    // Parse request body
    const body: SetSessionRequest = await request.json();

    // Validate access token
    if (!body.access_token || !isValidToken(body.access_token)) {
      return NextResponse.json(
        { success: false, error: 'Invalid access token' },
        { status: 400 }
      );
    }

    // Get cookie store
    const cookieStore = await cookies();

    // Set secure access token cookie with httpOnly flag
    cookieStore.set(ACCESS_TOKEN_COOKIE, body.access_token, {
      httpOnly: true,           // Prevents JavaScript access (XSS protection)
      secure: process.env.NODE_ENV === 'production', // HTTPS only in production
      sameSite: 'strict',       // CSRF protection
      maxAge: ACCESS_TOKEN_MAX_AGE, // 7 days
      path: '/',                // Available across entire app
    });

    // Set refresh token cookie if provided
    if (body.refresh_token && isValidToken(body.refresh_token)) {
      cookieStore.set(REFRESH_TOKEN_COOKIE, body.refresh_token, {
        httpOnly: true,           // Prevents JavaScript access (XSS protection)
        secure: process.env.NODE_ENV === 'production', // HTTPS only in production
        sameSite: 'strict',       // CSRF protection
        maxAge: REFRESH_TOKEN_MAX_AGE, // 30 days
        path: '/',                // Available across entire app
      });
    }

    return NextResponse.json({
      success: true,
      message: 'Session created successfully'
    });

  } catch (error) {
    console.error('[Auth Session API] Error setting session:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to set session' },
      { status: 500 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// DELETE: Remove Session Cookie
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Removes the session cookie (logout)
 */
export async function DELETE(request: NextRequest) {
  try {
    // Rate limiting (lighter for logout)
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, {
      ...RATE_LIMIT_CONFIG,
      maxRequests: 30,
    });

    if (rateLimited) {
      return NextResponse.json(
        { success: false, error: 'Too many requests. Please try again later.' },
        { status: 429 }
      );
    }

    // Get cookie store
    const cookieStore = await cookies();

    // Remove both cookies
    cookieStore.delete(ACCESS_TOKEN_COOKIE);
    cookieStore.delete(REFRESH_TOKEN_COOKIE);

    return NextResponse.json({
      success: true,
      message: 'Session removed successfully'
    });

  } catch (error) {
    console.error('[Auth Session API] Error removing session:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to remove session' },
      { status: 500 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// GET: Check Session Status
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if session cookie exists (without exposing the token)
 */
export async function GET() {
  try {
    const cookieStore = await cookies();
    const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE);
    const refreshToken = cookieStore.get(REFRESH_TOKEN_COOKIE);

    return NextResponse.json({
      success: true,
      hasSession: !!accessToken,
      hasRefreshToken: !!refreshToken,
    });

  } catch (error) {
    console.error('[Auth Session API] Error checking session:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to check session' },
      { status: 500 }
    );
  }
}
