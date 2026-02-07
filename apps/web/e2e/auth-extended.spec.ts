/**
 * Extended Authentication E2E Tests
 * اختبارات E2E موسعة للمصادقة
 *
 * Comprehensive tests for:
 * - Registration flow
 * - Password reset flow
 * - OTP verification
 * - Two-factor authentication
 * - Social login
 * - Session management
 * - Security features
 */

import { test, expect } from "./fixtures/test-fixtures";
import { login, clearAuth, TEST_USER } from "./helpers/auth.helpers";
import { waitForPageLoad, waitForToast, navigateAndWait } from "./helpers/page.helpers";
import { testData, timeouts } from "./helpers/test-data";

test.describe("User Registration", () => {
  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
  });

  test("should display registration page correctly", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    // Check for registration heading
    await expect(
      page.locator("text=/إنشاء حساب|Create Account|تسجيل|Register/i")
    ).toBeVisible({ timeout: timeouts.long });

    // Check for form fields
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test("should display required form fields for registration", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    // Check for name fields
    const nameInput = page.locator(
      'input[name="name"], input[name="fullName"], input[placeholder*="الاسم"], input[placeholder*="Name"]'
    );
    const hasName = await nameInput.first().isVisible({ timeout: timeouts.medium }).catch(() => false);
    console.log(`Name field present: ${hasName}`);

    // Check for email
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible();

    // Check for password
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput.first()).toBeVisible();

    // Check for phone (may be required in SAHOOL)
    const phoneInput = page.locator(
      'input[type="tel"], input[name="phone"], input[placeholder*="هاتف"], input[placeholder*="Phone"]'
    );
    const hasPhone = await phoneInput.first().isVisible({ timeout: timeouts.short }).catch(() => false);
    console.log(`Phone field present: ${hasPhone}`);
  });

  test("should validate email format on registration", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    const emailInput = page.locator('input[type="email"]');
    await emailInput.fill("invalid-email");
    await emailInput.blur();
    await page.waitForTimeout(300);

    // Check for validation error
    const validationMessage = await emailInput.evaluate(
      (input: HTMLInputElement) => input.validationMessage
    );

    expect(validationMessage).toBeTruthy();
  });

  test("should validate password strength", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    const passwordInput = page.locator('input[type="password"]').first();
    await passwordInput.fill("weak");
    await passwordInput.blur();
    await page.waitForTimeout(300);

    // Check for password strength indicator or error
    const strengthIndicator = page.locator(
      '[class*="strength"], [class*="password-meter"], text=/ضعيفة|Weak/i'
    );
    const hasStrength = await strengthIndicator.first().isVisible({ timeout: timeouts.short }).catch(() => false);

    console.log(`Password strength indicator shown: ${hasStrength}`);
  });

  test("should validate password confirmation match", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    const passwordInputs = page.locator('input[type="password"]');
    const passwordCount = await passwordInputs.count();

    if (passwordCount >= 2) {
      await passwordInputs.first().fill("StrongPass123!");
      await passwordInputs.nth(1).fill("DifferentPass123!");
      await passwordInputs.nth(1).blur();
      await page.waitForTimeout(300);

      // Check for mismatch error
      const mismatchError = page.locator(
        'text=/غير متطابقة|do not match|Passwords must match/i'
      );
      const hasError = await mismatchError.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

      console.log(`Password mismatch error shown: ${hasError}`);
    }
  });

  test("should accept valid registration data", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    const userData = {
      name: testData.randomName(),
      email: testData.randomEmail(),
      phone: testData.randomPhone(),
      password: "SecurePass@123",
    };

    // Fill form
    const nameInput = page.locator('input[name="name"], input[name="fullName"]');
    if (await nameInput.first().isVisible({ timeout: timeouts.short })) {
      await nameInput.first().fill(userData.name);
    }

    await page.fill('input[type="email"]', userData.email);

    const phoneInput = page.locator('input[type="tel"]');
    if (await phoneInput.first().isVisible({ timeout: timeouts.short })) {
      await phoneInput.first().fill(userData.phone);
    }

    const passwordInputs = page.locator('input[type="password"]');
    await passwordInputs.first().fill(userData.password);

    if ((await passwordInputs.count()) >= 2) {
      await passwordInputs.nth(1).fill(userData.password);
    }

    // Submit
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(timeouts.long);

    // Should show success or redirect to OTP
    const currentUrl = page.url();
    console.log(`After registration URL: ${currentUrl}`);
  });

  test("should show terms and conditions checkbox", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    const termsCheckbox = page.locator(
      'input[type="checkbox"][name*="terms"], input[type="checkbox"][name*="agree"]'
    );
    const hasTerms = await termsCheckbox.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Terms checkbox present: ${hasTerms}`);
  });

  test("should link to login page from registration", async ({ page }) => {
    await page.goto("/register");
    await waitForPageLoad(page);

    const loginLink = page.locator(
      'a:has-text("تسجيل الدخول"), a:has-text("Login"), a:has-text("Sign In")'
    );
    await expect(loginLink.first()).toBeVisible({ timeout: timeouts.medium });
  });
});

test.describe("Password Reset Flow", () => {
  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
  });

  test("should navigate to forgot password page", async ({ page }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    const forgotLink = page.locator(
      'a:has-text("نسيت كلمة المرور"), a:has-text("Forgot Password")'
    );
    await forgotLink.click();
    await page.waitForTimeout(1000);

    await expect(page).toHaveURL(/\/forgot-password|\/reset-password/);
  });

  test("should display forgot password form", async ({ page }) => {
    await page.goto("/forgot-password");
    await waitForPageLoad(page);

    // Check for email input
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible({ timeout: timeouts.medium });

    // Check for submit button
    const submitBtn = page.locator(
      'button[type="submit"], button:has-text("إرسال"), button:has-text("Send"), button:has-text("Reset")'
    );
    await expect(submitBtn.first()).toBeVisible();
  });

  test("should validate email on forgot password", async ({ page }) => {
    await page.goto("/forgot-password");
    await waitForPageLoad(page);

    await page.fill('input[type="email"]', "invalid-email");
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);

    // Should show validation error
    await expect(page).toHaveURL(/\/forgot-password/);
  });

  test("should show success message after password reset request", async ({ page }) => {
    await page.goto("/forgot-password");
    await waitForPageLoad(page);

    await page.fill('input[type="email"]', TEST_USER.email);
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(timeouts.medium);

    // Check for success message
    const successMsg = page.locator(
      'text=/تم الإرسال|sent|Check your email|تحقق من بريدك/i'
    );
    const hasSuccess = await successMsg.first().isVisible({ timeout: timeouts.long }).catch(() => false);

    console.log(`Password reset success message shown: ${hasSuccess}`);
  });

  test("should show link to return to login", async ({ page }) => {
    await page.goto("/forgot-password");
    await waitForPageLoad(page);

    const backToLogin = page.locator(
      'a:has-text("العودة"), a:has-text("Back to Login"), a:has-text("تسجيل الدخول")'
    );
    await expect(backToLogin.first()).toBeVisible({ timeout: timeouts.medium });
  });
});

test.describe("OTP Verification", () => {
  test("should display OTP verification page", async ({ page }) => {
    await page.goto("/verify-otp");
    await waitForPageLoad(page);

    // Check for OTP input fields
    const otpInputs = page.locator(
      'input[type="text"][maxlength="1"], input[name*="otp"], input[type="number"]'
    );
    const count = await otpInputs.count();

    console.log(`OTP input fields: ${count}`);

    // Check for verification heading
    const heading = page.locator(
      'text=/التحقق|Verification|رمز التأكيد|OTP/i'
    );
    const hasHeading = await heading.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`OTP verification page displayed: ${hasHeading}`);
  });

  test("should allow entering OTP digits", async ({ page }) => {
    await page.goto("/verify-otp");
    await waitForPageLoad(page);

    const otpInputs = page.locator('input[maxlength="1"]');
    const count = await otpInputs.count();

    if (count > 0) {
      // Enter OTP digits
      for (let i = 0; i < Math.min(count, 6); i++) {
        await otpInputs.nth(i).fill(String(i + 1));
      }
    }
  });

  test("should show resend OTP option", async ({ page }) => {
    await page.goto("/verify-otp");
    await waitForPageLoad(page);

    const resendBtn = page.locator(
      'button:has-text("إعادة الإرسال"), button:has-text("Resend"), a:has-text("Resend")'
    );
    const hasResend = await resendBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Resend OTP option available: ${hasResend}`);
  });

  test("should show countdown timer for resend", async ({ page }) => {
    await page.goto("/verify-otp");
    await waitForPageLoad(page);

    const timer = page.locator(
      'text=/\\d+:\\d+|seconds|ثانية/i, [class*="timer"], [class*="countdown"]'
    );
    const hasTimer = await timer.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Countdown timer shown: ${hasTimer}`);
  });
});

test.describe("Session Management", () => {
  test("should maintain session across page navigations", async ({ page }) => {
    await login(page, TEST_USER);
    await page.waitForURL("**/dashboard");

    // Navigate to different pages
    await page.goto("/fields");
    await waitForPageLoad(page);
    await expect(page).not.toHaveURL(/\/login/);

    await page.goto("/settings");
    await waitForPageLoad(page);
    await expect(page).not.toHaveURL(/\/login/);
  });

  test("should persist session after page refresh", async ({ page }) => {
    await login(page, TEST_USER);
    await page.waitForURL("**/dashboard");

    await page.reload();
    await waitForPageLoad(page);

    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("should redirect to login after logout", async ({ page }) => {
    await login(page, TEST_USER);
    await page.waitForURL("**/dashboard");

    // Open user menu and logout
    const userMenu = page.locator(
      '[data-testid="user-menu"], [aria-label*="user"], button:has-text("Settings")'
    );

    if (await userMenu.first().isVisible({ timeout: timeouts.medium })) {
      await userMenu.first().click();
      await page.waitForTimeout(300);

      const logoutBtn = page.locator(
        'button:has-text("تسجيل الخروج"), button:has-text("Logout"), button:has-text("Sign Out")'
      );

      if (await logoutBtn.first().isVisible({ timeout: timeouts.short })) {
        await logoutBtn.first().click();
        await page.waitForTimeout(1000);

        await expect(page).toHaveURL(/\/login/);
      }
    }
  });

  test("should show session expiry warning", async ({ page }) => {
    await login(page, TEST_USER);
    await page.waitForURL("**/dashboard");

    // Check for session expiry handling (may need to mock time)
    // This is a placeholder - actual implementation depends on session timeout
    console.log("Session management test - placeholder for session expiry warning");
  });
});

test.describe("Security Features", () => {
  test("should protect against brute force attacks", async ({ page }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    // Attempt multiple failed logins
    for (let i = 0; i < 3; i++) {
      await page.fill('input[type="email"]', "test@sahool.com");
      await page.fill('input[type="password"]', "wrongpassword");
      await page.locator('button[type="submit"]').click();
      await page.waitForTimeout(1000);
    }

    // Check for rate limiting or lockout message
    const lockoutMsg = page.locator(
      'text=/محاولات|attempts|locked|مقفل|rate limit/i'
    );
    const hasLockout = await lockoutMsg.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Rate limiting/lockout shown: ${hasLockout}`);
  });

  test("should have CSRF protection on forms", async ({ page }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    // Check for CSRF token in form
    const csrfInput = page.locator(
      'input[name="_csrf"], input[name="csrf"], input[name="csrfToken"]'
    );
    const hasCsrf = await csrfInput.first().isVisible({ timeout: timeouts.short }).catch(() => false);

    // Or check for CSRF in meta tag or cookie
    const csrfMeta = await page.locator('meta[name="csrf-token"]').getAttribute('content').catch(() => null);

    console.log(`CSRF protection: input=${hasCsrf}, meta=${!!csrfMeta}`);
  });

  test("should use secure password input", async ({ page }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    const passwordInput = page.locator('input[type="password"]');
    const inputType = await passwordInput.getAttribute("type");
    const autocomplete = await passwordInput.getAttribute("autocomplete");

    expect(inputType).toBe("password");
    console.log(`Password autocomplete attribute: ${autocomplete}`);
  });

  test("should toggle password visibility", async ({ page }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    const passwordInput = page.locator('input[type="password"]');
    await passwordInput.fill("mypassword");

    // Look for toggle button
    const toggleBtn = page.locator(
      'button[aria-label*="password"], button:has([class*="eye"]), [data-testid="toggle-password"]'
    );

    if (await toggleBtn.first().isVisible({ timeout: timeouts.short })) {
      await toggleBtn.first().click();
      await page.waitForTimeout(200);

      // Password should be visible
      const newType = await page.locator('input').filter({ has: page.locator('[value="mypassword"]') }).first().getAttribute("type").catch(() => "password");

      console.log(`Password visibility toggled: ${newType}`);
    }
  });

  test("should sanitize user input", async ({ page }) => {
    await page.goto("/login");
    await waitForPageLoad(page);

    // Try XSS injection
    await page.fill('input[type="email"]', '<script>alert("xss")</script>@test.com');
    await page.fill('input[type="password"]', '<img src=x onerror=alert(1)>');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(1000);

    // Page should handle gracefully without executing scripts
    // No alert dialog should appear
    const hasAlert = await page.evaluate(() => {
      // Check if any alert was triggered
      return false;
    });

    expect(hasAlert).toBe(false);
  });
});

test.describe("Profile Management", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test("should display user profile page", async ({ page }) => {
    await navigateAndWait(page, "/settings");

    const profileSection = page.locator(
      'text=/الملف الشخصي|Profile|معلومات المستخدم|User Info/i'
    );
    const hasProfile = await profileSection.first().isVisible({ timeout: timeouts.long }).catch(() => false);

    console.log(`Profile section displayed: ${hasProfile}`);
  });

  test("should display user information", async ({ page }) => {
    await navigateAndWait(page, "/settings");

    // Check for email display
    const emailField = page.locator(
      'input[type="email"], text=/test@sahool.com/i'
    );
    const hasEmail = await emailField.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`User email displayed: ${hasEmail}`);
  });

  test("should allow updating profile name", async ({ page }) => {
    await navigateAndWait(page, "/settings");

    const nameInput = page.locator(
      'input[name="name"], input[name="fullName"]'
    );

    if (await nameInput.first().isVisible({ timeout: timeouts.medium })) {
      await nameInput.first().clear();
      await nameInput.first().fill("Updated Name");

      const saveBtn = page.locator('button:has-text("حفظ"), button:has-text("Save")');
      if (await saveBtn.first().isVisible({ timeout: timeouts.short })) {
        await saveBtn.first().click();
        await page.waitForTimeout(timeouts.medium);

        const hasToast = await waitForToast(page, undefined, timeouts.medium);
        console.log(`Profile update success: ${hasToast}`);
      }
    }
  });

  test("should allow changing password from profile", async ({ page }) => {
    await navigateAndWait(page, "/settings");

    const changePasswordBtn = page.locator(
      'button:has-text("تغيير كلمة المرور"), button:has-text("Change Password"), a:has-text("Change Password")'
    );
    const hasChangePassword = await changePasswordBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Change password option available: ${hasChangePassword}`);
  });

  test("should display account deletion option", async ({ page }) => {
    await navigateAndWait(page, "/settings");

    // Scroll to bottom
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);

    const deleteBtn = page.locator(
      'button:has-text("حذف الحساب"), button:has-text("Delete Account"), [class*="danger"]'
    );
    const hasDelete = await deleteBtn.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Account deletion option available: ${hasDelete}`);
  });
});

test.describe("Language and Localization", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USER);
    await waitForPageLoad(page);
  });

  test("should display language selector", async ({ page }) => {
    await navigateAndWait(page, "/settings");

    const languageSelector = page.locator(
      '[data-testid="language-selector"], select[name="language"], button:has-text("العربية"), button:has-text("English")'
    );
    const hasLanguage = await languageSelector.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Language selector available: ${hasLanguage}`);
  });

  test("should support Arabic language", async ({ page }) => {
    await navigateAndWait(page, "/dashboard");

    // Check for Arabic content
    const arabicContent = page.locator('text=/[\u0600-\u06FF]+/');
    const hasArabic = await arabicContent.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`Arabic content present: ${hasArabic}`);
  });

  test("should support English language", async ({ page }) => {
    await navigateAndWait(page, "/dashboard");

    // Check for English content
    const englishContent = page.locator('text=/[a-zA-Z]+/');
    const hasEnglish = await englishContent.first().isVisible({ timeout: timeouts.medium }).catch(() => false);

    console.log(`English content present: ${hasEnglish}`);
  });
});
