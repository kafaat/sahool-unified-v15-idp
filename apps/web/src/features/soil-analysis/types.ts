/**
 * Soil Analysis Feature - Types
 * أنواع ميزة تحليل التربة
 */

export interface SoilTest {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  sampleDate: string;
  pH: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  organicMatter: number;
  electricalConductivity: number;
  texture: string;
  textureAr: string;
  calcium?: number;
  magnesium?: number;
  sulfur?: number;
  iron?: number;
  zinc?: number;
  manganese?: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  labName?: string;
  notes?: string;
  notesAr?: string;
  createdAt: string;
}

export interface SoilRecommendation {
  id: string;
  testId: string;
  fieldId: string;
  nutrient: string;
  nutrientAr: string;
  currentLevel: number;
  optimalRange: { min: number; max: number };
  recommendation: string;
  recommendationAr: string;
  fertilizer?: string;
  fertilizerAr?: string;
  rate?: number;
  unit?: string;
  priority: 'low' | 'medium' | 'high';
}

export interface SoilFilters {
  fieldId?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
}
