/**
 * Weather API Proxy Routes
 * وكيل واجهة برمجة تطبيقات الطقس
 *
 * Server-side proxy that extracts tenant_id from the httpOnly JWT cookie
 * and forwards weather requests to the backend weather-service.
 * This solves the issue where client-side code cannot read httpOnly cookies.
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { getUserFromToken } from "@/lib/auth/jwt-verify";

// Weather service URL from environment, fallback to docker service name
const WEATHER_SERVICE_URL =
  process.env.WEATHER_SERVICE_URL || "http://weather-service:8092";

/**
 * Validate UUID format for tenant_id injection prevention
 */
function isValidUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
}

/**
 * Extract tenant_id from httpOnly cookie server-side
 */
async function getTenantId(): Promise<string> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("sahool_admin_token")?.value;
    if (!token) return "default";

    const user = await getUserFromToken(token);
    if (user?.tenant_id && isValidUUID(user.tenant_id)) {
      return user.tenant_id;
    }
    return "default";
  } catch {
    return "default";
  }
}

/**
 * POST /api/weather
 *
 * Proxies weather requests to the backend weather-service.
 * Expects JSON body with: { action, lat, lon, field_id?, days? }
 * where action is one of: "current", "forecast", "agricultural"
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, lat, lon, field_id, days } = body;

    if (!action || !["current", "forecast", "agricultural"].includes(action)) {
      return NextResponse.json(
        { error: "Invalid action. Must be: current, forecast, or agricultural" },
        { status: 400 },
      );
    }

    if (typeof lat !== "number" || typeof lon !== "number") {
      return NextResponse.json(
        { error: "lat and lon are required numeric parameters" },
        { status: 400 },
      );
    }

    const tenantId = await getTenantId();

    // Build path based on action
    const pathMap: Record<string, string> = {
      current: "/weather/current",
      forecast: "/weather/forecast",
      agricultural: "/weather/agricultural-report",
    };

    const payload: Record<string, unknown> = {
      tenant_id: tenantId,
      field_id: field_id || "default",
      lat,
      lon,
    };

    if (action === "forecast" && days) {
      payload.days = days;
    }

    const response = await fetch(`${WEATHER_SERVICE_URL}${pathMap[action]}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(15000),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Weather API proxy error:", error);
    return NextResponse.json(
      { error: "Failed to fetch weather data" },
      { status: 502 },
    );
  }
}
