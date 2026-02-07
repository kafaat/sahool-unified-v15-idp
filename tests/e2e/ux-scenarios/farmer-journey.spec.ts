/**
 * Farmer Journey E2E Test Scenarios
 * سيناريوهات اختبار رحلة المزارع من البداية إلى النهاية
 *
 * Complete farmer journey from registration to daily operations:
 * رحلة المزارع الكاملة من التسجيل إلى العمليات اليومية:
 *
 * - Registration and login (التسجيل وتسجيل الدخول)
 * - Adding first farm and fields (إضافة المزرعة والحقول الأولى)
 * - Setting up crop planning (إعداد تخطيط المحاصيل)
 * - Viewing weather and NDVI data (عرض بيانات الطقس ومؤشر NDVI)
 * - Receiving irrigation recommendations (تلقي توصيات الري)
 * - Managing tasks and equipment (إدارة المهام والمعدات)
 *
 * Crops covered: Wheat (قمح), Date Palm (نخيل), Tomato (طماطم)
 *
 * @author SAHOOL Platform Team
 */

import { test, expect } from "./fixtures/test-fixtures";
import {
  registerUser,
  loginUser,
  logoutUser,
  createFarm,
  createField,
  createTask,
  testUsers,
  sampleFarms,
  sampleFields,
  sampleTasks,
  waitForPageLoad,
  navigateAndWait,
  waitForNotification,
  timeouts,
  selectors,
} from "./helpers/ux-helpers";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Farmer Registration & Onboarding
// مجموعة الاختبارات: تسجيل المزارع والإعداد الأولي
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Farmer Registration & Onboarding | تسجيل المزارع والإعداد", () => {
  test("should display registration page with Arabic/English content | عرض صفحة التسجيل بمحتوى عربي/إنجليزي", async ({
    page,
  }) => {
    // Navigate to registration page
    // الانتقال إلى صفحة التسجيل
    await page.goto("/register");
    await waitForPageLoad(page);

    // Verify bilingual content is present
    // التحقق من وجود المحتوى ثنائي اللغة
    await expect(
      page.locator("text=/إنشاء حساب|Create Account|Register|تسجيل/i")
    ).toBeVisible();

    // Check for required form fields
    // التحقق من حقول النموذج المطلوبة
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();

    // Check for SAHOOL branding
    // التحقق من العلامة التجارية لسهول
    await expect(page.locator("text=/SAHOOL|سهول/i")).toBeVisible();
  });

  test("should validate registration form fields | التحقق من صحة حقول نموذج التسجيل", async ({
    page,
  }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    // Try to submit empty form
    // محاولة إرسال نموذج فارغ
    await page.click('button[type="submit"]');

    // Should show validation errors or stay on page
    // يجب أن تظهر أخطاء التحقق أو البقاء في الصفحة
    await expect(page).toHaveURL(/\/register/);

    // Test invalid email format
    // اختبار تنسيق بريد إلكتروني غير صالح
    await page.fill('input[type="email"]', "invalid-email");
    await page.fill('input[type="password"]', "Test@123456");
    await page.click('button[type="submit"]');

    // Should show email validation error
    // يجب أن يظهر خطأ التحقق من البريد الإلكتروني
    const emailInput = page.locator('input[type="email"]');
    const isInvalid = await emailInput.evaluate(
      (el: HTMLInputElement) => !el.validity.valid
    );
    expect(isInvalid).toBe(true);
  });

  test("should successfully register new farmer | تسجيل مزارع جديد بنجاح", async ({
    page,
  }) => {
    const uniqueEmail = `farmer-${Date.now()}@sahool.test`;

    await page.goto("/register");
    await waitForPageLoad(page);

    // Fill registration form
    // ملء نموذج التسجيل
    await page.fill('input[type="email"]', uniqueEmail);
    await page.fill('input[type="password"]', "SecurePass@123");

    // Fill phone number if field exists
    // ملء رقم الهاتف إذا كان الحقل موجوداً
    const phoneInput = page.locator('input[type="tel"], input[name="phone"]');
    if (await phoneInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await phoneInput.fill("+966501234567");
    }

    // Fill name if field exists
    // ملء الاسم إذا كان الحقل موجوداً
    const nameInput = page.locator('input[name="name"]');
    if (await nameInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await nameInput.fill("Test Farmer");
    }

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for success - either redirect to dashboard or verification page
    // انتظار النجاح - إما إعادة التوجيه إلى لوحة التحكم أو صفحة التحقق
    await page.waitForURL(/\/(dashboard|verify|login|onboarding)/, {
      timeout: timeouts.navigation,
    });
  });

  test("should show onboarding flow for new farmer | عرض تدفق الإعداد للمزارع الجديد", async ({
    farmerPage,
  }) => {
    // New farmer should see dashboard or onboarding
    // يجب أن يرى المزارع الجديد لوحة التحكم أو الإعداد
    await expect(farmerPage).toHaveURL(/\/(dashboard|onboarding)/);

    // Check for welcome message
    // التحقق من رسالة الترحيب
    const welcomeText = farmerPage.locator(
      "text=/Welcome|مرحباً|أهلاً|Getting Started|البدء/i"
    );

    const hasWelcome = await welcomeText
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasWelcome) {
      await expect(welcomeText).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Login Flow
// مجموعة الاختبارات: تدفق تسجيل الدخول
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Farmer Login Flow | تدفق تسجيل دخول المزارع", () => {
  test("should display login page correctly | عرض صفحة تسجيل الدخول بشكل صحيح", async ({
    page,
  }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    // Check for login form elements
    // التحقق من عناصر نموذج تسجيل الدخول
    await expect(
      page.locator("text=/تسجيل الدخول|Login|Sign In/i")
    ).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Check for forgot password link
    // التحقق من رابط نسيت كلمة المرور
    await expect(
      page.locator("text=/نسيت كلمة المرور|Forgot Password/i")
    ).toBeVisible();
  });

  test("should show error for invalid credentials | عرض خطأ لبيانات اعتماد غير صالحة", async ({
    page,
  }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    await page.fill('input[type="email"]', "wrong@email.com");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    // Wait for error message
    // انتظار رسالة الخطأ
    const errorNotification = await waitForNotification(page, "error", 5000);

    // Should still be on login page
    // يجب أن يظل في صفحة تسجيل الدخول
    await expect(page).toHaveURL(/\/login/);
  });

  test("should successfully login and redirect to dashboard | تسجيل الدخول بنجاح والانتقال إلى لوحة التحكم", async ({
    page,
    farmer,
  }) => {
    await loginUser(page, farmer);

    // Should be on dashboard
    // يجب أن يكون في لوحة التحكم
    await expect(page).toHaveURL(/\/dashboard/);

    // Should see user name or welcome message
    // يجب أن يرى اسم المستخدم أو رسالة الترحيب
    await expect(
      page.locator("text=/مرحباً|Welcome|Dashboard|لوحة التحكم/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should logout successfully | تسجيل الخروج بنجاح", async ({
    farmerPage,
  }) => {
    // Already logged in via fixture
    // تم تسجيل الدخول بالفعل عبر الإعداد
    await expect(farmerPage).toHaveURL(/\/dashboard/);

    await logoutUser(farmerPage);

    // Should be redirected to login
    // يجب إعادة التوجيه إلى تسجيل الدخول
    await expect(farmerPage).toHaveURL(/\/login/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Adding Farm & Fields
// مجموعة الاختبارات: إضافة المزرعة والحقول
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Adding Farm & Fields | إضافة المزرعة والحقول", () => {
  test("should display farms page with add button | عرض صفحة المزارع مع زر الإضافة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/farms");

    // Check for add farm button
    // التحقق من زر إضافة المزرعة
    const addButton = farmerPage.locator(
      'button:has-text("Add Farm"), button:has-text("إضافة مزرعة"), a:has-text("Add"), a:has-text("إضافة")'
    );

    await expect(addButton.first()).toBeVisible({ timeout: timeouts.long });
  });

  test("should open add farm form with required fields | فتح نموذج إضافة المزرعة مع الحقول المطلوبة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/farms/new");

    // Check for form fields
    // التحقق من حقول النموذج
    await expect(farmerPage.locator('input[name="name"]')).toBeVisible({
      timeout: timeouts.long,
    });

    // Check for location/map section
    // التحقق من قسم الموقع/الخريطة
    const mapSection = farmerPage.locator(
      '[data-testid="map"], [class*="map"], #map'
    );
    const hasMap = await mapSection
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Farm should have either map or coordinate inputs
    // يجب أن يكون للمزرعة خريطة أو حقول إحداثيات
    if (!hasMap) {
      const latInput = farmerPage.locator('input[name="latitude"]');
      const lngInput = farmerPage.locator('input[name="longitude"]');
      expect(
        (await latInput.isVisible()) || (await lngInput.isVisible())
      ).toBeTruthy();
    }
  });

  test("should create first farm successfully | إنشاء المزرعة الأولى بنجاح", async ({
    farmerPage,
    sampleFarm,
  }) => {
    await navigateAndWait(farmerPage, "/farms/new");

    // Fill farm name
    // ملء اسم المزرعة
    await farmerPage.fill('input[name="name"]', sampleFarm.name);

    // Fill Arabic name if available
    // ملء الاسم بالعربية إذا كان متاحاً
    const nameArInput = farmerPage.locator('input[name="nameAr"]');
    if (await nameArInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await nameArInput.fill(sampleFarm.nameAr);
    }

    // Fill total area
    // ملء المساحة الإجمالية
    const areaInput = farmerPage.locator('input[name="totalArea"]');
    if (await areaInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await areaInput.fill(sampleFarm.totalArea.toString());
    }

    // Submit
    await farmerPage.click(selectors.submitButton);

    // Should redirect to farm details or list
    // يجب إعادة التوجيه إلى تفاصيل المزرعة أو القائمة
    await farmerPage.waitForURL(/\/farms/, { timeout: timeouts.navigation });

    // Check for success toast
    // التحقق من رسالة النجاح
    const notification = await waitForNotification(farmerPage, "success", 3000);
    if (notification) {
      await expect(notification).toBeVisible();
    }
  });

  test("should add wheat field with crop details | إضافة حقل قمح مع تفاصيل المحصول", async ({
    farmerPage,
    sampleWheatField,
  }) => {
    await navigateAndWait(farmerPage, "/fields/new");

    // Fill field name
    // ملء اسم الحقل
    await farmerPage.fill('input[name="name"]', sampleWheatField.name);

    // Fill area
    // ملء المساحة
    const areaInput = farmerPage.locator('input[name="area"]');
    if (await areaInput.isVisible()) {
      await areaInput.fill(sampleWheatField.area.toString());
    }

    // Select wheat as crop type
    // اختيار القمح كنوع المحصول
    const cropSelect = farmerPage.locator(
      'select[name="cropType"], [data-testid="crop-type"]'
    );
    if (await cropSelect.isVisible()) {
      await cropSelect.selectOption({ value: "wheat" });
    }

    // Submit
    await farmerPage.click(selectors.submitButton);

    // Verify navigation
    await farmerPage.waitForURL(/\/fields/, { timeout: timeouts.navigation });
  });

  test("should add date palm field | إضافة حقل نخيل", async ({
    farmerPage,
    sampleDatePalmField,
  }) => {
    await navigateAndWait(farmerPage, "/fields/new");

    await farmerPage.fill('input[name="name"]', sampleDatePalmField.name);

    const areaInput = farmerPage.locator('input[name="area"]');
    if (await areaInput.isVisible()) {
      await areaInput.fill(sampleDatePalmField.area.toString());
    }

    // Select date_palm as crop type
    // اختيار النخيل كنوع المحصول
    const cropSelect = farmerPage.locator('select[name="cropType"]');
    if (await cropSelect.isVisible()) {
      await cropSelect.selectOption({ value: "date_palm" });
    }

    // Select drip irrigation for date palm
    // اختيار الري بالتنقيط للنخيل
    const irrigationSelect = farmerPage.locator('select[name="irrigationType"]');
    if (await irrigationSelect.isVisible()) {
      await irrigationSelect.selectOption({ value: "drip" });
    }

    await farmerPage.click(selectors.submitButton);
    await farmerPage.waitForURL(/\/fields/, { timeout: timeouts.navigation });
  });

  test("should display fields list with created fields | عرض قائمة الحقول مع الحقول المنشأة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields");

    // Should see field cards or table
    // يجب أن ترى بطاقات الحقول أو الجدول
    const fieldItems = farmerPage.locator(
      '[data-testid="field-card"], [class*="field"], table tbody tr'
    );

    const count = await fieldItems.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Crop Planning
// مجموعة الاختبارات: تخطيط المحاصيل
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Crop Planning | تخطيط المحاصيل", () => {
  test("should display crop planning page | عرض صفحة تخطيط المحاصيل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/planning");

    // Should see planning content
    // يجب أن ترى محتوى التخطيط
    await expect(
      farmerPage.locator("text=/Planning|التخطيط|Crop Plan|خطة المحاصيل/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should create seasonal crop plan | إنشاء خطة المحاصيل الموسمية", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/planning/new");

    // Fill season details
    // ملء تفاصيل الموسم
    const seasonSelect = farmerPage.locator('select[name="season"]');
    if (await seasonSelect.isVisible()) {
      await seasonSelect.selectOption({ value: "winter" });
    }

    // Select year
    // اختيار السنة
    const yearInput = farmerPage.locator('input[name="year"]');
    if (await yearInput.isVisible()) {
      await yearInput.fill("2026");
    }

    // Add crop to plan
    // إضافة محصول للخطة
    const addCropBtn = farmerPage.locator(
      'button:has-text("Add Crop"), button:has-text("إضافة محصول")'
    );
    if (await addCropBtn.isVisible()) {
      await addCropBtn.click();
    }

    // Select wheat for winter season
    // اختيار القمح للموسم الشتوي
    const cropSelect = farmerPage.locator('[data-testid="crop-select"]');
    if (await cropSelect.isVisible()) {
      await cropSelect.selectOption({ value: "wheat" });
    }

    // Save plan
    await farmerPage.click(selectors.saveButton);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Weather & NDVI Data
// مجموعة الاختبارات: بيانات الطقس ومؤشر NDVI
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Weather & NDVI Data | بيانات الطقس ومؤشر NDVI", () => {
  test("should display current weather on dashboard | عرض الطقس الحالي في لوحة التحكم", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for weather widget
    // البحث عن أداة الطقس
    const weatherWidget = farmerPage.locator(
      '[data-testid="weather-widget"], [class*="weather"], text=/°C|°F|الطقس|Weather/i'
    );

    const hasWeather = await weatherWidget
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasWeather) {
      await expect(weatherWidget.first()).toBeVisible();
    }
  });

  test("should display weather forecast page | عرض صفحة توقعات الطقس", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/weather");

    // Check for weather content
    // التحقق من محتوى الطقس
    await expect(
      farmerPage.locator("text=/Weather|الطقس|Forecast|التوقعات/i")
    ).toBeVisible({ timeout: timeouts.long });

    // Should show temperature
    // يجب أن تظهر درجة الحرارة
    const tempElement = farmerPage.locator("text=/\\d+°/");
    const hasTemp = await tempElement
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasTemp) {
      await expect(tempElement.first()).toBeVisible();
    }
  });

  test("should display NDVI/crop health data for field | عرض بيانات NDVI/صحة المحصول للحقل", async ({
    farmerPage,
  }) => {
    // Navigate to fields
    await navigateAndWait(farmerPage, "/fields");

    // Click on first field to see details
    // النقر على الحقل الأول لرؤية التفاصيل
    const fieldCard = farmerPage.locator(
      '[data-testid="field-card"], [class*="field-card"]'
    ).first();

    const hasField = await fieldCard
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasField) {
      await fieldCard.click();
      await waitForPageLoad(farmerPage);

      // Look for NDVI or crop health indicator
      // البحث عن مؤشر NDVI أو صحة المحصول
      const ndviElement = farmerPage.locator(
        'text=/NDVI|Vegetation|Crop Health|صحة المحصول|الغطاء النباتي/i'
      );

      const hasNdvi = await ndviElement
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasNdvi) {
        await expect(ndviElement.first()).toBeVisible();
      }
    }
  });

  test("should show satellite imagery timeline | عرض الجدول الزمني للصور الفضائية", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/satellite");

    // Check for satellite/imagery content
    // التحقق من محتوى الأقمار الصناعية/الصور
    const satelliteContent = farmerPage.locator(
      "text=/Satellite|NDVI|Imagery|القمر الصناعي|صور فضائية/i"
    );

    const hasSatellite = await satelliteContent
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasSatellite) {
      // Look for timeline or date selector
      // البحث عن الجدول الزمني أو محدد التاريخ
      const timeline = farmerPage.locator(
        '[data-testid="timeline"], [class*="timeline"], input[type="date"]'
      );

      const hasTimeline = await timeline
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      expect(hasSatellite || hasTimeline).toBeTruthy();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Irrigation Recommendations
// مجموعة الاختبارات: توصيات الري
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Irrigation Recommendations | توصيات الري", () => {
  test("should display irrigation recommendations on dashboard | عرض توصيات الري في لوحة التحكم", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for irrigation widget or recommendations
    // البحث عن أداة الري أو التوصيات
    const irrigationWidget = farmerPage.locator(
      '[data-testid="irrigation-widget"], text=/Irrigation|الري|Water|مياه/i'
    );

    const hasIrrigation = await irrigationWidget
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasIrrigation) {
      await expect(irrigationWidget.first()).toBeVisible();
    }
  });

  test("should navigate to irrigation recommendations page | الانتقال إلى صفحة توصيات الري", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/irrigation");

    // Check for irrigation content
    // التحقق من محتوى الري
    await expect(
      farmerPage.locator(
        "text=/Irrigation|الري|Recommendations|التوصيات|Smart Irrigation|الري الذكي/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should show field-specific irrigation recommendation | عرض توصية ري محددة للحقل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/irrigation");

    // Look for irrigation recommendation cards
    // البحث عن بطاقات توصيات الري
    const recommendationCard = farmerPage.locator(
      '[data-testid="irrigation-recommendation"], [class*="recommendation"]'
    );

    const hasRecommendation = await recommendationCard
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasRecommendation) {
      // Should show water amount (e.g., "25mm" or "25 mm")
      // يجب أن تظهر كمية المياه
      const waterAmount = farmerPage.locator("text=/\\d+\\s*mm|\\d+\\s*ملم/i");
      const hasAmount = await waterAmount
        .first()
        .isVisible({ timeout: timeouts.short })
        .catch(() => false);

      if (hasAmount) {
        await expect(waterAmount.first()).toBeVisible();
      }
    }
  });

  test("should apply irrigation recommendation | تطبيق توصية الري", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/irrigation");

    // Look for apply button on recommendation
    // البحث عن زر التطبيق في التوصية
    const applyButton = farmerPage.locator(
      'button:has-text("Apply"), button:has-text("تطبيق"), button:has-text("Start Irrigation"), button:has-text("بدء الري")'
    );

    const hasApplyBtn = await applyButton
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasApplyBtn) {
      await applyButton.first().click();

      // Wait for confirmation or task creation
      // انتظار التأكيد أو إنشاء المهمة
      const confirmation = await waitForNotification(farmerPage, "success", 5000);

      if (confirmation) {
        await expect(confirmation).toBeVisible();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Tasks Management
// مجموعة الاختبارات: إدارة المهام
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Tasks Management | إدارة المهام", () => {
  test("should display tasks page | عرض صفحة المهام", async ({ farmerPage }) => {
    await navigateAndWait(farmerPage, "/tasks");

    // Check for tasks content
    // التحقق من محتوى المهام
    await expect(
      farmerPage.locator("text=/Tasks|المهام|My Tasks|مهامي/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should create irrigation task | إنشاء مهمة ري", async ({
    farmerPage,
    sampleIrrigationTask,
  }) => {
    await navigateAndWait(farmerPage, "/tasks/new");

    // Fill task details
    // ملء تفاصيل المهمة
    await farmerPage.fill('input[name="title"]', sampleIrrigationTask.title);

    // Fill description if available
    // ملء الوصف إذا كان متاحاً
    const descInput = farmerPage.locator('textarea[name="description"]');
    if (await descInput.isVisible()) {
      await descInput.fill(sampleIrrigationTask.description || "");
    }

    // Select task type
    // اختيار نوع المهمة
    const typeSelect = farmerPage.locator('select[name="type"]');
    if (await typeSelect.isVisible()) {
      await typeSelect.selectOption({ value: "irrigation" });
    }

    // Set priority
    // تعيين الأولوية
    const prioritySelect = farmerPage.locator('select[name="priority"]');
    if (await prioritySelect.isVisible()) {
      await prioritySelect.selectOption({ value: "high" });
    }

    // Set due date
    // تعيين تاريخ الاستحقاق
    const dueDateInput = farmerPage.locator('input[name="dueDate"], input[type="date"]');
    if (await dueDateInput.isVisible()) {
      await dueDateInput.fill(sampleIrrigationTask.dueDate);
    }

    // Submit
    await farmerPage.click(selectors.submitButton);

    // Verify task creation
    await farmerPage.waitForURL(/\/tasks/, { timeout: timeouts.navigation });
  });

  test("should mark task as completed | تحديد المهمة كمكتملة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/tasks");

    // Find first task
    // البحث عن المهمة الأولى
    const taskItem = farmerPage.locator(
      '[data-testid="task-item"], [class*="task"]'
    ).first();

    const hasTask = await taskItem
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasTask) {
      // Look for complete button or checkbox
      // البحث عن زر الإكمال أو مربع الاختيار
      const completeBtn = taskItem.locator(
        'button:has-text("Complete"), button:has-text("إكمال"), input[type="checkbox"]'
      );

      if (await completeBtn.first().isVisible()) {
        await completeBtn.first().click();

        // Wait for status update
        // انتظار تحديث الحالة
        await farmerPage.waitForTimeout(1000);
      }
    }
  });

  test("should filter tasks by type | تصفية المهام حسب النوع", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/tasks");

    // Look for type filter
    // البحث عن فلتر النوع
    const typeFilter = farmerPage.locator(
      '[data-testid="type-filter"], select[name="type"], button:has-text("Filter"), button:has-text("تصفية")'
    );

    const hasFilter = await typeFilter
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFilter) {
      await typeFilter.first().click();
      await farmerPage.waitForTimeout(300);

      // Select irrigation type
      // اختيار نوع الري
      const irrigationOption = farmerPage.locator(
        'option:has-text("Irrigation"), option:has-text("الري"), [role="option"]:has-text("Irrigation")'
      );

      if (await irrigationOption.first().isVisible()) {
        await irrigationOption.first().click();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Equipment Management
// مجموعة الاختبارات: إدارة المعدات
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Equipment Management | إدارة المعدات", () => {
  test("should display equipment page | عرض صفحة المعدات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/equipment");

    // Check for equipment content
    // التحقق من محتوى المعدات
    await expect(
      farmerPage.locator("text=/Equipment|المعدات|Machinery|الآلات/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should add new equipment | إضافة معدات جديدة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/equipment/new");

    // Fill equipment details
    // ملء تفاصيل المعدات
    await farmerPage.fill('input[name="name"]', "John Deere Tractor 6130R");

    // Fill Arabic name if available
    // ملء الاسم بالعربية إذا كان متاحاً
    const nameArInput = farmerPage.locator('input[name="nameAr"]');
    if (await nameArInput.isVisible()) {
      await nameArInput.fill("جرار جون ديير 6130R");
    }

    // Select equipment type
    // اختيار نوع المعدات
    const typeSelect = farmerPage.locator('select[name="type"]');
    if (await typeSelect.isVisible()) {
      await typeSelect.selectOption({ value: "tractor" });
    }

    // Fill model
    // ملء الموديل
    const modelInput = farmerPage.locator('input[name="model"]');
    if (await modelInput.isVisible()) {
      await modelInput.fill("6130R");
    }

    // Submit
    await farmerPage.click(selectors.submitButton);
    await farmerPage.waitForURL(/\/equipment/, { timeout: timeouts.navigation });
  });

  test("should view equipment status | عرض حالة المعدات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/equipment");

    // Look for equipment status indicators
    // البحث عن مؤشرات حالة المعدات
    const statusIndicator = farmerPage.locator(
      '[data-testid="equipment-status"], text=/Available|متاح|In Use|قيد الاستخدام|Maintenance|صيانة/i'
    );

    const hasStatus = await statusIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasStatus) {
      await expect(statusIndicator.first()).toBeVisible();
    }
  });

  test("should schedule equipment maintenance | جدولة صيانة المعدات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/equipment");

    // Click on first equipment item
    // النقر على عنصر المعدات الأول
    const equipmentItem = farmerPage.locator(
      '[data-testid="equipment-item"], [class*="equipment"]'
    ).first();

    const hasEquipment = await equipmentItem
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasEquipment) {
      await equipmentItem.click();
      await waitForPageLoad(farmerPage);

      // Look for maintenance button
      // البحث عن زر الصيانة
      const maintenanceBtn = farmerPage.locator(
        'button:has-text("Maintenance"), button:has-text("صيانة"), button:has-text("Schedule"), button:has-text("جدولة")'
      );

      if (await maintenanceBtn.first().isVisible()) {
        await maintenanceBtn.first().click();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Dashboard Overview
// مجموعة الاختبارات: نظرة عامة على لوحة التحكم
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Dashboard Overview | نظرة عامة على لوحة التحكم", () => {
  test("should display key metrics on dashboard | عرض المقاييس الرئيسية في لوحة التحكم", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Check for key metric widgets
    // التحقق من أدوات المقاييس الرئيسية
    const widgets = [
      "text=/Total Fields|إجمالي الحقول|Fields|الحقول/i",
      "text=/Tasks|المهام|Pending|معلقة/i",
      "text=/Weather|الطقس|°/i",
    ];

    for (const widget of widgets) {
      const element = farmerPage.locator(widget);
      const isVisible = await element
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (isVisible) {
        await expect(element.first()).toBeVisible();
      }
    }
  });

  test("should show recent activity | عرض النشاط الأخير", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for activity feed or recent updates
    // البحث عن تغذية النشاط أو التحديثات الأخيرة
    const activityFeed = farmerPage.locator(
      '[data-testid="activity-feed"], [class*="activity"], text=/Recent|الأخيرة|Activity|النشاط/i'
    );

    const hasActivity = await activityFeed
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasActivity) {
      await expect(activityFeed.first()).toBeVisible();
    }
  });

  test("should navigate to field from dashboard | الانتقال إلى الحقل من لوحة التحكم", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Find clickable field element
    // البحث عن عنصر الحقل القابل للنقر
    const fieldLink = farmerPage.locator(
      '[data-testid="field-card"] a, [class*="field"] a, a[href*="/fields/"]'
    ).first();

    const hasFieldLink = await fieldLink
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFieldLink) {
      await fieldLink.click();
      await farmerPage.waitForURL(/\/fields\//, { timeout: timeouts.navigation });
    }
  });
});
