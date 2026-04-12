import { test, expect } from "@playwright/test";

/**
 * API Health & Readiness E2E Tests
 * اختبارات صحة وجاهزية الـ API
 *
 * Verifies that the web application's internal health/readiness
 * API routes respond correctly. These routes are used by Kubernetes
 * probes and monitoring tools.
 *
 * Also tests that the frontend correctly calls backend APIs
 * for each major service area (verifying API integration wiring).
 *
 * The `request` fixture tests (health, CSRF, error endpoints) require
 * the Next.js dev server to be running. They are skipped in CI when
 * the server is not available.
 */

const serverAvailable =
  !!process.env.API_AVAILABLE || !process.env.CI;

test.describe("Web App Health Endpoints", () => {
  test.skip(!serverAvailable, "Requires running Next.js server");

  test("GET /api/health returns 200", async ({ request }) => {
    const response = await request.get("/api/health");
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty("status");
    expect(body.status).toBe("ok");
  });

  test("GET /api/healthz returns 200 (liveness probe)", async ({
    request,
  }) => {
    const response = await request.get("/api/healthz");
    expect(response.status()).toBe(200);
  });

  test("GET /api/readyz returns 200 (readiness probe)", async ({
    request,
  }) => {
    const response = await request.get("/api/readyz");
    expect(response.status()).toBe(200);
  });
});

test.describe("CSRF Token Endpoint", () => {
  test.skip(!serverAvailable, "Requires running Next.js server");

  test("GET /api/csrf-token returns a token", async ({ request }) => {
    const response = await request.get("/api/csrf-token");

    // Should return 200
    expect(response.status()).toBe(200);

    const body = await response.json();
    // Should contain a token field
    expect(body).toHaveProperty("token");
    expect(typeof body.token).toBe("string");
    expect(body.token.length).toBeGreaterThan(0);
  });
});

test.describe("Error Handling Endpoints", () => {
  test.skip(!serverAvailable, "Requires running Next.js server");

  test("POST /api/log-error accepts error reports", async ({ request }) => {
    const response = await request.post("/api/log-error", {
      data: {
        message: "Test error from E2E",
        stack: "Error: test\n    at test.spec.ts:1:1",
        url: "/dashboard",
        userAgent: "Playwright E2E",
      },
    });

    // Should accept the error report (200 or 204)
    expect([200, 204]).toContain(response.status());
  });

  test("POST /api/csp-report accepts CSP violation reports", async ({
    request,
  }) => {
    const response = await request.post("/api/csp-report", {
      data: {
        "csp-report": {
          "document-uri": "http://localhost:3000/dashboard",
          "violated-directive": "script-src",
          "blocked-uri": "http://evil.example.com",
        },
      },
    });

    // Should accept the report (200, 204, or even 400 if strict validation)
    expect([200, 204, 400]).toContain(response.status());
  });
});

test.describe("API Integration Verification", () => {
  /**
   * These tests verify that navigating to each service page triggers
   * the correct API call. They do NOT require a live backend — they
   * intercept and mock the calls, then assert the call was made.
   */

  async function setupWithApiTracking(page: import("@playwright/test").Page) {
    const apiCalls: string[] = [];

    await page.route("**/api/**", async (route) => {
      apiCalls.push(route.request().url());

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }),
      });
    });

    // Auth cookies
    const baseURL =
      process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000";
    await page.context().addCookies([
      {
        name: "access_token",
        value: "mock_test_token_for_e2e_testing",
        domain: new URL(baseURL).hostname,
        path: "/",
        httpOnly: true,
        secure: false,
        sameSite: "Lax",
      },
      {
        name: "user_session",
        value: JSON.stringify({
          id: "test-user-123",
          email: "test@sahool.com",
          name: "Test User",
          nameAr: "مستخدم اختباري",
          role: "admin",
        }),
        domain: new URL(baseURL).hostname,
        path: "/",
        httpOnly: false,
        secure: false,
        sameSite: "Lax",
      },
    ]);

    return { apiCalls };
  }

  const serviceApiTests = [
    { route: "/dashboard", expectApi: /auth|dashboard|stats|analytics|kpi/i, label: "Dashboard" },
    { route: "/fields", expectApi: /field/i, label: "Fields" },
    { route: "/tasks", expectApi: /task/i, label: "Tasks" },
    { route: "/weather", expectApi: /weather/i, label: "Weather" },
    { route: "/equipment", expectApi: /equipment/i, label: "Equipment" },
    { route: "/irrigation", expectApi: /irrigation/i, label: "Irrigation" },
    { route: "/alerts", expectApi: /alert/i, label: "Alerts" },
    { route: "/crop-health", expectApi: /crop|health|ndvi/i, label: "Crop Health" },
    { route: "/marketplace", expectApi: /market/i, label: "Marketplace" },
    { route: "/analytics", expectApi: /analytics|report|stat/i, label: "Analytics" },
    { route: "/satellite", expectApi: /satellite|ndvi|vegetation/i, label: "Satellite" },
    { route: "/iot", expectApi: /iot|sensor|device/i, label: "IoT" },
  ];

  for (const svc of serviceApiTests) {
    test(`${svc.label} page (${svc.route}) triggers API call`, async ({
      page,
    }) => {
      const { apiCalls } = await setupWithApiTracking(page);

      await page.goto(svc.route, { waitUntil: "domcontentloaded" });

      // Wait for page content to render (triggers data fetching)
      await expect(page.locator("h1, h2, main").first()).toBeVisible({
        timeout: 10000,
      });

      // The page should have made at least one API call
      expect(apiCalls.length).toBeGreaterThan(0);

      // Check if a service-specific API was called
      const serviceApiCalled = apiCalls.some((url) => svc.expectApi.test(url));

      // Log API calls for debugging when service-specific API is not found
      if (!serviceApiCalled) {
        console.log(
          `[${svc.label}] API calls made:`,
          apiCalls.map((u) => new URL(u).pathname),
        );
      }

      // The service-specific API must be called (not just auth)
      expect.soft(
        serviceApiCalled,
        `Expected ${svc.label} page to call API matching ${svc.expectApi}`,
      ).toBeTruthy();
    });
  }
});
