/**
 * Crop Health Feature - Type Definitions
 * تعريفات الأنواع لميزة صحة المحصول
 */

// Disease severity levels
export type DiseaseSeverity = 'low' | 'medium' | 'high' | 'critical';

// Diagnosis status
export type DiagnosisStatus = 'pending' | 'analyzing' | 'completed' | 'failed';

// Treatment types
export type TreatmentType = 'chemical' | 'biological' | 'cultural' | 'preventive';

// Disease category
export type DiseaseCategory =
  | 'fungal'
  | 'bacterial'
  | 'viral'
  | 'pest'
  | 'nutrient_deficiency'
  | 'environmental'
  | 'other';

// Disease information
export interface Disease {
  id: string;
  name: string;
  nameAr: string;
  category: DiseaseCategory;
  description: string;
  descriptionAr: string;
  symptoms: string[];
  symptomsAr: string[];
  causes: string[];
  causesAr: string[];
  affectedCrops: string[];
  affectedCropsAr: string[];
  severity: DiseaseSeverity;
  prevalence: number; // percentage
  images?: string[];
}

// Treatment recommendation
export interface Treatment {
  id: string;
  name: string;
  nameAr: string;
  type: TreatmentType;
  description: string;
  descriptionAr: string;
  steps: string[];
  stepsAr: string[];
  materials?: TreatmentMaterial[];
  timing?: string;
  timingAr?: string;
  frequency?: string;
  frequencyAr?: string;
  precautions?: string[];
  precautionsAr?: string[];
  expectedResults?: string;
  expectedResultsAr?: string;
  cost?: {
    min: number;
    max: number;
    currency: string;
  };
}

// Treatment material
export interface TreatmentMaterial {
  name: string;
  nameAr: string;
  quantity: string;
  quantityAr: string;
  type: 'pesticide' | 'fungicide' | 'herbicide' | 'fertilizer' | 'biological' | 'other';
}

// Diagnosis request
export interface DiagnosisRequest {
  id: string;
  userId: string;
  fieldId?: string;
  fieldName?: string;
  fieldNameAr?: string;
  cropType: string;
  cropTypeAr: string;
  images: string[];
  description?: string;
  descriptionAr?: string;
  symptoms?: string[];
  symptomsAr?: string[];
  location?: {
    lat: number;
    lng: number;
  };
  status: DiagnosisStatus;
  createdAt: string;
  updatedAt: string;
}

// Diagnosis result
export interface DiagnosisResult {
  id: string;
  requestId: string;
  diseases: DiagnosedDisease[];
  confidence: number; // overall confidence percentage
  analyzedAt: string;
  notes?: string;
  notesAr?: string;
}

// Diagnosed disease with confidence
export interface DiagnosedDisease {
  disease: Disease;
  confidence: number; // percentage
  affectedArea?: number; // percentage of crop affected
  recommendedTreatments: Treatment[];
  urgency: 'immediate' | 'soon' | 'monitor';
  estimatedSpread?: {
    current: number; // percentage
    projected: number; // percentage in X days
    days: number;
  };
}

// Health monitoring record
export interface HealthRecord {
  id: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  date: string;
  healthScore: number; // 0-100
  status: 'healthy' | 'at_risk' | 'diseased' | 'critical';
  observations?: string;
  observationsAr?: string;
  images?: string[];
  issues?: {
    type: string;
    typeAr: string;
    severity: DiseaseSeverity;
    description: string;
    descriptionAr: string;
  }[];
  treatments?: {
    treatmentId: string;
    appliedAt: string;
    status: 'planned' | 'applied' | 'completed';
  }[];
  nextCheckDate?: string;
}

// Health dashboard summary
export interface HealthSummary {
  totalFields: number;
  healthyFields: number;
  atRiskFields: number;
  diseasedFields: number;
  criticalFields: number;
  avgHealthScore: number;
  recentDiagnoses: number;
  pendingTreatments: number;
  topDiseases: {
    disease: Disease;
    affectedFields: number;
  }[];
}

// Health filters
export interface HealthFilters {
  fieldIds?: string[];
  cropTypes?: string[];
  status?: HealthRecord['status'][];
  dateFrom?: string;
  dateTo?: string;
  severity?: DiseaseSeverity[];
}

// Disease alert
export interface DiseaseAlert {
  id: string;
  disease: Disease;
  severity: DiseaseSeverity;
  affectedFields: string[];
  affectedFieldsAr: string[];
  region?: string;
  regionAr?: string;
  message: string;
  messageAr: string;
  recommendations?: string[];
  recommendationsAr?: string[];
  issuedAt: string;
  expiresAt?: string;
  source: 'ai_detection' | 'expert_report' | 'government' | 'community';
}

// Expert consultation
export interface ExpertConsultation {
  id: string;
  diagnosisId: string;
  expertId: string;
  expertName: string;
  expertNameAr: string;
  status: 'pending' | 'in_review' | 'completed' | 'cancelled';
  question?: string;
  questionAr?: string;
  response?: string;
  responseAr?: string;
  recommendations?: string[];
  recommendationsAr?: string[];
  requestedAt: string;
  respondedAt?: string;
}
