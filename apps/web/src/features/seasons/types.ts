/**
 * Seasons Feature - Types
 * أنواع ميزة المواسم
 */

export type SeasonStatus = 'planning' | 'active' | 'harvesting' | 'completed' | 'cancelled';
export type SeasonType = 'winter' | 'summer' | 'spring' | 'fall';

export interface Season {
  id: string;
  name: string;
  nameAr: string;
  type: SeasonType;
  year: number;
  status: SeasonStatus;
  startDate: string;
  endDate: string;
  farmId: string;
  farmName: string;
  farmNameAr: string;
  cropsCount: number;
  fieldsCount: number;
  totalAreaHa: number;
  targetYieldTons: number;
  actualYieldTons?: number;
  budgetSar: number;
  spentSar: number;
  progress: number;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SeasonFilters {
  status?: SeasonStatus;
  type?: SeasonType;
  year?: number;
  farmId?: string;
  search?: string;
}

export interface SeasonFormData {
  name: string;
  nameAr: string;
  type: SeasonType;
  year: number;
  startDate: string;
  endDate: string;
  farmId: string;
  targetYieldTons: number;
  budgetSar: number;
  notes?: string;
}

export interface SeasonStats {
  totalSeasons: number;
  activeSeasons: number;
  completedSeasons: number;
  averageYieldRate: number;
  totalBudgetSar: number;
}
