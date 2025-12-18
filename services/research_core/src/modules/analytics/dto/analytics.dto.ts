import { IsString, IsOptional, IsDateString, IsEnum, IsNumber, Min, Max } from 'class-validator';

export enum AnalyticsPeriod {
  DAY = 'day',
  WEEK = 'week',
  MONTH = 'month',
  QUARTER = 'quarter',
  YEAR = 'year',
}

export enum KpiType {
  EXPERIMENT_PROGRESS = 'experiment_progress',
  LOG_COMPLETION = 'log_completion',
  SAMPLE_PROCESSING = 'sample_processing',
  DATA_INTEGRITY = 'data_integrity',
  FIELD_HEALTH = 'field_health',
  TASK_COMPLETION = 'task_completion',
}

export class AnalyticsQueryDto {
  @IsOptional()
  @IsString()
  experimentId?: string;

  @IsOptional()
  @IsString()
  farmId?: string;

  @IsOptional()
  @IsDateString()
  startDate?: string;

  @IsOptional()
  @IsDateString()
  endDate?: string;

  @IsOptional()
  @IsEnum(AnalyticsPeriod)
  period?: AnalyticsPeriod;

  @IsOptional()
  @IsString()
  groupBy?: string;
}

export class KpiQueryDto {
  @IsOptional()
  @IsString()
  experimentId?: string;

  @IsOptional()
  @IsString()
  farmId?: string;

  @IsOptional()
  @IsEnum(KpiType, { each: true })
  types?: KpiType[];

  @IsOptional()
  @IsDateString()
  asOfDate?: string;
}

export class ExportQueryDto {
  @IsString()
  experimentId: string;

  @IsOptional()
  @IsDateString()
  startDate?: string;

  @IsOptional()
  @IsDateString()
  endDate?: string;

  @IsOptional()
  @IsEnum(['csv', 'json', 'xlsx'])
  format?: 'csv' | 'json' | 'xlsx';

  @IsOptional()
  @IsString({ each: true })
  includeEntities?: string[];
}

export class TrendQueryDto {
  @IsString()
  metric: string;

  @IsOptional()
  @IsString()
  experimentId?: string;

  @IsOptional()
  @IsDateString()
  startDate?: string;

  @IsOptional()
  @IsDateString()
  endDate?: string;

  @IsOptional()
  @IsNumber()
  @Min(2)
  @Max(365)
  dataPoints?: number;
}
