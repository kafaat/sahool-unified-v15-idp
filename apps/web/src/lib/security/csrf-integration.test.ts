/**
 * CSRF Integration Tests
 * اختبارات تكامل CSRF
 *
 * Tests the integration between security library and API client for CSRF protection
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { getCsrfToken, getCsrfHeaders } from "./security";

describe("CSRF Integration", () => {
  beforeEach(() => {
    // Reset document.cookie
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "",
    });
  });

  describe("getCsrfToken", () => {
    it("should return null when no CSRF cookie exists", () => {
      const token = getCsrfToken();
      expect(token).toBeNull();
    });

    it("should extract CSRF token from cookie", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=test-token-123; other=value",
      });

      const token = getCsrfToken();
      expect(token).toBe("test-token-123");
    });

    it("should handle cookies with spaces", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "session=abc; csrf_token=my-csrf-token; expires=...",
      });

      const token = getCsrfToken();
      expect(token).toBe("my-csrf-token");
    });

    it("should handle cookie with just the CSRF token", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=only-token",
      });

      const token = getCsrfToken();
      expect(token).toBe("only-token");
    });
  });

  describe("getCsrfHeaders", () => {
    it("should return empty object when no token exists", () => {
      const headers = getCsrfHeaders();
      expect(headers).toEqual({});
    });

    it("should return headers with CSRF token", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=my-token-abc123",
      });

      const headers = getCsrfHeaders();
      expect(headers).toEqual({
        "X-CSRF-Token": "my-token-abc123",
      });
    });

    it("should use correct header name", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=test",
      });

      const headers = getCsrfHeaders();
      expect(headers).toHaveProperty("X-CSRF-Token");
      expect(headers["X-CSRF-Token"]).toBe("test");
    });

    it("should return empty object when CSRF is disabled", async () => {
      // Import and configure security
      const { configureSecurity, getCsrfHeaders: getHeaders } =
        await import("./security");

      // Set cookie
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=test-token",
      });

      // Disable CSRF
      configureSecurity({ csrfEnabled: false });

      // Should return empty headers
      const headers = getHeaders();
      expect(headers).toEqual({});

      // Re-enable for other tests
      configureSecurity({ csrfEnabled: true });
    });
  });

  describe("CSRF Token Format", () => {
    it("should handle base64url encoded tokens", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=abc123DEF456-_",
      });

      const token = getCsrfToken();
      expect(token).toBe("abc123DEF456-_");
      expect(token).toMatch(/^[A-Za-z0-9_-]+$/);
    });

    it("should handle long tokens (256+ characters)", () => {
      const longToken = "a".repeat(300);
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: `csrf_token=${longToken}`,
      });

      const token = getCsrfToken();
      expect(token).toBe(longToken);
      expect(token?.length).toBeGreaterThan(256);
    });
  });

  describe("Edge Cases", () => {
    it("should handle malformed cookies", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=",
      });

      const token = getCsrfToken();
      expect(token).toBeNull();
    });

    it("should handle cookies without value", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token",
      });

      const token = getCsrfToken();
      // Should return null or handle gracefully
      expect(token === null || token === "").toBe(true);
    });

    it("should handle multiple cookies with similar names", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "not_csrf_token=fake; csrf_token=real; csrf_token_old=old",
      });

      const token = getCsrfToken();
      expect(token).toBe("real");
    });
  });

  describe("Security Requirements", () => {
    it("should not expose token in XSS-vulnerable ways", () => {
      // Token should only be in cookie, not in localStorage or sessionStorage
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=secret-token",
      });

      const token = getCsrfToken();

      // Should be able to read from cookie
      expect(token).toBe("secret-token");

      // Should NOT be in localStorage (if available)
      if (typeof localStorage !== "undefined") {
        const lsToken = localStorage.getItem("csrf_token");
        expect(lsToken === null || lsToken === undefined).toBe(true);
      }

      // Should NOT be in sessionStorage (if available)
      if (typeof sessionStorage !== "undefined") {
        const ssToken = sessionStorage.getItem("csrf_token");
        expect(ssToken === null || ssToken === undefined).toBe(true);
      }
    });

    it("should return headers suitable for fetch API", () => {
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=valid-token",
      });

      const headers = getCsrfHeaders();

      // Should be an object that can be spread into fetch headers
      const fetchHeaders = new Headers({
        "Content-Type": "application/json",
        ...headers,
      });

      expect(fetchHeaders.get("X-CSRF-Token")).toBe("valid-token");
      expect(fetchHeaders.get("Content-Type")).toBe("application/json");
    });

    it("should work with SameSite cookies", () => {
      // SameSite cookies should still be readable by JavaScript
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=samesite-token",
      });

      const token = getCsrfToken();
      expect(token).toBe("samesite-token");
    });
  });

  describe("Configuration", () => {
    it("should use custom cookie name when configured", async () => {
      const { configureSecurity, getCsrfToken: getToken } =
        await import("./security");

      // Configure custom cookie name
      configureSecurity({ csrfCookieName: "my_custom_csrf" });

      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "my_custom_csrf=custom-token",
      });

      const token = getToken();
      expect(token).toBe("custom-token");

      // Reset to default
      configureSecurity({ csrfCookieName: "csrf_token" });
    });

    it("should use custom header name when configured", async () => {
      const { configureSecurity, getCsrfHeaders: getHeaders } =
        await import("./security");

      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "csrf_token=test-token",
      });

      // Configure custom header name
      configureSecurity({ csrfTokenHeader: "X-Custom-CSRF" });

      const headers = getHeaders();
      expect(headers["X-Custom-CSRF"]).toBe("test-token");

      // Reset to default
      configureSecurity({ csrfTokenHeader: "X-CSRF-Token" });
    });
  });
});
