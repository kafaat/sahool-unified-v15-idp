import { test, expect } from "@playwright/test";

/**
 * CI Smoke Tests - Run without backend API
 * اختبارات تدخين CI - تعمل بدون خادم خلفي
 *
 * These tests validate that the web app builds and renders correctly
 * in CI without requiring a running backend. They test static rendering,
 * client-side routing, and basic UI elements.
 */

test.describe("CI Smoke Tests (no backend required)", () => {
  test("login page renders with bilingual content", async ({ page }) => {
    await page.goto("/login", { waitUntil: "domcontentloaded" });

    // Verify Arabic heading
    await expect(page.locator("text=تسجيل الدخول")).toBeVisible({ timeout: 10000 });

    // Verify English heading
    await expect(page.locator("text=Login")).toBeVisible();

    // Verify form inputs exist
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();

    // Verify submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("register page renders with form fields", async ({ page }) => {
    await page.goto("/register", { waitUntil: "domcontentloaded" });

    // Verify Arabic heading
    await expect(page.locator("text=إنشاء حساب جديد")).toBeVisible({ timeout: 10000 });

    // Verify name inputs
    await expect(page.locator('input[autocomplete="given-name"]')).toBeVisible();
    await expect(page.locator('input[autocomplete="family-name"]')).toBeVisible();

    // Verify email input
    await expect(page.locator('input[type="email"]')).toBeVisible();

    // Verify password inputs (at least 2 - password + confirm)
    const passwordInputs = page.locator('input[type="password"]');
    await expect(passwordInputs).toHaveCount(2);
  });

  test("forgot-password page renders", async ({ page }) => {
    await page.goto("/forgot-password", { waitUntil: "domcontentloaded" });

    // Verify page loaded with password recovery content
    await expect(page.locator("text=/نسيت كلمة المرور|Forgot Password|استعادة/i")).toBeVisible({
      timeout: 10000,
    });
  });

  test("navigation between auth pages works", async ({ page }) => {
    // Start at login
    await page.goto("/login", { waitUntil: "domcontentloaded" });
    await expect(page.locator("text=تسجيل الدخول")).toBeVisible({ timeout: 10000 });

    // Navigate to register via link
    await page.click("text=/إنشاء حساب|Create Account/i");
    await expect(page).toHaveURL(/\/register/);
    await expect(page.locator("text=إنشاء حساب جديد")).toBeVisible({ timeout: 10000 });

    // Navigate back to login
    await page.click("text=/تسجيل الدخول.*Login|Login/i");
    await expect(page).toHaveURL(/\/login/);
  });

  test("login form validates empty submission", async ({ page }) => {
    await page.goto("/login", { waitUntil: "domcontentloaded" });
    await expect(page.locator('button[type="submit"]')).toBeVisible({ timeout: 10000 });

    // Try to submit empty form - HTML5 validation should prevent submission
    // or the form should show errors
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');

    // Verify inputs are required
    await expect(emailInput).toHaveAttribute("required", "");
    await expect(passwordInput).toHaveAttribute("required", "");
  });

  test("page has correct meta and accessibility structure", async ({ page }) => {
    await page.goto("/login", { waitUntil: "domcontentloaded" });

    // Check that form labels/inputs have proper structure
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible({ timeout: 10000 });

    // Verify autocomplete attributes for security
    await expect(emailInput).toHaveAttribute("autocomplete", "email");
    await expect(page.locator('input[type="password"]')).toHaveAttribute(
      "autocomplete",
      "current-password",
    );
  });
});
