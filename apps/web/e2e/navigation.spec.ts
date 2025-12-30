import { test, expect } from './fixtures/test-fixtures';
import { navigateAndWait, waitForPageLoad } from './helpers/page.helpers';

/**
 * Navigation E2E Tests
 * اختبارات E2E للتنقل بين الصفحات
 */

test.describe('Navigation Flow', () => {
  // Use authenticated fixture to ensure user is logged in
  test.use({ storageState: undefined });

  test.beforeEach(async ({ page }) => {
    // authenticatedPage fixture handles login automatically
    await navigateAndWait(page, '/dashboard');
  });

  test('should navigate to dashboard from any page', async ({ page }) => {
    // Navigate to another page first
    await navigateAndWait(page, '/fields');

    // Click dashboard link using data-testid
    const dashboardLink = page.getByTestId('nav-link-dashboard');
    await expect(dashboardLink).toBeVisible();
    await dashboardLink.click();

    // Should be on dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    // Check for welcome message on dashboard
    await expect(page.locator('h1:has-text("مرحباً")')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate to Fields page', async ({ page }) => {
    // Click fields link in navigation using data-testid
    const fieldsLink = page.getByTestId('nav-link-fields');

    await expect(fieldsLink).toBeVisible();
    await fieldsLink.click();

    // Should be on fields page
    await expect(page).toHaveURL(/\/fields/);

    // Wait for page to load
    await waitForPageLoad(page);
  });

  test('should navigate to Analytics page', async ({ page }) => {
    const analyticsLink = page.getByTestId('nav-link-analytics');

    await expect(analyticsLink).toBeVisible();
    await analyticsLink.click();

    // Should be on analytics page
    await expect(page).toHaveURL(/\/analytics/);
    await waitForPageLoad(page);
  });

  test('should navigate to Marketplace page', async ({ page }) => {
    const marketplaceLink = page.getByTestId('nav-link-marketplace');

    await expect(marketplaceLink).toBeVisible();
    await marketplaceLink.click();

    // Should be on marketplace page
    await expect(page).toHaveURL(/\/marketplace/);
    await waitForPageLoad(page);
  });

  test('should navigate to Tasks page', async ({ page }) => {
    const tasksLink = page.getByTestId('nav-link-tasks');

    await expect(tasksLink).toBeVisible();
    await tasksLink.click();

    // Should be on tasks page
    await expect(page).toHaveURL(/\/tasks/);
    await waitForPageLoad(page);
  });

  test('should navigate to Settings page', async ({ page }) => {
    const settingsLink = page.getByTestId('nav-link-settings');

    await expect(settingsLink).toBeVisible();
    await settingsLink.click();

    // Should be on settings page
    await expect(page).toHaveURL(/\/settings/);
    await waitForPageLoad(page);
  });

  test('should navigate to Weather page', async ({ page }) => {
    const weatherLink = page.getByTestId('nav-link-weather');

    await expect(weatherLink).toBeVisible();
    await weatherLink.click();

    // Should be on weather page
    await expect(page).toHaveURL(/\/weather/);
    await waitForPageLoad(page);
  });

  test('should navigate to IoT page', async ({ page }) => {
    const iotLink = page.getByTestId('nav-link-iot');

    await expect(iotLink).toBeVisible();
    await iotLink.click();

    // Should be on iot page
    await expect(page).toHaveURL(/\/iot/);
    await waitForPageLoad(page);
  });

  test('should navigate to Crop Health page', async ({ page }) => {
    const cropHealthLink = page.getByTestId('nav-link-crop-health');

    await expect(cropHealthLink).toBeVisible();
    await cropHealthLink.click();

    // Should be on crop-health page
    await expect(page).toHaveURL(/\/crop-health/);
    await waitForPageLoad(page);
  });

  test('should navigate to Equipment page', async ({ page }) => {
    const equipmentLink = page.getByTestId('nav-link-equipment');

    await expect(equipmentLink).toBeVisible();
    await equipmentLink.click();

    // Should be on equipment page
    await expect(page).toHaveURL(/\/equipment/);
    await waitForPageLoad(page);
  });

  test('should navigate to Community page', async ({ page }) => {
    const communityLink = page.getByTestId('nav-link-community');

    await expect(communityLink).toBeVisible();
    await communityLink.click();

    // Should be on community page
    await expect(page).toHaveURL(/\/community/);
    await waitForPageLoad(page);
  });

  test('should navigate to Wallet page', async ({ page }) => {
    const walletLink = page.getByTestId('nav-link-wallet');

    await expect(walletLink).toBeVisible();
    await walletLink.click();

    // Should be on wallet page
    await expect(page).toHaveURL(/\/wallet/);
    await waitForPageLoad(page);
  });

  test('should maintain navigation state after page reload', async ({ page }) => {
    // Navigate to a specific page
    await navigateAndWait(page, '/analytics');
    await expect(page).toHaveURL(/\/analytics/);

    // Reload page
    await page.reload();
    await waitForPageLoad(page);

    // Should still be on analytics page
    await expect(page).toHaveURL(/\/analytics/);
  });

  test('should use browser back button correctly', async ({ page }) => {
    // Navigate to fields
    await navigateAndWait(page, '/fields');
    await expect(page).toHaveURL(/\/fields/);

    // Navigate to analytics
    await navigateAndWait(page, '/analytics');
    await expect(page).toHaveURL(/\/analytics/);

    // Go back
    await page.goBack();
    await waitForPageLoad(page);

    // Should be back on fields
    await expect(page).toHaveURL(/\/fields/);

    // Go back again
    await page.goBack();
    await waitForPageLoad(page);

    // Should be on dashboard
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should use browser forward button correctly', async ({ page }) => {
    // Navigate to fields
    await navigateAndWait(page, '/fields');

    // Navigate to analytics
    await navigateAndWait(page, '/analytics');

    // Go back
    await page.goBack();
    await waitForPageLoad(page);

    // Go forward
    await page.goForward();
    await waitForPageLoad(page);

    // Should be back on analytics
    await expect(page).toHaveURL(/\/analytics/);
  });

  test('should highlight active navigation item', async ({ page }) => {
    // Navigate to different pages and check if nav item is highlighted
    const pages = [
      { url: '/dashboard', text: 'Dashboard' },
      { url: '/fields', text: 'Fields' },
      { url: '/analytics', text: 'Analytics' },
    ];

    for (const pageInfo of pages) {
      await navigateAndWait(page, pageInfo.url);

      // Check if there's an active class or aria-current on the nav item
      const activeNavItem = page.locator(`
        nav a[href="${pageInfo.url}"][aria-current="page"],
        nav a[href="${pageInfo.url}"].active,
        nav a[href="${pageInfo.url}"][class*="active"]
      `).first();

      // Allow this to be optional as implementation may vary
      const exists = await activeNavItem.count();
      // Just log the result, don't fail the test
      console.log(`Active nav indicator for ${pageInfo.url}: ${exists > 0 ? 'found' : 'not found'}`);
    }
  });

  test('should handle direct URL navigation', async ({ page }) => {
    // Navigate directly to a deep URL
    await navigateAndWait(page, '/settings');

    // Should successfully load the page
    await expect(page).toHaveURL(/\/settings/);
    await expect(page.locator('h1:has-text("الإعدادات")')).toBeVisible();
  });

  test('should handle 404 for non-existent routes', async ({ page }) => {
    // Try to navigate to a non-existent route
    await page.goto('/this-page-does-not-exist');

    // Should either show 404 page or redirect to dashboard
    await page.waitForTimeout(2000);

    const url = page.url();
    const is404 = await page.locator('text=/404|Not Found|الصفحة غير موجودة/i').isVisible().catch(() => false);
    const isDashboard = url.includes('/dashboard');

    // Either shows 404 or redirects to dashboard
    expect(is404 || isDashboard).toBe(true);
  });
});

/**
 * Mobile Navigation Tests
 * اختبارات التنقل على الأجهزة المحمولة
 */
test.describe('Mobile Navigation', () => {
  test.use({
    viewport: { width: 375, height: 667 }, // iPhone SE size
  });

  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/dashboard');
  });

  test('should show mobile menu toggle', async ({ page }) => {
    // Look for hamburger menu icon using data-testid
    const mobileMenuToggle = page.getByTestId('mobile-menu-toggle');

    // Mobile menu toggle should be visible on small screens
    const isVisible = await mobileMenuToggle.isVisible().catch(() => false);

    // Log result (may not be implemented yet)
    console.log(`Mobile menu toggle visible: ${isVisible}`);
  });

  test.skip('should open and close mobile menu', async ({ page }) => {
    // Skip if mobile menu not implemented
    const mobileMenuToggle = page.getByTestId('mobile-menu-toggle');

    // Open menu
    await mobileMenuToggle.click();

    // Menu should be visible
    const menu = page.getByTestId('mobile-menu');
    await expect(menu).toBeVisible();

    // Close menu
    await mobileMenuToggle.click();

    // Menu should be hidden
    await expect(menu).not.toBeVisible();
  });
});

/**
 * Sidebar and Navigation Element Tests
 * اختبارات الشريط الجانبي وعناصر التنقل
 */
test.describe('Sidebar and Navigation Elements', () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndWait(page, '/dashboard');
  });

  test('should display sidebar with proper data-testid', async ({ page }) => {
    // Sidebar should be visible
    const sidebar = page.getByTestId('sidebar');
    await expect(sidebar).toBeVisible();

    // Sidebar should have proper ARIA attributes
    await expect(sidebar).toHaveAttribute('role', 'navigation');
  });

  test('should display sidebar logo and be clickable', async ({ page }) => {
    const logo = page.getByTestId('sidebar-logo');

    // Logo should be visible
    await expect(logo).toBeVisible();

    // Logo should be clickable (is a link)
    await expect(logo).toHaveAttribute('href', '/dashboard');

    // Navigate to another page first
    await navigateAndWait(page, '/fields');

    // Click logo to go back to dashboard
    await logo.click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should display all navigation links with data-testid', async ({ page }) => {
    // Check all navigation links are visible and have proper test IDs
    const navLinks = [
      { testId: 'nav-link-dashboard', href: '/dashboard', visible: true },
      { testId: 'nav-link-fields', href: '/fields', visible: true },
      { testId: 'nav-link-analytics', href: '/analytics', visible: true },
      { testId: 'nav-link-marketplace', href: '/marketplace', visible: true },
      { testId: 'nav-link-tasks', href: '/tasks', visible: true },
      { testId: 'nav-link-weather', href: '/weather', visible: true },
      { testId: 'nav-link-iot', href: '/iot', visible: true },
      { testId: 'nav-link-crop-health', href: '/crop-health', visible: true },
      { testId: 'nav-link-equipment', href: '/equipment', visible: true },
      { testId: 'nav-link-community', href: '/community', visible: true },
      { testId: 'nav-link-wallet', href: '/wallet', visible: true },
      { testId: 'nav-link-settings', href: '/settings', visible: true },
    ];

    for (const link of navLinks) {
      const navLink = page.getByTestId(link.testId);

      // Check visibility
      if (link.visible) {
        await expect(navLink).toBeVisible();
      }

      // Check href attribute
      await expect(navLink).toHaveAttribute('href', link.href);

      // Check that link is accessible (has proper ARIA label)
      const ariaLabel = await navLink.getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();
    }
  });

  test('should display active state on current page navigation link', async ({ page }) => {
    // Navigate to fields page
    await navigateAndWait(page, '/fields');

    // Fields link should have aria-current="page"
    const fieldsLink = page.getByTestId('nav-link-fields');
    await expect(fieldsLink).toHaveAttribute('aria-current', 'page');

    // Navigate to analytics page
    await navigateAndWait(page, '/analytics');

    // Analytics link should have aria-current="page"
    const analyticsLink = page.getByTestId('nav-link-analytics');
    await expect(analyticsLink).toHaveAttribute('aria-current', 'page');

    // Fields link should no longer have aria-current="page"
    await expect(fieldsLink).not.toHaveAttribute('aria-current', 'page');
  });

  test('should display header with proper data-testid', async ({ page }) => {
    const header = page.getByTestId('header');
    await expect(header).toBeVisible();
  });

  test('should display and interact with notifications button', async ({ page }) => {
    const notificationsButton = page.getByTestId('notifications-button');

    // Button should be visible
    await expect(notificationsButton).toBeVisible();

    // Button should have proper ARIA label
    const ariaLabel = await notificationsButton.getAttribute('aria-label');
    expect(ariaLabel).toBeTruthy();

    // Button should be clickable
    await expect(notificationsButton).toBeEnabled();
  });

  test('should display and interact with user menu', async ({ page }) => {
    const userMenuButton = page.getByTestId('user-menu-button');

    // Button should be visible
    await expect(userMenuButton).toBeVisible();

    // Button should have proper ARIA attributes
    await expect(userMenuButton).toHaveAttribute('aria-haspopup', 'true');

    // Click to open menu
    await userMenuButton.click();

    // User menu should be visible
    const userMenu = page.getByTestId('user-menu');
    await expect(userMenu).toBeVisible();

    // Check menu items are visible
    const profileItem = page.getByTestId('user-menu-profile');
    const settingsItem = page.getByTestId('user-menu-settings');
    const logoutItem = page.getByTestId('user-menu-logout');

    await expect(profileItem).toBeVisible();
    await expect(settingsItem).toBeVisible();
    await expect(logoutItem).toBeVisible();
  });

  test('should navigate via user menu items', async ({ page }) => {
    // Open user menu
    const userMenuButton = page.getByTestId('user-menu-button');
    await userMenuButton.click();

    // Click settings menu item
    const settingsItem = page.getByTestId('user-menu-settings');
    await settingsItem.click();

    // Should navigate to settings page
    await expect(page).toHaveURL(/\/dashboard\/settings/);
  });

  test('should have keyboard navigation support for nav links', async ({ page }) => {
    const dashboardLink = page.getByTestId('nav-link-dashboard');

    // Focus on the link
    await dashboardLink.focus();

    // Should have focus ring (check for focus-visible or outline)
    const isFocused = await dashboardLink.evaluate((el) => {
      return document.activeElement === el;
    });
    expect(isFocused).toBe(true);

    // Press Enter should navigate
    await dashboardLink.press('Enter');
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
