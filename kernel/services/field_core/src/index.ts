import "reflect-metadata";
import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import { AppDataSource } from "./data-source";
import { Field } from "./entity/Field";
import {
    generateETag,
    validateIfMatch,
    createConflictResponse,
    setETagHeader,
    getIfMatchHeader
} from "./middleware/etag";

const app = express();
const PORT = parseInt(process.env.PORT || "3000");

// ─────────────────────────────────────────────────────────────────────────────
// Middleware
// ─────────────────────────────────────────────────────────────────────────────

app.use(cors());
app.use(express.json());

// ETag header middleware
app.use(setETagHeader);

// Request logging with ETag info
app.use((req: Request, _res: Response, next: NextFunction) => {
    const ifMatch = getIfMatchHeader(req);
    const etagInfo = ifMatch ? ` [If-Match: ${ifMatch}]` : "";
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}${etagInfo}`);
    next();
});

// ─────────────────────────────────────────────────────────────────────────────
// Health Check Endpoints
// ─────────────────────────────────────────────────────────────────────────────

app.get("/healthz", (_req: Request, res: Response) => {
    res.json({
        status: "healthy",
        service: "field-core",
        timestamp: new Date().toISOString()
    });
});

app.get("/readyz", async (_req: Request, res: Response) => {
    try {
        await AppDataSource.query("SELECT 1");
        res.json({
            status: "ready",
            database: "connected",
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(503).json({
            status: "not ready",
            database: "disconnected",
            error: error instanceof Error ? error.message : "Unknown error"
        });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// Field API Endpoints
// ─────────────────────────────────────────────────────────────────────────────

/**
 * GET /api/v1/fields
 * List all fields with optional filtering
 */
app.get("/api/v1/fields", async (req: Request, res: Response) => {
    try {
        const fieldRepo = AppDataSource.getRepository(Field);
        const { tenantId, status, cropType, limit = 100, offset = 0 } = req.query;

        const queryBuilder = fieldRepo.createQueryBuilder("field");

        if (tenantId) {
            queryBuilder.andWhere("field.tenantId = :tenantId", { tenantId });
        }
        if (status) {
            queryBuilder.andWhere("field.status = :status", { status });
        }
        if (cropType) {
            queryBuilder.andWhere("field.cropType = :cropType", { cropType });
        }

        const [fields, total] = await queryBuilder
            .orderBy("field.createdAt", "DESC")
            .skip(Number(offset))
            .take(Number(limit))
            .getManyAndCount();

        res.json({
            success: true,
            data: fields,
            pagination: {
                total,
                limit: Number(limit),
                offset: Number(offset)
            }
        });
    } catch (error) {
        console.error("Error fetching fields:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch fields"
        });
    }
});

/**
 * GET /api/v1/fields/:id
 * Get a single field by ID
 * Returns ETag header for optimistic locking
 */
app.get("/api/v1/fields/:id", async (req: Request, res: Response) => {
    try {
        const fieldRepo = AppDataSource.getRepository(Field);
        const field = await fieldRepo.findOne({
            where: { id: req.params.id }
        });

        if (!field) {
            return res.status(404).json({
                success: false,
                error: "Field not found"
            });
        }

        // Generate and set ETag from field ID and version
        const etag = generateETag(field.id, field.version);
        res.locals.etag = etag;

        res.json({
            success: true,
            data: field,
            etag: etag // Also include in body for mobile clients
        });
    } catch (error) {
        console.error("Error fetching field:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch field"
        });
    }
});

/**
 * POST /api/v1/fields
 * Create a new field with geospatial boundary
 */
app.post("/api/v1/fields", async (req: Request, res: Response) => {
    try {
        const fieldRepo = AppDataSource.getRepository(Field);
        const {
            name,
            tenantId,
            cropType,
            coordinates,
            ownerId,
            irrigationType,
            soilType,
            plantingDate,
            expectedHarvest,
            metadata
        } = req.body;

        // Validate required fields
        if (!name || !tenantId || !cropType) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: name, tenantId, cropType"
            });
        }

        // Create field entity
        const newField = fieldRepo.create({
            name,
            tenantId,
            cropType,
            ownerId,
            irrigationType,
            soilType,
            plantingDate: plantingDate ? new Date(plantingDate) : undefined,
            expectedHarvest: expectedHarvest ? new Date(expectedHarvest) : undefined,
            metadata,
            status: "active"
        });

        // If coordinates provided, create GeoJSON polygon
        if (coordinates && Array.isArray(coordinates) && coordinates.length >= 3) {
            // Ensure polygon is closed
            const closedCoords = [...coordinates];
            if (JSON.stringify(closedCoords[0]) !== JSON.stringify(closedCoords[closedCoords.length - 1])) {
                closedCoords.push(closedCoords[0]);
            }

            newField.boundary = {
                type: "Polygon",
                coordinates: [closedCoords]
            };

            // Calculate centroid (simple average for now)
            const centroidLng = closedCoords.reduce((sum, c) => sum + c[0], 0) / closedCoords.length;
            const centroidLat = closedCoords.reduce((sum, c) => sum + c[1], 0) / closedCoords.length;

            newField.centroid = {
                type: "Point",
                coordinates: [centroidLng, centroidLat]
            };
        }

        const savedField = await fieldRepo.save(newField);

        // Calculate area using PostGIS if boundary exists
        if (savedField.boundary) {
            await AppDataSource.query(`
                UPDATE fields
                SET area_hectares = ST_Area(ST_Transform(boundary, 32637)) / 10000
                WHERE id = $1
            `, [savedField.id]);
        }

        // Fetch updated field with calculated area
        const finalField = await fieldRepo.findOne({
            where: { id: savedField.id }
        });

        // Generate ETag for newly created field
        const etag = finalField ? generateETag(finalField.id, finalField.version) : null;
        if (etag) {
            res.locals.etag = etag;
        }

        res.status(201).json({
            success: true,
            data: finalField,
            etag: etag,
            message: "حقل جديد تم إنشاؤه بنجاح" // New field created successfully
        });
    } catch (error) {
        console.error("Error creating field:", error);
        res.status(500).json({
            success: false,
            error: "Failed to create field"
        });
    }
});

/**
 * PUT /api/v1/fields/:id
 * Update an existing field with optimistic locking
 *
 * Headers:
 *   If-Match: ETag from previous GET request
 *
 * Returns:
 *   200: Success with new ETag
 *   404: Field not found
 *   409: Conflict - field was modified by another user
 */
app.put("/api/v1/fields/:id", async (req: Request, res: Response) => {
    try {
        const fieldRepo = AppDataSource.getRepository(Field);
        const field = await fieldRepo.findOne({
            where: { id: req.params.id }
        });

        if (!field) {
            return res.status(404).json({
                success: false,
                error: "Field not found"
            });
        }

        // Validate If-Match header for optimistic locking
        const ifMatch = getIfMatchHeader(req);
        if (ifMatch && !validateIfMatch(ifMatch, field.id, field.version)) {
            // 409 Conflict - the field was modified by another user
            const currentETag = generateETag(field.id, field.version);
            console.log(`⚠️ 409 Conflict: Field ${field.id} - Client ETag: ${ifMatch}, Server ETag: ${currentETag}`);

            return res.status(409).json(
                createConflictResponse(field, currentETag, "field")
            );
        }

        // Update allowed fields
        const allowedUpdates = [
            "name", "cropType", "status", "irrigationType",
            "soilType", "plantingDate", "expectedHarvest", "metadata"
        ];

        for (const key of allowedUpdates) {
            if (req.body[key] !== undefined) {
                (field as any)[key] = req.body[key];
            }
        }

        // Save will auto-increment the version column (optimistic lock)
        const updatedField = await fieldRepo.save(field);

        // Generate new ETag with updated version
        const newETag = generateETag(updatedField.id, updatedField.version);
        res.locals.etag = newETag;

        res.json({
            success: true,
            data: updatedField,
            etag: newETag,
            message: "تم تحديث الحقل بنجاح" // Field updated successfully
        });
    } catch (error) {
        console.error("Error updating field:", error);
        res.status(500).json({
            success: false,
            error: "Failed to update field"
        });
    }
});

/**
 * DELETE /api/v1/fields/:id
 * Delete a field
 */
app.delete("/api/v1/fields/:id", async (req: Request, res: Response) => {
    try {
        const fieldRepo = AppDataSource.getRepository(Field);
        const result = await fieldRepo.delete(req.params.id);

        if (result.affected === 0) {
            return res.status(404).json({
                success: false,
                error: "Field not found"
            });
        }

        res.json({
            success: true,
            message: "تم حذف الحقل بنجاح" // Field deleted successfully
        });
    } catch (error) {
        console.error("Error deleting field:", error);
        res.status(500).json({
            success: false,
            error: "Failed to delete field"
        });
    }
});

/**
 * GET /api/v1/fields/nearby
 * Find fields within a radius of a point (geospatial query)
 */
app.get("/api/v1/fields/nearby", async (req: Request, res: Response) => {
    try {
        const { lat, lng, radius = 5000 } = req.query; // radius in meters

        if (!lat || !lng) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameters: lat, lng"
            });
        }

        const fields = await AppDataSource.query(`
            SELECT
                id, name, crop_type, status, area_hectares, health_score,
                ST_AsGeoJSON(boundary) as boundary,
                ST_AsGeoJSON(centroid) as centroid,
                ST_Distance(
                    centroid::geography,
                    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
                ) as distance_meters
            FROM fields
            WHERE ST_DWithin(
                centroid::geography,
                ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
                $3
            )
            ORDER BY distance_meters ASC
        `, [parseFloat(lng as string), parseFloat(lat as string), parseInt(radius as string)]);

        res.json({
            success: true,
            data: fields.map((f: any) => ({
                ...f,
                boundary: f.boundary ? JSON.parse(f.boundary) : null,
                centroid: f.centroid ? JSON.parse(f.centroid) : null
            })),
            query: { lat, lng, radius }
        });
    } catch (error) {
        console.error("Error finding nearby fields:", error);
        res.status(500).json({
            success: false,
            error: "Failed to find nearby fields"
        });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// NDVI Analysis Endpoints
// ─────────────────────────────────────────────────────────────────────────────

/**
 * GET /api/v1/fields/:id/ndvi
 * Get NDVI analysis for a specific field
 */
app.get("/api/v1/fields/:id/ndvi", async (req: Request, res: Response) => {
    try {
        const fieldRepo = AppDataSource.getRepository(Field);
        const field = await fieldRepo.findOne({
            where: { id: req.params.id }
        });

        if (!field) {
            return res.status(404).json({
                success: false,
                error: "Field not found"
            });
        }

        // Generate mock NDVI history (in production, this would come from satellite data)
        const history = generateMockNdviHistory(30);
        const current = history[history.length - 1].value;
        const values = history.map(h => h.value);
        const average = values.reduce((a, b) => a + b, 0) / values.length;
        const min = Math.min(...values);
        const max = Math.max(...values);

        // Calculate trend
        const firstHalf = values.slice(0, Math.floor(values.length / 2));
        const secondHalf = values.slice(Math.floor(values.length / 2));
        const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
        const trend = secondAvg - firstAvg;

        // Determine health category
        const healthCategory = getNdviCategory(current);

        res.json({
            success: true,
            data: {
                fieldId: field.id,
                fieldName: field.name,
                current: {
                    value: current,
                    category: healthCategory,
                    date: new Date().toISOString()
                },
                statistics: {
                    average: Math.round(average * 100) / 100,
                    min: Math.round(min * 100) / 100,
                    max: Math.round(max * 100) / 100,
                    trend: Math.round(trend * 100) / 100,
                    trendDirection: trend > 0.05 ? 'improving' : trend < -0.05 ? 'declining' : 'stable'
                },
                history: history,
                lastUpdated: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error("Error fetching NDVI data:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch NDVI data"
        });
    }
});

/**
 * PUT /api/v1/fields/:id/ndvi
 * Update NDVI value for a field (from external source)
 */
app.put("/api/v1/fields/:id/ndvi", async (req: Request, res: Response) => {
    try {
        const fieldRepo = AppDataSource.getRepository(Field);
        const { value, source } = req.body;

        if (typeof value !== 'number' || value < -1 || value > 1) {
            return res.status(400).json({
                success: false,
                error: "NDVI value must be between -1 and 1"
            });
        }

        const field = await fieldRepo.findOne({
            where: { id: req.params.id }
        });

        if (!field) {
            return res.status(404).json({
                success: false,
                error: "Field not found"
            });
        }

        // Update NDVI value
        field.ndviValue = value;
        field.healthScore = calculateHealthScore(value);
        await fieldRepo.save(field);

        // Generate ETag for updated field
        const etag = generateETag(field.id, field.version);
        res.locals.etag = etag;

        res.json({
            success: true,
            data: {
                fieldId: field.id,
                ndviValue: value,
                healthScore: field.healthScore,
                category: getNdviCategory(value),
                source: source || 'manual',
                updatedAt: new Date().toISOString()
            },
            etag: etag,
            message: "تم تحديث مؤشر NDVI بنجاح"
        });
    } catch (error) {
        console.error("Error updating NDVI:", error);
        res.status(500).json({
            success: false,
            error: "Failed to update NDVI"
        });
    }
});

/**
 * GET /api/v1/ndvi/summary
 * Get NDVI summary for all fields (tenant-wide analytics)
 */
app.get("/api/v1/ndvi/summary", async (req: Request, res: Response) => {
    try {
        const { tenantId } = req.query;

        if (!tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameter: tenantId"
            });
        }

        const result = await AppDataSource.query(`
            SELECT
                COUNT(*) as total_fields,
                AVG(ndvi_value) as average_ndvi,
                AVG(health_score) as average_health,
                SUM(area_hectares) as total_area,
                COUNT(*) FILTER (WHERE ndvi_value >= 0.6) as healthy_count,
                COUNT(*) FILTER (WHERE ndvi_value >= 0.4 AND ndvi_value < 0.6) as moderate_count,
                COUNT(*) FILTER (WHERE ndvi_value >= 0.2 AND ndvi_value < 0.4) as stressed_count,
                COUNT(*) FILTER (WHERE ndvi_value < 0.2) as critical_count
            FROM fields
            WHERE tenant_id = $1 AND ndvi_value IS NOT NULL
        `, [tenantId]);

        const summary = result[0];

        res.json({
            success: true,
            data: {
                tenantId,
                totalFields: parseInt(summary.total_fields) || 0,
                averageNdvi: parseFloat(summary.average_ndvi) || 0,
                averageHealth: parseFloat(summary.average_health) || 0,
                totalAreaHectares: parseFloat(summary.total_area) || 0,
                distribution: {
                    healthy: parseInt(summary.healthy_count) || 0,
                    moderate: parseInt(summary.moderate_count) || 0,
                    stressed: parseInt(summary.stressed_count) || 0,
                    critical: parseInt(summary.critical_count) || 0
                },
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error("Error fetching NDVI summary:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch NDVI summary"
        });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// NDVI Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

function generateMockNdviHistory(days: number) {
    const history = [];
    const baseValue = 0.4 + Math.random() * 0.3;

    for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);

        // Add some variation
        const variation = (Math.random() - 0.5) * 0.15;
        const trend = (days - i) * 0.003; // Slight upward trend
        const value = Math.max(-1, Math.min(1, baseValue + variation + trend));

        history.push({
            date: date.toISOString().split('T')[0],
            value: Math.round(value * 100) / 100,
            cloudCover: Math.round(Math.random() * 30)
        });
    }

    return history;
}

function getNdviCategory(value: number): { name: string; nameAr: string; color: string } {
    if (value < 0) return { name: 'non-vegetation', nameAr: 'غير نباتي', color: '#1565C0' };
    if (value < 0.2) return { name: 'bare-soil', nameAr: 'تربة جرداء', color: '#8D6E63' };
    if (value < 0.4) return { name: 'stressed', nameAr: 'إجهاد', color: '#FF5722' };
    if (value < 0.6) return { name: 'moderate', nameAr: 'متوسط', color: '#FFEB3B' };
    if (value < 0.8) return { name: 'healthy', nameAr: 'صحي', color: '#8BC34A' };
    return { name: 'very-healthy', nameAr: 'ممتاز', color: '#2E7D32' };
}

function calculateHealthScore(ndviValue: number): number {
    // Convert NDVI (-1 to 1) to health score (0 to 1)
    // Focus on vegetation range (0.2 to 0.8)
    if (ndviValue < 0.2) return 0;
    if (ndviValue > 0.8) return 1;
    return (ndviValue - 0.2) / 0.6;
}

// ─────────────────────────────────────────────────────────────────────────────
// Error Handler
// ─────────────────────────────────────────────────────────────────────────────

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
    console.error("Unhandled error:", err);
    res.status(500).json({
        success: false,
        error: "Internal server error"
    });
});

// ─────────────────────────────────────────────────────────────────────────────
// Start Server
// ─────────────────────────────────────────────────────────────────────────────

AppDataSource.initialize()
    .then(async () => {
        console.log("═══════════════════════════════════════════════════════════");
        console.log("  🔥 Database Connected & PostGIS Engine Ready!");
        console.log("═══════════════════════════════════════════════════════════");

        // Enable PostGIS extension if not exists
        try {
            await AppDataSource.query("CREATE EXTENSION IF NOT EXISTS postgis");
            console.log("  ✅ PostGIS extension enabled");
        } catch (e) {
            console.log("  ⚠️  PostGIS extension may already exist");
        }

        app.listen(PORT, "0.0.0.0", () => {
            console.log(`  🚀 Field Core Service running on port ${PORT}`);
            console.log("═══════════════════════════════════════════════════════════");
            console.log("");
            console.log("  📡 Available endpoints:");
            console.log("    GET  /healthz              - Health check");
            console.log("    GET  /readyz               - Readiness check");
            console.log("    GET  /api/v1/fields        - List fields");
            console.log("    GET  /api/v1/fields/:id    - Get field (+ ETag)");
            console.log("    POST /api/v1/fields        - Create field (+ ETag)");
            console.log("    PUT  /api/v1/fields/:id    - Update field (If-Match → 409)");
            console.log("    DELETE /api/v1/fields/:id  - Delete field");
            console.log("    GET  /api/v1/fields/nearby - Geospatial query");
            console.log("");
            console.log("  🌿 NDVI Analysis:");
            console.log("    GET  /api/v1/fields/:id/ndvi  - Field NDVI analysis");
            console.log("    PUT  /api/v1/fields/:id/ndvi  - Update NDVI value");
            console.log("    GET  /api/v1/ndvi/summary     - Tenant-wide NDVI summary");
            console.log("");
            console.log("  🔐 ETag Conflict Resolution:");
            console.log("    • GET returns ETag header + body.etag");
            console.log("    • PUT with If-Match header validates version");
            console.log("    • 409 Conflict returns serverData for resolution");
            console.log("");
        });
    })
    .catch((error) => {
        console.error("❌ Database connection failed:", error);
        process.exit(1);
    });
