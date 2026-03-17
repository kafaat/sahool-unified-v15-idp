/**
 * Auth API Routes - Security Fix Tests
 * اختبارات إصلاحات أمان مسارات المصادقة
 *
 * Validates:
 * - Refresh route maxAge alignment (1800s default, not 86400s)
 * - Content-type check in /api/auth/me (rejects non-JSON)
 * - Content-type check in /api/auth/refresh (rejects non-JSON)
 * - Logout timeout and API_URL usage with AbortController
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { NextRequest } from "next/server";

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

const mockCookieStore = {
  get: vi.fn(),
  set: vi.fn(),
  delete: vi.fn(),
};

vi.mock("next/headers", () => ({
  cookies: vi.fn(() => Promise.resolve(mockCookieStore)),
}));

vi.mock("@/lib/logger", () => ({
  logger: {
    log: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    production: vi.fn(),
    critical: vi.fn(),
  },
}));

vi.mock("@/config/api", () => ({
  API_URL: "http://localhost:8000",
  API_BASE_URL: "http://localhost:8000",
  TIMEOUT_TIERS: {
    default: 10000,
    upload: 30000,
    analysis: 60000,
    report: 120000,
    healthCheck: 5000,
  },
}));

vi.mock("@/lib/rate-limiter", () => ({
  checkRateLimit: vi.fn(() => ({ allowed: true })),
  resetRateLimit: vi.fn(),
}));

// Helper to create NextRequest
function createRequest(
  url: string,
  options: RequestInit & { headers?: Record<string, string> } = {},
): NextRequest {
  return new NextRequest(new URL(url, "http://localhost:3002"), options);
}

// Helper to create a Response with specific content-type
function createResponseWithContentType(
  body: string,
  status: number,
  contentType: string,
): Response {
  return new Response(body, {
    status,
    headers: { "Content-Type": contentType },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Refresh Route - maxAge Alignment Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/auth/refresh - maxAge alignment", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();
    // Clear env vars to test defaults
    delete process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS;
    delete process.env.JWT_REFRESH_TOKEN_EXPIRE_SECONDS;
  });

  it("uses 1800s (30 min) as default maxAge for access token cookie, not 86400s", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        JSON.stringify({
          access_token: "new-access-token",
          refresh_token: "new-refresh-token",
        }),
        200,
        "application/json",
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    const response = await POST(request);
    expect(response.status).toBe(200);

    // Verify access token cookie maxAge is 1800 (30 min), NOT 86400 (24h)
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_token",
      "new-access-token",
      expect.objectContaining({
        httpOnly: true,
        sameSite: "strict",
        maxAge: 1800,
        path: "/",
      }),
    );
  });

  it("uses 604800s (7 days) as default maxAge for refresh token cookie", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        JSON.stringify({
          access_token: "new-access-token",
          refresh_token: "new-refresh-token",
        }),
        200,
        "application/json",
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    await POST(request);

    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_refresh_token",
      "new-refresh-token",
      expect.objectContaining({
        httpOnly: true,
        sameSite: "strict",
        maxAge: 604800,
        path: "/",
      }),
    );
  });

  it("respects JWT_ACCESS_TOKEN_EXPIRE_SECONDS env var when set", async () => {
    process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS = "900"; // 15 minutes

    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        JSON.stringify({
          access_token: "new-access-token",
          refresh_token: "new-refresh-token",
        }),
        200,
        "application/json",
      ),
    );

    // Re-import to pick up env var change
    vi.resetModules();

    // Re-apply mocks after resetModules
    vi.doMock("next/headers", () => ({
      cookies: vi.fn(() => Promise.resolve(mockCookieStore)),
    }));
    vi.doMock("@/lib/logger", () => ({
      logger: {
        log: vi.fn(),
        info: vi.fn(),
        warn: vi.fn(),
        error: vi.fn(),
        production: vi.fn(),
        critical: vi.fn(),
      },
    }));
    vi.doMock("@/config/api", () => ({
      API_URL: "http://localhost:8000",
      TIMEOUT_TIERS: { default: 10000 },
    }));

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    await POST(request);

    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_token",
      "new-access-token",
      expect.objectContaining({
        maxAge: 900,
      }),
    );
  });

  it("sets last_activity cookie with same maxAge as access token", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        JSON.stringify({
          access_token: "new-access-token",
          refresh_token: "new-refresh-token",
        }),
        200,
        "application/json",
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    await POST(request);

    // last_activity should use the same maxAge as the access token (1800s default)
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_last_activity",
      expect.any(String),
      expect.objectContaining({
        maxAge: 1800,
      }),
    );
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// /api/auth/me - Content-Type Check Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("GET /api/auth/me - content-type validation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();
  });

  it("returns 502 when backend responds with text/html instead of JSON", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        "<html><body>502 Bad Gateway</body></html>",
        200,
        "text/html",
      ),
    );

    const { GET } = await import("@/app/api/auth/me/route");
    const request = createRequest("http://localhost:3002/api/auth/me");

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe("Invalid response from backend");
  });

  it("returns 502 when backend responds with text/plain", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        "Internal Server Error",
        500,
        "text/plain",
      ),
    );

    const { GET } = await import("@/app/api/auth/me/route");
    const request = createRequest("http://localhost:3002/api/auth/me");

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe("Invalid response from backend");
  });

  it("returns 502 when backend has no content-type header", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    // Response with no content-type header at all
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response('{"data": "test"}', { status: 200 }),
    );

    const { GET } = await import("@/app/api/auth/me/route");
    const request = createRequest("http://localhost:3002/api/auth/me");

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe("Invalid response from backend");
  });

  it("succeeds when backend responds with application/json content-type", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        JSON.stringify({
          id: "user-1",
          email: "admin@sahool.app",
          role: "admin",
        }),
        200,
        "application/json",
      ),
    );

    const { GET } = await import("@/app/api/auth/me/route");
    const request = createRequest("http://localhost:3002/api/auth/me");

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.data.email).toBe("admin@sahool.app");
  });

  it("accepts application/json; charset=utf-8 content-type", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        JSON.stringify({ id: "user-1", email: "admin@sahool.app" }),
        200,
        "application/json; charset=utf-8",
      ),
    );

    const { GET } = await import("@/app/api/auth/me/route");
    const request = createRequest("http://localhost:3002/api/auth/me");

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// /api/auth/refresh - Content-Type Check Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/auth/refresh - content-type validation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();
  });

  it("returns 502 when backend responds with text/html instead of JSON", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        "<html><body>Bad Gateway</body></html>",
        200,
        "text/html",
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe("Invalid response from backend");
  });

  it("returns 502 when backend responds with text/plain", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        "Service Unavailable",
        503,
        "text/plain",
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe("Invalid response from backend");
  });

  it("does not attempt JSON.parse on non-JSON response (prevents crash)", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    // Simulate nginx/Kong returning HTML error page
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        "<!DOCTYPE html><html><head><title>502 Bad Gateway</title></head><body><h1>502 Bad Gateway</h1><p>nginx</p></body></html>",
        502,
        "text/html; charset=utf-8",
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    // This should NOT throw - it should gracefully return 502
    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe("Invalid response from backend");
  });

  it("succeeds when backend responds with valid application/json", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      createResponseWithContentType(
        JSON.stringify({
          access_token: "new-token",
          refresh_token: "new-refresh",
        }),
        200,
        "application/json",
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// /api/auth/logout - Timeout and API_URL Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/auth/logout - timeout and API_URL", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();
  });

  it("calls backend with API_URL from config (not hardcoded)", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ success: true }), { status: 200 }),
    );

    const { POST } = await import("@/app/api/auth/logout/route");
    const request = createRequest("http://localhost:3002/api/auth/logout", {
      method: "POST",
    });

    await POST(request);

    // Verify fetch was called with the API_URL from config
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/logout",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer valid-token",
        }),
      }),
    );
  });

  it("passes AbortController signal to fetch for timeout support", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ success: true }), { status: 200 }),
    );

    const { POST } = await import("@/app/api/auth/logout/route");
    const request = createRequest("http://localhost:3002/api/auth/logout", {
      method: "POST",
    });

    await POST(request);

    // Verify fetch was called with a signal (AbortController)
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        signal: expect.any(AbortSignal),
      }),
    );
  });

  it("still clears cookies even when fetch times out (abort)", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    // Simulate an abort error
    const abortError = new DOMException("The operation was aborted", "AbortError");
    vi.mocked(globalThis.fetch).mockRejectedValueOnce(abortError);

    const { POST } = await import("@/app/api/auth/logout/route");
    const request = createRequest("http://localhost:3002/api/auth/logout", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    // Should still succeed (cookies cleared)
    expect(response.status).toBe(200);
    expect(data.success).toBe(true);

    // Cookies should still be deleted
    expect(mockCookieStore.delete).toHaveBeenCalledWith("sahool_admin_token");
    expect(mockCookieStore.delete).toHaveBeenCalledWith("sahool_admin_refresh_token");
    expect(mockCookieStore.delete).toHaveBeenCalledWith("sahool_admin_last_activity");
  });

  it("does not call backend when no access token exists", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const { POST } = await import("@/app/api/auth/logout/route");
    const request = createRequest("http://localhost:3002/api/auth/logout", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);

    // fetch should NOT have been called since no token
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });
});
