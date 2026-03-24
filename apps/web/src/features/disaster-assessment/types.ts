/**
 * Disaster Assessment Feature - Types
 * أنواع ميزة تقييم الكوارث
 */

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type DisasterType =
  | 'flood'
  | 'drought'
  | 'frost'
  | 'pest'
  | 'disease'
  | 'storm'
  | 'fire'
  | 'other';
export type EventSeverity = 'minor' | 'moderate' | 'severe' | 'catastrophic';
export type EventStatus = 'active' | 'monitoring' | 'resolved' | 'closed';

export interface RiskAssessment {
  id: string;
  type: DisasterType;
  typeAr: string;
  riskLevel: RiskLevel;
  affectedArea: string;
  affectedAreaAr: string;
  affectedFields?: string[];
  probability: number;
  potentialLoss: number;
  currency: string;
  description?: string;
  descriptionAr?: string;
  indicators?: RiskIndicator[];
  mitigationPlan?: string;
  mitigationPlanAr?: string;
  mitigationActions?: MitigationAction[];
  lastUpdated: string;
  validUntil?: string;
  source?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface RiskIndicator {
  name: string;
  nameAr: string;
  value: number;
  threshold: number;
  unit: string;
  trend: 'increasing' | 'decreasing' | 'stable';
}

export interface MitigationAction {
  id: string;
  action: string;
  actionAr: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed';
  assignedTo?: string;
  dueDate?: string;
  cost?: number;
}

export interface DisasterEvent {
  id: string;
  type: DisasterType;
  typeAr: string;
  date: string;
  location: string;
  locationAr: string;
  coordinates?: { lat: number; lng: number };
  affectedArea: number;
  areaUnit: string;
  severity: EventSeverity;
  status: EventStatus;
  damageEstimate: number;
  currency: string;
  description?: string;
  descriptionAr?: string;
  affectedCrops?: string[];
  affectedInfrastructure?: string[];
  responseActions?: string[];
  insuranceClaim?: {
    status: 'not_filed' | 'filed' | 'approved' | 'rejected' | 'paid';
    amount?: number;
    claimNumber?: string;
  };
  photos?: string[];
  reports?: string[];
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface DisasterFilters {
  type?: DisasterType;
  riskLevel?: RiskLevel;
  status?: EventStatus;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface DisasterFormData {
  type: DisasterType;
  date: string;
  location: string;
  locationAr: string;
  coordinates?: { lat: number; lng: number };
  affectedArea: number;
  areaUnit: string;
  severity: EventSeverity;
  description?: string;
  descriptionAr?: string;
  damageEstimate?: number;
  affectedCrops?: string[];
}

export interface DisasterStats {
  activeRisks: number;
  criticalRisks: number;
  totalPotentialLoss: number;
  activeEvents: number;
  totalDamage: number;
  eventsThisYear: number;
  byType: Record<DisasterType, number>;
  byRiskLevel: Record<RiskLevel, number>;
  recentAlerts: number;
}

export interface WeatherAlert {
  id: string;
  type: 'storm' | 'frost' | 'heat' | 'rain' | 'wind';
  severity: 'advisory' | 'watch' | 'warning' | 'emergency';
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  affectedAreas: string[];
  startTime: string;
  endTime?: string;
  source: string;
}
