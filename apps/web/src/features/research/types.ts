/**
 * Research Feature - Types
 * أنواع ميزة الأبحاث والتجارب
 */

export type ResearchStatus = 'planning' | 'active' | 'completed' | 'on_hold' | 'cancelled';
export type ResearchType = 'trial' | 'experiment' | 'study' | 'survey';

export interface ResearchTrial {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr?: string;
  crop: string;
  cropAr: string;
  type?: ResearchType;
  status: ResearchStatus;
  startDate: string;
  endDate: string;
  fieldId: string;
  fieldName: string;
  researchers: number;
  progress: number;
  objectives?: string[];
  objectivesAr?: string[];
  methodology?: string;
  methodologyAr?: string;
  results?: string;
  resultsAr?: string;
  leadResearcher?: string;
  team?: string[];
  budget?: number;
  actualCost?: number;
  attachments?: string[];
  metadata?: Record<string, unknown>;
  createdAt?: string;
  updatedAt?: string;
}

export interface ResearchFilters {
  type?: ResearchType;
  status?: ResearchStatus;
  cropType?: string;
  search?: string;
}

export interface ResearchFormData {
  name: string;
  nameAr: string;
  description: string;
  descriptionAr?: string;
  crop: string;
  cropAr: string;
  type?: ResearchType;
  startDate: string;
  endDate: string;
  fieldId?: string;
  objectives?: string[];
  objectivesAr?: string[];
  methodology?: string;
  methodologyAr?: string;
  leadResearcher?: string;
  team?: string[];
  budget?: number;
}

export interface ResearchMilestone {
  id: string;
  trialId: string;
  title: string;
  titleAr: string;
  description?: string;
  dueDate: string;
  completedDate?: string;
  status: 'pending' | 'completed' | 'overdue';
}

export interface ResearchStats {
  totalTrials: number;
  activeTrials: number;
  completedTrials: number;
  planningTrials?: number;
  totalResearchers: number;
  totalBudget?: number;
  byType?: Record<string, number>;
  byStatus?: Record<string, number>;
}
