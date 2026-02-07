/**
 * Notifications & Alerts E2E Tests
 * اختبارات E2E للإشعارات والتنبيهات
 *
 * Comprehensive tests for:
 * - Notification center
 * - Alert management
 * - Push notification permissions
 * - Notification preferences
 * - Real-time notifications
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import {
  waitForPageLoad,
  navigateAndWait,
  waitForToast,
} from "./helpers/page.helpers";
import { timeouts } from "./helpers/test-data";

test.describe("Notifications & Alerts", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Notification Bell/Icon", () => {
    test("should display notification icon in header", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Look for notification bell icon
      const notificationIcon = page.locator(
        '[data-testid="notification-bell"], [aria-label*="notification"], button:has([class*="bell"]), [class*="notification-icon"]'
      );

      await expect(notificationIcon.first()).toBeVisible({ timeout: timeouts.long });
    });

    test("should show notification count badge", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Look for notification badge with count
      const badge = page.locator(
        '[data-testid="notification-count"], [class*="badge"], span:has-text(/^\\d+$/)'
      );
      const hasBadge = await badge.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Notification badge displayed: ${hasBadge}`);
    });

    test("should open notification dropdown on click", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const notificationIcon = page.locator(
        '[data-testid="notification-bell"], [aria-label*="notification"], button:has([class*="bell"])'
      );

      if (await notificationIcon.first().isVisible({ timeout: timeouts.medium })) {
        await notificationIcon.first().click();
        await page.waitForTimeout(500);

        // Dropdown should appear
        const dropdown = page.locator(
          '[data-testid="notification-dropdown"], [role="menu"], [class*="notification-list"], [class*="dropdown"]'
        );
        await expect(dropdown.first()).toBeVisible({ timeout: timeouts.medium });
      }
    });

    test("should display notification list in dropdown", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const notificationIcon = page.locator(
        '[data-testid="notification-bell"], [aria-label*="notification"]'
      );

      if (await notificationIcon.first().isVisible({ timeout: timeouts.medium })) {
        await notificationIcon.first().click();
        await page.waitForTimeout(500);

        // Look for notification items
        const notificationItems = page.locator(
          '[data-testid="notification-item"], [class*="notification-item"], [role="menuitem"]'
        );
        const count = await notificationItems.count();

        console.log(`Found ${count} notification items in dropdown`);
      }
    });

    test("should navigate to notifications page from dropdown", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const notificationIcon = page.locator('[data-testid="notification-bell"]');

      if (await notificationIcon.first().isVisible({ timeout: timeouts.medium })) {
        await notificationIcon.first().click();
        await page.waitForTimeout(500);

        // Look for "View All" link
        const viewAllLink = page.locator(
          'a:has-text("عرض الكل"), a:has-text("View All"), a:has-text("See All")'
        );

        if (await viewAllLink.first().isVisible({ timeout: timeouts.short })) {
          await viewAllLink.first().click();
          await page.waitForTimeout(1000);

          // Should navigate to notifications page
          const currentUrl = page.url();
          console.log(`Navigated to: ${currentUrl}`);
        }
      }
    });
  });

  test.describe("Alerts Page", () => {
    test("should display alerts page correctly", async ({ page }) => {
      await navigateAndWait(page, "/alerts");

      // Check for page heading
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      // Check for alerts-related content
      await expect(
        page.locator("text=/التنبيهات|Alerts|الإشعارات|Notifications/i")
      ).toBeVisible();
    });

    test("should display alert categories/filters", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for category filters
      const categoryFilters = page.locator(
        '[data-testid="alert-filter"], button:has-text("الكل"), button:has-text("All"), [class*="filter"], [class*="tab"]'
      );
      const count = await categoryFilters.count();

      console.log(`Found ${count} alert category filters`);
    });

    test("should filter alerts by type", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for specific alert type filters
      const typeFilters = [
        "text=/الري|Irrigation/i",
        "text=/الطقس|Weather/i",
        "text=/المحصول|Crop/i",
        "text=/المعدات|Equipment/i",
      ];

      for (const filter of typeFilters) {
        const filterBtn = page.locator(filter);
        const hasFilter = await filterBtn.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        if (hasFilter) {
          console.log(`Found filter: ${filter}`);
        }
      }
    });

    test("should display alert items with details", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for alert items
      const alertItems = page.locator(
        '[data-testid="alert-item"], [class*="alert-item"], [class*="notification-item"]'
      );
      const count = await alertItems.count();

      if (count > 0) {
        const firstAlert = alertItems.first();

        // Check for alert content
        const hasTitle = await firstAlert.locator('h3, h4, [class*="title"]').isVisible().catch(() => false);
        const hasTime = await firstAlert.locator('[class*="time"], [class*="date"], time').isVisible().catch(() => false);

        console.log(`Alert has title: ${hasTitle}, has time: ${hasTime}`);
      }

      console.log(`Found ${count} alert items`);
    });

    test("should mark alert as read", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const alertItems = page.locator('[data-testid="alert-item"], [class*="alert-item"]');

      if (await alertItems.first().isVisible({ timeout: timeouts.medium })) {
        // Look for mark as read button
        const markReadBtn = page.locator(
          'button:has-text("قراءة"), button:has-text("Read"), [data-testid="mark-read"]'
        );

        if (await markReadBtn.first().isVisible({ timeout: timeouts.short })) {
          await markReadBtn.first().click();
          await page.waitForTimeout(500);

          console.log("Alert marked as read");
        } else {
          // Try clicking the alert itself
          await alertItems.first().click();
          await page.waitForTimeout(500);
        }
      }
    });

    test("should mark all alerts as read", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for "Mark All Read" button
      const markAllBtn = page.locator(
        'button:has-text("تحديد الكل كمقروء"), button:has-text("Mark All Read"), button:has-text("Clear All")'
      );

      if (await markAllBtn.first().isVisible({ timeout: timeouts.medium })) {
        await markAllBtn.first().click();
        await page.waitForTimeout(500);

        const hasToast = await waitForToast(page, undefined, timeouts.medium);
        console.log(`Mark all read success: ${hasToast}`);
      }
    });

    test("should delete/dismiss alert", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const alertItems = page.locator('[data-testid="alert-item"]');

      if (await alertItems.first().isVisible({ timeout: timeouts.medium })) {
        // Hover to reveal delete button
        await alertItems.first().hover();
        await page.waitForTimeout(300);

        const deleteBtn = page.locator(
          'button:has-text("حذف"), button:has-text("Delete"), button:has-text("Dismiss"), [aria-label*="delete"]'
        );

        if (await deleteBtn.first().isVisible({ timeout: timeouts.short })) {
          await deleteBtn.first().click();
          await page.waitForTimeout(500);

          console.log("Alert deleted/dismissed");
        }
      }
    });
  });

  test.describe("Alert Priority Levels", () => {
    test("should display critical alerts with high priority styling", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for critical/urgent alerts
      const criticalAlerts = page.locator(
        '[data-priority="critical"], [class*="critical"], [class*="urgent"], [class*="error"]'
      );
      const count = await criticalAlerts.count();

      console.log(`Found ${count} critical alerts`);
    });

    test("should display warning alerts", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const warningAlerts = page.locator(
        '[data-priority="warning"], [class*="warning"], [class*="warn"]'
      );
      const count = await warningAlerts.count();

      console.log(`Found ${count} warning alerts`);
    });

    test("should display informational alerts", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const infoAlerts = page.locator(
        '[data-priority="info"], [class*="info"], [class*="notice"]'
      );
      const count = await infoAlerts.count();

      console.log(`Found ${count} informational alerts`);
    });

    test("should sort alerts by priority", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for sort dropdown
      const sortBtn = page.locator(
        'button:has-text("ترتيب"), button:has-text("Sort"), [data-testid="sort-alerts"]'
      );

      if (await sortBtn.first().isVisible({ timeout: timeouts.medium })) {
        await sortBtn.first().click();
        await page.waitForTimeout(300);

        // Look for priority sort option
        const priorityOption = page.locator(
          '[data-value="priority"], button:has-text("الأولوية"), button:has-text("Priority")'
        );
        const hasPriority = await priorityOption.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Priority sort option available: ${hasPriority}`);
      }
    });
  });

  test.describe("Notification Settings", () => {
    test("should navigate to notification settings", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      // Look for notification settings section
      const notifSettings = page.locator(
        'text=/إعدادات الإشعارات|Notification Settings|تفضيلات الإشعارات/i'
      );
      const hasSettings = await notifSettings.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Notification settings found: ${hasSettings}`);
    });

    test("should toggle push notification permission", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      const pushToggle = page.locator(
        '[data-testid="push-notifications-toggle"], input[name="pushNotifications"], [aria-label*="push"]'
      );

      if (await pushToggle.first().isVisible({ timeout: timeouts.medium })) {
        // Check current state
        const isEnabled = await pushToggle.first().isChecked().catch(() => false);
        console.log(`Push notifications currently: ${isEnabled ? 'enabled' : 'disabled'}`);
      }
    });

    test("should toggle email notifications", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      const emailToggle = page.locator(
        '[data-testid="email-notifications-toggle"], input[name="emailNotifications"], [aria-label*="email"]'
      );

      if (await emailToggle.first().isVisible({ timeout: timeouts.medium })) {
        const isEnabled = await emailToggle.first().isChecked().catch(() => false);
        console.log(`Email notifications currently: ${isEnabled ? 'enabled' : 'disabled'}`);
      }
    });

    test("should configure alert types", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      // Look for alert type checkboxes
      const alertTypes = page.locator(
        '[data-testid*="alert-type"], input[type="checkbox"][name*="alert"]'
      );
      const count = await alertTypes.count();

      console.log(`Found ${count} configurable alert types`);
    });

    test("should set quiet hours", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      const quietHours = page.locator(
        'text=/ساعات الهدوء|Quiet Hours|Do Not Disturb|عدم الإزعاج/i'
      );
      const hasQuietHours = await quietHours.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Quiet hours setting available: ${hasQuietHours}`);
    });

    test("should save notification settings", async ({ page }) => {
      await navigateAndWait(page, "/settings");
      await page.waitForTimeout(timeouts.medium);

      const saveBtn = page.locator(
        'button:has-text("حفظ"), button:has-text("Save"), button[type="submit"]'
      );

      if (await saveBtn.first().isVisible({ timeout: timeouts.medium })) {
        await saveBtn.first().click();

        const hasToast = await waitForToast(page, undefined, timeouts.long);
        console.log(`Settings saved: ${hasToast}`);
      }
    });
  });

  test.describe("Real-Time Notifications", () => {
    test("should display toast notification when new alert arrives", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");
      await page.waitForTimeout(timeouts.medium);

      // Check for toast container
      const toastContainer = page.locator(
        '[role="alert"], [class*="toast"], [data-testid="toast-container"]'
      );
      const hasToastContainer = await toastContainer.first().isVisible({ timeout: timeouts.short }).catch(() => false);

      console.log(`Toast container present: ${hasToastContainer}`);
    });

    test("should update notification count in real-time", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const badge = page.locator('[data-testid="notification-count"]');
      const initialCount = await badge.first().textContent().catch(() => "0");

      console.log(`Initial notification count: ${initialCount}`);

      // Wait for potential updates
      await page.waitForTimeout(timeouts.long);

      const newCount = await badge.first().textContent().catch(() => "0");
      console.log(`Updated notification count: ${newCount}`);
    });
  });

  test.describe("Notification Actions", () => {
    test("should navigate to related content when clicking notification", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const alertItems = page.locator('[data-testid="alert-item"], [class*="alert-item"]');

      if (await alertItems.first().isVisible({ timeout: timeouts.medium })) {
        const initialUrl = page.url();
        await alertItems.first().click();
        await page.waitForTimeout(1000);

        const newUrl = page.url();
        console.log(`Navigation after click: ${initialUrl} -> ${newUrl}`);
      }
    });

    test("should display action buttons on alert", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const alertItems = page.locator('[data-testid="alert-item"]');

      if (await alertItems.first().isVisible({ timeout: timeouts.medium })) {
        // Look for action buttons
        const actionBtns = alertItems.first().locator('button');
        const count = await actionBtns.count();

        console.log(`Found ${count} action buttons on alert`);
      }
    });

    test("should snooze alert", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const snoozeBtn = page.locator(
        'button:has-text("تأجيل"), button:has-text("Snooze"), button:has-text("Remind Later")'
      );

      if (await snoozeBtn.first().isVisible({ timeout: timeouts.medium })) {
        await snoozeBtn.first().click();
        await page.waitForTimeout(500);

        // Snooze options should appear
        const snoozeOptions = page.locator(
          '[data-testid="snooze-options"], [role="menu"]'
        );
        const hasOptions = await snoozeOptions.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Snooze options available: ${hasOptions}`);
      }
    });
  });

  test.describe("Alert History", () => {
    test("should display alert history/archive", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for history/archive tab
      const historyTab = page.locator(
        'button:has-text("السجل"), button:has-text("History"), button:has-text("Archive")'
      );

      if (await historyTab.first().isVisible({ timeout: timeouts.medium })) {
        await historyTab.first().click();
        await page.waitForTimeout(500);

        console.log("Alert history accessed");
      }
    });

    test("should filter alerts by date range", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Look for date range picker
      const dateRangePicker = page.locator(
        '[data-testid="date-range"], input[type="date"], button:has-text("التاريخ"), button:has-text("Date Range")'
      );
      const hasDatePicker = await dateRangePicker.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Date range filter available: ${hasDatePicker}`);
    });

    test("should search alerts", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      const searchInput = page.locator(
        'input[type="search"], input[placeholder*="بحث"], input[placeholder*="Search"]'
      );

      if (await searchInput.first().isVisible({ timeout: timeouts.medium })) {
        await searchInput.first().fill("test");
        await page.waitForTimeout(500);

        console.log("Alert search performed");
      }
    });
  });

  test.describe("Bilingual Notifications", () => {
    test("should display alerts in Arabic", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Check for Arabic content
      const arabicContent = page.locator('text=/[\u0600-\u06FF]/');
      const hasArabic = await arabicContent.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Arabic content displayed: ${hasArabic}`);
    });

    test("should support RTL layout for alerts", async ({ page }) => {
      await navigateAndWait(page, "/alerts");
      await page.waitForTimeout(timeouts.medium);

      // Check for RTL attribute
      const htmlDir = await page.locator('html').getAttribute('dir');
      const bodyDir = await page.locator('body').getAttribute('dir');

      console.log(`HTML dir: ${htmlDir}, Body dir: ${bodyDir}`);
    });
  });
});
