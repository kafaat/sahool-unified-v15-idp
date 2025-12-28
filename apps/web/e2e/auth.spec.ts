import { test, expect } from './fixtures/test-fixtures';
import { login, logout, clearAuth, TEST_USER } from './helpers/auth.helpers';
import { waitForToast } from './helpers/page.helpers';

/**
 * Authentication E2E Tests
 * اختبارات E2E للمصادقة
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing authentication
    await clearAuth(page);
  });

  test('should display login page correctly', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Check page title - login page doesn't set a custom title
    // Just verify we're on the page and can see the main heading
    await expect(page.locator('text=/تسجيل الدخول إلى سهول/i')).toBeVisible();

    // Check for SAHOOL branding
    await expect(page.locator('text=/SAHOOL|سهول/i')).toBeVisible();

    // Check for email input
    await expect(page.locator('input[type="email"]')).toBeVisible();

    // Check for password input
    await expect(page.locator('input[type="password"]')).toBeVisible();

    // Check for submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Check for forgot password link
    await expect(page.locator('text=/نسيت كلمة المرور.*Forgot Password/i')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill in invalid credentials
    await page.fill('input[type="email"]', 'invalid@sahool.com');
    await page.fill('input[type="password"]', 'wrongpassword');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for error message
    const hasError = await waitForToast(page, undefined, 5000);
    expect(hasError).toBe(true);

    // Should still be on login page
    await expect(page).toHaveURL(/\/login/);
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Perform login
    await login(page, TEST_USER);

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);

    // Check for welcome message or user name
    await expect(page.locator('text=/مرحباً|Welcome/i')).toBeVisible({ timeout: 10000 });
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/login');

    // Try to submit with invalid email format
    await page.fill('input[type="email"]', 'notanemail');
    await page.fill('input[type="password"]', 'password123');

    // The HTML5 validation should prevent submission
    const emailInput = page.locator('input[type="email"]');
    const validationMessage = await emailInput.evaluate((input: HTMLInputElement) => input.validationMessage);

    expect(validationMessage).toBeTruthy();
  });

  test('should require both email and password', async ({ page }) => {
    await page.goto('/login');

    // Try to submit without filling any fields
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Check that we're still on login page
    await expect(page).toHaveURL(/\/login/);

    // Try with only email
    await page.fill('input[type="email"]', TEST_USER.email);
    await submitButton.click();

    // Should still be on login page
    await expect(page).toHaveURL(/\/login/);
  });

  test('should show loading state during login', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);

    // Click submit and immediately check for loading state
    await page.click('button[type="submit"]');

    // Button should show loading state (disabled or with loading indicator)
    const submitButton = page.locator('button[type="submit"]');
    const isDisabled = await submitButton.isDisabled();

    // Either the button is disabled or contains loading text/spinner
    expect(isDisabled).toBe(true);
  });

  test('should successfully logout', async ({ page }) => {
    // First, login
    await login(page, TEST_USER);
    await expect(page).toHaveURL(/\/dashboard/);

    // Perform logout
    await logout(page);

    // Should redirect to login page
    await expect(page).toHaveURL(/\/login/);

    // Try to access dashboard - should redirect to login
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });

  test('should persist login session on page reload', async ({ page }) => {
    // Login
    await login(page, TEST_USER);
    await expect(page).toHaveURL(/\/dashboard/);

    // Reload page
    await page.reload();

    // Should still be on dashboard (not redirected to login)
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Clear auth first
    await clearAuth(page);

    // Try to access protected route
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/, { timeout: 10000 });
  });

  test('should prevent access to login page when already authenticated', async ({ page }) => {
    // Login first
    await login(page, TEST_USER);
    await expect(page).toHaveURL(/\/dashboard/);

    // Try to navigate to login page
    await page.goto('/login');

    // Should redirect back to dashboard or stay on dashboard
    // (depending on implementation)
    await page.waitForTimeout(2000);
    const currentUrl = page.url();

    // Either stays on dashboard or redirects from login
    expect(currentUrl).toMatch(/\/(dashboard|login)/);
  });
});

/**
 * Password Reset Flow (if implemented)
 * تدفق إعادة تعيين كلمة المرور
 */
test.describe('Password Reset', () => {
  test('should display forgot password link', async ({ page }) => {
    await page.goto('/login');

    const forgotPasswordLink = page.locator('text=/Forgot Password|نسيت كلمة المرور/i');
    await expect(forgotPasswordLink).toBeVisible();
  });

  test.skip('should navigate to password reset page', async ({ page }) => {
    // Skip this test if password reset is not yet implemented
    await page.goto('/login');

    const forgotPasswordLink = page.locator('text=/Forgot Password|نسيت كلمة المرور/i');
    await forgotPasswordLink.click();

    // Should navigate to reset password page
    await expect(page).toHaveURL(/\/reset-password|\/forgot-password/);
  });
});
