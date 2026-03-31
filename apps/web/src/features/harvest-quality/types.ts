/**
 * Harvest Quality Feature - Types
 * أنواع ميزة جودة الحصاد
 */

export type CropCategory = 'grain' | 'date' | 'vegetable' | 'fruit' | 'legume';

export type QualityGrade = 'premium' | 'grade_a' | 'grade_b' | 'grade_c' | 'industrial' | 'rejected';

export type GrainType = 'wheat' | 'barley' | 'corn' | 'sorghum' | 'rice' | 'millet';

export type DateVariety =
  | 'sukkari' | 'khalas' | 'ajwa' | 'medjool' | 'barhi'
  | 'deglet_noor' | 'safawi' | 'segai' | 'khudri' | 'mabroom' | 'zahidi' | 'other';

export type DateStage = 'kimri' | 'khalal' | 'rutab' | 'tamr';

export type VegetableType =
  | 'tomato' | 'cucumber' | 'onion' | 'potato' | 'carrot'
  | 'eggplant' | 'pepper' | 'lettuce' | 'zucchini' | 'cabbage' | 'other';

export type TestType =
  | 'moisture' | 'protein' | 'test_weight' | 'foreign_matter'
  | 'damaged_kernels' | 'broken_kernels' | 'falling_number' | 'gluten'
  | 'sugar_content' | 'texture' | 'size' | 'color' | 'defects'
  | 'firmness' | 'brix' | 'ph_level' | 'uniformity' | 'freshness'
  | 'pest_damage' | 'disease_presence' | 'visual_inspection' | 'weight_check';

export type TestStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';

export type TestResult = 'pass' | 'marginal' | 'fail' | 'not_applicable';

export interface QualityParameter {
  parameterName: string;
  parameterNameAr: string;
  unit: string;
  premiumThreshold: number;
  gradeAThreshold: number;
  gradeBThreshold: number;
  gradeCThreshold: number;
  lowerIsBetter: boolean;
  weight: number;
  mandatory: boolean;
}

export interface QualityStandard {
  id: string;
  cropType: string;
  cropTypeAr: string;
  parameters: QualityParameter[];
  version: string;
  effectiveDate: string;
  regulatoryBody: string;
  regulatoryBodyAr: string;
  standardCode: string;
}

export interface QualityTestResultItem {
  testType: TestType;
  parameterName: string;
  parameterNameAr: string;
  value: number;
  unit: string;
  grade: QualityGrade;
  result: TestResult;
  testMethod: string;
  testerId: string;
  testTimestamp: string;
}

export interface QualityTestRecord {
  id: string;
  batchId: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropCategory: CropCategory;
  cropType: string;
  cropTypeAr: string;
  testResults: QualityTestResultItem[];
  overallGrade: QualityGrade;
  gradeScore: number;
  confidence: number;
  status: TestStatus;
  notes?: string;
  notesAr?: string;
  createdAt: string;
  updatedAt: string;
}

export interface BuyerRequirement {
  id: string;
  buyerId: string;
  buyerName: string;
  buyerNameAr: string;
  minGrade: QualityGrade;
  maxGrade: QualityGrade;
  cropType: string;
  quantityNeeded: number;
  unit: string;
  priceRangeMin: number;
  priceRangeMax: number;
  currency: string;
}

export interface BuyerMatch {
  buyerId: string;
  buyerName: string;
  buyerNameAr: string;
  batchId: string;
  matchScore: number;
  meetingRequirements: boolean;
  priceQuote: number;
  currency: string;
  confidence: number;
}

export interface GradePriceMatrix {
  cropType: string;
  cropTypeAr: string;
  premiumPrice: number;
  gradeAPrice: number;
  gradeBPrice: number;
  gradeCPrice: number;
  industrialPrice: number;
  currency: string;
  unit: string;
  effectiveDate: string;
}

export interface PriceCalculation {
  finalPrice: number;
  currency: string;
  basePrice: number;
  gradeAdjustment: number;
  qualityAdjustments: Record<string, number>;
  totalMargin: number;
  calculationDate: string;
}

export interface QualityTrend {
  fieldId: string;
  cropType: string;
  trendDirection: 'improving' | 'declining' | 'stable' | 'volatile';
  confidence: number;
  recentTests: number;
  slope: number;
  sampleSize: number;
  periodDays: number;
}

export interface HarvestQualityFilters {
  fieldId?: string;
  cropCategory?: CropCategory;
  grade?: QualityGrade;
  status?: TestStatus;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface QualityTestFormData {
  batchId: string;
  fieldId: string;
  cropCategory: CropCategory;
  cropType: string;
  testResults: Array<{
    testType: TestType;
    parameterName: string;
    value: number;
    unit: string;
    testMethod?: string;
  }>;
  notes?: string;
  notesAr?: string;
}

export interface HarvestQualityStats {
  totalTests: number;
  byGrade: Record<QualityGrade, number>;
  byCropCategory: Record<string, number>;
  averageGradeScore: number;
  passRate: number;
  trendDirection: string;
}
