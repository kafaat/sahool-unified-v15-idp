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

  // ── Cost breakdown (IAS 41 — all optional, additive) ───────────────
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000)
  fuelLiters?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000_000)
  fuelCost?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(10000)
  laborHours?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000_000)
  laborCost?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000_000)
  materialsCost?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000_000)
  overheadCost?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000_000)
  otherCost?: number;

  // ── Tax + multi-currency ────────────────────────────────────────────
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000_000)
  taxAmount?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(100)
  taxRate?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(1_000_000)
  exchangeRate?: number;
  @IsOptional() @IsString() @MaxLength(8)
  baseCurrency?: string;

  // ── Vendor / invoice ────────────────────────────────────────────────
  @IsOptional() @IsString() @MaxLength(100)
  invoiceNumber?: string;
  @IsOptional() @IsDateString()
  invoiceDate?: string;
  @IsOptional() @IsString() @MaxLength(100)
  vendorId?: string;
  @IsOptional() @IsString() @MaxLength(255)
  vendorName?: string;
  @IsOptional() @IsString() @MaxLength(500)
  receiptUrl?: string;

  // ── GL / cost-center / project ──────────────────────────────────────
  @IsOptional() @IsString() @MaxLength(50)
  glAccount?: string;
  @IsOptional() @IsString() @MaxLength(50)
  costCenter?: string;
  @IsOptional() @IsString() @MaxLength(50)
  projectCode?: string;
}

/**
 * DTO for approval workflow (approve / reject a pending operation).
 */
export class ApproveFieldOperationDto {
  @IsOptional()
  @IsString()
  @MaxLength(2000)
  notes?: string;
}

export class RejectFieldOperationDto {
  @IsString()
  @MaxLength(2000)
  reason: string;
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

  // All accounting fields from CreateFieldOperationDto are also
  // updatable on PATCH.
  @IsOptional() @IsNumber() @Min(0) fuelLiters?: number;
  @IsOptional() @IsNumber() @Min(0) fuelCost?: number;
  @IsOptional() @IsNumber() @Min(0) laborHours?: number;
  @IsOptional() @IsNumber() @Min(0) laborCost?: number;
  @IsOptional() @IsNumber() @Min(0) materialsCost?: number;
  @IsOptional() @IsNumber() @Min(0) overheadCost?: number;
  @IsOptional() @IsNumber() @Min(0) otherCost?: number;
  @IsOptional() @IsNumber() @Min(0) taxAmount?: number;
  @IsOptional() @IsNumber() @Min(0) @Max(100) taxRate?: number;
  @IsOptional() @IsNumber() @Min(0) exchangeRate?: number;
  @IsOptional() @IsString() @MaxLength(8) baseCurrency?: string;
  @IsOptional() @IsString() @MaxLength(100) invoiceNumber?: string;
  @IsOptional() @IsDateString() invoiceDate?: string;
  @IsOptional() @IsString() @MaxLength(100) vendorId?: string;
  @IsOptional() @IsString() @MaxLength(255) vendorName?: string;
  @IsOptional() @IsString() @MaxLength(500) receiptUrl?: string;
  @IsOptional() @IsString() @MaxLength(50) glAccount?: string;
  @IsOptional() @IsString() @MaxLength(50) costCenter?: string;
  @IsOptional() @IsString() @MaxLength(50) projectCode?: string;
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
