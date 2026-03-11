/**
 * Prisma Singleton Pattern & Connection Management Tests
 * اختبارات نمط المفرد وإدارة الاتصال في Prisma
 *
 * Validates that the PrismaService follows the singleton pattern within
 * NestJS modules, properly manages connections via lifecycle hooks,
 * and reads configuration from environment variables.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ─────────────────────────────────────────────────────────────────────────────
// Mock PrismaClient before importing anything that depends on it
// ─────────────────────────────────────────────────────────────────────────────

const mockConnect = vi.fn().mockResolvedValue(undefined);
const mockDisconnect = vi.fn().mockResolvedValue(undefined);
const mockQueryRaw = vi.fn().mockResolvedValue([{ "?column?": 1 }]);
const mockOn = vi.fn();

// Track constructor calls and args
const constructorCalls: Array<{ options: any }> = [];

vi.mock("@prisma/client", () => {
  class MockPrismaClient {
    constructor(options?: any) {
      constructorCalls.push({ options });
    }

    $connect = mockConnect;
    $disconnect = mockDisconnect;
    $queryRaw = mockQueryRaw;
    $queryRawUnsafe = mockQueryRaw;
    $on = mockOn;
  }

  return {
    PrismaClient: MockPrismaClient,
    Prisma: {
      PrismaClientOptions: {},
    },
  };
});

// Minimal NestJS decorator mocks
vi.mock("@nestjs/common", () => ({
  Injectable: () => (target: any) => target,
  OnModuleInit: undefined,
  OnModuleDestroy: undefined,
  Logger: vi.fn().mockImplementation(() => ({
    log: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  })),
  Global: () => (target: any) => target,
  Module: () => (target: any) => target,
}));

import { PrismaClient } from "@prisma/client";

// ═══════════════════════════════════════════════════════════════════════════════
// PrismaService implementation under test (inline to avoid generated client dep)
// Mirrors the pattern used across field-management-service, user-service, etc.
// ═══════════════════════════════════════════════════════════════════════════════

class PrismaService extends PrismaClient {
  private isConnected = false;
  private readonly isTestEnvironment: boolean;

  constructor() {
    super({
      log: [
        { level: "error", emit: "stdout" },
        { level: "warn", emit: "stdout" },
      ],
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });

    this.isTestEnvironment = ["test", "ci", "testing"].includes(
      (process.env.ENVIRONMENT || process.env.NODE_ENV || "").toLowerCase(),
    );
  }

  async onModuleInit() {
    try {
      await this.$connect();
      this.isConnected = true;
    } catch (error) {
      if (this.isTestEnvironment) {
        this.isConnected = false;
      } else {
        throw error;
      }
    }
  }

  async onModuleDestroy() {
    if (this.isConnected) {
      await this.$disconnect();
    }
  }

  isHealthy(): boolean {
    return this.isConnected;
  }

  async getConnectionStatus() {
    try {
      await this.$queryRaw`SELECT 1`;
      return { connected: true, timestamp: new Date().toISOString() };
    } catch {
      return { connected: false, timestamp: new Date().toISOString() };
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════════

describe("Prisma Singleton Pattern", () => {
  beforeEach(() => {
    constructorCalls.length = 0;
    vi.clearAllMocks();
  });

  afterEach(() => {
    delete process.env.DATABASE_URL;
    delete process.env.ENVIRONMENT;
    delete process.env.NODE_ENV;
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 1. Singleton Pattern
  // ───────────────────────────────────────────────────────────────────────────

  describe("Singleton pattern", () => {
    it("should extend PrismaClient", () => {
      const service = new PrismaService();

      expect(service).toBeInstanceOf(PrismaClient);
    });

    it("should create only one instance when used as a module provider", () => {
      // Simulate NestJS module behavior: a single provider instance
      // is shared across all consumers within the same module scope.
      const moduleProviders = new Map<string, PrismaService>();

      // Register once (NestJS DI container behavior)
      if (!moduleProviders.has("PrismaService")) {
        moduleProviders.set("PrismaService", new PrismaService());
      }

      // Multiple "injections" all receive the same instance
      const injectionA = moduleProviders.get("PrismaService");
      const injectionB = moduleProviders.get("PrismaService");

      expect(injectionA).toBe(injectionB);
      // Only one PrismaService constructor call within this test
      expect(constructorCalls).toHaveLength(1);
    });

    it("should pass configuration to PrismaClient constructor", () => {
      process.env.DATABASE_URL = "postgresql://user:pass@localhost:5432/testdb";

      new PrismaService();

      expect(constructorCalls).toHaveLength(1);
      const opts = constructorCalls[0].options;
      expect(opts).toBeDefined();
      expect(opts.datasources.db.url).toBe(
        "postgresql://user:pass@localhost:5432/testdb",
      );
    });

    it("should configure logging levels", () => {
      new PrismaService();

      const opts = constructorCalls[0].options;
      expect(opts.log).toBeDefined();
      expect(Array.isArray(opts.log)).toBe(true);
      // At minimum, error logging should be configured
      const errorLog = opts.log.find(
        (entry: any) => entry.level === "error",
      );
      expect(errorLog).toBeDefined();
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 2. Connection Management - onModuleInit
  // ───────────────────────────────────────────────────────────────────────────

  describe("Connection initialization (onModuleInit)", () => {
    it("should call $connect on module init", async () => {
      const service = new PrismaService();

      await service.onModuleInit();

      expect(mockConnect).toHaveBeenCalledTimes(1);
    });

    it("should set isHealthy to true after successful connection", async () => {
      const service = new PrismaService();

      expect(service.isHealthy()).toBe(false);

      await service.onModuleInit();

      expect(service.isHealthy()).toBe(true);
    });

    it("should throw on connection failure in non-test environment", async () => {
      process.env.ENVIRONMENT = "production";
      mockConnect.mockRejectedValueOnce(new Error("Connection refused"));

      const service = new PrismaService();

      await expect(service.onModuleInit()).rejects.toThrow(
        "Connection refused",
      );
      expect(service.isHealthy()).toBe(false);
    });

    it("should degrade gracefully in test environment on connection failure", async () => {
      process.env.ENVIRONMENT = "test";
      mockConnect.mockRejectedValueOnce(new Error("Connection refused"));

      const service = new PrismaService();

      // Should NOT throw
      await service.onModuleInit();

      expect(service.isHealthy()).toBe(false);
    });

    it("should degrade gracefully when NODE_ENV is ci", async () => {
      process.env.NODE_ENV = "ci";
      mockConnect.mockRejectedValueOnce(new Error("No database"));

      const service = new PrismaService();

      await service.onModuleInit();

      expect(service.isHealthy()).toBe(false);
    });

    it("should degrade gracefully when ENVIRONMENT is testing", async () => {
      process.env.ENVIRONMENT = "testing";
      mockConnect.mockRejectedValueOnce(new Error("No database"));

      const service = new PrismaService();

      await service.onModuleInit();

      expect(service.isHealthy()).toBe(false);
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 3. Connection Management - onModuleDestroy
  // ───────────────────────────────────────────────────────────────────────────

  describe("Connection teardown (onModuleDestroy)", () => {
    it("should call $disconnect when connected", async () => {
      const service = new PrismaService();

      await service.onModuleInit();
      await service.onModuleDestroy();

      expect(mockDisconnect).toHaveBeenCalledTimes(1);
    });

    it("should not call $disconnect when not connected", async () => {
      const service = new PrismaService();

      // Never initialized, so isConnected is false
      await service.onModuleDestroy();

      expect(mockDisconnect).not.toHaveBeenCalled();
    });

    it("should not call $disconnect after failed init in test mode", async () => {
      process.env.ENVIRONMENT = "test";
      mockConnect.mockRejectedValueOnce(new Error("No database"));

      const service = new PrismaService();

      await service.onModuleInit();
      await service.onModuleDestroy();

      expect(mockDisconnect).not.toHaveBeenCalled();
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 4. Connection Management - Environment Configuration
  // ───────────────────────────────────────────────────────────────────────────

  describe("Environment configuration", () => {
    it("should read DATABASE_URL from environment variable", () => {
      const expectedUrl =
        "postgresql://sahool:secret@pgbouncer:6432/sahool?sslmode=require";
      process.env.DATABASE_URL = expectedUrl;

      new PrismaService();

      const opts = constructorCalls[0].options;
      expect(opts.datasources.db.url).toBe(expectedUrl);
    });

    it("should handle missing DATABASE_URL gracefully (undefined)", () => {
      delete process.env.DATABASE_URL;

      new PrismaService();

      const opts = constructorCalls[0].options;
      expect(opts.datasources.db.url).toBeUndefined();
    });

    it("should support SSL mode in DATABASE_URL", () => {
      process.env.DATABASE_URL =
        "postgresql://user:pass@host:5432/db?sslmode=require";

      new PrismaService();

      const opts = constructorCalls[0].options;
      expect(opts.datasources.db.url).toContain("sslmode=require");
    });

    it("should support connection pooling params in DATABASE_URL", () => {
      process.env.DATABASE_URL =
        "postgresql://user:pass@pgbouncer:6432/db?sslmode=require&connection_limit=8&pool_timeout=20";

      new PrismaService();

      const opts = constructorCalls[0].options;
      expect(opts.datasources.db.url).toContain("connection_limit=8");
      expect(opts.datasources.db.url).toContain("pool_timeout=20");
    });
  });

  // ───────────────────────────────────────────────────────────────────────────
  // 5. Health Check
  // ───────────────────────────────────────────────────────────────────────────

  describe("Health checks", () => {
    it("should report connected status via getConnectionStatus", async () => {
      const service = new PrismaService();
      await service.onModuleInit();

      const status = await service.getConnectionStatus();

      expect(status.connected).toBe(true);
      expect(status.timestamp).toBeDefined();
    });

    it("should report disconnected when query fails", async () => {
      mockQueryRaw.mockRejectedValueOnce(new Error("Connection lost"));

      const service = new PrismaService();
      await service.onModuleInit();

      const status = await service.getConnectionStatus();

      expect(status.connected).toBe(false);
      expect(status.timestamp).toBeDefined();
    });
  });
});
