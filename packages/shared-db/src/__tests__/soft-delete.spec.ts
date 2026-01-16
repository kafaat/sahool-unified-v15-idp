/**
 * اختبارات نظام الحذف الناعم
 * Soft Delete Pattern Tests
 *
 * Tests for Prisma soft delete middleware and helper functions.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  createSoftDeleteMiddleware,
  softDelete,
  softDeleteMany,
  restore,
  restoreMany,
  findWithDeleted,
  findFirstWithDeleted,
  isDeleted,
  hardDelete,
  count,
  countWithDeleted,
  getDeletionMetadata,
  filterDeleted,
  filterOnlyDeleted,
} from "../soft-delete";

// Type for middleware params that can be mutated
interface MiddlewareParams {
  model: string;
  action: string;
  args: {
    where?: Record<string, unknown>;
    data?: Record<string, unknown>;
    deletedBy?: string;
    includeDeleted?: boolean;
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Middleware Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("createSoftDeleteMiddleware", () => {
  let middleware: ReturnType<typeof createSoftDeleteMiddleware>;
  let next: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    middleware = createSoftDeleteMiddleware();
    next = vi.fn().mockResolvedValue({ id: "1" });
  });

  describe("DELETE operations", () => {
    it("should convert delete to update with deletedAt", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "delete",
        args: { where: { id: "123" } },
      };

      await middleware(params, next);

      expect(params.action).toBe("update");
      expect(params.args.data?.deletedAt).toBeInstanceOf(Date);
      expect(params.args.data?.deletedBy).toBeNull();
    });

    it("should include deletedBy when provided", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "delete",
        args: { where: { id: "123" }, deletedBy: "user-456" },
      };

      await middleware(params, next);

      expect(params.args.data?.deletedBy).toBe("user-456");
    });

    it("should convert deleteMany to updateMany", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "deleteMany",
        args: { where: { status: "DEPRECATED" } },
      };

      await middleware(params, next);

      expect(params.action).toBe("updateMany");
      expect(params.args.data?.deletedAt).toBeInstanceOf(Date);
    });
  });

  describe("FIND operations", () => {
    it("should add deletedAt filter to findMany", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "findMany",
        args: { where: {} },
      };

      await middleware(params, next);

      expect(params.args.where?.deletedAt).toBeNull();
    });

    it("should add deletedAt filter to findUnique", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "findUnique",
        args: { where: { id: "123" } },
      };

      await middleware(params, next);

      expect(params.args.where?.deletedAt).toBeNull();
    });

    it("should add deletedAt filter to count", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "count",
        args: { where: {} },
      };

      await middleware(params, next);

      expect(params.args.where?.deletedAt).toBeNull();
    });

    it("should not override existing deletedAt filter", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "findMany",
        args: { where: { deletedAt: { not: null } } },
      };

      await middleware(params, next);

      expect(params.args.where?.deletedAt).toEqual({ not: null });
    });

    it("should skip filter when includeDeleted is true", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "findMany",
        args: { where: {}, includeDeleted: true },
      };

      await middleware(params, next);

      expect(params.args.where?.deletedAt).toBeUndefined();
      expect(params.args.includeDeleted).toBeUndefined(); // Should be removed
    });

    it("should create where clause if not present", async () => {
      const params: MiddlewareParams = {
        model: "Product",
        action: "findMany",
        args: {},
      };

      await middleware(params, next);

      expect(params.args.where).toEqual({ deletedAt: null });
    });
  });

  describe("Excluded models", () => {
    it("should skip soft delete for excluded models", async () => {
      const customMiddleware = createSoftDeleteMiddleware({
        excludedModels: ["AuditLog"],
      });

      const params: MiddlewareParams = {
        model: "AuditLog",
        action: "delete",
        args: { where: { id: "123" } },
      };

      await customMiddleware(params, next);

      expect(params.action).toBe("delete"); // Not converted
    });
  });

  describe("Logging", () => {
    it("should log when enableLogging is true", async () => {
      const mockLogger = vi.fn();
      const customMiddleware = createSoftDeleteMiddleware({
        enableLogging: true,
        logger: mockLogger,
      });

      const params: MiddlewareParams = {
        model: "Product",
        action: "delete",
        args: { where: { id: "123" } },
      };

      await customMiddleware(params, next);

      expect(mockLogger).toHaveBeenCalled();
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("softDelete", () => {
  it("should call update with deletedAt", async () => {
    const mockModel = {
      update: vi.fn().mockResolvedValue({ id: "123", deletedAt: new Date() }),
    };

    const result = await softDelete(mockModel, { id: "123" });

    expect(mockModel.update).toHaveBeenCalledWith({
      where: { id: "123" },
      data: expect.objectContaining({
        deletedAt: expect.any(Date),
        deletedBy: null,
      }),
    });
    expect(result.deletedAt).toBeInstanceOf(Date);
  });

  it("should include deletedBy when provided", async () => {
    const mockModel = {
      update: vi.fn().mockResolvedValue({ id: "123" }),
    };

    await softDelete(mockModel, { id: "123" }, { deletedBy: "user-456" });

    expect(mockModel.update).toHaveBeenCalledWith({
      where: { id: "123" },
      data: expect.objectContaining({
        deletedBy: "user-456",
      }),
    });
  });
});

describe("softDeleteMany", () => {
  it("should call updateMany with deletedAt", async () => {
    const mockModel = {
      updateMany: vi.fn().mockResolvedValue({ count: 5 }),
    };

    const result = await softDeleteMany(mockModel, { category: "OLD" });

    expect(mockModel.updateMany).toHaveBeenCalledWith({
      where: { category: "OLD" },
      data: expect.objectContaining({
        deletedAt: expect.any(Date),
        deletedBy: null,
      }),
    });
    expect(result.count).toBe(5);
  });
});

describe("restore", () => {
  it("should set deletedAt and deletedBy to null", async () => {
    const mockModel = {
      update: vi.fn().mockResolvedValue({ id: "123", deletedAt: null }),
    };

    await restore(mockModel, { id: "123" });

    expect(mockModel.update).toHaveBeenCalledWith({
      where: { id: "123" },
      data: expect.objectContaining({
        deletedAt: null,
        deletedBy: null,
      }),
    });
  });

  it("should include updatedAt when restoredBy provided", async () => {
    const mockModel = {
      update: vi.fn().mockResolvedValue({ id: "123" }),
    };

    await restore(mockModel, { id: "123" }, { restoredBy: "admin" });

    expect(mockModel.update).toHaveBeenCalledWith({
      where: { id: "123" },
      data: expect.objectContaining({
        deletedAt: null,
        deletedBy: null,
        updatedAt: expect.any(Date),
      }),
    });
  });
});

describe("restoreMany", () => {
  it("should restore multiple records", async () => {
    const mockModel = {
      updateMany: vi.fn().mockResolvedValue({ count: 3 }),
    };

    const result = await restoreMany(mockModel, { category: "RESTORED" });

    expect(mockModel.updateMany).toHaveBeenCalledWith({
      where: { category: "RESTORED" },
      data: { deletedAt: null, deletedBy: null },
    });
    expect(result.count).toBe(3);
  });
});

describe("findWithDeleted", () => {
  it("should pass includeDeleted flag", async () => {
    const mockModel = {
      findMany: vi.fn().mockResolvedValue([{ id: "1" }, { id: "2" }]),
    };

    await findWithDeleted(mockModel, { where: { category: "TEST" } });

    expect(mockModel.findMany).toHaveBeenCalledWith({
      where: { category: "TEST" },
      includeDeleted: true,
    });
  });
});

describe("findFirstWithDeleted", () => {
  it("should pass includeDeleted flag", async () => {
    const mockModel = {
      findFirst: vi.fn().mockResolvedValue({ id: "1" }),
    };

    await findFirstWithDeleted(mockModel, { where: { id: "123" } });

    expect(mockModel.findFirst).toHaveBeenCalledWith({
      where: { id: "123" },
      includeDeleted: true,
    });
  });
});

describe("isDeleted", () => {
  it("should return true when deletedAt is set", () => {
    const record = { id: "1", deletedAt: new Date() };
    expect(isDeleted(record)).toBe(true);
  });

  it("should return false when deletedAt is null", () => {
    const record = { id: "1", deletedAt: null };
    expect(isDeleted(record)).toBe(false);
  });

  it("should return false when deletedAt is undefined", () => {
    const record = { id: "1" };
    expect(isDeleted(record)).toBe(false);
  });

  it("should return false for null record", () => {
    expect(isDeleted(null)).toBe(false);
  });
});

describe("hardDelete", () => {
  it("should call delete directly", async () => {
    const mockModel = {
      delete: vi.fn().mockResolvedValue({ id: "123" }),
    };

    await hardDelete(mockModel, { id: "123" });

    expect(mockModel.delete).toHaveBeenCalledWith({ where: { id: "123" } });
  });
});

describe("count", () => {
  it("should count non-deleted records", async () => {
    const mockModel = {
      count: vi.fn().mockResolvedValue(10),
    };

    const result = await count(mockModel, { status: "ACTIVE" });

    expect(mockModel.count).toHaveBeenCalledWith({
      where: {
        status: "ACTIVE",
        deletedAt: null,
      },
    });
    expect(result).toBe(10);
  });

  it("should work without where clause", async () => {
    const mockModel = {
      count: vi.fn().mockResolvedValue(5),
    };

    await count(mockModel);

    expect(mockModel.count).toHaveBeenCalledWith({
      where: { deletedAt: null },
    });
  });
});

describe("countWithDeleted", () => {
  it("should count all records including deleted", async () => {
    const mockModel = {
      count: vi.fn().mockResolvedValue(15),
    };

    const result = await countWithDeleted(mockModel, { status: "ACTIVE" });

    expect(mockModel.count).toHaveBeenCalledWith({
      where: { status: "ACTIVE" },
      includeDeleted: true,
    });
    expect(result).toBe(15);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Utility Functions Tests
// ─────────────────────────────────────────────────────────────────────────────

describe("getDeletionMetadata", () => {
  it("should return metadata for deleted record", () => {
    const deletedAt = new Date();
    const record = {
      id: "1",
      deletedAt,
      deletedBy: "user-123",
    };

    const metadata = getDeletionMetadata(record);

    expect(metadata).toEqual({
      deletedAt,
      deletedBy: "user-123",
    });
  });

  it("should return null for non-deleted record", () => {
    const record = { id: "1", deletedAt: null, deletedBy: null };

    expect(getDeletionMetadata(record)).toBeNull();
  });
});

describe("filterDeleted", () => {
  it("should filter out deleted records", () => {
    const records = [
      { id: "1", deletedAt: null },
      { id: "2", deletedAt: new Date() },
      { id: "3", deletedAt: null },
      { id: "4", deletedAt: new Date() },
    ];

    const filtered = filterDeleted(records);

    expect(filtered).toHaveLength(2);
    expect(filtered.map((r) => r.id)).toEqual(["1", "3"]);
  });

  it("should handle empty array", () => {
    expect(filterDeleted([])).toEqual([]);
  });
});

describe("filterOnlyDeleted", () => {
  it("should return only deleted records", () => {
    const records = [
      { id: "1", deletedAt: null },
      { id: "2", deletedAt: new Date() },
      { id: "3", deletedAt: null },
      { id: "4", deletedAt: new Date() },
    ];

    const filtered = filterOnlyDeleted(records);

    expect(filtered).toHaveLength(2);
    expect(filtered.map((r) => r.id)).toEqual(["2", "4"]);
  });

  it("should handle empty array", () => {
    expect(filterOnlyDeleted([])).toEqual([]);
  });
});
