/**
 * WebSocket Token API Endpoint
 * نقطة نهاية API لتوكن WebSocket
 *
 * Provides a short-lived token for WebSocket authentication
 * The token is extracted from the httpOnly cookie and returned for WebSocket use
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { isRateLimited } from "@/lib/rate-limiter";

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const ACCESS_TOKEN_COOKIE = "access_token";

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 30, // Allow reasonable number of WebSocket token requests
  keyPrefix: "ws-token",
};

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get client IP address for rate limiting
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
 * Extract tenant_id from JWT token payload (basic decode without verification)
 * Note: Full verification happens on the WebSocket server
 */
function extractTenantId(token: string): string | null {
  try {
    // JWT tokens are base64url encoded with 3 parts separated by dots
    const parts = token.split(".");
    if (parts.length !== 3) {
      return null;
    }

    // Get payload part (second part) with null check for TypeScript strict mode
    const payloadPart = parts[1];
    if (!payloadPart) {
      return null;
    }

    // Decode the payload
    const payload = JSON.parse(
      Buffer.from(payloadPart, "base64url").toString("utf-8"),
    );

    return payload.tenant_id || null;
  } catch {
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// GET: Get WebSocket Token
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Returns the access token for WebSocket authentication
 *
 * SECURITY NOTE: This endpoint exposes the token to client-side JavaScript,
 * but only for the purpose of WebSocket authentication. The token is:
 * - Rate limited to prevent abuse
 * - Only accessible to authenticated users (must have valid httpOnly cookie)
 * - Used for WebSocket connections which cannot use httpOnly cookies
 */
export async function GET(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);

    if (rateLimited) {
      return NextResponse.json(
        { success: false, error: "Too many requests. Please try again later." },
        { status: 429 },
      );
    }

    // Get access token from httpOnly cookie
    const cookieStore = await cookies();
    const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE);

    if (!accessToken || !accessToken.value) {
      return NextResponse.json(
        { success: false, error: "No active session" },
        { status: 401 },
      );
    }

    // Extract tenant_id from token for WebSocket connection
    const tenantId = extractTenantId(accessToken.value);

    return NextResponse.json({
      success: true,
      token: accessToken.value,
      tenant_id: tenantId,
    });
  } catch (error) {
    console.error("[WS Token API] Error getting WebSocket token:", error);
    return NextResponse.json(
      { success: false, error: "Failed to get WebSocket token" },
      { status: 500 },
    );
  }
}
