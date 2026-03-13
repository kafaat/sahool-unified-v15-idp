/**
 * TenantGuard Unit Tests
 *
 * Verifies that:
 * - Health check endpoints (marked @Public) are always allowed through
 * - Routes marked @SkipTenantCheck bypass tenant validation
 * - Requests with a valid tenantId in header are allowed
 * - Requests with mismatched tenant header (non-admin) are rejected
 * - Requests missing tenantId on protected routes are rejected
 *
 * Regression guard for: TenantGuard blocking /healthz → container fails health check
 */

import { BadRequestException, ExecutionContext, ForbiddenException } from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { TenantGuard, SKIP_TENANT_KEY } from "../auth/tenant.guard";
import { IS_PUBLIC_KEY } from "../auth/public.decorator";

// ─── helpers ─────────────────────────────────────────────────────────────────

function makeRequest(
  user: Record<string, any> | undefined,
  headers: Record<string, string> = {},
  method = "GET",
  url = "/test",
): Record<string, any> {
  return { user, headers, method, url };
}

function makeContext(
  user: Record<string, any> | undefined,
  headers: Record<string, string> = {},
): ExecutionContext {
  const req = makeRequest(user, headers);
  return {
    getHandler: () => ({}),
    getClass: () => ({}),
    switchToHttp: () => ({ getRequest: () => req }),
  } as unknown as ExecutionContext;
}

function makeReflector(isPublic: boolean | undefined, skipTenant: boolean | undefined): Reflector {
  const reflector = new Reflector();
  jest.spyOn(reflector, "getAllAndOverride").mockImplementation((key: unknown) => {
    if (key === IS_PUBLIC_KEY) return isPublic;
    if (key === SKIP_TENANT_KEY) return skipTenant;
    return undefined;
  });
  return reflector;
}

// ─── tests ───────────────────────────────────────────────────────────────────

describe("TenantGuard", () => {
  afterEach(() => jest.restoreAllMocks());

  describe("public routes (e.g. /healthz, /readyz, /health)", () => {
    it("allows request when @Public() is set on the handler", () => {
      const guard = new TenantGuard(makeReflector(true, undefined));
      // No user, no headers — simulates Docker health probe
      expect(guard.canActivate(makeContext(undefined, {}))).toBe(true);
    });

    it("allows request when @SkipTenantCheck() is set on the class", () => {
      const guard = new TenantGuard(makeReflector(undefined, true));
      expect(guard.canActivate(makeContext(undefined, {}))).toBe(true);
    });

    it("allows request when both @Public() and @SkipTenantCheck() are set", () => {
      const guard = new TenantGuard(makeReflector(true, true));
      expect(guard.canActivate(makeContext(undefined, {}))).toBe(true);
    });
  });

  describe("protected routes", () => {
    it("throws BadRequestException when no tenantId is present at all", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      expect(() => guard.canActivate(makeContext(undefined, {}))).toThrow(BadRequestException);
    });

    it("sets request.tenantId and returns true when tenantId comes from X-Tenant-ID header", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest(undefined, { "x-tenant-id": "tenant-abc" }, "GET", "/api/v1/iot/field/f1/sensors");
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-abc");
    });

    it("sets request.tenantId from authenticated user's tenantId", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest({ id: "u1", tenantId: "tenant-abc", roles: [] }, {}, "GET", "/api/v1/iot/devices");
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-abc");
    });

    it("throws ForbiddenException when non-admin supplies a different X-Tenant-ID", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      expect(() =>
        guard.canActivate(
          makeContext(
            { id: "u1", tenantId: "tenant-abc", roles: ["user"] },
            { "x-tenant-id": "tenant-xyz" },
          ),
        ),
      ).toThrow(ForbiddenException);
    });

    it("allows admin to override tenant via X-Tenant-ID header", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest(
        { id: "admin1", tenantId: "tenant-abc", roles: ["admin"] },
        { "x-tenant-id": "tenant-xyz" },
        "GET",
        "/api/v1/iot/devices",
      );
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-xyz");
    });
  });
});
