import "reflect-metadata";
import express, { Request, Response, NextFunction, Application } from "express";
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
  getIfMatchHeader,
} from "./middleware/etag";
import {
  validatePolygonCoordinates,
  validateGeoJSON,
  calculatePolygonArea,
  GeoValidationResult,
} from "./middleware/validation";
import { pestRoutes } from "./api/pest-routes";
import { geoRoutes } from "./geo/geo-routes";
import { fieldHealthRoutes } from "./api/field-health-routes";
import { taskRoutes } from "./api/task-routes";
import { Logger } from "./middleware/logger";

const logger = new Logger("field-shared", "16.0.0");

/**
 * Create and configure the field management Express application
 * @param serviceName - Name of the service (for health check and logging)
 * @returns Configured Express application
 */
export function createFieldApp(
  serviceName: string = "field-service",
): Application {
  const app = express();

  // ─────────────────────────────────────────────────────────────────────────────
  // CORS Configuration - Restrict to allowed origins
  // ─────────────────────────────────────────────────────────────────────────────

  const allowedOrigins = [
    "https://sahool.app",
    "https://admin.sahool.app",
    "https://api.sahool.app",
    "https://api.sahool.io",
    // Development origins - remove in production
    ...(process.env.NODE_ENV !== "production"
      ? [
          "http://localhost:3000",
          "http://localhost:5173",
          "http://localhost:8080",
        ]
      : []),
  ];

  const corsOptions: cors.CorsOptions = {
    origin: (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
      // Allow requests with no origin (mobile apps, curl, etc)
      if (!origin) return callback(null, true);

      if (allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        const sanitizedOrigin = origin.replace(/[\n\r\t\x1b]/g, "");
        logger.warn(`⚠️ CORS blocked request from: ${sanitizedOrigin}`);
        callback(new Error("Not allowed by CORS"));
      }
    },
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: [
      "Content-Type",
      "Authorization",
      "If-Match",
      "X-Request-ID",
      "X-Tenant-ID",
    ],
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // Middleware
  // ─────────────────────────────────────────────────────────────────────────────

  app.use(cors(corsOptions));
  app.use(express.json());

  // ETag header middleware
  app.use(setETagHeader);

  // Request logging with ETag info
  app.use((req: Request, _res: Response, next: NextFunction) => {
    const ifMatch = getIfMatchHeader(req);
    const etagInfo = ifMatch ? ` [If-Match: ${ifMatch}]` : "";
    logger.info(
      `[${new Date().toISOString()}] ${req.method} ${req.path}${etagInfo}`,
    );
    next();
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Health Check Endpoints
  // ─────────────────────────────────────────────────────────────────────────────

  app.get("/healthz", (_req: Request, res: Response) => {
    res.json({
      status: "healthy",
      service: serviceName,
      timestamp: new Date().toISOString(),
    });
  });

  app.get("/readyz", async (_req: Request, res: Response) => {
    try {
      await AppDataSource.query("SELECT 1");
      res.json({
        status: "ready",
        database: "connected",
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      res.status(503).json({
        status: "not ready",
        database: "disconnected",
        error: error instanceof Error ? error.message : "Unknown error",
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
          offset: Number(offset),
        },
      });
    } catch (error) {
      logger.error("Error fetching fields:", error);
      res.status(500).json({
        success: false,
        error: "Failed to fetch fields",
      });
    }
  });

  /**
   * GET /api/v1/fields/:id
   * Get a single field by ID
   * Returns ETag header for optimistic locking
   */
  app.get("/api/v1/fields/:id", async (req: Request, res: Response, next: NextFunction) => {
    // Skip fixed sub-paths that have their own handlers registered after this route.
    // TODO: Move /nearby, /sync, /stats routes BEFORE /:id to use Express route
    // ordering instead of this workaround. Add any new fixed sub-path here until then.
    const reservedPaths = ["nearby", "sync", "stats"];
    if (reservedPaths.includes(req.params.id)) {
      return next();
    }

    try {
      const id = Array.isArray(req.params.id)
        ? req.params.id[0]
        : req.params.id;
      const fieldRepo = AppDataSource.getRepository(Field);
      const field = await fieldRepo.findOne({
        where: { id },
      });

      if (!field) {
        return res.status(404).json({
          success: false,
          error: "Field not found",
        });
      }

      // Generate and set ETag from field ID and version
      const etag = generateETag(field.id, field.version);
      res.locals.etag = etag;

      res.json({
        success: true,
        data: field,
        etag: etag, // Also include in body for mobile clients
      });
    } catch (error) {
      logger.error("Error fetching field:", error);
      res.status(500).json({
        success: false,
        error: "Failed to fetch field",
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
        metadata,
      } = req.body;

      // Validate required fields
      if (!name || !tenantId || !cropType) {
        return res.status(400).json({
          success: false,
          error: "Missing required fields: name, tenantId, cropType",
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
        expectedHarvest: expectedHarvest
          ? new Date(expectedHarvest)
          : undefined,
        metadata,
        status: "active",
      });

      // If coordinates provided, create GeoJSON polygon with validation
      if (
        coordinates &&
        Array.isArray(coordinates) &&
        coordinates.length >= 3
      ) {
        // Ensure polygon is closed
        const closedCoords = [...coordinates];
        if (
          JSON.stringify(closedCoords[0]) !==
          JSON.stringify(closedCoords[closedCoords.length - 1])
        ) {
          closedCoords.push(closedCoords[0]);
        }

        // Validate polygon coordinates
        const validationResult: GeoValidationResult =
          validatePolygonCoordinates([closedCoords]);
        if (!validationResult.valid) {
          return res.status(400).json({
            success: false,
            error: "Invalid polygon coordinates",
            error_ar: "إحداثيات المضلع غير صالحة",
            details: validationResult.errors.map((e, i) => ({
              message: e,
              message_ar: validationResult.errors_ar[i],
            })),
            warnings: validationResult.warnings,
          });
        }

        newField.boundary = {
          type: "Polygon",
          coordinates: [closedCoords],
        };

        // Calculate centroid (simple average for now)
        const centroidLng =
          closedCoords.reduce((sum, c) => sum + c[0], 0) / closedCoords.length;
        const centroidLat =
          closedCoords.reduce((sum, c) => sum + c[1], 0) / closedCoords.length;

        newField.centroid = {
          type: "Point",
          coordinates: [centroidLng, centroidLat],
        };

        // Calculate approximate area locally
        const approxArea = calculatePolygonArea(closedCoords);
        logger.info(`📐 Approximate area: ${approxArea.toFixed(2)} hectares`);
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
              message_ar: geoValidation.errors_ar[i],
            })),
          });
        }
        newField.boundary = boundary;
      }

      const savedField = await fieldRepo.save(newField);

      // Calculate area using PostGIS if boundary exists
      if (savedField.boundary) {
        await AppDataSource.query(
          `
                    UPDATE fields
                    SET area_hectares = ST_Area(ST_Transform(boundary, 32637)) / 10000
                    WHERE id = $1
                `,
          [savedField.id],
        );
      }

      // Fetch updated field with calculated area
      const finalField = await fieldRepo.findOne({
        where: { id: savedField.id },
      });

      // Generate ETag for newly created field
      const etag = finalField
        ? generateETag(finalField.id, finalField.version)
        : null;
      if (etag) {
        res.locals.etag = etag;
      }

      res.status(201).json({
        success: true,
        data: finalField,
        etag: etag,
        message: "حقل جديد تم إنشاؤه بنجاح", // New field created successfully
      });
    } catch (error) {
      logger.error("Error creating field:", error);
      res.status(500).json({
        success: false,
        error: "Failed to create field",
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
      const id = Array.isArray(req.params.id)
        ? req.params.id[0]
        : req.params.id;
      const fieldRepo = AppDataSource.getRepository(Field);
      const field = await fieldRepo.findOne({
        where: { id },
      });

      if (!field) {
        return res.status(404).json({
          success: false,
          error: "Field not found",
        });
      }

      // Validate If-Match header for optimistic locking
      const ifMatch = getIfMatchHeader(req);
      if (ifMatch && !validateIfMatch(ifMatch, field.id, field.version)) {
        // 409 Conflict - the field was modified by another user
        const currentETag = generateETag(field.id, field.version);
        logger.info(
          `⚠️ 409 Conflict: Field ${field.id} - Client ETag: ${ifMatch}, Server ETag: ${currentETag}`,
        );

        return res
          .status(409)
          .json(createConflictResponse(field, currentETag, "field"));
      }

      // Update allowed fields using explicit property assignment
      // to prevent prototype pollution attacks
      const updates = req.body;
      if (updates.name !== undefined) field.name = updates.name;
      if (updates.cropType !== undefined) field.cropType = updates.cropType;
      if (updates.status !== undefined) field.status = updates.status;
      if (updates.irrigationType !== undefined)
        field.irrigationType = updates.irrigationType;
      if (updates.soilType !== undefined) field.soilType = updates.soilType;
      if (updates.plantingDate !== undefined)
        field.plantingDate = updates.plantingDate;
      if (updates.expectedHarvest !== undefined)
        field.expectedHarvest = updates.expectedHarvest;
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
        message: "تم تحديث الحقل بنجاح", // Field updated successfully
      });
    } catch (error) {
      logger.error("Error updating field:", error);
      res.status(500).json({
        success: false,
        error: "Failed to update field",
      });
    }
  });

  /**
   * DELETE /api/v1/fields/:id
   * Delete a field
   */
  app.delete("/api/v1/fields/:id", async (req: Request, res: Response) => {
    try {
      const id = Array.isArray(req.params.id)
        ? req.params.id[0]
        : req.params.id;
      const fieldRepo = AppDataSource.getRepository(Field);
      const result = await fieldRepo.delete(id);

      if (result.affected === 0) {
        return res.status(404).json({
          success: false,
          error: "Field not found",
        });
      }

      res.json({
        success: true,
        message: "تم حذف الحقل بنجاح", // Field deleted successfully
      });
    } catch (error) {
      logger.error("Error deleting field:", error);
      res.status(500).json({
        success: false,
        error: "Failed to delete field",
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
          error: "Missing required parameters: lat, lng",
        });
      }

      const fields = await AppDataSource.query(
        `
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
            `,
        [
          parseFloat(lng as string),
          parseFloat(lat as string),
          parseInt(radius as string),
        ],
      );

      res.json({
        success: true,
        data: fields.map((f: any) => ({
          ...f,
          boundary: f.boundary ? JSON.parse(f.boundary) : null,
          centroid: f.centroid ? JSON.parse(f.centroid) : null,
        })),
        query: { lat, lng, radius },
      });
    } catch (error) {
      logger.error("Error finding nearby fields:", error);
      res.status(500).json({
        success: false,
        error: "Failed to find nearby fields",
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
      const id = Array.isArray(req.params.id)
        ? req.params.id[0]
        : req.params.id;
      const fieldRepo = AppDataSource.getRepository(Field);
      const field = await fieldRepo.findOne({
        where: { id },
      });

      if (!field) {
        return res.status(404).json({
          success: false,
          error: "Field not found",
        });
      }

      // Generate mock NDVI history (in production, this would come from satellite data)
      const history = generateMockNdviHistory(30);
      const current = history[history.length - 1].value;
      const values = history.map((h) => h.value);
      const average = values.reduce((a, b) => a + b, 0) / values.length;
      const min = Math.min(...values);
      const max = Math.max(...values);

      // Calculate trend
      const firstHalf = values.slice(0, Math.floor(values.length / 2));
      const secondHalf = values.slice(Math.floor(values.length / 2));
      const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
      const secondAvg =
        secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
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
            date: new Date().toISOString(),
          },
          statistics: {
            average: Math.round(average * 100) / 100,
            min: Math.round(min * 100) / 100,
            max: Math.round(max * 100) / 100,
            trend: Math.round(trend * 100) / 100,
            trendDirection:
              trend > 0.05
                ? "improving"
                : trend < -0.05
                  ? "declining"
                  : "stable",
          },
          history: history,
          lastUpdated: new Date().toISOString(),
        },
      });
    } catch (error) {
      logger.error("Error fetching NDVI data:", error);
      res.status(500).json({
        success: false,
        error: "Failed to fetch NDVI data",
      });
    }
  });

  /**
   * PUT /api/v1/fields/:id/ndvi
   * Update NDVI value for a field (from external source)
   */
  app.put("/api/v1/fields/:id/ndvi", async (req: Request, res: Response) => {
    try {
      const id = Array.isArray(req.params.id)
        ? req.params.id[0]
        : req.params.id;
      const fieldRepo = AppDataSource.getRepository(Field);
      const { value, source } = req.body;

      if (typeof value !== "number" || value < -1 || value > 1) {
        return res.status(400).json({
          success: false,
          error: "NDVI value must be between -1 and 1",
        });
      }

      const field = await fieldRepo.findOne({
        where: { id },
      });

      if (!field) {
        return res.status(404).json({
          success: false,
          error: "Field not found",
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
          source: source || "manual",
          updatedAt: new Date().toISOString(),
        },
        etag: etag,
        message: "تم تحديث مؤشر NDVI بنجاح",
      });
    } catch (error) {
      logger.error("Error updating NDVI:", error);
      res.status(500).json({
        success: false,
        error: "Failed to update NDVI",
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
          error: "Missing required parameter: tenantId",
        });
      }

      const result = await AppDataSource.query(
        `
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
            `,
        [tenantId],
      );

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
            critical: parseInt(summary.critical_count) || 0,
          },
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      logger.error("Error fetching NDVI summary:", error);
      res.status(500).json({
        success: false,
        error: "Failed to fetch NDVI summary",
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
        date: date.toISOString().split("T")[0],
        value: Math.round(value * 100) / 100,
        cloudCover: Math.round(Math.random() * 30),
      });
    }

    return history;
  }

  function getNdviCategory(value: number): {
    name: string;
    nameAr: string;
    color: string;
  } {
    if (value < 0)
      return { name: "non-vegetation", nameAr: "غير نباتي", color: "#1565C0" };
    if (value < 0.2)
      return { name: "bare-soil", nameAr: "تربة جرداء", color: "#8D6E63" };
    if (value < 0.4)
      return { name: "stressed", nameAr: "إجهاد", color: "#FF5722" };
    if (value < 0.6)
      return { name: "moderate", nameAr: "متوسط", color: "#FFEB3B" };
    if (value < 0.8)
      return { name: "healthy", nameAr: "صحي", color: "#8BC34A" };
    return { name: "very-healthy", nameAr: "ممتاز", color: "#2E7D32" };
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
      const {
        tenantId,
        since,
        includeDeleted = "false",
        limit = 100,
      } = req.query;

      if (!tenantId) {
        return res.status(400).json({
          success: false,
          error: "Missing required parameter: tenantId",
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
            error: "Invalid 'since' timestamp format. Use ISO 8601.",
          });
        }
        queryBuilder.andWhere("field.updatedAt > :since", { since: sinceDate });
      }

      // Filter by status if not including deleted
      if (includeDeleted !== "true") {
        queryBuilder.andWhere("field.status != :deleted", {
          deleted: "deleted",
        });
      }

      const fields = await queryBuilder
        .orderBy("field.updatedAt", "ASC")
        .take(Number(limit))
        .getMany();

      // Calculate sync metadata
      const hasMore = fields.length === Number(limit);
      const lastUpdated =
        fields.length > 0 ? fields[fields.length - 1].updatedAt : null;

      // Transform fields with server_version for mobile sync
      const syncData = fields.map((field: any) => ({
        ...field,
        server_version: field.version,
        etag: generateETag(field.id, field.version),
        _syncMeta: {
          serverTime: new Date().toISOString(),
          action: field.status === "deleted" ? "delete" : "upsert",
        },
      }));

      res.json({
        success: true,
        data: syncData,
        sync: {
          serverTime: new Date().toISOString(),
          lastUpdated: lastUpdated?.toISOString() || null,
          count: fields.length,
          hasMore,
          nextSince: lastUpdated?.toISOString() || since,
        },
      });
    } catch (error) {
      logger.error("Error in delta sync:", error);
      res.status(500).json({
        success: false,
        error: "Failed to perform delta sync",
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
          error:
            "Missing required fields: deviceId, userId, tenantId, fields[]",
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
              status: fieldData.status || "active",
            } as Partial<Field>);

            // Handle boundary
            if (fieldData.coordinates && Array.isArray(fieldData.coordinates)) {
              const closedCoords = [...fieldData.coordinates];
              if (
                JSON.stringify(closedCoords[0]) !==
                JSON.stringify(closedCoords[closedCoords.length - 1])
              ) {
                closedCoords.push(closedCoords[0]);
              }
              (newField as Field).boundary = {
                type: "Polygon",
                coordinates: [closedCoords],
              } as any;
            }

            const saved = await fieldRepo.save(newField as Field);

            results.push({
              clientId: id || "new",
              serverId: saved.id,
              status: "created",
              server_version: saved.version,
              etag: generateETag(saved.id, saved.version),
            });
            continue;
          }

          // Update existing field
          const existingField = await fieldRepo.findOne({ where: { id } });

          if (!existingField) {
            results.push({
              clientId: id,
              status: "error",
              error: "Field not found",
            });
            continue;
          }

          // Version conflict check
          if (
            client_version !== undefined &&
            client_version < existingField.version
          ) {
            results.push({
              clientId: id,
              serverId: id,
              status: "conflict",
              server_version: existingField.version,
              etag: generateETag(existingField.id, existingField.version),
              serverData: existingField,
            });
            continue;
          }

          // Track boundary change if applicable
          const boundaryChanged =
            fieldData.boundary &&
            JSON.stringify(fieldData.boundary) !==
              JSON.stringify(existingField.boundary);

          if (boundaryChanged) {
            const historyEntry = historyRepo.create({
              fieldId: id,
              versionAtChange: existingField.version,
              previousBoundary: existingField.boundary,
              newBoundary: fieldData.boundary,
              changedBy: userId,
              changeSource: "mobile",
              deviceId,
            });
            await historyRepo.save(historyEntry);
          }

          // Apply updates using explicit property assignment
          // to prevent prototype pollution attacks
          if (fieldData.name !== undefined) existingField.name = fieldData.name;
          if (fieldData.cropType !== undefined)
            existingField.cropType = fieldData.cropType;
          if (fieldData.status !== undefined)
            existingField.status = fieldData.status;
          if (fieldData.irrigationType !== undefined)
            existingField.irrigationType = fieldData.irrigationType;
          if (fieldData.soilType !== undefined)
            existingField.soilType = fieldData.soilType;
          if (fieldData.plantingDate !== undefined)
            existingField.plantingDate = fieldData.plantingDate;
          if (fieldData.expectedHarvest !== undefined)
            existingField.expectedHarvest = fieldData.expectedHarvest;
          if (fieldData.metadata !== undefined)
            existingField.metadata = fieldData.metadata;
          if (fieldData.boundary !== undefined)
            existingField.boundary = fieldData.boundary;

          const updated = await fieldRepo.save(existingField);

          results.push({
            clientId: id,
            serverId: updated.id,
            status: "updated",
            server_version: updated.version,
            etag: generateETag(updated.id, updated.version),
          });
        } catch (fieldError) {
          results.push({
            clientId: clientField.id || "unknown",
            status: "error",
            error:
              fieldError instanceof Error
                ? fieldError.message
                : "Unknown error",
          });
        }
      }

      // Update sync status for device
      const syncStatusRepo = AppDataSource.getRepository(SyncStatus);
      let syncStatus = await syncStatusRepo.findOne({
        where: { deviceId, userId, tenantId },
      });

      if (!syncStatus) {
        syncStatus = syncStatusRepo.create({ deviceId, userId, tenantId });
      }

      syncStatus.lastSyncAt = new Date();
      syncStatus.status = results.some((r) => r.status === "conflict")
        ? "conflict"
        : "idle";
      syncStatus.conflictsCount = results.filter(
        (r) => r.status === "conflict",
      ).length;
      await syncStatusRepo.save(syncStatus);

      const successCount = results.filter(
        (r) => r.status === "created" || r.status === "updated",
      ).length;
      const conflictCount = results.filter(
        (r) => r.status === "conflict",
      ).length;
      const errorCount = results.filter((r) => r.status === "error").length;

      res.json({
        success: true,
        results,
        summary: {
          total: results.length,
          created: results.filter((r) => r.status === "created").length,
          updated: results.filter((r) => r.status === "updated").length,
          conflicts: conflictCount,
          errors: errorCount,
          successRate: `${Math.round((successCount / results.length) * 100)}%`,
        },
        serverTime: new Date().toISOString(),
      });
    } catch (error) {
      logger.error("Error in batch sync:", error);
      res.status(500).json({
        success: false,
        error: "Failed to perform batch sync",
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
          error: "Missing required parameters: deviceId, tenantId",
        });
      }

      const syncStatusRepo = AppDataSource.getRepository(SyncStatus);
      const syncStatus = await syncStatusRepo.findOne({
        where: {
          deviceId: deviceId as string,
          tenantId: tenantId as string,
          ...(userId ? { userId: userId as string } : {}),
        },
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
            conflictsCount: 0,
          },
        });
      }

      // Calculate pending downloads (fields modified since last sync)
      const fieldRepo = AppDataSource.getRepository(Field);
      let pendingDownloads = 0;

      if (syncStatus.lastSyncAt) {
        pendingDownloads = await fieldRepo
          .createQueryBuilder("field")
          .where("field.tenantId = :tenantId", { tenantId })
          .andWhere("field.updatedAt > :lastSync", {
            lastSync: syncStatus.lastSyncAt,
          })
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
          pendingDownloads,
        },
      });
    } catch (error) {
      logger.error("Error fetching sync status:", error);
      res.status(500).json({
        success: false,
        error: "Failed to fetch sync status",
      });
    }
  });

  /**
   * PUT /api/v1/sync/status
   * Update sync status for a device (called by mobile on sync completion)
   */
  app.put("/api/v1/sync/status", async (req: Request, res: Response) => {
    try {
      const {
        deviceId,
        userId,
        tenantId,
        lastSyncVersion,
        deviceInfo,
        status,
      } = req.body;

      if (!deviceId || !userId || !tenantId) {
        return res.status(400).json({
          success: false,
          error: "Missing required fields: deviceId, userId, tenantId",
        });
      }

      const syncStatusRepo = AppDataSource.getRepository(SyncStatus);
      let syncStatus = await syncStatusRepo.findOne({
        where: { deviceId, userId, tenantId },
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
        message: "تم تحديث حالة المزامنة بنجاح",
      });
    } catch (error) {
      logger.error("Error updating sync status:", error);
      res.status(500).json({
        success: false,
        error: "Failed to update sync status",
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
  app.get(
    "/api/v1/fields/:id/boundary-history",
    async (req: Request, res: Response) => {
      try {
        const id = Array.isArray(req.params.id)
          ? req.params.id[0]
          : req.params.id;
        const { limit = 20 } = req.query;

        const historyRepo = AppDataSource.getRepository(FieldBoundaryHistory);
        const history = await historyRepo.find({
          where: { fieldId: id },
          order: { createdAt: "DESC" },
          take: Number(limit),
        });

        // Batch fetch all GeoJSON data in a single query to avoid N+1
        const historyIds = history.map((h: any) => h.id);
        const geoJsonResults =
          historyIds.length > 0
            ? await AppDataSource.query(
                `
                SELECT
                    id,
                    ST_AsGeoJSON(previous_boundary) as previous_boundary_geojson,
                    ST_AsGeoJSON(new_boundary) as new_boundary_geojson
                FROM field_boundary_history
                WHERE id = ANY($1)
            `,
                [historyIds],
              )
            : [];

        // Create a map for quick lookup
        const geoJsonMap = new Map(
          geoJsonResults.map((result: any) => [result.id, result]),
        );

        // Convert geometries to GeoJSON for response
        const historyWithGeoJson = history.map((entry: any) => {
          const geoJsonResult: any = geoJsonMap.get(entry.id);

          return {
            id: entry.id,
            fieldId: entry.fieldId,
            versionAtChange: entry.versionAtChange,
            previousBoundary: geoJsonResult?.previous_boundary_geojson
              ? JSON.parse(geoJsonResult.previous_boundary_geojson)
              : null,
            newBoundary: geoJsonResult?.new_boundary_geojson
              ? JSON.parse(geoJsonResult.new_boundary_geojson)
              : null,
            areaChangeHectares: entry.areaChangeHectares,
            changedBy: entry.changedBy,
            changeReason: entry.changeReason,
            changeSource: entry.changeSource,
            deviceId: entry.deviceId,
            createdAt: entry.createdAt,
          };
        });

        res.json({
          success: true,
          data: historyWithGeoJson,
          count: history.length,
        });
      } catch (error) {
        logger.error("Error fetching boundary history:", error);
        res.status(500).json({
          success: false,
          error: "Failed to fetch boundary history",
        });
      }
    },
  );

  /**
   * POST /api/v1/fields/:id/boundary-history/rollback
   * Rollback field boundary to a previous version
   */
  app.post(
    "/api/v1/fields/:id/boundary-history/rollback",
    async (req: Request, res: Response) => {
      try {
        const id = Array.isArray(req.params.id)
          ? req.params.id[0]
          : req.params.id;
        const { historyId, userId, reason } = req.body;

        if (!historyId) {
          return res.status(400).json({
            success: false,
            error: "Missing required field: historyId",
          });
        }

        const fieldRepo = AppDataSource.getRepository(Field);
        const historyRepo = AppDataSource.getRepository(FieldBoundaryHistory);

        const field = await fieldRepo.findOne({ where: { id } });
        if (!field) {
          return res.status(404).json({
            success: false,
            error: "Field not found",
          });
        }

        const historyEntry = await historyRepo.findOne({
          where: { id: historyId, fieldId: id },
        });
        if (!historyEntry) {
          return res.status(404).json({
            success: false,
            error: "History entry not found",
          });
        }

        // Create new history entry for the rollback
        const rollbackHistory = historyRepo.create({
          fieldId: id,
          versionAtChange: field.version,
          previousBoundary: field.boundary,
          newBoundary: historyEntry.previousBoundary,
          changedBy: userId,
          changeReason:
            reason || `Rollback to version ${historyEntry.versionAtChange}`,
          changeSource: "api",
        });
        await historyRepo.save(rollbackHistory);

        // Apply the rollback
        field.boundary = historyEntry.previousBoundary;
        const updated = await fieldRepo.save(field);

        // Recalculate area
        if (updated.boundary) {
          await AppDataSource.query(
            `
                    UPDATE fields
                    SET area_hectares = ST_Area(ST_Transform(boundary, 32637)) / 10000
                    WHERE id = $1
                `,
            [updated.id],
          );
        }

        const finalField = await fieldRepo.findOne({ where: { id } });

        res.json({
          success: true,
          data: finalField,
          etag: generateETag(finalField!.id, finalField!.version),
          message: "تم استرجاع الحدود السابقة بنجاح",
        });
      } catch (error) {
        logger.error("Error rolling back boundary:", error);
        res.status(500).json({
          success: false,
          error: "Failed to rollback boundary",
        });
      }
    },
  );

  // ─────────────────────────────────────────────────────────────────────────────
  // Pest Management API Routes
  // ─────────────────────────────────────────────────────────────────────────────

  app.use("/api/v1/pests", pestRoutes);

  // ─────────────────────────────────────────────────────────────────────────────
  // Geospatial API Routes (PostGIS)
  // ─────────────────────────────────────────────────────────────────────────────

  app.use("/api/v1/geo", geoRoutes);

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Health API Routes (migrated from field-ops)
  // ─────────────────────────────────────────────────────────────────────────────

  app.use("/api/v1", fieldHealthRoutes);

  // ─────────────────────────────────────────────────────────────────────────────
  // Task and Operations API Routes (migrated from field-ops)
  // ─────────────────────────────────────────────────────────────────────────────

  app.use("/api/v1", taskRoutes);

  // ─────────────────────────────────────────────────────────────────────────────
  // Error Handler
  // ─────────────────────────────────────────────────────────────────────────────

  app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
    logger.error("Unhandled error:", err);
    res.status(500).json({
      success: false,
      error: "Internal server error",
    });
  });

  return app;
}

/**
 * Initialize database and start field service
 * @param serviceName - Name of the service
 * @param port - Port number to listen on
 */
export async function startFieldService(
  serviceName: string,
  port: number = 3000,
): Promise<void> {
  const app = createFieldApp(serviceName);

  // Allow skipping database initialization for container smoke tests
  const skipDbInit = process.env.SKIP_DB_INIT === "true" ||
                     process.env.ENVIRONMENT === "test";

  let dbConnected = false;

  if (!skipDbInit) {
    try {
      await AppDataSource.initialize();
      dbConnected = true;
      logger.info("═══════════════════════════════════════════════════════════");
      logger.info("  🔥 Database Connected & PostGIS Engine Ready!");
      logger.info("═══════════════════════════════════════════════════════════");

      // Enable PostGIS extension if not exists
      try {
        await AppDataSource.query("CREATE EXTENSION IF NOT EXISTS postgis");
        logger.info("  ✅ PostGIS extension enabled");
      } catch (e) {
        logger.info("  ⚠️  PostGIS extension may already exist");
      }
    } catch (dbError) {
      logger.warn("═══════════════════════════════════════════════════════════");
      logger.warn("  ⚠️  Database connection failed - running in limited mode");
      logger.warn(`  Error: ${dbError instanceof Error ? dbError.message : String(dbError)}`);
      logger.warn("═══════════════════════════════════════════════════════════");
    }
  } else {
    logger.info("═══════════════════════════════════════════════════════════");
    logger.info("  ⚠️  SKIP_DB_INIT=true - Database initialization skipped");
    logger.info("═══════════════════════════════════════════════════════════");
  }

  app.listen(port, "0.0.0.0", () => {
    logger.info(`  🚀 ${serviceName} running on port ${port}`);
    logger.info("═══════════════════════════════════════════════════════════");
    logger.info("");
    logger.info("  📡 Field CRUD Endpoints:");
    logger.info("    GET  /healthz              - Health check");
    logger.info("    GET  /readyz               - Readiness check");
    logger.info("    GET  /api/v1/fields        - List fields");
    logger.info("    GET  /api/v1/fields/:id    - Get field (+ ETag)");
    logger.info("    POST /api/v1/fields        - Create field (+ ETag)");
    logger.info(
      "    PUT  /api/v1/fields/:id    - Update field (If-Match → 409)",
    );
    logger.info("    DELETE /api/v1/fields/:id  - Delete field");
    logger.info("    GET  /api/v1/fields/nearby - Geospatial query");
    logger.info("");
    logger.info("  📱 Mobile Sync (Delta Sync):");
    logger.info(
      "    GET  /api/v1/fields/sync          - Delta sync (since=timestamp)",
    );
    logger.info(
      "    POST /api/v1/fields/sync/batch    - Batch upload with conflict check",
    );
    logger.info("    GET  /api/v1/sync/status          - Device sync status");
    logger.info("    PUT  /api/v1/sync/status          - Update sync status");
    logger.info("");
    logger.info("  📜 Boundary History:");
    logger.info("    GET  /api/v1/fields/:id/boundary-history  - Get history");
    logger.info(
      "    POST /api/v1/fields/:id/boundary-history/rollback - Rollback",
    );
    logger.info("");
    logger.info("  🌿 NDVI Analysis:");
    logger.info("    GET  /api/v1/fields/:id/ndvi  - Field NDVI analysis");
    logger.info("    PUT  /api/v1/fields/:id/ndvi  - Update NDVI value");
    logger.info("    GET  /api/v1/ndvi/summary     - Tenant-wide NDVI summary");
    logger.info("");
    logger.info("  🐛 Pest Management:");
    logger.info(
      "    GET    /api/v1/pests/incidents           - List pest incidents",
    );
    logger.info(
      "    POST   /api/v1/pests/incidents           - Report pest incident",
    );
    logger.info(
      "    GET    /api/v1/pests/incidents/:id       - Get incident details",
    );
    logger.info(
      "    PUT    /api/v1/pests/incidents/:id       - Update incident",
    );
    logger.info(
      "    PATCH  /api/v1/pests/incidents/:id/status - Update status",
    );
    logger.info(
      "    DELETE /api/v1/pests/incidents/:id       - Delete incident",
    );
    logger.info(
      "    GET    /api/v1/pests/treatments          - List treatments",
    );
    logger.info(
      "    POST   /api/v1/pests/treatments          - Record treatment",
    );
    logger.info(
      "    GET    /api/v1/pests/treatments/:id      - Get treatment details",
    );
    logger.info(
      "    PUT    /api/v1/pests/treatments/:id      - Update treatment",
    );
    logger.info(
      "    DELETE /api/v1/pests/treatments/:id      - Delete treatment",
    );
    logger.info("");
    logger.info("  🌍 Geospatial (PostGIS):");
    logger.info(
      "    GET  /api/v1/geo/fields/radius          - Find fields in radius",
    );
    logger.info(
      "    GET  /api/v1/geo/farms/nearby           - Find nearby farms",
    );
    logger.info(
      "    GET  /api/v1/geo/fields/:id/area        - Calculate field area",
    );
    logger.info(
      "    POST /api/v1/geo/fields/:id/contains-point - Check point in field",
    );
    logger.info(
      "    GET  /api/v1/geo/fields/bbox            - Find fields in bbox",
    );
    logger.info(
      "    GET  /api/v1/geo/fields/:id1/distance/:id2 - Distance between fields",
    );
    logger.info(
      "    GET  /api/v1/geo/region/stats           - Regional statistics",
    );
    logger.info(
      "    GET  /api/v1/geo/fields/:id/geojson     - Get field GeoJSON",
    );
    logger.info(
      "    GET  /api/v1/geo/farms/:id/geojson      - Get farm GeoJSON",
    );
    logger.info(
      "    GET  /api/v1/geo/farms/:id/fields       - Get farm's fields",
    );
    logger.info(
      "    POST /api/v1/geo/fields                 - Create field with boundary",
    );
    logger.info(
      "    PUT  /api/v1/geo/fields/:id/boundary    - Update field boundary",
    );
    logger.info(
      "    POST /api/v1/geo/farms                  - Create farm with location",
    );
    logger.info("");
    logger.info("  🏥 Field Health Analysis (migrated from field-ops):");
    logger.info(
      "    POST /api/v1/field-health               - Comprehensive health analysis",
    );
    logger.info("");
    logger.info("  📋 Operations & Tasks (migrated from field-ops):");
    logger.info(
      "    GET  /api/v1/operations                 - List operations",
    );
    logger.info(
      "    POST /api/v1/operations                 - Create operation",
    );
    logger.info("    GET  /api/v1/operations/:id             - Get operation");
    logger.info(
      "    PATCH /api/v1/operations/:id            - Update operation",
    );
    logger.info("    POST /api/v1/operations/:id/complete    - Mark complete");
    logger.info(
      "    DELETE /api/v1/operations/:id           - Delete operation",
    );
    logger.info(
      "    GET  /api/v1/stats/tenant/:id           - Tenant statistics",
    );
    logger.info("");
    logger.info("  🔐 Conflict Resolution:");
    logger.info("    • GET returns ETag header + body.etag + server_version");
    logger.info("    • PUT with If-Match header validates version");
    logger.info("    • 409 Conflict returns serverData + server_version");
    logger.info("");
  });
}
