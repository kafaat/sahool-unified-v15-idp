/**
 * Server-side token refresh API route
 * Refreshes access token using refresh token
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const refreshToken = cookieStore.get("sahool_admin_refresh_token")?.value;

    if (!refreshToken) {
      return NextResponse.json(
        { error: "No refresh token available" },
        { status: 401 },
      );
    }

    // Call backend refresh endpoint
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refreshToken: refreshToken }),
    });

    const data = await response.json();

    if (!response.ok) {
      // Refresh token is invalid or expired - clear cookies
      cookieStore.delete("sahool_admin_token");
      cookieStore.delete("sahool_admin_refresh_token");
      cookieStore.delete("sahool_admin_last_activity");

      return NextResponse.json(
        { error: data.message || data.detail || "Token refresh failed" },
        { status: response.status },
      );
    }

    // Update access token
    cookieStore.set("sahool_admin_token", data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 86400, // 1 day
      path: "/",
    });

    // Update refresh token (always rotated now)
    if (data.refresh_token) {
      cookieStore.set("sahool_admin_refresh_token", data.refresh_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
        maxAge: 604800, // 7 days
        path: "/",
      });
    }

    // Update last activity
    cookieStore.set("sahool_admin_last_activity", Date.now().toString(), {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 86400, // 1 day
      path: "/",
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Token refresh error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
