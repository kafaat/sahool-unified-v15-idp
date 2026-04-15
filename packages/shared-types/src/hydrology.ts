/**
 * SAHOOL Hydrology Service Types
 * أنواع خدمة الهيدرولوجيا
 *
 * Type definitions for hydrological analysis services including:
 * - Drainage network extraction (استخراج شبكة التصريف)
 * - Topographic Wetness Index (مؤشر الرطوبة الطبوغرافية)
 * - Depression detection (كشف المنخفضات)
 * - Basin delineation (تحديد الأحواض)
 * - Waterlogging prediction (التنبؤ بالتشبع المائي)
 *
 * @packageDocumentation
 * @module @sahool/shared-types/hydrology
 * @version 16.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════
// GeoJSON Types (local definitions for hydrology module)
// أنواع GeoJSON محلية لوحدة الهيدرولوجيا
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GeoJSON LineString geometry for drainage segments
 */
interface HydroLineString {
  type: 'LineString';
  coordinates: Array<[number, number]>; // [longitude, latitude] pairs
}

/**
 * GeoJSON Polygon geometry for basins and zones
 */
interface HydroPolygon {
  type: 'Polygon';
  coordinates: Array<Array<[number, number]>>;
}

/**
 * GeoJSON Feature for individual geographic features
 */
interface HydroFeature<G = HydroLineString | HydroPolygon, P = Record<string, unknown>> {
  type: 'Feature';
  geometry: G;
  properties: P;
}

/**
 * GeoJSON FeatureCollection for network and zone collections
 */
interface HydroFeatureCollection<G = HydroLineString | HydroPolygon, P = Record<string, unknown>> {
  type: 'FeatureCollection';
  features: Array<HydroFeature<G, P>>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Common Types
// الأنواع المشتركة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Flow direction algorithms
 */
export type FlowDirectionMethod = 'd8' | 'dinf' | 'mfd';

/**
 * Risk level for waterlogging and depression
 */
export type WaterloggingRisk = 'low' | 'medium' | 'high' | 'critical';

/**
 * Depression risk level
 */
export type DepressionRisk = 'low' | 'medium' | 'high' | 'critical';

/**
 * Stream order classification (Strahler method)
 */
export type StreamOrder = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;

/**
 * Basin size classification
 */
export type BasinSize = 'micro' | 'small' | 'medium' | 'large' | 'major';

// ═══════════════════════════════════════════════════════════════════════════
// Drainage Network Types
// أنواع شبكة التصريف
// ═══════════════════════════════════════════════════════════════════════════

/**
 * A single drainage segment
 */
export interface DrainageSegment {
  segmentId: string;
  streamOrder: StreamOrder;
  lengthMeters: number;
  avgSlopePercent: number;
  flowAccumulationMax: number;
  upstreamAreaHa: number;
  startPoint: {
    latitude: number;
    longitude: number;
    elevation: number;
  };
  endPoint: {
    latitude: number;
    longitude: number;
    elevation: number;
  };
  geometry: HydroLineString;
}

/**
 * Drainage network analysis result
 */
export interface DrainageNetworkResult {
  fieldId: string;
  tenantId?: string;
  analyzedAt: string; // ISO 8601 timestamp
  demSource: string;
  resolutionM: number;

  // Network statistics
  totalLengthM: number;
  totalLengthKm: number;
  drainageDensityKmPerKm2: number;
  mainChannelLengthM: number;
  maxStreamOrder: StreamOrder;

  // Segments
  segments: DrainageSegment[];
  segmentCount: number;

  // By stream order
  streamOrderStats: Array<{
    order: StreamOrder;
    count: number;
    totalLengthM: number;
    avgLengthM: number;
  }>;

  // GeoJSON for mapping
  networkGeoJson: HydroFeatureCollection;

  // Bilingual messages
  summaryEn: string;
  summaryAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Topographic Wetness Index (TWI) Types
// أنواع مؤشر الرطوبة الطبوغرافية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * TWI zone classification
 */
export interface TWIZone {
  zoneId: string;
  zoneName: string;
  zoneNameAr: string;
  twiMin: number;
  twiMax: number;
  twiMean: number;
  areaHa: number;
  areaPercent: number;
  waterloggingRisk: WaterloggingRisk;
  irrigationSuitability: 'excellent' | 'good' | 'moderate' | 'poor';
  recommendations: string[];
  recommendationsAr: string[];
}

/**
 * TWI analysis result
 */
export interface TWIAnalysisResult {
  fieldId: string;
  tenantId?: string;
  analyzedAt: string;
  demSource: string;
  resolutionM: number;

  // Statistics
  minTWI: number;
  maxTWI: number;
  meanTWI: number;
  stdTWI: number;
  medianTWI: number;

  // Classification
  highMoistureAreaPct: number;
  moderateMoistureAreaPct: number;
  lowMoistureAreaPct: number;

  // Zones
  zones: TWIZone[];

  // Interpretation
  interpretationEn: string;
  interpretationAr: string;

  // Recommendations
  recommendationsEn: string[];
  recommendationsAr: string[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Depression Detection Types
// أنواع كشف المنخفضات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * A detected depression (potential waterlogging area)
 */
export interface Depression {
  depressionId: string;
  centroid: {
    latitude: number;
    longitude: number;
  };
  areaM2: number;
  areaHa: number;
  depthM: number;
  volumeM3: number;
  perimeterM: number;
  compactnessIndex: number;
  risk: DepressionRisk;
  riskNameEn: string;
  riskNameAr: string;
  drainageTime: number; // hours to drain naturally
  requiresIntervention: boolean;
  geometry: HydroPolygon;
}

/**
 * Depression analysis result
 */
export interface DepressionAnalysisResult {
  fieldId: string;
  tenantId?: string;
  analyzedAt: string;
  demSource: string;
  resolutionM: number;

  // Summary
  totalDepressions: number;
  totalAreaHa: number;
  totalVolumeM3: number;
  fieldAreaHa: number;
  depressionPercentage: number;

  // By risk level
  criticalCount: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;

  // Depressions list
  depressions: Depression[];

  // Recommendations
  recommendationsEn: string[];
  recommendationsAr: string[];

  // Cost estimate for remediation (SAR)
  estimatedRemediationCostSAR: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Basin/Watershed Delineation Types
// أنواع تحديد الأحواض
// ═══════════════════════════════════════════════════════════════════════════

/**
 * A delineated watershed basin
 */
export interface Basin {
  basinId: string;
  name: string;
  nameAr: string;
  areaHa: number;
  areaKm2: number;
  perimeterKm: number;
  size: BasinSize;

  // Hydrological parameters
  meanSlope: number;
  reliefM: number;
  elongationRatio: number;
  circularityRatio: number;
  drainageDensity: number;

  // Outlet
  outlet: {
    latitude: number;
    longitude: number;
    elevation: number;
  };

  // Time of concentration (hours)
  timeOfConcentration: number;

  // Runoff potential
  runoffCoefficientMin: number;
  runoffCoefficientMax: number;

  geometry: HydroPolygon;
}

/**
 * Basin delineation result
 */
export interface BasinDelineationResult {
  fieldId: string;
  tenantId?: string;
  analyzedAt: string;
  demSource: string;
  resolutionM: number;

  // Summary
  totalBasins: number;
  totalAreaHa: number;

  // Basins
  basins: Basin[];

  // Main basin (largest)
  mainBasinId: string;

  // GeoJSON for mapping
  basinsGeoJson: HydroFeatureCollection;
}

// ═══════════════════════════════════════════════════════════════════════════
// Waterlogging Prediction Types
// أنواع التنبؤ بالتشبع المائي
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Waterlogging prediction for a zone
 */
export interface WaterloggingZone {
  zoneId: string;
  zoneName: string;
  zoneNameAr: string;
  risk: WaterloggingRisk;
  areaHa: number;

  // Prediction factors
  twiMean: number;
  slopePct: number;
  depthToWaterTableM: number;

  // Weather-based prediction
  rainfallThresholdMm: number; // Rainfall that triggers waterlogging
  predictedDurationHours: number;

  recommendations: string[];
  recommendationsAr: string[];

  geometry: HydroPolygon;
}

/**
 * Waterlogging prediction result
 */
export interface WaterloggingPredictionResult {
  fieldId: string;
  tenantId?: string;
  analyzedAt: string;

  // Weather context
  forecastRainfallMm: number;
  forecastPeriodDays: number;

  // Overall risk
  overallRisk: WaterloggingRisk;
  overallRiskNameEn: string;
  overallRiskNameAr: string;

  // Affected area
  totalAffectedAreaHa: number;
  affectedPercentage: number;

  // Zones
  zones: WaterloggingZone[];

  // Recommendations
  immediateActionsEn: string[];
  immediateActionsAr: string[];
  preventiveMeasuresEn: string[];
  preventiveMeasuresAr: string[];
}

// ═══════════════════════════════════════════════════════════════════════════
// API Request/Response Types
// أنواع طلبات واستجابات API
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Request for drainage network analysis
 */
export interface DrainageNetworkRequest {
  fieldId: string;
  tenantId?: string;
  demSource?: string;
  resolutionM?: number;
  flowAccumulationThreshold?: number;
  minStreamOrder?: StreamOrder;
}

/**
 * Request for TWI analysis
 */
export interface TWIAnalysisRequest {
  fieldId: string;
  tenantId?: string;
  demSource?: string;
  resolutionM?: number;
  highWetnessThreshold?: number;
}

/**
 * Request for depression detection
 */
export interface DepressionDetectionRequest {
  fieldId: string;
  tenantId?: string;
  demSource?: string;
  resolutionM?: number;
  minDepressionDepthM?: number;
  minDepressionAreaM2?: number;
}

/**
 * Request for basin delineation
 */
export interface BasinDelineationRequest {
  fieldId: string;
  tenantId?: string;
  demSource?: string;
  resolutionM?: number;
  minBasinAreaHa?: number;
}

/**
 * Request for waterlogging prediction
 */
export interface WaterloggingPredictionRequest {
  fieldId: string;
  tenantId?: string;
  forecastRainfallMm: number;
  forecastPeriodDays: number;
}

/**
 * Health check response
 */
export interface HydrologyHealthResponse {
  status: 'ok' | 'degraded' | 'error';
  service: 'hydrology-service';
  serviceAr: 'خدمة الهيدرولوجيا';
  version: string;
  timestamp: string;
  checks: {
    database: 'connected' | 'disconnected';
    nats: 'connected' | 'disconnected';
    terrainService: string;
    weatherService: string;
  };
}
