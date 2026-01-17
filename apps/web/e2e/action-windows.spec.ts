/**
 * Action Windows (Spray/Irrigation) E2E Tests
 * اختبارات نوافذ الإجراءات (الرش والري)
 *
 * Tests for spray windows, irrigation windows, and weather-based recommendations.
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import { waitForPageLoad } from "./helpers/page.helpers";

test.describe("Action Windows", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Spray Windows", () => {
    test("should display spray windows panel", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Look for spray windows section
        await expect(
          page.locator("text=/نوافذ الرش|Spray Windows/i"),
        ).toBeVisible({ timeout: 10000 });
      }
    });

    test("should show 7-day spray forecast", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Click on spray windows tab/section
        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Should show 7 days
          const days = page.locator('[data-testid="spray-day"]');
          await expect(days).toHaveCount(7, { timeout: 10000 });
        }
      }
    });

    test("should display spray window status indicators", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Check for status indicators (optimal, good, poor, avoid)
          await expect(
            page
              .locator("text=/ممتاز|Optimal|جيد|Good|ضعيف|Poor|تجنب|Avoid/i")
              .first(),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test("should show spray window details on click", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Click on first day
          const firstDay = page.locator('[data-testid="spray-day"]').first();
          if (await firstDay.isVisible()) {
            await firstDay.click();

            // Details should be shown
            await expect(
              page.locator("text=/درجة الحرارة|Temperature/i"),
            ).toBeVisible({ timeout: 5000 });
            await expect(
              page.locator("text=/الرطوبة|Humidity/i"),
            ).toBeVisible();
            await expect(
              page.locator("text=/سرعة الرياح|Wind Speed/i"),
            ).toBeVisible();
          }
        }
      }
    });

    test("should display hourly breakdown for spray window", async ({
      page,
    }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          const firstDay = page.locator('[data-testid="spray-day"]').first();
          if (await firstDay.isVisible()) {
            await firstDay.click();

            // Should show hourly timeline
            await expect(
              page.locator('[data-testid="hourly-timeline"]'),
            ).toBeVisible({ timeout: 5000 });
          }
        }
      }
    });
  });

  test.describe("Irrigation Windows", () => {
    test("should display irrigation windows panel", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Look for irrigation windows section
        const irrigationTab = page.locator(
          'button:has-text("نوافذ الري"), button:has-text("Irrigation Windows")',
        );
        if (await irrigationTab.isVisible()) {
          await irrigationTab.click();

          await expect(
            page.locator('[data-testid="irrigation-windows-panel"]'),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test("should show irrigation recommendation status", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const irrigationTab = page.locator(
          'button:has-text("نوافذ الري"), button:has-text("Irrigation Windows")',
        );
        if (await irrigationTab.isVisible()) {
          await irrigationTab.click();

          // Should show recommendation
          await expect(
            page.locator(
              "text=/موصى به|Recommended|غير موصى به|Not Recommended/i",
            ),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test("should display soil moisture indicator", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const irrigationTab = page.locator(
          'button:has-text("نوافذ الري"), button:has-text("Irrigation Windows")',
        );
        if (await irrigationTab.isVisible()) {
          await irrigationTab.click();

          await expect(
            page.locator("text=/رطوبة التربة|Soil Moisture/i"),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test("should show rain probability in irrigation forecast", async ({
      page,
    }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const irrigationTab = page.locator(
          'button:has-text("نوافذ الري"), button:has-text("Irrigation Windows")',
        );
        if (await irrigationTab.isVisible()) {
          await irrigationTab.click();

          await expect(
            page.locator("text=/احتمالية الأمطار|Rain Probability/i"),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });
  });

  test.describe("Window Timeline", () => {
    test("should display window timeline visualization", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Timeline should be visible
          await expect(
            page.locator('[data-testid="window-timeline"]'),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test("should show optimal time slots in timeline", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Should show time slots
          await expect(
            page.locator('[data-testid="time-slot"]').first(),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });
  });

  test.describe("Weather Integration", () => {
    test("should display current weather conditions", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Current conditions should be shown
          await expect(
            page.locator("text=/الظروف الحالية|Current Conditions/i"),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test("should update windows based on weather changes", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Refresh button should be available
          const refreshBtn = page.locator(
            'button:has-text("تحديث"), button:has-text("Refresh")',
          );
          if (await refreshBtn.isVisible()) {
            await refreshBtn.click();

            // Loading indicator should appear
            await expect(page.locator('[data-testid="loading"]')).toBeVisible();

            // Then data should update
            await expect(page.locator('[data-testid="loading"]')).toBeHidden({
              timeout: 10000,
            });
          }
        }
      }
    });
  });

  test.describe("Alerts and Notifications", () => {
    test("should display window alerts if conditions change", async ({
      page,
    }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const sprayTab = page.locator(
          'button:has-text("نوافذ الرش"), button:has-text("Spray Windows")',
        );
        if (await sprayTab.isVisible()) {
          await sprayTab.click();

          // Check for any alerts
          const alert = page.locator('[data-testid="window-alert"]');
          if (await alert.isVisible()) {
            await expect(alert).toContainText(/تحذير|Warning|تنبيه|Alert/i);
          }
        }
      }
    });
  });
});
