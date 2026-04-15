/**
 * SAHOOL Admin API Services v16.0.0
 * خدمات API الإدارية - سهول
 *
 * Comprehensive API integration for all backend services
 * Dynamic CRUD operations with proper type safety
 *
 * Uses unified API contracts from @sahool/shared-types/contracts
 */

import { logger } from '../logger';
import {
  USER_ENDPOINTS,
  IOT_ENDPOINTS,
  IRRIGATION_ENDPOINTS,
  ALERT_ENDPOINTS,
  EQUIPMENT_ENDPOINTS,
  buildUrl,
} from '@sahool/shared-types/contracts';

// Default fetch options to ensure httpOnly cookies are sent with requests
const fetchDefaults: RequestInit = {
  credentials: 'same-origin',
};

// =============================================================================
// Common Types | الأنواع الشائعة
// =============================================================================

export interface PaginationParams {
  page?: number;
  limit?: number;
  search?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  errorAr?: string;
}

// =============================================================================
// User Management Service | خدمة إدارة المستخدمين
// =============================================================================

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'farmer' | 'researcher' | 'expert' | 'viewer';
  phone?: string;
  status: 'active' | 'inactive' | 'suspended' | 'pending';
  farmCount?: number;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateUserData {
  email: string;
  password: string;
  name: string;
  phone?: string;
  role?: User['role'];
  tenantId: string;
}

export interface UpdateUserData {
  name?: string;
  email?: string;
  role?: User['role'];
  phone?: string;
  status?: User['status'];
}

export const userService = {
  /**
   * Get all users with pagination
   * جلب جميع المستخدمين مع التصفح
   */
  async getAll(params?: PaginationParams & { role?: string; status?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.limit) queryParams.set('limit', params.limit.toString());
      if (params?.search) queryParams.set('search', params.search);
      if (params?.role) queryParams.set('role', params.role);
      if (params?.status) queryParams.set('status', params.status);

      const response = await fetch(`${USER_ENDPOINTS.LIST}?${queryParams.toString()}`, {
        ...fetchDefaults,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return (await response.json()) as PaginatedResponse<User>;
    } catch (error) {
      logger.error('Failed to fetch users', { error });
      throw error;
    }
  },

  /**
   * Get user by ID
   * جلب مستخدم بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(buildUrl(USER_ENDPOINTS.GET, { userId: id }), fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as User;
    } catch (error) {
      logger.error('Failed to fetch user', { id, error });
      throw error;
    }
  },

  /**
   * Create new user
   * إنشاء مستخدم جديد
   */
  async create(data: CreateUserData) {
    try {
      const response = await fetch(USER_ENDPOINTS.CREATE, {
        ...fetchDefaults,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as User;
    } catch (error) {
      logger.error('Failed to create user', { error });
      throw error;
    }
  },

  /**
   * Update user
   * تحديث مستخدم
   */
  async update(id: string, data: UpdateUserData) {
    try {
      const response = await fetch(buildUrl(USER_ENDPOINTS.UPDATE, { userId: id }), {
        ...fetchDefaults,
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as User;
    } catch (error) {
      logger.error('Failed to update user', { id, error });
      throw error;
    }
  },

  /**
   * Delete user
   * حذف مستخدم
   */
  async delete(id: string) {
    try {
      const response = await fetch(buildUrl(USER_ENDPOINTS.DELETE, { userId: id }), {
        ...fetchDefaults,
        method: 'DELETE',
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as { success: boolean };
    } catch (error) {
      logger.error('Failed to delete user', { id, error });
      throw error;
    }
  },
};

// =============================================================================
// IoT Devices & Sensors Service | خدمة الأجهزة والمستشعرات
// =============================================================================

export interface IoTDevice {
  id: string;
  name: string;
  type: 'soil_moisture' | 'weather_station' | 'camera' | 'flow_meter' | 'other';
  fieldId: string;
  fieldName?: string;
  serialNumber: string;
  status: 'online' | 'offline' | 'error' | 'maintenance';
  batteryLevel?: number;
  lastReading?: string;
  lastReadingValue?: number;
  unit?: string;
  config?: Record<string, unknown>;
  installedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SensorReading {
  id: string;
  deviceId: string;
  metric: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface CreateDeviceData {
  name: string;
  type: IoTDevice['type'];
  fieldId: string;
  serialNumber: string;
  config?: Record<string, unknown>;
}

export const iotService = {
  /**
   * Get all IoT devices
   * جلب جميع الأجهزة
   */
  async getAll(params?: PaginationParams & { fieldId?: string; type?: string; status?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.limit) queryParams.set('limit', params.limit.toString());
      if (params?.fieldId) queryParams.set('field_id', params.fieldId);
      if (params?.type) queryParams.set('type', params.type);
      if (params?.status) queryParams.set('status', params.status);

      const response = await fetch(
        `${IOT_ENDPOINTS.DEVICES}?${queryParams.toString()}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as PaginatedResponse<IoTDevice>;
    } catch (error) {
      logger.error('Failed to fetch IoT devices', { error });
      throw error;
    }
  },

  /**
   * Get device by ID
   * جلب جهاز بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(
        buildUrl(IOT_ENDPOINTS.DEVICE_GET, { deviceId: id }),
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as IoTDevice;
    } catch (error) {
      logger.error('Failed to fetch IoT device', { id, error });
      throw error;
    }
  },

  /**
   * Get device readings
   * جلب قراءات الجهاز
   */
  async getReadings(deviceId: string, params?: { from?: string; to?: string; metric?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.from) queryParams.set('from', params.from);
      if (params?.to) queryParams.set('to', params.to);
      if (params?.metric) queryParams.set('metric', params.metric);

      const response = await fetch(
        `${buildUrl(IOT_ENDPOINTS.DEVICE_READINGS, { deviceId })}?${queryParams.toString()}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as PaginatedResponse<SensorReading>;
    } catch (error) {
      logger.error('Failed to fetch device readings', { deviceId, error });
      throw error;
    }
  },

  /**
   * Register new device
   * تسجيل جهاز جديد
   */
  async create(data: CreateDeviceData) {
    try {
      const response = await fetch(IOT_ENDPOINTS.DEVICE_CREATE, {
        ...fetchDefaults,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as IoTDevice;
    } catch (error) {
      logger.error('Failed to register IoT device', { error });
      throw error;
    }
  },

  /**
   * Update device
   * تحديث جهاز
   */
  async update(id: string, data: Partial<CreateDeviceData> & { status?: IoTDevice['status'] }) {
    try {
      const response = await fetch(buildUrl(IOT_ENDPOINTS.DEVICE_UPDATE, { deviceId: id }), {
        ...fetchDefaults,
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as IoTDevice;
    } catch (error) {
      logger.error('Failed to update IoT device', { id, error });
      throw error;
    }
  },

  /**
   * Delete device
   * حذف جهاز
   */
  async delete(id: string) {
    try {
      const response = await fetch(buildUrl(IOT_ENDPOINTS.DEVICE_DELETE, { deviceId: id }), {
        ...fetchDefaults,
        method: 'DELETE',
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as { success: boolean };
    } catch (error) {
      logger.error('Failed to delete IoT device', { id, error });
      throw error;
    }
  },
};

// =============================================================================
// Irrigation Management Service | خدمة إدارة الري
// =============================================================================

export interface IrrigationSchedule {
  id: string;
  fieldId: string;
  fieldName?: string;
  name: string;
  type: 'manual' | 'automatic' | 'scheduled';
  status: 'active' | 'paused' | 'completed';
  startDate: string;
  endDate?: string;
  frequency: 'daily' | 'weekly' | 'custom';
  duration: number; // minutes
  waterAmount: number; // liters or cubic meters
  schedule?: {
    daysOfWeek?: number[];
    timeOfDay?: string;
    interval?: number;
  };
  nextRun?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateIrrigationData {
  fieldId: string;
  name: string;
  type: IrrigationSchedule['type'];
  startDate: string;
  endDate?: string;
  frequency: IrrigationSchedule['frequency'];
  duration: number;
  waterAmount: number;
  schedule?: IrrigationSchedule['schedule'];
}

export const irrigationService = {
  /**
   * Get all irrigation schedules
   * جلب جميع جداول الري
   */
  async getAll(params?: PaginationParams & { fieldId?: string; status?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.limit) queryParams.set('limit', params.limit.toString());
      if (params?.fieldId) queryParams.set('field_id', params.fieldId);
      if (params?.status) queryParams.set('status', params.status);

      const response = await fetch(
        `${IRRIGATION_ENDPOINTS.SCHEDULES_LIST}?${queryParams.toString()}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as PaginatedResponse<IrrigationSchedule>;
    } catch (error) {
      logger.error('Failed to fetch irrigation schedules', { error });
      throw error;
    }
  },

  /**
   * Get schedule by ID
   * جلب جدول بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(
        buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_GET, { scheduleId: id }),
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as IrrigationSchedule;
    } catch (error) {
      logger.error('Failed to fetch irrigation schedule', { id, error });
      throw error;
    }
  },

  /**
   * Create irrigation schedule
   * إنشاء جدول ري
   */
  async create(data: CreateIrrigationData) {
    try {
      const response = await fetch(IRRIGATION_ENDPOINTS.SCHEDULES_CREATE, {
        ...fetchDefaults,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as IrrigationSchedule;
    } catch (error) {
      logger.error('Failed to create irrigation schedule', { error });
      throw error;
    }
  },

  /**
   * Update irrigation schedule
   * تحديث جدول ري
   */
  async update(
    id: string,
    data: Partial<CreateIrrigationData> & { status?: IrrigationSchedule['status'] }
  ) {
    try {
      const response = await fetch(
        buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_UPDATE, { scheduleId: id }),
        {
          ...fetchDefaults,
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as IrrigationSchedule;
    } catch (error) {
      logger.error('Failed to update irrigation schedule', { id, error });
      throw error;
    }
  },

  /**
   * Delete irrigation schedule
   * حذف جدول ري
   */
  async delete(id: string) {
    try {
      const response = await fetch(
        buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_DELETE, { scheduleId: id }),
        {
          ...fetchDefaults,
          method: 'DELETE',
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as { success: boolean };
    } catch (error) {
      logger.error('Failed to delete irrigation schedule', { id, error });
      throw error;
    }
  },
};

// =============================================================================
// Alert Management Service | خدمة إدارة التنبيهات
// =============================================================================

export interface Alert {
  id: string;
  type: 'weather' | 'disease' | 'pest' | 'irrigation' | 'sensor' | 'system' | 'ndvi_low';
  severity: 'info' | 'warning' | 'critical' | 'high' | 'medium' | 'low';
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  source: string;
  fieldId?: string;
  fieldName?: string;
  status: 'unread' | 'read' | 'acknowledged' | 'resolved' | 'dismissed';
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  resolvedBy?: string;
  resolvedAt?: string;
  dismissedBy?: string;
  dismissedAt?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface AlertRule {
  id: string;
  name: string;
  nameAr: string;
  condition: string;
  conditionAr: string;
  severity: Alert['severity'];
  type: Alert['type'];
  enabled: boolean;
  createdAt: string;
}

export interface CreateAlertData {
  type: Alert['type'];
  severity: Alert['severity'];
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  source: string;
  fieldId?: string;
  metadata?: Record<string, unknown>;
}

export interface AlertRulesResponse {
  data: AlertRule[];
  meta: { total: number };
}

export const alertService = {
  /**
   * Get all alerts
   * جلب جميع التنبيهات
   */
  async getAll(
    params?: PaginationParams & {
      type?: string;
      severity?: string;
      status?: string;
      fieldId?: string;
    }
  ) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.limit) queryParams.set('limit', params.limit.toString());
      if (params?.type) queryParams.set('type', params.type);
      if (params?.severity) queryParams.set('severity', params.severity);
      if (params?.status) queryParams.set('status', params.status);
      if (params?.fieldId) queryParams.set('field_id', params.fieldId);

      const response = await fetch(
        `${ALERT_ENDPOINTS.LIST}?${queryParams.toString()}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as PaginatedResponse<Alert>;
    } catch (error) {
      logger.error('Failed to fetch alerts', { error });
      throw error;
    }
  },

  /**
   * Get alert by ID
   * جلب تنبيه بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(buildUrl(ALERT_ENDPOINTS.GET, { alertId: id }), fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Alert;
    } catch (error) {
      logger.error('Failed to fetch alert', { id, error });
      throw error;
    }
  },

  /**
   * Create alert
   * إنشاء تنبيه
   */
  async create(data: CreateAlertData) {
    try {
      const response = await fetch(ALERT_ENDPOINTS.CREATE, {
        ...fetchDefaults,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Alert;
    } catch (error) {
      logger.error('Failed to create alert', { error });
      throw error;
    }
  },

  /**
   * Acknowledge alert
   * إقرار التنبيه
   */
  async acknowledge(id: string) {
    try {
      const response = await fetch(buildUrl(ALERT_ENDPOINTS.ACKNOWLEDGE, { alertId: id }), {
        ...fetchDefaults,
        method: 'POST',
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Alert;
    } catch (error) {
      logger.error('Failed to acknowledge alert', { id, error });
      throw error;
    }
  },

  /**
   * Resolve alert
   * حل التنبيه
   */
  async resolve(id: string, resolution?: string) {
    try {
      const response = await fetch(buildUrl(ALERT_ENDPOINTS.RESOLVE, { alertId: id }), {
        ...fetchDefaults,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Alert;
    } catch (error) {
      logger.error('Failed to resolve alert', { id, error });
      throw error;
    }
  },

  /**
   * Dismiss alert
   * تجاهل التنبيه
   */
  async dismiss(id: string) {
    try {
      const response = await fetch(buildUrl(ALERT_ENDPOINTS.DISMISS, { alertId: id }), {
        ...fetchDefaults,
        method: 'POST',
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Alert;
    } catch (error) {
      logger.error('Failed to dismiss alert', { id, error });
      throw error;
    }
  },

  /**
   * Delete alert
   * حذف تنبيه
   */
  async delete(id: string) {
    try {
      const response = await fetch(buildUrl(ALERT_ENDPOINTS.DELETE, { alertId: id }), {
        ...fetchDefaults,
        method: 'DELETE',
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as { success: boolean };
    } catch (error) {
      logger.error('Failed to delete alert', { id, error });
      throw error;
    }
  },

  /**
   * Get alert rules
   * جلب قواعد التنبيهات
   */
  async getRules() {
    try {
      const response = await fetch(ALERT_ENDPOINTS.RULES, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as AlertRulesResponse;
    } catch (error) {
      logger.error('Failed to fetch alert rules', { error });
      throw error;
    }
  },
};

// =============================================================================
// Equipment Management Service | خدمة إدارة المعدات
// =============================================================================

export interface Equipment {
  id: string;
  name: string;
  nameAr: string;
  type: 'tractor' | 'harvester' | 'sprayer' | 'pump' | 'other';
  model?: string;
  serialNumber?: string;
  status: 'available' | 'in_use' | 'maintenance' | 'broken';
  ownerId?: string;
  ownerName?: string;
  purchaseDate?: string;
  purchasePrice?: number;
  currentValue?: number;
  lastMaintenanceDate?: string;
  nextMaintenanceDate?: string;
  hoursUsed?: number;
  fuelType?: string;
  location?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateEquipmentData {
  name: string;
  nameAr: string;
  type: Equipment['type'];
  model?: string;
  serialNumber?: string;
  purchaseDate?: string;
  purchasePrice?: number;
  fuelType?: string;
  location?: string;
  notes?: string;
}

export const equipmentService = {
  /**
   * Get all equipment
   * جلب جميع المعدات
   */
  async getAll(params?: PaginationParams & { type?: string; status?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.limit) queryParams.set('limit', params.limit.toString());
      if (params?.type) queryParams.set('type', params.type);
      if (params?.status) queryParams.set('status', params.status);
      if (params?.search) queryParams.set('search', params.search);

      const response = await fetch(
        `${EQUIPMENT_ENDPOINTS.LIST}?${queryParams.toString()}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as PaginatedResponse<Equipment>;
    } catch (error) {
      logger.error('Failed to fetch equipment', { error });
      throw error;
    }
  },

  /**
   * Get equipment by ID
   * جلب معدة بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(
        buildUrl(EQUIPMENT_ENDPOINTS.GET, { equipmentId: id }),
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Equipment;
    } catch (error) {
      logger.error('Failed to fetch equipment', { id, error });
      throw error;
    }
  },

  /**
   * Create equipment
   * إنشاء معدة
   */
  async create(data: CreateEquipmentData) {
    try {
      const response = await fetch(EQUIPMENT_ENDPOINTS.CREATE, {
        ...fetchDefaults,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Equipment;
    } catch (error) {
      logger.error('Failed to create equipment', { error });
      throw error;
    }
  },

  /**
   * Update equipment
   * تحديث معدة
   */
  async update(id: string, data: Partial<CreateEquipmentData> & { status?: Equipment['status'] }) {
    try {
      const response = await fetch(buildUrl(EQUIPMENT_ENDPOINTS.UPDATE, { equipmentId: id }), {
        ...fetchDefaults,
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as Equipment;
    } catch (error) {
      logger.error('Failed to update equipment', { id, error });
      throw error;
    }
  },

  /**
   * Delete equipment
   * حذف معدة
   */
  async delete(id: string) {
    try {
      const response = await fetch(buildUrl(EQUIPMENT_ENDPOINTS.DELETE, { equipmentId: id }), {
        ...fetchDefaults,
        method: 'DELETE',
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return (await response.json()) as { success: boolean };
    } catch (error) {
      logger.error('Failed to delete equipment', { id, error });
      throw error;
    }
  },
};

// Export all services
export default {
  users: userService,
  iot: iotService,
  irrigation: irrigationService,
  alerts: alertService,
  equipment: equipmentService,
};
