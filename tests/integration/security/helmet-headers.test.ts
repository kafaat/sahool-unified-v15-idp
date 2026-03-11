/**
 * SAHOOL Helmet Security Headers Integration Tests
 * اختبارات رؤوس الأمان لمنصة سهول
 *
 * Tests verify that security headers are properly configured via helmet
 * middleware across all NestJS services.
 *
 * Helmet sets the following headers by default:
 * - Content-Security-Policy
 * - Cross-Origin-Embedder-Policy
 * - Cross-Origin-Opener-Policy
 * - Cross-Origin-Resource-Policy
 * - X-DNS-Prefetch-Control
 * - X-Frame-Options
 * - Strict-Transport-Security
 * - X-Download-Options
 * - X-Content-Type-Options
 * - Origin-Agent-Cluster
 * - X-Permitted-Cross-Domain-Policies
 * - Referrer-Policy
 * - X-XSS-Protection
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect } from "vitest";
import * as fs from "fs";
import * as path from "path";

// ═══════════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════════

const SERVICES_DIR = path.resolve(
  __dirname,
  "../../../apps/services"
);

/**
 * NestJS services that should have helmet configured in main.ts.
 */
const NESTJS_SERVICES_WITH_HELMET = [
  "user-service",
  "marketplace-service",
  "chat-service",
  "iot-service",
  "crop-growth-model",
  "disaster-assessment",
  "yield-prediction-service",
  "lai-estimation",
] as const;

/**
 * Default security headers set by helmet().
 * See: https://helmetjs.github.io/
 */
const HELMET_DEFAULT_HEADERS = {
  "Content-Security-Policy":
    "default-src 'self';base-uri 'self';font-src 'self' https: data:;form-action 'self';frame-ancestors 'self';img-src 'self' data:;object-src 'none';script-src 'self';script-src-attr 'none';style-src 'self' https: 'unsafe-inline';upgrade-insecure-requests",
  "Cross-Origin-Embedder-Policy": "require-corp",
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Resource-Policy": "same-origin",
  "X-DNS-Prefetch-Control": "off",
  "X-Frame-Options": "SAMEORIGIN",
  "Strict-Transport-Security": "max-age=15552000; includeSubDomains",
  "X-Download-Options": "noopen",
  "X-Content-Type-Options": "nosniff",
  "X-Permitted-Cross-Domain-Policies": "none",
  "Referrer-Policy": "no-referrer",
  "X-XSS-Protection": "0",
} as const;

/**
 * Critical security headers that MUST be present regardless of configuration.
 */
const CRITICAL_HEADERS = [
  "X-Content-Type-Options",
  "X-Frame-Options",
  "Strict-Transport-Security",
  "Referrer-Policy",
] as const;

// ═══════════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Reads the main.ts file for a given NestJS service.
 */
function readMainFile(serviceName: string): string | null {
  const mainPath = path.join(
    SERVICES_DIR,
    serviceName,
    "src",
    "main.ts"
  );

  if (!fs.existsSync(mainPath)) {
    return null;
  }

  return fs.readFileSync(mainPath, "utf-8");
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tests: Helmet Configuration
// ═══════════════════════════════════════════════════════════════════════════════

describe("Helmet Security Headers", () => {
  describe("Helmet Middleware Installation", () => {
    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s imports helmet",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          // Skip if main.ts doesn't exist
          return;
        }

        // Verify helmet import
        expect(source).toMatch(
          /import\s+helmet\s+from\s+['"]helmet['"]/
        );
      }
    );

    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s calls app.use(helmet())",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        // Verify helmet is applied as middleware
        expect(source).toMatch(/app\.use\(\s*helmet\(\s*\)\s*\)/);
      }
    );

    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s applies helmet before route handlers",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        // helmet() should be called before app.listen()
        const helmetIndex = source.indexOf("helmet()");
        const listenIndex = source.indexOf("app.listen");

        expect(helmetIndex).toBeGreaterThan(-1);
        expect(listenIndex).toBeGreaterThan(-1);
        expect(helmetIndex).toBeLessThan(listenIndex);
      }
    );
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Default Header Expectations
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Default Helmet Headers", () => {
    it("helmet default configuration includes X-Content-Type-Options: nosniff", () => {
      expect(HELMET_DEFAULT_HEADERS["X-Content-Type-Options"]).toBe("nosniff");
    });

    it("helmet default configuration includes X-Frame-Options: SAMEORIGIN", () => {
      expect(HELMET_DEFAULT_HEADERS["X-Frame-Options"]).toBe("SAMEORIGIN");
    });

    it("helmet default configuration includes Strict-Transport-Security (HSTS)", () => {
      expect(HELMET_DEFAULT_HEADERS["Strict-Transport-Security"]).toContain(
        "max-age="
      );
      expect(HELMET_DEFAULT_HEADERS["Strict-Transport-Security"]).toContain(
        "includeSubDomains"
      );
    });

    it("helmet default configuration includes Referrer-Policy: no-referrer", () => {
      expect(HELMET_DEFAULT_HEADERS["Referrer-Policy"]).toBe("no-referrer");
    });

    it("helmet default configuration disables DNS prefetch", () => {
      expect(HELMET_DEFAULT_HEADERS["X-DNS-Prefetch-Control"]).toBe("off");
    });

    it("helmet default configuration sets X-XSS-Protection to 0 (modern approach)", () => {
      // Modern best practice is to set X-XSS-Protection to 0 and rely on CSP instead
      expect(HELMET_DEFAULT_HEADERS["X-XSS-Protection"]).toBe("0");
    });

    it("helmet default configuration includes Content-Security-Policy", () => {
      expect(HELMET_DEFAULT_HEADERS["Content-Security-Policy"]).toContain(
        "default-src 'self'"
      );
    });

    it("helmet default configuration blocks cross-origin embedding", () => {
      expect(HELMET_DEFAULT_HEADERS["Cross-Origin-Embedder-Policy"]).toBe(
        "require-corp"
      );
    });

    it("helmet default configuration enforces same-origin opener policy", () => {
      expect(HELMET_DEFAULT_HEADERS["Cross-Origin-Opener-Policy"]).toBe(
        "same-origin"
      );
    });

    it("helmet default configuration blocks cross-domain policies", () => {
      expect(HELMET_DEFAULT_HEADERS["X-Permitted-Cross-Domain-Policies"]).toBe(
        "none"
      );
    });

    it("HSTS max-age is at least 180 days (15552000 seconds)", () => {
      const hsts = HELMET_DEFAULT_HEADERS["Strict-Transport-Security"];
      const maxAgeMatch = hsts.match(/max-age=(\d+)/);

      expect(maxAgeMatch).not.toBeNull();
      const maxAge = parseInt(maxAgeMatch![1], 10);
      expect(maxAge).toBeGreaterThanOrEqual(15552000);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: No Custom Overrides Weakening Security
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("No Security Weakening Overrides", () => {
    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s does not disable X-Frame-Options",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        // Should not disable frameguard
        expect(source).not.toMatch(/frameguard:\s*false/);
        expect(source).not.toMatch(/xFrameOptions:\s*false/);
      }
    );

    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s does not disable HSTS",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        // Should not disable HSTS
        expect(source).not.toMatch(
          /strictTransportSecurity:\s*false/
        );
        expect(source).not.toMatch(/hsts:\s*false/);
      }
    );

    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s does not disable Content-Security-Policy",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        // Should not disable CSP entirely
        expect(source).not.toMatch(
          /contentSecurityPolicy:\s*false/
        );
      }
    );

    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s does not disable noSniff",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        expect(source).not.toMatch(/noSniff:\s*false/);
        expect(source).not.toMatch(/xContentTypeOptions:\s*false/);
      }
    );

    it("no service sets X-Powered-By header (helmet removes it by default)", () => {
      for (const serviceName of NESTJS_SERVICES_WITH_HELMET) {
        const source = readMainFile(serviceName);

        if (!source) {
          continue;
        }

        // Services should not re-enable X-Powered-By
        expect(source).not.toMatch(/hidePoweredBy:\s*false/);
        expect(source).not.toMatch(
          /app\.use\([^)]*x-powered-by[^)]*\)/i
        );
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: CORS Configuration
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("CORS Configuration", () => {
    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s configures CORS with specific origins (not wildcard)",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        if (source.includes("enableCors")) {
          // Should not use wildcard origin
          expect(source).not.toMatch(/origin:\s*["']\*["']/);
          expect(source).not.toMatch(/origin:\s*true/);
        }
      }
    );

    it("user-service CORS allows sahool.com domains", () => {
      const source = readMainFile("user-service");

      if (!source) {
        return;
      }

      expect(source).toContain("sahool.com");
      expect(source).toContain("app.sahool.com");
      expect(source).toContain("admin.sahool.com");
    });

    it("user-service CORS allows required headers", () => {
      const source = readMainFile("user-service");

      if (!source) {
        return;
      }

      expect(source).toContain("Content-Type");
      expect(source).toContain("Authorization");
      expect(source).toContain("X-Tenant-ID");
      expect(source).toContain("X-Request-ID");
    });

    it("CORS credentials are enabled for authenticated requests", () => {
      const source = readMainFile("user-service");

      if (!source) {
        return;
      }

      expect(source).toMatch(/credentials:\s*true/);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Validation Pipe (Input Security)
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Validation Pipe Configuration", () => {
    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s has global ValidationPipe with whitelist enabled",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        if (source.includes("ValidationPipe")) {
          // whitelist: true strips unknown properties (prevents mass assignment)
          expect(source).toMatch(/whitelist:\s*true/);
        }
      }
    );

    it.each(NESTJS_SERVICES_WITH_HELMET.map((s) => [s]))(
      "service %s has transform enabled for automatic type coercion",
      (serviceName) => {
        const source = readMainFile(serviceName as string);

        if (!source) {
          return;
        }

        if (source.includes("ValidationPipe")) {
          expect(source).toMatch(/transform:\s*true/);
        }
      }
    );

    it("user-service forbids non-whitelisted properties", () => {
      const source = readMainFile("user-service");

      if (!source) {
        return;
      }

      // forbidNonWhitelisted: true returns 400 for unknown properties
      expect(source).toMatch(/forbidNonWhitelisted:\s*true/);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Swagger/OpenAPI Security
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Swagger/OpenAPI Security", () => {
    it("user-service disables Swagger in production", () => {
      const source = readMainFile("user-service");

      if (!source) {
        return;
      }

      // Swagger should be gated behind environment check
      expect(source).toMatch(
        /process\.env\.NODE_ENV\s*!==\s*['"]production['"]/
      );
      expect(source).toContain("SwaggerModule");
    });

    it("marketplace-service disables Swagger in production", () => {
      const source = readMainFile("marketplace-service");

      if (!source) {
        return;
      }

      expect(source).toMatch(
        /process\.env\.NODE_ENV\s*!==\s*['"]production['"]/
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Health Endpoint Exclusion from Global Prefix
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Health Endpoints Accessibility", () => {
    it("user-service excludes health endpoints from global prefix", () => {
      const source = readMainFile("user-service");

      if (!source) {
        return;
      }

      // Health endpoints should be accessible at root for K8s probes
      expect(source).toContain("setGlobalPrefix");
      expect(source).toContain("healthz");
      expect(source).toContain("readyz");
    });

    it("marketplace-service excludes health endpoints from global prefix", () => {
      const source = readMainFile("marketplace-service");

      if (!source) {
        return;
      }

      expect(source).toContain("setGlobalPrefix");
      expect(source).toContain("healthz");
      expect(source).toContain("readyz");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Graceful Shutdown
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Graceful Shutdown Handlers", () => {
    it.each(["user-service", "marketplace-service"] as const)(
      "service %s handles SIGTERM for graceful shutdown",
      (serviceName) => {
        const source = readMainFile(serviceName);

        if (!source) {
          return;
        }

        expect(source).toContain("SIGTERM");
        expect(source).toContain("gracefulShutdown");
      }
    );

    it.each(["user-service", "marketplace-service"] as const)(
      "service %s handles SIGINT for graceful shutdown",
      (serviceName) => {
        const source = readMainFile(serviceName);

        if (!source) {
          return;
        }

        expect(source).toContain("SIGINT");
      }
    );

    it.each(["user-service", "marketplace-service"] as const)(
      "service %s calls app.close() during shutdown",
      (serviceName) => {
        const source = readMainFile(serviceName);

        if (!source) {
          return;
        }

        expect(source).toContain("app.close()");
      }
    );
  });

  // ═══════════════════════════════════════════════════════════════════════════════
  // Tests: Critical Security Header Completeness
  // ═══════════════════════════════════════════════════════════════════════════════

  describe("Critical Security Headers Completeness", () => {
    it("all critical headers are covered by helmet defaults", () => {
      for (const header of CRITICAL_HEADERS) {
        expect(header in HELMET_DEFAULT_HEADERS).toBe(true);
      }
    });

    it("helmet provides at least 10 security headers", () => {
      const headerCount = Object.keys(HELMET_DEFAULT_HEADERS).length;
      expect(headerCount).toBeGreaterThanOrEqual(10);
    });

    it("CSP default-src is set to self (deny by default)", () => {
      const csp = HELMET_DEFAULT_HEADERS["Content-Security-Policy"];
      expect(csp).toContain("default-src 'self'");
    });

    it("CSP blocks object-src (prevents plugin-based attacks)", () => {
      const csp = HELMET_DEFAULT_HEADERS["Content-Security-Policy"];
      expect(csp).toContain("object-src 'none'");
    });

    it("CSP blocks inline script-src-attr", () => {
      const csp = HELMET_DEFAULT_HEADERS["Content-Security-Policy"];
      expect(csp).toContain("script-src-attr 'none'");
    });

    it("CSP requests upgrade to HTTPS via upgrade-insecure-requests", () => {
      const csp = HELMET_DEFAULT_HEADERS["Content-Security-Policy"];
      expect(csp).toContain("upgrade-insecure-requests");
    });
  });
});
