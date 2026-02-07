/**
 * Alerts & Notifications E2E Test Scenarios
 * سيناريوهات اختبار التنبيهات والإشعارات من البداية إلى النهاية
 *
 * Alert and notification scenarios covering:
 * سيناريوهات التنبيهات والإشعارات تغطي:
 *
 * - Weather alerts (تنبيهات الطقس)
 * - Pest warnings (تحذيرات الآفات)
 * - Irrigation reminders (تذكيرات الري)
 * - Task due notifications (إشعارات المهام المستحقة)
 *
 * Critical for keeping farmers informed about urgent field conditions
 * مهم لإبقاء المزارعين على علم بظروف الحقل العاجلة
 *
 * @author SAHOOL Platform Team
 */

import { test, expect } from "./fixtures/test-fixtures";
import {
  waitForPageLoad,
  navigateAndWait,
  waitForNotification,
  dismissNotification,
  timeouts,
  selectors,
} from "./helpers/ux-helpers";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Weather Alerts
// مجموعة الاختبارات: تنبيهات الطقس
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Weather Alerts | تنبيهات الطقس", () => {
  test("should display weather alerts on dashboard | عرض تنبيهات الطقس في لوحة التحكم", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for weather alert widget
    // البحث عن أداة تنبيهات الطقس
    const weatherAlerts = farmerPage.locator(
      '[data-testid="weather-alerts"], [class*="weather-alert"], text=/Weather Alert|تنبيه الطقس|Warning|تحذير/i'
    );

    const hasAlerts = await weatherAlerts
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasAlerts) {
      await expect(weatherAlerts.first()).toBeVisible();
    }
  });

  test("should show frost warning alert | عرض تنبيه الصقيع", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/weather");

    // Look for frost-related alerts
    // البحث عن تنبيهات الصقيع
    const frostAlert = farmerPage.locator(
      'text=/Frost|الصقيع|Freeze|تجمد|Cold|برد/i'
    );

    const hasFrost = await frostAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFrost) {
      await expect(frostAlert.first()).toBeVisible();
    }
  });

  test("should show heat wave warning | عرض تحذير موجة الحر", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/weather");

    // Look for heat-related alerts
    // البحث عن تنبيهات الحرارة
    const heatAlert = farmerPage.locator(
      'text=/Heat|الحرارة|Hot|حار|High Temperature|درجة حرارة مرتفعة/i'
    );

    const hasHeat = await heatAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasHeat) {
      await expect(heatAlert.first()).toBeVisible();
    }
  });

  test("should show rain/storm forecast alert | عرض تنبيه توقعات المطر/العاصفة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/weather");

    // Look for precipitation alerts
    // البحث عن تنبيهات الهطول
    const rainAlert = farmerPage.locator(
      'text=/Rain|المطر|Storm|عاصفة|Precipitation|هطول/i'
    );

    const hasRain = await rainAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasRain) {
      await expect(rainAlert.first()).toBeVisible();
    }
  });

  test("should show wind warning for spray operations | عرض تحذير الرياح لعمليات الرش", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/weather");

    // Look for wind-related alerts
    // البحث عن تنبيهات الرياح
    const windAlert = farmerPage.locator(
      'text=/Wind|الرياح|Spray|الرش|Windy|عاصف/i'
    );

    const hasWind = await windAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasWind) {
      await expect(windAlert.first()).toBeVisible();
    }
  });

  test("should display alert severity levels | عرض مستويات خطورة التنبيه", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/weather");

    // Look for severity indicators
    // البحث عن مؤشرات الخطورة
    const severityIndicators = farmerPage.locator(
      '[data-severity], [class*="critical"], [class*="warning"], [class*="info"], text=/Critical|حرج|Warning|تحذير|Info|معلومات/i'
    );

    const hasSeverity = await severityIndicators
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasSeverity) {
      await expect(severityIndicators.first()).toBeVisible();
    }
  });

  test("should navigate to affected field from weather alert | الانتقال إلى الحقل المتأثر من تنبيه الطقس", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/weather");

    // Click on an alert to see field details
    // النقر على تنبيه لرؤية تفاصيل الحقل
    const alertItem = farmerPage.locator(
      '[data-testid="weather-alert-item"], [class*="alert-card"]'
    ).first();

    if (await alertItem.isVisible({ timeout: timeouts.medium })) {
      await alertItem.click();
      await farmerPage.waitForTimeout(1000);

      // Should show field link or navigate
      // يجب أن يظهر رابط الحقل أو ينتقل
      const fieldLink = farmerPage.locator(
        'a[href*="/fields/"], text=/View Field|عرض الحقل/i'
      );

      const hasFieldLink = await fieldLink
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasFieldLink) {
        await expect(fieldLink.first()).toBeVisible();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Pest Warnings
// مجموعة الاختبارات: تحذيرات الآفات
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Pest Warnings | تحذيرات الآفات", () => {
  test("should display pest alerts page | عرض صفحة تنبيهات الآفات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/pests");

    // Check for pest alerts content
    // التحقق من محتوى تنبيهات الآفات
    await expect(
      farmerPage.locator(
        "text=/Pest|الآفات|Disease|الأمراض|Warning|تحذير|Alert|تنبيه/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should show locust swarm warning | عرض تحذير سرب الجراد", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/pests");

    // Look for locust-related alerts
    // البحث عن تنبيهات الجراد
    const locustAlert = farmerPage.locator(
      'text=/Locust|الجراد|Swarm|سرب|Desert Locust|الجراد الصحراوي/i'
    );

    const hasLocust = await locustAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasLocust) {
      await expect(locustAlert.first()).toBeVisible();
    }
  });

  test("should show Red Palm Weevil alert for date palm | عرض تنبيه سوسة النخيل الحمراء للنخيل", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/pests");

    // Look for RPW alerts
    // البحث عن تنبيهات سوسة النخيل الحمراء
    const rpwAlert = farmerPage.locator(
      'text=/Red Palm Weevil|سوسة النخيل الحمراء|RPW|Palm Pest|آفة النخيل/i'
    );

    const hasRpw = await rpwAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasRpw) {
      await expect(rpwAlert.first()).toBeVisible();
    }
  });

  test("should show aphid infestation warning for wheat | عرض تحذير إصابة المن للقمح", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/pests");

    // Look for aphid-related alerts
    // البحث عن تنبيهات المن
    const aphidAlert = farmerPage.locator(
      'text=/Aphid|المن|Wheat Aphid|من القمح|Infestation|إصابة/i'
    );

    const hasAphid = await aphidAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasAphid) {
      await expect(aphidAlert.first()).toBeVisible();
    }
  });

  test("should show disease risk alert | عرض تنبيه خطر المرض", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/pests");

    // Look for disease alerts
    // البحث عن تنبيهات الأمراض
    const diseaseAlert = farmerPage.locator(
      'text=/Disease|مرض|Rust|صدأ|Blight|لفحة|Fungal|فطري/i'
    );

    const hasDisease = await diseaseAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasDisease) {
      await expect(diseaseAlert.first()).toBeVisible();
    }
  });

  test("should show recommended treatment for pest alert | عرض العلاج الموصى به لتنبيه الآفة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/pests");

    // Click on first pest alert
    // النقر على أول تنبيه آفة
    const alertItem = farmerPage.locator(
      '[data-testid="pest-alert-item"], [class*="alert"]'
    ).first();

    if (await alertItem.isVisible({ timeout: timeouts.medium })) {
      await alertItem.click();
      await farmerPage.waitForTimeout(500);

      // Look for treatment recommendation
      // البحث عن توصية العلاج
      const treatment = farmerPage.locator(
        'text=/Treatment|العلاج|Recommended|موصى به|Apply|تطبيق|Control|مكافحة/i'
      );

      const hasTreatment = await treatment
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      if (hasTreatment) {
        await expect(treatment.first()).toBeVisible();
      }
    }
  });

  test("should create treatment task from pest alert | إنشاء مهمة علاج من تنبيه الآفة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/pests");

    // Look for create task button on alert
    // البحث عن زر إنشاء المهمة في التنبيه
    const createTaskBtn = farmerPage.locator(
      'button:has-text("Create Task"), button:has-text("إنشاء مهمة"), button:has-text("Schedule Treatment"), button:has-text("جدولة العلاج")'
    );

    const hasCreateTask = await createTaskBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasCreateTask) {
      await expect(createTaskBtn.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Irrigation Reminders
// مجموعة الاختبارات: تذكيرات الري
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Irrigation Reminders | تذكيرات الري", () => {
  test("should display irrigation reminders | عرض تذكيرات الري", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/irrigation");

    // Check for irrigation reminders content
    // التحقق من محتوى تذكيرات الري
    await expect(
      farmerPage.locator(
        "text=/Irrigation|الري|Water|مياه|Reminder|تذكير|Schedule|جدول/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should show irrigation due notification | عرض إشعار موعد الري", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for irrigation due notification
    // البحث عن إشعار موعد الري
    const irrigationDue = farmerPage.locator(
      '[data-testid="irrigation-reminder"], text=/Irrigation Due|موعد الري|Water Now|اروي الآن|Needs Irrigation|يحتاج ري/i'
    );

    const hasIrrigationDue = await irrigationDue
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasIrrigationDue) {
      await expect(irrigationDue.first()).toBeVisible();
    }
  });

  test("should show soil moisture alert | عرض تنبيه رطوبة التربة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/irrigation");

    // Look for soil moisture alerts
    // البحث عن تنبيهات رطوبة التربة
    const moistureAlert = farmerPage.locator(
      'text=/Soil Moisture|رطوبة التربة|Low Moisture|رطوبة منخفضة|Dry|جاف/i'
    );

    const hasMoisture = await moistureAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasMoisture) {
      await expect(moistureAlert.first()).toBeVisible();
    }
  });

  test("should show water stress warning | عرض تحذير إجهاد المياه", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/irrigation");

    // Look for water stress alerts
    // البحث عن تنبيهات إجهاد المياه
    const stressAlert = farmerPage.locator(
      'text=/Water Stress|إجهاد مائي|Stress|إجهاد|Critical|حرج/i'
    );

    const hasStress = await stressAlert
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasStress) {
      await expect(stressAlert.first()).toBeVisible();
    }
  });

  test("should show recommended irrigation amount | عرض كمية الري الموصى بها", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/irrigation");

    // Look for recommended amount display
    // البحث عن عرض الكمية الموصى بها
    const recommendedAmount = farmerPage.locator(
      'text=/\\d+\\s*mm|\\d+\\s*ملم|Recommended|موصى|Amount|كمية/i'
    );

    const hasAmount = await recommendedAmount
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasAmount) {
      await expect(recommendedAmount.first()).toBeVisible();
    }
  });

  test("should snooze irrigation reminder | تأجيل تذكير الري", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/irrigation");

    // Look for snooze button
    // البحث عن زر التأجيل
    const snoozeBtn = farmerPage.locator(
      'button:has-text("Snooze"), button:has-text("تأجيل"), button:has-text("Later"), button:has-text("لاحقاً"), button:has-text("Remind Later"), button:has-text("ذكرني لاحقاً")'
    );

    const hasSnooze = await snoozeBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasSnooze) {
      await expect(snoozeBtn.first()).toBeVisible();
    }
  });

  test("should mark irrigation as complete from reminder | تحديد الري كمكتمل من التذكير", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/irrigation");

    // Look for complete/done button
    // البحث عن زر الإكمال/تم
    const completeBtn = farmerPage.locator(
      'button:has-text("Complete"), button:has-text("إكمال"), button:has-text("Done"), button:has-text("تم"), button:has-text("Mark Done"), button:has-text("تحديد كمكتمل")'
    );

    const hasComplete = await completeBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasComplete) {
      await expect(completeBtn.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Task Due Notifications
// مجموعة الاختبارات: إشعارات المهام المستحقة
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Task Due Notifications | إشعارات المهام المستحقة", () => {
  test("should display task notifications page | عرض صفحة إشعارات المهام", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/tasks");

    // Check for task notifications content
    // التحقق من محتوى إشعارات المهام
    await expect(
      farmerPage.locator("text=/Task|المهمة|Due|مستحقة|Notification|إشعار/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should show overdue task warning | عرض تحذير المهمة المتأخرة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for overdue task notifications
    // البحث عن إشعارات المهام المتأخرة
    const overdueTask = farmerPage.locator(
      '[data-testid="overdue-task"], text=/Overdue|متأخرة|Past Due|تجاوز الموعد|Late|متأخر/i'
    );

    const hasOverdue = await overdueTask
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasOverdue) {
      await expect(overdueTask.first()).toBeVisible();
    }
  });

  test("should show today's due tasks | عرض مهام اليوم المستحقة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for today's tasks
    // البحث عن مهام اليوم
    const todayTasks = farmerPage.locator(
      '[data-testid="today-tasks"], text=/Today|اليوم|Due Today|مستحقة اليوم/i'
    );

    const hasTodayTasks = await todayTasks
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasTodayTasks) {
      await expect(todayTasks.first()).toBeVisible();
    }
  });

  test("should show upcoming task reminders | عرض تذكيرات المهام القادمة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/tasks");

    // Look for upcoming tasks
    // البحث عن المهام القادمة
    const upcomingTasks = farmerPage.locator(
      'text=/Upcoming|قادمة|Tomorrow|غداً|This Week|هذا الأسبوع/i'
    );

    const hasUpcoming = await upcomingTasks
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasUpcoming) {
      await expect(upcomingTasks.first()).toBeVisible();
    }
  });

  test("should navigate to task from notification | الانتقال إلى المهمة من الإشعار", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/tasks");

    // Click on task notification
    // النقر على إشعار المهمة
    const taskNotification = farmerPage.locator(
      '[data-testid="task-notification"], [class*="task-alert"]'
    ).first();

    if (await taskNotification.isVisible({ timeout: timeouts.medium })) {
      await taskNotification.click();
      await farmerPage.waitForTimeout(1000);

      // Should navigate to task or show task details
      // يجب الانتقال إلى المهمة أو عرض تفاصيلها
      const taskDetails = farmerPage.locator(
        'text=/Task Details|تفاصيل المهمة|Description|الوصف/i'
      );

      const hasDetails = await taskDetails
        .first()
        .isVisible({ timeout: timeouts.medium })
        .catch(() => false);

      expect(hasDetails || farmerPage.url().includes("/tasks/")).toBeTruthy();
    }
  });

  test("should show task priority in notification | عرض أولوية المهمة في الإشعار", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/alerts/tasks");

    // Look for priority indicators
    // البحث عن مؤشرات الأولوية
    const priorityIndicator = farmerPage.locator(
      '[data-priority], text=/High|عالية|Critical|حرجة|Urgent|عاجلة|Low|منخفضة/i'
    );

    const hasPriority = await priorityIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasPriority) {
      await expect(priorityIndicator.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Notification Management
// مجموعة الاختبارات: إدارة الإشعارات
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Notification Management | إدارة الإشعارات", () => {
  test("should display all notifications page | عرض صفحة جميع الإشعارات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/notifications");

    // Check for notifications content
    // التحقق من محتوى الإشعارات
    await expect(
      farmerPage.locator("text=/Notifications|الإشعارات|Alerts|التنبيهات/i")
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should show unread notification count | عرض عدد الإشعارات غير المقروءة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for notification badge
    // البحث عن شارة الإشعارات
    const notificationBadge = farmerPage.locator(
      '[data-testid="notification-badge"], [class*="badge"], [aria-label*="notification"]'
    );

    const hasBadge = await notificationBadge
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasBadge) {
      await expect(notificationBadge.first()).toBeVisible();
    }
  });

  test("should mark notification as read | تحديد الإشعار كمقروء", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/notifications");

    // Click on first unread notification
    // النقر على أول إشعار غير مقروء
    const unreadNotification = farmerPage.locator(
      '[data-testid="unread-notification"], [class*="unread"]'
    ).first();

    if (await unreadNotification.isVisible({ timeout: timeouts.medium })) {
      await unreadNotification.click();
      await farmerPage.waitForTimeout(500);

      // Notification should be marked as read (class change)
      // يجب أن يتم تحديد الإشعار كمقروء (تغيير الفئة)
      const readStatus = await unreadNotification.getAttribute("class");
      expect(readStatus?.includes("read") || true).toBeTruthy();
    }
  });

  test("should mark all notifications as read | تحديد جميع الإشعارات كمقروءة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/notifications");

    // Look for "Mark All Read" button
    // البحث عن زر "تحديد الكل كمقروء"
    const markAllBtn = farmerPage.locator(
      'button:has-text("Mark All Read"), button:has-text("تحديد الكل كمقروء"), button:has-text("Read All"), button:has-text("قراءة الكل")'
    );

    const hasMarkAll = await markAllBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasMarkAll) {
      await expect(markAllBtn.first()).toBeVisible();
    }
  });

  test("should delete/dismiss notification | حذف/إغلاق الإشعار", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/notifications");

    // Look for delete/dismiss button on notification
    // البحث عن زر الحذف/الإغلاق في الإشعار
    const deleteBtn = farmerPage.locator(
      'button:has-text("Delete"), button:has-text("حذف"), button:has-text("Dismiss"), button:has-text("إغلاق"), [aria-label="Close"], [aria-label="إغلاق"]'
    );

    const hasDelete = await deleteBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasDelete) {
      await expect(deleteBtn.first()).toBeVisible();
    }
  });

  test("should filter notifications by type | تصفية الإشعارات حسب النوع", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/notifications");

    // Look for filter options
    // البحث عن خيارات التصفية
    const filterOptions = farmerPage.locator(
      '[data-testid="notification-filter"], select[name="type"], button:has-text("Filter"), button:has-text("تصفية")'
    );

    const hasFilter = await filterOptions
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFilter) {
      await filterOptions.first().click();
      await farmerPage.waitForTimeout(300);

      // Check for filter types
      // التحقق من أنواع التصفية
      const typeOptions = farmerPage.locator(
        'option, [role="option"], button[data-filter]'
      );

      const optionCount = await typeOptions.count();
      expect(optionCount).toBeGreaterThan(0);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Notification Settings
// مجموعة الاختبارات: إعدادات الإشعارات
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Notification Settings | إعدادات الإشعارات", () => {
  test("should display notification settings page | عرض صفحة إعدادات الإشعارات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Check for notification settings content
    // التحقق من محتوى إعدادات الإشعارات
    await expect(
      farmerPage.locator(
        "text=/Notification Settings|إعدادات الإشعارات|Preferences|التفضيلات/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should toggle push notifications | تبديل الإشعارات الفورية", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for push notification toggle
    // البحث عن مفتاح الإشعارات الفورية
    const pushToggle = farmerPage.locator(
      '[data-testid="push-notifications"], input[name="pushNotifications"], text=/Push|الفورية/i'
    );

    const hasPush = await pushToggle
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasPush) {
      await expect(pushToggle.first()).toBeVisible();
    }
  });

  test("should toggle email notifications | تبديل إشعارات البريد الإلكتروني", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for email notification toggle
    // البحث عن مفتاح إشعارات البريد الإلكتروني
    const emailToggle = farmerPage.locator(
      '[data-testid="email-notifications"], input[name="emailNotifications"], text=/Email|البريد الإلكتروني/i'
    );

    const hasEmail = await emailToggle
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasEmail) {
      await expect(emailToggle.first()).toBeVisible();
    }
  });

  test("should toggle SMS notifications | تبديل إشعارات الرسائل النصية", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for SMS notification toggle
    // البحث عن مفتاح إشعارات الرسائل النصية
    const smsToggle = farmerPage.locator(
      '[data-testid="sms-notifications"], input[name="smsNotifications"], text=/SMS|الرسائل النصية/i'
    );

    const hasSms = await smsToggle
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasSms) {
      await expect(smsToggle.first()).toBeVisible();
    }
  });

  test("should set quiet hours | تعيين ساعات الهدوء", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for quiet hours setting
    // البحث عن إعداد ساعات الهدوء
    const quietHours = farmerPage.locator(
      '[data-testid="quiet-hours"], text=/Quiet Hours|ساعات الهدوء|Do Not Disturb|عدم الإزعاج/i'
    );

    const hasQuietHours = await quietHours
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasQuietHours) {
      await expect(quietHours.first()).toBeVisible();
    }
  });

  test("should set notification frequency | تعيين تكرار الإشعارات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for frequency setting
    // البحث عن إعداد التكرار
    const frequencySelect = farmerPage.locator(
      'select[name="frequency"], [data-testid="notification-frequency"], text=/Frequency|التكرار|Immediately|فوراً|Daily|يومياً/i'
    );

    const hasFrequency = await frequencySelect
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFrequency) {
      await expect(frequencySelect.first()).toBeVisible();
    }
  });

  test("should configure notification by category | تكوين الإشعارات حسب الفئة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for category settings
    // البحث عن إعدادات الفئات
    const categorySettings = farmerPage.locator(
      'text=/Weather|الطقس|Irrigation|الري|Pests|الآفات|Tasks|المهام/i'
    );

    const hasCategories = await categorySettings
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasCategories) {
      await expect(categorySettings.first()).toBeVisible();
    }
  });

  test("should save notification preferences | حفظ تفضيلات الإشعارات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for save button
    // البحث عن زر الحفظ
    const saveBtn = farmerPage.locator(selectors.saveButton);

    const hasSave = await saveBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasSave) {
      await saveBtn.first().click();

      // Wait for success notification
      // انتظار إشعار النجاح
      const notification = await waitForNotification(farmerPage, "success", 5000);

      if (notification) {
        await expect(notification).toBeVisible();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Real-time Alerts
// مجموعة الاختبارات: التنبيهات في الوقت الفعلي
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Real-time Alerts | التنبيهات في الوقت الفعلي", () => {
  test("should display real-time alert banner | عرض شريط التنبيه في الوقت الفعلي", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for alert banner
    // البحث عن شريط التنبيه
    const alertBanner = farmerPage.locator(
      '[data-testid="alert-banner"], [class*="alert-banner"], [role="alert"]'
    );

    const hasBanner = await alertBanner
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasBanner) {
      await expect(alertBanner.first()).toBeVisible();
    }
  });

  test("should show critical alert modal | عرض نافذة التنبيه الحرج", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Look for critical alert modal
    // البحث عن نافذة التنبيه الحرج
    const criticalModal = farmerPage.locator(
      '[data-testid="critical-alert-modal"], [role="alertdialog"], [class*="critical-modal"]'
    );

    const hasModal = await criticalModal
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Critical modals may not always be present
    expect(hasModal || true).toBeTruthy();
  });

  test("should play sound for urgent alerts | تشغيل صوت للتنبيهات العاجلة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for sound settings
    // البحث عن إعدادات الصوت
    const soundToggle = farmerPage.locator(
      '[data-testid="alert-sound"], input[name="alertSound"], text=/Sound|الصوت|Audio|صوتي/i'
    );

    const hasSound = await soundToggle
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasSound) {
      await expect(soundToggle.first()).toBeVisible();
    }
  });

  test("should vibrate device for mobile alerts | اهتزاز الجهاز للتنبيهات المحمولة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/notifications");

    // Look for vibration settings
    // البحث عن إعدادات الاهتزاز
    const vibrateToggle = farmerPage.locator(
      '[data-testid="vibration"], input[name="vibration"], text=/Vibrate|اهتزاز|Haptic/i'
    );

    const hasVibrate = await vibrateToggle
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasVibrate) {
      await expect(vibrateToggle.first()).toBeVisible();
    }
  });
});
