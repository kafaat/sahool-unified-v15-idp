/**
 * UX Scenarios Test Fixtures
 * إعدادات اختبار سيناريوهات تجربة المستخدم
 *
 * Custom Playwright fixtures for SAHOOL UX testing scenarios
 * إعدادات Playwright مخصصة لسيناريوهات اختبار تجربة المستخدم في سهول
 */

import { test as base, expect, Page } from "@playwright/test";
import {
  testUsers,
  loginUser,
  mockLogin,
  waitForPageLoad,
  UserCredentials,
  sampleFarms,
  sampleFields,
  sampleTasks,
  mockWeatherData,
  mockNDVIData,
  sampleCooperatives,
} from "../helpers/ux-helpers";

// ═══════════════════════════════════════════════════════════════════════════════
// Custom Fixture Types - أنواع الإعدادات المخصصة
// ═══════════════════════════════════════════════════════════════════════════════

interface UXScenarioFixtures {
  /**
   * Authenticated farmer page
   * صفحة المزارع المصادق عليه
   */
  farmerPage: Page;

  /**
   * Authenticated cooperative admin page
   * صفحة مدير التعاونية المصادق عليه
   */
  coopAdminPage: Page;

  /**
   * Test user credentials
   * بيانات اعتماد المستخدم الاختباري
   */
  farmer: UserCredentials;

  /**
   * Cooperative admin credentials
   * بيانات اعتماد مدير التعاونية
   */
  coopAdmin: UserCredentials;

  /**
   * Sample farm data
   * بيانات المزرعة النموذجية
   */
  sampleFarm: typeof sampleFarms[0];

  /**
   * Sample field data
   * بيانات الحقل النموذجية
   */
  sampleWheatField: typeof sampleFields.wheat;
  sampleDatePalmField: typeof sampleFields.datePalm;
  sampleTomatoField: typeof sampleFields.tomato;

  /**
   * Sample task data
   * بيانات المهمة النموذجية
   */
  sampleIrrigationTask: typeof sampleTasks.irrigation;
  sampleFertilizerTask: typeof sampleTasks.fertilizer;

  /**
   * Mock API responses enabled
   * تفعيل استجابات API الوهمية
   */
  mockApiEnabled: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Mock API Responses - استجابات API الوهمية
// ═══════════════════════════════════════════════════════════════════════════════

const mockApiResponses: Record<string, unknown> = {
  // Authentication - المصادقة
  "/api/v1/auth/me": {
    success: true,
    data: {
      id: "farmer-001",
      email: testUsers.farmer.email,
      name: testUsers.farmer.name,
      nameAr: testUsers.farmer.nameAr,
      role: "farmer",
    },
  },

  // Dashboard Stats - إحصائيات لوحة التحكم
  "/api/v1/dashboard/stats": {
    success: true,
    data: {
      totalFields: 5,
      totalArea: 46.0,
      activeTasks: 12,
      pendingAlerts: 3,
      weatherStatus: "sunny",
    },
  },

  // Farms - المزارع
  "/api/v1/farms": {
    success: true,
    data: sampleFarms.map((farm, idx) => ({
      id: `farm-${idx + 1}`,
      ...farm,
    })),
  },

  // Fields - الحقول
  "/api/v1/fields": {
    success: true,
    data: Object.entries(sampleFields).map(([key, field], idx) => ({
      id: `field-${idx + 1}`,
      ...field,
      ndvi: mockNDVIData.currentValue - idx * 0.05,
      healthStatus: mockNDVIData.healthStatus,
    })),
  },

  // Tasks - المهام
  "/api/v1/tasks": {
    success: true,
    data: Object.entries(sampleTasks).map(([key, task], idx) => ({
      id: `task-${idx + 1}`,
      ...task,
      status: idx === 0 ? "pending" : "in_progress",
    })),
  },

  // Weather - الطقس
  "/api/v1/weather": {
    success: true,
    data: mockWeatherData,
  },
  "/api/v1/weather/current": {
    success: true,
    data: mockWeatherData.current,
  },
  "/api/v1/weather/forecast": {
    success: true,
    data: mockWeatherData.forecast,
  },

  // NDVI - مؤشر الغطاء النباتي
  "/api/v1/ndvi": {
    success: true,
    data: mockNDVIData,
  },
  "/api/v1/vegetation": {
    success: true,
    data: {
      ndvi: mockNDVIData.currentValue,
      lai: 3.2,
      healthStatus: mockNDVIData.healthStatus,
    },
  },

  // Irrigation Recommendations - توصيات الري
  "/api/v1/irrigation/recommendations": {
    success: true,
    data: {
      fieldId: "field-1",
      recommendedAmount: 25,
      unit: "mm",
      timing: "morning",
      timingAr: "صباحاً",
      reason: "Soil moisture below threshold",
      reasonAr: "رطوبة التربة أقل من الحد الأدنى",
      urgency: "high",
    },
  },

  // Equipment - المعدات
  "/api/v1/equipment": {
    success: true,
    data: [
      {
        id: "equip-1",
        name: "John Deere Tractor",
        nameAr: "جرار جون ديير",
        type: "tractor",
        status: "available",
      },
      {
        id: "equip-2",
        name: "Center Pivot",
        nameAr: "رشاش محوري",
        type: "irrigation",
        status: "in_use",
      },
    ],
  },

  // Cooperatives - التعاونيات
  "/api/v1/cooperatives": {
    success: true,
    data: sampleCooperatives.map((coop, idx) => ({
      id: `coop-${idx + 1}`,
      ...coop,
      memberCount: 25 + idx * 10,
    })),
  },

  // Notifications - الإشعارات
  "/api/v1/notifications": {
    success: true,
    data: [
      {
        id: "notif-1",
        type: "weather_alert",
        title: "Heat Wave Warning",
        titleAr: "تحذير من موجة حر",
        body: "High temperatures expected tomorrow",
        bodyAr: "درجات حرارة مرتفعة متوقعة غداً",
        severity: "warning",
        read: false,
        createdAt: new Date().toISOString(),
      },
      {
        id: "notif-2",
        type: "irrigation_reminder",
        title: "Irrigation Due",
        titleAr: "موعد الري",
        body: "Wheat Field North needs irrigation",
        bodyAr: "حقل القمح الشمالي يحتاج للري",
        severity: "info",
        read: false,
        createdAt: new Date(Date.now() - 3600000).toISOString(),
      },
    ],
  },

  // Alerts - التنبيهات
  "/api/v1/alerts": {
    success: true,
    data: [
      {
        id: "alert-1",
        type: "pest_warning",
        severity: "high",
        title: "Aphid Detection",
        titleAr: "اكتشاف المن",
        description: "Aphid population detected in Wheat Field",
        descriptionAr: "تم اكتشاف المن في حقل القمح",
        fieldId: "field-1",
        createdAt: new Date().toISOString(),
        status: "active",
      },
    ],
  },

  // Analytics - التحليلات
  "/api/v1/analytics/summary": {
    success: true,
    data: {
      totalYield: 45000,
      averageNDVI: 0.68,
      waterUsage: 12500,
      costSavings: 15000,
    },
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// Extended Test with Custom Fixtures - الاختبار الموسع مع الإعدادات المخصصة
// ═══════════════════════════════════════════════════════════════════════════════

export const test = base.extend<UXScenarioFixtures>({
  /**
   * Farmer user credentials
   * بيانات اعتماد المزارع
   */
  farmer: async ({}, use) => {
    await use(testUsers.farmer);
  },

  /**
   * Cooperative admin credentials
   * بيانات اعتماد مدير التعاونية
   */
  coopAdmin: async ({}, use) => {
    await use(testUsers.cooperativeAdmin);
  },

  /**
   * Sample farm data fixture
   * إعداد بيانات المزرعة النموذجية
   */
  sampleFarm: async ({}, use) => {
    await use(sampleFarms[0]);
  },

  /**
   * Sample wheat field data
   * بيانات حقل القمح النموذجي
   */
  sampleWheatField: async ({}, use) => {
    await use(sampleFields.wheat);
  },

  /**
   * Sample date palm field data
   * بيانات بستان النخيل النموذجي
   */
  sampleDatePalmField: async ({}, use) => {
    await use(sampleFields.datePalm);
  },

  /**
   * Sample tomato field data
   * بيانات حقل الطماطم النموذجي
   */
  sampleTomatoField: async ({}, use) => {
    await use(sampleFields.tomato);
  },

  /**
   * Sample irrigation task
   * مهمة الري النموذجية
   */
  sampleIrrigationTask: async ({}, use) => {
    await use(sampleTasks.irrigation);
  },

  /**
   * Sample fertilizer task
   * مهمة التسميد النموذجية
   */
  sampleFertilizerTask: async ({}, use) => {
    await use(sampleTasks.fertilizer);
  },

  /**
   * Mock API enabled flag
   * علامة تفعيل API الوهمي
   */
  mockApiEnabled: async ({}, use) => {
    await use(!!process.env.CI || process.env.MOCK_API === "true");
  },

  /**
   * Authenticated farmer page
   * صفحة المزارع المصادقة
   */
  farmerPage: async ({ page, farmer }, use) => {
    // Setup API mocking in CI
    // إعداد API الوهمي في CI
    if (process.env.CI || process.env.MOCK_API === "true") {
      await page.route("**/api/**", async (route) => {
        const url = new URL(route.request().url());
        const pathname = url.pathname;

        // Find matching mock response
        const mockKey = Object.keys(mockApiResponses).find((key) =>
          pathname.includes(key)
        );

        if (mockKey) {
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(mockApiResponses[mockKey]),
          });
        } else {
          // Default success response
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true, data: [] }),
          });
        }
      });
    }

    // Login as farmer
    await loginUser(page, farmer);
    await waitForPageLoad(page);

    await use(page);
  },

  /**
   * Authenticated cooperative admin page
   * صفحة مدير التعاونية المصادقة
   */
  coopAdminPage: async ({ page, coopAdmin }, use) => {
    // Setup API mocking in CI
    if (process.env.CI || process.env.MOCK_API === "true") {
      await page.route("**/api/**", async (route) => {
        const url = new URL(route.request().url());
        const pathname = url.pathname;

        const mockKey = Object.keys(mockApiResponses).find((key) =>
          pathname.includes(key)
        );

        if (mockKey) {
          // Modify response for cooperative admin context
          let response = mockApiResponses[mockKey];
          if (pathname.includes("/auth/me")) {
            response = {
              success: true,
              data: {
                id: "coop-admin-001",
                email: testUsers.cooperativeAdmin.email,
                name: testUsers.cooperativeAdmin.name,
                nameAr: testUsers.cooperativeAdmin.nameAr,
                role: "cooperative_admin",
              },
            };
          }

          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(response),
          });
        } else {
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ success: true, data: [] }),
          });
        }
      });
    }

    // Login as cooperative admin
    await loginUser(page, coopAdmin);
    await waitForPageLoad(page);

    await use(page);
  },
});

// ═══════════════════════════════════════════════════════════════════════════════
// Re-exports - إعادة التصدير
// ═══════════════════════════════════════════════════════════════════════════════

export { expect };
export { mockApiResponses };
