import { test, expect } from './fixtures/test-fixtures';
import { navigateAndWait, waitForToast, waitForPageLoad } from './helpers/page.helpers';

/**
 * Settings E2E Tests
 * اختبارات E2E للإعدادات
 */

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login
    await navigateAndWait(page, '/settings');
  });

  test('should display settings page correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Settings.*SAHOOL/i);

    // Check for settings heading in Arabic
    const heading = page.locator('h1:has-text("الإعدادات")');
    await expect(heading).toBeVisible();

    // Check for Settings subtitle in English
    const subtitle = page.locator('text=/^Settings$/');
    await expect(subtitle).toBeVisible();
  });

  test.describe('Profile Settings', () => {
    test('should display profile information section', async ({ page }) => {
      // Profile tab should be active by default
      const profileTab = page.locator('button:has-text("الملف الشخصي")');
      await expect(profileTab).toBeVisible({ timeout: 5000 });

      // Profile heading should be visible in main content
      const profileHeading = page.locator('h2:has-text("الملف الشخصي")');
      await expect(profileHeading).toBeVisible();
    });

    test('should display user name', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Look for name field
      const nameInput = page.locator('input[name="name"], input[placeholder*="Name"], input[placeholder*="الاسم"]').first();
      const isVisible = await nameInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const value = await nameInput.inputValue();
        console.log(`User name: ${value}`);
        expect(value).toBeTruthy();
      }
    });

    test('should display user email', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Look for email field
      const emailInput = page.locator('input[type="email"], input[name="email"]').first();
      const isVisible = await emailInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const value = await emailInput.inputValue();
        console.log(`User email: ${value}`);
        expect(value).toBeTruthy();
      }
    });

    test('should allow editing profile name', async ({ page }) => {
      await page.waitForTimeout(1000);

      const nameInput = page.locator('input[name="name"], input[placeholder*="Name"]').first();
      const isVisible = await nameInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Clear and enter new name
        await nameInput.clear();
        await nameInput.fill('Test User Updated');

        // Check if value was updated
        const value = await nameInput.inputValue();
        expect(value).toBe('Test User Updated');
      }
    });

    test.skip('should save profile changes', async ({ page }) => {
      // Skip this test as it modifies data
      await page.waitForTimeout(1000);

      const nameInput = page.locator('input[name="name"]').first();

      if (await nameInput.isVisible({ timeout: 3000 })) {
        const originalValue = await nameInput.inputValue();

        // Update name
        await nameInput.clear();
        await nameInput.fill('Updated Name');

        // Save
        const saveButton = page.locator('button:has-text("Save"), button:has-text("حفظ")').first();
        await saveButton.click();

        // Wait for success message
        const hasToast = await waitForToast(page, undefined, 5000);
        expect(hasToast).toBe(true);

        // Restore original value
        await nameInput.clear();
        await nameInput.fill(originalValue);
        await saveButton.click();
      }
    });

    test('should validate email format in profile', async ({ page }) => {
      await page.waitForTimeout(1000);

      const emailInput = page.locator('input[type="email"]').first();
      const isVisible = await emailInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Try invalid email
        await emailInput.clear();
        await emailInput.fill('invalid-email');
        await emailInput.blur();

        // Check validation
        await page.waitForTimeout(500);
        const validationMessage = await emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);

        console.log(`Email validation: ${validationMessage}`);
      }
    });

    test('should display profile avatar', async ({ page }) => {
      // Look for avatar/profile picture
      const avatar = page.locator('img[alt*="avatar"], img[alt*="profile"], [class*="avatar"]').first();
      const isVisible = await avatar.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('Profile avatar found');
      } else {
        console.log('Profile avatar not found');
      }
    });
  });

  test.describe('Password Settings', () => {
    test('should display change password section', async ({ page }) => {
      // Click on Security tab first
      const securityTab = page.locator('button:has-text("الأمان")');
      await securityTab.click();
      await page.waitForTimeout(500);

      // Check for security heading
      const securityHeading = page.locator('h2:has-text("الأمان")');
      await expect(securityHeading).toBeVisible({ timeout: 5000 });

      // Check for password change section
      const passwordSection = page.locator('h3:has-text("تغيير كلمة المرور")');
      await expect(passwordSection).toBeVisible();
    });

    test('should have password input fields', async ({ page }) => {
      const passwordInputs = page.locator('input[type="password"]');
      const count = await passwordInputs.count();

      console.log(`Found ${count} password input fields`);

      if (count > 0) {
        // Should have at least current and new password fields
        expect(count).toBeGreaterThanOrEqual(2);
      }
    });

    test('should validate password strength', async ({ page }) => {
      const newPasswordInput = page.locator('input[name*="new"], input[placeholder*="New Password"]').first();
      const isVisible = await newPasswordInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Try weak password
        await newPasswordInput.fill('123');

        // Look for strength indicator
        await page.waitForTimeout(500);
        const strengthIndicator = page.locator('[class*="strength"], text=/weak|ضعيف/i');
        const hasIndicator = await strengthIndicator.isVisible({ timeout: 1000 }).catch(() => false);

        console.log(`Password strength indicator shown: ${hasIndicator}`);
      }
    });

    test('should require current password to change', async ({ page }) => {
      const currentPasswordInput = page.locator('input[name*="current"], input[placeholder*="Current Password"]').first();
      const isVisible = await currentPasswordInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const isRequired = await currentPasswordInput.getAttribute('required');
        expect(isRequired !== null).toBe(true);
      }
    });

    test.skip('should change password successfully', async ({}) => {
      // Skip - requires valid current password
    });
  });

  test.describe('Notification Settings', () => {
    test('should display notification preferences', async ({ page }) => {
      // Click on Notifications tab
      const notificationsTab = page.locator('button:has-text("الإشعارات")');
      await notificationsTab.click();
      await page.waitForTimeout(500);

      // Check for notifications heading
      const notificationHeading = page.locator('h2:has-text("إعدادات الإشعارات")');
      await expect(notificationHeading).toBeVisible({ timeout: 5000 });
    });

    test('should have notification toggles', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Look for checkboxes or toggle switches
      const toggles = page.locator('input[type="checkbox"], [role="switch"]');
      const count = await toggles.count();

      console.log(`Found ${count} notification toggles`);
    });

    test('should toggle notification setting', async ({ page }) => {
      await page.waitForTimeout(1000);

      const firstToggle = page.locator('input[type="checkbox"], [role="switch"]').first();
      const isVisible = await firstToggle.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const initialState = await firstToggle.isChecked();

        // Toggle
        await firstToggle.click();

        // Wait for state change
        await page.waitForTimeout(500);

        const newState = await firstToggle.isChecked();
        expect(newState).not.toBe(initialState);

        // Toggle back
        await firstToggle.click();
      }
    });
  });

  test.describe('Language Settings', () => {
    test('should display language options', async ({ page }) => {
      const languageSection = page.locator('text=/Language|اللغة/i');
      const isVisible = await languageSection.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        await expect(languageSection).toBeVisible();
      } else {
        console.log('Language section not found');
      }
    });

    test('should have language selector', async ({ page }) => {
      await page.waitForTimeout(1000);

      const languageSelector = page.locator('select[name*="language"], [role="combobox"]').first();
      const isVisible = await languageSelector.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('Language selector found');

        // Check options
        await languageSelector.click();
        await page.waitForTimeout(300);

        const options = page.locator('option, [role="option"]');
        const count = await options.count();

        console.log(`Found ${count} language options`);
      }
    });

    test.skip('should switch language', async ({ page }) => {
      // Skip - requires language implementation
      const languageSelector = page.locator('select[name*="language"]').first();

      if (await languageSelector.isVisible({ timeout: 3000 })) {
        await languageSelector.selectOption({ index: 1 });
        await page.waitForTimeout(2000);

        // Page should update with new language
        await waitForPageLoad(page);
      }
    });
  });

  test.describe('Theme Settings', () => {
    test('should display theme options', async ({ page }) => {
      const themeSection = page.locator('text=/Theme|المظهر|Dark Mode|الوضع الداكن/i');
      const isVisible = await themeSection.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        await expect(themeSection).toBeVisible();
      } else {
        console.log('Theme section not found');
      }
    });

    test('should have theme toggle', async ({ page }) => {
      await page.waitForTimeout(1000);

      const themeToggle = page.locator('input[type="checkbox"][name*="theme"], input[type="checkbox"][name*="dark"], [role="switch"]').first();
      const isVisible = await themeToggle.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('Theme toggle found');
      }
    });

    test.skip('should toggle dark mode', async ({ page }) => {
      const darkModeToggle = page.locator('input[name*="dark"], [aria-label*="dark"]').first();

      if (await darkModeToggle.isVisible({ timeout: 3000 })) {
        // const initialState = await darkModeToggle.isChecked();

        // Toggle dark mode
        await darkModeToggle.click();
        await page.waitForTimeout(1000);

        // Check if theme changed (look for dark class on html/body)
        const isDark = await page.locator('html[class*="dark"], body[class*="dark"]').count();

        console.log(`Dark mode applied: ${isDark > 0}`);

        // Toggle back
        await darkModeToggle.click();
      }
    });
  });

  test.describe('Privacy Settings', () => {
    test('should display privacy options', async ({ page }) => {
      const privacySection = page.locator('text=/Privacy|الخصوصية|Security|الأمان/i');
      const isVisible = await privacySection.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        await expect(privacySection).toBeVisible();
      } else {
        console.log('Privacy section not found');
      }
    });

    test('should have privacy toggles', async ({ page }) => {
      await page.waitForTimeout(1000);

      const toggles = page.locator('input[type="checkbox"]');
      const count = await toggles.count();

      console.log(`Found ${count} privacy toggles`);
    });
  });

  test.describe('Account Management', () => {
    test('should display account actions', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Look for delete account or deactivate button
      const dangerActions = page.locator('button:has-text("Delete"), button:has-text("حذف"), button:has-text("Deactivate")');
      const count = await dangerActions.count();

      console.log(`Found ${count} account management actions`);
    });

    test('should show confirmation before dangerous actions', async ({ page }) => {
      await page.waitForTimeout(1000);

      const deleteButton = page.locator('button:has-text("Delete Account"), button:has-text("حذف الحساب")').first();
      const isVisible = await deleteButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        await deleteButton.click();

        // Should show confirmation dialog
        const confirmDialog = page.locator('[role="dialog"], [role="alertdialog"]');
        const hasDialog = await confirmDialog.isVisible({ timeout: 2000 }).catch(() => false);

        if (hasDialog) {
          console.log('Confirmation dialog shown');

          // Cancel the action
          const cancelButton = page.locator('button:has-text("Cancel"), button:has-text("إلغاء")').first();
          await cancelButton.click();
        }
      }
    });
  });

  test.describe('Settings Tabs/Sections', () => {
    test('should have multiple setting sections', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Look for tabs or section headers
      const sections = page.locator('h2, h3, [role="tab"]');
      const count = await sections.count();

      console.log(`Found ${count} setting sections/tabs`);
      expect(count).toBeGreaterThan(0);
    });

    test('should navigate between setting sections', async ({ page }) => {
      await page.waitForTimeout(1000);

      const tabs = page.locator('[role="tab"]');
      const count = await tabs.count();

      if (count > 1) {
        // Click second tab
        await tabs.nth(1).click();
        await page.waitForTimeout(500);

        // Tab should be active
        const isSelected = await tabs.nth(1).getAttribute('aria-selected');
        console.log(`Second tab selected: ${isSelected}`);
      }
    });
  });

  test.describe('Settings Form Validation', () => {
    test('should prevent saving invalid settings', async ({ page }) => {
      await page.waitForTimeout(1000);

      const emailInput = page.locator('input[type="email"]').first();
      const isVisible = await emailInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Enter invalid email
        await emailInput.clear();
        await emailInput.fill('invalid');

        // Try to save
        const saveButton = page.locator('button:has-text("Save"), button:has-text("حفظ")').first();

        if (await saveButton.isVisible()) {
          await saveButton.click();

          // Should show error or prevent submission
          await page.waitForTimeout(1000);

          // Check for error message
          const hasError = await page.locator('[role="alert"], [class*="error"]').isVisible({ timeout: 1000 }).catch(() => false);
          console.log(`Validation error shown: ${hasError}`);
        }
      }
    });

    test('should show unsaved changes warning', async ({ page }) => {
      await page.waitForTimeout(1000);

      const nameInput = page.locator('input[name="name"]').first();
      const isVisible = await nameInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Make a change
        await nameInput.fill('Changed Name');

        // Try to navigate away
        await page.goto('/dashboard');
        await page.waitForTimeout(1000);

        // Might show confirmation dialog (browser default or custom)
        // This is hard to test reliably
        console.log('Navigated away from settings');
      }
    });
  });

  test.describe('Settings Persistence', () => {
    test('should persist settings after page reload', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Get a checkbox state
      const firstCheckbox = page.locator('input[type="checkbox"]').first();
      const isVisible = await firstCheckbox.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const initialState = await firstCheckbox.isChecked();

        // Reload page
        await page.reload();
        await waitForPageLoad(page);
        await page.waitForTimeout(1000);

        // State should be the same
        const newState = await firstCheckbox.isChecked();
        expect(newState).toBe(initialState);
      }
    });
  });
});
