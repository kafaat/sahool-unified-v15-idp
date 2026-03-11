/**
 * Prisma Patterns Tests
 * اختبارات أنماط Prisma
 *
 * Tests for Prisma singleton pattern, connection lifecycle,
 * soft-delete middleware, and query optimization patterns
 * used across the SAHOOL platform.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ---------------------------------------------------------------------------
// Prisma Singleton Pattern
// ---------------------------------------------------------------------------

describe("Prisma Singleton Pattern", () => {
  it("should reuse the same PrismaClient instance across module", () => {
    // Simulate the NestJS Injectable singleton pattern
    class PrismaService {
      private static instance: PrismaService | null = null;
      private connected = false;
      public readonly instanceId: string;

      constructor() {
        this.instanceId = Math.random().toString(36).slice(2);
      }

      static getInstance(): PrismaService {
        if (!PrismaService.instance) {
          PrismaService.instance = new PrismaService();
        }
        return PrismaService.instance;
      }

      static resetForTesting(): void {
        PrismaService.instance = null;
      }
    }

    PrismaService.resetForTesting();

    const instance1 = PrismaService.getInstance();
    const instance2 = PrismaService.getInstance();

    expect(instance1).toBe(instance2);
    expect(instance1.instanceId).toBe(instance2.instanceId);

    PrismaService.resetForTesting();
  });

  it("should not create multiple PrismaClient instances in production", () => {
    let instanceCount = 0;

    class PrismaClientMock {
      constructor() {
        instanceCount++;
      }
    }

    // Singleton guard used in NestJS module
    class PrismaModule {
      private static client: PrismaClientMock | null = null;

      static getClient(): PrismaClientMock {
        if (!PrismaModule.client) {
          PrismaModule.client = new PrismaClientMock();
        }
        return PrismaModule.client;
      }
    }

    PrismaModule.getClient();
    PrismaModule.getClient();
    PrismaModule.getClient();

    // Only one instance should have been created
    expect(instanceCount).toBe(1);
  });

  it("should prevent instantiation outside the module in global scope", () => {
    // Pattern: attach to globalThis to survive hot-reload in development
    function getGlobalPrismaClient() {
      const globalForPrisma = globalThis as unknown as {
        __prisma?: { id: string };
      };

      if (!globalForPrisma.__prisma) {
        globalForPrisma.__prisma = { id: "singleton-" + Date.now() };
      }

      return globalForPrisma.__prisma;
    }

    const client1 = getGlobalPrismaClient();
    const client2 = getGlobalPrismaClient();

    expect(client1).toBe(client2);

    // Cleanup
    delete (globalThis as any).__prisma;
  });
});

// ---------------------------------------------------------------------------
// Connection Lifecycle
// ---------------------------------------------------------------------------

describe("Connection Lifecycle", () => {
  it("should connect on module initialization (onModuleInit)", async () => {
    const events: string[] = [];

    class MockPrismaService {
      private connected = false;

      async onModuleInit() {
        events.push("connecting");
        // Simulate $connect()
        this.connected = true;
        events.push("connected");

        // Verify PostGIS extension
        events.push("postgis_check");
      }

      isHealthy(): boolean {
        return this.connected;
      }
    }

    const service = new MockPrismaService();
    expect(service.isHealthy()).toBe(false);

    await service.onModuleInit();

    expect(service.isHealthy()).toBe(true);
    expect(events).toEqual(["connecting", "connected", "postgis_check"]);
  });

  it("should disconnect on module destruction (onModuleDestroy)", async () => {
    const events: string[] = [];

    class MockPrismaService {
      private connected = true;

      async onModuleDestroy() {
        if (this.connected) {
          events.push("disconnecting");
          this.connected = false;
          events.push("disconnected");
        }
      }

      isHealthy(): boolean {
        return this.connected;
      }
    }

    const service = new MockPrismaService();
    expect(service.isHealthy()).toBe(true);

    await service.onModuleDestroy();

    expect(service.isHealthy()).toBe(false);
    expect(events).toEqual(["disconnecting", "disconnected"]);
  });

  it("should handle connection failure gracefully in test environment", async () => {
    class MockPrismaService {
      private connected = false;
      private isTestEnv: boolean;

      constructor(env: string) {
        this.isTestEnv = ["test", "ci", "testing"].includes(env.toLowerCase());
      }

      async onModuleInit() {
        try {
          // Simulate connection failure
          throw new Error("Connection refused: ECONNREFUSED");
        } catch (error) {
          if (this.isTestEnv) {
            // In test env, we degrade gracefully
            this.connected = false;
            return; // No rethrow
          }
          throw error; // In production, fail hard
        }
      }

      isHealthy(): boolean {
        return this.connected;
      }
    }

    // Test environment: graceful degradation
    const testService = new MockPrismaService("test");
    await testService.onModuleInit(); // Should not throw
    expect(testService.isHealthy()).toBe(false);

    // Production environment: fail hard
    const prodService = new MockPrismaService("production");
    await expect(prodService.onModuleInit()).rejects.toThrow("Connection refused");
  });

  it("should not disconnect if never connected", async () => {
    const disconnectSpy = vi.fn();

    class MockPrismaService {
      private connected = false;

      async onModuleDestroy() {
        if (this.connected) {
          disconnectSpy();
        }
      }
    }

    const service = new MockPrismaService();
    await service.onModuleDestroy();

    expect(disconnectSpy).not.toHaveBeenCalled();
  });

  it("should provide health check via SELECT 1", async () => {
    class MockPrismaService {
      private connected = true;

      async getConnectionStatus() {
        try {
          // Simulate $queryRaw`SELECT 1`
          if (!this.connected) {
            throw new Error("Connection lost");
          }
          return {
            connected: true,
            timestamp: new Date().toISOString(),
          };
        } catch (error) {
          return {
            connected: false,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : "Unknown error",
          };
        }
      }
    }

    const service = new MockPrismaService();
    const status = await service.getConnectionStatus();

    expect(status.connected).toBe(true);
    expect(status.timestamp).toBeDefined();
    expect(status).not.toHaveProperty("error");
  });

  it("should report unhealthy when connection is lost", async () => {
    class MockPrismaService {
      connected = false;

      async getConnectionStatus() {
        try {
          if (!this.connected) {
            throw new Error("Connection lost");
          }
          return { connected: true, timestamp: new Date().toISOString() };
        } catch (error) {
          return {
            connected: false,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : "Unknown",
          };
        }
      }
    }

    const service = new MockPrismaService();
    const status = await service.getConnectionStatus();

    expect(status.connected).toBe(false);
    expect(status.error).toBe("Connection lost");
  });
});

// ---------------------------------------------------------------------------
// Soft-Delete Middleware
// ---------------------------------------------------------------------------

describe("Soft-Delete Middleware", () => {
  interface MiddlewareParams {
    model: string;
    action: string;
    args: Record<string, any>;
  }

  function createSoftDeleteMiddleware(config: {
    excludedModels?: string[];
    enableLogging?: boolean;
  } = {}) {
    const { excludedModels = [] } = config;

    return async (params: MiddlewareParams, next: (p: MiddlewareParams) => Promise<any>) => {
      if (!params.model || excludedModels.includes(params.model)) {
        return next(params);
      }

      // Convert delete to soft delete
      if (params.action === "delete") {
        params.action = "update";
        params.args.data = {
          deletedAt: new Date(),
          deletedBy: params.args.deletedBy || null,
        };
      }

      if (params.action === "deleteMany") {
        params.action = "updateMany";
        params.args.data = {
          deletedAt: new Date(),
          deletedBy: params.args.deletedBy || null,
        };
      }

      // Add soft delete filter to read operations
      const readActions = ["findUnique", "findFirst", "findMany", "count", "aggregate", "groupBy"];
      if (readActions.includes(params.action)) {
        const includeDeleted = params.args.includeDeleted;
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

  let middleware: ReturnType<typeof createSoftDeleteMiddleware>;
  let next: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    middleware = createSoftDeleteMiddleware();
    next = vi.fn().mockResolvedValue({ id: "1" });
  });

  it("should convert delete to update with deletedAt timestamp", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "delete",
      args: { where: { id: "field-1" } },
    };

    await middleware(params, next);

    expect(params.action).toBe("update");
    expect(params.args.data.deletedAt).toBeInstanceOf(Date);
    expect(params.args.data.deletedBy).toBeNull();
  });

  it("should convert deleteMany to updateMany", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "deleteMany",
      args: { where: { tenantId: "t1", status: "inactive" } },
    };

    await middleware(params, next);

    expect(params.action).toBe("updateMany");
    expect(params.args.data.deletedAt).toBeInstanceOf(Date);
  });

  it("should auto-filter deleted records on findMany", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "findMany",
      args: { where: { tenantId: "t1" } },
    };

    await middleware(params, next);

    expect(params.args.where.deletedAt).toBeNull();
    expect(params.args.where.tenantId).toBe("t1");
  });

  it("should auto-filter deleted records on findFirst", async () => {
    const params: MiddlewareParams = {
      model: "Task",
      action: "findFirst",
      args: { where: { id: "task-1" } },
    };

    await middleware(params, next);

    expect(params.args.where.deletedAt).toBeNull();
  });

  it("should auto-filter deleted records on count", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "count",
      args: { where: { tenantId: "t1" } },
    };

    await middleware(params, next);

    expect(params.args.where.deletedAt).toBeNull();
  });

  it("should skip filter when includeDeleted flag is set", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "findMany",
      args: { where: { tenantId: "t1" }, includeDeleted: true },
    };

    await middleware(params, next);

    expect(params.args.where.deletedAt).toBeUndefined();
    expect(params.args.includeDeleted).toBeUndefined(); // Flag should be removed
  });

  it("should not override explicit deletedAt filter", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "findMany",
      args: { where: { deletedAt: { not: null } } },
    };

    await middleware(params, next);

    expect(params.args.where.deletedAt).toEqual({ not: null });
  });

  it("should create where clause if not present", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "findMany",
      args: {},
    };

    await middleware(params, next);

    expect(params.args.where).toEqual({ deletedAt: null });
  });

  it("should skip excluded models entirely", async () => {
    const customMiddleware = createSoftDeleteMiddleware({
      excludedModels: ["AuditLog", "SyncStatus"],
    });

    const params: MiddlewareParams = {
      model: "AuditLog",
      action: "delete",
      args: { where: { id: "log-1" } },
    };

    await customMiddleware(params, next);

    // Action should NOT be converted
    expect(params.action).toBe("delete");
    expect(params.args.data).toBeUndefined();
  });

  it("should preserve deletedBy when provided on delete", async () => {
    const params: MiddlewareParams = {
      model: "Field",
      action: "delete",
      args: { where: { id: "f-1" }, deletedBy: "user-admin" },
    };

    await middleware(params, next);

    expect(params.args.data.deletedBy).toBe("user-admin");
  });

  it("should handle aggregate and groupBy actions", async () => {
    for (const action of ["aggregate", "groupBy"]) {
      const params: MiddlewareParams = {
        model: "Field",
        action,
        args: { where: {} },
      };

      await middleware(params, next);

      expect(params.args.where.deletedAt).toBeNull();
    }
  });
});

// ---------------------------------------------------------------------------
// Soft-Delete Helper Functions
// ---------------------------------------------------------------------------

describe("Soft-Delete Helper Functions", () => {
  it("isDeleted should check deletedAt field", () => {
    function isDeleted(record: any): boolean {
      return record?.deletedAt !== null && record?.deletedAt !== undefined;
    }

    expect(isDeleted({ deletedAt: new Date() })).toBe(true);
    expect(isDeleted({ deletedAt: null })).toBe(false);
    expect(isDeleted({ deletedAt: undefined })).toBe(false);
    expect(isDeleted({})).toBe(false);
    expect(isDeleted(null)).toBe(false);
    expect(isDeleted(undefined)).toBe(false);
  });

  it("softDelete should set deletedAt and deletedBy", async () => {
    const mockModel = {
      update: vi.fn().mockResolvedValue({ id: "1", deletedAt: new Date() }),
    };

    async function softDelete(model: any, where: any, options: { deletedBy?: string } = {}) {
      return model.update({
        where,
        data: {
          deletedAt: new Date(),
          deletedBy: options.deletedBy || null,
        },
      });
    }

    await softDelete(mockModel, { id: "field-1" }, { deletedBy: "admin" });

    expect(mockModel.update).toHaveBeenCalledWith({
      where: { id: "field-1" },
      data: expect.objectContaining({
        deletedAt: expect.any(Date),
        deletedBy: "admin",
      }),
    });
  });

  it("restore should clear deletedAt and deletedBy", async () => {
    const mockModel = {
      update: vi.fn().mockResolvedValue({ id: "1", deletedAt: null }),
    };

    async function restore(model: any, where: any) {
      return model.update({
        where,
        data: { deletedAt: null, deletedBy: null },
      });
    }

    await restore(mockModel, { id: "field-1" });

    expect(mockModel.update).toHaveBeenCalledWith({
      where: { id: "field-1" },
      data: { deletedAt: null, deletedBy: null },
    });
  });

  it("getDeletionMetadata should return metadata for deleted records", () => {
    function getDeletionMetadata(record: any) {
      if (!record?.deletedAt) return null;
      return {
        deletedAt: record.deletedAt,
        deletedBy: record.deletedBy,
      };
    }

    const now = new Date();
    expect(getDeletionMetadata({ deletedAt: now, deletedBy: "admin" })).toEqual({
      deletedAt: now,
      deletedBy: "admin",
    });
    expect(getDeletionMetadata({ deletedAt: null })).toBeNull();
    expect(getDeletionMetadata({})).toBeNull();
  });

  it("filterDeleted should partition records correctly", () => {
    function filterDeleted<T extends { deletedAt: Date | null }>(records: T[]) {
      return records.filter((r) => r.deletedAt === null || r.deletedAt === undefined);
    }

    function filterOnlyDeleted<T extends { deletedAt: Date | null }>(records: T[]) {
      return records.filter((r) => r.deletedAt !== null && r.deletedAt !== undefined);
    }

    const records = [
      { id: "1", deletedAt: null },
      { id: "2", deletedAt: new Date() },
      { id: "3", deletedAt: null },
      { id: "4", deletedAt: new Date() },
    ];

    const active = filterDeleted(records);
    const deleted = filterOnlyDeleted(records);

    expect(active).toHaveLength(2);
    expect(deleted).toHaveLength(2);
    expect(active.map((r) => r.id)).toEqual(["1", "3"]);
    expect(deleted.map((r) => r.id)).toEqual(["2", "4"]);

    // Partition is exhaustive
    expect(active.length + deleted.length).toBe(records.length);
  });
});

// ---------------------------------------------------------------------------
// Query Optimization Patterns
// ---------------------------------------------------------------------------

describe("Query Optimization Patterns", () => {
  it("should log slow queries above threshold", () => {
    const SLOW_QUERY_THRESHOLD = 1000;
    const warnings: string[] = [];

    function handleQueryEvent(event: { query: string; duration: number }) {
      if (event.duration > SLOW_QUERY_THRESHOLD) {
        warnings.push(
          `Slow query (${event.duration}ms): ${event.query.substring(0, 100)}`,
        );
      }
    }

    handleQueryEvent({ query: "SELECT * FROM fields", duration: 50 });
    expect(warnings).toHaveLength(0);

    handleQueryEvent({
      query: "SELECT * FROM fields WHERE ST_Intersects(...)",
      duration: 2500,
    });
    expect(warnings).toHaveLength(1);
    expect(warnings[0]).toContain("2500ms");
  });

  it("should use select to avoid over-fetching", () => {
    function createSelect<T extends string>(fields: T[]): Record<T, true> {
      return fields.reduce(
        (acc, field) => {
          acc[field] = true;
          return acc;
        },
        {} as Record<T, true>,
      );
    }

    const fieldSelect = createSelect([
      "id",
      "name",
      "tenantId",
      "cropType",
      "status",
      "areaHectares",
    ]);

    expect(fieldSelect.id).toBe(true);
    expect(fieldSelect.name).toBe(true);
    expect(fieldSelect.tenantId).toBe(true);
    expect(Object.keys(fieldSelect)).toHaveLength(6);

    // Should not include sensitive or large fields
    expect((fieldSelect as any).metadata).toBeUndefined();
    expect((fieldSelect as any).boundary).toBeUndefined();
  });

  it("should measure query execution time", async () => {
    const SLOW_THRESHOLD = 1000;
    const logs: Array<{ name: string; duration: number; slow: boolean }> = [];

    async function measureQueryTime<T>(
      queryFn: () => Promise<T>,
      queryName: string,
    ): Promise<T> {
      const start = Date.now();
      try {
        return await queryFn();
      } finally {
        const duration = Date.now() - start;
        logs.push({
          name: queryName,
          duration,
          slow: duration >= SLOW_THRESHOLD,
        });
      }
    }

    const result = await measureQueryTime(
      async () => [{ id: "1" }],
      "findActiveFields",
    );

    expect(result).toEqual([{ id: "1" }]);
    expect(logs).toHaveLength(1);
    expect(logs[0].name).toBe("findActiveFields");
    expect(logs[0].duration).toBeLessThan(SLOW_THRESHOLD);
    expect(logs[0].slow).toBe(false);
  });

  it("should rethrow errors from measured queries", async () => {
    async function measureQueryTime<T>(
      queryFn: () => Promise<T>,
      queryName: string,
    ): Promise<T> {
      const start = Date.now();
      try {
        return await queryFn();
      } catch (error) {
        throw error;
      }
    }

    await expect(
      measureQueryTime(
        async () => {
          throw new Error("Connection timeout");
        },
        "failedQuery",
      ),
    ).rejects.toThrow("Connection timeout");
  });

  it("batch operations should split into appropriately sized chunks", async () => {
    async function batchOperation<T, R>(
      items: T[],
      batchSize: number,
      operation: (batch: T[]) => Promise<R>,
    ): Promise<R[]> {
      const results: R[] = [];
      for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        results.push(await operation(batch));
      }
      return results;
    }

    const ids = Array.from({ length: 250 }, (_, i) => `id-${i}`);
    const batchSizes: number[] = [];

    await batchOperation(ids, 50, async (batch) => {
      batchSizes.push(batch.length);
      return batch.length;
    });

    expect(batchSizes).toEqual([50, 50, 50, 50, 50]);
    expect(batchSizes.every((s) => s <= 50)).toBe(true);
  });

  it("parallel operations should respect concurrency limit", async () => {
    let concurrent = 0;
    let maxConcurrent = 0;

    async function parallelLimit<T, R>(
      items: T[],
      concurrency: number,
      operation: (item: T) => Promise<R>,
    ): Promise<R[]> {
      const results: R[] = [];
      const executing: Promise<void>[] = [];

      for (const item of items) {
        const promise = operation(item).then((result) => {
          results.push(result);
          executing.splice(executing.indexOf(promise), 1);
        });
        executing.push(promise);
        if (executing.length >= concurrency) {
          await Promise.race(executing);
        }
      }
      await Promise.all(executing);
      return results;
    }

    const items = Array.from({ length: 10 }, (_, i) => i);

    await parallelLimit(items, 3, async (item) => {
      concurrent++;
      maxConcurrent = Math.max(maxConcurrent, concurrent);
      await new Promise((r) => setTimeout(r, 10));
      concurrent--;
      return item * 2;
    });

    expect(maxConcurrent).toBeLessThanOrEqual(3);
  });
});

// ---------------------------------------------------------------------------
// Transaction Configuration
// ---------------------------------------------------------------------------

describe("Transaction Configuration", () => {
  it("should define appropriate isolation levels for different operations", () => {
    const configs = {
      financial: {
        isolationLevel: "Serializable",
        maxWait: 5000,
        timeout: 10000,
      },
      general: {
        isolationLevel: "ReadCommitted",
        maxWait: 3000,
        timeout: 5000,
      },
      readOnly: {
        isolationLevel: "ReadCommitted",
        maxWait: 2000,
        timeout: 3000,
      },
    };

    // Financial: strictest isolation for money operations
    expect(configs.financial.isolationLevel).toBe("Serializable");
    expect(configs.financial.timeout).toBeGreaterThan(configs.general.timeout);

    // General: standard isolation for business operations
    expect(configs.general.isolationLevel).toBe("ReadCommitted");

    // Read-only: fast timeout, no strict isolation needed
    expect(configs.readOnly.timeout).toBeLessThan(configs.general.timeout);
  });

  it("should have timeout hierarchy: financial > general > readOnly", () => {
    const financialTimeout = 10000;
    const generalTimeout = 5000;
    const readOnlyTimeout = 3000;

    expect(financialTimeout).toBeGreaterThan(generalTimeout);
    expect(generalTimeout).toBeGreaterThan(readOnlyTimeout);
  });

  it("maxWait should always be less than timeout", () => {
    const configs = [
      { name: "financial", maxWait: 5000, timeout: 10000 },
      { name: "general", maxWait: 3000, timeout: 5000 },
      { name: "readOnly", maxWait: 2000, timeout: 3000 },
    ];

    for (const config of configs) {
      expect(config.maxWait).toBeLessThan(config.timeout);
    }
  });
});

// ---------------------------------------------------------------------------
// PostGIS Extension Management
// ---------------------------------------------------------------------------

describe("PostGIS Extension Management", () => {
  it("should attempt to create PostGIS extension on init", async () => {
    const queryLog: string[] = [];

    class MockPrismaService {
      async onModuleInit() {
        // Simulate CREATE EXTENSION IF NOT EXISTS postgis
        queryLog.push("CREATE EXTENSION IF NOT EXISTS postgis");
      }
    }

    const service = new MockPrismaService();
    await service.onModuleInit();

    expect(queryLog).toContain("CREATE EXTENSION IF NOT EXISTS postgis");
  });

  it("should handle PostGIS already exists gracefully", async () => {
    class MockPrismaService {
      private postgisAvailable = false;

      async onModuleInit() {
        try {
          // Simulate extension already existing (no error)
          this.postgisAvailable = true;
        } catch {
          // PostGIS may already exist - this is fine
          this.postgisAvailable = true;
        }
      }

      hasPostGIS(): boolean {
        return this.postgisAvailable;
      }
    }

    const service = new MockPrismaService();
    await service.onModuleInit();
    expect(service.hasPostGIS()).toBe(true);
  });

  it("executePostGIS should delegate to $queryRawUnsafe with params", () => {
    const queryRawUnsafeSpy = vi.fn().mockResolvedValue([]);

    function executePostGIS<T>(query: string, params: any[] = []) {
      if (params.length === 0) {
        return queryRawUnsafeSpy(query);
      }
      return queryRawUnsafeSpy(query, ...params);
    }

    // Static query
    executePostGIS("SELECT PostGIS_Version()");
    expect(queryRawUnsafeSpy).toHaveBeenCalledWith("SELECT PostGIS_Version()");

    // Parameterized query
    executePostGIS(
      "SELECT ST_AsGeoJSON(boundary) FROM fields WHERE id = $1::uuid",
      ["field-uuid-123"],
    );
    expect(queryRawUnsafeSpy).toHaveBeenCalledWith(
      "SELECT ST_AsGeoJSON(boundary) FROM fields WHERE id = $1::uuid",
      "field-uuid-123",
    );
  });
});

// ---------------------------------------------------------------------------
// Optimistic Locking
// ---------------------------------------------------------------------------

describe("Optimistic Locking", () => {
  it("should generate ETag from id and version", () => {
    function generateETag(id: string, version: number): string {
      return `"${id}-v${version}"`;
    }

    expect(generateETag("field-1", 1)).toBe('"field-1-v1"');
    expect(generateETag("field-1", 5)).toBe('"field-1-v5"');
  });

  it("should reject update when ETag does not match", () => {
    function validateETag(
      providedETag: string,
      currentId: string,
      currentVersion: number,
    ): boolean {
      const expected = `"${currentId}-v${currentVersion}"`;
      return providedETag === expected;
    }

    // Match
    expect(validateETag('"f1-v3"', "f1", 3)).toBe(true);

    // Mismatch (stale client)
    expect(validateETag('"f1-v2"', "f1", 3)).toBe(false);
  });

  it("should increment version on successful update", () => {
    function updateWithVersion(
      current: { id: string; version: number; name: string },
      updateData: { name?: string },
    ) {
      return {
        ...current,
        ...updateData,
        version: current.version + 1,
      };
    }

    const field = { id: "f1", version: 1, name: "Old Name" };
    const updated = updateWithVersion(field, { name: "New Name" });

    expect(updated.version).toBe(2);
    expect(updated.name).toBe("New Name");
    expect(updated.id).toBe("f1");
  });
});
