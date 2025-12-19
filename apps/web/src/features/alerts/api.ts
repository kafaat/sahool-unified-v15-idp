/**
 * Alerts Feature - API Layer
 * طبقة API لميزة التنبيهات
 */

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export type AlertSeverity = 'info' | 'warning' | 'critical' | 'emergency';
export type AlertCategory = 'crop_health' | 'weather' | 'irrigation' | 'pest' | 'disease' | 'market' | 'system';
export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed';

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
  metadata: Record<string, unknown>;
  createdAt: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
  expiresAt?: string;
}

export interface AlertFilters {
  severity?: AlertSeverity;
  category?: AlertCategory;
  status?: AlertStatus;
  fieldId?: string;
  governorate?: string;
  startDate?: string;
  endDate?: string;
}

export interface AlertStats {
  total: number;
  bySeverity: Record<AlertSeverity, number>;
  byCategory: Record<AlertCategory, number>;
  byStatus: Record<AlertStatus, number>;
  trend: 'increasing' | 'stable' | 'decreasing';
}

// API Functions
export const alertsApi = {
  /**
   * Get all alerts with filters
   */
  getAlerts: async (filters?: AlertFilters): Promise<Alert[]> => {
    const params = new URLSearchParams();
    if (filters?.severity) params.set('severity', filters.severity);
    if (filters?.category) params.set('category', filters.category);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.fieldId) params.set('field_id', filters.fieldId);
    if (filters?.governorate) params.set('governorate', filters.governorate);

    const response = await api.get(`/v1/alerts?${params.toString()}`);
    return response.data;
  },

  /**
   * Get active alerts count
   */
  getActiveCount: async (): Promise<{ count: number; bySeverity: Record<AlertSeverity, number> }> => {
    const response = await api.get('/v1/alerts/count');
    return response.data;
  },

  /**
   * Get alert by ID
   */
  getAlertById: async (id: string): Promise<Alert> => {
    const response = await api.get(`/v1/alerts/${id}`);
    return response.data;
  },

  /**
   * Acknowledge alert
   */
  acknowledgeAlert: async (id: string): Promise<Alert> => {
    const response = await api.post(`/v1/alerts/${id}/acknowledge`);
    return response.data;
  },

  /**
   * Resolve alert
   */
  resolveAlert: async (id: string, resolution?: string): Promise<Alert> => {
    const response = await api.post(`/v1/alerts/${id}/resolve`, { resolution });
    return response.data;
  },

  /**
   * Dismiss alert
   */
  dismissAlert: async (id: string): Promise<void> => {
    await api.post(`/v1/alerts/${id}/dismiss`);
  },

  /**
   * Get alert statistics
   */
  getStats: async (governorate?: string): Promise<AlertStats> => {
    const params = governorate ? `?governorate=${governorate}` : '';
    const response = await api.get(`/v1/alerts/stats${params}`);
    return response.data;
  },

  /**
   * Subscribe to real-time alerts (returns EventSource URL)
   */
  getStreamUrl: (): string => {
    return `${api.defaults.baseURL}/v1/alerts/stream`;
  },
};
