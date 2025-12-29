import "reflect-metadata";
import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import { AppDataSource } from "./data-source";
import { Field } from "./entity/Field";
import { FieldBoundaryHistory } from "./entity/FieldBoundaryHistory";
import { SyncStatus } from "./entity/SyncStatus";
import {
    generateETag,
    validateIfMatch,
    createConflictResponse,
    setETagHeader,
    getIfMatchHeader
} from "./middleware/etag";
import {
    validatePolygonCoordinates,
    validateGeoJSON,
    calculatePolygonArea,
    GeoValidationResult
} from "./middleware/validation";
import { createRateLimiter } from "../../shared/middleware/rateLimiter";
import {
    securityHeaders,
    removeSensitiveHeaders,
    createSecureCorsOptions
} from "../../shared/middleware-ts";

const app = express();
const PORT = parseInt(process.env.PORT || "3000");

// ─────────────────────────────────────────────────────────────────────────────
// Security Middleware
// ─────────────────────────────────────────────────────────────────────────────

// Remove sensitive headers that expose server information
app.use(removeSensitiveHeaders);

// ─────────────────────────────────────────────────────────────────────────────
// CORS Configuration - Strict origin validation with production security
// ─────────────────────────────────────────────────────────────────────────────

// Use secure CORS configuration from shared middleware
// In production: Rejects requests without Origin header
// In development: Allows localhost and testing tools
// Environment variable ALLOWED_ORIGINS can override default origins
const corsOptions = createSecureCorsOptions({
    // Reject requests without Origin header in production for enhanced security
    // Set to true only if you need to support server-to-server API calls
    allowNoOrigin: false,

    // Additional custom origins beyond the defaults (if needed)
    additionalOrigins: [],

    // Allowed HTTP methods
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],

    // Custom headers specific to this service
    allowedHeaders: [
        'Content-Type',
        'Authorization',
        'If-Match',
        'If-None-Match',
        'X-Request-ID',
        'X-Tenant-ID',
        'X-User-ID',
        'X-Device-ID'
    ]
});

app.use(cors(corsOptions));

// Add comprehensive security headers (CSP, HSTS, X-Frame-Options, etc.)
app.use(securityHeaders);

// ─────────────────────────────────────────────────────────────────────────────
// Standard Middleware
// ─────────────────────────────────────────────────────────────────────────────

app.use(express.json());

// Rate limiting middleware (Redis-backed distributed rate limiting)
app.use(createRateLimiter({
    redis: {
        url: process.env.REDIS_URL || 'redis://localhost:6379'
    },
    skipPaths: ['/healthz', '/readyz']
}));

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

        // If coordinates provided, create GeoJSON polygon with validation
        if (coordinates && Array.isArray(coordinates) && coordinates.length >= 3) {
            // Ensure polygon is closed
            const closedCoords = [...coordinates];
            if (JSON.stringify(closedCoords[0]) !== JSON.stringify(closedCoords[closedCoords.length - 1])) {
                closedCoords.push(closedCoords[0]);
            }

            // Validate polygon coordinates
            const validationResult: GeoValidationResult = validatePolygonCoordinates([closedCoords]);
            if (!validationResult.valid) {
                return res.status(400).json({
                    success: false,
                    error: "Invalid polygon coordinates",
                    error_ar: "إحداثيات المضلع غير صالحة",
                    details: validationResult.errors.map((e, i) => ({
                        message: e,
                        message_ar: validationResult.errors_ar[i]
                    })),
                    warnings: validationResult.warnings
                });
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

            // Calculate approximate area locally
            const approxArea = calculatePolygonArea(closedCoords);
            console.log(`📐 Approximate area: ${approxArea.toFixed(2)} hectares`);
        }

        // If boundary provided as GeoJSON, validate it
        const { boundary } = req.body;
        if (boundary && typeof boundary === "object") {
            const geoValidation = validateGeoJSON(boundary);
            if (!geoValidation.valid) {
                return res.status(400).json({
                    success: false,
                    error: "Invalid GeoJSON boundary",
                    error_ar: "حدود GeoJSON غير صالحة",
                    details: geoValidation.errors.map((e, i) => ({
                        message: e,
                        message_ar: geoValidation.errors_ar[i]
                    }))
                });
            }
            newField.boundary = boundary;
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

        // Update allowed fields using explicit property assignment
        // to prevent prototype pollution attacks
        const updates = req.body;
        if (updates.name !== undefined) field.name = updates.name;
        if (updates.cropType !== undefined) field.cropType = updates.cropType;
        if (updates.status !== undefined) field.status = updates.status;
        if (updates.irrigationType !== undefined) field.irrigationType = updates.irrigationType;
        if (updates.soilType !== undefined) field.soilType = updates.soilType;
        if (updates.plantingDate !== undefined) field.plantingDate = updates.plantingDate;
        if (updates.expectedHarvest !== undefined) field.expectedHarvest = updates.expectedHarvest;
        if (updates.metadata !== undefined) field.metadata = updates.metadata;

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
// Mobile Sync Endpoints (Delta Sync)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * GET /api/v1/fields/sync
 * Delta Sync endpoint for mobile clients
 *
 * Query params:
 *   - tenantId: Required tenant ID
 *   - since: ISO timestamp - returns fields modified after this time
 *   - includeDeleted: Include soft-deleted fields (default: false)
 *   - limit: Max results (default: 100)
 *
 * Returns fields with server_version for conflict resolution
 */
app.get("/api/v1/fields/sync", async (req: Request, res: Response) => {
    try {
        const { tenantId, since, includeDeleted = "false", limit = 100 } = req.query;

        if (!tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameter: tenantId"
            });
        }

        const fieldRepo = AppDataSource.getRepository(Field);
        const queryBuilder = fieldRepo.createQueryBuilder("field");

        queryBuilder.where("field.tenantId = :tenantId", { tenantId });

        // Delta sync - only fields modified after 'since' timestamp
        if (since) {
            const sinceDate = new Date(since as string);
            if (isNaN(sinceDate.getTime())) {
                return res.status(400).json({
                    success: false,
                    error: "Invalid 'since' timestamp format. Use ISO 8601."
                });
            }
            queryBuilder.andWhere("field.updatedAt > :since", { since: sinceDate });
        }

        // Filter by status if not including deleted
        if (includeDeleted !== "true") {
            queryBuilder.andWhere("field.status != :deleted", { deleted: "deleted" });
        }

        const fields = await queryBuilder
            .orderBy("field.updatedAt", "ASC")
            .take(Number(limit))
            .getMany();

        // Calculate sync metadata
        const hasMore = fields.length === Number(limit);
        const lastUpdated = fields.length > 0
            ? fields[fields.length - 1].updatedAt
            : null;

        // Transform fields with server_version for mobile sync
        const syncData = fields.map(field => ({
            ...field,
            server_version: field.version,
            etag: generateETag(field.id, field.version),
            _syncMeta: {
                serverTime: new Date().toISOString(),
                action: field.status === "deleted" ? "delete" : "upsert"
            }
        }));

        res.json({
            success: true,
            data: syncData,
            sync: {
                serverTime: new Date().toISOString(),
                lastUpdated: lastUpdated?.toISOString() || null,
                count: fields.length,
                hasMore,
                nextSince: lastUpdated?.toISOString() || since
            }
        });
    } catch (error) {
        console.error("Error in delta sync:", error);
        res.status(500).json({
            success: false,
            error: "Failed to perform delta sync"
        });
    }
});

/**
 * POST /api/v1/fields/sync/batch
 * Batch sync endpoint for uploading multiple fields at once
 *
 * Body:
 *   - deviceId: Device identifier
 *   - userId: User ID
 *   - fields: Array of field objects with client_version
 *
 * Returns results for each field (success/conflict/error)
 */
app.post("/api/v1/fields/sync/batch", async (req: Request, res: Response) => {
    try {
        const { deviceId, userId, tenantId, fields: fieldsToSync } = req.body;

        if (!deviceId || !userId || !tenantId || !Array.isArray(fieldsToSync)) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: deviceId, userId, tenantId, fields[]"
            });
        }

        const fieldRepo = AppDataSource.getRepository(Field);
        const historyRepo = AppDataSource.getRepository(FieldBoundaryHistory);
        const results: Array<{
            clientId: string;
            serverId?: string;
            status: "created" | "updated" | "conflict" | "error";
            server_version?: number;
            etag?: string;
            serverData?: object;
            error?: string;
        }> = [];

        for (const clientField of fieldsToSync) {
            try {
                const { id, client_version, _isNew, ...fieldData } = clientField;

                // New field creation
                if (_isNew || !id) {
                    const newField = fieldRepo.create({
                        ...fieldData,
                        tenantId,
                        status: fieldData.status || "active"
                    } as Partial<Field>);

                    // Handle boundary
                    if (fieldData.coordinates && Array.isArray(fieldData.coordinates)) {
                        const closedCoords = [...fieldData.coordinates];
                        if (JSON.stringify(closedCoords[0]) !== JSON.stringify(closedCoords[closedCoords.length - 1])) {
                            closedCoords.push(closedCoords[0]);
                        }
                        (newField as Field).boundary = {
                            type: "Polygon",
                            coordinates: [closedCoords]
                        } as any;
                    }

                    const saved = await fieldRepo.save(newField as Field);

                    results.push({
                        clientId: id || "new",
                        serverId: saved.id,
                        status: "created",
                        server_version: saved.version,
                        etag: generateETag(saved.id, saved.version)
                    });
                    continue;
                }

                // Update existing field
                const existingField = await fieldRepo.findOne({ where: { id } });

                if (!existingField) {
                    results.push({
                        clientId: id,
                        status: "error",
                        error: "Field not found"
                    });
                    continue;
                }

                // Version conflict check
                if (client_version !== undefined && client_version < existingField.version) {
                    results.push({
                        clientId: id,
                        serverId: id,
                        status: "conflict",
                        server_version: existingField.version,
                        etag: generateETag(existingField.id, existingField.version),
                        serverData: existingField
                    });
                    continue;
                }

                // Track boundary change if applicable
                const boundaryChanged = fieldData.boundary &&
                    JSON.stringify(fieldData.boundary) !== JSON.stringify(existingField.boundary);

                if (boundaryChanged) {
                    const historyEntry = historyRepo.create({
                        fieldId: id,
                        versionAtChange: existingField.version,
                        previousBoundary: existingField.boundary,
                        newBoundary: fieldData.boundary,
                        changedBy: userId,
                        changeSource: "mobile",
                        deviceId
                    });
                    await historyRepo.save(historyEntry);
                }

                // Apply updates using explicit property assignment
                // to prevent prototype pollution attacks
                if (fieldData.name !== undefined) existingField.name = fieldData.name;
                if (fieldData.cropType !== undefined) existingField.cropType = fieldData.cropType;
                if (fieldData.status !== undefined) existingField.status = fieldData.status;
                if (fieldData.irrigationType !== undefined) existingField.irrigationType = fieldData.irrigationType;
                if (fieldData.soilType !== undefined) existingField.soilType = fieldData.soilType;
                if (fieldData.plantingDate !== undefined) existingField.plantingDate = fieldData.plantingDate;
                if (fieldData.expectedHarvest !== undefined) existingField.expectedHarvest = fieldData.expectedHarvest;
                if (fieldData.metadata !== undefined) existingField.metadata = fieldData.metadata;
                if (fieldData.boundary !== undefined) existingField.boundary = fieldData.boundary;

                const updated = await fieldRepo.save(existingField);

                results.push({
                    clientId: id,
                    serverId: updated.id,
                    status: "updated",
                    server_version: updated.version,
                    etag: generateETag(updated.id, updated.version)
                });

            } catch (fieldError) {
                results.push({
                    clientId: clientField.id || "unknown",
                    status: "error",
                    error: fieldError instanceof Error ? fieldError.message : "Unknown error"
                });
            }
        }

        // Update sync status for device
        const syncStatusRepo = AppDataSource.getRepository(SyncStatus);
        let syncStatus = await syncStatusRepo.findOne({
            where: { deviceId, userId, tenantId }
        });

        if (!syncStatus) {
            syncStatus = syncStatusRepo.create({ deviceId, userId, tenantId });
        }

        syncStatus.lastSyncAt = new Date();
        syncStatus.status = results.some(r => r.status === "conflict") ? "conflict" : "idle";
        syncStatus.conflictsCount = results.filter(r => r.status === "conflict").length;
        await syncStatusRepo.save(syncStatus);

        const successCount = results.filter(r => r.status === "created" || r.status === "updated").length;
        const conflictCount = results.filter(r => r.status === "conflict").length;
        const errorCount = results.filter(r => r.status === "error").length;

        res.json({
            success: true,
            results,
            summary: {
                total: results.length,
                created: results.filter(r => r.status === "created").length,
                updated: results.filter(r => r.status === "updated").length,
                conflicts: conflictCount,
                errors: errorCount,
                successRate: `${Math.round((successCount / results.length) * 100)}%`
            },
            serverTime: new Date().toISOString()
        });
    } catch (error) {
        console.error("Error in batch sync:", error);
        res.status(500).json({
            success: false,
            error: "Failed to perform batch sync"
        });
    }
});

/**
 * GET /api/v1/sync/status
 * Get sync status for a device
 */
app.get("/api/v1/sync/status", async (req: Request, res: Response) => {
    try {
        const { deviceId, userId, tenantId } = req.query;

        if (!deviceId || !tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameters: deviceId, tenantId"
            });
        }

        const syncStatusRepo = AppDataSource.getRepository(SyncStatus);
        const syncStatus = await syncStatusRepo.findOne({
            where: {
                deviceId: deviceId as string,
                tenantId: tenantId as string,
                ...(userId ? { userId: userId as string } : {})
            }
        });

        if (!syncStatus) {
            return res.json({
                success: true,
                data: {
                    deviceId,
                    tenantId,
                    status: "new",
                    lastSyncAt: null,
                    pendingDownloads: 0,
                    conflictsCount: 0
                }
            });
        }

        // Calculate pending downloads (fields modified since last sync)
        const fieldRepo = AppDataSource.getRepository(Field);
        let pendingDownloads = 0;

        if (syncStatus.lastSyncAt) {
            pendingDownloads = await fieldRepo
                .createQueryBuilder("field")
                .where("field.tenantId = :tenantId", { tenantId })
                .andWhere("field.updatedAt > :lastSync", { lastSync: syncStatus.lastSyncAt })
                .getCount();
        } else {
            pendingDownloads = await fieldRepo
                .createQueryBuilder("field")
                .where("field.tenantId = :tenantId", { tenantId })
                .getCount();
        }

        res.json({
            success: true,
            data: {
                ...syncStatus,
                pendingDownloads
            }
        });
    } catch (error) {
        console.error("Error fetching sync status:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch sync status"
        });
    }
});

/**
 * PUT /api/v1/sync/status
 * Update sync status for a device (called by mobile on sync completion)
 */
app.put("/api/v1/sync/status", async (req: Request, res: Response) => {
    try {
        const { deviceId, userId, tenantId, lastSyncVersion, deviceInfo, status } = req.body;

        if (!deviceId || !userId || !tenantId) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: deviceId, userId, tenantId"
            });
        }

        const syncStatusRepo = AppDataSource.getRepository(SyncStatus);
        let syncStatus = await syncStatusRepo.findOne({
            where: { deviceId, userId, tenantId }
        });

        if (!syncStatus) {
            syncStatus = syncStatusRepo.create({ deviceId, userId, tenantId });
        }

        syncStatus.lastSyncAt = new Date();
        if (lastSyncVersion) syncStatus.lastSyncVersion = lastSyncVersion;
        if (deviceInfo) syncStatus.deviceInfo = deviceInfo;
        if (status) syncStatus.status = status;

        await syncStatusRepo.save(syncStatus);

        res.json({
            success: true,
            data: syncStatus,
            message: "تم تحديث حالة المزامنة بنجاح"
        });
    } catch (error) {
        console.error("Error updating sync status:", error);
        res.status(500).json({
            success: false,
            error: "Failed to update sync status"
        });
    }
});

// ─────────────────────────────────────────────────────────────────────────────
// Field Boundary History Endpoints
// ─────────────────────────────────────────────────────────────────────────────

/**
 * GET /api/v1/fields/:id/boundary-history
 * Get boundary change history for a field
 */
app.get("/api/v1/fields/:id/boundary-history", async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const { limit = 20 } = req.query;

        // Use single query with ST_AsGeoJSON to avoid N+1
        const historyWithGeoJson = await AppDataSource.query(`
            SELECT
                id,
                field_id,
                version_at_change,
                ST_AsGeoJSON(previous_boundary) as previous_boundary_geojson,
                ST_AsGeoJSON(new_boundary) as new_boundary_geojson,
                area_change_hectares,
                changed_by,
                change_reason,
                change_source,
                device_id,
                created_at
            FROM field_boundary_history
            WHERE field_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        `, [id, Number(limit)]);

        // Parse GeoJSON strings
        const parsedHistory = historyWithGeoJson.map((entry: any) => ({
            id: entry.id,
            fieldId: entry.field_id,
            versionAtChange: entry.version_at_change,
            previousBoundary: entry.previous_boundary_geojson
                ? JSON.parse(entry.previous_boundary_geojson)
                : null,
            newBoundary: entry.new_boundary_geojson
                ? JSON.parse(entry.new_boundary_geojson)
                : null,
            areaChangeHectares: entry.area_change_hectares,
            changedBy: entry.changed_by,
            changeReason: entry.change_reason,
            changeSource: entry.change_source,
            deviceId: entry.device_id,
            createdAt: entry.created_at
        }));

        res.json({
            success: true,
            data: parsedHistory,
            count: parsedHistory.length
        });
    } catch (error) {
        console.error("Error fetching boundary history:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch boundary history"
        });
    }
});

/**
 * POST /api/v1/fields/:id/boundary-history/rollback
 * Rollback field boundary to a previous version
 */
app.post("/api/v1/fields/:id/boundary-history/rollback", async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const { historyId, userId, reason } = req.body;

        if (!historyId) {
            return res.status(400).json({
                success: false,
                error: "Missing required field: historyId"
            });
        }

        const fieldRepo = AppDataSource.getRepository(Field);
        const historyRepo = AppDataSource.getRepository(FieldBoundaryHistory);

        const field = await fieldRepo.findOne({ where: { id } });
        if (!field) {
            return res.status(404).json({
                success: false,
                error: "Field not found"
            });
        }

        const historyEntry = await historyRepo.findOne({ where: { id: historyId, fieldId: id } });
        if (!historyEntry) {
            return res.status(404).json({
                success: false,
                error: "History entry not found"
            });
        }

        // Create new history entry for the rollback
        const rollbackHistory = historyRepo.create({
            fieldId: id,
            versionAtChange: field.version,
            previousBoundary: field.boundary,
            newBoundary: historyEntry.previousBoundary,
            changedBy: userId,
            changeReason: reason || `Rollback to version ${historyEntry.versionAtChange}`,
            changeSource: "api"
        });
        await historyRepo.save(rollbackHistory);

        // Apply the rollback
        field.boundary = historyEntry.previousBoundary;
        const updated = await fieldRepo.save(field);

        // Recalculate area
        if (updated.boundary) {
            await AppDataSource.query(`
                UPDATE fields
                SET area_hectares = ST_Area(ST_Transform(boundary, 32637)) / 10000
                WHERE id = $1
            `, [updated.id]);
        }

        const finalField = await fieldRepo.findOne({ where: { id } });

        res.json({
            success: true,
            data: finalField,
            etag: generateETag(finalField!.id, finalField!.version),
            message: "تم استرجاع الحدود السابقة بنجاح"
        });
    } catch (error) {
        console.error("Error rolling back boundary:", error);
        res.status(500).json({
            success: false,
            error: "Failed to rollback boundary"
        });
    }
});

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
            console.log("  📡 Field CRUD Endpoints:");
            console.log("    GET  /healthz              - Health check");
            console.log("    GET  /readyz               - Readiness check");
            console.log("    GET  /api/v1/fields        - List fields");
            console.log("    GET  /api/v1/fields/:id    - Get field (+ ETag)");
            console.log("    POST /api/v1/fields        - Create field (+ ETag)");
            console.log("    PUT  /api/v1/fields/:id    - Update field (If-Match → 409)");
            console.log("    DELETE /api/v1/fields/:id  - Delete field");
            console.log("    GET  /api/v1/fields/nearby - Geospatial query");
            console.log("");
            console.log("  📱 Mobile Sync (Delta Sync):");
            console.log("    GET  /api/v1/fields/sync          - Delta sync (since=timestamp)");
            console.log("    POST /api/v1/fields/sync/batch    - Batch upload with conflict check");
            console.log("    GET  /api/v1/sync/status          - Device sync status");
            console.log("    PUT  /api/v1/sync/status          - Update sync status");
            console.log("");
            console.log("  📜 Boundary History:");
            console.log("    GET  /api/v1/fields/:id/boundary-history  - Get history");
            console.log("    POST /api/v1/fields/:id/boundary-history/rollback - Rollback");
            console.log("");
            console.log("  🌿 NDVI Analysis:");
            console.log("    GET  /api/v1/fields/:id/ndvi  - Field NDVI analysis");
            console.log("    PUT  /api/v1/fields/:id/ndvi  - Update NDVI value");
            console.log("    GET  /api/v1/ndvi/summary     - Tenant-wide NDVI summary");
            console.log("");
            console.log("  🔐 Conflict Resolution:");
            console.log("    • GET returns ETag header + body.etag + server_version");
            console.log("    • PUT with If-Match header validates version");
            console.log("    • 409 Conflict returns serverData + server_version");
            console.log("");
        });
    })
    .catch((error) => {
        console.error("❌ Database connection failed:", error);
        process.exit(1);
    });
