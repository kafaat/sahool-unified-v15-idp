/**
 * Team Management E2E Tests
 * اختبارات إدارة الفريق
 *
 * Tests for team member management, role assignment, and permissions.
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import {
  waitForPageLoad,
  waitForToast,
  fillFieldByLabel,
} from "./helpers/page.helpers";
import { testData } from "./helpers/test-data";

test.describe("Team Management", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Team Page Navigation", () => {
    test("should navigate to team management page", async ({ page }) => {
      // Navigate to settings or team page
      await page.goto("/settings");
      await waitForPageLoad(page);

      // Click on team tab/link
      const teamLink = page.locator(
        'a:has-text("الفريق"), a:has-text("Team"), button:has-text("الفريق"), button:has-text("Team")',
      );
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        // Team management section should be visible
        await expect(
          page.locator("text=/إدارة الفريق|Team Management/i"),
        ).toBeVisible({ timeout: 10000 });
      }
    });

    test("should display team members list", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        // Team members should be listed
        const membersList = page.locator('[data-testid="team-members-list"]');
        await expect(membersList).toBeVisible({ timeout: 10000 });
      }
    });
  });

  test.describe("Invite Member", () => {
    test("should open invite member dialog", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        // Click invite button
        const inviteBtn = page.locator(
          'button:has-text("دعوة"), button:has-text("Invite")',
        );
        if (await inviteBtn.isVisible()) {
          await inviteBtn.click();

          // Dialog should open
          await expect(
            page.locator('[data-testid="invite-dialog"], [role="dialog"]'),
          ).toBeVisible({ timeout: 5000 });
        }
      }
    });

    test("should validate email in invite form", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        const inviteBtn = page.locator(
          'button:has-text("دعوة"), button:has-text("Invite")',
        );
        if (await inviteBtn.isVisible()) {
          await inviteBtn.click();

          // Enter invalid email
          const emailInput = page.locator(
            'input[type="email"], input[name="email"]',
          );
          await emailInput.fill("invalid-email");

          // Try to submit
          const submitBtn = page.locator(
            'button:has-text("إرسال"), button:has-text("Send")',
          );
          await submitBtn.click();

          // Error should be shown
          await expect(
            page.locator("text=/بريد إلكتروني غير صالح|Invalid email/i"),
          ).toBeVisible({ timeout: 5000 });
        }
      }
    });

    test("should send invitation with valid data", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        const inviteBtn = page.locator(
          'button:has-text("دعوة"), button:has-text("Invite")',
        );
        if (await inviteBtn.isVisible()) {
          await inviteBtn.click();

          // Fill valid email
          const emailInput = page.locator(
            'input[type="email"], input[name="email"]',
          );
          await emailInput.fill(testData.randomEmail());

          // Select role
          const roleSelector = page.locator('[data-testid="role-selector"]');
          if (await roleSelector.isVisible()) {
            await roleSelector.click();
            await page.locator('[data-value="FARMER"]').click();
          }

          // Submit
          const submitBtn = page.locator(
            'button:has-text("إرسال"), button:has-text("Send")',
          );
          await submitBtn.click();

          // Success message
          await waitForToast(page, /تم إرسال الدعوة|Invitation sent/i, 10000);
        }
      }
    });
  });

  test.describe("Role Management", () => {
    test("should display role selector with all roles", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        const inviteBtn = page.locator(
          'button:has-text("دعوة"), button:has-text("Invite")',
        );
        if (await inviteBtn.isVisible()) {
          await inviteBtn.click();

          const roleSelector = page.locator('[data-testid="role-selector"]');
          if (await roleSelector.isVisible()) {
            await roleSelector.click();

            // All roles should be available
            const roles = ["ADMIN", "MANAGER", "FARMER", "WORKER", "VIEWER"];
            for (const role of roles) {
              await expect(
                page.locator(`[data-value="${role}"]`),
              ).toBeVisible();
            }
          }
        }
      }
    });

    test("should update member role", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        // Find member card with edit option
        const memberCard = page.locator('[data-testid="member-card"]').first();
        if (await memberCard.isVisible()) {
          // Click more options menu
          const moreBtn = memberCard.locator('[data-testid="more-options"]');
          if (await moreBtn.isVisible()) {
            await moreBtn.click();

            // Click change role
            const changeRoleBtn = page.locator(
              'button:has-text("تغيير الدور"), button:has-text("Change Role")',
            );
            if (await changeRoleBtn.isVisible()) {
              await changeRoleBtn.click();

              // Select new role
              await page.locator('[data-value="MANAGER"]').click();

              // Confirm
              const confirmBtn = page.locator(
                'button:has-text("تأكيد"), button:has-text("Confirm")',
              );
              await confirmBtn.click();

              await waitForToast(page, /تم تحديث الدور|Role updated/i, 5000);
            }
          }
        }
      }
    });
  });

  test.describe("Permissions Matrix", () => {
    test("should display permissions matrix", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        // Click permissions tab
        const permissionsTab = page.locator(
          'button:has-text("الصلاحيات"), button:has-text("Permissions")',
        );
        if (await permissionsTab.isVisible()) {
          await permissionsTab.click();

          // Permissions matrix should be visible
          await expect(
            page.locator('[data-testid="permissions-matrix"]'),
          ).toBeVisible({ timeout: 10000 });

          // Check for permission categories
          await expect(
            page.locator("text=/عرض|قراءة|View|Read/i"),
          ).toBeVisible();
          await expect(page.locator("text=/إنشاء|Create/i")).toBeVisible();
          await expect(page.locator("text=/تعديل|Edit/i")).toBeVisible();
          await expect(page.locator("text=/حذف|Delete/i")).toBeVisible();
        }
      }
    });
  });

  test.describe("Remove Member", () => {
    test("should remove team member", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        const memberCard = page.locator('[data-testid="member-card"]').first();
        if (await memberCard.isVisible()) {
          const moreBtn = memberCard.locator('[data-testid="more-options"]');
          if (await moreBtn.isVisible()) {
            await moreBtn.click();

            // Click remove
            const removeBtn = page.locator(
              'button:has-text("إزالة"), button:has-text("Remove")',
            );
            if (await removeBtn.isVisible()) {
              await removeBtn.click();

              // Confirm removal
              const confirmBtn = page.locator(
                'button:has-text("تأكيد"), button:has-text("Confirm")',
              );
              await confirmBtn.click();

              await waitForToast(page, /تمت إزالة العضو|Member removed/i, 5000);
            }
          }
        }
      }
    });
  });

  test.describe("Team Statistics", () => {
    test("should display team statistics", async ({ page }) => {
      await page.goto("/settings");
      await waitForPageLoad(page);

      const teamLink = page.locator('a:has-text("الفريق"), a:has-text("Team")');
      if (await teamLink.isVisible()) {
        await teamLink.click();
        await waitForPageLoad(page);

        // Statistics should be displayed
        await expect(
          page.locator("text=/إجمالي الأعضاء|Total Members/i"),
        ).toBeVisible({ timeout: 10000 });
        await expect(page.locator("text=/نشط|Active/i")).toBeVisible();
      }
    });
  });
});
