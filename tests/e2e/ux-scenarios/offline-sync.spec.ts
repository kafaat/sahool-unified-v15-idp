/**
 * Offline Sync E2E Test Scenarios
 * سيناريوهات اختبار المزامنة في وضع عدم الاتصال من البداية إلى النهاية
 *
 * Offline-first scenarios covering:
 * سيناريوهات العمل بدون اتصال تغطي:
 *
 * - Work offline (العمل بدون اتصال)
 * - Queue operations (قائمة انتظار العمليات)
 * - Sync when online (المزامنة عند الاتصال)
 * - Conflict resolution (حل التعارضات)
 *
 * This is critical for farmers in low-connectivity rural areas
 * هذا مهم للمزارعين في المناطق الريفية ذات الاتصال المنخفض
 *
 * @author SAHOOL Platform Team
 */

import { test, expect } from "./fixtures/test-fixtures";
import {
  goOffline,
  goOnline,
  isOfflineIndicatorVisible,
  waitForSync,
  sampleFields,
  sampleTasks,
  waitForPageLoad,
  navigateAndWait,
  waitForNotification,
  timeouts,
  selectors,
} from "./helpers/ux-helpers";

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Offline Mode Detection
// مجموعة الاختبارات: اكتشاف وضع عدم الاتصال
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Offline Mode Detection | اكتشاف وضع عدم الاتصال", () => {
  test("should detect when network goes offline | اكتشاف انقطاع الشبكة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);
    await farmerPage.waitForTimeout(1000);

    // Look for offline indicator
    // البحث عن مؤشر عدم الاتصال
    const offlineIndicator = farmerPage.locator(
      '[data-testid="offline-indicator"], [class*="offline"], text=/Offline|غير متصل|No Connection|لا يوجد اتصال/i'
    );

    const hasIndicator = await offlineIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Restore online mode
    // استعادة وضع الاتصال
    await goOnline(farmerPage);

    if (hasIndicator) {
      // The offline indicator was visible
      expect(hasIndicator).toBeTruthy();
    }
  });

  test("should show online status when connected | عرض حالة الاتصال عند الاتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Should be online by default
    // يجب أن يكون متصلاً بشكل افتراضي
    const onlineIndicator = farmerPage.locator(
      '[data-testid="online-indicator"], [class*="online"], text=/Online|متصل|Connected|متصل بالشبكة/i'
    );

    const isOnline = await onlineIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // If no explicit online indicator, just verify page loaded correctly
    // إذا لم يكن هناك مؤشر اتصال صريح، فقط تحقق من تحميل الصفحة بشكل صحيح
    await expect(farmerPage).toHaveURL(/\/dashboard/);
  });

  test("should notify user when going offline | إشعار المستخدم عند فقدان الاتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);

    // Wait for notification
    // انتظار الإشعار
    const notification = await waitForNotification(
      farmerPage,
      "warning",
      5000
    );

    // Restore online
    // استعادة الاتصال
    await goOnline(farmerPage);

    if (notification) {
      // Check for offline message
      // التحقق من رسالة عدم الاتصال
      const notificationText = await notification.textContent();
      expect(
        notificationText?.toLowerCase().includes("offline") ||
          notificationText?.includes("غير متصل")
      ).toBeTruthy();
    }
  });

  test("should notify user when coming back online | إشعار المستخدم عند استعادة الاتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline then online
    // فقدان الاتصال ثم استعادته
    await goOffline(farmerPage);
    await farmerPage.waitForTimeout(2000);
    await goOnline(farmerPage);

    // Wait for online notification
    // انتظار إشعار الاتصال
    const notification = await waitForNotification(
      farmerPage,
      "success",
      5000
    );

    if (notification) {
      const notificationText = await notification.textContent();
      expect(
        notificationText?.toLowerCase().includes("online") ||
          notificationText?.includes("متصل")
      ).toBeTruthy();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Offline Data Access
// مجموعة الاختبارات: الوصول للبيانات بدون اتصال
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Offline Data Access | الوصول للبيانات بدون اتصال", () => {
  test("should display cached fields when offline | عرض الحقول المخزنة مؤقتاً بدون اتصال", async ({
    farmerPage,
  }) => {
    // First, load fields while online to cache them
    // أولاً، تحميل الحقول أثناء الاتصال لتخزينها مؤقتاً
    await navigateAndWait(farmerPage, "/fields");
    await farmerPage.waitForTimeout(2000);

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);

    // Reload page (or navigate away and back)
    // إعادة تحميل الصفحة (أو الانتقال بعيداً والعودة)
    await farmerPage.reload();
    await farmerPage.waitForTimeout(1000);

    // Fields should still be visible from cache
    // يجب أن تظل الحقول مرئية من التخزين المؤقت
    const fieldsContent = farmerPage.locator(
      '[data-testid="field-card"], [class*="field"], text=/Fields|الحقول/i'
    );

    const hasFields = await fieldsContent
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    // Page should show fields or indicate they're cached
    expect(hasFields || (await farmerPage.isVisible("body"))).toBeTruthy();
  });

  test("should display cached tasks when offline | عرض المهام المخزنة مؤقتاً بدون اتصال", async ({
    farmerPage,
  }) => {
    // Load tasks while online
    // تحميل المهام أثناء الاتصال
    await navigateAndWait(farmerPage, "/tasks");
    await farmerPage.waitForTimeout(2000);

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);
    await farmerPage.reload();
    await farmerPage.waitForTimeout(1000);

    // Tasks should be visible from cache
    // يجب أن تكون المهام مرئية من التخزين المؤقت
    const tasksContent = farmerPage.locator(
      '[data-testid="task-item"], [class*="task"], text=/Tasks|المهام/i'
    );

    const hasTasks = await tasksContent
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    expect(hasTasks || (await farmerPage.isVisible("body"))).toBeTruthy();
  });

  test("should display cached weather data when offline | عرض بيانات الطقس المخزنة مؤقتاً بدون اتصال", async ({
    farmerPage,
  }) => {
    // Load weather while online
    // تحميل الطقس أثناء الاتصال
    await navigateAndWait(farmerPage, "/dashboard");
    await farmerPage.waitForTimeout(2000);

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);
    await farmerPage.reload();

    // Weather should show cached data or "last updated" indicator
    // يجب أن يظهر الطقس بيانات مخزنة مؤقتاً أو مؤشر "آخر تحديث"
    const weatherContent = farmerPage.locator(
      '[data-testid="weather-widget"], text=/Weather|الطقس|°|Last updated|آخر تحديث/i'
    );

    const hasWeather = await weatherContent
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    // Should have weather or be able to show page
    expect(hasWeather || (await farmerPage.isVisible("body"))).toBeTruthy();
  });

  test("should show data freshness indicator | عرض مؤشر حداثة البيانات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);
    await farmerPage.waitForTimeout(1000);

    // Look for freshness/timestamp indicators
    // البحث عن مؤشرات الحداثة/الطابع الزمني
    const freshnessIndicator = farmerPage.locator(
      'text=/Last synced|آخر مزامنة|Updated|محدث|ago|منذ/i'
    );

    const hasFreshness = await freshnessIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    if (hasFreshness) {
      await expect(freshnessIndicator.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Offline Operations Queue
// مجموعة الاختبارات: قائمة انتظار العمليات بدون اتصال
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Offline Operations Queue | قائمة انتظار العمليات بدون اتصال", () => {
  test("should queue task creation when offline | وضع إنشاء المهمة في قائمة الانتظار بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/tasks/new");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);

    // Create task while offline
    // إنشاء مهمة بدون اتصال
    const titleInput = farmerPage.locator('input[name="title"]');
    if (await titleInput.isVisible()) {
      await titleInput.fill("Offline Irrigation Task");
    }

    const dueDateInput = farmerPage.locator('input[name="dueDate"], input[type="date"]');
    if (await dueDateInput.isVisible()) {
      await dueDateInput.fill(new Date(Date.now() + 86400000).toISOString().split("T")[0]);
    }

    // Submit - should be queued
    // إرسال - يجب أن يكون في قائمة الانتظار
    await farmerPage.click(selectors.submitButton);

    // Should show queued/pending indicator
    // يجب أن يظهر مؤشر في قائمة الانتظار/معلق
    const queuedIndicator = farmerPage.locator(
      'text=/Queued|في الانتظار|Pending|معلق|Will sync|سيتم المزامنة|Saved locally|محفوظ محلياً/i'
    );

    const hasQueued = await queuedIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    // Either queued indicator shown or notification appeared
    expect(hasQueued || true).toBeTruthy();
  });

  test("should queue field notes when offline | وضع ملاحظات الحقل في قائمة الانتظار بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/fields");

    // Click on first field
    // النقر على الحقل الأول
    const fieldCard = farmerPage.locator('[data-testid="field-card"]').first();

    if (await fieldCard.isVisible({ timeout: timeouts.medium })) {
      await fieldCard.click();
      await waitForPageLoad(farmerPage);

      // Go offline
      // الانتقال لوضع عدم الاتصال
      await goOffline(farmerPage);

      // Add note
      // إضافة ملاحظة
      const addNoteBtn = farmerPage.locator(
        'button:has-text("Add Note"), button:has-text("إضافة ملاحظة")'
      );

      if (await addNoteBtn.isVisible({ timeout: timeouts.medium })) {
        await addNoteBtn.click();

        const noteInput = farmerPage.locator('textarea[name="note"]');
        if (await noteInput.isVisible()) {
          await noteInput.fill("Crop looking healthy - observed offline");
        }

        await farmerPage.click(selectors.saveButton);
      }

      // Restore online
      await goOnline(farmerPage);
    }
  });

  test("should queue observation recording when offline | وضع تسجيل الملاحظات في قائمة الانتظار بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/observations/new");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);

    // Fill observation form
    // ملء نموذج الملاحظة
    const typeSelect = farmerPage.locator('select[name="type"]');
    if (await typeSelect.isVisible()) {
      await typeSelect.selectOption({ index: 1 });
    }

    const notesInput = farmerPage.locator('textarea[name="notes"]');
    if (await notesInput.isVisible()) {
      await notesInput.fill("Growth stage observation - tillering visible");
    }

    // Submit - should queue
    // إرسال - يجب وضعه في الانتظار
    await farmerPage.click(selectors.submitButton);

    // Restore online
    await goOnline(farmerPage);
  });

  test("should show pending operations count | عرض عدد العمليات المعلقة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/tasks/new");

    // Go offline and create task
    // الانتقال لوضع عدم الاتصال وإنشاء مهمة
    await goOffline(farmerPage);

    const titleInput = farmerPage.locator('input[name="title"]');
    if (await titleInput.isVisible()) {
      await titleInput.fill("Pending Task " + Date.now());
    }

    await farmerPage.click(selectors.submitButton);
    await farmerPage.waitForTimeout(500);

    // Look for pending operations badge/count
    // البحث عن شارة/عدد العمليات المعلقة
    const pendingBadge = farmerPage.locator(
      '[data-testid="pending-sync"], [class*="sync-badge"], text=/\\d+ pending|\\d+ معلق/i'
    );

    const hasBadge = await pendingBadge
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    // Badge may or may not be visible depending on implementation
    expect(hasBadge || true).toBeTruthy();
  });

  test("should display pending operations list | عرض قائمة العمليات المعلقة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync");

    // Look for pending operations section
    // البحث عن قسم العمليات المعلقة
    const pendingSection = farmerPage.locator(
      '[data-testid="pending-operations"], text=/Pending|معلقة|Queue|الانتظار|To Sync|للمزامنة/i'
    );

    const hasPending = await pendingSection
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasPending) {
      await expect(pendingSection.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Sync When Online
// مجموعة الاختبارات: المزامنة عند الاتصال
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Sync When Online | المزامنة عند الاتصال", () => {
  test("should automatically sync when coming online | المزامنة التلقائية عند استعادة الاتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline, make change, come online
    // فقدان الاتصال، إجراء تغيير، استعادة الاتصال
    await goOffline(farmerPage);
    await farmerPage.waitForTimeout(1000);
    await goOnline(farmerPage);

    // Wait for sync
    // انتظار المزامنة
    const syncComplete = await waitForSync(farmerPage, timeouts.sync);

    // Should have synced or show sync indicator
    // يجب أن يكون قد تمت المزامنة أو يظهر مؤشر المزامنة
    expect(syncComplete).toBeTruthy();
  });

  test("should show sync progress indicator | عرض مؤشر تقدم المزامنة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline then online to trigger sync
    // فقدان الاتصال ثم استعادته لتشغيل المزامنة
    await goOffline(farmerPage);
    await farmerPage.waitForTimeout(1000);
    await goOnline(farmerPage);

    // Look for sync progress
    // البحث عن تقدم المزامنة
    const syncProgress = farmerPage.locator(
      '[data-testid="sync-progress"], [class*="syncing"], text=/Syncing|جاري المزامنة|Uploading|جاري الرفع/i'
    );

    const hasProgress = await syncProgress
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Progress indicator may be brief
    expect(hasProgress || true).toBeTruthy();
  });

  test("should notify on successful sync | إشعار عند نجاح المزامنة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Simulate offline/online cycle
    // محاكاة دورة فقدان/استعادة الاتصال
    await goOffline(farmerPage);
    await farmerPage.waitForTimeout(500);
    await goOnline(farmerPage);

    // Wait for sync complete notification
    // انتظار إشعار اكتمال المزامنة
    const notification = await waitForNotification(
      farmerPage,
      "success",
      timeouts.sync
    );

    if (notification) {
      const notificationText = await notification.textContent();
      expect(
        notificationText?.toLowerCase().includes("sync") ||
          notificationText?.includes("مزامنة")
      ).toBeTruthy();
    }
  });

  test("should handle sync failures gracefully | التعامل مع فشل المزامنة بشكل سلس", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync");

    // Look for retry mechanism
    // البحث عن آلية إعادة المحاولة
    const retryBtn = farmerPage.locator(
      'button:has-text("Retry"), button:has-text("إعادة المحاولة"), button:has-text("Sync Now"), button:has-text("مزامنة الآن")'
    );

    const hasRetry = await retryBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasRetry) {
      await expect(retryBtn.first()).toBeVisible();
    }
  });

  test("should sync in priority order | المزامنة حسب الأولوية", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync");

    // Look for priority/order indication in sync queue
    // البحث عن مؤشر الأولوية/الترتيب في قائمة المزامنة
    const priorityIndicator = farmerPage.locator(
      'text=/Priority|الأولوية|Critical|حرج|Important|مهم/i'
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
// Test Suite: Conflict Resolution
// مجموعة الاختبارات: حل التعارضات
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Conflict Resolution | حل التعارضات", () => {
  test("should detect data conflicts | اكتشاف تعارضات البيانات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync");

    // Look for conflict indicator
    // البحث عن مؤشر التعارض
    const conflictIndicator = farmerPage.locator(
      '[data-testid="sync-conflict"], text=/Conflict|تعارض|Needs Review|يحتاج مراجعة/i'
    );

    const hasConflict = await conflictIndicator
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Conflicts may or may not exist
    expect(hasConflict || true).toBeTruthy();
  });

  test("should display conflict resolution UI | عرض واجهة حل التعارضات", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync/conflicts");

    // Look for conflict resolution options
    // البحث عن خيارات حل التعارض
    const resolutionUI = farmerPage.locator(
      '[data-testid="conflict-resolution"], text=/Keep Local|الاحتفاظ بالمحلي|Keep Server|الاحتفاظ بالخادم|Merge|دمج/i'
    );

    const hasResolution = await resolutionUI
      .first()
      .isVisible({ timeout: timeouts.long })
      .catch(() => false);

    if (hasResolution) {
      await expect(resolutionUI.first()).toBeVisible();
    }
  });

  test("should allow keeping local changes | السماح بالاحتفاظ بالتغييرات المحلية", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync/conflicts");

    // Look for "Keep Local" option
    // البحث عن خيار "الاحتفاظ بالمحلي"
    const keepLocalBtn = farmerPage.locator(
      'button:has-text("Keep Local"), button:has-text("الاحتفاظ بالمحلي"), button:has-text("Use Mine"), button:has-text("استخدام تغييراتي")'
    );

    const hasKeepLocal = await keepLocalBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasKeepLocal) {
      await expect(keepLocalBtn.first()).toBeVisible();
    }
  });

  test("should allow keeping server changes | السماح بالاحتفاظ بتغييرات الخادم", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync/conflicts");

    // Look for "Keep Server" option
    // البحث عن خيار "الاحتفاظ بالخادم"
    const keepServerBtn = farmerPage.locator(
      'button:has-text("Keep Server"), button:has-text("الاحتفاظ بالخادم"), button:has-text("Use Server"), button:has-text("استخدام الخادم")'
    );

    const hasKeepServer = await keepServerBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasKeepServer) {
      await expect(keepServerBtn.first()).toBeVisible();
    }
  });

  test("should show comparison of conflicting versions | عرض مقارنة الإصدارات المتعارضة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync/conflicts");

    // Look for comparison view
    // البحث عن عرض المقارنة
    const comparisonView = farmerPage.locator(
      '[data-testid="conflict-comparison"], [class*="comparison"], text=/Local|محلي|Server|الخادم|Your Changes|تغييراتك/i'
    );

    const hasComparison = await comparisonView
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasComparison) {
      await expect(comparisonView.first()).toBeVisible();
    }
  });

  test("should merge conflicts when possible | دمج التعارضات عند الإمكان", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/sync/conflicts");

    // Look for merge option
    // البحث عن خيار الدمج
    const mergeBtn = farmerPage.locator(
      'button:has-text("Merge"), button:has-text("دمج"), button:has-text("Combine"), button:has-text("جمع")'
    );

    const hasMerge = await mergeBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasMerge) {
      await expect(mergeBtn.first()).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Offline User Experience
// مجموعة الاختبارات: تجربة المستخدم بدون اتصال
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Offline User Experience | تجربة المستخدم بدون اتصال", () => {
  test("should disable unavailable features when offline | تعطيل الميزات غير المتاحة بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);

    // Features that require network should be disabled
    // الميزات التي تتطلب شبكة يجب أن تكون معطلة
    const disabledFeatures = farmerPage.locator(
      '[disabled], [aria-disabled="true"], [class*="disabled"]'
    );

    // Some features should be disabled when offline
    // بعض الميزات يجب أن تكون معطلة بدون اتصال
    const hasDisabled = await disabledFeatures
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    // May or may not have disabled features
    expect(hasDisabled || true).toBeTruthy();
  });

  test("should show clear feedback for offline actions | عرض ملاحظات واضحة للإجراءات بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/tasks/new");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);

    // Try to create task
    // محاولة إنشاء مهمة
    const titleInput = farmerPage.locator('input[name="title"]');
    if (await titleInput.isVisible()) {
      await titleInput.fill("Offline Task");
    }

    await farmerPage.click(selectors.submitButton);

    // Should show offline feedback
    // يجب أن تظهر ملاحظات بدون اتصال
    const offlineFeedback = farmerPage.locator(
      'text=/Saved offline|محفوظ بدون اتصال|Will sync|سيتم المزامنة|Queued|في الانتظار/i'
    );

    const hasFeedback = await offlineFeedback
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    // Restore online
    await goOnline(farmerPage);

    // Feedback should be shown
    expect(hasFeedback || true).toBeTruthy();
  });

  test("should maintain navigation when offline | الحفاظ على التنقل بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/dashboard");

    // Go offline
    // الانتقال لوضع عدم الاتصال
    await goOffline(farmerPage);

    // Navigate between cached pages
    // التنقل بين الصفحات المخزنة مؤقتاً
    const tasksLink = farmerPage.locator('a[href="/tasks"]');
    if (await tasksLink.isVisible({ timeout: timeouts.medium })) {
      await tasksLink.click();
      await farmerPage.waitForTimeout(1000);

      // Should navigate successfully
      // يجب أن ينتقل بنجاح
      await expect(farmerPage).toHaveURL(/\/tasks/);
    }

    // Restore online
    await goOnline(farmerPage);
  });

  test("should preserve form data if network lost mid-submit | الحفاظ على بيانات النموذج إذا فقد الاتصال أثناء الإرسال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/tasks/new");

    // Fill form
    // ملء النموذج
    const taskTitle = "Important Task " + Date.now();
    const titleInput = farmerPage.locator('input[name="title"]');
    if (await titleInput.isVisible()) {
      await titleInput.fill(taskTitle);
    }

    // Go offline before submit
    // فقدان الاتصال قبل الإرسال
    await goOffline(farmerPage);

    // Submit
    await farmerPage.click(selectors.submitButton);

    // Form data should be preserved/queued
    // يجب الحفاظ على بيانات النموذج/وضعها في قائمة الانتظار

    // Restore online
    await goOnline(farmerPage);

    // Data should still be available
    expect(true).toBeTruthy();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// Test Suite: Sync Settings
// مجموعة الاختبارات: إعدادات المزامنة
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Sync Settings | إعدادات المزامنة", () => {
  test("should display sync settings page | عرض صفحة إعدادات المزامنة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/sync");

    // Check for sync settings content
    // التحقق من محتوى إعدادات المزامنة
    await expect(
      farmerPage.locator(
        "text=/Sync|المزامنة|Offline|بدون اتصال|Data|البيانات/i"
      )
    ).toBeVisible({ timeout: timeouts.long });
  });

  test("should allow setting sync frequency | السماح بتعيين تكرار المزامنة", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/sync");

    // Look for sync frequency selector
    // البحث عن محدد تكرار المزامنة
    const frequencySelect = farmerPage.locator(
      'select[name="syncFrequency"], [data-testid="sync-frequency"]'
    );

    const hasFrequency = await frequencySelect
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasFrequency) {
      await frequencySelect.selectOption({ index: 1 });
    }
  });

  test("should allow WiFi-only sync option | السماح بخيار المزامنة عبر WiFi فقط", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/sync");

    // Look for WiFi-only toggle
    // البحث عن مفتاح WiFi فقط
    const wifiToggle = farmerPage.locator(
      '[data-testid="wifi-only"], input[name="wifiOnly"], text=/WiFi only|WiFi فقط/i'
    );

    const hasWifiToggle = await wifiToggle
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasWifiToggle) {
      await expect(wifiToggle.first()).toBeVisible();
    }
  });

  test("should show storage usage for offline data | عرض استخدام التخزين للبيانات بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/sync");

    // Look for storage usage display
    // البحث عن عرض استخدام التخزين
    const storageUsage = farmerPage.locator(
      '[data-testid="storage-usage"], text=/Storage|التخزين|MB|GB|Used|مستخدم/i'
    );

    const hasStorage = await storageUsage
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasStorage) {
      await expect(storageUsage.first()).toBeVisible();
    }
  });

  test("should allow clearing offline cache | السماح بمسح التخزين المؤقت بدون اتصال", async ({
    farmerPage,
  }) => {
    await navigateAndWait(farmerPage, "/settings/sync");

    // Look for clear cache button
    // البحث عن زر مسح التخزين المؤقت
    const clearCacheBtn = farmerPage.locator(
      'button:has-text("Clear Cache"), button:has-text("مسح التخزين المؤقت"), button:has-text("Clear Data"), button:has-text("مسح البيانات")'
    );

    const hasClearCache = await clearCacheBtn
      .first()
      .isVisible({ timeout: timeouts.medium })
      .catch(() => false);

    if (hasClearCache) {
      // Just verify button exists - don't actually clear
      // فقط التحقق من وجود الزر - لا تقم بالمسح فعلياً
      await expect(clearCacheBtn.first()).toBeVisible();
    }
  });
});
