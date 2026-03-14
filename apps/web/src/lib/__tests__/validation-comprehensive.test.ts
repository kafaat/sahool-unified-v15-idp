/**
 * Comprehensive Validation & Sanitization Tests - SAHOOL Platform
 * اختبارات شاملة للتحقق والتعقيم - منصة سهول
 *
 * Extended coverage for edge cases, security vectors, and bilingual validation
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
// Validator Edge Case Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("validators - comprehensive edge cases", () => {
  describe("twoFactorCode", () => {
    it("should accept code with leading zeros", () => {
      expect(validators.twoFactorCode("000001")).toBe(true);
    });

    it("should accept code with all zeros", () => {
      expect(validators.twoFactorCode("000000")).toBe(true);
    });

    it("should trim whitespace and accept valid code", () => {
      expect(validators.twoFactorCode("  123456  ")).toBe(true);
    });

    it("should reject code with spaces in between", () => {
      expect(validators.twoFactorCode("123 456")).toBe(false);
    });

    it("should reject empty string", () => {
      expect(validators.twoFactorCode("")).toBe(false);
    });

    it("should reject null", () => {
      expect(validators.twoFactorCode(null as any)).toBe(false);
    });

    it("should reject undefined", () => {
      expect(validators.twoFactorCode(undefined as any)).toBe(false);
    });

    it("should reject number type", () => {
      expect(validators.twoFactorCode(123456 as any)).toBe(false);
    });

    it("should reject code with special characters", () => {
      expect(validators.twoFactorCode("12345!")).toBe(false);
    });

    it("should reject code with Arabic numerals", () => {
      expect(validators.twoFactorCode("١٢٣٤٥٦")).toBe(false);
    });
  });

  describe("email", () => {
    it("should accept valid international email", () => {
      expect(validators.email("user@domain.co.uk")).toBe(true);
    });

    it("should accept email with plus addressing", () => {
      expect(validators.email("user+tag@example.com")).toBe(true);
    });

    it("should accept email with dots in local part", () => {
      expect(validators.email("first.last@example.com")).toBe(true);
    });

    it("should accept email with hyphens in domain", () => {
      expect(validators.email("user@my-domain.com")).toBe(true);
    });

    it("should reject email exceeding 254 characters", () => {
      const longEmail = "a".repeat(250) + "@test.com";
      expect(validators.email(longEmail)).toBe(false);
    });

    it("should reject email with double @", () => {
      expect(validators.email("user@@example.com")).toBe(false);
    });

    it("should reject email without domain extension", () => {
      expect(validators.email("user@domain")).toBe(false);
    });

    it("should reject empty string", () => {
      expect(validators.email("")).toBe(false);
    });

    it("should reject null", () => {
      expect(validators.email(null as any)).toBe(false);
    });

    it("should accept email with subdomain", () => {
      expect(validators.email("user@sub.domain.com")).toBe(true);
    });
  });

  describe("phone", () => {
    it("should accept Saudi phone number", () => {
      expect(validators.phone("+966 50 123 4567")).toBe(true);
    });

    it("should accept Yemen phone number", () => {
      expect(validators.phone("+967-1-234-567")).toBe(true);
    });

    it("should accept phone with dashes", () => {
      expect(validators.phone("555-123-4567")).toBe(true);
    });

    it("should reject short phone number", () => {
      expect(validators.phone("12345")).toBe(false);
    });

    it("should reject phone with letters", () => {
      expect(validators.phone("+1-800-FLOWERS")).toBe(false);
    });

    it("should reject empty string", () => {
      expect(validators.phone("")).toBe(false);
    });

    it("should reject null", () => {
      expect(validators.phone(null as any)).toBe(false);
    });
  });

  describe("url", () => {
    it("should accept https url", () => {
      expect(validators.url("https://sahool.app")).toBe(true);
    });

    it("should accept http url", () => {
      expect(validators.url("http://example.com")).toBe(true);
    });

    it("should accept url with path", () => {
      expect(validators.url("https://api.sahool.app/v1/fields")).toBe(true);
    });

    it("should accept url with query params", () => {
      expect(validators.url("https://example.com?key=value&foo=bar")).toBe(true);
    });

    it("should accept url with port", () => {
      expect(validators.url("http://localhost:3000")).toBe(true);
    });

    it("should reject ftp protocol", () => {
      expect(validators.url("ftp://files.example.com")).toBe(false);
    });

    it("should reject javascript protocol", () => {
      expect(validators.url("javascript:alert(1)")).toBe(false);
    });

    it("should reject data protocol", () => {
      expect(validators.url("data:text/html,<h1>XSS</h1>")).toBe(false);
    });

    it("should reject plain text", () => {
      expect(validators.url("not a url")).toBe(false);
    });

    it("should reject empty string", () => {
      expect(validators.url("")).toBe(false);
    });

    it("should reject null", () => {
      expect(validators.url(null as any)).toBe(false);
    });
  });

  describe("password", () => {
    it("should accept complex password", () => {
      expect(validators.password("MyStr0ng!Pass")).toBe(true);
    });

    it("should accept password with Arabic and Latin mix", () => {
      expect(validators.password("Arabic1!Aa")).toBe(true);
    });

    it("should reject password under 8 chars", () => {
      expect(validators.password("Aa1!")).toBe(false);
    });

    it("should reject password without uppercase", () => {
      expect(validators.password("lowercase1!")).toBe(false);
    });

    it("should reject password without lowercase", () => {
      expect(validators.password("UPPERCASE1!")).toBe(false);
    });

    it("should reject password without number", () => {
      expect(validators.password("NoNumber!Aa")).toBe(false);
    });

    it("should reject password without special char", () => {
      expect(validators.password("NoSpecial1Aa")).toBe(false);
    });

    it("should reject empty string", () => {
      expect(validators.password("")).toBe(false);
    });

    it("should reject null", () => {
      expect(validators.password(null as any)).toBe(false);
    });

    it("should accept all valid special chars", () => {
      expect(validators.password("Test1@#$%^&*()")).toBe(true);
    });
  });

  describe("number", () => {
    it("should accept positive integer string", () => {
      expect(validators.number("42")).toBe(true);
    });

    it("should accept negative integer string", () => {
      expect(validators.number("-42")).toBe(true);
    });

    it("should accept decimal string", () => {
      expect(validators.number("3.14")).toBe(true);
    });

    it("should accept negative decimal string", () => {
      expect(validators.number("-3.14")).toBe(true);
    });

    it("should accept number type", () => {
      expect(validators.number(42)).toBe(true);
    });

    it("should reject NaN", () => {
      expect(validators.number(NaN)).toBe(false);
    });

    it("should reject Infinity", () => {
      expect(validators.number(Infinity)).toBe(false);
    });

    it("should reject text", () => {
      expect(validators.number("not a number")).toBe(false);
    });

    it("should reject empty string", () => {
      expect(validators.number("")).toBe(false);
    });

    it("should reject boolean", () => {
      expect(validators.number(true as any)).toBe(false);
    });
  });

  describe("alphanumeric", () => {
    it("should accept letters only", () => {
      expect(validators.alphanumeric("Hello")).toBe(true);
    });

    it("should accept numbers only", () => {
      expect(validators.alphanumeric("12345")).toBe(true);
    });

    it("should accept mixed letters and numbers", () => {
      expect(validators.alphanumeric("Hello123")).toBe(true);
    });

    it("should reject special characters", () => {
      expect(validators.alphanumeric("hello!")).toBe(false);
    });

    it("should reject spaces", () => {
      expect(validators.alphanumeric("hello world")).toBe(false);
    });

    it("should reject empty string", () => {
      expect(validators.alphanumeric("")).toBe(false);
    });

    it("should reject null", () => {
      expect(validators.alphanumeric(null as any)).toBe(false);
    });

    it("should reject Arabic text", () => {
      expect(validators.alphanumeric("مرحبا")).toBe(false);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Sanitizer Edge Case Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("sanitizers - comprehensive edge cases", () => {
  describe("escape", () => {
    it("should escape ampersand", () => {
      expect(sanitizers.escape("Tom & Jerry")).toContain("&amp;");
    });

    it("should escape less-than", () => {
      expect(sanitizers.escape("a < b")).toContain("&lt;");
    });

    it("should escape greater-than", () => {
      expect(sanitizers.escape("a > b")).toContain("&gt;");
    });

    it("should handle empty string", () => {
      expect(sanitizers.escape("")).toBe("");
    });

    it("should handle null", () => {
      expect(sanitizers.escape(null as any)).toBe("");
    });

    it("should handle plain text", () => {
      const text = "no special chars";
      const result = sanitizers.escape(text);
      expect(result).toBe(text);
    });

    it("should handle Arabic text with HTML", () => {
      const result = sanitizers.escape("<b>مرحبا</b>");
      expect(result).toContain("&lt;");
      expect(result).not.toContain("<b>");
    });
  });

  describe("email", () => {
    it("should lowercase and trim", () => {
      expect(sanitizers.email("  User@EXAMPLE.COM  ")).toBe("user@example.com");
    });

    it("should remove invalid characters", () => {
      const result = sanitizers.email("user<script>@example.com");
      expect(result).not.toContain("<");
      expect(result).not.toContain(">");
    });

    it("should handle empty string", () => {
      expect(sanitizers.email("")).toBe("");
    });

    it("should handle null", () => {
      expect(sanitizers.email(null as any)).toBe("");
    });

    it("should preserve plus addressing", () => {
      expect(sanitizers.email("user+tag@example.com")).toBe("user+tag@example.com");
    });

    it("should preserve dots", () => {
      expect(sanitizers.email("first.last@example.com")).toBe("first.last@example.com");
    });
  });

  describe("phone", () => {
    it("should keep digits and +", () => {
      expect(sanitizers.phone("+1 (555) 123-4567")).toBe("+1 555 123-4567");
    });

    it("should remove letters", () => {
      expect(sanitizers.phone("abc123")).toBe("123");
    });

    it("should handle empty string", () => {
      expect(sanitizers.phone("")).toBe("");
    });

    it("should handle null", () => {
      expect(sanitizers.phone(null as any)).toBe("");
    });

    it("should keep international format", () => {
      expect(sanitizers.phone("+966501234567")).toBe("+966501234567");
    });
  });

  describe("number", () => {
    it("should keep digits and decimal", () => {
      expect(sanitizers.number("$1,234.56")).toBe("1234.56");
    });

    it("should keep negative sign", () => {
      expect(sanitizers.number("-42.5")).toBe("-42.5");
    });

    it("should remove non-numeric", () => {
      expect(sanitizers.number("abc")).toBe("");
    });

    it("should handle empty string", () => {
      expect(sanitizers.number("")).toBe("");
    });

    it("should handle null", () => {
      expect(sanitizers.number(null as any)).toBe("");
    });
  });

  describe("alphanumeric", () => {
    it("should remove special characters", () => {
      expect(sanitizers.alphanumeric("hello!@#world")).toBe("helloworld");
    });

    it("should remove spaces", () => {
      expect(sanitizers.alphanumeric("hello world")).toBe("helloworld");
    });

    it("should handle empty string", () => {
      expect(sanitizers.alphanumeric("")).toBe("");
    });

    it("should handle null", () => {
      expect(sanitizers.alphanumeric(null as any)).toBe("");
    });

    it("should keep only a-z, A-Z, 0-9", () => {
      expect(sanitizers.alphanumeric("Test123!@#")).toBe("Test123");
    });
  });

  describe("filename", () => {
    it("should prevent path traversal", () => {
      expect(sanitizers.filename("../../../etc/passwd")).not.toContain("..");
    });

    it("should replace special chars with underscore", () => {
      const result = sanitizers.filename("file name (1).txt");
      expect(result).not.toContain(" ");
      expect(result).not.toContain("(");
    });

    it("should keep valid chars", () => {
      expect(sanitizers.filename("valid-file_name.txt")).toBe("valid-file_name.txt");
    });

    it("should limit length to 255", () => {
      const longName = "a".repeat(300) + ".txt";
      expect(sanitizers.filename(longName).length).toBeLessThanOrEqual(255);
    });

    it("should handle empty string", () => {
      expect(sanitizers.filename("")).toBe("");
    });

    it("should handle null", () => {
      expect(sanitizers.filename(null as any)).toBe("");
    });

    it("should prevent Windows path traversal", () => {
      const result = sanitizers.filename("..\\..\\windows\\system32");
      expect(result).not.toContain("..");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Arabic Error Messages Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("validationErrors - Arabic messages", () => {
  it("should have Arabic error for twoFactorCode", () => {
    expect(validationErrors.twoFactorCode).toContain("6 أرقام");
  });

  it("should have Arabic error for email", () => {
    expect(validationErrors.email).toContain("بريد إلكتروني");
  });

  it("should have Arabic error for phone", () => {
    expect(validationErrors.phone).toContain("رقم هاتف");
  });

  it("should have Arabic error for password", () => {
    expect(validationErrors.password).toContain("8 أحرف");
  });

  it("should have Arabic error for required", () => {
    expect(validationErrors.required).toContain("مطلوب");
  });

  it("should have Arabic error for tooLong", () => {
    expect(validationErrors.tooLong).toBeTruthy();
  });

  it("should have Arabic error for tooShort", () => {
    expect(validationErrors.tooShort).toBeTruthy();
  });

  it("should have all validator keys covered", () => {
    const validatorKeys = Object.keys(validators);
    for (const key of validatorKeys) {
      expect(validationErrors[key as keyof typeof validationErrors]).toBeTruthy();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Combined Validation Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("validateInput - comprehensive", () => {
  it("should return required error for empty input", () => {
    const result = validateInput("", "email");
    expect(result.isValid).toBe(false);
    expect(result.error).toBe(validationErrors.required);
    expect(result.value).toBe("");
  });

  it("should validate and sanitize phone", () => {
    const result = validateInput("+966 501234567", "phone");
    expect(result.isValid).toBe(true);
  });

  it("should reject invalid phone", () => {
    const result = validateInput("123", "phone");
    expect(result.isValid).toBe(false);
    expect(result.error).toBeTruthy();
  });

  it("should validate password", () => {
    const result = validateInput("Str0ng!Pass", "password");
    expect(result.isValid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it("should reject weak password", () => {
    const result = validateInput("weak", "password");
    expect(result.isValid).toBe(false);
    expect(result.error).toBeTruthy();
  });

  it("should validate number", () => {
    const result = validateInput("42.5", "number");
    expect(result.isValid).toBe(true);
  });

  it("should validate alphanumeric", () => {
    const result = validateInput("Test123", "alphanumeric");
    expect(result.isValid).toBe(true);
  });

  it("should validate 2FA code", () => {
    const result = validateInput("123456", "twoFactorCode");
    expect(result.isValid).toBe(true);
  });

  it("should validate URL", () => {
    const result = validateInput("https://sahool.app", "url");
    expect(result.isValid).toBe(true);
  });
});

describe("validateForm - comprehensive", () => {
  it("should validate complete registration form", () => {
    const inputs = {
      email: "farmer@sahool.app",
      phone: "+966501234567",
      password: "Str0ng!Pass123",
    };
    const rules = {
      email: "email" as const,
      phone: "phone" as const,
      password: "password" as const,
    };
    const results = validateForm(inputs, rules);
    expect(results.email.isValid).toBe(true);
    expect(results.phone.isValid).toBe(true);
    expect(results.password.isValid).toBe(true);
    expect(isFormValid(results)).toBe(true);
  });

  it("should detect invalid fields in form", () => {
    const inputs = {
      email: "invalid",
      phone: "123",
      password: "weak",
    };
    const rules = {
      email: "email" as const,
      phone: "phone" as const,
      password: "password" as const,
    };
    const results = validateForm(inputs, rules);
    expect(results.email.isValid).toBe(false);
    expect(results.phone.isValid).toBe(false);
    expect(results.password.isValid).toBe(false);
    expect(isFormValid(results)).toBe(false);
  });

  it("should handle empty form", () => {
    const results = validateForm({}, {});
    expect(isFormValid(results)).toBe(true);
  });

  it("should skip fields without matching rules", () => {
    const inputs = { email: "user@example.com", extra: "data" };
    const rules = { email: "email" as const };
    const results = validateForm(inputs, rules);
    expect(results.email).toBeDefined();
    expect(results.extra).toBeUndefined();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Security-Focused Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Security - SQL injection prevention in validators", () => {
  it("should reject SQL injection in email", () => {
    expect(validators.email("'; DROP TABLE users; --")).toBe(false);
  });

  it("should reject UNION SELECT in email", () => {
    expect(validators.email("user@example.com' UNION SELECT")).toBe(false);
  });

  it("should handle SQL in alphanumeric input", () => {
    expect(validators.alphanumeric("1; DROP TABLE")).toBe(false);
  });
});

describe("Security - prototype pollution prevention", () => {
  it("should handle __proto__ in input", () => {
    expect(validators.alphanumeric("__proto__")).toBe(false);
  });

  it("should handle constructor in input", () => {
    const result = sanitizers.alphanumeric("constructor");
    expect(result).toBe("constructor");
  });
});
