/**
 * Terrain & Hydrology Feature - Types
 * أنواع ميزة التضاريس والمياه
 */

export interface DEMAnalysis {
  fieldId: string;
  minElevation: number;
  maxElevation: number;
  meanElevation: number;
  resolution: number;
  rasterUrl?: string;
  processedAt: string;
}

export interface SlopeAnalysis {
  fieldId: string;
  minSlope: number;
  maxSlope: number;
  meanSlope: number;
  slopeClasses: Array<{ range: string; rangeAr: string; percentage: number }>;
  rasterUrl?: string;
}

export interface AspectAnalysis {
  fieldId: string;
  dominantDirection: string;
  dominantDirectionAr: string;
  distribution: Record<string, number>;
  rasterUrl?: string;
}

export interface DrainageAnalysis {
  fieldId: string;
  drainageDensity: number;
  mainChannels: number;
  problemAreas: Array<{ lat: number; lng: number; severity: string; severityAr: string }>;
  recommendations: string[];
  recommendationsAr: string[];
}

export interface WatershedAnalysis {
  fieldId: string;
  area: number;
  perimeter: number;
  outlets: Array<{ lat: number; lng: number }>;
  subBasins: number;
}

export interface FlowAnalysis {
  fieldId: string;
  accumulation: number;
  direction: string;
  directionAr: string;
  rasterUrl?: string;
}

export interface LevelingPlan {
  fieldId: string;
  cutVolume: number;
  fillVolume: number;
  netVolume: number;
  optimalSlope: number;
  estimatedDuration: number;
  gridPoints: Array<{ lat: number; lng: number; cut: number; fill: number }>;
}

export interface CutFillResult {
  fieldId: string;
  totalCut: number;
  totalFill: number;
  balance: number;
  areaAffected: number;
  rasterUrl?: string;
}

export interface LevelingCost {
  fieldId: string;
  earthworkCost: number;
  equipmentCost: number;
  laborCost: number;
  totalCost: number;
  currency: string;
  estimatedDays: number;
}

export interface TerrainFilters {
  fieldId?: string;
  analysisType?: string;
}
