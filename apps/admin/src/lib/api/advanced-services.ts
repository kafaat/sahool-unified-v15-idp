/**
 * SAHOOL Admin Advanced API Services v16.0.0
 * خدمات API المتقدمة للوحة الإدارة - سهول
 *
 * API integration for audit, vision, terrain, edge devices, drones,
 * virtual sensors, and scouting services.
 *
 * Uses centralized API config from @/config/api
 */

import { logger } from '../logger';
import type { PaginationParams, PaginatedResponse } from './services';
import { SERVICE_URLS, API_URLS } from '@/config/api';

// Default fetch options — httpOnly cookies
const fetchDefaults: RequestInit = {
  credentials: 'same-origin',
};

// =============================================================================
// CSV Export Helper | مساعد تصدير CSV
// =============================================================================

/**
 * Download an array of objects as a CSV file
 * تحميل مصفوفة من الكائنات كملف CSV
 */
export function downloadCSV(data: Record<string, unknown>[], filename: string): void {
  if (data.length === 0 || !data[0]) return;
  const headers = Object.keys(data[0]);
  const csvRows = [
    headers.join(','),
    ...data.map((row) =>
      headers
        .map((h) => {
          const val = row[h];
          const str = val === null || val === undefined ? '' : String(val);
          // Escape quotes and wrap in quotes if needed
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str;
        })
        .join(',')
    ),
  ];
  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

// =============================================================================
// Audit Service | خدمة التدقيق
// =============================================================================

/** سجل التدقيق — Audit log entry */
export interface AuditLog {
  id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  ip_address: string;
  details: Record<string, unknown>;
  status: 'success' | 'failure';
}

/** إحصائيات التدقيق — Audit statistics */
export interface AuditStats {
  total_logs: number;
  actions_today: number;
  unique_users: number;
  failure_rate: number;
  top_actions: Array<{ action: string; count: number }>;
}

export const auditService = {
  /** جلب سجلات التدقيق — Fetch audit logs */
  async getAll(
    params?: PaginationParams & {
      action?: string;
      resource_type?: string;
      user_id?: string;
      status?: string;
      from?: string;
      to?: string;
    }
  ): Promise<PaginatedResponse<AuditLog>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.action) qp.set('action', params.action);
      if (params?.resource_type) qp.set('resource_type', params.resource_type);
      if (params?.user_id) qp.set('user_id', params.user_id);
      if (params?.status) qp.set('status', params.status);
      if (params?.from) qp.set('from', params.from);
      if (params?.to) qp.set('to', params.to);
      const response = await fetch(
        `${API_URLS.auditEndpoints.logs}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<AuditLog>;
    } catch (error) {
      logger.error('Failed to load audit logs:', error);
      return { data: [], meta: { total: 0, page: 1, totalPages: 1 } };
    }
  },

  /** إحصائيات التدقيق — Fetch audit stats */
  async getStats(): Promise<AuditStats> {
    try {
      const response = await fetch(API_URLS.auditEndpoints.stats, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as AuditStats;
    } catch (error) {
      logger.error('Failed to load audit stats:', error);
      return { total_logs: 0, actions_today: 0, unique_users: 0, failure_rate: 0, top_actions: [] };
    }
  },
};

// =============================================================================
// Vision Service | خدمة الرؤية الحاسوبية
// =============================================================================

/** نموذج الرؤية — Vision model */
export interface VisionModel {
  id: string;
  name: string;
  variant: string;
  version: string;
  task: string;
  status: 'active' | 'loading' | 'error';
  accuracy: number;
  size_mb: number;
  loaded_at: string;
}

/** نتيجة الاكتشاف — Vision detection result */
export interface VisionDetection {
  id: string;
  image_url: string;
  task: string;
  detections: Array<{ class: string; confidence: number; bbox: number[] }>;
  created_at: string;
  model_variant: string;
  processing_time_ms: number;
}

export const visionService = {
  /** جلب النماذج المحملة — Get loaded models */
  async getModels(): Promise<VisionModel[]> {
    try {
      const response = await fetch(API_URLS.visionEndpoints.models, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      return Array.isArray(result) ? result : (result?.data ?? []);
    } catch (error) {
      logger.error('Failed to load vision models:', error);
      return [];
    }
  },

  /** فحص صحة الخدمة — Get service health */
  async getHealth(): Promise<Record<string, unknown>> {
    try {
      const response = await fetch(
        `${SERVICE_URLS.yoloVision}/healthz`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      logger.error('Failed to get vision health:', error);
      return {};
    }
  },
};

// =============================================================================
// Terrain Service | خدمة تحليل التضاريس
// =============================================================================

/** تحليل التضاريس — Terrain analysis */
export interface TerrainAnalysis {
  id: string;
  field_id: string;
  analysis_type: 'dem' | 'slope' | 'aspect';
  status: 'completed' | 'processing' | 'failed';
  created_at: string;
  result_url?: string;
  metadata: Record<string, unknown>;
}

export const terrainService = {
  /** جلب التحليلات — Fetch analyses */
  async getAnalyses(
    params?: PaginationParams & { field_id?: string; analysis_type?: string }
  ): Promise<PaginatedResponse<TerrainAnalysis>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.field_id) qp.set('field_id', params.field_id);
      if (params?.analysis_type) qp.set('analysis_type', params.analysis_type);
      const response = await fetch(
        `${API_URLS.terrainEndpoints.analyze}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<TerrainAnalysis>;
    } catch (error) {
      logger.error('Failed to load terrain analyses:', error);
      return { data: [], meta: { total: 0, page: 1, totalPages: 1 } };
    }
  },
};

// =============================================================================
// Edge Device Service | خدمة أجهزة الحافة
// =============================================================================

/** جهاز الحافة — Edge device */
export interface EdgeDevice {
  id: string;
  name: string;
  device_type: string;
  status: 'online' | 'offline' | 'error';
  ip_address: string;
  last_seen: string;
  firmware_version: string;
  models_deployed: number;
  cpu_usage: number;
  memory_usage: number;
  gpu_usage?: number;
}

const EDGE_DEVICES_URL = `${SERVICE_URLS.edgeOrchestrator}/api/v1/edge/devices`;

export const edgeService = {
  /** جلب الأجهزة — Fetch devices */
  async getDevices(
    params?: PaginationParams & { status?: string }
  ): Promise<PaginatedResponse<EdgeDevice>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(`${EDGE_DEVICES_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<EdgeDevice>;
    } catch (error) {
      logger.error('Failed to load edge devices:', error);
      return { data: [], meta: { total: 0, page: 1, totalPages: 1 } };
    }
  },

  /** جلب جهاز بالمعرف — Get device by ID */
  async getDeviceById(id: string): Promise<EdgeDevice | null> {
    try {
      const response = await fetch(`${EDGE_DEVICES_URL}/${id}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as EdgeDevice;
    } catch (error) {
      logger.error('Failed to load edge device:', error);
      return null;
    }
  },
};

// =============================================================================
// Drone Service | خدمة الطائرات المسيّرة
// =============================================================================

/** طائرة مسيّرة — Drone device */
export interface DroneDevice {
  id: string;
  name: string;
  model: string;
  status: 'available' | 'in_flight' | 'maintenance' | 'offline';
  battery_level: number;
  last_flight: string;
  total_flights: number;
}

/** رحلة طيران — Drone flight */
export interface DroneFlight {
  id: string;
  drone_id: string;
  field_id: string;
  flight_type: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  start_time: string;
  end_time?: string;
  area_covered_ha?: number;
}

export const droneService = {
  /** جلب الطائرات — Fetch drone devices */
  async getDevices(
    params?: PaginationParams & { status?: string }
  ): Promise<PaginatedResponse<DroneDevice>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(
        `${API_URLS.droneEndpoints.devices}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<DroneDevice>;
    } catch (error) {
      logger.error('Failed to load drones:', error);
      return { data: [], meta: { total: 0, page: 1, totalPages: 1 } };
    }
  },

  /** جلب الرحلات — Fetch flights */
  async getFlights(
    params?: PaginationParams & { status?: string; drone_id?: string }
  ): Promise<PaginatedResponse<DroneFlight>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      if (params?.drone_id) qp.set('drone_id', params.drone_id);
      const response = await fetch(
        `${API_URLS.droneEndpoints.flights}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<DroneFlight>;
    } catch (error) {
      logger.error('Failed to load drone flights:', error);
      return { data: [], meta: { total: 0, page: 1, totalPages: 1 } };
    }
  },
};

// =============================================================================
// Virtual Sensor Service | خدمة المستشعرات الافتراضية
// =============================================================================

/** مستشعر افتراضي — Virtual sensor */
export interface VirtualSensor {
  id: string;
  name: string;
  sensor_type: string;
  status: 'active' | 'inactive' | 'error';
  source_sensors: string[];
  algorithm: string;
  last_reading: number;
  unit: string;
  last_updated: string;
  accuracy: number;
}

const VIRTUAL_SENSORS_URL = `${SERVICE_URLS.virtualSensors}/api/v1/sensors/virtual`;

export const virtualSensorService = {
  /** جلب المستشعرات — Fetch virtual sensors */
  async getAll(
    params?: PaginationParams & { sensor_type?: string; status?: string }
  ): Promise<PaginatedResponse<VirtualSensor>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.sensor_type) qp.set('sensor_type', params.sensor_type);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(`${VIRTUAL_SENSORS_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<VirtualSensor>;
    } catch (error) {
      logger.error('Failed to load virtual sensors:', error);
      return { data: [], meta: { total: 0, page: 1, totalPages: 1 } };
    }
  },
};

// =============================================================================
// Scouting Service | خدمة الاستكشاف الميداني
// =============================================================================

/** تقرير استكشاف — Scouting report */
export interface ScoutingReport {
  id: string;
  field_id: string;
  scout_name: string;
  date: string;
  pest_found: boolean;
  pest_type?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  location: { lat: number; lng: number };
  notes: string;
  images: string[];
  status: 'pending' | 'reviewed' | 'resolved';
}

const SCOUTING_URL = `${SERVICE_URLS.pestDetection}/api/v1/scouting/reports`;

export const scoutingService = {
  /** جلب التقارير — Fetch scouting reports */
  async getAll(
    params?: PaginationParams & { field_id?: string; severity?: string; status?: string }
  ): Promise<PaginatedResponse<ScoutingReport>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.field_id) qp.set('field_id', params.field_id);
      if (params?.severity) qp.set('severity', params.severity);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(`${SCOUTING_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<ScoutingReport>;
    } catch (error) {
      logger.error('Failed to load scouting reports:', error);
      return { data: [], meta: { total: 0, page: 1, totalPages: 1 } };
    }
  },
};
