import { ApiProperty, ApiPropertyOptional, PartialType } from "@nestjs/swagger";
import {
  IsString,
  IsOptional,
  IsUUID,
  IsEnum,
  IsBoolean,
  IsObject,
  IsDateString,
} from "class-validator";

export enum TreatmentType {
  FERTILIZER = "fertilizer",
  PESTICIDE = "pesticide",
  IRRIGATION = "irrigation",
  SEED_VARIETY = "seed_variety",
  OTHER = "other",
}

export class CreateTreatmentDto {
  @ApiProperty({ description: "Experiment ID" })
  @IsUUID()
  experimentId: string;

  @ApiPropertyOptional({ description: "Plot ID" })
  @IsUUID()
  @IsOptional()
  plotId?: string;

  @ApiProperty({ description: "Treatment code" })
  @IsString()
  treatmentCode: string;

  @ApiProperty({ description: "Treatment name" })
  @IsString()
  name: string;

  @ApiPropertyOptional({ description: "Arabic name" })
  @IsString()
  @IsOptional()
  nameAr?: string;

  @ApiProperty({ enum: TreatmentType, description: "Treatment type" })
  @IsEnum(TreatmentType)
  type: TreatmentType;

  @ApiPropertyOptional({ description: "Description" })
  @IsString()
  @IsOptional()
  description?: string;

  @ApiPropertyOptional({ description: "Arabic description" })
  @IsString()
  @IsOptional()
  descriptionAr?: string;

  @ApiPropertyOptional({ description: "Dosage amount" })
  @IsString()
  @IsOptional()
  dosage?: string;

  @ApiPropertyOptional({ description: "Dosage unit" })
  @IsString()
  @IsOptional()
  dosageUnit?: string;

  @ApiPropertyOptional({ description: "Application method" })
  @IsString()
  @IsOptional()
  applicationMethod?: string;

  @ApiPropertyOptional({ description: "Application frequency" })
  @IsString()
  @IsOptional()
  applicationFrequency?: string;

  @ApiPropertyOptional({ description: "Start date" })
  @IsDateString()
  @IsOptional()
  startDate?: string;

  @ApiPropertyOptional({ description: "End date" })
  @IsDateString()
  @IsOptional()
  endDate?: string;

  @ApiPropertyOptional({ description: "Is this a control treatment?" })
  @IsBoolean()
  @IsOptional()
  isControl?: boolean;

  @ApiPropertyOptional({ description: "Additional parameters as JSON object" })
  @IsObject()
  @IsOptional()
  parameters?: Record<string, unknown>;
}

export class UpdateTreatmentDto extends PartialType(CreateTreatmentDto) {
  @ApiPropertyOptional({ description: "Experiment ID" })
  @IsUUID()
  @IsOptional()
  experimentId?: string;
}
