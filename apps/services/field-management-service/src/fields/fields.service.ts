/**
 * Fields Service - Core Field Operations
 *
 * Features:
 * - CRUD operations with optimistic locking
 * - PostGIS geospatial queries
 * - Boundary history tracking
 * - Redis caching integration
 */

import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
  Logger,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CacheService, CACHE_KEYS, CACHE_TTL } from "../cache/cache.service";
import { FieldEventsService } from "../events/field-events.service";
import {
  CreateFieldDto,
  UpdateFieldDto,
  QueryFieldsDto,
  NearbyFieldsDto,
  UpdateBoundaryDto,
  RollbackBoundaryDto,
  FieldResponseDto,
  PaginatedFieldsResponseDto,
} from "./dto/field.dto";
import { assertTenantOwnership } from "../auth/tenant.utils";
import { v4 as uuidv4 } from "uuid";

// ETag generation
function generateETag(id: string, version: number): string {
  return `"${id}-v${version}"`;
}

// Convert Prisma Decimal fields to numbers for DTO compatibility
function toNumber(value: any): number | undefined {
  if (value === null || value === undefined) return undefined;
  return typeof value === "number" ? value : Number(value);
}

// Polygon area calculation (approximate, in hectares)
function calculatePolygonArea(coordinates: number[][]): number {
  if (coordinates.length < 3) return 0;

  let area = 0;
  const n = coordinates.length;

  for (let i = 0; i < n - 1; i++) {
    const [x1, y1] = coordinates[i];
    const [x2, y2] = coordinates[i + 1];
    area += x1 * y2 - x2 * y1;
  }

  // Earth's radius at equator in km
  const R = 6371;
  // Convert degrees to radians and calculate approximate area
  const avgLat = coordinates.reduce((sum, c) => sum + c[1], 0) / n;
  const cosLat = Math.cos((avgLat * Math.PI) / 180);

  // Convert to hectares (1 km² = 100 hectares)
  const areaKm2 = Math.abs(area / 2) * ((Math.PI * R) / 180) ** 2 * cosLat;
  return areaKm2 * 100;
}

@Injectable()
export class FieldsService {
  private readonly logger = new Logger(FieldsService.name);

  constructor(
    private prisma: PrismaService,
    private cacheService: CacheService,
    private fieldEvents: FieldEventsService,
  ) {}

  /**
   * Create a new field
   */
  async create(dto: CreateFieldDto): Promise<FieldResponseDto & { etag: string }> {
    // Validate farmId belongs to the same tenant (prevent cross-tenant reference)
    if (dto.farmId) {
      const farm = await this.prisma.farm.findUnique({
        where: { id: dto.farmId },
        select: { tenantId: true },
      });
      if (!farm) {
        throw new BadRequestException({
          message: "Farm not found",
          messageAr: "المزرعة غير موجودة",
        });
      }
      assertTenantOwnership(farm.tenantId, dto.tenantId, "farm");
    }

    // Prepare boundary if coordinates provided
    let boundary: any = dto.boundary;
    let centroid: any = null;
    let approximateArea: number | null = null;

    if (dto.coordinates && dto.coordinates.length >= 3) {
      // Ensure polygon is closed
      const coords = [...dto.coordinates];
      if (
        JSON.stringify(coords[0]) !== JSON.stringify(coords[coords.length - 1])
      ) {
        coords.push(coords[0]);
      }

      boundary = {
        type: "Polygon",
        coordinates: [coords],
      };

      // Calculate centroid
      const centroidLng = coords.reduce((sum, c) => sum + c[0], 0) / coords.length;
      const centroidLat = coords.reduce((sum, c) => sum + c[1], 0) / coords.length;

      centroid = {
        type: "Point",
        coordinates: [centroidLng, centroidLat],
      };

      approximateArea = calculatePolygonArea(coords);
    }

    // Create field and update PostGIS boundary atomically
    const field = await this.prisma.$transaction(async (tx) => {
      const created = await tx.field.create({
        data: {
          name: dto.name,
          tenantId: dto.tenantId,
          cropType: dto.cropType,
          ownerId: dto.ownerId,
          farmId: dto.farmId,
          irrigationType: dto.irrigationType,
          soilType: dto.soilType,
          plantingDate: dto.plantingDate ? new Date(dto.plantingDate) : null,
          expectedHarvest: dto.expectedHarvest ? new Date(dto.expectedHarvest) : null,
          metadata: dto.metadata,
          status: "active",
          areaHectares: approximateArea,
        },
      });

      // Update with PostGIS boundary if exists
      if (boundary) {
        await tx.$executeRaw`
          UPDATE fields
          SET
            boundary = ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(boundary)}), 4326),
            centroid = ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(centroid)}), 4326),
            area_hectares = ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(boundary)}), 4326), 32637)) / 10000
          WHERE id = ${created.id}::uuid
        `;
      }

      return created;
    });

    // Fetch updated field
    const createdField = await this.findById(field.id);

    // Invalidate related caches
    await this.cacheService.invalidateTenant(dto.tenantId);

    // Publish field created event (non-blocking)
    this.fieldEvents.publishFieldCreated(dto.tenantId, createdField.id, {
      name: dto.name,
      cropType: dto.cropType,
      areaHectares: createdField.areaHectares,
      ownerId: dto.ownerId,
    }).catch((e) => this.logger.error(`Event publish failed: ${e}`));

    const etag = generateETag(createdField.id, createdField.version);

    return { ...createdField, etag };
  }

  /**
   * Find field by ID with tenant isolation
   *
   * @param id - Field UUID
   * @param tenantId - If provided, enforces tenant ownership check
   */
  async findById(id: string, tenantId?: string): Promise<FieldResponseDto> {
    // Try cache first
    const cached = await this.cacheService.get<FieldResponseDto>(
      CACHE_KEYS.FIELD(id),
    );
    if (cached) {
      // Verify tenant ownership even for cached results
      if (tenantId) {
        assertTenantOwnership(cached.tenantId, tenantId, "field");
      }
      return cached;
    }

    const field = await this.prisma.field.findUnique({
      where: { id },
      select: {
        id: true,
        name: true,
        tenantId: true,
        cropType: true,
        status: true,
        areaHectares: true,
        healthScore: true,
        ndviValue: true,
        irrigationType: true,
        soilType: true,
        plantingDate: true,
        expectedHarvest: true,
        metadata: true,
        version: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    if (!field) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation: prevent cross-tenant data access
    if (tenantId) {
      assertTenantOwnership(field.tenantId, tenantId, "field");
    }

    const etag = generateETag(field.id, field.version);
    const result: FieldResponseDto = {
      id: field.id,
      name: field.name,
      tenantId: field.tenantId,
      cropType: field.cropType,
      status: field.status as unknown as FieldResponseDto["status"],
      areaHectares: toNumber(field.areaHectares),
      healthScore: toNumber(field.healthScore),
      ndviValue: toNumber(field.ndviValue),
      irrigationType: field.irrigationType ?? undefined,
      soilType: field.soilType ?? undefined,
      plantingDate: field.plantingDate ?? undefined,
      expectedHarvest: field.expectedHarvest ?? undefined,
      version: field.version,
      createdAt: field.createdAt,
      updatedAt: field.updatedAt,
      etag,
    };

    // Cache the result
    await this.cacheService.set(CACHE_KEYS.FIELD(id), result, CACHE_TTL.MEDIUM);

    return result;
  }

  /**
   * Find all fields with pagination and filtering
   */
  async findAll(query: QueryFieldsDto): Promise<PaginatedFieldsResponseDto> {
    const page = query.page || 1;
    const limit = Math.min(query.limit || 20, 100);
    const skip = (page - 1) * limit;

    // Build where clause - tenantId is always required for isolation
    const where: any = { tenantId: query.tenantId };
    if (query.status) where.status = query.status;
    if (query.cropType) where.cropType = query.cropType;

    // Execute queries in parallel
    const [fields, total] = await Promise.all([
      this.prisma.field.findMany({
        where,
        select: {
          id: true,
          name: true,
          tenantId: true,
          cropType: true,
          status: true,
          areaHectares: true,
          healthScore: true,
          ndviValue: true,
          irrigationType: true,
          soilType: true,
          plantingDate: true,
          expectedHarvest: true,
          version: true,
          createdAt: true,
          updatedAt: true,
        },
        skip,
        take: limit,
        orderBy: { createdAt: "desc" },
      }),
      this.prisma.field.count({ where }),
    ]);

    const totalPages = Math.ceil(total / limit);

    const data: FieldResponseDto[] = fields.map((f: any) => ({
      id: f.id,
      name: f.name,
      tenantId: f.tenantId,
      cropType: f.cropType,
      status: f.status as unknown as FieldResponseDto["status"],
      areaHectares: toNumber(f.areaHectares),
      healthScore: toNumber(f.healthScore),
      ndviValue: toNumber(f.ndviValue),
      irrigationType: f.irrigationType ?? undefined,
      soilType: f.soilType ?? undefined,
      plantingDate: f.plantingDate ?? undefined,
      expectedHarvest: f.expectedHarvest ?? undefined,
      version: f.version,
      createdAt: f.createdAt,
      updatedAt: f.updatedAt,
      etag: generateETag(f.id, f.version),
    }));

    return {
      data,
      meta: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1,
      },
    };
  }

  /**
   * Update field with optimistic locking and tenant isolation
   */
  async update(
    id: string,
    dto: UpdateFieldDto,
    tenantId: string,
    ifMatch?: string,
  ): Promise<FieldResponseDto & { etag: string }> {
    // Get current field
    const current = await this.prisma.field.findUnique({
      where: { id },
      select: { id: true, version: true, tenantId: true },
    });

    if (!current) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(current.tenantId, tenantId, "field");

    // Validate ETag if provided
    if (ifMatch) {
      const expectedETag = generateETag(current.id, current.version);
      if (ifMatch !== expectedETag && ifMatch !== `"${current.id}-v${current.version}"`) {
        throw new ConflictException({
          message: "Field was modified by another user",
          messageAr: "تم تعديل الحقل بواسطة مستخدم آخر",
          currentVersion: current.version,
          currentETag: expectedETag,
        });
      }
    }

    // Update field and boundary atomically
    await this.prisma.$transaction(async (tx) => {
      await tx.field.update({
        where: { id, version: current.version },
        data: {
          ...(dto.name && { name: dto.name }),
          ...(dto.cropType && { cropType: dto.cropType }),
          ...(dto.status && { status: dto.status }),
          ...(dto.irrigationType && { irrigationType: dto.irrigationType }),
          ...(dto.soilType && { soilType: dto.soilType }),
          ...(dto.plantingDate && { plantingDate: new Date(dto.plantingDate) }),
          ...(dto.expectedHarvest && { expectedHarvest: new Date(dto.expectedHarvest) }),
          ...(dto.metadata && { metadata: dto.metadata }),
          version: { increment: 1 },
          serverUpdatedAt: new Date(),
        },
      });

      // Handle boundary update within the same transaction
      if (dto.boundary) {
        await tx.$executeRaw`
          UPDATE fields
          SET
            boundary = ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(dto.boundary)}), 4326),
            area_hectares = ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(dto.boundary)}), 4326), 32637)) / 10000
          WHERE id = ${id}::uuid
        `;
      }
    });

    // Invalidate caches
    await this.cacheService.invalidateField(id, current.tenantId);

    const result = await this.findById(id);

    // Publish field updated event (non-blocking)
    this.fieldEvents.publishFieldUpdated(tenantId, id, {
      changes: dto,
    }).catch((e) => this.logger.error(`Event publish failed: ${e}`));

    const etag = generateETag(result.id, result.version);

    return { ...result, etag };
  }

  /**
   * Delete field (soft delete) with tenant isolation
   */
  async delete(id: string, tenantId: string): Promise<void> {
    const field = await this.prisma.field.findUnique({
      where: { id },
      select: { tenantId: true },
    });

    if (!field) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(field.tenantId, tenantId, "field");

    await this.prisma.field.update({
      where: { id },
      data: { isDeleted: true, status: "inactive" },
    });

    // Invalidate caches
    await this.cacheService.invalidateField(id, field.tenantId);

    // Publish field deleted event (non-blocking)
    this.fieldEvents.publishFieldDeleted(tenantId, id)
      .catch((e) => this.logger.error(`Event publish failed: ${e}`));
  }

  /**
   * Find nearby fields using PostGIS
   */
  async findNearby(query: NearbyFieldsDto): Promise<any[]> {
    const { tenantId, lat, lng, radius } = query;

    const fields = await this.prisma.$queryRaw<any[]>`
      SELECT
        id, name, crop_type, status, area_hectares, health_score,
        ST_AsGeoJSON(boundary) as boundary,
        ST_AsGeoJSON(centroid) as centroid,
        ST_Distance(
          centroid::geography,
          ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326)::geography
        ) as distance_meters
      FROM fields
      WHERE tenant_id = ${tenantId}
        AND is_deleted = false
        AND ST_DWithin(
          centroid::geography,
          ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326)::geography,
          ${radius}
        )
      ORDER BY distance_meters ASC
      LIMIT 50
    `;

    return fields.map((f) => ({
      ...f,
      boundary: f.boundary ? JSON.parse(f.boundary) : null,
      centroid: f.centroid ? JSON.parse(f.centroid) : null,
    }));
  }

  /**
   * Update field boundary with history tracking and tenant isolation
   */
  async updateBoundary(
    id: string,
    dto: UpdateBoundaryDto,
    tenantId: string,
  ): Promise<FieldResponseDto & { etag: string }> {
    const field = await this.prisma.field.findUnique({
      where: { id },
      select: { id: true, version: true, tenantId: true },
    });

    if (!field) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(field.tenantId, tenantId, "field");

    // Ensure polygon is closed
    const coords = [...dto.coordinates];
    if (
      JSON.stringify(coords[0]) !== JSON.stringify(coords[coords.length - 1])
    ) {
      coords.push(coords[0]);
    }

    const newBoundary = {
      type: "Polygon",
      coordinates: [coords],
    };

    // Create history entry and update boundary in transaction
    await this.prisma.$transaction(async (tx) => {
      // Get current boundary for history
      const currentBoundary = await tx.$queryRaw<any[]>`
        SELECT ST_AsGeoJSON(boundary) as boundary FROM fields WHERE id = ${id}::uuid
      `;

      // Create history entry
      await tx.fieldBoundaryHistory.create({
        data: {
          tenantId: field.tenantId,
          fieldId: id,
          versionAtChange: field.version,
          changedBy: dto.userId,
          changeReason: dto.reason,
          changeSource: dto.deviceId ? "mobile" : "api",
          deviceId: dto.deviceId,
        },
      });

      // Update boundary with PostGIS
      await tx.$executeRaw`
        UPDATE fields
        SET
          boundary = ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(newBoundary)}), 4326),
          area_hectares = ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(newBoundary)}), 4326), 32637)) / 10000,
          version = version + 1,
          server_updated_at = NOW()
        WHERE id = ${id}::uuid
      `;
    });

    // Invalidate caches
    await this.cacheService.invalidateField(id, field.tenantId);

    // Publish boundary changed event (non-blocking)
    this.fieldEvents.publishBoundaryChanged(tenantId, id, {
      reason: dto.reason,
      changeSource: dto.deviceId ? 'mobile' : 'api',
    }).catch((e) => this.logger.error(`Event publish failed: ${e}`));

    return this.findById(id) as Promise<FieldResponseDto & { etag: string }>;
  }

  /**
   * Get boundary history for a field with tenant isolation
   */
  async getBoundaryHistory(id: string, tenantId: string, limit: number = 20): Promise<any[]> {
    const history = await this.prisma.fieldBoundaryHistory.findMany({
      where: { fieldId: id, tenantId },
      orderBy: { createdAt: "desc" },
      take: limit,
      select: {
        id: true,
        fieldId: true,
        versionAtChange: true,
        areaChangeHectares: true,
        changedBy: true,
        changeReason: true,
        changeSource: true,
        deviceId: true,
        createdAt: true,
      },
    });

    // Fetch GeoJSON for boundaries
    if (history.length > 0) {
      const historyIds = history.map((h: any) => h.id);
      const geoJsonResults = await this.prisma.$queryRaw<any[]>`
        SELECT
          id,
          ST_AsGeoJSON(previous_boundary) as previous_boundary_geojson,
          ST_AsGeoJSON(new_boundary) as new_boundary_geojson
        FROM field_boundary_history
        WHERE id = ANY(${historyIds}::uuid[])
      `;

      const geoJsonMap = new Map(
        geoJsonResults.map((r) => [r.id, r]),
      );

      return history.map((entry: any) => {
        const geoJson = geoJsonMap.get(entry.id);
        return {
          ...entry,
          previousBoundary: geoJson?.previous_boundary_geojson
            ? JSON.parse(geoJson.previous_boundary_geojson)
            : null,
          newBoundary: geoJson?.new_boundary_geojson
            ? JSON.parse(geoJson.new_boundary_geojson)
            : null,
        };
      });
    }

    return history;
  }

  /**
   * Rollback boundary to a previous version with tenant isolation
   */
  async rollbackBoundary(
    id: string,
    dto: RollbackBoundaryDto,
    tenantId: string,
  ): Promise<FieldResponseDto & { etag: string }> {
    const [field, historyEntry] = await Promise.all([
      this.prisma.field.findUnique({
        where: { id },
        select: { id: true, version: true, tenantId: true },
      }),
      this.prisma.fieldBoundaryHistory.findUnique({
        where: { id: dto.historyId },
      }),
    ]);

    if (!field) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(field.tenantId, tenantId, "field");

    if (!historyEntry || historyEntry.fieldId !== id) {
      throw new NotFoundException("History entry not found - سجل التاريخ غير موجود");
    }

    // Perform rollback in transaction
    await this.prisma.$transaction(async (tx) => {
      // Create history entry for the rollback
      await tx.fieldBoundaryHistory.create({
        data: {
          tenantId: field.tenantId,
          fieldId: id,
          versionAtChange: field.version,
          changedBy: dto.userId,
          changeReason: dto.reason || `Rollback to version ${historyEntry.versionAtChange}`,
          changeSource: "api",
        },
      });

      // Restore previous boundary
      await tx.$executeRaw`
        UPDATE fields
        SET
          boundary = (
            SELECT previous_boundary
            FROM field_boundary_history
            WHERE id = ${dto.historyId}::uuid
          ),
          area_hectares = ST_Area(ST_Transform(
            (SELECT previous_boundary FROM field_boundary_history WHERE id = ${dto.historyId}::uuid),
            32637
          )) / 10000,
          version = version + 1,
          server_updated_at = NOW()
        WHERE id = ${id}::uuid
      `;
    });

    // Invalidate caches
    await this.cacheService.invalidateField(id, field.tenantId);

    return this.findById(id) as Promise<FieldResponseDto & { etag: string }>;
  }

  /**
   * Get field statistics for a tenant
   */
  async getStats(tenantId: string): Promise<any> {
    const cacheKey = CACHE_KEYS.FIELD_STATS(tenantId);
    const cached = await this.cacheService.get<any>(cacheKey);
    if (cached) return cached;

    const stats = await this.prisma.$queryRaw<any[]>`
      SELECT
        COUNT(*) as total_fields,
        COUNT(*) FILTER (WHERE status = 'active') as active_fields,
        COUNT(*) FILTER (WHERE status = 'fallow') as fallow_fields,
        COUNT(*) FILTER (WHERE status = 'harvested') as harvested_fields,
        SUM(area_hectares) as total_area,
        AVG(health_score) as average_health,
        AVG(ndvi_value) as average_ndvi,
        COUNT(DISTINCT crop_type) as crop_types
      FROM fields
      WHERE tenant_id = ${tenantId} AND is_deleted = false
    `;

    const result = stats[0] || {};
    await this.cacheService.set(cacheKey, result, CACHE_TTL.MEDIUM);

    return result;
  }
}
