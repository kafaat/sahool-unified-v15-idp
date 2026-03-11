/**
 * SAHOOL Swagger/Docs Endpoint Restriction Tests
 * اختبارات تقييد الوصول إلى وثائق Swagger لمنصة سهول
 *
 * Validates that API documentation endpoints (/docs, /redoc, /openapi.json)
 * are properly restricted by environment:
 * - Production: /docs should return 404 (disabled)
 * - Development/Staging: /docs should be accessible
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════════
// Service Registry (matching health-endpoints.test.ts)
// ═══════════════════════════════════════════════════════════════════════════════

interface ServiceDefinition {
  name: string;
  port: number;
  type: "python" | "node";
  /** Python FastAPI services expose /docs by default; NestJS uses /api */
  docsPath: string;
  /** Alternative docs paths to check */
  altDocsPaths?: string[];
}

/**
 * Python (FastAPI) services expose Swagger UI at /docs and ReDoc at /redoc.
 * Node.js (NestJS) services typically expose Swagger at /api or /api/docs.
 */
const SERVICES: ServiceDefinition[] = [
  // Python FastAPI Services
  {
    name: "notification-service",
    port: 8110,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "billing-core",
    port: 8089,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "task-service",
    port: 8103,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "equipment-service",
    port: 8101,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "alert-service",
    port: 8113,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "audit-service",
    port: 8114,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "vegetation-analysis-service",
    port: 8090,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "crop-intelligence-service",
    port: 8095,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "indicators-service",
    port: 8091,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "weather-service",
    port: 8092,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "advisory-service",
    port: 8093,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "irrigation-smart",
    port: 8094,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "yolo26-vision-service",
    port: 8150,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "terrain-core-service",
    port: 8185,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "hydrology-service",
    port: 8165,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "leveling-optimizer-service",
    port: 8170,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "edge-orchestrator-service",
    port: 8180,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "ai-advisor",
    port: 8112,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "copilot-api",
    port: 8088,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "ws-gateway",
    port: 8081,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "inventory-service",
    port: 8116,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },
  {
    name: "crm-service",
    port: 8131,
    type: "python",
    docsPath: "/docs",
    altDocsPaths: ["/redoc", "/openapi.json"],
  },

  // Node.js NestJS Services
  {
    name: "field-management-service",
    port: 3000,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
  {
    name: "user-service",
    port: 3025,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
  {
    name: "marketplace-service",
    port: 3010,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
  {
    name: "chat-service",
    port: 8115,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
  {
    name: "crop-growth-model",
    port: 3023,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
  {
    name: "yield-prediction-service",
    port: 8152,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
  {
    name: "lai-estimation",
    port: 3022,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
  {
    name: "iot-service",
    port: 8117,
    type: "node",
    docsPath: "/api",
    altDocsPaths: ["/api/docs"],
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_HOST = process.env.SERVICE_HOST || "localhost";
const REQUEST_TIMEOUT_MS = 5000;

/**
 * The environment being tested. In CI or production testing, set
 * ENVIRONMENT=production to verify docs are disabled.
 */
const CURRENT_ENVIRONMENT = process.env.ENVIRONMENT || "development";

function getServiceUrl(service: ServiceDefinition): string {
  const envKey = service.name.toUpperCase().replace(/-/g, "_") + "_URL";
  return process.env[envKey] || `http://${BASE_HOST}:${service.port}`;
}

async function fetchWithTimeout(
  url: string,
  timeoutMs: number = REQUEST_TIMEOUT_MS
): Promise<{ status: number; contentType: string } | null> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { Accept: "text/html,application/json" },
    });
    clearTimeout(timeoutId);

    // Consume body to avoid leaks
    await response.text();

    return {
      status: response.status,
      contentType: response.headers.get("content-type") || "",
    };
  } catch (error) {
    clearTimeout(timeoutId);
    const message = error instanceof Error ? error.message : String(error);
    if (
      message.includes("fetch failed") ||
      message.includes("ECONNREFUSED") ||
      message.includes("ECONNRESET") ||
      message.includes("ENOTFOUND") ||
      message.includes("AbortError") ||
      message.includes("aborted")
    ) {
      return null; // Service not running
    }
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Swagger Restriction Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Swagger/Docs Restriction Tests - اختبارات تقييد التوثيق", () => {
  // ─────────────────────────────────────────────────────────────────────────────
  // Production Mode: /docs must be disabled
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Production mode - /docs should be disabled", () => {
    const isProduction = CURRENT_ENVIRONMENT === "production";

    for (const service of SERVICES) {
      const serviceUrl = getServiceUrl(service);

      describe(`${service.name} (port ${service.port})`, () => {
        it(`should return 404 for ${service.docsPath} in production`, async () => {
          if (!isProduction) {
            // When not testing production, verify the concept:
            // the test documents the expected behavior
            console.warn(
              `  [INFO] ENVIRONMENT=${CURRENT_ENVIRONMENT} - ` +
                `Set ENVIRONMENT=production to enforce this check. ` +
                `Verifying endpoint existence instead.`
            );

            const result = await fetchWithTimeout(
              `${serviceUrl}${service.docsPath}`
            );

            if (!result) {
              console.warn(`  [SKIP] ${service.name} not reachable`);
              return;
            }

            // In non-production, docs may or may not be available
            // We just verify the service is reachable
            expect([200, 301, 302, 404]).toContain(result.status);
            return;
          }

          // Production enforcement
          const result = await fetchWithTimeout(
            `${serviceUrl}${service.docsPath}`
          );

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          expect(result.status).toBe(404);
        });

        if (service.altDocsPaths) {
          for (const altPath of service.altDocsPaths) {
            it(`should return 404 for ${altPath} in production`, async () => {
              if (!isProduction) {
                console.warn(
                  `  [INFO] Skipping production-only check for ${altPath} ` +
                    `(ENVIRONMENT=${CURRENT_ENVIRONMENT})`
                );
                return;
              }

              const result = await fetchWithTimeout(
                `${serviceUrl}${altPath}`
              );

              if (!result) {
                console.warn(`  [SKIP] ${service.name} not reachable`);
                return;
              }

              expect(result.status).toBe(404);
            });
          }
        }
      });
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Development Mode: /docs should be accessible
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Development mode - /docs should be accessible", () => {
    const isDevelopment =
      CURRENT_ENVIRONMENT === "development" ||
      CURRENT_ENVIRONMENT === "test";

    for (const service of SERVICES) {
      const serviceUrl = getServiceUrl(service);

      describe(`${service.name} (port ${service.port})`, () => {
        it(`should serve ${service.docsPath} in development mode`, async () => {
          if (!isDevelopment) {
            console.warn(
              `  [INFO] Skipping dev-only check (ENVIRONMENT=${CURRENT_ENVIRONMENT})`
            );
            return;
          }

          const result = await fetchWithTimeout(
            `${serviceUrl}${service.docsPath}`
          );

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          // In development, docs should be accessible (200 or redirect)
          expect([200, 301, 302]).toContain(result.status);
        });

        if (service.type === "python") {
          it("should serve /openapi.json in development mode", async () => {
            if (!isDevelopment) {
              return;
            }

            const result = await fetchWithTimeout(
              `${serviceUrl}/openapi.json`
            );

            if (!result) {
              console.warn(`  [SKIP] ${service.name} not reachable`);
              return;
            }

            // OpenAPI spec should be accessible and return JSON
            if (result.status === 200) {
              expect(result.contentType).toContain("application/json");
            }
          });
        }
      });
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Swagger must NOT be exposed through Kong Gateway in production
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Kong Gateway - docs should not be proxied in production", () => {
    const kongUrl = process.env.KONG_URL || `http://${BASE_HOST}:8000`;
    const isProduction = CURRENT_ENVIRONMENT === "production";

    const gatewayDocsPaths = [
      "/docs",
      "/redoc",
      "/openapi.json",
      "/api/docs",
      "/api/v1/docs",
      "/swagger",
      "/swagger-ui",
      "/swagger.json",
    ];

    for (const docsPath of gatewayDocsPaths) {
      it(`should not expose ${docsPath} through Kong Gateway`, async () => {
        if (!isProduction) {
          console.warn(
            `  [INFO] Skipping Kong production check (ENVIRONMENT=${CURRENT_ENVIRONMENT})`
          );
          return;
        }

        const result = await fetchWithTimeout(`${kongUrl}${docsPath}`);

        if (!result) {
          console.warn("  [SKIP] Kong Gateway not reachable");
          return;
        }

        // In production, Kong should not proxy documentation endpoints
        // Expected: 404 (no route) or 403 (blocked)
        expect([403, 404]).toContain(result.status);
      });
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Docs accessibility should NOT require authentication
  // (when docs are enabled in development)
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Development docs - no auth required", () => {
    const isDevelopment =
      CURRENT_ENVIRONMENT === "development" ||
      CURRENT_ENVIRONMENT === "test";

    if (!isDevelopment) {
      it.skip("skipped - not in development mode", () => {});
      return;
    }

    for (const service of SERVICES) {
      const serviceUrl = getServiceUrl(service);

      it(`${service.name} docs should not require auth`, async () => {
        const result = await fetchWithTimeout(
          `${serviceUrl}${service.docsPath}`
        );

        if (!result) {
          console.warn(`  [SKIP] ${service.name} not reachable`);
          return;
        }

        // Docs should be accessible without auth (not 401 or 403)
        if (result.status !== 404) {
          expect(result.status).not.toBe(401);
          expect(result.status).not.toBe(403);
        }
      });
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Summary Report
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Swagger restriction summary", () => {
    it("should report docs accessibility across all services", async () => {
      const results: Array<{
        name: string;
        port: number;
        type: string;
        docsPath: string;
        reachable: boolean;
        docsStatus: number | null;
      }> = [];

      for (const service of SERVICES) {
        const serviceUrl = getServiceUrl(service);
        const result = await fetchWithTimeout(
          `${serviceUrl}${service.docsPath}`
        );

        results.push({
          name: service.name,
          port: service.port,
          type: service.type,
          docsPath: service.docsPath,
          reachable: result !== null,
          docsStatus: result?.status ?? null,
        });
      }

      const reachable = results.filter((r) => r.reachable);
      const docsAccessible = reachable.filter((r) => r.docsStatus === 200);
      const docsBlocked = reachable.filter((r) => r.docsStatus === 404);

      console.log("\n=== Swagger/Docs Restriction Summary ===");
      console.log(`Environment: ${CURRENT_ENVIRONMENT}`);
      console.log(`Total services: ${SERVICES.length}`);
      console.log(`Reachable: ${reachable.length}`);
      console.log(`Docs accessible (200): ${docsAccessible.length}`);
      console.log(`Docs blocked (404): ${docsBlocked.length}`);
      console.log("========================================\n");

      for (const r of results) {
        const status = !r.reachable
          ? "UNREACHABLE"
          : r.docsStatus === 200
            ? "EXPOSED"
            : r.docsStatus === 404
              ? "BLOCKED"
              : `HTTP ${r.docsStatus}`;
        console.log(
          `  ${status.padEnd(14)} ${r.name.padEnd(35)} :${r.port} ${r.docsPath}`
        );
      }

      // In production, no docs should be exposed
      if (CURRENT_ENVIRONMENT === "production") {
        expect(docsAccessible).toHaveLength(0);
      }

      expect(results.length).toBe(SERVICES.length);
    });
  });
});
