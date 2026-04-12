import { test, expect } from "@playwright/test";

/**
 * Sidebar Navigation & Icons E2E Tests
 * اختبارات E2E للشريط الجانبي والأيقونات
 *
 * Verifies that every sidebar navigation group, link, and icon renders
 * correctly and that clicking each link navigates to the expected page
 * without crashing. Runs against static rendering (no backend needed).
 *
 * Uses `waitUntil: "domcontentloaded"` to avoid networkidle flakiness.
 */

/**
 * Complete map of every sidebar navigation group and its items,
 * mirroring the navGroups array in sidebar.tsx.
 */
const sidebarGroups = [
  {
    groupKey: "overview",
    items: [{ href: "/dashboard", hasIcon: true }],
  },
  {
    groupKey: "farmManagement",
    items: [
      { href: "/farms", hasIcon: true },
      { href: "/fields", hasIcon: true },
      { href: "/crops", hasIcon: true },
      { href: "/seasons", hasIcon: true },
      { href: "/inventory", hasIcon: true },
      { href: "/tasks", hasIcon: true },
      { href: "/scouting", hasIcon: true },
    ],
  },
  {
    groupKey: "waterAndIrrigation",
    items: [
      { href: "/irrigation", hasIcon: true },
      { href: "/pivot-irrigation", hasIcon: true },
    ],
  },
  {
    groupKey: "cropIntelligence",
    items: [
      { href: "/crop-health", hasIcon: true },
      { href: "/diseases", hasIcon: true },
      { href: "/weather", hasIcon: true },
      { href: "/satellite", hasIcon: true },
      { href: "/satellite-monitor", hasIcon: true },
      { href: "/yield", hasIcon: true },
      { href: "/precision-agriculture/gdd", hasIcon: true },
      { href: "/crop-protection", hasIcon: true },
      { href: "/crop-planning", hasIcon: true },
      { href: "/epidemic", hasIcon: true },
      { href: "/vision", hasIcon: true },
      { href: "/soil-map", hasIcon: true },
      { href: "/terrain", hasIcon: true },
      { href: "/soil-analysis", hasIcon: true },
    ],
  },
  {
    groupKey: "iotAndEquipment",
    items: [
      { href: "/iot", hasIcon: true },
      { href: "/sensors", hasIcon: true },
      { href: "/equipment", hasIcon: true },
      { href: "/drone", hasIcon: true },
      { href: "/edge-devices", hasIcon: true },
      { href: "/virtual-sensors", hasIcon: true },
    ],
  },
  {
    groupKey: "precisionAgriculture",
    items: [
      { href: "/precision-agriculture/spray", hasIcon: true },
      { href: "/precision-agriculture/vra", hasIcon: true },
      { href: "/precision-agriculture/fertilizer", hasIcon: true },
    ],
  },
  {
    groupKey: "businessAndCommunity",
    items: [
      { href: "/marketplace", hasIcon: true },
      { href: "/wallet", hasIcon: true },
      { href: "/community", hasIcon: true },
      { href: "/logistics", hasIcon: true },
      { href: "/market-prices", hasIcon: true },
      { href: "/cooperatives", hasIcon: true },
      { href: "/crop-insurance", hasIcon: true },
      { href: "/traceability", hasIcon: true },
      { href: "/harvest-quality", hasIcon: true },
    ],
  },
  {
    groupKey: "reportsAndDocs",
    items: [
      { href: "/reports", hasIcon: true },
      { href: "/analytics", hasIcon: true },
      { href: "/documents", hasIcon: true },
      { href: "/analytics/field-compare", hasIcon: true },
      { href: "/reports/seasonal", hasIcon: true },
    ],
  },
  {
    groupKey: "alertsAndNotifications",
    items: [
      { href: "/alerts", hasIcon: true },
      { href: "/notifications", hasIcon: true },
      { href: "/disaster-assessment", hasIcon: true },
    ],
  },
  {
    groupKey: "tools",
    items: [
      { href: "/copilot", hasIcon: true },
      { href: "/support", hasIcon: true },
      { href: "/settings", hasIcon: true },
      { href: "/audit", hasIcon: true },
      { href: "/seeds", hasIcon: true },
    ],
  },
];

/** Total number of navigation links across all groups */
const TOTAL_NAV_LINKS = sidebarGroups.reduce(
  (sum, g) => sum + g.items.length,
  0,
);

test.describe("Sidebar Navigation & Icons", () => {
  test.beforeEach(async ({ page }) => {
    // Mock API calls so the dashboard renders without a backend
    await page.route("**/api/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }),
      });
    });

    // Set auth cookies to bypass login redirect
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
  });

  test("sidebar renders with correct number of navigation links", async ({
    page,
  }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    // Desktop sidebar should be visible
    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    // Count all navigation links inside the sidebar
    const navLinks = sidebar.locator("a[href]");
    const count = await navLinks.count();

    // +1 for the logo link to /dashboard
    expect(count).toBeGreaterThanOrEqual(TOTAL_NAV_LINKS);
  });

  test("every sidebar link has an SVG icon", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    // Each nav link (inside <li>) should contain an SVG icon
    const navItems = sidebar.locator("nav li a");
    const itemCount = await navItems.count();
    expect(itemCount).toBe(TOTAL_NAV_LINKS);

    for (let i = 0; i < itemCount; i++) {
      const link = navItems.nth(i);
      const svg = link.locator("svg");
      await expect(svg).toBeVisible({ timeout: 5000 });
    }
  });

  test("all navigation group headers are visible", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    // Group headers are rendered as uppercase divs with tracking-wider
    // "overview" group has no header, so we expect groupCount - 1 headers
    const groupHeaders = sidebar.locator(
      "div.uppercase.tracking-wider",
    );
    const headerCount = await groupHeaders.count();

    // 10 groups total, "overview" has no header = 9 headers
    expect(headerCount).toBe(sidebarGroups.length - 1);
  });

  test("sidebar shows app name and version", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    // App name (SAHOOL or سهول)
    await expect(
      sidebar.getByText(/SAHOOL|سهول/).first(),
    ).toBeVisible();

    // Version badge
    await expect(sidebar.getByText("16.0.0")).toBeVisible();
  });

  test("active link is highlighted when on dashboard", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    // The dashboard link should have aria-current="page"
    const dashboardLink = sidebar.locator('a[href="/dashboard"]').last();
    await expect(dashboardLink).toHaveAttribute("aria-current", "page");
  });

  // Test each navigation group renders its links
  for (const group of sidebarGroups) {
    test(`group "${group.groupKey}" renders all ${group.items.length} links`, async ({
      page,
    }) => {
      await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

      const sidebar = page.locator('[data-testid="desktop-sidebar"]');
      await expect(sidebar).toBeVisible({ timeout: 15000 });

      for (const item of group.items) {
        const link = sidebar.locator(`a[href="${item.href}"]`);
        await expect(link).toBeVisible({ timeout: 5000 });

        // Verify the icon SVG is present inside the link
        const icon = link.locator("svg");
        await expect(icon).toBeVisible();
      }
    });
  }

  // Test clicking sidebar links navigates to each page without crashing
  const criticalPages = [
    "/dashboard",
    "/fields",
    "/tasks",
    "/weather",
    "/irrigation",
    "/crop-health",
    "/equipment",
    "/marketplace",
    "/settings",
    "/alerts",
    "/analytics",
    "/copilot",
  ];

  for (const href of criticalPages) {
    test(`clicking sidebar link navigates to ${href}`, async ({ page }) => {
      await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

      const sidebar = page.locator('[data-testid="desktop-sidebar"]');
      await expect(sidebar).toBeVisible({ timeout: 15000 });

      const link = sidebar.locator(`a[href="${href}"]`).last();
      await expect(link).toBeVisible({ timeout: 5000 });

      await link.click();

      // URL should change to the expected page
      await expect(page).toHaveURL(new RegExp(href.replace("/", "\\/")), {
        timeout: 15000,
      });

      // Page should not show an unhandled error (i.e., a heading or content renders)
      const pageContent = page.locator("h1, h2, main, [role='main']").first();
      await expect(pageContent).toBeVisible({ timeout: 10000 });
    });
  }

  test.describe("Mobile Sidebar", () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test("mobile sidebar is hidden by default", async ({ page }) => {
      await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

      // Desktop sidebar should be hidden on mobile
      const desktopSidebar = page.locator(
        '[data-testid="desktop-sidebar"]',
      );
      await expect(desktopSidebar).toBeHidden({ timeout: 10000 });
    });

    test("hamburger menu opens mobile drawer", async ({ page }) => {
      await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

      // Find the hamburger / menu button
      const menuButton = page
        .locator(
          'button[aria-label*="menu" i], button[aria-label*="القائمة" i], button:has(svg)',
        )
        .first();

      // Wait for page to be interactive
      await page.waitForTimeout(2000);

      if (await menuButton.isVisible({ timeout: 5000 })) {
        await menuButton.click();

        // Mobile drawer should appear
        const drawer = page.locator('[data-testid="mobile-drawer"]');
        await expect(drawer).toBeVisible({ timeout: 5000 });

        // Drawer should contain navigation links
        const drawerLinks = drawer.locator("nav a[href]");
        const count = await drawerLinks.count();
        expect(count).toBeGreaterThanOrEqual(10);
      }
    });
  });
});
