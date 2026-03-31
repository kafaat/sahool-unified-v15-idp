/**
 * Hydrology Feature - Types
 * أنواع ميزة الهيدرولوجيا
 */

// ═══════════════════════════════════════════════════════════════════════════
// Enums - التعدادات
// ═══════════════════════════════════════════════════════════════════════════

export type DrainageType =
  | 'dendritic'
  | 'parallel'
  | 'trellis'
  | 'rectangular'
  | 'radial'
  | 'centripetal'
  | 'deranged'
  | 'unknown';

export type WetnessLevel =
  | 'very_dry'
  | 'dry'
  | 'moderate'
  | 'wet'
  | 'very_wet'
  | 'waterlogged';

export type DepressionRisk = 'low' | 'medium' | 'high' | 'critical';

// ═══════════════════════════════════════════════════════════════════════════
// Base Types - الأنواع الأساسية
// ═══════════════════════════════════════════════════════════════════════════

export interface GeoPoint {
  lat: number;
  lon: number;
}

export interface GeoPolygon {
  coordinates: number[][];
  type: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Drainage - التصريف
// ═══════════════════════════════════════════════════════════════════════════

export interface DrainageSegment {
  segmentId: string;
  coordinates: number[][];
  streamOrder: number;
  lengthM: number;
  upstreamAreaHa: number;
  slopePercent: number;
}

export interface DrainageAnalysis {
  fieldId: string;
  totalLengthM: number;
  drainageDensity: number;
  mainChannelLengthM: number;
  bifurcationRatio: number;
  pattern: DrainageType;
  patternAr: string;
  segments: DrainageSegment[];
  statistics: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Wetness - الرطوبة
// ═══════════════════════════════════════════════════════════════════════════

export interface WetnessZone {
  zoneId: string;
  level: WetnessLevel;
  levelAr: string;
  areaHa: number;
  percentage: number;
  twiMean: number;
  twiRange: [number, number];
  polygon?: GeoPolygon;
  recommendationsAr: string[];
  recommendationsEn: string[];
}

export interface WaterloggingPrediction {
  rainfallMm: number;
  riskLevel: DepressionRisk;
  riskLevelAr: string;
  affectedAreaHa: number;
  affectedPercentage: number;
  timeToDrainHours?: number;
  mitigationAr: string[];
  mitigationEn: string[];
}

export interface WetnessAnalysis {
  fieldId: string;
  totalAreaHa: number;
  twiMean: number;
  twiStd: number;
  twiMin: number;
  twiMax: number;
  dominantLevel: WetnessLevel;
  dominantLevelAr: string;
  zones: WetnessZone[];
  waterloggingPrediction?: WaterloggingPrediction;
  irrigationEfficiencyScore: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Depressions - المنخفضات
// ═══════════════════════════════════════════════════════════════════════════

export interface Depression {
  depressionId: string;
  center: GeoPoint;
  depthM: number;
  areaSqm: number;
  volumeM3: number;
  perimeterM: number;
  riskLevel: DepressionRisk;
  riskLevelAr: string;
  boundary?: GeoPolygon;
  drainageRecommendationsAr: string[];
  drainageRecommendationsEn: string[];
}

export interface DepressionAnalysis {
  fieldId: string;
  totalDepressions: number;
  totalVolumeM3: number;
  totalAreaSqm: number;
  fieldAreaHa: number;
  depressionsPercentage: number;
  highRiskCount: number;
  criticalCount: number;
  depressions: Depression[];
  summaryAr: string;
  summaryEn: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Streams - المجاري المائية
// ═══════════════════════════════════════════════════════════════════════════

export interface Stream {
  streamId: string;
  order: number;
  coordinates: number[][];
  lengthM: number;
  avgSlopePercent: number;
  upstreamAreaHa: number;
  isPerennial: boolean;
}

export interface StreamNetwork {
  fieldId: string;
  totalStreams: number;
  totalLengthM: number;
  maxOrder: number;
  streamsByOrder: Record<number, number>;
  mainStreamLengthM: number;
  streams: Stream[];
  hydraulicGeometry: Record<string, number>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Basins - الأحواض
// ═══════════════════════════════════════════════════════════════════════════

export interface SubBasin {
  basinId: string;
  areaHa: number;
  perimeterM: number;
  centroid: GeoPoint;
  pourPoint: GeoPoint;
  meanElevationM: number;
  elevationRangeM: number;
  meanSlopePercent: number;
  timeOfConcentrationMin: number;
  boundary: GeoPolygon;
}

export interface BasinDelineation {
  fieldId: string;
  totalBasins: number;
  totalAreaHa: number;
  mainBasinAreaHa: number;
  outletPoint: GeoPoint;
  meanElevationM: number;
  reliefM: number;
  elongationRatio: number;
  circularityRatio: number;
  basins: SubBasin[];
  runoffCoefficient: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Full Analysis - التحليل الكامل
// ═══════════════════════════════════════════════════════════════════════════

export interface HydrologyAnalysisResult {
  fieldId: string;
  tenantId: string;
  analyzedAt: string;
  demSource: string;
  resolutionM: number;
  fieldAreaHa: number;
  meanElevationM: number;
  elevationRangeM: number;
  meanSlopePercent: number;
  drainage: DrainageAnalysis;
  wetness: WetnessAnalysis;
  depressions: DepressionAnalysis;
  streams: StreamNetwork;
  basins: BasinDelineation;
  floodRiskLevel: DepressionRisk;
  floodRiskLevelAr: string;
  drainageQualityScore: number;
  recommendationsAr: string[];
  recommendationsEn: string[];
  rainfallData?: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Request Parameters - معلمات الطلب
// ═══════════════════════════════════════════════════════════════════════════

export interface HydrologyAnalysisParams {
  fieldId: string;
  tenantId: string;
  boundary?: GeoPolygon;
  demSource?: string;
  resolutionM?: number;
  includeRainfall?: boolean;
  rainfallPeriodDays?: number;
}

export interface DrainageParams {
  flowThreshold?: number;
  includePattern?: boolean;
}

export interface WetnessParams {
  includePrediction?: boolean;
  rainfallMm?: number;
}

export interface DepressionParams {
  minDepthM?: number;
  minAreaSqm?: number;
}

export interface StreamParams {
  minOrder?: number;
}

export interface BasinParams {
  minAreaHa?: number;
}

export interface HydrologyFilters {
  fieldId?: string;
  analysisType?: string;
}
