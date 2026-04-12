/**
 * UX Scenario Helper Functions
 * دوال مساعدة لسيناريوهات تجربة المستخدم
 *
 * Common utilities for SAHOOL platform E2E UX testing
 * أدوات مشتركة لاختبارات تجربة المستخدم E2E لمنصة سهول
 */

import { Page, expect, Locator } from "@playwright/test";

// ═══════════════════════════════════════════════════════════════════════════════
// Authentication Helpers - مساعدات المصادقة
// ═══════════════════════════════════════════════════════════════════════════════

export interface UserCredentials {
  email: string;
  password: string;
  phone?: string;
  name?: string;
  nameAr?: string;
  role?: "farmer" | "cooperative_admin" | "advisor" | "admin";
}

/**
 * Default test users for different scenarios
 * المستخدمون الافتراضيون للاختبار لسيناريوهات مختلفة
 */
export const testUsers = {
  farmer: {
    email: "farmer@sahool.test",
    password: "Farmer@123456",
    phone: "+966501234567",
    name: "Ahmed Al-Farsi",
    nameAr: "أحمد الفارسي",
    role: "farmer" as const,
  },
  cooperativeAdmin: {
    email: "coop-admin@sahool.test",
    password: "CoopAdmin@123456",
    phone: "+966502345678",
    name: "Fatima Al-Hassan",
    nameAr: "فاطمة الحسن",
    role: "cooperative_admin" as const,
  },
  advisor: {
    email: "advisor@sahool.test",
    password: "Advisor@123456",
    phone: "+966503456789",
    name: "Mohammed Al-Rashid",
    nameAr: "محمد الراشد",
    role: "advisor" as const,
  },
};

/**
 * Register a new user
 * تسجيل مستخدم جديد
 */
export async function registerUser(
  page: Page,
  user: Partial<UserCredentials> & { email: string; password: string }
): Promise<void> {
  await page.goto("/register");
  await page.waitForLoadState("domcontentloaded");

  // Fill registration form
  // ملء نموذج التسجيل
  await page.fill('input[name="email"], input[type="email"]', user.email);
  await page.fill('input[name="password"], input[type="password"]', user.password);

  if (user.phone) {
    await page.fill('input[name="phone"], input[type="tel"]', user.phone);
  }

  if (user.name) {
    await page.fill('input[name="name"], input[placeholder*="Name"]', user.name);
  }

  if (user.nameAr) {
    await page.fill('input[name="nameAr"], input[placeholder*="الاسم"]', user.nameAr);
  }

  // Submit form
  await page.click('button[type="submit"]');

  // Wait for success (redirect to dashboard or verification page)
  // انتظار النجاح (إعادة التوجيه إلى لوحة التحكم أو صفحة التحقق)
  await page.waitForURL(/\/(dashboard|verify|login)/, { timeout: 15000 });
}

/**
 * Login user
 * تسجيل دخول المستخدم
 */
export async function loginUser(
  page: Page,
  credentials: { email: string; password: string }
): Promise<void> {
  // Check if already in CI mode - use mock login
  // التحقق إذا كان في وضع CI - استخدام تسجيل دخول وهمي
  if (process.env.CI) {
    await mockLogin(page, credentials);
    return;
  }

  await page.goto("/login");
  await page.waitForLoadState("domcontentloaded");

  await page.fill('input[type="email"]', credentials.email);
  await page.fill('input[type="password"]', credentials.password);
  await page.click('button[type="submit"]');

  await page.waitForURL(/\/dashboard/, { timeout: 15000 });
}

/**
 * Mock login for CI environment
 * تسجيل دخول وهمي لبيئة CI
 */
export async function mockLogin(
  page: Page,
  credentials: { email: string; password?: string }
): Promise<void> {
  const baseURL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000";

  await page.context().addCookies([
    {
      name: "access_token",
      value: "mock_test_token_ux_scenarios",
      domain: new URL(baseURL).hostname,
      path: "/",
      httpOnly: true,
      secure: false,
      sameSite: "Lax",
    },
    {
      name: "user_session",
      value: JSON.stringify({
        id: `test-user-${Date.now()}`,
        email: credentials.email,
        name: "Test User",
        nameAr: "مستخدم اختباري",
        role: "farmer",
      }),
      domain: new URL(baseURL).hostname,
      path: "/",
      httpOnly: false,
      secure: false,
      sameSite: "Lax",
    },
  ]);

  await page.goto("/dashboard");
  await page.waitForLoadState("domcontentloaded");
}

/**
 * Logout user
 * تسجيل خروج المستخدم
 */
export async function logoutUser(page: Page): Promise<void> {
  // Try to find user menu
  const userMenu = page.locator(
    '[data-testid="user-menu"], [aria-label*="user"], [aria-label*="المستخدم"]'
  ).first();

  if (await userMenu.isVisible({ timeout: 3000 }).catch(() => false)) {
    await userMenu.click();
    await page.waitForTimeout(300);

    const logoutBtn = page.locator(
      'button:has-text("Logout"), button:has-text("تسجيل الخروج"), [data-testid="logout"]'
    ).first();

    if (await logoutBtn.isVisible()) {
      await logoutBtn.click();
    }
  }

  await page.waitForURL(/\/login/, { timeout: 10000 });
}

// ═══════════════════════════════════════════════════════════════════════════════
// Farm & Field Helpers - مساعدات المزرعة والحقل
// ═══════════════════════════════════════════════════════════════════════════════

export interface FarmData {
  name: string;
  nameAr: string;
  location: { lat: number; lng: number };
  totalArea: number;
  waterSource?: string;
}

export interface FieldData {
  name: string;
  nameAr: string;
  area: number;
  cropType: string;
  soilType?: string;
  irrigationType?: string;
  geometry?: GeoJSON.Polygon;
}

/**
 * Sample farm data for testing
 * بيانات مزرعة نموذجية للاختبار
 */
export const sampleFarms: FarmData[] = [
  {
    name: "Al-Rashid Farm",
    nameAr: "مزرعة الراشد",
    location: { lat: 24.7136, lng: 46.6753 },
    totalArea: 50,
    waterSource: "well",
  },
  {
    name: "Green Valley Farm",
    nameAr: "مزرعة الوادي الأخضر",
    location: { lat: 21.4858, lng: 39.1925 },
    totalArea: 120,
    waterSource: "irrigation_canal",
  },
];

/**
 * Sample field data for different crops
 * بيانات حقول نموذجية لمحاصيل مختلفة
 */
export const sampleFields = {
  wheat: {
    name: "Wheat Field North",
    nameAr: "حقل القمح الشمالي",
    area: 15.5,
    cropType: "wheat",
    soilType: "clay_loam",
    irrigationType: "center_pivot",
  },
  datePalm: {
    name: "Date Palm Grove",
    nameAr: "بستان النخيل",
    area: 8.0,
    cropType: "date_palm",
    soilType: "sandy_loam",
    irrigationType: "drip",
  },
  tomato: {
    name: "Tomato Greenhouse",
    nameAr: "دفيئة الطماطم",
    area: 2.5,
    cropType: "tomato",
    soilType: "loam",
    irrigationType: "drip",
  },
  barley: {
    name: "Barley Field",
    nameAr: "حقل الشعير",
    area: 20.0,
    cropType: "barley",
    soilType: "sandy",
    irrigationType: "flood",
  },
};

/**
 * Create a new farm
 * إنشاء مزرعة جديدة
 */
export async function createFarm(page: Page, farm: FarmData): Promise<string> {
  await page.goto("/farms/new");
  await page.waitForLoadState("domcontentloaded");

  // Fill farm details
  // ملء تفاصيل المزرعة
  await page.fill('input[name="name"]', farm.name);
  await page.fill('input[name="nameAr"]', farm.nameAr);
  await page.fill('input[name="totalArea"]', farm.totalArea.toString());

  if (farm.waterSource) {
    const waterSelect = page.locator('select[name="waterSource"], [data-testid="water-source"]');
    if (await waterSelect.isVisible()) {
      await waterSelect.selectOption(farm.waterSource);
    }
  }

  // Set location (click on map or fill coordinates)
  // تعيين الموقع (النقر على الخريطة أو ملء الإحداثيات)
  const latInput = page.locator('input[name="latitude"]');
  const lngInput = page.locator('input[name="longitude"]');

  if (await latInput.isVisible()) {
    await latInput.fill(farm.location.lat.toString());
    await lngInput.fill(farm.location.lng.toString());
  }

  // Submit
  await page.click('button[type="submit"], button:has-text("Save"), button:has-text("حفظ")');

  // Wait for success and return farm ID
  await page.waitForURL(/\/farms\/[a-zA-Z0-9-]+/, { timeout: 10000 });
  const url = page.url();
  const farmId = url.split("/").pop() || "";

  return farmId;
}

/**
 * Create a new field with boundary drawing simulation
 * إنشاء حقل جديد مع محاكاة رسم الحدود
 */
export async function createField(page: Page, field: FieldData): Promise<string> {
  await page.goto("/fields/new");
  await page.waitForLoadState("domcontentloaded");

  // Fill field details
  // ملء تفاصيل الحقل
  await page.fill('input[name="name"]', field.name);

  const nameArInput = page.locator('input[name="nameAr"]');
  if (await nameArInput.isVisible()) {
    await nameArInput.fill(field.nameAr);
  }

  await page.fill('input[name="area"]', field.area.toString());

  // Select crop type
  // اختيار نوع المحصول
  const cropSelect = page.locator(
    'select[name="cropType"], [data-testid="crop-type-select"]'
  );
  if (await cropSelect.isVisible()) {
    await cropSelect.selectOption(field.cropType);
  }

  // Select soil type if available
  // اختيار نوع التربة إذا كان متاحاً
  if (field.soilType) {
    const soilSelect = page.locator('select[name="soilType"]');
    if (await soilSelect.isVisible()) {
      await soilSelect.selectOption(field.soilType);
    }
  }

  // Select irrigation type if available
  // اختيار نوع الري إذا كان متاحاً
  if (field.irrigationType) {
    const irrigationSelect = page.locator('select[name="irrigationType"]');
    if (await irrigationSelect.isVisible()) {
      await irrigationSelect.selectOption(field.irrigationType);
    }
  }

  // Submit
  await page.click('button[type="submit"], button:has-text("Save"), button:has-text("حفظ")');

  // Wait for success
  await page.waitForURL(/\/fields\/[a-zA-Z0-9-]+/, { timeout: 10000 });
  const url = page.url();
  const fieldId = url.split("/").pop() || "";

  return fieldId;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Task & Operations Helpers - مساعدات المهام والعمليات
// ═══════════════════════════════════════════════════════════════════════════════

export interface TaskData {
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  type: "irrigation" | "fertilizer" | "pest_control" | "harvest" | "planting" | "other";
  priority: "low" | "medium" | "high" | "critical";
  dueDate: string;
  fieldId?: string;
}

/**
 * Sample tasks for different operations
 * مهام نموذجية لعمليات مختلفة
 */
export const sampleTasks = {
  irrigation: {
    title: "Morning Irrigation - Wheat Field",
    titleAr: "ري صباحي - حقل القمح",
    description: "Apply 25mm of irrigation water using center pivot",
    descriptionAr: "تطبيق 25 ملم من مياه الري باستخدام الرشاش المحوري",
    type: "irrigation" as const,
    priority: "high" as const,
    dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  },
  fertilizer: {
    title: "Nitrogen Application",
    titleAr: "تطبيق النيتروجين",
    description: "Apply Urea 46% at 50kg/ha for wheat tillering stage",
    descriptionAr: "تطبيق يوريا 46% بمعدل 50 كجم/هكتار لمرحلة التفريع",
    type: "fertilizer" as const,
    priority: "medium" as const,
    dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  },
  pestControl: {
    title: "Aphid Treatment",
    titleAr: "معالجة المن",
    description: "Apply insecticide for aphid infestation in wheat",
    descriptionAr: "تطبيق مبيد حشري لإصابة المن في القمح",
    type: "pest_control" as const,
    priority: "critical" as const,
    dueDate: new Date().toISOString().split("T")[0],
  },
  harvest: {
    title: "Date Harvest - First Pick",
    titleAr: "حصاد التمور - الجني الأول",
    description: "Harvest ripe dates from Date Palm Grove",
    descriptionAr: "حصاد التمور الناضجة من بستان النخيل",
    type: "harvest" as const,
    priority: "high" as const,
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  },
};

/**
 * Create a new task
 * إنشاء مهمة جديدة
 */
export async function createTask(page: Page, task: TaskData): Promise<string> {
  await page.goto("/tasks/new");
  await page.waitForLoadState("domcontentloaded");

  await page.fill('input[name="title"]', task.title);

  const titleArInput = page.locator('input[name="titleAr"]');
  if (await titleArInput.isVisible()) {
    await titleArInput.fill(task.titleAr);
  }

  if (task.description) {
    await page.fill('textarea[name="description"]', task.description);
  }

  // Select task type
  const typeSelect = page.locator('select[name="type"], [data-testid="task-type"]');
  if (await typeSelect.isVisible()) {
    await typeSelect.selectOption(task.type);
  }

  // Select priority
  const prioritySelect = page.locator('select[name="priority"]');
  if (await prioritySelect.isVisible()) {
    await prioritySelect.selectOption(task.priority);
  }

  // Set due date
  await page.fill('input[name="dueDate"], input[type="date"]', task.dueDate);

  // Submit
  await page.click('button[type="submit"]');

  await page.waitForURL(/\/tasks\/[a-zA-Z0-9-]+/, { timeout: 10000 });
  const taskId = page.url().split("/").pop() || "";

  return taskId;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Weather & NDVI Helpers - مساعدات الطقس ومؤشر NDVI
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Mock weather data for testing
 * بيانات طقس وهمية للاختبار
 */
export const mockWeatherData = {
  current: {
    temperature: 28,
    humidity: 45,
    windSpeed: 12,
    condition: "sunny",
    conditionAr: "مشمس",
  },
  forecast: [
    { day: "Today", high: 32, low: 22, condition: "sunny", rainChance: 0 },
    { day: "Tomorrow", high: 30, low: 20, condition: "partly_cloudy", rainChance: 10 },
    { day: "Day After", high: 28, low: 18, condition: "cloudy", rainChance: 30 },
  ],
};

/**
 * Mock NDVI data for testing
 * بيانات NDVI وهمية للاختبار
 */
export const mockNDVIData = {
  currentValue: 0.72,
  healthStatus: "healthy",
  healthStatusAr: "صحي",
  trend: "stable",
  lastUpdated: new Date().toISOString(),
  history: [
    { date: "2026-01-01", value: 0.65 },
    { date: "2026-01-15", value: 0.68 },
    { date: "2026-02-01", value: 0.72 },
  ],
};

// ═══════════════════════════════════════════════════════════════════════════════
// Offline & Sync Helpers - مساعدات عدم الاتصال والمزامنة
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Simulate offline mode
 * محاكاة وضع عدم الاتصال
 */
export async function goOffline(page: Page): Promise<void> {
  await page.context().setOffline(true);
}

/**
 * Simulate online mode
 * محاكاة وضع الاتصال
 */
export async function goOnline(page: Page): Promise<void> {
  await page.context().setOffline(false);
}

/**
 * Check if offline indicator is visible
 * التحقق من ظهور مؤشر عدم الاتصال
 */
export async function isOfflineIndicatorVisible(page: Page): Promise<boolean> {
  const offlineIndicator = page.locator(
    '[data-testid="offline-indicator"], [class*="offline"], text=/offline|غير متصل/i'
  );
  return offlineIndicator.isVisible({ timeout: 3000 }).catch(() => false);
}

/**
 * Wait for sync to complete
 * انتظار اكتمال المزامنة
 */
export async function waitForSync(page: Page, timeout = 30000): Promise<boolean> {
  const syncIndicator = page.locator(
    '[data-testid="sync-indicator"], [class*="syncing"]'
  );

  // Wait for sync indicator to appear
  const appeared = await syncIndicator.isVisible({ timeout: 5000 }).catch(() => false);

  if (!appeared) {
    return true; // No sync needed
  }

  // Wait for it to disappear (sync complete)
  await syncIndicator.waitFor({ state: "hidden", timeout });
  return true;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Notification Helpers - مساعدات الإشعارات
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Wait for notification/alert to appear
 * انتظار ظهور الإشعار/التنبيه
 */
export async function waitForNotification(
  page: Page,
  type?: "success" | "error" | "warning" | "info",
  timeout = 5000
): Promise<Locator | null> {
  let selector = '[role="alert"], [data-testid="notification"], .toast, [class*="notification"]';

  if (type) {
    selector += `, [class*="${type}"]`;
  }

  try {
    await page.waitForSelector(selector, { timeout, state: "visible" });
    return page.locator(selector).first();
  } catch {
    return null;
  }
}

/**
 * Dismiss notification
 * إغلاق الإشعار
 */
export async function dismissNotification(page: Page): Promise<void> {
  const dismissBtn = page.locator(
    '[data-testid="dismiss-notification"], [aria-label="Close"], [aria-label="إغلاق"], button:has-text("×")'
  ).first();

  if (await dismissBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
    await dismissBtn.click();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Cooperative Helpers - مساعدات التعاونيات
// ═══════════════════════════════════════════════════════════════════════════════

export interface CooperativeData {
  name: string;
  nameAr: string;
  registrationNumber: string;
  location: string;
  locationAr: string;
}

/**
 * Sample cooperative data
 * بيانات تعاونية نموذجية
 */
export const sampleCooperatives: CooperativeData[] = [
  {
    name: "Al-Qassim Agricultural Cooperative",
    nameAr: "التعاونية الزراعية بالقصيم",
    registrationNumber: "COOP-2024-001",
    location: "Buraidah, Al-Qassim",
    locationAr: "بريدة، القصيم",
  },
  {
    name: "Green Oasis Cooperative",
    nameAr: "تعاونية الواحة الخضراء",
    registrationNumber: "COOP-2024-002",
    location: "Al-Ahsa, Eastern Province",
    locationAr: "الأحساء، المنطقة الشرقية",
  },
];

/**
 * Create a cooperative organization
 * إنشاء منظمة تعاونية
 */
export async function createCooperative(
  page: Page,
  coop: CooperativeData
): Promise<string> {
  await page.goto("/cooperatives/new");
  await page.waitForLoadState("domcontentloaded");

  await page.fill('input[name="name"]', coop.name);
  await page.fill('input[name="nameAr"]', coop.nameAr);
  await page.fill('input[name="registrationNumber"]', coop.registrationNumber);
  await page.fill('input[name="location"]', coop.location);

  await page.click('button[type="submit"]');

  await page.waitForURL(/\/cooperatives\/[a-zA-Z0-9-]+/, { timeout: 10000 });
  return page.url().split("/").pop() || "";
}

// ═══════════════════════════════════════════════════════════════════════════════
// Common UI Helpers - مساعدات واجهة المستخدم الشائعة
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Wait for page to be fully loaded
 * انتظار تحميل الصفحة بالكامل
 */
export async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState("domcontentloaded");
}

/**
 * Navigate and wait for load
 * التنقل وانتظار التحميل
 */
export async function navigateAndWait(page: Page, url: string): Promise<void> {
  await page.goto(url);
  await waitForPageLoad(page);
}

/**
 * Check for Arabic RTL layout
 * التحقق من تخطيط RTL للعربية
 */
export async function isRTLLayout(page: Page): Promise<boolean> {
  const dir = await page.locator("html").getAttribute("dir");
  return dir === "rtl";
}

/**
 * Switch language
 * تبديل اللغة
 */
export async function switchLanguage(page: Page, lang: "ar" | "en"): Promise<void> {
  const langSwitcher = page.locator(
    '[data-testid="language-switcher"], [aria-label*="language"], [aria-label*="اللغة"]'
  ).first();

  if (await langSwitcher.isVisible()) {
    await langSwitcher.click();
    await page.waitForTimeout(300);

    const langOption = page.locator(
      `button:has-text("${lang === "ar" ? "العربية" : "English"}"), [data-lang="${lang}"]`
    ).first();

    if (await langOption.isVisible()) {
      await langOption.click();
      await page.waitForTimeout(500);
    }
  }
}

/**
 * Common timeouts for E2E tests
 * المهلات الشائعة لاختبارات E2E
 */
export const timeouts = {
  short: 1000,
  medium: 3000,
  long: 5000,
  veryLong: 10000,
  navigation: 15000,
  sync: 30000,
};

/**
 * Common selectors for bilingual UI
 * محددات شائعة لواجهة المستخدم ثنائية اللغة
 */
export const selectors = {
  // Buttons - الأزرار
  saveButton: 'button:has-text("Save"), button:has-text("حفظ")',
  cancelButton: 'button:has-text("Cancel"), button:has-text("إلغاء")',
  addButton: 'button:has-text("Add"), button:has-text("إضافة")',
  deleteButton: 'button:has-text("Delete"), button:has-text("حذف")',
  editButton: 'button:has-text("Edit"), button:has-text("تعديل")',
  submitButton: 'button[type="submit"]',
  confirmButton: 'button:has-text("Confirm"), button:has-text("تأكيد")',

  // Navigation - التنقل
  dashboardLink: 'a[href="/dashboard"]',
  fieldsLink: 'a[href="/fields"]',
  tasksLink: 'a[href="/tasks"]',
  weatherLink: 'a[href="/weather"]',
  settingsLink: 'a[href="/settings"]',

  // Common elements - العناصر الشائعة
  toast: '[role="alert"], [data-testid="toast"], .toast',
  modal: '[role="dialog"]',
  loading: '[class*="loading"], [aria-busy="true"], [data-testid="loading"]',
  error: '[role="alert"][class*="error"], [data-testid="error"]',
};
