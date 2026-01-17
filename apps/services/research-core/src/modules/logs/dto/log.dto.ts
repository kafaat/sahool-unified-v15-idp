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

export enum LogCategory {
  OBSERVATION = "observation",
  MEASUREMENT = "measurement",
  TREATMENT = "treatment",
  HARVEST = "harvest",
  WEATHER = "weather",
  PEST = "pest",
  OTHER = "other",
}

export class CreateLogDto {
  @ApiProperty({ description: "Experiment ID" })
  @IsUUID()
  experimentId: string;

  @ApiPropertyOptional({ description: "Plot ID" })
  @IsUUID()
  @IsOptional()
  plotId?: string;

  @ApiPropertyOptional({ description: "Treatment ID" })
  @IsUUID()
  @IsOptional()
  treatmentId?: string;

  @ApiProperty({ description: "Log date" })
  @IsDateString()
  logDate: string;

  @ApiPropertyOptional({ description: "Log time (HH:MM:SS)" })
  @IsString()
  @IsOptional()
  logTime?: string;

  @ApiProperty({ enum: LogCategory })
  @IsEnum(LogCategory)
  category: LogCategory;

  @ApiProperty({ description: "Log title" })
  @IsString()
  title: string;

  @ApiPropertyOptional({ description: "Arabic title" })
  @IsString()
  @IsOptional()
  titleAr?: string;

  @ApiPropertyOptional({ description: "Notes" })
  @IsString()
  @IsOptional()
  notes?: string;

  @ApiPropertyOptional({ description: "Arabic notes" })
  @IsString()
  @IsOptional()
  notesAr?: string;

  @ApiPropertyOptional({ description: "Measurements data" })
  @IsObject()
  @IsOptional()
  measurements?: Record<string, unknown>;

  @ApiPropertyOptional({ description: "Weather conditions" })
  @IsObject()
  @IsOptional()
  weatherConditions?: Record<string, unknown>;

  @ApiPropertyOptional({ description: "Photo URLs" })
  @IsArray()
  @IsString({ each: true })
  @IsOptional()
  photos?: string[];

  @ApiPropertyOptional({ description: "Attachment URLs" })
  @IsArray()
  @IsString({ each: true })
  @IsOptional()
  attachments?: string[];

  @ApiPropertyOptional({ description: "Device ID for tracking" })
  @IsString()
  @IsOptional()
  deviceId?: string;

  @ApiPropertyOptional({ description: "Offline sync ID" })
  @IsString()
  @IsOptional()
  offlineId?: string;
}

export class UpdateLogDto extends PartialType(CreateLogDto) {}

export class SyncLogDto extends CreateLogDto {
  @ApiProperty({ description: "Offline ID for sync tracking" })
  @IsString()
  offlineId: string;
}
