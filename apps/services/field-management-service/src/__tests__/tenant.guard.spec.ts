/**
 * TenantGuard Unit Tests
 *
 * Verifies that:
 * - Health check endpoints (marked @Public) are always allowed through
 * - Routes marked @SkipTenantCheck bypass tenant validation
 * - Unauthenticated requests to protected routes are rejected
 * - Authenticated requests without a tenant ID are rejected
 * - Authenticated requests with a valid tenant ID are allowed
 *
 * Regression guard for: TenantGuard blocking /healthz → container fails health check
 */

import { BadRequestException, ExecutionContext, ForbiddenException, UnauthorizedException } from "@nestjs/common";
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
    it("throws UnauthorizedException when no user is present", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      expect(() => guard.canActivate(makeContext(undefined, {}))).toThrow(UnauthorizedException);
    });

    it("throws BadRequestException when authenticated user has no tenantId", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      expect(() =>
        guard.canActivate(makeContext({ id: "user-1", tenantId: undefined, roles: [] }, {})),
      ).toThrow(BadRequestException);
    });

    it("sets request.tenantId and returns true for authenticated user with tenantId", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest({ id: "user-1", tenantId: "tenant-abc", roles: [] }, {}, "GET", "/api/v1/fields");
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-abc");
    });

    it("uses X-Tenant-ID header when it matches the user's tenantId", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest(
        { id: "user-1", tenantId: "tenant-abc", roles: [] },
        { "x-tenant-id": "tenant-abc" },
        "GET",
        "/api/v1/fields",
      );
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-abc");
    });

    it("throws ForbiddenException when non-admin supplies a different tenant ID header", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      expect(() =>
        guard.canActivate(
          makeContext({ id: "user-1", tenantId: "tenant-abc", roles: ["user"] }, { "x-tenant-id": "tenant-xyz" }),
        ),
      ).toThrow(ForbiddenException);
    });

    it("allows admin to override tenant via X-Tenant-ID header (lowercase legacy)", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest(
        { id: "admin-1", tenantId: "tenant-abc", roles: ["admin"] },
        { "x-tenant-id": "tenant-xyz" },
        "GET",
        "/api/v1/fields",
      );
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-xyz");
    });

    // Prisma UserRole enum emits uppercase values; the platform JWT carries
    // [user.role] verbatim. The previous guard used lowercase-only matching
    // which silently forbade every real production admin.
    it("allows ADMIN (uppercase from Prisma enum) to override tenant", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest(
        { id: "admin-1", tenantId: "tenant-abc", roles: ["ADMIN"] },
        { "x-tenant-id": "tenant-xyz" },
      );
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-xyz");
    });

    it("allows SUPER_ADMIN to override tenant", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const req = makeRequest(
        { id: "admin-1", tenantId: "tenant-abc", roles: ["SUPER_ADMIN"] },
        { "x-tenant-id": "tenant-xyz" },
      );
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(req.tenantId).toBe("tenant-xyz");
    });

    it("emits audit log when admin overrides tenant (privileged cross-tenant access)", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      const warnSpy = jest
        .spyOn((guard as unknown as { logger: { warn: (msg: string) => void } }).logger, "warn")
        .mockImplementation(() => {});
      const req = makeRequest(
        { id: "admin-42", tenantId: "tenant-abc", roles: ["ADMIN"] },
        { "x-tenant-id": "tenant-xyz" },
        "POST",
        "/api/v1/fields",
      );
      const ctx = {
        getHandler: () => ({}),
        getClass: () => ({}),
        switchToHttp: () => ({ getRequest: () => req }),
      } as unknown as ExecutionContext;

      expect(guard.canActivate(ctx)).toBe(true);
      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining("admin_tenant_override"),
      );
      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining("userId=admin-42"),
      );
      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining("toTenant=tenant-xyz"),
      );
    });

    it("normalizes duplicated X-Tenant-ID header (array from proxy)", () => {
      const guard = new TenantGuard(makeReflector(false, false));
      // Express represents duplicated headers as arrays. Without
      // normalization, comparing `[“tenant-xyz”] !== "tenant-abc"` still
      // triggers the override path but request.tenantId would be an array,
      // polluting every downstream tenant-scoped query.
      const req = makeRequest(
        { id: "admin-1", tenantId: "tenant-abc", roles: ["ADMIN"] },
        { "x-tenant-id": ["tenant-xyz", "tenant-abc"] as unknown as string },
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
