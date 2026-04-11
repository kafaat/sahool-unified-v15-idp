/**
 * Field Operation DTOs
 * نقل البيانات - عمليات الحقل
 */

import {
  IsString,
  IsOptional,
  IsUUID,
  IsDateString,
  IsNumber,
  IsIn,
  Min,
  Max,
  MaxLength,
} from "class-validator";

/**
 * Canonical operation types. Kept as a VARCHAR in the DB (with a CHECK
 * constraint) so adding a new type does not require a migration — only
 * update this list + the DB CHECK, which can be done in the same PR.
 */
export const OPERATION_TYPES = [
  "plowing",
  "land_preparation",
  "fertilization",
  "spraying",
  "irrigation",
  "harvesting",
  "scouting",
  "sowing",
  "other",
] as const;
export type OperationType = (typeof OPERATION_TYPES)[number];

/**
 * DTO for creating a new field operation. Caller must pass either
 * `cropSeasonId` (to attribute to a specific rotation) or leave it
 * unset (for pre-sowing operations that precede any season — e.g.
 * fallow tillage).
 */
export class CreateFieldOperationDto {
  @IsString()
  @IsIn(OPERATION_TYPES as unknown as string[])
  operationType: OperationType;

  @IsDateString()
  performedAt: string;

  @IsOptional()
  @IsDateString()
  endedAt?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(10000)
  durationHours?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(1_000_000_000)
  costAmount?: number;

  @IsOptional()
  @IsString()
  @MaxLength(8)
  costCurrency?: string;

  @IsOptional()
  @IsUUID()
  cropSeasonId?: string;

  @IsOptional()
  @IsUUID()
  equipmentId?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  equipmentName?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  equipmentNameAr?: string;

  @IsOptional()
  @IsString()
  @MaxLength(2000)
  notes?: string;
}

export class UpdateFieldOperationDto {
  @IsOptional()
  @IsString()
  @IsIn(OPERATION_TYPES as unknown as string[])
  operationType?: OperationType;

  @IsOptional()
  @IsDateString()
  performedAt?: string;

  @IsOptional()
  @IsDateString()
  endedAt?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(10000)
  durationHours?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  costAmount?: number;

  @IsOptional()
  @IsString()
  @MaxLength(8)
  costCurrency?: string;

  @IsOptional()
  @IsUUID()
  equipmentId?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  equipmentName?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  equipmentNameAr?: string;

  @IsOptional()
  @IsString()
  @MaxLength(2000)
  notes?: string;
}

export class QueryFieldOperationsDto {
  @IsOptional()
  @IsUUID()
  fieldId?: string;

  @IsOptional()
  @IsUUID()
  cropSeasonId?: string;

  @IsOptional()
  @IsString()
  @IsIn(OPERATION_TYPES as unknown as string[])
  operationType?: OperationType;

  @IsOptional()
  @IsUUID()
  equipmentId?: string;

  @IsOptional()
  @IsDateString()
  fromDate?: string;

  @IsOptional()
  @IsDateString()
  toDate?: string;

  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(200)
  limit?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  offset?: number;
}
