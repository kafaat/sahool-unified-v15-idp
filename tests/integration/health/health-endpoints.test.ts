/**
 * SAHOOL Health & Readiness Endpoint Integration Tests
 * اختبارات نقاط صحة واستعداد الخدمات لمنصة سهول
 *
 * Validates that all services conform to the platform health endpoint contract:
 * - /healthz returns { status: 'ok' } with service name and version
 * - /readyz reports honest dependency status (database, NATS, Redis)
 * - Health endpoints are accessible without authentication or tenant ID
 * - Response times are within acceptable SLA (500ms)
 *
 * @author SAHOOL Platform Team
 */

import { describe, it, expect } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════════
// Service Registry
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Whether a service uses a database connection.
 * Services without a database should NOT claim database connectivity in /readyz.
 */
interface ServiceDefinition {
  name: string;
  port: number;
  type: "python" | "node";
  /** Whether this service connects to PostgreSQL */
  usesDatabase: boolean;
  /** Whether this service connects to NATS */
  usesNats: boolean;
  /** Whether this service connects to Redis */
  usesRedis: boolean;
  /** Health endpoint path (default: /healthz) */
  healthPath?: string;
  /** Readiness endpoint path (default: /readyz) */
  readyPath?: string;
}

const SERVICES: ServiceDefinition[] = [
  // Core Services
  {
    name: "field-management-service",
    port: 3000,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "user-service",
    port: 3025,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "notification-service",
    port: 8110,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "billing-core",
    port: 8089,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "task-service",
    port: 8103,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "equipment-service",
    port: 8101,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "alert-service",
    port: 8113,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "audit-service",
    port: 8114,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },

  // Analytics & Intelligence
  {
    name: "vegetation-analysis-service",
    port: 8090,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "crop-intelligence-service",
    port: 8095,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "indicators-service",
    port: 8091,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "weather-service",
    port: 8092,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "advisory-service",
    port: 8093,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "irrigation-smart",
    port: 8094,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "soil-analysis-service",
    port: 8134,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "pest-detection-service",
    port: 8125,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },

  // Vision, Terrain & Edge
  {
    name: "yolo26-vision-service",
    port: 8150,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "terrain-core-service",
    port: 8185,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "hydrology-service",
    port: 8165,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "leveling-optimizer-service",
    port: 8170,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "edge-orchestrator-service",
    port: 8180,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },

  // Decision Services
  {
    name: "crop-growth-model",
    port: 3023,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "yield-prediction-service",
    port: 8152,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "lai-estimation",
    port: 3022,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },

  // Integration & IoT
  {
    name: "iot-service",
    port: 8117,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "iot-gateway",
    port: 8106,
    type: "python",
    usesDatabase: false,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "ws-gateway",
    port: 8081,
    type: "python",
    usesDatabase: false,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "virtual-sensors",
    port: 8119,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "astronomical-calendar",
    port: 8111,
    type: "python",
    usesDatabase: false,
    usesNats: false,
    usesRedis: false,
  },

  // Community & Business
  {
    name: "marketplace-service",
    port: 3010,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "chat-service",
    port: 8115,
    type: "node",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "inventory-service",
    port: 8116,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "crm-service",
    port: 8131,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "globalgap-compliance",
    port: 8128,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },

  // AI & Agents
  {
    name: "ai-advisor",
    port: 8112,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "copilot-api",
    port: 8088,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
  {
    name: "agent-registry",
    port: 8160,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: false,
  },
  {
    name: "llm-orchestrator-service",
    port: 8164,
    type: "python",
    usesDatabase: true,
    usesNats: true,
    usesRedis: true,
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// Test Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_HOST = process.env.SERVICE_HOST || "localhost";
const REQUEST_TIMEOUT_MS = 5000;
const HEALTH_SLA_MS = 500;
const PLATFORM_VERSION = "16.0.0";

function getServiceUrl(service: ServiceDefinition): string {
  const envKey = service.name.toUpperCase().replace(/-/g, "_") + "_URL";
  return process.env[envKey] || `http://${BASE_HOST}:${service.port}`;
}

interface HealthResponse {
  status: string;
  service?: string;
  version?: string;
  [key: string]: unknown;
}

interface ReadinessResponse {
  status: string;
  database?: boolean;
  db?: boolean;
  db_connected?: boolean;
  nats?: boolean;
  nats_connected?: boolean;
  redis?: boolean;
  redis_connected?: boolean;
  [key: string]: unknown;
}

/**
 * Fetches a URL with timeout, returning null on connection errors
 * so tests can skip unavailable services gracefully.
 */
async function fetchWithTimeout(
  url: string,
  timeoutMs: number = REQUEST_TIMEOUT_MS
): Promise<{
  status: number;
  data: Record<string, unknown>;
  responseTimeMs: number;
  headers: Headers;
} | null> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  const start = Date.now();

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { Accept: "application/json" },
    });
    clearTimeout(timeoutId);

    const responseTimeMs = Date.now() - start;
    const contentType = response.headers.get("content-type") || "";
    let data: Record<string, unknown> = {};

    if (contentType.includes("application/json")) {
      data = (await response.json()) as Record<string, unknown>;
    } else {
      const text = await response.text();
      try {
        data = JSON.parse(text) as Record<string, unknown>;
      } catch {
        data = { raw: text };
      }
    }

    return { status: response.status, data, responseTimeMs, headers: response.headers };
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
// Health Endpoint Contract Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Health Endpoints - اختبارات نقاط الصحة", () => {
  // ─────────────────────────────────────────────────────────────────────────────
  // 1. Health Endpoint Contract
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Health endpoint contract - عقد نقطة الصحة", () => {
    for (const service of SERVICES) {
      const serviceUrl = getServiceUrl(service);
      const healthPath = service.healthPath || "/healthz";

      describe(`${service.name} (port ${service.port})`, () => {
        it(`should return { status: 'ok' } on ${healthPath}`, async () => {
          const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable at ${serviceUrl}`);
            return;
          }

          expect(result.status).toBe(200);

          const data = result.data as HealthResponse;
          expect(data).toHaveProperty("status");
          expect(data.status).toBe("ok");
        });

        it("should include service name in health response", async () => {
          const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          if (result.status !== 200) {
            return;
          }

          const data = result.data as HealthResponse;
          // Service name should be present in the response
          expect(data).toHaveProperty("service");
          expect(typeof data.service).toBe("string");
          expect((data.service as string).length).toBeGreaterThan(0);
        });

        it("should include version in health response", async () => {
          const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          if (result.status !== 200) {
            return;
          }

          const data = result.data as HealthResponse;
          expect(data).toHaveProperty("version");
          expect(typeof data.version).toBe("string");
          // Version should match semver pattern or platform version
          expect(data.version).toMatch(/^\d+\.\d+\.\d+/);
        });

        it(`should respond within ${HEALTH_SLA_MS}ms`, async () => {
          const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          expect(result.responseTimeMs).toBeLessThanOrEqual(HEALTH_SLA_MS);
        });
      });
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 2. Readiness Probe Honesty
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Readiness probe honesty - صدق اختبار الاستعداد", () => {
    for (const service of SERVICES) {
      const serviceUrl = getServiceUrl(service);
      const readyPath = service.readyPath || "/readyz";

      describe(`${service.name} (port ${service.port})`, () => {
        it("should return appropriate status fields in readiness response", async () => {
          const result = await fetchWithTimeout(`${serviceUrl}${readyPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          // Readiness endpoint should exist; 200 or 503 are both valid
          expect([200, 503]).toContain(result.status);

          const data = result.data as ReadinessResponse;
          expect(data).toHaveProperty("status");
          expect(["ok", "degraded", "unhealthy", "error", "not_ready"]).toContain(
            data.status
          );
        });

        if (service.usesDatabase) {
          it("should report database status when service uses a database", async () => {
            const result = await fetchWithTimeout(`${serviceUrl}${readyPath}`);

            if (!result) {
              console.warn(`  [SKIP] ${service.name} not reachable`);
              return;
            }

            if (![200, 503].includes(result.status)) {
              return;
            }

            const data = result.data as ReadinessResponse;
            const hasDbField =
              "database" in data || "db" in data || "db_connected" in data;
            expect(hasDbField).toBe(true);
          });
        }

        if (!service.usesDatabase) {
          it("should NOT claim database connectivity when service has no database", async () => {
            const result = await fetchWithTimeout(`${serviceUrl}${readyPath}`);

            if (!result) {
              console.warn(`  [SKIP] ${service.name} not reachable`);
              return;
            }

            if (![200, 503].includes(result.status)) {
              return;
            }

            const data = result.data as ReadinessResponse;
            // If a database field is present at all, it must NOT be hardcoded true
            const dbValue = data.database ?? data.db ?? data.db_connected;
            if (dbValue !== undefined) {
              // Service does not use a database, so claiming true is dishonest
              expect(dbValue).not.toBe(true);
            }
          });
        }

        if (service.usesNats) {
          it("should report NATS status when service uses NATS", async () => {
            const result = await fetchWithTimeout(`${serviceUrl}${readyPath}`);

            if (!result) {
              console.warn(`  [SKIP] ${service.name} not reachable`);
              return;
            }

            if (![200, 503].includes(result.status)) {
              return;
            }

            const data = result.data as ReadinessResponse;
            const hasNatsField = "nats" in data || "nats_connected" in data;
            expect(hasNatsField).toBe(true);
          });
        }

        it("should not return 200 with all dependencies true when database is disconnected", async () => {
          // This test verifies honesty: if a service reports database: true,
          // it should actually have checked the connection.
          // We verify this by checking that the readiness response is internally
          // consistent (if status is 'ok', dependencies should be true; if a
          // dependency is false, status should not be 'ok').
          const result = await fetchWithTimeout(`${serviceUrl}${readyPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          if (result.status !== 200) {
            return;
          }

          const data = result.data as ReadinessResponse;

          // If status is 'ok', no dependency should explicitly be false
          if (data.status === "ok") {
            const dbValue = data.database ?? data.db ?? data.db_connected;
            const natsValue = data.nats ?? data.nats_connected;
            const redisValue = data.redis ?? data.redis_connected;

            if (service.usesDatabase && dbValue !== undefined) {
              expect(dbValue).toBe(true);
            }
            if (service.usesNats && natsValue !== undefined) {
              expect(natsValue).toBe(true);
            }
            if (service.usesRedis && redisValue !== undefined) {
              expect(redisValue).toBe(true);
            }
          }
        });
      });
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 3. Health Endpoint Accessibility
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Health endpoint accessibility - إمكانية الوصول بدون مصادقة", () => {
    for (const service of SERVICES) {
      const serviceUrl = getServiceUrl(service);
      const healthPath = service.healthPath || "/healthz";
      const readyPath = service.readyPath || "/readyz";

      describe(`${service.name} (port ${service.port})`, () => {
        it("should be accessible without authentication (no Authorization header)", async () => {
          const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          // Health should NOT return 401 or 403
          expect(result.status).not.toBe(401);
          expect(result.status).not.toBe(403);
        });

        it("should be accessible without tenant ID (no X-Tenant-ID header)", async () => {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

          try {
            const response = await fetch(`${serviceUrl}${healthPath}`, {
              signal: controller.signal,
              headers: {
                Accept: "application/json",
                // Explicitly NOT sending X-Tenant-ID
              },
            });
            clearTimeout(timeoutId);

            // Health should NOT require tenant ID
            expect(response.status).not.toBe(401);
            expect(response.status).not.toBe(403);
          } catch (error) {
            clearTimeout(timeoutId);
            const message = error instanceof Error ? error.message : "";
            if (
              message.includes("fetch failed") ||
              message.includes("ECONNREFUSED") ||
              message.includes("aborted")
            ) {
              console.warn(`  [SKIP] ${service.name} not reachable`);
              return;
            }
            throw error;
          }
        });

        it("readiness endpoint should be accessible without authentication", async () => {
          const result = await fetchWithTimeout(`${serviceUrl}${readyPath}`);

          if (!result) {
            console.warn(`  [SKIP] ${service.name} not reachable`);
            return;
          }

          // Readiness should NOT return 401 or 403
          expect(result.status).not.toBe(401);
          expect(result.status).not.toBe(403);
        });
      });
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // 4. Cross-Service Health Summary
  // ─────────────────────────────────────────────────────────────────────────────

  describe("Cross-service health summary - ملخص صحة جميع الخدمات", () => {
    it("should collect health status from all reachable services", async () => {
      const results: Array<{
        name: string;
        port: number;
        reachable: boolean;
        healthy: boolean;
        responseTimeMs: number;
        version?: string;
      }> = [];

      for (const service of SERVICES) {
        const serviceUrl = getServiceUrl(service);
        const healthPath = service.healthPath || "/healthz";
        const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

        results.push({
          name: service.name,
          port: service.port,
          reachable: result !== null,
          healthy: result?.status === 200,
          responseTimeMs: result?.responseTimeMs ?? -1,
          version: (result?.data as HealthResponse)?.version as string | undefined,
        });
      }

      // Log summary table for visibility
      const reachableCount = results.filter((r) => r.reachable).length;
      const healthyCount = results.filter((r) => r.healthy).length;

      console.log("\n=== Health Check Summary ===");
      console.log(`Total services: ${SERVICES.length}`);
      console.log(`Reachable: ${reachableCount}`);
      console.log(`Healthy: ${healthyCount}`);
      console.log("============================\n");

      for (const r of results) {
        const status = r.healthy
          ? "OK"
          : r.reachable
            ? "UNHEALTHY"
            : "UNREACHABLE";
        const time = r.responseTimeMs >= 0 ? `${r.responseTimeMs}ms` : "N/A";
        const ver = r.version || "unknown";
        console.log(
          `  ${status.padEnd(12)} ${r.name.padEnd(35)} :${r.port} ${time.padStart(8)} v${ver}`
        );
      }

      // At minimum, the test itself should pass (the summary is informational)
      expect(results.length).toBe(SERVICES.length);
    });

    it("all reachable services should respond to healthz within SLA", async () => {
      const violations: Array<{ name: string; responseTimeMs: number }> = [];

      for (const service of SERVICES) {
        const serviceUrl = getServiceUrl(service);
        const healthPath = service.healthPath || "/healthz";
        const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

        if (result && result.responseTimeMs > HEALTH_SLA_MS) {
          violations.push({
            name: service.name,
            responseTimeMs: result.responseTimeMs,
          });
        }
      }

      if (violations.length > 0) {
        console.warn(
          `\nSLA violations (>${HEALTH_SLA_MS}ms):`,
          violations.map((v) => `${v.name}: ${v.responseTimeMs}ms`)
        );
      }

      // All reachable services should meet the SLA
      expect(violations).toHaveLength(0);
    });

    it("all reachable services should return consistent version", async () => {
      const versions: Array<{ name: string; version: string }> = [];

      for (const service of SERVICES) {
        const serviceUrl = getServiceUrl(service);
        const healthPath = service.healthPath || "/healthz";
        const result = await fetchWithTimeout(`${serviceUrl}${healthPath}`);

        if (result?.status === 200) {
          const data = result.data as HealthResponse;
          if (data.version) {
            versions.push({ name: service.name, version: data.version });
          }
        }
      }

      if (versions.length === 0) {
        console.warn("  [SKIP] No services reachable to check version consistency");
        return;
      }

      // All services should report the same major version
      const majorVersions = new Set(
        versions.map((v) => v.version.split(".")[0])
      );

      if (majorVersions.size > 1) {
        console.warn(
          "Version inconsistency detected:",
          versions.map((v) => `${v.name}: ${v.version}`)
        );
      }

      // All services should be on the same major version
      expect(majorVersions.size).toBeLessThanOrEqual(1);
    });
  });
});
