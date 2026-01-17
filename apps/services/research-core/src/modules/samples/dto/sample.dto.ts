import { ApiProperty, ApiPropertyOptional, PartialType } from "@nestjs/swagger";
import {
  IsString,
  IsOptional,
  IsUUID,
  IsEnum,
  IsObject,
  IsDateString,
  IsArray,
  IsDecimal,
  IsNumber,
} from "class-validator";

export enum SampleType {
  SOIL = "soil",
  PLANT = "plant",
  WATER = "water",
  PEST = "pest",
  OTHER = "other",
}

export class CreateSampleDto {
  @ApiProperty({ description: "Experiment ID" })
  @IsUUID()
  experimentId: string;

  @ApiPropertyOptional({ description: "Plot ID" })
  @IsUUID()
  @IsOptional()
  plotId?: string;

  @ApiPropertyOptional({ description: "Log ID" })
  @IsUUID()
  @IsOptional()
  logId?: string;

  @ApiProperty({ description: "Sample code (unique identifier)" })
  @IsString()
  sampleCode: string;

  @ApiProperty({ enum: SampleType, description: "Sample type" })
  @IsEnum(SampleType)
  type: SampleType;

  @ApiPropertyOptional({ description: "Description" })
  @IsString()
  @IsOptional()
  description?: string;

  @ApiPropertyOptional({ description: "Arabic description" })
  @IsString()
  @IsOptional()
  descriptionAr?: string;

  @ApiProperty({ description: "Collection date" })
  @IsDateString()
  collectionDate: string;

  @ApiPropertyOptional({ description: "Collection time (HH:MM:SS)" })
  @IsString()
  @IsOptional()
  collectionTime?: string;

  @ApiProperty({ description: "Collected by user ID" })
  @IsString()
  collectedBy: string;

  @ApiPropertyOptional({ description: "Storage location" })
  @IsString()
  @IsOptional()
  storageLocation?: string;

  @ApiPropertyOptional({ description: "Storage conditions" })
  @IsString()
  @IsOptional()
  storageConditions?: string;

  @ApiPropertyOptional({ description: "Quantity", type: Number })
  @IsNumber()
  @IsOptional()
  quantity?: number;

  @ApiPropertyOptional({ description: "Quantity unit" })
  @IsString()
  @IsOptional()
  quantityUnit?: string;

  @ApiPropertyOptional({ description: "Analysis status" })
  @IsString()
  @IsOptional()
  analysisStatus?: string;

  @ApiPropertyOptional({ description: "Analysis results as JSON object" })
  @IsObject()
  @IsOptional()
  analysisResults?: Record<string, unknown>;

  @ApiPropertyOptional({ description: "Analyzed by user ID" })
  @IsString()
  @IsOptional()
  analyzedBy?: string;

  @ApiPropertyOptional({ description: "Analysis date" })
  @IsDateString()
  @IsOptional()
  analyzedAt?: string;

  @ApiPropertyOptional({ description: "Photo URLs" })
  @IsArray()
  @IsString({ each: true })
  @IsOptional()
  photos?: string[];

  @ApiPropertyOptional({ description: "Additional metadata as JSON object" })
  @IsObject()
  @IsOptional()
  metadata?: Record<string, unknown>;
}

export class UpdateSampleDto extends PartialType(CreateSampleDto) {
  @ApiPropertyOptional({ description: "Experiment ID" })
  @IsUUID()
  @IsOptional()
  experimentId?: string;
}
