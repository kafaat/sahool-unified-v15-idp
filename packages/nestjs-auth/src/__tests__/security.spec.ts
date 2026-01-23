/**
 * Comprehensive Security Tests for NestJS Auth Module
 * اختبارات الأمان الشاملة لوحدة مصادقة NestJS
 *
 * Tests security features including:
 * - Token type validation
 * - JTI enforcement
 * - Secret key validation
 * - All roles/permissions guards
 * - Fingerprint validation
 * - Rate limiting
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";

// ─────────────────────────────────────────────────────────────────────────────
// JWTConfig Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("JWTConfig Security", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe("validate", () => {
    it("should throw error when secret is missing in production", async () => {
      process.env.NODE_ENV = "production";
      process.env.JWT_SECRET_KEY = "";

      const { JWTConfig } = await import("../config/jwt.config");

      expect(() => JWTConfig.validate()).toThrow(
        /JWT_SECRET_KEY or JWT_SECRET environment variable is required/,
      );
    });

    it("should throw error when secret is too short in production", async () => {
      process.env.NODE_ENV = "production";
      process.env.JWT_SECRET_KEY = "short-secret";

      const { JWTConfig } = await import("../config/jwt.config");

      expect(() => JWTConfig.validate()).toThrow(/at least 32 characters/);
    });

    it("should throw error for weak secrets in production", async () => {
      process.env.NODE_ENV = "production";
      process.env.JWT_SECRET_KEY =
        "this-is-a-secret-that-contains-password-in-it";

      const { JWTConfig } = await import("../config/jwt.config");

      expect(() => JWTConfig.validate()).toThrow(/weak patterns/);
    });

    it("should pass validation with strong secret", async () => {
      process.env.NODE_ENV = "production";
      process.env.JWT_SECRET_KEY =
        "a-very-long-and-random-32char-plus-extra-characters";

      const { JWTConfig } = await import("../config/jwt.config");

      expect(() => JWTConfig.validate()).not.toThrow();
    });
  });

  describe("getVerificationKey", () => {
    it("should return secret key when configured", async () => {
      process.env.JWT_SECRET_KEY = "test-secret-key-for-testing-purposes";

      const { JWTConfig } = await import("../config/jwt.config");

      expect(JWTConfig.getVerificationKey()).toBe(
        "test-secret-key-for-testing-purposes",
      );
    });

    it("should throw error when secret is not configured", async () => {
      process.env.JWT_SECRET_KEY = "";
      process.env.JWT_SECRET = "";

      // Force reload module
      vi.resetModules();
      const { JWTConfig } = await import("../config/jwt.config");

      expect(() => JWTConfig.getVerificationKey()).toThrow(/not configured/);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// All Roles Guard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("AllRolesGuard Security", () => {
  let guard: any;
  let reflector: Reflector;

  const createMockContext = (user: any): ExecutionContext => {
    return {
      switchToHttp: () => ({
        getRequest: () => ({ user }),
      }),
      getHandler: () => ({}),
      getClass: () => ({}),
    } as unknown as ExecutionContext;
  };

  beforeEach(async () => {
    reflector = new Reflector();
    const { AllRolesGuard } = await import("../guards/jwt.guard");
    guard = new AllRolesGuard(reflector);
  });

  it("should require ALL roles (AND logic)", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue([
      "admin",
      "verified",
    ]);

    // User has only admin role - should fail
    const context = createMockContext({
      id: "1",
      roles: ["admin"],
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should allow when user has all required roles", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue([
      "admin",
      "verified",
    ]);

    const context = createMockContext({
      id: "1",
      roles: ["admin", "verified", "extra"],
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it("should deny when user has no roles", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue(["admin"]);

    const context = createMockContext({
      id: "1",
      roles: [],
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// All Permissions Guard Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("AllPermissionsGuard Security", () => {
  let guard: any;
  let reflector: Reflector;

  const createMockContext = (user: any): ExecutionContext => {
    return {
      switchToHttp: () => ({
        getRequest: () => ({ user }),
      }),
      getHandler: () => ({}),
      getClass: () => ({}),
    } as unknown as ExecutionContext;
  };

  beforeEach(async () => {
    reflector = new Reflector();
    const { AllPermissionsGuard } = await import("../guards/jwt.guard");
    guard = new AllPermissionsGuard(reflector);
  });

  it("should require ALL permissions (AND logic)", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue([
      "farm:read",
      "farm:write",
    ]);

    // User has only read permission - should fail
    const context = createMockContext({
      id: "1",
      permissions: ["farm:read"],
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should allow when user has all required permissions", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue([
      "farm:read",
      "farm:write",
    ]);

    const context = createMockContext({
      id: "1",
      permissions: ["farm:read", "farm:write", "farm:delete"],
    });

    expect(guard.canActivate(context)).toBe(true);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Token Fingerprint Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("TokenFingerprintService Security", () => {
  let service: any;

  beforeEach(async () => {
    const { TokenFingerprintService } = await import(
      "../services/token-fingerprint.service"
    );
    service = new TokenFingerprintService({
      includeUserAgent: true,
      includeClientId: true,
      strictValidation: true,
    });
  });

  it("should generate consistent fingerprints for same input", () => {
    const components = {
      userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      clientId: "device-123",
    };

    const fp1 = service.generateFingerprint(components);
    const fp2 = service.generateFingerprint(components);

    expect(fp1).toBe(fp2);
    expect(fp1.length).toBe(32);
  });

  it("should generate different fingerprints for different inputs", () => {
    const fp1 = service.generateFingerprint({
      userAgent: "Mozilla/5.0 (Windows)",
      clientId: "device-123",
    });

    const fp2 = service.generateFingerprint({
      userAgent: "Mozilla/5.0 (Mac)",
      clientId: "device-123",
    });

    expect(fp1).not.toBe(fp2);
  });

  it("should validate matching fingerprints", () => {
    const components = {
      userAgent: "Mozilla/5.0 (Windows NT 10.0)",
      clientId: "device-abc",
    };

    const fingerprint = service.generateFingerprint(components);
    const result = service.validateFingerprint(fingerprint, components);

    expect(result.isValid).toBe(true);
  });

  it("should reject non-matching fingerprints in strict mode", () => {
    const fingerprint = service.generateFingerprint({
      userAgent: "Mozilla/5.0 (Windows)",
      clientId: "device-123",
    });

    const result = service.validateFingerprint(fingerprint, {
      userAgent: "Mozilla/5.0 (Mac)",
      clientId: "device-123",
    });

    expect(result.isValid).toBe(false);
    expect(result.reason).toBe("fingerprint_mismatch");
  });

  it("should allow missing fingerprint for backward compatibility", () => {
    const result = service.validateFingerprint(undefined, {
      userAgent: "Mozilla/5.0",
    });

    expect(result.isValid).toBe(true);
  });

  it("should extract components from request", () => {
    const mockRequest = {
      headers: {
        "user-agent": "Mozilla/5.0 Test",
        "accept-language": "en-US",
        "x-client-id": "test-device",
      },
      ip: "192.168.1.1",
    };

    const components = service.extractFromRequest(mockRequest);

    expect(components.userAgent).toBe("Mozilla/5.0 Test");
    expect(components.clientId).toBe("test-device");
    expect(components.clientIp).toBe("192.168.1.1");
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Security Audit Service Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("SecurityAuditService", () => {
  let service: any;

  beforeEach(async () => {
    const { SecurityAuditService } = await import(
      "../services/security-audit.service"
    );
    service = new SecurityAuditService();
  });

  it("should log authentication success", () => {
    const logSpy = vi.spyOn(service, "log");

    service.logAuthSuccess("user-123", {
      tenantId: "tenant-1",
      path: "/api/v1/protected",
    });

    expect(logSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "auth.success",
        userId: "user-123",
        tenantId: "tenant-1",
      }),
    );
  });

  it("should log authentication failure", () => {
    const logSpy = vi.spyOn(service, "log");

    service.logAuthFailure("invalid_token", {
      userId: "user-123",
      clientIp: "192.168.1.1",
    });

    expect(logSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "auth.failure",
        severity: "warning",
      }),
    );
  });

  it("should log brute force attempts as critical", () => {
    const logSpy = vi.spyOn(service, "log");

    service.logBruteForceAttempt("192.168.1.100", 50, {
      timeWindow: 300,
    });

    expect(logSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "security.brute_force_attempt",
        severity: "critical",
        clientIp: "192.168.1.100",
      }),
    );
  });

  it("should extract request metadata correctly", () => {
    const mockRequest = {
      url: "/api/v1/test",
      method: "POST",
      ip: "10.0.0.1",
      headers: {
        "user-agent": "Test Agent",
        "x-request-id": "req-123",
      },
    };

    const metadata = service.extractRequestMetadata(mockRequest);

    expect(metadata.path).toBe("/api/v1/test");
    expect(metadata.method).toBe("POST");
    expect(metadata.clientIp).toBe("10.0.0.1");
    expect(metadata.requestId).toBe("req-123");
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Rate Limiting Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("RateLimitGuard Security", () => {
  let guard: any;
  let reflector: Reflector;

  const createMockContext = (
    request: any,
    response: any = {},
  ): ExecutionContext => {
    return {
      switchToHttp: () => ({
        getRequest: () => request,
        getResponse: () => ({
          setHeader: vi.fn(),
          ...response,
        }),
      }),
      getHandler: () => ({}),
      getClass: () => ({}),
    } as unknown as ExecutionContext;
  };

  beforeEach(async () => {
    reflector = new Reflector();
    const { RateLimitGuard } = await import("../guards/rate-limit.guard");
    guard = new RateLimitGuard(reflector);
  });

  afterEach(() => {
    guard.onModuleDestroy();
  });

  it("should allow requests within rate limit", async () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue({
      limit: 5,
      windowSeconds: 60,
    });

    const context = createMockContext({
      ip: "192.168.1.1",
      url: "/api/test",
    });

    // First request should pass
    const result = await guard.canActivate(context);
    expect(result).toBe(true);
  });

  it("should set rate limit headers", async () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue({
      limit: 5,
      windowSeconds: 60,
    });

    const setHeaderMock = vi.fn();
    const context = createMockContext(
      { ip: "192.168.1.2", url: "/api/test" },
      { setHeader: setHeaderMock },
    );

    await guard.canActivate(context);

    expect(setHeaderMock).toHaveBeenCalledWith("X-RateLimit-Limit", 5);
    expect(setHeaderMock).toHaveBeenCalledWith(
      "X-RateLimit-Remaining",
      expect.any(Number),
    );
  });

  it("should block requests exceeding rate limit", async () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue({
      limit: 2,
      windowSeconds: 60,
    });

    const context = createMockContext({
      ip: "192.168.1.3",
      url: "/api/limited",
    });

    // First two requests should pass
    await guard.canActivate(context);
    await guard.canActivate(context);

    // Third request should be blocked
    await expect(guard.canActivate(context)).rejects.toMatchObject({
      status: 429,
    });
  });

  it("should use different keys for different IPs", async () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue({
      limit: 1,
      windowSeconds: 60,
    });

    const context1 = createMockContext({
      ip: "192.168.1.10",
      url: "/api/test",
    });

    const context2 = createMockContext({
      ip: "192.168.1.11",
      url: "/api/test",
    });

    // Both should pass (different IPs)
    await expect(guard.canActivate(context1)).resolves.toBe(true);
    await expect(guard.canActivate(context2)).resolves.toBe(true);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Decorator Helper Functions Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("Auth Decorator Helpers", () => {
  describe("hasAllRoles", () => {
    it("should return true when user has all roles", async () => {
      const { hasAllRoles } = await import("../decorators");

      const user = { roles: ["admin", "verified", "premium"] };
      expect(hasAllRoles(user, ["admin", "verified"])).toBe(true);
    });

    it("should return false when user is missing any role", async () => {
      const { hasAllRoles } = await import("../decorators");

      const user = { roles: ["admin"] };
      expect(hasAllRoles(user, ["admin", "verified"])).toBe(false);
    });

    it("should return false for null user", async () => {
      const { hasAllRoles } = await import("../decorators");

      expect(hasAllRoles(null, ["admin"])).toBe(false);
    });
  });

  describe("hasAllPermissions", () => {
    it("should return true when user has all permissions", async () => {
      const { hasAllPermissions } = await import("../decorators");

      const user = { permissions: ["farm:read", "farm:write", "farm:delete"] };
      expect(hasAllPermissions(user, ["farm:read", "farm:write"])).toBe(true);
    });

    it("should return false when user is missing any permission", async () => {
      const { hasAllPermissions } = await import("../decorators");

      const user = { permissions: ["farm:read"] };
      expect(hasAllPermissions(user, ["farm:read", "farm:write"])).toBe(false);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Token Revocation Fail-Closed Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("Token Revocation Fail-Closed Behavior", () => {
  it("should deny access when Redis fails (fail-closed)", async () => {
    // This test verifies the critical security fix:
    // Token revocation checks should fail closed, not fail open

    const mockRevocationStore = {
      isRevoked: vi.fn().mockRejectedValue(new Error("Redis connection failed")),
    };

    const mockJwtService = {
      decode: vi.fn().mockReturnValue({
        sub: "user-123",
        jti: "token-456",
        iat: Date.now() / 1000,
      }),
    };

    const reflector = new Reflector();
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue(false);

    const { TokenRevocationGuard } = await import(
      "../guards/token-revocation.guard"
    );

    const guard = new TokenRevocationGuard(
      mockRevocationStore as any,
      mockJwtService as any,
      reflector,
    );

    const context = {
      switchToHttp: () => ({
        getRequest: () => ({
          headers: {
            authorization: "Bearer valid.jwt.token",
          },
        }),
      }),
      getHandler: () => ({}),
      getClass: () => ({}),
    } as unknown as ExecutionContext;

    // Should throw UnauthorizedException due to fail-closed behavior
    await expect(guard.canActivate(context)).rejects.toThrow(
      UnauthorizedException,
    );
  });
});
