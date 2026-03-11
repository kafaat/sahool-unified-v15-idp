/**
 * Tenant Isolation Integration Tests
 *
 * Verifies multi-tenant data isolation across the SAHOOL platform:
 * - TenantGuard rejects mismatched tenantId
 * - @Public() decorated routes skip auth and tenant checks
 * - Prisma tenant middleware injects tenantId into queries
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  ExecutionContext,
  ForbiddenException,
  BadRequestException,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { TenantGuard, SkipTenantCheck } from "../../../packages/nestjs-auth/src/guards/tenant.guard";
import { JwtAuthGuard } from "../../../packages/nestjs-auth/src/guards/jwt.guard";
import { createTenantExtension } from "../../../packages/nestjs-auth/src/middleware/prisma-tenant.middleware";

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
// 1. TenantGuard Rejects Mismatched tenantId
// ─────────────────────────────────────────────────────────────────────────────

describe("TenantGuard rejects when user.tenantId does not match request tenantId", () => {
  let guard: TenantGuard;
  let reflector: Reflector;

  beforeEach(() => {
    reflector = createReflector();
    guard = new TenantGuard(reflector);
  });

  it("should reject when x-tenant-id header differs from JWT tenantId for farmer", () => {
    const context = createMockContext({
      user: { id: "farmer-1", roles: ["farmer"], tenantId: "tenant-A" },
      headers: { "x-tenant-id": "tenant-B" },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should reject when x-tenant-id header differs from JWT tenantId for viewer", () => {
    const context = createMockContext({
      user: { id: "viewer-1", roles: ["viewer"], tenantId: "tenant-100" },
      headers: { "x-tenant-id": "tenant-200" },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should reject even when user has multiple non-admin roles", () => {
    const context = createMockContext({
      user: {
        id: "user-1",
        roles: ["farmer", "manager", "supervisor"],
        tenantId: "tenant-A",
      },
      headers: { "x-tenant-id": "tenant-B" },
    });

    expect(() => guard.canActivate(context)).toThrow(ForbiddenException);
  });

  it("should allow admin users to access different tenants", () => {
    const context = createMockContext({
      user: { id: "admin-1", roles: ["admin"], tenantId: "tenant-A" },
      headers: { "x-tenant-id": "tenant-B" },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it("should allow admin with mixed roles to access different tenants", () => {
    const context = createMockContext({
      user: {
        id: "admin-1",
        roles: ["admin", "farmer"],
        tenantId: "tenant-A",
      },
      headers: { "x-tenant-id": "tenant-C" },
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it("should allow when no header is provided and user has tenantId", () => {
    const context = createMockContext({
      user: { id: "farmer-1", roles: ["farmer"], tenantId: "tenant-A" },
      headers: {},
    });

    expect(guard.canActivate(context)).toBe(true);
  });

  it("should set tenantId on request from JWT when no header", () => {
    const context = createMockContext({
      user: { id: "farmer-1", roles: ["farmer"], tenantId: "tenant-A" },
      headers: {},
    });

    guard.canActivate(context);

    const request = context.switchToHttp().getRequest() as any;
    expect(request.tenantId).toBe("tenant-A");
  });

  it("should set tenantId on request from header for admin cross-tenant", () => {
    const context = createMockContext({
      user: { id: "admin-1", roles: ["admin"], tenantId: "tenant-A" },
      headers: { "x-tenant-id": "tenant-B" },
    });

    guard.canActivate(context);

    const request = context.switchToHttp().getRequest() as any;
    // requestedTenantId = headerTenantId || userTenantId, so header wins
    expect(request.tenantId).toBe("tenant-B");
  });

  it("should reject when no tenant information is available at all", () => {
    const context = createMockContext({
      user: { id: "user-1", roles: ["farmer"] },
      headers: {},
    });

    expect(() => guard.canActivate(context)).toThrow(BadRequestException);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 2. @Public() Decorated Routes Skip Auth
// ─────────────────────────────────────────────────────────────────────────────

describe("@Public() decorated routes skip auth", () => {
  describe("JwtAuthGuard with @Public()", () => {
    it("should return true for routes with isPublic metadata", () => {
      const reflector = createReflector({ isPublic: true });
      const guard = new JwtAuthGuard(reflector);

      const context = createMockContext({
        user: null,
        url: "/healthz",
      });

      expect(guard.canActivate(context)).toBe(true);
    });

    it("should allow unauthenticated access to public routes", () => {
      const reflector = createReflector({ isPublic: true });
      const guard = new JwtAuthGuard(reflector);

      // No user, no token -- should still pass for public route
      const context = createMockContext({
        user: null,
        url: "/api/v1/auth/login",
      });

      expect(guard.canActivate(context)).toBe(true);
    });

    it("should not skip auth when isPublic is false", () => {
      const reflector = createReflector({ isPublic: false });
      const guard = new JwtAuthGuard(reflector);

      const context = createMockContext({
        user: null,
        url: "/api/v1/fields",
      });

      // canActivate will delegate to super.canActivate (Passport),
      // but handleRequest should reject
      expect(() => guard.handleRequest(null, null, null, context)).toThrow();
    });

    it("should not skip auth when isPublic metadata is not set", () => {
      const reflector = createReflector({});
      const guard = new JwtAuthGuard(reflector);

      const context = createMockContext({
        user: null,
        url: "/api/v1/fields",
      });

      expect(() => guard.handleRequest(null, null, null, context)).toThrow();
    });
  });

  describe("TenantGuard with @Public()", () => {
    it("should skip tenant check for public routes", () => {
      const reflector = createReflector({ isPublic: true });
      const guard = new TenantGuard(reflector);

      const context = createMockContext({
        user: null,
        headers: {},
        url: "/healthz",
      });

      expect(guard.canActivate(context)).toBe(true);
    });

    it("should skip tenant check for login route marked as public", () => {
      const reflector = createReflector({ isPublic: true });
      const guard = new TenantGuard(reflector);

      const context = createMockContext({
        user: null,
        headers: {},
        url: "/api/v1/auth/login",
      });

      expect(guard.canActivate(context)).toBe(true);
    });

    it("should enforce tenant check when route is not public", () => {
      const reflector = createReflector({ isPublic: false });
      const guard = new TenantGuard(reflector);

      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"] },
        headers: {},
      });

      expect(() => guard.canActivate(context)).toThrow(BadRequestException);
    });
  });

  describe("TenantGuard with @SkipTenantCheck()", () => {
    it("should skip tenant validation when skipTenantCheck is set", () => {
      const reflector = createReflector({ skipTenantCheck: true });
      const guard = new TenantGuard(reflector);

      const context = createMockContext({
        user: { id: "admin-1", roles: ["admin"] },
        headers: {},
      });

      expect(guard.canActivate(context)).toBe(true);
    });

    it("should enforce tenant validation when skipTenantCheck is false", () => {
      const reflector = createReflector({ skipTenantCheck: false });
      const guard = new TenantGuard(reflector);

      const context = createMockContext({
        user: { id: "user-1", roles: ["farmer"] },
        headers: {},
      });

      expect(() => guard.canActivate(context)).toThrow(BadRequestException);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// 3. Tenant-Scoped Prisma Middleware
// ─────────────────────────────────────────────────────────────────────────────

describe("Tenant-scoped Prisma middleware adds tenantId to queries", () => {
  const TENANT_ID = "tenant-abc-123";

  describe("createTenantExtension structure", () => {
    it("should return an extension with name tenant-isolation", () => {
      const extension = createTenantExtension(TENANT_ID);

      expect(extension.name).toBe("tenant-isolation");
      expect(extension.query).toBeDefined();
      expect(extension.query.$allModels).toBeDefined();
    });

    it("should define handlers for all standard Prisma operations", () => {
      const extension = createTenantExtension(TENANT_ID);
      const operations = extension.query.$allModels;

      expect(operations.findMany).toBeTypeOf("function");
      expect(operations.findFirst).toBeTypeOf("function");
      expect(operations.findUnique).toBeTypeOf("function");
      expect(operations.create).toBeTypeOf("function");
      expect(operations.createMany).toBeTypeOf("function");
      expect(operations.update).toBeTypeOf("function");
      expect(operations.updateMany).toBeTypeOf("function");
      expect(operations.delete).toBeTypeOf("function");
      expect(operations.deleteMany).toBeTypeOf("function");
      expect(operations.count).toBeTypeOf("function");
      expect(operations.aggregate).toBeTypeOf("function");
    });
  });

  describe("findMany injects tenantId for tenant-aware models", () => {
    it("should add tenantId to where clause for Field model", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: { status: "active" } };
      const queryFn = vi.fn().mockResolvedValue([]);

      await extension.query.$allModels.findMany({
        args,
        query: queryFn,
        model: "Field",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({ tenantId: TENANT_ID }),
        }),
      );
    });

    it("should add tenantId to where clause for Farm model", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: {} };
      const queryFn = vi.fn().mockResolvedValue([]);

      await extension.query.$allModels.findMany({
        args,
        query: queryFn,
        model: "Farm",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({ tenantId: TENANT_ID }),
        }),
      );
    });

    it("should add tenantId to where clause for Task model", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: { assigneeId: "user-1" } };
      const queryFn = vi.fn().mockResolvedValue([]);

      await extension.query.$allModels.findMany({
        args,
        query: queryFn,
        model: "Task",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            tenantId: TENANT_ID,
            assigneeId: "user-1",
          }),
        }),
      );
    });

    it("should NOT add tenantId for non-tenant models", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: { email: "test@test.com" } };
      const queryFn = vi.fn().mockResolvedValue([]);

      // "User" is not in the TENANT_MODELS set
      await extension.query.$allModels.findMany({
        args,
        query: queryFn,
        model: "User",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.not.objectContaining({ tenantId: TENANT_ID }),
        }),
      );
    });

    it("should preserve existing where conditions", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = {
        where: { status: "active", name: { contains: "wheat" } },
      };
      const queryFn = vi.fn().mockResolvedValue([]);

      await extension.query.$allModels.findMany({
        args,
        query: queryFn,
        model: "Field",
      });

      const calledArgs = queryFn.mock.calls[0][0];
      expect(calledArgs.where.status).toBe("active");
      expect(calledArgs.where.name).toEqual({ contains: "wheat" });
      expect(calledArgs.where.tenantId).toBe(TENANT_ID);
    });
  });

  describe("findFirst injects tenantId", () => {
    it("should add tenantId for tenant-aware model", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: { id: "field-1" } };
      const queryFn = vi.fn().mockResolvedValue(null);

      await extension.query.$allModels.findFirst({
        args,
        query: queryFn,
        model: "Field",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({ tenantId: TENANT_ID }),
        }),
      );
    });
  });

  describe("create injects tenantId into data", () => {
    it("should add tenantId to data for Field model", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { data: { name: "Test Field", area: 10.5 } };
      const queryFn = vi.fn().mockResolvedValue({ id: "new-1" });

      await extension.query.$allModels.create({
        args,
        query: queryFn,
        model: "Field",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            tenantId: TENANT_ID,
            name: "Test Field",
            area: 10.5,
          }),
        }),
      );
    });

    it("should NOT add tenantId to data for non-tenant models", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { data: { email: "test@test.com" } };
      const queryFn = vi.fn().mockResolvedValue({ id: "new-1" });

      await extension.query.$allModels.create({
        args,
        query: queryFn,
        model: "User",
      });

      const calledArgs = queryFn.mock.calls[0][0];
      expect(calledArgs.data.tenantId).toBeUndefined();
    });
  });

  describe("createMany injects tenantId into each record", () => {
    it("should add tenantId to each item in array data", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = {
        data: [
          { name: "Field 1", area: 5 },
          { name: "Field 2", area: 8 },
        ],
      };
      const queryFn = vi.fn().mockResolvedValue({ count: 2 });

      await extension.query.$allModels.createMany({
        args,
        query: queryFn,
        model: "Field",
      });

      const calledArgs = queryFn.mock.calls[0][0];
      expect(calledArgs.data).toHaveLength(2);
      expect(calledArgs.data[0].tenantId).toBe(TENANT_ID);
      expect(calledArgs.data[1].tenantId).toBe(TENANT_ID);
    });

    it("should handle single object data in createMany", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { data: { name: "Field 1", area: 5 } };
      const queryFn = vi.fn().mockResolvedValue({ count: 1 });

      await extension.query.$allModels.createMany({
        args,
        query: queryFn,
        model: "Field",
      });

      const calledArgs = queryFn.mock.calls[0][0];
      expect(calledArgs.data.tenantId).toBe(TENANT_ID);
    });
  });

  describe("update injects tenantId into where clause", () => {
    it("should scope updates to tenant", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = {
        where: { id: "field-1" },
        data: { name: "Updated Field" },
      };
      const queryFn = vi.fn().mockResolvedValue({ id: "field-1" });

      await extension.query.$allModels.update({
        args,
        query: queryFn,
        model: "Field",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            id: "field-1",
            tenantId: TENANT_ID,
          }),
        }),
      );
    });
  });

  describe("delete injects tenantId into where clause", () => {
    it("should scope deletes to tenant", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: { id: "field-1" } };
      const queryFn = vi.fn().mockResolvedValue({ id: "field-1" });

      await extension.query.$allModels.delete({
        args,
        query: queryFn,
        model: "Field",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            id: "field-1",
            tenantId: TENANT_ID,
          }),
        }),
      );
    });
  });

  describe("deleteMany injects tenantId", () => {
    it("should scope bulk deletes to tenant", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: { status: "archived" } };
      const queryFn = vi.fn().mockResolvedValue({ count: 5 });

      await extension.query.$allModels.deleteMany({
        args,
        query: queryFn,
        model: "Task",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            status: "archived",
            tenantId: TENANT_ID,
          }),
        }),
      );
    });
  });

  describe("count injects tenantId", () => {
    it("should scope count queries to tenant", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: { status: "active" } };
      const queryFn = vi.fn().mockResolvedValue(42);

      await extension.query.$allModels.count({
        args,
        query: queryFn,
        model: "Field",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            status: "active",
            tenantId: TENANT_ID,
          }),
        }),
      );
    });
  });

  describe("aggregate injects tenantId", () => {
    it("should scope aggregate queries to tenant", async () => {
      const extension = createTenantExtension(TENANT_ID);
      const args: any = { where: {}, _sum: { area: true } };
      const queryFn = vi.fn().mockResolvedValue({ _sum: { area: 100 } });

      await extension.query.$allModels.aggregate({
        args,
        query: queryFn,
        model: "Field",
      });

      expect(queryFn).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({ tenantId: TENANT_ID }),
        }),
      );
    });
  });

  describe("tenant isolation across multiple tenants", () => {
    it("should produce different extensions for different tenants", () => {
      const extA = createTenantExtension("tenant-A");
      const extB = createTenantExtension("tenant-B");

      // Both should have the same structure but different tenant IDs
      expect(extA.name).toBe(extB.name);
      expect(extA).not.toBe(extB); // Different object references
    });

    it("should prevent cross-tenant data access in findMany", async () => {
      const extA = createTenantExtension("tenant-A");
      const queryFnA = vi.fn().mockResolvedValue([{ id: "1", tenantId: "tenant-A" }]);

      await extA.query.$allModels.findMany({
        args: { where: {} },
        query: queryFnA,
        model: "Field",
      });

      const calledArgs = queryFnA.mock.calls[0][0];
      expect(calledArgs.where.tenantId).toBe("tenant-A");
      expect(calledArgs.where.tenantId).not.toBe("tenant-B");
    });

    it("should prevent cross-tenant data creation", async () => {
      const extA = createTenantExtension("tenant-A");
      const queryFn = vi.fn().mockResolvedValue({ id: "new-1" });

      // Even if someone tries to pass tenant-B in data, the extension
      // will overwrite it with tenant-A
      await extA.query.$allModels.create({
        args: { data: { name: "Hijacked", tenantId: "tenant-B" } },
        query: queryFn,
        model: "Field",
      });

      const calledArgs = queryFn.mock.calls[0][0];
      // The spread { ...args.data, tenantId } means extension's tenantId wins
      expect(calledArgs.data.tenantId).toBe("tenant-A");
    });
  });

  describe("coverage of all tenant-aware models", () => {
    const EXPECTED_TENANT_MODELS = [
      "Field",
      "Farm",
      "Task",
      "NdviReading",
      "FieldBoundaryHistory",
      "SyncStatus",
      "Product",
      "Order",
      "OrderItem",
      "Wallet",
      "Transaction",
      "Loan",
      "CreditEvent",
      "Escrow",
      "ScheduledPayment",
      "WalletAuditLog",
      "SellerProfile",
      "BuyerProfile",
      "ProductReview",
      "ReviewResponse",
      "Message",
      "Channel",
      "ChannelMember",
      "Device",
      "DeviceReading",
      "Assessment",
      "Hazard",
      "ResearchTrial",
      "Experiment",
      "DataPoint",
      "CropModel",
      "GrowthStage",
      "YieldPrediction",
      "LaiReading",
    ];

    for (const model of EXPECTED_TENANT_MODELS) {
      it(`should inject tenantId for ${model} model in findMany`, async () => {
        const extension = createTenantExtension(TENANT_ID);
        const args: any = { where: {} };
        const queryFn = vi.fn().mockResolvedValue([]);

        await extension.query.$allModels.findMany({
          args,
          query: queryFn,
          model,
        });

        const calledArgs = queryFn.mock.calls[0][0];
        expect(calledArgs.where.tenantId).toBe(TENANT_ID);
      });
    }

    const NON_TENANT_MODELS = ["User", "Role", "Permission", "AuditLog", "SystemConfig"];

    for (const model of NON_TENANT_MODELS) {
      it(`should NOT inject tenantId for ${model} model in findMany`, async () => {
        const extension = createTenantExtension(TENANT_ID);
        const args: any = { where: {} };
        const queryFn = vi.fn().mockResolvedValue([]);

        await extension.query.$allModels.findMany({
          args,
          query: queryFn,
          model,
        });

        const calledArgs = queryFn.mock.calls[0][0];
        expect(calledArgs.where.tenantId).toBeUndefined();
      });
    }
  });
});
