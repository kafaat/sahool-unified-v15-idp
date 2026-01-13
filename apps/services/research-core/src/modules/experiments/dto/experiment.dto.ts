import { ApiProperty, ApiPropertyOptional, PartialType } from "@nestjs/swagger";
import {
  IsString,
  IsOptional,
  IsDateString,
  IsArray,
  IsEnum,
  IsUUID,
  IsObject,
} from "class-validator";

export enum ExperimentStatus {
  DRAFT = "draft",
  ACTIVE = "active",
  LOCKED = "locked",
  COMPLETED = "completed",
  ARCHIVED = "archived",
}

export class CreateExperimentDto {
  @ApiProperty({ description: "Experiment title" })
  @IsString()
  title: string;

  @ApiPropertyOptional({ description: "Arabic title" })
  @IsString()
  @IsOptional()
  titleAr?: string;

  @ApiPropertyOptional({ description: "Description" })
  @IsString()
  @IsOptional()
  description?: string;

  @ApiPropertyOptional({ description: "Arabic description" })
  @IsString()
  @IsOptional()
  descriptionAr?: string;

  @ApiPropertyOptional({ description: "Hypothesis" })
  @IsString()
  @IsOptional()
  hypothesis?: string;

  @ApiPropertyOptional({ description: "Arabic hypothesis" })
  @IsString()
  @IsOptional()
  hypothesisAr?: string;

  @ApiProperty({ description: "Start date" })
  @IsDateString()
  startDate: string;

  @ApiPropertyOptional({ description: "End date" })
  @IsDateString()
  @IsOptional()
  endDate?: string;

  @ApiPropertyOptional({ enum: ExperimentStatus })
  @IsEnum(ExperimentStatus)
  @IsOptional()
  status?: ExperimentStatus;

  @ApiPropertyOptional({ description: "Organization ID" })
  @IsUUID()
  @IsOptional()
  organizationId?: string;

  @ApiPropertyOptional({ description: "Farm ID" })
  @IsUUID()
  @IsOptional()
  farmId?: string;

  @ApiPropertyOptional({ description: "Tags" })
  @IsArray()
  @IsString({ each: true })
  @IsOptional()
  tags?: string[];

  @ApiPropertyOptional({ description: "Additional metadata" })
  @IsObject()
  @IsOptional()
  metadata?: Record<string, unknown>;
}

export class UpdateExperimentDto extends PartialType(CreateExperimentDto) {}
