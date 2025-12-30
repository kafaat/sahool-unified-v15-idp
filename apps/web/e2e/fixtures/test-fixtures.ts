import { test as base, expect, Page } from '@playwright/test';
import { login, logout, TEST_USER, LoginCredentials, isLoggedIn } from '../helpers/auth.helpers';
import { waitForPageLoad, NAVIGATION_TIMEOUT, takeTimestampedScreenshot } from '../helpers/page.helpers';

/**
 * Custom Test Fixtures
 * إعدادات الاختبار المخصصة
 */

/**
 * Authentication state for testing
 * حالة المصادقة للاختبار
 */
export interface AuthState {
  isAuthenticated: boolean;
  user?: LoginCredentials;
  timestamp?: number;
}

interface CustomFixtures {
  /**
   * Authenticated page - automatically logs in before test
   * صفحة مصادقة - تسجيل دخول تلقائي قبل الاختبار
   */
  authenticatedPage: void;

  /**
   * Test user credentials
   * بيانات اعتماد المستخدم الاختباري
   */
  testUser: LoginCredentials;

  /**
   * Mock authenticated state - sets up auth without actual login
   * حالة مصادقة وهمية - إعداد المصادقة بدون تسجيل دخول فعلي
   */
  mockAuthPage: Page;

  /**
   * Auth state storage path
   * مسار تخزين حالة المصادقة
   */
  authStatePath: string;
}

/**
 * Extend base test with custom fixtures
 * توسيع الاختبار الأساسي بإعدادات مخصصة
 */
export const test = base.extend<CustomFixtures>({
  /**
   * Test user fixture
   * إعداد المستخدم الاختباري
   */
  testUser: async ({}, use) => {
    await use(TEST_USER);
  },

  /**
   * Auth state storage path fixture
   * إعداد مسار تخزين حالة المصادقة
   */
  authStatePath: async ({}, use, testInfo) => {
    const path = `test-results/auth-state-${testInfo.workerIndex}.json`;
    await use(path);
  },

  /**
   * Authenticated page fixture
   * Automatically logs in before each test that uses this fixture
   * إعداد الصفحة المصادقة
   * تسجيل دخول تلقائي قبل كل اختبار يستخدم هذا الإعداد
   */
  authenticatedPage: async ({ page }, use, testInfo) => {
    console.log(`[${testInfo.title}] Setting up authenticated page...`);
    const startTime = Date.now();

    try {
      // Validate page is ready
      if (!page) {
        throw new Error('Page object is not available');
      }

      // Check if already logged in (from previous tests)
      const alreadyLoggedIn = await isLoggedIn(page);

      if (!alreadyLoggedIn) {
        console.log(`[${testInfo.title}] Logging in...`);

        // Login with timeout and retry
        try {
          await login(page);
        } catch (loginError) {
          // Take screenshot on login failure
          await takeTimestampedScreenshot(page, `login-failure-${testInfo.title}`).catch(() => {});
          throw new Error(
            `Login failed for test "${testInfo.title}". Error: ${loginError instanceof Error ? loginError.message : 'Unknown error'}`
          );
        }

        // Wait for page to be fully ready
        try {
          await waitForPageLoad(page, NAVIGATION_TIMEOUT);
        } catch (loadError) {
          await takeTimestampedScreenshot(page, `page-load-failure-${testInfo.title}`).catch(() => {});
          throw new Error(
            `Page load failed after login for test "${testInfo.title}". Error: ${loadError instanceof Error ? loadError.message : 'Unknown error'}`
          );
        }
      } else {
        console.log(`[${testInfo.title}] Already logged in, skipping login`);
      }

      // Validate authentication state
      const isAuthenticated = await isLoggedIn(page);
      if (!isAuthenticated) {
        await takeTimestampedScreenshot(page, `auth-validation-failure-${testInfo.title}`).catch(() => {});
        throw new Error(
          `Authentication validation failed for test "${testInfo.title}". User is not logged in after login attempt.`
        );
      }

      const setupTime = Date.now() - startTime;
      console.log(`[${testInfo.title}] Authentication setup completed in ${setupTime}ms`);

      // Run the test
      await use();

      console.log(`[${testInfo.title}] Test completed, cleaning up...`);

    } catch (error) {
      // Log error and re-throw
      console.error(`[${testInfo.title}] Authentication fixture error:`, error);
      throw error;
    } finally {
      // Cleanup: logout after test (best effort, don't fail test if logout fails)
      try {
        const stillLoggedIn = await isLoggedIn(page);
        if (stillLoggedIn) {
          await logout(page);
          console.log(`[${testInfo.title}] Logged out successfully`);
        }
      } catch (logoutError) {
        // Log but don't fail the test
        console.warn(
          `[${testInfo.title}] Logout cleanup failed (non-critical):`,
          logoutError instanceof Error ? logoutError.message : 'Unknown error'
        );
      }
    }
  },

  /**
   * Mock authenticated page fixture
   * Sets up authentication state without going through login flow
   * Useful for faster tests that don't need to test the login flow itself
   * إعداد صفحة مصادقة وهمية
   * إعداد حالة المصادقة بدون المرور بعملية تسجيل الدخول
   */
  mockAuthPage: async ({ page, context, authStatePath }, use, testInfo) => {
    console.log(`[${testInfo.title}] Setting up mock authentication...`);

    try {
      // Set up mock authentication tokens/cookies
      // This is a placeholder - adjust based on your actual auth mechanism
      await context.addCookies([
        {
          name: 'auth-token',
          value: 'mock-test-token',
          domain: 'localhost',
          path: '/',
          httpOnly: true,
          secure: false,
          sameSite: 'Lax'
        }
      ]);

      // Set localStorage items if needed
      await page.goto('/');
      await page.evaluate((user) => {
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('isAuthenticated', 'true');
      }, TEST_USER);

      // Navigate to dashboard to verify mock auth works
      await page.goto('/dashboard', { waitUntil: 'domcontentloaded', timeout: NAVIGATION_TIMEOUT });
      await waitForPageLoad(page);

      console.log(`[${testInfo.title}] Mock authentication setup completed`);

      // Run the test
      await use(page);

    } catch (error) {
      console.error(`[${testInfo.title}] Mock auth fixture error:`, error);
      await takeTimestampedScreenshot(page, `mock-auth-failure-${testInfo.title}`).catch(() => {});
      throw error;
    } finally {
      // Cleanup: clear mock state
      try {
        await context.clearCookies();
        await page.evaluate(() => {
          localStorage.clear();
          sessionStorage.clear();
        });
        console.log(`[${testInfo.title}] Mock auth state cleared`);
      } catch (cleanupError) {
        console.warn(`[${testInfo.title}] Mock auth cleanup failed:`, cleanupError);
      }
    }
  },
});

/**
 * Re-export expect for convenience
 * إعادة تصدير expect للسهولة
 */
export { expect };
