/**
 * Code Review API Proxy Routes
 * وكيل واجهة برمجة تطبيقات مراجعة الكود
 *
 * Server-side proxy that forwards code review requests to the backend
 * code-review-service. Extracts tenant_id from the httpOnly JWT cookie.
 */

import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { getUserFromToken } from "@/lib/auth/jwt-verify";
import { logger } from "@/lib/logger";

const CODE_REVIEW_SERVICE_URL =
  process.env.CODE_REVIEW_SERVICE_URL || "http://code-review-service:8102";

async function getAuthHeaders(): Promise<Record<string, string> | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("sahool_admin_token")?.value;
    if (!token) return null;

    const user = await getUserFromToken(token);
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
    if (user?.tenant_id) {
      headers["X-Tenant-ID"] = user.tenant_id;
    }
    return headers;
  } catch {
    return null;
  }
}

async function proxyGet(path: string): Promise<NextResponse> {
  try {
    const headers = await getAuthHeaders();
    if (!headers) {
      return NextResponse.json({ error: "Authentication required" }, { status: 401 });
    }
    const response = await fetch(`${CODE_REVIEW_SERVICE_URL}${path}`, {
      headers,
      signal: AbortSignal.timeout(15000),
    });
    const text = await response.text();
    try {
      const data = JSON.parse(text);
      return NextResponse.json(data, { status: response.status });
    } catch {
      logger.error("Code review service returned non-JSON:", { status: response.status, body: text.slice(0, 200) });
      return NextResponse.json(
        { error: "Code review service returned an unexpected response" },
        { status: 502 },
      );
    }
  } catch (error) {
    logger.error("Code review proxy GET error:", error);
    return NextResponse.json(
      { error: "Code review service unavailable" },
      { status: 502 },
    );
  }
}

async function proxyPost(
  path: string,
  body: unknown,
): Promise<NextResponse> {
  try {
    const headers = await getAuthHeaders();
    if (!headers) {
      return NextResponse.json({ error: "Authentication required" }, { status: 401 });
    }
    const response = await fetch(`${CODE_REVIEW_SERVICE_URL}${path}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(60000),
    });
    const text = await response.text();
    try {
      const data = JSON.parse(text);
      return NextResponse.json(data, { status: response.status });
    } catch {
      logger.error("Code review service returned non-JSON:", { status: response.status, body: text.slice(0, 200) });
      return NextResponse.json(
        { error: "Code review service returned an unexpected response" },
        { status: 502 },
      );
    }
  } catch (error) {
    logger.error("Code review proxy POST error:", error);
    return NextResponse.json(
      { error: "Code review service unavailable" },
      { status: 502 },
    );
  }
}

/**
 * GET /api/code-review?action=health|models|cache
 */
export async function GET(request: NextRequest) {
  const action = request.nextUrl.searchParams.get("action") || "health";

  const pathMap: Record<string, string> = {
    health: "/health",
    models: "/models",
    cache: "/cache/stats",
  };

  const path = pathMap[action];
  if (!path) {
    return NextResponse.json(
      { error: "Invalid action. Must be: health, models, or cache" },
      { status: 400 },
    );
  }

  return proxyGet(path);
}

/**
 * POST /api/code-review
 * Body: { action: "review"|"clear_cache", ...params }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, ...params } = body;

    if (!action) {
      return NextResponse.json(
        { error: "action is required" },
        { status: 400 },
      );
    }

    switch (action) {
      case "review":
        if (!params.code || typeof params.code !== "string") {
          return NextResponse.json(
            { error: "code is required" },
            { status: 400 },
          );
        }
        return proxyPost("/review", {
          code: params.code,
          language: params.language,
          filename: params.filename,
          model: params.model,
          use_cache: params.use_cache ?? true,
        });

      case "clear_cache":
        return proxyPost("/cache/clear", {});

      default:
        return NextResponse.json(
          { error: "Invalid action. Must be: review or clear_cache" },
          { status: 400 },
        );
    }
  } catch (error) {
    logger.error("Code review API proxy error:", error);
    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 },
    );
  }
}
