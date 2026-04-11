import { ApiProperty, ApiPropertyOptional, PartialType } from "@nestjs/swagger";
import {
  IsString,
  IsOptional,
  IsDateString,
  IsArray,
  IsEnum,
  IsUUID,
  IsObject,
  IsInt,
  Min,
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

export class UpdateExperimentDto extends PartialType(CreateExperimentDto) {
  /**
   * Expected version for optimistic locking (CAS pattern).
   * If provided, the update will fail with 409 Conflict when the stored
   * row's `version` does not match this value — preventing lost updates
   * in concurrent edit scenarios.
   *
   * رقم النسخة المتوقع للقفل التفاؤلي - يمنع الكتابة فوق التعديلات المتزامنة
   */
  @ApiPropertyOptional({
    description:
      "Expected version for optimistic locking (CAS). If supplied, update fails with 409 on mismatch.",
    type: Number,
    minimum: 1,
  })
  @IsInt()
  @Min(1)
  @IsOptional()
  version?: number;
}
