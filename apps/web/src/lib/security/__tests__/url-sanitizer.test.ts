/**
 * SAHOOL URL Sanitizer Tests
 * اختبارات التحقق من الروابط
 */

import { describe, it, expect } from "vitest";
import { sanitizeUrl, isUrlSafe, sanitizeUrlForNavigation } from "../url-sanitizer";

describe("URL Sanitizer", () => {
  describe("sanitizeUrl", () => {
    describe("blocks dangerous protocols", () => {
      it("should block javascript: protocol", () => {
        expect(sanitizeUrl("javascript:alert(1)")).toBeNull();
        expect(sanitizeUrl("javascript:void(0)")).toBeNull();
        expect(sanitizeUrl("javascript:document.cookie")).toBeNull();
      });

      it("should block javascript: with various encodings", () => {
        expect(sanitizeUrl("JAVASCRIPT:alert(1)")).toBeNull();
        expect(sanitizeUrl("JavaScript:alert(1)")).toBeNull();
        expect(sanitizeUrl("  javascript:alert(1)")).toBeNull();
        expect(sanitizeUrl("\tjavascript:alert(1)")).toBeNull();
        expect(sanitizeUrl("\njavascript:alert(1)")).toBeNull();
      });

      it("should block vbscript: protocol", () => {
        expect(sanitizeUrl("vbscript:msgbox(1)")).toBeNull();
        expect(sanitizeUrl("VBSCRIPT:msgbox(1)")).toBeNull();
      });

      it("should block data: protocol", () => {
        expect(sanitizeUrl("data:text/html,<script>alert(1)</script>")).toBeNull();
        expect(sanitizeUrl("data:text/javascript,alert(1)")).toBeNull();
        expect(sanitizeUrl("DATA:text/html,test")).toBeNull();
      });

      it("should block blob: protocol", () => {
        expect(sanitizeUrl("blob:https://example.com/uuid")).toBeNull();
        expect(sanitizeUrl("BLOB:https://example.com/uuid")).toBeNull();
      });

      it("should block file: protocol", () => {
        expect(sanitizeUrl("file:///etc/passwd")).toBeNull();
        expect(sanitizeUrl("FILE:///etc/passwd")).toBeNull();
      });
    });

    describe("allows safe URLs", () => {
      it("should allow https: URLs", () => {
        expect(sanitizeUrl("https://example.com")).toBe("https://example.com");
        expect(sanitizeUrl("https://example.com/path")).toBe("https://example.com/path");
        expect(sanitizeUrl("https://example.com/path?query=1")).toBe("https://example.com/path?query=1");
      });

      it("should allow http: URLs", () => {
        expect(sanitizeUrl("http://example.com")).toBe("http://example.com");
        expect(sanitizeUrl("http://localhost:3000")).toBe("http://localhost:3000");
      });

      it("should allow relative URLs starting with /", () => {
        expect(sanitizeUrl("/dashboard")).toBe("/dashboard");
        expect(sanitizeUrl("/fields/123")).toBe("/fields/123");
        expect(sanitizeUrl("/api/v1/alerts")).toBe("/api/v1/alerts");
      });

      it("should allow relative URLs starting with ./", () => {
        expect(sanitizeUrl("./page.html")).toBe("./page.html");
        expect(sanitizeUrl("./assets/image.png")).toBe("./assets/image.png");
      });

      it("should allow protocol-relative URLs", () => {
        expect(sanitizeUrl("//example.com/path")).toBe("//example.com/path");
      });

      it("should allow mailto: links", () => {
        expect(sanitizeUrl("mailto:support@sahool.com")).toBe("mailto:support@sahool.com");
      });

      it("should allow tel: links", () => {
        expect(sanitizeUrl("tel:+966123456789")).toBe("tel:+966123456789");
      });

      it("should allow plain relative paths", () => {
        expect(sanitizeUrl("page.html")).toBe("page.html");
        expect(sanitizeUrl("path/to/page")).toBe("path/to/page");
      });
    });

    describe("handles edge cases", () => {
      it("should return null for empty strings", () => {
        expect(sanitizeUrl("")).toBeNull();
        expect(sanitizeUrl("   ")).toBeNull();
      });

      it("should return null for null/undefined", () => {
        expect(sanitizeUrl(null)).toBeNull();
        expect(sanitizeUrl(undefined)).toBeNull();
      });

      it("should trim whitespace from valid URLs", () => {
        expect(sanitizeUrl("  https://example.com  ")).toBe("https://example.com");
        expect(sanitizeUrl("  /dashboard  ")).toBe("/dashboard");
      });

      it("should block unknown protocols", () => {
        expect(sanitizeUrl("ftp://example.com")).toBeNull();
        expect(sanitizeUrl("custom://app/path")).toBeNull();
      });

      it("should preserve original URL case for valid URLs", () => {
        expect(sanitizeUrl("https://Example.COM/Path")).toBe("https://Example.COM/Path");
        expect(sanitizeUrl("/Dashboard/Fields")).toBe("/Dashboard/Fields");
      });
    });

    describe("defense in depth - embedded protocols", () => {
      it("should block javascript: in query parameters", () => {
        expect(sanitizeUrl("https://evil.com?redirect=javascript:alert(1)")).toBeNull();
      });

      it("should block javascript: in fragments", () => {
        expect(sanitizeUrl("https://evil.com#javascript:alert(1)")).toBeNull();
      });
    });
  });

  describe("isUrlSafe", () => {
    it("should return true for safe URLs", () => {
      expect(isUrlSafe("https://example.com")).toBe(true);
      expect(isUrlSafe("/dashboard")).toBe(true);
    });

    it("should return false for dangerous URLs", () => {
      expect(isUrlSafe("javascript:alert(1)")).toBe(false);
      expect(isUrlSafe("data:text/html,test")).toBe(false);
    });

    it("should return false for empty/null values", () => {
      expect(isUrlSafe("")).toBe(false);
      expect(isUrlSafe(null)).toBe(false);
      expect(isUrlSafe(undefined)).toBe(false);
    });
  });

  describe("sanitizeUrlForNavigation", () => {
    it("should return safe URL when valid", () => {
      expect(sanitizeUrlForNavigation("https://example.com")).toBe("https://example.com");
    });

    it("should return null for dangerous URLs when no fallback", () => {
      expect(sanitizeUrlForNavigation("javascript:alert(1)")).toBeNull();
    });

    it("should return fallback for dangerous URLs", () => {
      expect(sanitizeUrlForNavigation("javascript:alert(1)", "/dashboard")).toBe("/dashboard");
    });

    it("should return fallback for empty URLs", () => {
      expect(sanitizeUrlForNavigation("", "/home")).toBe("/home");
      expect(sanitizeUrlForNavigation(null, "/home")).toBe("/home");
    });
  });
});
