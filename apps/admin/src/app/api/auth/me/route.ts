/**
 * Server-side current user API route
 * Proxies request to backend with httpOnly cookie token
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("sahool_admin_token")?.value;

    if (!token) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    // Forward request to backend API with token
    const response = await fetch(`${API_URL}/api/v1/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (!response.ok) {
      // Token might be expired or invalid - clear cookies
      if (response.status === 401) {
        const logoutResponse = NextResponse.json(
          { error: data.message || data.detail || "Unauthorized" },
          { status: 401 },
        );
        logoutResponse.cookies.delete("sahool_admin_token");
        logoutResponse.cookies.delete("sahool_admin_refresh_token");
        logoutResponse.cookies.delete("sahool_admin_last_activity");
        return logoutResponse;
      }

      return NextResponse.json(
        { error: data.message || data.detail || "Failed to fetch user" },
        { status: response.status },
      );
    }

    return NextResponse.json({
      success: true,
      data: data,
    });
  } catch (error) {
    console.error("Get current user error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
