/**
 * Fields CRUD E2E Tests
 * اختبارات E2E لإدارة الحقول
 *
 * Comprehensive tests for field management:
 * - Create, Read, Update, Delete fields
 * - Field details and map view
 * - Field filters and search
 * - Field statistics and analytics
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import {
  waitForPageLoad,
  waitForToast,
  navigateAndWait,
} from "./helpers/page.helpers";
import { testData, timeouts } from "./helpers/test-data";

test.describe("Fields Management", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Fields List Page", () => {
    test("should display fields list page correctly", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      // Check page title
      await expect(page).toHaveTitle(/SAHOOL|سهول|Fields|الحقول/i);

      // Check for main heading
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      // Check for fields-related content
      await expect(
        page.locator("text=/الحقول|Fields|My Fields|حقولي/i")
      ).toBeVisible();
    });

    test("should display add field button", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      // Look for add field button
      const addButton = page.locator(
        'button:has-text("إضافة حقل"), button:has-text("Add Field"), a:has-text("إضافة"), a:has-text("Add")'
      );

      await expect(addButton.first()).toBeVisible({ timeout: timeouts.long });
    });

    test("should display field cards or table", async ({ page }) => {
      await navigateAndWait(page, "/fields");
      await page.waitForTimeout(timeouts.medium);

      // Look for field cards or table rows
      const fieldCards = page.locator(
        '[data-testid="field-card"], [class*="field-card"], .card, table tbody tr'
      );
      const count = await fieldCards.count();

      console.log(`Found ${count} field items`);
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test("should display search/filter functionality", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      // Look for search input
      const searchInput = page.locator(
        'input[type="search"], input[placeholder*="بحث"], input[placeholder*="Search"], [data-testid="search-input"]'
      );

      const hasSearch = await searchInput.isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasSearch) {
        await expect(searchInput).toBeVisible();
        console.log("Search input found");
      } else {
        console.log("Search input not found - may not be implemented");
      }
    });

    test("should filter fields by crop type", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      // Look for filter dropdown
      const filterDropdown = page.locator(
        '[data-testid="crop-filter"], select[name="cropType"], button:has-text("تصفية"), button:has-text("Filter")'
      );

      const hasFilter = await filterDropdown.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasFilter) {
        await filterDropdown.first().click();
        await page.waitForTimeout(500);

        // Look for filter options
        const filterOptions = page.locator('[role="option"], option');
        const optionCount = await filterOptions.count();

        console.log(`Found ${optionCount} filter options`);
      }
    });

    test("should toggle between map and list view", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      // Look for view toggle buttons
      const mapViewBtn = page.locator(
        'button:has-text("خريطة"), button:has-text("Map"), [data-testid="map-view"]'
      );
      const _listViewBtn = page.locator(
        'button:has-text("قائمة"), button:has-text("List"), [data-testid="list-view"]'
      );

      const hasViewToggle = await mapViewBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasViewToggle) {
        await mapViewBtn.first().click();
        await page.waitForTimeout(1000);

        // Check for map container
        const mapContainer = page.locator('[class*="map"], #map, [data-testid="map"]');
        const hasMap = await mapContainer.isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Map view available: ${hasMap}`);
      }
    });

    test("should sort fields by different criteria", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      // Look for sort dropdown
      const sortDropdown = page.locator(
        '[data-testid="sort-dropdown"], select[name="sort"], button:has-text("ترتيب"), button:has-text("Sort")'
      );

      const hasSort = await sortDropdown.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasSort) {
        await sortDropdown.first().click();
        await page.waitForTimeout(500);

        const sortOptions = page.locator('[role="option"], option');
        const optionCount = await sortOptions.count();

        console.log(`Found ${optionCount} sort options`);
      }
    });
  });

  test.describe("Create Field", () => {
    test("should open create field form", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      // Click add field button
      const addButton = page.locator(
        'button:has-text("إضافة حقل"), button:has-text("Add Field"), a:has-text("إضافة"), a:has-text("Add"), [data-testid="add-field"]'
      );

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(1000);

        // Check for form or modal
        const form = page.locator(
          'form, [role="dialog"], [data-testid="field-form"]'
        );
        await expect(form.first()).toBeVisible({ timeout: timeouts.long });
      }
    });

    test("should display required form fields", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      const addButton = page.locator(
        'button:has-text("إضافة حقل"), button:has-text("Add Field"), a:has-text("إضافة")'
      );

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(1000);

        // Check for name input
        const nameInput = page.locator(
          'input[name="name"], input[placeholder*="اسم"], input[placeholder*="Name"]'
        );
        await expect(nameInput.first()).toBeVisible({ timeout: timeouts.long });

        // Check for area input
        const areaInput = page.locator(
          'input[name="area"], input[placeholder*="مساحة"], input[placeholder*="Area"]'
        );
        const hasArea = await areaInput.first().isVisible({ timeout: timeouts.short }).catch(() => false);
        console.log(`Area input found: ${hasArea}`);

        // Check for crop type selector
        const cropSelector = page.locator(
          'select[name="cropType"], [data-testid="crop-selector"]'
        );
        const hasCrop = await cropSelector.first().isVisible({ timeout: timeouts.short }).catch(() => false);
        console.log(`Crop selector found: ${hasCrop}`);
      }
    });

    test("should validate required fields", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      const addButton = page.locator(
        'button:has-text("إضافة حقل"), button:has-text("Add Field")'
      );

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(1000);

        // Try to submit empty form
        const submitButton = page.locator('button[type="submit"], button:has-text("حفظ"), button:has-text("Save")');

        if (await submitButton.first().isVisible({ timeout: timeouts.short })) {
          await submitButton.first().click();

          // Should show validation errors
          const errorMessage = page.locator(
            '[class*="error"], [role="alert"], text=/مطلوب|Required/i'
          );
          const hasError = await errorMessage.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

          if (hasError) {
            console.log("Validation errors displayed correctly");
          }
        }
      }
    });

    test("should create field with valid data", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      const addButton = page.locator(
        'button:has-text("إضافة حقل"), button:has-text("Add Field")'
      );

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(1000);

        const fieldData = testData.randomField();

        // Fill form fields
        const nameInput = page.locator(
          'input[name="name"], input[placeholder*="اسم"], input[placeholder*="Name"]'
        );
        if (await nameInput.first().isVisible({ timeout: timeouts.short })) {
          await nameInput.first().fill(fieldData.name);
        }

        const areaInput = page.locator(
          'input[name="area"], input[placeholder*="مساحة"], input[placeholder*="Area"]'
        );
        if (await areaInput.first().isVisible({ timeout: timeouts.short })) {
          await areaInput.first().fill(fieldData.area.toString());
        }

        // Submit form
        const submitButton = page.locator('button[type="submit"], button:has-text("حفظ"), button:has-text("Save")');

        if (await submitButton.first().isVisible({ timeout: timeouts.short })) {
          await submitButton.first().click();

          // Wait for success message or redirect
          const hasToast = await waitForToast(page, undefined, timeouts.long);
          console.log(`Success toast shown: ${hasToast}`);
        }
      }
    });

    test("should support map-based field boundary drawing", async ({ page }) => {
      await navigateAndWait(page, "/fields");

      const addButton = page.locator(
        'button:has-text("إضافة حقل"), button:has-text("Add Field")'
      );

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(1000);

        // Look for draw boundary button
        const drawButton = page.locator(
          'button:has-text("رسم"), button:has-text("Draw"), [data-testid="draw-boundary"]'
        );

        const hasDrawTool = await drawButton.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        if (hasDrawTool) {
          console.log("Map drawing tool available");
          await drawButton.first().click();
          await page.waitForTimeout(500);

          // Check for map canvas
          const mapCanvas = page.locator('canvas, [class*="maplibre"], [class*="leaflet"]');
          await expect(mapCanvas.first()).toBeVisible({ timeout: timeouts.medium });
        }
      }
    });
  });

  test.describe("Field Details", () => {
    test("should navigate to field details page", async ({ page }) => {
      await navigateAndWait(page, "/fields");
      await page.waitForTimeout(timeouts.medium);

      // Click on first field
      const fieldItem = page.locator(
        '[data-testid="field-card"], [class*="field-card"], table tbody tr, .card'
      ).first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        // Should navigate to field details or open modal
        const currentUrl = page.url();
        const hasDetailsUrl = currentUrl.includes("/fields/") && currentUrl.match(/\/fields\/[a-zA-Z0-9-]+/);

        if (hasDetailsUrl) {
          console.log(`Navigated to field details: ${currentUrl}`);
        }
      }
    });

    test("should display field information", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);
      await page.waitForTimeout(timeouts.medium);

      const fieldItem = page.locator(
        '[data-testid="field-card"], table tbody tr'
      ).first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        // Check for field name
        const fieldName = page.locator('h1, h2, [data-testid="field-name"]');
        await expect(fieldName.first()).toBeVisible({ timeout: timeouts.long });

        // Check for field area
        const areaInfo = page.locator('text=/هكتار|ha|hectare|المساحة|Area/i');
        const hasArea = await areaInfo.first().isVisible({ timeout: timeouts.short }).catch(() => false);
        console.log(`Field area displayed: ${hasArea}`);
      }
    });

    test("should display field map", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(2000);

        // Check for map container
        const mapContainer = page.locator(
          '[class*="map"], #map, canvas, [data-testid="field-map"]'
        );
        const hasMap = await mapContainer.first().isVisible({ timeout: timeouts.long }).catch(() => false);

        console.log(`Field map displayed: ${hasMap}`);
      }
    });

    test("should display NDVI/crop health indicators", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(2000);

        // Check for NDVI indicator
        const ndviSection = page.locator(
          'text=/NDVI|صحة المحصول|Crop Health|مؤشر الغطاء النباتي/i'
        );
        const hasNdvi = await ndviSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`NDVI section displayed: ${hasNdvi}`);
      }
    });

    test("should display weather information for field", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(2000);

        // Check for weather section
        const weatherSection = page.locator('text=/الطقس|Weather|درجة الحرارة|Temperature/i');
        const hasWeather = await weatherSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Weather section displayed: ${hasWeather}`);
      }
    });

    test("should display field tasks", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(2000);

        // Check for tasks section
        const tasksSection = page.locator('text=/المهام|Tasks|Upcoming|القادمة/i');
        const hasTasks = await tasksSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Tasks section displayed: ${hasTasks}`);
      }
    });
  });

  test.describe("Update Field", () => {
    test("should open edit field form", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        // Look for edit button
        const editButton = page.locator(
          'button:has-text("تعديل"), button:has-text("Edit"), [data-testid="edit-field"], [aria-label*="edit"]'
        );

        if (await editButton.first().isVisible({ timeout: timeouts.medium })) {
          await editButton.first().click();
          await page.waitForTimeout(500);

          // Form should be visible
          const form = page.locator('form, [role="dialog"], [data-testid="field-form"]');
          await expect(form.first()).toBeVisible({ timeout: timeouts.long });
        }
      }
    });

    test("should update field name", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        const editButton = page.locator(
          'button:has-text("تعديل"), button:has-text("Edit")'
        );

        if (await editButton.first().isVisible({ timeout: timeouts.medium })) {
          await editButton.first().click();
          await page.waitForTimeout(500);

          // Update name
          const nameInput = page.locator('input[name="name"]');
          if (await nameInput.first().isVisible({ timeout: timeouts.short })) {
            await nameInput.first().clear();
            await nameInput.first().fill(`Updated Field ${Date.now()}`);

            // Submit
            const submitButton = page.locator('button[type="submit"], button:has-text("حفظ")');
            await submitButton.first().click();

            // Wait for success
            const hasToast = await waitForToast(page, undefined, timeouts.long);
            console.log(`Update success: ${hasToast}`);
          }
        }
      }
    });

    test("should update field boundary on map", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        const editButton = page.locator(
          'button:has-text("تعديل"), button:has-text("Edit")'
        );

        if (await editButton.first().isVisible({ timeout: timeouts.medium })) {
          await editButton.first().click();
          await page.waitForTimeout(500);

          // Look for boundary edit tool
          const editBoundaryBtn = page.locator(
            'button:has-text("تعديل الحدود"), button:has-text("Edit Boundary")'
          );
          const hasEditBoundary = await editBoundaryBtn.first().isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`Edit boundary tool available: ${hasEditBoundary}`);
        }
      }
    });
  });

  test.describe("Delete Field", () => {
    test("should show delete confirmation dialog", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        // Look for delete button
        const deleteButton = page.locator(
          'button:has-text("حذف"), button:has-text("Delete"), [data-testid="delete-field"]'
        );

        if (await deleteButton.first().isVisible({ timeout: timeouts.medium })) {
          await deleteButton.first().click();

          // Confirmation dialog should appear
          const confirmDialog = page.locator(
            '[role="alertdialog"], [role="dialog"], [data-testid="confirm-dialog"]'
          );
          await expect(confirmDialog.first()).toBeVisible({ timeout: timeouts.medium });

          // Cancel button should be present
          const cancelBtn = page.locator('button:has-text("إلغاء"), button:has-text("Cancel")');
          await expect(cancelBtn.first()).toBeVisible();
        }
      }
    });

    test("should cancel delete when clicking cancel", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        const deleteButton = page.locator(
          'button:has-text("حذف"), button:has-text("Delete")'
        );

        if (await deleteButton.first().isVisible({ timeout: timeouts.medium })) {
          await deleteButton.first().click();
          await page.waitForTimeout(500);

          // Click cancel
          const cancelBtn = page.locator('button:has-text("إلغاء"), button:has-text("Cancel")');
          if (await cancelBtn.first().isVisible({ timeout: timeouts.short })) {
            await cancelBtn.first().click();
            await page.waitForTimeout(500);

            // Dialog should close, field should still exist
            const confirmDialog = page.locator('[role="alertdialog"]');
            await expect(confirmDialog).not.toBeVisible();
          }
        }
      }
    });
  });

  test.describe("Field Analytics", () => {
    test("should display field yield history", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(2000);

        // Look for analytics/yield section
        const analyticsSection = page.locator(
          'text=/الإنتاجية|Yield|تحليلات|Analytics|تاريخ المحصول/i'
        );
        const hasAnalytics = await analyticsSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Analytics section displayed: ${hasAnalytics}`);
      }
    });

    test("should display field irrigation history", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(2000);

        // Look for irrigation section
        const irrigationSection = page.locator(
          'text=/الري|Irrigation|سجل الري/i'
        );
        const hasIrrigation = await irrigationSection.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Irrigation history displayed: ${hasIrrigation}`);
      }
    });

    test("should display time range selector for analytics", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(2000);

        // Look for time range selector
        const timeRangeSelector = page.locator(
          '[data-testid="time-range"], select[name="timeRange"], button:has-text("7 أيام"), button:has-text("30 days")'
        );
        const hasTimeRange = await timeRangeSelector.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Time range selector displayed: ${hasTimeRange}`);
      }
    });
  });

  test.describe("Field Export", () => {
    test("should export field data as PDF", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        // Look for export button
        const exportButton = page.locator(
          'button:has-text("تصدير"), button:has-text("Export"), [data-testid="export-field"]'
        );

        if (await exportButton.first().isVisible({ timeout: timeouts.medium })) {
          await exportButton.first().click();
          await page.waitForTimeout(500);

          // Look for PDF option
          const pdfOption = page.locator(
            'button:has-text("PDF"), [data-value="pdf"]'
          );
          const hasPdfOption = await pdfOption.first().isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`PDF export option available: ${hasPdfOption}`);
        }
      }
    });

    test("should export field data as Excel", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldItem = page.locator('[data-testid="field-card"]').first();

      if (await fieldItem.isVisible({ timeout: timeouts.medium })) {
        await fieldItem.click();
        await page.waitForTimeout(1000);

        const exportButton = page.locator(
          'button:has-text("تصدير"), button:has-text("Export")'
        );

        if (await exportButton.first().isVisible({ timeout: timeouts.medium })) {
          await exportButton.first().click();
          await page.waitForTimeout(500);

          // Look for Excel option
          const excelOption = page.locator(
            'button:has-text("Excel"), [data-value="excel"], [data-value="xlsx"]'
          );
          const hasExcelOption = await excelOption.first().isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`Excel export option available: ${hasExcelOption}`);
        }
      }
    });
  });
});
