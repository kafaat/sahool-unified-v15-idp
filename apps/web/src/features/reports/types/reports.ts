/**
 * Reports Feature - Type Definitions
 * تعريفات أنواع ميزة التقارير
 */

// ═══════════════════════════════════════════════════════════════════════════
// Report Type Enums
// ═══════════════════════════════════════════════════════════════════════════

export type ReportType = 'field' | 'season' | 'scouting' | 'tasks' | 'ndvi' | 'weather' | 'comprehensive';

export type ReportFormat = 'pdf' | 'excel' | 'csv' | 'json';

export type ReportStatus = 'pending' | 'generating' | 'ready' | 'failed' | 'expired';

export type ReportSection =
  | 'field_info'
  | 'ndvi_trend'
  | 'health_zones'
  | 'tasks_summary'
  | 'weather_summary'
  | 'recommendations'
  | 'crop_stages'
  | 'yield_estimate'
  | 'input_summary'
  | 'cost_analysis'
  | 'pest_disease'
  | 'soil_analysis';

export type ShareMethod = 'link' | 'email' | 'whatsapp' | 'download';

// ═══════════════════════════════════════════════════════════════════════════
// Field Report Types
// ═══════════════════════════════════════════════════════════════════════════

export interface FieldReportOptions {
  fieldId: string;
  startDate?: string;
  endDate?: string;
  sections: ReportSection[];
  includeCharts?: boolean;
  includeMaps?: boolean;
  format?: ReportFormat;
  language?: 'ar' | 'en' | 'both';
}

export interface FieldReportData {
  field: {
    id: string;
    name: string;
    nameAr: string;
    area: number;
    location: {
      latitude: number;
      longitude: number;
      governorate: string;
      governorateAr: string;
    };
    cropType: string;
    cropTypeAr: string;
    plantingDate: string;
    harvestDate?: string;
  };
  ndviTrend?: {
    dates: string[];
    values: number[];
    average: number;
    trend: 'increasing' | 'decreasing' | 'stable';
  };
  healthZones?: {
    healthy: number;
    moderate: number;
    stressed: number;
    critical: number;
  };
  recentTasks?: Array<{
    id: string;
    title: string;
    titleAr: string;
    type: string;
    status: string;
    completedAt?: string;
  }>;
  weatherSummary?: {
    avgTemperature: number;
    totalRainfall: number;
    avgHumidity: number;
    avgWindSpeed: number;
  };
  recommendations?: Array<{
    id: string;
    type: string;
    priority: 'high' | 'medium' | 'low';
    title: string;
    titleAr: string;
    description: string;
    descriptionAr: string;
  }>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Season Report Types
// ═══════════════════════════════════════════════════════════════════════════

export interface SeasonReportOptions {
  fieldId: string;
  season: string; // e.g., "2024-spring" or custom date range
  startDate?: string;
  endDate?: string;
  sections: ReportSection[];
  includeCharts?: boolean;
  format?: ReportFormat;
  language?: 'ar' | 'en' | 'both';
}

export interface SeasonReportData {
  season: {
    name: string;
    nameAr: string;
    startDate: string;
    endDate: string;
    duration: number; // days
  };
  field: {
    id: string;
    name: string;
    nameAr: string;
    area: number;
    cropType: string;
    cropTypeAr: string;
  };
  cropStages?: Array<{
    stage: string;
    stageAr: string;
    startDate: string;
    endDate?: string;
    duration: number;
    healthScore: number;
  }>;
  yieldEstimate?: {
    estimated: number;
    actual?: number;
    unit: string;
    confidence: number;
    perHectare: number;
  };
  inputSummary?: {
    water: {
      total: number;
      unit: string;
      avgPerWeek: number;
      cost?: number;
    };
    fertilizer: {
      total: number;
      unit: string;
      types: Array<{
        type: string;
        amount: number;
        cost?: number;
      }>;
    };
    pesticides?: {
      total: number;
      applications: number;
      cost?: number;
    };
  };
  costAnalysis?: {
    totalCost: number;
    costBreakdown: {
      seeds?: number;
      water: number;
      fertilizer: number;
      pesticides: number;
      labor: number;
      equipment: number;
      other: number;
    };
    revenue?: number;
    profit?: number;
    roi?: number; // Return on Investment percentage
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Generated Report Types
// ═══════════════════════════════════════════════════════════════════════════

export interface GeneratedReport {
  id: string;
  type: ReportType;
  format: ReportFormat;
  status: ReportStatus;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  title: string;
  titleAr: string;
  startDate: string;
  endDate: string;
  sections: ReportSection[];
  downloadUrl?: string;
  shareUrl?: string;
  fileSize?: number; // bytes
  pageCount?: number;
  createdAt: string;
  completedAt?: string;
  expiresAt?: string;
  createdBy?: string;
  language: 'ar' | 'en' | 'both';
  metadata?: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Report History Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ReportHistoryFilters {
  fieldId?: string;
  type?: ReportType;
  status?: ReportStatus;
  startDate?: string;
  endDate?: string;
  search?: string;
}

export interface ReportHistoryItem extends GeneratedReport {
  thumbnailUrl?: string;
  downloadCount?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Report Generation Request Types
// ═══════════════════════════════════════════════════════════════════════════

export interface GenerateFieldReportRequest {
  fieldId: string;
  startDate?: string;
  endDate?: string;
  sections: ReportSection[];
  options?: {
    includeCharts?: boolean;
    includeMaps?: boolean;
    includeRecommendations?: boolean;
    format?: ReportFormat;
    language?: 'ar' | 'en' | 'both';
    title?: string;
    titleAr?: string;
  };
}

export interface GenerateSeasonReportRequest {
  fieldId: string;
  season?: string;
  startDate?: string;
  endDate?: string;
  sections: ReportSection[];
  options?: {
    includeCharts?: boolean;
    includeCostAnalysis?: boolean;
    includeYieldEstimate?: boolean;
    format?: ReportFormat;
    language?: 'ar' | 'en' | 'both';
    title?: string;
    titleAr?: string;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Report Preview Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ReportPreviewData {
  reportId: string;
  pages: Array<{
    pageNumber: number;
    thumbnailUrl?: string;
    content: unknown; // Can be HTML or other renderable content
  }>;
  totalPages: number;
  canShare: boolean;
  canDownload: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Share Report Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ShareReportRequest {
  reportId: string;
  method: ShareMethod;
  recipients?: string[]; // email addresses or phone numbers
  message?: string;
  messageAr?: string;
  expiresIn?: number; // hours
}

export interface ShareReportResponse {
  success: boolean;
  shareUrl?: string;
  expiresAt?: string;
  message?: string;
  messageAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// PDF Generation Types
// ═══════════════════════════════════════════════════════════════════════════

export interface PDFGenerationOptions {
  language: 'ar' | 'en' | 'both';
  includeCharts: boolean;
  includeMaps: boolean;
  pageSize: 'A4' | 'Letter';
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  watermark?: {
    text: string;
    opacity: number;
  };
  footer?: {
    includePageNumbers: boolean;
    includeDate: boolean;
    customText?: string;
  };
}

export interface PDFChartConfig {
  type: 'line' | 'bar' | 'pie' | 'area';
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string;
    }>;
  };
  options?: {
    title?: string;
    titleAr?: string;
    width?: number;
    height?: number;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════════════════════════════════

export interface GenerateReportResponse {
  success: boolean;
  data?: GeneratedReport;
  error?: string;
  errorAr?: string;
}

export interface ReportHistoryResponse {
  success: boolean;
  data?: ReportHistoryItem[];
  total?: number;
  page?: number;
  limit?: number;
  error?: string;
  errorAr?: string;
}

export interface DownloadReportResponse {
  success: boolean;
  url?: string;
  expiresAt?: string;
  error?: string;
  errorAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Report Template Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ReportTemplateSection {
  section: ReportSection;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  required: boolean;
  order: number;
}

export interface ReportTemplate {
  type: ReportType;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  defaultSections: ReportTemplateSection[];
  supportedFormats: ReportFormat[];
  estimatedGenerationTime: number; // seconds
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages
// ═══════════════════════════════════════════════════════════════════════════

export interface BilingualMessage {
  en: string;
  ar: string;
}

export interface ReportErrorMessages {
  GENERATION_FAILED: BilingualMessage;
  DOWNLOAD_FAILED: BilingualMessage;
  SHARE_FAILED: BilingualMessage;
  DELETE_FAILED: BilingualMessage;
  INVALID_DATA: BilingualMessage;
  NOT_FOUND: BilingualMessage;
  EXPIRED: BilingualMessage;
  UNAUTHORIZED: BilingualMessage;
  NO_DATA: BilingualMessage;
  NETWORK_ERROR: BilingualMessage;
}
