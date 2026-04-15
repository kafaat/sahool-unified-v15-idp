// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Events DTOs - أنواع بيانات أحداث الكوارث
// ═══════════════════════════════════════════════════════════════════════════════
//
// DTOs for the /api/v1/disasters/events/* endpoints. These reuse the underlying
// DisasterReport storage but expose the frontend-expected "events" shape.
// ═══════════════════════════════════════════════════════════════════════════════

import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import {
  IsString,
  IsEnum,
  IsOptional,
  IsInt,
  IsNumber,
  IsArray,
  IsDateString,
  Min,
  Max,
  ValidateNested,
} from "class-validator";
import { Type } from "class-transformer";
import { DisasterType, Severity, LocationDto } from "../disaster/disaster.dto";

// ─────────────────────────────────────────────────────────────────────────────
// Event Status - flat set aligned with frontend expectations
// ─────────────────────────────────────────────────────────────────────────────

export enum DisasterEventStatus {
  ACTIVE = "active",
  MONITORING = "monitoring",
  RESOLVED = "resolved",
  ARCHIVED = "archived",
  REPORTED = "reported",
  VERIFIED = "verified",
}

// ─────────────────────────────────────────────────────────────────────────────
// List query
// ─────────────────────────────────────────────────────────────────────────────

export class ListEventsQueryDto {
  @ApiPropertyOptional({ enum: DisasterType })
  @IsOptional()
  @IsEnum(DisasterType)
  type?: DisasterType;

  @ApiPropertyOptional({ enum: Severity })
  @IsOptional()
  @IsEnum(Severity)
  severity?: Severity;

  @ApiPropertyOptional({ enum: DisasterEventStatus })
  @IsOptional()
  @IsEnum(DisasterEventStatus)
  status?: DisasterEventStatus;

  @ApiPropertyOptional({ description: "Filter by governorate" })
  @IsOptional()
  @IsString()
  governorate?: string;

  @ApiPropertyOptional({ description: "Filter by field ID" })
  @IsOptional()
  @IsString()
  fieldId?: string;

  @ApiPropertyOptional({ description: "Events reported on or after this date" })
  @IsOptional()
  @IsDateString()
  fromDate?: string;

  @ApiPropertyOptional({ description: "Events reported on or before this date" })
  @IsOptional()
  @IsDateString()
  toDate?: string;

  @ApiPropertyOptional({ default: 50, minimum: 1, maximum: 200 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(200)
  limit?: number;

  @ApiPropertyOptional({ default: 0, minimum: 0 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(0)
  offset?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Create event
// ─────────────────────────────────────────────────────────────────────────────

export class CreateDisasterEventDto {
  @ApiProperty({ enum: DisasterType, description: "Event type | نوع الحدث" })
  @IsEnum(DisasterType)
  type: DisasterType;

  @ApiProperty({ enum: Severity, description: "Severity | الشدة" })
  @IsEnum(Severity)
  severity: Severity;

  @ApiProperty({ description: "Short title" })
  @IsString()
  title: string;

  @ApiPropertyOptional({ description: "Arabic title" })
  @IsOptional()
  @IsString()
  titleAr?: string;

  @ApiPropertyOptional({ description: "Description (English)" })
  @IsOptional()
  @IsString()
  description?: string;

  @ApiPropertyOptional({ description: "Description (Arabic)" })
  @IsOptional()
  @IsString()
  descriptionAr?: string;

  @ApiProperty({ description: "Governorate code" })
  @IsString()
  governorate: string;

  @ApiPropertyOptional({ description: "District" })
  @IsOptional()
  @IsString()
  district?: string;

  @ApiProperty({ type: LocationDto, description: "Geo location" })
  @ValidateNested()
  @Type(() => LocationDto)
  location: LocationDto;

  @ApiPropertyOptional({ description: "Field ID (optional)" })
  @IsOptional()
  @IsString()
  fieldId?: string;

  @ApiPropertyOptional({ description: "Affected radius in km" })
  @IsOptional()
  @IsNumber()
  @Min(0)
  affectedRadiusKm?: number;

  @ApiPropertyOptional({ description: "Reported by user ID" })
  @IsOptional()
  @IsString()
  reportedBy?: string;

  @ApiPropertyOptional({ description: "ISO start date" })
  @IsOptional()
  @IsDateString()
  startDate?: string;

  @ApiPropertyOptional({ description: "Evidence image URLs", type: [String] })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  images?: string[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Update event (optimistic locking via version)
// ─────────────────────────────────────────────────────────────────────────────

export class UpdateDisasterEventDto {
  @ApiProperty({
    description: "Current version for optimistic locking",
    example: 1,
  })
  @IsInt()
  @Min(1)
  version: number;

  @ApiPropertyOptional({ enum: Severity })
  @IsOptional()
  @IsEnum(Severity)
  severity?: Severity;

  @ApiPropertyOptional({ enum: DisasterEventStatus })
  @IsOptional()
  @IsEnum(DisasterEventStatus)
  status?: DisasterEventStatus;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  title?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  titleAr?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  description?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  descriptionAr?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsNumber()
  @Min(0)
  affectedRadiusKm?: number;

  @ApiPropertyOptional({ description: "ISO end date" })
  @IsOptional()
  @IsDateString()
  endDate?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Update event status
// ─────────────────────────────────────────────────────────────────────────────

export class UpdateEventStatusDto {
  @ApiProperty({ enum: DisasterEventStatus })
  @IsEnum(DisasterEventStatus)
  status: DisasterEventStatus;

  @ApiPropertyOptional({ description: "Optional status change note" })
  @IsOptional()
  @IsString()
  note?: string;
}
