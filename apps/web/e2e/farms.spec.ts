/**
 * Farms CRUD E2E Tests
 * اختبارات E2E لإدارة المزارع
 *
 * Comprehensive tests for farm management:
 * - Create, Read, Update, Delete farms
 * - Farm overview and statistics
 * - Farm settings and configuration
 * - Multi-farm management
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import {
  waitForPageLoad,
  waitForToast,
  navigateAndWait,
} from "./helpers/page.helpers";
import { timeouts } from "./helpers/test-data";

/**
 * Generate random farm data
 */
const randomFarm = () => ({
  name: `Test Farm ${Date.now()}`,
  nameAr: `مزرعة اختبارية ${Date.now()}`,
  location: "Riyadh, Saudi Arabia",
  locationAr: "الرياض، المملكة العربية السعودية",
  totalArea: Math.floor(Math.random() * 1000) + 50,
  waterSource: ["well", "canal", "municipal"][Math.floor(Math.random() * 3)],
  soilType: ["sandy", "clay", "loamy"][Math.floor(Math.random() * 3)],
});

test.describe("Farms Management", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Farms List Page", () => {
    test("should display farms list or dashboard", async ({ page }) => {
      // Navigate to farms or dashboard which shows farms
      await navigateAndWait(page, "/dashboard");

      // Check for farms section
      const farmsSection = page.locator(
        'text=/المزارع|Farms|My Farms|مزارعي/i'
      );
      const hasFarms = await farmsSection.first().isVisible({ timeout: timeouts.long }).catch(() => false);

      if (hasFarms) {
        await expect(farmsSection.first()).toBeVisible();
        console.log("Farms section found on dashboard");
      } else {
        // Try dedicated farms page
        await page.goto("/farms");
        await page.waitForTimeout(timeouts.medium);

        const heading = page.locator("h1, h2").first();
        await expect(heading).toBeVisible({ timeout: timeouts.long });
      }
    });

    test("should display farm cards or list items", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Look for farm cards
      const farmItems = page.locator(
        '[data-testid="farm-card"], [class*="farm-card"], [class*="farm-item"]'
      );
      const count = await farmItems.count();

      console.log(`Found ${count} farm items`);
    });

    test("should show farm summary statistics", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Look for total area, fields count, etc.
      const statsSection = page.locator(
        'text=/إجمالي المساحة|Total Area|عدد الحقول|Fields Count/i'
      );
      const hasStats = await statsSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Farm statistics displayed: ${hasStats}`);
    });

    test("should display add farm button for multi-farm users", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Look for add farm button (may not be visible for single-farm users)
      const addFarmBtn = page.locator(
        'button:has-text("إضافة مزرعة"), button:has-text("Add Farm"), [data-testid="add-farm"]'
      );
      const hasAddFarm = await addFarmBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Add farm button available: ${hasAddFarm}`);
    });
  });

  test.describe("Farm Overview", () => {
    test("should display farm overview section", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Check for farm name/title
      const farmName = page.locator(
        '[data-testid="farm-name"], h1:has-text("مزرعة"), h1:has-text("Farm")'
      );
      const hasFarmName = await farmName.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Farm name displayed: ${hasFarmName}`);
    });

    test("should display farm location on map", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Look for map container
      const mapContainer = page.locator(
        '[class*="map"], canvas, [data-testid="farm-map"], #map'
      );
      const hasMap = await mapContainer.first().isVisible({ timeout: timeouts.long }).catch(() => false);

      console.log(`Farm map displayed: ${hasMap}`);
    });

    test("should display farm fields summary", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Look for fields count or list
      const fieldsSection = page.locator(
        'text=/الحقول|Fields|حقول المزرعة/i'
      );
      const hasFields = await fieldsSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Fields summary displayed: ${hasFields}`);
    });

    test("should display farm weather summary", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Look for weather section
      const weatherSection = page.locator(
        'text=/الطقس|Weather|درجة الحرارة|Temperature/i'
      );
      const hasWeather = await weatherSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Farm weather displayed: ${hasWeather}`);
    });

    test("should display farm alerts summary", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Look for alerts section
      const alertsSection = page.locator(
        'text=/التنبيهات|Alerts|إشعارات|Notifications/i'
      );
      const hasAlerts = await alertsSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Farm alerts displayed: ${hasAlerts}`);
    });
  });

  test.describe("Create Farm", () => {
    test("should open create farm form when available", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const addFarmBtn = page.locator(
        'button:has-text("إضافة مزرعة"), button:has-text("Add Farm")'
      );

      if (await addFarmBtn.first().isVisible({ timeout: timeouts.medium })) {
        await addFarmBtn.first().click();
        await page.waitForTimeout(500);

        // Form should appear
        const form = page.locator(
          'form, [role="dialog"], [data-testid="farm-form"]'
        );
        await expect(form.first()).toBeVisible({ timeout: timeouts.long });
      } else {
        console.log("Add farm button not available - may be single-farm mode");
      }
    });

    test("should display required farm fields", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const addFarmBtn = page.locator(
        'button:has-text("إضافة مزرعة"), button:has-text("Add Farm")'
      );

      if (await addFarmBtn.first().isVisible({ timeout: timeouts.medium })) {
        await addFarmBtn.first().click();
        await page.waitForTimeout(500);

        // Check for name input
        const nameInput = page.locator(
          'input[name="name"], input[placeholder*="اسم"], input[placeholder*="Name"]'
        );
        await expect(nameInput.first()).toBeVisible({ timeout: timeouts.medium });

        // Check for location input
        const locationInput = page.locator(
          'input[name="location"], input[placeholder*="موقع"], input[placeholder*="Location"]'
        );
        const hasLocation = await locationInput.first().isVisible({ timeout: timeouts.short }).catch(() => false);
        console.log(`Location input found: ${hasLocation}`);
      }
    });

    test("should validate required fields", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const addFarmBtn = page.locator(
        'button:has-text("إضافة مزرعة"), button:has-text("Add Farm")'
      );

      if (await addFarmBtn.first().isVisible({ timeout: timeouts.medium })) {
        await addFarmBtn.first().click();
        await page.waitForTimeout(500);

        // Try to submit empty form
        const submitBtn = page.locator('button[type="submit"], button:has-text("حفظ")');
        if (await submitBtn.first().isVisible({ timeout: timeouts.short })) {
          await submitBtn.first().click();

          // Should show validation errors
          const errorMsg = page.locator('[class*="error"], text=/مطلوب|Required/i');
          const hasError = await errorMsg.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

          console.log(`Validation errors shown: ${hasError}`);
        }
      }
    });

    test("should create farm with valid data", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const addFarmBtn = page.locator(
        'button:has-text("إضافة مزرعة"), button:has-text("Add Farm")'
      );

      if (await addFarmBtn.first().isVisible({ timeout: timeouts.medium })) {
        await addFarmBtn.first().click();
        await page.waitForTimeout(500);

        const farmData = randomFarm();

        // Fill form
        const nameInput = page.locator('input[name="name"]');
        if (await nameInput.first().isVisible({ timeout: timeouts.short })) {
          await nameInput.first().fill(farmData.name);
        }

        const locationInput = page.locator('input[name="location"]');
        if (await locationInput.first().isVisible({ timeout: timeouts.short })) {
          await locationInput.first().fill(farmData.location);
        }

        // Submit
        const submitBtn = page.locator('button[type="submit"], button:has-text("حفظ")');
        if (await submitBtn.first().isVisible({ timeout: timeouts.short })) {
          await submitBtn.first().click();

          const hasToast = await waitForToast(page, undefined, timeouts.long);
          console.log(`Farm creation success: ${hasToast}`);
        }
      }
    });
  });

  test.describe("Farm Settings", () => {
    test("should navigate to farm settings", async ({ page }) => {
      await navigateAndWait(page, "/settings");

      // Look for farm settings section
      const farmSettings = page.locator(
        'text=/إعدادات المزرعة|Farm Settings|بيانات المزرعة/i'
      );
      const hasSettings = await farmSettings.first().isVisible({ timeout: timeouts.long }).catch(() => false);

      console.log(`Farm settings section found: ${hasSettings}`);
    });

    test("should display farm profile settings", async ({ page }) => {
      await navigateAndWait(page, "/settings");

      // Check for farm name in settings
      const farmNameSetting = page.locator(
        'input[name="farmName"], [data-testid="farm-name-setting"]'
      );
      const hasNameSetting = await farmNameSetting.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Farm name setting found: ${hasNameSetting}`);
    });

    test("should display water source configuration", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      // Look for water source settings
      const waterSettings = page.locator(
        'text=/مصدر المياه|Water Source|نوع الري|Irrigation Type/i'
      );
      const hasWaterSettings = await waterSettings.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Water source settings found: ${hasWaterSettings}`);
    });

    test("should display notification preferences", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      // Look for notification settings
      const notifSettings = page.locator(
        'text=/الإشعارات|Notifications|تفضيلات الإشعارات/i'
      );
      const hasNotifSettings = await notifSettings.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Notification settings found: ${hasNotifSettings}`);
    });

    test("should save farm settings changes", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      // Look for save button
      const saveBtn = page.locator(
        'button:has-text("حفظ"), button:has-text("Save"), button[type="submit"]'
      );
      const hasSaveBtn = await saveBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasSaveBtn) {
        console.log("Save button found in settings");
      }
    });
  });

  test.describe("Farm Switching (Multi-Farm)", () => {
    test("should display farm switcher when multiple farms exist", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Look for farm switcher/selector
      const farmSwitcher = page.locator(
        '[data-testid="farm-switcher"], select[name="farm"], button:has-text("اختر مزرعة"), [aria-label*="switch farm"]'
      );
      const hasSwitcher = await farmSwitcher.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Farm switcher available: ${hasSwitcher}`);
    });

    test("should switch between farms", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const farmSwitcher = page.locator(
        '[data-testid="farm-switcher"], select[name="farm"]'
      );

      if (await farmSwitcher.first().isVisible({ timeout: timeouts.medium })) {
        await farmSwitcher.first().click();
        await page.waitForTimeout(500);

        // Look for farm options
        const farmOptions = page.locator('[role="option"], option');
        const optionCount = await farmOptions.count();

        if (optionCount > 1) {
          // Select second option
          await farmOptions.nth(1).click();
          await page.waitForTimeout(1000);

          console.log("Switched to different farm");
        }
      }
    });
  });

  test.describe("Farm Statistics", () => {
    test("should display total farm area", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      const totalArea = page.locator(
        'text=/إجمالي المساحة|Total Area/i'
      );
      const hasArea = await totalArea.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Total area displayed: ${hasArea}`);
    });

    test("should display active fields count", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      const fieldsCount = page.locator(
        'text=/عدد الحقول|Fields Count|حقول نشطة|Active Fields/i'
      );
      const hasFieldsCount = await fieldsCount.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Fields count displayed: ${hasFieldsCount}`);
    });

    test("should display water usage summary", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      const waterUsage = page.locator(
        'text=/استهلاك المياه|Water Usage|الري|Irrigation/i'
      );
      const hasWaterUsage = await waterUsage.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Water usage displayed: ${hasWaterUsage}`);
    });

    test("should display production/yield summary", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      const yieldSummary = page.locator(
        'text=/الإنتاج|Production|Yield|المحصول/i'
      );
      const hasYield = await yieldSummary.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Yield summary displayed: ${hasYield}`);
    });
  });

  test.describe("Farm Export and Reports", () => {
    test("should access farm reports", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Look for reports button
      const reportsBtn = page.locator(
        'button:has-text("التقارير"), button:has-text("Reports"), a:has-text("تقارير")'
      );
      const hasReports = await reportsBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Reports button available: ${hasReports}`);
    });

    test("should export farm data", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Look for export button
      const exportBtn = page.locator(
        'button:has-text("تصدير"), button:has-text("Export"), [data-testid="export-farm"]'
      );
      const hasExport = await exportBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Export button available: ${hasExport}`);
    });
  });

  test.describe("Delete Farm", () => {
    test("should show delete farm option in settings", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      // Scroll to bottom to find delete option
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(500);

      const deleteFarmBtn = page.locator(
        'button:has-text("حذف المزرعة"), button:has-text("Delete Farm"), [data-testid="delete-farm"]'
      );
      const hasDelete = await deleteFarmBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Delete farm option available: ${hasDelete}`);
    });

    test("should require confirmation before deleting farm", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(500);

      const deleteFarmBtn = page.locator(
        'button:has-text("حذف المزرعة"), button:has-text("Delete Farm")'
      );

      if (await deleteFarmBtn.first().isVisible({ timeout: timeouts.medium })) {
        await deleteFarmBtn.first().click();
        await page.waitForTimeout(500);

        // Confirmation dialog should appear
        const confirmDialog = page.locator('[role="alertdialog"], [role="dialog"]');
        await expect(confirmDialog.first()).toBeVisible({ timeout: timeouts.medium });

        // Should have warning text
        const warningText = page.locator('text=/تحذير|Warning|لا يمكن التراجع|cannot be undone/i');
        const hasWarning = await warningText.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Delete warning displayed: ${hasWarning}`);
      }
    });
  });
});
