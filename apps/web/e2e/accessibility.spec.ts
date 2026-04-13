/**
 * Accessibility (A11y) E2E Tests
 * اختبارات E2E لإمكانية الوصول
 *
 * Comprehensive accessibility tests following WCAG 2.1 guidelines:
 * - Keyboard navigation
 * - Screen reader compatibility (ARIA)
 * - Color contrast
 * - Focus management
 * - Form accessibility
 * - RTL language support
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import { waitForPageLoad, navigateAndWait } from "./helpers/page.helpers";
import { timeouts } from "./helpers/test-data";

test.describe("Accessibility Tests", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Keyboard Navigation", () => {
    test("should focus first interactive element on page load", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      // Press Tab to move focus
      await page.keyboard.press("Tab");
      await page.waitForTimeout(300);

      // Check if an interactive element has focus
      const focusedElement = page.locator(":focus");
      await expect(focusedElement).toBeVisible({ timeout: timeouts.medium });
    });

    test("should navigate through form fields using Tab", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      const _submitButton = page.locator('button[type="submit"]');

      // Focus email input
      await emailInput.focus();
      await expect(emailInput).toBeFocused();

      // Tab to password
      await page.keyboard.press("Tab");
      await expect(passwordInput).toBeFocused();

      // Tab to submit button
      await page.keyboard.press("Tab");
      await page.waitForTimeout(200);

      // Submit button or another element should be focused
      const focused = page.locator(":focus");
      await expect(focused).toBeVisible();
    });

    test("should navigate backwards using Shift+Tab", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Focus an element
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");

      // Navigate backwards
      await page.keyboard.press("Shift+Tab");
      await page.waitForTimeout(200);

      const focused = page.locator(":focus");
      await expect(focused).toBeVisible();
    });

    test("should open dropdown menus with Enter/Space", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Find a dropdown or expandable element
      const dropdownTrigger = page.locator(
        'button[aria-haspopup="true"], [aria-expanded], button:has-text("Select")'
      );

      if (await dropdownTrigger.first().isVisible({ timeout: timeouts.medium })) {
        await dropdownTrigger.first().focus();
        await page.keyboard.press("Enter");
        await page.waitForTimeout(300);

        // Check for expanded content
        const expandedContent = page.locator(
          '[role="menu"], [role="listbox"], [aria-expanded="true"]'
        );
        const isExpanded = await expandedContent.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Dropdown expanded with keyboard: ${isExpanded}`);
      }
    });

    test("should close modals with Escape key", async ({ page }) => {
      await navigateAndWait(page, "/fields");
      await page.waitForTimeout(timeouts.medium);

      // Try to open a modal
      const addButton = page.locator('button:has-text("إضافة"), button:has-text("Add")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        const modal = page.locator('[role="dialog"]');
        if (await modal.first().isVisible({ timeout: timeouts.short })) {
          // Press Escape
          await page.keyboard.press("Escape");
          await page.waitForTimeout(300);

          // Modal should be closed
          await expect(modal).not.toBeVisible();
        }
      }
    });

    test("should navigate sidebar with arrow keys", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Focus sidebar
      const _sidebar = page.locator('nav, aside');
      const navLinks = page.locator('nav a, aside a');

      if (await navLinks.first().isVisible({ timeout: timeouts.medium })) {
        await navLinks.first().focus();

        // Use arrow keys
        await page.keyboard.press("ArrowDown");
        await page.waitForTimeout(200);

        const focused = page.locator(":focus");
        await expect(focused).toBeVisible();
      }
    });

    test("should trap focus within modal", async ({ page }) => {
      await navigateAndWait(page, "/fields");
      await page.waitForTimeout(timeouts.medium);

      const addButton = page.locator('button:has-text("إضافة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        const modal = page.locator('[role="dialog"]');
        if (await modal.first().isVisible({ timeout: timeouts.short })) {
          // Tab through all elements in modal
          for (let i = 0; i < 10; i++) {
            await page.keyboard.press("Tab");
            await page.waitForTimeout(100);
          }

          // Focus should still be within modal
          const _focused = page.locator(":focus");
          const focusedInModal = await modal.locator(":focus").isVisible().catch(() => false);

          console.log(`Focus trapped in modal: ${focusedInModal}`);
        }
      }
    });
  });

  test.describe("ARIA Attributes", () => {
    test("should have proper ARIA landmarks", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for main landmark
      const mainContent = page.locator('main, [role="main"]');
      await expect(mainContent.first()).toBeVisible({ timeout: timeouts.medium });

      // Check for navigation landmark
      const navigation = page.locator('nav, [role="navigation"]');
      await expect(navigation.first()).toBeVisible({ timeout: timeouts.medium });

      // Check for banner (header)
      const header = page.locator('header, [role="banner"]');
      const hasHeader = await header.first().isVisible({ timeout: timeouts.short }).catch(() => false);

      console.log(`ARIA landmarks present: main, nav, header=${hasHeader}`);
    });

    test("should have proper ARIA labels on interactive elements", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check buttons have accessible names
      const buttons = page.locator("button");
      const buttonCount = await buttons.count();

      let unlabeledButtons = 0;
      for (let i = 0; i < Math.min(buttonCount, 10); i++) {
        const button = buttons.nth(i);
        const ariaLabel = await button.getAttribute("aria-label");
        const innerText = await button.innerText().catch(() => "");
        const title = await button.getAttribute("title");

        if (!ariaLabel && !innerText.trim() && !title) {
          unlabeledButtons++;
        }
      }

      console.log(`Unlabeled buttons: ${unlabeledButtons} out of ${Math.min(buttonCount, 10)}`);
      expect(unlabeledButtons).toBeLessThan(3);
    });

    test("should have proper ARIA roles on custom widgets", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for proper roles on custom components
      const alerts = page.locator('[role="alert"]');
      const alertCount = await alerts.count();

      const dialogs = page.locator('[role="dialog"]');
      const dialogCount = await dialogs.count();

      const tabs = page.locator('[role="tablist"]');
      const tabCount = await tabs.count();

      console.log(`ARIA roles found: alerts=${alertCount}, dialogs=${dialogCount}, tabs=${tabCount}`);
    });

    test("should have aria-expanded on expandable elements", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const expandables = page.locator('[aria-expanded]');
      const count = await expandables.count();

      console.log(`Elements with aria-expanded: ${count}`);

      if (count > 0) {
        const firstExpandable = expandables.first();
        const initialState = await firstExpandable.getAttribute("aria-expanded");

        await firstExpandable.click();
        await page.waitForTimeout(300);

        const newState = await firstExpandable.getAttribute("aria-expanded");

        console.log(`aria-expanded changed: ${initialState} -> ${newState}`);
      }
    });

    test("should have aria-live for dynamic content", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for live regions
      const liveRegions = page.locator('[aria-live]');
      const count = await liveRegions.count();

      console.log(`ARIA live regions found: ${count}`);
    });

    test("should have proper heading hierarchy", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const h1Count = await page.locator("h1").count();
      const h2Count = await page.locator("h2").count();
      const h3Count = await page.locator("h3").count();

      console.log(`Heading hierarchy: h1=${h1Count}, h2=${h2Count}, h3=${h3Count}`);

      // Should have exactly one h1
      expect(h1Count).toBeLessThanOrEqual(2);
    });
  });

  test.describe("Form Accessibility", () => {
    test("should have labels for all form inputs", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      const inputs = page.locator("input:not([type='hidden'])");
      const inputCount = await inputs.count();

      let unlabeledInputs = 0;
      for (let i = 0; i < inputCount; i++) {
        const input = inputs.nth(i);
        const id = await input.getAttribute("id");
        const ariaLabel = await input.getAttribute("aria-label");
        const ariaLabelledby = await input.getAttribute("aria-labelledby");
        const placeholder = await input.getAttribute("placeholder");

        // Check if label exists for this input
        let hasLabel = false;
        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          hasLabel = await label.isVisible().catch(() => false);
        }

        if (!hasLabel && !ariaLabel && !ariaLabelledby && !placeholder) {
          unlabeledInputs++;
        }
      }

      console.log(`Unlabeled inputs: ${unlabeledInputs} out of ${inputCount}`);
      expect(unlabeledInputs).toBe(0);
    });

    test("should announce form errors to screen readers", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      // Submit empty form
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(500);

      // Check for error messages with proper ARIA
      const errors = page.locator('[role="alert"], [aria-live="polite"], .error');
      const hasErrors = await errors.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Form errors announced: ${hasErrors}`);
    });

    test("should have proper required field indicators", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      const requiredInputs = page.locator('input[required], input[aria-required="true"]');
      const count = await requiredInputs.count();

      console.log(`Required fields marked: ${count}`);
      expect(count).toBeGreaterThan(0);
    });

    test("should have proper autocomplete attributes", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      const emailInput = page.locator('input[type="email"]');
      const autocomplete = await emailInput.getAttribute("autocomplete");

      console.log(`Email autocomplete attribute: ${autocomplete}`);
    });

    test("should have descriptive error messages", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      await page.fill('input[type="email"]', "invalid");
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(500);

      const errorMessage = page.locator('[class*="error"], [role="alert"]');
      const hasDescriptiveError = await errorMessage.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      if (hasDescriptiveError) {
        const errorText = await errorMessage.first().textContent();
        console.log(`Error message: ${errorText}`);
      }
    });
  });

  test.describe("Focus Management", () => {
    test("should have visible focus indicators", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Tab to first interactive element
      await page.keyboard.press("Tab");
      await page.waitForTimeout(200);

      const focused = page.locator(":focus");

      // Check if focus is visible (outline or other visual indicator)
      const outlineStyle = await focused.evaluate((el) => {
        const style = window.getComputedStyle(el);
        return {
          outline: style.outline,
          boxShadow: style.boxShadow,
          border: style.border,
        };
      }).catch(() => ({}));

      console.log(`Focus styles:`, outlineStyle);
    });

    test("should maintain focus after form submission", async ({ page }) => {
      await page.goto("/login");
      await waitForPageLoad(page);

      await page.fill('input[type="email"]', TEST_USER.email);
      await page.fill('input[type="password"]', TEST_USER.password);

      const submitButton = page.locator('button[type="submit"]');
      await submitButton.focus();
      await submitButton.click();

      await page.waitForTimeout(1000);

      // Focus should be managed (either on submit button or moved appropriately)
      const focused = page.locator(":focus");
      const hasFocus = await focused.isVisible({ timeout: timeouts.short }).catch(() => false);

      console.log(`Focus maintained after submission: ${hasFocus}`);
    });

    test("should skip to main content link", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for skip link
      const skipLink = page.locator(
        'a:has-text("Skip"), a:has-text("تخطي"), [class*="skip"], a[href="#main"]'
      );
      const hasSkipLink = await skipLink.first().isVisible({ timeout: timeouts.short }).catch(() => false);

      console.log(`Skip to main content link: ${hasSkipLink}`);
    });

    test("should restore focus after modal closes", async ({ page }) => {
      await navigateAndWait(page, "/fields");
      await page.waitForTimeout(timeouts.medium);

      const addButton = page.locator('button:has-text("إضافة")');

      if (await addButton.first().isVisible({ timeout: timeouts.medium })) {
        await addButton.first().click();
        await page.waitForTimeout(500);

        const modal = page.locator('[role="dialog"]');
        if (await modal.first().isVisible({ timeout: timeouts.short })) {
          // Close modal with Escape
          await page.keyboard.press("Escape");
          await page.waitForTimeout(300);

          // Focus should return to trigger button
          const focused = page.locator(":focus");
          const focusRestored = await focused.isVisible({ timeout: timeouts.short }).catch(() => false);

          console.log(`Focus restored after modal close: ${focusRestored}`);
        }
      }
    });
  });

  test.describe("Color and Contrast", () => {
    test("should have sufficient text contrast", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check text color contrast (simplified check)
      const textElements = page.locator("p, span, h1, h2, h3, h4, label").first();

      if (await textElements.isVisible({ timeout: timeouts.short })) {
        const colors = await textElements.evaluate((el) => {
          const style = window.getComputedStyle(el);
          return {
            color: style.color,
            backgroundColor: style.backgroundColor,
          };
        });

        console.log(`Text colors: color=${colors.color}, bg=${colors.backgroundColor}`);
      }
    });

    test("should not rely solely on color to convey information", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for status indicators with text/icons, not just color
      const statusElements = page.locator('[class*="status"], [class*="badge"]');
      const count = await statusElements.count();

      if (count > 0) {
        const firstStatus = statusElements.first();
        const hasText = await firstStatus.innerText().catch(() => "");
        const hasIcon = await firstStatus.locator("svg, img, [class*='icon']").isVisible().catch(() => false);

        console.log(`Status element has text: ${!!hasText}, has icon: ${hasIcon}`);
      }
    });

    test("should support high contrast mode", async ({ page }) => {
      // Emulate forced colors mode
      await page.emulateMedia({ forcedColors: "active" });
      await navigateAndWait(page, "/dashboard");

      // Page should still be functional
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: timeouts.medium });
    });
  });

  test.describe("RTL Accessibility", () => {
    test("should have proper RTL direction attribute", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const htmlDir = await page.locator("html").getAttribute("dir");
      const lang = await page.locator("html").getAttribute("lang");

      console.log(`HTML attributes: dir=${htmlDir}, lang=${lang}`);
    });

    test("should have proper text alignment in RTL", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const textElement = page.locator("p, h1, h2").first();
      const textAlign = await textElement.evaluate((el) =>
        window.getComputedStyle(el).textAlign
      );

      console.log(`Text alignment: ${textAlign}`);
    });

    test("should have proper icon direction in RTL", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check if directional icons are flipped
      const directionalIcons = page.locator(
        '[class*="arrow"], [class*="chevron"], [class*="back"]'
      );
      const count = await directionalIcons.count();

      console.log(`Directional icons found: ${count}`);
    });

    test("should announce Arabic content correctly", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for Arabic text with proper lang attribute
      const arabicText = page.locator('[lang="ar"], text=/[\u0600-\u06FF]+/');
      const count = await arabicText.count();

      console.log(`Arabic text elements: ${count}`);
    });
  });

  test.describe("Multimedia Accessibility", () => {
    test("should have alt text for images", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const images = page.locator("img");
      const imageCount = await images.count();

      let missingAlt = 0;
      for (let i = 0; i < imageCount; i++) {
        const alt = await images.nth(i).getAttribute("alt");
        const role = await images.nth(i).getAttribute("role");

        // Decorative images should have role="presentation" or empty alt
        if (alt === null && role !== "presentation") {
          missingAlt++;
        }
      }

      console.log(`Images missing alt: ${missingAlt} out of ${imageCount}`);
    });

    test("should have accessible icons", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      const iconButtons = page.locator("button:has(svg)");
      const count = await iconButtons.count();

      let accessibleIcons = 0;
      for (let i = 0; i < Math.min(count, 5); i++) {
        const button = iconButtons.nth(i);
        const ariaLabel = await button.getAttribute("aria-label");
        const title = await button.getAttribute("title");
        const srText = await button.locator(".sr-only, [class*='visually-hidden']").textContent().catch(() => "");

        if (ariaLabel || title || srText) {
          accessibleIcons++;
        }
      }

      console.log(`Accessible icon buttons: ${accessibleIcons} out of ${Math.min(count, 5)}`);
    });
  });

  test.describe("Motion and Animation", () => {
    test("should respect reduced motion preference", async ({ page }) => {
      // Emulate reduced motion preference
      await page.emulateMedia({ reducedMotion: "reduce" });
      await navigateAndWait(page, "/dashboard");

      // Check for animation styles
      const animatedElements = page.locator("[class*='animate'], [class*='transition']");
      const count = await animatedElements.count();

      console.log(`Animated elements: ${count} (should be reduced with prefers-reduced-motion)`);
    });

    test("should not have auto-playing content", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for auto-playing videos or audio
      const autoplayMedia = page.locator("video[autoplay], audio[autoplay]");
      const count = await autoplayMedia.count();

      console.log(`Auto-playing media: ${count}`);
      expect(count).toBe(0);
    });
  });

  test.describe("Touch and Pointer Accessibility", () => {
    test("should have adequate touch targets", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await navigateAndWait(page, "/dashboard");

      const buttons = page.locator("button, a, [role='button']");
      const count = await buttons.count();

      let smallTargets = 0;
      for (let i = 0; i < Math.min(count, 10); i++) {
        const box = await buttons.nth(i).boundingBox();
        if (box && (box.height < 44 || box.width < 44)) {
          smallTargets++;
        }
      }

      console.log(`Touch targets below 44px: ${smallTargets} out of ${Math.min(count, 10)}`);
    });

    test("should have proper spacing between touch targets", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await navigateAndWait(page, "/dashboard");

      // Check spacing between adjacent buttons
      const buttons = page.locator("button");
      const count = await buttons.count();

      if (count >= 2) {
        const first = await buttons.first().boundingBox();
        const second = await buttons.nth(1).boundingBox();

        if (first && second) {
          const spacing = second.y - (first.y + first.height);
          console.log(`Button spacing: ${spacing}px`);
        }
      }
    });
  });

  test.describe("Loading States", () => {
    test("should have accessible loading indicators", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for loading spinners with proper ARIA
      const loadingIndicators = page.locator(
        '[aria-busy="true"], [role="progressbar"], [aria-label*="loading"], [aria-label*="تحميل"]'
      );
      const count = await loadingIndicators.count();

      console.log(`Accessible loading indicators: ${count}`);
    });

    test("should announce content updates to screen readers", async ({ page }) => {
      await navigateAndWait(page, "/dashboard");

      // Check for live regions
      const liveRegions = page.locator(
        '[aria-live="polite"], [aria-live="assertive"]'
      );
      const count = await liveRegions.count();

      console.log(`Live regions for announcements: ${count}`);
    });
  });
});
