export type SchedulerStatus = 'completed' | 'missed' | 'skipped' | 'retry_pending' | 'failed';
export type SchedulerPeriod = '7d' | '30d' | '90d';

export interface IndexValues {
  mean: number;
  min: number;
  max: number;
  std: number;
}

export interface SchedulerLogEntry {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  acquisitionDate: string;
  processedAt: string | null;
  satellite: string;
  cloudCoverPercent: number;
  status: SchedulerStatus;
  indices: {
    ndvi: IndexValues | null;
    evi: IndexValues | null;
    lai: IndexValues | null;
    ndwi: IndexValues | null;
  };
  errorMessage: string | null;
  retryCount: number;
  geotiffUrl: string | null;
  pngUrl: string | null;
}

export interface SchedulerStats {
  totalRuns: number;
  successfulRuns: number;
  failedRuns: number;
  missedRuns: number;
  successRate: number;
  lastRunAt: string | null;
  nextRunAt: string | null;
  totalFieldsProcessed: number;
  averageCloudCover: number;
  period: SchedulerPeriod;
}

export interface SchedulerLogsResponse {
  logs: SchedulerLogEntry[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface SchedulerFilters {
  period?: SchedulerPeriod;
  status?: SchedulerStatus | 'all';
  search?: string;
  page?: number;
  limit?: number;
}
