/**
 * Field Management Service - Controller Tests
 * Tests for Field CRUD operations, geospatial queries, and boundary management
 */

import request from "supertest";
import { Application } from "express";
import { createFieldApp } from "@sahool/field-shared";
import { AppDataSource } from "@sahool/field-shared";
import { Field } from "@sahool/field-shared";
import { FieldBoundaryHistory } from "@sahool/field-shared";
import { SyncStatus } from "@sahool/field-shared";

// Mock the data source
jest.mock("@sahool/field-shared", () => {
  const original = jest.requireActual("@sahool/field-shared");

  const mockRepository = {
    findOne: jest.fn(),
    find: jest.fn(),
    create: jest.fn(),
    save: jest.fn(),
    delete: jest.fn(),
    createQueryBuilder: jest.fn(() => ({
      where: jest.fn().mockReturnThis(),
      andWhere: jest.fn().mockReturnThis(),
      orderBy: jest.fn().mockReturnThis(),
      skip: jest.fn().mockReturnThis(),
      take: jest.fn().mockReturnThis(),
      getManyAndCount: jest.fn(),
      getMany: jest.fn(),
      getCount: jest.fn(),
    })),
  };

  return {
    ...original,
    AppDataSource: {
      initialize: jest.fn().mockResolvedValue(undefined),
      query: jest.fn(),
      getRepository: jest.fn(() => mockRepository),
      isInitialized: true,
    },
  };
});

describe("Field Management Service - Controller Tests", () => {
  let app: Application;
  let mockFieldRepo: any;
  let mockHistoryRepo: any;
  let mockSyncStatusRepo: any;

  const mockField = {
    id: "field-001",
    name: "North Farm Field",
    tenantId: "tenant-001",
    cropType: "wheat",
    status: "active",
    version: 1,
    ownerId: "owner-001",
    boundary: {
      type: "Polygon",
      coordinates: [
        [
          [44.0, 15.0],
          [44.1, 15.0],
          [44.1, 15.1],
          [44.0, 15.1],
          [44.0, 15.0],
        ],
      ],
    },
    centroid: {
      type: "Point",
      coordinates: [44.05, 15.05],
    },
    areaHectares: 100.5,
    healthScore: 0.75,
    ndviValue: 0.65,
    irrigationType: "drip",
    soilType: "clay",
    createdAt: new Date("2024-01-01"),
    updatedAt: new Date("2024-01-01"),
  };

  beforeAll(() => {
    app = createFieldApp("field-management-service-test");
  });

  beforeEach(() => {
    jest.clearAllMocks();
    mockFieldRepo = (AppDataSource as any).getRepository(Field);
    mockHistoryRepo = (AppDataSource as any).getRepository(
      FieldBoundaryHistory,
    );
    mockSyncStatusRepo = (AppDataSource as any).getRepository(SyncStatus);
  });

  describe("Health Check Endpoints", () => {
    it("GET /healthz - should return healthy status", async () => {
      const response = await request(app).get("/healthz");

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        status: "healthy",
        service: "field-management-service-test",
      });
      expect(response.body.timestamp).toBeDefined();
    });

    it("GET /readyz - should return ready status when database is connected", async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([{ result: 1 }]);

      const response = await request(app).get("/readyz");

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        status: "ready",
        database: "connected",
      });
    });

    it("GET /readyz - should return not ready when database is disconnected", async () => {
      (AppDataSource.query as jest.Mock).mockRejectedValue(
        new Error("Connection failed"),
      );

      const response = await request(app).get("/readyz");

      expect(response.status).toBe(503);
      expect(response.body.status).toBe("not ready");
      expect(response.body.database).toBe("disconnected");
    });
  });

  describe("Field CRUD Operations", () => {
    describe("GET /api/v1/fields - List all fields", () => {
      it("should return paginated list of fields", async () => {
        const mockFields = [mockField, { ...mockField, id: "field-002" }];
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockResolvedValue([mockFields, 2]);

        const response = await request(app).get("/api/v1/fields").query({
          limit: 10,
          offset: 0,
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toHaveLength(2);
        expect(response.body.pagination).toEqual({
          total: 2,
          limit: 10,
          offset: 0,
        });
      });

      it("should filter by tenantId", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockResolvedValue([[mockField], 1]);

        const response = await request(app).get("/api/v1/fields").query({
          tenantId: "tenant-001",
        });

        expect(response.status).toBe(200);
        expect(
          mockFieldRepo.createQueryBuilder().andWhere,
        ).toHaveBeenCalledWith("field.tenantId = :tenantId", {
          tenantId: "tenant-001",
        });
      });

      it("should filter by status", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockResolvedValue([[mockField], 1]);

        const response = await request(app).get("/api/v1/fields").query({
          status: "active",
        });

        expect(response.status).toBe(200);
        expect(
          mockFieldRepo.createQueryBuilder().andWhere,
        ).toHaveBeenCalledWith("field.status = :status", { status: "active" });
      });

      it("should filter by cropType", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockResolvedValue([[mockField], 1]);

        const response = await request(app).get("/api/v1/fields").query({
          cropType: "wheat",
        });

        expect(response.status).toBe(200);
        expect(
          mockFieldRepo.createQueryBuilder().andWhere,
        ).toHaveBeenCalledWith("field.cropType = :cropType", {
          cropType: "wheat",
        });
      });

      it("should handle errors gracefully", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockRejectedValue(new Error("Database error"));

        const response = await request(app).get("/api/v1/fields");

        expect(response.status).toBe(500);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe("Failed to fetch fields");
      });
    });

    describe("GET /api/v1/fields/:id - Get field by ID", () => {
      it("should return a field with ETag", async () => {
        mockFieldRepo.findOne.mockResolvedValue(mockField);

        const response = await request(app).get("/api/v1/fields/field-001");

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.id).toBe("field-001");
        expect(response.body.etag).toBeDefined();
        expect(response.body.etag).toMatch(/^"field-001_v1"$/);
      });

      it("should return 404 for non-existent field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app).get("/api/v1/fields/nonexistent");

        expect(response.status).toBe(404);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe("Field not found");
      });

      it("should handle errors gracefully", async () => {
        mockFieldRepo.findOne.mockRejectedValue(new Error("Database error"));

        const response = await request(app).get("/api/v1/fields/field-001");

        expect(response.status).toBe(500);
        expect(response.body.success).toBe(false);
      });
    });

    describe("POST /api/v1/fields - Create new field", () => {
      it("should create a field with valid data", async () => {
        const newFieldData = {
          name: "New Test Field",
          tenantId: "tenant-001",
          cropType: "corn",
          ownerId: "owner-001",
        };

        mockFieldRepo.create.mockReturnValue({ ...mockField, ...newFieldData });
        mockFieldRepo.save.mockResolvedValue({
          ...mockField,
          ...newFieldData,
          id: "field-new",
        });
        mockFieldRepo.findOne.mockResolvedValue({
          ...mockField,
          ...newFieldData,
          id: "field-new",
          areaHectares: 100.5,
        });
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app)
          .post("/api/v1/fields")
          .send(newFieldData);

        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
        expect(response.body.data.name).toBe("New Test Field");
        expect(response.body.etag).toBeDefined();
      });

      it("should create field with coordinates", async () => {
        const newFieldData = {
          name: "Geo Field",
          tenantId: "tenant-001",
          cropType: "wheat",
          coordinates: [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.1, 15.1],
            [44.0, 15.1],
          ],
        };

        mockFieldRepo.create.mockReturnValue({ ...mockField, ...newFieldData });
        mockFieldRepo.save.mockResolvedValue({
          ...mockField,
          ...newFieldData,
          id: "field-geo",
        });
        mockFieldRepo.findOne.mockResolvedValue({
          ...mockField,
          ...newFieldData,
          id: "field-geo",
        });
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app)
          .post("/api/v1/fields")
          .send(newFieldData);

        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
        expect(mockFieldRepo.create).toHaveBeenCalled();
      });

      it("should return 400 for missing required fields", async () => {
        const response = await request(app).post("/api/v1/fields").send({
          name: "Incomplete Field",
        });

        expect(response.status).toBe(400);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain("Missing required fields");
      });

      it("should validate polygon coordinates", async () => {
        const invalidData = {
          name: "Invalid Poly",
          tenantId: "tenant-001",
          cropType: "wheat",
          coordinates: [[44.0, 95.0]], // Invalid coordinates
        };

        const response = await request(app)
          .post("/api/v1/fields")
          .send(invalidData);

        expect(response.status).toBe(400);
      });
    });

    describe("PUT /api/v1/fields/:id - Update field", () => {
      it("should update field with valid If-Match header", async () => {
        const updatedField = {
          ...mockField,
          name: "Updated Field",
          version: 2,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockFieldRepo.save.mockResolvedValue(updatedField);

        const response = await request(app)
          .put("/api/v1/fields/field-001")
          .set("If-Match", '"field-001_v1"')
          .send({ name: "Updated Field" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.name).toBe("Updated Field");
        expect(response.body.etag).toBe('"field-001_v2"');
      });

      it("should return 404 for non-existent field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app)
          .put("/api/v1/fields/nonexistent")
          .send({ name: "Updated" });

        expect(response.status).toBe(404);
        expect(response.body.success).toBe(false);
      });

      it("should return 409 for version conflict", async () => {
        mockFieldRepo.findOne.mockResolvedValue(mockField);

        const response = await request(app)
          .put("/api/v1/fields/field-001")
          .set("If-Match", '"field-001_v99"')
          .send({ name: "Updated" });

        expect(response.status).toBe(409);
        expect(response.body.success).toBe(false);
        expect(response.body.serverData).toBeDefined();
      });

      it("should update multiple fields at once", async () => {
        const updatedField = {
          ...mockField,
          name: "Updated Name",
          cropType: "rice",
          status: "fallow",
          version: 2,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockFieldRepo.save.mockResolvedValue(updatedField);

        const response = await request(app)
          .put("/api/v1/fields/field-001")
          .set("If-Match", '"field-001_v1"')
          .send({
            name: "Updated Name",
            cropType: "rice",
            status: "fallow",
          });

        expect(response.status).toBe(200);
        expect(response.body.data.name).toBe("Updated Name");
        expect(response.body.data.cropType).toBe("rice");
        expect(response.body.data.status).toBe("fallow");
      });
    });

    describe("DELETE /api/v1/fields/:id - Delete field", () => {
      it("should delete an existing field", async () => {
        mockFieldRepo.delete.mockResolvedValue({ affected: 1 });

        const response = await request(app).delete("/api/v1/fields/field-001");

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.message).toBeDefined();
      });

      it("should return 404 for non-existent field", async () => {
        mockFieldRepo.delete.mockResolvedValue({ affected: 0 });

        const response = await request(app).delete(
          "/api/v1/fields/nonexistent",
        );

        expect(response.status).toBe(404);
        expect(response.body.success).toBe(false);
      });
    });
  });

  describe("Geospatial Operations", () => {
    describe("GET /api/v1/fields/nearby - Find nearby fields", () => {
      it("should find fields within radius", async () => {
        const nearbyFields = [
          {
            ...mockField,
            distance_meters: 1500,
            boundary: JSON.stringify(mockField.boundary),
            centroid: JSON.stringify(mockField.centroid),
          },
        ];
        (AppDataSource.query as jest.Mock).mockResolvedValue(nearbyFields);

        const response = await request(app).get("/api/v1/fields/nearby").query({
          lat: 15.05,
          lng: 44.05,
          radius: 5000,
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toHaveLength(1);
        expect(response.body.data[0].distance_meters).toBe(1500);
      });

      it("should return 400 for missing coordinates", async () => {
        const response = await request(app).get("/api/v1/fields/nearby").query({
          radius: 5000,
        });

        expect(response.status).toBe(400);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain("Missing required parameters");
      });

      it("should use default radius when not provided", async () => {
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app).get("/api/v1/fields/nearby").query({
          lat: 15.05,
          lng: 44.05,
        });

        expect(response.status).toBe(200);
        expect(response.body.query.radius).toBe("5000");
      });
    });
  });

  describe("NDVI Analysis Endpoints", () => {
    describe("GET /api/v1/fields/:id/ndvi - Get NDVI analysis", () => {
      it("should return NDVI analysis for a field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(mockField);

        const response = await request(app).get(
          "/api/v1/fields/field-001/ndvi",
        );

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.fieldId).toBe("field-001");
        expect(response.body.data.current).toBeDefined();
        expect(response.body.data.statistics).toBeDefined();
        expect(response.body.data.history).toBeDefined();
      });

      it("should return 404 for non-existent field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app).get(
          "/api/v1/fields/nonexistent/ndvi",
        );

        expect(response.status).toBe(404);
        expect(response.body.success).toBe(false);
      });
    });

    describe("PUT /api/v1/fields/:id/ndvi - Update NDVI value", () => {
      it("should update NDVI value within valid range", async () => {
        const updatedField = {
          ...mockField,
          ndviValue: 0.72,
          healthScore: 0.85,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockFieldRepo.save.mockResolvedValue(updatedField);

        const response = await request(app)
          .put("/api/v1/fields/field-001/ndvi")
          .send({ value: 0.72, source: "satellite" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.ndviValue).toBe(0.72);
        expect(response.body.data.category).toBeDefined();
      });

      it("should return 400 for invalid NDVI value (> 1)", async () => {
        const response = await request(app)
          .put("/api/v1/fields/field-001/ndvi")
          .send({ value: 1.5 });

        expect(response.status).toBe(400);
        expect(response.body.error).toContain(
          "NDVI value must be between -1 and 1",
        );
      });

      it("should return 400 for invalid NDVI value (< -1)", async () => {
        const response = await request(app)
          .put("/api/v1/fields/field-001/ndvi")
          .send({ value: -1.5 });

        expect(response.status).toBe(400);
      });

      it("should return 404 for non-existent field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app)
          .put("/api/v1/fields/nonexistent/ndvi")
          .send({ value: 0.5 });

        expect(response.status).toBe(404);
      });
    });

    describe("GET /api/v1/ndvi/summary - Get NDVI summary", () => {
      it("should return NDVI summary for tenant", async () => {
        const mockSummary = {
          total_fields: "10",
          average_ndvi: "0.55",
          average_health: "0.68",
          total_area: "500.5",
          healthy_count: "4",
          moderate_count: "3",
          stressed_count: "2",
          critical_count: "1",
        };
        (AppDataSource.query as jest.Mock).mockResolvedValue([mockSummary]);

        const response = await request(app)
          .get("/api/v1/ndvi/summary")
          .query({ tenantId: "tenant-001" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.totalFields).toBe(10);
        expect(response.body.data.distribution).toEqual({
          healthy: 4,
          moderate: 3,
          stressed: 2,
          critical: 1,
        });
      });

      it("should return 400 for missing tenantId", async () => {
        const response = await request(app).get("/api/v1/ndvi/summary");

        expect(response.status).toBe(400);
        expect(response.body.error).toContain("Missing required parameter");
      });
    });
  });

  describe("Mobile Sync Endpoints", () => {
    describe("GET /api/v1/fields/sync - Delta sync", () => {
      it("should return fields modified after timestamp", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getMany.mockResolvedValue([mockField]);

        const response = await request(app).get("/api/v1/fields/sync").query({
          tenantId: "tenant-001",
          since: "2024-01-01T00:00:00Z",
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toBeDefined();
        expect(response.body.sync).toBeDefined();
        expect(response.body.sync.serverTime).toBeDefined();
      });

      it("should return 400 for missing tenantId", async () => {
        const response = await request(app).get("/api/v1/fields/sync");

        expect(response.status).toBe(400);
        expect(response.body.error).toContain("Missing required parameter");
      });

      it("should handle pagination with hasMore flag", async () => {
        const fields = Array(100)
          .fill(null)
          .map((_, i) => ({ ...mockField, id: `field-${i}` }));
        mockFieldRepo.createQueryBuilder().getMany.mockResolvedValue(fields);

        const response = await request(app).get("/api/v1/fields/sync").query({
          tenantId: "tenant-001",
          limit: 100,
        });

        expect(response.status).toBe(200);
        expect(response.body.sync.hasMore).toBe(true);
      });
    });

    describe("POST /api/v1/fields/sync/batch - Batch sync", () => {
      it("should batch sync multiple fields", async () => {
        const newField = { ...mockField, id: "field-new", version: 1 };
        mockFieldRepo.create.mockReturnValue(newField);
        mockFieldRepo.save.mockResolvedValue(newField);
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockSyncStatusRepo.findOne.mockResolvedValue(null);
        mockSyncStatusRepo.create.mockReturnValue({});
        mockSyncStatusRepo.save.mockResolvedValue({});

        const response = await request(app)
          .post("/api/v1/fields/sync/batch")
          .send({
            deviceId: "device-001",
            userId: "user-001",
            tenantId: "tenant-001",
            fields: [
              { id: "field-001", name: "Updated Field", client_version: 1 },
              { _isNew: true, name: "New Field", cropType: "corn" },
            ],
          });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.results).toHaveLength(2);
        expect(response.body.summary).toBeDefined();
      });

      it("should handle version conflicts", async () => {
        const serverField = { ...mockField, version: 5 };
        mockFieldRepo.findOne.mockResolvedValue(serverField);
        mockSyncStatusRepo.findOne.mockResolvedValue(null);
        mockSyncStatusRepo.create.mockReturnValue({});
        mockSyncStatusRepo.save.mockResolvedValue({});

        const response = await request(app)
          .post("/api/v1/fields/sync/batch")
          .send({
            deviceId: "device-001",
            userId: "user-001",
            tenantId: "tenant-001",
            fields: [{ id: "field-001", name: "Updated", client_version: 1 }],
          });

        expect(response.status).toBe(200);
        expect(response.body.results[0].status).toBe("conflict");
        expect(response.body.results[0].serverData).toBeDefined();
      });

      it("should return 400 for missing required fields", async () => {
        const response = await request(app)
          .post("/api/v1/fields/sync/batch")
          .send({ deviceId: "device-001" });

        expect(response.status).toBe(400);
      });
    });

    describe("GET /api/v1/sync/status - Get sync status", () => {
      it("should return sync status for device", async () => {
        const mockSyncStatus = {
          deviceId: "device-001",
          userId: "user-001",
          tenantId: "tenant-001",
          status: "idle",
          lastSyncAt: new Date(),
          conflictsCount: 0,
        };
        mockSyncStatusRepo.findOne.mockResolvedValue(mockSyncStatus);
        mockFieldRepo.createQueryBuilder().getCount.mockResolvedValue(5);

        const response = await request(app).get("/api/v1/sync/status").query({
          deviceId: "device-001",
          tenantId: "tenant-001",
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.pendingDownloads).toBe(5);
      });

      it("should return 400 for missing deviceId", async () => {
        const response = await request(app)
          .get("/api/v1/sync/status")
          .query({ tenantId: "tenant-001" });

        expect(response.status).toBe(400);
      });
    });

    describe("PUT /api/v1/sync/status - Update sync status", () => {
      it("should update sync status", async () => {
        mockSyncStatusRepo.findOne.mockResolvedValue(null);
        mockSyncStatusRepo.create.mockReturnValue({});
        mockSyncStatusRepo.save.mockResolvedValue({
          deviceId: "device-001",
          userId: "user-001",
          tenantId: "tenant-001",
          status: "idle",
        });

        const response = await request(app).put("/api/v1/sync/status").send({
          deviceId: "device-001",
          userId: "user-001",
          tenantId: "tenant-001",
          status: "idle",
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
      });

      it("should return 400 for missing required fields", async () => {
        const response = await request(app)
          .put("/api/v1/sync/status")
          .send({ deviceId: "device-001" });

        expect(response.status).toBe(400);
      });
    });
  });

  describe("Boundary History Endpoints", () => {
    describe("GET /api/v1/fields/:id/boundary-history", () => {
      it("should return boundary change history", async () => {
        const mockHistory = [
          {
            id: "history-001",
            fieldId: "field-001",
            versionAtChange: 1,
            changedBy: "user-001",
            changeSource: "mobile",
            createdAt: new Date(),
          },
        ];
        mockHistoryRepo.find.mockResolvedValue(mockHistory);
        (AppDataSource.query as jest.Mock).mockResolvedValue([
          {
            id: "history-001",
            previous_boundary_geojson: JSON.stringify(mockField.boundary),
            new_boundary_geojson: JSON.stringify(mockField.boundary),
          },
        ]);

        const response = await request(app).get(
          "/api/v1/fields/field-001/boundary-history",
        );

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toHaveLength(1);
        expect(response.body.count).toBe(1);
      });
    });

    describe("POST /api/v1/fields/:id/boundary-history/rollback", () => {
      it("should rollback to previous boundary", async () => {
        const mockHistory = {
          id: "history-001",
          fieldId: "field-001",
          previousBoundary: mockField.boundary,
          versionAtChange: 1,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockHistoryRepo.findOne.mockResolvedValue(mockHistory);
        mockHistoryRepo.create.mockReturnValue({});
        mockHistoryRepo.save.mockResolvedValue({});
        mockFieldRepo.save.mockResolvedValue({ ...mockField, version: 2 });
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app)
          .post("/api/v1/fields/field-001/boundary-history/rollback")
          .send({ historyId: "history-001", userId: "user-001" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.etag).toBeDefined();
      });

      it("should return 400 for missing historyId", async () => {
        const response = await request(app)
          .post("/api/v1/fields/field-001/boundary-history/rollback")
          .send({});

        expect(response.status).toBe(400);
      });

      it("should return 404 for non-existent field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app)
          .post("/api/v1/fields/nonexistent/boundary-history/rollback")
          .send({ historyId: "history-001" });

        expect(response.status).toBe(404);
      });
    });
  });
});
