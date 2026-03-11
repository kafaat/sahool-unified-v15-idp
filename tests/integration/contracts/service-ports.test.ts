/**
 * SAHOOL Service Ports Consistency Tests
 * اختبارات اتساق منافذ الخدمات
 *
 * Verifies that all service ports are unique, properly registered,
 * and consistent with the service registry metadata.
 *
 * @module tests/integration/contracts
 * @version 16.0.0
 */

import { describe, it, expect } from "vitest";
import {
  SERVICE_PORTS,
  SERVICE_REGISTRY,
  SERVICE_PORT_ALIASES,
  getServiceUrl,
  getAllServiceUrls,
  type ServicePortKey,
  type ServiceInfo,
} from "../../../packages/shared-types/src/contracts/service-ports";

// =============================================================================
// Service Ports Uniqueness and Registration
// =============================================================================

describe("Service Ports", () => {
  describe("Port Uniqueness", () => {
    it("should have all service ports be unique (no collisions)", () => {
      const portToService = new Map<number, string>();
      const duplicates: string[] = [];

      for (const [name, port] of Object.entries(SERVICE_PORTS)) {
        if (portToService.has(port)) {
          duplicates.push(
            `Port ${port} is claimed by both "${portToService.get(port)}" and "${name}"`,
          );
        } else {
          portToService.set(port, name);
        }
      }

      expect(
        duplicates,
        `Port conflicts detected:\n${duplicates.join("\n")}`,
      ).toHaveLength(0);
    });

    it("should have a minimum number of registered services", () => {
      const serviceCount = Object.keys(SERVICE_PORTS).length;
      // Platform has 72+ active services; port registry should cover a significant portion
      expect(serviceCount).toBeGreaterThanOrEqual(50);
    });

    it("should separate Node.js services (3000-3999) from Python services (8000-8999)", () => {
      const nodeJsPorts: [string, number][] = [];
      const pythonPorts: [string, number][] = [];
      const infraPorts: [string, number][] = [];

      const infraKeys = new Set([
        "KONG_GATEWAY",
        "KONG_ADMIN",
        "NATS",
        "NATS_MONITOR",
        "POSTGRES",
        "PGBOUNCER",
        "REDIS",
      ]);

      for (const [name, port] of Object.entries(SERVICE_PORTS)) {
        if (infraKeys.has(name)) {
          infraPorts.push([name, port]);
        } else if (port >= 3000 && port <= 3999) {
          nodeJsPorts.push([name, port]);
        } else if (port >= 8000 && port <= 8999) {
          pythonPorts.push([name, port]);
        }
      }

      // Verify Node.js services are in the registry with type "nodejs"
      for (const [name] of nodeJsPorts) {
        const registryEntry = Object.values(SERVICE_REGISTRY).find(
          (info) => info.key === name,
        );
        if (registryEntry) {
          expect(
            registryEntry.type,
            `Service ${name} on port 3000-3999 should be nodejs type in registry, got "${registryEntry.type}"`,
          ).toBe("nodejs");
        }
      }

      // Verify Python services are in the registry with type "python"
      // Note: Some Node.js services (e.g., CHAT_SERVICE, IOT_SERVICE) use 8xxx ports
      const nodeJsServicesOn8xxx = new Set([
        "CHAT_SERVICE",
        "IOT_SERVICE",
        "YIELD_PREDICTION",
        "COMMUNITY_CHAT",
      ]);
      for (const [name] of pythonPorts) {
        const registryEntry = Object.values(SERVICE_REGISTRY).find(
          (info) => info.key === name,
        );
        if (registryEntry && !nodeJsServicesOn8xxx.has(name)) {
          expect(
            registryEntry.type,
            `Service ${name} on port 8000-8999 should be python type in registry, got "${registryEntry.type}"`,
          ).toBe("python");
        }
      }
    });
  });

  describe("Port Range Validation", () => {
    it("should have no ports below 1024 except well-known infrastructure", () => {
      const allowedLowPorts: Record<string, number> = {};

      for (const [name, port] of Object.entries(SERVICE_PORTS)) {
        if (port < 1024 && !allowedLowPorts[name]) {
          expect.fail(
            `Service "${name}" uses privileged port ${port} which requires root access`,
          );
        }
      }
    });

    it("should have all ports be integers", () => {
      for (const [name, port] of Object.entries(SERVICE_PORTS)) {
        expect(
          Number.isInteger(port),
          `Service "${name}" port ${port} should be an integer`,
        ).toBe(true);
      }
    });

    it("should have no ports exceed 65535", () => {
      for (const [name, port] of Object.entries(SERVICE_PORTS)) {
        expect(
          port,
          `Service "${name}" port ${port} exceeds max port 65535`,
        ).toBeLessThanOrEqual(65535);
      }
    });

    it("should group core Node.js services in 3000-3030 range", () => {
      const coreNodeServices = [
        "FIELD_MANAGEMENT",
        "MARKETPLACE",
        "RESEARCH_CORE",
        "DISASTER_ASSESSMENT",
        "USER_SERVICE",
        "LAI_ESTIMATION",
        "CROP_GROWTH_MODEL",
      ];

      for (const name of coreNodeServices) {
        const port =
          SERVICE_PORTS[name as keyof typeof SERVICE_PORTS];
        if (port !== undefined) {
          expect(
            port >= 3000 && port <= 3030,
            `Core Node.js service ${name} port ${port} should be in 3000-3030`,
          ).toBe(true);
        }
      }
    });

    it("should assign application ports (ADMIN, WEB) in 3001-3002 range", () => {
      expect(SERVICE_PORTS.ADMIN).toBe(3001);
      expect(SERVICE_PORTS.WEB).toBe(3002);
    });

    it("should assign infrastructure ports to standard values", () => {
      expect(SERVICE_PORTS.KONG_GATEWAY).toBe(8000);
      expect(SERVICE_PORTS.KONG_ADMIN).toBe(8001);
      expect(SERVICE_PORTS.NATS).toBe(4222);
      expect(SERVICE_PORTS.POSTGRES).toBe(5432);
      expect(SERVICE_PORTS.PGBOUNCER).toBe(6432);
      expect(SERVICE_PORTS.REDIS).toBe(6379);
    });
  });

  describe("Service Registry Completeness", () => {
    it("should have registry entries reference correct ports", () => {
      for (const [serviceName, info] of Object.entries(SERVICE_REGISTRY)) {
        const expectedPort =
          SERVICE_PORTS[info.key as keyof typeof SERVICE_PORTS];

        expect(
          expectedPort,
          `Registry entry "${serviceName}" references unknown port key "${info.key}"`,
        ).toBeDefined();

        expect(
          info.port,
          `Registry "${serviceName}" port mismatch: got ${info.port}, expected ${expectedPort}`,
        ).toBe(expectedPort);
      }
    });

    it("should have no registry entries with empty names", () => {
      for (const [serviceName, info] of Object.entries(SERVICE_REGISTRY)) {
        expect(info.name.trim().length).toBeGreaterThan(0);
        expect(info.nameAr.trim().length).toBeGreaterThan(0);
      }
    });

    it("should have registry entries with non-empty kongRoute", () => {
      for (const [serviceName, info] of Object.entries(SERVICE_REGISTRY)) {
        expect(
          info.kongRoute.length,
          `Registry "${serviceName}" has empty kongRoute`,
        ).toBeGreaterThan(0);
        expect(
          info.kongRoute.startsWith("/"),
          `Registry "${serviceName}" kongRoute "${info.kongRoute}" should start with /`,
        ).toBe(true);
      }
    });

    it("should have no duplicate kongRoutes in registry", () => {
      const routeMap = new Map<string, string>();
      const duplicates: string[] = [];

      for (const [serviceName, info] of Object.entries(SERVICE_REGISTRY)) {
        if (routeMap.has(info.kongRoute)) {
          duplicates.push(
            `Kong route "${info.kongRoute}" is claimed by "${routeMap.get(info.kongRoute)}" and "${serviceName}"`,
          );
        } else {
          routeMap.set(info.kongRoute, serviceName);
        }
      }

      expect(
        duplicates,
        `Duplicate Kong routes:\n${duplicates.join("\n")}`,
      ).toHaveLength(0);
    });

    it("should have at least one deprecated service in registry", () => {
      const deprecatedServices = Object.entries(SERVICE_REGISTRY).filter(
        ([, info]) => info.deprecated === true,
      );

      expect(deprecatedServices.length).toBeGreaterThanOrEqual(1);
    });

    it("should have deprecated services point to active replacement services", () => {
      for (const [name, info] of Object.entries(SERVICE_REGISTRY)) {
        if (info.deprecated && info.replacedBy) {
          // The replacement should exist in SERVICE_PORTS
          const replacementPort =
            SERVICE_PORTS[info.replacedBy as keyof typeof SERVICE_PORTS];
          expect(
            replacementPort,
            `Deprecated "${name}" replacement "${info.replacedBy}" not found in SERVICE_PORTS`,
          ).toBeDefined();

          // The replacement should NOT itself be deprecated
          const replacementEntry = Object.values(SERVICE_REGISTRY).find(
            (r) => r.key === info.replacedBy,
          );
          if (replacementEntry) {
            expect(
              replacementEntry.deprecated,
              `Replacement service "${info.replacedBy}" for "${name}" is itself deprecated`,
            ).toBeFalsy();
          }
        }
      }
    });
  });

  describe("Service Port Aliases", () => {
    it("should have all aliases resolve to valid ports", () => {
      for (const [alias, port] of Object.entries(SERVICE_PORT_ALIASES)) {
        expect(
          typeof port,
          `Alias "${alias}" should resolve to a number, got ${typeof port}`,
        ).toBe("number");
        expect(
          port,
          `Alias "${alias}" resolves to invalid port ${port}`,
        ).toBeGreaterThan(0);
      }
    });

    it("should have all alias ports exist in SERVICE_PORTS", () => {
      const validPorts = new Set(Object.values(SERVICE_PORTS));

      for (const [alias, port] of Object.entries(SERVICE_PORT_ALIASES)) {
        expect(
          validPorts.has(port),
          `Alias "${alias}" maps to port ${port} which is not in SERVICE_PORTS`,
        ).toBe(true);
      }
    });

    it("should have aliases use camelCase naming convention", () => {
      for (const alias of Object.keys(SERVICE_PORT_ALIASES)) {
        // camelCase: starts with lowercase, no underscores or hyphens
        expect(
          alias,
          `Alias "${alias}" should use camelCase naming`,
        ).toMatch(/^[a-z][a-zA-Z0-9]*$/);
      }
    });

    it("should have expected legacy aliases present", () => {
      // Key aliases that existing code depends on
      expect(SERVICE_PORT_ALIASES).toHaveProperty("auth");
      expect(SERVICE_PORT_ALIASES).toHaveProperty("fieldCore");
      expect(SERVICE_PORT_ALIASES).toHaveProperty("satellite");
      expect(SERVICE_PORT_ALIASES).toHaveProperty("weather");
      expect(SERVICE_PORT_ALIASES).toHaveProperty("irrigation");
      expect(SERVICE_PORT_ALIASES).toHaveProperty("billing");
    });
  });

  describe("Helper Functions", () => {
    it("should generate correct service URL with defaults", () => {
      const url = getServiceUrl(SERVICE_PORTS.FIELD_MANAGEMENT);
      expect(url).toBe("http://localhost:3000");
    });

    it("should generate correct service URL with custom host", () => {
      const url = getServiceUrl(
        SERVICE_PORTS.WEATHER,
        "weather.sahool.svc.cluster.local",
      );
      expect(url).toBe("http://weather.sahool.svc.cluster.local:8092");
    });

    it("should generate correct service URL with HTTPS", () => {
      const url = getServiceUrl(
        SERVICE_PORTS.USER_SERVICE,
        "api.sahool.app",
        "https",
      );
      expect(url).toBe("https://api.sahool.app:3025");
    });

    it("should return all service URLs with matching count", () => {
      const urls = getAllServiceUrls();
      const portCount = Object.keys(SERVICE_PORTS).length;
      expect(Object.keys(urls).length).toBe(portCount);
    });

    it("should return all service URLs with correct format", () => {
      const urls = getAllServiceUrls("internal.sahool.io", "https");

      for (const [key, url] of Object.entries(urls)) {
        expect(url).toMatch(/^https:\/\/internal\.sahool\.io:\d+$/);

        const port =
          SERVICE_PORTS[key as keyof typeof SERVICE_PORTS];
        expect(url).toContain(`:${port}`);
      }
    });
  });

  describe("Cross-Reference with Known Services", () => {
    it("should include all core services from the CLAUDE.md specification", () => {
      // Core services that must exist per architecture
      const requiredServices: Array<[string, number]> = [
        ["FIELD_MANAGEMENT", 3000],
        ["USER_SERVICE", 3025],
        ["NOTIFICATIONS", 8110],
        ["BILLING_CORE", 8089],
        ["TASK_SERVICE", 8103],
        ["EQUIPMENT", 8101],
        ["ALERT_SERVICE", 8113],
        ["AUDIT_SERVICE", 8114],
      ];

      for (const [name, expectedPort] of requiredServices) {
        const port =
          SERVICE_PORTS[name as keyof typeof SERVICE_PORTS];
        expect(
          port,
          `Required service "${name}" not found in SERVICE_PORTS`,
        ).toBeDefined();
        expect(
          port,
          `Service "${name}" should be on port ${expectedPort}, got ${port}`,
        ).toBe(expectedPort);
      }
    });

    it("should include all intelligence layer services", () => {
      const intelligenceServices: Array<[string, number]> = [
        ["VEGETATION_ANALYSIS", 8090],
        ["INDICATORS", 8091],
        ["CROP_INTELLIGENCE", 8095],
        ["YOLO_VISION", 8150],
        ["TERRAIN_CORE", 8185],
      ];

      for (const [name, expectedPort] of intelligenceServices) {
        const port =
          SERVICE_PORTS[name as keyof typeof SERVICE_PORTS];
        expect(port, `Intelligence service "${name}" missing`).toBe(
          expectedPort,
        );
      }
    });

    it("should include all AI/agent services", () => {
      const aiServices = [
        "COPILOT_API",
        "AI_ADVISOR",
        "AI_AGENTS_CORE",
        "AI_AGENTS_SERVICE",
        "AGENT_REGISTRY",
        "LLM_ORCHESTRATOR",
        "KNOWLEDGE_GRAPH",
        "CODE_FIX_AGENT",
        "CODE_REVIEW_SERVICE",
      ];

      for (const name of aiServices) {
        expect(
          SERVICE_PORTS[name as keyof typeof SERVICE_PORTS],
          `AI service "${name}" missing from SERVICE_PORTS`,
        ).toBeDefined();
      }
    });

    it("should include all IoT services", () => {
      expect(SERVICE_PORTS.IOT_SERVICE).toBe(8117);
      expect(SERVICE_PORTS.IOT_GATEWAY).toBe(8106);
      expect(SERVICE_PORTS.IOT_SENSOR_HUB).toBe(8251);
    });

    it("should include vision and terrain services", () => {
      expect(SERVICE_PORTS.YOLO_VISION).toBe(8150);
      expect(SERVICE_PORTS.GROUND_VISION).toBe(8182);
      expect(SERVICE_PORTS.TERRAIN_CORE).toBe(8185);
      expect(SERVICE_PORTS.HYDROLOGY).toBe(8165);
      expect(SERVICE_PORTS.LEVELING_OPTIMIZER).toBe(8170);
      expect(SERVICE_PORTS.EDGE_ORCHESTRATOR).toBe(8180);
    });

    it("should include specialized domain services", () => {
      expect(SERVICE_PORTS.FERTIGATION_ENGINE).toBe(8252);
      expect(SERVICE_PORTS.IRRIGATION_CYCLE_ENGINE).toBe(8250);
      expect(SERVICE_PORTS.DIGITAL_TWIN).toBe(8253);
      expect(SERVICE_PORTS.LOWCODE_ENGINE).toBe(8132);
      expect(SERVICE_PORTS.MCP_SERVER).toBe(8201);
    });
  });
});
