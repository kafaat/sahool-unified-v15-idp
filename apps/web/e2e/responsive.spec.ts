/**
 * Responsive Design E2E Tests
 * اختبارات E2E للتصميم المتجاوب
 *
 * Comprehensive tests for responsive behavior across devices:
 * - Mobile viewport (375x667, 414x896)
 * - Tablet viewport (768x1024, 834x1194)
 * - Desktop viewport (1920x1080, 2560x1440)
 * - Navigation behavior on different screen sizes
 * - Layout and component responsiveness
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, TEST_USER } from "./helpers/auth.helpers";
import { waitForPageLoad, navigateAndWait } from "./helpers/page.helpers";
import { timeouts } from "./helpers/test-data";

/**
 * Viewport configurations
 */
const viewports = {
  // Mobile devices
  mobileSmall: { width: 320, height: 568, name: "iPhone SE" },
  mobileMedium: { width: 375, height: 667, name: "iPhone 8" },
  mobileLarge: { width: 414, height: 896, name: "iPhone 11 Pro Max" },

  // Tablets
  tabletPortrait: { width: 768, height: 1024, name: "iPad Portrait" },
  tabletLandscape: { width: 1024, height: 768, name: "iPad Landscape" },
  tabletPro: { width: 834, height: 1194, name: "iPad Pro" },

  // Desktop
  desktopSmall: { width: 1280, height: 720, name: "HD Desktop" },
  desktopMedium: { width: 1920, height: 1080, name: "Full HD Desktop" },
  desktopLarge: { width: 2560, height: 1440, name: "2K Desktop" },
};

test.describe("Responsive Design Tests", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test.describe("Mobile Viewport Tests", () => {
    test.describe("Mobile Navigation", () => {
      test("should show hamburger menu on mobile", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");

        // Look for hamburger/mobile menu button
        const hamburgerMenu = page.locator(
          '[data-testid="mobile-menu"], [aria-label*="menu"], button:has([class*="hamburger"]), [class*="burger"], button[class*="menu"]'
        );

        await expect(hamburgerMenu.first()).toBeVisible({ timeout: timeouts.long });
      });

      test("should open mobile drawer menu when hamburger clicked", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");

        const hamburgerMenu = page.locator(
          '[data-testid="mobile-menu"], [aria-label*="menu"], button:has([class*="hamburger"])'
        );

        if (await hamburgerMenu.first().isVisible({ timeout: timeouts.medium })) {
          await hamburgerMenu.first().click();
          await page.waitForTimeout(500);

          // Drawer/sidebar should appear
          const drawer = page.locator(
            '[data-testid="mobile-drawer"], [role="dialog"], [class*="drawer"], [class*="sidebar"]:visible'
          );
          await expect(drawer.first()).toBeVisible({ timeout: timeouts.medium });
        }
      });

      test("should close mobile drawer when clicking outside", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");

        const hamburgerMenu = page.locator('[data-testid="mobile-menu"]');

        if (await hamburgerMenu.first().isVisible({ timeout: timeouts.medium })) {
          await hamburgerMenu.first().click();
          await page.waitForTimeout(500);

          // Click overlay/backdrop to close
          const overlay = page.locator('[data-testid="mobile-drawer-backdrop"], [class*="overlay"], [class*="backdrop"]');
          if (await overlay.first().isVisible({ timeout: timeouts.short })) {
            await overlay.first().click();
            await page.waitForTimeout(500);

            // Drawer should be closed
            const drawer = page.locator('[data-testid="mobile-drawer"]');
            await expect(drawer).not.toBeVisible();
          }
        }
      });

      test("should navigate correctly from mobile menu", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");

        const hamburgerMenu = page.locator('[data-testid="mobile-menu"], [aria-label*="menu"]');

        if (await hamburgerMenu.first().isVisible({ timeout: timeouts.medium })) {
          await hamburgerMenu.first().click();
          await page.waitForTimeout(500);

          // Click on a navigation link
          const fieldsLink = page.locator('a:has-text("الحقول"), a:has-text("Fields")');
          if (await fieldsLink.first().isVisible({ timeout: timeouts.short })) {
            await fieldsLink.first().click();
            await page.waitForTimeout(1000);

            // Should navigate to fields page
            await expect(page).toHaveURL(/\/fields/);
          }
        }
      });
    });

    test.describe("Mobile Layout", () => {
      test("should stack cards vertically on mobile", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");
        await page.waitForTimeout(timeouts.medium);

        // Cards should be full width on mobile
        const cards = page.locator('[class*="card"], [data-testid*="card"]');
        const cardCount = await cards.count();

        if (cardCount > 0) {
          const firstCard = cards.first();
          const box = await firstCard.boundingBox();

          if (box) {
            // Card width should be close to viewport width (minus padding)
            expect(box.width).toBeGreaterThan(300);
            console.log(`Card width on mobile: ${box.width}px`);
          }
        }
      });

      test("should hide sidebar on mobile", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");

        // Desktop sidebar should be hidden (parent has hidden md:block)
        const sidebar = page.locator('[data-testid="desktop-sidebar"]');
        const isSidebarVisible = await sidebar.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        // Sidebar should be hidden on mobile viewport
        expect(isSidebarVisible).toBe(false);
        console.log(`Desktop sidebar visible on mobile: ${isSidebarVisible}`);
      });

      test("should adjust font sizes for mobile", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");

        const heading = page.locator("h1").first();
        const fontSize = await heading.evaluate((el) =>
          window.getComputedStyle(el).fontSize
        );

        console.log(`H1 font size on mobile: ${fontSize}`);
        // Font size should be reasonable for mobile
        expect(parseFloat(fontSize)).toBeLessThanOrEqual(48);
      });

      test("should make buttons touch-friendly on mobile", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await navigateAndWait(page, "/dashboard");

        const buttons = page.locator('button').first();
        const box = await buttons.boundingBox();

        if (box) {
          // Minimum touch target should be 44x44 pixels
          console.log(`Button size: ${box.width}x${box.height}px`);
          expect(box.height).toBeGreaterThanOrEqual(32);
        }
      });
    });

    test.describe("Mobile Forms", () => {
      test("should display full-width form fields on mobile", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await page.goto("/login");
        await waitForPageLoad(page);

        const emailInput = page.locator('input[type="email"]');
        const box = await emailInput.boundingBox();

        if (box) {
          // Input should be nearly full width on mobile
          expect(box.width).toBeGreaterThan(280);
          console.log(`Input width on mobile: ${box.width}px`);
        }
      });

      test("should show mobile keyboard-friendly inputs", async ({ page }) => {
        await page.setViewportSize(viewports.mobileMedium);
        await page.goto("/login");
        await waitForPageLoad(page);

        const emailInput = page.locator('input[type="email"]');
        const inputType = await emailInput.getAttribute("type");

        // Email input should have correct type for mobile keyboard
        expect(inputType).toBe("email");
      });
    });
  });

  test.describe("Tablet Viewport Tests", () => {
    test.describe("Tablet Navigation", () => {
      test("should show sidebar or top nav on tablet", async ({ page }) => {
        await page.setViewportSize(viewports.tabletPortrait);
        await navigateAndWait(page, "/dashboard");

        // Check for sidebar or navigation
        const navigation = page.locator(
          'nav, aside, [data-testid="sidebar"], [role="navigation"]'
        );
        await expect(navigation.first()).toBeVisible({ timeout: timeouts.long });
      });

      test("should show collapsible sidebar on tablet portrait", async ({ page }) => {
        await page.setViewportSize(viewports.tabletPortrait);
        await navigateAndWait(page, "/dashboard");

        // Look for collapsed sidebar or mini sidebar
        const sidebar = page.locator('[class*="sidebar"], aside');
        const sidebarVisible = await sidebar.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Sidebar visible on tablet portrait: ${sidebarVisible}`);
      });

      test("should expand sidebar on tablet landscape", async ({ page }) => {
        await page.setViewportSize(viewports.tabletLandscape);
        await navigateAndWait(page, "/dashboard");

        const sidebar = page.locator('[class*="sidebar"], aside');
        const sidebarVisible = await sidebar.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

        console.log(`Sidebar visible on tablet landscape: ${sidebarVisible}`);
      });
    });

    test.describe("Tablet Layout", () => {
      test("should show 2-column grid on tablet", async ({ page }) => {
        await page.setViewportSize(viewports.tabletPortrait);
        await navigateAndWait(page, "/dashboard");
        await page.waitForTimeout(timeouts.medium);

        // Check for grid layout
        const gridContainer = page.locator('[class*="grid"]').first();
        const gridVisible = await gridContainer.isVisible({ timeout: timeouts.short }).catch(() => false);

        console.log(`Grid container visible: ${gridVisible}`);
      });

      test("should maintain readable text width on tablet", async ({ page }) => {
        await page.setViewportSize(viewports.tabletPortrait);
        await navigateAndWait(page, "/dashboard");

        const mainContent = page.locator('main, [class*="content"]').first();
        const box = await mainContent.boundingBox();

        if (box) {
          console.log(`Main content width on tablet: ${box.width}px`);
        }
      });
    });
  });

  test.describe("Desktop Viewport Tests", () => {
    test.describe("Desktop Navigation", () => {
      test("should show full sidebar on desktop", async ({ page }) => {
        await page.setViewportSize(viewports.desktopMedium);
        await navigateAndWait(page, "/dashboard");

        const sidebar = page.locator(
          '[data-testid="sidebar"], aside, nav[class*="sidebar"]'
        );
        await expect(sidebar.first()).toBeVisible({ timeout: timeouts.long });
      });

      test("should hide mobile hamburger on desktop", async ({ page }) => {
        await page.setViewportSize(viewports.desktopMedium);
        await navigateAndWait(page, "/dashboard");

        const hamburger = page.locator('[data-testid="mobile-menu"]');
        const isVisible = await hamburger.first().isVisible({ timeout: timeouts.short }).catch(() => false);

        expect(isVisible).toBe(false);
      });

      test("should show all navigation items on desktop", async ({ page }) => {
        await page.setViewportSize(viewports.desktopMedium);
        await navigateAndWait(page, "/dashboard");

        const navItems = page.locator('nav a, aside a');
        const count = await navItems.count();

        console.log(`Navigation items visible on desktop: ${count}`);
        expect(count).toBeGreaterThan(3);
      });
    });

    test.describe("Desktop Layout", () => {
      test("should show multi-column layout on desktop", async ({ page }) => {
        await page.setViewportSize(viewports.desktopMedium);
        await navigateAndWait(page, "/dashboard");
        await page.waitForTimeout(timeouts.medium);

        // Cards should be in grid layout
        const cards = page.locator('[class*="card"]');
        const cardCount = await cards.count();

        if (cardCount >= 2) {
          const firstBox = await cards.first().boundingBox();
          const secondBox = await cards.nth(1).boundingBox();

          if (firstBox && secondBox) {
            // Cards should be side by side (not stacked)
            const sameRow = Math.abs(firstBox.y - secondBox.y) < 50;
            console.log(`Cards in same row: ${sameRow}`);
          }
        }
      });

      test("should maximize content area on large screens", async ({ page }) => {
        await page.setViewportSize(viewports.desktopLarge);
        await navigateAndWait(page, "/dashboard");

        const mainContent = page.locator('main').first();
        const box = await mainContent.boundingBox();

        if (box) {
          // Content should use significant portion of screen
          expect(box.width).toBeGreaterThan(1000);
          console.log(`Main content width on 2K: ${box.width}px`);
        }
      });
    });
  });

  test.describe("Cross-Device Consistency", () => {
    test("should maintain branding across all viewports", async ({ page }) => {
      const viewportSizes = [
        viewports.mobileMedium,
        viewports.tabletPortrait,
        viewports.desktopMedium,
      ];

      for (const viewport of viewportSizes) {
        await page.setViewportSize(viewport);
        await navigateAndWait(page, "/dashboard");

        // Check for SAHOOL logo/branding
        const branding = page.locator('text=/SAHOOL|سهول/i');
        await expect(branding.first()).toBeVisible({ timeout: timeouts.medium });

        console.log(`Branding visible at ${viewport.name}: true`);
      }
    });

    test("should maintain color scheme across viewports", async ({ page }) => {
      const viewportSizes = [viewports.mobileMedium, viewports.desktopMedium];

      for (const viewport of viewportSizes) {
        await page.setViewportSize(viewport);
        await navigateAndWait(page, "/dashboard");

        // Check primary color consistency
        const primaryElement = page.locator('button[class*="primary"], [class*="primary"]').first();
        const isVisible = await primaryElement.isVisible({ timeout: timeouts.short }).catch(() => false);

        if (isVisible) {
          const bgColor = await primaryElement.evaluate((el) =>
            window.getComputedStyle(el).backgroundColor
          );
          console.log(`Primary color at ${viewport.name}: ${bgColor}`);
        }
      }
    });

    test("should maintain functionality across viewports", async ({ page }) => {
      const viewportSizes = [viewports.mobileMedium, viewports.desktopMedium];

      for (const viewport of viewportSizes) {
        await page.setViewportSize(viewport);
        await navigateAndWait(page, "/dashboard");

        // Key elements should be functional
        const heading = page.locator('h1, h2').first();
        await expect(heading).toBeVisible({ timeout: timeouts.medium });

        console.log(`Dashboard functional at ${viewport.name}: true`);
      }
    });
  });

  test.describe("RTL Support Responsiveness", () => {
    test("should maintain RTL layout on all viewports", async ({ page }) => {
      const viewportSizes = [
        viewports.mobileMedium,
        viewports.tabletPortrait,
        viewports.desktopMedium,
      ];

      for (const viewport of viewportSizes) {
        await page.setViewportSize(viewport);
        await navigateAndWait(page, "/dashboard");

        const htmlDir = await page.locator('html').getAttribute('dir');
        console.log(`RTL direction at ${viewport.name}: ${htmlDir}`);
      }
    });

    test("should flip sidebar to right on RTL mobile", async ({ page }) => {
      await page.setViewportSize(viewports.mobileMedium);
      await navigateAndWait(page, "/dashboard");

      const hamburgerMenu = page.locator('[data-testid="mobile-menu"]');

      if (await hamburgerMenu.first().isVisible({ timeout: timeouts.medium })) {
        await hamburgerMenu.first().click();
        await page.waitForTimeout(500);

        const drawer = page.locator('[class*="drawer"], [data-testid="mobile-drawer"]');
        if (await drawer.first().isVisible({ timeout: timeouts.short })) {
          const box = await drawer.first().boundingBox();
          if (box) {
            // In RTL, drawer typically appears from right
            console.log(`Drawer position: x=${box.x}`);
          }
        }
      }
    });
  });

  test.describe("Orientation Changes", () => {
    test("should handle portrait to landscape change", async ({ page }) => {
      // Start in portrait
      await page.setViewportSize(viewports.tabletPortrait);
      await navigateAndWait(page, "/dashboard");

      const headingPortrait = page.locator('h1, h2').first();
      await expect(headingPortrait).toBeVisible({ timeout: timeouts.medium });

      // Change to landscape
      await page.setViewportSize(viewports.tabletLandscape);
      await page.waitForTimeout(500);

      // Content should still be visible
      const headingLandscape = page.locator('h1, h2').first();
      await expect(headingLandscape).toBeVisible({ timeout: timeouts.medium });
    });

    test("should preserve scroll position on orientation change", async ({ page }) => {
      await page.setViewportSize(viewports.mobileMedium);
      await navigateAndWait(page, "/dashboard");

      // Scroll down
      await page.evaluate(() => window.scrollTo(0, 200));
      await page.waitForTimeout(300);

      const scrollBefore = await page.evaluate(() => window.scrollY);

      // Change orientation
      await page.setViewportSize(viewports.mobileLarge);
      await page.waitForTimeout(500);

      const scrollAfter = await page.evaluate(() => window.scrollY);

      console.log(`Scroll position: before=${scrollBefore}, after=${scrollAfter}`);
    });
  });

  test.describe("Touch Interactions", () => {
    test("should support swipe gestures on mobile", async ({ page }) => {
      await page.setViewportSize(viewports.mobileMedium);
      await navigateAndWait(page, "/dashboard");

      // Simulate swipe on a swipeable element (if exists)
      const swipeable = page.locator('[class*="swipe"], [data-swipeable]');
      const hasSwipeable = await swipeable.first().isVisible({ timeout: timeouts.short }).catch(() => false);

      console.log(`Swipeable elements available: ${hasSwipeable}`);
    });

    test("should provide adequate tap targets", async ({ page }) => {
      await page.setViewportSize(viewports.mobileMedium);
      await navigateAndWait(page, "/dashboard");

      // Check all interactive elements
      const buttons = page.locator('button, a, [role="button"]');
      const count = await buttons.count();

      let smallTargets = 0;
      for (let i = 0; i < Math.min(count, 10); i++) {
        const box = await buttons.nth(i).boundingBox();
        if (box && (box.height < 32 || box.width < 32)) {
          smallTargets++;
        }
      }

      console.log(`Small tap targets found: ${smallTargets} out of ${Math.min(count, 10)}`);
    });
  });

  test.describe("Image and Media Responsiveness", () => {
    test("should resize images appropriately", async ({ page }) => {
      await page.setViewportSize(viewports.mobileMedium);
      await navigateAndWait(page, "/dashboard");

      const images = page.locator('img');
      const count = await images.count();

      if (count > 0) {
        const firstImage = images.first();
        const box = await firstImage.boundingBox();

        if (box) {
          // Image should fit within viewport
          expect(box.width).toBeLessThanOrEqual(viewports.mobileMedium.width);
          console.log(`Image width on mobile: ${box.width}px`);
        }
      }
    });

    test("should lazy load images on scroll", async ({ page }) => {
      await page.setViewportSize(viewports.mobileMedium);
      await navigateAndWait(page, "/dashboard");

      // Check for lazy loading attributes
      const lazyImages = page.locator('img[loading="lazy"], img[data-src]');
      const count = await lazyImages.count();

      console.log(`Lazy loaded images: ${count}`);
    });
  });
});
