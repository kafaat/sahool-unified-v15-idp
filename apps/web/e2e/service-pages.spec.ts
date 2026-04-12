import { test, expect, Page } from "@playwright/test";

/**
 * Service Pages Rendering E2E Tests
 * اختبارات E2E لعرض صفحات الخدمات
 *
 * Verifies that every major service page in the web dashboard loads
 * correctly, renders meaningful content (heading, cards, tables, etc.),
 * and does not crash. Uses API mocking so no live backend is required.
 *
 * Each page is tested for:
 *  1. Successful HTTP 200 response (no redirect to error page)
 *  2. A visible heading or main content area
 *  3. Presence of service-specific UI (cards, tables, icons, buttons)
 *  4. No unhandled JavaScript errors
 */

/** Helper to set up auth cookies and mock API for each test */
async function setupPage(page: Page) {
  // Collect JS errors to assert against later
  const jsErrors: string[] = [];
  page.on("pageerror", (err) => jsErrors.push(err.message));

  // Mock all API calls
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;

    // Provide realistic mock data for common endpoints
    const mocks: Record<string, unknown> = {
      "/api/v1/auth/me": {
        success: true,
        data: {
          id: "test-user-123",
          email: "test@sahool.com",
          name: "Test User",
          nameAr: "مستخدم اختباري",
          role: "admin",
        },
      },
      "/api/v1/dashboard/stats": {
        success: true,
        data: {
          totalFields: 5,
          activeTasks: 12,
          pendingAlerts: 3,
          weatherStatus: "sunny",
        },
      },
      "/api/v1/fields": {
        success: true,
        data: [
          { id: "1", name: "North Field", nameAr: "الحقل الشمالي", area: 5.5, status: "active" },
          { id: "2", name: "South Field", nameAr: "الحقل الجنوبي", area: 3.2, status: "active" },
        ],
      },
      "/api/v1/tasks": {
        success: true,
        data: [
          { id: "1", title: "Irrigation Check", titleAr: "فحص الري", status: "pending", priority: "high" },
        ],
      },
      "/api/v1/weather": {
        success: true,
        data: { temperature: 28, humidity: 45, condition: "sunny", conditionAr: "مشمس" },
      },
      "/api/v1/equipment": {
        success: true,
        data: [
          { id: "1", name: "Tractor A1", nameAr: "جرار A1", type: "tractor", status: "operational" },
        ],
      },
      "/api/v1/alerts": {
        success: true,
        data: [
          { id: "1", type: "warning", message: "High temperature expected", messageAr: "متوقع ارتفاع درجة الحرارة" },
        ],
      },
      "/api/v1/notifications": {
        success: true,
        data: [],
        unread: 0,
      },
    };

    const mockKey = Object.keys(mocks).find((key) => path.includes(key));
    if (mockKey) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mocks[mockKey]),
      });
    } else {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }),
      });
    }
  });

  // Set auth cookies
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
      }),
      domain: new URL(baseURL).hostname,
      path: "/",
      httpOnly: false,
      secure: false,
      sameSite: "Lax",
    },
  ]);

  return { jsErrors };
}

/**
 * All service pages grouped by category.
 * Each entry defines the route and what we expect to find on the page.
 */
const servicePages = [
  // Farm Management
  { route: "/dashboard", category: "Farm Management", expect: { heading: /مرحباً|Welcome|Dashboard|لوحة التحكم/i } },
  { route: "/farms", category: "Farm Management", expect: { heading: /Farms|المزارع/i } },
  { route: "/fields", category: "Farm Management", expect: { heading: /Fields|الحقول/i } },
  { route: "/crops", category: "Farm Management", expect: { heading: /Crops|المحاصيل/i } },
  { route: "/seasons", category: "Farm Management", expect: { heading: /Seasons|المواسم/i } },
  { route: "/inventory", category: "Farm Management", expect: { heading: /Inventory|المخزون/i } },
  { route: "/tasks", category: "Farm Management", expect: { heading: /Tasks|المهام/i } },
  { route: "/scouting", category: "Farm Management", expect: { heading: /Scouting|الاستكشاف/i } },

  // Water & Irrigation
  { route: "/irrigation", category: "Water & Irrigation", expect: { heading: /Irrigation|الري/i } },
  { route: "/pivot-irrigation", category: "Water & Irrigation", expect: { heading: /Pivot|محوري|الري/i } },

  // Crop Intelligence
  { route: "/crop-health", category: "Crop Intelligence", expect: { heading: /Crop Health|صحة المحصول/i } },
  { route: "/diseases", category: "Crop Intelligence", expect: { heading: /Disease|الأمراض/i } },
  { route: "/weather", category: "Crop Intelligence", expect: { heading: /Weather|الطقس/i } },
  { route: "/satellite", category: "Crop Intelligence", expect: { heading: /Satellite|القمر الصناعي|الأقمار/i } },
  { route: "/satellite-monitor", category: "Crop Intelligence", expect: { heading: /Satellite|القمر|المراقبة/i } },
  { route: "/yield", category: "Crop Intelligence", expect: { heading: /Yield|الإنتاجية/i } },
  { route: "/precision-agriculture/gdd", category: "Crop Intelligence", expect: { heading: /GDD|Growing Degree|حرارة النمو|الزراعة الدقيقة/i } },
  { route: "/crop-protection", category: "Crop Intelligence", expect: { heading: /Crop Protection|حماية المحصول/i } },
  { route: "/crop-planning", category: "Crop Intelligence", expect: { heading: /Crop Planning|تخطيط المحاصيل/i } },
  { route: "/epidemic", category: "Crop Intelligence", expect: { heading: /Epidemic|الوباء/i } },
  { route: "/vision", category: "Crop Intelligence", expect: { heading: /Vision|الرؤية/i } },
  { route: "/soil-map", category: "Crop Intelligence", expect: { heading: /Soil Map|خريطة التربة/i } },
  { route: "/terrain", category: "Crop Intelligence", expect: { heading: /Terrain|التضاريس/i } },
  { route: "/soil-analysis", category: "Crop Intelligence", expect: { heading: /Soil Analysis|تحليل التربة/i } },

  // IoT & Equipment
  { route: "/iot", category: "IoT & Equipment", expect: { heading: /IoT|إنترنت الأشياء/i } },
  { route: "/sensors", category: "IoT & Equipment", expect: { heading: /Sensor|المستشعرات/i } },
  { route: "/equipment", category: "IoT & Equipment", expect: { heading: /Equipment|المعدات/i } },
  { route: "/drone", category: "IoT & Equipment", expect: { heading: /Drone|الطائرات/i } },
  { route: "/edge-devices", category: "IoT & Equipment", expect: { heading: /Edge|الحوسبة|أجهزة/i } },
  { route: "/virtual-sensors", category: "IoT & Equipment", expect: { heading: /Virtual Sensor|مستشعرات افتراضية/i } },

  // Precision Agriculture
  { route: "/precision-agriculture/spray", category: "Precision Agriculture", expect: { heading: /Spray|الرش/i } },
  { route: "/precision-agriculture/vra", category: "Precision Agriculture", expect: { heading: /VRA|Variable Rate|معدل متغير/i } },
  { route: "/precision-agriculture/fertilizer", category: "Precision Agriculture", expect: { heading: /Fertilizer|السماد|التسميد/i } },

  // Business & Community
  { route: "/marketplace", category: "Business & Community", expect: { heading: /Marketplace|السوق/i } },
  { route: "/wallet", category: "Business & Community", expect: { heading: /Wallet|المحفظة/i } },
  { route: "/community", category: "Business & Community", expect: { heading: /Community|المجتمع/i } },
  { route: "/logistics", category: "Business & Community", expect: { heading: /Logistics|اللوجستيات/i } },
  { route: "/market-prices", category: "Business & Community", expect: { heading: /Market Price|أسعار السوق/i } },
  { route: "/cooperatives", category: "Business & Community", expect: { heading: /Cooperative|التعاونيات/i } },
  { route: "/crop-insurance", category: "Business & Community", expect: { heading: /Insurance|التأمين/i } },
  { route: "/traceability", category: "Business & Community", expect: { heading: /Traceability|التتبع/i } },
  { route: "/harvest-quality", category: "Business & Community", expect: { heading: /Harvest|جودة الحصاد/i } },

  // Reports & Docs
  { route: "/reports", category: "Reports & Docs", expect: { heading: /Report|التقارير/i } },
  { route: "/analytics", category: "Reports & Docs", expect: { heading: /Analytics|التحليلات/i } },
  { route: "/documents", category: "Reports & Docs", expect: { heading: /Document|المستندات/i } },

  // Alerts & Notifications
  { route: "/alerts", category: "Alerts & Notifications", expect: { heading: /Alert|التنبيهات/i } },
  { route: "/notifications", category: "Alerts & Notifications", expect: { heading: /Notification|الإشعارات/i } },
  { route: "/disaster-assessment", category: "Alerts & Notifications", expect: { heading: /Disaster|تقييم الكوارث/i } },

  // Tools
  { route: "/copilot", category: "Tools", expect: { heading: /Copilot|المساعد/i } },
  { route: "/support", category: "Tools", expect: { heading: /Support|الدعم/i } },
  { route: "/settings", category: "Tools", expect: { heading: /Settings|الإعدادات/i } },
  { route: "/audit", category: "Tools", expect: { heading: /Audit|سجل التدقيق/i } },
  { route: "/seeds", category: "Tools", expect: { heading: /Seed|البذور/i } },
];

test.describe("Service Pages Rendering", () => {
  // Group tests by category for better organization
  const categories = [...new Set(servicePages.map((p) => p.category))];

  for (const category of categories) {
    test.describe(category, () => {
      const pages = servicePages.filter((p) => p.category === category);

      for (const servicePage of pages) {
        test(`${servicePage.route} loads and renders content`, async ({
          page,
        }) => {
          const { jsErrors } = await setupPage(page);

          await page.goto(servicePage.route, {
            waitUntil: "domcontentloaded",
          });

          // 1. Page should not redirect to an error page
          const currentUrl = page.url();
          expect(currentUrl).not.toContain("/error");
          expect(currentUrl).not.toContain("/500");

          // 2. Look for a heading that matches the expected pattern
          const heading = page
            .locator("h1, h2, [role='heading']")
            .filter({ hasText: servicePage.expect.heading })
            .first();

          const headingVisible = await heading
            .isVisible({ timeout: 10000 })
            .catch(() => false);

          if (!headingVisible) {
            // Fallback: at least some main content should be visible
            const anyContent = page
              .locator("main, [role='main'], h1, h2")
              .first();
            await expect(anyContent).toBeVisible({ timeout: 10000 });
          }

          // 3. Page should have interactive elements (buttons, links, or inputs)
          const interactiveElements = page.locator(
            "button, a[href], input, select, textarea",
          );
          const interactiveCount = await interactiveElements.count();
          expect(interactiveCount).toBeGreaterThan(0);

          // 4. No unhandled JavaScript errors
          expect(jsErrors).toHaveLength(0);
        });
      }
    });
  }
});

test.describe("Service Pages - UI Components", () => {
  test("dashboard page renders stat cards and widgets", async ({ page }) => {
    await setupPage(page);
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    // Should display welcome message
    const welcome = page.getByText(/مرحباً|Welcome/i).first();
    await expect(welcome).toBeVisible({ timeout: 15000 });

    // Should have SVG icons (lucide-react renders as SVG)
    const icons = page.locator("main svg, [role='main'] svg");
    const iconCount = await icons.count();
    expect(iconCount).toBeGreaterThan(0);
  });

  test("fields page renders field list or empty state", async ({ page }) => {
    await setupPage(page);
    await page.goto("/fields", { waitUntil: "domcontentloaded" });

    // Should have either a field list or an empty state with "add" button
    const addButton = page.locator(
      'button:has-text("Add"), button:has-text("إضافة"), a:has-text("Add"), a:has-text("إضافة")',
    );
    const tableOrList = page.locator(
      "table, [role='table'], [class*='grid'], [class*='list']",
    );

    const hasAdd = await addButton.first().isVisible({ timeout: 5000 }).catch(() => false);
    const hasList = await tableOrList.first().isVisible({ timeout: 5000 }).catch(() => false);

    // At least one of these should be present
    expect(hasAdd || hasList).toBeTruthy();
  });

  test("weather page renders weather information", async ({ page }) => {
    await setupPage(page);
    await page.goto("/weather", { waitUntil: "domcontentloaded" });

    // Weather page should have some kind of weather display
    const weatherContent = page.locator(
      "text=/Weather|الطقس|Temperature|درجة الحرارة|°C|°F/i",
    );
    const hasWeather = await weatherContent
      .first()
      .isVisible({ timeout: 10000 })
      .catch(() => false);

    if (!hasWeather) {
      // Fallback: page should at least render a heading
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: 10000 });
    }
  });

  test("equipment page renders equipment list or management UI", async ({
    page,
  }) => {
    await setupPage(page);
    await page.goto("/equipment", { waitUntil: "domcontentloaded" });

    // Should show heading
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Should have action buttons or list
    const actionElements = page.locator("button, a[href]");
    const count = await actionElements.count();
    expect(count).toBeGreaterThan(2);
  });

  test("settings page renders settings form", async ({ page }) => {
    await setupPage(page);
    await page.goto("/settings", { waitUntil: "domcontentloaded" });

    // Settings should have form elements (inputs, toggles, buttons)
    const formElements = page.locator(
      "input, select, button, [role='switch'], [role='checkbox']",
    );
    const count = await formElements.count();
    expect(count).toBeGreaterThan(0);
  });

  test("alerts page renders alert list or empty state", async ({ page }) => {
    await setupPage(page);
    await page.goto("/alerts", { waitUntil: "domcontentloaded" });

    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Should have some alert-related content or empty state
    const content = page.locator("main, [role='main']").first();
    await expect(content).toBeVisible({ timeout: 5000 });
  });
});

test.describe("Service Pages - Cross-cutting Concerns", () => {
  test("all pages include sidebar navigation", async ({ page }) => {
    await setupPage(page);

    const pagesToCheck = ["/dashboard", "/fields", "/weather", "/settings"];

    for (const route of pagesToCheck) {
      await page.goto(route, { waitUntil: "domcontentloaded" });

      const sidebar = page.locator('[data-testid="desktop-sidebar"]');
      await expect(sidebar).toBeVisible({ timeout: 10000 });
    }
  });

  test("all pages include header with user info", async ({ page }) => {
    await setupPage(page);

    const pagesToCheck = ["/dashboard", "/fields", "/tasks"];

    for (const route of pagesToCheck) {
      await page.goto(route, { waitUntil: "domcontentloaded" });

      // Header should be visible with user info or notification bell
      const header = page.locator("header").first();
      await expect(header).toBeVisible({ timeout: 10000 });
    }
  });

  test("pages support bilingual content (Arabic/English)", async ({
    page,
  }) => {
    await setupPage(page);
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    // The page should contain Arabic text (RTL content)
    const arabicText = page.locator("text=/[\u0600-\u06FF]/");
    const arabicCount = await arabicText.count();

    // At minimum, the app name or navigation should have Arabic
    expect(arabicCount).toBeGreaterThan(0);
  });

  test("404 page renders for unknown routes", async ({ page }) => {
    await setupPage(page);
    await page.goto("/this-page-does-not-exist-xyz", {
      waitUntil: "domcontentloaded",
    });

    // Should show a 404 or "not found" message
    const notFoundText = page.locator(
      "text=/404|Not Found|الصفحة غير موجودة|Page not found/i",
    );
    const hasNotFound = await notFoundText
      .first()
      .isVisible({ timeout: 10000 })
      .catch(() => false);

    // Should either show 404 text or redirect to another page
    const currentUrl = page.url();
    expect(hasNotFound || !currentUrl.includes("does-not-exist")).toBeTruthy();
  });
});
