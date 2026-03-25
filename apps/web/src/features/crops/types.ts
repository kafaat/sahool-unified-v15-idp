/**
 * Crops Feature - Types
 * أنواع ميزة المحاصيل
 */

export type CropStage =
  | 'germination'
  | 'seedling'
  | 'vegetative'
  | 'flowering'
  | 'fruiting'
  | 'maturity'
  | 'harvest';
export type CropCategory =
  | 'cereals'
  | 'vegetables'
  | 'fruits'
  | 'legumes'
  | 'forage'
  | 'industrial';

export interface Crop {
  id: string;
  name: string;
  nameAr: string;
  variety: string;
  varietyAr: string;
  category: CropCategory;
  currentStage: CropStage;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  plantingDate: string;
  expectedHarvestDate: string;
  areaHa: number;
  healthScore: number;
  ndvi?: number;
  irrigationType: string;
  irrigationTypeAr: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CropFilters {
  category?: CropCategory;
  stage?: CropStage;
  fieldId?: string;
  search?: string;
}

export interface CropFormData {
  name: string;
  nameAr: string;
  variety: string;
  varietyAr: string;
  category: CropCategory;
  fieldId: string;
  plantingDate: string;
  expectedHarvestDate: string;
  areaHa: number;
  irrigationType: string;
  irrigationTypeAr: string;
  notes?: string;
}

export interface CropStats {
  totalCrops: number;
  byCategory: Record<string, number>;
  byStage: Record<string, number>;
  averageHealth: number;
  totalAreaHa: number;
}
