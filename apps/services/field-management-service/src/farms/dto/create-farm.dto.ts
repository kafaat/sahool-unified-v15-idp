/**
 * Create Farm DTO - SAHOOL Field Management Service
 * نموذج إنشاء مزرعة
 *
 * Validates the payload for POST /api/v1/farms.
 */

import {
  IsString,
  IsOptional,
  IsInt,
  IsNumber,
  IsEmail,
  IsEnum,
  IsNotEmpty,
  IsUUID,
  Min,
  MaxLength,
} from "class-validator";
import { Transform, Type } from "class-transformer";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

export enum FarmStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  ARCHIVED = "archived",
}

export class CreateFarmDto {
  @ApiProperty({ description: "Farm name (EN)", example: "Al-Rashid Farm" })
  @IsString()
  @IsNotEmpty()
  @MaxLength(255)
  @Transform(({ value }: { value?: string }) => value?.trim())
  name!: string;

  @ApiProperty({
    description: "Farm name (AR)",
    example: "مزرعة الراشد",
  })
  @IsString()
  @IsNotEmpty()
  @MaxLength(255)
  @Transform(({ value }: { value?: string }) => value?.trim())
  nameAr!: string;

  @ApiPropertyOptional({ description: "Owner ID (UUID)" })
  @IsOptional()
  @IsUUID()
  ownerId?: string;

  @ApiPropertyOptional({ description: "Farm owner display name" })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  owner?: string;

  @ApiPropertyOptional({ description: "Region / province (EN)" })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  region?: string;

  @ApiPropertyOptional({ description: "Region / province (AR)" })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  regionAr?: string;

  @ApiPropertyOptional({ description: "Primary water source (EN)" })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  waterSource?: string;

  @ApiPropertyOptional({ description: "Primary water source (AR)" })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  waterSourceAr?: string;

  @ApiPropertyOptional({ description: "Number of workers", minimum: 0 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(0)
  workersCount?: number;

  @ApiPropertyOptional({
    enum: FarmStatus,
    description: "Farm status",
    default: FarmStatus.ACTIVE,
  })
  @IsOptional()
  @IsEnum(FarmStatus)
  status?: FarmStatus;

  @ApiPropertyOptional({
    description: "Total area in hectares",
    minimum: 0,
  })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(0)
  totalAreaHectares?: number;

  @ApiPropertyOptional({
    description: "Cultivated area in hectares",
    minimum: 0,
  })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(0)
  cultivatedAreaHectares?: number;

  @ApiPropertyOptional({ description: "Human-readable location label (EN)" })
  @IsOptional()
  @IsString()
  @MaxLength(500)
  location?: string;

  @ApiPropertyOptional({ description: "Human-readable location label (AR)" })
  @IsOptional()
  @IsString()
  @MaxLength(500)
  locationAr?: string;

  @ApiPropertyOptional({ description: "Street address" })
  @IsOptional()
  @IsString()
  address?: string;

  @ApiPropertyOptional({ description: "Contact phone" })
  @IsOptional()
  @IsString()
  @MaxLength(20)
  phone?: string;

  @ApiPropertyOptional({ description: "Contact email" })
  @IsOptional()
  @IsEmail()
  @MaxLength(255)
  email?: string;
}
