import { test, expect } from "@playwright/test";

/**
 * CI Smoke Tests - Run without backend API
 * اختبارات تدخين CI - تعمل بدون خادم خلفي
 *
 * These tests validate that the web app builds and renders correctly
 * in CI without requiring a running backend. They test static rendering,
 * client-side routing, and basic UI elements.
 *
 * Tests use .first() on text locators to avoid strict-mode failures
 * when multiple elements match (e.g. heading + button both contain
 * "تسجيل الدخول").
 */

test.describe("CI Smoke Tests (no backend required)", () => {
  test("login page renders with bilingual content", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle" });

    // Verify Arabic content is present
    await expect(page.getByText("تسجيل الدخول").first()).toBeVisible({
      timeout: 15000,
    });

    // Verify English content is present
    await expect(page.getByText("Login").first()).toBeVisible();

    // Default login method is phone — verify phone input is visible
    await expect(page.locator('input[type="tel"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();

    // Switch to email login and verify email input renders
    await page.getByText("البريد الإلكتروني").click();
    await expect(page.locator('input[type="email"]')).toBeVisible();

    // Verify submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("register page renders with form fields", async ({ page }) => {
    await page.goto("/register", { waitUntil: "networkidle" });

    // Verify Arabic heading
    await expect(page.getByText("إنشاء حساب جديد").first()).toBeVisible({
      timeout: 15000,
    });

    // Verify name inputs
    await expect(page.locator('input[autocomplete="given-name"]')).toBeVisible();
    await expect(page.locator('input[autocomplete="family-name"]')).toBeVisible();

    // Verify email input
    await expect(page.locator('input[type="email"]')).toBeVisible();

    // Verify password inputs (at least 2 - password + confirm)
    const passwordInputs = page.locator('input[type="password"]');
    await expect(passwordInputs.first()).toBeVisible();
    expect(await passwordInputs.count()).toBeGreaterThanOrEqual(2);
  });

  test("forgot-password page renders", async ({ page }) => {
    await page.goto("/forgot-password", { waitUntil: "networkidle" });

    // Verify page loaded with password recovery content
    // Match any of the bilingual heading variants
    const heading = page.getByText(/نسيت كلمة المرور|Forgot Password|استعادة/i).first();
    await expect(heading).toBeVisible({ timeout: 15000 });
  });

  test("navigation between auth pages works", async ({ page }) => {
    // Start at login
    await page.goto("/login", { waitUntil: "networkidle" });
    await expect(page.getByText("تسجيل الدخول").first()).toBeVisible({
      timeout: 15000,
    });

    // Navigate to register via link
    const createAccountLink = page.getByRole("link", {
      name: /إنشاء حساب|Create Account/i,
    });
    await createAccountLink.click();
    await expect(page).toHaveURL(/\/register/, { timeout: 15000 });
    await expect(page.getByText("إنشاء حساب جديد").first()).toBeVisible({
      timeout: 15000,
    });

    // Navigate back to login
    const loginLink = page.getByRole("link", {
      name: /تسجيل الدخول|Login/i,
    });
    await loginLink.click();
    await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
  });

  test("login form has required fields", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle" });
    await expect(page.locator('button[type="submit"]')).toBeVisible({
      timeout: 15000,
    });

    // Default is phone — verify phone input is required
    const phoneInput = page.locator('input[type="tel"]');
    const passwordInput = page.locator('input[type="password"]');

    await expect(phoneInput).toHaveAttribute("required", "");
    await expect(passwordInput).toHaveAttribute("required", "");

    // Switch to email and verify email input is also required
    await page.getByText("البريد الإلكتروني").click();
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toHaveAttribute("required", "");
  });

  test("page has correct accessibility structure", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle" });

    // Default is phone — verify phone autocomplete
    const phoneInput = page.locator('input[type="tel"]');
    await expect(phoneInput).toBeVisible({ timeout: 15000 });
    await expect(phoneInput).toHaveAttribute("autocomplete", "tel");
    await expect(page.locator('input[type="password"]')).toHaveAttribute(
      "autocomplete",
      "current-password",
    );

    // Switch to email and verify email autocomplete
    await page.getByText("البريد الإلكتروني").click();
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible();
    await expect(emailInput).toHaveAttribute("autocomplete", "email");
  });
});
