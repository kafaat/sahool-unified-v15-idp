/**
 * اختبارات حراس مصادقة الخدمات
 * Service Authentication Guards Tests
 *
 * Comprehensive tests for ServiceAuthGuard and OptionalServiceAuthGuard
 *
 * Tests service-to-service authentication guards for:
 * - Token validation
 * - Service authorization
 * - Allowed services checking
 * - Target service verification
 * - Optional authentication
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import {
  ServiceAuthGuard,
  OptionalServiceAuthGuard,
  AllowedServices,
  CurrentService,
  ServiceInfo,
  CallingService,
} from "../service-auth.guard";
import * as serviceAuth from "../service_auth";

// ─────────────────────────────────────────────────────────────────────────────
// Mock Setup
// ─────────────────────────────────────────────────────────────────────────────

const createMockExecutionContext = (options: {
  headers?: Record<string, string>;
  params?: any;
  url?: string;
  method?: string;
}): ExecutionContext => {
  const request = {
    headers: options.headers || {},
    params: options.params || {},
    url: options.url || "/test",
    method: options.method || "GET",
    serviceInfo: undefined as any,
    isServiceRequest: undefined as any,
  };

  return {
    switchToHttp: () => ({
      getRequest: () => request,
    }),
    getHandler: () => ({}),
    getClass: () => ({}),
  } as unknown as ExecutionContext;
};

const createValidServiceToken = (
  serviceName: string = "farm-service",
  targetService: string = "field-service",
): string => {
  return "valid.service.token";
};

const mockServiceTokenPayload = (
  serviceName: string = "farm-service",
  targetService: string = "field-service",
): serviceAuth.ServiceTokenPayload => ({
  service_name: serviceName,
  target_service: targetService,
  jti: "test-jti-123",
  exp: new Date(Date.now() + 300000),
  iat: new Date(),
});

// ─────────────────────────────────────────────────────────────────────────────
// ServiceAuthGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("ServiceAuthGuard", () => {
  let guard: ServiceAuthGuard;
  let reflector: Reflector;
  let verifyServiceTokenSpy: any;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new ServiceAuthGuard(reflector, "field-service");

    // Mock verifyServiceToken function
    verifyServiceTokenSpy = vi
      .spyOn(serviceAuth, "verifyServiceToken")
      .mockReturnValue(mockServiceTokenPayload("farm-service", "field-service"));
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Basic Token Validation Tests
  // ───────────────────────────────────────────────────────────────────────────

  describe("Token Validation", () => {
    it("should allow valid service token", async () => {
      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
      expect(verifyServiceTokenSpy).toHaveBeenCalledWith(
        createValidServiceToken(),
      );
    });

    it("should throw UnauthorizedException when service token is missing", async () => {
      const context = createMockExecutionContext({
        headers: {},
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(guard.canActivate(context)).rejects.toThrow(
        "Service authentication token is required",
      );
    });

    it("should throw UnauthorizedException when token is empty string", async () => {
      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "",
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        UnauthorizedException,
      );
    });

    it("should throw UnauthorizedException when token verification fails", async () => {
      verifyServiceTokenSpy.mockImplementation(() => {
        throw new serviceAuth.ServiceAuthException(
          serviceAuth.ServiceAuthErrors.INVALID_SERVICE_TOKEN,
        );
      });

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "invalid.token",
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        UnauthorizedException,
      );
    });

    it("should throw UnauthorizedException for malformed token", async () => {
      verifyServiceTokenSpy.mockImplementation(() => {
        throw new Error("Malformed token");
      });

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "malformed.token",
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        UnauthorizedException,
      );
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Target Service Validation Tests
  // ───────────────────────────────────────────────────────────────────────────

  describe("Target Service Validation", () => {
    it("should allow when target service matches current service", async () => {
      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(
            "farm-service",
            "field-service",
          ),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should throw ForbiddenException when target service does not match", async () => {
      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "other-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        ForbiddenException,
      );
    });

    it("should use service name from SERVICE_NAME environment variable", async () => {
      const originalEnv = process.env.SERVICE_NAME;
      process.env.SERVICE_NAME = "crop-service";

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "crop-service"),
      );

      const guardWithoutConstructorArg = new ServiceAuthGuard(reflector);

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guardWithoutConstructorArg.canActivate(context);

      expect(result).toBe(true);

      // Restore
      process.env.SERVICE_NAME = originalEnv;
    });

    it("should use service name from @CurrentService decorator", async () => {
      vi.spyOn(reflector, "get").mockImplementation((key, target) => {
        if (key === "current_service") {
          return "custom-service";
        }
        return undefined;
      });

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "custom-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should throw error when current service is not configured", async () => {
      const originalEnv = process.env.SERVICE_NAME;
      delete process.env.SERVICE_NAME;

      const guardWithoutConfig = new ServiceAuthGuard(reflector);

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      await expect(guardWithoutConfig.canActivate(context)).rejects.toThrow(
        "Current service name not configured",
      );

      // Restore
      process.env.SERVICE_NAME = originalEnv;
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Allowed Services Tests
  // ───────────────────────────────────────────────────────────────────────────

  describe("Allowed Services", () => {
    it("should allow any service when no allowed services specified", async () => {
      vi.spyOn(reflector, "get").mockReturnValue(undefined);

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("any-service", "field-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should allow service in allowed services list", async () => {
      vi.spyOn(reflector, "get").mockImplementation((key, target) => {
        if (key === "allowed_services") {
          return ["farm-service", "crop-service"];
        }
        return undefined;
      });

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "field-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should throw ForbiddenException for service not in allowed list", async () => {
      vi.spyOn(reflector, "get").mockImplementation((key, target) => {
        if (key === "allowed_services") {
          return ["crop-service", "weather-service"];
        }
        return undefined;
      });

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "field-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        ForbiddenException,
      );
      await expect(guard.canActivate(context)).rejects.toThrow(
        "not allowed to call this endpoint",
      );
    });

    it("should check allowed services at handler level first", async () => {
      const handlerServices = ["farm-service"];
      const classServices = ["crop-service"];

      vi.spyOn(reflector, "get").mockImplementation((key, target) => {
        if (key === "allowed_services") {
          // Return handler-level services first
          return target === context.getHandler()
            ? handlerServices
            : classServices;
        }
        return undefined;
      });

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "field-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Request Metadata Tests
  // ───────────────────────────────────────────────────────────────────────────

  describe("Request Metadata", () => {
    it("should attach serviceInfo to request", async () => {
      const payload = mockServiceTokenPayload("farm-service", "field-service");
      verifyServiceTokenSpy.mockReturnValue(payload);

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      await guard.canActivate(context);

      const request = context.switchToHttp().getRequest();
      expect(request.serviceInfo).toEqual(payload);
    });

    it("should set isServiceRequest to true", async () => {
      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      await guard.canActivate(context);

      const request = context.switchToHttp().getRequest();
      expect(request.isServiceRequest).toBe(true);
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Error Handling Tests
  // ───────────────────────────────────────────────────────────────────────────

  describe("Error Handling", () => {
    it("should handle ServiceAuthException properly", async () => {
      const authException = new serviceAuth.ServiceAuthException(
        serviceAuth.ServiceAuthErrors.INVALID_SERVICE,
      );

      verifyServiceTokenSpy.mockImplementation(() => {
        throw authException;
      });

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "invalid.token",
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        UnauthorizedException,
      );
    });

    it("should rethrow UnauthorizedException as-is", async () => {
      const unauthorizedException = new UnauthorizedException(
        "Custom unauthorized",
      );

      verifyServiceTokenSpy.mockImplementation(() => {
        throw unauthorizedException;
      });

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "invalid.token",
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        unauthorizedException,
      );
    });

    it("should rethrow ForbiddenException as-is", async () => {
      const forbiddenException = new ForbiddenException("Custom forbidden");

      verifyServiceTokenSpy.mockImplementation(() => {
        throw forbiddenException;
      });

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "invalid.token",
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        forbiddenException,
      );
    });

    it("should wrap generic errors in UnauthorizedException", async () => {
      verifyServiceTokenSpy.mockImplementation(() => {
        throw new Error("Some generic error");
      });

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "invalid.token",
        },
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        UnauthorizedException,
      );
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// OptionalServiceAuthGuard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("OptionalServiceAuthGuard", () => {
  let guard: OptionalServiceAuthGuard;
  let reflector: Reflector;
  let verifyServiceTokenSpy: any;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new OptionalServiceAuthGuard(reflector, "field-service");

    verifyServiceTokenSpy = vi
      .spyOn(serviceAuth, "verifyServiceToken")
      .mockReturnValue(mockServiceTokenPayload("farm-service", "field-service"));
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Optional Authentication Tests
  // ───────────────────────────────────────────────────────────────────────────

  describe("Optional Authentication", () => {
    it("should allow request without service token", async () => {
      const context = createMockExecutionContext({
        headers: {},
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
      expect(verifyServiceTokenSpy).not.toHaveBeenCalled();
    });

    it("should validate and attach serviceInfo when token is present", async () => {
      const payload = mockServiceTokenPayload("farm-service", "field-service");
      verifyServiceTokenSpy.mockReturnValue(payload);

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
      expect(verifyServiceTokenSpy).toHaveBeenCalled();

      const request = context.switchToHttp().getRequest();
      expect(request.serviceInfo).toEqual(payload);
      expect(request.isServiceRequest).toBe(true);
    });

    it("should allow request even if token verification fails", async () => {
      verifyServiceTokenSpy.mockImplementation(() => {
        throw new Error("Invalid token");
      });

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": "invalid.token",
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should allow request when target service does not match", async () => {
      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "other-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should allow request when current service is not configured", async () => {
      const originalEnv = process.env.SERVICE_NAME;
      delete process.env.SERVICE_NAME;

      const guardWithoutConfig = new OptionalServiceAuthGuard(reflector);

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guardWithoutConfig.canActivate(context);

      expect(result).toBe(true);

      // Restore
      process.env.SERVICE_NAME = originalEnv;
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Valid Token Handling Tests
  // ───────────────────────────────────────────────────────────────────────────

  describe("Valid Token Handling", () => {
    it("should validate token when current service matches", async () => {
      const payload = mockServiceTokenPayload("farm-service", "field-service");
      verifyServiceTokenSpy.mockReturnValue(payload);

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);

      const request = context.switchToHttp().getRequest();
      expect(request.serviceInfo).toEqual(payload);
      expect(request.isServiceRequest).toBe(true);
    });

    it("should use service name from @CurrentService decorator", async () => {
      vi.spyOn(reflector, "get").mockImplementation((key, target) => {
        if (key === "current_service") {
          return "custom-service";
        }
        return undefined;
      });

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "custom-service"),
      );

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guard.canActivate(context);

      expect(result).toBe(true);

      const request = context.switchToHttp().getRequest();
      expect(request.isServiceRequest).toBe(true);
    });

    it("should use service name from SERVICE_NAME environment variable", async () => {
      const originalEnv = process.env.SERVICE_NAME;
      process.env.SERVICE_NAME = "env-service";

      verifyServiceTokenSpy.mockReturnValue(
        mockServiceTokenPayload("farm-service", "env-service"),
      );

      const guardWithEnvConfig = new OptionalServiceAuthGuard(reflector);

      const context = createMockExecutionContext({
        headers: {
          "x-service-token": createValidServiceToken(),
        },
      });

      const result = await guardWithEnvConfig.canActivate(context);

      expect(result).toBe(true);

      // Restore
      process.env.SERVICE_NAME = originalEnv;
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Decorator Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("Service Auth Decorators", () => {
  describe("@AllowedServices", () => {
    it("should set metadata for allowed services", () => {
      const decorator = AllowedServices("farm-service", "crop-service");
      expect(decorator).toBeDefined();
    });
  });

  describe("@CurrentService", () => {
    it("should set metadata for current service", () => {
      const decorator = CurrentService("field-service");
      expect(decorator).toBeDefined();
    });
  });

  describe("@ServiceInfo", () => {
    it("should extract service info from request", () => {
      const mockPayload = mockServiceTokenPayload();
      const context = createMockExecutionContext({
        headers: {},
      });

      const request = context.switchToHttp().getRequest();
      request.serviceInfo = mockPayload;

      // Create parameter decorator execution context
      const paramContext = {
        switchToHttp: () => ({
          getRequest: () => request,
        }),
      } as ExecutionContext;

      const result = ServiceInfo(undefined, paramContext);

      expect(result).toEqual(mockPayload);
    });
  });

  describe("@CallingService", () => {
    it("should extract calling service name from request", () => {
      const mockPayload = mockServiceTokenPayload("farm-service");
      const context = createMockExecutionContext({
        headers: {},
      });

      const request = context.switchToHttp().getRequest();
      request.serviceInfo = mockPayload;

      // Create parameter decorator execution context
      const paramContext = {
        switchToHttp: () => ({
          getRequest: () => request,
        }),
      } as ExecutionContext;

      const result = CallingService(undefined, paramContext);

      expect(result).toBe("farm-service");
    });

    it("should return undefined when serviceInfo is not present", () => {
      const context = createMockExecutionContext({
        headers: {},
      });

      const request = context.switchToHttp().getRequest();

      // Create parameter decorator execution context
      const paramContext = {
        switchToHttp: () => ({
          getRequest: () => request,
        }),
      } as ExecutionContext;

      const result = CallingService(undefined, paramContext);

      expect(result).toBeUndefined();
    });
  });
});
