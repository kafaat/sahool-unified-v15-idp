/**
 * Query Farms DTO - SAHOOL Field Management Service
 * نموذج استعلام المزارع
 *
 * List / filter parameters for GET /api/v1/farms.
 */

import {
  IsString,
  IsOptional,
  IsInt,
  IsEnum,
  Min,
  Max,
  MaxLength,
} from "class-validator";
import { Type } from "class-transformer";
import { ApiPropertyOptional } from "@nestjs/swagger";
import { FarmStatus } from "./create-farm.dto";

export class QueryFarmsDto {
  @ApiPropertyOptional({ enum: FarmStatus, description: "Filter by status" })
  @IsOptional()
  @IsEnum(FarmStatus)
  status?: FarmStatus;

  @ApiPropertyOptional({ description: "Filter by region (exact match)" })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  region?: string;

  @ApiPropertyOptional({
    description: "Search by name / nameAr / location (ILIKE)",
  })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  search?: string;

  @ApiPropertyOptional({ description: "Page number", minimum: 1, default: 1 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
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
  @IsInt()
  @Min(1)
  @Max(100)
  limit?: number = 20;
}
