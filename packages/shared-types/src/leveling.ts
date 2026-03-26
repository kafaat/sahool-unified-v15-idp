/**
 * SAHOOL Leveling Optimizer Service Types
 * أنواع خدمة تحسين التسوية
 *
 * Type definitions for field leveling optimization including:
 * - Cut/fill volume calculations (حسابات أحجام القطع والردم)
 * - Optimal grade plane computation (حساب مستوى الميل الأمثل)
 * - Equipment recommendations (توصيات المعدات)
 * - Cost estimation in SAR (تقدير التكلفة بالريال السعودي)
 * - Leveling simulation (محاكاة التسوية)
 *
 * @packageDocumentation
 * @module @sahool/shared-types/leveling
 * @version 16.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════
// Common Types
// الأنواع المشتركة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Equipment types for leveling operations
 */
export type EquipmentType =
  | 'bulldozer' // جرافة
  | 'scraper' // كاشطة
  | 'grader' // ممهدة
  | 'laser_leveler' // مسوي ليزر
  | 'excavator' // حفارة
  | 'dump_truck'; // شاحنة قلابة

/**
 * Soil types for leveling calculations
 * (Named LevelingSoilType to avoid conflict with field.ts SoilType)
 */
export type LevelingSoilType =
  | 'sandy' // رملية
  | 'loamy' // طفالية
  | 'clay' // طينية
  | 'silty' // طميية
  | 'rocky'; // صخرية

/**
 * Leveling methods
 */
export type LevelingMethod =
  | 'single_plane' // مستوى واحد
  | 'dual_plane' // مستويين
  | 'contour' // كنتوري
  | 'bench'; // مصاطب

/**
 * Leveling optimization priority
 */
export type LevelingPriority =
  | 'minimize_cost' // تقليل التكلفة
  | 'minimize_earthwork' // تقليل الحفر والردم
  | 'optimal_drainage' // تصريف مثالي
  | 'irrigation_efficiency'; // كفاءة الري

// ═══════════════════════════════════════════════════════════════════════════
// Elevation Point Types
// أنواع نقاط الارتفاع
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Single elevation survey point
 */
export interface ElevationPoint {
  x: number; // X coordinate (meters)
  y: number; // Y coordinate (meters)
  elevation: number; // Elevation (meters)
  pointId?: string; // Optional point identifier
}

/**
 * Field boundary polygon
 */
export interface FieldBoundary {
  coordinates: Array<[number, number]>; // [x, y] pairs
}

// ═══════════════════════════════════════════════════════════════════════════
// Cut/Fill Calculation Types
// أنواع حسابات القطع والردم
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Cut and fill volume calculations
 */
export interface CutFillVolume {
  cutVolumeM3: number; // Volume to cut (m³)
  fillVolumeM3: number; // Volume to fill (m³)
  netVolumeM3: number; // Net volume (cut - fill)
  cutAreaM2: number; // Area requiring cut (m²)
  fillAreaM2: number; // Area requiring fill (m²)
  balanceRatio: number; // Cut/Fill balance ratio
  maxCutDepthM: number; // Maximum cut depth (m)
  maxFillDepthM: number; // Maximum fill depth (m)
  avgCutDepthM: number; // Average cut depth (m)
  avgFillDepthM: number; // Average fill depth (m)
}

/**
 * Design plane parameters
 */
export interface DesignPlane {
  centroidElevation: number; // Elevation at centroid (m)
  gradeXPercent: number; // Grade in X direction (%)
  gradeYPercent: number; // Grade in Y direction (%)
  planeEquation: string; // Plane equation: z = a*x + b*y + c
  coefficientA: number; // Coefficient a (grade X)
  coefficientB: number; // Coefficient b (grade Y)
  coefficientC: number; // Coefficient c (elevation offset)
}

// ═══════════════════════════════════════════════════════════════════════════
// Cost Estimation Types
// أنواع تقدير التكلفة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Detailed cost estimation in SAR
 */
export interface CostEstimate {
  totalCostSAR: number; // Total estimated cost
  earthworkCostSAR: number; // Earthwork cost
  equipmentCostSAR: number; // Equipment rental cost
  laborCostSAR: number; // Labor cost
  fuelCostSAR: number; // Fuel cost
  surveyingCostSAR: number; // Surveying cost
  contingencySAR: number; // Contingency (10%)
  costPerM3SAR: number; // Cost per cubic meter
  costPerHectareSAR: number; // Cost per hectare
  estimatedDurationHours: number; // Estimated duration (hours)
  estimatedDurationDays: number; // Estimated duration (8-hour days)

  // Bilingual summary
  summaryEn: string;
  summaryAr: string;
}

/**
 * Equipment recommendation
 */
export interface EquipmentRecommendation {
  equipmentType: EquipmentType;
  equipmentNameEn: string;
  equipmentNameAr: string;
  quantity: number;
  hoursRequired: number;
  costPerHourSAR: number;
  totalCostSAR: number;
  productivityM3PerHour: number;
  recommendedFor: string;
  priority: number; // 1 = highest priority
}

// ═══════════════════════════════════════════════════════════════════════════
// Leveling Plan Types
// أنواع خطة التسوية
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Comprehensive leveling plan
 */
export interface LevelingPlan {
  planId: string;
  fieldId: string;
  createdAt: string; // ISO 8601 timestamp

  // Design parameters
  designPlane: DesignPlane;
  method: LevelingMethod;

  // Volumes
  cutFill: CutFillVolume;

  // Field statistics
  fieldAreaM2: number;
  fieldAreaHectares: number;
  originalElevationRange: number;
  leveledElevationRange: number;

  // Haul analysis
  avgHaulDistanceM: number;

  // Recommendations
  equipmentRecommendations: EquipmentRecommendation[];

  // Cost estimate
  costEstimate?: CostEstimate;

  // Bilingual summaries
  summaryEn: string;
  summaryAr: string;
  recommendationsEn: string[];
  recommendationsAr: string[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Simulation Types
// أنواع المحاكاة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Leveling simulation result
 */
export interface SimulationResult {
  fieldId: string;
  simulationTimestamp: string;

  // Original vs Simulated
  originalPoints: ElevationPoint[];
  simulatedPoints: ElevationPoint[];
  cutPoints: ElevationPoint[];
  fillPoints: ElevationPoint[];

  // Design plane
  designPlane: DesignPlane;

  // Volumes
  cutFill: CutFillVolume;

  // Statistics
  originalStdDev: number;
  simulatedStdDev: number;
  uniformityImprovement: number; // Percentage improvement

  // Bilingual summary
  summaryEn: string;
  summaryAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Request/Response Types
// أنواع طلبات واستجابات API
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Request for leveling analysis
 */
export interface LevelingAnalysisRequest {
  fieldId: string;
  elevationPoints: ElevationPoint[];
  boundary?: FieldBoundary;
  soilType?: LevelingSoilType;
  targetGradeX?: number;
  targetGradeY?: number;
  method?: LevelingMethod;
  priority?: LevelingPriority;
  includeCostEstimate?: boolean;
}

/**
 * Response from leveling analysis
 */
export interface LevelingAnalysisResponse {
  success: boolean;
  fieldId: string;
  analysisTimestamp: string;
  plan: LevelingPlan;
  messageEn: string;
  messageAr: string;
}

/**
 * Request for leveling simulation
 */
export interface SimulationRequest {
  fieldId: string;
  elevationPoints: ElevationPoint[];
  targetElevation?: number;
  targetGradeX?: number;
  targetGradeY?: number;
  soilType?: LevelingSoilType;
  method?: LevelingMethod;
}

/**
 * Health check response
 */
export interface LevelingHealthResponse {
  status: 'ok' | 'not_ready';
  service: 'leveling-optimizer-service';
  serviceAr: 'خدمة تحسين التسوية';
  version: string;
  timestamp: string;
}

/**
 * Readiness check response
 */
export interface LevelingReadinessResponse {
  status: 'ok' | 'not_ready';
  database: boolean;
  nats: boolean;
  checks: {
    algorithms: boolean;
    config: boolean;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Configuration Types
// أنواع الإعدادات
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Equipment costs configuration (SAR per hour)
 */
export interface EquipmentCostsConfig {
  bulldozer: number;
  scraper: number;
  grader: number;
  laserLeveler: number;
  excavator: number;
  dumpTruck: number;
}

/**
 * Equipment productivity configuration (m³ per hour)
 */
export interface EquipmentProductivityConfig {
  bulldozer: number;
  scraper: number;
  grader: number;
  laserLeveler: number;
  excavator: number;
}

/**
 * Soil factors configuration
 */
export interface SoilFactorsConfig {
  expansionFactor: number; // Soil expansion factor
  compactionFactor: number; // Soil compaction factor
}

/**
 * Service configuration
 */
export interface LevelingServiceConfig {
  equipmentCosts: EquipmentCostsConfig;
  equipmentProductivity: EquipmentProductivityConfig;
  soilFactors: SoilFactorsConfig;
  fuelCostPerLiter: number;
  operatorCostPerHour: number;
  surveyingCostPerHectare: number;
  defaultHaulDistance: number;
  minDrainageGrade: number;
  maxIrrigationGrade: number;
}
