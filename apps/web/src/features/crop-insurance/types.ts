/**
 * Crop Insurance Feature - Types
 * أنواع ميزة التأمين على المحاصيل
 */

export type InsuranceType =
  | 'traditional'
  | 'parametric'
  | 'hybrid'
  | 'area_yield'
  | 'weather_index';

export type PolicyStatus =
  | 'draft'
  | 'pending_approval'
  | 'active'
  | 'suspended'
  | 'expired'
  | 'cancelled'
  | 'claimed';

export type ClaimStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'field_inspection'
  | 'approved'
  | 'partially_approved'
  | 'rejected'
  | 'paid'
  | 'appealed'
  | 'closed';

export type ClaimType =
  | 'crop_loss'
  | 'yield_shortfall'
  | 'weather_event'
  | 'pest_damage'
  | 'disease_damage'
  | 'hail_damage'
  | 'flood_damage'
  | 'drought_damage'
  | 'frost_damage'
  | 'fire_damage'
  | 'equipment_failure'
  | 'parametric_trigger';

export type RiskLevel =
  | 'very_low'
  | 'low'
  | 'moderate'
  | 'high'
  | 'very_high'
  | 'extreme';

export type CoverageType =
  | 'full'
  | 'partial'
  | 'basic'
  | 'comprehensive'
  | 'premium'
  | 'custom';

export interface InsuranceProvider {
  id: string;
  name: string;
  nameAr: string;
  licenseNumber: string;
  contactEmail: string;
  contactPhone: string;
  website: string;
  rating: number;
  supportedRegions: string[];
  supportedCrops: string[];
}

export interface CoverageDetails {
  coverageType: CoverageType;
  sumInsured: number;
  currency: string;
  deductiblePercentage: number;
  deductibleAmount: number;
  maxPayout: number;
  coverageStart: string;
  coverageEnd: string;
  replantingCoverage: boolean;
  inputCostCoverage: boolean;
  revenueProtection: boolean;
}

export interface PolicyPremium {
  basePremium: number;
  riskLoading: number;
  adminFee: number;
  taxAmount: number;
  discountAmount: number;
  totalPremium: number;
  baseRate: number;
  riskMultiplier: number;
  paymentFrequency: string;
  governmentSubsidy: number;
}

export interface InsurancePolicy {
  id: string;
  policyNumber: string;
  insuredFarmer: string;
  insuredFarmerAr: string;
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  coverageAreaHa: number;
  insuranceType: InsuranceType;
  coverageDetails: CoverageDetails;
  premium: PolicyPremium;
  policyStartDate: string;
  policyEndDate: string;
  status: PolicyStatus;
  providerName: string;
  providerNameAr: string;
  claimHistory: string[];
  createdAt: string;
  updatedAt: string;
}

export interface ClaimEvidence {
  id: string;
  type: 'photo' | 'document' | 'satellite_image' | 'weather_data';
  url: string;
  description: string;
  uploadedAt: string;
}

export interface InsuranceClaim {
  id: string;
  claimNumber: string;
  policyId: string;
  claimType: ClaimType;
  claimDate: string;
  lossDescription: string;
  lossDescriptionAr: string;
  estimatedLossAmount: number;
  currency: string;
  evidenceList: ClaimEvidence[];
  claimStatus: ClaimStatus;
  fieldInspectionDate?: string;
  assessorId?: string;
  approvedAmount?: number;
  payoutDate?: string;
  appealDeadline?: string;
  notes?: string;
  notesAr?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ClaimPayout {
  id: string;
  claimId: string;
  grossAmount: number;
  deductibleAmount: number;
  netPayout: number;
  currency: string;
  scheduledDate: string;
  actualDate?: string;
  paymentMethod: string;
  status: string;
}

export interface RiskFactor {
  name: string;
  nameAr: string;
  riskLevel: RiskLevel;
  score: number;
  description: string;
  descriptionAr: string;
}

export interface FieldRiskProfile {
  fieldId: string;
  fieldName: string;
  overallRiskLevel: RiskLevel;
  riskFactors: RiskFactor[];
  historicalClaims: number;
  coverageRecommendations: string[];
}

export interface PolicyFilters {
  status?: PolicyStatus;
  insuranceType?: InsuranceType;
  fieldId?: string;
  search?: string;
}

export interface ClaimFilters {
  claimStatus?: ClaimStatus;
  claimType?: ClaimType;
  policyId?: string;
  search?: string;
}

export interface PolicyFormData {
  insuredFarmer: string;
  insuredFarmerAr: string;
  fieldId: string;
  cropType: string;
  cropTypeAr: string;
  coverageAreaHa: number;
  insuranceType: InsuranceType;
  coverageDetails: CoverageDetails;
  providerId: string;
  policyStartDate: string;
  policyEndDate: string;
}

export interface ClaimFormData {
  policyId: string;
  claimType: ClaimType;
  claimDate: string;
  lossDescription: string;
  lossDescriptionAr: string;
  estimatedLossAmount: number;
  currency: string;
}

export interface InsuranceStats {
  totalPolicies: number;
  activePolicies: number;
  totalClaims: number;
  pendingClaims: number;
  totalPremiumCollected: number;
  totalClaimsPaid: number;
  averageClaimAmount: number;
  lossRatio: number;
  byInsuranceType: Record<string, number>;
  byStatus: Record<string, number>;
}
