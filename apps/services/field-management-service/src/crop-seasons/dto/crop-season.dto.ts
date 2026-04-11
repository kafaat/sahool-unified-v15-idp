/**
 * Crop Season DTOs
 * نقل البيانات - مواسم المحاصيل
 */

import {
  IsString,
  IsOptional,
  IsUUID,
  IsDateString,
  IsNumber,
  IsBoolean,
  IsIn,
  Min,
  Max,
  MaxLength,
} from "class-validator";

/**
 * Canonical season classifications accepted by the backend. Kept as a
 * VARCHAR in the DB so new values can be added without a migration.
 */
export const SEASON_VALUES = [
  "winter",
  "spring",
  "summer",
  "autumn",
  "year-round",
] as const;
export type SeasonValue = (typeof SEASON_VALUES)[number];

/**
 * DTO for creating a new crop season.
 *
 * The service layer enforces `tenantId` from the JWT via TenantGuard, so
 * the client CANNOT override it even if they try. The controller strips
 * `tenantId` out of the body and sets it from `req.tenantId`.
 */
export class CreateCropSeasonDto {
  @IsString()
  @MaxLength(100)
  cropType: string;

  @IsOptional()
  @IsString()
  @MaxLength(100)
  cropTypeAr?: string;

  @IsOptional()
  @IsString()
  @IsIn(SEASON_VALUES as unknown as string[])
  season?: SeasonValue;

  @IsDateString()
  sowingDate: string;

  @IsOptional()
  @IsDateString()
  expectedHarvestDate?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  seedVariety?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  seedVarietyAr?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100000)
  plantingDensityKgHa?: number;

  @IsOptional()
  @IsString()
  @MaxLength(50)
  irrigationType?: string;

  @IsOptional()
  @IsString()
  @MaxLength(2000)
  notes?: string;
}

/**
 * DTO for updating a crop season. All fields optional — service layer
 * applies only the provided keys. `isCurrent` can be toggled (useful
 * when admins correct a mis-ended season).
 */
export class UpdateCropSeasonDto {
  @IsOptional()
  @IsString()
  @MaxLength(100)
  cropType?: string;

  @IsOptional()
  @IsString()
  @MaxLength(100)
  cropTypeAr?: string;

  @IsOptional()
  @IsString()
  @IsIn(SEASON_VALUES as unknown as string[])
  season?: SeasonValue;

  @IsOptional()
  @IsDateString()
  sowingDate?: string;

  @IsOptional()
  @IsDateString()
  expectedHarvestDate?: string;

  @IsOptional()
  @IsDateString()
  actualHarvestDate?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  seedVariety?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  seedVarietyAr?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100000)
  plantingDensityKgHa?: number;

  @IsOptional()
  @IsString()
  @MaxLength(50)
  irrigationType?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  yieldKgHa?: number;

  @IsOptional()
  @IsString()
  @MaxLength(2000)
  notes?: string;

  @IsOptional()
  @IsBoolean()
  isCurrent?: boolean;
}

/**
 * DTO for ending a crop season. Sets endedAt = now (or explicit),
 * endReason, actualHarvestDate, and isCurrent = false.
 */
export class EndCropSeasonDto {
  @IsOptional()
  @IsDateString()
  endedAt?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  endReason?: string;

  @IsOptional()
  @IsDateString()
  actualHarvestDate?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  yieldKgHa?: number;
}

/**
 * Query filters for listing crop seasons. Tenant isolation is enforced
 * by TenantGuard - clients cannot request cross-tenant data.
 */
export class QueryCropSeasonsDto {
  @IsOptional()
  @IsUUID()
  fieldId?: string;

  @IsOptional()
  @IsString()
  cropType?: string;

  @IsOptional()
  @IsBoolean()
  isCurrent?: boolean;

  @IsOptional()
  @IsDateString()
  sowingAfter?: string;

  @IsOptional()
  @IsDateString()
  sowingBefore?: string;

  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(100)
  limit?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  offset?: number;
}
