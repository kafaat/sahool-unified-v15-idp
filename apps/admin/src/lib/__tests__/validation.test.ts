/**
 * Validation Tests
 * اختبارات التحقق
 */

import { describe, it, expect } from "vitest";
import {
  validators,
  sanitizers,
  validationErrors,
  validateInput,
  validateForm,
  isFormValid,
} from "../validation";

describe("Validators", () => {
  describe("email", () => {
    it("accepts valid email", () => {
      expect(validators.email("admin@sahool.io")).toBe(true);
      expect(validators.email("user@example.com")).toBe(true);
      expect(validators.email("test+tag@mail.co.uk")).toBe(true);
    });

    it("rejects invalid email", () => {
      expect(validators.email("")).toBe(false);
      expect(validators.email("notanemail")).toBe(false);
      expect(validators.email("@missing.com")).toBe(false);
      expect(validators.email("missing@")).toBe(false);
      expect(validators.email(null as unknown as string)).toBe(false);
    });

    it("rejects email longer than 254 chars", () => {
      const longEmail = "a".repeat(250) + "@b.com";
      expect(validators.email(longEmail)).toBe(false);
    });
  });

  describe("phone", () => {
    it("accepts valid phone numbers", () => {
      expect(validators.phone("+967 1234567890")).toBe(true);
      expect(validators.phone("01234567890")).toBe(true);
      expect(validators.phone("+1-555-123-4567")).toBe(true);
    });

    it("rejects invalid phone numbers", () => {
      expect(validators.phone("")).toBe(false);
      expect(validators.phone("123")).toBe(false);
      expect(validators.phone(null as unknown as string)).toBe(false);
    });
  });

  describe("password", () => {
    it("accepts strong passwords", () => {
      expect(validators.password("SecureP@ss1")).toBe(true);
      expect(validators.password("MyStr0ng!Pass")).toBe(true);
    });

    it("rejects weak passwords", () => {
      expect(validators.password("")).toBe(false);
      expect(validators.password("short")).toBe(false);
      expect(validators.password("nouppercase1!")).toBe(false);
      expect(validators.password("NOLOWERCASE1!")).toBe(false);
      expect(validators.password("NoNumber!!")).toBe(false);
      expect(validators.password("NoSpecial1a")).toBe(false);
      expect(validators.password(null as unknown as string)).toBe(false);
    });
  });

  describe("twoFactorCode", () => {
    it("accepts valid 6-digit codes", () => {
      expect(validators.twoFactorCode("123456")).toBe(true);
      expect(validators.twoFactorCode("000000")).toBe(true);
      expect(validators.twoFactorCode(" 123456 ")).toBe(true);
    });

    it("rejects invalid codes", () => {
      expect(validators.twoFactorCode("")).toBe(false);
      expect(validators.twoFactorCode("12345")).toBe(false);
      expect(validators.twoFactorCode("1234567")).toBe(false);
      expect(validators.twoFactorCode("abcdef")).toBe(false);
      expect(validators.twoFactorCode(null as unknown as string)).toBe(false);
    });
  });

  describe("safeText", () => {
    it("accepts safe text", () => {
      expect(validators.safeText("Hello World")).toBe(true);
      expect(validators.safeText("مرحبا بالعالم")).toBe(true);
      expect(validators.safeText("Simple 123 text")).toBe(true);
    });

    it("rejects text with HTML tags", () => {
      expect(validators.safeText("<script>alert(1)</script>")).toBe(false);
      expect(validators.safeText("<img src=x onerror=alert(1)>")).toBe(false);
    });

    it("rejects text with dangerous protocols", () => {
      expect(validators.safeText("javascript:alert(1)")).toBe(false);
      expect(validators.safeText("vbscript:msgbox")).toBe(false);
      expect(validators.safeText("data:text/html")).toBe(false);
    });

    it("rejects event handlers", () => {
      expect(validators.safeText("onclick=alert(1)")).toBe(false);
      expect(validators.safeText("onerror=alert(1)")).toBe(false);
    });

    it("rejects encoded attacks", () => {
      expect(validators.safeText("&#x3C;script&#x3E;")).toBe(false);
      expect(validators.safeText("%3Cscript%3E")).toBe(false);
    });
  });

  describe("url", () => {
    it("accepts valid URLs", () => {
      expect(validators.url("https://sahool.io")).toBe(true);
      expect(validators.url("http://localhost:3000")).toBe(true);
    });

    it("rejects invalid URLs", () => {
      expect(validators.url("")).toBe(false);
      expect(validators.url("not-a-url")).toBe(false);
      expect(validators.url("ftp://files.com")).toBe(false);
      expect(validators.url("javascript:alert(1)")).toBe(false);
    });
  });

  describe("number", () => {
    it("accepts valid numbers", () => {
      expect(validators.number("123")).toBe(true);
      expect(validators.number("-42")).toBe(true);
      expect(validators.number("3.14")).toBe(true);
      expect(validators.number(42)).toBe(true);
    });

    it("rejects invalid numbers", () => {
      expect(validators.number("abc")).toBe(false);
      expect(validators.number(NaN)).toBe(false);
      expect(validators.number(Infinity)).toBe(false);
    });
  });

  describe("alphanumeric", () => {
    it("accepts alphanumeric strings", () => {
      expect(validators.alphanumeric("abc123")).toBe(true);
      expect(validators.alphanumeric("ABC")).toBe(true);
    });

    it("rejects non-alphanumeric strings", () => {
      expect(validators.alphanumeric("abc-123")).toBe(false);
      expect(validators.alphanumeric("abc 123")).toBe(false);
      expect(validators.alphanumeric("")).toBe(false);
    });
  });
});

describe("Sanitizers", () => {
  describe("html", () => {
    it("strips HTML tags", () => {
      const result = sanitizers.html("<b>bold</b>");
      expect(result).not.toContain("<b>");
      expect(result).toContain("bold");
    });

    it("returns empty string for non-string input", () => {
      expect(sanitizers.html("")).toBe("");
      expect(sanitizers.html(null as unknown as string)).toBe("");
    });
  });

  describe("email", () => {
    it("sanitizes email", () => {
      expect(sanitizers.email("  Admin@Sahool.IO  ")).toBe("admin@sahool.io");
    });

    it("returns empty for invalid input", () => {
      expect(sanitizers.email("")).toBe("");
    });
  });

  describe("phone", () => {
    it("keeps only phone characters", () => {
      expect(sanitizers.phone("+967-123 4567")).toBe("+967-123 4567");
      expect(sanitizers.phone("abc123")).toBe("123");
    });
  });

  describe("number", () => {
    it("keeps only numeric characters", () => {
      expect(sanitizers.number("$1,234.56")).toBe("1234.56");
    });
  });

  describe("alphanumeric", () => {
    it("removes non-alphanumeric characters", () => {
      expect(sanitizers.alphanumeric("abc-123!")).toBe("abc123");
    });
  });

  describe("filename", () => {
    it("sanitizes filenames", () => {
      expect(sanitizers.filename("../../../etc/passwd")).toBe("___etc_passwd");
      expect(sanitizers.filename("normal-file_v2.txt")).toBe(
        "normal-file_v2.txt",
      );
    });

    it("limits filename length", () => {
      const longName = "a".repeat(300) + ".txt";
      expect(sanitizers.filename(longName).length).toBeLessThanOrEqual(255);
    });
  });

  describe("escape", () => {
    it("escapes HTML entities server-side", () => {
      // In test env, window is defined via jsdom, so we test client path
      const result = sanitizers.escape('<script>alert("xss")</script>');
      expect(result).not.toContain("<script>");
    });

    it("returns empty for invalid input", () => {
      expect(sanitizers.escape("")).toBe("");
    });
  });
});

describe("Validation Errors", () => {
  it("has Arabic error messages for all validators", () => {
    expect(validationErrors.email).toContain("بريد إلكتروني");
    expect(validationErrors.password).toContain("كلمة المرور");
    expect(validationErrors.required).toContain("مطلوب");
    expect(validationErrors.twoFactorCode).toContain("أرقام");
  });
});

describe("validateInput", () => {
  it("returns valid result for valid email", () => {
    const result = validateInput("admin@sahool.io", "email");
    expect(result.isValid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it("returns error for invalid email", () => {
    const result = validateInput("notvalid", "email");
    expect(result.isValid).toBe(false);
    expect(result.error).toBeDefined();
  });

  it("returns required error for empty input", () => {
    const result = validateInput("", "email");
    expect(result.isValid).toBe(false);
    expect(result.error).toBe(validationErrors.required);
  });
});

describe("validateForm", () => {
  it("validates multiple fields", () => {
    const results = validateForm(
      { email: "admin@sahool.io", password: "SecureP@ss1" },
      { email: "email", password: "password" },
    );

    expect(results.email?.isValid).toBe(true);
    expect(results.password?.isValid).toBe(true);
  });

  it("catches invalid fields", () => {
    const results = validateForm(
      { email: "bad", password: "weak" },
      { email: "email", password: "password" },
    );

    expect(results.email?.isValid).toBe(false);
    expect(results.password?.isValid).toBe(false);
  });
});

describe("isFormValid", () => {
  it("returns true when all fields valid", () => {
    const results = validateForm(
      { email: "admin@sahool.io" },
      { email: "email" },
    );
    expect(isFormValid(results)).toBe(true);
  });

  it("returns false when any field invalid", () => {
    const results = validateForm({ email: "bad" }, { email: "email" });
    expect(isFormValid(results)).toBe(false);
  });
});
