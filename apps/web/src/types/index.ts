/**
 * SAHOOL Web Dashboard Types
 * أنواع لوحة التحكم
 */

// ═══════════════════════════════════════════════════════════════
// KPI Types
// ═══════════════════════════════════════════════════════════════

export interface KPI {
  id: string;
  label: string;
  labelAr: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  trendValue: number;
  status: 'good' | 'warning' | 'critical';
  icon: string;
}

// ═══════════════════════════════════════════════════════════════
// Alert Types
// ═══════════════════════════════════════════════════════════════

export type AlertSeverity = 'info' | 'warning' | 'critical';
export type AlertCategory = 'ndvi' | 'weather' | 'irrigation' | 'pest' | 'system';

export interface Alert {
  id: string;
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  severity: AlertSeverity;
  category: AlertCategory;
  fieldId?: string;
  fieldName?: string;
  createdAt: string;
  read: boolean;
  actionUrl?: string;
}

// ═══════════════════════════════════════════════════════════════
// Field Types
// ═══════════════════════════════════════════════════════════════

export interface Field {
  id: string;
  name: string;
  farmName: string;
  crop: string;
  areaHectares: number;
  geometry: GeoJSON.Polygon;
  ndviCurrent?: number;
  ndviTrend?: 'rising' | 'falling' | 'stable';
  healthStatus?: 'healthy' | 'moderate' | 'stressed' | 'critical';
  lastUpdated: string;
}

// ═══════════════════════════════════════════════════════════════
// Dashboard State
// ═══════════════════════════════════════════════════════════════

export interface DashboardState {
  kpis: KPI[];
  alerts: Alert[];
  fields: Field[];
  selectedFieldId: string | null;
  isLoading: boolean;
  error: string | null;
}

// ═══════════════════════════════════════════════════════════════
// WebSocket Types
// ═══════════════════════════════════════════════════════════════

export type WSMessageType =
  | 'kpi_update'
  | 'alert_new'
  | 'alert_dismiss'
  | 'field_update'
  | 'ndvi_update';

export interface WSMessage {
  type: WSMessageType;
  payload: unknown;
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════════════════════

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ═══════════════════════════════════════════════════════════════
// User & Auth Types
// ═══════════════════════════════════════════════════════════════

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'manager' | 'operator' | 'viewer';
  tenantId: string;
  avatar?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
