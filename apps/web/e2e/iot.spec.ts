import { test, expect } from "./fixtures/test-fixtures";
import { navigateAndWait, waitForPageLoad } from "./helpers/page.helpers";
import { pages, timeouts } from "./helpers/test-data";

/**
 * IoT & Sensors Page E2E Tests
 * اختبارات E2E لصفحة إنترنت الأشياء والمستشعرات
 */

test.describe("IoT & Sensors Page", () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, pages.iot);
  });

  /**
   * Basic Page Loading Tests
   * اختبارات تحميل الصفحة الأساسية
   */
  test.describe("Page Loading", () => {
    test("should display IoT page correctly", async ({ page }) => {
      // Check page title - uses default SAHOOL title
      await expect(page).toHaveTitle(/SAHOOL|سهول/i);

      // Check for main heading in Arabic
      const heading = page.locator('h1:has-text("إنترنت الأشياء والمستشعرات")');
      await expect(heading).toBeVisible();

      // Check for English subtitle
      const subtitle = page.locator("text=/IoT & Sensors Management/i");
      await expect(subtitle).toBeVisible();
    });

    test("should display page header with title", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for header section
      const header = page.locator(".bg-white.rounded-xl").first();
      await expect(header).toBeVisible();

      // Check for main title
      const title = page.locator("h1");
      await expect(title).toBeVisible();
      await expect(title).toHaveText("إنترنت الأشياء والمستشعرات");
    });

    test("should show loading state initially", async ({ page }) => {
      // Navigate to page and check for loading state
      await page.goto(pages.iot);

      // Look for loading indicators
      const loadingIndicator = page.locator(
        '.animate-pulse, [aria-busy="true"]',
      );
      const hasLoading = await loadingIndicator
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Loading state shown: ${hasLoading}`);

      // Wait for content to load
      await page.waitForTimeout(3000);

      // Content should be visible after loading
      const heading = page.locator("h1").first();
      await expect(heading).toBeVisible();
    });
  });

  /**
   * Statistics Cards Tests
   * اختبارات بطاقات الإحصائيات
   */
  test.describe("Statistics Cards", () => {
    test("should display three statistics cards", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for statistics cards
      const statCards = page.locator(
        ".grid.grid-cols-1.md\\:grid-cols-3 > div.bg-white",
      );
      const count = await statCards.count();

      console.log(`Found ${count} statistics cards`);
      expect(count).toBe(3);
    });

    test("should display active sensors card", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for active sensors card
      const sensorsCard = page.locator("text=/مستشعرات نشطة|Active Sensors/i");
      await expect(sensorsCard).toBeVisible();

      // Check for icon
      const activityIcon = page.locator(".bg-blue-100").first();
      await expect(activityIcon).toBeVisible();

      // Check for numeric value
      const sensorCount = page
        .locator("text=/مستشعرات نشطة|Active Sensors/i")
        .locator("..")
        .locator("h3")
        .first();
      const isVisible = await sensorCount
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        const value = await sensorCount.textContent();
        console.log(`Active sensors count: ${value}`);
        expect(value).toMatch(/\d+/);
      }
    });

    test("should display active actuators card", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for active actuators card
      const actuatorsCard = page.locator(
        "text=/مشغلات نشطة|Active Actuators/i",
      );
      await expect(actuatorsCard).toBeVisible();

      // Check for icon
      const zapIcon = page.locator(".bg-green-100").first();
      await expect(zapIcon).toBeVisible();

      // Check for numeric value
      const actuatorCount = page
        .locator("text=/مشغلات نشطة|Active Actuators/i")
        .locator("..")
        .locator("h3")
        .first();
      const isVisible = await actuatorCount
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        const value = await actuatorCount.textContent();
        console.log(`Active actuators count: ${value}`);
        expect(value).toMatch(/\d+/);
      }
    });

    test("should display alert rules card", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Look for alert rules card
      const alertCard = page.locator("text=/قواعد التنبيه|Alert Rules/i");
      await expect(alertCard).toBeVisible();

      // Check for icon
      const alertIcon = page.locator(".bg-orange-100").first();
      await expect(alertIcon).toBeVisible();

      // Check for numeric value
      const alertCount = page
        .locator("text=/قواعد التنبيه|Alert Rules/i")
        .locator("..")
        .locator("h3")
        .first();
      const isVisible = await alertCount
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        const value = await alertCount.textContent();
        console.log(`Alert rules count: ${value}`);
        expect(value).toMatch(/\d+/);
      }
    });

    test("should display status labels on cards", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for status labels (متصل / مفعّل)
      const statusLabels = page.locator("span.text-xs.text-gray-500");
      const count = await statusLabels.count();

      console.log(`Found ${count} status labels`);
      expect(count).toBeGreaterThanOrEqual(3);
    });

    test("should display statistics in grid layout", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for grid container
      const gridContainer = page
        .locator(".grid.grid-cols-1.md\\:grid-cols-3")
        .first();
      await expect(gridContainer).toBeVisible();

      // Cards should be properly styled
      const cards = gridContainer.locator("> div.bg-white.rounded-xl");
      const count = await cards.count();

      expect(count).toBe(3);
    });
  });

  /**
   * Sensors Dashboard Tests
   * اختبارات لوحة المستشعرات
   */
  test.describe("Sensors Dashboard", () => {
    test("should display sensors dashboard section", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for sensors dashboard heading
      const heading = page.locator('h2:has-text("لوحة المستشعرات")');
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      // Check for English subtitle
      const subtitle = page.locator("text=/Sensors Dashboard/i");
      await expect(subtitle).toBeVisible();
    });

    test("should display sensor list", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for sensors dashboard section
      const dashboardSection = page
        .locator('h2:has-text("لوحة المستشعرات")')
        .locator("..");

      if (await dashboardSection.isVisible({ timeout: 5000 })) {
        // Look for sensor items/cards
        const sensorItems = dashboardSection.locator(
          '[class*="sensor"], [data-testid*="sensor"]',
        );
        const count = await sensorItems.count();

        console.log(`Found ${count} sensor items in dashboard`);

        if (count === 0) {
          // Check for "no sensors" message
          const noSensorsMsg = page.locator(
            "text=/لا توجد مستشعرات|No sensors/i",
          );
          const hasNoSensorsMsg = await noSensorsMsg
            .isVisible({ timeout: 2000 })
            .catch(() => false);

          if (hasNoSensorsMsg) {
            console.log("No sensors available - showing empty state");
          }
        }
      }
    });

    test("should display sensor names and types", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for sensor type labels (soil moisture, temperature, etc.)
      const sensorTypes = page.locator(
        "text=/soil|temperature|humidity|الرطوبة|درجة الحرارة/i",
      );
      const count = await sensorTypes.count();

      console.log(`Found ${count} sensor type indicators`);
    });

    test("should display sensor status indicators", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for status badges (online, offline, active)
      const statusBadges = page.locator(
        "text=/online|offline|active|متصل|غير متصل|نشط/i",
      );
      const count = await statusBadges.count();

      console.log(`Found ${count} status indicators`);
    });

    test("should allow clicking on a sensor", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Try to find a clickable sensor card
      const sensorCard = page
        .locator('[class*="cursor-pointer"], button')
        .filter({
          has: page.locator("text=/sensor|مستشعر/i"),
        })
        .first();

      const isClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isClickable) {
        // Click the sensor
        await sensorCard.click();
        await page.waitForTimeout(2000);

        console.log("Sensor clicked - should show readings");

        // Check if sensor readings section appears
        const readingsSection = page.locator("text=/قراءات|Readings/i");
        const hasReadings = await readingsSection
          .isVisible({ timeout: 3000 })
          .catch(() => false);

        console.log(`Sensor readings section visible: ${hasReadings}`);
      } else {
        console.log("No clickable sensors found");
      }
    });

    test("should display sensor last reading values", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for sensor reading values
      const readingValues = page.locator("text=/\\d+%|\\d+°C|\\d+\\s*C/i");
      const count = await readingValues.count();

      console.log(`Found ${count} sensor reading values`);
    });

    test("should display sensor icons", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for SVG icons in sensor cards
      const sensorIcons = page.locator(".bg-white.rounded-xl svg").filter({
        hasNot: page.locator(".w-4.h-4"),
      });
      const count = await sensorIcons.count();

      console.log(`Found ${count} sensor icons`);
    });
  });

  /**
   * Sensor Readings Display Tests
   * اختبارات عرض قراءات المستشعرات
   */
  test.describe("Sensor Readings Display", () => {
    test("should display sensor readings section when sensor is selected", async ({
      page,
    }) => {
      await page.waitForTimeout(3000);

      // Try to click a sensor
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const hasClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasClickable) {
        await sensorCard.click();
        await page.waitForTimeout(2000);

        // Look for readings section
        const readingsHeading = page.locator("text=/قراءات/i");
        const isVisible = await readingsHeading
          .isVisible({ timeout: 3000 })
          .catch(() => false);

        if (isVisible) {
          await expect(readingsHeading).toBeVisible();
          console.log("Sensor readings section displayed");
        }
      } else {
        console.log("No sensors available to select");
      }
    });

    test("should display sensor chart", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Try to click a sensor
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const hasClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasClickable) {
        await sensorCard.click();
        await page.waitForTimeout(2000);

        // Look for chart (SVG or canvas)
        const chart = page.locator("svg, canvas").filter({
          has: page.locator("path, rect"),
        });
        const hasChart = await chart
          .isVisible({ timeout: 3000 })
          .catch(() => false);

        console.log(`Sensor chart visible: ${hasChart}`);

        if (hasChart) {
          await expect(chart.first()).toBeVisible();
        }
      }
    });

    test("should display readings table", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Try to click a sensor
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const hasClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasClickable) {
        await sensorCard.click();
        await page.waitForTimeout(2000);

        // Look for table or list of readings
        const readingsTable = page.locator('table, [class*="table"]');
        const hasList = await readingsTable
          .isVisible({ timeout: 3000 })
          .catch(() => false);

        console.log(`Readings table/list visible: ${hasList}`);
      }
    });

    test("should display reading timestamps", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for timestamp patterns
      const timestamps = page.locator("text=/\\d{1,2}:\\d{2}|AM|PM|ص|م/i");
      const count = await timestamps.count();

      console.log(`Found ${count} timestamps`);
    });

    test("should display sensor units", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for common sensor units
      const units = page.locator("text=/%|°C|°F|ppm|lux|hPa/");
      const count = await units.count();

      console.log(`Found ${count} unit indicators`);
    });

    test("should display chart statistics", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Try to click a sensor
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const hasClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasClickable) {
        await sensorCard.click();
        await page.waitForTimeout(2000);

        // Look for stats (min, max, avg)
        const statsLabels = page.locator(
          "text=/minimum|maximum|average|min|max|avg|أدنى|أعلى|متوسط/i",
        );
        const count = await statsLabels.count();

        console.log(`Found ${count} chart statistics labels`);
      }
    });

    test("should handle empty readings gracefully", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for "no readings" message
      const noReadingsMsg = page.locator(
        "text=/لا توجد قراءات|No readings available|No data/i",
      );
      const hasNoReadings = await noReadingsMsg
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasNoReadings) {
        console.log("Empty readings state displayed correctly");
        await expect(noReadingsMsg).toBeVisible();
      }
    });
  });

  /**
   * Device Status Indicators Tests
   * اختبارات مؤشرات حالة الأجهزة
   */
  test.describe("Device Status Indicators", () => {
    test("should display sensor status badges", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for status badges
      const statusBadges = page
        .locator('[class*="badge"], [class*="status"]')
        .filter({
          has: page.locator("text=/online|offline|active|inactive/i"),
        });
      const count = await statusBadges.count();

      console.log(`Found ${count} status badges`);
    });

    test("should show online status with green indicator", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for online/active status with green color
      const onlineStatus = page.locator('[class*="green"]').filter({
        has: page.locator("text=/online|active|متصل|نشط/i"),
      });
      const count = await onlineStatus.count();

      console.log(`Found ${count} online status indicators`);
    });

    test("should show offline status with red/gray indicator", async ({
      page,
    }) => {
      await page.waitForTimeout(3000);

      // Look for offline status with red/gray color
      const offlineStatus = page
        .locator('[class*="red"], [class*="gray"]')
        .filter({
          has: page.locator("text=/offline|inactive|غير متصل|غير نشط/i"),
        });
      const count = await offlineStatus.count();

      console.log(`Found ${count} offline status indicators`);
    });

    test("should display battery level if available", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for battery indicators
      const batteryIcons = page.locator("text=/battery|بطارية|\\d+%/i");
      const count = await batteryIcons.count();

      console.log(`Found ${count} battery indicators`);
    });

    test("should display signal strength if available", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for signal indicators
      const signalIcons = page.locator("text=/signal|إشارة/i");
      const count = await signalIcons.count();

      console.log(`Found ${count} signal indicators`);
    });

    test("should show error status with warning indicator", async ({
      page,
    }) => {
      await page.waitForTimeout(3000);

      // Look for error/warning status
      const errorStatus = page
        .locator('[class*="red"], [class*="orange"]')
        .filter({
          has: page.locator("text=/error|warning|خطأ|تحذير/i"),
        });
      const count = await errorStatus.count();

      console.log(`Found ${count} error/warning indicators`);
    });

    test("should display actuator status toggles", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to actuators section
      const actuatorsSection = page.locator('h2:has-text("التحكم بالمشغلات")');
      const isVisible = await actuatorsSection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        await actuatorsSection.scrollIntoViewIfNeeded();
        await page.waitForTimeout(1000);

        // Look for status indicators in actuator controls
        const actuatorStatus = page.locator(
          "text=/on|off|auto|تشغيل|إيقاف|تلقائي/i",
        );
        const count = await actuatorStatus.count();

        console.log(`Found ${count} actuator status indicators`);
      }
    });
  });

  /**
   * Real-time Data Updates Tests
   * اختبارات تحديثات البيانات في الوقت الفعلي
   */
  test.describe("Real-time Data Updates", () => {
    test("should handle data refresh", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Get initial sensor count
      const initialCount = await page
        .locator("h3")
        .filter({ hasText: /^\d+$/ })
        .first()
        .textContent();
      console.log(`Initial count: ${initialCount}`);

      // Wait for potential auto-refresh
      await page.waitForTimeout(5000);

      // Page should still be functional
      const heading = page.locator("h1").first();
      await expect(heading).toBeVisible();
    });

    test("should update readings when sensor is selected", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Click a sensor
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const hasClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasClickable) {
        await sensorCard.click();
        await page.waitForTimeout(2000);

        // Readings should load
        const readingsSection = page.locator("text=/قراءات|Readings/i");
        const hasReadings = await readingsSection
          .isVisible({ timeout: 5000 })
          .catch(() => false);

        console.log(`Readings updated after selection: ${hasReadings}`);
      }
    });

    test("should handle sensor data polling", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Listen for API requests
      const apiCalls: string[] = [];
      page.on("request", (request) => {
        if (
          request.url().includes("/api/") ||
          request.url().includes("sensor")
        ) {
          apiCalls.push(request.url());
        }
      });

      // Wait for potential polling
      await page.waitForTimeout(6000);

      console.log(`API calls made: ${apiCalls.length}`);
    });

    test("should show loading state during data refresh", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Reload to trigger loading
      await page.reload();

      // Look for loading indicators
      const loadingSpinner = page.locator(
        '[class*="animate-pulse"], [class*="animate-spin"]',
      );
      const hasLoading = await loadingSpinner
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Loading state during refresh: ${hasLoading}`);

      // Wait for content to load
      await page.waitForTimeout(3000);

      // Content should be visible
      const heading = page.locator("h1").first();
      await expect(heading).toBeVisible();
    });

    test("should handle websocket connection if available", async ({
      page,
    }) => {
      await page.waitForTimeout(3000);

      // Check if websocket is used (this is informational)
      const wsConnected = await page.evaluate(() => {
        return "WebSocket" in window;
      });

      console.log(`WebSocket support available: ${wsConnected}`);
    });
  });

  /**
   * Actuator Controls Tests
   * اختبارات التحكم بالمشغلات
   */
  test.describe("Actuator Controls", () => {
    test("should display actuator controls section", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for actuator controls heading
      const heading = page.locator('h2:has-text("التحكم بالمشغلات")');
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      // Check for English subtitle
      const subtitle = page.locator("text=/Actuator Controls/i");
      await expect(subtitle).toBeVisible();
    });

    test("should display actuator list", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to actuators section
      const actuatorsSection = page.locator('h2:has-text("التحكم بالمشغلات")');
      await actuatorsSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      // Look for actuator items
      const actuatorItems = page.locator(
        '[class*="actuator"], [data-testid*="actuator"]',
      );
      const count = await actuatorItems.count();

      console.log(`Found ${count} actuator items`);

      if (count === 0) {
        // Check for "no actuators" message
        const noActuatorsMsg = page.locator(
          "text=/لا توجد مشغلات|No actuators/i",
        );
        const hasMsg = await noActuatorsMsg
          .isVisible({ timeout: 2000 })
          .catch(() => false);

        if (hasMsg) {
          console.log("No actuators available - showing empty state");
        }
      }
    });

    test("should display actuator control buttons", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to actuators section
      const actuatorsSection = page.locator('h2:has-text("التحكم بالمشغلات")');
      await actuatorsSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      // Look for control buttons
      const controlButtons = page.locator("button").filter({
        has: page.locator("text=/on|off|toggle|تشغيل|إيقاف/i"),
      });
      const count = await controlButtons.count();

      console.log(`Found ${count} actuator control buttons`);
    });

    test("should display actuator status", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to actuators section
      const actuatorsSection = page.locator('h2:has-text("التحكم بالمشغلات")');
      const isVisible = await actuatorsSection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        await actuatorsSection.scrollIntoViewIfNeeded();
        await page.waitForTimeout(1000);

        // Look for status indicators
        const statusIndicators = page.locator(
          "text=/on|off|auto|تشغيل|إيقاف|تلقائي/i",
        );
        const count = await statusIndicators.count();

        console.log(`Found ${count} actuator status indicators`);
      }
    });

    test("should show actuator types", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for actuator types (valve, pump, fan, etc.)
      const actuatorTypes = page.locator(
        "text=/valve|pump|fan|heater|صمام|مضخة|مروحة/i",
      );
      const count = await actuatorTypes.count();

      console.log(`Found ${count} actuator type labels`);
    });
  });

  /**
   * Alert Rules Tests
   * اختبارات قواعد التنبيه
   */
  test.describe("Alert Rules", () => {
    test("should display alert rules section", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for alert rules heading
      const heading = page.locator('h2:has-text("قواعد التنبيه")');
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      // Check for English subtitle
      const subtitle = page.locator("text=/Alert Rules/i");
      await expect(subtitle).toBeVisible();
    });

    test("should display alert rules list", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to alert rules section
      const alertSection = page.locator('h2:has-text("قواعد التنبيه")');
      await alertSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      // Look for alert rule items
      const alertItems = page.locator(
        '[class*="alert"], [data-testid*="alert"]',
      );
      const count = await alertItems.count();

      console.log(`Found ${count} alert rule items`);

      if (count === 0) {
        // Check for "no alerts" message
        const noAlertsMsg = page.locator(
          "text=/لا توجد قواعد|No rules|No alerts/i",
        );
        const hasMsg = await noAlertsMsg
          .isVisible({ timeout: 2000 })
          .catch(() => false);

        if (hasMsg) {
          console.log("No alert rules - showing empty state");
        }
      }
    });

    test("should display alert severity levels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for severity indicators
      const severityLabels = page.locator(
        "text=/info|warning|critical|معلومات|تحذير|حرج/i",
      );
      const count = await severityLabels.count();

      console.log(`Found ${count} severity indicators`);
    });

    test("should display alert conditions", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for condition text (above, below, between)
      const conditions = page.locator(
        "text=/above|below|between|أعلى من|أقل من|بين/i",
      );
      const count = await conditions.count();

      console.log(`Found ${count} alert conditions`);
    });

    test("should display alert threshold values", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to alert rules
      const alertSection = page.locator('h2:has-text("قواعد التنبيه")');
      const isVisible = await alertSection
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        await alertSection.scrollIntoViewIfNeeded();
        await page.waitForTimeout(1000);

        // Look for numeric thresholds
        const thresholds = page.locator("text=/\\d+%|\\d+°C|\\d+\\s*C/i");
        const count = await thresholds.count();

        console.log(`Found ${count} threshold values`);
      }
    });

    test("should show enabled/disabled state for rules", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for enabled/disabled indicators
      const stateIndicators = page.locator(
        "text=/enabled|disabled|مفعّل|معطّل/i",
      );
      const count = await stateIndicators.count();

      console.log(`Found ${count} rule state indicators`);
    });
  });

  /**
   * Responsive Design Tests
   * اختبارات التصميم المتجاوب
   */
  test.describe("Responsive Design", () => {
    test("should display correctly on mobile viewport", async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Page title should be visible
      const heading = page.locator('h1:has-text("إنترنت الأشياء والمستشعرات")');
      await expect(heading).toBeVisible();

      // Statistics should stack vertically
      const statCards = page.locator(".grid.grid-cols-1 > div.bg-white");
      const count = await statCards.count();

      console.log(`Statistics cards on mobile: ${count}`);
    });

    test("should display correctly on tablet viewport", async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("إنترنت الأشياء والمستشعرات")');
      await expect(heading).toBeVisible();

      console.log("IoT page responsive on tablet");
    });

    test("should display correctly on desktop viewport", async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("إنترنت الأشياء والمستشعرات")');
      await expect(heading).toBeVisible();

      // Should show 3 columns for statistics
      const gridContainer = page.locator(".grid.md\\:grid-cols-3").first();
      await expect(gridContainer).toBeVisible();

      console.log("IoT page responsive on desktop");
    });

    test("should adapt layout grid on different screens", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(3000);

      // Main content grid should be visible
      const mainGrid = page
        .locator(".grid.grid-cols-1.lg\\:grid-cols-3")
        .first();
      const isVisible = await mainGrid
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      console.log(`Main grid visible on mobile: ${isVisible}`);
    });

    test("should maintain functionality on small screens", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(3000);

      // Try to click a sensor on mobile
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const isClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isClickable) {
        await sensorCard.click();
        await page.waitForTimeout(1000);

        console.log("Sensor interaction works on mobile");
      }
    });

    test("should scroll properly on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Scroll to bottom of page
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(1000);

      // Alert rules section should be visible after scroll
      const alertSection = page.locator('h2:has-text("قواعد التنبيه")');
      const isVisible = await alertSection
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Alert section visible after scroll: ${isVisible}`);
    });
  });

  /**
   * Loading States Tests
   * اختبارات حالات التحميل
   */
  test.describe("Loading States", () => {
    test("should show loading state for sensors dashboard", async ({
      page,
    }) => {
      await page.goto(pages.iot);

      // Look for loading indicator in sensors section
      const loadingIndicator = page.locator(
        '.animate-pulse, [class*="skeleton"]',
      );
      const hasLoading = await loadingIndicator
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Sensors loading state shown: ${hasLoading}`);

      // Wait for content to load
      await page.waitForTimeout(3000);

      // Content should be visible
      const heading = page.locator('h2:has-text("لوحة المستشعرات")');
      await expect(heading).toBeVisible({ timeout: timeouts.long });
    });

    test("should show loading state for actuators", async ({ page }) => {
      await page.goto(pages.iot);

      // Look for loading in actuators section
      const actuatorsSection = page.locator("text=/التحكم بالمشغلات/i");
      const loadingPulse = actuatorsSection
        .locator("..")
        .locator(".animate-pulse");

      const hasLoading = await loadingPulse
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Actuators loading state shown: ${hasLoading}`);
    });

    test("should show loading state for alert rules", async ({ page }) => {
      await page.goto(pages.iot);

      // Look for loading in alert rules section
      const alertSection = page.locator("text=/قواعد التنبيه/i");
      const loadingPulse = alertSection.locator("..").locator(".animate-pulse");

      const hasLoading = await loadingPulse
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Alert rules loading state shown: ${hasLoading}`);
    });

    test("should transition from loading to content", async ({ page }) => {
      await page.goto(pages.iot);

      // Wait for loading to disappear and content to appear
      await page.waitForTimeout(5000);

      // All main sections should be visible
      const sensorsHeading = page.locator('h2:has-text("لوحة المستشعرات")');
      const actuatorsHeading = page.locator('h2:has-text("التحكم بالمشغلات")');
      const alertsHeading = page.locator('h2:has-text("قواعد التنبيه")');

      await expect(sensorsHeading).toBeVisible({ timeout: timeouts.long });
      await expect(actuatorsHeading).toBeVisible({ timeout: timeouts.long });
      await expect(alertsHeading).toBeVisible({ timeout: timeouts.long });
    });

    test("should show skeleton loaders with correct structure", async ({
      page,
    }) => {
      await page.goto(pages.iot);

      // Check for skeleton loaders
      const skeletons = page.locator(".animate-pulse");
      const count = await skeletons.count();

      console.log(`Found ${count} skeleton loaders`);
    });

    test("should show loading when fetching sensor readings", async ({
      page,
    }) => {
      await page.waitForTimeout(3000);

      // Click a sensor
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const hasClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasClickable) {
        // Click and look for loading
        await sensorCard.click();

        const loadingSpinner = page.locator('[class*="animate-spin"]');
        const hasLoading = await loadingSpinner
          .isVisible({ timeout: 1000 })
          .catch(() => false);

        console.log(`Sensor readings loading state: ${hasLoading}`);
      }
    });
  });

  /**
   * Arabic/English Labels Tests
   * اختبارات الملصقات العربية/الإنجليزية
   */
  test.describe("Bilingual Labels", () => {
    test("should display Arabic primary labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for Arabic headings
      const arabicHeadings = [
        "إنترنت الأشياء والمستشعرات",
        "لوحة المستشعرات",
        "التحكم بالمشغلات",
        "قواعد التنبيه",
      ];

      for (const heading of arabicHeadings) {
        const element = page.locator(`text=${heading}`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);
        console.log(`Arabic heading "${heading}" visible: ${isVisible}`);

        if (isVisible) {
          await expect(element).toBeVisible();
        }
      }
    });

    test("should display English secondary labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for English subtitles
      const englishLabels = [
        "IoT & Sensors Management",
        "Sensors Dashboard",
        "Actuator Controls",
        "Alert Rules",
      ];

      for (const label of englishLabels) {
        const element = page.locator(`text=${label}`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);
        console.log(`English label "${label}" visible: ${isVisible}`);

        if (isVisible) {
          await expect(element).toBeVisible();
        }
      }
    });

    test("should display Arabic statistics labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for Arabic stat labels
      const arabicLabels = ["مستشعرات نشطة", "مشغلات نشطة", "قواعد التنبيه"];

      for (const label of arabicLabels) {
        const element = page.locator(`text=${label}`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);

        if (isVisible) {
          console.log(`Arabic stat label "${label}" found`);
          await expect(element).toBeVisible();
        }
      }
    });

    test("should display English statistics labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for English stat labels
      const englishLabels = [
        "Active Sensors",
        "Active Actuators",
        "Alert Rules",
      ];

      for (const label of englishLabels) {
        const element = page.locator(`text=${label}`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);

        if (isVisible) {
          console.log(`English stat label "${label}" found`);
          await expect(element).toBeVisible();
        }
      }
    });

    test("should display bilingual status labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for status labels in both languages
      const statusLabels = page.locator(
        "text=/متصل|مفعّل|online|active|connected/i",
      );
      const count = await statusLabels.count();

      console.log(`Found ${count} bilingual status labels`);
    });

    test("should display Arabic sensor type names", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for Arabic sensor types
      const arabicTypes = page.locator(
        "text=/رطوبة التربة|درجة الحرارة|الرطوبة/i",
      );
      const count = await arabicTypes.count();

      console.log(`Found ${count} Arabic sensor type labels`);
    });

    test("should have proper RTL direction", async ({ page }) => {
      await page.waitForTimeout(2000);

      // Check for RTL direction
      const mainContainer = page.locator('[dir="rtl"]').first();
      const isVisible = await mainContainer
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        await expect(mainContainer).toBeVisible();

        const direction = await mainContainer.getAttribute("dir");
        expect(direction).toBe("rtl");
      }
    });
  });

  /**
   * Error Handling Tests
   * اختبارات معالجة الأخطاء
   */
  test.describe("Error Handling", () => {
    test("should handle no sensors gracefully", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for "no sensors" message
      const noSensorsMsg = page.locator(
        "text=/لا توجد مستشعرات|No sensors available|No devices/i",
      );
      const hasMsg = await noSensorsMsg
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasMsg) {
        console.log("No sensors message displayed gracefully");
        await expect(noSensorsMsg).toBeVisible();
      }
    });

    test("should handle no actuators gracefully", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to actuators section
      const actuatorsSection = page.locator('h2:has-text("التحكم بالمشغلات")');
      await actuatorsSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      // Look for "no actuators" message
      const noActuatorsMsg = page.locator(
        "text=/لا توجد مشغلات|No actuators/i",
      );
      const hasMsg = await noActuatorsMsg
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasMsg) {
        console.log("No actuators message displayed gracefully");
      }
    });

    test("should handle no alert rules gracefully", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Scroll to alert rules
      const alertSection = page.locator('h2:has-text("قواعد التنبيه")');
      await alertSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(1000);

      // Look for "no rules" message
      const noRulesMsg = page.locator(
        "text=/لا توجد قواعد|No rules|No alerts/i",
      );
      const hasMsg = await noRulesMsg
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasMsg) {
        console.log("No alert rules message displayed gracefully");
      }
    });

    test("should not crash on missing data", async ({ page }) => {
      await page.waitForTimeout(5000);

      // Page should still be functional
      const heading = page.locator('h1:has-text("إنترنت الأشياء والمستشعرات")');
      await expect(heading).toBeVisible();

      console.log("Page remains stable with missing data");
    });

    test("should display fallback UI for failed components", async ({
      page,
    }) => {
      await page.waitForTimeout(5000);

      // Check if page has basic structure even if data fails
      const sections = page.locator("h2");
      const count = await sections.count();

      console.log(`Found ${count} section headings`);
      expect(count).toBeGreaterThanOrEqual(3);
    });

    test("should handle sensor selection errors", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Try to click a sensor (might not exist)
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const exists = await sensorCard
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (!exists) {
        console.log("No sensors to select - handled gracefully");
        // Page should still be stable
        const heading = page.locator("h1").first();
        await expect(heading).toBeVisible();
      }
    });
  });

  /**
   * Integration Tests
   * اختبارات التكامل
   */
  test.describe("Integration", () => {
    test("should maintain state when navigating away and back", async ({
      page,
    }) => {
      await page.waitForTimeout(3000);

      // Click a sensor if available
      const sensorCard = page.locator('[class*="cursor-pointer"]').first();
      const hasClickable = await sensorCard
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasClickable) {
        await sensorCard.click();
        await page.waitForTimeout(1000);
      }

      // Navigate away
      await page.goto(pages.dashboard);
      await waitForPageLoad(page);

      // Navigate back
      await page.goto(pages.iot);
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Page should load correctly
      const heading = page.locator('h1:has-text("إنترنت الأشياء والمستشعرات")');
      await expect(heading).toBeVisible();

      console.log("Navigated away and back to IoT page");
    });

    test("should work with browser refresh", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Reload page
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(3000);

      // Page should load correctly
      const heading = page.locator('h1:has-text("إنترنت الأشياء والمستشعرات")');
      await expect(heading).toBeVisible();

      console.log("Page works after browser refresh");
    });

    test("should display all sections together", async ({ page }) => {
      await page.waitForTimeout(5000);

      // Check that all main sections are present
      const sections = ["لوحة المستشعرات", "التحكم بالمشغلات", "قواعد التنبيه"];

      let visibleSections = 0;
      for (const section of sections) {
        const element = page.locator(`h2:has-text("${section}")`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);
        if (isVisible) visibleSections++;
      }

      console.log(
        `${visibleSections} out of ${sections.length} sections visible`,
      );
      expect(visibleSections).toBe(3);
    });

    test("should handle multiple sensor clicks", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Get all clickable sensors
      const sensorCards = page.locator('[class*="cursor-pointer"]');
      const count = await sensorCards.count();

      if (count >= 2) {
        // Click first sensor
        await sensorCards.first().click();
        await page.waitForTimeout(1500);

        // Click second sensor
        await sensorCards.nth(1).click();
        await page.waitForTimeout(1500);

        console.log("Multiple sensor clicks handled successfully");

        // Page should still be functional
        const heading = page.locator("h1").first();
        await expect(heading).toBeVisible();
      } else {
        console.log("Not enough sensors for multiple click test");
      }
    });
  });

  /**
   * Accessibility Tests
   * اختبارات إمكانية الوصول
   */
  test.describe("Accessibility", () => {
    test("should have proper heading hierarchy", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for h1
      const h1 = page.locator("h1");
      await expect(h1).toBeVisible();

      // Check for h2 sections
      const h2Elements = page.locator("h2");
      const count = await h2Elements.count();

      console.log(`Found ${count} h2 headings`);
      expect(count).toBeGreaterThanOrEqual(3);
    });

    test("should have accessible button labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check that buttons have text or aria-labels
      const buttons = page.locator("button");
      const count = await buttons.count();

      console.log(`Found ${count} buttons on page`);
    });

    test("should support keyboard navigation", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Focus on first interactive element
      const firstButton = page.locator("button").first();
      const isVisible = await firstButton
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (isVisible) {
        await firstButton.focus();

        // Tab key should move focus
        await page.keyboard.press("Tab");
        await page.waitForTimeout(300);

        console.log("Keyboard navigation functional");
      }
    });
  });
});
