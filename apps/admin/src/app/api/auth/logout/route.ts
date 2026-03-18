/**
 * Server-side logout API route
 * Clears httpOnly cookies and revokes JWT token
 */

import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { logger } from "@/lib/logger";
import { API_URL, TIMEOUT_TIERS, API_PATHS } from "@/config/api";

export async function POST(_request: Request) {
  try {
    const cookieStore = await cookies();

    // Get the access token from cookies
    const accessToken = cookieStore.get("sahool_admin_token")?.value;

    // Call backend to revoke the token if it exists
    if (accessToken) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_TIERS.default);

      try {
        const response = await fetch(`${API_URL}${API_PATHS.auth.logout}`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          signal: controller.signal,
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
      } finally {
        clearTimeout(timeoutId);
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
