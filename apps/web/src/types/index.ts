/**
 * SAHOOL Web Dashboard Types
 * أنواع لوحة التحكم
 *
 * This file re-exports shared types and adds web-specific extensions
 */

// Re-export all shared types from api-client
export type {
  // Core Types
  Locale,
  Priority,
  Severity,
  TaskStatus,
  DiagnosisStatus,
  FarmStatus,
  // Geometry Types
  Coordinates,
  GeoPosition,
  GeoPoint,
  GeoPolygon,
  GeoMultiPolygon,
  GeoLineString,
  GeoGeometry,
  GeoFeature,
  GeoFeatureCollection,
  // Domain Types
  Task,
  CreateTaskRequest,
  TaskEvidence,
  Field,
  Farm,
  WeatherData,
  WeatherForecast,
  DailyForecast,
  WeatherAlert,
  DiagnosisRecord,
  ExpertReview,
  DiagnosisStats,
  DashboardStats,
  DashboardData,
  FieldIndicators,
  Indicator,
  SensorReading,
  Equipment,
  Notification,
  CommunityPost,
  // Alert Types
  AlertSeverity,
  AlertCategory,
  AlertStatus,
  Alert,
  AlertFilters,
  AlertStats,
  // User & Auth Types
  UserRole,
  User,
  AuthState,
  LoginRequest,
  LoginResponse,
  // KPI Types
  TrendDirection,
  HealthStatus,
  KPI,
  // Other
  Governorate,
  Treatment,
  ApiResponse,
  PaginatedResponse,
  ApiClientConfig,
  ServicePorts,
} from "@sahool/api-client";

// ═══════════════════════════════════════════════════════════════════════════
// Web-specific type extensions
// ═══════════════════════════════════════════════════════════════════════════

import type {
  Field as BaseField,
  Alert as BaseAlert,
  KPI as BaseKPI,
  TrendDirection,
  HealthStatus,
  AlertSeverity,
  AlertCategory,
} from "@sahool/api-client";

/** Extended Field type with web dashboard display properties */
export interface DashboardField extends BaseField {
  farmName?: string;
  ndviTrend?: TrendDirection;
  healthStatus?: HealthStatus;
}

/** Dashboard state for the web app */
export interface DashboardState {
  kpis: BaseKPI[];
  alerts: BaseAlert[];
  fields: DashboardField[];
  selectedFieldId: string | null;
  isLoading: boolean;
  error: string | null;
}

// ═══════════════════════════════════════════════════════════════════════════
// WebSocket Types
// ═══════════════════════════════════════════════════════════════════════════

export type WSMessageType =
  | "kpi_update"
  | "alert_new"
  | "alert_dismiss"
  | "field_update"
  | "ndvi_update"
  | "weather_update"
  | "sensor_reading";

export interface WSMessage<T = unknown> {
  type: WSMessageType;
  payload: T;
  timestamp: string;
}

export interface WSKpiUpdatePayload {
  kpiId: string;
  value: number;
  trend: TrendDirection;
  trendValue: number;
}

export interface WSAlertPayload {
  alertId: string;
  alert?: BaseAlert;
}

export interface WSFieldUpdatePayload {
  fieldId: string;
  updates: Partial<DashboardField>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Filter Types
// ═══════════════════════════════════════════════════════════════════════════

export interface DashboardFilters {
  severities?: AlertSeverity[];
  categories?: AlertCategory[];
  fieldIds?: string[];
  farmIds?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Chart & Visualization Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface NDVITimeSeriesData {
  fieldId: string;
  fieldName: string;
  data: ChartDataPoint[];
  average: number;
  trend: TrendDirection;
}

export interface WeatherChartData {
  date: string;
  temperature: number;
  humidity: number;
  precipitation?: number;
}
