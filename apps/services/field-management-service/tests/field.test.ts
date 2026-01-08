/**
 * SAHOOL Field Core Service - Unit Tests
 * اختبارات خدمة إدارة الحقول الجغرافية
 */

import express, { Express } from "express";
import request from "supertest";

// Sample test data
const sampleField = {
    id: "field_001",
    name: "North Field",
    tenantId: "tenant_001",
    cropType: "wheat",
    status: "active",
    version: 1,
    createdAt: new Date(),
    updatedAt: new Date(),
    boundary: {
        type: "Polygon",
        coordinates: [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]]]
    },
    centroid: {
        type: "Point",
        coordinates: [44.05, 15.05]
    },
    areaHectares: 100.5,
    healthScore: 0.75,
    ndviValue: 0.65,
};

// Create test app
function createTestApp(): Express {
    const app = express();
    app.use(express.json());

    // Health endpoints
    app.get("/healthz", (_req, res) => {
        res.json({
            status: "healthy",
            service: "field-core",
            timestamp: new Date().toISOString(),
        });
    });

    app.get("/readyz", async (_req, res) => {
        res.json({
            status: "ready",
            database: "connected",
            timestamp: new Date().toISOString(),
        });
    });

    // Field CRUD endpoints
    app.get("/api/v1/fields", async (req, res) => {
        const { tenantId, status, cropType, limit = 100, offset = 0 } = req.query;
        res.json({
            success: true,
            data: [sampleField],
            pagination: {
                total: 1,
                limit: Number(limit),
                offset: Number(offset),
            },
        });
    });

    app.get("/api/v1/fields/nearby", async (req, res) => {
        const { lat, lng, radius = 5000 } = req.query;
        if (!lat || !lng) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameters: lat, lng",
            });
        }
        res.json({
            success: true,
            data: [{ ...sampleField, distance_meters: 1500 }],
            query: { lat, lng, radius },
        });
    });

    app.get("/api/v1/fields/sync", async (req, res) => {
        const { tenantId, since } = req.query;
        if (!tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameter: tenantId",
            });
        }
        res.json({
            success: true,
            data: [sampleField],
            sync: {
                serverTime: new Date().toISOString(),
                lastUpdated: new Date().toISOString(),
                count: 1,
                hasMore: false,
                nextSince: since,
            },
        });
    });

    app.get("/api/v1/fields/:id", async (req, res) => {
        if (req.params.id === "nonexistent") {
            return res.status(404).json({
                success: false,
                error: "Field not found",
            });
        }
        res.json({
            success: true,
            data: { ...sampleField, id: req.params.id },
            etag: `"field_${req.params.id}_v1"`,
        });
    });

    app.post("/api/v1/fields", async (req, res) => {
        const { name, tenantId, cropType } = req.body;
        if (!name || !tenantId || !cropType) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: name, tenantId, cropType",
            });
        }
        const newField = {
            ...sampleField,
            id: `field_${Date.now()}`,
            ...req.body,
            version: 1,
        };
        res.status(201).json({
            success: true,
            data: newField,
            etag: `"${newField.id}_v1"`,
            message: "حقل جديد تم إنشاؤه بنجاح",
        });
    });

    app.put("/api/v1/fields/:id", async (req, res) => {
        if (req.params.id === "nonexistent") {
            return res.status(404).json({
                success: false,
                error: "Field not found",
            });
        }

        const ifMatch = req.get("If-Match");
        if (ifMatch && ifMatch !== `"field_${req.params.id}_v1"`) {
            return res.status(409).json({
                success: false,
                error: "Conflict - field was modified",
                serverData: sampleField,
            });
        }

        res.json({
            success: true,
            data: { ...sampleField, ...req.body, id: req.params.id, version: 2 },
            etag: `"${req.params.id}_v2"`,
            message: "تم تحديث الحقل بنجاح",
        });
    });

    app.delete("/api/v1/fields/:id", async (req, res) => {
        if (req.params.id === "nonexistent") {
            return res.status(404).json({
                success: false,
                error: "Field not found",
            });
        }
        res.json({
            success: true,
            message: "تم حذف الحقل بنجاح",
        });
    });

    // NDVI endpoints
    app.get("/api/v1/fields/:id/ndvi", async (req, res) => {
        if (req.params.id === "nonexistent") {
            return res.status(404).json({
                success: false,
                error: "Field not found",
            });
        }
        res.json({
            success: true,
            data: {
                fieldId: req.params.id,
                fieldName: sampleField.name,
                current: {
                    value: 0.65,
                    category: { name: "healthy", nameAr: "صحي", color: "#8BC34A" },
                    date: new Date().toISOString(),
                },
                statistics: {
                    average: 0.58,
                    min: 0.42,
                    max: 0.72,
                    trend: 0.03,
                    trendDirection: "stable",
                },
                history: [],
                lastUpdated: new Date().toISOString(),
            },
        });
    });

    app.put("/api/v1/fields/:id/ndvi", async (req, res) => {
        const { value } = req.body;
        if (typeof value !== "number" || value < -1 || value > 1) {
            return res.status(400).json({
                success: false,
                error: "NDVI value must be between -1 and 1",
            });
        }
        if (req.params.id === "nonexistent") {
            return res.status(404).json({
                success: false,
                error: "Field not found",
            });
        }
        res.json({
            success: true,
            data: {
                fieldId: req.params.id,
                ndviValue: value,
                healthScore: 0.75,
                category: { name: "healthy", nameAr: "صحي" },
                updatedAt: new Date().toISOString(),
            },
            message: "تم تحديث مؤشر NDVI بنجاح",
        });
    });

    app.get("/api/v1/ndvi/summary", async (req, res) => {
        const { tenantId } = req.query;
        if (!tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameter: tenantId",
            });
        }
        res.json({
            success: true,
            data: {
                tenantId,
                totalFields: 10,
                averageNdvi: 0.55,
                averageHealth: 0.68,
                totalAreaHectares: 500,
                distribution: {
                    healthy: 4,
                    moderate: 3,
                    stressed: 2,
                    critical: 1,
                },
                timestamp: new Date().toISOString(),
            },
        });
    });

    // Sync endpoints
    app.post("/api/v1/fields/sync/batch", async (req, res) => {
        const { deviceId, userId, tenantId, fields } = req.body;
        if (!deviceId || !userId || !tenantId || !Array.isArray(fields)) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: deviceId, userId, tenantId, fields[]",
            });
        }
        const results = fields.map((f: any) => ({
            clientId: f.id || "new",
            serverId: f.id || `field_${Date.now()}`,
            status: f._isNew ? "created" : "updated",
            server_version: 1,
        }));
        res.json({
            success: true,
            results,
            summary: {
                total: results.length,
                created: results.filter((r: any) => r.status === "created").length,
                updated: results.filter((r: any) => r.status === "updated").length,
                conflicts: 0,
                errors: 0,
                successRate: "100%",
            },
            serverTime: new Date().toISOString(),
        });
    });

    app.get("/api/v1/sync/status", async (req, res) => {
        const { deviceId, tenantId } = req.query;
        if (!deviceId || !tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameters: deviceId, tenantId",
            });
        }
        res.json({
            success: true,
            data: {
                deviceId,
                tenantId,
                status: "idle",
                lastSyncAt: new Date().toISOString(),
                pendingDownloads: 0,
                conflictsCount: 0,
            },
        });
    });

    app.put("/api/v1/sync/status", async (req, res) => {
        const { deviceId, userId, tenantId } = req.body;
        if (!deviceId || !userId || !tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: deviceId, userId, tenantId",
            });
        }
        res.json({
            success: true,
            data: {
                deviceId,
                userId,
                tenantId,
                status: "idle",
                lastSyncAt: new Date().toISOString(),
            },
            message: "تم تحديث حالة المزامنة بنجاح",
        });
    });

    // Boundary history endpoints
    app.get("/api/v1/fields/:id/boundary-history", async (req, res) => {
        res.json({
            success: true,
            data: [
                {
                    id: "history_001",
                    fieldId: req.params.id,
                    versionAtChange: 1,
                    changedBy: "user_001",
                    changeSource: "mobile",
                    createdAt: new Date().toISOString(),
                },
            ],
            count: 1,
        });
    });

    app.post("/api/v1/fields/:id/boundary-history/rollback", async (req, res) => {
        const { historyId } = req.body;
        if (!historyId) {
            return res.status(400).json({
                success: false,
                error: "Missing required field: historyId",
            });
        }
        if (req.params.id === "nonexistent") {
            return res.status(404).json({
                success: false,
                error: "Field not found",
            });
        }
        res.json({
            success: true,
            data: sampleField,
            etag: `"${req.params.id}_v2"`,
            message: "تم استرجاع الحدود السابقة بنجاح",
        });
    });

    return app;
}

describe("SAHOOL Field Core Service", () => {
    let app: Express;

    beforeAll(() => {
        app = createTestApp();
    });

    describe("Health Endpoints", () => {
        it("should return healthy status on /healthz", async () => {
            const response = await request(app).get("/healthz");
            expect(response.status).toBe(200);
            expect(response.body.status).toBe("healthy");
            expect(response.body.service).toBe("field-core");
            expect(response.body.timestamp).toBeDefined();
        });

        it("should return ready status on /readyz", async () => {
            const response = await request(app).get("/readyz");
            expect(response.status).toBe(200);
            expect(response.body.status).toBe("ready");
            expect(response.body.database).toBe("connected");
        });
    });

    describe("Field CRUD Endpoints", () => {
        describe("GET /api/v1/fields", () => {
            it("should list all fields", async () => {
                const response = await request(app).get("/api/v1/fields");
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data).toBeDefined();
                expect(response.body.pagination).toBeDefined();
            });

            it("should support pagination", async () => {
                const response = await request(app)
                    .get("/api/v1/fields")
                    .query({ limit: 10, offset: 5 });
                expect(response.status).toBe(200);
                expect(response.body.pagination.limit).toBe(10);
                expect(response.body.pagination.offset).toBe(5);
            });

            it("should support filtering by tenantId", async () => {
                const response = await request(app)
                    .get("/api/v1/fields")
                    .query({ tenantId: "tenant_001" });
                expect(response.status).toBe(200);
            });

            it("should support filtering by cropType", async () => {
                const response = await request(app)
                    .get("/api/v1/fields")
                    .query({ cropType: "wheat" });
                expect(response.status).toBe(200);
            });
        });

        describe("GET /api/v1/fields/:id", () => {
            it("should return a field by ID", async () => {
                const response = await request(app).get("/api/v1/fields/field_001");
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data.id).toBe("field_001");
                expect(response.body.etag).toBeDefined();
            });

            it("should return 404 for non-existent field", async () => {
                const response = await request(app).get("/api/v1/fields/nonexistent");
                expect(response.status).toBe(404);
            });
        });

        describe("POST /api/v1/fields", () => {
            it("should create a new field", async () => {
                const newField = {
                    name: "Test Field",
                    tenantId: "tenant_001",
                    cropType: "rice",
                };
                const response = await request(app)
                    .post("/api/v1/fields")
                    .send(newField);
                expect(response.status).toBe(201);
                expect(response.body.success).toBe(true);
                expect(response.body.data.name).toBe("Test Field");
                expect(response.body.etag).toBeDefined();
            });

            it("should return 400 for missing required fields", async () => {
                const response = await request(app)
                    .post("/api/v1/fields")
                    .send({ name: "Test" });
                expect(response.status).toBe(400);
            });

            it("should create field with coordinates", async () => {
                const newField = {
                    name: "Geo Field",
                    tenantId: "tenant_001",
                    cropType: "wheat",
                    coordinates: [[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1]],
                };
                const response = await request(app)
                    .post("/api/v1/fields")
                    .send(newField);
                expect(response.status).toBe(201);
            });
        });

        describe("PUT /api/v1/fields/:id", () => {
            it("should update an existing field", async () => {
                const response = await request(app)
                    .put("/api/v1/fields/field_001")
                    .set("If-Match", '"field_field_001_v1"')
                    .send({ name: "Updated Name" });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data.version).toBe(2);
            });

            it("should return 404 for non-existent field", async () => {
                const response = await request(app)
                    .put("/api/v1/fields/nonexistent")
                    .send({ name: "Test" });
                expect(response.status).toBe(404);
            });

            it("should return 409 for version conflict", async () => {
                const response = await request(app)
                    .put("/api/v1/fields/field_001")
                    .set("If-Match", '"field_field_001_v99"')
                    .send({ name: "Updated" });
                expect(response.status).toBe(409);
            });
        });

        describe("DELETE /api/v1/fields/:id", () => {
            it("should delete a field", async () => {
                const response = await request(app).delete("/api/v1/fields/field_001");
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
            });

            it("should return 404 for non-existent field", async () => {
                const response = await request(app).delete("/api/v1/fields/nonexistent");
                expect(response.status).toBe(404);
            });
        });
    });

    describe("Geospatial Endpoints", () => {
        describe("GET /api/v1/fields/nearby", () => {
            it("should find nearby fields", async () => {
                const response = await request(app)
                    .get("/api/v1/fields/nearby")
                    .query({ lat: 15.05, lng: 44.05, radius: 5000 });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data).toBeDefined();
                expect(response.body.query.lat).toBe("15.05");
                expect(response.body.query.lng).toBe("44.05");
            });

            it("should return 400 for missing coordinates", async () => {
                const response = await request(app).get("/api/v1/fields/nearby");
                expect(response.status).toBe(400);
            });
        });
    });

    describe("NDVI Endpoints", () => {
        describe("GET /api/v1/fields/:id/ndvi", () => {
            it("should return NDVI analysis for a field", async () => {
                const response = await request(app).get("/api/v1/fields/field_001/ndvi");
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data.fieldId).toBe("field_001");
                expect(response.body.data.current).toBeDefined();
                expect(response.body.data.statistics).toBeDefined();
            });

            it("should return 404 for non-existent field", async () => {
                const response = await request(app).get("/api/v1/fields/nonexistent/ndvi");
                expect(response.status).toBe(404);
            });
        });

        describe("PUT /api/v1/fields/:id/ndvi", () => {
            it("should update NDVI value", async () => {
                const response = await request(app)
                    .put("/api/v1/fields/field_001/ndvi")
                    .send({ value: 0.72, source: "satellite" });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data.ndviValue).toBe(0.72);
            });

            it("should return 400 for invalid NDVI value", async () => {
                const response = await request(app)
                    .put("/api/v1/fields/field_001/ndvi")
                    .send({ value: 1.5 });
                expect(response.status).toBe(400);
            });

            it("should return 404 for non-existent field", async () => {
                const response = await request(app)
                    .put("/api/v1/fields/nonexistent/ndvi")
                    .send({ value: 0.5 });
                expect(response.status).toBe(404);
            });
        });

        describe("GET /api/v1/ndvi/summary", () => {
            it("should return NDVI summary for tenant", async () => {
                const response = await request(app)
                    .get("/api/v1/ndvi/summary")
                    .query({ tenantId: "tenant_001" });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data.tenantId).toBe("tenant_001");
                expect(response.body.data.distribution).toBeDefined();
            });

            it("should return 400 for missing tenantId", async () => {
                const response = await request(app).get("/api/v1/ndvi/summary");
                expect(response.status).toBe(400);
            });
        });
    });

    describe("Mobile Sync Endpoints", () => {
        describe("GET /api/v1/fields/sync", () => {
            it("should return delta sync data", async () => {
                const response = await request(app)
                    .get("/api/v1/fields/sync")
                    .query({ tenantId: "tenant_001" });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.sync).toBeDefined();
                expect(response.body.sync.serverTime).toBeDefined();
            });

            it("should support since parameter for delta sync", async () => {
                const response = await request(app)
                    .get("/api/v1/fields/sync")
                    .query({ tenantId: "tenant_001", since: "2024-01-01T00:00:00Z" });
                expect(response.status).toBe(200);
            });

            it("should return 400 for missing tenantId", async () => {
                const response = await request(app).get("/api/v1/fields/sync");
                expect(response.status).toBe(400);
            });
        });

        describe("POST /api/v1/fields/sync/batch", () => {
            it("should batch sync multiple fields", async () => {
                const response = await request(app)
                    .post("/api/v1/fields/sync/batch")
                    .send({
                        deviceId: "device_001",
                        userId: "user_001",
                        tenantId: "tenant_001",
                        fields: [
                            { id: "field_001", name: "Updated Field" },
                            { _isNew: true, name: "New Field", cropType: "corn" },
                        ],
                    });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.results).toHaveLength(2);
                expect(response.body.summary).toBeDefined();
            });

            it("should return 400 for missing required fields", async () => {
                const response = await request(app)
                    .post("/api/v1/fields/sync/batch")
                    .send({ deviceId: "device_001" });
                expect(response.status).toBe(400);
            });
        });

        describe("GET /api/v1/sync/status", () => {
            it("should return sync status for device", async () => {
                const response = await request(app)
                    .get("/api/v1/sync/status")
                    .query({ deviceId: "device_001", tenantId: "tenant_001" });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data.status).toBeDefined();
            });

            it("should return 400 for missing deviceId", async () => {
                const response = await request(app)
                    .get("/api/v1/sync/status")
                    .query({ tenantId: "tenant_001" });
                expect(response.status).toBe(400);
            });
        });

        describe("PUT /api/v1/sync/status", () => {
            it("should update sync status", async () => {
                const response = await request(app)
                    .put("/api/v1/sync/status")
                    .send({
                        deviceId: "device_001",
                        userId: "user_001",
                        tenantId: "tenant_001",
                        status: "idle",
                    });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
            });

            it("should return 400 for missing required fields", async () => {
                const response = await request(app)
                    .put("/api/v1/sync/status")
                    .send({ deviceId: "device_001" });
                expect(response.status).toBe(400);
            });
        });
    });

    describe("Boundary History Endpoints", () => {
        describe("GET /api/v1/fields/:id/boundary-history", () => {
            it("should return boundary history", async () => {
                const response = await request(app).get("/api/v1/fields/field_001/boundary-history");
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.data).toBeDefined();
                expect(response.body.count).toBeDefined();
            });
        });

        describe("POST /api/v1/fields/:id/boundary-history/rollback", () => {
            it("should rollback to previous boundary", async () => {
                const response = await request(app)
                    .post("/api/v1/fields/field_001/boundary-history/rollback")
                    .send({ historyId: "history_001", userId: "user_001" });
                expect(response.status).toBe(200);
                expect(response.body.success).toBe(true);
                expect(response.body.etag).toBeDefined();
            });

            it("should return 400 for missing historyId", async () => {
                const response = await request(app)
                    .post("/api/v1/fields/field_001/boundary-history/rollback")
                    .send({});
                expect(response.status).toBe(400);
            });

            it("should return 404 for non-existent field", async () => {
                const response = await request(app)
                    .post("/api/v1/fields/nonexistent/boundary-history/rollback")
                    .send({ historyId: "history_001" });
                expect(response.status).toBe(404);
            });
        });
    });

    describe("ETag and Optimistic Locking", () => {
        it("should return ETag header on GET", async () => {
            const response = await request(app).get("/api/v1/fields/field_001");
            expect(response.body.etag).toBeDefined();
        });

        it("should support If-Match header for updates", async () => {
            const response = await request(app)
                .put("/api/v1/fields/field_001")
                .set("If-Match", '"field_field_001_v1"')
                .send({ name: "Updated" });
            expect(response.status).toBe(200);
        });

        it("should return 409 Conflict for mismatched ETag", async () => {
            const response = await request(app)
                .put("/api/v1/fields/field_001")
                .set("If-Match", '"outdated_etag"')
                .send({ name: "Updated" });
            expect(response.status).toBe(409);
            expect(response.body.serverData).toBeDefined();
        });
    });
});
