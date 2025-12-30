import { test as base, expect } from '@playwright/test';
import { login, logout, TEST_USER, LoginCredentials } from '../helpers/auth.helpers';
import { waitForPageLoad } from '../helpers/page.helpers';

/**
 * Custom Test Fixtures
 * إعدادات الاختبار المخصصة
 */

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
   * Authenticated page fixture
   * Automatically logs in before each test that uses this fixture
   * إعداد الصفحة المصادقة
   * تسجيل دخول تلقائي قبل كل اختبار يستخدم هذا الإعداد
   */
  authenticatedPage: async ({ page }, use) => {
    // Login before test
    await login(page);

    // Wait for page to be ready
    await waitForPageLoad(page);

    // Run the test
    await use();

    // Cleanup: logout after test (optional)
    try {
      await logout(page);
    } catch (error) {
      // Ignore logout errors in cleanup
      console.log('Logout cleanup failed:', error);
    }
  },
});

/**
 * Re-export expect for convenience
 * إعادة تصدير expect للسهولة
 */
export { expect };
