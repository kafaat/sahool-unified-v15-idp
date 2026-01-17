/**
 * SAHOOL Agricultural Monitoring Types
 * أنواع الرصد الزراعي
 *
 * Based on Remote Sensing + AI Agricultural Monitoring Products:
 * 1. Crop Distribution and Area Monitoring
 * 2. Economic Crop Distribution Monitoring
 * 3. Crop Growth Monitoring
 * 4. Crop Maturity Monitoring
 * 5. Seedling Status Monitoring
 * 6. Crop Yield Estimation
 */

// ═══════════════════════════════════════════════════════════════════════════
// Common Types
// ═══════════════════════════════════════════════════════════════════════════

export type DataSource = "sentinel-2" | "landsat-8" | "modis" | "gee" | "copernicus" | "mock";

export type Resolution = "high" | "medium" | "low"; // 1-3m, 10-16m, 30m

export interface GeoCoordinates {
  latitude: number;
  longitude: number;
}

export interface BoundingBox {
  minLat: number;
  minLon: number;
  maxLat: number;
  maxLon: number;
}

export interface MonitoringMetadata {
  dataSource: DataSource;
  resolution: Resolution;
  resolutionMeters: number;
  acquisitionDate: string;
  cloudCoverPercent: number;
  confidenceScore: number; // 0-100
  processingDate: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 1. Crop Distribution and Area Monitoring
// توزيع المحاصيل ورصد المساحة
// ═══════════════════════════════════════════════════════════════════════════

export type MainCropType =
  | "wheat"      // القمح
  | "corn"       // الذرة
  | "rice"       // الأرز
  | "soybean"    // فول الصويا
  | "cotton"     // القطن
  | "sorghum"    // الذرة الرفيعة
  | "barley"     // الشعير
  | "millet";    // الدخن

export interface CropDistribution {
  id: string;
  regionId: string;
  regionName: string;
  regionNameAr: string;
  cropType: MainCropType;
  cropNameAr: string;
  cropNameEn: string;
  areaHectares: number;
  percentageOfTotal: number;
  boundingBox: BoundingBox;
  centroid: GeoCoordinates;
  metadata: MonitoringMetadata;
  seasonYear: number;
  seasonType: "winter" | "summer" | "perennial";
}

export interface CropAreaMonitoringResult {
  success: boolean;
  regionId: string;
  totalAreaHectares: number;
  crops: CropDistribution[];
  accuracyPercent: number; // 85-95%
  updateFrequency: "monthly" | "seasonal";
  lastUpdated: string;
  nextUpdateExpected: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 2. Economic Crop Distribution Monitoring
// توزيع المحاصيل الاقتصادية المميزة
// ═══════════════════════════════════════════════════════════════════════════

export type EconomicCropType =
  | "tea"           // الشاي
  | "oil_tea"       // الشاي الزيتي
  | "sugarcane"     // قصب السكر
  | "tobacco"       // التبغ
  | "coffee"        // البن
  | "dates"         // التمور
  | "grapes"        // العنب
  | "mango"         // المانجو
  | "citrus"        // الحمضيات
  | "olives"        // الزيتون
  | "qat";          // القات

export interface EconomicCropDistribution {
  id: string;
  regionId: string;
  regionName: string;
  regionNameAr: string;
  cropType: EconomicCropType;
  cropNameAr: string;
  cropNameEn: string;
  areaHectares: number;
  estimatedValue: number; // USD
  valueCurrency: string;
  qualityGrade: "A" | "B" | "C";
  boundingBox: BoundingBox;
  centroid: GeoCoordinates;
  metadata: MonitoringMetadata;
  harvestSeason: string;
}

export interface EconomicCropMonitoringResult {
  success: boolean;
  regionId: string;
  totalAreaHectares: number;
  totalEstimatedValue: number;
  crops: EconomicCropDistribution[];
  accuracyPercent: number; // 95%
  updateFrequency: "seasonal";
  lastUpdated: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 3. Crop Growth Monitoring
// مراقبة نمو المحاصيل
// ═══════════════════════════════════════════════════════════════════════════

export type GrowthLevel = 1 | 2 | 3 | 4 | 5;

export type GrowthStatus =
  | "very_poor"   // سيئ جداً
  | "poor"        // سيئ
  | "normal"      // طبيعي
  | "good"        // جيد
  | "excellent";  // ممتاز

export interface GrowthIndicators {
  ndvi: number;        // Normalized Difference Vegetation Index
  evi: number;         // Enhanced Vegetation Index
  lai: number;         // Leaf Area Index
  chlorophyllContent: number;
  waterStressIndex: number;
}

export interface CropGrowthStatus {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  growthLevel: GrowthLevel;
  growthStatus: GrowthStatus;
  growthStatusAr: string;
  indicators: GrowthIndicators;
  comparisonToHistorical: number; // percentage +/-
  riskAlerts: RiskAlert[];
  recommendations: string[];
  recommendationsAr: string[];
  metadata: MonitoringMetadata;
  observationDate: string;
}

export interface RiskAlert {
  id: string;
  type: "disease" | "pest" | "nutrient_deficiency" | "water_stress" | "heat_stress";
  severity: "low" | "medium" | "high" | "critical";
  titleEn: string;
  titleAr: string;
  descriptionEn: string;
  descriptionAr: string;
  affectedAreaPercent: number;
  detectedAt: string;
  recommendedAction: string;
  recommendedActionAr: string;
}

export interface CropGrowthMonitoringResult {
  success: boolean;
  fieldId: string;
  currentStatus: CropGrowthStatus;
  historicalStatuses: CropGrowthStatus[];
  trend: "improving" | "stable" | "declining";
  accuracyPercent: number; // 85%
  updateFrequency: "10_days";
  lastUpdated: string;
  nextUpdateExpected: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 4. Crop Maturity Monitoring
// رصد نضج المحاصيل
// ═══════════════════════════════════════════════════════════════════════════

export type MaturityStage =
  | "vegetative"      // نمو خضري
  | "flowering"       // إزهار
  | "fruit_set"       // عقد الثمار
  | "development"     // تطور
  | "maturation"      // نضج
  | "harvest_ready";  // جاهز للحصاد

export interface MaturityIndex {
  value: number;           // 0-100
  stage: MaturityStage;
  stageAr: string;
  daysToOptimalHarvest: number;
  optimalHarvestWindow: {
    start: string;
    end: string;
  };
}

export interface CropMaturityStatus {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  maturityIndex: MaturityIndex;
  qualityPrediction: "A" | "B" | "C";
  qualityFactors: {
    moistureContent: number;
    sugarContent?: number;
    proteinContent?: number;
    oilContent?: number;
  };
  harvestRecommendation: string;
  harvestRecommendationAr: string;
  weatherRisk: {
    rainProbability: number;
    frostRisk: boolean;
    heatWaveRisk: boolean;
  };
  metadata: MonitoringMetadata;
  observationDate: string;
}

export interface CropMaturityMonitoringResult {
  success: boolean;
  fieldId: string;
  currentStatus: CropMaturityStatus;
  projectedHarvestDate: string;
  accuracyPercent: number; // 85%
  updateFrequency: "10_days";
  lastUpdated: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 5. Seedling Status Monitoring
// رصد حالة النباتات (الشتلات)
// ═══════════════════════════════════════════════════════════════════════════

export type SeedlingLevel = 1 | 2 | 3 | 4;

export type SeedlingStatus =
  | "weak"           // شتلات ضعيفة - تدخل فوري مطلوب
  | "moderate"       // شتلات متوسطة - مراقبة مستمرة
  | "good"           // شتلات جيدة - صيانة عادية
  | "excellent";     // شتلات ممتازة - نمو مزدهر

export interface SeedlingCondition {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  seedlingLevel: SeedlingLevel;
  seedlingStatus: SeedlingStatus;
  seedlingStatusAr: string;
  emergenceRate: number;        // percentage of expected seedlings
  uniformityScore: number;      // 0-100
  densityPerSquareMeter: number;
  soilMoistureStatus: "critical" | "low" | "optimal" | "high";
  soilMoistureStatusAr: string;
  earlyDiseaseRisk: {
    detected: boolean;
    type?: string;
    severity?: "low" | "medium" | "high";
    affectedAreaPercent?: number;
  };
  earlyPestRisk: {
    detected: boolean;
    type?: string;
    severity?: "low" | "medium" | "high";
    affectedAreaPercent?: number;
  };
  interventionRequired: boolean;
  interventionType?: "irrigation" | "fertilization" | "pest_control" | "replanting";
  recommendations: string[];
  recommendationsAr: string[];
  metadata: MonitoringMetadata;
  observationDate: string;
}

export interface SeedlingMonitoringResult {
  success: boolean;
  fieldId: string;
  currentCondition: SeedlingCondition;
  historicalConditions: SeedlingCondition[];
  trend: "improving" | "stable" | "declining";
  updateFrequency: "8_to_10_days";
  lastUpdated: string;
  nextUpdateExpected: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 6. Crop Yield Estimation
// تقديرات إنتاج المحاصيل
// ═══════════════════════════════════════════════════════════════════════════

export interface YieldInputs {
  satelliteNdvi: number[];
  weatherData: {
    temperatureMin: number[];
    temperatureMax: number[];
    precipitation: number;
    et0?: number;
  };
  soilProperties: {
    type: string;
    ph: number;
    organicMatter: number;
    nitrogen: number;
    phosphorus: number;
    potassium: number;
  };
  plantedAreaHa: number;
  cropType: string;
  plantingDate: string;
  irrigationType: "rainfed" | "drip" | "sprinkler" | "flood";
}

export interface YieldEstimate {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropNameAr: string;
  estimatedYieldTons: number;
  confidenceInterval: {
    min: number;
    max: number;
  };
  yieldPerHectare: number;
  comparisonToAverage: number;      // percentage +/-
  comparisonToLastYear?: number;    // percentage +/-
  yieldFactors: {
    vegetationHealth: number;       // 0-1
    biomassAccumulation: number;    // 0-1
    thermalTime: number;            // 0-1
    waterAvailability: number;      // 0-1
    soilQuality: number;            // 0-1
  };
  riskFactors: string[];
  riskFactorsAr: string[];
  recommendations: string[];
  recommendationsAr: string[];
  metadata: MonitoringMetadata;
  estimationDate: string;
  expectedHarvestDate: string;
}

export interface YieldEstimationResult {
  success: boolean;
  fieldId: string;
  currentEstimate: YieldEstimate;
  historicalEstimates: YieldEstimate[];
  accuracyPercent: number; // 80%
  updateFrequency: "critical_stage";
  lastUpdated: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Integrated Monitoring Dashboard Types
// ═══════════════════════════════════════════════════════════════════════════

export interface FieldMonitoringSummary {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  areaHectares: number;
  currentGrowthStatus: GrowthStatus;
  currentGrowthLevel: GrowthLevel;
  maturityPercent: number;
  seedlingStatus?: SeedlingStatus;
  estimatedYieldTons?: number;
  activeAlerts: RiskAlert[];
  lastUpdated: string;
  overallHealthScore: number; // 0-100
}

export interface RegionMonitoringSummary {
  regionId: string;
  regionName: string;
  regionNameAr: string;
  totalFields: number;
  totalAreaHectares: number;
  cropBreakdown: {
    cropType: string;
    cropNameAr: string;
    areaHectares: number;
    fieldCount: number;
    averageGrowthLevel: number;
  }[];
  alertsSummary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  estimatedTotalYieldTons: number;
  lastUpdated: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════

export interface GetCropDistributionRequest {
  regionId: string;
  seasonYear?: number;
  cropTypes?: MainCropType[];
}

export interface GetCropGrowthRequest {
  fieldId: string;
  startDate?: string;
  endDate?: string;
  includeHistory?: boolean;
}

export interface GetMaturityStatusRequest {
  fieldId: string;
  cropType?: string;
}

export interface GetSeedlingStatusRequest {
  fieldId: string;
  daysAfterPlanting?: number;
}

export interface GetYieldEstimateRequest {
  fieldId: string;
  inputs?: Partial<YieldInputs>;
}

export interface MonitoringApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  errorAr?: string;
  message?: string;
  messageAr?: string;
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Vegetation Indices Types (for SAHOOL integration)
// ═══════════════════════════════════════════════════════════════════════════

export interface VegetationIndices {
  ndvi: number;   // Normalized Difference Vegetation Index
  evi: number;    // Enhanced Vegetation Index
  savi: number;   // Soil Adjusted Vegetation Index
  lai: number;    // Leaf Area Index
  ndwi?: number;  // Normalized Difference Water Index
  ndmi?: number;  // Normalized Difference Moisture Index
}

export interface SpectralBands {
  red: number;
  nir: number;
  blue?: number;
  green?: number;
  swir1?: number;
  swir2?: number;
}

export interface SatelliteObservation {
  id: string;
  fieldId: string;
  observationDate: string;
  dataSource: DataSource;
  cloudCoverPercent: number;
  bands: SpectralBands;
  indices: VegetationIndices;
  qualityScore: number;
  metadata: Record<string, unknown>;
}
