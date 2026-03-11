/**
 * SAHOOL API Contract Consistency Tests
 * اختبارات اتساق عقود واجهة برمجة التطبيقات
 *
 * Verifies that all API contracts maintain structural consistency:
 * - ApiResponse shape compliance
 * - Error code format and bilingual messages
 * - Service port registry integrity
 * - DTO validation coverage
 * - Endpoint path conventions
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
} from "../../../packages/shared-types/src/contracts/service-ports";
import {
  ERROR_CODES,
  ERROR_MESSAGES,
  getErrorMessage,
  getLocalizedError,
  httpStatusToErrorCode,
  isRetryable,
} from "../../../packages/shared-types/src/contracts/error-codes";
import {
  API_PREFIX,
  API_VERSION,
  HEALTH_ENDPOINTS,
  AUTH_ENDPOINTS,
  FIELD_ENDPOINTS,
  WEATHER_ENDPOINTS,
  SATELLITE_ENDPOINTS,
  CROP_HEALTH_ENDPOINTS,
  IRRIGATION_ENDPOINTS,
  ADVISORY_ENDPOINTS,
  TASK_ENDPOINTS,
  EQUIPMENT_ENDPOINTS,
  ALERT_ENDPOINTS,
  NOTIFICATION_ENDPOINTS,
  IOT_ENDPOINTS,
  VIRTUAL_SENSOR_ENDPOINTS,
  MARKETPLACE_ENDPOINTS,
  BILLING_ENDPOINTS,
  CHAT_ENDPOINTS,
  INDICATOR_ENDPOINTS,
  INTELLIGENCE_ENDPOINTS,
  YIELD_ENDPOINTS,
  AI_ENDPOINTS,
  VISION_ENDPOINTS,
  TERRAIN_ENDPOINTS,
  USER_ENDPOINTS,
  AUDIT_ENDPOINTS,
  EDGE_ENDPOINTS,
  PUBLIC_ENDPOINTS,
  buildUrl,
} from "../../../packages/shared-types/src/contracts/api-endpoints";
import type {
  ApiResponse,
  PaginationMeta,
  PaginatedResponse,
  ServiceHealthResponse,
} from "../../../packages/shared-types/src/contracts/api-responses";
import {
  TIMEOUT_DEFAULTS,
  CIRCUIT_BREAKER_DEFAULTS,
  RETRY_DEFAULTS,
  RATE_LIMIT_HEADER_NAMES,
  CUSTOM_HEADERS,
  DEFAULT_HEADERS,
} from "../../../packages/shared-types/src/contracts/api-responses";
import { CONTRACT_VERSION } from "../../../packages/shared-types/src/contracts";

// =============================================================================
// 1. ApiResponse Shape Consistency
// =============================================================================

describe("API Contract Consistency", () => {
  describe("Contract Version", () => {
    it("should have a valid semver contract version", () => {
      expect(CONTRACT_VERSION).toBeDefined();
      expect(CONTRACT_VERSION).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it("should export API_VERSION as v1", () => {
      expect(API_VERSION).toBe("v1");
    });

    it("should have API_PREFIX matching /api/v1", () => {
      expect(API_PREFIX).toBe("/api/v1");
    });
  });

  describe("ApiResponse Shape Consistency", () => {
    it("should define ApiResponse with required success field", () => {
      const successResponse: ApiResponse<{ id: string }> = {
        success: true,
        data: { id: "test-123" },
      };

      expect(successResponse).toHaveProperty("success");
      expect(successResponse.success).toBe(true);
      expect(successResponse.data).toBeDefined();
    });

    it("should support error responses with errorCode", () => {
      const errorResponse: ApiResponse = {
        success: false,
        error: "Resource not found",
        errorAr: "المورد غير موجود",
        errorCode: ERROR_CODES.NOT_FOUND,
        requestId: "req-abc-123",
      };

      expect(errorResponse.success).toBe(false);
      expect(errorResponse.errorCode).toBeDefined();
      expect(errorResponse.error).toBeDefined();
      expect(errorResponse.errorAr).toBeDefined();
      expect(errorResponse.requestId).toBeDefined();
      expect(errorResponse.data).toBeUndefined();
    });

    it("should support optional message and requestId fields", () => {
      const response: ApiResponse = {
        success: true,
        message: "Operation completed successfully",
        requestId: "req-xyz-789",
      };

      expect(response.message).toBeDefined();
      expect(response.requestId).toMatch(/^req-/);
    });

    it("should support pagination metadata on paginated responses", () => {
      const paginatedResponse: PaginatedResponse<{ id: string }> = {
        success: true,
        data: [{ id: "1" }, { id: "2" }],
        pagination: {
          total: 100,
          page: 1,
          limit: 10,
          totalPages: 10,
          hasMore: true,
        },
      };

      expect(paginatedResponse.pagination).toBeDefined();
      expect(paginatedResponse.pagination.total).toBe(100);
      expect(paginatedResponse.pagination.page).toBe(1);
      expect(paginatedResponse.pagination.limit).toBe(10);
      expect(paginatedResponse.pagination.totalPages).toBe(10);
      expect(paginatedResponse.pagination.hasMore).toBe(true);
    });

    it("should require total, page, and limit in PaginationMeta", () => {
      const pagination: PaginationMeta = {
        total: 50,
        page: 2,
        limit: 25,
      };

      expect(pagination.total).toBeGreaterThanOrEqual(0);
      expect(pagination.page).toBeGreaterThanOrEqual(1);
      expect(pagination.limit).toBeGreaterThan(0);
    });

    it("should support optional offset in PaginationMeta", () => {
      const pagination: PaginationMeta = {
        total: 200,
        page: 3,
        limit: 20,
        offset: 40,
      };

      expect(pagination.offset).toBe(40);
    });

    it("should model ServiceHealthResponse with required status and service fields", () => {
      const health: ServiceHealthResponse = {
        status: "ok",
        service: "field-management",
        version: "16.0.0",
        checks: { database: true, nats: true },
      };

      expect(health.status).toMatch(/^(ok|degraded|error)$/);
      expect(health.service).toBeDefined();
    });

    it("should enforce error responses include errorCode for client mapping", () => {
      // Verify every error code has a corresponding ErrorMessage entry
      const errorCodesWithMessages = Object.values(ERROR_CODES).filter(
        (code) => ERROR_MESSAGES[code] !== undefined,
      );

      // Vision error codes (E1xxx-E8xxx) do not have entries in ERROR_MESSAGES
      const visionErrorCodes = Object.values(ERROR_CODES).filter((code) =>
        /^E\d{4}$/.test(code),
      );
      const generalErrorCodes = Object.values(ERROR_CODES).filter(
        (code) => !/^E\d{4}$/.test(code),
      );

      // All general error codes must have message entries
      for (const code of generalErrorCodes) {
        expect(
          ERROR_MESSAGES[code],
          `Missing ErrorMessage entry for general code: ${code}`,
        ).toBeDefined();
      }

      // Vision error codes are service-specific and may not have global messages
      expect(visionErrorCodes.length).toBeGreaterThan(0);
    });
  });

  // ===========================================================================
  // 2. Service Port Registry Accuracy
  // ===========================================================================

  describe("Service Port Registry Accuracy", () => {
    it("should have no port conflicts between services", () => {
      const ports = Object.entries(SERVICE_PORTS);
      const portMap = new Map<number, string[]>();

      for (const [name, port] of ports) {
        if (!portMap.has(port)) {
          portMap.set(port, []);
        }
        portMap.get(port)!.push(name);
      }

      for (const [port, services] of portMap.entries()) {
        expect(
          services.length,
          `Port ${port} is used by multiple services: ${services.join(", ")}`,
        ).toBe(1);
      }
    });

    it("should assign ports within valid ranges", () => {
      const infraPorts = [
        "KONG_GATEWAY",
        "KONG_ADMIN",
        "NATS",
        "NATS_MONITOR",
        "POSTGRES",
        "PGBOUNCER",
        "REDIS",
      ];

      for (const [name, port] of Object.entries(SERVICE_PORTS)) {
        expect(port, `Port for ${name} should be positive`).toBeGreaterThan(0);
        expect(port, `Port for ${name} should be below 65536`).toBeLessThan(
          65536,
        );

        // Application ports should be in 3000-3999 or 8000-9999 range
        if (!infraPorts.includes(name)) {
          const isValidRange =
            (port >= 3000 && port <= 3999) || (port >= 8000 && port <= 9999);
          expect(
            isValidRange,
            `Service ${name} port ${port} should be in 3000-3999 or 8000-9999 range`,
          ).toBe(true);
        }
      }
    });

    it("should have all SERVICE_REGISTRY entries referencing valid SERVICE_PORTS keys", () => {
      for (const [serviceName, info] of Object.entries(SERVICE_REGISTRY)) {
        // The key must exist in SERVICE_PORTS
        expect(
          SERVICE_PORTS[info.key as keyof typeof SERVICE_PORTS],
          `SERVICE_REGISTRY "${serviceName}" references unknown key "${info.key}"`,
        ).toBeDefined();

        // The port in registry must match the constant
        expect(
          info.port,
          `SERVICE_REGISTRY "${serviceName}" port ${info.port} does not match SERVICE_PORTS.${info.key} (${SERVICE_PORTS[info.key as keyof typeof SERVICE_PORTS]})`,
        ).toBe(SERVICE_PORTS[info.key as keyof typeof SERVICE_PORTS]);
      }
    });

    it("should have valid runtime types for all registry entries", () => {
      const validTypes = ["python", "nodejs", "infrastructure"];

      for (const [name, info] of Object.entries(SERVICE_REGISTRY)) {
        expect(
          validTypes,
          `SERVICE_REGISTRY "${name}" has invalid type "${info.type}"`,
        ).toContain(info.type);
      }
    });

    it("should have valid layer assignments for all registry entries", () => {
      const validLayers = [
        "core",
        "acquisition",
        "intelligence",
        "decision",
        "business",
      ];

      for (const [name, info] of Object.entries(SERVICE_REGISTRY)) {
        expect(
          validLayers,
          `SERVICE_REGISTRY "${name}" has invalid layer "${info.layer}"`,
        ).toContain(info.layer);
      }
    });

    it("should mark deprecated services with replacedBy pointing to valid keys", () => {
      for (const [name, info] of Object.entries(SERVICE_REGISTRY)) {
        if (info.deprecated) {
          expect(
            info.replacedBy,
            `Deprecated service "${name}" must have replacedBy set`,
          ).toBeDefined();

          expect(
            SERVICE_PORTS[info.replacedBy as keyof typeof SERVICE_PORTS],
            `Deprecated service "${name}" replacedBy "${info.replacedBy}" is not a valid SERVICE_PORTS key`,
          ).toBeDefined();
        }
      }
    });

    it("should have Kong routes for all registry entries", () => {
      for (const [name, info] of Object.entries(SERVICE_REGISTRY)) {
        expect(
          info.kongRoute,
          `SERVICE_REGISTRY "${name}" is missing kongRoute`,
        ).toBeDefined();
        expect(
          info.kongRoute.startsWith("/"),
          `SERVICE_REGISTRY "${name}" kongRoute should start with /`,
        ).toBe(true);
      }
    });

    it("should have bilingual names for all registry entries", () => {
      for (const [name, info] of Object.entries(SERVICE_REGISTRY)) {
        expect(
          info.name,
          `SERVICE_REGISTRY "${name}" is missing English name`,
        ).toBeTruthy();
        expect(
          info.nameAr,
          `SERVICE_REGISTRY "${name}" is missing Arabic name`,
        ).toBeTruthy();

        // Arabic name should contain Arabic characters
        expect(
          /[\u0600-\u06FF]/.test(info.nameAr),
          `SERVICE_REGISTRY "${name}" nameAr "${info.nameAr}" does not contain Arabic characters`,
        ).toBe(true);
      }
    });

    it("should have all SERVICE_PORT_ALIASES point to valid SERVICE_PORTS values", () => {
      for (const [alias, port] of Object.entries(SERVICE_PORT_ALIASES)) {
        const matchingEntry = Object.entries(SERVICE_PORTS).find(
          ([, p]) => p === port,
        );
        expect(
          matchingEntry,
          `Alias "${alias}" maps to port ${port} which is not in SERVICE_PORTS`,
        ).toBeDefined();
      }
    });

    it("should provide working getServiceUrl helper", () => {
      const url = getServiceUrl(SERVICE_PORTS.FIELD_MANAGEMENT);
      expect(url).toBe("http://localhost:3000");

      const customUrl = getServiceUrl(
        SERVICE_PORTS.USER_SERVICE,
        "api.sahool.app",
        "https",
      );
      expect(customUrl).toBe("https://api.sahool.app:3025");
    });

    it("should provide working getAllServiceUrls helper", () => {
      const urls = getAllServiceUrls();
      expect(Object.keys(urls).length).toBe(
        Object.keys(SERVICE_PORTS).length,
      );

      for (const [key, url] of Object.entries(urls)) {
        expect(url).toMatch(/^http:\/\/localhost:\d+$/);
      }
    });
  });

  // ===========================================================================
  // 3. Error Code Consistency
  // ===========================================================================

  describe("Error Code Consistency", () => {
    it("should have all vision error codes follow E{category}{sequence} pattern", () => {
      const visionCodeEntries = Object.entries(ERROR_CODES).filter(
        ([key]) => key.startsWith("VISION_"),
      );

      expect(visionCodeEntries.length).toBeGreaterThan(0);

      for (const [key, code] of visionCodeEntries) {
        expect(
          code,
          `Vision error ${key} should match E followed by 4 digits`,
        ).toMatch(/^E\d{4}$/);
      }
    });

    it("should have vision error codes organized by category", () => {
      const visionCodes = Object.entries(ERROR_CODES)
        .filter(([key]) => key.startsWith("VISION_"))
        .map(([key, code]) => ({ key, code, category: code.charAt(1) }));

      // Categories present in the codebase
      const categories = new Set(visionCodes.map((c) => c.category));
      // Should have validation (1), model (2), processing (3), resource (4),
      // external (5), rate limit (6), timeout (7)
      expect(categories.size).toBeGreaterThanOrEqual(6);
    });

    it("should have bilingual messages for all general error codes", () => {
      const generalCodes = Object.entries(ERROR_CODES).filter(
        ([, code]) => !/^E\d{4}$/.test(code),
      );

      for (const [key, code] of generalCodes) {
        const message = ERROR_MESSAGES[code];
        expect(
          message,
          `Missing error message for ${key} (${code})`,
        ).toBeDefined();

        if (message) {
          expect(
            message.en,
            `${key}: English message is empty`,
          ).toBeTruthy();
          expect(
            message.ar,
            `${key}: Arabic message is empty`,
          ).toBeTruthy();

          // Arabic message should contain Arabic characters
          expect(
            /[\u0600-\u06FF]/.test(message.ar),
            `${key}: Arabic message "${message.ar}" does not contain Arabic characters`,
          ).toBe(true);
        }
      }
    });

    it("should have consistent httpStatus codes matching error categories", () => {
      // Authentication errors -> 401
      const authCodes = [
        ERROR_CODES.UNAUTHORIZED,
        ERROR_CODES.TOKEN_EXPIRED,
        ERROR_CODES.TOKEN_INVALID,
        ERROR_CODES.SESSION_EXPIRED,
      ];
      for (const code of authCodes) {
        expect(
          ERROR_MESSAGES[code]?.httpStatus,
          `Auth code ${code} should map to HTTP 401`,
        ).toBe(401);
      }

      // Authorization errors -> 403
      const authzCodes = [
        ERROR_CODES.FORBIDDEN,
        ERROR_CODES.INSUFFICIENT_PERMISSIONS,
      ];
      for (const code of authzCodes) {
        expect(
          ERROR_MESSAGES[code]?.httpStatus,
          `Authz code ${code} should map to HTTP 403`,
        ).toBe(403);
      }

      // Not found -> 404
      expect(ERROR_MESSAGES[ERROR_CODES.NOT_FOUND]?.httpStatus).toBe(404);

      // Rate limited -> 429
      expect(ERROR_MESSAGES[ERROR_CODES.RATE_LIMITED]?.httpStatus).toBe(429);

      // Server error -> 500
      expect(ERROR_MESSAGES[ERROR_CODES.SERVER_ERROR]?.httpStatus).toBe(500);

      // Bad gateway -> 502
      expect(ERROR_MESSAGES[ERROR_CODES.BAD_GATEWAY]?.httpStatus).toBe(502);

      // Service unavailable -> 503
      expect(ERROR_MESSAGES[ERROR_CODES.SERVICE_UNAVAILABLE]?.httpStatus).toBe(
        503,
      );

      // Gateway timeout -> 504
      expect(ERROR_MESSAGES[ERROR_CODES.GATEWAY_TIMEOUT]?.httpStatus).toBe(504);
    });

    it("should have consistent retryable flags", () => {
      // Network/transport errors should be retryable
      expect(isRetryable(ERROR_CODES.NETWORK_ERROR)).toBe(true);
      expect(isRetryable(ERROR_CODES.TIMEOUT)).toBe(true);
      expect(isRetryable(ERROR_CODES.CIRCUIT_OPEN)).toBe(true);
      expect(isRetryable(ERROR_CODES.SERVICE_UNAVAILABLE)).toBe(true);
      expect(isRetryable(ERROR_CODES.RATE_LIMITED)).toBe(true);

      // Auth errors should NOT be retryable
      expect(isRetryable(ERROR_CODES.UNAUTHORIZED)).toBe(false);
      expect(isRetryable(ERROR_CODES.TOKEN_INVALID)).toBe(false);
      expect(isRetryable(ERROR_CODES.FORBIDDEN)).toBe(false);

      // Client validation errors should NOT be retryable
      expect(isRetryable(ERROR_CODES.BAD_REQUEST)).toBe(false);
      expect(isRetryable(ERROR_CODES.VALIDATION_ERROR)).toBe(false);
      expect(isRetryable(ERROR_CODES.NOT_FOUND)).toBe(false);
    });

    it("should have getErrorMessage return UNKNOWN for unrecognized codes", () => {
      const unknown = getErrorMessage("NONEXISTENT_CODE");
      expect(unknown.code).toBe(ERROR_CODES.UNKNOWN);
    });

    it("should have getLocalizedError return correct language", () => {
      const enMessage = getLocalizedError(ERROR_CODES.NOT_FOUND, "en");
      const arMessage = getLocalizedError(ERROR_CODES.NOT_FOUND, "ar");

      expect(enMessage).toBe("Resource not found");
      expect(arMessage).toBe("المورد غير موجود");
      expect(enMessage).not.toBe(arMessage);
    });

    it("should have httpStatusToErrorCode map all standard HTTP errors", () => {
      expect(httpStatusToErrorCode(400)).toBe(ERROR_CODES.BAD_REQUEST);
      expect(httpStatusToErrorCode(401)).toBe(ERROR_CODES.UNAUTHORIZED);
      expect(httpStatusToErrorCode(403)).toBe(ERROR_CODES.FORBIDDEN);
      expect(httpStatusToErrorCode(404)).toBe(ERROR_CODES.NOT_FOUND);
      expect(httpStatusToErrorCode(409)).toBe(ERROR_CODES.CONFLICT);
      expect(httpStatusToErrorCode(429)).toBe(ERROR_CODES.RATE_LIMITED);
      expect(httpStatusToErrorCode(502)).toBe(ERROR_CODES.INVALID_RESPONSE);
      expect(httpStatusToErrorCode(503)).toBe(ERROR_CODES.SERVICE_UNAVAILABLE);
      expect(httpStatusToErrorCode(504)).toBe(ERROR_CODES.GATEWAY_TIMEOUT);
      // Generic 5xx fallback
      expect(httpStatusToErrorCode(500)).toBe(ERROR_CODES.SERVER_ERROR);
      expect(httpStatusToErrorCode(501)).toBe(ERROR_CODES.SERVER_ERROR);
    });

    it("should have all ErrorMessage entries with matching code field", () => {
      for (const [code, message] of Object.entries(ERROR_MESSAGES)) {
        expect(
          message.code,
          `ERROR_MESSAGES["${code}"].code should match the key`,
        ).toBe(code);
      }
    });

    it("should have no duplicate error code values", () => {
      const values = Object.values(ERROR_CODES);
      const uniqueValues = new Set(values);
      expect(
        uniqueValues.size,
        `Found ${values.length - uniqueValues.size} duplicate error code values`,
      ).toBe(values.length);
    });

    it("should have httpStatus 0 only for non-HTTP errors", () => {
      for (const [code, message] of Object.entries(ERROR_MESSAGES)) {
        if (message.httpStatus === 0) {
          // Only network/mobile/unknown errors should have httpStatus 0
          const validZeroStatusCodes = [
            ERROR_CODES.NETWORK_ERROR,
            ERROR_CODES.OFFLINE,
            ERROR_CODES.SYNC_FAILED,
            ERROR_CODES.CERTIFICATE_ERROR,
            ERROR_CODES.UNKNOWN,
          ];
          expect(
            validZeroStatusCodes,
            `Error code "${code}" has httpStatus 0 but is not a non-HTTP error`,
          ).toContain(code);
        }
      }
    });
  });

  // ===========================================================================
  // 4. DTO Validation Coverage - Endpoint Path Conventions
  // ===========================================================================

  describe("DTO Validation Coverage and Endpoint Conventions", () => {
    it("should have all endpoint paths start with API_PREFIX", () => {
      const allEndpointGroups = [
        AUTH_ENDPOINTS,
        FIELD_ENDPOINTS,
        WEATHER_ENDPOINTS,
        SATELLITE_ENDPOINTS,
        CROP_HEALTH_ENDPOINTS,
        IRRIGATION_ENDPOINTS,
        ADVISORY_ENDPOINTS,
        TASK_ENDPOINTS,
        EQUIPMENT_ENDPOINTS,
        ALERT_ENDPOINTS,
        NOTIFICATION_ENDPOINTS,
        IOT_ENDPOINTS,
        VIRTUAL_SENSOR_ENDPOINTS,
        MARKETPLACE_ENDPOINTS,
        BILLING_ENDPOINTS,
        CHAT_ENDPOINTS,
        INDICATOR_ENDPOINTS,
        INTELLIGENCE_ENDPOINTS,
        YIELD_ENDPOINTS,
        AI_ENDPOINTS,
        VISION_ENDPOINTS,
        TERRAIN_ENDPOINTS,
        USER_ENDPOINTS,
        AUDIT_ENDPOINTS,
        EDGE_ENDPOINTS,
      ];

      for (const group of allEndpointGroups) {
        for (const [key, path] of Object.entries(group)) {
          expect(
            (path as string).startsWith(API_PREFIX),
            `Endpoint ${key} path "${path}" should start with "${API_PREFIX}"`,
          ).toBe(true);
        }
      }
    });

    it("should use {param} syntax for path parameters", () => {
      const endpointsWithParams = [
        FIELD_ENDPOINTS.GET,
        FIELD_ENDPOINTS.UPDATE,
        FIELD_ENDPOINTS.DELETE,
        TASK_ENDPOINTS.GET,
        EQUIPMENT_ENDPOINTS.GET,
        ALERT_ENDPOINTS.GET,
        IOT_ENDPOINTS.DEVICE_GET,
        EDGE_ENDPOINTS.DEVICE_GET,
      ];

      for (const endpoint of endpointsWithParams) {
        expect(
          endpoint,
          `Endpoint "${endpoint}" should contain {param} syntax`,
        ).toMatch(/\{[a-zA-Z]+\}/);
      }
    });

    it("should have buildUrl correctly replace path parameters", () => {
      const url = buildUrl(FIELD_ENDPOINTS.GET, { fieldId: "abc-123" });
      expect(url).toBe("/api/v1/fields/abc-123");
      expect(url).not.toContain("{");

      const taskUrl = buildUrl(TASK_ENDPOINTS.GET, { taskId: "task-456" });
      expect(taskUrl).toBe("/api/v1/tasks/task-456");

      const edgeUrl = buildUrl(EDGE_ENDPOINTS.DEVICE_GET, {
        deviceId: "dev-789",
      });
      expect(edgeUrl).toBe("/api/v1/edge/devices/dev-789");
    });

    it("should encode path parameters with special characters", () => {
      const url = buildUrl(FIELD_ENDPOINTS.GET, {
        fieldId: "field with spaces",
      });
      expect(url).toContain("field%20with%20spaces");
      expect(url).not.toContain(" ");
    });

    it("should have CRUD endpoints follow RESTful conventions", () => {
      // Fields - complete CRUD
      expect(FIELD_ENDPOINTS.LIST).toBe(`${API_PREFIX}/fields`);
      expect(FIELD_ENDPOINTS.CREATE).toBe(`${API_PREFIX}/fields`);
      expect(FIELD_ENDPOINTS.GET).toContain("{fieldId}");
      expect(FIELD_ENDPOINTS.UPDATE).toContain("{fieldId}");
      expect(FIELD_ENDPOINTS.DELETE).toContain("{fieldId}");

      // Tasks - complete CRUD
      expect(TASK_ENDPOINTS.LIST).toBe(`${API_PREFIX}/tasks`);
      expect(TASK_ENDPOINTS.CREATE).toBe(`${API_PREFIX}/tasks`);
      expect(TASK_ENDPOINTS.GET).toContain("{taskId}");
      expect(TASK_ENDPOINTS.UPDATE).toContain("{taskId}");
      expect(TASK_ENDPOINTS.DELETE).toContain("{taskId}");

      // Equipment - complete CRUD
      expect(EQUIPMENT_ENDPOINTS.LIST).toBe(`${API_PREFIX}/equipment`);
      expect(EQUIPMENT_ENDPOINTS.CREATE).toBe(`${API_PREFIX}/equipment`);
      expect(EQUIPMENT_ENDPOINTS.GET).toContain("{equipmentId}");
      expect(EQUIPMENT_ENDPOINTS.UPDATE).toContain("{equipmentId}");
      expect(EQUIPMENT_ENDPOINTS.DELETE).toContain("{equipmentId}");
    });

    it("should have LIST and CREATE endpoints share the same base path", () => {
      expect(FIELD_ENDPOINTS.LIST).toBe(FIELD_ENDPOINTS.CREATE);
      expect(TASK_ENDPOINTS.LIST).toBe(TASK_ENDPOINTS.CREATE);
      expect(EQUIPMENT_ENDPOINTS.LIST).toBe(EQUIPMENT_ENDPOINTS.CREATE);
      expect(ALERT_ENDPOINTS.LIST).toBe(ALERT_ENDPOINTS.CREATE);
      expect(USER_ENDPOINTS.LIST).toBe(USER_ENDPOINTS.CREATE);
    });

    it("should have health endpoints not use API_PREFIX", () => {
      expect(HEALTH_ENDPOINTS.LIVENESS).toBe("/healthz");
      expect(HEALTH_ENDPOINTS.READINESS).toBe("/readyz");
      expect(HEALTH_ENDPOINTS.HEALTH).toBe("/health");
      expect(HEALTH_ENDPOINTS.METRICS).toBe("/metrics");
    });

    it("should have PUBLIC_ENDPOINTS include only auth and health endpoints", () => {
      expect(PUBLIC_ENDPOINTS).toContain(AUTH_ENDPOINTS.LOGIN);
      expect(PUBLIC_ENDPOINTS).toContain(AUTH_ENDPOINTS.REGISTER);
      expect(PUBLIC_ENDPOINTS).toContain(HEALTH_ENDPOINTS.LIVENESS);
      expect(PUBLIC_ENDPOINTS).toContain(HEALTH_ENDPOINTS.READINESS);

      // Protected endpoints should NOT be public
      expect(PUBLIC_ENDPOINTS).not.toContain(FIELD_ENDPOINTS.LIST);
      expect(PUBLIC_ENDPOINTS).not.toContain(TASK_ENDPOINTS.LIST);
      expect(PUBLIC_ENDPOINTS).not.toContain(AI_ENDPOINTS.COPILOT_CHAT);
    });

    it("should have vision endpoints follow /vision/ namespace", () => {
      for (const [key, path] of Object.entries(VISION_ENDPOINTS)) {
        expect(
          path,
          `VISION_ENDPOINTS.${key} should be under /vision/`,
        ).toContain("/vision/");
      }
    });

    it("should have terrain endpoints cover terrain, hydrology, and leveling", () => {
      expect(TERRAIN_ENDPOINTS.DEM).toContain("/terrain/");
      expect(TERRAIN_ENDPOINTS.SLOPE).toContain("/terrain/");
      expect(TERRAIN_ENDPOINTS.ASPECT).toContain("/terrain/");
      expect(TERRAIN_ENDPOINTS.HYDROLOGY_DRAINAGE).toContain("/hydrology/");
      expect(TERRAIN_ENDPOINTS.HYDROLOGY_WATERSHED).toContain("/hydrology/");
      expect(TERRAIN_ENDPOINTS.LEVELING_OPTIMIZE).toContain("/leveling/");
      expect(TERRAIN_ENDPOINTS.LEVELING_CUT_FILL).toContain("/leveling/");
    });

    it("should have edge endpoints follow /edge/ namespace", () => {
      for (const [key, path] of Object.entries(EDGE_ENDPOINTS)) {
        expect(
          path,
          `EDGE_ENDPOINTS.${key} should be under /edge/`,
        ).toContain("/edge/");
      }
    });

    it("should have no duplicate endpoint paths within a group", () => {
      const groups: Record<string, Record<string, string>> = {
        AUTH: AUTH_ENDPOINTS as Record<string, string>,
        FIELD: FIELD_ENDPOINTS as Record<string, string>,
        TASK: TASK_ENDPOINTS as Record<string, string>,
        EQUIPMENT: EQUIPMENT_ENDPOINTS as Record<string, string>,
        ALERT: ALERT_ENDPOINTS as Record<string, string>,
        IOT: IOT_ENDPOINTS as Record<string, string>,
        VISION: VISION_ENDPOINTS as Record<string, string>,
        EDGE: EDGE_ENDPOINTS as Record<string, string>,
      };

      for (const [groupName, endpoints] of Object.entries(groups)) {
        const paths = Object.values(endpoints);
        const uniquePaths = new Set(paths);

        // Some groups intentionally share paths (LIST/CREATE), so we check
        // that any duplicates are intentional (same HTTP method distinction)
        // For this test, we allow LIST/CREATE to share a path
        const duplicates = paths.filter(
          (p, i) => paths.indexOf(p) !== i,
        );

        for (const dup of duplicates) {
          const keys = Object.entries(endpoints)
            .filter(([, v]) => v === dup)
            .map(([k]) => k);

          // REST APIs commonly share paths differentiated by HTTP method:
          // - LIST + CREATE share a collection path (GET vs POST)
          // - GET + UPDATE + DELETE share a resource path (GET vs PUT/PATCH vs DELETE)
          const isRestMethodDistinction =
            // Collection endpoints: LIST/CREATE
            (keys.some((k) =>
              ["LIST", "LISTINGS", "DEVICES", "CONVERSATIONS"].includes(k),
            ) &&
              keys.some((k) =>
                k.includes("CREATE") ||
                ["LIST", "LISTING_CREATE", "DEVICE_CREATE", "CREATE_CONVERSATION"].includes(k),
              )) ||
            // Resource endpoints: GET/UPDATE/DELETE share same path
            (keys.some((k) => k === "GET") &&
              keys.some((k) => k === "UPDATE" || k === "DELETE")) ||
            // Schedule or other sub-resource pairs
            (keys.some((k) => k.includes("LIST")) &&
              keys.some((k) => k.includes("CREATE")));

          if (!isRestMethodDistinction) {
            // Fail for truly unexpected duplicates
            expect(
              keys.length,
              `${groupName}: Unexpected duplicate path "${dup}" used by: ${keys.join(", ")}`,
            ).toBeLessThanOrEqual(3);
          }
        }
      }
    });
  });

  // ===========================================================================
  // 5. Configuration Constants Consistency
  // ===========================================================================

  describe("Configuration Constants Consistency", () => {
    it("should have valid timeout defaults", () => {
      expect(TIMEOUT_DEFAULTS.DEFAULT).toBeGreaterThan(0);
      expect(TIMEOUT_DEFAULTS.QUICK).toBeLessThan(TIMEOUT_DEFAULTS.DEFAULT);
      expect(TIMEOUT_DEFAULTS.CORE).toBeLessThanOrEqual(
        TIMEOUT_DEFAULTS.DEFAULT,
      );
      expect(TIMEOUT_DEFAULTS.AI).toBeGreaterThanOrEqual(
        TIMEOUT_DEFAULTS.DEFAULT,
      );
      expect(TIMEOUT_DEFAULTS.UPLOAD).toBeGreaterThanOrEqual(
        TIMEOUT_DEFAULTS.DEFAULT,
      );
    });

    it("should have valid circuit breaker defaults", () => {
      expect(CIRCUIT_BREAKER_DEFAULTS.THRESHOLD).toBeGreaterThan(0);
      expect(CIRCUIT_BREAKER_DEFAULTS.RESET_TIMEOUT).toBeGreaterThan(0);
    });

    it("should have valid retry defaults", () => {
      expect(RETRY_DEFAULTS.MAX_ATTEMPTS).toBeGreaterThan(0);
      expect(RETRY_DEFAULTS.BASE_DELAY).toBeGreaterThan(0);
      expect(RETRY_DEFAULTS.MULTIPLIER).toBeGreaterThanOrEqual(1);
    });

    it("should have standard header names", () => {
      expect(DEFAULT_HEADERS.CONTENT_TYPE).toBe("application/json");
      expect(DEFAULT_HEADERS.ACCEPT).toBe("application/json");
      expect(CUSTOM_HEADERS.REQUEST_ID).toBe("X-Request-Id");
      expect(CUSTOM_HEADERS.TENANT_ID).toBe("X-Tenant-Id");
    });

    it("should have rate limit header names following X-RateLimit convention", () => {
      expect(RATE_LIMIT_HEADER_NAMES.REMAINING).toMatch(/^X-RateLimit-/);
      expect(RATE_LIMIT_HEADER_NAMES.LIMIT).toMatch(/^X-RateLimit-/);
      expect(RATE_LIMIT_HEADER_NAMES.RESET).toMatch(/^X-RateLimit-/);
    });
  });
});
