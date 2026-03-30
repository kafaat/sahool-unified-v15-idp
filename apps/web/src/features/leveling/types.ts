/**
 * Leveling Optimizer Feature - Types
 * أنواع ميزة تحسين التسوية
 */

// ═══════════════════════════════════════════════════════════════════════════
// Enums - التعدادات
// ═══════════════════════════════════════════════════════════════════════════

export type EquipmentType =
  | 'bulldozer'
  | 'scraper'
  | 'grader'
  | 'laser_leveler'
  | 'excavator'
  | 'dump_truck';

export type SoilType = 'sandy' | 'loamy' | 'clay' | 'silty' | 'rocky';

export type LevelingMethod = 'single_plane' | 'dual_plane' | 'contour' | 'bench';

export type LevelingPriority =
  | 'minimize_cost'
  | 'minimize_earthwork'
  | 'optimal_drainage'
  | 'irrigation_efficiency';

// ═══════════════════════════════════════════════════════════════════════════
// Core Models - النماذج الأساسية
// ═══════════════════════════════════════════════════════════════════════════

export interface ElevationPoint {
  x: number;
  y: number;
  elevation: number;
  pointId?: string;
}

export interface FieldBoundary {
  coordinates: number[][];
}

export interface DesignPlane {
  centroidElevation: number;
  gradeXPercent: number;
  gradeYPercent: number;
  planeEquation: string;
  coefficientA: number;
  coefficientB: number;
  coefficientC: number;
}

export interface CutFillVolume {
  cutVolumeM3: number;
  fillVolumeM3: number;
  netVolumeM3: number;
  cutAreaM2: number;
  fillAreaM2: number;
  balanceRatio: number;
  maxCutDepthM: number;
  maxFillDepthM: number;
  avgCutDepthM: number;
  avgFillDepthM: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Recommendation - توصية المعدات
// ═══════════════════════════════════════════════════════════════════════════

export interface EquipmentRecommendation {
  equipmentType: EquipmentType;
  equipmentNameEn: string;
  equipmentNameAr: string;
  quantity: number;
  hoursRequired: number;
  costPerHourSar: number;
  totalCostSar: number;
  productivityM3PerHour: number;
  recommendedFor: string;
  priority: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Cost Estimation - تقدير التكلفة
// ═══════════════════════════════════════════════════════════════════════════

export interface CostEstimation {
  totalCostSar: number;
  earthworkCostSar: number;
  equipmentCostSar: number;
  laborCostSar: number;
  fuelCostSar: number;
  surveyingCostSar: number;
  contingencySar: number;
  costPerM3Sar: number;
  costPerHectareSar: number;
  estimatedDurationHours: number;
  estimatedDurationDays: number;
  summaryEn: string;
  summaryAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Leveling Plan - خطة التسوية
// ═══════════════════════════════════════════════════════════════════════════

export interface LevelingPlan {
  planId: string;
  fieldId: string;
  createdAt: string;
  designPlane: DesignPlane;
  method: LevelingMethod;
  cutFill: CutFillVolume;
  fieldAreaM2: number;
  fieldAreaHectares: number;
  originalElevationRange: number;
  leveledElevationRange: number;
  avgHaulDistanceM: number;
  equipmentRecommendations: EquipmentRecommendation[];
  costEstimate: CostEstimation | null;
  summaryEn: string;
  summaryAr: string;
  recommendationsEn: string[];
  recommendationsAr: string[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Leveling Analysis - تحليل التسوية
// ═══════════════════════════════════════════════════════════════════════════

export interface LevelingAnalysisRequest {
  fieldId: string;
  elevationPoints: ElevationPoint[];
  boundary?: FieldBoundary;
  soilType?: SoilType;
  targetGradeX?: number;
  targetGradeY?: number;
  method?: LevelingMethod;
  priority?: LevelingPriority;
  includeCostEstimate?: boolean;
}

export interface LevelingAnalysis {
  success: boolean;
  fieldId: string;
  analysisTimestamp: string;
  plan: LevelingPlan;
  messageEn: string;
  messageAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Leveling Simulation - محاكاة التسوية
// ═══════════════════════════════════════════════════════════════════════════

export interface LevelingSimulationRequest {
  fieldId: string;
  elevationPoints: ElevationPoint[];
  targetElevation?: number;
  targetGradeX?: number;
  targetGradeY?: number;
  soilType?: SoilType;
  method?: LevelingMethod;
}

export interface LevelingSimulation {
  fieldId: string;
  simulationTimestamp: string;
  originalPoints: ElevationPoint[];
  simulatedPoints: ElevationPoint[];
  cutPoints: ElevationPoint[];
  fillPoints: ElevationPoint[];
  designPlane: DesignPlane;
  cutFill: CutFillVolume;
  originalStdDev: number;
  simulatedStdDev: number;
  uniformityImprovement: number;
  summaryEn: string;
  summaryAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Cost Estimation Request Params - معلمات طلب تقدير التكلفة
// ═══════════════════════════════════════════════════════════════════════════

export interface CostEstimationParams {
  fieldId: string;
  cutVolumeM3: number;
  fillVolumeM3: number;
  fieldAreaHectares: number;
  haulDistanceM?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Request Params - معلمات طلب المعدات
// ═══════════════════════════════════════════════════════════════════════════

export interface EquipmentRecommendationParams {
  fieldId: string;
  totalVolumeM3: number;
  haulDistanceM?: number;
  method?: LevelingMethod;
}

// ═══════════════════════════════════════════════════════════════════════════
// Filters - الفلاتر
// ═══════════════════════════════════════════════════════════════════════════

export interface LevelingFilters {
  fieldId?: string;
  method?: LevelingMethod;
}
