/**
 * Field DTOs - Data Transfer Objects
 *
 * Comprehensive validation for field operations
 */

import {
  IsString,
  IsNumber,
  IsOptional,
  IsArray,
  IsEnum,
  IsUUID,
  IsNotEmpty,
  IsObject,
  Min,
  Max,
  ValidateNested,
  IsDateString,
  ArrayMinSize,
  ArrayMaxSize,
  Matches,
  Validate,
  ValidatorConstraint,
  ValidatorConstraintInterface,
} from "class-validator";
import { Type, Transform } from "class-transformer";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

// ---------------------------------------------------------------------------
// Configurable geospatial limits (override via environment variables)
// ---------------------------------------------------------------------------

/** Maximum boundary area in hectares (default: 10,000 ha) */
const parsedMaxBoundaryArea = parseFloat(process.env.MAX_BOUNDARY_AREA_HECTARES ?? '');
export const MAX_BOUNDARY_AREA_HECTARES = Number.isFinite(parsedMaxBoundaryArea) ? parsedMaxBoundaryArea : 10_000;

/** Maximum proximity query distance in meters (default: 100 km) */
const parsedMaxProximityDistance = parseFloat(process.env.MAX_PROXIMITY_DISTANCE_METERS ?? '');
export const MAX_PROXIMITY_DISTANCE_METERS = Number.isFinite(parsedMaxProximityDistance) ? parsedMaxProximityDistance : 100_000;

/** Maximum number of coordinate points in a single polygon ring */
const MAX_POLYGON_POINTS = 10_000;

// ---------------------------------------------------------------------------
// Custom validators
// ---------------------------------------------------------------------------

/**
 * Validates that every element in a number[][] array is a valid [lng, lat] pair.
 */
@ValidatorConstraint({ name: "isValidCoordinatePairs", async: false })
export class IsValidCoordinatePairsConstraint implements ValidatorConstraintInterface {
  validate(coordinates: unknown): boolean {
    if (!Array.isArray(coordinates)) return false;
    return coordinates.every(
      (pair: unknown) =>
        Array.isArray(pair) &&
        pair.length >= 2 &&
        typeof pair[0] === "number" &&
        typeof pair[1] === "number" &&
        pair[0] >= -180 &&
        pair[0] <= 180 && // longitude
        pair[1] >= -90 &&
        pair[1] <= 90, // latitude
    );
  }

  defaultMessage(): string {
    return "Each coordinate must be a [longitude, latitude] pair with longitude in [-180, 180] and latitude in [-90, 90]";
  }
}

/**
 * Validates GeoJSON Polygon coordinate structure:
 * - At least one linear ring
 * - Each ring has at least 4 positions (3 unique + closing point)
 * - Every position is a valid [lng, lat] pair
 * - Ring is closed (first === last position)
 * - No ring exceeds MAX_POLYGON_POINTS positions
 */
@ValidatorConstraint({ name: "isValidGeoJsonCoordinates", async: false })
export class IsValidGeoJsonCoordinatesConstraint implements ValidatorConstraintInterface {
  validate(coordinates: unknown): boolean {
    if (!Array.isArray(coordinates) || coordinates.length === 0) return false;

    return coordinates.every((ring: unknown) => {
      if (!Array.isArray(ring)) return false;
      // A valid polygon ring needs at least 4 points (3 unique + closing)
      if (ring.length < 4) return false;
      if (ring.length > MAX_POLYGON_POINTS) return false;

      // Validate each position
      const valid = ring.every(
        (pos: unknown) =>
          Array.isArray(pos) &&
          pos.length >= 2 &&
          typeof pos[0] === "number" &&
          typeof pos[1] === "number" &&
          pos[0] >= -180 &&
          pos[0] <= 180 &&
          pos[1] >= -90 &&
          pos[1] <= 90,
      );
      if (!valid) return false;

      // Ring must be closed (first position === last position)
      const first = ring[0] as number[];
      const last = ring[ring.length - 1] as number[];
      return first[0] === last[0] && first[1] === last[1];
    });
  }

  defaultMessage(): string {
    return (
      "GeoJSON Polygon coordinates must contain at least one ring, each ring must have " +
      "at least 4 positions (3 unique + closing point), every position must be a valid " +
      "[longitude, latitude] pair, and the ring must be closed (first === last position)"
    );
  }
}

/**
 * Rough area estimator for coordinate arrays (Shoelace formula on lng/lat).
 * Returns approximate area in hectares. Used only as a DoS guard, not for
 * precise geodetic area calculation.
 */
function estimateAreaHectares(coords: number[][]): number {
  // Shoelace formula on projected coordinates (rough, equirectangular)
  const n = coords.length;
  if (n < 3) return 0;

  // Use centroid latitude for equirectangular correction
  const avgLat =
    coords.reduce((sum, c) => sum + (c[1] ?? 0), 0) / n;
  const cosLat = Math.cos((avgLat * Math.PI) / 180);

  let area = 0;
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const xi = (coords[i]?.[0] ?? 0) * cosLat;
    const yi = coords[i]?.[1] ?? 0;
    const xj = (coords[j]?.[0] ?? 0) * cosLat;
    const yj = coords[j]?.[1] ?? 0;
    area += xi * yj - xj * yi;
  }

  // Convert square degrees to hectares (1 degree ≈ 111.32 km at equator)
  const sqDegrees = Math.abs(area) / 2;
  const sqKm = sqDegrees * 111.32 * 111.32;
  return sqKm * 100; // 1 km² = 100 ha
}

/**
 * Validates that a coordinate array does not exceed the maximum allowed area.
 */
@ValidatorConstraint({ name: "isWithinMaxArea", async: false })
export class IsWithinMaxAreaConstraint implements ValidatorConstraintInterface {
  validate(coordinates: unknown): boolean {
    if (!Array.isArray(coordinates) || coordinates.length < 3) return true; // skip, other validators handle this
    return estimateAreaHectares(coordinates as number[][]) <= MAX_BOUNDARY_AREA_HECTARES;
  }

  defaultMessage(): string {
    return `Field boundary area must not exceed ${MAX_BOUNDARY_AREA_HECTARES} hectares`;
  }
}

/**
 * Validates that GeoJSON Polygon coordinates do not exceed the maximum allowed area.
 */
@ValidatorConstraint({ name: "isGeoJsonWithinMaxArea", async: false })
export class IsGeoJsonWithinMaxAreaConstraint implements ValidatorConstraintInterface {
  validate(coordinates: unknown): boolean {
    if (!Array.isArray(coordinates) || coordinates.length === 0) return true;
    // Check outer ring only (index 0)
    const outerRing = coordinates[0] as number[][];
    if (!Array.isArray(outerRing) || outerRing.length < 4) return true;
    return estimateAreaHectares(outerRing) <= MAX_BOUNDARY_AREA_HECTARES;
  }

  defaultMessage(): string {
    return `Field boundary area must not exceed ${MAX_BOUNDARY_AREA_HECTARES} hectares`;
  }
}

// Field status enum
export enum FieldStatus {
  ACTIVE = "active",
  FALLOW = "fallow",
  HARVESTED = "harvested",
  PREPARING = "preparing",
  INACTIVE = "inactive",
}

// Irrigation types
export enum IrrigationType {
  DRIP = "drip",
  FLOOD = "flood",
  SPRINKLER = "sprinkler",
  RAINFED = "rainfed",
  PIVOT = "pivot",
}

// Soil types
export enum SoilType {
  CLAY = "clay",
  SANDY = "sandy",
  LOAMY = "loamy",
  SILTY = "silty",
  SALINE = "saline",
}

/**
 * Coordinate DTO for GeoJSON
 */
export class CoordinateDto {
  @ApiProperty({ description: "Longitude", example: 46.7 })
  @IsNumber()
  @Min(-180)
  @Max(180)
  longitude: number;

  @ApiProperty({ description: "Latitude", example: 24.7 })
  @IsNumber()
  @Min(-90)
  @Max(90)
  latitude: number;
}

/**
 * GeoJSON Polygon DTO
 *
 * Validates structural correctness of GeoJSON Polygon geometry:
 * - type must be "Polygon"
 * - coordinates must have at least one linear ring
 * - each ring must have >= 4 positions (3 unique + closing), be closed, and
 *   contain valid [lng, lat] pairs within [-180,180] / [-90,90]
 * - total area must not exceed MAX_BOUNDARY_AREA_HECTARES
 */
export class GeoJsonPolygonDto {
  @ApiProperty({ enum: ["Polygon"], example: "Polygon" })
  @IsString()
  @Matches(/^Polygon$/)
  type: "Polygon";

  @ApiProperty({
    description: "Polygon coordinates [[[lng, lat], ...]]",
    example: [[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]],
  })
  @IsArray()
  @ArrayMinSize(1)
  @Validate(IsValidGeoJsonCoordinatesConstraint)
  @Validate(IsGeoJsonWithinMaxAreaConstraint)
  coordinates: number[][][];
}

/**
 * Create Field DTO
 */
export class CreateFieldDto {
  @ApiProperty({ description: "Field name", example: "North Wheat Field" })
  @IsString()
  @IsNotEmpty()
  @Transform(({ value }: { value?: string }) => value?.trim())
  name: string;

  @ApiProperty({ description: "Tenant ID", example: "tenant-001" })
  @IsString()
  @IsNotEmpty()
  tenantId: string;

  @ApiProperty({ description: "Crop type", example: "wheat" })
  @IsString()
  @IsNotEmpty()
  cropType: string;

  @ApiPropertyOptional({ description: "Owner ID (UUID)" })
  @IsOptional()
  @IsUUID()
  ownerId?: string;

  @ApiPropertyOptional({ description: "Farm ID (UUID)" })
  @IsOptional()
  @IsUUID()
  farmId?: string;

  @ApiPropertyOptional({
    description: "Field boundary coordinates [[lng, lat], ...] — minimum 3 points for a valid polygon",
    example: [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8]],
  })
  @IsOptional()
  @IsArray()
  @ArrayMinSize(3, { message: "A polygon requires at least 3 coordinate points" })
  @ArrayMaxSize(MAX_POLYGON_POINTS, {
    message: `Polygon must not exceed ${MAX_POLYGON_POINTS} coordinate points`,
  })
  @Validate(IsValidCoordinatePairsConstraint)
  @Validate(IsWithinMaxAreaConstraint)
  coordinates?: number[][];

  @ApiPropertyOptional({ description: "GeoJSON boundary (Polygon)" })
  @IsOptional()
  @ValidateNested()
  @Type(() => GeoJsonPolygonDto)
  boundary?: GeoJsonPolygonDto;

  @ApiPropertyOptional({ enum: IrrigationType })
  @IsOptional()
  @IsEnum(IrrigationType)
  irrigationType?: IrrigationType;

  @ApiPropertyOptional({ enum: SoilType })
  @IsOptional()
  @IsEnum(SoilType)
  soilType?: SoilType;

  @ApiPropertyOptional({ description: "Planting date (ISO 8601)" })
  @IsOptional()
  @IsDateString()
  plantingDate?: string;

  @ApiPropertyOptional({ description: "Expected harvest date (ISO 8601)" })
  @IsOptional()
  @IsDateString()
  expectedHarvest?: string;

  @ApiPropertyOptional({ description: "Additional metadata (JSON)" })
  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}

/**
 * Update Field DTO
 */
export class UpdateFieldDto {
  @ApiPropertyOptional({ description: "Field name" })
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @Transform(({ value }: { value?: string }) => value?.trim())
  name?: string;

  @ApiPropertyOptional({ description: "Crop type" })
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  cropType?: string;

  @ApiPropertyOptional({ enum: FieldStatus })
  @IsOptional()
  @IsEnum(FieldStatus)
  status?: FieldStatus;

  @ApiPropertyOptional({ enum: IrrigationType })
  @IsOptional()
  @IsEnum(IrrigationType)
  irrigationType?: IrrigationType;

  @ApiPropertyOptional({ enum: SoilType })
  @IsOptional()
  @IsEnum(SoilType)
  soilType?: SoilType;

  @ApiPropertyOptional({ description: "Planting date (ISO 8601)" })
  @IsOptional()
  @IsDateString()
  plantingDate?: string;

  @ApiPropertyOptional({ description: "Expected harvest date (ISO 8601)" })
  @IsOptional()
  @IsDateString()
  expectedHarvest?: string;

  @ApiPropertyOptional({ description: "Additional metadata (JSON)" })
  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;

  @ApiPropertyOptional({ description: "GeoJSON boundary" })
  @IsOptional()
  @ValidateNested()
  @Type(() => GeoJsonPolygonDto)
  boundary?: GeoJsonPolygonDto;

  @ApiPropertyOptional({
    description:
      "Expected version for optimistic locking. If supplied and does not " +
      "match the server's current version, the request is rejected with " +
      "HTTP 409 Conflict. Takes precedence over the If-Match header when both are present.",
    example: 3,
  })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  ifMatch?: number;
}

/**
 * Query Fields DTO
 */
export class QueryFieldsDto {
  @ApiPropertyOptional({ description: "Tenant ID" })
  @IsOptional()
  @IsString()
  tenantId?: string;

  @ApiPropertyOptional({ enum: FieldStatus })
  @IsOptional()
  @IsEnum(FieldStatus)
  status?: FieldStatus;

  @ApiPropertyOptional({ description: "Crop type" })
  @IsOptional()
  @IsString()
  cropType?: string;

  @ApiPropertyOptional({ description: "Page number", minimum: 1, default: 1 })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  page?: number = 1;

  @ApiPropertyOptional({
    description: "Items per page",
    minimum: 1,
    maximum: 100,
    default: 20,
  })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  @Max(100)
  limit?: number = 20;
}

/**
 * Nearby Fields Query DTO
 */
export class NearbyFieldsDto {
  @ApiProperty({ description: "Tenant ID", example: "tenant-123" })
  @IsString()
  tenantId: string;

  @ApiProperty({ description: "Latitude", example: 24.7 })
  @Type(() => Number)
  @IsNumber()
  @Min(-90)
  @Max(90)
  lat: number;

  @ApiProperty({ description: "Longitude", example: 46.7 })
  @Type(() => Number)
  @IsNumber()
  @Min(-180)
  @Max(180)
  lng: number;

  @ApiPropertyOptional({
    description: `Radius in meters (max: ${MAX_PROXIMITY_DISTANCE_METERS})`,
    minimum: 100,
    maximum: MAX_PROXIMITY_DISTANCE_METERS,
    default: 5000,
  })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(100, { message: "Radius must be at least 100 meters" })
  @Max(MAX_PROXIMITY_DISTANCE_METERS, {
    message: `Radius must not exceed ${MAX_PROXIMITY_DISTANCE_METERS} meters (${MAX_PROXIMITY_DISTANCE_METERS / 1000} km)`,
  })
  radius?: number = 5000;
}

/**
 * Field Response DTO
 */
export class FieldResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty()
  name: string;

  @ApiProperty()
  tenantId: string;

  @ApiProperty()
  cropType: string;

  @ApiPropertyOptional()
  ownerId?: string;

  @ApiPropertyOptional()
  farmId?: string;

  @ApiProperty({ enum: FieldStatus })
  status: FieldStatus;

  @ApiPropertyOptional()
  areaHectares?: number;

  @ApiPropertyOptional()
  healthScore?: number;

  @ApiPropertyOptional()
  ndviValue?: number;

  @ApiPropertyOptional({ description: 'Centroid latitude (WGS84)' })
  centroidLat?: number;

  @ApiPropertyOptional({ description: 'Centroid longitude (WGS84)' })
  centroidLng?: number;

  @ApiPropertyOptional({
    description:
      'Axis-aligned bounding box in WGS84, in GeoJSON RFC 7946 order: [minLng, minLat, maxLng, maxLat]. Derived from `boundary` via PostGIS `ST_Envelope` at read time, so it is always in sync with the polygon.',
    type: [Number],
    example: [46.71, 24.71, 46.79, 24.79],
  })
  bbox?: [number, number, number, number];

  @ApiPropertyOptional()
  irrigationType?: string;

  @ApiPropertyOptional()
  soilType?: string;

  @ApiPropertyOptional()
  plantingDate?: Date;

  @ApiPropertyOptional()
  expectedHarvest?: Date;

  @ApiProperty()
  etag: string;

  @ApiProperty()
  version: number;

  @ApiProperty()
  createdAt: Date;

  @ApiProperty()
  updatedAt: Date;
}

/**
 * Paginated Response DTO
 */
export class PaginatedFieldsResponseDto {
  @ApiProperty({ type: [FieldResponseDto] })
  data: FieldResponseDto[];

  @ApiProperty()
  meta: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

/**
 * Update Boundary DTO
 */
export class UpdateBoundaryDto {
  @ApiProperty({
    description: "New boundary coordinates [[lng, lat], ...] — minimum 3 points for a valid polygon",
    example: [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8]],
  })
  @IsArray()
  @ArrayMinSize(3, { message: "A polygon requires at least 3 coordinate points" })
  @ArrayMaxSize(MAX_POLYGON_POINTS, {
    message: `Polygon must not exceed ${MAX_POLYGON_POINTS} coordinate points`,
  })
  @Validate(IsValidCoordinatePairsConstraint)
  @Validate(IsWithinMaxAreaConstraint)
  coordinates: number[][];

  @ApiPropertyOptional({ description: "User ID making the change" })
  @IsOptional()
  @IsString()
  userId?: string;

  @ApiPropertyOptional({ description: "Reason for boundary change" })
  @IsOptional()
  @IsString()
  reason?: string;

  @ApiPropertyOptional({ description: "Device ID (for mobile sync)" })
  @IsOptional()
  @IsString()
  deviceId?: string;
}

/**
 * Rollback Boundary DTO
 */
export class RollbackBoundaryDto {
  @ApiProperty({ description: "History entry ID to rollback to" })
  @IsUUID()
  historyId: string;

  @ApiPropertyOptional({ description: "User ID making the rollback" })
  @IsOptional()
  @IsString()
  userId?: string;

  @ApiPropertyOptional({ description: "Reason for rollback" })
  @IsOptional()
  @IsString()
  reason?: string;
}

/**
 * Check Overlap DTO - ported from the archived field-service
 *
 * Callers pass a candidate GeoJSON polygon (and optionally an existing
 * fieldId to exclude for the "am I overlapping anyone else?" update case)
 * and get back a list of tenant-scoped fields whose boundaries intersect.
 */
export class CheckOverlapDto {
  @ApiProperty({
    description: "Candidate polygon coordinates [[lng, lat], ...] (outer ring only)",
    example: [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8]],
  })
  @IsArray()
  @ArrayMinSize(3, { message: "A polygon requires at least 3 coordinate points" })
  @ArrayMaxSize(MAX_POLYGON_POINTS, {
    message: `Polygon must not exceed ${MAX_POLYGON_POINTS} coordinate points`,
  })
  @Validate(IsValidCoordinatePairsConstraint)
  @Validate(IsWithinMaxAreaConstraint)
  coordinates: number[][];

  @ApiPropertyOptional({
    description:
      "Field ID to exclude from the overlap scan — use when checking a boundary edit for an existing field",
  })
  @IsOptional()
  @IsUUID()
  excludeFieldId?: string;
}
