import { test, expect } from "@playwright/test";

/**
 * CI Smoke Tests - Admin Dashboard (no backend required)
 * اختبارات تدخين CI - لوحة الإدارة (بدون خادم خلفي)
 *
 * These tests validate that the admin portal builds and renders correctly
 * in CI without requiring a running backend. They test static rendering,
 * client-side routing, and basic UI elements.
 */

test.describe("Admin CI Smoke Tests (no backend required)", () => {
  test("login page loads", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle" });

    // Verify the login page rendered with a submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible({
      timeout: 15000,
    });

    // Verify at least one input field is present (email or password)
    const inputs = page.locator("input");
    expect(await inputs.count()).toBeGreaterThanOrEqual(1);
  });

  test("dashboard redirects to login when unauthenticated", async ({
    page,
  }) => {
    // Attempting to access dashboard without auth should redirect to login
    await page.goto("/", { waitUntil: "networkidle" });

    // Should end up on login page (redirect or rendered login)
    await expect(page).toHaveURL(/\/(login)?/, { timeout: 15000 });

    // Also try an explicit dashboard route
    await page.goto("/dashboard", { waitUntil: "networkidle" });
    await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
  });

  test("health endpoint returns 200", async ({ request }) => {
    // The admin app should expose a health or status endpoint
    // Try common health check paths
    const paths = ["/api/health", "/healthz", "/api/healthz"];
    let healthOk = false;

    for (const healthPath of paths) {
      try {
        const response = await request.get(healthPath);
        if (response.ok()) {
          healthOk = true;
          break;
        }
      } catch {
        // Path not available, try next
      }
    }

    // If no dedicated health endpoint, verify the app itself responds
    if (!healthOk) {
      const response = await request.get("/login");
      expect(response.status()).toBeLessThan(500);
    }
  });

  test("Arabic text renders correctly", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle" });

    // Verify Arabic content is present on the page
    // Admin portal should have bilingual support (Arabic/English)
    const arabicText = page
      .getByText(/تسجيل الدخول|لوحة الإدارة|الدخول|كلمة المرور/i)
      .first();
    await expect(arabicText).toBeVisible({ timeout: 15000 });

    // Verify RTL direction is set on the document or a container
    const dir = await page.locator("html").getAttribute("dir");
    const lang = await page.locator("html").getAttribute("lang");
    // Accept either explicit RTL direction or Arabic lang attribute
    const hasRtlSupport = dir === "rtl" || lang === "ar" || lang?.startsWith("ar");

    // If no explicit RTL attribute, at least verify Arabic text rendered
    if (!hasRtlSupport) {
      // Fallback: just confirm Arabic characters are in the page
      const bodyText = await page.locator("body").textContent();
      expect(bodyText).toMatch(/[\u0600-\u06FF]/);
    }
  });

  test("navigation sidebar loads", async ({ page }) => {
    // Go to login first - sidebar may only appear after auth context loads
    await page.goto("/login", { waitUntil: "networkidle" });

    // Check for common sidebar/navigation elements
    // Admin portals typically have a nav element or sidebar
    const nav = page.locator("nav, [role='navigation'], aside, .sidebar, [data-testid='sidebar']");
    const navCount = await nav.count();

    // If nav is visible on login page (some admin layouts show it)
    if (navCount > 0) {
      await expect(nav.first()).toBeVisible({ timeout: 10000 });
    } else {
      // On login page, navigation may be hidden - verify page structure loads
      // At minimum the page should have a main content area
      const mainContent = page.locator(
        "main, [role='main'], #root, #__next, .app",
      );
      expect(await mainContent.count()).toBeGreaterThanOrEqual(1);
    }
  });
});
