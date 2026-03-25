/**
 * IoT & Sensors Feature - API Layer
 * طبقة API لميزة إنترنت الأشياء والمستشعرات
 */

import { createApiClient, logger } from '@/lib/api/factory';
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

// Mock data for fallback (extracted to separate file for bundle optimization)
import { MOCK_SENSORS, MOCK_ACTUATORS, MOCK_ALERT_RULES } from './api.mock';

// Sensors API
export const sensorsApi = {
  /**
   * Get all sensors with filters
   * جلب جميع المستشعرات مع الفلاتر
   */
  getSensors: async (filters?: SensorFilters): Promise<Sensor[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${IOT_SENSORS_BASE}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format for sensors, using mock data');
      return MOCK_SENSORS;
    } catch (error) {
      logger.warn('Failed to fetch sensors from API, using mock data:', error);
      return MOCK_SENSORS;
    }
  },

  /**
   * Get sensor by ID
   * جلب مستشعر بواسطة المعرّف
   */
  getSensorById: async (id: string): Promise<Sensor> => {
    try {
      const response = await api.get(`${IOT_SENSORS_BASE}/${id}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(`Failed to fetch sensor ${id} from API, using mock data:`, error);
      const mockSensor = MOCK_SENSORS.find((s) => s.id === id);
      if (mockSensor) return mockSensor;
      throw new Error(`Sensor ${id} not found`);
    }
  },

  /**
   * Create new sensor
   * إنشاء مستشعر جديد
   */
  createSensor: async (data: Omit<Sensor, 'id' | 'createdAt' | 'updatedAt'>): Promise<Sensor> => {
    try {
      const response = await api.post(IOT_SENSORS_BASE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create sensor:', error);
      throw error;
    }
  },

  /**
   * Update sensor
   * تحديث مستشعر
   */
  updateSensor: async (id: string, data: Partial<Sensor>): Promise<Sensor> => {
    try {
      const response = await api.put(`${IOT_SENSORS_BASE}/${id}`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update sensor ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete sensor
   * حذف مستشعر
   */
  deleteSensor: async (id: string): Promise<void> => {
    try {
      await api.delete(`${IOT_SENSORS_BASE}/${id}`);
    } catch (error) {
      logger.error(`Failed to delete sensor ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get sensor readings
   * جلب قراءات المستشعر
   */
  getSensorReadings: async (query: SensorReadingsQuery): Promise<SensorReading[]> => {
    try {
      const params = new URLSearchParams();
      params.set('sensor_id', query.sensorId);
      if (query.startDate) params.set('start_date', query.startDate);
      if (query.endDate) params.set('end_date', query.endDate);
      if (query.interval) params.set('interval', query.interval);
      if (query.limit) params.set('limit', query.limit.toString());

      const response = await api.get(`${IOT_SENSORS_BASE}/readings?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format for readings');
      return [];
    } catch (error) {
      logger.warn('Failed to fetch sensor readings from API:', error);
      return [];
    }
  },

  /**
   * Get latest sensor reading
   * جلب أحدث قراءة للمستشعر
   */
  getLatestReading: async (sensorId: string): Promise<SensorReading> => {
    try {
      const response = await api.get(`${IOT_SENSORS_BASE}/${sensorId}/latest`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(`Failed to fetch latest reading for sensor ${sensorId}:`, error);
      throw error;
    }
  },

  /**
   * Get sensor statistics
   * جلب إحصائيات المستشعرات
   */
  getStats: async (): Promise<{
    total: number;
    active: number;
    byType: Record<string, number>;
    byStatus: Record<string, number>;
  }> => {
    try {
      const response = await api.get(`${IOT_SENSORS_BASE}/stats`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn('Failed to fetch sensor stats from API, using mock data:', error);
      return {
        total: MOCK_SENSORS.length,
        active: MOCK_SENSORS.filter((s) => s.status === 'active').length,
        byType: {
          soil_moisture: 1,
          temperature: 1,
          humidity: 1,
        },
        byStatus: {
          active: 3,
          offline: 0,
        },
      };
    }
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
    try {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${IOT_ACTUATORS_BASE}${params}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format for actuators, using mock data');
      return MOCK_ACTUATORS;
    } catch (error) {
      logger.warn('Failed to fetch actuators from API, using mock data:', error);
      return MOCK_ACTUATORS;
    }
  },

  /**
   * Get actuator by ID
   * جلب مُشغل بواسطة المعرّف
   */
  getActuatorById: async (id: string): Promise<Actuator> => {
    try {
      const response = await api.get(`${IOT_ACTUATORS_BASE}/${id}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(`Failed to fetch actuator ${id} from API, using mock data:`, error);
      const mockActuator = MOCK_ACTUATORS.find((a) => a.id === id);
      if (mockActuator) return mockActuator;
      throw new Error(`Actuator ${id} not found`);
    }
  },

  /**
   * Create new actuator
   * إنشاء مُشغل جديد
   */
  createActuator: async (
    data: Omit<Actuator, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<Actuator> => {
    try {
      const response = await api.post(IOT_ACTUATORS_BASE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create actuator:', error);
      throw error;
    }
  },

  /**
   * Update actuator
   * تحديث مُشغل
   */
  updateActuator: async (id: string, data: Partial<Actuator>): Promise<Actuator> => {
    try {
      const response = await api.put(`${IOT_ACTUATORS_BASE}/${id}`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update actuator ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete actuator
   * حذف مُشغل
   */
  deleteActuator: async (id: string): Promise<void> => {
    try {
      await api.delete(`${IOT_ACTUATORS_BASE}/${id}`);
    } catch (error) {
      logger.error(`Failed to delete actuator ${id}:`, error);
      throw error;
    }
  },

  /**
   * Control actuator
   * التحكم في المُشغل
   */
  controlActuator: async (data: ActuatorControlData): Promise<Actuator> => {
    try {
      const response = await api.post(`${IOT_ACTUATORS_BASE}/${data.actuatorId}/control`, {
        action: data.action,
        mode: data.mode,
        duration: data.duration,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to control actuator ${data.actuatorId}:`, error);
      throw error;
    }
  },

  /**
   * Set actuator mode
   * تعيين وضع المُشغل
   */
  setMode: async (
    actuatorId: string,
    mode: 'manual' | 'automatic' | 'scheduled'
  ): Promise<Actuator> => {
    try {
      const response = await api.patch(`${IOT_ACTUATORS_BASE}/${actuatorId}/mode`, { mode });
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to set mode for actuator ${actuatorId}:`, error);
      throw error;
    }
  },
};

// Alert Rules API
export const alertRulesApi = {
  /**
   * Get all alert rules
   * جلب جميع قواعد التنبيه
   */
  getAlertRules: async (sensorId?: string): Promise<AlertRule[]> => {
    try {
      const params = sensorId ? `?sensor_id=${sensorId}` : '';
      const response = await api.get(`${IOT_ALERT_RULES_BASE}${params}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format for alert rules, using mock data');
      return MOCK_ALERT_RULES;
    } catch (error) {
      logger.warn('Failed to fetch alert rules from API, using mock data:', error);
      return MOCK_ALERT_RULES;
    }
  },

  /**
   * Get alert rule by ID
   * جلب قاعدة تنبيه بواسطة المعرّف
   */
  getAlertRuleById: async (id: string): Promise<AlertRule> => {
    try {
      const response = await api.get(`${IOT_ALERT_RULES_BASE}/${id}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(`Failed to fetch alert rule ${id} from API, using mock data:`, error);
      const mockRule = MOCK_ALERT_RULES.find((r) => r.id === id);
      if (mockRule) return mockRule;
      throw new Error(`Alert rule ${id} not found`);
    }
  },

  /**
   * Create alert rule
   * إنشاء قاعدة تنبيه
   */
  createAlertRule: async (data: AlertRuleFormData): Promise<AlertRule> => {
    try {
      const response = await api.post(IOT_ALERT_RULES_BASE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create alert rule:', error);
      throw error;
    }
  },

  /**
   * Update alert rule
   * تحديث قاعدة تنبيه
   */
  updateAlertRule: async (id: string, data: Partial<AlertRuleFormData>): Promise<AlertRule> => {
    try {
      const response = await api.put(`${IOT_ALERT_RULES_BASE}/${id}`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update alert rule ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete alert rule
   * حذف قاعدة تنبيه
   */
  deleteAlertRule: async (id: string): Promise<void> => {
    try {
      await api.delete(`${IOT_ALERT_RULES_BASE}/${id}`);
    } catch (error) {
      logger.error(`Failed to delete alert rule ${id}:`, error);
      throw error;
    }
  },

  /**
   * Toggle alert rule
   * تبديل تفعيل قاعدة التنبيه
   */
  toggleAlertRule: async (id: string, enabled: boolean): Promise<AlertRule> => {
    try {
      const response = await api.patch(`${IOT_ALERT_RULES_BASE}/${id}/toggle`, {
        enabled,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to toggle alert rule ${id}:`, error);
      throw error;
    }
  },
};
