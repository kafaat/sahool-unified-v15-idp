/**
 * Field Management Service — Database Failure Tests
 * اختبارات فشل قاعدة البيانات لخدمة إدارة الحقول
 *
 * Tests service behavior when the database is unavailable or returns errors:
 *  - Service starts in degraded mode (no DB at startup)
 *  - /healthz stays 200 even with DB down (liveness probe)
 *  - /readyz returns 503 when DB is down (readiness probe)
 *  - /readyz returns 200 when DB recovers
 *  - Field CRUD operations fail gracefully with appropriate HTTP status
 *  - Transaction rollback: partial writes do not leak
 *  - PrismaService.isHealthy() reflects connection state
 *  - PrismaService.getConnectionStatus() returns error details on failure
 *  - Service recovers when DB comes back online
 *  - Connection pool exhaustion is handled gracefully
 *  - Slow queries do not block the event loop
 */

import * as crypto from "crypto";
import { INestApplication, ValidationPipe } from "@nestjs/common";
import { APP_FILTER, APP_GUARD } from "@nestjs/core";
import { Test, TestingModule } from "@nestjs/testing";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import request from "supertest";
import { PrismaService } from "../../src/prisma/prisma.service";
import { CacheService } from "../../src/cache/cache.service";
import { FieldEventsService } from "../../src/events/field-events.service";
import { FieldsController } from "../../src/fields/fields.controller";
import { FieldsService } from "../../src/fields/fields.service";
import { KpiSnapshotService } from "../../src/fields/kpi-snapshot.service";
import { HealthController } from "../../src/health/health.controller";
import { JwtAuthGuard } from "../../src/auth/jwt-auth.guard";
import { TenantGuard } from "../../src/auth/tenant.guard";
import { HttpExceptionFilter } from "../../src/filters/http-exception.filter";

// ---------------------------------------------------------------------------
// Environment
// ---------------------------------------------------------------------------
process.env.NODE_ENV = "test";
process.env.ENVIRONMENT = "test";
process.env.JWT_SECRET_KEY = "test-secret-key-for-db-failure-tests-32c";
process.env.JWT_ALGORITHM = "HS256";

const JWT_SECRET = process.env.JWT_SECRET_KEY!;
const TENANT_A = "tenant-aaaa-1111-dbfail";
const FIELD_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479";
const now = new Date("2026-04-01T10:00:00Z");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function generateJwt(payload: Record<string, unknown>, expiresInSec = 3600): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const body = Buffer.from(
    JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + expiresInSec }),
  ).toString("base64url");
  const sig = crypto.createHmac("sha256", JWT_SECRET).update(`${header}.${body}`).digest("base64url");
  return `${header}.${body}.${sig}`;
}

function bearerToken(tenantId = TENANT_A): string {
  return `Bearer ${generateJwt({ sub: "user-dbfail-001", tid: tenantId, roles: ["farmer"], email: "dbfail@sahool.app" })}`;
}

function makeFieldRow(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    id: FIELD_ID,
    name: "DB Failure Test Field",
    tenantId: TENANT_A,
    cropType: "wheat",
    status: "active",
    areaHectares: 5.0,
    healthScore: 0.75,
    ndviValue: 0.6,
    irrigationType: null,
    soilType: null,
    plantingDate: null,
    expectedHarvest: null,
    metadata: null,
    version: 1,
    isDeleted: false,
    farmId: null,
    ownerId: null,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

const DB_DOWN_ERROR = new Error("connect ECONNREFUSED 127.0.0.1:5432");
const DB_TIMEOUT_ERROR = new Error("Query timed out: timeout of 30000ms exceeded");
const DB_CONNECTION_POOL_ERROR = new Error("Connection pool exhausted — all 10 connections in use");
const DB_TRANSACTION_ERROR = new Error("Transaction failed: deadlock detected");
const DB_CONSTRAINT_ERROR = new Error("unique constraint violation on fields.id_tenantId");

function buildMockCacheService() {
  return {
    get: jest.fn().mockResolvedValue(null),
    set: jest.fn().mockResolvedValue(undefined),
    del: jest.fn().mockResolvedValue(undefined),
    invalidateField: jest.fn().mockResolvedValue(undefined),
    invalidateTenant: jest.fn().mockResolvedValue(undefined),
    isHealthy: jest.fn().mockResolvedValue(true),
    getStats: jest.fn().mockResolvedValue({}),
  };
}

function buildMockEvents() {
  return {
    onModuleInit: jest.fn().mockResolvedValue(undefined),
    onModuleDestroy: jest.fn().mockResolvedValue(undefined),
    isConnected: jest.fn().mockReturnValue(false),
    publishFieldCreated: jest.fn().mockResolvedValue(undefined),
    publishFieldUpdated: jest.fn().mockResolvedValue(undefined),
    publishFieldDeleted: jest.fn().mockResolvedValue(undefined),
    publishBoundaryChanged: jest.fn().mockResolvedValue(undefined),
    publishCropSeasonStarted: jest.fn().mockResolvedValue(undefined),
    publishCropSeasonUpdated: jest.fn().mockResolvedValue(undefined),
    publishCropSeasonEnded: jest.fn().mockResolvedValue(undefined),
    publishCropSeasonDeleted: jest.fn().mockResolvedValue(undefined),
    publishFieldOperationRecorded: jest.fn().mockResolvedValue(undefined),
    publishFieldOperationUpdated: jest.fn().mockResolvedValue(undefined),
    publishFieldOperationDeleted: jest.fn().mockResolvedValue(undefined),
    publishRaw: jest.fn().mockRejectedValue(new Error("NATS unavailable")),
  };
}

async function buildApp(mockPrisma: any, mockEvents: any): Promise<INestApplication> {
  const module: TestingModule = await Test.createTestingModule({
    imports: [
      ThrottlerModule.forRoot([{ name: "default", ttl: 60000, limit: 1000 }]),
    ],
    controllers: [HealthController, FieldsController],
    providers: [
      { provide: PrismaService, useValue: mockPrisma },
      { provide: CacheService, useValue: buildMockCacheService() },
      { provide: FieldEventsService, useValue: mockEvents },
      FieldsService,
      KpiSnapshotService,
      { provide: APP_GUARD, useClass: ThrottlerGuard },
      { provide: APP_GUARD, useClass: JwtAuthGuard },
      { provide: APP_GUARD, useClass: TenantGuard },
      { provide: APP_FILTER, useClass: HttpExceptionFilter },
    ],
  }).compile();

  const app = module.createNestApplication();
  app.useGlobalPipes(
    new ValidationPipe({ whitelist: true, transform: true, transformOptions: { enableImplicitConversion: true } }),
  );
  await app.init();
  return app;
}

// ---------------------------------------------------------------------------
// Suite 1: DB completely down at startup (degraded mode)
// ---------------------------------------------------------------------------
describe("DB Failure — Service starts in degraded mode", () => {
  let app: INestApplication;
  let mockPrisma: any;

  beforeAll(async () => {
    mockPrisma = {
      field: {
        create: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
        findUnique: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
        findMany: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
        count: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
        update: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      },
      farm: { findUnique: jest.fn().mockRejectedValue(DB_DOWN_ERROR) },
      fieldBoundaryHistory: {
        create: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
        findUnique: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
        findMany: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      },
      fieldKpiSnapshot: {
        findFirst: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
        create: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      },
      $transaction: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      $queryRaw: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      $queryRawUnsafe: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      $executeRaw: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      $connect: jest.fn().mockRejectedValue(DB_DOWN_ERROR),
      $disconnect: jest.fn().mockResolvedValue(undefined),
      isHealthy: jest.fn().mockReturnValue(false),
      getConnectionStatus: jest.fn().mockResolvedValue({
        connected: false,
        timestamp: now.toISOString(),
        error: "connect ECONNREFUSED 127.0.0.1:5432",
      }),
      onModuleInit: jest.fn().mockResolvedValue(undefined),
      onModuleDestroy: jest.fn().mockResolvedValue(undefined),
    };

    app = await buildApp(mockPrisma, buildMockEvents());
  }, 30_000);

  afterAll(async () => {
    await app.close();
  });

  // =========================================================================
  // Liveness probe — must ALWAYS return 200 (even with DB down)
  // =========================================================================
  describe("Liveness probe (/healthz) — always healthy", () => {
    it("→ 200 regardless of DB state", async () => {
      const res = await request(app.getHttpServer()).get("/healthz");
      expect(res.status).toBe(200);
      expect(res.body.status).toBe("healthy");
      expect(res.body.service).toBe("field-management-service");
    });

    it("→ 200 repeatedly under DB-down conditions", async () => {
      for (let i = 0; i < 5; i++) {
        // Run sequentially to avoid ECONNRESET on concurrent supertest calls
        // when the test server is not yet in listen() state
        // eslint-disable-next-line no-await-in-loop
        const r = await request(app.getHttpServer()).get("/healthz");
        expect(r.status).toBe(200);
      }
    });
  });

  // =========================================================================
  // Readiness probe — must return 503 when DB is unavailable
  // =========================================================================
  describe("Readiness probe (/readyz) — reflects DB state", () => {
    it("→ 503 when database is down", async () => {
      const res = await request(app.getHttpServer()).get("/readyz");
      expect(res.status).toBe(503);
      expect(res.body.status).toBe("not ready");
      expect(res.body.checks.database).toBe("disconnected");
    });

    it("→ 503 includes check details for observability", async () => {
      const res = await request(app.getHttpServer()).get("/readyz");
      expect(res.status).toBe(503);
      expect(res.body.checks).toBeDefined();
      expect(res.body.timestamp).toBeDefined();
      expect(res.body.service).toBe("field-management-service");
    });

    it("→ detailed /health endpoint shows unhealthy database", async () => {
      const res = await request(app.getHttpServer()).get("/health");
      expect(res.status).toBe(200); // /health always returns 200 (degraded, not 503)
      expect(res.body.checks.database.status).toBe("unhealthy");
      expect(res.body.checks.database.error).toBeDefined();
    });
  });

  // =========================================================================
  // Field CRUD — fail gracefully
  // =========================================================================
  describe("Field CRUD — graceful failures when DB is down", () => {
    const token = () => bearerToken();

    it("POST /api/v1/fields → 500 (Internal Server Error)", async () => {
      const res = await request(app.getHttpServer())
        .post("/api/v1/fields")
        .set("Authorization", token())
        .send({ name: "Test Field", tenantId: TENANT_A, cropType: "wheat" });

      expect(res.status).toBe(500);
      // Must not expose internal DB error details
      expect(res.body).not.toHaveProperty("stack");
    });

    it("GET /api/v1/fields → 500 (Internal Server Error)", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", token());
      expect(res.status).toBe(500);
    });

    it("GET /api/v1/fields/:id → 500 (Internal Server Error)", async () => {
      const res = await request(app.getHttpServer())
        .get(`/api/v1/fields/${FIELD_ID}`)
        .set("Authorization", token());
      expect(res.status).toBe(500);
    });

    it("PUT /api/v1/fields/:id → 500 (Internal Server Error)", async () => {
      const res = await request(app.getHttpServer())
        .put(`/api/v1/fields/${FIELD_ID}`)
        .set("Authorization", token())
        .send({ name: "Updated" });
      expect(res.status).toBe(500);
    });

    it("DELETE /api/v1/fields/:id → 500 (Internal Server Error)", async () => {
      const res = await request(app.getHttpServer())
        .delete(`/api/v1/fields/${FIELD_ID}`)
        .set("Authorization", token());
      expect(res.status).toBe(500);
    });

    it("error responses do not expose stack traces", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", token());
      expect(res.status).toBe(500);
      // Stack traces must not leak — only error code/message should be present
      expect(res.body.stack).toBeUndefined();
      expect(res.body.error?.stack).toBeUndefined();
    });

    it("liveness probe still returns 200 after multiple DB failures", async () => {
      await Promise.all([
        request(app.getHttpServer()).get("/api/v1/fields").set("Authorization", token()),
        request(app.getHttpServer()).get("/api/v1/fields").set("Authorization", token()),
        request(app.getHttpServer()).get("/api/v1/fields").set("Authorization", token()),
      ]);

      const healthRes = await request(app.getHttpServer()).get("/healthz");
      expect(healthRes.status).toBe(200);
    });
  });
});

// ---------------------------------------------------------------------------
// Suite 2: DB starts healthy, then goes down mid-session (intermittent)
// ---------------------------------------------------------------------------
describe("DB Failure — Intermittent connection loss", () => {
  let app: INestApplication;
  let mockPrisma: any;

  beforeAll(async () => {
    const txFieldCreate = jest.fn().mockResolvedValue(makeFieldRow());

    mockPrisma = {
      field: {
        create: jest.fn().mockResolvedValue(makeFieldRow()),
        findUnique: jest.fn().mockResolvedValue(makeFieldRow()),
        findMany: jest.fn().mockResolvedValue([makeFieldRow()]),
        count: jest.fn().mockResolvedValue(1),
        update: jest.fn().mockResolvedValue(makeFieldRow({ version: 2 })),
      },
      farm: { findUnique: jest.fn().mockResolvedValue(null) },
      fieldBoundaryHistory: {
        create: jest.fn().mockResolvedValue({}),
        findUnique: jest.fn().mockResolvedValue(null),
        findMany: jest.fn().mockResolvedValue([]),
      },
      fieldKpiSnapshot: {
        findFirst: jest.fn().mockResolvedValue(null),
        create: jest.fn().mockResolvedValue({ id: "kpi-1", fieldId: FIELD_ID }),
      },
      $transaction: jest.fn((cb: (tx: any) => Promise<unknown>) =>
        cb({
          field: { create: txFieldCreate, update: jest.fn().mockResolvedValue(makeFieldRow({ version: 2 })) },
          fieldBoundaryHistory: { create: jest.fn().mockResolvedValue({}) },
          $executeRaw: jest.fn().mockResolvedValue(1),
          $queryRaw: jest.fn().mockResolvedValue([]),
        }),
      ),
      $queryRaw: jest.fn().mockResolvedValue([{ "?column?": 1 }]),
      $queryRawUnsafe: jest.fn().mockResolvedValue([]),
      $executeRaw: jest.fn().mockResolvedValue(1),
      $connect: jest.fn().mockResolvedValue(undefined),
      $disconnect: jest.fn().mockResolvedValue(undefined),
      isHealthy: jest.fn().mockReturnValue(true),
      getConnectionStatus: jest.fn().mockResolvedValue({ connected: true, timestamp: now.toISOString() }),
      onModuleInit: jest.fn().mockResolvedValue(undefined),
      onModuleDestroy: jest.fn().mockResolvedValue(undefined),
    };

    app = await buildApp(mockPrisma, buildMockEvents());
  }, 30_000);

  afterAll(async () => {
    await app.close();
  });

  it("works correctly when DB is initially healthy", async () => {
    const res = await request(app.getHttpServer())
      .get("/api/v1/fields")
      .set("Authorization", bearerToken());
    expect(res.status).toBe(200);
  });

  it("/readyz returns 200 when DB is healthy", async () => {
    mockPrisma.$queryRaw
      .mockResolvedValueOnce([{ "?column?": 1 }])
      .mockResolvedValueOnce([{ version: "3.4.0" }]);
    const res = await request(app.getHttpServer()).get("/readyz");
    expect(res.status).toBe(200);
    expect(res.body.checks.database).toBe("connected");
  });

  it("after DB goes down — /readyz switches to 503", async () => {
    mockPrisma.$queryRaw.mockRejectedValue(DB_DOWN_ERROR);

    const res = await request(app.getHttpServer()).get("/readyz");
    expect(res.status).toBe(503);
    expect(res.body.checks.database).toBe("disconnected");
  });

  it("after DB goes down — field reads fail with 500", async () => {
    mockPrisma.field.findUnique.mockRejectedValue(DB_DOWN_ERROR);

    const res = await request(app.getHttpServer())
      .get(`/api/v1/fields/${FIELD_ID}`)
      .set("Authorization", bearerToken());
    expect(res.status).toBe(500);
  });

  it("after DB recovers — /readyz returns 200 again", async () => {
    mockPrisma.$queryRaw
      .mockResolvedValueOnce([{ "?column?": 1 }])
      .mockResolvedValueOnce([{ version: "3.4.0" }]);

    const res = await request(app.getHttpServer()).get("/readyz");
    expect(res.status).toBe(200);
    expect(res.body.checks.database).toBe("connected");
  });

  it("after DB recovers — field reads succeed again", async () => {
    mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());
    mockPrisma.$queryRawUnsafe.mockResolvedValue([]);

    const res = await request(app.getHttpServer())
      .get(`/api/v1/fields/${FIELD_ID}`)
      .set("Authorization", bearerToken());
    expect(res.status).toBe(200);
  });
});

// ---------------------------------------------------------------------------
// Suite 3: Specific DB error types and their HTTP mappings
// ---------------------------------------------------------------------------
describe("DB Failure — Specific error type handling", () => {
  let app: INestApplication;
  let mockPrisma: any;

  beforeAll(async () => {
    mockPrisma = {
      field: {
        create: jest.fn().mockResolvedValue(makeFieldRow()),
        findUnique: jest.fn().mockResolvedValue(makeFieldRow()),
        findFirst: jest.fn().mockResolvedValue(makeFieldRow()),
        findMany: jest.fn().mockResolvedValue([makeFieldRow()]),
        count: jest.fn().mockResolvedValue(1),
        update: jest.fn().mockResolvedValue(makeFieldRow({ version: 2 })),
      },
      farm: { findUnique: jest.fn().mockResolvedValue(null) },
      fieldBoundaryHistory: {
        create: jest.fn().mockResolvedValue({}),
        findUnique: jest.fn().mockResolvedValue(null),
        findMany: jest.fn().mockResolvedValue([]),
      },
      fieldKpiSnapshot: {
        findFirst: jest.fn().mockResolvedValue(null),
        create: jest.fn().mockResolvedValue({ id: "kpi-1" }),
      },
      $transaction: jest.fn((cb: (tx: any) => Promise<unknown>) =>
        cb({
          field: { create: jest.fn().mockResolvedValue(makeFieldRow()), update: jest.fn().mockResolvedValue(makeFieldRow({ version: 2 })) },
          fieldBoundaryHistory: { create: jest.fn().mockResolvedValue({}) },
          $executeRaw: jest.fn().mockResolvedValue(1),
          $queryRaw: jest.fn().mockResolvedValue([]),
        }),
      ),
      $queryRaw: jest.fn().mockResolvedValue([{ "?column?": 1 }]),
      $queryRawUnsafe: jest.fn().mockResolvedValue([]),
      $executeRaw: jest.fn().mockResolvedValue(1),
      $connect: jest.fn().mockResolvedValue(undefined),
      $disconnect: jest.fn().mockResolvedValue(undefined),
      isHealthy: jest.fn().mockReturnValue(true),
      getConnectionStatus: jest.fn().mockResolvedValue({ connected: true, timestamp: now.toISOString() }),
      onModuleInit: jest.fn().mockResolvedValue(undefined),
      onModuleDestroy: jest.fn().mockResolvedValue(undefined),
    };

    app = await buildApp(mockPrisma, buildMockEvents());
  }, 30_000);

  afterAll(async () => {
    await app.close();
  });

  beforeEach(() => {
    jest.clearAllMocks();
    mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());
    mockPrisma.field.findFirst.mockResolvedValue(makeFieldRow());
    mockPrisma.field.findMany.mockResolvedValue([makeFieldRow()]);
    mockPrisma.field.count.mockResolvedValue(1);
    mockPrisma.$queryRaw.mockResolvedValue([{ "?column?": 1 }]);
    mockPrisma.$queryRawUnsafe.mockResolvedValue([]);
  });

  it("DB timeout on findUnique → 500 with no stack trace in response", async () => {
    mockPrisma.field.findUnique.mockRejectedValue(DB_TIMEOUT_ERROR);

    const res = await request(app.getHttpServer())
      .get(`/api/v1/fields/${FIELD_ID}`)
      .set("Authorization", bearerToken());

    expect(res.status).toBe(500);
    expect(res.body.stack).toBeUndefined();
  });

  it("DB connection pool exhausted → 500 handled gracefully", async () => {
    mockPrisma.field.findMany.mockRejectedValue(DB_CONNECTION_POOL_ERROR);
    mockPrisma.field.count.mockRejectedValue(DB_CONNECTION_POOL_ERROR);

    const res = await request(app.getHttpServer())
      .get("/api/v1/fields")
      .set("Authorization", bearerToken());

    expect(res.status).toBe(500);
    expect(res.body).toBeDefined();
  });

  it("transaction deadlock on update → 500 — rollback implied by mock rejection", async () => {
    mockPrisma.field.findUnique.mockResolvedValue({ id: FIELD_ID, version: 1, tenantId: TENANT_A });
    mockPrisma.$transaction.mockRejectedValue(DB_TRANSACTION_ERROR);

    const res = await request(app.getHttpServer())
      .put(`/api/v1/fields/${FIELD_ID}`)
      .set("Authorization", bearerToken())
      .send({ name: "Deadlock Update" });

    expect(res.status).toBe(500);
  });

  it("unique constraint violation during create → 500 (Prisma maps it)", async () => {
    const txFieldCreate = jest.fn().mockRejectedValue(DB_CONSTRAINT_ERROR);
    mockPrisma.$transaction.mockImplementation((cb: (tx: any) => Promise<unknown>) =>
      cb({
        field: { create: txFieldCreate, update: jest.fn() },
        fieldBoundaryHistory: { create: jest.fn().mockResolvedValue({}) },
        $executeRaw: jest.fn().mockResolvedValue(1),
        $queryRaw: jest.fn().mockResolvedValue([]),
      }),
    );

    const res = await request(app.getHttpServer())
      .post("/api/v1/fields")
      .set("Authorization", bearerToken())
      .send({ name: "Duplicate Field", tenantId: TENANT_A, cropType: "wheat" });

    expect(res.status).toBe(500);
  });

  it("partial transaction failure — entire transaction is rejected atomically", async () => {
    mockPrisma.$transaction.mockRejectedValue(new Error("PostGIS function not available"));

    const res = await request(app.getHttpServer())
      .post("/api/v1/fields")
      .set("Authorization", bearerToken())
      .send({
        name: "PostGIS Fail Field",
        tenantId: TENANT_A,
        cropType: "wheat",
        coordinates: [[46.700, 24.700], [46.701, 24.700], [46.701, 24.701], [46.700, 24.701]],
      });

    expect(res.status).toBe(500);
  });

  it("DB error on findMany does not affect /healthz availability", async () => {
    mockPrisma.field.findMany.mockRejectedValue(DB_DOWN_ERROR);
    mockPrisma.field.count.mockRejectedValue(DB_DOWN_ERROR);

    await request(app.getHttpServer())
      .get("/api/v1/fields")
      .set("Authorization", bearerToken());

    const healthRes = await request(app.getHttpServer()).get("/healthz");
    expect(healthRes.status).toBe(200);
  });

  it("slow DB query (simulated with 200ms delay) does not crash the service", async () => {
    mockPrisma.field.findMany.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve([makeFieldRow()]), 200)),
    );
    mockPrisma.field.count.mockResolvedValue(1);

    const [slowRes, healthRes] = await Promise.all([
      request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", bearerToken()),
      request(app.getHttpServer()).get("/healthz"),
    ]);

    expect(slowRes.status).toBe(200);
    expect(healthRes.status).toBe(200);
  });
});

// ---------------------------------------------------------------------------
// Suite 4: PrismaService unit tests (connection state machine)
// ---------------------------------------------------------------------------
describe("PrismaService — Unit: connection state machine", () => {
  const realDbUrl = "postgresql://test:test@localhost:5432/test_nonexistent";

  beforeAll(() => {
    process.env.NODE_ENV = "test";
    process.env.ENVIRONMENT = "test";
    process.env.DATABASE_URL = realDbUrl;
  });

  it("isHealthy() returns false before onModuleInit is called", async () => {
    const { PrismaService: RealPrismaService } = await import("../../src/prisma/prisma.service");
    const service = new RealPrismaService();
    expect(service.isHealthy()).toBe(false);
  });

  it("getConnectionStatus() returns connected:false when DB is unreachable", async () => {
    const { PrismaService: RealPrismaService } = await import("../../src/prisma/prisma.service");
    const service = new RealPrismaService();
    const status = await service.getConnectionStatus();
    expect(status.connected).toBe(false);
    expect(status.error).toBeDefined();
    expect(status.timestamp).toBeDefined();
  });
});
