/**
 * Weather API Proxy Route Tests
 * اختبارات مسار وكيل واجهة برمجة تطبيقات الطقس
 *
 * Tests the weather proxy route handler:
 * - Input validation (action, lat, lon)
 * - Correct payload forwarding for each action
 * - Error handling when weather service fails
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

// Mock jwt-verify
const mockGetUserFromToken = vi.fn();

vi.mock("@/lib/auth/jwt-verify", () => ({
  getUserFromToken: (...args: unknown[]) => mockGetUserFromToken(...args),
}));

// Helper to create NextRequest
function createRequest(
  url: string,
  options: RequestInit & { headers?: Record<string, string> } = {},
): NextRequest {
  return new NextRequest(new URL(url, "http://localhost:3002"), options);
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("POST /api/weather", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(globalThis.fetch).mockReset();

    // Default: authenticated user with tenant_id
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });
    mockGetUserFromToken.mockResolvedValue({
      id: "user-1",
      email: "farmer@sahool.app",
      tenant_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    });
  });

  it("returns 400 for missing action", async () => {
    const { POST } = await import("@/app/api/weather/route");
    const request = createRequest("http://localhost:3002/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat: 24.7, lon: 46.7 }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain("Invalid action");
  });

  it("returns 400 for invalid action", async () => {
    const { POST } = await import("@/app/api/weather/route");
    const request = createRequest("http://localhost:3002/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "invalid", lat: 24.7, lon: 46.7 }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain("Invalid action");
  });

  it("returns 400 for non-numeric lat/lon", async () => {
    const { POST } = await import("@/app/api/weather/route");
    const request = createRequest("http://localhost:3002/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "current", lat: "not-a-number", lon: "abc" }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain("lat and lon are required numeric parameters");
  });

  it("calls weather service with correct body for 'current' action", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ temperature: 28, humidity: 45 }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    const { POST } = await import("@/app/api/weather/route");
    const request = createRequest("http://localhost:3002/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "current", lat: 24.7, lon: 46.7 }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.temperature).toBe(28);

    // Verify fetch was called with correct URL and payload
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://weather-service:8092/weather/current",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
          field_id: "default",
          lat: 24.7,
          lon: 46.7,
        }),
      }),
    );
  });

  it("calls weather service with correct body for 'forecast' action including days", async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ forecast: [{ day: 1, temp: 30 }] }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    const { POST } = await import("@/app/api/weather/route");
    const request = createRequest("http://localhost:3002/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "forecast",
        lat: 24.7,
        lon: 46.7,
        days: 7,
      }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.forecast).toBeDefined();

    // Verify fetch was called with forecast path and days in payload
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://weather-service:8092/weather/forecast",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          tenant_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
          field_id: "default",
          lat: 24.7,
          lon: 46.7,
          days: 7,
        }),
      }),
    );
  });

  it("returns 502 when weather service fails", async () => {
    vi.mocked(globalThis.fetch).mockRejectedValueOnce(
      new Error("Connection refused"),
    );

    const { POST } = await import("@/app/api/weather/route");
    const request = createRequest("http://localhost:3002/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "current", lat: 24.7, lon: 46.7 }),
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe("Failed to fetch weather data");
  });

  it("falls back to 'default' tenant_id when no token cookie exists", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ temperature: 25 }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    const { POST } = await import("@/app/api/weather/route");
    const request = createRequest("http://localhost:3002/api/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "current", lat: 24.7, lon: 46.7 }),
    });

    await POST(request);

    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://weather-service:8092/weather/current",
      expect.objectContaining({
        body: expect.stringContaining('"tenant_id":"default"'),
      }),
    );
  });
});
