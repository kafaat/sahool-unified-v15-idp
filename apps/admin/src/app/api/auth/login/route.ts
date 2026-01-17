/**
 * Server-side login API route
 * Sets httpOnly cookies for security
 *
 * Includes rate limiting to prevent brute force attacks:
 * - 5 attempts per 15 minutes per IP address
 * - 5 attempts per 15 minutes per email address
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { logger } from "@/lib/logger";
import { API_URL, API_ENDPOINTS } from "@/config/api";

// ═══════════════════════════════════════════════════════════════════════════
// Rate Limiting Configuration
// ═══════════════════════════════════════════════════════════════════════════

const RATE_LIMIT_WINDOW = 15 * 60 * 1000; // 15 minutes in milliseconds
const MAX_ATTEMPTS = 5; // Maximum attempts per window

// Separate maps for IP-based and email-based rate limiting
const ipAttempts = new Map<string, { count: number; resetTime: number }>();
const emailAttempts = new Map<string, { count: number; resetTime: number }>();

// ═══════════════════════════════════════════════════════════════════════════
// Rate Limiting Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if an identifier (IP or email) is rate limited
 * Returns remaining seconds until reset if rate limited, or 0 if not limited
 */
function checkRateLimit(
  map: Map<string, { count: number; resetTime: number }>,
  identifier: string,
): { isLimited: boolean; retryAfter: number } {
  const now = Date.now();
  const record = map.get(identifier);

  // No record or expired - create/reset entry
  if (!record || now > record.resetTime) {
    map.set(identifier, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return { isLimited: false, retryAfter: 0 };
  }

  // Check if limit exceeded
  if (record.count >= MAX_ATTEMPTS) {
    const retryAfter = Math.ceil((record.resetTime - now) / 1000);
    return { isLimited: true, retryAfter };
  }

  // Increment count
  record.count++;
  return { isLimited: false, retryAfter: 0 };
}

/**
 * Get client IP address from request headers
 */
function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get("x-forwarded-for");
  const realIp = request.headers.get("x-real-ip");

  if (forwarded) {
    const firstIp = forwarded.split(",")[0];
    return firstIp ? firstIp.trim() : "unknown";
  }

  if (realIp) {
    return realIp;
  }

  return "unknown";
}

/**
 * Normalize email for consistent rate limiting
 * (lowercase, trim whitespace)
 */
function normalizeEmail(email: string): string {
  return email.toLowerCase().trim();
}

// ═══════════════════════════════════════════════════════════════════════════
// Periodic Cleanup
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Clean up expired rate limit entries every 5 minutes
 * Prevents memory leaks from accumulated stale entries
 */
setInterval(
  () => {
    const now = Date.now();

    for (const [key, record] of ipAttempts.entries()) {
      if (now > record.resetTime) {
        ipAttempts.delete(key);
      }
    }

    for (const [key, record] of emailAttempts.entries()) {
      if (now > record.resetTime) {
        emailAttempts.delete(key);
      }
    }
  },
  5 * 60 * 1000,
); // Run every 5 minutes

// ═══════════════════════════════════════════════════════════════════════════
// Login Handler
// ═══════════════════════════════════════════════════════════════════════════

export async function POST(request: NextRequest) {
  try {
    // Get client IP for rate limiting
    const clientIP = getClientIP(request);

    // Check IP-based rate limit first (before parsing body)
    const ipCheck = checkRateLimit(ipAttempts, clientIP);
    if (ipCheck.isLimited) {
      logger.warn("Login rate limit exceeded (IP)", {
        ip: clientIP,
        retryAfter: ipCheck.retryAfter,
      });
      return NextResponse.json(
        {
          error: "Too many login attempts. Please try again later.",
          error_ar: "محاولات تسجيل دخول كثيرة جدًا. يرجى المحاولة لاحقًا.",
        },
        {
          status: 429,
          headers: {
            "Retry-After": ipCheck.retryAfter.toString(),
            "X-RateLimit-Limit": MAX_ATTEMPTS.toString(),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": Math.ceil(
              (Date.now() + ipCheck.retryAfter * 1000) / 1000,
            ).toString(),
          },
        },
      );
    }

    const body = await request.json();
    const { email, password, totp_code } = body;

    // Check email-based rate limit (after parsing body)
    if (email && typeof email === "string") {
      const normalizedEmail = normalizeEmail(email);
      const emailCheck = checkRateLimit(emailAttempts, normalizedEmail);
      if (emailCheck.isLimited) {
        logger.warn("Login rate limit exceeded (email)", {
          email: normalizedEmail,
          ip: clientIP,
          retryAfter: emailCheck.retryAfter,
        });
        return NextResponse.json(
          {
            error: "Too many login attempts for this account. Please try again later.",
            error_ar:
              "محاولات تسجيل دخول كثيرة جدًا لهذا الحساب. يرجى المحاولة لاحقًا.",
          },
          {
            status: 429,
            headers: {
              "Retry-After": emailCheck.retryAfter.toString(),
              "X-RateLimit-Limit": MAX_ATTEMPTS.toString(),
              "X-RateLimit-Remaining": "0",
              "X-RateLimit-Reset": Math.ceil(
                (Date.now() + emailCheck.retryAfter * 1000) / 1000,
              ).toString(),
            },
          },
        );
      }
    }

    // Forward to backend auth API
    const response = await fetch(`${API_URL}${API_ENDPOINTS.auth.login}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
        ...(totp_code && { totp_code }),
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.message || data.detail || "Login failed" },
        { status: response.status },
      );
    }

    // If 2FA required, return temp token
    if (data.requires_2fa) {
      return NextResponse.json({
        requires_2fa: true,
        temp_token: data.temp_token,
      });
    }

    // Set secure httpOnly cookies
    const cookieStore = await cookies();

    // Access token - 1 day expiry
    cookieStore.set("sahool_admin_token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 86400, // 1 day in seconds
      path: "/",
    });

    // Refresh token if provided - 7 days expiry
    if (data.refresh_token) {
      cookieStore.set("sahool_admin_refresh_token", data.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
        maxAge: 604800, // 7 days in seconds
        path: "/",
      });
    }

    // Last activity timestamp for idle timeout tracking
    cookieStore.set("sahool_admin_last_activity", Date.now().toString(), {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 86400, // 1 day
      path: "/",
    });

    return NextResponse.json({
      success: true,
      user: data.user,
    });
  } catch (error) {
    logger.error("Login error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
