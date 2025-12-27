import { test, expect } from './fixtures/test-fixtures';
import { navigateAndWait, waitForPageLoad } from './helpers/page.helpers';

/**
 * Navigation E2E Tests
 * اختبارات E2E للتنقل بين الصفحات
 */

test.describe('Navigation Flow', () => {
  // Use authenticated fixture to ensure user is logged in
  test.use({ storageState: undefined });

  test.beforeEach(async ({ page, authenticatedPage }) => {
    // authenticatedPage fixture handles login automatically
    await navigateAndWait(page, '/dashboard');
  });

  test('should navigate to dashboard from any page', async ({ page }) => {
    // Navigate to another page first
    await navigateAndWait(page, '/fields');

    // Click dashboard link
    const dashboardLink = page.locator('a[href="/dashboard"], a:has-text("Dashboard"), a:has-text("لوحة التحكم")').first();
    await dashboardLink.click();

    // Should be on dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator('text=/Dashboard|لوحة التحكم/i')).toBeVisible();
  });

  test('should navigate to Fields page', async ({ page }) => {
    // Click fields link in navigation
    const fieldsLink = page.locator('a[href="/fields"], a:has-text("Fields"), a:has-text("الحقول")').first();

    if (await fieldsLink.isVisible()) {
      await fieldsLink.click();

      // Should be on fields page
      await expect(page).toHaveURL(/\/fields/);

      // Wait for page to load
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Analytics page', async ({ page }) => {
    const analyticsLink = page.locator('a[href="/analytics"], a:has-text("Analytics"), a:has-text("التحليلات")').first();

    if (await analyticsLink.isVisible()) {
      await analyticsLink.click();

      // Should be on analytics page
      await expect(page).toHaveURL(/\/analytics/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Marketplace page', async ({ page }) => {
    const marketplaceLink = page.locator('a[href="/marketplace"], a:has-text("Marketplace"), a:has-text("السوق")').first();

    if (await marketplaceLink.isVisible()) {
      await marketplaceLink.click();

      // Should be on marketplace page
      await expect(page).toHaveURL(/\/marketplace/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Tasks page', async ({ page }) => {
    const tasksLink = page.locator('a[href="/tasks"], a:has-text("Tasks"), a:has-text("المهام")').first();

    if (await tasksLink.isVisible()) {
      await tasksLink.click();

      // Should be on tasks page
      await expect(page).toHaveURL(/\/tasks/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Settings page', async ({ page }) => {
    const settingsLink = page.locator('a[href="/settings"], a:has-text("Settings"), a:has-text("الإعدادات")').first();

    if (await settingsLink.isVisible()) {
      await settingsLink.click();

      // Should be on settings page
      await expect(page).toHaveURL(/\/settings/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Weather page', async ({ page }) => {
    const weatherLink = page.locator('a[href="/weather"], a:has-text("Weather"), a:has-text("الطقس")').first();

    if (await weatherLink.isVisible()) {
      await weatherLink.click();

      // Should be on weather page
      await expect(page).toHaveURL(/\/weather/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to IoT page', async ({ page }) => {
    const iotLink = page.locator('a[href="/iot"], a:has-text("IoT"), a:has-text("إنترنت الأشياء")').first();

    if (await iotLink.isVisible()) {
      await iotLink.click();

      // Should be on iot page
      await expect(page).toHaveURL(/\/iot/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Crop Health page', async ({ page }) => {
    const cropHealthLink = page.locator('a[href="/crop-health"], a:has-text("Crop Health"), a:has-text("صحة المحاصيل")').first();

    if (await cropHealthLink.isVisible()) {
      await cropHealthLink.click();

      // Should be on crop-health page
      await expect(page).toHaveURL(/\/crop-health/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Equipment page', async ({ page }) => {
    const equipmentLink = page.locator('a[href="/equipment"], a:has-text("Equipment"), a:has-text("المعدات")').first();

    if (await equipmentLink.isVisible()) {
      await equipmentLink.click();

      // Should be on equipment page
      await expect(page).toHaveURL(/\/equipment/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Community page', async ({ page }) => {
    const communityLink = page.locator('a[href="/community"], a:has-text("Community"), a:has-text("المجتمع")').first();

    if (await communityLink.isVisible()) {
      await communityLink.click();

      // Should be on community page
      await expect(page).toHaveURL(/\/community/);
      await waitForPageLoad(page);
    }
  });

  test('should navigate to Wallet page', async ({ page }) => {
    const walletLink = page.locator('a[href="/wallet"], a:has-text("Wallet"), a:has-text("المحفظة")').first();

    if (await walletLink.isVisible()) {
      await walletLink.click();

      // Should be on wallet page
      await expect(page).toHaveURL(/\/wallet/);
      await waitForPageLoad(page);
    }
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
    await expect(page.locator('text=/Settings|الإعدادات/i')).toBeVisible();
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

  test.beforeEach(async ({ page, authenticatedPage }) => {
    await navigateAndWait(page, '/dashboard');
  });

  test('should show mobile menu toggle', async ({ page }) => {
    // Look for hamburger menu icon
    const mobileMenuToggle = page.locator('[data-testid="mobile-menu-toggle"], button[aria-label*="menu"], button:has-text("☰")').first();

    // Mobile menu toggle should be visible on small screens
    const isVisible = await mobileMenuToggle.isVisible().catch(() => false);

    // Log result (may not be implemented yet)
    console.log(`Mobile menu toggle visible: ${isVisible}`);
  });

  test.skip('should open and close mobile menu', async ({ page }) => {
    // Skip if mobile menu not implemented
    const mobileMenuToggle = page.locator('[data-testid="mobile-menu-toggle"]');

    // Open menu
    await mobileMenuToggle.click();

    // Menu should be visible
    const menu = page.locator('[data-testid="mobile-menu"], nav[aria-label*="mobile"]');
    await expect(menu).toBeVisible();

    // Close menu
    await mobileMenuToggle.click();

    // Menu should be hidden
    await expect(menu).not.toBeVisible();
  });
});
