/**
 * Token Refresh Proxy Route Tests
 * اختبارات مسار وكيل تجديد التوكن
 *
 * Tests the server-side proxy that reads httpOnly refresh_token cookie
 * and forwards it to the backend auth service.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════
// Module Mocks
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
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}));

// Mock global fetch for backend calls
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

function createRequest(): any {
  return new Request("http://localhost:3000/api/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Token Refresh Proxy Route", () => {
  const originalEnv = { ...process.env };

  beforeEach(() => {
    vi.clearAllMocks();
    process.env = {
      ...originalEnv,
      NEXT_PUBLIC_API_URL: "http://localhost:8000",
      NODE_ENV: "test",
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it("should return 500 when NEXT_PUBLIC_API_URL is not configured", async () => {
    process.env.NEXT_PUBLIC_API_URL = "";
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    const response = await POST(createRequest());
    const body = await response.json();

    expect(response.status).toBe(500);
    expect(body.success).toBe(false);
    expect(body.error).toBe("Server configuration error");
  });

  it("should return 401 when no refresh_token cookie exists", async () => {
    mockCookieStore.get.mockReturnValue(undefined);
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    const response = await POST(createRequest());
    const body = await response.json();

    expect(response.status).toBe(401);
    expect(body.success).toBe(false);
    expect(body.error).toBe("No refresh token");
  });

  it("should return 401 and clear cookies when backend refresh fails", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });
    mockFetch.mockResolvedValue({
      ok: false,
      status: 401,
    });
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    const response = await POST(createRequest());
    const body = await response.json();

    expect(response.status).toBe(401);
    expect(body.success).toBe(false);
    expect(mockCookieStore.delete).toHaveBeenCalledWith("access_token");
    expect(mockCookieStore.delete).toHaveBeenCalledWith("refresh_token");
  });

  it("should return 401 when backend returns no access_token", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    const response = await POST(createRequest());
    const body = await response.json();

    expect(response.status).toBe(401);
    expect(body.error).toBe("No access token in refresh response");
  });

  it("should set httpOnly cookie and return token on success", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: "new-access-token" }),
    });
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    const response = await POST(createRequest());
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(body.success).toBe(true);
    expect(body.access_token).toBe("new-access-token");
    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "access_token",
      "new-access-token",
      expect.objectContaining({
        httpOnly: true,
        sameSite: "strict",
        path: "/",
      }),
    );
  });

  it("should support nested data.data.access_token response format", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });
    mockFetch.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({ data: { access_token: "nested-token" } }),
    });
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    const response = await POST(createRequest());
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(body.access_token).toBe("nested-token");
  });

  it("should use default maxAge of 1800 when env var is not set", async () => {
    delete process.env.JWT_ACCESS_TOKEN_EXPIRE_SECONDS;
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: "token" }),
    });
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    await POST(createRequest());

    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "access_token",
      "token",
      expect.objectContaining({ maxAge: 1800 }),
    );
  });

  it("should return 500 on unexpected errors", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-refresh-token" });
    mockFetch.mockRejectedValue(new Error("Network error"));
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    const response = await POST(createRequest());
    const body = await response.json();

    expect(response.status).toBe(500);
    expect(body.error).toBe("Internal server error");
  });

  it("should forward refresh_token to correct backend endpoint", async () => {
    mockCookieStore.get.mockReturnValue({ value: "my-refresh-token" });
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: "token" }),
    });
    vi.resetModules();

    const { POST } = await import("../refresh/route");
    await POST(createRequest());

    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/refresh",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ refresh_token: "my-refresh-token" }),
      }),
    );
  });
});
