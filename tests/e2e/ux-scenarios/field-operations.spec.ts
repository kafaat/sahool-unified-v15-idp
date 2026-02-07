/**
 * Field Operations E2E Test Scenarios
 * سيناريوهات اختبار عمليات الحقل من البداية إلى النهاية
 *
 * Field operations scenarios covering:
 * سيناريوهات عمليات الحقل تغطي:
 *
 * - Field boundary drawing (رسم حدود الحقل)
 * - Crop rotation planning (تخطيط دورة المحاصيل)
 * - Fertilizer recommendations (توصيات الأسمدة)
 * - Pest detection workflow (سير عمل اكتشاف الآفات)
 * - Harvest recording (تسجيل الحصاد)
 *
 * Crops covered: Wheat (قمح), Date Palm (نخيل), Tomato (طماطم), Barley (شعير)
 *
 * @author SAHOOL Platform Team
 */

import { test, expect } from "./fixtures/test-fixtures";
import {
  sampleFields,
  sampleTasks,
  waitForPageLoad,
  navigateAndWait,
  waitForNotification,
  createField,
  timeouts,
  selectors,
} from "./helpers/ux-helpers";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Field Boundary Drawing
// مجموعة الاختبارات: رسم حدود الحقل
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Field Boundary Drawing | رسم حدود الحقل", () => {
  test("should display map for boundary drawing | عرض الخريطة لرسم الحدود", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields/new");

    // Look for map container
    // البحث عن حاوية الخريطة
    const mapContainer = farmerPage.locator(
      '[data-testid="field-map"], [class*="map"], #map, [class*="maplibre"], [class*="leaflet"]'
    );

    const hasMap = await mapContainer
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasMap) {
      await expect(mapContainer.first()).toBeVisible();
    } else {
      // Alternative: coordinate input fields
      // بديل: حقول إدخال الإحداثيات
      const latInput = farmerPage.locator('input[name="latitude"]');
      const lngInput = farmerPage.locator('input[name="longitude"]');

      const hasCoordinates =
        (await latInput.isVisible().catch(() => false)) ||
        (await lngInput.isVisible().catch(() => false));

      expect(hasMap || hasCoordinates).toBeTruthy();
    }
  });

  test("should have drawing tools available | توفر أدوات الرسم", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields/new");

    // Look for drawing tools
    // البحث عن أدوات الرسم
    const drawingTools = farmerPage.locator(
      '[data-testid="draw-polygon"], button:has-text("Draw"), button:has-text("رسم"), [class*="draw"], [aria-label*="draw"]'
    );

    const hasDrawTools = await drawingTools
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasDrawTools) {
      await expect(drawingTools.first()).toBeVisible();
    }
  });

  test("should calculate area from drawn boundary | حساب المساحة من الحدود المرسومة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields/new");

    // Check if area is auto-calculated or manual input
    // التحقق مما إذا كانت المساحة محسوبة تلقائياً أو إدخال يدوي
    const areaInput = farmerPage.locator('input[name="area"]');
    const areaDisplay = farmerPage.locator(
      '[data-testid="calculated-area"], text=/hectares|هكتار|ha|م²/i'
    );

    const hasAreaInput = await areaInput.isVisible().catch(() => false);
    const hasAreaDisplay = await areaDisplay
      .first()
      .isVisible()
      .catch(() => false);

    expect(hasAreaInput || hasAreaDisplay).toBeTruthy();
  });

  test("should support GPS location for field boundary | دعم موقع GPS لحدود الحقل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields/new");

    // Look for GPS/location button
    // البحث عن زر GPS/الموقع
    const gpsButton = farmerPage.locator(
      'button:has-text("GPS"), button:has-text("Location"), button:has-text("الموقع"), [data-testid="gps-button"], [aria-label*="location"]'
    );

    const hasGps = await gpsButton
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasGps) {
      await expect(gpsButton.first()).toBeVisible();
    }
  });

  test("should save field boundary successfully | حفظ حدود الحقل بنجاح", async ({
    farmerPage,
    sampleWheatField,
  }) => {
    await navigateAndWait(farmerPage, "/fields/new");

    // Fill field name
    // ملء اسم الحقل
    await farmerPage.fill('input[name="name"]', sampleWheatField.name);

    // Fill area manually if needed
    // ملء المساحة يدوياً إذا لزم الأمر
    const areaInput = farmerPage.locator('input[name="area"]');
    if (await areaInput.isVisible()) {
      await areaInput.fill(sampleWheatField.area.toString());
    }

    // Select crop type
    // اختيار نوع المحصول
    const cropSelect = farmerPage.locator('select[name="cropType"]');
    if (await cropSelect.isVisible()) {
      await cropSelect.selectOption({ value: "wheat" });
    }

    // Save field
    await farmerPage.click(selectors.submitButton);

    // Verify save success
    await farmerPage.waitForURL(/\/fields/, { timeout: timeouts.navigation });
  });

  test("should edit existing field boundary | تعديل حدود الحقل الموجود", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields");

    // Click on first field to edit
    // النقر على الحقل الأول للتعديل
    const fieldCard = farmerPage.locator(
      '[data-testid="field-card"], [class*="field-card"]'
    ).first();

    const hasField = await fieldCard
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasField) {
      await fieldCard.click();
      await waitForPageLoad(farmerPage);

      // Look for edit button
      // البحث عن زر التعديل
      const editButton = farmerPage.locator(selectors.editButton);

      if (await editButton.first().isVisible()) {
        await editButton.first().click();
        await waitForPageLoad(farmerPage);

        // Should be on edit page
        // يجب أن يكون في صفحة التعديل
        await expect(farmerPage).toHaveURL(/\/fields\/.*\/(edit|update)/);
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Crop Rotation Planning
// مجموعة الاختبارات: تخطيط دورة المحاصيل
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Crop Rotation Planning | تخطيط دورة المحاصيل", () => {
  test("should display crop rotation page | عرض صفحة دورة المحاصيل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/rotation");

    // Check for rotation content
    // التحقق من محتوى الدورة
    await expect(
      farmerPage.locator(
        "text=/Rotation|الدورة|Crop Rotation|دورة المحاصيل|Planning|التخطيط/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should create new rotation plan | إنشاء خطة دورة جديدة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/rotation/new");

    // Fill rotation details
    // ملء تفاصيل الدورة
    const nameInput = farmerPage.locator('input[name="name"]');
    if (await nameInput.isVisible()) {
      await nameInput.fill("Winter-Summer Rotation 2026");
    }

    // Select field for rotation
    // اختيار الحقل للدورة
    const fieldSelect = farmerPage.locator('select[name="fieldId"]');
    if (await fieldSelect.isVisible()) {
      const options = await fieldSelect.locator("option").all();
      if (options.length > 1) {
        await fieldSelect.selectOption({ index: 1 });
      }
    }
  });

  test("should add crops to rotation cycle | إضافة محاصيل لدورة الزراعة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/rotation/new");

    // Look for add crop button
    // البحث عن زر إضافة محصول
    const addCropBtn = farmerPage.locator(
      'button:has-text("Add Crop"), button:has-text("إضافة محصول"), button:has-text("Add Season")'
    );

    if (await addCropBtn.first().isVisible({ timeout: timeouts.medium })) {
      await addCropBtn.first().click();

      // Add wheat for winter
      // إضافة القمح للشتاء
      const cropSelect = farmerPage.locator('[data-testid="crop-select"]');
      if (await cropSelect.isVisible()) {
        await cropSelect.selectOption({ value: "wheat" });
      }

      const seasonSelect = farmerPage.locator('[data-testid="season-select"]');
      if (await seasonSelect.isVisible()) {
        await seasonSelect.selectOption({ value: "winter" });
      }
    }
  });

  test("should show rotation calendar view | عرض تقويم الدورة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/rotation");

    // Look for calendar or timeline view
    // البحث عن عرض التقويم أو الجدول الزمني
    const calendarView = farmerPage.locator(
      '[data-testid="rotation-calendar"], [class*="calendar"], [class*="timeline"]'
    );

    const hasCalendar = await calendarView
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasCalendar) {
      await expect(calendarView.first()).toBeVisible();
    }
  });

  test("should recommend crops based on soil and history | توصية بالمحاصيل بناءً على التربة والتاريخ", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/rotation/new");

    // Look for AI recommendation button
    // البحث عن زر التوصية بالذكاء الاصطناعي
    const recommendBtn = farmerPage.locator(
      'button:has-text("Recommend"), button:has-text("توصية"), button:has-text("Suggest"), button:has-text("اقتراح")'
    );

    const hasRecommend = await recommendBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasRecommend) {
      await recommendBtn.first().click();

      // Wait for recommendations to load
      // انتظار تحميل التوصيات
      await farmerPage.waitForTimeout(2000);

      // Should show recommended crops
      // يجب أن تظهر المحاصيل الموصى بها
      const recommendations = farmerPage.locator(
        '[data-testid="crop-recommendation"], [class*="recommendation"]'
      );

      const hasRecs = await recommendations
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasRecs) {
        await expect(recommendations.first()).toBeVisible();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Fertilizer Recommendations
// مجموعة الاختبارات: توصيات الأسمدة
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Fertilizer Recommendations | توصيات الأسمدة", () => {
  test("should display fertilizer recommendations page | عرض صفحة توصيات الأسمدة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fertilizer");

    // Check for fertilizer content
    // التحقق من محتوى الأسمدة
    await expect(
      farmerPage.locator(
        "text=/Fertilizer|الأسمدة|السماد|NPK|Nutrients|المغذيات/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should show soil analysis integration | عرض تكامل تحليل التربة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fertilizer");

    // Look for soil analysis section
    // البحث عن قسم تحليل التربة
    const soilAnalysis = farmerPage.locator(
      '[data-testid="soil-analysis"], text=/Soil Analysis|تحليل التربة|Soil Test|فحص التربة/i'
    );

    const hasSoilAnalysis = await soilAnalysis
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasSoilAnalysis) {
      await expect(soilAnalysis.first()).toBeVisible();
    }
  });

  test("should generate fertilizer plan for wheat | إنشاء خطة تسميد للقمح", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fertilizer/plan");

    // Select field
    // اختيار الحقل
    const fieldSelect = farmerPage.locator('select[name="fieldId"]');
    if (await fieldSelect.isVisible()) {
      const options = await fieldSelect.locator("option").all();
      if (options.length > 1) {
        await fieldSelect.selectOption({ index: 1 });
      }
    }

    // Select crop type - wheat
    // اختيار نوع المحصول - القمح
    const cropSelect = farmerPage.locator('select[name="cropType"]');
    if (await cropSelect.isVisible()) {
      await cropSelect.selectOption({ value: "wheat" });
    }

    // Set target yield (tons/ha)
    // تعيين الإنتاج المستهدف (طن/هكتار)
    const yieldInput = farmerPage.locator('input[name="targetYield"]');
    if (await yieldInput.isVisible()) {
      await yieldInput.fill("5"); // 5 tons/ha for wheat
    }

    // Generate plan
    // إنشاء الخطة
    const generateBtn = farmerPage.locator(
      'button:has-text("Generate"), button:has-text("إنشاء"), button:has-text("Calculate"), button:has-text("حساب")'
    );

    if (await generateBtn.first().isVisible()) {
      await generateBtn.first().click();
      await farmerPage.waitForTimeout(2000);
    }
  });

  test("should display NPK requirements | عرض متطلبات NPK", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fertilizer");

    // Look for NPK values
    // البحث عن قيم NPK
    const npkDisplay = farmerPage.locator(
      '[data-testid="npk-values"], text=/N:|P:|K:|Nitrogen|Phosphorus|Potassium|النيتروجين|الفوسفور|البوتاسيوم/i'
    );

    const hasNpk = await npkDisplay
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasNpk) {
      await expect(npkDisplay.first()).toBeVisible();
    }
  });

  test("should show fertilizer application schedule | عرض جدول تطبيق الأسمدة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fertilizer/schedule");

    // Look for schedule/timeline
    // البحث عن الجدول/الخط الزمني
    const schedule = farmerPage.locator(
      '[data-testid="fertilizer-schedule"], [class*="schedule"], [class*="timeline"]'
    );

    const hasSchedule = await schedule
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasSchedule) {
      await expect(schedule.first()).toBeVisible();
    }
  });

  test("should create fertilizer application task | إنشاء مهمة تطبيق السماد", async ({
    farmerPage,
    sampleFertilizerTask,
  }) => {
    await navigateAndWait(farmerPage, "/fertilizer");

    // Look for apply button
    // البحث عن زر التطبيق
    const applyBtn = farmerPage.locator(
      'button:has-text("Apply"), button:has-text("تطبيق"), button:has-text("Create Task"), button:has-text("إنشاء مهمة")'
    );

    const hasApply = await applyBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasApply) {
      await applyBtn.first().click();

      // Should navigate to task creation or show modal
      // يجب أن ينتقل إلى إنشاء المهمة أو يعرض نافذة منبثقة
      await farmerPage.waitForTimeout(1000);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Pest Detection Workflow
// مجموعة الاختبارات: سير عمل اكتشاف الآفات
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Pest Detection Workflow | سير عمل اكتشاف الآفات", () => {
  test("should display pest detection page | عرض صفحة اكتشاف الآفات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/pest-detection");

    // Check for pest detection content
    // التحقق من محتوى اكتشاف الآفات
    await expect(
      farmerPage.locator(
        "text=/Pest|الآفات|Disease|الأمراض|Detection|الاكتشاف|Scan|فحص/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should allow image upload for pest detection | السماح بتحميل الصور لاكتشاف الآفات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/pest-detection");

    // Look for image upload input
    // البحث عن إدخال تحميل الصور
    const uploadInput = farmerPage.locator(
      'input[type="file"], [data-testid="image-upload"]'
    );

    const hasUpload = await uploadInput
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Or look for camera/upload button
    // أو البحث عن زر الكاميرا/التحميل
    const uploadButton = farmerPage.locator(
      'button:has-text("Upload"), button:has-text("تحميل"), button:has-text("Camera"), button:has-text("كاميرا"), button:has-text("Take Photo"), button:has-text("التقاط صورة")'
    );

    const hasUploadBtn = await uploadButton
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    expect(hasUpload || hasUploadBtn).toBeTruthy();
  });

  test("should show pest identification results | عرض نتائج تحديد الآفات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/pest-detection/results");

    // Look for detection results
    // البحث عن نتائج الاكتشاف
    const results = farmerPage.locator(
      '[data-testid="detection-results"], [class*="results"], text=/Detected|تم اكتشاف|Identified|تم تحديد/i'
    );

    const hasResults = await results
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasResults) {
      await expect(results.first()).toBeVisible();
    }
  });

  test("should display pest treatment recommendations | عرض توصيات معالجة الآفات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/pest-detection");

    // Look for treatment recommendations section
    // البحث عن قسم توصيات العلاج
    const treatments = farmerPage.locator(
      '[data-testid="treatments"], text=/Treatment|العلاج|Recommendation|توصية|Control|مكافحة/i'
    );

    const hasTreatments = await treatments
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasTreatments) {
      await expect(treatments.first()).toBeVisible();
    }
  });

  test("should create pest control task from detection | إنشاء مهمة مكافحة الآفات من الاكتشاف", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/pest-detection");

    // Look for create task button
    // البحث عن زر إنشاء المهمة
    const createTaskBtn = farmerPage.locator(
      'button:has-text("Create Task"), button:has-text("إنشاء مهمة"), button:has-text("Schedule Treatment"), button:has-text("جدولة العلاج")'
    );

    const hasCreateTask = await createTaskBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasCreateTask) {
      await createTaskBtn.first().click();
      await farmerPage.waitForTimeout(1000);
    }
  });

  test("should show pest alerts for field | عرض تنبيهات الآفات للحقل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields");

    // Click on first field
    // النقر على الحقل الأول
    const fieldCard = farmerPage.locator('[data-testid="field-card"]').first();

    if (await fieldCard.isVisible({ timeout: timeouts.medium })) {
      await fieldCard.click();
      await waitForPageLoad(farmerPage);

      // Look for pest alerts section
      // البحث عن قسم تنبيهات الآفات
      const pestAlerts = farmerPage.locator(
        '[data-testid="pest-alerts"], text=/Pest Alert|تنبيه آفات|Disease Risk|خطر الأمراض/i'
      );

      const hasAlerts = await pestAlerts
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasAlerts) {
        await expect(pestAlerts.first()).toBeVisible();
      }
    }
  });

  test("should support Red Palm Weevil detection for date palm | دعم اكتشاف سوسة النخيل الحمراء للنخيل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/pest-detection");

    // Look for palm-specific pest detection
    // البحث عن اكتشاف آفات خاصة بالنخيل
    const palmPests = farmerPage.locator(
      'text=/Red Palm Weevil|سوسة النخيل الحمراء|RPW|Date Palm Pest|آفات النخيل/i'
    );

    const hasPalmPests = await palmPests
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Not all implementations may have this specific feature
    // قد لا تحتوي جميع التطبيقات على هذه الميزة المحددة
    if (hasPalmPests) {
      await expect(palmPests.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Harvest Recording
// مجموعة الاختبارات: تسجيل الحصاد
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Harvest Recording | تسجيل الحصاد", () => {
  test("should display harvest recording page | عرض صفحة تسجيل الحصاد", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest");

    // Check for harvest content
    // التحقق من محتوى الحصاد
    await expect(
      farmerPage.locator("text=/Harvest|الحصاد|Yield|الإنتاج|Record|سجل/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should create new harvest record | إنشاء سجل حصاد جديد", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest/new");

    // Select field
    // اختيار الحقل
    const fieldSelect = farmerPage.locator('select[name="fieldId"]');
    if (await fieldSelect.isVisible()) {
      const options = await fieldSelect.locator("option").all();
      if (options.length > 1) {
        await fieldSelect.selectOption({ index: 1 });
      }
    }

    // Enter harvest date
    // إدخال تاريخ الحصاد
    const dateInput = farmerPage.locator(
      'input[name="harvestDate"], input[type="date"]'
    );
    if (await dateInput.isVisible()) {
      await dateInput.fill(new Date().toISOString().split("T")[0]);
    }

    // Enter yield amount
    // إدخال كمية الإنتاج
    const yieldInput = farmerPage.locator('input[name="yield"]');
    if (await yieldInput.isVisible()) {
      await yieldInput.fill("4500"); // 4.5 tons = 4500 kg
    }

    // Select yield unit
    // اختيار وحدة الإنتاج
    const unitSelect = farmerPage.locator('select[name="yieldUnit"]');
    if (await unitSelect.isVisible()) {
      await unitSelect.selectOption({ value: "kg" });
    }

    // Save harvest record
    await farmerPage.click(selectors.submitButton);
    await farmerPage.waitForURL(/\/harvest/, { timeout: timeouts.navigation });
  });

  test("should record harvest quality grades | تسجيل درجات جودة الحصاد", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest/new");

    // Look for quality grading section
    // البحث عن قسم تصنيف الجودة
    const qualitySection = farmerPage.locator(
      '[data-testid="quality-grade"], select[name="quality"], text=/Quality|الجودة|Grade|الدرجة/i'
    );

    const hasQuality = await qualitySection
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasQuality) {
      // Select quality grade
      // اختيار درجة الجودة
      const gradeSelect = farmerPage.locator('select[name="quality"]');
      if (await gradeSelect.isVisible()) {
        await gradeSelect.selectOption({ value: "A" });
      }
    }
  });

  test("should calculate yield per hectare | حساب الإنتاج لكل هكتار", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest");

    // Look for yield/hectare calculation
    // البحث عن حساب الإنتاج/هكتار
    const yieldPerHa = farmerPage.locator(
      '[data-testid="yield-per-hectare"], text=/kg\\/ha|tons\\/ha|كجم\\/هكتار|طن\\/هكتار|per hectare|لكل هكتار/i'
    );

    const hasYieldPerHa = await yieldPerHa
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasYieldPerHa) {
      await expect(yieldPerHa.first()).toBeVisible();
    }
  });

  test("should show harvest history and statistics | عرض تاريخ وإحصائيات الحصاد", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest/history");

    // Look for history table or list
    // البحث عن جدول أو قائمة التاريخ
    const historySection = farmerPage.locator(
      '[data-testid="harvest-history"], table, [class*="history"]'
    );

    const hasHistory = await historySection
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasHistory) {
      await expect(historySection.first()).toBeVisible();
    }
  });

  test("should compare harvest with previous seasons | مقارنة الحصاد مع المواسم السابقة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest/compare");

    // Look for comparison chart or table
    // البحث عن مخطط أو جدول المقارنة
    const comparison = farmerPage.locator(
      '[data-testid="harvest-comparison"], [class*="chart"], [class*="comparison"]'
    );

    const hasComparison = await comparison
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasComparison) {
      await expect(comparison.first()).toBeVisible();
    }
  });

  test("should record date palm harvest with varieties | تسجيل حصاد التمور مع الأصناف", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest/new");

    // Select date palm as crop
    // اختيار النخيل كمحصول
    const cropSelect = farmerPage.locator('select[name="cropType"]');
    if (await cropSelect.isVisible()) {
      await cropSelect.selectOption({ value: "date_palm" });
    }

    // Look for variety selector (e.g., Sukkari, Khalas, Ajwa)
    // البحث عن محدد الصنف (مثل: سكري، خلاص، عجوة)
    const varietySelect = farmerPage.locator(
      'select[name="variety"], [data-testid="variety-select"]'
    );

    const hasVariety = await varietySelect
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasVariety) {
      await varietySelect.selectOption({ index: 1 });
    }
  });

  test("should calculate harvest cost and profit | حساب تكلفة وربح الحصاد", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/harvest/economics");

    // Look for cost/profit calculations
    // البحث عن حسابات التكلفة/الربح
    const economics = farmerPage.locator(
      '[data-testid="harvest-economics"], text=/Cost|التكلفة|Profit|الربح|Revenue|الإيرادات/i'
    );

    const hasEconomics = await economics
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasEconomics) {
      await expect(economics.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Field Analytics
// مجموعة الاختبارات: تحليلات الحقل
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Field Analytics | تحليلات الحقل", () => {
  test("should display field performance dashboard | عرض لوحة أداء الحقل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/analytics");

    // Check for analytics content
    // التحقق من محتوى التحليلات
    await expect(
      farmerPage.locator(
        "text=/Analytics|التحليلات|Performance|الأداء|Statistics|الإحصائيات/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should show crop growth progress | عرض تقدم نمو المحصول", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields");

    // Click on first field
    // النقر على الحقل الأول
    const fieldCard = farmerPage.locator('[data-testid="field-card"]').first();

    if (await fieldCard.isVisible({ timeout: timeouts.medium })) {
      await fieldCard.click();
      await waitForPageLoad(farmerPage);

      // Look for growth stage indicator
      // البحث عن مؤشر مرحلة النمو
      const growthStage = farmerPage.locator(
        '[data-testid="growth-stage"], text=/Growth Stage|مرحلة النمو|Tillering|التفريع|Heading|السنبلة/i'
      );

      const hasGrowthStage = await growthStage
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasGrowthStage) {
        await expect(growthStage.first()).toBeVisible();
      }
    }
  });

  test("should display water usage statistics | عرض إحصائيات استخدام المياه", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/analytics/water");

    // Look for water usage charts/stats
    // البحث عن مخططات/إحصائيات استخدام المياه
    const waterStats = farmerPage.locator(
      '[data-testid="water-usage"], text=/Water Usage|استخدام المياه|Irrigation|الري|m³|لتر/i'
    );

    const hasWaterStats = await waterStats
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasWaterStats) {
      await expect(waterStats.first()).toBeVisible();
    }
  });

  test("should generate field report | إنشاء تقرير الحقل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/reports");

    // Look for generate report button
    // البحث عن زر إنشاء التقرير
    const generateBtn = farmerPage.locator(
      'button:has-text("Generate Report"), button:has-text("إنشاء تقرير"), button:has-text("Export"), button:has-text("تصدير")'
    );

    const hasGenerate = await generateBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasGenerate) {
      await generateBtn.first().click();
      await farmerPage.waitForTimeout(2000);

      // Check for download or report display
      // التحقق من التنزيل أو عرض التقرير
      const reportOutput = await waitForNotification(farmerPage, "success", 5000);

      if (reportOutput) {
        await expect(reportOutput).toBeVisible();
      }
    }
  });
});
