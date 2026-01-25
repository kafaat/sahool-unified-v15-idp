/**
 * Research Feature - Types
 * أنواع ميزة الأبحاث والتجارب
 */

export type ResearchStatus = "planning" | "active" | "completed" | "on_hold" | "cancelled";
export type ResearchType = "trial" | "experiment" | "study" | "survey";

export interface ResearchTrial {
  id: string;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  type: ResearchType;
  status: ResearchStatus;
  startDate: string;
  endDate?: string;
  targetEndDate: string;
  fieldId?: string;
  fieldName?: string;
  cropType?: string;
  objectives: string[];
  objectivesAr: string[];
  methodology?: string;
  methodologyAr?: string;
  progress: number;
  results?: string;
  resultsAr?: string;
  leadResearcher: string;
  team: string[];
  budget?: number;
  actualCost?: number;
  attachments?: string[];
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface ResearchFilters {
  type?: ResearchType;
  status?: ResearchStatus;
  cropType?: string;
  search?: string;
}

export interface ResearchFormData {
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  type: ResearchType;
  startDate: string;
  targetEndDate: string;
  fieldId?: string;
  cropType?: string;
  objectives: string[];
  objectivesAr: string[];
  methodology?: string;
  methodologyAr?: string;
  leadResearcher: string;
  team: string[];
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
  status: "pending" | "completed" | "overdue";
}

export interface ResearchStats {
  totalTrials: number;
  activeTrials: number;
  completedTrials: number;
  totalBudget: number;
  byType: Record<string, number>;
  byStatus: Record<string, number>;
}
