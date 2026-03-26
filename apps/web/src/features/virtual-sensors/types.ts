/**
 * Virtual Sensors Feature - Types
 * أنواع ميزة الاستشعار الافتراضي
 */

export interface ET0Result {
  et0: number;
  unit: string;
  method: string;
  date: string;
  inputs: Record<string, number>;
}

export interface ETCResult {
  etc: number;
  et0: number;
  kc: number;
  cropType: string;
  growthStage: string;
  growthStageAr: string;
  unit: string;
}

export interface CropInfo {
  type: string;
  name: string;
  nameAr: string;
  stages: Array<{ name: string; nameAr: string; kc: number; durationDays: number }>;
}

export interface SoilInfo {
  type: string;
  name: string;
  nameAr: string;
  fieldCapacity: number;
  wiltingPoint: number;
  saturatedConductivity: number;
}

export interface SoilMoistureEstimate {
  currentMoisture: number;
  fieldCapacity: number;
  wiltingPoint: number;
  depletionFraction: number;
  status: 'adequate' | 'deficit' | 'surplus';
  statusAr: string;
}

export interface IrrigationRecommendation {
  shouldIrrigate: boolean;
  amount: number;
  unit: string;
  timing: string;
  timingAr: string;
  reason: string;
  reasonAr: string;
  confidence: number;
}

export interface IrrigationQuickCheck {
  needsIrrigation: boolean;
  urgency: 'none' | 'low' | 'medium' | 'high';
  urgencyAr: string;
  recommendation: string;
  recommendationAr: string;
}
