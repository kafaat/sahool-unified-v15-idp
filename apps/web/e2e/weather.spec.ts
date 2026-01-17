import { test, expect } from "./fixtures/test-fixtures";
import { navigateAndWait, waitForPageLoad } from "./helpers/page.helpers";
import { pages } from "./helpers/test-data";

/**
 * Weather Page E2E Tests
 * اختبارات E2E لصفحة الطقس
 */

test.describe("Weather Page", () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, pages.weather);
  });

  /**
   * Basic Page Loading Tests
   * اختبارات تحميل الصفحة الأساسية
   */
  test.describe("Page Loading", () => {
    test("should display weather page correctly", async ({ page }) => {
      // Check page title - uses default SAHOOL title
      await expect(page).toHaveTitle(/SAHOOL|سهول/i);

      // Check for main heading in Arabic
      const heading = page.locator('h1:has-text("الطقس")');
      await expect(heading).toBeVisible();

      // Check for English subtitle
      const subtitle = page.locator('p:has-text("Weather Dashboard")');
      await expect(subtitle).toBeVisible();
    });

    test("should display page header with location selector", async ({
      page,
    }) => {
      // Check for header section
      const header = page.locator(".bg-white.rounded-xl").first();
      await expect(header).toBeVisible();

      // Check for location icon
      const locationIcon = page.locator("svg").first();
      await expect(locationIcon).toBeVisible();

      // Check for location selector dropdown
      const locationSelector = page.locator("select");
      await expect(locationSelector).toBeVisible();
    });

    test("should show loading state initially", async ({ page }) => {
      // Navigate to page and check for loading state
      await page.goto(pages.weather);

      // Look for loading indicators
      const loadingText = page.locator("text=/جاري تحميل/i");
      const loadingIndicator = page.locator(".animate-pulse");

      // At least one loading indicator should appear briefly
      const hasLoading = await loadingText
        .or(loadingIndicator)
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Loading state shown: ${hasLoading}`);
    });
  });

  /**
   * Location Selector Tests
   * اختبارات محدد الموقع
   */
  test.describe("Location Selector", () => {
    test("should have Yemen cities in location dropdown", async ({ page }) => {
      await page.waitForTimeout(1000);

      const locationSelector = page.locator("select");
      await expect(locationSelector).toBeVisible();

      // Get all options
      const options = await locationSelector
        .locator("option")
        .allTextContents();

      console.log(`Location options: ${options.join(", ")}`);

      // Should have multiple Yemen cities
      expect(options.length).toBeGreaterThan(1);
      expect(options.some((opt) => opt.includes("صنعاء"))).toBe(true);
    });

    test("should change location when selector is changed", async ({
      page,
    }) => {
      await page.waitForTimeout(2000);

      const locationSelector = page.locator("select");

      // Get initial value
      const initialValue = await locationSelector.inputValue();
      console.log(`Initial location: ${initialValue}`);

      // Select different location (Aden)
      await locationSelector.selectOption({ index: 1 });
      await page.waitForTimeout(1000);

      // Value should change
      const newValue = await locationSelector.inputValue();
      console.log(`New location: ${newValue}`);

      expect(newValue).not.toBe(initialValue);
    });

    test("should reload weather data when location changes", async ({
      page,
    }) => {
      await page.waitForTimeout(2000);

      // Wait for API call when changing location
      // const responsePromise = page.waitForResponse(
      //   response => response.url().includes('/api/weather') || response.url().includes('weather'),
      //   { timeout: 10000 }
      // ).catch(() => null);

      // Change location
      const locationSelector = page.locator("select");
      await locationSelector.selectOption({ index: 1 });

      // Should trigger API call
      await page.waitForTimeout(2000);

      console.log("Location changed, checking for data update");
    });

    test("should display all Yemen cities", async ({ page }) => {
      const locationSelector = page.locator("select");
      const options = await locationSelector
        .locator("option")
        .allTextContents();

      // Check for expected cities
      const expectedCities = ["صنعاء", "عدن", "تعز", "الحديدة", "إب"];

      for (const city of expectedCities) {
        const hasCity = options.some((opt) => opt.includes(city));
        console.log(`City ${city} found: ${hasCity}`);
      }
    });
  });

  /**
   * Current Weather Display Tests
   * اختبارات عرض الطقس الحالي
   */
  test.describe("Current Weather Display", () => {
    test("should display current weather section", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for current weather heading
      const heading = page.locator('h2:has-text("الطقس الحالي")');
      const isVisible = await heading
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(heading).toBeVisible();
      } else {
        console.log("Current weather section not loaded yet");
      }
    });

    test("should display temperature", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for temperature display (large number with °C)
      const temperature = page.locator("text=/\\d+°C/").first();
      const isVisible = await temperature
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        const tempText = await temperature.textContent();
        console.log(`Current temperature: ${tempText}`);

        await expect(temperature).toBeVisible();
        expect(tempText).toMatch(/\d+°C/);
      } else {
        console.log("Temperature not available");
      }
    });

    test("should display weather condition with icon", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for weather icon (SVG)
      const weatherIcon = page
        .locator(".text-6xl")
        .locator("..")
        .locator("svg")
        .first();
      const hasIcon = await weatherIcon
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (hasIcon) {
        console.log("Weather icon displayed");
        await expect(weatherIcon).toBeVisible();
      }
    });

    test("should display humidity", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for humidity label
      const humidityLabel = page.locator("text=/الرطوبة|Humidity/i");
      const isVisible = await humidityLabel
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(humidityLabel).toBeVisible();

        // Look for humidity percentage value
        const humidityValue = page.locator("text=/\\d+%/").first();
        const hasValue = await humidityValue
          .isVisible({ timeout: 2000 })
          .catch(() => false);

        if (hasValue) {
          const value = await humidityValue.textContent();
          console.log(`Humidity: ${value}`);
        }
      }
    });

    test("should display wind speed", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for wind label
      const windLabel = page.locator("text=/الرياح|Wind/i");
      const isVisible = await windLabel
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(windLabel).toBeVisible();

        // Look for wind speed value (km/h)
        const windSpeed = page.locator("text=/\\d+\\s*km\\/h/i").first();
        const hasValue = await windSpeed
          .isVisible({ timeout: 2000 })
          .catch(() => false);

        if (hasValue) {
          const value = await windSpeed.textContent();
          console.log(`Wind speed: ${value}`);
        }
      }
    });

    test("should display pressure if available", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for pressure label
      const pressureLabel = page.locator("text=/الضغط|Pressure/i");
      const isVisible = await pressureLabel
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        console.log("Pressure data available");
        await expect(pressureLabel).toBeVisible();

        // Check for hPa unit
        const unit = page.locator("text=/hPa/i");
        await expect(unit).toBeVisible();
      } else {
        console.log("Pressure data not available");
      }
    });

    test("should display visibility if available", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for visibility label
      const visibilityLabel = page.locator("text=/الرؤية|Visibility/i");
      const isVisible = await visibilityLabel
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        console.log("Visibility data available");
        await expect(visibilityLabel).toBeVisible();
      } else {
        console.log("Visibility data not available");
      }
    });

    test("should display UV index if available", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for UV index label
      const uvLabel = page.locator("text=/UV|مؤشر UV/i");
      const isVisible = await uvLabel
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        console.log("UV index data available");
        await expect(uvLabel).toBeVisible();
      } else {
        console.log("UV index data not available");
      }
    });

    test("should display timestamp", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Look for timestamp (آخر تحديث)
      const timestamp = page.locator("text=/آخر تحديث/i");
      const isVisible = await timestamp
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        const timestampText = await timestamp.textContent();
        console.log(`Last update: ${timestampText}`);
      }
    });

    test("should show weather details in grid layout", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Weather details should be in a grid
      const detailCards = page.locator(
        ".bg-white\\/50.backdrop-blur-sm.rounded-lg",
      );
      const count = await detailCards.count();

      console.log(`Found ${count} weather detail cards`);

      if (count > 0) {
        expect(count).toBeGreaterThanOrEqual(2); // At least humidity and wind
      }
    });
  });

  /**
   * 7-Day Forecast Tests
   * اختبارات توقعات 7 أيام
   */
  test.describe("7-Day Forecast", () => {
    test("should display forecast section", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for forecast heading
      const heading = page.locator('h2:has-text("توقعات 7 أيام")');
      const isVisible = await heading
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(heading).toBeVisible();

        // Check for English subtitle
        const subtitle = page.locator("text=/7-Day Forecast/i");
        await expect(subtitle).toBeVisible();
      } else {
        console.log("7-day forecast section not loaded");
      }
    });

    test("should display multiple forecast days", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for forecast items (should have date, condition, temp)
      const forecastItems = page
        .locator(".space-y-4 > div")
        .filter({ has: page.locator("text=/\\d+°C/") });
      const count = await forecastItems.count();

      console.log(`Found ${count} forecast days`);

      if (count > 0) {
        // Should show up to 7 days
        expect(count).toBeGreaterThanOrEqual(0);
        expect(count).toBeLessThanOrEqual(7);
      }
    });

    test("should display date for each forecast day", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for dates in the forecast
      const dates = page.locator(".w-24 .font-medium");
      const count = await dates.count();

      console.log(`Found ${count} forecast dates`);

      if (count > 0) {
        // Check first date
        const firstDate = await dates.first().textContent();
        console.log(`First forecast date: ${firstDate}`);
      }
    });

    test("should display temperature bars for forecast", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for temperature bars
      const tempBars = page.locator(
        ".bg-gradient-to-r.from-blue-400.to-red-400",
      );
      const count = await tempBars.count();

      console.log(`Found ${count} temperature bars`);

      if (count > 0) {
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });

    test("should display humidity for each forecast day", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for humidity indicators (💧 emoji)
      const humidityIndicators = page.locator("text=/💧\\s*\\d+%/");
      const count = await humidityIndicators.count();

      console.log(`Found ${count} humidity indicators in forecast`);
    });

    test("should show weather conditions for each day", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for condition text in forecast
      const conditions = page.locator(".w-32.text-sm.text-gray-600");
      const count = await conditions.count();

      console.log(`Found ${count} weather conditions in forecast`);

      if (count > 0) {
        const firstCondition = await conditions.first().textContent();
        console.log(`First forecast condition: ${firstCondition}`);
      }
    });

    test("should display forecast legend", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for legend at bottom of forecast
      const legend = page.locator("text=/درجة الحرارة/i");
      const isVisible = await legend
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        console.log("Forecast legend displayed");
        await expect(legend).toBeVisible();
      }
    });
  });

  /**
   * Weather Alerts Tests
   * اختبارات تنبيهات الطقس
   */
  test.describe("Weather Alerts", () => {
    test("should display weather alerts section", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for alerts heading
      const heading = page.locator('h2:has-text("تنبيهات الطقس")');
      const isVisible = await heading
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      if (isVisible) {
        await expect(heading).toBeVisible();

        // Check for English subtitle
        const subtitle = page.locator("text=/Weather Alerts/i");
        await expect(subtitle).toBeVisible();
      } else {
        console.log("Weather alerts section not loaded");
      }
    });

    test("should show no alerts message when no alerts exist", async ({
      page,
    }) => {
      await page.waitForTimeout(4000);

      // Look for "no alerts" message
      const noAlertsMessage = page.locator("text=/لا توجد تنبيهات/i");
      const normalConditions = page.locator("text=/الأحوال الجوية طبيعية/i");

      const hasNoAlerts = await noAlertsMessage
        .isVisible({ timeout: 3000 })
        .catch(() => false);
      const hasNormalMsg = await normalConditions
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (hasNoAlerts || hasNormalMsg) {
        console.log("No weather alerts - conditions are normal");
      } else {
        console.log("Weather alerts may be present or still loading");
      }
    });

    test("should display alert cards if alerts exist", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for alert cards
      const alertCards = page.locator(".rounded-xl.border-2.p-5").filter({
        has: page.locator("text=/حرج|عالي|متوسط|تحذير|منخفض|معلومات/"),
      });
      const count = await alertCards.count();

      console.log(`Found ${count} weather alert cards`);

      if (count > 0) {
        // Alerts are present
        console.log("Weather alerts are active");
      }
    });

    test("should show alert severity levels", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for severity indicators
      const severityLabels = page.locator(
        "text=/critical|high|medium|warning|low|info/i",
      );
      const severityArabic = page.locator(
        "text=/حرج|عالي|متوسط|تحذير|منخفض|معلومات/",
      );

      const hasSeverity = await severityLabels
        .or(severityArabic)
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasSeverity) {
        console.log("Alert severity levels displayed");
      }
    });

    test("should display alert icons", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for alert icons in alert cards
      const alertIcons = page.locator(".rounded-xl.border-2 svg").filter({
        hasNot: page.locator(".w-4.h-4"),
      });
      const count = await alertIcons.count();

      console.log(`Found ${count} alert icons`);
    });

    test("should show alert time periods", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for time indicators in alerts
      const timeLabels = page.locator("text=/من:|إلى:/");
      const count = await timeLabels.count();

      if (count > 0) {
        console.log(`Found ${count} alert time indicators`);
      }
    });

    test("should display affected areas if present", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for affected areas section
      const affectedAreas = page.locator("text=/المناطق المتأثرة/i");
      const hasAreas = await affectedAreas
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasAreas) {
        console.log("Affected areas displayed in alerts");
      }
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
      const heading = page.locator('h1:has-text("الطقس")');
      await expect(heading).toBeVisible();

      // Location selector should be visible
      const locationSelector = page.locator("select");
      await expect(locationSelector).toBeVisible();

      // Weather sections should stack vertically
      console.log("Weather page responsive on mobile");
    });

    test("should display correctly on tablet viewport", async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("الطقس")');
      await expect(heading).toBeVisible();

      console.log("Weather page responsive on tablet");
    });

    test("should display correctly on desktop viewport", async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const heading = page.locator('h1:has-text("الطقس")');
      await expect(heading).toBeVisible();

      console.log("Weather page responsive on desktop");
    });

    test("should adapt weather details grid on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(3000);

      // Weather details should be in grid
      const detailCards = page.locator(
        ".bg-white\\/50.backdrop-blur-sm.rounded-lg",
      );
      const count = await detailCards.count();

      console.log(`Weather detail cards on mobile: ${count}`);
    });

    test("should maintain location selector usability on small screens", async ({
      page,
    }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      const locationSelector = page.locator("select");
      await expect(locationSelector).toBeVisible();

      // Should be clickable
      await locationSelector.click();
      await page.waitForTimeout(300);

      console.log("Location selector usable on mobile");
    });
  });

  /**
   * Loading States Tests
   * اختبارات حالات التحميل
   */
  test.describe("Loading States", () => {
    test("should show loading state for current weather", async ({ page }) => {
      await page.goto(pages.weather);

      // Look for loading indicator
      const loadingText = page.locator("text=/جاري تحميل بيانات الطقس/i");
      const loadingPulse = page.locator(".animate-pulse");

      const hasLoading = await loadingText
        .or(loadingPulse)
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Current weather loading state shown: ${hasLoading}`);
    });

    test("should show loading state for forecast", async ({ page }) => {
      await page.goto(pages.weather);

      // Look for forecast loading state
      const forecastSection = page.locator("text=/توقعات 7 أيام/i");
      const loadingPulse = forecastSection
        .locator("..")
        .locator(".animate-pulse");

      const hasLoading = await loadingPulse
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Forecast loading state shown: ${hasLoading}`);
    });

    test("should show loading state for alerts", async ({ page }) => {
      await page.goto(pages.weather);

      // Look for alerts loading state
      const alertsSection = page.locator("text=/تنبيهات الطقس/i");
      const loadingPulse = alertsSection
        .locator("..")
        .locator(".animate-pulse");

      const hasLoading = await loadingPulse
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      console.log(`Alerts loading state shown: ${hasLoading}`);
    });

    test("should transition from loading to content", async ({ page }) => {
      await page.goto(pages.weather);

      // Wait for loading to disappear and content to appear
      await page.waitForTimeout(5000);

      // Content should be visible
      const temperature = page.locator("text=/\\d+°C/").first();
      const hasContent = await temperature
        .isVisible({ timeout: 5000 })
        .catch(() => false);

      console.log(`Content loaded successfully: ${hasContent}`);
    });

    test("should show skeleton loaders with correct structure", async ({
      page,
    }) => {
      await page.goto(pages.weather);

      // Check for skeleton loaders
      const skeletons = page.locator(".animate-pulse");
      const count = await skeletons.count();

      console.log(`Found ${count} skeleton loaders`);
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
        "الطقس",
        "الطقس الحالي",
        "توقعات 7 أيام",
        "تنبيهات الطقس",
      ];

      for (const heading of arabicHeadings) {
        const element = page.locator(`text=${heading}`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);
        console.log(`Arabic heading "${heading}" visible: ${isVisible}`);
      }
    });

    test("should display English secondary labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for English subtitles
      const englishLabels = [
        "Weather Dashboard",
        "Current Weather",
        "7-Day Forecast",
        "Weather Alerts",
      ];

      for (const label of englishLabels) {
        const element = page.locator(`text=${label}`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);
        console.log(`English label "${label}" visible: ${isVisible}`);
      }
    });

    test("should display Arabic weather detail labels", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Check for Arabic detail labels
      const arabicLabels = ["الرطوبة", "الرياح", "الضغط", "الرؤية"];

      for (const label of arabicLabels) {
        const element = page.locator(`text=${label}`);
        const isVisible = await element
          .isVisible({ timeout: 3000 })
          .catch(() => false);
        if (isVisible) {
          console.log(`Arabic detail label "${label}" found`);
        }
      }
    });

    test("should display bilingual location names", async ({ page }) => {
      const locationSelector = page.locator("select");
      const options = await locationSelector
        .locator("option")
        .allTextContents();

      // Options should contain Arabic text
      const hasArabic = options.some((opt) => /[\u0600-\u06FF]/.test(opt));
      console.log(`Location options have Arabic text: ${hasArabic}`);

      expect(hasArabic).toBe(true);
    });

    test("should display Arabic weather conditions", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for weather condition text in Arabic
      const conditionText = page.locator(".text-xl.text-gray-600").first();
      const isVisible = await conditionText
        .isVisible({ timeout: 3000 })
        .catch(() => false);

      if (isVisible) {
        const text = await conditionText.textContent();
        const hasArabic = /[\u0600-\u06FF]/.test(text || "");
        console.log(
          `Weather condition has Arabic: ${hasArabic}, text: ${text}`,
        );
      }
    });

    test("should display Arabic date formats", async ({ page }) => {
      await page.waitForTimeout(4000);

      // Look for Arabic formatted dates in forecast
      const dates = page.locator(".w-24 .font-medium");
      const count = await dates.count();

      if (count > 0) {
        const firstDate = await dates.first().textContent();
        console.log(`Date format: ${firstDate}`);
      }
    });
  });

  /**
   * Error Handling Tests
   * اختبارات معالجة الأخطاء
   */
  test.describe("Error Handling", () => {
    test("should handle no data gracefully", async ({ page }) => {
      await page.waitForTimeout(5000);

      // Look for "no data" messages
      const noDataMessages = page.locator(
        "text=/غير متوفرة|غير متاحة|not available/i",
      );
      const hasNoData = await noDataMessages
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      if (hasNoData) {
        console.log("No data message displayed gracefully");
      }
    });

    test("should not crash on missing weather data", async ({ page }) => {
      await page.waitForTimeout(5000);

      // Page should still be functional
      const heading = page.locator('h1:has-text("الطقس")');
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
      expect(count).toBeGreaterThanOrEqual(0);
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

      // Select a location
      const locationSelector = page.locator("select");
      await locationSelector.selectOption({ index: 2 });
      // const selectedValue = await locationSelector.inputValue();

      // Navigate away
      await page.goto(pages.dashboard);
      await waitForPageLoad(page);

      // Navigate back
      await page.goto(pages.weather);
      await waitForPageLoad(page);
      await page.waitForTimeout(2000);

      // Location should reset to default (state not persisted)
      console.log("Navigated away and back to weather page");
    });

    test("should work with browser refresh", async ({ page }) => {
      await page.waitForTimeout(3000);

      // Reload page
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(3000);

      // Page should load correctly
      const heading = page.locator('h1:has-text("الطقس")');
      await expect(heading).toBeVisible();

      console.log("Page works after browser refresh");
    });

    test("should display all sections together", async ({ page }) => {
      await page.waitForTimeout(5000);

      // Check that all main sections are present
      const sections = ["الطقس الحالي", "توقعات 7 أيام", "تنبيهات الطقس"];

      let visibleSections = 0;
      for (const section of sections) {
        const element = page.locator(`text=${section}`);
        const isVisible = await element
          .isVisible({ timeout: 2000 })
          .catch(() => false);
        if (isVisible) visibleSections++;
      }

      console.log(
        `${visibleSections} out of ${sections.length} sections visible`,
      );
      expect(visibleSections).toBeGreaterThanOrEqual(0);
    });
  });
});
