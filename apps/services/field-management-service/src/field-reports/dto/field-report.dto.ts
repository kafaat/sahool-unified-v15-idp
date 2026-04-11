/**
 * FieldReport DTOs
 * نقل البيانات - تقارير الحقل
 */

import {
  IsString,
  IsOptional,
  IsUUID,
  IsIn,
  IsDateString,
  MaxLength,
} from "class-validator";

export const REPORT_TYPES = [
  "field_summary",
  "crop_season",
  "weather_history",
  "ndvi_timeseries",
  "operation_log",
  "carbon_footprint",
  "financial_summary",
] as const;
export type ReportType = (typeof REPORT_TYPES)[number];

export const REPORT_LANGUAGES = ["ar", "en"] as const;
export type ReportLanguage = (typeof REPORT_LANGUAGES)[number];

/**
 * Request to generate a new report. The actual rendering happens
 * asynchronously in a background worker; this DTO just enqueues the
 * request and the caller polls the resulting row until status = 'ready'.
 */
export class CreateFieldReportDto {
  @IsOptional()
  @IsString()
  @IsIn(REPORT_TYPES as unknown as string[])
  reportType?: ReportType;

  @IsOptional()
  @IsString()
  @IsIn(REPORT_LANGUAGES as unknown as string[])
  language?: ReportLanguage;

  @IsOptional()
  @IsDateString()
  periodFrom?: string;

  @IsOptional()
  @IsDateString()
  periodTo?: string;

  @IsOptional()
  @IsUUID()
  cropSeasonId?: string;
}

/**
 * Query filter for listing reports.
 */
export class QueryFieldReportsDto {
  @IsOptional()
  @IsString()
  @IsIn(REPORT_TYPES as unknown as string[])
  reportType?: ReportType;

  @IsOptional()
  @IsString()
  @IsIn(["pending", "rendering", "ready", "failed", "expired"])
  status?: string;

  @IsOptional()
  @IsUUID()
  cropSeasonId?: string;
}
