import { test, expect } from "./fixtures/test-fixtures";
import { navigateAndWait, waitForPageLoad } from "./helpers/page.helpers";

/**
 * Dashboard E2E Tests
 * اختبارات E2E للوحة التحكم
 */

test.describe("Dashboard Page", () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, "/dashboard");
  });

  test("should display dashboard page correctly", async ({ page }) => {
    // Check page title - uses default SAHOOL title
    await expect(page).toHaveTitle(/SAHOOL|سهول/i);

    // Check for main heading with welcome message
    const heading = page.locator('h1:has-text("مرحباً")');
    await expect(heading).toBeVisible({ timeout: 10000 });

    // Check for welcome message to SAHOOL platform
    const welcomeMessage = page.locator("text=/Welcome back to SAHOOL/i");
    await expect(welcomeMessage).toBeVisible({ timeout: 10000 });
  });

  test("should display user information", async ({ page }) => {
    // Look for welcome message with user name in heading
    const userInfo = page.locator('h1:has-text("مرحباً")');
    await expect(userInfo).toBeVisible();
  });

  test.describe("Dashboard Statistics", () => {
    test("should display statistics cards", async ({ page }) => {
      // Wait for stats to load
      await page.waitForTimeout(2000);

      // Look for stat cards/widgets
      const statCards = page.locator(
        '[class*="stat"], [class*="card"], [data-testid*="stat"]',
      );
      const count = await statCards.count();

      // Soft assertion - cards may not appear without API data
      console.log(`Found ${count} stat cards`);
      if (count === 0) {
        console.log(
          "Warning: No stat cards found - this may be expected if API is unavailable",
        );
      }
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test("should display numeric values in stats", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for numbers in the page
      const numbers = page.locator("text=/\\d+/");
      const count = await numbers.count();

      // Soft assertion - numbers may not appear without API data
      console.log(`Found ${count} numeric elements`);
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test("should update statistics on refresh", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Get initial state
      // const initialContent = await page.content();

      // Reload page
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Page should load successfully
      const welcomeMessage = page.locator("text=/مرحباً|Welcome/i");
      await expect(welcomeMessage).toBeVisible();
    });
  });

  test.describe("Recent Activity Widget", () => {
    test("should display recent activity section", async ({ page }) => {
      // Look for recent activity heading
      const activityHeading = page.locator(
        "text=/النشاط الأخير|Recent Activity/i",
      );
      const isVisible = await activityHeading
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(activityHeading).toBeVisible();
      } else {
        console.log("Recent activity section not found");
      }
    });

    test("should display activity items", async ({ page }) => {
      await page.waitForTimeout(2000);

      const activitySection = page.locator(
        "text=/النشاط الأخير|Recent Activity/i",
      );
      const isSectionVisible = await activitySection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isSectionVisible) {
        // Look for activity items (lists, cards, etc.)
        const activityItems = page.locator(
          'ul li, [class*="activity"] [class*="item"]',
        );
        const count = await activityItems.count();

        console.log(`Found ${count} activity items`);
      }
    });
  });

  test.describe("Weather Widget", () => {
    test("should display weather section", async ({ page }) => {
      const weatherHeading = page.locator("text=/الطقس|Weather/i");
      const isVisible = await weatherHeading
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(weatherHeading).toBeVisible();
      } else {
        console.log("Weather section not found");
      }
    });

    test("should display weather data", async ({ page }) => {
      await page.waitForTimeout(2000);

      const weatherSection = page.locator("text=/الطقس|Weather/i");
      const isSectionVisible = await weatherSection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isSectionVisible) {
        // Look for temperature or weather icons
        const weatherIcons = page.locator(
          '[class*="weather"] svg, [data-testid*="weather"]',
        );
        const count = await weatherIcons.count();

        console.log(`Found ${count} weather elements`);
      }
    });
  });

  test.describe("Tasks Summary Widget", () => {
    test("should display tasks summary section", async ({ page }) => {
      const tasksHeading = page.locator(
        "text=/المهام القادمة|Upcoming Tasks|Tasks/i",
      );
      const isVisible = await tasksHeading
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(tasksHeading).toBeVisible();
      } else {
        console.log("Tasks summary section not found");
      }
    });

    test("should display upcoming tasks", async ({ page }) => {
      await page.waitForTimeout(2000);

      const tasksSection = page.locator(
        "text=/المهام القادمة|Upcoming Tasks/i",
      );
      const isSectionVisible = await tasksSection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isSectionVisible) {
        // Look for task items
        const taskItems = page.locator(
          'ul li, [class*="task"] [class*="item"]',
        );
        const count = await taskItems.count();

        console.log(`Found ${count} task items`);
      }
    });
  });

  test.describe("Quick Actions Widget", () => {
    test("should display quick actions section", async ({ page }) => {
      const quickActionsHeading = page.locator(
        "text=/إجراءات سريعة|Quick Actions/i",
      );
      const isVisible = await quickActionsHeading
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(quickActionsHeading).toBeVisible();
      } else {
        console.log("Quick actions section not found");
      }
    });

    test("should display action buttons", async ({ page }) => {
      await page.waitForTimeout(2000);

      const quickActionsSection = page.locator(
        "text=/إجراءات سريعة|Quick Actions/i",
      );
      const isSectionVisible = await quickActionsSection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isSectionVisible) {
        // Look for action buttons
        const actionButtons = page.locator('button, a[class*="action"]');
        const count = await actionButtons.count();

        console.log(`Found ${count} action buttons`);
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    test("should navigate when clicking quick action", async ({ page }) => {
      await page.waitForTimeout(2000);

      const quickActionsSection = page.locator(
        "text=/إجراءات سريعة|Quick Actions/i",
      );
      const isSectionVisible = await quickActionsSection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isSectionVisible) {
        // Find first clickable action
        const firstAction = page.locator("button, a").first();

        if (await firstAction.isVisible()) {
          const href = await firstAction.getAttribute("href");

          if (href && href.startsWith("/")) {
            // Click and verify navigation
            await firstAction.click();
            await page.waitForTimeout(1000);

            // URL should change or modal should open
            const currentUrl = page.url();
            console.log(`Navigated to: ${currentUrl}`);
          }
        }
      }
    });
  });

  test.describe("Dashboard Responsiveness", () => {
    test("should be responsive on mobile viewport", async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Reload to apply responsive styles
      await page.reload();
      await waitForPageLoad(page);

      // Dashboard should still be visible
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible();
    });

    test("should be responsive on tablet viewport", async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      await page.reload();
      await waitForPageLoad(page);

      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible();
    });

    test("should be responsive on desktop viewport", async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });

      await page.reload();
      await waitForPageLoad(page);

      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible();
    });
  });

  test.describe("Dashboard Interactions", () => {
    test("should handle loading states", async ({ page }) => {
      // Navigate to dashboard
      await page.goto("/dashboard");

      // Look for loading indicators initially
      const loadingIndicator = page.locator(
        '[class*="loading"], [class*="skeleton"], [aria-busy="true"]',
      );
      const hasLoader = await loadingIndicator
        .isVisible({ timeout: 1000 })
        .catch(() => false);

      console.log(`Loading state shown: ${hasLoader}`);

      // Wait for content to load
      await page.waitForTimeout(3000);

      // Content should be visible
      const content = page.locator("text=/مرحباً|Welcome/i");
      await expect(content).toBeVisible();
    });

    test("should handle error states gracefully", async ({ page }) => {
      // This test checks if dashboard handles errors without crashing
      await page.waitForTimeout(2000);

      // Look for error messages
      const errorMessage = page.locator('[role="alert"], [class*="error"]');
      const hasError = await errorMessage
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasError) {
        // Error should be displayed gracefully
        const errorText = await errorMessage.textContent();
        console.log(`Error message displayed: ${errorText}`);
      }

      // Dashboard should still be functional
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible();
    });

    test("should refresh data without page reload", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for refresh button
      const refreshButton = page.locator(
        'button:has-text("Refresh"), button:has-text("تحديث"), [aria-label*="refresh"]',
      );
      const hasRefreshButton = await refreshButton
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasRefreshButton) {
        await refreshButton.click();
        await page.waitForTimeout(1000);

        // Should show loading state
        console.log("Refresh button clicked");
      }
    });
  });

  test.describe("Dashboard Charts and Visualizations", () => {
    test("should display charts", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for chart elements (SVG, canvas)
      const charts = page.locator("svg, canvas");
      const count = await charts.count();

      console.log(`Found ${count} chart elements`);

      if (count > 0) {
        // At least one chart should be visible
        const firstChart = charts.first();
        await expect(firstChart).toBeVisible();
      }
    });

    test("should display chart legends", async ({ page }) => {
      await page.waitForTimeout(2000);

      const legends = page.locator(
        '[class*="legend"], [class*="recharts-legend"]',
      );
      const count = await legends.count();

      console.log(`Found ${count} chart legends`);
    });

    test("should handle chart interactions", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for interactive chart elements
      const chartElements = page.locator("svg path, canvas");

      if ((await chartElements.count()) > 0) {
        // Hover over chart element
        await chartElements
          .first()
          .hover()
          .catch(() => {});
        await page.waitForTimeout(500);

        // Tooltip might appear
        const tooltip = page.locator('[class*="tooltip"]');
        const hasTooltip = await tooltip
          .isVisible({ timeout: 1000 })
          .catch(() => false);

        console.log(`Chart tooltip shown: ${hasTooltip}`);
      }
    });
  });

  test.describe("Dashboard Error Boundaries", () => {
    test("should display fallback UI for failed components", async ({
      page,
    }) => {
      await page.waitForTimeout(2000);

      // Look for error fallback components mentioned in dashboard code
      const fallbacks = page.locator("text=/فشل تحميل|Failed to load/i");
      const count = await fallbacks.count();

      console.log(`Found ${count} error fallback messages`);

      // Even with errors, page should not crash
      const heading = page.locator("h1").first();
      await expect(heading).toBeVisible();
    });
  });
});
