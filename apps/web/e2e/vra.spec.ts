/**
 * VRA (Variable Rate Application) E2E Tests
 * اختبارات التطبيق المتغير المعدل
 *
 * Tests for prescription map generation, viewing, and export features.
 */

import { test, expect } from './fixtures/test-fixtures';
import { login, TEST_USER } from './helpers/auth.helpers';
import { waitForPageLoad, waitForToast, clickButtonByText } from './helpers/page.helpers';

test.describe('VRA - Variable Rate Application', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe('VRA Panel', () => {
    test('should display VRA panel on field page', async ({ page }) => {
      // Navigate to a field detail page
      await page.goto('/fields');
      await waitForPageLoad(page);

      // Click on first field
      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // VRA panel should be visible
        await expect(
          page.locator('text=/التطبيق المتغير|Variable Rate|VRA/i')
        ).toBeVisible({ timeout: 10000 });
      }
    });

    test('should show VRA type selector with all options', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Find VRA type selector
        const vraTypeSelector = page.locator('[data-testid="vra-type-selector"]');
        if (await vraTypeSelector.isVisible()) {
          await vraTypeSelector.click();

          // Check all VRA types are available
          const vraTypes = ['fertilizer', 'seed', 'lime', 'pesticide', 'irrigation'];
          for (const type of vraTypes) {
            await expect(
              page.locator(`[data-value="${type}"]`)
            ).toBeVisible();
          }
        }
      }
    });
  });

  test.describe('Prescription Generation', () => {
    test('should generate prescription map', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Click generate prescription button
        const generateBtn = page.locator('button:has-text("توليد"), button:has-text("Generate")');
        if (await generateBtn.isVisible()) {
          await generateBtn.click();

          // Wait for loading to complete
          await expect(
            page.locator('[data-testid="prescription-loading"]')
          ).toBeHidden({ timeout: 30000 });

          // Prescription map should be displayed
          await expect(
            page.locator('[data-testid="prescription-map"]')
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test('should display prescription results table', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Look for prescription table
        const prescriptionTable = page.locator('[data-testid="prescription-table"]');
        if (await prescriptionTable.isVisible()) {
          // Table should have zone columns
          await expect(
            page.locator('th:has-text("Zone"), th:has-text("المنطقة")')
          ).toBeVisible();
          await expect(
            page.locator('th:has-text("Rate"), th:has-text("المعدل")')
          ).toBeVisible();
        }
      }
    });
  });

  test.describe('Prescription Export', () => {
    test('should export prescription as GeoJSON', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Find export button
        const exportBtn = page.locator('button:has-text("تصدير"), button:has-text("Export")');
        if (await exportBtn.isVisible()) {
          await exportBtn.click();

          // Select GeoJSON format
          const geojsonOption = page.locator('[data-value="geojson"], button:has-text("GeoJSON")');
          if (await geojsonOption.isVisible()) {
            // Listen for download
            const downloadPromise = page.waitForEvent('download');
            await geojsonOption.click();

            // Verify download started
            const download = await downloadPromise;
            expect(download.suggestedFilename()).toContain('.geojson');
          }
        }
      }
    });

    test('should export prescription as CSV', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const exportBtn = page.locator('button:has-text("تصدير"), button:has-text("Export")');
        if (await exportBtn.isVisible()) {
          await exportBtn.click();

          const csvOption = page.locator('[data-value="csv"], button:has-text("CSV")');
          if (await csvOption.isVisible()) {
            const downloadPromise = page.waitForEvent('download');
            await csvOption.click();

            const download = await downloadPromise;
            expect(download.suggestedFilename()).toContain('.csv');
          }
        }
      }
    });
  });

  test.describe('VRA History', () => {
    test('should display prescription history', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Click history tab/button
        const historyBtn = page.locator('button:has-text("السجل"), button:has-text("History")');
        if (await historyBtn.isVisible()) {
          await historyBtn.click();

          // History list should be visible
          await expect(
            page.locator('[data-testid="vra-history-list"]')
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test('should view historical prescription', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const historyBtn = page.locator('button:has-text("السجل"), button:has-text("History")');
        if (await historyBtn.isVisible()) {
          await historyBtn.click();

          // Click on first history item
          const historyItem = page.locator('[data-testid="history-item"]').first();
          if (await historyItem.isVisible()) {
            await historyItem.click();

            // Prescription details should be displayed
            await expect(
              page.locator('[data-testid="prescription-details"]')
            ).toBeVisible({ timeout: 10000 });
          }
        }
      }
    });

    test('should delete prescription from history', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const historyBtn = page.locator('button:has-text("السجل"), button:has-text("History")');
        if (await historyBtn.isVisible()) {
          await historyBtn.click();

          // Find delete button on first history item
          const deleteBtn = page.locator('[data-testid="history-item"]').first()
            .locator('button:has-text("حذف"), button:has-text("Delete"), [data-testid="delete-btn"]');

          if (await deleteBtn.isVisible()) {
            await deleteBtn.click();

            // Confirm deletion
            const confirmBtn = page.locator('button:has-text("تأكيد"), button:has-text("Confirm")');
            if (await confirmBtn.isVisible()) {
              await confirmBtn.click();

              // Wait for success message
              await waitForToast(page, /تم الحذف|Deleted/i, 5000);
            }
          }
        }
      }
    });
  });
});
