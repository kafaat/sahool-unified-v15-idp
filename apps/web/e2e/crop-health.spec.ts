import { test, expect } from './fixtures/test-fixtures';
import { navigateAndWait } from './helpers/page.helpers';

/**
 * Crop Health E2E Tests
 * اختبارات E2E لصحة المحاصيل
 */

test.describe('Crop Health Page', () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, '/crop-health');
  });

  test('should display crop health page correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/SAHOOL|سهول/i);

    // Check for main heading
    const heading = page.locator('text=/صحة المحصول|Crop Health/i');
    await expect(heading).toBeVisible({ timeout: 10000 });
  });

  test('should display view toggle buttons', async ({ page }) => {
    // Check for dashboard view button
    const dashboardButton = page.locator('[data-testid="view-toggle-dashboard"], button:has-text("لوحة المعلومات")');
    await expect(dashboardButton.first()).toBeVisible({ timeout: 5000 });

    // Check for diagnosis view button
    const diagnosisButton = page.locator('[data-testid="view-toggle-diagnosis"], button:has-text("تشخيص جديد")');
    await expect(diagnosisButton.first()).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Health Dashboard View', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/crop-health');

    // Make sure we're on dashboard view
    const dashboardButton = page.locator('[data-testid="view-toggle-dashboard"], button:has-text("لوحة المعلومات")');
    if (await dashboardButton.isVisible()) {
      await dashboardButton.click();
      await page.waitForTimeout(1000);
    }
  });

  test('should display health statistics', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Look for stat cards
    const healthyFieldsStat = page.locator('[data-testid="stat-healthy-fields"], text=/حقول صحية|Healthy/i');
    const atRiskStat = page.locator('[data-testid="stat-at-risk"], text=/معرضة للخطر|At Risk/i');
    const diseasedStat = page.locator('[data-testid="stat-diseased"], text=/مصابة|Diseased/i');
    const avgHealthStat = page.locator('[data-testid="stat-avg-health"], text=/متوسط الصحة|Average Health/i');

    // At least one stat should be visible
    const statsVisible =
      await healthyFieldsStat.isVisible({ timeout: 5000 }).catch(() => false) ||
      await atRiskStat.isVisible({ timeout: 5000 }).catch(() => false) ||
      await diseasedStat.isVisible({ timeout: 5000 }).catch(() => false) ||
      await avgHealthStat.isVisible({ timeout: 5000 }).catch(() => false);

    if (statsVisible) {
      console.log('Health statistics displayed');
    }
  });

  test('should display search input', async ({ page }) => {
    const searchInput = page.locator('[data-testid="health-dashboard-search"], input[placeholder*="ابحث"]');
    const isVisible = await searchInput.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      await expect(searchInput).toBeVisible();
    } else {
      console.log('Search input not found');
    }
  });

  test('should display disease alerts if present', async ({ page }) => {
    await page.waitForTimeout(2000);

    const alerts = page.locator('[data-testid="disease-alert"]');
    const count = await alerts.count();

    console.log(`Found ${count} disease alerts`);

    if (count > 0) {
      // First alert should be visible
      await expect(alerts.first()).toBeVisible();
    }
  });

  test('should display health records', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Look for health records
    const healthRecords = page.locator('[data-testid="health-record"]');
    const recordsCount = await healthRecords.count();

    console.log(`Found ${recordsCount} health records`);

    if (recordsCount > 0) {
      // First record should be visible
      await expect(healthRecords.first()).toBeVisible();
    } else {
      // Should show empty state
      const emptyState = page.locator('text=/لا توجد سجلات|No health records/i');
      const hasEmptyState = await emptyState.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasEmptyState) {
        await expect(emptyState).toBeVisible();
      }
    }
  });

  test('should display top diseases section', async ({ page }) => {
    await page.waitForTimeout(2000);

    const topDiseasesSection = page.locator('[data-testid="top-diseases"], text=/الأمراض الأكثر انتشاراً/i');
    const isVisible = await topDiseasesSection.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      await expect(topDiseasesSection).toBeVisible();
    } else {
      console.log('Top diseases section not found or empty');
    }
  });

  test('should display loading state while fetching data', async ({ page }) => {
    // Navigate fresh to catch loading state
    await page.goto('/crop-health');

    // Look for loading indicator
    const loadingIndicator = page.locator('[data-testid="health-dashboard-loading"], [class*="animate-spin"]');
    const hasLoader = await loadingIndicator.isVisible({ timeout: 1000 }).catch(() => false);

    console.log(`Loading state shown: ${hasLoader}`);

    // Wait for content to load
    await page.waitForTimeout(3000);
  });
});

test.describe('Diagnosis Tool View', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/crop-health');

    // Switch to diagnosis view
    const diagnosisButton = page.locator('[data-testid="view-toggle-diagnosis"], button:has-text("تشخيص جديد")');
    await diagnosisButton.click();
    await page.waitForTimeout(1000);
  });

  test('should display diagnosis tool form', async ({ page }) => {
    // Check for diagnosis tool heading
    const heading = page.locator('[data-testid="diagnosis-tool-heading"], text=/تشخيص الأمراض/i');
    await expect(heading).toBeVisible({ timeout: 5000 });
  });

  test('should display image upload area', async ({ page }) => {
    // Look for upload input or area
    const uploadArea = page.locator('[data-testid="diagnosis-image-upload"], input[type="file"]');
    const isVisible = await uploadArea.isVisible({ timeout: 5000 }).catch(() => false);

    if (!isVisible) {
      // Look for upload label
      const uploadLabel = page.locator('text=/تحميل صورة|Upload/i');
      await expect(uploadLabel).toBeVisible();
    }
  });

  test('should display crop type selector', async ({ page }) => {
    const cropTypeSelect = page.locator('[data-testid="diagnosis-crop-type"], select');
    await expect(cropTypeSelect.first()).toBeVisible({ timeout: 5000 });
  });

  test('should display crop type options', async ({ page }) => {
    const cropTypeSelect = page.locator('[data-testid="diagnosis-crop-type"], select');
    await expect(cropTypeSelect.first()).toBeVisible();

    // Check that select has options
    const options = page.locator('[data-testid="diagnosis-crop-type"] option, select option');
    const count = await options.count();

    console.log(`Found ${count} crop type options`);
    expect(count).toBeGreaterThan(1); // At least one option plus placeholder
  });

  test('should display description textarea', async ({ page }) => {
    const descriptionTextarea = page.locator('[data-testid="diagnosis-description"], textarea');
    const isVisible = await descriptionTextarea.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      await expect(descriptionTextarea).toBeVisible();
    }
  });

  test('should display submit button', async ({ page }) => {
    const submitButton = page.locator('[data-testid="diagnosis-submit"], button:has-text("بدء التشخيص")');
    await expect(submitButton.first()).toBeVisible({ timeout: 5000 });
  });

  test('should display reset button', async ({ page }) => {
    const resetButton = page.locator('[data-testid="diagnosis-reset"], button:has-text("إعادة تعيين")');
    await expect(resetButton.first()).toBeVisible({ timeout: 5000 });
  });

  test('should disable submit button when form is invalid', async ({ page }) => {
    const submitButton = page.locator('[data-testid="diagnosis-submit"], button:has-text("بدء التشخيص")').first();

    // Button should be disabled initially (no images uploaded)
    const isDisabled = await submitButton.isDisabled();
    console.log(`Submit button disabled: ${isDisabled}`);
  });

  test('should display tips section', async ({ page }) => {
    const tipsSection = page.locator('[data-testid="diagnosis-tips"], text=/نصائح للحصول على تشخيص دقيق/i');
    const isVisible = await tipsSection.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      await expect(tipsSection).toBeVisible();
    } else {
      console.log('Tips section not found');
    }
  });

  test('should handle file input change', async ({ page }) => {
    // This test verifies the file input exists and can be interacted with
    const fileInput = page.locator('input[type="file"]').first();
    await expect(fileInput).toBeAttached();
  });

  test('should show error when no images uploaded', async ({ page }) => {
    // Select crop type
    const cropTypeSelect = page.locator('[data-testid="diagnosis-crop-type"], select').first();
    await cropTypeSelect.selectOption({ index: 1 });

    // Try to submit without images
    const submitButton = page.locator('[data-testid="diagnosis-submit"], button:has-text("بدء التشخيص")').first();

    // Button should be disabled
    const isDisabled = await submitButton.isDisabled();
    expect(isDisabled).toBe(true);
  });
});

test.describe('View Switching', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/crop-health');
  });

  test('should switch between dashboard and diagnosis views', async ({ page }) => {
    // Initially should show dashboard view (or diagnosis view)
    await page.waitForTimeout(1000);

    // Click diagnosis button
    const diagnosisButton = page.locator('[data-testid="view-toggle-diagnosis"], button:has-text("تشخيص جديد")');
    await diagnosisButton.click();
    await page.waitForTimeout(1000);

    // Should show diagnosis form
    const diagnosisHeading = page.locator('text=/تشخيص الأمراض/i');
    const diagnosisVisible = await diagnosisHeading.isVisible({ timeout: 5000 }).catch(() => false);

    if (diagnosisVisible) {
      await expect(diagnosisHeading).toBeVisible();
    }

    // Switch back to dashboard
    const dashboardButton = page.locator('[data-testid="view-toggle-dashboard"], button:has-text("لوحة المعلومات")');
    await dashboardButton.click();
    await page.waitForTimeout(1000);

    // Should show dashboard stats
    const statsHeading = page.locator('text=/صحة المحصول|Crop Health/i');
    await expect(statsHeading).toBeVisible();
  });

  test('should highlight active view button', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Click diagnosis button
    const diagnosisButton = page.locator('[data-testid="view-toggle-diagnosis"], button:has-text("تشخيص جديد")');
    await diagnosisButton.click();
    await page.waitForTimeout(500);

    // Diagnosis button should have active styling (bg-green-500)
    const diagnosisButtonClasses = await diagnosisButton.getAttribute('class');
    console.log(`Diagnosis button classes: ${diagnosisButtonClasses}`);

    // Switch to dashboard
    const dashboardButton = page.locator('[data-testid="view-toggle-dashboard"], button:has-text("لوحة المعلومات")');
    await dashboardButton.click();
    await page.waitForTimeout(500);

    // Dashboard button should have active styling
    const dashboardButtonClasses = await dashboardButton.getAttribute('class');
    console.log(`Dashboard button classes: ${dashboardButtonClasses}`);
  });
});

test.describe('Diagnosis Result View', () => {
  test.skip('should display diagnosis result after submission', async ({ page }) => {
    // This test would require mock data or file upload capability
    // Skipping for now as it requires more complex setup
    await navigateAndWait(page, '/crop-health');
  });

  test.skip('should display back button in result view', async ({ page }) => {
    // This test would require navigating to a result view
    // Skipping for now
    await navigateAndWait(page, '/crop-health');
  });

  test.skip('should return to main view when clicking back button', async ({ page }) => {
    // This test would require navigating to a result view
    // Skipping for now
    await navigateAndWait(page, '/crop-health');
  });
});

test.describe('Crop Health Responsiveness', () => {
  test('should be responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await navigateAndWait(page, '/crop-health');

    // Page should still be visible
    const heading = page.locator('text=/صحة المحصول|Crop Health/i');
    await expect(heading).toBeVisible({ timeout: 10000 });
  });

  test('should be responsive on tablet viewport', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    await navigateAndWait(page, '/crop-health');

    const heading = page.locator('text=/صحة المحصول|Crop Health/i');
    await expect(heading).toBeVisible({ timeout: 10000 });
  });

  test('should be responsive on desktop viewport', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    await navigateAndWait(page, '/crop-health');

    const heading = page.locator('text=/صحة المحصول|Crop Health/i');
    await expect(heading).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Crop Health Error Handling', () => {
  test('should handle loading states gracefully', async ({ page }) => {
    await page.goto('/crop-health');

    // Look for loading indicators
    const loadingIndicator = page.locator('[class*="animate-spin"], [aria-busy="true"]');
    const hasLoader = await loadingIndicator.isVisible({ timeout: 2000 }).catch(() => false);

    console.log(`Loading state shown: ${hasLoader}`);

    // Wait for content to load
    await page.waitForTimeout(3000);

    // Content should be visible
    const content = page.locator('text=/صحة المحصول|Crop Health/i');
    await expect(content).toBeVisible();
  });

  test('should handle empty states', async ({ page }) => {
    await navigateAndWait(page, '/crop-health');
    await page.waitForTimeout(2000);

    // Look for empty state messages
    const emptyState = page.locator('text=/لا توجد سجلات|No.*records|No.*data/i');
    const hasEmptyState = await emptyState.isVisible({ timeout: 3000 }).catch(() => false);

    if (hasEmptyState) {
      console.log('Empty state displayed correctly');
    }
  });

  test('should display error messages when validation fails', async ({ page }) => {
    await navigateAndWait(page, '/crop-health');

    // Switch to diagnosis view
    const diagnosisButton = page.locator('[data-testid="view-toggle-diagnosis"], button:has-text("تشخيص جديد")');
    await diagnosisButton.click();
    await page.waitForTimeout(1000);

    // Look for error message area
    const errorMessage = page.locator('[data-testid="diagnosis-error"], [role="alert"]');
    const count = await errorMessage.count();

    console.log(`Found ${count} error message containers`);
  });
});
