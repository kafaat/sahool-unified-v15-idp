/**
 * Test Data Helpers
 * مساعدات بيانات الاختبار
 */

/**
 * Generate random test data
 * إنشاء بيانات اختبار عشوائية
 */

export const testData = {
  /**
   * Generate random email
   * إنشاء بريد إلكتروني عشوائي
   */
  randomEmail: () => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 10000);
    return `test-${timestamp}-${random}@sahool.com`;
  },

  /**
   * Generate random name
   * إنشاء اسم عشوائي
   */
  randomName: () => {
    const names = [
      "Ahmed Ali",
      "Fatima Hassan",
      "Mohammed Ibrahim",
      "Aisha Abdullah",
      "Omar Khalid",
      "Noor Ahmad",
    ];
    return names[Math.floor(Math.random() * names.length)];
  },

  /**
   * Generate random phone number
   * إنشاء رقم هاتف عشوائي
   */
  randomPhone: () => {
    const prefix = "+966";
    const number = Math.floor(Math.random() * 900000000) + 100000000;
    return `${prefix}${number}`;
  },

  /**
   * Generate random field data
   * إنشاء بيانات حقل عشوائية
   */
  randomField: () => ({
    name: `Test Field ${Date.now()}`,
    nameAr: `حقل اختباري ${Date.now()}`,
    area: Math.floor(Math.random() * 1000) + 100,
    location: {
      lat: 24.7136 + (Math.random() - 0.5) * 0.1,
      lng: 46.6753 + (Math.random() - 0.5) * 0.1,
    },
    cropType: ["wheat", "corn", "rice", "barley"][
      Math.floor(Math.random() * 4)
    ],
  }),

  /**
   * Generate random task data
   * إنشاء بيانات مهمة عشوائية
   */
  randomTask: () => ({
    title: `Test Task ${Date.now()}`,
    titleAr: `مهمة اختبارية ${Date.now()}`,
    description: "This is a test task created by E2E tests",
    descriptionAr: "هذه مهمة اختبارية تم إنشاؤها بواسطة اختبارات E2E",
    priority: ["low", "medium", "high"][Math.floor(Math.random() * 3)],
    status: "pending",
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0],
  }),

  /**
   * Generate random equipment data
   * إنشاء بيانات معدات عشوائية
   */
  randomEquipment: () => ({
    name: `Test Equipment ${Date.now()}`,
    nameAr: `معدة اختبارية ${Date.now()}`,
    type: ["tractor", "harvester", "irrigation", "sprayer"][
      Math.floor(Math.random() * 4)
    ],
    model: `Model-${Math.floor(Math.random() * 1000)}`,
    purchaseDate: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0],
  }),

  /**
   * Generate random sensor data
   * إنشاء بيانات مستشعر عشوائية
   */
  randomSensor: () => ({
    name: `Test Sensor ${Date.now()}`,
    type: ["temperature", "humidity", "soil_moisture", "light"][
      Math.floor(Math.random() * 4)
    ],
    value: Math.floor(Math.random() * 100),
    unit: "percent",
    timestamp: new Date().toISOString(),
  }),
};

/**
 * Common test selectors
 * محددات الاختبار الشائعة
 */
export const selectors = {
  // Buttons
  saveButton: 'button:has-text("Save"), button:has-text("حفظ")',
  cancelButton: 'button:has-text("Cancel"), button:has-text("إلغاء")',
  addButton: 'button:has-text("Add"), button:has-text("إضافة")',
  deleteButton: 'button:has-text("Delete"), button:has-text("حذف")',
  editButton: 'button:has-text("Edit"), button:has-text("تعديل")',
  submitButton: 'button[type="submit"]',

  // Forms
  emailInput: 'input[type="email"]',
  passwordInput: 'input[type="password"]',
  searchInput:
    'input[type="search"], input[placeholder*="Search"], input[placeholder*="بحث"]',

  // Navigation
  loginLink: 'a[href="/login"]',
  dashboardLink: 'a[href="/dashboard"]',
  settingsLink: 'a[href="/settings"]',

  // Common elements
  toast: '[role="alert"], [data-testid="toast"]',
  modal: '[role="dialog"]',
  loading: '[class*="loading"], [aria-busy="true"]',
  error: '[role="alert"][class*="error"]',
};

/**
 * Common test timeouts
 * مهل الوقت الشائعة
 */
export const timeouts = {
  short: 1000,
  medium: 3000,
  long: 5000,
  veryLong: 10000,
  navigation: 15000,
};

/**
 * Test user roles
 * أدوار المستخدم الاختبارية
 */
export const userRoles = {
  admin: {
    email: process.env.ADMIN_USER_EMAIL || "admin@sahool.com",
    password: process.env.ADMIN_USER_PASSWORD || "Admin@123456",
  },
  farmer: {
    email: process.env.TEST_USER_EMAIL || "test@sahool.com",
    password: process.env.TEST_USER_PASSWORD || "Test@123456",
  },
  advisor: {
    email: process.env.ADVISOR_USER_EMAIL || "advisor@sahool.com",
    password: process.env.ADVISOR_USER_PASSWORD || "Advisor@123456",
  },
};

/**
 * API endpoints (for mocking or verification)
 * نقاط النهاية API
 */
export const apiEndpoints = {
  login: "/api/auth/login",
  logout: "/api/auth/logout",
  profile: "/api/users/profile",
  fields: "/api/fields",
  tasks: "/api/tasks",
  equipment: "/api/equipment",
  sensors: "/api/sensors",
  weather: "/api/weather",
  analytics: "/api/analytics",
};

/**
 * Page URLs
 * عناوين URL للصفحات
 */
export const pages = {
  home: "/",
  login: "/login",
  dashboard: "/dashboard",
  fields: "/fields",
  tasks: "/tasks",
  analytics: "/analytics",
  marketplace: "/marketplace",
  settings: "/settings",
  iot: "/iot",
  weather: "/weather",
  equipment: "/equipment",
  cropHealth: "/crop-health",
  community: "/community",
  wallet: "/wallet",
};
