/**
 * IoT & Sensors Feature - API Layer
 * طبقة API لميزة إنترنت الأشياء والمستشعرات
 */

import axios from 'axios';
import type {
  Sensor,
  SensorFilters,
  SensorReading,
  SensorReadingsQuery,
  Actuator,
  ActuatorControlData,
  AlertRule,
  AlertRuleFormData,
} from './types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sensors API
export const sensorsApi = {
  /**
   * Get all sensors with filters
   */
  getSensors: async (filters?: SensorFilters): Promise<Sensor[]> => {
    const params = new URLSearchParams();
    if (filters?.type) params.set('type', filters.type);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.fieldId) params.set('field_id', filters.fieldId);
    if (filters?.search) params.set('search', filters.search);

    const response = await api.get(`/v1/iot/sensors?${params.toString()}`);
    return response.data;
  },

  /**
   * Get sensor by ID
   */
  getSensorById: async (id: string): Promise<Sensor> => {
    const response = await api.get(`/v1/iot/sensors/${id}`);
    return response.data;
  },

  /**
   * Get sensor readings
   */
  getSensorReadings: async (query: SensorReadingsQuery): Promise<SensorReading[]> => {
    const params = new URLSearchParams();
    params.set('sensor_id', query.sensorId);
    if (query.startDate) params.set('start_date', query.startDate);
    if (query.endDate) params.set('end_date', query.endDate);
    if (query.interval) params.set('interval', query.interval);

    const response = await api.get(`/v1/iot/sensors/readings?${params.toString()}`);
    return response.data;
  },

  /**
   * Get latest sensor reading
   */
  getLatestReading: async (sensorId: string): Promise<SensorReading> => {
    const response = await api.get(`/v1/iot/sensors/${sensorId}/latest`);
    return response.data;
  },

  /**
   * Get sensor statistics
   */
  getStats: async (): Promise<{
    total: number;
    active: number;
    byType: Record<string, number>;
    byStatus: Record<string, number>;
  }> => {
    const response = await api.get('/v1/iot/sensors/stats');
    return response.data;
  },

  /**
   * Subscribe to real-time sensor readings (returns EventSource URL)
   */
  getStreamUrl: (sensorId?: string): string => {
    const params = sensorId ? `?sensor_id=${sensorId}` : '';
    return `${api.defaults.baseURL}/v1/iot/sensors/stream${params}`;
  },
};

// Actuators API
export const actuatorsApi = {
  /**
   * Get all actuators
   */
  getActuators: async (fieldId?: string): Promise<Actuator[]> => {
    const params = fieldId ? `?field_id=${fieldId}` : '';
    const response = await api.get(`/v1/iot/actuators${params}`);
    return response.data;
  },

  /**
   * Get actuator by ID
   */
  getActuatorById: async (id: string): Promise<Actuator> => {
    const response = await api.get(`/v1/iot/actuators/${id}`);
    return response.data;
  },

  /**
   * Control actuator
   */
  controlActuator: async (data: ActuatorControlData): Promise<Actuator> => {
    const response = await api.post(`/v1/iot/actuators/${data.actuatorId}/control`, {
      action: data.action,
      mode: data.mode,
      duration: data.duration,
    });
    return response.data;
  },

  /**
   * Set actuator mode
   */
  setMode: async (actuatorId: string, mode: 'manual' | 'automatic' | 'scheduled'): Promise<Actuator> => {
    const response = await api.patch(`/v1/iot/actuators/${actuatorId}/mode`, { mode });
    return response.data;
  },
};

// Alert Rules API
export const alertRulesApi = {
  /**
   * Get all alert rules
   */
  getAlertRules: async (sensorId?: string): Promise<AlertRule[]> => {
    const params = sensorId ? `?sensor_id=${sensorId}` : '';
    const response = await api.get(`/v1/iot/alert-rules${params}`);
    return response.data;
  },

  /**
   * Get alert rule by ID
   */
  getAlertRuleById: async (id: string): Promise<AlertRule> => {
    const response = await api.get(`/v1/iot/alert-rules/${id}`);
    return response.data;
  },

  /**
   * Create alert rule
   */
  createAlertRule: async (data: AlertRuleFormData): Promise<AlertRule> => {
    const response = await api.post('/v1/iot/alert-rules', data);
    return response.data;
  },

  /**
   * Update alert rule
   */
  updateAlertRule: async (id: string, data: Partial<AlertRuleFormData>): Promise<AlertRule> => {
    const response = await api.put(`/v1/iot/alert-rules/${id}`, data);
    return response.data;
  },

  /**
   * Delete alert rule
   */
  deleteAlertRule: async (id: string): Promise<void> => {
    await api.delete(`/v1/iot/alert-rules/${id}`);
  },

  /**
   * Toggle alert rule
   */
  toggleAlertRule: async (id: string, enabled: boolean): Promise<AlertRule> => {
    const response = await api.patch(`/v1/iot/alert-rules/${id}/toggle`, { enabled });
    return response.data;
  },
};
