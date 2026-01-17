/**
 * SAHOOL Action Windows Feature Types
 * أنواع ميزة نوافذ العمل
 *
 * Types for weather-based action windows (spray, irrigation, fertilization)
 */

// ═══════════════════════════════════════════════════════════════════════════
// Window Status Types
// ═══════════════════════════════════════════════════════════════════════════

export type WindowStatus = "optimal" | "marginal" | "avoid";

export type ActionType =
  | "spray"
  | "irrigate"
  | "fertilize"
  | "plant"
  | "harvest";

// ═══════════════════════════════════════════════════════════════════════════
// Weather Condition Types
// ═══════════════════════════════════════════════════════════════════════════

export interface WeatherCondition {
  timestamp: string;
  temperature: number; // °C
  humidity: number; // %
  windSpeed: number; // km/h
  windDirection: string;
  rainProbability: number; // %
  precipitation: number; // mm
  cloudCover: number; // %
  uvIndex?: number;
  pressure?: number; // hPa
}

// ═══════════════════════════════════════════════════════════════════════════
// Spray Window Types
// ═══════════════════════════════════════════════════════════════════════════

export interface SprayWindow {
  id: string;
  fieldId: string;
  startTime: string;
  endTime: string;
  duration: number; // hours
  status: WindowStatus;
  score: number; // 0-100
  conditions: WeatherCondition;
  suitability: {
    windSpeed: boolean;
    temperature: boolean;
    humidity: boolean;
    rain: boolean;
    overall: boolean;
  };
  warnings: string[];
  warningsAr: string[];
  recommendations: string[];
  recommendationsAr: string[];
}

export interface SprayWindowCriteria {
  windSpeedMax: number; // km/h (default: 15)
  windSpeedMin: number; // km/h (default: 3)
  temperatureMin: number; // °C (default: 10)
  temperatureMax: number; // °C (default: 30)
  humidityMin: number; // % (default: 50)
  humidityMax: number; // % (default: 90)
  rainProbabilityMax: number; // % (default: 20)
  minDuration: number; // hours (default: 2)
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Window Types
// ═══════════════════════════════════════════════════════════════════════════

export interface IrrigationWindow {
  id: string;
  fieldId: string;
  date: string;
  startTime: string;
  endTime: string;
  status: WindowStatus;
  priority: "urgent" | "high" | "medium" | "low";
  waterAmount: number; // mm
  duration: number; // hours
  soilMoisture: {
    current: number; // %
    target: number; // %
    deficit: number; // mm
    status: "critical" | "low" | "optimal" | "high";
    statusAr: string;
  };
  et: {
    et0: number; // mm/day - Reference evapotranspiration
    etc: number; // mm/day - Crop evapotranspiration
    kc: number; // Crop coefficient
  };
  weather: WeatherCondition;
  recommendations: string[];
  recommendationsAr: string[];
  reason: string;
  reasonAr: string;
}

export interface IrrigationNeed {
  fieldId: string;
  urgency: "none" | "low" | "medium" | "high" | "critical";
  recommendedAmount: number; // mm
  recommendedDuration: number; // hours
  nextIrrigationDate: string;
  soilMoistureDeficit: number; // mm
  currentMoisture: number; // %
  targetMoisture: number; // %
  et0: number; // mm/day
  reasoning: string;
  reasoningAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Action Recommendation Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ActionRecommendation {
  id: string;
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  actionType: ActionType;
  priority: "urgent" | "high" | "medium" | "low";
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  window: {
    startTime: string;
    endTime: string;
    optimal: boolean;
  };
  conditions: WeatherCondition;
  reason: string;
  reasonAr: string;
  benefits: string[];
  benefitsAr: string[];
  warnings?: string[];
  warningsAr?: string[];
  confidence: number; // 0-100
  createdAt: string;
  expiresAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Timeline Types
// ═══════════════════════════════════════════════════════════════════════════

export interface TimelineBlock {
  id: string;
  startTime: string;
  endTime: string;
  status: WindowStatus;
  score: number;
  label: string;
  labelAr: string;
  details: {
    temperature: number;
    windSpeed: number;
    humidity: number;
    rainProbability: number;
  };
  actionable: boolean;
}

export interface Timeline {
  fieldId: string;
  actionType: ActionType;
  startDate: string;
  endDate: string;
  blocks: TimelineBlock[];
  summary: {
    totalWindows: number;
    optimalWindows: number;
    marginalWindows: number;
    avoidWindows: number;
    bestWindowIndex: number;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Threshold Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ThresholdIndicator {
  parameter: "wind" | "temperature" | "humidity" | "rain";
  parameterAr: string;
  currentValue: number;
  threshold: number;
  operator: "less_than" | "greater_than" | "between";
  status: "good" | "warning" | "danger";
  unit: string;
  message: string;
  messageAr: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════

export interface GetSprayWindowsRequest {
  fieldId: string;
  days?: number; // default: 7
  startDate?: string;
  criteria?: Partial<SprayWindowCriteria>;
}

export interface GetIrrigationWindowsRequest {
  fieldId: string;
  days?: number; // default: 7
  startDate?: string;
}

export interface GetActionRecommendationsRequest {
  fieldId: string;
  actionTypes?: ActionType[];
  days?: number; // default: 7
}

export interface ActionWindowsResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  error_ar?: string;
  message?: string;
  message_ar?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Calculation Result Types
// ═══════════════════════════════════════════════════════════════════════════

export interface WindowCalculationResult {
  status: WindowStatus;
  score: number;
  suitability: Record<string, boolean>;
  warnings: string[];
  warningsAr: string[];
  recommendations: string[];
  recommendationsAr: string[];
}

export interface SoilMoistureData {
  current: number; // %
  target: number; // %
  fieldCapacity: number; // %
  wiltingPoint: number; // %
  timestamp: string;
}

export interface ETData {
  et0: number; // mm/day
  etc?: number; // mm/day
  kc?: number; // Crop coefficient
  date: string;
}
