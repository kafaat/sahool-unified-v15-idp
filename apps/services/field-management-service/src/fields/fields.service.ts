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

/**
 * Bumped whenever the shape of a cached FieldResponseDto changes in a
 * way that a subtle consumer (e.g. the `findById` short-circuit)
 * depends on. Previously we probed ``'bbox' in cached`` as a
 * schema-version marker, but JSON serialization drops `undefined`
 * values — so fields WITHOUT a bbox round-tripped through Redis
 * lost the marker and every read paid a DB round-trip (PR #1729
 * review). The dedicated integer is resilient to serialization.
 */
const CACHE_SCHEMA_VERSION = 2;

// Convert Prisma Decimal fields to numbers for DTO compatibility.
// Prisma returns Decimal columns as objects with a `.toNumber()` method or
// as strings (depending on configuration). The UI always expects `number`,
// so unconditionally coerce here.
function toNumber(value: any): number | undefined {
  if (value === null || value === undefined) return undefined;
  if (typeof value === "number") return value;
  if (typeof value === "object" && typeof value.toNumber === "function") {
    return value.toNumber();
  }
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

/**
 * Serialize a Field row from Prisma into a FieldResponseDto, coercing all
 * Decimal columns (areaHectares, healthScore, ndviValue) into plain numbers
 * so the UI can safely call `.toFixed()` / arithmetic on them.
 */
function serializeField(
  f: any,
  extras: {
    centroidLat?: number;
    centroidLng?: number;
    bbox?: [number, number, number, number];
  } = {},
): FieldResponseDto {
  const etag = generateETag(f.id, f.version);
  return {
    id: f.id,
    name: f.name,
    tenantId: f.tenantId,
    cropType: f.cropType,
    ownerId: f.ownerId ?? undefined,
    farmId: f.farmId ?? undefined,
    status: f.status as unknown as FieldResponseDto["status"],
    areaHectares: toNumber(f.areaHectares),
    healthScore: toNumber(f.healthScore),
    ndviValue: toNumber(f.ndviValue),
    centroidLat: extras.centroidLat,
    centroidLng: extras.centroidLng,
    bbox: extras.bbox,
    irrigationType: f.irrigationType ?? undefined,
    soilType: f.soilType ?? undefined,
    plantingDate: f.plantingDate ?? undefined,
    expectedHarvest: f.expectedHarvest ?? undefined,
    version: f.version,
    createdAt: f.createdAt,
    updatedAt: f.updatedAt,
    etag,
  };
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
        where: { id_tenantId: { id: dto.farmId, tenantId: dto.tenantId } },
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
    //
    // Centroid + bbox are computed by PostGIS at INSERT time (not in JS):
    //   * `ST_Centroid(boundary)` produces a mathematically correct
    //     centroid — the old JS code took the arithmetic mean of the ring
    //     vertices, which double-counts the closing vertex and skews the
    //     point for non-convex polygons.
    //   * The bounding box is always derivable from `boundary` via
    //     `ST_Envelope(boundary)`, so we do not introduce a separate
    //     denormalised `bbox` column — reading is cheap and avoids
    //     drift between the two representations.
    let boundary: any = dto.boundary;
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

      // Write PostGIS boundary, centroid, and area atomically.
      // The centroid is derived in-database from the boundary so it can
      // never drift out of sync with the polygon it describes.
      if (boundary) {
        await tx.$executeRaw`
          UPDATE fields
          SET
            boundary = ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(boundary)}), 4326),
            centroid = ST_Centroid(
              ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(boundary)}), 4326)
            ),
            area_hectares = ST_Area(
              ST_Transform(
                ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(boundary)}), 4326),
                32637
              )
            ) / 10000
          WHERE id = ${created.id}::uuid
        `;
      }

      return created;
    });

    // Fetch updated field (tenant is the same one we just wrote).
    const createdField = await this.findById(field.id, dto.tenantId);

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
   * Find field by ID with mandatory tenant isolation.
   *
   * SECURITY (PR #1724 review / 2026-04-21):
   * Previously took an OPTIONAL ``tenantId`` and silently fell back
   * to ``findUnique({ where: { id } })`` when the caller passed
   * ``undefined`` / ``""``. A controller forwarding an unsanitized
   * header value (``req.headers["x-tenant-id"]``) could therefore
   * resolve any field by UUID across tenants — a cross-tenant IDOR.
   *
   * ``tenantId`` is now REQUIRED and must be a non-empty, non-
   * whitespace string; every DB lookup uses the composite
   * ``@@unique([id, tenantId])`` key ``id_tenantId``. No un-scoped
   * path remains.
   *
   * Cache isolation (PR #1729 review, pullrequestreview-4150593669):
   * The cache key itself is tenant-scoped — ``CACHE_KEYS.FIELD(
   * tenantId, id)`` produces ``field:{tenantId}:{id}`` — so tenant
   * A can never read tenant B's cached entry regardless of what
   * arrives in the object body. That closes the enumeration oracle
   * (cache HIT 403 vs DB MISS 404) by construction: cross-tenant
   * reads miss the cache, fall through to the composite-key DB
   * query, and surface a uniform ``NotFoundException``.
   *
   * @param id       - Field UUID
   * @param tenantId - Caller's verified tenant; must be a
   *                   non-empty, non-whitespace string. Throws
   *                   ``BadRequestException`` otherwise.
   */
  async findById(id: string, tenantId: string): Promise<FieldResponseDto> {
    // Treat whitespace-only tenantIds as empty — a controller that
    // forwards `req.headers["x-tenant-id"]?.trim() ?? ""` might emit
    // `" "` for a malformed header value, which the previous
    // `!tenantId` guard accepted as truthy.
    if (!tenantId || typeof tenantId !== "string" || tenantId.trim() === "") {
      // Bilingual envelope to match the `create()` flow above (farmId
      // check) and the service's general error-response convention
      // (PR #1729 review, comment on pullrequestreview-4150593669).
      throw new BadRequestException({
        message:
          "tenantId is required — no un-scoped field lookup path exists",
        messageAr:
          "معرّف المستأجر (tenantId) مطلوب — لا يوجد مسار بحث عن الحقل غير مقيّد بالمستأجر",
      });
    }

    // Try cache first. Key is tenant-scoped, so a HIT is guaranteed
    // to belong to the caller's tenant.
    const cached = await this.cacheService.get<
      FieldResponseDto & { _cacheSchemaVersion?: number }
    >(CACHE_KEYS.FIELD(tenantId, id));
    // Schema-version marker: `_cacheSchemaVersion` is set on every
    // write (see CACHE_SCHEMA_VERSION above). An older entry without
    // it is ignored so clients pick up the new shape on next read.
    // The previous `'bbox' in cached` probe was unreliable because
    // JSON serialization drops keys whose value is `undefined`, so
    // entries for fields with no bbox would lose the marker on round-
    // trip and never hit the cache (PR #1729 review).
    if (cached && cached._cacheSchemaVersion === CACHE_SCHEMA_VERSION) {
      // Strip the internal marker before returning so callers never
      // observe `_cacheSchemaVersion` on cached reads when the DB
      // path would not include it — prevents a subtle response-
      // shape inconsistency (PR #1729 review, comment 1 on
      // pullrequestreview-4150593669).
      const { _cacheSchemaVersion: _ignored, ...publicShape } = cached;
      void _ignored;
      return publicShape;
    }

    const field = await this.prisma.field.findUnique({
      where: { id_tenantId: { id, tenantId } },
      select: {
        id: true,
        name: true,
        tenantId: true,
        cropType: true,
        ownerId: true,
        farmId: true,
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
      // Composite-key miss covers both "no such id" AND
      // "row exists but belongs to a different tenant" — both
      // indistinguishable to the caller (no enumeration oracle).
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Fetch centroid + bbox from PostGIS (neither is representable via the
    // Prisma select above). Both are derived in-database from the stored
    // boundary, so they can never drift out of sync with the polygon:
    //   centroid = ST_Centroid(boundary)
    //   bbox     = ST_Envelope(boundary)'s min/max lat/lng
    // The query uses a single row-trip so we don't pay two round-trips.
    let centroidLat: number | undefined;
    let centroidLng: number | undefined;
    let bbox: [number, number, number, number] | undefined;
    try {
      const geomRows = await this.prisma.$queryRawUnsafe<
        Array<{
          centroid_lng: number | null;
          centroid_lat: number | null;
          min_lng: number | null;
          min_lat: number | null;
          max_lng: number | null;
          max_lat: number | null;
        }>
      >(
        `SELECT
           ST_X(centroid::geometry) AS centroid_lng,
           ST_Y(centroid::geometry) AS centroid_lat,
           ST_XMin(boundary::geometry) AS min_lng,
           ST_YMin(boundary::geometry) AS min_lat,
           ST_XMax(boundary::geometry) AS max_lng,
           ST_YMax(boundary::geometry) AS max_lat
         FROM fields
         WHERE id = $1::uuid
           AND boundary IS NOT NULL`,
        id,
      );
      if (geomRows.length > 0) {
        const row = geomRows[0];
        if (row.centroid_lat != null && row.centroid_lng != null) {
          centroidLat = Number(row.centroid_lat);
          centroidLng = Number(row.centroid_lng);
        }
        if (
          row.min_lng != null &&
          row.min_lat != null &&
          row.max_lng != null &&
          row.max_lat != null
        ) {
          bbox = [
            Number(row.min_lng),
            Number(row.min_lat),
            Number(row.max_lng),
            Number(row.max_lat),
          ];
        }
      }
    } catch {
      // centroid / boundary columns may not exist on older DB schemas — ignore
    }

    const result: FieldResponseDto = serializeField(field, {
      centroidLat,
      centroidLng,
      bbox,
    });

    // Cache the result under a tenant-scoped key. The
    // `_cacheSchemaVersion` marker survives JSON round-tripping
    // (unlike `undefined`-valued keys such as `bbox`), so the
    // short-circuit in `findById` detects this as a current-
    // schema entry regardless of whether the field has a PostGIS
    // boundary populated. The marker is stripped from the
    // response on the cache-hit path.
    await this.cacheService.set(
      CACHE_KEYS.FIELD(tenantId, id),
      { ...result, _cacheSchemaVersion: CACHE_SCHEMA_VERSION },
      CACHE_TTL.MEDIUM,
    );

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
          ownerId: true,
          farmId: true,
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

    // Fetch centroid + bbox for the page in a single batch query. Both are
    // derived in-database from `boundary` so they never drift out of sync
    // with the polygon. This is a single round-trip regardless of page
    // size — avoids N+1 that a per-row lookup would incur.
    const geomByFieldId = new Map<
      string,
      {
        centroidLat?: number;
        centroidLng?: number;
        bbox?: [number, number, number, number];
      }
    >();
    if (fields.length > 0) {
      try {
        const ids = fields.map((f: { id: string }) => f.id);
        const geomRows = await this.prisma.$queryRawUnsafe<
          Array<{
            id: string;
            centroid_lng: number | null;
            centroid_lat: number | null;
            min_lng: number | null;
            min_lat: number | null;
            max_lng: number | null;
            max_lat: number | null;
          }>
        >(
          `SELECT
             id,
             ST_X(centroid::geometry) AS centroid_lng,
             ST_Y(centroid::geometry) AS centroid_lat,
             ST_XMin(boundary::geometry) AS min_lng,
             ST_YMin(boundary::geometry) AS min_lat,
             ST_XMax(boundary::geometry) AS max_lng,
             ST_YMax(boundary::geometry) AS max_lat
           FROM fields
           WHERE id = ANY($1::uuid[])
             AND boundary IS NOT NULL`,
          ids,
        );
        for (const row of geomRows) {
          const entry: {
            centroidLat?: number;
            centroidLng?: number;
            bbox?: [number, number, number, number];
          } = {};
          if (row.centroid_lat != null && row.centroid_lng != null) {
            entry.centroidLat = Number(row.centroid_lat);
            entry.centroidLng = Number(row.centroid_lng);
          }
          if (
            row.min_lng != null &&
            row.min_lat != null &&
            row.max_lng != null &&
            row.max_lat != null
          ) {
            entry.bbox = [
              Number(row.min_lng),
              Number(row.min_lat),
              Number(row.max_lng),
              Number(row.max_lat),
            ];
          }
          geomByFieldId.set(row.id, entry);
        }
      } catch {
        // centroid / boundary columns may not exist on older DB schemas — ignore
      }
    }

    const totalPages = Math.ceil(total / limit);

    const data: FieldResponseDto[] = fields.map((f: any) => {
      const geom = geomByFieldId.get(f.id);
      return serializeField(f, {
        centroidLat: geom?.centroidLat,
        centroidLng: geom?.centroidLng,
        bbox: geom?.bbox,
      });
    });

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
      where: { id_tenantId: { id, tenantId } },
      select: { id: true, version: true, tenantId: true },
    });

    if (!current) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(current.tenantId, tenantId, "field");

    // Validate If-Match version: DTO `ifMatch` (number) takes precedence
    // over the HTTP `If-Match` header (etag string). Either mechanism yields
    // a 409 Conflict on mismatch so concurrent edits never silently overwrite.
    if (dto.ifMatch !== undefined && dto.ifMatch !== null) {
      if (Number(dto.ifMatch) !== current.version) {
        throw new ConflictException({
          message: "Field was modified by another user",
          messageAr: "تم تعديل الحقل بواسطة مستخدم آخر",
          currentVersion: current.version,
          providedVersion: Number(dto.ifMatch),
          error: "version_conflict",
        });
      }
    } else if (ifMatch) {
      const expectedETag = generateETag(current.id, current.version);
      if (ifMatch !== expectedETag && ifMatch !== `"${current.id}-v${current.version}"`) {
        throw new ConflictException({
          message: "Field was modified by another user",
          messageAr: "تم تعديل الحقل بواسطة مستخدم آخر",
          currentVersion: current.version,
          currentETag: expectedETag,
          error: "version_conflict",
        });
      }
    }

    // Update field and boundary atomically
    await this.prisma.$transaction(async (tx) => {
      await tx.field.update({
        where: { id_tenantId: { id, tenantId }, version: current.version },
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

      // Handle boundary update within the same transaction. The centroid
      // is recomputed from the new boundary — previously this was missed
      // and the stored centroid would go stale after any boundary edit.
      if (dto.boundary) {
        await tx.$executeRaw`
          UPDATE fields
          SET
            boundary = ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(dto.boundary)}), 4326),
            centroid = ST_Centroid(
              ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(dto.boundary)}), 4326)
            ),
            area_hectares = ST_Area(
              ST_Transform(
                ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(dto.boundary)}), 4326),
                32637
              )
            ) / 10000
          WHERE id = ${id}::uuid
        `;
      }
    });

    // Invalidate caches
    await this.cacheService.invalidateField(id, current.tenantId);

    const result = await this.findById(id, tenantId);

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
      where: { id_tenantId: { id, tenantId } },
      select: { tenantId: true },
    });

    if (!field) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(field.tenantId, tenantId, "field");

    await this.prisma.field.update({
      where: { id_tenantId: { id, tenantId } },
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
      area_hectares: toNumber(f.area_hectares),
      health_score: toNumber(f.health_score),
      distance_meters: toNumber(f.distance_meters),
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
      where: { id_tenantId: { id, tenantId } },
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

      // Update boundary with PostGIS. The centroid is recomputed from the
      // new geometry so it stays consistent with the boundary after every
      // edit (without this the stored centroid would silently go stale).
      await tx.$executeRaw`
        UPDATE fields
        SET
          boundary = ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(newBoundary)}), 4326),
          centroid = ST_Centroid(
            ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(newBoundary)}), 4326)
          ),
          area_hectares = ST_Area(
            ST_Transform(
              ST_SetSRID(ST_GeomFromGeoJSON(${JSON.stringify(newBoundary)}), 4326),
              32637
            )
          ) / 10000,
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

    return this.findById(id, tenantId) as Promise<FieldResponseDto & { etag: string }>;
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
      // Defense-in-depth: historyIds are already tenant-filtered by the
      // findMany above (where: { fieldId, tenantId }), so the IN clause
      // only contains rows belonging to the authenticated tenant.
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
        where: { id_tenantId: { id, tenantId } },
        select: { id: true, version: true, tenantId: true },
      }),
      this.prisma.fieldBoundaryHistory.findUnique({
        where: { id_tenantId: { id: dto.historyId, tenantId } },
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

      // Restore previous boundary. The centroid is recomputed from the
      // restored geometry so rollback keeps centroid consistent with
      // boundary (previously rollback left a stale centroid behind).
      // Defense-in-depth: tenant_id added to both UPDATE and subquery WHERE
      // clauses, even though field ownership and history entry are validated above.
      await tx.$executeRaw`
        UPDATE fields
        SET
          boundary = (
            SELECT previous_boundary
            FROM field_boundary_history
            WHERE id = ${dto.historyId}::uuid
              AND tenant_id = ${field.tenantId}::uuid
          ),
          centroid = ST_Centroid(
            (SELECT previous_boundary FROM field_boundary_history
             WHERE id = ${dto.historyId}::uuid
               AND tenant_id = ${field.tenantId}::uuid)
          ),
          area_hectares = ST_Area(ST_Transform(
            (SELECT previous_boundary FROM field_boundary_history WHERE id = ${dto.historyId}::uuid AND tenant_id = ${field.tenantId}::uuid),
            32637
          )) / 10000,
          version = version + 1,
          server_updated_at = NOW()
        WHERE id = ${id}::uuid
          AND tenant_id = ${field.tenantId}::uuid
      `;
    });

    // Invalidate caches
    await this.cacheService.invalidateField(id, field.tenantId);

    return this.findById(id, field.tenantId) as Promise<FieldResponseDto & { etag: string }>;
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

    const raw = stats[0] || {};
    // Coerce Decimal/bigint counts to plain numbers so the UI can render them
    const result = {
      total_fields: toNumber(raw.total_fields) ?? 0,
      active_fields: toNumber(raw.active_fields) ?? 0,
      fallow_fields: toNumber(raw.fallow_fields) ?? 0,
      harvested_fields: toNumber(raw.harvested_fields) ?? 0,
      total_area: toNumber(raw.total_area) ?? 0,
      average_health: toNumber(raw.average_health),
      average_ndvi: toNumber(raw.average_ndvi),
      crop_types: toNumber(raw.crop_types) ?? 0,
    };
    await this.cacheService.set(cacheKey, result, CACHE_TTL.MEDIUM);

    return result;
  }
}
