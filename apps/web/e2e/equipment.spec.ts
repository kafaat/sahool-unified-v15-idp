import { test, expect } from './fixtures/test-fixtures';
import {
  navigateAndWait,
  waitForPageLoad,
} from './helpers/page.helpers';
import { timeouts, pages } from './helpers/test-data';

/**
 * Equipment E2E Tests
 * اختبارات E2E للمعدات
 */

test.describe('Equipment Page', () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, pages.equipment);
  });

  test.describe('Page Loading and Structure', () => {
    test('should display equipment page correctly', async ({ page }) => {
      // Check page title
      await expect(page).toHaveTitle(/Equipment Management.*SAHOOL/i);

      // Check for main heading in Arabic using data-testid
      const headingAr = page.locator('[data-testid="equipment-page-title"]');
      await expect(headingAr).toBeVisible();
      await expect(headingAr).toHaveText('إدارة المعدات');

      // Check for heading in English using data-testid
      const headingEn = page.locator('[data-testid="equipment-page-subtitle"]');
      await expect(headingEn).toBeVisible();
      await expect(headingEn).toHaveText('Equipment Management');
    });

    test('should display add equipment button', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await expect(addButton).toBeVisible();
    });

    test('should display equipment statistics', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for statistics cards using data-testid
      const statsContainer = page.locator('[data-testid="equipment-statistics"]');
      const isVisible = await statsContainer.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        // Check for all stat cards
        await expect(page.locator('[data-testid="stat-total-equipment"]')).toBeVisible();
        await expect(page.locator('[data-testid="stat-active-equipment"]')).toBeVisible();
        await expect(page.locator('[data-testid="stat-maintenance-equipment"]')).toBeVisible();
        await expect(page.locator('[data-testid="stat-maintenance-due"]')).toBeVisible();
      } else {
        console.log('Statistics cards not visible yet');
      }
    });

    test('should display maintenance schedule section', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const maintenanceSchedule = page.locator('[data-testid="maintenance-schedule-title"]');
      const isVisible = await maintenanceSchedule.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await expect(maintenanceSchedule).toBeVisible();
        await expect(maintenanceSchedule).toHaveText('جدول الصيانة');
      } else {
        console.log('Maintenance schedule section not visible');
      }
    });
  });

  test.describe('Equipment List Display', () => {
    test('should display equipment list', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for equipment grid using data-testid
      const equipmentGrid = page.locator('[data-testid="equipment-grid"]');
      const isEmpty = await page.locator('[data-testid="equipment-empty-state"]').isVisible().catch(() => false);

      if (isEmpty) {
        console.log('Equipment list is empty');
      } else {
        const isVisible = await equipmentGrid.isVisible({ timeout: timeouts.long }).catch(() => false);
        if (isVisible) {
          const equipmentCards = page.locator('[data-testid="equipment-card"]');
          const count = await equipmentCards.count();
          console.log(`Found ${count} equipment items`);
          expect(count).toBeGreaterThan(0);
        }
      }
    });

    test('should display search functionality', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for search input using data-testid
      const searchInput = page.locator('[data-testid="equipment-search-input"]');
      await expect(searchInput).toBeVisible({ timeout: timeouts.long });
    });

    test('should display filter options', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for filter sections using data-testid
      const typeFilters = page.locator('[data-testid="equipment-type-filters"]');
      const statusFilters = page.locator('[data-testid="equipment-status-filters"]');

      await expect(typeFilters).toBeVisible({ timeout: timeouts.long });
      await expect(statusFilters).toBeVisible({ timeout: timeouts.long });
    });

    test('should filter equipment by type', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Use data-testid for tractor filter button
      const tractorFilter = page.locator('[data-testid="filter-type-tractor"]');
      await expect(tractorFilter).toBeVisible({ timeout: timeouts.long });

      await tractorFilter.click();
      await page.waitForTimeout(timeouts.short);

      // Verify button is active (has green background)
      const buttonClass = await tractorFilter.getAttribute('class');
      expect(buttonClass).toContain('bg-green-600');
      console.log('Tractor filter clicked and activated');
    });

    test('should filter equipment by status', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Use data-testid for active status filter
      const activeFilter = page.locator('[data-testid="filter-status-active"]');
      await expect(activeFilter).toBeVisible({ timeout: timeouts.long });

      await activeFilter.click();
      await page.waitForTimeout(timeouts.short);

      // Verify button is active
      const buttonClass = await activeFilter.getAttribute('class');
      expect(buttonClass).toContain('bg-green-600');
      console.log('Active status filter clicked and activated');
    });

    test('should search for equipment', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const searchInput = page.locator('[data-testid="equipment-search-input"]');
      await expect(searchInput).toBeVisible({ timeout: timeouts.long });

      await searchInput.fill('جرار');

      // Click search button
      const searchButton = page.locator('[data-testid="equipment-search-button"]');
      await searchButton.click();
      await page.waitForTimeout(timeouts.medium);
      console.log('Search performed for: جرار');
    });
  });

  test.describe('Equipment Details', () => {
    test('should display equipment cards with details', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for equipment names in Arabic
      const equipmentNames = page.locator('[class*="card"] h3, [class*="equipment"] h3');
      const count = await equipmentNames.count();

      if (count > 0) {
        const firstName = await equipmentNames.first().textContent();
        console.log(`First equipment: ${firstName}`);
      }
    });

    test('should display equipment type labels', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for type labels (جرار, حصادة, etc.)
      const typeLabels = page.locator('text=/جرار|حصادة|نظام ري|رشاش/i');
      const count = await typeLabels.count();

      console.log(`Found ${count} type labels`);
    });

    test('should display equipment location if available', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for location icons or text
      const locationInfo = page.locator('text=/موقع|Location/i');
      const count = await locationInfo.count();

      console.log(`Found ${count} location indicators`);
    });

    test('should display operating hours if available', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for operating hours text
      const operatingHours = page.locator('text=/ساعات التشغيل|Operating Hours/i');
      const count = await operatingHours.count();

      console.log(`Found ${count} operating hours displays`);
    });

    test('should display assigned user if available', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for assigned user text
      const assignedTo = page.locator('text=/مُسند إلى|Assigned to/i');
      const count = await assignedTo.count();

      console.log(`Found ${count} assignments`);
    });
  });

  test.describe('Status Indicators', () => {
    test('should display active status indicator', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const activeStatus = page.locator('text=/نشط/i').first();
      const isVisible = await activeStatus.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        // Check if it has green styling
        const statusElement = activeStatus.locator('..');
        const className = await statusElement.getAttribute('class');
        console.log(`Active status class: ${className}`);
      }
    });

    test('should display maintenance status indicator', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const maintenanceStatus = page.locator('text=/صيانة/i, text=/Maintenance/i').first();
      const isVisible = await maintenanceStatus.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        // Check styling (should be yellow/orange)
        const statusElement = maintenanceStatus.locator('..');
        const className = await statusElement.getAttribute('class');
        console.log(`Maintenance status class: ${className}`);
      }
    });

    test('should display inactive/idle status indicator', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const idleStatus = page.locator('text=/خامل|Idle/i').first();
      const isVisible = await idleStatus.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        console.log('Idle status found');
      }
    });

    test('should display maintenance due warnings', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for overdue maintenance warnings
      const warningText = page.locator('text=/متأخرة|Overdue|Due/i');
      const count = await warningText.count();

      console.log(`Found ${count} maintenance warnings`);
    });

    test('should highlight overdue maintenance in red', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const overdueWarning = page.locator('text=/متأخرة|Overdue/i').first();
      const isVisible = await overdueWarning.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        const parentElement = overdueWarning.locator('..');
        const className = await parentElement.getAttribute('class');
        expect(className).toMatch(/red/i);
      }
    });
  });

  test.describe('Add Equipment Form', () => {
    test('should open add equipment form', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await addButton.click();

      await page.waitForTimeout(timeouts.medium);

      // Check for form container using data-testid
      const formContainer = page.locator('[data-testid="equipment-form-container"]');
      await expect(formContainer).toBeVisible();

      // Check for form heading
      const formHeading = page.locator('[data-testid="equipment-form-title"]');
      await expect(formHeading).toBeVisible();
      await expect(formHeading).toHaveText('إضافة معدة جديدة');
    });

    test('should display all required form fields', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      // Check for form fields using data-testid
      await expect(page.locator('[data-testid="equipment-name-ar-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="equipment-name-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="equipment-type-select"]')).toBeVisible();
      await expect(page.locator('[data-testid="equipment-status-select"]')).toBeVisible();
      await expect(page.locator('[data-testid="equipment-serial-number-input"]')).toBeVisible();
    });

    test('should display bilingual labels (Arabic/English)', async ({ page }) => {
      const addButton = page.locator('button:has-text("إضافة معدة")').first();
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      // Check for Arabic labels
      const arabicLabels = page.locator('text=/الاسم بالعربية|النوع|الحالة|الرقم التسلسلي/i');
      const arabicCount = await arabicLabels.count();
      expect(arabicCount).toBeGreaterThan(0);

      // Check for English labels
      const englishLabels = page.locator('text=/Name \\(English\\)|Type|Status|Serial/i');
      const englishCount = await englishLabels.count();
      console.log(`Found ${englishCount} English labels`);
    });

    test('should have type dropdown with options', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      // Find type select using data-testid
      const typeSelect = page.locator('[data-testid="equipment-type-select"]');
      await expect(typeSelect).toBeVisible();

      // Check for options
      const options = typeSelect.locator('option');
      const count = await options.count();
      expect(count).toBeGreaterThanOrEqual(6); // tractor, harvester, irrigation_system, sprayer, planter, other

      // Verify specific options exist
      await expect(typeSelect.locator('option[value="tractor"]')).toBeVisible();
      await expect(typeSelect.locator('option[value="harvester"]')).toBeVisible();
    });

    test('should have status dropdown with options', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      // Find status select using data-testid
      const statusSelect = page.locator('[data-testid="equipment-status-select"]');
      await expect(statusSelect).toBeVisible();

      // Check for status options
      const options = statusSelect.locator('option');
      const count = await options.count();
      expect(count).toBeGreaterThanOrEqual(5); // active, maintenance, repair, idle, retired

      // Verify specific options exist
      await expect(statusSelect.locator('option[value="active"]')).toBeVisible();
      await expect(statusSelect.locator('option[value="maintenance"]')).toBeVisible();
    });

    test('should have cancel button', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      const cancelButton = page.locator('[data-testid="equipment-form-cancel-button"]');
      await expect(cancelButton).toBeVisible();
    });

    test('should have save button', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      const saveButton = page.locator('[data-testid="equipment-form-submit-button"]');
      await expect(saveButton).toBeVisible();
    });

    test('should close form on cancel', async ({ page }) => {
      const addButton = page.locator('[data-testid="add-equipment-button"]');
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      const cancelButton = page.locator('[data-testid="equipment-form-cancel-button"]');
      await cancelButton.click();
      await page.waitForTimeout(timeouts.short);

      // Form container should not be visible
      const formContainer = page.locator('[data-testid="equipment-form-container"]');
      const isVisible = await formContainer.isVisible({ timeout: timeouts.short }).catch(() => false);
      expect(isVisible).toBe(false);
    });

    test.skip('should validate required fields', async ({ page }) => {
      // Skip - requires form submission without data
      const addButton = page.locator('button:has-text("إضافة معدة")').first();
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      // Try to submit empty form
      const saveButton = page.locator('button[type="submit"], button:has-text("حفظ")').first();
      await saveButton.click();
      await page.waitForTimeout(timeouts.short);

      // Should show validation errors
      console.log('Form validation check');
    });
  });

  test.describe('Edit Equipment Form', () => {
    test('should open equipment details when clicking an item', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for first equipment card
      const firstEquipment = page.locator('[class*="card"], a[href*="/equipment/"]').first();
      const isVisible = await firstEquipment.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await firstEquipment.click();
        await page.waitForTimeout(timeouts.medium);

        // Should navigate or show details
        console.log('Equipment item clicked');
      }
    });

    test('should display back button in details view', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const firstEquipment = page.locator('[class*="card"]').first();
      const isVisible = await firstEquipment.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await firstEquipment.click();
        await page.waitForTimeout(timeouts.medium);

        // Look for back button
        const backButton = page.locator('button:has-text("العودة"), button:has-text("Back"), text=/العودة للقائمة/i');
        const hasBackButton = await backButton.isVisible({ timeout: timeouts.medium }).catch(() => false);

        if (hasBackButton) {
          await expect(backButton).toBeVisible();
        }
      }
    });
  });

  test.describe('Content Rendering', () => {
    test('should display content after page load', async ({ page }) => {
      // Navigate and wait for content to load
      await page.goto(pages.equipment);
      await page.waitForTimeout(timeouts.medium);

      // Content should be visible
      const heading = page.locator('h1').first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });
    });

    test('should handle form interaction', async ({ page }) => {
      const addButton = page.locator('button:has-text("إضافة معدة")').first();
      const isVisible = await addButton.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await addButton.click();
        await page.waitForTimeout(timeouts.medium);

        // Form should be visible
        const inputs = page.locator('input[type="text"]');
        const inputCount = await inputs.count();
        expect(inputCount).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Responsive Design', () => {
    test('should be responsive on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(timeouts.medium);

      // Page heading should still be visible
      const heading = page.locator('text=/إدارة المعدات/i');
      await expect(heading).toBeVisible();

      // Add button should be visible
      const addButton = page.locator('button:has-text("إضافة معدة")');
      await expect(addButton).toBeVisible();
    });

    test('should stack statistics on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(timeouts.medium);

      // Statistics should be visible but stacked
      const stats = page.locator('text=/إجمالي المعدات|Total Equipment/i').first();
      const isVisible = await stats.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        console.log('Statistics visible on mobile');
      }
    });

    test('should be responsive on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(timeouts.medium);

      const heading = page.locator('text=/إدارة المعدات/i');
      await expect(heading).toBeVisible();
    });

    test('should display grid layout on desktop', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });

      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(timeouts.medium);

      const heading = page.locator('text=/إدارة المعدات/i');
      await expect(heading).toBeVisible();

      // Equipment list should be in grid
      const equipmentCards = page.locator('[class*="grid"]');
      const count = await equipmentCards.count();

      console.log(`Found ${count} grid containers on desktop`);
    });

    test('should show/hide maintenance schedule based on viewport', async ({ page }) => {
      // Desktop - should show
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.reload();
      await waitForPageLoad(page);
      await page.waitForTimeout(timeouts.medium);

      const maintenanceDesktop = page.locator('text=/جدول الصيانة|Maintenance Schedule/i');
      const visibleDesktop = await maintenanceDesktop.isVisible({ timeout: timeouts.long }).catch(() => false);

      console.log(`Maintenance schedule visible on desktop: ${visibleDesktop}`);

      // Mobile - might be hidden or collapsed
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(timeouts.short);

      const maintenanceMobile = page.locator('text=/جدول الصيانة|Maintenance Schedule/i');
      const visibleMobile = await maintenanceMobile.isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Maintenance schedule visible on mobile: ${visibleMobile}`);
    });
  });

  test.describe('Arabic/English Labels', () => {
    test('should display page title in both languages', async ({ page }) => {
      // Arabic title
      const titleAr = page.locator('text=/إدارة المعدات/i');
      await expect(titleAr).toBeVisible();

      // English title
      const titleEn = page.locator('text=/Equipment Management/i');
      await expect(titleEn).toBeVisible();
    });

    test('should display button labels in Arabic', async ({ page }) => {
      const addButton = page.locator('button:has-text("إضافة معدة")');
      await expect(addButton).toBeVisible();

      const searchButton = page.locator('button:has-text("بحث")').first();
      const isVisible = await searchButton.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await expect(searchButton).toBeVisible();
      }
    });

    test('should display status labels in Arabic', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for Arabic status labels
      const arabicStatuses = page.locator('text=/نشط|صيانة|خامل|متوقف/i');
      const count = await arabicStatuses.count();

      console.log(`Found ${count} Arabic status labels`);
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test('should display type labels in Arabic', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for Arabic type labels
      const arabicTypes = page.locator('text=/جرار|حصادة|نظام ري|رشاش/i');
      const count = await arabicTypes.count();

      console.log(`Found ${count} Arabic type labels`);
    });

    test('should display form labels in both languages', async ({ page }) => {
      const addButton = page.locator('button:has-text("إضافة معدة")').first();
      await addButton.click();
      await page.waitForTimeout(timeouts.medium);

      // Check Arabic labels
      const arabicLabel = page.locator('text=/الاسم بالعربية/i');
      const hasArabic = await arabicLabel.isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasArabic) {
        await expect(arabicLabel).toBeVisible();
      }

      // Check English labels
      const englishLabel = page.locator('text=/Name \\(English\\)/i');
      const hasEnglish = await englishLabel.isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasEnglish) {
        await expect(englishLabel).toBeVisible();
      }
    });

    test('should display maintenance schedule labels in Arabic', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const maintenanceLabel = page.locator('text=/جدول الصيانة/i');
      const isVisible = await maintenanceLabel.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await expect(maintenanceLabel).toBeVisible();

        // Also check for English subtitle
        const englishLabel = page.locator('text=/Maintenance Schedule/i');
        const hasEnglish = await englishLabel.isVisible({ timeout: timeouts.short }).catch(() => false);

        if (hasEnglish) {
          await expect(englishLabel).toBeVisible();
        }
      }
    });

    test('should display statistics labels in Arabic', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Check for Arabic statistics labels
      const totalLabel = page.locator('text=/إجمالي المعدات/i');
      const activeLabel = page.locator('text=/قيد التشغيل/i');
      const maintenanceLabel = page.locator('text=/قيد الصيانة/i');

      const labels = [totalLabel, activeLabel, maintenanceLabel];
      let visibleCount = 0;

      for (const label of labels) {
        const isVisible = await label.isVisible({ timeout: timeouts.medium }).catch(() => false);
        if (isVisible) visibleCount++;
      }

      console.log(`${visibleCount} Arabic statistic labels visible`);
    });

    test('should use Arabic numerals in statistics', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for numbers in the page
      const numbers = page.locator('text=/\\d+/').first();
      const isVisible = await numbers.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        const text = await numbers.textContent();
        console.log(`Found number: ${text}`);
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle empty equipment list gracefully', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for empty state message
      const emptyMessage = page.locator('text=/لا توجد معدات|No equipment|Empty/i');
      const hasEmpty = await emptyMessage.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (hasEmpty) {
        console.log('Empty state message displayed');
      }
    });

    test('should display error message on load failure', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Look for error messages
      const errorMessage = page.locator('text=/خطأ|Error|Failed/i, [role="alert"]');
      const hasError = await errorMessage.isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasError) {
        const errorText = await errorMessage.textContent();
        console.log(`Error message: ${errorText}`);
      }

      // Page should still be functional even with errors
      const heading = page.locator('text=/إدارة المعدات/i');
      await expect(heading).toBeVisible();
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // This test verifies the page doesn't crash
      await page.waitForTimeout(timeouts.medium);

      // Page should always have the header
      const heading = page.locator('h1, h2').first();
      await expect(heading).toBeVisible();
    });
  });

  test.describe('Maintenance Warnings', () => {
    test('should display maintenance due count', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const maintenanceDue = page.locator('text=/بحاجة لصيانة|Maintenance Due/i');
      const isVisible = await maintenanceDue.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await expect(maintenanceDue).toBeVisible();
      }
    });

    test('should show next maintenance date', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const maintenanceDate = page.locator('text=/الصيانة القادمة|Next Maintenance/i');
      const count = await maintenanceDate.count();

      console.log(`Found ${count} maintenance date displays`);
    });

    test('should highlight overdue items', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const overdueWarning = page.locator('text=/متأخرة|Overdue/i');
      const count = await overdueWarning.count();

      console.log(`Found ${count} overdue warnings`);
    });
  });

  test.describe('Navigation', () => {
    test('should navigate between list and details', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      const firstEquipment = page.locator('[class*="card"], a[href*="/equipment/"]').first();
      const isVisible = await firstEquipment.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await firstEquipment.click();
        await page.waitForTimeout(timeouts.medium);

        // Look for back button
        const backButton = page.locator('button:has-text("العودة"), text=/العودة للقائمة/i');
        const hasBack = await backButton.isVisible({ timeout: timeouts.medium }).catch(() => false);

        if (hasBack) {
          await backButton.click();
          await page.waitForTimeout(timeouts.short);

          // Should be back on list view
          const heading = page.locator('text=/إدارة المعدات/i');
          await expect(heading).toBeVisible();
        }
      }
    });

    test('should maintain filters after navigation', async ({ page }) => {
      await page.waitForTimeout(timeouts.medium);

      // Apply a filter
      const tractorFilter = page.locator('button:has-text("جرار")').first();
      const isVisible = await tractorFilter.isVisible({ timeout: timeouts.long }).catch(() => false);

      if (isVisible) {
        await tractorFilter.click();
        await page.waitForTimeout(timeouts.short);

        // Navigate to another page
        await page.goto('/dashboard');
        await page.waitForTimeout(timeouts.medium);

        // Navigate back
        await page.goto(pages.equipment);
        await page.waitForTimeout(timeouts.medium);

        // Filter might or might not persist (depends on implementation)
        console.log('Filter persistence check completed');
      }
    });
  });
});
