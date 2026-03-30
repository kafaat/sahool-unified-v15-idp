/**
 * Irrigation Feature - Types
 * أنواع ميزة الري
 *
 * These are feature-local types used by the irrigation feature module.
 * The canonical API types are in @/lib/api/types.ts (IrrigationSchedule, etc.)
 * and are used by the main dashboard at app/(dashboard)/irrigation/.
 */

export type IrrigationStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'overdue';
export type IrrigationType = 'drip' | 'sprinkler' | 'pivot' | 'flood' | 'manual';

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

// ---------------------------------------------------------------------------
// ML Irrigation Types - أنواع الري الذكي
// ---------------------------------------------------------------------------

/** Crop types supported by the irrigation-smart service */
export type SmartCropType =
  | 'tomato'
  | 'wheat'
  | 'coffee'
  | 'qat'
  | 'banana'
  | 'cucumber'
  | 'pepper'
  | 'potato'
  | 'corn'
  | 'grapes'
  | 'date_palm'
  | 'mango'
  | 'onion'
  | 'garlic'
  | 'alfalfa';

/** Growth stages */
export type GrowthStage = 'seedling' | 'vegetative' | 'flowering' | 'fruiting' | 'maturity';

/** Soil types */
export type SoilType = 'sandy' | 'clay' | 'loamy' | 'silt' | 'rocky';

/** Irrigation methods supported by the smart service */
export type SmartIrrigationMethod = 'flood' | 'drip' | 'sprinkler' | 'furrow' | 'traditional';

/** Urgency levels returned by the ML predictor */
export type IrrigationUrgency = 'low' | 'medium' | 'high' | 'critical';

/**
 * Request payload for POST /v1/calculate
 * طلب حساب احتياجات الري
 */
export interface CalculateIrrigationRequest {
  field_id: string;
  crop: SmartCropType;
  growth_stage: GrowthStage;
  area_hectares: number;
  soil_type?: SoilType;
  irrigation_method?: SmartIrrigationMethod;
  current_soil_moisture?: number | null;
  last_irrigation_date?: string | null;
  weather_forecast?: Record<string, unknown> | null;
}

/**
 * A single scheduled irrigation session within a plan
 * جلسة ري مجدولة ضمن خطة
 */
export interface IrrigationPlanSchedule {
  schedule_id: string;
  field_id: string;
  crop: SmartCropType;
  crop_name_ar: string;
  irrigation_date: string;
  start_time: string;
  duration_minutes: number;
  water_amount_liters: number;
  water_amount_m3: number;
  urgency: IrrigationUrgency;
  urgency_ar: string;
  method: SmartIrrigationMethod;
  method_ar: string;
  reasoning_ar: string;
  reasoning_en: string;
  weather_adjusted: boolean;
  savings_percent: number;
}

/**
 * ML irrigation prediction / plan result
 * نتيجة التنبؤ بالري باستخدام التعلم الآلي
 */
export interface IrrigationPrediction {
  plan_id: string;
  field_id: string;
  crop: SmartCropType;
  crop_name_ar: string;
  growth_stage: GrowthStage;
  growth_stage_ar: string;
  area_hectares: number;
  soil_type: SoilType;
  current_water_need_mm: number;
  daily_et_mm: number;
  schedules: IrrigationPlanSchedule[];
  total_water_m3: number;
  estimated_cost_yer: number;
  water_savings_m3: number;
  recommendations_ar: string[];
  recommendations_en: string[];
  alerts_ar: string[];
  created_at: string;
}

/**
 * Daily water balance entry for a field
 * الميزان المائي اليومي للحقل
 */
export interface WaterBalanceEntry {
  field_id: string;
  date: string;
  et_mm: number;
  rainfall_mm: number;
  irrigation_mm: number;
  soil_moisture_change_mm: number;
  water_deficit_mm: number;
  cumulative_deficit_mm: number;
}

/**
 * Water balance response from GET /v1/water-balance/{fieldId}
 * استجابة الميزان المائي
 */
export interface WaterBalanceResponse {
  field_id: string;
  crop: string;
  period_days: number;
  summary: {
    total_et_mm: number;
    total_rainfall_mm: number;
    total_irrigation_mm: number;
    net_water_balance_mm: number;
    cumulative_deficit_mm: number;
  };
  daily_data: WaterBalanceEntry[];
  recommendation_ar: string;
}

/**
 * Efficiency method comparison entry
 * مقارنة كفاءة طريقة الري
 */
export interface EfficiencyMethodComparison {
  method: SmartIrrigationMethod;
  method_ar: string;
  efficiency_percent: number;
  annual_water_m3: number;
  annual_cost_yer: number;
  water_saved_m3: number;
  cost_saved_yer: number;
  savings_percent: number;
}

/**
 * Efficiency report from GET /v1/efficiency-report/{fieldId}
 * تقرير كفاءة الري
 */
export interface EfficiencyReport {
  field_id: string;
  area_hectares: number;
  current_method: {
    method: SmartIrrigationMethod;
    method_ar: string;
    efficiency_percent: number;
    annual_water_m3: number;
    annual_cost_yer: number;
  };
  alternatives: EfficiencyMethodComparison[];
  recommendation_ar: string;
  roi_months: number | null;
}

/**
 * Sensor reading request for POST /v1/sensor-reading
 * بيانات قراءة المستشعر
 */
export interface SensorReadingRequest {
  field_id: string;
  sensor_id: string;
  reading_time: string;
  depth_cm: number;
  moisture_percent: number;
  temperature_c: number;
  ec_ds_m: number;
}

/**
 * Sensor reading response
 * استجابة تسجيل قراءة المستشعر
 */
export interface SensorReadingResponse {
  reading_id: string;
  field_id: string;
  sensor_id: string;
  moisture_percent: number;
  status: 'critical' | 'low' | 'optimal' | 'high';
  action_ar: string;
  action_en: string;
  recorded_at: string;
}

/**
 * Irrigation execution record for POST /v1/irrigation-executed
 * تسجيل تنفيذ عملية الري
 */
export interface IrrigationExecutionRequest {
  field_id: string;
  schedule_id?: string | null;
  plan_id?: string | null;
  amount_mm: number;
  duration_minutes: number;
  method?: SmartIrrigationMethod;
  executed_at?: string | null;
  notes?: string | null;
}

/**
 * Irrigation execution response
 * استجابة تسجيل تنفيذ الري
 */
export interface IrrigationExecutionResponse {
  execution_id: string;
  field_id: string;
  plan_id: string | null;
  schedule_id: string | null;
  amount_mm: number;
  duration_minutes: number;
  method: SmartIrrigationMethod;
  method_ar: string;
  executed_at: string;
  status: string;
  message_ar: string;
  message_en: string;
}

/**
 * Response from POST /v1/calculate-with-action
 * استجابة حساب الري مع قالب الإجراء
 */
export interface CalculateWithActionResponse {
  plan: IrrigationPrediction;
  action_template: Record<string, unknown> | null;
  action_template_available: boolean;
  task_card?: Record<string, unknown>;
  notification_payload?: Record<string, unknown>;
  message?: string;
}
