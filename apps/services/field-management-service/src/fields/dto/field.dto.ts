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
  IsBoolean,
  Matches,
} from "class-validator";
import { Type, Transform } from "class-transformer";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

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
  coordinates: number[][][];
}

/**
 * Create Field DTO
 */
export class CreateFieldDto {
  @ApiProperty({ description: "Field name", example: "North Wheat Field" })
  @IsString()
  @IsNotEmpty()
  @Transform(({ value }) => value?.trim())
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
    description: "Field boundary coordinates [[lng, lat], ...]",
    example: [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8]],
  })
  @IsOptional()
  @IsArray()
  @ArrayMinSize(3)
  coordinates?: number[][];

  @ApiPropertyOptional({ description: "GeoJSON boundary" })
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
  @Transform(({ value }) => value?.trim())
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
    description: "Radius in meters",
    minimum: 100,
    maximum: 50000,
    default: 5000,
  })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(100)
  @Max(50000)
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

  @ApiProperty({ enum: FieldStatus })
  status: FieldStatus;

  @ApiPropertyOptional()
  areaHectares?: number;

  @ApiPropertyOptional()
  healthScore?: number;

  @ApiPropertyOptional()
  ndviValue?: number;

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
    description: "New boundary coordinates [[lng, lat], ...]",
    example: [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8]],
  })
  @IsArray()
  @ArrayMinSize(3)
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
