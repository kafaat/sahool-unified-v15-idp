/**
 * Server-side activity tracking API route
 * Updates last activity timestamp for idle timeout
 *
 * SECURITY: This endpoint verifies JWT token validity before updating activity
 * to prevent malicious actors from keeping invalid sessions alive.
 */

import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { logger } from "@/lib/logger";
import { verifyToken, isTokenExpired } from "@/lib/auth/jwt-verify";

export async function POST() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("sahool_admin_token")?.value;

    if (!token) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    // SECURITY: Verify token is valid and not expired before updating activity
    // This prevents malicious actors from keeping invalid sessions alive
    if (isTokenExpired(token)) {
      return NextResponse.json({ error: "Token expired" }, { status: 401 });
    }

    try {
      // Verify the token signature is valid
      await verifyToken(token);
    } catch {
      return NextResponse.json({ error: "Invalid token" }, { status: 401 });
    }

    // Update last activity timestamp
    cookieStore.set("sahool_admin_last_activity", Date.now().toString(), {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 86400, // 1 day
      path: "/",
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    logger.error("Activity update error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
