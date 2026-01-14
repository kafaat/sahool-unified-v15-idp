/**
 * Server-side logout API route
 * Clears httpOnly cookies and revokes JWT token
 */

import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { logger } from "@/lib/logger";

export async function POST(request: Request) {
  try {
    const cookieStore = await cookies();

    // Get the access token from cookies
    const accessToken = cookieStore.get("sahool_admin_token")?.value;

    // Call backend to revoke the token if it exists
    if (accessToken) {
      try {
        const backendUrl =
          process.env.USER_SERVICE_URL || "http://localhost:3025";
        const response = await fetch(`${backendUrl}/api/v1/auth/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          logger.error("Backend logout failed:", await response.text());
          // Continue with cookie deletion even if backend logout fails
        } else {
          logger.log("Token revoked successfully on backend");
        }
      } catch (backendError) {
        // Log error but continue with cookie deletion
        logger.error("Failed to revoke token on backend:", backendError);
        // Don't fail the entire logout if backend is unreachable
      }
    }

    // Clear all auth-related cookies
    cookieStore.delete("sahool_admin_token");
    cookieStore.delete("sahool_admin_refresh_token");
    cookieStore.delete("sahool_admin_last_activity");

    return NextResponse.json({
      success: true,
      message: "Logged out successfully",
    });
  } catch (error) {
    logger.error("Logout error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
