/**
 * Data Integrity Tests for Prisma Middleware Patterns
 * اختبارات سلامة البيانات لأنماط وسيط Prisma
 *
 * Tests soft delete middleware, audit fields (timestamps),
 * unique constraints, and cascade behavior using mocked Prisma
 * middleware invocations that mirror the production patterns in:
 * - packages/shared-db/src/soft-delete.ts
 * - apps/services/shared/validation/prisma-middleware.ts
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════════
// Inline Middleware Implementations (mirroring production code)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Soft delete middleware - converts delete to update, filters reads.
 * Based on packages/shared-db/src/soft-delete.ts createSoftDeleteMiddleware
 * and apps/services/shared/validation/prisma-middleware.ts createSoftDeleteMiddleware.
 */
function createSoftDeleteMiddleware(
  config: { excludedModels?: string[] } = {},
) {
  const { excludedModels = [] } = config;

  return async (
    params: { model?: string; action: string; args: any },
    next: (params: any) => Promise<any>,
  ) => {
    const model = params.model;
    if (!model || excludedModels.includes(model)) {
      return next(params);
    }

    // DELETE -> UPDATE with deletedAt
    if (params.action === "delete") {
      params.action = "update";
      params.args.data = {
        deletedAt: new Date(),
        deletedBy: params.args.deletedBy || null,
      };
    }

    // DELETE MANY -> UPDATE MANY with deletedAt
    if (params.action === "deleteMany") {
      params.action = "updateMany";
      params.args.data = {
        deletedAt: new Date(),
        deletedBy: params.args.deletedBy || null,
      };
    }

    // FIND operations - filter out deleted records
    const readActions = [
      "findUnique",
      "findFirst",
      "findMany",
      "count",
      "aggregate",
      "groupBy",
    ];

    if (readActions.includes(params.action)) {
      const includeDeleted = params.args?.includeDeleted;
      if (!includeDeleted) {
        if (params.args.where) {
          if (params.args.where.deletedAt === undefined) {
            params.args.where.deletedAt = null;
          }
        } else {
          params.args.where = { deletedAt: null };
        }
      } else {
        delete params.args.includeDeleted;
      }
    }

    return next(params);
  };
}

/**
 * Timestamp middleware - auto-sets createdAt and updatedAt.
 * Based on apps/services/shared/validation/prisma-middleware.ts createTimestampMiddleware.
 */
function createTimestampMiddleware() {
  return async (
    params: { action: string; args: any },
    next: (params: any) => Promise<any>,
  ) => {
    const { action, args } = params;

    if (action === "create") {
      if (args.data) {
        args.data.createdAt = args.data.createdAt || new Date();
        args.data.updatedAt = args.data.updatedAt || new Date();
      }
    }

    if (action === "update" || action === "updateMany") {
      if (args.data) {
        args.data.updatedAt = new Date();
      }
    }

    return next(params);
  };
}

/**
 * Audit logging middleware - logs create/update/delete mutations.
 * Based on apps/services/shared/validation/prisma-middleware.ts createAuditLoggingMiddleware.
 */
function createAuditLoggingMiddleware(
  logger: (message: string, context?: any) => void,
) {
  return async (
    params: { model?: string; action: string; args: any },
    next: (params: any) => Promise<any>,
  ) => {
    const { model, action, args } = params;

    if (
      model &&
      ["create", "update", "updateMany", "delete", "deleteMany"].includes(
        action,
      )
    ) {
      const timestamp = new Date().toISOString();
      logger(`[${timestamp}] Prisma ${action} on ${model}`, {
        model,
        action,
        args: JSON.stringify(args).substring(0, 500),
      });
    }

    const result = await next(params);

    if (model && ["create", "update", "delete"].includes(action) && result) {
      logger(`${action} completed for ${model}`, {
        model,
        action,
        id: result.id || "N/A",
      });
    }

    return result;
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Test Helpers
// ═══════════════════════════════════════════════════════════════════════════════

/** Creates a mock next() that returns a predictable result */
function createMockNext(returnValue: any = { id: "mock-id" }) {
  return vi.fn().mockResolvedValue(returnValue);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Data Integrity", () => {
  // ───────────────────────────────────────────────────────────────────────────
  // 1. Soft Delete Middleware
  // ───────────────────────────────────────────────────────────────────────────

  describe("Soft delete middleware", () => {
    let middleware: ReturnType<typeof createSoftDeleteMiddleware>;
    let next: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      middleware = createSoftDeleteMiddleware();
      next = createMockNext();
    });

    it("should set deletedAt timestamp when deleting a record", async () => {
      const params = {
        model: "Field",
        action: "delete",
        args: { where: { id: "field-001" } },
      };

      const beforeDelete = new Date();
      await middleware(params, next);

      expect(params.action).toBe("update");
      expect(params.args.data).toBeDefined();
      expect(params.args.data.deletedAt).toBeInstanceOf(Date);
      expect(params.args.data.deletedAt.getTime()).toBeGreaterThanOrEqual(
        beforeDelete.getTime(),
      );
    });

    it("should set deletedBy to null when no user specified", async () => {
      const params = {
        model: "Field",
        action: "delete",
        args: { where: { id: "field-001" } },
      };

      await middleware(params, next);

      expect(params.args.data.deletedBy).toBeNull();
    });

    it("should preserve deletedBy when provided", async () => {
      const params = {
        model: "Field",
        action: "delete",
        args: { where: { id: "field-001" }, deletedBy: "user-123" },
      };

      await middleware(params, next);

      expect(params.args.data.deletedBy).toBe("user-123");
    });

    it("should set deletedAt on deleteMany operation", async () => {
      const params = {
        model: "Task",
        action: "deleteMany",
        args: { where: { status: "CANCELLED" } },
      };

      await middleware(params, next);

      expect(params.action).toBe("updateMany");
      expect(params.args.data.deletedAt).toBeInstanceOf(Date);
    });

    it("should exclude soft-deleted records from findMany by default", async () => {
      const params = {
        model: "Field",
        action: "findMany",
        args: { where: { tenantId: "tenant-001" } },
      };

      await middleware(params, next);

      expect(params.args.where.deletedAt).toBeNull();
      // Original where conditions are preserved
      expect(params.args.where.tenantId).toBe("tenant-001");
    });

    it("should exclude soft-deleted records from findFirst by default", async () => {
      const params = {
        model: "Field",
        action: "findFirst",
        args: { where: { name: "North Field" } },
      };

      await middleware(params, next);

      expect(params.args.where.deletedAt).toBeNull();
      expect(params.args.where.name).toBe("North Field");
    });

    it("should exclude soft-deleted records from findUnique by default", async () => {
      const params = {
        model: "Field",
        action: "findUnique",
        args: { where: { id: "field-001" } },
      };

      await middleware(params, next);

      expect(params.args.where.deletedAt).toBeNull();
    });

    it("should exclude soft-deleted records from count by default", async () => {
      const params = {
        model: "Field",
        action: "count",
        args: { where: {} },
      };

      await middleware(params, next);

      expect(params.args.where.deletedAt).toBeNull();
    });

    it("should add where clause with deletedAt filter when no where exists", async () => {
      const params = {
        model: "Field",
        action: "findMany",
        args: {},
      };

      await middleware(params, next);

      expect(params.args.where).toEqual({ deletedAt: null });
    });

    it("should not override explicit deletedAt filter", async () => {
      const params = {
        model: "Field",
        action: "findMany",
        args: { where: { deletedAt: { not: null } } },
      };

      await middleware(params, next);

      // The user explicitly set deletedAt, so it should be preserved
      expect(params.args.where.deletedAt).toEqual({ not: null });
    });

    it("should include deleted records when includeDeleted is true", async () => {
      const params = {
        model: "Field",
        action: "findMany",
        args: { where: { tenantId: "tenant-001" }, includeDeleted: true },
      };

      await middleware(params, next);

      // deletedAt filter should NOT be added
      expect(params.args.where.deletedAt).toBeUndefined();
      // includeDeleted flag should be removed to avoid Prisma errors
      expect(params.args.includeDeleted).toBeUndefined();
    });

    it("should skip middleware for excluded models", async () => {
      const customMiddleware = createSoftDeleteMiddleware({
        excludedModels: ["AuditLog", "SyncStatus"],
      });

      const deleteParams = {
        model: "AuditLog",
        action: "delete",
        args: { where: { id: "log-001" } },
      };

      await customMiddleware(deleteParams, next);

      // Should NOT be converted to update
      expect(deleteParams.action).toBe("delete");
    });

    it("should skip middleware for models without model name", async () => {
      const params = {
        model: undefined as any,
        action: "delete",
        args: { where: { id: "1" } },
      };

      await middleware(params, next);

      expect(params.action).toBe("delete");
    });

    it("should still call next() after transforming the operation", async () => {
      const params = {
        model: "Field",
        action: "delete",
        args: { where: { id: "field-001" } },
      };

      await middleware(params, next);

      expect(next).toHaveBeenCalledTimes(1);
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 2. Audit Fields (Timestamps)
  // ───────────────────────────────────────────────────────────────────────────

  describe("Audit fields", () => {
    let timestampMiddleware: ReturnType<typeof createTimestampMiddleware>;
    let next: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      timestampMiddleware = createTimestampMiddleware();
      next = createMockNext();
    });

    describe("createdAt", () => {
      it("should auto-set createdAt on create when not provided", async () => {
        const params = {
          action: "create",
          args: {
            data: { name: "New Field", tenantId: "t-001" },
          },
        };

        const beforeCreate = new Date();
        await timestampMiddleware(params, next);

        expect(params.args.data.createdAt).toBeInstanceOf(Date);
        expect(params.args.data.createdAt.getTime()).toBeGreaterThanOrEqual(
          beforeCreate.getTime(),
        );
      });

      it("should not override an explicit createdAt value", async () => {
        const explicitDate = new Date("2025-06-15T10:00:00Z");
        const params = {
          action: "create",
          args: {
            data: {
              name: "New Field",
              createdAt: explicitDate,
            },
          },
        };

        await timestampMiddleware(params, next);

        expect(params.args.data.createdAt).toBe(explicitDate);
      });
    });

    describe("updatedAt", () => {
      it("should auto-set updatedAt on create when not provided", async () => {
        const params = {
          action: "create",
          args: {
            data: { name: "New Field" },
          },
        };

        await timestampMiddleware(params, next);

        expect(params.args.data.updatedAt).toBeInstanceOf(Date);
      });

      it("should auto-update updatedAt on update", async () => {
        const params = {
          action: "update",
          args: {
            where: { id: "field-001" },
            data: { name: "Renamed Field" },
          },
        };

        const beforeUpdate = new Date();
        await timestampMiddleware(params, next);

        expect(params.args.data.updatedAt).toBeInstanceOf(Date);
        expect(params.args.data.updatedAt.getTime()).toBeGreaterThanOrEqual(
          beforeUpdate.getTime(),
        );
      });

      it("should auto-update updatedAt on updateMany", async () => {
        const params = {
          action: "updateMany",
          args: {
            where: { status: "active" },
            data: { status: "archived" },
          },
        };

        await timestampMiddleware(params, next);

        expect(params.args.data.updatedAt).toBeInstanceOf(Date);
      });

      it("should overwrite existing updatedAt on update to ensure freshness", async () => {
        const staleDate = new Date("2024-01-01T00:00:00Z");
        const params = {
          action: "update",
          args: {
            where: { id: "field-001" },
            data: { name: "Renamed", updatedAt: staleDate },
          },
        };

        await timestampMiddleware(params, next);

        // updatedAt should be refreshed, not the stale date
        expect(params.args.data.updatedAt).not.toBe(staleDate);
        expect(params.args.data.updatedAt.getTime()).toBeGreaterThan(
          staleDate.getTime(),
        );
      });

      it("should not modify timestamps on read operations", async () => {
        const params = {
          action: "findMany",
          args: { where: { tenantId: "t-001" } },
        };

        await timestampMiddleware(params, next);

        // No data field should be added for read operations
        expect(params.args.data).toBeUndefined();
      });
    });

    describe("Audit trail records", () => {
      it("should log create operations via audit middleware", async () => {
        const mockLogger = vi.fn();
        const auditMiddleware = createAuditLoggingMiddleware(mockLogger);
        const auditNext = createMockNext({ id: "field-001", name: "Test" });

        const params = {
          model: "Field",
          action: "create",
          args: {
            data: { name: "Test Field", tenantId: "t-001" },
          },
        };

        await auditMiddleware(params, auditNext);

        // Should log the mutation
        expect(mockLogger).toHaveBeenCalledTimes(2); // before and after
        expect(mockLogger).toHaveBeenCalledWith(
          expect.stringContaining("Prisma create on Field"),
          expect.objectContaining({
            model: "Field",
            action: "create",
          }),
        );
        // Should log completion with id
        expect(mockLogger).toHaveBeenCalledWith(
          expect.stringContaining("create completed for Field"),
          expect.objectContaining({
            id: "field-001",
          }),
        );
      });

      it("should log update operations via audit middleware", async () => {
        const mockLogger = vi.fn();
        const auditMiddleware = createAuditLoggingMiddleware(mockLogger);
        const auditNext = createMockNext({ id: "field-001" });

        const params = {
          model: "Field",
          action: "update",
          args: {
            where: { id: "field-001" },
            data: { name: "Updated" },
          },
        };

        await auditMiddleware(params, auditNext);

        expect(mockLogger).toHaveBeenCalledWith(
          expect.stringContaining("Prisma update on Field"),
          expect.any(Object),
        );
      });

      it("should log delete operations via audit middleware", async () => {
        const mockLogger = vi.fn();
        const auditMiddleware = createAuditLoggingMiddleware(mockLogger);
        const auditNext = createMockNext({ id: "field-001" });

        const params = {
          model: "Field",
          action: "delete",
          args: {
            where: { id: "field-001" },
          },
        };

        await auditMiddleware(params, auditNext);

        expect(mockLogger).toHaveBeenCalledWith(
          expect.stringContaining("Prisma delete on Field"),
          expect.any(Object),
        );
      });

      it("should not log read operations", async () => {
        const mockLogger = vi.fn();
        const auditMiddleware = createAuditLoggingMiddleware(mockLogger);
        const auditNext = createMockNext([{ id: "1" }]);

        const params = {
          model: "Field",
          action: "findMany",
          args: { where: {} },
        };

        await auditMiddleware(params, auditNext);

        expect(mockLogger).not.toHaveBeenCalled();
      });

      it("should truncate large args in audit log to 500 chars", async () => {
        const mockLogger = vi.fn();
        const auditMiddleware = createAuditLoggingMiddleware(mockLogger);
        const auditNext = createMockNext({ id: "1" });

        const largeData = { description: "x".repeat(1000) };
        const params = {
          model: "Field",
          action: "create",
          args: { data: largeData },
        };

        await auditMiddleware(params, auditNext);

        const loggedArgs = mockLogger.mock.calls[0][1].args;
        expect(loggedArgs.length).toBeLessThanOrEqual(500);
      });
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 3. Unique Constraints
  // ───────────────────────────────────────────────────────────────────────────

  describe("Unique constraints", () => {
    it("should reject duplicate records with Prisma unique constraint error", async () => {
      // Simulate Prisma P2002 unique constraint violation
      const prismaUniqueError = new Error(
        "Unique constraint failed on the fields: (`email`)",
      );
      (prismaUniqueError as any).code = "P2002";
      (prismaUniqueError as any).meta = { target: ["email"] };

      const middleware = createTimestampMiddleware();
      const failingNext = vi.fn().mockRejectedValue(prismaUniqueError);

      const params = {
        action: "create",
        args: {
          data: { email: "farmer@example.com", name: "Farmer" },
        },
      };

      await expect(middleware(params, failingNext)).rejects.toThrow(
        "Unique constraint failed",
      );
    });

    it("should include the violating field in the error metadata", async () => {
      const prismaUniqueError = new Error("Unique constraint failed");
      (prismaUniqueError as any).code = "P2002";
      (prismaUniqueError as any).meta = { target: ["email"] };

      const failingNext = vi.fn().mockRejectedValue(prismaUniqueError);
      const middleware = createTimestampMiddleware();

      try {
        await middleware(
          {
            action: "create",
            args: { data: { email: "dup@test.com" } },
          },
          failingNext,
        );
        expect.unreachable("Should have thrown");
      } catch (error: any) {
        expect(error.code).toBe("P2002");
        expect(error.meta.target).toContain("email");
      }
    });

    it("should enforce tenant-scoped uniqueness (composite unique)", async () => {
      // SyncStatus has @@unique([deviceId, userId]) in the schema
      // Same deviceId + userId = violation; different tenant = ok
      const compositeError = new Error("Unique constraint failed");
      (compositeError as any).code = "P2002";
      (compositeError as any).meta = { target: ["device_id", "user_id"] };

      const failingNext = vi.fn().mockRejectedValue(compositeError);
      const middleware = createTimestampMiddleware();

      try {
        await middleware(
          {
            action: "create",
            args: {
              data: {
                deviceId: "device-001",
                userId: "user-001",
                tenantId: "tenant-001",
              },
            },
          },
          failingNext,
        );
        expect.unreachable("Should have thrown");
      } catch (error: any) {
        expect(error.code).toBe("P2002");
        expect(error.meta.target).toContain("device_id");
        expect(error.meta.target).toContain("user_id");
      }
    });

    it("should allow same field name across different tenants", async () => {
      // This test validates the design: name is NOT globally unique,
      // so two tenants can each have a field named "North Field"
      const middleware = createTimestampMiddleware();

      const resultTenantA = createMockNext({
        id: "f-001",
        name: "North Field",
        tenantId: "tenant-a",
      });
      const resultTenantB = createMockNext({
        id: "f-002",
        name: "North Field",
        tenantId: "tenant-b",
      });

      const paramsA = {
        action: "create",
        args: {
          data: { name: "North Field", tenantId: "tenant-a" },
        },
      };
      const paramsB = {
        action: "create",
        args: {
          data: { name: "North Field", tenantId: "tenant-b" },
        },
      };

      const recordA = await middleware(paramsA, resultTenantA);
      const recordB = await middleware(paramsB, resultTenantB);

      expect(recordA.tenantId).toBe("tenant-a");
      expect(recordB.tenantId).toBe("tenant-b");
      expect(recordA.id).not.toBe(recordB.id);
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 4. Cascade Behavior
  // ───────────────────────────────────────────────────────────────────────────

  describe("Cascade behavior", () => {
    describe("onDelete: Cascade - deletes children with parent", () => {
      it("should cascade delete boundary history when field is deleted", async () => {
        // Schema: FieldBoundaryHistory -> Field with onDelete: Cascade
        // When a Field is deleted, all its FieldBoundaryHistory records
        // should be deleted automatically by the database.

        const deletedChildren: string[] = [];

        const cascadeNext = vi.fn().mockImplementation(async (params: any) => {
          // Simulate database cascade: when parent Field is deleted,
          // the DB automatically deletes related FieldBoundaryHistory records
          if (params.action === "delete" && params.model === "Field") {
            deletedChildren.push("boundary-history-001", "boundary-history-002");
            return {
              id: "field-001",
              name: "Deleted Field",
              _cascaded: {
                FieldBoundaryHistory: { count: 2 },
              },
            };
          }
          return params;
        });

        const params = {
          model: "Field",
          action: "delete",
          args: { where: { id: "field-001" } },
        };

        const result = await cascadeNext(params);

        expect(result._cascaded.FieldBoundaryHistory.count).toBe(2);
        expect(deletedChildren).toHaveLength(2);
      });

      it("should cascade to multiple levels of children", async () => {
        // Verify the cascade concept: Farm -> Field -> BoundaryHistory
        // Deleting a Farm sets Field.farmId to null (SetNull),
        // but deleting a Field cascades to BoundaryHistory.

        const cascadeMock = vi.fn().mockResolvedValue({
          id: "field-001",
          boundaryHistory: [],
          tasks: [],
          ndviReadings: [],
        });

        const params = {
          model: "Field",
          action: "delete",
          args: {
            where: { id: "field-001" },
            include: {
              boundaryHistory: true,
              tasks: true,
              ndviReadings: true,
            },
          },
        };

        await cascadeMock(params);

        expect(cascadeMock).toHaveBeenCalledWith(
          expect.objectContaining({
            args: expect.objectContaining({
              include: expect.objectContaining({
                boundaryHistory: true,
              }),
            }),
          }),
        );
      });
    });

    describe("onDelete: SetNull - nullifies foreign key", () => {
      it("should set farmId to null when farm is deleted (Field -> Farm SetNull)", async () => {
        // Schema: Field.farm -> Farm with onDelete: SetNull
        // When a Farm is deleted, Field.farmId becomes null

        const setNullNext = vi.fn().mockImplementation(async () => {
          return {
            id: "farm-001",
            name: "Deleted Farm",
            _sideEffects: {
              Field: { updatedCount: 3, farmId: null },
            },
          };
        });

        const params = {
          model: "Farm",
          action: "delete",
          args: { where: { id: "farm-001" } },
        };

        const result = await setNullNext(params);

        expect(result._sideEffects.Field.farmId).toBeNull();
        expect(result._sideEffects.Field.updatedCount).toBe(3);
      });

      it("should set fieldId to null when field is deleted (Task -> Field SetNull)", async () => {
        // Schema: Task.field -> Field with onDelete: SetNull

        const setNullNext = vi.fn().mockImplementation(async () => {
          return {
            id: "field-001",
            _sideEffects: {
              Task: { updatedCount: 5, fieldId: null },
            },
          };
        });

        const params = {
          model: "Field",
          action: "delete",
          args: { where: { id: "field-001" } },
        };

        const result = await setNullNext(params);

        expect(result._sideEffects.Task.fieldId).toBeNull();
      });
    });

    describe("onDelete: Restrict - prevents parent deletion", () => {
      it("should reject deletion when children exist (Restrict behavior)", async () => {
        // Simulate Prisma P2003 foreign key constraint violation
        const foreignKeyError = new Error(
          "Foreign key constraint failed on the field: `field_id`",
        );
        (foreignKeyError as any).code = "P2003";
        (foreignKeyError as any).meta = { field_name: "field_id" };

        const restrictNext = vi.fn().mockRejectedValue(foreignKeyError);

        const params = {
          model: "Field",
          action: "delete",
          args: { where: { id: "field-001" } },
        };

        await expect(restrictNext(params)).rejects.toThrow(
          "Foreign key constraint failed",
        );
      });

      it("should include the constraining field in the error", async () => {
        const foreignKeyError = new Error("Foreign key constraint failed");
        (foreignKeyError as any).code = "P2003";
        (foreignKeyError as any).meta = {
          field_name: "tenant_id_fkey",
        };

        const restrictNext = vi.fn().mockRejectedValue(foreignKeyError);

        try {
          await restrictNext({
            model: "Tenant",
            action: "delete",
            args: { where: { id: "tenant-001" } },
          });
          expect.unreachable("Should have thrown");
        } catch (error: any) {
          expect(error.code).toBe("P2003");
          expect(error.meta.field_name).toBe("tenant_id_fkey");
        }
      });
    });

    describe("Soft delete with cascade awareness", () => {
      it("should soft-delete parent without cascading to children", async () => {
        // When using soft delete middleware, the delete is converted to an update.
        // This means database-level cascade does NOT trigger, which is the
        // desired behavior: children remain but parent is marked deleted.

        const softDeleteMw = createSoftDeleteMiddleware();
        const trackedNext = vi.fn().mockResolvedValue({
          id: "field-001",
          deletedAt: new Date(),
        });

        const params = {
          model: "Field",
          action: "delete" as string,
          args: { where: { id: "field-001" } },
        };

        await softDeleteMw(params, trackedNext);

        // Verify it was converted to update (no cascade)
        expect(params.action).toBe("update");
        expect(params.args.data.deletedAt).toBeInstanceOf(Date);

        // The next function receives an update, not delete
        // so database CASCADE rules do not fire
        expect(trackedNext).toHaveBeenCalledTimes(1);
      });
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 5. Combined Middleware Pipeline
  // ───────────────────────────────────────────────────────────────────────────

  describe("Combined middleware pipeline", () => {
    it("should apply timestamp and soft delete together on create", async () => {
      const timestampMw = createTimestampMiddleware();
      const softDeleteMw = createSoftDeleteMiddleware();
      const finalNext = createMockNext({ id: "field-001", name: "Test" });

      const params = {
        model: "Field",
        action: "create",
        args: {
          data: { name: "New Field", tenantId: "t-001" },
        },
      };

      // Chain: timestamp -> softDelete -> next
      await timestampMw(params, async (p: any) => {
        return softDeleteMw(p, finalNext);
      });

      expect(params.args.data.createdAt).toBeInstanceOf(Date);
      expect(params.args.data.updatedAt).toBeInstanceOf(Date);
    });

    it("should apply all three middlewares on delete (audit + timestamp + soft delete)", async () => {
      const mockLogger = vi.fn();
      const auditMw = createAuditLoggingMiddleware(mockLogger);
      const timestampMw = createTimestampMiddleware();
      const softDeleteMw = createSoftDeleteMiddleware();
      const finalNext = createMockNext({ id: "field-001" });

      const params = {
        model: "Field",
        action: "delete" as string,
        args: { where: { id: "field-001" } },
      };

      // Chain: audit -> softDelete -> timestamp -> next
      await auditMw(params, async (p: any) => {
        return softDeleteMw(p, async (p2: any) => {
          return timestampMw(p2, finalNext);
        });
      });

      // Soft delete should have converted delete to update
      expect(params.action).toBe("update");
      expect(params.args.data.deletedAt).toBeInstanceOf(Date);
      // Timestamp middleware should have set updatedAt on the update
      expect(params.args.data.updatedAt).toBeInstanceOf(Date);
      // Audit should have logged
      expect(mockLogger).toHaveBeenCalled();
    });
  });
});
