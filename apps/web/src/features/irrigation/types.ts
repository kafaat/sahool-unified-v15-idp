/**
 * Irrigation Feature - Types
 * أنواع ميزة الري
 *
 * These are feature-local types used by the irrigation feature module.
 * The canonical API types are in @/lib/api/types.ts (IrrigationSchedule, etc.)
 * and are used by the main dashboard at app/(dashboard)/irrigation/.
 */

export type IrrigationStatus = "scheduled" | "in_progress" | "completed" | "cancelled" | "overdue";
export type IrrigationType = "drip" | "sprinkler" | "pivot" | "flood" | "manual";

export interface IrrigationSchedule {
  id: string;
  fieldId: string;
  fieldName: string;
  type: IrrigationType;
  status: IrrigationStatus;
  scheduledAt: string;
  duration: number;
  waterAmount: number;
  completedAt?: string;
  progress?: number;
}

export interface IrrigationMethod {
  id: string;
  name: string;
  nameAr: string;
  efficiency: number;
}

export interface IrrigationStats {
  totalWaterToday: number;
  inProgressCount: number;
  scheduledCount: number;
  overdueCount: number;
  efficiency: number;
}

export interface CreateScheduleRequest {
  fieldName: string;
  type: IrrigationType;
  scheduledAt: string;
  duration: number;
  waterAmount: number;
}
