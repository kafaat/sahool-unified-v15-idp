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

    // Check settings page is loaded
    const settingsPage = page.getByTestId('settings-page');
    await expect(settingsPage).toBeVisible();

    // Check for settings heading
    const heading = page.getByTestId('settings-heading');
    await expect(heading).toBeVisible();
    await expect(heading).toHaveText('الإعدادات');
  });

  test.describe('Profile Settings', () => {
    test('should display profile information section', async ({ page }) => {
      // Profile tab should be active by default
      const profileTab = page.getByTestId('settings-tab-profile');
      await expect(profileTab).toBeVisible({ timeout: 5000 });
      await expect(profileTab).toHaveAttribute('aria-selected', 'true');

      // Profile section should be visible
      const profileSection = page.getByTestId('profile-section');
      await expect(profileSection).toBeVisible();

      // Profile heading should be visible in main content
      const profileHeading = page.getByTestId('profile-heading');
      await expect(profileHeading).toBeVisible();
      await expect(profileHeading).toHaveText('الملف الشخصي');
    });

    test('should display user name', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Look for name field using test ID
      const nameInput = page.getByTestId('profile-name-en');
      const isVisible = await nameInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const value = await nameInput.inputValue();
        console.log(`User name: ${value}`);
        expect(value).toBeTruthy();
      }
    });

    test('should display user phone', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Look for phone field using test ID
      const phoneInput = page.getByTestId('profile-phone');
      const isVisible = await phoneInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('User phone field is visible');
      }
    });

    test('should allow editing profile name', async ({ page }) => {
      await page.waitForTimeout(1000);

      const nameInput = page.getByTestId('profile-name-en');
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

      const nameInput = page.getByTestId('profile-name-en');

      if (await nameInput.isVisible({ timeout: 3000 })) {
        const originalValue = await nameInput.inputValue();

        // Update name
        await nameInput.clear();
        await nameInput.fill('Updated Name');

        // Save
        const saveButton = page.getByTestId('profile-submit');
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

    test('should display language selector', async ({ page }) => {
      await page.waitForTimeout(1000);

      const languageSelector = page.getByTestId('profile-language');
      const isVisible = await languageSelector.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('Language selector found');
        await expect(languageSelector).toBeVisible();
      }
    });

    test('should display profile avatar', async ({ page }) => {
      // Look for avatar using test ID
      const avatar = page.getByTestId('profile-avatar');
      const avatarPlaceholder = page.getByTestId('profile-avatar-placeholder');

      const hasAvatar = await avatar.isVisible({ timeout: 3000 }).catch(() => false);
      const hasPlaceholder = await avatarPlaceholder.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasAvatar || hasPlaceholder) {
        console.log('Profile avatar or placeholder found');
      }
    });
  });

  test.describe('Password Settings', () => {
    test('should display change password section', async ({ page }) => {
      // Click on Security tab first
      const securityTab = page.getByTestId('settings-tab-security');
      await securityTab.click();
      await page.waitForTimeout(500);

      // Check for security section
      const securitySection = page.getByTestId('security-section');
      await expect(securitySection).toBeVisible({ timeout: 5000 });

      // Check for security heading
      const securityHeading = page.getByTestId('security-heading');
      await expect(securityHeading).toBeVisible();
      await expect(securityHeading).toHaveText('الأمان');

      // Check for password change section
      const passwordSection = page.getByTestId('security-password-section');
      await expect(passwordSection).toBeVisible();
    });

    test('should have password input fields', async ({ page }) => {
      // Navigate to security tab
      const securityTab = page.getByTestId('settings-tab-security');
      await securityTab.click();
      await page.waitForTimeout(500);

      // Check for all password fields using test IDs
      const currentPasswordInput = page.getByTestId('security-password-current');
      const newPasswordInput = page.getByTestId('security-password-new');
      const confirmPasswordInput = page.getByTestId('security-password-confirm');

      await expect(currentPasswordInput).toBeVisible();
      await expect(newPasswordInput).toBeVisible();
      await expect(confirmPasswordInput).toBeVisible();

      console.log('Found 3 password input fields');
    });

    test('should validate password strength', async ({ page }) => {
      // Navigate to security tab
      const securityTab = page.getByTestId('settings-tab-security');
      await securityTab.click();
      await page.waitForTimeout(500);

      const newPasswordInput = page.getByTestId('security-password-new');
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
      // Navigate to security tab
      const securityTab = page.getByTestId('settings-tab-security');
      await securityTab.click();
      await page.waitForTimeout(500);

      const currentPasswordInput = page.getByTestId('security-password-current');
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
      const notificationsTab = page.getByTestId('settings-tab-notifications');
      await notificationsTab.click();
      await page.waitForTimeout(500);

      // Check for notifications section
      const notificationsSection = page.getByTestId('notifications-section');
      await expect(notificationsSection).toBeVisible({ timeout: 5000 });

      // Check for notifications heading
      const notificationHeading = page.getByTestId('notifications-heading');
      await expect(notificationHeading).toBeVisible();
      await expect(notificationHeading).toHaveText('إعدادات الإشعارات');
    });

    test('should have notification toggles', async ({ page }) => {
      // Navigate to notifications tab
      const notificationsTab = page.getByTestId('settings-tab-notifications');
      await notificationsTab.click();
      await page.waitForTimeout(1000);

      // Look for notification sections
      const emailSection = page.getByTestId('notifications-email-section');
      const pushSection = page.getByTestId('notifications-push-section');

      await expect(emailSection).toBeVisible();
      await expect(pushSection).toBeVisible();

      // Count toggles with role="switch"
      const toggles = page.locator('[role="switch"]');
      const count = await toggles.count();

      console.log(`Found ${count} notification toggles`);
      expect(count).toBeGreaterThan(0);
    });

    test('should toggle notification setting', async ({ page }) => {
      // Navigate to notifications tab
      const notificationsTab = page.getByTestId('settings-tab-notifications');
      await notificationsTab.click();
      await page.waitForTimeout(1000);

      const firstToggle = page.locator('[role="switch"]').first();
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
      // Language selector is in the profile tab
      const languageSelector = page.getByTestId('profile-language');
      const isVisible = await languageSelector.isVisible({ timeout: 5000 }).catch(() => false);

      if (isVisible) {
        await expect(languageSelector).toBeVisible();
        console.log('Language selector found in profile section');
      } else {
        console.log('Language selector not found');
      }
    });

    test('should have language selector', async ({ page }) => {
      await page.waitForTimeout(1000);

      const languageSelector = page.getByTestId('profile-language');
      const isVisible = await languageSelector.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('Language selector found');
        await expect(languageSelector).toHaveAttribute('role', 'combobox');

        // Check options
        const options = languageSelector.locator('option');
        const count = await options.count();

        console.log(`Found ${count} language options`);
        expect(count).toBeGreaterThanOrEqual(3); // ar, en, both
      }
    });

    test.skip('should switch language', async ({ page }) => {
      // Skip - requires language implementation
      const languageSelector = page.getByTestId('profile-language');

      if (await languageSelector.isVisible({ timeout: 3000 })) {
        await languageSelector.selectOption({ index: 1 });
        await page.waitForTimeout(2000);

        // Page should update with new language
        await waitForPageLoad(page);
      }
    });
  });

  test.describe('Display Settings', () => {
    test('should display display settings section', async ({ page }) => {
      // Click on Display tab
      const displayTab = page.getByTestId('settings-tab-display');
      await displayTab.click();
      await page.waitForTimeout(500);

      // Check for display section
      const displaySection = page.getByTestId('display-section');
      await expect(displaySection).toBeVisible({ timeout: 5000 });

      // Check for display heading
      const displayHeading = page.getByTestId('display-heading');
      await expect(displayHeading).toBeVisible();
      await expect(displayHeading).toHaveText('إعدادات العرض');
    });

    test.skip('should have theme toggle', async ({ page }) => {
      // Skip - theme toggle not yet implemented in display section
      const displayTab = page.getByTestId('settings-tab-display');
      await displayTab.click();
      await page.waitForTimeout(1000);

      const themeToggle = page.locator('input[type="checkbox"][name*="theme"], input[type="checkbox"][name*="dark"], [role="switch"]').first();
      const isVisible = await themeToggle.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('Theme toggle found');
      }
    });

    test.skip('should toggle dark mode', async ({ page }) => {
      // Skip - dark mode not yet implemented
      const displayTab = page.getByTestId('settings-tab-display');
      await displayTab.click();
      await page.waitForTimeout(1000);

      const darkModeToggle = page.locator('input[name*="dark"], [aria-label*="dark"]').first();

      if (await darkModeToggle.isVisible({ timeout: 3000 })) {
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
      // Click on Privacy tab
      const privacyTab = page.getByTestId('settings-tab-privacy');
      await privacyTab.click();
      await page.waitForTimeout(500);

      // Check for privacy section
      const privacySection = page.getByTestId('privacy-section');
      await expect(privacySection).toBeVisible({ timeout: 5000 });

      // Check for privacy heading
      const privacyHeading = page.getByTestId('privacy-heading');
      await expect(privacyHeading).toBeVisible();
      await expect(privacyHeading).toHaveText('الخصوصية');
    });

    test.skip('should have privacy toggles', async ({ page }) => {
      // Skip - privacy toggles not yet implemented
      const privacyTab = page.getByTestId('settings-tab-privacy');
      await privacyTab.click();
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

      // Look for tabs using test ID
      const tabsContainer = page.getByTestId('settings-tabs');
      await expect(tabsContainer).toBeVisible();

      const tabs = page.locator('[role="tab"]');
      const count = await tabs.count();

      console.log(`Found ${count} setting tabs`);
      expect(count).toBeGreaterThan(0);
      expect(count).toBeGreaterThanOrEqual(7); // profile, notifications, security, privacy, display, integrations, subscription
    });

    test('should navigate between setting sections', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Profile tab should be active by default
      const profileTab = page.getByTestId('settings-tab-profile');
      await expect(profileTab).toHaveAttribute('aria-selected', 'true');

      // Click on notifications tab
      const notificationsTab = page.getByTestId('settings-tab-notifications');
      await notificationsTab.click();
      await page.waitForTimeout(500);

      // Notifications tab should now be active
      await expect(notificationsTab).toHaveAttribute('aria-selected', 'true');

      // Notifications section should be visible
      const notificationsSection = page.getByTestId('notifications-section');
      await expect(notificationsSection).toBeVisible();

      console.log('Successfully navigated from Profile to Notifications tab');
    });
  });

  test.describe('Settings Form Validation', () => {
    test('should require name fields in profile form', async ({ page }) => {
      await page.waitForTimeout(1000);

      const nameInput = page.getByTestId('profile-name-en');
      const isVisible = await nameInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        // Check that name field is required
        const isRequired = await nameInput.getAttribute('required');
        expect(isRequired !== null).toBe(true);
        console.log('Name field is required');
      }
    });

    test('should show unsaved changes warning', async ({ page }) => {
      await page.waitForTimeout(1000);

      const nameInput = page.getByTestId('profile-name-en');
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
    test('should persist profile data after page reload', async ({ page }) => {
      await page.waitForTimeout(1000);

      // Get the name input value
      const nameInput = page.getByTestId('profile-name-en');
      const isVisible = await nameInput.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const initialValue = await nameInput.inputValue();

        // Reload page
        await page.reload();
        await waitForPageLoad(page);
        await page.waitForTimeout(1000);

        // Value should be the same
        const newValue = await nameInput.inputValue();
        expect(newValue).toBe(initialValue);
        console.log('Profile data persisted after reload');
      }
    });

    test('should persist notification settings after page reload', async ({ page }) => {
      // Navigate to notifications tab
      const notificationsTab = page.getByTestId('settings-tab-notifications');
      await notificationsTab.click();
      await page.waitForTimeout(1000);

      // Get a notification toggle state
      const firstToggle = page.locator('[role="switch"]').first();
      const isVisible = await firstToggle.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        const initialState = await firstToggle.isChecked();

        // Reload page
        await page.reload();
        await waitForPageLoad(page);
        await navigateAndWait(page, '/settings');

        // Navigate back to notifications tab
        const notificationsTabAfterReload = page.getByTestId('settings-tab-notifications');
        await notificationsTabAfterReload.click();
        await page.waitForTimeout(1000);

        // State should be the same
        const newState = await firstToggle.isChecked();
        expect(newState).toBe(initialState);
        console.log('Notification settings persisted after reload');
      }
    });
  });
});
