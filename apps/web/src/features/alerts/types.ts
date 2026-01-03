/**
 * Alerts Feature - Type Definitions
 * تعريفات أنواع ميزة التنبيهات
 */

// ═══════════════════════════════════════════════════════════════════════════
// Alert Enums and Base Types
// ═══════════════════════════════════════════════════════════════════════════

export type AlertSeverity = 'info' | 'warning' | 'critical' | 'emergency';
export type AlertCategory = 'crop_health' | 'weather' | 'irrigation' | 'pest' | 'disease' | 'market' | 'system';
export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed';

// ═══════════════════════════════════════════════════════════════════════════
// Alert Interface
// ═══════════════════════════════════════════════════════════════════════════

export interface Alert {
  id: string;
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  severity: AlertSeverity;
  category: AlertCategory;
  status: AlertStatus;
  fieldId?: string;
  fieldName?: string;
  fieldNameAr?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
  dismissedAt?: string;
  expiresAt?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Filter and Query Types
// ═══════════════════════════════════════════════════════════════════════════

export interface AlertFilters {
  severity?: AlertSeverity | AlertSeverity[];
  category?: AlertCategory | AlertCategory[];
  status?: AlertStatus | AlertStatus[];
  fieldId?: string;
  governorate?: string;
  startDate?: string;
  endDate?: string;
  search?: string;
}

export interface AlertListParams extends AlertFilters {
  page?: number;
  limit?: number;
  sortBy?: 'createdAt' | 'severity' | 'status';
  sortOrder?: 'asc' | 'desc';
}

// ═══════════════════════════════════════════════════════════════════════════
// Statistics Types
// ═══════════════════════════════════════════════════════════════════════════

export interface AlertStats {
  total: number;
  bySeverity: Record<AlertSeverity, number>;
  byCategory: Record<AlertCategory, number>;
  byStatus: Record<AlertStatus, number>;
  trend: 'increasing' | 'stable' | 'decreasing';
  trendPercentage?: number;
}

export interface AlertCount {
  count: number;
  bySeverity: Record<AlertSeverity, number>;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════════════════════════════════

export interface AlertListResponse {
  success: boolean;
  data?: Alert[];
  total?: number;
  page?: number;
  limit?: number;
  error?: string;
  errorAr?: string;
}

export interface AlertResponse {
  success: boolean;
  data?: Alert;
  error?: string;
  errorAr?: string;
}

export interface AlertStatsResponse {
  success: boolean;
  data?: AlertStats;
  error?: string;
  errorAr?: string;
}

export interface AlertCountResponse {
  success: boolean;
  data?: AlertCount;
  error?: string;
  errorAr?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Payload Types
// ═══════════════════════════════════════════════════════════════════════════

export interface CreateAlertPayload {
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  severity: AlertSeverity;
  category: AlertCategory;
  fieldId?: string;
  metadata?: Record<string, unknown>;
  expiresAt?: string;
}

export interface UpdateAlertPayload {
  title?: string;
  titleAr?: string;
  message?: string;
  messageAr?: string;
  severity?: AlertSeverity;
  category?: AlertCategory;
  metadata?: Record<string, unknown>;
}

export interface AcknowledgeAlertPayload {
  alertId: string;
  notes?: string;
}

export interface ResolveAlertPayload {
  alertId: string;
  resolution?: string;
  notes?: string;
}

export interface DismissAlertPayload {
  alertId: string;
  reason?: string;
}

export interface BulkAlertActionPayload {
  alertIds: string[];
  action: 'acknowledge' | 'resolve' | 'dismiss';
  notes?: string;
  reason?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Alert Stream Types
// ═══════════════════════════════════════════════════════════════════════════

export interface AlertStreamEvent {
  type: 'new' | 'update' | 'delete';
  alert: Alert;
  timestamp: string;
}

export interface AlertStreamOptions {
  filters?: AlertFilters;
  reconnect?: boolean;
  reconnectDelay?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Hook Return Types
// ═══════════════════════════════════════════════════════════════════════════

export interface UseAlertsReturn {
  data: Alert[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface UseAlertReturn {
  data: Alert | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface UseAlertStatsReturn {
  data: AlertStats | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

export interface UseAlertStreamReturn {
  isConnected: boolean;
  error: Error | null;
  disconnect: () => void;
  reconnect: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages
// ═══════════════════════════════════════════════════════════════════════════

export interface BilingualMessage {
  en: string;
  ar: string;
}

export interface AlertErrorMessages {
  NETWORK_ERROR: BilingualMessage;
  FETCH_FAILED: BilingualMessage;
  CREATE_FAILED: BilingualMessage;
  UPDATE_FAILED: BilingualMessage;
  DELETE_FAILED: BilingualMessage;
  ACKNOWLEDGE_FAILED: BilingualMessage;
  RESOLVE_FAILED: BilingualMessage;
  DISMISS_FAILED: BilingualMessage;
  INVALID_DATA: BilingualMessage;
  NOT_FOUND: BilingualMessage;
  UNAUTHORIZED: BilingualMessage;
}
