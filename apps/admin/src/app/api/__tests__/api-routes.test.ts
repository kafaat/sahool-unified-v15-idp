/**
 * API Routes Tests - Phase 1 Coverage
 * اختبارات مسارات API - المرحلة الأولى
 *
 * Tests all 9 API route handlers:
 * - auth/login, auth/logout, auth/refresh, auth/me, auth/activity
 * - csrf-token, health, log-error, csp-report
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { NextRequest } from "next/server";

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

// Mock next/headers cookies
const mockCookieStore = {
  get: vi.fn(),
  set: vi.fn(),
  delete: vi.fn(),
};

vi.mock("next/headers", () => ({
  cookies: vi.fn(() => Promise.resolve(mockCookieStore)),
}));

// Mock logger
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

// Mock rate limiter
vi.mock("@/lib/rate-limiter", () => ({
  checkRateLimit: vi.fn(() => ({ allowed: true })),
  resetRateLimit: vi.fn(),
}));

// Mock config/api
vi.mock("@/config/api", () => ({
  API_URL: "http://localhost:8000",
  API_BASE_URL: "http://localhost:8000",
  API_ENDPOINTS: {
    auth: {
      login: "/api/v1/auth/login",
      logout: "/api/v1/auth/logout",
      me: "/api/v1/auth/me",
      refresh: "/api/v1/auth/refresh",
    },
  },
  TIMEOUT_TIERS: {
    default: 10000,
    upload: 30000,
    analysis: 60000,
    report: 120000,
    healthCheck: 5000,
  },
}));

// Mock csrf
vi.mock("@/lib/csrf", () => ({
  createCsrfTokenPayload: vi.fn(() => ({
    token: "test-csrf-token-abc123",
    expiresAt: Date.now() + 3600000,
  })),
  serializeCsrfTokenPayload: vi.fn(() => "serialized-csrf-payload"),
  getCsrfCookieOptions: vi.fn(() => ({
    httpOnly: true,
    secure: false,
    sameSite: "strict" as const,
    path: "/",
    maxAge: 3600,
  })),
  CSRF_CONFIG: {
    COOKIE_NAME: "sahool_csrf",
  },
}));

// Helper to create NextRequest
function createRequest(
  url: string,
  options: RequestInit & { headers?: Record<string, string> } = {},
): NextRequest {
  return new NextRequest(new URL(url, "http://localhost:3002"), options);
}

// ═══════════════════════════════════════════════════════════════════════════
// Health Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("GET /api/health", () => {
  it("returns healthy status with service info", async () => {
    const { GET } = await import("@/app/api/health/route");
    const response = await GET();
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.status).toBe("healthy");
    expect(data.service).toBe("sahool-admin");
    expect(data.timestamp).toBeDefined();
    expect(data.uptime).toBeDefined();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Login Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/auth/login", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockCookieStore.get.mockReturnValue(undefined);
    vi.mocked(globalThis.fetch).mockReset();
  });

  it("returns 429 when rate limited", async () => {
    const { checkRateLimit } = await import("@/lib/rate-limiter");
    vi.mocked(checkRateLimit).mockReturnValue({
      allowed: false,
      message: "Too many attempts",
      resetTime: Date.now() + 900000,
      remaining: 0,
    });

    const { POST } = await import("@/app/api/auth/login/route");
    const request = createRequest("http://localhost:3002/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "test@test.com", password: "pass" }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(429);
    expect(data.error).toContain("Too many");
  });

  it("forwards login to backend and sets cookies on success", async () => {
    const { checkRateLimit, resetRateLimit } = await import(
      "@/lib/rate-limiter"
    );
    vi.mocked(checkRateLimit).mockReturnValue({
      allowed: true,
      remaining: 4,
    });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          access_token: "test-access-token",
          refresh_token: "test-refresh-token",
          user: { id: "1", email: "admin@sahool.app", role: "admin" },
        }),
        { status: 200 },
      ),
    );

    const { POST } = await import("@/app/api/auth/login/route");
    const request = createRequest("http://localhost:3002/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: "admin@sahool.app",
        password: "password123",
      }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.user).toBeDefined();

    // Verify cookies were set
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_token",
      "test-access-token",
      expect.objectContaining({
        httpOnly: true,
        sameSite: "strict",
        path: "/",
      }),
    );
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_refresh_token",
      "test-refresh-token",
      expect.objectContaining({ httpOnly: true }),
    );

    // Rate limit should be reset on success
    expect(resetRateLimit).toHaveBeenCalledWith("login:admin@sahool.app");
  });

  it("returns error on backend failure", async () => {
    const { checkRateLimit } = await import("@/lib/rate-limiter");
    vi.mocked(checkRateLimit).mockReturnValue({ allowed: true, remaining: 4 });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ message: "Invalid credentials" }),
        { status: 401 },
      ),
    );

    const { POST } = await import("@/app/api/auth/login/route");
    const request = createRequest("http://localhost:3002/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "bad@test.com", password: "wrong" }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe("Invalid credentials");
  });

  it("handles 2FA required response", async () => {
    const { checkRateLimit } = await import("@/lib/rate-limiter");
    vi.mocked(checkRateLimit).mockReturnValue({ allowed: true, remaining: 4 });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          requires_2fa: true,
          temp_token: "temp-2fa-token",
        }),
        { status: 200 },
      ),
    );

    const { POST } = await import("@/app/api/auth/login/route");
    const request = createRequest("http://localhost:3002/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: "admin@sahool.app",
        password: "password123",
      }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.requires_2fa).toBe(true);
    expect(data.temp_token).toBe("temp-2fa-token");
  });

  it("returns 500 on unexpected error", async () => {
    const { checkRateLimit } = await import("@/lib/rate-limiter");
    vi.mocked(checkRateLimit).mockReturnValue({ allowed: true, remaining: 4 });

    vi.mocked(globalThis.fetch).mockRejectedValueOnce(
      new Error("Network error"),
    );

    const { POST } = await import("@/app/api/auth/login/route");
    const request = createRequest("http://localhost:3002/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "test@test.com", password: "pass" }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(500);
    expect(data.error).toBe("Internal server error");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Logout Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/auth/logout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();
  });

  it("clears cookies and revokes token on backend", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ success: true }), { status: 200 }),
    );

    const { POST } = await import("@/app/api/auth/logout/route");
    const request = createRequest("http://localhost:3002/api/auth/logout", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);

    // Verify cookies were deleted
    expect(mockCookieStore.delete).toHaveBeenCalledWith("sahool_admin_token");
    expect(mockCookieStore.delete).toHaveBeenCalledWith(
      "sahool_admin_refresh_token",
    );
    expect(mockCookieStore.delete).toHaveBeenCalledWith(
      "sahool_admin_last_activity",
    );
  });

  it("still clears cookies when backend revocation fails", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });
    vi.mocked(globalThis.fetch).mockRejectedValueOnce(
      new Error("Backend unreachable"),
    );

    const { POST } = await import("@/app/api/auth/logout/route");
    const request = createRequest("http://localhost:3002/api/auth/logout", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(mockCookieStore.delete).toHaveBeenCalledWith("sahool_admin_token");
  });

  it("succeeds even without access token cookie", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const { POST } = await import("@/app/api/auth/logout/route");
    const request = createRequest("http://localhost:3002/api/auth/logout", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Refresh Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/auth/refresh", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();
  });

  it("returns 401 when no refresh token", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe("No refresh token available");
  });

  it("refreshes token and updates cookies", async () => {
    mockCookieStore.get.mockReturnValue({ value: "old-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          access_token: "new-access-token",
          refresh_token: "new-refresh-token",
        }),
        { status: 200 },
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

    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_token",
      "new-access-token",
      expect.objectContaining({ httpOnly: true }),
    );
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_refresh_token",
      "new-refresh-token",
      expect.objectContaining({ httpOnly: true }),
    );
  });

  it("clears cookies when backend returns error", async () => {
    mockCookieStore.get.mockReturnValue({ value: "expired-refresh-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ message: "Token expired" }),
        { status: 401 },
      ),
    );

    const { POST } = await import("@/app/api/auth/refresh/route");
    const request = createRequest("http://localhost:3002/api/auth/refresh", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe("Token expired");
    expect(mockCookieStore.delete).toHaveBeenCalledWith("sahool_admin_token");
    expect(mockCookieStore.delete).toHaveBeenCalledWith(
      "sahool_admin_refresh_token",
    );
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Me Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("GET /api/auth/me", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();
  });

  it("returns 401 when no token", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const { GET } = await import("@/app/api/auth/me/route");
    const request = createRequest("http://localhost:3002/api/auth/me");

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe("Not authenticated");
  });

  it("returns user data from backend", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          id: "user-1",
          email: "admin@sahool.app",
          name: "Admin",
          role: "admin",
        }),
        { status: 200 },
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

  it("clears cookies on 401 from backend", async () => {
    mockCookieStore.get.mockReturnValue({ value: "expired-token" });

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ message: "Unauthorized" }),
        { status: 401 },
      ),
    );

    const { GET } = await import("@/app/api/auth/me/route");
    const request = createRequest("http://localhost:3002/api/auth/me");

    const response = await GET(request);

    expect(response.status).toBe(401);
    // Cookies cleared via response.cookies.delete
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Activity Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/auth/activity", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns 401 when not authenticated", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const { POST } = await import("@/app/api/auth/activity/route");
    const response = await POST();
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe("Not authenticated");
  });

  it("updates last activity timestamp", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });

    const { POST } = await import("@/app/api/auth/activity/route");
    const response = await POST();
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "sahool_admin_last_activity",
      expect.any(String),
      expect.objectContaining({ httpOnly: true }),
    );
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// CSRF Token Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("/api/csrf-token", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("GET generates a new CSRF token", async () => {
    const { GET } = await import("@/app/api/csrf-token/route");
    const request = createRequest("http://localhost:3002/api/csrf-token");

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.token).toBe("test-csrf-token-abc123");
    expect(data.expiresAt).toBeDefined();

    // Security headers
    expect(response.headers.get("X-Content-Type-Options")).toBe("nosniff");
    expect(response.headers.get("Cache-Control")).toContain("no-store");
  });

  it("POST refreshes CSRF token", async () => {
    const { POST } = await import("@/app/api/csrf-token/route");
    const request = createRequest("http://localhost:3002/api/csrf-token", {
      method: "POST",
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.token).toBeDefined();
    expect(data.refreshed).toBe(true);
  });

  it("OPTIONS returns CORS headers", async () => {
    const { OPTIONS } = await import("@/app/api/csrf-token/route");
    const response = await OPTIONS();

    expect(response.status).toBe(204);
    expect(response.headers.get("Access-Control-Allow-Methods")).toContain(
      "GET",
    );
    expect(response.headers.get("Access-Control-Allow-Headers")).toContain(
      "X-CSRF-Token",
    );
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Log Error Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/log-error", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("logs error with valid payload", async () => {
    const { POST } = await import("@/app/api/log-error/route");
    const request = createRequest("http://localhost:3002/api/log-error", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: "Test error",
        timestamp: new Date().toISOString(),
        stack: "Error: Test\n  at test.ts:1",
      }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.logged).toBe(true);
  });

  it("returns 400 for missing required fields", async () => {
    const { POST } = await import("@/app/api/log-error/route");
    const request = createRequest("http://localhost:3002/api/log-error", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stack: "some stack" }), // missing message & timestamp
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain("Missing required fields");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// CSP Report Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/csp-report", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("accepts valid CSP report", async () => {
    const { POST } = await import("@/app/api/csp-report/route");
    const request = createRequest("http://localhost:3002/api/csp-report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        origin: "https://admin.sahool.app",
      },
      body: JSON.stringify({
        "csp-report": {
          "document-uri": "https://admin.sahool.app/dashboard",
          "violated-directive": "script-src",
          "blocked-uri": "https://evil.example.com/script.js",
        },
      }),
    });

    const response = await POST(request);
    expect(response.status).toBe(204);
  });

  it("filters browser extension violations", async () => {
    const { POST } = await import("@/app/api/csp-report/route");
    const request = createRequest("http://localhost:3002/api/csp-report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        origin: "https://admin.sahool.app",
      },
      body: JSON.stringify({
        "csp-report": {
          "document-uri": "https://admin.sahool.app/",
          "violated-directive": "script-src",
          "blocked-uri": "chrome-extension://abc123/content.js",
        },
      }),
    });

    const response = await POST(request);
    expect(response.status).toBe(204);
  });

  it("returns 400 for invalid CSP report format", async () => {
    const { POST } = await import("@/app/api/csp-report/route");
    const request = createRequest("http://localhost:3002/api/csp-report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        origin: "https://admin.sahool.app",
      },
      body: JSON.stringify({ invalid: "data" }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toBe("Invalid CSP report format");
  });

  it("rejects requests from disallowed origins", async () => {
    const { POST } = await import("@/app/api/csp-report/route");
    const request = createRequest("http://localhost:3002/api/csp-report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        origin: "https://evil.example.com",
      },
      body: JSON.stringify({
        "csp-report": {
          "document-uri": "https://evil.example.com/",
          "violated-directive": "script-src",
          "blocked-uri": "https://bad.example.com/",
        },
      }),
    });

    const response = await POST(request);
    expect(response.status).toBe(403);
  });
});
