/**
 * Field Core Service - Controller Tests
 * Tests for core field operations, geospatial queries, and API endpoints
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

describe("Field Core Service - Controller Tests", () => {
  let app: Application;
  let mockFieldRepo: any;
  let mockHistoryRepo: any;
  let mockSyncStatusRepo: any;

  const mockField = {
    id: "field-core-001",
    name: "Core Test Field",
    tenantId: "tenant-core-001",
    cropType: "rice",
    status: "active",
    version: 1,
    ownerId: "owner-core-001",
    boundary: {
      type: "Polygon",
      coordinates: [
        [
          [44.5, 15.5],
          [44.6, 15.5],
          [44.6, 15.6],
          [44.5, 15.6],
          [44.5, 15.5],
        ],
      ],
    },
    centroid: {
      type: "Point",
      coordinates: [44.55, 15.55],
    },
    areaHectares: 250.75,
    healthScore: 0.85,
    ndviValue: 0.72,
    irrigationType: "sprinkler",
    soilType: "loam",
    createdAt: new Date("2024-01-15"),
    updatedAt: new Date("2024-01-15"),
  };

  beforeAll(() => {
    app = createFieldApp("field-core-test");
  });

  beforeEach(() => {
    jest.clearAllMocks();
    mockFieldRepo = (AppDataSource as any).getRepository(Field);
    mockHistoryRepo = (AppDataSource as any).getRepository(
      FieldBoundaryHistory,
    );
    mockSyncStatusRepo = (AppDataSource as any).getRepository(SyncStatus);
  });

  describe("Health and Readiness Checks", () => {
    it("GET /healthz - should return service health status", async () => {
      const response = await request(app).get("/healthz");

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        status: "healthy",
        service: "field-core-test",
      });
      expect(response.body.timestamp).toBeDefined();
    });

    it("GET /readyz - should confirm database connection", async () => {
      (AppDataSource.query as jest.Mock).mockResolvedValue([{ result: 1 }]);

      const response = await request(app).get("/readyz");

      expect(response.status).toBe(200);
      expect(response.body).toEqual({
        status: "ready",
        database: "connected",
        timestamp: expect.any(String),
      });
    });

    it("GET /readyz - should handle database disconnection", async () => {
      (AppDataSource.query as jest.Mock).mockRejectedValue(
        new Error("Database connection lost"),
      );

      const response = await request(app).get("/readyz");

      expect(response.status).toBe(503);
      expect(response.body.status).toBe("not ready");
      expect(response.body.database).toBe("disconnected");
      expect(response.body.error).toBeDefined();
    });
  });

  describe("Core Field CRUD Operations", () => {
    describe("GET /api/v1/fields - List fields with filtering", () => {
      it("should retrieve all fields with default pagination", async () => {
        const mockFields = [mockField, { ...mockField, id: "field-core-002" }];
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockResolvedValue([mockFields, 2]);

        const response = await request(app).get("/api/v1/fields");

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toHaveLength(2);
        expect(response.body.pagination).toEqual({
          total: 2,
          limit: 100,
          offset: 0,
        });
      });

      it("should support custom pagination parameters", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockResolvedValue([[mockField], 25]);

        const response = await request(app).get("/api/v1/fields").query({
          limit: 5,
          offset: 10,
        });

        expect(response.status).toBe(200);
        expect(response.body.pagination.limit).toBe(5);
        expect(response.body.pagination.offset).toBe(10);
        expect(response.body.pagination.total).toBe(25);
      });

      it("should filter fields by multiple criteria", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockResolvedValue([[mockField], 1]);

        const response = await request(app).get("/api/v1/fields").query({
          tenantId: "tenant-core-001",
          status: "active",
          cropType: "rice",
        });

        expect(response.status).toBe(200);
        expect(
          mockFieldRepo.createQueryBuilder().andWhere,
        ).toHaveBeenCalledWith("field.tenantId = :tenantId", {
          tenantId: "tenant-core-001",
        });
        expect(
          mockFieldRepo.createQueryBuilder().andWhere,
        ).toHaveBeenCalledWith("field.status = :status", { status: "active" });
        expect(
          mockFieldRepo.createQueryBuilder().andWhere,
        ).toHaveBeenCalledWith("field.cropType = :cropType", {
          cropType: "rice",
        });
      });

      it("should handle query errors gracefully", async () => {
        mockFieldRepo
          .createQueryBuilder()
          .getManyAndCount.mockRejectedValue(
            new Error("Query execution failed"),
          );

        const response = await request(app).get("/api/v1/fields");

        expect(response.status).toBe(500);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe("Failed to fetch fields");
      });
    });

    describe("GET /api/v1/fields/:id - Retrieve single field", () => {
      it("should return field with complete data and ETag", async () => {
        mockFieldRepo.findOne.mockResolvedValue(mockField);

        const response = await request(app).get(
          "/api/v1/fields/field-core-001",
        );

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toMatchObject({
          id: "field-core-001",
          name: "Core Test Field",
          cropType: "rice",
        });
        expect(response.body.etag).toBe('"field-core-001_v1"');
      });

      it("should return 404 when field does not exist", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app).get(
          "/api/v1/fields/nonexistent-id",
        );

        expect(response.status).toBe(404);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe("Field not found");
      });
    });

    describe("POST /api/v1/fields - Create new field", () => {
      it("should create field with minimal required data", async () => {
        const newFieldData = {
          name: "New Core Field",
          tenantId: "tenant-core-002",
          cropType: "corn",
        };

        mockFieldRepo.create.mockReturnValue({ ...mockField, ...newFieldData });
        mockFieldRepo.save.mockResolvedValue({
          ...mockField,
          ...newFieldData,
          id: "field-new-core",
        });
        mockFieldRepo.findOne.mockResolvedValue({
          ...mockField,
          ...newFieldData,
          id: "field-new-core",
        });
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app)
          .post("/api/v1/fields")
          .send(newFieldData);

        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
        expect(response.body.data.name).toBe("New Core Field");
        expect(response.body.etag).toBeDefined();
        expect(response.body.message).toBeDefined();
      });

      it("should create field with complete geospatial data", async () => {
        const geoFieldData = {
          name: "Geospatial Field",
          tenantId: "tenant-core-002",
          cropType: "wheat",
          coordinates: [
            [44.5, 15.5],
            [44.6, 15.5],
            [44.6, 15.6],
            [44.5, 15.6],
          ],
          irrigationType: "drip",
          soilType: "sandy",
          plantingDate: "2024-03-01",
          expectedHarvest: "2024-08-01",
        };

        mockFieldRepo.create.mockReturnValue({ ...mockField, ...geoFieldData });
        mockFieldRepo.save.mockResolvedValue({
          ...mockField,
          ...geoFieldData,
          id: "field-geo-core",
        });
        mockFieldRepo.findOne.mockResolvedValue({
          ...mockField,
          ...geoFieldData,
          id: "field-geo-core",
        });
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app)
          .post("/api/v1/fields")
          .send(geoFieldData);

        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
      });

      it("should validate and reject incomplete field data", async () => {
        const incompleteData = {
          name: "Incomplete Field",
          cropType: "wheat",
          // Missing tenantId
        };

        const response = await request(app)
          .post("/api/v1/fields")
          .send(incompleteData);

        expect(response.status).toBe(400);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain("Missing required fields");
      });

      it("should validate polygon geometry", async () => {
        const invalidGeoData = {
          name: "Invalid Geo Field",
          tenantId: "tenant-core-002",
          cropType: "rice",
          coordinates: [[44.5, 95.0]], // Invalid latitude
        };

        const response = await request(app)
          .post("/api/v1/fields")
          .send(invalidGeoData);

        expect(response.status).toBe(400);
      });
    });

    describe("PUT /api/v1/fields/:id - Update field with optimistic locking", () => {
      it("should successfully update with matching ETag", async () => {
        const updatedField = {
          ...mockField,
          name: "Updated Core Field",
          version: 2,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockFieldRepo.save.mockResolvedValue(updatedField);

        const response = await request(app)
          .put("/api/v1/fields/field-core-001")
          .set("If-Match", '"field-core-001_v1"')
          .send({ name: "Updated Core Field", cropType: "barley" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.name).toBe("Updated Core Field");
        expect(response.body.data.version).toBe(2);
        expect(response.body.etag).toBe('"field-core-001_v2"');
      });

      it("should detect and handle version conflicts (409)", async () => {
        const serverField = { ...mockField, version: 3 };
        mockFieldRepo.findOne.mockResolvedValue(serverField);

        const response = await request(app)
          .put("/api/v1/fields/field-core-001")
          .set("If-Match", '"field-core-001_v1"')
          .send({ name: "Conflicting Update" });

        expect(response.status).toBe(409);
        expect(response.body.success).toBe(false);
        expect(response.body.error).toContain("Conflict");
        expect(response.body.serverData).toBeDefined();
        expect(response.body.serverData.version).toBe(3);
      });

      it("should update without If-Match header (no conflict check)", async () => {
        const updatedField = {
          ...mockField,
          name: "No Lock Update",
          version: 2,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockFieldRepo.save.mockResolvedValue(updatedField);

        const response = await request(app)
          .put("/api/v1/fields/field-core-001")
          .send({ name: "No Lock Update" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
      });

      it("should return 404 for update on nonexistent field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app)
          .put("/api/v1/fields/does-not-exist")
          .send({ name: "Update" });

        expect(response.status).toBe(404);
      });
    });

    describe("DELETE /api/v1/fields/:id - Remove field", () => {
      it("should successfully delete existing field", async () => {
        mockFieldRepo.delete.mockResolvedValue({ affected: 1 });

        const response = await request(app).delete(
          "/api/v1/fields/field-core-001",
        );

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.message).toContain("حذف الحقل");
      });

      it("should return 404 when deleting nonexistent field", async () => {
        mockFieldRepo.delete.mockResolvedValue({ affected: 0 });

        const response = await request(app).delete(
          "/api/v1/fields/does-not-exist",
        );

        expect(response.status).toBe(404);
        expect(response.body.success).toBe(false);
      });
    });
  });

  describe("Geospatial Query Operations", () => {
    describe("GET /api/v1/fields/nearby - Proximity search", () => {
      it("should find fields within specified radius", async () => {
        const nearbyFields = [
          {
            id: "field-nearby-1",
            name: "Nearby Field 1",
            crop_type: "wheat",
            distance_meters: 1200,
            boundary: JSON.stringify(mockField.boundary),
            centroid: JSON.stringify(mockField.centroid),
          },
          {
            id: "field-nearby-2",
            name: "Nearby Field 2",
            crop_type: "rice",
            distance_meters: 3500,
            boundary: JSON.stringify(mockField.boundary),
            centroid: JSON.stringify(mockField.centroid),
          },
        ];
        (AppDataSource.query as jest.Mock).mockResolvedValue(nearbyFields);

        const response = await request(app).get("/api/v1/fields/nearby").query({
          lat: 15.55,
          lng: 44.55,
          radius: 5000,
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toHaveLength(2);
        expect(response.body.data[0].distance_meters).toBe(1200);
        expect(response.body.query).toEqual({
          lat: "15.55",
          lng: "44.55",
          radius: "5000",
        });
      });

      it("should use default radius when not specified", async () => {
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app).get("/api/v1/fields/nearby").query({
          lat: 15.55,
          lng: 44.55,
        });

        expect(response.status).toBe(200);
        expect(response.body.query.radius).toBe("5000");
      });

      it("should validate required location parameters", async () => {
        const response = await request(app).get("/api/v1/fields/nearby").query({
          radius: 5000,
        });

        expect(response.status).toBe(400);
        expect(response.body.error).toContain("Missing required parameters");
      });

      it("should handle PostGIS query errors", async () => {
        (AppDataSource.query as jest.Mock).mockRejectedValue(
          new Error("PostGIS error"),
        );

        const response = await request(app).get("/api/v1/fields/nearby").query({
          lat: 15.55,
          lng: 44.55,
          radius: 5000,
        });

        expect(response.status).toBe(500);
        expect(response.body.success).toBe(false);
      });
    });
  });

  describe("NDVI and Health Analysis", () => {
    describe("GET /api/v1/fields/:id/ndvi - Field health metrics", () => {
      it("should return comprehensive NDVI analysis", async () => {
        mockFieldRepo.findOne.mockResolvedValue(mockField);

        const response = await request(app).get(
          "/api/v1/fields/field-core-001/ndvi",
        );

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toMatchObject({
          fieldId: "field-core-001",
          fieldName: "Core Test Field",
        });
        expect(response.body.data.current).toHaveProperty("value");
        expect(response.body.data.current).toHaveProperty("category");
        expect(response.body.data.statistics).toHaveProperty("average");
        expect(response.body.data.statistics).toHaveProperty("trend");
        expect(response.body.data.history).toBeInstanceOf(Array);
      });

      it("should categorize NDVI correctly", async () => {
        const healthyField = { ...mockField, ndviValue: 0.75 };
        mockFieldRepo.findOne.mockResolvedValue(healthyField);

        const response = await request(app).get(
          "/api/v1/fields/field-core-001/ndvi",
        );

        expect(response.status).toBe(200);
        expect(response.body.data.current.category.name).toMatch(
          /healthy|very-healthy/,
        );
      });

      it("should return 404 for nonexistent field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(null);

        const response = await request(app).get(
          "/api/v1/fields/invalid-id/ndvi",
        );

        expect(response.status).toBe(404);
        expect(response.body.error).toBe("Field not found");
      });
    });

    describe("PUT /api/v1/fields/:id/ndvi - Update NDVI value", () => {
      it("should update NDVI with valid value and source", async () => {
        const updatedField = {
          ...mockField,
          ndviValue: 0.78,
          healthScore: 0.9,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockFieldRepo.save.mockResolvedValue(updatedField);

        const response = await request(app)
          .put("/api/v1/fields/field-core-001/ndvi")
          .send({ value: 0.78, source: "sentinel-2" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.ndviValue).toBe(0.78);
        expect(response.body.data.healthScore).toBeDefined();
        expect(response.body.data.category).toBeDefined();
        expect(response.body.etag).toBeDefined();
      });

      it("should validate NDVI range (-1 to 1)", async () => {
        const testCases = [
          { value: -1.5, shouldFail: true },
          { value: -1.0, shouldFail: false },
          { value: 0.0, shouldFail: false },
          { value: 1.0, shouldFail: false },
          { value: 1.5, shouldFail: true },
        ];

        for (const testCase of testCases) {
          mockFieldRepo.findOne.mockResolvedValue(mockField);
          mockFieldRepo.save.mockResolvedValue(mockField);

          const response = await request(app)
            .put("/api/v1/fields/field-core-001/ndvi")
            .send({ value: testCase.value });

          if (testCase.shouldFail) {
            expect(response.status).toBe(400);
            expect(response.body.error).toContain("NDVI value must be between");
          } else {
            expect(response.status).toBe(200);
          }
        }
      });

      it("should handle non-numeric NDVI values", async () => {
        const response = await request(app)
          .put("/api/v1/fields/field-core-001/ndvi")
          .send({ value: "invalid" });

        expect(response.status).toBe(400);
      });
    });

    describe("GET /api/v1/ndvi/summary - Tenant-wide analytics", () => {
      it("should return aggregate NDVI statistics", async () => {
        const mockSummary = {
          total_fields: "15",
          average_ndvi: "0.62",
          average_health: "0.74",
          total_area: "1250.5",
          healthy_count: "7",
          moderate_count: "5",
          stressed_count: "2",
          critical_count: "1",
        };
        (AppDataSource.query as jest.Mock).mockResolvedValue([mockSummary]);

        const response = await request(app)
          .get("/api/v1/ndvi/summary")
          .query({ tenantId: "tenant-core-001" });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toMatchObject({
          tenantId: "tenant-core-001",
          totalFields: 15,
          averageNdvi: 0.62,
          totalAreaHectares: 1250.5,
        });
        expect(response.body.data.distribution).toEqual({
          healthy: 7,
          moderate: 5,
          stressed: 2,
          critical: 1,
        });
      });

      it("should require tenantId parameter", async () => {
        const response = await request(app).get("/api/v1/ndvi/summary");

        expect(response.status).toBe(400);
        expect(response.body.error).toContain("Missing required parameter");
      });
    });
  });

  describe("Mobile Sync Operations", () => {
    describe("GET /api/v1/fields/sync - Delta synchronization", () => {
      it("should return modified fields since timestamp", async () => {
        const syncFields = [
          { ...mockField, updatedAt: new Date("2024-01-20") },
        ];
        mockFieldRepo
          .createQueryBuilder()
          .getMany.mockResolvedValue(syncFields);

        const response = await request(app).get("/api/v1/fields/sync").query({
          tenantId: "tenant-core-001",
          since: "2024-01-15T00:00:00Z",
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toBeDefined();
        expect(response.body.sync).toMatchObject({
          serverTime: expect.any(String),
          count: 1,
          hasMore: false,
        });
      });

      it("should handle invalid timestamp format", async () => {
        const response = await request(app).get("/api/v1/fields/sync").query({
          tenantId: "tenant-core-001",
          since: "invalid-timestamp",
        });

        expect(response.status).toBe(400);
        expect(response.body.error).toContain("Invalid");
      });

      it("should support pagination with hasMore flag", async () => {
        const largeDataSet = Array(100)
          .fill(null)
          .map((_, i) => ({ ...mockField, id: `field-${i}` }));
        mockFieldRepo
          .createQueryBuilder()
          .getMany.mockResolvedValue(largeDataSet);

        const response = await request(app).get("/api/v1/fields/sync").query({
          tenantId: "tenant-core-001",
          limit: 100,
        });

        expect(response.status).toBe(200);
        expect(response.body.sync.hasMore).toBe(true);
        expect(response.body.sync.nextSince).toBeDefined();
      });
    });

    describe("POST /api/v1/fields/sync/batch - Batch operations", () => {
      it("should process mixed create and update operations", async () => {
        mockFieldRepo.create.mockReturnValue({ ...mockField, id: "new-field" });
        mockFieldRepo.save.mockResolvedValue({ ...mockField, id: "new-field" });
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockSyncStatusRepo.findOne.mockResolvedValue(null);
        mockSyncStatusRepo.create.mockReturnValue({});
        mockSyncStatusRepo.save.mockResolvedValue({});

        const response = await request(app)
          .post("/api/v1/fields/sync/batch")
          .send({
            deviceId: "device-core-001",
            userId: "user-core-001",
            tenantId: "tenant-core-001",
            fields: [
              { id: "field-core-001", name: "Updated", client_version: 1 },
              {
                _isNew: true,
                name: "New Field",
                cropType: "corn",
                tenantId: "tenant-core-001",
              },
            ],
          });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.results).toHaveLength(2);
        expect(response.body.summary).toMatchObject({
          total: 2,
          created: expect.any(Number),
          updated: expect.any(Number),
        });
      });

      it("should detect and report version conflicts", async () => {
        const serverField = { ...mockField, version: 10 };
        mockFieldRepo.findOne.mockResolvedValue(serverField);
        mockSyncStatusRepo.findOne.mockResolvedValue(null);
        mockSyncStatusRepo.create.mockReturnValue({});
        mockSyncStatusRepo.save.mockResolvedValue({});

        const response = await request(app)
          .post("/api/v1/fields/sync/batch")
          .send({
            deviceId: "device-core-001",
            userId: "user-core-001",
            tenantId: "tenant-core-001",
            fields: [
              {
                id: "field-core-001",
                name: "Outdated Update",
                client_version: 1,
              },
            ],
          });

        expect(response.status).toBe(200);
        expect(response.body.results[0].status).toBe("conflict");
        expect(response.body.results[0].serverData.version).toBe(10);
        expect(response.body.summary.conflicts).toBe(1);
      });

      it("should track boundary changes in history", async () => {
        const existingField = { ...mockField };
        const updatedBoundary = {
          type: "Polygon",
          coordinates: [
            [
              [44.5, 15.5],
              [44.7, 15.5],
              [44.7, 15.7],
              [44.5, 15.7],
              [44.5, 15.5],
            ],
          ],
        };

        mockFieldRepo.findOne.mockResolvedValue(existingField);
        mockFieldRepo.save.mockResolvedValue({
          ...existingField,
          boundary: updatedBoundary,
        });
        mockHistoryRepo.create.mockReturnValue({});
        mockHistoryRepo.save.mockResolvedValue({});
        mockSyncStatusRepo.findOne.mockResolvedValue(null);
        mockSyncStatusRepo.create.mockReturnValue({});
        mockSyncStatusRepo.save.mockResolvedValue({});

        const response = await request(app)
          .post("/api/v1/fields/sync/batch")
          .send({
            deviceId: "device-core-001",
            userId: "user-core-001",
            tenantId: "tenant-core-001",
            fields: [
              {
                id: "field-core-001",
                boundary: updatedBoundary,
                client_version: 1,
              },
            ],
          });

        expect(response.status).toBe(200);
        expect(mockHistoryRepo.create).toHaveBeenCalled();
      });
    });

    describe("Sync Status Management", () => {
      it("GET /api/v1/sync/status - should return current sync state", async () => {
        const mockStatus = {
          deviceId: "device-core-001",
          tenantId: "tenant-core-001",
          status: "idle",
          lastSyncAt: new Date("2024-01-20"),
          conflictsCount: 0,
        };
        mockSyncStatusRepo.findOne.mockResolvedValue(mockStatus);
        mockFieldRepo.createQueryBuilder().getCount.mockResolvedValue(3);

        const response = await request(app).get("/api/v1/sync/status").query({
          deviceId: "device-core-001",
          tenantId: "tenant-core-001",
        });

        expect(response.status).toBe(200);
        expect(response.body.data.pendingDownloads).toBe(3);
        expect(response.body.data.status).toBe("idle");
      });

      it("PUT /api/v1/sync/status - should update sync status", async () => {
        mockSyncStatusRepo.findOne.mockResolvedValue(null);
        mockSyncStatusRepo.create.mockReturnValue({});
        mockSyncStatusRepo.save.mockResolvedValue({
          deviceId: "device-core-001",
          userId: "user-core-001",
          tenantId: "tenant-core-001",
          status: "syncing",
        });

        const response = await request(app).put("/api/v1/sync/status").send({
          deviceId: "device-core-001",
          userId: "user-core-001",
          tenantId: "tenant-core-001",
          status: "syncing",
        });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
      });
    });
  });

  describe("Boundary History Management", () => {
    describe("GET /api/v1/fields/:id/boundary-history", () => {
      it("should retrieve complete boundary change history", async () => {
        const mockHistory = [
          {
            id: "history-001",
            fieldId: "field-core-001",
            versionAtChange: 2,
            changedBy: "user-core-001",
            changeSource: "mobile",
            areaChangeHectares: -5.5,
            createdAt: new Date("2024-01-20"),
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
          "/api/v1/fields/field-core-001/boundary-history",
        );

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toHaveLength(1);
        expect(response.body.data[0]).toMatchObject({
          id: "history-001",
          fieldId: "field-core-001",
          versionAtChange: 2,
          areaChangeHectares: -5.5,
        });
      });

      it("should support pagination via limit parameter", async () => {
        const mockHistory = Array(20)
          .fill(null)
          .map((_, i) => ({
            id: `history-${i}`,
            fieldId: "field-core-001",
            versionAtChange: i + 1,
            changedBy: "user-core-001",
            changeSource: "api",
            createdAt: new Date(),
          }));
        mockHistoryRepo.find.mockResolvedValue(mockHistory.slice(0, 10));
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app)
          .get("/api/v1/fields/field-core-001/boundary-history")
          .query({ limit: 10 });

        expect(response.status).toBe(200);
        expect(response.body.data).toHaveLength(10);
      });
    });

    describe("POST /api/v1/fields/:id/boundary-history/rollback", () => {
      it("should rollback boundary to previous version", async () => {
        const historyEntry = {
          id: "history-001",
          fieldId: "field-core-001",
          previousBoundary: mockField.boundary,
          versionAtChange: 1,
        };
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockHistoryRepo.findOne.mockResolvedValue(historyEntry);
        mockHistoryRepo.create.mockReturnValue({});
        mockHistoryRepo.save.mockResolvedValue({});
        mockFieldRepo.save.mockResolvedValue({ ...mockField, version: 2 });
        (AppDataSource.query as jest.Mock).mockResolvedValue([]);

        const response = await request(app)
          .post("/api/v1/fields/field-core-001/boundary-history/rollback")
          .send({
            historyId: "history-001",
            userId: "user-core-001",
            reason: "Incorrect boundary update",
          });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data).toBeDefined();
        expect(response.body.etag).toBeDefined();
      });

      it("should validate historyId is provided", async () => {
        const response = await request(app)
          .post("/api/v1/fields/field-core-001/boundary-history/rollback")
          .send({ userId: "user-core-001" });

        expect(response.status).toBe(400);
        expect(response.body.error).toContain("Missing required field");
      });

      it("should verify history entry belongs to field", async () => {
        mockFieldRepo.findOne.mockResolvedValue(mockField);
        mockHistoryRepo.findOne.mockResolvedValue(null);

        const response = await request(app)
          .post("/api/v1/fields/field-core-001/boundary-history/rollback")
          .send({ historyId: "wrong-history-id", userId: "user-core-001" });

        expect(response.status).toBe(404);
        expect(response.body.error).toContain("History entry not found");
      });
    });
  });

  describe("ETag and Optimistic Concurrency Control", () => {
    it("should include ETag in GET response", async () => {
      mockFieldRepo.findOne.mockResolvedValue(mockField);

      const response = await request(app).get("/api/v1/fields/field-core-001");

      expect(response.body.etag).toBeDefined();
      expect(response.body.etag).toMatch(/^"field-core-001_v\d+"$/);
    });

    it("should validate If-Match header on update", async () => {
      mockFieldRepo.findOne.mockResolvedValue(mockField);
      mockFieldRepo.save.mockResolvedValue({ ...mockField, version: 2 });

      const response = await request(app)
        .put("/api/v1/fields/field-core-001")
        .set("If-Match", '"field-core-001_v1"')
        .send({ name: "Updated" });

      expect(response.status).toBe(200);
    });

    it("should return 409 Conflict with server data on ETag mismatch", async () => {
      mockFieldRepo.findOne.mockResolvedValue(mockField);

      const response = await request(app)
        .put("/api/v1/fields/field-core-001")
        .set("If-Match", '"field-core-001_v99"')
        .send({ name: "Conflicting Update" });

      expect(response.status).toBe(409);
      expect(response.body.serverData).toBeDefined();
      expect(response.body.serverETag).toBe('"field-core-001_v1"');
    });
  });
});
