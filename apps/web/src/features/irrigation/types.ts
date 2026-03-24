/**
 * Irrigation Feature - Types
 * أنواع ميزة الري
 *
 * NOTE: These types are kept for backward compatibility.
 * The canonical irrigation types are in @/lib/api/types.ts.
 * Prefer importing from @/lib/api/types instead.
 */

export type { IrrigationStatus, IrrigationScheduleType, IrrigationFrequency, IrrigationSchedule } from "@/lib/api/types";

export type IrrigationType = "drip" | "sprinkler" | "pivot" | "flood" | "manual";

export interface IrrigationMethod {
  id: string;
  name: string;
  nameAr: string;
  efficiency: number;
}

export interface IrrigationStats {
  totalWaterToday: number;
  activeCount: number;
  pausedCount: number;
  completedCount: number;
  efficiency: number;
}

export interface CreateScheduleRequest {
  fieldId: string;
  name: string;
  type: string;
  startDate: string;
  frequency: string;
  duration: number;
  waterAmount: number;
}
