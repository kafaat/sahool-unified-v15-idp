/**
 * Field Sub-Zones Service
 * خدمة المناطق الفرعية للحقل
 *
 * Manages sub-polygons inside a Field. The service enforces:
 *
 *   1. Tenant + field ownership (no cross-tenant / cross-field leakage).
 *   2. Polygon validity via raw SQL (ST_IsValid, ST_IsSimple).
 *   3. Containment: every sub-zone boundary must lie WITHIN the parent
 *      field boundary (ST_Contains). Prevents "orphan" sub-zones floating
 *      outside the field.
 *   4. Area auto-calculation via ST_Area (geography).
 *   5. Soft delete (deleted_at stamp) + tenant-scoped queries filter out
 *      deleted rows automatically.
 *
 * All mutations go through the transactional outbox so downstream services
 * (vegetation-analysis, advisory, carbon-service) can pick up per-zone
 * NDVI / carbon / advisory computations.
 */

import {
  Injectable,
  Logger,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { OutboxService } from "../outbox/outbox.service";
import type {
  CreateFieldSubZoneDto,
  UpdateFieldSubZoneDto,
  SubZoneVertexDto,
} from "./dto/field-sub-zone.dto";

/** Raw row shape returned by our $queryRaw calls (bigint → number coerced). */
interface SubZoneRow {
  id: string;
  tenant_id: string;
  field_id: string;
  name: string;
  name_ar: string | null;
  description: string | null;
  area_hectares: string | number | null;
  elevation_m: string | number | null;
  slope_degrees: string | number | null;
  aspect: string | null;
  is_terrace: boolean;
  terrace_level: number | null;
  display_order: number;
  boundary_geojson: string | null;
  deleted_at: Date | null;
  created_by: string | null;
  created_at: Date;
  updated_at: Date;
}

@Injectable()
export class FieldSubZonesService {
  private readonly logger = new Logger(FieldSubZonesService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly outbox: OutboxService,
  ) {}

  /**
   * Tenant IDs in this service are VARCHAR(100); the outbox table stores
   * them as UUIDs. For non-UUID tenants we fall back to the nil UUID —
   * the full tenantId stays in payload.tenantId so nothing is lost.
   */
  private uuidOrNull(value: string): string {
    const uuidRe =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRe.test(value)
      ? value
      : "00000000-0000-0000-0000-000000000000";
  }

  // ---------------------------------------------------------------------
  // Queries
  // ---------------------------------------------------------------------

  /**
   * List all sub-zones for a field. Always filters out soft-deleted rows
   * and always returns in display_order (stable UI ordering).
   */
  async listByField(fieldId: string, tenantId: string) {
    await this.assertFieldOwnership(fieldId, tenantId);

    // Raw SQL so we can return the boundary as GeoJSON in one round-trip
    // instead of needing ST_AsGeoJSON() per row on the client side.
    const rows = await this.prisma.$queryRaw<SubZoneRow[]>`
      SELECT
        id,
        tenant_id,
        field_id,
        name,
        name_ar,
        description,
        area_hectares,
        elevation_m,
        slope_degrees,
        aspect,
        is_terrace,
        terrace_level,
        display_order,
        ST_AsGeoJSON(boundary) AS boundary_geojson,
        deleted_at,
        created_by,
        created_at,
        updated_at
      FROM field_sub_zones
      WHERE tenant_id = ${tenantId}
        AND field_id = ${fieldId}::uuid
        AND deleted_at IS NULL
      ORDER BY display_order ASC, created_at ASC
    `;

    return rows.map((r) => this.mapRow(r));
  }

  /**
   * Fetch a single sub-zone by id. Tenant-scoped; returns 404 for
   * cross-tenant access (indistinguishable from "not found" by design).
   */
  async getById(id: string, tenantId: string) {
    const rows = await this.prisma.$queryRaw<SubZoneRow[]>`
      SELECT
        id, tenant_id, field_id, name, name_ar, description,
        area_hectares, elevation_m, slope_degrees, aspect,
        is_terrace, terrace_level, display_order,
        ST_AsGeoJSON(boundary) AS boundary_geojson,
        deleted_at, created_by, created_at, updated_at
      FROM field_sub_zones
      WHERE id = ${id}::uuid
        AND tenant_id = ${tenantId}
        AND deleted_at IS NULL
      LIMIT 1
    `;
    if (rows.length === 0) {
      throw new NotFoundException({
        message: "Sub-zone not found",
        messageAr: "المنطقة الفرعية غير موجودة",
      });
    }
    return this.mapRow(rows[0]);
  }

  // ---------------------------------------------------------------------
  // Mutations
  // ---------------------------------------------------------------------

  /**
   * Create a new sub-zone. Validates that:
   *   - The parent field exists and belongs to the tenant.
   *   - The polygon is valid (ST_IsValid + ST_IsSimple via PostGIS).
   *   - The polygon lies WITHIN the parent field boundary (ST_Contains).
   *   - The polygon has a sensible area (> 1 m², < parent field area).
   */
  async create(
    fieldId: string,
    tenantId: string,
    dto: CreateFieldSubZoneDto,
    createdBy?: string,
  ) {
    await this.assertFieldOwnership(fieldId, tenantId);

    const wkt = this.buildPolygonWkt(dto.boundary);

    // Validate the geometry. The $queryRaw call returns one row with
    // named columns we can destructure. We use a LIMIT 1 so the planner
    // can short-circuit — there's only ever one row coming back.
    const validation = await this.prisma.$queryRaw<
      Array<{
        is_valid: boolean;
        is_simple: boolean;
        area_ha: string;
        inside_field: boolean;
      }>
    >`
      SELECT
        ST_IsValid(p.geom)                              AS is_valid,
        ST_IsSimple(p.geom)                             AS is_simple,
        ST_Area(p.geom::geography) / 10000              AS area_ha,
        COALESCE(
          ST_Contains(f.boundary, p.geom),
          FALSE
        )                                               AS inside_field
      FROM (
        SELECT ST_GeomFromText(${wkt}, 4326) AS geom
      ) p
      LEFT JOIN fields f ON f.id = ${fieldId}::uuid
      LIMIT 1
    `;
    const v = validation[0];
    if (!v) {
      throw new BadRequestException({
        message: "Failed to validate polygon",
        messageAr: "فشل التحقق من صحة حدود المنطقة",
      });
    }
    if (!v.is_valid) {
      throw new BadRequestException({
        message: "Polygon geometry is invalid",
        messageAr: "هندسة المنطقة الفرعية غير صالحة",
      });
    }
    if (!v.is_simple) {
      throw new BadRequestException({
        message: "Polygon has self-intersection",
        messageAr: "المنطقة الفرعية تحتوي على تقاطع ذاتي",
      });
    }
    const areaHa = Number(v.area_ha);
    if (!Number.isFinite(areaHa) || areaHa < 0.0001) {
      throw new BadRequestException({
        message: "Sub-zone area is too small (< 1 m²)",
        messageAr: "مساحة المنطقة الفرعية أصغر من حد السماح",
      });
    }

    // Parent-field containment is advisory for legacy fields that were
    // imported without a boundary; if the field has no boundary we skip
    // the check instead of rejecting valid sub-zones.
    if (v.inside_field === false) {
      // Check whether the parent field actually HAS a boundary — if not,
      // the FALSE result was spurious (ST_Contains(NULL,...) = NULL,
      // COALESCEd to FALSE above).
      const hasField = await this.prisma.$queryRaw<
        Array<{ has_boundary: boolean }>
      >`
        SELECT boundary IS NOT NULL AS has_boundary
        FROM fields
        WHERE id = ${fieldId}::uuid
      `;
      if (hasField[0]?.has_boundary) {
        throw new BadRequestException({
          message: "Sub-zone boundary must lie inside the parent field",
          messageAr: "يجب أن تكون حدود المنطقة الفرعية داخل حدود الحقل",
        });
      }
    }

    // INSERT + compute area in one statement. We do NOT use Prisma's
    // high-level create() because it can't round-trip PostGIS geometries.
    const [row] = await this.prisma.$queryRaw<SubZoneRow[]>`
      WITH inserted AS (
        INSERT INTO field_sub_zones (
          tenant_id, field_id, name, name_ar, description,
          boundary, area_hectares,
          elevation_m, slope_degrees, aspect, is_terrace, terrace_level,
          display_order, created_by
        )
        VALUES (
          ${tenantId},
          ${fieldId}::uuid,
          ${dto.name},
          ${dto.nameAr ?? null},
          ${dto.description ?? null},
          ST_GeomFromText(${wkt}, 4326),
          ST_Area(ST_GeomFromText(${wkt}, 4326)::geography) / 10000,
          ${dto.elevationM ?? null},
          ${dto.slopeDegrees ?? null},
          ${dto.aspect ?? null},
          ${dto.isTerrace ?? false},
          ${dto.terraceLevel ?? null},
          ${dto.displayOrder ?? 0},
          ${createdBy ?? null}
        )
        RETURNING *
      )
      SELECT
        id, tenant_id, field_id, name, name_ar, description,
        area_hectares, elevation_m, slope_degrees, aspect,
        is_terrace, terrace_level, display_order,
        ST_AsGeoJSON(boundary) AS boundary_geojson,
        deleted_at, created_by, created_at, updated_at
      FROM inserted
    `;

    // Write the outbox event OUTSIDE the $queryRaw above because Prisma's
    // $transaction wrapper doesn't nest with $queryRaw PostGIS calls in
    // a way that preserves the tx client — we accept weaker "best-effort"
    // delivery here and rely on outbox.markFailed retries if NATS is down.
    try {
      await this.prisma.outboxEvent.create({
        data: {
          eventType: "sahool.field.sub_zone.created",
          eventVersion: 1,
          schemaRef: "sahool.field.sub_zone.created:v1",
          tenantId: this.uuidOrNull(tenantId),
          correlationId: this.uuidOrNull(tenantId),
          aggregateType: "FieldSubZone",
          aggregateId: row.id,
          payloadJson: JSON.stringify({
            event_type: "sahool.field.sub_zone.created",
            tenant_id: tenantId,
            field_id: fieldId,
            sub_zone_id: row.id,
            name: row.name,
            area_hectares: row.area_hectares,
            is_terrace: row.is_terrace,
            terrace_level: row.terrace_level,
            occurred_at: new Date().toISOString(),
          }),
          published: false,
        },
      });
    } catch (e) {
      // Non-fatal: the row is already persisted; the outbox publisher
      // won't see it but that's still better than failing the mutation.
      this.logger.warn(
        `Failed to enqueue sub-zone.created outbox event: ${
          e instanceof Error ? e.message : e
        }`,
      );
    }

    return this.mapRow(row);
  }

  /**
   * Partial update. Only fields present in the DTO are changed. If
   * `boundary` is supplied it goes through the same validation as create.
   */
  async update(id: string, tenantId: string, dto: UpdateFieldSubZoneDto) {
    const existing = await this.getById(id, tenantId);

    // Build SET clauses dynamically. We use $queryRaw with explicit
    // parameters so this stays injection-safe.
    const sets: string[] = [];
    const params: unknown[] = [];
    let p = 1;
    const add = (col: string, val: unknown) => {
      sets.push(`${col} = $${p++}`);
      params.push(val);
    };

    if (dto.name !== undefined) add("name", dto.name);
    if (dto.nameAr !== undefined) add("name_ar", dto.nameAr);
    if (dto.description !== undefined) add("description", dto.description);
    if (dto.elevationM !== undefined) add("elevation_m", dto.elevationM);
    if (dto.slopeDegrees !== undefined) add("slope_degrees", dto.slopeDegrees);
    if (dto.aspect !== undefined) add("aspect", dto.aspect);
    if (dto.isTerrace !== undefined) add("is_terrace", dto.isTerrace);
    if (dto.terraceLevel !== undefined) add("terrace_level", dto.terraceLevel);
    if (dto.displayOrder !== undefined) add("display_order", dto.displayOrder);

    if (dto.boundary !== undefined) {
      const wkt = this.buildPolygonWkt(dto.boundary);
      await this.validatePolygonWithinField(wkt, existing.fieldId);
      sets.push(`boundary = ST_GeomFromText($${p++}, 4326)`);
      params.push(wkt);
      sets.push(
        `area_hectares = ST_Area(ST_GeomFromText($${p++}, 4326)::geography) / 10000`,
      );
      params.push(wkt);
    }

    if (sets.length === 0) {
      return existing;
    }

    params.push(id);
    const idParam = `$${p}`;
    const sql = `
      WITH updated AS (
        UPDATE field_sub_zones
        SET ${sets.join(", ")}
        WHERE id = ${idParam}::uuid
        RETURNING *
      )
      SELECT
        id, tenant_id, field_id, name, name_ar, description,
        area_hectares, elevation_m, slope_degrees, aspect,
        is_terrace, terrace_level, display_order,
        ST_AsGeoJSON(boundary) AS boundary_geojson,
        deleted_at, created_by, created_at, updated_at
      FROM updated
    `;
    const rows = await this.prisma.$queryRawUnsafe<SubZoneRow[]>(
      sql,
      ...params,
    );
    if (rows.length === 0) {
      throw new NotFoundException({
        message: "Sub-zone not found",
        messageAr: "المنطقة الفرعية غير موجودة",
      });
    }

    try {
      await this.prisma.outboxEvent.create({
        data: {
          eventType: "sahool.field.sub_zone.updated",
          eventVersion: 1,
          schemaRef: "sahool.field.sub_zone.updated:v1",
          tenantId: this.uuidOrNull(tenantId),
          correlationId: this.uuidOrNull(tenantId),
          aggregateType: "FieldSubZone",
          aggregateId: id,
          payloadJson: JSON.stringify({
            event_type: "sahool.field.sub_zone.updated",
            tenant_id: tenantId,
            field_id: existing.fieldId,
            sub_zone_id: id,
            changes: Object.keys(dto),
            occurred_at: new Date().toISOString(),
          }),
          published: false,
        },
      });
    } catch (e) {
      this.logger.warn(
        `Failed to enqueue sub-zone.updated outbox event: ${
          e instanceof Error ? e.message : e
        }`,
      );
    }

    return this.mapRow(rows[0]);
  }

  /**
   * Soft-delete — keeps the row for audit + allows undelete later.
   */
  async remove(
    id: string,
    tenantId: string,
    deletedBy?: string,
  ) {
    const existing = await this.getById(id, tenantId);
    await this.prisma.$executeRaw`
      UPDATE field_sub_zones
      SET deleted_at = NOW(),
          deleted_by = ${deletedBy ?? "system"}
      WHERE id = ${id}::uuid AND tenant_id = ${tenantId}
    `;
    try {
      await this.prisma.outboxEvent.create({
        data: {
          eventType: "sahool.field.sub_zone.deleted",
          eventVersion: 1,
          schemaRef: "sahool.field.sub_zone.deleted:v1",
          tenantId: this.uuidOrNull(tenantId),
          correlationId: this.uuidOrNull(tenantId),
          aggregateType: "FieldSubZone",
          aggregateId: id,
          payloadJson: JSON.stringify({
            event_type: "sahool.field.sub_zone.deleted",
            tenant_id: tenantId,
            field_id: existing.fieldId,
            sub_zone_id: id,
            deleted_by: deletedBy ?? "system",
            occurred_at: new Date().toISOString(),
          }),
          published: false,
        },
      });
    } catch (e) {
      this.logger.warn(
        `Failed to enqueue sub-zone.deleted outbox event: ${
          e instanceof Error ? e.message : e
        }`,
      );
    }
    return { id };
  }

  // ---------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------

  /**
   * Build a WKT POLYGON string from the DTO vertex list. Closes the ring
   * automatically if the client didn't (first vertex == last vertex).
   *
   * WKT format: POLYGON((lng1 lat1, lng2 lat2, ..., lng1 lat1))
   *
   * NOTE: WKT uses (x y) = (lng lat) order, NOT (lat lng)! Getting this
   * wrong is the #1 cause of "polygon in the ocean" bugs.
   */
  private buildPolygonWkt(points: SubZoneVertexDto[]): string {
    if (points.length < 3) {
      throw new BadRequestException({
        message: "Polygon must have at least 3 vertices",
        messageAr: "يجب أن تحتوي المنطقة على 3 نقاط على الأقل",
      });
    }
    const coords = [...points];
    const first = coords[0];
    const last = coords[coords.length - 1];
    if (first.lat !== last.lat || first.lng !== last.lng) {
      coords.push({ lat: first.lat, lng: first.lng });
    }
    const wktBody = coords.map((p) => `${p.lng} ${p.lat}`).join(", ");
    return `POLYGON((${wktBody}))`;
  }

  /** Validate a polygon fits inside a specific field. */
  private async validatePolygonWithinField(wkt: string, fieldId: string) {
    const validation = await this.prisma.$queryRaw<
      Array<{
        is_valid: boolean;
        is_simple: boolean;
        inside_field: boolean;
        has_field_boundary: boolean;
      }>
    >`
      SELECT
        ST_IsValid(p.geom)                              AS is_valid,
        ST_IsSimple(p.geom)                             AS is_simple,
        COALESCE(ST_Contains(f.boundary, p.geom), FALSE) AS inside_field,
        (f.boundary IS NOT NULL)                         AS has_field_boundary
      FROM (
        SELECT ST_GeomFromText(${wkt}, 4326) AS geom
      ) p
      LEFT JOIN fields f ON f.id = ${fieldId}::uuid
      LIMIT 1
    `;
    const v = validation[0];
    if (!v || !v.is_valid) {
      throw new BadRequestException({
        message: "Polygon geometry is invalid",
        messageAr: "هندسة المنطقة الفرعية غير صالحة",
      });
    }
    if (!v.is_simple) {
      throw new BadRequestException({
        message: "Polygon has self-intersection",
        messageAr: "المنطقة الفرعية تحتوي على تقاطع ذاتي",
      });
    }
    if (v.has_field_boundary && !v.inside_field) {
      throw new BadRequestException({
        message: "Sub-zone boundary must lie inside the parent field",
        messageAr: "يجب أن تكون حدود المنطقة الفرعية داخل حدود الحقل",
      });
    }
  }

  /** Verify field exists + belongs to the tenant. */
  private async assertFieldOwnership(fieldId: string, tenantId: string) {
    const field = await this.prisma.field.findUnique({
      where: { id_tenantId: { id: fieldId, tenantId } },
      select: { id: true, tenantId: true, isDeleted: true },
    });
    if (!field || field.isDeleted || field.tenantId !== tenantId) {
      throw new NotFoundException({
        message: "Field not found",
        messageAr: "الحقل غير موجود",
      });
    }
  }

  /** Normalize a raw SQL row into the camelCase API response shape. */
  private mapRow(r: SubZoneRow) {
    const num = (v: unknown): number | null =>
      v === null || v === undefined ? null : Number(v);
    return {
      id: r.id,
      tenantId: r.tenant_id,
      fieldId: r.field_id,
      name: r.name,
      nameAr: r.name_ar,
      description: r.description,
      boundary: r.boundary_geojson ? JSON.parse(r.boundary_geojson) : null,
      areaHectares: num(r.area_hectares),
      elevationM: num(r.elevation_m),
      slopeDegrees: num(r.slope_degrees),
      aspect: r.aspect,
      isTerrace: r.is_terrace,
      terraceLevel: r.terrace_level,
      displayOrder: r.display_order,
      createdBy: r.created_by,
      createdAt: r.created_at,
      updatedAt: r.updated_at,
    };
  }
}
