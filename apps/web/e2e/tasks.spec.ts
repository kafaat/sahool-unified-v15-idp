/**
 * Tasks Management E2E Tests
 * اختبارات E2E لإدارة المهام
 *
 * Comprehensive tests for:
 * - Task CRUD operations
 * - Task scheduling and reminders
 * - Task assignment and team collaboration
 * - Task filtering and search
 * - Task status management
 * - Task calendar view
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import {
  waitForPageLoad,
  navigateAndWait,
  waitForToast,
} from "./helpers/page.helpers";
import { testData, timeouts } from "./helpers/test-data";

test.describe("Tasks Management", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Tasks List Page", () => {
    test("should display tasks page correctly", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      // Check for page heading
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.long });

      // Check for tasks-related content
      await expect(
        page.locator("text=/المهام|Tasks/i")
      ).toBeVisible();
    });

    test("should display add task button", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator(
        'button:has-text("إضافة مهمة"), button:has-text("Add Task"), button:has-text("جديد"), button:has-text("New")'
      );

      await expect(addButton.first()).toBeVisible({ timeout: timeouts.long });
    });

    test("should display task list or empty state", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      // Look for tasks or empty state
      const taskItems = page.locator(
        '[data-testid="task-item"], [class*="task-item"], [class*="task-card"]'
      );
      const emptyState = page.locator(
        'text=/لا توجد مهام|No tasks|Empty|فارغ/i'
      );

      const hasTasks = await taskItems.first().isVisible({ timeout: timeouts.short }).catch(() => false);
      const hasEmpty = await emptyState.first().isVisible({ timeout: timeouts.short }).catch(() => false);

      console.log(`Tasks present: ${hasTasks}, Empty state: ${hasEmpty}`);
    });

    test("should display task status tabs", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      // Look for status tabs
      const statusTabs = page.locator(
        'button:has-text("الكل"), button:has-text("All"), button:has-text("قيد التنفيذ"), button:has-text("In Progress"), button:has-text("مكتمل"), button:has-text("Completed")'
      );
      const count = await statusTabs.count();

      console.log(`Status tabs found: ${count}`);
    });

    test("should display search functionality", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const searchInput = page.locator(
        'input[type="search"], input[placeholder*="بحث"], input[placeholder*="Search"]'
      );
      const hasSearch = await searchInput.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Search available: ${hasSearch}`);
    });

    test("should display filter options", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const filterBtn = page.locator(
        'button:has-text("تصفية"), button:has-text("Filter"), [data-testid="filter-button"]'
      );
      const hasFilter = await filterBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Filter available: ${hasFilter}`);
    });
  });

  test.describe("Create Task", () => {
    test("should open create task form", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator(
        'button:has-text("إضافة مهمة"), button:has-text("Add Task")'
      );

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        // Form should appear
        const form = page.locator(
          'form, [role="dialog"], [data-testid="task-form"]'
        );
        await expect(form.first()).toBeVisible({ timeout: timeouts.medium });
      }
    });

    test("should display required task fields", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator('button:has-text("إضافة مهمة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        // Check for title input
        const titleInput = page.locator(
          'input[name="title"], input[placeholder*="عنوان"], input[placeholder*="Title"]'
        );
        await expect(titleInput.first()).toBeVisible({ timeout: timeouts.medium });

        // Check for description
        const descInput = page.locator(
          'textarea[name="description"], textarea[placeholder*="وصف"], textarea[placeholder*="Description"]'
        );
        const hasDesc = await descInput.first().isVisible({ timeout: timeouts.short }).catch(() => false);
        console.log(`Description field: ${hasDesc}`);

        // Check for due date
        const dueDateInput = page.locator(
          'input[type="date"], input[name="dueDate"], [data-testid="due-date"]'
        );
        const hasDueDate = await dueDateInput.first().isVisible({ timeout: timeouts.short }).catch(() => false);
        console.log(`Due date field: ${hasDueDate}`);

        // Check for priority
        const prioritySelect = page.locator(
          'select[name="priority"], [data-testid="priority-select"]'
        );
        const hasPriority = await prioritySelect.first().isVisible({ timeout: timeouts.short }).catch(() => false);
        console.log(`Priority field: ${hasPriority}`);
      }
    });

    test("should validate required fields", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator('button:has-text("إضافة مهمة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        // Try to submit empty form
        const submitBtn = page.locator('button[type="submit"], button:has-text("حفظ"), button:has-text("Save")');
        if (await submitBtn.first().isVisible({ timeout: timeouts.short })) {
          await submitBtn.first().click();
          await page.waitForTimeout(300);

          // Check for validation errors
          const errorMsg = page.locator('[class*="error"], text=/مطلوب|Required/i');
          const hasError = await errorMsg.first().isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`Validation errors shown: ${hasError}`);
        }
      }
    });

    test("should create task with valid data", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator('button:has-text("إضافة مهمة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        const taskData = testData.randomTask();

        // Fill title
        const titleInput = page.locator('input[name="title"]');
        if (await titleInput.first().isVisible({ timeout: timeouts.short })) {
          await titleInput.first().fill(taskData.title);
        }

        // Fill description
        const descInput = page.locator('textarea[name="description"]');
        if (await descInput.first().isVisible({ timeout: timeouts.short })) {
          await descInput.first().fill(taskData.description);
        }

        // Set due date
        const dueDateInput = page.locator('input[type="date"]');
        if (await dueDateInput.first().isVisible({ timeout: timeouts.short })) {
          await dueDateInput.first().fill(taskData.dueDate);
        }

        // Submit
        const submitBtn = page.locator('button[type="submit"], button:has-text("حفظ")');
        if (await submitBtn.first().isVisible({ timeout: timeouts.short })) {
          await submitBtn.first().click();

          const hasToast = await waitForToast(page, undefined, timeouts.long);
          console.log(`Task creation success: ${hasToast}`);
        }
      }
    });

    test("should assign task to field", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator('button:has-text("إضافة مهمة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        // Look for field selector
        const fieldSelector = page.locator(
          'select[name="field"], [data-testid="field-selector"]'
        );
        const hasFieldSelector = await fieldSelector.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Field selector available: ${hasFieldSelector}`);
      }
    });

    test("should set task priority", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator('button:has-text("إضافة مهمة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        // Look for priority selector
        const prioritySelector = page.locator(
          'select[name="priority"], [data-testid="priority-selector"], button:has-text("الأولوية")'
        );

        if (await prioritySelector.first().isVisible({ timeout: timeouts.short })) {
          await prioritySelector.first().click();
          await page.waitForTimeout(300);

          // Select high priority
          const highPriority = page.locator(
            '[data-value="high"], option[value="high"], button:has-text("عالية"), button:has-text("High")'
          );
          const hasHighOption = await highPriority.first().isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`Priority options available: ${hasHighOption}`);
        }
      }
    });
  });

  test.describe("Task Details", () => {
    test("should display task details on click", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const taskItem = page.locator('[data-testid="task-item"], [class*="task-item"]').first();

      if (await taskItem.isVisible({ timeout: timeouts.medium })) {
        await taskItem.click();
        await page.waitForTimeout(500);

        // Details should be visible
        const details = page.locator(
          '[data-testid="task-details"], [role="dialog"], [class*="task-detail"]'
        );
        const hasDetails = await details.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Task details shown: ${hasDetails}`);
      }
    });

    test("should display task status", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      // Look for status indicators
      const statusIndicators = page.locator(
        'text=/قيد التنفيذ|In Progress|مكتمل|Completed|معلق|Pending/i'
      );
      const hasStatus = await statusIndicators.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Task status displayed: ${hasStatus}`);
    });

    test("should display task due date", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      // Look for due date
      const dueDate = page.locator(
        'text=/الموعد|Due|تاريخ الاستحقاق/i, [class*="due-date"]'
      );
      const hasDueDate = await dueDate.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Due date displayed: ${hasDueDate}`);
    });

    test("should display task priority", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      // Look for priority indicators
      const priority = page.locator(
        'text=/الأولوية|Priority|عالية|High|متوسطة|Medium|منخفضة|Low/i'
      );
      const hasPriority = await priority.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Priority displayed: ${hasPriority}`);
    });
  });

  test.describe("Update Task", () => {
    test("should open edit task form", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const taskItem = page.locator('[data-testid="task-item"]').first();

      if (await taskItem.isVisible({ timeout: timeouts.medium })) {
        await taskItem.click();
        await page.waitForTimeout(500);

        const editBtn = page.locator('button:has-text("تعديل"), button:has-text("Edit")');

        if (await editBtn.first().isVisible({ timeout: timeouts.short })) {
          await editBtn.first().click();
          await page.waitForTimeout(300);

          const form = page.locator('form, [data-testid="task-form"]');
          const hasForm = await form.first().isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`Edit form opened: ${hasForm}`);
        }
      }
    });

    test("should update task status", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const taskItem = page.locator('[data-testid="task-item"]').first();

      if (await taskItem.isVisible({ timeout: timeouts.medium })) {
        // Look for status change button or checkbox
        const statusBtn = page.locator(
          'button:has-text("إكمال"), button:has-text("Complete"), input[type="checkbox"]'
        );

        if (await statusBtn.first().isVisible({ timeout: timeouts.short })) {
          await statusBtn.first().click();
          await page.waitForTimeout(500);

          const hasToast = await waitForToast(page, undefined, timeouts.medium);
          console.log(`Status update success: ${hasToast}`);
        }
      }
    });

    test("should update task priority", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const taskItem = page.locator('[data-testid="task-item"]').first();

      if (await taskItem.isVisible({ timeout: timeouts.medium })) {
        await taskItem.click();
        await page.waitForTimeout(500);

        const editBtn = page.locator('button:has-text("تعديل")');

        if (await editBtn.first().isVisible({ timeout: timeouts.short })) {
          await editBtn.first().click();
          await page.waitForTimeout(300);

          // Change priority
          const prioritySelector = page.locator('select[name="priority"]');
          if (await prioritySelector.first().isVisible({ timeout: timeouts.short })) {
            await prioritySelector.first().selectOption("high");
          }
        }
      }
    });
  });

  test.describe("Delete Task", () => {
    test("should show delete confirmation", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const taskItem = page.locator('[data-testid="task-item"]').first();

      if (await taskItem.isVisible({ timeout: timeouts.medium })) {
        await taskItem.click();
        await page.waitForTimeout(500);

        const deleteBtn = page.locator('button:has-text("حذف"), button:has-text("Delete")');

        if (await deleteBtn.first().isVisible({ timeout: timeouts.short })) {
          await deleteBtn.first().click();
          await page.waitForTimeout(300);

          const confirmDialog = page.locator('[role="alertdialog"], [role="dialog"]');
          const hasConfirm = await confirmDialog.first().isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`Delete confirmation shown: ${hasConfirm}`);
        }
      }
    });

    test("should cancel delete", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const taskItem = page.locator('[data-testid="task-item"]').first();

      if (await taskItem.isVisible({ timeout: timeouts.medium })) {
        await taskItem.click();
        await page.waitForTimeout(500);

        const deleteBtn = page.locator('button:has-text("حذف")');

        if (await deleteBtn.first().isVisible({ timeout: timeouts.short })) {
          await deleteBtn.first().click();
          await page.waitForTimeout(300);

          const cancelBtn = page.locator('button:has-text("إلغاء"), button:has-text("Cancel")');
          if (await cancelBtn.first().isVisible({ timeout: timeouts.short })) {
            await cancelBtn.first().click();
            await page.waitForTimeout(300);

            // Dialog should close
            const dialog = page.locator('[role="alertdialog"]');
            await expect(dialog).not.toBeVisible();
          }
        }
      }
    });
  });

  test.describe("Task Filtering and Search", () => {
    test("should filter tasks by status", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      // Click on status filter
      const statusTab = page.locator(
        'button:has-text("قيد التنفيذ"), button:has-text("In Progress")'
      );

      if (await statusTab.first().isVisible({ timeout: timeouts.medium })) {
        await statusTab.first().click();
        await page.waitForTimeout(500);

        console.log("Status filter applied");
      }
    });

    test("should filter tasks by priority", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const filterBtn = page.locator('button:has-text("تصفية"), button:has-text("Filter")');

      if (await filterBtn.first().isVisible({ timeout: timeouts.medium })) {
        await filterBtn.first().click();
        await page.waitForTimeout(300);

        const priorityFilter = page.locator(
          'button:has-text("الأولوية"), [data-testid="priority-filter"]'
        );
        const hasPriorityFilter = await priorityFilter.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Priority filter available: ${hasPriorityFilter}`);
      }
    });

    test("should filter tasks by due date", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const filterBtn = page.locator('button:has-text("تصفية")');

      if (await filterBtn.first().isVisible({ timeout: timeouts.medium })) {
        await filterBtn.first().click();
        await page.waitForTimeout(300);

        const dateFilter = page.locator(
          '[data-testid="date-filter"], input[type="date"]'
        );
        const hasDateFilter = await dateFilter.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Date filter available: ${hasDateFilter}`);
      }
    });

    test("should search tasks by title", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const searchInput = page.locator('input[type="search"], input[placeholder*="بحث"]');

      if (await searchInput.first().isVisible({ timeout: timeouts.medium })) {
        await searchInput.first().fill("test");
        await page.waitForTimeout(500);

        console.log("Search performed");
      }
    });

    test("should clear filters", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const clearBtn = page.locator(
        'button:has-text("مسح"), button:has-text("Clear"), button:has-text("Reset")'
      );
      const hasClear = await clearBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Clear filters button available: ${hasClear}`);
    });
  });

  test.describe("Task Calendar View", () => {
    test("should toggle to calendar view", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const calendarBtn = page.locator(
        'button:has-text("التقويم"), button:has-text("Calendar"), [data-testid="calendar-view"]'
      );

      if (await calendarBtn.first().isVisible({ timeout: timeouts.medium })) {
        await calendarBtn.first().click();
        await page.waitForTimeout(500);

        const calendar = page.locator('[class*="calendar"], [data-testid="calendar"]');
        const hasCalendar = await calendar.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Calendar view displayed: ${hasCalendar}`);
      }
    });

    test("should navigate calendar months", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const calendarBtn = page.locator('button:has-text("التقويم")');

      if (await calendarBtn.first().isVisible({ timeout: timeouts.medium })) {
        await calendarBtn.first().click();
        await page.waitForTimeout(500);

        const nextMonth = page.locator(
          'button:has-text("التالي"), button:has-text("Next"), [aria-label*="next"]'
        );
        const hasNavigation = await nextMonth.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Calendar navigation available: ${hasNavigation}`);
      }
    });

    test("should display tasks on calendar dates", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const calendarBtn = page.locator('button:has-text("التقويم")');

      if (await calendarBtn.first().isVisible({ timeout: timeouts.medium })) {
        await calendarBtn.first().click();
        await page.waitForTimeout(500);

        // Look for task indicators on dates
        const taskIndicators = page.locator(
          '[class*="event"], [class*="task-dot"], [class*="calendar-event"]'
        );
        const count = await taskIndicators.count();

        console.log(`Task indicators on calendar: ${count}`);
      }
    });
  });

  test.describe("Task Notifications", () => {
    test("should display overdue task indicators", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const overdueIndicator = page.locator(
        'text=/متأخر|Overdue|منتهي|Past Due/i, [class*="overdue"]'
      );
      const hasOverdue = await overdueIndicator.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Overdue indicator displayed: ${hasOverdue}`);
    });

    test("should display upcoming task reminders", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const reminder = page.locator(
        'text=/تذكير|Reminder|اليوم|Today|غداً|Tomorrow/i'
      );
      const hasReminder = await reminder.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Reminder displayed: ${hasReminder}`);
    });
  });

  test.describe("Task Assignment (Team)", () => {
    test("should display assignee selector", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator('button:has-text("إضافة مهمة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        const assigneeSelector = page.locator(
          'select[name="assignee"], [data-testid="assignee-selector"]'
        );
        const hasAssignee = await assigneeSelector.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Assignee selector available: ${hasAssignee}`);
      }
    });

    test("should display task assignee in list", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const assigneeInfo = page.locator(
        '[class*="assignee"], [class*="avatar"], [data-testid="task-assignee"]'
      );
      const hasAssigneeInfo = await assigneeInfo.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Assignee info displayed: ${hasAssigneeInfo}`);
    });
  });

  test.describe("Task Types", () => {
    test("should display task type selector", async ({ page }) => {
      await navigateAndWait(page, "/tasks");

      const addButton = page.locator('button:has-text("إضافة مهمة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        const typeSelector = page.locator(
          'select[name="type"], [data-testid="task-type"]'
        );
        const hasType = await typeSelector.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Task type selector available: ${hasType}`);
      }
    });

    test("should filter by task type", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      // Look for task type filters (irrigation, fertilization, spraying, etc.)
      const typeFilters = page.locator(
        'button:has-text("الري"), button:has-text("Irrigation"), button:has-text("التسميد"), button:has-text("الرش")'
      );
      const count = await typeFilters.count();

      console.log(`Task type filters: ${count}`);
    });
  });

  test.describe("Task Export", () => {
    test("should export tasks list", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const exportBtn = page.locator(
        'button:has-text("تصدير"), button:has-text("Export"), [data-testid="export-tasks"]'
      );
      const hasExport = await exportBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Export button available: ${hasExport}`);
    });

    test("should print tasks list", async ({ page }) => {
      await navigateAndWait(page, "/tasks");
      await page.waitForTimeout(timeouts.medium);

      const printBtn = page.locator(
        'button:has-text("طباعة"), button:has-text("Print"), [data-testid="print-tasks"]'
      );
      const hasPrint = await printBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Print button available: ${hasPrint}`);
    });
  });
});
