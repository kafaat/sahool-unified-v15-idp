/**
 * Field Management Service — End-to-End Tests
 * اختبارات شاملة من طرف إلى طرف لخدمة إدارة الحقول
 *
 * Tests the real HTTP request/response cycle using a minimal NestJS
 * TestingModule (no AppModule) with mocked infrastructure (Prisma, NATS
 * events, Cache) but real routing, guards, validation pipes, and exception
 * filters.
 *
 * Coverage:
 *  - Health endpoints (liveness / readiness / metrics)
 *  - JWT authentication guard (missing token, invalid signature, expired)
 *  - Tenant isolation guard (header mismatch, cross-tenant access)
 *  - Full field CRUD lifecycle
 *  - Optimistic locking (ETag / If-Match / ifMatch version body field)
 *  - Boundary history + rollback
 *  - Nearby fields
 *  - Stats endpoint
 *  - KPI snapshots
 *  - Pagination
 *  - Input validation (400 errors)
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
// Environment setup — must run BEFORE AppModule loads
// ---------------------------------------------------------------------------
process.env.NODE_ENV = "test";
process.env.ENVIRONMENT = "test";
process.env.JWT_SECRET_KEY = "test-secret-key-for-e2e-tests-only-32c";
process.env.JWT_ALGORITHM = "HS256";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const JWT_SECRET = process.env.JWT_SECRET_KEY!;
const TENANT_A = "tenant-aaaa-1111-e2e0";
const TENANT_B = "tenant-bbbb-2222-e2e0";
const FIELD_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479";
const FARM_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890";
const HISTORY_ID = "c3d4e5f6-a7b8-4012-8cde-123456789012";
const now = new Date("2026-04-01T10:00:00Z");

// ---------------------------------------------------------------------------
// JWT helpers
// ---------------------------------------------------------------------------
function generateJwt(payload: Record<string, unknown>, expiresInSec = 3600): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const body = Buffer.from(
    JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + expiresInSec }),
  ).toString("base64url");
  const sig = crypto.createHmac("sha256", JWT_SECRET).update(`${header}.${body}`).digest("base64url");
  return `${header}.${body}.${sig}`;
}

function bearerToken(tenantId: string, roles: string[] = ["farmer"], userId = "user-001"): string {
  return `Bearer ${generateJwt({ sub: userId, tid: tenantId, roles, email: "test@sahool.app" })}`;
}

// ---------------------------------------------------------------------------
// Mock field row factory
// ---------------------------------------------------------------------------
function makeFieldRow(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    id: FIELD_ID,
    name: "North Wheat Field",
    tenantId: TENANT_A,
    cropType: "wheat",
    status: "active",
    areaHectares: 12.5,
    healthScore: 0.72,
    ndviValue: 0.65,
    irrigationType: "drip",
    soilType: "loamy",
    plantingDate: now,
    expectedHarvest: new Date("2026-07-15T00:00:00Z"),
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

// ---------------------------------------------------------------------------
// Mock Prisma builder
// ---------------------------------------------------------------------------
function buildMockPrisma() {
  const innerExecuteRaw = jest.fn().mockResolvedValue(1);
  const txFieldCreate = jest.fn().mockResolvedValue(makeFieldRow());
  const txFieldUpdate = jest.fn().mockResolvedValue(makeFieldRow({ version: 2 }));

  const mock = {
    field: {
      create: jest.fn().mockResolvedValue(makeFieldRow()),
      findUnique: jest.fn().mockResolvedValue(makeFieldRow()),
      findFirst: jest.fn().mockResolvedValue(makeFieldRow()),
      findMany: jest.fn().mockResolvedValue([makeFieldRow()]),
      count: jest.fn().mockResolvedValue(1),
      update: jest.fn().mockResolvedValue(makeFieldRow({ version: 2 })),
    },
    farm: {
      findUnique: jest.fn().mockResolvedValue({ id: FARM_ID, tenantId: TENANT_A }),
    },
    fieldBoundaryHistory: {
      create: jest.fn().mockResolvedValue({ id: HISTORY_ID }),
      findUnique: jest.fn().mockResolvedValue({
        id: HISTORY_ID,
        fieldId: FIELD_ID,
        coordinates: JSON.stringify([[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8]]),
        changedAt: now,
        userId: null,
        reason: "test",
      }),
      findMany: jest.fn().mockResolvedValue([
        { id: HISTORY_ID, fieldId: FIELD_ID, changedAt: now, reason: "initial", userId: null },
      ]),
    },
    fieldKpiSnapshot: {
      findFirst: jest.fn().mockResolvedValue(null),
      create: jest.fn().mockResolvedValue({
        id: "kpi-001",
        fieldId: FIELD_ID,
        tenantId: TENANT_A,
        ndvi: 0.72,
        temperature: 28,
        createdAt: now,
      }),
    },
    $transaction: jest.fn((cb: (tx: any) => Promise<unknown>) =>
      cb({
        field: {
          create: txFieldCreate,
          update: txFieldUpdate,
        },
        fieldBoundaryHistory: {
          create: jest.fn().mockResolvedValue({}),
        },
        $executeRaw: innerExecuteRaw,
        $queryRaw: jest.fn().mockResolvedValue([{ boundary: null }]),
      }),
    ),
    $queryRaw: jest.fn().mockResolvedValue([{ "?column?": 1 }]),
    $queryRawUnsafe: jest.fn().mockResolvedValue([]),
    $executeRaw: jest.fn().mockResolvedValue(1),
    $connect: jest.fn().mockResolvedValue(undefined),
    $disconnect: jest.fn().mockResolvedValue(undefined),
    // Expose internals for assertions
    __txFieldCreate: txFieldCreate,
    __txFieldUpdate: txFieldUpdate,
    __innerExecuteRaw: innerExecuteRaw,
  };

  return mock;
}

// ---------------------------------------------------------------------------
// Mock events builder
// ---------------------------------------------------------------------------
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
    publishRaw: jest.fn().mockResolvedValue(undefined),
  };
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------
describe("Field Management Service — E2E", () => {
  let app: INestApplication;
  let mockPrisma: ReturnType<typeof buildMockPrisma>;
  let mockEvents: ReturnType<typeof buildMockEvents>;

  beforeAll(async () => {
    mockPrisma = buildMockPrisma();
    mockEvents = buildMockEvents();

    const mockCacheService = {
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue(undefined),
      del: jest.fn().mockResolvedValue(undefined),
      invalidateField: jest.fn().mockResolvedValue(undefined),
      invalidateTenant: jest.fn().mockResolvedValue(undefined),
      isHealthy: jest.fn().mockResolvedValue(true),
      getStats: jest.fn().mockResolvedValue({}),
    };

    const module: TestingModule = await Test.createTestingModule({
      imports: [
        ThrottlerModule.forRoot([{ name: "default", ttl: 60000, limit: 1000 }]),
      ],
      controllers: [HealthController, FieldsController],
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
        { provide: CacheService, useValue: mockCacheService },
        { provide: FieldEventsService, useValue: mockEvents },
        FieldsService,
        KpiSnapshotService,
        { provide: APP_GUARD, useClass: ThrottlerGuard },
        { provide: APP_GUARD, useClass: JwtAuthGuard },
        { provide: APP_GUARD, useClass: TenantGuard },
        { provide: APP_FILTER, useClass: HttpExceptionFilter },
      ],
    }).compile();

    app = module.createNestApplication();
    app.useGlobalPipes(
      new ValidationPipe({ whitelist: true, transform: true, transformOptions: { enableImplicitConversion: true } }),
    );
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(() => {
    jest.clearAllMocks();
    // Restore default mocks after each test
    mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());
    mockPrisma.field.findFirst.mockResolvedValue(makeFieldRow());
    mockPrisma.field.findMany.mockResolvedValue([makeFieldRow()]);
    mockPrisma.field.count.mockResolvedValue(1);
    mockPrisma.$queryRaw.mockResolvedValue([{ "?column?": 1 }]);
    mockPrisma.$queryRawUnsafe.mockResolvedValue([]);
  });

  // =========================================================================
  // Health endpoints — public routes, no auth required
  // =========================================================================
  describe("Health Endpoints", () => {
    it("GET /healthz → 200 with service info", async () => {
      const res = await request(app.getHttpServer()).get("/healthz");
      expect(res.status).toBe(200);
      expect(res.body.status).toBe("healthy");
      expect(res.body.service).toBe("field-management-service");
      expect(res.body.version).toBe("16.0.0");
      expect(res.body.timestamp).toBeDefined();
    });

    it("GET /readyz → 200 when database and PostGIS are available", async () => {
      mockPrisma.$queryRaw
        .mockResolvedValueOnce([{ "?column?": 1 }]) // SELECT 1
        .mockResolvedValueOnce([{ version: "3.4.0 r17264" }]); // PostGIS_Version()
      const res = await request(app.getHttpServer()).get("/readyz");
      expect(res.status).toBe(200);
      expect(res.body.status).toBe("ready");
      expect(res.body.checks.database).toBe("connected");
    });

    it("GET /readyz → 503 when database is unavailable", async () => {
      mockPrisma.$queryRaw.mockRejectedValue(new Error("connection refused"));
      const res = await request(app.getHttpServer()).get("/readyz");
      expect(res.status).toBe(503);
      expect(res.body.status).toBe("not ready");
      expect(res.body.checks.database).toBe("disconnected");
    });

    it("GET /health → 200 with detailed checks", async () => {
      mockPrisma.$queryRaw
        .mockResolvedValueOnce([{ "?column?": 1 }]) // SELECT 1 for latency
        .mockResolvedValueOnce([{ version: "3.4.0" }]); // PostGIS
      const res = await request(app.getHttpServer()).get("/health");
      expect(res.status).toBe(200);
      expect(res.body.checks.database).toBeDefined();
      expect(res.body.checks.memory).toBeDefined();
      expect(res.body.checks.uptime).toBeDefined();
    });

    it("GET /metrics → 200 with Prometheus format", async () => {
      const res = await request(app.getHttpServer()).get("/metrics");
      expect(res.status).toBe(200);
      expect(res.headers["content-type"]).toMatch(/text\/plain/);
      expect(res.text).toContain("nodejs_heap_size_used_bytes");
      expect(res.text).toContain("service_info");
    });
  });

  // =========================================================================
  // Authentication Guard
  // =========================================================================
  describe("Authentication Guard", () => {
    it("→ 401 when Authorization header is missing", async () => {
      const res = await request(app.getHttpServer()).get("/api/v1/fields");
      expect(res.status).toBe(401);
    });

    it("→ 401 when token uses wrong signature", async () => {
      const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
      const payload = Buffer.from(JSON.stringify({ sub: "u1", tid: TENANT_A, exp: Math.floor(Date.now() / 1000) + 3600 })).toString("base64url");
      const badSig = crypto.createHmac("sha256", "wrong-secret").update(`${header}.${payload}`).digest("base64url");
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", `Bearer ${header}.${payload}.${badSig}`);
      expect(res.status).toBe(401);
    });

    it("→ 401 when token is expired", async () => {
      const token = generateJwt({ sub: "u1", tid: TENANT_A }, -1); // expired 1 second ago
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", `Bearer ${token}`);
      expect(res.status).toBe(401);
    });

    it("→ 401 with malformed JWT (2 parts only)", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", "Bearer part1.part2");
      expect(res.status).toBe(401);
    });
  });

  // =========================================================================
  // Tenant Guard
  // =========================================================================
  describe("Tenant Guard", () => {
    it("→ 200 when X-Tenant-ID matches JWT tenant", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", bearerToken(TENANT_A))
        .set("X-Tenant-ID", TENANT_A);
      expect(res.status).toBe(200);
    });

    it("→ 403 when X-Tenant-ID differs from JWT tenant (non-admin user)", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", bearerToken(TENANT_A))
        .set("X-Tenant-ID", TENANT_B);
      expect(res.status).toBe(403);
    });

    it("→ 200 when admin overrides tenant via X-Tenant-ID", async () => {
      mockPrisma.field.findMany.mockResolvedValue([makeFieldRow({ tenantId: TENANT_B })]);
      mockPrisma.field.count.mockResolvedValue(1);
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", bearerToken(TENANT_A, ["ADMIN"]))
        .set("X-Tenant-ID", TENANT_B);
      expect(res.status).toBe(200);
    });
  });

  // =========================================================================
  // Field CRUD Lifecycle
  // =========================================================================
  describe("Field CRUD", () => {
    describe("POST /api/v1/fields — Create field", () => {
      const createDto = {
        name: "North Wheat Field",
        tenantId: TENANT_A,
        cropType: "wheat",
        irrigationType: "drip",
        soilType: "loamy",
      };

      it("→ 201 with valid payload", async () => {
        mockPrisma.__txFieldCreate.mockResolvedValue(makeFieldRow());
        mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());

        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send(createDto);

        expect(res.status).toBe(201);
        expect(res.body.success).toBe(true);
        expect(res.body.data.id).toBe(FIELD_ID);
        expect(res.body.data.cropType).toBe("wheat");
        expect(res.body.etag).toContain(FIELD_ID);
        expect(res.body.message).toBeDefined();
      });

      it("→ 201 with coordinates (polygon boundary)", async () => {
        mockPrisma.__txFieldCreate.mockResolvedValue(makeFieldRow());
        mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());

        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({
            ...createDto,
            coordinates: [
              [46.700, 24.700],
              [46.701, 24.700],
              [46.701, 24.701],
              [46.700, 24.701],
            ],
          });

        expect(res.status).toBe(201);
        expect(res.body.success).toBe(true);
      });

      it("→ 400 when name is missing", async () => {
        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({ tenantId: TENANT_A, cropType: "wheat" });
        expect(res.status).toBe(400);
      });

      it("→ 400 when cropType is missing", async () => {
        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({ name: "Test Field", tenantId: TENANT_A });
        expect(res.status).toBe(400);
      });

      it("→ 400 when coordinates has < 3 points", async () => {
        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({ ...createDto, coordinates: [[46.7, 24.7], [46.8, 24.7]] });
        expect(res.status).toBe(400);
      });

      it("→ 400 when coordinates contain out-of-range longitude", async () => {
        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({
            ...createDto,
            coordinates: [
              [200, 24.7], // invalid longitude > 180
              [46.8, 24.7],
              [46.8, 24.8],
              [46.7, 24.8],
            ],
          });
        expect(res.status).toBe(400);
      });

      it("→ 400 when irrigationType is invalid enum value", async () => {
        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({ ...createDto, irrigationType: "laser" });
        expect(res.status).toBe(400);
      });

      it("→ 400 when soilType is invalid enum value", async () => {
        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({ ...createDto, soilType: "volcanic" });
        expect(res.status).toBe(400);
      });

      it("→ 400 for invalid GeoJSON boundary (ring not closed)", async () => {
        const res = await request(app.getHttpServer())
          .post("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A))
          .send({
            ...createDto,
            boundary: {
              type: "Polygon",
              coordinates: [[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8]]],
            },
          });
        expect(res.status).toBe(400);
      });
    });

    describe("GET /api/v1/fields — List fields", () => {
      it("→ 200 with paginated result", async () => {
        const res = await request(app.getHttpServer())
          .get("/api/v1/fields")
          .set("Authorization", bearerToken(TENANT_A));

        expect(res.status).toBe(200);
        expect(res.body.success).toBe(true);
        expect(Array.isArray(res.body.data)).toBe(true);
        expect(res.body.meta).toBeDefined();
        expect(res.body.meta.page).toBe(1);
        expect(res.body.meta.total).toBe(1);
      });

      it("→ 200 filtered by status", async () => {
        const res = await request(app.getHttpServer())
          .get("/api/v1/fields?status=active")
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(200);
      });

      it("→ 200 filtered by cropType", async () => {
        const res = await request(app.getHttpServer())
          .get("/api/v1/fields?cropType=wheat")
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(200);
      });

      it("→ 200 with custom pagination", async () => {
        mockPrisma.field.count.mockResolvedValue(50);
        mockPrisma.field.findMany.mockResolvedValue(
          Array(10).fill(null).map((_, i) => makeFieldRow({ id: `field-00${i}` })),
        );
        const res = await request(app.getHttpServer())
          .get("/api/v1/fields?page=2&limit=10")
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(200);
        expect(res.body.meta.page).toBe(2);
        expect(res.body.meta.limit).toBe(10);
        expect(res.body.meta.total).toBe(50);
        expect(res.body.meta.hasNext).toBe(true);
        expect(res.body.meta.hasPrev).toBe(true);
      });

      it("→ 400 for invalid status enum", async () => {
        const res = await request(app.getHttpServer())
          .get("/api/v1/fields?status=invalid_status")
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(400);
      });
    });

    describe("GET /api/v1/fields/:id — Get field by ID", () => {
      it("→ 200 with field data and ETag", async () => {
        const res = await request(app.getHttpServer())
          .get(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A));

        expect(res.status).toBe(200);
        expect(res.body.success).toBe(true);
        expect(res.body.data.id).toBe(FIELD_ID);
        expect(res.body.etag).toBeDefined();
      });

      it("→ 404 when field does not exist", async () => {
        mockPrisma.field.findUnique.mockResolvedValue(null);
        const nonExistentId = "00000000-0000-0000-0000-000000000000";
        const res = await request(app.getHttpServer())
          .get(`/api/v1/fields/${nonExistentId}`)
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(404);
      });

      it("→ 400 for non-UUID id", async () => {
        const res = await request(app.getHttpServer())
          .get("/api/v1/fields/not-a-uuid")
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(400);
      });
    });

    describe("PUT /api/v1/fields/:id — Update field", () => {
      it("→ 200 with updated field", async () => {
        mockPrisma.field.findUnique
          .mockResolvedValueOnce({ id: FIELD_ID, version: 1, tenantId: TENANT_A }) // update guard
          .mockResolvedValueOnce(makeFieldRow({ version: 2 })); // findById after update

        const res = await request(app.getHttpServer())
          .put(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A))
          .send({ name: "Updated Field Name", cropType: "barley" });

        expect(res.status).toBe(200);
        expect(res.body.success).toBe(true);
        expect(res.body.etag).toBeDefined();
      });

      it("→ 409 when If-Match header version is stale", async () => {
        mockPrisma.field.findUnique.mockResolvedValueOnce({
          id: FIELD_ID,
          version: 3, // server is at version 3
          tenantId: TENANT_A,
        });

        const res = await request(app.getHttpServer())
          .put(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A))
          .set("If-Match", `"${FIELD_ID}-v1"`) // client thinks version is 1
          .send({ name: "Stale Update" });

        expect(res.status).toBe(409);
        expect(res.body.success).toBe(false);
      });

      it("→ 409 when ifMatch body field version is stale", async () => {
        mockPrisma.field.findUnique.mockResolvedValueOnce({
          id: FIELD_ID,
          version: 5,
          tenantId: TENANT_A,
        });

        const res = await request(app.getHttpServer())
          .put(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A))
          .send({ name: "Stale", ifMatch: 2 });

        expect(res.status).toBe(409);
      });

      it("→ 200 when If-Match matches current version", async () => {
        mockPrisma.field.findUnique
          .mockResolvedValueOnce({ id: FIELD_ID, version: 1, tenantId: TENANT_A })
          .mockResolvedValueOnce(makeFieldRow({ version: 2 }));

        const res = await request(app.getHttpServer())
          .put(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A))
          .set("If-Match", `"${FIELD_ID}-v1"`)
          .send({ name: "Correct ETag Update" });

        expect(res.status).toBe(200);
      });

      it("→ 404 when field does not exist", async () => {
        mockPrisma.field.findUnique.mockResolvedValue(null);
        const res = await request(app.getHttpServer())
          .put(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A))
          .send({ name: "Phantom Field" });
        expect(res.status).toBe(404);
      });
    });

    describe("DELETE /api/v1/fields/:id — Delete field (soft delete)", () => {
      it("→ 200 when field exists", async () => {
        mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());
        mockPrisma.field.update.mockResolvedValue(makeFieldRow({ status: "inactive", isDeleted: true }));

        const res = await request(app.getHttpServer())
          .delete(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A));

        expect(res.status).toBe(200);
        expect(res.body.success).toBe(true);
        expect(res.body.message).toBeDefined();
      });

      it("→ 404 when field does not exist", async () => {
        mockPrisma.field.findUnique.mockResolvedValue(null);
        const res = await request(app.getHttpServer())
          .delete(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(404);
      });

      it("→ 403 when accessing another tenant's field", async () => {
        // Field belongs to TENANT_B but request comes from TENANT_A
        mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow({ tenantId: TENANT_B }));
        const res = await request(app.getHttpServer())
          .delete(`/api/v1/fields/${FIELD_ID}`)
          .set("Authorization", bearerToken(TENANT_A));
        expect(res.status).toBe(403);
      });
    });
  });

  // =========================================================================
  // Nearby Fields
  // =========================================================================
  describe("GET /api/v1/fields/nearby — Nearby fields", () => {
    it("→ 200 with nearby fields list", async () => {
      mockPrisma.$queryRawUnsafe.mockResolvedValue([makeFieldRow()]);

      const res = await request(app.getHttpServer())
        .get(`/api/v1/fields/nearby?lat=24.7&lng=46.7&radius=5000&tenantId=${TENANT_A}`)
        .set("Authorization", bearerToken(TENANT_A));

      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.query).toBeDefined();
      expect(res.body.query.lat).toBe(24.7);
      expect(res.body.query.lng).toBe(46.7);
    });

    it("→ 400 when lat is missing", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields/nearby?lng=46.7")
        .set("Authorization", bearerToken(TENANT_A));
      expect(res.status).toBe(400);
    });

    it("→ 400 when lng is missing", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields/nearby?lat=24.7")
        .set("Authorization", bearerToken(TENANT_A));
      expect(res.status).toBe(400);
    });

    it("→ 400 when radius < 100 meters", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields/nearby?lat=24.7&lng=46.7&radius=50")
        .set("Authorization", bearerToken(TENANT_A));
      expect(res.status).toBe(400);
    });

    it("→ 400 when radius > 100 km", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields/nearby?lat=24.7&lng=46.7&radius=150000")
        .set("Authorization", bearerToken(TENANT_A));
      expect(res.status).toBe(400);
    });

    it("→ 400 when lat is out of range", async () => {
      const res = await request(app.getHttpServer())
        .get("/api/v1/fields/nearby?lat=95&lng=46.7")
        .set("Authorization", bearerToken(TENANT_A));
      expect(res.status).toBe(400);
    });
  });

  // =========================================================================
  // Stats Endpoint
  // =========================================================================
  describe("GET /api/v1/fields/stats/:tenantId — Field statistics", () => {
    it("→ 200 with stats for the authenticated tenant", async () => {
      mockPrisma.$queryRaw.mockResolvedValue([
        { total: 5, active: 3, fallow: 1, harvested: 1 },
      ]);

      const res = await request(app.getHttpServer())
        .get(`/api/v1/fields/stats/${TENANT_A}`)
        .set("Authorization", bearerToken(TENANT_A));

      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.timestamp).toBeDefined();
    });

    it("→ 403 when accessing stats for a different tenant", async () => {
      const res = await request(app.getHttpServer())
        .get(`/api/v1/fields/stats/${TENANT_B}`)
        .set("Authorization", bearerToken(TENANT_A));
      expect(res.status).toBe(403);
    });
  });

  // =========================================================================
  // Boundary History & Rollback
  // =========================================================================
  describe("Boundary History", () => {
    it("GET /:id/boundary-history → 200 with history list", async () => {
      const res = await request(app.getHttpServer())
        .get(`/api/v1/fields/${FIELD_ID}/boundary-history`)
        .set("Authorization", bearerToken(TENANT_A));

      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(Array.isArray(res.body.data)).toBe(true);
      expect(typeof res.body.count).toBe("number");
    });

    it("PUT /:id/boundary → 200 with updated boundary", async () => {
      mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());

      const res = await request(app.getHttpServer())
        .put(`/api/v1/fields/${FIELD_ID}/boundary`)
        .set("Authorization", bearerToken(TENANT_A))
        .send({
          coordinates: [
            [46.700, 24.700],
            [46.701, 24.700],
            [46.701, 24.701],
            [46.700, 24.701],
          ],
          reason: "Land survey correction",
          userId: "user-001",
        });

      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.etag).toBeDefined();
    });

    it("PUT /:id/boundary → 400 with only 2 coordinates", async () => {
      const res = await request(app.getHttpServer())
        .put(`/api/v1/fields/${FIELD_ID}/boundary`)
        .set("Authorization", bearerToken(TENANT_A))
        .send({ coordinates: [[46.7, 24.7], [46.8, 24.7]] });
      expect(res.status).toBe(400);
    });

    it("POST /:id/boundary-history/rollback → 200 with restored boundary", async () => {
      mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());
      mockPrisma.fieldBoundaryHistory.findUnique.mockResolvedValue({
        id: HISTORY_ID,
        fieldId: FIELD_ID,
        coordinates: JSON.stringify([[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8]]),
        changedAt: now,
      });

      const res = await request(app.getHttpServer())
        .post(`/api/v1/fields/${FIELD_ID}/boundary-history/rollback`)
        .set("Authorization", bearerToken(TENANT_A))
        .send({ historyId: HISTORY_ID, reason: "Rollback test" });

      expect(res.status).toBe(201);
      expect(res.body.success).toBe(true);
    });

    it("POST /:id/boundary-history/rollback → 400 when historyId is not a UUID", async () => {
      const res = await request(app.getHttpServer())
        .post(`/api/v1/fields/${FIELD_ID}/boundary-history/rollback`)
        .set("Authorization", bearerToken(TENANT_A))
        .send({ historyId: "not-a-uuid" });
      expect(res.status).toBe(400);
    });
  });

  // =========================================================================
  // KPI Snapshots
  // =========================================================================
  describe("KPI Snapshots", () => {
    it("GET /:id/kpi-snapshot → 200 or 404 depending on snapshot existence", async () => {
      // If no snapshot exists, service should return null or throw 404
      mockPrisma.fieldKpiSnapshot.findFirst.mockResolvedValue(null);
      mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());

      const res = await request(app.getHttpServer())
        .get(`/api/v1/fields/${FIELD_ID}/kpi-snapshot`)
        .set("Authorization", bearerToken(TENANT_A));

      // Accept either 200 (with null data) or 404 (not found)
      expect([200, 404]).toContain(res.status);
    });

    it("POST /:id/kpi-snapshot → 201 with saved snapshot", async () => {
      mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());
      mockPrisma.fieldKpiSnapshot.create.mockResolvedValue({
        id: "kpi-001",
        fieldId: FIELD_ID,
        tenantId: TENANT_A,
        ndvi: 0.72,
        temperature: 28,
        createdAt: now,
      });

      const res = await request(app.getHttpServer())
        .post(`/api/v1/fields/${FIELD_ID}/kpi-snapshot`)
        .set("Authorization", bearerToken(TENANT_A))
        .send({ ndvi: 0.72, temperature: 28, humidity: 65 });

      expect(res.status).toBe(201);
      expect(res.body.success).toBe(true);
    });
  });

  // =========================================================================
  // Tenant Isolation (cross-tenant IDOR prevention)
  // =========================================================================
  describe("Tenant Isolation", () => {
    it("cannot read TENANT_B field using TENANT_A token", async () => {
      // The composite key lookup (id + tenantId) returns null when tenants differ
      mockPrisma.field.findUnique.mockResolvedValue(null);

      const res = await request(app.getHttpServer())
        .get(`/api/v1/fields/${FIELD_ID}`)
        .set("Authorization", bearerToken(TENANT_A));

      expect(res.status).toBe(404);
    });

    it("findAll only returns current tenant's fields", async () => {
      // Verify tenantId is passed to the query — the mock captures arguments
      mockPrisma.field.findMany.mockResolvedValue([makeFieldRow({ tenantId: TENANT_A })]);
      mockPrisma.field.count.mockResolvedValue(1);

      await request(app.getHttpServer())
        .get("/api/v1/fields")
        .set("Authorization", bearerToken(TENANT_A));

      const findManyCall = mockPrisma.field.findMany.mock.calls[0]?.[0] as any;
      expect(findManyCall?.where?.tenantId).toBe(TENANT_A);
    });
  });

  // =========================================================================
  // Full CRUD Lifecycle Integration
  // =========================================================================
  describe("Full Lifecycle: Create → Read → Update → Delete", () => {
    it("executes the complete field lifecycle without errors", async () => {
      // 1. Create
      mockPrisma.__txFieldCreate.mockResolvedValue(makeFieldRow());
      mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow());

      const createRes = await request(app.getHttpServer())
        .post("/api/v1/fields")
        .set("Authorization", bearerToken(TENANT_A))
        .send({ name: "Lifecycle Field", tenantId: TENANT_A, cropType: "barley" });
      expect(createRes.status).toBe(201);
      const etag = createRes.body.etag as string;

      // 2. Read
      const getRes = await request(app.getHttpServer())
        .get(`/api/v1/fields/${FIELD_ID}`)
        .set("Authorization", bearerToken(TENANT_A));
      expect(getRes.status).toBe(200);

      // 3. Update with ETag
      mockPrisma.field.findUnique
        .mockResolvedValueOnce({ id: FIELD_ID, version: 1, tenantId: TENANT_A })
        .mockResolvedValueOnce(makeFieldRow({ version: 2, name: "Updated Lifecycle Field" }));

      const updateRes = await request(app.getHttpServer())
        .put(`/api/v1/fields/${FIELD_ID}`)
        .set("Authorization", bearerToken(TENANT_A))
        .set("If-Match", etag)
        .send({ name: "Updated Lifecycle Field" });
      expect(updateRes.status).toBe(200);

      // 4. Delete
      mockPrisma.field.findUnique.mockResolvedValue(makeFieldRow({ version: 2 }));
      mockPrisma.field.update.mockResolvedValue(makeFieldRow({ status: "inactive", isDeleted: true }));

      const deleteRes = await request(app.getHttpServer())
        .delete(`/api/v1/fields/${FIELD_ID}`)
        .set("Authorization", bearerToken(TENANT_A));
      expect(deleteRes.status).toBe(200);
    });
  });
});
