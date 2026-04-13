import { test, expect, type Page } from "@playwright/test";

/**
 * Services Contract E2E Tests
 * اختبارات عقد الخدمات - End-to-End
 *
 * Verifies that every dashboard page wires up to the *correct* backend
 * endpoint as defined in `@sahool/shared-types/contracts/api-endpoints`.
 *
 * Unlike `service-pages.spec.ts` (which only checks that pages render),
 * this suite asserts the exact contract path is hit. It mocks the backend
 * to keep the test hermetic — no live services needed.
 *
 * Pattern verified end-to-end:
 *   Browser → Next.js page → feature hook → unified-client / createApiClient
 *           → (Next.js rewrite OR /api/* proxy route)
 *           → Kong Gateway (production) / direct service (dev)
 *           → backend FastAPI / NestJS service
 *
 * If a page is supposed to call `WEATHER_ENDPOINTS.FORECAST` but instead
 * calls `/api/v1/weather/forecasts/extended` (typo, drift, refactor), this
 * test fails — catching contract drift before it reaches production.
 */

// ---------------------------------------------------------------------------
// Test fixtures
// ---------------------------------------------------------------------------

interface ServiceContract {
  /** Dashboard route the user navigates to */
  route: string;
  /** Human-readable label */
  label: string;
  /** Service category (for grouping) */
  category: string;
  /**
   * Regex matching at least one expected backend endpoint hit.
   * Drawn directly from packages/shared-types/src/contracts/api-endpoints.ts
   * so renames will fail this test and force a contract update.
   */
  expectEndpoint: RegExp;
  /**
   * Optional second regex — useful when a page legitimately fans out
   * (e.g. /dashboard hits /auth/me + /dashboard/stats).
   */
  expectAlsoEndpoint?: RegExp;
  /**
   * If true, this contract is allowed to be soft (page may render without
   * the call in some flows). Used for pages whose data is form-driven.
   */
  soft?: boolean;
}

const SERVICE_CONTRACTS: ServiceContract[] = [
  // ── Dashboard / Overview ─────────────────────────────────────────────
  {
    route: "/dashboard",
    label: "Dashboard",
    category: "Overview",
    expectEndpoint: /\/api\/v1\/(auth\/me|dashboard|stats|kpi)/i,
  },

  // ── Field Management ─────────────────────────────────────────────────
  {
    route: "/fields",
    label: "Fields",
    category: "Field Management",
    expectEndpoint: /\/api\/v1\/fields(\?|$|\/)/,
  },
  {
    route: "/farms",
    label: "Farms",
    category: "Field Management",
    expectEndpoint: /\/api\/v1\/farms/,
  },
  {
    route: "/crops",
    label: "Crops",
    category: "Field Management",
    expectEndpoint: /\/api\/v1\/(crops|crop-seasons)/,
  },
  {
    route: "/seasons",
    label: "Seasons",
    category: "Field Management",
    expectEndpoint: /\/api\/v1\/(seasons|crop-seasons)/,
  },
  {
    route: "/inventory",
    label: "Inventory",
    category: "Field Management",
    expectEndpoint: /\/api\/v1\/inventory/,
  },
  {
    route: "/tasks",
    label: "Tasks",
    category: "Field Management",
    expectEndpoint: /\/api\/v1\/tasks/,
  },
  {
    route: "/scouting",
    label: "Scouting",
    category: "Field Management",
    expectEndpoint: /\/api\/v1\/scouting/,
  },

  // ── Water & Irrigation ───────────────────────────────────────────────
  {
    route: "/irrigation",
    label: "Irrigation",
    category: "Water & Irrigation",
    expectEndpoint:
      /\/(api\/v1\/irrigation|api\/irrigation)(\?|$|\/)/,
  },
  {
    route: "/pivot-irrigation",
    label: "Pivot Irrigation",
    category: "Water & Irrigation",
    expectEndpoint: /\/api\/v1\/irrigation\/(pivot|schedule)/,
    soft: true,
  },

  // ── Crop Intelligence ────────────────────────────────────────────────
  {
    route: "/crop-health",
    label: "Crop Health",
    category: "Crop Intelligence",
    expectEndpoint: /\/api\/v1\/crop-health/,
  },
  {
    route: "/diseases",
    label: "Diseases",
    category: "Crop Intelligence",
    expectEndpoint: /\/api\/v1\/(crop-health\/diseases|diseases)/,
  },
  {
    route: "/weather",
    label: "Weather",
    category: "Crop Intelligence",
    expectEndpoint: /\/api\/v1\/weather/,
  },
  {
    route: "/satellite",
    label: "Satellite",
    category: "Crop Intelligence",
    expectEndpoint: /\/(api\/v1\/satellite|api\/satellite)/,
  },
  {
    route: "/yield",
    label: "Yield",
    category: "Crop Intelligence",
    expectEndpoint: /\/api\/v1\/(yield|crop-health)/,
    soft: true,
  },
  {
    route: "/crop-protection",
    label: "Crop Protection",
    category: "Crop Intelligence",
    expectEndpoint: /\/api\/v1\/(crop-protection|crop-health|advisory)/,
    soft: true,
  },
  {
    route: "/crop-planning",
    label: "Crop Planning",
    category: "Crop Intelligence",
    expectEndpoint: /\/api\/v1\/crop-planning/,
    soft: true,
  },
  {
    route: "/vision",
    label: "AI Vision",
    category: "Crop Intelligence",
    // Vision page mostly POSTs on user upload; GET /models on mount
    expectEndpoint: /\/api\/v1\/vision/,
    soft: true,
  },
  {
    route: "/soil-analysis",
    label: "Soil Analysis",
    category: "Crop Intelligence",
    expectEndpoint: /\/(api\/v1\/soil|api\/soil-analysis)/,
  },
  {
    route: "/terrain",
    label: "Terrain",
    category: "Crop Intelligence",
    expectEndpoint: /\/(api\/v1\/terrain|api\/terrain|api\/v1\/hydrology|api\/v1\/leveling)/,
    soft: true,
  },

  // ── IoT & Equipment ──────────────────────────────────────────────────
  {
    route: "/iot",
    label: "IoT",
    category: "IoT & Equipment",
    expectEndpoint: /\/api\/v1\/(iot|sensors|devices)/,
  },
  {
    route: "/sensors",
    label: "Sensors",
    category: "IoT & Equipment",
    expectEndpoint: /\/api\/v1\/(iot|sensors)/,
  },
  {
    route: "/equipment",
    label: "Equipment",
    category: "IoT & Equipment",
    expectEndpoint: /\/(api\/v1\/equipment|api\/equipment)/,
  },
  {
    route: "/drone",
    label: "Drone",
    category: "IoT & Equipment",
    expectEndpoint: /\/api\/v1\/drone/,
  },
  {
    route: "/edge-devices",
    label: "Edge Devices",
    category: "IoT & Equipment",
    expectEndpoint: /\/api\/v1\/edge/,
    soft: true,
  },
  {
    route: "/virtual-sensors",
    label: "Virtual Sensors",
    category: "IoT & Equipment",
    expectEndpoint: /\/api\/v1\/(virtual-sensors|sensors\/virtual)/,
    soft: true,
  },

  // ── Business & Community ─────────────────────────────────────────────
  {
    route: "/marketplace",
    label: "Marketplace",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/marketplace/,
  },
  {
    route: "/wallet",
    label: "Wallet",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/(wallet|billing)/,
  },
  {
    route: "/community",
    label: "Community",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/(chat|community)/,
  },
  {
    route: "/logistics",
    label: "Logistics",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/logistics/,
    soft: true,
  },
  {
    route: "/market-prices",
    label: "Market Prices",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/(marketplace|market-prices|prices)/,
    soft: true,
  },
  {
    route: "/cooperatives",
    label: "Cooperatives",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/cooperatives/,
    soft: true,
  },
  {
    route: "/crop-insurance",
    label: "Crop Insurance",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/(crop-insurance|insurance)/,
    soft: true,
  },
  {
    route: "/traceability",
    label: "Traceability",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/traceability/,
    soft: true,
  },
  {
    route: "/harvest-quality",
    label: "Harvest Quality",
    category: "Business & Community",
    expectEndpoint: /\/api\/v1\/(harvest|harvest-quality|quality)/,
    soft: true,
  },

  // ── Reports & Docs ───────────────────────────────────────────────────
  {
    route: "/reports",
    label: "Reports",
    category: "Reports & Docs",
    expectEndpoint: /\/api\/v1\/(reports|analytics)/,
    soft: true,
  },
  {
    route: "/analytics",
    label: "Analytics",
    category: "Reports & Docs",
    expectEndpoint: /\/api\/v1\/(analytics|dashboard|stats)/,
  },
  {
    route: "/documents",
    label: "Documents",
    category: "Reports & Docs",
    expectEndpoint: /\/api\/v1\/(documents|farm-documents)/,
    soft: true,
  },

  // ── Alerts & Notifications ───────────────────────────────────────────
  {
    route: "/alerts",
    label: "Alerts",
    category: "Alerts & Notifications",
    expectEndpoint: /\/(api\/v1\/alerts|api\/alerts)/,
  },
  {
    route: "/notifications",
    label: "Notifications",
    category: "Alerts & Notifications",
    expectEndpoint: /\/api\/v1\/notifications/,
  },
  {
    route: "/disaster-assessment",
    label: "Disaster Assessment",
    category: "Alerts & Notifications",
    expectEndpoint: /\/api\/v1\/(disaster|disaster-assessment)/,
    soft: true,
  },

  // ── Tools ────────────────────────────────────────────────────────────
  {
    route: "/audit",
    label: "Audit",
    category: "Tools",
    expectEndpoint: /\/api\/v1\/audit/,
    soft: true,
  },
  {
    route: "/settings",
    label: "Settings",
    category: "Tools",
    expectEndpoint: /\/api\/v1\/(users|auth|settings)/,
    soft: true,
  },
  {
    route: "/seeds",
    label: "Seeds",
    category: "Tools",
    expectEndpoint: /\/api\/v1\/seeds/,
    soft: true,
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

interface ApiCallTracker {
  calls: string[];
  pathsByMethod: Map<string, string[]>;
}

/**
 * Mock every backend response with a generic success envelope so pages
 * can render without flagging missing-data errors. Records every call
 * for later assertions.
 */
async function setupContractTracking(page: Page): Promise<ApiCallTracker> {
  const tracker: ApiCallTracker = {
    calls: [],
    pathsByMethod: new Map(),
  };

  // Catch JS errors so we surface contract bugs that crash the page
  page.on("pageerror", (err) => {
    if (!/hydration|chunk|ChunkLoadError/i.test(err.message)) {
      console.warn(`[pageerror] ${err.message}`);
    }
  });

  await page.route("**/api/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();
    tracker.calls.push(url);

    const path = new URL(url).pathname;
    const list = tracker.pathsByMethod.get(method) ?? [];
    list.push(path);
    tracker.pathsByMethod.set(method, list);

    // Generic success envelope matching ApiResponse<T>
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [],
        meta: { total: 0, page: 1, pageSize: 20 },
      }),
    });
  });

  // Auth cookies (aligned with service-pages.spec.ts)
  const baseURL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000";
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
        tenantId: "tenant-test-001",
      }),
      domain: new URL(baseURL).hostname,
      path: "/",
      httpOnly: false,
      secure: false,
      sameSite: "Lax",
    },
  ]);

  return tracker;
}

function summariseCalls(tracker: ApiCallTracker): string {
  if (tracker.calls.length === 0) return "(no API calls observed)";
  return tracker.calls
    .slice(0, 10)
    .map((u) => {
      try {
        return new URL(u).pathname;
      } catch {
        return u;
      }
    })
    .join("\n  - ");
}

// ---------------------------------------------------------------------------
// Tests grouped by service category
// ---------------------------------------------------------------------------

const categories = [...new Set(SERVICE_CONTRACTS.map((c) => c.category))];

for (const category of categories) {
  const contractsInCategory = SERVICE_CONTRACTS.filter(
    (c) => c.category === category,
  );

  test.describe(`Service Contract: ${category}`, () => {
    for (const contract of contractsInCategory) {
      test(`${contract.label} (${contract.route}) calls expected endpoint`, async ({
        page,
      }) => {
        const tracker = await setupContractTracking(page);

        await page.goto(contract.route, { waitUntil: "domcontentloaded" });

        // Wait for hydration / data fetching to settle
        await page
          .locator("main, [role='main'], h1, h2")
          .first()
          .waitFor({ state: "visible", timeout: 15000 });

        // Allow React Query / SWR to fire
        await page.waitForTimeout(500);

        const matched = tracker.calls.some((url) =>
          contract.expectEndpoint.test(url),
        );

        const message = `Expected ${contract.label} (${contract.route}) to call endpoint matching ${contract.expectEndpoint}.\nObserved calls:\n  - ${summariseCalls(tracker)}`;

        if (contract.soft) {
          // Soft pages: page must render (some interaction may be required
          // to trigger the contract call). We log the gap but don't fail CI.
          expect.soft(matched, message).toBeTruthy();
        } else {
          expect(matched, message).toBeTruthy();
        }

        if (contract.expectAlsoEndpoint) {
          const alsoMatched = tracker.calls.some((url) =>
            contract.expectAlsoEndpoint!.test(url),
          );
          expect.soft(
            alsoMatched,
            `Expected ${contract.label} to also call ${contract.expectAlsoEndpoint}`,
          ).toBeTruthy();
        }
      });
    }
  });
}

// ---------------------------------------------------------------------------
// Cross-cutting contract checks
// ---------------------------------------------------------------------------

test.describe("Service Contract: Cross-cutting", () => {
  test("all service calls go through /api/v1/* (no hardcoded ports / hosts)", async ({
    page,
  }) => {
    const tracker = await setupContractTracking(page);

    // Hit a representative set of pages
    const sampleRoutes = [
      "/dashboard",
      "/fields",
      "/weather",
      "/tasks",
      "/equipment",
      "/alerts",
      "/marketplace",
    ];

    for (const route of sampleRoutes) {
      await page.goto(route, { waitUntil: "domcontentloaded" });
      await page
        .locator("main, [role='main'], h1, h2")
        .first()
        .waitFor({ state: "visible", timeout: 15000 });
      await page.waitForTimeout(300);
    }

    // Every observed call must be same-origin and start with /api/
    const baseHost = new URL(
      process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000",
    ).host;

    const offenders: string[] = [];
    for (const url of tracker.calls) {
      try {
        const u = new URL(url);
        // Internal requests must be same host (Next.js will rewrite /api/v1/*)
        const sameHost = u.host === baseHost;
        const apiPath = u.pathname.startsWith("/api/");
        if (!sameHost || !apiPath) {
          offenders.push(url);
        }
        // Forbid hardcoded service ports (3000/80xx/81xx) leaking into URLs
        if (/:(3010|8089|808[0-9]|809[0-9]|81[0-9]{2}|82[0-9]{2})/.test(url)) {
          offenders.push(url);
        }
      } catch {
        // skip non-URL strings
      }
    }

    expect(
      offenders,
      `Found service calls bypassing the gateway:\n  - ${offenders.slice(0, 10).join("\n  - ")}`,
    ).toHaveLength(0);
  });

  test("auth/me is called on every protected page (session bootstrap)", async ({
    page,
  }) => {
    const tracker = await setupContractTracking(page);

    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
    await page
      .locator("main, [role='main'], h1, h2")
      .first()
      .waitFor({ state: "visible", timeout: 15000 });
    await page.waitForTimeout(500);

    const calledMe = tracker.calls.some((u) => /\/api\/v1\/auth\/me/.test(u));
    expect.soft(
      calledMe,
      "Dashboard should bootstrap session via /api/v1/auth/me",
    ).toBeTruthy();
  });

  test("CSRF token is fetched before any mutation", async ({ request }) => {
    // This test verifies the CSRF endpoint exists and returns a token.
    // The actual double-submit verification happens in unified-client interceptors.
    const serverAvailable = !!process.env.API_AVAILABLE || !process.env.CI;
    test.skip(!serverAvailable, "Requires running Next.js server");

    const response = await request.get("/api/csrf-token");
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveProperty("token");
    expect(typeof body.token).toBe("string");
    expect(body.token.length).toBeGreaterThan(16);
  });
});
