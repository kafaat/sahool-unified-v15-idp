/**
 * Server-side login API route
 * Sets httpOnly cookies for security
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { logger } from "@/lib/logger";
import { API_URL, API_ENDPOINTS } from "@/config/api";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, totp_code } = body;

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
