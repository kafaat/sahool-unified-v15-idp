import { Page, expect } from '@playwright/test';

/**
 * Authentication Helper Functions
 * دوال مساعدة للمصادقة
 */

export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Default test user credentials
 * بيانات المستخدم الافتراضية للاختبار
 */
export const TEST_USER: LoginCredentials = {
  email: process.env.TEST_USER_EMAIL || 'test@sahool.com',
  password: process.env.TEST_USER_PASSWORD || 'Test@123456',
};

/**
 * Login to the application
 * تسجيل الدخول إلى التطبيق
 */
export async function login(page: Page, credentials: LoginCredentials = TEST_USER) {
  // Navigate to login page
  await page.goto('/login');

  // Wait for page to load
  await page.waitForLoadState('networkidle');

  // Fill in credentials
  await page.fill('input[type="email"]', credentials.email);
  await page.fill('input[type="password"]', credentials.password);

  // Submit form
  await page.click('button[type="submit"]');

  // Wait for navigation to dashboard
  await page.waitForURL('**/dashboard', { timeout: 15000 });

  // Verify successful login
  await expect(page).toHaveURL(/\/dashboard/);
}

/**
 * Logout from the application
 * تسجيل الخروج من التطبيق
 */
export async function logout(page: Page) {
  // Look for logout button or user menu
  // This may need adjustment based on actual UI structure
  const userMenuButton = page.locator('[data-testid="user-menu"], [aria-label*="menu"], button:has-text("Settings")').first();

  if (await userMenuButton.isVisible()) {
    await userMenuButton.click();

    // Wait for dropdown menu
    await page.waitForTimeout(500);

    // Click logout button
    const logoutButton = page.locator('[data-testid="logout"], button:has-text("Logout"), button:has-text("تسجيل الخروج")').first();
    await logoutButton.click();
  }

  // Wait for redirect to login page
  await page.waitForURL('**/login', { timeout: 10000 });

  // Verify we're on login page
  await expect(page).toHaveURL(/\/login/);
}

/**
 * Check if user is logged in
 * التحقق من تسجيل دخول المستخدم
 */
export async function isLoggedIn(page: Page): Promise<boolean> {
  try {
    // Check if we can access dashboard
    await page.goto('/dashboard', { waitUntil: 'networkidle', timeout: 5000 });
    return page.url().includes('/dashboard');
  } catch {
    return false;
  }
}

/**
 * Setup authenticated state for tests
 * إعداد حالة المصادقة للاختبارات
 */
export async function setupAuthenticatedState(page: Page) {
  const loggedIn = await isLoggedIn(page);

  if (!loggedIn) {
    await login(page);
  }
}

/**
 * Save authentication state to storage
 * حفظ حالة المصادقة في التخزين
 */
export async function saveAuthState(page: Page, path: string) {
  await page.context().storageState({ path });
}

/**
 * Clear authentication cookies and storage
 * مسح cookies والتخزين
 */
export async function clearAuth(page: Page) {
  await page.context().clearCookies();
  // Only clear storage if we're on a valid page (not about:blank)
  try {
    const url = page.url();
    if (url && url !== 'about:blank') {
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
    }
  } catch {
    // Ignore storage errors on restricted pages
  }
}
