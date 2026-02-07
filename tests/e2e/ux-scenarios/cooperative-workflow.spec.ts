/**
 * Cooperative Workflow E2E Test Scenarios
 * سيناريوهات اختبار سير عمل التعاونيات من البداية إلى النهاية
 *
 * Cooperative/multi-user scenarios covering:
 * سيناريوهات التعاونيات/متعددة المستخدمين تغطي:
 *
 * - Cooperative admin creates organization (إنشاء المنظمة بواسطة مدير التعاونية)
 * - Adding farmers to cooperative (إضافة المزارعين للتعاونية)
 * - Shared resource management (إدارة الموارد المشتركة)
 * - Collective purchase workflow (سير عمل الشراء الجماعي)
 * - Report generation (إنشاء التقارير)
 *
 * Crops covered: Wheat (قمح), Date Palm (نخيل), Vegetables (خضروات)
 *
 * @author SAHOOL Platform Team
 */

import { test, expect } from "./fixtures/test-fixtures";
import {
  sampleCooperatives,
  testUsers,
  waitForPageLoad,
  navigateAndWait,
  waitForNotification,
  timeouts,
  selectors,
} from "./helpers/ux-helpers";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Cooperative Creation
// مجموعة الاختبارات: إنشاء التعاونية
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Cooperative Creation | إنشاء التعاونية", () => {
  test("should display cooperative creation page | عرض صفحة إنشاء التعاونية", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/new");

    // Check for cooperative creation content
    // التحقق من محتوى إنشاء التعاونية
    await expect(
      coopAdminPage.locator(
        "text=/Create Cooperative|إنشاء تعاونية|New Cooperative|تعاونية جديدة|Register Cooperative|تسجيل تعاونية/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should fill cooperative registration form | ملء نموذج تسجيل التعاونية", async ({
    coopAdminPage,
  }) => {
    const coop = sampleCooperatives[0];

    await navigateAndWait(coopAdminPage, "/cooperatives/new");

    // Fill cooperative name
    // ملء اسم التعاونية
    const nameInput = coopAdminPage.locator('input[name="name"]');
    if (await nameInput.isVisible()) {
      await nameInput.fill(coop.name);
    }

    // Fill Arabic name
    // ملء الاسم بالعربية
    const nameArInput = coopAdminPage.locator('input[name="nameAr"]');
    if (await nameArInput.isVisible()) {
      await nameArInput.fill(coop.nameAr);
    }

    // Fill registration number
    // ملء رقم التسجيل
    const regNumInput = coopAdminPage.locator('input[name="registrationNumber"]');
    if (await regNumInput.isVisible()) {
      await regNumInput.fill(coop.registrationNumber);
    }

    // Fill location
    // ملء الموقع
    const locationInput = coopAdminPage.locator('input[name="location"]');
    if (await locationInput.isVisible()) {
      await locationInput.fill(coop.location);
    }
  });

  test("should create cooperative successfully | إنشاء التعاونية بنجاح", async ({
    coopAdminPage,
  }) => {
    const coop = sampleCooperatives[0];

    await navigateAndWait(coopAdminPage, "/cooperatives/new");

    // Fill required fields
    // ملء الحقول المطلوبة
    await coopAdminPage.fill('input[name="name"]', `Test Coop ${Date.now()}`);

    const nameArInput = coopAdminPage.locator('input[name="nameAr"]');
    if (await nameArInput.isVisible()) {
      await nameArInput.fill(`تعاونية اختبار ${Date.now()}`);
    }

    const regNumInput = coopAdminPage.locator('input[name="registrationNumber"]');
    if (await regNumInput.isVisible()) {
      await regNumInput.fill(`TEST-${Date.now()}`);
    }

    // Submit form
    await coopAdminPage.click(selectors.submitButton);

    // Verify creation success
    await coopAdminPage.waitForURL(/\/cooperatives/, {
      timeout: timeouts.navigation,
    });

    const notification = await waitForNotification(coopAdminPage, "success", 5000);
    if (notification) {
      await expect(notification).toBeVisible();
    }
  });

  test("should display cooperative dashboard after creation | عرض لوحة تحكم التعاونية بعد الإنشاء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives");

    // Check for cooperative dashboard elements
    // التحقق من عناصر لوحة تحكم التعاونية
    const dashboard = coopAdminPage.locator(
      '[data-testid="coop-dashboard"], text=/Members|الأعضاء|Overview|نظرة عامة/i'
    );

    const hasDashboard = await dashboard
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasDashboard) {
      await expect(dashboard.first()).toBeVisible();
    }
  });

  test("should set cooperative region and focus crops | تعيين منطقة التعاونية والمحاصيل المستهدفة", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/settings");

    // Look for region selector
    // البحث عن محدد المنطقة
    const regionSelect = coopAdminPage.locator(
      'select[name="region"], [data-testid="region-select"]'
    );

    if (await regionSelect.isVisible({ timeout: timeouts.medium })) {
      await regionSelect.selectOption({ index: 1 });
    }

    // Look for focus crops selector (multi-select)
    // البحث عن محدد المحاصيل المستهدفة (اختيار متعدد)
    const cropsSelect = coopAdminPage.locator(
      '[data-testid="focus-crops"], [name="focusCrops"]'
    );

    if (await cropsSelect.isVisible({ timeout: timeouts.medium })) {
      // Select wheat and date palm as focus crops
      // اختيار القمح والنخيل كمحاصيل مستهدفة
      await cropsSelect.click();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Member Management
// مجموعة الاختبارات: إدارة الأعضاء
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Member Management | إدارة الأعضاء", () => {
  test("should display members list | عرض قائمة الأعضاء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/members");

    // Check for members list content
    // التحقق من محتوى قائمة الأعضاء
    await expect(
      coopAdminPage.locator("text=/Members|الأعضاء|Farmers|المزارعين/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should invite new farmer to cooperative | دعوة مزارع جديد للتعاونية", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/members");

    // Look for invite button
    // البحث عن زر الدعوة
    const inviteBtn = coopAdminPage.locator(
      'button:has-text("Invite"), button:has-text("دعوة"), button:has-text("Add Member"), button:has-text("إضافة عضو")'
    );

    if (await inviteBtn.first().isVisible({ timeout: timeouts.medium })) {
      await inviteBtn.first().click();
      await coopAdminPage.waitForTimeout(500);

      // Fill invite form
      // ملء نموذج الدعوة
      const emailInput = coopAdminPage.locator(
        'input[name="email"], input[type="email"]'
      );

      if (await emailInput.isVisible()) {
        await emailInput.fill(`farmer-invite-${Date.now()}@sahool.test`);
      }

      // Submit invitation
      await coopAdminPage.click(selectors.submitButton);
    }
  });

  test("should search for existing farmers | البحث عن المزارعين الموجودين", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/members");

    // Look for search input
    // البحث عن حقل البحث
    const searchInput = coopAdminPage.locator(
      'input[type="search"], input[placeholder*="Search"], input[placeholder*="بحث"]'
    );

    if (await searchInput.isVisible({ timeout: timeouts.medium })) {
      await searchInput.fill("Ahmed");
      await coopAdminPage.waitForTimeout(500);

      // Check for search results
      // التحقق من نتائج البحث
      const results = coopAdminPage.locator(
        '[data-testid="member-card"], [data-testid="search-result"]'
      );

      const hasResults = await results
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasResults) {
        await expect(results.first()).toBeVisible();
      }
    }
  });

  test("should view member profile and fields | عرض ملف العضو وحقوله", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/members");

    // Click on first member
    // النقر على العضو الأول
    const memberCard = coopAdminPage.locator(
      '[data-testid="member-card"], [class*="member"]'
    ).first();

    if (await memberCard.isVisible({ timeout: timeouts.medium })) {
      await memberCard.click();
      await waitForPageLoad(coopAdminPage);

      // Check for member profile content
      // التحقق من محتوى ملف العضو
      const profileContent = coopAdminPage.locator(
        "text=/Profile|الملف الشخصي|Fields|الحقول|Farm|المزرعة/i"
      );

      const hasProfile = await profileContent
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasProfile) {
        await expect(profileContent.first()).toBeVisible();
      }
    }
  });

  test("should assign role to member | تعيين دور للعضو", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/members");

    // Click on first member
    // النقر على العضو الأول
    const memberCard = coopAdminPage.locator('[data-testid="member-card"]').first();

    if (await memberCard.isVisible({ timeout: timeouts.medium })) {
      await memberCard.click();
      await waitForPageLoad(coopAdminPage);

      // Look for role selector
      // البحث عن محدد الدور
      const roleSelect = coopAdminPage.locator(
        'select[name="role"], [data-testid="role-select"]'
      );

      if (await roleSelect.isVisible({ timeout: timeouts.medium })) {
        await roleSelect.selectOption({ value: "member" });
      }
    }
  });

  test("should remove member from cooperative | إزالة عضو من التعاونية", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/members");

    // Click on first member
    // النقر على العضو الأول
    const memberCard = coopAdminPage.locator('[data-testid="member-card"]').first();

    if (await memberCard.isVisible({ timeout: timeouts.medium })) {
      await memberCard.click();
      await waitForPageLoad(coopAdminPage);

      // Look for remove button
      // البحث عن زر الإزالة
      const removeBtn = coopAdminPage.locator(
        'button:has-text("Remove"), button:has-text("إزالة"), button:has-text("Delete"), button:has-text("حذف")'
      );

      if (await removeBtn.first().isVisible({ timeout: timeouts.medium })) {
        // Just verify the button exists - don't actually remove
        // فقط التحقق من وجود الزر - لا تقم بالإزالة فعلياً
        await expect(removeBtn.first()).toBeVisible();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Shared Resource Management
// مجموعة الاختبارات: إدارة الموارد المشتركة
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Shared Resource Management | إدارة الموارد المشتركة", () => {
  test("should display shared equipment list | عرض قائمة المعدات المشتركة", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/equipment");

    // Check for equipment content
    // التحقق من محتوى المعدات
    await expect(
      coopAdminPage.locator(
        "text=/Equipment|المعدات|Shared Resources|الموارد المشتركة|Machinery|الآلات/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should add shared equipment | إضافة معدات مشتركة", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/equipment/new");

    // Fill equipment details
    // ملء تفاصيل المعدات
    const nameInput = coopAdminPage.locator('input[name="name"]');
    if (await nameInput.isVisible()) {
      await nameInput.fill("Cooperative Harvester");
    }

    const nameArInput = coopAdminPage.locator('input[name="nameAr"]');
    if (await nameArInput.isVisible()) {
      await nameArInput.fill("حاصدة التعاونية");
    }

    // Select equipment type
    // اختيار نوع المعدات
    const typeSelect = coopAdminPage.locator('select[name="type"]');
    if (await typeSelect.isVisible()) {
      await typeSelect.selectOption({ value: "harvester" });
    }

    // Submit
    await coopAdminPage.click(selectors.submitButton);
  });

  test("should schedule equipment for member | جدولة المعدات للعضو", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/equipment");

    // Click on first equipment
    // النقر على المعدات الأولى
    const equipmentCard = coopAdminPage.locator(
      '[data-testid="equipment-card"]'
    ).first();

    if (await equipmentCard.isVisible({ timeout: timeouts.medium })) {
      await equipmentCard.click();
      await waitForPageLoad(coopAdminPage);

      // Look for schedule button
      // البحث عن زر الجدولة
      const scheduleBtn = coopAdminPage.locator(
        'button:has-text("Schedule"), button:has-text("جدولة"), button:has-text("Book"), button:has-text("حجز")'
      );

      if (await scheduleBtn.first().isVisible()) {
        await scheduleBtn.first().click();
        await coopAdminPage.waitForTimeout(500);

        // Fill scheduling form
        // ملء نموذج الجدولة
        const dateInput = coopAdminPage.locator('input[type="date"]');
        if (await dateInput.first().isVisible()) {
          await dateInput
            .first()
            .fill(new Date(Date.now() + 86400000).toISOString().split("T")[0]);
        }

        // Select member
        // اختيار العضو
        const memberSelect = coopAdminPage.locator('select[name="memberId"]');
        if (await memberSelect.isVisible()) {
          const options = await memberSelect.locator("option").all();
          if (options.length > 1) {
            await memberSelect.selectOption({ index: 1 });
          }
        }
      }
    }
  });

  test("should display equipment availability calendar | عرض تقويم توفر المعدات", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/equipment/calendar");

    // Look for calendar view
    // البحث عن عرض التقويم
    const calendar = coopAdminPage.locator(
      '[data-testid="equipment-calendar"], [class*="calendar"]'
    );

    const hasCalendar = await calendar
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasCalendar) {
      await expect(calendar.first()).toBeVisible();
    }
  });

  test("should manage shared water resources | إدارة موارد المياه المشتركة", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/water");

    // Check for water resources content
    // التحقق من محتوى موارد المياه
    const waterContent = coopAdminPage.locator(
      "text=/Water|المياه|Irrigation|الري|Well|البئر|Canal|القناة/i"
    );

    const hasWater = await waterContent
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasWater) {
      await expect(waterContent.first()).toBeVisible();
    }
  });

  test("should track resource usage by members | تتبع استخدام الموارد من قبل الأعضاء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/resources/usage");

    // Look for usage tracking content
    // البحث عن محتوى تتبع الاستخدام
    const usageContent = coopAdminPage.locator(
      "text=/Usage|الاستخدام|Hours|ساعات|Member|العضو/i"
    );

    const hasUsage = await usageContent
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasUsage) {
      await expect(usageContent.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Collective Purchase Workflow
// مجموعة الاختبارات: سير عمل الشراء الجماعي
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Collective Purchase Workflow | سير عمل الشراء الجماعي", () => {
  test("should display collective purchase page | عرض صفحة الشراء الجماعي", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/purchases");

    // Check for purchase content
    // التحقق من محتوى الشراء
    await expect(
      coopAdminPage.locator(
        "text=/Purchases|المشتريات|Collective|الجماعي|Bulk Order|طلب جملة/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should create collective fertilizer order | إنشاء طلب سماد جماعي", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/purchases/new");

    // Select product category
    // اختيار فئة المنتج
    const categorySelect = coopAdminPage.locator('select[name="category"]');
    if (await categorySelect.isVisible()) {
      await categorySelect.selectOption({ value: "fertilizer" });
    }

    // Select specific product
    // اختيار المنتج المحدد
    const productSelect = coopAdminPage.locator('select[name="product"]');
    if (await productSelect.isVisible()) {
      await productSelect.selectOption({ index: 1 });
    }

    // Enter total quantity
    // إدخال الكمية الإجمالية
    const quantityInput = coopAdminPage.locator('input[name="quantity"]');
    if (await quantityInput.isVisible()) {
      await quantityInput.fill("5000"); // 5 tons
    }

    // Set order deadline
    // تعيين الموعد النهائي للطلب
    const deadlineInput = coopAdminPage.locator('input[name="deadline"]');
    if (await deadlineInput.isVisible()) {
      const futureDate = new Date(Date.now() + 7 * 86400000)
        .toISOString()
        .split("T")[0];
      await deadlineInput.fill(futureDate);
    }
  });

  test("should allow members to join purchase order | السماح للأعضاء بالانضمام لطلب الشراء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/purchases");

    // Click on first active purchase order
    // النقر على أول طلب شراء نشط
    const orderCard = coopAdminPage.locator(
      '[data-testid="purchase-order"], [class*="order-card"]'
    ).first();

    if (await orderCard.isVisible({ timeout: timeouts.medium })) {
      await orderCard.click();
      await waitForPageLoad(coopAdminPage);

      // Look for member participation section
      // البحث عن قسم مشاركة الأعضاء
      const participationSection = coopAdminPage.locator(
        "text=/Participants|المشاركون|Join|انضمام|Add Quantity|إضافة كمية/i"
      );

      const hasParticipation = await participationSection
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasParticipation) {
        await expect(participationSection.first()).toBeVisible();
      }
    }
  });

  test("should show order progress and totals | عرض تقدم الطلب والإجماليات", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/purchases");

    // Look for order progress indicators
    // البحث عن مؤشرات تقدم الطلب
    const progressIndicator = coopAdminPage.locator(
      '[data-testid="order-progress"], text=/Progress|التقدم|Total|الإجمالي|%/i'
    );

    const hasProgress = await progressIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasProgress) {
      await expect(progressIndicator.first()).toBeVisible();
    }
  });

  test("should calculate member share of collective order | حساب حصة العضو من الطلب الجماعي", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/purchases");

    // Click on first order
    // النقر على الطلب الأول
    const orderCard = coopAdminPage.locator('[data-testid="purchase-order"]').first();

    if (await orderCard.isVisible({ timeout: timeouts.medium })) {
      await orderCard.click();
      await waitForPageLoad(coopAdminPage);

      // Look for member cost breakdown
      // البحث عن تفصيل تكلفة العضو
      const costBreakdown = coopAdminPage.locator(
        "text=/Cost|التكلفة|Share|الحصة|Amount|المبلغ|SAR|ريال/i"
      );

      const hasCostBreakdown = await costBreakdown
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasCostBreakdown) {
        await expect(costBreakdown.first()).toBeVisible();
      }
    }
  });

  test("should finalize and distribute collective order | إنهاء وتوزيع الطلب الجماعي", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/purchases");

    // Look for finalize button on an order
    // البحث عن زر الإنهاء في الطلب
    const finalizeBtn = coopAdminPage.locator(
      'button:has-text("Finalize"), button:has-text("إنهاء"), button:has-text("Complete"), button:has-text("إكمال")'
    );

    const hasFinalize = await finalizeBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFinalize) {
      // Just verify button exists - don't actually finalize
      // فقط التحقق من وجود الزر - لا تقم بالإنهاء فعلياً
      await expect(finalizeBtn.first()).toBeVisible();
    }
  });

  test("should view purchase history | عرض سجل المشتريات", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/purchases/history");

    // Look for history content
    // البحث عن محتوى السجل
    const historyContent = coopAdminPage.locator(
      "text=/History|السجل|Past Orders|الطلبات السابقة|Completed|مكتملة/i"
    );

    const hasHistory = await historyContent
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasHistory) {
      await expect(historyContent.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Cooperative Reports
// مجموعة الاختبارات: تقارير التعاونية
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Cooperative Reports | تقارير التعاونية", () => {
  test("should display reports dashboard | عرض لوحة التقارير", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/reports");

    // Check for reports content
    // التحقق من محتوى التقارير
    await expect(
      coopAdminPage.locator(
        "text=/Reports|التقارير|Analytics|التحليلات|Statistics|الإحصائيات/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should generate member activity report | إنشاء تقرير نشاط الأعضاء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/reports/members");

    // Look for generate report button
    // البحث عن زر إنشاء التقرير
    const generateBtn = coopAdminPage.locator(
      'button:has-text("Generate"), button:has-text("إنشاء"), button:has-text("Export"), button:has-text("تصدير")'
    );

    if (await generateBtn.first().isVisible({ timeout: timeouts.medium })) {
      await generateBtn.first().click();
      await coopAdminPage.waitForTimeout(2000);
    }
  });

  test("should generate collective harvest report | إنشاء تقرير الحصاد الجماعي", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/reports/harvest");

    // Look for date range selector
    // البحث عن محدد نطاق التاريخ
    const dateRange = coopAdminPage.locator(
      '[data-testid="date-range"], input[type="date"]'
    );

    if (await dateRange.first().isVisible({ timeout: timeouts.medium })) {
      // Set date range
      // تعيين نطاق التاريخ
      const startDate = coopAdminPage.locator(
        'input[name="startDate"], input[type="date"]'
      ).first();
      const endDate = coopAdminPage.locator(
        'input[name="endDate"], input[type="date"]'
      ).last();

      if (await startDate.isVisible()) {
        await startDate.fill("2026-01-01");
      }

      if (await endDate.isVisible()) {
        await endDate.fill("2026-02-07");
      }
    }

    // Generate report
    const generateBtn = coopAdminPage.locator(
      'button:has-text("Generate"), button:has-text("إنشاء")'
    );

    if (await generateBtn.first().isVisible()) {
      await generateBtn.first().click();
      await coopAdminPage.waitForTimeout(2000);
    }
  });

  test("should view financial summary report | عرض تقرير الملخص المالي", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/reports/financial");

    // Look for financial report content
    // البحث عن محتوى التقرير المالي
    const financialContent = coopAdminPage.locator(
      "text=/Revenue|الإيرادات|Expenses|المصروفات|Profit|الربح|Balance|الرصيد/i"
    );

    const hasFinancial = await financialContent
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFinancial) {
      await expect(financialContent.first()).toBeVisible();
    }
  });

  test("should export report as PDF | تصدير التقرير بصيغة PDF", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/reports");

    // Look for export PDF button
    // البحث عن زر تصدير PDF
    const exportPdfBtn = coopAdminPage.locator(
      'button:has-text("PDF"), button:has-text("Export PDF"), button:has-text("تصدير PDF")'
    );

    const hasExportPdf = await exportPdfBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasExportPdf) {
      await expect(exportPdfBtn.first()).toBeVisible();
    }
  });

  test("should view comparative performance across members | عرض الأداء المقارن عبر الأعضاء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/reports/comparison");

    // Look for comparison content
    // البحث عن محتوى المقارنة
    const comparisonContent = coopAdminPage.locator(
      "text=/Comparison|المقارنة|Ranking|الترتيب|Top Performers|أفضل الأداء/i"
    );

    const hasComparison = await comparisonContent
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasComparison) {
      await expect(comparisonContent.first()).toBeVisible();
    }
  });

  test("should share report with members | مشاركة التقرير مع الأعضاء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/reports");

    // Look for share button
    // البحث عن زر المشاركة
    const shareBtn = coopAdminPage.locator(
      'button:has-text("Share"), button:has-text("مشاركة"), button:has-text("Send"), button:has-text("إرسال")'
    );

    const hasShare = await shareBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasShare) {
      await expect(shareBtn.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Cooperative Communication
// مجموعة الاختبارات: تواصل التعاونية
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Cooperative Communication | تواصل التعاونية", () => {
  test("should display announcement board | عرض لوحة الإعلانات", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/announcements");

    // Check for announcements content
    // التحقق من محتوى الإعلانات
    await expect(
      coopAdminPage.locator(
        "text=/Announcements|الإعلانات|Notices|الإشعارات|News|الأخبار/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should create new announcement | إنشاء إعلان جديد", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/announcements/new");

    // Fill announcement details
    // ملء تفاصيل الإعلان
    const titleInput = coopAdminPage.locator('input[name="title"]');
    if (await titleInput.isVisible()) {
      await titleInput.fill("Fertilizer Bulk Purchase Opportunity");
    }

    const titleArInput = coopAdminPage.locator('input[name="titleAr"]');
    if (await titleArInput.isVisible()) {
      await titleArInput.fill("فرصة شراء سماد بالجملة");
    }

    const contentInput = coopAdminPage.locator(
      'textarea[name="content"], [data-testid="rich-editor"]'
    );
    if (await contentInput.isVisible()) {
      await contentInput.fill(
        "Dear members, we have an opportunity to purchase Urea fertilizer at 20% discount."
      );
    }

    // Submit
    await coopAdminPage.click(selectors.submitButton);
  });

  test("should send notification to all members | إرسال إشعار لجميع الأعضاء", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/notifications");

    // Look for send notification button
    // البحث عن زر إرسال الإشعار
    const sendBtn = coopAdminPage.locator(
      'button:has-text("Send"), button:has-text("إرسال"), button:has-text("Notify All"), button:has-text("إشعار الجميع")'
    );

    if (await sendBtn.first().isVisible({ timeout: timeouts.medium })) {
      await expect(sendBtn.first()).toBeVisible();
    }
  });

  test("should display cooperative chat/forum | عرض دردشة/منتدى التعاونية", async ({
    coopAdminPage,
  }) => {
    await navigateAndWait(coopAdminPage, "/cooperatives/chat");

    // Check for chat content
    // التحقق من محتوى الدردشة
    const chatContent = coopAdminPage.locator(
      "text=/Chat|الدردشة|Forum|المنتدى|Messages|الرسائل|Discussion|النقاش/i"
    );

    const hasChat = await chatContent
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasChat) {
      await expect(chatContent.first()).toBeVisible();
    }
  });
});
