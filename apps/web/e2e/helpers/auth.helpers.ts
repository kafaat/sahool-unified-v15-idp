import { Page, expect } from '@playwright/test';
import { NAVIGATION_TIMEOUT, DEFAULT_TIMEOUT, ELEMENT_TIMEOUT, retryWithBackoff } from './page.helpers';

/**
 * Authentication Helper Functions
 * دوال مساعدة للمصادقة
 */

export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Login options
 * خيارات تسجيل الدخول
 */
export interface LoginOptions {
  timeout?: number;
  maxRetries?: number;
  validateAuth?: boolean;
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
export async function login(
  page: Page,
  credentials: LoginCredentials = TEST_USER,
  options: LoginOptions = {}
): Promise<void> {
  const {
    timeout = NAVIGATION_TIMEOUT,
    maxRetries = 1,
    validateAuth = true
  } = options;

  await retryWithBackoff(async () => {
    try {
      console.log(`Attempting login for user: ${credentials.email}`);

      // Navigate to login page
      try {
        await page.goto('/login', { timeout, waitUntil: 'domcontentloaded' });
      } catch (gotoError) {
        throw new Error(
          `Failed to navigate to login page. Error: ${gotoError instanceof Error ? gotoError.message : 'Unknown error'}`
        );
      }

      // Wait for page to load
      try {
        await page.waitForLoadState('networkidle', { timeout });
      } catch (loadError) {
        console.warn('Network idle timeout, continuing with login attempt...');
      }

      // Wait for login form to be visible
      try {
        await page.waitForSelector('[data-testid="login-email-input"]', {
          state: 'visible',
          timeout: ELEMENT_TIMEOUT
        });
      } catch (selectorError) {
        throw new Error(
          `Login form not found. The page may not have loaded correctly. Error: ${selectorError instanceof Error ? selectorError.message : 'Unknown error'}`
        );
      }

      // Fill in credentials using data-testid selectors
      try {
        await page.fill('[data-testid="login-email-input"]', credentials.email, {
          timeout: DEFAULT_TIMEOUT
        });
        await page.fill('[data-testid="login-password-input"]', credentials.password, {
          timeout: DEFAULT_TIMEOUT
        });
      } catch (fillError) {
        throw new Error(
          `Failed to fill login form. Error: ${fillError instanceof Error ? fillError.message : 'Unknown error'}`
        );
      }

      // Submit form
      try {
        await page.click('[data-testid="login-submit-button"]', { timeout: DEFAULT_TIMEOUT });
      } catch (clickError) {
        throw new Error(
          `Failed to click login button. Error: ${clickError instanceof Error ? clickError.message : 'Unknown error'}`
        );
      }

      // Wait for navigation to dashboard
      try {
        await page.waitForURL('**/dashboard', { timeout });
      } catch (navError) {
        const currentUrl = page.url();
        throw new Error(
          `Failed to navigate to dashboard after login. Current URL: ${currentUrl}. Error: ${navError instanceof Error ? navError.message : 'Unknown error'}`
        );
      }

      // Verify successful login
      try {
        await expect(page).toHaveURL(/\/dashboard/, { timeout: ELEMENT_TIMEOUT });
      } catch (verifyError) {
        const currentUrl = page.url();
        throw new Error(
          `Login verification failed. Expected dashboard URL but got: ${currentUrl}`
        );
      }

      // Optional: Validate authentication state
      if (validateAuth) {
        const authenticated = await isLoggedIn(page);
        if (!authenticated) {
          throw new Error('Login appeared successful but authentication validation failed');
        }
      }

      console.log('Login successful');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }, { maxRetries, retryDelay: 2000 });
}

/**
 * Logout from the application
 * تسجيل الخروج من التطبيق
 */
export async function logout(page: Page, timeout: number = NAVIGATION_TIMEOUT): Promise<void> {
  try {
    console.log('Attempting to logout...');

    // Look for logout button or user menu
    const userMenuSelectors = [
      '[data-testid="user-menu"]',
      '[aria-label*="menu"]',
      'button:has-text("Settings")',
      '[data-testid="user-avatar"]'
    ];

    let menuFound = false;
    for (const selector of userMenuSelectors) {
      try {
        const userMenuButton = page.locator(selector).first();
        const isVisible = await userMenuButton.isVisible({ timeout: ELEMENT_TIMEOUT / 2 });

        if (isVisible) {
          await userMenuButton.click({ timeout: DEFAULT_TIMEOUT });
          menuFound = true;
          console.log(`User menu opened using selector: ${selector}`);
          break;
        }
      } catch {
        // Try next selector
        continue;
      }
    }

    if (!menuFound) {
      throw new Error('Could not find user menu button to initiate logout');
    }

    // Wait for dropdown menu to appear
    const logoutSelectors = [
      '[data-testid="logout"]',
      '[data-testid="logout-button"]',
      'button:has-text("Logout")',
      'button:has-text("تسجيل الخروج")',
      'a:has-text("Logout")',
      'a:has-text("تسجيل الخروج")'
    ];

    let logoutClicked = false;
    for (const selector of logoutSelectors) {
      try {
        const logoutButton = page.locator(selector).first();
        await logoutButton.waitFor({ state: 'visible', timeout: ELEMENT_TIMEOUT });
        await logoutButton.click({ timeout: DEFAULT_TIMEOUT });
        logoutClicked = true;
        console.log(`Logout button clicked using selector: ${selector}`);
        break;
      } catch {
        // Try next selector
        continue;
      }
    }

    if (!logoutClicked) {
      throw new Error('Could not find logout button in menu');
    }

    // Wait for redirect to login page
    try {
      await page.waitForURL('**/login', { timeout });
    } catch (navError) {
      const currentUrl = page.url();
      throw new Error(
        `Failed to navigate to login page after logout. Current URL: ${currentUrl}. Error: ${navError instanceof Error ? navError.message : 'Unknown error'}`
      );
    }

    // Verify we're on login page
    try {
      await expect(page).toHaveURL(/\/login/, { timeout: ELEMENT_TIMEOUT });
      console.log('Logout successful');
    } catch (verifyError) {
      const currentUrl = page.url();
      throw new Error(
        `Logout verification failed. Expected login URL but got: ${currentUrl}`
      );
    }
  } catch (error) {
    console.error('Logout failed:', error);
    throw new Error(
      `Logout operation failed. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Check if user is logged in
 * التحقق من تسجيل دخول المستخدم
 */
export async function isLoggedIn(page: Page): Promise<boolean> {
  try {
    const currentUrl = page.url();

    // If already on dashboard, user is logged in
    if (currentUrl.includes('/dashboard')) {
      // Verify dashboard content is loaded
      const hasDashboardContent = await page.locator('main, [role="main"], #app').count() > 0;
      return hasDashboardContent;
    }

    // Try to navigate to dashboard
    const response = await page.goto('/dashboard', {
      waitUntil: 'domcontentloaded',
      timeout: ELEMENT_TIMEOUT
    });

    // If redirected to login, user is not logged in
    const newUrl = page.url();
    if (newUrl.includes('/login') || newUrl.includes('/auth')) {
      return false;
    }

    // If we're on dashboard and got a successful response, user is logged in
    if (newUrl.includes('/dashboard')) {
      return response ? response.ok() : true;
    }

    return false;
  } catch (error) {
    console.warn('isLoggedIn check failed:', error);
    return false;
  }
}

/**
 * Setup authenticated state for tests
 * إعداد حالة المصادقة للاختبارات
 */
export async function setupAuthenticatedState(
  page: Page,
  options: LoginOptions = {}
): Promise<void> {
  try {
    console.log('Checking authentication state...');
    const loggedIn = await isLoggedIn(page);

    if (!loggedIn) {
      console.log('User not logged in, performing login...');
      await login(page, TEST_USER, options);
    } else {
      console.log('User already logged in, skipping login');
    }
  } catch (error) {
    throw new Error(
      `Failed to setup authenticated state. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Save authentication state to storage
 * حفظ حالة المصادقة في التخزين
 */
export async function saveAuthState(page: Page, path: string): Promise<void> {
  try {
    await page.context().storageState({ path });
    console.log(`Authentication state saved to: ${path}`);
  } catch (error) {
    throw new Error(
      `Failed to save authentication state to ${path}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Clear authentication cookies and storage
 * مسح cookies والتخزين
 */
export async function clearAuth(page: Page): Promise<void> {
  try {
    console.log('Clearing authentication state...');

    // Clear cookies
    await page.context().clearCookies();

    // Only clear storage if we're on a valid page (not about:blank)
    try {
      const url = page.url();
      if (url && url !== 'about:blank' && !url.startsWith('data:')) {
        await page.evaluate(() => {
          try {
            localStorage.clear();
            sessionStorage.clear();
          } catch (e) {
            console.warn('Storage clear failed:', e);
          }
        });
      }
    } catch (storageError) {
      console.warn('Failed to clear storage:', storageError);
      // Don't throw - this is best effort
    }

    console.log('Authentication state cleared');
  } catch (error) {
    console.error('Failed to clear authentication:', error);
    throw new Error(
      `Failed to clear authentication. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Wait for authentication to complete (useful for SSO flows)
 * الانتظار حتى تكتمل المصادقة (مفيد لتدفقات SSO)
 */
export async function waitForAuthComplete(
  page: Page,
  timeout: number = NAVIGATION_TIMEOUT
): Promise<void> {
  try {
    // Wait for either dashboard or login page
    await Promise.race([
      page.waitForURL('**/dashboard', { timeout }),
      page.waitForURL('**/login', { timeout })
    ]);

    const currentUrl = page.url();
    console.log(`Authentication flow completed. Current URL: ${currentUrl}`);
  } catch (error) {
    const currentUrl = page.url();
    throw new Error(
      `Authentication flow did not complete within ${timeout}ms. Current URL: ${currentUrl}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}
