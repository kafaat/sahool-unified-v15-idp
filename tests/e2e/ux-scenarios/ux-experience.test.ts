/**
 * SAHOOL Platform — UX Experience Validation Tests
 * اختبارات التحقق من تجربة المستخدم لمنصة سهول
 *
 * Filesystem-based Vitest tests that read actual source files and validate
 * UX patterns, bilingual content, accessibility, security, and navigation.
 *
 * These tests do NOT launch a browser; they analyse the source code on disk
 * to enforce UX conventions across the platform.
 */

import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// ─── Path Constants ──────────────────────────────────────────────────────────
const ROOT = path.resolve(__dirname, '../../..');
const WEB_APP = path.join(ROOT, 'apps/web/src');
const ADMIN_APP = path.join(ROOT, 'apps/admin/src');

// ─── Helper: safe file reader ────────────────────────────────────────────────
function readFile(filePath: string): string {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`File not found: ${resolved}`);
  }
  return fs.readFileSync(resolved, 'utf-8');
}

/** Returns true when the file exists */
function fileExists(filePath: string): boolean {
  return fs.existsSync(path.resolve(filePath));
}

/** Arabic Unicode range regex */
const ARABIC_RE = /[\u0600-\u06FF]/;

// =============================================================================
// 1. WEB APP AUTH UX — تجربة المصادقة لتطبيق الويب
// =============================================================================

describe('1. Web App Auth UX | تجربة المصادقة لتطبيق الويب', () => {
  // ─── 1.1 Login Page ─────────────────────────────────────────────────────
  describe('1.1 Login Page | صفحة تسجيل الدخول', () => {
    const LOGIN_CLIENT = path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx');
    const LOGIN_PAGE = path.join(WEB_APP, 'app/(auth)/login/page.tsx');

    it('should have LoginClient.tsx file', () => {
      expect(fileExists(LOGIN_CLIENT)).toBe(true);
    });

    it('should have login page.tsx server component', () => {
      expect(fileExists(LOGIN_PAGE)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should contain Arabic text (bilingual content)', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(ARABIC_RE);
    });

    it('should contain "تسجيل الدخول" (Login in Arabic)', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('تسجيل الدخول');
    });

    it('should contain SAHOOL branding in Arabic "سهول"', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('سهول');
    });

    it('should contain English login text', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/Login to SAHOOL/i);
    });

    it('should support email login method', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain("'email'");
      expect(content).toMatch(/type="email"/);
    });

    it('should support phone login method', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain("'phone'");
      expect(content).toMatch(/type="tel"/);
    });

    it('should have LoginMethod type with email and phone', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/type LoginMethod\s*=\s*['"]email['"]\s*\|\s*['"]phone['"]/);
    });

    it('should have a password input field', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/type="password"/);
    });

    it('should have form submit handler', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/handleSubmit/);
      expect(content).toMatch(/onSubmit/);
    });

    it('should have OTP login support', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/handleOtpLogin/);
      expect(content).toContain('send-otp');
    });

    it('should show bilingual OTP button text', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('الدخول برمز SMS');
      expect(content).toMatch(/Login with SMS code/);
    });

    it('should implement isSafeReturnTo for open redirect prevention', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/function isSafeReturnTo/);
    });

    it('should block redirect to auth pages (loop prevention)', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('/login');
      expect(content).toContain('/register');
      expect(content).toContain('/forgot-password');
      expect(content).toContain('/reset-password');
      expect(content).toContain('/verify-otp');
    });

    it('should block protocol-relative URLs (//) in redirects', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/startsWith\(['"]\/\/['"]\)/);
    });

    it('should block backslash URL tricks (/\\) in redirects', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('/\\\\');
    });

    it('should default redirect to /dashboard', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain("'/dashboard'");
    });

    it('should use getErrorMessage utility for error handling', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/function getErrorMessage/);
    });

    it('should handle axios-style error responses', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/response\?\.data\?\.message/);
    });

    it('should show bilingual error toast on login failure', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('فشل تسجيل الدخول');
    });

    it('should show bilingual success toast on login', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('تم تسجيل الدخول بنجاح');
      expect(content).toContain('Login successful');
    });

    it('should have bilingual phone label', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('رقم الهاتف');
    });

    it('should have bilingual email label', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('البريد الإلكتروني');
    });

    it('should have bilingual password label', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('كلمة المرور');
    });

    it('should have a forgot password link', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('نسيت كلمة المرور');
      expect(content).toContain('Forgot Password');
    });

    it('should have a create account / register link', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('إنشاء حساب جديد');
      expect(content).toContain('Create Account');
    });

    it('should use Next.js Link for internal navigation', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/import Link from ['"]next\/link['"]/);
    });

    it('should have loading state management', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/isLoading/);
      expect(content).toMatch(/setIsLoading/);
    });

    it('should use autoComplete attributes for inputs', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('autoComplete="email"');
      expect(content).toContain('autoComplete="tel"');
      expect(content).toContain('autoComplete="current-password"');
    });

    it('should have ARIA attributes for login method toggle', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('role="radiogroup"');
      expect(content).toContain('role="radio"');
      expect(content).toContain('aria-checked');
    });

    it('should have bilingual ARIA labels', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/aria-label=".*[\u0600-\u06FF].*"/);
    });

    it('should use lucide-react icons', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/from ['"]lucide-react['"]/);
      expect(content).toContain('Mail');
      expect(content).toContain('Lock');
      expect(content).toContain('Phone');
    });

    it('should have aria-hidden on decorative icons', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('aria-hidden="true"');
    });

    it('should have SAHOOL green brand gradient background', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/sahool-green/);
    });

    it('should use useAuth store for login', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/useAuth/);
      expect(content).toMatch(/login/);
    });

    it('should use useToast for notifications', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toMatch(/useToast/);
      expect(content).toMatch(/showToast/);
    });

    it('should have bilingual platform description', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('منصة الإدارة الزراعية المتكاملة');
      expect(content).toContain('Integrated Agricultural Management Platform');
    });

    it('should have phone number placeholder with Yemen format', () => {
      const content = readFile(LOGIN_CLIENT);
      expect(content).toContain('+967');
    });

    it('login page.tsx should have SEO metadata', () => {
      const content = readFile(LOGIN_PAGE);
      expect(content).toMatch(/Metadata/);
    });
  });

  // ─── 1.2 Register Page ──────────────────────────────────────────────────
  describe('1.2 Register Page | صفحة التسجيل', () => {
    const REGISTER_CLIENT = path.join(WEB_APP, 'app/(auth)/register/RegisterClient.tsx');
    const REGISTER_PAGE = path.join(WEB_APP, 'app/(auth)/register/page.tsx');

    it('should have RegisterClient.tsx file', () => {
      expect(fileExists(REGISTER_CLIENT)).toBe(true);
    });

    it('should have register page.tsx', () => {
      expect(fileExists(REGISTER_PAGE)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should contain Arabic text', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(ARABIC_RE);
    });

    it('should have bilingual registration title', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('إنشاء حساب جديد');
      expect(content).toContain('Create New Account');
    });

    it('should have firstName form field', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('firstName');
    });

    it('should have lastName form field', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('lastName');
    });

    it('should have email form field', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/type="email"/);
    });

    it('should have phone form field with tel type', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/type="tel"/);
    });

    it('should have password field', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/type="password"/);
    });

    it('should have confirmPassword field', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('confirmPassword');
    });

    it('should have Yemen phone regex validation', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/YEMEN_PHONE_REGEX/);
    });

    it('should have Yemen country code +967', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain("'+967'");
    });

    it('should detect Yemen mobile operators', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('Yemen Mobile');
      expect(content).toContain('SabaFone');
      expect(content).toContain('YOU');
      expect(content).toContain('Y Telecom');
    });

    it('should have bilingual operator names', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('يمن موبايل');
      expect(content).toContain('سبأفون');
      expect(content).toContain('يو');
      expect(content).toContain('واي');
    });

    it('should validate email format', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/[^\s@]+@[^\s@]+\.[^\s@]+/);
    });

    it('should validate password minimum length of 8', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/password\.length\s*<\s*8/);
    });

    it('should validate password strength (uppercase, lowercase, number)', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/\[a-z\].*\[A-Z\].*\\d/);
    });

    it('should check passwords match', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('Passwords do not match');
    });

    it('should have bilingual password requirements helper text', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('At least 8 characters');
      expect(content).toMatch(/أحرف على الأقل/);
    });

    it('should have bilingual first name label', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('First Name');
      expect(content).toContain('الاسم الأول');
    });

    it('should have bilingual last name label', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('Last Name');
      expect(content).toContain('اسم العائلة');
    });

    it('should have email/phone registration method toggle', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/RegisterMethod/);
      expect(content).toContain("'email'");
      expect(content).toContain("'phone'");
    });

    it('should have link to login page', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('href="/login"');
      expect(content).toContain('تسجيل الدخول');
    });

    it('should have "Already have an account?" text in both languages', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('لديك حساب بالفعل');
      expect(content).toContain('Already have an account?');
    });

    it('should use autoComplete for form fields', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('autoComplete="given-name"');
      expect(content).toContain('autoComplete="family-name"');
      expect(content).toContain('autoComplete="new-password"');
    });

    it('should have form validation with error display', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/function validateForm/);
      expect(content).toMatch(/errors/);
    });

    it('should use SAHOOL green brand colors', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/sahool-green/);
    });

    it('register page.tsx should have bilingual SEO metadata', () => {
      const content = readFile(REGISTER_PAGE);
      expect(content).toMatch(/Metadata/);
      expect(content).toMatch(ARABIC_RE);
    });

    it('register page.tsx should have Open Graph metadata', () => {
      const content = readFile(REGISTER_PAGE);
      expect(content).toContain('openGraph');
    });

    it('should submit via authApiClient.register', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toMatch(/authApiClient\.register/);
    });

    it('should have bilingual success toast after registration', () => {
      const content = readFile(REGISTER_CLIENT);
      expect(content).toContain('تم إنشاء الحساب بنجاح');
      expect(content).toContain('Account created successfully');
    });
  });

  // ─── 1.3 Verify OTP Page ───────────────────────────────────────────────
  describe('1.3 Verify OTP Page | صفحة التحقق من الرمز', () => {
    const VERIFY_OTP = path.join(WEB_APP, 'app/(auth)/verify-otp/VerifyOTPClient.tsx');

    it('should have VerifyOTPClient.tsx file', () => {
      expect(fileExists(VERIFY_OTP)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should have 6-digit OTP length', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/OTP_LENGTH\s*=\s*6/);
    });

    it('should have 5-minute expiration (300 seconds)', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/OTP_EXPIRATION_SECONDS\s*=\s*300/);
    });

    it('should have 60-second resend cooldown', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/RESEND_COOLDOWN_SECONDS\s*=\s*60/);
    });

    it('should support password_reset purpose', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain("'password_reset'");
    });

    it('should support verify_phone purpose', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain("'verify_phone'");
    });

    it('should support login purpose', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain("'login'");
    });

    it('should support SMS channel', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain("'sms'");
    });

    it('should support WhatsApp channel', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain("'whatsapp'");
    });

    it('should support Telegram channel', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain("'telegram'");
    });

    it('should have bilingual channel labels', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('رسالة نصية');
      expect(content).toContain('واتساب');
      expect(content).toContain('تيليجرام');
    });

    it('should have bilingual purpose labels', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('إعادة تعيين كلمة المرور');
      expect(content).toContain('التحقق من رقم الهاتف');
    });

    it('should have auto-submit on OTP completion', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/otp\.length\s*===\s*OTP_LENGTH/);
    });

    it('should support OTP paste functionality', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/handlePaste/);
      expect(content).toContain('clipboardData');
    });

    it('should only accept digits in OTP input', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('inputMode="numeric"');
      expect(content).toMatch(/replace\(\/\\D\/g/);
    });

    it('should have bilingual verify button', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('تحقق من الرمز');
      expect(content).toContain('Verify Code');
    });

    it('should have bilingual resend text', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('لم تستلم الرمز');
      expect(content).toMatch(/Didn.*receive the code/);
    });

    it('should have resend code button', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('إعادة إرسال الرمز');
      expect(content).toContain('Resend Code');
    });

    it('should show bilingual expiration message', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('انتهت صلاحية الرمز');
      expect(content).toContain('Code expired');
    });

    it('should clear OTP when timer expires', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/expirationTime\s*===\s*0/);
      expect(content).toMatch(/setOtp\(['"]'?['"]\)/);
    });

    it('should have back to login link', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('href="/login"');
      expect(content).toContain('العودة لتسجيل الدخول');
      expect(content).toContain('Back to Login');
    });

    it('should show bilingual success message', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('تم التحقق بنجاح');
      expect(content).toContain('Verification Successful');
    });

    it('should have ARIA labels for OTP digit inputs', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toMatch(/aria-label={`Digit \$\{index \+ 1\}`}/);
    });

    it('should use Suspense boundary', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('Suspense');
    });

    it('should have LTR direction for OTP input', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('dir="ltr"');
    });

    it('should redirect to reset-password after password_reset purpose', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain('/reset-password?token=');
    });

    it('should redirect to dashboard after login/verify purpose', () => {
      const content = readFile(VERIFY_OTP);
      expect(content).toContain("router.push('/dashboard')");
    });
  });

  // ─── 1.4 Forgot Password Page ──────────────────────────────────────────
  describe('1.4 Forgot Password Page | صفحة نسيت كلمة المرور', () => {
    const FORGOT_PW = path.join(WEB_APP, 'app/(auth)/forgot-password/ForgotPasswordClient.tsx');

    it('should have ForgotPasswordClient.tsx file', () => {
      expect(fileExists(FORGOT_PW)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should support email recovery channel', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain("id: 'email'");
    });

    it('should support SMS recovery channel', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain("id: 'sms'");
    });

    it('should support WhatsApp recovery channel', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain("id: 'whatsapp'");
    });

    it('should support Telegram recovery channel', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain("id: 'telegram'");
    });

    it('should have bilingual channel labels', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('البريد الإلكتروني');
      expect(content).toContain('رسالة نصية');
      expect(content).toContain('واتساب');
      expect(content).toContain('تيليجرام');
    });

    it('should have bilingual title', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('نسيت كلمة المرور؟');
      expect(content).toContain('Forgot Password?');
    });

    it('should have bilingual recovery method label', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('طريقة الاسترداد');
      expect(content).toContain('Recovery Method');
    });

    it('should have email input for email channel', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toMatch(/type="email"/);
    });

    it('should have phone input for non-email channels', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toMatch(/type="tel"/);
    });

    it('should have bilingual submit button text', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('إرسال رابط إعادة التعيين');
      expect(content).toContain('Send Reset Link');
      expect(content).toContain('إرسال رمز التحقق');
      expect(content).toContain('Send OTP');
    });

    it('should have back to login link', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('العودة لتسجيل الدخول');
      expect(content).toContain('Back to Login');
    });

    it('should redirect to verify-otp for SMS/WhatsApp/Telegram channels', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('/verify-otp');
    });

    it('should show success state with bilingual text', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('تم الإرسال');
      expect(content).toContain('Sent Successfully');
    });

    it('should mention link validity period', () => {
      const content = readFile(FORGOT_PW);
      expect(content).toContain('الرابط صالح لمدة ساعة واحدة فقط');
      expect(content).toContain('The link is valid for 1 hour only');
    });
  });

  // ─── 1.5 Reset Password Page ───────────────────────────────────────────
  describe('1.5 Reset Password Page | صفحة إعادة تعيين كلمة المرور', () => {
    const RESET_PW = path.join(WEB_APP, 'app/(auth)/reset-password/ResetPasswordClient.tsx');

    it('should have ResetPasswordClient.tsx file', () => {
      expect(fileExists(RESET_PW)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(RESET_PW);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should have JWT token inspection function', () => {
      const content = readFile(RESET_PW);
      expect(content).toMatch(/function inspectJwt/);
    });

    it('should handle token states: pending, valid, expired, invalid', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain("'pending'");
      expect(content).toContain("'valid'");
      expect(content).toContain("'expired'");
      expect(content).toContain("'invalid'");
    });

    it('should verify token against backend endpoint', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('/api/auth/reset-password/verify');
    });

    it('should have newPassword and confirmPassword fields', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('newPassword');
      expect(content).toContain('confirmPassword');
    });

    it('should validate password minimum length', () => {
      const content = readFile(RESET_PW);
      expect(content).toMatch(/newPassword\.length\s*<\s*8/);
    });

    it('should validate passwords match', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('Passwords do not match');
    });

    it('should show bilingual expired token message', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('الرابط منتهي الصلاحية');
      expect(content).toContain('Link Expired');
    });

    it('should show bilingual invalid token message', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('رابط غير صالح');
      expect(content).toContain('Invalid Link');
    });

    it('should have bilingual success message', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('تم تغيير كلمة المرور بنجاح');
      expect(content).toContain('Password reset successful');
    });

    it('should have bilingual reset button text', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('إعادة تعيين كلمة المرور');
      expect(content).toContain('Reset Password');
    });

    it('should have "Request New Link" option for expired tokens', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('طلب رابط جديد');
      expect(content).toContain('Request New Link');
    });

    it('should redirect to login after 3 seconds on success', () => {
      const content = readFile(RESET_PW);
      expect(content).toMatch(/setTimeout.*3000/s);
      expect(content).toContain("router.push('/login')");
    });

    it('should use Suspense boundary', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('Suspense');
    });

    it('should use autoComplete="new-password"', () => {
      const content = readFile(RESET_PW);
      expect(content).toContain('autoComplete="new-password"');
    });
  });

  // ─── 1.6 Auth Layout & Loading & Error ──────────────────────────────────
  describe('1.6 Auth Layout, Loading & Error | التخطيط والتحميل والخطأ', () => {
    const AUTH_LAYOUT = path.join(WEB_APP, 'app/(auth)/layout.tsx');
    const AUTH_LOADING = path.join(WEB_APP, 'app/(auth)/loading.tsx');
    const AUTH_ERROR = path.join(WEB_APP, 'app/(auth)/error.tsx');

    it('should have auth layout.tsx', () => {
      expect(fileExists(AUTH_LAYOUT)).toBe(true);
    });

    it('should have auth loading.tsx', () => {
      expect(fileExists(AUTH_LOADING)).toBe(true);
    });

    it('should have auth error.tsx', () => {
      expect(fileExists(AUTH_ERROR)).toBe(true);
    });

    it('layout should have gradient background', () => {
      const content = readFile(AUTH_LAYOUT);
      expect(content).toMatch(/bg-gradient/);
      expect(content).toMatch(/sahool-green/);
    });

    it('layout should accept children prop', () => {
      const content = readFile(AUTH_LAYOUT);
      expect(content).toContain('children');
    });

    it('error boundary should be a client component', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('error boundary should sanitize error messages (XSS prevention)', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toMatch(/function sanitizeErrorMessage/);
      expect(content).toContain('&lt;');
      expect(content).toContain('&gt;');
      expect(content).toContain('&amp;');
      expect(content).toContain('&quot;');
    });

    it('error boundary should hide details in non-development environments', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toContain("process.env.NODE_ENV !== 'development'");
    });

    it('error boundary should have bilingual error heading', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toContain('خطأ في تسجيل الدخول');
      expect(content).toContain('Authentication Error');
    });

    it('error boundary should have bilingual retry button', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toContain('إعادة المحاولة');
      expect(content).toContain('Try Again');
    });

    it('error boundary should truncate long error messages', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toContain('MAX_ERROR_MESSAGE_LENGTH');
    });

    it('error boundary should log errors', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toMatch(/logger\.error/);
    });

    it('error boundary should have reset function support', () => {
      const content = readFile(AUTH_ERROR);
      expect(content).toContain('reset');
    });
  });
});

// =============================================================================
// 2. ADMIN APP AUTH UX — تجربة المصادقة للوحة الإدارة
// =============================================================================

describe('2. Admin App Auth UX | تجربة المصادقة للوحة الإدارة', () => {
  // ─── 2.1 Admin Login Page ───────────────────────────────────────────────
  describe('2.1 Admin Login Page | صفحة تسجيل الدخول للإدارة', () => {
    const ADMIN_LOGIN = path.join(ADMIN_APP, 'app/(auth)/login/page.tsx');

    it('should have admin login page.tsx', () => {
      expect(fileExists(ADMIN_LOGIN)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toMatch(/['"]use client['"]/);
    });

    it('should use email-only authentication (no phone toggle)', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toMatch(/type="email"/);
      // Admin login does not have a LoginMethod type toggle
      expect(content).not.toMatch(/type LoginMethod/);
    });

    it('should support 2FA (two-factor authentication)', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('requires2FA');
      expect(content).toContain('twoFACode');
    });

    it('should have 2FA code input with 6-digit max', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('maxLength={6}');
    });

    it('should have bilingual 2FA heading', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('التحقق الثنائي');
    });

    it('should have 2FA instruction text in Arabic', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('أدخل رمز التحقق من تطبيق المصادقة');
    });

    it('should have field-level validation with touched state', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('touched');
      expect(content).toContain('emailError');
      expect(content).toContain('passwordError');
    });

    it('should have Arabic email validation error', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('البريد الإلكتروني مطلوب');
    });

    it('should have Arabic email format error', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('صيغة البريد الإلكتروني غير صحيحة');
    });

    it('should have Arabic password validation error', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('كلمة المرور مطلوبة');
    });

    it('should validate password minimum length of 6', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toMatch(/value\.length\s*<\s*6/);
    });

    it('should have password visibility toggle', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('showPassword');
      expect(content).toContain('Eye');
      expect(content).toContain('EyeOff');
    });

    it('should have bilingual password visibility ARIA label', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('إخفاء كلمة المرور');
      expect(content).toContain('إظهار كلمة المرور');
    });

    it('should set dir="rtl" and lang="ar"', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('dir="rtl"');
      expect(content).toContain('lang="ar"');
    });

    it('should have ARIA attributes for form validation', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('aria-invalid');
      expect(content).toContain('aria-describedby');
    });

    it('should use role="alert" for error messages', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('role="alert"');
    });

    it('should have safe redirect handling (open redirect prevention)', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toMatch(/startsWith\(['"]\/['"]\)/);
      expect(content).toMatch(/startsWith\(['"]\/\/['"]\)/);
    });

    it('should default redirect to /dashboard', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain("'/dashboard'");
    });

    it('should have SAHOOL branding "سهول"', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('سهول');
    });

    it('should have admin-specific description', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('لوحة إدارة المنصة الزراعية');
    });

    it('should have link to registration page', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('href="/register"');
    });

    it('should have link to forgot-password page', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('href="/forgot-password"');
    });

    it('should have dark mode support', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toMatch(/dark:/);
    });

    it('should use validators utility for validation', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('validators');
    });

    it('should have Suspense boundary for useSearchParams', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('Suspense');
    });

    it('should have copyright footer', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('جميع الحقوق محفوظة');
    });

    it('should not have hardcoded demo credentials', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('Demo credentials removed for security');
      expect(content).not.toMatch(/password.*=.*['"](?:admin|test|demo|123|password)/i);
    });

    it('should use Leaf icon for branding', () => {
      const content = readFile(ADMIN_LOGIN);
      expect(content).toContain('Leaf');
    });
  });

  // ─── 2.2 Admin Register Page ────────────────────────────────────────────
  describe('2.2 Admin Register Page | صفحة تسجيل الإدارة', () => {
    const ADMIN_REGISTER = path.join(ADMIN_APP, 'app/(auth)/register/page.tsx');

    it('should have admin register page.tsx', () => {
      expect(fileExists(ADMIN_REGISTER)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toMatch(/['"]use client['"]/);
    });

    it('should have firstName field', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('firstName');
    });

    it('should have lastName field', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('lastName');
    });

    it('should have email field', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toMatch(/type="email"/);
    });

    it('should have optional phone field with Yemeni validation', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('اختياري');
      expect(content).toMatch(/type="tel"/);
      expect(content).toContain('validateYemeniPhone');
    });

    it('should validate Yemeni phone format', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toMatch(/\+967/);
      expect(content).toContain('رقم هاتف يمني غير صالح');
    });

    it('should have password field with visibility toggle', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('showPassword');
      expect(content).toContain('Eye');
      expect(content).toContain('EyeOff');
    });

    it('should require minimum 8 character password', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('minLength={8}');
    });

    it('should have Arabic password requirement text', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('يجب أن تكون كلمة المرور 8 أحرف على الأقل');
    });

    it('should set dir="rtl" and lang="ar"', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('dir="rtl"');
      expect(content).toContain('lang="ar"');
    });

    it('should have dark mode support', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toMatch(/dark:/);
    });

    it('should have link to login page', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('href="/login"');
    });

    it('should have ARIA attributes for phone validation', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('aria-invalid');
      expect(content).toContain('aria-describedby');
    });

    it('should use role="alert" for phone errors', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain('role="alert"');
    });

    it('should submit with credentials: same-origin', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain("credentials: 'same-origin'");
    });

    it('should redirect to login after successful registration', () => {
      const content = readFile(ADMIN_REGISTER);
      expect(content).toContain("router.push('/login')");
    });
  });

  // ─── 2.3 Admin Auth Layout ──────────────────────────────────────────────
  describe('2.3 Admin Auth Layout | تخطيط مصادقة الإدارة', () => {
    const ADMIN_LAYOUT = path.join(ADMIN_APP, 'app/(auth)/layout.tsx');

    it('should have admin auth layout.tsx', () => {
      expect(fileExists(ADMIN_LAYOUT)).toBe(true);
    });

    it('should accept children prop', () => {
      const content = readFile(ADMIN_LAYOUT);
      expect(content).toContain('children');
    });
  });
});

// =============================================================================
// 3. WEB NAVIGATION UX — تجربة التنقل لتطبيق الويب
// =============================================================================

describe('3. Web Navigation UX | تجربة التنقل لتطبيق الويب', () => {
  // ─── 3.1 Sidebar ────────────────────────────────────────────────────────
  describe('3.1 Sidebar | الشريط الجانبي', () => {
    const SIDEBAR = path.join(WEB_APP, 'components/layouts/sidebar.tsx');

    it('should have sidebar.tsx', () => {
      expect(fileExists(SIDEBAR)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(SIDEBAR);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should have dashboard nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/dashboard'");
    });

    it('should have farms nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/farms'");
    });

    it('should have fields nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/fields'");
    });

    it('should have crops nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/crops'");
    });

    it('should have irrigation nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/irrigation'");
    });

    it('should have weather nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/weather'");
    });

    it('should have satellite nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/satellite'");
    });

    it('should have equipment nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/equipment'");
    });

    it('should have marketplace nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/marketplace'");
    });

    it('should have settings nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/settings'");
    });

    it('should have copilot nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/copilot'");
    });

    it('should have alerts nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/alerts'");
    });

    it('should have reports nav item', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("href: '/reports'");
    });

    it('should have at least 10 navigation groups', () => {
      const content = readFile(SIDEBAR);
      const groupMatches = content.match(/groupKey:\s*'/g);
      expect(groupMatches).not.toBeNull();
      expect(groupMatches!.length).toBeGreaterThanOrEqual(10);
    });

    it('should have overview group', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("groupKey: 'overview'");
    });

    it('should have farmManagement group', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("groupKey: 'farmManagement'");
    });

    it('should have waterAndIrrigation group', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("groupKey: 'waterAndIrrigation'");
    });

    it('should have cropIntelligence group', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("groupKey: 'cropIntelligence'");
    });

    it('should have iotAndEquipment group', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("groupKey: 'iotAndEquipment'");
    });

    it('should have businessAndCommunity group', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("groupKey: 'businessAndCommunity'");
    });

    it('should use Next.js Link for navigation', () => {
      const content = readFile(SIDEBAR);
      expect(content).toMatch(/import Link from ['"]next\/link['"]/);
    });

    it('should use next-intl for translations', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('useTranslations');
      expect(content).toContain('next-intl');
    });

    it('should have responsive design: hidden on mobile, visible on desktop', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('hidden md:block');
    });

    it('should have mobile drawer overlay', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('md:hidden');
      expect(content).toContain('fixed inset-0');
    });

    it('should close drawer on Escape key', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("e.key === 'Escape'");
    });

    it('should close drawer on route change', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('pathname');
      expect(content).toMatch(/onClose/);
    });

    it('should have aria-current="page" for active items', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("aria-current={isActive ? 'page' : undefined}");
    });

    it('should have role="navigation" on aside element', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('role="navigation"');
    });

    it('should have aria-label for navigation', () => {
      const content = readFile(SIDEBAR);
      expect(content).toMatch(/aria-label=\{t\(['"]mainNav['"]\)\}/);
    });

    it('should have aria-hidden on icons', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('aria-hidden="true"');
    });

    it('should have mobile close button with aria-label', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain("aria-label={t('closeMenu')");
    });

    it('should have mobile drawer with role="dialog"', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('role="dialog"');
      expect(content).toContain('aria-modal="true"');
    });

    it('should have data-testid attributes for testing', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('data-testid="desktop-sidebar"');
      expect(content).toContain('data-testid="mobile-drawer"');
    });

    it('should have dark mode support', () => {
      const content = readFile(SIDEBAR);
      expect(content).toMatch(/dark:/);
    });

    it('should display version number', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('16.0.0');
    });

    it('should use React.memo for performance', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('React.memo');
    });

    it('should use lucide-react icons (40+ icons)', () => {
      const content = readFile(SIDEBAR);
      const iconImports = content.match(/\b[A-Z][a-zA-Z0-9]+(?=,|\s)/g) || [];
      const lucideIcons = iconImports.filter((i) =>
        ['LayoutDashboard', 'Sprout', 'Droplets', 'Satellite', 'MapPin', 'CloudSun', 'Bot', 'ShoppingCart', 'Truck', 'Cpu'].includes(i)
      );
      expect(lucideIcons.length).toBeGreaterThanOrEqual(5);
    });

    it('should have prefetch=false on nav links for performance', () => {
      const content = readFile(SIDEBAR);
      expect(content).toContain('prefetch={false}');
    });
  });

  // ─── 3.2 Header ────────────────────────────────────────────────────────
  describe('3.2 Header | رأس الصفحة', () => {
    const HEADER = path.join(WEB_APP, 'components/layouts/header.tsx');

    it('should have header.tsx', () => {
      expect(fileExists(HEADER)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(HEADER);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should have bilingual greeting', () => {
      const content = readFile(HEADER);
      expect(content).toContain('welcomeMessage');
    });

    it('should display user role badge', () => {
      const content = readFile(HEADER);
      expect(content).toContain('user?.role');
      expect(content).toContain('Badge');
    });

    it('should display user Arabic name when available', () => {
      const content = readFile(HEADER);
      expect(content).toContain('user?.name_ar');
    });

    it('should have notification bell button', () => {
      const content = readFile(HEADER);
      expect(content).toContain('Bell');
    });

    it('should show real unread notification count', () => {
      const content = readFile(HEADER);
      expect(content).toContain('useUnreadCount');
      expect(content).toContain('unreadCount');
    });

    it('should cap notification display at 99+', () => {
      const content = readFile(HEADER);
      expect(content).toContain("'99+'");
    });

    it('should have locale switcher', () => {
      const content = readFile(HEADER);
      expect(content).toContain('LocaleSwitcher');
    });

    it('should have theme toggle', () => {
      const content = readFile(HEADER);
      expect(content).toContain('ThemeToggle');
    });

    it('should have hamburger menu button for mobile', () => {
      const content = readFile(HEADER);
      expect(content).toContain('Menu');
      expect(content).toContain('md:hidden');
    });

    it('should lazy-load UserMenuDropdown', () => {
      const content = readFile(HEADER);
      expect(content).toContain('dynamic');
      expect(content).toContain('ssr: false');
    });

    it('should have aria-label for notification bell', () => {
      const content = readFile(HEADER);
      expect(content).toMatch(/aria-label/);
      expect(content).toContain('notifications');
    });

    it('should have aria-expanded for user menu', () => {
      const content = readFile(HEADER);
      expect(content).toContain('aria-expanded');
    });

    it('should have aria-haspopup for user menu', () => {
      const content = readFile(HEADER);
      expect(content).toContain('aria-haspopup="true"');
    });

    it('should have bilingual user menu aria-label', () => {
      const content = readFile(HEADER);
      expect(content).toContain('قائمة المستخدم');
      expect(content).toContain('User menu');
    });

    it('should have screen reader text for notification count', () => {
      const content = readFile(HEADER);
      expect(content).toContain('sr-only');
      expect(content).toContain('aria-live="polite"');
    });

    it('should handle logout and redirect to login', () => {
      const content = readFile(HEADER);
      expect(content).toContain('handleLogout');
      expect(content).toContain("router.push('/login')");
    });

    it('should use React.memo for performance', () => {
      const content = readFile(HEADER);
      expect(content).toContain('React.memo');
    });

    it('should close menu on outside click', () => {
      const content = readFile(HEADER);
      expect(content).toContain('handleClickOutside');
    });
  });

  // ─── 3.3 UserMenuDropdown ──────────────────────────────────────────────
  describe('3.3 UserMenuDropdown | قائمة المستخدم', () => {
    const USER_MENU = path.join(WEB_APP, 'components/layouts/UserMenuDropdown.tsx');

    it('should have UserMenuDropdown.tsx', () => {
      expect(fileExists(USER_MENU)).toBe(true);
    });

    it('should be a client component', () => {
      const content = readFile(USER_MENU);
      expect(content).toMatch(/^['"]use client['"]/);
    });

    it('should have profile option', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('onProfileClick');
      expect(content).toContain('profileLabel');
    });

    it('should have settings option', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('onSettingsClick');
      expect(content).toContain('settingsLabel');
    });

    it('should have logout option', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('onLogout');
      expect(content).toContain('logoutLabel');
      expect(content).toContain('LogOut');
    });

    it('should use role="menu" for accessibility', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('role="menu"');
    });

    it('should use role="menuitem" for menu items', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('role="menuitem"');
    });

    it('should have Arabic aria-label for menu', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('قائمة خيارات المستخدم');
    });

    it('should have overlay backdrop for closing', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('fixed inset-0');
      expect(content).toContain('onClose');
    });

    it('should display user name', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('userName');
    });

    it('should display user email', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('userEmail');
    });

    it('should have aria-label on each menu item', () => {
      const content = readFile(USER_MENU);
      const ariaLabels = content.match(/aria-label=\{/g);
      expect(ariaLabels).not.toBeNull();
      expect(ariaLabels!.length).toBeGreaterThanOrEqual(3);
    });

    it('should have red styling for logout button', () => {
      const content = readFile(USER_MENU);
      expect(content).toContain('text-red-600');
    });
  });
});

// =============================================================================
// 4. ADMIN DASHBOARD PAGES — صفحات لوحة الإدارة
// =============================================================================

describe('4. Admin Dashboard Pages | صفحات لوحة الإدارة', () => {
  const ADMIN_PAGES_DIR = path.join(ADMIN_APP, 'app');

  const expectedAdminPages = [
    'dashboard/page.tsx',
    'farms/page.tsx',
    'seasons/page.tsx',
    'diseases/page.tsx',
    'irrigation/page.tsx',
    'tasks/page.tsx',
    'sensors/page.tsx',
    'alerts/page.tsx',
    'weather/page.tsx',
    'epidemic/page.tsx',
    'yield/page.tsx',
    'users/page.tsx',
    'equipment/page.tsx',
    'cooperatives/page.tsx',
    'inventory/page.tsx',
    'marketplace/page.tsx',
    'market-prices/page.tsx',
    'insurance/page.tsx',
    'seeds/page.tsx',
    'soil-map/page.tsx',
    'research/page.tsx',
    'compliance/page.tsx',
    'traceability/page.tsx',
    'copilot/page.tsx',
    'code-review/page.tsx',
    'vision/page.tsx',
    'drone/page.tsx',
    'edge-devices/page.tsx',
    'terrain/page.tsx',
    'virtual-sensors/page.tsx',
    'scouting/page.tsx',
    'audit/page.tsx',
    'reports/page.tsx',
    'support/page.tsx',
    'settings/page.tsx',
  ];

  it('should have 35+ admin dashboard pages', () => {
    const existing = expectedAdminPages.filter((p) =>
      fileExists(path.join(ADMIN_PAGES_DIR, p))
    );
    expect(existing.length).toBeGreaterThanOrEqual(35);
  });

  expectedAdminPages.forEach((pagePath) => {
    it(`should have admin page: ${pagePath}`, () => {
      expect(fileExists(path.join(ADMIN_PAGES_DIR, pagePath))).toBe(true);
    });
  });

  it('should have admin dashboard layout', () => {
    expect(fileExists(path.join(ADMIN_PAGES_DIR, '(dashboard)/layout.tsx'))).toBe(true);
  });

  it('should have precision agriculture sub-pages', () => {
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'precision-agriculture/vra/page.tsx'))).toBe(true);
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'precision-agriculture/gdd/page.tsx'))).toBe(true);
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'precision-agriculture/spray/page.tsx'))).toBe(true);
  });

  it('should have analytics sub-pages', () => {
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'analytics/profitability/page.tsx'))).toBe(true);
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'analytics/yield/page.tsx'))).toBe(true);
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'analytics/satellite/page.tsx'))).toBe(true);
  });

  it('should have farm detail page with dynamic route', () => {
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'farms/[id]/page.tsx'))).toBe(true);
  });

  it('should have equipment fleet-tracking sub-page', () => {
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'equipment/fleet-tracking/page.tsx'))).toBe(true);
  });

  it('should have settings/security sub-page', () => {
    expect(fileExists(path.join(ADMIN_PAGES_DIR, 'settings/security/page.tsx'))).toBe(true);
  });
});

// =============================================================================
// 5. BILINGUAL / i18n UX — تجربة ثنائية اللغة / التدويل
// =============================================================================

describe('5. Bilingual / i18n UX | تجربة ثنائية اللغة', () => {
  it('web login should have Arabic content', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('web register should have Arabic content', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/register/RegisterClient.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('web verify-otp should have Arabic content', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/verify-otp/VerifyOTPClient.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('web forgot-password should have Arabic content', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/forgot-password/ForgotPasswordClient.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('web reset-password should have Arabic content', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/reset-password/ResetPasswordClient.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('web error page should have Arabic content', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/error.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('admin login should have Arabic content', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('admin register should have Arabic content', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/register/page.tsx'));
    expect(content).toMatch(ARABIC_RE);
  });

  it('web sidebar should use i18n translations', () => {
    const content = readFile(path.join(WEB_APP, 'components/layouts/sidebar.tsx'));
    expect(content).toContain('useTranslations');
  });

  it('web header should use i18n translations', () => {
    const content = readFile(path.join(WEB_APP, 'components/layouts/header.tsx'));
    expect(content).toContain('useTranslations');
  });

  it('admin login should set RTL direction', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toContain('dir="rtl"');
  });

  it('admin register should set RTL direction', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/register/page.tsx'));
    expect(content).toContain('dir="rtl"');
  });

  it('OTP input should use LTR direction for number entry', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/verify-otp/VerifyOTPClient.tsx'));
    expect(content).toContain('dir="ltr"');
  });

  it('admin email inputs should use LTR direction', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toContain('dir="ltr"');
  });

  it('web login should use bilingual toast messages (messageAr + message)', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toMatch(/messageAr:/);
    expect(content).toMatch(/\bmessage:/);
  });

  it('web register should use bilingual toast messages', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/register/RegisterClient.tsx'));
    expect(content).toMatch(/messageAr:/);
    expect(content).toMatch(/\bmessage:/);
  });

  it('web login should have bilingual input labels (label + labelAr)', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toMatch(/\blabel="/);
    expect(content).toMatch(/labelAr="/);
  });
});

// =============================================================================
// 6. ACCESSIBILITY UX PATTERNS — أنماط إمكانية الوصول
// =============================================================================

describe('6. Accessibility UX Patterns | أنماط إمكانية الوصول', () => {
  it('login form should use type="email" for email inputs', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('type="email"');
  });

  it('login form should use type="password" for password inputs', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('type="password"');
  });

  it('login form should use type="tel" for phone inputs', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('type="tel"');
  });

  it('login form should have type="submit" button', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('type="submit"');
  });

  it('register form should have type="submit" button', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/register/RegisterClient.tsx'));
    expect(content).toContain('type="submit"');
  });

  it('admin login should have type="submit" button', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toContain('type="submit"');
  });

  it('admin register should have type="submit" button', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/register/page.tsx'));
    expect(content).toContain('type="submit"');
  });

  it('web login should use Next.js Link for internal navigation', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toMatch(/import Link from ['"]next\/link['"]/);
    expect(content).toContain('<Link');
  });

  it('web register should use Next.js Link', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/register/RegisterClient.tsx'));
    expect(content).toMatch(/import Link from ['"]next\/link['"]/);
  });

  it('admin login should use Next.js Link', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toMatch(/import Link from ['"]next\/link['"]/);
  });

  it('sidebar should use Next.js Link for navigation', () => {
    const content = readFile(path.join(WEB_APP, 'components/layouts/sidebar.tsx'));
    expect(content).toMatch(/import Link from ['"]next\/link['"]/);
  });

  it('admin login should have htmlFor on labels', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toContain('htmlFor="email"');
    expect(content).toContain('htmlFor="password"');
  });

  it('admin register should have htmlFor on labels', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/register/page.tsx'));
    expect(content).toContain('htmlFor="firstName"');
    expect(content).toContain('htmlFor="lastName"');
    expect(content).toContain('htmlFor="email"');
    expect(content).toContain('htmlFor="password"');
  });

  it('admin login should have matching id attributes on inputs', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toContain('id="email"');
    expect(content).toContain('id="password"');
  });

  it('sidebar links should have aria-label for each nav item', () => {
    const content = readFile(path.join(WEB_APP, 'components/layouts/sidebar.tsx'));
    expect(content).toMatch(/aria-label=\{t\(item\.labelKey\)\}/);
  });

  it('user menu dropdown should use proper ARIA roles', () => {
    const content = readFile(path.join(WEB_APP, 'components/layouts/UserMenuDropdown.tsx'));
    expect(content).toContain('role="menu"');
    expect(content).toContain('role="menuitem"');
  });

  it('OTP inputs should have inputMode="numeric"', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/verify-otp/VerifyOTPClient.tsx'));
    expect(content).toContain('inputMode="numeric"');
  });

  it('decorative icons should be hidden from screen readers', () => {
    const loginContent = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    const sidebarContent = readFile(path.join(WEB_APP, 'components/layouts/sidebar.tsx'));
    expect(loginContent).toContain('aria-hidden="true"');
    expect(sidebarContent).toContain('aria-hidden="true"');
  });

  it('header notification should have screen reader live region', () => {
    const content = readFile(path.join(WEB_APP, 'components/layouts/header.tsx'));
    expect(content).toContain('aria-live="polite"');
    expect(content).toContain('sr-only');
  });

  it('form inputs should have required attribute', () => {
    const loginContent = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(loginContent).toMatch(/required/);
  });

  it('web login form method toggle should have radiogroup role', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('role="radiogroup"');
  });
});

// =============================================================================
// 7. SECURITY UX — أمان تجربة المستخدم
// =============================================================================

describe('7. Security UX | أمان تجربة المستخدم', () => {
  const authFiles = [
    path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'),
    path.join(WEB_APP, 'app/(auth)/register/RegisterClient.tsx'),
    path.join(WEB_APP, 'app/(auth)/verify-otp/VerifyOTPClient.tsx'),
    path.join(WEB_APP, 'app/(auth)/forgot-password/ForgotPasswordClient.tsx'),
    path.join(WEB_APP, 'app/(auth)/reset-password/ResetPasswordClient.tsx'),
    path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'),
    path.join(ADMIN_APP, 'app/(auth)/register/page.tsx'),
  ];

  authFiles.forEach((filePath) => {
    const name = path.relative(ROOT, filePath);

    it(`${name}: should not contain hardcoded passwords`, () => {
      const content = readFile(filePath);
      expect(content).not.toMatch(/password\s*[:=]\s*['"](?:admin|test|demo|123456|password)/i);
    });

    it(`${name}: should not use eval()`, () => {
      const content = readFile(filePath);
      expect(content).not.toMatch(/\beval\s*\(/);
    });

    it(`${name}: should not use dangerouslySetInnerHTML`, () => {
      const content = readFile(filePath);
      expect(content).not.toContain('dangerouslySetInnerHTML');
    });
  });

  it('web login should have isSafeReturnTo for redirect protection', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('isSafeReturnTo');
  });

  it('admin login should prevent open redirect via // check', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toMatch(/startsWith\(['"]\/\/['"]\)/);
  });

  it('error boundary should sanitize HTML in error messages', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/error.tsx'));
    expect(content).toContain('sanitizeErrorMessage');
    expect(content).toContain('&lt;');
    expect(content).toContain('&gt;');
  });

  it('error boundary should hide internals in production', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/error.tsx'));
    expect(content).toContain("process.env.NODE_ENV !== 'development'");
  });

  it('web login should use httpOnly cookie approach', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('httpOnly cookie');
  });

  it('web register should use same-origin fetch for CSRF protection', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/register/RegisterClient.tsx'));
    // RegisterClient uses authApiClient (which handles same-origin)
    expect(content).toContain('authApiClient');
  });

  it('admin register should use credentials: same-origin', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/register/page.tsx'));
    expect(content).toContain("credentials: 'same-origin'");
  });

  it('reset password should verify token before showing form', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/reset-password/ResetPasswordClient.tsx'));
    expect(content).toContain('inspectJwt');
    expect(content).toContain('/api/auth/reset-password/verify');
  });

  it('admin login should not expose demo credentials', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toContain('Demo credentials removed for security');
  });

  it('OTP verification should not expose server error details', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/verify-otp/VerifyOTPClient.tsx'));
    expect(content).toMatch(/Do not expose server error details/);
  });

  it('sidebar overlay should have aria-hidden for backdrop', () => {
    const content = readFile(path.join(WEB_APP, 'components/layouts/sidebar.tsx'));
    expect(content).toContain('aria-hidden="true"');
  });

  it('no auth file should contain localStorage token storage pattern', () => {
    for (const filePath of authFiles) {
      const content = readFile(filePath);
      expect(content).not.toMatch(/localStorage\.(setItem|getItem)\(['"](?:token|access_token|jwt)['"]/);
    }
  });

  it('web login should prevent form submission during loading', () => {
    const content = readFile(path.join(WEB_APP, 'app/(auth)/login/LoginClient.tsx'));
    expect(content).toContain('isLoading');
    expect(content).toContain('setIsLoading(true)');
    expect(content).toContain('setIsLoading(false)');
  });

  it('admin login submit should be disabled during loading', () => {
    const content = readFile(path.join(ADMIN_APP, 'app/(auth)/login/page.tsx'));
    expect(content).toContain('disabled={isLoading}');
  });
});
