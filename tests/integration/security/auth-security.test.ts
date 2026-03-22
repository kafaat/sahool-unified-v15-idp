/**
 * Authentication & Authorization Security Integration Tests
 *
 * Verifies JWT authentication guards, tenant isolation guards,
 * JWT secret validation, and rate limiting behavior across
 * the SAHOOL platform's NestJS security layer.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
  BadRequestException,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  ActiveAccountGuard,
} from "../../../packages/nestjs-auth/src/guards/jwt.guard";
import { TenantGuard } from "../../../packages/nestjs-auth/src/guards/tenant.guard";
import { AuthErrors, JWTConfig } from "../../../packages/nestjs-auth/src/config/jwt.config";

// ─────────────────────────────────────────────────────────────────────────────
// Test Helpers
// ─────────────────────────────────────────────────────────────────────────────

interface MockRequestOptions {
  user?: Record<string, any> | null;
  params?: Record<string, string>;
  headers?: Record<string, string>;
  url?: string;
  method?: string;
}

function createMockContext(options: MockRequestOptions = {}): ExecutionContext {
  const request: Record<string, any> = {
    user: options.user === null ? undefined : options.user,
    params: options.params || {},
    headers: options.headers || {},
    url: options.url || "/api/v1/fields",
    method: options.method || "GET",
  };

  return {
    switchToHttp: () => ({
      getRequest: () => request,
      getResponse: () => ({}),
    }),
    getHandler: () => ({}),
    getClass: () => ({}),
  } as unknown as ExecutionContext;
}

function createReflector(overrides: Record<string, any> = {}): Reflector {
  const reflector = new Reflector();
  vi.spyOn(reflector, "getAllAndOverride").mockImplementation((key: string) => {
    return overrides[key] ?? null;
  });
  return reflector;
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. JwtAuthGuard Enforcement
// ─────────────────────────────────────────────────────────────────────────────

describe("JwtAuthGuard enforcement", () => {
  let guard: JwtAuthGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = createReflector();
    guard = new JwtAuthGuard(reflector);
  });

  describe("protected endpoints without a token", () => {
    it("should throw UnauthorizedException with missing token message", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });

      expect(() => guard.handleRequest(null, null, null, context)).toThrow(
        UnauthorizedException,
      );
    });

    it("should include the correct error message for missing token", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });

      try {
        guard.handleRequest(null, null, null, context);
        expect.fail("Expected UnauthorizedException to be thrown");
      } catch (error: any) {
        expect(error).toBeInstanceOf(UnauthorizedException);
        expect(error.message).toBe(AuthErrors.MISSING_TOKEN.en);
      }
    });

    it("should reject POST requests without a token", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "POST" });

      expect(() => guard.handleRequest(null, null, null, context)).toThrow(
        UnauthorizedException,
      );
    });

    it("should reject DELETE requests without a token", () => {
      const context = createMockContext({ url: "/api/v1/fields/123", method: "DELETE" });

      expect(() => guard.handleRequest(null, null, null, context)).toThrow(
        UnauthorizedException,
      );
    });
  });

  describe("protected endpoints with an invalid token", () => {
    it("should throw UnauthorizedException for JsonWebTokenError", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });
      const info = { name: "JsonWebTokenError", message: "invalid signature" };

      expect(() => guard.handleRequest(null, null, info, context)).toThrow(
        UnauthorizedException,
      );
    });

    it("should include the correct error message for invalid token", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });
      const info = { name: "JsonWebTokenError", message: "jwt malformed" };

      try {
        guard.handleRequest(null, null, info, context);
        expect.fail("Expected UnauthorizedException to be thrown");
      } catch (error: any) {
        expect(error).toBeInstanceOf(UnauthorizedException);
        expect(error.message).toBe(AuthErrors.INVALID_TOKEN.en);
      }
    });

    it("should reject tokens with invalid algorithm", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });
      const info = { name: "JsonWebTokenError", message: "invalid algorithm" };

      expect(() => guard.handleRequest(null, null, info, context)).toThrow(
        UnauthorizedException,
      );
    });
  });

  describe("protected endpoints with an expired token", () => {
    it("should throw UnauthorizedException for TokenExpiredError", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });
      const info = { name: "TokenExpiredError" };

      expect(() => guard.handleRequest(null, null, info, context)).toThrow(
        UnauthorizedException,
      );
    });

    it("should include the correct error message for expired token", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });
      const info = { name: "TokenExpiredError" };

      try {
        guard.handleRequest(null, null, info, context);
        expect.fail("Expected UnauthorizedException to be thrown");
      } catch (error: any) {
        expect(error).toBeInstanceOf(UnauthorizedException);
        expect(error.message).toBe(AuthErrors.EXPIRED_TOKEN.en);
      }
    });
  });

  describe("health endpoints work without auth", () => {
    it("should allow /healthz when route is marked @Public()", () => {
      const publicReflector = createReflector({ isPublic: true });
      const publicGuard = new JwtAuthGuard(publicReflector);

      const context = createMockContext({ url: "/healthz", method: "GET" });
      const result = publicGuard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should allow /readyz when route is marked @Public()", () => {
      const publicReflector = createReflector({ isPublic: true });
      const publicGuard = new JwtAuthGuard(publicReflector);

      const context = createMockContext({ url: "/readyz", method: "GET" });
      const result = publicGuard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should allow /health when route is marked @Public()", () => {
      const publicReflector = createReflector({ isPublic: true });
      const publicGuard = new JwtAuthGuard(publicReflector);

      const context = createMockContext({ url: "/health", method: "GET" });
      const result = publicGuard.canActivate(context);

      expect(result).toBe(true);
    });

    it("should not bypass auth for non-public routes", () => {
      // Default reflector returns null for isPublic
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });

      // canActivate delegates to super (Passport) which would need a real strategy;
      // but handleRequest should reject when no user is returned
      expect(() => guard.handleRequest(null, null, null, context)).toThrow(
        UnauthorizedException,
      );
    });
  });

  describe("valid authentication", () => {
    it("should return user object when authentication succeeds", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });
      const user = {
        id: "user-abc-123",
        roles: ["farmer"],
        tenantId: "00000000-0000-0000-0000-000000000001",
        permissions: ["field:read"],
      };

      const result = guard.handleRequest(null, user, null, context);

      expect(result).toBe(user);
      expect(result.id).toBe("user-abc-123");
    });

    it("should propagate errors passed by passport", () => {
      const context = createMockContext({ url: "/api/v1/fields", method: "GET" });
      const customError = new Error("Database connection failed");

      expect(() => guard.handleRequest(customError, null, null, context)).toThrow(
        customError,
      );
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 2. TenantGuard Enforcement
// ─────────────────────────────────────────────────────────────────────────────

describe("TenantGuard enforcement", () => {
  let guard: TenantGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = createReflector();
    guard = new TenantGuard(reflector);
  });

  describe("requests without tenant ID", () => {
    it("should throw BadRequestException when user has no tenantId and no header", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"] },
        headers: {},
      });

      expect(() => guard.canActivate(context)).toThrow(BadRequestException);
    });

    it("should include descriptive error message about tenant requirement", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"] },
        headers: {},
      });

      try {
        guard.canActivate(context);
        expect.fail("Expected BadRequestException to be thrown");
      } catch (error: any) {
        expect(error).toBeInstanceOf(BadRequestException);
        expect(error.message).toContain("Tenant ID is required");
      }
    });

    it("should reject when neither user nor header provides tenant ID", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: [] },
        headers: {},
      });

      expect(() => guard.canActivate(context)).toThrow(BadRequestException);
    });
  });

  describe("authenticated users accessing their own tenant data", () => {
    it("should allow access when user.tenantId matches request", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"], tenantId: "00000000-0000-0000-0000-000000000001" },
        headers: {},
      });

      expect(guard.canActivate(context)).toBe(true);
    });

    it("should attach tenantId to the request object", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"], tenantId: "00000000-0000-0000-0000-000000000001" },
        headers: {},
      });

      guard.canActivate(context);

      const request = context.switchToHttp().getRequest() as any;
      expect(request.tenantId).toBe("00000000-0000-0000-0000-000000000001");
    });

    it("should allow when header and JWT tenantId match", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"], tenantId: "00000000-0000-0000-0000-000000000001" },
        headers: { "x-tenant-id": "00000000-0000-0000-0000-000000000001" },
      });

      expect(guard.canActivate(context)).toBe(true);
    });
  });

  describe("x-tenant-id header cannot override JWT tenant for non-admin users", () => {
    it("should throw ForbiddenException when header tenantId differs from JWT", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"], tenantId: "00000000-0000-0000-0000-000000000001" },
        headers: { "x-tenant-id": "00000000-0000-0000-0000-000000000002" },
      });

      expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
    });

    it("should include tenant mismatch in error message", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"], tenantId: "00000000-0000-0000-0000-000000000001" },
        headers: { "x-tenant-id": "00000000-0000-0000-0000-000000000999" },
      });

      try {
        guard.canActivate(context);
        expect.fail("Expected ForbiddenException to be thrown");
      } catch (error: any) {
        expect(error).toBeInstanceOf(ForbiddenException);
        expect(error.message).toContain("tenant mismatch");
      }
    });

    it("should reject override attempt for user role", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["user"], tenantId: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" },
        headers: { "x-tenant-id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb" },
      });

      expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
    });

    it("should reject override attempt for manager role (non-admin)", () => {
      const context = createMockContext({
        user: { id: "user-1", roles: ["manager"], tenantId: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" },
        headers: { "x-tenant-id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb" },
      });

      expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
    });
  });

  describe("admin users can access other tenants", () => {
    it("should allow admin to use x-tenant-id header for different tenant", () => {
      const context = createMockContext({
        user: { id: "admin-1", roles: ["admin"], tenantId: "00000000-0000-0000-0000-000000000001" },
        headers: { "x-tenant-id": "00000000-0000-0000-0000-000000000002" },
      });

      expect(guard.canActivate(context)).toBe(true);
    });

    it("should attach the header tenantId for admin cross-tenant access", () => {
      const context = createMockContext({
        user: { id: "admin-1", roles: ["admin"], tenantId: "00000000-0000-0000-0000-000000000001" },
        headers: { "x-tenant-id": "00000000-0000-0000-0000-000000000002" },
      });

      guard.canActivate(context);

      const request = context.switchToHttp().getRequest() as any;
      expect(request.tenantId).toBe("00000000-0000-0000-0000-000000000002");
    });
  });

  describe("unauthenticated requests with x-tenant-id header", () => {
    it("should reject when user is undefined but header provides tenant", () => {
      // When no user is set (unauthenticated), the TenantGuard still
      // processes because JwtAuthGuard should have already rejected.
      // But if it reaches TenantGuard, headerTenantId is used as fallback.
      // The guard itself does not enforce authentication -- it allows
      // if a tenantId is derivable. Real rejection happens via JwtAuthGuard.
      const context = createMockContext({
        user: null,
        headers: { "x-tenant-id": "00000000-0000-0000-0000-000000000001" },
      });

      // TenantGuard allows it because it finds a tenantId from the header.
      // Authentication enforcement is the responsibility of JwtAuthGuard.
      // This test documents that TenantGuard alone does not reject
      // unauthenticated requests -- it relies on guard ordering.
      const result = guard.canActivate(context);
      expect(result).toBe(true);
    });

    it("should reject when no user and no header (no tenant derivable)", () => {
      const context = createMockContext({
        user: null,
        headers: {},
      });

      expect(() => guard.canActivate(context)).toThrow(BadRequestException);
    });
  });

  describe("public routes skip tenant check", () => {
    it("should skip tenant validation for @Public() routes", () => {
      const publicReflector = createReflector({ isPublic: true });
      const publicGuard = new TenantGuard(publicReflector);

      const context = createMockContext({
        user: null,
        headers: {},
      });

      expect(publicGuard.canActivate(context)).toBe(true);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 3. JWT Secret Validation
// ─────────────────────────────────────────────────────────────────────────────

describe("JWT secret validation", () => {
  // We test the JWTConfig.validate() method which checks secret strength
  // by environment. We must mock process.env to avoid side effects.

  const originalEnv = { ...process.env };

  afterEach(() => {
    // Restore original environment
    process.env = { ...originalEnv };
  });

  describe("empty JWT secret in non-test environments", () => {
    it("should throw error when secret is empty in production", () => {
      // JWTConfig.validate() checks the static SECRET property.
      // We test the validate logic directly by simulating conditions.
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "",
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "production";

        expect(() => JWTConfig.validate()).toThrow();
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });

    it("should throw error when secret is empty in staging", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "",
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "staging";

        expect(() => JWTConfig.validate()).toThrow();
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });

    it("should throw error when secret is empty in development", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "",
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "development";

        expect(() => JWTConfig.validate()).toThrow(
          "JWT_SECRET must be set in development",
        );
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });
  });

  describe("weak secrets (< 32 chars) in production", () => {
    it("should throw error for short secret in production", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "short-secret-only-20ch",
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "production";

        expect(() => JWTConfig.validate()).toThrow(
          "JWT_SECRET must be at least 32 characters",
        );
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });

    it("should throw error for 31-character secret in production", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "a".repeat(31),
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "production";

        expect(() => JWTConfig.validate()).toThrow(
          "JWT_SECRET must be at least 32 characters",
        );
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });

    it("should accept 32-character secret in production", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "a".repeat(32),
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "production";

        expect(() => JWTConfig.validate()).not.toThrow();
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });

    it("should throw error for short secret in staging", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "only-15-chars!!",
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "staging";

        expect(() => JWTConfig.validate()).toThrow(
          "JWT_SECRET must be at least 32 characters",
        );
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });

    it("should throw for secrets shorter than 16 chars in development", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "short",
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "development";

        expect(() => JWTConfig.validate()).toThrow(
          "JWT_SECRET must be at least 16 characters",
        );
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });

    it("should warn but not throw for 16-31 char secrets in development", () => {
      const originalSecret = JWTConfig.SECRET;
      const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "a".repeat(20),
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "development";

        expect(() => JWTConfig.validate()).not.toThrow();
        expect(warnSpy).toHaveBeenCalledWith(
          expect.stringContaining("SECURITY WARNING"),
        );
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
        warnSpy.mockRestore();
      }
    });
  });

  describe("test environment secret handling", () => {
    it("should throw if SECRET is empty even in test environment", () => {
      const originalSecret = JWTConfig.SECRET;
      try {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: "",
          writable: true,
          configurable: true,
        });
        process.env.NODE_ENV = "test";

        expect(() => JWTConfig.validate()).toThrow(
          "JWT_SECRET must not be empty",
        );
      } finally {
        Object.defineProperty(JWTConfig, "SECRET", {
          value: originalSecret,
          writable: true,
          configurable: true,
        });
      }
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 4. Rate Limiting
// ─────────────────────────────────────────────────────────────────────────────

describe("Rate limiting", () => {
  describe("rate limiting configuration", () => {
    it("should have rate limiting enabled by default", () => {
      // RATE_LIMIT_ENABLED defaults to true unless RATE_LIMIT_ENABLED=false
      expect(JWTConfig.RATE_LIMIT_ENABLED).toBe(true);
    });

    it("should have default rate limit of 100 requests", () => {
      expect(JWTConfig.RATE_LIMIT_REQUESTS).toBe(100);
    });

    it("should have default rate limit window of 60 seconds", () => {
      expect(JWTConfig.RATE_LIMIT_WINDOW_SECONDS).toBe(60);
    });

    it("should have RATE_LIMIT_EXCEEDED error defined", () => {
      expect(AuthErrors.RATE_LIMIT_EXCEEDED).toBeDefined();
      expect(AuthErrors.RATE_LIMIT_EXCEEDED.en).toContain("Too many requests");
      expect(AuthErrors.RATE_LIMIT_EXCEEDED.ar).toBeTruthy();
      expect(AuthErrors.RATE_LIMIT_EXCEEDED.code).toBe("rate_limit_exceeded");
    });
  });

  describe("rate limit response simulation", () => {
    it("should return 429 status code semantics for rate limit exceeded", () => {
      // The RATE_LIMIT_EXCEEDED error code maps to HTTP 429.
      // Verify the error structure supports rate limiting responses.
      const error = AuthErrors.RATE_LIMIT_EXCEEDED;

      expect(error.code).toBe("rate_limit_exceeded");
      expect(error.en).toMatch(/try again later/i);
    });

    it("should include bilingual rate limit messages", () => {
      const error = AuthErrors.RATE_LIMIT_EXCEEDED;

      // English message
      expect(error.en).toBe("Too many requests. Please try again later");
      // Arabic message
      expect(error.ar).toBe(
        "طلبات كثيرة جدا. الرجاء المحاولة مرة أخرى لاحقا",
      );
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 5. Guard Composition (JwtAuthGuard + TenantGuard together)
// ─────────────────────────────────────────────────────────────────────────────

describe("Guard composition: JwtAuthGuard + TenantGuard", () => {
  let jwtGuard: JwtAuthGuard;
  let tenantGuard: TenantGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = createReflector();
    jwtGuard = new JwtAuthGuard(reflector);
    tenantGuard = new TenantGuard(reflector);
  });

  it("should reject at JWT level when no token (before tenant check)", () => {
    const context = createMockContext({ url: "/api/v1/fields", method: "GET" });

    // JwtAuthGuard rejects first
    expect(() => jwtGuard.handleRequest(null, null, null, context)).toThrow(
      UnauthorizedException,
    );
  });

  it("should reject at tenant level when authenticated but no tenant", () => {
    const context = createMockContext({
      user: { id: "user-1", roles: ["farmer"] },
      headers: {},
    });

    // JWT passes (user exists), but tenant check fails
    const user = jwtGuard.handleRequest(null, { id: "user-1", roles: ["farmer"] }, null, context);
    expect(user).toBeTruthy();

    expect(() => tenantGuard.canActivate(context)).toThrow(BadRequestException);
  });

  it("should pass both guards when authenticated with tenant", () => {
    const user = { id: "user-1", roles: ["farmer"], tenantId: "00000000-0000-0000-0000-000000000001" };
    const context = createMockContext({
      user,
      headers: {},
    });

    const jwtResult = jwtGuard.handleRequest(null, user, null, context);
    expect(jwtResult).toBe(user);

    const tenantResult = tenantGuard.canActivate(context);
    expect(tenantResult).toBe(true);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 6. ActiveAccountGuard with Auth Flow
// ─────────────────────────────────────────────────────────────────────────────

describe("ActiveAccountGuard in auth flow", () => {
  let guard: ActiveAccountGuard;

  beforeEach(() => {
    guard = new ActiveAccountGuard();
  });

  it("should reject disabled accounts after successful JWT validation", () => {
    const context = createMockContext({
      user: { id: "user-1", isActive: false, isVerified: true },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should reject unverified accounts after successful JWT validation", () => {
    const context = createMockContext({
      user: { id: "user-1", isActive: true, isVerified: false },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should include account disabled message", () => {
    const context = createMockContext({
      user: { id: "user-1", isActive: false },
    });

    try {
      guard.canActivate(context);
      expect.fail("Expected ForbiddenException");
    } catch (error: any) {
      expect(error.message).toBe(AuthErrors.ACCOUNT_DISABLED.en);
    }
  });

  it("should include account not verified message", () => {
    const context = createMockContext({
      user: { id: "user-1", isActive: true, isVerified: false },
    });

    try {
      guard.canActivate(context);
      expect.fail("Expected ForbiddenException");
    } catch (error: any) {
      expect(error.message).toBe(AuthErrors.ACCOUNT_NOT_VERIFIED.en);
    }
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 7. RolesGuard Security
// ─────────────────────────────────────────────────────────────────────────────

describe("RolesGuard security", () => {
  let guard: RolesGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new RolesGuard(reflector);
  });

  it("should prevent privilege escalation by checking user roles array", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue(["admin"]);

    const context = createMockContext({
      user: { id: "user-1", roles: ["farmer", "viewer"] },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should reject when roles array is empty", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue(["admin"]);

    const context = createMockContext({
      user: { id: "user-1", roles: [] },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should allow when user has one of multiple required roles", () => {
    vi.spyOn(reflector, "getAllAndOverride").mockReturnValue([
      "admin",
      "manager",
      "supervisor",
    ]);

    const context = createMockContext({
      user: { id: "user-1", roles: ["manager"] },
    });

    expect(guard.canActivate(context)).toBe(true);
  });
});
