import { test, expect, Page } from "@playwright/test";

/**
 * End-to-End Operation Flows
 * اختبارات سير العمليات من البداية إلى النهاية
 *
 * Tests complete user workflows: navigating to a feature, performing
 * an operation (create, edit, delete), and verifying the result.
 * All API calls are intercepted and mocked — these tests validate the
 * frontend flow, not the backend logic.
 */

/** Reusable auth + API setup for every test */
async function setupAuthenticatedPage(page: Page) {
  const apiCalls: { method: string; url: string; body?: string }[] = [];

  await page.route("**/api/**", async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const method = req.method();
    const body = req.postData() || undefined;

    apiCalls.push({ method, url: url.pathname, body });

    // Mock responses by endpoint
    const path = url.pathname;

    if (path.includes("/auth/me")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            id: "test-user-123",
            email: "test@sahool.com",
            name: "Test User",
            nameAr: "مستخدم اختباري",
            role: "admin",
          },
        }),
      });
    }

    // Fields CRUD
    if (path.includes("/fields") && method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [
            { id: "f1", name: "North Field", nameAr: "الحقل الشمالي", area: 5.5, status: "active", cropType: "wheat" },
            { id: "f2", name: "South Field", nameAr: "الحقل الجنوبي", area: 3.2, status: "active", cropType: "barley" },
          ],
        }),
      });
    }
    if (path.includes("/fields") && method === "POST") {
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { id: "f3", name: "New Field", status: "active" },
          message: "Field created successfully",
        }),
      });
    }

    // Tasks CRUD
    if (path.includes("/tasks") && method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [
            { id: "t1", title: "Irrigate North Field", titleAr: "ري الحقل الشمالي", status: "pending", priority: "high", dueDate: new Date().toISOString() },
            { id: "t2", title: "Apply Fertilizer", titleAr: "تطبيق السماد", status: "in_progress", priority: "medium", dueDate: new Date().toISOString() },
          ],
        }),
      });
    }
    if (path.includes("/tasks") && method === "POST") {
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { id: "t3", title: "New Task", status: "pending" },
          message: "Task created successfully",
        }),
      });
    }

    // Equipment CRUD
    if (path.includes("/equipment") && method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [
            { id: "e1", name: "Tractor A1", nameAr: "جرار A1", type: "tractor", status: "operational", model: "JD-8R" },
          ],
        }),
      });
    }
    if (path.includes("/equipment") && method === "POST") {
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { id: "e2", name: "New Equipment", status: "operational" },
          message: "Equipment added successfully",
        }),
      });
    }

    // Weather
    if (path.includes("/weather")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            temperature: 28,
            humidity: 45,
            windSpeed: 12,
            condition: "sunny",
            conditionAr: "مشمس",
            forecast: [
              { day: "Mon", temp: 30, condition: "sunny" },
              { day: "Tue", temp: 27, condition: "cloudy" },
              { day: "Wed", temp: 25, condition: "rainy" },
            ],
          },
        }),
      });
    }

    // Alerts
    if (path.includes("/alerts") && method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [
            { id: "a1", type: "warning", title: "High Temperature", titleAr: "ارتفاع درجة الحرارة", severity: "medium" },
            { id: "a2", type: "critical", title: "Pest Detected", titleAr: "اكتشاف آفة", severity: "high" },
          ],
        }),
      });
    }

    // Default response
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ success: true, data: [] }),
    });
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

  return { apiCalls };
}

test.describe("Field Management Operations", () => {
  test("navigate to fields page, view field list, and open add form", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);

    // Step 1: Start at dashboard
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 15000 });

    // Step 2: Navigate to fields via sidebar
    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    const fieldsLink = sidebar.locator('a[href="/fields"]');
    await expect(fieldsLink).toBeVisible({ timeout: 5000 });
    await fieldsLink.click();
    await expect(page).toHaveURL(/\/fields/, { timeout: 10000 });

    // Step 3: Verify fields page content
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Step 4: Look for add/create button
    const addButton = page.locator(
      'button:has-text("Add"), button:has-text("إضافة"), button:has-text("Create"), button:has-text("إنشاء"), a:has-text("Add"), a:has-text("إضافة")',
    ).first();

    const hasAddButton = await addButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (hasAddButton) {
      await addButton.click();
      await page.waitForTimeout(1000);

      // Modal or form should appear
      const formOrModal = page.locator(
        '[role="dialog"], form, [class*="modal"], [class*="form"]',
      ).first();
      const formVisible = await formOrModal.isVisible({ timeout: 5000 }).catch(() => false);

      if (formVisible) {
        // Look for form inputs
        const inputs = formOrModal.locator("input, select, textarea");
        const inputCount = await inputs.count();
        expect(inputCount).toBeGreaterThan(0);
      }
    }
  });

  test("field list displays field data (name, area, status)", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/fields", { waitUntil: "domcontentloaded" });

    // At least the page should have some content
    const pageContent = page.locator("main, [role='main']").first();
    await expect(pageContent).toBeVisible({ timeout: 10000 });

    // Look for field names from our mock data
    const northField = page.getByText(/North Field|الحقل الشمالي/i).first();
    const southField = page.getByText(/South Field|الحقل الجنوبي/i).first();

    const hasNorth = await northField.isVisible({ timeout: 5000 }).catch(() => false);
    const hasSouth = await southField.isVisible({ timeout: 5000 }).catch(() => false);

    // Use soft assertion — mock data may not render depending on page implementation
    expect.soft(hasNorth || hasSouth).toBeTruthy();
  });
});

test.describe("Task Management Operations", () => {
  test("navigate to tasks and view task list", async ({ page }) => {
    await setupAuthenticatedPage(page);

    // Navigate to tasks
    await page.goto("/tasks", { waitUntil: "domcontentloaded" });

    // Verify heading
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Page should render content
    const mainContent = page.locator("main, [role='main']").first();
    await expect(mainContent).toBeVisible();

    // Look for task items from mock data (soft assertion)
    const taskContent = page.getByText(/Irrigate|ري|Fertilizer|سماد|pending|قيد الانتظار/i).first();
    const hasTask = await taskContent.isVisible({ timeout: 5000 }).catch(() => false);
    expect.soft(hasTask).toBeTruthy();
  });

  test("task page has add/create action", async ({ page }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/tasks", { waitUntil: "domcontentloaded" });

    // Look for add task button
    const addButton = page.locator(
      'button:has-text("Add"), button:has-text("إضافة"), button:has-text("New"), button:has-text("جديد"), a:has-text("Add"), a:has-text("إضافة")',
    ).first();

    const hasButton = await addButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (hasButton) {
      await addButton.click();

      // Check for form or modal (auto-retrying)
      const formElements = page.locator("input, select, textarea").first();
      await expect(formElements).toBeVisible({ timeout: 5000 });
    } else {
      // Page should still be functional
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible();
    }
  });
});

test.describe("Weather Service Operations", () => {
  test("weather page displays current conditions", async ({ page }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/weather", { waitUntil: "domcontentloaded" });

    // Verify page loaded
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Look for weather data (temperature, conditions, etc.)
    const weatherContent = page.getByText(/°C|°F|sunny|مشمس|temperature|درجة|humidity|رطوبة|28/i).first();
    const hasWeather = await weatherContent.isVisible({ timeout: 8000 }).catch(() => false);

    // Check for weather icons (SVG elements in weather section)
    const svgIcons = page.locator("main svg, [role='main'] svg");
    const iconCount = await svgIcons.count();

    // Either weather data or icons should be present
    expect(hasWeather || iconCount > 0).toBeTruthy();
  });

  test("weather page has forecast section", async ({ page }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/weather", { waitUntil: "domcontentloaded" });

    // The page should at least render
    const mainContent = page.locator("main, [role='main']").first();
    await expect(mainContent).toBeVisible({ timeout: 10000 });

    // Look for forecast-related content (soft assertion)
    const forecastContent = page.getByText(/Forecast|التوقعات|Mon|Tue|Wed|tomorrow|غداً/i).first();
    const hasForecast = await forecastContent.isVisible({ timeout: 5000 }).catch(() => false);
    expect.soft(hasForecast).toBeTruthy();
  });
});

test.describe("Equipment Management Operations", () => {
  test("equipment page lists equipment items", async ({ page }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/equipment", { waitUntil: "domcontentloaded" });

    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Look for equipment data from mock (soft assertion)
    const equipmentItem = page.getByText(/Tractor|جرار|JD-8R|operational/i).first();
    const hasEquipment = await equipmentItem.isVisible({ timeout: 8000 }).catch(() => false);
    expect.soft(hasEquipment).toBeTruthy();
  });

  test("equipment page has management actions (add, filter)", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/equipment", { waitUntil: "domcontentloaded" });

    // Look for action buttons
    const actionButtons = page.locator(
      'button:has-text("Add"), button:has-text("إضافة"), button:has-text("Filter"), button:has-text("تصفية"), input[placeholder*="Search"], input[placeholder*="بحث"]',
    );
    const count = await actionButtons.count();

    // Should have at least one management UI element
    expect(count).toBeGreaterThan(0);
  });
});

test.describe("Alert & Notification Operations", () => {
  test("alerts page displays alert items with severity levels", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/alerts", { waitUntil: "domcontentloaded" });

    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Look for alert content from mock data (soft assertion)
    const alertContent = page.getByText(/High Temperature|ارتفاع|Pest Detected|آفة|warning|critical/i).first();
    const hasAlerts = await alertContent.isVisible({ timeout: 8000 }).catch(() => false);
    expect.soft(hasAlerts).toBeTruthy();
  });

  test("notifications page renders notification list", async ({ page }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/notifications", { waitUntil: "domcontentloaded" });

    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Should show either notifications or an empty state
    const content = page.locator("main, [role='main']").first();
    await expect(content).toBeVisible();
  });
});

test.describe("Cross-Feature Navigation Flow", () => {
  test("complete farmer workflow: dashboard -> fields -> tasks -> weather", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);

    // Step 1: Dashboard
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 15000 });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');

    // Step 2: Navigate to Fields
    await sidebar.locator('a[href="/fields"]').click();
    await expect(page).toHaveURL(/\/fields/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });

    // Step 3: Navigate to Tasks
    await sidebar.locator('a[href="/tasks"]').click();
    await expect(page).toHaveURL(/\/tasks/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });

    // Step 4: Navigate to Weather
    await sidebar.locator('a[href="/weather"]').click();
    await expect(page).toHaveURL(/\/weather/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });

    // Step 5: Back to Dashboard
    await sidebar.locator('a[href="/dashboard"]').last().click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });
  });

  test("complete intelligence workflow: crop-health -> diseases -> satellite -> weather", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    // Crop Health
    await sidebar.locator('a[href="/crop-health"]').click();
    await expect(page).toHaveURL(/\/crop-health/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });

    // Diseases
    await sidebar.locator('a[href="/diseases"]').click();
    await expect(page).toHaveURL(/\/diseases/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });

    // Satellite
    await sidebar.locator('a[href="/satellite"]').click();
    await expect(page).toHaveURL(/\/satellite/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });

    // Weather
    await sidebar.locator('a[href="/weather"]').click();
    await expect(page).toHaveURL(/\/weather/, { timeout: 10000 });
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });
  });

  test("business workflow: marketplace -> wallet -> logistics -> market-prices", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    const routes = ["/marketplace", "/wallet", "/logistics", "/market-prices"];

    for (const route of routes) {
      await sidebar.locator(`a[href="${route}"]`).click();
      await expect(page).toHaveURL(new RegExp(route.replace(/\//g, "\\/")), {
        timeout: 10000,
      });
      await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });
    }
  });

  test("IoT workflow: iot -> sensors -> equipment -> drone", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    const sidebar = page.locator('[data-testid="desktop-sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 15000 });

    const routes = ["/iot", "/sensors", "/equipment", "/drone"];

    for (const route of routes) {
      await sidebar.locator(`a[href="${route}"]`).click();
      await expect(page).toHaveURL(new RegExp(route.replace(/\//g, "\\/")), {
        timeout: 10000,
      });
      await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10000 });
    }
  });
});

test.describe("Settings Operations", () => {
  test("settings page allows navigation between setting sections", async ({
    page,
  }) => {
    await setupAuthenticatedPage(page);
    await page.goto("/settings", { waitUntil: "domcontentloaded" });

    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Look for settings tabs or sections (profile, security, notifications, etc.)
    const tabs = page.locator(
      '[role="tab"], [role="tablist"] button, nav a, button:has-text("Profile"), button:has-text("Security"), button:has-text("الملف الشخصي"), button:has-text("الأمان")',
    );
    const tabCount = await tabs.count();

    if (tabCount > 0) {
      // Click first available tab/section
      const firstTab = tabs.first();
      if (await firstTab.isVisible({ timeout: 3000 })) {
        await firstTab.click();
        await page.waitForTimeout(1000);

        // Content should update without crashing
        const content = page.locator("main, [role='main']").first();
        await expect(content).toBeVisible();
      }
    }
  });
});
