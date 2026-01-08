/**
 * Reports E2E Tests
 * اختبارات التقارير
 *
 * Tests for report generation, preview, and export features.
 */

import { test, expect } from './fixtures/test-fixtures';
import { login, TEST_USER } from './helpers/auth.helpers';
import { waitForPageLoad, waitForToast } from './helpers/page.helpers';

test.describe('Reports Feature', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe('Report Generator', () => {
    test('should display report generator on field page', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        // Look for reports section
        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          await expect(
            page.locator('[data-testid="report-generator"]')
          ).toBeVisible({ timeout: 10000 });
        }
      }
    });

    test('should display report type selector', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Report type selector should be visible
          await expect(
            page.locator('[data-testid="report-type-selector"]')
          ).toBeVisible({ timeout: 10000 });

          // Check for report types
          const reportTypes = ['field', 'season'];
          for (const type of reportTypes) {
            await expect(
              page.locator(`[data-value="${type}"]`)
            ).toBeVisible();
          }
        }
      }
    });

    test('should display section checkboxes', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Sections should be available
          await expect(
            page.locator('text=/معلومات الحقل|Field Info/i')
          ).toBeVisible({ timeout: 10000 });
          await expect(
            page.locator('text=/NDVI|مؤشر الصحة/i')
          ).toBeVisible();
        }
      }
    });

    test('should toggle report sections', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Click on a section checkbox
          const sectionCheckbox = page.locator('input[type="checkbox"]').first();
          if (await sectionCheckbox.isVisible()) {
            const wasChecked = await sectionCheckbox.isChecked();
            await sectionCheckbox.click();

            // State should toggle
            const isNowChecked = await sectionCheckbox.isChecked();
            expect(isNowChecked).not.toBe(wasChecked);
          }
        }
      }
    });
  });

  test.describe('Report Generation', () => {
    test('should generate field report', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Select field report type
          const fieldReportBtn = page.locator('[data-value="field"], button:has-text("تقرير حقل"), button:has-text("Field Report")');
          if (await fieldReportBtn.isVisible()) {
            await fieldReportBtn.click();
          }

          // Click generate
          const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
          if (await generateBtn.isVisible()) {
            await generateBtn.click();

            // Wait for generation to complete
            await expect(
              page.locator('[data-testid="report-loading"]')
            ).toBeHidden({ timeout: 30000 });

            // Report preview should appear
            await expect(
              page.locator('[data-testid="report-preview"]')
            ).toBeVisible({ timeout: 10000 });
          }
        }
      }
    });

    test('should generate season report', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Select season report type
          const seasonReportBtn = page.locator('[data-value="season"], button:has-text("تقرير موسم"), button:has-text("Season Report")');
          if (await seasonReportBtn.isVisible()) {
            await seasonReportBtn.click();

            // Click generate
            const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
            await generateBtn.click();

            // Wait for generation
            await expect(
              page.locator('[data-testid="report-loading"]')
            ).toBeHidden({ timeout: 30000 });
          }
        }
      }
    });
  });

  test.describe('Report Preview', () => {
    test('should display report preview with navigation', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
          if (await generateBtn.isVisible()) {
            await generateBtn.click();
            await page.waitForTimeout(5000);

            // Check for navigation buttons
            await expect(
              page.locator('button:has-text("السابق"), button:has-text("Previous")')
            ).toBeVisible({ timeout: 10000 });
            await expect(
              page.locator('button:has-text("التالي"), button:has-text("Next")')
            ).toBeVisible();
          }
        }
      }
    });

    test('should show page count in preview', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
          if (await generateBtn.isVisible()) {
            await generateBtn.click();
            await page.waitForTimeout(5000);

            // Page count should be visible
            await expect(
              page.locator('text=/صفحة|Page/i')
            ).toBeVisible({ timeout: 10000 });
          }
        }
      }
    });
  });

  test.describe('Report Export', () => {
    test('should download report as PDF', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
          if (await generateBtn.isVisible()) {
            await generateBtn.click();
            await page.waitForTimeout(5000);

            // Click download button
            const downloadBtn = page.locator('button:has-text("تنزيل"), button:has-text("Download")');
            if (await downloadBtn.isVisible()) {
              const downloadPromise = page.waitForEvent('download');
              await downloadBtn.click();

              const download = await downloadPromise;
              expect(download.suggestedFilename()).toContain('.pdf');
            }
          }
        }
      }
    });

    test('should export report as Excel', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Find format selector
          const formatSelector = page.locator('[data-testid="format-selector"]');
          if (await formatSelector.isVisible()) {
            await formatSelector.click();

            // Select Excel
            const excelOption = page.locator('[data-value="excel"]');
            if (await excelOption.isVisible()) {
              await excelOption.click();

              // Generate
              const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
              await generateBtn.click();
              await page.waitForTimeout(5000);

              // Download
              const downloadBtn = page.locator('button:has-text("تنزيل"), button:has-text("Download")');
              if (await downloadBtn.isVisible()) {
                const downloadPromise = page.waitForEvent('download');
                await downloadBtn.click();

                const download = await downloadPromise;
                expect(download.suggestedFilename()).toMatch(/\.(xlsx|xls)$/);
              }
            }
          }
        }
      }
    });
  });

  test.describe('Report Sharing', () => {
    test('should open share menu', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
          if (await generateBtn.isVisible()) {
            await generateBtn.click();
            await page.waitForTimeout(5000);

            // Click share button
            const shareBtn = page.locator('button:has-text("مشاركة"), button:has-text("Share")');
            if (await shareBtn.isVisible()) {
              await shareBtn.click();

              // Share menu should open
              await expect(
                page.locator('[data-testid="share-menu"]')
              ).toBeVisible({ timeout: 5000 });
            }
          }
        }
      }
    });

    test('should copy share link', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
          if (await generateBtn.isVisible()) {
            await generateBtn.click();
            await page.waitForTimeout(5000);

            const shareBtn = page.locator('button:has-text("مشاركة"), button:has-text("Share")');
            if (await shareBtn.isVisible()) {
              await shareBtn.click();

              // Click copy link option
              const copyLinkBtn = page.locator('button:has-text("نسخ الرابط"), button:has-text("Copy Link")');
              if (await copyLinkBtn.isVisible()) {
                await copyLinkBtn.click();

                await waitForToast(page, /تم النسخ|Copied/i, 5000);
              }
            }
          }
        }
      }
    });
  });

  test.describe('Arabic RTL Support', () => {
    test('should generate report in Arabic', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Select Arabic language
          const languageSelector = page.locator('[data-testid="language-selector"]');
          if (await languageSelector.isVisible()) {
            await languageSelector.click();
            await page.locator('[data-value="ar"]').click();
          }

          const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
          if (await generateBtn.isVisible()) {
            await generateBtn.click();
            await page.waitForTimeout(5000);

            // Report should contain Arabic text
            await expect(
              page.locator('[data-testid="report-preview"]')
            ).toContainText(/[\u0600-\u06FF]/);
          }
        }
      }
    });

    test('should generate bilingual report', async ({ page }) => {
      await page.goto('/fields');
      await waitForPageLoad(page);

      const fieldCard = page.locator('[data-testid="field-card"]').first();
      if (await fieldCard.isVisible()) {
        await fieldCard.click();
        await waitForPageLoad(page);

        const reportsBtn = page.locator('button:has-text("التقارير"), button:has-text("Reports")');
        if (await reportsBtn.isVisible()) {
          await reportsBtn.click();

          // Select bilingual option
          const languageSelector = page.locator('[data-testid="language-selector"]');
          if (await languageSelector.isVisible()) {
            await languageSelector.click();
            await page.locator('[data-value="both"]').click();

            const generateBtn = page.locator('button:has-text("إنشاء"), button:has-text("Generate")');
            await generateBtn.click();
            await page.waitForTimeout(5000);

            // Report should contain both Arabic and English
            const preview = page.locator('[data-testid="report-preview"]');
            await expect(preview).toContainText(/[\u0600-\u06FF]/); // Arabic
            await expect(preview).toContainText(/[a-zA-Z]/); // English
          }
        }
      }
    });
  });
});
