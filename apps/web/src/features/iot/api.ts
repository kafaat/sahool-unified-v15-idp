/**
 * IoT & Sensors Feature - API Layer
 * طبقة API لميزة إنترنت الأشياء والمستشعرات
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
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
import { API_PREFIX } from '@sahool/shared-types/contracts';

const IOT_SENSORS_BASE = `${API_PREFIX}/iot/sensors`;
const IOT_ACTUATORS_BASE = `${API_PREFIX}/iot/actuators`;
const IOT_ALERT_RULES_BASE = `${API_PREFIX}/iot/alert-rules`;

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_SENSORS_FAILED: {
    en: 'Failed to fetch sensors. Using cached data.',
    ar: 'فشل في جلب المستشعرات. استخدام البيانات المخزنة.',
  },
  FETCH_ACTUATORS_FAILED: {
    en: 'Failed to fetch actuators. Using cached data.',
    ar: 'فشل في جلب المُشغلات. استخدام البيانات المخزنة.',
  },
  FETCH_READINGS_FAILED: {
    en: 'Failed to fetch sensor readings.',
    ar: 'فشل في جلب قراءات المستشعر.',
  },
};

// Sensors API
export const sensorsApi = {
  /**
   * Get all sensors with filters
   * جلب جميع المستشعرات مع الفلاتر
   */
  getSensors: async (filters?: SensorFilters): Promise<Sensor[]> => {
    return safeFetch(IOT_SENSORS_BASE, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${IOT_SENSORS_BASE}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get sensor by ID
   * جلب مستشعر بواسطة المعرّف
   */
  getSensorById: async (id: string): Promise<Sensor> => {
    return safeFetch(`${IOT_SENSORS_BASE}/${id}`, async () => {
      const response = await api.get(`${IOT_SENSORS_BASE}/${id}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Create new sensor
   * إنشاء مستشعر جديد
   */
  createSensor: async (data: Omit<Sensor, 'id' | 'createdAt' | 'updatedAt'>): Promise<Sensor> => {
    return safeFetch(IOT_SENSORS_BASE, async () => {
      const response = await api.post(IOT_SENSORS_BASE, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Update sensor
   * تحديث مستشعر
   */
  updateSensor: async (id: string, data: Partial<Sensor>): Promise<Sensor> => {
    return safeFetch(`${IOT_SENSORS_BASE}/${id}`, async () => {
      const response = await api.put(`${IOT_SENSORS_BASE}/${id}`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Delete sensor
   * حذف مستشعر
   */
  deleteSensor: async (id: string): Promise<void> => {
    return safeFetch(`${IOT_SENSORS_BASE}/${id}`, async () => {
      await api.delete(`${IOT_SENSORS_BASE}/${id}`);
    });
  },

  /**
   * Get sensor readings
   * جلب قراءات المستشعر
   */
  getSensorReadings: async (query: SensorReadingsQuery): Promise<SensorReading[]> => {
    return safeFetch(`${IOT_SENSORS_BASE}/readings`, async () => {
      const params = new URLSearchParams();
      params.set('sensor_id', query.sensorId);
      if (query.startDate) params.set('start_date', query.startDate);
      if (query.endDate) params.set('end_date', query.endDate);
      if (query.interval) params.set('interval', query.interval);
      if (query.limit) params.set('limit', query.limit.toString());
      const response = await api.get(`${IOT_SENSORS_BASE}/readings?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get latest sensor reading
   * جلب أحدث قراءة للمستشعر
   */
  getLatestReading: async (sensorId: string): Promise<SensorReading> => {
    return safeFetch(`${IOT_SENSORS_BASE}/${sensorId}/latest`, async () => {
      const response = await api.get(`${IOT_SENSORS_BASE}/${sensorId}/latest`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get sensor statistics
   * جلب إحصائيات المستشعرات
   */
  getStats: async (): Promise<{ total: number; active: number; byType: Record<string, number>; byStatus: Record<string, number> }> => {
    return safeFetch(`${IOT_SENSORS_BASE}/stats`, async () => {
      const response = await api.get(`${IOT_SENSORS_BASE}/stats`);
      return response.data.data || response.data;
    });
  },

  /**
   * Subscribe to real-time sensor readings (returns EventSource URL)
   * الاشتراك في قراءات المستشعر في الوقت الفعلي
   */
  getStreamUrl: (sensorId?: string): string => {
    const params = sensorId ? `?sensor_id=${sensorId}` : '';
    return `${api.defaults.baseURL}${IOT_SENSORS_BASE}/stream${params}`;
  },
};

// Actuators API
export const actuatorsApi = {
  /**
   * Get all actuators
   * جلب جميع المُشغلات
   */
  getActuators: async (fieldId?: string): Promise<Actuator[]> => {
    return safeFetch(IOT_ACTUATORS_BASE, async () => {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${IOT_ACTUATORS_BASE}${params}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get actuator by ID
   * جلب مُشغل بواسطة المعرّف
   */
  getActuatorById: async (id: string): Promise<Actuator> => {
    return safeFetch(`${IOT_ACTUATORS_BASE}/${id}`, async () => {
      const response = await api.get(`${IOT_ACTUATORS_BASE}/${id}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Create new actuator
   * إنشاء مُشغل جديد
   */
  createActuator: async (
    data: Omit<Actuator, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<Actuator> => {
    return safeFetch(IOT_ACTUATORS_BASE, async () => {
      const response = await api.post(IOT_ACTUATORS_BASE, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Update actuator
   * تحديث مُشغل
   */
  updateActuator: async (id: string, data: Partial<Actuator>): Promise<Actuator> => {
    return safeFetch(`${IOT_ACTUATORS_BASE}/${id}`, async () => {
      const response = await api.put(`${IOT_ACTUATORS_BASE}/${id}`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Delete actuator
   * حذف مُشغل
   */
  deleteActuator: async (id: string): Promise<void> => {
    return safeFetch(`${IOT_ACTUATORS_BASE}/${id}`, async () => {
      await api.delete(`${IOT_ACTUATORS_BASE}/${id}`);
    });
  },

  /**
   * Control actuator
   * التحكم في المُشغل
   */
  controlActuator: async (data: ActuatorControlData): Promise<Actuator> => {
    return safeFetch(`${IOT_ACTUATORS_BASE}/${data.actuatorId}/control`, async () => {
      const response = await api.post(`${IOT_ACTUATORS_BASE}/${data.actuatorId}/control`, {
        action: data.action,
        mode: data.mode,
        duration: data.duration,
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Set actuator mode
   * تعيين وضع المُشغل
   */
  setMode: async (
    actuatorId: string,
    mode: 'manual' | 'automatic' | 'scheduled'
  ): Promise<Actuator> => {
    return safeFetch(`${IOT_ACTUATORS_BASE}/${actuatorId}/mode`, async () => {
      const response = await api.patch(`${IOT_ACTUATORS_BASE}/${actuatorId}/mode`, { mode });
      return response.data.data || response.data;
    });
  },
};

// Alert Rules API
export const alertRulesApi = {
  /**
   * Get all alert rules
   * جلب جميع قواعد التنبيه
   */
  getAlertRules: async (sensorId?: string): Promise<AlertRule[]> => {
    return safeFetch(IOT_ALERT_RULES_BASE, async () => {
      const params = sensorId ? `?sensor_id=${sensorId}` : '';
      const response = await api.get(`${IOT_ALERT_RULES_BASE}${params}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get alert rule by ID
   * جلب قاعدة تنبيه بواسطة المعرّف
   */
  getAlertRuleById: async (id: string): Promise<AlertRule> => {
    return safeFetch(`${IOT_ALERT_RULES_BASE}/${id}`, async () => {
      const response = await api.get(`${IOT_ALERT_RULES_BASE}/${id}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Create alert rule
   * إنشاء قاعدة تنبيه
   */
  createAlertRule: async (data: AlertRuleFormData): Promise<AlertRule> => {
    return safeFetch(IOT_ALERT_RULES_BASE, async () => {
      const response = await api.post(IOT_ALERT_RULES_BASE, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Update alert rule
   * تحديث قاعدة تنبيه
   */
  updateAlertRule: async (id: string, data: Partial<AlertRuleFormData>): Promise<AlertRule> => {
    return safeFetch(`${IOT_ALERT_RULES_BASE}/${id}`, async () => {
      const response = await api.put(`${IOT_ALERT_RULES_BASE}/${id}`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Delete alert rule
   * حذف قاعدة تنبيه
   */
  deleteAlertRule: async (id: string): Promise<void> => {
    return safeFetch(`${IOT_ALERT_RULES_BASE}/${id}`, async () => {
      await api.delete(`${IOT_ALERT_RULES_BASE}/${id}`);
    });
  },

  /**
   * Toggle alert rule
   * تبديل تفعيل قاعدة التنبيه
   */
  toggleAlertRule: async (id: string, enabled: boolean): Promise<AlertRule> => {
    return safeFetch(`${IOT_ALERT_RULES_BASE}/${id}/toggle`, async () => {
      const response = await api.patch(`${IOT_ALERT_RULES_BASE}/${id}/toggle`, {
        enabled,
      });
      return response.data.data || response.data;
    });
  },
};
