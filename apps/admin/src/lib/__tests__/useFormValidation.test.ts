/**
 * Form Validation Integration Tests
 * اختبارات تكامل التحقق من النماذج
 *
 * Tests real-world form validation workflows using the validation utilities.
 */

import { describe, it, expect } from "vitest";
import {
  validators,
  sanitizers,
  validateInput,
  validateForm,
  isFormValid,
  validationErrors,
} from "../validation";

// ═══════════════════════════════════════════════════════════════════════════
// Login Form Validation | التحقق من نموذج تسجيل الدخول
// ═══════════════════════════════════════════════════════════════════════════

describe("Login Form Validation", () => {
  it("validates a complete login form", () => {
    const results = validateForm(
      { email: "admin@sahool.io", password: "SecureP@ss1" },
      { email: "email", password: "password" },
    );

    expect(isFormValid(results)).toBe(true);
  });

  it("catches empty email and password", () => {
    const results = validateForm(
      { email: "", password: "" },
      { email: "email", password: "password" },
    );

    expect(isFormValid(results)).toBe(false);
    expect(results.email?.error).toBe(validationErrors.required);
    expect(results.password?.error).toBe(validationErrors.required);
  });

  it("catches invalid email format", () => {
    const results = validateForm(
      { email: "not-an-email", password: "SecureP@ss1" },
      { email: "email", password: "password" },
    );

    expect(results.email?.isValid).toBe(false);
    expect(results.password?.isValid).toBe(true);
    expect(isFormValid(results)).toBe(false);
  });

  it("catches weak password", () => {
    const results = validateForm(
      { email: "admin@sahool.io", password: "short" },
      { email: "email", password: "password" },
    );

    expect(results.email?.isValid).toBe(true);
    expect(results.password?.isValid).toBe(false);
    expect(isFormValid(results)).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// User Registration Form | نموذج تسجيل المستخدم
// ═══════════════════════════════════════════════════════════════════════════

describe("User Registration Form Validation", () => {
  it("validates complete registration data", () => {
    const results = validateForm(
      {
        email: "farmer@sahool.io",
        password: "Str0ng!Pass",
        phone: "+967 123456789",
      },
      {
        email: "email",
        password: "password",
        phone: "phone",
      },
    );

    expect(isFormValid(results)).toBe(true);
  });

  it("validates phone number formats", () => {
    // Valid
    expect(validateInput("+967 1234567890", "phone").isValid).toBe(true);
    expect(validateInput("01234567890", "phone").isValid).toBe(true);

    // Invalid
    expect(validateInput("123", "phone").isValid).toBe(false);
  });

  it("catches all invalid fields at once", () => {
    const results = validateForm(
      {
        email: "bad",
        password: "weak",
        phone: "123",
      },
      {
        email: "email",
        password: "password",
        phone: "phone",
      },
    );

    expect(results.email?.isValid).toBe(false);
    expect(results.password?.isValid).toBe(false);
    expect(results.phone?.isValid).toBe(false);
    expect(isFormValid(results)).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 2FA Code Validation | التحقق من رمز المصادقة الثنائية
// ═══════════════════════════════════════════════════════════════════════════

describe("2FA Code Validation", () => {
  it("validates correct 6-digit code", () => {
    expect(validateInput("123456", "twoFactorCode").isValid).toBe(true);
    expect(validateInput("000000", "twoFactorCode").isValid).toBe(true);
  });

  it("rejects codes with wrong length", () => {
    expect(validateInput("12345", "twoFactorCode").isValid).toBe(false);
    expect(validateInput("1234567", "twoFactorCode").isValid).toBe(false);
  });

  it("rejects non-numeric codes", () => {
    expect(validateInput("abcdef", "twoFactorCode").isValid).toBe(false);
  });

  it("trims whitespace from code", () => {
    expect(validateInput(" 123456 ", "twoFactorCode").isValid).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Field/Farm Form Validation (Safe Text) | التحقق من نموذج الحقل
// ═══════════════════════════════════════════════════════════════════════════

describe("Field Form Validation (Safe Text)", () => {
  it("accepts Arabic text", () => {
    expect(validators.safeText("حقل القمح الشمالي")).toBe(true);
    expect(validators.safeText("مزرعة الريف ١")).toBe(true);
  });

  it("accepts English text", () => {
    expect(validators.safeText("Northern Wheat Field")).toBe(true);
  });

  it("accepts mixed Arabic-English text", () => {
    expect(validators.safeText("حقل A - Field A")).toBe(true);
  });

  it("rejects XSS attempts in field names", () => {
    expect(validators.safeText('<script>alert("xss")</script>')).toBe(false);
    expect(validators.safeText("onclick=malicious()")).toBe(false);
    expect(validators.safeText("javascript:alert(1)")).toBe(false);
  });

  it("allows SQL-like text (SQL injection handled at database layer)", () => {
    // safeText only checks for XSS patterns, not SQL injection
    // SQL injection prevention is handled by parameterized queries at the DB layer
    expect(validators.safeText("'; DROP TABLE fields; --")).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Sanitization Workflows | سير عمل التطهير
// ═══════════════════════════════════════════════════════════════════════════

describe("Sanitization Workflows", () => {
  it("sanitizes email before validation", () => {
    const rawEmail = "  Admin@Sahool.IO  ";
    const sanitized = sanitizers.email(rawEmail);
    expect(sanitized).toBe("admin@sahool.io");
    expect(validators.email(sanitized)).toBe(true);
  });

  it("sanitizes HTML from user input", () => {
    const maliciousInput = '<b>Bold</b><script>alert("xss")</script>';
    const sanitized = sanitizers.html(maliciousInput);
    expect(sanitized).not.toContain("<script>");
    expect(sanitized).not.toContain("<b>");
    expect(sanitized).toContain("Bold");
  });

  it("sanitizes phone number", () => {
    const rawPhone = "+967-123 abc 4567";
    const sanitized = sanitizers.phone(rawPhone);
    expect(sanitized).not.toContain("abc");
  });

  it("sanitizes filename to prevent path traversal", () => {
    const maliciousFilename = "../../../etc/passwd";
    const sanitized = sanitizers.filename(maliciousFilename);
    expect(sanitized).not.toContain("../");
  });

  it("sanitizes numbers", () => {
    const rawNumber = "$1,234.56";
    const sanitized = sanitizers.number(rawNumber);
    expect(sanitized).toBe("1234.56");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// URL Validation | التحقق من الروابط
// ═══════════════════════════════════════════════════════════════════════════

describe("URL Validation for Farm Links", () => {
  it("accepts valid HTTPS URLs", () => {
    expect(validators.url("https://sahool.io")).toBe(true);
    expect(validators.url("https://api.sahool.io/v1/fields")).toBe(true);
  });

  it("accepts HTTP URLs for development", () => {
    expect(validators.url("http://localhost:3000")).toBe(true);
  });

  it("rejects dangerous protocols", () => {
    expect(validators.url("javascript:alert(1)")).toBe(false);
    expect(validators.url("ftp://files.com")).toBe(false);
  });

  it("rejects malformed URLs", () => {
    expect(validators.url("not-a-url")).toBe(false);
    expect(validators.url("")).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages Bilingual | رسائل الخطأ ثنائية اللغة
// ═══════════════════════════════════════════════════════════════════════════

describe("Bilingual Error Messages", () => {
  it("provides Arabic error for required fields", () => {
    expect(validationErrors.required).toContain("مطلوب");
  });

  it("provides Arabic error for email", () => {
    expect(validationErrors.email).toContain("بريد إلكتروني");
  });

  it("provides Arabic error for password", () => {
    expect(validationErrors.password).toContain("كلمة المرور");
  });

  it("provides Arabic error for 2FA code", () => {
    expect(validationErrors.twoFactorCode).toContain("أرقام");
  });

  it("returns validation error message for invalid input", () => {
    const result = validateInput("bad-email", "email");
    expect(result.isValid).toBe(false);
    expect(result.error).toBeDefined();
    expect(typeof result.error).toBe("string");
    expect(result.error!.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Edge Cases | حالات الحدود
// ═══════════════════════════════════════════════════════════════════════════

describe("Edge Cases", () => {
  it("handles null/undefined values gracefully", () => {
    expect(validators.email(null as unknown as string)).toBe(false);
    expect(validators.password(undefined as unknown as string)).toBe(false);
    expect(validators.phone(null as unknown as string)).toBe(false);
  });

  it("handles very long input", () => {
    const longString = "a".repeat(1000);
    expect(validators.email(longString + "@b.com")).toBe(false);
  });

  it("validates empty form returns all errors", () => {
    const results = validateForm(
      { email: "", password: "", phone: "" },
      { email: "email", password: "password", phone: "phone" },
    );

    expect(results.email?.isValid).toBe(false);
    expect(results.password?.isValid).toBe(false);
    expect(results.phone?.isValid).toBe(false);
  });

  it("isFormValid returns true for empty results (no fields)", () => {
    expect(isFormValid({})).toBe(true);
  });
});
