/**
 * IoT & Sensors Feature - API Layer
 * طبقة API لميزة إنترنت الأشياء والمستشعرات
 */

import axios from 'axios';
import { logger } from '@/lib/logger';
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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
import Cookies from 'js-cookie';

api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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

// Mock data for fallback
const MOCK_SENSORS: Sensor[] = [
  {
    id: '1',
    name: 'Soil Moisture Sensor 1',
    nameAr: 'مستشعر رطوبة التربة 1',
    type: 'soil_moisture',
    status: 'active',
    deviceId: 'SMS-001',
    unit: '%',
    unitAr: '%',
    location: {
      latitude: 15.3694,
      longitude: 44.191,
      fieldId: 'field-1',
      fieldName: 'North Field',
    },
    lastReading: {
      value: 45,
      unit: '%',
      timestamp: new Date().toISOString(),
    },
    battery: 85,
    signalStrength: 92,
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'Temperature Sensor 1',
    nameAr: 'مستشعر درجة الحرارة 1',
    type: 'temperature',
    status: 'active',
    deviceId: 'TEMP-001',
    unit: '°C',
    unitAr: '°م',
    location: {
      latitude: 15.3695,
      longitude: 44.192,
      fieldId: 'field-1',
      fieldName: 'North Field',
    },
    lastReading: {
      value: 28,
      unit: '°C',
      timestamp: new Date().toISOString(),
    },
    battery: 78,
    signalStrength: 88,
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 25).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    name: 'Humidity Sensor 1',
    nameAr: 'مستشعر الرطوبة 1',
    type: 'humidity',
    status: 'active',
    deviceId: 'HUM-001',
    unit: '%',
    unitAr: '%',
    location: {
      latitude: 15.3696,
      longitude: 44.193,
      fieldId: 'field-2',
      fieldName: 'South Field',
    },
    lastReading: {
      value: 65,
      unit: '%',
      timestamp: new Date().toISOString(),
    },
    battery: 90,
    signalStrength: 95,
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 20).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const MOCK_ACTUATORS: Actuator[] = [
  {
    id: '1',
    name: 'Irrigation Valve 1',
    nameAr: 'صمام الري 1',
    type: 'valve',
    status: 'off',
    deviceId: 'VALVE-001',
    location: {
      latitude: 15.3694,
      longitude: 44.191,
      fieldId: 'field-1',
      fieldName: 'North Field',
    },
    controlMode: 'automatic',
    linkedSensorId: '1',
    linkedSensorName: 'Soil Moisture Sensor 1',
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'Water Pump 1',
    nameAr: 'مضخة المياه 1',
    type: 'pump',
    status: 'off',
    deviceId: 'PUMP-001',
    location: {
      latitude: 15.3695,
      longitude: 44.192,
      fieldId: 'field-1',
      fieldName: 'North Field',
    },
    controlMode: 'manual',
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 28).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const MOCK_ALERT_RULES: AlertRule[] = [
  {
    id: '1',
    name: 'Low Soil Moisture Alert',
    nameAr: 'تنبيه انخفاض رطوبة التربة',
    sensorId: '1',
    sensorName: 'Soil Moisture Sensor 1',
    condition: 'below',
    threshold: 30,
    severity: 'warning',
    enabled: true,
    actionType: 'both',
    actuatorId: '1',
    actuatorAction: 'turn_on',
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'High Temperature Alert',
    nameAr: 'تنبيه ارتفاع درجة الحرارة',
    sensorId: '2',
    sensorName: 'Temperature Sensor 1',
    condition: 'above',
    threshold: 35,
    severity: 'critical',
    enabled: true,
    actionType: 'notification',
    metadata: {},
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

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

      const response = await api.get(`/v1/iot/sensors?${params.toString()}`);
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
      const response = await api.get(`/v1/iot/sensors/${id}`);
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
      const response = await api.post('/v1/iot/sensors', data);
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
      const response = await api.put(`/v1/iot/sensors/${id}`, data);
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
      await api.delete(`/v1/iot/sensors/${id}`);
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

      const response = await api.get(`/v1/iot/sensors/readings?${params.toString()}`);
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
      const response = await api.get(`/v1/iot/sensors/${sensorId}/latest`);
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
      const response = await api.get('/v1/iot/sensors/stats');
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
    return `${api.defaults.baseURL}/v1/iot/sensors/stream${params}`;
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
      const response = await api.get(`/v1/iot/actuators${params}`);
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
      const response = await api.get(`/v1/iot/actuators/${id}`);
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
  createActuator: async (data: Omit<Actuator, 'id' | 'createdAt' | 'updatedAt'>): Promise<Actuator> => {
    try {
      const response = await api.post('/v1/iot/actuators', data);
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
      const response = await api.put(`/v1/iot/actuators/${id}`, data);
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
      await api.delete(`/v1/iot/actuators/${id}`);
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
      const response = await api.post(`/v1/iot/actuators/${data.actuatorId}/control`, {
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
  setMode: async (actuatorId: string, mode: 'manual' | 'automatic' | 'scheduled'): Promise<Actuator> => {
    try {
      const response = await api.patch(`/v1/iot/actuators/${actuatorId}/mode`, { mode });
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
      const response = await api.get(`/v1/iot/alert-rules${params}`);
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
      const response = await api.get(`/v1/iot/alert-rules/${id}`);
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
      const response = await api.post('/v1/iot/alert-rules', data);
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
      const response = await api.put(`/v1/iot/alert-rules/${id}`, data);
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
      await api.delete(`/v1/iot/alert-rules/${id}`);
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
      const response = await api.patch(`/v1/iot/alert-rules/${id}/toggle`, { enabled });
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to toggle alert rule ${id}:`, error);
      throw error;
    }
  },
};
