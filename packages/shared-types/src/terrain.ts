/**
 * SAHOOL Terrain Service Types
 * أنواع خدمة التضاريس
 *
 * Type definitions for terrain analysis services including:
 * - Digital Elevation Model (DEM) analysis (تحليل نموذج الارتفاع الرقمي)
 * - Slope analysis (تحليل الميل)
 * - Aspect analysis (تحليل الاتجاه)
 * - Hydrological modeling (النمذجة الهيدرولوجية)
 * - Erosion risk assessment (تقييم مخاطر التعرية)
 */

// ═══════════════════════════════════════════════════════════════════════════
// Common Types
// الأنواع المشتركة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Digital Elevation Model data source
 */
export type DEMSource = 'copernicus' | 'srtm' | 'alos' | 'aster' | 'lidar' | 'local' | 'drone';

/**
 * Risk level classification
 */
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

/**
 * Resolution of terrain data
 */
export type TerrainResolution = '1m' | '5m' | '10m' | '30m' | '90m';

// ═══════════════════════════════════════════════════════════════════════════
// Elevation Types
// أنواع الارتفاع
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Elevation statistics for a field
 */
export interface ElevationStats {
  min: number; // meters above sea level
  max: number;
  mean: number;
  median: number;
  stdDev: number;
  range: number;
  percentile25: number;
  percentile75: number;
}

/**
 * Elevation profile along a transect
 */
export interface ElevationProfile {
  profileId: string;
  startPoint: {
    latitude: number;
    longitude: number;
  };
  endPoint: {
    latitude: number;
    longitude: number;
  };
  lengthMeters: number;
  sampleCount: number;
  samples: Array<{
    distance: number; // meters from start
    elevation: number; // meters
    latitude: number;
    longitude: number;
  }>;
  maxSlope: number; // degrees
  avgSlope: number;
  cumulativeGain: number; // meters
  cumulativeLoss: number; // meters
}

// ═══════════════════════════════════════════════════════════════════════════
// Slope Analysis Types
// أنواع تحليل الميل
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Slope classification
 */
export type SlopeClass =
  | 'flat' // مسطح (0-2°)
  | 'gentle' // منحدر خفيف (2-5°)
  | 'moderate' // معتدل (5-10°)
  | 'steep' // منحدر (10-20°)
  | 'very_steep' // شديد الانحدار (20-45°)
  | 'extreme'; // حاد جداً (>45°)

/**
 * Slope analysis result
 */
export interface SlopeAnalysis {
  min: number; // degrees
  max: number;
  mean: number;
  stdDev: number;
  distribution: {
    flat: number; // percentage of area
    gentle: number;
    moderate: number;
    steep: number;
    verysteep: number;
    extreme: number;
  };
  dominantClass: SlopeClass;
  dominantClassAr: string;
  suitableForMachinery: boolean;
  suitableForIrrigation: boolean;
  suitableForIrrigationAr: string;
  terraceRecommended: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Aspect Analysis Types
// أنواع تحليل الاتجاه
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Aspect direction (compass direction)
 */
export type AspectDirection =
  | 'flat' // مسطح
  | 'north' // شمال
  | 'northeast' // شمال شرق
  | 'east' // شرق
  | 'southeast' // جنوب شرق
  | 'south' // جنوب
  | 'southwest' // جنوب غرب
  | 'west' // غرب
  | 'northwest'; // شمال غرب

/**
 * Aspect analysis result
 */
export interface AspectAnalysis {
  dominantDirection: AspectDirection;
  dominantDirectionAr: string;
  dominantAngle: number; // degrees (0-360)
  distribution: {
    flat: number; // percentage of area
    north: number;
    northeast: number;
    east: number;
    southeast: number;
    south: number;
    southwest: number;
    west: number;
    northwest: number;
  };
  solarExposure: 'low' | 'medium' | 'high';
  solarExposureAr: string;
  frostRisk: 'low' | 'medium' | 'high';
  frostRiskAr: string;
  windExposure: 'sheltered' | 'moderate' | 'exposed';
  windExposureAr: string;
  recommendedCrops?: string[];
  recommendedCropsAr?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Hydrological Analysis Types
// أنواع التحليل الهيدرولوجي
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Flow accumulation analysis
 */
export interface FlowAnalysis {
  maxAccumulation: number; // number of cells
  drainageChannels: Array<{
    channelId: string;
    lengthMeters: number;
    startPoint: {
      latitude: number;
      longitude: number;
    };
    endPoint: {
      latitude: number;
      longitude: number;
    };
    avgAccumulation: number;
    order: number; // Strahler stream order
  }>;
  watershedArea: number; // hectares
  outletPoint?: {
    latitude: number;
    longitude: number;
  };
  flowDirection:
    | 'north'
    | 'northeast'
    | 'east'
    | 'southeast'
    | 'south'
    | 'southwest'
    | 'west'
    | 'northwest';
  flowDirectionAr: string;
  drainageDensity: number; // km/km²
}

/**
 * Topographic Wetness Index (TWI) analysis
 */
export interface TWIAnalysis {
  min: number;
  max: number;
  mean: number;
  stdDev: number;
  distribution: {
    veryDry: number; // percentage (TWI < 4)
    dry: number; // percentage (TWI 4-6)
    moderate: number; // percentage (TWI 6-8)
    wet: number; // percentage (TWI 8-10)
    veryWet: number; // percentage (TWI > 10)
  };
  waterloggingProneAreas: number; // percentage of field
  wellDrainedAreas: number; // percentage of field
  moistureRetentionIndex: number; // 0-100
}

// ═══════════════════════════════════════════════════════════════════════════
// Erosion Risk Types
// أنواع مخاطر التعرية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Erosion type classification
 */
export type ErosionType =
  | 'sheet' // تعرية سطحية
  | 'rill' // تعرية أخدودية صغيرة
  | 'gully' // تعرية أخدودية كبيرة
  | 'wind'; // تعرية ريحية

/**
 * Erosion risk assessment
 */
export interface ErosionRiskAssessment {
  overallRisk: RiskLevel;
  overallRiskAr: string;
  riskScore: number; // 0-100
  erosionTypes: Array<{
    type: ErosionType;
    typeAr: string;
    risk: RiskLevel;
    riskAr: string;
    affectedAreaPercent: number;
  }>;
  estimatedSoilLoss: number; // tons/ha/year (RUSLE model)
  kFactor: number; // soil erodibility factor
  lsFactor: number; // slope length and steepness factor
  cFactor: number; // cover management factor
  pFactor: number; // support practice factor
  mitigationRequired: boolean;
  mitigationMeasures?: string[];
  mitigationMeasuresAr?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Terrain Analysis Types
// أنواع تحليل التضاريس الرئيسية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Complete terrain analysis for a field
 */
export interface TerrainAnalysis {
  analysisId: string;
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  demSource: DEMSource;
  demSourceAr: string;
  resolution: TerrainResolution;
  resolutionMeters: number;
  elevation: ElevationStats;
  slope: SlopeAnalysis;
  aspect: AspectAnalysis;
  flowAccumulation: FlowAnalysis;
  twi: TWIAnalysis;
  erosionRisk: RiskLevel;
  erosionRiskAr: string;
  erosionAssessment: ErosionRiskAssessment;
  waterloggingRisk: RiskLevel;
  waterloggingRiskAr: string;
  requiresLeveling: boolean;
  levelingRecommendation?: string;
  levelingRecommendationAr?: string;
  drainageRequired: boolean;
  drainageRecommendation?: string;
  drainageRecommendationAr?: string;
  terracingRequired: boolean;
  terracingRecommendation?: string;
  terracingRecommendationAr?: string;
  analyzedAt: Date;
  dataQuality: 'high' | 'medium' | 'low';
  dataQualityAr: string;
  processingTimeMs: number;
}

/**
 * Terrain analysis summary (lightweight)
 */
export interface TerrainSummary {
  fieldId: string;
  avgElevation: number;
  avgSlope: number;
  dominantAspect: AspectDirection;
  erosionRisk: RiskLevel;
  waterloggingRisk: RiskLevel;
  requiresIntervention: boolean;
  lastAnalyzed: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Terrain Service Request/Response Types
// أنواع طلبات واستجابات خدمة التضاريس
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Terrain analysis request
 */
export interface TerrainAnalysisRequest {
  fieldId: string;
  demSource?: DEMSource;
  resolution?: TerrainResolution;
  includeErosionAssessment?: boolean;
  includeFlowAnalysis?: boolean;
  includeTWI?: boolean;
  customDEMUrl?: string;
  forceReanalysis?: boolean;
}

/**
 * Terrain analysis response
 */
export interface TerrainAnalysisResponse {
  success: boolean;
  analysis?: TerrainAnalysis;
  error?: string;
  errorAr?: string;
  warnings?: string[];
  warningsAr?: string[];
}

/**
 * Elevation profile request
 */
export interface ElevationProfileRequest {
  fieldId?: string;
  startPoint: {
    latitude: number;
    longitude: number;
  };
  endPoint: {
    latitude: number;
    longitude: number;
  };
  sampleCount?: number;
  demSource?: DEMSource;
}

/**
 * Multi-field terrain comparison
 */
export interface TerrainComparison {
  comparisonId: string;
  fields: Array<{
    fieldId: string;
    fieldName: string;
    fieldNameAr: string;
    summary: TerrainSummary;
  }>;
  bestForIrrigation: string; // field ID
  bestForMachinery: string; // field ID
  lowestErosionRisk: string; // field ID
  lowestWaterloggingRisk: string; // field ID
  overallRanking: Array<{
    fieldId: string;
    score: number;
    rank: number;
  }>;
  comparedAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Terrain-based Recommendations Types
// أنواع التوصيات المبنية على التضاريس
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Irrigation recommendation based on terrain
 */
export interface TerrainIrrigationRecommendation {
  fieldId: string;
  suitableIrrigationTypes: Array<{
    type: 'drip' | 'sprinkler' | 'flood' | 'pivot' | 'furrow';
    typeAr: string;
    suitabilityScore: number; // 0-100
    considerations: string[];
    considerationsAr: string[];
  }>;
  recommendedZones?: Array<{
    zoneId: string;
    areaHectares: number;
    irrigationType: string;
    justification: string;
    justificationAr: string;
  }>;
  waterFlowDirection: string;
  waterFlowDirectionAr: string;
  pumpingRequired: boolean;
  estimatedHeadLossMeters?: number;
}

/**
 * Land leveling recommendation
 */
export interface LandLevelingRecommendation {
  fieldId: string;
  required: boolean;
  urgency: 'low' | 'medium' | 'high';
  urgencyAr: string;
  estimatedCutVolume: number; // cubic meters
  estimatedFillVolume: number; // cubic meters
  estimatedCost?: number;
  estimatedCostCurrency?: string;
  expectedBenefits: string[];
  expectedBenefitsAr: string[];
  alternativeApproaches?: string[];
  alternativeApproachesAr?: string[];
}
