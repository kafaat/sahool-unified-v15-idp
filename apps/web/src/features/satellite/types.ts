/**
 * Satellite Feature - Types
 * أنواع ميزة صور الأقمار الصناعية
 */

export type HealthStatus = "excellent" | "good" | "moderate" | "poor" | "critical";
export type IndexType = "ndvi" | "ndwi" | "evi" | "lai" | "ndre" | "savi";

export interface SatelliteField {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  area: number;
  coordinates: {
    lat: number;
    lng: number;
  };
  boundary?: Array<{ lat: number; lng: number }>;
  lastCapture: string;
  lastCaptureSource: string;
  cloudCoverage?: number;
  indices: {
    ndvi: number;
    ndviChange: number;
    ndwi?: number;
    evi?: number;
    savi?: number;
    ndre?: number;
    lai?: number;
  };
  healthStatus: HealthStatus;
  healthScore: number;
  alerts?: string[];
  metadata: Record<string, unknown>;
  updatedAt: string;
}

export interface SatelliteImage {
  id: string;
  fieldId: string;
  captureDate: string;
  source: "sentinel-2" | "landsat-8" | "planet" | "drone";
  cloudCoverage: number;
  resolution: number;
  indexType: IndexType;
  imageUrl: string;
  thumbnailUrl: string;
  processingStatus: "pending" | "processing" | "completed" | "failed";
  metadata: Record<string, unknown>;
}

export interface SatelliteFilters {
  fieldId?: string;
  indexType?: IndexType;
  healthStatus?: HealthStatus;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface TimeSeriesData {
  date: string;
  value: number;
  source?: string;
}

export interface SatelliteStats {
  totalFields: number;
  averageNdvi: number;
  ndviTrend: "up" | "down" | "stable";
  lastCapture: string;
  fieldsMonitored: number;
  alertsCount: number;
  healthDistribution: Record<HealthStatus, number>;
  totalArea: number;
}

export interface ZoneAnalysis {
  id: string;
  fieldId: string;
  zoneName: string;
  zoneNameAr: string;
  area: number;
  ndvi: number;
  healthStatus: HealthStatus;
  recommendation?: string;
  recommendationAr?: string;
}
