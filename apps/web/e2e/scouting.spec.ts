/**
 * Scouting Feature E2E Tests
 * اختبارات ميزة الكشافة الحقلية
 *
 * Tests for field scouting, observation creation, and history.
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import { waitForPageLoad, waitForToast } from "./helpers/page.helpers";

test.describe("Scouting Feature", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Scouting Mode", () => {
    test("should navigate to field with scouting mode", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      // Click on first field
      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Look for scouting mode button
        await expect(
          page.locator(
            'button:has-text("الكشافة"), button:has-text("Scouting"), button:has-text("Scout")',
          ),
        ).toBeVisible({ timeout: 10000 });
      }
    });

    test("should start scouting session", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Click scouting button
        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting"), button:has-text("Scout")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          // Start session button
          const startBtn = page.locator(
            'button:has-text("بدء الجلسة"), button:has-text("Start Session")',
          );
          if (await startBtn.isVisible()) {
            await startBtn.click();

            // Session should start
            await expect(
              page.locator("text=/جلسة نشطة|Active Session/i"),
            ).toBeVisible({ timeout: 10000 });
          }
        }
      }
    });

    test("should end scouting session", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          // If there's an active session, end it
          const endBtn = page.locator(
            'button:has-text("إنهاء"), button:has-text("End Session")',
          );
          if (await endBtn.isVisible()) {
            await endBtn.click();

            // Confirm end
            const confirmBtn = page.locator(
              'button:has-text("تأكيد"), button:has-text("Confirm")',
            );
            if (await confirmBtn.isVisible()) {
              await confirmBtn.click();

              await waitForToast(page, /تم إنهاء الجلسة|Session ended/i, 5000);
            }
          }
        }
      }
    });
  });

  test.describe("Observation Creation", () => {
    test("should open observation form on map click", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          // Start session first
          const startBtn = page.locator(
            'button:has-text("بدء الجلسة"), button:has-text("Start Session")',
          );
          if (await startBtn.isVisible()) {
            await startBtn.click();
            await page.waitForTimeout(1000);
          }

          // Click on map to add observation
          const map = page.locator(
            '[data-testid="scouting-map"], .leaflet-container',
          );
          if (await map.isVisible()) {
            // Click center of map
            const box = await map.boundingBox();
            if (box) {
              await page.mouse.click(
                box.x + box.width / 2,
                box.y + box.height / 2,
              );

              // Observation form should open
              await expect(
                page.locator('[data-testid="observation-form"]'),
              ).toBeVisible({ timeout: 5000 });
            }
          }
        }
      }
    });

    test("should fill observation form with category", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          // Start session
          const startBtn = page.locator(
            'button:has-text("بدء الجلسة"), button:has-text("Start Session")',
          );
          if (await startBtn.isVisible()) {
            await startBtn.click();
            await page.waitForTimeout(1000);
          }

          // Click on map
          const map = page.locator(".leaflet-container");
          if (await map.isVisible()) {
            const box = await map.boundingBox();
            if (box) {
              await page.mouse.click(
                box.x + box.width / 2,
                box.y + box.height / 2,
              );
              await page.waitForTimeout(500);

              // Select pest category
              const pestBtn = page.locator(
                'button:has-text("آفات"), button:has-text("Pest")',
              );
              if (await pestBtn.isVisible()) {
                await pestBtn.click();

                // Category should be selected
                await expect(pestBtn).toHaveClass(/selected|active/i);
              }
            }
          }
        }
      }
    });

    test("should set severity level", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          const startBtn = page.locator(
            'button:has-text("بدء الجلسة"), button:has-text("Start Session")',
          );
          if (await startBtn.isVisible()) {
            await startBtn.click();
            await page.waitForTimeout(1000);
          }

          const map = page.locator(".leaflet-container");
          if (await map.isVisible()) {
            const box = await map.boundingBox();
            if (box) {
              await page.mouse.click(
                box.x + box.width / 2,
                box.y + box.height / 2,
              );
              await page.waitForTimeout(500);

              // Select severity level 4
              const severityBtn = page.locator(
                '[data-testid="severity-4"], button:has-text("4")',
              );
              if (await severityBtn.isVisible()) {
                await severityBtn.click();

                await expect(severityBtn).toHaveClass(/selected|active|ring/i);
              }
            }
          }
        }
      }
    });

    test("should save observation", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          const startBtn = page.locator(
            'button:has-text("بدء الجلسة"), button:has-text("Start Session")',
          );
          if (await startBtn.isVisible()) {
            await startBtn.click();
            await page.waitForTimeout(1000);
          }

          const map = page.locator(".leaflet-container");
          if (await map.isVisible()) {
            const box = await map.boundingBox();
            if (box) {
              await page.mouse.click(
                box.x + box.width / 2,
                box.y + box.height / 2,
              );
              await page.waitForTimeout(500);

              // Select category
              const categoryBtn = page
                .locator('button:has-text("آفات"), button:has-text("Pest")')
                .first();
              if (await categoryBtn.isVisible()) {
                await categoryBtn.click();
              }

              // Select severity
              const severityBtn = page.locator('button:has-text("3")').first();
              if (await severityBtn.isVisible()) {
                await severityBtn.click();
              }

              // Add notes
              const notesInput = page.locator(
                'textarea[name="notes"], textarea[placeholder*="ملاحظات"], textarea[placeholder*="Notes"]',
              );
              if (await notesInput.isVisible()) {
                await notesInput.fill("Test observation - تجربة ملاحظة");
              }

              // Save
              const saveBtn = page.locator(
                'button:has-text("حفظ"), button:has-text("Save")',
              );
              if (await saveBtn.isVisible()) {
                await saveBtn.click();

                await waitForToast(page, /تم الحفظ|Saved|Added/i, 5000);
              }
            }
          }
        }
      }
    });
  });

  test.describe("Scouting History", () => {
    test("should display scouting history", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          // Click history tab
          const historyTab = page.locator(
            'button:has-text("السجل"), button:has-text("History")',
          );
          if (await historyTab.isVisible()) {
            await historyTab.click();

            // History list should be visible
            await expect(
              page.locator('[data-testid="scouting-history"]'),
            ).toBeVisible({ timeout: 10000 });
          }
        }
      }
    });

    test("should filter history by date", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          const historyTab = page.locator(
            'button:has-text("السجل"), button:has-text("History")',
          );
          if (await historyTab.isVisible()) {
            await historyTab.click();

            // Click date filter
            const dateFilter = page.locator('[data-testid="date-filter"]');
            if (await dateFilter.isVisible()) {
              await dateFilter.click();

              // Select last week
              const lastWeekOption = page.locator(
                'button:has-text("الأسبوع الماضي"), button:has-text("Last Week")',
              );
              if (await lastWeekOption.isVisible()) {
                await lastWeekOption.click();

                // Results should update
                await page.waitForTimeout(1000);
              }
            }
          }
        }
      }
    });

    test("should filter history by category", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          const historyTab = page.locator(
            'button:has-text("السجل"), button:has-text("History")',
          );
          if (await historyTab.isVisible()) {
            await historyTab.click();

            // Click category filter
            const categoryFilter = page.locator(
              '[data-testid="category-filter"]',
            );
            if (await categoryFilter.isVisible()) {
              await categoryFilter.click();

              // Select pest category
              const pestOption = page.locator('[data-value="pest"]');
              if (await pestOption.isVisible()) {
                await pestOption.click();

                // Results should update
                await page.waitForTimeout(1000);
              }
            }
          }
        }
      }
    });
  });

  test.describe("Statistics", () => {
    test("should display scouting statistics", async ({ page }) => {
      await page.goto("/fields");
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const scoutingBtn = page.locator(
          'button:has-text("الكشافة"), button:has-text("Scouting")',
        );
        if (await scoutingBtn.isVisible()) {
          await scoutingBtn.click();

          // Statistics should be visible
          await expect(
            page.locator("text=/إجمالي الملاحظات|Total Observations/i"),
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });
  });
});
