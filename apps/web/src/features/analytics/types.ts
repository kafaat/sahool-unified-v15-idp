/**
 * Analytics Feature - Type Definitions
 * تعريفات الأنواع لميزة التحليلات
 */

// Time period for analytics
export type AnalyticsPeriod = 'week' | 'month' | 'season' | 'year' | 'custom';

// Metric types
export type MetricType = 'yield' | 'cost' | 'revenue' | 'profit' | 'water_usage' | 'fertilizer_usage';

// Chart types
export type ChartType = 'line' | 'bar' | 'pie' | 'area';

// Comparison types
export type ComparisonType = 'fields' | 'seasons' | 'crops';

// Analytics data point
export interface DataPoint {
  date: string;
  value: number;
  label?: string;
  labelAr?: string;
}

// Yield analysis data
export interface YieldData {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  totalYield: number; // kg
  expectedYield: number; // kg
  yieldPerHectare: number;
  area: number; // hectares
  season: string;
  harvestDate?: string;
  variance: number; // percentage difference from expected
  timeSeries: DataPoint[];
}

// Cost analysis data
export interface CostData {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  totalCost: number;
  breakdown: CostBreakdown;
  costPerHectare: number;
  period: {
    start: string;
    end: string;
  };
}

// Cost breakdown by category
export interface CostBreakdown {
  seeds: number;
  fertilizers: number;
  pesticides: number;
  irrigation: number;
  labor: number;
  equipment: number;
  other: number;
}

// Revenue and profit data
export interface RevenueData {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  revenue: number;
  cost: number;
  profit: number;
  profitMargin: number; // percentage
  roi: number; // return on investment percentage
  period: {
    start: string;
    end: string;
  };
}

// KPI metrics
export interface KPIMetric {
  id: string;
  name: string;
  nameAr: string;
  value: number;
  unit: string;
  unitAr: string;
  change: number; // percentage change
  trend: 'up' | 'down' | 'stable';
  status: 'good' | 'warning' | 'critical';
  icon: string;
  description?: string;
  descriptionAr?: string;
}

// Comparison data
export interface ComparisonData {
  type: ComparisonType;
  items: ComparisonItem[];
  metric: MetricType;
  period: {
    start: string;
    end: string;
  };
}

export interface ComparisonItem {
  id: string;
  name: string;
  nameAr: string;
  value: number;
  data: DataPoint[];
  metadata?: Record<string, unknown>;
}

// Report configuration
export interface ReportConfig {
  title: string;
  titleAr: string;
  period: {
    start: string;
    end: string;
  };
  sections: ReportSection[];
  includeCharts: boolean;
  includeTables: boolean;
  format: 'pdf' | 'excel' | 'csv';
  language: 'en' | 'ar' | 'both';
}

export type ReportSectionType =
  | 'summary'
  | 'yield_analysis'
  | 'cost_analysis'
  | 'revenue_analysis'
  | 'comparison'
  | 'recommendations';

export interface ReportSection {
  type: ReportSectionType;
  enabled: boolean;
  config?: Record<string, unknown>;
}

// Analytics filters
export interface AnalyticsFilters {
  fieldIds?: string[];
  cropTypes?: string[];
  period?: AnalyticsPeriod;
  startDate?: string;
  endDate?: string;
  seasons?: string[];
}

// Analytics summary
export interface AnalyticsSummary {
  totalFields: number;
  totalArea: number; // hectares
  totalYield: number; // kg
  totalRevenue: number;
  totalCost: number;
  totalProfit: number;
  averageYieldPerHectare: number;
  topPerformingField?: {
    id: string;
    name: string;
    nameAr: string;
    yieldPerHectare: number;
  };
  period: {
    start: string;
    end: string;
  };
}

// Resource usage analytics
export interface ResourceUsage {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  waterUsage: number; // cubic meters
  fertilizerUsage: number; // kg
  pesticideUsage: number; // liters
  energyUsage: number; // kWh
  period: {
    start: string;
    end: string;
  };
  efficiency: {
    waterPerKg: number;
    fertilizerPerKg: number;
    energyPerKg: number;
  };
}

// Harvest Planning Types
export type ReadinessStatus = 'ready' | 'almost_ready' | 'not_ready';
export type QualityGrade = 'premium' | 'grade_a' | 'grade_b' | 'grade_c';
export type EquipmentStatus = 'available' | 'in_use' | 'maintenance' | 'unavailable';

export interface WeatherForecast {
  date: string;
  dateAr: string;
  tempHigh: number;
  tempLow: number;
  precipitation: number;
  humidity: number;
  windSpeed: number;
  condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy';
  conditionAr: string;
  harvestSuitability: 'excellent' | 'good' | 'fair' | 'poor';
  harvestSuitabilityAr: string;
}

export interface HarvestWindow {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  startDate: string;
  endDate: string;
  optimalDate: string;
  confidence: number;
  reason: string;
  reasonAr: string;
}

export interface FieldReadiness {
  fieldId: string;
  fieldName: string;
  fieldNameAr: string;
  cropType: string;
  cropTypeAr: string;
  area: number;
  location: {
    lat: number;
    lng: number;
    region: string;
    regionAr: string;
  };
  status: ReadinessStatus;
  statusAr: string;
  maturityLevel: number;
  moistureContent: number;
  optimalMoisture: number;
  daysToOptimal: number;
  predictedYield: number;
  yieldPerHectare: number;
  qualityGrade: QualityGrade;
  qualityGradeAr: string;
  qualityScore: number;
  priority: number;
  lastUpdated: string;
}

export interface Equipment {
  id: string;
  name: string;
  nameAr: string;
  type: string;
  typeAr: string;
  status: EquipmentStatus;
  statusAr: string;
  capacity: number;
  availableDate?: string;
  assignedField?: string;
  maintenanceDue?: string;
  efficiency: number;
}

export interface HarvestPlan {
  id: string;
  farmId: string;
  season: string;
  fields: FieldReadiness[];
  harvestWindows: HarvestWindow[];
  equipment: Equipment[];
  weatherForecast: WeatherForecast[];
  totalArea: number;
  totalPredictedYield: number;
  estimatedDuration: number;
  createdAt: string;
  updatedAt: string;
}
