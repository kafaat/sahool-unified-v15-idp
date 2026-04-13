import { test as base, expect } from "@playwright/test";
import {
  login,
  logout,
  TEST_USER,
  LoginCredentials,
} from "../helpers/auth.helpers";
import { waitForPageLoad } from "../helpers/page.helpers";

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
 * Mock API responses for E2E tests
 */
const mockApiResponses: Record<string, unknown> = {
  "/api/v1/auth/me": {
    success: true,
    data: {
      id: "test-user-123",
      email: "test@sahool.com",
      name: "Test User",
      name_ar: "مستخدم اختباري",
      role: "admin",
    },
  },
  "/api/v1/analytics/summary": {
    success: true,
    data: {
      totalFields: 3,
      totalArea: 13.5,
      totalYield: 45000,
      totalRevenue: 135000,
      totalCost: 67500,
      totalProfit: 67500,
      averageYieldPerHectare: 3333.33,
    },
  },
  "/api/v1/analytics/kpis": {
    success: true,
    data: [
      {
        id: "yield",
        name: "Total Yield",
        nameAr: "إجمالي الإنتاج",
        value: 45000,
        unit: "kg",
        unitAr: "كجم",
      },
      {
        id: "revenue",
        name: "Revenue",
        nameAr: "الإيرادات",
        value: 135000,
        unit: "SAR",
        unitAr: "ريال",
      },
    ],
  },
  "/api/v1/dashboard/stats": {
    success: true,
    data: {
      totalFields: 5,
      activeTasks: 12,
      pendingAlerts: 3,
      weatherStatus: "sunny",
    },
  },
  "/api/v1/fields": {
    success: true,
    data: [
      {
        id: "1",
        name: "North Field",
        nameAr: "الحقل الشمالي",
        area: 5.5,
        status: "active",
      },
      {
        id: "2",
        name: "South Field",
        nameAr: "الحقل الجنوبي",
        area: 3.2,
        status: "active",
      },
    ],
  },
  "/api/v1/tasks": {
    success: true,
    data: [
      {
        id: "1",
        title: "Irrigation",
        titleAr: "الري",
        status: "pending",
        dueDate: new Date().toISOString(),
      },
    ],
  },
  "/api/v1/weather": {
    success: true,
    data: {
      temperature: 28,
      humidity: 45,
      condition: "sunny",
      conditionAr: "مشمس",
    },
  },
};

/**
 * Extend base test with custom fixtures
 * توسيع الاختبار الأساسي بإعدادات مخصصة
 */
export const test = base.extend<CustomFixtures>({
  /**
   * Test user fixture
   * إعداد المستخدم الاختباري
   */
  // Playwright passes `use` as the fixture-resolver — same name as the
  // React 19 `use()` hook, which triggers react-hooks/rules-of-hooks.
  // This is a Playwright fixture, not a React render context, so the
  // hook rules don't apply. The rule is suppressed at the call site.
  //
  // Playwright also requires the first argument to use the destructuring
  // pattern (even when no dependencies are needed) so it can statically
  // inspect the dependency list — that's why the first arg is `{}` and
  // not a plain identifier like `_options`.
  // eslint-disable-next-line no-empty-pattern
  testUser: async ({}, use) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    await use(TEST_USER);
  },

  /**
   * Authenticated page fixture
   * Automatically logs in before each test that uses this fixture
   * إعداد الصفحة المصادقة
   * تسجيل دخول تلقائي قبل كل اختبار يستخدم هذا الإعداد
   */
  // See note above on `use` vs the React 19 `use()` hook.
  authenticatedPage: async ({ page }, use) => {
    // In CI, mock all API calls to return test data
    if (process.env.CI) {
      await page.route("**/api/**", async (route) => {
        const url = new URL(route.request().url());
        const pathname = url.pathname;

        // Find matching mock response
        const mockKey = Object.keys(mockApiResponses).find((key) =>
          pathname.includes(key),
        );

        if (mockKey) {
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(mockApiResponses[mockKey]),
          });
        } else {
          // Default success response for unknown endpoints
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true, data: [] }),
          });
        }
      });
    }

    // Login before test
    await login(page);

    // Wait for page to be ready
    await waitForPageLoad(page);

    // Run the test
    // eslint-disable-next-line react-hooks/rules-of-hooks
    await use();

    // Cleanup: logout after test (optional)
    try {
      await logout(page);
    } catch (error) {
      // Ignore logout errors in cleanup
      console.log("Logout cleanup failed:", error);
    }
  },
});

/**
 * Re-export expect for convenience
 * إعادة تصدير expect للسهولة
 */
export { expect };
