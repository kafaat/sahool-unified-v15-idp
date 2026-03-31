/**
 * Crop Rotation Feature - Types
 * أنواع ميزة الدورة الزراعية
 */

// ── Enums / Union Types ────────────────────────────────────────────

export type CropFamily =
  | 'poaceae'
  | 'fabaceae'
  | 'solanaceae'
  | 'cucurbitaceae'
  | 'brassicaceae'
  | 'apiaceae'
  | 'liliaceae'
  | 'chenopodiaceae'
  | 'arecaceae'
  | 'malvaceae';

export type CropType =
  | 'wheat'
  | 'barley'
  | 'rice'
  | 'maize'
  | 'sorghum'
  | 'millet'
  | 'oat'
  | 'triticale'
  | 'alfalfa'
  | 'clover'
  | 'fava_bean'
  | 'chickpea'
  | 'lentil'
  | 'peanut'
  | 'soybean'
  | 'cowpea'
  | 'tomato'
  | 'potato'
  | 'pepper'
  | 'eggplant'
  | 'cucumber'
  | 'watermelon'
  | 'melon'
  | 'squash'
  | 'pumpkin'
  | 'zucchini'
  | 'cabbage'
  | 'cauliflower'
  | 'broccoli'
  | 'carrot'
  | 'celery'
  | 'parsley'
  | 'onion'
  | 'garlic'
  | 'leek'
  | 'spinach'
  | 'beet'
  | 'date_palm'
  | 'cotton'
  | 'okra'
  | 'sunflower'
  | 'sesame';

export type Season =
  | 'winter'
  | 'summer'
  | 'spring'
  | 'fall'
  | 'year_round'
  | 'perennial';

export type RotationBenefit =
  | 'nitrogen_fixation'
  | 'pest_break'
  | 'disease_break'
  | 'weed_suppression'
  | 'soil_structure'
  | 'organic_matter'
  | 'nutrient_cycling'
  | 'erosion_control'
  | 'water_efficiency'
  | 'biodiversity';

export type SoilHealthIndicator =
  | 'organic_matter'
  | 'nitrogen'
  | 'phosphorus'
  | 'potassium'
  | 'ph'
  | 'ec'
  | 'soil_structure'
  | 'microbial_activity'
  | 'water_retention'
  | 'compaction';

export type RecommendationPriority =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'optional';

export type PlanStatus =
  | 'draft'
  | 'active'
  | 'completed'
  | 'cancelled'
  | 'archived';

// ── Interfaces ─────────────────────────────────────────────────────

export interface CropCharacteristics {
  cropType: CropType;
  family: CropFamily;
  name: string;
  nameAr: string;
  season: Season;
  growingDaysMin: number;
  growingDaysMax: number;
  optimalTemp: { min: number; max: number };
  waterRequirementMm: number;
  droughtTolerance: 'low' | 'medium' | 'high';
  phRange: { min: number; max: number };
  saltTolerance: 'low' | 'medium' | 'high';
  nutrientDemands: { nitrogen: number; phosphorus: number; potassium: number };
  rootDepth: 'shallow' | 'medium' | 'deep';
  minRotationYears: number;
  majorPests: string[];
  majorDiseases: string[];
}

export interface RotationSlot {
  cropType: CropType;
  season: Season;
  year: number;
  plannedPlantingDate: string;
  plannedHarvestDate: string;
  areaHa: number;
  expectedYieldTonsHa: number;
  rotationBenefits: RotationBenefit[];
  isCompleted: boolean;
}

export interface RotationSequence {
  fieldId: string;
  startYear: number;
  slots: RotationSlot[];
  totalAreaHa: number;
  durationYears: number;
}

export interface RotationPlan {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  sequences: RotationSequence[];
  status: PlanStatus;
  createdAt: string;
  updatedAt: string;
}

export interface RotationRecommendation {
  recommendedCrop: CropType;
  cropNameAr: string;
  score: number;
  expectedYield: number;
  expectedRevenue: number;
  priority: RecommendationPriority;
  soilImpactScore: number;
  pestBreakScore: number;
  waterEfficiencyScore: number;
  reasoning: string;
  reasoningAr: string;
  positiveFactors: string[];
  negativeFactors: string[];
  warnings: string[];
}

export interface NutrientBalance {
  nitrogen: { input: number; output: number; balance: number };
  phosphorus: { input: number; output: number; balance: number };
  potassium: { input: number; output: number; balance: number };
  sustainabilityScore: number;
  fertilizerSavingsPotential: number;
}

export interface MultiYearPlan {
  id: string;
  durationYears: number;
  recommendations: RotationRecommendation[];
  nutrientBalance: NutrientBalance;
  keyRecommendations: string[];
  summary: string;
  summaryAr: string;
}

export interface CropHistoryRecord {
  cropType: CropType;
  season: Season;
  year: number;
  plantingDate: string;
  harvestDate: string;
  yieldTonsHa: number;
  areaHa: number;
  issues: string[];
}

export interface FieldRotationHistory {
  fieldId: string;
  currentCrop: CropType | null;
  previousCrops: CropType[];
  historyRecords: CropHistoryRecord[];
  rotationScores: {
    diversity: number;
    soilHealth: number;
    pestManagement: number;
    overall: number;
  };
}

export interface PestBreakRecommendation {
  currentCrop: CropType;
  recommendedBreakCrops: CropType[];
  breakDurationYears: number;
  effectiveness: number;
}

export interface SoilHealthMeasurement {
  indicator: SoilHealthIndicator;
  value: number;
  unit: string;
  rating: 'poor' | 'fair' | 'good' | 'excellent';
}

export interface SoilHealthTrend {
  indicator: SoilHealthIndicator;
  initialValue: number;
  currentValue: number;
  targetValue: number;
  direction: 'improving' | 'stable' | 'declining';
  changeRate: number;
}

export interface SoilHealthReport {
  fieldId: string;
  testDate: string;
  measurements: SoilHealthMeasurement[];
  trends: SoilHealthTrend[];
  overallHealthScore: number;
  recommendations: string[];
  recommendationsAr: string[];
}

// ── Filters & Form Data ────────────────────────────────────────────

export interface CropRotationFilters {
  fieldId?: string;
  status?: PlanStatus;
  season?: Season;
  cropType?: CropType;
  search?: string;
}

export interface RotationPlanFormData {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  sequences: RotationSequence[];
  status: PlanStatus;
}

export interface CropRotationStats {
  totalPlans: number;
  activePlans: number;
  completedPlans: number;
  averageRotationScore: number;
  topCrops: { cropType: CropType; count: number }[];
  averageSoilHealthScore: number;
  totalFieldsCovered: number;
  byStatus: Record<string, number>;
}
