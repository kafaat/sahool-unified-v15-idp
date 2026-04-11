/**
 * FieldSubZone DTOs
 * نقل البيانات - المناطق الفرعية للحقل
 *
 * A FieldSubZone represents a sub-polygon inside a parent Field. Essential
 * for terraced Yemeni farms where a single "field" is actually many small
 * terraces with different elevation / slope / aspect / crop performance.
 */

import {
  IsString,
  IsOptional,
  IsBoolean,
  IsNumber,
  IsIn,
  IsArray,
  ArrayMinSize,
  ArrayMaxSize,
  Min,
  Max,
  MaxLength,
  ValidateNested,
} from "class-validator";
import { Type } from "class-transformer";

/** Canonical aspect directions (matches CHECK constraint in migration). */
export const ASPECT_VALUES = [
  "N",
  "NE",
  "E",
  "SE",
  "S",
  "SW",
  "W",
  "NW",
  "flat",
] as const;
export type AspectValue = (typeof ASPECT_VALUES)[number];

/**
 * A single (lat, lng) vertex of the sub-zone polygon. Matches the shape
 * already used by FieldBoundary in types.ts so the web client can reuse
 * the same validation + rendering code.
 */
export class SubZoneVertexDto {
  @IsNumber()
  @Min(-90)
  @Max(90)
  lat: number;

  @IsNumber()
  @Min(-180)
  @Max(180)
  lng: number;
}

export class CreateFieldSubZoneDto {
  @IsString()
  @MaxLength(255)
  name: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  nameAr?: string;

  @IsOptional()
  @IsString()
  @MaxLength(2000)
  description?: string;

  /**
   * Polygon vertices in WGS84. Must have at least 3 vertices (for a valid
   * triangle) and at most 500 (upper bound so clients can't DoS the service
   * with pathological geometries). The service enforces closure + inside-
   * parent-field validation on top of this schema check.
   */
  @IsArray()
  @ArrayMinSize(3)
  @ArrayMaxSize(500)
  @ValidateNested({ each: true })
  @Type(() => SubZoneVertexDto)
  boundary: SubZoneVertexDto[];

  @IsOptional()
  @IsNumber()
  @Min(-500)
  @Max(10000)
  elevationM?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(90)
  slopeDegrees?: number;

  @IsOptional()
  @IsString()
  @IsIn(ASPECT_VALUES as unknown as string[])
  aspect?: AspectValue;

  @IsOptional()
  @IsBoolean()
  isTerrace?: boolean;

  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(100)
  terraceLevel?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(1_000_000)
  displayOrder?: number;
}

/**
 * Partial update. Clients send only the fields they want to change. The
 * service layer merges with the existing row — fields that are NOT present
 * in the DTO are preserved unchanged.
 */
export class UpdateFieldSubZoneDto {
  @IsOptional()
  @IsString()
  @MaxLength(255)
  name?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  nameAr?: string;

  @IsOptional()
  @IsString()
  @MaxLength(2000)
  description?: string;

  @IsOptional()
  @IsArray()
  @ArrayMinSize(3)
  @ArrayMaxSize(500)
  @ValidateNested({ each: true })
  @Type(() => SubZoneVertexDto)
  boundary?: SubZoneVertexDto[];

  @IsOptional()
  @IsNumber()
  elevationM?: number;

  @IsOptional()
  @IsNumber()
  slopeDegrees?: number;

  @IsOptional()
  @IsString()
  @IsIn(ASPECT_VALUES as unknown as string[])
  aspect?: AspectValue;

  @IsOptional()
  @IsBoolean()
  isTerrace?: boolean;

  @IsOptional()
  @IsNumber()
  terraceLevel?: number;

  @IsOptional()
  @IsNumber()
  displayOrder?: number;
}
