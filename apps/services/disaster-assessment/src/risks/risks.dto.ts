// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Risks DTOs - أنواع بيانات مخاطر الكوارث
// ═══════════════════════════════════════════════════════════════════════════════

import { ApiPropertyOptional } from "@nestjs/swagger";
import {
  IsEnum,
  IsInt,
  IsOptional,
  IsString,
  Max,
  Min,
} from "class-validator";
import { Type } from "class-transformer";
import { DisasterType } from "../disaster/disaster.dto";

export class ListRisksQueryDto {
  @ApiPropertyOptional({ enum: DisasterType, description: "Filter by risk type" })
  @IsOptional()
  @IsEnum(DisasterType)
  type?: DisasterType;

  @ApiPropertyOptional({ description: "Filter by governorate" })
  @IsOptional()
  @IsString()
  governorate?: string;

  @ApiPropertyOptional({ description: "Filter by field ID" })
  @IsOptional()
  @IsString()
  fieldId?: string;

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
